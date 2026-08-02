# ADR-0007: Versioned theorem registry and statement hashes

- Status: Proposed

## Decision

Every public theorem has a stable ID, version, normalized statement hash, source anchors, assumption profile, reviews, examples, and compatibility relations.

## Consequences

Proof refactors can preserve a statement version; meaning changes cannot. Artifacts resolve exact theorem locks rather than names alone.
