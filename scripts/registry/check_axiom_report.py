#!/usr/bin/env python3
"""Fail-closed static verification of the SQ-0007 live axiom observation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REQUIRED = {
    "StatQED.Registry.Tests.falseImpliesTrue",
    "StatQED.Registry.Tests.testOnlyTrue",
    "StatQED.Registry.Tests.testOnlyTrueRefactor",
    "True.intro",
}


def verify(path: Path) -> None:
    report = json.loads(path.read_text(encoding="utf-8"))
    if report.get("schema") != "statqed.registry-axioms.v0":
        raise ValueError("registry.axiom_report_schema")
    declarations = report.get("declarations")
    if not isinstance(declarations, list) or len(declarations) > 256:
        raise ValueError("registry.resource_limit")
    names = [item.get("declaration") for item in declarations]
    if names != sorted(names) or set(names) != REQUIRED:
        raise ValueError("registry.axiom_report_declarations")
    for item in declarations:
        if set(item) != {
            "axioms", "declaration", "kind", "normalized_type", "normalizer",
            "origin", "type_repr_diagnostic", "unsafe",
        }:
            raise ValueError("registry.axiom_report_shape")
        if item["normalizer"] != "statqed.lean-expr.v0":
            raise ValueError("registry.axiom_report_normalizer")
        if item["unsafe"] is not False or item["axioms"] != []:
            raise ValueError("registry.forbidden_axiom")
        if not isinstance(item["normalized_type"], dict):
            raise ValueError("registry.axiom_report_type")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", type=Path, required=True)
    args = parser.parse_args()
    try:
        verify(args.check)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"SQ-0007 axiom report failed: {error}")
        return 1
    print(f"SQ-0007 axiom report verified: 4 declarations, 0 axioms, sha256 {hashlib.sha256(args.check.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
