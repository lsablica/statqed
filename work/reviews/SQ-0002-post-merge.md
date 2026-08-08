# Post-Merge Review: SQ-0002

- Review date: 2026-08-08
- Reviewed repository head: `01c5b6e1bfacf332dbb01259aa19258a3edd0f9e`
- SQ-0002 reviewed baseline: `9bf99227240550a6c84f417eccd99c48f43be6ec`
- Original integration merge: `4e8a1e3b77736cca64e460723bbe61941eca3bb5`
- Durable-evidence correction: `10b75eecb5b34a518557133a4876ced93ea34bba`
- Packaging re-review: `804c11916bf5d05bc569af9df1aa73bb331626b2`
- Final evidence-packaging merge: `01c5b6e1bfacf332dbb01259aa19258a3edd0f9e`
- Review type: independent post-merge repository, evidence, planning, and successor-readiness review

## Disposition

**APPROVE WITH COMPLETED PLANNING MAINTENANCE.**

No blocking defect was found in the SQ-0002 research result, retained evidence, trust-boundary claims, task-state transition, or recommendation scope. The post-merge review found five planning/durability defects that did not invalidate the reviewed recommendations:

1. `START_HERE.md` still named SQ-0002 as the current task after SQ-0002 was DONE.
2. `work/status.yaml` still identified the pre-merge DONE-transition commit rather than the final evidence-packaging merge.
3. Plan 0001 still reported 119 prototype subjects after the clean-checkout packaging correction reduced the durable tracked manifest to 115.
4. GitHub `repository-guardrails` ran `make check`, but `make check` did not yet invoke the strict SQ-0002 evidence verifier, so later evidence drift would not necessarily fail CI.
5. The SQ-0003 and SQ-0004 contracts did not authorize their own state transitions, review/handoff records, or sufficiently detailed trust/reproducibility gates.

The review branch corrects those issues without changing any SQ-0002 toolchain recommendation, probe classification, source record, Draft RFC status, accepted ADR, or task state.

## Scope and change review

The complete SQ-0002 series adds only:

- the compatibility report;
- machine-readable source/probe/recommendation/CI data;
- isolated research prototypes and retained logs;
- the standard-library evidence verifier and safe rerun dispatcher;
- task contract, review, handoff, status, and active-plan records.

No production Lean, Rust, R, Python, Julia, schema, conformance, theorem-registry, method-pack, artifact, RFC, or ADR implementation was introduced by SQ-0002. The two unrelated Dependabot workflow-action updates landed before the substantive evidence series and do not alter SQ-0002's recommendation semantics.

## Evidence integrity

The final retained subject is described by:

- compatibility-report SHA-256 `3c47b0d4bc090b8dd52db5860c297075ac9bd8b1e82bfa2c3608c24b6449a205`;
- matrix SHA-256 `9e6e09085ffe1b1877492fe8835f75ad5961583ceaa7886e778ab3edbf16c3cf`;
- compact prototype-subject manifest SHA-256 `47a9aeaad96bbe5235dd91997a8b1902525cdb67f72514c5f5b7c932d30984c4`;
- 115 tracked `{path, sha256}` prototype subjects;
- 75 probes: 31 success, 37 failure, seven unknown;
- six recommendation records;
- 90 dated source records.

The initial clean-checkout packaging failure was handled correctly: four ignored `.pytest_cache` files were removed from the durable manifest, no substantive probe or recommendation changed, and an independent packaging re-review verified that every remaining subject was tracked and hash-matched.

## Verifier review

`scripts/bootstrap/run_toolchain_probes.py` is appropriately narrow for a research-evidence verifier:

- it uses the Python standard library;
- evidence paths are confined to the prototype tree;
- retained stdout/stderr and prototype subjects are SHA-256 bound;
- sources, timestamps, classifications, dispositions, locks, recommendations, CI claims, and report-summary consistency are validated;
- recommendations may rely only on successful recommended probes;
- direct CI claims are bound to observed OS, architecture, and version evidence;
- reruns are opt-in, path-confined, and allowlisted;
- the rerun environment is non-inherited and isolates HOME/cache/configuration;
- unavailable recommended tooling fails closed;
- eight minimized corruption cases exercise mutable pins, platform laundering, arbitrary commands, normalized failure, missing locks, advisory-response corruption, environment inheritance, and unavailable recommendations.

The verifier does not itself prove that external commands originally ran, that source websites were truthful, that dependencies are secure, or that a toolchain has statistical meaning. Those are correctly excluded from its claim boundary.

The post-merge correction makes this verifier a permanent `make check` dependency, so the existing repository-guardrails workflow will detect later matrix/report/evidence drift.

## Recommendation review

The recommendations remain bounded and coherent:

- Lean 4.32.2 and Mathlib commit `905b95818eb32af7874a58b427f50c1711a5e96c` are one exact pair, not independently floating versions.
- Rust 1.97.1 is the development/acquisition toolchain; Rust 1.85.1 is an offline compiler/API compatibility floor, not a networked Cargo or release tool.
- Python, R, and Julia development pins, support floors, and planned CI coverage remain separate concepts.
- Arrow, CBOR, and CDDL libraries remain Experimental compatibility observations and do not settle RFC-0001 or RFC-0006.
- Direct compatibility claims remain Linux x86-64 only; macOS, Windows, ARM, hosted-runner, publication, and intermediate-version entries remain planned or unknown.

The selected pins are research recommendations for their owning bootstrap tasks. SQ-0003 and SQ-0004 must reproduce their own production locks and checks; they may not cite SQ-0002 as a substitute for executing their contracts.

## Source and specialist review

The original review record contains distinct final approvals for:

- source currentness and lineage;
- Lean/Mathlib/Lake compatibility;
- Rust/Cargo/MSRV;
- R/Python/Julia support policy;
- Arrow/CBOR/CDDL interoperability;
- statistical semantics and trust boundaries;
- release/security adversarial review;
- integration;
- post-merge packaging integrity.

The post-merge review does not replace those reviews. It checks that the merged repository accurately preserves their subject and limitations.

## CI and reproducibility evidence

The final SQ-0002 merge `01c5b6e1bfacf332dbb01259aa19258a3edd0f9e` has a successful `repository-guardrails` push run. Its checkout, Python setup, repository-guardrail, and work-ledger steps all completed successfully.

That run predated the permanent `make check` integration of the strict SQ-0002 verifier. The planning-maintenance branch must therefore receive a successful repository-guardrails run after the Makefile change before this post-merge maintenance is integrated.

This review inspected retained source and evidence through GitHub and the recorded command transcripts. It did not redownload every external runtime asset or repeat the 1,710-job Mathlib source build. The task's original exact execution evidence and independent integration review remain the authority for those expensive probes.

## Successor readiness

The ledger correctly exposes two independent successors:

- SQ-0003 — Lean/Mathlib project bootstrap;
- SQ-0004 — Rust reference-workspace bootstrap.

The recommended next isolated execution is SQ-0003 because it establishes the initial proof-backend build, actual axiom-reporting surface, and Lean trust guardrails. SQ-0004 remains READY and must retain its state unless a separate execution begins.

Both successor contracts were expanded during this review to make their state transitions, exact pins, negative tests, workflow evidence, review records, and handoffs executable without semantic improvisation.

## Final nonclaims

Approval of SQ-0002 does not establish:

- a functioning production Lean or Rust project;
- canonical CBOR or CDDL semantics;
- logical-data identity;
- artifact verification;
- theorem identity or authorization;
- a statistical ontology or guarantee;
- cross-platform compatibility beyond the directly tested Linux x86-64 host;
- package-name reservation or publication approval;
- absence of dependency or toolchain vulnerabilities.

Those remain explicitly owned by later tasks and Draft RFCs.
