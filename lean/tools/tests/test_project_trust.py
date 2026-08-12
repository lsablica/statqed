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
from unittest.mock import patch


TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import check_all_modules  # noqa: E402
import project_axiom_report as report  # noqa: E402


def completed(exit_status: int = 0, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess([], exit_status, stdout, stderr)


class TemporaryProject:
    def __init__(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="statqed-project-trust-test-")
        self.root = Path(self.temporary.name)
        self.lean = self.root / "lean"
        (self.lean / "StatQED").mkdir(parents=True)
        (self.lean / "Tests").mkdir()
        (self.lean / "Tests" / "ProjectAxiomProbe.lean").write_text("-- probe\n")
        (self.lean / "StatQED.lean").write_text("namespace StatQED\nend StatQED\n")
        subprocess.run(["git", "init", "--quiet"], cwd=self.root, check=True)

    def add_module(self, relative: str, source: str = "namespace StatQED\nend StatQED\n") -> Path:
        path = self.lean / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source)
        return path

    def stage(self) -> None:
        subprocess.run(
            ["git", "add", "lean/StatQED.lean", "lean/StatQED"],
            cwd=self.root,
            check=True,
        )

    def close(self) -> None:
        self.temporary.cleanup()


def observation(modules: list[str], declarations: list[dict[str, object]] | None = None) -> str:
    payload = {
        "declarations": declarations or [],
        "project_modules": modules,
        "schema_version": report.OBSERVATION_SCHEMA,
    }
    return "\n".join([report.BEGIN, json.dumps(payload, sort_keys=True), report.END, ""])


class ModuleEnumerationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = TemporaryProject()

    def tearDown(self) -> None:
        self.project.close()

    def test_01_foundation_modules_are_enumerated(self) -> None:
        self.project.add_module("StatQED/Internal/Smoke.lean")
        self.project.stage()
        self.assertEqual(
            report.source_modules(self.project.root, self.project.lean),
            ["StatQED", "StatQED.Internal.Smoke"],
        )

    def test_02_new_registry_module_increases_count(self) -> None:
        self.project.add_module("StatQED/Registry/One.lean")
        self.project.stage()
        self.assertEqual(
            report.source_modules(self.project.root, self.project.lean),
            ["StatQED", "StatQED.Registry.One"],
        )

    def test_03_five_registry_modules_are_all_enumerated(self) -> None:
        for name in ("Closure", "Normalize", "Smoke", "AxiomReport", "Extract"):
            self.project.add_module(f"StatQED/Registry/{name}.lean")
        self.project.stage()
        modules = report.source_modules(self.project.root, self.project.lean)
        self.assertEqual(len(modules), 6)
        self.assertEqual(modules[1:], [
            "StatQED.Registry.AxiomReport",
            "StatQED.Registry.Closure",
            "StatQED.Registry.Extract",
            "StatQED.Registry.Normalize",
            "StatQED.Registry.Smoke",
        ])

    def test_04_untracked_module_is_rejected(self) -> None:
        self.project.stage()
        self.project.add_module("StatQED/Registry/Smuggled.lean")
        with self.assertRaisesRegex(report.ProjectTrustError, "untracked"):
            report.source_modules(self.project.root, self.project.lean)

    def test_05_symlinked_module_is_rejected(self) -> None:
        self.project.stage()
        target = self.project.root / "outside.lean"
        target.write_text("namespace Outside\nend Outside\n")
        os.symlink(target, self.project.lean / "StatQED" / "Linked.lean")
        with self.assertRaisesRegex(report.ProjectTrustError, "not a regular file"):
            report.source_modules(self.project.root, self.project.lean)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO creation is unavailable")
    def test_06_special_file_module_is_rejected(self) -> None:
        self.project.stage()
        os.mkfifo(self.project.lean / "StatQED" / "Pipe.lean")
        with self.assertRaisesRegex(report.ProjectTrustError, "not a regular file"):
            report.source_modules(self.project.root, self.project.lean)

    def test_07_tracked_symlink_mode_is_rejected(self) -> None:
        target = self.project.root / "outside.lean"
        target.write_text("namespace Outside\nend Outside\n")
        os.symlink(target, self.project.lean / "StatQED" / "Linked.lean")
        subprocess.run(
            ["git", "add", "lean/StatQED.lean", "lean/StatQED/Linked.lean"],
            cwd=self.project.root,
            check=True,
        )
        with self.assertRaisesRegex(report.ProjectTrustError, "not a regular file"):
            report.source_modules(self.project.root, self.project.lean)

    def test_08_invalid_module_name_is_rejected(self) -> None:
        self.project.add_module("StatQED/bad-name.lean")
        self.project.stage()
        with self.assertRaisesRegex(report.ProjectTrustError, "unsupported Lean name"):
            report.source_modules(self.project.root, self.project.lean)

    def test_09_module_count_is_bounded(self) -> None:
        self.project.add_module("StatQED/Internal/Smoke.lean")
        self.project.stage()
        with patch.object(report, "MAX_PROJECT_MODULES", 1):
            with self.assertRaisesRegex(report.ProjectTrustError, "module count"):
                report.source_modules(self.project.root, self.project.lean)

    def test_10_unimportable_tracked_module_rejects_generated_wrapper(self) -> None:
        self.project.add_module(
            "StatQED/Registry/Broken.lean",
            "import StatQED.Registry.Missing\n",
        )
        self.project.stage()

        def runner(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            if command[:2] == ["git", "ls-files"]:
                return subprocess.run(
                    command,
                    cwd=kwargs["cwd"],
                    check=False,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            wrapper = command[-1]
            return completed(1, stderr=f"{wrapper}:1: unknown module")

        with patch.object(report, "run", side_effect=runner):
            with self.assertRaisesRegex(
                report.ProjectTrustError,
                r"<generated-import-all-wrapper>:1: unknown module",
            ) as caught:
                report.generate(self.project.root, self.project.lean)
        self.assertNotIn("statqed-project-axiom-", str(caught.exception))

    def test_11_omitted_source_module_is_rejected_before_wrapper_execution(self) -> None:
        self.project.add_module("StatQED/Internal/Smoke.lean")
        self.project.stage()
        with self.assertRaisesRegex(
            report.ProjectTrustError,
            "generated wrapper module set differs from tracked source-module set",
        ):
            report.generate(
                self.project.root,
                self.project.lean,
                omitted_modules=frozenset({"StatQED.Internal.Smoke"}),
            )


class ObservationTests(unittest.TestCase):
    modules = ["StatQED", "StatQED.Internal.Smoke"]

    @staticmethod
    def declaration(**overrides: object) -> dict[str, object]:
        value: dict[str, object] = {
            "axioms": [],
            "declaration": "StatQED.Internal.testOnlySmoke",
            "kind": "theorem",
            "module": "StatQED.Internal.Smoke",
            "type": "True",
            "unsafe": False,
        }
        value.update(overrides)
        return value

    def test_12_valid_observation_is_accepted(self) -> None:
        value = report.parse_observation(
            observation(self.modules, [self.declaration()]), self.modules
        )
        self.assertEqual(value["project_modules"], self.modules)

    def test_13_observation_omitted_source_module_is_rejected(self) -> None:
        with self.assertRaisesRegex(report.ProjectTrustError, "does not equal"):
            report.parse_observation(observation(["StatQED"]), self.modules)

    def test_14_import_without_source_is_rejected(self) -> None:
        with self.assertRaisesRegex(report.ProjectTrustError, "does not equal"):
            report.parse_observation(
                observation([*self.modules, "StatQED.Ghost"]), self.modules
            )

    def test_15_project_axiom_is_rejected(self) -> None:
        with self.assertRaisesRegex(report.ProjectTrustError, "axiom declaration"):
            report.parse_observation(
                observation(self.modules, [self.declaration(kind="axiom")]), self.modules
            )

    def test_16_unsafe_declaration_is_rejected(self) -> None:
        with self.assertRaisesRegex(report.ProjectTrustError, "unsafe"):
            report.parse_observation(
                observation(self.modules, [self.declaration(unsafe=True)]), self.modules
            )

    def test_17_sorry_closure_is_rejected(self) -> None:
        with self.assertRaisesRegex(report.ProjectTrustError, "sorryAx"):
            report.parse_observation(
                observation(self.modules, [self.declaration(axioms=["sorryAx"])]), self.modules
            )

    def test_18_native_trust_closure_is_rejected(self) -> None:
        with self.assertRaisesRegex(report.ProjectTrustError, "native-trust"):
            report.parse_observation(
                observation(
                    self.modules,
                    [self.declaration(axioms=["Lean.trustCompiler"])],
                ),
                self.modules,
            )

    def test_19_duplicate_declaration_is_rejected(self) -> None:
        entry = self.declaration()
        with self.assertRaisesRegex(report.ProjectTrustError, "sorted and unique"):
            report.parse_observation(observation(self.modules, [entry, entry]), self.modules)

    def test_20_wrapper_is_deterministic(self) -> None:
        first = report.wrapper_source(self.modules, "-- probe\n")
        second = report.wrapper_source(list(self.modules), "-- probe\n")
        self.assertEqual(first, second)
        self.assertIn("#statqed_project_axiom_report", first)

    def test_21_wrapper_rejects_unsorted_modules(self) -> None:
        with self.assertRaisesRegex(report.ProjectTrustError, "sorted"):
            report.wrapper_source(list(reversed(self.modules)), "-- probe\n")


class FreshReplayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = TemporaryProject()
        self.project.add_module("StatQED/Internal/Smoke.lean")
        self.project.stage()

    def tearDown(self) -> None:
        self.project.close()

    def test_22_every_module_receives_fresh_replay(self) -> None:
        commands: list[list[str]] = []

        def runner(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
            commands.append(command)
            return completed()

        result = check_all_modules.check_all(
            self.project.root, self.project.lean, runner=runner
        )
        self.assertEqual(result["module_count"], 2)
        self.assertEqual(
            commands,
            [
                ["lake", "env", "leanchecker", "--fresh", "StatQED"],
                ["lake", "env", "leanchecker", "--fresh", "StatQED.Internal.Smoke"],
            ],
        )

    def test_23_one_failed_fresh_replay_rejects_entire_check(self) -> None:
        def runner(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
            return completed(1, stderr="kernel failure") if command[-1].endswith("Smoke") else completed()

        with self.assertRaisesRegex(report.ProjectTrustError, "Smoke"):
            check_all_modules.check_all(
                self.project.root, self.project.lean, runner=runner
            )

    def test_24_five_new_modules_receive_seven_total_replays(self) -> None:
        for index in range(5):
            self.project.add_module(f"StatQED/Registry/M{index}.lean")
        self.project.stage()
        commands: list[list[str]] = []

        def runner(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
            commands.append(command)
            return completed()

        result = check_all_modules.check_all(
            self.project.root, self.project.lean, runner=runner
        )
        self.assertEqual(result["module_count"], 7)
        self.assertEqual(len(commands), 7)


if __name__ == "__main__":
    unittest.main()
