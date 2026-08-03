# ADR-0004: Deterministic CBOR with CDDL candidate

- Status: Proposed
- Blocking RFC/task: RFC-0001 / SQ-0005
- Decision owner: SQ-0005

## Context

Normative hashing and cross-language interchange require one accepted representation for each accepted semantic object. RFC 8949 defines multiple deterministic choices, and CDDL shape validation does not settle semantic normalization or byte behavior.

## Candidate decision

Prototype deterministic CBOR under one explicit RFC 8949 application profile with versioned CDDL files. JSON/YAML remain diagnostic/authoring projections only.

## Consequences

The full numeric/tag, map-order, duplicate, Unicode, extension, decoder, domain-separation, malformed-input, and resource profile must be explicit. CDDL module/import draft syntax is not assumed to be a standard. The artifact envelope and logical-data digest are separately governed.

## Alternatives

Canonical JSON and a custom format remain prototype comparators. Silent normalization versus strict rejection is an unresolved per-case decision.

## Validation and evidence

RFC-0001 requires two genuinely independent implementations or oracles, reviewed semantic fixtures, canonical bytes/digests, malformed/resource tests, mutation detection, and security review.

## Review

This ADR must remain Proposed until RFC-0001 is Accepted. No current document may treat deterministic CBOR/CDDL as implemented or normative.
