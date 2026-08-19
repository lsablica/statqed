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


def git(root: Path, arguments: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def commit_exists(root: Path, commit: str) -> bool:
    return git(root, ["cat-file", "-e", f"{commit}^{{commit}}"]).returncode == 0


def is_ancestor(root: Path, ancestor: str, descendant: str = "HEAD") -> bool:
    return git(root, ["merge-base", "--is-ancestor", ancestor, descendant]).returncode == 0


def commit_parents(root: Path, commit: str) -> list[str] | None:
    completed = git(root, ["show", "-s", "--format=%P", commit])
    return completed.stdout.strip().split() if completed.returncode == 0 else None


def ancestry_errors(root: Path, spec: dict) -> list[str]:
    """Verify frozen launch provenance and reviewed normal predecessor merges."""
    if not (root / ".git").exists():
        return []
    errors: list[str] = []
    launch = spec["historical_launch_base"]
    historical = spec["historical_task_commits"]
    chain = spec["verified_predecessor_chain"]
    required_phases = [
        "phase_m_compositional_evidence",
        "phase_f_fixture_neutrality",
        "phase_t_branch_relative_live_report_fixtures",
    ]
    if [entry.get("phase") for entry in chain] != required_phases:
        errors.append("evidence.predecessor_chain_unverified")
        return errors
    required = [launch, *historical.values()]
    for entry in chain:
        required.extend((entry["predecessor_tip"], entry["task_integration_merge"]))
    if any(not commit_exists(root, commit) for commit in required):
        errors.append("evidence.predecessor_commit_missing")
        return errors
    if spec["verified_predecessor_tip"] != chain[-1]["predecessor_tip"]:
        errors.append("evidence.predecessor_tip_unverified")
    if not is_ancestor(root, launch, historical["prototype"]):
        errors.append("evidence.launch_base_replaced")
    if not is_ancestor(root, historical["prototype"], historical["blocked_head"]):
        errors.append("evidence.historical_task_history_rewritten")
    for index, entry in enumerate(chain):
        expected_parents = [entry["first_parent"], entry["second_parent"]]
        if commit_parents(root, entry["task_integration_merge"]) != expected_parents:
            errors.append(f"evidence.predecessor_merge_not_normal:{entry['phase']}")
        if entry["second_parent"] != entry["predecessor_tip"]:
            errors.append(f"evidence.predecessor_chain_unverified:{entry['phase']}")
        if not is_ancestor(root, entry["predecessor_tip"]):
            errors.append(f"evidence.predecessor_tip_not_in_ancestry:{entry['phase']}")
        if not is_ancestor(root, entry["task_integration_merge"]):
            errors.append(f"evidence.predecessor_tip_not_in_ancestry:{entry['phase']}")
        if index and entry["first_parent"] != chain[index - 1]["task_integration_merge"]:
            errors.append(f"evidence.predecessor_chain_truncated:{entry['phase']}")
    if not is_ancestor(root, historical["blocked_head"]):
        errors.append("evidence.historical_task_history_rewritten")
    return sorted(set(errors))


def active_scope_errors(root: Path, verified_tip: str, launch_base: str, allowed_patterns: list[str]) -> list[str]:
    if not (root / ".git").exists():
        return []
    completed = git(root, ["diff", "--name-only", verified_tip, "--"])
    if completed.returncode != 0:
        return ["evidence.scope_diff_failed"]
    untracked = git(root, ["ls-files", "--others", "--exclude-standard"])
    if untracked.returncode != 0:
        return ["evidence.scope_untracked_failed"]
    paths = sorted(set(completed.stdout.splitlines() + untracked.stdout.splitlines()))
    errors = [f"evidence.path_outside_contract:{path}" for path in paths if not path_allowed(path, allowed_patterns)]
    predecessor = git(root, ["diff", "--name-only", launch_base, verified_tip, "--"])
    if predecessor.returncode != 0:
        errors.append("evidence.predecessor_scope_diff_failed")
    else:
        predecessor_only = {
            path for path in predecessor.stdout.splitlines()
            if not path_allowed(path, allowed_patterns)
        }
        errors.extend(
            f"evidence.predecessor_file_modified_by_task:{path}"
            for path in paths if path in predecessor_only
        )
    return errors


def rust_build_evidence_errors(root: Path) -> list[str]:
    """Check retained Rust claims against the exact bound source and test set."""

    relative = Path("backend/crates/statqed-registry/evidence/build-evidence.json")
    try:
        evidence = load_json(root / relative)
        if evidence.get("schema") != "statqed.registry-rust-build-evidence.v0":
            return ["evidence.rust_build_schema_unsupported"]
        subjects = evidence.get("subjects")
        if not isinstance(subjects, dict):
            return ["evidence.rust_build_subjects_malformed"]
        expected_subjects = {
            "Cargo.toml", "Cargo.lock", "rust-toolchain.toml", "src/lib.rs", "tests/resolver.rs"
        }
        if set(subjects) != expected_subjects:
            return ["evidence.rust_build_subjects_malformed"]
        errors = []
        crate = relative.parent.parent
        for path, expected_hash in sorted(subjects.items()):
            target = root / crate / path
            if not target.is_file() or not isinstance(expected_hash, str) or sha(target) != expected_hash:
                errors.append(f"evidence.rust_build_subject_drift:{path}")
        test_source = (root / crate / "tests/resolver.rs").read_text(encoding="utf-8")
        test_count = len(re.findall(r"^\s*#\[test\]\s*$", test_source, re.MULTILINE))
        expected_result = f"pass: {test_count} integration tests and doc tests"
        development = evidence.get("development", {})
        expected_development = {
            "rustc": "rustc 1.97.1 (8bab26f4f 2026-07-14)",
            "rustc_commit": "8bab26f4f68e0e26f0bb7960be334d5b520ea452",
            "cargo": "cargo 1.97.1 (c980f4866 2026-06-30)",
            "commands": [
                "cargo +1.97.1 fmt --check",
                "cargo +1.97.1 clippy --all-targets --all-features --locked -- -D warnings",
                "cargo +1.97.1 test --all-features --locked",
            ],
        }
        if any(development.get(key) != value for key, value in expected_development.items()):
            errors.append("evidence.rust_build_development_toolchain_drift")
        if development.get("result") != expected_result:
            errors.append("evidence.rust_build_development_result_drift")
        offline = evidence.get("offline_floor", {})
        expected_offline = {
            "rustc": "rustc 1.85.1 (4eb161250 2025-03-15)",
            "rustc_commit": "4eb161250e340c8f48f66e2b929ef4a5bed7c181",
            "cargo": "cargo 1.85.1 (d73d2caf9 2024-12-31)",
            "command": "cargo +1.85.1 test --all-features --locked --offline",
        }
        if any(offline.get(key) != value for key, value in expected_offline.items()):
            errors.append("evidence.rust_build_offline_toolchain_drift")
        if offline.get("result") != expected_result:
            errors.append("evidence.rust_build_offline_result_drift")
        return errors
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return ["evidence.rust_build_record_malformed"]


def verify(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    try:
        spec = load_json(root / build_evidence_manifest.SPEC_PATH)
        errors.extend(ancestry_errors(root, spec))
        errors.extend(rust_build_evidence_errors(root))
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
            errors.extend(active_scope_errors(
                root,
                spec["verified_predecessor_tip"],
                spec["historical_launch_base"],
                contract["allowed_paths"],
            ))

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
            "theorem-registry/evidence/project-axioms.json",
            "theorem-registry/evidence/all-module-fresh-check.json",
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
