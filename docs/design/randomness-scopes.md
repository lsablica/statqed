# Randomness Scopes

Status: **Draft; public ontology blocked on RFC-0004**.

Probability statements must name what is random and what is fixed.

Research catalogue (not a flat public enumeration):

- `sampling`: observations drawn from a population/model;
- `assignment`: treatment or exposure assigned by a design;
- `finite_population`: potential outcomes fixed, assignment random;
- `resampling`: bootstrap/permutation randomness conditional on observed data;
- `monte_carlo`: finite simulation used to approximate a deterministic target;
- `algorithmic`: ideal randomized algorithm;
- `sequential`: filtration-indexed process and stopping rule;
- `posterior`: uncertainty under a Bayesian model;
- `measurement`: explicit measurement-error mechanism;
- `privacy`: randomness introduced by a privacy mechanism.

These entries mix sources, regimes, computational purposes, temporal/index structures, and interpretations. RFC-0004 must separate those dimensions and define laws, fixed objects, conditioning, nesting/coupling, and quantifier scope before SQ-0008 freezes a public type. For example, a Monte Carlo approximation to an assignment-randomization p-value has two distinct probability contexts. Frontends may not collapse them into a generic `probability` field.
