# Statistical IR Specification

Status: **Draft; public ontology blocked on RFC-0002 and RFC-0004**.

The IR is a typed, language-neutral graph of analysis semantics. It is not source-language AST and contains no R/Python/Julia-specific object.

## Top-level envelope

- schema version and feature set;
- analysis identity;
- data declarations and commitments;
- design/model/experiment declarations;
- estimands;
- procedures;
- claims;
- numerical obligations;
- evidence and provenance references;
- extension declarations.

## Required principles

- stable identifiers within an artifact;
- explicit numeric types: integer, rational, dyadic, fixed decimal, IEEE bits, interval;
- explicit missing values and categorical levels;
- typed weights and structured probability contexts once RFC-0004 is accepted;
- deterministic maps/lists and a governed Unicode policy once RFC-0001 is accepted;
- no unknown critical extension acceptance;
- lossless round trip through the normative encoding.

Dialect details are added through versioned RFCs and CDDL schemas.

## Experimental data-free foundation fixture

SQ-0006 defines only `statqed.foundation-structural.v0`, a closed
`foundation_structural` fixture with exactly `schema_id`, `schema_version`,
`fixture_kind`, `analysis_id`, `probability_context`, and `features`.
`probability_context` is exactly `not_applicable` and `features` is exactly
empty. Every other field is absent and rejected, rather than represented by a
null or empty placeholder.

This fixture is a structural bootstrap witness, not the top-level envelope
listed above. It defines no data, experiment, estimand, procedure, claim,
evidence, provenance, theorem, artifact, certificate, or public probability
context. RFC-0002 and RFC-0004 still block the public statistical ontology;
RFC-0006 still blocks logical-data semantics.
