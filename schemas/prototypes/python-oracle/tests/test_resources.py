import unittest

from statqed_oracle.oracle import (
    Array,
    ByteString,
    Integer,
    Map,
    MAX_DIAGNOSTIC_BYTES,
    NULL,
    TextString,
    decode,
    encode,
    render_diagnostic,
)


class ResourceTests(unittest.TestCase):
    def test_declared_string_limit_fails_before_truncated_body(self):
        self.assertEqual(decode(bytes.fromhex("5a00010001")).code, "resource.string_bytes")
        self.assertEqual(encode(ByteString(b"x" * 65_537)).code, "resource.string_bytes")

    def test_collection_direct_child_limits(self):
        self.assertEqual(decode(bytes.fromhex("990401")).code, "resource.array_items")
        self.assertEqual(decode(bytes.fromhex("b90401")).code, "resource.map_entries")
        self.assertEqual(
            encode(Array(Integer(index) for index in range(1_025))).code,
            "resource.array_items",
        )
        self.assertEqual(
            encode(Map((Integer(index), NULL) for index in range(1_025))).code,
            "resource.map_entries",
        )

    def test_total_item_limit(self):
        encoded = bytes.fromhex("990400") + bytes.fromhex("83000000") * 1_024
        self.assertEqual(decode(encoded).code, "resource.total_items")
        value = Array(Array((Integer(0), Integer(0), Integer(0))) for _ in range(1_024))
        self.assertEqual(encode(value).code, "resource.total_items")

    def test_structural_depth_limit_on_both_sides(self):
        accepted = NULL
        for _ in range(32):
            accepted = Array((accepted,))
        self.assertTrue(encode(accepted).accepted)
        self.assertTrue(decode(b"\x81" * 32 + b"\xf6").accepted)

        rejected = Array((accepted,))
        self.assertEqual(encode(rejected).code, "resource.depth")
        self.assertEqual(decode(b"\x81" * 33 + b"\xf6").code, "resource.depth")
        self.assertEqual(decode(b"\xc0" * 33 + b"\xf6").code, "resource.depth")

    def test_output_bytes_limit(self):
        value = Array(ByteString(b"x" * 65_536) for _ in range(16))
        self.assertEqual(encode(value).code, "resource.output_bytes")

    def test_diagnostic_has_independent_bounded_summary(self):
        result = encode(TextString("\u00e9" * 1_000))
        self.assertTrue(result.accepted)
        rendered = render_diagnostic(result)
        self.assertLessEqual(len(rendered), MAX_DIAGNOSTIC_BYTES)
        self.assertIn(b'"code":"resource.diagnostic_bytes"', rendered)
        self.assertIn(b'"validation_code":"accepted"', rendered)


if __name__ == "__main__":
    unittest.main()
