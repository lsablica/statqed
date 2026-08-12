#!/usr/bin/env python3
"""Fail-closed static verifier for the SQ-0006 evidence package."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCOPE_BEGIN = "<!-- SQ-0005-NORMATIVE-SCOPE-BEGIN -->"
SCOPE_END = "<!-- SQ-0005-NORMATIVE-SCOPE-END -->"
EXPECTED_HISTORICAL_MANIFEST_SHA256 = "eefe309c3ab16d05321e5071698009b716721b8c1119c7c48bf4fa37d60521eb"
EXPECTED_HISTORICAL_SCIENTIFIC_SHA256 = "4bfd5fad7f9884d592d5c8c320dbd4efd735c990f3b23d6b3cb5d8e9854df5f0"
EXPECTED_HISTORICAL_LIFECYCLE_MANIFEST_SHA256 = "5c6b3081846ba8ec2bc1ac17bf7d9014ee4d8f2dedb9e7d625a1226d2957b752"
EXPECTED_SUCCESSOR_HISTORY = {
    "SQ-0007": (
        "bddf4334bbef4391b6024010f6073bcec34c272d9e15809f54d6ee927de5c4e2",
        "60cb7493c9f4828ba8b8c4583698f084f589103deadcc9b5d7bb9dc05e7389fb",
    ),
    "SQ-0008": (
        "8ca1d8f0a50abc6d081cd2b3b73456a334f6ac43a2572576b6b452553ec8d471",
        "c5b7f222b914f2dab8fc2c8592979d20150ddb0d8c4700669c5bf923f977f9e4",
    ),
    "SQ-0011": (
        "a6dd037dc74e81c681161b79ac324fae8093bef5f8449a0322d93f45962a7b12",
        "63b2dd821a27d6732aa910a608fea139b3bc76d3a2e006a0cf198c01fe406654",
    ),
    "SQ-0013": (
        "8132e0887c5d5765b608944761946a046ee4ea2597e1e7eb90eea825780e9290",
        "b36645159632f2cf055d32c378e5240e49690af2393cf05223ec68cf51664f82",
    ),
    "SQ-0014": (
        "0faa9eac82339efb08d55e8cc633de29988366dfb599dd9f968e92d24c38468b",
        "2a2b688e94b574a478d563782eba913c83f1fcd36193ffd14cc305e57be9f21b",
    ),
    "SQ-0015": (
        "c17d1c85574980ead5a7224f213d3277d14e3c21e3145d1c74ef76ba4624227b",
        "f22cfb53af999a8272205468a185844755609934b24b1f0f1dd61d61523b6988",
    ),
}
EXPECTED_LEGAL_STATUSES = ("BLOCKED", "READY", "IN_PROGRESS", "IN_REVIEW", "DONE", "SUPERSEDED")
EXPECTED_AUTHORIZING_STATUSES = ("IN_PROGRESS", "IN_REVIEW", "DONE")
EXPECTED_MAINTENANCE_LIVE_BASELINE_PATHS = (
    ".github/workflows/lean.yml",
    "docs/implementation/lean-core.md",
    "lean/README.md",
    "lean/Reports/foundation-axiom-history.json",
    "lean/Tests/ProjectAxiomProbe.lean",
    "lean/Tests/Trust/expectations.json",
    "lean/Tests/Trust/registry_axiom.lean.fixture",
    "lean/Tests/Trust/registry_native.lean.fixture",
    "lean/Tests/Trust/registry_safe.lean.fixture",
    "lean/Tests/Trust/registry_sorry.lean.fixture",
    "lean/Tests/Trust/registry_unimportable.lean.fixture",
    "lean/Tests/Trust/registry_unsafe.lean.fixture",
    "lean/tools/check_all_modules.py",
    "lean/tools/no_cache_build.sh",
    "lean/tools/project_axiom_report.py",
    "lean/tools/tests/test_project_trust.py",
    "scripts/check_lean_trust.py",
)
EXPECTED_LIFECYCLE_PATHS = (
    "conformance/schema-v0/evidence/evidence-spec.json",
    "scripts/schema/build_evidence_manifest.py",
    "scripts/schema/check_schema_v0.py",
    "scripts/schema/tests/test_check_schema_v0.py",
)
EXPECTED_PATH_PARTITIONS = {
    "lean_registry": (
        "lean", ("lean/StatQED/Registry",), (), ("SQ-0007",),
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 0,
    ),
    "lean_assurance": (
        "lean", ("lean/StatQED/Assurance",), (), ("SQ-0008",),
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 0,
    ),
    "lean_guarantee": (
        "lean", ("lean/StatQED/Guarantee",), (), ("SQ-0008",),
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 0,
    ),
    "lean_remainder": (
        "lean",
        (),
        ("lean/StatQED/Registry", "lean/StatQED/Assurance", "lean/StatQED/Guarantee"),
        (),
        "5fe397a8b53bfb2488f8dd81e9d7d0d8896c65f754ae8a280db5a8f2125ff184", 67,
    ),
    "backend_registry": (
        "backend",
        ("backend/crates/statqed-registry",),
        (),
        ("SQ-0007", "SQ-0011"),
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 0,
    ),
    "backend_remainder": (
        "backend", (), ("backend/crates/statqed-registry",), ("SQ-0011",),
        "5f2891a03d785e9a4652f756681cf288e15e8914bccfafe27e3250802c8dbd42", 22,
    ),
    "frontend_r": (
        "frontends", ("frontends/r",), (), ("SQ-0013",),
        "d88fe7e954b179850bc926edee0db668e32cad8981f66697defd3b4693962e41", 2,
    ),
    "frontend_python": (
        "frontends", ("frontends/python",), (), ("SQ-0014",),
        "5568aa52ec47fea334d2e2ce97052edba5769e9118b5c6ac45e1da907cf60f4a", 2,
    ),
    "frontend_julia": (
        "frontends", ("frontends/julia",), (), ("SQ-0015",),
        "5f68e97ec97b290bb8264f25f25b151e6bb138f088f6518020f8a1bacfc3c317", 2,
    ),
    "frontends_remainder": (
        "frontends",
        (),
        ("frontends/r", "frontends/python", "frontends/julia"),
        (), "8265f27bb2b1ca9f890f09194d63fa1ac27841a9645c5b9e58f1301e8bc16983", 2,
    ),
    "schemas_prototypes": (
        "schemas/prototypes", (), (), (),
        "c766b55670d8722bb17ec42d1eea6ecf556926f6573886f7125d4be977a5dc29", 32,
    ),
}
EXPECTED_IGNORED_PREFIXES = (
    "lean/.lake",
    "lean/tools/__pycache__",
    "lean/tools/tests/__pycache__",
    "backend/target",
    "schemas/prototypes/rust-cbor/target",
    "schemas/prototypes/python-oracle/.pytest_cache",
    "schemas/prototypes/python-oracle/statqed_oracle/__pycache__",
    "schemas/prototypes/python-oracle/tests/__pycache__",
)


class EvidenceError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode()


def load_json(root: Path, relative: str) -> Any:
    try:
        return json.loads((root / relative).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise EvidenceError(f"invalid required JSON: {relative}") from error


def under_prefix(relative: str, prefix: str) -> bool:
    return relative == prefix or relative.startswith(prefix + "/")


def partition_matches(relative: str, policy: dict[str, Any]) -> bool:
    includes = policy["include_prefixes"]
    excludes = policy["exclude_prefixes"]
    return (not includes or any(under_prefix(relative, prefix) for prefix in includes)) and not any(
        under_prefix(relative, prefix) for prefix in excludes
    )


def tracked_paths(root: Path, relative: str) -> set[str] | None:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--", relative],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return {item.decode() for item in result.stdout.split(b"\0") if item}


def protected_files(root: Path, relative: str, ignored: tuple[str, ...]) -> list[tuple[str, Path]]:
    base = root / relative
    if not base.is_dir():
        raise EvidenceError(f"missing protected tree: {relative}")
    tracked = tracked_paths(root, relative)
    files: list[tuple[str, Path]] = []
    for directory, directory_names, file_names in os.walk(base, topdown=True, followlinks=False):
        current = Path(directory)
        kept_directories: list[str] = []
        for name in sorted(directory_names):
            path = current / name
            item = path.relative_to(root).as_posix()
            if path.is_symlink():
                raise EvidenceError(f"protected path symlink: {item}")
            if any(under_prefix(item, prefix) for prefix in ignored):
                if tracked is None:
                    raise EvidenceError(f"unverifiable ignored protected path: {item}")
                tracked_below = sorted(entry for entry in tracked if under_prefix(entry, item))
                if tracked_below:
                    raise EvidenceError(
                        f"tracked protected path under ignored cache: {tracked_below[0]}"
                    )
                continue
            kept_directories.append(name)
        directory_names[:] = kept_directories
        for name in sorted(file_names):
            path = current / name
            item = path.relative_to(root).as_posix()
            if path.is_symlink():
                raise EvidenceError(f"protected path symlink: {item}")
            if not path.is_file():
                raise EvidenceError(f"protected path special file: {item}")
            if any(under_prefix(item, prefix) for prefix in ignored):
                if tracked is None:
                    raise EvidenceError(f"unverifiable ignored protected path: {item}")
                if item in tracked:
                    raise EvidenceError(f"tracked protected path under ignored cache: {item}")
                continue
            files.append((item, path))
    return sorted(files)


def protected_partition_digest(
    files: list[tuple[str, Path]], policy: dict[str, Any]
) -> tuple[str, int]:
    digest = hashlib.sha256()
    selected = [(relative, path) for relative, path in files if partition_matches(relative, policy)]
    for relative, path in selected:
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(b"x" if path.stat().st_mode & 0o111 else b"-")
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest(), len(selected)


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


def contract_projection(root: Path, task: str, legal_statuses: set[str]) -> tuple[str, str]:
    document = load_json(root, f"work/contracts/{task}.yaml")
    status = document.get("status")
    if status not in legal_statuses:
        raise EvidenceError(f"illegal {task} status: {status}")
    projected = dict(document)
    projected.pop("status", None)
    raw = json.dumps(projected, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode()
    return status, sha256(raw)


def task_map(backlog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {task["id"]: task for task in backlog["tasks"]}


def validate_historical_completion(
    manifest: dict[str, Any], policy: dict[str, Any]
) -> list[dict[str, Any]]:
    historical = manifest.get("historical_completion")
    if not isinstance(historical, dict):
        raise EvidenceError("missing historical SQ-0006 completion manifest")
    if sha256(canonical(historical)) != EXPECTED_HISTORICAL_MANIFEST_SHA256:
        raise EvidenceError("historical SQ-0006 completion manifest drift")
    expected_fields = {
        "evidence_manifest_version": policy["evidence_manifest_version"],
        "evidence_spec_sha256": policy["evidence_spec_sha256"],
        "subject_count": policy["subject_count"],
        "subject_digest": policy["subject_digest"],
        "scientific_subject_digest": policy["scientific_subject_digest"],
    }
    for field, expected in expected_fields.items():
        if historical.get(field) != expected:
            raise EvidenceError(f"historical SQ-0006 {field} drift")
    subjects = historical.get("subjects")
    if not isinstance(subjects, list) or len(subjects) != historical.get("subject_count"):
        raise EvidenceError("historical SQ-0006 subject count mismatch")
    if sha256(canonical(subjects)) != historical.get("subject_digest"):
        raise EvidenceError("historical SQ-0006 subject digest mismatch")
    historical_scientific = [
        item for item in subjects
        if not item["path"].startswith("work/reviews/")
        and not item["path"].startswith("docs/quality/")
    ]
    if sha256(canonical(historical_scientific)) != EXPECTED_HISTORICAL_SCIENTIFIC_SHA256:
        raise EvidenceError("historical SQ-0006 scientific subject digest mismatch")
    return subjects


def validate_live_ledger(
    backlog: dict[str, Any], status: dict[str, Any], tasks: dict[str, dict[str, Any]], legal: set[str]
) -> None:
    expected = {"done": [], "ready": [], "in_progress": []}
    blocked_count = 0
    for task_id, task in tasks.items():
        state = task.get("status")
        if state not in legal:
            raise EvidenceError(f"illegal backlog status: {task_id}: {state}")
        if state == "DONE":
            expected["done"].append(task_id)
        elif state == "READY":
            expected["ready"].append(task_id)
        elif state in {"IN_PROGRESS", "IN_REVIEW"}:
            expected["in_progress"].append(task_id)
        elif state == "BLOCKED":
            blocked_count += 1
    for key, expected_items in expected.items():
        actual = status.get(key)
        if not isinstance(actual, list) or actual != sorted(expected_items):
            raise EvidenceError(f"live ledger {key} disagrees with backlog")
        if len(actual) != len(set(actual)):
            raise EvidenceError(f"duplicate live ledger entry: {key}")
    represented = [item for key in expected for item in status.get(key, [])]
    if len(represented) != len(set(represented)):
        raise EvidenceError("task appears in multiple live ledger sets")
    if status.get("blocked_count") != blocked_count:
        raise EvidenceError("live ledger blocked count disagrees with backlog")


def verify(root: Path = ROOT) -> dict[str, Any]:
    spec = load_json(root, "conformance/schema-v0/evidence/evidence-spec.json")
    manifest = load_json(root, "conformance/schema-v0/evidence/evidence-manifest.json")
    if spec.get("evidence_spec_version") != "statqed.sq0006-evidence-spec.v3":
        raise EvidenceError("unexpected SQ-0006 evidence spec version")
    if manifest.get("evidence_manifest_version") != "statqed.sq0006-evidence.v3":
        raise EvidenceError("unexpected SQ-0006 evidence manifest version")
    if manifest.get("evidence_spec_sha256") != sha256((root / "conformance/schema-v0/evidence/evidence-spec.json").read_bytes()):
        raise EvidenceError("evidence spec hash mismatch")
    historical_policy = spec["historical_completion_manifest"]
    if historical_policy.get("manifest_sha256") != EXPECTED_HISTORICAL_MANIFEST_SHA256:
        raise EvidenceError("historical completion policy drift")
    if historical_policy.get("scientific_subject_digest") != EXPECTED_HISTORICAL_SCIENTIFIC_SHA256:
        raise EvidenceError("historical scientific policy drift")
    historical_subjects = validate_historical_completion(manifest, historical_policy)
    if manifest.get("historical_completion_manifest_sha256") != EXPECTED_HISTORICAL_MANIFEST_SHA256:
        raise EvidenceError("historical completion binding drift")
    if manifest.get("historical_scientific_subject_digest") != EXPECTED_HISTORICAL_SCIENTIFIC_SHA256:
        raise EvidenceError("historical scientific binding drift")
    lifecycle_policy = spec.get("historical_lifecycle_manifest", {})
    if lifecycle_policy.get("manifest_sha256") != EXPECTED_HISTORICAL_LIFECYCLE_MANIFEST_SHA256:
        raise EvidenceError("historical v2 lifecycle policy drift")
    historical_lifecycle = manifest.get("historical_lifecycle")
    if not isinstance(historical_lifecycle, dict) or sha256(canonical(historical_lifecycle)) != EXPECTED_HISTORICAL_LIFECYCLE_MANIFEST_SHA256:
        raise EvidenceError("historical SQ-0006 v2 lifecycle manifest drift")
    if manifest.get("historical_lifecycle_manifest_sha256") != EXPECTED_HISTORICAL_LIFECYCLE_MANIFEST_SHA256:
        raise EvidenceError("historical v2 lifecycle binding drift")
    for field in (
        "evidence_manifest_version",
        "evidence_spec_sha256",
        "historical_completion_manifest_sha256",
        "historical_scientific_subject_digest",
        "immutable_scientific_subject_count",
        "immutable_scientific_subject_digest",
        "live_subject_count",
        "live_subject_digest",
    ):
        if historical_lifecycle.get(field) != lifecycle_policy.get(field):
            raise EvidenceError(f"historical SQ-0006 v2 {field} drift")
    if historical_lifecycle.get("historical_completion") != manifest.get("historical_completion"):
        raise EvidenceError("historical SQ-0006 v1/v2 completion disagreement")

    subjects = manifest.get("live_subjects")
    if not isinstance(subjects, list) or len(subjects) != manifest.get("live_subject_count"):
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
    if sha256(canonical_subjects) != manifest.get("live_subject_digest"):
        raise EvidenceError("evidence subject digest mismatch")

    immutable_policy = spec["historical_immutable_scientific_subjects"]
    if tuple(immutable_policy["excluded_lifecycle_paths"]) != EXPECTED_LIFECYCLE_PATHS:
        raise EvidenceError("lifecycle-maintenance path policy drift")
    excluded_lifecycle = set(EXPECTED_LIFECYCLE_PATHS)
    historical_immutable = [
        item for item in historical_subjects
        if not item["path"].startswith("work/reviews/")
        and not item["path"].startswith("docs/quality/")
        and item["path"] not in excluded_lifecycle
    ]
    historical_immutable_digest = sha256(canonical(historical_immutable))
    if (
        immutable_policy["subject_count"] != len(historical_immutable)
        or immutable_policy["subject_digest"] != historical_immutable_digest
    ):
        raise EvidenceError("historical immutable scientific policy drift")
    immutable_scientific = [
        item for item in subjects
        if not item["path"].startswith("work/reviews/")
        and not item["path"].startswith("docs/quality/")
        and item["path"] not in excluded_lifecycle
    ]
    if len(immutable_scientific) != immutable_policy["subject_count"]:
        raise EvidenceError("immutable scientific subject count mismatch")
    if immutable_scientific != historical_immutable:
        raise EvidenceError("immutable scientific subjects differ from completion history")
    if sha256(canonical(immutable_scientific)) != immutable_policy["subject_digest"]:
        raise EvidenceError("immutable scientific subject digest mismatch")
    if manifest.get("immutable_scientific_subject_count") != immutable_policy["subject_count"]:
        raise EvidenceError("manifest immutable scientific subject count drift")
    if manifest.get("immutable_scientific_subject_digest") != immutable_policy["subject_digest"]:
        raise EvidenceError("manifest immutable scientific subject digest drift")
    lifecycle_subjects = [item for item in subjects if item["path"] in excluded_lifecycle]
    if {item["path"] for item in lifecycle_subjects} != excluded_lifecycle:
        raise EvidenceError("lifecycle-maintenance subject set mismatch")
    if sha256(canonical(lifecycle_subjects)) != manifest.get("lifecycle_subject_digest"):
        raise EvidenceError("lifecycle-maintenance subject digest mismatch")
    maintenance_paths = spec.get("maintenance_live_baseline_paths")
    if not isinstance(maintenance_paths, list) or tuple(maintenance_paths) != EXPECTED_MAINTENANCE_LIVE_BASELINE_PATHS:
        raise EvidenceError("invalid maintenance live baseline path policy")
    maintenance_live = manifest.get("maintenance_live_baselines")
    if not isinstance(maintenance_live, list) or [item.get("path") for item in maintenance_live] != maintenance_paths:
        raise EvidenceError("maintenance live baseline set mismatch")
    for subject in maintenance_live:
        relative = subject["path"]
        path = root / relative
        if path.is_symlink() or not path.is_file() or path.stat().st_size != subject.get("size_bytes") or sha256(path.read_bytes()) != subject.get("sha256"):
            raise EvidenceError(f"maintenance live baseline mismatch: {relative}")
    if sha256(canonical(maintenance_live)) != manifest.get("maintenance_live_baseline_digest"):
        raise EvidenceError("maintenance live baseline digest mismatch")

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
    live_policy = spec["live_invariants"]
    if tuple(live_policy["legal_task_statuses"]) != EXPECTED_LEGAL_STATUSES:
        raise EvidenceError("legal task status policy drift")
    if tuple(live_policy["owner_authorizing_statuses"]) != EXPECTED_AUTHORIZING_STATUSES:
        raise EvidenceError("owner authorizing status policy drift")
    legal_statuses = set(live_policy["legal_task_statuses"])
    authorizing_statuses = set(live_policy["owner_authorizing_statuses"])
    validate_live_ledger(backlog, status, tasks, legal_statuses)

    sq6_state, sq6_projection = contract_projection(root, "SQ-0006", legal_statuses)
    if sq6_state != "DONE" or tasks["SQ-0006"]["status"] != "DONE":
        raise EvidenceError("SQ-0006 contract/backlog lifecycle mismatch")
    if "SQ-0006" not in status.get("done", []):
        raise EvidenceError("SQ-0006 live ledger lifecycle mismatch")
    if sq6_projection != live_policy["sq0006_non_status_sha256"]:
        raise EvidenceError("SQ-0006 non-lifecycle contract drift")

    historical_successors = spec["historical_successor_contracts"]
    if set(historical_successors) != set(EXPECTED_SUCCESSOR_HISTORY):
        raise EvidenceError("historical successor contract set drift")
    for task, (file_hash, projection_hash) in EXPECTED_SUCCESSOR_HISTORY.items():
        observed = historical_successors[task]
        if observed != {
            "status": "READY",
            "file_sha256": file_hash,
            "non_status_sha256": projection_hash,
        }:
            raise EvidenceError(f"historical {task} contract evidence drift")

    successors = set(live_policy["successor_tasks"])
    if successors != set(EXPECTED_SUCCESSOR_HISTORY):
        raise EvidenceError("live successor task policy drift")
    for task in sorted(successors | {"SQ-0027"}):
        contract_state, _ = contract_projection(root, task, legal_statuses)
        if tasks[task]["status"] != contract_state:
            raise EvidenceError(f"{task} contract/backlog lifecycle mismatch")

    baseline = spec["historical_protected_baselines"]
    path_policy = spec["protected_path_policy"]
    ignored_prefixes = tuple(path_policy["ignored_prefixes"])
    if ignored_prefixes != EXPECTED_IGNORED_PREFIXES:
        raise EvidenceError("protected path ignore policy drift")
    partitions = path_policy["partitions"]
    if {item.get("id") for item in partitions} != set(EXPECTED_PATH_PARTITIONS):
        raise EvidenceError("protected path partition set drift")
    files_by_root: dict[str, list[tuple[str, Path]]] = {}
    policies_by_root: dict[str, list[dict[str, Any]]] = {}
    for policy in partitions:
        expected_root, includes, excludes, owners, expected_digest, expected_count = EXPECTED_PATH_PARTITIONS[
            policy["id"]
        ]
        if (
            policy.get("root") != expected_root
            or tuple(policy.get("include_prefixes", [])) != includes
            or tuple(policy.get("exclude_prefixes", [])) != excludes
            or tuple(policy.get("owners", [])) != owners
            or policy.get("baseline_sha256") != expected_digest
            or policy.get("baseline_file_count") != expected_count
        ):
            raise EvidenceError(f"protected path policy drift: {policy['id']}")
        if any(owner not in successors for owner in owners):
            raise EvidenceError(f"unknown protected path owner: {policy['id']}")
        policies_by_root.setdefault(expected_root, []).append(policy)
        files_by_root.setdefault(expected_root, protected_files(root, expected_root, ignored_prefixes))
    for relative, files in files_by_root.items():
        for path, _ in files:
            matching = [policy["id"] for policy in policies_by_root[relative] if partition_matches(path, policy)]
            if len(matching) != 1:
                raise EvidenceError(f"protected path ownership is not unique: {path}")
    for policy in partitions:
        digest, count = protected_partition_digest(files_by_root[policy["root"]], policy)
        owners = policy["owners"]
        owner_active = any(tasks[owner]["status"] in authorizing_statuses for owner in owners)
        if not owner_active and (
            digest != policy["baseline_sha256"] or count != policy["baseline_file_count"]
        ):
            raise EvidenceError(f"protected path contamination before owner claim: {policy['id']}")

    rfc6_owner = next(item["owner"] for item in backlog["decision_register"] if item["id"] == "RFC-0006")
    if rfc6_owner != spec["rfc_0006"]["owner"]:
        raise EvidenceError("RFC-0006 ownership drift")
    if tasks["SQ-0027"]["status"] not in authorizing_statuses:
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
