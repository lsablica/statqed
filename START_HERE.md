# Start Here: Manager-Agent Launch Contract

This file is the entry point for a coding agent that coordinates specialist subagents.

StatQED is architecture-first and dependency-driven. Never select work from an old prompt, remembered conversation, or task number embedded in documentation. Derive the current eligible set from the checked repository ledger at the beginning and end of every execution.

## Mandatory preflight

From the repository root:

```bash
git status --short
git rev-parse HEAD
make check
make list-work
git diff --check
```

Then read `work/status.yaml` and `work/backlog.yaml`. A task may begin only when:

- it is reported as `READY` by the shared readiness calculation;
- all task and decision prerequisites are satisfied;
- the active execution plan permits the work;
- its detailed contract authorizes every intended file;
- the repository is clean or the pre-existing differences are explicitly outside the task and reviewed.

If the guardrail output, backlog, status ledger, contract, or plan disagree, stop. Repair the planning state through an independently reviewed planning change before implementation.

At the reviewed post-SQ-0002 state, **SQ-0003 and SQ-0004 are both READY**. The recommended next isolated execution is **SQ-0003: Bootstrap Lean and Mathlib project** because it establishes the initial proof-backend build and trust-reporting surface. SQ-0004 remains READY and unstarted; do not execute it in the SQ-0003 branch.

## Copy-paste manager prompt

```text
You are the implementation manager for StatQED.

First run:
  git status --short
  git rev-parse HEAD
  make check
  make list-work
  git diff --check

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
11. the detailed contract for the selected READY task
12. the previous completed task's handoff and review records
13. docs/implementation/toolchain-compatibility.md when the task depends on SQ-0002
14. agents/protocols/task-contract.md
15. agents/protocols/source-lineage.md
16. agents/protocols/semantic-audit.md
17. agents/protocols/merge-gates.md
18. agents/protocols/handoff.md
19. the nearest nested AGENTS.md before changing any scoped file.

Execute exactly one dependency-ready task in one isolated branch or worktree. At the current reviewed state, select SQ-0003 and follow work/contracts/SQ-0003.yaml. Leave SQ-0004 READY and unstarted.

Non-negotiable constraints:
- Treat public statistical meanings and theorem statements as governed interfaces.
- Do not strengthen assumptions, weaken conclusions, change a frozen signature, or add an axiom to complete a task.
- Do not describe external assumptions as proved by Lean.
- Keep identification, inference, numerical correctness, provenance/data binding, and interpretation separate.
- Keep solvers, frontends, report generators, and AI agents outside a verification mode's trusted base unless their unchecked output is explicitly admitted into that mode's reported TCB.
- Use small, reviewable changes and keep the default branch green.
- Update the active execution plan's Progress, Decision Log, Surprises & Discoveries, and Outcomes sections as work proceeds.
- Update work/backlog.yaml and work/status.yaml only through reviewed task-state transitions.
- Preserve exact toolchain, dependency, command, environment, and failure evidence.
- Run all applicable quality gates before handoff.
- If a core semantic or trust-boundary choice is unresolved, stop the affected work, mark it BLOCKED, and use the assigned RFC owner rather than improvising.
- Never claim functionality represented only by a plan, Draft RFC, prototype, lock resolution, or unexecuted command.

For the selected task:
1. Confirm dependency and decision-prerequisite evidence.
2. Update the task contract and ledger atomically from READY to IN_PROGRESS.
3. Create one isolated branch or worktree.
4. Assign source, implementation, adversarial, specialist, and integration roles before implementation.
5. Implement only contract-authorized files.
6. Preserve failures and contradictory evidence.
7. Add the positive, negative, mutation, clean-build, security, and trust-boundary tests required by the contract.
8. Produce review records and an exact command transcript.
9. Run merge gates from a clean repository state.
10. Update plan, backlog, status, review, and handoff records atomically with the final task transition.
11. Merge only after independent integration approval.
12. Recompute the next READY set after merge.

Do not attempt the full roadmap or combine SQ-0003 and SQ-0004 in one branch.
```

## Current manager action: SQ-0003

SQ-0002 is complete. Its reviewed output is a compatibility recommendation and retained research evidence, not production toolchain initialization or normative statistical semantics.

Read:

```text
work/contracts/SQ-0003.yaml
work/handoffs/SQ-0002.md
work/reviews/SQ-0002.md
docs/implementation/toolchain-compatibility.md
docs/research/toolchain-prototypes/lean-mathlib/README.md
lean/AGENTS.md
docs/implementation/lean-core.md
```

SQ-0003 must use the reviewed exact Lean/Mathlib pair unless a directly reproduced blocker is found:

```text
Lean 4.32.2
Lean commit f3b06c705e6c85f5314019d5d3baab0fec5b580c
Mathlib commit 905b95818eb32af7874a58b427f50c1711a5e96c
Lake 5.0.0-src+f3b06c7
```

The task establishes only a minimal proof-backend project, reproducible dependency lock, build/test surface, actual axiom reporting, trusted-path checks, and Lean-specific CI. It does not create statistical ontology, artifact semantics, certificate checkers, theorem-registry semantics, or a public statistical theorem.

SQ-0003 must:

- initialize the production Lean project under `lean/` with the exact reviewed pair;
- preserve the normal and no-binary-cache build distinction;
- make the Mathlib revision immutable in the committed dependency lock;
- provide a minimal namespace, smoke import, project test/example, and deterministic commands;
- report actual transitive axioms for named checked declarations;
- reject `sorry`, `admit`, `sorryAx`, project-defined axioms, altered toolchains, altered Mathlib locks, and unreviewed native-trust shortcuts;
- add a least-privilege Lean workflow and clean-checkout reproduction;
- document precisely what the successful build and axiom report do and do not establish;
- obtain independent Mathlib/source, Lean/formal, adversarial trust, CI/release, and integration review.

SQ-0003 must not:

- modify Rust or frontend projects;
- add statistical definitions or inference theorems;
- accept RFC-0002, RFC-0003, RFC-0004, or RFC-0005;
- describe a smoke theorem as a public StatQED theorem or non-vacuity witness;
- treat the ordinary Mathlib axiom baseline as permission to introduce new axioms;
- claim artifact-level kernel verification;
- begin SQ-0004 or any later task.

## Expected execution pattern

```text
manager
  ├─ source/Mathlib scout
  ├─ Lean build engineer
  ├─ formal trust and axiom reviewer
  ├─ adversarial mutation reviewer
  ├─ CI/reproducibility reviewer
  └─ integration reviewer
```

The implementation author must not be the only formal or integration reviewer.

## Branch and worktree policy

Use one task per isolated branch or worktree:

```text
agent/SQ-0003-lean-bootstrap
agent/SQ-0004-rust-bootstrap
```

The current execution uses `agent/SQ-0003-lean-bootstrap`. Experimental scratch work stays outside production paths unless the contract explicitly permits it. The default branch remains green.

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

Until SQ-0020 completes the independent foundation review, the project remains Draft/pre-alpha and makes no general “verified statistics” claim.
