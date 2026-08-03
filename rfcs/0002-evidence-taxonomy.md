# RFC-0002: Evidence and Assurance Taxonomy

- Status: Draft
- Author: SQ-0001 manager
- Reviewers: statistical architect, formal-methods reviewer, interoperability reviewer, counterexample reviewer
- Created: 2026-08-03
- Task: SQ-0001; concrete public types remain blocked on SQ-0008 and SQ-0009
- Supersedes: Draft placeholder installed at repository bootstrap

## Decision boundary

This RFC governs the constitutional distinction among propositions, claims, premises, evidence objects, attestations, diagnostics, citations, provenance records, and unresolved obligations. It also governs which assurance-graph relations may be deductive.

It does not freeze Lean constructors, IR tags, an assurance lattice, or report schema. Those interfaces remain Draft until SQ-0008 and SQ-0009 implement the accepted distinctions with examples, nonexamples, and independent review.

## Motivation

An artifact can be formally well-formed while making an invalid scientific promotion: a residual may be presented as a solution certificate, a diagnostic as proof of a model premise, an attestation as truth, or a citation as proof that a theorem applies. A single `evidence` bucket makes these category errors difficult to detect.

## Terminology and source background

- A **proposition** is a statement capable of being assumed or established in a named formal semantics.
- A **claim** is a typed proposition selected for possible reporting, together with its scope and interpretation limits.
- A **premise** is a proposition required by a deductive step. A premise may itself be derived or remain external.
- An **external assumption** is a premise about the scientific or physical world that the artifact does not derive.
- An **evidence object** is an object with a typed interpretation specifying exactly which proposition, if any, it can support and under which verification mode.
- An **attestation** records that an identified actor asserts or accepts a proposition or event description. It does not establish the asserted proposition's truth.
- A **diagnostic** is a computed or observed object that may inform judgment. It is not a deductive discharge of a model, design, or measurement premise.
- A **citation** is a source locator and attribution record. It does not by itself establish source fidelity, applicability, or truth.
- A **provenance record** describes an entity, activity, agent, or asserted lineage. It does not by itself establish that the described physical event occurred.
- An **unresolved obligation** records missing support. It is not evidence for a proposition.

This taxonomy applies the separations in `CHARTER.md` and the audit rules in `agents/protocols/semantic-audit.md`. It does not claim that an external evidence standard already supplies StatQED's statistical semantics.

## Examples and nonexamples

Examples:

- Kernel acceptance of a proof term supports the exact elaborated proposition relative to the named environment and axiom report.
- A checker result may support a numeric proposition only when the accepted inputs are bound and a checked soundness theorem links acceptance to that proposition.
- A deterministic transformation check may support an exact data-derived proposition about the bound logical input.
- An attestation may support only that the artifact contains a record attributing assertion P to actor A under policy V. A claim that A actually made the assertion requires separate authentication evidence and explicit premises.
- A diagnostic may have a non-deductive `informs judgment` edge to a decision record.

Nonexamples:

- Balance diagnostics do not prove that treatment was randomized.
- A small residual does not prove a small solution error without explicit conditioning, rank, and error-bound premises.
- A solver log or replay trace does not prove convergence or optimality without a separate checked obligation.
- An attestation that a protocol was followed does not prove that the protocol was followed.
- A citation to a theorem does not prove that its hypotheses hold or that a formalization matches the source.
- A matching digest does not prove physical data identity or collision-freedom; it records equality of recomputed digests under named algorithms and representations.
- An unresolved obligation cannot appear in the accepted deductive closure of a claim.

## Alternatives

### One undifferentiated evidence type

Rejected. It makes invalid promotions easy and report language ambiguous.

### A total assurance score or fixed linear ladder

Rejected. Assurance dimensions are only partially ordered where a reviewed theorem or policy defines an order; averaging can hide an external or unresolved premise.

### Encode every relation as a proposition immediately

Deferred. Formalizing narrow relations is desirable, but provenance, human judgment, source fidelity, and external events still need explicitly non-deductive records.

## Proposed semantics

1. Deductive edges connect propositions only through a kernel-checked theorem or a checker-soundness path that names every premise and exact conclusion.
2. Checked computation establishes only its checker proposition. It does not establish identification, an inferential guarantee, an external assumption, or an interpretation.
3. Data-derived facts remain distinct from external truth about collection, measurement, or protocol adherence.
4. Attestations establish only that an assertion record exists and contains the declared attribution; they never establish that the named actor made the assertion or discharge the asserted external premise without separate authentication evidence and premises.
5. Diagnostics use non-deductive judgment edges unless a registered theorem derives a distinct formal proposition from explicit premises. The theorem does not make a physical-world premise true.
6. Citations and provenance are attribution and lineage records. Any proposition they establish must be narrowly typed to the record itself.
7. An unresolved obligation blocks any status that would require that obligation to be discharged.
8. Refinement, weakening, implication, and compatibility edges are deductive only when locked to a checked theorem in the required direction. Review-only classifications remain visibly non-deductive.
9. Reports expose the dependency closure by category and do not collapse dimensions into a single `verified` result.

## Formal and implementation consequences

- SQ-0008 must use distinct types or tags for propositions, external assumptions, evidence objects, diagnostics, attestations, citations, provenance, and unresolved obligations.
- SQ-0009 must make invalid diagnostic/attestation/citation/provenance-to-premise discharge unconstructible or reject it during validation.
- A support edge records the exact proposition established, the verification mode, the checker/theorem lock when applicable, and remaining premises.
- Evidence and assurance statuses are not inferred from labels alone.
- Meaning-bearing tags and edge kinds require conformance vectors and compatibility review.

## Trust, security, privacy, and accessibility

Type confusion is a soundness and report-overclaim risk. Parsers must reject unknown critical support types and mismatched proposition references. Attestations and provenance may carry sensitive identity or workflow data, so disclosure and redaction rules must not alter the claim dependency closure. Human reports must use category names and nonclaims understandable without color or badge interpretation.

## Compatibility and migration

Bootstrap documents that use `evidence` loosely are Draft and must be revised before public type freeze. A future migration may split a broad legacy record into several typed nodes; it must not invent deductive support. Meaning changes require a new schema/semantic version.

## Validation plan

- positive examples for checked propositions, data-derived facts, and declaration attestations;
- nonexamples for diagnostic, attestation, citation, provenance, residual, replay, and digest promotions;
- graph rejection fixtures for every prohibited deductive edge;
- a forged unsigned record naming another actor, which must not establish an actor-event claim;
- report tests exposing external and unresolved leaves;
- statistical, formal, interoperability, adversarial, and integration review;
- conformance review of exact public tags in SQ-0008/SQ-0009.

## Objections and resolution

- **Objection:** An attestation should make a protocol premise usable. **Resolution:** it may record acceptance of the premise for a conditional analysis, but the premise remains an external leaf and is not proved true.
- **Objection:** A diagnostic can sometimes imply a formal property. **Resolution:** only a theorem with explicit premises may derive that property; the diagnostic label alone supplies no implication.
- **Objection:** Citations are evidence in ordinary scholarship. **Resolution:** they remain essential source evidence and attribution, but are not deductive proof of applicability or formal-source fidelity.

## Decision

Draft pending re-review of this complete proposal. No implementation may treat these categories as frozen until this RFC is Accepted. SQ-0008, SQ-0009, and SQ-0017 remain blocked from freezing public taxonomy or report semantics until acceptance.
