from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest


SCRIPT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from check_schema_v0 import EvidenceError, protected_files, protected_partition_digest, verify


ROOT = Path(__file__).resolve().parents[3]
EMPTY_REGISTRY_PARTITIONS = (
    "lean/StatQED/Registry",
    "backend/crates/statqed-registry",
)
EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


class EvidenceCorruptionTests(unittest.TestCase):
    def setUp(self):
        self._shadow_roots: set[Path] = set()

    def shadow(self):
        temporary = tempfile.TemporaryDirectory(prefix="statqed-sq0006-corrupt-")
        destination = Path(temporary.name) / "repo"
        destination.mkdir()
        tracked = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "-z"],
            check=True,
            capture_output=True,
        ).stdout.split(b"\0")
        for raw in tracked:
            if not raw:
                continue
            relative = Path(raw.decode())
            source = ROOT / relative
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        # A maintenance candidate can bind newly added live trust files before
        # its review commit exists. Copy the spec-declared set explicitly; do
        # not widen the shadow to arbitrary untracked workspace content.
        spec = json.loads((ROOT / "conformance/schema-v0/evidence/evidence-spec.json").read_text())
        for relative_text in spec.get("maintenance_live_baseline_paths", []):
            relative = Path(relative_text)
            source = ROOT / relative
            target = destination / relative
            if source.is_file() and not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
        self._shadow_roots.add(destination.resolve())
        return temporary, destination

    def neutralize_ambient_sq0007_registry_paths(
        self,
        root: Path,
        relative_roots: tuple[str, ...] = EMPTY_REGISTRY_PARTITIONS,
    ) -> tuple[str, ...]:
        """Restore only the historically empty Registry partitions in a shadow."""

        resolved_root = root.resolve()
        if (
            resolved_root == ROOT.resolve()
            or resolved_root == Path(resolved_root.anchor)
            or resolved_root not in self._shadow_roots
            or not (root / "work/status.yaml").is_file()
        ):
            raise ValueError("neutralizer requires an isolated temporary repository copy")
        if tuple(relative_roots) != EMPTY_REGISTRY_PARTITIONS:
            raise ValueError("neutralizer roots must equal the exact Registry allowlist")

        spec = json.loads(
            (root / "conformance/schema-v0/evidence/evidence-spec.json").read_text()
        )
        partitions = {
            item["id"]: item for item in spec["protected_path_policy"]["partitions"]
        }
        for partition_id in ("lean_registry", "backend_registry"):
            policy = partitions[partition_id]
            self.assertEqual(0, policy["baseline_file_count"])
            self.assertEqual(EMPTY_SHA256, policy["baseline_sha256"])

        removal_plans: list[tuple[list[Path], list[Path]]] = []
        removed: list[str] = []
        for relative in EMPTY_REGISTRY_PARTITIONS:
            target = root / relative
            current = root
            for part in Path(relative).parts:
                current = current / part
                if current.is_symlink():
                    raise ValueError(f"neutralizer refuses symlink traversal: {relative}")
            try:
                target_mode = target.lstat().st_mode
            except FileNotFoundError:
                continue
            if not stat.S_ISDIR(target_mode):
                raise ValueError(f"neutralizer refuses non-directory root: {relative}")

            directories: list[Path] = []
            target_files: list[Path] = []
            for directory, names, files in os.walk(target, topdown=True, followlinks=False):
                directory_path = Path(directory)
                directories.append(directory_path)
                for name in sorted([*names, *files]):
                    path = directory_path / name
                    mode = path.lstat().st_mode
                    if stat.S_ISLNK(mode):
                        raise ValueError(
                            f"neutralizer refuses symlink entry: {path.relative_to(root)}"
                        )
                    if not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                        raise ValueError(
                            f"neutralizer refuses special entry: {path.relative_to(root)}"
                        )
                    if stat.S_ISREG(mode):
                        target_files.append(path)
                        removed.append(path.relative_to(root).as_posix())
            removal_plans.append((target_files, directories))
        for target_files, directories in removal_plans:
            for path in sorted(target_files):
                path.unlink()
            for directory in sorted(directories, key=lambda path: len(path.parts), reverse=True):
                directory.rmdir()
        return tuple(sorted(removed))

    def mutate(self, root: Path, relative: str, transform):
        path = root / relative
        data = path.read_bytes()
        path.unlink()
        changed = transform(data)
        path.write_bytes(changed)

    def assert_rejected(self, relative: str, transform, reason: str | None = None):
        temporary, root = self.shadow()
        try:
            self.mutate(root, relative, transform)
            with self.assertRaises(EvidenceError) as caught:
                verify(root)
            if reason is not None:
                self.assertIn(reason, str(caught.exception))
        finally:
            temporary.cleanup()

    def write_json(self, root: Path, relative: str, document):
        path = root / relative
        path.unlink()
        path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")

    def set_task_state(self, root: Path, task_id: str, state: str):
        contract = json.loads((root / f"work/contracts/{task_id}.yaml").read_text())
        backlog = json.loads((root / "work/backlog.yaml").read_text())
        status = json.loads((root / "work/status.yaml").read_text())
        contract["status"] = state
        next(task for task in backlog["tasks"] if task["id"] == task_id)["status"] = state
        for key in ("ready", "in_progress", "done"):
            status[key] = [item for item in status[key] if item != task_id]
        if state == "READY":
            status["ready"].append(task_id)
        elif state in {"IN_PROGRESS", "IN_REVIEW"}:
            status["in_progress"].append(task_id)
        elif state == "DONE":
            status["done"].append(task_id)
        for key in ("ready", "in_progress", "done"):
            status[key].sort()
        status["blocked_count"] = sum(item["status"] == "BLOCKED" for item in backlog["tasks"])
        self.write_json(root, f"work/contracts/{task_id}.yaml", contract)
        self.write_json(root, "work/backlog.yaml", backlog)
        self.write_json(root, "work/status.yaml", status)

    def expand_contract(self, root: Path, task_id: str):
        contract = json.loads((root / f"work/contracts/{task_id}.yaml").read_text())
        contract["planning_review_probe"] = {"purpose": "non-status successor planning"}
        self.write_json(root, f"work/contracts/{task_id}.yaml", contract)

    def add_file(self, root: Path, relative: str):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("lifecycle ownership probe\n", encoding="utf-8")

    def rebuild_manifest(self, root: Path):
        subprocess.run(
            [sys.executable, "scripts/schema/build_evidence_manifest.py"],
            cwd=root,
            check=True,
            capture_output=True,
        )

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
        for state in ("IN_PROGRESS", "IN_REVIEW"):
            with self.subTest(state=state):
                temporary, root = self.shadow()
                try:
                    self.set_task_state(root, "SQ-0006", state)
                    with self.assertRaisesRegex(EvidenceError, "SQ-0006 contract/backlog lifecycle mismatch"):
                        verify(root)
                finally:
                    temporary.cleanup()
        temporary, root = self.shadow()
        try:
            verify(root)
        finally:
            temporary.cleanup()

    # Phase-A successor-planning and path-ownership regression matrix.
    def test_phase_a_01_sq0007_ready_contract_expansion(self):
        temporary, root = self.shadow()
        try:
            self.neutralize_ambient_sq0007_registry_paths(root)
            self.set_task_state(root, "SQ-0007", "READY")
            verify(root)
            self.expand_contract(root, "SQ-0007")
            verify(root)
        finally:
            temporary.cleanup()

    def test_phase_a_02_sq0008_ready_contract_expansion(self):
        temporary, root = self.shadow()
        try:
            self.neutralize_ambient_sq0007_registry_paths(root)
            self.set_task_state(root, "SQ-0007", "READY")
            self.set_task_state(root, "SQ-0008", "READY")
            verify(root)
            self.expand_contract(root, "SQ-0008")
            verify(root)
        finally:
            temporary.cleanup()

    def test_phase_a_03_sq0011_ready_contract_expansion(self):
        temporary, root = self.shadow()
        try:
            self.neutralize_ambient_sq0007_registry_paths(root)
            self.set_task_state(root, "SQ-0007", "READY")
            self.set_task_state(root, "SQ-0011", "READY")
            verify(root)
            self.expand_contract(root, "SQ-0011")
            verify(root)
        finally:
            temporary.cleanup()

    def test_phase_a_04_sq0013_ready_contract_expansion(self):
        temporary, root = self.shadow()
        try:
            self.neutralize_ambient_sq0007_registry_paths(root)
            self.set_task_state(root, "SQ-0007", "READY")
            self.set_task_state(root, "SQ-0013", "READY")
            verify(root)
            self.expand_contract(root, "SQ-0013")
            verify(root)
        finally:
            temporary.cleanup()

    def test_phase_a_05_sq0014_ready_contract_expansion(self):
        temporary, root = self.shadow()
        try:
            self.neutralize_ambient_sq0007_registry_paths(root)
            self.set_task_state(root, "SQ-0007", "READY")
            self.set_task_state(root, "SQ-0014", "READY")
            verify(root)
            self.expand_contract(root, "SQ-0014")
            verify(root)
        finally:
            temporary.cleanup()

    def test_phase_a_06_sq0015_ready_contract_expansion(self):
        temporary, root = self.shadow()
        try:
            self.neutralize_ambient_sq0007_registry_paths(root)
            self.set_task_state(root, "SQ-0007", "READY")
            self.set_task_state(root, "SQ-0015", "READY")
            verify(root)
            self.expand_contract(root, "SQ-0015")
            verify(root)
        finally:
            temporary.cleanup()

    def test_phase_a_07_contract_expansion_preserves_historical_hashes(self):
        temporary, root = self.shadow()
        try:
            self.neutralize_ambient_sq0007_registry_paths(root)
            self.set_task_state(root, "SQ-0007", "READY")
            verify(root)
            before = json.loads((root / "conformance/schema-v0/evidence/evidence-spec.json").read_text())[
                "historical_successor_contracts"
            ]
            for task in ("SQ-0007", "SQ-0008", "SQ-0011", "SQ-0013", "SQ-0014", "SQ-0015"):
                self.expand_contract(root, task)
            verify(root)
            after = json.loads((root / "conformance/schema-v0/evidence/evidence-spec.json").read_text())[
                "historical_successor_contracts"
            ]
            self.assertEqual(before, after)
        finally:
            temporary.cleanup()

    def test_phase_a_08_contract_expansion_needs_no_manifest_regeneration(self):
        temporary, root = self.shadow()
        try:
            self.neutralize_ambient_sq0007_registry_paths(root)
            self.set_task_state(root, "SQ-0007", "READY")
            verify(root)
            manifest_path = root / "conformance/schema-v0/evidence/evidence-manifest.json"
            before = manifest_path.read_bytes()
            historical = json.loads(before)["historical_scientific_subject_digest"]
            self.expand_contract(root, "SQ-0007")
            verify(root)
            self.assertEqual(before, manifest_path.read_bytes())
            self.assertEqual(
                "4bfd5fad7f9884d592d5c8c320dbd4efd735c990f3b23d6b3cb5d8e9854df5f0",
                historical,
            )
        finally:
            temporary.cleanup()

    def test_phase_a_09_sq0006_semantic_contract_mutation_rejected(self):
        self.assert_rejected(
            "work/contracts/SQ-0006.yaml",
            lambda data: data.replace(b'"objective":', b'"mutated_objective":', 1),
            "SQ-0006 non-lifecycle contract drift",
        )
        temporary, root = self.shadow()
        try:
            self.add_file(root, "backend/unauthorized-baseline-redefinition.txt")
            spec = json.loads((root / "conformance/schema-v0/evidence/evidence-spec.json").read_text())
            policy = next(
                item for item in spec["protected_path_policy"]["partitions"]
                if item["id"] == "backend_remainder"
            )
            digest, count = protected_partition_digest(protected_files(root, "backend", ()), policy)
            policy["baseline_sha256"] = digest
            policy["baseline_file_count"] = count
            self.write_json(root, "conformance/schema-v0/evidence/evidence-spec.json", spec)
            self.rebuild_manifest(root)
            with self.assertRaisesRegex(EvidenceError, "protected path policy drift"):
                verify(root)
        finally:
            temporary.cleanup()

    def test_phase_a_10_successor_contract_backlog_disagreement_rejected(self):
        temporary, root = self.shadow()
        try:
            self.neutralize_ambient_sq0007_registry_paths(root)
            self.set_task_state(root, "SQ-0007", "READY")
            verify(root)
            contract = json.loads((root / "work/contracts/SQ-0007.yaml").read_text())
            contract["status"] = "IN_PROGRESS"
            self.write_json(root, "work/contracts/SQ-0007.yaml", contract)
            with self.assertRaisesRegex(EvidenceError, "SQ-0007 contract/backlog lifecycle mismatch"):
                verify(root)
        finally:
            temporary.cleanup()

    def test_phase_a_11_illegal_successor_status_rejected(self):
        temporary, root = self.shadow()
        try:
            self.neutralize_ambient_sq0007_registry_paths(root)
            self.set_task_state(root, "SQ-0007", "READY")
            verify(root)
            self.set_task_state(root, "SQ-0007", "UNREVIEWED")
            with self.assertRaisesRegex(EvidenceError, "illegal backlog status: SQ-0007"):
                verify(root)
        finally:
            temporary.cleanup()
        temporary, root = self.shadow()
        try:
            spec = json.loads((root / "conformance/schema-v0/evidence/evidence-spec.json").read_text())
            spec["live_invariants"]["owner_authorizing_statuses"].append("READY")
            self.write_json(root, "conformance/schema-v0/evidence/evidence-spec.json", spec)
            self.rebuild_manifest(root)
            with self.assertRaisesRegex(EvidenceError, "owner authorizing status policy drift"):
                verify(root)
        finally:
            temporary.cleanup()

    def test_phase_a_12_rfc0006_mutation_rejected(self):
        self.assert_rejected(
            "rfcs/0006-canonical-logical-data-digest.md",
            lambda data: data + b"\nphase-a mutation\n",
            "RFC-0006 historical baseline drift",
        )

    def test_phase_a_13_rfc_adr_scope_drift_rejected(self):
        self.assert_rejected(
            "docs/adr/0004-deterministic-cbor-cddl.md",
            lambda data: data.replace(
                b"\n`statqed.cbor-core.v1` application profile",
                b"\n`statqed.cbor-core.v2` application profile",
                1,
            ),
            "normative scope drift",
        )

    def test_phase_a_14_schema_prototype_and_golden_mutations_rejected(self):
        mutations = (
            ("schemas/v0/README.md", lambda data: data + b"\nmutation\n", "evidence subject mismatch"),
            (
                "schemas/prototypes/python-oracle/LINEAGE.md",
                lambda data: data + b"\nmutation\n",
                "schemas_prototypes",
            ),
            (
                "conformance/golden/v0/positive-minimum.cbor",
                lambda data: data[:-1] + bytes((data[-1] ^ 1,)),
                "evidence subject mismatch",
            ),
        )
        for relative, transform, reason in mutations:
            with self.subTest(relative=relative):
                self.assert_rejected(relative, transform, reason)

    def test_phase_a_15_sq0007_ready_registry_change_rejected(self):
        temporary, root = self.shadow()
        try:
            self.neutralize_ambient_sq0007_registry_paths(root)
            self.set_task_state(root, "SQ-0007", "READY")
            verify(root)
            self.add_file(root, "lean/StatQED/Registry/Probe.lean")
            with self.assertRaisesRegex(EvidenceError, "lean_registry"):
                verify(root)
        finally:
            temporary.cleanup()

    def test_phase_a_16_sq0007_active_registry_change_accepted(self):
        temporary, root = self.shadow()
        try:
            self.neutralize_ambient_sq0007_registry_paths(root)
            self.set_task_state(root, "SQ-0007", "IN_PROGRESS")
            verify(root)
            self.add_file(root, "lean/StatQED/Registry/Probe.lean")
            self.add_file(root, "backend/crates/statqed-registry/src/lib.rs")
            verify(root)
        finally:
            temporary.cleanup()

    def test_phase_a_17_sq0007_active_unrelated_lean_change_rejected(self):
        temporary, root = self.shadow()
        try:
            self.neutralize_ambient_sq0007_registry_paths(root)
            self.set_task_state(root, "SQ-0007", "IN_PROGRESS")
            verify(root)
            self.add_file(root, "lean/StatQED/Unowned/Probe.lean")
            with self.assertRaisesRegex(EvidenceError, "lean_remainder"):
                verify(root)
        finally:
            temporary.cleanup()

    def test_phase_a_18_sq0007_active_backend_registry_change_accepted(self):
        temporary, root = self.shadow()
        try:
            self.neutralize_ambient_sq0007_registry_paths(root)
            self.set_task_state(root, "SQ-0007", "IN_PROGRESS")
            self.set_task_state(root, "SQ-0011", "READY")
            verify(root)
            self.add_file(root, "backend/crates/statqed-registry/src/lib.rs")
            verify(root)
        finally:
            temporary.cleanup()

    def test_phase_a_19_sq0007_active_unrelated_backend_change_rejected(self):
        temporary, root = self.shadow()
        try:
            self.neutralize_ambient_sq0007_registry_paths(root)
            self.set_task_state(root, "SQ-0007", "IN_PROGRESS")
            self.set_task_state(root, "SQ-0011", "READY")
            verify(root)
            self.add_file(root, "backend/crates/unowned-probe/src/lib.rs")
            with self.assertRaisesRegex(EvidenceError, "backend_remainder"):
                verify(root)
        finally:
            temporary.cleanup()
        temporary, root = self.shadow()
        try:
            self.neutralize_ambient_sq0007_registry_paths(root)
            self.set_task_state(root, "SQ-0007", "READY")
            self.set_task_state(root, "SQ-0011", "IN_PROGRESS")
            verify(root)
            self.add_file(root, "backend/crates/statqed-registry/src/lib.rs")
            self.add_file(root, "backend/crates/sq0011-probe/src/lib.rs")
            verify(root)
        finally:
            temporary.cleanup()

    def test_phase_a_20_sq0008_active_assurance_change_accepted(self):
        temporary, root = self.shadow()
        try:
            self.neutralize_ambient_sq0007_registry_paths(root)
            self.set_task_state(root, "SQ-0007", "READY")
            self.set_task_state(root, "SQ-0008", "IN_PROGRESS")
            verify(root)
            self.add_file(root, "lean/StatQED/Assurance/Probe.lean")
            verify(root)
        finally:
            temporary.cleanup()

    def test_phase_a_21_sq0008_active_registry_change_rejected(self):
        temporary, root = self.shadow()
        try:
            self.neutralize_ambient_sq0007_registry_paths(root)
            self.set_task_state(root, "SQ-0007", "READY")
            self.set_task_state(root, "SQ-0008", "IN_PROGRESS")
            verify(root)
            self.add_file(root, "lean/StatQED/Registry/Probe.lean")
            with self.assertRaisesRegex(EvidenceError, "lean_registry"):
                verify(root)
        finally:
            temporary.cleanup()
        temporary, root = self.shadow()
        try:
            self.neutralize_ambient_sq0007_registry_paths(root)
            self.set_task_state(root, "SQ-0008", "IN_PROGRESS")
            self.set_task_state(root, "SQ-0007", "IN_PROGRESS")
            verify(root)
            self.add_file(root, "lean/StatQED/Registry/Probe.lean")
            verify(root)
            status = json.loads((root / "work/status.yaml").read_text())
            status["in_progress"].reverse()
            self.write_json(root, "work/status.yaml", status)
            with self.assertRaisesRegex(EvidenceError, "live ledger in_progress disagrees"):
                verify(root)
        finally:
            temporary.cleanup()

    def test_phase_a_22_sq0013_active_r_change_accepted(self):
        temporary, root = self.shadow()
        try:
            self.neutralize_ambient_sq0007_registry_paths(root)
            self.set_task_state(root, "SQ-0007", "READY")
            self.set_task_state(root, "SQ-0013", "IN_PROGRESS")
            verify(root)
            self.add_file(root, "frontends/r/R/probe.R")
            verify(root)
        finally:
            temporary.cleanup()

    def test_phase_a_23_sq0013_active_python_change_rejected(self):
        temporary, root = self.shadow()
        try:
            self.neutralize_ambient_sq0007_registry_paths(root)
            self.set_task_state(root, "SQ-0007", "READY")
            self.set_task_state(root, "SQ-0013", "IN_PROGRESS")
            self.set_task_state(root, "SQ-0014", "READY")
            verify(root)
            self.add_file(root, "frontends/python/probe.py")
            with self.assertRaisesRegex(EvidenceError, "frontend_python"):
                verify(root)
        finally:
            temporary.cleanup()

    def test_phase_a_24_sq0014_active_python_change_accepted(self):
        temporary, root = self.shadow()
        try:
            self.neutralize_ambient_sq0007_registry_paths(root)
            self.set_task_state(root, "SQ-0007", "READY")
            self.set_task_state(root, "SQ-0014", "IN_PROGRESS")
            verify(root)
            self.add_file(root, "frontends/python/probe.py")
            verify(root)
        finally:
            temporary.cleanup()

    def test_phase_a_25_sq0014_active_julia_change_rejected(self):
        temporary, root = self.shadow()
        try:
            self.neutralize_ambient_sq0007_registry_paths(root)
            self.set_task_state(root, "SQ-0007", "READY")
            self.set_task_state(root, "SQ-0014", "IN_PROGRESS")
            self.set_task_state(root, "SQ-0015", "READY")
            verify(root)
            self.add_file(root, "frontends/julia/src/Probe.jl")
            with self.assertRaisesRegex(EvidenceError, "frontend_julia"):
                verify(root)
        finally:
            temporary.cleanup()

    def test_phase_a_26_sq0015_active_julia_change_accepted(self):
        temporary, root = self.shadow()
        try:
            self.neutralize_ambient_sq0007_registry_paths(root)
            self.set_task_state(root, "SQ-0007", "READY")
            self.set_task_state(root, "SQ-0015", "IN_PROGRESS")
            verify(root)
            self.add_file(root, "frontends/julia/src/Probe.jl")
            verify(root)
        finally:
            temporary.cleanup()

    def test_phase_a_27_sq0015_active_r_change_rejected(self):
        temporary, root = self.shadow()
        try:
            self.neutralize_ambient_sq0007_registry_paths(root)
            self.set_task_state(root, "SQ-0007", "READY")
            self.set_task_state(root, "SQ-0015", "IN_PROGRESS")
            self.set_task_state(root, "SQ-0013", "READY")
            verify(root)
            self.add_file(root, "frontends/r/R/probe.R")
            with self.assertRaisesRegex(EvidenceError, "frontend_r"):
                verify(root)
        finally:
            temporary.cleanup()

    def test_phase_a_28_no_owner_active_new_protected_file_rejected(self):
        temporary, root = self.shadow()
        try:
            self.neutralize_ambient_sq0007_registry_paths(root)
            self.set_task_state(root, "SQ-0007", "READY")
            self.set_task_state(root, "SQ-0011", "READY")
            verify(root)
            self.add_file(root, "backend/new-protected-file.txt")
            with self.assertRaisesRegex(EvidenceError, "backend_remainder"):
                verify(root)
        finally:
            temporary.cleanup()
        for kind in ("symlink", "special", "regular"):
            with self.subTest(ignored_kind=kind):
                temporary, root = self.shadow()
                try:
                    self.neutralize_ambient_sq0007_registry_paths(root)
                    self.set_task_state(root, "SQ-0007", "READY")
                    self.set_task_state(root, "SQ-0011", "READY")
                    verify(root)
                    target = root / "backend/target"
                    if kind == "symlink":
                        target.symlink_to(root / "lean", target_is_directory=True)
                    elif kind == "special":
                        target.mkdir()
                        os.mkfifo(target / "probe.fifo")
                    else:
                        self.add_file(root, "backend/target/hidden-source.rs")
                    with self.assertRaisesRegex(EvidenceError, "protected path"):
                        verify(root)
                finally:
                    temporary.cleanup()

    def test_phase_f_unneutralized_registry_paths_obey_live_owner_state(self):
        temporary, root = self.shadow()
        try:
            self.neutralize_ambient_sq0007_registry_paths(root)
            for index in range(5):
                self.add_file(root, f"lean/StatQED/Registry/Ambient{index}.lean")
            self.add_file(root, "backend/crates/statqed-registry/src/lib.rs")
            self.set_task_state(root, "SQ-0007", "IN_REVIEW")
            verify(root)
            self.set_task_state(root, "SQ-0007", "READY")
            with self.assertRaisesRegex(EvidenceError, "lean_registry"):
                verify(root)
            self.set_task_state(root, "SQ-0007", "SUPERSEDED")
            with self.assertRaisesRegex(EvidenceError, "lean_registry"):
                verify(root)
        finally:
            temporary.cleanup()

    def test_phase_f_owner_scenarios_ignore_ambient_registry_paths(self):
        outcomes: list[str] = []
        for ambient in (False, True):
            with self.subTest(ambient=ambient):
                temporary, root = self.shadow()
                try:
                    self.neutralize_ambient_sq0007_registry_paths(root)
                    expected_removed: list[str] = []
                    if ambient:
                        for index in range(5):
                            relative = f"lean/StatQED/Registry/Ambient{index}.lean"
                            self.add_file(root, relative)
                            expected_removed.append(relative)
                        rust = "backend/crates/statqed-registry/src/lib.rs"
                        self.add_file(root, rust)
                        expected_removed.append(rust)
                        self.set_task_state(root, "SQ-0007", "IN_REVIEW")
                        verify(root)
                    removed = self.neutralize_ambient_sq0007_registry_paths(root)
                    self.assertEqual(tuple(sorted(expected_removed)), removed)
                    self.set_task_state(root, "SQ-0007", "READY")
                    self.set_task_state(root, "SQ-0011", "READY")
                    verify(root)
                    self.add_file(root, "lean/StatQED/Registry/Controlled.lean")
                    with self.assertRaisesRegex(EvidenceError, "lean_registry") as caught:
                        verify(root)
                    registry_outcome = str(caught.exception)
                    (root / "lean/StatQED/Registry/Controlled.lean").unlink()
                    self.add_file(root, "backend/controlled-unowned-probe.txt")
                    with self.assertRaisesRegex(EvidenceError, "backend_remainder") as caught:
                        verify(root)
                    outcomes.extend((registry_outcome, str(caught.exception)))
                finally:
                    temporary.cleanup()
        self.assertEqual(outcomes[:2], outcomes[2:])

    def test_phase_f_registry_neutralizer_is_allowlisted_and_safe(self):
        temporary, root = self.shadow()
        try:
            self.neutralize_ambient_sq0007_registry_paths(root)
            self.add_file(root, "lean/StatQED/Registry/Controlled.lean")
            self.add_file(root, "backend/crates/statqed-registry/src/lib.rs")
            self.assertEqual(
                (
                    "backend/crates/statqed-registry/src/lib.rs",
                    "lean/StatQED/Registry/Controlled.lean",
                ),
                self.neutralize_ambient_sq0007_registry_paths(root),
            )
            for invalid in (
                ("/",),
                (".",),
                ("lean",),
                ("backend",),
                ("lean/StatQED/Assurance",),
            ):
                with self.assertRaises(ValueError):
                    self.neutralize_ambient_sq0007_registry_paths(
                        root, relative_roots=invalid
                    )
            for invalid_root in (Path("/"), ROOT, root.parent, root / "lean"):
                with self.assertRaises(ValueError):
                    self.neutralize_ambient_sq0007_registry_paths(invalid_root)

            registry = root / "lean/StatQED/Registry"
            registry.parent.mkdir(parents=True, exist_ok=True)
            registry.symlink_to(root / "lean", target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink"):
                self.neutralize_ambient_sq0007_registry_paths(root)
            registry.unlink()

            registry.symlink_to(root / "missing-registry-target", target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink"):
                self.neutralize_ambient_sq0007_registry_paths(root)
            registry.unlink()

            if hasattr(os, "mkfifo"):
                os.mkfifo(registry)
                with self.assertRaisesRegex(ValueError, "non-directory"):
                    self.neutralize_ambient_sq0007_registry_paths(root)
        finally:
            temporary.cleanup()

    def test_phase_a_29_unowned_historical_baseline_mutation_rejected(self):
        self.assert_rejected(
            "lean/README.md",
            lambda data: data + b"\nphase-a mutation\n",
            "maintenance live baseline mismatch",
        )

    def test_phase_m_historical_v2_manifest_mutation_rejected(self):
        temporary, root = self.shadow()
        try:
            manifest = json.loads((root / "conformance/schema-v0/evidence/evidence-manifest.json").read_text())
            manifest["historical_lifecycle"]["live_subject_count"] += 1
            self.write_json(root, "conformance/schema-v0/evidence/evidence-manifest.json", manifest)
            with self.assertRaisesRegex(EvidenceError, "historical SQ-0006 v2 lifecycle manifest drift"):
                verify(root)
        finally:
            temporary.cleanup()

    def test_phase_m_maintenance_live_baseline_rejects_trust_drift(self):
        self.assert_rejected(
            "scripts/check_lean_trust.py",
            lambda data: data + b"\n# unreviewed trust mutation\n",
            "maintenance live baseline mismatch",
        )

    def test_phase_m_untracked_ignored_cache_symlink_is_pruned(self):
        temporary, root = self.shadow()
        try:
            subprocess.run(["git", "init", "--quiet"], cwd=root, check=True)
            cache = root / "lean/.lake/packages/example/docs"
            cache.mkdir(parents=True)
            (cache / "README.md").symlink_to(root / "README.md")
            verify(root)
        finally:
            temporary.cleanup()


if __name__ == "__main__":
    unittest.main()
