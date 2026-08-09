# Handoff: SQ-0004 Post-Merge Review

## Objective and status

SQ-0004 remains **DONE** with an **Experimental** Rust operational foundation.
The independent post-merge review found no blocking code, security, evidence,
workflow, or task-state defect. It repaired current-task metadata and rebuilt
the SQ-0005 execution contract without changing Rust source, Cargo.lock, task
states, accepted ADRs, or RFC dispositions.

## Reviewed commits

- Reviewed pre-SQ-0004 main: `726821bf1a29995756dc10cbbecfd452dccad7e5`
- Corrected immutable review package: `cecbaa318f043bedd9898afe20e9f930c39eb732`
- Final reviewed task head: `35a8404920dee19ecda6e8c6a0e549cacd06b069`
- SQ-0004 task merge / PR #8: `7a83eb843a216886816553897bf541aeb0270c22`
- Post-merge evidence record / PR #9: `4aa0b9c145ce2595f3630d17abcfb7e4248579b4`
- Post-merge review: `work/reviews/SQ-0004-post-merge.md`

The final planning-maintenance merge and workflow IDs are recorded after the
exact maintenance head passes review and CI.

## Accepted SQ-0004 surface

- Rust 1.97.1 for development, acquisition, formatting, Clippy, tests, lock
  generation, and security tooling;
- Rust 1.85.1 for the exact committed graph under `--locked --offline` only;
- Edition 2024, resolver 3, and `rust-version = "1.85.1"`;
- dependency-free local `statqed-core` and `statqed-cli` packages;
- Cargo.lock SHA-256
  `408f171020abc33031390a1c22ed3f21ec271b797d880f7749f83edec04211a3`;
- deterministic bounded version/error CLI behavior;
- fixed input limits and non-UTF-8 handling;
- two clean lock reproductions and isolated development/floor execution;
- 20 adversarial mutations and ten deterministic process fixtures;
- normalized two-package license inventory;
- hash-bound cargo-audit/RustSec point-in-time observation; and
- least-privilege Rust CI with exact action and tool identities.

## Review outcome

No blocking defect was found. The source and tests enforce the stated
bootstrap boundary, and the evidence package is unusually complete for a
foundation-only Rust task. The main residual limits are explicit: the CLI is
not a verifier, the workflow policy parser is narrow, advisory results are
dated, rustup/OS/runner infrastructure remains operationally trusted, and
direct platform evidence is Linux x86-64 only.

## Planning corrections

The maintenance branch:

- advances `START_HERE.md` from completed SQ-0004 to the actual
  SQ-0005/SQ-0008 READY state;
- records `4aa0b9c145ce2595f3630d17abcfb7e4248579b4` as the final integrated SQ-0004
  evidence state;
- recommends SQ-0005 as the next isolated task while leaving SQ-0008 READY;
- expands SQ-0005 into a complete RFC, prototype, conformance, evidence,
  security, review, and state-transition contract; and
- removes RFC-0006 from SQ-0005's writable scope because RFC-0006 belongs to
  SQ-0027.

No task state changes during this maintenance.

## Critical SQ-0005 boundary

SQ-0005 owns RFC-0001 and cannot become DONE while RFC-0001 remains Draft.
SQ-0005 must decide the smallest data-free deterministic encoding profile using
independent source-grounded implementations and reviewed vectors.

RFC-0006 remains Draft under SQ-0027 ownership. SQ-0005 may record generic atom
and digest-framing requirements relevant to future data work, but must not
create a logical table, Arrow lowering, logical-data identity, privacy claim,
or canonical logical-data digest.

## Required validation before maintenance merge

```text
make check
make list-work
git diff --check
```

The exact maintenance head must also receive successful:

- repository guardrails;
- Rust development and offline-floor jobs; and
- unchanged Lean proof-backend jobs.

## Trust boundary and nonclaims

SQ-0004 establishes a reproducible minimal Rust workspace and bounded bootstrap
CLI behavior. It does not establish:

- statistical semantics or validity;
- deterministic normative encoding;
- CDDL schema semantics;
- logical-data identity or digest;
- artifact verification;
- theorem identity or registry authority;
- certificate checking;
- frontend conformance;
- source theorem fidelity; or
- a verified statistical analysis.

## Next dependency-ready work

After this maintenance is merged, the checked ledger remains:

```text
READY: SQ-0005, SQ-0008
ACTIVE: none
```

Execute **SQ-0005 only** in
`agent/SQ-0005-deterministic-serialization`. Leave SQ-0008 READY and unstarted.
If SQ-0005 accepts RFC-0001 and is independently transitioned to DONE, recompute
readiness; the expected result is SQ-0006 and SQ-0008 READY, but do not force
that result or begin either successor in the SQ-0005 run.

## Cleanup

Task-created build trees, temporary Cargo homes, extracted advisory databases,
and disposable evidence-generation directories may be removed after their
small reviewed records are committed. Preserve shared toolchains and all
user-owned untracked paths, including `.codex/`, unless the user explicitly
requests otherwise.
