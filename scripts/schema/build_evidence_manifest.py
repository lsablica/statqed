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


def historical_records(spec: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return and authenticate the immutable v1 and v2 historical records."""
    completion_policy = spec["historical_completion_manifest"]
    lifecycle_policy = spec["historical_lifecycle_manifest"]
    current = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if current.get("evidence_manifest_version") == lifecycle_policy["evidence_manifest_version"]:
        lifecycle = current
    elif current.get("evidence_manifest_version") == "statqed.sq0006-evidence.v3":
        lifecycle = current.get("historical_lifecycle")
    else:
        raise ValueError("unrecognized SQ-0006 evidence manifest version")
    if not isinstance(lifecycle, dict):
        raise ValueError("missing historical SQ-0006 v2 lifecycle manifest")
    if digest(canonical(lifecycle)) != lifecycle_policy["manifest_sha256"]:
        raise ValueError("historical SQ-0006 v2 lifecycle manifest drift")
    for field in (
        "evidence_manifest_version",
        "evidence_spec_sha256",
        "historical_completion_manifest_sha256",
        "historical_scientific_subject_digest",
        "immutable_scientific_subject_count",
        "immutable_scientific_subject_digest",
        "live_subject_count",
        "live_subject_digest",
    ):
        if lifecycle.get(field) != lifecycle_policy[field]:
            raise ValueError(f"historical SQ-0006 v2 {field} drift")
    historical = lifecycle.get("historical_completion")
    if not isinstance(historical, dict):
        raise ValueError("missing historical SQ-0006 completion manifest")
    if digest(canonical(historical)) != completion_policy["manifest_sha256"]:
        raise ValueError("historical SQ-0006 completion manifest drift")
    for field in (
        "evidence_manifest_version",
        "evidence_spec_sha256",
        "subject_count",
        "subject_digest",
        "scientific_subject_digest",
    ):
        if historical.get(field) != completion_policy[field]:
            raise ValueError(f"historical SQ-0006 v1 {field} drift")
    return historical, lifecycle


def collect() -> dict[str, Any]:
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    historical, historical_lifecycle = historical_records(spec)
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
    live_subject_bytes = canonical(subjects)
    immutable_policy = spec["historical_immutable_scientific_subjects"]
    excluded = set(immutable_policy["excluded_lifecycle_paths"])
    historical_immutable = [
        item for item in historical["subjects"]
        if not item["path"].startswith("work/reviews/")
        and not item["path"].startswith("docs/quality/")
        and item["path"] not in excluded
    ]
    if (
        len(historical_immutable) != immutable_policy["subject_count"]
        or digest(canonical(historical_immutable)) != immutable_policy["subject_digest"]
    ):
        raise ValueError("historical immutable scientific policy drift")
    immutable_scientific = [
        item for item in subjects
        if not item["path"].startswith("work/reviews/")
        and not item["path"].startswith("docs/quality/")
        and item["path"] not in excluded
    ]
    if len(immutable_scientific) != immutable_policy["subject_count"]:
        raise ValueError("immutable SQ-0006 scientific subject count drift")
    if immutable_scientific != historical_immutable:
        raise ValueError("immutable SQ-0006 scientific subjects differ from completion history")
    immutable_digest = digest(canonical(immutable_scientific))
    if immutable_digest != immutable_policy["subject_digest"]:
        raise ValueError("immutable SQ-0006 scientific subject drift")
    lifecycle_subjects = [item for item in subjects if item["path"] in excluded]
    if {item["path"] for item in lifecycle_subjects} != excluded:
        raise ValueError("missing lifecycle-maintenance subject")
    maintenance_paths = spec["maintenance_live_baseline_paths"]
    if maintenance_paths != sorted(maintenance_paths) or len(maintenance_paths) != len(set(maintenance_paths)):
        raise ValueError("invalid maintenance live baseline path policy")
    maintenance_live_baselines = []
    for relative in maintenance_paths:
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"missing maintenance live baseline: {relative}")
        maintenance_live_baselines.append(
            {"path": relative, "sha256": digest(path.read_bytes()), "size_bytes": path.stat().st_size}
        )
    return {
        "evidence_manifest_version": "statqed.sq0006-evidence.v3",
        "evidence_spec_sha256": digest(SPEC.read_bytes()),
        "historical_completion_manifest_sha256": spec["historical_completion_manifest"]["manifest_sha256"],
        "historical_scientific_subject_digest": spec["historical_completion_manifest"]["scientific_subject_digest"],
        "historical_completion": historical,
        "historical_lifecycle_manifest_sha256": spec["historical_lifecycle_manifest"]["manifest_sha256"],
        "historical_lifecycle": historical_lifecycle,
        "immutable_scientific_subject_count": len(immutable_scientific),
        "immutable_scientific_subject_digest": immutable_digest,
        "lifecycle_subject_digest": digest(canonical(lifecycle_subjects)),
        "maintenance_live_baseline_digest": digest(canonical(maintenance_live_baselines)),
        "maintenance_live_baselines": maintenance_live_baselines,
        "live_subject_digest": digest(live_subject_bytes),
        "live_subject_count": len(subjects),
        "live_subjects": subjects,
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
    print(
        "wrote SQ-0006 evidence manifest: "
        f"{manifest['live_subject_count']} live subjects, "
        f"historical science {manifest['historical_scientific_subject_digest']}, "
        f"historical lifecycle {manifest['historical_lifecycle_manifest_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
