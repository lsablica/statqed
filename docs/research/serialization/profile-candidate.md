# SQ-0005 deterministic CBOR profile candidate

Status: **Experimental research note; non-normative**.

Candidate identifier: `statqed.cbor-core.v1`.

This is a complete candidate for prototype and adversarial testing. It does
not accept RFC-0001, update ADR-0004, freeze schema v0, or make any encoder an
authority. Acceptance still requires the task contract's source,
interoperability, security, formal, cryptographic, conformance, CI, and
integration evidence.

The profile is deliberately smaller than the full CBOR generic data model. It
uses RFC 8949 core deterministic encoding, accepts only the semantic
constructors in `semantic-value-model.md`, rejects all tags and floats, and
strictly rejects rather than repairs non-profile wire input.

## Candidate decisions at a glance

| Topic | Candidate decision | Rejected alternative |
|---|---|---|
| Base format | One well-formed, valid CBOR data item. | CBOR sequences, trailing items, custom binary, or JSON as normative bytes. |
| Deterministic option | RFC 8949 section 4.2.1 **core deterministic encoding**, including bytewise lexicographic map-key order. | Length-first ordering retained by RFC 8949 for RFC 7049 compatibility; StatQED has no such compatibility requirement. |
| Preferred forms | Required for every integer and length head. | Over-wide heads or library-default forms. |
| Containers/strings | Definite length only. | Indefinite arrays, maps, strings, or chunks. |
| Values | Direct-range integers, bytes, UTF-8 text, arrays, maps, booleans, and null. | Bignums, rationals, decimals, IEEE values/floats, intervals, undefined, other simple values, and extensions. |
| Map keys | Direct-range integer or text. | Byte-string, boolean, null, composite, tagged, floating, extension, or unsupported numeric keys. |
| Map duplicates | Reject typed-equal keys before native-map collapse and before order validation. | First-wins, last-wins, deduplication, or checking only encoded-byte equality. |
| Unicode | Preserve exact Unicode scalar sequence; no normalization. | NFC/NFD conversion, case folding, locale handling, or confusable folding. |
| Tags | No tag number is accepted. | Whitelisting speculative tags or treating unknown tags as transparent. |
| Extensions | Zero extensions in v1; critical and noncritical attempts both fail explicitly. | Ignoring unknown noncritical values or mapping extensions onto arbitrary tags. |
| Decoder | Strict validation; no decode-and-re-encode acceptance. | Silent normalization of decodable input. |
| CDDL | Published RFC 8610 as updated by RFC 9682, restricted to a tested common structural subset in standalone files; no module/import draft. | Optional RFC 9165/RFC 9741 controls or treating CDDL as byte, duplicate, semantic, or digest validation. |
| Digest framing | SHA-256 over fixed magic plus six unsigned-32-bit length-prefixed components binding purpose, algorithm, profile, object-class/schema, framing, and payload. | Recursive CBOR framing, raw concatenation, implicit purpose, fallback, truncation, or an unframed payload hash. |

## Accepted byte grammar

The top level is exactly one item and consumes the complete input. The
following CBOR major types are accepted:

- major type 0: unsigned integer;
- major type 1: negative integer;
- major type 2: byte string;
- major type 3: text string;
- major type 4: array;
- major type 5: map;
- major type 7: simple values `false`, `true`, and `null` only.

Major type 6 (tags), all floating-point encodings, `undefined`, unassigned
simple values, and break are forbidden. Reserved additional-information values
remain non-well-formed under RFC 8949 rather than merely non-profile.

### Preferred integer and length heads

Every argument for major types 0 through 5 uses its shortest RFC 8949 head:

| Argument | Additional information and following bytes |
|---|---|
| `0..23` | argument in the initial byte; no following argument bytes |
| `24..255` | additional information 24 plus one unsigned byte |
| `256..65535` | additional information 25 plus two big-endian bytes |
| `65536..4294967295` | additional information 26 plus four big-endian bytes |
| `4294967296..18446744073709551615` | additional information 27 plus eight big-endian bytes |

For `Integer(n) >= 0`, the argument is `n` in major type 0. For
`Integer(n) < 0`, the argument is `-1-n` in major type 1. This yields the exact
accepted range `[-2^64, 2^64-1]`. No tag-based extension of that range exists
in v1.

Examples:

| Semantic value | Accepted hex |
|---|---|
| `Integer(0)` | `00` |
| `Integer(23)` | `17` |
| `Integer(24)` | `1818` |
| `Integer(-24)` | `37` |
| `Integer(-25)` | `3818` |
| `Integer(65536)` | `1a00010000` |
| `Boolean(false)` | `f4` |
| `Boolean(true)` | `f5` |
| `Null` | `f6` |

`1800` for integer zero is well-formed and decodable but rejected as
`profile.non_preferred_head`.

### Byte and text strings

Strings use definite length and a preferred length head. The length is the
number of content bytes. Byte strings preserve arbitrary bytes. Text strings
must be valid shortest-form UTF-8 for a sequence of Unicode scalar values.
Overlong UTF-8, surrogates, out-of-range scalar encodings, invalid continuation
bytes, and truncated sequences fail CBOR validity.

No Unicode normalization is performed. For example:

| Text value | Accepted hex | Equality |
|---|---|---|
| U+00E9 | `62c3a9` | Distinct from the next row. |
| U+0065 U+0301 | `6365cc81` | Distinct from the previous row. |

Both are accepted and stay distinct as values and map keys. Valid encodings of
controls and Unicode noncharacters are preserved at this generic layer. A
schema may restrict identifiers, but it may not claim that the encoding
profile normalized them.

### Arrays

Arrays have a definite preferred length and contain that many accepted values
in order. Array equality and bytes are order-sensitive. Cyclic/shared-reference
graphs have no representation because tags are forbidden.

### Maps, raw entries, equality, and ordering

A map is first parsed as an ordered `MapEntrySequence`. Every key and value is
retained before validation and before any host-language dictionary is built.
Allowed keys are `Integer` and `TextString`. Byte strings, booleans, and null
remain accepted values but are forbidden in key position.

Validation of a completely parsed map occurs in this order:

1. validate every key as an allowed scalar semantic value;
2. compare typed semantic key equality over the raw entry sequence and reject
   any duplicate;
3. calculate each key's candidate deterministic encoding;
4. require strict unsigned bytewise lexicographic order of the complete
   deterministic key encodings; and
5. only then construct an implementation map, if desired.

The order comparison is over the complete canonical key encoding, not source
text, UTF-16 code units, locale order, a host hash, or the encoded value. Strict
increase also supplies a second duplicate defense, but it does not replace the
raw semantic duplicate scan.

Map semantic equality ignores insertion order after uniqueness has been
established. Map bytes use only the selected order. The following two-key case
discriminates the selected RFC 8949 core order from length-first ordering:

```text
semantic map: { Integer(-1): Null, Integer(100): Null }

accepted core order:     a2 18 64 f6 20 f6
rejected length-first:   a2 20 f6 18 64 f6
```

The second byte string is well-formed and otherwise valid but fails
`profile.map_order`.

A cross-major-type diagnostic uses `Integer(24)` (`1818`, two bytes) and the
empty `TextString` (`60`, one byte): core order puts `1818` first because
`0x18 < 0x60`, while length-first puts `60` first. Both keys are inside the
narrow accepted key model.

Duplicate comparison uses decoded typed equality even when a key uses a
non-preferred head. Thus `00` and `1800` in the same raw map both denote
`Integer(0)` for duplicate detection and produce `validity.map_duplicate`, not
two distinct keys and not a repaired map.

## Unsupported numeric and semantic classes

Candidate v1 rejects the following without fallback:

| Input class | Raw-wire outcome | Semantic-encoder outcome |
|---|---|---|
| Bignum / tags 2 and 3 | `profile.tag_forbidden` after the tagged item is parsed and basic validity is established. | `semantic.unsupported_bignum`. |
| Rational / tag 30 | `profile.tag_forbidden`; an untagged two-element array remains only an array. | Invalid normal forms fail `semantic.rational_invalid`; well-formed values fail `semantic.unsupported_rational`. |
| Decimal fraction / tag 4 | `profile.tag_forbidden`; text or array fallbacks do not acquire decimal meaning. | Non-normal values fail `semantic.decimal_non_normal`; well-formed values fail `semantic.unsupported_decimal`. |
| IEEE bit pattern or CBOR float | Any half/single/double float, finite or not, fails `profile.float_forbidden`. | `semantic.unsupported_ieee_bits`. |
| Interval | No implicit tag, array, or map interpretation exists. | Invalid bounds fail `semantic.interval_invalid`; otherwise `semantic.unsupported_interval`. |
| Extension | No tag or generic container acquires extension semantics. | Duplicate IDs, unknown critical, and unsupported noncritical cases use the distinct semantic codes in the value-model note. |

This includes signed zero, infinity, every NaN payload/sign, and finite CBOR
floats. Their bit distinctions can be tested by the raw parser, but none is an
accepted profile value. A future profile must be versioned and must settle its
own exact normal forms; it cannot silently expand `statqed.cbor-core.v1`.

## Tag and extension policy

No CBOR tag is transparent, ignorable, or accepted. A decoder must still parse
the complete tagged item with normal syntax and resource checks before
reporting `profile.tag_forbidden`; it must not skip unvalidated content based
only on the tag head. Nested tag depth is therefore measured during raw parse,
but the accepted maximum is zero.

The profile declares no understood tags for tag-specific validity checking.
Consequently, a well-formed tag whose content would mismatch a registered tag
definition still receives `profile.tag_forbidden`; malformed, invalid UTF-8,
duplicate-map, or resource faults inside its child take their earlier class.
This is a fixed conformance outcome, not permission for libraries to disagree
about whether to interpret the tag.

Within deterministic-profile checks, a non-preferred tag-number head receives
`profile.non_preferred_head` because that fault occurs at the tag head; a
preferred tag head around a valid child receives `profile.tag_forbidden`.
Neither outcome accepts or normalizes the tag.

Candidate v1 defines no extension wire representation and accepts an extension
count of zero. Unknown critical extensions fail closed. Unknown noncritical
extensions are also unsupported and must not be discarded. Duplicate
extension identifiers are rejected before unknown/critical disposition at the
semantic producer boundary. Ordinary arrays/maps cannot be relabeled as
extensions without a later schema and profile decision.

## Strict decoder and result taxonomy

The conformance interface returns exactly one result class plus a stable code.
Human prose and byte offsets are diagnostic and not stable API. The phases are
separate; success at one phase says nothing about later phases.

| Phase/result class | Candidate codes and meaning |
|---|---|
| `resource` | `resource.input_bytes`, `resource.output_bytes`, `resource.string_bytes`, `resource.array_items`, `resource.map_entries`, `resource.total_items`, `resource.depth`, `resource.diagnostic_bytes`. A declared size beyond a bound may fail immediately, before the body is read. |
| `well_formedness` | `wellformed.truncated`, `wellformed.reserved_additional`, `wellformed.unexpected_break`, `wellformed.indefinite_chunk_type`, `wellformed.length_overflow`, `wellformed.map_pair_missing`. The bytes do not form one processable CBOR item. |
| `validity` | `validity.invalid_utf8` and `validity.map_duplicate`. Duplicate detection uses the application key equality above and occurs before map collapse. Candidate v1 interprets no tags, so it does not apply tag-specific content-validity rules. |
| `expectedness` | `expected.single_item`, `expected.trailing_bytes`, `expected.map_key_type`, `expected.profile_id`, `expected.schema_id`, `expected.schema_version`, `expected.top_level`. These are well-formed/valid CBOR but not the kind or version requested by the application call. |
| `deterministic_profile` | `profile.non_preferred_head`, `profile.indefinite`, `profile.map_order`, `profile.tag_forbidden`, `profile.float_forbidden`, `profile.simple_forbidden`. These inputs are decodable but are not `statqed.cbor-core.v1` bytes. |
| `cddl_shape` | `shape.cddl_mismatch` with a versioned rule identifier. It establishes only failure to match the selected published-syntax CDDL rule. |
| `semantic_validity` | The `semantic.*` classes in the value-model note plus schema-owned invariants. It does not establish inferential, provenance, or kernel claims. |
| `digest_verification` | `digest.magic`, `digest.component_length`, `digest.trailing_bytes`, `digest.purpose`, `digest.algorithm`, `digest.profile`, `digest.object_class_schema`, `digest.framing`, `digest.payload`, `digest.length`, `digest.mismatch`. Digest verification is conditional on all preceding checks. |
| `accepted` | `accepted` only after every requested phase succeeds. The result names profile and schema identifiers. |

### Error precedence

Resource checks can terminate any phase when the decoder cannot safely finish.
Otherwise the precedence is:

```text
well_formedness
< validity (including a complete-map duplicate scan)
< expectedness
< deterministic_profile
< cddl_shape
< semantic_validity
< digest_verification
< accepted
```

Within a phase, parsing is depth-first and wire-order deterministic. For a
fully parsed map, duplicate checks precede order checks. Conformance fixtures
should isolate one primary fault; compound-fault fixtures must record the
precedence above rather than relying on language-specific parser prose.

A strict validation API never returns `accepted` merely because decoding and
re-encoding produced candidate bytes. A separately named diagnostic
canonicalizer may report what it would emit from a valid semantic value, but it
must not upgrade the raw input's validation result.

## Resource profile

The following are candidate acceptance limits for one structured object. They
are part of the profile identifier and apply before schema-specific smaller
limits:

| Resource | Inclusive limit | Counting rule |
|---|---:|---|
| Total input bytes | 1,048,576 | Entire byte slice presented to the single-item decoder, including trailing bytes. |
| Canonical output bytes | 1,048,576 | Entire encoded item; fail before returning a partial accepted result. |
| One byte/text string | 65,536 content bytes | UTF-8 text counts encoded bytes, not scalar count or host code units. |
| One array | 1,024 elements | Direct children only. |
| One map | 1,024 entries | Key/value pair counts as one entry. |
| Total items | 4,096 | Every scalar/container/tag plus every map key and value counts once. |
| Structural nesting | 32 open arrays/maps/tags | Root scalar has depth 0; entering a container or attempted tag increments depth. |
| Integer magnitude | Direct CBOR range only | `[-2^64,2^64-1]`; wider values are unsupported, not resource failures. |
| Tag depth | 0 accepted | Raw parser still bounds attempted tag nesting by the 32 structural nesting limit before reporting forbidden tag. |
| Extension count | 0 accepted | Producer attempts use extension-specific semantic errors. |
| Diagnostic rendering | 4,096 UTF-8 bytes | Over-limit diagnostics return a bounded summary and `resource.diagnostic_bytes`; validation outcome remains separately available. |
| Digest frame bytes | 1,049,255 | Fixed 15-byte magic, six four-byte length prefixes, five identifiers of at most 128 bytes, and payload of at most 1,048,576 bytes. |

The logical counters, not a wall-clock duration or host object size, determine
profile acceptance. Each implementation must additionally be tested in a
declared environment with a 5-second per-fixture timeout and a 128 MiB process
memory ceiling. Those operational numbers are security/conformance evidence,
not cross-platform semantic equivalence. A timeout, allocation failure, stack
overflow, exception, or panic must fail closed and must never yield
`accepted`.

Headers that declare a string or collection above a limit may return the
resource code immediately even if the supplied body is truncated. This avoids
requiring attacker-controlled allocation merely to discover a later syntax
fault.

## CDDL boundary

Candidate schema files use the published RFC 8610 grammar as updated by RFC
9682, in standalone, versioned files. They intentionally remain inside the
independently tested common subset where newer syntax is unnecessary. The
initial portable subset is:

- named type and group rules;
- integer and text/byte literals;
- `uint`, `nint`, `int`, `bstr`, `tstr`, `bool`, and `nil`;
- arrays, closed maps, groups, choices, occurrences, integer ranges, and the
  RFC 8610 `.size` control where independently supported; and
- comments and diagnostic labels that do not affect matching.

Excluded from the initial candidate are:

- floats, tags, `any`, open wildcard map entries, and embedded-CBOR controls,
  because they exceed the accepted value model;
- optional control operators from RFC 9165 and RFC 9741, and every socket or
  other extension whose exact published RFC and tool support is not named by
  the schema;
- CDDL module/import Internet-Draft syntax; and
- tool-specific directives or code generation annotations.

Schemas are standalone or are concatenated by a deterministic, reviewed build
step; draft imports are not silently emulated as standards semantics.

CDDL runs only after raw validity and deterministic-profile validation. CDDL
matching cannot establish canonical bytes, preferred heads, map order,
duplicate absence lost by a parser, Unicode normalization, semantic numeric
normal forms, digest correctness, provenance, inference, or kernel checking.
The selected CDDL tool and exact rule are evidence fields, not semantic
authority.

## Data-free content-digest framing

This section defines a generic framing candidate for data-free structured
objects only. It assigns no table/data object, lowering, or data-digest
semantics.

Define `LP(x)` as the four-byte unsigned big-endian length of byte string `x`,
followed by `x`. Construct the exact byte string:

```text
ASCII("StatQED-Digest") || 00
|| LP(purpose_id)
|| LP(algorithm_id)
|| LP(profile_id)
|| LP(object_class_schema_id)
|| LP(framing_id)
|| LP(payload)
```

The magic is the exact 15-byte sequence
`53 74 61 74 51 45 44 2d 44 69 67 65 73 74 00`. There are exactly six
length-prefixed components, in the order shown; there is no count, terminator,
padding, or trailing field. The framing is an injective byte construction and
does not recursively depend on CBOR decoding.

`payload` is the exact nonempty canonical byte string of one value already
accepted under the named profile and object-class/schema. The five identifier
components are 1 to 128 ASCII bytes and match
`[a-z0-9][a-z0-9._:-]{0,127}` exactly; there is no trimming or case folding.
`algorithm_id` is exactly `sha-256`, `profile_id` is exactly
`statqed.cbor-core.v1`, and `framing_id` is exactly
`statqed.digest-lp.v1`; aliases are not accepted. `purpose_id` and
`object_class_schema_id` come from their owning registries. This candidate
allocates no production purpose or object-class/schema identifiers; vectors
use only names beginning `test.`.

The digest is the 32-byte SHA-256 result over the complete framed byte string.
The stored digest must be exactly 32 bytes. With five maximum-size identifiers
and a maximum-size payload, the frame is at most 1,049,255 bytes: 15 magic
bytes, 24 length bytes, 640 identifier bytes, and 1,048,576 payload bytes.

Verification parses exactly the fixed magic and six components and consumes
the complete frame. It is called with externally expected purpose, algorithm,
profile, object-class/schema, and framing identifiers. It rejects a supplied component
mismatch before digest comparison, then revalidates the payload under the
named profile/object-class/schema, reconstructs the frame, and compares all 32
digest bytes. Unsupported algorithm, profile, framing, or schema values fail
without fallback. A component whose length exceeds `u32` is unrepresentable;
the tighter limits above fail first. Truncated length prefixes/components,
prefix digests, concatenated digests, empty identifiers, empty payload fields,
or concatenated payload items fail explicitly.

Required framing mutations include:

- substitute a different purpose while retaining payload and recorded digest;
- substitute algorithm, profile, object-class/schema, or framing identifier;
- use an unsupported algorithm and attempt fallback to SHA-256;
- alter the magic; delete, reorder, duplicate, or append a component;
- mutate a component length to be short, long, zero, or inconsistent with the
  available bytes;
- truncate or extend the digest;
- split or concatenate two payloads inside the byte string;
- provide empty purpose, algorithm, profile, object-class/schema, framing, or
  payload components; and
- replay a valid frame under a caller-requested different purpose.

The fixed magic and explicit lengths remove raw-concatenation ambiguity; they
do not prove collision freedom, truthful provenance, or semantic equality outside the exact locked
profile/schema/purpose assumptions.

## Acceptance, rejection, and normalization matrix

| Case | Outcome |
|---|---|
| Preferred direct integer, definite string/container, sorted unique map, allowed scalar/simple | Accept after shape and semantic checks. |
| Reversed producer insertion order | Encoder emits the same sorted bytes; insertion order is not semantic. |
| Raw map in length-first rather than core order | Reject `profile.map_order`; do not reorder and accept. |
| Exact duplicate or typed-equivalent differently encoded key | Reject `validity.map_duplicate` before native-map collapse. |
| Indefinite string/array/map | Reject `profile.indefinite`; do not concatenate and accept. |
| Non-preferred integer or length head | Reject `profile.non_preferred_head`; do not re-encode and accept. |
| Invalid UTF-8 | Reject `validity.invalid_utf8`. |
| Composed/decomposed valid text | Accept both as distinct values; perform no normalization. |
| CBOR tag, including bignum/rational/decimal tags | Reject `profile.tag_forbidden`. |
| Float, signed zero, infinity, or NaN | Reject `profile.float_forbidden`. |
| `undefined` or other simple value | Reject `profile.simple_forbidden`. |
| Unsupported semantic class from a producer | Reject its stable `semantic.*` code; no fallback bytes. |
| Unknown critical extension | Reject `semantic.extension_critical_unknown`. |
| Unknown noncritical extension | Reject `semantic.extension_noncritical_unsupported`; do not ignore. |
| Duplicate extension identifiers | Reject `semantic.extension_duplicate` before unknown-extension disposition. |
| Valid profile bytes with wrong schema/version | Reject `expected.schema_id` or `expected.schema_version`. |
| Over-limit input | Reject the applicable `resource.*` code without partial success. |
| Digest/frame mutation | Reject the specific digest/frame code; never fall back or compare a prefix. |

## Examples and nonexamples

Positive byte fixtures should include at least:

```text
00                         # Integer(0)
1818                       # Integer(24)
3818                       # Integer(-25)
4200ff                     # ByteString(00 ff)
62c3a9                     # U+00E9
6365cc81                   # U+0065 U+0301
82f4f6                     # [false, null]
a21864f620f6               # {-1: null, 100: null}, core order
a21818f660f6               # {24: null, "": null}, core order
```

Negative or non-profile fixtures should include at least:

```text
1800                       # non-preferred zero
9f00ff                     # indefinite array
61ff                       # invalid UTF-8
a200f400f5                 # duplicate Integer(0) key
a220f61864f6               # length-first order, not core
a260f61818f6               # {"": null, 24: null}, length-first, not core
c249010000000000000000     # tag 2 bignum, forbidden
c349010000000000000000     # tag 3 negative bignum, forbidden
c200                       # tag 2 with wrong registered content; still forbidden
c4820001                   # tag 4 decimal [0, 1], forbidden
d81e820102                 # tag 30 rational [1, 2], forbidden
f90000                     # binary16 +0, forbidden
f98000                     # binary16 -0, forbidden
f97e00                     # binary16 NaN, forbidden
f7                         # undefined, forbidden
ff                         # unexpected break; not well-formed as a root item
```

Nonexamples:

- accepting bytes after decode/re-encode because the re-encoding is canonical;
- comparing only maps already collapsed by a generic decoder;
- using host-language key order, UTF-16 order, locale collation, or JSON order;
- treating two libraries that share a canonicalizer lineage as independent;
- generating expected bytes from the Rust prototype and feeding them to the
  second implementation as truth;
- calling CDDL match, digest match, replay, or structural validation
  statistical or kernel verification; and
- changing limits, accepted atom classes, Unicode behavior, map ordering, or
  framing while retaining `statqed.cbor-core.v1`.

## Evidence required before RFC-0001 could be Accepted

1. Two genuinely independent implementations agree on semantic values, exact
   bytes, and stable classes for every positive, boundary, malformed,
   non-profile, unsupported, and resource fixture.
2. At least one path visibly retains raw map entries and catches duplicates
   formed by different serializations before host-map collapse.
3. A deliberate encoder order mutation and decoder permissiveness mutation are
   both detected by the harness.
4. Every integer/length-width boundary, core-vs-length-first divergence,
   Unicode case, tag/float/simple rejection, extension semantic rejection,
   and resource boundary has a retained fixture.
5. Digest framing survives purpose/algorithm/profile/object-class/schema/framing
   mutations, downgrade/fallback attempts, truncation, replay, and ambiguity
   tests.
6. The selected CDDL subset validates only structural shape and is reproduced
   without draft modules/imports or tool-specific silent extensions.
7. Source, semantic, interoperability, security, cryptographic, formal,
   conformance, CI/release, and integration reviewers approve the exact
   content-addressed subject.

## Unresolved decisions, blockers, and review questions

These do not license implementation-specific choices. Any unresolved blocker
must leave RFC-0001 Draft.

1. **Core ordering evidence:** independent implementations must demonstrate the
   `{24,""}` core/length-first discriminating fixture. Length-first remains a
   rejected RFC 7049-compatibility alternative, not an implementation option.
2. **Map-key sufficiency:** confirm that `Integer | TextString` covers the
   data-free schemas. The broader scalar-key alternative (byte strings,
   booleans, and null in key position) is rejected absent a concrete need.
3. **Resource numbers:** both implementations must meet every logical boundary
   and the declared operational harness ceiling. Any changed number creates a
   new review subject and must be settled before acceptance.
4. **Unicode preservation:** source/security review must approve no
   normalization and confirm that schema-owned identifier restrictions are
   sufficient. The profile must not add a Unicode-version dependency by
   accident.
5. **All-tags-forbidden rule:** source and schema reviewers must confirm that
   the data-free foundation object needs no tag. If one is needed, its exact
   registry source, content validity, semantic equality, preferred form, and
   resource behavior reopen this candidate.
6. **CDDL portability:** the actual candidate tools must agree on the selected
   RFC 8610/RFC 9682 common subset, especially `.size`, closed maps, and choice
   matching. Any published CDDL extension must be named and tested before use.
7. **Digest review:** cryptographic review must confirm SHA-256, exact
   `sha-256` identifier, output length, frame construction, caller-supplied
   expected-domain checks, and the purpose/schema identifier grammar against
   the dated source audit.
8. **Result-code alignment:** conformance and implementation reviewers must
   adopt one stable machine-readable spelling and precedence. Library-specific
   exceptions/prose cannot become the contract.
9. **Evidence still absent:** this note is architecture, not validation. Until
   independent vectors, malformed/resource evidence, source audit, and all
   required reviews exist, RFC-0001 and ADR-0004 must remain Draft/Proposed.

## Primary source anchors

- [RFC 8949 sections 4.1 and 4.2](https://www.rfc-editor.org/rfc/rfc8949.html#section-4)
  for preferred serialization and the two deterministic map-order choices;
  sections 5.3 and 5.6 for validity, expectedness, duplicate keys, map
  equality, and parser obligations.
- [RFC 8610](https://www.rfc-editor.org/rfc/rfc8610.html) and its published
  grammar update [RFC 9682](https://www.rfc-editor.org/rfc/rfc9682.html) for the
  CDDL structural matching boundary.
- [IANA CBOR Tags registry](https://www.iana.org/assignments/cbor-tags/cbor-tags.xhtml)
  to make the all-tags-forbidden decision auditable rather than treating tags
  2, 3, 4, or 30 as unregistered accidents.
- [NIST FIPS 180-4](https://csrc.nist.gov/pubs/fips/180-4/upd1/final) for the
  candidate SHA-256 algorithm, subject to the dated SQ-0005 cryptographic
  source audit and review.

The current draft source-lineage records are
`source-audits/encoding/SA-SQ0005-CBOR.yaml` and
`source-audits/encoding/SA-SQ0005-CDDL.yaml`. This candidate is reconciled to
their recommended core-order, closed-tag, strict-rejection, and
published-CDDL boundaries; the audits, this candidate, and actual prototype
evidence still require independent review before they can inform RFC text.
