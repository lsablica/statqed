#!/usr/bin/env python3
"""Record exact stdout/stderr and command intervals for bounded Arrow attempts."""

from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[4]
PROBE = Path(__file__).resolve().parent
LOGS = ROOT / "docs/research/toolchain-prototypes/logs/arrow"


def run(attempt_id: str, command: list[str], environment: dict[str, str]) -> dict[str, object]:
    started = dt.datetime.now().astimezone()
    completed = subprocess.run(
        command,
        cwd=PROBE,
        env={**os.environ, **environment},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    ended = dt.datetime.now().astimezone()
    LOGS.mkdir(parents=True, exist_ok=True)
    (LOGS / f"{attempt_id}.stdout.log").write_text(completed.stdout, encoding="utf-8")
    (LOGS / f"{attempt_id}.stderr.log").write_text(completed.stderr, encoding="utf-8")
    return {
        "id": attempt_id,
        "command": command,
        "environment": environment,
        "started_at": started.isoformat(timespec="seconds"),
        "ended_at": ended.isoformat(timespec="seconds"),
        "exit_status": completed.returncode,
    }


def main() -> None:
    metadata_path = LOGS / "attempt-metadata.json"
    attempts = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else []
    result = run(
        "arrow-pyarrow25-arrow-rs59-cross-lineage-hash-bound",
        ["bash", str(PROBE / "run-probes.sh")],
        {
            "STATQED_UV": "/tmp/statqed-sq0002-python-tools/uv",
            "STATQED_ARROW_PYTHON": "/tmp/statqed-sq0002-python-runtimes/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14",
            "RUSTUP_HOME": "/tmp/statqed-sq0002-rust-cache/rustup",
            "RUSTUP_TOOLCHAIN": "1.97.1",
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
        },
    )
    attempts = [attempt for attempt in attempts if attempt["id"] != result["id"]]
    attempts.append(result)
    metadata_path.write_text(json.dumps(attempts, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(attempts, indent=2))


if __name__ == "__main__":
    main()
