# Rust Backend Implementation Guide

Planned workspace crates:

```text
statqed-types
statqed-schema
statqed-canonical
statqed-digest
statqed-artifact
statqed-registry
statqed-cli
statqed-testkit
```

Requirements: stable pinned toolchain, `unsafe_code = "forbid"`, deterministic output, structured errors, bounded parsing/archive extraction, no network during verification, reproducible fixtures, property/fuzz testing, and no panics on hostile input.

The CLI remains a thin composition layer and emits machine-readable verification reports.
