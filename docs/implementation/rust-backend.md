# Rust Backend Implementation Guide

Status: **Experimental** foundation evidence produced by SQ-0004. This guide
describes the locked bootstrap workspace, not a statistical backend or artifact
verifier.

## Exact toolchain policy

| Role | Exact identity | Permitted use |
|---|---|---|
| Development and acquisition | Rust/rustc 1.97.1, commit `8bab26f4f68e0e26f0bb7960be334d5b520ea452`; Cargo 1.97.1, commit `c980f4866141969fab6254a680546a277789d6f0` | dependency acquisition, lock generation, formatting, Clippy, tests, documentation, security tooling |
| Compiler/API floor | Rust/rustc 1.85.1, commit `4eb161250e340c8f48f66e2b929ef4a5bed7c181`; Cargo 1.85.1, commit `d73d2caf9e41a39daf2a8d6ce60ec80bf354d2a7` | exact committed graph only, always `--locked --offline` |

The workspace uses Edition 2024, Cargo resolver 3, and package
`rust-version = "1.85.1"`. Rust 1.85.0 introduced Edition 2024; the selected
1.85.1 patch is the tested compatibility floor. Resolver 3's
incompatible-Rust fallback is useful dependency selection behavior, not proof
of MSRV compatibility. The exact floor build and tests are the evidence.

Cargo 1.85.1 predates fixes for 2026 Cargo/tar and libssh2 advisories and is
within affected ranges of the documented third-party-registry advisories. It
must not access a general registry, read Cargo credentials, generate the lock,
or act as the release toolchain. The exact current source observations and
retrieval date are retained in `backend/evidence/source-lock.json`.

Install the reviewed tools with rustup:

```bash
rustup toolchain install 1.97.1 --profile minimal --component rustfmt --component clippy
rustup toolchain install 1.85.1 --profile minimal --component rustfmt --component clippy
rustc +1.97.1 -Vv
cargo +1.97.1 -Vv
rustc +1.85.1 -Vv
cargo +1.85.1 -Vv
```

`backend/rust-toolchain.toml` selects 1.97.1 for ordinary work. Patch labels
are additionally checked against the full compiler and Cargo source commits in
CI.

## Workspace and responsibilities

```text
backend/
├── rust-toolchain.toml
├── Cargo.toml
├── Cargo.lock
├── crates/
│   ├── statqed-core/  # bounded parsing and deterministic response values
│   └── statqed-cli/   # process I/O and exit codes only
├── tools/             # standard-library verification and evidence tools
└── evidence/          # small, hash-bound normalized records
```

Both packages are non-publishable bootstrap crates, inherit the workspace
edition, rust-version, license, and lint policy, and use
`#![forbid(unsafe_code)]` in every Rust target. Workspace Rust lints forbid
unsafe code and Clippy denies panics, unwrap/expect, unchecked indexing,
unreachable paths, and warnings. The exact Cargo graph contains only these two
local MIT packages; there are no registry, build, development, native, unsafe,
or FFI dependencies.

The committed `Cargo.lock` SHA-256 is
`408f171020abc33031390a1c22ed3f21ec271b797d880f7749f83edec04211a3`.
It was generated twice with Cargo 1.97.1 in fresh credential-free Cargo homes;
both results were byte-identical. `backend/evidence/isolated-execution.json`
retains the command records and environment policy.

## Acquisition and clean reproduction

Normal acquisition is performed only by Cargo 1.97.1 with a new `CARGO_HOME`,
no inherited Cargo credential variables, no project Cargo configuration, and
the reviewed crates.io source. The complete local reproduction is:

```bash
python3 backend/tools/run_isolated_checks.py
```

The script creates disposable HOME, CARGO_HOME, target, XDG, and temporary
directories; generates the lock twice; acquires the exact graph with current
Cargo; changes to offline mode; runs development checks; and separately runs
the 1.85.1 floor offline. Only the rustup installation location is inherited.
It does not retain caches.

To reproduce lock generation manually in a copy, remove only the copied lock
and run:

```bash
cargo +1.97.1 generate-lockfile
sha256sum Cargo.lock
```

Never manually edit `Cargo.lock`. A changed manifest with the old lock fails
under `--locked`; changed lock bytes fail the evidence binding.

## Development and floor gates

Run the primary gates from `backend/`:

```bash
cargo +1.97.1 fmt --check
cargo +1.97.1 build --workspace --all-features --locked
cargo +1.97.1 clippy --workspace --all-targets --all-features --locked -- -D warnings
cargo +1.97.1 test --workspace --all-features --locked
cargo +1.97.1 test --workspace --all-features --doc --locked
```

After current Cargo has acquired the committed graph into an isolated Cargo
home, reuse that same home without credentials or network and run:

```bash
CARGO_NET_OFFLINE=true cargo +1.85.1 metadata --locked --offline --format-version 1
CARGO_NET_OFFLINE=true cargo +1.85.1 build --workspace --all-features --locked --offline
CARGO_NET_OFFLINE=true cargo +1.85.1 clippy --workspace --all-targets --all-features --locked --offline -- -D warnings
CARGO_NET_OFFLINE=true cargo +1.85.1 test --workspace --all-features --locked --offline
CARGO_NET_OFFLINE=true cargo +1.85.1 test --workspace --all-features --doc --locked --offline
```

The maintained script constructs the full clean environment and is the
preferred reproduction. Its negative floor-network fixture uses an empty Cargo
home with an absent dependency and proves Cargo 1.85.1 fails closed in offline
mode instead of acquiring it.

## Deterministic CLI contract

The only successful surface is deterministic version metadata:

```text
statqed --version
statqed version --format text
statqed version --format json
```

JSON responses use protocol version 1 and fixed field order. Malformed or
unsupported invocation writes one JSON object to stderr, nothing to stdout,
and exits 2. Stable symbolic codes cover missing/unknown/repeated/empty/invalid
input, unexpected arguments, invalid Unix argument encoding, and resource
limits. Output never echoes hostile input and contains no timestamp, random
identifier, host path, locale text, dependency debug value, or stack trace.
Write failures return a generic failure exit rather than panic.

The parser accepts at most 64 arguments, 4,096 UTF-8 bytes per argument, and
8,192 aggregate UTF-8 bytes. Both sides of these limits are tested. Tests also
cover no arguments, missing values, repeated options, truncated
structured-looking input, non-UTF-8 Unix arguments, very long input, 256
deterministic randomized process sequences, 1,024 deterministic randomized
library sequences, and broken output.

Run the bound response and policy verifier with:

```bash
python3 backend/tools/check_workspace.py
python3 backend/tools/check_workspace.py --json
python3 backend/tools/check_workspace.py --run-mutations
```

`backend/evidence/deterministic-output-fixtures.json` is replayed against the
real binary. `backend/evidence/bindings.json` binds production sources, the
workflow, tools, fixtures, mutation results, lock, inventory, source record,
isolated execution, and advisory report.

## Adversarial mutations

The verifier creates disposable copies and rejects project unsafe code,
removal of `forbid(unsafe_code)`, changed workspace/package rust-version,
manifest drift without a lock update, changed lock bytes, alternate registry
configuration, ambient Cargo credentials, floor acquisition, nondeterministic
timestamp/random fields, host paths, panic output, unstable debug output,
floating GitHub Actions, and persisted checkout credentials. The minimized
classifications are retained in `backend/evidence/mutation-results.json`.
Comments or static documentation are not scanned as executable Rust.

## Dependency licenses and advisories

Reproduce the normalized lock-bound inventory with:

```bash
python3 backend/tools/dependency_inventory.py
```

It records name, exact version, source, checksum, license expression, feature
set, and dependency role. The current graph has two local MIT packages and no
third-party crate. This does not replace review of distributed license texts or
cover rustc, Cargo, rustup, cargo-audit, GitHub Actions, Python, or the OS.

The point-in-time advisory observation uses cargo-audit 0.22.2 and immutable
RustSec database commit
`1237bbe09d2701e14e6593a630fbaf28928df712`. Download the official archives
at the locators in `backend/evidence/security-lock.json`, verify their recorded
SHA-256 values, then run:

```bash
python3 backend/tools/security_audit.py \
  --cargo-audit-archive /path/to/cargo-audit-0.22.2.tgz \
  --rustsec-archive /path/to/rustsec-1237bbe.tar.gz
```

The tool safely extracts into a temporary directory, verifies the executable,
database, lock, and inventory hashes, and runs the database offline with
`--no-fetch`. The retained result observed zero vulnerabilities and zero
warnings for the two-package lock. This is a dated database observation, not a
security guarantee; yanked-state network queries are deliberately excluded.

## CI and platform evidence

`.github/workflows/rust.yml` uses least-privilege `contents: read`, disables
persisted checkout credentials, and pins the official checkout and Python
setup actions to full commits. It has no cache, upload, release, or write-token
path. The development job validates both full tool identities, repository
guardrails, exact lock, formatting, Clippy, tests, deterministic responses,
clean reproductions, mutations, inventory, and hash-bound RustSec scan. The
floor job acquires with 1.97.1 in a clean Cargo home, then executes 1.85.1 only
with `--locked --offline` in a scrubbed environment.

Each job logs the observed GitHub-hosted runner image, OS, architecture, and
tool versions. Direct task evidence is limited to the actually executed Linux
x86-64 environments. The mutable `ubuntu-24.04` label is not immutable Linux
support and says nothing about macOS, Windows, ARM, or other targets. Those
platforms require separate clean runs before any support claim.

## Update, rollback, generated files, and TCB

For an update, research current official releases and advisories; test a new
development/floor pair independently; regenerate the lock only with the new
reviewed current Cargo; regenerate all evidence; run the full mutation and CI
suite; and obtain Rust, security, CI, and integration review. Never allow an
automated dependency update to change the pair or lock silently.

Rollback is an atomic revert of the toolchain file, manifests, lock, sources,
workflow, evidence bindings, and associated documentation to the last reviewed
commit. Re-run the old pair and its hash-bound security inputs before claiming
the rollback restored the reviewed state. Build trees, Cargo homes, rustup
downloads, and extracted advisory databases are disposable and untracked.
`Cargo.lock` and normalized evidence are generated only through the documented
commands and are reviewed; hand editing generated records is prohibited.

The trusted computing base for these bootstrap claims includes the reviewed
project Rust source, rustc/Cargo/rustup and standard library distributions,
Cargo lock/resolution behavior, Python and the four evidence tools, the OS and
filesystem/process APIs, Git, cargo-audit and the exact RustSec database for
the advisory observation, and GitHub Actions/runner infrastructure for hosted
evidence. The CLI itself is not a trusted verifier. Rust remains a planned
reference operational backend outside the Lean kernel trust boundary.

## Explicit nonclaims

SQ-0004 establishes a reproducible minimal Rust workspace, an exact
development toolchain and offline compiler/API floor, safe project-source
policy, bounded deterministic bootstrap CLI behavior, and point-in-time
dependency/license/advisory evidence. It does **not** establish statistical
objects or validity, an IR or schema, canonical CBOR or Arrow behavior,
logical-data identity, digests, archives, artifacts, theorem locks or registry
authority, certificates, frontend protocols, network services, source-theorem
fidelity, Lean proof checking, artifact verification, or end-to-end verified
analysis. No Draft RFC is implemented or accepted here.
