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

from model import canonical_cbor, canonical_json, digest_frame  # noqa: E402
import independent_oracle  # noqa: E402

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

    proposition_value = ["statqed.lean-expr.v0", expr_array(target["proposition"]["expression"])]
    refactor_value = ["statqed.lean-expr.v0", expr_array(refactor["proposition"]["expression"])]
    if proposition_value != refactor_value:
        raise RuntimeError("proof-only refactor changed canonical proposition")
    proposition_bytes = canonical_cbor(proposition_value)
    proposition_frame, proposition_digest = digest_frame("proposition", proposition_bytes)
    independent = independent_oracle.observe(target["proposition"]["expression"])
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
    environment_frame, environment_digest = digest_frame("environment", environment_bytes)

    axiom_records = axioms["declarations"]
    target_axioms = next(item for item in axiom_records if item["declaration"] == target["declaration"])
    if target_axioms["axioms"]:
        raise RuntimeError("test-only record has nonempty transitive axiom observation")
    axiom_bytes = canonical_json(axioms)
    axiom_digest = sha256(axiom_bytes)
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
        "proof_subject": expr_array(target["proof_subject"]),
        "axiom_report_sha256": axiom_digest,
        "kernel_check": "lake env lean --trust=0 and same-kernel leanchecker --fresh passed",
        "trust_policy": "statqed.registry-empty-imported-axioms.v0",
        "nonclaim": "Same-kernel replay is not an external verifier.",
    }
    proof_bytes = canonical_cbor(proof_lock)
    proof_frame, proof_digest = digest_frame("proof_build", proof_bytes)

    refactor_lock = copy_without = dict(proof_lock)
    copy_without["declaration"] = refactor["declaration"]
    copy_without["proof_subject"] = expr_array(refactor["proof_subject"])
    _, refactor_digest = digest_frame("proof_build", canonical_cbor(copy_without))
    if refactor_digest == proof_digest:
        raise RuntimeError("proof-only refactor did not change proof/build lock")

    compatibility = {
        "schema": "statqed.compatibility-proof-lock.v0",
        "direction": "new_implies_old",
        "new_proposition": "False",
        "old_proposition_digest": proposition_digest,
        "declaration": compatibility_source["declaration"],
        "normalized_type": expr_array(compatibility_source["proposition"]["expression"]),
        "proof_subject": expr_array(compatibility_source["proof_subject"]),
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
        EVIDENCE / "lean-observation.json": canonical_json(observation),
        EVIDENCE / "independent-observation.json": canonical_json(independent),
        EVIDENCE / "axioms.json": axiom_bytes,
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
        ROOT / "theorem-registry/registry.json": canonical_json(registry_index),
        RECORDS / "test-only-true.v0.json": canonical_json(record),
        RECORDS / "snapshot-v0.json": canonical_json(snapshot),
        LOCKS / "proof-build-v0.json": canonical_json(proof_lock),
        LOCKS / "proof-build-refactor-v0.json": canonical_json(copy_without),
        LOCKS / "compatibility-v0.json": canonical_json(compatibility),
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
