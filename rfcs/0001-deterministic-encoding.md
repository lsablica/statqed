# RFC-0001: Deterministic Normative Encoding

- Status: Accepted
- Author: foundation serialization team
- Reviewers: source, semantic, interoperability, formal, implementation, security, cryptographic, CI, and integration reviewers
- Created: 2026-08-02
- Last revised: 2026-08-09
- Task: SQ-0005
- Profile identifier: `statqed.cbor-core.v1`

## Decision scope

<!-- SQ-0005-NORMATIVE-SCOPE-BEGIN -->
StatQED normative structural objects use the versioned
`statqed.cbor-core.v1` application profile of RFC 8949 CBOR. The profile uses
preferred definite-length serialization and RFC 8949 Section 4.2.1 core
deterministic map ordering. It accepts only direct-range integers, byte
strings, exact Unicode text, arrays, raw-entry-validated maps with integer or
text keys, booleans, and null. It rejects tags, floating point, indefinite and
non-preferred encodings, duplicates, unknown extensions, and every unsupported
semantic atom. Published RFC 8610 CDDL syntax may describe structural subsets
but does not define deterministic bytes or semantic validity. Generic
data-free digests use the separately identified six-component
`statqed.digest-lp.v1` SHA-256 frame. This decision does not define archives,
artifacts, logical tables, logical-data identity, or RFC-0006.
<!-- SQ-0005-NORMATIVE-SCOPE-END -->

This RFC defines a generic structural encoding profile, strict decoder result
classes, generic data-free digest framing, resource ceilings, and conformance
obligations. Object schemas still decide which profile value is meaningful in
their own context.

It does not define the `.statqed` archive or artifact envelope (SQ-0010),
theorem identity, proof locks, certificate semantics, source fidelity,
statistical validity, real-data tables, Arrow lowering, row identity,
missingness, categorical semantics, privacy, or the canonical logical-data
digest. RFC-0006 remains Draft and owned by SQ-0027.

## Normative and supporting sources

The profile relies on RFC 8949 / STD 94 for CBOR well-formedness, validity,
preferred serialization, and core deterministic ordering. Published CDDL
syntax is RFC 8610 as formally updated by RFC 9682; RFCs 9165 and 9741 define
optional published extensions that this minimum profile does not require.
UTF-8 validity is the RFC 3629 scalar-value subset. SHA-256 is the FIPS 180-4
algorithm used by the generic frame. Purpose separation follows the
explicit-domain principle in RFC 9380 Section 10.7; RFC 9380's hash-to-curve
construction is not adopted.

The exact source versions, retrieval dates, errata disposition, IANA CBOR Tag
registry snapshot, draft/stable distinctions, licenses, and unresolved source
interpretations are content-addressed under `source-audits/encoding/`. CDDL
module/import draft revision `-06` is Work in Progress and is not a normative
dependency.

## Semantic value model

The semantic model precedes every host-language type and byte rule.

| Class | v1 disposition and equality |
|---|---|
| `Integer(n)` | Accepted exactly for `-2^64 <= n <= 2^64-1`; equality by mathematical integer. |
| `ByteString(b)` | Accepted within limits; equality byte-for-byte. |
| `TextString(s)` | Accepted Unicode scalar sequence within limits; equality by exact scalar sequence with no normalization. |
| `Array(v...)` | Accepted recursively; equality is ordered elementwise equality. |
| `Map(entries...)` | Accepted after raw-entry validation; equality ignores insertion order only after typed key uniqueness is established. |
| `Boolean(b)` | Accepted; `false` and `true` are distinct. |
| `Null` | Accepted as one singleton. |
| `Bignum`, `Rational`, `Decimal`, `IEEEBits`, `Interval`, `Extension`, `ExtensionSequence` | Explicitly unsupported or invalid as classified below; never coerced into an accepted atom. |

Library-native dictionaries, numeric towers, Unicode normalization, and JSON
numbers do not define this model. A decoder must retain ordered raw map entries
until duplicate and ordering validation are complete.

## Deterministic byte profile

### Accepted major types and preferred heads

Only CBOR major types 0 through 5 and simple values `false`, `true`, and
`null` are accepted. Every integer, string length, array length, and map length
uses the shortest RFC 8949 argument head. Strings, arrays, and maps are always
definite length. Non-preferred but value-equivalent input is rejected as
`profile.non_preferred_head`; it is not silently repaired.

For nonnegative `Integer(n)`, major type 0 carries `n`. For negative
`Integer(n)`, major type 1 carries `-1-n`. The largest eight-byte argument
therefore fixes the accepted interval at `[-2^64, 2^64-1]`. Values outside it
are `semantic.integer_range` when presented as an `Integer`; tag-based bignum
encoding has no v1 fallback.

Byte strings use major type 2. Text strings use major type 3 containing
shortest-form valid UTF-8. Arrays use major type 4. Maps use major type 5.
Booleans use `f4` and `f5`; null uses `f6`. `undefined`, every other simple
value, break, all tags, and all floating encodings are forbidden.

### Map keys, duplicates, and ordering

Map keys are only `Integer` or `TextString`. The decoder must:

1. parse the complete map into an ordered raw entry sequence;
2. validate every key as an allowed scalar;
3. detect duplicate typed semantic keys before any native-map collapse;
4. compute each key's deterministic encoding;
5. require strict unsigned bytewise lexicographic increase of those complete
   encodings; and
6. only then construct an implementation map, if desired.

This is RFC 8949 Section 4.2.1 core order, not Section 4.2.3 length-first
order. Exact and non-preferred equivalent encodings of the same typed key are
duplicates. Exact Unicode scalar equality controls text-key duplicates;
canonically equivalent but scalar-distinct strings remain distinct. Integer
and text keys are distinct even when their diagnostic spelling resembles.

The discriminating example `{Integer(-1): Null, Integer(100): Null}` encodes
as `a21864f620f6`. The length-first `a220f61864f6` is rejected as
`profile.map_order`.

## Numeric policy

- Tags 2 and 3 and semantic `Bignum` values are unsupported. Bignum leading
  zero, sign, and negative-boundary ambiguities therefore cannot enter v1.
- Rational values are unsupported. A zero or negative denominator, a
  non-reduced pair, or a sign outside the numerator is invalid before the
  unsupported result.
- Decimal fractions are unsupported. Zero must have exponent zero and a
  nonzero coefficient divisible by ten is non-normal before the unsupported
  result.
- Every IEEE binary16/32/64 bit pattern is unsupported, including finite
  numbers, positive and negative zero, infinities, quiet/signaling NaNs, NaN
  signs, and payloads. No cross-representation numeric equality exists.
- Intervals are unsupported and their diagnostic research shape is deliberately
  narrow: both endpoints are accepted-range integers and closure is exactly
  `closed`, `open`, `left_closed`, or `right_closed`, with the latter two
  naming the included endpoint. Bounds must be strictly increasing, except a
  closed equal-bound singleton. Reversed bounds, equal-bound non-closed empty
  intervals, unknown closures, and rational, decimal, IEEE/NaN, or mixed
  endpoints are `semantic.interval_invalid` before the unsupported result.

These exclusions are decisions, not missing implementation branches. Adding
any class requires a new profile identifier, semantic review, independent
vectors, and migration record.

## Unicode policy

Text is an exact sequence of Unicode scalar values encoded as valid shortest
UTF-8. No NFC, NFD, NFKC, NFKD, case folding, locale processing, or versioned
Unicode normalization table is applied. Consequently U+00E9 and U+0065
U+0301 are both accepted and remain unequal. Normalization collisions do not
occur because there is no normalization step.

Controls, noncharacters, and unassigned scalar values are structurally
preserved. An object schema may reject them for its own identifiers or text,
but the schema must not claim that this profile normalized them. Surrogates,
overlong UTF-8, invalid continuation bytes, and values beyond U+10FFFF are
invalid UTF-8.

## Tags and extensions

The v1 tag allowlist is empty. A syntactically valid tagged item is fully
parsed with ordinary child validity and resource checks, then rejected as
`profile.tag_forbidden`. A malformed child is not hidden by the tag result.

The v1 extension allowlist is also empty. Typed extension sequences scan all
identifiers for duplicates before classifying criticality. Duplicate IDs are
`semantic.extension_duplicate`; otherwise any critical extension is
`semantic.extension_critical_unknown`, and an all-noncritical sequence is
`semantic.extension_noncritical_unsupported`. Unknown noncritical extensions
are not discarded. Nested tags do not provide an extension escape hatch.

## Decoder taxonomy and precedence

Successful decoding means only that one byte string is a strict instance of
this generic profile under the supplied profile expectation. Rejection uses
stable classes:

| Class | Meaning and examples |
|---|---|
| `well_formedness` | Not well-formed CBOR: truncation, reserved additional information, unexpected break, or bad indefinite chunk syntax. |
| `validity` | Well-formed but invalid CBOR: invalid UTF-8 or duplicate typed map keys. |
| `expectedness` | Valid CBOR violates caller/application expectations: trailing input, a raw map-key type outside the profile, wrong expected top-level kind, or profile identifier. |
| `deterministic_profile` | Otherwise valid item violates v1: non-preferred head, indefinite form, wrong map order, tag, float, or forbidden simple value. |
| `cddl_shape` | A separately requested published-syntax CDDL structural rule did not match (`shape.cddl_mismatch`). It says nothing about bytes, duplicates, semantic normalization, or a different object schema. |
| `semantic_validity` | A producer supplied an invalid or unsupported generic semantic atom. A producer-side forbidden map key is `semantic.map_key_type`; it is not the raw decoder's `expected.map_key_type`. |
| `schema_mismatch` | A separate object-schema-owning validator rejected the decoded profile value (`schema.mismatch`). This profile, CDDL prototype, and digest frame do not manufacture this result. |
| `resource` | An explicit byte, depth, item, collection, or diagnostic ceiling was exceeded. |
| `digest_verification` | The generic frame, expected identifier, algorithm, profile, payload, or digest comparison failed. |
| `operational` | Harness timeout, memory ceiling, crash, or implementation exception. It is never successful validation. |

Resource ceilings may fail as soon as safe completion is impossible.
Otherwise, when an interface requests every applicable phase, precedence is
`well_formedness`, `validity`, `expectedness`, `deterministic_profile`,
`cddl_shape`, producer `semantic_validity`, separate `schema_mismatch`, and
`digest_verification`, followed by acceptance. Within a complete input,
duplicate validation precedes order and non-preferred map-key results. A
decode-and-reencode match is not proof that the original bytes conformed.

CDDL mismatch, schema mismatch, digest mismatch, provenance, and statistical
validity remain distinct results. They must never be collapsed into a generic
“verified” response.

## Resource limits

| Resource | v1 limit | Counting rule |
|---|---:|---|
| Total CBOR input | 1,048,576 bytes | Entire byte slice presented to the single-item decoder, including trailing bytes. |
| Total canonical output | 1,048,576 bytes | Entire encoded item; a partial output is never accepted. |
| One byte or text string | 65,536 encoded content bytes | Text counts UTF-8 bytes, not scalar values or host code units. |
| Array items | 1,024 | Direct children of one array. |
| Map entries | 1,024 | Each key/value pair is one entry. |
| Total parsed/encoded items | 4,096 | Every scalar, container, attempted tag, map key, and map value counts once; an indefinite string wrapper and each definite chunk count once. |
| Open array/map/tag levels | 32 | A root scalar has depth 0; entering an array, map, or attempted tag increments depth. |
| Accepted tags | 0 | The raw parser still applies the depth and item counters before the closed-tag result. |
| Accepted extensions | 0 | Typed producer attempts receive extension-specific semantic failures. |
| Rendered diagnostic | 4,096 UTF-8 bytes | Over-limit prose is replaced by a bounded summary without upgrading validation. |
| Generic digest-frame allocation cap | 1,049,255 bytes | Conservative allocation bound over fixed magic, six length prefixes, maximal identifiers, and payload. |
| Largest attainable valid generic frame | 1,048,918 bytes | Fixed identifiers, two maximal caller identifiers, and a 1,048,576-byte payload. |

The conformance harness additionally imposes a five-second process timeout
and 128 MiB address-space ceiling per executed probe on supported Linux hosts.
These operational limits are evidence controls rather than replacements for
the profile's logical bounds. Diagnostic typed-JSON transports may have a
separate documented bound and have no normative encoding authority.

## Generic data-free digest framing

The framing identifier is `statqed.digest-lp.v1`, the algorithm identifier is
`sha-256`, and the profile identifier is `statqed.cbor-core.v1`. The frame is:

```text
ASCII "StatQED-Digest" || 0x00 ||
u32be(len(purpose_id)) || purpose_id ||
u32be(len(algorithm_id)) || algorithm_id ||
u32be(len(profile_id)) || profile_id ||
u32be(len(object_class_schema_id)) || object_class_schema_id ||
u32be(len(framing_id)) || framing_id ||
u32be(len(payload)) || payload
```

There are exactly six length-prefixed components after the magic. Identifiers
are nonempty ASCII matching `[a-z0-9][a-z0-9._:-]{0,127}`. Payload is nonempty,
strictly accepted `statqed.cbor-core.v1` bytes within the input limit. The
digest is SHA-256 over the entire frame. Verification binds the caller's exact
purpose, algorithm, profile, object-class/schema, and framing identifiers and
rejects unsupported fallback, downgrade, truncation, trailing data, reordered
components, or length ambiguity before reporting a digest match.

A missing length prefix or component body is `digest.component_length`. Once
all bytes declared for an identifier are present, an empty, over-128-byte,
non-ASCII, grammar-invalid, fixed-value, or caller-expected mismatch receives
that field's specific `digest.*` code rather than a truncation code.

The frame binds the schema identifier but does not resolve it or prove that
the payload conforms to that schema. Schema validation is a separate caller
prerequisite. No purpose or object-class identifier for real data or logical
tables is assigned here.

Digest equality is conditional on the algorithm and framing assumptions. It
does not prove collision absence, provenance truth, source fidelity, semantic
interpretation, logical-data identity, privacy, or statistical validity and
does not resolve RFC-0006.

## CDDL boundary

Candidate structural CDDL uses only published RFC 8610 syntax as updated by
published RFCs. The `foundation_structural` prototype schema is a data-free
shape example, not an artifact, IR, theorem-registry, or logical-table schema.

CDDL acceptance does not establish preferred heads, core map order, duplicate
semantics, Unicode preservation, semantic normalization, digest identity,
provenance, or statistical validity. Draft module/import syntax may be studied
only in separately pinned Experimental research and is not required here.

## Independent implementation and conformance evidence

Semantic fixtures were committed before accepted golden bytes. The corpus has
273 stable cases (70 accepted and 203 rejected) spanning accepted, boundary,
one-over-limit, malformed,
invalid, non-profile, unsupported, ambiguous, divergent, and resource cases.
The Rust/library-backed prototype and direct standard-library Python oracle
have independent source roots, parser/canonicalizer lineages, dependency
locks, and no output-consumption edge between them.

Accepted golden bytes are retained only where both implementations agree with
the precommitted semantic expectation. The current candidate produces 69 such
binary vectors. The harness also detects 20 deliberate divergences, including
a length-first encoder, a duplicate-collapsing decoder, silent
decode-and-reencode normalization, status/result mutations, and framing
mutations. Historical implementation and fixture failures are retained rather
than overwritten.

Agreement is evidence, not authority. Neither program nor the Rust library
defines the profile, and shared misunderstanding remains possible.

## Security and trust boundary

The profile addresses duplicate erasure, parser differential behavior,
Unicode confusion, numeric/tag type confusion, non-preferred normalization,
unknown critical behavior, length ambiguity, resource exhaustion, diagnostic
amplification, cross-domain replay, fallback, downgrade, and truncation.
Project runtimes, prototype libraries, the CDDL matcher, SHA-256
implementation, CI, and agents are untrusted evidence producers outside the
verification-mode trusted computing base.

Structural acceptance, canonical-byte equality, schema validity, digest
verification, provenance, proof validity, identification, inference,
numerical correctness, and interpretation are separate results. This RFC
licenses no claim stronger than its generic structural and framing rules.

## Rejected alternatives

- RFC 8949 Section 4.2.3 length-first map ordering: rejected for v1 in favor
  of core ordering, with discriminating fixtures retained.
- Silent normalization of non-profile input: rejected because it erases the
  property being checked and can hide duplicate/order ambiguity.
- Library “canonical” modes as the definition: rejected because library
  defaults and algorithms differ.
- Canonical JSON: retained only as diagnostic transport; it does not preserve
  all type distinctions without another profile.
- Custom binary format: rejected because the selected standard subset meets
  the measured foundation needs with less parser/governance burden.
- Unicode normalization and numeric coercion: rejected because they erase
  distinctions not licensed by generic source semantics.
- Any tag or extension allowlist in v1: rejected until a concrete object-class
  need receives its own semantic and interoperability review.
- CDDL draft module/import syntax as normative: rejected while it remains Work
  in Progress.

## Compatibility, update, rollback, and migration

The profile identifier is part of every framing decision. A change to an
accepted value class, equality relation, byte rule, error precedence, resource
limit, tag/extension rule, or digest frame requires a new profile/framing
identifier or a separately reviewed demonstration that the accepted language
and bytes are unchanged. Golden vectors cannot be replaced solely because one
implementation changed.

An update must refresh the primary-source audit, semantic fixtures,
independent implementations and locks, dependency/license/advisory evidence,
full differential and mutation corpus, RFC/ADR hashes, workflow, and all
distinct reviews. Rollback restores the complete previously reviewed profile,
schema, implementations, locks, corpus, evidence manifest, and identifiers;
partial rollback fails closed as evidence drift.

## Explicit nonclaims

RFC-0001 does not establish source theorem fidelity, external assumptions,
Lean theorem identity, artifact-byte binding, artifact-envelope validity,
certificate-checker soundness, theorem-registry authority, provenance truth,
logical-data identity, collision absence, privacy, identification,
inferential validity, numerical certification, interpretation, or general
verification of `.statqed` artifacts.

## Validation disposition

Every original validation-plan item is represented by a positive, negative,
boundary, malformed, resource, differential, deliberate-divergence, framing,
or retained-failure record. Acceptance remains gated on the final
content-addressed source, semantic, interoperability, formal, implementation,
security, cryptographic, CI, and integration reviews and a green hosted
serialization-prototype workflow.

The acceptance candidate is bound to these exact evidence subjects. The RFC's
own hash and the matching ADR hash are bound by the independent review record
rather than embedded recursively in this document.

| Subject | SHA-256 |
|---|---|
| Semantic value model | `a94588e54fdc3e2aa08e73f5f6e76bb71128940bb245305b2dec9dffa2ffcfb2` |
| Profile candidate | `6cbf0f686a1f35b5c6fac8411ef5abc708c9c4410b5fdb2ee510c513df067d2f` |
| Primary-source audit manifest | `b3f70746a36c350590f2f77ffebb0e550773337d79db4103317426be94ac0a40` |
| Semantic fixture tree | `90fc4b5a1346f0693b84a0fa9a6a1e1fa4ac535aff2b83d6177313c6779fa3c8` |
| Generated result manifest | `e69e863053fad44faf2511cedbd53a13725e309cbdb0551621e217c2095dd6cd` |
| Differential results | `4e48d962644cec0f83b868ba13bcc62f3bc8cee4dca748fed10e3ad911195274` |
| Deliberate-mutation results | `1b6c448a29ce76b83c5e85673731382dc24bba8a1902a7686988626015d22da6` |
| Binary golden manifest | `8db0e43760421ea694e0e2d7095ade93a821ce5f3b7c66eaf954d7fe969af7a1` |
| Independent-lineage declaration | `7a7e48658e81e478c3858f265d24eb0c1402fa6169e7c03eb74363effb8208a4` |
| Python executable/lock subjects | `cc05dbf3d4996f44e204099ad335df843557571ae61aac8044903de5f9e41a9f` |
| Rust executable/lock subjects | `cb3c03907bc7cdf6f495be7d98d795347b3b51c1415637a6b1e8d71f558027ea` |
| Rust `Cargo.lock` | `2e9c4f95aa0aa54ab2338e980d388f9f0223be8964d94f82d82f086f2dadb180` |
| Published-syntax CDDL prototype | `05ee85b0d028af588ed9e95e83fdf017259988f05709de85f033cb0ab5badda0` |
| Digest-framing semantic corpus | `36895de279202434a1511bb1bf552c199e55d57ee8a57a7d724772a737824d0b` |
| Permanent evidence verifier | `864568ef80e2c1f0517999cf45130f744c6599eab34040932f1fa0258e0c7d0e` |
| Serialization-prototype workflow | `3cb67d26721258413ff80150df453dca77f76ea77374fe6a5a92bd7494cd8536` |
| Unchanged Draft RFC-0006 baseline | `e834f805cc38fca2185433c72df4ac7db856c0ae20037fedcb57329a740b3429` |

## Decision

The independently reviewed evidence supports, and the atomic SQ-0005
transition accepts, this deterministic CBOR profile and generic data-free
frame. This document is Accepted. Acceptance binds only the marked normative
scope and its content-addressed evidence; it grants no production authority
to either prototype and resolves none of RFC-0006's logical-data decisions.
