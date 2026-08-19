from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest


SCRIPT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

import run_conformance
import independent_oracle


ROOT = Path(__file__).resolve().parents[3]


class DifferentialConformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = json.loads(
            (ROOT / "theorem-registry/evidence/bundle.json").read_text(encoding="utf-8")
        )
        cls.policy = json.loads(
            (ROOT / "theorem-registry/policy/authorization-v0.json").read_text(
                encoding="utf-8"
            )
        )

    def test_every_expression_and_closure_compares_result_class(self):
        catalog = json.loads(run_conformance.CATALOG.read_text(encoding="utf-8"))
        cases = [
            case for case in catalog["fixtures"]
            if case["kind"] in {"expression", "closure"}
        ]
        self.assertTrue(cases)
        for case in cases:
            with self.subTest(fixture=case["id"]):
                classification, code, _, oracle_classification, oracle_code = (
                    run_conformance.evaluate(case, self.bundle, self.policy)
                )
                self.assertEqual(oracle_classification, classification)
                self.assertEqual(oracle_code, code)

    def test_closure_goldens_use_the_normative_four_component_envelope(self):
        case = next(
            item
            for item in json.loads(run_conformance.CATALOG.read_text(encoding="utf-8"))["fixtures"]
            if item["id"] == "CLOSURE-TRUE-FAMILY"
        )
        classification, code, payload, oracle_classification, oracle_code = (
            run_conformance.evaluate(case, self.bundle, self.policy)
        )
        records = run_conformance.closure(case["roots"], case["declarations"])
        expected = run_conformance.canonical_cbor(
            [
                run_conformance.CLOSURE_ID,
                run_conformance.LEAN_COMMIT,
                run_conformance.NORMALIZER_ID,
                records,
            ]
        )
        self.assertEqual((classification, code), ("accepted", "accepted"))
        self.assertEqual((oracle_classification, oracle_code), ("accepted", "accepted"))
        self.assertEqual(payload, expected)
        self.assertEqual(payload[:1], b"\x84")
        self.assertNotEqual(
            payload,
            run_conformance.canonical_cbor(
                [run_conformance.CLOSURE_ID, "0" * 40, run_conformance.NORMALIZER_ID, records]
            ),
        )
        self.assertNotEqual(
            payload,
            run_conformance.canonical_cbor(
                [run_conformance.CLOSURE_ID, run_conformance.LEAN_COMMIT, "statqed.lean-expr.v999", records]
            ),
        )

    def test_rejected_oracle_disagreement_marks_generated_corpus_failed(self):
        original = (
            run_conformance.independent_oracle.semantic_expression_payload_with_parameters
        )

        def disagree(expression, level_parameters):
            if (
                isinstance(expression, list)
                and len(expression) == 3
                and expression[0] == 2
                and isinstance(expression[1], list)
                and len(expression[1]) == 65
            ):
                raise run_conformance.independent_oracle.OracleError(
                    "registry.normalization_failure"
                )
            return original(expression, level_parameters)

        try:
            run_conformance.independent_oracle.semantic_expression_payload_with_parameters = (
                disagree
            )
            result_bytes, _, _ = run_conformance.generated()
        finally:
            run_conformance.independent_oracle.semantic_expression_payload_with_parameters = (
                original
            )
        result = json.loads(result_bytes)
        self.assertGreater(result["failed"], 0)

    def test_reauthorized_governed_field_forgery_is_rejected(self):
        for mutation in (
            "forged_declaration",
            "forged_normalizer",
            "forged_closure",
            "forged_version",
            "forged_source_anchor",
            "forged_attribution",
            "forged_nonclaims",
            "forged_axiom_report_digest",
        ):
            with self.subTest(mutation=mutation):
                candidate, policy = run_conformance.mutate_bundle(
                    copy.deepcopy(self.bundle), copy.deepcopy(self.policy), mutation
                )
                self.assertEqual(
                    run_conformance._classification(candidate, policy),
                    "registry.record_digest_mismatch",
                )

    def test_selected_instance_unit_changes_live_environment_identity(self):
        observation = json.loads(
            (ROOT / "theorem-registry/evidence/lean-observation.json").read_text(
                encoding="utf-8"
            )
        )
        fixture = next(
            item for item in observation["live_fixtures"]["closure_fixtures"]
            if item["fixture_id"] == "LIVE-CLOSURE-SELECTED-INSTANCE"
        )
        records = fixture["observation"]["records"]
        changed = copy.deepcopy(records)
        instance = next(
            record for record in changed
            if record["name"].get("segment") == "liveSelectedInstance"
        )
        instance["body"] = {"kind": "natural", "tag": "literal", "value": "38"}
        baseline = independent_oracle.environment_payload_from_records(
            records, "f3b06c705e6c85f5314019d5d3baab0fec5b580c"
        )
        mutated = independent_oracle.environment_payload_from_records(
            changed, "f3b06c705e6c85f5314019d5d3baab0fec5b580c"
        )
        self.assertNotEqual(baseline, mutated)


if __name__ == "__main__":
    unittest.main()
