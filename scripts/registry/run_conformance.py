#!/usr/bin/env python3
"""Generate or verify the deterministic SQ-0007 conformance corpus."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from model import (  # noqa: E402
    LIMITS,
    RegistryError,
    canonical_cbor,
    canonical_json,
    closure,
    digest_frame,
    normalize_expr,
    verify_bundle,
)
import independent_oracle  # noqa: E402

CATALOG = ROOT / "conformance/registry/fixtures/catalog.json"
RESULTS = ROOT / "conformance/registry/results/results.json"
MUTATIONS = ROOT / "conformance/registry/results/mutations.json"
GOLDEN_DIR = ROOT / "conformance/registry/golden"
BUNDLE_PATH = ROOT / "theorem-registry/evidence/bundle.json"
POLICY_PATH = ROOT / "theorem-registry/policy/authorization-v0.json"
COMPATIBILITY_PATH = ROOT / "theorem-registry/locks/compatibility-v0.json"
LEAN_COMMIT = "f3b06c705e6c85f5314019d5d3baab0fec5b580c"
NORMALIZER_ID = "statqed.lean-expr.v0"
CLOSURE_ID = "statqed.lean-environment-closure.v0"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def expanded(value: Any) -> Any:
    if value == "@max-depth@":
        expr: Any = [2, [[0, "x"]], []]
        for _ in range(LIMITS["expression_depth"]):
            expr = [3, [2, [[0, "f"]], []], expr]
        return expr
    if value == "@over-depth@":
        expr: Any = [2, [[0, "x"]], []]
        for _ in range(LIMITS["expression_depth"] + 1):
            expr = [3, [2, [[0, "f"]], []], expr]
        return expr
    if value == "@max-level-depth@":
        level: Any = [0]
        for _ in range(LIMITS["level_depth"]):
            level = [1, level]
        return [1, level]
    if value == "@over-level-depth@":
        level = [0]
        for _ in range(LIMITS["level_depth"] + 1):
            level = [1, level]
        return [1, level]
    if value == "@over-name-segments@":
        return [2, [[0, "x"]] * 65, []]
    if value == "@max-level-params@":
        return [f"u{index}" for index in range(LIMITS["universe_arguments"])]
    if value == "@over-level-params@":
        return [f"u{index}" for index in range(LIMITS["universe_arguments"] + 1)]
    if value == "@max-expression-nodes@":
        leaves: list[Any] = [[0, 0] for _ in range(32_767)]
        while len(leaves) > 1:
            paired = [[3, leaves[index], leaves[index + 1]] for index in range(0, len(leaves) - 1, 2)]
            if len(leaves) % 2:
                paired.append(leaves[-1])
            leaves = paired
        return [4, 0, [1, [0]], leaves[0]]
    if value == "@over-expression-nodes@":
        expression = expanded("@max-expression-nodes@")
        expression[2] = [1, [1, [0]]]
        return expression
    if value == "@combined-depth-max@":
        level = [0]
        for _ in range(LIMITS["level_depth"]):
            level = [1, level]
        expression = [1, level]
        for _ in range(LIMITS["expression_depth"]):
            expression = [3, [2, [[0, "f"]], []], expression]
        return expression
    if value == "@aggregate-string-max@":
        literal = [8, "x" * LIMITS["string_bytes"]]
        return [3, [3, literal, literal], [3, literal, literal]]
    if value == "@aggregate-string-over@":
        return [3, expanded("@aggregate-string-max@"), [8, "x"]]
    if value == "@over-width@":
        return [f"r{i:03d}" for i in range(LIMITS["closure_width"] + 1)]
    if value == "@over-reference-width-unknown-field@":
        return {
            "root": {
                "kind": "definition",
                "references": [f"r{i:03d}" for i in range(LIMITS["closure_width"] + 1)],
                "unknown": "must-not-mask-resource-limit",
            }
        }
    if value == "@over-definition-value-unknown-field@":
        return {
            "root": {
                "kind": "definition",
                "references": [],
                "value": "x" * (LIMITS["string_bytes"] + 1),
                "unknown": "must-not-mask-resource-limit",
            }
        }
    if isinstance(value, str) and value in {"@max-closure-name-roots@", "@over-closure-name-roots@"}:
        base = ".".join(["x" * LIMITS["name_segment_bytes"]] * 4)
        name = base if value.startswith("@max") else base + ".x"
        return [name]
    if isinstance(value, str) and value in {"@max-closure-name-declarations@", "@over-closure-name-declarations@"}:
        root_token = value.replace("declarations", "roots")
        name = expanded(root_token)[0]
        return {name: {"kind": "definition", "references": []}}
    if value == "@over-closure-depth@":
        result = {}
        for i in range(LIMITS["closure_depth"] + 2):
            result[f"n{i}"] = {
                "kind": "definition",
                "references": [] if i == LIMITS["closure_depth"] + 1 else [f"n{i + 1}"],
            }
        return result
    if value == "@max-closure-depth@":
        result = {}
        for i in range(LIMITS["closure_depth"] + 1):
            result[f"n{i}"] = {
                "kind": "definition",
                "references": [] if i == LIMITS["closure_depth"] else [f"n{i + 1}"],
            }
        return result
    if value == "@max-string@":
        return "x" * LIMITS["string_bytes"]
    if value == "@over-string@":
        return "x" * (LIMITS["string_bytes"] + 1)
    return value


def rebuild_bundle_record(bundle: dict[str, Any]) -> None:
    _, record_digest = digest_frame("record", canonical_cbor(bundle["record"]))
    bundle["record_digest"] = record_digest
    bundle["snapshot"] = {
        "schema": "statqed.registry-snapshot.v0",
        "records": [[bundle["record"]["id"], bundle["record"]["version"], record_digest]],
    }
    _, root = digest_frame("snapshot", canonical_cbor(bundle["snapshot"]))
    bundle["requested_root"] = root


def nested_lists(depth: int) -> Any:
    value: Any = None
    for _ in range(depth):
        value = [value]
    return value


def mutate_bundle(base: dict[str, Any], base_policy: dict[str, Any], mutation: str) -> tuple[dict[str, Any], dict[str, Any]]:
    bundle = copy.deepcopy(base)
    policy = copy.deepcopy(base_policy)
    root = bundle["requested_root"]
    if mutation == "none":
        return bundle, policy
    if mutation == "historical_permitted":
        policy["current_permitted_roots"] = []
        policy["historical_permitted_roots"] = [root]
    elif mutation == "wrong_root":
        bundle["requested_root"] = "00" * 32
    elif mutation in {
        "malformed_requested_root", "malformed_record_digest",
        "malformed_proposition_digest", "malformed_environment_digest",
        "malformed_proof_build_digest",
    }:
        field = {
            "malformed_requested_root": "requested_root",
            "malformed_record_digest": "record_digest",
            "malformed_proposition_digest": "proposition_digest",
            "malformed_environment_digest": "environment_digest",
            "malformed_proof_build_digest": "proof_build_digest",
        }[mutation]
        bundle[field] = "not-a-digest"
    elif mutation == "unknown_root":
        policy["current_permitted_roots"] = []
    elif mutation == "revoked_root":
        policy["current_permitted_roots"] = []
        policy["revoked_roots"] = [root]
    elif mutation == "historical_forbidden":
        policy["current_permitted_roots"] = []
        policy["historical_forbidden_roots"] = [root]
    elif mutation == "policy_version":
        policy["policy_version"] = "statqed.registry-authorization.v999"
    elif mutation == "policy_overlap":
        policy["historical_permitted_roots"].append(root)
    elif mutation == "policy_schema":
        policy["schema"] = "forged"
    elif mutation == "policy_selection":
        policy["selection"] = "candidate_selected"
    elif mutation == "policy_unknown_field":
        policy["unknown"] = "field"
    elif mutation == "policy_malformed_root":
        policy["historical_permitted_roots"].append("not-a-digest")
    elif mutation == "policy_root_limit":
        policy["current_permitted_roots"] = [root] + [f"{index + 4:064x}" for index in range(12)]
    elif mutation == "policy_root_over":
        policy["current_permitted_roots"] = [root] + [f"{index + 4:064x}" for index in range(13)]
    elif mutation == "policy_root_over_malformed":
        policy["current_permitted_roots"] = ["not-a-digest"] + [
            f"{index + 4:064x}" for index in range(LIMITS["registry_entries"])
        ]
    elif mutation == "policy_compatibility_digest_over":
        policy["compatibility_digest"] = "x" * (LIMITS["string_bytes"] + 1)
    elif mutation == "bundle_surrogate":
        bundle["candidate_policy"] = "\ud800"
    elif mutation == "bundle_unknown_string_over":
        bundle["unknown"] = "x" * (LIMITS["string_bytes"] + 1)
    elif mutation in {
        "resource_id_over_policy_surrogate",
        "resource_axioms_over_policy_surrogate",
        "resource_unknown_string_over_policy_surrogate",
        "resource_id_over_bundle_surrogate",
    }:
        if mutation in {
            "resource_id_over_policy_surrogate", "resource_id_over_bundle_surrogate"
        }:
            bundle["record"]["id"] = "a" * (LIMITS["identifier_bytes"] + 1)
        elif mutation == "resource_axioms_over_policy_surrogate":
            bundle["axioms"] = [None] * (LIMITS["axioms"] + 1)
        else:
            bundle["unknown"] = "x" * (LIMITS["string_bytes"] + 1)
        if mutation == "resource_id_over_bundle_surrogate":
            bundle["candidate_policy"] = "\ud800"
        else:
            policy["schema"] = "\ud800"
    elif mutation == "forged_id":
        bundle["record"]["id"] = "statqed.test-only.forged.v0"
        rebuild_bundle_record(bundle)
        policy["current_permitted_roots"] = [bundle["requested_root"]]
    elif mutation == "record_schema_null":
        bundle["record"]["schema"] = None
    elif mutation == "forged_maturity":
        bundle["record"]["maturity"] = "Stable"
        rebuild_bundle_record(bundle)
        policy["current_permitted_roots"] = [bundle["requested_root"]]
    elif mutation in {
        "forged_declaration",
        "forged_normalizer",
        "forged_closure",
        "forged_version",
        "forged_source_anchor",
        "forged_attribution",
        "forged_nonclaims",
        "forged_axiom_report_digest",
    }:
        field, value = {
            "forged_declaration": ("declaration", "StatQED.Registry.Tests.forged"),
            "forged_normalizer": ("normalizer", "statqed.lean-expr.v999"),
            "forged_closure": ("closure", "statqed.lean-environment-closure.v999"),
            "forged_version": ("version", "9.9.9"),
            "forged_source_anchor": ("source_anchor", "forged/source.md"),
            "forged_attribution": ("attribution", "forged attribution"),
            "forged_nonclaims": ("nonclaims", ["forged public theorem claim"]),
            "forged_axiom_report_digest": ("axiom_report_digest", "44" * 32),
        }[mutation]
        bundle["record"][field] = value
        rebuild_bundle_record(bundle)
        policy["current_permitted_roots"] = [bundle["requested_root"]]
    elif mutation == "registry_replacement":
        bundle["snapshot"]["records"].append(["statqed.test-only.replacement.v0", "0.0.1", "00" * 32])
        _, new_root = digest_frame("snapshot", canonical_cbor(bundle["snapshot"]))
        bundle["requested_root"] = new_root
        policy["current_permitted_roots"] = [new_root]
    elif mutation in {"snapshot_entries_max", "snapshot_entries_over"}:
        count = LIMITS["registry_entries"] + (mutation == "snapshot_entries_over")
        bundle["snapshot"]["records"] = [
            [f"statqed.test-only.snapshot-{index:02d}.v0", "0.0.1", bundle["record_digest"]]
            for index in range(count)
        ]
        _, new_root = digest_frame("snapshot", canonical_cbor(bundle["snapshot"]))
        bundle["requested_root"] = new_root
        policy["current_permitted_roots"] = [new_root]
    elif mutation == "snapshot_entries_over_unknown_field":
        bundle["snapshot"]["records"] = [
            [f"statqed.test-only.snapshot-{index:02d}.v0", "0.0.1", bundle["record_digest"]]
            for index in range(LIMITS["registry_entries"] + 1)
        ]
        bundle["snapshot"]["unknown"] = True
    elif mutation == "artifact_policy":
        bundle["candidate_policy"] = {"current_permitted_roots": ["11" * 32]}
    elif mutation == "artifact_policy_nested_max":
        bundle["candidate_policy"] = nested_lists(LIMITS["canonical_depth"] - 1)
    elif mutation == "artifact_policy_nested_over":
        bundle["candidate_policy"] = nested_lists(LIMITS["canonical_depth"])
    elif mutation == "bundle_null":
        return None, policy
    elif mutation == "bundle_list":
        return [], policy
    elif mutation == "policy_null":
        return bundle, None
    elif mutation == "proposition":
        bundle["proposition_digest"] = "11" * 32
    elif mutation == "environment":
        bundle["environment_digest"] = "22" * 32
    elif mutation == "proof_build":
        bundle["proof_build_digest"] = "33" * 32
    elif mutation == "forbidden_axiom":
        bundle["axioms"] = ["Classical.choice"]
    elif mutation == "axioms_max":
        bundle["axioms"] = ["Classical.choice"] * LIMITS["axioms"]
    elif mutation == "axioms_over":
        bundle["axioms"] = ["Classical.choice"] * (LIMITS["axioms"] + 1)
    elif mutation == "axioms_over_wrong_schema":
        bundle["axioms"] = ["Classical.choice"] * (LIMITS["axioms"] + 1)
        bundle["record"]["schema"] = "statqed.registry-record.v999"
    elif mutation == "identifier_over":
        bundle["record"]["id"] = "a" * (LIMITS["identifier_bytes"] + 1)
    elif mutation == "identifier_utf8_at_limit":
        bundle["record"]["id"] = "é" * (LIMITS["identifier_bytes"] // 2)
    elif mutation == "identifier_utf8_over":
        bundle["record"]["id"] = "é" * (LIMITS["identifier_bytes"] // 2) + "a"
    elif mutation == "identifier_over_wrong_schema":
        bundle["record"]["id"] = "a" * (LIMITS["identifier_bytes"] + 1)
        bundle["record"]["schema"] = "statqed.registry-record.v999"
    elif mutation == "compatibility_null_digest_malformed":
        bundle["compatibility_digest"] = "not-a-digest"
    elif mutation == "compatibility_null_digest_substitution":
        bundle["compatibility_digest"] = "00" * 32
    elif mutation == "compatibility_policy_digest_malformed":
        policy["compatibility_digest"] = "not-a-digest"
    elif mutation == "compatibility_candidate_and_policy_digest_malformed":
        bundle["compatibility_digest"] = "not-a-digest"
        policy["compatibility_digest"] = "not-a-digest"
    elif mutation == "compatibility_policy_digest_substitution":
        policy["compatibility_digest"] = "00" * 32
    elif mutation == "compatibility_policy_binding_malformed":
        policy["compatibility_binding"] = None
    elif mutation in {
        "compatibility_policy_path_boolean",
        "compatibility_policy_normalized_type_null",
        "compatibility_policy_proof_subject_null",
        "compatibility_policy_universes_null",
        "compatibility_policy_new_proposition_null",
        "compatibility_policy_normalized_type_bool",
        "compatibility_policy_wrong_valid_proof_subject",
    }:
        field, value = {
            "compatibility_policy_path_boolean": ("path_length", True),
            "compatibility_policy_normalized_type_null": ("normalized_type", None),
            "compatibility_policy_proof_subject_null": ("proof_subject", None),
            "compatibility_policy_universes_null": ("universe_instantiations", None),
            "compatibility_policy_new_proposition_null": ("new_proposition", None),
            "compatibility_policy_normalized_type_bool": (
                "normalized_type", [5, False, [2, [[0, "False"]], []], [2, [[0, "True"]], []]]
            ),
            "compatibility_policy_wrong_valid_proof_subject": (
                "proof_subject", [2, [[0, "True"]], []]
            ),
        }[mutation]
        policy["compatibility_binding"][field] = value
        _, digest = digest_frame(
            "compatibility", canonical_cbor(policy["compatibility_binding"])
        )
        policy["compatibility_digest"] = digest
        bundle["compatibility_digest"] = digest
    elif mutation == "compatibility_policy_binding_substitution":
        policy["compatibility_binding"]["new_proposition_digest"] = "44" * 32
        _, policy["compatibility_digest"] = digest_frame(
            "compatibility", canonical_cbor(policy["compatibility_binding"])
        )
    elif mutation == "compatibility_correct":
        bundle["compatibility"] = read_json(COMPATIBILITY_PATH)
        _, bundle["compatibility_digest"] = digest_frame(
            "compatibility", canonical_cbor(bundle["compatibility"])
        )
        policy["compatibility_digest"] = bundle["compatibility_digest"]
    elif mutation == "compatibility_reverse":
        bundle["compatibility"] = read_json(COMPATIBILITY_PATH)
        bundle["compatibility"]["direction"] = "old_implies_new"
        _, bundle["compatibility_digest"] = digest_frame(
            "compatibility", canonical_cbor(bundle["compatibility"])
        )
        policy["compatibility_digest"] = digest_frame(
            "compatibility", canonical_cbor(read_json(COMPATIBILITY_PATH))
        )[1]
    elif mutation == "compatibility_metadata":
        bundle["compatibility"] = {"label": "equivalent"}
    elif mutation in {
        "compatibility_environment", "compatibility_assumption",
        "compatibility_definition", "compatibility_missing_proof",
        "compatibility_proof_lock",
    }:
        bundle["compatibility"] = read_json(COMPATIBILITY_PATH)
        field, value = {
            "compatibility_environment": ("environment_digest", "44" * 32),
            "compatibility_assumption": (
                "normalized_type", [5, 0, [2, [[0, "True"]], []], [2, [[0, "True"]], []]]
            ),
            "compatibility_definition": ("new_proposition_digest", "55" * 32),
            "compatibility_missing_proof": ("proof_subject", None),
            "compatibility_proof_lock": ("proof_build_digest", "66" * 32),
        }[mutation]
        if value is None:
            del bundle["compatibility"][field]
        else:
            bundle["compatibility"][field] = value
        _, bundle["compatibility_digest"] = digest_frame(
            "compatibility", canonical_cbor(bundle["compatibility"])
        )
    else:
        raise AssertionError(mutation)
    return bundle, policy


def evaluate(
    case: dict[str, Any], bundle: dict[str, Any], policy: dict[str, Any]
) -> tuple[str, str, bytes | None, str | None, str | None]:
    try:
        if case["kind"] == "expression":
            value = expanded(case["input"])
            if isinstance(value, list) and len(value) == 2 and value[0] == 8:
                value = [8, expanded(value[1])]
            level_parameters = expanded(case["level_params"]) if "level_params" in case else []
            try:
                normalized = normalize_expr(value, level_params=level_parameters)
                payload = canonical_cbor(["statqed.lean-expr.v0", normalized])
                digest_frame("proposition", payload)
                primary_classification, primary_code = "accepted", "accepted"
            except RegistryError as error:
                payload = None
                primary_classification, primary_code = "rejected", error.code
            try:
                oracle_parameters = independent_oracle.validate_level_parameters(level_parameters)
                oracle_payload = independent_oracle.semantic_expression_payload(
                    value, level_parameter_count=len(oracle_parameters)
                )
                oracle_classification, oracle_code = "accepted", "accepted"
            except independent_oracle.OracleError as error:
                oracle_payload = None
                oracle_classification, oracle_code = "rejected", error.code
            if (
                primary_classification == "accepted"
                and oracle_classification == "accepted"
                and payload != oracle_payload
            ):
                oracle_code = "registry.proposition_mismatch"
            return (
                primary_classification,
                primary_code,
                payload,
                oracle_classification,
                oracle_code,
            )
        if case["kind"] == "closure":
            roots = expanded(case["roots"])
            declarations = expanded(case["declarations"])
            try:
                primary = closure(roots, declarations)
                payload = canonical_cbor(
                    [CLOSURE_ID, LEAN_COMMIT, NORMALIZER_ID, primary]
                )
                digest_frame("environment", payload)
                primary_classification, primary_code = "accepted", "accepted"
            except RegistryError as error:
                primary = None
                payload = None
                primary_classification, primary_code = "rejected", error.code
            try:
                oracle = independent_oracle.environment_closure(roots, declarations)
                oracle_payload = independent_oracle.canonical_cbor(
                    [CLOSURE_ID, LEAN_COMMIT, NORMALIZER_ID, oracle]
                )
                oracle_classification, oracle_code = "accepted", "accepted"
            except independent_oracle.OracleError as error:
                oracle = None
                oracle_payload = None
                oracle_classification, oracle_code = "rejected", error.code
            if (
                primary_classification == "accepted"
                and oracle_classification == "accepted"
                and (primary != oracle or payload != oracle_payload)
            ):
                oracle_code = "registry.environment_mismatch"
            return (
                primary_classification,
                primary_code,
                payload,
                oracle_classification,
                oracle_code,
            )
        if case["kind"] == "bundle":
            candidate, selected_policy = mutate_bundle(bundle, policy, case["mutation"])
            if case["mutation"] == "compatibility_metadata":
                raise RegistryError("registry.compatibility_missing")
            verify_bundle(candidate, selected_policy)
            return "accepted", "accepted", None, None, None
        if case["kind"] == "digest":
            payload = canonical_cbor(["statqed.lean-expr.v0", [2, [[0, "True"]], []]])
            frame, digest = digest_frame("proposition", payload)
            if case["mutation"] == "cross_domain":
                frame, _ = digest_frame("environment", payload)
            elif case["mutation"] == "truncated":
                frame = frame[:-1]
            elif case["mutation"] == "purpose":
                frame = frame.replace(b"statqed.theorem.proposition.v0", b"statqed.theorem.environment.v0")
            elif case["mutation"] == "algorithm":
                frame = frame.replace(b"sha-256", b"sha-512")
            elif case["mutation"] == "profile":
                frame = frame.replace(b"statqed.cbor-core.v1", b"statqed.cbor-core.v0")
            elif case["mutation"] == "object_class":
                frame = frame.replace(b"statqed.lean-proposition.v0", b"statqed.registry-record.v0")
            elif case["mutation"] == "framing":
                frame = frame.replace(b"statqed.digest-lp.v1", b"statqed.digest-lp.v0")
            elif case["mutation"] == "reordered":
                frame = frame.replace(b"sha-256", b"SHA-256")
            elif case["mutation"] == "concatenation":
                frame = frame.replace((7).to_bytes(4, "big") + b"sha-256", b"sha-256")
            elif case["mutation"] == "empty":
                frame = frame[:-len(payload)]
            elif case["mutation"] == "fallback":
                frame = frame.replace(b"sha-256", b"sha-1")
            elif case["mutation"] == "downgrade":
                frame = frame.replace(b"statqed.lean-expr.v0", b"statqed.lean-expr.v-1")
            if hashlib.sha256(frame).hexdigest() != digest:
                raise RegistryError("registry.statement_digest_mismatch")
            return "accepted", "accepted", None, None, None
        raise RegistryError("registry.operational_failure")
    except RegistryError as error:
        return "rejected", error.code, None, None, None


def _classification(candidate: dict[str, Any], policy: dict[str, Any]) -> str:
    try:
        verify_bundle(candidate, policy)
        return "accepted"
    except RegistryError as error:
        return error.code


def deliberate_divergences(
    bundle: dict[str, Any], policy: dict[str, Any]
) -> list[dict[str, Any]]:
    """Execute deliberately wrong implementations and detect disagreement."""

    true_expr = [2, [[0, "True"]], []]
    correct_expr = independent_oracle.semantic_expression_payload(true_expr)
    wrong_tag = canonical_cbor(["statqed.lean-expr.v0", [1, [0]]])

    binder = [5, 0, [1, [0]], [0, 0]]
    wrong_binder = copy.deepcopy(binder)
    wrong_binder[1] = 3
    binder_detected = (
        independent_oracle.semantic_expression_payload(binder)
        != canonical_cbor(["statqed.lean-expr.v0", wrong_binder])
    )

    universe = [1, [4, 0]]
    wrong_universe = [1, [0]]
    universe_detected = (
        independent_oracle.semantic_expression_payload(universe, level_parameter_count=1)
        != canonical_cbor(["statqed.lean-expr.v0", wrong_universe])
    )

    typed_metadata = {
        "tag": "metadata",
        "metadata": {"source": "deliberately-retained"},
        "expression": {
            "tag": "constant",
            "name": {"tag": "string", "parent": {"tag": "anonymous"}, "segment": "True"},
            "universes": [],
        },
    }
    erased = independent_oracle.proposition_payload(typed_metadata)
    retained = canonical_cbor(["statqed.lean-expr.v0", [10, "metadata", true_expr]])

    declarations = {
        "root": {"kind": "definition", "references": ["dep"]},
        "dep": {"kind": "definition", "references": []},
    }
    correct_closure = independent_oracle.environment_closure(["root"], declarations)
    wrong_closure = [{"name": "root", "kind": "definition"}]
    correct_closure_envelope = independent_oracle.canonical_cbor(
        [CLOSURE_ID, LEAN_COMMIT, NORMALIZER_ID, correct_closure]
    )
    wrong_closure_envelope = independent_oracle.canonical_cbor(
        [CLOSURE_ID, correct_closure]
    )

    forged, forged_policy = mutate_bundle(bundle, policy, "forged_id")
    selected = copy.deepcopy(bundle)
    selected["requested_root"] = "44" * 32
    selected_policy = copy.deepcopy(policy)
    substituted = copy.deepcopy(bundle)
    substituted["proof_build_digest"] = "55" * 32
    axiom_candidate = copy.deepcopy(bundle)
    axiom_candidate["axioms"] = ["Classical.choice"]
    axiom_omitting_bad = copy.deepcopy(axiom_candidate)
    axiom_omitting_bad["axioms"] = []
    reverse, reverse_policy = mutate_bundle(bundle, policy, "compatibility_reverse")
    correct_compat, correct_compat_policy = mutate_bundle(bundle, policy, "compatibility_correct")

    observations = [
        ("wrong_expression_tag", correct_expr != wrong_tag),
        ("wrong_binder_info", binder_detected),
        ("wrong_universe_param", universe_detected),
        ("metadata_not_erased", erased != retained),
        ("missing_closure_edge", correct_closure != wrong_closure),
        ("missing_closure_envelope_fields", correct_closure_envelope != wrong_closure_envelope),
        ("record_field_forgery", _classification(forged, forged_policy) == "registry.record_digest_mismatch"),
        ("candidate_selected_root", _classification(selected, selected_policy) == "registry.authorization_root_mismatch"),
        ("proof_lock_substitution", _classification(substituted, policy) == "registry.proof_build_lock_mismatch"),
        (
            "axiom_omission",
            _classification(axiom_candidate, policy) == "registry.forbidden_axiom"
            and _classification(axiom_omitting_bad, policy) == "accepted",
        ),
        (
            "compatibility_reversal",
            _classification(correct_compat, correct_compat_policy) == "accepted"
            and _classification(reverse, reverse_policy) == "registry.compatibility_wrong_direction",
        ),
    ]
    return [
        {"detected": detected, "id": name, "status": "pass" if detected else "fail"}
        for name, detected in observations
    ]


def generated() -> tuple[bytes, bytes, dict[str, bytes]]:
    catalog = read_json(CATALOG)
    bundle = read_json(BUNDLE_PATH)
    policy = read_json(POLICY_PATH)
    results = []
    goldens: dict[str, bytes] = {}
    for case in catalog["fixtures"]:
        classification, code, payload, oracle_classification, oracle_code = evaluate(
            case, bundle, policy
        )
        passed = classification == case["expected"] and (
            classification == "accepted" or code == case["code"]
        )
        result = {
            "classification": classification,
            "code": code,
            "expected": case["expected"],
            "fixture_id": case["id"],
        }
        if oracle_classification is not None:
            passed = passed and oracle_classification == classification and oracle_code == code
            result["oracle_classification"] = oracle_classification
            result["oracle_code"] = oracle_code
        result["status"] = "pass" if passed else "fail"
        results.append(result)
        if payload is not None and classification == "accepted":
            goldens[case["id"] + ".cbor"] = payload

    mutations = deliberate_divergences(bundle, policy)
    output = {
        "accepted": sum(item["classification"] == "accepted" for item in results),
        "failed": sum(item["status"] != "pass" for item in results),
        "rejected": sum(item["classification"] == "rejected" for item in results),
        "results": results,
        "schema": "statqed.registry-conformance-results.v1",
        "total": len(results),
    }
    mutation_output = {
        "detected": sum(item["detected"] for item in mutations),
        "mutations": mutations,
        "schema": "statqed.registry-deliberate-mutations.v0",
    }
    return canonical_json(output), canonical_json(mutation_output), goldens


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    result_bytes, mutation_bytes, goldens = generated()
    expected_names = sorted(goldens)
    if args.verify:
        mismatches = []
        if not RESULTS.is_file() or RESULTS.read_bytes() != result_bytes:
            mismatches.append(str(RESULTS.relative_to(ROOT)))
        if not MUTATIONS.is_file() or MUTATIONS.read_bytes() != mutation_bytes:
            mismatches.append(str(MUTATIONS.relative_to(ROOT)))
        actual_names = sorted(path.name for path in GOLDEN_DIR.glob("*.cbor")) if GOLDEN_DIR.is_dir() else []
        if actual_names != expected_names:
            mismatches.append(str(GOLDEN_DIR.relative_to(ROOT)))
        for name, data in goldens.items():
            path = GOLDEN_DIR / name
            if not path.is_file() or path.read_bytes() != data:
                mismatches.append(str(path.relative_to(ROOT)))
        if mismatches:
            print("registry conformance drift: " + ", ".join(sorted(set(mismatches))))
            return 1
    else:
        RESULTS.parent.mkdir(parents=True, exist_ok=True)
        GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
        RESULTS.write_bytes(result_bytes)
        MUTATIONS.write_bytes(mutation_bytes)
        for old in GOLDEN_DIR.glob("*.cbor"):
            if old.name not in goldens:
                old.unlink()
        for name, data in goldens.items():
            (GOLDEN_DIR / name).write_bytes(data)
    results = json.loads(result_bytes)
    mutations = json.loads(mutation_bytes)
    print(f"SQ-0007 conformance verified: {results['total']} cases, {results['failed']} failures")
    print(f"  accepted: {results['accepted']}; rejected: {results['rejected']}; goldens: {len(goldens)}")
    print(f"  deliberate divergences detected: {mutations['detected']}")
    return 0 if results["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
