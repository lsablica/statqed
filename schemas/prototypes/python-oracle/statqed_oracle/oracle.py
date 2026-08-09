"""Independent standard-library oracle for the Experimental CBOR core profile.

This module is intentionally implemented from the SQ-0005 semantic model and
profile text.  It does not import a CBOR package or another StatQED encoder.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import hmac
import json
import math
import re
import struct
from typing import Any, Final, Iterable, Sequence


PROFILE_ID: Final = "statqed.cbor-core.v1"
FRAMING_ID: Final = "statqed.digest-lp.v1"
ALGORITHM_ID: Final = "sha-256"
DIAGNOSTIC_ID: Final = "statqed.python-oracle-diagnostic.v1"
DIGEST_MAGIC: Final = b"StatQED-Digest\x00"

MAX_INPUT_BYTES: Final = 1_048_576
MAX_OUTPUT_BYTES: Final = 1_048_576
MAX_STRING_BYTES: Final = 65_536
MAX_ARRAY_ITEMS: Final = 1_024
MAX_MAP_ENTRIES: Final = 1_024
MAX_TOTAL_ITEMS: Final = 4_096
MAX_DEPTH: Final = 32
MAX_DIAGNOSTIC_BYTES: Final = 4_096
MAX_IDENTIFIER_BYTES: Final = 128
MAX_DIGEST_FRAME_BYTES: Final = 1_049_255
MAX_VALID_DIGEST_FRAME_BYTES: Final = 1_048_918
MIN_INTEGER: Final = -(1 << 64)
MAX_INTEGER: Final = (1 << 64) - 1

_IDENTIFIER_RE: Final = re.compile(rb"[a-z0-9][a-z0-9._:-]{0,127}\Z")


@dataclass(frozen=True)
class Integer:
    value: int


@dataclass(frozen=True)
class ByteString:
    value: bytes


@dataclass(frozen=True)
class TextString:
    value: str


@dataclass(frozen=True)
class Array:
    items: tuple[SemanticValue, ...]

    def __init__(self, items: Iterable[SemanticValue]):
        object.__setattr__(self, "items", tuple(items))


@dataclass(frozen=True)
class Map:
    entries: tuple[tuple[SemanticValue, SemanticValue], ...]

    def __init__(self, entries: Iterable[tuple[SemanticValue, SemanticValue]]):
        object.__setattr__(self, "entries", tuple(entries))


@dataclass(frozen=True)
class Boolean:
    value: bool


@dataclass(frozen=True)
class Null:
    pass


NULL: Final = Null()


@dataclass(frozen=True)
class Bignum:
    # Typed JSON retains the decimal spelling because this class is always
    # rejected by the v1 profile.  Avoiding host-integer conversion keeps an
    # unsupported, very large value from depending on CPython's configurable
    # decimal-digit limit.
    value: int | str


@dataclass(frozen=True)
class Rational:
    numerator: int
    denominator: int


@dataclass(frozen=True)
class Decimal:
    coefficient: int
    exponent: int


@dataclass(frozen=True)
class IEEEBits:
    width: int
    bits: int


@dataclass(frozen=True)
class Interval:
    lower: SemanticValue
    upper: SemanticValue
    closure: str


@dataclass(frozen=True)
class Extension:
    type_id: str
    critical: bool
    body: SemanticValue


@dataclass(frozen=True)
class ExtensionSequence:
    extensions: tuple[Extension, ...]

    def __init__(self, extensions: Iterable[Extension]):
        object.__setattr__(self, "extensions", tuple(extensions))


SemanticValue = (
    Integer
    | ByteString
    | TextString
    | Array
    | Map
    | Boolean
    | Null
    | Bignum
    | Rational
    | Decimal
    | IEEEBits
    | Interval
    | Extension
    | ExtensionSequence
)


@dataclass(frozen=True)
class RawEntry:
    """One map pair retained in wire order before duplicate validation."""

    key: RawItem
    value: RawItem


@dataclass(frozen=True)
class RawItem:
    """Lossless-enough raw parse node for every relevant profile decision."""

    kind: str
    start: int
    end: int
    initial_byte: int
    additional_information: int
    argument: int | None = None
    indefinite: bool = False
    data: bytes | None = None
    text: str | None = None
    items: tuple[RawItem, ...] = ()
    entries: tuple[RawEntry, ...] = ()
    chunks: tuple[RawItem, ...] = ()
    child: RawItem | None = None
    bits: int | None = None


@dataclass(frozen=True)
class Result:
    result_class: str
    code: str
    value: SemanticValue | None = None
    raw: RawItem | None = None
    encoded: bytes | None = None
    frame: bytes | None = None
    digest: bytes | None = None
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def accepted(self) -> bool:
        return self.result_class == "accepted" and self.code == "accepted"


class OracleError(Exception):
    """Internal control-flow exception carrying only stable API fields."""

    def __init__(self, result_class: str, code: str):
        super().__init__(code)
        self.result_class = result_class
        self.code = code

    def as_result(self, *, raw: RawItem | None = None) -> Result:
        return Result(self.result_class, self.code, raw=raw)


class _Parser:
    def __init__(self, data: bytes):
        self.data = data
        self.position = 0
        self.total_items = 0
        self.validity_issues: list[OracleError] = []
        self.expectedness_issues: list[OracleError] = []
        self.profile_issues: list[OracleError] = []

    def _need(self, count: int) -> bytes:
        if count < 0 or self.position + count < self.position:
            # Python integers do not overflow, and finite profile input is at
            # most 1 MiB. Keep defensive host arithmetic outside the public
            # profile taxonomy if this invariant is ever violated.
            raise OverflowError("parser offset arithmetic invariant failed")
        end = self.position + count
        if end > len(self.data):
            raise OracleError("well_formedness", "wellformed.truncated")
        out = self.data[self.position:end]
        self.position = end
        return out

    def _read_argument(self, ai: int) -> int | None:
        if ai < 24:
            return ai
        widths = {24: 1, 25: 2, 26: 4, 27: 8}
        if ai in widths:
            return int.from_bytes(self._need(widths[ai]), "big")
        if ai in (28, 29, 30):
            raise OracleError("well_formedness", "wellformed.reserved_additional")
        return None

    @staticmethod
    def _is_preferred(ai: int, argument: int) -> bool:
        if argument < 24:
            return ai == argument
        if argument <= 0xFF:
            return ai == 24
        if argument <= 0xFFFF:
            return ai == 25
        if argument <= 0xFFFF_FFFF:
            return ai == 26
        return ai == 27

    def _enter_item(self) -> None:
        self.total_items += 1
        if self.total_items > MAX_TOTAL_ITEMS:
            raise OracleError("resource", "resource.total_items")

    @staticmethod
    def _check_open_depth(open_depth: int) -> int:
        next_depth = open_depth + 1
        if next_depth > MAX_DEPTH:
            raise OracleError("resource", "resource.depth")
        return next_depth

    def parse_item(self, open_depth: int = 0, *, allow_break: bool = False) -> RawItem | None:
        if self.position >= len(self.data):
            raise OracleError("well_formedness", "wellformed.truncated")
        start = self.position
        initial = self._need(1)[0]
        major = initial >> 5
        ai = initial & 0x1F

        if major == 7 and ai == 31:
            if allow_break:
                return None
            raise OracleError("well_formedness", "wellformed.unexpected_break")

        self._enter_item()
        argument = self._read_argument(ai)

        if ai == 31 and major not in (2, 3, 4, 5):
            raise OracleError("well_formedness", "wellformed.reserved_additional")

        if major <= 6 and ai != 31:
            assert argument is not None
            if not self._is_preferred(ai, argument):
                self.profile_issues.append(
                    OracleError("deterministic_profile", "profile.non_preferred_head")
                )

        if major == 0:
            assert argument is not None
            return RawItem("unsigned", start, self.position, initial, ai, argument=argument)
        if major == 1:
            assert argument is not None
            return RawItem("negative", start, self.position, initial, ai, argument=argument)
        if major in (2, 3):
            return self._parse_string(start, initial, ai, argument, major, open_depth)
        if major == 4:
            return self._parse_array(start, initial, ai, argument, open_depth)
        if major == 5:
            return self._parse_map(start, initial, ai, argument, open_depth)
        if major == 6:
            assert argument is not None
            child_depth = self._check_open_depth(open_depth)
            child = self.parse_item(child_depth)
            assert child is not None
            self.profile_issues.append(
                OracleError("deterministic_profile", "profile.tag_forbidden")
            )
            return RawItem(
                "tag",
                start,
                self.position,
                initial,
                ai,
                argument=argument,
                child=child,
            )
        return self._parse_simple_or_float(start, initial, ai, argument)

    def _parse_string(
        self,
        start: int,
        initial: int,
        ai: int,
        argument: int | None,
        major: int,
        open_depth: int,
    ) -> RawItem:
        kind = "bytes" if major == 2 else "text"
        if ai != 31:
            assert argument is not None
            if argument > MAX_STRING_BYTES:
                raise OracleError("resource", "resource.string_bytes")
            data = self._need(argument)
            text: str | None = None
            if major == 3:
                try:
                    text = data.decode("utf-8", "strict")
                except UnicodeDecodeError:
                    self.validity_issues.append(
                        OracleError("validity", "validity.invalid_utf8")
                    )
            return RawItem(
                kind,
                start,
                self.position,
                initial,
                ai,
                argument=argument,
                data=data,
                text=text,
            )

        self.profile_issues.append(
            OracleError("deterministic_profile", "profile.indefinite")
        )
        chunks: list[RawItem] = []
        total = 0
        while True:
            if self.position >= len(self.data):
                raise OracleError("well_formedness", "wellformed.truncated")
            if self.data[self.position] == 0xFF:
                self.position += 1
                break
            chunk_start = self.position
            chunk_initial = self.data[self.position]
            chunk_major = chunk_initial >> 5
            chunk_ai = chunk_initial & 0x1F
            if chunk_major != major or chunk_ai == 31:
                raise OracleError("well_formedness", "wellformed.indefinite_chunk_type")
            chunk = self.parse_item(open_depth)
            assert chunk is not None and chunk.start == chunk_start
            chunks.append(chunk)
            assert chunk.data is not None
            total += len(chunk.data)
            if total > MAX_STRING_BYTES:
                raise OracleError("resource", "resource.string_bytes")
        data = b"".join(chunk.data or b"" for chunk in chunks)
        text = None
        if major == 3 and all(chunk.text is not None for chunk in chunks):
            text = "".join(chunk.text or "" for chunk in chunks)
        return RawItem(
            kind,
            start,
            self.position,
            initial,
            ai,
            indefinite=True,
            data=data,
            text=text,
            chunks=tuple(chunks),
        )

    def _parse_array(
        self,
        start: int,
        initial: int,
        ai: int,
        argument: int | None,
        open_depth: int,
    ) -> RawItem:
        child_depth = self._check_open_depth(open_depth)
        items: list[RawItem] = []
        if ai == 31:
            self.profile_issues.append(
                OracleError("deterministic_profile", "profile.indefinite")
            )
            while True:
                child = self.parse_item(child_depth, allow_break=True)
                if child is None:
                    break
                items.append(child)
                if len(items) > MAX_ARRAY_ITEMS:
                    raise OracleError("resource", "resource.array_items")
        else:
            assert argument is not None
            if argument > MAX_ARRAY_ITEMS:
                raise OracleError("resource", "resource.array_items")
            for _ in range(argument):
                child = self.parse_item(child_depth)
                assert child is not None
                items.append(child)
        return RawItem(
            "array",
            start,
            self.position,
            initial,
            ai,
            argument=argument,
            indefinite=ai == 31,
            items=tuple(items),
        )

    def _parse_map(
        self,
        start: int,
        initial: int,
        ai: int,
        argument: int | None,
        open_depth: int,
    ) -> RawItem:
        child_depth = self._check_open_depth(open_depth)
        entries: list[RawEntry] = []
        if ai == 31:
            self.profile_issues.append(
                OracleError("deterministic_profile", "profile.indefinite")
            )
            while True:
                key = self.parse_item(child_depth, allow_break=True)
                if key is None:
                    break
                if self.position >= len(self.data):
                    raise OracleError("well_formedness", "wellformed.truncated")
                if self.data[self.position] == 0xFF:
                    raise OracleError("well_formedness", "wellformed.map_pair_missing")
                value = self.parse_item(child_depth)
                assert value is not None
                entries.append(RawEntry(key, value))
                if len(entries) > MAX_MAP_ENTRIES:
                    raise OracleError("resource", "resource.map_entries")
        else:
            assert argument is not None
            if argument > MAX_MAP_ENTRIES:
                raise OracleError("resource", "resource.map_entries")
            for _ in range(argument):
                key = self.parse_item(child_depth)
                assert key is not None
                if self.position >= len(self.data):
                    raise OracleError(
                        "well_formedness", "wellformed.map_pair_missing"
                    )
                value = self.parse_item(child_depth)
                assert value is not None
                entries.append(RawEntry(key, value))

        self._check_map(entries)
        return RawItem(
            "map",
            start,
            self.position,
            initial,
            ai,
            argument=argument,
            indefinite=ai == 31,
            entries=tuple(entries),
        )

    def _check_map(self, entries: Sequence[RawEntry]) -> None:
        identities: list[tuple[str, int | str] | None] = []
        for entry in entries:
            identity = _raw_key_identity(entry.key)
            identities.append(identity)
            if identity is None:
                self.expectedness_issues.append(
                    OracleError("expectedness", "expected.map_key_type")
                )

        seen: set[tuple[str, int | str]] = set()
        duplicate = False
        for identity in identities:
            if identity is None:
                continue
            if identity in seen:
                duplicate = True
                break
            seen.add(identity)
        if duplicate:
            self.validity_issues.append(
                OracleError("validity", "validity.map_duplicate")
            )

        if all(identity is not None for identity in identities):
            encodings = [_encode_key_identity(identity) for identity in identities]
            if any(left >= right for left, right in zip(encodings, encodings[1:])):
                self.profile_issues.append(
                    OracleError("deterministic_profile", "profile.map_order")
                )

    def _parse_simple_or_float(
        self, start: int, initial: int, ai: int, argument: int | None
    ) -> RawItem:
        if ai < 20:
            self.profile_issues.append(
                OracleError("deterministic_profile", "profile.simple_forbidden")
            )
            return RawItem("simple", start, self.position, initial, ai, argument=ai)
        if ai in (20, 21, 22, 23):
            if ai == 23:
                self.profile_issues.append(
                    OracleError("deterministic_profile", "profile.simple_forbidden")
                )
            return RawItem("simple", start, self.position, initial, ai, argument=ai)
        if ai == 24:
            assert argument is not None
            if argument < 32:
                raise OracleError("well_formedness", "wellformed.reserved_additional")
            self.profile_issues.append(
                OracleError("deterministic_profile", "profile.simple_forbidden")
            )
            return RawItem("simple", start, self.position, initial, ai, argument=argument)
        if ai in (25, 26, 27):
            assert argument is not None
            self.profile_issues.append(
                OracleError("deterministic_profile", "profile.float_forbidden")
            )
            return RawItem(
                f"float{16 if ai == 25 else 32 if ai == 26 else 64}",
                start,
                self.position,
                initial,
                ai,
                bits=argument,
            )
        raise OracleError("well_formedness", "wellformed.reserved_additional")


def _raw_key_identity(raw: RawItem) -> tuple[str, int | str] | None:
    if raw.kind == "unsigned":
        assert raw.argument is not None
        return ("integer", raw.argument)
    if raw.kind == "negative":
        assert raw.argument is not None
        return ("integer", -1 - raw.argument)
    if raw.kind == "text" and raw.text is not None:
        return ("text", raw.text)
    return None


def _encode_argument(major: int, argument: int) -> bytes:
    if not 0 <= major <= 7 or argument < 0 or argument > MAX_INTEGER:
        raise ValueError("argument outside direct CBOR range")
    prefix = major << 5
    if argument < 24:
        return bytes((prefix | argument,))
    if argument <= 0xFF:
        return bytes((prefix | 24, argument))
    if argument <= 0xFFFF:
        return bytes((prefix | 25,)) + argument.to_bytes(2, "big")
    if argument <= 0xFFFF_FFFF:
        return bytes((prefix | 26,)) + argument.to_bytes(4, "big")
    return bytes((prefix | 27,)) + argument.to_bytes(8, "big")


def _encode_integer(value: int) -> bytes:
    if type(value) is not int:
        raise OracleError("semantic_validity", "semantic.unsupported_value")
    if value < MIN_INTEGER or value > MAX_INTEGER:
        raise OracleError("semantic_validity", "semantic.integer_range")
    if value >= 0:
        return _encode_argument(0, value)
    return _encode_argument(1, -1 - value)


def _encode_key_identity(identity: tuple[str, int | str] | None) -> bytes:
    assert identity is not None
    kind, value = identity
    if kind == "integer":
        assert isinstance(value, int)
        return _encode_integer(value)
    assert kind == "text" and isinstance(value, str)
    raw = _encode_text(value)
    return _encode_argument(3, len(raw)) + raw


def _encode_text(value: str) -> bytes:
    if not isinstance(value, str):
        raise OracleError("semantic_validity", "semantic.unsupported_value")
    try:
        return value.encode("utf-8", "strict")
    except UnicodeEncodeError as error:
        raise OracleError("semantic_validity", "semantic.unsupported_value") from error


@dataclass
class _EncodeState:
    total_items: int = 0

    def item(self) -> None:
        self.total_items += 1
        if self.total_items > MAX_TOTAL_ITEMS:
            raise OracleError("resource", "resource.total_items")


@dataclass
class _TypedJsonState:
    total_items: int = 0

    def item(self) -> None:
        self.total_items += 1
        if self.total_items > MAX_TOTAL_ITEMS:
            raise OracleError("resource", "resource.total_items")


def _semantic_key_identity(value: SemanticValue) -> tuple[str, int | str]:
    if isinstance(value, Integer):
        if type(value.value) is not int:
            raise OracleError("semantic_validity", "semantic.unsupported_value")
        if value.value < MIN_INTEGER or value.value > MAX_INTEGER:
            raise OracleError("semantic_validity", "semantic.integer_range")
        return ("integer", value.value)
    if isinstance(value, TextString):
        _encode_text(value.value)
        return ("text", value.value)
    raise OracleError("semantic_validity", "semantic.map_key_type")


def _validate_interval(value: Interval) -> None:
    lower = value.lower
    upper = value.upper
    if value.closure not in ("open", "closed", "left_closed", "right_closed"):
        raise OracleError("semantic_validity", "semantic.interval_invalid")
    if not isinstance(lower, Integer) or not isinstance(upper, Integer):
        raise OracleError("semantic_validity", "semantic.interval_invalid")
    if type(lower.value) is not int or type(upper.value) is not int:
        raise OracleError("semantic_validity", "semantic.interval_invalid")
    if not (MIN_INTEGER <= lower.value <= MAX_INTEGER):
        raise OracleError("semantic_validity", "semantic.interval_invalid")
    if not (MIN_INTEGER <= upper.value <= MAX_INTEGER):
        raise OracleError("semantic_validity", "semantic.interval_invalid")
    if lower.value > upper.value or (
        lower.value == upper.value and value.closure != "closed"
    ):
        raise OracleError("semantic_validity", "semantic.interval_invalid")


def _encode_value(value: SemanticValue, state: _EncodeState, open_depth: int) -> bytes:
    state.item()
    if isinstance(value, Integer):
        return _encode_integer(value.value)
    if isinstance(value, ByteString):
        if type(value.value) is not bytes:
            raise OracleError("semantic_validity", "semantic.unsupported_value")
        if len(value.value) > MAX_STRING_BYTES:
            raise OracleError("resource", "resource.string_bytes")
        return _encode_argument(2, len(value.value)) + value.value
    if isinstance(value, TextString):
        raw = _encode_text(value.value)
        if len(raw) > MAX_STRING_BYTES:
            raise OracleError("resource", "resource.string_bytes")
        return _encode_argument(3, len(raw)) + raw
    if isinstance(value, Boolean):
        if type(value.value) is not bool:
            raise OracleError("semantic_validity", "semantic.unsupported_value")
        return b"\xf5" if value.value else b"\xf4"
    if isinstance(value, Null):
        return b"\xf6"
    if isinstance(value, Array):
        if type(value.items) is not tuple:
            raise OracleError("semantic_validity", "semantic.unsupported_value")
        if len(value.items) > MAX_ARRAY_ITEMS:
            raise OracleError("resource", "resource.array_items")
        next_depth = open_depth + 1
        if next_depth > MAX_DEPTH:
            raise OracleError("resource", "resource.depth")
        body = b"".join(_encode_value(item, state, next_depth) for item in value.items)
        return _encode_argument(4, len(value.items)) + body
    if isinstance(value, Map):
        if type(value.entries) is not tuple:
            raise OracleError("semantic_validity", "semantic.unsupported_value")
        if len(value.entries) > MAX_MAP_ENTRIES:
            raise OracleError("resource", "resource.map_entries")
        next_depth = open_depth + 1
        if next_depth > MAX_DEPTH:
            raise OracleError("resource", "resource.depth")
        keyed: list[tuple[bytes, SemanticValue, SemanticValue]] = []
        seen: set[tuple[str, int | str]] = set()
        for entry in value.entries:
            if type(entry) is not tuple or len(entry) != 2:
                raise OracleError("semantic_validity", "semantic.unsupported_value")
            key, map_value = entry
            identity = _semantic_key_identity(key)
            if identity in seen:
                raise OracleError("semantic_validity", "semantic.map_duplicate")
            seen.add(identity)
            keyed.append((_encode_key_identity(identity), key, map_value))
        keyed.sort(key=lambda row: row[0])
        body_parts: list[bytes] = []
        for key_bytes, key, map_value in keyed:
            # Count and validate the semantic key through the ordinary encoder.
            encoded_key = _encode_value(key, state, next_depth)
            assert encoded_key == key_bytes
            body_parts.append(encoded_key)
            body_parts.append(_encode_value(map_value, state, next_depth))
        return _encode_argument(5, len(keyed)) + b"".join(body_parts)
    if isinstance(value, Bignum):
        raise OracleError("semantic_validity", "semantic.unsupported_bignum")
    if isinstance(value, Rational):
        if type(value.numerator) is not int or type(value.denominator) is not int:
            raise OracleError("semantic_validity", "semantic.unsupported_value")
        if value.denominator <= 0 or math.gcd(
            abs(value.numerator), value.denominator
        ) != 1:
            raise OracleError("semantic_validity", "semantic.rational_invalid")
        raise OracleError("semantic_validity", "semantic.unsupported_rational")
    if isinstance(value, Decimal):
        if type(value.coefficient) is not int or type(value.exponent) is not int:
            raise OracleError("semantic_validity", "semantic.unsupported_value")
        if (value.coefficient == 0 and value.exponent != 0) or (
            value.coefficient != 0 and value.coefficient % 10 == 0
        ):
            raise OracleError("semantic_validity", "semantic.decimal_non_normal")
        raise OracleError("semantic_validity", "semantic.unsupported_decimal")
    if isinstance(value, IEEEBits):
        if type(value.width) is not int or type(value.bits) is not int:
            raise OracleError("semantic_validity", "semantic.unsupported_value")
        if value.width not in (16, 32, 64) or value.bits < 0 or value.bits >= (
            1 << value.width
        ):
            raise OracleError("semantic_validity", "semantic.unsupported_value")
        raise OracleError("semantic_validity", "semantic.unsupported_ieee_bits")
    if isinstance(value, Interval):
        _validate_interval(value)
        raise OracleError("semantic_validity", "semantic.unsupported_interval")
    if isinstance(value, ExtensionSequence):
        if type(value.extensions) is not tuple or not all(
            isinstance(extension, Extension) for extension in value.extensions
        ):
            raise OracleError("semantic_validity", "semantic.unsupported_value")
        seen_ids: set[str] = set()
        for extension in value.extensions:
            if not isinstance(extension.type_id, str) or type(extension.critical) is not bool:
                raise OracleError("semantic_validity", "semantic.unsupported_value")
            if extension.type_id in seen_ids:
                raise OracleError("semantic_validity", "semantic.extension_duplicate")
            seen_ids.add(extension.type_id)
        if not value.extensions:
            raise OracleError("semantic_validity", "semantic.unsupported_value")
        code = (
            "semantic.extension_critical_unknown"
            if any(extension.critical for extension in value.extensions)
            else "semantic.extension_noncritical_unsupported"
        )
        raise OracleError("semantic_validity", code)
    if isinstance(value, Extension):
        if not isinstance(value.type_id, str) or type(value.critical) is not bool:
            raise OracleError("semantic_validity", "semantic.unsupported_value")
        code = (
            "semantic.extension_critical_unknown"
            if value.critical
            else "semantic.extension_noncritical_unsupported"
        )
        raise OracleError("semantic_validity", code)
    raise OracleError("semantic_validity", "semantic.unsupported_value")


def encode(value: SemanticValue) -> Result:
    """Encode one semantic value under the candidate profile."""

    try:
        encoded = _encode_value(value, _EncodeState(), 0)
        if len(encoded) > MAX_OUTPUT_BYTES:
            raise OracleError("resource", "resource.output_bytes")
    except OracleError as error:
        return error.as_result()
    return Result("accepted", "accepted", value=value, encoded=encoded)


def decode(
    data: bytes,
    *,
    profile_id: str = PROFILE_ID,
    expected_top_level: str | None = None,
) -> Result:
    """Strictly decode exactly one candidate-profile CBOR item."""

    if len(data) > MAX_INPUT_BYTES:
        return Result("resource", "resource.input_bytes")
    parser = _Parser(data)
    raw: RawItem | None = None
    try:
        raw = parser.parse_item(0)
        assert raw is not None
    except OracleError as error:
        return error.as_result(raw=raw)
    except OverflowError:
        return Result("operational", "operational.exception", raw=raw)

    if parser.position != len(data):
        parser.expectedness_issues.append(
            OracleError("expectedness", "expected.trailing_bytes")
        )
    if parser.validity_issues:
        return parser.validity_issues[0].as_result(raw=raw)
    if profile_id != PROFILE_ID:
        return Result("expectedness", "expected.profile_id", raw=raw)
    if expected_top_level is not None and raw.kind != expected_top_level:
        return Result("expectedness", "expected.top_level", raw=raw)
    if parser.expectedness_issues:
        return parser.expectedness_issues[0].as_result(raw=raw)
    if parser.profile_issues:
        return parser.profile_issues[0].as_result(raw=raw)
    value = _raw_to_semantic(raw)
    return Result("accepted", "accepted", value=value, raw=raw)


def _raw_to_semantic(raw: RawItem) -> SemanticValue:
    if raw.kind == "unsigned":
        assert raw.argument is not None
        return Integer(raw.argument)
    if raw.kind == "negative":
        assert raw.argument is not None
        return Integer(-1 - raw.argument)
    if raw.kind == "bytes":
        assert raw.data is not None
        return ByteString(raw.data)
    if raw.kind == "text":
        assert raw.text is not None
        return TextString(raw.text)
    if raw.kind == "array":
        return Array(_raw_to_semantic(item) for item in raw.items)
    if raw.kind == "map":
        return Map(
            (_raw_to_semantic(entry.key), _raw_to_semantic(entry.value))
            for entry in raw.entries
        )
    if raw.kind == "simple":
        if raw.argument == 20:
            return Boolean(False)
        if raw.argument == 21:
            return Boolean(True)
        if raw.argument == 22:
            return NULL
    raise AssertionError(f"non-profile raw item reached semantic conversion: {raw.kind}")


def _decimal_spelling(value: Any) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"-?(0|[1-9][0-9]*)", value):
        raise OracleError("semantic_validity", "semantic.unsupported_value")
    return value


def _parse_profile_integer(value: Any) -> int:
    spelling = _decimal_spelling(value)
    negative = spelling.startswith("-")
    magnitude = spelling[1:] if negative else spelling
    limit = str(1 << 64) if negative else str(MAX_INTEGER)
    if len(magnitude) > len(limit) or (
        len(magnitude) == len(limit) and magnitude > limit
    ):
        raise OracleError("semantic_validity", "semantic.integer_range")
    return int(spelling)


def _parse_small_decimal(value: Any) -> int:
    """Parse bounded diagnostic metadata without host digit-limit behavior."""

    spelling = _decimal_spelling(value)
    magnitude = spelling[1:] if spelling.startswith("-") else spelling
    if len(magnitude) > 20:
        raise OracleError("semantic_validity", "semantic.unsupported_value")
    return int(spelling)


def _require_object_fields(
    obj: dict[str, Any], required: set[str], optional: set[str] = frozenset()
) -> None:
    if set(obj) != required | (set(obj) & optional) or not required <= set(obj):
        raise OracleError("semantic_validity", "semantic.unsupported_value")


def semantic_from_typed_json(
    obj: Any,
    *,
    _open_depth: int = 0,
    _state: _TypedJsonState | None = None,
) -> SemanticValue:
    """Parse the diagnostic typed-JSON projection without numeric coercion."""

    state = _TypedJsonState() if _state is None else _state
    state.item()

    if not isinstance(obj, dict) or not isinstance(obj.get("type"), str):
        raise OracleError("semantic_validity", "semantic.unsupported_value")
    kind = obj["type"]
    if kind == "integer":
        _require_object_fields(obj, {"type", "value"})
        return Integer(_parse_profile_integer(obj["value"]))
    if kind == "bytes":
        _require_object_fields(obj, {"type", "hex"})
        value = obj["hex"]
        if not isinstance(value, str) or len(value) % 2 or not re.fullmatch(
            r"[0-9a-f]*", value
        ):
            raise OracleError("semantic_validity", "semantic.unsupported_value")
        return ByteString(bytes.fromhex(value))
    if kind == "text":
        _require_object_fields(obj, {"type", "value"})
        if not isinstance(obj["value"], str):
            raise OracleError("semantic_validity", "semantic.unsupported_value")
        return TextString(obj["value"])
    if kind == "array":
        _require_object_fields(obj, {"type", "items"})
        if not isinstance(obj["items"], list):
            raise OracleError("semantic_validity", "semantic.unsupported_value")
        if len(obj["items"]) > MAX_ARRAY_ITEMS:
            raise OracleError("resource", "resource.array_items")
        next_depth = _open_depth + 1
        if next_depth > MAX_DEPTH:
            raise OracleError("resource", "resource.depth")
        return Array(
            semantic_from_typed_json(
                item, _open_depth=next_depth, _state=state
            )
            for item in obj["items"]
        )
    if kind == "map":
        _require_object_fields(obj, {"type", "entries"})
        if not isinstance(obj["entries"], list):
            raise OracleError("semantic_validity", "semantic.unsupported_value")
        if len(obj["entries"]) > MAX_MAP_ENTRIES:
            raise OracleError("resource", "resource.map_entries")
        next_depth = _open_depth + 1
        if next_depth > MAX_DEPTH:
            raise OracleError("resource", "resource.depth")
        entries: list[tuple[SemanticValue, SemanticValue]] = []
        for entry in obj["entries"]:
            if not isinstance(entry, dict) or set(entry) != {"key", "value"}:
                raise OracleError("semantic_validity", "semantic.unsupported_value")
            entries.append(
                (
                    semantic_from_typed_json(
                        entry["key"], _open_depth=next_depth, _state=state
                    ),
                    semantic_from_typed_json(
                        entry["value"], _open_depth=next_depth, _state=state
                    ),
                )
            )
        return Map(entries)
    if kind == "boolean":
        _require_object_fields(obj, {"type", "value"})
        if type(obj["value"]) is not bool:
            raise OracleError("semantic_validity", "semantic.unsupported_value")
        return Boolean(obj["value"])
    if kind == "null":
        _require_object_fields(obj, {"type"})
        return NULL
    if kind == "bignum":
        _require_object_fields(obj, {"type", "value"})
        return Bignum(_decimal_spelling(obj["value"]))
    if kind == "rational":
        _require_object_fields(obj, {"type", "numerator", "denominator"})
        return Rational(
            _parse_small_decimal(obj["numerator"]),
            _parse_small_decimal(obj["denominator"]),
        )
    if kind == "decimal":
        _require_object_fields(obj, {"type", "coefficient", "exponent"})
        return Decimal(
            _parse_small_decimal(obj["coefficient"]),
            _parse_small_decimal(obj["exponent"]),
        )
    if kind == "ieee_bits":
        _require_object_fields(obj, {"type", "width", "bits_hex"})
        if type(obj["width"]) is not int or not isinstance(obj["bits_hex"], str):
            raise OracleError("semantic_validity", "semantic.unsupported_value")
        try:
            bits = int(obj["bits_hex"], 16)
        except ValueError as error:
            raise OracleError(
                "semantic_validity", "semantic.unsupported_value"
            ) from error
        return IEEEBits(obj["width"], bits)
    if kind == "interval":
        _require_object_fields(obj, {"type", "lower", "upper", "closure"})
        if not isinstance(obj["closure"], str):
            raise OracleError("semantic_validity", "semantic.unsupported_value")
        next_depth = _open_depth + 1
        if next_depth > MAX_DEPTH:
            raise OracleError("resource", "resource.depth")
        return Interval(
            semantic_from_typed_json(
                obj["lower"], _open_depth=next_depth, _state=state
            ),
            semantic_from_typed_json(
                obj["upper"], _open_depth=next_depth, _state=state
            ),
            obj["closure"],
        )
    if kind == "extension":
        _require_object_fields(obj, {"type", "type_id", "critical", "body"})
        if not isinstance(obj["type_id"], str) or type(obj["critical"]) is not bool:
            raise OracleError("semantic_validity", "semantic.unsupported_value")
        next_depth = _open_depth + 1
        if next_depth > MAX_DEPTH:
            raise OracleError("resource", "resource.depth")
        return Extension(
            obj["type_id"],
            obj["critical"],
            semantic_from_typed_json(
                obj["body"], _open_depth=next_depth, _state=state
            ),
        )
    if kind == "extension_sequence":
        _require_object_fields(obj, {"type", "extensions"})
        if not isinstance(obj["extensions"], list):
            raise OracleError("semantic_validity", "semantic.unsupported_value")
        if len(obj["extensions"]) > MAX_TOTAL_ITEMS:
            raise OracleError("resource", "resource.total_items")
        next_depth = _open_depth + 1
        if next_depth > MAX_DEPTH:
            raise OracleError("resource", "resource.depth")
        extensions: list[Extension] = []
        for extension_obj in obj["extensions"]:
            extension = semantic_from_typed_json(
                extension_obj, _open_depth=next_depth, _state=state
            )
            if not isinstance(extension, Extension):
                raise OracleError("semantic_validity", "semantic.unsupported_value")
            extensions.append(extension)
        return ExtensionSequence(extensions)
    raise OracleError("semantic_validity", "semantic.unsupported_value")


def typed_json_from_semantic(value: SemanticValue) -> dict[str, Any]:
    """Return the deterministic typed-JSON projection of a semantic value."""

    if isinstance(value, Integer):
        return {"type": "integer", "value": str(value.value)}
    if isinstance(value, ByteString):
        return {"hex": value.value.hex(), "type": "bytes"}
    if isinstance(value, TextString):
        return {"type": "text", "value": value.value}
    if isinstance(value, Array):
        return {
            "items": [typed_json_from_semantic(item) for item in value.items],
            "type": "array",
        }
    if isinstance(value, Map):
        sorted_entries = sorted(
            value.entries,
            key=lambda entry: _encode_key_identity(_semantic_key_identity(entry[0])),
        )
        return {
            "entries": [
                {
                    "key": typed_json_from_semantic(key),
                    "value": typed_json_from_semantic(map_value),
                }
                for key, map_value in sorted_entries
            ],
            "type": "map",
        }
    if isinstance(value, Boolean):
        return {"type": "boolean", "value": value.value}
    if isinstance(value, Null):
        return {"type": "null"}
    raise OracleError("semantic_validity", "semantic.unsupported_value")


def _identifier_bytes(value: str, code: str) -> bytes:
    try:
        raw = value.encode("ascii", "strict")
    except (AttributeError, UnicodeEncodeError) as error:
        raise OracleError("digest_verification", code) from error
    if not _IDENTIFIER_RE.fullmatch(raw):
        raise OracleError("digest_verification", code)
    return raw


def _lp(component: bytes) -> bytes:
    if len(component) > 0xFFFF_FFFF:
        raise OracleError("digest_verification", "digest.component_length")
    return struct.pack(">I", len(component)) + component


def build_digest_frame(
    *,
    purpose_id: str,
    object_class_schema_id: str,
    payload: bytes,
    algorithm_id: str = ALGORITHM_ID,
    profile_id: str = PROFILE_ID,
    framing_id: str = FRAMING_ID,
) -> Result:
    """Build and hash the frame; bind, but do not validate, the schema ID."""

    try:
        purpose = _identifier_bytes(purpose_id, "digest.purpose")
        algorithm = _identifier_bytes(algorithm_id, "digest.algorithm")
        profile = _identifier_bytes(profile_id, "digest.profile")
        schema = _identifier_bytes(
            object_class_schema_id, "digest.object_class_schema"
        )
        framing = _identifier_bytes(framing_id, "digest.framing")
        if algorithm_id != ALGORITHM_ID:
            raise OracleError("digest_verification", "digest.algorithm")
        if profile_id != PROFILE_ID:
            raise OracleError("digest_verification", "digest.profile")
        if framing_id != FRAMING_ID:
            raise OracleError("digest_verification", "digest.framing")
        if not payload:
            raise OracleError("digest_verification", "digest.payload")
        if len(payload) > MAX_INPUT_BYTES:
            raise OracleError("digest_verification", "digest.length")
        payload_result = decode(payload, profile_id=profile_id)
        if not payload_result.accepted:
            raise OracleError("digest_verification", "digest.payload")
        components = (purpose, algorithm, profile, schema, framing, payload)
        frame = DIGEST_MAGIC + b"".join(_lp(component) for component in components)
        if len(frame) > MAX_DIGEST_FRAME_BYTES:
            raise OracleError("digest_verification", "digest.length")
    except OracleError as error:
        return error.as_result()
    digest = hashlib.sha256(frame).digest()
    return Result("accepted", "accepted", frame=frame, digest=digest)


def verify_digest_frame(
    *,
    frame: bytes,
    digest: bytes,
    expected_purpose_id: str,
    expected_object_class_schema_id: str,
    expected_algorithm_id: str = ALGORITHM_ID,
    expected_profile_id: str = PROFILE_ID,
    expected_framing_id: str = FRAMING_ID,
) -> Result:
    """Verify profile bytes and identifier binding, not schema conformance."""

    try:
        if len(frame) > MAX_DIGEST_FRAME_BYTES:
            raise OracleError("digest_verification", "digest.length")
        if len(digest) != hashlib.sha256().digest_size:
            raise OracleError("digest_verification", "digest.length")
        if not frame.startswith(DIGEST_MAGIC):
            raise OracleError("digest_verification", "digest.magic")
        position = len(DIGEST_MAGIC)
        components: list[bytes] = []
        for index in range(6):
            if position + 4 > len(frame):
                raise OracleError(
                    "digest_verification", "digest.component_length"
                )
            length = int.from_bytes(frame[position : position + 4], "big")
            position += 4
            limit = MAX_IDENTIFIER_BYTES if index < 5 else MAX_INPUT_BYTES
            if length > limit:
                code = "digest.component_length" if index < 5 else "digest.length"
                raise OracleError("digest_verification", code)
            if position + length > len(frame):
                raise OracleError(
                    "digest_verification", "digest.component_length"
                )
            components.append(frame[position : position + length])
            position += length
        if position != len(frame):
            raise OracleError("digest_verification", "digest.trailing_bytes")

        purpose, algorithm, profile, schema, framing, payload = components
        expected = (
            _identifier_bytes(expected_purpose_id, "digest.purpose"),
            _identifier_bytes(expected_algorithm_id, "digest.algorithm"),
            _identifier_bytes(expected_profile_id, "digest.profile"),
            _identifier_bytes(
                expected_object_class_schema_id, "digest.object_class_schema"
            ),
            _identifier_bytes(expected_framing_id, "digest.framing"),
        )
        names = (
            "digest.purpose",
            "digest.algorithm",
            "digest.profile",
            "digest.object_class_schema",
            "digest.framing",
        )
        for component, wanted, code in zip(components[:5], expected, names):
            if component != wanted:
                raise OracleError("digest_verification", code)
        if algorithm != ALGORITHM_ID.encode("ascii") or expected_algorithm_id != ALGORITHM_ID:
            raise OracleError("digest_verification", "digest.algorithm")
        if profile != PROFILE_ID.encode("ascii") or expected_profile_id != PROFILE_ID:
            raise OracleError("digest_verification", "digest.profile")
        if framing != FRAMING_ID.encode("ascii") or expected_framing_id != FRAMING_ID:
            raise OracleError("digest_verification", "digest.framing")
        if not purpose:
            raise OracleError("digest_verification", "digest.purpose")
        if not schema:
            raise OracleError(
                "digest_verification", "digest.object_class_schema"
            )
        if not payload:
            raise OracleError("digest_verification", "digest.payload")
        if not all(_IDENTIFIER_RE.fullmatch(component) for component in components[:5]):
            for component, code in zip(components[:5], names):
                if not _IDENTIFIER_RE.fullmatch(component):
                    raise OracleError("digest_verification", code)
        payload_result = decode(payload, profile_id=expected_profile_id)
        if not payload_result.accepted:
            raise OracleError("digest_verification", "digest.payload")
        if not hmac.compare_digest(hashlib.sha256(frame).digest(), digest):
            raise OracleError("digest_verification", "digest.mismatch")
    except OracleError as error:
        return error.as_result()
    return Result("accepted", "accepted", value=payload_result.value, frame=frame, digest=digest)


def diagnostic_object(result: Result, *, include_artifacts: bool = True) -> dict[str, Any]:
    obj: dict[str, Any] = {
        "code": result.code,
        "diagnostic_version": DIAGNOSTIC_ID,
        "profile_id": PROFILE_ID,
        "result_class": result.result_class,
        "status": "accepted" if result.accepted else "rejected",
    }
    if result.value is not None:
        obj["value"] = typed_json_from_semantic(result.value)
    if include_artifacts and result.encoded is not None:
        obj["cbor_hex"] = result.encoded.hex()
    if include_artifacts and result.frame is not None:
        obj["frame_hex"] = result.frame.hex()
    if include_artifacts and result.digest is not None:
        obj["digest_hex"] = result.digest.hex()
    obj.update(result.details)
    return obj


def render_diagnostic(result: Result, *, include_artifacts: bool = True) -> bytes:
    """Render canonical JSON, falling back to a bounded resource summary."""

    rendered = (
        json.dumps(
            diagnostic_object(result, include_artifacts=include_artifacts),
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")
    if len(rendered) <= MAX_DIAGNOSTIC_BYTES:
        return rendered
    summary = {
        "code": "resource.diagnostic_bytes",
        "diagnostic_version": DIAGNOSTIC_ID,
        "profile_id": PROFILE_ID,
        "result_class": "resource",
        "status": "rejected",
        "validation_code": result.code,
        "validation_result_class": result.result_class,
        "validation_status": "accepted" if result.accepted else "rejected",
    }
    bounded = (
        json.dumps(summary, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
        + "\n"
    ).encode("utf-8")
    assert len(bounded) <= MAX_DIAGNOSTIC_BYTES
    return bounded
