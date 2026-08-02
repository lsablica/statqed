# Merge Gates

Every pull request must pass applicable gates.

## Universal gates

- task contract valid;
- dependencies complete;
- allowed-file scope respected;
- repository checks pass;
- implementation tests pass;
- documentation and plan/status updated;
- handoff complete;
- no false maturity or verification claim;
- generated files reproducible.

## Trusted-path gates

- no `sorry`, `admit`, project axiom, or unreviewed unsafe construct;
- axiom report matches accepted baseline;
- theorem/checker statement lock present;
- source and semantic reviews approve;
- independent formal review;
- trust report updated;
- negative/corruption tests pass.

## Schema/canonicalization gates

- schema parses;
- positive/negative vectors;
- canonical byte/digest vectors;
- second implementation comparison;
- unknown extension behavior;
- resource/security tests;
- migration impact.

## Frontend gates

- shared conformance vectors;
- unsupported features fail explicitly;
- no duplicated normative canonicalizer;
- exact numeric conversion;
- provenance;
- package-native tests;
- report status fidelity.

## Integration gates

- rebase/current base;
- clean checkout build;
- full cross-module tests when public interfaces change;
- no dependency cycle;
- no stale plan/backlog entries;
- quality dashboard updated for milestones.

## Reviewer independence

High-risk changes require at least:

- one author;
- one semantic/source reviewer;
- one formal/conformance reviewer;
- one integrator.

One person/agent may fill multiple review roles only for low-risk work and must document the exception.
