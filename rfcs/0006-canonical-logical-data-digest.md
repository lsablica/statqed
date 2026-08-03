# RFC-0006: Canonical Logical Data and Digest

- Status: Draft
- Author: foundation interoperability team
- Reviewers: statistical architect, interoperability reviewer, formal-methods reviewer, security reviewer
- Created: 2026-08-03
- Task: SQ-0027 (with encoding prototypes from SQ-0005 and a deliberately data-free foundation from SQ-0006/SQ-0011)
- Supersedes: none

## Decision boundary

Define the canonical logical table/data model, the lowering from supported physical transports, the exact bytes or structured object covered by a logical digest, the hash/profile/domain-separation rules, and the limits of any resulting data-binding claim.

## Motivation

Arrow and language-specific tables admit multiple physical encodings and metadata choices for the same intended logical data. Conversely, superficially similar tables may differ in row order, type, missingness, categorical levels, or numeric meaning. A digest cannot be governed before the logical object is exact.

## Terminology and source background

- **Physical transport:** bytes/layout used by Arrow or a source language.
- **Logical data object:** the versioned StatQED representation after a reviewed lowering.
- **Logical digest:** a named hash over domain-separated canonical bytes for that logical object.
- **Digest match:** equality of recomputed and recorded digest values under the named algorithms/profile; not proof of collision-freedom, physical provenance, or truthful collection.

Exact Arrow and hashing sources are a required input to this RFC before acceptance.

## Examples and nonexamples

Examples:

- Two accepted Arrow physical layouts lower to the same logical table and therefore the same logical digest.
- Changing one row, column order where order is semantic, exact type, missingness marker, or categorical-level declaration changes the logical object and digest.
- An exact byte comparison can establish equality of available canonical bytes; a digest comparison is conditional on named cryptographic assumptions.

Nonexamples:

- Hashing raw Arrow files and calling the result a format-independent logical digest.
- Treating decimal text, rational values, and IEEE bit patterns as interchangeable.
- Omitting row/column identity, categorical levels, missingness semantics, or relevant metadata from the digest domain without a reviewed rule.
- Claiming that a digest proves which physical data were observed or that provenance records are truthful.

## Alternatives

### Digest raw transport bytes

Rejected as the logical digest; it may remain a separate physical-file commitment.

### Digest canonical IR data bytes

Provisional direction, contingent on RFC-0001 and the data dialect schema.

### Use transport-independent Merkle commitments

Deferred. They may support large/partial datasets later but add ordering, chunking, proof, and resource semantics.

### Omit data from the foundation fixture

Accepted as a simplification for the first toy slice. SQ-0011 therefore remains strictly data-free; SQ-0027 must resolve this RFC before the first normative real-data schema/backend path, logical digest, or real-data artifact binding.

## Proposed semantics

No logical data model or digest profile is Accepted. A successor must settle row and column identity/order, names, exact types, numeric atoms, missingness, categorical levels, relevant metadata, physical-to-logical lowering, canonical encoding profile, hash algorithm, domain separation, schema/profile versioning, and resource limits.

## Formal and implementation consequences

- SQ-0005 must test the required numeric/missingness/category atoms relevant to canonical encoding.
- SQ-0006 and SQ-0011 remain deliberately data-free; they do not implement a logical-data schema or digest.
- SQ-0027 must accept this RFC before adding the first normative real-data schema, digest, or backend path.
- Frontend adapters record transport-specific provenance separately from logical data commitments.

## Trust, security, privacy, and accessibility

Threats include row/type substitution, Unicode/name confusion, ambiguous missingness, extension omission, hash-domain confusion, collision/second-preimage attacks, resource exhaustion, and privacy leakage through commitments. Reports state precisely what bytes/object were recomputed and which external/cryptographic assumptions remain.

## Compatibility and migration

A change in logical lowering, included metadata, canonical profile, hash algorithm, or domain separation creates a new digest profile. Lossy migrations create a new artifact/data identity and disclosure.

## Validation plan

- primary Arrow/logical-type and cryptographic source audit;
- equivalent-physical-layout and semantic-mutation fixtures;
- cross-language exact numeric/missing/category tests;
- hash/profile/domain-separation and resource-limit tests;
- statistical, interoperability, formal, security, and adversarial review.

## Objections and resolution

- **Objection:** The first slice should exercise data digests. **Resolution:** a premature toy table would freeze unresolved data semantics; the foundation fixture is intentionally data-free, and SQ-0027 must resolve and test this RFC before the first real-data schema/backend path or logical-data-binding claim.

## Decision

Deferred to SQ-0027. This RFC is the explicit blocker for the first normative real-data schema/backend path and canonical logical-data digest. A raw-file checksum may be called only a physical commitment and must not be substituted for the unresolved logical digest.
