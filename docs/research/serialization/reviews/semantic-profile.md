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

The earlier interval, result-taxonomy, resource-counting, corpus-count, and
source-attribution defects were corrected before this review. In the final
subject, producer semantic validity no longer absorbs object-schema
invariants; `schema_mismatch` belongs only to a separately identified schema
validator. The RFC now correctly identifies RFC 9682 as the formal update to
RFC 8610 and treats RFCs 9165 and 9741 as optional published extensions that
the minimum profile does not require. That attribution correction changes no
semantic constructor, accepted byte, equality relation, failure precedence,
resource bound, or fixture expectation.

This reviewer did not author or edit the candidate, semantic model, profile,
fixtures, RFC, ADR, canonicalization spec, source audit, implementations, or
generated evidence. This record reviews definitions, classifications,
fixtures, serialization consequences, and trust claims. It does not review
implementation correctness or by itself accept RFC-0001 or ADR-0004.

## Exact subject

The review was performed at repository HEAD
`a0737efe5a9bee1a6d37ac358d8a8b9a8011e78f`. The semantic model, profile,
and complete fixture directory are unchanged from frozen semantic commit
`b2ec69de45a3406cdcf29aec3243f81e8a42432f`.

| Subject | SHA-256 or identity |
|---|---|
| Semantic/fixture frozen commit | `b2ec69de45a3406cdcf29aec3243f81e8a42432f` |
| `docs/research/serialization/semantic-value-model.md` | `a94588e54fdc3e2aa08e73f5f6e76bb71128940bb245305b2dec9dffa2ffcfb2` |
| `docs/research/serialization/profile-candidate.md` | `c164816bb1d7c8bb1dd0683343d25b018964e2da417aa17a9bb366490d8b2679` |
| `rfcs/0001-deterministic-encoding.md` | `79aa54a53d914bb47689a4256daddd2e5832da10936ec8b551e0d93d26ad7f38` |
| `docs/adr/0004-deterministic-cbor-cddl.md` | `004b41b65dc8450de6f0bd8431f7de2e1f885e95dfd985f50981e1c1c5c9e49d` |
| RFC/ADR marked normative-scope block | `737847efcdb917f8c3db8c05c314c85f62775fa8ca80638a56de69cadb0fc060` |
| `docs/spec/canonicalization.md` | `355bb36a3c41021ef75c52da61bf90501866cbef0abaa2f20bdb757e8f1afa90` |
| Semantic fixture content tree | `61aca5d116ab07bae26265a35c112668c34dbfae2c274dda428d856cdbdfb2b6` |
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
| `digest-framing.json` | `75b11a2b6069f759710cd132d92a8ef1d91a0dbc1488f85f14f3920819277a19` |
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

## Fixture and non-vacuity audit

The fixture tree contains 271 unique case identifiers: 70 accepted and 201
rejected. Sixty-nine accepted cases have a binary expectation; the remaining
accepted case is the deliberately non-normative exact diagnostic-rendering
boundary. The class counts are 15 well-formedness, 10 validity, 6
expectedness, 63 deterministic-profile, 1 CDDL-shape, 39 semantic-validity,
31 digest-verification, 15 resource, 17 differential-detection, and 4
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
