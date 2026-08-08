# Handoff: SQ-0003 Post-Merge Review

## Objective and status

SQ-0003 remains **DONE** with an **Experimental** Lean proof foundation. The
independent post-merge review found no blocking implementation or evidence
defect. It added one defense-in-depth trust gate and repaired successor
planning without changing the exact Lean/Mathlib environment, task states,
accepted ADRs, or Draft RFCs.

## Reviewed commits

- SQ-0003 reviewed base: `d32c50adaec62543e1a7fbc52f62e33ce8f373bb`
- Immutable task review package: `34e4d856e3ee5c85aab91a0427f9b4176aa7aac7`
- Atomic DONE transition: `3194f12b1b14f48813e98db60cac9c42f5c7280c`
- Reviewed task head: `94a6381e25c18fbd317e119e8f6b80d91239ce61`
- SQ-0003 task merge: `92e3b331b1ae795a21d6e030a21e8ce8d7da03dd`
- Final task merge-evidence record: `b7f98a99cdc4babccd920c52f5a2e55f8051228c`
- Post-merge review record: `work/reviews/SQ-0003-post-merge.md`

The final maintenance merge and workflow IDs are recorded after the exact
maintenance head passes review and CI.

## Accepted SQ-0003 surface

- Lean `leanprover/lean4:v4.32.2`, commit
  `f3b06c705e6c85f5314019d5d3baab0fec5b580c`;
- Lake `5.0.0-src+f3b06c7`;
- Mathlib `905b95818eb32af7874a58b427f50c1711a5e96c`;
- manifest SHA-256
  `c7e814b11c0e33ec8dd4e58bb31ea0999910bdb32848770dd5721f43eee7a14b`;
- empty public namespace and internal test-only `True` theorem;
- live environment-derived declaration/axiom report;
- exact lock and dependency-checkout validation;
- 33 trust, lock, report, native-path, positive-control, and kernel-regression
  cases;
- normal and isolated no-binary-cache source builds;
- least-privilege, commit-pinned Lean CI.

## Post-merge hardening

The review adds fresh replay of the compiled smoke module and its imports:

```bash
cd lean
lake env leanchecker --fresh StatQED.Internal.Smoke
```

The command is now part of:

- cached Lean CI;
- isolated no-binary-cache CI;
- `lean/tools/no_cache_build.sh`;
- `lean/README.md`; and
- `docs/implementation/lean-core.md`.

The source-job selector also treats changes to the workflow or no-cache helper
as reasons to execute the isolated source job. This prevents a helper-only
change from being merged without exercising the path it changes.

Fresh replay is same-kernel defense-in-depth against compiled environment
manipulation. It is not an independent verifier, theorem-source validation,
artifact byte-to-term checking, or statistical assurance.

## Planning corrections

- `START_HERE.md` now derives the current state as SQ-0004 and SQ-0008 READY.
- SQ-0004 is the recommended next isolated execution because it completes the
  second Milestone B language bootstrap and unlocks SQ-0005.
- SQ-0008 remains independently READY and unstarted.
- `work/status.yaml` now records the final SQ-0003 merge-evidence commit.
- `work/contracts/SQ-0004.yaml` now reflects SQ-0003 DONE, preserves SQ-0008,
  and authorizes the readiness-only SQ-0005 contract update required by the
  shared ledger when SQ-0004 becomes DONE.

No task state changed during this maintenance.

## Required validation before merge

```text
make check
make list-work
git diff --check
```

The exact maintenance head must also receive successful:

- repository guardrails;
- cached Lean build/trust gates, including `leanchecker --fresh`; and
- isolated no-binary-cache source build/trust gates, including
  `leanchecker --fresh`.

## Trust boundary and remaining nonclaims

The Lean foundation establishes reproducible build/trust observations for the
named locked environment. It does not establish:

- public statistical semantics or theorem source fidelity;
- external scientific assumptions;
- numerical correctness;
- artifact-byte binding or decoder soundness;
- theorem registry identity or authorization;
- certificate checker soundness;
- cross-platform support beyond direct Linux x86-64 evidence; or
- a verified statistical analysis.

RFC-0001 through RFC-0009 remain Draft.

## Next dependency-ready work

After this maintenance is merged, the checked ledger remains:

```text
READY: SQ-0004, SQ-0008
ACTIVE: none
```

Execute **SQ-0004 only** in `agent/SQ-0004-rust-bootstrap`. Leave SQ-0008
READY and unstarted. When SQ-0004 is independently reviewed and transitioned
to DONE, recompute readiness; the expected result is SQ-0005 and SQ-0008 READY,
but do not force that result or begin either successor in the SQ-0004 run.
