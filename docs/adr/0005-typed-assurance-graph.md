# ADR-0005: Typed Statistical Assurance Graph

- Status: Proposed
- Proposed ratification date: 2026-08-03
- Decision owner: SQ-0001
- Governed taxonomy: RFC-0002; ontology boundary: RFC-0004

## Context

A flat certificate or binary badge hides dependencies and invites promotions among computation, empirical premises, and scientific conclusions.

## Decision

Represent the justification of a reported claim as a typed DAG whose deductive and non-deductive relations are distinct. Reports expose dependency closures and unresolved/external leaves.

## Prohibitions and consequences

Identification, inference, computation, data-derived facts, external premises, attestations, diagnostics, citations, provenance, and unresolved obligations remain distinct. Attestations, diagnostics, citations, provenance, and policy records never discharge an external premise. Deductive refinement/implication edges require checked evidence in the required direction.

Exact public node/edge types remain blocked on RFC-0002/RFC-0004 and SQ-0008/SQ-0009.

## Alternatives

A flat certificate and total assurance score were rejected because they obscure weak links. An untyped generic graph was rejected because edge type confusion would become a soundness/reporting risk.

## Validation and evidence

SQ-0009 must include positive, negative, malformed, ablation, and overclaim fixtures, including every prohibited promotion.

## Review

Acceptance requires statistical, formal, interoperability, adversarial, and integration approval of RFC-0002 and this architectural boundary.
