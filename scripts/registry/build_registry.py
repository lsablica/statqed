#!/usr/bin/env python3
"""Generate deterministic test-only SQ-0007 records from the live Lean environment."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
LEAN_TOOLS = Path(__file__).resolve().parents[2] / "lean/tools"
if str(LEAN_TOOLS) not in sys.path:
    sys.path.insert(0, str(LEAN_TOOLS))

from model import (  # noqa: E402
    canonical_cbor,
    canonical_json,
    digest_frame,
    retained_evidence_json,
)
import independent_oracle  # noqa: E402
import check_all_modules  # noqa: E402
import project_axiom_report  # noqa: E402

LEAN_ROOT = ROOT / "lean"
EVIDENCE = ROOT / "theorem-registry/evidence"
RECORDS = ROOT / "theorem-registry/records"
LOCKS = ROOT / "theorem-registry/locks"
POLICY = ROOT / "theorem-registry/policy"

LEAN_COMMIT = "f3b06c705e6c85f5314019d5d3baab0fec5b580c"
MATHLIB_COMMIT = "905b95818eb32af7874a58b427f50c1711a5e96c"
TOOLCHAIN = "leanprover/lean4:v4.32.2"
LAKE_VERSION = "5.0.0-src+f3b06c7"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_lean(path: str, begin: str, end: str) -> dict[str, Any]:
    env = os.environ.copy()
    env["LC_ALL"] = "C.UTF-8"
    completed = subprocess.run(
        ["lake", "env", "lean", "--trust=0", path],
        cwd=LEAN_ROOT,
        env=env,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip())
    lines = completed.stdout.splitlines()
    if lines.count(begin) != 1 or lines.count(end) != 1:
        raise RuntimeError(f"missing unique sentinel pair for {path}")
    start = lines.index(begin)
    stop = lines.index(end)
    if stop != start + 2:
        raise RuntimeError(f"unexpected output inside sentinel pair for {path}")
    return json.loads(lines[start + 1])


def name_segments(value: dict[str, Any]) -> list[list[Any]]:
    tag = value.get("tag")
    if tag == "anonymous":
        return []
    parent = name_segments(value["parent"])
    if tag == "string":
        return parent + [[0, value["segment"]]]
    if tag == "numeric":
        return parent + [[1, value["segment"]]]
    raise RuntimeError(f"unsupported Lean name observation: {tag!r}")


def level_array(value: dict[str, Any], params: list[list[Any]]) -> list[Any]:
    tag = value.get("tag")
    if tag == "zero":
        return [0]
    if tag == "succ":
        return [1, level_array(value["level"], params)]
    if tag == "max":
        return [2, level_array(value["left"], params), level_array(value["right"], params)]
    if tag == "imax":
        return [3, level_array(value["left"], params), level_array(value["right"], params)]
    if tag == "parameter":
        name = name_segments(value["name"])
        if name not in params:
            raise RuntimeError("undeclared universe parameter in Lean observation")
        return [4, params.index(name)]
    raise RuntimeError(f"unsupported Lean level observation: {tag!r}")


def expr_array(value: dict[str, Any], params: list[list[Any]] | None = None) -> list[Any]:
    parameters = params or []
    tag = value.get("tag")
    if tag == "bound_variable":
        return [0, value["index"]]
    if tag == "sort":
        return [1, level_array(value["level"], parameters)]
    if tag == "constant":
        return [2, name_segments(value["name"]), [level_array(item, parameters) for item in value["universes"]]]
    if tag == "application":
        return [3, expr_array(value["function"], parameters), expr_array(value["argument"], parameters)]
    binder = {"explicit": 0, "implicit": 1, "strict_implicit": 2, "instance_implicit": 3}
    if tag == "lambda":
        return [4, binder[value["binder_info"]], expr_array(value["type"], parameters), expr_array(value["body"], parameters)]
    if tag == "forall":
        return [5, binder[value["binder_info"]], expr_array(value["type"], parameters), expr_array(value["body"], parameters)]
    if tag == "let":
        return [6, expr_array(value["type"], parameters), expr_array(value["value"], parameters), expr_array(value["body"], parameters)]
    if tag == "literal" and value.get("kind") == "natural":
        return [7, int(value["value"])]
    if tag == "literal" and value.get("kind") == "string":
        return [8, value["value"]]
    if tag == "projection":
        return [9, name_segments(value["type_name"]), value["index"], expr_array(value["structure"], parameters)]
    raise RuntimeError(f"unsupported Lean expression observation: {tag!r}")


def name_json(segments: list[list[Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {"tag": "anonymous"}
    for kind, segment in segments:
        value = {
            "parent": value,
            "segment": segment,
            "tag": "string" if kind == 0 else "numeric",
        }
    return value


def semantic_expr_json(value: list[Any], params: list[dict[str, Any]]) -> dict[str, Any]:
    tag = value[0]

    def level_json(level: list[Any]) -> dict[str, Any]:
        level_tag = level[0]
        if level_tag == 0:
            return {"tag": "zero"}
        if level_tag == 1:
            return {"level": level_json(level[1]), "tag": "succ"}
        if level_tag in (2, 3):
            return {
                "left": level_json(level[1]),
                "right": level_json(level[2]),
                "tag": "max" if level_tag == 2 else "imax",
            }
        if level_tag == 4 and 0 <= level[1] < len(params):
            return {"name": params[level[1]], "tag": "parameter"}
        raise RuntimeError("invalid independent semantic level")

    if tag == 0:
        return {"index": value[1], "tag": "bound_variable"}
    if tag == 1:
        return {"level": level_json(value[1]), "tag": "sort"}
    if tag == 2:
        return {
            "name": name_json(value[1]),
            "tag": "constant",
            "universes": [level_json(item) for item in value[2]],
        }
    if tag == 3:
        return {
            "argument": semantic_expr_json(value[2], params),
            "function": semantic_expr_json(value[1], params),
            "tag": "application",
        }
    binder = {0: "explicit", 1: "implicit", 2: "strict_implicit", 3: "instance_implicit"}
    if tag in (4, 5):
        return {
            "binder_info": binder[value[1]],
            "body": semantic_expr_json(value[3], params),
            "tag": "lambda" if tag == 4 else "forall",
            "type": semantic_expr_json(value[2], params),
        }
    if tag == 6:
        return {
            "body": semantic_expr_json(value[3], params),
            "tag": "let",
            "type": semantic_expr_json(value[1], params),
            "value": semantic_expr_json(value[2], params),
        }
    if tag == 7:
        return {"kind": "natural", "tag": "literal", "value": str(value[1])}
    if tag == 8:
        return {"kind": "string", "tag": "literal", "value": value[1]}
    if tag == 9:
        return {
            "index": value[2],
            "structure": semantic_expr_json(value[3], params),
            "tag": "projection",
            "type_name": name_json(value[1]),
        }
    raise RuntimeError(f"unsupported independent semantic expression tag: {tag!r}")


def independently_normalized_expr(
    typed: dict[str, Any], level_parameters: list[dict[str, Any]]
) -> dict[str, Any]:
    semantic = independent_oracle.normalize_expression(
        typed, level_parameters=level_parameters
    )
    return semantic_expr_json(semantic, level_parameters)


def independent_name_key(value: dict[str, Any]) -> bytes:
    return independent_oracle.canonical_cbor(name_segments(value))


def expression_references(value: dict[str, Any]) -> list[dict[str, Any]]:
    found: dict[bytes, dict[str, Any]] = {}

    def add(name: dict[str, Any]) -> None:
        found[independent_name_key(name)] = name

    def visit(expression: dict[str, Any]) -> None:
        tag = expression["tag"]
        if tag == "constant":
            add(expression["name"])
        elif tag == "projection":
            add(expression["type_name"])
            visit(expression["structure"])
        elif tag == "application":
            visit(expression["function"])
            visit(expression["argument"])
        elif tag in {"lambda", "forall"}:
            visit(expression["type"])
            visit(expression["body"])
        elif tag == "let":
            visit(expression["type"])
            visit(expression["value"])
            visit(expression["body"])
        elif tag == "metadata":
            visit(expression["expression"])

    visit(value)
    return [found[key] for key in sorted(found)]


def independently_normalized_closure_unit(raw: dict[str, Any]) -> dict[str, Any]:
    result = {key: value for key, value in raw.items() if key not in {"type", "body", "members", "recursors"}}
    params = raw["level_parameters"]
    result["type"] = independently_normalized_expr(raw["type"], params)
    result["body"] = None if raw["body"] is None else independently_normalized_expr(raw["body"], params)
    references = expression_references(raw["type"])
    if raw["body"] is not None:
        references.extend(expression_references(raw["body"]))

    if raw["kind"] == "inductive_family":
        members = []
        for member in raw["members"]:
            member_params = member["level_parameters"]
            converted_member = {key: value for key, value in member.items() if key not in {"type", "constructors"}}
            converted_member["type"] = independently_normalized_expr(member["type"], member_params)
            references.extend(expression_references(member["type"]))
            constructors = []
            for constructor in member["constructors"]:
                constructor_params = constructor["level_parameters"]
                converted_constructor = {
                    key: value for key, value in constructor.items()
                    if key != "type"
                }
                converted_constructor["type"] = independently_normalized_expr(
                    constructor["type"], constructor_params
                )
                constructors.append(converted_constructor)
                references.append(constructor["name"])
                references.extend(expression_references(constructor["type"]))
            converted_member["constructors"] = constructors
            members.append(converted_member)
            references.append(member["name"])
        recursors = []
        for recursor in raw["recursors"]:
            recursor_params = recursor["level_parameters"]
            converted_recursor = {
                key: value for key, value in recursor.items()
                if key not in {"type", "rules"}
            }
            converted_recursor["type"] = independently_normalized_expr(
                recursor["type"], recursor_params
            )
            references.append(recursor["name"])
            references.extend(recursor["family"])
            references.extend(expression_references(recursor["type"]))
            rules = []
            for rule in recursor["rules"]:
                converted_rule = dict(rule)
                converted_rule["rhs"] = independently_normalized_expr(
                    rule["rhs"], recursor_params
                )
                rules.append(converted_rule)
                references.append(rule["constructor"])
                references.extend(expression_references(rule["rhs"]))
            converted_recursor["rules"] = rules
            recursors.append(converted_recursor)
        result["members"] = members
        result["recursors"] = recursors

    unique_references = {independent_name_key(name): name for name in references}
    result["references"] = [unique_references[key] for key in sorted(unique_references)]
    return result


def typed_expression_visits(value: dict[str, Any]) -> int:
    """Count the expression/level visits defined by closure-v0."""

    def level_visits(level: dict[str, Any]) -> int:
        tag = level["tag"]
        if tag in {"zero", "parameter"}:
            return 1
        if tag == "succ":
            return 1 + level_visits(level["level"])
        if tag in {"max", "imax"}:
            return 1 + level_visits(level["left"]) + level_visits(level["right"])
        raise RuntimeError(f"unsupported typed level for work accounting: {tag!r}")

    tag = value["tag"]
    if tag in {"bound_variable", "literal"}:
        return 1
    if tag == "sort":
        return 1 + level_visits(value["level"])
    if tag == "constant":
        return 1 + sum(level_visits(level) for level in value["universes"])
    if tag == "application":
        return 1 + typed_expression_visits(value["function"]) + typed_expression_visits(value["argument"])
    if tag in {"lambda", "forall"}:
        return 1 + typed_expression_visits(value["type"]) + typed_expression_visits(value["body"])
    if tag == "let":
        return (
            1
            + typed_expression_visits(value["type"])
            + typed_expression_visits(value["value"])
            + typed_expression_visits(value["body"])
        )
    if tag == "projection":
        return 1 + typed_expression_visits(value["structure"])
    if tag == "metadata":
        # The v0 normalizer erases mdata before counting a semantic node.
        return typed_expression_visits(value["expression"])
    raise RuntimeError(f"unsupported typed expression for work accounting: {tag!r}")


def typed_unit_expression_visits(unit: dict[str, Any]) -> int:
    # The atomic family `members` list already includes the root member type;
    # non-family units count their top-level type directly.
    visits = 0 if unit["kind"] == "inductive_family" else typed_expression_visits(unit["type"])
    if unit["body"] is not None:
        visits += typed_expression_visits(unit["body"])
    if unit["kind"] == "inductive_family":
        for member in unit["members"]:
            visits += typed_expression_visits(member["type"])
            visits += sum(
                typed_expression_visits(constructor["type"])
                for constructor in member["constructors"]
            )
        for recursor in unit["recursors"]:
            visits += typed_expression_visits(recursor["type"])
            visits += sum(
                typed_expression_visits(rule["rhs"])
                for rule in recursor["rules"]
            )
    return visits


def derive_live_closure(
    roots: list[dict[str, Any]], typed_units: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], int, int]:
    """Independently derive reachability, canonical units, and work counters."""

    units: dict[bytes, dict[str, Any]] = {}
    aliases: dict[bytes, bytes] = {}
    normalized: dict[bytes, dict[str, Any]] = {}
    for unit in typed_units:
        unit_key = independent_name_key(unit["name"])
        if unit_key in units:
            raise RuntimeError("duplicate live typed closure unit")
        units[unit_key] = unit
        normalized[unit_key] = independently_normalized_closure_unit(unit)
        owned = [unit["name"]]
        if unit["kind"] == "inductive_family":
            owned.extend(unit["family"])
            for member in unit["members"]:
                owned.append(member["name"])
                owned.extend(constructor["name"] for constructor in member["constructors"])
            owned.extend(recursor["name"] for recursor in unit["recursors"])
        for alias in owned:
            alias_key = independent_name_key(alias)
            previous = aliases.get(alias_key)
            if previous is not None and previous != unit_key:
                raise RuntimeError("live closure alias belongs to multiple atomic units")
            aliases[alias_key] = unit_key

    reached: set[bytes] = set()
    active: set[bytes] = set()
    attempted_edges = 0

    def visit(name: dict[str, Any], depth: int) -> None:
        nonlocal attempted_edges
        name_key = independent_name_key(name)
        unit_key = aliases.get(name_key)
        if unit_key is None or unit_key not in units:
            raise RuntimeError("independent live closure has a missing dependency")
        if unit_key in reached:
            return
        if unit_key in active:
            raise RuntimeError("independent live closure has a non-family cycle")
        if depth > 64:
            raise RuntimeError("independent live closure exceeds depth")
        active.add(unit_key)
        # Production charges every attempted reference before duplicate/self
        # suppression.  Mirror that rule independently.
        for reference in normalized[unit_key]["references"]:
            attempted_edges += 1
            reference_key = independent_name_key(reference)
            if aliases.get(reference_key) == unit_key:
                continue
            if aliases.get(reference_key) in reached:
                continue
            visit(reference, depth + 1)
        active.remove(unit_key)
        reached.add(unit_key)

    for root in sorted(roots, key=independent_name_key):
        visit(root, 0)
    if reached != set(units):
        raise RuntimeError("live closure contains unreachable or extra typed units")
    expression_visits = sum(typed_unit_expression_visits(units[key]) for key in reached)
    work = expression_visits + len(reached) + attempted_edges
    return [normalized[key] for key in sorted(reached)], expression_visits, work


def validate_live_fixtures(observation: dict[str, Any]) -> dict[str, Any]:
    live = observation["live_fixtures"]
    expression_results = []
    required_typed_tags = {
        "LIVE-LAMBDA-CONSTRUCTOR": "lambda",
        "LIVE-LET-CONSTRUCTOR": "let",
        "LIVE-METADATA-ERASURE": "metadata",
        "LIVE-PROJECTION-CONSTRUCTOR": "projection",
    }

    def contains_typed_tag(value: Any, tag: str) -> bool:
        if isinstance(value, dict):
            return value.get("tag") == tag or any(
                contains_typed_tag(child, tag) for child in value.values()
            )
        if isinstance(value, list):
            return any(contains_typed_tag(child, tag) for child in value)
        return False

    def primary_result_class(code: str) -> str:
        if code == "registry.normalization_failure":
            return code
        if code.startswith("registry.normalization.") and code.endswith("_limit"):
            return "registry.resource_limit"
        if code.startswith("registry.normalization."):
            return "registry.normalization_failure"
        return code

    for fixture in live["expression_fixtures"]:
        expected = fixture["expected"]
        required_tag = required_typed_tags.get(fixture["fixture_id"])
        if required_tag is not None and not contains_typed_tag(fixture["typed_expression"], required_tag):
            raise RuntimeError(
                f"live typed fixture omitted required constructor: {fixture['fixture_id']}:{required_tag}"
            )
        try:
            independent = independent_oracle.observe(
                fixture["typed_expression"],
                level_parameters=fixture["level_parameters"],
            )
        except independent_oracle.OracleError as error:
            if expected != "rejected" or error.code != primary_result_class(fixture.get("code", "")):
                raise RuntimeError(
                    f"independent live fixture mismatch: {fixture['fixture_id']}:{error.code}"
                ) from error
            expression_results.append({
                "classification": "rejected",
                "code": error.code,
                "fixture_id": fixture["fixture_id"],
            })
            continue
        if expected != "accepted":
            raise RuntimeError(f"independent oracle accepted rejected live fixture: {fixture['fixture_id']}")
        parameters = [name_segments(name) for name in fixture["level_parameters"]]
        primary = expr_array(fixture["normalized"]["expression"], parameters)
        if independent["normalized_expression"] != primary:
            raise RuntimeError(f"independent oracle disagrees on live fixture: {fixture['fixture_id']}")
        expression_results.append({
            "classification": "accepted",
            "fixture_id": fixture["fixture_id"],
            "payload_sha256": sha256(bytes.fromhex(independent["payload_hex"])),
        })

    closure_results = []
    for fixture in live["closure_fixtures"]:
        observed = fixture["observation"]
        independent_records, expression_visits, work = derive_live_closure(
            observed["roots"], observed["typed_units"]
        )
        if independent_records != observed["records"]:
            raise RuntimeError(f"independent oracle disagrees on live closure: {fixture['fixture_id']}")
        if expression_visits != observed["expression_level_visits"] or work != observed["work"]:
            raise RuntimeError(f"independent work accounting disagrees: {fixture['fixture_id']}")
        payload = independent_oracle.environment_payload_from_records(
            independent_records, LEAN_COMMIT
        )
        closure_results.append({
            "fixture_id": fixture["fixture_id"],
            "payload_sha256": sha256(payload),
            "record_count": len(independent_records),
            "work": work,
        })
        record_names = {independent_name_key(record["name"]) for record in independent_records}
        for required in fixture.get("required_units", []):
            if independent_name_key(required) not in record_names:
                raise RuntimeError(
                    f"live closure omitted required selected dependency: {fixture['fixture_id']}"
                )
    by_fixture = {item["fixture_id"]: item for item in expression_results}
    if (
        by_fixture["LIVE-METADATA-BASE"].get("payload_sha256")
        != by_fixture["LIVE-METADATA-ERASURE"].get("payload_sha256")
    ):
        raise RuntimeError("live metadata erasure changed normalized bytes")

    depth_boundary = live["depth_boundary"]
    accepted_depth = depth_boundary["accepted"]
    accepted_records, accepted_visits, accepted_work = derive_live_closure(
        accepted_depth["roots"], accepted_depth["typed_units"]
    )
    if (
        accepted_records != accepted_depth["records"]
        or accepted_visits != accepted_depth["expression_level_visits"]
        or accepted_work != accepted_depth["work"]
    ):
        raise RuntimeError("independent live closure depth-max observation disagrees")
    over_units = [*accepted_depth["typed_units"], depth_boundary["over_typed_unit"]]
    try:
        derive_live_closure([depth_boundary["over_root"]], over_units)
    except RuntimeError as error:
        if str(error) != "independent live closure exceeds depth":
            raise
    else:
        raise RuntimeError("independent oracle accepted live closure one over depth")
    if depth_boundary["over_code"] != "registry.closure.depth_limit":
        raise RuntimeError("primary live closure one-over depth error drifted")
    work_boundary = live["work_boundary"]
    root_key = independent_name_key(work_boundary["root"])
    matching = next(
        fixture for fixture in live["closure_fixtures"]
        if [independent_name_key(root) for root in fixture["observation"]["roots"]] == [root_key]
    )
    _, boundary_visits, boundary_work = derive_live_closure(
        matching["observation"]["roots"], matching["observation"]["typed_units"]
    )
    if (
        boundary_visits != work_boundary["expression_level_visits"]
        or boundary_work != work_boundary["required_work"]
        or work_boundary["one_under_limit"] + 1 != boundary_work
        or not work_boundary["accepted_at_required"]
        or work_boundary["one_under_code"] != "registry.closure.work_budget_limit"
    ):
        raise RuntimeError("independent work-boundary accounting disagrees")
    unit_boundary = live["unit_boundary"]
    if unit_boundary != {
        "accepted_at_max": True,
        "configured_limit": independent_oracle.LIMITS["closure_units"],
        "one_over_rejected": True,
    }:
        raise RuntimeError("live closure-unit boundary predicate disagrees")
    fixed_work_boundary = live["fixed_work_boundary"]
    dominance_upper_bound = 262_144 + independent_oracle.LIMITS["closure_units"] + (
        independent_oracle.LIMITS["closure_units"] * independent_oracle.LIMITS["closure_width"]
    )
    if (
        fixed_work_boundary["accepted_at_max"] is not True
        or fixed_work_boundary["configured_limit"] != independent_oracle.LIMITS["work"]
        or fixed_work_boundary["dominance_upper_bound"] != dominance_upper_bound
        or fixed_work_boundary["one_over_rejected"] is not True
        or dominance_upper_bound >= independent_oracle.LIMITS["work"]
    ):
        raise RuntimeError("live fixed work-boundary predicate disagrees")
    return {
        "closure_fixtures": closure_results,
        "depth_boundary": {
            "accepted_record_count": len(accepted_records),
            "classification_at_max": "accepted",
            "classification_one_over": "rejected",
            "one_over_code": depth_boundary["over_code"],
        },
        "expression_fixtures": expression_results,
        "schema": "statqed.registry-live-independent-comparison.v0",
        "fixed_work_boundary": fixed_work_boundary,
        "unit_boundary": unit_boundary,
        "work_boundary": work_boundary,
    }


def project_source_manifest() -> list[dict[str, str]]:
    return [
        {"path": str(path.relative_to(ROOT)), "sha256": sha256(path.read_bytes())}
        for path in sorted((LEAN_ROOT / "StatQED/Registry").rglob("*.lean"))
    ]


def outputs() -> dict[Path, bytes]:
    observation = run_lean(
        "StatQED/Registry/Tools/Extract.lean",
        "STATQED_REGISTRY_EXTRACT_BEGIN",
        "STATQED_REGISTRY_EXTRACT_END",
    )
    axioms = run_lean(
        "StatQED/Registry/Tools/AxiomReport.lean",
        "STATQED_REGISTRY_AXIOM_REPORT_BEGIN",
        "STATQED_REGISTRY_AXIOM_REPORT_END",
    )
    by_name = {item["declaration"]: item for item in observation["declarations"]}
    target = by_name["StatQED.Registry.Tests.testOnlyTrue"]
    refactor = by_name["StatQED.Registry.Tests.testOnlyTrueRefactor"]
    compatibility_source = by_name["StatQED.Registry.Tests.falseImpliesTrue"]

    if target["proposition"].get("normalizer") != "statqed.lean-expr.v0":
        raise RuntimeError("live Lean observation used an unsupported normalizer version")
    if target.get("closure_version") != "statqed.lean-environment-closure.v0":
        raise RuntimeError("live Lean observation used an unsupported closure version")
    target_parameters = [name_segments(name) for name in target["proposition"]["level_parameters"]]
    refactor_parameters = [name_segments(name) for name in refactor["proposition"]["level_parameters"]]
    proposition_value = [
        "statqed.lean-expr.v0",
        expr_array(target["proposition"]["expression"], target_parameters),
    ]
    refactor_value = [
        "statqed.lean-expr.v0",
        expr_array(refactor["proposition"]["expression"], refactor_parameters),
    ]
    if proposition_value != refactor_value:
        raise RuntimeError("proof-only refactor changed canonical proposition")
    proposition_bytes = canonical_cbor(proposition_value)
    proposition_frame, proposition_digest = digest_frame("proposition", proposition_bytes)
    independent = independent_oracle.observe(
        target["proposition"]["expression"],
        level_parameters=target["proposition"]["level_parameters"],
    )
    if independent["payload_hex"] != proposition_bytes.hex():
        raise RuntimeError("independent oracle disagrees on canonical proposition bytes")
    if independent["digests"]["proposition"]["digest"] != proposition_digest:
        raise RuntimeError("independent oracle disagrees on proposition digest")

    environment_value = [
        "statqed.lean-environment-closure.v0",
        LEAN_COMMIT,
        "statqed.lean-expr.v0",
        target["closure"],
    ]
    refactor_environment_value = [
        "statqed.lean-environment-closure.v0",
        LEAN_COMMIT,
        "statqed.lean-expr.v0",
        refactor["closure"],
    ]
    if environment_value != refactor_environment_value:
        raise RuntimeError("proof-only refactor changed environment closure")
    environment_bytes = canonical_cbor(environment_value)
    independent_environment_bytes = independent_oracle.environment_payload_from_records(
        target["closure"], LEAN_COMMIT
    )
    if independent_environment_bytes != environment_bytes:
        raise RuntimeError("independent oracle disagrees on environment closure bytes")
    environment_frame, environment_digest = digest_frame("environment", environment_bytes)
    independent_environment_frame, independent_environment_digest = (
        independent_oracle.digest_frame("environment", independent_environment_bytes)
    )
    if independent_environment_digest != environment_digest:
        raise RuntimeError("independent oracle disagrees on environment closure digest")
    independent["environment_closure"] = {
        "digest": independent_environment_digest,
        "frame_hex": independent_environment_frame.hex(),
        "payload_hex": independent_environment_bytes.hex(),
        "record_count": len(target["closure"]),
    }
    independent["live_fixtures"] = validate_live_fixtures(observation)

    axiom_records = axioms["declarations"]
    target_axioms = next(item for item in axiom_records if item["declaration"] == target["declaration"])
    if target_axioms["axioms"]:
        raise RuntimeError("test-only record has nonempty transitive axiom observation")
    axiom_bytes = canonical_json(axioms)
    axiom_digest = sha256(axiom_bytes)
    project_axiom_bytes = project_axiom_report.encoded(project_axiom_report.generate())
    fresh_check_bytes = canonical_json(check_all_modules.check_all())
    project_axiom_digest = sha256(project_axiom_bytes)
    fresh_check_digest = sha256(fresh_check_bytes)
    source_manifest = project_source_manifest()
    manifest_digest = sha256((LEAN_ROOT / "lake-manifest.json").read_bytes())

    proof_lock = {
        "schema": "statqed.proof-build-lock.v0",
        "lean_toolchain": TOOLCHAIN,
        "lean_source_commit": LEAN_COMMIT,
        "lake_version": LAKE_VERSION,
        "mathlib_commit": MATHLIB_COMMIT,
        "lake_manifest_sha256": manifest_digest,
        "project_sources": source_manifest,
        "declaration": target["declaration"],
        "kind": target["kind"],
        "proposition_digest": proposition_digest,
        "environment_digest": environment_digest,
        "proof_subject": expr_array(target["proof_subject"], target_parameters),
        "axiom_report_sha256": axiom_digest,
        "kernel_check": {
            "project_axiom_report_sha256": project_axiom_digest,
            "all_module_fresh_check_sha256": fresh_check_digest,
            "module_count": json.loads(fresh_check_bytes)["module_count"],
            "status": "pass",
        },
        "trust_policy": "statqed.registry-empty-imported-axioms.v0",
        "nonclaim": "Same-kernel replay is not an external verifier.",
    }
    proof_bytes = canonical_cbor(proof_lock)
    proof_frame, proof_digest = digest_frame("proof_build", proof_bytes)

    refactor_lock = copy_without = dict(proof_lock)
    copy_without["declaration"] = refactor["declaration"]
    copy_without["proof_subject"] = expr_array(refactor["proof_subject"], refactor_parameters)
    _, refactor_digest = digest_frame("proof_build", canonical_cbor(copy_without))
    if refactor_digest == proof_digest:
        raise RuntimeError("proof-only refactor did not change proof/build lock")

    compatibility_parameters = [name_segments(name) for name in compatibility_source["proposition"]["level_parameters"]]
    compatibility_normalized_type = expr_array(
        compatibility_source["proposition"]["expression"], compatibility_parameters
    )
    if compatibility_normalized_type[:2] != [5, 0]:
        raise RuntimeError("compatibility declaration is not an explicit implication")
    new_proposition_bytes = canonical_cbor(["statqed.lean-expr.v0", compatibility_normalized_type[2]])
    _, new_proposition_digest = digest_frame("proposition", new_proposition_bytes)
    compatibility_environment_bytes = canonical_cbor([
        "statqed.lean-environment-closure.v0", LEAN_COMMIT,
        "statqed.lean-expr.v0", compatibility_source["closure"],
    ])
    _, compatibility_environment_digest = digest_frame("environment", compatibility_environment_bytes)
    compatibility_axioms = next(
        item for item in axiom_records if item["declaration"] == compatibility_source["declaration"]
    )["axioms"]
    if compatibility_axioms:
        raise RuntimeError("compatibility proof has nonempty transitive axiom observation")
    compatibility_proof_lock = {
        **proof_lock,
        "declaration": compatibility_source["declaration"],
        "proposition_digest": digest_frame(
            "proposition", canonical_cbor(["statqed.lean-expr.v0", compatibility_normalized_type])
        )[1],
        "environment_digest": compatibility_environment_digest,
        "proof_subject": expr_array(compatibility_source["proof_subject"], compatibility_parameters),
        "axiom_report_sha256": axiom_digest,
    }
    compatibility_proof_bytes = canonical_cbor(compatibility_proof_lock)
    compatibility_proof_frame, compatibility_proof_digest = digest_frame(
        "proof_build", compatibility_proof_bytes
    )
    compatibility = {
        "schema": "statqed.compatibility-proof-lock.v0",
        "direction": "new_implies_old",
        "new_proposition": "False",
        "new_proposition_digest": new_proposition_digest,
        "old_proposition_digest": proposition_digest,
        "environment_digest": compatibility_environment_digest,
        "declaration": compatibility_source["declaration"],
        "normalized_type": compatibility_normalized_type,
        "proof_subject": expr_array(compatibility_source["proof_subject"], compatibility_parameters),
        "proof_build_digest": compatibility_proof_digest,
        "axiom_report_digest": axiom_digest,
        "axioms": [],
        "universe_instantiations": {"new": [], "old": []},
        "path_length": 1,
    }
    compatibility_bytes = canonical_cbor(compatibility)
    compatibility_frame, compatibility_digest = digest_frame("compatibility", compatibility_bytes)

    record = {
        "schema": "statqed.registry-record.v0",
        "id": "statqed.test-only.foundation.true.v0",
        "version": "0.0.1",
        "declaration": target["declaration"],
        "normalizer": "statqed.lean-expr.v0",
        "closure": "statqed.lean-environment-closure.v0",
        "proposition_digest": proposition_digest,
        "environment_digest": environment_digest,
        "proof_build_digest": proof_digest,
        "axiom_report_digest": axiom_digest,
        "maturity": "Experimental",
        "exposure": "test_only",
        "source_anchor": "docs/adr/0011-foundation-toy-slice.md",
        "attribution": "not_applicable: definitionally trivial test proposition",
        "nonclaims": [
            "not a public or statistical theorem",
            "not a non-vacuity witness",
            "not source-fidelity or artifact verification evidence",
        ],
    }
    record_bytes = canonical_cbor(record)
    record_frame, record_digest = digest_frame("record", record_bytes)
    snapshot = {
        "schema": "statqed.registry-snapshot.v0",
        "records": [[record["id"], record["version"], record_digest]],
    }
    snapshot_bytes = canonical_cbor(snapshot)
    snapshot_frame, root = digest_frame("snapshot", snapshot_bytes)
    policy = {
        "schema": "statqed.registry-authorization-policy.v0",
        "policy_version": "statqed.registry-authorization.v0",
        "current_permitted_roots": [root],
        "historical_permitted_roots": ["11" * 32],
        "historical_forbidden_roots": ["22" * 32],
        "revoked_roots": ["33" * 32],
        "compatibility_digest": compatibility_digest,
        "compatibility_binding": compatibility,
        "record_binding": record,
        "record_digest": record_digest,
        "selection": "verifier_local_only",
    }
    bundle = {
        "record": record,
        "record_digest": record_digest,
        "snapshot": snapshot,
        "requested_root": root,
        "proposition_digest": proposition_digest,
        "environment_digest": environment_digest,
        "proof_build_digest": proof_digest,
        "compatibility_digest": compatibility_digest,
        "axioms": [],
        "compatibility": None,
    }
    identity = {
        "schema": "statqed.registry-identity-summary.v0",
        "governed_id": record["id"],
        "version": record["version"],
        "normalizer": record["normalizer"],
        "proposition_digest": proposition_digest,
        "environment_digest": environment_digest,
        "record_digest": record_digest,
        "proof_build_digest": proof_digest,
        "refactor_proof_build_digest": refactor_digest,
        "authorization_root": root,
        "compatibility_digest": compatibility_digest,
    }
    registry_index = {
        "schema": "statqed.theorem-registry-index.v0",
        "maturity": "Experimental",
        "entries": [{
            "id": record["id"],
            "version": record["version"],
            "record": "records/test-only-true.v0.json",
            "record_digest": record_digest,
        }],
        "snapshot": "records/snapshot-v0.json",
        "authorization_root": root,
        "scope": "test_only",
    }

    return {
        EVIDENCE / "lean-observation.json": retained_evidence_json(observation),
        EVIDENCE / "independent-observation.json": retained_evidence_json(independent),
        EVIDENCE / "axioms.json": axiom_bytes,
        EVIDENCE / "project-axioms.json": project_axiom_bytes,
        EVIDENCE / "all-module-fresh-check.json": fresh_check_bytes,
        EVIDENCE / "identity-summary.json": canonical_json(identity),
        EVIDENCE / "bundle.json": canonical_json(bundle),
        EVIDENCE / "proposition.cbor": proposition_bytes,
        EVIDENCE / "proposition.frame": proposition_frame,
        EVIDENCE / "environment.cbor": environment_bytes,
        EVIDENCE / "environment.frame": environment_frame,
        EVIDENCE / "record.frame": record_frame,
        EVIDENCE / "proof-build.frame": proof_frame,
        EVIDENCE / "snapshot.frame": snapshot_frame,
        EVIDENCE / "compatibility.frame": compatibility_frame,
        EVIDENCE / "compatibility-proof-build.frame": compatibility_proof_frame,
        ROOT / "theorem-registry/registry.json": canonical_json(registry_index),
        RECORDS / "test-only-true.v0.json": canonical_json(record),
        RECORDS / "snapshot-v0.json": canonical_json(snapshot),
        LOCKS / "proof-build-v0.json": canonical_json(proof_lock),
        LOCKS / "proof-build-refactor-v0.json": canonical_json(copy_without),
        LOCKS / "compatibility-v0.json": canonical_json(compatibility),
        LOCKS / "compatibility-proof-build-v0.json": canonical_json(compatibility_proof_lock),
        POLICY / "authorization-v0.json": canonical_json(policy),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated = outputs()
    if args.check:
        drift = [str(path.relative_to(ROOT)) for path, data in generated.items() if not path.is_file() or path.read_bytes() != data]
        if drift:
            print("registry generation drift: " + ", ".join(drift))
            return 1
    else:
        for path, data in generated.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(f"SQ-0007 registry generation verified: {len(generated)} deterministic subjects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
