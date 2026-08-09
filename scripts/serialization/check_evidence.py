#!/usr/bin/env python3
"""Statically verify the content-addressed SQ-0005 evidence package."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = Path("conformance/prototypes/evidence/evidence-manifest.json")
FORBIDDEN_SUBJECT_PREFIXES = (
    "backend/",
    "lean/",
    "frontends/",
    "schemas/v0/",
    "rfcs/0006-canonical-logical-data-digest.md",
)
REVIEW_BEGIN = "<!-- SQ-0005-REVIEW-SUBJECTS-BEGIN -->"
REVIEW_END = "<!-- SQ-0005-REVIEW-SUBJECTS-END -->"
SCOPE_BEGIN = "<!-- SQ-0005-NORMATIVE-SCOPE-BEGIN -->"
SCOPE_END = "<!-- SQ-0005-NORMATIVE-SCOPE-END -->"


class EvidenceError(RuntimeError):
    """One deterministic static evidence failure."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as stream:
            return json.load(stream)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise EvidenceError(f"cannot read JSON {path}: {error}") from error


def checked_relative(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise EvidenceError(f"unsafe evidence path: {value}")
    return path


def repository_path(root: Path, value: str) -> Path:
    return root.joinpath(*checked_relative(value).parts)


def require_file(root: Path, value: str) -> Path:
    path = repository_path(root, value)
    if not path.is_file() or path.is_symlink():
        raise EvidenceError(f"missing regular evidence file: {value}")
    return path


def extract_marked_json(text: str, begin: str, end: str) -> Any:
    start = text.find(begin)
    finish = text.find(end)
    if start < 0 or finish < 0 or finish <= start:
        raise EvidenceError(f"missing marked JSON block: {begin}")
    body = text[start + len(begin) : finish].strip()
    if body.startswith("```json") and body.endswith("```"):
        body = body[len("```json") : -len("```")].strip()
    try:
        return json.loads(body)
    except json.JSONDecodeError as error:
        raise EvidenceError(f"invalid marked JSON block: {error}") from error


def marked_scope(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    start = text.find(SCOPE_BEGIN)
    finish = text.find(SCOPE_END)
    if start < 0 or finish < 0 or finish <= start:
        raise EvidenceError(f"missing normative scope markers: {path}")
    return text[start + len(SCOPE_BEGIN) : finish].strip()


def task(tasks: list[dict[str, Any]], task_id: str) -> dict[str, Any]:
    matches = [item for item in tasks if item.get("id") == task_id]
    if len(matches) != 1:
        raise EvidenceError(f"expected one task {task_id}, found {len(matches)}")
    return matches[0]


def header_status(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines()[:20]:
        match = re.fullmatch(r"- Status: ([A-Za-z]+)", line)
        if match:
            return match.group(1)
    raise EvidenceError(f"missing status header: {path}")


def verify_subjects(root: Path, manifest: dict[str, Any]) -> dict[str, str]:
    subjects = manifest.get("subjects")
    if not isinstance(subjects, list) or not subjects:
        raise EvidenceError("manifest subjects must be a nonempty list")
    paths = [item.get("path") for item in subjects if isinstance(item, dict)]
    if len(paths) != len(subjects) or paths != sorted(paths) or len(set(paths)) != len(paths):
        raise EvidenceError("manifest subject paths must be unique and sorted")
    observed: dict[str, str] = {}
    for item in subjects:
        path_value = item["path"]
        if any(
            path_value == prefix.rstrip("/") or path_value.startswith(prefix)
            for prefix in FORBIDDEN_SUBJECT_PREFIXES
        ):
            raise EvidenceError(f"production or RFC-0006 contamination: {path_value}")
        path = require_file(root, path_value)
        digest = sha256(path)
        if digest != item.get("sha256"):
            raise EvidenceError(f"subject SHA-256 mismatch: {path_value}")
        if not isinstance(item.get("role"), str) or not item["role"]:
            raise EvidenceError(f"missing subject role: {path_value}")
        observed[path_value] = digest
    return observed


def verify_coverage(root: Path, manifest: dict[str, Any], subjects: set[str]) -> None:
    for coverage in manifest.get("coverage_roots", []):
        prefix = coverage.get("path")
        extensions = tuple(coverage.get("extensions", []))
        directory = repository_path(root, prefix)
        if not directory.is_dir():
            raise EvidenceError(f"missing coverage root: {prefix}")
        actual = {
            path.relative_to(root).as_posix()
            for path in directory.rglob("*")
            if path.is_file()
            and not path.is_symlink()
            and (not extensions or path.suffix in extensions)
            and path.relative_to(root).as_posix()
            != "conformance/prototypes/evidence/evidence-manifest.json"
        }
        missing = sorted(actual - subjects)
        if missing:
            raise EvidenceError("unbound covered evidence: " + ", ".join(missing))


def fixture_cases(root: Path) -> list[dict[str, Any]]:
    directory = root / "conformance/prototypes/fixtures/semantic-v1"
    catalog = load_json(directory / "catalog.json")
    cases: list[dict[str, Any]] = []
    seen: set[str] = set()
    for component in catalog.get("components", []):
        data = load_json(directory / component)
        for case in data.get("cases", []):
            case_id = case.get("id")
            if not isinstance(case_id, str) or case_id in seen:
                raise EvidenceError(f"invalid or duplicate fixture ID: {case_id}")
            seen.add(case_id)
            cases.append(case)
    if catalog.get("unresolved"):
        raise EvidenceError("semantic fixture catalog retains unresolved blockers")
    return cases


def verify_fixture_coverage(root: Path, manifest: dict[str, Any]) -> None:
    cases = fixture_cases(root)
    negative = sorted(case["id"] for case in cases if not case.get("accept"))
    accepted = sorted(
        case["id"]
        for case in cases
        if case.get("accept")
        and case.get("expected_encoding", {}).get("kind") != "none"
    )
    if negative != manifest.get("negative_fixture_ids"):
        raise EvidenceError("negative fixture manifest is missing or stale")
    if accepted != manifest.get("accepted_fixture_ids"):
        raise EvidenceError("accepted fixture manifest is missing or stale")
    golden = load_json(
        root / "conformance/prototypes/golden/serialization-v1/manifest.json"
    )
    golden_ids = sorted(item.get("fixture_id") for item in golden.get("vectors", []))
    if accepted != golden_ids:
        raise EvidenceError("golden vector manifest does not cover every accepted fixture")
    if any(not require_file(root, item["path"]) for item in golden["vectors"]):
        raise EvidenceError("unreachable golden-vector path check")


def verify_failures(root: Path, manifest: dict[str, Any]) -> None:
    failures = manifest.get("retained_failures", [])
    if not failures:
        raise EvidenceError("no retained failure records")
    for value in failures:
        path = require_file(root, value)
        if path.stat().st_size == 0:
            raise EvidenceError(f"empty retained failure record: {value}")


def verify_lineage(root: Path, manifest: dict[str, Any]) -> None:
    lineage = load_json(root / "schemas/prototypes/lineage.json")
    implementations = lineage.get("implementations", [])
    if len(implementations) < 2:
        raise EvidenceError("fewer than two implementation lineages")
    ids = [item.get("id") for item in implementations]
    languages = [item.get("language") for item in implementations]
    canonicalizers = [item.get("canonicalizer_lineage") for item in implementations]
    source_roots = [item.get("source_root") for item in implementations]
    if len(set(ids)) != len(ids) or len(set(languages)) < 2:
        raise EvidenceError("implementation identities or languages are not independent")
    if len(set(canonicalizers)) != len(canonicalizers):
        raise EvidenceError("implementations falsely share canonicalizer lineage")
    if len(set(source_roots)) != len(source_roots):
        raise EvidenceError("implementations falsely share source roots")
    known = set(ids)
    for item in implementations:
        source_root = item.get("source_root", "")
        if source_root.startswith(("backend/", "lean/", "frontends/")):
            raise EvidenceError("production implementation claimed as prototype lineage")
        require_file(root, item["record_path"])
        forbidden = known - {item["id"]}
        if forbidden.intersection(item.get("calls", [])) or forbidden.intersection(
            item.get("consumes_outputs_from", [])
        ):
            raise EvidenceError("implementation lineage consumes another candidate")
    declared = sorted(item.get("id") for item in manifest.get("independent_origins", []))
    if declared != sorted(ids):
        raise EvidenceError("manifest independent-origin declarations are stale")


def verify_review(root: Path, manifest_path: str, manifest: dict[str, Any]) -> None:
    review_path = require_file(root, manifest["review_record"])
    review = review_path.read_text(encoding="utf-8")
    bindings = extract_marked_json(review, REVIEW_BEGIN, REVIEW_END)
    expected_paths = manifest.get("review_subject_paths", [])
    if sorted(bindings) != sorted(expected_paths):
        raise EvidenceError("review subject path set is stale")
    for value, expected in bindings.items():
        if sha256(require_file(root, value)) != expected:
            raise EvidenceError(f"stale review hash: {value}")
    if manifest_path not in bindings:
        raise EvidenceError("review does not bind the evidence manifest")


def verify_status_and_scope(root: Path, manifest: dict[str, Any]) -> None:
    expected = manifest["expected_state"]
    backlog = load_json(root / "work/backlog.yaml")
    status = load_json(root / "work/status.yaml")
    contract5 = load_json(root / "work/contracts/SQ-0005.yaml")
    contract6 = load_json(root / "work/contracts/SQ-0006.yaml")
    contract8 = load_json(root / "work/contracts/SQ-0008.yaml")
    backlog5 = task(backlog["tasks"], "SQ-0005")
    backlog6 = task(backlog["tasks"], "SQ-0006")
    backlog8 = task(backlog["tasks"], "SQ-0008")
    checks = {
        "contract_sq0005": contract5.get("status"),
        "contract_sq0006": contract6.get("status"),
        "contract_sq0008": contract8.get("status"),
        "backlog_sq0005": backlog5.get("status"),
        "backlog_sq0006": backlog6.get("status"),
        "backlog_sq0008": backlog8.get("status"),
        "rfc0001": header_status(root / "rfcs/0001-deterministic-encoding.md"),
        "adr0004": header_status(
            root / "docs/adr/0004-deterministic-cbor-cddl.md"
        ),
    }
    if checks != expected["statuses"]:
        raise EvidenceError(f"task/RFC/ADR status drift: {checks}")
    if sorted(status.get("ready", [])) != sorted(expected["ready"]):
        raise EvidenceError("work/status ready set drift")
    if sorted(status.get("in_progress", [])) != sorted(expected["in_progress"]):
        raise EvidenceError("work/status in-progress set drift")
    if sorted(status.get("done", [])) != sorted(expected["done"]):
        raise EvidenceError("work/status done set drift")
    if status.get("blocked_count") != expected["blocked_count"]:
        raise EvidenceError("work/status blocked count drift")
    rfc = root / "rfcs/0001-deterministic-encoding.md"
    adr = root / "docs/adr/0004-deterministic-cbor-cddl.md"
    if marked_scope(rfc) != marked_scope(adr):
        raise EvidenceError("RFC-0001 and ADR-0004 normative scopes disagree")


def verify_rfc6_and_protected(root: Path, manifest: dict[str, Any]) -> None:
    rfc6 = require_file(root, "rfcs/0006-canonical-logical-data-digest.md")
    baseline = manifest["baseline"]
    if sha256(rfc6) != baseline["rfc0006_sha256"]:
        raise EvidenceError("RFC-0006 changed")
    if header_status(rfc6) != "Draft":
        raise EvidenceError("RFC-0006 is not Draft")
    backlog = load_json(root / "work/backlog.yaml")
    owners = {
        item.get("id"): item.get("owner") for item in backlog["decision_register"]
    }
    if owners.get("RFC-0006") != "SQ-0027":
        raise EvidenceError("RFC-0006 ownership drift")
    sq0008 = require_file(root, "work/contracts/SQ-0008.yaml")
    if sha256(sq0008) != baseline["sq0008_contract_sha256"]:
        raise EvidenceError("SQ-0008 contract changed")
    protected = manifest.get("protected_files", [])
    protected_paths = [item.get("path") for item in protected]
    if protected_paths != sorted(protected_paths) or len(set(protected_paths)) != len(
        protected_paths
    ):
        raise EvidenceError("protected file list is not unique and sorted")
    for item in protected:
        if sha256(require_file(root, item["path"])) != item["sha256"]:
            raise EvidenceError(f"protected production file changed: {item['path']}")
    expected_protected = set(protected_paths)
    actual_protected: set[str] = set()
    for prefix in manifest.get("protected_prefixes", []):
        directory = repository_path(root, prefix)
        if not directory.is_dir():
            raise EvidenceError(f"protected directory missing: {prefix}")
        for path in directory.rglob("*"):
            if (
                path.is_file()
                and not path.is_symlink()
                and not any(
                    part in {"target", ".lake", "__pycache__", ".pytest_cache"}
                    for part in path.relative_to(root).parts
                )
                and path.suffix not in {".pyc", ".pyo"}
            ):
                actual_protected.add(path.relative_to(root).as_posix())
    extras = sorted(actual_protected - expected_protected)
    missing = sorted(expected_protected - actual_protected)
    if extras or missing:
        raise EvidenceError(
            "protected production path-set drift: extras="
            + ",".join(extras)
            + " missing="
            + ",".join(missing)
        )
    if (root / "schemas/v0").exists():
        raise EvidenceError("schemas/v0 was created during SQ-0005")


def verify(root: Path, manifest_value: str) -> dict[str, Any]:
    manifest_path = require_file(root, manifest_value)
    manifest = load_json(manifest_path)
    if manifest.get("schema") != "statqed.sq0005-evidence.v1":
        raise EvidenceError("unsupported evidence manifest schema")
    subjects = verify_subjects(root, manifest)
    verify_coverage(root, manifest, set(subjects))
    verify_fixture_coverage(root, manifest)
    verify_failures(root, manifest)
    verify_lineage(root, manifest)
    verify_status_and_scope(root, manifest)
    verify_rfc6_and_protected(root, manifest)
    verify_review(root, manifest_value, manifest)
    return {
        "manifest_sha256": sha256(manifest_path),
        "negative_fixture_count": len(manifest["negative_fixture_ids"]),
        "protected_file_count": len(manifest["protected_files"]),
        "status": "verified",
        "subject_count": len(subjects),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST.as_posix())
    parser.add_argument("--json", action="store_true")
    arguments = parser.parse_args()
    root = arguments.root.resolve()
    try:
        result = verify(root, arguments.manifest)
    except (EvidenceError, OSError, UnicodeDecodeError) as error:
        if arguments.json:
            print(json.dumps({"error": str(error), "status": "rejected"}, sort_keys=True))
        else:
            print(f"SQ-0005 evidence rejected: {error}", file=sys.stderr)
        return 1
    if arguments.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(
            "SQ-0005 serialization evidence verified: "
            f"{result['subject_count']} subjects, "
            f"{result['negative_fixture_count']} negative fixtures"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
