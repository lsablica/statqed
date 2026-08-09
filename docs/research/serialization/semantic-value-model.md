# SQ-0005 language-neutral semantic value model

Status: **Experimental research note; non-normative**.

This note proposes the semantic input to the SQ-0005 encoding experiments. It
does not accept RFC-0001, define schema v0, or make prototype behavior
authoritative. The candidate byte profile is described separately in
`profile-candidate.md`.

## Scope and boundary

The model is deliberately data-free. It covers generic structured values and
the exact distinctions that an encoder or strict decoder must preserve. It
does not define a table, a physical-to-logical lowering, a data identity, or a
data digest. `null` below is one literal value; this note assigns it no
missingness meaning.

The central rule is:

> semantic values are defined before bytes, and raw map entries are preserved
> before any host-language map is constructed.

Three layers must not be collapsed:

1. **Raw CBOR item:** parser output retaining original heads, lengths, tag and
   float bits, and every map entry in wire order.
2. **Profile semantic value:** one of the accepted constructors below, after
   CBOR validity, duplicate, profile, shape, and semantic checks.
3. **Host representation:** an implementation convenience which has no
   authority to merge keys, coerce numbers, normalize text, or invent a
   fallback.

## Raw parser model

At minimum, one conformance decoder must expose the following lossless parser
result before semantic conversion:

```text
Raw = Unsigned(head, argument)
    | Negative(head, argument)
    | Bytes(head, chunks)
    | Text(head, raw_utf8_chunks)
    | Array(head, [Raw])
    | Map(head, [RawEntry])
    | Tag(head, tag_number, Raw)
    | Simple(head, simple_number)
    | Float16(bits) | Float32(bits) | Float64(bits)

RawEntry = (raw_key: Raw, raw_value: Raw)
```

`head` retains the original additional-information width and whether a
container was indefinite. `chunks` retain indefinite-string chunk boundaries.
A native dictionary, normalized string, host float, or interpreted tag is not
a valid substitute for this layer.

## Semantic constructors

The candidate's accepted subset is intentionally small. Unsupported
constructors remain distinct so producers fail explicitly and later profiles
cannot inherit accidental host-language coercions.

| Constructor | Well-formed members and equality | Candidate v1 disposition | Bytes in candidate v1 |
|---|---|---|---|
| `Integer(n)` | Exact mathematical integer in `[-2^64, 2^64 - 1]`; equality by integer value. | Accepted. | CBOR major type 0 or 1, shortest argument. |
| `Bignum(n)` | Exact mathematical integer outside the `Integer` range; equality by integer value within this constructor. | Unsupported. No coercion to text, bytes, float, or decimal. | None. Tags 2 and 3 are rejected. |
| `Rational(p,q)` | `q > 0`, `gcd(abs(p),q) = 1`; equality is structural after this required normal form. | Unsupported. `2/4`, a negative denominator, and denominator zero are rejected semantic inputs, not silently normalized. | None. Tag 30 and array fallbacks are rejected or remain ordinary arrays, respectively. |
| `Decimal(coefficient,exponent)` | Exact `coefficient * 10^exponent`; zero is `(0,0)` and a nonzero coefficient is not divisible by 10. Equality is structural after this required normal form. | Unsupported. It is never equal to an integer or rational merely because their mathematical values coincide. | None. Tag 4 and text fallbacks are rejected. |
| `IEEEBits(width,bits)` | `width` is 16, 32, or 64 and `bits` is exactly that many bits; equality is width-and-bit equality. Thus `+0` and `-0` differ, as do NaN payloads and signs. | Unsupported, including finite values and infinities. | None. Every CBOR float encoding is rejected. |
| `ByteString(bytes)` | Finite byte sequence; equality byte-for-byte. | Accepted within resource limits. | Definite-length CBOR major type 2, shortest length head. |
| `TextString(scalars)` | Finite sequence of Unicode scalar values; equality by exact scalar sequence. | Accepted within resource limits. No normalization, case folding, or locale processing. | Definite-length CBOR major type 3 containing shortest-form valid UTF-8. |
| `Array(values)` | Ordered finite sequence; equality is elementwise and order-sensitive. | Accepted recursively within resource limits. | Definite-length CBOR major type 4. |
| `Map(entries)` | Finite map with unique scalar keys from the allowed key subset below; equality is the same set of key/value pairs independent of insertion order. | Accepted recursively after raw-entry duplicate checking. | Definite-length CBOR major type 5 with candidate profile ordering. |
| `MapEntrySequence(entries)` | Ordered sequence of key/value pairs, including possible duplicates. | Parser-only evidence, never an accepted semantic value. | It is the retained interpretation of a raw major-type-5 item before validation. |
| `Boolean(value)` | `true` or `false`; equality only within `Boolean`. | Accepted. A language boolean is not an integer. | CBOR simple values 21 or 20 (`f5` or `f4`). |
| `Null` | One literal; equal only to `Null`. | Accepted with no additional meaning. | CBOR simple value 22 (`f6`). |
| `Interval(kind,lower,upper,closure)` | Candidate research shape only: endpoints have the same exact ordered kind (`Integer`, `Rational`, or `Decimal`), `lower <= upper`, and closure flags are explicit. Equality is structural. | Unsupported. Reversed bounds, mixed endpoint kinds, and IEEE/NaN endpoints are invalid semantic inputs. | None. An untagged array is only an `Array`, not an interval. |
| `Extension(type_id,critical,body)` | Abstract extension value with exact text identifier, Boolean criticality, and a semantic-value body; equality is structural. An extension sequence must have unique `type_id` values. | Unsupported in candidate v1. No extension identifier or payload meaning is frozen here. | None. An ordinary map/array is not reinterpreted as an extension, and arbitrary CBOR tags are rejected. |

The bignum, rational, decimal, IEEE-bit, interval, and extension rows make the
rejection boundary explicit; they do not reserve encodings or promise later
support.

### Allowed map keys

Candidate v1 map keys are restricted to the two accepted scalar classes needed
for field identifiers and exact integer labels:

```text
Integer | TextString
```

Byte strings, booleans, null, arrays, maps, tags, floats, and every unsupported
constructor are forbidden in key position even though some remain valid as map
values. Key equivalence is the typed equality above. In particular:

- canonically equivalent Unicode sequences are distinct unless their scalar
  sequences are identical;
- two different wire encodings that decode to the same allowed scalar key are
  duplicates, even if one encoding is non-preferred.

The decoder must check duplicates over the retained `MapEntrySequence` before
constructing a native map. It must not apply first-wins, last-wins, or silent
deduplication. Duplicate detection precedes deterministic ordering checks so a
fully parsed map containing both faults still reports the duplicate class.

### Extension sequences

The abstract `Extension` constructor exists only to make producer failure
explicit. Candidate v1 has no known extension identifiers and accepts zero
extensions. When a producer attempts to encode an extension sequence, it must
first reject duplicate identifiers across the complete sequence. If the
unique sequence contains any critical extension, it then returns
`semantic.extension_critical_unknown`; otherwise it returns
`semantic.extension_noncritical_unsupported`. This result is independent of
sequence order. It may not discard either kind. This supplies stable negative
cases without assigning an extension wire format.

## Equality and non-equivalence

Equality is typed and structural. There is no generic "numeric equality" or
host-language loose equality:

```text
Integer(1) != Rational(1,1)
Integer(1) != Decimal(1,0)
Integer(0) != IEEEBits(64, +0 bits)
TextString("1") != Integer(1)
ByteString(31) != TextString("1")
Array([]) != Map({})
Boolean(false) != Integer(0)
```

Map insertion order is not semantic. Array order is semantic. A raw map entry
sequence is evidence used to establish uniqueness and ordering; it is not
equal to an accepted `Map`.

## Normalization policy

The strict wire decoder performs no value-changing normalization.

- Non-preferred CBOR is rejected, not decoded and re-encoded to success.
- Text is preserved exactly; NFC/NFD conversion, case folding, and removal of
  controls or noncharacters are forbidden in the profile layer.
- Map sorting is an encoder operation over an already valid semantic map. It
  does not license a decoder to repair unordered bytes.
- Accepted integers have one deterministic serialization, but their value is
  not converted to another numeric constructor.
- Unsupported numeric and extension constructors fail instead of falling back
  to strings, arrays, maps, tags, or host serialization.

A frontend may offer a separately named, non-normative import helper, but that
helper must disclose every conversion and produce a value which is checked
again. It is not part of canonical-byte validation.

## Semantic producer contract

A producer that claims to construct this model must:

1. expose integers without passing through a binary float;
2. distinguish booleans from integers even in languages where one subclasses
   or coerces to the other;
3. construct maps from an entry sequence and reject duplicate semantic keys
   before creating a native dictionary;
4. preserve UTF-8-decodable text as an exact scalar sequence;
5. reject cycles, functions, references, custom objects, undefined/simple
   sentinels, and unsupported constructors with stable codes;
6. enforce semantic resource limits before encoding; and
7. never stringify or use a language's generic object serializer as fallback.

## Failure classes at the semantic boundary

These are candidate stable class names; profile parsing adds the wire-level
classes in `profile-candidate.md`.

| Code | Condition |
|---|---|
| `semantic.integer_range` | Integer lies outside the accepted direct-CBOR range. |
| `semantic.unsupported_bignum` | A `Bignum` is supplied. |
| `semantic.unsupported_rational` | A well-formed `Rational` is supplied. |
| `semantic.rational_invalid` | Denominator is zero/negative or the pair is not reduced. |
| `semantic.unsupported_decimal` | A well-formed `Decimal` is supplied. |
| `semantic.decimal_non_normal` | Decimal has removable powers of ten or a noncanonical zero exponent. |
| `semantic.unsupported_ieee_bits` | An IEEE bit-pattern value is supplied. |
| `semantic.unsupported_interval` | A well-formed interval is supplied. |
| `semantic.interval_invalid` | Endpoints are mixed, unordered, or otherwise outside the research shape. |
| `semantic.extension_duplicate` | An extension sequence repeats an exact `type_id`. |
| `semantic.extension_critical_unknown` | An unknown critical extension is supplied. |
| `semantic.extension_noncritical_unsupported` | An unknown noncritical extension is supplied; it is not ignored. |
| `semantic.map_key_type` | A map key is not in the allowed scalar subset. |
| `semantic.map_duplicate` | Two producer entries have equal typed keys. |
| `semantic.unsupported_value` | Any other unmodeled language value is supplied. |

## Examples

Accepted semantic values:

```text
Integer(0)
Integer(-18446744073709551616)
ByteString(00 ff)
TextString(U+0065 U+0301)
Array([Boolean(false), Null])
Map([(Integer(-1), Null), (Integer(100), Boolean(true))])
```

Accepted but unequal Unicode values:

```text
TextString(U+00E9)             # composed e-acute
TextString(U+0065 U+0301)      # e plus combining acute
```

They remain distinct values and, in key position, distinct keys. Controls and
Unicode noncharacters are also preserved by the generic text layer when their
UTF-8 is valid; a schema may impose a narrower identifier policy.

Rejected or unsupported semantic inputs:

```text
Integer(18446744073709551616)        # use of the unsupported bignum domain
Rational(2, 4)                       # non-normal
Rational(1, 0)                       # invalid
Decimal(1200, -2)                    # non-normal
IEEEBits(64, 0x8000000000000000)     # exact -0, but unsupported
Interval(Integer, 2, 1, closed)      # reversed
Map([(TextString("x"), Integer(1)),
     (TextString("x"), Integer(2))]) # duplicate before native-map collapse
Extension("example", false, Null)    # unsupported, not silently ignored
```

## Nonexamples and prohibited shortcuts

- A Python `dict`, R named list, Julia `Dict`, or Rust `HashMap` received after
  duplicate collapse is not evidence that the source map was valid.
- A host `double` containing `1.0` is not an exact `Integer(1)` constructor.
- JSON number/text round-trips are not semantic or byte conformance.
- Unicode display equality is not text equality.
- Decode/re-encode equality is not strict input validation.
- A digest match is not semantic equality unless the profile, schema, purpose,
  framing, and algorithm checks have already succeeded, and even then the
  cryptographic assumptions remain explicit.

## Open review questions and blockers

1. **Range sufficiency:** reviewers must confirm that the asymmetric direct
   CBOR integer range is sufficient for the data-free foundation schemas. Any
   bignum need requires a new, fully reviewed profile decision.
2. **Narrow map keys:** interoperability and schema reviewers must confirm that
   `Integer | TextString` covers the data-free foundation schemas. The broader
   scalar-key alternative (`ByteString`, `Boolean`, and `Null` in key position)
   is rejected for v1 because no concrete foundation need justifies its extra
   equality and conformance surface.
3. **No Unicode normalization:** source and security review must approve exact
   scalar preservation and require schema-level restrictions where identifiers
   need stronger confusable/control policy.
4. **Unsupported exact numeric classes:** future support must choose encodings
   and normal forms in a new profile version. It must not be inferred from the
   research shapes above.
5. **Extension abstraction:** schema work must either define a reviewed
   extension representation or retain the zero-extension rule. This note does
   not reserve an identifier grammar or wire form.
6. **Implementation evidence:** both independent decoders must demonstrate raw
   entry preservation and detect semantic duplicates formed from different
   CBOR serializations before this model can support an Accepted RFC.

## Source anchors

- [RFC 8949 sections 2, 3, 4, and 5](https://www.rfc-editor.org/rfc/rfc8949.html)
  for the generic data model, preferred/deterministic serialization,
  well-formedness, validity, expectedness, map equality, and duplicate handling.
- [RFC 8610](https://www.rfc-editor.org/rfc/rfc8610.html), as updated by
  [RFC 9682](https://www.rfc-editor.org/rfc/rfc9682.html), for the structural
  CDDL boundary; CDDL matching is not semantic or byte-profile validation.

The current draft source-lineage records are
`source-audits/encoding/SA-SQ0005-CBOR.yaml` and
`source-audits/encoding/SA-SQ0005-CDDL.yaml`. This note is reconciled to their
recommended core-order, closed-tag, strict-rejection, and published-CDDL
boundaries; the audits and this note still require independent review.
