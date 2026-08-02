# ADR-0005: Typed Statistical Assurance Graph

- Status: Proposed

## Decision

Represent the justification of a reported claim as a typed DAG rather than a flat certificate or binary badge.

## Consequences

Identification, inference, computation, data facts, attestations, diagnostics, citations, and unresolved obligations use distinct node/edge types. Reports compute dependency closures and expose external leaves.
