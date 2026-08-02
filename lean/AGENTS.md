# Lean Scope Instructions

Scope: `lean/**`.

Read `docs/implementation/lean-core.md`, theorem/source protocols, and the active task contract.

- Search pinned Mathlib first.
- Public definitions/statements require reviewed source records and frozen hashes.
- Proof executors cannot change frozen signatures.
- No `sorry`, `admit`, project axiom, or unreviewed unsafe shortcut in trusted paths.
- Keep imports narrow and bridge abstract/computable concepts explicitly.
- Run build, tests, examples, lints, and axiom report.
- General mathematics should be prepared for upstream contribution.
