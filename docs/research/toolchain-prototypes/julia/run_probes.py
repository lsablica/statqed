#!/usr/bin/env python3
"""Run the isolated SQ-0002 Julia/Pkg compatibility probes.

The script intentionally uses only the Python standard library. Downloaded
Julia runtimes, depots, compiled caches, and working copies stay under /tmp.
Only concise command/output metadata is retained. Generated manifests are
compared byte-for-byte with versioned locks retained under ``locks/``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
PROBE_ROOT = Path(__file__).resolve().parent
LOG_ROOT = Path(
    os.environ.get(
        "SQ0002_JULIA_LOG_ROOT",
        REPOSITORY_ROOT / "docs/research/toolchain-prototypes/logs/julia",
    )
)
SOURCE_REFS = [
    "julia-support-policy",
    "julia-release-v1.12.6",
    "julia-release-v1.10.11",
    "julia-pkg-toml",
    "julia-pkg-registries",
]
LOCK_ROOT = PROBE_ROOT / "locks"

RUNTIMES = {
    "1.12.6": {
        "binary": Path(os.environ.get("SQ0002_JULIA_DEVELOPMENT_BINARY", "/tmp/statqed-julia-runtimes/julia-1.12.6/bin/julia")),
        "archive": Path(os.environ.get("SQ0002_JULIA_DEVELOPMENT_ARCHIVE", "/tmp/julia-1.12.6-linux-x86_64.tar.gz")),
        "archive_sha256": "bbabf3bef19421a9dbd24a767d807606ab85e444323b5a1c73ffe293fa3d079a",
        "role": "development",
    },
    "1.10.11": {
        "binary": Path(os.environ.get("SQ0002_JULIA_FLOOR_BINARY", "/tmp/statqed-julia-runtimes/julia-1.10.11/bin/julia")),
        "archive": Path(os.environ.get("SQ0002_JULIA_FLOOR_ARCHIVE", "/tmp/julia-1.10.11-linux-x86_64.tar.gz")),
        "archive_sha256": "fb49c6b174600cd2051e37ba3f7330f8acf06dd00bce609bab6611387fdb37bf",
        "role": "floor-lts",
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def relative(path: Path) -> str:
    try:
        return path.relative_to(REPOSITORY_ROOT).as_posix()
    except ValueError:
        # Owned verification dispatchers deliberately place all generated
        # logs outside the repository and remove them on exit.
        return str(path)


def run_command(
    *,
    attempt_id: str,
    command_id: str,
    argv: list[str],
    cwd: Path,
    environment: dict[str, str],
    run_log_root: Path,
) -> dict[str, object]:
    stdout_path = run_log_root / f"{attempt_id}-{command_id}.stdout"
    stderr_path = run_log_root / f"{attempt_id}-{command_id}.stderr"
    metadata_path = run_log_root / f"{attempt_id}-{command_id}.command.json"
    started = utc_now()
    completed = subprocess.run(
        argv,
        cwd=cwd,
        env={**os.environ, **environment},
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    ended = utc_now()
    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")
    metadata = {
        "id": command_id,
        "argv": argv,
        "cwd": str(cwd),
        "environment_variables": environment,
        "start": started,
        "end": ended,
        "exit_status": completed.returncode,
        "stdout_path": relative(stdout_path),
        "stderr_path": relative(stderr_path),
    }
    metadata_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return metadata


def combine_logs(
    attempt_id: str, command_records: list[dict[str, object]], run_log_root: Path
) -> tuple[Path, Path]:
    combined_stdout = run_log_root / f"{attempt_id}.stdout"
    combined_stderr = run_log_root / f"{attempt_id}.stderr"
    stdout_parts: list[str] = []
    stderr_parts: list[str] = []
    for record in command_records:
        heading = f"$ {json.dumps(record['argv'])}\n"
        stdout_parts.extend(
            [heading, (REPOSITORY_ROOT / str(record["stdout_path"])).read_text()]
        )
        stderr_parts.extend(
            [heading, (REPOSITORY_ROOT / str(record["stderr_path"])).read_text()]
        )
    combined_stdout.write_text("".join(stdout_parts), encoding="utf-8")
    combined_stderr.write_text("".join(stderr_parts), encoding="utf-8")
    return combined_stdout, combined_stderr


def prepare_working_copy(version: str) -> tuple[Path, Path, Path]:
    work_root = Path(tempfile.mkdtemp(prefix=f"statqed-julia-{version}-", dir="/tmp"))
    project = work_root / "project"
    depot = work_root / "depot"
    project.mkdir()
    depot.mkdir()
    # Pkg otherwise bootstraps General merely because the depot has no known
    # registry, even though this probe has only stdlib dependencies.  A fixed,
    # valid empty local registry makes the no-General/no-network assumption
    # explicit without contaminating the isolated depot with a global cache.
    registry = depot / "registries/StatQEDProbeRegistry"
    registry.mkdir(parents=True)
    (registry / "Registry.toml").write_text(
        'name = "StatQEDProbeRegistry"\n'
        'uuid = "59fb3518-58e7-4454-a10f-5790d776e366"\n'
        'repo = "file:///nonexistent/statqed-probe-registry"\n'
        'description = "Empty local registry sentinel for the offline SQ-0002 probe"\n'
        "\n[packages]\n",
        encoding="utf-8",
    )
    shutil.copy2(PROBE_ROOT / "Project.toml", project / "Project.toml")
    shutil.copytree(PROBE_ROOT / "src", project / "src")
    shutil.copytree(PROBE_ROOT / "test", project / "test")
    return work_root, project, depot


def bind_manifest(version: str, generated: Path) -> tuple[Path, str]:
    """Bind a generated manifest to its reviewed, retained lock bytes.

    ``SQ0002_JULIA_RECORD_LOCKS=1`` is a deliberate evidence-capture mode. A
    normal probe never refreshes a lock: it requires the retained bytes and
    fails closed on drift.
    """

    if not generated.is_file():
        raise RuntimeError(f"Julia {version} did not generate Manifest.toml")
    retained = LOCK_ROOT / f"Manifest-{version}.toml"
    if os.environ.get("SQ0002_JULIA_RECORD_LOCKS") == "1":
        LOCK_ROOT.mkdir(parents=True, exist_ok=True)
        if retained.exists() and retained.read_bytes() != generated.read_bytes():
            raise RuntimeError(
                f"refusing to overwrite drifting retained Julia lock: {retained}"
            )
        if not retained.exists():
            shutil.copy2(generated, retained)
    if not retained.is_file():
        raise RuntimeError(
            f"retained Julia lock is absent for {version}: {retained}"
        )
    if retained.read_bytes() != generated.read_bytes():
        raise RuntimeError(
            f"generated Julia {version} manifest differs from {retained}"
        )
    return retained, sha256(retained)


def run_candidate(
    version: str,
    details: dict[str, object],
    run_log_root: Path,
    prior_attempt: dict[str, object] | None = None,
) -> dict[str, object]:
    binary = Path(details["binary"])
    archive = Path(details["archive"])
    expected_archive_sha256 = str(details["archive_sha256"])
    if not binary.is_file():
        raise FileNotFoundError(f"missing Julia runtime: {binary}")
    if not archive.is_file():
        raise FileNotFoundError(f"missing Julia archive: {archive}")
    observed_archive_sha256 = sha256(archive)
    if observed_archive_sha256 != expected_archive_sha256:
        raise RuntimeError(
            f"archive digest mismatch for Julia {version}: "
            f"{observed_archive_sha256} != {expected_archive_sha256}"
        )

    if prior_attempt is None:
        _, project, depot = prepare_working_copy(version)
    else:
        project_argument = str(prior_attempt["commands"][1][3])
        project = Path(project_argument.removeprefix("--project="))
        depot = Path(str(prior_attempt["environment_variables"]["JULIA_DEPOT_PATH"]))
    environment = {
        "JULIA_DEPOT_PATH": str(depot),
        "JULIA_LOAD_PATH": "@:@stdlib",
        "JULIA_NUM_THREADS": "1",
        "JULIA_PKG_OFFLINE": "true",
        "JULIA_PKG_PRECOMPILE_AUTO": "0",
        "JULIA_PKG_SERVER": "",
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
    }
    common = [
        str(binary),
        "--startup-file=no",
        "--history-file=no",
        f"--project={project}",
    ]
    commands = [
        ("version", [str(binary), "--version"]),
        (
            "versioninfo",
            common
            + [
                "-e",
                "using InteractiveUtils; versioninfo(verbose=true); "
                "println(\"Sys.MACHINE=\", Sys.MACHINE); "
                "println(\"Sys.KERNEL=\", Sys.KERNEL)",
            ],
        ),
        (
            "resolve",
            common + ["-e", "using Pkg; Pkg.resolve()"],
        ),
        (
            "instantiate",
            common
            + [
                "-e",
                "using Pkg; Pkg.instantiate(; verbose=true, update_registry=false)",
            ],
        ),
        (
            "precompile",
            common + ["-e", "using Pkg; Pkg.precompile(; strict=true)"],
        ),
        (
            "test",
            common + ["-e", "using Pkg; Pkg.test(; coverage=false)"],
        ),
        (
            "status",
            common
            + [
                "-e",
                "using Pkg; Pkg.status(; mode=Pkg.PKGMODE_PROJECT); "
                "Pkg.status(; mode=Pkg.PKGMODE_MANIFEST)",
            ],
        ),
    ]
    attempt_id = f"{details['role']}-julia-{version.replace('.', '-')}-linux-x86-64"
    if prior_attempt is not None:
        attempt_id += "-recovery-after-registry-bootstrap-failure"
    command_records = [
        run_command(
            attempt_id=attempt_id,
            command_id=command_id,
            argv=argv,
            cwd=REPOSITORY_ROOT,
            environment=environment,
            run_log_root=run_log_root,
        )
        for command_id, argv in commands
    ]
    if any(record["exit_status"] != 0 for record in command_records):
        classification = "candidate_failure"
        disposition = "rejected"
        reason = "At least one package-native command failed; inspect command logs."
    else:
        classification = "compatible"
        disposition = "recommended"
        reason = (
            "Exact official runtime passed isolated offline Pkg instantiate, "
            "precompile, test, and status commands on the named host."
        )

    manifest = project / "Manifest.toml"
    retained_manifest: Path | None = None
    manifest_sha256: str | None = None
    if classification == "compatible":
        retained_manifest, manifest_sha256 = bind_manifest(version, manifest)

    combined_stdout, combined_stderr = combine_logs(
        attempt_id, command_records, run_log_root
    )
    version_stdout = (
        REPOSITORY_ROOT / str(command_records[0]["stdout_path"])
    ).read_text(encoding="utf-8").strip()
    return {
        "id": attempt_id,
        "component": "Julia/Pkg",
        "candidate": version,
        "platform": {
            "os": "Ubuntu 24.04.4 LTS",
            "kernel": "Linux 7.0.0-28-generic",
            "architecture": "x86_64",
            "libc": "glibc 2.39",
            "locale": "C.UTF-8",
            "directly_tested": True,
        },
        "commands": [record["argv"] for record in command_records],
        "environment_variables": environment,
        "dependency_locks": {
            "runtime_archive": str(archive),
            "runtime_archive_sha256": observed_archive_sha256,
            "project_toml": relative(PROBE_ROOT / "Project.toml"),
            "project_toml_sha256": sha256(PROBE_ROOT / "Project.toml"),
            "manifest_toml": relative(retained_manifest)
            if retained_manifest is not None
            else None,
            "manifest_toml_sha256": manifest_sha256,
            "registry_packages": [],
            "stdlib_dependencies": ["SHA", "Test"],
        },
        "start": command_records[0]["start"],
        "end": command_records[-1]["end"],
        "exit_status": [record["exit_status"] for record in command_records],
        "stdout_path": relative(combined_stdout),
        "stderr_path": relative(combined_stderr),
        "classification": classification,
        "reason": reason,
        "source_refs": SOURCE_REFS,
        "disposition": disposition,
        "version_output": version_stdout,
        "rerun": {
            "locally_runnable": True,
            "fresh_working_directory": str(project),
            "isolated_empty_depot_at_start": str(depot),
            "network": "disabled by JULIA_PKG_OFFLINE=true, JULIA_PKG_SERVER='', a fixed valid empty local registry, and sandbox isolation",
            "cache": (
                "empty per-candidate depot; later commands reuse only caches created by earlier commands in this same attempt"
                if prior_attempt is None
                else "isolated candidate depot; Pkg compilation cache was created by the separately recorded failed empty-depot attempt, with no registry or package dependency added"
            ),
            "command": [
                "python3",
                relative(PROBE_ROOT / "run_probes.py"),
                "--run-id",
                "<new-run-id>",
            ],
        },
    }


def run_rejection(run_log_root: Path, successful_attempt: dict[str, object]) -> dict[str, object]:
    version = "1.12.6"
    binary = Path(RUNTIMES[version]["binary"])
    depot = Path(
        str(successful_attempt["environment_variables"]["JULIA_DEPOT_PATH"])
    )
    environment = {
        **successful_attempt["environment_variables"],
        "JULIA_DEPOT_PATH": str(depot),
    }
    argv = [
        str(binary),
        "--startup-file=no",
        "--history-file=no",
        f"--project={PROBE_ROOT / 'rejected-compat'}",
        "-e",
        "using Pkg; Pkg.resolve()",
    ]
    attempt_id = "rejected-julia-1-12-6-requires-1-13"
    record = run_command(
        attempt_id=attempt_id,
        command_id="resolve",
        argv=argv,
        cwd=REPOSITORY_ROOT,
        environment=environment,
        run_log_root=run_log_root,
    )
    stderr = (REPOSITORY_ROOT / str(record["stderr_path"])).read_text(
        encoding="utf-8"
    )
    expected = (
        record["exit_status"] != 0
        and 'compat entry "julia = 1.13" does not include Julia version 1.12.6'
        in stderr
    )
    combined_stdout, combined_stderr = combine_logs(attempt_id, [record], run_log_root)
    return {
        "id": attempt_id,
        "component": "Julia/Pkg",
        "candidate": "Julia 1.12.6 against [compat] julia = \"1.13\"",
        "platform": successful_attempt["platform"],
        "commands": [argv],
        "environment_variables": environment,
        "dependency_locks": {
            "runtime_archive_sha256": RUNTIMES[version]["archive_sha256"],
            "project_toml": relative(PROBE_ROOT / "rejected-compat/Project.toml"),
            "project_toml_sha256": sha256(
                PROBE_ROOT / "rejected-compat/Project.toml"
            ),
            "manifest_toml": None,
        },
        "start": record["start"],
        "end": record["end"],
        "exit_status": record["exit_status"],
        "stdout_path": relative(combined_stdout),
        "stderr_path": relative(combined_stderr),
        "classification": "expected_rejection" if expected else "mutation_failure",
        "reason": (
            "Pkg.resolve rejected the active project because its Julia compat range excludes the running Julia version."
            if expected
            else "The deliberate Julia compat mutation was not rejected with the expected diagnostic."
        ),
        "source_refs": ["julia-pkg-toml"],
        "disposition": "rejected" if expected else "probe_failed",
        "version_output": successful_attempt["version_output"],
        "rerun": {
            "locally_runnable": True,
            "command": argv,
            "expected_exit_status": "nonzero",
            "expected_diagnostic": 'compat entry "julia = 1.13" does not include Julia version 1.12.6',
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--run-id",
        default=datetime.now(timezone.utc).strftime("run-%Y%m%dT%H%M%SZ"),
        help="new log directory name under logs/julia",
    )
    parser.add_argument(
        "--reuse-from",
        type=Path,
        help="reuse the isolated project/depot paths from a preserved failed attempts-generated.json",
    )
    parser.add_argument(
        "--mode",
        choices=("all", "development", "floor"),
        default="all",
        help="run both endpoints or one exact endpoint",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_log_root = LOG_ROOT / args.run_id
    run_log_root.mkdir(parents=True, exist_ok=False)
    prior_attempts = None
    if args.reuse_from is not None:
        prior_attempts = json.loads(args.reuse_from.read_text(encoding="utf-8"))
    attempts = []
    selected = [
        (version, details)
        for version, details in RUNTIMES.items()
        if args.mode == "all"
        or (args.mode == "development" and details["role"] == "development")
        or (args.mode == "floor" and details["role"] == "floor-lts")
    ]
    for index, (version, details) in enumerate(selected):
        prior_attempt = prior_attempts[index] if prior_attempts is not None else None
        attempts.append(run_candidate(version, details, run_log_root, prior_attempt))
    candidate_count = len(attempts)
    if args.mode in {"all", "development"}:
        attempts.append(run_rejection(run_log_root, attempts[0]))
    generated_path = run_log_root / "attempts-generated.json"
    generated_path.write_text(
        json.dumps(attempts, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    for attempt in attempts[:candidate_count]:
        depot = Path(str(attempt["environment_variables"]["JULIA_DEPOT_PATH"]))
        work_root = depot.parent.resolve()
        if work_root.parent == Path("/tmp") and work_root.name.startswith("statqed-julia-"):
            shutil.rmtree(work_root)
        else:
            raise ValueError(f"refusing unsafe Julia cleanup target: {work_root}")

    expected_success = all(
        attempt["classification"] == "compatible"
        for attempt in attempts[:candidate_count]
    )
    if args.mode in {"all", "development"}:
        expected_success = expected_success and attempts[-1]["classification"] == "expected_rejection"
    return 0 if expected_success else 1


if __name__ == "__main__":
    raise SystemExit(main())
