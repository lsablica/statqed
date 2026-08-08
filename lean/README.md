# StatQED Lean proof-backend bootstrap

Status: **Experimental**.

This directory is the minimal SQ-0003 Lean project. It establishes a pinned
build, test, and axiom-reporting surface only. It contains no statistical
ontology, inference theorem, certificate checker, registry semantics, artifact
semantics, or public StatQED theorem.

## Exact environment

| Component | Locked identity |
|---|---|
| Lean channel | `leanprover/lean4:v4.32.2` |
| Lean commit | `f3b06c705e6c85f5314019d5d3baab0fec5b580c` |
| Lake | `5.0.0-src+f3b06c7` bundled with Lean |
| Mathlib | `905b95818eb32af7874a58b427f50c1711a5e96c` |

`lean-toolchain`, `lakefile.toml`, and the Lake-generated
`lake-manifest.json` must move together. The manifest locks the full resolved
dependency graph. Mutable input labels inherited from Mathlib are not accepted
as root StatQED pins; their resolved manifest revisions remain immutable.

Elan 4.2.3 is the reviewed bootstrap manager. It is installation provenance,
not theorem authority. With that exact Elan on `PATH`, prepare the toolchain:

```bash
elan toolchain install leanprover/lean4:v4.32.2
lean --version
lake --version
```

## Normal build and test

From this directory:

```bash
lake update --keep-toolchain
lake build
lake env lean --trust=0 Examples/Smoke.lean
python3 tools/axiom_report.py --check Reports/axioms.json
```

`StatQED.lean` is the top-level library. `StatQED.Internal.testOnlySmoke` is a
definitionally trivial `True` theorem in an internal module which imports only
`Mathlib.Data.Set.Defs`. It is test infrastructure, not a registered theorem,
semantic non-vacuity witness, scientific result, or artifact claim.

The normal update may use Mathlib's binary cache. A cache is a performance and
supply-chain input, not a semantic authority. A cache miss must fall back to
the same locked sources.

## Actual axiom report

`Tests/AxiomReport.lean` obtains declaration names, defining modules,
declaration kinds, elaborated type representations, and transitive axiom sets
from the live `Lean.Environment` and `Lean.collectAxioms`. It enumerates every
declaration owned by imported `StatQED` modules, rejects project axiom
declarations and project declarations whose closure contains `sorryAx` or a
project axiom, and also reports the selected imported declaration `Set.ext`.

`tools/axiom_report.py` binds that live probe to:

- exact Lean and Lake version output;
- committed manifest SHA-256;
- Mathlib input and resolved revisions;
- the actual checked-out Mathlib `HEAD`;
- the exact `--trust=0` probe command; and
- complete project source-module coverage.

The generated report is `Reports/axioms.json`. Regenerate it only from the
locked environment:

```bash
python3 tools/axiom_report.py --write Reports/axioms.json
python3 tools/axiom_report.py --check Reports/axioms.json
```

The type text is locked diagnostic `Lean.Expr` representation, not a canonical
theorem identity. The report is actual logical-dependency evidence, not an
allowlist granting permission to add axioms.

## Manifest regeneration

A clean manifest-only reproduction uses a disposable directory and disables
Mathlib/Lake binary-cache use:

```bash
STATQED_MANIFEST_REPRO_DIR=/tmp/statqed-lean-manifest-repro
mkdir "$STATQED_MANIFEST_REPRO_DIR"
cp lakefile.toml lean-toolchain "$STATQED_MANIFEST_REPRO_DIR"/
cd "$STATQED_MANIFEST_REPRO_DIR"
MATHLIB_NO_CACHE_ON_UPDATE=1 LAKE_NO_CACHE=1 lake update --keep-toolchain
cmp lake-manifest.json /path/to/statqed/lean/lake-manifest.json
```

The observed SQ-0003 run produced byte-identical SHA-256
`c7e814b11c0e33ec8dd4e58bb31ea0999910bdb32848770dd5721f43eee7a14b`.
See `evidence/manifest-reproduction.json` for the exact observed command and
result.

## Isolated no-binary-cache source build

Run the helper only inside a fresh checkout where `lean/.lake` does not exist.
It refuses pre-existing Lake state and keeps both cache-disable variables set
for dependency resolution, build, example, and report verification:

```bash
cd /fresh/checkout/lean
STATQED_LEAN_ISOLATION_ROOT=/tmp/statqed-lean-source-isolation \
STATQED_LEAN_ELAN_HOME=/tmp/statqed-lean-source-isolation/elan \
  ./tools/no_cache_build.sh
```

Prepare the exact Elan/toolchain installation below the dedicated isolation
root before invoking the helper. The helper refuses pre-existing project Lake
state or reused XDG/curl/GnuPG/temp state, launches every build command through
`env -i` so the host home is not inherited, and supplies only explicit isolated
configuration/cache locations. This is intentionally a separate path from the
normal build. Do not present a normal cache-assisted result as source-build
evidence.

## Trust mutations and kernel regression

`Tests/Trust/expectations.json` describes permanent negative fixtures for
placeholders, project axioms/bodyless constants, toolchain and lock changes,
mutable revisions, native proof shortcuts, and missing or fabricated axiom
reports. It also contains comment/string positive controls. Fixture files are
not part of the accepted library.

The same corpus retains the official Lean issue #14576 wrong-structure
projection reproducer. The pinned kernel rejects it under `--trust=0` with
`(kernel) invalid projection`; that observed regression does not establish the
absence of other kernel defects.

## Update, rollback, and limits

For an update, re-audit official releases, change the Lean channel, full
Mathlib revision, and generated manifest atomically, then rerun normal and
no-cache builds, manifest byte reproduction, the live axiom report, trust
mutations, and independent review. Rollback restores all three lock files and
the matching reviewed report together.

A successful build and axiom report establish only that named declarations
elaborate and have the reported dependencies in the locked environment. They
do not establish source fidelity, statistical identification or inference,
external premises, data/provenance truth, interpretation, or `.statqed`
artifact-byte binding. Direct SQ-0003 execution evidence is Linux x86-64 only;
other platforms require separate observed evidence.
