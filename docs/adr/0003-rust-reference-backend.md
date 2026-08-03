# ADR-0003: Rust reference operational backend

- Status: Accepted
- Accepted: 2026-08-03
- Review surface: sha256:5793ce0b5c7e819090c74480e93e7167f6821897b96567c8b6c737bc8fa1ff96
- Review commit: `31fbd22`
- Review record: `work/reviews/SQ-0001.md`
- Independent reviewers: interoperability reviewer, formal-methods reviewer, security reviewer, counterexample reviewer
- Decision owner: SQ-0001

## Context

StatQED needs a shared operational implementation for parsing, canonicalization, encoding, digests, registry utilities, archive handling, and CLI behavior without making source-language frontends semantic authorities.

## Decision

Use Rust for the reference operational backend and CLI. Rust implements accepted specifications; it does not define them.

## Constraints and consequences

Verification paths are deterministic, offline, bounded, and panic-free on untrusted input as tested properties, not properties inferred from using Rust. Project crates forbid unsafe code by default, but compiler, dependencies, runtime, FFI, and platform trust are still reported when relied upon. Production frontends call or bind to shared Rust canonicalization rather than duplicating it.

Agreement among several frontends that call the same Rust encoder is integration evidence, not independent encoder-conformance evidence. RFC-0001 requires an independently originated implementation or oracle before canonical bytes are accepted.

## Alternatives

Duplicated frontend canonicalizers were rejected due to differential behavior. Rust as semantic authority was rejected because normative meaning is governed by accepted specifications and reviewed formal declarations.

## Validation and evidence

Cargo supports workspaces and the required lint policy, but SQ-0002/SQ-0004 must select exact toolchains, package boundaries, dependencies, and hostile-input tests. See the SQ-0001 source audit.

## Review

Acceptance requires interoperability, security, and integration review of this role boundary.
