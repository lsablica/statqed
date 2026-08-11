#!/usr/bin/env python3
"""Verify the exact std-only standalone registry dependency inventory."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CRATE = ROOT / "backend/crates/statqed-registry"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    lock = (CRATE / "Cargo.lock").read_text(encoding="utf-8")
    inventory = json.loads((CRATE / "evidence/dependency-inventory.json").read_text())
    ok = (
        inventory.get("schema") == "statqed.registry-rust-dependency-inventory.v0"
        and inventory.get("dependencies") == []
        and inventory.get("build_scripts") == []
        and inventory.get("native_dependencies") == []
        and lock.count("[[package]]") == 1
        and 'name = "statqed-registry"' in lock
        and "source = " not in lock
        and "checksum = " not in lock
    )
    if not ok:
        print("SQ-0007 dependency inventory failed")
        return 1
    print(f"SQ-0007 dependency inventory verified: 1 local package, 0 third-party; lock {hashlib.sha256(lock.encode()).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
