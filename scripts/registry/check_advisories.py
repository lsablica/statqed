#!/usr/bin/env python3
"""Verify the reviewed N/A advisory observation for the exact std-only graph."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    path = ROOT / "backend/crates/statqed-registry/evidence/supply-chain.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    if not (
        value.get("schema") == "statqed.registry-rust-supply-chain.v0"
        and value.get("third_party_dependencies") == 0
        and value.get("advisory_database_required_for_graph") is False
        and "not a security guarantee" in value.get("advisory_observation", "")
    ):
        print("SQ-0007 advisory observation failed")
        return 1
    print("SQ-0007 advisory observation verified: no third-party Cargo package to match; point-in-time non-guarantee retained")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
