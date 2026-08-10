#!/usr/bin/env python3
"""Verify the retained, hash-bound cddl RustSec observation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
OBSERVATION = ROOT / "source-audits/schema/cddl-advisory-observation.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--cargo-audit", type=Path, required=True)
    parser.add_argument("--cargo-audit-archive", type=Path, required=True)
    parser.add_argument("--database-archive", type=Path, required=True)
    parser.add_argument("--cargo-lock", type=Path, required=True)
    args = parser.parse_args()

    expected = json.loads(OBSERVATION.read_text(encoding="utf-8"))
    report = json.loads(args.report.read_text(encoding="utf-8"))
    version = subprocess.run(
        [str(args.cargo_audit), "--version"],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    ).stdout.strip()
    checks = {
        "cargo-audit version": version == f"cargo-audit {expected['cargo_audit_version']}",
        "cargo-audit executable": sha256(args.cargo_audit) == expected["cargo_audit_executable_sha256"],
        "cargo-audit archive": sha256(args.cargo_audit_archive) == expected["cargo_audit_archive_sha256"],
        "database archive": sha256(args.database_archive) == expected["advisory_database_archive_sha256"],
        "Cargo.lock": sha256(args.cargo_lock) == expected["cargo_lock_sha256"],
        "advisory count": report["database"]["advisory-count"] == expected["result"]["advisory_count"],
        "dependency count": report["lockfile"]["dependency-count"] == expected["dependency_count"],
        "vulnerabilities": report["vulnerabilities"]["count"] == expected["result"]["vulnerabilities"] == 0,
        "warnings": len(report["warnings"]) == expected["result"]["warnings"] == 0,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise SystemExit("cddl advisory observation mismatch: " + ", ".join(failed))
    print(
        "cddl advisory observation reproduced: "
        f"{expected['dependency_count']} dependencies, "
        f"{expected['result']['advisory_count']} advisories, zero findings"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
