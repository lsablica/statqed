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
    "rust-dev-prototype": (["bash", "run-probes.sh", "development"], "docs/research/toolchain-prototypes/rust"),
    "rust-msrv-prototype": (["bash", "run-probes.sh", "msrv"], "docs/research/toolchain-prototypes/rust"),
    "r-development-4.6.1-package-native": (["bash", "run-probes.sh", "development"], "docs/research/toolchain-prototypes/r"),
    "r-floor-4.4.3-package-native": (["bash", "run-probes.sh", "floor"], "docs/research/toolchain-prototypes/r"),
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
    extra_source("rust-release-1.85.1", "Rust 1.85.1 release tag", "https://github.com/rust-lang/rust/releases/tag/1.85.1", "Rust project release"),
    extra_source("cargo-resolver3", "Cargo resolver version 3", "https://doc.rust-lang.org/cargo/reference/resolver.html#resolver-versions", "Cargo official reference"),
    extra_source("cargo-rust-version", "Cargo rust-version field", "https://doc.rust-lang.org/cargo/reference/rust-version.html", "Cargo official reference"),
    extra_source("rust-lint-unsafe-code", "rustc unsafe_code lint", "https://doc.rust-lang.org/rustc/lints/listing/allowed-by-default.html#unsafe-code", "rustc official reference"),
    extra_source("rustfmt-component", "rustup component management", "https://rust-lang.github.io/rustup/concepts/components.html", "rustup official documentation"),
    extra_source("rustup-profiles", "rustup profiles", "https://rust-lang.github.io/rustup/concepts/profiles.html", "rustup official documentation"),
    extra_source("arrow-rs-readme-policy", "arrow-rs crate 59.1.0", "https://crates.io/crates/arrow/59.1.0", "crates.io canonical package record"),
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
    log_root = PROTOTYPES / "logs/python/run-20260803"
    common_locks = [
        {"kind": "requirements_lock_sha256", "value": "0fcf65ff2348ef6356caad22169b7b907f6899069749b70660ef76e7ba7730b3"},
        {"kind": "uv_0.11.32_binary_sha256", "value": "da15297d6879b2cfbe5ea3cb03725c1613d51ba72892cc996468d871f0a532fb"},
    ]
    def record(name: str) -> dict[str, Any]:
        return load(log_root / f"{name}.command.json")
    def raw_probe(probe_id: str, candidate: str, names: list[str], classification: str, disposition: str, reason: str, version_output: str, locks_extra: list[dict[str, str]]) -> dict[str, Any]:
        records = [record(name) for name in names]
        return {
            "id": probe_id,
            "component": "Python packaging",
            "candidate": candidate,
            "platform": {"os": "Ubuntu", "version": "24.04.4 LTS; Linux 7.0.0-28-generic", "architecture": "x86_64", "environment": "uv 0.11.32 managed python-build-standalone runtime; isolated venv and hash-locked wheelhouse"},
            "commands": [item["command"] for item in records],
            "environment_variables": records[-1]["environment_variables"],
            "dependency_locks": common_locks + locks_extra,
            "start": records[0]["started_at"], "end": records[-1]["ended_at"],
            "exit_status": records[-1]["exit_status"],
            "stdout_path": f"{LOG_PREFIX}/python/run-20260803/{probe_id.replace('python-', '')}.stdout" if (log_root / f"{probe_id.replace('python-', '')}.stdout").is_file() else rel(log_root / f"{names[-1]}.stdout"),
            "stderr_path": f"{LOG_PREFIX}/python/run-20260803/{probe_id.replace('python-', '')}.stderr" if (log_root / f"{probe_id.replace('python-', '')}.stderr").is_file() else rel(log_root / f"{names[-1]}.stderr"),
            "classification": classification, "disposition": disposition, "reason": reason,
            "version_output": version_output,
            "source_refs": ["python-release-v3.14.6", "python-supported-versions", "python-packaging-flow", "python-build-standalone-20260718", "uv-release-0.11.32"],
            "rerun": {"runnable": disposition == "recommended"},
        }
    success_steps = lambda prefix: [f"{prefix}-python-version", f"{prefix}-build", f"{prefix}-wheel-install", f"{prefix}-pip-check-installed", f"{prefix}-pytest", f"{prefix}-metadata", f"{prefix}-artifact-digests"]
    return [
        raw_probe("python-development-3-14-6", "CPython 3.14.6; upstream tag c63aec69bd59c55314c06c23f4c22c03de76fe45; python-build-standalone 20260718", success_steps("development-3-14-6"), "success", "recommended", "Fresh SHA-verified release asset passed offline hash-locked PEP 517 sdist/wheel build, separate install, pip check, pytest, metadata, and artifact digest checks.", "Python 3.14.6; pip 26.2; build 1.5.0; Hatchling 1.31.0; pytest 9.1.1", [{"kind":"runtime_archive_sha256","value":"86bf107f65fc30b56f2b263b26797fcbb1661f5315910cdbf27f733eb8738b74"},{"kind":"extracted_runtime_tree_manifest_sha256","value":"c41a9b71760ee232683bde1bf919f3dc95822922104feee3ef3acc7edbe876ad"},{"kind":"wheel_sha256","value":"99137bdaa71c96a9fce94ee7a141c8c9c7b4ddc3c4b3df6257d6e09a47b4a643"}]),
        raw_probe("python-floor-3-11-15", "CPython 3.11.15; declared support floor >=3.11; python-build-standalone 20260718", success_steps("floor-3-11-15"), "success", "recommended", "The identical package-native offline sequence passed from the fresh SHA-verified floor release asset.", "Python 3.11.15; pip 26.2; build 1.5.0; Hatchling 1.31.0; pytest 9.1.1", [{"kind":"runtime_archive_sha256","value":"23ccae6f1ff73e8aa8378436f869da003b8eb7d6c95f2bc706f494115ba1447d"},{"kind":"extracted_runtime_tree_manifest_sha256","value":"63cf815a25d02d2b88031d46c0b11b9c5548dab53ea24b98c6168e179f050716"}]),
        raw_probe("python-rejected-3-10-20-metadata-rejection", "CPython 3.10.20 against Requires-Python >=3.11", ["rejected-3-10-20-python-version", "rejected-3-10-20-metadata-rejection"], "failure", "rejected", "pip rejected the wheel because 3.10.20 is outside Requires-Python >=3.11.", "Python 3.10.20; requires a different Python", [{"kind":"installed_runtime_tree_manifest_sha256","value":"f1b5dfab0b58f4b2a90e8de2352404db05c63c3a2e4f3d57578c2464ab2d5af0"}]),
        raw_probe("python-floor-cold-seed-network-failure", "CPython 3.11.15 cold uv seeded venv", ["floor-3-11-15-builder-venv-sandbox-network-failure"], "failure", "rejected", "Cold uv seed required absent packages and failed DNS; ordinary cache state was insufficient.", "uv 0.11.32; DNS resolution failure", []),
        raw_probe("python-development-pep517-network-failure", "CPython 3.14.6 PEP 517 build without wheelhouse", ["development-3-14-6-build-sandbox-network-failure"], "failure", "rejected", "PEP 517 isolation attempted to resolve Hatchling and failed without DNS.", "Python 3.14.6; no Hatchling distribution found offline", []),
        raw_probe("python-development-uv-seed-cache-failure", "CPython 3.14.6 uv seed from ordinary cache", ["development-3-14-6-builder-venv-uv-seed-cache-failure"], "failure", "rejected", "uv seed cache was interpreter-specific and still attempted a network fetch.", "uv 0.11.32; DNS resolution failure", []),
        raw_probe("python-rejected-pip-cache-network-failure", "CPython 3.10.20 ordinary pip cache", ["rejected-3-10-20-pin-pip-sandbox-network-failure"], "failure", "rejected", "Pinning pip from an ordinary cache still attempted mutable index metadata retrieval.", "Python 3.10.20; DNS resolution failure", []),
    ]


def main() -> None:
    sources = load(PROTOTYPES / "sources/sources.json") + EXTRA_SOURCES
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
    probes.sort(key=lambda item: item["id"])

    recommendations = [
        {"id":"lean-mathlib","component":"Lean/Mathlib/Lake","role":"initial normative proof backend research pin","development_pin":"Lean 4.32.1 commit f054605aea4b840552cca2e725580bffd1e1b704; Mathlib commit 520045ab14e26149ee970e2e617ca04b09bde5d6; bundled Lake 5.0.0-src+f054605","support_floor":"No range: support only the exact Mathlib-selected Lean pair","update_policy":"Re-query releases, resolve both immutable commits, rerun cached and no-cache builds plus axiom inspection","rollback_policy":"Restore the prior exact Lean/Mathlib commits and manifest; never mix adjacent tags","evidence_probe_ids":["lean-recommended-cache-success","lean-no-cache-success"],"ci_matrix":["lean-linux-exact","lean-linux-no-cache","lean-macos-planned","lean-windows-planned"]},
        {"id":"rust-cargo","component":"Rust/Cargo","role":"reference operational backend research pin","development_pin":"Rust 1.97.1; rustc build commit 8bab26f4f; Cargo build commit c980f4866","support_floor":"Rust 1.85.1 MSRV (rustc 4eb161250; Cargo d73d2caf9); Edition 2024; resolver 3","update_policy":"Advance stable only after dev and MSRV share one lock and fmt/clippy/test/audit pass","rollback_policy":"Restore rust-toolchain and Cargo.lock from the prior reviewed pin","evidence_probe_ids":["rust-install-dev","rust-dev-prototype","rust-install-msrv","rust-msrv-prototype","rustsec-audit"],"ci_matrix":["rust-linux-dev","rust-linux-msrv","rust-macos-planned","rust-windows-planned"]},
        {"id":"python","component":"Python","role":"thin frontend development/support research pin","development_pin":"CPython 3.14.6 upstream tag commit c63aec69bd59c55314c06c23f4c22c03de76fe45","support_floor":"Python >=3.11; exact floor patch tested: 3.11.15 commit 2340a037f7450e70fccfe411e6531afb4d57a312","update_policy":"Test every supported minor; refresh security patches and hash lock before upgrade","rollback_policy":"Restore prior interpreter patch and universal hash lock","evidence_probe_ids":["python-development-3-14-6","python-floor-3-11-15"],"ci_matrix":["python-linux-314","python-linux-311","python-linux-312-planned","python-linux-313-planned","python-macos-planned","python-windows-planned"]},
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
        {"id":"lean-linux-exact","component":"Lean/Mathlib/Lake","version":"4.32.1/520045ab","os":"Ubuntu 24.04.4","architecture":"x86_64","status":"direct_success","evidence_probe_ids":["lean-recommended-cache-success"]},
        {"id":"lean-linux-no-cache","component":"Lean/Mathlib/Lake","version":"4.32.1/520045ab no-cache","os":"Ubuntu 24.04.4","architecture":"x86_64","status":"direct_success","evidence_probe_ids":["lean-no-cache-success"]},
        {"id":"lean-macos-planned","component":"Lean/Mathlib/Lake","version":"exact pair","os":"macOS","architecture":"arm64","status":"planned_validation","evidence_probe_ids":[]},
        {"id":"lean-windows-planned","component":"Lean/Mathlib/Lake","version":"exact pair","os":"Windows","architecture":"x86_64","status":"planned_validation","evidence_probe_ids":[]},
        {"id":"rust-linux-dev","component":"Rust/Cargo","version":"1.97.1","os":"Ubuntu 24.04.4","architecture":"x86_64","status":"direct_success","evidence_probe_ids":["rust-dev-prototype"]},
        {"id":"rust-linux-msrv","component":"Rust/Cargo","version":"1.85.1","os":"Ubuntu 24.04.4","architecture":"x86_64","status":"direct_success","evidence_probe_ids":["rust-msrv-prototype"]},
        {"id":"rust-macos-planned","component":"Rust/Cargo","version":"1.97.1/1.85.1","os":"macOS","architecture":"arm64","status":"planned_validation","evidence_probe_ids":[]},
        {"id":"rust-windows-planned","component":"Rust/Cargo","version":"1.97.1/1.85.1","os":"Windows","architecture":"x86_64","status":"planned_validation","evidence_probe_ids":[]},
        {"id":"python-linux-314","component":"Python","version":"3.14.6","os":"Ubuntu 24.04.4","architecture":"x86_64","status":"direct_success","evidence_probe_ids":["python-development-3-14-6"]},
        {"id":"python-linux-311","component":"Python","version":"3.11.15","os":"Ubuntu 24.04.4","architecture":"x86_64","status":"direct_success","evidence_probe_ids":["python-floor-3-11-15"]},
        {"id":"python-linux-312-planned","component":"Python","version":"3.12 latest security patch","os":"Ubuntu","architecture":"x86_64","status":"planned_validation","evidence_probe_ids":[]},
        {"id":"python-linux-313-planned","component":"Python","version":"3.13 latest patch","os":"Ubuntu","architecture":"x86_64","status":"planned_validation","evidence_probe_ids":[]},
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

    subject_paths = sorted(
        path for directory in ("lean-mathlib", "rust", "python", "r", "julia", "arrow", "cbor-cddl")
        for path in (PROTOTYPES / directory).rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    )
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
        "retrieval_date": "2026-08-03",
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
