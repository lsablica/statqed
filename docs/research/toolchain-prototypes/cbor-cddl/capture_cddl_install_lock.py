#!/usr/bin/env python3
"""Capture the exact published lock graph used by `cargo install cddl --locked`."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tomllib


def main() -> None:
    cargo_home = Path(sys.argv[1])
    output = Path(sys.argv[2])
    matches = sorted(cargo_home.glob("registry/src/*/cddl-0.10.6/Cargo.lock"))
    if len(matches) != 1:
        raise SystemExit(f"expected one cddl 0.10.6 published lock, found {len(matches)}")
    raw = matches[0].read_bytes()
    lock = tomllib.loads(raw.decode("utf-8"))
    packages = [
        {
            key: package[key]
            for key in ("name", "version", "source", "checksum", "dependencies")
            if key in package
        }
        for package in lock["package"]
    ]
    result = {
        "schema_note": "Exact published Cargo.lock graph consumed by cargo install cddl 0.10.6 --locked in the final development-runtime probe.",
        "cargo_lock_sha256": hashlib.sha256(raw).hexdigest(),
        "packages": packages,
    }
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"cddl_published_lock_sha256={result['cargo_lock_sha256']}")
    print(f"cddl_published_lock_packages={len(packages)}")


if __name__ == "__main__":
    main()
