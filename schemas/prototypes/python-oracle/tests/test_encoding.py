import unittest

from statqed_oracle.oracle import (
    Array,
    Bignum,
    Boolean,
    ByteString,
    Decimal,
    Extension,
    ExtensionSequence,
    IEEEBits,
    Integer,
    Interval,
    Map,
    NULL,
    Rational,
    TextString,
    encode,
    semantic_from_typed_json,
    typed_json_from_semantic,
)


class EncoderTests(unittest.TestCase):
    def assert_encoding(self, value, expected_hex):
        result = encode(value)
        self.assertTrue(result.accepted, result.code)
        self.assertEqual(result.encoded.hex(), expected_hex)

    def assert_code(self, value, expected_code):
        result = encode(value)
        self.assertFalse(result.accepted)
        self.assertEqual(result.code, expected_code)

    def test_published_positive_examples(self):
        cases = (
            (Integer(0), "00"),
            (Integer(23), "17"),
            (Integer(24), "1818"),
            (Integer(-24), "37"),
            (Integer(-25), "3818"),
            (Integer(65536), "1a00010000"),
            (ByteString(b"\x00\xff"), "4200ff"),
            (TextString("\u00e9"), "62c3a9"),
            (TextString("e\u0301"), "6365cc81"),
            (Array((Boolean(False), NULL)), "82f4f6"),
        )
        for value, expected in cases:
            with self.subTest(value=value):
                self.assert_encoding(value, expected)

    def test_integer_width_boundaries(self):
        cases = {
            23: "17",
            24: "1818",
            255: "18ff",
            256: "190100",
            65535: "19ffff",
            65536: "1a00010000",
            4294967295: "1affffffff",
            4294967296: "1b0000000100000000",
            18446744073709551615: "1bffffffffffffffff",
            -24: "37",
            -25: "3818",
            -256: "38ff",
            -257: "390100",
            -65536: "39ffff",
            -65537: "3a00010000",
            -4294967296: "3affffffff",
            -4294967297: "3b0000000100000000",
            -18446744073709551616: "3bffffffffffffffff",
        }
        for integer, expected in cases.items():
            with self.subTest(integer=integer):
                self.assert_encoding(Integer(integer), expected)

    def test_integer_range_rejected_without_bignum_fallback(self):
        self.assert_code(Integer(1 << 64), "semantic.integer_range")
        self.assert_code(Integer(-(1 << 64) - 1), "semantic.integer_range")

    def test_string_length_heads(self):
        self.assert_encoding(ByteString(b"x" * 23), "57" + "78" * 23)
        self.assert_encoding(ByteString(b"x" * 24), "5818" + "78" * 24)
        self.assert_encoding(TextString("a" * 256), "790100" + "61" * 256)

    def test_map_is_sorted_by_complete_core_key_encoding(self):
        first = Map(((Integer(-1), NULL), (Integer(100), NULL)))
        reversed_input = Map(tuple(reversed(first.entries)))
        self.assert_encoding(first, "a21864f620f6")
        self.assert_encoding(reversed_input, "a21864f620f6")

        cross_major = Map(((TextString(""), NULL), (Integer(24), NULL)))
        self.assert_encoding(cross_major, "a21818f660f6")

    def test_typed_duplicate_keys_rejected_before_map_creation(self):
        self.assert_code(
            Map(((TextString("x"), Integer(1)), (TextString("x"), Integer(2)))),
            "semantic.map_duplicate",
        )
        self.assert_code(
            Map(((Integer(0), Integer(1)), (Integer(0), Integer(2)))),
            "semantic.map_duplicate",
        )

    def test_map_key_type_is_narrow(self):
        for key in (ByteString(b"x"), Boolean(False), NULL, Array(()), Map(())):
            with self.subTest(key=key):
                self.assert_code(Map(((key, NULL),)), "semantic.map_key_type")

    def test_unsupported_numeric_classes_are_not_coerced(self):
        cases = (
            (Bignum(1 << 64), "semantic.unsupported_bignum"),
            (Rational(1, 2), "semantic.unsupported_rational"),
            (Rational(2, 4), "semantic.rational_invalid"),
            (Rational(1, 0), "semantic.rational_invalid"),
            (Decimal(12, -1), "semantic.unsupported_decimal"),
            (Decimal(1200, -2), "semantic.decimal_non_normal"),
            (Decimal(0, 1), "semantic.decimal_non_normal"),
            (IEEEBits(64, 0x8000000000000000), "semantic.unsupported_ieee_bits"),
        )
        for value, code in cases:
            with self.subTest(value=value):
                self.assert_code(value, code)

    def test_intervals_invalid_before_unsupported(self):
        self.assert_code(
            Interval(Integer(2), Integer(1), "closed"),
            "semantic.interval_invalid",
        )
        self.assert_code(
            Interval(Integer(1), Integer(2), "closed"),
            "semantic.unsupported_interval",
        )
        self.assert_code(
            Interval(Integer(1), Rational(2, 1), "closed"),
            "semantic.interval_invalid",
        )

    def test_extension_precedence(self):
        duplicate = ExtensionSequence(
            (
                Extension("example", False, NULL),
                Extension("example", True, NULL),
            )
        )
        self.assert_code(duplicate, "semantic.extension_duplicate")
        for extensions in (
            (
                Extension("optional", False, NULL),
                Extension("critical", True, NULL),
            ),
            (
                Extension("critical", True, NULL),
                Extension("optional", False, NULL),
            ),
        ):
            with self.subTest(extensions=extensions):
                self.assert_code(
                    ExtensionSequence(extensions),
                    "semantic.extension_critical_unknown",
                )
        self.assert_code(
            ExtensionSequence(
                (
                    Extension("optional-a", False, NULL),
                    Extension("optional-b", False, NULL),
                )
            ),
            "semantic.extension_noncritical_unsupported",
        )
        self.assert_code(
            Extension("critical", True, NULL),
            "semantic.extension_critical_unknown",
        )
        self.assert_code(
            Extension("optional", False, NULL),
            "semantic.extension_noncritical_unsupported",
        )

    def test_unicode_is_preserved_without_normalization(self):
        composed = encode(TextString("\u00e9"))
        decomposed = encode(TextString("e\u0301"))
        self.assertNotEqual(composed.encoded, decomposed.encoded)
        self.assert_encoding(TextString("\u0000\ufdd0"), "6400efb790")

    def test_typed_json_uses_decimal_strings_and_entry_sequences(self):
        source = {
            "type": "map",
            "entries": [
                {
                    "key": {"type": "text", "value": "x"},
                    "value": {
                        "type": "integer",
                        "value": "18446744073709551615",
                    },
                }
            ],
        }
        value = semantic_from_typed_json(source)
        self.assertEqual(typed_json_from_semantic(value), source)

    def test_typed_json_rejects_host_number_for_integer(self):
        with self.assertRaisesRegex(Exception, "semantic.unsupported_value"):
            semantic_from_typed_json({"type": "integer", "value": 1})


if __name__ == "__main__":
    unittest.main()
