from __future__ import annotations

import copy
import hashlib
from pathlib import Path
import subprocess
import sys
import unittest


SCRIPT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

import independent_oracle as oracle


def anonymous():
    return {"tag": "anonymous"}


def name(*segments):
    current = anonymous()
    for segment in segments:
        if isinstance(segment, str):
            current = {"tag": "string", "parent": current, "segment": segment}
        else:
            current = {"tag": "numeric", "parent": current, "segment": segment}
    return current


def constant(identifier, levels=None):
    return {
        "tag": "constant",
        "name": name(*identifier.split(".")),
        "universes": levels or [],
    }


def sort(level=None):
    return {"tag": "sort", "level": level or {"tag": "zero"}}


class IndependentOracleTests(unittest.TestCase):
    def test_true_false_are_distinct_stable_vectors(self):
        true_observation = oracle.observe(constant("True"))
        false_observation = oracle.observe(constant("False"))
        self.assertEqual(true_observation["normalized_expression"], [2, [[0, "True"]], []])
        self.assertEqual(false_observation["normalized_expression"], [2, [[0, "False"]], []])
        self.assertEqual(
            true_observation["payload_hex"],
            "8274737461747165642e6c65616e2d657870722e76308302818200645472756580",
        )
        self.assertEqual(
            true_observation["digests"]["proposition"]["digest"],
            "68a6c0b4a9c83cc7c29c251b900d5a3c265fe9b4856df78a590aef99492513c4",
        )
        self.assertEqual(
            false_observation["payload_hex"],
            "8274737461747165642e6c65616e2d657870722e763083028182006546616c736580",
        )
        self.assertEqual(
            false_observation["digests"]["proposition"]["digest"],
            "1e2200d6f84e49e9b7e4363faa3288e17f601ae3e865e1ce663bf9587df1140d",
        )
        self.assertNotEqual(true_observation["payload_hex"], false_observation["payload_hex"])
        self.assertNotEqual(
            true_observation["digests"]["proposition"]["digest"],
            false_observation["digests"]["proposition"]["digest"],
        )
        self.assertEqual(
            hashlib.sha256(
                bytes.fromhex(true_observation["digests"]["proposition"]["frame_hex"])
            ).hexdigest(),
            true_observation["digests"]["proposition"]["digest"],
        )

    def test_binder_info_and_bound_scope(self):
        vectors = {}
        for binder in ("explicit", "implicit", "strict_implicit", "instance_implicit"):
            expression = {
                "tag": "forall",
                "binder_info": binder,
                "binder_name": "display-only",
                "type": sort(),
                "body": {"tag": "bound_variable", "index": 0},
            }
            vectors[binder] = oracle.normalize_expression(expression)
        self.assertEqual([vectors[key][1] for key in vectors], [0, 1, 2, 3])
        self.assertEqual(len({oracle.canonical_cbor(value) for value in vectors.values()}), 4)
        with self.assertRaisesRegex(oracle.OracleError, "registry.normalization_failure"):
            oracle.normalize_expression({"tag": "bound_variable", "index": 0})

    def test_universe_levels_and_missing_parameter(self):
        alpha = name("u")
        level = {
            "tag": "max",
            "left": {"tag": "succ", "level": {"tag": "zero"}},
            "right": {
                "tag": "imax",
                "left": {"tag": "parameter", "name": alpha},
                "right": {"tag": "zero"},
            },
        }
        expression = constant("SortFixture", [level])
        self.assertEqual(
            oracle.normalize_expression(expression, level_parameters=[alpha]),
            [2, [[0, "SortFixture"]], [[2, [1, [0]], [3, [4, 0], [0]]]]],
        )
        with self.assertRaisesRegex(oracle.OracleError, "registry.normalization_failure"):
            oracle.normalize_expression(expression)

    def test_metadata_binder_names_and_let_nondep_are_erased(self):
        underlying = {
            "tag": "let",
            "binder_name": "x",
            "nondep": False,
            "type": sort(),
            "value": sort(),
            "body": {"tag": "bound_variable", "index": 0},
        }
        wrapped_a = {"tag": "metadata", "metadata": {"source": "first"}, "expression": underlying}
        wrapped_b = {
            "tag": "metadata",
            "metadata": {"source": "second", "cached_hash": 99},
            "expression": {**underlying, "binder_name": "renamed", "nondep": True},
        }
        self.assertEqual(oracle.observe(wrapped_a), oracle.observe(wrapped_b))

    def test_projection_and_literals(self):
        projection = {
            "tag": "projection",
            "type_name": name("Pair"),
            "index": 1,
            "structure": {
                "tag": "application",
                "function": constant("mkPair"),
                "argument": {"tag": "literal", "kind": "natural", "value": "24"},
            },
        }
        self.assertEqual(
            oracle.normalize_expression(projection),
            [9, [[0, "Pair"]], 1, [3, [2, [[0, "mkPair"]], []], [7, 24]]],
        )
        self.assertEqual(
            oracle.normalize_expression({"tag": "literal", "kind": "string", "value": "e\u0301"}),
            [8, "e\u0301"],
        )

    def test_all_six_digest_frames_are_domain_separated(self):
        payload = oracle.proposition_payload(constant("True"))
        frames = oracle.six_digest_frames(payload)
        self.assertEqual(set(frames), set(oracle.DIGEST_DOMAINS))
        self.assertEqual(len({item["digest"] for item in frames.values()}), 6)
        for domain, (purpose, object_class) in oracle.DIGEST_DOMAINS.items():
            frame = bytes.fromhex(frames[domain]["frame_hex"])
            self.assertIn(purpose.encode("ascii"), frame)
            self.assertIn(object_class.encode("ascii"), frame)

    def test_missing_unsupported_and_resource_fail_closed(self):
        cases = (
            ({"tag": "constant", "name": name("X")}, "registry.normalization_failure"),
            ({"tag": "free_variable"}, "registry.expression_unsupported"),
            ({"tag": "literal", "kind": "float", "value": "1.0"}, "registry.expression_unsupported"),
            ({"tag": "constant", "name": name("X"), "universes": [{"tag": "parameter", "name": name("u")}]}, "registry.normalization_failure"),
            ({"tag": "literal", "kind": "string", "value": "x" * (oracle.LIMITS["string_literal_bytes"] + 1)}, "registry.resource_limit"),
        )
        for expression, code in cases:
            with self.subTest(code=code), self.assertRaisesRegex(oracle.OracleError, code):
                oracle.normalize_expression(expression)

    def test_expression_depth_is_bounded(self):
        expression = constant("True")
        for _ in range(oracle.LIMITS["expression_depth"] + 1):
            expression = {
                "tag": "application",
                "function": constant("id"),
                "argument": expression,
            }
        with self.assertRaisesRegex(oracle.OracleError, "registry.resource_limit"):
            oracle.normalize_expression(expression)

    def test_deliberately_wrong_encoder_is_detected(self):
        expression = constant("True")
        correct = oracle.proposition_payload(expression)
        wrong = bytearray(correct)
        wrong[-1] ^= 1
        oracle.require_candidate_bytes(expression, correct)
        with self.assertRaisesRegex(oracle.OracleError, "registry.proposition_mismatch"):
            oracle.require_candidate_bytes(expression, bytes(wrong))

    def test_semantic_array_oracle_covers_expression_and_closure_corpora(self):
        expression = [5, 3, [1, [0]], [0, 0]]
        self.assertEqual(
            oracle.semantic_expression_payload(expression),
            oracle.canonical_cbor([oracle.GRAMMAR_ID, expression]),
        )
        declarations = {
            "root": {"kind": "definition", "references": ["dep"]},
            "dep": {"kind": "definition", "references": []},
        }
        self.assertEqual(
            oracle.environment_closure(["root"], declarations),
            [
                {"name": "dep", "kind": "definition"},
                {"name": "root", "kind": "definition"},
            ],
        )
        with self.assertRaisesRegex(oracle.OracleError, "registry.closure_cycle"):
            oracle.environment_closure(
                ["a"], {"a": {"kind": "definition", "references": ["b"]}, "b": {"kind": "definition", "references": ["a"]}}
            )

    def test_closure_unicode_failures_are_stable(self):
        cases = (
            (["\ud800"], {"\ud800": {"kind": "definition", "references": []}}),
            (["root"], {"root": {"kind": "definition", "references": ["\ud800"]}, "\ud800": {"kind": "definition", "references": []}}),
        )
        for roots, declarations in cases:
            with self.subTest(roots=repr(roots)), self.assertRaisesRegex(
                oracle.OracleError, "registry.normalization_failure"
            ):
                oracle.environment_closure(roots, declarations)
        with self.assertRaisesRegex(oracle.OracleError, "registry.normalization_failure"):
            oracle.environment_closure(
                ["root"], {"root": {"kind": "definition", "references": [], "value": "\ud800"}}
            )

    def test_level_parameter_context_is_closed_and_utf8(self):
        for parameters in (None, "u", 1, [None], [True], ["\ud800"], ["u", "u"]):
            with self.subTest(parameters=repr(parameters)), self.assertRaisesRegex(
                oracle.OracleError, "registry.normalization_failure"
            ):
                oracle.validate_level_parameters(parameters)
        maximum = [f"u{index}" for index in range(oracle.LIMITS["universe_arguments"])]
        self.assertEqual(oracle.validate_level_parameters(maximum), maximum)
        with self.assertRaisesRegex(oracle.OracleError, "registry.resource_limit"):
            oracle.validate_level_parameters(maximum + ["over"])
        for count in (True, -1, oracle.LIMITS["universe_arguments"] + 1):
            with self.assertRaisesRegex(oracle.OracleError, "registry.normalization_failure"):
                oracle.normalize_semantic_expression([1, [0]], level_parameter_count=count)

    def test_malformed_closure_shapes_fail_stably(self):
        cases = (
            (None, {}), ("root", {"root": {"kind": "definition", "references": []}}),
            ([], None), ([], []), (["root"], {"root": None}), (["root"], {"root": []}),
            (["root"], {"root": {"kind": "definition", "references": None}}),
            (["root"], {"root": {"kind": "definition", "references": "dep"}}),
        )
        for roots, declarations in cases:
            with self.subTest(roots=repr(roots), declarations=repr(declarations)), self.assertRaisesRegex(
                oracle.OracleError, "registry.normalization_failure"
            ):
                oracle.environment_closure(roots, declarations)

    def test_closure_declaration_units_are_closed_and_versioned(self):
        accepted = {"a": {"kind": "definition", "references": [], "value": "body"}}
        self.assertEqual(
            oracle.environment_closure(["a"], accepted),
            [{"name": "a", "kind": "definition", "value": "body"}],
        )
        rejected = (
            {"a": None},
            {"a": {"references": []}},
            {"a": {"kind": "unknown", "references": []}},
            {"a": {"kind": "definition", "references": [], "unknown": -1}},
            {"a": {"kind": "definition", "references": [], "value": -1}},
        )
        for declarations in rejected:
            with self.subTest(declarations=declarations), self.assertRaisesRegex(
                oracle.OracleError, "registry.normalization_failure"
            ):
                oracle.environment_closure(["a"], declarations)

    def test_resource_precedence_for_mixed_invalid_declaration(self):
        declarations = {
            "root": {
                "kind": "definition",
                "references": [
                    f"r{index}" for index in range(oracle.LIMITS["closure_width"] + 1)
                ],
                "unknown": True,
            }
        }
        with self.assertRaisesRegex(oracle.OracleError, "registry.closure_width_limit"):
            oracle.environment_closure(["root"], declarations)
        declarations = {
            "root": {
                "kind": "definition",
                "references": [],
                "value": "x" * (oracle.LIMITS["string_literal_bytes"] + 1),
                "unknown": True,
            }
        }
        with self.assertRaisesRegex(oracle.OracleError, "registry.resource_limit"):
            oracle.environment_closure(["root"], declarations)

    def test_cli_is_deterministic_and_uses_stable_errors(self):
        command = [sys.executable, str(SCRIPT_DIR / "independent_oracle.py")]
        input_bytes = (
            '{"expression":{"name":{"parent":{"tag":"anonymous"},'
            '"segment":"True","tag":"string"},"tag":"constant","universes":[]}}'
        ).encode()
        first = subprocess.run(command, input=input_bytes, capture_output=True, check=False)
        second = subprocess.run(command, input=input_bytes, capture_output=True, check=False)
        self.assertEqual(first.returncode, 0)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(first.stderr, b"")
        malformed = subprocess.run(command, input=b"{", capture_output=True, check=False)
        self.assertEqual(malformed.returncode, 2)
        self.assertEqual(
            malformed.stdout,
            b'{"classification":"rejected","code":"registry.normalization_failure"}\n',
        )
        oversized = subprocess.run(
            command,
            input=b" " * (oracle.LIMITS["input_bytes"] + 1),
            capture_output=True,
            check=False,
        )
        self.assertEqual(oversized.returncode, 2)
        self.assertEqual(
            oversized.stdout,
            b'{"classification":"rejected","code":"registry.resource_limit"}\n',
        )
        deeply_nested = subprocess.run(
            command,
            input=(b'{"expression":' + b'[' * 2000 + b'null' + b']' * 2000 + b'}'),
            capture_output=True,
            check=False,
        )
        self.assertEqual(deeply_nested.returncode, 2)
        self.assertEqual(
            deeply_nested.stdout,
            b'{"classification":"rejected","code":"registry.resource_limit"}\n',
        )

    def test_output_does_not_depend_on_input_identity(self):
        expression = constant("True")
        first = oracle.observe(copy.deepcopy(expression))
        second = oracle.observe(copy.deepcopy(expression))
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
