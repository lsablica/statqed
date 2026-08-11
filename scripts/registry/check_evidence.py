#!/usr/bin/env python3
"""Permanent fail-closed verification for SQ-0007 evidence and live invariants."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import build_evidence_manifest  # noqa: E402

RFC_SCOPE_BEGIN = "<!-- SQ-0007-NORMATIVE-SCOPE-BEGIN -->"
RFC_SCOPE_END = "<!-- SQ-0007-NORMATIVE-SCOPE-END -->"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decision_status(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^- Status: (Draft|Accepted|Proposed)$", text, re.MULTILINE)
    if not match:
        raise ValueError(f"missing decision status: {path.name}")
    return match.group(1)


def marked_scope(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if text.count(RFC_SCOPE_BEGIN) != 1 or text.count(RFC_SCOPE_END) != 1:
        raise ValueError(f"missing unique SQ-0007 normative scope: {path.name}")
    return text.split(RFC_SCOPE_BEGIN, 1)[1].split(RFC_SCOPE_END, 1)[0]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def task_status(backlog: dict, task: str) -> str:
    for item in backlog["tasks"]:
        if item["id"] == task:
            return item["status"]
    raise ValueError(f"missing backlog task {task}")


def path_allowed(path: str, allowed_patterns: list[str]) -> bool:
    return any(
        fnmatch.fnmatchcase(path, pattern)
        or (pattern.endswith("/**") and path == pattern[:-3])
        for pattern in allowed_patterns
    )


def active_scope_errors(root: Path, launch_base: str, allowed_patterns: list[str]) -> list[str]:
    if not (root / ".git").exists():
        return []
    completed = subprocess.run(
        ["git", "diff", "--name-only", launch_base, "--"],
        cwd=root,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        return ["evidence.scope_diff_failed"]
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=root,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if untracked.returncode != 0:
        return ["evidence.scope_untracked_failed"]
    paths = sorted(set(completed.stdout.splitlines() + untracked.stdout.splitlines()))
    return [f"evidence.path_outside_contract:{path}" for path in paths if not path_allowed(path, allowed_patterns)]


def verify(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    try:
        spec = load_json(root / build_evidence_manifest.SPEC_PATH)
        expected = build_evidence_manifest.encoded(build_evidence_manifest.build(root))
        manifest_path = root / build_evidence_manifest.MANIFEST_PATH
        if not manifest_path.is_file() or manifest_path.read_bytes() != expected:
            errors.append("evidence.manifest_drift")
        for relative, expected_hash in (
            ("rfcs/0006-canonical-logical-data-digest.md", spec["predecessor_bindings"]["rfc0006_sha256"]),
            ("conformance/schema-v0/evidence/evidence-manifest.json", spec["predecessor_bindings"]["sq0006_manifest_sha256"]),
            ("conformance/prototypes/evidence/evidence-manifest.json", spec["predecessor_bindings"]["sq0005_manifest_sha256"]),
        ):
            if sha(root / relative) != expected_hash:
                errors.append(f"evidence.predecessor_drift:{relative}")

        contract = load_json(root / "work/contracts/SQ-0007.yaml")
        backlog = load_json(root / "work/backlog.yaml")
        status = load_json(root / "work/status.yaml")
        current = contract["status"]
        if current not in spec["live_invariants"]["allowed_statuses"]:
            errors.append("evidence.task_status_illegal")
        if task_status(backlog, "SQ-0007") != current:
            errors.append("evidence.task_contract_backlog_disagreement")
        represented = (
            "DONE" if "SQ-0007" in status["done"] else
            current if current in {"IN_PROGRESS", "IN_REVIEW"} and "SQ-0007" in status["in_progress"] else
            "BLOCKED" if current == "BLOCKED" and "SQ-0007" not in status["ready"] else
            "READY" if "SQ-0007" in status["ready"] else "MISSING"
        )
        if represented != current:
            errors.append("evidence.task_status_ledger_disagreement")
        if current != "DONE":
            errors.extend(active_scope_errors(root, spec["launch_base"], contract["allowed_paths"]))

        rfc = root / "rfcs/0005-theorem-identity-and-compatibility.md"
        adr = root / "docs/adr/0007-versioned-theorem-registry.md"
        rfc_status = decision_status(rfc)
        adr_status = decision_status(adr)
        if (rfc_status, adr_status) not in {("Draft", "Proposed"), ("Accepted", "Accepted")}:
            errors.append("evidence.decision_status_disagreement")
        if current == "DONE" and (rfc_status, adr_status) != ("Accepted", "Accepted"):
            errors.append("evidence.done_without_accepted_decisions")
        if marked_scope(rfc) != marked_scope(adr):
            errors.append("evidence.normative_scope_drift")

        rfc6 = (root / "rfcs/0006-canonical-logical-data-digest.md").read_text(encoding="utf-8")
        if "- Status: Draft" not in rfc6 or "- Task: SQ-0027" not in rfc6:
            errors.append("evidence.rfc0006_governance_drift")

        required = (
            "theorem-registry/evidence/axioms.json",
            "theorem-registry/evidence/independent-observation.json",
            "theorem-registry/records/test-only-true.v0.json",
            "theorem-registry/policy/authorization-v0.json",
            "conformance/registry/results/results.json",
            "conformance/registry/results/mutations.json",
            "backend/crates/statqed-registry/Cargo.lock",
            "source-audits/registry/primary-sources.yaml",
        )
        for relative in required:
            if not (root / relative).is_file():
                errors.append(f"evidence.required_missing:{relative}")
        if (root / "conformance/registry/results/results.json").is_file():
            results = load_json(root / "conformance/registry/results/results.json")
            if results.get("failed") != 0 or results.get("total", 0) < 50:
                errors.append("evidence.conformance_incomplete")
        if (root / "conformance/registry/results/mutations.json").is_file():
            mutations = load_json(root / "conformance/registry/results/mutations.json")
            if mutations.get("detected", 0) < 10 or any(item.get("status") != "pass" for item in mutations.get("mutations", [])):
                errors.append("evidence.mutation_incomplete")
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"evidence.operational_failure:{type(error).__name__}")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors = verify(args.root.resolve())
    if errors:
        print("SQ-0007 evidence verification failed:")
        for error in errors:
            print(f"  {error}")
        return 1
    manifest = load_json(args.root / build_evidence_manifest.MANIFEST_PATH)
    print(f"SQ-0007 evidence verified: {manifest['subject_count']} subjects; scientific digest {manifest['scientific_subject_digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
