# StatQED registry resolver prototype

This standalone Cargo workspace contains the Experimental, bounded, offline
resolver for the single ADR-0011 test-only theorem-registry record. It is not
part of the parent Rust workspace and has no production artifact authority.

The resolver consumes an operational line-oriented transport and a separately
provided trusted policy. The transport is deliberately not described as the
normative registry encoding. Normative identities are represented by distinct
lower-case SHA-256 digest values for proposition, environment, registry record,
authorization, proof/build, axiom observation, and compatibility evidence.
Canonical subjects and framed digests are recomputed by the composed Python
verifier before this resolver is invoked. This crate compares the resulting
separated bindings with verifier-selected policy; it does not parse canonical
CBOR, Lean expressions, or proof-lock payloads and is not an independent
canonical-byte oracle.

The crate has no third-party dependencies, build script, network fallback,
ambient credential use, unsafe code, or locale-dependent error text.

Development checks:

```text
cargo +1.97.1 fmt --check
cargo +1.97.1 clippy --all-targets --all-features --locked -- -D warnings
cargo +1.97.1 test --all-features --locked
cargo +1.85.1 test --all-features --locked --offline
```

Rust 1.97.1 is the development and lock-generation toolchain. Rust 1.85.1 is
only the locked, offline API-compatibility floor.

Passing resolution establishes only that the supplied test-only record agrees
with the verifier-selected local policy and the expected evidence bindings. It
does not prove source fidelity, external truth, statistical validity, artifact
verification, theorem non-vacuity, or collision freedom.
