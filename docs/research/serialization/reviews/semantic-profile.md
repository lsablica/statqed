# SQ-0005 semantic-profile and numeric-model review

Status: **Experimental review record**

Disposition: **APPROVE**

Review date: 2026-08-09

Reviewer: `/root/sq0002_statistical_trust_review`, acting as the independent
semantic-profile, numeric-model, and statistical trust-boundary reviewer

## Decision

The exact subject below is approved for the SQ-0005 semantic-profile gate.
The language-neutral model defines the accepted structural atoms before bytes,
keeps unsupported and invalid numeric classes typed, preserves exact Unicode
and raw map entries, and gives every accepted semantic value one selected v1
encoding. The Draft RFC, Proposed ADR, and Draft implementation-facing spec
agree on the same bounded, data-free scope.

The earlier interval, result-taxonomy, resource-counting, corpus-count,
source-attribution, and raw digest-identifier precedence defects were corrected
before this review. In the final subject, producer semantic validity no longer
absorbs object-schema invariants; `schema_mismatch` belongs only to a separately
identified schema validator. RFC 9682 is correctly identified as the formal
update to RFC 8610, while RFCs 9165 and 9741 are optional published extensions
that the minimum profile does not require. A missing digest length prefix or
declared component body is now distinct from a fully present identifier that
violates its field-specific grammar or expectation. These corrections do not
change any accepted atom, equality relation, canonical byte, resource bound,
or statistical boundary.

This reviewer did not author or edit the candidate, semantic model, profile,
fixtures, RFC, ADR, canonicalization spec, source audit, implementations, or
generated evidence. This record reviews definitions, classifications,
fixtures, serialization consequences, and trust claims. It does not review
implementation correctness or by itself accept RFC-0001 or ADR-0004.

## Exact subject

The reviewed candidate and implementation/evidence subject is commit
`410465d773fc011ee01e38e6e76a79a60efe8837`. Later commits reachable from the
current review-time HEAD add independent review records only; the candidate
paths and hashes below are unchanged from `410465d`.

| Subject | SHA-256 or identity |
|---|---|
| Candidate implementation/evidence commit | `410465d773fc011ee01e38e6e76a79a60efe8837` |
| Fixture frozen commit recorded by generated evidence | `b4d92a39e30fa5736c58bc71c57790ec215fbad7` |
| `docs/research/serialization/semantic-value-model.md` | `a94588e54fdc3e2aa08e73f5f6e76bb71128940bb245305b2dec9dffa2ffcfb2` |
| `docs/research/serialization/profile-candidate.md` | `6cbf0f686a1f35b5c6fac8411ef5abc708c9c4410b5fdb2ee510c513df067d2f` |
| `rfcs/0001-deterministic-encoding.md` | `d4258501486affdaf99ec95322bae1e1212806c896e33360a17c137fd2f51106` |
| `docs/adr/0004-deterministic-cbor-cddl.md` | `004b41b65dc8450de6f0bd8431f7de2e1f885e95dfd985f50981e1c1c5c9e49d` |
| RFC/ADR marked normative-scope block | `737847efcdb917f8c3db8c05c314c85f62775fa8ca80638a56de69cadb0fc060` |
| `docs/spec/canonicalization.md` | `e0bc0628fd0ac05a43f06ac478c029e83a5daeb4fe88f2b00579d4f892cce61a` |
| Semantic fixture content tree | `90fc4b5a1346f0693b84a0fa9a6a1e1fa4ac535aff2b83d6177313c6779fa3c8` |
| Generated result manifest | `e69e863053fad44faf2511cedbd53a13725e309cbdb0551621e217c2095dd6cd` |
| Differential results | `4e48d962644cec0f83b868ba13bcc62f3bc8cee4dca748fed10e3ad911195274` |
| Python executable/lock subject | `cc05dbf3d4996f44e204099ad335df843557571ae61aac8044903de5f9e41a9f` |
| Rust executable/lock subject | `cb3c03907bc7cdf6f495be7d98d795347b3b51c1415637a6b1e8d71f558027ea` |
| Primary-source audit manifest | `b3f70746a36c350590f2f77ffebb0e550773337d79db4103317426be94ac0a40` |
| Unchanged Draft RFC-0006 | `e834f805cc38fca2185433c72df4ac7db856c0ae20037fedcb57329a740b3429` |

The fixture-tree digest was independently recomputed over fixture files in
sorted relative-path order as
`path || NUL || exact_file_bytes || NUL`. Its members are:

| Fixture member | SHA-256 |
|---|---|
| `atoms-and-widths.json` | `2ffec8250ace8283959db11a29d2d7c2b55500429065d484394732c59e52dcd9` |
| `catalog.json` | `d5bf3079d9ff8119a2372873a1b116601011e78c30067bc1d05228211659b4d3` |
| `differential-mutants.json` | `313a784148be66fa471c2684be27512fbf5e0f446f7681dd27e8317b36c882e6` |
| `digest-framing.json` | `36895de279202434a1511bb1bf552c199e55d57ee8a57a7d724772a737824d0b` |
| `malformed-and-strictness.json` | `b6af575d7111def454a642fa3052bc626f2aea2a4fee76cf7719677739fcf2af` |
| `maps-and-unicode.json` | `c1053fc27be0e8afb60ef655038daca71b43e93c98a2abe5c0dae56e29efb110` |
| `numeric-tags-extensions.json` | `5c50a8ed96b4e1a032f818b9ecec0ae2e6db9b4e2e746e1ed47bcd8cca739329` |
| `resources.json` | `984a142eb002a38d4f137a98d44c222fe2bf56dd2147808608372cb0f7ad0039` |

The RFC and ADR marked blocks, including their boundary comments, compare
byte-for-byte equal. RFC-0006 is byte-identical to its pre-SQ-0005 baseline at
`8875d8f6fa8e3b45e706ea567d45448927a02efa` and remains Draft under SQ-0027.

## Semantic value and equality audit

The accepted model is intentionally closed and sufficient for the data-free
foundation structure:

- `Integer` is an exact mathematical integer in
  `[-2^64, 2^64-1]`; it is not a host float or Boolean.
- `ByteString` equality is byte equality, and `TextString` equality is exact
  Unicode-scalar-sequence equality.
- `Array` equality is ordered elementwise equality.
- `Map` equality ignores insertion order only after typed key uniqueness has
  been established over the retained raw entry sequence.
- `Boolean` is disjoint from `Integer`; `Null` is one literal with no
  missingness meaning.

Equality is typed. In particular, `Integer(1)`, `Rational(1,1)`,
`Decimal(1,0)`, IEEE binary `1.0`, and `TextString("1")` are not generic-equal
values. Map keys are restricted to `Integer | TextString`, so none of the
unsupported numeric constructors can enter key equivalence or ordering by
coercion.

`Bignum`, `Rational`, `Decimal`, `IEEEBits`, `Interval`, and `Extension` remain
explicit constructors at the producer boundary so they fail with stable,
typed results. They have no v1 bytes and do not reserve future encodings.
This is a complete unsupported boundary, not an implementation omission.

## Numeric and interval audit

The numeric policy is exact and does not rely on decimal text or host binary
floating point:

- A mathematical integer outside the direct range is
  `semantic.integer_range` when supplied as `Integer`; an explicit `Bignum`
  is separately `semantic.unsupported_bignum`. Tags 2 and 3 are forbidden.
- A well-formed `Rational(p,q)` has `q > 0` and a reduced pair. Zero or
  negative denominators and non-reduced pairs are invalid; well-formed
  rationals are unsupported. Tag 30 and array fallbacks acquire no rational
  meaning.
- A well-formed `Decimal(coefficient, exponent)` has canonical zero `(0,0)`
  and no removable power of ten in a nonzero coefficient. Non-normal decimals
  are invalid; normal decimals remain unsupported. Tag 4 and text/array
  fallbacks acquire no decimal meaning.
- `IEEEBits` equality is width-and-bit equality for widths 16, 32, and 64.
  Positive and negative zero remain distinct, as do infinity signs and NaN
  signs/payloads. All semantic IEEE values and all CBOR float encodings are
  rejected; none is silently shortened, normalized, or coerced.
- The research `Interval` shape admits only accepted-range integer endpoints
  and exactly `closed`, `open`, `left_closed`, or `right_closed`. Bounds are
  strict except that equal closed bounds form a singleton. Reversed bounds,
  equal non-closed empty intervals, unknown closure tokens, and
  rational/decimal/IEEE or mixed endpoints are
  `semantic.interval_invalid`; a well-formed integer interval is
  `semantic.unsupported_interval`.

The interval fixtures distinguish every closure token, an unknown inverse-style
token, an empty open interval, a closed singleton, reversed bounds, mixed
endpoints, and rational, decimal, and IEEE/NaN endpoint attempts. The large
decimal-exponent diagnostic case is interval-invalid without licensing
materialization of an enormous host power.

## Map, Unicode, and extension audit

Raw maps remain ordered entry sequences until allowed-key and typed-duplicate
checks finish. Duplicate equality is checked before native-map collapse,
before deterministic order, and before a non-preferred map-key result. Core
ordering compares complete deterministic key encodings using unsigned bytewise
lexicographic order. The discriminating map
`{Integer(-1): Null, Integer(100): Null}` therefore has accepted bytes
`a21864f620f6`; length-first `a220f61864f6` is rejected.

Text uses shortest-form valid UTF-8 and preserves the exact scalar sequence.
No NFC, NFD, NFKC, NFKD, case, locale, or confusable normalization occurs.
U+00E9 and U+0065 U+0301 are accepted, unequal values and unequal keys.
Controls, noncharacters, and unassigned scalar values are preserved at this
generic layer; a later object schema may impose separately identified text or
identifier restrictions. Invalid UTF-8 remains CBOR validity failure and is
never repaired with replacement characters.

The v1 tag and extension allowlists are empty. A tagged child is still parsed
within ordinary validity and resource bounds before `profile.tag_forbidden`.
Producer extension sequences scan the complete sequence for duplicate exact
identifiers first; otherwise any critical extension gives
`semantic.extension_critical_unknown`, while a wholly noncritical sequence
gives `semantic.extension_noncritical_unsupported`. Neither class is ignored,
and sequence order cannot change the result.

## Result taxonomy and resource audit

The final taxonomy keeps the following result owners distinct:

1. resource exhaustion;
2. CBOR well-formedness;
3. CBOR validity, including raw typed duplicate keys;
4. caller/application expectedness, including raw forbidden map-key type;
5. deterministic-profile conformance;
6. separately requested published-syntax CDDL shape;
7. producer semantic validity;
8. separately requested object-schema mismatch;
9. digest verification; and
10. acceptance, with operational failures remaining evidence outcomes.

The raw decoder uses `expected.map_key_type`; a producer uses
`semantic.map_key_type`. `cddl_shape / shape.cddl_mismatch` cannot establish
canonical bytes or semantic validity. `schema_mismatch / schema.mismatch`
belongs only to a separately identified object-schema validator and is not
emitted by the generic profile, CDDL prototype, or digest frame. Its absence
from this data-free profile's executable cases is therefore not a fixture gap;
the future schema-owning task must supply its own positive and negative
schema-invariant vectors.

Logical bounds have exact counting rules: the whole supplied input slice and
whole canonical output are bounded at 1,048,576 bytes; one string at 65,536
content bytes; an array or map at 1,024 direct children or entries; total
items at 4,096; and open structural depth at 32 with root-scalar depth zero.
Every scalar, container, attempted tag, map key/value, indefinite wrapper, and
definite string chunk counts once where applicable. Accepted tags and
extensions are zero. Diagnostic rendering is bounded at 4,096 UTF-8 bytes.
The 1,049,255-byte digest-frame allocation cap is correctly distinguished
from the largest attainable valid frame of 1,048,918 bytes. Five seconds and
128 MiB are operational harness evidence, not cross-platform semantic limits.

Digest framing also has an exact structural-versus-field-error boundary. A
missing or truncated four-byte prefix, or a component body shorter than its
declared length, is `digest.component_length`. Once all declared identifier
bytes are present, an empty, over-128-byte, non-ASCII, grammar-invalid,
fixed-value, or caller-expectation mismatch receives the corresponding
`digest.purpose`, `digest.algorithm`, `digest.profile`,
`digest.object_class_schema`, or `digest.framing` result. The new raw 129-byte
purpose and schema cases exercise this distinction without altering the frame
grammar or any accepted vector.

## Fixture and non-vacuity audit

The fixture tree contains 273 unique case identifiers: 70 accepted and 203
rejected. Sixty-nine accepted cases have a binary expectation; the remaining
accepted case is the deliberately non-normative exact diagnostic-rendering
boundary. The class counts are 15 well-formedness, 10 validity, 6
expectedness, 63 deterministic-profile, 1 CDDL-shape, 39 semantic-validity,
33 digest-verification, 15 resource, 17 differential-detection, and 4
operational-failure cases, in addition to the 70 accepted cases.

The accepted language is nonempty and includes each accepted atom class and
recursive container shape. Boundary cases cover every direct integer head,
maximum and one-over resource values, composed/decomposed Unicode, raw map
duplicates and both ordering choices, forbidden numeric tags and float widths,
signed zero, infinities, NaN payloads, interval invalid/unsupported
precedence, and extension duplicate/criticality order.

Relevant nonexamples remain rejected:

- decode-and-reencode equality is not strict conformance;
- CDDL match is not byte, duplicate, semantic, inferential, or kernel proof;
- a digest match is not collision absence, schema conformance, provenance, or
  semantic equality outside the named profile and separately validated schema;
- host dictionaries after duplicate collapse are not valid raw-map evidence;
- host floats and JSON numbers are not exact numeric constructors; and
- implementation agreement and replay are evidence, not normative authority
  or verification.

## Statistical and trust-boundary audit

The subject is deliberately data-free. It defines no logical table, Arrow
lowering, row/column identity, missingness, categorical semantics, privacy
property, physical normalization, real-data purpose identifier, or
logical-data digest. `Null` is only a literal and is not a missing-value
decision. RFC-0006 remains unchanged and outside SQ-0005 ownership.

Structural acceptance, canonical-byte equality, CDDL shape, object-schema
validity, digest verification, provenance, proof validity, identification,
inference, numerical correctness, and interpretation remain distinct. The
RFC explicitly disclaims theorem-source fidelity, external-premise truth,
artifact-byte binding, artifact-envelope validity, checker soundness,
registry authority, collision absence, privacy, and general `.statqed`
verification. No diagnostic is promoted into a model assumption or scientific
claim.

There is no statistical probability statement in the reviewed subject, so no
sampling, assignment, algorithmic, Monte Carlo, posterior, or other randomness
scope is invoked. The cryptographic digest statements are conditional framing
and nonclaim statements, not statistical coverage or error-probability claims.

## Migration and limitations

Any change to the accepted value classes, equality, byte rules, failure
precedence, resource numbers or counting, Unicode behavior, tag/extension
policy, or digest frame reopens RFC-0001 and normally requires a new profile
or framing identifier. Rational, decimal, bignum, IEEE, interval, tag, or
extension support cannot be added silently to `statqed.cbor-core.v1`.

This approval is limited to the exact hashes above. It does not establish
implementation conformance, cryptographic security, source-currentness,
workflow sufficiency, or integration readiness; those are owned by distinct
review records. It does not authorize the RFC/ADR status transition by itself.
Any candidate-byte or semantic change invalidates this disposition and
requires independent re-review.

Within these limits, no semantic ambiguity, unsupported statistical claim,
source conflict, or missing semantic fixture blocks the exact candidate. The
semantic-profile and numeric-model disposition is **APPROVE**.
