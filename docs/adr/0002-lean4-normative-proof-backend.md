# ADR-0002: Lean 4 is the initial normative proof backend

- Status: Proposed

## Decision

Use Lean 4 with pinned Mathlib for formal semantics, theorem statements, checker soundness, and kernel verification.

## Rationale

Mathlib provides active probability infrastructure and a unified upstream community. Lean supports executable checkers and modern proof automation while retaining a small kernel.

## Consequences

The analysis-level artifact remains prover-neutral where feasible. Multiple proof backends are not an initial implementation goal. General lemmas should be upstreamed.
