#!/usr/bin/env python3
"""Exercise the four cbor2 6.1.4 security-relevant release regressions."""

from __future__ import annotations

import importlib.metadata

import cbor2


def rejected(label: str, data: bytes) -> str:
    try:
        value = cbor2.loads(data)
    except cbor2.CBORDecodeError as error:
        return f"{label}=reject:{type(error).__name__}:{error}"
    raise AssertionError(f"{label} unexpectedly accepted as {value!r}")


def main() -> None:
    version = importlib.metadata.version("cbor2")
    assert version == "6.1.4", version

    # An indefinite map that breaks after a key and before its value is malformed.
    incomplete_indefinite_map = bytes.fromhex("bf01ff")
    incomplete_result = rejected(
        "indefinite_map_missing_value", incomplete_indefinite_map
    )

    # Tag 2 requires a byte string payload; an array must not be coerced to int.
    non_bytes_bignum = bytes.fromhex("c28101")
    bignum_result = rejected("bignum_non_bytes_payload", non_bytes_bignum)

    # These mappings have the same key set and value set but different pairing.
    # Version 6.1.4 derives the hash from the pairs, avoiding the prior systematic
    # collision for this adversarial construction.
    paired = cbor2.frozendict({1: 2, 3: 4})
    crossed = cbor2.frozendict({1: 4, 3: 2})
    assert paired != crossed
    assert hash(paired) != hash(crossed)

    # Registering bytearray in the encoder namespace keeps later references in
    # sync with the decoder, which registers every byte string it reads.
    reference_payload = cbor2.dumps(
        [bytearray(b"statqed-reference"), b"statqed-reference"],
        string_referencing=True,
    )
    reference_round_trip = cbor2.loads(reference_payload)
    assert reference_round_trip == [b"statqed-reference", b"statqed-reference"]

    print(f"cbor2_version={version}")
    print(incomplete_result)
    print(bignum_result)
    print(f"frozendict_pair_hashes_distinct={hash(paired) != hash(crossed)}")
    print(f"bytearray_string_reference_hex={reference_payload.hex()}")
    print("bytearray_string_reference_round_trip=true")


if __name__ == "__main__":
    main()
