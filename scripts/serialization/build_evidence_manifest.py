#!/usr/bin/env python3
"""Generate the deterministic content manifest for SQ-0005 evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
from typing import Any


REPOSITORY = Path(__file__).resolve().parents[2]
SPEC = REPOSITORY / "conformance/prototypes/evidence/evidence-spec.json"
OUTPUT = REPOSITORY / "conformance/prototypes/evidence/evidence-manifest.json"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def relative(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise RuntimeError(f"unsafe evidence path: {value}")
    return path


def repository_path(value: str) -> Path:
    return REPOSITORY.joinpath(*relative(value).parts)


def eligible(path: Path) -> bool:
    relative_path = path.relative_to(REPOSITORY)
    return (
        path.is_file()
        and not path.is_symlink()
        and not any(
            part in {"__pycache__", ".pytest_cache", "target", ".lake"}
            for part in relative_path.parts
        )
        and path.suffix not in {".pyc", ".pyo"}
        and relative_path.as_posix()
        != "conformance/prototypes/evidence/evidence-manifest.json"
    )


def subject_paths(spec: dict[str, Any]) -> dict[str, str]:
    subjects: dict[str, str] = {}
    for item in spec["subject_roots"]:
        root = repository_path(item["path"])
        if not root.is_dir():
            raise RuntimeError(f"missing subject root: {item['path']}")
        for path in sorted(root.rglob("*")):
            if eligible(path):
                subjects[path.relative_to(REPOSITORY).as_posix()] = item["role"]
    for item in spec["subject_files"]:
        path = repository_path(item["path"])
        if not eligible(path):
            raise RuntimeError(f"missing subject file: {item['path']}")
        subjects[item["path"]] = item["role"]
    return subjects


def fixture_ids() -> tuple[list[str], list[str]]:
    root = REPOSITORY / "conformance/prototypes/fixtures/semantic-v1"
    catalog = load_json(root / "catalog.json")
    accepted: list[str] = []
    negative: list[str] = []
    for name in catalog["components"]:
        for case in load_json(root / name)["cases"]:
            if case["accept"]:
                if case.get("expected_encoding", {}).get("kind") != "none":
                    accepted.append(case["id"])
            else:
                negative.append(case["id"])
    return sorted(accepted), sorted(negative)


def run_git(arguments: list[str]) -> bytes:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=REPOSITORY,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.decode("utf-8", "replace").strip())
    return completed.stdout


def protected_files(base: str, prefixes: list[str]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for prefix in prefixes:
        names = run_git(["ls-tree", "-r", "--name-only", base, "--", prefix])
        for name_bytes in names.splitlines():
            name = name_bytes.decode("utf-8")
            content = run_git(["show", f"{base}:{name}"])
            output.append({"path": name, "sha256": sha256_bytes(content)})
    unique = {item["path"]: item for item in output}
    return [unique[name] for name in sorted(unique)]


def retained_failures(spec: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for value in spec["retained_failure_roots"]:
        root = repository_path(value)
        if not root.is_dir():
            raise RuntimeError(f"missing retained-failure root: {value}")
        paths.extend(
            path.relative_to(REPOSITORY).as_posix()
            for path in sorted(root.rglob("*"))
            if eligible(path)
        )
    if not paths:
        raise RuntimeError("no retained failure files")
    return sorted(set(paths))


def build() -> dict[str, Any]:
    spec = load_json(SPEC)
    if spec.get("schema") != "statqed.sq0005-evidence-spec.v1":
        raise RuntimeError("unsupported evidence-spec schema")
    subjects = subject_paths(spec)
    accepted, negative = fixture_ids()
    lineage = load_json(REPOSITORY / "schemas/prototypes/lineage.json")
    origins = [
        {
            "canonicalizer_lineage": item["canonicalizer_lineage"],
            "id": item["id"],
            "language": item["language"],
        }
        for item in lineage["implementations"]
    ]
    origins.sort(key=lambda item: item["id"])
    base = spec["baseline_commit"]
    return {
        "accepted_fixture_ids": accepted,
        "baseline": {
            "commit": base,
            "rfc0006_sha256": sha256_bytes(
                run_git(["show", f"{base}:rfcs/0006-canonical-logical-data-digest.md"])
            ),
            "sq0008_contract_sha256": sha256_bytes(
                run_git(["show", f"{base}:work/contracts/SQ-0008.yaml"])
            ),
        },
        "coverage_roots": spec["coverage_roots"],
        "expected_state": spec["expected_state"],
        "independent_origins": origins,
        "negative_fixture_ids": negative,
        "protected_files": protected_files(base, spec["protected_prefixes"]),
        "protected_prefixes": spec["protected_prefixes"],
        "retained_failures": retained_failures(spec),
        "review_record": spec["review_record"],
        "review_subject_paths": sorted(spec["review_subject_paths"]),
        "schema": "statqed.sq0005-evidence.v1",
        "subjects": [
            {"path": path, "role": subjects[path], "sha256": sha256(repository_path(path))}
            for path in sorted(subjects)
        ],
    }


def canonical_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    arguments = parser.parse_args()
    try:
        rendered = canonical_bytes(build())
    except (KeyError, OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"cannot build SQ-0005 evidence manifest: {error}", file=sys.stderr)
        return 1
    if arguments.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_bytes(rendered)
        print(OUTPUT.relative_to(REPOSITORY).as_posix())
        return 0
    if not OUTPUT.is_file() or OUTPUT.read_bytes() != rendered:
        print("SQ-0005 evidence manifest is stale", file=sys.stderr)
        return 1
    print("SQ-0005 evidence manifest regenerated byte-identically")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
