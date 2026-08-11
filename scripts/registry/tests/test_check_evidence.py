from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

SCRIPT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

import check_evidence

ROOT = Path(__file__).resolve().parents[3]


class EvidenceCorruptionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._temp = tempfile.TemporaryDirectory(prefix="statqed-sq0007-evidence-")
        cls.root = Path(cls._temp.name) / "repo"
        shutil.copytree(
            ROOT,
            cls.root,
            ignore=shutil.ignore_patterns(".git", ".codex", ".lake", "target", "__pycache__", ".pytest_cache"),
        )
        assert check_evidence.verify(cls.root) == []

    @classmethod
    def tearDownClass(cls):
        cls._temp.cleanup()

    def mutate(self, relative: str, operation) -> list[str]:
        path = self.root / relative
        existed = path.exists()
        original = path.read_bytes() if existed else None
        operation(path)
        try:
            return check_evidence.verify(self.root)
        finally:
            if existed:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(original)
            elif path.exists():
                path.unlink()

    def append(self, relative: str) -> list[str]:
        return self.mutate(relative, lambda path: path.write_bytes(path.read_bytes() + b"\ncorrupt\n"))

    def test_baseline_verifies(self):
        self.assertEqual(check_evidence.verify(self.root), [])

    def test_rfc_drift(self):
        self.assertIn("evidence.manifest_drift", self.append("rfcs/0005-theorem-identity-and-compatibility.md"))

    def test_adr_drift(self):
        self.assertIn("evidence.manifest_drift", self.append("docs/adr/0007-versioned-theorem-registry.md"))

    def test_normative_scope_divergence(self):
        errors = self.mutate(
            "docs/adr/0007-versioned-theorem-registry.md",
            lambda path: path.write_text(path.read_text().replace("eleven layers", "twelve layers", 1)),
        )
        self.assertIn("evidence.normative_scope_drift", errors)

    def test_proposition_mutation(self):
        self.assertIn("evidence.manifest_drift", self.append("theorem-registry/evidence/proposition.cbor"))

    def test_environment_mutation(self):
        self.assertIn("evidence.manifest_drift", self.append("theorem-registry/evidence/environment.cbor"))

    def test_referenced_definition_mutation(self):
        self.assertIn("evidence.manifest_drift", self.append("lean/StatQED/Registry/Closure.lean"))

    def test_golden_replacement(self):
        self.assertIn("evidence.manifest_drift", self.append("conformance/registry/golden/PROP-TRUE.cbor"))

    def test_missing_negative_fixture(self):
        errors = self.mutate("conformance/registry/fixtures/catalog.json", lambda path: path.unlink())
        self.assertTrue(any(error.startswith("evidence.required_missing") or error == "evidence.manifest_drift" for error in errors))

    def test_removed_result(self):
        self.assertIn("evidence.manifest_drift", self.mutate("conformance/registry/results/results.json", lambda path: path.unlink()))

    def test_shared_lineage_forgery(self):
        self.assertIn("evidence.manifest_drift", self.append("scripts/registry/independent_oracle.py"))

    def test_statement_digest_substitution(self):
        self.assertIn("evidence.manifest_drift", self.append("theorem-registry/records/test-only-true.v0.json"))

    def test_registry_root_replacement(self):
        self.assertIn("evidence.manifest_drift", self.append("theorem-registry/policy/authorization-v0.json"))

    def test_proof_lock_replacement(self):
        self.assertIn("evidence.manifest_drift", self.append("theorem-registry/locks/proof-build-v0.json"))

    def test_axiom_report_replacement(self):
        self.assertIn("evidence.manifest_drift", self.append("theorem-registry/evidence/axioms.json"))

    def test_compatibility_reversal(self):
        self.assertIn("evidence.manifest_drift", self.append("theorem-registry/locks/compatibility-v0.json"))

    def test_rfc0006_mutation(self):
        errors = self.append("rfcs/0006-canonical-logical-data-digest.md")
        self.assertTrue(any(error.startswith("evidence.predecessor_drift:rfcs/0006") for error in errors))

    def test_sq0006_predecessor_mutation(self):
        errors = self.append("conformance/schema-v0/evidence/evidence-manifest.json")
        self.assertTrue(any(error.startswith("evidence.predecessor_drift:conformance/schema-v0") for error in errors))

    def test_task_status_regression(self):
        path = "work/contracts/SQ-0007.yaml"
        errors = self.mutate(path, lambda target: target.write_text(target.read_text().replace('"status": "BLOCKED"', '"status": "READY"')))
        self.assertIn("evidence.task_status_illegal", errors)

    def test_contract_backlog_disagreement(self):
        path = "work/backlog.yaml"
        def change(target):
            value = json.loads(target.read_text())
            next(item for item in value["tasks"] if item["id"] == "SQ-0007")["status"] = "READY"
            target.write_text(json.dumps(value) + "\n")
        errors = self.mutate(path, change)
        self.assertIn("evidence.task_contract_backlog_disagreement", errors)

    def test_production_path_contamination_rejected_by_scope_policy(self):
        contract = json.loads((self.root / "work/contracts/SQ-0007.yaml").read_text())
        self.assertFalse(check_evidence.path_allowed("backend/crates/statqed-core/src/contamination.rs", contract["allowed_paths"]))

    def test_allowed_registry_path_accepted_by_scope_policy(self):
        contract = json.loads((self.root / "work/contracts/SQ-0007.yaml").read_text())
        self.assertTrue(check_evidence.path_allowed("backend/crates/statqed-registry/src/lib.rs", contract["allowed_paths"]))


if __name__ == "__main__":
    unittest.main()
