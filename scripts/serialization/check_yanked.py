#!/usr/bin/env python3
"""Record or check official crates.io yanked state for the SQ-0005 lock."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import tomllib
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


REPOSITORY = Path(__file__).resolve().parents[2]
PROTOTYPE = REPOSITORY / "schemas/prototypes/rust-cbor"
LOCK = PROTOTYPE / "Cargo.lock"
OUTPUT = PROTOTYPE / "evidence/crates-io-yanked.json"
API_ROOT = "https://crates.io/api/v1/crates"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def packages() -> list[dict[str, str]]:
    with LOCK.open("rb") as stream:
        lock = tomllib.load(stream)
    result = []
    for package in lock["package"]:
        source = package.get("source", "")
        if not source.startswith("registry+"):
            continue
        result.append(
            {
                "checksum": package["checksum"],
                "name": package["name"],
                "version": package["version"],
            }
        )
    return sorted(result, key=lambda item: (item["name"], item["version"]))


def query(package: dict[str, str]) -> dict[str, Any]:
    locator = f"{API_ROOT}/{quote(package['name'], safe='')}/{quote(package['version'], safe='')}"
    request = Request(
        locator,
        headers={"User-Agent": "StatQED-SQ-0005-evidence/1 (+https://github.com/lsablica/statqed)"},
    )
    with urlopen(request, timeout=30) as response:
        document = json.load(response)
    version = document.get("version")
    if not isinstance(version, dict):
        raise RuntimeError(f"missing crates.io version record: {package['name']}")
    if version.get("num") != package["version"]:
        raise RuntimeError(f"crates.io version mismatch: {package['name']}")
    if version.get("checksum") != package["checksum"]:
        raise RuntimeError(f"crates.io checksum mismatch: {package['name']}")
    if type(version.get("yanked")) is not bool:
        raise RuntimeError(f"missing crates.io yanked state: {package['name']}")
    return {
        **package,
        "locator": locator,
        "yanked": version["yanked"],
    }


def live_records() -> list[dict[str, Any]]:
    return [query(package) for package in packages()]


def validate(records: list[dict[str, Any]]) -> None:
    expected = packages()
    observed = [
        {key: item.get(key) for key in ("checksum", "name", "version")}
        for item in records
    ]
    if observed != expected:
        raise RuntimeError("retained crates.io package set or checksum is stale")
    yanked = [f"{item['name']} {item['version']}" for item in records if item["yanked"]]
    if yanked:
        raise RuntimeError("locked crates are now yanked: " + ", ".join(yanked))


def canonical(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--observed-at")
    arguments = parser.parse_args()
    try:
        if arguments.write or arguments.live:
            records = live_records()
            validate(records)
            if arguments.live:
                print(f"crates.io live yanked check passed: {len(records)} exact packages")
                return 0
            if not arguments.observed_at:
                raise RuntimeError("--write requires --observed-at")
            document = {
                "cargo_lock_sha256": sha256(LOCK),
                "limitations": [
                    "This is a point-in-time crates.io registry observation, not a maintenance or security guarantee.",
                    "A later yanked state does not rewrite this retained observation; live CI and release checks must fail closed.",
                ],
                "observed_at": arguments.observed_at,
                "packages": records,
                "schema_id": "statqed.crates-io-yanked-observation.v1",
                "source": "official crates.io version API",
            }
            OUTPUT.parent.mkdir(parents=True, exist_ok=True)
            OUTPUT.write_bytes(canonical(document))
            print(f"wrote crates.io yanked evidence: {len(records)} exact packages")
            return 0

        with OUTPUT.open(encoding="utf-8") as stream:
            retained = json.load(stream)
        if retained.get("cargo_lock_sha256") != sha256(LOCK):
            raise RuntimeError("retained crates.io observation has stale Cargo.lock hash")
        validate(retained.get("packages", []))
        print(
            "retained crates.io yanked evidence verified: "
            f"{len(retained['packages'])} exact packages"
        )
        return 0
    except (HTTPError, KeyError, OSError, RuntimeError, TypeError, URLError, json.JSONDecodeError) as error:
        print(f"crates.io yanked check failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
