# SQ-0005 Rust prototype, parser, resource, and security review

Status: **Experimental review record**

Disposition: **APPROVE**

Review date: 2026-08-09

Reviewer: `/root/sq0004_workspace_msrv`, acting as the distinct Rust
prototype, malformed-input/resource, lineage, and dependency-security reviewer

## Decision

The exact implementation subject below is approved as an Experimental,
non-normative Rust prototype and as bounded interoperability evidence. Fresh
Rust 1.97.1 format, build, lint, unit/integration, doc, 273-case conformance,
offline lock-reproduction, dependency-inventory, retained and live yanked,
and immutable RustSec gates pass. The earlier compound-fault, indefinite-chunk
counter, and mutable raw-span findings remain resolved. The two final raw
overlong digest-identifier regressions select their field-specific failures.

This approval is deliberately narrower than SQ-0005 or RFC-0001 acceptance.
It does not approve a production backend, a distributable binary, or the
eventual static integration package. It does not make Rust, Cargo, the parser,
the CLI, `minicbor`, `serde_json`, `sha2`, the conformance runner, or their
outputs semantic or kernel authority.

## Exact implementation subject

All substantive inspection and execution used a clean `git archive` snapshot
of the assigned implementation commit. Later reachable commits were checked
and changed review records only; the diff from this commit to the review-time
head was empty for the Rust crate, semantic fixtures, generated conformance
evidence, and conformance runner.

| Subject | Exact identity |
|---|---|
| Reviewed implementation commit | `410465d773fc011ee01e38e6e76a79a60efe8837` |
| Reviewed repository tree | `a93ac8fe4befe4da52ff0ef5ee928ea04679b85c` |
| Reviewed parent | `7d83204d5ebde9e86e7493e2c9be89506afcd2ee` |
| Reviewed commit subject | `Refresh final prototype evidence bindings` |
| Rust prototype Git tree | `e6d2133ce1f19f1241aca741905435aa478307f6` |
| Rust behavior commit | `14f1ffb0646b280fea805fbec6ba6bb8b3d1a282` |
| Frozen executable/lock commit | `fd8dd9e344ff6bbe1488cb143f8b700c6c795efe` |
| Rust executable/lock selected-source SHA-256 | `cb3c03907bc7cdf6f495be7d98d795347b3b51c1415637a6b1e8d71f558027ea` |
| Semantic model SHA-256 | `a94588e54fdc3e2aa08e73f5f6e76bb71128940bb245305b2dec9dffa2ffcfb2` |
| Profile candidate SHA-256 | `6cbf0f686a1f35b5c6fac8411ef5abc708c9c4410b5fdb2ee510c513df067d2f` |
| Frozen semantic-fixture commit | `b4d92a39e30fa5736c58bc71c57790ec215fbad7` |

The executable/lock subject is the runner's deterministic SHA-256 over sorted,
NUL-framed relative paths and exact bytes for `Cargo.toml`, `Cargo.lock`,
`rust-toolchain.toml`, `src/lib.rs`, and `src/main.rs`. It is the persistent
source/toolchain/lock identity used by the conformance manifest, not a claim
that a path-sensitive local debug ELF is reproducible across platforms.

### Rust files

| File | SHA-256 |
|---|---|
| `schemas/prototypes/rust-cbor/README.md` | `a73f4319d96482f401acb9124fb7c036f195831a6bcc1825ac93a532eaec1680` |
| `schemas/prototypes/rust-cbor/LICENSE` | `e2135b5acb4ab6f5c9d9ac8b4be2d6bcdb0da6a6262fd990ef9117ca44383dd4` |
| `schemas/prototypes/rust-cbor/Cargo.toml` | `37e51170459929bd4a674eca8a2a0168f976de7191eb886ee193c360b8fc6fad` |
| `schemas/prototypes/rust-cbor/Cargo.lock` | `2e9c4f95aa0aa54ab2338e980d388f9f0223be8964d94f82d82f086f2dadb180` |
| `schemas/prototypes/rust-cbor/rust-toolchain.toml` | `8e390d6a0838315f972690f46ef8bae8b7ecc9ee6c1ed70140ef852869c2482e` |
| `schemas/prototypes/rust-cbor/src/lib.rs` | `bf5cd89521f4151197beeb8a9e07d9a92503e615de9c9da2aec1d6f73834d70d` |
| `schemas/prototypes/rust-cbor/src/main.rs` | `a48b67f10d0a7a77d553b226c73d02dae48057d66be83cfd6c517c8ae925f211` |
| `schemas/prototypes/rust-cbor/tests/profile.rs` | `f278b61f959f4f71b707c2a424b879fbb71922a85e5b79ecbf3258ee729d1ae3` |
| `schemas/prototypes/rust-cbor/tests/cli.rs` | `311f5f7faa50664e1f89dc4cb6f7a7a39abf65a1a05f8b809e9b23c1987d2ba9` |
| `schemas/prototypes/rust-cbor/DEPENDENCIES.md` | `90a4c6c9f01684e0659a6f590911a0f068e6c28697c1cab42d00db8765358ec0` |
| `schemas/prototypes/rust-cbor/LINEAGE.md` | `6136314a0c7ac9b971f636e520e8d9dd0d94548f39a96a891d34a37ac9e1dd1a` |

### Conformance and security bindings

| File or subject | SHA-256 |
|---|---|
| Conformance runner, `scripts/serialization/run_conformance.py` | `8a61f6deeeba7bed4e8bb7e0c8202fa0ce730d5328036365d8536ed5950fe01c` |
| Generated manifest | `e69e863053fad44faf2511cedbd53a13725e309cbdb0551621e217c2095dd6cd` |
| Generated results | `4e48d962644cec0f83b868ba13bcc62f3bc8cee4dca748fed10e3ad911195274` |
| Resource fixtures | `984a142eb002a38d4f137a98d44c222fe2bf56dd2147808608372cb0f7ad0039` |
| Digest-framing fixtures | `36895de279202434a1511bb1bf552c199e55d57ee8a57a7d724772a737824d0b` |
| Implementation-lineage registry | `7a7e48658e81e478c3858f265d24eb0c1402fa6169e7c03eb74363effb8208a4` |
| Security lock | `58940480cb4ca163ee5ec1e2bf5a9e3165371e96703018c3ebd147775c8ac0f5` |
| Advisory report | `abe01dc61e4f02fb179f39457077b832491c3503d8461fe82f1835712482cd55` |
| Retained crates.io yanked record | `fd69cb31758d9f3da5f674a3b14b731bda03ba77e9ca1295e03663d67e571e2b` |
| Dependency/license inventory | `3d44e9d26c756c2aa950779f9fcf557f11efc28a50d20f27c2ec1a501aaadfa9` |
| Security reproducer | `d31f7baf094049d5d8437d6fd104af25874c0530e9f18f792ed629dfcf16ee39` |
| Yanked-state checker | `073079e06bdf7e3bb291de3c229530ae695a57a6bcf6e1de9489e36cd2381ca5` |
| Dependency-inventory generator | `b21d621e57943e6ddfbdbc4de8c01e8ecb99843b2746fbd953b3c4329e35c24d` |

The generated manifest binds 273 cases, 70 accepted cases, 203 rejected cases,
69 joint goldens, zero failures, a five-second per-process timeout, and a
128 MiB Linux address-space ceiling. Its Rust subject is exactly `cb3c0390…`;
the fresh `--verify` execution reproduced the manifest and results above.

## Malformed and failure-precedence review

The raw parser retains the first complete root plus its consumed boundary.
Validation performs root CBOR validity before trailing-byte expectedness,
followed by application expectedness and deterministic-profile validation.
The minimized compound faults reproduce as follows:

- `61ff00` returns `validity.invalid_utf8` at byte offset 1 rather than
  `expected.trailing_bytes`;
- `a200f400f500` returns `validity.map_duplicate` at byte offset 3 rather than
  `expected.trailing_bytes`;
- a complete raw frame with a 129-byte purpose returns `digest.purpose`;
- a complete raw frame with a 129-byte object/schema identifier returns
  `digest.object_class_schema`, not truncation or generic length failure.

The 273-case corpus includes 15 well-formedness failures, 10 validity
failures, six expectedness failures, 63 deterministic-profile failures, one
CDDL-shape failure, 39 semantic-validity failures, 33 digest-verification
failures, 15 resource failures, 17 differential detections, and four
operational failures. Both independent implementations match every reviewed
expectation; agreement remains evidence, not proof.

Raw ordered map entries remain present until exact typed-equivalent duplicate
detection completes. No native map can overwrite a key first. Tags, floats,
unsupported simple values, indefinite encodings, non-preferred heads, invalid
UTF-8, unknown extension states, malformed lengths, breaks, and incomplete map
pairs retain explicit failure classes rather than library exception text.

## Resource, allocation, panic, and process review

One indefinite root plus 4,095 empty byte or text chunks reaches exactly the
4,096-item cap and returns `profile.indefinite`; adding one chunk returns
`resource.total_items`. Chunk heads therefore participate in the same counter
as ordinary items.

Declared byte-string lengths `2^32-1` and `2^32` return
`resource.string_bytes` before body allocation. Raw and typed nesting depth 32
is admitted where specified and depth 33 is rejected. A 2,000-level typed-JSON
value is rejected by lexical preflight before `serde_json`. Array, map, string,
input, canonical output, diagnostic output, total-item, extension, and digest
frame boundaries all have inclusive and one-over cases. Writer growth and
length arithmetic use checked addition and explicit caps.

The fresh results contain 250 Rust observations. None was unavailable, timed
out, crashed, raised an operational exception, wrote stderr, or had a negative
return code. The four timeout, memory, crash, and exception recipes are
harness-level fail-closed tests and remain `operational.*`, never `accepted`.
They do not prove allocator recovery if the operating system or allocator
terminates a Rust process.

The crate forbids unsafe Rust and denies Clippy `all`, `pedantic`, `unwrap`,
`expect`, and `panic` lints. Raw node, map-entry, and document fields are
private; accessors are immutable; public cross-document slicing is checked and
returns `None`. Internal direct slices receive only private parser-created
ranges. Three `unreachable!` sites remain, guarded respectively by a masked
three-bit major type, a masked five-bit additional-information value, and
internal literal subjects. I found no input-reachable panic path. Allocator,
compiler, standard-library, and dependency defects remain operational trust
assumptions.

## Nondeterminism and platform scope

Direct repeats of an accepted ordered map and decomposed Unicode text under
`LC_ALL=C`, `LANG=C`, `TZ=UTC` from `/tmp` and under `C.UTF-8` with
`TZ=Pacific/Auckland` from the snapshot root produced byte-identical compact
JSON. The CLI output contains no timestamp, host path, localized prose, random
seed, or hash-map iteration dependence.

Executed platform evidence is limited to Ubuntu 24.04.4 LTS, Linux
7.0.0-28-generic, x86-64. No macOS, Windows, ARM, big-endian, alternate libc,
or release-mode equivalence is inferred. Process time and memory ceilings are
external conformance controls, not properties proved by the Rust type system.

## Lineage and authority boundary

The Rust behavior is rooted at `14f1ffb…`; the later frozen executable/lock
commit `fd8dd9e…` changes only end-of-file whitespace in `.gitignore` and
`rust-toolchain.toml`. The final profile clarification and the two 273-case
fixtures document field-specific raw digest behavior already implemented by
the Rust source. No Rust source or test changed between the behavior commit
and the reviewed implementation subject.

`schemas/prototypes/lineage.json` records distinct source roots, parser
lineages, and canonicalizer lineages for Python and Rust. Both `calls` and
`consumes_outputs_from` are empty. `minicbor` emits preferred primitive and
container heads only; the project code owns semantic types, raw parsing,
duplicate detection, Unicode validity/preservation, map sorting, limits,
framing, and validation staging. Differential output was not used as expected
truth.

The protected-path diff from the completed SQ-0004 baseline
`4aa0b9c145ce2595f3630d17abcfb7e4248579b4` through the reviewed subject is
empty for `backend/`, `lean/`, `frontends/`, `schemas/v0/`, and RFC-0006. The
crate has `publish = false`; the hosted workflow has read-only repository
permissions and no artifact-upload or release step.

## Toolchain, lock, dependencies, and notices

The executed toolchain was:

- `rustc 1.97.1 (8bab26f4f 2026-07-14)`, full commit
  `8bab26f4f68e0e26f0bb7960be334d5b520ea452`, LLVM 22.1.6;
- `cargo 1.97.1 (c980f4866 2026-06-30)`, full commit
  `c980f4866141969fab6254a680546a277789d6f0`;
- Cargo's observed libgit2 1.9.2, vendored libcurl 8.20.0-DEV, and OpenSSL
  3.6.2 are tool/runtime observations, not Cargo.lock dependencies.

Fresh offline `cargo +1.97.1 generate-lockfile` resolved 22 registry packages
and reproduced `Cargo.lock` byte-for-byte at SHA-256
`2e9c4f95aa0aa54ab2338e980d388f9f0223be8964d94f82d82f086f2dadb180`.
All 22 locally acquired `.crate` archives matched the checksums in that lock.
The normalized inventory excludes the workspace package and reports 22;
`cargo-audit` includes it in the lockfile total and reports 23.

Every locked registry package has a Cargo-declared license expression, exact
checksum, selected features, and dependency role. Every matching local crate
source tree contained at least one top-level license, copying, notice, or
unlicense file. Two easily lost obligations were inspected directly:

- `minicbor` 2.3.0 is `BlueOak-1.0.0`; packaged `LICENSE.md` SHA-256 is
  `79860758b46e85f70a1762c21a8fff4f2d220d89f9bdca096e12aed15b9951c5`;
- `unicode-ident` 1.0.24 is `(MIT OR Apache-2.0) AND Unicode-3.0`; packaged
  Unicode, Apache, and MIT notice hashes are respectively
  `f7db81051789b729fea528a63ec4c938fdcb93d9d61d97dc8cc2e9df6d47f2a1`,
  `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`,
  and `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`.

The inventory's `license_file: null` means Cargo metadata did not declare its
singular `license-file` field; it does not mean package license texts were
absent. The repository does not vendor those sources or retain a binary
third-party notice bundle. Approval therefore covers this source-only
Experimental prototype. Binary distribution, vendoring, or production release
requires a complete independently reviewed notice bundle, including the
Unicode copyright-and-permission notice. This is not legal advice or
redistribution clearance.

## Advisory and yanked-state review

The retained crates.io observation is bound to the exact lock and records all
22 packages as not yanked at `2026-08-09T14:15:00Z`. The offline checker
reproduced every name, version, and checksum. A fresh read-only query to the
official crates.io version API on the review date also reported all 22 exact
versions not yanked. That live result remains a transient registry observation,
not a maintenance or future-security guarantee.

The offline advisory reproduction verified these immutable inputs:

| Input | Exact identity |
|---|---|
| `cargo-audit` | 0.22.2 |
| `cargo-audit` archive SHA-256 | `ab28a1bdb54db4d5d8ad5981cf1f959410370b3d28250dbd35f6a44248620e39` |
| Extracted executable SHA-256 | `473b9a71e5cb5bde22f69c32f749c9b83931287d92dc36b91cb04f6705640ef2` |
| RustSec advisory database commit | `309ad29d8fe448bf986019e05d47b9e0e29a2218` |
| RustSec commit timestamp | `2026-08-09T12:34:06Z` |
| RustSec archive SHA-256 | `a5036fadecadb3e382f852b0d698460e931c85eb5e12e63447cc95875fe80256` |

With `--no-fetch --stale --no-yanked`, that exact scan reproduced zero
vulnerabilities and zero warnings. Wrong tool and advisory-database archives
were rejected on SHA-256 before extraction.

The zero result is only a dated RustSec match over the exact Cargo.lock graph.
It does not cover rustc, Cargo, LLVM, Cargo's libgit2/libcurl/OpenSSL stack, the
operating system, CPython, future advisories, live yanked state, malicious but
unadvised code, configuration defects, or unmodeled native/system behavior.
It is not a security guarantee.

## Commands and results

```text
rustc +1.97.1 -Vv
cargo +1.97.1 -Vv
  PASS: exact versions and commits above

cargo +1.97.1 fmt --all -- --check
cargo +1.97.1 build --all-features --locked --offline
cargo +1.97.1 clippy --all-targets --all-features --locked --offline -- -D warnings
cargo +1.97.1 test --all-targets --all-features --locked --offline
cargo +1.97.1 test --doc --locked --offline
  PASS: 9 CLI tests, 22 profile tests, 0 failures; doc tests pass

cargo +1.97.1 generate-lockfile --offline
cmp Cargo.lock Cargo.lock.expected
  PASS: byte-identical 22-package registry lock

PYTHONDONTWRITEBYTECODE=1 make check
  PASS: repository checks and 75 retained SQ-0002 toolchain probes

PYTHONDONTWRITEBYTECODE=1 make list-work
  PASS: SQ-0005 IN_PROGRESS at the implementation subject

PYTHONDONTWRITEBYTECODE=1 python3 scripts/serialization/run_conformance.py \
  --verify --rust-bin <locally built binary from the exact subject>
  PASS: 273 cases; 0 failures; 69 joint goldens; 20 mutations

PYTHONDONTWRITEBYTECODE=1 python3 scripts/serialization/dependency_inventory.py --check
  PASS: exact 22-package inventory

PYTHONDONTWRITEBYTECODE=1 python3 scripts/serialization/check_yanked.py
  PASS: retained 22-package record matches the exact lock

PYTHONDONTWRITEBYTECODE=1 python3 scripts/serialization/check_yanked.py --live
  PASS: official crates.io API reports all 22 exact versions not yanked

PYTHONDONTWRITEBYTECODE=1 python3 scripts/serialization/security_audit.py \
  --cargo-audit-archive <hash-matching 0.22.2 archive> \
  --rustsec-archive <hash-matching 309ad29 archive>
  PASS: 0 vulnerabilities; 0 warnings

python3 scripts/serialization/security_audit.py <wrong tool or DB archive>
  EXPECTED REJECTION: archive SHA-256 mismatch

git diff --check 410465d^ 410465d
  PASS
```

## Final scope and limitations

This approval establishes only that the exact Experimental Rust prototype is
a bounded, reproducible, independently reviewed producer of serialization
evidence. Replay is not verification. Numerical certification,
identification, inference, provenance, interpretation, schema meaning,
artifact validity, and kernel validity remain outside this review. Within
that scope, no Rust implementation, malformed-input/resource, lineage,
dependency/license, or point-in-time security blocker remains.
