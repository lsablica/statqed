# ADR-0010: MIT license, citation, and source attribution

- Status: Proposed
- Proposed ratification date: 2026-08-03
- Decision owner: SQ-0001

## Context

The public verifier/specification ecosystem needs an open outbound license and explicit credit for original mathematics, formalization, software, standards, data, review, and method-pack contributions.

## Decision

License original repository code, specifications, and documentation under MIT unless a file states otherwise. Maintain top-level CFF citation metadata. Preserve third-party notices/licenses and cite original mathematical/software/standards sources at theorem, method-pack, artifact, and release granularity.

Formalization does not transfer authorship. Agents are tools rather than authors, while their model/tool provenance may be retained for reproducibility.

## Consequences

Copied standards code components/examples retain applicable upstream terms; a link or paraphrase is preferred when copying is unnecessary. CFF complements rather than replaces source lineage and artifact-specific citations. Future relicensing requires governance and rights review.

## Alternatives

Proprietary core verification and citation-only-without-license policies conflict with the charter. A dual-license or contributor agreement is not justified at foundation scope.

## Validation and evidence

`LICENSE` contains the MIT text and `CITATION.cff` declares CFF 1.2.0/MIT metadata. OSI/SPDX/CFF and source-lineage implications are recorded in the SQ-0001 source audit.

## Review

Acceptance requires source, attribution, and integration review. It is not legal advice or third-party license clearance.
