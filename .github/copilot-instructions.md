# GitHub Copilot instructions for StatQED

Read root `AGENTS.md`, then the nearest nested `AGENTS.md`.

StatQED is a language-independent proof-carrying statistical-analysis infrastructure. Lean is the normative proof backend; Rust is the reference operational backend; R/Python/Julia are thin frontends.

Do not:

- conflate identification, inference, numerics, provenance, or interpretation;
- call external assumptions kernel-verified;
- add hypotheses or change frozen theorem statements;
- introduce project axioms or trusted-path `sorry`;
- define normative semantics only in a frontend or Rust;
- silently coerce floats to exact reals;
- update golden vectors merely because implementation changed;
- claim planned components are implemented.

Use dependency-ready tasks from `work/backlog.yaml`, active plans, task contracts, independent reviews, and `make check`.
