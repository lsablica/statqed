# Statistical IR Specification

Status: **Draft 0**.

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
- typed weights and randomness scopes;
- deterministic maps/lists and Unicode normalization;
- no unknown critical extension acceptance;
- lossless round trip through the normative encoding.

Dialect details are added through versioned RFCs and CDDL schemas.
