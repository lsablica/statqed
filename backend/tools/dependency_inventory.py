#!/usr/bin/env python3
"""Generate or verify the normalized SQ-0004 dependency/license inventory."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean_environment(temporary: Path) -> dict[str, str]:
    cargo = shutil.which("cargo")
    if cargo is None:
        raise RuntimeError("cargo proxy is unavailable")
    paths = {
        "HOME": temporary / "home",
        "CARGO_HOME": temporary / "cargo-home",
        "CARGO_TARGET_DIR": temporary / "target",
        "XDG_CONFIG_HOME": temporary / "xdg-config",
        "XDG_CACHE_HOME": temporary / "xdg-cache",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return {
        **{key: str(value) for key, value in paths.items()},
        "RUSTUP_HOME": os.environ.get("RUSTUP_HOME", str(Path.home() / ".rustup")),
        "PATH": os.pathsep.join([str(Path(cargo).resolve().parent), "/usr/bin", "/bin"]),
        "CARGO_NET_OFFLINE": "true",
        "CARGO_TERM_COLOR": "never",
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "TZ": "UTC",
    }


def cargo_metadata() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="statqed-inventory-") as temporary_name:
        environment = clean_environment(Path(temporary_name))
        observed = subprocess.run(
            [
                "cargo",
                "+1.97.1",
                "metadata",
                "--locked",
                "--offline",
                "--format-version",
                "1",
            ],
            cwd=ROOT,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120,
            check=False,
        )
    if observed.returncode != 0:
        raise RuntimeError(f"cargo metadata failed: {observed.stderr.strip()}")
    return json.loads(observed.stdout)


def build_inventory() -> dict[str, Any]:
    metadata = cargo_metadata()
    with (ROOT / "Cargo.lock").open("rb") as stream:
        lock = tomllib.load(stream)
    locked = {(item["name"], item["version"]): item for item in lock.get("package", [])}
    packages = {(item["name"], item["version"]): item for item in metadata["packages"]}
    if set(locked) != set(packages):
        raise RuntimeError("Cargo.lock and cargo metadata package sets differ")

    resolve = metadata.get("resolve") or {}
    nodes = {item["id"]: item for item in resolve.get("nodes", [])}
    workspace_members = set(metadata.get("workspace_members", []))
    depended_on: dict[str, set[str]] = {item["id"]: set() for item in metadata["packages"]}
    dependency_roles: dict[str, set[str]] = {item["id"]: set() for item in metadata["packages"]}
    for node in nodes.values():
        for dependency in node.get("deps", []):
            dependency_id = dependency["pkg"]
            depended_on.setdefault(dependency_id, set()).add(node["id"])
            for kind in dependency.get("dep_kinds", []):
                dependency_roles.setdefault(dependency_id, set()).add(kind.get("kind") or "normal")

    records = []
    for key in sorted(packages):
        package = packages[key]
        locked_package = locked[key]
        package_id = package["id"]
        roles = set(dependency_roles.get(package_id, set()))
        if package_id in workspace_members:
            roles.add("workspace")
        source = package.get("source")
        if source is None:
            manifest_path = Path(package["manifest_path"])
            source = f"path:{manifest_path.parent.relative_to(ROOT).as_posix()}"
        records.append(
            {
                "name": package["name"],
                "version": package["version"],
                "source": source,
                "checksum": locked_package.get("checksum"),
                "license": package.get("license"),
                "features": sorted(nodes.get(package_id, {}).get("features", [])),
                "roles": sorted(roles),
                "depended_on_by": sorted(
                    next(
                        candidate["name"]
                        for candidate in metadata["packages"]
                        if candidate["id"] == depender
                    )
                    for depender in depended_on.get(package_id, set())
                ),
            }
        )
    if any(record["license"] in (None, "") for record in records):
        raise RuntimeError("dependency inventory contains a missing license")
    return {
        "schema_version": 1,
        "cargo_lock_sha256": sha256(ROOT / "Cargo.lock"),
        "package_count": len(records),
        "registry_package_count": sum(
            str(record["source"]).startswith("registry+") for record in records
        ),
        "packages": records,
        "limitations": [
            "License metadata is not a substitute for reviewing distributed license texts.",
            "The SQ-0004 graph has no third-party crate dependency; Rust tooling and the operating system are outside this inventory.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", type=Path, default=ROOT / "evidence/dependency-license-inventory.json")
    parser.add_argument("--write", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        inventory = build_inventory()
    except (OSError, RuntimeError, subprocess.TimeoutExpired, tomllib.TOMLDecodeError) as error:
        print(f"dependency inventory failed: {error}", file=sys.stderr)
        return 1
    rendered = json.dumps(inventory, indent=2, sort_keys=True) + "\n"
    if args.write:
        args.inventory.parent.mkdir(parents=True, exist_ok=True)
        args.inventory.write_text(rendered, encoding="utf-8")
        print(f"wrote dependency inventory: {inventory['package_count']} packages")
        return 0
    if not args.inventory.is_file() or args.inventory.read_text(encoding="utf-8") != rendered:
        print("retained dependency inventory differs from exact Cargo.lock and metadata", file=sys.stderr)
        return 1
    print(
        "verified dependency inventory: "
        f"{inventory['package_count']} packages, {inventory['registry_package_count']} registry"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
