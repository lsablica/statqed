# Theorem Registry Design

The registry makes formal results discoverable, citable, reviewable, and lockable.

Each public theorem records:

- stable ID and version;
- Lean declaration and normalized statement hash;
- maturity and proof-backend lock;
- claim class and randomness scopes;
- quantifier/conditioning profile;
- assumptions and conclusion;
- primary source anchors;
- source, statistical, and formal reviews;
- non-vacuity models and ablation tests;
- examples and counterexamples;
- predecessor/successor implication or equivalence relations;
- original-source and formalization citations.

Changing a proof body need not change the statement hash. Changing statement meaning creates a new version and compatibility record.
