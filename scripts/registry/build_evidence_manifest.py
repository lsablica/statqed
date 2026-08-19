#!/usr/bin/env python3
"""Build the deterministic, content-addressed SQ-0007 evidence manifest."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import subprocess
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = Path("conformance/registry/evidence/evidence-spec.json")
MANIFEST_PATH = Path("conformance/registry/evidence/evidence-manifest.json")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encoded(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


def matches(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def subjects(root: Path, patterns: list[str], ignored: list[str]) -> list[dict[str, Any]]:
    found = []
    ignored_set = set(ignored) | {".git", ".codex"}
    for directory, names, files in os.walk(root):
        names[:] = sorted(name for name in names if name not in ignored_set)
        for filename in sorted(files):
            path = Path(directory) / filename
            if path.is_symlink():
                continue
            relative = path.relative_to(root).as_posix()
            if relative == MANIFEST_PATH.as_posix():
                continue
            if matches(relative, patterns):
                data = path.read_bytes()
                found.append({"bytes": len(data), "path": relative, "sha256": sha(data)})
    return sorted(found, key=lambda item: item["path"])


def aggregate(items: list[dict[str, Any]]) -> str:
    lines = [f"{item['path']}\0{item['sha256']}\0{item['bytes']}\n" for item in items]
    return sha("".join(lines).encode())


def git_paths(root: Path, base: str) -> list[str]:
    """Return the task-local path set relative to the reviewed predecessor tip."""
    if not (root / ".git").exists():
        retained = root / MANIFEST_PATH
        if retained.is_file():
            value = json.loads(retained.read_text(encoding="utf-8"))
            paths = value.get("task_local_changed_paths")
            if isinstance(paths, list) and all(isinstance(path, str) for path in paths):
                return paths
        return []
    completed = subprocess.run(
        ["git", "diff", "--name-only", base, "--"],
        cwd=root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return sorted(set(completed.stdout.splitlines() + untracked.stdout.splitlines()))


def review_projection(root: Path, path: str) -> dict[str, str] | None:
    target = root / path
    if not target.is_file():
        return None
    lines = []
    for line in target.read_text(encoding="utf-8").splitlines():
        if line.startswith("- Evidence manifest SHA-256:"):
            lines.append("- Evidence manifest SHA-256: <masked-nonrecursive-binding>")
        else:
            lines.append(line)
    return {"path": path, "projection_sha256": sha(("\n".join(lines) + "\n").encode())}


def build(root: Path = ROOT) -> dict[str, Any]:
    spec_bytes = (root / SPEC_PATH).read_bytes()
    spec = json.loads(spec_bytes)
    all_subjects = subjects(root, spec["subject_patterns"], spec["ignored_components"])
    scientific = subjects(root, spec["scientific_subject_patterns"], spec["ignored_components"])
    task_local_paths = git_paths(root, spec["verified_predecessor_tip"])
    return {
        "schema": "statqed.sq0007-evidence.v2",
        "evidence_spec_sha256": sha(spec_bytes),
        "subjects": all_subjects,
        "subject_count": len(all_subjects),
        "subject_digest": aggregate(all_subjects),
        "scientific_subjects": scientific,
        "scientific_subject_count": len(scientific),
        "scientific_subject_digest": aggregate(scientific),
        "review_projection": review_projection(root, spec["review_path"]),
        "historical_launch_base": spec["historical_launch_base"],
        "historical_task_commits": spec["historical_task_commits"],
        "verified_predecessor_chain": spec["verified_predecessor_chain"],
        "verified_predecessor_tip": spec["verified_predecessor_tip"],
        "task_local_changed_paths": task_local_paths,
        "task_local_changed_paths_digest": sha(("\n".join(task_local_paths) + "\n").encode()),
        "predecessor_bindings": spec["predecessor_bindings"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = encoded(build())
    target = ROOT / MANIFEST_PATH
    if args.check:
        if not target.is_file() or target.read_bytes() != output:
            print("SQ-0007 evidence manifest drift")
            return 1
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(output)
    manifest = json.loads(output)
    print(f"SQ-0007 evidence manifest verified: {manifest['subject_count']} subjects; scientific digest {manifest['scientific_subject_digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
