from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest


SCRIPT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

import independent_oracle as oracle
import run_conformance


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


def canonical_payload_expression(leaf_count):
    leaf = [
        2,
        [[1, (1 << 64) - 1]] * oracle.LIMITS["name_segments"],
        [],
    ]
    leaves = [copy.deepcopy(leaf) for _ in range(leaf_count)]
    while len(leaves) > 1:
        paired = [
            [3, leaves[index], leaves[index + 1]]
            for index in range(0, len(leaves) - 1, 2)
        ]
        if len(leaves) % 2:
            paired.append(leaves[-1])
        leaves = paired
    return leaves[0]


def exact_canonical_payload_expression(*, one_over=False):
    expression = canonical_payload_expression(1_474)
    first_leaf = expression
    while first_leaf[0] == 3:
        first_leaf = first_leaf[1]
    first_leaf[1][0] = [0, "x" * oracle.LIMITS["name_segment_bytes"]]
    first_leaf[1][1] = [0, "x" * oracle.LIMITS["name_segment_bytes"]]
    first_leaf[1][2] = [0, "x" * (50 if one_over else 49)]
    return expression


def exact_canonical_payload_declarations(*, one_over=False):
    adjustment = 645 if one_over else 646
    return {
        f"r{index:02d}": {
            "kind": "definition",
            "references": [],
            "value": "x" * (
                oracle.LIMITS["string_literal_bytes"] - 1
                if index < 15
                else oracle.LIMITS["string_literal_bytes"] - 1 - adjustment
            ),
        }
        for index in range(16)
    }


def exact_node_expression():
    leaves = [constant("True") for _ in range(32_767)]
    while len(leaves) > 1:
        paired = [
            {
                "tag": "application",
                "function": leaves[index],
                "argument": leaves[index + 1],
            }
            for index in range(0, len(leaves) - 1, 2)
        ]
        if len(leaves) % 2:
            paired.append(leaves[-1])
        leaves = paired
    return {
        "tag": "lambda",
        "binder_info": "explicit",
        "type": sort(),
        "body": leaves[0],
    }


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
        self.assertEqual(
            oracle.normalize_expression(
                {"tag": "literal", "kind": "natural", "value": "0" * 4_301}
            ),
            [7, 0],
        )
        self.assertEqual(
            oracle.normalize_expression({
                "tag": "literal",
                "kind": "natural",
                "value": str((1 << 64) - 1),
            }),
            [7, (1 << 64) - 1],
        )
        with self.assertRaisesRegex(
            oracle.OracleError, "registry.normalization_failure"
        ):
            oracle.normalize_expression({
                "tag": "literal",
                "kind": "natural",
                "value": str(1 << 64),
            })
        with self.assertRaisesRegex(
            oracle.OracleError, "registry.normalization_failure"
        ):
            oracle.normalize_expression(
                {"tag": "literal", "kind": "natural", "value": "9" * 4_301}
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

    def test_exported_resource_preflight_is_sibling_order_independent(self):
        malformed = {"tag": "unknown"}
        oversized = {
            "tag": "literal",
            "kind": "string",
            "value": "x" * (oracle.LIMITS["string_literal_bytes"] + 1),
        }
        for function, argument in ((malformed, oversized), (oversized, malformed)):
            expression = {
                "tag": "application",
                "function": function,
                "argument": argument,
            }
            with self.subTest(function=function["tag"]), self.assertRaisesRegex(
                oracle.OracleError, "registry.resource_limit"
            ):
                oracle.normalize_expression(expression)

    def test_exported_names_metadata_and_parameter_budgets_match_live_limits(self):
        maximum_name = name(*(["x" * oracle.LIMITS["name_segment_bytes"]] * 4))
        over_name = name(
            *(["x" * oracle.LIMITS["name_segment_bytes"]] * 4), "x"
        )
        oracle.normalize_expression({
            "tag": "constant", "name": maximum_name, "universes": []
        })
        malformed = {"tag": "unknown"}
        for long_node in (
            {"tag": "constant", "name": over_name, "universes": []},
            {
                "tag": "projection", "type_name": over_name, "index": 0,
                "structure": constant("True"),
            },
            {
                "tag": "sort",
                "level": {"tag": "parameter", "name": over_name},
            },
        ):
            for function, argument in ((malformed, long_node), (long_node, malformed)):
                with self.subTest(tag=long_node["tag"]), self.assertRaisesRegex(
                    oracle.OracleError, "registry.resource_limit"
                ):
                    oracle.normalize_expression({
                        "tag": "application", "function": function, "argument": argument
                    })
        with self.assertRaisesRegex(oracle.OracleError, "registry.resource_limit"):
            oracle.normalize_expression(constant("True"), level_parameters=[over_name])

        expression = constant("True")
        for _ in range(oracle.LIMITS["expression_depth"]):
            expression = {"tag": "metadata", "expression": expression}
        oracle.normalize_expression(expression)
        with self.assertRaisesRegex(oracle.OracleError, "registry.resource_limit"):
            oracle.normalize_expression({"tag": "metadata", "expression": expression})

        maximum_nodes = exact_node_expression()
        oracle.normalize_expression(maximum_nodes)
        oracle.normalize_expression({"tag": "metadata", "expression": maximum_nodes})

        parameters = []
        for index in range(oracle.LIMITS["universe_arguments"]):
            suffix = f"{index:03d}"
            parameters.append(name(
                "x" * 256, "x" * 256, "x" * 256, "x" * (256 - len(suffix)) + suffix
            ))
        oracle.normalize_expression(constant("True"), level_parameters=parameters)

    def test_joint_semantic_resource_preflight_precedes_cross_input_syntax(self):
        over_string = [8, "x" * (oracle.LIMITS["string_literal_bytes"] + 1)]
        over_nodes = run_conformance.expanded("@over-expression-nodes@")
        over_depth = run_conformance.expanded("@over-depth@")
        for expression in (over_string, over_nodes, over_depth):
            with self.subTest(resource="expression"), self.assertRaisesRegex(
                oracle.OracleError, "registry.resource_limit"
            ):
                oracle.semantic_expression_payload_with_parameters(expression, [True])
        for parameters in (
            ["u"] * (oracle.LIMITS["universe_arguments"] + 1),
            ["x" * (oracle.LIMITS["name_segment_bytes"] + 1)],
        ):
            with self.subTest(resource="parameters"), self.assertRaisesRegex(
                oracle.OracleError, "registry.resource_limit"
            ):
                oracle.semantic_expression_payload_with_parameters([99], parameters)

    def test_canonical_payload_limit_precedes_sibling_and_root_syntax(self):
        maximum = exact_canonical_payload_expression()
        self.assertEqual(
            len(oracle.semantic_expression_payload(maximum)),
            oracle.LIMITS["payload_bytes"],
        )
        one_over = exact_canonical_payload_expression(one_over=True)
        for expression in (one_over, [3, [99], one_over], [3, one_over, [99]]):
            with self.subTest(kind="expression"), self.assertRaisesRegex(
                oracle.OracleError, "registry.resource_limit"
            ):
                oracle.semantic_expression_payload(expression)

        maximum_declarations = exact_canonical_payload_declarations()
        maximum_records = oracle.environment_closure(
            sorted(maximum_declarations), maximum_declarations
        )
        self.assertEqual(
            len(oracle.canonical_cbor([
                oracle.CLOSURE_ID, oracle.LEAN_COMMIT, oracle.GRAMMAR_ID,
                maximum_records,
            ])),
            oracle.LIMITS["payload_bytes"],
        )
        over_declarations = exact_canonical_payload_declarations(one_over=True)
        for roots, declarations in (
            (sorted(over_declarations), over_declarations),
            (["a", *sorted(over_declarations)], {
                "a": {"kind": "unknown", "references": []}, **over_declarations,
            }),
        ):
            with self.subTest(kind="closure"), self.assertRaisesRegex(
                oracle.OracleError, "registry.resource_limit"
            ):
                oracle.environment_closure(roots, declarations)

    def test_exported_environment_records_are_closed_total_and_bounded(self):
        valid = {
            "body": constant("True"),
            "kind": "definition",
            "level_parameters": [],
            "name": name("StatQED", "Registry", "fixture"),
            "origin": "project",
            "reducibility": "regular",
            "references": [],
            "type": sort(),
            "unsafe": False,
        }
        oracle.environment_payload_from_records([valid], oracle.LEAN_COMMIT)
        malformed = (
            "not-an-array",
            [None],
            [{key: value for key, value in valid.items() if key != "kind"}],
            [{**valid, "unknown": True}],
            [{**valid, "name": name(*(["x"] * 65))}],
            [{**valid, "name": name("x" * 257)}],
            [{**valid, "name": name(*(["x" * 256] * 5))}],
        )
        for records in malformed:
            code = (
                "registry.resource_limit"
                if isinstance(records, list) and records and isinstance(records[0], dict)
                and records[0].get("name") != valid["name"]
                else "registry.normalization_failure"
            )
            with self.subTest(records=type(records).__name__), self.assertRaisesRegex(
                oracle.OracleError, code
            ):
                oracle.environment_payload_from_records(records, oracle.LEAN_COMMIT)
        deep = anonymous()
        for _ in range(2_000):
            deep = {"tag": "string", "parent": deep, "segment": "x"}
        with self.assertRaisesRegex(oracle.OracleError, "registry.resource_limit"):
            oracle.environment_payload_from_records(
                [{**valid, "name": deep}], oracle.LEAN_COMMIT
            )

    def test_exported_environment_payload_preflight_precedes_record_syntax(self):
        def definition(index):
            return {
                "body": {
                    "tag": "literal",
                    "kind": "string",
                    "value": "x" * (oracle.LIMITS["string_literal_bytes"] - 1),
                },
                "kind": "definition",
                "level_parameters": [],
                "name": name("StatQED", "Registry", f"large{index:02d}"),
                "origin": "project",
                "reducibility": "regular",
                "references": [],
                "type": sort(),
                "unsafe": False,
            }

        maximum = [definition(index) for index in range(15)]
        oracle.environment_payload_from_records(maximum, oracle.LEAN_COMMIT)
        one_over = [*maximum, definition(15)]
        malformed = {**definition(16), "unknown": True}
        for records in (one_over, [malformed, *one_over], [*one_over, malformed]):
            with self.subTest(first=records[0]["name"]), self.assertRaisesRegex(
                oracle.OracleError, "registry.resource_limit"
            ):
                oracle.environment_payload_from_records(records, oracle.LEAN_COMMIT)

    def test_exported_environment_enum_shapes_fail_stably(self):
        valid = {
            "body": constant("True"),
            "kind": "definition",
            "level_parameters": [],
            "name": name("StatQED", "Registry", "fixture"),
            "origin": "project",
            "reducibility": "regular",
            "references": [],
            "type": sort(),
            "unsafe": False,
        }
        malformed_values = ([], {})
        for malformed in malformed_values:
            cases = (
                {**valid, "kind": malformed},
                {**valid, "origin": malformed},
                {**valid, "reducibility": malformed},
                {**valid, "name": {"tag": malformed}},
                {**valid, "body": {"tag": malformed}},
                {
                    **valid,
                    "body": {"tag": "literal", "kind": malformed, "value": "x"},
                },
                {
                    **valid,
                    "body": {
                        "tag": "lambda",
                        "binder_info": malformed,
                        "type": sort(),
                        "body": {"tag": "bound_variable", "index": 0},
                    },
                },
            )
            for index, candidate in enumerate(cases):
                with self.subTest(value=type(malformed).__name__, index=index), self.assertRaisesRegex(
                    oracle.OracleError, "registry.normalization_failure"
                ):
                    oracle.environment_payload_from_records(
                        [candidate], oracle.LEAN_COMMIT
                    )

    def test_nested_typed_enums_fail_stably(self):
        valid = {
            "body": constant("True"),
            "kind": "definition",
            "level_parameters": [],
            "name": name("StatQED", "Registry", "fixture"),
            "origin": "project",
            "reducibility": "regular",
            "references": [],
            "type": sort(),
            "unsafe": False,
        }
        malformed_values = ([], {})
        for malformed in malformed_values:
            expressions = (
                {"tag": malformed},
                {"tag": "sort", "level": {"tag": malformed}},
                {
                    "tag": "constant",
                    "name": {"tag": malformed},
                    "universes": [],
                },
                {
                    "tag": "constant",
                    "name": name("True"),
                    "universes": [{"tag": malformed}],
                },
                {
                    "tag": "lambda",
                    "binder_info": malformed,
                    "type": sort(),
                    "body": {"tag": "bound_variable", "index": 0},
                },
                {"tag": "literal", "kind": malformed, "value": "x"},
            )
            for index, expression in enumerate(expressions):
                with self.subTest(
                    entrypoint="direct", value=type(malformed).__name__, index=index
                ), self.assertRaisesRegex(
                    oracle.OracleError, "registry.normalization_failure"
                ):
                    oracle.normalize_expression(expression)
                with self.subTest(
                    entrypoint="environment", value=type(malformed).__name__, index=index
                ), self.assertRaisesRegex(
                    oracle.OracleError, "registry.normalization_failure"
                ):
                    oracle.environment_payload_from_records(
                        [{**valid, "type": expression}], oracle.LEAN_COMMIT
                    )

    def test_exported_nested_declarations_use_their_own_universe_contexts(self):
        observation = json.loads(
            (SCRIPT_DIR.parents[1] / "theorem-registry/evidence/lean-observation.json")
            .read_text(encoding="utf-8")
        )
        closure = copy.deepcopy(observation["declarations"][0]["closure"])
        family = next(record for record in closure if record["kind"] == "inductive_family")
        declared = name("u")
        second = name("v")
        undeclared_sort = {
            "tag": "sort",
            "level": {"tag": "parameter", "name": name("rogue")},
        }

        self.assertIn("level_parameters", family["members"][0]["constructors"][0])
        self.assertIn("level_parameters", family["recursors"][0])
        oracle.environment_payload_from_records(closure, oracle.LEAN_COMMIT)

        valid_contexts = copy.deepcopy(closure)
        valid_family = next(
            record for record in valid_contexts if record["kind"] == "inductive_family"
        )
        valid_member = valid_family["members"][0]
        valid_member["level_parameters"] = [declared, second]
        valid_member["type"] = {
            "tag": "sort",
            "level": {
                "tag": "max",
                "left": {"tag": "parameter", "name": declared},
                "right": {"tag": "parameter", "name": second},
            },
        }
        valid_constructor = valid_member["constructors"][0]
        valid_constructor["level_parameters"] = [second, declared]
        valid_constructor["type"] = {
            "tag": "sort",
            "level": {"tag": "parameter", "name": second},
        }
        oracle.environment_payload_from_records(valid_contexts, oracle.LEAN_COMMIT)

        mutations = []
        member = family["members"][0]
        mutations.append((member, "type", undeclared_sort))
        constructor = member["constructors"][0]
        mutations.append((constructor, "type", undeclared_sort))
        recursor = family["recursors"][0]
        mutations.append((recursor, "type", undeclared_sort))
        mutations.append((recursor["rules"][0], "rhs", undeclared_sort))

        for index, (_target, field, value) in enumerate(mutations):
            candidate = copy.deepcopy(closure)
            candidate_family = next(
                record for record in candidate if record["kind"] == "inductive_family"
            )
            candidate_member = candidate_family["members"][0]
            candidate_constructor = candidate_member["constructors"][0]
            candidate_recursor = candidate_family["recursors"][0]
            targets = (
                candidate_member,
                candidate_constructor,
                candidate_recursor,
                candidate_recursor["rules"][0],
            )
            if index == 0:
                targets[index]["level_parameters"] = [declared]
            targets[index][field] = value
            with self.subTest(index=index), self.assertRaisesRegex(
                oracle.OracleError, "registry.normalization_failure"
            ):
                oracle.environment_payload_from_records(candidate, oracle.LEAN_COMMIT)

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

    def test_resource_preflight_is_independent_of_expression_and_root_order(self):
        over_nodes = run_conformance.expanded("@over-expression-nodes@")
        over_string = [8, "x" * (oracle.LIMITS["string_literal_bytes"] + 1)]
        for expression in (
            [3, [99], over_nodes],
            [3, over_nodes, [99]],
            [3, [99], over_string],
            [3, over_string, [99]],
        ):
            with self.subTest(kind="expression"), self.assertRaisesRegex(
                oracle.OracleError, "registry.resource_limit"
            ):
                oracle.normalize_semantic_expression(expression)

        declarations = {
            "a": {"kind": "unknown", "references": []},
            "z": {
                "kind": "definition",
                "references": [],
                "value": "x" * (oracle.LIMITS["string_literal_bytes"] + 1),
            },
        }
        for roots in (["a", "z"], ["z", "a"]):
            with self.subTest(roots=roots), self.assertRaisesRegex(
                oracle.OracleError, "registry.resource_limit"
            ):
                oracle.environment_closure(roots, declarations)

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
        wrong_enum_documents = (
            {"expression": {"tag": []}},
            {
                "expression": {
                    "tag": "sort",
                    "level": {"tag": []},
                }
            },
            {
                "expression": {
                    "tag": "lambda",
                    "binder_info": [],
                    "type": sort(),
                    "body": {"tag": "bound_variable", "index": 0},
                }
            },
            {
                "expression": {
                    "tag": "constant",
                    "name": {"tag": []},
                    "universes": [],
                }
            },
            {
                "expression": {
                    "tag": "constant",
                    "name": name("True"),
                    "universes": [{"tag": []}],
                }
            },
            {
                "expression": {
                    "tag": "literal",
                    "kind": [],
                    "value": "x",
                }
            },
            {
                "expression": {
                    "tag": "literal",
                    "kind": "natural",
                    "value": "9" * 4_301,
                }
            },
        )
        for document in wrong_enum_documents:
            wrong_enum = subprocess.run(
                command,
                input=json.dumps(document, separators=(",", ":")).encode(),
                capture_output=True,
                check=False,
            )
            with self.subTest(document=document):
                self.assertEqual(wrong_enum.returncode, 2)
                self.assertEqual(
                    wrong_enum.stdout,
                    b'{"classification":"rejected","code":"registry.normalization_failure"}\n',
                )
                self.assertEqual(wrong_enum.stderr, b"")

    def test_output_does_not_depend_on_input_identity(self):
        expression = constant("True")
        first = oracle.observe(copy.deepcopy(expression))
        second = oracle.observe(copy.deepcopy(expression))
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
