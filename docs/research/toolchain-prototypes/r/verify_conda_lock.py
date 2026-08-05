#!/usr/bin/env python3
"""Verify, copy, and compare artifacts named by an explicit conda SHA lock."""

from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path
from urllib.parse import unquote, urlparse


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_lock(path: Path) -> list[tuple[str, str, str]]:
    artifacts: list[tuple[str, str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or line.startswith("@EXPLICIT"):
            continue
        url, separator, expected = line.rpartition("#")
        if not separator or len(expected) != 64:
            raise ValueError(f"explicit lock entry lacks SHA-256: {line}")
        filename = Path(unquote(urlparse(url).path)).name
        artifacts.append((filename, url, expected))
    if not artifacts:
        raise ValueError(f"empty or non-explicit conda lock: {path}")
    return artifacts


def prepare(lock: Path, cache: Path, destination: Path, local_lock: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    lines = ["@EXPLICIT"]
    for filename, _, expected in parse_lock(lock):
        matches = list(cache.rglob(filename))
        if len(matches) != 1:
            raise FileNotFoundError(
                f"expected one locked conda archive {filename}, found {len(matches)}"
            )
        source = matches[0]
        observed = sha256(source)
        if observed != expected:
            raise ValueError(
                f"locked conda archive digest mismatch for {filename}: {observed} != {expected}"
            )
        copied = destination / filename
        shutil.copy2(source, copied)
        if sha256(copied) != expected:
            raise ValueError(f"copied conda archive digest mismatch for {filename}")
        lines.append(f"{copied.resolve().as_uri()}#{expected}")
    local_lock.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"verified and copied {len(lines) - 1} locked conda archives")


def compare(expected_path: Path, observed_path: Path) -> None:
    expected = {(name, digest) for name, _, digest in parse_lock(expected_path)}
    observed = {(name, digest) for name, _, digest in parse_lock(observed_path)}
    if expected != observed:
        missing = sorted(expected - observed)
        unexpected = sorted(observed - expected)
        raise ValueError(
            f"normalized conda lock mismatch; missing={missing}, unexpected={unexpected}"
        )
    print(f"normalized conda lock matches {len(expected)} filename/SHA-256 pairs")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare", action="store_true")
    mode.add_argument("--compare", action="store_true")
    parser.add_argument("--lock", type=Path, required=True)
    parser.add_argument("--cache", type=Path)
    parser.add_argument("--destination", type=Path)
    parser.add_argument("--local-lock", type=Path)
    parser.add_argument("--observed", type=Path)
    args = parser.parse_args()
    if args.prepare:
        if not all((args.cache, args.destination, args.local_lock)):
            parser.error("--prepare requires --cache, --destination, and --local-lock")
        prepare(args.lock, args.cache, args.destination, args.local_lock)
    else:
        if args.observed is None:
            parser.error("--compare requires --observed")
        compare(args.lock, args.observed)


if __name__ == "__main__":
    main()
