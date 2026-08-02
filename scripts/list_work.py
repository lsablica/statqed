#!/usr/bin/env python3
"""Print a compact dependency-aware summary of the StatQED work ledger."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    payload = json.loads((ROOT / "work/backlog.yaml").read_text(encoding="utf-8"))
    tasks = payload["tasks"]
    done = {task["id"] for task in tasks if task["status"] == "DONE"}
    ready = [
        task for task in tasks
        if task["status"] not in {"DONE", "SUPERSEDED"}
        and all(dep in done for dep in task["dependencies"])
    ]
    counts = Counter(task["status"] for task in tasks)

    print("StatQED work ledger")
    print("-------------------")
    print(" ".join(f"{status}={counts[status]}" for status in sorted(counts)))
    print("\nDependency-ready tasks:")
    for task in ready:
        print(f"  {task['id']}  {task['title']}")
        print(f"           plan: {task['plan']}")
        if task.get("contract"):
            print(f"       contract: {task['contract']}")
    if not ready:
        print("  none")


if __name__ == "__main__":
    main()
