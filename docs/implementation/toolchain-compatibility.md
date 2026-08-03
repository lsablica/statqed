# SQ-0002 toolchain compatibility

Status: **Experimental**. Evidence and source cutoff: 2026-08-03.

This report recommends research pins for the production bootstrap tasks. It
does not initialize a production toolchain, accept an RFC, define canonical
bytes or logical-data identity, reserve a package name, or claim support on an
untested platform. Source-language runtimes, package managers, registries,
caches, solvers, and prototype libraries remain outside the trusted computing
base. The machine matrix retains commands, environment variables, timestamps,
locks, logs, failures, and content hashes for every attempted combination.

Matrix SHA-256: `sha256:52b63324c22056938ac152666f86c8eea46d8cfb7a42ae8106abbe242e361b48`

## Recommendation summary

| Component and role | Development/reference pin | Support floor | Directly tested CI anchors | Planned validation |
|---|---|---|---|---|
| Lean/Mathlib/Lake, normative proof backend | Lean 4.32.1 commit `f054605aea4b840552cca2e725580bffd1e1b704`; Mathlib `520045ab14e26149ee970e2e617ca04b09bde5d6`; Lake `5.0.0-src+f054605` | No version range; exact matched pair only | Ubuntu x86-64 cached and fresh no-cache builds | macOS arm64, Windows x86-64 |
| Rust/Cargo, reference operational backend | Rust 1.97.1 (`rustc 8bab26f4f`, Cargo `c980f4866`) | Rust 1.85.1 MSRV (`rustc 4eb161250`, Cargo `d73d2caf9`), Edition 2024, resolver 3 | Ubuntu x86-64 development and MSRV | macOS arm64, Windows x86-64 |
| Python thin frontend | CPython 3.14.6, upstream commit `c63aec69bd59c55314c06c23f4c22c03de76fe45`; tested Astral build `20260718` | Python `>=3.11`; exact floor patch 3.11.15, upstream commit `2340a037f7450e70fccfe411e6531afb4d57a312` | Ubuntu x86-64 endpoints 3.14.6 and 3.11.15 | Linux 3.12/3.13, macOS, Windows |
| R thin frontend | R 4.6.1; testthat 3.3.2 | `Depends: R (>= 4.4.0)`; exact floor patch 4.4.3/testthat 3.2.3 | Ubuntu x86-64 development and floor | macOS and Windows development pin |
| Julia thin frontend | Julia Stable 1.12.6 archive `bbabf3…079a` | Julia LTS 1.10.11 archive `fb49c6…7bf` | Ubuntu x86-64 Stable and LTS | macOS arm64 and Windows x86-64 |
| Arrow interoperability experiments | Arrow format/release 25.0.0; PyArrow 25.0.0; arrow-rs 59.1.0 | None selected | Ubuntu x86-64 on Python 3.14.6/Rust 1.97.1 | R, Julia, other platforms; RFC-0006 remains Draft |
| CBOR interoperability experiments | cbor2 6.1.3, ciborium 0.2.2, minicbor 2.3.0 | None selected | Ubuntu x86-64 on Python 3.14.6/Rust 1.97.1 | Independent strict validators/oracles; RFC-0001 remains Draft |
| CDDL experiment | `cddl` 0.10.6 on Rust 1.97.1 | No compatible StatQED MSRV floor: tool requires Rust 1.88 | Ubuntu x86-64 as isolated research tool | Decide isolation/replacement in later schema work |

The five language recommendations are machine-bound below. Arrow, CBOR, and
CDDL are exact experimental candidate pins, not production recommendations.

## Direct environment and evidence rules

All direct runs used Ubuntu 24.04.4 LTS, Linux 7.0.0-28-generic, x86-64,
`C.UTF-8`, on the host (no container). Retrieval and direct execution dates
are 2026-08-03. GitHub `*-latest`, release indexes, package registries, and
runner labels are mutable discovery mechanisms; recommendations use exact
versions, commits, release assets, checksums, or locks after discovery.
Official platform documentation is recorded separately from execution. No
macOS, Windows, ARM, or container behavior is claimed as directly tested.

Each recommendation advances only after the complete endpoint matrix passes
from isolated state. Rollback restores the prior reviewed exact pins and lock
files. Failed preparation, network, cache, malformed-input, MSRV, and mutation
runs are evidence, not noise. Known-advisory results are point-in-time only;
absence of a listed advisory is never a vulnerability-free guarantee.

## Lean, Mathlib, Lake, and Elan

- Role/pin: Lean 4.32.1 and Mathlib commit `520045ab…` are the latest matched
  stable pair observed. Standalone Lean 4.32.2 exists but had no matching
  stable Mathlib release, so matching names were not inferred as compatibility.
- Sources: official Lean/Mathlib release pages, the immutable Mathlib
  `lean-toolchain` and `lakefile.toml`, and official Lake/Elan references in
  `sources.json`, all retrieved 2026-08-03.
- Installation/version commands: install checksum-inspected Elan 4.2.3, then
  `elan toolchain install leanprover/lean4:v4.32.1`; `lean --version` reported
  `Lean 4.32.1 (f054605…, Release)` and `lake --version` reported
  `Lake 5.0.0-src+f054605`.
- Prototype: in `lean-mathlib/recommended`, `lake update --keep-toolchain`,
  `lake build`, and `lake env lean StatQEDLeanProbe.lean`. A separate fresh
  directory set `MATHLIB_NO_CACHE_ON_UPDATE=1 LAKE_NO_CACHE=1` and completed
  1,710 source jobs. The relevant Mathlib probability import built.
- Proof inspection: `#print axioms` reported exactly `propext`,
  `Classical.choice`, and `Quot.sound`; it did not report `sorryAx`. Rejected
  proof bodies that did report `sorryAx` remain in failure logs.
- Cache/network: ordinary resolution requires GitHub/Reservoir access. The
  binary cache was tested separately; a stale cache executable failed and was
  recovered only by package-scoped cleaning. A no-cache source build is the
  clean compatibility anchor.
- License/security: Lean and Mathlib are Apache-2.0. Elan is a bootstrap tool,
  not proof authority. Lean releases warn against broad compatibility
  assumptions; upgrade the exact pair together.
- Rejected/unknown: Lean 4.31.0 with Mathlib 4.32.1 failed in `Mathlib.Init`;
  stale Elan 4.2.1 was rejected; sandbox DNS and interrupted initial clones are
  preserved. SQ-0003 must copy the exact prototype toolchain/commit and compare
  the resulting manifest and axiom report before creating production files.

## Rust and Cargo

- Role/pins: development Rust 1.97.1; MSRV 1.85.1, the first patch line used
  here for Edition 2024/resolver 3. Exact rustc/Cargo commits and host/target
  triples are in the matrix and Rust logs.
- Installation/version commands: isolated `rustup toolchain install 1.97.1`
  and `rustup toolchain install 1.85.1`; `rustc -Vv`, `cargo -V`, and
  `rustup show active-toolchain` were captured.
- Prototype: the same Cargo lock passed `cargo metadata --locked --offline`,
  `cargo fmt --check`, `cargo clippy --locked --all-targets -- -D warnings`,
  and `cargo test --locked` on both pins. `#![forbid(unsafe_code)]` is active,
  and an unsafe mutation failed.
- Candidate graph: Arrow 59.1.0, serde 1.0.229, serde_json 1.0.151, clap 4.6.5,
  sha2 0.11, blake3 1.8.5, and zip 7.2.0 were compatibility candidates, not
  production dependencies. zip 8.1.0 worked on development but requires Rust
  1.88 and failed the MSRV, so 7.2.0 is the bounded candidate.
- Cache/network/security: preparation used isolated rustup/Cargo homes;
  package checks reran offline from the exact lock. `cargo-audit 0.22.2`
  against RustSec commit `d91a8fc…` reported zero advisories/warnings for the
  retained graph at that instant. Rust and Cargo are MIT/Apache-2.0; dependency
  license inventory is retained. SQ-0004 must copy the exact toolchain/MSRV
  and lock proposal, rerun all four gates, and retain `cargo tree`/audit output.

## Python

- Role/policy: CPython 3.14.6 development, declared floor `>=3.11`, exact floor
  test 3.11.15, and future CI on every supported minor 3.11–3.14. Python 3.10.20
  was deliberately rejected by `Requires-Python >=3.11`.
- Exact distribution assets: direct behavior used Astral
  python-build-standalone release 20260718, not official CPython binaries.
  The 3.14.6 and 3.11.15 archives have verified SHA-256 values `86bf107f…8b74`
  and `23ccae6f…447d`; uv 0.11.32 archive `aab924fd…b967`. Exact URLs and
  GitHub release-asset digest fields are retained in
  `logs/python/run-20260803/pinned-release-assets.stdout`.
- Installation/prototype: download the exact assets, verify SHA-256, extract,
  set `SQ0002_PYTHON_DEVELOPMENT`/`SQ0002_PYTHON_FLOOR`, then run
  `python3 run_probes.py --probe development` and `--probe floor`. Both built
  sdist/wheel through PEP 517 isolation from a `--require-hashes` wheelhouse,
  installed into separate venvs, passed `pip check`, two pytest tests, and
  metadata checks. Version outputs were Python 3.14.6 and 3.11.15.
- Exact tool snapshot: pip 26.2, build 1.5.0, Hatchling 1.31.0, packaging 26.2,
  pytest 9.1.1; universal lock `0fcf65ff…30b3`. The final wheel and sdist were
  byte-identical across endpoints within the same final run, but this is build
  evidence, not a general reproducible-build claim.
- Cache/network/licenses: asset/wheelhouse preparation is networked and
  checksum-gated; final builds are offline. CPython uses PSF-2.0;
  python-build-standalone/uv and tool packages carry the licenses inventoried
  in `python/RESULTS.md`. There is no exhaustive authoritative Python advisory
  scan in SQ-0002; it remains a pre-release gate. macOS/Windows, ARM, and the
  3.12/3.13 middle minors remain untested.

## R

- Role/policy: exact R 4.6.1 development with testthat 3.3.2; project-defined
  floor `R >=4.4.0`, exercised at exact R 4.4.3/testthat 3.2.3. This is not an
  R Core maintenance promise.
- Sources/commands: official current release, Writing R Extensions, CRAN
  policy, and R SDLC records were retrieved 2026-08-03. Package-native commands
  are `R CMD build`, `R CMD check --no-manual` on the built tarball,
  `R CMD INSTALL`, direct `testthat::test_local`, and installed-package smoke.
- Isolation: the final development evidence installs a SHA-locked CRAN source
  graph into a fresh library; the floor uses a conda explicit lock with SHA-256
  for every artifact and was freshly recreated offline before the same tests.
  Exact lock paths/digests and version/session output are in `r/README.md` and
  the matrix. An earlier host-library copy and a failed conda R 4.6.1/testthat
  solve remain rejected preparation evidence.
- Results: both development and floor built, checked with `Status: OK`,
  installed, passed five expectations, and passed smoke. A mutated
  `Depends: R (>=4.7.0)` failed check/install under R 4.6.1.
- Licenses/security/platform: R is GPL-2 | GPL-3; the prototype and testthat
  are MIT; the full test-only graph retains declared licenses. CRAN checks are
  not a security audit and no exhaustive R advisory database result is
  claimed. macOS and Windows remain planned validation, not support evidence.

## Julia and Pkg

- Role/pins: official Julia Stable 1.12.6 and LTS 1.10.11 Linux x86-64 archive
  digests `bbabf3…079a` and `fb49c6…7bf`. The declared package floor is the LTS
  line, reviewed whenever Julia changes maintained lines.
- Installation/version: verify official archive checksums, extract under
  `/tmp`, then run `python3 julia/run_probes.py --run-id <fresh-id>`.
  `julia --version` reported 1.12.6 and 1.10.11.
- Prototype: each fresh depot has a fixed empty registry sentinel and no
  registry packages; offline resolve, instantiate, strict precompile, test,
  and status passed. Manifests are content-addressed. A `julia = "1.13"`
  mutation failed under 1.12.6.
- Failures/cache: three earlier empty-depot approaches still tried to clone
  mutable General and failed DNS. They remain failures. The successful run did
  not reuse those depots. Julia source is MIT; official binary distributions
  may be GPL aggregates due to bundled dependencies. Security policy is
  project-coordinated; no package advisory absence is claimed. Non-Linux
  platforms and registry publication remain untested.

## Arrow boundary

PyArrow/Arrow C++ 25.0.0 (CPython 3.14 wheel `447df7…`) and arrow-rs 59.1.0
(Rust 1.97.1 locked graph) independently wrote and cross-read Int64/Utf8/Binary
IPC files. Repeated same-process writes matched, file and stream encodings were
different physical bytes, and a magic-only malformed file was rejected. These
are observable API/compatibility facts only. They do not select a normative
Arrow representation, define logical-data identity, or accept RFC-0006.

Apache Arrow is Apache-2.0 with third-party notices and a project security
process. R Arrow and Julia Arrow were not installed/tested; host absence is not
ecosystem incompatibility. The update policy is to refresh the Arrow release,
implementation-status/security pages, exact wheel/crate locks, and cross-read
tests. Rollback removes the candidates because no production dependency exists.

## CBOR and CDDL boundary

cbor2 6.1.3 (hash-bound CPython 3.14 wheel), ciborium 0.2.2, and minicbor 2.3.0
compiled/imported and exercised discriminating map-order, duplicate-key,
indefinite-length, nesting, break, truncated, and malformed cases. Their
permissive and representation behaviors differ materially: no library is a
semantic oracle. A future RFC must define a strict profile/validator and an
independently originated conformance oracle before canonical bytes exist.

`cddl` 0.10.6 on Rust 1.97.1 accepted both tested map orders and rejected a
wrong type. Its 154-package install graph requires Rust 1.88, so the exact
locked Rust 1.85.1 attempt failed; it cannot be an MSRV-compatible backend
dependency and remains an isolated experimental tool. RFC 8610, RFC 8949, RFC
9682, and the active CDDL modules draft are distinct sources; CDDL does not
choose canonical bytes. Licenses are cbor2 MIT, ciborium Apache-2.0, minicbor
BlueOak-1.0.0, and cddl MIT. cbor2 6.1.3 follows a recent security fix; strict
malformed-input limits remain mandatory future work.

## Complete attempted-combination inventory

<!-- SQ0002_ATTEMPTS_BEGIN -->
| Probe | Class | Disposition | Result and retained evidence |
|---|---|---|---|
| `arrow-host-python-venv-missing` | failure | rejected | The host Python lacked ensurepip/python3-venv; the attempt was preserved and replaced by the already-reviewed isolated CPython runtime plus uv. Logs: `docs/research/toolchain-prototypes/logs/arrow/arrow-host-python-venv-missing.stdout.log`, `docs/research/toolchain-prototypes/logs/arrow/arrow-host-python-venv-missing.stderr.log`. |
| `arrow-julia-host-command-unavailable` | unknown | unresolved | No julia command was on PATH. This is not Arrow.jl evidence because separate exact Julia runtimes existed outside PATH and no Arrow.jl environment was prepared. Logs: `docs/research/toolchain-prototypes/logs/arrow/arrow-julia-host-command-unavailable.stdout.log`, `docs/research/toolchain-prototypes/logs/arrow/arrow-julia-host-command-unavailable.stderr.log`. |
| `arrow-pyarrow25-arrow-rs59-cross-lineage-hash-bound` | success | unresolved | Exact hash-bound preparation succeeded. Both independent code lineages self-round-tripped the narrow typed subset, cross-read IPC files, observed same-process repeatability but unequal file/stream bytes, and rejected a minimized magic-only file. This is transport compatibility evidence only. Logs: `docs/research/toolchain-prototypes/logs/arrow/arrow-pyarrow25-arrow-rs59-cross-lineage-hash-bound.stdout.log`, `docs/research/toolchain-prototypes/logs/arrow/arrow-pyarrow25-arrow-rs59-cross-lineage-hash-bound.stderr.log`. |
| `arrow-pyarrow25-arrow-rs59-cross-lineage-unbound` | success | rejected | Typed self-round-trips, cross-lineage IPC reads, repeatability observations, and malformed rejection passed, but the wheel was not hash-bound and the proposed runtimes were not used; this evidence is superseded. Logs: `docs/research/toolchain-prototypes/logs/arrow/arrow-pyarrow25-arrow-rs59-cross-lineage.stdout.log`, `docs/research/toolchain-prototypes/logs/arrow/arrow-pyarrow25-arrow-rs59-cross-lineage.stderr.log`. |
| `arrow-r-package-unavailable` | unknown | unresolved | R was runnable but the Arrow package was absent; no R Arrow import, table, or IPC behavior was tested. Logs: `docs/research/toolchain-prototypes/logs/arrow/arrow-r-package-unavailable.stdout.log`, `docs/research/toolchain-prototypes/logs/arrow/arrow-r-package-unavailable.stderr.log`. |
| `cbor-cddl-full-dev-rust-unbound` | success | rejected | Differential map-order, duplicate, indefinite, depth, malformed, and CDDL shape tests ran, but the wheel was not hash-bound, proposed runtimes were not used, and the cddl install graph was not retained. Superseded by the final run. Logs: `docs/research/toolchain-prototypes/logs/cbor-cddl/cbor-cddl-full-dev-rust.stdout.log`, `docs/research/toolchain-prototypes/logs/cbor-cddl/cbor-cddl-full-dev-rust.stderr.log`. |
| `cbor-libraries-final-hash-bound` | success | unresolved | Hash-bound differential and malformed probes completed. cbor2 and ciborium matched length-first order; minicbor exposed insertion-order control. Duplicate and indefinite behavior differed or was permissive, tested nesting was accepted, and truncated arguments were rejected. Results require a future strict profile validator and do not recommend decoder semantics. Logs: `docs/research/toolchain-prototypes/logs/cbor-cddl/cbor-cddl-full-dev-rust-hash-bound.stdout.log`, `docs/research/toolchain-prototypes/logs/cbor-cddl/cbor-cddl-full-dev-rust-hash-bound.stderr.log`. |
| `cbor2-break-assumption-failure` | failure | rejected | The probe incorrectly asserted that a top-level break byte must be rejected. cbor2 accepted it as an internal sentinel; the assumption was removed and the behavior retained as security-relevant evidence. Logs: `docs/research/toolchain-prototypes/logs/cbor-cddl/cbor2-break-assumption-failure.stdout.log`, `docs/research/toolchain-prototypes/logs/cbor-cddl/cbor2-break-assumption-failure.stderr.log`. |
| `cbor2-version-attribute-failure` | failure | rejected | cbor2 6.1.3 does not expose module __version__; the probe now uses importlib.metadata. Logs: `docs/research/toolchain-prototypes/logs/cbor-cddl/cbor2-version-attribute-failure.stdout.log`, `docs/research/toolchain-prototypes/logs/cbor-cddl/cbor2-version-attribute-failure.stderr.log`. |
| `cddl-0.10.6-rust-1.85.1-msrv-rejection` | failure | rejected | The checked-in lock was used with --locked. Cargo rejected cddl 0.10.6 and selected time packages because they require rustc 1.88.0. Logs: `docs/research/toolchain-prototypes/logs/cbor-cddl/cddl-0.10.6-rust-1.85.1-msrv-rejection.stdout.log`, `docs/research/toolchain-prototypes/logs/cbor-cddl/cddl-0.10.6-rust-1.85.1-msrv-rejection.stderr.log`. |
| `cddl-tool-final-hash-bound` | success | unresolved | The exact published --locked graph built on Rust 1.97.1. CDDL compiled and checked shape, rejected the wrong value type, and accepted both deterministic map-order byte variants. This supports only a conditional development shape tool; it does not canonicalize bytes and requires transitive license/advisory review. Logs: `docs/research/toolchain-prototypes/logs/cbor-cddl/cbor-cddl-full-dev-rust-hash-bound.stdout.log`, `docs/research/toolchain-prototypes/logs/cbor-cddl/cbor-cddl-full-dev-rust-hash-bound.stderr.log`. |
| `development-julia-1-12-6-linux-x86-64-20260803t122700z` | failure | rejected | At least one package-native command failed; inspect command logs. Logs: `docs/research/toolchain-prototypes/logs/julia/run-20260803T122700Z/development-julia-1-12-6-linux-x86-64.stdout`, `docs/research/toolchain-prototypes/logs/julia/run-20260803T122700Z/development-julia-1-12-6-linux-x86-64.stderr`. |
| `development-julia-1-12-6-linux-x86-64-20260803t123100z` | failure | rejected | At least one package-native command failed; inspect command logs. Logs: `docs/research/toolchain-prototypes/logs/julia/run-20260803T123100Z/development-julia-1-12-6-linux-x86-64.stdout`, `docs/research/toolchain-prototypes/logs/julia/run-20260803T123100Z/development-julia-1-12-6-linux-x86-64.stderr`. |
| `development-julia-1-12-6-linux-x86-64-20260803t124500z` | success | recommended | Exact official runtime passed isolated offline Pkg instantiate, precompile, test, and status commands on the named host. Logs: `docs/research/toolchain-prototypes/logs/julia/run-20260803T124500Z/development-julia-1-12-6-linux-x86-64.stdout`, `docs/research/toolchain-prototypes/logs/julia/run-20260803T124500Z/development-julia-1-12-6-linux-x86-64.stderr`. |
| `development-julia-1-12-6-linux-x86-64-recovery-after-registry-bootstrap-failure-20260803t123700z` | failure | rejected | At least one package-native command failed; inspect command logs. Logs: `docs/research/toolchain-prototypes/logs/julia/run-20260803T123700Z/development-julia-1-12-6-linux-x86-64-recovery-after-registry-bootstrap-failure.stdout`, `docs/research/toolchain-prototypes/logs/julia/run-20260803T123700Z/development-julia-1-12-6-linux-x86-64-recovery-after-registry-bootstrap-failure.stderr`. |
| `elan-4.2.1-superseded` | success | rejected | A live updater notice and official latest-release API showed v4.2.3; stale v4.2.1 search evidence was rejected. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `floor-lts-julia-1-10-11-linux-x86-64-20260803t122700z` | failure | rejected | At least one package-native command failed; inspect command logs. Logs: `docs/research/toolchain-prototypes/logs/julia/run-20260803T122700Z/floor-lts-julia-1-10-11-linux-x86-64.stdout`, `docs/research/toolchain-prototypes/logs/julia/run-20260803T122700Z/floor-lts-julia-1-10-11-linux-x86-64.stderr`. |
| `floor-lts-julia-1-10-11-linux-x86-64-20260803t123100z` | failure | rejected | At least one package-native command failed; inspect command logs. Logs: `docs/research/toolchain-prototypes/logs/julia/run-20260803T123100Z/floor-lts-julia-1-10-11-linux-x86-64.stdout`, `docs/research/toolchain-prototypes/logs/julia/run-20260803T123100Z/floor-lts-julia-1-10-11-linux-x86-64.stderr`. |
| `floor-lts-julia-1-10-11-linux-x86-64-20260803t124500z` | success | recommended | Exact official runtime passed isolated offline Pkg instantiate, precompile, test, and status commands on the named host. Logs: `docs/research/toolchain-prototypes/logs/julia/run-20260803T124500Z/floor-lts-julia-1-10-11-linux-x86-64.stdout`, `docs/research/toolchain-prototypes/logs/julia/run-20260803T124500Z/floor-lts-julia-1-10-11-linux-x86-64.stderr`. |
| `floor-lts-julia-1-10-11-linux-x86-64-recovery-after-registry-bootstrap-failure-20260803t123700z` | failure | rejected | At least one package-native command failed; inspect command logs. Logs: `docs/research/toolchain-prototypes/logs/julia/run-20260803T123700Z/floor-lts-julia-1-10-11-linux-x86-64-recovery-after-registry-bootstrap-failure.stdout`, `docs/research/toolchain-prototypes/logs/julia/run-20260803T123700Z/floor-lts-julia-1-10-11-linux-x86-64-recovery-after-registry-bootstrap-failure.stderr`. |
| `lean-cache-stale-link-failure` | failure | rejected | cache:exe link omitted stale Cache.Requests object symbols; package-scoped Lake clean and retry recovered. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `lean-host-tools-absent` | failure | rejected | No host elan, lean, or lake executable existed; isolation was therefore required. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `lean-mathlib-version-mismatch` | failure | rejected | Expected incompatibility detected in Mathlib.Init: v4.31 lacks Std.TreeMap.localEntries and related APIs required by the v4.32.1 Mathlib commit. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `lean-no-cache-incomplete-clone` | unknown | unresolved | First approved clone returned without manifest or resolvable HEAD; retry was required and separately succeeded. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `lean-no-cache-success` | success | recommended | Fresh locked dependency resolution and 1,710-job source build succeeded without binary cache; axiom set matched cached result and had no sorryAx. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `lean-proof-body-failures` | failure | rejected | Preserves unsolved PMF sum, invalid field notation, and missing namespace failures; failed declarations reported sorryAx and were not accepted. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `lean-recommended-cache-success` | success | recommended | Immutable dependency resolution, relevant probability import, build, and explicit transitive axiom inspection succeeded; no sorryAx. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `lean-recommended-incomplete-clone` | unknown | unresolved | Harness returned after clone notice without exit status; no manifest or resolvable checkout HEAD existed, so this was not classified as success. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `lean-recommended-network-denied` | failure | rejected | Expected Reservoir/curl DNS failure; network is a dependency-resolution/cache assumption. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `lean-tag-resolution-approved` | success | recommended | Resolved both release tags to full immutable and distinct commits. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `lean-tag-resolution-sandbox` | failure | rejected | Expected sandbox DNS failure; preserved and rerun with approved read-only network access. Logs: `docs/research/toolchain-prototypes/logs/lean/stdout.log`, `docs/research/toolchain-prototypes/logs/lean/stderr.log`. |
| `python-development-3-14-6` | success | recommended | Fresh SHA-verified release asset passed offline hash-locked PEP 517 sdist/wheel build, separate install, pip check, pytest, metadata, and artifact digest checks. Logs: `docs/research/toolchain-prototypes/logs/python/run-20260803/development-3-14-6.stdout`, `docs/research/toolchain-prototypes/logs/python/run-20260803/development-3-14-6.stderr`. |
| `python-development-pep517-network-failure` | failure | rejected | PEP 517 isolation attempted to resolve Hatchling and failed without DNS. Logs: `docs/research/toolchain-prototypes/logs/python/run-20260803/development-3-14-6-build-sandbox-network-failure.stdout`, `docs/research/toolchain-prototypes/logs/python/run-20260803/development-3-14-6-build-sandbox-network-failure.stderr`. |
| `python-development-uv-seed-cache-failure` | failure | rejected | uv seed cache was interpreter-specific and still attempted a network fetch. Logs: `docs/research/toolchain-prototypes/logs/python/run-20260803/development-3-14-6-builder-venv-uv-seed-cache-failure.stdout`, `docs/research/toolchain-prototypes/logs/python/run-20260803/development-3-14-6-builder-venv-uv-seed-cache-failure.stderr`. |
| `python-floor-3-11-15` | success | recommended | The identical package-native offline sequence passed from the fresh SHA-verified floor release asset. Logs: `docs/research/toolchain-prototypes/logs/python/run-20260803/floor-3-11-15.stdout`, `docs/research/toolchain-prototypes/logs/python/run-20260803/floor-3-11-15.stderr`. |
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
| `rust-dev-prototype` | success | recommended | Resolution, offline metadata, formatting, Clippy with warnings denied, tests, and API runtime smoke passed. Logs: `docs/research/toolchain-prototypes/logs/rust/run-20260803/dev-run.stdout`, `docs/research/toolchain-prototypes/logs/rust/run-20260803/dev-run.stderr`. |
| `rust-install-dev` | success | recommended | Exact patched stable toolchain, rustfmt, and Clippy installed in isolated RUSTUP_HOME. Logs: `docs/research/toolchain-prototypes/logs/rust/run-20260803/install-dev.stdout`, `docs/research/toolchain-prototypes/logs/rust/run-20260803/install-dev.stderr`. |
| `rust-install-dev-isolated-cargo-home-failure` | failure | rejected | The toolchain downloaded, but rustup rejected a CARGO_HOME that did not contain its installed proxy. Logs: `docs/research/toolchain-prototypes/logs/rust/run-20260803/install-dev-isolated-cargo-home-failure.stdout`, `docs/research/toolchain-prototypes/logs/rust/run-20260803/install-dev-isolated-cargo-home-failure.stderr`. |
| `rust-install-msrv` | success | recommended | Patched first Edition-2024 toolchain installed with rustfmt and Clippy. Logs: `docs/research/toolchain-prototypes/logs/rust/run-20260803/install-msrv.stdout`, `docs/research/toolchain-prototypes/logs/rust/run-20260803/install-msrv.stderr`. |
| `rust-msrv-prototype` | success | recommended | The same lock passed offline metadata, formatting, Clippy with warnings denied, tests, and runtime smoke at the proposed floor. Logs: `docs/research/toolchain-prototypes/logs/rust/run-20260803/msrv-run.stdout`, `docs/research/toolchain-prototypes/logs/rust/run-20260803/msrv-run.stderr`. |
| `rust-registry-metadata` | success | recommended | Exact registry metadata captured declared Rust versions, licenses, repositories, and feature sets. Logs: `docs/research/toolchain-prototypes/logs/rust/run-20260803/candidate-registry-metadata.stdout`, `docs/research/toolchain-prototypes/logs/rust/run-20260803/candidate-registry-metadata.stderr`. |
| `rust-unsafe-policy-rejection` | failure | rejected | Expected compiler rejection confirms project code cannot contain an unsafe block; transitive dependency unsafe usage is outside this claim. Logs: `docs/research/toolchain-prototypes/logs/rust/run-20260803/unsafe-policy-rejection.stdout`, `docs/research/toolchain-prototypes/logs/rust/run-20260803/unsafe-policy-rejection.stderr`. |
| `rustfmt-initial-rejection` | failure | rejected | rustfmt identified two source formatting differences; corrected source later passes. Logs: `docs/research/toolchain-prototypes/logs/rust/run-20260803/dev-fmt-check-initial-failure.stdout`, `docs/research/toolchain-prototypes/logs/rust/run-20260803/dev-fmt-check-initial-failure.stderr`. |
| `rustsec-audit` | success | recommended | Point-in-time scan of 128 locked dependencies found zero vulnerabilities and no warnings. Logs: `docs/research/toolchain-prototypes/logs/rust/run-20260803/cargo-audit-rustsec.stdout`, `docs/research/toolchain-prototypes/logs/rust/run-20260803/cargo-audit-rustsec.stderr`. |
| `sha2-initial-api-failure` | failure | rejected | SHA-2 0.11 digest output did not implement the assumed LowerHex trait; explicit byte formatting fixed the prototype. Logs: `docs/research/toolchain-prototypes/logs/rust/run-20260803/dev-clippy-initial-compile-failure.stdout`, `docs/research/toolchain-prototypes/logs/rust/run-20260803/dev-clippy-initial-compile-failure.stderr`. |
| `zip-8.1-development` | success | rejected | Compiles on development Rust but is rejected overall because it cannot satisfy the proposed floor. Logs: `docs/research/toolchain-prototypes/logs/rust/run-20260803/archive-8.1-dev-compatible.stdout`, `docs/research/toolchain-prototypes/logs/rust/run-20260803/archive-8.1-dev-compatible.stderr`. |
| `zip-8.1-msrv-rejection` | failure | rejected | Cargo rejects zip 8.1.0 because it requires rustc 1.88. Logs: `docs/research/toolchain-prototypes/logs/rust/run-20260803/archive-8.1-msrv-rejection.stdout`, `docs/research/toolchain-prototypes/logs/rust/run-20260803/archive-8.1-msrv-rejection.stderr`. |
<!-- SQ0002_ATTEMPTS_END -->

## Update, rollback, and downstream instructions

SQ-0003 may initialize only the production Lean files allowed by its own
contract, using the exact Lean/Mathlib pair above, normal and no-cache build
paths, and the recorded axiom set as a smoke expectation—not as a theorem
soundness claim. SQ-0004 may initialize only its Rust workspace, with Rust
1.97.1, MSRV 1.85.1, Edition 2024/resolver 3, `forbid(unsafe_code)`, the bounded
candidate graph, and fmt/clippy/test/audit gates. Neither task may import the
experimental Arrow/CBOR/CDDL behavior into normative semantics.

Every update opens a new evidence change: re-query current primary sources,
pin immutable assets/commits/locks, run fresh isolated positive and negative
probes, review licenses/advisories, compare generated locks, and obtain an
independent integration disposition. Rollback restores the last reviewed
toolchain and dependency locks; moving tags, registry re-resolution, and cache
success cannot substitute for those bytes.

## Machine-readable recommendation binding

The following JSON must equal `matrix.json.report_summary`; the verifier also
binds the exact matrix SHA-256, every retained log, and every prototype subject.

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
      "version": "4.32.1/520045ab"
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
      "version": "4.32.1/520045ab no-cache"
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
        "python-development-3-14-6"
      ],
      "id": "python-linux-314",
      "os": "Ubuntu 24.04.4",
      "status": "direct_success",
      "version": "3.14.6"
    },
    {
      "architecture": "x86_64",
      "component": "Python",
      "evidence_probe_ids": [
        "python-floor-3-11-15"
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
      "version": "3.12 latest security patch"
    },
    {
      "architecture": "x86_64",
      "component": "Python",
      "evidence_probe_ids": [],
      "id": "python-linux-313-planned",
      "os": "Ubuntu",
      "status": "planned_validation",
      "version": "3.13 latest patch"
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
      "development_pin": "Lean 4.32.1 commit f054605aea4b840552cca2e725580bffd1e1b704; Mathlib commit 520045ab14e26149ee970e2e617ca04b09bde5d6; bundled Lake 5.0.0-src+f054605",
      "evidence_probe_ids": [
        "lean-recommended-cache-success",
        "lean-no-cache-success"
      ],
      "id": "lean-mathlib",
      "role": "initial normative proof backend research pin",
      "rollback_policy": "Restore the prior exact Lean/Mathlib commits and manifest; never mix adjacent tags",
      "support_floor": "No range: support only the exact Mathlib-selected Lean pair",
      "update_policy": "Re-query releases, resolve both immutable commits, rerun cached and no-cache builds plus axiom inspection"
    },
    {
      "ci_matrix": [
        "rust-linux-dev",
        "rust-linux-msrv",
        "rust-macos-planned",
        "rust-windows-planned"
      ],
      "component": "Rust/Cargo",
      "development_pin": "Rust 1.97.1; rustc build commit 8bab26f4f; Cargo build commit c980f4866",
      "evidence_probe_ids": [
        "rust-install-dev",
        "rust-dev-prototype",
        "rust-install-msrv",
        "rust-msrv-prototype",
        "rustsec-audit"
      ],
      "id": "rust-cargo",
      "role": "reference operational backend research pin",
      "rollback_policy": "Restore rust-toolchain and Cargo.lock from the prior reviewed pin",
      "support_floor": "Rust 1.85.1 MSRV (rustc 4eb161250; Cargo d73d2caf9); Edition 2024; resolver 3",
      "update_policy": "Advance stable only after dev and MSRV share one lock and fmt/clippy/test/audit pass"
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
      "development_pin": "CPython 3.14.6 upstream tag commit c63aec69bd59c55314c06c23f4c22c03de76fe45",
      "evidence_probe_ids": [
        "python-development-3-14-6",
        "python-floor-3-11-15"
      ],
      "id": "python",
      "role": "thin frontend development/support research pin",
      "rollback_policy": "Restore prior interpreter patch and universal hash lock",
      "support_floor": "Python >=3.11; exact floor patch tested: 3.11.15 commit 2340a037f7450e70fccfe411e6531afb4d57a312",
      "update_policy": "Test every supported minor; refresh security patches and hash lock before upgrade"
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
    }
  ]
}
<!-- SQ0002_REPORT_SUMMARY_END -->
