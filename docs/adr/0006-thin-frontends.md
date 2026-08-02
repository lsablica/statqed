# ADR-0006: Thin R, Python, and Julia frontends

- Status: Proposed

## Decision

Frontends provide native ergonomics, checked adapters, producers, reports, and provenance while compiling to one shared IR/canonical backend.

## Consequences

No frontend is the semantic source of truth. Unsupported behavior fails explicitly. Conformance fixtures are shared across languages.
