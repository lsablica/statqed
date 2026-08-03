#!/usr/bin/env python3
"""Validate the architecture-first StatQED repository scaffold."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_TASK_STATUS = {"READY", "IN_PROGRESS", "BLOCKED", "IN_REVIEW", "DONE", "SUPERSEDED"}
ALLOWED_DECISION_STATUS = {"Draft", "Accepted"}
REQUIRED_FILES = [
    "README.md", "CHARTER.md", "ARCHITECTURE.md", "ROADMAP.md", "START_HERE.md",
    "AGENTS.md", "GOVERNANCE.md", "SECURITY.md", "CONTRIBUTING.md", "CITATION.cff",
    "docs/design/core-beliefs.md", "docs/design/trust-model.md",
    "docs/spec/ir.md", "docs/spec/assurance-graph.md", "docs/spec/artifact.md",
    "docs/exec-plans/active/0001-foundation-bootstrap.md",
    "docs/exec-plans/active/0002-randomization-vertical-slice.md",
    "work/backlog.yaml", "work/status.yaml",
    "agents/protocols/task-contract.md", "agents/protocols/merge-gates.md",
    ".github/workflows/repository-guardrails.yml",
]
LIVING_SECTIONS = ["## Progress", "## Surprises & Discoveries", "## Decision Log", "## Outcomes & Retrospective"]


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"{path.relative_to(ROOT)} is not valid JSON-compatible YAML: {exc}")


def document_status(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"(?m)^- Status:\s*([A-Za-z_]+)\s*$", text)
    if not match:
        fail(f"{path.relative_to(ROOT)} has no machine-readable '- Status:' line")
    status = match.group(1)
    if status not in ALLOWED_DECISION_STATUS:
        fail(f"{path.relative_to(ROOT)} has invalid decision status {status!r}")
    return status


def decision_owner_state_valid(decision_status: str, owner_status: str) -> bool:
    return (
        decision_status in ALLOWED_DECISION_STATUS
        and (
            decision_status == "Accepted"
            or owner_status not in {"DONE", "SUPERSEDED"}
        )
    )


def path_allowed(path_value: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        if pattern == path_value:
            return True
        if pattern.endswith("/**") and path_value.startswith(pattern[:-3] + "/"):
            return True
    return False


def prerequisites_satisfied(
    prerequisites: list[dict], decision_statuses: dict[str, str]
) -> bool:
    return all(
        decision_statuses.get(prerequisite.get("id")) == prerequisite.get("status")
        for prerequisite in prerequisites
    )


def check_readiness_regression_fixtures() -> None:
    accepted_requirement = [{"id": "RFC-FIXTURE", "status": "Accepted"}]
    if prerequisites_satisfied(accepted_requirement, {"RFC-FIXTURE": "Draft"}):
        fail("readiness fixture promoted a task whose required RFC remains Draft")
    if not prerequisites_satisfied(accepted_requirement, {"RFC-FIXTURE": "Accepted"}):
        fail("readiness fixture blocked a task whose required RFC is Accepted")

    active_owner_states = {"BLOCKED", "READY", "IN_PROGRESS", "IN_REVIEW"}
    completed_owner_states = {"DONE", "SUPERSEDED"}
    for decision_status in ALLOWED_DECISION_STATUS:
        for owner_status in active_owner_states | completed_owner_states:
            expected = (
                decision_status == "Accepted"
                or owner_status in active_owner_states
            )
            if decision_owner_state_valid(decision_status, owner_status) != expected:
                fail(
                    "decision lifecycle fixture failed for "
                    f"{decision_status}/{owner_status}"
                )
    for owner_status in {"IN_PROGRESS", "DONE"}:
        if decision_owner_state_valid("Accepetd", owner_status):
            fail(
                "decision lifecycle fixture accepted an invalid/typo status "
                f"for owner {owner_status}"
            )


def check_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ROOT / name).is_file()]
    if missing:
        fail(f"missing required files: {', '.join(missing)}")

    forbidden = [
        ROOT / "bootstrap_scaffold.py",
        ROOT / "bootstrap_payload",
        ROOT / ".github/workflows/materialize-scaffold.yml",
    ]
    present = [str(path.relative_to(ROOT)) for path in forbidden if path.exists()]
    if present:
        fail(f"temporary bootstrap transport remains: {', '.join(present)}")


def check_backlog() -> tuple[list[dict], set[str], set[str], set[str]]:
    payload = load_json(ROOT / "work/backlog.yaml")
    tasks = payload.get("tasks")
    if not isinstance(tasks, list) or len(tasks) != 60:
        fail(f"expected exactly 60 backlog tasks, found {len(tasks) if isinstance(tasks, list) else 'non-list'}")

    ids = [task.get("id") for task in tasks]
    expected = [f"SQ-{number:04d}" for number in range(1, 61)]
    if ids != expected:
        fail("task IDs must be unique and sequential SQ-0001 through SQ-0060")

    by_id = {task["id"]: task for task in tasks}
    decision_entries = payload.get("decision_register", [])
    if not isinstance(decision_entries, list):
        fail("decision_register must be a list")
    decisions: dict[str, dict] = {}
    decision_paths: set[str] = set()
    for entry in decision_entries:
        if not isinstance(entry, dict):
            fail("decision_register entries must be objects")
        decision_id = entry.get("id")
        path_value = entry.get("path")
        owner = entry.get("owner")
        if not isinstance(decision_id, str) or decision_id in decisions:
            fail(f"invalid or duplicate decision id {decision_id!r}")
        if not isinstance(path_value, str) or not (ROOT / path_value).is_file():
            fail(f"{decision_id} references missing decision path {path_value!r}")
        if path_value in decision_paths:
            fail(f"decision path {path_value!r} is registered more than once")
        expected_prefix = decision_id.removeprefix("RFC-")
        if not path_value.startswith(f"rfcs/{expected_prefix}-"):
            fail(f"{decision_id} does not match decision path {path_value!r}")
        if owner not in by_id:
            fail(f"{decision_id} references unknown owner task {owner!r}")
        contract_value = by_id[owner].get("contract")
        if not isinstance(contract_value, str) or not (ROOT / contract_value).is_file():
            fail(f"{decision_id} owner {owner} has no detailed contract")
        owner_contract = load_json(ROOT / contract_value)
        allowed_paths = owner_contract.get("allowed_paths", [])
        if not isinstance(allowed_paths, list) or not path_allowed(path_value, allowed_paths):
            fail(f"{decision_id} path {path_value!r} is not writable by owner {owner}")
        decisions[decision_id] = entry
        decision_paths.add(path_value)

    rfc_paths = {
        str(path.relative_to(ROOT))
        for path in (ROOT / "rfcs").glob("[0-9][0-9][0-9][0-9]-*.md")
    }
    if decision_paths != rfc_paths:
        missing = sorted(rfc_paths - decision_paths)
        stale = sorted(decision_paths - rfc_paths)
        fail(f"decision_register RFC coverage mismatch; missing={missing}, stale={stale}")

    for task in tasks:
        if task.get("status") not in ALLOWED_TASK_STATUS:
            fail(f"{task['id']} has invalid status {task.get('status')!r}")
        deps = task.get("dependencies")
        if not isinstance(deps, list) or any(dep not in by_id for dep in deps):
            fail(f"{task['id']} has invalid dependencies {deps!r}")
        if task["id"] in deps:
            fail(f"{task['id']} depends on itself")
        plan = task.get("plan")
        if not isinstance(plan, str) or not (ROOT / plan).is_file():
            fail(f"{task['id']} references missing plan {plan!r}")
        prerequisites = task.get("decision_prerequisites", [])
        if not isinstance(prerequisites, list):
            fail(f"{task['id']} decision_prerequisites must be a list")
        for prerequisite in prerequisites:
            if not isinstance(prerequisite, dict):
                fail(f"{task['id']} has malformed decision prerequisite")
            decision_id = prerequisite.get("id")
            required_status = prerequisite.get("status")
            if decision_id not in decisions or required_status != "Accepted":
                fail(f"{task['id']} has invalid decision prerequisite {prerequisite!r}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visiting:
            fail(f"dependency cycle detected at {task_id}")
        if task_id in visited:
            return
        visiting.add(task_id)
        for dep in by_id[task_id]["dependencies"]:
            visit(dep)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in ids:
        visit(task_id)

    done = {task["id"] for task in tasks if task["status"] == "DONE"}

    decision_statuses = {
        decision_id: document_status(ROOT / entry["path"])
        for decision_id, entry in decisions.items()
    }
    for decision_id, entry in decisions.items():
        decision_state = decision_statuses[decision_id]
        owner_state = by_id[entry["owner"]]["status"]
        if not decision_owner_state_valid(decision_state, owner_state):
            fail(
                f"non-Accepted {decision_id} has completed owner {entry['owner']}; "
                "owner handoff must be atomic"
            )

    def decisions_ready(task: dict) -> bool:
        return prerequisites_satisfied(
            task.get("decision_prerequisites", []), decision_statuses
        )

    computed_eligible = {
        task["id"]
        for task in tasks
        if task["status"] not in {"DONE", "SUPERSEDED"}
        and all(dep in done for dep in task["dependencies"])
        and decisions_ready(task)
    }
    declared_ready = {task["id"] for task in tasks if task["status"] == "READY"}
    declared_active = {
        task["id"] for task in tasks if task["status"] in {"IN_PROGRESS", "IN_REVIEW"}
    }
    if computed_eligible != declared_ready | declared_active:
        fail(
            f"declared READY/active tasks {sorted(declared_ready | declared_active)} "
            f"do not match dependency/decision-eligible tasks {sorted(computed_eligible)}"
        )
    return tasks, done, declared_ready, declared_active


def check_contracts(tasks: list[dict]) -> int:
    expected_ids = {task["id"] for task in tasks if task.get("contract") is not None}
    files = sorted((ROOT / "work/contracts").glob("SQ-*.yaml"))
    found_ids: set[str] = set()
    for path in files:
        contract = load_json(path)
        task_id = contract.get("id")
        found_ids.add(task_id)
        if path.stem != task_id:
            fail(f"contract filename/id mismatch: {path.name} vs {task_id!r}")
        required = ["objective", "dependencies", "allowed_paths", "forbidden_paths", "steps", "tests", "reviewers", "acceptance", "commands", "handoff_outputs"]
        missing = [field for field in required if field not in contract]
        if missing:
            fail(f"{path.name} missing fields: {', '.join(missing)}")
        backlog_task = next((task for task in tasks if task["id"] == task_id), None)
        if backlog_task is None:
            fail(f"contract {path.name} has no backlog task")
        if backlog_task.get("contract") != str(path.relative_to(ROOT)):
            fail(f"{task_id} backlog contract path differs from {path.relative_to(ROOT)}")
        if contract.get("status") != backlog_task["status"]:
            fail(f"{task_id} contract status differs from backlog")
        if contract["dependencies"] != backlog_task["dependencies"]:
            fail(f"{task_id} contract dependencies differ from backlog")
    if found_ids != expected_ids:
        fail(f"detailed contract set differs from backlog: expected {sorted(expected_ids)}, found {sorted(found_ids)}")
    return len(files)


def check_plans() -> None:
    for path in sorted((ROOT / "docs/exec-plans/active").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        missing = [section for section in LIVING_SECTIONS if section not in text]
        if missing:
            fail(f"active plan {path.name} missing living sections: {', '.join(missing)}")


def check_agent_wrappers() -> None:
    for base in [ROOT / ".agents/skills", ROOT / ".claude/skills"]:
        if not base.exists():
            fail(f"missing agent skill directory {base.relative_to(ROOT)}")
        for skill in base.glob("*/SKILL.md"):
            text = skill.read_text(encoding="utf-8")
            match = re.search(r"agents/workflows/([a-z0-9-]+\.md)", text)
            if not match:
                fail(f"{skill.relative_to(ROOT)} does not reference a canonical workflow")
            if not (ROOT / "agents/workflows" / match.group(1)).is_file():
                fail(f"{skill.relative_to(ROOT)} references missing workflow {match.group(1)}")


def check_trusted_placeholders() -> None:
    for path in (ROOT / "lean").rglob("*.lean"):
        text = path.read_text(encoding="utf-8")
        if re.search(r"\b(sorry|admit)\b", text):
            fail(f"trusted placeholder found in {path.relative_to(ROOT)}")


def check_status(
    tasks: list[dict], done: set[str], ready: set[str], active: set[str]
) -> None:
    status = load_json(ROOT / "work/status.yaml")
    if set(status.get("done", [])) != done:
        fail("work/status.yaml done set differs from backlog")
    if status.get("ready") != sorted(ready):
        fail("work/status.yaml ready set differs from backlog")
    if status.get("in_progress") != sorted(active):
        fail("work/status.yaml in_progress set differs from backlog")
    blocked_count = sum(task["status"] == "BLOCKED" for task in tasks)
    if status.get("blocked_count") != blocked_count:
        fail("work/status.yaml blocked_count differs from backlog")
    if status.get("project_maturity") != "Draft":
        fail("initial project maturity must be Draft")


def main() -> None:
    check_readiness_regression_fixtures()
    check_required_files()
    tasks, done, ready, active = check_backlog()
    contract_count = check_contracts(tasks)
    check_plans()
    check_agent_wrappers()
    check_trusted_placeholders()
    check_status(tasks, done, ready, active)
    print("StatQED repository checks passed:")
    print(f"  {len(tasks)} backlog tasks")
    print(f"  {contract_count} detailed task contracts")
    print(f"  dependency-ready tasks: {', '.join(sorted(ready)) or 'none'}")
    print(f"  active tasks: {', '.join(sorted(active)) or 'none'}")


if __name__ == "__main__":
    main()
