# SQ-0005 CI and release-boundary review

Status: **Experimental review record**

Disposition: **APPROVE FOR HOSTED EXECUTION**

Review date: 2026-08-09

Reviewer: `/root/sq0005_ci_release_backup`, acting as the distinct CI,
reproducibility, dependency-gate, and release-boundary reviewer

## Decision

The exact implementation subject and workflow below are approved for hosted
execution. The workflow is least-privilege, uses exact action commits and exact
language patch versions, separates dependency acquisition from locked offline
Rust execution, checks lock and evidence regeneration, and exercises the
retained conformance, corruption, license, yanked-state, and advisory paths.

This is a conditional pre-hosted disposition. It is not permission to merge,
accept RFC-0001, mark ADR-0004 Accepted, or mark SQ-0005 DONE. Final approval
requires the workflow to pass on the exact final post-transition pull-request
head, including the then-present evidence manifest and final ledger states, and
to pass again on the merged `main` commit. The observed hosted image metadata
must be retained with those runs.

## Exact subject

| Subject | Exact identity |
|---|---|
| Reviewed implementation commit | `410465d773fc011ee01e38e6e76a79a60efe8837` |
| Reviewed repository tree | `a93ac8fe4befe4da52ff0ef5ee928ea04679b85c` |
| Workflow | `.github/workflows/serialization-prototypes.yml` |
| Workflow SHA-256 | `ee7b9643374d001cd595f4232d42780bdf70b8c78c2cbe0396551501d3674117` |
| Cargo.lock SHA-256 | `2e9c4f95aa0aa54ab2338e980d388f9f0223be8964d94f82d82f086f2dadb180` |
| Conformance runner SHA-256 | `8a61f6deeeba7bed4e8bb7e0c8202fa0ce730d5328036365d8536ed5950fe01c` |
| Static evidence verifier SHA-256 | `864568ef80e2c1f0517999cf45130f744c6599eab34040932f1fa0258e0c7d0e` |
| Dependency inventory SHA-256 | `3d44e9d26c756c2aa950779f9fcf557f11efc28a50d20f27c2ec1a501aaadfa9` |
| Retained yanked-state record SHA-256 | `fd69cb31758d9f3da5f674a3b14b731bda03ba77e9ca1295e03663d67e571e2b` |
| Retained advisory report SHA-256 | `abe01dc61e4f02fb179f39457077b832491c3503d8461fe82f1835712482cd55` |
| Security reproducer SHA-256 | `d31f7baf094049d5d8437d6fd104af25874c0530e9f18f792ed629dfcf16ee39` |

The workflow and implementation paths above are byte-identical between the
reviewed commit and the review-time branch. Later commits visible during this
review changed specialist review records, not the workflow or implementations.

## Workflow authority and action pins

The workflow runs for pull requests, pushes to `main`, and manual dispatch. It
does not use `pull_request_target`. Top-level permissions are exactly
`contents: read`; both checkouts set `persist-credentials: false`; there is no
write permission, artifact upload, package publication, release, deployment,
or token-bearing step. Job timeouts are 20 and 60 minutes. Workflow concurrency
is explicit and cancels superseded pull-request and push runs.

Every `uses:` reference is a 40-hex commit:

- `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1`,
  verified through the official GitHub API as tag `v7.0.1`;
- `actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97`,
  verified through the official GitHub API as tag `v7.0.0`.

There is no floating action tag, branch, or `@latest`. The hosted runner label
`ubuntu-24.04` remains a mutable service label; the workflow records
`RUNNER_OS`, `RUNNER_ARCH`, `RUNNER_NAME`, `ImageOS`, `ImageVersion`,
`/etc/os-release`, `uname`, tool versions, and the exact repository commit.
Its comments correctly limit direct evidence to the observed hosted runner and
do not infer macOS, Windows, ARM, big-endian, alternate-libc, or immutable
Linux support.

## Python matrix

The independent-oracle job selects exact CPython `3.12.13` and `3.14.7`, runs
the standard-library test suite with `-S`, errors on warnings, disables bytecode
generation, proves the requirements file has no effective third-party entry,
rejects `__pycache__`/bytecode residue, and ends with clean-diff checks.

Official `actions/python-versions` release records were available at review
time for both exact patches: `3.12.13-27650778726` (published 2026-06-16) and
`3.14.7-31064857500` (published 2026-08-06). Local execution directly covered
only conda-forge CPython 3.12.13; all 57 oracle tests passed. CPython 3.14.7 is
therefore a configured hosted candidate until the exact workflow run succeeds,
not local or cross-platform support evidence.

## Rust acquisition, offline execution, and lock drift

The conformance job installs exact Rust 1.97.1 with the minimal profile plus
rustfmt and Clippy, and records full Rust and Cargo version output. Dependency
acquisition then uses a new runner-temporary `CARGO_HOME` and target directory,
rejects ambient Cargo credential variables and credential/config files, and
fetches only the committed graph with `--locked`. The runner-created Cargo
locations are passed to later steps explicitly.

After acquisition, formatting, build, Clippy with warnings denied, all-target
tests, and doc tests run with the exact toolchain and locked/offline graph.
Cargo network access is disabled for those gates. A separate runner-temporary
copy removes its lock, regenerates it offline, compares it byte-for-byte, and
checks the fixed lock SHA-256. Thus Rust 1.97.1 performs acquisition, while the
actual verification gates do not silently acquire or rewrite dependencies.

Fresh local review execution with Rust 1.97.1 passed format, locked/offline
build, Clippy, 31 unit/integration tests (9 CLI and 22 profile), and doc tests.
SQ-0005's isolated prototype declares 1.97.1 as its own minimum and does not
claim that the production backend's distinct Rust 1.85.1 floor applies to this
research crate.

## Conformance, evidence, license, and advisory gates

The workflow runs repository guardrails, the permanent evidence verifier,
the 273-case differential conformance verifier, deliberate divergence and
resource checks embedded in that runner, source-audit regeneration, evidence
corruption tests, evidence-manifest regeneration, and a final clean diff.
Consequently a changed generated result, golden, failure record, review binding,
or manifest cannot pass merely because one implementation changed.

The dependency inventory is regenerated from exact locked/offline Cargo
metadata and must byte-match the retained normalized inventory. The retained
crates.io checksum/yanked record is checked offline, then CI performs a separate
fail-closed live query for all 22 exact package versions. This live query is a
current registry observation, deliberately not deterministic historical
evidence.

The advisory step downloads cargo-audit 0.22.2 and RustSec database commit
`309ad29d8fe448bf986019e05d47b9e0e29a2218`; immutable content hashes are
checked before safe extraction and execution. The reproducer uses isolated
home and Cargo directories, disables database fetching and yanked lookup, and
requires the retained zero-vulnerability/zero-warning report to reproduce.
This is a lock-bound point-in-time observation, not a security guarantee.

Every locked crate has an exact checksum and Cargo-declared license expression
in the normalized inventory. The separate Rust/security review inspected
packaged license/notice material. This workflow does not create a distributable
third-party notice bundle, so the branch remains source-only Experimental
evidence and the absence of any release/upload step is required. Binary or
package distribution needs a fresh complete license/notices review.

## Update, rollback, and release boundary

The RFC candidate and implementation specification require a semantic/profile
change to reopen RFC-0001 and refresh sources, fixtures, both implementations,
locks, license/advisory evidence, workflow, and reviews together. Rollback must
restore one complete previously reviewed evidence set and identifiers; partial
rollback fails as evidence drift. The workflow's fixed toolchain, action,
Cargo.lock, advisory archive, database, and evidence hashes support that policy.

No prototype is production authority. CI agreement does not prove artifact
validity, source fidelity, logical-data identity, provenance, cryptographic
collision absence, proof validity, or statistical validity. RFC-0006 and
production `backend/`, `lean/`, and frontend code remain outside this review.

## Commands and results

```text
git diff --exit-code 410465d773fc011ee01e38e6e76a79a60efe8837 -- \
  .github/workflows/serialization-prototypes.yml schemas/prototypes \
  scripts/serialization conformance/prototypes \
  rfcs/0001-deterministic-encoding.md \
  docs/adr/0004-deterministic-cbor-cddl.md \
  docs/spec/canonicalization.md
  PASS: implementation subject unchanged at review time

static workflow assertions
  PASS: all actions use 40-hex commits; contents:read; checkout credentials
  disabled; explicit timeouts/concurrency; no pull_request_target

official GitHub API tag checks
  PASS: checkout v7.0.1 and setup-python v7.0.0 resolve to configured commits

official actions/python-versions release checks
  PASS: exact 3.12.13 and 3.14.7 hosted tool releases exist

make check
  PASS: pre-transition repository checks and SQ-0002 verifier

make list-work
  PASS: SQ-0005 IN_PROGRESS; SQ-0008 READY

CPython 3.12.13 standard-library oracle suite
  PASS: 57 tests

Rust 1.97.1 fmt/build/clippy/test/doc with --locked --offline
  PASS: format; build; Clippy -D warnings; 31 tests; doc tests
```

## Conditions before merge

1. Build the final evidence manifest only after the atomic RFC/ADR/task/status
   transition and exact final specialist reviews are present.
2. Run `serialization-prototypes` on that exact pull-request head. Both exact
   Python matrix jobs and the conformance job must succeed; retain run ID,
   commit, timestamps, and observed runner-image metadata.
3. Confirm `make check` invokes the SQ-0005 permanent evidence verifier in the
   final state and that the explicit verifier, corruption suite, conformance,
   clean regeneration, lock, live-yanked, license-inventory, and immutable
   advisory gates all pass in the hosted run.
4. Recheck that the workflow file hash remains
   `ee7b9643374d001cd595f4232d42780bdf70b8c78c2cbe0396551501d3674117`;
   any workflow change invalidates this disposition and requires re-review.
5. After merge, require the same workflow to pass on the exact `main` merge
   commit before the default branch is described as green.

Subject to those conditions, there is no CI, reproducibility, dependency-gate,
platform-claim, or release-boundary blocker to hosted execution.
