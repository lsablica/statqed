#!/usr/bin/env python3
"""Generate or verify the content manifest for the SQ-0005 source audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


REPOSITORY = Path(__file__).resolve().parents[2]
ROOT = REPOSITORY / "source-audits/encoding"
OUTPUT = ROOT / "manifest.json"


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def build() -> dict[str, object]:
    files = []
    tree = hashlib.sha256()
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.is_symlink() or path == OUTPUT:
            continue
        relative = path.relative_to(REPOSITORY).as_posix()
        content = path.read_bytes()
        encoded_path = relative.encode("utf-8")
        tree.update(len(encoded_path).to_bytes(8, "big"))
        tree.update(encoded_path)
        tree.update(len(content).to_bytes(8, "big"))
        tree.update(content)
        files.append(
            {
                "bytes": len(content),
                "path": relative,
                "sha256": sha256(content),
            }
        )
    return {
        "file_count": len(files),
        "files": files,
        "retrieval_date": "2026-08-09",
        "schema_id": "statqed.encoding-source-audit-manifest.v1",
        "tree_hash_algorithm": "sha256(u64be(path_len)||path||u64be(content_len)||content for sorted paths)",
        "tree_sha256": tree.hexdigest(),
    }


def canonical(value: dict[str, object]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    arguments = parser.parse_args()
    rendered = canonical(build())
    if arguments.write:
        OUTPUT.write_bytes(rendered)
        print(OUTPUT.relative_to(REPOSITORY).as_posix())
        return 0
    if not OUTPUT.is_file() or OUTPUT.read_bytes() != rendered:
        print("SQ-0005 source-audit manifest is stale", file=sys.stderr)
        return 1
    document = json.loads(rendered)
    print(
        "SQ-0005 source audit verified: "
        f"{document['file_count']} files, tree {document['tree_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
