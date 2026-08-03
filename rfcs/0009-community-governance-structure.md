# RFC-0009: Community Governance Structure

- Status: Draft
- Author: foundation governance team
- Reviewers: community representative, statistical governance reviewer, formal-methods governance reviewer, interoperability reviewer, integration reviewer
- Created: 2026-08-03
- Task: SQ-0020; must be Accepted before SQ-0020 completes or any steering body exercises authority
- Supersedes: none

## Decision boundary

Define membership, appointment/removal, voting, recusals/conflicts, quorum, decision authority, appeals, transparency, term limits, succession, and emergency powers for the planned Ontology, Formal Methods, Methods, Interoperability, and Community bodies.

## Motivation

The founder-led phase can merge reviewed work, but planned community bodies cannot exercise undefined authority. Statistical meaning, theorem/trust interfaces, package interoperability, credit, and security decisions need accountable governance before Candidate maturity.

## Examples and nonexamples

Examples:

- A reviewer with a material conflict recuses under a documented rule.
- Constitutional changes name quorum, eligible voters, dissent, and appeal path.
- Emergency security action has bounded authority and mandatory retrospective review.

Nonexamples:

- Treating the planned councils listed in `GOVERNANCE.md` as currently constituted.
- A single maintainer waiving required scientific/formal review.
- Undisclosed private votes or permanent emergency authority.

## Alternatives

### Permanent founder control

Rejected as the long-term model because it conflicts with the charter's durability and community-governance goals.

### Immediate multi-council constitution during SQ-0001

Deferred. Membership criteria require community participation and operational evidence unavailable at scaffold time.

### One steering committee

Retained as an alternative for the RFC; it may be simpler than several councils if review-specialization and conflict rules remain explicit.

## Proposed semantics

No community body is constituted by this Draft. Current release authority remains as stated in `GOVERNANCE.md`, subject to mandatory independent review evidence. SQ-0020 must resolve and Accept this RFC before it can complete; if the evidence is insufficient, SQ-0020 remains BLOCKED rather than handing an unresolved decision to an unspecified future owner.

## Formal and implementation consequences

Governance metadata may later identify authorized decision roots for theorem registries, releases, and RFCs, but authorization never replaces formal proof or semantic review. Repository automation must not encode voting rules before acceptance.

## Trust, security, privacy, and accessibility

Rules must address capture, conflicts, private security handling, contributor safety, accessibility, timezone/language inclusion, and publication of decisions/dissent without exposing confidential reports.

## Compatibility and migration

Changes after acceptance require a successor RFC with transition/succession rules. Existing artifact/theorem identities and source credit remain immutable.

## Validation plan

- community consultation;
- mock constitutional, routine, conflicted, and emergency decisions;
- statistical/formal/interoperability/community/legal-process review as appropriate;
- documented succession and appeal exercise.

## Objections and resolution

- **Objection:** Governance is unrelated to the executable foundation. **Resolution:** exact council rules are deferred, but leaving the constitutional promise ownerless would allow planned bodies to be described as real or Candidate authority without a decision.

## Decision

Deferred to SQ-0020. The planned councils have no current membership or voting authority. SQ-0020 remains BLOCKED until this RFC is Accepted, and Candidate governance claims remain blocked until acceptance.
