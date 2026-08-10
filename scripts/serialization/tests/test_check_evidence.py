"""Corruption and lifecycle tests for the permanent SQ-0005 verifier."""

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
SPEC = Path("conformance/prototypes/evidence/evidence-spec.json")
REVIEW_BEGIN = "<!-- SQ-0005-REVIEW-SUBJECTS-BEGIN -->"
REVIEW_END = "<!-- SQ-0005-REVIEW-SUBJECTS-END -->"
SCOPE_BEGIN = "<!-- SQ-0005-NORMATIVE-SCOPE-BEGIN -->"
SCOPE_END = "<!-- SQ-0005-NORMATIVE-SCOPE-END -->"
SUCCESSORS_AFTER_SQ0006 = (
    "SQ-0007",
    "SQ-0011",
    "SQ-0013",
    "SQ-0014",
    "SQ-0015",
)
HIGH_VALUE_PATHS = (
    "rfcs/0001-deterministic-encoding.md",
    "docs/adr/0004-deterministic-cbor-cddl.md",
    "docs/research/serialization/profile-candidate.md",
    "docs/research/serialization/semantic-value-model.md",
    "conformance/prototypes/fixtures/semantic-v1/catalog.json",
    "conformance/prototypes/generated-v1/manifest.json",
    "conformance/prototypes/generated-v1/mutations.json",
    "conformance/prototypes/golden/serialization-v1/manifest.json",
    "schemas/prototypes/lineage.json",
    "schemas/prototypes/python-oracle/LINEAGE.md",
    "schemas/prototypes/rust-cbor/Cargo.lock",
    "schemas/prototypes/rust-cbor/LINEAGE.md",
    "source-audits/encoding/manifest.json",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def canonical_write(path: Path, value: object) -> None:
    path.write_bytes(canonical_bytes(value))


class EvidenceCorruptionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(
            prefix="statqed-evidence-corruption-"
        )
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
        self.frozen_manifest = (self.root / MANIFEST).read_bytes()
        self.frozen_spec = (self.root / SPEC).read_bytes()
        manifest = self.manifest()
        self.frozen_historical_state = canonical_bytes(
            manifest["historical_completion_state"]
        )
        self.frozen_historical_sq0008 = manifest["baseline"][
            "sq0008_contract_sha256"
        ]
        self.frozen_historical_contracts = canonical_bytes(
            manifest["historical_successor_contracts"]
        )
        self.frozen_high_value = {
            path: digest(self.root / path) for path in HIGH_VALUE_PATHS
        }

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_command(self, arguments: list[str]) -> tuple[int, str]:
        completed = subprocess.run(
            arguments,
            cwd=self.root,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            timeout=30,
            env={"PYTHONDONTWRITEBYTECODE": "1"},
        )
        return completed.returncode, completed.stdout + completed.stderr

    def run_check(self) -> tuple[int, str]:
        return self.run_command(
            [
                sys.executable,
                str(self.root / "scripts/serialization/check_evidence.py"),
                "--root",
                str(self.root),
                "--json",
            ]
        )

    def run_repository_check(self) -> tuple[int, str]:
        return self.run_command(
            [sys.executable, str(self.root / "scripts/check_repository.py")]
        )

    def assert_verified(self, repository: bool = False) -> None:
        status, output = self.run_check()
        self.assertEqual(status, 0, output)
        if repository:
            status, output = self.run_repository_check()
            self.assertEqual(status, 0, output)

    def assert_rejected(self, fragment: str) -> None:
        status, output = self.run_check()
        self.assertNotEqual(status, 0, output)
        self.assertIn(fragment, output)

    def assert_frozen_evidence_unchanged(self) -> None:
        self.assertEqual((self.root / MANIFEST).read_bytes(), self.frozen_manifest)
        self.assertEqual((self.root / SPEC).read_bytes(), self.frozen_spec)
        manifest = self.manifest()
        self.assertEqual(
            canonical_bytes(manifest["historical_completion_state"]),
            self.frozen_historical_state,
        )
        self.assertEqual(
            manifest["baseline"]["sq0008_contract_sha256"],
            self.frozen_historical_sq0008,
        )
        self.assertEqual(
            canonical_bytes(manifest["historical_successor_contracts"]),
            self.frozen_historical_contracts,
        )
        self.assertEqual(
            {path: digest(self.root / path) for path in HIGH_VALUE_PATHS},
            self.frozen_high_value,
        )

    def manifest(self) -> dict:
        return json.loads((self.root / MANIFEST).read_text(encoding="utf-8"))

    def write_manifest(self, value: dict) -> None:
        canonical_write(self.root / MANIFEST, value)

    def live_subject_with_prefix(self, prefix: str) -> str:
        for item in self.manifest()["live_subjects"]:
            if item["path"].startswith(prefix):
                return item["path"]
        self.fail(f"no live subject with prefix {prefix}")

    def update_live_subject_hash(self, relative: str) -> None:
        manifest = self.manifest()
        for item in manifest["live_subjects"]:
            if item["path"] == relative:
                item["sha256"] = digest(self.root / relative)
                self.write_manifest(manifest)
                return
        self.fail(f"live subject absent: {relative}")

    def rewrite_review_bindings(self, changed: tuple[str, ...] = ()) -> None:
        manifest = self.manifest()
        review_path = self.root / manifest["review_record"]
        text = review_path.read_text(encoding="utf-8")
        start = text.index(REVIEW_BEGIN) + len(REVIEW_BEGIN)
        end = text.index(REVIEW_END)
        body = text[start:end].strip()
        fenced = body.startswith("```json")
        if fenced:
            body = body[len("```json") : -len("```")].strip()
        bindings = json.loads(body)
        for relative in changed:
            bindings[relative] = digest(self.root / relative)
        bindings[MANIFEST.as_posix()] = digest(self.root / MANIFEST)
        replacement = json.dumps(bindings, indent=2, sort_keys=True)
        if fenced:
            replacement = "```json\n" + replacement + "\n```"
        review_path.write_text(
            text[:start] + "\n" + replacement + "\n" + text[end:],
            encoding="utf-8",
        )

    def rebind_live_subject(self, relative: str) -> None:
        self.update_live_subject_hash(relative)
        self.rewrite_review_bindings((relative,))

    def set_task_status(self, task_id: str, new_status: str) -> None:
        contract_path = self.root / f"work/contracts/{task_id}.yaml"
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        contract["status"] = new_status
        canonical_write(contract_path, contract)

        backlog_path = self.root / "work/backlog.yaml"
        backlog = json.loads(backlog_path.read_text(encoding="utf-8"))
        matches = [item for item in backlog["tasks"] if item["id"] == task_id]
        self.assertEqual(len(matches), 1)
        matches[0]["status"] = new_status
        canonical_write(backlog_path, backlog)

        status_path = self.root / "work/status.yaml"
        status = json.loads(status_path.read_text(encoding="utf-8"))
        for bucket in ("ready", "in_progress", "done"):
            status[bucket] = [value for value in status[bucket] if value != task_id]
        bucket = {
            "READY": "ready",
            "IN_PROGRESS": "in_progress",
            "IN_REVIEW": "in_progress",
            "DONE": "done",
        }.get(new_status)
        if bucket is not None:
            status[bucket] = sorted([*status[bucket], task_id])
        canonical_write(status_path, status)

    def transition_sq0006(self, new_status: str) -> None:
        self.set_task_status("SQ-0006", new_status)
        if new_status == "DONE":
            for task_id in SUCCESSORS_AFTER_SQ0006:
                self.set_task_status(task_id, "READY")
            status_path = self.root / "work/status.yaml"
            status = json.loads(status_path.read_text(encoding="utf-8"))
            status["blocked_count"] = 48
            canonical_write(status_path, status)

    def mutate_status_header(self, relative: str, replacement: str) -> None:
        path = self.root / relative
        text = path.read_text(encoding="utf-8")
        text = text.replace("- Status: Accepted", f"- Status: {replacement}", 1)
        path.write_text(text, encoding="utf-8")
        self.rebind_live_subject(relative)

    # Original twelve corruption tests remain effective.

    def test_baseline_is_verified(self) -> None:
        self.assert_verified()

    def test_changed_profile_text_is_rejected(self) -> None:
        path = self.root / "docs/research/serialization/profile-candidate.md"
        path.write_text(
            path.read_text(encoding="utf-8") + "\ncorruption\n", encoding="utf-8"
        )
        self.assert_rejected("subject SHA-256 mismatch")

    def test_changed_source_audit_is_rejected(self) -> None:
        relative = self.live_subject_with_prefix("source-audits/encoding/")
        path = self.root / relative
        path.write_text(
            path.read_text(encoding="utf-8") + "\ncorruption: true\n",
            encoding="utf-8",
        )
        self.assert_rejected("subject SHA-256 mismatch")

    def test_replaced_golden_bytes_are_rejected(self) -> None:
        matches = [
            item["path"]
            for item in self.manifest()["live_subjects"]
            if item["path"].startswith("conformance/prototypes/golden/")
            and not item["path"].endswith("manifest.json")
        ]
        self.assertTrue(matches)
        path = self.root / matches[0]
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
        self.rebind_live_subject(relative)
        self.assert_rejected("share canonicalizer lineage")

    def test_stale_review_hash_is_rejected(self) -> None:
        review_path = self.root / self.manifest()["review_record"]
        text = review_path.read_text(encoding="utf-8")
        start = text.index(REVIEW_BEGIN) + len(REVIEW_BEGIN)
        end = text.index(REVIEW_END)
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
        review_path.write_text(
            text[:start] + "\n" + replacement + "\n" + text[end:],
            encoding="utf-8",
        )
        self.assert_rejected("stale review hash")

    def test_status_drift_is_rejected(self) -> None:
        path = self.root / "work/backlog.yaml"
        backlog = json.loads(path.read_text(encoding="utf-8"))
        for item in backlog["tasks"]:
            if item["id"] == "SQ-0005":
                item["status"] = "IN_REVIEW"
        canonical_write(path, backlog)
        self.assert_rejected("SQ-0005 live status regressed")

    def test_rfc0006_modification_is_rejected(self) -> None:
        path = self.root / "rfcs/0006-canonical-logical-data-digest.md"
        path.write_text(
            path.read_text(encoding="utf-8") + "\ncorruption\n", encoding="utf-8"
        )
        self.assert_rejected("RFC-0006 changed")

    def test_sq0008_modification_is_rejected(self) -> None:
        path = self.root / "work/contracts/SQ-0008.yaml"
        contract = json.loads(path.read_text(encoding="utf-8"))
        contract["objective"] += " semantic corruption"
        canonical_write(path, contract)
        self.assert_rejected("SQ-0008 non-lifecycle contract projection changed")

    def test_production_backend_contamination_is_rejected(self) -> None:
        path = self.root / "backend/contamination.rs"
        path.write_text("// prohibited SQ-0005 contamination\n", encoding="utf-8")
        self.assert_rejected("protected production path-set drift")

    # Lifecycle-model regressions cover required positive and negative cases.

    def test_lifecycle_historical_completion_snapshot_verifies(self) -> None:
        self.assertEqual(
            self.manifest()["historical_completion_state"],
            json.loads(self.frozen_historical_state),
        )
        self.assert_verified()

    def test_lifecycle_sq0006_ready_verifies(self) -> None:
        self.assert_verified(repository=True)
        self.assert_frozen_evidence_unchanged()

    def test_lifecycle_sq0006_in_progress_verifies_with_schema_path(self) -> None:
        self.transition_sq0006("IN_PROGRESS")
        schema = self.root / "schemas/v0/README.md"
        schema.parent.mkdir(parents=True)
        schema.write_text("# simulated successor-owned schema\n", encoding="utf-8")
        self.assert_verified(repository=True)
        self.assert_frozen_evidence_unchanged()

    def test_lifecycle_sq0006_in_review_verifies(self) -> None:
        self.transition_sq0006("IN_REVIEW")
        self.assert_verified(repository=True)
        self.assert_frozen_evidence_unchanged()

    def test_lifecycle_sq0006_done_verifies_with_recomputed_successors(self) -> None:
        self.transition_sq0006("DONE")
        self.assert_verified(repository=True)
        self.assert_frozen_evidence_unchanged()

    def test_lifecycle_sq0008_status_only_transition_verifies(self) -> None:
        self.set_task_status("SQ-0008", "IN_PROGRESS")
        self.assert_verified(repository=True)
        self.assert_frozen_evidence_unchanged()

    def test_lifecycle_sq0005_in_review_regression_is_rejected(self) -> None:
        self.set_task_status("SQ-0005", "IN_REVIEW")
        self.assert_rejected("SQ-0005 live status regressed")

    def test_lifecycle_sq0005_ready_regression_is_rejected(self) -> None:
        self.set_task_status("SQ-0005", "READY")
        self.assert_rejected("SQ-0005 live status regressed")

    def test_lifecycle_sq0006_contract_backlog_disagreement_is_rejected(self) -> None:
        path = self.root / "work/contracts/SQ-0006.yaml"
        contract = json.loads(path.read_text(encoding="utf-8"))
        contract["status"] = "IN_PROGRESS"
        canonical_write(path, contract)
        self.assert_rejected("SQ-0006 contract/backlog status disagreement")

    def test_lifecycle_sq0006_illegal_status_is_rejected(self) -> None:
        self.set_task_status("SQ-0006", "BLOCKED")
        self.assert_rejected("SQ-0006 has illegal lifecycle status")

    def test_lifecycle_historical_snapshot_mutation_is_rejected_after_rebind(self) -> None:
        manifest = self.manifest()
        manifest["historical_completion_state"]["blocked_count"] = 52
        self.write_manifest(manifest)
        self.rewrite_review_bindings()
        self.assert_rejected("historical SQ-0005 completion snapshot changed")

    def test_lifecycle_historical_successor_contract_binding_mutation_is_rejected(
        self,
    ) -> None:
        manifest = self.manifest()
        manifest["historical_successor_contracts"]["SQ-0006"]["sha256"] = "0" * 64
        self.write_manifest(manifest)
        self.assert_rejected("historical successor contract bindings changed")

    def test_lifecycle_rfc0001_draft_is_rejected_after_rebind(self) -> None:
        relative = "rfcs/0001-deterministic-encoding.md"
        self.mutate_status_header(relative, "Draft")
        self.assert_rejected("RFC-0001 live status is not Accepted")

    def test_lifecycle_adr0004_draft_is_rejected_after_rebind(self) -> None:
        relative = "docs/adr/0004-deterministic-cbor-cddl.md"
        self.mutate_status_header(relative, "Draft")
        self.assert_rejected("ADR-0004 live status is not Accepted")

    def test_lifecycle_normative_scope_divergence_is_rejected_after_rebind(self) -> None:
        relative = "docs/adr/0004-deterministic-cbor-cddl.md"
        path = self.root / relative
        text = path.read_text(encoding="utf-8")
        start = text.index(SCOPE_BEGIN) + len(SCOPE_BEGIN)
        end = text.index(SCOPE_END)
        text = text[:end] + "\nsemantic corruption\n" + text[end:]
        path.write_text(text, encoding="utf-8")
        self.rebind_live_subject(relative)
        self.assert_rejected("normative scopes disagree")

    def test_lifecycle_rfc0006_ownership_drift_is_rejected(self) -> None:
        path = self.root / "work/backlog.yaml"
        backlog = json.loads(path.read_text(encoding="utf-8"))
        for item in backlog["decision_register"]:
            if item["id"] == "RFC-0006":
                item["owner"] = "SQ-0006"
        canonical_write(path, backlog)
        self.assert_rejected("RFC-0006 ownership drift")

    def test_lifecycle_sq0008_non_status_mutation_is_rejected(self) -> None:
        path = self.root / "work/contracts/SQ-0008.yaml"
        contract = json.loads(path.read_text(encoding="utf-8"))
        contract["allowed_paths"].append("forbidden-semantic-expansion/**")
        canonical_write(path, contract)
        self.assert_rejected("SQ-0008 non-lifecycle contract projection changed")

    def test_lifecycle_protected_file_change_is_rejected(self) -> None:
        path = self.root / "backend/README.md"
        path.write_text(
            path.read_text(encoding="utf-8") + "\ncontamination\n", encoding="utf-8"
        )
        self.assert_rejected("protected production file changed")

    def test_lifecycle_scientific_subject_change_is_rejected(self) -> None:
        path = self.root / "docs/research/serialization/semantic-value-model.md"
        path.write_text(
            path.read_text(encoding="utf-8") + "\nsemantic drift\n",
            encoding="utf-8",
        )
        self.assert_rejected("subject SHA-256 mismatch")

    def test_lifecycle_canonicalization_owned_section_change_is_rejected(self) -> None:
        path = self.root / "docs/spec/canonicalization.md"
        text = path.read_text(encoding="utf-8").replace(
            "ordering is rejected.",
            "ordering is accepted.",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assert_rejected("shared SQ-0005 document projection changed")

    def test_lifecycle_dashboard_sq0005_claim_change_is_rejected(self) -> None:
        path = self.root / "docs/quality/dashboard.md"
        text = path.read_text(encoding="utf-8").replace(
            "It is not a production canonicalizer",
            "It is a production canonicalizer",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assert_rejected("shared SQ-0005 document projection changed")

    def test_lifecycle_successor_document_additions_verify(self) -> None:
        canonicalization = self.root / "docs/spec/canonicalization.md"
        canonicalization.write_text(
            canonicalization.read_text(encoding="utf-8")
            + "## Successor-owned schema note\n\nExperimental successor evidence.\n",
            encoding="utf-8",
        )
        dashboard = self.root / "docs/quality/dashboard.md"
        dashboard.write_text(
            dashboard.read_text(encoding="utf-8")
            + "\nSuccessor-owned Experimental evidence.\n",
            encoding="utf-8",
        )
        self.assert_verified()

    def test_lifecycle_duplicate_makefile_target_is_rejected(self) -> None:
        path = self.root / "Makefile"
        path.write_text(
            path.read_text(encoding="utf-8")
            + "\ncheck-sq0005-evidence:\n\t@true\n",
            encoding="utf-8",
        )
        self.assert_rejected("Makefile target is not unique")

    def test_lifecycle_grouped_makefile_target_is_rejected(self) -> None:
        path = self.root / "Makefile"
        path.write_text(
            path.read_text(encoding="utf-8")
            + "\ncheck-sq0005-evidence &:\n\t@true\n",
            encoding="utf-8",
        )
        self.assert_rejected("Makefile target is not unique")

    def test_lifecycle_multitarget_makefile_override_is_rejected(self) -> None:
        path = self.root / "Makefile"
        path.write_text(
            path.read_text(encoding="utf-8")
            + "\nother check-sq0005-evidence:\n\t@true\n",
            encoding="utf-8",
        )
        self.assert_rejected("Makefile target is not unique")

    def test_lifecycle_indented_makefile_override_is_rejected(self) -> None:
        path = self.root / "Makefile"
        path.write_text(
            path.read_text(encoding="utf-8")
            + "\n check-sq0005-evidence:\n\t@true\n",
            encoding="utf-8",
        )
        self.assert_rejected("Makefile target is not unique")

    def test_lifecycle_variable_makefile_override_is_rejected(self) -> None:
        path = self.root / "Makefile"
        path.write_text(
            path.read_text(encoding="utf-8")
            + "\nprotected_target := check-sq0005-evidence\n"
            + "$(protected_target):\n\t@true\n",
            encoding="utf-8",
        )
        self.assert_rejected("Makefile assignments are prohibited")

    def test_lifecycle_missing_makefile_phony_membership_is_rejected(self) -> None:
        path = self.root / "Makefile"
        text = path.read_text(encoding="utf-8").replace(
            " check-sq0005-evidence", "", 1
        )
        path.write_text(text, encoding="utf-8")
        self.assert_rejected("evidence target is not uniquely phony")

    def test_lifecycle_makefile_ignore_special_target_is_rejected(self) -> None:
        path = self.root / "Makefile"
        path.write_text(
            path.read_text(encoding="utf-8")
            + "\n.IGNORE: check-sq0005-evidence\n",
            encoding="utf-8",
        )
        self.assert_rejected("Makefile special target is prohibited")

    def test_lifecycle_makeflags_ignore_errors_assignment_is_rejected(self) -> None:
        path = self.root / "Makefile"
        path.write_text(
            path.read_text(encoding="utf-8") + "\nMAKEFLAGS := -i\n",
            encoding="utf-8",
        )
        self.assert_rejected("Makefile assignments are prohibited")

    def test_lifecycle_phony_inline_comment_is_rejected(self) -> None:
        path = self.root / "Makefile"
        text = path.read_text(encoding="utf-8").replace(
            ".PHONY: check check-repo check-sq0002-evidence check-sq0005-evidence",
            ".PHONY: check check-repo check-sq0002-evidence # check-sq0005-evidence",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assert_rejected("Makefile inline comments are prohibited")

    def test_lifecycle_check_dependency_inline_comment_is_rejected(self) -> None:
        path = self.root / "Makefile"
        text = path.read_text(encoding="utf-8").replace(
            "check: check-repo check-sq0002-evidence check-sq0005-evidence",
            "check: check-repo check-sq0002-evidence # check-sq0005-evidence",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assert_rejected("Makefile inline comments are prohibited")

    def test_lifecycle_check_inline_recipe_is_rejected(self) -> None:
        path = self.root / "Makefile"
        text = path.read_text(encoding="utf-8").replace(
            "check: check-repo check-sq0002-evidence check-sq0005-evidence",
            "check: check-repo check-sq0002-evidence ; @echo check-sq0005-evidence",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assert_rejected("Makefile inline recipes are prohibited")

    def test_lifecycle_dashboard_html_comment_wrapper_is_rejected(self) -> None:
        path = self.root / "docs/quality/dashboard.md"
        text = path.read_text(encoding="utf-8")
        begin = text.index("SQ-0005 adds one Experimental deterministic")
        marker = "does not define logical-data identity."
        end = text.index(marker, begin) + len(marker)
        path.write_text(text[:begin] + "<!-- " + text[begin:end] + " -->" + text[end:], encoding="utf-8")
        self.assert_rejected("quality dashboard uses prohibited wrapping markup")

    def test_lifecycle_dashboard_strikethrough_wrapper_is_rejected(self) -> None:
        path = self.root / "docs/quality/dashboard.md"
        text = path.read_text(encoding="utf-8")
        begin = text.index("SQ-0005 adds one Experimental deterministic")
        marker = "does not define logical-data identity."
        end = text.index(marker, begin) + len(marker)
        path.write_text(text[:begin] + "~~" + text[begin:end] + "~~" + text[end:], encoding="utf-8")
        self.assert_rejected("quality dashboard uses prohibited wrapping markup")

    def test_lifecycle_dashboard_link_wrapper_is_rejected(self) -> None:
        path = self.root / "docs/quality/dashboard.md"
        text = path.read_text(encoding="utf-8")
        begin = text.index("SQ-0005 adds one Experimental deterministic")
        marker = "does not define logical-data identity."
        end = text.index(marker, begin) + len(marker)
        path.write_text(text[:begin] + "[" + text[begin:end] + "](https://example.invalid)" + text[end:], encoding="utf-8")
        self.assert_rejected("shared SQ-0005 document projection changed")

    def test_lifecycle_active_review_redirection_is_rejected(self) -> None:
        manifest = self.manifest()
        original = self.root / manifest["review_record"]
        redirected = self.root / "work/reviews/fake-review.md"
        redirected.write_bytes(original.read_bytes())
        manifest["review_record"] = "work/reviews/fake-review.md"
        self.write_manifest(manifest)
        self.assert_rejected("active SQ-0005 lifecycle review path changed")

    def test_lifecycle_global_blocked_count_is_repository_owned(self) -> None:
        path = self.root / "work/status.yaml"
        status = json.loads(path.read_text(encoding="utf-8"))
        status["blocked_count"] = 52
        canonical_write(path, status)
        self.assert_verified()
        returncode, output = self.run_repository_check()
        self.assertNotEqual(returncode, 0, output)
        self.assertIn("blocked_count", output)


if __name__ == "__main__":
    unittest.main()
