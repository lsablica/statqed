# Retained SQ-0002 Failures

Status: **Draft research evidence**.

Failures are first-class compatibility evidence. Exact commands, timestamps,
stdout, and stderr are indexed by `matrix.json`; this file is the human map.

## Lean/Mathlib/Lake

- Network-disabled tag lookup and toolchain/dependency downloads failed rather
  than being mistaken for local compatibility failures.
- Interrupted dependency clones produced no usable manifest and remain
  classified unknown.
- A retry after an incomplete clone exposed a stale cache-executable link
  failure; package-scoped cleaning recovered the same immutable lock.
- Three rejected proof bodies exposed `sorryAx`; the accepted proof body does
  not. These failures are not proof evidence.
- Lean 4.31.0 with Mathlib commit `520045ab14e26149ee970e2e617ca04b09bde5d6`
  fails in `Mathlib.Init`, rejecting a compiler-range interpretation of one
  fixed Mathlib revision.

## Rust/Cargo

- A fully isolated empty `CARGO_HOME` lacked the rustup proxy and failed after
  download; the corrected layout separates rustup from build/registry caches.
- Initial formatting and SHA-2 API assumptions failed and were corrected
  before the passing lint/test evidence.
- The unsafe fixture is rejected by `forbid(unsafe_code)`; that does not make
  transitive dependencies or the compiler unsafe-free.
- `zip` 8.1.0 builds on Rust 1.97.1 but Cargo rejects it on Rust 1.85.1 because
  it declares Rust 1.88. The 7.2.0 compatibility candidate remains only a
  library probe, not an artifact-envelope decision.

## Python

- Cold or ordinary caches did not make network-disabled build isolation
  reproducible; a hash-locked wheelhouse was required.
- CPython 3.10.20 is rejected by the prototype's `Requires-Python >=3.11`
  metadata.

## R

- The conda-forge solver could not combine R 4.6.1 with the available
  `testthat` 3.3.2 builds. The accepted development probe instead installs a
  SHA-256-locked CRAN source closure; the R 4.4.3 floor is recreated offline
  from an explicit conda artifact lock.
- A mutated package requiring R 4.7.0 failed both check-time installation and
  direct installation under R 4.6.1.
- macOS and Windows were unavailable and remain unknown, with later runner
  commands recorded rather than inferred from Linux.

## Julia

- Three fresh-depot attempts tried to bootstrap the mutable General registry
  and failed DNS. They remain rejected. The accepted Stable/LTS probes use a
  fixed empty local registry because the package has no registry dependencies.
- A mutated Julia 1.13 compatibility bound failed resolution under 1.12.6.

## Arrow

- The host Python lacked the required virtual-environment support; the final
  probe used the exact isolated CPython asset instead.
- R Arrow was not installed and Julia Arrow was not prepared, so those language
  combinations remain unknown.
- File and stream IPC forms produced different physical bytes. No observation
  here defines canonical bytes or logical-data identity.

## CBOR and CDDL

- `cbor2` accepted a top-level break sentinel, contradicting an initial probe
  assumption; duplicate-key, indefinite-length, and ordering behavior also
  differed across candidate implementations.
- `cddl` 0.10.6 built on Rust 1.97.1 but its locked graph requires Rust 1.88,
  so it failed the proposed Rust 1.85.1 MSRV.
- These results require later strict-profile and conformance decisions. They do
  not accept RFC-0001 or choose normative decoder behavior.
