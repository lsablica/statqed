# Start Here: Manager-Agent Launch Contract

This file is the entry point for a coding agent that coordinates specialist subagents.

StatQED is architecture-first and dependency-driven. Do not begin by generating broad implementation code. At the start of every run, derive the current task from the repository ledger rather than from an old prompt or remembered conversation.

## Mandatory preflight

From the repository root:

```bash
make check
make list-work
```

Then read `work/status.yaml` and `work/backlog.yaml`. Select only a task that is reported as dependency-ready and whose decision prerequisites are satisfied. If these sources disagree, stop and repair the ledger through an independently reviewed planning change.

At the reviewed post-SQ-0001 state on 2026-08-03, the sole dependency-ready task is **SQ-0002: Research and pin compatible toolchains**. Future agents must still recompute the ready set rather than assuming SQ-0002 remains current.

## Copy-paste manager prompt

```text
You are the implementation manager for StatQED.

First run:
  make check
  make list-work

Read, in order:
1. AGENTS.md
2. CHARTER.md
3. ARCHITECTURE.md
4. docs/design/core-beliefs.md
5. docs/design/trust-model.md
6. docs/exec-plans/README.md
7. docs/exec-plans/active/0001-foundation-bootstrap.md
8. work/README.md
9. work/backlog.yaml
10. work/status.yaml
11. the contract for the sole dependency-ready task
12. the previous completed task's handoff and review records
13. agents/protocols/task-contract.md
14. agents/protocols/merge-gates.md
15. the nearest nested AGENTS.md before changing any scoped file.

Your objective is to execute exactly the dependency-ready work reported by the repository ledger. At the current reviewed state, begin with SQ-0002 and follow work/contracts/SQ-0002.yaml. Do not begin SQ-0003, SQ-0004, or any later task during the SQ-0002 branch.

Non-negotiable constraints:
- Treat public statistical meanings and theorem statements as governed interfaces.
- Do not strengthen assumptions, weaken conclusions, change a frozen signature, or add an axiom to complete a task.
- Do not describe external assumptions as proved by Lean.
- Keep identification, inference, numerical correctness, provenance/data binding, and interpretation separate.
- Keep solvers, frontends, report generators, and AI agents outside a verification mode's trusted base unless their unchecked output is explicitly admitted into that mode's reported TCB.
- Use small, reviewable changes and keep the default branch green.
- Update the active execution plan's Progress, Decision Log, Surprises & Discoveries, and Outcomes sections as work proceeds.
- Update work/backlog.yaml and work/status.yaml only through the task's reviewed integration transition.
- Run all applicable quality gates before handoff.
- If a core semantic choice is unresolved, stop the affected work, mark it BLOCKED, and use the assigned RFC owner rather than improvising.
- Never claim functionality represented only by a plan, Draft RFC, prototype, or unexecuted command.

For each task:
1. Confirm dependency and decision-prerequisite evidence.
2. Instantiate or update the task contract within its allowed scope.
3. Create one isolated branch or worktree.
4. Assign source, implementation, adversarial, specialist, and integration roles before implementation.
5. Implement only contracted files.
6. Preserve failed prototypes and contradictory evidence.
7. Add the positive, negative, malformed, corruption, conformance, security, and overclaim tests required by the task.
8. Produce source/review records and an exact command transcript.
9. Run merge gates from a clean repository state.
10. Update plan, backlog, status, review, and handoff records atomically with the task transition.
11. Merge only after independent integration approval.
12. Recompute the next dependency-ready set after merge.

Do not attempt the full roadmap in one run. Complete the active task and its integration evidence before proceeding.
```

## Current manager action: SQ-0002

SQ-0001 is complete and merged. Its accepted decisions, explicit deferrals, source audit, review record, and handoff are the baseline for SQ-0002.

Read:

```text
work/contracts/SQ-0002.yaml
work/handoffs/SQ-0001.md
work/reviews/SQ-0001.md
docs/research/SQ-0001-constitutional-source-audit.md
```

SQ-0002 is a **research-and-pin proposal**, not a toolchain-bootstrap task. It must:

- identify current official compatibility constraints on the execution date;
- reproduce tiny, isolated prototypes under the task's research paths;
- distinguish the proposed development/reference pin from minimum supported versions and the future CI matrix;
- evaluate Lean/Mathlib/Lake, Rust, Python, R, Julia, Arrow, CBOR/CDDL tooling, supported platforms, caching, licensing, maintenance, and supply-chain considerations;
- retain failed combinations and rejected alternatives;
- provide exact commands, versions, environment details, and evidence for every recommendation;
- leave real repository lock files and production package skeletons untouched.

SQ-0002 must not:

- initialize `lean/`, `backend/`, or any frontend package;
- write production `lean-toolchain`, `lakefile.toml`, `rust-toolchain.toml`, package manifests, or lock files;
- accept RFC-0001 or choose normative serialization merely because a candidate library works;
- freeze theorem identity, artifact, data-digest, statistical ontology, or frontend semantics;
- make package-publication or platform-support claims without direct evidence.

Real Lean and Rust bootstrap work begins only after SQ-0002 is integrated, through SQ-0003 and SQ-0004 respectively.

## Expected execution pattern

```text
manager
  ├─ source curator
  ├─ Lean/Mathlib compatibility specialist
  ├─ Rust/tooling specialist
  ├─ R/Python/Julia compatibility specialists
  ├─ interoperability and licensing reviewer
  ├─ release/security adversarial reviewer
  └─ integration reviewer
```

The author of a recommendation must not be its only reviewer. Unsupported platform or package claims are recorded as unknown, not inferred from a different platform.

## Branch and worktree policy

Use one task per branch or isolated worktree:

```text
agent/SQ-0002-toolchain-research
agent/SQ-0003-lean-bootstrap
agent/SQ-0004-rust-bootstrap
```

Prefer pull requests small enough for line-by-line review. A task may have several commits, but the default branch must remain green. Experimental files belong only in contract-authorized prototype paths.

## What “foundation complete” means

The foundation is complete only when:

- Lean and Rust projects build from clean, pinned environments;
- an Accepted RFC-0001 profile governs the data-free fixture's canonical encoding and reviewed vectors;
- R, Python, and Julia construct the same ADR-0011 `foundation_structural` semantic fixture;
- the Rust reference backend produces byte-identical accepted canonical bytes and domain-separated fixture digests;
- theorem/environment/proof/authorization locks follow an Accepted RFC-0005 design;
- any artifact-level kernel result uses the Accepted RFC-0003 byte-to-term path and reports its actual TCB and axiom baseline;
- the assurance graph and trust report expose every unresolved or external leaf without evidence union;
- CI enforces language builds, conformance, malformed-input tests, source-audit presence, trusted-path restrictions, and clean-checkout reproduction;
- documentation states exactly what is and is not checked.

Until SQ-0020 completes the independent foundation review, the project remains Draft/pre-alpha and must make no general “verified statistics” claim.
