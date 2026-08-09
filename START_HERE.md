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

At the reviewed post-SQ-0005 state, **SQ-0006 and SQ-0008 are both READY**.
The recommended next isolated execution is **SQ-0006: Define schema v0 and
golden vectors**. SQ-0008 remains independently READY and unstarted; do not
combine schema and ontology work in one branch. RFC-0001 and ADR-0004 are
Accepted for the bounded data-free encoding profile. RFC-0006 remains Draft
under SQ-0027 ownership, and the SQ-0005 prototypes have no production
canonicalizer authority.

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

Execute exactly one dependency-ready task in one isolated branch or worktree.
At the current reviewed state, select SQ-0006 and follow
work/contracts/SQ-0006.yaml. Leave SQ-0008 READY and unstarted.

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

For the selected task:
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

Do not attempt the full roadmap or combine SQ-0006 and SQ-0008 in one branch.
```

## Current manager action: SQ-0006

SQ-0005 accepted the bounded data-free `statqed.cbor-core.v1` encoding profile
and generic `statqed.digest-lp.v1` framing after independent differential and
adversarial review. Its Rust and Python implementations remain Experimental
prototypes without production canonicalizer authority. SQ-0006 must now define
only the versioned data-free schema and reviewed golden vectors for ADR-0011's
`foundation_structural` fixture.

Read:

```text
work/contracts/SQ-0006.yaml
work/handoffs/SQ-0005.md
work/reviews/SQ-0005.md
rfcs/0001-deterministic-encoding.md
rfcs/0006-canonical-logical-data-digest.md
docs/adr/0004-deterministic-cbor-cddl.md
docs/adr/0011-foundation-toy-slice.md
docs/spec/canonicalization.md
schemas/AGENTS.md
conformance/AGENTS.md
```

### Decision ownership

- RFC-0001 and ADR-0004 are Accepted and govern the bounded data-free encoding
  profile used by SQ-0006. SQ-0006 may not silently amend that profile.
- RFC-0006 is owned by SQ-0027 and remains Draft. SQ-0006 must not define a
  logical table, physical-to-logical lowering, canonical logical-data digest,
  or privacy property for data commitments.
- Artifact-envelope semantics remain outside schema v0 and belong to the later
  RFC-0008/SQ-0010 decision path.

### Required schema boundary

The task must use published CDDL syntax for versioned numeric/common/toy files.
Draft CDDL module/import syntax may be explored only at an exact pinned revision
and labeled Experimental; it cannot become a normative dependency.

The schema and fixture review must explicitly cover:

- exact ADR-0011 field names and their semantic prose;
- data-free numeric, identifier, and extension shapes allowed by RFC-0001;
- explicit feature and unknown-critical behavior;
- minimal and maximal valid fixtures;
- malformed, numeric, Unicode, and unknown-critical negative fixtures;
- stable error classes and schema-version/migration policy; and
- independent semantic review before canonical bytes or digests are accepted.

### Independent evidence

Every accepted field and example needs semantic review independent of the
encoder that emits its bytes. Golden output must agree across independently
reviewed semantics and implementations; it must never be accepted merely by
copying the SQ-0005 Rust prototype's output.

### Scope prohibitions

SQ-0006 must not:

- treat an SQ-0005 prototype as production authority;
- implement a logical table or RFC-0006 data-lowering/digest decision;
- implement an artifact envelope, theorem registry, certificate, frontend, or
  statistical type;
- treat CDDL validation as canonical-byte or semantic proof;
- treat a digest equality as collision-free identity proof;
- modify the Lean or production Rust foundations; or
- begin SQ-0008 or any successor after a readiness-only transition.

## Expected execution pattern

```text
manager
  ├─ schema/source curator
  ├─ ontology and field-semantics reviewer
  ├─ schema and fixture engineer
  ├─ independent conformance/vector reviewer
  ├─ adversarial malformed/extension reviewer
  └─ independent integration reviewer
```

The schema author must not be the sole semantic, conformance, security, or
integration reviewer.

## Branch and worktree policy

Use one task per isolated branch or worktree:

```text
agent/SQ-0006-schema-v0
agent/SQ-0008-core-ontology
```

The default branch remains green. SQ-0006 and SQ-0008 remain separate, and
golden bytes do not gain authority without the reviewed schema semantics.

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
