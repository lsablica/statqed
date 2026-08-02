# Continuous Integration Design

Foundation CI stages:

- repository/documentation/task-ledger guardrails;
- formatting and linting per language;
- schema parse and golden vectors;
- Rust unit/property/fuzz-smoke tests;
- Lean build, examples, and axiom report;
- R CMD check, Python tests/type checks, Julia tests;
- cross-language conformance;
- artifact structural/kernel verification;
- trusted-path and dependency audit;
- clean-checkout reproducibility.

Required status checks are enabled only after their toolchains exist; until then `repository-guardrails` prevents false completion claims.
