# Start Here: Manager-Agent Launch Contract

This file is the entry point for a coding agent that coordinates specialist
subagents.

StatQED is architecture-first and dependency-driven. Never select work from an
old prompt, remembered conversation, or task number embedded in documentation.
Derive the eligible set from the checked repository ledger at the beginning and
end of every execution.

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
- its detailed contract authorizes every intended file; and
- the repository is clean or pre-existing differences are explicitly outside
  the task and independently reviewed.

If the guardrail output, backlog, status ledger, contract, or plan disagree,
stop. Repair the planning state through an independently reviewed planning
change before implementation.

At the reviewed post-SQ-0003 state, **SQ-0004 and SQ-0008 are both READY**.
The recommended next isolated execution is **SQ-0004: Bootstrap Rust reference
workspace** because it completes Milestone B's second language foundation and
unlocks the SQ-0005 serialization research task. SQ-0008 remains READY and
unstarted; do not execute it in the SQ-0004 branch.

## Copy-paste manager contract

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

Execute exactly one dependency-ready task in one isolated branch or worktree.
At the current reviewed state, select SQ-0004 and follow
work/contracts/SQ-0004.yaml. Leave SQ-0008 READY and unstarted.

Non-negotiable constraints:
- Treat public statistical meanings and theorem statements as governed interfaces.
- Do not strengthen assumptions, weaken conclusions, change a frozen signature,
  or add an axiom to complete a task.
- Do not describe external assumptions as proved by Lean.
- Keep identification, inference, numerical correctness, provenance/data
  binding, and interpretation separate.
- Keep solvers, frontends, report generators, and AI agents outside a
  verification mode's trusted base unless their unchecked output is explicitly
  admitted into that mode's reported TCB.
- Use small, reviewable changes and keep the default branch green.
- Update the active plan's Progress, Decision Log, Surprises & Discoveries, and
  Outcomes sections as work proceeds.
- Update work/backlog.yaml and work/status.yaml only through reviewed task-state
  transitions.
- Preserve exact toolchain, dependency, command, environment, and failure
  evidence.
- Run every applicable quality gate before handoff.
- If a core semantic or trust-boundary choice is unresolved, stop the affected
  work, mark it BLOCKED, and use the assigned RFC owner rather than improvising.
- Never claim functionality represented only by a plan, Draft RFC, prototype,
  lock resolution, or unexecuted command.

For the selected task:
1. Confirm dependency and decision-prerequisite evidence.
2. Update the task contract and ledger atomically from READY to IN_PROGRESS.
3. Create one isolated branch or worktree.
4. Assign source, implementation, adversarial, specialist, and integration
   roles before implementation.
5. Implement only contract-authorized files.
6. Preserve failures and contradictory evidence.
7. Add the positive, negative, mutation, clean-build, security, and
   trust-boundary tests required by the contract.
8. Produce review records and an exact command transcript.
9. Run merge gates from a clean repository state.
10. Update plan, backlog, status, review, handoff, and any readiness-only
    successor contract records atomically with the final task transition.
11. Merge only after independent integration approval.
12. Recompute the next READY set after merge.

Do not attempt the full roadmap or combine SQ-0004 and SQ-0008 in one branch.
```

## Current manager action: SQ-0004

SQ-0002 established reviewed toolchain recommendations. SQ-0003 subsequently
created the Experimental Lean proof foundation. Their results are prerequisites
and constraints, not permission to invent Rust-side statistical or artifact
semantics.

Read:

```text
work/contracts/SQ-0004.yaml
work/handoffs/SQ-0002.md
work/reviews/SQ-0002.md
work/handoffs/SQ-0003.md
work/reviews/SQ-0003.md
work/handoffs/SQ-0003-post-merge.md
work/reviews/SQ-0003-post-merge.md
docs/implementation/toolchain-compatibility.md
docs/research/toolchain-prototypes/rust/README.md
backend/AGENTS.md
docs/implementation/rust-backend.md
```

SQ-0004 must use the reviewed Rust policy unless a directly reproduced blocker
is found:

```text
Development/build/acquisition toolchain: Rust 1.97.1
Compatibility-only compiler/API floor: Rust 1.85.1
Edition: 2024
Cargo resolver: 3
Project rust-version: 1.85.1
```

Rust 1.85.1 is not an approved networked acquisition or release tool. Current
Cargo acquires the exact dependency graph into a clean, credential-free,
crates.io-only environment; the floor validates the committed lock offline.

The task establishes only a minimal operational-backend workspace, deterministic
version/error CLI surface, exact dependency lock, safe-code policy, build/test
surface, dependency/license/advisory evidence, and Rust-specific CI. It does
not create statistical IR, canonical encoding, artifact, theorem-registry,
certificate, frontend, or method-pack semantics.

SQ-0004 must:

- initialize the production Rust workspace under `backend/` with the exact
  reviewed development pin and compatibility floor;
- keep the workspace minimal rather than generating speculative future crates;
- use Edition 2024, resolver 3, `rust-version = "1.85.1"`, and
  `unsafe_code = "forbid"` for all project targets;
- generate one exact `Cargo.lock` using current Cargo in a clean acquisition
  environment;
- run the same lock under Rust 1.85.1 with `--locked --offline`;
- implement only deterministic version/build metadata and a machine-readable
  error envelope for malformed or unsupported CLI input;
- add formatting, Clippy, tests, panic-resistance, unsafe, lock, registry,
  credential, determinism, license, advisory, and CI gates;
- document exact trust boundaries, update/rollback instructions, and nonclaims;
- obtain distinct source, Rust/workspace, API/error, security/adversarial,
  CI/reproducibility, and integration reviews.

SQ-0004 must not:

- modify the Lean project or its workflow;
- begin or modify SQ-0008;
- accept any Draft RFC;
- implement an IR, schema, canonicalizer, digest, archive, theorem registry,
  certificate checker, frontend binding, or statistical object;
- use Rust 1.85.1 for general networked acquisition;
- claim non-Linux or other unexecuted compatibility;
- begin SQ-0005 after its readiness-only transition.

## Expected execution pattern

```text
manager
  ├─ Rust/source curator
  ├─ workspace and MSRV engineer
  ├─ API/error-conformance reviewer
  ├─ security and malformed-input reviewer
  ├─ CI/reproducibility reviewer
  └─ integration reviewer
```

The implementation author must not be the only API, security, CI, or
integration reviewer.

## Branch and worktree policy

Use one task per isolated branch or worktree:

```text
agent/SQ-0004-rust-bootstrap
agent/SQ-0008-core-ontology
```

The default branch remains green. Experimental scratch work stays outside
production paths unless the contract explicitly permits it.

## What “foundation complete” means

The foundation is complete only when:

- Lean and Rust projects build from clean, pinned environments;
- an Accepted RFC-0001 profile governs the data-free fixture's canonical
  encoding and reviewed vectors;
- R, Python, and Julia construct the same ADR-0011 `foundation_structural`
  semantic fixture;
- the Rust reference backend produces byte-identical accepted canonical bytes
  and domain-separated fixture digests;
- theorem/environment/proof/authorization locks follow an Accepted RFC-0005
  design;
- any artifact-level kernel result uses the Accepted RFC-0003 byte-to-term path
  and reports its actual TCB and axiom baseline;
- the assurance graph and trust report expose every unresolved or external leaf
  without evidence union;
- CI enforces language builds, conformance, malformed-input tests, source-audit
  presence, trusted-path restrictions, and clean-checkout reproduction; and
- documentation states exactly what is and is not checked.

Until SQ-0020 completes the independent foundation review, the project remains
Draft/pre-alpha and makes no general “verified statistics” claim.
