# Dependency, lineage, and license inventory

Status: **Experimental point-in-time inventory**, recorded 2026-08-09 for
SQ-0005. `Cargo.lock` SHA-256 after exact offline generation:
`2e9c4f95aa0aa54ab2338e980d388f9f0223be8964d94f82d82f086f2dadb180`.

Top-level behavior-bearing libraries:

| Crate | Version | crates.io checksum | Upstream release lineage | License | Role and limitation |
|---|---:|---|---|---|---|
| `minicbor` | 2.3.0 | `c12b4033ffaa92fbf9df03df38d19324f52bad130dd223f811734a8006dd2d69` | `twittner/minicbor` commit `67b22f849a0ff12b669a0c304236ffe9744f9a79`, crate path `minicbor` | [BlueOak-1.0.0](https://blueoakcouncil.org/license/1.0.0) | preferred primitive/header emission only; no native-map or decoder authority |
| `serde_json` | 1.0.151 | `c841b55ecdae098c80dcae9cf767f6f8a0c2cdb3416bbef72181df4d0fe73f14` | `serde-rs/json` commit `de8500740cdcabffb9734f503e4889def823cf10` | MIT OR Apache-2.0 | non-normative typed JSON diagnostic/evidence transport only |
| `sha2` | 0.11.0 | `446ba717509524cb3f22f17ecc096f10f4822d76ab5c0b9822c5f9c284e825f4` | `RustCrypto/hashes` commit `ffe093984c004769747e998f77da8ff7c0e7a765`, crate path `sha2` | MIT OR Apache-2.0 | SHA-256 for generic test-only data-free framing |
| `serde` | 1.0.228 | `9a8e94ea7f378bd32cbbd37198a4a91436180c5bb472411e48b5ec2e2124ae9e` | `serde-rs/serde` commit `a866b336f14aa57a07f0d0be9f8762746e64ecb4`, crate path `serde` | MIT OR Apache-2.0 | exact resolver constraint for the JSON closure |

Exact direct constraints on `serde_core`, `itoa`, `memchr`, and `zmij` prevent
offline lock regeneration from selecting newer packages absent from the
reviewed local acquisition set. They add no profile semantics.

Complete locked registry inventory:

| Crate | Version | Declared license |
|---|---:|---|
| `block-buffer` | 0.12.0 | MIT OR Apache-2.0 |
| `cfg-if` | 1.0.4 | MIT OR Apache-2.0 |
| `const-oid` | 0.10.2 | Apache-2.0 OR MIT |
| `cpufeatures` | 0.3.0 | MIT OR Apache-2.0 |
| `crypto-common` | 0.2.1 | MIT OR Apache-2.0 |
| `digest` | 0.11.2 | MIT OR Apache-2.0 |
| `hybrid-array` | 0.4.10 | MIT OR Apache-2.0 |
| `itoa` | 1.0.18 | MIT OR Apache-2.0 |
| `libc` | 0.2.183 | MIT OR Apache-2.0 |
| `memchr` | 2.8.0 | Unlicense OR MIT |
| `minicbor` | 2.3.0 | BlueOak-1.0.0 |
| `proc-macro2` | 1.0.106 | MIT OR Apache-2.0 |
| `quote` | 1.0.45 | MIT OR Apache-2.0 |
| `serde` | 1.0.228 | MIT OR Apache-2.0 |
| `serde_core` | 1.0.228 | MIT OR Apache-2.0 |
| `serde_derive` | 1.0.228 | MIT OR Apache-2.0 |
| `serde_json` | 1.0.151 | MIT OR Apache-2.0 |
| `sha2` | 0.11.0 | MIT OR Apache-2.0 |
| `syn` | 2.0.117 | MIT OR Apache-2.0 |
| `typenum` | 1.19.0 | MIT OR Apache-2.0 |
| `unicode-ident` | 1.0.24 | (MIT OR Apache-2.0) AND Unicode-3.0 |
| `zmij` | 1.0.21 | MIT |

The machine-readable inventory in
`evidence/dependency-license-inventory.json` binds every resolved package,
checksum, selected feature, and dependency role to the exact lock. The
hash-bound `cargo-audit` 0.22.2 observation in
`evidence/advisory-report.json` used RustSec database commit
`309ad29d8fe448bf986019e05d47b9e0e29a2218` and observed zero vulnerabilities
and zero warnings. That is a dated database observation, not legal advice,
advisory clearance, or a security guarantee. The lock and source still
require independent license/security review before any production or
trusted-computing-base decision.
