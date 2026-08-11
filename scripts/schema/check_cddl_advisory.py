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

EXPECTED_IDENTITIES = {
    "cargo_audit_version": "0.22.2",
    "cargo_audit_source_commit": "281452c35cf0870969042374110f099a411bc185",
    "cargo_audit_tag_object": "78bd4d48923d207898e94827cbd79d73903a85fa",
    "cargo_audit_license": "Apache-2.0 OR MIT",
    "advisory_database_commit": "309ad29d8fe448bf986019e05d47b9e0e29a2218",
    "advisory_database_license": "CC0-1.0; identified GHSA-derived content CC-BY-4.0",
}


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
        "source and license identities": all(
            expected.get(key) == value for key, value in EXPECTED_IDENTITIES.items()
        ),
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
