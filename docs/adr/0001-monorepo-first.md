# ADR-0001: Begin with a monorepo

- Status: Proposed

## Decision

Keep normative specs, Lean semantics, Rust reference backend, frontends, method packs, conformance fixtures, benchmark seed, and agent protocols in one repository through the foundation phase.

## Rationale

Early changes cross every layer; atomic versioning and shared fixtures outweigh independent release cadence.

## Consequences

Method packs and mature frontends may later split after a stable extension protocol. Generated bindings and theorem locks remain tied to the core release process.
