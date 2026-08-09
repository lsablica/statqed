# ADR-0004: Deterministic CBOR with published-syntax CDDL

- Status: Accepted
- Blocking RFC/task: RFC-0001 / SQ-0005
- Decision owner: SQ-0005
- Profile: `statqed.cbor-core.v1`

## Context

Normative hashing and cross-language interchange require one accepted byte
representation for each accepted semantic structural object. RFC 8949 offers
multiple deterministic map-order choices, and CDDL shape validation does not
settle semantic values, duplicates, Unicode, normalization, canonical bytes,
resource behavior, or digest framing.

## Decision

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

RFC-0001 contains the complete semantic value model, numeric and Unicode
policy, raw map-entry and duplicate rules, error taxonomy, resource limits,
digest framing, security considerations, evidence, migration rules, and
explicit nonclaims. That RFC is the detailed normative source; this ADR
records the Accepted architecture consequence.

## Consequences

- Structural schemas may use published RFC 8610 CDDL syntax, but CDDL success
  is not canonical-byte, semantic, digest, provenance, proof, or statistical
  verification.
- Tags, floats, extensions, rational/decimal/bignum atoms, intervals, and
  logical tables require later separately versioned decisions rather than
  implementation-specific coercion.
- Decoders preserve raw map entries until typed duplicate and order checks are
  complete and reject non-profile bytes instead of silently normalizing them.
- Object-class schema validation remains separate from generic profile and
  digest-frame validation.
- RFC-0006, artifact envelopes, archives, theorem locks, and certificates are
  unaffected and remain separately governed.

## Alternatives rejected for v1

Length-first map ordering, silent decode/reencode normalization, library
“canonical” defaults, canonical JSON, a custom binary format, Unicode
normalization, numeric coercion, and normative CDDL draft module/import syntax
are rejected for the reasons and discriminating evidence in RFC-0001.

## Validation and evidence

SQ-0005 commits semantic fixtures before golden bytes, uses independent Rust
and Python implementation lineages, retains malformed/resource/failure
evidence, proves deliberate encoder and decoder divergence detection, and
binds the complete evidence package with a permanent verifier. Evidence does
not promote either runtime or prototype implementation into the trusted
computing base.

## Review

This ADR is Accepted because the exact marked scope above matches Accepted
RFC-0001 byte-for-byte, the required distinct reviewers approved the
content-addressed candidate, the serialization workflow passed, and the
integration reviewer approved the atomic status transition. Acceptance does
not strengthen the trust or validity claims beyond that marked scope.
