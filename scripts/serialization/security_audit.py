#!/usr/bin/env python3
"""Reproduce the hash-bound offline RustSec observation for SQ-0005."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tarfile
import tempfile
from typing import Any


REPOSITORY = Path(__file__).resolve().parents[2]
PROTOTYPE = REPOSITORY / "schemas/prototypes/rust-cbor"
SECURITY_LOCK = PROTOTYPE / "evidence/security-lock.json"
DEFAULT_REPORT = PROTOTYPE / "evidence/advisory-report.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def safe_extract(archive: Path, destination: Path, *, strip_first: bool) -> None:
    with tarfile.open(archive, "r:gz") as bundle:
        for member in bundle.getmembers():
            parts = Path(member.name).parts
            if strip_first and parts:
                parts = parts[1:]
            if not parts:
                continue
            relative = Path(*parts)
            if (
                member.islnk()
                or member.issym()
                or relative.is_absolute()
                or ".." in parts
            ):
                raise RuntimeError(f"unsafe archive member: {member.name}")
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if member.isdir():
                target.mkdir(exist_ok=True)
                continue
            if not member.isfile():
                raise RuntimeError(f"unsupported archive member: {member.name}")
            source = bundle.extractfile(member)
            if source is None:
                raise RuntimeError(f"unreadable archive member: {member.name}")
            with target.open("wb") as stream:
                for block in iter(lambda: source.read(1024 * 1024), b""):
                    stream.write(block)
            target.chmod(member.mode & 0o777)


def require_hash(path: Path, expected: str, label: str) -> None:
    if not path.is_file() or sha256(path) != expected:
        raise RuntimeError(f"{label} is missing or has the wrong SHA-256")


def build_report(cargo_audit_archive: Path, rustsec_archive: Path) -> dict[str, Any]:
    security_lock = load_json(SECURITY_LOCK)
    cargo_lock = PROTOTYPE / "Cargo.lock"
    inventory = PROTOTYPE / "evidence/dependency-license-inventory.json"
    require_hash(
        cargo_audit_archive,
        security_lock["cargo_audit"]["archive_sha256"],
        "cargo-audit archive",
    )
    require_hash(
        rustsec_archive,
        security_lock["rustsec_advisory_db"]["archive_sha256"],
        "RustSec archive",
    )
    require_hash(cargo_lock, security_lock["cargo_lock_sha256"], "Cargo.lock")
    require_hash(
        inventory,
        security_lock["dependency_license_inventory_sha256"],
        "dependency inventory",
    )

    with tempfile.TemporaryDirectory(prefix="statqed-sq0005-rustsec-") as name:
        temporary = Path(name)
        executable_root = temporary / "cargo-audit"
        database_root = temporary / "advisory-db"
        executable_root.mkdir()
        database_root.mkdir()
        safe_extract(cargo_audit_archive, executable_root, strip_first=True)
        safe_extract(rustsec_archive, database_root, strip_first=True)
        executable = executable_root / "cargo-audit"
        require_hash(
            executable,
            security_lock["cargo_audit"]["executable_sha256"],
            "cargo-audit executable",
        )
        executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
        version = subprocess.run(
            [str(executable), "--version"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        expected_version = "cargo-audit " + security_lock["cargo_audit"]["version"]
        if version.returncode != 0 or version.stdout.strip() != expected_version:
            raise RuntimeError("cargo-audit version mismatch")
        environment = {
            "CARGO_HOME": str(temporary / "cargo-home"),
            "HOME": str(temporary / "home"),
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "PATH": os.pathsep.join([str(executable_root), "/usr/bin", "/bin"]),
            "TZ": "UTC",
        }
        scan = subprocess.run(
            [
                str(executable),
                "audit",
                "--db",
                str(database_root),
                "--no-fetch",
                "--stale",
                "--no-yanked",
                "--file",
                str(cargo_lock),
                "--json",
            ],
            cwd=PROTOTYPE,
            env=environment,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            timeout=120,
        )
        if scan.returncode != 0:
            raise RuntimeError("cargo-audit failed: " + scan.stderr.strip())
        observed = json.loads(scan.stdout)

    vulnerabilities = observed.get("vulnerabilities", {})
    warnings = observed.get("warnings", {})
    if vulnerabilities.get("found") is not False or vulnerabilities.get("count") != 0:
        raise RuntimeError("RustSec reported a vulnerability in the exact lock")
    if warnings:
        raise RuntimeError("RustSec reported warnings in the exact lock")
    return {
        "advisory_observed_at": security_lock["advisory_observed_at"],
        "cargo_audit": {
            "archive_sha256": security_lock["cargo_audit"]["archive_sha256"],
            "executable_sha256": security_lock["cargo_audit"]["executable_sha256"],
            "version": security_lock["cargo_audit"]["version"],
        },
        "cargo_lock_sha256": security_lock["cargo_lock_sha256"],
        "limitations": [
            "This is a point-in-time RustSec observation, not a security guarantee.",
            "The scan covers the exact prototype Cargo.lock graph, not Rust, Cargo, the operating system, CPython, or unmodeled native libraries.",
            "Yanked-state network queries are disabled for reproducible offline verification.",
            "Prototype dependencies remain outside production authority and the verification-mode trusted computing base.",
        ],
        "result": {
            "dependency_count_reported_by_cargo_audit": observed.get(
                "lockfile", {}
            ).get("dependency-count"),
            "vulnerability_count": 0,
            "warning_count": 0,
        },
        "rustsec_advisory_db": {
            "archive_sha256": security_lock["rustsec_advisory_db"][
                "archive_sha256"
            ],
            "commit": security_lock["rustsec_advisory_db"]["commit"],
        },
        "schema_version": 1,
    }


def canonical_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cargo-audit-archive", required=True, type=Path)
    parser.add_argument("--rustsec-archive", required=True, type=Path)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--write", action="store_true")
    arguments = parser.parse_args()
    try:
        rendered = canonical_bytes(
            build_report(arguments.cargo_audit_archive, arguments.rustsec_archive)
        )
    except (
        json.JSONDecodeError,
        OSError,
        RuntimeError,
        subprocess.TimeoutExpired,
        tarfile.TarError,
    ) as error:
        print(f"SQ-0005 security audit failed: {error}", file=sys.stderr)
        return 1
    if arguments.write:
        arguments.report.parent.mkdir(parents=True, exist_ok=True)
        arguments.report.write_bytes(rendered)
        print("wrote SQ-0005 hash-bound advisory report")
        return 0
    if not arguments.report.is_file() or arguments.report.read_bytes() != rendered:
        print("retained SQ-0005 advisory report is stale", file=sys.stderr)
        return 1
    print("SQ-0005 advisory report verified: 0 vulnerabilities, 0 warnings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
