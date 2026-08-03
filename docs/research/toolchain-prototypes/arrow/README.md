# Arrow interoperability prototype

Status: **Draft research evidence**.

This probe evaluates a deliberately small Arrow transport subset. It does not
define StatQED logical data, logical identity, canonical bytes, a digest, or an
RFC-0006 lowering. The repeated-byte and SHA-256 values below are observations
about particular physical outputs only.

## Exact candidates and environment

The final successful run used Ubuntu 24.04.4 LTS, Linux
7.0.0-28-generic, x86_64, `C.UTF-8`, CPython 3.14.6, uv 0.11.32,
rustc 1.97.1, and Cargo 1.97.1. It compared two implementation lineages:

| Candidate | Implementation lineage | Tested subset | License and floor |
|---|---|---|---|
| PyArrow 25.0.0 / Arrow C++ 25.0.0 | Python binding over Arrow C++ | `Int64`, nullable `Utf8`, nullable `Binary`, IPC file and stream | Apache-2.0; PyPI metadata requires Python >=3.10 |
| `arrow` 59.1.0 | native Rust `arrow-rs` implementation | same types, IPC file and stream | Apache-2.0; crate metadata declares Rust 1.85 |

These libraries have separate version sequences. The run observed IPC metadata
version V5 from both APIs; it did not equate library version 25.0.0 with Rust
crate version 59.1.0 or with format metadata V5. Both implementations are
Apache projects, but the C++ and Rust codebases are independently implemented
lineages for this narrow differential.

The PyArrow input was the exact CPython 3.14 manylinux x86_64 wheel with
SHA-256
`447df764beb07c544f0178a5f6b70ef44b9ecf382b3cdfad4c2d7867353c3887`.
`fetch_wheel.py` checks that hash before an offline `--no-index
--require-hashes` install. The Rust graph is bound by `Cargo.lock`, SHA-256
`b48ca90c270c065266d625e8d26a024217ac1559247d530de6b9348969bedaed`.

## Observations

- Each implementation constructed and read its own typed table successfully.
- Each implementation read the other implementation's IPC file and recovered
  the tested schema, rows, nulls, UTF-8 code-point sequence, and byte strings.
- Two writes by the same implementation in the same process were byte-equal
  for each IPC container kind. This is repeatability evidence for this exact
  build and fixture, not a cross-build guarantee or canonical-byte rule.
- IPC file bytes and IPC stream bytes were unequal in both implementations.
  PyArrow and arrow-rs also emitted unequal physical lengths for their files
  and streams. Cross-reading succeeded despite those physical differences.
- Both libraries rejected the minimized six-byte `ARROW1` magic-only file.
  That is one malformed case, not a parser-safety or resource-bound proof.

PyArrow called `Table.validate(full=True)`. The Rust probe constructed a
`RecordBatch` through checked APIs, but did not enable arrow-rs's optional
`force_validate` feature. A future untrusted-input path must separately define
validation, bounds, enabled features, and failure behavior.

## Unequal coverage and unavailable combinations

Official Arrow status records unequal language coverage. This run did not
collapse that status to an Arrow-wide support claim.

- R 4.6.1 was directly runnable, but `requireNamespace("arrow")` failed with
  status 42. No R Arrow runtime or IPC behavior was tested.
- `julia` was not on the host `PATH`. Exact Julia runtimes existed elsewhere in
  temporary frontend evidence, so this result proves only host-command
  unavailability; it says nothing about Arrow.jl installation or behavior.
- macOS, Windows, Linux arm64, R Arrow, and Julia Arrow remain untested. Each
  needs a pinned package/runtime job and the same typed/malformed fixtures
  before a support statement.

## Maintenance, licensing, and security

Apache Arrow 25.0.0 and arrow-rs 59.1.0 were active current candidates on the
2026-08-03 evidence date and are Apache-2.0. Apache publishes a security route,
and its format security guidance warns that invalid data may crash or disclose
data and that untrusted C Data Interface inputs are unsafe without validation.
The probe never used C Data Interface inputs.

Before production use, rerun dependency license and advisory scans over the
exact lock, review Arrow security notices, enable or implement the selected
validation path, add resource bounds, and test all claimed platforms. An Arrow
transport recommendation remains subordinate to Draft RFC-0006.

## Reproduction

The exact evidence run used:

```bash
STATQED_UV=/tmp/statqed-sq0002-python-tools/uv \
STATQED_ARROW_PYTHON=/tmp/statqed-sq0002-python-runtimes/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
RUSTUP_HOME=/tmp/statqed-sq0002-rust-cache/rustup \
RUSTUP_TOOLCHAIN=1.97.1 \
bash docs/research/toolchain-prototypes/arrow/run-probes.sh
```

The script uses a fresh `/tmp` directory and removes the wheelhouse, virtual
environment, Cargo home, build target, and exchanged Arrow files on exit.
Exact stdout, stderr, intervals, superseded preparation attempts, and explicit
unknowns are under `../logs/arrow/` and summarized in `probe-fragment.json`.
