# Rust prototype implementation lineage

Status: **Experimental evidence record**.

This record binds the isolated SQ-0005 Rust prototype to the exact candidate
inputs used for its current behavior:

| Input | Source commit | SHA-256 |
|---|---|---|
| `docs/research/serialization/semantic-value-model.md` | `ac5ce971eca4f46e7725f56599e5a30e7025bd22` | `fc7d86cfe4eae00d25afeb1cd8601dff6d5173dce728c5f4a507b20d5fa34dca` |
| `docs/research/serialization/profile-candidate.md` | `07b9461fef39dd0d81f1bce57f47e5c581b42956` | `d07816f7f3fadeb07b91196691848f3933a13f96503c86ed24c2ed9d42ed45bb` |

The committed semantic-v1 corpus used for adversarial comparison is rooted at
`d21e411fa5331c57b0e89d2b6bd57384317c1572`. A content change to either
candidate input invalidates this lineage record until the Rust prototype is
reviewed and retested.

## Implementation ownership and library boundary

The raw CBOR parser, ordered raw-map-entry representation, duplicate scan,
UTF-8 validation, expectedness and deterministic-profile staging, resource
counters, tag/indefinite handling, semantic conversion, map sorting policy,
length-prefix framing, and digest verification are implemented directly in
this Rust crate from the candidate documents and their cited RFC/FIPS rules.
They are not delegated to a generic CBOR decoder or native map.

`minicbor` 2.3.0 is used only to emit preferred primitive and container heads
after the crate has validated the semantic value and selected canonical map
order. Its reviewed upstream lineage is `twittner/minicbor` commit
`67b22f849a0ff12b669a0c304236ffe9744f9a79`, crate path `minicbor`; its
crates.io checksum is recorded in `DEPENDENCIES.md`. `minicbor` decoding,
native maps, tags, floats, and indefinite encoders do not define this profile.

No Python oracle implementation source or Python-produced byte stream,
semantic projection, digest, frame, or test result was consumed as expected
truth while implementing the Rust behavior. The public Python README was
consulted only for diagnostic CLI field-name interoperability. Agreement with
the independently owned Python implementation is established only by the
separate differential harness.

## Toolchain, dependency, and authority boundary

The exact Rust toolchain is bound by `rust-toolchain.toml` SHA-256
`da4fa49758e2d8da0f35f79049581134c98b02db0176e515e62367bf9242047c`.
The dependency constraints are bound by `Cargo.toml` SHA-256
`37e51170459929bd4a674eca8a2a0168f976de7191eb886ee193c360b8fc6fad`.
Offline lock regeneration produces 22 packages and `Cargo.lock` SHA-256
`2e9c4f95aa0aa54ab2338e980d388f9f0223be8964d94f82d82f086f2dadb180`.
Dependency versions, checksums, upstream lineage, and licenses are enumerated
in `DEPENDENCIES.md`.

This prototype and its CLI evidence channels remain Experimental research
artifacts. They are not production authority, are outside the verification
trusted computing base, do not resolve object-class/schema identifiers, and do
not establish artifact, provenance, statistical, inferential, or kernel
validity. No generated source is present; repository source is under the root
MIT license, with dependency terms recorded separately.
