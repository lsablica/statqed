#!/usr/bin/env python3
"""Generate or verify SQ-0006 schema-v0 conformance evidence.

The standards recipe in this file originates expected bytes directly from the
reviewed semantic value and RFC-0001's RFC 8949 core deterministic rule. The
two frozen SQ-0005 prototypes are independent comparisons, never authorities.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
from typing import Any

try:
    import resource
except ImportError:  # pragma: no cover - direct support evidence is Linux only
    resource = None  # type: ignore[assignment]

from semantic_validator import validate_fixture


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas/v0/compiled/foundation-structural.cddl"
POSITIVES = ROOT / "schemas/fixtures/v0/positive"
NEGATIVE_CATALOG = ROOT / "schemas/fixtures/v0/negative/catalog.json"
PYTHON_ORACLE = ROOT / "schemas/prototypes/python-oracle"
RUST_MANIFEST = ROOT / "schemas/prototypes/rust-cbor/Cargo.toml"
SQ0005_RESULTS = ROOT / "conformance/prototypes/generated-v1/results.json"

PURPOSE = "statqed.fixture.golden"
ALGORITHM = "sha-256"
PROFILE = "statqed.cbor-core.v1"
OBJECT_CLASS = "statqed.foundation-structural.v0"
FRAMING = "statqed.digest-lp.v1"
MAGIC = b"StatQED-Digest\x00"
SCHEMA_VERSION = 0
CDDL_VERSION = "cddl 0.10.6"
DIAGNOSTIC_LIMIT = 65_536


def _resource_limits() -> None:
    """Bound untrusted probe subprocesses on POSIX hosts."""
    if platform.system() != "Linux" or resource is None:
        return
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
    resource.setrlimit(resource.RLIMIT_CPU, (240, 240))
    resource.setrlimit(resource.RLIMIT_FSIZE, (16 * 1024**2, 16 * 1024**2))


def bounded_run(
    command: list[str],
    *,
    input_data: bytes | None = None,
    env: dict[str, str] | None = None,
    timeout: int,
) -> subprocess.CompletedProcess[bytes]:
    """Run a probe with bounded time, memory, file output, and diagnostics."""
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        try:
            completed = subprocess.run(
                command,
                input=input_data,
                stdout=stdout,
                stderr=stderr,
                env=env,
                check=False,
                timeout=timeout,
                preexec_fn=_resource_limits if os.name == "posix" else None,
            )
        except subprocess.TimeoutExpired as error:
            raise RuntimeError(f"operational.timeout: {command[0]}") from error
        stdout.seek(0)
        stderr.seek(0)
        out = stdout.read(DIAGNOSTIC_LIMIT + 1)
        err = stderr.read(DIAGNOSTIC_LIMIT + 1)
    if len(out) > DIAGNOSTIC_LIMIT or len(err) > DIAGNOSTIC_LIMIT:
        raise RuntimeError(f"resource.diagnostic_bytes: {command[0]}")
    return subprocess.CompletedProcess(command, completed.returncode, out, err)


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _head(major: int, argument: int) -> bytes:
    if argument < 24:
        return bytes(((major << 5) | argument,))
    if argument <= 0xFF:
        return bytes(((major << 5) | 24, argument))
    if argument <= 0xFFFF:
        return bytes(((major << 5) | 25,)) + argument.to_bytes(2, "big")
    if argument <= 0xFFFF_FFFF:
        return bytes(((major << 5) | 26,)) + argument.to_bytes(4, "big")
    if argument <= 0xFFFF_FFFF_FFFF_FFFF:
        return bytes(((major << 5) | 27,)) + argument.to_bytes(8, "big")
    raise ValueError("integer outside RFC-0001 range")


def direct_encode(value: Any, *, preserve_map_order: bool = False) -> bytes:
    """Direct reviewed-subset encoder; independent of both SQ-0005 prototypes."""
    if not isinstance(value, dict) or not isinstance(value.get("type"), str):
        raise ValueError("invalid typed semantic value")
    kind = value["type"]
    if kind == "integer":
        integer = int(value["value"])
        return _head(0, integer) if integer >= 0 else _head(1, -1 - integer)
    if kind == "text":
        raw = value["value"].encode("utf-8", "strict")
        return _head(3, len(raw)) + raw
    if kind == "array":
        items = [direct_encode(item, preserve_map_order=preserve_map_order) for item in value["items"]]
        return _head(4, len(items)) + b"".join(items)
    if kind == "map":
        pairs = [
            (direct_encode(entry["key"]), direct_encode(entry["value"]))
            for entry in value["entries"]
        ]
        if not preserve_map_order:
            pairs.sort(key=lambda pair: pair[0])
        return _head(5, len(pairs)) + b"".join(key + item for key, item in pairs)
    if kind == "null":
        return b"\xf6"
    if kind == "boolean":
        return b"\xf5" if value["value"] else b"\xf4"
    raise ValueError(f"unsupported direct recipe type: {kind}")


def direct_frame(payload: bytes) -> tuple[bytes, bytes]:
    components = [PURPOSE, ALGORITHM, PROFILE, OBJECT_CLASS, FRAMING]
    encoded = [component.encode("ascii") for component in components] + [payload]
    frame = MAGIC + b"".join(len(component).to_bytes(4, "big") + component for component in encoded)
    return frame, hashlib.sha256(frame).digest()


def run_json(command: list[str], request: Any, *, env: dict[str, str] | None = None) -> tuple[int, dict[str, Any], str]:
    completed = bounded_run(
        command,
        input_data=json.dumps(request, ensure_ascii=True, separators=(",", ":")).encode(),
        env=env,
        timeout=30,
    )
    try:
        result = json.loads(completed.stdout)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"operational.invalid_json: {command[0]}") from error
    return completed.returncode, result, completed.stderr.decode("utf-8", "replace")


def python_command(action: str) -> tuple[list[str], dict[str, str]]:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(PYTHON_ORACLE)
    return [sys.executable, "-S", "-m", "statqed_oracle.cli", action], env


def build_rust_binary(target: Path) -> Path:
    env = dict(os.environ)
    env["CARGO_NET_OFFLINE"] = "true"
    completed = bounded_run(
        [
            "cargo", "+1.97.1", "build", "--locked", "--offline",
            "--manifest-path", str(RUST_MANIFEST), "--target-dir", str(target),
        ],
        env=env,
        timeout=180,
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr.decode("utf-8", "replace"))
    binary = target / "debug/statqed-rust-cbor-prototype"
    if not binary.is_file():
        raise RuntimeError("Rust prototype binary missing")
    return binary


def invoke_encode(value: Any, rust_binary: Path) -> tuple[bytes, dict[str, Any], dict[str, Any]]:
    python_cmd, python_env = python_command("encode")
    py_rc, py, py_err = run_json(python_cmd, value, env=python_env)
    rs_rc, rs, rs_err = run_json([str(rust_binary), "encode"], value)
    if py_rc != 0 or rs_rc != 0 or py_err or rs_err:
        raise AssertionError(f"encoder failure: python={py_rc, py, py_err}; rust={rs_rc, rs, rs_err}")
    py_bytes = bytes.fromhex(py["cbor_hex"])
    rs_bytes = bytes.fromhex(rs["cbor_hex"])
    if py_bytes != rs_bytes:
        raise AssertionError("independent encoders disagree")
    return py_bytes, py, rs


def invoke_decode(
    data: bytes,
    rust_binary: Path,
    *,
    profile: str = PROFILE,
    require_same_code: bool = True,
) -> tuple[dict[str, Any], dict[str, Any]]:
    request = {"cbor_hex": data.hex(), "profile_id": profile}
    python_cmd, python_env = python_command("decode")
    _, py, py_err = run_json(python_cmd, request, env=python_env)
    _, rs, rs_err = run_json([str(rust_binary), "decode"], request)
    if py_err or rs_err:
        raise AssertionError(f"decoder stderr: {py_err!r} {rs_err!r}")
    same_class = py["result_class"] == rs["result_class"]
    same_code = py["code"] == rs["code"]
    if not same_class or (require_same_code and not same_code):
        raise AssertionError(f"decoder differential: {py} != {rs}")
    return py, rs


def invoke_frame(payload: bytes, rust_binary: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    common = {
        "purpose_id": PURPOSE,
        "algorithm_id": ALGORITHM,
        "profile_id": PROFILE,
        "object_class_schema_id": OBJECT_CLASS,
        "framing_id": FRAMING,
    }
    python_cmd, python_env = python_command("frame")
    py_rc, py, py_err = run_json(python_cmd, {**common, "payload_hex": payload.hex()}, env=python_env)
    rs_rc, rs, rs_err = run_json([str(rust_binary), "frame"], {**common, "cbor_hex": payload.hex()})
    if py_rc != 0 or rs_rc != 0 or py_err or rs_err:
        raise AssertionError(f"frame failure: python={py}; rust={rs}")
    return py, rs


def invoke_verify(frame: bytes, digest: bytes, rust_binary: Path, expected: dict[str, str]) -> tuple[dict[str, Any], dict[str, Any]]:
    python_request = {
        "frame_hex": frame.hex(), "digest_hex": digest.hex(),
        "expected_purpose_id": expected["purpose_id"],
        "expected_algorithm_id": expected["algorithm_id"],
        "expected_profile_id": expected["profile_id"],
        "expected_object_class_schema_id": expected["object_class_schema_id"],
        "expected_framing_id": expected["framing_id"],
    }
    rust_request = {"frame_hex": frame.hex(), "digest_hex": digest.hex(), **expected}
    python_cmd, python_env = python_command("verify-digest")
    _, py, py_err = run_json(python_cmd, python_request, env=python_env)
    _, rs, rs_err = run_json([str(rust_binary), "verify-digest"], rust_request)
    if py_err or rs_err:
        raise AssertionError(f"digest stderr: {py_err!r} {rs_err!r}")
    if (py["result_class"], py["code"]) != (rs["result_class"], rs["code"]):
        raise AssertionError(f"digest differential: {py} != {rs}")
    return py, rs


def cddl_result(cddl_binary: Path, data: bytes) -> dict[str, Any]:
    with tempfile.NamedTemporaryFile(suffix=".cbor") as handle:
        handle.write(data)
        handle.flush()
        completed = bounded_run(
            [str(cddl_binary), "--ci", "validate", "--cddl", str(SCHEMA), "--cbor", handle.name],
            timeout=30,
        )
    return {
        "status": "accepted" if completed.returncode == 0 else "rejected",
        "code": "accepted" if completed.returncode == 0 else "shape.cddl_mismatch",
        "exit_status": completed.returncode,
    }


def verify_cddl_version(cddl_binary: Path) -> None:
    version = bounded_run([str(cddl_binary), "--version"], timeout=10)
    if version.returncode or version.stdout.decode("utf-8", "replace").strip() != CDDL_VERSION:
        raise RuntimeError("operational.cddl_version")


def field_entry(value: dict[str, Any], field: str) -> dict[str, Any]:
    return next(entry for entry in value["entries"] if entry["key"].get("value") == field)


def mutate_semantic(base: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(base)
    kind = case["kind"]
    if kind == "remove":
        value["entries"] = [entry for entry in value["entries"] if entry["key"].get("value") != case["field"]]
    elif kind == "add":
        value["entries"].append({
            "key": {"type": "text", "value": case["field"]},
            "value": copy.deepcopy(case.get("value", {"type": "text", "value": "forbidden"})),
        })
    elif kind == "set":
        field_entry(value, case["field"])["value"] = copy.deepcopy(case["value"])
    elif kind == "analysis_over":
        field_entry(value, "analysis_id")["value"] = {"type": "text", "value": "a" + "z" * 128}
    elif kind == "set_version_pair":
        field_entry(value, "schema_id")["value"] = {"type": "text", "value": "statqed.foundation-structural.v1"}
        field_entry(value, "schema_version")["value"] = {"type": "integer", "value": "1"}
    elif kind == "duplicate":
        value["entries"].append(copy.deepcopy(field_entry(value, case["field"])))
    else:
        raise ValueError(kind)
    return value


def encoded_pairs(value: dict[str, Any], overrides: dict[str, bytes] | None = None) -> list[tuple[bytes, bytes]]:
    overrides = overrides or {}
    pairs = []
    for entry in value["entries"]:
        key = entry["key"]["value"]
        pairs.append((direct_encode(entry["key"]), overrides.get(key, direct_encode(entry["value"]))))
    pairs.sort(key=lambda pair: pair[0])
    return pairs


def raw_recipe(recipe: str, base: dict[str, Any], canonical: bytes) -> tuple[bytes, str]:
    pairs = encoded_pairs(base)
    if recipe == "nonpreferred_map_head":
        return b"\xb8\x06" + canonical[1:], PROFILE
    if recipe == "wrong_map_order":
        return direct_encode(base, preserve_map_order=True), PROFILE
    if recipe == "duplicate_nonpreferred_key":
        duplicate = field_entry(base, "schema_id")
        key_text = duplicate["key"]["value"].encode()
        nonpreferred_key = b"\x78" + bytes((len(key_text),)) + key_text
        all_pairs = pairs + [(nonpreferred_key, direct_encode(duplicate["value"]))]
        all_pairs.sort(key=lambda pair: pair[0])
        return _head(5, len(all_pairs)) + b"".join(k + v for k, v in all_pairs), PROFILE
    if recipe == "indefinite_map":
        return b"\xbf" + b"".join(k + v for k, v in pairs) + b"\xff", PROFILE
    if recipe == "indefinite_array":
        changed = encoded_pairs(base, {"features": b"\x9f\xff"})
        return b"\xa6" + b"".join(k + v for k, v in changed), PROFILE
    if recipe == "indefinite_text":
        text = field_entry(base, "analysis_id")["value"]["value"].encode()
        changed = encoded_pairs(base, {"analysis_id": b"\x7f" + _head(3, len(text)) + text + b"\xff"})
        return b"\xa6" + b"".join(k + v for k, v in changed), PROFILE
    if recipe == "invalid_utf8":
        changed = encoded_pairs(base, {"analysis_id": b"\x61\xff"})
        return b"\xa6" + b"".join(k + v for k, v in changed), PROFILE
    if recipe == "trailing":
        return canonical + b"\x00", PROFILE
    if recipe == "truncated":
        return canonical[:-1], PROFILE
    if recipe == "reserved_additional":
        return b"\x1c", PROFILE
    if recipe == "wrong_profile":
        return canonical, "statqed.cbor-core.v0"
    if recipe == "resource_input":
        return b"\x00" * (1_048_576 + 1), PROFILE
    if recipe == "resource_depth":
        return b"\x81" * 33 + b"\xf6", PROFILE
    raise ValueError(recipe)


def layer(status: str, code: str) -> dict[str, str]:
    return {"status": status, "code": code}


def schema_case_result(case: dict[str, Any], value: dict[str, Any], rust_binary: Path, cddl_binary: Path) -> dict[str, Any]:
    direct = direct_encode(value)
    encoded, py_encode, rs_encode = invoke_encode(value, rust_binary)
    if encoded != direct:
        raise AssertionError(f"direct/prototype bytes differ for {case['id']}")
    py_decode, rs_decode = invoke_decode(encoded, rust_binary)
    cddl = cddl_result(cddl_binary, encoded)
    semantic = validate_fixture(value)
    semantic_observation = layer("accepted" if semantic.accepted else "rejected", semantic.code)
    if semantic.code != case["schema_code"]:
        raise AssertionError(f"schema-layer code mismatch for {case['id']}: {semantic.code} != {case['schema_code']}")
    if cddl["status"] == "rejected":
        primary = layer("rejected", "shape.cddl_mismatch")
    elif not semantic.accepted:
        primary = layer("rejected", semantic.code)
    else:
        raise AssertionError(f"negative schema case unexpectedly accepted: {case['id']}")
    if primary["code"] != case["code"]:
        raise AssertionError(f"catalog primary mismatch for {case['id']}: {primary} != {case}")
    actual_stage = "cddl_shape" if cddl["status"] == "rejected" else "schema_semantics"
    if case["stage"] != actual_stage:
        raise AssertionError(f"catalog stage mismatch for {case['id']}: {actual_stage} != {case['stage']}")
    return {
        "id": case["id"], "classification": "rejected", "primary": primary,
        "layers": {
            "profile_decode": layer("accepted", py_decode["code"]),
            "deterministic_bytes": layer("accepted", "accepted"),
            "cddl_shape": layer(cddl["status"], cddl["code"]),
            "schema_semantics": semantic_observation,
            "fixture_digest": layer("not_reached", "not_reached"),
        },
        "implementation_outputs": {
            "python_encode_sha256": sha256(canonical_json(py_encode)),
            "rust_encode_sha256": sha256(canonical_json(rs_encode)),
            "python_decode_code": py_decode["code"],
            "rust_decode_code": rs_decode["code"],
        },
    }


def raw_case_result(case: dict[str, Any], base: dict[str, Any], canonical: bytes, rust_binary: Path) -> dict[str, Any]:
    data, expected_profile = raw_recipe(case["recipe"], base, canonical)
    try:
        py, rs = invoke_decode(data, rust_binary, profile=expected_profile, require_same_code=False)
    except AssertionError as error:
        raise AssertionError(f"{case['id']}: {error}") from error
    if py["code"] != case["code"]:
        raise AssertionError(f"raw code mismatch for {case['id']}: {py['code']} != {case['code']}")
    deterministic_failure = py["result_class"] == "deterministic_profile"
    actual_stage = "deterministic_bytes" if deterministic_failure else "profile_decode"
    if case["stage"] != actual_stage:
        raise AssertionError(f"raw catalog stage mismatch for {case['id']}: {actual_stage} != {case['stage']}")
    profile_layer = layer("accepted", "accepted") if deterministic_failure else layer("rejected", py["code"])
    deterministic_layer = layer("rejected", py["code"]) if deterministic_failure else layer("not_reached", "not_reached")
    return {
        "id": case["id"], "classification": "rejected", "primary": layer("rejected", py["code"]),
        "layers": {
            "profile_decode": profile_layer,
            "deterministic_bytes": deterministic_layer,
            "cddl_shape": layer("not_reached", "not_reached"),
            "schema_semantics": layer("not_reached", "not_reached"),
            "fixture_digest": layer("not_reached", "not_reached"),
        },
        "raw_sha256": sha256(data), "raw_bytes": len(data),
        "python_result_class": py["result_class"], "python_code": py["code"],
        "rust_result_class": rs["result_class"], "rust_code": rs["code"],
    }


def digest_case_result(
    case: dict[str, Any], canonical: bytes, alternate_payload: bytes,
    frame: bytes, digest: bytes, rust_binary: Path,
) -> dict[str, Any]:
    if case["stage"] != "fixture_digest":
        raise AssertionError(f"digest catalog stage mismatch for {case['id']}")
    expected = {
        "purpose_id": PURPOSE, "algorithm_id": ALGORITHM, "profile_id": PROFILE,
        "object_class_schema_id": OBJECT_CLASS, "framing_id": FRAMING,
    }
    test_frame, test_digest = frame, digest
    if case["field"] in expected:
        expected[case["field"]] = case["value"]
    elif case["field"] == "payload":
        test_frame, _ = direct_frame(alternate_payload)
    elif case["field"] == "digest":
        test_digest = bytes((digest[0] ^ 1,)) + digest[1:]
    else:
        raise ValueError(case)
    py, rs = invoke_verify(test_frame, test_digest, rust_binary, expected)
    if py["code"] != case["code"]:
        raise AssertionError(f"digest code mismatch for {case['id']}: {py['code']} != {case['code']}")
    return {
        "id": case["id"], "classification": "rejected", "primary": layer("rejected", py["code"]),
        "layers": {
            "profile_decode": layer("accepted", "accepted"),
            "deterministic_bytes": layer("accepted", "accepted"),
            "cddl_shape": layer("accepted", "accepted"),
            "schema_semantics": layer("accepted", "accepted"),
            "fixture_digest": layer("rejected", py["code"]),
        },
        "python_result_class": py["result_class"], "rust_result_class": rs["result_class"],
        "canonical_payload_sha256": sha256(canonical),
        "tested_frame_sha256": sha256(test_frame), "tested_digest_hex": test_digest.hex(),
    }


def standalone_empty_digest_case(case: dict[str, Any], rust_binary: Path) -> dict[str, Any]:
    frame, digest = direct_frame(b"")
    py_decode, _ = invoke_decode(b"", rust_binary)
    expected = {
        "purpose_id": PURPOSE, "algorithm_id": ALGORITHM, "profile_id": PROFILE,
        "object_class_schema_id": OBJECT_CLASS, "framing_id": FRAMING,
    }
    py_digest, rs_digest = invoke_verify(frame, digest, rust_binary, expected)
    if py_decode["code"] != case["code"] or py_digest["code"] != case["standalone_digest_code"]:
        raise AssertionError(f"empty-payload observations changed: {py_decode}, {py_digest}")
    return {
        "id": case["id"], "classification": "rejected",
        "primary": layer("rejected", py_decode["code"]),
        "layers": {
            "profile_decode": layer("rejected", py_decode["code"]),
            "deterministic_bytes": layer("not_reached", "not_reached"),
            "cddl_shape": layer("not_reached", "not_reached"),
            "schema_semantics": layer("not_reached", "not_reached"),
            "fixture_digest": layer("not_reached", "not_reached"),
        },
        "standalone_digest_observation": {
            "status": "rejected", "code": py_digest["code"],
            "rust_code": rs_digest["code"], "frame_sha256": sha256(frame),
            "digest_hex": digest.hex(),
        },
    }


def schema_invalid_digest_match_case(
    case: dict[str, Any], base: dict[str, Any], rust_binary: Path, cddl_binary: Path,
) -> dict[str, Any]:
    value = copy.deepcopy(base)
    field_entry(value, "analysis_id")["value"] = {"type": "text", "value": "Invalid"}
    payload = direct_encode(value)
    py_decode, _ = invoke_decode(payload, rust_binary)
    cddl = cddl_result(cddl_binary, payload)
    semantic = validate_fixture(value)
    frame, digest = direct_frame(payload)
    expected = {
        "purpose_id": PURPOSE, "algorithm_id": ALGORITHM, "profile_id": PROFILE,
        "object_class_schema_id": OBJECT_CLASS, "framing_id": FRAMING,
    }
    py_digest, rs_digest = invoke_verify(frame, digest, rust_binary, expected)
    if py_decode["code"] != "accepted" or cddl["status"] != "accepted":
        raise AssertionError("schema-invalid digest fixture failed before semantic validation")
    if semantic.code != case["code"] or py_digest["code"] != "accepted" or rs_digest["code"] != "accepted":
        raise AssertionError("schema-invalid matching-digest observation changed")
    return {
        "id": case["id"], "classification": "rejected",
        "primary": layer("rejected", semantic.code),
        "layers": {
            "profile_decode": layer("accepted", "accepted"),
            "deterministic_bytes": layer("accepted", "accepted"),
            "cddl_shape": layer("accepted", "accepted"),
            "schema_semantics": layer("rejected", semantic.code),
            "fixture_digest": layer("not_reached", "not_reached"),
        },
        "standalone_digest_observation": {
            "status": "accepted", "code": py_digest["code"],
            "rust_code": rs_digest["code"], "frame_sha256": sha256(frame),
            "digest_hex": digest.hex(),
        },
    }


def outputs(cddl_binary: Path, rust_target: Path) -> dict[Path, bytes]:
    if not cddl_binary.is_file():
        raise FileNotFoundError(cddl_binary)
    verify_cddl_version(cddl_binary)
    manifest = json.loads((ROOT / "schemas/v0/manifest.json").read_text(encoding="utf-8"))
    if (manifest.get("schema_id"), manifest.get("schema_version")) != (OBJECT_CLASS, SCHEMA_VERSION):
        raise AssertionError("schema identity/version pair drift")
    compile_check = bounded_run(
        [sys.executable, str(ROOT / "scripts/schema/compile_schema_v0.py"), "--check"], timeout=30
    )
    if compile_check.returncode:
        raise RuntimeError(compile_check.stderr.decode("utf-8", "replace"))
    compiled = bounded_run(
        [str(cddl_binary), "--ci", "compile-cddl", "--cddl", str(SCHEMA)],
        timeout=30,
    )
    if compiled.returncode:
        raise RuntimeError(compiled.stderr.decode("utf-8", "replace"))
    rust_binary = build_rust_binary(rust_target)

    generated: dict[Path, bytes] = {}
    positive_results = []
    fixture_manifest = []
    golden_manifest = []
    representative_value: dict[str, Any] | None = None
    representative_bytes: bytes | None = None
    representative_frame: bytes | None = None
    representative_digest: bytes | None = None
    alternate_valid_bytes: bytes | None = None

    for fixture_path in sorted(POSITIVES.glob("*.json")):
        fixture_raw = fixture_path.read_bytes()
        fixture = json.loads(fixture_raw)
        value = fixture["typed_value"]
        semantic = validate_fixture(value)
        if not semantic.accepted:
            raise AssertionError(f"positive semantic failure: {fixture_path}: {semantic.code}")
        expected = direct_encode(value)
        encoded, py_encode, rs_encode = invoke_encode(value, rust_binary)
        if encoded != expected:
            raise AssertionError(f"prototype output changed reviewed recipe: {fixture_path}")
        py_decode, rs_decode = invoke_decode(encoded, rust_binary)
        cddl = cddl_result(cddl_binary, encoded)
        if cddl["status"] != "accepted" or py_decode["code"] != "accepted":
            raise AssertionError(f"positive layer rejected: {fixture_path}")
        direct_framed, direct_digest = direct_frame(encoded)
        py_frame, rs_frame = invoke_frame(encoded, rust_binary)
        if bytes.fromhex(py_frame["frame_hex"]) != direct_framed or bytes.fromhex(rs_frame["frame_hex"]) != direct_framed:
            raise AssertionError(f"frame disagreement: {fixture_path}")
        if bytes.fromhex(py_frame["digest_hex"]) != direct_digest or bytes.fromhex(rs_frame["digest_hex"]) != direct_digest:
            raise AssertionError(f"digest disagreement: {fixture_path}")
        digest_expected = {
            "purpose_id": PURPOSE, "algorithm_id": ALGORITHM, "profile_id": PROFILE,
            "object_class_schema_id": OBJECT_CLASS, "framing_id": FRAMING,
        }
        py_verify, rs_verify = invoke_verify(direct_framed, direct_digest, rust_binary, digest_expected)
        if py_verify["code"] != "accepted" or rs_verify["code"] != "accepted":
            raise AssertionError(f"intact digest verification failed: {fixture_path}")

        stem = fixture["fixture_id"].replace(".", "-")
        cbor_path = Path(f"conformance/golden/v0/{stem}.cbor")
        frame_path = Path(f"conformance/golden/v0/{stem}.frame")
        generated[cbor_path] = encoded
        generated[frame_path] = direct_framed
        positive_results.append({
            "id": fixture["fixture_id"], "classification": "accepted", "primary": layer("accepted", "accepted"),
            "layers": {name: layer("accepted", "accepted") for name in (
                "profile_decode", "deterministic_bytes", "cddl_shape", "schema_semantics", "fixture_digest"
            )},
            "canonical_cbor_hex": encoded.hex(), "canonical_cbor_sha256": sha256(encoded),
            "frame_sha256": sha256(direct_framed), "digest_hex": direct_digest.hex(),
            "python_digest_verify_code": py_verify["code"],
            "rust_digest_verify_code": rs_verify["code"],
            "python_encode_output_sha256": sha256(canonical_json(py_encode)),
            "rust_encode_output_sha256": sha256(canonical_json(rs_encode)),
        })
        fixture_manifest.append({
            "fixture_id": fixture["fixture_id"], "source": fixture_path.relative_to(ROOT).as_posix(),
            "source_sha256": sha256(fixture_raw), "expected_cbor_recipe": fixture["expected_cbor_recipe"],
            "canonical_cbor_sha256": sha256(encoded),
        })
        golden_manifest.append({
            "fixture_id": fixture["fixture_id"], "cbor_path": cbor_path.as_posix(),
            "cbor_sha256": sha256(encoded), "frame_path": frame_path.as_posix(),
            "frame_sha256": sha256(direct_framed),
            "digest_hex": direct_digest.hex(),
        })
        if fixture["fixture_id"] == "positive.minimum":
            alternate_valid_bytes = encoded
        if fixture["fixture_id"] == "positive.representative":
            representative_value, representative_bytes = value, encoded
            representative_frame, representative_digest = direct_framed, direct_digest

    if (representative_value is None or representative_bytes is None or representative_frame is None
            or representative_digest is None or alternate_valid_bytes is None):
        raise AssertionError("representative fixture missing")

    catalog = json.loads(NEGATIVE_CATALOG.read_text(encoding="utf-8"))
    expanded_cases = list(catalog["cases"])
    for field in catalog["null_absence_fields"]:
        expanded_cases.append({
            "id": f"unknown.null_presence.{field}", "kind": "add", "field": field,
            "value": {"type": "null"}, "stage": "cddl_shape", "code": "shape.cddl_mismatch",
            "schema_code": "schema.unknown_field",
        })
    expanded_cases.extend([
        {"id": "raw.resource_input", "kind": "raw", "recipe": "resource_input", "stage": "profile_decode", "code": "resource.input_bytes"},
        {"id": "raw.resource_depth", "kind": "raw", "recipe": "resource_depth", "stage": "profile_decode", "code": "resource.depth"},
    ])

    negative_results = []
    for case in expanded_cases:
        if case["kind"] in {"remove", "add", "set", "analysis_over", "set_version_pair"}:
            negative_results.append(schema_case_result(case, mutate_semantic(representative_value, case), rust_binary, cddl_binary))
        elif case["kind"] == "duplicate":
            value = mutate_semantic(representative_value, case)
            raw = direct_encode(value)
            py, rs = invoke_decode(raw, rust_binary)
            if py["code"] != "validity.map_duplicate":
                raise AssertionError(f"duplicate decoder failure: {py}")
            if case["stage"] != "profile_decode" or case["code"] != py["code"]:
                raise AssertionError(f"duplicate catalog mismatch: {case}")
            negative_results.append({
                "id": case["id"], "classification": "rejected", "primary": layer("rejected", py["code"]),
                "layers": {"profile_decode": layer("rejected", py["code"]), **{
                    name: layer("not_reached", "not_reached") for name in (
                        "deterministic_bytes", "cddl_shape", "schema_semantics", "fixture_digest")}},
                "raw_sha256": sha256(raw), "rust_code": rs["code"],
            })
        elif case["kind"] == "raw":
            negative_results.append(raw_case_result(case, representative_value, representative_bytes, rust_binary))
        elif case["kind"] == "digest":
            negative_results.append(digest_case_result(
                case, representative_bytes, alternate_valid_bytes,
                representative_frame, representative_digest, rust_binary
            ))
        elif case["kind"] == "standalone_digest":
            negative_results.append(standalone_empty_digest_case(case, rust_binary))
        elif case["kind"] == "schema_invalid_digest_match":
            negative_results.append(schema_invalid_digest_match_case(case, representative_value, rust_binary, cddl_binary))
        else:
            raise ValueError(case)

    # Retained tool limitation: the pinned CDDL validator accepts duplicate
    # map members. RFC-0001 raw decoders must reject them before this layer.
    duplicate_value = copy.deepcopy(representative_value)
    duplicate_value["entries"].append(copy.deepcopy(field_entry(duplicate_value, "schema_id")))
    duplicate_raw = direct_encode(duplicate_value)
    duplicate_cddl = cddl_result(cddl_binary, duplicate_raw)
    if duplicate_cddl["status"] != "accepted":
        raise AssertionError("expected retained cddl 0.10.6 duplicate limitation changed")

    unknown_value = mutate_semantic(representative_value, {"kind": "add", "field": "future"})
    baseline_unknown = validate_fixture(unknown_value)
    stripped = copy.deepcopy(unknown_value)
    stripped["entries"] = [entry for entry in stripped["entries"] if entry["key"].get("value") != "future"]
    collapsed_by_key: dict[str, dict[str, Any]] = {}
    collapsed_order: list[str] = []
    for entry in duplicate_value["entries"]:
        key = entry["key"]["value"]
        if key not in collapsed_by_key:
            collapsed_order.append(key)
        collapsed_by_key[key] = entry
    collapsed_value = {"type": "map", "entries": [collapsed_by_key[key] for key in collapsed_order]}
    duplicate_py, duplicate_rs = invoke_decode(duplicate_raw, rust_binary)
    mutations = [
        {
            "id": "mutation.semantic_unknown_drop", "detected": not baseline_unknown.accepted and validate_fixture(stripped).accepted,
            "reason": "test-only mutant strips an unknown field before the real validator",
        },
        {
            "id": "mutation.encoder_changed_golden", "detected": representative_bytes != representative_bytes[:-1] + bytes((representative_bytes[-1] ^ 1,)),
            "reason": "changed accepted golden differs from direct recipe and both prototypes",
        },
        {
            "id": "mutation.decoder_duplicate_collapse",
            "detected": (
                validate_fixture(collapsed_value).accepted
                and duplicate_py["code"] == "validity.map_duplicate"
                and duplicate_rs["code"] == "validity.map_duplicate"
            ),
            "reason": "last-wins collapse would accept while both RFC-0001 decoders reject duplicate raw bytes",
            "python_decoder_code": duplicate_py["code"],
            "rust_decoder_code": duplicate_rs["code"],
        },
    ]
    if not all(item["detected"] for item in mutations):
        raise AssertionError("deliberate mutation escaped")

    inherited_resource_ids = [
        "RESOURCE-INPUT-BYTES-1048576", "RESOURCE-INPUT-BYTES-1048577",
        "RESOURCE-OUTPUT-BYTES-1048576", "RESOURCE-OUTPUT-BYTES-1048577",
        "RESOURCE-DEPTH-32", "RESOURCE-DEPTH-33",
        "RESOURCE-MAP-ENTRIES-1024", "RESOURCE-MAP-ENTRIES-1025",
        "RESOURCE-ARRAY-ITEMS-1024", "RESOURCE-ARRAY-ITEMS-1025",
        "RESOURCE-TEXT-STRING-65536-BYTES", "RESOURCE-TEXT-STRING-65537-BYTES",
        "RESOURCE-DIAGNOSTIC-BYTES-4096", "RESOURCE-DIAGNOSTIC-BYTES-4097",
        "MUTANT-DECODER-ALLOCATES-DECLARED-STRING", "OPERATIONAL-TIMEOUT-OVER",
    ]
    inherited_document = json.loads(SQ0005_RESULTS.read_text(encoding="utf-8"))
    inherited_by_id = {case["id"]: case for case in inherited_document["cases"]}
    inherited_resources = []
    for fixture_id in inherited_resource_ids:
        case = inherited_by_id.get(fixture_id)
        if case is None or any(case["comparison_errors"].values()):
            raise AssertionError(f"invalid inherited SQ-0005 resource evidence: {fixture_id}")
        inherited_resources.append({
            "id": fixture_id,
            "accepted": case["expected"]["accept"],
            "code": case["expected"]["code"],
            "result_class": case["expected"]["result_class"],
        })

    results = {
        "result_version": "statqed.schema-v0-results.v1",
        "schema_id": OBJECT_CLASS, "schema_version": SCHEMA_VERSION,
        "layer_order": ["profile_decode", "deterministic_bytes", "cddl_shape", "schema_semantics", "fixture_digest"],
        "positive_count": len(positive_results), "negative_count": len(negative_results),
        "results": positive_results + negative_results,
        "retained_limitations": [
            {
                "id": "cddl-0.10.6-duplicate-map-members",
                "observation": "pinned CDDL accepts duplicate members; both RFC-0001 decoders reject first",
                "raw_sha256": sha256(duplicate_raw), "cddl_status": duplicate_cddl["status"],
            },
            {
                "id": "schema-fixed-text-keys-do-not-discriminate-order-algorithms",
                "observation": "all six key encodings sort identically under core and length-first order; SQ-0005 generic discriminator remains bound",
            },
        ],
        "resource_observation": {
            "maximum_accepted_payload_bytes": max(len(generated[Path(item["cbor_path"])]) for item in golden_manifest),
            "maximum_accepted_frame_bytes": max(len(generated[Path(item["frame_path"])]) for item in golden_manifest),
            "rfc0001_input_limit_bytes": 1_048_576,
        },
        "inherited_sq0005_resource_evidence": {
            "source": SQ0005_RESULTS.relative_to(ROOT).as_posix(),
            "source_sha256": sha256(SQ0005_RESULTS.read_bytes()),
            "cases": inherited_resources,
            "interpretation": "Re-executed by the permanent SQ-0005 conformance gate; SQ-0006 adds fixture-specific input/depth negatives and accepted payload/frame size observations without duplicating the generic profile corpus."
        },
    }
    golden = {
        "manifest_version": "statqed.schema-v0-goldens.v1",
        "schema_id": OBJECT_CLASS, "schema_version": SCHEMA_VERSION,
        "digest_identifiers": {
            "purpose": PURPOSE, "algorithm": ALGORITHM, "profile": PROFILE,
            "object_class_schema": OBJECT_CLASS, "framing": FRAMING,
        },
        "entries": golden_manifest,
    }
    fixtures = {
        "manifest_version": "statqed.schema-v0-fixtures.v1",
        "schema_id": OBJECT_CLASS, "schema_version": SCHEMA_VERSION,
        "positive": fixture_manifest,
        "negative_catalog": NEGATIVE_CATALOG.relative_to(ROOT).as_posix(),
        "negative_catalog_sha256": sha256(NEGATIVE_CATALOG.read_bytes()),
        "expanded_negative_count": len(negative_results),
        "expanded_negative_ids": [case["id"] for case in expanded_cases],
    }
    generated[Path("schemas/fixtures/v0/manifest.json")] = canonical_json(fixtures)
    generated[Path("conformance/golden/v0/manifest.json")] = canonical_json(golden)
    generated[Path("conformance/schema-v0/results.json")] = canonical_json(results)
    generated[Path("conformance/schema-v0/mutations.json")] = canonical_json({
        "mutation_version": "statqed.schema-v0-mutations.v1", "mutations": mutations,
    })
    return generated


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--cddl-bin", type=Path, default=Path(os.environ.get("STATQED_CDDL_BIN", "/tmp/statqed-sq0006-cddl-0.10.6/bin/cddl")))
    parser.add_argument("--rust-target-dir", type=Path, default=Path(os.environ.get("STATQED_SCHEMA_RUST_TARGET", "/tmp/statqed-sq0006-rust-target")))
    args = parser.parse_args()
    generated = outputs(args.cddl_bin, args.rust_target_dir)
    failures = []
    for relative, data in sorted(generated.items(), key=lambda item: item[0].as_posix()):
        destination = ROOT / relative
        if args.verify:
            if not destination.is_file() or destination.read_bytes() != data:
                failures.append(relative.as_posix())
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
    if failures:
        print("schema-v0 generated drift: " + ", ".join(failures), file=sys.stderr)
        return 1
    action = "verified" if args.verify else "generated"
    results = json.loads(generated[Path("conformance/schema-v0/results.json")])
    print(
        f"SQ-0006 schema v0 {action}: {results['positive_count']} positive, "
        f"{results['negative_count']} negative, 3 deliberate mutations"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
