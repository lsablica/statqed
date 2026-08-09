#!/usr/bin/env python3
"""Generate the lock-bound SQ-0005 Rust prototype dependency inventory."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tomllib
from typing import Any


REPOSITORY = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = REPOSITORY / "schemas/prototypes/rust-cbor/Cargo.toml"
DEFAULT_OUTPUT = (
    REPOSITORY
    / "schemas/prototypes/rust-cbor/evidence/dependency-license-inventory.json"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(command: list[str]) -> str:
    completed = subprocess.run(
        command,
        cwd=REPOSITORY,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        sys.stderr.write(completed.stderr)
        raise SystemExit(completed.returncode)
    return completed.stdout.strip()


def relative(path: str) -> str:
    candidate = Path(path).resolve()
    try:
        return candidate.relative_to(REPOSITORY).as_posix()
    except ValueError:
        return "external:" + candidate.name


def build_inventory(manifest: Path) -> dict[str, Any]:
    manifest = manifest.resolve()
    lock = manifest.parent / "Cargo.lock"
    metadata_command = [
        "cargo",
        "+1.97.1",
        "metadata",
        "--format-version",
        "1",
        "--locked",
        "--offline",
        "--manifest-path",
        str(manifest),
    ]
    metadata = json.loads(run(metadata_command))
    lock_data = tomllib.loads(lock.read_text(encoding="utf-8"))
    lock_packages = {
        (item["name"], item["version"], item.get("source")): item
        for item in lock_data["package"]
    }
    workspace_ids = set(metadata["workspace_members"])
    resolve_features = {
        node["id"]: sorted(node.get("features", []))
        for node in metadata["resolve"]["nodes"]
    }
    workspace_packages = {
        package["id"]: package
        for package in metadata["packages"]
        if package["id"] in workspace_ids
    }
    direct_roles: dict[tuple[str, str | None], set[str]] = {}
    for package in workspace_packages.values():
        for dependency in package["dependencies"]:
            role = dependency.get("kind") or "normal"
            key = (dependency["name"], dependency.get("source"))
            direct_roles.setdefault(key, set()).add(role)

    packages: list[dict[str, Any]] = []
    for package in metadata["packages"]:
        if package["id"] in workspace_ids:
            continue
        lock_item = lock_packages.get(
            (package["name"], package["version"], package.get("source"))
        )
        if lock_item is None:
            raise SystemExit(
                f"metadata package missing from Cargo.lock: {package['name']} "
                f"{package['version']}"
            )
        roles = direct_roles.get((package["name"], package.get("source")))
        packages.append(
            {
                "checksum": lock_item.get("checksum"),
                "features": resolve_features.get(package["id"], []),
                "license": package.get("license"),
                "license_file": (
                    relative(package["license_file"])
                    if package.get("license_file")
                    else None
                ),
                "name": package["name"],
                "role": sorted(roles) if roles else ["transitive"],
                "source": package.get("source"),
                "version": package["version"],
            }
        )
    packages.sort(key=lambda item: (item["name"], item["version"]))
    missing = [
        f"{item['name']} {item['version']}"
        for item in packages
        if not item["license"] and not item["license_file"]
    ]
    if missing:
        raise SystemExit("missing dependency license metadata: " + ", ".join(missing))
    return {
        "cargo_lock_sha256": sha256(lock),
        "cargo_version": run(["cargo", "+1.97.1", "--version"]),
        "command": "cargo +1.97.1 metadata --format-version 1 --locked "
        "--offline --manifest-path schemas/prototypes/rust-cbor/Cargo.toml",
        "dependency_count": len(packages),
        "inventory_schema": "statqed.serialization-dependencies.v1",
        "manifest": relative(str(manifest)),
        "packages": packages,
        "rustc_version": run(["rustc", "+1.97.1", "--version", "--verbose"]),
        "scope": "Experimental SQ-0005 Rust prototype only",
    }


def canonical_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    rendered = canonical_bytes(build_inventory(arguments.manifest))
    if arguments.check:
        if not arguments.output.is_file():
            print(f"missing inventory: {relative(str(arguments.output))}", file=sys.stderr)
            return 1
        if arguments.output.read_bytes() != rendered:
            print(f"stale inventory: {relative(str(arguments.output))}", file=sys.stderr)
            return 1
        print("SQ-0005 dependency inventory verified")
        return 0
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_bytes(rendered)
    print(relative(str(arguments.output)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
