# CBOR and CDDL interoperability prototype

Status: **Draft research evidence**.

This prototype observes library and tooling behavior only. RFC-0001 is Draft:
no tested encoder is a semantic oracle, no map order is selected, no bytes are
golden, and no decoder acceptance behavior is recommended. CDDL checks shape;
it does not establish deterministic bytes, duplicate policy, semantic
normalization, inferential validity, or kernel verification.

## Exact candidates and preparation

The cross-language run used Ubuntu 24.04.4 LTS x86_64, CPython 3.14.6,
uv 0.11.32, rustc 1.97.1, and Cargo 1.97.1:

| Candidate | Role observed | License / maintenance note |
|---|---|---|
| cbor2 6.1.4 | Python encoder/decoder | MIT; current release retrieved 2026-08-05, Python >=3.10; project documentation says malicious-input testing has not been performed |
| cbor2 6.1.3 | Historical cross-lineage observation | Superseded on 2026-08-01; retained because it was the version in the differential run |
| ciborium 0.2.2 | Rust serde/value encoder/decoder | Apache-2.0; maintained candidate; declared Rust 1.58 |
| minicbor 2.3.0 | independent low-level Rust encoder/decoder | BlueOak-1.0.0; current maintained candidate; no crate MSRV declared |
| cddl 0.10.6 | CDDL compile/CBOR shape-validation CLI | MIT; actively developed metadata; declared Rust 1.88.0 |

`serde_cbor` was not run: its repository is archived and explicitly says it is
unmaintained, so it is rejected as a new foundation candidate. Its own README
points users to ciborium or minicbor.

The current cbor2 CPython 3.14 manylinux x86_64 wheel is hash-bound as
`c0f5f2d6d3b58e44146860c049f3c082207a4005588b8926d51bf937ab66773c`
and installed offline with `--no-index --require-hashes`. The earlier 6.1.3
wheel is retained in the historical matrix entry. The direct Rust CBOR
graph is the checked-in `Cargo.lock`, SHA-256
`141d50267ec9db74ecd09cd32e37ec7c41a7c6e5bb10cc85741429532549d871`.

`cargo install cddl --version 0.10.6 --locked` consumed the crate's published
154-package lock graph. `cddl-install-lock.json` records every package,
registry checksum, and dependency list; its source lock SHA-256 is
`193467cae8f59b079960f6678cc7a0951f9391a7854fbe636489d30cdfddcb93`.
This graph capture is not a transitive license or advisory approval. A complete
license inventory and current RustSec/supply-chain scan is a required
pre-production gate.

## Discriminating deterministic-order observation

For `{24: 0, "": 0}`, the tested byte orders differ:

| RFC 8949 variant | Hex |
|---|---|
| Section 4.2.1 core bytewise lexicographic key order | `a21818006000` |
| Section 4.2.3 length-first key order | `a26000181800` |

cbor2 `canonical=True` and a ciborium map keyed by `CanonicalValue` emitted the
length-first bytes. Minicbor's low-level encoder emitted either vector when
given the corresponding insertion order; no matching canonicalizer was found
in the tested API. These facts distinguish implementations and profiles. They
do not select RFC 8949 section 4.2.3 for StatQED.

## Decoder and malformed-input observations

- cbor2 decoded duplicate map key bytes `a201000102` with last value wins.
  Ciborium `Value::Map` and a manual minicbor map decoder both exposed two
  entries. Any future strict profile must reject duplicates before conversion
  to a map representation that loses them.
- cbor2, ciborium, and minicbor accepted tested indefinite-length array bytes
  `9f0102ff`. cbor2 and ciborium re-encoded the resulting value as definite
  `820102`.
- cbor2 accepted a top-level break byte `ff` as an internal sentinel object;
  the first probe incorrectly assumed rejection and that failed attempt is
  retained.
- cbor2 accepted tested nesting depths 254 through 257. Ciborium accepted
  depths 127 and 128. This is not evidence of a safe maximum; strict profile
  validation needs explicit application bounds before general decoding.
- cbor2, ciborium, and minicbor rejected the minimized truncated argument byte
  `18` in their tested APIs.

These incompatible duplicate and non-profile acceptance behaviors preclude a
decoder semantic recommendation from SQ-0002. A later strict profile validator
must operate before lossy generic-value conversion and must test duplicates,
indefinite items, depth, size, tags, Unicode, and numeric boundaries.

## Current cbor2 security-regression probe

The owned `verify-cbor2-6.1.4.sh` dispatcher used exact CPython 3.14.7 and the
hash-bound 6.1.4 wheel. It directly confirmed all four security-relevant fixes
listed in the release history: an indefinite map missing its final value and a
non-byte bignum payload were rejected; the tested frozendict construction with
the same key and value sets but different pairing produced distinct hashes;
and a bytearray followed by an equal byte string round-tripped through a string
reference without namespace desynchronization. This is narrow regression
evidence, not an assurance that malicious CBOR is safe.

## CDDL shape-only observation and MSRV conflict

cddl 0.10.6 on Rust 1.97.1 compiled `schema.cddl`, accepted the valid map,
rejected an integer where `tstr` was required, and accepted both RFC 8949 map
order byte vectors against the same schema. Thus it distinguishes shape but
not the deterministic order variants.

The checked-in `cddl-msrv/Cargo.lock` has SHA-256
`a5f32725bc013d06c05dafeea0249f90c414987541657947c9bd623d6c950872`.
`cargo +1.85.1 check --locked` exited 101 because cddl 0.10.6 and selected
transitive `time` packages require Rust 1.88.0. Therefore cddl 0.10.6 is
incompatible with the proposed Rust 1.85.1 support floor. It is at most a
development/CI schema tool on Rust >=1.88, not a support-floor library.

The default cddl feature set also implements standards and draft features.
CDDL module syntax remains an Internet-Draft and must stay Experimental and
version-pinned if later enabled; tool support does not make a draft an RFC.

## Reproduction

```bash
python3 record_cbor2_6_1_4.py

STATQED_UV=/tmp/statqed-sq0002-python-tools/uv \
STATQED_CBOR_PYTHON=/tmp/statqed-sq0002-python-runtimes/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
RUSTUP_HOME=/tmp/statqed-sq0002-rust-cache/rustup \
RUSTUP_TOOLCHAIN=1.97.1 \
bash docs/research/toolchain-prototypes/cbor-cddl/run-probes.sh
```

The current-version dispatcher rechecks the Python archive, uv binary, wheel,
and lock digests; uses fresh HOME, uv, XDG, venv, runtime, and wheelhouse paths;
and removes them on exit. The historical cross-language script likewise keeps
downloaded wheels, registries, compilation outputs, validators, and binary
vectors under a fresh `/tmp` directory. Exact logs and retained failures are in
`../logs/cbor-cddl/`.
