# Lean Core Implementation Guide

Status: **Experimental**.

SQ-0003 establishes a minimal, reproducible Lean project and a specific locked
proof environment. It does not introduce StatQED statistical semantics or a
public theorem interface.

## Reviewed environment

Treat the Lean and Mathlib revisions as one compatibility pair.

| Component | Exact identity |
|---|---|
| Lean release/channel | `v4.32.2`; `leanprover/lean4:v4.32.2` |
| Lean source | `f3b06c705e6c85f5314019d5d3baab0fec5b580c` |
| Lake | `5.0.0-src+f3b06c7` |
| Mathlib | `905b95818eb32af7874a58b427f50c1711a5e96c` |
| Lake manifest SHA-256 | `c7e814b11c0e33ec8dd4e58bb31ea0999910bdb32848770dd5721f43eee7a14b` |
| Elan bootstrap | `4.2.3`; Linux x86-64 archive SHA-256 `df0b2b3a439961ffcbb3985214365ffe40f49bc871df04dff268c7d8e21ca8b2` |

Primary sources were retrieved on 2026-08-08: the official [Lean v4.32.2
release](https://github.com/leanprover/lean4/releases/tag/v4.32.2), [Lean source
commit](https://github.com/leanprover/lean4/commit/f3b06c705e6c85f5314019d5d3baab0fec5b580c),
[Mathlib commit](https://github.com/leanprover-community/mathlib4/commit/905b95818eb32af7874a58b427f50c1711a5e96c),
[Lean axiom reference](https://lean-lang.org/doc/reference/latest/Axioms/), and
[Lake reference](https://lean-lang.org/doc/reference/latest/build-tools-and-distribution/lake/).
The immutable repository objects, committed lock, and retained command evidence
are authoritative for this task; a release name alone is not compatibility
evidence.

Direct local execution is limited to Ubuntu 24.04.4 LTS on x86-64. GitHub
Actions records the hosted `ubuntu-24.04` image metadata at run time. Neither
observation establishes immutable Linux support or any macOS, Windows, or ARM
support.

## Project boundary

The production layout is deliberately small:

```text
lean/
├── lean-toolchain
├── lakefile.toml
├── lake-manifest.json
├── StatQED.lean
├── StatQED/Internal/Smoke.lean
├── Examples/Smoke.lean
├── Tests/AxiomReport.lean
├── Tests/Trust/
├── Reports/axioms.json
└── tools/
```

`StatQED.lean` establishes the library namespace only.
`StatQED.Internal.testOnlySmoke : True` is definitionally trivial, imports the
narrow `Mathlib.Data.Set.Defs` module, and exists only to test compilation and
environment inspection. It is not a public or registered theorem, statistical
result, non-vacuity witness, artifact claim, or evidence that propositions can
be reconstructed from bytes.

## Installation and normal build

Install the reviewed channel with Elan, then verify the exact identities:

```bash
elan toolchain install leanprover/lean4:v4.32.2
cd lean
lean --version
lake --version
lake update --keep-toolchain
lake build
lake env lean --trust=0 Examples/Smoke.lean
```

The ordinary path may download and reuse Mathlib binary build outputs. These
are performance and supply-chain inputs, not proof authority. The manifest and
kernel-checked declarations remain the relevant logical bindings. Exact local
commands, cache state, elapsed time, source hashes, and failures are retained
under `lean/evidence/`.

Generate the manifest only with the exact Lake tool. A fresh regeneration must
be byte-identical:

```bash
cp lean/lake-manifest.json /tmp/statqed-lean-manifest.expected.json
cd lean
lake update --keep-toolchain
cmp lake-manifest.json /tmp/statqed-lean-manifest.expected.json
sha256sum lake-manifest.json
```

The generated manifest is committed. Do not hand-edit or normalize it. Every
resolved dependency revision is immutable. Mathlib's own inherited input labels
are provenance recorded beside full resolved commits; they are not accepted as
mutable StatQED root pins.

## Isolated no-binary-cache build

The source path must run in a fresh checkout with no `lean/.lake`. Prepare the
exact Elan installation below a dedicated task directory, then run:

```bash
cd /fresh/statqed/lean
STATQED_LEAN_ISOLATION_ROOT=/tmp/statqed-lean-source-isolation \
STATQED_LEAN_ELAN_HOME=/tmp/statqed-lean-source-isolation/elan \
  ./tools/no_cache_build.sh
```

The helper refuses existing Lake state and reused isolation subdirectories. It
runs through `env -i`, so the host home and ambient environment are absent, and
sets task-specific XDG, curl, GnuPG, temporary, Git, and Elan locations. Both
`MATHLIB_NO_CACHE_ON_UPDATE=1` and `LAKE_NO_CACHE=1` remain set for resolution,
source build, smoke execution, and report verification. The exact retained
result is `lean/evidence/no-cache-source-build.json`; cache-assisted success
cannot substitute for it.

## Trust scan

From the repository root, run both output modes:

```bash
python3 scripts/check_lean_trust.py
python3 scripts/check_lean_trust.py --json
python3 scripts/check_lean_trust.py --run-mutations
python3 scripts/check_lean_trust.py --run-mutations --json
```

The scanner binds the exact toolchain, Lake configuration, manifest, resolved
checkout revisions, committed report, and live report regeneration. Its
comment/string-aware source scan is supplementary: declaration kind, module
ownership, elaborated type representation, and transitive axioms come from the
live Lean environment.

The accepted path rejects project-source `sorry`, `admit`, direct or quoted
`sorryAx`, project axiom declarations, checked environment insertion of a
bodyless `.axiomDecl`, mutable or mismatched locks, stale/fabricated reports,
and unreviewed native/unsafe trust shortcuts. The latter include
`native_decide`, `bv_decide`, `Lean.trustCompiler`, `Lean.ofReduceBool`, and
`Lean.ofReduceNat`; these imported or generated axioms are not made acceptable
merely by regenerating the observed baseline. Indirect `Lean.reduceBool` and
`Lean.reduceNat` dependencies are covered by both source mutations and an
actual live report rejection. The scanner does not traverse downloaded Mathlib
source as if it were project-authored code.

`Tests/Trust/expectations.json` defines isolated mutations. The corpus includes
same-line declaration attributes, comments/string positive controls, exact
toolchain and lock changes, and the official Lean issue #14576 projection
reproducer. Lean 4.32.2 has no `constant` surface command; the retained parser
failure documents that fact, while the valid `.axiomDecl` mutation supplies
the non-vacuous bodyless-assumption test. A right-hand-side-free `opaque`
declaration for an inhabited type receives a definition and is not mislabeled
as an axiom.

## Actual axiom report

Run:

```bash
cd lean
lake env lean --trust=0 Tests/AxiomReport.lean
python3 tools/axiom_report.py --check Reports/axioms.json
```

`Tests/AxiomReport.lean` enumerates declarations owned by imported `StatQED`
modules from `Lean.Environment`, inspects declaration kinds and module
ownership, and calls `Lean.collectAxioms`. The selected imported control
`Set.ext` observes `Quot.sound` and `propext`; the internal smoke theorem
observes no transitive axioms. Imported logical axioms are reported separately
from prohibited project-defined axioms.

`tools/axiom_report.py` binds the observation to exact Lean/Lake output,
Mathlib checkout `HEAD`, Mathlib input and resolved revisions, manifest digest,
named command, and deterministic non-normative provenance. The serialized
`Lean.Expr` representation is a locked-environment diagnostic only. This
report is not an axiom permission list, canonical theorem identity, theorem
authorization record, compatibility lock, or RFC-0005 decision.

## CI behavior

`.github/workflows/lean.yml` uses `contents: read`, no persisted checkout
credentials, full action commit pins, explicit timeouts and concurrency, and
the exact reviewed environment. Pull requests and pushes run repository
guardrails, exact pin checks, a dependency cache keyed without fallback by
runner OS/architecture plus the toolchain and manifest, manifest drift checks,
build, smoke, trust/report, and mutation gates.

The no-binary-cache job runs on manual dispatch, weekly schedule, and changes
to the three lock inputs. Its evidence may be at most 14 days old; delayed,
dropped, or disabled hosted schedules do not waive revalidation. Exact lock
changes fail closed into the source-build job. No workflow success is described
as artifact-level verification.

## Updating, rollback, and generated files

For an update:

1. research current official Lean, Mathlib, Lake, Elan, and action sources;
2. test the Lean/Mathlib pair as one exact pair;
3. change `lean-toolchain`, the full Mathlib revision in `lakefile.toml`, and
   the Lake-generated manifest together;
4. regenerate the actual axiom report;
5. run normal, fresh source, manifest, trust, mutation, and CI gates; and
6. obtain independent formal, adversarial, reproducibility, and integration
   review before merging.

Rollback restores the reviewed toolchain, Lake configuration, manifest, and
matching report together. Partial rollback is a lock mismatch and must fail.
Only Lake generates `lake-manifest.json`; only the reviewed report helper
generates `Reports/axioms.json`. Generated build trees and downloaded packages
are never committed.

## Trust boundary and nonclaims

For these observations, the pinned Lean kernel checks declarations. Logical
axioms named in the report remain explicit assumptions of that environment.
Elan, Lake, Git, operating-system services, networks, caches, the Lean
elaborator/compiler, Mathlib build tooling, Python report orchestration, GitHub
Actions, reviewers, and agents are operational or evidence-producing inputs;
they are not silently promoted to scientific or artifact-verification
authority.

SQ-0003 establishes only:

- a reproducible minimal Lean project;
- a specific locked Lean/Mathlib environment;
- project-source trust checks with retained positive and negative controls; and
- actual axiom observations for explicitly named declarations.

It does not establish source-theorem fidelity, statistical identification or
validity, external model assumptions, numerical correctness, data or
provenance truth, interpretation, artifact-byte binding, theorem-registry
authority, certificate-checker soundness, or general kernel verification of
`.statqed` artifacts.
