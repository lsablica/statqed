# Rust/Cargo compatibility prototype

Status: **Experimental**.

Evidence dates: 2026-08-03, refreshed 2026-08-05. This prototype tests toolchain and dependency
compatibility only. It defines no StatQED serialization, Arrow, archive,
digest, CLI, artifact, canonicalization, or statistical semantics. Successful
execution is not verification and does not accept any Draft RFC.

## Recommendation

- Development pin: Rust `1.97.1` with rustc commit
  `8bab26f4f68e0e26f0bb7960be334d5b520ea452` and Cargo commit
  `c980f4866141969fab6254a680546a277789d6f0`. This is the current patched
  stable release on the evidence date; `1.97.1` fixes an LLVM optimization
  miscompilation reported for `1.97.0` and earlier releases.
- Proposed MSRV: Rust `1.85.1`, not the `stable` channel alias. It is the
  patched first Rust release supporting Edition 2024. The tested candidate
  dependencies Arrow `59.1.0`, SHA-2 `0.11.0`, and clap `4.6.5` each declare
  Rust `1.85`; the exact `1.85.1` patch floor avoids known `1.85.0`
  regressions. Use Edition 2024 and workspace resolver `3`.
- MSRV policy: keep `1.85.1` fixed through the foundation milestone. Raise it
  only in a dedicated compatibility-policy change that re-resolves from a
  clean cache, runs both exact compiler jobs, records rejected dependencies,
  and updates downstream platform evidence. The Rust project supplies fixes
  only for its latest stable release, so the MSRV job demonstrates source
  compatibility, not a security-supported compiler. Run it isolated and
  uncredentialed, with network disabled after a current patched Cargo performs
  the exact crates.io-only fetch; do not use Cargo `1.85.1` for releases,
  signing, publication, third-party registries, or secret-bearing work.
- Update policy: check each stable and every patch/security announcement.
  Update the development pin only through a PR that atomically changes the
  toolchain file and lock, passes the development/MSRV/cross-platform gates,
  and records the new rustc/Cargo commits. Roll back by reverting that atomic
  pin-and-lock change; never silently move the `stable` alias in CI.

The official source records `cargo-cve-2026-5222` and
`cargo-cve-2026-5223` place Cargo `1.85.1` in both affected ranges. The former
concerns credential exposure with sparse third-party registries (and states
crates.io users are unaffected); the latter concerns symlink extraction from
malicious third-party-registry tarballs. Source record
`rust-release-1.96.1-libssh2-security` also identifies three later libssh2
security fixes bundled into Cargo. These are why the compiler/API floor and
the networked package-acquisition tool are separate roles.

The exact prototype `Cargo.lock` SHA-256 is
`993f587b7dee5a7e18bff312ae76ac7ab84031ccc771b5e9789915d2bfd3883b`.
A fresh resolver moved only `regex-automata` from `0.4.16` to `0.4.18`.
The previous lock SHA-256
`8db0b054ed47a9eb63678ea96644fd5791acd1cab0a3441754c0d70229b55040`
is retained as rejected drift evidence; the replacement lock was reviewed,
reproduced by a fresh resolution, and passed both exact toolchains.
Both toolchains used this same lock in offline mode and produced the same
runtime observation:

```json
{"arrow_ipc_bytes":776,"archive_bytes":175,"blake3_hex":"ac758c4353bce30e16cc6c1e5387139c1f43b4feca0fe3ffeab81d04a0c5af04","json_bytes":49,"rows":3,"sha256_hex":"0ea463438fdd5d4584bb4a8a33bd98b7f6db6cb5bff484359c59f8c858a9d611"}
```

Those bytes and digests are observations of candidate APIs, not proposed
canonical vectors or artifact identifiers.

## Direct dependency candidates

| Capability | Candidate tested | Declared Rust version | License metadata | Result and maintenance observation |
|---|---:|---:|---|---|
| Serialization traits | serde `1.0.229` | `1.56` | MIT OR Apache-2.0 | Passes both toolchains; current registry release observed 2026-08-03. |
| Diagnostic JSON | serde_json `1.0.151` | `1.71` | MIT OR Apache-2.0 | Passes both toolchains. JSON remains diagnostic in this prototype. |
| Arrow transport/API | arrow `59.1.0`, only `ipc` enabled | `1.85` | Apache-2.0 | Passes both; Apache arrow-rs documents approximately monthly releases and a rolling MSRV changed in major releases. This does not select logical-data identity. |
| Archive API | zip `7.2.0`, default features disabled, stored entries only | `1.83.0` | MIT | Passes both. Current stable `8.1.0` and prerelease `9.0.0-pre2` require Rust `1.88`; `8.1.0` passes development but is rejected for the proposed MSRV. Archive-envelope selection remains later work. |
| Digest API | blake3 `1.8.5` | undeclared | CC0-1.0 OR Apache-2.0 OR Apache-2.0 WITH LLVM-exception | Directly passes `1.85.1`; the undeclared crate MSRV is a maintenance risk and must remain covered by the real MSRV job. This does not select a StatQED digest profile. |
| Digest API | sha2 `0.11.0` | `1.85` | MIT OR Apache-2.0 | Passes both. This does not select a StatQED digest profile. |
| CLI parsing | clap `4.6.5` | `1.85` | MIT OR Apache-2.0 | Passes both with derive support. No CLI protocol is defined. |

The exact inventory contains 128 packages: 127 registry packages plus the
local prototype. Every registry package has license metadata. The normalized
inventory is `dependency-license-inventory.json`, SHA-256
`e13f2450893fa02a668b3cd722a909f7abc267a23868b88b99bfbded299d6374`,
and is regenerated from `cargo metadata --locked --offline` and the reviewed
lock by `verify_license_inventory.py`. Metadata is not a substitute for
reviewing distributed license texts before production.

The security probe verifies all of these immutable inputs before execution:

- official cargo-audit `0.22.2` Linux release archive SHA-256
  `ab28a1bdb54db4d5d8ad5981cf1f959410370b3d28250dbd35f6a44248620e39`;
- extracted cargo-audit executable SHA-256
  `473b9a71e5cb5bde22f69c32f749c9b83931287d92dc36b91cb04f6705640ef2`;
- RustSec database commit `d91a8fc9492378f23cba86b81770c6d16de6ebba`
  source-archive SHA-256
  `e6a7e9ac185d5a41cac57adb47b9d0a8b8796f66978b9a6b8788af9f238b3d7c`;
- the exact Cargo lock and normalized dependency-license inventory hashes.

With database fetching and yanked-state queries disabled, cargo-audit reported
zero vulnerabilities and no warnings for the 128 locked packages. This is a
point-in-time observation of the crate graph only. It does not assess rustc,
Cargo, rustup, the operating system, or unmodeled native libraries, and it is
not a guarantee that the graph is vulnerability-free. Exact external-input
locks are in `security-lock.json`.

## Directly tested environment

- Ubuntu 24.04.4 LTS, kernel `7.0.0-28-generic`, glibc `2.39`;
- `x86_64-unknown-linux-gnu`, x86_64 host;
- locale `C.UTF-8`, timezone UTC;
- rustup `1.29.0 (28d1352db 2026-03-05)`;
- only the native `x86_64-unknown-linux-gnu` target was installed and tested;
- network was required for exact toolchain installation, initial registry
  resolution/fetch, the rejected archive-candidate fetch, and retrieval of the
  checksum-published cargo-audit asset and immutable RustSec source snapshot;
- development and MSRV compilation then used `--locked --offline` with
  distinct fresh target directories under `/tmp`; `verify-probe.sh` deleted
  each owned target on exit;
- `run-probes.sh` refuses a nonempty evidence directory, including the
  committed evidence directory, so a rerun cannot overwrite reviewed logs.

No macOS, Windows, Linux arm64, musl, or cross-compilation result was directly
tested. Official Rust target-tier documentation and GitHub runner availability
are not substitutes for a StatQED build. SQ-0004/SQ-0018 should run the
following concrete CI entries before claiming those platforms:

| Entry | Runner/toolchain | Required commands | Current evidence |
|---|---|---|---|
| `rust-dev-linux-x64` | `ubuntu-24.04`, `1.97.1` | metadata locked, fmt check, Clippy all targets/features with `-D warnings`, tests, runtime smoke, RustSec audit | Direct host analogue passed. |
| `rust-msrv-linux-x64` | `ubuntu-24.04`, `1.85.1`; isolated, offline after exact crates.io-only fetch, uncredentialed | metadata/test/Clippy with the committed lock and warnings denied | Direct host analogue passed; compatibility only, not security support. |
| `rust-dev-linux-arm64` | `ubuntu-24.04-arm`, `1.97.1` | locked metadata, Clippy, tests, runtime smoke | Untested; required before support claim. |
| `rust-dev-macos-arm64` | `macos-15`, `1.97.1` | locked metadata, Clippy, tests, runtime smoke | Untested; required before support claim. |
| `rust-dev-macos-x64` | `macos-15-intel`, `1.97.1` | locked metadata, Clippy, tests, runtime smoke | Untested; required before support claim. |
| `rust-dev-windows-x64` | `windows-2025`, `1.97.1` | locked metadata, Clippy, tests, runtime smoke | Untested; required before support claim. |

Use named runner images rather than `*-latest`. Add a scheduled, non-gating
current-`stable` drift probe that opens an update issue; it must not silently
alter the exact production pin.

## Failures and rejections preserved

1. A first isolated rustup invocation set both `RUSTUP_HOME` and `CARGO_HOME`
   to empty cache roots. Rust `1.97.1` downloaded, but rustup exited `1`
   because its proxy was not installed in that `CARGO_HOME`. The corrected
   command keeps only `RUSTUP_HOME` isolated while pointing rustup's
   `CARGO_HOME` at its installed proxy; Cargo registry/build caches remain
   isolated. Both artifacts are preserved.
2. The first `cargo fmt --check` rejected two formatting differences. The
   source was formatted and the exact check then passed.
3. The first Clippy attempt found a real compilation error: the SHA-2 `0.11`
   output no longer implemented the assumed `LowerHex` formatting. The probe
   now formats bytes explicitly; Clippy with warnings denied passes on both
   compilers. This is API-compatibility evidence, not a normative digest
   implementation.
4. The unsafe fixture exits `101` because `#![forbid(unsafe_code)]` rejects an
   unsafe block. This demonstrates the project-code policy is active; it does
   not assert that transitive dependencies contain no unsafe code.
5. zip `8.1.0` compiles on Rust `1.97.1` but Cargo rejects it on Rust `1.85.1`
   because it declares Rust `1.88`. The exact rejected lock SHA-256 is
   `0e85549ba43c18f41e3160f71bbe6e015e5a14e938222dae91d01ade74309e71`.
6. A fresh resolver selected `regex-automata 0.4.18` instead of `0.4.16`.
   The old lock hash is retained as a detected failure. Review confirmed this
   was the only lock change; the replacement lock reproduced exactly and
   passed development, MSRV, license, and RustSec checks.
7. The first post-crash offline archive-fixture rerun failed because the rebuilt
   cache did not contain the rejected zip `8.1.0` crate. Cargo correctly refused
   network access. After an exact locked fetch, the development success and
   MSRV rejection were rerun offline and retained separately.
8. In the restricted workspace sandbox, rustup `1.29.0` aborted with exit `134`
   after an `Operation not permitted` error in `wait-timeout` signal handling.
   The exact diagnostics are retained. Identical direct-host probes passed, so
   this is an execution-environment limitation, not Rust incompatibility.

## Reproduction and SQ-0004 handoff

For owned verification after the exact external assets have been retrieved:

```bash
STATQED_RUST_CACHE_ROOT=/tmp/statqed-sq0002-rust-cache \
  docs/research/toolchain-prototypes/rust/verify-probe.sh development
STATQED_RUST_CACHE_ROOT=/tmp/statqed-sq0002-rust-cache \
  docs/research/toolchain-prototypes/rust/verify-probe.sh msrv
STATQED_RUST_CACHE_ROOT=/tmp/statqed-sq0002-rust-cache \
STATQED_CARGO_AUDIT_ARCHIVE=/tmp/statqed-sq0002-cargo-audit-0.22.2.tgz \
STATQED_RUSTSEC_ARCHIVE=/tmp/statqed-sq0002-rustsec-d91a8fc.tar.gz \
  docs/research/toolchain-prototypes/rust/verify-probe.sh security
```

The verifier requires the exact cached toolchains and registry graph, operates
offline, owns fresh target directories, and deletes those targets on exit. It
refuses a caller-supplied target. The cargo-audit release archive and RustSec
snapshot URLs and hashes are in `security-lock.json`.

`run-probes.sh` is the evidence recorder. It deliberately exits `2` rather
than overwrite the committed `run-20260803` evidence. A new evidence run must
name a new empty path explicitly, for example:

```bash
STATQED_RUST_LOG_DIR=/tmp/statqed-sq0002-new-rust-evidence \
STATQED_RUST_CACHE_ROOT=/tmp/statqed-sq0002-rust-cache \
  docs/research/toolchain-prototypes/rust/run-probes.sh checks
```

The cache root contains toolchains and downloaded crates; compilation targets
remain disposable. Remove the task cache and downloaded security archives only
after final integration so downstream review does not trigger large downloads.

For SQ-0004, initialize the production workspace with `rust-version =
"1.85.1"`, Edition 2024, resolver `3`, workspace `unsafe_code = "forbid"`,
and an exact `rust-toolchain.toml` channel `1.97.1`. Commit `Cargo.lock`, then
run:

```bash
cargo +1.97.1 metadata --locked --format-version 1
cargo +1.97.1 fmt --all -- --check
cargo +1.97.1 clippy --locked --workspace --all-targets --all-features -- -D warnings
cargo +1.97.1 test --locked --workspace --all-targets --all-features
cargo +1.85.1 clippy --locked --workspace --all-targets --all-features -- -D warnings
cargo +1.85.1 test --locked --workspace --all-targets --all-features
```

Expected result: every command exits `0`. The bootstrap task must use its own
toy, non-semantic smoke output; the compatibility JSON above is not production
behavior.

## Primary sources retrieved 2026-08-03 and refreshed 2026-08-05

- Rust 1.97.1 release and miscompilation fix:
  <https://blog.rust-lang.org/2026/07/16/Rust-1.97.1/>
- Rust 1.85.1 fixes: <https://blog.rust-lang.org/2025/03/18/Rust-1.85.1/>
- Rust 1.85.0 and Edition 2024:
  <https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/>
- Cargo CVE-2026-5222 advisory:
  <https://blog.rust-lang.org/2026/05/25/cve-2026-5222/>
- Cargo CVE-2026-5223 advisory:
  <https://blog.rust-lang.org/2026/05/25/cve-2026-5223/>
- Rust 1.96.1 bundled-libssh2 security fixes:
  <https://blog.rust-lang.org/2026/06/30/Rust-1.96.1/>
- Cargo `rust-version` policy:
  <https://doc.rust-lang.org/stable/cargo/reference/rust-version.html>
- Edition 2024 resolver behavior:
  <https://doc.rust-lang.org/stable/edition-guide/rust-2024/cargo-resolver.html>
- Rust target tiers:
  <https://doc.rust-lang.org/rustc/platform-support.html>
- Apache arrow-rs release/MSRV policy:
  <https://github.com/apache/arrow-rs>
- GitHub-hosted runner labels:
  <https://docs.github.com/en/actions/reference/runners/github-hosted-runners>
- RustSec/cargo-audit: <https://github.com/rustsec/rustsec>
- cargo-audit `0.22.2` official release and published asset digests:
  <https://github.com/rustsec/rustsec/releases/tag/cargo-audit%2Fv0.22.2>
- immutable RustSec advisory database subject:
  <https://github.com/RustSec/advisory-db/tree/d91a8fc9492378f23cba86b81770c6d16de6ebba>
- Exact registry metadata and repository/license links:
  `../logs/rust/run-20260803/candidate-registry-metadata.stdout`

Machine-oriented recommendations and attempts are in `probe-fragment.json`.
