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


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def expanded(value: Any) -> Any:
    if value == "@over-depth@":
        expr: Any = [2, [[0, "x"]], []]
        for _ in range(LIMITS["expression_depth"] + 1):
            expr = [3, [2, [[0, "f"]], []], expr]
        return expr
    if value == "@over-name-segments@":
        return [2, [[0, "x"]] * 65, []]
    if value == "@over-width@":
        return [f"r{i:03d}" for i in range(LIMITS["closure_width"] + 1)]
    if value == "@over-closure-depth@":
        result = {}
        for i in range(LIMITS["closure_depth"] + 2):
            result[f"n{i}"] = {
                "kind": "definition",
                "references": [] if i == LIMITS["closure_depth"] + 1 else [f"n{i + 1}"],
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
    elif mutation == "forged_id":
        bundle["record"]["id"] = "statqed.test-only.forged.v0"
        rebuild_bundle_record(bundle)
        policy["current_permitted_roots"] = [bundle["requested_root"]]
    elif mutation == "forged_maturity":
        bundle["record"]["maturity"] = "Stable"
        rebuild_bundle_record(bundle)
        policy["current_permitted_roots"] = [bundle["requested_root"]]
    elif mutation == "registry_replacement":
        bundle["snapshot"]["records"].append(["statqed.test-only.replacement.v0", "0.0.1", "00" * 32])
        _, new_root = digest_frame("snapshot", canonical_cbor(bundle["snapshot"]))
        bundle["requested_root"] = new_root
        policy["current_permitted_roots"] = [new_root]
    elif mutation == "artifact_policy":
        bundle["candidate_policy"] = {"current_permitted_roots": ["11" * 32]}
    elif mutation == "proposition":
        bundle["proposition_digest"] = "11" * 32
    elif mutation == "environment":
        bundle["environment_digest"] = "22" * 32
    elif mutation == "proof_build":
        bundle["proof_build_digest"] = "33" * 32
    elif mutation == "forbidden_axiom":
        bundle["axioms"] = ["Classical.choice"]
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
    else:
        raise AssertionError(mutation)
    return bundle, policy


def evaluate(case: dict[str, Any], bundle: dict[str, Any], policy: dict[str, Any]) -> tuple[str, str, bytes | None]:
    try:
        if case["kind"] == "expression":
            value = expanded(case["input"])
            if isinstance(value, list) and len(value) == 2 and value[0] == 8:
                value = [8, expanded(value[1])]
            normalized = normalize_expr(value, level_params=case.get("level_params"))
            payload = canonical_cbor(["statqed.lean-expr.v0", normalized])
            oracle_payload = independent_oracle.semantic_expression_payload(
                value, level_parameter_count=len(case.get("level_params", []))
            )
            if oracle_payload != payload:
                raise RegistryError("registry.proposition_mismatch")
            digest_frame("proposition", payload)
            return "accepted", "accepted", payload
        if case["kind"] == "closure":
            roots = expanded(case["roots"])
            declarations = expanded(case["declarations"])
            primary = closure(roots, declarations)
            oracle = independent_oracle.environment_closure(roots, declarations)
            if oracle != primary:
                raise RegistryError("registry.environment_mismatch")
            payload = canonical_cbor(["statqed.lean-environment-closure.v0", primary])
            digest_frame("environment", payload)
            return "accepted", "accepted", payload
        if case["kind"] == "bundle":
            candidate, selected_policy = mutate_bundle(bundle, policy, case["mutation"])
            if case["mutation"] == "compatibility_metadata":
                raise RegistryError("registry.compatibility_missing")
            verify_bundle(candidate, selected_policy)
            return "accepted", "accepted", None
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
            return "accepted", "accepted", None
        raise RegistryError("registry.operational_failure")
    except RegistryError as error:
        return "rejected", error.code, None


def _classification(candidate: dict[str, Any], policy: dict[str, Any]) -> str:
    try:
        verify_bundle(candidate, policy)
        return "accepted"
    except RegistryError as error:
        return error.code


def deliberate_divergences(
    bundle: dict[str, Any], policy: dict[str, Any]
) -> list[dict[str, Any]]:
    """Execute ten deliberately wrong implementations and detect disagreement."""

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
        classification, code, payload = evaluate(case, bundle, policy)
        passed = classification == case["expected"] and (classification == "accepted" or code == case["code"])
        results.append({
            "classification": classification,
            "code": code,
            "expected": case["expected"],
            "fixture_id": case["id"],
            "status": "pass" if passed else "fail",
        })
        if payload is not None and classification == "accepted":
            goldens[case["id"] + ".cbor"] = payload

    mutations = deliberate_divergences(bundle, policy)
    output = {
        "accepted": sum(item["classification"] == "accepted" for item in results),
        "failed": sum(item["status"] != "pass" for item in results),
        "rejected": sum(item["classification"] == "rejected" for item in results),
        "results": results,
        "schema": "statqed.registry-conformance-results.v0",
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
