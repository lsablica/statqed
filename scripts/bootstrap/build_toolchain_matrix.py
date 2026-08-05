#!/usr/bin/env python3
"""Assemble the reviewed SQ-0002 evidence fragments into matrix.json.

This standard-library-only builder is intentionally separate from the probe
runner.  It normalizes specialist fragments, retains failed attempts, binds
logs and prototype subjects by SHA-256, and supplies manager-owned support/CI
recommendations.  It never touches production toolchain paths.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PROTOTYPES = ROOT / "docs/research/toolchain-prototypes"
LOG_PREFIX = "docs/research/toolchain-prototypes/logs"
RERUN_DISPATCHERS = {
    "lean-recommended-cache-success": (["/usr/bin/bash", "verify-probe.sh", "recommended"], "docs/research/toolchain-prototypes/lean-mathlib"),
    "lean-no-cache-success": (["/usr/bin/bash", "verify-probe.sh", "no-binary-cache"], "docs/research/toolchain-prototypes/lean-mathlib"),
    "rust-dev-prototype": (["/usr/bin/bash", "verify-probe.sh", "development"], "docs/research/toolchain-prototypes/rust"),
    "rust-msrv-prototype": (["/usr/bin/bash", "verify-probe.sh", "msrv"], "docs/research/toolchain-prototypes/rust"),
    "python-development-3-14-7": (["/usr/bin/bash", "verify-probe.sh", "development"], "docs/research/toolchain-prototypes/python"),
    "python-floor-3-11-15-owned": (["/usr/bin/bash", "verify-probe.sh", "floor"], "docs/research/toolchain-prototypes/python"),
    "r-development-4.6.1-package-native": (["/usr/bin/bash", "verify-probe.sh", "development"], "docs/research/toolchain-prototypes/r"),
    "r-floor-4.4.3-package-native": (["/usr/bin/bash", "verify-probe.sh", "floor"], "docs/research/toolchain-prototypes/r"),
    "development-julia-1-12-6-linux-x86-64-20260803t124500z": (["/usr/bin/bash", "verify-probe.sh", "development"], "docs/research/toolchain-prototypes/julia"),
    "floor-lts-julia-1-10-11-linux-x86-64-20260803t124500z": (["/usr/bin/bash", "verify-probe.sh", "floor"], "docs/research/toolchain-prototypes/julia"),
    "arrow-pyarrow25-arrow-rs59-cross-lineage-hardened": (["/usr/bin/bash", "verify-probe.sh"], "docs/research/toolchain-prototypes/arrow"),
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def extra_source(source_id: str, title: str, url: str, authority: str) -> dict[str, str]:
    return {"id": source_id, "title": title, "url": url, "retrieved_at": "2026-08-03T15:10:00+02:00", "authority": authority, "license": "See linked primary source and package/repository metadata", "maintenance_security": "Point-in-time primary-source record; re-query before update.", "notes": "Added during manager integration to retain the specialist's exact source identity rather than aliasing it to a non-equivalent source."}


EXTRA_SOURCES = [
    extra_source("python-build-standalone-20260718", "python-build-standalone 20260718 release", "https://github.com/astral-sh/python-build-standalone/releases/tag/20260718", "Astral python-build-standalone official release"),
    extra_source("uv-release-0.11.32", "uv 0.11.32 release", "https://github.com/astral-sh/uv/releases/tag/0.11.32", "Astral uv official release"),
    extra_source("official-lean-elan-reference", "Elan reference", "https://github.com/leanprover/elan", "Lean project repository"),
    extra_source("official-lean-releases", "Lean releases", "https://github.com/leanprover/lean4/releases", "Lean project release index"),
    extra_source("official-mathlib-releases", "Mathlib releases", "https://github.com/leanprover-community/mathlib4/releases", "Mathlib project release index"),
    extra_source("official-lake-reference", "Lake reference", "https://lean-lang.org/doc/reference/latest/Build-Tools-and-Distribution/Lake/", "Lean official reference"),
    extra_source("official-mathlib-dependency-guide", "Mathlib project dependency guide", "https://leanprover-community.github.io/install/project.html", "Mathlib project documentation"),
    extra_source("official-elan-release-api", "Elan latest release API", "https://api.github.com/repos/leanprover/elan/releases/latest", "Elan official GitHub release API"),
    extra_source("official-mathlib-cache-guide", "Mathlib cache documentation", "https://leanprover-community.github.io/mathlib4_docs/Mathlib.html", "Mathlib project documentation"),
    extra_source("official-mathlib-pmf-docs", "Mathlib probability mass function documentation", "https://leanprover-community.github.io/mathlib4_docs/Mathlib/Probability/ProbabilityMassFunction/Constructions.html", "Mathlib generated documentation"),
    extra_source("official-lean-4.32.1", "Lean v4.32.1", "https://github.com/leanprover/lean4/releases/tag/v4.32.1", "Lean project release"),
    extra_source("official-mathlib-v4.32.1", "Mathlib v4.32.1", "https://github.com/leanprover-community/mathlib4/releases/tag/v4.32.1", "Mathlib project release"),
    extra_source("immutable-mathlib-lean-toolchain", "Mathlib 520045ab lean-toolchain", "https://github.com/leanprover-community/mathlib4/blob/520045ab14e26149ee970e2e617ca04b09bde5d6/lean-toolchain", "Immutable Mathlib repository blob"),
    extra_source("immutable-mathlib-lakefile", "Mathlib 520045ab lakefile", "https://github.com/leanprover-community/mathlib4/blob/520045ab14e26149ee970e2e617ca04b09bde5d6/lakefile.toml", "Immutable Mathlib repository blob"),
    extra_source("rust-release-1.85.0-edition-2024", "Rust 1.85.0 release", "https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/", "Rust project release announcement"),
    extra_source("cargo-resolver3", "Cargo resolver version 3", "https://doc.rust-lang.org/cargo/reference/resolver.html#resolver-versions", "Cargo official reference"),
    extra_source("cargo-rust-version", "Cargo rust-version field", "https://doc.rust-lang.org/cargo/reference/rust-version.html", "Cargo official reference"),
    extra_source("rust-lint-unsafe-code", "rustc unsafe_code lint", "https://doc.rust-lang.org/rustc/lints/listing/allowed-by-default.html#unsafe-code", "rustc official reference"),
    extra_source("rustfmt-component", "rustup component management", "https://rust-lang.github.io/rustup/concepts/components.html", "rustup official documentation"),
    extra_source("rustup-profiles", "rustup profiles", "https://rust-lang.github.io/rustup/concepts/profiles.html", "rustup official documentation"),
    extra_source("crates-io-metadata-2026-08-03", "Rust prototype package records", "https://crates.io/", "crates.io package registry"),
    extra_source("crates-io-sha2-0.11.0", "sha2 0.11.0", "https://crates.io/crates/sha2/0.11.0", "crates.io canonical package record"),
    extra_source("crates-io-zip-8.1.0", "zip 8.1.0", "https://crates.io/crates/zip/8.1.0", "crates.io canonical package record"),
    extra_source("rustsec-db-d91a8fc9492378f23cba86b81770c6d16de6ebba", "RustSec advisory database snapshot d91a8fc", "https://github.com/RustSec/advisory-db/tree/d91a8fc9492378f23cba86b81770c6d16de6ebba", "Immutable RustSec advisory database tree"),
]


def source_refs(raw: list[str], component: str, source_ids: set[str]) -> list[str]:
    if not raw:
        raise ValueError(f"{component}: missing source references")
    missing = set(raw) - source_ids
    if missing:
        raise ValueError(f"{component}: unknown source references {sorted(missing)}")
    return list(dict.fromkeys(raw))


def locks(raw: Any) -> list[dict[str, str]]:
    if isinstance(raw, list):
        return [
            {"kind": str(item.get("kind", "record")), "value": str(item.get("value", ""))}
            for item in raw
            if isinstance(item, dict) and item.get("value") not in (None, "")
        ]
    if isinstance(raw, dict):
        return [
            {"kind": str(kind), "value": json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else str(value)}
            for kind, value in raw.items()
            if value not in (None, "", [])
        ]
    return []


def platform(raw: Any) -> dict[str, str]:
    raw = raw if isinstance(raw, dict) else {}
    os_value = str(raw.get("os", "Ubuntu"))
    version = str(raw.get("version", raw.get("kernel", "24.04.4 LTS")))
    architecture = str(raw.get("architecture", "x86_64"))
    environment = raw.get("environment")
    if not environment:
        extras = {k: v for k, v in raw.items() if k not in {"os", "version", "architecture"}}
        environment = json.dumps(extras, sort_keys=True) if extras else "direct host"
    return {"os": os_value, "version": version, "architecture": architecture, "environment": str(environment)}


def normalize(raw: dict[str, Any], source_ids: set[str], *, id_suffix: str = "") -> dict[str, Any]:
    probe_id = str(raw["id"]) + id_suffix
    classification = str(raw.get("classification", "unknown"))
    status = raw.get("exit_status")
    if isinstance(status, list):
        nonzero = next((int(value) for value in status if int(value) != 0), None)
        status = nonzero if nonzero is not None else 0
    mapping = {
        "compatible": "success",
        "expected_rejection": "failure",
        "candidate_failure": "failure",
        "mutation_failure": "failure",
        "unavailable": "unknown",
    }
    classification = mapping.get(classification, classification)
    if classification not in {"success", "failure", "unknown"}:
        raise ValueError(f"{probe_id}: unsupported classification {classification!r}")
    if classification == "success" and status != 0:
        raise ValueError(f"{probe_id}: success has exit status {status!r}")
    if classification == "failure" and (not isinstance(status, int) or status == 0):
        raise ValueError(f"{probe_id}: failure has exit status {status!r}")
    if classification == "unknown" and status == 0:
        raise ValueError(f"{probe_id}: unknown has successful exit status 0")
    disposition_raw = str(raw.get("disposition", "unresolved"))
    disposition = "recommended" if disposition_raw.startswith("recommended") and classification == "success" else (
        "unresolved" if disposition_raw in {"unresolved", "later-validation", "probe_failed"} or classification == "unknown" else "rejected"
    )
    commands = raw.get("commands")
    if not isinstance(commands, list) or not commands:
        raise ValueError(f"{probe_id}: missing command sequence")
    if not raw.get("stdout_path") or not raw.get("stderr_path"):
        raise ValueError(f"{probe_id}: missing retained stdout/stderr path")
    stdout = str(raw["stdout_path"])
    stderr = str(raw["stderr_path"])
    stdout_path = ROOT / stdout
    stderr_path = ROOT / stderr
    rerun_raw = raw.get("rerun") if isinstance(raw.get("rerun"), dict) else {}
    runnable = bool(rerun_raw.get("runnable", rerun_raw.get("locally_runnable", False)))
    cwd = str(rerun_raw.get("cwd", ""))
    command = rerun_raw.get("command")
    # Only component-owned dispatchers are executable through the top-level runner.
    dispatcher = RERUN_DISPATCHERS.get(probe_id) if disposition == "recommended" else None
    if dispatcher:
        command, cwd = dispatcher
        runnable = True
    else:
        runnable = False
    normalized_locks = locks(raw.get("dependency_locks"))
    if disposition == "recommended" and not normalized_locks:
        raise ValueError(f"{probe_id}: recommended evidence has no immutable dependency lock")
    return {
        "id": probe_id,
        "component": str(raw.get("component", "unknown")),
        "candidate": str(raw.get("candidate", "unknown")),
        "platform": platform(raw.get("platform")),
        "commands": commands,
        "environment_variables": {str(k): str(v) for k, v in (raw.get("environment_variables") or {}).items()},
        "dependency_locks": normalized_locks,
        "started_at": str(raw.get("started_at", raw.get("start_time", raw.get("start")))),
        "ended_at": str(raw.get("ended_at", raw.get("end_time", raw.get("end")))),
        "exit_status": status,
        "stdout_path": stdout,
        "stdout_sha256": digest(stdout_path),
        "stderr_path": stderr,
        "stderr_sha256": digest(stderr_path),
        "classification": classification,
        "reason": str(raw.get("reason", "No reason recorded.")),
        "source_refs": source_refs(list(raw.get("source_refs") or []), str(raw.get("component", "")), source_ids),
        "disposition": disposition,
        "version_output": str(raw.get("version_output", "not available")),
        "rerun": {
            "runnable": runnable,
            **({"command": command, "cwd": cwd} if runnable else {"unavailable_reason": str(rerun_raw.get("unavailable_reason", "archived evidence; use the component README for full fresh preparation"))}),
        },
    }


def python_attempts() -> list[dict[str, Any]]:
    old_logs = PROTOTYPES / "logs/python/run-20260803"
    current_logs = PROTOTYPES / "logs/python/run-20260805"
    common_locks = [
        {"kind": "requirements_lock_sha256", "value": "0fcf65ff2348ef6356caad22169b7b907f6899069749b70660ef76e7ba7730b3"},
        {"kind": "uv_0.11.32_binary_sha256", "value": "da15297d6879b2cfbe5ea3cb03725c1613d51ba72892cc996468d871f0a532fb"},
    ]

    def owned(
        mode: str,
        probe_id: str,
        candidate: str,
        archive_sha256: str,
        version_output: str,
        refs: list[str],
    ) -> dict[str, Any]:
        record = load(current_logs / f"python-{mode}-owned-verify.command.json")
        return {
            "id": probe_id,
            "component": "Python packaging",
            "candidate": candidate,
            "platform": {
                "os": "Ubuntu",
                "version": "24.04.4 LTS; Linux 7.0.0-28-generic",
                "architecture": "x86_64",
                "environment": "fresh extracted python-build-standalone runtime; fresh HOME/XDG/uv/pip caches and venvs; hash-locked offline wheelhouse; C.UTF-8",
            },
            "commands": [record["command"]],
            "environment_variables": record["environment"],
            "dependency_locks": common_locks
            + [{"kind": "runtime_archive_sha256", "value": archive_sha256}],
            "start": record["started_at"],
            "end": record["ended_at"],
            "exit_status": record["exit_status"],
            "stdout_path": rel(current_logs / f"python-{mode}-owned-verify.stdout.log"),
            "stderr_path": rel(current_logs / f"python-{mode}-owned-verify.stderr.log"),
            "classification": "success",
            "disposition": "recommended",
            "reason": "The owned dispatcher rechecked runtime, uv, and lock digests; built sdist and wheel with the package-native PEP 517 path; installed in a separate venv; ran pip check and pytest; and removed all extracted runtime, build, log, and cache state on exit.",
            "version_output": version_output,
            "source_refs": refs + ["python-supported-versions", "python-packaging-flow", "uv-release-0.11.32"],
            "rerun": {"runnable": True},
        }

    def old(
        probe_id: str,
        candidate: str,
        names: list[str],
        classification: str,
        reason: str,
        version_output: str,
        refs: list[str],
        locks_extra: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        records = [load(old_logs / f"{name}.command.json") for name in names]
        composite = old_logs / f"{probe_id.removeprefix('python-')}.stdout"
        return {
            "id": probe_id,
            "component": "Python packaging",
            "candidate": candidate,
            "platform": {
                "os": "Ubuntu",
                "version": "24.04.4 LTS; Linux 7.0.0-28-generic",
                "architecture": "x86_64",
                "environment": "historical python-build-standalone/uv attempt on C.UTF-8",
            },
            "commands": [item["command"] for item in records],
            "environment_variables": records[-1]["environment_variables"],
            "dependency_locks": common_locks + (locks_extra or []),
            "start": records[0]["started_at"],
            "end": records[-1]["ended_at"],
            "exit_status": records[-1]["exit_status"],
            "stdout_path": rel(composite if composite.is_file() else old_logs / f"{names[-1]}.stdout"),
            "stderr_path": rel((old_logs / f"{probe_id.removeprefix('python-')}.stderr") if (old_logs / f"{probe_id.removeprefix('python-')}.stderr").is_file() else old_logs / f"{names[-1]}.stderr"),
            "classification": classification,
            "disposition": "rejected",
            "reason": reason,
            "version_output": version_output,
            "source_refs": refs,
            "rerun": {"runnable": False, "unavailable_reason": "Historical attempt retained; use the owned current dispatcher for fresh validation."},
        }

    success_steps = lambda prefix: [
        f"{prefix}-python-version",
        f"{prefix}-build",
        f"{prefix}-wheel-install",
        f"{prefix}-pip-check-installed",
        f"{prefix}-pytest",
        f"{prefix}-metadata",
        f"{prefix}-artifact-digests",
    ]
    old_refs = ["python-release-v3.14.6", "python-supported-versions", "python-packaging-flow", "python-build-standalone-20260718", "uv-release-0.11.32"]
    floor_refs = ["python-release-v3.11.15", "python-supported-versions", "python-packaging-flow", "python-build-standalone-20260718", "uv-release-0.11.32"]
    return [
        owned(
            "development",
            "python-development-3-14-7",
            "CPython 3.14.7; python-build-standalone tag 20260805 target 76b41240bc8dfe753a54b2e32c8941e536568be8",
            "a3a4e4b81b138960c7c546694df8a77578c0b6aa46d47e96f49b9e10e8f860c9",
            "Python 3.14.7; pip 26.2; build 1.5.0; Hatchling 1.31.0; pytest 9.1.1; 2 passed",
            ["python-release-v3.14.7", "python-build-standalone-20260805"],
        ),
        owned(
            "floor",
            "python-floor-3-11-15-owned",
            "CPython 3.11.15; declared project support floor Python >=3.11; python-build-standalone 20260718",
            "23ccae6f1ff73e8aa8378436f869da003b8eb7d6c95f2bc706f494115ba1447d",
            "Python 3.11.15; pip 26.2; build 1.5.0; Hatchling 1.31.0; pytest 9.1.1; 2 passed",
            ["python-release-v3.11.15", "python-build-standalone-20260718"],
        ),
        old(
            "python-development-3-14-6-historical",
            "CPython 3.14.6 historical development candidate",
            success_steps("development-3-14-6"),
            "success",
            "The exact package-native sequence passed, but Python 3.14.7 superseded this patch on 2026-08-05; retained as successful historical evidence and rejected as the final development pin.",
            "Python 3.14.6; pip 26.2; build 1.5.0; Hatchling 1.31.0; pytest 9.1.1",
            old_refs,
            [{"kind": "runtime_archive_sha256", "value": "86bf107f65fc30b56f2b263b26797fcbb1661f5315910cdbf27f733eb8738b74"}],
        ),
        old(
            "python-floor-3-11-15-historical",
            "CPython 3.11.15 original floor run",
            success_steps("floor-3-11-15"),
            "success",
            "The original floor run passed and is retained, but the final recommendation is bound to the later owned dispatcher evidence.",
            "Python 3.11.15; pip 26.2; build 1.5.0; Hatchling 1.31.0; pytest 9.1.1",
            floor_refs,
            [{"kind": "runtime_archive_sha256", "value": "23ccae6f1ff73e8aa8378436f869da003b8eb7d6c95f2bc706f494115ba1447d"}],
        ),
        old(
            "python-rejected-3-10-20-metadata-rejection",
            "CPython 3.10.20 against Requires-Python >=3.11",
            ["rejected-3-10-20-python-version", "rejected-3-10-20-metadata-rejection"],
            "failure",
            "pip rejected the wheel because 3.10.20 is outside Requires-Python >=3.11.",
            "Python 3.10.20; requires a different Python",
            ["python-supported-versions", "python-packaging-flow", "uv-release-0.11.32"],
        ),
        old("python-floor-cold-seed-network-failure", "CPython 3.11.15 cold uv seeded venv", ["floor-3-11-15-builder-venv-sandbox-network-failure"], "failure", "Cold uv seed required absent packages and failed DNS; ordinary cache state was insufficient.", "uv 0.11.32; DNS resolution failure", floor_refs),
        old("python-development-pep517-network-failure", "CPython 3.14.6 PEP 517 build without wheelhouse", ["development-3-14-6-build-sandbox-network-failure"], "failure", "PEP 517 isolation attempted to resolve Hatchling and failed without DNS.", "Python 3.14.6; no Hatchling distribution found offline", old_refs),
        old("python-development-uv-seed-cache-failure", "CPython 3.14.6 uv seed from ordinary cache", ["development-3-14-6-builder-venv-uv-seed-cache-failure"], "failure", "uv seed cache was interpreter-specific and still attempted a network fetch.", "uv 0.11.32; DNS resolution failure", old_refs),
        old("python-rejected-pip-cache-network-failure", "CPython 3.10.20 ordinary pip cache", ["rejected-3-10-20-pin-pip-sandbox-network-failure"], "failure", "Pinning pip from an ordinary cache still attempted mutable index metadata retrieval.", "Python 3.10.20; DNS resolution failure", ["python-packaging-flow", "uv-release-0.11.32"]),
    ]


def manager_attempts() -> list[dict[str, Any]]:
    cbor_logs = PROTOTYPES / "logs/cbor-cddl"
    cbor_record = load(cbor_logs / "cbor2-6.1.4-security-regressions.command.json")
    arrow_logs = PROTOTYPES / "logs/arrow"
    arrow_record = load(
        arrow_logs / "arrow-pyarrow25-arrow-rs59-cross-lineage-hardened.command.json"
    )
    attempts: list[dict[str, Any]] = [
        {
            "id": "arrow-pyarrow25-arrow-rs59-cross-lineage-hardened",
            "component": "Apache Arrow interoperability candidates",
            "candidate": "PyArrow/Arrow C++ 25.0.0 and arrow-rs 59.1.0 on CPython 3.14.7/Rust 1.97.1",
            "platform": {
                "os": "Ubuntu",
                "version": "24.04.4 LTS; Linux 7.0.0-28-generic",
                "architecture": "x86_64",
                "environment": "fresh extracted CPython runtime and Python environment; exact prepared PyArrow wheel; fresh Cargo target with hash-bound offline task cache; C.UTF-8",
            },
            "commands": [arrow_record["command"]],
            "environment_variables": arrow_record["environment"],
            "dependency_locks": [
                {"kind": "python_runtime_archive_sha256", "value": "a3a4e4b81b138960c7c546694df8a77578c0b6aa46d47e96f49b9e10e8f860c9"},
                {"kind": "pyarrow_wheel_sha256", "value": "447df764beb07c544f0178a5f6b70ef44b9ecf382b3cdfad4c2d7867353c3887"},
                {"kind": "python_requirements_lock_sha256", "value": "bfd009e1da9d19fc65296c52f9d94b7666f468ce146f2437de435984a59439f3"},
                {"kind": "cargo_lock_sha256", "value": "b48ca90c270c065266d625e8d26a024217ac1559247d530de6b9348969bedaed"},
                {"kind": "uv_binary_sha256", "value": "da15297d6879b2cfbe5ea3cb03725c1613d51ba72892cc996468d871f0a532fb"},
            ],
            "start": arrow_record["started_at"],
            "end": arrow_record["ended_at"],
            "exit_status": arrow_record["exit_status"],
            "stdout_path": rel(
                arrow_logs
                / "arrow-pyarrow25-arrow-rs59-cross-lineage-hardened.stdout.log"
            ),
            "stderr_path": rel(
                arrow_logs
                / "arrow-pyarrow25-arrow-rs59-cross-lineage-hardened.stderr.log"
            ),
            "classification": "success",
            "disposition": "recommended-experimental-candidate",
            "reason": "The exact current Python and Rust candidates passed self-round-trips, complete schema/value/null cross-reads in both directions, same-schema altered-value rejection with the expected differential, repeat-write observation, and malformed magic-only rejection. This recommends only further experimental evaluation; it does not define logical identity, canonical bytes, or RFC-0006 semantics.",
            "version_output": "Python 3.14.7; PyArrow/Arrow C++ 25.0.0; rustc/Cargo 1.97.1; arrow-rs 59.1.0",
            "source_refs": [
                "python-release-v3.14.7",
                "python-build-standalone-20260805",
                "arrow-release-25.0.0",
                "pyarrow-25.0.0",
                "arrow-rs-readme-policy",
                "arrow-format-versioning",
                "arrow-format-security",
            ],
            "rerun": {"runnable": True},
        },
        {
            "id": "cbor2-6.1.4-security-regressions",
            "component": "cbor2",
            "candidate": "cbor2 6.1.4 on CPython 3.14.7",
            "platform": {
                "os": "Ubuntu",
                "version": "24.04.4 LTS; Linux 7.0.0-28-generic",
                "architecture": "x86_64",
                "environment": "fresh extracted runtime, HOME, XDG, uv cache, venv, and wheelhouse; C.UTF-8; PYTHONHASHSEED=0",
            },
            "commands": [cbor_record["command"]],
            "environment_variables": cbor_record["environment"],
            "dependency_locks": [
                {"kind": "python_runtime_archive_sha256", "value": "a3a4e4b81b138960c7c546694df8a77578c0b6aa46d47e96f49b9e10e8f860c9"},
                {"kind": "cbor2_wheel_sha256", "value": "c0f5f2d6d3b58e44146860c049f3c082207a4005588b8926d51bf937ab66773c"},
                {"kind": "requirements_lock_sha256", "value": "547717250bbd70c0857bedfd3a0ab7ddf8f78e86f1b0c523b5dc6ed510de7667"},
                {"kind": "uv_binary_sha256", "value": "da15297d6879b2cfbe5ea3cb03725c1613d51ba72892cc996468d871f0a532fb"},
            ],
            "start": cbor_record["started_at"],
            "end": cbor_record["ended_at"],
            "exit_status": cbor_record["exit_status"],
            "stdout_path": rel(cbor_logs / "cbor2-6.1.4-security-regressions.stdout.log"),
            "stderr_path": rel(cbor_logs / "cbor2-6.1.4-security-regressions.stderr.log"),
            "classification": "success",
            "disposition": "unresolved",
            "reason": "The exact current wheel rejected an incomplete indefinite map and a non-byte bignum, produced distinct hashes for the tested adversarial frozendict pairing, and round-tripped bytearray string references. This is narrow release-regression evidence, not a decoder-profile or canonical-byte decision.",
            "version_output": "Python 3.14.7; cbor2 6.1.4; four release-regression controls passed",
            "source_refs": ["python-release-v3.14.7", "python-build-standalone-20260805", "python-cbor2-6.1.4", "python-cbor2-api-6.1.3", "rfc8949-cbor"],
            "rerun": {"runnable": False, "unavailable_reason": "Current candidate is non-normative; run verify-cbor2-6.1.4.sh directly after exact asset preparation."},
        }
    ]
    security_logs = PROTOTYPES / "logs/security/run-20260805"
    security_specs = [
        (
            "pypi",
            "PyPI",
            "12 exact packages from the Python prototype lock",
            ["python-packaging-flow", "osv-querybatch-api"],
            "0fcf65ff2348ef6356caad22169b7b907f6899069749b70660ef76e7ba7730b3",
        ),
        (
            "cran",
            "CRAN",
            "29 distinct exact package/version pairs from the R development and floor inventories",
            ["r-release-4.6.1", "r-release-4.4.3", "cran-testthat-3.3.2", "cran-testthat-3.2.3", "osv-querybatch-api"],
            digest(PROTOTYPES / "r/development-cran-source-lock.tsv"),
        ),
    ]
    for slug, ecosystem, candidate, refs, source_lock_sha in security_specs:
        record = load(security_logs / f"{slug}-osv.command.json")
        response = security_logs / f"{slug}-osv.response.json"
        request = security_logs / f"{slug}-osv.request.json"
        attempts.append(
            {
                "id": f"{slug}-osv-exact-lock-query",
                "component": f"{ecosystem} dependency advisory observation",
                "candidate": candidate,
                "platform": {
                    "os": "Ubuntu",
                    "version": "24.04.4 LTS; Linux 7.0.0-28-generic",
                    "architecture": "x86_64",
                    "environment": "Python 3.12 standard-library HTTPS client; live official OSV API; response retained",
                },
                "commands": [record["command"]],
                "environment_variables": {"LANG": "C.UTF-8", "LC_ALL": "C.UTF-8"},
                "dependency_locks": [
                    {"kind": "source_lock_sha256", "value": source_lock_sha},
                    {"kind": "osv_request_sha256", "value": digest(request)},
                    {"kind": "osv_response_sha256", "value": digest(response)},
                ],
                "start": record["started_at"],
                "end": record["ended_at"],
                "exit_status": record["exit_status"],
                "stdout_path": rel(security_logs / f"{slug}-osv.stdout.log"),
                "stderr_path": rel(security_logs / f"{slug}-osv.stderr.log"),
                "classification": "success",
                "disposition": "unresolved",
                "reason": f"The official OSV batch API returned one aligned, unpaginated result per exact {ecosystem} query and zero vulnerability records at the recorded 2026-08-05 query time. This covers only the selected prototype package lock and is not a security guarantee.",
                "version_output": f"OSV querybatch; {record['package_count']} exact {ecosystem} package versions; zero returned vulnerability records",
                "source_refs": refs,
                "rerun": {"runnable": False, "unavailable_reason": "Live advisory state is mutable; query_osv.py --verify performs a fresh, non-retaining check."},
            }
        )
    return attempts


def main() -> None:
    sources = load(PROTOTYPES / "sources/sources.json") + EXTRA_SOURCES
    source_id_list = [item["id"] for item in sources]
    if len(source_id_list) != len(set(source_id_list)):
        duplicates = sorted(
            source_id
            for source_id in set(source_id_list)
            if source_id_list.count(source_id) > 1
        )
        raise ValueError(f"duplicate source identifiers: {duplicates}")
    source_ids = {item["id"] for item in sources}
    probes: list[dict[str, Any]] = []
    for fragment_path in sorted(PROTOTYPES.glob("*/probe-fragment.json")):
        data = load(fragment_path)
        for raw in data.get("probes", data.get("attempts", [])):
            probes.append(normalize(raw, source_ids))
    for run_path in sorted((PROTOTYPES / "logs/julia").glob("run-*/attempts-generated.json")):
        suffix = "-" + run_path.parent.name.removeprefix("run-").lower()
        for raw in load(run_path):
            probes.append(normalize(raw, source_ids, id_suffix=suffix))
    for raw in python_attempts():
        probes.append(normalize(raw, source_ids))
    for raw in manager_attempts():
        probes.append(normalize(raw, source_ids))
    probes.sort(key=lambda item: item["id"])

    recommendations = [
        {"id":"lean-mathlib","component":"Lean/Mathlib/Lake","role":"initial normative proof backend research pin","development_pin":"Lean 4.32.2 commit f3b06c705e6c85f5314019d5d3baab0fec5b580c; Mathlib commit 905b95818eb32af7874a58b427f50c1711a5e96c; bundled Lake 5.0.0-src+f3b06c7","support_floor":"No version range: support only the exact Mathlib-selected Lean pair","update_policy":"Re-query both official releases, resolve immutable commits, rerun cached and no-cache builds, mismatch/manifest controls, and axiom inspection","rollback_policy":"Restore the prior exact Lean/Mathlib commits and reviewed manifests; never mix adjacent release names","evidence_probe_ids":["lean-recommended-cache-success","lean-no-cache-success"],"ci_matrix":["lean-linux-exact","lean-linux-no-cache","lean-macos-planned","lean-windows-planned"]},
        {"id":"rust-cargo","component":"Rust/Cargo","role":"reference operational backend research pin","development_pin":"Rust 1.97.1; rustc build commit 8bab26f4f68e0e26f0bb7960be334d5b520ea452; Cargo build commit c980f4866141969fab6254a680546a277789d6f0","support_floor":"Compatibility-only Rust 1.85.1 MSRV (rustc 4eb161250e340c8f48f66e2b929ef4a5bed7c181; Cargo d73d2caf9e41a39daf2a8d6ce60ec80bf354d2a7); fetch with current patched Cargo, then isolated uncredentialed crates.io-only offline 1.85 checks","update_policy":"Advance only after development and MSRV share the exact lock and fmt, clippy -D warnings, tests, unsafe rejection, license inventory, and advisory checks pass; do not use Cargo <1.96 with credentials or third-party registries","rollback_policy":"Restore the prior reviewed toolchain and Cargo.lock; retain Cargo CVE-2026-5222/CVE-2026-5223 mitigations","evidence_probe_ids":["rust-install-dev","rust-dev-prototype","rust-install-msrv","rust-msrv-prototype","rustsec-audit"],"ci_matrix":["rust-linux-dev","rust-linux-msrv","rust-linux-arm64-planned","rust-macos-planned","rust-windows-planned"]},
        {"id":"python","component":"Python","role":"thin frontend development/support research pin","development_pin":"CPython 3.14.7; python-build-standalone 20260805 target commit 76b41240bc8dfe753a54b2e32c8941e536568be8; runtime archive sha256 a3a4e4b81b138960c7c546694df8a77578c0b6aa46d47e96f49b9e10e8f860c9","support_floor":"Python >=3.11; exact floor patch tested: CPython 3.11.15 source commit 2340a037f7450e70fccfe411e6531afb4d57a312","update_policy":"Test every supported minor in CI; refresh security patches, managed-runtime provenance, and the universal hash lock before upgrade","rollback_policy":"Restore the prior reviewed interpreter archive digest and universal hash lock; never fall back to the superseded 3.14.6 pin silently","evidence_probe_ids":["python-development-3-14-7","python-floor-3-11-15-owned"],"ci_matrix":["python-linux-314","python-linux-311","python-linux-312-planned","python-linux-313-planned","python-macos-planned","python-windows-planned"]},
        {"id":"r","component":"R","role":"thin frontend development/support research pin","development_pin":"R 4.6.1 with testthat 3.3.2","support_floor":"DESCRIPTION R >=4.4.0; exact floor patch tested: R 4.4.3 with testthat 3.2.3","update_policy":"Review floor each feature release and rerun built-tarball checks on every claimed platform","rollback_policy":"Restore the previous exact R runtime and explicit test dependency inventory","evidence_probe_ids":["r-development-4.6.1-package-native","r-floor-4.4.3-package-native"],"ci_matrix":["r-linux-dev","r-linux-floor","r-macos-planned","r-windows-planned"]},
        {"id":"julia","component":"Julia/Pkg","role":"thin frontend development/LTS research pin","development_pin":"Julia 1.12.6 official Linux x86-64 archive sha256 bbabf3bef19421a9dbd24a767d807606ab85e444323b5a1c73ffe293fa3d079a","support_floor":"Julia LTS 1.10.11 archive sha256 fb49c6b174600cd2051e37ba3f7330f8acf06dd00bce609bab6611387fdb37bf","update_policy":"Follow maintained Stable/LTS lines and rerun fresh-depot offline package-native probes","rollback_policy":"Restore prior official archive digest, compat entry, and generated manifest","evidence_probe_ids":["development-julia-1-12-6-linux-x86-64-20260803t124500z","floor-lts-julia-1-10-11-linux-x86-64-20260803t124500z"],"ci_matrix":["julia-linux-stable","julia-linux-lts","julia-macos-planned","julia-windows-planned"]},
    ]
    # Interoperability recommendations are added only when their exact final
    # specialist fragment names successful recommended evidence.
    successful_recommended = {p["id"] for p in probes if p["classification"] == "success" and p["disposition"] == "recommended"}
    def first_ids(words: tuple[str, ...]) -> list[str]:
        return [p["id"] for p in probes if p["id"] in successful_recommended and any(word in (p["id"]+p["component"]).lower() for word in words)]
    arrow_ids = first_ids(("arrow", "pyarrow"))
    cbor_ids = first_ids(("cbor", "ciborium", "minicbor"))
    cddl_ids = first_ids(("cddl",))
    if arrow_ids:
        recommendations.append({"id":"arrow-candidates","component":"Apache Arrow libraries","role":"experimental interoperability candidates only","development_pin":"Apache Arrow 25.0.0 format release; PyArrow 25.0.0 and arrow-rs 59.1.0 candidates","support_floor":"None selected; experimental candidate, not logical-data identity","update_policy":"Refresh implementation matrix/security pages and cross-read probes before later RFC work","rollback_policy":"Remove candidate libraries; no production or normative dependency exists","evidence_probe_ids":arrow_ids,"ci_matrix":["arrow-linux-candidates"]})
    if cbor_ids:
        recommendations.append({"id":"cbor-candidates","component":"CBOR libraries","role":"experimental encoding/conformance candidates only","development_pin":"cbor2 6.1.3, ciborium 0.2.2, minicbor 2.3.0","support_floor":"None selected; strict validation and RFC-0001 remain unresolved","update_policy":"Repeat discriminating malformed/duplicate/indefinite/depth probes before RFC selection","rollback_policy":"Remove candidates; no canonical bytes are frozen","evidence_probe_ids":cbor_ids,"ci_matrix":["cbor-linux-candidates"]})
    if cddl_ids:
        recommendations.append({"id":"cddl-candidate","component":"CDDL tooling","role":"experimental schema-validation candidate only","development_pin":"Rust cddl 0.10.6 candidate","support_floor":"No floor; incompatible with proposed Rust 1.85.1 MSRV unless isolated as a tool","update_policy":"Re-evaluate dependency graph/MSRV and RFC 8610/9682 coverage before adoption","rollback_policy":"Remove the tool candidate; schema semantics remain Draft","evidence_probe_ids":cddl_ids,"ci_matrix":["cddl-linux-candidate"]})

    ci_matrix = [
        {"id":"lean-linux-exact","component":"Lean/Mathlib/Lake","version":"4.32.2/905b95818eb32af7874a58b427f50c1711a5e96c","os":"Ubuntu 24.04.4","architecture":"x86_64","status":"direct_success","evidence_probe_ids":["lean-recommended-cache-success"]},
        {"id":"lean-linux-no-cache","component":"Lean/Mathlib/Lake","version":"4.32.2/905b95818eb32af7874a58b427f50c1711a5e96c no-cache","os":"Ubuntu 24.04.4","architecture":"x86_64","status":"direct_success","evidence_probe_ids":["lean-no-cache-success"]},
        {"id":"lean-macos-planned","component":"Lean/Mathlib/Lake","version":"exact pair","os":"macOS","architecture":"arm64","status":"planned_validation","evidence_probe_ids":[]},
        {"id":"lean-windows-planned","component":"Lean/Mathlib/Lake","version":"exact pair","os":"Windows","architecture":"x86_64","status":"planned_validation","evidence_probe_ids":[]},
        {"id":"rust-linux-dev","component":"Rust/Cargo","version":"1.97.1","os":"Ubuntu 24.04.4","architecture":"x86_64","status":"direct_success","evidence_probe_ids":["rust-dev-prototype"]},
        {"id":"rust-linux-msrv","component":"Rust/Cargo","version":"1.85.1","os":"Ubuntu 24.04.4","architecture":"x86_64","status":"direct_success","evidence_probe_ids":["rust-msrv-prototype"]},
        {"id":"rust-linux-arm64-planned","component":"Rust/Cargo","version":"1.97.1/1.85.1","os":"Ubuntu","architecture":"arm64","status":"planned_validation","evidence_probe_ids":[]},
        {"id":"rust-macos-planned","component":"Rust/Cargo","version":"1.97.1/1.85.1","os":"macOS","architecture":"arm64","status":"planned_validation","evidence_probe_ids":[]},
        {"id":"rust-windows-planned","component":"Rust/Cargo","version":"1.97.1/1.85.1","os":"Windows","architecture":"x86_64","status":"planned_validation","evidence_probe_ids":[]},
        {"id":"python-linux-314","component":"Python","version":"3.14.7","os":"Ubuntu 24.04.4","architecture":"x86_64","status":"direct_success","evidence_probe_ids":["python-development-3-14-7"]},
        {"id":"python-linux-311","component":"Python","version":"3.11.15","os":"Ubuntu 24.04.4","architecture":"x86_64","status":"direct_success","evidence_probe_ids":["python-floor-3-11-15-owned"]},
        {"id":"python-linux-312-planned","component":"Python","version":"3.12.13","os":"Ubuntu","architecture":"x86_64","status":"planned_validation","evidence_probe_ids":[]},
        {"id":"python-linux-313-planned","component":"Python","version":"3.13.15","os":"Ubuntu","architecture":"x86_64","status":"planned_validation","evidence_probe_ids":[]},
        {"id":"python-macos-planned","component":"Python","version":"3.11-3.14","os":"macOS","architecture":"arm64","status":"planned_validation","evidence_probe_ids":[]},
        {"id":"python-windows-planned","component":"Python","version":"3.11-3.14","os":"Windows","architecture":"x86_64","status":"planned_validation","evidence_probe_ids":[]},
        {"id":"r-linux-dev","component":"R","version":"4.6.1","os":"Ubuntu 24.04.4","architecture":"x86_64","status":"direct_success","evidence_probe_ids":["r-development-4.6.1-package-native"]},
        {"id":"r-linux-floor","component":"R","version":"4.4.3","os":"Ubuntu 24.04.4","architecture":"x86_64","status":"direct_success","evidence_probe_ids":["r-floor-4.4.3-package-native"]},
        {"id":"r-macos-planned","component":"R","version":"4.6.1","os":"macOS","architecture":"unknown until runner selection","status":"planned_validation","evidence_probe_ids":[]},
        {"id":"r-windows-planned","component":"R","version":"4.6.1","os":"Windows","architecture":"x86_64","status":"planned_validation","evidence_probe_ids":[]},
        {"id":"julia-linux-stable","component":"Julia/Pkg","version":"1.12.6","os":"Ubuntu 24.04.4","architecture":"x86_64","status":"direct_success","evidence_probe_ids":["development-julia-1-12-6-linux-x86-64-20260803t124500z"]},
        {"id":"julia-linux-lts","component":"Julia/Pkg","version":"1.10.11","os":"Ubuntu 24.04.4","architecture":"x86_64","status":"direct_success","evidence_probe_ids":["floor-lts-julia-1-10-11-linux-x86-64-20260803t124500z"]},
        {"id":"julia-macos-planned","component":"Julia/Pkg","version":"Stable/LTS","os":"macOS","architecture":"arm64","status":"planned_validation","evidence_probe_ids":[]},
        {"id":"julia-windows-planned","component":"Julia/Pkg","version":"Stable/LTS","os":"Windows","architecture":"x86_64","status":"planned_validation","evidence_probe_ids":[]},
    ]
    if arrow_ids:
        ci_matrix.append({"id":"arrow-linux-candidates","component":"Apache Arrow libraries","version":"25.0.0/59.1.0","os":"Ubuntu 24.04.4","architecture":"x86_64","status":"direct_success","evidence_probe_ids":arrow_ids})
    if cbor_ids:
        ci_matrix.append({"id":"cbor-linux-candidates","component":"CBOR libraries","version":"6.1.3/0.2.2/2.3.0","os":"Ubuntu 24.04.4","architecture":"x86_64","status":"direct_success","evidence_probe_ids":cbor_ids})
    if cddl_ids:
        ci_matrix.append({"id":"cddl-linux-candidate","component":"CDDL tooling","version":"0.10.6","os":"Ubuntu 24.04.4","architecture":"x86_64","status":"direct_success","evidence_probe_ids":cddl_ids})

    subject_paths = sorted(set(
        path for directory in ("lean-mathlib", "rust", "python", "r", "julia", "arrow", "cbor-cddl")
        for path in (PROTOTYPES / directory).rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    ) | {
        path
        for path in (PROTOTYPES / "logs/security").rglob("*")
        if path.is_file()
    } | {
        PROTOTYPES / "logs/r/run-20260803/floor-package-lock.stdout",
    })
    subjects = [{"path": rel(path), "sha256": digest(path)} for path in subject_paths]
    summary = {"recommendations": recommendations, "ci_matrix": ci_matrix}
    generated_at = max(
        dt.datetime.fromisoformat(probe["ended_at"].replace("Z", "+00:00"))
        for probe in probes
    ).astimezone(dt.timezone.utc).isoformat(timespec="seconds")
    matrix = {
        "schema_version": 1,
        "task_id": "SQ-0002",
        "generated_at": generated_at,
        "retrieval_date": "2026-08-05",
        "host": {"os":"Ubuntu","version":"24.04.4 LTS","kernel":"Linux 7.0.0-28-generic","architecture":"x86_64"},
        "sources": sources,
        "prototype_subjects": subjects,
        "probes": probes,
        "recommendations": recommendations,
        "ci_matrix": ci_matrix,
        "report_summary": summary,
    }
    (PROTOTYPES / "matrix.json").write_text(json.dumps(matrix, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path = ROOT / "docs/implementation/toolchain-compatibility.md"
    if report_path.is_file():
        report = report_path.read_text(encoding="utf-8")
        begin = "<!-- SQ0002_REPORT_SUMMARY_BEGIN -->"
        end = "<!-- SQ0002_REPORT_SUMMARY_END -->"
        if report.count(begin) != 1 or report.count(end) != 1:
            raise ValueError("report must contain one SQ-0002 summary placeholder")
        summary_text = json.dumps(summary, indent=2, sort_keys=True)
        report = report.split(begin, 1)[0] + begin + "\n" + summary_text + "\n" + end + report.split(end, 1)[1]
        attempts_begin = "<!-- SQ0002_ATTEMPTS_BEGIN -->"
        attempts_end = "<!-- SQ0002_ATTEMPTS_END -->"
        if report.count(attempts_begin) != 1 or report.count(attempts_end) != 1:
            raise ValueError("report must contain one SQ-0002 attempt-table placeholder")
        rows = ["| Probe | Class | Disposition | Result and retained evidence |", "|---|---|---|---|"]
        for probe in probes:
            reason = probe["reason"].replace("|", "\\|").replace("\n", " ")
            rows.append(f"| `{probe['id']}` | {probe['classification']} | {probe['disposition']} | {reason} Logs: `{probe['stdout_path']}`, `{probe['stderr_path']}`. |")
        report = report.split(attempts_begin, 1)[0] + attempts_begin + "\n" + "\n".join(rows) + "\n" + attempts_end + report.split(attempts_end, 1)[1]
        matrix_sha = digest(PROTOTYPES / "matrix.json")
        import re
        report, count = re.subn(r"Matrix SHA-256: `(?:sha256:[0-9a-f]{64}|PENDING)`", f"Matrix SHA-256: `sha256:{matrix_sha}`", report)
        if count != 1:
            raise ValueError("report must contain one matrix SHA placeholder")
        report_path.write_text(report, encoding="utf-8")
    print(f"wrote {len(probes)} probes, {len(recommendations)} recommendations, {len(subjects)} subjects")


if __name__ == "__main__":
    main()
