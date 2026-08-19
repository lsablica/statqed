from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest

SCRIPT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

import model


ROOT = Path(__file__).resolve().parents[3]


class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = json.loads((ROOT / "theorem-registry/evidence/bundle.json").read_text())
        cls.policy = json.loads((ROOT / "theorem-registry/policy/authorization-v0.json").read_text())

    def test_true_vector_matches_independent_fixed_vector(self):
        payload = model.canonical_cbor(["statqed.lean-expr.v0", [2, [[0, "True"]], []]])
        self.assertEqual(payload.hex(), "8274737461747165642e6c65616e2d657870722e76308302818200645472756580")
        self.assertEqual(model.digest_frame("proposition", payload)[1], "68a6c0b4a9c83cc7c29c251b900d5a3c265fe9b4856df78a590aef99492513c4")

    def test_map_order_is_independent_of_insertion(self):
        self.assertEqual(model.canonical_cbor({"b": 2, "a": 1}), model.canonical_cbor({"a": 1, "b": 2}))

    def test_six_domains_are_distinct(self):
        payload = model.canonical_cbor(["x"])
        digests = {model.digest_frame(kind, payload)[1] for kind in model.PURPOSES}
        self.assertEqual(len(digests), 6)

    def test_all_declared_errors_are_stable(self):
        for code in model.ERRORS:
            self.assertEqual(model.RegistryError(code).code, code)
        with self.assertRaises(ValueError):
            model.RegistryError("host-dependent debug text")

    def test_expression_constructor_vectors(self):
        vectors = (
            ([1, [0]], []),
            ([2, [[0, "X"]], []], []),
            ([3, [2, [[0, "f"]], []], [2, [[0, "x"]], []]], []),
            ([4, 0, [1, [0]], [0, 0]], []),
            ([5, 3, [1, [0]], [0, 0]], []),
            ([6, [1, [0]], [1, [0]], [0, 0]], []),
            ([7, 24], []),
            ([8, "text"], []),
            ([9, [[0, "Pair"]], 0, [2, [[0, "p"]], []]], []),
        )
        for expression, params in vectors:
            with self.subTest(expression=expression):
                self.assertEqual(model.normalize_expr(expression, level_params=params), expression)

    def test_expression_and_level_depth_boundaries(self):
        expression = [2, [[0, "x"]], []]
        for _ in range(model.LIMITS["expression_depth"]):
            expression = [3, [2, [[0, "f"]], []], expression]
        self.assertEqual(model.normalize_expr(expression), expression)
        with self.assertRaisesRegex(model.RegistryError, "registry.resource_limit"):
            model.normalize_expr([3, [2, [[0, "f"]], []], expression])

        level = [0]
        for _ in range(model.LIMITS["level_depth"]):
            level = [1, level]
        self.assertEqual(model.normalize_expr([1, level]), [1, level])
        with self.assertRaisesRegex(model.RegistryError, "registry.resource_limit"):
            model.normalize_expr([1, [1, level]])

    def test_normalizer_structural_boundaries_accept_maximum_and_reject_one_over(self):
        universes = [[0]] * model.LIMITS["universe_arguments"]
        self.assertEqual(
            model.normalize_expr([2, [[0, "X"]], universes]),
            [2, [[0, "X"]], universes],
        )
        with self.assertRaisesRegex(model.RegistryError, "registry.resource_limit"):
            model.normalize_expr([2, [[0, "X"]], universes + [[0]]])

        segments = [[0, "x"]] * model.LIMITS["name_segments"]
        self.assertEqual(model.normalize_expr([2, segments, []]), [2, segments, []])
        with self.assertRaisesRegex(model.RegistryError, "registry.resource_limit"):
            model.normalize_expr([2, segments + [[0, "x"]], []])

        segment = "x" * model.LIMITS["name_segment_bytes"]
        self.assertEqual(model.normalize_expr([2, [[0, segment]], []]), [2, [[0, segment]], []])
        with self.assertRaisesRegex(model.RegistryError, "registry.resource_limit"):
            model.normalize_expr([2, [[0, segment + "x"]], []])

        qualified = [[0, "x" * model.LIMITS["name_segment_bytes"]]] * (
            model.LIMITS["qualified_name_bytes"] // model.LIMITS["name_segment_bytes"]
        )
        self.assertEqual(model.normalize_expr([2, qualified, []]), [2, qualified, []])
        with self.assertRaisesRegex(model.RegistryError, "registry.resource_limit"):
            model.normalize_expr([2, qualified + [[0, "x"]], []])

    def test_binder_info_changes_identity(self):
        vectors = [model.canonical_cbor(model.normalize_expr([5, info, [1, [0]], [0, 0]])) for info in range(4)]
        self.assertEqual(len(set(vectors)), 4)

    def test_integer_type_unicode_and_uint64_boundaries(self):
        rejected = (
            [5, True, [1, [0]], [0, 0]], [5, False, [1, [0]], [0, 0]],
            [2, [[False, "x"]], []], [8, "\ud800"], [8, "\udfff"],
            [2, [[0, "\ud800"]], []], [7, 1 << 64],
            [9, [[0, "P"]], 1 << 64, [2, [[0, "x"]], []]],
            [2, [[1, 1 << 64]], []], [4, 0, [1, [0]], [0, 1 << 64]],
        )
        for expression in rejected:
            with self.subTest(expression=repr(expression)), self.assertRaisesRegex(
                model.RegistryError, "registry.normalization_failure"
            ):
                model.normalize_expr(expression)
        maximum = (1 << 64) - 1
        for expression in (
            [7, maximum], [9, [[0, "P"]], maximum, [2, [[0, "x"]], []]],
            [2, [[1, maximum]], []],
        ):
            self.assertEqual(model.normalize_expr(expression), expression)

    def test_closure_unicode_failures_are_stable(self):
        cases = (
            (["\ud800"], {"\ud800": {"kind": "definition", "references": []}}),
            (["root"], {"root": {"kind": "definition", "references": ["\ud800"]}, "\ud800": {"kind": "definition", "references": []}}),
        )
        for roots, declarations in cases:
            with self.subTest(roots=repr(roots)), self.assertRaisesRegex(
                model.RegistryError, "registry.normalization_failure"
            ):
                model.closure(roots, declarations)
        with self.assertRaisesRegex(model.RegistryError, "registry.normalization_failure"):
            model.closure(
                ["root"], {"root": {"kind": "definition", "references": [], "value": "\ud800"}}
            )

    def test_semantic_limits_survive_canonical_framing(self):
        leaves = [[0, 0] for _ in range(32_767)]
        while len(leaves) > 1:
            paired = [[3, leaves[index], leaves[index + 1]] for index in range(0, len(leaves) - 1, 2)]
            if len(leaves) % 2:
                paired.append(leaves[-1])
            leaves = paired
        exact_nodes = [4, 0, [1, [0]], leaves[0]]
        model.canonical_cbor(["statqed.lean-expr.v0", model.normalize_expr(exact_nodes)])
        over_nodes = copy.deepcopy(exact_nodes)
        over_nodes[2] = [1, [1, [0]]]
        with self.assertRaisesRegex(model.RegistryError, "registry.resource_limit"):
            model.normalize_expr(over_nodes)
        level = [0]
        for _ in range(model.LIMITS["level_depth"]):
            level = [1, level]
        combined = [1, level]
        for _ in range(model.LIMITS["expression_depth"]):
            combined = [3, [2, [[0, "f"]], []], combined]
        model.canonical_cbor(["statqed.lean-expr.v0", model.normalize_expr(combined)])
        literal = [8, "x" * model.LIMITS["string_bytes"]]
        aggregate = [3, [3, literal, literal], [3, literal, literal]]
        model.canonical_cbor(["statqed.lean-expr.v0", model.normalize_expr(aggregate)])
        with self.assertRaisesRegex(model.RegistryError, "registry.resource_limit"):
            model.normalize_expr([3, aggregate, [8, "x"]])

    def test_loose_variable_rejected(self):
        with self.assertRaisesRegex(model.RegistryError, "registry.normalization_failure"):
            model.normalize_expr([0, 0])

    def test_unknown_expression_rejected(self):
        with self.assertRaisesRegex(model.RegistryError, "registry.normalization_failure"):
            model.normalize_expr([99])

    def test_universe_parameter_must_be_declared(self):
        with self.assertRaisesRegex(model.RegistryError, "registry.normalization_failure"):
            model.normalize_expr([1, [4, 0]])
        self.assertEqual(model.normalize_expr([1, [4, 0]], level_params=["u"]), [1, [4, 0]])

    def test_level_parameter_context_is_closed_and_utf8(self):
        for parameters in ("u", 1, [None], [True], ["\ud800"], ["u", "u"]):
            with self.subTest(parameters=repr(parameters)), self.assertRaisesRegex(
                model.RegistryError, "registry.normalization_failure"
            ):
                model.validate_level_parameters(parameters)
        maximum = [f"u{index}" for index in range(model.LIMITS["universe_arguments"])]
        self.assertEqual(model.validate_level_parameters(maximum), maximum)
        with self.assertRaisesRegex(model.RegistryError, "registry.resource_limit"):
            model.validate_level_parameters(maximum + ["over"])

    def test_bundle_and_policy_shapes_fail_stably(self):
        for bundle in (None, []):
            with self.subTest(bundle=repr(bundle)), self.assertRaisesRegex(
                model.RegistryError, "registry.malformed_record"
            ):
                model.verify_bundle(bundle, copy.deepcopy(self.policy))
        with self.assertRaisesRegex(model.RegistryError, "registry.authorization_policy_unsupported"):
            model.verify_bundle(copy.deepcopy(self.bundle), None)

    def test_candidate_digest_and_record_types_fail_as_malformed(self):
        for field in (
            "requested_root", "record_digest", "proposition_digest",
            "environment_digest", "proof_build_digest", "compatibility_digest",
        ):
            bundle = copy.deepcopy(self.bundle)
            bundle[field] = "not-a-digest"
            with self.subTest(field=field), self.assertRaisesRegex(
                model.RegistryError, "registry.malformed_record"
            ):
                model.verify_bundle(bundle, copy.deepcopy(self.policy))
        bundle = copy.deepcopy(self.bundle)
        bundle["record"]["schema"] = None
        with self.assertRaisesRegex(model.RegistryError, "registry.malformed_record"):
            model.verify_bundle(bundle, copy.deepcopy(self.policy))

    def test_json_structure_depth_boundary(self):
        value = None
        for _ in range(model.LIMITS["canonical_depth"]):
            value = [value]
        model.canonical_json(value)
        with self.assertRaisesRegex(model.RegistryError, "registry.resource_limit"):
            model.canonical_json([value])
        with self.assertRaisesRegex(model.RegistryError, "registry.resource_limit"):
            model.canonical_json(1 << 64)
        cyclic = []
        cyclic.append(cyclic)
        with self.assertRaisesRegex(model.RegistryError, "registry.normalization_failure"):
            model.canonical_json(cyclic)

        retained = model.retained_evidence_json({"rejected_integer": 1 << 64})
        self.assertIn(b'"rejected_integer":18446744073709551616', retained)

    def test_closure_is_sorted(self):
        declarations = {
            "z": {"kind": "definition", "references": ["a"]},
            "a": {"kind": "definition", "references": []},
        }
        self.assertEqual([item["name"] for item in model.closure(["z"], declarations)], ["a", "z"])

    def test_closure_uses_canonical_name_bytes_not_text_order(self):
        declarations = {
            "aa": {"kind": "definition", "references": []},
            "b": {"kind": "definition", "references": []},
        }
        self.assertEqual(
            [item["name"] for item in model.closure(["aa", "b"], declarations)],
            ["b", "aa"],
        )

    def test_closure_missing_rejected(self):
        with self.assertRaisesRegex(model.RegistryError, "registry.missing_dependency"):
            model.closure(["x"], {})

    def test_closure_cycle_rejected(self):
        declarations = {"a": {"kind": "definition", "references": ["b"]}, "b": {"kind": "definition", "references": ["a"]}}
        with self.assertRaisesRegex(model.RegistryError, "registry.closure_cycle"):
            model.closure(["a"], declarations)

    def test_closure_width_boundary(self):
        roots = [f"x{i}" for i in range(model.LIMITS["closure_width"])]
        declarations = {name: {"kind": "definition", "references": []} for name in roots}
        self.assertEqual(len(model.closure(roots, declarations)), len(roots))
        with self.assertRaisesRegex(model.RegistryError, "registry.closure_width_limit"):
            model.closure(roots + ["over"], declarations)
        outgoing = [f"d{i}" for i in range(model.LIMITS["closure_width"])]
        graph = {"root": {"kind": "definition", "references": outgoing}, **{name: {"kind": "definition", "references": []} for name in outgoing}}
        self.assertEqual(len(model.closure(["root"], graph)), len(outgoing) + 1)
        graph["root"]["references"].append("over")
        graph["over"] = {"kind": "definition", "references": []}
        with self.assertRaisesRegex(model.RegistryError, "registry.closure_width_limit"):
            model.closure(["root"], graph)

    def test_closure_depth_boundary(self):
        accepted = {
            f"n{index}": {
                "kind": "definition",
                "references": [] if index == model.LIMITS["closure_depth"] else [f"n{index + 1}"]
            }
            for index in range(model.LIMITS["closure_depth"] + 1)
        }
        self.assertEqual(len(model.closure(["n0"], accepted)), len(accepted))
        rejected = copy.deepcopy(accepted)
        rejected[f"n{model.LIMITS['closure_depth']}"]["references"] = ["over"]
        rejected["over"] = {"kind": "definition", "references": []}
        with self.assertRaisesRegex(model.RegistryError, "registry.closure_depth_limit"):
            model.closure(["n0"], rejected)

    def test_closure_unit_boundary_has_no_off_by_one_escape(self):
        maximum = model.LIMITS["closure_units"]
        branches = [f"b{i}" for i in range(model.LIMITS["closure_width"])]
        accepted = {"root": {"kind": "definition", "references": branches}}
        remaining = maximum - 1 - len(branches)
        for index, branch in enumerate(branches):
            leaf_count = min(3, remaining)
            leaves = [f"{branch}.l{leaf}" for leaf in range(leaf_count)]
            accepted[branch] = {"kind": "definition", "references": leaves}
            accepted.update({leaf: {"kind": "definition", "references": []} for leaf in leaves})
            remaining -= leaf_count
        self.assertEqual(remaining, 0)
        self.assertEqual(len(model.closure(["root"], accepted)), maximum)
        rejected = copy.deepcopy(accepted)
        rejected[branches[-1]]["references"].append("one.over")
        rejected["one.over"] = {"kind": "definition", "references": []}
        with self.assertRaisesRegex(model.RegistryError, "registry.closure_work_budget_limit"):
            model.closure(["root"], rejected)

    def test_closure_declaration_units_are_closed_and_versioned(self):
        accepted = {"a": {"kind": "definition", "references": [], "value": "body"}}
        self.assertEqual(model.closure(["a"], accepted), [{"name": "a", "kind": "definition", "value": "body"}])
        rejected = (
            {"a": None},
            {"a": {"references": []}},
            {"a": {"kind": "unknown", "references": []}},
            {"a": {"kind": "definition", "references": [], "unknown": -1}},
            {"a": {"kind": "definition", "references": [], "value": -1}},
        )
        for declarations in rejected:
            with self.subTest(declarations=declarations), self.assertRaisesRegex(
                model.RegistryError, "registry.normalization_failure"
            ):
                model.closure(["a"], declarations)

    def test_resource_precedence_for_mixed_invalid_declaration(self):
        declarations = {
            "root": {
                "kind": "definition",
                "references": [
                    f"r{index}" for index in range(model.LIMITS["closure_width"] + 1)
                ],
                "unknown": True,
            }
        }
        with self.assertRaisesRegex(model.RegistryError, "registry.closure_width_limit"):
            model.closure(["root"], declarations)
        declarations = {
            "root": {
                "kind": "definition",
                "references": [],
                "value": "x" * (model.LIMITS["string_bytes"] + 1),
                "unknown": True,
            }
        }
        with self.assertRaisesRegex(model.RegistryError, "registry.resource_limit"):
            model.closure(["root"], declarations)

    def test_fixed_work_cap_is_explicitly_dominated_by_other_v0_limits(self):
        dominance_upper_bound = (
            262_144
            + model.LIMITS["closure_units"]
            + model.LIMITS["closure_units"] * model.LIMITS["closure_width"]
        )
        self.assertEqual(dominance_upper_bound, 525_312)
        self.assertLess(dominance_upper_bound, model.LIMITS["work"])

    def test_identifier_boundary(self):
        self.assertEqual(model.validate_identifier("a" + "x" * 127), "a" + "x" * 127)
        with self.assertRaisesRegex(model.RegistryError, "registry.resource_limit"):
            model.validate_identifier("a" + "x" * 128)
        with self.assertRaisesRegex(model.RegistryError, "registry.malformed_record"):
            model.validate_identifier("é" * 64)
        with self.assertRaisesRegex(model.RegistryError, "registry.resource_limit"):
            model.validate_identifier("é" * 64 + "a")
        with self.assertRaisesRegex(model.RegistryError, "registry.malformed_record"):
            model.validate_identifier("Upper")

    def test_current_root_accepts(self):
        self.assertEqual(model.verify_bundle(copy.deepcopy(self.bundle), copy.deepcopy(self.policy))["classification"], "accepted")

    def test_candidate_policy_is_ignored(self):
        bundle = copy.deepcopy(self.bundle)
        bundle["candidate_policy"] = {"current_permitted_roots": ["00" * 32]}
        self.assertEqual(model.verify_bundle(bundle, copy.deepcopy(self.policy))["classification"], "accepted")

    def test_revocation_dominates(self):
        policy = copy.deepcopy(self.policy)
        policy["current_permitted_roots"] = []
        policy["revoked_roots"] = [self.bundle["requested_root"]]
        with self.assertRaisesRegex(model.RegistryError, "registry.authorization_root_revoked"):
            model.verify_bundle(copy.deepcopy(self.bundle), policy)

    def test_unknown_root_rejected(self):
        policy = copy.deepcopy(self.policy)
        policy["current_permitted_roots"] = []
        with self.assertRaisesRegex(model.RegistryError, "registry.authorization_root_unknown"):
            model.verify_bundle(copy.deepcopy(self.bundle), policy)

    def test_historical_forbidden_rejected(self):
        policy = copy.deepcopy(self.policy)
        policy["current_permitted_roots"] = []
        policy["historical_forbidden_roots"] = [self.bundle["requested_root"]]
        with self.assertRaisesRegex(model.RegistryError, "registry.authorization_root_historical_forbidden"):
            model.verify_bundle(copy.deepcopy(self.bundle), policy)

    def test_authorization_root_classes_must_be_pairwise_disjoint(self):
        for field in (
            "historical_permitted_roots",
            "historical_forbidden_roots",
            "revoked_roots",
        ):
            with self.subTest(field=field):
                policy = copy.deepcopy(self.policy)
                policy[field].append(self.bundle["requested_root"])
                with self.assertRaisesRegex(
                    model.RegistryError, "registry.authorization_policy_unsupported"
                ):
                    model.verify_bundle(copy.deepcopy(self.bundle), policy)

    def test_authorization_policy_is_closed_bounded_and_utf8(self):
        mutations = []
        for field, value in (("schema", "forged"), ("selection", "candidate_selected")):
            policy = copy.deepcopy(self.policy); policy[field] = value; mutations.append(policy)
        policy = copy.deepcopy(self.policy); policy["unknown"] = "field"; mutations.append(policy)
        policy = copy.deepcopy(self.policy); policy["historical_permitted_roots"].append("not-a-digest"); mutations.append(policy)
        for policy in mutations:
            with self.assertRaisesRegex(model.RegistryError, "registry.authorization_policy_unsupported"):
                model.verify_bundle(copy.deepcopy(self.bundle), policy)
        policy = copy.deepcopy(self.policy)
        policy["current_permitted_roots"] += [f"{index + 4:064x}" for index in range(13)]
        with self.assertRaisesRegex(model.RegistryError, "registry.resource_limit"):
            model.verify_bundle(copy.deepcopy(self.bundle), policy)
        policy = copy.deepcopy(self.policy)
        policy["current_permitted_roots"] = ["not-a-digest"] + [
            f"{index + 4:064x}" for index in range(model.LIMITS["registry_entries"])
        ]
        with self.assertRaisesRegex(model.RegistryError, "registry.resource_limit"):
            model.verify_bundle(copy.deepcopy(self.bundle), policy)
        policy = copy.deepcopy(self.policy)
        policy["compatibility_digest"] = "x" * (model.LIMITS["string_bytes"] + 1)
        with self.assertRaisesRegex(model.RegistryError, "registry.resource_limit"):
            model.verify_bundle(copy.deepcopy(self.bundle), policy)
        bundle = copy.deepcopy(self.bundle); bundle["candidate_policy"] = "\ud800"
        with self.assertRaisesRegex(model.RegistryError, "registry.normalization_failure"):
            model.verify_bundle(bundle, copy.deepcopy(self.policy))
        bundle = copy.deepcopy(self.bundle)
        bundle["unknown"] = "x" * (model.LIMITS["string_bytes"] + 1)
        with self.assertRaisesRegex(model.RegistryError, "registry.resource_limit"):
            model.verify_bundle(bundle, copy.deepcopy(self.policy))

    def test_forged_metadata_rejected(self):
        bundle = copy.deepcopy(self.bundle)
        bundle["record"]["maturity"] = "Stable"
        with self.assertRaisesRegex(model.RegistryError, "registry.record_digest_mismatch"):
            model.verify_bundle(bundle, copy.deepcopy(self.policy))

    def test_reauthorized_self_consistent_record_forgery_is_rejected(self):
        mutations = {
            "declaration": "StatQED.Registry.Tests.forged",
            "normalizer": "statqed.lean-expr.v999",
            "closure": "statqed.lean-environment-closure.v999",
            "version": "9.9.9",
            "source_anchor": "forged/source.md",
            "attribution": "forged attribution",
            "nonclaims": ["forged public theorem claim"],
            "axiom_report_digest": "44" * 32,
        }
        for field, value in mutations.items():
            with self.subTest(field=field):
                bundle = copy.deepcopy(self.bundle)
                policy = copy.deepcopy(self.policy)
                bundle["record"][field] = value
                _, digest = model.digest_frame(
                    "record", model.canonical_cbor(bundle["record"])
                )
                bundle["record_digest"] = digest
                bundle["snapshot"] = {
                    "schema": "statqed.registry-snapshot.v0",
                    "records": [[bundle["record"]["id"], bundle["record"]["version"], digest]],
                }
                _, root = model.digest_frame(
                    "snapshot", model.canonical_cbor(bundle["snapshot"])
                )
                bundle["requested_root"] = root
                policy["current_permitted_roots"] = [root]
                with self.assertRaisesRegex(
                    model.RegistryError, "registry.record_digest_mismatch"
                ):
                    model.verify_bundle(bundle, policy)

    def test_forbidden_axiom_rejected(self):
        bundle = copy.deepcopy(self.bundle)
        bundle["axioms"] = ["sorryAx"]
        with self.assertRaisesRegex(model.RegistryError, "registry.forbidden_axiom"):
            model.verify_bundle(bundle, copy.deepcopy(self.policy))

    def test_axiom_count_resource_boundary(self):
        bundle = copy.deepcopy(self.bundle)
        bundle["axioms"] = ["Classical.choice"] * model.LIMITS["axioms"]
        with self.assertRaisesRegex(model.RegistryError, "registry.forbidden_axiom"):
            model.verify_bundle(bundle, copy.deepcopy(self.policy))
        bundle["axioms"].append("Classical.choice")
        with self.assertRaisesRegex(model.RegistryError, "registry.resource_limit"):
            model.verify_bundle(bundle, copy.deepcopy(self.policy))

    def test_snapshot_entry_resource_boundary(self):
        for count, code in (
            (model.LIMITS["registry_entries"], "registry.malformed_record"),
            (model.LIMITS["registry_entries"] + 1, "registry.resource_limit"),
        ):
            bundle = copy.deepcopy(self.bundle)
            bundle["snapshot"]["records"] = [
                [f"statqed.test-only.snapshot-{index:02d}.v0", "0.0.1", bundle["record_digest"]]
                for index in range(count)
            ]
            _, root = model.digest_frame("snapshot", model.canonical_cbor(bundle["snapshot"]))
            bundle["requested_root"] = root
            policy = copy.deepcopy(self.policy)
            policy["current_permitted_roots"] = [root]
            with self.subTest(count=count), self.assertRaisesRegex(model.RegistryError, code):
                model.verify_bundle(bundle, policy)

    def test_resource_precedence_over_mixed_schema_failures(self):
        bundle = copy.deepcopy(self.bundle)
        bundle["record"]["id"] = "a" * (model.LIMITS["identifier_bytes"] + 1)
        bundle["record"]["schema"] = "statqed.registry-record.v999"
        with self.assertRaisesRegex(model.RegistryError, "registry.resource_limit"):
            model.verify_bundle(bundle, copy.deepcopy(self.policy))

        bundle = copy.deepcopy(self.bundle)
        bundle["snapshot"]["records"] = [
            [f"statqed.test-only.snapshot-{index:02d}.v0", "0.0.1", bundle["record_digest"]]
            for index in range(model.LIMITS["registry_entries"] + 1)
        ]
        bundle["snapshot"]["unknown"] = True
        with self.assertRaisesRegex(model.RegistryError, "registry.resource_limit"):
            model.verify_bundle(bundle, copy.deepcopy(self.policy))

        bundle = copy.deepcopy(self.bundle)
        bundle["axioms"] = ["Classical.choice"] * (model.LIMITS["axioms"] + 1)
        bundle["record"]["schema"] = "statqed.registry-record.v999"
        with self.assertRaisesRegex(model.RegistryError, "registry.resource_limit"):
            model.verify_bundle(bundle, copy.deepcopy(self.policy))

    def test_wrong_compatibility_direction_rejected(self):
        bundle = copy.deepcopy(self.bundle)
        bundle["compatibility"] = copy.deepcopy(self.policy["compatibility_binding"])
        bundle["compatibility"]["direction"] = "old_implies_new"
        with self.assertRaisesRegex(model.RegistryError, "registry.compatibility_wrong_direction"):
            model.verify_bundle(bundle, copy.deepcopy(self.policy))

    def test_compatibility_requires_the_bound_kernel_checked_lock(self):
        bundle = copy.deepcopy(self.bundle)
        bundle["compatibility"] = {
            "schema": "statqed.compatibility-proof-lock.v0",
            "direction": "new_implies_old",
            "declaration": "totally.forged.and.nonexistent",
            "old_proposition_digest": bundle["proposition_digest"],
            "axioms": [],
            "path_length": 1,
        }
        bundle["compatibility_digest"] = "00" * 32
        with self.assertRaisesRegex(model.RegistryError, "registry.compatibility_missing"):
            model.verify_bundle(bundle, copy.deepcopy(self.policy))

    def test_null_compatibility_still_authenticates_verifier_selected_lock(self):
        self.assertIsNone(self.bundle["compatibility"])
        self.assertEqual(
            model.verify_bundle(copy.deepcopy(self.bundle), copy.deepcopy(self.policy))["classification"],
            "accepted",
        )
        for location, value, code in (
            ("bundle_digest_none", None, "registry.malformed_record"),
            ("bundle_digest_boolean", True, "registry.malformed_record"),
            ("bundle_digest_wrong", "00" * 32, "registry.compatibility_missing"),
            ("policy_digest_none", None, "registry.authorization_policy_unsupported"),
            ("policy_digest_wrong", "00" * 32, "registry.authorization_policy_unsupported"),
            ("policy_binding_none", None, "registry.authorization_policy_unsupported"),
            ("policy_binding_boolean", True, "registry.authorization_policy_unsupported"),
            ("policy_binding_empty", {}, "registry.authorization_policy_unsupported"),
        ):
            bundle = copy.deepcopy(self.bundle)
            policy = copy.deepcopy(self.policy)
            if location.startswith("bundle_digest"):
                bundle["compatibility_digest"] = value
            elif location.startswith("policy_digest"):
                policy["compatibility_digest"] = value
            else:
                policy["compatibility_binding"] = value
            with self.subTest(location=location), self.assertRaisesRegex(
                model.RegistryError, code,
            ):
                model.verify_bundle(bundle, policy)

        for field, value in (
            ("path_length", True),
            ("normalized_type", None),
            ("proof_subject", None),
            ("universe_instantiations", None),
            ("new_proposition", None),
        ):
            bundle = copy.deepcopy(self.bundle)
            policy = copy.deepcopy(self.policy)
            policy["compatibility_binding"][field] = value
            _, digest = model.digest_frame(
                "compatibility", model.canonical_cbor(policy["compatibility_binding"])
            )
            policy["compatibility_digest"] = digest
            bundle["compatibility_digest"] = digest
            with self.subTest(policy_binding_field=field), self.assertRaisesRegex(
                model.RegistryError, "registry.authorization_policy_unsupported"
            ):
                model.verify_bundle(bundle, policy)

        for value in (True, {}, [], "candidate-selected"):
            bundle = copy.deepcopy(self.bundle)
            bundle["compatibility"] = value
            with self.subTest(candidate=value), self.assertRaisesRegex(
                model.RegistryError, "registry.compatibility_missing"
            ):
                model.verify_bundle(bundle, copy.deepcopy(self.policy))

        bundle = copy.deepcopy(self.bundle)
        policy = copy.deepcopy(self.policy)
        bundle["compatibility_digest"] = "not-a-digest"
        policy["compatibility_digest"] = "not-a-digest"
        with self.assertRaisesRegex(model.RegistryError, "registry.malformed_record"):
            model.verify_bundle(bundle, policy)

    def test_compatibility_lock_binds_environment_axioms_and_proof(self):
        original = copy.deepcopy(self.policy["compatibility_binding"])
        for field, value in (
            ("environment_digest", "44" * 32), ("axiom_report_digest", "55" * 32),
            ("proof_build_digest", "66" * 32),
            ("normalized_type", [5, 0, [2, [[0, "True"]], []], [2, [[0, "True"]], []]]),
            ("proof_subject", [2, [[0, "True"], [0, "intro"]], []]),
        ):
            bundle = copy.deepcopy(self.bundle)
            compatibility = copy.deepcopy(original); compatibility[field] = value
            bundle["compatibility"] = compatibility
            _, bundle["compatibility_digest"] = model.digest_frame("compatibility", model.canonical_cbor(compatibility))
            with self.subTest(field=field), self.assertRaisesRegex(model.RegistryError, "registry.compatibility_missing"):
                model.verify_bundle(bundle, copy.deepcopy(self.policy))

    def test_proof_lock_substitution_rejected(self):
        bundle = copy.deepcopy(self.bundle)
        bundle["proof_build_digest"] = "00" * 32
        with self.assertRaisesRegex(model.RegistryError, "registry.proof_build_lock_mismatch"):
            model.verify_bundle(bundle, copy.deepcopy(self.policy))


if __name__ == "__main__":
    unittest.main()
