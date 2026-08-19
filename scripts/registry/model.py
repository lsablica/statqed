"""Versioned, bounded SQ-0007 registry model.

This standard-library implementation is the independent operational oracle for
the test-only v0 record.  It consumes exported typed values; it does not call
the Lean extractor or trust candidate-supplied authorization state.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
import struct
from typing import Any, Final


PROFILE_ID: Final = "statqed.cbor-core.v1"
FRAMING_ID: Final = "statqed.digest-lp.v1"
ALGORITHM_ID: Final = "sha-256"
DIGEST_MAGIC: Final = b"StatQED-Digest\x00"

PURPOSES: Final = {
    "proposition": ("statqed.theorem.proposition.v0", "statqed.lean-proposition.v0"),
    "environment": ("statqed.theorem.environment.v0", "statqed.lean-environment-closure.v0"),
    "record": ("statqed.registry.record.v0", "statqed.registry-record.v0"),
    "proof_build": ("statqed.theorem.proof-build.v0", "statqed.proof-build-lock.v0"),
    "snapshot": ("statqed.registry.snapshot.v0", "statqed.registry-snapshot.v0"),
    "compatibility": ("statqed.theorem.compatibility.v0", "statqed.compatibility-proof-lock.v0"),
}

ERRORS: Final = {
    "registry.malformed_record",
    "registry.version_unsupported",
    "registry.normalization_failure",
    "registry.expression_unsupported",
    "registry.closure_cycle",
    "registry.closure_budget",
    "registry.closure_width_limit",
    "registry.closure_depth_limit",
    "registry.closure_work_budget_limit",
    "registry.missing_dependency",
    "registry.proposition_mismatch",
    "registry.environment_mismatch",
    "registry.statement_digest_mismatch",
    "registry.record_digest_mismatch",
    "registry.authorization_root_mismatch",
    "registry.authorization_root_unknown",
    "registry.authorization_root_revoked",
    "registry.authorization_root_historical_forbidden",
    "registry.authorization_policy_unsupported",
    "registry.proof_build_lock_mismatch",
    "registry.forbidden_axiom",
    "registry.compatibility_missing",
    "registry.compatibility_wrong_direction",
    "registry.resource_limit",
    "registry.operational_failure",
}

LIMITS: Final = {
    "input_bytes": 1_048_576,
    "object_bytes": 1_048_576,
    "output_bytes": 2_097_152,
    "registry_entries": 16,
    "identifier_bytes": 128,
    "string_bytes": 65_536,
    "aggregate_string_bytes": 262_144,
    "expression_depth": 256,
    "expression_nodes": 65_536,
    "level_depth": 64,
    "universe_arguments": 256,
    "name_segments": 64,
    "name_segment_bytes": 256,
    "qualified_name_bytes": 1_024,
    "closure_width": 256,
    "closure_depth": 64,
    "closure_units": 1_024,
    "work": 1_000_000,
    "axioms": 256,
    "compatibility_edges": 32,
    "diagnostic_bytes": 4_096,
    "canonical_nodes": 1_048_576,
    "canonical_depth": 336,
    "canonical_string_bytes": 1_048_576,
}

_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$")


@dataclass
class RegistryError(Exception):
    code: str

    def __post_init__(self) -> None:
        if self.code not in ERRORS:
            raise ValueError(f"unknown stable error: {self.code}")


def _validate_json_shape(value: Any, *, allow_oversized_integers: bool = False) -> None:
    stack = [(value, 0)]
    nodes = 0
    string_bytes = 0
    seen_containers: set[int] = set()
    while stack:
        current, depth = stack.pop()
        nodes += 1
        if nodes > LIMITS["canonical_nodes"]:
            raise RegistryError("registry.resource_limit")
        if depth > LIMITS["canonical_depth"]:
            raise RegistryError("registry.resource_limit")
        if current is None or type(current) is bool:
            continue
        if type(current) is int:
            if not allow_oversized_integers and current.bit_length() > 64:
                raise RegistryError("registry.resource_limit")
            continue
        if isinstance(current, str):
            try:
                string_bytes += len(current.encode("utf-8", "strict"))
            except UnicodeEncodeError as exc:
                raise RegistryError("registry.normalization_failure") from exc
            if string_bytes > LIMITS["canonical_string_bytes"]:
                raise RegistryError("registry.resource_limit")
            continue
        if isinstance(current, list):
            if id(current) in seen_containers:
                raise RegistryError("registry.normalization_failure")
            seen_containers.add(id(current))
            stack.extend((item, depth + 1) for item in reversed(current))
            continue
        if isinstance(current, dict):
            if id(current) in seen_containers:
                raise RegistryError("registry.normalization_failure")
            seen_containers.add(id(current))
            for key, item in reversed(list(current.items())):
                if not isinstance(key, str):
                    raise RegistryError("registry.normalization_failure")
                stack.append((item, depth + 1))
                stack.append((key, depth + 1))
            continue
        raise RegistryError("registry.normalization_failure")


def canonical_json(value: Any) -> bytes:
    _validate_json_shape(value)
    return _encode_json(value)


def retained_evidence_json(value: Any) -> bytes:
    """Encode bounded retained evidence, including deliberately invalid integers."""
    _validate_json_shape(value, allow_oversized_integers=True)
    return _encode_json(value)


def _encode_json(value: Any) -> bytes:
    try:
        return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8", "strict")
    except (RecursionError, UnicodeEncodeError, UnicodeDecodeError) as exc:
        raise RegistryError("registry.normalization_failure") from exc


def _head(major: int, value: int) -> bytes:
    if not 0 <= value <= 0xFFFF_FFFF_FFFF_FFFF:
        raise RegistryError("registry.resource_limit")
    if value < 24:
        return bytes([(major << 5) | value])
    if value <= 0xFF:
        return bytes([(major << 5) | 24, value])
    if value <= 0xFFFF:
        return bytes([(major << 5) | 25]) + struct.pack(">H", value)
    if value <= 0xFFFF_FFFF:
        return bytes([(major << 5) | 26]) + struct.pack(">I", value)
    return bytes([(major << 5) | 27]) + struct.pack(">Q", value)


def canonical_cbor(value: Any, *, _depth: int = 0, _state: list[int] | None = None) -> bytes:
    """Encode the v0 arrays/maps/atoms with RFC-0001 core ordering."""

    if _state is None:
        _state = [0, 0]
    if _depth > LIMITS["canonical_depth"]:
        raise RegistryError("registry.resource_limit")
    _state[0] += 1
    if _state[0] > LIMITS["canonical_nodes"]:
        raise RegistryError("registry.resource_limit")
    if value is None:
        out = b"\xf6"
    elif value is False:
        out = b"\xf4"
    elif value is True:
        out = b"\xf5"
    elif type(value) is int:
        out = _head(0, value) if value >= 0 else _head(1, -1 - value)
    elif isinstance(value, bytes):
        out = _head(2, len(value)) + value
    elif isinstance(value, str):
        try:
            raw = value.encode("utf-8", "strict")
        except UnicodeEncodeError as exc:
            raise RegistryError("registry.normalization_failure") from exc
        if len(raw) > LIMITS["string_bytes"]:
            raise RegistryError("registry.resource_limit")
        _state[1] += len(raw)
        if _state[1] > LIMITS["canonical_string_bytes"]:
            raise RegistryError("registry.resource_limit")
        out = _head(3, len(raw)) + raw
    elif isinstance(value, list):
        if len(value) > LIMITS["canonical_nodes"]:
            raise RegistryError("registry.resource_limit")
        parts = [canonical_cbor(item, _depth=_depth + 1, _state=_state) for item in value]
        out = _head(4, len(parts)) + b"".join(parts)
    elif isinstance(value, dict):
        if len(value) > LIMITS["registry_entries"] * 16:
            raise RegistryError("registry.resource_limit")
        entries: list[tuple[bytes, bytes]] = []
        for key, item in value.items():
            key_bytes = canonical_cbor(key, _depth=_depth + 1, _state=_state)
            item_bytes = canonical_cbor(item, _depth=_depth + 1, _state=_state)
            entries.append((key_bytes, item_bytes))
        entries.sort(key=lambda pair: pair[0])
        if len({key for key, _ in entries}) != len(entries):
            raise RegistryError("registry.malformed_record")
        out = _head(5, len(entries)) + b"".join(key + item for key, item in entries)
    else:
        raise RegistryError("registry.normalization_failure")
    if len(out) > LIMITS["object_bytes"]:
        raise RegistryError("registry.resource_limit")
    return out


def _lp(value: bytes) -> bytes:
    return struct.pack(">I", len(value)) + value


def digest_frame(kind: str, payload: bytes) -> tuple[bytes, str]:
    if kind not in PURPOSES or not payload or len(payload) > LIMITS["object_bytes"]:
        raise RegistryError("registry.resource_limit")
    purpose, object_class = PURPOSES[kind]
    components = (
        purpose.encode("ascii"),
        ALGORITHM_ID.encode("ascii"),
        PROFILE_ID.encode("ascii"),
        object_class.encode("ascii"),
        FRAMING_ID.encode("ascii"),
        payload,
    )
    frame = DIGEST_MAGIC + b"".join(_lp(component) for component in components)
    return frame, hashlib.sha256(frame).hexdigest()


def validate_level_parameters(value: Any) -> list[str]:
    if not isinstance(value, list):
        raise RegistryError("registry.normalization_failure")
    if len(value) > LIMITS["universe_arguments"]:
        raise RegistryError("registry.resource_limit")
    result = []
    for item in value:
        if not isinstance(item, str) or not item:
            raise RegistryError("registry.normalization_failure")
        try:
            raw = item.encode("utf-8", "strict")
        except UnicodeEncodeError as exc:
            raise RegistryError("registry.normalization_failure") from exc
        if len(raw) > LIMITS["name_segment_bytes"]:
            raise RegistryError("registry.resource_limit")
        result.append(item)
    if len(result) != len(set(result)):
        raise RegistryError("registry.normalization_failure")
    return result


def normalize_expr(expr: Any, *, level_params: list[str] | None = None) -> Any:
    """Validate the language-neutral structural expression grammar."""

    params = validate_level_parameters([] if level_params is None else level_params)
    nodes = 0
    string_bytes = 0

    def bounded_text(value: str, individual_limit: int) -> bytes:
        nonlocal string_bytes
        try:
            raw = value.encode("utf-8", "strict")
        except UnicodeEncodeError as exc:
            raise RegistryError("registry.normalization_failure") from exc
        if len(raw) > individual_limit:
            raise RegistryError("registry.resource_limit")
        string_bytes += len(raw)
        if string_bytes > LIMITS["aggregate_string_bytes"]:
            raise RegistryError("registry.resource_limit")
        return raw

    def level(value: Any, depth: int) -> Any:
        nonlocal nodes
        nodes += 1
        if nodes > LIMITS["expression_nodes"] or depth > LIMITS["level_depth"]:
            raise RegistryError("registry.resource_limit")
        if not isinstance(value, list) or not value or type(value[0]) is not int:
            raise RegistryError("registry.normalization_failure")
        tag = value[0]
        if tag == 0 and len(value) == 1:
            return [0]
        if tag == 1 and len(value) == 2:
            return [1, level(value[1], depth + 1)]
        if tag in (2, 3) and len(value) == 3:
            return [tag, level(value[1], depth + 1), level(value[2], depth + 1)]
        if tag == 4 and len(value) == 2 and type(value[1]) is int and 0 <= value[1] < len(params):
            return [4, value[1]]
        raise RegistryError("registry.normalization_failure")

    def name(value: Any) -> Any:
        if not isinstance(value, list) or not value:
            raise RegistryError("registry.normalization_failure")
        if len(value) > LIMITS["name_segments"]:
            raise RegistryError("registry.resource_limit")
        total = 0
        result = []
        for segment in value:
            if not isinstance(segment, list) or len(segment) != 2 or segment[0] not in (0, 1):
                raise RegistryError("registry.normalization_failure")
            if type(segment[0]) is not int:
                raise RegistryError("registry.normalization_failure")
            if segment[0] == 0:
                if not isinstance(segment[1], str):
                    raise RegistryError("registry.normalization_failure")
                raw = bounded_text(segment[1], LIMITS["name_segment_bytes"])
                total += len(raw)
            elif type(segment[1]) is not int or not 0 <= segment[1] <= 0xFFFF_FFFF_FFFF_FFFF:
                raise RegistryError("registry.normalization_failure")
            result.append(segment)
        if total > LIMITS["qualified_name_bytes"]:
            raise RegistryError("registry.resource_limit")
        return result

    def walk(value: Any, depth: int, bound: int) -> Any:
        nonlocal nodes
        nodes += 1
        if nodes > LIMITS["expression_nodes"] or depth > LIMITS["expression_depth"]:
            raise RegistryError("registry.resource_limit")
        if not isinstance(value, list) or not value or type(value[0]) is not int:
            raise RegistryError("registry.normalization_failure")
        tag = value[0]
        if tag == 0 and len(value) == 2 and type(value[1]) is int and 0 <= value[1] < bound:
            return value
        if tag == 1 and len(value) == 2:
            return [1, level(value[1], 0)]
        if tag == 2 and len(value) == 3 and isinstance(value[2], list):
            if len(value[2]) > LIMITS["universe_arguments"]:
                raise RegistryError("registry.resource_limit")
            return [2, name(value[1]), [level(item, 0) for item in value[2]]]
        if tag == 3 and len(value) == 3:
            return [3, walk(value[1], depth + 1, bound), walk(value[2], depth + 1, bound)]
        if tag in (4, 5) and len(value) == 4 and type(value[1]) is int and value[1] in (0, 1, 2, 3):
            return [tag, value[1], walk(value[2], depth + 1, bound), walk(value[3], depth + 1, bound + 1)]
        if tag == 6 and len(value) == 4:
            return [6, walk(value[1], depth + 1, bound), walk(value[2], depth + 1, bound), walk(value[3], depth + 1, bound + 1)]
        if tag == 7 and len(value) == 2 and type(value[1]) is int and 0 <= value[1] <= 0xFFFF_FFFF_FFFF_FFFF:
            return value
        if tag == 8 and len(value) == 2 and isinstance(value[1], str):
            bounded_text(value[1], LIMITS["string_bytes"])
            return value
        if tag == 9 and len(value) == 4 and type(value[2]) is int and 0 <= value[2] <= 0xFFFF_FFFF_FFFF_FFFF:
            return [9, name(value[1]), value[2], walk(value[3], depth + 1, bound)]
        raise RegistryError("registry.normalization_failure")

    return walk(expr, 0, 0)


def closure(root_names: list[str], declarations: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Compute the bounded deterministic fixture closure."""

    if not isinstance(root_names, list) or not isinstance(declarations, dict):
        raise RegistryError("registry.normalization_failure")
    if len(root_names) > LIMITS["closure_width"]:
        raise RegistryError("registry.closure_width_limit")
    gray: set[str] = set()
    done: dict[str, dict[str, Any]] = {}
    work = 0

    def name_key(name: str) -> bytes:
        if not isinstance(name, str) or not name or any(not part for part in name.split(".")):
            raise RegistryError("registry.normalization_failure")
        parts = name.split(".")
        if len(parts) > LIMITS["name_segments"]:
            raise RegistryError("registry.resource_limit")
        total = 0
        for part in parts:
            try:
                raw = part.encode("utf-8", "strict")
            except UnicodeEncodeError as exc:
                raise RegistryError("registry.normalization_failure") from exc
            if len(raw) > LIMITS["name_segment_bytes"]:
                raise RegistryError("registry.resource_limit")
            total += len(raw)
        if total > LIMITS["qualified_name_bytes"]:
            raise RegistryError("registry.resource_limit")
        return canonical_cbor([[0, part] for part in parts])

    def declaration_payload(declaration: dict[str, Any]) -> dict[str, Any]:
        kind = declaration.get("kind")
        if kind == "definition" and isinstance(declaration.get("value"), str):
            try:
                raw = declaration["value"].encode("utf-8", "strict")
            except UnicodeEncodeError as exc:
                raise RegistryError("registry.normalization_failure") from exc
            if len(raw) > LIMITS["string_bytes"]:
                raise RegistryError("registry.resource_limit")
        if kind == "definition" and set(declaration) in (
            {"kind", "references"},
            {"kind", "references", "value"},
        ):
            payload = {"kind": kind}
            if "value" in declaration:
                if not isinstance(declaration["value"], str):
                    raise RegistryError("registry.normalization_failure")
                payload["value"] = declaration["value"]
            return payload
        if kind == "inductive_family" and set(declaration) == {"kind", "references"}:
            return {"kind": kind}
        raise RegistryError("registry.normalization_failure")

    def visit(name: str, depth: int) -> None:
        nonlocal work
        work += 1
        if work > LIMITS["work"]:
            raise RegistryError("registry.closure_work_budget_limit")
        if depth > LIMITS["closure_depth"]:
            raise RegistryError("registry.closure_depth_limit")
        if name in done:
            return
        if name in gray:
            raise RegistryError("registry.closure_cycle")
        if len(done) + len(gray) >= LIMITS["closure_units"]:
            raise RegistryError("registry.closure_work_budget_limit")
        if name not in declarations:
            raise RegistryError("registry.missing_dependency")
        declaration = declarations[name]
        if not isinstance(declaration, dict):
            raise RegistryError("registry.normalization_failure")
        refs = declaration.get("references")
        # Resource ownership precedes closed-record schema ownership when the
        # references container is present and already over the published cap.
        if isinstance(refs, list) and len(refs) > LIMITS["closure_width"]:
            raise RegistryError("registry.closure_width_limit")
        payload = declaration_payload(declaration)
        if not isinstance(refs, list):
            raise RegistryError("registry.normalization_failure")
        gray.add(name)
        for reference in sorted(refs, key=name_key):
            if not isinstance(reference, str):
                raise RegistryError("registry.normalization_failure")
            visit(reference, depth + 1)
        gray.remove(name)
        done[name] = payload

    for root in sorted(root_names, key=name_key):
        visit(root, 0)
    return [dict(name=name, **done[name]) for name in sorted(done, key=name_key)]


def validate_identifier(value: Any) -> str:
    if not isinstance(value, str):
        raise RegistryError("registry.malformed_record")
    try:
        utf8 = value.encode("utf-8", "strict")
    except UnicodeEncodeError as exc:
        raise RegistryError("registry.malformed_record") from exc
    if len(utf8) > LIMITS["identifier_bytes"]:
        raise RegistryError("registry.resource_limit")
    try:
        encoded = value.encode("ascii", "strict")
    except UnicodeEncodeError as exc:
        raise RegistryError("registry.malformed_record") from exc
    if not _IDENTIFIER.fullmatch(value):
        raise RegistryError("registry.malformed_record")
    return value


def _utf8_length(value: Any) -> int | None:
    if not isinstance(value, str):
        return None
    try:
        return len(value.encode("utf-8", "strict"))
    except UnicodeEncodeError:
        return None


def _verify_bundle_resource_preflight(bundle: dict[str, Any], policy: dict[str, Any]) -> None:
    """Enforce observable v0 resource caps before lower-precedence errors.

    This pass deliberately inspects only fields whose container types make the
    applicable bound unambiguous. Shape and syntax errors remain owned by the
    normal validation pass when no resource boundary has already been crossed.
    """

    for root in (bundle, policy):
        stack: list[tuple[Any, int]] = [(root, 0)]
        seen_containers: set[int] = set()
        nodes = 0
        while stack:
            value, depth = stack.pop()
            nodes += 1
            if nodes > LIMITS["canonical_nodes"] or depth > LIMITS["canonical_depth"]:
                raise RegistryError("registry.resource_limit")
            if isinstance(value, str):
                length = _utf8_length(value)
                if length is not None and length > LIMITS["string_bytes"]:
                    raise RegistryError("registry.resource_limit")
            elif isinstance(value, list):
                if id(value) in seen_containers:
                    continue
                seen_containers.add(id(value))
                stack.extend((item, depth + 1) for item in value)
            elif isinstance(value, dict):
                if id(value) in seen_containers:
                    continue
                seen_containers.add(id(value))
                stack.extend((item, depth + 1) for item in value.keys())
                stack.extend((item, depth + 1) for item in value.values())

    root_fields = (
        "current_permitted_roots",
        "historical_permitted_roots",
        "historical_forbidden_roots",
        "revoked_roots",
    )
    root_lists = [policy.get(field) for field in root_fields]
    if (
        sum(len(values) for values in root_lists if isinstance(values, list))
        > LIMITS["registry_entries"]
    ):
        raise RegistryError("registry.resource_limit")

    record = bundle.get("record")
    if isinstance(record, dict):
        identifier_length = _utf8_length(record.get("id"))
        if identifier_length is not None and identifier_length > LIMITS["identifier_bytes"]:
            raise RegistryError("registry.resource_limit")

    snapshot = bundle.get("snapshot")
    if isinstance(snapshot, dict):
        records = snapshot.get("records")
        if isinstance(records, list) and len(records) > LIMITS["registry_entries"]:
            raise RegistryError("registry.resource_limit")

    axioms = bundle.get("axioms")
    if isinstance(axioms, list) and len(axioms) > LIMITS["axioms"]:
        raise RegistryError("registry.resource_limit")


def _compatibility_lock_digest(value: Any, old_proposition_digest: Any) -> str:
    """Validate one closed compatibility lock and return its framed digest."""

    if not isinstance(value, dict):
        raise RegistryError("registry.compatibility_missing")
    expected_fields = {
        "schema", "direction", "new_proposition", "new_proposition_digest",
        "old_proposition_digest", "environment_digest", "declaration",
        "normalized_type", "proof_subject", "proof_build_digest",
        "axiom_report_digest", "axioms", "universe_instantiations", "path_length",
    }
    if set(value) != expected_fields:
        raise RegistryError("registry.compatibility_missing")
    if value.get("direction") != "new_implies_old":
        raise RegistryError("registry.compatibility_wrong_direction")
    if value.get("schema") != "statqed.compatibility-proof-lock.v0":
        raise RegistryError("registry.compatibility_missing")
    if value.get("old_proposition_digest") != old_proposition_digest:
        raise RegistryError("registry.compatibility_missing")
    if value.get("declaration") != "StatQED.Registry.Tests.falseImpliesTrue":
        raise RegistryError("registry.compatibility_missing")
    if value.get("new_proposition") != "False":
        raise RegistryError("registry.compatibility_missing")
    if (
        value.get("axioms") != []
        or type(value.get("path_length")) is not int
        or value["path_length"] != 1
    ):
        raise RegistryError("registry.compatibility_missing")
    if value.get("universe_instantiations") != {"new": [], "old": []}:
        raise RegistryError("registry.compatibility_missing")
    expected_type = [
        5,
        0,
        [2, [[0, "False"]], []],
        [2, [[0, "True"]], []],
    ]
    expected_proof_subject = [
        4,
        0,
        [2, [[0, "False"]], []],
        [
            3,
            [
                3,
                [2, [[0, "False"], [0, "elim"]], [[0]]],
                [2, [[0, "True"]], []],
            ],
            [0, 0],
        ],
    ]
    try:
        normalized_type = normalize_expr(value.get("normalized_type"))
        normalized_proof = normalize_expr(value.get("proof_subject"))
    except RegistryError as error:
        raise RegistryError("registry.compatibility_missing") from error
    # Python's bool is an int subclass, so compare canonical typed bytes rather
    # than native lists. The v0 lock is deliberately limited to the one live,
    # kernel-checked False -> True fixture and its reviewed proof subject.
    if canonical_cbor(normalized_type) != canonical_cbor(expected_type):
        raise RegistryError("registry.compatibility_missing")
    if canonical_cbor(normalized_proof) != canonical_cbor(expected_proof_subject):
        raise RegistryError("registry.compatibility_missing")
    for field in (
        "new_proposition_digest", "old_proposition_digest", "environment_digest",
        "proof_build_digest", "axiom_report_digest",
    ):
        if re.fullmatch(r"[0-9a-f]{64}", str(value.get(field))) is None:
            raise RegistryError("registry.compatibility_missing")
    _, digest = digest_frame("compatibility", canonical_cbor(value))
    return digest


def verify_bundle(bundle: dict[str, Any], policy: dict[str, Any]) -> dict[str, str]:
    """Resolve one test-only record under independently supplied local policy."""

    if not isinstance(bundle, dict):
        raise RegistryError("registry.malformed_record")
    if not isinstance(policy, dict):
        raise RegistryError("registry.authorization_policy_unsupported")
    expected_bundle_fields = {
        "record", "record_digest", "snapshot", "requested_root",
        "proposition_digest", "environment_digest", "proof_build_digest",
        "axioms", "compatibility", "compatibility_digest",
    }
    _verify_bundle_resource_preflight(bundle, policy)
    if len(canonical_json(bundle)) > LIMITS["input_bytes"]:
        raise RegistryError("registry.resource_limit")
    if len(canonical_json(policy)) > LIMITS["input_bytes"]:
        raise RegistryError("registry.resource_limit")
    if set(bundle) - (expected_bundle_fields | {"candidate_policy"}) or not expected_bundle_fields.issubset(bundle):
        raise RegistryError("registry.malformed_record")
    candidate_digest_fields = (
        "record_digest", "requested_root", "proposition_digest",
        "environment_digest", "proof_build_digest", "compatibility_digest",
    )
    if any(
        not isinstance(bundle.get(field), str)
        or re.fullmatch(r"[0-9a-f]{64}", bundle[field]) is None
        for field in candidate_digest_fields
    ):
        raise RegistryError("registry.malformed_record")
    record = bundle.get("record")
    snapshot = bundle.get("snapshot")
    if not isinstance(record, dict) or not isinstance(snapshot, dict):
        raise RegistryError("registry.malformed_record")
    expected_record_fields = {
        "schema", "id", "version", "declaration", "normalizer", "closure",
        "proposition_digest", "environment_digest", "proof_build_digest",
        "axiom_report_digest", "maturity", "exposure", "source_anchor",
        "attribution", "nonclaims",
    }
    if set(record) != expected_record_fields:
        raise RegistryError("registry.malformed_record")
    record_text_fields = expected_record_fields - {"nonclaims"}
    if any(not isinstance(record.get(field), str) for field in record_text_fields):
        raise RegistryError("registry.malformed_record")
    if not isinstance(record.get("nonclaims"), list) or any(
        not isinstance(item, str) for item in record["nonclaims"]
    ):
        raise RegistryError("registry.malformed_record")
    for digest_field in (
        "proposition_digest", "environment_digest", "proof_build_digest",
        "axiom_report_digest",
    ):
        if re.fullmatch(r"[0-9a-f]{64}", record[digest_field]) is None:
            raise RegistryError("registry.malformed_record")
    if set(snapshot) != {"schema", "records"} or not isinstance(snapshot.get("records"), list):
        raise RegistryError("registry.malformed_record")
    if len(snapshot["records"]) > LIMITS["registry_entries"]:
        raise RegistryError("registry.resource_limit")
    if len(snapshot["records"]) != 1:
        raise RegistryError("registry.malformed_record")
    entry = snapshot["records"][0]
    if (
        not isinstance(snapshot.get("schema"), str)
        or not isinstance(entry, list)
        or len(entry) != 3
        or any(not isinstance(item, str) for item in entry)
        or re.fullmatch(r"[0-9a-f]{64}", entry[2]) is None
    ):
        raise RegistryError("registry.malformed_record")
    if record["schema"] != "statqed.registry-record.v0":
        raise RegistryError("registry.version_unsupported")
    if snapshot["schema"] != "statqed.registry-snapshot.v0":
        raise RegistryError("registry.version_unsupported")
    if validate_identifier(record["id"]) != "statqed.test-only.foundation.true.v0":
        raise RegistryError("registry.record_digest_mismatch")
    if record["maturity"] != "Experimental" or record["exposure"] != "test_only":
        raise RegistryError("registry.record_digest_mismatch")
    record_bytes = canonical_cbor(record)
    _, actual_record_digest = digest_frame("record", record_bytes)
    if actual_record_digest != bundle.get("record_digest"):
        raise RegistryError("registry.record_digest_mismatch")
    snapshot_bytes = canonical_cbor(snapshot)
    _, root = digest_frame("snapshot", snapshot_bytes)
    requested = bundle.get("requested_root")
    if requested != root:
        raise RegistryError("registry.authorization_root_mismatch")

    expected_policy_fields = {
        "schema", "policy_version", "current_permitted_roots",
        "historical_permitted_roots", "historical_forbidden_roots",
        "revoked_roots", "compatibility_digest", "record_binding",
        "compatibility_binding", "record_digest", "selection",
    }
    if (
        set(policy) != expected_policy_fields
        or policy.get("schema") != "statqed.registry-authorization-policy.v0"
        or policy.get("selection") != "verifier_local_only"
        or policy.get("policy_version") != "statqed.registry-authorization.v0"
    ):
        raise RegistryError("registry.authorization_policy_unsupported")
    root_classes = []
    for field in (
        "current_permitted_roots",
        "historical_permitted_roots",
        "historical_forbidden_roots",
        "revoked_roots",
    ):
        values = policy.get(field)
        if not isinstance(values, list) or any(
            not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None
            for value in values
        ):
            raise RegistryError("registry.authorization_policy_unsupported")
        if len(values) != len(set(values)):
            raise RegistryError("registry.authorization_policy_unsupported")
        root_classes.append(set(values))
    for digest_field in ("record_digest", "compatibility_digest"):
        if (
            not isinstance(policy.get(digest_field), str)
            or re.fullmatch(r"[0-9a-f]{64}", policy[digest_field]) is None
        ):
            raise RegistryError("registry.authorization_policy_unsupported")
    for index, left in enumerate(root_classes):
        if any(left & right for right in root_classes[index + 1 :]):
            raise RegistryError("registry.authorization_policy_unsupported")

    # A locally permitted snapshot root is an authorization selector, not a
    # license for a candidate to redefine the reviewed record.  Bind the full
    # closed record and its digest in verifier-selected policy so that
    # re-authorizing a self-consistent forged snapshot cannot change either
    # mechanically extracted or governed fields.
    if (
        policy.get("record_digest") != actual_record_digest
        or policy.get("record_binding") != record
    ):
        raise RegistryError("registry.record_digest_mismatch")
    current, historical, forbidden, revoked = root_classes
    if root in revoked:
        raise RegistryError("registry.authorization_root_revoked")
    if root in forbidden:
        raise RegistryError("registry.authorization_root_historical_forbidden")
    if root not in current and root not in historical:
        raise RegistryError("registry.authorization_root_unknown")
    if snapshot != {"schema": "statqed.registry-snapshot.v0", "records": [[record["id"], record["version"], actual_record_digest]]}:
        raise RegistryError("registry.authorization_root_mismatch")
    for key, code in (
        ("proposition_digest", "registry.statement_digest_mismatch"),
        ("environment_digest", "registry.environment_mismatch"),
        ("proof_build_digest", "registry.proof_build_lock_mismatch"),
    ):
        if record[key] != bundle.get(key):
            raise RegistryError(code)
    axioms = bundle.get("axioms")
    if not isinstance(axioms, list):
        raise RegistryError("registry.proof_build_lock_mismatch")
    if len(axioms) > LIMITS["axioms"]:
        raise RegistryError("registry.resource_limit")
    if axioms:
        raise RegistryError("registry.forbidden_axiom")
    # The verifier-selected compatibility lock is authenticated even when the
    # candidate does not request a compatibility edge.  Candidate null is the
    # Python representation of Rust's zero-edge path; it does not make the
    # required digest or trusted policy binding optional.
    policy_compatibility = policy.get("compatibility_binding")
    try:
        compatibility_digest = _compatibility_lock_digest(
            policy_compatibility, bundle.get("proposition_digest")
        )
    except RegistryError as error:
        raise RegistryError("registry.authorization_policy_unsupported") from error
    if compatibility_digest != policy.get("compatibility_digest"):
        raise RegistryError("registry.authorization_policy_unsupported")
    compatibility = bundle.get("compatibility")
    if compatibility is not None:
        candidate_digest = _compatibility_lock_digest(
            compatibility, bundle.get("proposition_digest")
        )
        if (
            candidate_digest != bundle.get("compatibility_digest")
            or candidate_digest != compatibility_digest
            or compatibility != policy_compatibility
        ):
            raise RegistryError("registry.compatibility_missing")
    elif compatibility_digest != bundle.get("compatibility_digest"):
        raise RegistryError("registry.compatibility_missing")
    return {"classification": "accepted", "root_status": "current" if root in current else "historical_permitted"}
