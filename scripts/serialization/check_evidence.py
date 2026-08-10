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
EXPECTED_HISTORICAL_COMPLETION_STATE = {
    "blocked_count": 53,
    "done": ["SQ-0001", "SQ-0002", "SQ-0003", "SQ-0004", "SQ-0005"],
    "in_progress": [],
    "ready": ["SQ-0006", "SQ-0008"],
    "schemas_v0_present": False,
    "statuses": {
        "adr0004": "Accepted",
        "backlog_sq0005": "DONE",
        "backlog_sq0006": "READY",
        "backlog_sq0008": "READY",
        "contract_sq0005": "DONE",
        "contract_sq0006": "READY",
        "contract_sq0008": "READY",
        "rfc0001": "Accepted",
    },
}
EXPECTED_HISTORICAL_REVIEW = {
    "path": "work/reviews/SQ-0005.md",
    "sha256": "a45c57c5abf9d99b89a5c5b86143da34651728a86b3b72d8ca7d5886a62f3ff7",
}
EXPECTED_HISTORICAL_MANIFEST = {
    "commit": "6c0451fffa8b875bf8a275473a3033bddb8a34da",
    "path": "conformance/prototypes/evidence/evidence-manifest.json",
    "schema": "statqed.sq0005-evidence.v1",
    "sha256": "0512a79a42cc6c6b70e5c139044841827b3ac3103968892fe6f135f02436a233",
    "subjects_sha256": "59aa64011c7afea1ed923a50479f151999cfcd16f7fa125114f6558c9a2b9105",
}
EXPECTED_HISTORICAL_SUCCESSOR_CONTRACTS = {
    "SQ-0006": {
        "commit": "6c0451fffa8b875bf8a275473a3033bddb8a34da",
        "path": "work/contracts/SQ-0006.yaml",
        "sha256": "1236fefeb2be7e70ea4b897f785049057cf659997eac4f00cbb72301e63acba1",
    },
    "SQ-0008": {
        "commit": "6c0451fffa8b875bf8a275473a3033bddb8a34da",
        "path": "work/contracts/SQ-0008.yaml",
        "sha256": "8ca1d8f0a50abc6d081cd2b3b73456a334f6ac43a2572576b6b452553ec8d471",
    },
}
EXPECTED_REVIEW_RECORD = "work/reviews/SQ-0005-evidence-lifecycle.md"
EXPECTED_BASELINE = {
    "commit": "8875d8f6fa8e3b45e706ea567d45448927a02efa",
    "rfc0006_sha256": "e834f805cc38fca2185433c72df4ac7db856c0ae20037fedcb57329a740b3429",
    "sq0008_contract_sha256": "8ca1d8f0a50abc6d081cd2b3b73456a334f6ac43a2572576b6b452553ec8d471",
}
EXPECTED_LIVE_DECISIONS = {
    "adr0004": "Accepted",
    "rfc0001": "Accepted",
    "rfc0006": "Draft",
    "rfc0006_owner": "SQ-0027",
}
EXPECTED_LIVE_SQ0005 = {
    "backlog_status": "DONE",
    "contract_status": "DONE",
    "ledger_bucket": "done",
}
EXPECTED_MAKEFILE_INTEGRATION = {
    "check_dependency": "check-sq0005-evidence",
    "command": "python3 scripts/serialization/check_evidence.py",
}
ALLOWED_SUCCESSOR_STATUSES = ("READY", "IN_PROGRESS", "IN_REVIEW", "DONE")
EXPECTED_SHARED_DOCUMENT_POLICIES = {
    "docs/quality/dashboard.md": {"projection": "sq0005_dashboard_v1"},
    "docs/spec/canonicalization.md": {
        "headings": [
            "Scope",
            "Exact byte rules",
            "Limits",
            "Generic data-free digest frame",
            "CDDL",
            "Reproduce the evidence",
            "Update and rollback",
            "Trust boundary and nonclaims",
        ],
        "projection": "markdown_preamble_and_sections_v1",
    },
}


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


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def semantic_projection_sha256(
    value: dict[str, Any], omitted_fields: list[str]
) -> str:
    if omitted_fields != ["status"]:
        raise EvidenceError(
            "SQ-0008 lifecycle projection must omit exactly the top-level status field"
        )
    if "status" not in value:
        raise EvidenceError("SQ-0008 contract lacks the projected status field")
    projection = {key: item for key, item in value.items() if key not in omitted_fields}
    return hashlib.sha256(canonical_json_bytes(projection)).hexdigest()


def markdown_sections_projection_sha256(value: bytes, headings: list[str]) -> str:
    try:
        text = value.decode("utf-8")
    except UnicodeDecodeError as error:
        raise EvidenceError(f"invalid UTF-8 shared document: {error}") from error
    lines = text.splitlines(keepends=True)
    heading_rows = [
        (index, line[3:].rstrip("\r\n"))
        for index, line in enumerate(lines)
        if line.startswith("## ")
    ]
    if len({name for _, name in heading_rows}) != len(heading_rows):
        raise EvidenceError("shared Markdown document has duplicate level-two headings")
    positions = {name: index for index, name in heading_rows}
    if any(name not in positions for name in headings):
        raise EvidenceError("shared Markdown document lacks a protected heading")
    first_heading = min(index for index, _ in heading_rows)
    all_indices = [index for index, _ in heading_rows]
    sections: dict[str, str] = {}
    for name in headings:
        start = positions[name]
        end = next((index for index in all_indices if index > start), len(lines))
        sections[name] = "".join(lines[start:end])
    projection = {"preamble": "".join(lines[:first_heading]), "sections": sections}
    return hashlib.sha256(canonical_json_bytes(projection)).hexdigest()


def sq0005_dashboard_projection_sha256(value: bytes) -> str:
    try:
        text = value.decode("utf-8")
    except UnicodeDecodeError as error:
        raise EvidenceError(f"invalid UTF-8 quality dashboard: {error}") from error
    if any(token in text for token in ("<", ">", "```", "~~~", "~~")):
        raise EvidenceError("quality dashboard uses prohibited wrapping markup")
    rows = [
        line
        for line in text.splitlines(keepends=True)
        if line.startswith("| Deterministic encoding profile |")
    ]
    if len(rows) != 1:
        raise EvidenceError("quality dashboard lacks one encoding-profile row")
    begin = "SQ-0005 adds one Experimental deterministic"
    end = "does not define logical-data identity."
    if text.count(begin) != 1 or text.count(end) != 1:
        raise EvidenceError("quality dashboard lacks one SQ-0005 evidence statement")
    evidence_start = text.index(begin)
    lines = text.splitlines(keepends=True)
    offsets: list[int] = []
    offset = 0
    for line in lines:
        offsets.append(offset)
        offset += len(line)
    containing = next(
        index
        for index, line_offset in enumerate(offsets)
        if line_offset <= evidence_start < line_offset + len(lines[index])
    )
    paragraph_start = containing
    while paragraph_start > 0 and lines[paragraph_start - 1].strip():
        paragraph_start -= 1
    paragraph_end = containing + 1
    while paragraph_end < len(lines) and lines[paragraph_end].strip():
        paragraph_end += 1
    paragraph = "".join(lines[paragraph_start:paragraph_end])
    if begin not in paragraph or end not in paragraph:
        raise EvidenceError("SQ-0005 evidence statement crosses a paragraph boundary")
    nonblank = [line for line in text.splitlines(keepends=True) if line.strip()]
    if len(nonblank) < 2:
        raise EvidenceError("quality dashboard preamble is incomplete")
    projection = {
        "heading": nonblank[0],
        "status": nonblank[1],
        "encoding_profile_row": rows[0],
        "sq0005_evidence_paragraph": paragraph,
    }
    return hashlib.sha256(canonical_json_bytes(projection)).hexdigest()


def shared_document_projection_sha256(
    value: bytes, policy: dict[str, Any]
) -> str:
    policy_without_hash = {
        key: item for key, item in policy.items() if key != "projection_sha256"
    }
    projection = policy_without_hash.get("projection")
    if projection == "markdown_preamble_and_sections_v1":
        headings = policy_without_hash.get("headings")
        if not isinstance(headings, list) or not all(
            isinstance(item, str) for item in headings
        ):
            raise EvidenceError("invalid shared Markdown heading policy")
        return markdown_sections_projection_sha256(value, headings)
    if projection == "sq0005_dashboard_v1" and sorted(policy_without_hash) == [
        "projection"
    ]:
        return sq0005_dashboard_projection_sha256(value)
    raise EvidenceError(f"unsupported shared-document projection: {projection}")


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


def checked_subject_list(manifest: dict[str, Any], key: str) -> list[dict[str, Any]]:
    subjects = manifest.get(key)
    if not isinstance(subjects, list) or not subjects:
        raise EvidenceError(f"manifest {key} must be a nonempty list")
    paths = [item.get("path") for item in subjects if isinstance(item, dict)]
    if len(paths) != len(subjects) or paths != sorted(paths) or len(set(paths)) != len(paths):
        raise EvidenceError(f"manifest {key} paths must be unique and sorted")
    for item in subjects:
        if not re.fullmatch(r"[0-9a-f]{64}", str(item.get("sha256", ""))):
            raise EvidenceError(f"invalid subject SHA-256: {item.get('path')}")
        if not isinstance(item.get("role"), str) or not item["role"]:
            raise EvidenceError(f"missing subject role: {item.get('path')}")
    return subjects


def verify_historical_subjects(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    subjects = checked_subject_list(manifest, "historical_subjects")
    observed = hashlib.sha256(canonical_json_bytes(subjects)).hexdigest()
    if observed != EXPECTED_HISTORICAL_MANIFEST["subjects_sha256"]:
        raise EvidenceError("historical SQ-0005 subject map changed")
    if len(subjects) != 158:
        raise EvidenceError("historical SQ-0005 subject count changed")
    return subjects


def verify_live_subjects(root: Path, manifest: dict[str, Any]) -> dict[str, str]:
    subjects = checked_subject_list(manifest, "live_subjects")
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
            and not any(
                part in {"__pycache__", ".pytest_cache", "target", ".lake"}
                for part in path.relative_to(root).parts
            )
            and path.suffix not in {".pyc", ".pyo"}
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
    if manifest.get("review_record") != EXPECTED_REVIEW_RECORD:
        raise EvidenceError("active SQ-0005 lifecycle review path changed")
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


def verify_historical_completion(root: Path, manifest: dict[str, Any]) -> None:
    if manifest.get("historical_completion_state") != EXPECTED_HISTORICAL_COMPLETION_STATE:
        raise EvidenceError("historical SQ-0005 completion snapshot changed")
    if manifest.get("historical_review") != EXPECTED_HISTORICAL_REVIEW:
        raise EvidenceError("historical SQ-0005 review binding changed")
    review = require_file(root, EXPECTED_HISTORICAL_REVIEW["path"])
    if sha256(review) != EXPECTED_HISTORICAL_REVIEW["sha256"]:
        raise EvidenceError("historical SQ-0005 review changed")
    if manifest.get("historical_manifest") != EXPECTED_HISTORICAL_MANIFEST:
        raise EvidenceError("historical SQ-0005 manifest binding changed")
    if (
        manifest.get("historical_successor_contracts")
        != EXPECTED_HISTORICAL_SUCCESSOR_CONTRACTS
    ):
        raise EvidenceError("historical successor contract bindings changed")
    if manifest.get("baseline") != EXPECTED_BASELINE:
        raise EvidenceError("historical SQ-0005 baseline changed")


def ledger_membership(status: dict[str, Any], task_id: str, task_status: str) -> None:
    buckets = {
        "done": status.get("done", []),
        "in_progress": status.get("in_progress", []),
        "ready": status.get("ready", []),
    }
    for name, values in buckets.items():
        if not isinstance(values, list) or len(values) != len(set(values)):
            raise EvidenceError(f"work/status {name} bucket is not a unique list")
    expected_bucket = {
        "DONE": "done",
        "IN_PROGRESS": "in_progress",
        "IN_REVIEW": "in_progress",
        "READY": "ready",
    }[task_status]
    present = [name for name, values in buckets.items() if task_id in values]
    if present != [expected_bucket]:
        raise EvidenceError(
            f"{task_id} live ledger membership disagrees with {task_status}: {present}"
        )


def verify_live_status_and_scope(root: Path, manifest: dict[str, Any]) -> None:
    policy = manifest.get("live_invariants")
    if not isinstance(policy, dict):
        raise EvidenceError("missing SQ-0005 live invariant policy")
    if policy.get("decisions") != EXPECTED_LIVE_DECISIONS:
        raise EvidenceError("SQ-0005 live decision policy changed")
    if policy.get("sq0005") != EXPECTED_LIVE_SQ0005:
        raise EvidenceError("SQ-0005 live completion policy changed")
    if policy.get("makefile_integration") != EXPECTED_MAKEFILE_INTEGRATION:
        raise EvidenceError("SQ-0005 Makefile integration policy changed")
    successor_policy = policy.get("successor_lifecycle")
    if not isinstance(successor_policy, dict) or sorted(successor_policy) != [
        "SQ-0006",
        "SQ-0008",
    ]:
        raise EvidenceError("SQ-0005 successor lifecycle policy changed")
    for task_id in sorted(successor_policy):
        if successor_policy[task_id] != {
            "allowed_statuses": list(ALLOWED_SUCCESSOR_STATUSES)
        }:
            raise EvidenceError(f"{task_id} allowed lifecycle policy changed")

    backlog = load_json(root / "work/backlog.yaml")
    status = load_json(root / "work/status.yaml")
    contract5 = load_json(root / "work/contracts/SQ-0005.yaml")
    contract6 = load_json(root / "work/contracts/SQ-0006.yaml")
    contract8 = load_json(root / "work/contracts/SQ-0008.yaml")
    backlog5 = task(backlog["tasks"], "SQ-0005")
    backlog6 = task(backlog["tasks"], "SQ-0006")
    backlog8 = task(backlog["tasks"], "SQ-0008")
    if contract5.get("status") != "DONE" or backlog5.get("status") != "DONE":
        raise EvidenceError("SQ-0005 live status regressed from DONE")
    ledger_membership(status, "SQ-0005", "DONE")

    for task_id, contract, backlog_task in (
        ("SQ-0006", contract6, backlog6),
        ("SQ-0008", contract8, backlog8),
    ):
        contract_status = contract.get("status")
        backlog_status = backlog_task.get("status")
        if contract_status != backlog_status:
            raise EvidenceError(f"{task_id} contract/backlog status disagreement")
        if contract_status not in ALLOWED_SUCCESSOR_STATUSES:
            raise EvidenceError(f"{task_id} has illegal lifecycle status: {contract_status}")
        ledger_membership(status, task_id, contract_status)

    if header_status(root / "rfcs/0001-deterministic-encoding.md") != "Accepted":
        raise EvidenceError("RFC-0001 live status is not Accepted")
    if header_status(root / "docs/adr/0004-deterministic-cbor-cddl.md") != "Accepted":
        raise EvidenceError("ADR-0004 live status is not Accepted")

    makefile = (root / "Makefile").read_text(encoding="utf-8")
    make_lines = makefile.splitlines()
    rules: list[tuple[int, list[str], str, list[str]]] = []
    for index, line in enumerate(make_lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or line.startswith("\t"):
            continue
        if line.rstrip().endswith("\\") or "$" in line:
            raise EvidenceError("SQ-0005 Makefile dynamic syntax is prohibited")
        if re.match(
            r"^\s*(?:-?include|sinclude|define|endef|eval|ifeq|ifneq|ifdef|ifndef|else|endif)(?:\s|$)",
            line,
        ) or re.match(r"^\s*(?:override\s+)?SHELL\s*[:?+]?=", line):
            raise EvidenceError("SQ-0005 Makefile indirection is prohibited")
        match = re.match(
            r"^\s*(?P<targets>[^:#]*?)\s*(?P<separator>::|&:|:)(?=\s|$)(?P<rest>.*)$",
            line,
        )
        if match is None:
            raise EvidenceError("SQ-0005 Makefile uses unsupported structural syntax")
        targets = match.group("targets").split()
        if not targets:
            raise EvidenceError("SQ-0005 Makefile rule lacks a target")
        special = [target for target in targets if target.startswith(".")]
        if special and targets != [".PHONY"]:
            raise EvidenceError("SQ-0005 Makefile special target is prohibited")
        rules.append(
            (
                index,
                targets,
                match.group("separator"),
                match.group("rest").strip().split(),
            )
        )

    check_rules = [rule for rule in rules if "check" in rule[1]]
    if (
        len(check_rules) != 1
        or check_rules[0][1] != ["check"]
        or check_rules[0][2] != ":"
        or check_rules[0][3].count("check-sq0005-evidence") != 1
    ):
        raise EvidenceError("make check no longer depends exactly on SQ-0005 evidence")

    protected_rules = [
        rule for rule in rules if "check-sq0005-evidence" in rule[1]
    ]
    if len(protected_rules) != 1:
        raise EvidenceError("SQ-0005 evidence Makefile target is not unique")
    target_index, targets, separator, prerequisites = protected_rules[0]
    if (
        targets != ["check-sq0005-evidence"]
        or separator != ":"
        or prerequisites
        or make_lines[target_index] != "check-sq0005-evidence:"
    ):
        raise EvidenceError("SQ-0005 evidence Makefile target changed")
    phony_rules = [rule for rule in rules if rule[1] == [".PHONY"]]
    if (
        len(phony_rules) != 1
        or phony_rules[0][2] != ":"
        or phony_rules[0][3].count("check-sq0005-evidence") != 1
    ):
        raise EvidenceError("SQ-0005 evidence target is not uniquely phony")
    recipes: list[str] = []
    for line in make_lines[target_index + 1 :]:
        if line.startswith("\t"):
            recipes.append(line)
            continue
        if not line.strip() or line.lstrip().startswith("#"):
            if recipes:
                break
            continue
        break
    if recipes != ["\tpython3 scripts/serialization/check_evidence.py"]:
        raise EvidenceError("SQ-0005 evidence Makefile recipe changed")

    shared_documents = policy.get("shared_document_integrity")
    if not isinstance(shared_documents, dict) or sorted(shared_documents) != sorted(
        EXPECTED_SHARED_DOCUMENT_POLICIES
    ):
        raise EvidenceError("shared SQ-0005 document policy changed")
    for path, expected_policy in sorted(EXPECTED_SHARED_DOCUMENT_POLICIES.items()):
        observed_policy = shared_documents[path]
        if not isinstance(observed_policy, dict):
            raise EvidenceError(f"missing shared document policy: {path}")
        policy_without_hash = {
            key: item
            for key, item in observed_policy.items()
            if key != "projection_sha256"
        }
        if policy_without_hash != expected_policy:
            raise EvidenceError(f"shared document projection policy changed: {path}")
        observed_hash = shared_document_projection_sha256(
            require_file(root, path).read_bytes(), observed_policy
        )
        if observed_hash != observed_policy.get("projection_sha256"):
            raise EvidenceError(f"shared SQ-0005 document projection changed: {path}")

    integrity = policy.get("successor_contract_integrity")
    if not isinstance(integrity, dict) or sorted(integrity) != ["SQ-0008"]:
        raise EvidenceError("successor contract integrity policy changed")
    sq0008_integrity = integrity["SQ-0008"]
    if not isinstance(sq0008_integrity, dict):
        raise EvidenceError("missing SQ-0008 contract integrity projection")
    omitted_fields = sq0008_integrity.get("omitted_fields")
    observed_projection = semantic_projection_sha256(contract8, omitted_fields)
    if observed_projection != sq0008_integrity.get("projection_sha256"):
        raise EvidenceError("SQ-0008 non-lifecycle contract projection changed")

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
def verify(root: Path, manifest_value: str) -> dict[str, Any]:
    manifest_path = require_file(root, manifest_value)
    manifest = load_json(manifest_path)
    if manifest.get("schema") != "statqed.sq0005-evidence.v2":
        raise EvidenceError("unsupported evidence manifest schema")
    verify_historical_completion(root, manifest)
    historical_subjects = verify_historical_subjects(manifest)
    live_subjects = verify_live_subjects(root, manifest)
    verify_coverage(root, manifest, set(live_subjects))
    verify_fixture_coverage(root, manifest)
    verify_failures(root, manifest)
    verify_lineage(root, manifest)
    verify_live_status_and_scope(root, manifest)
    verify_rfc6_and_protected(root, manifest)
    verify_review(root, manifest_value, manifest)
    return {
        "manifest_sha256": sha256(manifest_path),
        "negative_fixture_count": len(manifest["negative_fixture_ids"]),
        "protected_file_count": len(manifest["protected_files"]),
        "status": "verified",
        "historical_subject_count": len(historical_subjects),
        "live_subject_count": len(live_subjects),
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
            f"{result['historical_subject_count']} historical subjects, "
            f"{result['live_subject_count']} live subjects, "
            f"{result['negative_fixture_count']} negative fixtures"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
