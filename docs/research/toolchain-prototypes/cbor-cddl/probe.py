#!/usr/bin/env python3
"""cbor2 6.1.3 behavior probe; output is evidence, not a byte oracle."""

from __future__ import annotations

import argparse
import importlib.metadata
from pathlib import Path

import cbor2


CORE_421 = bytes.fromhex("a21818006000")
LENGTH_FIRST_423 = bytes.fromhex("a26000181800")


def nested(depth: int) -> bytes:
    return b"\x81" * depth + b"\x00"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vectors", type=Path)
    args = parser.parse_args()

    forward = {24: 0, "": 0}
    reverse = {"": 0, 24: 0}
    canonical_forward = cbor2.dumps(forward, canonical=True)
    canonical_reverse = cbor2.dumps(reverse, canonical=True)
    assert canonical_forward == canonical_reverse == LENGTH_FIRST_423
    assert canonical_forward != CORE_421

    duplicate = bytes.fromhex("a201000102")
    duplicate_value = cbor2.loads(duplicate)
    assert duplicate_value == {1: 2}

    indefinite = bytes.fromhex("9f0102ff")
    indefinite_value = cbor2.loads(indefinite)
    assert indefinite_value == [1, 2]
    assert cbor2.dumps(indefinite_value, canonical=True).hex() == "820102"

    depth_results: dict[int, str] = {}
    for depth in (254, 255, 256, 257):
        try:
            cbor2.loads(nested(depth))
        except Exception as error:  # exact implementation exception is logged below
            depth_results[depth] = f"reject:{type(error).__name__}:{error}"
        else:
            depth_results[depth] = "accept"

    malformed_results = {}
    for name, data in {
        "truncated_argument": bytes.fromhex("18"),
        "break_outside_indefinite": bytes.fromhex("ff"),
    }.items():
        try:
            value = cbor2.loads(data)
        except Exception as error:
            malformed_results[name] = f"reject:{type(error).__name__}:{error}"
        else:
            malformed_results[name] = f"accept:{value!r}"

    print(f"cbor2_version={importlib.metadata.version('cbor2')}")
    print(f"rfc8949_4_2_1_hex={CORE_421.hex()}")
    print(f"rfc8949_4_2_3_hex={LENGTH_FIRST_423.hex()}")
    print(f"cbor2_canonical_hex={canonical_forward.hex()}")
    print("cbor2_matches_length_first=true")
    print("cbor2_duplicate_default=last_value_wins")
    print("cbor2_accepts_indefinite=true")
    print("cbor2_indefinite_reencode_hex=820102")
    for depth, result in depth_results.items():
        print(f"cbor2_depth_{depth}={result}")
    for name, result in malformed_results.items():
        print(f"cbor2_{name}={result}")

    if args.vectors:
        args.vectors.mkdir(parents=True, exist_ok=True)
        (args.vectors / "valid.cbor").write_bytes(bytes.fromhex("a262696401656c6162656c626f6b"))
        (args.vectors / "invalid-shape.cbor").write_bytes(bytes.fromhex("a262696401656c6162656c02"))
        (args.vectors / "core-4.2.1.cbor").write_bytes(CORE_421)
        (args.vectors / "length-first-4.2.3.cbor").write_bytes(LENGTH_FIRST_423)


if __name__ == "__main__":
    main()
