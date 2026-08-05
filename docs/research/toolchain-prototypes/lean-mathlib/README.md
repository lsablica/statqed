# Lean / Mathlib / Lake compatibility prototype

Status: **Draft research evidence**.

Evidence dates: 2026-08-03 and currentness rerun 2026-08-05. Directly tested only on Ubuntu 24.04.4 LTS, Linux 7.0.0-28-generic, x86_64, `C.UTF-8`. This prototype neither initializes `lean/` nor claims artifact-level kernel verification.

## Recommendation

Use this exact development pair for SQ-0003:

- Lean release/channel file: `leanprover/lean4:v4.32.2`;
- Lean release commit reported by the installed binary: `f3b06c705e6c85f5314019d5d3baab0fec5b580c`;
- Mathlib immutable git revision: `905b95818eb32af7874a58b427f50c1711a5e96c` (also tagged `v4.32.2`);
- Lake: the version bundled with that Lean release, `5.0.0-src+f3b06c7` (Lean `4.32.2`), not an independently floating Lake installation;
- tested toolchain manager for bootstrapping: elan `4.2.3` (`b6cec7e10`, archive SHA-256 `df0b2b3a439961ffcbb3985214365ffe40f49bc871df04dff268c7d8e21ca8b2`). Elan is installation provenance, not part of the mathematical theorem lock.

The Lean release tag and Mathlib commit are deliberately distinct identifiers. Matching version text does not establish compatibility; the cache-assisted and cache-disabled builds below use the full immutable revisions.

An independent minimum Lean support floor is not meaningful for one frozen Mathlib revision. Mathlib's immutable `lakefile.lean` sets `fixedToolchain := true` and its `lean-toolchain` selects Lean `v4.32.2`. The permanent `rejected-lean-4.32.1-mathlib-4.32.2/` control rejects a root selecting adjacent Lean `v4.32.1` even though dependency resolution can complete. StatQED should support the exact environment lock, not a Lean range. The older `v4.31.0`/Mathlib `v4.32.1` compiler failure remains preserved separately as historical negative evidence.

## Results

| Probe | Cache/network mode | Result |
|---|---|---|
| `recommended/` | Fresh dependency resolution, then Mathlib's official binary-cache executable | Success; the first `mathlib4-master` lookup found no artifacts, the `mathlib4` fallback downloaded and decompressed all 8,639 artifacts |
| `recommended/` | Cached `lake build` plus `lake env lean` | Success; imported `Mathlib.Probability.ProbabilityMassFunction.Basic` and printed the exact expected axiom set |
| `no-binary-cache/` | Fresh dependency resolution with `MATHLIB_NO_CACHE_ON_UPDATE=1` and `LAKE_NO_CACHE=1` | Success; committed manifest matches the independently regenerated manifest |
| `no-binary-cache/` | Fresh source build with both variables set | Success, 1,710 jobs; completed 2026-08-05 20:12:29+02:00 |
| `rejected-lean-4.32.1-mathlib-4.32.2/` | Fresh no-cache resolution | Expected policy rejection: root toolchain `v4.32.1` differs from Mathlib's immutable required `v4.32.2` |
| altered manifest | Disposable copy with the Mathlib revision changed | Expected rejection: byte comparison differs from the reviewed regenerated manifest |

The reviewed manifest SHA-256 values are:

- `recommended/lake-manifest.json`: `ff2ecf31ced1cb1cff770a54d281c92a9c6bd9fa3826b243eac4dac2d5dca93f`;
- `no-binary-cache/lake-manifest.json`: `0dc9be6725815434799a9ed732f335924ac4daf6f9ff38c59bae4ed2cd8be73c`;
- `rejected-lean-4.32.1-mathlib-4.32.2/lake-manifest.json`: `0a30181171c157d4034b6e286b30dc79420c39d2010f4ff25940bb1369393637`.

The successful axiom inspection is exactly:

```text
'StatQEDLeanProbe.pmf_total_mass' depends on axioms: [propext, Classical.choice, Quot.sound]
```

The no-binary-cache namespace produces the same set. Neither successful result contains `sorryAx`. Three rejected 2026-08-03 proof bodies did report `sorryAx` because elaboration failed; those failures remain in `../logs/lean/stderr.log` and are not accepted proof evidence.

## Exact rerun commands

The following uses a task-specific isolated Elan directory. Replace `<repo>` with the checkout root. Network access is required for the toolchain and first dependency resolution. Generated `.lake` trees are intentionally not committed.

```bash
ELAN_HOME=/tmp/statqed-sq0003-elan <elan-4.2.3-extracted>/elan-init -y --no-modify-path --default-toolchain none
ELAN_HOME=/tmp/statqed-sq0003-elan /tmp/statqed-sq0003-elan/bin/elan toolchain install leanprover/lean4:v4.32.2
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
ELAN_HOME=/tmp/statqed-sq0003-elan PATH=/tmp/statqed-sq0003-elan/bin:/usr/bin:/bin MATHLIB_NO_CACHE_ON_UPDATE=1 LAKE_NO_CACHE=1 lake env lean StatQEDLeanNoBinaryCacheProbe.lean
```

The owned verifier always copies a fixture to a disposable `/tmp/statqed-sq0002-lean-probe.*` directory, regenerates its manifest, compares it with the reviewed manifest, and removes the generated tree. It requires an explicitly prepared Elan home and returns status 77 when that preparation is absent:

```bash
STATQED_LEAN_ELAN_HOME=/tmp/statqed-sq0003-elan ./verify-probe.sh recommended
STATQED_LEAN_ELAN_HOME=/tmp/statqed-sq0003-elan ./verify-probe.sh no-binary-cache
STATQED_LEAN_ELAN_HOME=/tmp/statqed-sq0003-elan ./verify-probe.sh mismatch
./verify-probe.sh static
```

The cache requires the network and is a performance path, not a semantic authority. The tested cache client first queried `https://lakecache.blob.core.windows.net/mathlib4-master` and observed zero matches, then automatically fell back to `https://lakecache.blob.core.windows.net/mathlib4` and obtained all 8,639 files. A cache miss must fall back to the same locked-source build; it must never normalize an unexplained recommended-pin failure to success.

## Proposed CI entries

- Required pull-request job: Ubuntu x86_64, exact Lean/Mathlib lock, dependency resolution, cached build, prototype/test build, and exact `#print axioms` comparison rejecting `sorryAx` and unexpected axiom-set changes.
- Required clean-lock job: regenerate the manifest in a fresh directory and compare every resolved revision with the committed lock.
- Scheduled/manual source job: Ubuntu x86_64 with `MATHLIB_NO_CACHE_ON_UPDATE=1` and `LAKE_NO_CACHE=1`.
- Required mutation jobs: reject both the adjacent root-toolchain/Mathlib mismatch and an altered manifest.
- Future platform jobs before support is claimed: macOS arm64 and Windows x86_64 on the exact pair, plus any other platform selected by the project. This prototype does not support a current macOS, Windows, arm64, musl, or container-image claim.

## Trust and maintenance notes

- Lean 4, Lake, Mathlib, and Elan were actively maintained at the evidence dates, but Lean's official release notes say compatibility can break across regular releases. Update the exact pair together.
- Lean 4/Lake and Mathlib are Apache-2.0. Elan publishes Apache-2.0 and MIT license files. This is a source-level inventory, not legal advice.
- Mutable registries, GitHub, release services, and binary caches are network/supply-chain inputs. The full revisions and reviewed manifest are required for reproduction. Archive verification must not depend on the network.
- A successful build and `#print axioms` establish only that this Lean proposition elaborates and has the reported transitive axiom dependencies in the locked environment. They do not establish source fidelity, statistical identification, external premises, or `.statqed` artifact binding.
- Update policy: test a candidate Lean release with its corresponding immutable Mathlib revision in cache-assisted and cache-disabled modes; compare regenerated manifests and the actual axiom report; review migration changes; land Lean tag, Mathlib commit, and manifest atomically. Roll back all three to the last successful lock if any required probe fails.

## Primary sources retrieved 2026-08-05

- [Lean 4.32.2 official release notes](https://lean-lang.org/doc/reference/latest/releases/v4.32.2/)
- [Lean official releases](https://github.com/leanprover/lean4/releases)
- [Mathlib official releases](https://github.com/leanprover-community/mathlib4/releases)
- [Immutable Mathlib `lean-toolchain`](https://github.com/leanprover-community/mathlib4/blob/905b95818eb32af7874a58b427f50c1711a5e96c/lean-toolchain)
- [Immutable Mathlib `lakefile.lean`](https://github.com/leanprover-community/mathlib4/blob/905b95818eb32af7874a58b427f50c1711a5e96c/lakefile.lean)
- [Mathlib dependency and cache instructions](https://github.com/leanprover-community/mathlib4/wiki/Using-mathlib4-as-a-dependency)
- [Official Lake reference](https://lean-lang.org/doc/reference/latest/Build-Tools-and-Distribution/Lake/)
- [Official Elan reference](https://lean-lang.org/doc/reference/latest/Build-Tools-and-Distribution/Managing-Toolchains-with-Elan/)
- [Elan v4.2.3 release](https://github.com/leanprover/elan/releases/tag/v4.2.3)
- [Lean license](https://github.com/leanprover/lean4/blob/f3b06c705e6c85f5314019d5d3baab0fec5b580c/LICENSE)
- [Mathlib license](https://github.com/leanprover-community/mathlib4/blob/905b95818eb32af7874a58b427f50c1711a5e96c/LICENSE)

Generated dependency trees and build products were removed after testing. Exact sources, reviewed manifests, hashes, stdout, stderr, and negative-control evidence remain versioned here.
