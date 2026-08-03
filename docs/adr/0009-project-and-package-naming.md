# ADR-0009: Project and foundation package naming

- Status: Accepted
- Accepted: 2026-08-03
- Review surface: sha256:5793ce0b5c7e819090c74480e93e7167f6821897b96567c8b6c737bc8fa1ff96
- Review commit: `31fbd22`
- Review record: `work/reviews/SQ-0001.md`
- Independent reviewers: source curator, statistical architect, interoperability reviewer, counterexample reviewer
- Decision owner: SQ-0001

## Context

The repository needs stable local names before toolchain bootstrap, while public registry reservation, similarity review, publication topology, and legal clearance are time-dependent and ecosystem-specific.

## Decision

Use **StatQED** as the academic project/repository family name. Use `StatQED` as the Lean namespace, `statqed` as the local CLI executable and R/Python source package label, `StatQED` as the Julia source package label, and `.statqed` as the provisional artifact extension.

These are foundation source-tree conventions. They do not claim registry reservation, exclusive use, trademark clearance, a public Rust crate name, a Lake package name, or a stable Julia publication topology.

## Consequences

SQ-0003/SQ-0004/SQ-0013/SQ-0014/SQ-0015 recheck current registry syntax, availability/ownership, similarity rules, and publication layout before freezing manifests. Julia must test a General-compatible mirror/split/publication path. Internal workspace crate names and APIs remain unpublished by default. Generated bindings are non-authoritative.

## Alternatives

Freezing every public registry name now was rejected because point-in-time 404 responses are neither reservations nor clearance. Renaming the project was not supported by current technical evidence.

## Validation and evidence

The spellings are syntactically admissible under reviewed official rules. On 2026-08-03 exact PyPI, CRAN, and Julia General endpoints returned 404; crates.io returned a 403 data-access denial. GitHub organization/domain availability and trademark/confusion clearance remain unresolved. See the SQ-0001 source audit.

## Review

Acceptance requires source, interoperability, statistical-scope, and integration review with these limitations retained.
