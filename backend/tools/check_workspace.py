#!/usr/bin/env python3
"""Verify the SQ-0004 Rust workspace and its adversarial mutations.

The checker uses only the Python standard library. It inspects project-owned
files, invokes exact installed Rust toolchains in constructed environments,
and creates mutations only in disposable temporary copies.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path
from typing import Any, Callable, Iterable


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = ROOT.parent
EXPECTED_TOOLCHAIN = "1.97.1"
EXPECTED_FLOOR = "1.85.1"
EXPECTED_EDITION = "2024"
EXPECTED_RESOLVER = "3"
EXPECTED_ERROR_EXIT = 2
FORBIDDEN_OUTPUT_KEYS = {
    "timestamp",
    "time",
    "random_id",
    "request_id",
    "host_path",
    "stack_trace",
}
FORBIDDEN_CARGO_ENV_FRAGMENTS = ("TOKEN", "CREDENTIAL", "SECRET")
EXPECTED_ACTIONS = {
    "actions/checkout": "3d3c42e5aac5ba805825da76410c181273ba90b1",
    "actions/setup-python": "5fda3b95a4ea91299a34e894583c3862153e4b97",
}
EXPECTED_EVIDENCE_FILES = {
    "evidence/advisory-report.json",
    "evidence/dependency-license-inventory.json",
    "evidence/deterministic-output-fixtures.json",
    "evidence/isolated-execution.json",
    "evidence/mutation-results.json",
    "evidence/security-lock.json",
    "evidence/source-lock.json",
}
EXPECTED_TOOL_FILES = {
    "tools/check_workspace.py",
    "tools/dependency_inventory.py",
    "tools/run_isolated_checks.py",
    "tools/security_audit.py",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as stream:
        return tomllib.load(stream)


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def source_manifest(root: Path) -> list[dict[str, str]]:
    paths = [
        root / "Cargo.toml",
        root / "Cargo.lock",
        root / "rust-toolchain.toml",
    ]
    paths.extend(sorted(root.glob("crates/*/Cargo.toml")))
    paths.extend(sorted(root.glob("crates/**/*.rs")))
    return [
        {"path": path.relative_to(root).as_posix(), "sha256": sha256(path)}
        for path in sorted(paths)
    ]


def compact_digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def credential_environment_findings(environment: dict[str, str]) -> list[str]:
    findings = []
    for key in sorted(environment):
        upper = key.upper()
        if not upper.startswith("CARGO_"):
            continue
        if any(fragment in upper for fragment in FORBIDDEN_CARGO_ENV_FRAGMENTS):
            findings.append(key)
    return findings


def workflow_findings_text(text: str) -> list[str]:
    findings: list[str] = []
    uses = re.findall(r"^\s*uses:\s*([^\s#]+)", text, flags=re.MULTILINE)
    expected_uses = [
        f"{action}@{revision}"
        for action, revision in EXPECTED_ACTIONS.items()
        for _ in range(2)
    ]
    if sorted(uses) != sorted(expected_uses):
        findings.append("workflow: action set or full-commit pin drifted")
    if re.search(r"uses:\s*[^\s#]+@(latest|main|master|v?\d+(?:\.\d+)*)\b", text):
        findings.append("workflow: floating action reference is prohibited")
    required_fragments = (
        "permissions:\n  contents: read",
        "persist-credentials: false",
        "timeout-minutes:",
        "concurrency:",
        "cargo +1.97.1 fetch --locked",
        "cargo +1.85.1 metadata --locked --offline",
        "cargo +1.85.1 test --workspace --all-targets",
        "CARGO_NET_OFFLINE=true",
        "git diff --exit-code",
    )
    for fragment in required_fragments:
        if fragment not in text:
            findings.append(f"workflow: required policy fragment missing: {fragment}")
    if text.count("persist-credentials: false") != 2:
        findings.append("workflow: every checkout must disable persisted credentials")
    prohibited_fragments = (
        "actions/cache@",
        "actions/upload-artifact@",
        "permissions: write-all",
        "contents: write",
    )
    for fragment in prohibited_fragments:
        if fragment in text:
            findings.append(f"workflow: prohibited capability present: {fragment}")
    return sorted(set(findings))


def workflow_findings(path: Path) -> list[str]:
    try:
        return workflow_findings_text(path.read_text(encoding="utf-8"))
    except OSError:
        return ["workflow: .github/workflows/rust.yml is missing or unreadable"]


def bound_file_findings(
    root: Path,
    entries: Any,
    expected_paths: set[str],
    category: str,
) -> list[str]:
    findings: list[str] = []
    if not isinstance(entries, list):
        return [f"bindings: {category} manifest is missing"]
    observed_paths = {
        entry.get("path") for entry in entries if isinstance(entry, dict)
    }
    if observed_paths != expected_paths:
        findings.append(f"bindings: {category} file set mismatch")
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            findings.append(f"bindings: malformed {category} entry")
            continue
        path = root / entry["path"]
        if not path.is_file():
            findings.append(f"bindings: missing bound file {entry['path']}")
        elif entry.get("sha256") != sha256(path):
            findings.append(f"bindings: digest mismatch for {entry['path']}")
    return findings


def project_findings(root: Path, *, check_bindings: bool = True) -> list[str]:
    findings: list[str] = []
    toolchain_path = root / "rust-toolchain.toml"
    workspace_path = root / "Cargo.toml"
    lock_path = root / "Cargo.lock"

    try:
        toolchain = load_toml(toolchain_path).get("toolchain", {})
    except (OSError, tomllib.TOMLDecodeError):
        toolchain = {}
        findings.append("toolchain: unreadable rust-toolchain.toml")
    if toolchain.get("channel") != EXPECTED_TOOLCHAIN:
        findings.append("toolchain: channel must be exactly 1.97.1")
    if sorted(toolchain.get("components", [])) != ["clippy", "rustfmt"]:
        findings.append("toolchain: components must be exactly clippy and rustfmt")
    if toolchain.get("profile") != "minimal":
        findings.append("toolchain: profile must be minimal")

    try:
        workspace = load_toml(workspace_path)
    except (OSError, tomllib.TOMLDecodeError):
        workspace = {}
        findings.append("workspace: unreadable Cargo.toml")
    workspace_table = workspace.get("workspace", {})
    package_policy = workspace.get("workspace", {}).get("package", {})
    if workspace_table.get("resolver") != EXPECTED_RESOLVER:
        findings.append("workspace: resolver must be exactly 3")
    if package_policy.get("edition") != EXPECTED_EDITION:
        findings.append("workspace: edition must be exactly 2024")
    if package_policy.get("rust-version") != EXPECTED_FLOOR:
        findings.append("workspace: rust-version must be exactly 1.85.1")
    rust_lints = workspace.get("workspace", {}).get("lints", {}).get("rust", {})
    if rust_lints.get("unsafe_code") != "forbid":
        findings.append("workspace: unsafe_code lint must be forbid")

    expected_packages = {"statqed-core", "statqed-cli"}
    observed_packages: set[str] = set()
    for manifest_path in sorted(root.glob("crates/*/Cargo.toml")):
        try:
            package_manifest = load_toml(manifest_path)
        except (OSError, tomllib.TOMLDecodeError):
            findings.append(f"package: unreadable {manifest_path.relative_to(root)}")
            continue
        package = package_manifest.get("package", {})
        name = package.get("name")
        if isinstance(name, str):
            observed_packages.add(name)
        edition = package.get("edition")
        if not isinstance(edition, dict) or edition.get("workspace") is not True:
            findings.append(f"package: {name} must inherit workspace edition")
        rust_version = package.get("rust-version")
        if not isinstance(rust_version, dict) or rust_version.get("workspace") is not True:
            findings.append(f"package: {name} must inherit workspace rust-version")
        if package_manifest.get("lints", {}).get("workspace") is not True:
            findings.append(f"package: {name} must inherit workspace lints")
        dependencies = package_manifest.get("dependencies", {})
        if name == "statqed-core" and dependencies:
            findings.append("package: statqed-core must remain dependency-free in SQ-0004")
        if name == "statqed-cli":
            expected_dependency = {"path": "../statqed-core"}
            if dependencies != {"statqed-core": expected_dependency}:
                findings.append("package: statqed-cli dependency graph drifted")
    if observed_packages != expected_packages:
        findings.append("workspace: package set must be statqed-core and statqed-cli")

    for source_path in sorted(root.glob("crates/**/*.rs")):
        try:
            source = source_path.read_text(encoding="utf-8")
        except OSError:
            findings.append(f"source: unreadable {source_path.relative_to(root)}")
            continue
        if "#![forbid(unsafe_code)]" not in source:
            findings.append(
                f"source: missing forbid(unsafe_code) in {source_path.relative_to(root)}"
            )

    cargo_config_candidates = [
        root / ".cargo" / "config",
        root / ".cargo" / "config.toml",
        root / ".cargo" / "credentials",
        root / ".cargo" / "credentials.toml",
    ]
    for candidate in cargo_config_candidates:
        if candidate.exists():
            findings.append(f"cargo-config: project Cargo state is prohibited: {candidate.name}")

    if lock_path.is_file():
        try:
            lock = load_toml(lock_path)
        except tomllib.TOMLDecodeError:
            findings.append("lock: Cargo.lock is not valid TOML")
            lock = {}
        if lock.get("version") != 4:
            findings.append("lock: Cargo.lock version must be 4")
        packages = lock.get("package", [])
        lock_names = {package.get("name") for package in packages if isinstance(package, dict)}
        if lock_names != expected_packages:
            findings.append("lock: exact graph must contain only the two local packages")
        if any(package.get("source") for package in packages if isinstance(package, dict)):
            findings.append("lock: SQ-0004 accepts no registry or alternate-source dependency")
    else:
        findings.append("lock: Cargo.lock is missing")

    if check_bindings:
        bindings_path = root / "evidence" / "bindings.json"
        if not bindings_path.is_file():
            findings.append("bindings: evidence/bindings.json is missing")
        else:
            bindings = load_json(bindings_path)
            if bindings.get("cargo_lock_sha256") != sha256(lock_path):
                findings.append("bindings: Cargo.lock digest mismatch")
            observed_manifest = source_manifest(root)
            if bindings.get("source_manifest") != observed_manifest:
                findings.append("bindings: project source manifest mismatch")
            if bindings.get("source_manifest_sha256") != compact_digest(observed_manifest):
                findings.append("bindings: project source manifest digest mismatch")
            findings.extend(
                bound_file_findings(
                    root,
                    bindings.get("evidence_files"),
                    EXPECTED_EVIDENCE_FILES,
                    "evidence",
                )
            )
            findings.extend(
                bound_file_findings(
                    root,
                    bindings.get("tool_files"),
                    EXPECTED_TOOL_FILES,
                    "tool",
                )
            )
            workflow = bindings.get("workflow")
            workflow_path = REPOSITORY_ROOT / ".github/workflows/rust.yml"
            if not isinstance(workflow, dict):
                findings.append("bindings: workflow binding is missing")
            elif workflow.get("path") != ".github/workflows/rust.yml":
                findings.append("bindings: workflow path mismatch")
            elif not workflow_path.is_file() or workflow.get("sha256") != sha256(workflow_path):
                findings.append("bindings: workflow digest mismatch")
            mutation_path = root / "evidence/mutation-results.json"
            fixture_path = root / "evidence/deterministic-output-fixtures.json"
            if mutation_path.is_file():
                mutation_cases = load_json(mutation_path).get("cases", [])
                if bindings.get("mutation_corpus_sha256") != compact_digest(mutation_cases):
                    findings.append("bindings: mutation corpus digest mismatch")
            if fixture_path.is_file() and bindings.get(
                "deterministic_output_fixture_sha256"
            ) != sha256(fixture_path):
                findings.append("bindings: deterministic-output fixture digest mismatch")

    findings.extend(workflow_findings(REPOSITORY_ROOT / ".github/workflows/rust.yml"))

    return sorted(findings)


def clean_environment(root: Path, temporary_root: Path, *, offline: bool) -> dict[str, str]:
    cargo = shutil.which("cargo")
    if cargo is None:
        raise RuntimeError("cargo proxy is unavailable")
    cargo_parent = str(Path(cargo).resolve().parent)
    home = temporary_root / "home"
    cargo_home = temporary_root / "cargo-home"
    target = temporary_root / "target"
    xdg = temporary_root / "xdg"
    for path in (home, cargo_home, target, xdg):
        path.mkdir(parents=True, exist_ok=True)
    rustup_home = os.environ.get("RUSTUP_HOME", str(Path.home() / ".rustup"))
    environment = {
        "HOME": str(home),
        "CARGO_HOME": str(cargo_home),
        "CARGO_TARGET_DIR": str(target),
        "RUSTUP_HOME": rustup_home,
        "XDG_CACHE_HOME": str(xdg / "cache"),
        "XDG_CONFIG_HOME": str(xdg / "config"),
        "XDG_DATA_HOME": str(xdg / "data"),
        "PATH": os.pathsep.join([cargo_parent, "/usr/bin", "/bin"]),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "TZ": "UTC",
        "CARGO_TERM_COLOR": "never",
        "CARGO_REGISTRIES_CRATES_IO_PROTOCOL": "sparse",
    }
    if offline:
        environment["CARGO_NET_OFFLINE"] = "true"
    if credential_environment_findings(environment):
        raise RuntimeError("constructed Cargo environment unexpectedly contains credentials")
    return environment


def run(
    command: list[str],
    *,
    cwd: Path,
    environment: dict[str, str],
    timeout: int = 120,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )


def validate_machine_output(stdout: str, stderr: str, returncode: int) -> list[str]:
    findings: list[str] = []
    if stdout:
        findings.append("output: malformed invocation wrote stdout")
    if returncode != EXPECTED_ERROR_EXIT:
        findings.append("output: malformed invocation exit code must be 2")
    try:
        payload = json.loads(stderr)
    except json.JSONDecodeError:
        return findings + ["output: stderr is not one deterministic JSON object"]
    if payload.get("protocol_version") != 1:
        findings.append("output: protocol_version must be 1")
    error = payload.get("error")
    if not isinstance(error, dict):
        findings.append("output: error object is missing")
    else:
        if sorted(error) != ["code", "message"]:
            findings.append("output: error object has unstable or extra fields")
        if not isinstance(error.get("code"), str) or not isinstance(error.get("message"), str):
            findings.append("output: error code/message must be strings")

    def inspect(value: Any) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                if key in FORBIDDEN_OUTPUT_KEYS:
                    findings.append(f"output: forbidden nondeterministic field {key}")
                inspect(nested)
        elif isinstance(value, list):
            for nested in value:
                inspect(nested)
        elif isinstance(value, str):
            if value.startswith(("/tmp/", "/home/")) or "\\Users\\" in value:
                findings.append("output: host path leakage")
            if any(marker in value for marker in ("Err(", "Some(", "backtrace", "panicked at")):
                findings.append("output: unstable debug or panic text")

    inspect(payload)
    return sorted(set(findings))


def runtime_findings(root: Path, toolchain: str = EXPECTED_TOOLCHAIN) -> list[str]:
    findings: list[str] = []
    with tempfile.TemporaryDirectory(prefix="statqed-rust-runtime-") as temporary:
        temporary_root = Path(temporary)
        environment = clean_environment(root, temporary_root, offline=True)
        cargo = ["cargo", f"+{toolchain}", "run", "--quiet", "--locked", "--offline", "-p", "statqed-cli", "--"]
        version = run(cargo + ["version", "--format", "json"], cwd=root, environment=environment)
        if version.returncode != 0 or version.stderr:
            findings.append("runtime: deterministic JSON version command failed")
        else:
            try:
                payload = json.loads(version.stdout)
            except json.JSONDecodeError:
                findings.append("runtime: JSON version output is invalid")
            else:
                expected_keys = ["program", "protocol_version", "rust", "version"]
                if sorted(payload) != expected_keys:
                    findings.append("runtime: JSON version field set drifted")
                if payload.get("protocol_version") != 1:
                    findings.append("runtime: JSON version protocol drifted")

        malformed = run(cargo + ["version", "--format"], cwd=root, environment=environment)
        findings.extend(validate_machine_output(malformed.stdout, malformed.stderr, malformed.returncode))
        fixtures_path = root / "evidence/deterministic-output-fixtures.json"
        try:
            fixtures = load_json(fixtures_path)
        except (OSError, json.JSONDecodeError):
            findings.append("runtime: deterministic-output fixtures are unreadable")
        else:
            cases = fixtures.get("cases", [])
            if fixtures.get("schema_version") != 1 or not isinstance(cases, list):
                findings.append("runtime: deterministic-output fixture shape is invalid")
            else:
                for case in cases:
                    if not isinstance(case, dict) or not isinstance(case.get("args"), list):
                        findings.append("runtime: malformed deterministic-output fixture")
                        continue
                    observed = run(cargo + case["args"], cwd=root, environment=environment)
                    if (
                        observed.returncode != case.get("exit_status")
                        or observed.stdout != case.get("stdout")
                        or observed.stderr != case.get("stderr")
                    ):
                        findings.append(
                            f"runtime: deterministic-output fixture failed: {case.get('id', 'unknown')}"
                        )
    return sorted(set(findings))


def copy_workspace(source: Path, destination: Path) -> Path:
    ignored = shutil.ignore_patterns("target", "__pycache__", "*.pyc")
    shutil.copytree(source, destination, ignore=ignored)
    return destination


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise RuntimeError(f"mutation anchor is not unique in {path}: {old!r}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def mutation_results(root: Path) -> dict[str, Any]:
    cases: list[dict[str, str]] = []

    def record(case_id: str, rejected: bool, reason: str) -> None:
        if not rejected:
            raise RuntimeError(f"mutation was not rejected: {case_id}")
        cases.append(
            {
                "id": case_id,
                "classification": "rejected",
                "reason": reason,
            }
        )

    def copied(case_id: str, mutate: Callable[[Path], tuple[bool, str]]) -> None:
        with tempfile.TemporaryDirectory(prefix=f"statqed-{case_id}-") as temporary:
            mutated = copy_workspace(root, Path(temporary) / "backend")
            rejected, reason = mutate(mutated)
            record(case_id, rejected, reason)

    def unsafe_code(mutated: Path) -> tuple[bool, str]:
        source = mutated / "crates/statqed-core/src/lib.rs"
        source.write_text(
            source.read_text(encoding="utf-8")
            + "\npub fn mutation_unsafe() { unsafe { core::ptr::read_volatile(&0); } }\n",
            encoding="utf-8",
        )
        with tempfile.TemporaryDirectory(prefix="statqed-unsafe-cargo-") as temporary:
            environment = clean_environment(mutated, Path(temporary), offline=True)
            observed = run(
                ["cargo", "+1.97.1", "check", "--workspace", "--locked", "--offline"],
                cwd=mutated,
                environment=environment,
            )
        return observed.returncode != 0 and "unsafe" in observed.stderr, "compiler rejected unsafe code under forbid"

    copied("project-unsafe-code", unsafe_code)

    def removed_forbid(mutated: Path) -> tuple[bool, str]:
        replace_once(mutated / "crates/statqed-core/src/lib.rs", "#![forbid(unsafe_code)]", "")
        return any("missing forbid" in item for item in project_findings(mutated)), "static target policy rejected removed forbid"

    copied("removed-forbid-unsafe-code", removed_forbid)

    def workspace_rust_version(mutated: Path) -> tuple[bool, str]:
        replace_once(mutated / "Cargo.toml", 'rust-version = "1.85.1"', 'rust-version = "1.86.0"')
        return any("rust-version" in item for item in project_findings(mutated)), "workspace policy rejected changed rust-version"

    copied("changed-workspace-rust-version", workspace_rust_version)

    def package_rust_version(mutated: Path) -> tuple[bool, str]:
        replace_once(
            mutated / "crates/statqed-core/Cargo.toml",
            "rust-version.workspace = true",
            'rust-version = "1.86.0"',
        )
        return any("inherit workspace rust-version" in item for item in project_findings(mutated)), "package policy rejected changed rust-version"

    copied("changed-package-rust-version", package_rust_version)

    def dependency_without_lock(mutated: Path) -> tuple[bool, str]:
        manifest = mutated / "crates/statqed-core/Cargo.toml"
        manifest.write_text(manifest.read_text(encoding="utf-8") + '\n[dependencies]\nitoa = "1"\n', encoding="utf-8")
        with tempfile.TemporaryDirectory(prefix="statqed-lock-drift-") as temporary:
            environment = clean_environment(mutated, Path(temporary), offline=True)
            observed = run(
                ["cargo", "+1.97.1", "metadata", "--locked", "--offline", "--format-version", "1"],
                cwd=mutated,
                environment=environment,
            )
        static_rejection = any(
            "dependency-free" in item for item in project_findings(mutated)
        )
        return static_rejection and observed.returncode != 0, "workspace policy and Cargo --locked rejected dependency graph drift"

    copied("dependency-graph-without-lock", dependency_without_lock)

    def changed_lock(mutated: Path) -> tuple[bool, str]:
        lock = mutated / "Cargo.lock"
        lock.write_text(lock.read_text(encoding="utf-8") + "# mutation\n", encoding="utf-8")
        return any("Cargo.lock digest mismatch" in item for item in project_findings(mutated)), "binding rejected changed Cargo.lock bytes"

    copied("changed-cargo-lock", changed_lock)

    def alternate_registry(mutated: Path) -> tuple[bool, str]:
        config = mutated / ".cargo/config.toml"
        config.parent.mkdir()
        config.write_text('[source.crates-io]\nreplace-with = "alternate"\n', encoding="utf-8")
        return any("Cargo state is prohibited" in item for item in project_findings(mutated)), "project Cargo configuration rejected alternate registry"

    copied("alternate-registry", alternate_registry)

    synthetic_environment = {"CARGO_REGISTRIES_CRATES_IO_TOKEN": "fixture-not-a-secret"}
    record(
        "ambient-cargo-credentials",
        credential_environment_findings(synthetic_environment)
        == ["CARGO_REGISTRIES_CRATES_IO_TOKEN"],
        "environment allowlist rejected inherited Cargo credential variable",
    )

    workflow_path = REPOSITORY_ROOT / ".github/workflows/rust.yml"
    workflow_text = workflow_path.read_text(encoding="utf-8")
    floating_workflow = workflow_text.replace(
        "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
        "actions/checkout@v7",
        1,
    )
    record(
        "floating-github-action",
        bool(workflow_findings_text(floating_workflow)),
        "workflow policy rejected a floating action tag",
    )
    credential_workflow = workflow_text.replace(
        "persist-credentials: false", "persist-credentials: true", 1
    )
    record(
        "persisted-checkout-credentials",
        bool(workflow_findings_text(credential_workflow)),
        "workflow policy rejected persisted checkout credentials",
    )

    with tempfile.TemporaryDirectory(prefix="statqed-floor-network-") as temporary:
        fixture = Path(temporary) / "fixture"
        fixture.mkdir()
        (fixture / "Cargo.toml").write_text(
            '[package]\nname="floor-network-fixture"\nversion="0.0.0"\nedition="2024"\n'
            '[dependencies]\nitoa="=1.0.15"\n',
            encoding="utf-8",
        )
        (fixture / "src").mkdir()
        (fixture / "src/lib.rs").write_text("#![forbid(unsafe_code)]\n", encoding="utf-8")
        environment = clean_environment(fixture, Path(temporary) / "isolation", offline=True)
        observed = run(
            ["cargo", "+1.85.1", "metadata", "--offline", "--format-version", "1"],
            cwd=fixture,
            environment=environment,
        )
        record(
            "floor-network-acquisition",
            observed.returncode != 0
            and ("offline mode" in observed.stderr.lower() or "no matching package" in observed.stderr.lower()),
            "Rust 1.85.1 failed closed with an empty Cargo home in offline mode",
        )

    timestamp_payload = (
        "",
        '{"protocol_version":1,"timestamp":"2026-08-09T00:00:00Z",'
        '"error":{"code":"missing_command","message":"a command is required"}}\n',
        2,
    )
    record(
        "nondeterministic-timestamp-field",
        any("timestamp" in item for item in validate_machine_output(*timestamp_payload)),
        "machine-output validator rejected timestamp field",
    )
    random_payload = (
        "",
        '{"protocol_version":1,"random_id":"123",'
        '"error":{"code":"missing_command","message":"a command is required"}}\n',
        2,
    )
    record(
        "nondeterministic-random-field",
        any("random_id" in item for item in validate_machine_output(*random_payload)),
        "machine-output validator rejected random identifier field",
    )
    path_payload = (
        "",
        '{"protocol_version":1,"error":{"code":"missing_command",'
        '"message":"/tmp/statqed-host-path"}}\n',
        2,
    )
    record(
        "host-path-leakage",
        any("host path" in item for item in validate_machine_output(*path_payload)),
        "machine-output validator rejected host path",
    )

    def panic_on_malformed(mutated: Path) -> tuple[bool, str]:
        main = mutated / "crates/statqed-cli/src/main.rs"
        replace_once(
            main,
            "Err(error) => emit_stderr(error.as_json(), MALFORMED_INPUT_EXIT_CODE),",
            'Err(_error) => panic!("mutation panic"),',
        )
        with tempfile.TemporaryDirectory(prefix="statqed-panic-") as temporary:
            environment = clean_environment(mutated, Path(temporary), offline=True)
            observed = run(
                ["cargo", "+1.97.1", "run", "--quiet", "--locked", "--offline", "-p", "statqed-cli", "--", "unknown"],
                cwd=mutated,
                environment=environment,
            )
        output_findings = validate_machine_output(observed.stdout, observed.stderr, observed.returncode)
        return observed.returncode != 2 and bool(output_findings), "runtime contract rejected panic on malformed input"

    copied("panic-on-malformed-input", panic_on_malformed)

    def debug_error_text(mutated: Path) -> tuple[bool, str]:
        main = mutated / "crates/statqed-cli/src/main.rs"
        replace_once(
            main,
            "Err(error) => emit_stderr(error.as_json(), MALFORMED_INPUT_EXIT_CODE),",
            "Err(error) => { eprintln!(\"{error:?}\"); ExitCode::from(MALFORMED_INPUT_EXIT_CODE) },",
        )
        with tempfile.TemporaryDirectory(prefix="statqed-debug-") as temporary:
            environment = clean_environment(mutated, Path(temporary), offline=True)
            observed = run(
                ["cargo", "+1.97.1", "run", "--quiet", "--locked", "--offline", "-p", "statqed-cli", "--", "unknown"],
                cwd=mutated,
                environment=environment,
            )
        return bool(validate_machine_output(observed.stdout, observed.stderr, observed.returncode)), "runtime contract rejected unstable Debug output"

    copied("dependency-debug-text", debug_error_text)

    return {"schema_version": 1, "case_count": len(cases), "cases": sorted(cases, key=lambda item: item["id"])}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="emit machine-readable check output")
    parser.add_argument("--run-mutations", action="store_true")
    parser.add_argument("--record-mutations", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    findings = project_findings(ROOT)
    findings.extend(runtime_findings(ROOT))
    findings = sorted(set(findings))
    mutations: dict[str, Any] | None = None
    if args.run_mutations or args.record_mutations:
        try:
            mutations = mutation_results(ROOT)
        except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
            findings.append(f"mutations: {error}")
    if args.run_mutations and mutations is not None and not findings:
        retained_path = ROOT / "evidence" / "mutation-results.json"
        rendered = json.dumps(mutations, indent=2, sort_keys=True) + "\n"
        if not retained_path.is_file() or retained_path.read_text(encoding="utf-8") != rendered:
            findings.append("mutations: retained mutation results differ from generated results")
    if args.record_mutations and mutations is not None and not findings:
        args.record_mutations.parent.mkdir(parents=True, exist_ok=True)
        args.record_mutations.write_text(
            json.dumps(mutations, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    result = {
        "schema_version": 1,
        "status": "pass" if not findings else "fail",
        "findings": findings,
        "mutation_case_count": mutations["case_count"] if mutations else 0,
    }
    if args.json:
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    elif findings:
        print("SQ-0004 Rust workspace checks failed:", file=sys.stderr)
        for finding in findings:
            print(f"  - {finding}", file=sys.stderr)
    else:
        suffix = f"; {mutations['case_count']} mutations rejected" if mutations else ""
        print(f"SQ-0004 Rust workspace checks passed{suffix}")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
