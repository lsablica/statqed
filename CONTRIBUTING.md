# Contributing to StatQED

StatQED welcomes contributions in statistics, formal methods, numerical analysis, programming languages, software engineering, documentation, and benchmark design.

## Before contributing

Read:

- `CHARTER.md`;
- `AGENTS.md`;
- `docs/governance/rfc-process.md`;
- `docs/quality/definition-of-done.md`;
- the nearest scoped `AGENTS.md`.

Search the theorem registry and Mathlib before introducing a new public abstraction.

## Contribution classes

### Documentation or non-semantic maintenance

Examples: spelling, broken links, generated documentation, non-normative examples.

These generally require one review and repository checks.

### Implementation under an accepted interface

Examples: a certificate producer, frontend constructor, internal helper lemma, test fixture.

These require a task contract, tests, and the scoped review checklist.

### Semantic or trusted-path change

Examples: public definitions, theorem statements, evidence types, artifact encoding, canonicalization, checker soundness, trusted computing base.

These require:

- an accepted RFC or existing accepted design;
- source-lineage record;
- statistical-semantic review;
- formal or conformance review;
- adversarial tests;
- explicit compatibility assessment.

## Pull requests

A pull request should:

- name the task ID in its title;
- link the active execution plan;
- state the claim boundary;
- list changed public interfaces;
- identify trust-boundary effects;
- include tests and review records;
- update plan/status documentation;
- remain small enough for substantive review.

Use `.github/PULL_REQUEST_TEMPLATE.md`.

## Formal theorem contributions

Every public statistical theorem must include:

- exact source anchor or original-result declaration;
- explanation of all hypotheses;
- nontrivial witness that assumptions are jointly satisfiable;
- at least one finite or concrete example where feasible;
- ablation or counterexample tests for material assumptions;
- explicit randomness scopes and quantifier review;
- axiom report;
- theorem-registry entry;
- independent statistical review.

Proof completion does not compensate for an incorrect statement.

## Generated code

Generated files must state their generator and source. Edit the source or generator, not the output. Generated frontend bindings must be checked against shared conformance fixtures.

## Authorship and credit

See `docs/governance/authorship-and-credit.md`. Formalizing an existing result does not transfer authorship of that result. Cite original sources and credit formalization, review, benchmark, engineering, and maintenance work separately.
