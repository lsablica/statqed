#!/usr/bin/env python3
"""Fail-closed static verifier for the SQ-0006 evidence package."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCOPE_BEGIN = "<!-- SQ-0005-NORMATIVE-SCOPE-BEGIN -->"
SCOPE_END = "<!-- SQ-0005-NORMATIVE-SCOPE-END -->"
ALLOWED_SUCCESSOR = {"BLOCKED", "READY", "IN_PROGRESS", "IN_REVIEW", "DONE"}


class EvidenceError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(root: Path, relative: str) -> Any:
    try:
        return json.loads((root / relative).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise EvidenceError(f"invalid required JSON: {relative}") from error


def tree_digest(root: Path, relative: str) -> str:
    base = root / relative
    if not base.is_dir():
        raise EvidenceError(f"missing protected tree: {relative}")
    digest = hashlib.sha256()
    files = []
    for path in base.rglob("*"):
        if path.is_file() and not any(part in {"target", "__pycache__", ".pytest_cache"} for part in path.parts):
            files.append(path)
    for path in sorted(files):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def marked_scope(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if text.count(SCOPE_BEGIN) != 1 or text.count(SCOPE_END) != 1:
        raise EvidenceError(f"invalid normative scope markers: {path}")
    return text.split(SCOPE_BEGIN, 1)[1].split(SCOPE_END, 1)[0]


def markdown_status(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"(?mi)^-?\s*status:\s*([A-Za-z_]+)\s*$", text)
    if match is None:
        raise EvidenceError(f"missing status: {path}")
    return match.group(1)


def markdown_section(path: Path, heading: str) -> str:
    text = path.read_text(encoding="utf-8")
    marker = f"## {heading}\n"
    if text.count(marker) != 1:
        raise EvidenceError(f"missing or duplicate owned section: {path}: {heading}")
    tail = text.split(marker, 1)[1]
    body = tail.split("\n## ", 1)[0]
    return marker + body.rstrip() + "\n"


def dashboard_projection(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    row = "| Data-free foundation fixture schema | 0 | 1 | 0 | 0 |"
    begin = "SQ-0006 adds one Experimental data-free fixture schema:"
    end = "It is neither Candidate nor Stable."
    if text.count(row) != 1 or text.count(begin) != 1 or text.count(end) != 1:
        raise EvidenceError("invalid SQ-0006 dashboard projection")
    body = begin + text.split(begin, 1)[1].split(end, 1)[0] + end
    return row + "\n" + body + "\n"


def document_projection(root: Path, policy: dict[str, str]) -> str:
    path = root / policy["path"]
    if policy["kind"] == "section":
        return markdown_section(path, policy["heading"])
    if policy["kind"] == "dashboard":
        return dashboard_projection(path)
    raise EvidenceError(f"unknown document projection: {policy['kind']}")


def contract_projection(root: Path, task: str) -> tuple[str, str]:
    document = load_json(root, f"work/contracts/{task}.yaml")
    status = document.get("status")
    if status not in ALLOWED_SUCCESSOR:
        raise EvidenceError(f"illegal {task} status: {status}")
    projected = dict(document)
    projected.pop("status", None)
    raw = json.dumps(projected, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode()
    return status, sha256(raw)


def task_map(backlog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {task["id"]: task for task in backlog["tasks"]}


def verify(root: Path = ROOT) -> dict[str, Any]:
    spec = load_json(root, "conformance/schema-v0/evidence/evidence-spec.json")
    manifest = load_json(root, "conformance/schema-v0/evidence/evidence-manifest.json")
    if spec.get("evidence_spec_version") != "statqed.sq0006-evidence-spec.v1":
        raise EvidenceError("unexpected SQ-0006 evidence spec version")
    if manifest.get("evidence_manifest_version") != "statqed.sq0006-evidence.v1":
        raise EvidenceError("unexpected SQ-0006 evidence manifest version")
    if manifest.get("evidence_spec_sha256") != sha256((root / "conformance/schema-v0/evidence/evidence-spec.json").read_bytes()):
        raise EvidenceError("evidence spec hash mismatch")
    subjects = manifest.get("subjects")
    if not isinstance(subjects, list) or len(subjects) != manifest.get("subject_count"):
        raise EvidenceError("evidence subject count mismatch")
    seen = set()
    for subject in subjects:
        relative = subject.get("path")
        if not isinstance(relative, str) or relative in seen or relative.startswith("/") or ".." in Path(relative).parts:
            raise EvidenceError("invalid evidence subject path")
        seen.add(relative)
        path = root / relative
        if not path.is_file() or path.stat().st_size != subject.get("size_bytes") or sha256(path.read_bytes()) != subject.get("sha256"):
            raise EvidenceError(f"evidence subject mismatch: {relative}")
    expected_paths = set()
    manifest_path = root / "conformance/schema-v0/evidence/evidence-manifest.json"
    for pattern in spec.get("subject_patterns", []):
        for path in root.glob(pattern):
            if path.is_file() and path != manifest_path and "__pycache__" not in path.parts:
                expected_paths.add(path.relative_to(root).as_posix())
    if seen != expected_paths:
        raise EvidenceError("evidence subject set does not match specification")
    canonical_subjects = (json.dumps(subjects, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode()
    if sha256(canonical_subjects) != manifest.get("subject_digest"):
        raise EvidenceError("evidence subject digest mismatch")
    scientific = [
        item for item in subjects
        if not item["path"].startswith("work/reviews/")
        and not item["path"].startswith("docs/quality/")
    ]
    scientific_bytes = (json.dumps(scientific, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode()
    if sha256(scientific_bytes) != manifest.get("scientific_subject_digest"):
        raise EvidenceError("scientific subject digest mismatch")

    decisions = spec["accepted_decisions"]
    rfc = root / "rfcs/0001-deterministic-encoding.md"
    adr = root / "docs/adr/0004-deterministic-cbor-cddl.md"
    if markdown_status(rfc) != decisions["rfc_0001_status"] or markdown_status(adr) != decisions["adr_0004_status"]:
        raise EvidenceError("RFC-0001 or ADR-0004 status regression")
    rfc_scope = marked_scope(rfc)
    if rfc_scope != marked_scope(adr) or sha256(rfc_scope.encode()) != decisions["normative_scope_sha256"]:
        raise EvidenceError("RFC-0001 and ADR-0004 normative scope drift")
    adr_0011 = root / "docs/adr/0011-foundation-toy-slice.md"
    adr_0011_policy = spec["adr_0011"]
    if markdown_status(adr_0011) != adr_0011_policy["status"] or sha256(adr_0011.read_bytes()) != adr_0011_policy["sha256"]:
        raise EvidenceError("ADR-0011 reviewed semantic source drift")
    for policy in spec["document_projections"]:
        if sha256(document_projection(root, policy).encode()) != policy["sha256"]:
            raise EvidenceError(f"owned document section drift: {policy['path']}")

    backlog = load_json(root, "work/backlog.yaml")
    status = load_json(root, "work/status.yaml")
    tasks = task_map(backlog)
    sq6_contract = load_json(root, "work/contracts/SQ-0006.yaml")
    sq6_state = sq6_contract.get("status")
    if sq6_state not in {"IN_PROGRESS", "IN_REVIEW", "DONE"} or tasks["SQ-0006"]["status"] != sq6_state:
        raise EvidenceError("SQ-0006 contract/backlog lifecycle mismatch")
    expected_list = {"IN_PROGRESS": "in_progress", "IN_REVIEW": "in_progress", "DONE": "done"}[sq6_state]
    if "SQ-0006" not in status.get(expected_list, []):
        raise EvidenceError("SQ-0006 live ledger lifecycle mismatch")
    for other in {"done", "in_progress", "in_review", "ready"} - {expected_list}:
        if "SQ-0006" in status.get(other, []):
            raise EvidenceError("SQ-0006 appears in multiple live ledger sets")

    projections = spec["live_contract_projections"]
    _, sq6_projection = contract_projection(root, "SQ-0006")
    if sq6_projection != projections["SQ-0006_non_status_sha256"]:
        raise EvidenceError("SQ-0006 non-lifecycle contract drift")
    for task in ("SQ-0007", "SQ-0008", "SQ-0011", "SQ-0013", "SQ-0014", "SQ-0015", "SQ-0027"):
        contract_state, projection = contract_projection(root, task)
        if projection != projections[f"{task}_non_status_sha256"]:
            raise EvidenceError(f"{task} non-lifecycle contract drift")
        if tasks[task]["status"] != contract_state:
            raise EvidenceError(f"{task} contract/backlog lifecycle mismatch")

    baseline = spec["historical_protected_baselines"]
    if tree_digest(root, "schemas/prototypes") != baseline["schemas_prototypes_tree_sha256"]:
        raise EvidenceError("schemas/prototypes contamination")
    owner_roots = {
        "SQ-0008": ("lean", "lean_tree_sha256"),
        "SQ-0011": ("backend", "backend_tree_sha256"),
    }
    for owner, (relative, key) in owner_roots.items():
        if tasks[owner]["status"] in {"BLOCKED", "READY"} and tree_digest(root, relative) != baseline[key]:
            raise EvidenceError(f"protected {relative} contamination before {owner} claim")
    frontend_owners = ("SQ-0013", "SQ-0014", "SQ-0015")
    if all(tasks[owner]["status"] in {"BLOCKED", "READY"} for owner in frontend_owners):
        if tree_digest(root, "frontends") != baseline["frontends_tree_sha256"]:
            raise EvidenceError("protected frontends contamination before successor claim")

    rfc6_owner = next(item["owner"] for item in backlog["decision_register"] if item["id"] == "RFC-0006")
    if rfc6_owner != spec["rfc_0006"]["owner"]:
        raise EvidenceError("RFC-0006 ownership drift")
    if tasks["SQ-0027"]["status"] in {"BLOCKED", "READY"}:
        rfc6 = root / "rfcs/0006-canonical-logical-data-digest.md"
        if sha256(rfc6.read_bytes()) != baseline["rfc_0006_sha256"]:
            raise EvidenceError("RFC-0006 historical baseline drift")
        if markdown_status(rfc6) != spec["rfc_0006"]["status"]:
            raise EvidenceError("RFC-0006 status drift before owner claim")

    results = load_json(root, "conformance/schema-v0/results.json")
    mutations = load_json(root, "conformance/schema-v0/mutations.json")
    fixtures = load_json(root, "schemas/fixtures/v0/manifest.json")
    goldens = load_json(root, "conformance/golden/v0/manifest.json")
    schema_manifest = load_json(root, "schemas/v0/manifest.json")
    expected_pair = ("statqed.foundation-structural.v0", 0)
    if (schema_manifest.get("schema_id"), schema_manifest.get("schema_version")) != expected_pair:
        raise EvidenceError("schema manifest identity/version pair drift")
    if (results.get("schema_id"), results.get("schema_version")) != expected_pair:
        raise EvidenceError("result identity/version pair drift")
    if (goldens.get("schema_id"), goldens.get("schema_version")) != expected_pair:
        raise EvidenceError("golden identity/version pair drift")
    if (fixtures.get("schema_id"), fixtures.get("schema_version")) != expected_pair:
        raise EvidenceError("fixture identity/version pair drift")
    digest_ids = goldens.get("digest_identifiers", {})
    if digest_ids.get("object_class_schema") != expected_pair[0]:
        raise EvidenceError("digest object-class/schema identity drift")
    semantic_source = (root / "scripts/schema/semantic_validator.py").read_text(encoding="utf-8")
    cddl_source = (root / "schemas/v0/source/foundation-structural.cddl").read_text(encoding="utf-8")
    if f'SCHEMA_ID = "{expected_pair[0]}"' not in semantic_source or "SCHEMA_VERSION = 0" not in semantic_source:
        raise EvidenceError("semantic validator identity/version constants drift")
    if f'"schema_id": "{expected_pair[0]}"' not in cddl_source or '"schema_version": schema-version-v0' not in cddl_source:
        raise EvidenceError("CDDL identity/version binding drift")
    if results.get("positive_count") != len(goldens.get("entries", [])) or results.get("negative_count") != fixtures.get("expanded_negative_count"):
        raise EvidenceError("fixture/result/golden count disagreement")
    layer_names = ["profile_decode", "deterministic_bytes", "cddl_shape", "schema_semantics"]
    for result in results.get("results", []):
        layers = result.get("layers", {})
        digest_layer = layers.get("fixture_digest", {})
        if digest_layer.get("status") != "not_reached":
            if any(layers.get(name, {}).get("status") != "accepted" for name in layer_names):
                raise EvidenceError(f"digest evaluated without accepted prerequisites: {result.get('id')}")
        if result.get("classification") == "accepted":
            if result.get("python_digest_verify_code") != "accepted" or result.get("rust_digest_verify_code") != "accepted":
                raise EvidenceError(f"accepted fixture lacks independent digest verification: {result.get('id')}")
    inherited = results.get("inherited_sq0005_resource_evidence", {})
    inherited_path = inherited.get("source")
    if (
        not isinstance(inherited_path, str)
        or len(inherited.get("cases", [])) != 16
        or not (root / inherited_path).is_file()
        or sha256((root / inherited_path).read_bytes()) != inherited.get("source_sha256")
    ):
        raise EvidenceError("inherited SQ-0005 resource evidence drift")
    if not mutations.get("mutations") or not all(item.get("detected") is True for item in mutations["mutations"]):
        raise EvidenceError("deliberate schema mutation escaped")
    for entry in goldens["entries"]:
        for path_key, hash_key in (("cbor_path", "cbor_sha256"), ("frame_path", "frame_sha256")):
            path = root / entry[path_key]
            if not path.is_file() or sha256(path.read_bytes()) != entry[hash_key]:
                raise EvidenceError(f"golden mismatch: {entry[path_key]}")
    return {
        "subjects": len(subjects), "positive": results["positive_count"],
        "negative": results["negative_count"], "mutations": len(mutations["mutations"]),
        "sq6_status": sq6_state,
    }


def main() -> int:
    try:
        result = verify()
    except EvidenceError as error:
        print(f"SQ-0006 evidence verification failed: {error}", file=sys.stderr)
        return 1
    print(
        "SQ-0006 schema evidence verified: "
        f"{result['subjects']} subjects, {result['positive']} positive, "
        f"{result['negative']} negative, {result['mutations']} mutations, "
        f"task {result['sq6_status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
