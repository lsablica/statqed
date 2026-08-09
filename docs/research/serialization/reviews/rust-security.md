# SQ-0005 Rust prototype, parser, resource, and security review

Status: **Experimental review record**

Disposition: **APPROVE**

Review date: 2026-08-09

Reviewer: `/root/sq0004_workspace_msrv`, acting as the distinct Rust
prototype, parser/resource, and dependency-security reviewer

## Decision

The exact subject below is approved as an Experimental, non-normative Rust
prototype and as bounded interoperability evidence. The two blocking parser
findings from the review of commit
`2f0d778fff38bedd512dadd8603fc59e38be75b4` are resolved, and the previously
nonblocking mutable-span panic surface is closed. Exact Rust 1.97.1 gates,
offline lock reproduction, the 271-case differential suite, dependency and
retained-yanked checks, and the hash-bound RustSec reproduction all pass.

This approval is deliberately narrower than SQ-0005 acceptance. It does not
approve RFC-0001, ADR-0004, the final static evidence package, a distributable
binary, or any production backend. It does not make Rust, Cargo, the parser,
the CLI, `minicbor`, `serde_json`, `sha2`, the conformance harness, or their
outputs semantic or kernel authority.

## Exact subject and hashes

The shared worktree advanced during this review. All substantive inspection
and execution used a clean `git archive` snapshot of the assigned subject,
not the later worktree head.

| Subject | Exact identity |
|---|---|
| Reviewed commit | `71d637eadf3bfce1c9b1502c63e74fc3922ef300` |
| Reviewed repository tree | `5e8c519ce047566b0f73a37b8a3806fe713e5e54` |
| Reviewed commit parent | `bc5a38deb4b886fcc2ac9afab4615b9dc837b8c9` |
| Reviewed commit subject | `Record independent serialization conformance review` |
| Rust prototype Git tree | `0e265a068642258e2f1eab0751c40872d1be3ee0` |
| Frozen behavior commit | `14f1ffb0646b280fea805fbec6ba6bb8b3d1a282` |

### Prototype files

| File | SHA-256 |
|---|---|
| `schemas/prototypes/rust-cbor/README.md` | `a73f4319d96482f401acb9124fb7c036f195831a6bcc1825ac93a532eaec1680` |
| `schemas/prototypes/rust-cbor/LICENSE` | `e2135b5acb4ab6f5c9d9ac8b4be2d6bcdb0da6a6262fd990ef9117ca44383dd4` |
| `schemas/prototypes/rust-cbor/Cargo.toml` | `37e51170459929bd4a674eca8a2a0168f976de7191eb886ee193c360b8fc6fad` |
| `schemas/prototypes/rust-cbor/Cargo.lock` | `2e9c4f95aa0aa54ab2338e980d388f9f0223be8964d94f82d82f086f2dadb180` |
| `schemas/prototypes/rust-cbor/rust-toolchain.toml` | `da4fa49758e2d8da0f35f79049581134c98b02db0176e515e62367bf9242047c` |
| `schemas/prototypes/rust-cbor/src/lib.rs` | `bf5cd89521f4151197beeb8a9e07d9a92503e615de9c9da2aec1d6f73834d70d` |
| `schemas/prototypes/rust-cbor/src/main.rs` | `a48b67f10d0a7a77d553b226c73d02dae48057d66be83cfd6c517c8ae925f211` |
| `schemas/prototypes/rust-cbor/tests/profile.rs` | `f278b61f959f4f71b707c2a424b879fbb71922a85e5b79ecbf3258ee729d1ae3` |
| `schemas/prototypes/rust-cbor/tests/cli.rs` | `311f5f7faa50664e1f89dc4cb6f7a7a39abf65a1a05f8b809e9b23c1987d2ba9` |
| `schemas/prototypes/rust-cbor/DEPENDENCIES.md` | `90a4c6c9f01684e0659a6f590911a0f068e6c28697c1cab42d00db8765358ec0` |
| `schemas/prototypes/rust-cbor/LINEAGE.md` | `26e7c178c04886b57b7e8ab5dd335f3544e6cd02b9fc5da3b11dfcce9ea36aef` |

### Security and resource evidence

| File | SHA-256 |
|---|---|
| `schemas/prototypes/rust-cbor/evidence/security-lock.json` | `58940480cb4ca163ee5ec1e2bf5a9e3165371e96703018c3ebd147775c8ac0f5` |
| `schemas/prototypes/rust-cbor/evidence/advisory-report.json` | `abe01dc61e4f02fb179f39457077b832491c3503d8461fe82f1835712482cd55` |
| `schemas/prototypes/rust-cbor/evidence/crates-io-yanked.json` | `fd69cb31758d9f3da5f674a3b14b731bda03ba77e9ca1295e03663d67e571e2b` |
| `schemas/prototypes/rust-cbor/evidence/dependency-license-inventory.json` | `3d44e9d26c756c2aa950779f9fcf557f11efc28a50d20f27c2ec1a501aaadfa9` |
| `scripts/serialization/security_audit.py` | `d31f7baf094049d5d8437d6fd104af25874c0530e9f18f792ed629dfcf16ee39` |
| `scripts/serialization/check_yanked.py` | `073079e06bdf7e3bb291de3c229530ae695a57a6bcf6e1de9489e36cd2381ca5` |
| `scripts/serialization/dependency_inventory.py` | `b21d621e57943e6ddfbdbc4de8c01e8ecb99843b2746fbd953b3c4329e35c24d` |
| `scripts/serialization/run_conformance.py` | `e78edf3b0cb4411755bd67a2019567eecd61e81e7821d590d251a0eca34cb0cd` |
| `conformance/prototypes/fixtures/semantic-v1/resources.json` | `984a142eb002a38d4f137a98d44c222fe2bf56dd2147808608372cb0f7ad0039` |
| `conformance/prototypes/generated-v1/manifest.json` | `9157bf5cc331b026353e12de4adbe9a623509aac9ef6e2a1e8fc22eba71f1d0d` |
| `conformance/prototypes/generated-v1/results.json` | `4ad3b4c121e0a1008ce783d8aaa5f80a43df187b8725ad918bbd78fa244dcdf0` |

## Resolution of earlier findings

| Earlier finding | Final behavior | Result |
|---|---|---|
| Trailing-byte expectedness masked validity faults in the parsed root. | `decode_raw` retains the consumed boundary; `validate_raw_with_expectations` validates CBOR validity before checking trailing bytes. `61ff00` returns `validity.invalid_utf8` at offset 1, and `a200f400f500` returns `validity.map_duplicate` at offset 3. | Resolved |
| Indefinite byte/text chunks were omitted from the total-item counter. | One indefinite root plus 4,095 empty chunks reaches exactly 4,096 items and returns `profile.indefinite`; one root plus 4,096 chunks returns `resource.total_items`. Both byte and text strings are tested. | Resolved |
| Public mutable raw spans could be corrupted and then indexed. | `RawNode`, `RawMapEntry`, and `RawDocument` structural fields are private; accessors are immutable; `RawDocument::encoded` uses checked slicing and returns `None` for a node from another document. | Resolved |

The internal validator still uses direct slicing for nodes constructed by its
own parser. Those ranges and the owning source are private and immutable. No
external path can construct or replace such a node. Three production
`unreachable!` branches remain, but their predicates are fixed by a three-bit
major type, a five-bit additional-information value, and internal literal
subjects. I found no input-reachable panic path.

## Malformed, resource, process, and determinism assessment

The parser checks declared string, collection, total-item, depth, input,
output, diagnostic, typed-JSON, and digest-frame limits before the associated
unbounded work. In particular, declared byte-string lengths `2^32-1` and
`2^32` return `resource.string_bytes` without body allocation; raw and typed
depth 32 is admitted where specified and depth 33 is rejected; a 2,000-level
typed-JSON input is rejected by lexical preflight before `serde_json`; and
canonical one-megabyte boundaries are exercised under an external 128 MiB
address-space ceiling.

The fresh differential verification passed 271 cases with zero failures, 69
joint goldens, and 20 detected mutations. Of those, 248 invoked the Rust
implementation: none had an operational/unavailable outcome, stderr, a
negative return code, timeout, crash, or exception. The timeout, memory,
crash, and exception recipes are harness-level fail-closed tests. They produce
`operational.*`, never `accepted`; they do not prove that Rust allocation is
recoverable after the allocator or operating system terminates a process.

Direct repeats of an accepted ordered map and decomposed Unicode text under
`LC_ALL=C`, `LANG=C`, `TZ=UTC` from `/tmp` and under `C.UTF-8` with
`TZ=Pacific/Auckland` from the snapshot root produced byte-identical compact
JSON. Output has no timestamp, host path, localized text, random seed, or
iteration-order dependence. This is direct Linux/x86-64 evidence, not a claim
for unexecuted operating systems or architectures.

The crate forbids unsafe Rust and denies Clippy `all`, `pedantic`, `unwrap`,
`expect`, and `panic` lints. This does not eliminate allocator aborts, compiler
defects, dependency defects, or the three reviewed invariant-only
`unreachable!` sites; those remain operational trust assumptions and fail
closed at the external harness.

## Toolchain, lock, dependencies, advisories, and yanked state

The executed toolchain was:

- `rustc 1.97.1 (8bab26f4f 2026-07-14)`, full commit
  `8bab26f4f68e0e26f0bb7960be334d5b520ea452`, LLVM 22.1.6;
- `cargo 1.97.1 (c980f4866 2026-06-30)`;
- Ubuntu 24.04.4 LTS, Linux 7.0.0-28-generic, x86-64.

Fresh offline `cargo +1.97.1 generate-lockfile` resolved 22 registry packages
and reproduced `Cargo.lock` byte-for-byte at SHA-256
`2e9c4f95aa0aa54ab2338e980d388f9f0223be8964d94f82d82f086f2dadb180`.
All 22 locally acquired `.crate` archives matched the checksums in that lock.
The dependency inventory excludes the workspace package and therefore reports
22; `cargo-audit` includes it in the lockfile total and reports 23.

The retained official-crates.io observation is bound to the same lock. It
records all 22 exact packages as not yanked at `2026-08-09T14:15:00Z`. The
offline checker reproduced the package names, versions, and checksums. This is
not a claim about live registry state after that timestamp; the hosted workflow
must repeat the fail-closed live query.

The offline advisory reproduction verified all of these immutable inputs:

| Input | Exact identity |
|---|---|
| `cargo-audit` release | 0.22.2 |
| `cargo-audit` archive SHA-256 | `ab28a1bdb54db4d5d8ad5981cf1f959410370b3d28250dbd35f6a44248620e39` |
| Extracted executable SHA-256 | `473b9a71e5cb5bde22f69c32f749c9b83931287d92dc36b91cb04f6705640ef2` |
| RustSec advisory database commit | `309ad29d8fe448bf986019e05d47b9e0e29a2218` |
| RustSec commit timestamp | `2026-08-09T12:34:06Z` |
| RustSec archive SHA-256 | `a5036fadecadb3e382f852b0d698460e931c85eb5e12e63447cc95875fe80256` |

With `--no-fetch --stale --no-yanked`, that exact scan reproduced zero
vulnerabilities and zero warnings. Supplying a wrong tool archive or wrong
database archive failed before extraction on its SHA-256 check.

The zero result is only a dated RustSec match over the exact Cargo.lock graph.
It does not cover rustc, Cargo, LLVM, the operating system, CPython, future
advisories, yanked state, malicious-but-unadvised code, configuration defects,
or unmodeled native/system behavior. It is not a security guarantee.

## License and notice boundary

The normalized inventory gives every locked registry package a Cargo-declared
license expression and binds its crate checksum, feature set, and role. All 22
checksum-matching local crate source trees contained at least one top-level
license, copying, notice, or unlicense file. Two easily lost obligations were
inspected directly:

- `minicbor` 2.3.0 is `BlueOak-1.0.0`; its packaged `LICENSE.md` SHA-256 is
  `79860758b46e85f70a1762c21a8fff4f2d220d89f9bdca096e12aed15b9951c5`.
  `DEPENDENCIES.md` supplies the required Blue Oak 1.0.0 link.
- `unicode-ident` 1.0.24 is `(MIT OR Apache-2.0) AND Unicode-3.0`; its packaged
  Unicode notice SHA-256 is
  `f7db81051789b729fea528a63ec4c938fdcb93d9d61d97dc8cc2e9df6d47f2a1`.
  Its packaged Apache and MIT texts have SHA-256
  `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`
  and `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`.

The inventory's `license_file: null` means Cargo metadata did not declare the
singular `license-file` field; it does not mean the crate archives lacked
license texts. The repository does not vendor dependency source, publish this
crate (`publish = false`), upload a built artifact, or retain a third-party
binary notice bundle. Approval therefore covers the source-only Experimental
prototype. Any binary distribution, vendoring, or production release must
assemble and independently review the complete applicable notice bundle,
including the Unicode copyright-and-permission notice. This review is not
legal advice or redistribution clearance.

## Commands and results

```text
rustc +1.97.1 -Vv
cargo +1.97.1 -V
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
  PASS: correctly reports SQ-0005 IN_PROGRESS at this pre-integration subject

PYTHONDONTWRITEBYTECODE=1 python3 scripts/serialization/run_conformance.py \
  --verify --rust-bin <exact locally built binary>
  PASS: 271 cases; 0 failures; 69 joint goldens; 20 mutations

PYTHONDONTWRITEBYTECODE=1 python3 scripts/serialization/dependency_inventory.py --check
  PASS: exact 22-package inventory

PYTHONDONTWRITEBYTECODE=1 python3 scripts/serialization/check_yanked.py
  PASS: retained 22-package observation matches the exact lock

PYTHONDONTWRITEBYTECODE=1 python3 scripts/serialization/security_audit.py \
  --cargo-audit-archive <hash-matching 0.22.2 archive> \
  --rustsec-archive <hash-matching 309ad29 archive>
  PASS: 0 vulnerabilities; 0 warnings

python3 scripts/serialization/security_audit.py <wrong tool or DB archive>
  EXPECTED REJECTION: archive SHA-256 mismatch

git diff --check 71d637e^ 71d637e
  PASS
```

The future static-evidence corruption suite is not a gate for this exact
pre-integration Rust subject. A deliberate exploratory run of
`python3 -m unittest discover -s scripts/serialization/tests` at `71d637e`
failed because `conformance/prototypes/evidence/evidence-manifest.json` did not
yet exist. The final SQ-0005 integration subject must create that manifest and
rerun the static verifier and all corruption tests; no pass is claimed here.

## Authority and remaining limitations

The diff from the completed SQ-0004 baseline
`4aa0b9c145ce2595f3630d17abcfb7e4248579b4` through the reviewed commit is
empty for `backend/`, `lean/`, `frontends/`, `schemas/v0/`, and RFC-0006. The
prototype is `publish = false`; the workflow has read-only repository
permissions and no artifact-upload or release step.

Accordingly, this approval establishes only that the exact Experimental Rust
prototype is a bounded, reproducible, independently reviewed producer of
serialization evidence. Replay is not verification. Numerical certification,
identification, inference, provenance, interpretation, schema meaning,
artifact validity, and kernel validity remain outside this review. Within
that scope, no Rust prototype, parser/resource, dependency, or point-in-time
security blocker remains.
