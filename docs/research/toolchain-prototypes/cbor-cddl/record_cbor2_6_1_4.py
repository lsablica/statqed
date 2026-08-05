#!/usr/bin/env python3
"""Retain the exact command and output for the cbor2 6.1.4 probe."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[4]
PROBE = Path(__file__).resolve().parent
LOGS = ROOT / "docs/research/toolchain-prototypes/logs/cbor-cddl"
ATTEMPT_ID = "cbor2-6.1.4-security-regressions"


def main() -> None:
    command = ["/usr/bin/bash", str(PROBE / "verify-cbor2-6.1.4.sh")]
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
    (LOGS / f"{ATTEMPT_ID}.stdout.log").write_text(
        completed.stdout, encoding="utf-8"
    )
    (LOGS / f"{ATTEMPT_ID}.stderr.log").write_text(
        completed.stderr, encoding="utf-8"
    )
    record = {
        "id": ATTEMPT_ID,
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
    (LOGS / f"{ATTEMPT_ID}.command.json").write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(record, indent=2))
    raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()
