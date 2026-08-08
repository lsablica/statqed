#!/usr/bin/env python3
"""Fail-closed trust checks for the Experimental SQ-0003 Lean project.

The source scan is supplementary.  Declaration kinds, elaborated types, and
transitive axioms come from Lean itself through ``lean/tools/axiom_report.py``.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from typing import Any


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_TOOLCHAIN = "leanprover/lean4:v4.32.2"
ADJACENT_TOOLCHAIN = "leanprover/lean4:v4.32.1"
EXPECTED_LEAN_COMMIT = "f3b06c705e6c85f5314019d5d3baab0fec5b580c"
EXPECTED_MATHLIB_REVISION = "905b95818eb32af7874a58b427f50c1711a5e96c"
EXPECTED_LAKE_VERSION = "5.0.0-src+f3b06c7"
FULL_GIT_REVISION = re.compile(r"^[0-9a-f]{40}$")
PROHIBITED_IMPORTED_NATIVE_AXIOMS = {
    "Lean.ofReduceBool",
    "Lean.ofReduceNat",
    "Lean.trustCompiler",
}


@dataclass(frozen=True, order=True)
class Finding:
    code: str
    path: str
    message: str

    def as_json(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message, "path": self.path}


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add(findings: list[Finding], code: str, path: str, message: str) -> None:
    findings.append(Finding(code, path, message))


def load_json(path: Path, root: Path, findings: list[Finding], code: str) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        add(findings, code, relative(path, root), f"cannot read deterministic JSON: {error}")
        return None


def check_toolchain(lean_root: Path, root: Path, findings: list[Finding]) -> None:
    path = lean_root / "lean-toolchain"
    expected = (EXPECTED_TOOLCHAIN + "\n").encode()
    try:
        actual = path.read_bytes()
    except OSError as error:
        add(findings, "toolchain_mismatch", relative(path, root), f"cannot read toolchain: {error}")
        return
    if actual == expected:
        return
    selected = actual.decode("utf-8", errors="replace").strip()
    code = (
        "adjacent_toolchain_mathlib_mismatch"
        if selected == ADJACENT_TOOLCHAIN
        else "toolchain_mismatch"
    )
    add(
        findings,
        code,
        relative(path, root),
        f"expected exact LF-terminated {EXPECTED_TOOLCHAIN!r}, found {selected!r}",
    )


def check_lakefile(lean_root: Path, root: Path, findings: list[Finding]) -> None:
    path = lean_root / "lakefile.toml"
    try:
        with path.open("rb") as stream:
            config = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as error:
        add(findings, "lakefile_invalid", relative(path, root), f"cannot parse Lake TOML: {error}")
        return
    requirements = config.get("require")
    if not isinstance(requirements, list):
        add(findings, "lakefile_invalid", relative(path, root), "require must be a list")
        return
    mathlib = [entry for entry in requirements if isinstance(entry, dict) and entry.get("name") == "mathlib"]
    if len(mathlib) != 1:
        add(findings, "mathlib_config_revision_mismatch", relative(path, root), "expected exactly one Mathlib requirement")
        return
    revision = mathlib[0].get("rev")
    if not isinstance(revision, str) or FULL_GIT_REVISION.fullmatch(revision) is None:
        add(findings, "mutable_mathlib_revision", relative(path, root), f"Mathlib rev is not a full commit: {revision!r}")
    elif revision != EXPECTED_MATHLIB_REVISION:
        add(
            findings,
            "mathlib_config_revision_mismatch",
            relative(path, root),
            f"Mathlib rev {revision!r} differs from the reviewed commit",
        )
    for index, requirement in enumerate(requirements):
        if not isinstance(requirement, dict):
            add(findings, "lakefile_invalid", relative(path, root), f"require[{index}] is not a table")
            continue
        revision = requirement.get("rev")
        if not isinstance(revision, str) or FULL_GIT_REVISION.fullmatch(revision) is None:
            add(
                findings,
                "mutable_dependency_revision",
                relative(path, root),
                f"require[{index}] {requirement.get('name')!r} is not pinned to a full commit",
            )


def check_manifest(
    lean_root: Path, root: Path, findings: list[Finding]
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    path = lean_root / "lake-manifest.json"
    manifest = load_json(path, root, findings, "manifest_invalid")
    if not isinstance(manifest, dict):
        return None, []
    packages = manifest.get("packages")
    if not isinstance(packages, list):
        add(findings, "manifest_invalid", relative(path, root), "packages must be a list")
        return manifest, []
    typed_packages = [package for package in packages if isinstance(package, dict)]
    if len(typed_packages) != len(packages):
        add(findings, "manifest_invalid", relative(path, root), "every package must be an object")
    names = [package.get("name") for package in typed_packages]
    if any(not isinstance(name, str) or not name for name in names) or len(names) != len(set(names)):
        add(findings, "manifest_invalid", relative(path, root), "package names must be nonempty and unique")
    for package in typed_packages:
        revision = package.get("rev")
        if not isinstance(revision, str) or FULL_GIT_REVISION.fullmatch(revision) is None:
            add(
                findings,
                "mutable_manifest_revision",
                relative(path, root),
                f"package {package.get('name')!r} has non-immutable resolved rev {revision!r}",
            )
    mathlib = [package for package in typed_packages if package.get("name") == "mathlib"]
    if len(mathlib) != 1:
        add(findings, "manifest_revision_mismatch", relative(path, root), "expected exactly one Mathlib package")
    else:
        for field in ("rev", "inputRev"):
            if mathlib[0].get(field) != EXPECTED_MATHLIB_REVISION:
                add(
                    findings,
                    "manifest_revision_mismatch",
                    relative(path, root),
                    f"Mathlib {field} differs from {EXPECTED_MATHLIB_REVISION}",
                )
    return manifest, typed_packages


def strip_lean_comments_and_literals(text: str) -> tuple[str, list[str]]:
    """Mask comments, strings, chars, and quoted identifiers while preserving lines."""

    output: list[str] = []
    errors: list[str] = []
    index = 0
    block_depth = 0
    state = "normal"
    while index < len(text):
        char = text[index]
        pair = text[index : index + 2]
        if state == "line_comment":
            if char == "\n":
                output.append("\n")
                state = "normal"
            else:
                output.append(" ")
            index += 1
            continue
        if state == "block_comment":
            if pair == "/-":
                block_depth += 1
                output.extend("  ")
                index += 2
            elif pair == "-/":
                block_depth -= 1
                output.extend("  ")
                index += 2
                if block_depth == 0:
                    state = "normal"
            else:
                output.append("\n" if char == "\n" else " ")
                index += 1
            continue
        if state in {"string", "char"}:
            delimiter = '"' if state == "string" else "'"
            if char == "\\" and index + 1 < len(text):
                output.extend("  ")
                index += 2
            elif char == delimiter:
                output.append(" ")
                index += 1
                state = "normal"
            else:
                output.append("\n" if char == "\n" else " ")
                index += 1
            continue
        if pair == "--":
            output.extend("  ")
            index += 2
            state = "line_comment"
        elif pair == "/-":
            output.extend("  ")
            index += 2
            state = "block_comment"
            block_depth = 1
        elif char == '"':
            output.append(" ")
            index += 1
            state = "string"
        elif char in "«»":
            # Quoted identifiers are executable names, not inert literals.
            # Preserve their contents so ``«sorryAx»`` cannot bypass the scan;
            # only mask the delimiters themselves.
            output.append(" ")
            index += 1
        elif char == "'" and (
            index == 0 or not (text[index - 1].isalnum() or text[index - 1] in "_'")
        ):
            output.append(" ")
            index += 1
            state = "char"
        else:
            output.append(char)
            index += 1
    if state == "block_comment":
        errors.append("unterminated block comment")
    elif state == "string":
        errors.append("unterminated string literal")
    elif state == "char":
        errors.append("unterminated character literal")
    return "".join(output), errors


def mask_lean_name_quotations(text: str) -> str:
    """Mask inert Lean ``Name`` quotations while preserving executable names.

    Backtick forms such as `` `Lean.trustCompiler`` and `` ``sorryAx`` build
    name values for environment inspection.  Guillemets such as
    ``«sorryAx»`` are executable quoted identifiers and intentionally remain.
    """

    pattern = re.compile(r"`{1,2}[A-Za-z_][A-Za-z0-9_'.]*")
    return pattern.sub(lambda match: " " * len(match.group(0)), text)


SOURCE_RULES: tuple[tuple[str, re.Pattern[str], str], ...] = (
    ("forbidden_sorry", re.compile(r"(?<![A-Za-z0-9_'])sorry(?![A-Za-z0-9_'])"), "project source contains sorry"),
    ("forbidden_admit", re.compile(r"(?<![A-Za-z0-9_'])admit(?![A-Za-z0-9_'])"), "project source contains admit"),
    # A leading backtick is Lean name syntax (for example ``sorryAx in the
    # environment reporter), not an invocation of the axiom.  Actual term use
    # remains caught here and, authoritatively, by the live axiom closure.
    ("forbidden_sorryAx", re.compile(r"(?<![A-Za-z0-9_'`])sorryAx(?![A-Za-z0-9_'])"), "project source uses sorryAx"),
    # Commands may be preceded by attributes and declaration modifiers.  Keep
    # this line-anchored so ordinary variables named ``axioms`` in the trusted
    # environment reporter are not mistaken for declarations.
    ("project_axiom", re.compile(r"(?m)^\s*(?:(?:@\[[^\]\n]*\]|private|protected|public|scoped|noncomputable)\s+)*(?:axiom|axioms|constant|constants)\b|(?<![A-Za-z0-9_'])axiomDecl(?![A-Za-z0-9_'])"), "project source declares an axiom or bodyless constant"),
    ("unreviewed_native_trust", re.compile(r"(?<![A-Za-z0-9_'])(?:native_decide|bv_decide|trustCompiler|reduceBool|reduceNat|ofReduceBool|ofReduceNat)(?![A-Za-z0-9_'])|(?<![A-Za-z0-9_'])decide\s*\+\s*native(?![A-Za-z0-9_'])"), "project source uses an unreviewed native proof shortcut"),
    ("unreviewed_native_trust", re.compile(r"(?<![A-Za-z0-9_'])(?:unsafe|extern|implemented_by|addDeclWithoutChecking)(?![A-Za-z0-9_'])|debug\.skipKernelTC"), "project source uses an unreviewed unsafe/native declaration path"),
)


def project_sources(lean_root: Path) -> list[Path]:
    candidates = [lean_root / "StatQED.lean"]
    for directory in ("StatQED", "Examples", "Tests"):
        base = lean_root / directory
        if base.is_dir():
            candidates.extend(base.rglob("*.lean"))
    return sorted({path for path in candidates if path.is_file()})


def project_modules(lean_root: Path) -> list[str]:
    modules = ["StatQED"]
    source_root = lean_root / "StatQED"
    if source_root.is_dir():
        modules.extend(
            ".".join(path.relative_to(lean_root).with_suffix("").parts)
            for path in source_root.rglob("*.lean")
        )
    return sorted(set(modules))


def check_sources(lean_root: Path, root: Path, findings: list[Finding]) -> None:
    for path in project_sources(lean_root):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            add(findings, "source_unreadable", relative(path, root), f"cannot read UTF-8 source: {error}")
            continue
        masked, lexical_errors = strip_lean_comments_and_literals(text)
        masked = mask_lean_name_quotations(masked)
        for error in lexical_errors:
            add(findings, "source_lexical_error", relative(path, root), error)
        for code, pattern, message in SOURCE_RULES:
            if pattern.search(masked):
                add(findings, code, relative(path, root), message)


def check_axiom_report_static(lean_root: Path, root: Path, findings: list[Finding]) -> Path:
    path = lean_root / "Reports" / "axioms.json"
    if not path.is_file():
        add(findings, "missing_axiom_report", relative(path, root), "committed live axiom report is absent")
        return path
    report = load_json(path, root, findings, "axiom_report_mismatch")
    if not isinstance(report, dict):
        return path
    expected_keys = {
        "command",
        "declarations",
        "environment",
        "nonclaims",
        "project_modules",
        "provenance",
        "schema_version",
        "type_representation",
    }
    if set(report) != expected_keys or report.get("schema_version") != 1:
        add(findings, "axiom_report_mismatch", relative(path, root), "report schema or top-level fields differ")
    if report.get("command") != ["lake", "env", "lean", "--trust=0", "Tests/AxiomReport.lean"]:
        add(findings, "axiom_report_mismatch", relative(path, root), "report command is missing or altered")
    environment = report.get("environment")
    if not isinstance(environment, dict):
        add(findings, "axiom_report_mismatch", relative(path, root), "report environment is absent")
    else:
        expected_environment = {
            "lean_toolchain": EXPECTED_TOOLCHAIN,
            "mathlib_input_revision": EXPECTED_MATHLIB_REVISION,
            "mathlib_resolved_revision": EXPECTED_MATHLIB_REVISION,
            "manifest_sha256": sha256_file(lean_root / "lake-manifest.json") if (lean_root / "lake-manifest.json").is_file() else None,
        }
        for field, expected in expected_environment.items():
            if environment.get(field) != expected:
                add(findings, "axiom_report_mismatch", relative(path, root), f"report environment {field} is altered")
        if environment.get("mathlib_checkout_head") != EXPECTED_MATHLIB_REVISION:
            add(findings, "axiom_report_mismatch", relative(path, root), "report Mathlib checkout HEAD is altered")
        lean_version = environment.get("lean_version")
        lake_version = environment.get("lake_version")
        if not isinstance(lean_version, str) or EXPECTED_LEAN_COMMIT not in lean_version:
            add(findings, "axiom_report_mismatch", relative(path, root), "report Lean identity is altered")
        if not isinstance(lake_version, str) or EXPECTED_LAKE_VERSION not in lake_version:
            add(findings, "axiom_report_mismatch", relative(path, root), "report Lake identity is altered")
    if report.get("project_modules") != project_modules(lean_root):
        add(findings, "axiom_report_mismatch", relative(path, root), "report project module coverage is incomplete or altered")
    nonclaims = report.get("nonclaims")
    if not isinstance(nonclaims, list) or not nonclaims or not all(isinstance(item, str) for item in nonclaims):
        add(findings, "axiom_report_mismatch", relative(path, root), "report nonclaims are absent")
    if report.get("type_representation") != {
        "format": "Lean.Expr Repr output",
        "normative": False,
        "purpose": "Locked-environment diagnostic; not a canonical theorem identity.",
    }:
        add(
            findings,
            "axiom_report_mismatch",
            relative(path, root),
            "report type-representation scope is absent or altered",
        )
    if report.get("provenance") != {
        "classification": "Non-normative locked-environment reproducibility evidence.",
        "generator": "tools/axiom_report.py",
        "probe": "Tests/AxiomReport.lean",
        "source": "Live Lean.Environment and Lean.collectAxioms observation.",
    }:
        add(
            findings,
            "axiom_report_mismatch",
            relative(path, root),
            "report non-normative provenance is absent or altered",
        )
    declarations = report.get("declarations")
    if not isinstance(declarations, list):
        add(findings, "axiom_report_mismatch", relative(path, root), "report declaration list is absent")
        return path
    names = [entry.get("declaration") if isinstance(entry, dict) else None for entry in declarations]
    if names != sorted(names) or len(names) != len(set(names)):
        add(findings, "axiom_report_mismatch", relative(path, root), "report declarations are not sorted and unique")
    required = {"Set.ext", "StatQED.Internal.testOnlySmoke"}
    if not required <= set(names):
        add(findings, "axiom_report_mismatch", relative(path, root), "report omits a required named declaration")
    project_axiom_names: set[str] = set()
    for entry in declarations:
        if not isinstance(entry, dict):
            add(findings, "axiom_report_mismatch", relative(path, root), "declaration entry is not an object")
            continue
        if set(entry) != {"axioms", "declaration", "kind", "module", "origin", "type", "unsafe"}:
            add(findings, "axiom_report_mismatch", relative(path, root), f"declaration {entry.get('declaration')!r} fields differ")
        axioms = entry.get("axioms")
        if not isinstance(axioms, list) or not all(isinstance(item, str) for item in axioms) or axioms != sorted(set(axioms)):
            add(findings, "axiom_report_mismatch", relative(path, root), f"declaration {entry.get('declaration')!r} axioms are not sorted strings")
            axioms = []
        origin = entry.get("origin")
        if origin not in {"project", "imported_mathlib"}:
            add(findings, "axiom_report_mismatch", relative(path, root), f"declaration {entry.get('declaration')!r} origin is invalid")
        if not isinstance(entry.get("type"), str) or not entry.get("type"):
            add(findings, "axiom_report_mismatch", relative(path, root), f"declaration {entry.get('declaration')!r} type is absent")
        if not isinstance(entry.get("unsafe"), bool):
            add(findings, "axiom_report_mismatch", relative(path, root), f"declaration {entry.get('declaration')!r} unsafe flag is absent")
        if origin == "project":
            if entry.get("kind") == "axiom":
                project_axiom_names.add(str(entry.get("declaration")))
                add(findings, "project_axiom", relative(path, root), f"report contains project axiom {entry.get('declaration')}")
            if "sorryAx" in axioms:
                add(findings, "forbidden_sorryAx", relative(path, root), f"project declaration {entry.get('declaration')} depends on sorryAx")
            if entry.get("unsafe") is True:
                add(findings, "unreviewed_native_trust", relative(path, root), f"project declaration {entry.get('declaration')} is unsafe")
            native_axioms = PROHIBITED_IMPORTED_NATIVE_AXIOMS.intersection(axioms)
            if native_axioms:
                add(
                    findings,
                    "unreviewed_native_trust",
                    relative(path, root),
                    f"project declaration {entry.get('declaration')} depends on prohibited imported native-trust axioms {sorted(native_axioms)}",
                )
    for entry in declarations:
        if isinstance(entry, dict) and entry.get("origin") == "project":
            used = set(entry.get("axioms", [])) & project_axiom_names
            if used:
                add(findings, "project_axiom_dependency", relative(path, root), f"project declaration depends on project axioms {sorted(used)}")
    return path


def run_checked(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.update({"LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "TZ": "UTC"})
    return subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def check_checkout_heads(
    packages: list[dict[str, Any]], lean_root: Path, root: Path, findings: list[Finding]
) -> None:
    packages_root = lean_root / ".lake" / "packages"
    for package in sorted(packages, key=lambda item: str(item.get("name"))):
        name = package.get("name")
        revision = package.get("rev")
        checkout = packages_root / str(name)
        if not checkout.is_dir():
            add(findings, "dependency_checkout_missing", relative(checkout, root), f"locked package {name!r} is not resolved")
            continue
        completed = run_checked(["git", "rev-parse", "HEAD"], checkout)
        head = completed.stdout.strip()
        if completed.returncode != 0 or head != revision:
            add(findings, "dependency_checkout_mismatch", relative(checkout, root), f"checkout HEAD {head!r} differs from manifest rev {revision!r}")
            continue
        status = run_checked(
            ["git", "status", "--porcelain", "--untracked-files=no"], checkout
        )
        if status.returncode != 0 or status.stdout.strip():
            add(
                findings,
                "dependency_checkout_dirty",
                relative(checkout, root),
                "locked package has tracked worktree or index modifications",
            )


def check_axiom_report_live(lean_root: Path, root: Path, report: Path, findings: list[Finding]) -> None:
    generator = lean_root / "tools" / "axiom_report.py"
    if not generator.is_file():
        add(findings, "axiom_report_live_failure", relative(generator, root), "live axiom-report generator is absent")
        return
    completed = run_checked(
        [sys.executable, str(generator), "--check", str(report)], lean_root
    )
    if completed.returncode != 0:
        detail = (completed.stderr.strip() or completed.stdout.strip()).replace(str(root), "<root>")
        code = "axiom_report_mismatch" if "differs from" in detail else "axiom_report_live_failure"
        add(findings, code, relative(report, root), detail)


def audit(root: Path, *, live: bool) -> list[Finding]:
    findings: list[Finding] = []
    lean_root = root / "lean"
    if not lean_root.is_dir():
        add(findings, "lean_project_missing", "lean", "Lean project directory is absent")
        return findings
    check_toolchain(lean_root, root, findings)
    check_lakefile(lean_root, root, findings)
    _manifest, packages = check_manifest(lean_root, root, findings)
    check_sources(lean_root, root, findings)
    report = check_axiom_report_static(lean_root, root, findings)
    if live and not findings:
        check_checkout_heads(packages, lean_root, root, findings)
        if not findings:
            check_axiom_report_live(lean_root, root, report, findings)
    return sorted(set(findings))


def apply_json_pointer(payload: Any, pointer: str, value: Any) -> None:
    parts = [part.replace("~1", "/").replace("~0", "~") for part in pointer.split("/")[1:]]
    current = payload
    for part in parts[:-1]:
        current = current[int(part)] if isinstance(current, list) else current[part]
    final = parts[-1]
    if isinstance(current, list):
        current[int(final)] = value
    else:
        current[final] = value


def mutate(case: dict[str, Any], source_lean: Path, target_lean: Path, fixture_root: Path) -> None:
    target = target_lean / case["target"]
    operation = case["mutation"]
    if operation == "replace_file":
        fixture = fixture_root / case["fixture"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(fixture, target)
    elif operation == "remove_file":
        target.unlink(missing_ok=True)
    elif operation == "replace_text":
        text = target.read_text(encoding="utf-8")
        search = case["search"]
        if text.count(search) != 1:
            raise ValueError(f"{case['id']}: expected one occurrence of {search!r}")
        target.write_text(text.replace(search, case["replacement"]), encoding="utf-8")
    elif operation == "replace_json_value":
        payload = json.loads(target.read_text(encoding="utf-8"))
        apply_json_pointer(payload, case["json_pointer"], case["replacement"])
        target.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    else:
        raise ValueError(f"{case['id']}: unsupported mutation {operation!r}")


def run_mutations(root: Path) -> tuple[list[dict[str, Any]], list[Finding]]:
    baseline = audit(root, live=True)
    if baseline:
        return [], baseline
    lean_root = root / "lean"
    fixture_root = lean_root / "Tests" / "Trust"
    expectations_path = fixture_root / "expectations.json"
    try:
        expectations = json.loads(expectations_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [], [Finding("mutation_fixture_invalid", relative(expectations_path, root), str(error))]
    if expectations.get("schema_version") != 1:
        return [], [Finding("mutation_fixture_invalid", relative(expectations_path, root), "schema_version must be 1")]
    cases = expectations.get("cases", []) + expectations.get("positive_controls", [])
    ids = [case.get("id") for case in cases]
    if any(not isinstance(case, dict) for case in cases) or len(ids) != len(set(ids)):
        return [], [Finding("mutation_fixture_invalid", relative(expectations_path, root), "case IDs must be unique")]
    results: list[dict[str, Any]] = []
    for case in cases:
        with tempfile.TemporaryDirectory(prefix="statqed-sq0003-mutation-") as directory:
            temp_root = Path(directory)
            temp_lean = temp_root / "lean"
            shutil.copytree(lean_root, temp_lean, ignore=shutil.ignore_patterns(".lake"))
            try:
                mutate(case, lean_root, temp_lean, fixture_root)
                observed = audit(temp_root, live=False)
                positive_build_exit: int | None = None
                if case["expected_code"] == "ok" and not observed:
                    temp_lake = temp_lean / ".lake"
                    temp_lake.mkdir()
                    temp_lake.joinpath("packages").symlink_to(
                        lean_root / ".lake" / "packages", target_is_directory=True
                    )
                    positive_build = run_checked(["lake", "build"], temp_lean)
                    positive_build_exit = positive_build.returncode
                    if positive_build.returncode != 0:
                        observed.append(
                            Finding(
                                "positive_control_build_failure",
                                f"lean/Tests/Trust/expectations.json#{case['id']}",
                                "static positive control did not compile in the locked environment",
                            )
                        )
                codes = sorted({finding.code for finding in observed})
                expected_code = case["expected_code"]
                expected_exit = case["expected_exit"]
                actual_exit = 1 if observed else 0
                passed = actual_exit == expected_exit and (
                    (expected_code == "ok" and not observed) or expected_code in codes
                )
                results.append({
                    **(
                        {"build_exit": positive_build_exit}
                        if positive_build_exit is not None
                        else {}
                    ),
                    "expected_code": expected_code,
                    "expected_exit": expected_exit,
                    "id": case["id"],
                    "observed_codes": codes,
                    "observed_exit": actual_exit,
                    "status": "pass" if passed else "fail",
                })
            except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
                results.append({
                    "expected_code": case.get("expected_code"),
                    "expected_exit": case.get("expected_exit"),
                    "id": case.get("id"),
                    "message": str(error),
                    "observed_codes": ["mutation_runner_error"],
                    "observed_exit": None,
                    "status": "fail",
                })
    for case in expectations.get("live_report_cases", []):
        with tempfile.TemporaryDirectory(
            prefix="statqed-sq0003-live-report-mutation-"
        ) as directory:
            temp_root = Path(directory)
            temp_lean = temp_root / "lean"
            shutil.copytree(
                lean_root, temp_lean, ignore=shutil.ignore_patterns(".lake")
            )
            try:
                mutate(case, lean_root, temp_lean, fixture_root)
                temp_lake = temp_lean / ".lake"
                temp_lake.mkdir()
                temp_lake.joinpath("packages").symlink_to(
                    lean_root / ".lake" / "packages", target_is_directory=True
                )
                build = run_checked(["lake", "build"], temp_lean)
                report_path = temp_lean / "Reports" / "mutated-axioms.json"
                report = run_checked(
                    [
                        sys.executable,
                        str(temp_lean / "tools" / "axiom_report.py"),
                        "--write",
                        str(report_path),
                    ],
                    temp_lean,
                )
                report_output = report.stdout + report.stderr
                expected_text = case["expected_output_substring"]
                passed = (
                    build.returncode == case["expected_build_exit"]
                    and report.returncode == case["expected_exit"]
                    and expected_text in report_output
                )
                results.append({
                    "build_exit": build.returncode,
                    "expected_code": case["expected_code"],
                    "expected_exit": case["expected_exit"],
                    "id": case["id"],
                    "observed_codes": [
                        "build_succeeded"
                        if build.returncode == 0
                        else "build_failed",
                        "expected_diagnostic"
                        if expected_text in report_output
                        else "missing_diagnostic",
                    ],
                    "observed_exit": report.returncode,
                    "status": "pass" if passed else "fail",
                })
            except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
                results.append({
                    "expected_code": case.get("expected_code"),
                    "expected_exit": case.get("expected_exit"),
                    "id": case.get("id"),
                    "message": str(error),
                    "observed_codes": ["mutation_runner_error"],
                    "observed_exit": None,
                    "status": "fail",
                })
    for regression in expectations.get("security_regressions", []):
        fixture = fixture_root / regression["fixture"]
        with tempfile.TemporaryDirectory(prefix="statqed-sq0003-kernel-regression-") as directory:
            bug = Path(directory) / "Bug.lean"
            shutil.copyfile(fixture, bug)
            command = list(regression["command"])
            command[-1] = str(bug)
            completed = run_checked(command, lean_root)
            combined = completed.stdout + completed.stderr
            expected_text = regression["expected_stdout_substring"]
            passed = completed.returncode == regression["expected_exit"] and expected_text in combined
            observed_stream = (
                "stdout"
                if expected_text in completed.stdout
                else "stderr"
                if expected_text in completed.stderr
                else "absent"
            )
            results.append({
                "expected_code": expected_text,
                "expected_exit": regression["expected_exit"],
                "id": regression["id"],
                "observed_codes": [f"exit_{completed.returncode}", "expected_diagnostic" if expected_text in combined else "missing_diagnostic"],
                "observed_exit": completed.returncode,
                "observed_stream": observed_stream,
                "status": "pass" if passed else "fail",
            })
    failures = [result for result in results if result["status"] != "pass"]
    findings = [
        Finding("mutation_case_failed", f"lean/Tests/Trust/expectations.json#{result['id']}", json.dumps(result, sort_keys=True))
        for result in failures
    ]
    return results, findings


def render_human(findings: list[Finding], mutation_results: list[dict[str, Any]] | None) -> None:
    if findings:
        print("Lean trust checks failed:")
        for finding in findings:
            print(f"  [{finding.code}] {finding.path}: {finding.message}")
        return
    print("Lean trust checks passed:")
    print(f"  toolchain: {EXPECTED_TOOLCHAIN}")
    print(f"  Mathlib: {EXPECTED_MATHLIB_REVISION}")
    print("  project source: no prohibited trusted-path constructs")
    print("  axiom report: live environment regeneration matched")
    if mutation_results is not None:
        print(f"  mutations: {len(mutation_results)} intended differentials passed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit deterministic machine-readable output")
    parser.add_argument("--run-mutations", action="store_true", help="run isolated mutation and kernel-regression fixtures")
    parser.add_argument(
        "--write-json",
        type=Path,
        metavar="PATH",
        help="write the same deterministic JSON payload to a retained evidence path",
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help=argparse.SUPPRESS)
    arguments = parser.parse_args()
    root = arguments.root.resolve()
    mutation_results: list[dict[str, Any]] | None = None
    if arguments.run_mutations:
        mutation_results, findings = run_mutations(root)
    else:
        findings = audit(root, live=True)
    payload: dict[str, Any] = {
        "findings": [finding.as_json() for finding in findings],
        "schema_version": 1,
        "status": "fail" if findings else "pass",
    }
    if mutation_results is not None:
        payload["mutations"] = mutation_results
    encoded_payload = json.dumps(
        payload, indent=2, sort_keys=True, ensure_ascii=False
    ) + "\n"
    if arguments.write_json is not None:
        arguments.write_json.write_text(encoded_payload, encoding="utf-8")
    if arguments.json:
        print(encoded_payload, end="")
    else:
        render_human(findings, mutation_results)
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
