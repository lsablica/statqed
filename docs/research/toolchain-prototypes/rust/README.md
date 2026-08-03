# Rust/Cargo compatibility prototype

Status: **Experimental**.

Evidence date: 2026-08-03. This prototype tests toolchain and dependency
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
  compatibility, not a security-supported compiler.
- Update policy: check each stable and every patch/security announcement.
  Update the development pin only through a PR that atomically changes the
  toolchain file and lock, passes the development/MSRV/cross-platform gates,
  and records the new rustc/Cargo commits. Roll back by reverting that atomic
  pin-and-lock change; never silently move the `stable` alias in CI.

The exact prototype `Cargo.lock` SHA-256 is
`8db0b054ed47a9eb63678ea96644fd5791acd1cab0a3441754c0d70229b55040`.
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

The locked graph contains 128 dependencies excluding the prototype package.
All registry `license` fields were present and used SPDX expressions with
permissive options; the raw inventory is
`../logs/rust/run-20260803/dependency-license-inventory.stdout`. Metadata is
not a substitute for reviewing distributed license texts before production.

`cargo-audit 0.22.2` reported zero vulnerabilities and no warnings against
RustSec database commit `d91a8fc9492378f23cba86b81770c6d16de6ebba`
(database timestamp `2026-08-02T19:56:20+02:00`). This is a point-in-time
database observation, not a guarantee that the graph is vulnerability-free.

## Directly tested environment

- Ubuntu 24.04.4 LTS, kernel `7.0.0-28-generic`, glibc `2.39`;
- `x86_64-unknown-linux-gnu`, x86_64 host;
- locale `C.UTF-8`, timezone UTC;
- rustup `1.29.0 (28d1352db 2026-03-05)`;
- only the native `x86_64-unknown-linux-gnu` target was installed and tested;
- network was required for exact toolchain installation, initial registry
  resolution/fetch, archive-candidate resolution, and RustSec database update;
- development and MSRV compilation then used `--locked --offline` with
  distinct fresh target directories under `/tmp`.

No macOS, Windows, Linux arm64, musl, or cross-compilation result was directly
tested. Official Rust target-tier documentation and GitHub runner availability
are not substitutes for a StatQED build. SQ-0004/SQ-0018 should run the
following concrete CI entries before claiming those platforms:

| Entry | Runner/toolchain | Required commands | Current evidence |
|---|---|---|---|
| `rust-dev-linux-x64` | `ubuntu-24.04`, `1.97.1` | metadata locked, fmt check, Clippy all targets/features with `-D warnings`, tests, runtime smoke, RustSec audit | Direct host analogue passed. |
| `rust-msrv-linux-x64` | `ubuntu-24.04`, `1.85.1` | metadata/test/Clippy with the committed lock and warnings denied | Direct host analogue passed. |
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

## Reproduction and SQ-0004 handoff

From the repository root, with network available for the first run:

```bash
STATQED_RUST_CACHE_ROOT=/tmp/statqed-sq0002-rust-cache \
  docs/research/toolchain-prototypes/rust/run-probes.sh all
```

The script places toolchains, Cargo registry/git data, build outputs,
`cargo-audit`, and the RustSec database only under the external `/tmp` cache.
It preserves command metadata and separate stdout/stderr below
`docs/research/toolchain-prototypes/logs/rust/run-20260803/`.

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

## Primary sources retrieved 2026-08-03

- Rust 1.97.1 release and miscompilation fix:
  <https://blog.rust-lang.org/2026/07/16/Rust-1.97.1/>
- Rust 1.85.1 fixes: <https://blog.rust-lang.org/2025/03/18/Rust-1.85.1/>
- Rust 1.85.0 and Edition 2024:
  <https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/>
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
- Exact registry metadata and repository/license links:
  `../logs/rust/run-20260803/candidate-registry-metadata.stdout`

Machine-oriented recommendations and attempts are in `probe-fragment.json`.
