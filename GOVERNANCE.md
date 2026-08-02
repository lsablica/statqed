# StatQED Governance

StatQED begins as a founder-led academic project but is designed to become community-governed.

## Current authority

Until a formal steering body is constituted, the repository owner is the release authority. This does not waive required semantic, formal, and source reviews. A single maintainer may merge only after the documented review evidence exists.

## Planned bodies

- **Ontology Council:** core statistical meanings, assurance graph, IR, evidence categories.
- **Formal Methods Council:** Lean architecture, trusted checkers, axiom policy, proof review.
- **Methods Council:** method-pack scientific scope and source fidelity.
- **Interoperability Council:** schemas, canonicalization, frontends, compatibility.
- **Community Council:** contribution policy, credit, releases, conduct, accessibility.

Membership criteria and voting rules require an RFC before the first Candidate release.

## Decision classes

| Class | Examples | Process |
|---|---|---|
| Routine | internal refactor, docs correction | pull request review |
| Interface | public API within accepted semantics | task contract + compatibility review |
| Constitutional | ontology, trust, normative format | RFC + designated reviews |
| Emergency | security or artifact-integrity issue | restricted patch + retrospective RFC |

## Transparency

Accepted decisions, dissenting technical arguments, migrations, and known limitations remain in the repository. Private security reports are handled according to `SECURITY.md`.

## Releases

No release may claim Stable semantics without:

- accepted versioned specifications;
- conformance vectors;
- reproducible builds;
- source and theorem locks;
- migration policy;
- independent review of trusted paths;
- documented known limitations.

See `docs/governance/release-policy.md`.
