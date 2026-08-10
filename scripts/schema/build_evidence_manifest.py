#!/usr/bin/env python3
"""Build the deterministic SQ-0006 content-addressed evidence manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "conformance/schema-v0/evidence/evidence-spec.json"
MANIFEST = ROOT / "conformance/schema-v0/evidence/evidence-manifest.json"


def canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def collect() -> dict[str, Any]:
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    paths: set[Path] = set()
    for pattern in spec["subject_patterns"]:
        for path in ROOT.glob(pattern):
            if path.is_file() and path != MANIFEST and "__pycache__" not in path.parts:
                paths.add(path)
    subjects = [
        {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": digest(path.read_bytes()),
            "size_bytes": path.stat().st_size,
        }
        for path in sorted(paths)
    ]
    if not subjects:
        raise ValueError("empty evidence subject set")
    subject_bytes = canonical(subjects)
    scientific = [
        item for item in subjects
        if not item["path"].startswith("work/reviews/")
        and not item["path"].startswith("docs/quality/")
    ]
    return {
        "evidence_manifest_version": "statqed.sq0006-evidence.v1",
        "evidence_spec_sha256": digest(SPEC.read_bytes()),
        "scientific_subject_digest": digest(canonical(scientific)),
        "subject_digest": digest(subject_bytes),
        "subject_count": len(subjects),
        "subjects": subjects,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = canonical(collect())
    if args.check:
        if not MANIFEST.is_file() or MANIFEST.read_bytes() != expected:
            print("SQ-0006 evidence manifest drift", file=sys.stderr)
            return 1
        print("SQ-0006 evidence manifest verified byte-identical")
        return 0
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_bytes(expected)
    manifest = json.loads(expected)
    print(f"wrote SQ-0006 evidence manifest: {manifest['subject_count']} subjects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
