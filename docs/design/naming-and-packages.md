# Naming and Package Layout

Status: **Draft**.

The academic project and repository family name is **StatQED**. Foundation-local names are:

- R package source: `statqed`;
- Python distribution/import source: `statqed`;
- Julia package source: `StatQED` (customary repository label `StatQED.jl`);
- CLI executable: `statqed`;
- artifact extension: `.statqed`;
- Lean namespace: `StatQED`.

These are source-tree conventions, not claims of registry reservation, exclusive use, trademark clearance, or future publication. Official checks on 2026-08-03 found no exact record at the queried PyPI, CRAN, and Julia General endpoints; crates.io, GitHub organization/domain availability, similarity rules, and legal clearance remain unresolved. Every publication task must recheck current registry policy and ownership before freezing a public name.

Rust public crate names, internal workspace-crate names, the Cargo package that may supply the CLI, and the Lean Lake package/library name remain deferred to SQ-0004 and SQ-0003. Internal foundation APIs are unpublished unless a task contract explicitly promotes them. Generated bindings are non-authoritative. The Julia task must test a General-compatible publication/mirror/split strategy because the foundation monorepo subdirectory is not itself evidence of registry compatibility.

Internal modules may use names derived from StatQED (`StatCore`, `StatIR`, `StatCert`, `StatQEDBench`) only when ownership and public citation relationships remain clear. See ADR-0009 and `docs/research/SQ-0001-constitutional-source-audit.md`.
