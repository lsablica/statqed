from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[3]
TRUST_PATH = ROOT / "scripts" / "check_lean_trust.py"
REPORT_PATH = ROOT / "lean" / "tools" / "project_axiom_report.py"


def load(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


trust = load(TRUST_PATH, "statqed_test_check_lean_trust")
reporter = load(REPORT_PATH, "statqed_test_project_axiom_report")


ONE_CASE = {
    "expected_live_report": {
        "added_modules": ["StatQED.Registry.Positive"],
        "baseline_mode": "current_tracked_modules",
        "require_exact_union": True,
    },
    "id": "one",
    "mutation": "replace_file",
    "target": "StatQED/Registry/Positive.lean",
}
FIVE_ADDED = [f"StatQED.Registry.Five{name}" for name in "ABCDE"]
FIVE_CASE = {
    "expected_live_report": {
        "added_modules": FIVE_ADDED,
        "baseline_mode": "current_tracked_modules",
        "require_exact_union": True,
    },
    "id": "five",
    "mutation": "replace_files",
    "targets": [f"StatQED/Registry/Five{name}.lean" for name in "ABCDE"],
}


def encoded_report(
    modules: list[str],
    *,
    count: int | None = None,
    schema: str = reporter.SCHEMA,
) -> str:
    value = {
        "declarations": [],
        "module_count": len(modules) if count is None else count,
        "modules": modules,
        "schema_version": schema,
    }
    return json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n"


class BranchRelativeLiveReportTests(unittest.TestCase):
    historical = ["StatQED", "StatQED.Internal.Smoke"]
    sq0007_like = [
        "StatQED",
        "StatQED.Internal.Smoke",
        "StatQED.Registry.Closure",
        "StatQED.Registry.Normalize",
        "StatQED.Registry.Tests.Bounds",
        "StatQED.Registry.Tests.Smoke",
        "StatQED.Registry.Tools.AxiomReport",
        "StatQED.Registry.Tools.Extract",
    ]

    def check(self, case: dict[str, object], baseline: list[str], modules: list[str], **overrides: object):
        return trust.validate_successful_live_report(
            case=case,
            baseline_modules=baseline,
            reporter=reporter,
            stdout=encoded_report(modules, **overrides),
            stderr="",
        )

    def test_historical_baseline_one_and_five_are_relative(self) -> None:
        one = self.check(
            ONE_CASE, self.historical, sorted([*self.historical, "StatQED.Registry.Positive"])
        )
        five = self.check(FIVE_CASE, self.historical, sorted([*self.historical, *FIVE_ADDED]))
        self.assertEqual((one["expected_final_module_count"], five["expected_final_module_count"]), (3, 7))
        self.assertTrue(one["exact_union"] and five["exact_union"])

    def test_sq0007_like_baseline_one_and_five_are_relative(self) -> None:
        one = self.check(
            ONE_CASE,
            self.sq0007_like,
            sorted([*self.sq0007_like, "StatQED.Registry.Positive"]),
        )
        five = self.check(
            FIVE_CASE, self.sq0007_like, sorted([*self.sq0007_like, *FIVE_ADDED])
        )
        self.assertEqual((one["expected_final_module_count"], five["expected_final_module_count"]), (9, 13))

    def test_mutation_loop_wiring_discovers_synthetic_eight_module_baseline(self) -> None:
        """Exercise copied discovery, Git staging, mutation, and result assembly."""

        with tempfile.TemporaryDirectory() as directory:
            synthetic_root = Path(directory)
            synthetic_lean = synthetic_root / "lean"
            shutil.copytree(ROOT / "lean", synthetic_lean, ignore=shutil.ignore_patterns(".lake"))
            existing_modules = [
                f"StatQED.Registry.Existing{name}" for name in "ABCDEF"
            ]
            for module in existing_modules:
                relative = Path(*module.split(".")).with_suffix(".lean")
                target = synthetic_lean / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(f"namespace {module}\n\ndef marker : True := True.intro\n\nend {module}\n")
            expectations = json.loads(
                (synthetic_lean / "Tests/Trust/expectations.json").read_text()
            )
            expectations["cases"] = []
            expectations["positive_controls"] = []
            expectations["security_regressions"] = []
            expectations["live_report_cases"] = [
                case
                for case in expectations["live_report_cases"]
                if case["id"]
                in {
                    "registry_module_live_positive",
                    "five_registry_modules_live_positive",
                }
            ]
            (synthetic_lean / "Tests/Trust/expectations.json").write_text(
                json.dumps(expectations, indent=2, sort_keys=True) + "\n"
            )
            subprocess.run(["git", "init", "--quiet"], cwd=synthetic_root, check=True)
            subprocess.run(
                ["git", "add", "lean/StatQED.lean", "lean/StatQED"],
                cwd=synthetic_root,
                check=True,
            )
            copied_reporter = trust.load_temporary_project_report(synthetic_lean)
            discovered = copied_reporter.source_modules(synthetic_root, synthetic_lean)
            self.assertEqual(discovered, sorted([*self.historical, *existing_modules]))

            real_run_checked = trust.run_checked

            def controlled_run(
                command: list[str], cwd: Path
            ) -> subprocess.CompletedProcess[str]:
                if command[:2] == ["git", "init"] or command[:2] == ["git", "add"]:
                    return real_run_checked(command, cwd)
                if command == ["lake", "build"]:
                    return subprocess.CompletedProcess(command, 0, "", "")
                if command[-1:] == ["--verify"] and "project_axiom_report.py" in command[-2]:
                    live_reporter = trust.load_temporary_project_report(cwd)
                    modules = live_reporter.source_modules(cwd.parent, cwd)
                    return subprocess.CompletedProcess(
                        command,
                        0,
                        encoded_report(modules, schema=live_reporter.SCHEMA),
                        "",
                    )
                raise AssertionError(f"unexpected command: {command!r}")

            with mock.patch.object(trust, "audit", return_value=[]), mock.patch.object(
                trust, "run_checked", side_effect=controlled_run
            ):
                results, findings = trust.run_mutations(synthetic_root)

            self.assertEqual(findings, [])
            by_id = {result["id"]: result for result in results}
            self.assertEqual(set(by_id), {
                "registry_module_live_positive",
                "five_registry_modules_live_positive",
            })
            self.assertEqual(
                by_id["registry_module_live_positive"]["baseline_module_count"], 8
            )
            self.assertEqual(
                by_id["registry_module_live_positive"]["observed_final_module_count"], 9
            )
            self.assertEqual(
                by_id["five_registry_modules_live_positive"]["observed_final_module_count"], 13
            )
            self.assertTrue(all(result["exact_union"] for result in results))

    def test_missing_baseline_module_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "union mismatch"):
            self.check(ONE_CASE, self.historical, ["StatQED", "StatQED.Registry.Positive"])

    def test_unexpected_extra_module_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "union mismatch"):
            self.check(
                ONE_CASE,
                self.historical,
                sorted([*self.historical, "StatQED.Registry.Extra", "StatQED.Registry.Positive"]),
            )

    def test_missing_added_module_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "union mismatch"):
            self.check(ONE_CASE, self.historical, self.historical)

    def test_added_module_already_in_baseline_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "already exists"):
            trust.expected_live_report(
                ONE_CASE,
                sorted([*self.historical, "StatQED.Registry.Positive"]),
                reporter,
            )

    def test_module_count_mismatch_is_rejected(self) -> None:
        modules = sorted([*self.historical, "StatQED.Registry.Positive"])
        with self.assertRaisesRegex(ValueError, "module_count"):
            self.check(ONE_CASE, self.historical, modules, count=99)

    def test_unsorted_modules_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "sorted and unique"):
            self.check(
                ONE_CASE,
                self.historical,
                ["StatQED.Registry.Positive", *self.historical],
            )

    def test_duplicate_modules_are_rejected(self) -> None:
        modules = sorted([*self.historical, "StatQED.Registry.Positive"])
        with self.assertRaisesRegex(ValueError, "sorted and unique"):
            self.check(ONE_CASE, self.historical, [*modules, modules[-1]])

    def test_malformed_json_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "not one JSON document"):
            trust.validate_successful_live_report(
                case=ONE_CASE,
                baseline_modules=self.historical,
                reporter=reporter,
                stdout="not-json\n",
                stderr="",
            )

    def test_wrong_schema_is_rejected(self) -> None:
        modules = sorted([*self.historical, "StatQED.Registry.Positive"])
        with self.assertRaisesRegex(ValueError, "schema"):
            self.check(ONE_CASE, self.historical, modules, schema="wrong")

    def test_target_module_mismatch_is_rejected(self) -> None:
        bad = json.loads(json.dumps(ONE_CASE))
        bad["target"] = "StatQED/Registry/Different.lean"
        with self.assertRaisesRegex(ValueError, "differ from declared"):
            trust.expected_live_report(bad, self.historical, reporter)

    def test_successful_report_stderr_is_rejected(self) -> None:
        modules = sorted([*self.historical, "StatQED.Registry.Positive"])
        with self.assertRaisesRegex(ValueError, "stderr"):
            trust.validate_successful_live_report(
                case=ONE_CASE,
                baseline_modules=self.historical,
                reporter=reporter,
                stdout=encoded_report(modules),
                stderr="warning\n",
            )

    def test_nondeterministic_json_layout_is_rejected(self) -> None:
        modules = sorted([*self.historical, "StatQED.Registry.Positive"])
        with self.assertRaisesRegex(ValueError, "not deterministic"):
            trust.validate_successful_live_report(
                case=ONE_CASE,
                baseline_modules=self.historical,
                reporter=reporter,
                stdout=json.dumps({"schema_version": reporter.SCHEMA, "modules": modules, "module_count": 3}),
                stderr="",
            )

    def test_expectation_schema_is_version_two(self) -> None:
        value = json.loads((ROOT / "lean/Tests/Trust/expectations.json").read_text())
        self.assertEqual(value["schema_version"], trust.MUTATION_EXPECTATION_SCHEMA)

    def test_unsupported_expectation_schema_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "expectations.json"
            path.write_text('{"schema_version":1}\n')
            with self.assertRaisesRegex(ValueError, "schema_version must be 2"):
                trust.load_mutation_expectations(path)

    def test_negative_live_cases_retain_exact_diagnostics(self) -> None:
        value = json.loads((ROOT / "lean/Tests/Trust/expectations.json").read_text())
        negative = [case for case in value["live_report_cases"] if case["expected_code"] != "ok"]
        self.assertGreaterEqual(len(negative), 5)
        for case in negative:
            self.assertIsInstance(case.get("expected_output_substring"), str)
            self.assertNotEqual(case["expected_output_substring"], "")
            self.assertNotIn("expected_live_report", case)

    def test_sq0006_partition_rejects_unreviewed_manifest_only_rebinding(self) -> None:
        checker = load(
            ROOT / "scripts/schema/check_schema_v0.py",
            "statqed_test_schema_evidence_checker",
        )
        specification = json.loads(
            (ROOT / "conformance/schema-v0/evidence/evidence-spec.json").read_text()
        )
        policy = next(
            item
            for item in specification["protected_path_policy"]["partitions"]
            if item["id"] == "lean_remainder"
        )
        files = checker.protected_files(
            ROOT,
            "lean",
            tuple(specification["protected_path_policy"]["ignored_prefixes"]),
        )
        current_digest, current_count = checker.protected_partition_digest(files, policy)
        self.assertEqual(
            (current_digest, current_count),
            (policy["baseline_sha256"], policy["baseline_file_count"]),
        )
        changed = (ROOT / "lean/Tests/Trust/expectations.json").read_bytes() + b" "
        digest = hashlib.sha256()
        for relative, path in [
            pair for pair in files if checker.partition_matches(pair[0], policy)
        ]:
            digest.update(relative.encode())
            digest.update(b"\0")
            digest.update(b"x" if path.stat().st_mode & 0o111 else b"-")
            digest.update(b"\0")
            digest.update(
                hashlib.sha256(
                    changed
                    if relative == "lean/Tests/Trust/expectations.json"
                    else path.read_bytes()
                ).digest()
            )
        self.assertNotEqual(digest.hexdigest(), policy["baseline_sha256"])

    def test_sq0005_live_overlay_is_fixed_and_rejects_current_tree_drift(self) -> None:
        generator = load(
            ROOT / "scripts/serialization/build_evidence_manifest.py",
            "statqed_test_serialization_evidence_generator",
        )
        paths = sorted(generator.REVIEWED_POST_V3_LIVE_OVERLAYS)
        baseline = [{"path": "lean/StatQED.lean", "sha256": "0" * 64}]
        current = generator.apply_reviewed_live_overlays(baseline, ROOT)
        observed = {item["path"]: item["sha256"] for item in current}
        self.assertEqual(
            {path: observed[path] for path in paths},
            generator.REVIEWED_POST_V3_LIVE_OVERLAYS,
        )
        with tempfile.TemporaryDirectory() as directory:
            shadow = Path(directory)
            for path in paths:
                target = shadow / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / path).read_bytes())
            (shadow / paths[0]).write_bytes((shadow / paths[0]).read_bytes() + b" ")
            with self.assertRaisesRegex(RuntimeError, "live overlay differs"):
                generator.apply_reviewed_live_overlays(baseline, shadow)


if __name__ == "__main__":
    unittest.main()
