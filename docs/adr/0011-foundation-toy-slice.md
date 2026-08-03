# ADR-0011: Data-free structural foundation slice

- Status: Accepted
- Accepted: 2026-08-03
- Review surface: sha256:5793ce0b5c7e819090c74480e93e7167f6821897b96567c8b6c737bc8fa1ff96
- Review commit: `31fbd22`
- Review record: `work/reviews/SQ-0001.md`
- Independent reviewers: statistical architect, formal-methods reviewer, interoperability reviewer, security reviewer, counterexample reviewer
- Decision owner: SQ-0001

## Context

Plan 0001 needs one cross-language path through IR, encoding, registry, graph, envelope, Lean, and reporting without freezing real statistical semantics or a logical-data model prematurely.

## Decision

The first composed foundation fixture is data-free and non-statistical. Its reviewed semantic scope is:

- one analysis identity with fixture kind `foundation_structural`;
- no data/table, design/model/experiment, estimand, procedure, statistical claim, numerical obligation, external assumption, diagnostic, or extension;
- probability context explicitly `not_applicable`;
- one separate toy formal proposition `True`, represented through a toy theorem-registry record and a minimal assurance-graph theorem-application path;
- provenance records only for the fixture/build activities, treated as records rather than proof that external events occurred;
- explicit schema/profile/theorem/environment/envelope locks supplied by their owning later tasks.

SQ-0006 freezes the exact field names/IR fixture only after RFC-0001; SQ-0007 freezes the Lean declaration and theorem lock after RFC-0005; SQ-0009 freezes the toy graph after RFC-0002; SQ-0010 freezes the envelope; SQ-0019 composes them. SQ-0001 freezes no canonical bytes.

`True` is definitionally trivial and is classified as a test-only conformance record, not a public statistical theorem or a non-vacuity witness. It cannot satisfy any public-theorem non-vacuity gate. The later bytes-for-`False` mapped to `True` mutation checks only the exact byte-to-proposition binding path; passing it does not establish a general decoder, theorem-registry, or formalization capability.

## Verification result and nonclaims

The planned result is structural validation, canonical-byte conformance under an accepted profile, toy lock resolution, and—only after RFC-0003—kernel checking of the exact toy proposition. It establishes no:

- identification result or estimand;
- coverage, type-I error, power, multiplicity, posterior, or other probability guarantee;
- external-assumption truth;
- certified numerical method;
- physical data or provenance truth;
- frontend fidelity beyond this exact fixture;
- theorem validity merely from lock resolution;
- public-theorem non-vacuity from the test-only `True` record;
- canonical-format status before RFC-0001;
- artifact-level kernel verification before RFC-0003.

## Alternatives

A real statistical method was rejected as premature. A toy table was rejected because it would force the unresolved logical-data/digest model. A purely empty artifact was rejected because it would not exercise theorem registry and graph composition.

## Validation and evidence

The slice must pass shared semantic, byte, digest, malformed, mutation, lock-substitution, graph, trust-report, and clean-checkout tests under the later accepted interfaces. Independent encoder evidence cannot share the Rust canonicalizer.

## Review

Acceptance requires statistical, formal, interoperability, adversarial, security/trust, and integration review. Each future verification-result record has exactly one mode; a document may show several results but never unions their evidence or reports an overall stronger status. This ADR defines scope/nonclaims, not an implemented artifact.
