# RFC-0007: Compatibility and Migration Semantics

- Status: Draft
- Author: foundation interoperability team
- Reviewers: interoperability reviewer, formal-methods reviewer, statistical architect, integration reviewer
- Created: 2026-08-03
- Task: SQ-0006, SQ-0007, SQ-0010, and SQ-0020
- Supersedes: none

## Decision boundary

Define compatibility separately for semantic objects, canonical bytes, logical-data digests, theorem meaning, method/checker locks, artifact envelopes, adapters, wire/error protocols, reports, and verification modes. Specify when a migration preserves a claim and when it creates a new artifact/result identity.

## Motivation

Semver ranges and “reader accepts old bytes” do not establish preservation of statistical meaning or theorem direction. A migration can preserve syntax while changing a premise, probability context, theorem environment, digest domain, or TCB.

## Terminology and source background

- **Byte-identical:** exact canonical bytes under the same accepted profile.
- **Semantic equivalence:** a reviewed or checked bidirectional relation over complete objects/propositions.
- **Directional compatibility:** a checked implication or migration in the direction required by the consumer claim.
- **Readable:** a parser can decode a representation; no claim-preservation implication follows.
- **Lossy conversion:** an explicit transformation that omits or changes meaning-bearing information.

The theorem-specific subset is governed by RFC-0005. Exact schema and envelope behavior depend on RFC-0001, RFC-0006, and SQ-0010.

## Examples and nonexamples

Examples:

- A new theorem may support an old locked claim only through a checked proof in the required direction with all instantiations recorded.
- A report-renderer update can be provenance-only when no normative object or accepted claim changes.
- A decoder reading an old schema is `backward-readable`; it is not automatically claim-preserving.

Nonexamples:

- A semver-compatible version range authorizes theorem, schema, or method substitution.
- Equal statement digests under different environments establish semantic equality.
- Re-encoding or lowering that changes logical data semantics preserves the old logical digest or artifact identity.
- A lossy migration silently drops unresolved assumptions or nonclaims.

## Alternatives

### One global project version

Rejected. Components evolve on different semantic and operational axes.

### Semver-only compatibility

Rejected as evidence; semver may summarize policy but cannot replace exact locks and checked relations.

### Never migrate; archive every implementation forever

Retained as an archival fallback but insufficient alone for usability and security maintenance.

### Defer exact compatibility matrices to the owning component RFCs

Accepted for SQ-0001. This RFC defines the required distinctions and remains Draft until Plan 0001 supplies concrete schemas, theorem locks, and envelope prototypes.

## Proposed semantics

Every compatibility claim names the source/target versions and canonical records, registry authorization root/policy and historical/revocation status where applicable, cryptographic profile, relation class, direction, evidence/proof/review lock, effects on bytes/digests/claims/TCB, and new result identity. Readability, semantic equivalence, directional implication, and loss are never conflated.

## Formal and implementation consequences

- Component schemas declare their own compatibility/migration rules under this RFC.
- Theorem compatibility uses RFC-0005 checked proof paths.
- CLI/wire/error compatibility is versioned separately from semantic artifacts.
- Frontend and renderer versions remain provenance-only unless their semantics are relied upon.
- SQ-0020 must test at least one old/new or mutated compatibility case before Candidate maturity is considered.

## Trust, security, privacy, and accessibility

Migrations must not execute bundled code, hide external/unresolved leaves, weaken resource bounds, or suppress nonclaims. Human reports show migration direction and losses in text. Historical verifiers and schemas are content-locked and archived.

## Compatibility and migration

This RFC governs its own future changes: once Accepted, a semantic correction requires a successor RFC. Draft text is not a compatibility promise.

## Validation plan

- byte-identical, readable-only, equivalent, directional, lossy, and incompatible fixtures;
- wrong-direction theorem implication and changed-environment cases;
- schema migration changing bytes but preserving reviewed semantics;
- migration that changes claim/nonclaim/TCB and therefore result identity;
- interoperability, formal, statistical, adversarial, and integration review.

## Objections and resolution

- **Objection:** The distinctions are too heavy for a Draft project. **Resolution:** implementations remain free to reject all incompatible versions; false compatibility is more damaging than explicit non-support.

## Decision

Deferred to SQ-0020. No compatibility promise beyond exact current locks is Accepted. SQ-0020 remains blocked until this RFC is Accepted; it may not complete while retaining ownership of an unresolved compatibility decision.
