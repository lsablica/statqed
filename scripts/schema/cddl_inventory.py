#!/usr/bin/env python3
"""Reproduce the cddl 0.10.6 lock-bound dependency/license inventory."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tomllib
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "source-audits/schema/cddl-dependency-inventory.json"


def canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode()


def package_toml(archive: Path) -> dict[str, Any]:
    with tarfile.open(archive, "r:gz") as package:
        members = [member for member in package.getmembers() if member.name.count("/") == 1 and member.name.endswith("/Cargo.toml")]
        if len(members) != 1:
            raise ValueError(f"Cargo.toml missing or ambiguous: {archive}")
        extracted = package.extractfile(members[0])
        if extracted is None:
            raise ValueError(f"Cargo.toml unreadable: {archive}")
        return tomllib.loads(extracted.read().decode("utf-8"))


def direct_roles(root_manifest: dict[str, Any]) -> dict[str, set[str]]:
    roles: dict[str, set[str]] = {}
    for table, role in (("dependencies", "normal"), ("build-dependencies", "build"), ("dev-dependencies", "development")):
        for name, value in root_manifest.get(table, {}).items():
            actual = value.get("package", name) if isinstance(value, dict) else name
            roles.setdefault(actual, set()).add(role)
    for target in root_manifest.get("target", {}).values():
        if isinstance(target, dict):
            for table, role in (("dependencies", "normal"), ("build-dependencies", "build"), ("dev-dependencies", "development")):
                for name, value in target.get(table, {}).items():
                    actual = value.get("package", name) if isinstance(value, dict) else name
                    roles.setdefault(actual, set()).add(role)
    return roles


def normalize_license(value: str) -> str:
    aliases = {
        "Apache-2.0 / MIT": "Apache-2.0 OR MIT",
        "Apache-2.0/MIT": "Apache-2.0 OR MIT",
        "MIT/Apache-2.0": "MIT OR Apache-2.0",
        "Unlicense/MIT": "Unlicense OR MIT",
    }
    return aliases.get(value, value)


def build(cargo_home: Path, manifest_path: Path) -> bytes:
    lock_path = manifest_path.with_name("Cargo.lock")
    lock_bytes = lock_path.read_bytes()
    lock = tomllib.loads(lock_bytes.decode("utf-8"))
    env = dict(os.environ)
    env.update({"CARGO_HOME": str(cargo_home), "CARGO_NET_OFFLINE": "true"})
    completed = subprocess.run(
        [
            "cargo", "+1.97.1", "metadata", "--locked", "--offline",
            "--format-version", "1", "--manifest-path", str(manifest_path),
        ],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, check=False,
        timeout=60,
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr.decode("utf-8", "replace"))
    metadata = json.loads(completed.stdout)
    features = {
        node["id"].split("#")[-1]: sorted(node.get("features", []))
        for node in metadata["resolve"]["nodes"]
    }
    root_manifest = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    roles = direct_roles(root_manifest)
    cache_dirs = list((cargo_home / "registry/cache").glob("*"))
    if len(cache_dirs) != 1:
        raise ValueError("expected one isolated crates.io cache")
    cache = cache_dirs[0]
    entries = []
    for package in sorted(lock["package"], key=lambda item: (item["name"], item["version"], item.get("source", ""))):
        name, version = package["name"], package["version"]
        if name == "cddl" and version == "0.10.6" and "source" not in package:
            package_document = root_manifest["package"]
            license_expression = package_document.get("license")
            role = ["root"]
        else:
            archive = cache / f"{name}-{version}.crate"
            if not archive.is_file():
                raise FileNotFoundError(archive)
            package_document = package_toml(archive)["package"]
            license_expression = package_document.get("license") or package_document.get("license-file")
            role = sorted(roles.get(name, {"transitive"}))
        if not license_expression:
            raise ValueError(f"missing license metadata: {name} {version}")
        package_id_suffix = f"{name}@{version}"
        entries.append({
            "name": name,
            "version": version,
            "source": package.get("source", "packaged-root"),
            "checksum": package.get("checksum"),
            "declared_license": license_expression,
            "license_expression": normalize_license(license_expression),
            "roles": role,
            "resolved_features": features.get(package_id_suffix, []),
        })
    document = {
        "inventory_version": "statqed.sq0006-cddl-inventory.v1",
        "component": "cddl 0.10.6 untrusted development/CI validator",
        "cargo_lock_sha256": hashlib.sha256(lock_bytes).hexdigest(),
        "package_count": len(entries),
        "platform_observation": "cargo metadata default host graph on Linux x86_64; lock retains all target packages",
        "feature_limitation": "Cargo.lock does not encode feature activation; resolved_features records this exact default metadata run, while target-only locked packages may be absent from its active node graph.",
        "entries": entries,
    }
    return canonical(document)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cargo-home", type=Path, required=True)
    parser.add_argument("--manifest-path", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = build(args.cargo_home, args.manifest_path)
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_bytes() != expected:
            print("cddl dependency inventory drift")
            return 1
        print("cddl dependency inventory reproduced")
        return 0
    OUTPUT.write_bytes(expected)
    print(f"wrote cddl dependency inventory ({json.loads(expected)['package_count']} packages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
