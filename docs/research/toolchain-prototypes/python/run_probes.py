#!/usr/bin/env python3
"""Run the SQ-0002 Python packaging probes in isolated /tmp state."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]
LOG_ROOT = ROOT.parent / "logs" / "python" / "run-20260803"
TMP_ROOT = Path(os.environ.get("SQ0002_PYTHON_TMP", "/tmp/statqed-sq0002-python"))
UV = Path(os.environ.get("SQ0002_UV", "/tmp/statqed-sq0002-python-tools/uv"))
UV_CACHE = Path(os.environ.get("UV_CACHE_DIR", "/tmp/statqed-sq0002-python-cache"))
PYTHON_INSTALLS = Path(
    os.environ.get("UV_PYTHON_INSTALL_DIR", "/tmp/statqed-sq0002-python-runtimes")
)
WHEELHOUSE = Path(
    os.environ.get("SQ0002_PYTHON_WHEELHOUSE", "/tmp/statqed-sq0002-python-wheelhouse")
)
LOCK = ROOT / "probe-requirements.lock"
VERSIONS = {
    "development": "3.14.6",
    "floor": "3.11.15",
    "rejected": "3.10.20",
}
COMMON_ENV = {
    "LANG": "C.UTF-8",
    "LC_ALL": "C.UTF-8",
    "PYTHONHASHSEED": "0",
    "PIP_DISABLE_PIP_VERSION_CHECK": "1",
    "PIP_CACHE_DIR": "/tmp/statqed-sq0002-python-pip-cache",
    "PIP_NO_INPUT": "1",
    "UV_CACHE_DIR": str(UV_CACHE),
    "UV_PYTHON_INSTALL_DIR": str(PYTHON_INSTALLS),
    "UV_PYTHON_DOWNLOADS": "manual",
}


def now() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def safe_remove(path: Path) -> None:
    tmp_base = Path("/tmp").resolve()
    task_root = TMP_ROOT.resolve()
    task_root.relative_to(tmp_base)
    if task_root == tmp_base:
        raise ValueError("SQ0002_PYTHON_TMP must be a task-specific directory under /tmp")
    resolved = path.resolve()
    resolved.relative_to(task_root)
    if resolved.exists():
        shutil.rmtree(resolved)


def recreate_wheelhouse() -> None:
    tmp_base = Path("/tmp").resolve()
    resolved = WHEELHOUSE.resolve()
    resolved.relative_to(tmp_base)
    if resolved == tmp_base:
        raise ValueError("SQ0002_PYTHON_WHEELHOUSE must be a directory under /tmp")
    if resolved.exists():
        shutil.rmtree(resolved)
    resolved.mkdir(parents=True)


def run(
    name: str,
    command: Sequence[str],
    *,
    cwd: Path = ROOT,
    env_additions: dict[str, str] | None = None,
    expected: set[int] | None = None,
) -> subprocess.CompletedProcess[str]:
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment.update(COMMON_ENV)
    environment.update(env_additions or {})
    started_at = now()
    completed = subprocess.run(
        list(command),
        cwd=cwd,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    ended_at = now()
    (LOG_ROOT / f"{name}.stdout").write_text(completed.stdout, encoding="utf-8")
    (LOG_ROOT / f"{name}.stderr").write_text(completed.stderr, encoding="utf-8")
    record: dict[str, Any] = {
        "name": name,
        "started_at": started_at,
        "ended_at": ended_at,
        "cwd": str(cwd.relative_to(REPO)),
        "command": list(command),
        "environment_variables": COMMON_ENV | (env_additions or {}),
        "exit_status": completed.returncode,
        "expected_exit_statuses": sorted(expected or {0}),
    }
    (LOG_ROOT / f"{name}.command.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    sys.stdout.write(completed.stdout)
    sys.stderr.write(completed.stderr)
    if completed.returncode not in (expected or {0}):
        raise SystemExit(
            f"{name} exited {completed.returncode}; expected {sorted(expected or {0})}"
        )
    return completed


def uv(*args: str) -> list[str]:
    if not UV.is_file():
        raise SystemExit(
        f"uv not found at {UV}; install pinned uv 0.11.32 there or set SQ0002_UV"
        )
    return [str(UV), "--color", "never", "--no-progress", *args]


def compose_probe_log(prefix: str, step_names: Sequence[str]) -> None:
    """Create the concise stdout/stderr pair referenced by the matrix fragment."""

    stdout_sections: list[str] = []
    stderr_sections: list[str] = []
    for step_name in step_names:
        for suffix, sections in (("stdout", stdout_sections), ("stderr", stderr_sections)):
            path = LOG_ROOT / f"{step_name}.{suffix}"
            content = path.read_text(encoding="utf-8") if path.is_file() else ""
            if content:
                sections.append(f"## {step_name}\n{content.rstrip()}\n")
    (LOG_ROOT / f"{prefix}.stdout").write_text(
        "\n".join(stdout_sections), encoding="utf-8"
    )
    (LOG_ROOT / f"{prefix}.stderr").write_text(
        "\n".join(stderr_sections), encoding="utf-8"
    )


def managed_python(version: str) -> Path:
    explicit_variables = {
        VERSIONS["development"]: "SQ0002_PYTHON_DEVELOPMENT",
        VERSIONS["floor"]: "SQ0002_PYTHON_FLOOR",
        VERSIONS["rejected"]: "SQ0002_PYTHON_REJECTED",
    }
    explicit = os.environ.get(explicit_variables[version])
    if explicit:
        path = Path(explicit)
        if not path.is_file():
            raise SystemExit(f"explicit Python does not exist: {path}")
        return path
    completed = subprocess.run(
        uv("python", "find", "--managed-python", version),
        env=os.environ | COMMON_ENV,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.stderr)
    return Path(completed.stdout.strip())


def prepare() -> None:
    run("uv-version", uv("--version"))
    run(
        "managed-runtime-install",
        uv(
            "python",
            "install",
            "--no-bin",
            "--install-dir",
            str(PYTHON_INSTALLS),
            *VERSIONS.values(),
        ),
    )
    floor_python = managed_python(VERSIONS["floor"])
    run(
        "requirements-lock",
        uv(
            "pip",
            "compile",
            "--python",
            str(floor_python),
            "--universal",
            "--generate-hashes",
            "--no-emit-index-url",
            "--output-file",
            str(LOCK),
            str(ROOT / "probe-requirements.in"),
        ),
    )
    safe_remove(TMP_ROOT / "wheelhouse-download")
    recreate_wheelhouse()
    downloader = TMP_ROOT / "wheelhouse-download"
    run(
        "wheelhouse-download-venv",
        [str(floor_python), "-m", "venv", str(downloader)],
    )
    run(
        "wheelhouse-download",
        [
            str(downloader / "bin" / "python"),
            "-m",
            "pip",
            "download",
            "--require-hashes",
            "--only-binary=:all:",
            "--dest",
            str(WHEELHOUSE),
            "-r",
            str(LOCK),
        ],
    )


def write_runtime_script(path: Path) -> None:
    path.write_text(
        """from __future__ import annotations
import hashlib
import importlib.metadata as md
import json
import pathlib
import platform
import sys
import sysconfig
import zipfile
from packaging.specifiers import SpecifierSet

dist = md.metadata("statqed-python-toolchain-probe")
version = platform.python_version()
wheel = next(pathlib.Path(sys.argv[1]).glob("*.whl"))
with zipfile.ZipFile(wheel) as archive:
    metadata_name = next(name for name in archive.namelist() if name.endswith(".dist-info/METADATA"))
    wheel_metadata = archive.read(metadata_name).decode("utf-8")
requires_python = dist["Requires-Python"]
payload = {
    "python": sys.version,
    "implementation": platform.python_implementation(),
    "executable": sys.executable,
    "soabi": sysconfig.get_config_var("SOABI"),
    "platform": sysconfig.get_platform(),
    "requires_python": requires_python,
    "requires_python_accepts_runtime": SpecifierSet(requires_python).contains(version),
    "distribution_version": md.version("statqed-python-toolchain-probe"),
    "tool_versions": {
        name: md.version(name)
        for name in ("build", "hatchling", "packaging", "pip", "pytest")
    },
    "wheel": wheel.name,
    "wheel_sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
    "wheel_metadata_has_requires_python": "Requires-Python: >=3.11" in wheel_metadata,
}
print(json.dumps(payload, indent=2, sort_keys=True))
""",
        encoding="utf-8",
    )


def run_supported(role: str) -> None:
    version = VERSIONS[role]
    tag = version.replace(".", "-")
    work = TMP_ROOT / f"supported-{tag}"
    safe_remove(work)
    work.mkdir(parents=True)
    builder = work / "builder"
    installed = work / "installed"
    dist = work / "dist"
    dist.mkdir()
    python = managed_python(version)
    prefix = f"{role}-{tag}"
    offline_pip = {
        "PIP_FIND_LINKS": str(WHEELHOUSE),
        "PIP_NO_INDEX": "1",
    }
    if not WHEELHOUSE.is_dir():
        raise SystemExit("isolated wheelhouse is absent; run with --prepare first")

    run(f"{prefix}-python-version", [str(python), "--version"])
    run(
        f"{prefix}-builder-venv",
        [str(python), "-m", "venv", str(builder)],
    )
    builder_python = builder / "bin" / "python"
    run(
        f"{prefix}-locked-tools-install",
        [
            str(builder_python),
            "-m",
            "pip",
            "install",
            "--require-hashes",
            "--only-binary=:all:",
            "-r",
            str(LOCK),
        ],
        env_additions=offline_pip,
    )
    run(
        f"{prefix}-tool-versions",
        [
            str(builder_python),
            "-c",
            (
                "import importlib.metadata as m, json; "
                "print(json.dumps({n:m.version(n) for n in "
                "('pip','build','pytest','hatchling','packaging')}, sort_keys=True))"
            ),
        ],
    )
    run(f"{prefix}-pip-check-builder", [str(builder_python), "-m", "pip", "check"])
    run(
        f"{prefix}-build",
        [
            str(builder_python),
            "-m",
            "build",
            "--sdist",
            "--wheel",
            "--outdir",
            str(dist),
            str(ROOT),
        ],
        env_additions=offline_pip,
    )
    artifacts = sorted(dist.iterdir())
    if {path.suffix for path in artifacts} != {".gz", ".whl"}:
        raise SystemExit(f"unexpected build artifacts: {artifacts}")
    artifact_lines = [f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}" for path in artifacts]
    (LOG_ROOT / f"{prefix}-artifact-digests.stdout").write_text(
        "\n".join(artifact_lines) + "\n", encoding="utf-8"
    )
    (LOG_ROOT / f"{prefix}-artifact-digests.stderr").write_text("", encoding="utf-8")
    (LOG_ROOT / f"{prefix}-artifact-digests.command.json").write_text(
        json.dumps(
            {
                "name": f"{prefix}-artifact-digests",
                "started_at": now(),
                "ended_at": now(),
                "cwd": str(ROOT.relative_to(REPO)),
                "command": ["sha256", *[path.name for path in artifacts]],
                "environment_variables": COMMON_ENV,
                "exit_status": 0,
                "expected_exit_statuses": [0],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print("\n".join(artifact_lines))

    run(
        f"{prefix}-install-venv",
        [str(python), "-m", "venv", str(installed)],
    )
    installed_python = installed / "bin" / "python"
    run(
        f"{prefix}-locked-tools-install-isolated",
        [
            str(installed_python),
            "-m",
            "pip",
            "install",
            "--require-hashes",
            "--only-binary=:all:",
            "-r",
            str(LOCK),
        ],
        env_additions=offline_pip,
    )
    wheel = next(dist.glob("*.whl"))
    run(
        f"{prefix}-wheel-install",
        [str(installed_python), "-m", "pip", "install", "--no-deps", str(wheel)],
        env_additions=offline_pip,
    )
    run(f"{prefix}-pip-check-installed", [str(installed_python), "-m", "pip", "check"])
    run(
        f"{prefix}-pytest",
        [str(installed_python), "-m", "pytest", "-q"],
        env_additions={"PYTHONPATH": ""},
    )
    inspect_script = work / "inspect_runtime.py"
    write_runtime_script(inspect_script)
    run(
        f"{prefix}-metadata",
        [str(installed_python), str(inspect_script), str(dist)],
    )
    compose_probe_log(
        prefix,
        [
            f"{prefix}-python-version",
            f"{prefix}-tool-versions",
            f"{prefix}-pip-check-builder",
            f"{prefix}-build",
            f"{prefix}-artifact-digests",
            f"{prefix}-wheel-install",
            f"{prefix}-pip-check-installed",
            f"{prefix}-pytest",
            f"{prefix}-metadata",
        ],
    )


def run_rejection() -> int:
    version = VERSIONS["rejected"]
    tag = version.replace(".", "-")
    work = TMP_ROOT / f"rejected-{tag}"
    safe_remove(work)
    work.mkdir(parents=True)
    rejected = work / "venv"
    python = managed_python(version)
    prefix = f"rejected-{tag}"
    offline_pip = {
        "PIP_FIND_LINKS": str(WHEELHOUSE),
        "PIP_NO_INDEX": "1",
    }
    if not WHEELHOUSE.is_dir():
        raise SystemExit("isolated wheelhouse is absent; run with --prepare first")
    run(f"{prefix}-python-version", [str(python), "--version"])
    run(
        f"{prefix}-venv",
        [str(python), "-m", "venv", str(rejected)],
    )
    rejected_python = rejected / "bin" / "python"
    run(
        f"{prefix}-pin-pip",
        [str(rejected_python), "-m", "pip", "install", "pip==26.2"],
        env_additions=offline_pip,
    )
    dev_dist = TMP_ROOT / "supported-3-14-6" / "dist"
    wheel = next(dev_dist.glob("*.whl"), None)
    if wheel is None:
        run_supported("development")
        wheel = next(dev_dist.glob("*.whl"))
    completed = run(
        f"{prefix}-metadata-rejection",
        [str(rejected_python), "-m", "pip", "install", "--no-deps", str(wheel)],
        env_additions=offline_pip,
        expected={1},
    )
    compose_probe_log(
        prefix,
        [
            f"{prefix}-python-version",
            f"{prefix}-pin-pip",
            f"{prefix}-metadata-rejection",
        ],
    )
    return completed.returncode


def environment() -> None:
    run("host-uname", ["uname", "-a"])
    run("host-os-release", ["sed", "-n", "1,16p", "/etc/os-release"])
    run("host-locale", ["locale"])
    run(
        "prototype-input-digests",
        [
            "sha256sum",
            "pyproject.toml",
            "probe-requirements.in",
            "probe-requirements.lock",
            "run_probes.py",
            "src/statqed_python_toolchain_probe/__init__.py",
            "tests/test_package.py",
        ],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--prepare",
        action="store_true",
        help="install exact managed runtimes and generate the hashed tool lock (network needed)",
    )
    parser.add_argument(
        "--probe",
        choices=("development", "floor", "rejected", "all"),
        default="all",
    )
    args = parser.parse_args()
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    if args.prepare:
        prepare()
    if not LOCK.is_file():
        raise SystemExit("probe-requirements.lock is absent; run with --prepare first")
    if args.probe in {"development", "all"}:
        run_supported("development")
    if args.probe in {"floor", "all"}:
        run_supported("floor")
    rejected_status = 0
    if args.probe in {"rejected", "all"}:
        rejected_status = run_rejection()
    environment()
    if args.probe == "rejected":
        return rejected_status
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
