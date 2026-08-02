# Randomness Scopes

Probability statements must name what is random and what is fixed.

Initial scope taxonomy:

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

A claim records conditioning and nested scopes. For example, a Monte Carlo approximation to an assignment-randomization p-value has two distinct probability layers. Frontends may not collapse them into a generic `probability` field.
