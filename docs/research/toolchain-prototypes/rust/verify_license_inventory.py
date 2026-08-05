#!/usr/bin/env python3
"""Generate or verify the reviewed Rust dependency-license inventory."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tomllib
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package_key(package: dict[str, Any]) -> tuple[str, str, str | None]:
    return package["name"], package["version"], package.get("source")


def build_inventory(lock_path: Path, metadata_path: Path) -> dict[str, Any]:
    with lock_path.open("rb") as stream:
        lock = tomllib.load(stream)
    with metadata_path.open(encoding="utf-8") as stream:
        metadata = json.load(stream)

    lock_packages = {package_key(package): package for package in lock["package"]}
    metadata_packages = {
        package_key(package): package for package in metadata["packages"]
    }
    missing_metadata = sorted(set(lock_packages) - set(metadata_packages))
    unexpected_metadata = sorted(set(metadata_packages) - set(lock_packages))
    if missing_metadata or unexpected_metadata:
        raise ValueError(
            "Cargo.lock and cargo metadata package sets differ: "
            f"missing={missing_metadata!r}; unexpected={unexpected_metadata!r}"
        )

    packages: list[dict[str, Any]] = []
    for key in sorted(lock_packages, key=lambda item: (item[0], item[1], item[2] or "")):
        locked = lock_packages[key]
        observed = metadata_packages[key]
        if locked.get("source") is not None and not observed.get("license"):
            raise ValueError(f"registry package lacks license metadata: {key!r}")
        packages.append(
            {
                "name": observed["name"],
                "version": observed["version"],
                "source": observed.get("source"),
                "checksum": locked.get("checksum"),
                "license": observed.get("license"),
                "rust_version": observed.get("rust_version"),
                "repository": observed.get("repository"),
            }
        )

    registry_count = sum(package["source"] is not None for package in packages)
    return {
        "schema_version": 1,
        "cargo_lock_sha256": sha256(lock_path),
        "package_count": len(packages),
        "registry_package_count": registry_count,
        "prototype_local_package_count": len(packages) - registry_count,
        "packages": packages,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lock", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--write", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    actual = build_inventory(args.lock, args.metadata)
    rendered = json.dumps(actual, indent=2, sort_keys=True) + "\n"
    if args.write:
        args.inventory.write_text(rendered, encoding="utf-8")
        return 0
    if not args.inventory.is_file():
        print(f"missing reviewed inventory: {args.inventory}", file=sys.stderr)
        return 1
    expected = args.inventory.read_text(encoding="utf-8")
    if expected != rendered:
        print(
            "reviewed dependency-license inventory differs from exact Cargo.lock "
            "and cargo metadata",
            file=sys.stderr,
        )
        return 1
    print(
        "verified dependency-license inventory: "
        f"{actual['package_count']} packages "
        f"({actual['registry_package_count']} registry + "
        f"{actual['prototype_local_package_count']} local)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
