#!/usr/bin/env python3
"""Run clean current-Cargo and offline-floor SQ-0004 checks."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "rustc_dev": "rustc 1.97.1 (8bab26f4f 2026-07-14)",
    "cargo_dev": "cargo 1.97.1 (c980f4866 2026-06-30)",
    "rustc_floor": "rustc 1.85.1 (4eb161250 2025-03-15)",
    "cargo_floor": "cargo 1.85.1 (d73d2caf9 2024-12-31)",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def environment(temporary: Path, *, offline: bool) -> dict[str, str]:
    cargo = shutil.which("cargo")
    if cargo is None:
        raise RuntimeError("cargo proxy is unavailable")
    values = {
        "HOME": temporary / "home",
        "CARGO_HOME": temporary / "cargo-home",
        "CARGO_TARGET_DIR": temporary / "target",
        "XDG_CONFIG_HOME": temporary / "xdg-config",
        "XDG_CACHE_HOME": temporary / "xdg-cache",
        "TMPDIR": temporary / "tmp",
    }
    for value in values.values():
        value.mkdir(parents=True, exist_ok=True)
    result = {
        **{key: str(value) for key, value in values.items()},
        "RUSTUP_HOME": os.environ.get("RUSTUP_HOME", str(Path.home() / ".rustup")),
        "PATH": os.pathsep.join([str(Path(cargo).resolve().parent), "/usr/bin", "/bin"]),
        "CARGO_REGISTRIES_CRATES_IO_PROTOCOL": "sparse",
        "CARGO_TERM_COLOR": "never",
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "TZ": "UTC",
    }
    if offline:
        result["CARGO_NET_OFFLINE"] = "true"
    forbidden = [
        key
        for key in result
        if key.startswith("CARGO_")
        and any(marker in key for marker in ("TOKEN", "CREDENTIAL", "SECRET"))
    ]
    if forbidden:
        raise RuntimeError(f"constructed environment contains credentials: {forbidden}")
    return result


def run_command(
    command: list[str], cwd: Path, env: dict[str, str], command_id: str
) -> dict[str, Any]:
    started = dt.datetime.now(dt.timezone.utc)
    monotonic_start = time.monotonic()
    observed = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=300,
        check=False,
    )
    ended = dt.datetime.now(dt.timezone.utc)
    return {
        "id": command_id,
        "command": command,
        "cwd": "backend",
        "start": started.isoformat().replace("+00:00", "Z"),
        "end": ended.isoformat().replace("+00:00", "Z"),
        "elapsed_seconds": round(time.monotonic() - monotonic_start, 3),
        "exit_status": observed.returncode,
        "stdout": observed.stdout,
        "stderr": observed.stderr,
    }


def run_suite() -> dict[str, Any]:
    started = dt.datetime.now(dt.timezone.utc)
    committed_lock = (ROOT / "Cargo.lock").read_bytes()
    records: list[dict[str, Any]] = []
    version_commands = [
        (["rustc", "+1.97.1", "--version"], "rustc-dev-version"),
        (["cargo", "+1.97.1", "--version"], "cargo-dev-version"),
        (["rustc", "+1.85.1", "--version"], "rustc-floor-version"),
        (["cargo", "+1.85.1", "--version"], "cargo-floor-version"),
    ]
    with tempfile.TemporaryDirectory(prefix="statqed-version-identities-") as temporary_name:
        version_environment = environment(Path(temporary_name), offline=True)
        for command, command_id in version_commands:
            records.append(run_command(command, ROOT, version_environment, command_id))

    lock_reproductions = []
    for repetition in (1, 2):
        with tempfile.TemporaryDirectory(prefix=f"statqed-lock-{repetition}-") as temporary_name:
            temporary = Path(temporary_name)
            project = temporary / "backend"
            shutil.copytree(ROOT, project, ignore=shutil.ignore_patterns("target", "__pycache__", "*.pyc"))
            (project / "Cargo.lock").unlink()
            isolated = environment(temporary / "isolation", offline=False)
            generation = run_command(
                ["cargo", "+1.97.1", "generate-lockfile"],
                project,
                isolated,
                f"lock-generation-{repetition}",
            )
            records.append(generation)
            reproduced = project / "Cargo.lock"
            identical = reproduced.is_file() and reproduced.read_bytes() == committed_lock
            lock_reproductions.append(
                {
                    "id": f"lock-reproduction-{repetition}",
                    "byte_identical": identical,
                    "sha256": sha256(reproduced) if reproduced.is_file() else None,
                }
            )
            if generation["exit_status"] != 0 or not identical:
                raise RuntimeError(f"clean lock reproduction {repetition} failed")

    with tempfile.TemporaryDirectory(prefix="statqed-dev-acquisition-") as temporary_name:
        temporary = Path(temporary_name)
        isolated = environment(temporary, offline=False)
        dev_commands = [
            (["cargo", "+1.97.1", "fetch", "--locked"], "dev-fetch-locked"),
            (
                ["cargo", "+1.97.1", "metadata", "--locked", "--offline", "--format-version", "1"],
                "dev-metadata-locked-offline",
            ),
            (["cargo", "+1.97.1", "fmt", "--all", "--", "--check"], "dev-fmt"),
            (
                [
                    "cargo",
                    "+1.97.1",
                    "clippy",
                    "--workspace",
                    "--all-targets",
                    "--all-features",
                    "--locked",
                    "--offline",
                    "--",
                    "-D",
                    "warnings",
                ],
                "dev-clippy",
            ),
            (
                [
                    "cargo",
                    "+1.97.1",
                    "test",
                    "--workspace",
                    "--all-features",
                    "--locked",
                    "--offline",
                ],
                "dev-tests",
            ),
            (
                [
                    "cargo",
                    "+1.97.1",
                    "run",
                    "--quiet",
                    "--locked",
                    "--offline",
                    "-p",
                    "statqed-cli",
                    "--",
                    "version",
                    "--format",
                    "json",
                ],
                "dev-cli-json",
            ),
        ]
        for command, command_id in dev_commands:
            record = run_command(command, ROOT, isolated, command_id)
            records.append(record)
            if record["exit_status"] != 0:
                raise RuntimeError(f"development command failed: {command_id}")

    with tempfile.TemporaryDirectory(prefix="statqed-floor-offline-") as temporary_name:
        temporary = Path(temporary_name)
        isolated = environment(temporary, offline=True)
        floor_commands = [
            (
                ["cargo", "+1.85.1", "metadata", "--locked", "--offline", "--format-version", "1"],
                "floor-metadata-locked-offline",
            ),
            (
                [
                    "cargo",
                    "+1.85.1",
                    "clippy",
                    "--workspace",
                    "--all-targets",
                    "--all-features",
                    "--locked",
                    "--offline",
                    "--",
                    "-D",
                    "warnings",
                ],
                "floor-clippy-locked-offline",
            ),
            (
                [
                    "cargo",
                    "+1.85.1",
                    "test",
                    "--workspace",
                    "--all-features",
                    "--locked",
                    "--offline",
                ],
                "floor-tests-locked-offline",
            ),
        ]
        for command, command_id in floor_commands:
            record = run_command(command, ROOT, isolated, command_id)
            records.append(record)
            if record["exit_status"] != 0:
                raise RuntimeError(f"offline floor command failed: {command_id}")

    observed_versions = {record["id"]: record["stdout"].strip() for record in records}
    expected_versions = {
        "rustc-dev-version": EXPECTED["rustc_dev"],
        "cargo-dev-version": EXPECTED["cargo_dev"],
        "rustc-floor-version": EXPECTED["rustc_floor"],
        "cargo-floor-version": EXPECTED["cargo_floor"],
    }
    for command_id, expected in expected_versions.items():
        if observed_versions.get(command_id) != expected:
            raise RuntimeError(f"tool identity mismatch: {command_id}")

    return {
        "schema_version": 1,
        "classification": "success",
        "start": started.isoformat().replace("+00:00", "Z"),
        "end": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "cargo_lock_sha256": hashlib.sha256(committed_lock).hexdigest(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "container": "none detected or claimed",
        },
        "environment_policy": {
            "inherited": ["RUSTUP_HOME location only"],
            "constructed": [
                "HOME",
                "CARGO_HOME",
                "CARGO_TARGET_DIR",
                "XDG_CONFIG_HOME",
                "XDG_CACHE_HOME",
                "TMPDIR",
                "PATH",
                "CARGO_REGISTRIES_CRATES_IO_PROTOCOL=sparse",
                "CARGO_TERM_COLOR=never",
                "LANG=C.UTF-8",
                "LC_ALL=C.UTF-8",
                "TZ=UTC",
                "CARGO_NET_OFFLINE=true for all floor commands",
            ],
            "credentials_inherited": False,
            "alternate_registries": False,
        },
        "lock_reproductions": lock_reproductions,
        "commands": records,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = run_suite()
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(f"isolated Rust checks failed: {error}", file=sys.stderr)
        return 1
    if args.record:
        args.record.parent.mkdir(parents=True, exist_ok=True)
        args.record.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote isolated Rust evidence: {len(report['commands'])} commands")
    else:
        print(
            "isolated Rust checks passed: two lock reproductions, "
            "development acquisition/build, offline 1.85.1 floor"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
