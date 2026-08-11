# Start Here: Manager-Agent Launch Contract

This file is the entry point for a coding agent that coordinates specialist
subagents.

StatQED is architecture-first and dependency-driven. Never select work from an
old prompt, remembered conversation, or a task number embedded in prose. Derive
the eligible set from the checked repository ledger at the beginning and end of
every execution.

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

At the reviewed post-SQ-0006 state, **SQ-0007, SQ-0008, SQ-0011, SQ-0013,
SQ-0014, and SQ-0015 are READY**, no task is active, and SQ-0008 remains
unstarted. The permanent SQ-0006 verifier now preserves the exact completion
manifest as historical evidence while allowing independently reviewed
successor planning and path-granular task ownership. The next operation is a
planning-only expansion of the still-READY SQ-0007 contract; do not claim
SQ-0007 until that contract is independently reviewed and merged. RFC-0001 and
ADR-0004 remain Accepted for the
bounded data-free encoding profile. RFC-0006 remains Draft under SQ-0027
ownership. The SQ-0005 prototypes and SQ-0006 schema evidence have no
production canonicalizer authority.

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
13. agents/protocols/task-contract.md
14. agents/protocols/source-lineage.md
15. agents/protocols/semantic-audit.md
16. agents/protocols/merge-gates.md
17. agents/protocols/handoff.md
18. the nearest nested AGENTS.md before changing any scoped file.

Do not claim a dependency-ready implementation task at the current reviewed
state. First expand SQ-0007 into a complete executable contract on an isolated
planning branch, obtain independent planning/formal/evidence/integration
review, and merge that planning-only change. Leave all six READY tasks READY
and unstarted, including SQ-0008.

Non-negotiable constraints:
- Treat public statistical meanings, normative encodings, and theorem
  statements as governed interfaces.
- Do not strengthen assumptions, weaken conclusions, change a frozen
  signature, or add an axiom to complete a task.
- Do not describe external assumptions as proved by Lean.
- Keep identification, inference, numerical correctness, provenance/data
  binding, serialization, and interpretation separate.
- Keep solvers, frontends, report generators, prototypes, and AI agents outside
  a verification mode's trusted base unless their unchecked output is
  explicitly admitted into that mode's reported TCB.
- Use small, reviewable changes and keep the default branch green.
- Update the active plan's Progress, Decision Log, Surprises & Discoveries, and
  Outcomes sections as work proceeds.
- Update work/backlog.yaml and work/status.yaml only through reviewed task-state
  transitions.
- Preserve exact toolchain, dependency, command, environment, source, vector,
  and failure evidence.
- Run every applicable quality gate before handoff.
- If a core semantic or trust-boundary choice is unresolved, stop the affected
  work, mark it BLOCKED, and use the assigned RFC owner rather than improvising.
- Never claim functionality represented only by a plan, Draft RFC, prototype,
  lock resolution, digest match, or unexecuted command.

For an implementation task after that maintenance is merged:
1. Confirm dependency and decision-prerequisite evidence.
2. Update the task contract and ledger atomically from READY to IN_PROGRESS.
3. Create one isolated branch or worktree.
4. Assign source, implementation, independent-oracle, adversarial, semantic,
   security, and integration roles before implementation.
5. Implement only contract-authorized files.
6. Preserve failures, implementation disagreements, and contradictory evidence.
7. Add the positive, negative, mutation, differential, resource, clean-build,
   security, and trust-boundary tests required by the contract.
8. Produce source audits, review records, and exact command transcripts.
9. Run merge gates from a clean repository state.
10. Update plan, backlog, status, review, handoff, and readiness-only successor
    contract records atomically with the final task transition.
11. Merge only after independent integration approval.
12. Recompute the next READY set after merge.

Do not attempt the full roadmap, combine successors, or begin SQ-0007 before
its executable planning contract is reviewed and merged.
```

## Current manager action: expand SQ-0007 planning only

SQ-0006 is merged and DONE. It established only the Experimental, closed,
data-free `statqed.foundation-structural.v0` fixture schema, its independently
compared canonical bytes, and conditional fixture digests. It did not create a
general statistical IR, logical-data identity, artifact envelope, theorem
registry, production canonicalizer, certificate, or statistical-validity
claim.

The permanent SQ-0006 evidence uses an explicit v2 historical/live model. It
retains the complete v1 completion manifest and every successor-contract hash
observed at completion, but it no longer compares future reviewed planning
prose with those historical values. Static path partitions keep unrelated
Lean, Rust, frontend, prototype, schema, and golden subtrees frozen until an
explicit owner is active. This maintenance changed no schema scientific
subject and claimed no successor.

Before SQ-0007 is claimed, expand only its contract on
`planning/SQ-0007-executable-contract`. Keep its status READY, preserve the
other five successor contracts and states, and require independent planning,
formal/trust-boundary, evidence-lifecycle, and integration approval. Do not
regenerate SQ-0006 evidence merely because SQ-0007 planning prose changes.

The checked READY set is:

- SQ-0007 — expected next scientific task after maintenance;
- SQ-0008 — independently READY and unstarted;
- SQ-0011;
- SQ-0013;
- SQ-0014; and
- SQ-0015.

RFC-0001 and ADR-0004 remain Accepted. RFC-0006 remains unchanged, Draft, and
owned by SQ-0027. No maintenance may use this planning boundary to change any
of those decisions or the reviewed schema-v0 subject.

## Expected execution pattern

```text
manager
  ├─ evidence-lifecycle reviewer
  ├─ successor-contract planning reviewer
  ├─ adversarial regression reviewer
  └─ independent integration reviewer
```

The maintenance author must not be the sole evidence, planning, adversarial,
or integration reviewer.

## Branch and worktree policy

Use one task per isolated branch or worktree:

Use one isolated branch for the SQ-0007 planning contract. Create no successor
implementation branch until that planning change is integrated and the full
checked ledger remains green. Golden bytes and the Experimental schema retain
only their reviewed structural authority.

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
