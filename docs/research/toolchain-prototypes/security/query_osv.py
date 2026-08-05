#!/usr/bin/env python3
"""Query the official OSV batch API for exact SQ-0002 prototype locks."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
from pathlib import Path
import re
import tempfile
import urllib.request


ROOT = Path(__file__).resolve().parents[4]
PROTOTYPES = ROOT / "docs/research/toolchain-prototypes"
LOG_ROOT = PROTOTYPES / "logs/security/run-20260805"
ENDPOINT = "https://api.osv.dev/v1/querybatch"


def now() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


def python_packages() -> list[tuple[str, str]]:
    lock = PROTOTYPES / "python/probe-requirements.lock"
    pattern = re.compile(r"^([A-Za-z0-9_.-]+)==([^ ;\\]+)")
    packages: list[tuple[str, str]] = []
    for line in lock.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            packages.append((match.group(1), match.group(2)))
    if not packages:
        raise ValueError("Python lock did not yield package/version pairs")
    return sorted(set(packages), key=lambda item: item[0].lower())


def r_packages() -> list[tuple[str, str]]:
    packages: set[tuple[str, str]] = set()
    dev_lock = PROTOTYPES / "r/development-cran-source-lock.tsv"
    with dev_lock.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            packages.add((row["package"], row["version"]))

    floor_lock = PROTOTYPES / "logs/r/run-20260803/floor-package-lock.stdout"
    with floor_lock.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t", quotechar='"'):
            if row.get("Priority") not in {"base", "recommended"}:
                packages.add((row["Package"], row["Version"]))
    if not packages:
        raise ValueError("R locks did not yield package/version pairs")
    return sorted(packages, key=lambda item: (item[0].lower(), item[1]))


def query(ecosystem: str, packages: list[tuple[str, str]], output: Path) -> dict[str, object]:
    output.mkdir(parents=True, exist_ok=True)
    slug = ecosystem.lower()
    request_payload = {
        "queries": [
            {"package": {"ecosystem": ecosystem, "name": name}, "version": version}
            for name, version in packages
        ]
    }
    request_bytes = (json.dumps(request_payload, indent=2, sort_keys=True) + "\n").encode()
    (output / f"{slug}-osv.request.json").write_bytes(request_bytes)
    started = now()
    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(request_payload, separators=(",", ":"), sort_keys=True).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "StatQED-SQ-0002/1"},
        method="POST",
    )
    stderr = ""
    status = 0
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            response_bytes = response.read()
        response_payload = json.loads(response_bytes)
        results = response_payload.get("results")
        if not isinstance(results, list) or len(results) != len(packages):
            raise ValueError("OSV result count does not match the exact package query count")
        if any(isinstance(result, dict) and result.get("next_page_token") for result in results):
            raise ValueError("OSV pagination was returned; complete page traversal is required")
        vulnerability_count = sum(
            len(result.get("vulns", [])) for result in results if isinstance(result, dict)
        )
        stdout = (
            f"ecosystem={ecosystem}\npackages={len(packages)}\n"
            f"vulnerabilities={vulnerability_count}\nendpoint={ENDPOINT}\n"
        )
        (output / f"{slug}-osv.response.json").write_text(
            json.dumps(response_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except Exception as error:  # retain exact unavailable/malformed evidence
        status = 1
        vulnerability_count = -1
        stdout = f"ecosystem={ecosystem}\npackages={len(packages)}\n"
        stderr = f"{type(error).__name__}: {error}\n"
    ended = now()
    (output / f"{slug}-osv.stdout.log").write_text(stdout, encoding="utf-8")
    (output / f"{slug}-osv.stderr.log").write_text(stderr, encoding="utf-8")
    command_record: dict[str, object] = {
        "id": f"{slug}-osv-exact-lock-query",
        "command": ["/usr/bin/python3", "query_osv.py", "--record"],
        "endpoint": ENDPOINT,
        "ecosystem": ecosystem,
        "package_count": len(packages),
        "started_at": started,
        "ended_at": ended,
        "exit_status": status,
    }
    (output / f"{slug}-osv.command.json").write_text(
        json.dumps(command_record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if status:
        raise RuntimeError(stderr.strip())
    return {**command_record, "vulnerability_count": vulnerability_count}


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--record", action="store_true")
    mode.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.record:
        output = LOG_ROOT
        records = [query("PyPI", python_packages(), output), query("CRAN", r_packages(), output)]
    else:
        with tempfile.TemporaryDirectory(prefix="statqed-sq0002-osv-") as directory:
            records = [
                query("PyPI", python_packages(), Path(directory)),
                query("CRAN", r_packages(), Path(directory)),
            ]
    print(json.dumps(records, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
