#!/usr/bin/env python3
"""Generate and verify a deterministic live axiom report for every StatQED module."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
from typing import Any, Callable


LEAN_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = LEAN_ROOT.parent
BEGIN = "STATQED_PROJECT_AXIOM_REPORT_BEGIN"
END = "STATQED_PROJECT_AXIOM_REPORT_END"
SCHEMA = "statqed.project-axiom-report.v1"
OBSERVATION_SCHEMA = "statqed.project-axiom-observation.v1"
MODULE_SEGMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_']*$")
PROHIBITED_NATIVE_AXIOMS = {
    "Lean.ofReduceBool",
    "Lean.ofReduceNat",
    "Lean.trustCompiler",
}
MAX_PROJECT_MODULES = 512


class ProjectTrustError(RuntimeError):
    """A fail-closed project-module or axiom observation error."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def run(
    command: list[str],
    *,
    cwd: Path,
    timeout: int = 300,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.update({"LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "TZ": "UTC"})
    try:
        return runner(
            command,
            cwd=cwd,
            env=environment,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        raise ProjectTrustError(
            f"command exceeded {timeout}s: {' '.join(command)}"
        ) from error


def _tracked_lean_paths(repository_root: Path, lean_root: Path) -> dict[Path, str]:
    completed = run(
        [
            "git",
            "ls-files",
            "--stage",
            "-z",
            "--",
            "lean/StatQED.lean",
            "lean/StatQED",
        ],
        cwd=repository_root,
    )
    if completed.returncode != 0:
        raise ProjectTrustError(
            "cannot enumerate tracked StatQED modules: "
            + (completed.stderr.strip() or completed.stdout.strip())
        )
    tracked: dict[Path, str] = {}
    for raw in completed.stdout.split("\0"):
        if not raw:
            continue
        try:
            metadata, name = raw.split("\t", 1)
            mode, _object_id, stage = metadata.split(" ", 2)
        except ValueError as error:
            raise ProjectTrustError(f"malformed git index record: {raw!r}") from error
        path = repository_root / name
        try:
            relative = path.relative_to(lean_root)
        except ValueError as error:
            raise ProjectTrustError(f"tracked module escapes lean root: {name}") from error
        if stage != "0":
            raise ProjectTrustError(f"tracked module has unresolved index stage {stage}: {name}")
        if mode not in {"100644", "100755"}:
            raise ProjectTrustError(f"tracked module is not a regular file ({mode}): {name}")
        if relative.suffix == ".lean":
            tracked[relative] = mode
    return tracked


def _filesystem_lean_paths(lean_root: Path) -> set[Path]:
    paths: set[Path] = set()
    candidates = [lean_root / "StatQED.lean"]
    source_root = lean_root / "StatQED"
    if source_root.exists() or source_root.is_symlink():
        for directory, directory_names, file_names in os.walk(
            source_root, topdown=True, followlinks=False
        ):
            current = Path(directory)
            for name in sorted(directory_names):
                item = current / name
                mode = item.lstat().st_mode
                if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
                    raise ProjectTrustError(
                        f"module tree contains a symlink or special directory: {item.relative_to(lean_root)}"
                    )
            for name in sorted(file_names):
                item = current / name
                mode = item.lstat().st_mode
                if name.endswith(".lean"):
                    if not stat.S_ISREG(mode):
                        raise ProjectTrustError(
                            f"module source is not a regular file: {item.relative_to(lean_root)}"
                        )
                    paths.add(item.relative_to(lean_root))
    for candidate in candidates:
        try:
            mode = candidate.lstat().st_mode
        except FileNotFoundError as error:
            raise ProjectTrustError(
                f"required project module is missing: {candidate.relative_to(lean_root)}"
            ) from error
        if not stat.S_ISREG(mode):
            raise ProjectTrustError(
                f"project module is not a regular file: {candidate.relative_to(lean_root)}"
            )
        paths.add(candidate.relative_to(lean_root))
    return paths


def path_to_module(path: Path) -> str:
    if path.suffix != ".lean":
        raise ProjectTrustError(f"module path does not end in .lean: {path}")
    parts = path.with_suffix("").parts
    if not parts or any(MODULE_SEGMENT.fullmatch(part) is None for part in parts):
        raise ProjectTrustError(f"module path has an unsupported Lean name: {path}")
    return ".".join(parts)


def source_modules(
    repository_root: Path = REPOSITORY_ROOT, lean_root: Path = LEAN_ROOT
) -> list[str]:
    tracked = _tracked_lean_paths(repository_root, lean_root)
    filesystem = _filesystem_lean_paths(lean_root)
    tracked_paths = set(tracked)
    if tracked_paths != filesystem:
        missing = sorted(path.as_posix() for path in tracked_paths - filesystem)
        extra = sorted(path.as_posix() for path in filesystem - tracked_paths)
        raise ProjectTrustError(
            f"tracked/filesystem module mismatch; missing={missing!r}; untracked={extra!r}"
        )
    modules = sorted(path_to_module(path) for path in tracked_paths)
    if len(modules) != len(set(modules)):
        raise ProjectTrustError("duplicate Lean module names derive from tracked sources")
    if len(modules) > MAX_PROJECT_MODULES:
        raise ProjectTrustError(
            f"tracked project module count {len(modules)} exceeds limit {MAX_PROJECT_MODULES}"
        )
    return modules


def wrapper_source(modules: list[str], probe: str) -> str:
    if not modules or modules != sorted(set(modules)):
        raise ProjectTrustError("wrapper modules must be nonempty, sorted, and unique")
    return "\n".join(
        [
            *(f"import {name}" for name in modules),
            "",
            probe,
            "",
            "#statqed_project_axiom_report",
            "",
        ]
    )


def parse_observation(stdout: str, modules: list[str]) -> dict[str, Any]:
    lines = stdout.splitlines()
    if lines.count(BEGIN) != 1 or lines.count(END) != 1:
        raise ProjectTrustError("project axiom probe did not emit one sentinel pair")
    begin = lines.index(BEGIN)
    end = lines.index(END)
    if end != begin + 2:
        raise ProjectTrustError("project axiom probe emitted unexpected sentinel content")
    try:
        observation = json.loads(lines[begin + 1])
    except json.JSONDecodeError as error:
        raise ProjectTrustError(f"project axiom probe emitted invalid JSON: {error}") from error
    if observation.get("schema_version") != OBSERVATION_SCHEMA:
        raise ProjectTrustError("project axiom observation schema is unsupported")
    if observation.get("project_modules") != modules:
        raise ProjectTrustError(
            "imported project-module set does not equal tracked source-module set"
        )
    declarations = observation.get("declarations")
    if not isinstance(declarations, list):
        raise ProjectTrustError("project axiom observation has no declarations")
    names = [entry.get("declaration") for entry in declarations if isinstance(entry, dict)]
    if len(names) != len(declarations) or names != sorted(set(names)):
        raise ProjectTrustError("project declarations are not globally sorted and unique")
    module_set = set(modules)
    project_axioms: set[str] = set()
    for entry in declarations:
        if set(entry) != {"axioms", "declaration", "kind", "module", "type", "unsafe"}:
            raise ProjectTrustError(f"declaration record fields differ: {entry!r}")
        if entry["module"] not in module_set:
            raise ProjectTrustError(f"declaration has an untracked module: {entry!r}")
        axioms = entry["axioms"]
        if not isinstance(axioms, list) or axioms != sorted(set(axioms)):
            raise ProjectTrustError(f"declaration axioms are not sorted and unique: {entry!r}")
        if not isinstance(entry["type"], str) or not entry["type"]:
            raise ProjectTrustError(f"declaration type is missing: {entry!r}")
        if not isinstance(entry["unsafe"], bool):
            raise ProjectTrustError(f"declaration unsafe status is missing: {entry!r}")
        if entry["kind"] == "axiom":
            project_axioms.add(entry["declaration"])
            raise ProjectTrustError(f"project axiom declaration observed: {entry['declaration']}")
        if entry["unsafe"]:
            raise ProjectTrustError(f"unsafe project declaration observed: {entry['declaration']}")
        if "sorryAx" in axioms:
            raise ProjectTrustError(f"project declaration depends on sorryAx: {entry['declaration']}")
        prohibited = PROHIBITED_NATIVE_AXIOMS.intersection(axioms)
        if prohibited:
            raise ProjectTrustError(
                f"project declaration depends on prohibited native-trust axioms: {entry['declaration']} {sorted(prohibited)!r}"
            )
    for entry in declarations:
        inherited = project_axioms.intersection(entry["axioms"])
        if inherited:
            raise ProjectTrustError(
                f"project declaration depends on project axioms: {entry['declaration']} {sorted(inherited)!r}"
            )
    return observation


def generate(
    repository_root: Path = REPOSITORY_ROOT,
    lean_root: Path = LEAN_ROOT,
    *,
    omitted_modules: frozenset[str] = frozenset(),
) -> dict[str, Any]:
    modules = source_modules(repository_root, lean_root)
    wrapper_modules = [module for module in modules if module not in omitted_modules]
    if wrapper_modules != modules:
        raise ProjectTrustError(
            "generated wrapper module set differs from tracked source-module set"
        )
    probe = (lean_root / "Tests" / "ProjectAxiomProbe.lean").read_text(
        encoding="utf-8"
    )
    source = wrapper_source(wrapper_modules, probe)
    # Keep the ephemeral wrapper outside the protected source tree.  This lets
    # evidence and path-integrity gates run concurrently without observing a
    # transient project-owned source file.
    with tempfile.TemporaryDirectory(prefix="statqed-project-axiom-") as directory:
        wrapper = Path(directory) / "ProjectAxiomReport.lean"
        # The reusable probe is test infrastructure and therefore is not in
        # the production library's `.olean` search path.  Inline its exact
        # source after the generated imports while still binding its hash.
        wrapper.write_text(source, encoding="utf-8")
        command = ["lake", "env", "lean", "--trust=0", str(wrapper)]
        completed = run(command, cwd=lean_root)
        if completed.returncode != 0:
            detail = completed.stderr.strip() or completed.stdout.strip()
            detail = detail.replace(str(wrapper), "<generated-import-all-wrapper>")
            detail = detail.replace(str(Path(directory)), "<temporary-directory>")
            detail = detail.replace(str(repository_root), "<repository>")
            raise ProjectTrustError(
                f"project axiom wrapper failed with exit {completed.returncode}: {detail}"
            )
        observation = parse_observation(completed.stdout, modules)
    return {
        "command": ["lake", "env", "lean", "--trust=0", "<generated-import-all-wrapper>"],
        "declarations": observation["declarations"],
        "module_count": len(modules),
        "modules": modules,
        "nonclaims": [
            "This is a live pinned-environment observation, not a historical SQ-0003 report rewrite.",
            "It is not theorem identity, source fidelity, statistical validity, authorization, or artifact verification.",
        ],
        "probe_sha256": hashlib.sha256(
            (lean_root / "Tests" / "ProjectAxiomProbe.lean").read_bytes()
        ).hexdigest(),
        "schema_version": SCHEMA,
        "wrapper_sha256": sha256_bytes(wrapper_source(modules, probe).encode("utf-8")),
    }


def encoded(report: dict[str, Any]) -> bytes:
    return (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="require two byte-identical live observations")
    parser.add_argument("--write", type=Path, metavar="PATH", help="write deterministic live output")
    arguments = parser.parse_args()
    try:
        first = encoded(generate())
        if arguments.verify:
            second = encoded(generate())
            if first != second:
                raise ProjectTrustError("two clean live axiom observations differ")
        if arguments.write is not None:
            arguments.write.write_bytes(first)
        else:
            sys.stdout.buffer.write(first)
    except (OSError, ProjectTrustError, subprocess.SubprocessError) as error:
        print(f"project-axiom-report error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
