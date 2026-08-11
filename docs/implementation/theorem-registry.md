# Theorem registry v0 implementation

Status: Experimental and test-only.

## Exact environment

- Lean `v4.32.2`, source `f3b06c705e6c85f5314019d5d3baab0fec5b580c`;
- Lake `5.0.0-src+f3b06c7`;
- Mathlib `905b95818eb32af7874a58b427f50c1711a5e96c`;
- Rust development `1.97.1` and locked-offline floor `1.85.1`;
- Python standard library from the reviewed project environment.

## Layout and responsibilities

- `lean/StatQED/Registry/` extracts typed live propositions, kind-specific
  closure, proof subjects, and transitive axiom observations. It is the primary
  environment observation, not an external verifier.
- `scripts/registry/independent_oracle.py` independently implements the v0
  expression grammar, canonical CBOR and digest domains without importing the
  primary model, Rust resolver, or SQ-0005 oracle.
- `scripts/registry/build_registry.py` is the deterministic comparison and
  record generator.
- `backend/crates/statqed-registry/` is a standalone, std-only, bounded offline
  resolver. Its key/value transport is operational and non-normative.
- `scripts/registry/check_evidence.py` permanently binds evidence and live
  predecessor invariants.

## Build and verify

```bash
cd lean
lake build
lake env lean --trust=0 StatQED/Registry/Tests/Smoke.lean
lake env lean --trust=0 StatQED/Registry/Tools/AxiomReport.lean
lake env leanchecker --fresh StatQED.Registry.Tests.Smoke

cd ..
python3 scripts/registry/build_registry.py --check
python3 scripts/registry/check_axiom_report.py --check theorem-registry/evidence/axioms.json
python3 scripts/registry/run_conformance.py --verify
python3 scripts/registry/check_evidence.py
python3 -m unittest discover -s scripts/registry/tests -p 'test_*.py' -v

cd backend/crates/statqed-registry
cargo +1.97.1 fmt --check
cargo +1.97.1 clippy --all-targets --all-features --locked -- -D warnings
cargo +1.97.1 test --all-features --locked
cargo +1.85.1 test --all-features --locked --offline
```

Use `python3 scripts/registry/build_registry.py` and
`python3 scripts/registry/run_conformance.py` only for intentional reviewed
regeneration. `--check` and `--verify` are the normal fail-closed modes.

## Results and error surface

The corpus separates proposition normalization, environment closure, record,
authorization, proof/build, axiom, compatibility, resource, and operational
failures. Stable `registry.*` codes contain no timestamps, random values, host
paths, locale text, or dependency debug strings. Limits are tested at accepted
and one-over boundaries.

## Supply chain and platform

The Rust workspace contains only its unpublished local package, so Cargo.lock
has no registry source, checksum, build script, native dependency, advisory
match, or yanked crate. This N/A observation is not a security guarantee. The
directly tested platform is Ubuntu 24.04 x86-64; hosted CI records its observed
runner metadata without extrapolating macOS, Windows, ARM, or immutable Linux
support.

## Trusted computing base

Lean's kernel and pinned environment check the named declarations. The local
authorization policy is a verifier input. The resolver and hash implementations
are security-critical operational code but do not become mathematical proof.
Elan, Lake, Git, Python, Rust/Cargo, the OS, filesystem, CI runner, agents, and
report generators remain operational dependencies outside the logical kernel
TCB. `collectAxioms` is an observation with documented extension and missing-
constant limitations; same-kernel fresh replay is not independent verification.

## Update and rollback

Any grammar, closure, record, lock, policy, error, or limit change requires a
new version, regenerated evidence, all mutation gates, RFC/ADR review, and an
authorized root update. Toolchain changes additionally require Lean/Rust source
and supply-chain review. Rollback restores the last authorized root, exact
record/lock subjects, toolchain pins, and manifest together; individual hashes
must never be mixed across versions.

## Explicit nonclaims

V0 does not establish a public/statistical theorem, non-vacuity, source
fidelity, theorem equality from hashes, artifact-byte binding, logical-data
identity, certificate/checker soundness, external-premise truth, provenance,
interpretation, or statistical validity.
