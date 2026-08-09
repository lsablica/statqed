"""Corruption tests for the permanent SQ-0005 static evidence verifier."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPOSITORY = Path(__file__).resolve().parents[3]
MANIFEST = Path("conformance/prototypes/evidence/evidence-manifest.json")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class EvidenceCorruptionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="statqed-evidence-corruption-")
        self.root = Path(self.temporary.name) / "repository"
        shutil.copytree(
            REPOSITORY,
            self.root,
            ignore=shutil.ignore_patterns(
                ".git",
                ".lake",
                "target",
                "__pycache__",
                ".pytest_cache",
                "*.pyc",
                "*.pyo",
            ),
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_check(self) -> tuple[int, str]:
        completed = subprocess.run(
            [
                sys.executable,
                str(self.root / "scripts/serialization/check_evidence.py"),
                "--root",
                str(self.root),
                "--json",
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        return completed.returncode, completed.stdout + completed.stderr

    def assert_rejected(self, fragment: str) -> None:
        status, output = self.run_check()
        self.assertNotEqual(status, 0, output)
        self.assertIn(fragment, output)

    def manifest(self) -> dict:
        return json.loads((self.root / MANIFEST).read_text(encoding="utf-8"))

    def write_manifest(self, value: dict) -> None:
        canonical_write(self.root / MANIFEST, value)

    def subject_with_prefix(self, prefix: str) -> str:
        for item in self.manifest()["subjects"]:
            if item["path"].startswith(prefix):
                return item["path"]
        self.fail(f"no subject with prefix {prefix}")

    def update_subject_hash(self, relative: str) -> None:
        manifest = self.manifest()
        for item in manifest["subjects"]:
            if item["path"] == relative:
                item["sha256"] = digest(self.root / relative)
                self.write_manifest(manifest)
                return
        self.fail(f"subject absent: {relative}")

    def test_baseline_is_verified(self) -> None:
        status, output = self.run_check()
        self.assertEqual(status, 0, output)

    def test_changed_profile_text_is_rejected(self) -> None:
        path = self.root / "docs/research/serialization/profile-candidate.md"
        path.write_text(path.read_text(encoding="utf-8") + "\ncorruption\n", encoding="utf-8")
        self.assert_rejected("subject SHA-256 mismatch")

    def test_changed_source_audit_is_rejected(self) -> None:
        relative = self.subject_with_prefix("source-audits/encoding/")
        path = self.root / relative
        path.write_text(path.read_text(encoding="utf-8") + "\ncorruption: true\n", encoding="utf-8")
        self.assert_rejected("subject SHA-256 mismatch")

    def test_replaced_golden_bytes_are_rejected(self) -> None:
        relative = self.subject_with_prefix("conformance/prototypes/golden/")
        while relative.endswith("manifest.json"):
            manifest = self.manifest()
            matches = [
                item["path"]
                for item in manifest["subjects"]
                if item["path"].startswith("conformance/prototypes/golden/")
                and not item["path"].endswith("manifest.json")
            ]
            self.assertTrue(matches)
            relative = matches[0]
        path = self.root / relative
        data = path.read_bytes()
        self.assertTrue(data)
        path.write_bytes(bytes([data[0] ^ 1]) + data[1:])
        self.assert_rejected("subject SHA-256 mismatch")

    def test_missing_negative_case_is_rejected(self) -> None:
        manifest = self.manifest()
        manifest["negative_fixture_ids"] = manifest["negative_fixture_ids"][:-1]
        self.write_manifest(manifest)
        self.assert_rejected("negative fixture manifest")

    def test_removed_failed_result_is_rejected(self) -> None:
        relative = self.manifest()["retained_failures"][0]
        (self.root / relative).unlink()
        self.assert_rejected("missing regular evidence file")

    def test_falsely_shared_lineage_is_rejected(self) -> None:
        relative = "schemas/prototypes/lineage.json"
        path = self.root / relative
        lineage = json.loads(path.read_text(encoding="utf-8"))
        shared = lineage["implementations"][0]["canonicalizer_lineage"]
        lineage["implementations"][1]["canonicalizer_lineage"] = shared
        canonical_write(path, lineage)
        self.update_subject_hash(relative)
        self.assert_rejected("share canonicalizer lineage")

    def test_stale_review_hash_is_rejected(self) -> None:
        review_path = self.root / self.manifest()["review_record"]
        text = review_path.read_text(encoding="utf-8")
        marker = "<!-- SQ-0005-REVIEW-SUBJECTS-BEGIN -->"
        start = text.index(marker) + len(marker)
        end = text.index("<!-- SQ-0005-REVIEW-SUBJECTS-END -->")
        body = text[start:end].strip()
        fenced = body.startswith("```json")
        if fenced:
            body = body[len("```json") : -len("```")].strip()
        bindings = json.loads(body)
        first = sorted(bindings)[0]
        bindings[first] = "0" * 64
        replacement = json.dumps(bindings, indent=2, sort_keys=True)
        if fenced:
            replacement = "```json\n" + replacement + "\n```"
        review_path.write_text(text[:start] + "\n" + replacement + "\n" + text[end:], encoding="utf-8")
        self.assert_rejected("stale review hash")

    def test_status_drift_is_rejected(self) -> None:
        path = self.root / "work/backlog.yaml"
        backlog = json.loads(path.read_text(encoding="utf-8"))
        for item in backlog["tasks"]:
            if item["id"] == "SQ-0005":
                item["status"] = "IN_REVIEW"
        canonical_write(path, backlog)
        self.assert_rejected("status drift")

    def test_rfc0006_modification_is_rejected(self) -> None:
        path = self.root / "rfcs/0006-canonical-logical-data-digest.md"
        path.write_text(path.read_text(encoding="utf-8") + "\ncorruption\n", encoding="utf-8")
        self.assert_rejected("RFC-0006 changed")

    def test_sq0008_modification_is_rejected(self) -> None:
        path = self.root / "work/contracts/SQ-0008.yaml"
        path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        self.assert_rejected("SQ-0008 contract changed")

    def test_production_backend_contamination_is_rejected(self) -> None:
        path = self.root / "backend/contamination.rs"
        path.write_text("// prohibited SQ-0005 contamination\n", encoding="utf-8")
        self.assert_rejected("protected production path-set drift")


if __name__ == "__main__":
    unittest.main()
