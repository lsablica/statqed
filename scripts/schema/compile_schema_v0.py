#!/usr/bin/env python3
"""Deterministically concatenate the published-syntax CDDL sources."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import re


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "schemas/v0/manifest.json"
SCHEMA_ID = "statqed.foundation-structural.v0"
SCHEMA_VERSION = 0


def compiled_bytes() -> tuple[Path, bytes]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if (manifest.get("schema_id"), manifest.get("schema_version")) != (SCHEMA_ID, SCHEMA_VERSION):
        raise ValueError("schema identifier/version pair mismatch")
    sources = manifest["source_order"]
    if not sources or len(sources) != len(set(sources)):
        raise ValueError("source_order must be nonempty and unique")
    chunks: list[bytes] = []
    for relative in sources:
        relative_path = Path(relative)
        source = ROOT / relative_path
        if relative_path.is_absolute() or ".." in relative_path.parts or source.is_symlink():
            raise ValueError(f"unsafe source path: {relative}")
        data = source.read_bytes()
        if b"\r" in data or not data.endswith(b"\n") or data.endswith(b"\n\n"):
            raise ValueError(f"source newline policy failed: {relative}")
        code = b"\n".join(line.split(b";", 1)[0] for line in data.splitlines())
        if re.search(rb"\b(import|module)\b", code, re.IGNORECASE):
            raise ValueError(f"draft module/import syntax is prohibited: {relative}")
        data.decode("utf-8", "strict")
        chunks.append(data)
    compiled = b"".join(chunks)
    if SCHEMA_ID.encode() not in compiled or b'schema-version-v0 = 0' not in compiled:
        raise ValueError("compiled CDDL does not bind the exact schema identity/version pair")
    first_rule = re.search(rb"(?m)^([a-z][a-z0-9-]*)\s*=", compiled)
    if first_rule is None or first_rule.group(1).decode() != manifest["entry_rule"]:
        raise ValueError("compiled CDDL first rule does not match entry_rule")
    output_relative = Path(manifest["compiled_output"])
    output = ROOT / output_relative
    if output_relative.is_absolute() or ".." in output_relative.parts or output.is_symlink():
        raise ValueError("unsafe compiled output path")
    return output, compiled


def manifest_with_hashes(compiled: bytes) -> bytes:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["source_sha256"] = {
        relative: hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        for relative in manifest["source_order"]
    }
    manifest["compiled_sha256"] = hashlib.sha256(compiled).hexdigest()
    manifest["compiled_size_bytes"] = len(compiled)
    return (json.dumps(manifest, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output, expected = compiled_bytes()
    expected_manifest = manifest_with_hashes(expected)
    if args.check:
        if not output.is_file() or output.read_bytes() != expected or MANIFEST.read_bytes() != expected_manifest:
            print(f"schema-v0 compiled CDDL drift: {output.relative_to(ROOT)}", file=sys.stderr)
            return 1
        print("SQ-0006 compiled CDDL verified byte-identical")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(expected)
    MANIFEST.write_bytes(expected_manifest)
    print(f"wrote {output.relative_to(ROOT)} ({len(expected)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
