# ADR-0007: Versioned theorem registry and statement locks

- Status: Proposed
- Blocking RFC/task: RFC-0005 / SQ-0007
- Decision owner: SQ-0007

## Context

Artifacts need stable, citable formal references, but theorem names or surface statement hashes do not identify exact meaning across environments.

## Candidate decision

Use a versioned theorem registry that distinguishes governed semantic ID/version, canonical elaborated proposition and environment lock, statement digest, proof/build lock, actual axiom report, canonical registry record, independently selected registry authorization root/policy with historical/revocation status, source/semantic/formal reviews, and checked compatibility paths.

## Consequences

Proof refactors may preserve semantic proposition identity only in the same locked meaning environment; they create new proof/build locks and axiom reports. Meaning changes create new versions. Metadata-only implication/equivalence never authorizes substitution.

## Alternatives

Name-only, semver-only, pretty-print-only, and proof-body-hash-as-semantic-ID schemes are rejected. The exact normalizer and environment closure remain prototype decisions.

## Validation and evidence

RFC-0005 and SQ-0007 require environment/definition mutations, forbidden-axiom mutations, whole-registry replacement and forged-governance metadata, root mismatch/revocation/resource cases, wrong-direction implications, canonical-record binding, independent normalization/oracle evidence, and offline resolution.

## Review

This ADR remains Proposed until RFC-0005 is Accepted. No theorem registry or statement-lock interface is frozen by SQ-0001.
