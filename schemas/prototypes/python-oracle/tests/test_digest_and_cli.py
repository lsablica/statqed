import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import unittest

from statqed_oracle.cli import MAX_TYPED_JSON_INPUT_BYTES
from statqed_oracle.oracle import (
    ALGORITHM_ID,
    DIGEST_MAGIC,
    FRAMING_ID,
    MAX_DIGEST_FRAME_BYTES,
    MAX_INPUT_BYTES,
    MAX_VALID_DIGEST_FRAME_BYTES,
    PROFILE_ID,
    build_digest_frame,
    verify_digest_frame,
)


def lp(value):
    return struct.pack(">I", len(value)) + value


def manual_frame(components):
    return DIGEST_MAGIC + b"".join(lp(component) for component in components)


class DigestTests(unittest.TestCase):
    def setUp(self):
        self.purpose = "test.content"
        self.schema = "test.object.v1"
        self.payload = b"\x00"
        self.components = (
            self.purpose.encode("ascii"),
            ALGORITHM_ID.encode("ascii"),
            PROFILE_ID.encode("ascii"),
            self.schema.encode("ascii"),
            FRAMING_ID.encode("ascii"),
            self.payload,
        )
        self.frame = manual_frame(self.components)
        self.digest = hashlib.sha256(self.frame).digest()

    def verify(self, **changes):
        arguments = {
            "frame": self.frame,
            "digest": self.digest,
            "expected_purpose_id": self.purpose,
            "expected_object_class_schema_id": self.schema,
        }
        arguments.update(changes)
        return verify_digest_frame(**arguments)

    def test_exact_six_component_frame_and_digest(self):
        result = build_digest_frame(
            purpose_id=self.purpose,
            object_class_schema_id=self.schema,
            payload=self.payload,
        )
        self.assertTrue(result.accepted, result.code)
        self.assertEqual(result.frame, self.frame)
        self.assertEqual(result.digest, self.digest)
        self.assertEqual(
            result.frame.hex(),
            "537461745145442d44696765737400"
            "0000000c746573742e636f6e74656e74"
            "000000077368612d323536"
            "00000014737461747165642e63626f722d636f72652e7631"
            "0000000e746573742e6f626a6563742e7631"
            "00000014737461747165642e6469676573742d6c702e7631"
            "0000000100",
        )
        self.assertEqual(
            result.digest.hex(),
            "87fcc3cef174a2233f4f7dab7af0e56b5c9b5d6804e34727abe7901f070058ad",
        )
        self.assertTrue(self.verify().accepted)

    def test_schema_identifier_is_bound_but_not_resolved(self):
        schema_id = "test.must-be-text.v1"
        framed = build_digest_frame(
            purpose_id=self.purpose,
            object_class_schema_id=schema_id,
            payload=b"\x00",
        )
        self.assertTrue(framed.accepted, framed.code)
        verified = verify_digest_frame(
            frame=framed.frame,
            digest=framed.digest,
            expected_purpose_id=self.purpose,
            expected_object_class_schema_id=schema_id,
        )
        self.assertTrue(verified.accepted, verified.code)
        # Integer(0) is canonical profile data. This deliberately unresolvable
        # test ID receives no schema interpretation here; a schema-owning
        # caller must separately reject it if the named object requires text.
        self.assertEqual(verified.value.value, 0)

    def test_domain_substitution_is_rejected_before_digest_comparison(self):
        cases = (
            ({"expected_purpose_id": "test.other"}, "digest.purpose"),
            ({"expected_algorithm_id": "sha-512"}, "digest.algorithm"),
            ({"expected_profile_id": "statqed.cbor-core.v2"}, "digest.profile"),
            (
                {"expected_object_class_schema_id": "test.other.v1"},
                "digest.object_class_schema",
            ),
            ({"expected_framing_id": "statqed.digest-lp.v2"}, "digest.framing"),
        )
        for changes, code in cases:
            with self.subTest(code=code):
                self.assertEqual(self.verify(**changes).code, code)

    def test_no_algorithm_profile_or_framing_fallback(self):
        for index, replacement, code in (
            (1, b"sha-512", "digest.algorithm"),
            (2, b"statqed.cbor-core.v2", "digest.profile"),
            (4, b"statqed.digest-lp.v2", "digest.framing"),
        ):
            components = list(self.components)
            components[index] = replacement
            frame = manual_frame(components)
            digest = hashlib.sha256(frame).digest()
            kwargs = {
                "frame": frame,
                "digest": digest,
                "expected_purpose_id": self.purpose,
                "expected_object_class_schema_id": self.schema,
            }
            if index == 1:
                kwargs["expected_algorithm_id"] = replacement.decode()
            elif index == 2:
                kwargs["expected_profile_id"] = replacement.decode()
            else:
                kwargs["expected_framing_id"] = replacement.decode()
            self.assertEqual(verify_digest_frame(**kwargs).code, code)

    def test_frame_structure_mutations(self):
        self.assertEqual(self.verify(frame=b"X" + self.frame[1:]).code, "digest.magic")
        self.assertEqual(self.verify(frame=self.frame[:-1]).code, "digest.component_length")
        self.assertEqual(self.verify(frame=self.frame + b"\x00").code, "digest.trailing_bytes")
        bad_length = self.frame[:15] + b"\x00\x00\x00\xff" + self.frame[19:]
        self.assertEqual(self.verify(frame=bad_length).code, "digest.component_length")

    def test_digest_failure_precedence(self):
        self.assertEqual(
            self.verify(frame=b"X", digest=b"").code,
            "digest.length",
        )
        over_cap = b"\x00" * (MAX_DIGEST_FRAME_BYTES + 1)
        self.assertEqual(self.verify(frame=over_cap).code, "digest.length")

        prefix = DIGEST_MAGIC + b"".join(lp(part) for part in self.components[:5])
        oversized_payload_declaration = prefix + struct.pack(">I", MAX_INPUT_BYTES + 1)
        self.assertEqual(
            self.verify(frame=oversized_payload_declaration).code,
            "digest.length",
        )
        truncated_payload = prefix + struct.pack(">I", 2) + b"\x00"
        self.assertEqual(
            self.verify(frame=truncated_payload).code,
            "digest.component_length",
        )
        self.assertEqual(
            self.verify(frame=self.frame + b"\x00").code,
            "digest.trailing_bytes",
        )

    def test_attainable_valid_frame_and_conservative_allocation_cap(self):
        maximum_payload = (
            b"\x90"
            + (b"\x5a\x00\x01\x00\x00" + b"x" * 65_536) * 15
            + b"\x59\xff\xb1"
            + b"x" * 65_457
        )
        self.assertEqual(len(maximum_payload), MAX_INPUT_BYTES)
        identifier = "t" + "a" * 127
        result = build_digest_frame(
            purpose_id=identifier,
            object_class_schema_id=identifier,
            payload=maximum_payload,
        )
        self.assertTrue(result.accepted, result.code)
        self.assertEqual(len(result.frame), MAX_VALID_DIGEST_FRAME_BYTES)
        self.assertLess(MAX_VALID_DIGEST_FRAME_BYTES, MAX_DIGEST_FRAME_BYTES)
        one_over = result.frame + b"\x00"
        one_over_result = verify_digest_frame(
            frame=one_over,
            digest=hashlib.sha256(one_over).digest(),
            expected_purpose_id=identifier,
            expected_object_class_schema_id=identifier,
        )
        self.assertEqual(len(one_over), MAX_VALID_DIGEST_FRAME_BYTES + 1)
        self.assertEqual(one_over_result.code, "digest.trailing_bytes")

    def test_empty_components_and_payload_are_rejected(self):
        for index, code in (
            (0, "digest.purpose"),
            (1, "digest.algorithm"),
            (2, "digest.profile"),
            (3, "digest.object_class_schema"),
            (4, "digest.framing"),
            (5, "digest.payload"),
        ):
            components = list(self.components)
            components[index] = b""
            frame = manual_frame(components)
            result = verify_digest_frame(
                frame=frame,
                digest=hashlib.sha256(frame).digest(),
                expected_purpose_id=self.purpose,
                expected_object_class_schema_id=self.schema,
            )
            self.assertEqual(result.code, code)

    def test_payload_must_itself_be_strictly_accepted(self):
        components = list(self.components)
        components[5] = bytes.fromhex("1800")
        frame = manual_frame(components)
        result = verify_digest_frame(
            frame=frame,
            digest=hashlib.sha256(frame).digest(),
            expected_purpose_id=self.purpose,
            expected_object_class_schema_id=self.schema,
        )
        self.assertEqual(result.code, "digest.payload")

    def test_digest_length_and_full_comparison(self):
        self.assertEqual(self.verify(digest=self.digest[:-1]).code, "digest.length")
        mutated = bytes((self.digest[0] ^ 1,)) + self.digest[1:]
        self.assertEqual(self.verify(digest=mutated).code, "digest.mismatch")


class CliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]
        cls.environment = dict(os.environ)
        cls.environment["PYTHONPATH"] = str(cls.root)

    def run_cli(self, command, raw_input):
        completed = subprocess.run(
            [sys.executable, "-m", "statqed_oracle.cli", command],
            input=raw_input,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.environment,
            check=False,
        )
        self.assertEqual(completed.stderr, b"")
        return completed.returncode, completed.stdout, json.loads(completed.stdout)

    def test_encode_and_decode_diagnostics_are_canonical_and_stable(self):
        value = {
            "type": "map",
            "entries": [
                {
                    "key": {"type": "integer", "value": "-1"},
                    "value": {"type": "null"},
                },
                {
                    "key": {"type": "integer", "value": "100"},
                    "value": {"type": "null"},
                },
            ],
        }
        source = json.dumps(value, separators=(",", ":")).encode()
        code, first, obj = self.run_cli("encode", source)
        self.assertEqual(code, 0)
        self.assertEqual(obj["cbor_hex"], "a21864f620f6")
        self.assertNotIn(b"/tmp/", first)
        self.assertNotIn(b"timestamp", first)
        self.assertEqual(first, self.run_cli("encode", source)[1])

        code, _, decoded = self.run_cli(
            "decode", b'{"cbor_hex":"a200f41800f5"}'
        )
        self.assertEqual(code, 1)
        self.assertEqual(decoded["code"], "validity.map_duplicate")

    def test_duplicate_json_members_and_nonfinite_numbers_fail_closed(self):
        for source in (
            b'{"type":"null","type":"null"}',
            b'{"type":"integer","value":NaN}',
        ):
            with self.subTest(source=source):
                code, _, obj = self.run_cli("encode", source)
                self.assertEqual(code, 1)
                self.assertEqual(obj["code"], "expected.typed_json")

    def test_typed_json_transport_limit_on_both_sides(self):
        value = b'{"type":"null"}'
        accepted = b" " * (MAX_TYPED_JSON_INPUT_BYTES - len(value)) + value
        code, _, result = self.run_cli("encode", accepted)
        self.assertEqual(code, 0)
        self.assertEqual(result["code"], "accepted")
        rejected = b" " + accepted
        code, _, result = self.run_cli("encode", rejected)
        self.assertEqual(code, 1)
        self.assertEqual(result["code"], "resource.input_bytes")

    def test_large_decimal_never_leaks_runtime_traceback(self):
        source = json.dumps(
            {"type": "integer", "value": "9" * 5000}, separators=(",", ":")
        ).encode()
        code, _, result = self.run_cli("encode", source)
        self.assertEqual(code, 1)
        self.assertEqual(result["code"], "semantic.integer_range")


if __name__ == "__main__":
    unittest.main()
