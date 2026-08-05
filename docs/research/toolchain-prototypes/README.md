# SQ-0002 Toolchain Prototypes

Status: **Draft research evidence**.

This directory contains disposable, package-native probes used to propose
foundation toolchain pins. It is not a production Lean project, Rust backend,
or R/Python/Julia frontend. Successful behavior here does not accept any RFC,
define canonical bytes, define logical-data identity, or establish support on
an untested platform.

## Layout

- `lean-mathlib/`, `rust/`, `python/`, `r/`, and `julia/` contain minimal
  language-native prototype inputs.
- `arrow/` and `cbor-cddl/` contain interoperability experiments only.
- `sources/` records dated official-source evidence.
- `logs/` preserves concise stdout, stderr, command, version, and environment
  evidence for attempted combinations.
- `failures/` indexes retained failed and unavailable candidates.
- `matrix.json` is the complete machine-readable inventory and recommendation
  evidence map.

Downloaded runtimes, dependency clones, virtual environments, compilation
outputs, and package caches are intentionally excluded. Reproduction uses
isolated caches outside the repository and must not assume a warm global cache.

## Verification and reruns

From the repository root:

```bash
python3 -m json.tool docs/research/toolchain-prototypes/matrix.json
python3 scripts/bootstrap/run_toolchain_probes.py --verify
python3 scripts/bootstrap/run_toolchain_probes.py --run-available
```

`--verify` is read-only. `--run-available` executes only matrix entries marked
locally runnable and constrains their working directories to this prototype
tree. Platform documentation remains separate from direct run evidence.
