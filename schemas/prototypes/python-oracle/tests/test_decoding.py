import unittest

from statqed_oracle.oracle import (
    Integer,
    Map,
    MAX_INPUT_BYTES,
    TextString,
    decode,
)


class DecoderTests(unittest.TestCase):
    def assert_accepts(self, value_hex):
        result = decode(bytes.fromhex(value_hex))
        self.assertTrue(result.accepted, result.code)
        return result

    def assert_code(self, value_hex, expected_code):
        result = decode(bytes.fromhex(value_hex))
        self.assertFalse(result.accepted)
        self.assertEqual(result.code, expected_code)
        return result

    def test_positive_examples(self):
        for value_hex in (
            "00",
            "1818",
            "3818",
            "4200ff",
            "62c3a9",
            "6365cc81",
            "82f4f6",
            "a21864f620f6",
            "a21818f660f6",
        ):
            with self.subTest(value_hex=value_hex):
                self.assert_accepts(value_hex)

    def test_raw_map_entries_survive_before_duplicate_rejection(self):
        result = self.assert_code("a200f41800f5", "validity.map_duplicate")
        self.assertIsNotNone(result.raw)
        self.assertEqual(result.raw.kind, "map")
        self.assertEqual(len(result.raw.entries), 2)
        self.assertEqual(result.raw.entries[0].key.additional_information, 0)
        self.assertEqual(result.raw.entries[1].key.additional_information, 24)
        self.assertEqual(result.raw.entries[0].value.argument, 20)
        self.assertEqual(result.raw.entries[1].value.argument, 21)

    def test_duplicate_detection_precedes_nonpreferred_and_order(self):
        self.assert_code("a200f41800f5", "validity.map_duplicate")
        self.assert_code("a21800f500f4", "validity.map_duplicate")

    def test_nested_duplicate_is_not_collapsed(self):
        self.assert_code("81a200f400f5", "validity.map_duplicate")

    def test_core_order_and_length_first_discriminators(self):
        self.assert_code("a220f61864f6", "profile.map_order")
        self.assert_code("a260f61818f6", "profile.map_order")

    def test_nonpreferred_integer_and_length_heads(self):
        for value_hex in (
            "1800",
            "190017",
            "1a0000ffff",
            "1b00000000ffffffff",
            "3800",
            "5800",
            "590017" + "00" * 23,
            "9800",
            "b800",
        ):
            with self.subTest(value_hex=value_hex):
                self.assert_code(value_hex, "profile.non_preferred_head")

    def test_indefinite_forms_are_parsed_then_rejected(self):
        for value_hex in (
            "5f4100ff",
            "7f6161ff",
            "9f00ff",
            "bf00f6ff",
        ):
            with self.subTest(value_hex=value_hex):
                self.assert_code(value_hex, "profile.indefinite")

    def test_invalid_utf8(self):
        for value_hex in ("61ff", "62c080", "63eda080", "64f4908080"):
            with self.subTest(value_hex=value_hex):
                self.assert_code(value_hex, "validity.invalid_utf8")

    def test_valid_unicode_is_not_normalized(self):
        composed = self.assert_accepts("62c3a9").value
        decomposed = self.assert_accepts("6365cc81").value
        self.assertEqual(composed, TextString("\u00e9"))
        self.assertEqual(decomposed, TextString("e\u0301"))
        self.assertNotEqual(composed, decomposed)

    def test_all_tags_are_forbidden_after_child_parse(self):
        for value_hex in (
            "c249010000000000000000",
            "c349010000000000000000",
            "c200",
            "c4820001",
            "d81e820102",
        ):
            with self.subTest(value_hex=value_hex):
                self.assert_code(value_hex, "profile.tag_forbidden")

    def test_tag_child_fault_precedence(self):
        self.assert_code("c261ff", "validity.invalid_utf8")
        self.assert_code("c2a200f400f5", "validity.map_duplicate")
        self.assert_code("d80000", "profile.non_preferred_head")

    def test_all_float_widths_and_payloads_are_forbidden(self):
        for value_hex in (
            "f90000",
            "f98000",
            "f97c00",
            "f97e00",
            "fa3f800000",
            "fb3ff0000000000000",
        ):
            with self.subTest(value_hex=value_hex):
                self.assert_code(value_hex, "profile.float_forbidden")

    def test_undefined_and_other_simple_values_are_forbidden(self):
        for value_hex in ("e0", "f7", "f820"):
            with self.subTest(value_hex=value_hex):
                self.assert_code(value_hex, "profile.simple_forbidden")

    def test_malformed_classes(self):
        cases = {
            "": "wellformed.truncated",
            "18": "wellformed.truncated",
            "1c": "wellformed.reserved_additional",
            "ff": "wellformed.unexpected_break",
            "5f6100ff": "wellformed.indefinite_chunk_type",
            "bf00ff": "wellformed.map_pair_missing",
            "a100": "wellformed.map_pair_missing",
            "a10018": "wellformed.truncated",
        }
        for value_hex, code in cases.items():
            with self.subTest(value_hex=value_hex):
                self.assert_code(value_hex, code)

    def test_expectedness_precedes_profile(self):
        self.assert_code("a140f6", "expected.map_key_type")
        self.assertEqual(
            decode(b"\x18\x00", profile_id="wrong.profile").code,
            "expected.profile_id",
        )

    def test_top_level_and_trailing_bytes(self):
        self.assertEqual(decode(b"\x00\x01").code, "expected.trailing_bytes")
        self.assertEqual(
            decode(b"\x00", expected_top_level="map").code,
            "expected.top_level",
        )

    def test_decoded_map_keeps_semantic_entries_not_a_dictionary(self):
        result = self.assert_accepts("a21864f620f6")
        self.assertIsInstance(result.value, Map)
        self.assertEqual(result.value.entries[0][0], Integer(100))
        self.assertEqual(result.value.entries[1][0], Integer(-1))

    def test_input_limit_is_checked_before_parsing(self):
        result = decode(b"\x00" * (MAX_INPUT_BYTES + 1))
        self.assertEqual(result.code, "resource.input_bytes")


if __name__ == "__main__":
    unittest.main()
