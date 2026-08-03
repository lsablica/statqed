# Plan 0002: Exact Randomization Inference Vertical Slice

- Status: Active but blocked by SQ-0020
- Backlog: SQ-0021 through SQ-0036
- Objective: produce the first scientifically meaningful, finite-sample, end-to-end StatQED method pack.

## Observable exit condition

An R, Python, or Julia user can declare a finite randomized experiment, compute an exact or validity-preserving Monte Carlo randomization test, and emit a `.statqed` artifact. Independent verification establishes the exact count/numeric fact and instantiates a Lean theorem giving the advertised assignment-randomization guarantee conditional on explicitly displayed design/null assumptions. Bonferroni/Holm claims and confidence-set inversion are supported for the selected scope.

## Non-goals

- proving that randomization was physically followed;
- arbitrary permutation tests without precise invariance assumptions;
- observational causal identification;
- unrestricted test statistics or adaptive analyses;
- hiding finite Monte Carlo corrections.

## Milestone A — Sources and finite design semantics (SQ-0021–SQ-0025)

1. Curate primary sources for complete/block randomization, sharp-null randomization tests, p-value conventions, ties, two-sided definitions, Monte Carlo corrections, and interval inversion.
2. Define finite units, assignments, admissible assignment sets/distributions, observed assignment, potential outcomes or sharp-null outcome transformation, statistic, tail order, and p-value.
3. Distinguish assignment randomness from Monte Carlo randomness.
4. Exhaust small finite examples and counterexamples for wrong denominators, omitted observed assignment, random tie breaking, and data-dependent statistics.
5. Draft the super-uniformity theorem, audit every premise, and freeze the statement.

## Milestone B — Formal validity (SQ-0026)

Prove the frozen theorem using finite probability/combinatorics and upstream general lemmas where appropriate. Add exact enumerated examples, boundary alpha values, theorem mutations, and axiom report. Register the theorem with original-source citations and nonclaims.

## Milestone C — Exact witness/checker (SQ-0027–SQ-0029)

Before introducing any normative real-data field, digest, or backend path, SQ-0027 must source-audit and Accept RFC-0006's logical-data object, physical lowering, exact numeric/missingness/categorical semantics, canonical digest domain/profile, privacy limits, and resource rules. Foundation tasks remain deliberately data-free.

Witness content:

- canonical design/assignment-set digest;
- observed assignment and outcome/statistic binding;
- tail/tie convention;
- extreme count and total count;
- optional enumeration/dynamic-program trace;
- exact rational p-value;
- resource metadata.

Checker validates bindings, counts, rational construction, and any trace. Corruption tests alter assignments, count, denominator, tail, outcome digest, statistic ID, and theorem lock. Lean proves checker acceptance implies the numeric fact used by the inferential theorem.

## Milestone D — Confidence inversion and multiplicity (SQ-0030–SQ-0032)

- Define a restricted invertible family and exact confidence set.
- Formalize Bonferroni with minimal dependence assumptions.
- Formalize Holm step-down with sorted p-value witness and family definition.
- Expose family/endpoint choices as external scientific declarations rather than inferred semantics.

## Milestone E — Frontends (SQ-0033–SQ-0035)

Each frontend supplies typed native constructors, exact integer/rational handling, a certificate producer, report renderer, provenance, and shared fixtures. Frontends must produce the same IR and certificate for the canonical examples. Unsupported custom code enters opaque mode.

## Milestone F — Publication exemplar (SQ-0036)

Create a self-contained simulated randomized trial with blocked assignment, one primary and one secondary endpoint, exact test, Holm adjustment, confidence-set inversion where supported, deliberate corruptions, and an assumption ledger.

Outputs:

- reproducible scripts in all three languages;
- byte-identical canonical semantic objects;
- artifact carrying a named mode-specific verification result and trust report;
- human-readable methods narrative;
- benchmark items derived from failures;
- draft software/formalization paper case study.

## Required reviews

Source curator, design-based inference statistician, Lean reviewer, certificate/conformance reviewer, counterexample reviewer, security reviewer for artifact handling, integrator.

## Progress

- [ ] Blocked by foundation review.

## Surprises & Discoveries

- None recorded.

## Decision Log

- Exact finite design-based inference is the first method because the randomness and certificate boundaries are unusually explicit.

## Outcomes & Retrospective

To be completed at SQ-0036.
