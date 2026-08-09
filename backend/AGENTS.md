# Rust Backend Scope Instructions

Scope: `backend/**`.

- Implement accepted specs; do not invent statistical meaning.
- Deterministic, offline verification; bounded hostile input; structured errors.
- No panics on untrusted input and no unsafe code without accepted RFC.
- Keep CLI thin; core logic belongs in tested crates.
- Add property, differential, malformed, resource, and fuzz-smoke tests.
- Do not update golden vectors solely to match implementation output.

## Bootstrap gates

Run from `backend/`:

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

Rust 1.97.1 is the only acquisition/development toolchain. Rust 1.85.1 is
only an offline compiler/API floor consuming the exact committed lock. The
hash-bound advisory command and immutable input locators are documented in
`../docs/implementation/rust-backend.md` and `evidence/security-lock.json`.
