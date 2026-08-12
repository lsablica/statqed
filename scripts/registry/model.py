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
}

_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$")


@dataclass
class RegistryError(Exception):
    code: str

    def __post_init__(self) -> None:
        if self.code not in ERRORS:
            raise ValueError(f"unknown stable error: {self.code}")


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


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
    # The expression grammar has its own exact depth bound.  Canonical payload
    # containers add a small fixed envelope around that already-validated
    # expression, so the generic encoder permits only that explicit overhead.
    if _depth > LIMITS["expression_depth"] + 8:
        raise RegistryError("registry.resource_limit")
    _state[0] += 1
    if _state[0] > LIMITS["expression_nodes"]:
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
        raw = value.encode("utf-8", "strict")
        if len(raw) > LIMITS["string_bytes"]:
            raise RegistryError("registry.resource_limit")
        _state[1] += len(raw)
        if _state[1] > LIMITS["aggregate_string_bytes"]:
            raise RegistryError("registry.resource_limit")
        out = _head(3, len(raw)) + raw
    elif isinstance(value, list):
        if len(value) > LIMITS["expression_nodes"]:
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


def normalize_expr(expr: Any, *, level_params: list[str] | None = None) -> Any:
    """Validate the language-neutral structural expression grammar."""

    params = level_params or []
    nodes = 0

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
            if segment[0] == 0:
                if not isinstance(segment[1], str):
                    raise RegistryError("registry.normalization_failure")
                raw = segment[1].encode("utf-8", "strict")
                if len(raw) > LIMITS["name_segment_bytes"]:
                    raise RegistryError("registry.resource_limit")
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
        if tag in (4, 5) and len(value) == 4 and value[1] in (0, 1, 2, 3):
            return [tag, value[1], walk(value[2], depth + 1, bound), walk(value[3], depth + 1, bound + 1)]
        if tag == 6 and len(value) == 4:
            return [6, walk(value[1], depth + 1, bound), walk(value[2], depth + 1, bound), walk(value[3], depth + 1, bound + 1)]
        if tag == 7 and len(value) == 2 and type(value[1]) is int and value[1] >= 0:
            return value
        if tag == 8 and len(value) == 2 and isinstance(value[1], str):
            return value
        if tag == 9 and len(value) == 4 and type(value[2]) is int and value[2] >= 0:
            return [9, name(value[1]), value[2], walk(value[3], depth + 1, bound)]
        raise RegistryError("registry.normalization_failure")

    return walk(expr, 0, 0)


def closure(root_names: list[str], declarations: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Compute the bounded deterministic fixture closure."""

    if len(root_names) > LIMITS["closure_width"]:
        raise RegistryError("registry.closure_width_limit")
    gray: set[str] = set()
    done: dict[str, dict[str, Any]] = {}
    work = 0

    def name_key(name: str) -> bytes:
        if not isinstance(name, str) or not name or any(not part for part in name.split(".")):
            raise RegistryError("registry.normalization_failure")
        return canonical_cbor([[0, part] for part in name.split(".")])

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
        declaration = declarations.get(name)
        if declaration is None:
            raise RegistryError("registry.missing_dependency")
        refs = declaration.get("references")
        if not isinstance(refs, list) or len(refs) > LIMITS["closure_width"]:
            raise RegistryError("registry.closure_width_limit")
        gray.add(name)
        for reference in sorted(refs, key=name_key):
            if not isinstance(reference, str):
                raise RegistryError("registry.normalization_failure")
            visit(reference, depth + 1)
        gray.remove(name)
        done[name] = {key: value for key, value in declaration.items() if key != "references"}

    for root in sorted(root_names, key=name_key):
        visit(root, 0)
    return [dict(name=name, **done[name]) for name in sorted(done, key=name_key)]


def validate_identifier(value: Any) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise RegistryError("registry.malformed_record")
    return value


def verify_bundle(bundle: dict[str, Any], policy: dict[str, Any]) -> dict[str, str]:
    """Resolve one test-only record under independently supplied local policy."""

    if len(canonical_json(bundle)) > LIMITS["input_bytes"]:
        raise RegistryError("registry.resource_limit")
    if policy.get("policy_version") != "statqed.registry-authorization.v0":
        raise RegistryError("registry.authorization_policy_unsupported")
    root_classes = []
    for field in (
        "current_permitted_roots",
        "historical_permitted_roots",
        "historical_forbidden_roots",
        "revoked_roots",
    ):
        values = policy.get(field)
        if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
            raise RegistryError("registry.authorization_policy_unsupported")
        if len(values) != len(set(values)):
            raise RegistryError("registry.authorization_policy_unsupported")
        root_classes.append(set(values))
    for index, left in enumerate(root_classes):
        if any(left & right for right in root_classes[index + 1 :]):
            raise RegistryError("registry.authorization_policy_unsupported")
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
    if record["schema"] != "statqed.registry-record.v0":
        raise RegistryError("registry.version_unsupported")
    if validate_identifier(record["id"]) != "statqed.test-only.foundation.true.v0":
        raise RegistryError("registry.record_digest_mismatch")
    if record["maturity"] != "Experimental" or record["exposure"] != "test_only":
        raise RegistryError("registry.record_digest_mismatch")
    record_bytes = canonical_cbor(record)
    _, actual_record_digest = digest_frame("record", record_bytes)
    if actual_record_digest != bundle.get("record_digest"):
        raise RegistryError("registry.record_digest_mismatch")
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
    snapshot_bytes = canonical_cbor(snapshot)
    _, root = digest_frame("snapshot", snapshot_bytes)
    requested = bundle.get("requested_root")
    if requested != root:
        raise RegistryError("registry.authorization_root_mismatch")
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
    if not isinstance(axioms, list) or len(axioms) > LIMITS["axioms"]:
        raise RegistryError("registry.proof_build_lock_mismatch")
    if axioms:
        raise RegistryError("registry.forbidden_axiom")
    compatibility = bundle.get("compatibility")
    if compatibility is not None:
        if not isinstance(compatibility, dict):
            raise RegistryError("registry.compatibility_missing")
        if compatibility.get("direction") != "new_implies_old":
            raise RegistryError("registry.compatibility_wrong_direction")
        if compatibility.get("schema") != "statqed.compatibility-proof-lock.v0":
            raise RegistryError("registry.compatibility_missing")
        if compatibility.get("old_proposition_digest") != bundle.get("proposition_digest"):
            raise RegistryError("registry.compatibility_missing")
        if compatibility.get("declaration") != "StatQED.Registry.Tests.falseImpliesTrue":
            raise RegistryError("registry.compatibility_missing")
        if compatibility.get("axioms") != [] or compatibility.get("path_length") != 1:
            raise RegistryError("registry.compatibility_missing")
        _, compatibility_digest = digest_frame(
            "compatibility", canonical_cbor(compatibility)
        )
        if (
            compatibility_digest != bundle.get("compatibility_digest")
            or compatibility_digest != policy.get("compatibility_digest")
        ):
            raise RegistryError("registry.compatibility_missing")
    return {"classification": "accepted", "root_status": "current" if root in current else "historical_permitted"}
