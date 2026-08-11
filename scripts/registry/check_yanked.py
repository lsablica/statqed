#!/usr/bin/env python3
"""Verify the reviewed N/A crates.io yanked-state observation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    value = json.loads((ROOT / "backend/crates/statqed-registry/evidence/supply-chain.json").read_text())
    if value.get("third_party_dependencies") != 0 or "not applicable" not in value.get("yanked_observation", ""):
        print("SQ-0007 yanked-state observation failed")
        return 1
    print("SQ-0007 yanked-state observation verified: no crates.io package in exact graph")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
