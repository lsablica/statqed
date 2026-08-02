---
applyTo: "backend/**/*.rs"
---

Read `backend/AGENTS.md` and ADR-0003.

Rust must conform to accepted specs, be deterministic, bound untrusted input, avoid panics, deny unsafe code by default, and keep the CLI thin. It does not independently define statistical meaning.
