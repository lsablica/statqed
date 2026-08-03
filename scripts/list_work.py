#!/usr/bin/env python3
"""Print a compact dependency-aware summary of the StatQED work ledger."""

from __future__ import annotations

from collections import Counter

from check_repository import check_backlog


def main() -> None:
    tasks, _done, ready_ids, active_ids = check_backlog()
    by_id = {task["id"]: task for task in tasks}
    counts = Counter(task["status"] for task in tasks)

    print("StatQED work ledger")
    print("-------------------")
    print(" ".join(f"{status}={counts[status]}" for status in sorted(counts)))
    print("\nDependency-ready tasks:")
    for task_id in sorted(ready_ids):
        task = by_id[task_id]
        print(f"  {task['id']}  {task['title']}")
        print(f"           plan: {task['plan']}")
        if task.get("contract"):
            print(f"       contract: {task['contract']}")
    if not ready_ids:
        print("  none")

    print("\nActive tasks:")
    for task_id in sorted(active_ids):
        task = by_id[task_id]
        print(f"  {task['id']}  {task['title']} ({task['status']})")
    if not active_ids:
        print("  none")


if __name__ == "__main__":
    main()
