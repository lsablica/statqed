# Rust Backend Scope Instructions

Scope: `backend/**`.

- Implement accepted specs; do not invent statistical meaning.
- Deterministic, offline verification; bounded hostile input; structured errors.
- No panics on untrusted input and no unsafe code without accepted RFC.
- Keep CLI thin; core logic belongs in tested crates.
- Add property, differential, malformed, resource, and fuzz-smoke tests.
- Do not update golden vectors solely to match implementation output.
