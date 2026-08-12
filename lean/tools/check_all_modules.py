#!/usr/bin/env python3
"""Replay every tracked StatQED module in a fresh Lean kernel environment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Callable

from project_axiom_report import LEAN_ROOT, REPOSITORY_ROOT, ProjectTrustError, run, source_modules


SCHEMA = "statqed.all-module-fresh-check.v1"


def check_all(
    repository_root: Path = REPOSITORY_ROOT,
    lean_root: Path = LEAN_ROOT,
    *,
    timeout_per_module: int = 180,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, object]:
    modules = source_modules(repository_root, lean_root)
    results: list[dict[str, object]] = []
    for module in modules:
        command = ["lake", "env", "leanchecker", "--fresh", module]
        completed = run(
            command,
            cwd=lean_root,
            timeout=timeout_per_module,
            runner=runner,
        )
        result = {
            "command": command,
            "exit_status": completed.returncode,
            "module": module,
        }
        results.append(result)
        if completed.returncode != 0:
            detail = completed.stderr.strip() or completed.stdout.strip()
            raise ProjectTrustError(
                f"fresh kernel replay failed for {module} with exit {completed.returncode}: {detail}"
            )
    if len(results) != len(modules):
        raise ProjectTrustError("fresh replay count differs from tracked module count")
    return {
        "module_count": len(modules),
        "modules": modules,
        "results": results,
        "schema_version": SCHEMA,
        "status": "pass",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit deterministic JSON")
    parser.add_argument("--timeout-per-module", type=int, default=180)
    arguments = parser.parse_args()
    try:
        if arguments.timeout_per_module < 1 or arguments.timeout_per_module > 600:
            raise ProjectTrustError("timeout-per-module must be between 1 and 600 seconds")
        result = check_all(timeout_per_module=arguments.timeout_per_module)
        if arguments.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(f"all-module fresh check passed: {result['module_count']} modules")
            for module in result["modules"]:
                print(f"  {module}")
    except (OSError, ProjectTrustError, subprocess.SubprocessError) as error:
        print(f"all-module fresh check error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
