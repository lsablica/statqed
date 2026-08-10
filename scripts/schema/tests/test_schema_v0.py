from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


SCRIPT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from compile_schema_v0 import compiled_bytes
from semantic_validator import validate_fixture
from run_schema_v0 import verify_cddl_version
import subprocess


ROOT = Path(__file__).resolve().parents[3]


def representative():
    return json.loads((ROOT / "schemas/fixtures/v0/positive/representative.json").read_text())["typed_value"]


class SemanticValidatorTests(unittest.TestCase):
    def test_positive(self):
        self.assertTrue(validate_fixture(representative()).accepted)

    def test_unknown_and_missing(self):
        value = representative()
        value["entries"].append({"key": {"type": "text", "value": "future"}, "value": {"type": "null"}})
        self.assertEqual(validate_fixture(value).code, "schema.unknown_field")
        value = representative()
        value["entries"] = [entry for entry in value["entries"] if entry["key"]["value"] != "schema_id"]
        self.assertEqual(validate_fixture(value).code, "schema.missing_field")

    def test_features_has_no_element_ontology(self):
        for item in ({"type": "null"}, {"type": "integer", "value": "0"}, {"type": "text", "value": "x"}):
            value = representative()
            next(entry for entry in value["entries"] if entry["key"]["value"] == "features")["value"]["items"] = [item]
            self.assertEqual(validate_fixture(value).code, "schema.feature_unsupported")

    def test_identifier_boundaries(self):
        for text, code in (("a", "accepted"), ("a" + "z" * 127, "accepted"), ("", "schema.identifier_length"), ("a" + "z" * 128, "schema.identifier_length"), ("A", "schema.identifier_syntax"), ("é", "schema.identifier_syntax")):
            value = representative()
            next(entry for entry in value["entries"] if entry["key"]["value"] == "analysis_id")["value"]["value"] = text
            self.assertEqual(validate_fixture(value).code, code)

    def test_compiler_root_and_output(self):
        output, expected = compiled_bytes()
        self.assertEqual(output.read_bytes(), expected)
        self.assertTrue(expected.lstrip().startswith(b"; Closed"))
        first_rule = next(line for line in expected.splitlines() if line and not line.startswith(b";"))
        self.assertTrue(first_rule.startswith(b"foundation-structural-v0 ="))

    def test_wrong_cddl_version_is_rejected(self):
        completed = subprocess.CompletedProcess(["cddl", "--version"], 0, b"cddl 0.10.5\n", b"")
        with patch("run_schema_v0.bounded_run", return_value=completed):
            with self.assertRaisesRegex(RuntimeError, "operational.cddl_version"):
                verify_cddl_version(Path("/nonexistent/cddl"))


if __name__ == "__main__":
    unittest.main()
