#!/usr/bin/env python3
"""Run or verify the hash-bound, offline RustSec scan for SQ-0004."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
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
            if member.islnk() or member.issym() or Path(*parts).is_absolute() or ".." in parts:
                raise RuntimeError(f"unsafe archive member: {member.name}")
            target = destination.joinpath(*parts)
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
                while chunk := source.read(1024 * 1024):
                    stream.write(chunk)
            target.chmod(member.mode & 0o777)


def build_report(cargo_audit_archive: Path, rustsec_archive: Path) -> dict[str, Any]:
    security_lock = load_json(ROOT / "evidence/security-lock.json")
    cargo_lock = ROOT / "Cargo.lock"
    inventory = ROOT / "evidence/dependency-license-inventory.json"
    checks = [
        (cargo_audit_archive, security_lock["cargo_audit"]["archive_sha256"], "cargo-audit archive"),
        (rustsec_archive, security_lock["rustsec_advisory_db"]["archive_sha256"], "RustSec archive"),
        (cargo_lock, security_lock["cargo_lock_sha256"], "Cargo.lock"),
        (inventory, security_lock["dependency_license_inventory_sha256"], "license inventory"),
    ]
    for path, expected, label in checks:
        if not path.is_file() or sha256(path) != expected:
            raise RuntimeError(f"{label} is unavailable or has the wrong SHA-256")

    with tempfile.TemporaryDirectory(prefix="statqed-security-audit-") as temporary_name:
        temporary = Path(temporary_name)
        audit_root = temporary / "cargo-audit"
        database_root = temporary / "advisory-db"
        audit_root.mkdir()
        database_root.mkdir()
        safe_extract(cargo_audit_archive, audit_root, strip_first=True)
        safe_extract(rustsec_archive, database_root, strip_first=True)
        executable = audit_root / "cargo-audit"
        if not executable.is_file():
            raise RuntimeError("cargo-audit executable is missing from reviewed archive")
        if sha256(executable) != security_lock["cargo_audit"]["executable_sha256"]:
            raise RuntimeError("cargo-audit executable SHA-256 mismatch")
        executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
        version = subprocess.run(
            [str(executable), "--version"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
            check=False,
        )
        if version.returncode != 0 or version.stdout.strip() != "cargo-audit 0.22.2":
            raise RuntimeError("cargo-audit identity mismatch")
        environment = {
            "HOME": str(temporary / "home"),
            "CARGO_HOME": str(temporary / "cargo-home"),
            "PATH": os.pathsep.join([str(executable.parent), "/usr/bin", "/bin"]),
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "TZ": "UTC",
        }
        observed = subprocess.run(
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
            cwd=ROOT,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120,
            check=False,
        )
        if observed.returncode != 0:
            raise RuntimeError(f"cargo-audit failed: {observed.stderr.strip()}")
        raw = json.loads(observed.stdout)

    vulnerabilities = raw.get("vulnerabilities", {})
    warnings = raw.get("warnings", {})
    if vulnerabilities.get("found") is not False or vulnerabilities.get("count") != 0:
        raise RuntimeError("RustSec reported a vulnerability in the exact locked graph")
    if warnings:
        raise RuntimeError("RustSec reported warnings in the exact locked graph")
    return {
        "schema_version": 1,
        "cargo_lock_sha256": security_lock["cargo_lock_sha256"],
        "cargo_audit": {
            "version": security_lock["cargo_audit"]["version"],
            "archive_sha256": security_lock["cargo_audit"]["archive_sha256"],
            "executable_sha256": security_lock["cargo_audit"]["executable_sha256"],
        },
        "rustsec_advisory_db": {
            "commit": security_lock["rustsec_advisory_db"]["commit"],
            "archive_sha256": security_lock["rustsec_advisory_db"]["archive_sha256"],
        },
        "result": {
            "vulnerability_count": 0,
            "warning_count": 0,
            "dependency_count_reported_by_cargo_audit": raw.get("lockfile", {}).get("dependency-count"),
        },
        "limitations": [
            "This is a point-in-time RustSec database observation, not a security guarantee.",
            "The scan covers the exact Cargo.lock crate graph, not rustc, Cargo, rustup, the operating system, or unmodeled native libraries.",
            "Yanked-state network queries are disabled so the scan is reproducible and offline.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cargo-audit-archive", type=Path, required=True)
    parser.add_argument("--rustsec-archive", type=Path, required=True)
    parser.add_argument("--report", type=Path, default=ROOT / "evidence/advisory-report.json")
    parser.add_argument("--write", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = build_report(args.cargo_audit_archive, args.rustsec_archive)
    except (OSError, RuntimeError, subprocess.TimeoutExpired, tarfile.TarError, json.JSONDecodeError) as error:
        print(f"security audit failed: {error}", file=sys.stderr)
        return 1
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.write:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered, encoding="utf-8")
        print("wrote hash-bound RustSec advisory report")
        return 0
    if not args.report.is_file() or args.report.read_text(encoding="utf-8") != rendered:
        print("retained advisory report differs from the exact offline scan", file=sys.stderr)
        return 1
    print(
        "verified RustSec advisory report: 0 vulnerabilities, 0 warnings, "
        f"database {report['rustsec_advisory_db']['commit']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
