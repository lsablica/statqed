"""Independent, standard-library oracle for the SQ-0007 expression grammar.

This module is deliberately separate from ``scripts.registry.model`` and the
Lean extractor.  It implements the reviewed ``statqed.lean-expr.v0`` grammar
directly from ``theorem-registry/spec/normalizer-v0.md``.  The input is a typed
constructor tree; it is observation material, not expected bytes supplied by
another implementation.

The oracle performs structural normalization only.  It does not reduce Lean
expressions, pretty-print them, query a Lean environment, or infer missing
dependencies.  Its output is deterministic and contains no paths, times, or
random identifiers.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import struct
import sys
from typing import Any, Final, Mapping, Sequence


GRAMMAR_ID: Final = "statqed.lean-expr.v0"
PROFILE_ID: Final = "statqed.cbor-core.v1"
FRAMING_ID: Final = "statqed.digest-lp.v1"
ALGORITHM_ID: Final = "sha-256"
OBSERVATION_ID: Final = "statqed.registry-independent-observation.v0"
DIGEST_MAGIC: Final = b"StatQED-Digest\x00"

DIGEST_DOMAINS: Final[dict[str, tuple[str, str]]] = {
    "proposition": (
        "statqed.theorem.proposition.v0",
        "statqed.lean-proposition.v0",
    ),
    "environment": (
        "statqed.theorem.environment.v0",
        "statqed.lean-environment-closure.v0",
    ),
    "record": ("statqed.registry.record.v0", "statqed.registry-record.v0"),
    "proof_build": (
        "statqed.theorem.proof-build.v0",
        "statqed.proof-build-lock.v0",
    ),
    "snapshot": (
        "statqed.registry.snapshot.v0",
        "statqed.registry-snapshot.v0",
    ),
    "compatibility": (
        "statqed.theorem.compatibility.v0",
        "statqed.compatibility-proof-lock.v0",
    ),
}

LIMITS: Final[dict[str, int]] = {
    "input_bytes": 1_048_576,
    "output_bytes": 2_097_152,
    "expression_depth": 256,
    "level_depth": 64,
    "nodes": 65_536,
    "universe_arguments": 256,
    "name_segments": 64,
    "name_segment_bytes": 256,
    "qualified_name_bytes": 1_024,
    "string_literal_bytes": 65_536,
    "aggregate_string_bytes": 262_144,
    "payload_bytes": 1_048_576,
}

_BINDER_INFO: Final = {
    "explicit": 0,
    "implicit": 1,
    "strict_implicit": 2,
    "instance_implicit": 3,
}
_UINT64_MAX: Final = (1 << 64) - 1


@dataclass
class OracleError(Exception):
    """A stable failure with no host-dependent diagnostic material."""

    code: str

    def __str__(self) -> str:
        return self.code


@dataclass
class _Budget:
    nodes: int = 0
    string_bytes: int = 0

    def node(self) -> None:
        self.nodes += 1
        if self.nodes > LIMITS["nodes"]:
            raise OracleError("registry.resource_limit")

    def string(self, text: str, *, individual_limit: int) -> bytes:
        try:
            raw = text.encode("utf-8", "strict")
        except UnicodeEncodeError as exc:
            raise OracleError("registry.normalization_failure") from exc
        if len(raw) > individual_limit:
            raise OracleError("registry.resource_limit")
        self.string_bytes += len(raw)
        if self.string_bytes > LIMITS["aggregate_string_bytes"]:
            raise OracleError("registry.resource_limit")
        return raw


def _object(value: Any, *, fields: set[str], optional: set[str] | None = None) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise OracleError("registry.normalization_failure")
    allowed = fields | (optional or set())
    if set(value) - allowed or not fields.issubset(value):
        raise OracleError("registry.normalization_failure")
    return value


def _uint(value: Any) -> int:
    if type(value) is not int or not 0 <= value <= _UINT64_MAX:
        raise OracleError("registry.normalization_failure")
    return value


def _text(value: Any, budget: _Budget, *, limit: int) -> str:
    if not isinstance(value, str):
        raise OracleError("registry.normalization_failure")
    budget.string(value, individual_limit=limit)
    return value


def _name(value: Any, budget: _Budget, *, allow_anonymous: bool = False) -> list[list[Any]]:
    """Project recursive Lean-name JSON to the language-neutral segment form."""

    segments: list[list[Any]] = []

    def visit(current: Any, depth: int) -> None:
        if depth > LIMITS["name_segments"]:
            raise OracleError("registry.resource_limit")
        node = _object(current, fields={"tag"}, optional={"parent", "segment"})
        tag = node["tag"]
        if tag == "anonymous":
            if set(node) != {"tag"}:
                raise OracleError("registry.normalization_failure")
            return
        if tag not in {"string", "numeric"} or set(node) != {"tag", "parent", "segment"}:
            raise OracleError("registry.normalization_failure")
        visit(node["parent"], depth + 1)
        if tag == "string":
            segment = _text(
                node["segment"], budget, limit=LIMITS["name_segment_bytes"]
            )
            segments.append([0, segment])
        else:
            segments.append([1, _uint(node["segment"])])

    visit(value, 0)
    if len(segments) > LIMITS["name_segments"]:
        raise OracleError("registry.resource_limit")
    total = 0
    for kind, segment in segments:
        if kind == 0:
            total += len(segment.encode("utf-8", "strict"))
    if total > LIMITS["qualified_name_bytes"]:
        raise OracleError("registry.resource_limit")
    if not segments and not allow_anonymous:
        raise OracleError("registry.normalization_failure")
    return segments


def _level(
    value: Any,
    budget: _Budget,
    parameter_names: Sequence[list[list[Any]]],
    *,
    depth: int,
) -> list[Any]:
    budget.node()
    if depth > LIMITS["level_depth"]:
        raise OracleError("registry.resource_limit")
    node = _object(value, fields={"tag"}, optional={"level", "left", "right", "name"})
    tag = node["tag"]
    if tag == "zero" and set(node) == {"tag"}:
        return [0]
    if tag == "succ" and set(node) == {"tag", "level"}:
        return [1, _level(node["level"], budget, parameter_names, depth=depth + 1)]
    if tag in {"max", "imax"} and set(node) == {"tag", "left", "right"}:
        return [
            2 if tag == "max" else 3,
            _level(node["left"], budget, parameter_names, depth=depth + 1),
            _level(node["right"], budget, parameter_names, depth=depth + 1),
        ]
    if tag == "parameter" and set(node) == {"tag", "name"}:
        projected = _name(node["name"], budget)
        try:
            index = parameter_names.index(projected)
        except ValueError as exc:
            raise OracleError("registry.missing_dependency") from exc
        return [4, index]
    if tag == "metavariable":
        raise OracleError("registry.expression_unsupported")
    raise OracleError("registry.normalization_failure")


def normalize_expression(
    expression: Any,
    *,
    level_parameters: Sequence[Any] = (),
) -> list[Any]:
    """Normalize one closed typed constructor tree to ``statqed.lean-expr.v0``."""

    budget = _Budget()
    if len(level_parameters) > LIMITS["universe_arguments"]:
        raise OracleError("registry.resource_limit")
    parameters = [_name(name, budget) for name in level_parameters]
    if len({json.dumps(name, separators=(",", ":")) for name in parameters}) != len(parameters):
        raise OracleError("registry.normalization_failure")

    def walk(value: Any, *, depth: int, bound: int) -> list[Any]:
        budget.node()
        if depth > LIMITS["expression_depth"]:
            raise OracleError("registry.resource_limit")
        node = _object(
            value,
            fields={"tag"},
            optional={
                "index", "level", "name", "universes", "function", "argument",
                "binder_info", "type", "body", "value", "kind", "structure",
                "type_name", "expression", "metadata", "binder_name", "nondep",
            },
        )
        tag = node["tag"]
        if tag == "metadata":
            if set(node) - {"tag", "expression", "metadata"} or "expression" not in node:
                raise OracleError("registry.normalization_failure")
            return walk(node["expression"], depth=depth, bound=bound)
        if tag in {"free_variable", "metavariable"}:
            raise OracleError("registry.expression_unsupported")
        if tag == "bound_variable" and set(node) == {"tag", "index"}:
            index = _uint(node["index"])
            if index >= bound:
                raise OracleError("registry.normalization_failure")
            return [0, index]
        if tag == "sort" and set(node) == {"tag", "level"}:
            return [1, _level(node["level"], budget, parameters, depth=0)]
        if tag == "constant" and set(node) == {"tag", "name", "universes"}:
            universes = node["universes"]
            if not isinstance(universes, list):
                raise OracleError("registry.normalization_failure")
            if len(universes) > LIMITS["universe_arguments"]:
                raise OracleError("registry.resource_limit")
            return [
                2,
                _name(node["name"], budget),
                [_level(level, budget, parameters, depth=0) for level in universes],
            ]
        if tag == "application" and set(node) == {"tag", "function", "argument"}:
            return [
                3,
                walk(node["function"], depth=depth + 1, bound=bound),
                walk(node["argument"], depth=depth + 1, bound=bound),
            ]
        if tag in {"lambda", "forall"}:
            allowed = {"tag", "binder_info", "type", "body", "binder_name"}
            if set(node) - allowed or not {"tag", "binder_info", "type", "body"}.issubset(node):
                raise OracleError("registry.normalization_failure")
            binder_info = _BINDER_INFO.get(node["binder_info"])
            if binder_info is None:
                raise OracleError("registry.normalization_failure")
            return [
                4 if tag == "lambda" else 5,
                binder_info,
                walk(node["type"], depth=depth + 1, bound=bound),
                walk(node["body"], depth=depth + 1, bound=bound + 1),
            ]
        if tag == "let":
            allowed = {"tag", "type", "value", "body", "binder_name", "nondep"}
            if set(node) - allowed or not {"tag", "type", "value", "body"}.issubset(node):
                raise OracleError("registry.normalization_failure")
            return [
                6,
                walk(node["type"], depth=depth + 1, bound=bound),
                walk(node["value"], depth=depth + 1, bound=bound),
                walk(node["body"], depth=depth + 1, bound=bound + 1),
            ]
        if tag == "literal" and set(node) == {"tag", "kind", "value"}:
            if node["kind"] == "natural":
                raw_value = node["value"]
                if isinstance(raw_value, str) and raw_value.isascii() and raw_value.isdigit():
                    natural = int(raw_value, 10)
                else:
                    natural = raw_value
                return [7, _uint(natural)]
            if node["kind"] == "string":
                return [
                    8,
                    _text(
                        node["value"],
                        budget,
                        limit=LIMITS["string_literal_bytes"],
                    ),
                ]
            raise OracleError("registry.expression_unsupported")
        if tag == "projection" and set(node) == {"tag", "type_name", "index", "structure"}:
            return [
                9,
                _name(node["type_name"], budget),
                _uint(node["index"]),
                walk(node["structure"], depth=depth + 1, bound=bound),
            ]
        if tag in {
            "bound_variable",
            "sort",
            "constant",
            "application",
            "lambda",
            "forall",
            "let",
            "literal",
            "projection",
            "metadata",
        }:
            raise OracleError("registry.normalization_failure")
        raise OracleError("registry.expression_unsupported")

    return walk(expression, depth=0, bound=0)


def _cbor_head(major: int, value: int) -> bytes:
    if not 0 <= value <= _UINT64_MAX:
        raise OracleError("registry.resource_limit")
    if value < 24:
        return bytes([(major << 5) | value])
    if value <= 0xFF:
        return bytes([(major << 5) | 24, value])
    if value <= 0xFFFF:
        return bytes([(major << 5) | 25]) + struct.pack(">H", value)
    if value <= 0xFFFF_FFFF:
        return bytes([(major << 5) | 26]) + struct.pack(">I", value)
    return bytes([(major << 5) | 27]) + struct.pack(">Q", value)


def canonical_cbor(value: Any, *, _depth: int = 0, _nodes: list[int] | None = None) -> bytes:
    """Encode exactly the atom/array subset used by the structural grammar."""

    nodes = _nodes if _nodes is not None else [0]
    nodes[0] += 1
    if nodes[0] > LIMITS["nodes"] or _depth > LIMITS["expression_depth"] + 8:
        raise OracleError("registry.resource_limit")
    if type(value) is int:
        out = _cbor_head(0, _uint(value))
    elif isinstance(value, str):
        try:
            encoded = value.encode("utf-8", "strict")
        except UnicodeEncodeError as exc:
            raise OracleError("registry.normalization_failure") from exc
        out = _cbor_head(3, len(encoded)) + encoded
    elif isinstance(value, list):
        parts = [canonical_cbor(item, _depth=_depth + 1, _nodes=nodes) for item in value]
        out = _cbor_head(4, len(parts)) + b"".join(parts)
    else:
        raise OracleError("registry.normalization_failure")
    if len(out) > LIMITS["payload_bytes"]:
        raise OracleError("registry.resource_limit")
    return out


def proposition_payload(expression: Any, *, level_parameters: Sequence[Any] = ()) -> bytes:
    normalized = normalize_expression(expression, level_parameters=level_parameters)
    payload = canonical_cbor([GRAMMAR_ID, normalized])
    if len(payload) > LIMITS["payload_bytes"]:
        raise OracleError("registry.resource_limit")
    return payload


def _length_prefix(component: bytes) -> bytes:
    if len(component) > 0xFFFF_FFFF:
        raise OracleError("registry.resource_limit")
    return struct.pack(">I", len(component)) + component


def digest_frame(domain: str, payload: bytes) -> tuple[bytes, str]:
    """Frame one payload under one of the six disjoint v0 digest domains."""

    if domain not in DIGEST_DOMAINS:
        raise OracleError("registry.version_unsupported")
    if not isinstance(payload, bytes) or not payload or len(payload) > LIMITS["payload_bytes"]:
        raise OracleError("registry.resource_limit")
    purpose, object_class = DIGEST_DOMAINS[domain]
    components = (
        purpose.encode("ascii"),
        ALGORITHM_ID.encode("ascii"),
        PROFILE_ID.encode("ascii"),
        object_class.encode("ascii"),
        FRAMING_ID.encode("ascii"),
        payload,
    )
    frame = DIGEST_MAGIC + b"".join(_length_prefix(component) for component in components)
    return frame, hashlib.sha256(frame).hexdigest()


def six_digest_frames(payload: bytes) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for domain in sorted(DIGEST_DOMAINS):
        frame, digest = digest_frame(domain, payload)
        result[domain] = {"digest": digest, "frame_hex": frame.hex()}
    return result


def observe(expression: Any, *, level_parameters: Sequence[Any] = ()) -> dict[str, Any]:
    normalized = normalize_expression(expression, level_parameters=level_parameters)
    payload = canonical_cbor([GRAMMAR_ID, normalized])
    if len(payload) > LIMITS["payload_bytes"]:
        raise OracleError("registry.resource_limit")
    return {
        "digests": six_digest_frames(payload),
        "normalizer": GRAMMAR_ID,
        "normalized_expression": normalized,
        "payload_hex": payload.hex(),
        "schema": OBSERVATION_ID,
    }


def require_candidate_bytes(
    expression: Any,
    candidate: bytes,
    *,
    level_parameters: Sequence[Any] = (),
) -> None:
    """Reject a candidate encoder whose bytes differ from this oracle."""

    if not isinstance(candidate, bytes):
        raise OracleError("registry.normalization_failure")
    if proposition_payload(expression, level_parameters=level_parameters) != candidate:
        raise OracleError("registry.proposition_mismatch")


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def main() -> int:
    try:
        raw_input = sys.stdin.buffer.read(LIMITS["input_bytes"] + 1)
        if len(raw_input) > LIMITS["input_bytes"]:
            raise OracleError("registry.resource_limit")
        document = json.loads(raw_input)
        if not isinstance(document, Mapping) or set(document) - {"expression", "level_parameters"}:
            raise OracleError("registry.normalization_failure")
        if "expression" not in document:
            raise OracleError("registry.normalization_failure")
        result = observe(
            document["expression"],
            level_parameters=document.get("level_parameters", []),
        )
    except (json.JSONDecodeError, UnicodeError):
        print(_canonical_json({"classification": "rejected", "code": "registry.normalization_failure"}))
        return 2
    except OracleError as exc:
        print(_canonical_json({"classification": "rejected", "code": exc.code}))
        return 2
    output = _canonical_json({"classification": "accepted", "observation": result})
    if len(output.encode("utf-8")) > LIMITS["output_bytes"]:
        print(_canonical_json({"classification": "rejected", "code": "registry.resource_limit"}))
        return 2
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
