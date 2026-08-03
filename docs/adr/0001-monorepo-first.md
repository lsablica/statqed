# ADR-0001: Begin with a monorepo

- Status: Proposed
- Proposed ratification date: 2026-08-03
- Decision owner: SQ-0001

## Context

Foundation changes cross normative documents, Lean semantics, Rust reference behavior, schemas, frontends, fixtures, registry records, and agent protocols. These layers need atomic review and shared conformance assets before independent release boundaries are stable.

## Decision

Keep the normative specs, Lean semantics, Rust reference backend, frontend sources, method packs, conformance fixtures, benchmark seed, and agent protocols in one source repository through the foundation phase. Monorepo co-location does not make all components one public package or one compatibility/version axis.

## Consequences

Foundation changes can be reviewed atomically. Public package publication remains ecosystem-specific. Method packs and mature frontends may split only after an accepted extension, compatibility, and archival-verification policy. The Julia frontend requires a tested publication/mirror/split strategy before any General-registry promise.

## Alternatives

Starting with separate repositories was rejected because cross-layer semantic changes and shared fixtures would be difficult to coordinate. A permanent monorepo mandate was rejected; the decision is explicitly foundation-bounded.

## Validation and evidence

Cargo workspaces and package-local R/Python sources are compatible with a monorepo. The ordinary Julia General workflow needs later evidence for the subdirectory layout. See `docs/research/SQ-0001-constitutional-source-audit.md`.

## Review

Acceptance requires statistical-scope, interoperability, and integration review of the exact SQ-0001 review surface.
