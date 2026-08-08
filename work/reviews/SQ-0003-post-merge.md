# Post-Merge Review: SQ-0003

- Review date: 2026-08-09
- Reviewed repository head: `b7f98a99cdc4babccd920c52f5a2e55f8051228c`
- Reviewed SQ-0003 task merge: `92e3b331b1ae795a21d6e030a21e8ce8d7da03dd`
- Reviewed final merge-evidence record: `b7f98a99cdc4babccd920c52f5a2e55f8051228c`
- Original immutable review package: `34e4d856e3ee5c85aab91a0427f9b4176aa7aac7`
- Review type: independent post-merge code, formal-trust, evidence, CI, planning, and successor-readiness review

## Disposition

**APPROVE WITH TRUST-HARDENING AND COMPLETED PLANNING MAINTENANCE.**

No blocking defect was found in SQ-0003's task scope, exact Lean/Mathlib lock,
minimal project structure, live axiom observations, source scanner, mutation
corpus, normal/source builds, independent review, or DONE transition. SQ-0003
correctly remains **Experimental** and makes no statistical, artifact,
registry-authority, or source-fidelity claim.

The post-merge review found four non-blocking maintenance issues:

1. `START_HERE.md` still selected SQ-0003 after SQ-0003 was DONE.
2. `work/status.yaml` identified the first task merge rather than the final
   merge-evidence record as the last integrated SQ-0003 commit.
3. The SQ-0004 contract still described SQ-0003 as READY and did not authorize
   the readiness-only SQ-0005 contract update required when SQ-0004 becomes
   DONE.
4. The Lean gates built source, ran a `--trust=0` smoke check, generated a live
   axiom report, and tested environment mutations, but did not independently
   replay the compiled `.olean` declaration graph in a fresh kernel
   environment.

The maintenance branch fixes these issues without changing the Lean/Mathlib
pair, manifest, theorem source, axiom report, task states, accepted ADRs, or any
Draft RFC status.

## Scope review

The complete SQ-0003 implementation changes only the contracted Lean
foundation and associated planning/evidence paths:

- exact `lean-toolchain`, `lakefile.toml`, and Lake-generated manifest;
- empty top-level `StatQED` namespace and one internal test-only theorem;
- smoke example and environment-derived axiom report;
- source/trust scanner and 33 positive, negative, live-report, and kernel
  regression cases;
- normal, manifest-reproduction, and isolated source-build evidence;
- least-privilege, commit-pinned Lean workflow;
- implementation guide, quality dashboard, review, handoff, and task ledger.

No Rust, frontend, schema, artifact, registry, certificate, method-pack, or
statistical semantic implementation was introduced by SQ-0003.

## Exact environment and dependency lock

The production project binds:

- `leanprover/lean4:v4.32.2`;
- Lean commit `f3b06c705e6c85f5314019d5d3baab0fec5b580c`;
- Lake `5.0.0-src+f3b06c7`;
- Mathlib commit `905b95818eb32af7874a58b427f50c1711a5e96c`;
- manifest SHA-256
  `c7e814b11c0e33ec8dd4e58bb31ea0999910bdb32848770dd5721f43eee7a14b`.

The root Mathlib requirement and manifest input/resolved revisions are exact
full commits. Every resolved transitive package has a full commit. Inherited
Mathlib input labels such as `main` or `master` remain provenance beside exact
resolved revisions and are not root StatQED pins. Manifest regeneration was
recorded byte-identical.

## Project and semantic-boundary review

The production library is intentionally minimal:

- `StatQED.lean` creates an otherwise empty namespace;
- `StatQED.Internal.testOnlySmoke : True` is definitionally trivial and
  test-only;
- the internal smoke module imports only `Mathlib.Data.Set.Defs`;
- the smoke theorem is not imported into the top-level module;
- no registry record, public statistical theorem, estimand, procedure,
  experiment, evidence taxonomy, artifact, certificate, or method pack exists.

The comments and documentation consistently state that `True` is not a public
theorem, non-vacuity witness, scientific result, or artifact claim.

## Axiom and declaration review

`Tests/AxiomReport.lean` reads the elaborated `Lean.Environment`, identifies
project-owned modules/declarations, obtains declaration kind, defining module,
unsafe status, elaborated type representation, and transitive axioms using
`Lean.collectAxioms`, and rejects:

- project axiom declarations;
- unsafe project declarations;
- project closures containing `sorryAx`;
- project-owned axiom dependencies; and
- the reviewed imported native-trust axioms.

`tools/axiom_report.py` binds the observation to the exact toolchain, Lean
commit, Lake version, manifest digest, Mathlib input/resolved revisions,
checked-out Mathlib `HEAD`, command, and complete project-source module set.
The committed report observes:

- no transitive axioms for `StatQED.Internal.testOnlySmoke`;
- `Quot.sound` and `propext` for imported `Set.ext`.

This is locked-environment logical-dependency evidence. It is not a canonical
theorem identity, an axiom permission list, registry authorization, source
fidelity, or RFC-0005 resolution.

## Trust scanner and mutation review

`scripts/check_lean_trust.py` combines exact lock checks, dependency checkout
HEAD/cleanliness checks, comment/string-aware source inspection, static report
validation, and live report regeneration. It does not scan downloaded Mathlib
source as though it were project-authored code.

The retained corpus contains 33 intended differentials covering:

- `sorry`, `admit`, direct and quoted `sorryAx`;
- project axioms, bodyless declarations, and checked `.axiomDecl` insertion;
- exact and adjacent toolchain mismatches;
- changed, stale, mutable, or fabricated dependency/report state;
- `native_decide`, `bv_decide`, unsafe declarations, `trustCompiler`,
  `ofReduceBool`, `ofReduceNat`, and indirect native-trust closures;
- positive controls for comments, strings, and inert name quotations; and
- the official Lean issue #14576 wrong-projection regression.

The live report cases ensure important failures are observed in the Lean
environment rather than only through text patterns. The official regression is
rejected by the pinned kernel under `--trust=0`; this does not establish the
absence of other kernel defects.

## Normal and isolated source builds

The retained evidence records:

- successful normal build and `--trust=0` smoke execution;
- byte-identical manifest regeneration;
- an isolated no-binary-cache source build with no existing project `.lake`,
  `env -i`, isolated Elan/XDG/Git/curl/GnuPG/temp state, and both
  `MATHLIB_NO_CACHE_ON_UPDATE=1` and `LAKE_NO_CACHE=1`;
- successful dependency resolution, 88-job source build, smoke execution, and
  live axiom-report comparison.

The exact merge workflow also completed both cached and isolated-source jobs.
Direct evidence is Ubuntu Linux x86-64 only.

## Fresh compiled-module replay hardening

Official Lean proof-validation guidance recommends replaying declarations from
compiled `.olean` files through a fresh kernel environment to detect a small
class of environment manipulation or dishonest compiled-environment behavior.
Lean's environment implementation also documents that imported constants may
be assumed type-correct when the environment trust level is greater than zero.

The maintenance adds:

```text
lake env leanchecker --fresh StatQED.Internal.Smoke
```

to cached CI, isolated-source CI, the no-cache helper, and user-facing Lean
documentation. The source-job selector now also runs when the Lean workflow or
no-cache helper changes, ensuring this maintenance is tested on both paths.

This replay uses the same Lean kernel and trusts structural decoding of `.olean`
files. It is additional defense-in-depth, not an independent external verifier,
artifact decoder, theorem-source audit, or scientific-validity check.

## Original CI and review evidence

The original exact task package received distinct final approvals for:

- Mathlib/source lineage;
- production build and lock reproduction;
- formal declaration and axiom reporting;
- adversarial trust and overclaim resistance;
- CI/reproducibility; and
- integration.

The main task merge workflow `31280203112` completed cached and isolated-source
builds, smoke checks, live reports, and all trust mutations. The final
merge-evidence head `b7f98a99cdc4babccd920c52f5a2e55f8051228c` also passed
repository guardrails and the cached Lean trust suite; the source job was
correctly skipped because that final commit changed documentation only.

## Planning maintenance

The maintenance branch:

- advances `START_HERE.md` to the actual SQ-0004/SQ-0008 READY state and
  recommends SQ-0004 as the next isolated task;
- updates `work/status.yaml` to the final SQ-0003 merge-evidence record;
- expands SQ-0004's dependency/current-state language;
- authorizes only the readiness-status update to `work/contracts/SQ-0005.yaml`
  when SQ-0004 completion makes SQ-0005 eligible;
- requires SQ-0004 to leave SQ-0003 DONE and SQ-0008 READY/unstarted; and
- preserves every task state during this review maintenance.

## Residual limitations

- Direct compatibility evidence remains Linux x86-64 only.
- The weekly no-cache age requirement is documented and operationally reviewed,
  not yet represented by an independent repository-age checker.
- The report type representation is diagnostic rather than a canonical theorem
  identity.
- `leanchecker` is a same-kernel replay, not an independent proof checker.
- No source theorem, statistical guarantee, external premise, numerical fact,
  artifact byte binding, registry authority, checker soundness, or verified
  analysis is established.
- RFC-0001 through RFC-0009 remain Draft.

## Integration condition

The maintenance may merge only after repository guardrails and the Lean
workflow pass on the exact maintenance head. Because the workflow and
no-cache helper changed, the source selector must run and the isolated-source
job must execute the new fresh replay command rather than being skipped.
