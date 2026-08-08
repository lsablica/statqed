#!/usr/bin/env python3
"""Generate or verify the SQ-0003 live Lean axiom report."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tomllib
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_TOOLCHAIN = "leanprover/lean4:v4.32.2"
EXPECTED_LEAN_COMMIT = "f3b06c705e6c85f5314019d5d3baab0fec5b580c"
EXPECTED_LAKE_VERSION = "5.0.0-src+f3b06c7"
EXPECTED_MATHLIB_REVISION = "905b95818eb32af7874a58b427f50c1711a5e96c"
PROHIBITED_IMPORTED_NATIVE_AXIOMS = {
    "Lean.ofReduceBool",
    "Lean.ofReduceNat",
    "Lean.trustCompiler",
}
PROBE_COMMAND = ["lake", "env", "lean", "--trust=0", "Tests/AxiomReport.lean"]
BEGIN_SENTINEL = "STATQED_AXIOM_REPORT_BEGIN"
END_SENTINEL = "STATQED_AXIOM_REPORT_END"


class ReportError(RuntimeError):
    """A fail-closed axiom-report generation error."""


def run(command: list[str], *, cwd: Path = ROOT) -> str:
    environment = os.environ.copy()
    environment["LC_ALL"] = "C.UTF-8"
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise ReportError(
            f"command failed with exit {completed.returncode}: {' '.join(command)}\n{detail}"
        )
    return completed.stdout.strip()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_manifest() -> tuple[dict[str, Any], dict[str, Any]]:
    path = ROOT / "lake-manifest.json"
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ReportError(f"cannot read generated Lake manifest: {error}") from error
    packages = manifest.get("packages")
    if not isinstance(packages, list):
        raise ReportError("Lake manifest has no package list")
    mathlib = next(
        (package for package in packages if package.get("name") == "mathlib"), None
    )
    if not isinstance(mathlib, dict):
        raise ReportError("Lake manifest has no Mathlib package")
    for field in ("inputRev", "rev"):
        if mathlib.get(field) != EXPECTED_MATHLIB_REVISION:
            raise ReportError(
                f"Mathlib manifest {field} is {mathlib.get(field)!r}, "
                f"expected {EXPECTED_MATHLIB_REVISION!r}"
            )
    return manifest, mathlib


def validate_configuration() -> None:
    toolchain = (ROOT / "lean-toolchain").read_text(encoding="utf-8").strip()
    if toolchain != EXPECTED_TOOLCHAIN:
        raise ReportError(
            f"lean-toolchain is {toolchain!r}, expected {EXPECTED_TOOLCHAIN!r}"
        )
    with (ROOT / "lakefile.toml").open("rb") as stream:
        lakefile = tomllib.load(stream)
    requirements = lakefile.get("require", [])
    mathlib = next(
        (entry for entry in requirements if entry.get("name") == "mathlib"), None
    )
    if not isinstance(mathlib, dict) or mathlib.get("rev") != EXPECTED_MATHLIB_REVISION:
        raise ReportError("lakefile.toml does not pin Mathlib to the reviewed full revision")


def source_modules() -> list[str]:
    modules = []
    for path in ROOT.glob("StatQED/**/*.lean"):
        modules.append(".".join(path.relative_to(ROOT).with_suffix("").parts))
    modules.append("StatQED")
    return sorted(set(modules))


def parse_probe(stdout: str) -> dict[str, Any]:
    lines = stdout.splitlines()
    if lines.count(BEGIN_SENTINEL) != 1 or lines.count(END_SENTINEL) != 1:
        raise ReportError("Lean axiom probe did not emit one complete sentinel pair")
    begin = lines.index(BEGIN_SENTINEL)
    end = lines.index(END_SENTINEL)
    if end != begin + 2:
        raise ReportError("Lean axiom probe emitted unexpected data inside its sentinel pair")
    try:
        probe = json.loads(lines[begin + 1])
    except json.JSONDecodeError as error:
        raise ReportError(f"Lean axiom probe emitted invalid JSON: {error}") from error
    if probe.get("schema_version") != 1:
        raise ReportError("Lean axiom probe schema version is not 1")
    if probe.get("project_modules") != source_modules():
        raise ReportError(
            "Lean environment project modules do not equal the project source modules"
        )
    declarations = probe.get("declarations")
    if not isinstance(declarations, list):
        raise ReportError("Lean axiom probe has no declaration list")
    names = [entry.get("declaration") for entry in declarations]
    if len(names) != len(set(names)):
        raise ReportError("Lean axiom probe contains duplicate declarations")
    if "StatQED.Internal.testOnlySmoke" not in names or "Set.ext" not in names:
        raise ReportError("Lean axiom probe omitted a required named declaration")
    if names != sorted(names):
        raise ReportError("Lean axiom probe declarations are not globally sorted")
    origins = {entry.get("origin") for entry in declarations}
    if origins != {"project", "imported_mathlib"}:
        raise ReportError(f"Lean axiom probe has unexpected origins: {sorted(origins)!r}")
    project_entries = [entry for entry in declarations if entry.get("origin") == "project"]
    imported_entries = [
        entry for entry in declarations if entry.get("origin") == "imported_mathlib"
    ]
    if [entry.get("declaration") for entry in imported_entries] != ["Set.ext"]:
        raise ReportError("Lean axiom probe imported-declaration set is incomplete or altered")
    if any(entry.get("kind") == "axiom" for entry in project_entries):
        raise ReportError("Lean axiom probe found a project axiom declaration")
    if any(entry.get("unsafe") is True for entry in project_entries):
        raise ReportError("Lean axiom probe found an unsafe project declaration")
    if not all(
        isinstance(entry.get("axioms"), list)
        and isinstance(entry.get("kind"), str)
        and isinstance(entry.get("module"), str)
        and isinstance(entry.get("type"), str)
        and isinstance(entry.get("unsafe"), bool)
        for entry in declarations
    ):
        raise ReportError("Lean axiom probe contains an incomplete declaration record")
    for entry in declarations:
        axioms = entry["axioms"]
        if axioms != sorted(set(axioms)):
            raise ReportError(
                f"axioms for {entry['declaration']} are not sorted and unique"
            )
    if any("sorryAx" in entry["axioms"] for entry in project_entries):
        raise ReportError("Lean axiom probe found sorryAx in a project declaration closure")
    for entry in project_entries:
        prohibited = PROHIBITED_IMPORTED_NATIVE_AXIOMS.intersection(entry["axioms"])
        if prohibited:
            raise ReportError(
                "Lean axiom probe found prohibited imported native-trust axioms "
                f"in project declaration {entry['declaration']!r}: {sorted(prohibited)!r}"
            )
    return probe


def tool_identity() -> tuple[str, str]:
    lean_version = run(["lean", "--version"])
    lake_version = run(["lake", "--version"])
    if "4.32.2" not in lean_version:
        raise ReportError(f"unexpected Lean version output: {lean_version!r}")
    commit_match = re.search(r"commit ([0-9a-f]{40})", lean_version)
    if commit_match is None or commit_match.group(1) != EXPECTED_LEAN_COMMIT:
        raise ReportError(f"unexpected Lean commit in version output: {lean_version!r}")
    if EXPECTED_LAKE_VERSION not in lake_version:
        raise ReportError(f"unexpected Lake version output: {lake_version!r}")
    return lean_version, lake_version


def generate() -> dict[str, Any]:
    validate_configuration()
    _manifest, mathlib = load_manifest()
    mathlib_checkout = ROOT / ".lake" / "packages" / "mathlib"
    mathlib_head = run(["git", "rev-parse", "HEAD"], cwd=mathlib_checkout)
    if mathlib_head != EXPECTED_MATHLIB_REVISION:
        raise ReportError(
            f"Mathlib checkout HEAD is {mathlib_head!r}, expected {EXPECTED_MATHLIB_REVISION!r}"
        )
    lean_version, lake_version = tool_identity()
    probe = parse_probe(run(PROBE_COMMAND))
    return {
        "command": PROBE_COMMAND,
        "declarations": probe["declarations"],
        "environment": {
            "lake_version": lake_version,
            "lean_toolchain": EXPECTED_TOOLCHAIN,
            "lean_version": lean_version,
            "manifest_sha256": file_sha256(ROOT / "lake-manifest.json"),
            "mathlib_checkout_head": mathlib_head,
            "mathlib_input_revision": mathlib["inputRev"],
            "mathlib_resolved_revision": mathlib["rev"],
        },
        "nonclaims": [
            "This report is reproducibility and logical-dependency evidence, not a normative theorem lock.",
            "It does not establish source fidelity, statistical validity, external premises, provenance truth, or artifact-byte binding.",
            "The test-only True declaration is not a public theorem or a non-vacuity witness.",
        ],
        "project_modules": probe["project_modules"],
        "provenance": {
            "classification": "Non-normative locked-environment reproducibility evidence.",
            "generator": "tools/axiom_report.py",
            "probe": "Tests/AxiomReport.lean",
            "source": "Live Lean.Environment and Lean.collectAxioms observation.",
        },
        "schema_version": 1,
        "type_representation": {
            "format": "Lean.Expr Repr output",
            "normative": False,
            "purpose": "Locked-environment diagnostic; not a canonical theorem identity.",
        },
    }


def encoded(report: dict[str, Any]) -> bytes:
    return (json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", type=Path, metavar="PATH")
    mode.add_argument("--check", type=Path, metavar="PATH")
    arguments = parser.parse_args()
    try:
        output = encoded(generate())
        if arguments.write is not None:
            arguments.write.write_bytes(output)
        elif arguments.check is not None:
            if arguments.check.read_bytes() != output:
                raise ReportError(f"axiom report differs from {arguments.check}")
        else:
            sys.stdout.buffer.write(output)
    except (OSError, ReportError, subprocess.SubprocessError) as error:
        print(f"axiom-report error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
