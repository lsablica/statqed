# Semantic Audit Protocol

## Purpose

Detect definitions and statements that are formally provable but statistically wrong, vacuous, irrelevant, or misleading.

## Audit passes

### Meaning

Restate the object/claim without Lean notation. Identify estimand, procedure, guarantee, and interpretation.

### Quantifiers

List quantifier order, pointwise/uniform scope, conditioning, and finite/asymptotic regime.

### Randomness

Name every source of probability and what is held fixed.

### Hypotheses

Classify by source lineage and empirical/formal status.

### Non-vacuity

Produce a nontrivial model satisfying all premises. Check that the conclusion is not true only because the premise is impossible or definition degenerate.

### Ablation

Remove or weaken material premises and search for counterexamples.

### Mutation

Change tail, inequality, conditioning, quantifier, randomness, or target and verify that review/tests detect the difference.

### Interpretation

List allowed and prohibited prose conclusions.

## Outcome codes

- `APPROVE`
- `APPROVE_WITH_LIMITATIONS`
- `REVISE`
- `BLOCK_SOURCE_CONFLICT`
- `BLOCK_VACUITY`
- `BLOCK_OVERCLAIM`
- `BLOCK_UNSUPPORTED_HYPOTHESIS`

An approval names the exact statement hash or schema digest reviewed.
