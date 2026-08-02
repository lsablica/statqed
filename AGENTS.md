# StatQED Agent Map

This is the root instruction file. Keep it concise. Detailed rules live in the linked system-of-record documents. A nested `AGENTS.md` overrides or extends this file for its directory.

## Read first

1. `CHARTER.md`
2. `ARCHITECTURE.md`
3. `docs/design/core-beliefs.md`
4. `docs/design/trust-model.md`
5. the active plan in `docs/exec-plans/active/`
6. `work/backlog.yaml`
7. the nearest nested `AGENTS.md`

## Repository purpose

StatQED is a language-independent infrastructure for proof-carrying statistical analysis. Lean is the initial normative proof backend. Rust is the planned reference operational backend. R, Python, and Julia are thin frontends.

## Constitutional constraints

- Separate identification, inference, numerical correctness, provenance, and interpretation.
- Never label an external assumption as kernel-verified.
- Never infer a model assumption from a diagnostic without a theorem that licenses the inference.
- Never change a frozen theorem signature or add a hypothesis to make a proof pass.
- Never add project axioms or leave `sorry` in a trusted release path.
- Treat R, Python, Julia, solvers, BLAS/LAPACK, report generators, and agents as untrusted producers.
- Use exact values or explicit numeric representations; do not treat decimal text or binary floats as exact reals.
- State every probability source and quantifier scope.
- Preserve original-source attribution and source anchors.
- Prefer contributing general mathematics upstream to Mathlib.

## Work protocol

- Select only a dependency-ready task from `work/backlog.yaml`.
- Create a task contract from `agents/templates/task.yaml`.
- Stay within contracted files.
- Use an RFC for unresolved core semantics.
- Keep execution-plan sections current.
- Add tests before claiming completion.
- Run `make check`.
- Produce a handoff using `agents/templates/handoff.md`.
- Update `work/status.yaml`.

## Required independent review

Changes affecting any of these require distinct author and reviewer roles:

- public definitions;
- theorem statements;
- assumption sets;
- guarantee classes;
- evidence types;
- artifact semantics;
- checker soundness;
- canonicalization;
- trusted computing base.

Use the protocols in `agents/protocols/`.

## Source of truth

| Subject | Source |
|---|---|
| Mission and non-goals | `CHARTER.md` |
| Architecture | `ARCHITECTURE.md`, accepted ADRs |
| Scientific principles | `docs/design/core-beliefs.md` |
| Trust boundary | `docs/design/trust-model.md` |
| Current execution | `docs/exec-plans/active/` |
| Task dependencies | `work/backlog.yaml` |
| Method contract | `docs/design/method-packs.md` |
| IR | `docs/spec/ir.md` |
| Artifact | `docs/spec/artifact.md` |
| Assurance graph | `docs/spec/assurance-graph.md` |
| Review gates | `agents/protocols/merge-gates.md` |

## Commands

```bash
make check       # repository guardrails
make list-work   # summarize task ledger
```

Language-specific build commands are added by the bootstrap tasks and must then be documented in the nearest nested `AGENTS.md`.

## Status language

Use only: Draft, Experimental, Candidate, Stable, Archived.

Do not describe a planned component as implemented. Do not describe replay as verification. Do not describe numerical certification as identification or scientific validity.
