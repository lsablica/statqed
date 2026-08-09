"""Deterministic stdin/stdout typed-JSON diagnostic CLI."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .oracle import (
    OracleError,
    Result,
    build_digest_frame,
    decode,
    encode,
    render_diagnostic,
    semantic_from_typed_json,
    verify_digest_frame,
)


# Non-normative typed-JSON transport cap. This is deliberately separate from
# the one-MiB canonical-CBOR input/output profile limits; it accommodates the
# largest reviewed typed projection without licensing unbounded stdin reads.
MAX_TYPED_JSON_INPUT_BYTES = 2_200_000


class _DuplicateJsonKey(ValueError):
    pass


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise _DuplicateJsonKey(key)
        obj[key] = value
    return obj


def _reject_constant(value: str) -> None:
    raise ValueError(value)


def _read_json() -> Any:
    raw = sys.stdin.buffer.read(MAX_TYPED_JSON_INPUT_BYTES + 1)
    if len(raw) > MAX_TYPED_JSON_INPUT_BYTES:
        raise OracleError("resource", "resource.input_bytes")
    try:
        text = raw.decode("utf-8", "strict")
        return json.loads(
            text,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise OracleError("expectedness", "expected.typed_json") from error


def _hex_field(obj: Any, name: str) -> bytes:
    if not isinstance(obj, dict) or not isinstance(obj.get(name), str):
        raise OracleError("expectedness", "expected.typed_json")
    value = obj[name]
    if len(value) % 2:
        raise OracleError("expectedness", "expected.typed_json")
    try:
        return bytes.fromhex(value)
    except ValueError as error:
        raise OracleError("expectedness", "expected.typed_json") from error


def _text_field(obj: Any, name: str, default: str | None = None) -> str:
    if not isinstance(obj, dict):
        raise OracleError("expectedness", "expected.typed_json")
    value = obj.get(name, default)
    if not isinstance(value, str):
        raise OracleError("expectedness", "expected.typed_json")
    return value


def _dispatch(command: str, obj: Any) -> Result:
    if command == "encode":
        try:
            value = semantic_from_typed_json(obj)
        except OracleError as error:
            return error.as_result()
        return encode(value)
    if command == "decode":
        try:
            data = _hex_field(obj, "cbor_hex")
            profile_id = _text_field(obj, "profile_id", "statqed.cbor-core.v1")
            expected_top_level = obj.get("expected_top_level")
            if expected_top_level is not None and not isinstance(expected_top_level, str):
                raise OracleError("expectedness", "expected.typed_json")
        except OracleError as error:
            return error.as_result()
        return decode(data, profile_id=profile_id, expected_top_level=expected_top_level)
    if command == "frame":
        try:
            return build_digest_frame(
                purpose_id=_text_field(obj, "purpose_id"),
                object_class_schema_id=_text_field(obj, "object_class_schema_id"),
                payload=_hex_field(obj, "payload_hex"),
                algorithm_id=_text_field(obj, "algorithm_id", "sha-256"),
                profile_id=_text_field(obj, "profile_id", "statqed.cbor-core.v1"),
                framing_id=_text_field(obj, "framing_id", "statqed.digest-lp.v1"),
            )
        except OracleError as error:
            return error.as_result()
    if command == "verify-digest":
        try:
            return verify_digest_frame(
                frame=_hex_field(obj, "frame_hex"),
                digest=_hex_field(obj, "digest_hex"),
                expected_purpose_id=_text_field(obj, "expected_purpose_id"),
                expected_object_class_schema_id=_text_field(
                    obj, "expected_object_class_schema_id"
                ),
                expected_algorithm_id=_text_field(
                    obj, "expected_algorithm_id", "sha-256"
                ),
                expected_profile_id=_text_field(
                    obj, "expected_profile_id", "statqed.cbor-core.v1"
                ),
                expected_framing_id=_text_field(
                    obj, "expected_framing_id", "statqed.digest-lp.v1"
                ),
            )
        except OracleError as error:
            return error.as_result()
    raise AssertionError(command)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="statqed-python-oracle")
    parser.add_argument("command", choices=("encode", "decode", "frame", "verify-digest"))
    arguments = parser.parse_args(argv)
    try:
        obj = _read_json()
        result = _dispatch(arguments.command, obj)
    except OracleError as error:
        result = error.as_result()
    sys.stdout.buffer.write(render_diagnostic(result))
    return 0 if result.accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
