# Canonicalization Specification

Status: **Draft** implementation-facing summary of Accepted RFC-0001;
logical-data canonicalization remains blocked on RFC-0006.

## Scope

This document is the implementation-facing summary of
`statqed.cbor-core.v1`, the generic data-free structural profile selected by
RFC-0001. The RFC and its content-addressed evidence package are authoritative
for the decision. A library's native values or “canonical” option are not.

The profile accepts:

- exact integers from `-2^64` through `2^64-1`;
- bounded byte strings and exact Unicode-scalar text;
- bounded ordered arrays;
- bounded maps with integer or text keys after raw-entry duplicate checks;
- booleans and null.

It explicitly rejects bignums, rationals, decimals, IEEE values and all float
encodings, intervals, tags, extensions, undefined/other simple values,
indefinite lengths, and non-preferred heads. Unsupported semantic atoms are
not coerced into the accepted model.

This profile does not define logical tables, Arrow lowering, row or column
identity, categorical or missing-data semantics, physical normalization,
privacy, or a logical-data digest. RFC-0006 remains Draft under SQ-0027.

## Exact byte rules

Accepted values use preferred definite-length RFC 8949 CBOR. Map keys are
ordered by unsigned lexicographic comparison of their complete deterministic
key encodings, following RFC 8949 Section 4.2.1 core ordering. Length-first
ordering is rejected.

A decoder retains the complete ordered raw map-entry sequence. It validates
allowed key types and typed semantic duplicates before native-map
construction, then validates strict core order. Exact and non-preferred
equivalent keys are duplicates. Unicode scalar sequences are preserved
without NFC, NFD, NFKC, NFKD, case, or locale normalization, so composed and
decomposed text remains distinct.

The stable result taxonomy keeps resources, CBOR well-formedness, CBOR
validity, caller expectedness, deterministic-profile conformance, published-
syntax CDDL shape mismatch, producer semantic validity, separate object-schema
mismatch, digest verification, and operational failures separate. A forbidden
raw map-key type is `expected.map_key_type`; a producer-side forbidden key is
`semantic.map_key_type`. Decode-and-reencode equality is not strict
conformance evidence.

## Limits

| Resource | Limit | Counting rule |
|---|---:|---|
| CBOR input/output | 1,048,576 bytes each | Input is the entire supplied slice including trailing bytes; output is the entire canonical item. |
| One byte/text string | 65,536 content bytes | Text counts UTF-8 bytes. |
| Array items / map entries | 1,024 each | Direct children / key-value pairs. |
| Total CBOR items | 4,096 | Every scalar, container, attempted tag, map key/value, indefinite wrapper, and definite string chunk counts once. |
| Open array/map/tag levels | 32 | Root scalar depth is 0; each entered container or attempted tag adds one. |
| Accepted tags / extensions | 0 / 0 | Attempted tags are still parsed within resource bounds. |
| Diagnostic output | 4,096 UTF-8 bytes | Over-limit prose becomes a bounded summary. |
| Digest-frame allocation cap | 1,049,255 bytes | Conservative allocation ceiling. |
| Largest attainable valid frame | 1,048,918 bytes | Fixed identifiers and maximal accepted payload. |

The Linux conformance harness separately applies five seconds and 128 MiB per
probe. Typed-JSON diagnostic transports have their own documented 2,200,000
byte input ceiling and no normative authority.

## Generic data-free digest frame

`statqed.digest-lp.v1` hashes this exact preimage with SHA-256:

```text
"StatQED-Digest" || 0x00 ||
LP32(purpose_id) || LP32("sha-256") ||
LP32("statqed.cbor-core.v1") || LP32(object_class_schema_id) ||
LP32("statqed.digest-lp.v1") || LP32(payload)
```

`LP32(x)` is `u32be(len(x)) || x`. Identifiers are nonempty, at most 128
ASCII bytes, and match `[a-z0-9][a-z0-9._:-]*`. Payload is nonempty strict
profile bytes. Verification binds all identifiers and rejects fallback,
downgrade, truncation, extra bytes, component reordering, and ambiguity.
A missing prefix or declared body is `digest.component_length`; a fully
present identifier that violates its length, ASCII, grammar, fixed-value, or
caller expectation fails its field-specific `digest.*` code.

The frame binds but does not resolve or validate its object-class/schema
identifier. Schema validation is a separate prerequisite. Digest equality is
conditional evidence; it does not prove collision absence, provenance,
logical-data identity, privacy, or statistical validity.

## CDDL

The data-free `foundation_structural` prototype uses published RFC 8610 syntax
only. It demonstrates structural shape and its limitations. CDDL acceptance
does not prove preferred encoding, map order, duplicate semantics, Unicode
policy, semantic normalization, digest identity, provenance, proof validity,
or statistical validity. Module/import Internet-Draft syntax is not normative.

## Reproduce the evidence

From the repository root:

```bash
python3 scripts/serialization/run_conformance.py --verify
python3 scripts/serialization/check_evidence.py
python3 scripts/serialization/dependency_inventory.py --check
python3 scripts/serialization/check_yanked.py
```

The Rust prototype uses the exact toolchain and lock in
`schemas/prototypes/rust-cbor/`; its README records format, Clippy, build,
test, and offline lock-reproduction commands. The independently originated
standard-library Python oracle and exact interpreter evidence are under
`schemas/prototypes/python-oracle/`.

Semantic fixtures were committed before goldens. Binary vectors are retained
only when both implementations agree with the precommitted semantic result.
Historical failures and deliberately incorrect encoder/decoder behavior are
retained. Changing one implementation is never authority to replace a vector.

## Update and rollback

Any value, equality, byte, error-precedence, limit, tag/extension, or framing
change reopens RFC-0001 and normally requires a new profile/framing identifier.
Refresh sources, fixtures, both independent implementations, locks,
license/advisory evidence, conformance results, corruption tests, workflow,
and all reviews together. Rollback restores one complete previously reviewed
evidence set and identifiers; partial rollback is rejected as drift.

## Trust boundary and nonclaims

The prototypes, CPython, Rust, Cargo, dependencies, CDDL matcher, SHA-256
implementation, operating system, CI, and agents are untrusted evidence
producers. SQ-0005 establishes only a reviewed generic structural profile,
actual independent implementation observations, bounded failure behavior, and
generic data-free framing evidence.

It does not establish theorem-source fidelity, external assumptions, Lean
proof identity, artifact binding, artifact-envelope validity, certificate
checker soundness, registry authority, provenance truth, logical-data
identity, collision absence, identification, inference, numerical
certification, interpretation, or general `.statqed` verification.
