# Rust Reference Workspace

This is the minimal SQ-0004 Rust foundation. It contains a dependency-free
library for bounded argument parsing and deterministic version/error output,
plus a thin `statqed` binary. It intentionally contains no statistical,
schema, encoding, artifact, digest, registry, certificate, or verification
semantics.

The toolchain roles are deliberately separate:

- Rust 1.97.1 acquires and locks dependencies and runs development gates.
- Rust 1.85.1 is only the compiler/API compatibility floor; it consumes the
  committed graph with `--locked --offline` and never acquires dependencies.

From this directory, run:

```bash
cargo +1.97.1 fmt --check
cargo +1.97.1 clippy --workspace --all-targets --all-features --locked -- -D warnings
cargo +1.97.1 test --workspace --all-features --locked
cargo +1.85.1 clippy --workspace --all-targets --all-features --locked --offline -- -D warnings
cargo +1.85.1 test --workspace --all-features --locked --offline
python3 tools/check_workspace.py --run-mutations
python3 tools/dependency_inventory.py
python3 tools/run_isolated_checks.py
```

The point-in-time advisory check also needs the two immutable archives named
and hashed in `evidence/security-lock.json`; see
`../docs/implementation/rust-backend.md` for the exact command. Build output
and isolated Cargo homes are disposable. Only `Cargo.lock` and the small
normalized records in `evidence/` are retained.
