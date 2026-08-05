#!/usr/bin/env python3
"""Retain exact owned-dispatcher output for a Python endpoint."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[4]
PROBE = Path(__file__).resolve().parent
LOGS = ROOT / "docs/research/toolchain-prototypes/logs/python/run-20260805"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("development", "floor"))
    args = parser.parse_args()
    attempt_id = f"python-{args.mode}-owned-verify"
    command = ["/usr/bin/bash", str(PROBE / "verify-probe.sh"), args.mode]
    started = dt.datetime.now(dt.UTC)
    completed = subprocess.run(
        command,
        cwd=PROBE,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    ended = dt.datetime.now(dt.UTC)
    LOGS.mkdir(parents=True, exist_ok=True)
    (LOGS / f"{attempt_id}.stdout.log").write_text(
        completed.stdout, encoding="utf-8"
    )
    (LOGS / f"{attempt_id}.stderr.log").write_text(
        completed.stderr, encoding="utf-8"
    )
    record = {
        "id": attempt_id,
        "command": command,
        "cwd": str(PROBE.relative_to(ROOT)),
        "environment": {
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "PYTHONHASHSEED": "0",
        },
        "started_at": started.isoformat(timespec="seconds"),
        "ended_at": ended.isoformat(timespec="seconds"),
        "exit_status": completed.returncode,
    }
    (LOGS / f"{attempt_id}.command.json").write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(record, indent=2))
    raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()
