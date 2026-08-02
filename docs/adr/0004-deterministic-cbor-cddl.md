# ADR-0004: Deterministic CBOR with CDDL

- Status: Proposed; requires prototype RFC

## Decision

Use deterministic CBOR for normative structured objects and CDDL for schemas. Offer JSON/YAML diagnostic projections only.

## Rationale

Normative hashing requires unambiguous numbers, ordering, binary values, and extension behavior.

## Validation

At least two independent implementations must produce identical canonical bytes and digests for golden vectors before acceptance.
