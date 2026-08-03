# Lean / Mathlib / Lake compatibility prototype

Status: **Draft research evidence**.

Evidence date: 2026-08-03. Directly tested only on Ubuntu 24.04.4 LTS, Linux 7.0.0-28-generic, x86_64, `C.UTF-8`. This prototype neither initializes `lean/` nor claims artifact-level kernel verification.

## Recommendation

Use this exact development pair for SQ-0003:

- Lean release/channel file: `leanprover/lean4:v4.32.1`;
- Lean release commit reported by the installed binary: `f054605aea4b840552cca2e725580bffd1e1b704`;
- Mathlib immutable git revision: `520045ab14e26149ee970e2e617ca04b09bde5d6` (also tagged `v4.32.1`);
- Lake: the version bundled with that Lean release, `5.0.0-src+f054605` (Lean `4.32.1`), not an independently floating Lake installation;
- tested toolchain manager for bootstrapping: elan `4.2.3` (`b6cec7e10`, archive SHA-256 `df0b2b3a439961ffcbb3985214365ffe40f49bc871df04dff268c7d8e21ca8b2`). Elan is installation provenance, not part of the mathematical theorem lock.

The Lean release tag and Mathlib commit are deliberately distinct identifiers. The matching version text does not establish compatibility; the builds in `recommended/` and `no-binary-cache/` do.

An independent minimum Lean support floor is not meaningful for one frozen Mathlib revision. Mathlib's immutable `lakefile.lean` sets `fixedToolchain := true` and says a Mathlib version supports the toolchain it was built with. The deliberate Lean `v4.31.0` plus Mathlib `v4.32.1`-commit build fails in `Mathlib.Init`. StatQED should therefore support an exact Lean/Mathlib environment lock, not a Lean range. If the project later supports an older line, it should test a separate matched Lean/Mathlib pair and migration path rather than call that version a floor for the current lock.

## Results

| Probe | Cache/network mode | Result |
|---|---|---|
| `recommended/` | Lake resolution with Mathlib's post-update binary-cache hook | Success after a package-scoped clean recovered an incomplete-clone/stale-object failure |
| `recommended/` | `lake build` plus `lake env lean` | Success; imported `Mathlib.Probability.ProbabilityMassFunction.Basic` |
| `no-binary-cache/` | Fresh dependency resolution with `MATHLIB_NO_CACHE_ON_UPDATE=1` and `LAKE_NO_CACHE=1` | Success |
| `no-binary-cache/` | Fresh source build with both variables set | Success, 1,710 jobs |
| `rejected-lean-4.31-mathlib-4.32.1/` | Fresh no-cache build | Expected failure in `Mathlib.Init` |

The successful axiom inspection is:

```text
'StatQEDLeanProbe.pmf_total_mass' depends on axioms: [propext, Classical.choice, Quot.sound]
```

There is no `sorryAx` in the successful result. Three rejected proof bodies did report `sorryAx` because elaboration failed; those failures are retained in `../logs/lean/stderr.log` and are not accepted proof evidence.

## Exact rerun commands

The following uses a task-specific isolated Elan directory. Replace `<repo>` with the checkout root. Network access is required for the toolchain and first dependency resolution. Generated `.lake` trees are intentionally not committed.

```bash
ELAN_HOME=/tmp/statqed-sq0003-elan <elan-4.2.3-extracted>/elan-init -y --no-modify-path --default-toolchain none
ELAN_HOME=/tmp/statqed-sq0003-elan /tmp/statqed-sq0003-elan/bin/elan toolchain install leanprover/lean4:v4.32.1
cd <repo>/docs/research/toolchain-prototypes/lean-mathlib/recommended
ELAN_HOME=/tmp/statqed-sq0003-elan PATH=/tmp/statqed-sq0003-elan/bin:/usr/bin:/bin lake update --keep-toolchain
ELAN_HOME=/tmp/statqed-sq0003-elan PATH=/tmp/statqed-sq0003-elan/bin:/usr/bin:/bin lake build
ELAN_HOME=/tmp/statqed-sq0003-elan PATH=/tmp/statqed-sq0003-elan/bin:/usr/bin:/bin lake env lean StatQEDLeanProbe.lean
```

Fresh source/no-binary-cache check:

```bash
cd <repo>/docs/research/toolchain-prototypes/lean-mathlib/no-binary-cache
ELAN_HOME=/tmp/statqed-sq0003-elan PATH=/tmp/statqed-sq0003-elan/bin:/usr/bin:/bin MATHLIB_NO_CACHE_ON_UPDATE=1 LAKE_NO_CACHE=1 lake update --keep-toolchain
ELAN_HOME=/tmp/statqed-sq0003-elan PATH=/tmp/statqed-sq0003-elan/bin:/usr/bin:/bin MATHLIB_NO_CACHE_ON_UPDATE=1 LAKE_NO_CACHE=1 lake build
```

The tested cache path is Mathlib's post-update `lake exe cache get` hook triggered by the first recommended `lake update`. It contacted `https://lakecache.blob.core.windows.net/mathlib4-master` and attempted 8,639 artifacts. It requires the network and is a performance path, not a semantic authority. A cache miss must fall back to the same locked-source build, never normalize an unexplained recommended-pin failure to success. A future hardening probe should separately test the current cache tool's explicit per-commit `--scope` option before making that option normative in bootstrap scripts.

## Proposed CI entries

- Required pull-request job: Ubuntu x86_64, exact Lean/Mathlib lock, dependency resolution, cached build, prototype/test build, and actual `#print axioms` output comparison that rejects `sorryAx` and unexpected axiom-set changes.
- Required clean-lock job: regenerate the prototype manifest in a fresh directory and compare every resolved revision with the committed lock.
- Scheduled/manual source job: Ubuntu x86_64 with `MATHLIB_NO_CACHE_ON_UPDATE=1` and `LAKE_NO_CACHE=1`; this directly tested build took about ten minutes after resolution.
- Required mutation test: reject a modified toolchain/Mathlib pair; the preserved `v4.31.0`/`v4.32.1` mismatch is a concrete fixture.
- Future platform jobs before support is claimed: macOS arm64 and Windows x86_64 on the exact pair, plus any other platform chosen by the repository. No result in this prototype supports a current macOS, Windows, arm64, musl, or container-image claim.

## Trust and maintenance notes

- Lean 4, Lake, Mathlib, and Elan are actively maintained upstream as of the evidence date, but Lean's official release notes say compatibility can break across regular releases. Update the exact pair together.
- Lean 4/Lake and Mathlib are Apache-2.0. Elan publishes Apache-2.0 and MIT license files. This is source-level license inventory, not legal advice.
- Mutable registries, GitHub, release services, and binary caches are network/supply-chain inputs. The committed full git revision and Lake manifest are required for reproduction. Archive verification must not depend on the network.
- A successful build and `#print axioms` establish only that this Lean proposition elaborates and has the reported transitive axiom dependencies in the locked environment. They do not establish source fidelity, statistical identification, external premises, or `.statqed` artifact binding.
- Update policy: test a candidate Lean release with the corresponding immutable Mathlib revision in both cache-assisted and cache-disabled modes; compare the actual axiom report; review migration changes; land Lean tag, Mathlib commit, and manifest atomically. Roll back all three to the last successful lock if any required probe fails.

## Primary sources retrieved 2026-08-03

- [Lean 4.32.1 official release notes](https://lean-lang.org/doc/reference/latest/releases/v4.32.1/)
- [Lean official releases](https://github.com/leanprover/lean4/releases)
- [Mathlib official releases](https://github.com/leanprover-community/mathlib4/releases)
- [Immutable Mathlib `lean-toolchain`](https://github.com/leanprover-community/mathlib4/blob/520045ab14e26149ee970e2e617ca04b09bde5d6/lean-toolchain)
- [Immutable Mathlib `lakefile.lean`](https://github.com/leanprover-community/mathlib4/blob/520045ab14e26149ee970e2e617ca04b09bde5d6/lakefile.lean)
- [Mathlib dependency and cache instructions](https://github.com/leanprover-community/mathlib4/wiki/Using-mathlib4-as-a-dependency)
- [Official Lake reference](https://lean-lang.org/doc/reference/latest/Build-Tools-and-Distribution/Lake/)
- [Official Elan reference](https://lean-lang.org/doc/reference/latest/Build-Tools-and-Distribution/Managing-Toolchains-with-Elan/)
- [Elan v4.2.3 release](https://github.com/leanprover/elan/releases/tag/v4.2.3)
- [Lean license](https://github.com/leanprover/lean4/blob/f054605aea4b840552cca2e725580bffd1e1b704/LICENSE)
- [Mathlib license](https://github.com/leanprover-community/mathlib4/blob/520045ab14e26149ee970e2e617ca04b09bde5d6/LICENSE)

Generated dependency trees and build products were removed. Exact source, manifests, hashes, stdout, stderr, and failure evidence remain versioned here.
