#!/usr/bin/env python3
"""Validate the architecture-first StatQED repository scaffold."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_TASK_STATUS = {"READY", "IN_PROGRESS", "BLOCKED", "IN_REVIEW", "DONE", "SUPERSEDED"}
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


def check_backlog() -> tuple[list[dict], set[str]]:
    payload = load_json(ROOT / "work/backlog.yaml")
    tasks = payload.get("tasks")
    if not isinstance(tasks, list) or len(tasks) != 60:
        fail(f"expected exactly 60 backlog tasks, found {len(tasks) if isinstance(tasks, list) else 'non-list'}")

    ids = [task.get("id") for task in tasks]
    expected = [f"SQ-{number:04d}" for number in range(1, 61)]
    if ids != expected:
        fail("task IDs must be unique and sequential SQ-0001 through SQ-0060")

    by_id = {task["id"]: task for task in tasks}
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
    computed_ready = {
        task["id"]
        for task in tasks
        if task["status"] not in {"DONE", "SUPERSEDED"}
        and all(dep in done for dep in task["dependencies"])
    }
    declared_ready = {task["id"] for task in tasks if task["status"] == "READY"}
    if computed_ready != declared_ready:
        fail(f"declared READY tasks {sorted(declared_ready)} do not match dependency-ready tasks {sorted(computed_ready)}")
    if declared_ready != {"SQ-0001"}:
        fail(f"initial ready set must be only SQ-0001, found {sorted(declared_ready)}")

    return tasks, done


def check_contracts(tasks: list[dict]) -> int:
    expected_ids = {f"SQ-{number:04d}" for number in range(1, 21)}
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
        backlog_task = next(task for task in tasks if task["id"] == task_id)
        if contract["dependencies"] != backlog_task["dependencies"]:
            fail(f"{task_id} contract dependencies differ from backlog")
    if found_ids != expected_ids:
        fail(f"expected detailed contracts SQ-0001..SQ-0020, found {sorted(found_ids)}")
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


def check_status(done: set[str]) -> None:
    status = load_json(ROOT / "work/status.yaml")
    if set(status.get("done", [])) != done:
        fail("work/status.yaml done set differs from backlog")
    if status.get("ready") != ["SQ-0001"]:
        fail("initial status ready list must be [SQ-0001]")
    if status.get("project_maturity") != "Draft":
        fail("initial project maturity must be Draft")


def main() -> None:
    check_required_files()
    tasks, done = check_backlog()
    contract_count = check_contracts(tasks)
    check_plans()
    check_agent_wrappers()
    check_trusted_placeholders()
    check_status(done)
    print("StatQED repository checks passed:")
    print(f"  {len(tasks)} backlog tasks")
    print(f"  {contract_count} detailed task contracts")
    print("  initial dependency-ready task: SQ-0001")


if __name__ == "__main__":
    main()
