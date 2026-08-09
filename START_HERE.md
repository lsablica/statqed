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

At the reviewed post-SQ-0004 state, **SQ-0005 and SQ-0008 are both READY**.
The recommended next isolated execution is **SQ-0005: Prototype deterministic
serialization**. It owns RFC-0001 and is the dependency gate for schema v0,
canonical backend work, theorem locks, artifacts, and the language frontends.
SQ-0008 remains independently READY and unstarted; do not combine ontology and
encoding work in one branch.

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
At the current reviewed state, select SQ-0005 and follow
work/contracts/SQ-0005.yaml. Leave SQ-0008 READY and unstarted.

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

Do not attempt the full roadmap or combine SQ-0005 and SQ-0008 in one branch.
```

## Current manager action: SQ-0005

SQ-0002 established current serialization-library compatibility observations.
SQ-0004 established only a minimal dependency-free Rust operational workspace.
Neither task selected a normative encoding profile. SQ-0005 must decide the
smallest defensible data-free encoding profile through source-grounded,
independently reproduced evidence.

Read:

```text
work/contracts/SQ-0005.yaml
work/handoffs/SQ-0002.md
work/reviews/SQ-0002.md
work/handoffs/SQ-0004.md
work/reviews/SQ-0004.md
rfcs/0001-deterministic-encoding.md
rfcs/0006-canonical-logical-data-digest.md
docs/adr/0004-deterministic-cbor-cddl.md
docs/spec/canonicalization.md
docs/research/toolchain-prototypes/arrow/README.md
docs/research/toolchain-prototypes/cbor-cddl/README.md
schemas/AGENTS.md
conformance/AGENTS.md
```

### Decision ownership

- SQ-0005 owns RFC-0001. It cannot transition to `DONE` while RFC-0001 remains
  Draft. If the evidence is insufficient, leave SQ-0005 active or blocked and
  record the exact missing decision rather than forcing acceptance.
- RFC-0006 is owned by SQ-0027. It is read-only in SQ-0005. SQ-0005 may record
  generic atom, framing, and cross-domain requirements needed by later logical
  data work, but it must not define a logical table, physical-to-logical
  lowering, or canonical logical-data digest.
- ADR-0004 may become Accepted only after RFC-0001 is Accepted and the ADR text
  precisely matches the selected profile and evidence.

### Required research boundary

The task must use current primary standards and registries, including RFC 8949,
RFC 8610 and its published extensions/updates, applicable errata, the IANA CBOR
tag registry, and the pinned Unicode normalization specification chosen by the
profile. CDDL module/import syntax remains work in progress and may be used only
as an explicitly pinned Experimental input, not silently as an RFC feature.

The selected profile must explicitly settle or exclude:

- core versus length-first deterministic map ordering;
- preferred integer, length, tag, and floating-point serialization;
- finite floats, infinities, signed zero, NaN payloads, and whether floats are
  permitted at all in each initial atom class;
- integer, bignum, decimal-fraction, rational, byte-string, text-string, array,
  map, boolean, null, interval, and extension representations;
- map-key type restrictions and duplicate-key equivalence before native-map
  collapse;
- invalid UTF-8 and Unicode normalization/preservation policy;
- tag allowlist, unknown tag behavior, and critical/noncritical extensions;
- strict rejection versus accepted normalization for non-profile but decodable
  CBOR;
- exact profile/schema identifiers and failure classes;
- maximum nesting, items, map entries, string/byte lengths, total input/output,
  and integer/resource bounds;
- hash algorithm identifiers, framing, domain separation, downgrade/fallback,
  truncation, and cross-domain replay rules for data-free normative object
  classes; and
- the distinction among CBOR well-formedness, CBOR validity, application
  expectations, CDDL shape conformance, canonical bytes, and semantic validity.

### Independent evidence

At least two implementations with genuinely independent canonicalization
lineage must agree. One should be a Rust/library-backed prototype and one a
separately implemented reference oracle in another language that does not call
the Rust implementation or share its canonicalizer. A third diagnostic library
may be used to expose disagreements, but two wrappers over the same library do
not satisfy independence.

The conformance corpus must include exact bytes, semantic input, expected
accept/reject result, stable failure class, and implementation-lineage metadata.
The harness must prove it detects a deliberately divergent implementation.
Duplicate-key tests must operate before a decoder can discard or overwrite map
entries.

### Scope prohibitions

SQ-0005 must not:

- modify production `backend/` crates or the Rust bootstrap CLI;
- modify the Lean project;
- create schema v0 under `schemas/v0/`;
- implement a logical table or RFC-0006 data-lowering/digest decision;
- implement an artifact envelope, theorem registry, certificate, frontend, or
  statistical type;
- treat CDDL validation as canonical-byte or semantic proof;
- treat a digest equality as collision-free identity proof;
- begin SQ-0006 or SQ-0008 after a readiness-only transition.

## Expected execution pattern

```text
manager
  ├─ CBOR/CDDL/Unicode/registry source curator
  ├─ encoding-profile and numeric-model architect
  ├─ Rust prototype engineer
  ├─ independent reference-oracle engineer
  ├─ differential/conformance engineer
  ├─ parser/resource/security reviewer
  ├─ formal/trust-boundary reviewer
  └─ independent integration reviewer
```

The profile author must not be the sole implementation, security, or
integration reviewer.

## Branch and worktree policy

Use one task per isolated branch or worktree:

```text
agent/SQ-0005-deterministic-serialization
agent/SQ-0008-core-ontology
```

The default branch remains green. Prototypes remain isolated from production
backends and are never promoted merely because they emit the expected bytes.

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
