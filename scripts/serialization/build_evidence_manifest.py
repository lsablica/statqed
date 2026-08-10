#!/usr/bin/env python3
"""Generate the deterministic content manifest for SQ-0005 evidence."""

from __future__ import annotations

import argparse
import copy
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


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def parsed_json_bytes(value: bytes, label: str) -> Any:
    try:
        return json.loads(value.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"invalid JSON-compatible YAML for {label}: {error}") from error


def semantic_projection_sha256(
    value: dict[str, Any], omitted_fields: list[str]
) -> str:
    if omitted_fields != ["status"]:
        raise RuntimeError(
            "SQ-0008 lifecycle projection must omit exactly the top-level status field"
        )
    if "status" not in value:
        raise RuntimeError("SQ-0008 contract lacks the projected status field")
    projection = {key: item for key, item in value.items() if key not in omitted_fields}
    return sha256_bytes(canonical_json_bytes(projection))


def markdown_sections_projection_sha256(value: bytes, headings: list[str]) -> str:
    try:
        text = value.decode("utf-8")
    except UnicodeDecodeError as error:
        raise RuntimeError(f"invalid UTF-8 shared document: {error}") from error
    lines = text.splitlines(keepends=True)
    heading_rows = [
        (index, line[3:].rstrip("\r\n"))
        for index, line in enumerate(lines)
        if line.startswith("## ")
    ]
    if len({name for _, name in heading_rows}) != len(heading_rows):
        raise RuntimeError("shared Markdown document has duplicate level-two headings")
    positions = {name: index for index, name in heading_rows}
    if any(name not in positions for name in headings):
        raise RuntimeError("shared Markdown document lacks a protected heading")
    first_heading = min(index for index, _ in heading_rows)
    sections: dict[str, str] = {}
    all_indices = [index for index, _ in heading_rows]
    for name in headings:
        start = positions[name]
        end = next((index for index in all_indices if index > start), len(lines))
        sections[name] = "".join(lines[start:end])
    projection = {"preamble": "".join(lines[:first_heading]), "sections": sections}
    return sha256_bytes(canonical_json_bytes(projection))


def sq0005_dashboard_projection_sha256(value: bytes) -> str:
    try:
        text = value.decode("utf-8")
    except UnicodeDecodeError as error:
        raise RuntimeError(f"invalid UTF-8 quality dashboard: {error}") from error
    rows = [
        line
        for line in text.splitlines(keepends=True)
        if line.startswith("| Deterministic encoding profile |")
    ]
    if len(rows) != 1:
        raise RuntimeError("quality dashboard lacks one encoding-profile row")
    begin = "SQ-0005 adds one Experimental deterministic"
    end = "does not define logical-data identity."
    if text.count(begin) != 1 or text.count(end) != 1:
        raise RuntimeError("quality dashboard lacks one SQ-0005 evidence statement")
    evidence_start = text.index(begin)
    evidence_end = text.index(end, evidence_start) + len(end)
    nonblank = [line for line in text.splitlines(keepends=True) if line.strip()]
    if len(nonblank) < 2:
        raise RuntimeError("quality dashboard preamble is incomplete")
    projection = {
        "heading": nonblank[0],
        "status": nonblank[1],
        "encoding_profile_row": rows[0],
        "sq0005_evidence": text[evidence_start:evidence_end],
    }
    return sha256_bytes(canonical_json_bytes(projection))


def shared_document_projection_sha256(value: bytes, policy: dict[str, Any]) -> str:
    projection = policy.get("projection")
    if projection == "markdown_preamble_and_sections_v1":
        headings = policy.get("headings")
        if not isinstance(headings, list) or not all(
            isinstance(item, str) for item in headings
        ):
            raise RuntimeError("invalid shared Markdown heading policy")
        return markdown_sections_projection_sha256(value, headings)
    if projection == "sq0005_dashboard_v1" and sorted(policy) == ["projection"]:
        return sq0005_dashboard_projection_sha256(value)
    raise RuntimeError(f"unsupported shared-document projection: {projection}")


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
    for item in spec["live_subject_roots"]:
        root = repository_path(item["path"])
        if not root.is_dir():
            raise RuntimeError(f"missing subject root: {item['path']}")
        for path in sorted(root.rglob("*")):
            if eligible(path):
                subjects[path.relative_to(REPOSITORY).as_posix()] = item["role"]
    for item in spec["live_subject_files"]:
        path = repository_path(item["path"])
        if not eligible(path):
            raise RuntimeError(f"missing subject file: {item['path']}")
        subjects[item["path"]] = item["role"]
    return subjects


def historical_subjects(spec: dict[str, Any]) -> list[dict[str, str]]:
    binding = spec["historical_manifest"]
    blob = run_git(["show", f"{binding['commit']}:{binding['path']}"])
    if sha256_bytes(blob) != binding["sha256"]:
        raise RuntimeError("historical SQ-0005 manifest hash mismatch")
    manifest = parsed_json_bytes(blob, "historical SQ-0005 evidence manifest")
    if manifest.get("schema") != binding["schema"]:
        raise RuntimeError("historical SQ-0005 manifest schema mismatch")
    subjects = manifest.get("subjects")
    if not isinstance(subjects, list) or not subjects:
        raise RuntimeError("historical SQ-0005 manifest lacks subjects")
    if sha256_bytes(canonical_json_bytes(subjects)) != binding["subjects_sha256"]:
        raise RuntimeError("historical SQ-0005 subject map mismatch")
    return subjects


def historical_successor_contracts(spec: dict[str, Any]) -> dict[str, Any]:
    bindings = copy.deepcopy(spec["historical_successor_contracts"])
    if sorted(bindings) != ["SQ-0006", "SQ-0008"]:
        raise RuntimeError("historical successor contract bindings changed")
    for task_id, binding in sorted(bindings.items()):
        blob = run_git(["show", f"{binding['commit']}:{binding['path']}"])
        if sha256_bytes(blob) != binding["sha256"]:
            raise RuntimeError(f"historical {task_id} contract hash mismatch")
    return bindings


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
    if spec.get("schema") != "statqed.sq0005-evidence-spec.v2":
        raise RuntimeError("unsupported evidence-spec schema")
    live_subjects = subject_paths(spec)
    frozen_subjects = historical_subjects(spec)
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
    baseline_sq0008 = parsed_json_bytes(
        run_git(["show", f"{base}:work/contracts/SQ-0008.yaml"]),
        "baseline SQ-0008 contract",
    )
    live_invariants = copy.deepcopy(spec["live_invariants"])
    sq0008_integrity = live_invariants["successor_contract_integrity"]["SQ-0008"]
    sq0008_integrity["projection_sha256"] = semantic_projection_sha256(
        baseline_sq0008,
        sq0008_integrity["omitted_fields"],
    )
    shared_documents = live_invariants["shared_document_integrity"]
    for path, policy in sorted(shared_documents.items()):
        completion_blob = run_git(
            ["show", f"{spec['historical_manifest']['commit']}:{path}"]
        )
        policy["projection_sha256"] = shared_document_projection_sha256(
            completion_blob, policy
        )
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
        "historical_completion_state": spec["historical_completion_state"],
        "historical_manifest": spec["historical_manifest"],
        "historical_review": spec["historical_review"],
        "historical_successor_contracts": historical_successor_contracts(spec),
        "historical_subjects": frozen_subjects,
        "independent_origins": origins,
        "live_invariants": live_invariants,
        "negative_fixture_ids": negative,
        "protected_files": protected_files(base, spec["protected_prefixes"]),
        "protected_prefixes": spec["protected_prefixes"],
        "retained_failures": retained_failures(spec),
        "review_record": spec["review_record"],
        "review_subject_paths": sorted(spec["review_subject_paths"]),
        "schema": "statqed.sq0005-evidence.v2",
        "live_subjects": [
            {
                "path": path,
                "role": live_subjects[path],
                "sha256": sha256(repository_path(path)),
            }
            for path in sorted(live_subjects)
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
