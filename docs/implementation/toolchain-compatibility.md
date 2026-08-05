# SQ-0002 toolchain compatibility

Status: **Experimental**. Source and recommendation cutoff: 2026-08-05.

This report recommends research pins for SQ-0003 and SQ-0004. It initializes
no production toolchain, accepts no RFC, defines no canonical bytes or logical
data, reserves no package name, and claims no untested platform. Runtimes,
package managers, registries, caches, solvers, report generators, and agents
remain outside the trusted computing base.

Matrix SHA-256: `sha256:71b6c85ff75f130f37c762e45d19c9c7757b2579e3e64221031ebabff238a78e`

## Recommendation and CI summary

All direct execution used the same physical host: Ubuntu 24.04.4 LTS, Linux
7.0.0-28-generic, glibc 2.39, x86_64, `C.UTF-8`, no container or hosted runner.
The matrix names that environment on every direct attempt. The proposed CI
anchors reproduce the Linux x86-64 endpoints; macOS arm64, Windows x86-64,
and Linux arm64 entries are planned validation only. SQ-0003/SQ-0004 must
record the exact hosted-runner image version or immutable container digest when
workflows are authorized; a mutable `*-latest` label is not support evidence.

| Component and role | Development/reference pin | Support floor | Proposed CI |
|---|---|---|---|
| Lean/Mathlib/Lake, proof-backend bootstrap | Lean 4.32.2 commit `f3b06c705e6c85f5314019d5d3baab0fec5b580c`; Mathlib `905b95818eb32af7874a58b427f50c1711a5e96c`; bundled Lake `5.0.0-src+f3b06c7` | exact pair only | Linux cached and no-cache; macOS/Windows planned |
| Rust/Cargo, operational-backend bootstrap | Rust 1.97.1, rustc `8bab26f4f68e0e26f0bb7960be334d5b520ea452`, Cargo `c980f4866141969fab6254a680546a277789d6f0` | compatibility-only Rust 1.85.1, rustc `4eb161250e340c8f48f66e2b929ef4a5bed7c181`, Cargo `d73d2caf9e41a39daf2a8d6ce60ec80bf354d2a7` | Linux dev/MSRV; Linux arm64, macOS, Windows planned |
| Python thin frontend | CPython 3.14.7; tested python-build-standalone 20260805 target `76b41240bc8dfe753a54b2e32c8941e536568be8` | Python `>=3.11`; exact patch 3.11.15 | Linux 3.14/3.11; 3.12/3.13 and other OSes planned |
| R thin frontend | R 4.6.1/testthat 3.3.2 | `R >=4.4.0`; exact patch R 4.4.3/testthat 3.2.3 | Linux dev/floor; macOS/Windows planned |
| Julia thin frontend | Julia 1.12.6 | maintained LTS policy; exact LTS 1.10.11 | Linux Stable/LTS; macOS/Windows planned |
| Arrow transport experiment | PyArrow/Arrow C++ 25.0.0 and arrow-rs 59.1.0 | none; experimental candidate | Linux differential only |
| CBOR encoding experiment | cbor2 6.1.4 current narrow probe; cbor2 6.1.3, ciborium 0.2.2, minicbor 2.3.0 historical broad differential | none; experimental candidates | Linux differential only |
| CDDL shape-tool experiment | cddl 0.10.6 on Rust 1.97.1 | none; requires Rust 1.88 and fails the proposed MSRV | isolated Linux tool experiment only |

Development pins, support floors, CI coverage, experimental candidates, and
publication requirements are distinct decisions. Python 3.11, R 4.4, and
Julia LTS are project support policies; they do not claim upstream security
support. The Rust 1.85.1 job is compiler compatibility only and must not fetch
with credentials or third-party registries.

## Lean, Mathlib, Lake, and Elan

- **Primary sources and retrieval.** Official Lean and Mathlib v4.32.2 release
  records, immutable repository blobs, Lake reference, Mathlib dependency/cache
  guidance, and Elan release data were retrieved 2026-08-05. Exact locators and
  timestamps are the `official-lean-4.32.2`, `official-mathlib-v4.32.2`,
  `immutable-mathlib-4.32.2-lean-toolchain`, and related matrix source records.
- **Install/version evidence.** The preparation command installs exact Elan
  4.2.3 and `leanprover/lean4:v4.32.2`; `lean --version` reported commit
  `f3b06c7…`, and `lake --version` reported `5.0.0-src+f3b06c7`. The owned
  commands are `/usr/bin/bash verify-probe.sh recommended` and
  `/usr/bin/bash verify-probe.sh no-binary-cache` from `lean-mathlib/`.
- **Result.** Immutable normal resolution and a separate cache-disabled source
  build both completed all 1,710 jobs, imported the probability module, and
  byte-matched the reviewed manifests. `#print axioms` returned exactly
  `[propext, Classical.choice, Quot.sound]`; no `sorryAx` appeared.
- **Network/cache/license/security.** Preparation needs official release,
  GitHub/Reservoir, and optional Mathlib cache access. The no-cache build is a
  separate anchor. Lean, Mathlib, and Lake are Apache-2.0; Elan is MIT OR
  Apache-2.0 and is a bootstrap tool, not proof authority.
- **Rejected/unknown.** Lean 4.31 with newer Mathlib, Lean 4.32.1 with Mathlib
  4.32.2, stale cache state, incomplete clones, and `sorryAx` mutations are
  retained. Only Linux x86-64 was run. SQ-0003 must copy the exact pair and
  reviewed manifest direction, rerun both cache modes and axiom inspection,
  and preserve the mismatch fixture. Rollback restores the prior reviewed
  commits and manifests together; matching release names are never inferred.

## Rust and Cargo

- **Primary sources and retrieval.** Official Rust 1.97.1/1.85.1 releases,
  Cargo resolver/MSRV references, target tiers, crates.io records, RustSec, and
  Rust security advisories were refreshed 2026-08-05. Source IDs include
  `rust-release-1.97.1`, `rust-release-1.85.1`, `cargo-cve-2026-5222`,
  `cargo-cve-2026-5223`, and `rust-release-1.96.1-libssh2-security`.
- **Install/version evidence.** Exact rustup commands install 1.97.1 and 1.85.1
  with rustfmt and Clippy. `rustc -Vv`, `cargo -V`, host and target triples are
  retained. Owned commands are `/usr/bin/bash verify-probe.sh development` and
  `... msrv` from `rust/`.
- **Result.** The same `Cargo.lock`, SHA-256
  `993f587b7dee5a7e18bff312ae76ac7ab84031ccc771b5e9789915d2bfd3883b`,
  passed locked/offline metadata, `cargo fmt --check`, Clippy with warnings
  denied, tests, and runtime smoke on both pins. `#![forbid(unsafe_code)]` and
  an unsafe mutation were exercised. Candidate Arrow, archive, digest, JSON,
  and CLI libraries are compatibility observations, not production choices.
- **Network/cache/license/security.** Current patched Cargo performs the exact
  crates.io-only fetch; the 1.85 job is isolated, uncredentialed, and offline.
  Cargo 1.85.1 is in the affected ranges for the named credential/symlink
  advisories and must not be an acquisition or release tool. cargo-audit 0.22.2
  against immutable RustSec commit `d91a8fc…` returned zero findings for 128
  locked packages at that instant. The normalized license inventory is
  retained; Rust tooling and most core candidates are MIT/Apache-2.0, with
  exact per-package licenses in `dependency-license-inventory.json`.
- **Rejected/unknown and policy.** zip 8.1.0 and cddl 0.10.6 fail the MSRV;
  resolver drift and cache failures are retained. SQ-0004 must use Edition
  2024/resolver 3, the exact dev pin and compatibility floor, current Cargo for
  acquisition, `forbid(unsafe_code)`, and the four package gates. Rollback
  restores the reviewed pin and lock atomically. No non-Linux target was run.

## Python

- **Primary sources and retrieval.** The PSF 3.14.7 and 3.11.15 release pages,
  supported-versions/security policy, packaging flow, Astral releases, and uv
  0.11.32 were retrieved 2026-08-05. Source IDs are
  `python-release-v3.14.7`, `python-release-v3.13.15`,
  `python-release-v3.12.13`, `python-release-v3.11.15`,
  `python-build-standalone-20260805`, and `python-packaging-flow`.
- **Immutable assets/version evidence.** Development archive SHA-256 is
  `a3a4e4b81b138960c7c546694df8a77578c0b6aa46d47e96f49b9e10e8f860c9`;
  floor archive SHA-256 is
  `23ccae6f1ff73e8aa8378436f869da003b8eb7d6c95f2bc706f494115ba1447d`;
  uv binary SHA-256 is
  `da15297d6879b2cfbe5ea3cb03725c1613d51ba72892cc996468d871f0a532fb`.
  Exact versions reported Python 3.14.7/3.11.15, pip 26.2, build 1.5.0,
  Hatchling 1.31.0, and pytest 9.1.1.
- **Install/prototype/result.** After downloading those exact assets and the
  hash-locked wheelhouse, run `/usr/bin/bash verify-probe.sh development` and
  `... floor` from `python/`. Each fresh offline run built sdist/wheel through
  PEP 517, installed separately, passed `pip check`, two tests, and metadata.
  The wheel/sdist digests agreed across endpoints. Python 3.10.20 was rejected
  by `Requires-Python >=3.11`; Python 3.14.6 remains superseded history.
- **Network/cache/license/security.** Preparation is networked and
  checksum-gated; execution uses fresh HOME/XDG/caches and `PIP_NO_INDEX=1`.
  CPython is PSF-2.0; python-build-standalone is MPL-2.0 with bundled notices;
  uv is MIT OR Apache-2.0. The OSV 2026-08-05 point-in-time query returned no
  vulnerability records for 12 exact packages, not a security guarantee.
- **Unknown/update/rollback.** Exact planned intermediate CI patches 3.12.13
  and 3.13.15, plus macOS, Windows, and ARM, are untested. SQ-0014 must test
  every supported minor and exact platform asset.
  Advance patch pins only with refreshed sources, hashes, lock, positive and
  floor-rejection tests; rollback restores the reviewed runtime asset and
  universal hash lock.

## R

- **Primary sources and retrieval.** Official R 4.6.1 and 4.4.3 releases,
  Writing R Extensions, CRAN policy, R SDLC, and testthat records were refreshed
  2026-08-05 (`r-release-4.6.1`, `r-release-4.4.3`, and related source IDs).
- **Install/version/prototype.** Development uses R 4.6.1/testthat 3.3.2 and a
  24-package CRAN/Archive URL+SHA-256 source lock, SHA-256
  `34578de2ad22a24e2ffb1f5584731618f9862a1a063623b6c5523a635a5f9721`.
  Floor uses exact R 4.4.3/testthat 3.2.3 and a 123-artifact conda explicit
  URL+SHA-256 lock. Owned commands are `/usr/bin/bash verify-probe.sh
  development` and `... floor` from `r/`; both run `R CMD build`, built-tarball
  `R CMD check --no-manual`, install, `testthat`, and installed smoke.
- **Result/cache.** Both endpoints produced `Status: OK`, five passing
  expectations, and smoke success. Development installs the locked source
  closure into a fresh library; no host library is copied. Floor recreates a
  fresh prefix offline from the exact retained artifacts. A conda 4.6.1 solve
  gap and `R >=4.7` mutation remain failures.
- **License/security/unknown.** R is GPL-2 | GPL-3; the prototype/testthat are
  MIT; dependency licenses are retained in inventory evidence. The OSV
  2026-08-05 query returned no records for 29 exact CRAN package/version pairs,
  a point-in-time observation only. macOS and Windows are untested. Update
  requires exact sources/locks and built-tarball checks on every claimed
  platform; rollback restores the previous runtime and dependency inventories.

## Julia and Pkg

- **Primary sources and retrieval.** Official Julia release/support, Pkg,
  registry, license, and security sources were retrieved 2026-08-03 and checked
  current on 2026-08-05. Exact source IDs include `julia-release-v1.12.6`,
  `julia-release-v1.10.11`, and `julia-support-policy`.
- **Immutable assets/version evidence.** Official Linux x86-64 archives are
  `https://julialang-s3.julialang.org/bin/linux/x64/1.12/julia-1.12.6-linux-x86_64.tar.gz`
  (SHA-256 `bbabf3bef19421a9dbd24a767d807606ab85e444323b5a1c73ffe293fa3d079a`)
  and the analogous `/1.10/julia-1.10.11-linux-x86_64.tar.gz`
  (SHA-256 `fb49c6b174600cd2051e37ba3f7330f8acf06dd00bce609bab6611387fdb37bf`).
  Version output reported 1.12.6/1.10.11.
- **Prototype/result.** Run `/usr/bin/bash verify-probe.sh development` and
  `... floor` from `julia/`. Fresh offline depots use a fixed empty registry
  sentinel, resolve, instantiate, strictly precompile, test, and report status.
  Generated manifests must byte-match retained locks: 1.12.6 SHA-256
  `52c13c02e7b2fa2500c742aaf63923bb66baca177e1945909b27eafc5456fdb1`
  and 1.10.11 SHA-256
  `44d6bb77fbd18006cb248017b6465f02fa47a733bdea158ca3e2b3172faee480`.
  A Julia 1.13 compat mutation is rejected.
- **Cache/license/unknown.** Earlier empty-depot attempts tried to bootstrap
  mutable General and remain failures. Corrected runs use no registry package
  or network. Julia source is MIT; official binaries aggregate bundled
  licenses. macOS, Windows, ARM, General-registry publication, and external
  dependencies are untested. Update follows maintained Stable/LTS with fresh
  locks; rollback restores both exact archive and reviewed manifest.

## Arrow interoperability boundary

- **Primary sources/pins.** Apache Arrow 25.0.0 release, format versioning,
  implementation status, security guidance, PyArrow, and arrow-rs policies were
  retrieved 2026-08-03 and refreshed 2026-08-05. Exact candidates are PyArrow
  25.0.0/Arrow C++ 25.0.0 and arrow-rs 59.1.0.
- **Immutable/install evidence.** CPython 3.14.7 and uv assets are the Python
  pins above; PyArrow wheel SHA-256 is
  `447df764beb07c544f0178a5f6b70ef44b9ecf382b3cdfad4c2d7867353c3887`;
  Arrow `Cargo.lock` SHA-256 is
  `b48ca90c270c065266d625e8d26a024217ac1559247d530de6b9348969bedaed`.
  After exact asset preparation run `/usr/bin/bash verify-probe.sh` in
  `arrow/`; installation is offline and hash-locked.
- **Result.** Both lineages self-round-tripped and cross-read the complete
  tested Int64/Utf8/Binary schema, values, nulls, Unicode sequence, and bytes.
  A same-schema altered-value control failed with the expected `2002`
  differential; a magic-only file was rejected. Same-process repeat writes
  matched while file and stream bytes differed. This is transport observation,
  not canonicalization or logical identity.
- **License/security/unknown.** Arrow implementations are Apache-2.0 with
  third-party notices; official guidance requires validation of untrusted
  inputs. R Arrow, Arrow.jl, macOS, Windows, ARM, resource bounds, and parser
  safety remain untested. SQ-0004 may retain these as optional candidates only;
  RFC-0006 stays Draft. Rollback removes them because no production dependency
  or semantic commitment exists.

## CBOR and CDDL boundary

- **Primary sources/pins.** RFC 8949, RFC 8610, RFC 9682, the current CDDL
  modules draft, official package records, release histories, repositories,
  licenses, and advisories were retrieved 2026-08-03 and refreshed 2026-08-05.
  Current cbor2 6.1.4 uses exact wheel SHA-256
  `c0f5f2d6d3b58e44146860c049f3c082207a4005588b8926d51bf937ab66773c`
  and requirements-lock SHA-256
  `547717250bbd70c0857bedfd3a0ab7ddf8f78e86f1b0c523b5dc6ed510de7667`.
- **Prototype/result.** `/usr/bin/bash verify-cbor2-6.1.4.sh` confirms four
  focused regressions on CPython 3.14.7: incomplete indefinite map and non-byte
  bignum rejection, distinct tested adversarial hashes, and bytearray string
  reference round-trip. Broader map-order, duplicate, indefinite, nesting,
  break, and truncation observations remain from cbor2 6.1.3 with ciborium
  0.2.2/minicbor 2.3.0; they are not relabeled as 6.1.4 results.
- **CDDL result.** `cargo install cddl --version 0.10.6 --locked` on Rust
  1.97.1 checked shape and accepted both tested deterministic orderings. Its
  published graph requires Rust 1.88; the exact 1.85.1 check fails. CDDL does
  not select bytes. Archived `serde_cbor` is rejected.
- **License/security/unknown.** cbor2 is MIT and states malicious-input testing
  has not been performed; ciborium is Apache-2.0; minicbor is BlueOak-1.0.0;
  cddl is MIT. Duplicate handling and permissive inputs differ. Future work
  needs a strict pre-lossy validator, limits, independently originated oracle,
  license/advisory review, and all claimed platforms. RFC-0001 stays Draft;
  no encoding, decoder profile, logical data, or artifact semantics are frozen.

## Update, rollback, publication, and downstream instructions

Every update must re-query primary sources, replace mutable discovery with
exact releases/commits/digests, preserve failed candidates, run fresh positive,
negative, malformed, corruption, support-floor, and cache-independent probes,
compare generated locks, review licenses/advisories, and obtain independent
integration approval. Rollback restores the complete previous reviewed pin and
lock set. Cache success, a moving tag, or registry re-resolution cannot replace
those bytes.

SQ-0003 may initialize only its contracted Lean production paths with the exact
Lean/Mathlib pair above. SQ-0004 may initialize only its contracted Rust paths
with the exact Rust dev/MSRV split, current-Cargo acquisition policy, and
unsafe/fmt/Clippy/test/security gates. Neither may import experimental
Arrow/CBOR/CDDL behavior into normative semantics. Python/R/Julia publication
names, platform wheels/binaries, registries, and package topology remain later
tasks; this report makes no reservation or publication approval.

## Exact command index

Preparation commands below are networked only where stated; each owned probe
then verifies immutable inputs and creates disposable state. Full argv arrays,
environment variables, timestamps, stdout, and stderr are in `matrix.json`.

| Component | Exact installation/preparation command | Version command and retained output | Exact owned prototype command and result |
|---|---|---|---|
| Lean | `elan toolchain install leanprover/lean4:v4.32.2` after Elan 4.2.3 archive verification | `lean --version` → `Lean 4.32.2 (f3b06c7…, Release)`; `lake --version` → `5.0.0-src+f3b06c7` | `/usr/bin/bash verify-probe.sh recommended` and `... no-binary-cache` in `lean-mathlib/` → both exit 0 |
| Rust | `rustup toolchain install 1.97.1 --profile minimal --component rustfmt --component clippy` and the same for `1.85.1` | `rustc -Vv`/`cargo -V` → commits `8bab26f…`/`c980f48…` and `4eb1612…`/`d73d2ca…` | `/usr/bin/bash verify-probe.sh development` and `... msrv` in `rust/` → both exit 0 |
| Python | verify and extract the named python-build-standalone archives; use uv binary SHA-256 `da15297…` and the checked-in hash lock | `python --version` → `3.14.7` and `3.11.15`; tool snapshot retained | `/usr/bin/bash verify-probe.sh development` and `... floor` in `python/` → both exit 0 |
| R | development installs all `development-cran-source-lock.tsv` archives with `R CMD INSTALL`; floor runs `conda create --offline --yes --prefix <fresh> --file <local-explicit-lock>` | `R --version` → `4.6.1` and `4.4.3`; testthat → `3.3.2` and `3.2.3` | `/usr/bin/bash verify-probe.sh development` and `... floor` in `r/` → both exit 0 |
| Julia | verify the two official archive hashes and extract with `/usr/bin/tar --extract --gzip --file <archive> --directory <fresh>` | `julia --version` → `1.12.6` and `1.10.11` | `/usr/bin/bash verify-probe.sh development` and `... floor` in `julia/` → both package-native runs exit 0 and match retained manifests |
| Arrow | verify/extract CPython, verify PyArrow wheel `447df764…`, and use Cargo lock `b48ca90c…` with the prepared offline registry cache | version output → Python `3.14.7`, PyArrow/C++ `25.0.0`, rustc/Cargo `1.97.1`, arrow-rs `59.1.0` | `/usr/bin/bash verify-probe.sh` in `arrow/` → exit 0, cross-lineage positive/altered/malformed controls pass |
| cbor2 | verify/extract CPython and install cbor2 wheel `c0f5f2d6…` with `uv pip install --no-index --require-hashes` | `importlib.metadata.version("cbor2")` → `6.1.4` | `/usr/bin/bash verify-cbor2-6.1.4.sh` in `cbor-cddl/` → exit 0, four focused regressions pass |
| CDDL | `cargo install cddl --version 0.10.6 --locked --root <fresh>` on Rust 1.97.1 | `cddl --version` → `cddl 0.10.6` | historical hash-bound `run-probes.sh` → development exit 0; Rust 1.85.1 locked check exits 101 and is rejected |

## Complete attempted-combination inventory

The builder inserts every success, expected failure, ordinary failure, and
unavailable combination from `matrix.json` here. Failures are retained rather
than erased when a later candidate succeeds.

<!-- SQ0002_ATTEMPTS_BEGIN -->
| Probe | Class | Disposition | Result and retained evidence |
|---|---|---|---|
| `arrow-host-python-venv-missing` | failure | rejected | The host Python lacked ensurepip/python3-venv; the attempt was preserved and replaced by the already-reviewed isolated CPython runtime plus uv. Logs: `docs/research/toolchain-prototypes/logs/arrow/arrow-host-python-venv-missing.stdout.log`, `docs/research/toolchain-prototypes/logs/arrow/arrow-host-python-venv-missing.stderr.log`. |
| `arrow-julia-host-command-unavailable` | unknown | unresolved | No julia command was on PATH. This is not Arrow.jl evidence because separate exact Julia runtimes existed outside PATH and no Arrow.jl environment was prepared. Logs: `docs/research/toolchain-prototypes/logs/arrow/arrow-julia-host-command-unavailable.stdout.log`, `docs/research/toolchain-prototypes/logs/arrow/arrow-julia-host-command-unavailable.stderr.log`. |
| `arrow-pyarrow25-arrow-rs59-cross-lineage-hardened` | success | recommended | The exact current Python and Rust candidates passed self-round-trips, complete schema/value/null cross-reads in both directions, same-schema altered-value rejection with the expected differential, repeat-write observation, and malformed magic-only rejection. This recommends only further experimental evaluation; it does not define logical identity, canonical bytes, or RFC-0006 semantics. Logs: `docs/research/toolchain-prototypes/logs/arrow/arrow-pyarrow25-arrow-rs59-cross-lineage-hardened.stdout.log`, `docs/research/toolchain-prototypes/logs/arrow/arrow-pyarrow25-arrow-rs59-cross-lineage-hardened.stderr.log`. |
| `arrow-pyarrow25-arrow-rs59-cross-lineage-hash-bound` | success | unresolved | Exact hash-bound preparation succeeded. Both independent code lineages self-round-tripped the narrow typed subset, cross-read IPC files, observed same-process repeatability but unequal file/stream bytes, and rejected a minimized magic-only file. This is transport compatibility evidence only. Logs: `docs/research/toolchain-prototypes/logs/arrow/arrow-pyarrow25-arrow-rs59-cross-lineage-hash-bound.stdout.log`, `docs/research/toolchain-prototypes/logs/arrow/arrow-pyarrow25-arrow-rs59-cross-lineage-hash-bound.stderr.log`. |
| `arrow-pyarrow25-arrow-rs59-cross-lineage-unbound` | success | rejected | Typed self-round-trips, cross-lineage IPC reads, repeatability observations, and malformed rejection passed, but the wheel was not hash-bound and the proposed runtimes were not used; this evidence is superseded. Logs: `docs/research/toolchain-prototypes/logs/arrow/arrow-pyarrow25-arrow-rs59-cross-lineage.stdout.log`, `docs/research/toolchain-prototypes/logs/arrow/arrow-pyarrow25-arrow-rs59-cross-lineage.stderr.log`. |
| `arrow-r-package-unavailable` | unknown | unresolved | R was runnable but the Arrow package was absent; no R Arrow import, table, or IPC behavior was tested. Logs: `docs/research/toolchain-prototypes/logs/arrow/arrow-r-package-unavailable.stdout.log`, `docs/research/toolchain-prototypes/logs/arrow/arrow-r-package-unavailable.stderr.log`. |
| `cbor-cddl-full-dev-rust-unbound` | success | rejected | Differential map-order, duplicate, indefinite, depth, malformed, and CDDL shape tests ran, but the wheel was not hash-bound, proposed runtimes were not used, and the cddl install graph was not retained. Superseded by the final run. Logs: `docs/research/toolchain-prototypes/logs/cbor-cddl/cbor-cddl-full-dev-rust.stdout.log`, `docs/research/toolchain-prototypes/logs/cbor-cddl/cbor-cddl-full-dev-rust.stderr.log`. |
| `cbor-libraries-final-hash-bound` | success | unresolved | Hash-bound differential and malformed probes completed. cbor2 and ciborium matched length-first order; minicbor exposed insertion-order control. Duplicate and indefinite behavior differed or was permissive, tested nesting was accepted, and truncated arguments were rejected. Results require a future strict profile validator and do not recommend decoder semantics. Logs: `docs/research/toolchain-prototypes/logs/cbor-cddl/cbor-cddl-full-dev-rust-hash-bound.stdout.log`, `docs/research/toolchain-prototypes/logs/cbor-cddl/cbor-cddl-full-dev-rust-hash-bound.stderr.log`. |
| `cbor2-6.1.4-security-regressions` | success | unresolved | The exact current wheel rejected an incomplete indefinite map and a non-byte bignum, produced distinct hashes for the tested adversarial frozendict pairing, and round-tripped bytearray string references. This is narrow release-regression evidence, not a decoder-profile or canonical-byte decision. Logs: `docs/research/toolchain-prototypes/logs/cbor-cddl/cbor2-6.1.4-security-regressions.stdout.log`, `docs/research/toolchain-prototypes/logs/cbor-cddl/cbor2-6.1.4-security-regressions.stderr.log`. |
| `cbor2-break-assumption-failure` | failure | rejected | The probe incorrectly asserted that a top-level break byte must be rejected. cbor2 accepted it as an internal sentinel; the assumption was removed and the behavior retained as security-relevant evidence. Logs: `docs/research/toolchain-prototypes/logs/cbor-cddl/cbor2-break-assumption-failure.stdout.log`, `docs/research/toolchain-prototypes/logs/cbor-cddl/cbor2-break-assumption-failure.stderr.log`. |
| `cbor2-version-attribute-failure` | failure | rejected | cbor2 6.1.3 does not expose module __version__; the probe now uses importlib.metadata. Logs: `docs/research/toolchain-prototypes/logs/cbor-cddl/cbor2-version-attribute-failure.stdout.log`, `docs/research/toolchain-prototypes/logs/cbor-cddl/cbor2-version-attribute-failure.stderr.log`. |
| `cddl-0.10.6-rust-1.85.1-msrv-rejection` | failure | rejected | The checked-in lock was used with --locked. Cargo rejected cddl 0.10.6 and selected time packages because they require rustc 1.88.0. Logs: `docs/research/toolchain-prototypes/logs/cbor-cddl/cddl-0.10.6-rust-1.85.1-msrv-rejection.stdout.log`, `docs/research/toolchain-prototypes/logs/cbor-cddl/cddl-0.10.6-rust-1.85.1-msrv-rejection.stderr.log`. |
| `cddl-tool-final-hash-bound` | success | unresolved | The exact published --locked graph built on Rust 1.97.1. CDDL compiled and checked shape, rejected the wrong value type, and accepted both deterministic map-order byte variants. This supports only a conditional development shape tool; it does not canonicalize bytes and requires transitive license/advisory review. Logs: `docs/research/toolchain-prototypes/logs/cbor-cddl/cbor-cddl-full-dev-rust-hash-bound.stdout.log`, `docs/research/toolchain-prototypes/logs/cbor-cddl/cbor-cddl-full-dev-rust-hash-bound.stderr.log`. |
| `cran-osv-exact-lock-query` | success | unresolved | The official OSV batch API returned one aligned, unpaginated result per exact CRAN query and zero vulnerability records at the recorded 2026-08-05 query time. This covers only the selected prototype package lock and is not a security guarantee. Logs: `docs/research/toolchain-prototypes/logs/security/run-20260805/cran-osv.stdout.log`, `docs/research/toolchain-prototypes/logs/security/run-20260805/cran-osv.stderr.log`. |
| `development-julia-1-12-6-linux-x86-64-20260803t122700z` | failure | rejected | At least one package-native command failed; inspect command logs. Logs: `docs/research/toolchain-prototypes/logs/julia/run-20260803T122700Z/development-julia-1-12-6-linux-x86-64.stdout`, `docs/research/toolchain-prototypes/logs/julia/run-20260803T122700Z/development-julia-1-12-6-linux-x86-64.stderr`. |
| `development-julia-1-12-6-linux-x86-64-20260803t123100z` | failure | rejected | At least one package-native command failed; inspect command logs. Logs: `docs/research/toolchain-prototypes/logs/julia/run-20260803T123100Z/development-julia-1-12-6-linux-x86-64.stdout`, `docs/research/toolchain-prototypes/logs/julia/run-20260803T123100Z/development-julia-1-12-6-linux-x86-64.stderr`. |
| `development-julia-1-12-6-linux-x86-64-20260803t124500z` | success | recommended | Exact official runtime passed isolated offline Pkg instantiate, precompile, test, and status commands on the named host. Logs: `docs/research/toolchain-prototypes/logs/julia/run-20260803T124500Z/development-julia-1-12-6-linux-x86-64.stdout`, `docs/research/toolchain-prototypes/logs/julia/run-20260803T124500Z/development-julia-1-12-6-linux-x86-64.stderr`. |
| `development-julia-1-12-6-linux-x86-64-recovery-after-registry-bootstrap-failure-20260803t123700z` | failure | rejected | At least one package-native command failed; inspect command logs. Logs: `docs/research/toolchain-prototypes/logs/julia/run-20260803T123700Z/development-julia-1-12-6-linux-x86-64-recovery-after-registry-bootstrap-failure.stdout`, `docs/research/toolchain-prototypes/logs/julia/run-20260803T123700Z/development-julia-1-12-6-linux-x86-64-recovery-after-registry-bootstrap-failure.stderr`. |
| `elan-4.2.1-superseded` | success | rejected | A live updater notice and official latest-release API showed v4.2.3; stale v4.2.1 search evidence was rejected. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `floor-lts-julia-1-10-11-linux-x86-64-20260803t122700z` | failure | rejected | At least one package-native command failed; inspect command logs. Logs: `docs/research/toolchain-prototypes/logs/julia/run-20260803T122700Z/floor-lts-julia-1-10-11-linux-x86-64.stdout`, `docs/research/toolchain-prototypes/logs/julia/run-20260803T122700Z/floor-lts-julia-1-10-11-linux-x86-64.stderr`. |
| `floor-lts-julia-1-10-11-linux-x86-64-20260803t123100z` | failure | rejected | At least one package-native command failed; inspect command logs. Logs: `docs/research/toolchain-prototypes/logs/julia/run-20260803T123100Z/floor-lts-julia-1-10-11-linux-x86-64.stdout`, `docs/research/toolchain-prototypes/logs/julia/run-20260803T123100Z/floor-lts-julia-1-10-11-linux-x86-64.stderr`. |
| `floor-lts-julia-1-10-11-linux-x86-64-20260803t124500z` | success | recommended | Exact official runtime passed isolated offline Pkg instantiate, precompile, test, and status commands on the named host. Logs: `docs/research/toolchain-prototypes/logs/julia/run-20260803T124500Z/floor-lts-julia-1-10-11-linux-x86-64.stdout`, `docs/research/toolchain-prototypes/logs/julia/run-20260803T124500Z/floor-lts-julia-1-10-11-linux-x86-64.stderr`. |
| `floor-lts-julia-1-10-11-linux-x86-64-recovery-after-registry-bootstrap-failure-20260803t123700z` | failure | rejected | At least one package-native command failed; inspect command logs. Logs: `docs/research/toolchain-prototypes/logs/julia/run-20260803T123700Z/floor-lts-julia-1-10-11-linux-x86-64-recovery-after-registry-bootstrap-failure.stdout`, `docs/research/toolchain-prototypes/logs/julia/run-20260803T123700Z/floor-lts-julia-1-10-11-linux-x86-64-recovery-after-registry-bootstrap-failure.stderr`. |
| `lean-adjacent-mismatch-build-interrupted` | unknown | unresolved | The exploratory compile reached 571 of 1,710 jobs without a diagnostic and was manually interrupted to avoid turning a partial build into compatibility evidence. The pair is rejected independently by its immutable toolchain mismatch. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `lean-cache-stale-link-failure` | failure | rejected | cache:exe link omitted stale Cache.Requests object symbols; package-scoped Lake clean and retry recovered. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `lean-host-tools-absent` | failure | rejected | No host elan, lean, or lake executable existed; isolation was therefore required. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `lean-manifest-mutation-rejection` | failure | rejected | The byte comparison rejected the deliberately altered dependency lock; the verifier treats an unexpected match as its own failure. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `lean-mathlib-toolchain-mismatch` | failure | rejected | The root selected adjacent Lean v4.32.1 while the resolved immutable Mathlib revision selected v4.32.2; the verifier rejected this altered pair before it could be presented as a supported environment. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `lean-mathlib-version-mismatch` | failure | rejected | Expected incompatibility detected in Mathlib.Init: v4.31 lacks Std.TreeMap.localEntries and related APIs required by the v4.32.1 Mathlib commit. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `lean-no-cache-incomplete-clone` | unknown | unresolved | First approved clone returned without manifest or resolvable HEAD; retry was required and separately succeeded. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `lean-no-cache-success` | success | recommended | A fresh locked dependency resolution and 1,710-job source build succeeded with both binary-cache controls disabled; the relevant probability import built, the reviewed manifest matched regeneration, and the exact axiom set contained no sorryAx. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `lean-proof-body-failures` | failure | rejected | Preserves unsolved PMF sum, invalid field notation, and missing namespace failures; failed declarations reported sorryAx and were not accepted. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `lean-recommended-cache-success` | success | recommended | The official cache client observed no matching files at its first endpoint, automatically fell back to the second endpoint, downloaded and decompressed all 8,639 artifacts, and the locked build plus explicit axiom inspection succeeded without sorryAx. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `lean-recommended-incomplete-clone` | unknown | unresolved | Harness returned after clone notice without exit status; no manifest or resolvable checkout HEAD existed, so this was not classified as success. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `lean-recommended-network-denied` | failure | rejected | Expected Reservoir/curl DNS failure; network is a dependency-resolution/cache assumption. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `lean-tag-resolution-approved` | success | recommended | The currentness correction resolved both v4.32.2 tags to full immutable commits; the installed Lean binary independently reported the exact Lean commit. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `lean-tag-resolution-sandbox` | failure | rejected | Expected sandbox DNS failure; preserved and rerun with approved read-only network access. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `lean-tag-resolution-v4.32.1-superseded` | success | rejected | Resolved both release tags to full immutable and distinct commits; the successful pair was later superseded by the v4.32.2 currentness correction. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `lean-v4.32.1-cache-success-superseded` | success | rejected | Immutable dependency resolution, relevant probability import, build, and explicit transitive axiom inspection succeeded; no sorryAx. This successful pair is preserved but superseded by v4.32.2. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `lean-v4.32.1-no-cache-success-superseded` | success | rejected | Fresh locked dependency resolution and 1,710-job source build succeeded without binary cache; axiom set matched cached result and had no sorryAx. This successful pair is preserved but superseded by v4.32.2. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `pypi-osv-exact-lock-query` | success | unresolved | The official OSV batch API returned one aligned, unpaginated result per exact PyPI query and zero vulnerability records at the recorded 2026-08-05 query time. This covers only the selected prototype package lock and is not a security guarantee. Logs: `docs/research/toolchain-prototypes/logs/security/run-20260805/pypi-osv.stdout.log`, `docs/research/toolchain-prototypes/logs/security/run-20260805/pypi-osv.stderr.log`. |
| `python-development-3-14-6-historical` | success | rejected | The exact package-native sequence passed, but Python 3.14.7 superseded this patch on 2026-08-05; retained as successful historical evidence and rejected as the final development pin. Logs: `docs/research/toolchain-prototypes/logs/python/run-20260803/development-3-14-6-artifact-digests.stdout`, `docs/research/toolchain-prototypes/logs/python/run-20260803/development-3-14-6-artifact-digests.stderr`. |
| `python-development-3-14-7` | success | recommended | The owned dispatcher rechecked runtime, uv, and lock digests; built sdist and wheel with the package-native PEP 517 path; installed in a separate venv; ran pip check and pytest; and removed all extracted runtime, build, log, and cache state on exit. Logs: `docs/research/toolchain-prototypes/logs/python/run-20260805/python-development-owned-verify.stdout.log`, `docs/research/toolchain-prototypes/logs/python/run-20260805/python-development-owned-verify.stderr.log`. |
| `python-development-pep517-network-failure` | failure | rejected | PEP 517 isolation attempted to resolve Hatchling and failed without DNS. Logs: `docs/research/toolchain-prototypes/logs/python/run-20260803/development-3-14-6-build-sandbox-network-failure.stdout`, `docs/research/toolchain-prototypes/logs/python/run-20260803/development-3-14-6-build-sandbox-network-failure.stderr`. |
| `python-development-uv-seed-cache-failure` | failure | rejected | uv seed cache was interpreter-specific and still attempted a network fetch. Logs: `docs/research/toolchain-prototypes/logs/python/run-20260803/development-3-14-6-builder-venv-uv-seed-cache-failure.stdout`, `docs/research/toolchain-prototypes/logs/python/run-20260803/development-3-14-6-builder-venv-uv-seed-cache-failure.stderr`. |
| `python-floor-3-11-15-historical` | success | rejected | The original floor run passed and is retained, but the final recommendation is bound to the later owned dispatcher evidence. Logs: `docs/research/toolchain-prototypes/logs/python/run-20260803/floor-3-11-15-artifact-digests.stdout`, `docs/research/toolchain-prototypes/logs/python/run-20260803/floor-3-11-15-artifact-digests.stderr`. |
| `python-floor-3-11-15-owned` | success | recommended | The owned dispatcher rechecked runtime, uv, and lock digests; built sdist and wheel with the package-native PEP 517 path; installed in a separate venv; ran pip check and pytest; and removed all extracted runtime, build, log, and cache state on exit. Logs: `docs/research/toolchain-prototypes/logs/python/run-20260805/python-floor-owned-verify.stdout.log`, `docs/research/toolchain-prototypes/logs/python/run-20260805/python-floor-owned-verify.stderr.log`. |
| `python-floor-cold-seed-network-failure` | failure | rejected | Cold uv seed required absent packages and failed DNS; ordinary cache state was insufficient. Logs: `docs/research/toolchain-prototypes/logs/python/run-20260803/floor-3-11-15-builder-venv-sandbox-network-failure.stdout`, `docs/research/toolchain-prototypes/logs/python/run-20260803/floor-3-11-15-builder-venv-sandbox-network-failure.stderr`. |
| `python-rejected-3-10-20-metadata-rejection` | failure | rejected | pip rejected the wheel because 3.10.20 is outside Requires-Python >=3.11. Logs: `docs/research/toolchain-prototypes/logs/python/run-20260803/rejected-3-10-20-metadata-rejection.stdout`, `docs/research/toolchain-prototypes/logs/python/run-20260803/rejected-3-10-20-metadata-rejection.stderr`. |
| `python-rejected-pip-cache-network-failure` | failure | rejected | Pinning pip from an ordinary cache still attempted mutable index metadata retrieval. Logs: `docs/research/toolchain-prototypes/logs/python/run-20260803/rejected-3-10-20-pin-pip-sandbox-network-failure.stdout`, `docs/research/toolchain-prototypes/logs/python/run-20260803/rejected-3-10-20-pin-pip-sandbox-network-failure.stderr`. |
| `r-4.6.1-macos-unavailable` | unknown | unresolved | CRAN policy motivates multi-platform validation but does not establish this package's macOS behavior. Run the identical built-tarball check on an exact official macOS R 4.6.1 runtime before claiming support. Logs: `docs/research/toolchain-prototypes/logs/r/run-20260803/macos-unavailable.stdout`, `docs/research/toolchain-prototypes/logs/r/run-20260803/macos-unavailable.stderr`. |
| `r-4.6.1-windows-unavailable` | unknown | unresolved | CRAN policy motivates multi-platform validation but does not establish this package's Windows behavior. Run R CMD build/check/install and testthat with exact R 4.6.1 on Windows before claiming support. Logs: `docs/research/toolchain-prototypes/logs/r/run-20260803/windows-unavailable.stdout`, `docs/research/toolchain-prototypes/logs/r/run-20260803/windows-unavailable.stderr`. |
| `r-conda-development-build-gap` | failure | rejected | conda-forge had R 4.6.1 but its available testthat 3.3.2 builds required R 4.4 or 4.5, so the combined environment was unsatisfiable; development test dependencies were instead installed from the SHA-locked CRAN source closure. Logs: `docs/research/toolchain-prototypes/logs/r/run-20260803/development-conda-unsatisfied.stdout`, `docs/research/toolchain-prototypes/logs/r/run-20260803/development-conda-unsatisfied.stderr`. |
| `r-depends-incompatibility-rejection` | failure | rejected | Expected genuine incompatibility: both R CMD check installation and direct R CMD INSTALL reject the built tarball because R 4.6.1 does not satisfy Depends: R (>= 4.7.0). Logs: `docs/research/toolchain-prototypes/logs/r/run-20260803/rejection-check-tarball.stdout`, `docs/research/toolchain-prototypes/logs/r/run-20260803/rejection-install-tarball.stderr`. |
| `r-development-4.6.1-package-native` | success | recommended | A fresh library installed the exact 24-package CRAN/Archive source closure from URL+SHA-256 lock without copying the host library; R CMD build/check (Status: OK), installation, five testthat expectations, and installed smoke passed. Logs: `docs/research/toolchain-prototypes/logs/r/run-20260803/development-check-tarball.stdout`, `docs/research/toolchain-prototypes/logs/r/run-20260803/development-check-tarball.stderr`. |
| `r-floor-4.4.3-package-native` | success | recommended | A fresh prefix recreated offline from the full explicit URL+SHA-256 lock; R CMD build, built-tarball check (Status: OK), installation, five expectations, and smoke passed in that recreated prefix. Logs: `docs/research/toolchain-prototypes/logs/r/run-20260803/floor-check-tarball.stdout`, `docs/research/toolchain-prototypes/logs/r/run-20260803/floor-check-tarball.stderr`. |
| `rejected-julia-1-12-6-requires-1-13-20260803t122700z` | failure | rejected | Pkg.resolve rejected the active project because its Julia compat range excludes the running Julia version. Logs: `docs/research/toolchain-prototypes/logs/julia/run-20260803T122700Z/rejected-julia-1-12-6-requires-1-13.stdout`, `docs/research/toolchain-prototypes/logs/julia/run-20260803T122700Z/rejected-julia-1-12-6-requires-1-13.stderr`. |
| `rejected-julia-1-12-6-requires-1-13-20260803t123100z` | failure | rejected | Pkg.resolve rejected the active project because its Julia compat range excludes the running Julia version. Logs: `docs/research/toolchain-prototypes/logs/julia/run-20260803T123100Z/rejected-julia-1-12-6-requires-1-13.stdout`, `docs/research/toolchain-prototypes/logs/julia/run-20260803T123100Z/rejected-julia-1-12-6-requires-1-13.stderr`. |
| `rejected-julia-1-12-6-requires-1-13-20260803t123700z` | failure | rejected | Pkg.resolve rejected the active project because its Julia compat range excludes the running Julia version. Logs: `docs/research/toolchain-prototypes/logs/julia/run-20260803T123700Z/rejected-julia-1-12-6-requires-1-13.stdout`, `docs/research/toolchain-prototypes/logs/julia/run-20260803T123700Z/rejected-julia-1-12-6-requires-1-13.stderr`. |
| `rejected-julia-1-12-6-requires-1-13-20260803t124500z` | failure | rejected | Pkg.resolve rejected the active project because its Julia compat range excludes the running Julia version. Logs: `docs/research/toolchain-prototypes/logs/julia/run-20260803T124500Z/rejected-julia-1-12-6-requires-1-13.stdout`, `docs/research/toolchain-prototypes/logs/julia/run-20260803T124500Z/rejected-julia-1-12-6-requires-1-13.stderr`. |
| `rust-archive-offline-cache-miss` | failure | rejected | The offline probe correctly refused to download the rejected zip 8.1.0 fixture after crash recovery. An exact locked fetch populated only that fixture; the separately retained development-success and MSRV-rejection probes then passed as expected. Logs: `docs/research/toolchain-prototypes/logs/rust/run-20260805-final/archive-8.1-dev-compatible.stdout`, `docs/research/toolchain-prototypes/logs/rust/run-20260805-final/archive-8.1-dev-compatible.stderr`. |
| `rust-dev-prototype` | success | recommended | Exact version/commit assertions, offline metadata, formatting, Clippy with warnings denied, tests, runtime smoke, and unsafe-code rejection passed in owned fresh targets that were deleted on exit. Logs: `docs/research/toolchain-prototypes/logs/rust/run-20260805-final/development-verify.stdout`, `docs/research/toolchain-prototypes/logs/rust/run-20260805-final/development-verify.stderr`. |
| `rust-fresh-resolution-lock-drift` | failure | rejected | The superseded lock hash was rejected after a fresh resolver selected regex-automata 0.4.18 instead of 0.4.16. Review found this was the only lock change; both exact toolchains and the immutable security probe then passed the replacement lock. Logs: `docs/research/toolchain-prototypes/logs/rust/run-20260805-stale-lock/reviewed-stale-lock-rejection.stdout`, `docs/research/toolchain-prototypes/logs/rust/run-20260805-stale-lock/reviewed-stale-lock-rejection.stderr`. |
| `rust-install-dev` | success | recommended | Exact patched stable toolchain, rustfmt, and Clippy installed in isolated RUSTUP_HOME. Logs: `docs/research/toolchain-prototypes/logs/rust/run-20260803/install-dev.stdout`, `docs/research/toolchain-prototypes/logs/rust/run-20260803/install-dev.stderr`. |
| `rust-install-dev-isolated-cargo-home-failure` | failure | rejected | The toolchain downloaded, but rustup rejected a CARGO_HOME that did not contain its installed proxy. Logs: `docs/research/toolchain-prototypes/logs/rust/run-20260803/install-dev-isolated-cargo-home-failure.stdout`, `docs/research/toolchain-prototypes/logs/rust/run-20260803/install-dev-isolated-cargo-home-failure.stderr`. |
| `rust-install-msrv` | success | recommended | Patched first Edition-2024 toolchain installed with rustfmt and Clippy. This establishes tool availability only; its Cargo is affected by the cited 2026 advisories and is not approved for networked bootstrap. Logs: `docs/research/toolchain-prototypes/logs/rust/run-20260803/install-msrv.stdout`, `docs/research/toolchain-prototypes/logs/rust/run-20260803/install-msrv.stderr`. |
| `rust-msrv-prototype` | success | recommended | The reviewed lock passed exact version/commit assertions, offline metadata, formatting, Clippy with warnings denied, tests, and runtime smoke at the compatibility floor in an owned fresh target deleted on exit. This is not security-support evidence for Rust 1.85.1. Logs: `docs/research/toolchain-prototypes/logs/rust/run-20260805-final/msrv-verify.stdout`, `docs/research/toolchain-prototypes/logs/rust/run-20260805-final/msrv-verify.stderr`. |
| `rust-registry-metadata` | success | recommended | Exact registry metadata captured declared Rust versions, licenses, repositories, and feature sets. Logs: `docs/research/toolchain-prototypes/logs/rust/run-20260803/candidate-registry-metadata.stdout`, `docs/research/toolchain-prototypes/logs/rust/run-20260803/candidate-registry-metadata.stderr`. |
| `rust-sandbox-seccomp-failure` | failure | unresolved | rustup aborted when the sandbox denied an operation in wait-timeout's signal handling. The identical owned probes passed outside that sandbox, so this is retained as an environment limitation, not a Rust compatibility result. Logs: `docs/research/toolchain-prototypes/logs/rust/run-20260805-recovery/rustup-version.stdout`, `docs/research/toolchain-prototypes/logs/rust/run-20260805-recovery/rustup-version.stderr`. |
| `rust-unsafe-policy-rejection` | failure | rejected | Expected compiler rejection confirms project code cannot contain an unsafe block; transitive dependency unsafe usage is outside this claim. Logs: `docs/research/toolchain-prototypes/logs/rust/run-20260805-policy/unsafe-policy-rejection.stdout`, `docs/research/toolchain-prototypes/logs/rust/run-20260805-policy/unsafe-policy-rejection.stderr`. |
| `rustfmt-initial-rejection` | failure | rejected | rustfmt identified two source formatting differences; corrected source later passes. Logs: `docs/research/toolchain-prototypes/logs/rust/run-20260803/dev-fmt-check-initial-failure.stdout`, `docs/research/toolchain-prototypes/logs/rust/run-20260803/dev-fmt-check-initial-failure.stderr`. |
| `rustsec-audit` | success | recommended | cargo-audit 0.22.2 verified its official release-asset and executable hashes, scanned the exact 128-package lock against an archive-hash-bound RustSec snapshot with no fetch, and reported zero crate vulnerabilities or warnings. This claim is limited to the locked crate graph. Logs: `docs/research/toolchain-prototypes/logs/rust/run-20260805-security/security-verify.stdout`, `docs/research/toolchain-prototypes/logs/rust/run-20260805-security/security-verify.stderr`. |
| `sha2-initial-api-failure` | failure | rejected | SHA-2 0.11 digest output did not implement the assumed LowerHex trait; explicit byte formatting fixed the prototype. Logs: `docs/research/toolchain-prototypes/logs/rust/run-20260803/dev-clippy-initial-compile-failure.stdout`, `docs/research/toolchain-prototypes/logs/rust/run-20260803/dev-clippy-initial-compile-failure.stderr`. |
| `zip-8.1-development` | success | rejected | Compiles on development Rust but is rejected overall because it cannot satisfy the proposed floor. Logs: `docs/research/toolchain-prototypes/logs/rust/run-20260805-policy/archive-8.1-dev-compatible.stdout`, `docs/research/toolchain-prototypes/logs/rust/run-20260805-policy/archive-8.1-dev-compatible.stderr`. |
| `zip-8.1-msrv-rejection` | failure | rejected | Cargo rejects zip 8.1.0 because it requires rustc 1.88. Logs: `docs/research/toolchain-prototypes/logs/rust/run-20260805-policy/archive-8.1-msrv-rejection.stdout`, `docs/research/toolchain-prototypes/logs/rust/run-20260805-policy/archive-8.1-msrv-rejection.stderr`. |
<!-- SQ0002_ATTEMPTS_END -->

## Machine-readable recommendation binding

This JSON must equal `matrix.json.report_summary`. The verifier also binds the
exact matrix, every retained stdout/stderr artifact, current advisory response,
prototype subject, and corruption fixture.

<!-- SQ0002_REPORT_SUMMARY_BEGIN -->
{
  "ci_matrix": [
    {
      "architecture": "x86_64",
      "component": "Lean/Mathlib/Lake",
      "evidence_probe_ids": [
        "lean-recommended-cache-success"
      ],
      "id": "lean-linux-exact",
      "os": "Ubuntu 24.04.4",
      "status": "direct_success",
      "version": "4.32.2/905b95818eb32af7874a58b427f50c1711a5e96c"
    },
    {
      "architecture": "x86_64",
      "component": "Lean/Mathlib/Lake",
      "evidence_probe_ids": [
        "lean-no-cache-success"
      ],
      "id": "lean-linux-no-cache",
      "os": "Ubuntu 24.04.4",
      "status": "direct_success",
      "version": "4.32.2/905b95818eb32af7874a58b427f50c1711a5e96c no-cache"
    },
    {
      "architecture": "arm64",
      "component": "Lean/Mathlib/Lake",
      "evidence_probe_ids": [],
      "id": "lean-macos-planned",
      "os": "macOS",
      "status": "planned_validation",
      "version": "exact pair"
    },
    {
      "architecture": "x86_64",
      "component": "Lean/Mathlib/Lake",
      "evidence_probe_ids": [],
      "id": "lean-windows-planned",
      "os": "Windows",
      "status": "planned_validation",
      "version": "exact pair"
    },
    {
      "architecture": "x86_64",
      "component": "Rust/Cargo",
      "evidence_probe_ids": [
        "rust-dev-prototype"
      ],
      "id": "rust-linux-dev",
      "os": "Ubuntu 24.04.4",
      "status": "direct_success",
      "version": "1.97.1"
    },
    {
      "architecture": "x86_64",
      "component": "Rust/Cargo",
      "evidence_probe_ids": [
        "rust-msrv-prototype"
      ],
      "id": "rust-linux-msrv",
      "os": "Ubuntu 24.04.4",
      "status": "direct_success",
      "version": "1.85.1"
    },
    {
      "architecture": "arm64",
      "component": "Rust/Cargo",
      "evidence_probe_ids": [],
      "id": "rust-linux-arm64-planned",
      "os": "Ubuntu",
      "status": "planned_validation",
      "version": "1.97.1/1.85.1"
    },
    {
      "architecture": "arm64",
      "component": "Rust/Cargo",
      "evidence_probe_ids": [],
      "id": "rust-macos-planned",
      "os": "macOS",
      "status": "planned_validation",
      "version": "1.97.1/1.85.1"
    },
    {
      "architecture": "x86_64",
      "component": "Rust/Cargo",
      "evidence_probe_ids": [],
      "id": "rust-windows-planned",
      "os": "Windows",
      "status": "planned_validation",
      "version": "1.97.1/1.85.1"
    },
    {
      "architecture": "x86_64",
      "component": "Python",
      "evidence_probe_ids": [
        "python-development-3-14-7"
      ],
      "id": "python-linux-314",
      "os": "Ubuntu 24.04.4",
      "status": "direct_success",
      "version": "3.14.7"
    },
    {
      "architecture": "x86_64",
      "component": "Python",
      "evidence_probe_ids": [
        "python-floor-3-11-15-owned"
      ],
      "id": "python-linux-311",
      "os": "Ubuntu 24.04.4",
      "status": "direct_success",
      "version": "3.11.15"
    },
    {
      "architecture": "x86_64",
      "component": "Python",
      "evidence_probe_ids": [],
      "id": "python-linux-312-planned",
      "os": "Ubuntu",
      "status": "planned_validation",
      "version": "3.12.13"
    },
    {
      "architecture": "x86_64",
      "component": "Python",
      "evidence_probe_ids": [],
      "id": "python-linux-313-planned",
      "os": "Ubuntu",
      "status": "planned_validation",
      "version": "3.13.15"
    },
    {
      "architecture": "arm64",
      "component": "Python",
      "evidence_probe_ids": [],
      "id": "python-macos-planned",
      "os": "macOS",
      "status": "planned_validation",
      "version": "3.11-3.14"
    },
    {
      "architecture": "x86_64",
      "component": "Python",
      "evidence_probe_ids": [],
      "id": "python-windows-planned",
      "os": "Windows",
      "status": "planned_validation",
      "version": "3.11-3.14"
    },
    {
      "architecture": "x86_64",
      "component": "R",
      "evidence_probe_ids": [
        "r-development-4.6.1-package-native"
      ],
      "id": "r-linux-dev",
      "os": "Ubuntu 24.04.4",
      "status": "direct_success",
      "version": "4.6.1"
    },
    {
      "architecture": "x86_64",
      "component": "R",
      "evidence_probe_ids": [
        "r-floor-4.4.3-package-native"
      ],
      "id": "r-linux-floor",
      "os": "Ubuntu 24.04.4",
      "status": "direct_success",
      "version": "4.4.3"
    },
    {
      "architecture": "unknown until runner selection",
      "component": "R",
      "evidence_probe_ids": [],
      "id": "r-macos-planned",
      "os": "macOS",
      "status": "planned_validation",
      "version": "4.6.1"
    },
    {
      "architecture": "x86_64",
      "component": "R",
      "evidence_probe_ids": [],
      "id": "r-windows-planned",
      "os": "Windows",
      "status": "planned_validation",
      "version": "4.6.1"
    },
    {
      "architecture": "x86_64",
      "component": "Julia/Pkg",
      "evidence_probe_ids": [
        "development-julia-1-12-6-linux-x86-64-20260803t124500z"
      ],
      "id": "julia-linux-stable",
      "os": "Ubuntu 24.04.4",
      "status": "direct_success",
      "version": "1.12.6"
    },
    {
      "architecture": "x86_64",
      "component": "Julia/Pkg",
      "evidence_probe_ids": [
        "floor-lts-julia-1-10-11-linux-x86-64-20260803t124500z"
      ],
      "id": "julia-linux-lts",
      "os": "Ubuntu 24.04.4",
      "status": "direct_success",
      "version": "1.10.11"
    },
    {
      "architecture": "arm64",
      "component": "Julia/Pkg",
      "evidence_probe_ids": [],
      "id": "julia-macos-planned",
      "os": "macOS",
      "status": "planned_validation",
      "version": "Stable/LTS"
    },
    {
      "architecture": "x86_64",
      "component": "Julia/Pkg",
      "evidence_probe_ids": [],
      "id": "julia-windows-planned",
      "os": "Windows",
      "status": "planned_validation",
      "version": "Stable/LTS"
    },
    {
      "architecture": "x86_64",
      "component": "Apache Arrow libraries",
      "evidence_probe_ids": [
        "arrow-pyarrow25-arrow-rs59-cross-lineage-hardened"
      ],
      "id": "arrow-linux-candidates",
      "os": "Ubuntu 24.04.4",
      "status": "direct_success",
      "version": "25.0.0/59.1.0"
    }
  ],
  "recommendations": [
    {
      "ci_matrix": [
        "lean-linux-exact",
        "lean-linux-no-cache",
        "lean-macos-planned",
        "lean-windows-planned"
      ],
      "component": "Lean/Mathlib/Lake",
      "development_pin": "Lean 4.32.2 commit f3b06c705e6c85f5314019d5d3baab0fec5b580c; Mathlib commit 905b95818eb32af7874a58b427f50c1711a5e96c; bundled Lake 5.0.0-src+f3b06c7",
      "evidence_probe_ids": [
        "lean-recommended-cache-success",
        "lean-no-cache-success"
      ],
      "id": "lean-mathlib",
      "role": "initial normative proof backend research pin",
      "rollback_policy": "Restore the prior exact Lean/Mathlib commits and reviewed manifests; never mix adjacent release names",
      "support_floor": "No version range: support only the exact Mathlib-selected Lean pair",
      "update_policy": "Re-query both official releases, resolve immutable commits, rerun cached and no-cache builds, mismatch/manifest controls, and axiom inspection"
    },
    {
      "ci_matrix": [
        "rust-linux-dev",
        "rust-linux-msrv",
        "rust-linux-arm64-planned",
        "rust-macos-planned",
        "rust-windows-planned"
      ],
      "component": "Rust/Cargo",
      "development_pin": "Rust 1.97.1; rustc build commit 8bab26f4f68e0e26f0bb7960be334d5b520ea452; Cargo build commit c980f4866141969fab6254a680546a277789d6f0",
      "evidence_probe_ids": [
        "rust-install-dev",
        "rust-dev-prototype",
        "rust-install-msrv",
        "rust-msrv-prototype",
        "rustsec-audit"
      ],
      "id": "rust-cargo",
      "role": "reference operational backend research pin",
      "rollback_policy": "Restore the prior reviewed toolchain and Cargo.lock; retain Cargo CVE-2026-5222/CVE-2026-5223 mitigations",
      "support_floor": "Compatibility-only Rust 1.85.1 MSRV (rustc 4eb161250e340c8f48f66e2b929ef4a5bed7c181; Cargo d73d2caf9e41a39daf2a8d6ce60ec80bf354d2a7); fetch with current patched Cargo, then isolated uncredentialed crates.io-only offline 1.85 checks",
      "update_policy": "Advance only after development and MSRV share the exact lock and fmt, clippy -D warnings, tests, unsafe rejection, license inventory, and advisory checks pass; do not use Cargo <1.96 with credentials or third-party registries"
    },
    {
      "ci_matrix": [
        "python-linux-314",
        "python-linux-311",
        "python-linux-312-planned",
        "python-linux-313-planned",
        "python-macos-planned",
        "python-windows-planned"
      ],
      "component": "Python",
      "development_pin": "CPython 3.14.7; python-build-standalone 20260805 target commit 76b41240bc8dfe753a54b2e32c8941e536568be8; runtime archive sha256 a3a4e4b81b138960c7c546694df8a77578c0b6aa46d47e96f49b9e10e8f860c9",
      "evidence_probe_ids": [
        "python-development-3-14-7",
        "python-floor-3-11-15-owned"
      ],
      "id": "python",
      "role": "thin frontend development/support research pin",
      "rollback_policy": "Restore the prior reviewed interpreter archive digest and universal hash lock; never fall back to the superseded 3.14.6 pin silently",
      "support_floor": "Python >=3.11; exact floor patch tested: CPython 3.11.15 source commit 2340a037f7450e70fccfe411e6531afb4d57a312",
      "update_policy": "Test every supported minor in CI; refresh security patches, managed-runtime provenance, and the universal hash lock before upgrade"
    },
    {
      "ci_matrix": [
        "r-linux-dev",
        "r-linux-floor",
        "r-macos-planned",
        "r-windows-planned"
      ],
      "component": "R",
      "development_pin": "R 4.6.1 with testthat 3.3.2",
      "evidence_probe_ids": [
        "r-development-4.6.1-package-native",
        "r-floor-4.4.3-package-native"
      ],
      "id": "r",
      "role": "thin frontend development/support research pin",
      "rollback_policy": "Restore the previous exact R runtime and explicit test dependency inventory",
      "support_floor": "DESCRIPTION R >=4.4.0; exact floor patch tested: R 4.4.3 with testthat 3.2.3",
      "update_policy": "Review floor each feature release and rerun built-tarball checks on every claimed platform"
    },
    {
      "ci_matrix": [
        "julia-linux-stable",
        "julia-linux-lts",
        "julia-macos-planned",
        "julia-windows-planned"
      ],
      "component": "Julia/Pkg",
      "development_pin": "Julia 1.12.6 official Linux x86-64 archive sha256 bbabf3bef19421a9dbd24a767d807606ab85e444323b5a1c73ffe293fa3d079a",
      "evidence_probe_ids": [
        "development-julia-1-12-6-linux-x86-64-20260803t124500z",
        "floor-lts-julia-1-10-11-linux-x86-64-20260803t124500z"
      ],
      "id": "julia",
      "role": "thin frontend development/LTS research pin",
      "rollback_policy": "Restore prior official archive digest, compat entry, and generated manifest",
      "support_floor": "Julia LTS 1.10.11 archive sha256 fb49c6b174600cd2051e37ba3f7330f8acf06dd00bce609bab6611387fdb37bf",
      "update_policy": "Follow maintained Stable/LTS lines and rerun fresh-depot offline package-native probes"
    },
    {
      "ci_matrix": [
        "arrow-linux-candidates"
      ],
      "component": "Apache Arrow libraries",
      "development_pin": "Apache Arrow 25.0.0 format release; PyArrow 25.0.0 and arrow-rs 59.1.0 candidates",
      "evidence_probe_ids": [
        "arrow-pyarrow25-arrow-rs59-cross-lineage-hardened"
      ],
      "id": "arrow-candidates",
      "role": "experimental interoperability candidates only",
      "rollback_policy": "Remove candidate libraries; no production or normative dependency exists",
      "support_floor": "None selected; experimental candidate, not logical-data identity",
      "update_policy": "Refresh implementation matrix/security pages and cross-read probes before later RFC work"
    }
  ]
}
<!-- SQ0002_REPORT_SUMMARY_END -->
