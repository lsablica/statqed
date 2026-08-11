from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest


SCRIPT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from check_schema_v0 import EvidenceError, verify


ROOT = Path(__file__).resolve().parents[3]


class EvidenceCorruptionTests(unittest.TestCase):
    def shadow(self):
        temporary = tempfile.TemporaryDirectory(prefix="statqed-sq0006-corrupt-")
        destination = Path(temporary.name) / "repo"
        shutil.copytree(
            ROOT,
            destination,
            copy_function=os.link,
            ignore=shutil.ignore_patterns(".git", "target", "__pycache__", ".pytest_cache"),
        )
        return temporary, destination

    def mutate(self, root: Path, relative: str, transform):
        path = root / relative
        data = path.read_bytes()
        path.unlink()
        changed = transform(data)
        path.write_bytes(changed)

    def assert_rejected(self, relative: str, transform):
        temporary, root = self.shadow()
        try:
            self.mutate(root, relative, transform)
            with self.assertRaises(EvidenceError):
                verify(root)
        finally:
            temporary.cleanup()

    def write_json(self, root: Path, relative: str, document):
        path = root / relative
        path.unlink()
        path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")

    def test_changed_field_semantics(self):
        self.assert_rejected("schemas/v0/README.md", lambda data: data.replace(b"Opaque", b"Global", 1))

    def test_changed_cddl(self):
        self.assert_rejected("schemas/v0/source/foundation-structural.cddl", lambda data: data + b"; mutation\n")

    def test_replaced_golden(self):
        self.assert_rejected("conformance/golden/v0/positive-minimum.cbor", lambda data: data[:-1] + bytes((data[-1] ^ 1,)))

    def test_missing_negative_fixture(self):
        self.assert_rejected("schemas/fixtures/v0/negative/catalog.json", lambda data: data.replace(b'"missing.schema_id"', b'"removed.schema_id"', 1))

    def test_changed_error_code(self):
        self.assert_rejected("conformance/schema-v0/results.json", lambda data: data.replace(b"schema.identifier_syntax", b"schema.identifier_length", 1))

    def test_removed_independent_result(self):
        self.assert_rejected("conformance/schema-v0/results.json", lambda data: data.replace(b'"rust_encode_output_sha256"', b'"removed_rust_output_sha256"', 1))

    def test_stale_review_binding(self):
        self.assert_rejected("work/reviews/SQ-0006.md", lambda data: data + b"\nstale mutation\n")

    def test_rfc0006_modification(self):
        self.assert_rejected("rfcs/0006-canonical-logical-data-digest.md", lambda data: data + b"\nmutation\n")

    def test_prototype_modification(self):
        self.assert_rejected("schemas/prototypes/python-oracle/LINEAGE.md", lambda data: data + b"\nmutation\n")

    def test_production_backend_contamination(self):
        self.assert_rejected("backend/README.md", lambda data: data + b"\nmutation\n")

    def test_task_state_drift(self):
        def transform(data):
            document = json.loads(data)
            document["status"] = "READY"
            return (json.dumps(document, indent=2) + "\n").encode()
        self.assert_rejected("work/contracts/SQ-0006.yaml", transform)

    def test_owned_document_projection_rejects_drift(self):
        self.assert_rejected(
            "docs/spec/ir.md",
            lambda data: data.replace(b"closed\n`foundation_structural`", b"open\n`foundation_structural`", 1),
        )

    def test_unrelated_successor_document_append_is_allowed(self):
        temporary, root = self.shadow()
        try:
            self.mutate(root, "docs/spec/ir.md", lambda data: data + b"\n## Future unrelated section\n\nNot SQ-0006 evidence.\n")
            verify(root)
        finally:
            temporary.cleanup()

    def test_adr0011_drift(self):
        self.assert_rejected(
            "docs/adr/0011-foundation-toy-slice.md",
            lambda data: data.replace(b"- Status: Accepted", b"- Status: Proposed", 1),
        )

    def test_schema_identity_pair_drift(self):
        for schema_id, version in (("statqed.foundation-structural.v1", 0), ("statqed.foundation-structural.v1", 1)):
            with self.subTest(schema_id=schema_id, version=version):
                temporary, root = self.shadow()
                try:
                    manifest = json.loads((root / "schemas/v0/manifest.json").read_text())
                    manifest["schema_id"] = schema_id
                    manifest["schema_version"] = version
                    self.write_json(root, "schemas/v0/manifest.json", manifest)
                    with self.assertRaises(EvidenceError):
                        verify(root)
                finally:
                    temporary.cleanup()

    def test_sq0006_lifecycle_states(self):
        for state in ("IN_PROGRESS", "IN_REVIEW", "DONE"):
            with self.subTest(state=state):
                temporary, root = self.shadow()
                try:
                    contract = json.loads((root / "work/contracts/SQ-0006.yaml").read_text())
                    backlog = json.loads((root / "work/backlog.yaml").read_text())
                    status = json.loads((root / "work/status.yaml").read_text())
                    contract["status"] = state
                    next(task for task in backlog["tasks"] if task["id"] == "SQ-0006")["status"] = state
                    status["in_progress"] = [item for item in status["in_progress"] if item != "SQ-0006"]
                    status["done"] = [item for item in status["done"] if item != "SQ-0006"]
                    status["in_progress" if state != "DONE" else "done"].append("SQ-0006")
                    self.write_json(root, "work/contracts/SQ-0006.yaml", contract)
                    self.write_json(root, "work/backlog.yaml", backlog)
                    self.write_json(root, "work/status.yaml", status)
                    verify(root)
                finally:
                    temporary.cleanup()


if __name__ == "__main__":
    unittest.main()
