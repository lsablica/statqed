# ADR-0002: Lean 4 is the initial normative proof backend

- Status: Accepted
- Accepted: 2026-08-03
- Review surface: sha256:5793ce0b5c7e819090c74480e93e7167f6821897b96567c8b6c737bc8fa1ff96
- Review commit: `31fbd22`
- Review record: `work/reviews/SQ-0001.md`
- Independent reviewers: source curator, statistical architect, formal-methods reviewer, counterexample reviewer
- Decision owner: SQ-0001

## Context

StatQED needs an initial backend for formal definitions, public theorem statements, checker-soundness proofs, and kernel checking, without claiming that one prover's syntax defines all cross-language semantics.

## Decision

Use Lean 4 with a pinned Mathlib revision as the initial normative proof backend. Accepted language-independent specifications govern interoperable object meaning; reviewed Lean declarations govern the exact formal propositions checked by this backend.

## Consequences

Toolchain versions and axiom baselines remain SQ-0002/SQ-0003 decisions. Kernel acceptance establishes only the exact proposition relative to the locked environment and actual axiom report. It does not establish source fidelity, external premises, artifact-byte binding, provenance truth, or interpretation. General mathematics should be proposed upstream when feasible, not assumed to be accepted upstream.

## Alternatives

Multiple proof backends and a custom proof kernel were rejected for the foundation because they multiply semantic and interoperability risk. Prover-neutral artifact design remains a goal where it does not obscure the initial checked semantics.

## Validation and evidence

Official Lean documentation describes kernel validation, axioms, and Lake locking; Mathlib exposes relevant Markov-kernel infrastructure. No current toolchain compatibility or roadmap-wide Mathlib sufficiency is claimed. See the SQ-0001 source audit.

## Review

Acceptance requires formal, statistical, source, and integration review. Artifact-level kernel claims remain blocked on RFC-0003.
