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
