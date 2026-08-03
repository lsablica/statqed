#!/usr/bin/env python3
"""Run or verify the SQ-0002 toolchain compatibility probes.

The verifier uses only the Python standard library.  It never writes a
production toolchain file.  Probe execution is opt-in and limited to commands
whose working directories are inside ``docs/research/toolchain-prototypes``.
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PROTOTYPE_ROOT = ROOT / "docs/research/toolchain-prototypes"
MATRIX_PATH = PROTOTYPE_ROOT / "matrix.json"
REPORT_PATH = ROOT / "docs/implementation/toolchain-compatibility.md"
SUMMARY_BEGIN = "<!-- SQ0002_REPORT_SUMMARY_BEGIN -->"
SUMMARY_END = "<!-- SQ0002_REPORT_SUMMARY_END -->"
CLASSIFICATIONS = {"success", "failure", "unknown"}
DISPOSITIONS = {"recommended", "rejected", "unresolved"}
RERUN_ALLOWLIST = {
    "rust-dev-prototype": (["bash", "run-probes.sh", "development"], "docs/research/toolchain-prototypes/rust"),
    "rust-msrv-prototype": (["bash", "run-probes.sh", "msrv"], "docs/research/toolchain-prototypes/rust"),
    "r-development-4.6.1-package-native": (["bash", "run-probes.sh", "development"], "docs/research/toolchain-prototypes/r"),
    "r-floor-4.4.3-package-native": (["bash", "run-probes.sh", "floor"], "docs/research/toolchain-prototypes/r"),
}
IMMUTABLE_LOCK_MARKERS = ("sha256", "commit", "manifest", "lock", "toolchain", "archive", "release", "rust_version", "version")
MUTABLE_PIN_PATTERN = re.compile(r"(?:^|\W)(?:latest|any|main|master|head|nightly|stable)(?:$|\W)", re.IGNORECASE)


class ValidationError(ValueError):
    """Raised when SQ-0002 evidence is incomplete or contradictory."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot load {path.relative_to(ROOT)}: {exc}") from exc


def parse_timestamp(value: Any, field: str) -> dt.datetime:
    require(isinstance(value, str) and value, f"{field} must be a non-empty timestamp")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValidationError(f"{field} is not ISO-8601: {value!r}") from exc
    require(parsed.tzinfo is not None, f"{field} must include a UTC offset")
    return parsed


def evidence_path(value: Any, field: str) -> Path:
    require(isinstance(value, str) and value, f"{field} must be a relative path")
    path = (ROOT / value).resolve()
    try:
        path.relative_to(PROTOTYPE_ROOT.resolve())
    except ValueError as exc:
        raise ValidationError(f"{field} escapes the prototype root: {value!r}") from exc
    require(path.is_file(), f"{field} does not exist: {value}")
    return path


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_source(source: Any, index: int) -> str:
    prefix = f"sources[{index}]"
    require(isinstance(source, dict), f"{prefix} must be an object")
    for field in ("id", "title", "url", "retrieved_at", "authority"):
        require(isinstance(source.get(field), str) and source[field], f"{prefix}.{field} is required")
    parse_timestamp(source["retrieved_at"], f"{prefix}.retrieved_at")
    require(source["url"].startswith("https://"), f"{prefix}.url must use HTTPS")
    return source["id"]


def validate_probe(probe: Any, index: int, source_ids: set[str]) -> str:
    prefix = f"probes[{index}]"
    require(isinstance(probe, dict), f"{prefix} must be an object")
    required_strings = (
        "id", "component", "candidate", "started_at", "ended_at",
        "classification", "reason", "disposition", "version_output",
    )
    for field in required_strings:
        require(isinstance(probe.get(field), str) and probe[field], f"{prefix}.{field} is required")
    started = parse_timestamp(probe["started_at"], f"{prefix}.started_at")
    ended = parse_timestamp(probe["ended_at"], f"{prefix}.ended_at")
    require(ended >= started, f"{prefix} ends before it starts")
    require(probe["classification"] in CLASSIFICATIONS, f"{prefix} has invalid classification")
    require(probe["disposition"] in DISPOSITIONS, f"{prefix} has invalid disposition")

    platform = probe.get("platform")
    require(isinstance(platform, dict), f"{prefix}.platform must be an object")
    for field in ("os", "version", "architecture", "environment"):
        require(isinstance(platform.get(field), str) and platform[field], f"{prefix}.platform.{field} is required")

    commands = probe.get("commands")
    require(isinstance(commands, list) and commands, f"{prefix}.commands must be non-empty")
    require(all(isinstance(command, list) and command and all(isinstance(token, str) and token for token in command) for command in commands), f"{prefix}.commands must be argv arrays")
    environment = probe.get("environment_variables")
    require(isinstance(environment, dict), f"{prefix}.environment_variables must be an object")
    require(all(isinstance(key, str) and isinstance(value, str) for key, value in environment.items()), f"{prefix}.environment_variables must contain strings")
    locks = probe.get("dependency_locks")
    require(isinstance(locks, list), f"{prefix}.dependency_locks must be a list")
    require(all(isinstance(lock, dict) and isinstance(lock.get("kind"), str) and isinstance(lock.get("value"), str) for lock in locks), f"{prefix}.dependency_locks entries need kind/value")

    status = probe.get("exit_status")
    require(status is None or isinstance(status, int), f"{prefix}.exit_status must be integer or null")
    if probe["classification"] == "success":
        require(status == 0, f"{prefix} success requires exit_status 0")
    elif probe["classification"] == "failure":
        require(isinstance(status, int) and status != 0, f"{prefix} failure requires nonzero exit_status")
    else:
        require(status is None or status != 0, f"{prefix} unknown cannot have exit_status 0")
    if probe["disposition"] == "recommended":
        require(probe["classification"] == "success", f"{prefix} recommended evidence must succeed")

    stdout_path = evidence_path(probe.get("stdout_path"), f"{prefix}.stdout_path")
    stderr_path = evidence_path(probe.get("stderr_path"), f"{prefix}.stderr_path")
    for name, path in (("stdout", stdout_path), ("stderr", stderr_path)):
        digest = probe.get(f"{name}_sha256")
        require(
            isinstance(digest, str) and len(digest) == 64,
            f"{prefix}.{name}_sha256 must be a SHA-256 hex digest",
        )
        require(
            sha256_file(path) == digest,
            f"{prefix}.{name}_sha256 does not bind {path.relative_to(ROOT)}",
        )
    refs = probe.get("source_refs")
    require(isinstance(refs, list) and refs, f"{prefix}.source_refs must be non-empty")
    require(set(refs) <= source_ids, f"{prefix}.source_refs contains an unknown source ID")

    rerun = probe.get("rerun")
    require(isinstance(rerun, dict), f"{prefix}.rerun must be an object")
    require(isinstance(rerun.get("runnable"), bool), f"{prefix}.rerun.runnable must be boolean")
    if rerun["runnable"]:
        command = rerun.get("command")
        require(isinstance(command, list) and command and all(isinstance(token, str) and token for token in command), f"{prefix}.rerun.command must be argv")
        cwd_value = rerun.get("cwd")
        require(isinstance(cwd_value, str) and cwd_value, f"{prefix}.rerun.cwd is required")
        cwd = (ROOT / cwd_value).resolve()
        try:
            cwd.relative_to(PROTOTYPE_ROOT.resolve())
        except ValueError as exc:
            raise ValidationError(f"{prefix}.rerun.cwd escapes prototype root") from exc
        require(cwd.is_dir(), f"{prefix}.rerun.cwd does not exist")
        allowed = RERUN_ALLOWLIST.get(probe["id"])
        require(allowed is not None, f"{prefix} is not an allowlisted rerun dispatcher")
        require(command == allowed[0] and cwd_value == allowed[1], f"{prefix} rerun differs from the owned dispatcher")
    if probe["disposition"] == "recommended":
        require(locks, f"{prefix} recommended evidence must contain dependency locks")
        require(
            any(any(marker in lock["kind"].lower() for marker in IMMUTABLE_LOCK_MARKERS) for lock in locks),
            f"{prefix} recommended evidence lacks an immutable lock kind",
        )
    return probe["id"]


def extract_report_summary(text: str) -> Any:
    require(text.count(SUMMARY_BEGIN) == 1 and text.count(SUMMARY_END) == 1, "report must contain exactly one machine-readable summary block")
    payload = text.split(SUMMARY_BEGIN, 1)[1].split(SUMMARY_END, 1)[0].strip()
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"report summary block is invalid JSON: {exc}") from exc


def validate_matrix(matrix_path: Path = MATRIX_PATH, report_path: Path = REPORT_PATH) -> dict[str, Any]:
    matrix = load_json(matrix_path)
    require(isinstance(matrix, dict), "matrix root must be an object")
    require(matrix.get("schema_version") == 1, "matrix.schema_version must be 1")
    require(matrix.get("task_id") == "SQ-0002", "matrix.task_id must be SQ-0002")
    parse_timestamp(matrix.get("generated_at"), "matrix.generated_at")
    require(matrix.get("retrieval_date") == "2026-08-03", "matrix.retrieval_date must be 2026-08-03")
    host = matrix.get("host")
    require(isinstance(host, dict), "matrix.host must be an object")
    for field in ("os", "version", "kernel", "architecture"):
        require(isinstance(host.get(field), str) and host[field], f"matrix.host.{field} is required")

    sources = matrix.get("sources")
    require(isinstance(sources, list) and sources, "matrix.sources must be non-empty")
    source_ids = [validate_source(source, index) for index, source in enumerate(sources)]
    require(len(source_ids) == len(set(source_ids)), "source IDs must be unique")

    probes = matrix.get("probes")
    require(isinstance(probes, list) and probes, "matrix.probes must be non-empty")
    probe_ids = [validate_probe(probe, index, set(source_ids)) for index, probe in enumerate(probes)]
    require(len(probe_ids) == len(set(probe_ids)), "probe IDs must be unique")
    probe_by_id = {probe["id"]: probe for probe in probes}

    subjects = matrix.get("prototype_subjects")
    require(isinstance(subjects, list) and subjects, "matrix.prototype_subjects must be non-empty")
    subject_paths: list[str] = []
    for index, subject in enumerate(subjects):
        prefix = f"prototype_subjects[{index}]"
        require(isinstance(subject, dict), f"{prefix} must be an object")
        path = evidence_path(subject.get("path"), f"{prefix}.path")
        digest = subject.get("sha256")
        require(isinstance(digest, str) and len(digest) == 64, f"{prefix}.sha256 must be a SHA-256 hex digest")
        require(sha256_file(path) == digest, f"{prefix}.sha256 does not bind {path.relative_to(ROOT)}")
        subject_paths.append(subject["path"])
    require(len(subject_paths) == len(set(subject_paths)), "prototype subject paths must be unique")

    recommendations = matrix.get("recommendations")
    require(isinstance(recommendations, list) and recommendations, "matrix.recommendations must be non-empty")
    recommendation_ids: list[str] = []
    for index, recommendation in enumerate(recommendations):
        prefix = f"recommendations[{index}]"
        require(isinstance(recommendation, dict), f"{prefix} must be an object")
        for field in ("id", "component", "role", "development_pin", "support_floor", "update_policy", "rollback_policy"):
            require(isinstance(recommendation.get(field), str) and recommendation[field], f"{prefix}.{field} is required")
        require(not MUTABLE_PIN_PATTERN.search(recommendation["development_pin"]), f"{prefix}.development_pin contains a mutable alias")
        require(not MUTABLE_PIN_PATTERN.search(recommendation["support_floor"]), f"{prefix}.support_floor contains a mutable alias")
        require(re.search(r"\d+\.\d+|[0-9a-f]{12,64}", recommendation["development_pin"]), f"{prefix}.development_pin lacks an exact version or commit")
        evidence = recommendation.get("evidence_probe_ids")
        require(isinstance(evidence, list) and evidence, f"{prefix}.evidence_probe_ids must be non-empty")
        for probe_id in evidence:
            require(probe_id in probe_by_id, f"{prefix} references unknown probe {probe_id!r}")
            probe = probe_by_id[probe_id]
            require(probe["classification"] == "success", f"{prefix} relies on unsuccessful probe {probe_id}")
            require(probe["disposition"] == "recommended", f"{prefix} relies on non-recommended probe {probe_id}")
        ci_entries = recommendation.get("ci_matrix")
        require(isinstance(ci_entries, list) and ci_entries, f"{prefix}.ci_matrix must be non-empty")
        recommendation_ids.append(recommendation["id"])
    require(len(recommendation_ids) == len(set(recommendation_ids)), "recommendation IDs must be unique")

    ci_matrix = matrix.get("ci_matrix")
    require(isinstance(ci_matrix, list) and ci_matrix, "matrix.ci_matrix must be non-empty")
    ci_ids: list[str] = []
    for index, entry in enumerate(ci_matrix):
        prefix = f"ci_matrix[{index}]"
        require(isinstance(entry, dict), f"{prefix} must be an object")
        for field in ("id", "component", "version", "os", "architecture", "status"):
            require(isinstance(entry.get(field), str) and entry[field], f"{prefix}.{field} is required")
        require(entry["status"] in {"direct_success", "planned_validation"}, f"{prefix}.status is invalid")
        evidence = entry.get("evidence_probe_ids")
        require(isinstance(evidence, list), f"{prefix}.evidence_probe_ids must be a list")
        if entry["status"] == "direct_success":
            require(evidence, f"{prefix} direct success requires evidence")
            for probe_id in evidence:
                require(probe_id in probe_by_id, f"{prefix} references unknown probe {probe_id!r}")
                require(probe_by_id[probe_id]["classification"] == "success", f"{prefix} relies on unsuccessful probe {probe_id}")
                probe = probe_by_id[probe_id]
                claimed_os = entry["os"].split()[0].lower()
                observed_platform = f"{probe['platform']['os']} {probe['platform']['version']}".lower()
                require(claimed_os in observed_platform, f"{prefix} OS is not bound to {probe_id}")
                require(entry["architecture"].lower() == probe["platform"]["architecture"].lower(), f"{prefix} architecture is not bound to {probe_id}")
                version_tokens = re.findall(r"\d+\.\d+(?:\.\d+)?", entry["version"])
                evidence_text = f"{probe['candidate']} {probe['version_output']}"
                require(not version_tokens or any(token in evidence_text for token in version_tokens), f"{prefix} version is not bound to {probe_id}")
        else:
            require(not evidence, f"{prefix} planned validation cannot claim direct evidence")
        ci_ids.append(entry["id"])
    require(len(ci_ids) == len(set(ci_ids)), "CI entry IDs must be unique")
    for index, recommendation in enumerate(recommendations):
        require(set(recommendation["ci_matrix"]) <= set(ci_ids), f"recommendations[{index}].ci_matrix contains an unknown CI entry")
    report_summary = matrix.get("report_summary")
    require(isinstance(report_summary, dict), "matrix.report_summary must be an object")
    require(report_summary.get("recommendations") == recommendations, "matrix.report_summary recommendations disagree with matrix")
    require(report_summary.get("ci_matrix") == ci_matrix, "matrix.report_summary CI matrix disagrees with matrix")

    try:
        report_text = report_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValidationError(f"cannot read report: {exc}") from exc
    require(extract_report_summary(report_text) == report_summary, "report summary disagrees with matrix.report_summary")
    matrix_digest = hashlib.sha256(matrix_path.read_bytes()).hexdigest()
    require(f"Matrix SHA-256: `sha256:{matrix_digest}`" in report_text, "report does not bind the exact matrix SHA-256")
    for probe in probes:
        if probe["classification"] != "success":
            require(f"`{probe['id']}`" in report_text, f"report omits failed/unknown probe {probe['id']}")
    return matrix


def run_available(matrix: dict[str, Any], selected: set[str]) -> int:
    failures: list[str] = []
    for probe in matrix["probes"]:
        if selected and probe["id"] not in selected:
            continue
        rerun = probe["rerun"]
        if not rerun["runnable"]:
            print(f"SKIP {probe['id']}: {rerun.get('unavailable_reason', 'not locally runnable')}")
            continue
        command = rerun["command"]
        if shutil.which(command[0]) is None:
            message = f"UNAVAILABLE {probe['id']}: executable {command[0]!r} not found"
            print(message)
            if probe["disposition"] == "recommended":
                failures.append(message)
            continue
        environment = os.environ.copy()
        environment.update(probe["environment_variables"])
        cwd = ROOT / rerun["cwd"]
        print(f"RUN {probe['id']}: {command!r} (cwd={cwd.relative_to(ROOT)})")
        completed = subprocess.run(command, cwd=cwd, env=environment, check=False)
        expected = probe["exit_status"]
        if completed.returncode != expected:
            message = f"MISMATCH {probe['id']}: exit {completed.returncode}, recorded {expected}"
            print(message, file=sys.stderr)
            if probe["disposition"] == "recommended" or probe["classification"] != "unknown":
                failures.append(message)
        else:
            print(f"MATCH {probe['id']}: exit {completed.returncode}")
    return 1 if failures else 0


def run_corruption_regressions(matrix: dict[str, Any]) -> None:
    """Prove the verifier rejects the minimized adversarial mutations."""

    fixture = load_json(PROTOTYPE_ROOT / "failures/verifier-corruption-cases.json")
    require(isinstance(fixture, dict) and len(fixture.get("cases", [])) == 5, "corruption fixture must contain five cases")
    mutations: list[tuple[str, Any]] = []

    mutable = copy.deepcopy(matrix)
    mutable["recommendations"][0]["development_pin"] = "latest"
    mutations.append(("mutable-recommendation", mutable))

    cross_platform = copy.deepcopy(matrix)
    direct = next(entry for entry in cross_platform["ci_matrix"] if entry["status"] == "direct_success")
    direct["os"] = "Windows 999"
    direct["architecture"] = "arm64"
    mutations.append(("cross-platform-evidence", cross_platform))

    unsafe = copy.deepcopy(matrix)
    runnable = next(probe for probe in unsafe["probes"] if probe["rerun"]["runnable"])
    runnable["rerun"] = {"runnable": True, "command": ["/usr/bin/touch", "/tmp/statqed-unsafe"], "cwd": "docs/research/toolchain-prototypes"}
    mutations.append(("unsafe-rerun-command", unsafe))

    normalized_failure = copy.deepcopy(matrix)
    failed = next(probe for probe in normalized_failure["probes"] if probe["classification"] == "failure")
    failed["exit_status"] = 0
    mutations.append(("failure-exit-zero", normalized_failure))

    fabricated_lock = copy.deepcopy(matrix)
    recommended = next(probe for probe in fabricated_lock["probes"] if probe["disposition"] == "recommended")
    recommended["dependency_locks"] = []
    mutations.append(("recommended-empty-lock", fabricated_lock))

    with tempfile.TemporaryDirectory(prefix="statqed-sq0002-verifier-") as directory:
        root = Path(directory)
        for case_id, candidate in mutations:
            candidate["report_summary"] = {"recommendations": candidate["recommendations"], "ci_matrix": candidate["ci_matrix"]}
            matrix_path = root / f"{case_id}.json"
            matrix_path.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            report_path = root / f"{case_id}.md"
            report_path.write_text(
                f"{SUMMARY_BEGIN}\n{json.dumps(candidate['report_summary'], indent=2, sort_keys=True)}\n{SUMMARY_END}\n"
                f"Matrix SHA-256: `sha256:{sha256_file(matrix_path)}`\n",
                encoding="utf-8",
            )
            try:
                validate_matrix(matrix_path, report_path)
            except ValidationError:
                continue
            raise ValidationError(f"corruption regression was accepted: {case_id}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--verify", action="store_true", help="validate matrix, report, and retained evidence")
    mode.add_argument("--run-available", action="store_true", help="rerun locally available, explicitly safe prototype commands")
    parser.add_argument("--probe", action="append", default=[], help="limit --run-available to a probe ID")
    args = parser.parse_args()
    try:
        matrix = validate_matrix()
        if args.verify:
            run_corruption_regressions(matrix)
            print(f"SQ-0002 toolchain evidence verified: {len(matrix['probes'])} probes, {len(matrix['recommendations'])} recommendations")
            return 0
        selected = set(args.probe)
        known = {probe["id"] for probe in matrix["probes"]}
        require(selected <= known, f"unknown --probe IDs: {sorted(selected - known)}")
        return run_available(matrix, selected)
    except ValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
