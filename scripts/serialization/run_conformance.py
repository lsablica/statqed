#!/usr/bin/env python3
"""Run SQ-0005 semantic-first serialization conformance.

The standard-library harness treats the committed semantic-v1 catalogue as
the reviewed expectation.  Implementations are observations, never an oracle
for changing that catalogue.  Generated goldens are retained only when both
independent implementations agree with an accepted semantic expectation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import resource
import shutil
import struct
import subprocess
import sys
import tempfile
from typing import Any, Callable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "conformance/prototypes/fixtures/semantic-v1"
GENERATED_ROOT = ROOT / "conformance/prototypes/generated-v1"
GOLDEN_ROOT = ROOT / "conformance/prototypes/golden/serialization-v1"
CDDL_PATH = ROOT / "schemas/prototypes/cddl/profile-v1.cddl"
PYTHON_ORACLE_ROOT = ROOT / "schemas/prototypes/python-oracle"
RUST_ROOT = ROOT / "schemas/prototypes/rust-cbor"

EXPECTED_CASE_COUNT = 273
PROFILE_ID = "statqed.cbor-core.v1"
SCHEMA_ID = "test.semantic-value"
SCHEMA_VERSION = 1
FRAME_MAGIC = b"StatQED-Digest\x00"
ALGORITHM_ID = "sha-256"
FRAMING_ID = "statqed.digest-lp.v1"
BASE_PURPOSE_ID = "test.fixture"
BASE_OBJECT_SCHEMA_ID = "test.semantic-value.v1"
FIXTURE_TIMEOUT_SECONDS = 5
PROCESS_MEMORY_BYTES = 128 * 1024 * 1024
INLINE_ARTIFACT_LIMIT = 4096

# Reviewed implementation snapshots used for the final differential run.  The
# content hashes below remain authoritative if these commits are later
# unavailable; the commit identifiers make the review lineage explicit.
SEMANTIC_FIXTURE_FROZEN_COMMIT = "b2ec69de45a3406cdcf29aec3243f81e8a42432f"
PYTHON_ORACLE_FROZEN_COMMIT = "14f1ffb0646b280fea805fbec6ba6bb8b3d1a282"
RUST_PROTOTYPE_COMMIT = "2f0d778fff38bedd512dadd8603fc59e38be75b4"
RUST_DEPENDENCY_EVIDENCE_COMMIT = "31a1a773f149248703db8b26930d0a3b4025a099"
RUST_ADVERSARIAL_FIX_COMMIT = "81aa7909591617589150bc9756ce904ac5fd5f20"
RUST_TRANSPORT_FIX_COMMIT = "4809224d2b06a10dc212865c8e1b667d3fe3e34a"
RUST_FROZEN_TREE_COMMIT = "14f1ffb0646b280fea805fbec6ba6bb8b3d1a282"

PYTHON_FULL_RESULT_HELPER = """
import json
import sys
from statqed_oracle.cli import _dispatch
from statqed_oracle.oracle import diagnostic_object

request = json.load(sys.stdin)
result = _dispatch(request["command"], request["input"])
json.dump(diagnostic_object(result), sys.stdout, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
sys.stdout.write("\\n")
raise SystemExit(0 if result.accepted else 1)
"""

REQUIRED_CASE_FIELDS = {
    "id",
    "input_layer",
    "input",
    "intended_class",
    "accept",
    "stable_code",
    "expected_encoding",
    "source_refs",
    "rationale",
    "purpose",
}


class ConformanceError(RuntimeError):
    """Fail-closed harness configuration or fixture error."""


def canonical_json_bytes(value: Any) -> bytes:
    """Return stable generated JSON with a terminal newline."""

    return (
        json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def compact_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
        + "\n"
    ).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ConformanceError(f"cannot parse {path.relative_to(ROOT)}: {error}") from error


def valid_hex(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) % 2 == 0
        and re.fullmatch(r"[0-9a-f]*", value) is not None
    )


def walk_hex_fields(value: Any, location: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            is_hex = key == "hex" or key.endswith("_hex") or key in {
                "literal_hex",
                "append_hex",
                "suffix_hex",
                "from_hex",
                "to_hex",
                "mutant_output_hex",
                "reviewed_expected_hex",
                "payload_hex",
                "hashed_hex",
            }
            if is_hex and isinstance(child, str) and not valid_hex(child):
                errors.append(f"{location}.{key}: not lowercase even-length hex")
            walk_hex_fields(child, f"{location}.{key}", errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            walk_hex_fields(child, f"{location}[{index}]", errors)


def load_and_validate_fixtures() -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, dict[str, Any]]]:
    catalog = read_json(FIXTURE_ROOT / "catalog.json")
    errors: list[str] = []
    if catalog.get("catalog_id") != "statqed.sq0005.semantic-corpus.v1":
        errors.append("catalog_id changed")
    if catalog.get("profile_id") != PROFILE_ID or catalog.get("profile_version") != 1:
        errors.append("catalog profile identity changed")
    if catalog.get("test_object_schema_id") != SCHEMA_ID:
        errors.append("catalog schema identity changed")
    if catalog.get("test_object_schema_version") != SCHEMA_VERSION:
        errors.append("catalog schema version changed")
    if catalog.get("unresolved") != []:
        errors.append("catalog contains unresolved semantic decisions")

    components = catalog.get("components")
    if not isinstance(components, list) or not all(isinstance(item, str) for item in components):
        errors.append("catalog components must be a string list")
        components = []
    expected_files = {"catalog.json", *components}
    actual_files = {path.name for path in FIXTURE_ROOT.glob("*.json")}
    if expected_files != actual_files:
        errors.append(
            f"catalog component set differs: expected={sorted(expected_files)} actual={sorted(actual_files)}"
        )

    allowed_classes = set(catalog.get("result_classes", []))
    allowed_kinds = set(catalog.get("encoding_expectation_kinds", {}))
    allowed_sources = set(catalog.get("source_index", {}))
    cases: list[dict[str, Any]] = []
    by_id: dict[str, dict[str, Any]] = {}
    reference_fields = {
        "base_case",
        "semantic_fixture",
        "raw_fixture",
        "frame_fixture",
        "digest_fixture",
        "case_payload",
    }
    deferred_refs: list[tuple[str, str, str]] = []

    for component in components:
        path = FIXTURE_ROOT / component
        document = read_json(path)
        if document.get("fixture_schema_version") != 1:
            errors.append(f"{component}: fixture_schema_version must be 1")
        if document.get("profile_id") != PROFILE_ID or document.get("profile_version") != 1:
            errors.append(f"{component}: profile identity mismatch")
        if document.get("test_object_schema_id") != SCHEMA_ID:
            errors.append(f"{component}: schema identity mismatch")
        if document.get("test_object_schema_version") != SCHEMA_VERSION:
            errors.append(f"{component}: schema version mismatch")
        component_cases = document.get("cases")
        if not isinstance(component_cases, list):
            errors.append(f"{component}: cases must be a list")
            continue
        for index, case in enumerate(component_cases):
            location = f"{component}:cases[{index}]"
            if not isinstance(case, dict):
                errors.append(f"{location}: case must be an object")
                continue
            missing = REQUIRED_CASE_FIELDS - set(case)
            if missing:
                errors.append(f"{location}: missing {sorted(missing)}")
                continue
            identifier = case["id"]
            if not isinstance(identifier, str) or not re.fullmatch(r"[A-Z0-9-]+", identifier):
                errors.append(f"{location}: invalid stable case id")
                continue
            if identifier in by_id:
                errors.append(f"{location}: duplicate id {identifier}")
            by_id[identifier] = case
            cases.append(case)
            if type(case["accept"]) is not bool:
                errors.append(f"{identifier}: accept must be boolean")
            if case["accept"] != (case["stable_code"] == "accepted"):
                errors.append(f"{identifier}: accept/code inconsistency")
            if case["intended_class"] not in allowed_classes:
                errors.append(f"{identifier}: unknown class {case['intended_class']}")
            expectation = case["expected_encoding"]
            if not isinstance(expectation, dict) or expectation.get("kind") not in allowed_kinds:
                errors.append(f"{identifier}: unknown expected_encoding kind")
            if set(case["source_refs"]) - allowed_sources:
                errors.append(f"{identifier}: unknown source reference")
            if (
                case["accept"]
                and case["input_layer"] not in {"diagnostic_recipe", "harness_recipe"}
                and expectation.get("kind") == "none"
            ):
                errors.append(f"{identifier}: accepted profile input lacks expected bytes")
            walk_hex_fields(case["input"], f"{identifier}.input", errors)
            walk_hex_fields(expectation, f"{identifier}.expected_encoding", errors)

            def collect_refs(value: Any) -> None:
                if isinstance(value, dict):
                    for key, child in value.items():
                        if key in reference_fields and isinstance(child, str):
                            deferred_refs.append((identifier, key, child))
                        collect_refs(child)
                elif isinstance(value, list):
                    for child in value:
                        collect_refs(child)

            collect_refs(case)

    if len(cases) != EXPECTED_CASE_COUNT:
        errors.append(f"expected {EXPECTED_CASE_COUNT} cases, found {len(cases)}")
    for owner, field, target in deferred_refs:
        if target not in by_id:
            errors.append(f"{owner}: unresolved {field}={target}")
    if errors:
        raise ConformanceError("fixture validation failed:\n- " + "\n- ".join(errors))
    return catalog, cases, by_id


def validate_cddl_source() -> dict[str, str]:
    """Validate and load the deliberately tiny published-syntax CDDL subset."""

    try:
        source = CDDL_PATH.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise ConformanceError(f"cannot read CDDL source: {error}") from error
    logical: list[str] = []
    syntax_lines: list[str] = []
    for raw_line in source.splitlines():
        line = raw_line.split(";", 1)[0].strip()
        if not line:
            continue
        syntax_lines.append(line)
        if "=" in line:
            logical.append(line)
        elif logical:
            logical[-1] += " " + line
        else:
            raise ConformanceError("CDDL continuation appears before a rule")
    syntax = " ".join(syntax_lines).lower()
    forbidden = ("import", "module", "$$", ".cbor", ".within", "#6.", "float", " any")
    for token in forbidden:
        if token in syntax:
            raise ConformanceError(f"CDDL source uses excluded token {token!r}")
    rules: dict[str, str] = {}
    for line in logical:
        name, expression = line.split("=", 1)
        name = name.strip()
        if not re.fullmatch(r"[a-z][a-z0-9-]*", name) or name in rules:
            raise ConformanceError(f"invalid or duplicate CDDL rule {name!r}")
        rules[name] = re.sub(r"\s+", "", expression)
    expected = {
        "statqed-value": "statqed-integer/bstr/tstr/statqed-array/statqed-map/bool/nil",
        "statqed-integer": "int",
        "statqed-array": "[*statqed-value]",
        "statqed-map": "{*statqed-key=>statqed-value}",
        "statqed-key": "int/tstr",
    }
    if rules != expected:
        raise ConformanceError(f"CDDL restricted profile changed: {rules!r}")
    return rules


def codepoint(token: str) -> str:
    if not re.fullmatch(r"U\+[0-9A-F]{4,6}", token):
        raise ConformanceError(f"invalid Unicode scalar token {token!r}")
    value = int(token[2:], 16)
    if value > 0x10FFFF or 0xD800 <= value <= 0xDFFF:
        raise ConformanceError(f"non-scalar Unicode token {token!r}")
    return chr(value)


def semantic_to_typed(value: Mapping[str, Any]) -> dict[str, Any]:
    """Expand the reviewed fixture DSL into the CLIs' typed JSON projection."""

    kind = value.get("kind")
    if kind == "integer":
        return {"type": "integer", "value": value["decimal"]}
    if kind == "byte_string":
        return {"type": "bytes", "hex": value["hex"]}
    if kind == "byte_string_recipe":
        unit = bytes.fromhex(value["byte_hex"])
        return {"type": "bytes", "hex": (unit * value["repeat"]).hex()}
    if kind == "text":
        if "unicode_scalars" in value:
            text = "".join(codepoint(item) for item in value["unicode_scalars"])
        else:
            text = value["value"]
        return {"type": "text", "value": text}
    if kind == "text_recipe":
        return {"type": "text", "value": codepoint(value["unicode_scalar"]) * value["repeat"]}
    if kind == "boolean":
        return {"type": "boolean", "value": value["value"]}
    if kind == "null":
        return {"type": "null"}
    if kind == "array":
        items: list[dict[str, Any]] = []
        for item in value["items"]:
            if "repeat_item" in item:
                expanded = semantic_to_typed(item["repeat_item"])
                items.extend(expanded for _ in range(item["count"]))
            else:
                items.append(semantic_to_typed(item))
        return {"type": "array", "items": items}
    if kind == "array_recipe":
        item = semantic_to_typed(value["item"])
        return {"type": "array", "items": [item for _ in range(value["repeat"])]}
    if kind == "nested_singleton_array":
        result = semantic_to_typed(value["leaf"])
        for _ in range(value["wrappers"]):
            result = {"type": "array", "items": [result]}
        return result
    if kind in {"map", "map_entry_sequence"}:
        return {
            "type": "map",
            "entries": [
                {
                    "key": semantic_to_typed(entry["key"]),
                    "value": semantic_to_typed(entry["value"]),
                }
                for entry in value["entries"]
            ],
        }
    if kind == "map_recipe":
        unique = value["unique_keys"]
        if unique.get("kind") != "integer_range":
            raise ConformanceError("unsupported map recipe key generator")
        start = unique["start"]
        map_value = semantic_to_typed(value["value"])
        return {
            "type": "map",
            "entries": [
                {
                    "key": {"type": "integer", "value": str(start + index)},
                    "value": map_value,
                }
                for index in range(value["entries"])
            ],
        }
    if kind == "bignum":
        return {"type": "bignum", "value": value["decimal"]}
    if kind == "rational":
        return {
            "type": "rational",
            "numerator": value["numerator"],
            "denominator": value["denominator"],
        }
    if kind == "decimal":
        return {
            "type": "decimal",
            "coefficient": value["coefficient"],
            "exponent": value["exponent"],
        }
    if kind == "ieee_bits":
        return {"type": "ieee_bits", "width": value["width"], "bits_hex": value["bits_hex"]}
    if kind == "interval":
        if value.get("endpoint_kind") == "integer":
            lower = {"type": "integer", "value": value["lower"]}
            upper = {"type": "integer", "value": value["upper"]}
        else:
            lower = semantic_to_typed(value["lower"])
            upper = semantic_to_typed(value["upper"])
        return {"type": "interval", "lower": lower, "upper": upper, "closure": value["closure"]}
    if kind == "extension":
        return {
            "type": "extension",
            "type_id": value["type_id"],
            "critical": value["critical"],
            "body": semantic_to_typed(value["body"]),
        }
    if kind == "extension_sequence":
        return {
            "type": "extension_sequence",
            "extensions": [
                semantic_to_typed({"kind": "extension", **extension})
                for extension in value["extensions"]
            ],
        }
    if kind == "object_with_extensions":
        if not value["extensions"]:
            return semantic_to_typed(value["base"])
        return semantic_to_typed({"kind": "extension_sequence", "extensions": value["extensions"]})
    raise ConformanceError(f"unsupported semantic fixture kind {kind!r}")


def encode_argument(major: int, argument: int) -> bytes:
    if argument < 24:
        return bytes([(major << 5) | argument])
    if argument <= 0xFF:
        return bytes([(major << 5) | 24, argument])
    if argument <= 0xFFFF:
        return bytes([(major << 5) | 25]) + argument.to_bytes(2, "big")
    if argument <= 0xFFFF_FFFF:
        return bytes([(major << 5) | 26]) + argument.to_bytes(4, "big")
    if argument <= 0xFFFF_FFFF_FFFF_FFFF:
        return bytes([(major << 5) | 27]) + argument.to_bytes(8, "big")
    raise ConformanceError("integer recipe outside direct CBOR range")


def encode_integer(value: int) -> bytes:
    if value >= 0:
        return encode_argument(0, value)
    return encode_argument(1, -1 - value)


def expand_hex_parts(parts: Sequence[Mapping[str, Any]], by_id: Mapping[str, dict[str, Any]]) -> bytes:
    output = bytearray()
    for part in parts:
        if "literal_hex" in part:
            output.extend(bytes.fromhex(part["literal_hex"]))
        elif "repeat_hex" in part:
            output.extend(bytes.fromhex(part["repeat_hex"]) * part["count"])
        elif "repeat_group" in part:
            group = expand_hex_parts(part["repeat_group"]["parts"], by_id)
            output.extend(group * part["count"])
        elif "map_entries" in part:
            match = re.fullmatch(r"Integer\((-?[0-9]+)\.\.(-?[0-9]+)\)", part["key_recipe"])
            if match is None:
                raise ConformanceError(f"unsupported map key recipe {part['key_recipe']!r}")
            start, end = (int(item) for item in match.groups())
            if end - start + 1 != part["map_entries"]:
                raise ConformanceError("map recipe count mismatch")
            entries = [(encode_integer(key), bytes.fromhex(part["value_hex"])) for key in range(start, end + 1)]
            entries.sort(key=lambda entry: entry[0])
            for key, map_value in entries:
                output.extend(key)
                output.extend(map_value)
        elif "u32be_length" in part:
            output.extend(struct.pack(">I", part["u32be_length"]))
        elif "literal_ascii" in part:
            output.extend(part["literal_ascii"].encode("ascii"))
        elif "repeat_ascii" in part:
            encoded = part["repeat_ascii"].encode("ascii")
            output.extend(encoded * part["count"])
        elif "case_payload" in part:
            target = by_id[part["case_payload"]]
            payload = expected_bytes(target, by_id)
            if payload is None:
                raise ConformanceError(f"case payload {target['id']} lacks expected bytes")
            output.extend(payload)
        else:
            raise ConformanceError(f"unsupported hex recipe part {part!r}")
    return bytes(output)


def raw_cbor_bytes(case: Mapping[str, Any], by_id: Mapping[str, dict[str, Any]]) -> bytes:
    value = case["input"]
    kind = value.get("kind")
    if kind == "literal_hex":
        return bytes.fromhex(value["hex"])
    if kind == "hex_recipe":
        result = expand_hex_parts(value["parts"], by_id)
    elif kind == "append_hex":
        result = raw_cbor_bytes(by_id[value["base_case"]], by_id) + bytes.fromhex(value["suffix_hex"])
    else:
        raise ConformanceError(f"unsupported raw CBOR recipe {case['id']}: {kind!r}")
    if "derived_byte_length" in value and len(result) != value["derived_byte_length"]:
        raise ConformanceError(f"{case['id']}: raw recipe derived length mismatch")
    return result


def typed_json_bytes(case: Mapping[str, Any]) -> bytes:
    """Expand reviewed producer-transport recipes without host JSON coercion."""

    value = case["input"]
    kind = value.get("kind")
    if kind == "nested_array_typed_json":
        wrappers = value["wrappers"]
        result = (
            b'{"type":"array","items":[' * wrappers
            + b'{"type":"null"}'
            + b"]}" * wrappers
        )
    elif kind == "decimal_interval_typed_json":
        coefficient = value["coefficient"]
        exponent = value["exponent"]
        closure = value["closure"]
        if not re.fullmatch(r"-?(0|[1-9][0-9]*)", coefficient):
            raise ConformanceError(f"{case['id']}: invalid decimal coefficient recipe")
        if not re.fullmatch(r"-?(0|[1-9][0-9]*)", exponent):
            raise ConformanceError(f"{case['id']}: invalid decimal exponent recipe")
        if closure not in {"closed", "open", "left_closed", "right_closed"}:
            raise ConformanceError(f"{case['id']}: invalid interval closure recipe")
        result = compact_json_bytes(
            {
                "type": "interval",
                "lower": {"type": "decimal", "coefficient": coefficient, "exponent": exponent},
                "upper": {"type": "decimal", "coefficient": coefficient, "exponent": exponent},
                "closure": closure,
            }
        ).removesuffix(b"\n")
    elif kind == "unquoted_integer_typed_json":
        digit = value["digit"]
        repeat = value["repeat"]
        if not isinstance(digit, str) or not re.fullmatch(r"[1-9]", digit):
            raise ConformanceError(f"{case['id']}: invalid unquoted integer digit recipe")
        result = b'{"type":"integer","value":' + digit.encode("ascii") * repeat + b"}"
    else:
        raise ConformanceError(f"unsupported typed-JSON recipe {case['id']}: {kind!r}")
    if len(result) != value["derived_byte_length"]:
        raise ConformanceError(f"{case['id']}: typed-JSON recipe derived length mismatch")
    return result


def expected_bytes(case: Mapping[str, Any], by_id: Mapping[str, dict[str, Any]]) -> bytes | None:
    expectation = case["expected_encoding"]
    kind = expectation["kind"]
    if kind == "none":
        return None
    if kind == "literal_hex":
        result = bytes.fromhex(expectation["hex"])
    elif kind == "hex_recipe":
        result = expand_hex_parts(expectation["parts"], by_id)
    elif kind == "same_as_input_recipe":
        result = raw_cbor_bytes(case, by_id)
    else:
        raise ConformanceError(f"{case['id']}: unsupported expectation kind {kind}")
    declared = expectation.get("derived_byte_length", expectation.get("byte_length"))
    if declared is not None and len(result) != declared:
        raise ConformanceError(f"{case['id']}: expected recipe derived length mismatch")
    return result


def typed_key_bytes(value: Mapping[str, Any]) -> bytes:
    if value.get("type") == "integer":
        return encode_integer(int(value["value"]))
    if value.get("type") == "text":
        encoded = value["value"].encode("utf-8")
        return encode_argument(3, len(encoded)) + encoded
    raise ConformanceError("typed projection contains forbidden map key")


def canonicalize_typed(value: Any) -> Any:
    if not isinstance(value, dict):
        return value
    kind = value.get("type")
    if kind == "array":
        return {"type": "array", "items": [canonicalize_typed(item) for item in value["items"]]}
    if kind == "map":
        entries = [
            {"key": canonicalize_typed(entry["key"]), "value": canonicalize_typed(entry["value"])}
            for entry in value["entries"]
        ]
        entries.sort(key=lambda entry: typed_key_bytes(entry["key"]))
        return {"type": "map", "entries": entries}
    return {key: canonicalize_typed(child) for key, child in value.items()}


def cddl_matches_typed(value: Mapping[str, Any]) -> bool:
    kind = value.get("type")
    if kind in {"integer", "bytes", "text", "boolean", "null"}:
        return True
    if kind == "array":
        return all(cddl_matches_typed(item) for item in value.get("items", []))
    if kind == "map":
        return all(
            entry.get("key", {}).get("type") in {"integer", "text"}
            and cddl_matches_typed(entry.get("value", {}))
            for entry in value.get("entries", [])
        )
    return False


def identifier_recipe(value: Any) -> str:
    if isinstance(value, str):
        return value
    if not isinstance(value, dict):
        raise ConformanceError("identifier recipe must be text or object")
    if "ascii_prefix" in value:
        result = value["ascii_prefix"] + value["repeat_ascii"] * value["repeat"]
    elif "prefix" in value:
        result = value["prefix"] + value["repeat_ascii"] * value["repeat"]
    else:
        raise ConformanceError(f"unsupported identifier recipe {value!r}")
    if len(result.encode("ascii")) != value["derived_bytes"]:
        raise ConformanceError("identifier recipe derived length mismatch")
    return result


def lp(value: bytes) -> bytes:
    return struct.pack(">I", len(value)) + value


def frame_components(
    purpose: str,
    algorithm: str,
    profile: str,
    schema: str,
    framing: str,
    payload: bytes,
) -> bytes:
    components = [
        purpose.encode("ascii"),
        algorithm.encode("ascii"),
        profile.encode("ascii"),
        schema.encode("ascii"),
        framing.encode("ascii"),
        payload,
    ]
    return FRAME_MAGIC + b"".join(lp(component) for component in components)


def base_digest_components(by_id: Mapping[str, dict[str, Any]]) -> tuple[list[bytes], bytes]:
    baseline = read_json(FIXTURE_ROOT / "digest-framing.json")["baseline"]
    components = [
        baseline["purpose_id"].encode("ascii"),
        baseline["algorithm_id"].encode("ascii"),
        baseline["profile_id"].encode("ascii"),
        baseline["object_class_schema_id"].encode("ascii"),
        baseline["framing_id"].encode("ascii"),
        bytes.fromhex(baseline["payload_hex"]),
    ]
    frame = FRAME_MAGIC + b"".join(lp(component) for component in components)
    if frame.hex() != baseline["frame_hex"] or len(frame) != baseline["frame_byte_length"]:
        raise ConformanceError("digest baseline manual derivation is inconsistent")
    return components, frame


def digest_material(case: Mapping[str, Any], by_id: Mapping[str, dict[str, Any]]) -> dict[str, Any]:
    """Expand a digest fixture into either a construction or verification request."""

    components, baseline = base_digest_components(by_id)
    data = case["input"]
    identifier_names = {
        "purpose_id": 0,
        "algorithm_id": 1,
        "profile_id": 2,
        "object_class_schema_id": 3,
        "framing_id": 4,
        "payload": 5,
    }
    expected = {
        "purpose_id": BASE_PURPOSE_ID,
        "algorithm_id": ALGORITHM_ID,
        "profile_id": PROFILE_ID,
        "object_class_schema_id": BASE_OBJECT_SCHEMA_ID,
        "framing_id": FRAMING_ID,
    }

    if case["input_layer"] == "digest_frame_components":
        if case["id"] == "DIGEST-FRAME-BASELINE":
            return {"operation": "frame", **expected, "payload": components[5]}
        return {
            "operation": "frame",
            "purpose_id": data["purpose_id"],
            "algorithm_id": data["algorithm_id"],
            "profile_id": data["profile_id"],
            "object_class_schema_id": data["object_class_schema_id"],
            "framing_id": data["framing_id"],
            "payload": bytes.fromhex(data["payload_hex"]),
        }
    if case["id"] == "DIGEST-FRAME-ATTAINABLE-MAX":
        payload = expected_bytes(by_id["RESOURCE-INPUT-BYTES-1048576"], by_id)
        assert payload is not None
        return {
            "operation": "frame",
            "purpose_id": identifier_recipe(data["purpose_id"]),
            "algorithm_id": data["algorithm_id"],
            "profile_id": data["profile_id"],
            "object_class_schema_id": identifier_recipe(data["object_class_schema_id"]),
            "framing_id": data["framing_id"],
            "payload": payload,
        }
    if case["id"] in {"DIGEST-PURPOSE-BYTES-129", "DIGEST-SCHEMA-BYTES-129"}:
        replacement = data["replace_component"]
        expected[replacement["name"]] = identifier_recipe(replacement["ascii_recipe"])
        return {"operation": "frame", **expected, "payload": components[5]}
    if case["id"] == "DIGEST-FRAME-PAYLOAD-ONE-OVER":
        return {"operation": "frame", **expected, "payload": b"\x00" * data["mutate"]["payload_bytes"]}

    frame = baseline
    supplied_digest = hashlib.sha256(frame).digest()
    if case["id"] == "DIGEST-FRAME-ALLOCATION-CAP-PLUS1":
        frame = baseline + b"\x00" * (data["total_bytes"] - len(baseline))
    elif case["id"] in {
        "DIGEST-RAW-PURPOSE-BYTES-129",
        "DIGEST-RAW-SCHEMA-BYTES-129",
    }:
        replacement = data["replace_component"]
        changed = list(components)
        changed[identifier_names[replacement["name"]]] = identifier_recipe(
            replacement["ascii_recipe"]
        ).encode("ascii")
        frame = FRAME_MAGIC + b"".join(lp(component) for component in changed)
    elif case["input_layer"] == "raw_digest_frame":
        frame = bytes.fromhex(data["hex"])
    elif case["id"] == "DIGEST-MAGIC-BITFLIP":
        offset = data["mutate"]["byte_offset"]
        frame = baseline[:offset] + bytes.fromhex(data["mutate"]["to_hex"]) + baseline[offset + 1 :]
    elif case["id"] == "DIGEST-COMPONENT-DECLARED-LONG":
        frame = FRAME_MAGIC + struct.pack(">I", data["mutate"]["declared_length"]) + components[0]
    elif case["id"] == "DIGEST-COMPONENT-DELETE":
        kept = [component for index, component in enumerate(components) if index != identifier_names[data["component"]]]
        frame = FRAME_MAGIC + b"".join(lp(component) for component in kept)
    elif case["id"] == "DIGEST-COMPONENT-REORDER":
        changed = list(components)
        left, right = identifier_names[data["left"]], identifier_names[data["right"]]
        changed[left], changed[right] = changed[right], changed[left]
        frame = FRAME_MAGIC + b"".join(lp(component) for component in changed)
    elif case["id"] == "DIGEST-COMPONENT-DUPLICATE":
        duplicate = components[identifier_names[data["duplicate"]]]
        before = identifier_names[data["before"]]
        changed = components[:before] + [duplicate] + components[before:]
        del changed[identifier_names[data["dropped"]] + 1]
        frame = FRAME_MAGIC + b"".join(lp(component) for component in changed)
    elif case["id"] == "DIGEST-COMPONENT-APPEND":
        frame = baseline + lp(data["ascii"].encode("ascii"))
    elif case["id"] == "DIGEST-FRAME-COMPLETE-TRAILING-BYTE":
        frame = baseline + bytes.fromhex(data["append_hex"])
    elif case["input_layer"] == "digest_frame_mutation" and "replace_component" in data:
        replacement = data["replace_component"]
        changed = list(components)
        if "ascii" in replacement:
            changed[identifier_names[replacement["name"]]] = replacement["ascii"].encode("ascii")
        else:
            changed[identifier_names[replacement["name"]]] = bytes.fromhex(replacement["hex"])
        frame = FRAME_MAGIC + b"".join(lp(component) for component in changed)
    elif case["id"] == "DIGEST-PAYLOAD-SPLIT":
        parts = [bytes.fromhex(item) for item in data["payload_parts_hex"]]
        frame = FRAME_MAGIC + b"".join(lp(component) for component in components[:5] + parts)
    elif case["id"] == "DIGEST-PURPOSE-REPLAY":
        expected["purpose_id"] = data["caller_expected_purpose_id"]
    elif case["id"] == "DIGEST-ALGORITHM-SUBSTITUTE-NO-FALLBACK":
        changed = list(components)
        changed[1] = data["replace_component"]["ascii"].encode("ascii")
        frame = FRAME_MAGIC + b"".join(lp(component) for component in changed)
    elif case["id"] in {"DIGEST-SUPPLIED-LENGTH-31", "DIGEST-SUPPLIED-LENGTH-33", "DIGEST-MISMATCH-32"}:
        digest_spec = data["supplied_digest"]
        supplied_digest = bytes.fromhex(digest_spec["hex_recipe"]["repeat_hex"]) * digest_spec["hex_recipe"]["count"]
    elif case["id"] == "DIGEST-COMPONENT-PREFIX-TRUNCATED":
        pass
    else:
        raise ConformanceError(f"unsupported digest fixture {case['id']}")

    if case["id"] not in {"DIGEST-SUPPLIED-LENGTH-31", "DIGEST-SUPPLIED-LENGTH-33", "DIGEST-MISMATCH-32", "DIGEST-PURPOSE-REPLAY"}:
        supplied_digest = hashlib.sha256(frame).digest()
    return {"operation": "verify", **expected, "frame": frame, "digest": supplied_digest}


def linux_limits() -> Callable[[], None] | None:
    if platform.system() != "Linux":
        return None

    def apply() -> None:
        resource.setrlimit(resource.RLIMIT_AS, (PROCESS_MEMORY_BYTES, PROCESS_MEMORY_BYTES))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

    return apply


def invoke_process(command: Sequence[str], stdin: bytes, *, cwd: Path, env: Mapping[str, str]) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            list(command),
            input=stdin,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
            env=dict(env),
            check=False,
            timeout=FIXTURE_TIMEOUT_SECONDS,
            preexec_fn=linux_limits(),
        )
    except subprocess.TimeoutExpired:
        return {"outcome": "operational", "result_class": "operational_failure", "code": "operational.timeout"}
    except OSError:
        return {"outcome": "operational", "result_class": "operational_failure", "code": "operational.exception"}
    if completed.returncode < 0:
        return {
            "outcome": "operational",
            "result_class": "operational_failure",
            "code": "operational.crash",
            "signal": -completed.returncode,
        }
    try:
        diagnostic = json.loads(completed.stdout.decode("utf-8", "strict"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {
            "outcome": "operational",
            "result_class": "operational_failure",
            "code": "operational.exception",
            "returncode": completed.returncode,
            "stdout_bytes": len(completed.stdout),
            "stdout_sha256": sha256_hex(completed.stdout),
            "stderr_present": bool(completed.stderr),
        }
    if not isinstance(diagnostic, dict):
        return {"outcome": "operational", "result_class": "operational_failure", "code": "operational.exception"}
    return {
        "outcome": "diagnostic",
        "returncode": completed.returncode,
        "diagnostic": diagnostic,
        "stderr_present": bool(completed.stderr),
    }


def invoke_evidence_process(
    command: Sequence[str], stdin: bytes, *, cwd: Path, env: Mapping[str, str]
) -> dict[str, Any]:
    """Invoke a test-only raw evidence channel whose successful stdout is not JSON."""

    try:
        completed = subprocess.run(
            list(command),
            input=stdin,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
            env=dict(env),
            check=False,
            timeout=FIXTURE_TIMEOUT_SECONDS,
            preexec_fn=linux_limits(),
        )
    except subprocess.TimeoutExpired:
        return {"outcome": "operational", "result_class": "operational_failure", "code": "operational.timeout"}
    except OSError:
        return {"outcome": "operational", "result_class": "operational_failure", "code": "operational.exception"}
    if completed.returncode == 0:
        return {
            "outcome": "evidence",
            "bytes": completed.stdout,
            "stderr_present": bool(completed.stderr),
        }
    if completed.returncode < 0:
        return {"outcome": "operational", "result_class": "operational_failure", "code": "operational.crash"}
    try:
        diagnostic = json.loads(completed.stdout.decode("utf-8", "strict"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {"outcome": "operational", "result_class": "operational_failure", "code": "operational.exception"}
    return normalize_observation(
        {
            "outcome": "diagnostic",
            "returncode": completed.returncode,
            "diagnostic": diagnostic,
            "stderr_present": bool(completed.stderr),
        }
    )


def summarize_artifact(value: Any, *, hex_value: bool = False) -> dict[str, Any] | None:
    if not isinstance(value, str):
        return None
    if hex_value:
        if not valid_hex(value):
            return {"invalid_hex": True}
        raw = bytes.fromhex(value)
    else:
        raw = value.encode("utf-8")
    summary: dict[str, Any] = {"byte_length": len(raw), "sha256": sha256_hex(raw)}
    if len(raw) <= INLINE_ARTIFACT_LIMIT:
        summary["hex" if hex_value else "value"] = value
    return summary


def normalize_observation(process: Mapping[str, Any]) -> dict[str, Any]:
    if process.get("outcome") != "diagnostic":
        return dict(process)
    diagnostic = process["diagnostic"]
    result_class = diagnostic.get("result_class")
    code = diagnostic.get("code")
    diagnostic_limited = code == "resource.diagnostic_bytes" and {
        "validation_result_class",
        "validation_code",
        "validation_status",
    } <= set(diagnostic)
    if diagnostic_limited:
        result_class = diagnostic["validation_result_class"]
        code = diagnostic["validation_code"]
    status = diagnostic.get("status")
    accepted = status == "accepted" if isinstance(status, str) else result_class == "accepted" and code == "accepted"
    if diagnostic_limited:
        accepted = diagnostic["validation_status"] == "accepted"
    normalized: dict[str, Any] = {
        "outcome": "completed",
        "returncode": process["returncode"],
        "accepted": accepted,
        "result_class": result_class,
        "code": code,
        "diagnostic_limited": diagnostic_limited or code == "resource.diagnostic_bytes",
        "stderr_present": process["stderr_present"],
    }
    if "cbor_hex" in diagnostic:
        normalized["cbor"] = summarize_artifact(diagnostic["cbor_hex"], hex_value=True)
    if "frame_hex" in diagnostic:
        normalized["frame"] = summarize_artifact(diagnostic["frame_hex"], hex_value=True)
    if "digest_hex" in diagnostic:
        normalized["digest"] = summarize_artifact(diagnostic["digest_hex"], hex_value=True)
    if "value" in diagnostic:
        projection = canonical_json_bytes(diagnostic["value"])
        normalized["typed_projection"] = {
            "byte_length": len(projection),
            "sha256": sha256_hex(projection),
        }
        if len(projection) <= INLINE_ARTIFACT_LIMIT:
            normalized["typed_projection"]["value"] = diagnostic["value"]
    return normalized


def implementation_environment(extra: Mapping[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONHASHSEED"] = "0"
    env["LC_ALL"] = "C.UTF-8"
    env["LANG"] = "C.UTF-8"
    if extra:
        env.update(extra)
    return env


class Implementations:
    def __init__(self, rust_binary: Path | None):
        self.rust_binary = rust_binary
        python_path = str(PYTHON_ORACLE_ROOT)
        existing = os.environ.get("PYTHONPATH")
        if existing:
            python_path += os.pathsep + existing
        self.python_env = implementation_environment({"PYTHONPATH": python_path})
        self.rust_env = implementation_environment()

    def invoke_python(self, command: str, value: Any) -> dict[str, Any]:
        process = invoke_process(
            [sys.executable, "-m", "statqed_oracle.cli", command],
            compact_json_bytes(value),
            cwd=ROOT,
            env=self.python_env,
        )
        observation = normalize_observation(process)
        if observation.get("diagnostic_limited") and observation.get("accepted"):
            full_process = invoke_process(
                [sys.executable, "-c", PYTHON_FULL_RESULT_HELPER],
                compact_json_bytes({"command": command, "input": value}),
                cwd=ROOT,
                env=self.python_env,
            )
            full_observation = normalize_observation(full_process)
            if full_observation.get("outcome") == "completed":
                full_observation["diagnostic_fallback"] = "bounded_cli_then_full_library_projection"
                return full_observation
        return observation

    def invoke_python_raw(self, command: str, encoded_input: bytes) -> dict[str, Any]:
        return normalize_observation(
            invoke_process(
                [sys.executable, "-m", "statqed_oracle.cli", command],
                encoded_input,
                cwd=ROOT,
                env=self.python_env,
            )
        )

    def invoke_rust(self, command: str, value: Any) -> dict[str, Any]:
        if self.rust_binary is None:
            return {"outcome": "unavailable", "reason": "rust binary not requested"}
        encoded_input = compact_json_bytes(value)
        process = invoke_process(
            [str(self.rust_binary), command],
            encoded_input,
            cwd=ROOT,
            env=self.rust_env,
        )
        observation = normalize_observation(process)
        if observation.get("code") == "resource.diagnostic_bytes" and command in {"encode", "decode"}:
            evidence_command = "encode-raw" if command == "encode" else "decode-raw"
            evidence = invoke_evidence_process(
                [str(self.rust_binary), evidence_command],
                encoded_input,
                cwd=ROOT,
                env=self.rust_env,
            )
            if evidence.get("outcome") == "evidence":
                if command == "encode":
                    cbor = evidence["bytes"]
                    projection_evidence = invoke_evidence_process(
                        [str(self.rust_binary), "decode-raw"],
                        compact_json_bytes({"cbor_hex": cbor.hex()}),
                        cwd=ROOT,
                        env=self.rust_env,
                    )
                    if projection_evidence.get("outcome") != "evidence":
                        return projection_evidence
                    projection_bytes = projection_evidence["bytes"]
                else:
                    cbor = bytes.fromhex(value["cbor_hex"])
                    projection_bytes = evidence["bytes"]
                try:
                    projection = json.loads(projection_bytes.decode("utf-8", "strict"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    return {"outcome": "operational", "result_class": "operational_failure", "code": "operational.exception"}
                return {
                    "outcome": "completed",
                    "returncode": 0,
                    "accepted": True,
                    "result_class": "accepted",
                    "code": "accepted",
                    "diagnostic_limited": True,
                    "diagnostic_fallback": f"bounded_cli_then_{evidence_command}",
                    "stderr_present": evidence["stderr_present"],
                    "cbor": summarize_artifact(cbor.hex(), hex_value=True),
                    "typed_projection": projection_summary(projection),
                }
            return evidence
        if observation.get("code") == "resource.diagnostic_bytes" and command == "frame":
            evidence = invoke_evidence_process(
                [str(self.rust_binary), "frame-raw"],
                encoded_input,
                cwd=ROOT,
                env=self.rust_env,
            )
            if evidence.get("outcome") == "evidence":
                frame = evidence["bytes"]
                return {
                    "outcome": "completed",
                    "returncode": 0,
                    "accepted": True,
                    "result_class": "accepted",
                    "code": "accepted",
                    "diagnostic_limited": True,
                    "diagnostic_fallback": "bounded_cli_then_frame-raw",
                    "stderr_present": evidence["stderr_present"],
                    "frame": summarize_artifact(frame.hex(), hex_value=True),
                }
        return observation

    def invoke_rust_raw(self, command: str, encoded_input: bytes) -> dict[str, Any]:
        if self.rust_binary is None:
            return {"outcome": "unavailable", "reason": "rust binary not requested"}
        return normalize_observation(
            invoke_process(
                [str(self.rust_binary), command],
                encoded_input,
                cwd=ROOT,
                env=self.rust_env,
            )
        )


def build_rust_binary(target_root: Path) -> tuple[Path | None, dict[str, Any]]:
    cargo = shutil.which("cargo")
    if cargo is None:
        return None, {"status": "unavailable", "reason": "cargo not found"}
    target = target_root / "rust-target"
    command = [cargo, "build", "--locked", "--offline", "--target-dir", str(target)]
    try:
        completed = subprocess.run(
            command,
            cwd=RUST_ROOT,
            env=implementation_environment(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=180,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return None, {"status": "unavailable", "reason": type(error).__name__}
    if completed.returncode != 0:
        return None, {
            "status": "build_failed",
            "returncode": completed.returncode,
            "stdout_sha256": sha256_hex(completed.stdout),
            "stderr_sha256": sha256_hex(completed.stderr),
        }
    binary = target / "debug/statqed-rust-cbor-prototype"
    if not binary.is_file():
        return None, {"status": "build_failed", "reason": "expected binary absent"}
    return binary, {
        "status": "available",
        "implementation_source_sha256": rust_implementation_source_hash(),
        "prototype_commit": RUST_PROTOTYPE_COMMIT,
        "dependency_evidence_commit": RUST_DEPENDENCY_EVIDENCE_COMMIT,
        "adversarial_fix_commit": RUST_ADVERSARIAL_FIX_COMMIT,
        "transport_fix_commit": RUST_TRANSPORT_FIX_COMMIT,
        "frozen_tree_commit": RUST_FROZEN_TREE_COMMIT,
    }


def tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file() and "target" not in item.parts and "__pycache__" not in item.parts):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\x00")
        digest.update(path.read_bytes())
        digest.update(b"\x00")
    return digest.hexdigest()


def selected_source_hash(root: Path, relative_paths: Sequence[str]) -> str:
    """Hash only executable/locked implementation subjects, excluding later review prose."""

    digest = hashlib.sha256()
    for relative in sorted(relative_paths):
        path = root / relative
        if not path.is_file():
            raise ConformanceError(f"implementation provenance subject missing: {path.relative_to(ROOT)}")
        digest.update(relative.encode("utf-8"))
        digest.update(b"\x00")
        digest.update(path.read_bytes())
        digest.update(b"\x00")
    return digest.hexdigest()


def python_oracle_source_hash() -> str:
    return selected_source_hash(
        PYTHON_ORACLE_ROOT,
        (
            ".python-version",
            "requirements.txt",
            "statqed_oracle/__init__.py",
            "statqed_oracle/cli.py",
            "statqed_oracle/oracle.py",
        ),
    )


def rust_implementation_source_hash() -> str:
    return selected_source_hash(
        RUST_ROOT,
        (
            "Cargo.toml",
            "Cargo.lock",
            "rust-toolchain.toml",
            "src/lib.rs",
            "src/main.rs",
        ),
    )


def expected_projection(case: Mapping[str, Any]) -> dict[str, Any] | None:
    if not case["accept"]:
        return None
    if case["input_layer"] in {"semantic", "semantic_recipe"}:
        typed = semantic_to_typed(case["input"])
        if typed.get("type") in {"bignum", "rational", "decimal", "ieee_bits", "interval", "extension_sequence"}:
            return None
        return canonicalize_typed(typed)
    if case["id"] in {"RESOURCE-INPUT-BYTES-1048576"}:
        return semantic_to_typed(
            {
                "kind": "array",
                "items": [
                    {"kind": "byte_string_recipe", "byte_hex": "00", "repeat": 1030},
                    {
                        "repeat_item": {"kind": "byte_string_recipe", "byte_hex": "00", "repeat": 1024},
                        "count": 1020,
                    },
                ],
            }
        )
    return None


def decode_request(case: Mapping[str, Any], by_id: Mapping[str, dict[str, Any]]) -> dict[str, Any]:
    if case["input_layer"] in {"raw_cbor", "raw_cbor_recipe"}:
        raw = raw_cbor_bytes(case, by_id)
        return {"cbor_hex": raw.hex()}
    if case["input_layer"] == "validation_request":
        data = case["input"]
        request: dict[str, Any] = {"cbor_hex": data["raw_hex"]}
        if "requested_profile_id" in data:
            request["profile_id"] = data["requested_profile_id"]
        if "required_top_level_kind" in data:
            request["expected_top_level"] = data["required_top_level_kind"]
        return request
    if case["input_layer"] == "shape_request":
        return {"cbor_hex": case["input"]["raw_hex"]}
    raise ConformanceError(f"{case['id']}: not a decode request")


def invoke_digest(implementations: Implementations, case: Mapping[str, Any], by_id: Mapping[str, dict[str, Any]]) -> dict[str, Any]:
    material = digest_material(case, by_id)
    outputs: dict[str, Any] = {}
    if material["operation"] == "frame":
        common = {
            "purpose_id": material["purpose_id"],
            "algorithm_id": material["algorithm_id"],
            "profile_id": material["profile_id"],
            "object_class_schema_id": material["object_class_schema_id"],
            "framing_id": material["framing_id"],
        }
        outputs["python"] = implementations.invoke_python(
            "frame", {**common, "payload_hex": material["payload"].hex()}
        )
        outputs["rust"] = implementations.invoke_rust(
            "frame", {**common, "cbor_hex": material["payload"].hex()}
        )
    else:
        python_request = {
            "frame_hex": material["frame"].hex(),
            "digest_hex": material["digest"].hex(),
            "expected_purpose_id": material["purpose_id"],
            "expected_algorithm_id": material["algorithm_id"],
            "expected_profile_id": material["profile_id"],
            "expected_object_class_schema_id": material["object_class_schema_id"],
            "expected_framing_id": material["framing_id"],
        }
        rust_request = {
            "frame_hex": material["frame"].hex(),
            "digest_hex": material["digest"].hex(),
            "purpose_id": material["purpose_id"],
            "algorithm_id": material["algorithm_id"],
            "profile_id": material["profile_id"],
            "object_class_schema_id": material["object_class_schema_id"],
            "framing_id": material["framing_id"],
        }
        outputs["python"] = implementations.invoke_python("verify-digest", python_request)
        outputs["rust"] = implementations.invoke_rust("verify-digest", rust_request)
    return outputs


def apply_harness_phase(case: Mapping[str, Any], observation: dict[str, Any], cddl_rules: Mapping[str, str]) -> dict[str, Any]:
    if observation.get("outcome") != "completed" or not observation.get("accepted"):
        return observation
    layer = case["input_layer"]
    if layer == "validation_request":
        data = case["input"]
        if data.get("requested_schema_id", SCHEMA_ID) != SCHEMA_ID:
            return {**observation, "accepted": False, "result_class": "expectedness", "code": "expected.schema_id", "phase_owner": "harness_schema_expectedness"}
        if data.get("requested_schema_version", SCHEMA_VERSION) != SCHEMA_VERSION:
            return {**observation, "accepted": False, "result_class": "expectedness", "code": "expected.schema_version", "phase_owner": "harness_schema_expectedness"}
    if layer == "shape_request":
        if not cddl_rules:
            raise ConformanceError("CDDL rules were not loaded")
        return {**observation, "accepted": False, "result_class": "cddl_shape", "code": "shape.cddl_mismatch", "phase_owner": "restricted_cddl_checker"}
    return observation


def local_operational_case(case: Mapping[str, Any]) -> dict[str, Any]:
    kind = case["input"]["kind"]
    if kind == "forced_nontermination_or_delay":
        command = [sys.executable, "-c", "import time; time.sleep(30)"]
    elif kind == "forced_allocation_pressure":
        command = [sys.executable, "-c", "x=bytearray(256*1024*1024); print(len(x))"]
    elif kind == "forced_process_termination":
        command = [sys.executable, "-c", "import os; os.abort()"]
    elif kind == "forced_uncaught_exception":
        command = [sys.executable, "-c", "raise RuntimeError('deliberate conformance exception')"]
    else:
        raise ConformanceError(f"unsupported operational recipe {kind}")
    observation = invoke_process(command, b"", cwd=ROOT, env=implementation_environment())
    if kind == "forced_allocation_pressure" and observation.get("code") == "operational.exception":
        observation["code"] = "operational.memory"
    return {
        "outcome": "completed",
        "accepted": False,
        "result_class": "operational_failure",
        "code": observation.get("code", "operational.exception"),
    }


def local_diagnostic_case(case: Mapping[str, Any]) -> dict[str, Any]:
    size = case["input"]["exact_rendered_bytes"]
    if size <= 4096:
        return {"outcome": "completed", "accepted": True, "result_class": "accepted", "code": "accepted"}
    return {"outcome": "completed", "accepted": False, "result_class": "resource", "code": "resource.diagnostic_bytes"}


def case_observations(
    case: Mapping[str, Any],
    by_id: Mapping[str, dict[str, Any]],
    implementations: Implementations,
    cddl_rules: Mapping[str, str],
) -> dict[str, Any]:
    layer = case["input_layer"]
    if layer in {"semantic", "semantic_recipe"}:
        typed = semantic_to_typed(case["input"])
        return {
            "python": implementations.invoke_python("encode", typed),
            "rust": implementations.invoke_rust("encode", typed),
        }
    if layer == "typed_json_recipe":
        encoded_input = typed_json_bytes(case)
        return {
            "python": implementations.invoke_python_raw("encode", encoded_input),
            "rust": implementations.invoke_rust_raw("encode", encoded_input),
        }
    if layer in {"raw_cbor", "raw_cbor_recipe", "validation_request", "shape_request"}:
        request = decode_request(case, by_id)
        decoded: dict[str, Any] = {}
        input_bytes = bytes.fromhex(request["cbor_hex"])
        for name, observation in (
            ("python", implementations.invoke_python("decode", request)),
            ("rust", implementations.invoke_rust("decode", request)),
        ):
            observation = apply_harness_phase(case, observation, cddl_rules)
            if observation.get("accepted"):
                observation["cbor"] = summarize_artifact(input_bytes.hex(), hex_value=True)
            decoded[name] = observation
        return decoded
    if layer.startswith("digest_") or layer.startswith("raw_digest_"):
        return invoke_digest(implementations, case, by_id)
    if layer == "diagnostic_recipe":
        return {"harness": local_diagnostic_case(case)}
    if layer == "harness_recipe":
        return {"harness": local_operational_case(case)}
    if layer == "mutant_spec":
        return {
            "harness": {
                "outcome": "completed",
                "accepted": False,
                "result_class": "differential_detection",
                "code": case["stable_code"],
                "evidence_ref": "conformance/prototypes/generated-v1/mutations.json",
            }
        }
    raise ConformanceError(f"{case['id']}: unsupported input_layer {layer}")


def projection_summary(value: Mapping[str, Any]) -> dict[str, Any]:
    rendered = canonical_json_bytes(value)
    result: dict[str, Any] = {"byte_length": len(rendered), "sha256": sha256_hex(rendered)}
    if len(rendered) <= INLINE_ARTIFACT_LIMIT:
        result["value"] = value
    return result


def compare_observation(
    case: Mapping[str, Any],
    observation: Mapping[str, Any],
    expected: bytes | None,
    projection: Mapping[str, Any] | None,
) -> list[str]:
    errors: list[str] = []
    if observation.get("outcome") == "unavailable":
        return ["implementation_unavailable"]
    if observation.get("outcome") != "completed":
        return [f"operational_outcome:{observation.get('code', observation.get('outcome'))}"]
    if observation.get("accepted") != case["accept"]:
        errors.append(f"acceptance:{observation.get('accepted')}!=expected:{case['accept']}")
    if observation.get("result_class") != case["intended_class"]:
        errors.append(f"class:{observation.get('result_class')}!=expected:{case['intended_class']}")
    if observation.get("code") != case["stable_code"]:
        errors.append(f"code:{observation.get('code')}!=expected:{case['stable_code']}")
    if case["accept"] and expected is not None:
        field = "frame" if case["input_layer"].startswith("digest_frame") else "cbor"
        artifact = observation.get(field)
        if not isinstance(artifact, dict):
            errors.append(f"{field}_unavailable")
        else:
            if artifact.get("byte_length") != len(expected):
                errors.append(f"{field}_length")
            if artifact.get("sha256") != sha256_hex(expected):
                errors.append(f"{field}_bytes")
    if case["accept"] and projection is not None:
        actual = observation.get("typed_projection")
        wanted = projection_summary(projection)
        if not isinstance(actual, dict):
            errors.append("typed_projection_unavailable")
        elif actual.get("sha256") != wanted["sha256"]:
            errors.append("typed_projection")
    return errors


def cross_compare(case: Mapping[str, Any], observations: Mapping[str, Any]) -> list[str]:
    if "python" not in observations or "rust" not in observations:
        return []
    left, right = observations["python"], observations["rust"]
    if left.get("outcome") != "completed" or right.get("outcome") != "completed":
        return []
    errors: list[str] = []
    for field in ("accepted", "result_class", "code"):
        if left.get(field) != right.get(field):
            errors.append(f"implementations_{field}")
    if case["accept"]:
        artifact_name = "frame" if case["input_layer"].startswith("digest_frame") else "cbor"
        left_artifact, right_artifact = left.get(artifact_name), right.get(artifact_name)
        if isinstance(left_artifact, dict) and isinstance(right_artifact, dict):
            if left_artifact.get("sha256") != right_artifact.get("sha256"):
                errors.append("implementations_bytes")
        left_value, right_value = left.get("typed_projection"), right.get("typed_projection")
        if isinstance(left_value, dict) and isinstance(right_value, dict):
            if left_value.get("sha256") != right_value.get("sha256"):
                errors.append("implementations_typed_projection")
        left_digest, right_digest = left.get("digest"), right.get("digest")
        if isinstance(left_digest, dict) and isinstance(right_digest, dict):
            if left_digest.get("sha256") != right_digest.get("sha256"):
                errors.append("implementations_digest")
    return errors


def first_difference(left: bytes, right: bytes) -> int | None:
    for index, (a, b) in enumerate(zip(left, right)):
        if a != b:
            return index
    if len(left) != len(right):
        return min(len(left), len(right))
    return None


def run_mutations(by_id: Mapping[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Execute two real mutants and validate every retained mutant specification."""

    results: list[dict[str, Any]] = []
    encoder_case = by_id["MUTANT-ENCODER-LENGTH-FIRST-MAP"]
    expected = bytes.fromhex(encoder_case["input"]["reviewed_expected_hex"])
    mutant = bytes.fromhex(encoder_case["input"]["mutant_output_hex"])
    results.append(
        {
            "id": "EXECUTED-BAD-ENCODER-LENGTH-FIRST",
            "mutant_kind": "length_first_map_order",
            "source_fixture": encoder_case["id"],
            "detected": mutant != expected,
            "first_difference_byte": first_difference(mutant, expected),
            "expected_sha256": sha256_hex(expected),
            "mutant_sha256": sha256_hex(mutant),
        }
    )

    duplicate_fixture = by_id["MAP-DUPLICATE-EXACT-INT0"]
    raw = raw_cbor_bytes(duplicate_fixture, by_id)
    # Deliberately wrong last-wins decoder for only the minimized a2/int/bool case.
    wrong_accepted = raw == bytes.fromhex("a200f400f5")
    results.append(
        {
            "id": "EXECUTED-BAD-DECODER-LAST-WINS",
            "mutant_kind": "native_map_before_duplicate_scan",
            "source_fixture": duplicate_fixture["id"],
            "detected": wrong_accepted and not duplicate_fixture["accept"],
            "required_code": duplicate_fixture["stable_code"],
            "mutant_result": "accepted",
        }
    )

    nonpreferred = by_id["HEAD-NONPREF-U-0-AS-U8"]
    wrong_normalized = raw_cbor_bytes(nonpreferred, by_id) == bytes.fromhex("1800")
    results.append(
        {
            "id": "EXECUTED-BAD-DECODER-REENCODE",
            "mutant_kind": "decode_reencode_upgrades_nonprofile",
            "source_fixture": nonpreferred["id"],
            "detected": wrong_normalized and not nonpreferred["accept"],
            "required_code": nonpreferred["stable_code"],
            "mutant_result": "accepted",
        }
    )

    for case in sorted(
        (item for item in by_id.values() if item["input_layer"] == "mutant_spec"),
        key=lambda item: item["id"],
    ):
        spec = case["input"]
        detected = False
        evidence: dict[str, Any] = {}
        if "mutant_output_hex" in spec and "reviewed_expected_hex" in spec:
            mutant_bytes = bytes.fromhex(spec["mutant_output_hex"])
            expected_bytes_value = bytes.fromhex(spec["reviewed_expected_hex"])
            detected = mutant_bytes != expected_bytes_value
            evidence = {"first_difference_byte": first_difference(mutant_bytes, expected_bytes_value)}
        elif "required_result" in spec:
            referenced = None
            for field in ("raw_fixture", "semantic_fixture", "frame_fixture", "digest_fixture"):
                if field in spec:
                    referenced = by_id[spec[field]]
                    break
            required = spec["required_result"]
            if referenced is None:
                referenced = next(
                    (item for item in by_id.values() if item["stable_code"] == required),
                    None,
                )
            detected = referenced is not None and referenced["stable_code"] == required
            evidence = {"linked_fixture": referenced["id"] if referenced else None, "required_code": required}
        elif "required_hash_input" in spec and "hashed_hex" in spec:
            _, baseline_frame = base_digest_components(by_id)
            mutant_hash_input = bytes.fromhex(spec["hashed_hex"])
            detected = mutant_hash_input != baseline_frame
            evidence = {
                "required_input_sha256": sha256_hex(baseline_frame),
                "mutant_input_sha256": sha256_hex(mutant_hash_input),
            }
        else:
            detected = False
        results.append(
            {
                "id": case["id"],
                "mutant_kind": spec["mutation"],
                "detected": detected,
                "stable_code": case["stable_code"],
                **evidence,
            }
        )
    if not all(result["detected"] for result in results):
        missed = [result["id"] for result in results if not result["detected"]]
        raise ConformanceError(f"deliberate mutation escaped detection: {missed}")
    return results


def golden_candidate(
    case: Mapping[str, Any],
    expected: bytes | None,
    observations: Mapping[str, Any],
    comparison_errors: Mapping[str, list[str]],
) -> tuple[dict[str, Any], bytes] | None:
    if not case["accept"] or expected is None or set(observations) != {"python", "rust"}:
        return None
    if comparison_errors.get("python") or comparison_errors.get("rust") or comparison_errors.get("cross"):
        return None
    field = "frame" if case["input_layer"].startswith("digest_frame") else "cbor"
    for implementation in ("python", "rust"):
        artifact = observations[implementation].get(field)
        if not isinstance(artifact, dict) or artifact.get("sha256") != sha256_hex(expected):
            return None
    suffix = "frame" if field == "frame" else "cbor"
    relative_path = f"conformance/prototypes/golden/serialization-v1/{case['id']}.{suffix}"
    result: dict[str, Any] = {
        "id": case["id"],
        "fixture_id": case["id"],
        "path": relative_path,
        "artifact_kind": field,
        "byte_length": len(expected),
        "sha256": sha256_hex(expected),
        "expectation_kind": case["expected_encoding"]["kind"],
        "agreement": ["python-oracle", "rust-prototype"],
    }
    if len(expected) <= INLINE_ARTIFACT_LIMIT:
        result["inline_hex"] = expected.hex()
    if field == "frame":
        digests = [observations[name].get("digest") for name in ("python", "rust")]
        if all(isinstance(item, dict) and isinstance(item.get("hex"), str) for item in digests):
            if digests[0]["hex"] == digests[1]["hex"]:
                result["digest_hex"] = digests[0]["hex"]
    return result, expected


def run_suite(
    rust_binary: Path | None, rust_build: Mapping[str, Any]
) -> tuple[dict[str, bytes], dict[str, bytes]]:
    catalog, cases, by_id = load_and_validate_fixtures()
    cddl_rules = validate_cddl_source()
    implementations = Implementations(rust_binary)
    result_cases: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    goldens: list[dict[str, Any]] = []
    golden_files: dict[str, bytes] = {}

    for case in cases:
        expected = expected_bytes(case, by_id)
        projection = expected_projection(case)
        if projection is not None:
            cddl_result = {
                "phase": "cddl_shape",
                "rule_id": "statqed-value",
                "matched": cddl_matches_typed(projection),
                "source": "schemas/prototypes/cddl/profile-v1.cddl",
            }
        elif case["input_layer"] == "shape_request":
            cddl_result = {
                "phase": "cddl_shape",
                "rule_id": case["input"]["published_rule_id"],
                "matched": False,
                "code": "shape.cddl_mismatch",
                "source": "restricted_harness_rule",
            }
        else:
            cddl_result = {"phase": "cddl_shape", "status": "not_reached_or_not_applicable"}
        observations = case_observations(case, by_id, implementations, cddl_rules)
        comparisons: dict[str, list[str]] = {}
        for name, observation in observations.items():
            comparisons[name] = compare_observation(case, observation, expected, projection)
        comparisons["cross"] = cross_compare(case, observations)
        if projection is not None and not cddl_result["matched"]:
            comparisons["cddl"] = ["reviewed_accepted_projection_failed_statqed_value"]
        case_result = {
            "id": case["id"],
            "expected": {
                "accept": case["accept"],
                "result_class": case["intended_class"],
                "code": case["stable_code"],
                "encoding": None
                if expected is None
                else {"byte_length": len(expected), "sha256": sha256_hex(expected)},
                "typed_projection": None if projection is None else projection_summary(projection),
            },
            "observations": observations,
            "cddl": cddl_result,
            "comparison_errors": comparisons,
        }
        result_cases.append(case_result)
        for implementation, errors in comparisons.items():
            if errors:
                failures.append(
                    {
                        "id": case["id"],
                        "implementation": implementation,
                        "errors": errors,
                        "expected_class": case["intended_class"],
                        "expected_code": case["stable_code"],
                        "observed_class": observations.get(implementation, {}).get("result_class"),
                        "observed_code": observations.get(implementation, {}).get("code"),
                    }
                )
        candidate = golden_candidate(case, expected, observations, comparisons)
        if candidate is not None:
            vector, artifact = candidate
            goldens.append(vector)
            golden_files[Path(vector["path"]).name] = artifact

    mutations = run_mutations(by_id)
    counts: dict[str, int] = {}
    for case in cases:
        counts[case["intended_class"]] = counts.get(case["intended_class"], 0) + 1
    results_document = {
        "schema_id": "statqed.serialization-conformance-results.v1",
        "status": "pass" if not failures else "fail",
        "fixture_catalog_sha256": sha256_hex((FIXTURE_ROOT / "catalog.json").read_bytes()),
        "cddl_sha256": sha256_hex(CDDL_PATH.read_bytes()),
        "case_count": len(cases),
        "class_counts": dict(sorted(counts.items())),
        "joint_golden_count": len(goldens),
        "failure_count": len(failures),
        "cases": result_cases,
    }
    golden_manifest = {
        "schema_id": "statqed.serialization-binary-golden-manifest.v1",
        "authority": "joint_implementation_agreement_with_precommitted_semantic_expectation",
        "profile_id": PROFILE_ID,
        "fixture_catalog_sha256": sha256_hex((FIXTURE_ROOT / "catalog.json").read_bytes()),
        "nonclaims": [
            "Neither implementation is the semantic oracle.",
            "CDDL shape, byte agreement, and digest agreement establish no statistical, provenance, inferential, or kernel claim.",
        ],
        "vector_count": len(goldens),
        "vectors": goldens,
    }
    golden_manifest_bytes = canonical_json_bytes(golden_manifest)
    golden_files["manifest.json"] = golden_manifest_bytes
    goldens_document = {
        "schema_id": "statqed.serialization-golden-index.v1",
        "manifest_path": "conformance/prototypes/golden/serialization-v1/manifest.json",
        "manifest_sha256": sha256_hex(golden_manifest_bytes),
        "vector_count": len(goldens),
    }
    failures_document = {
        "schema_id": "statqed.serialization-minimized-failures.v1",
        "status": "empty" if not failures else "genuine_disagreements_present",
        "failure_count": len(failures),
        "failures": failures,
    }
    mutations_document = {
        "schema_id": "statqed.serialization-mutation-evidence.v1",
        "mutation_count": len(mutations),
        "all_detected": all(item["detected"] for item in mutations),
        "mutations": mutations,
    }
    files = {
        "results.json": canonical_json_bytes(results_document),
        "goldens.json": canonical_json_bytes(goldens_document),
        "failures.json": canonical_json_bytes(failures_document),
        "mutations.json": canonical_json_bytes(mutations_document),
    }
    manifest = {
        "schema_id": "statqed.serialization-generated-manifest.v1",
        "generator": "scripts/serialization/run_conformance.py",
        "regeneration_command": "python3 scripts/serialization/run_conformance.py --regenerate",
        "verification_command": "python3 scripts/serialization/run_conformance.py --verify",
        "status": results_document["status"],
        "case_count": len(cases),
        "accepted_count": sum(case["accept"] for case in cases),
        "rejected_count": sum(not case["accept"] for case in cases),
        "joint_golden_count": len(goldens),
        "failure_count": len(failures),
        "fixture_frozen_commit": SEMANTIC_FIXTURE_FROZEN_COMMIT,
        "fixture_tree_sha256": tree_hash(FIXTURE_ROOT),
        "python_oracle": {
            "frozen_commit": PYTHON_ORACLE_FROZEN_COMMIT,
            "implementation_source_sha256": python_oracle_source_hash(),
        },
        "rust_prototype": dict(rust_build),
        "cddl_sha256": sha256_hex(CDDL_PATH.read_bytes()),
        "golden_manifest_sha256": sha256_hex(golden_manifest_bytes),
        "operational_limits": {
            "fixture_timeout_seconds": FIXTURE_TIMEOUT_SECONDS,
            "process_memory_mib": PROCESS_MEMORY_BYTES // (1024 * 1024),
            "platform_scope": "Linux" if platform.system() == "Linux" else "unsupported_non_linux",
        },
        "files": {name: {"bytes": len(data), "sha256": sha256_hex(data)} for name, data in sorted(files.items())},
    }
    files["manifest.json"] = canonical_json_bytes(manifest)
    return files, golden_files


def verify_file_set(root: Path, files: Mapping[str, bytes], label: str) -> list[str]:
    errors: list[str] = []
    expected_names = set(files)
    actual_names = {path.name for path in root.iterdir() if path.is_file()} if root.is_dir() else set()
    if actual_names != expected_names:
        errors.append(f"{label} file set differs: expected={sorted(expected_names)} actual={sorted(actual_names)}")
    for name, expected in files.items():
        path = root / name
        try:
            actual = path.read_bytes()
        except OSError:
            continue
        if actual != expected:
            errors.append(f"{label} drift: {path.relative_to(ROOT)}")
    return errors


def write_file_set(root: Path, files: Mapping[str, bytes]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for path in root.iterdir():
        if not path.is_file():
            raise ConformanceError(f"unexpected directory in generated file set: {path.relative_to(ROOT)}")
        if path.name not in files:
            path.unlink()
    for name, data in files.items():
        path = root / name
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_bytes(data)
        os.replace(temporary, path)


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--verify", action="store_true", help="re-run and byte-compare generated evidence")
    action.add_argument("--regenerate", action="store_true", help="replace generated evidence from a fresh bounded run")
    parser.add_argument("--python-only", action="store_true", help="retain Python observations while Rust is unavailable; cannot pass")
    parser.add_argument("--rust-bin", type=Path, help="use an already built Rust diagnostic CLI")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_arguments(argv)
    if platform.system() != "Linux":
        raise ConformanceError("the 128 MiB operational ceiling is implemented only on Linux")
    with tempfile.TemporaryDirectory(prefix="statqed-sq0005-conformance-") as temporary:
        rust_build: dict[str, Any]
        if arguments.python_only:
            rust_binary = None
            rust_build = {"status": "unavailable", "reason": "--python-only"}
        elif arguments.rust_bin is not None:
            rust_binary = arguments.rust_bin.resolve()
            if not rust_binary.is_file():
                raise ConformanceError(f"Rust binary not found: {rust_binary}")
            rust_build = {
                "status": "available",
                "implementation_source_sha256": rust_implementation_source_hash(),
                "prototype_commit": RUST_PROTOTYPE_COMMIT,
                "dependency_evidence_commit": RUST_DEPENDENCY_EVIDENCE_COMMIT,
                "adversarial_fix_commit": RUST_ADVERSARIAL_FIX_COMMIT,
                "transport_fix_commit": RUST_TRANSPORT_FIX_COMMIT,
                "frozen_tree_commit": RUST_FROZEN_TREE_COMMIT,
            }
        else:
            rust_binary, rust_build = build_rust_binary(Path(temporary))
        files, golden_files = run_suite(rust_binary, rust_build)
    results = json.loads(files["results.json"])
    if arguments.regenerate:
        write_file_set(GENERATED_ROOT, files)
        if results["status"] == "pass":
            write_file_set(GOLDEN_ROOT, golden_files)
    else:
        drift = verify_file_set(GENERATED_ROOT, files, "generated evidence")
        drift.extend(verify_file_set(GOLDEN_ROOT, golden_files, "binary golden"))
        if drift:
            for item in drift:
                print(item, file=sys.stderr)
            return 1
    print(
        json.dumps(
            {
                "case_count": results["case_count"],
                "failure_count": results["failure_count"],
                "joint_golden_count": results["joint_golden_count"],
                "mutation_count": json.loads(files["mutations.json"])["mutation_count"],
                "status": results["status"],
            },
            separators=(",", ":"),
            sort_keys=True,
        )
    )
    return 0 if results["status"] == "pass" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ConformanceError as error:
        print(f"conformance error: {error}", file=sys.stderr)
        raise SystemExit(2) from error
