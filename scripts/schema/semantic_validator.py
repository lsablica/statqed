#!/usr/bin/env python3
"""Independent standard-library semantics for the six-field v0 fixture.

The validator consumes the typed-JSON projection used by the frozen SQ-0005
oracles so map-entry order and duplicates remain visible before host-map
collapse. It does not encode or decode CBOR and has no authority over RFC-0001.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any


SCHEMA_ID = "statqed.foundation-structural.v0"
SCHEMA_VERSION = 0
FIELDS = (
    "schema_id",
    "schema_version",
    "fixture_kind",
    "analysis_id",
    "probability_context",
    "features",
)
ANALYSIS_ID = re.compile(r"[a-z0-9][a-z0-9._:-]{0,127}\Z", re.ASCII)


@dataclass(frozen=True)
class SemanticResult:
    accepted: bool
    code: str


def _typed_text(value: Any) -> str | None:
    if isinstance(value, dict) and value.get("type") == "text" and isinstance(value.get("value"), str):
        return value["value"]
    return None


def validate_fixture(value: Any) -> SemanticResult:
    if not isinstance(value, dict) or value.get("type") != "map" or not isinstance(value.get("entries"), list):
        return SemanticResult(False, "schema.field_type")

    entries: dict[str, Any] = {}
    for entry in value["entries"]:
        if not isinstance(entry, dict) or set(entry) != {"key", "value"}:
            return SemanticResult(False, "schema.field_type")
        key = _typed_text(entry["key"])
        if key is None:
            return SemanticResult(False, "schema.field_type")
        if key in entries:
            return SemanticResult(False, "schema.duplicate_field")
        entries[key] = entry["value"]

    missing = [field for field in FIELDS if field not in entries]
    if missing:
        return SemanticResult(False, "schema.missing_field")
    unknown = [field for field in entries if field not in FIELDS]
    if unknown:
        return SemanticResult(False, "schema.unknown_field")

    expected_text = {
        "schema_id": SCHEMA_ID,
        "fixture_kind": "foundation_structural",
        "probability_context": "not_applicable",
    }
    for field, expected in expected_text.items():
        actual = _typed_text(entries[field])
        if actual is None:
            return SemanticResult(False, "schema.field_type")
        if actual != expected:
            code = {
                "schema_id": "schema.literal_mismatch",
                "fixture_kind": "schema.fixture_kind",
                "probability_context": "schema.probability_context",
            }[field]
            return SemanticResult(False, code)

    version = entries["schema_version"]
    if not isinstance(version, dict) or version.get("type") != "integer" or not isinstance(version.get("value"), str):
        return SemanticResult(False, "schema.field_type")
    if version["value"] != str(SCHEMA_VERSION):
        return SemanticResult(False, "schema.version_unsupported")

    analysis = _typed_text(entries["analysis_id"])
    if analysis is None:
        return SemanticResult(False, "schema.field_type")
    try:
        analysis_bytes = analysis.encode("ascii", "strict")
    except UnicodeEncodeError:
        return SemanticResult(False, "schema.identifier_syntax")
    if not 1 <= len(analysis_bytes) <= 128:
        return SemanticResult(False, "schema.identifier_length")
    if ANALYSIS_ID.fullmatch(analysis) is None:
        return SemanticResult(False, "schema.identifier_syntax")

    features = entries["features"]
    if not isinstance(features, dict) or features.get("type") != "array" or not isinstance(features.get("items"), list):
        return SemanticResult(False, "schema.field_type")
    if features["items"]:
        return SemanticResult(False, "schema.feature_unsupported")

    return SemanticResult(True, "accepted")
