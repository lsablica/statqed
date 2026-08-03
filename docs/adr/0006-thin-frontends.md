# ADR-0006: Thin R, Python, and Julia frontends

- Status: Proposed
- Proposed ratification date: 2026-08-03
- Decision owner: SQ-0001

## Context

StatQED needs native ergonomics without allowing R, Python, or Julia runtime objects to redefine statistical or encoding semantics.

## Decision

Frontends provide typed constructors, checked adapters, untrusted producers, reports, and provenance while lowering to one accepted semantic IR and calling shared production canonicalization.

## Consequences

No frontend is a semantic source of truth. Unsupported behavior fails explicitly. Frontends expose source-package/adapter versions and relevant lowering choices. Shared conformance fixtures test semantic IR, canonical bytes, digests, and errors, while independent encoder evidence must not reuse the shared Rust canonicalizer.

## Alternatives

Independent normative frontend implementations were rejected for the foundation because they would duplicate canonicalization and increase drift. Opaque capture remains an explicitly lower-assurance mode.

## Validation and evidence

SQ-0013–SQ-0016 own package-native tests, exact numeric conversion, unsupported-feature failures, provenance, and shared fixture comparison.

## Review

Acceptance requires statistical-scope, interoperability, and integration review.
