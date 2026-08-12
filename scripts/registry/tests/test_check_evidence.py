from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
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

    def test_import_environment_mutation_changes_bound_build_material(self):
        errors = self.mutate(
            "lean/StatQED/Registry/Tests/Smoke.lean",
            lambda path: path.write_text(
                path.read_text().replace(
                    "import Mathlib.Data.Set.Defs\n",
                    "import Mathlib.Data.Set.Defs\nimport Mathlib.Data.List.Basic\n",
                    1,
                )
            ),
        )
        self.assertIn("evidence.manifest_drift", errors)

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

    def test_project_axiom_report_replacement(self):
        self.assertIn("evidence.manifest_drift", self.append("theorem-registry/evidence/project-axioms.json"))

    def test_all_module_fresh_check_replacement(self):
        self.assertIn("evidence.manifest_drift", self.append("theorem-registry/evidence/all-module-fresh-check.json"))

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
        errors = self.mutate(path, lambda target: target.write_text(target.read_text().replace('"status": "IN_REVIEW"', '"status": "READY"')))
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


class PredecessorAncestryTests(unittest.TestCase):
    def setUp(self):
        self._temp = tempfile.TemporaryDirectory(prefix="statqed-sq0007-ancestry-")
        self.root = Path(self._temp.name) / "repo"
        self.root.mkdir()
        self.git_run("init", "-q", "-b", "task")
        self.git_run("config", "user.email", "sq0007-tests@example.invalid")
        self.git_run("config", "user.name", "SQ-0007 test")
        (self.root / "task").mkdir()
        (self.root / "pred").mkdir()
        (self.root / "task/base.txt").write_text("base\n")
        self.commit("launch")
        self.launch = self.rev()

        (self.root / "task/prototype.txt").write_text("prototype\n")
        self.commit("prototype")
        self.prototype = self.rev()
        (self.root / "task/blocked.txt").write_text("blocked\n")
        self.commit("blocked")
        self.blocked = self.rev()

        self.git_run("switch", "-q", "-c", "phase-m", self.launch)
        (self.root / "pred/phase-m.txt").write_text("phase m\n")
        self.commit("phase m")
        self.phase_m = self.rev()
        self.git_run("switch", "-q", "task")
        self.git_run("merge", "--no-ff", "-q", self.phase_m, "-m", "integrate phase m")
        self.merge_m = self.rev()

        self.git_run("switch", "-q", "-c", "phase-f", self.phase_m)
        (self.root / "pred/phase-f.txt").write_text("phase f\n")
        self.commit("phase f")
        self.phase_f = self.rev()
        self.git_run("switch", "-q", "task")
        self.git_run("merge", "--no-ff", "-q", self.phase_f, "-m", "integrate phase f")
        self.merge_f = self.rev()

        self.git_run("switch", "-q", "-c", "phase-t", self.phase_f)
        (self.root / "pred/phase-t.txt").write_text("phase t\n")
        self.commit("phase t")
        self.phase_t = self.rev()
        self.git_run("switch", "-q", "task")
        self.git_run("merge", "--no-ff", "-q", self.phase_t, "-m", "integrate phase t")
        self.merge_t = self.rev()
        self.spec = {
            "historical_launch_base": self.launch,
            "historical_task_commits": {
                "prototype": self.prototype,
                "blocked_head": self.blocked,
            },
            "verified_predecessor_chain": [
                {
                    "phase": "phase_m_compositional_evidence",
                    "predecessor_tip": self.phase_m,
                    "task_integration_merge": self.merge_m,
                    "first_parent": self.blocked,
                    "second_parent": self.phase_m,
                },
                {
                    "phase": "phase_f_fixture_neutrality",
                    "predecessor_tip": self.phase_f,
                    "task_integration_merge": self.merge_f,
                    "first_parent": self.merge_m,
                    "second_parent": self.phase_f,
                },
                {
                    "phase": "phase_t_branch_relative_live_report_fixtures",
                    "predecessor_tip": self.phase_t,
                    "task_integration_merge": self.merge_t,
                    "first_parent": self.merge_f,
                    "second_parent": self.phase_t,
                },
            ],
            "verified_predecessor_tip": self.phase_t,
        }

    def tearDown(self):
        self._temp.cleanup()

    def git_run(self, *arguments: str):
        subprocess.run(
            ["git", *arguments],
            cwd=self.root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def rev(self) -> str:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.root, text=True).strip()

    def commit(self, message: str):
        self.git_run("add", "--all")
        self.git_run("commit", "-q", "-m", message)

    def test_reviewed_normal_predecessor_chain_verifies(self):
        self.assertEqual(check_evidence.ancestry_errors(self.root, self.spec), [])

    def test_predecessor_tip_not_in_ancestry_is_rejected(self):
        self.git_run("switch", "-q", "-c", "unmerged", self.phase_t)
        (self.root / "pred/unmerged.txt").write_text("unmerged\n")
        self.commit("unmerged predecessor")
        unmerged = self.rev()
        self.git_run("switch", "-q", "task")
        changed = json.loads(json.dumps(self.spec))
        changed["verified_predecessor_chain"][-1]["predecessor_tip"] = unmerged
        changed["verified_predecessor_chain"][-1]["second_parent"] = unmerged
        changed["verified_predecessor_tip"] = unmerged
        self.assertIn(
            "evidence.predecessor_tip_not_in_ancestry:phase_t_branch_relative_live_report_fixtures",
            check_evidence.ancestry_errors(self.root, changed),
        )

    def test_unverified_predecessor_substitution_is_rejected(self):
        changed = json.loads(json.dumps(self.spec))
        changed["verified_predecessor_chain"][-1]["predecessor_tip"] = self.launch
        self.assertTrue(any("predecessor" in error for error in check_evidence.ancestry_errors(self.root, changed)))

    def test_rewritten_history_dropping_blocked_head_is_rejected(self):
        changed = json.loads(json.dumps(self.spec))
        changed["historical_task_commits"]["blocked_head"] = self.phase_t
        self.assertIn("evidence.historical_task_history_rewritten", check_evidence.ancestry_errors(self.root, changed))

    def test_task_local_path_outside_contract_is_rejected(self):
        (self.root / "outside.txt").write_text("outside\n")
        errors = check_evidence.active_scope_errors(self.root, self.phase_t, self.launch, ["task/**"])
        self.assertIn("evidence.path_outside_contract:outside.txt", errors)

    def test_predecessor_only_file_modified_again_is_rejected(self):
        (self.root / "pred/phase-t.txt").write_text("changed by task\n")
        errors = check_evidence.active_scope_errors(self.root, self.phase_t, self.launch, ["task/**"])
        self.assertIn("evidence.predecessor_file_modified_by_task:pred/phase-t.txt", errors)

    def test_launch_base_replacement_is_rejected(self):
        changed = json.loads(json.dumps(self.spec))
        changed["historical_launch_base"] = self.phase_m
        self.assertIn("evidence.launch_base_replaced", check_evidence.ancestry_errors(self.root, changed))

    def test_predecessor_chain_truncation_is_rejected(self):
        changed = json.loads(json.dumps(self.spec))
        changed["verified_predecessor_chain"] = changed["verified_predecessor_chain"][1:]
        self.assertIn("evidence.predecessor_chain_unverified", check_evidence.ancestry_errors(self.root, changed))


if __name__ == "__main__":
    unittest.main()
