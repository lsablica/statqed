# ADR-0008: Minimal trusted base and untrusted producers

- Status: Accepted
- Accepted: 2026-08-03
- Review surface: sha256:5793ce0b5c7e819090c74480e93e7167f6821897b96567c8b6c737bc8fa1ff96
- Review commit: `31fbd22`
- Review record: `work/reviews/SQ-0001.md`
- Independent reviewers: formal-methods reviewer, interoperability reviewer, security reviewer, counterexample reviewer
- Decision owner: SQ-0001
- Exact artifact-binding boundary: RFC-0003 / SQ-0012

## Context

Statistical workflows rely on large source-language runtimes, solvers, libraries, report generators, and agents. Trusting the whole stack would make assurance opaque and fragile.

## Decision

Keep producers outside a verification mode's trusted base only when their outputs are independently rebound and checked for the exact proposition used. Verification reports distinguish logical kernel TCB, semantic review base, artifact-binding obligations/TCB, operational TCB, cryptographic assumptions, and external premises.

## Consequences

R, Python, Julia, solvers, reports, and AI agents are untrusted by default, not unconditionally. A decoder, bridge, compiler, native checker, or generator joins the relevant operational TCB whenever its unchecked output determines the interpreted artifact or proposition. Every checker has a precise acceptance proposition, bound inputs, corruption/resource tests, and a soundness path.

## Alternatives

Trusting the full analysis environment and claiming that the Lean kernel alone validates artifact bytes were rejected. Exact byte-to-term architecture remains deferred, not silently assumed.

## Validation and evidence

RFC-0003/SQ-0012 must select and test the byte-to-term adequacy path. RFC-0005 governs theorem/proof/environment/axiom locks. Trust reports must enumerate actual components and nonclaims by mode.

## Review

Acceptance covers only this minimal-TCB direction and untrusted-producer rule. Artifact-level kernel verification remains prohibited until RFC-0003 is Accepted and implemented.
