# Post-Merge Review: SQ-0004

- Review date: 2026-08-09
- Reviewed repository head: `4aa0b9c145ce2595f3630d17abcfb7e4248579b4`
- Reviewed SQ-0004 task merge: `7a83eb843a216886816553897bf541aeb0270c22`
- Reviewed post-merge evidence record: PR #9 / `4aa0b9c145ce2595f3630d17abcfb7e4248579b4`
- Corrected immutable review package: `cecbaa318f043bedd9898afe20e9f930c39eb732`
- Final reviewed task head: `35a8404920dee19ecda6e8c6a0e549cacd06b069`
- Review type: independent post-merge code, security, evidence, workflow, planning, and successor-readiness review

## Disposition

**APPROVE WITH COMPLETED PLANNING MAINTENANCE.**

No blocking defect was found in SQ-0004's exact Rust policy, workspace layout,
source code, bounded CLI behavior, lock reproduction, offline compatibility
floor, dependency/license inventory, advisory evidence, mutation corpus,
workflow, independent review, or DONE transition. SQ-0004 correctly remains
**Experimental** and introduces no statistical, schema, encoding, artifact,
registry, certificate, frontend, or verification semantics.

The post-merge review found three planning defects that did not invalidate the
Rust result:

1. `START_HERE.md` still selected completed task SQ-0004 after SQ-0004 was DONE.
2. `work/status.yaml` named the task merge rather than the final PR #9
   merge/workflow evidence commit as the latest integrated SQ-0004 state.
3. `work/contracts/SQ-0005.yaml` was too short to execute without semantic
   improvisation and incorrectly authorized SQ-0005 to edit RFC-0006 even
   though the decision register assigns RFC-0006 to SQ-0027.

The maintenance branch corrects these issues without changing the Rust source,
Cargo.lock, toolchain policy, retained evidence, task states, accepted ADRs, or
any RFC status.

## Scope and workspace review

The complete SQ-0004 production graph contains only:

- workspace policy and exact toolchain selection;
- local `statqed-core` and `statqed-cli` crates;
- bounded deterministic version and malformed-invocation behavior;
- standard-library verification/evidence tooling;
- small content-addressed evidence records; and
- Rust-specific CI and documentation.

The workspace uses Edition 2024, resolver 3, package
`rust-version = "1.85.1"`, workspace `unsafe_code = "forbid"`, and
`#![forbid(unsafe_code)]` in project targets. The exact lock contains only the
two local packages and no registry, build, native, unsafe, or FFI dependency.
No speculative encoding, artifact, registry, certificate, schema, frontend, or
statistical crate was created.

## Exact toolchain and lock review

The accepted roles remain:

- Rust/rustc 1.97.1, commit
  `8bab26f4f68e0e26f0bb7960be334d5b520ea452`, and Cargo 1.97.1,
  commit `c980f4866141969fab6254a680546a277789d6f0`, for development,
  acquisition, formatting, Clippy, tests, lock generation, and security tools;
- Rust/rustc 1.85.1, commit
  `4eb161250e340c8f48f66e2b929ef4a5bed7c181`, and Cargo 1.85.1,
  commit `d73d2caf9e41a39daf2a8d6ce60ec80bf354d2a7`, for the exact committed graph
  only under `--locked --offline`.

Cargo.lock SHA-256 is
`408f171020abc33031390a1c22ed3f21ec271b797d880f7749f83edec04211a3`.
Two clean current-Cargo generations were byte-identical. The offline-floor job
first acquires the exact graph with current Cargo in a scrubbed Cargo home and
then executes Rust 1.85.1 without network access. A separate empty-Cargo-home
fixture with an absent crate proves the floor fails closed rather than
acquiring.

Rust 1.85.1 is a compiler/API compatibility observation, not an approved
network acquisition or release tool.

## Source and CLI review

`statqed-core` defines only:

- protocol version 1 for this bootstrap CLI surface;
- fixed limits of 64 arguments, 4,096 UTF-8 bytes per argument, and 8,192
  aggregate bytes;
- one version command;
- stable malformed-input classes; and
- literal deterministic JSON/text responses.

Parsing validates bounded count, byte length, aggregate length, and UTF-8
before command grammar. Error output never echoes hostile input and has no
runtime timestamp, random identifier, path, stack trace, locale text, or
library debug value. Resource/encoding errors take precedence over grammar
errors because the complete bounded stream is validated first.

`statqed-cli` is a thin process-I/O layer. Malformed input writes one JSON line
to stderr and exits 2. Write failure returns generic failure rather than
panicking. Unit and process tests independently assert exact responses, both
sides of each resource boundary, non-UTF-8 Unix arguments, broken output, and
deterministic randomized input sequences.

This protocol is not an artifact-verifier error schema and has no authority over
future RFC-defined object formats.

## Verification and adversarial review

`backend/tools/check_workspace.py` verifies exact toolchain/workspace policy,
source/evidence/workflow hashes, package and lock shape, deterministic runtime
fixtures, and clean result classes. Its disposable mutation corpus contains 20
rejections covering:

- unsafe code and removal of the source-level unsafe prohibition;
- workspace/package rust-version drift;
- dependency or lock drift;
- project alternate registries and ambient Cargo credentials;
- floating actions, persisted credentials, alternate registry variables, and
  top-level or job-level write permissions;
- floor network acquisition;
- timestamp/random/path leakage;
- panic output; and
- unstable debug output.

The workflow-policy parser is a deliberately narrow project guardrail rather
than a complete YAML security analyzer. `actionlint` was run as independent
review evidence. Future workflow growth requires corresponding mutation and
policy-parser review.

## Dependency, license, and advisory review

The normalized inventory is derived independently from Cargo metadata and
Cargo.lock. It records the two local MIT packages, exact versions, sources,
roles, features, and dependency relation and reports no registry package.

The advisory record is bound to:

- cargo-audit 0.22.2 and its exact archive/executable hashes;
- RustSec advisory database commit
  `1237bbe09d2701e14e6593a630fbaf28928df712` and archive hash;
- the exact Cargo.lock and dependency-inventory hashes.

The verifier safely extracts the exact trusted archives into temporary
locations and runs the database offline with no fetch. The retained result
observes zero vulnerabilities and zero warnings for the local-only lock. This
is a point-in-time database observation and does not cover rustc, Cargo,
rustup, Python, GitHub Actions, the operating system, or unmodeled native code.

## CI and integration evidence

The final main commit `4aa0b9c145ce2595f3630d17abcfb7e4248579b4`
has successful runs for:

- repository guardrails `31305825572`;
- Rust reference workspace `31305825523`; and
- unchanged Lean proof backend `31305825538`.

The Rust development job passed exact identity checks, workspace policy,
formatting, build, Clippy, tests, doctests, deterministic fixtures, two lock
reproductions, isolated acquisition, all 20 mutations, inventory, hash-bound
advisory verification, and clean-tree checks. The floor job passed current-Cargo
acquisition followed by exact-lock Rust 1.85.1 metadata/build/Clippy/tests and
doctests under a scrubbed offline environment.

Direct task evidence remains limited to the observed Ubuntu Linux x86-64
runners and local host. It establishes no macOS, Windows, ARM, musl, or other
platform compatibility.

## Cleanup review

The reported removal of task-created build trees and temporary evidence state
is consistent with repository policy: generated build output, Cargo homes,
rustup downloads, and extracted databases are disposable, while small
content-addressed evidence remains committed. Preserving shared toolchains and
the user-owned untracked `.codex/` directory was correct; user-owned untracked
state is outside the task and must not be deleted by an agent.

## Successor and RFC ownership review

The checked ledger exposes:

- SQ-0005 — deterministic serialization / RFC-0001 owner;
- SQ-0008 — core evidence and ontology / RFC-0002 and RFC-0004 owner.

SQ-0005 is recommended next because it gates SQ-0006 and much of the remaining
foundation. Its previous contract incorrectly allowed direct edits to
RFC-0006. RFC-0006 is owned by SQ-0027 and governs the first logical table,
physical-to-logical lowering, and canonical logical-data digest. SQ-0005 may
prototype generic numeric/missing/category atoms and data-free digest framing,
but it must not define or accept RFC-0006.

The expanded SQ-0005 contract now requires:

- current primary-source audit;
- explicit profile decisions rather than library defaults;
- two genuinely independent canonicalization implementations/oracles;
- raw duplicate-key detection before native-map collapse;
- exact semantic fixtures, byte vectors, stable failure classes, and deliberate
  divergence detection;
- numeric, Unicode, tags, extensions, decoder strictness, resource limits, and
  generic domain framing;
- a durable static evidence verifier added to `make check`;
- independent source, semantic, implementation, conformance, security,
  cryptographic, CI, formal, and integration review; and
- atomic RFC-0001/ADR-0004/task/successor transitions.

## Residual limitations

- The Rust CLI is not a verifier and its protocol is bootstrap-only.
- The workspace is dependency-free; future external dependencies require new
  acquisition, MSRV, license, advisory, and supply-chain review.
- Rustup and GitHub-hosted runner infrastructure are operational inputs whose
  exact compiler/Cargo outputs are checked but whose distribution path is not
  formally verified.
- The workflow-policy parser is intentionally narrow.
- The advisory extractor is appropriate for exact hash-bound trusted archives,
  not a generic hostile archive service.
- Direct platform evidence is Linux x86-64 only.
- No canonical encoding, logical-data model, artifact, registry, certificate,
  statistical guarantee, or verified analysis exists yet.
- RFC-0001 through RFC-0009 remain Draft at this review point.

## Integration condition

This maintenance may merge only after repository guardrails and the unchanged
Rust and Lean workflows pass on the exact maintenance head. It changes no Rust
source or task state; the workflows still provide regression evidence that the
planning changes did not disturb either language foundation.
