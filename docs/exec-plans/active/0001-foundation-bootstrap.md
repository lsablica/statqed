# Plan 0001: Foundation Bootstrap

- Status: Active
- Backlog: SQ-0001 through SQ-0020
- Objective: turn the architecture-first scaffold into a reproducible executable foundation without prematurely freezing incorrect statistical semantics.

## Observable exit condition

From a clean checkout:

1. Lean and Rust workspaces build with pinned toolchains.
2. Draft CDDL schemas and canonical vectors are versioned.
3. R, Python, and Julia construct the same trivial typed analysis object.
4. The Rust backend produces byte-identical canonical CBOR and logical digests.
5. Lean validates the corresponding structural artifact and toy theorem lock.
6. CI runs repository, language, conformance, trusted-path, and clean-checkout checks.
7. A trust report says exactly that only structural/toy obligations are checked.

No real statistical method is claimed complete at this milestone.

## Context

StatQED’s main risk is semantic incoherence, not insufficient generated code. The foundation therefore freezes only small interfaces after prototypes and independent review. The first vertical slice must exercise the entire path before broad theorem formalization begins.

## Dependency graph

```text
SQ-0001 constitutional baseline
  ├─ SQ-0002 toolchain research
  │    ├─ SQ-0003 Lean bootstrap
  │    └─ SQ-0004 Rust bootstrap
  ├─ SQ-0005 serialization prototype ─ SQ-0006 schema v0
  │       ├─ SQ-0007 theorem registry
  │       ├─ SQ-0010 artifact envelope
  │       ├─ SQ-0011 canonical backend
  │       └─ SQ-0012 Lean structural decoder
  ├─ SQ-0008 core Lean types ─ SQ-0009 assurance graph ─ SQ-0017 trust report
  └─ SQ-0013/14/15 frontend skeletons

SQ-0016 conformance harness
SQ-0018 expanded CI
SQ-0019 trivial cross-language artifact
SQ-0020 independent foundation review
```

## Milestone A — Ratify the constitution (SQ-0001)

### Work

- Review CHARTER, ARCHITECTURE, all proposed ADRs, glossary, trust model, maturity language, and naming.
- Research current package-name availability and official toolchain constraints before accepting names/versions.
- Convert unresolved decisions into RFCs; do not bury them in code.
- Mark accepted ADRs with date and reviewers.
- Confirm the exact first artifact and nonclaims.

### Required review

Statistical architect, formal-methods reviewer, interoperability reviewer, integrator.

### Acceptance

No contradictory definitions, all constitutional choices have an Accepted ADR/RFC or an explicit blocked research task, and `make check` passes.

## Milestone B — Pin and bootstrap toolchains (SQ-0002–SQ-0004)

### SQ-0002

Create a compatibility report covering Lean 4, Mathlib commit/release, Lake, Rust stable/MSRV, Python, R, Julia, Arrow/CBOR libraries, and supported platforms. Validate tiny prototypes before pinning. Record exact installation commands and cache policy.

### SQ-0003

Initialize a minimal Lean project under `lean/` with one namespace, one executable test/example, pinned `lean-toolchain`, `lakefile.toml`, Mathlib lock, formatting/lint conventions, and an axiom-report script. Do not add statistical abstractions here.

### SQ-0004

Initialize the Rust workspace under `backend/` with planned crates reduced to the smallest compiling skeleton. Add structured errors, deterministic CLI output, `unsafe_code = "forbid"`, formatting/lint/tests, and platform matrix. No schema semantics beyond a toy object.

### Acceptance

Clean builds on CI-supported platforms and documented local reproduction.

## Milestone C — Settle an encoding prototype (SQ-0005–SQ-0007)

### SQ-0005

Implement competing prototypes for deterministic CBOR behavior using at least two libraries/implementations. Test integer/rational tags, byte strings, map ordering, Unicode, duplicate keys, IEEE bits, intervals, missing values, and unknown extensions. Open/resolve RFC-0001.

### SQ-0006

Create CDDL modules for envelope, numeric atoms, identifiers, extensions, and a trivial analysis. Add diagnostic JSON Schema projections, valid/invalid examples, canonical bytes, digests, and a schema-version policy.

### SQ-0007

Implement the registry metadata/lock schema and a toy theorem record. Normalize and hash a toy Lean statement by a documented algorithm. Keep proof-body changes separate from statement changes.

### Acceptance

Two implementations agree on all accepted golden vectors. Every negative vector has a named rejection reason.

## Milestone D — Create formal semantic skeleton (SQ-0008–SQ-0009)

### SQ-0008

Define minimal Lean types/interfaces for randomness scope, claim class, evidence class, verification mode, external assumption, and typed claim reference. Supply examples/nonexamples. Avoid committing to a universal statistical experiment abstraction until the ontology RFC is reviewed.

### SQ-0009

Define assurance node/edge kinds and DAG well-formedness for the toy subset. Prove that forbidden diagnostic-to-deductive edges cannot be constructed or validated. Establish deterministic node identity rules.

### Acceptance

Public definitions have source/semantic reviews and frozen hashes; no `sorry` or project axiom.

## Milestone E — Artifact and reference backend (SQ-0010–SQ-0012)

### SQ-0010

Define the safe deterministic archive envelope, entry limits, required manifest fields, content hashes, critical feature behavior, and report separation. Add path traversal, duplicate entry, oversized, and unknown-critical fixtures.

### SQ-0011

Implement Rust parsing, validation, canonical encoding, logical digest, theorem-lock resolution for the toy registry, and machine-readable inspect/validate commands. Parser behavior must be bounded and panic-free.

### SQ-0012

Implement the minimal Lean-side decoder/bridge for the toy structural object or generate checked Lean source from a validated representation, according to the accepted trust RFC. Document exactly which parser/bridge components enter each mode’s TCB.

### Acceptance

Rust and Lean agree on the toy object; malformed artifacts fail consistently.

## Milestone F — Frontend skeletons (SQ-0013–SQ-0016)

Create package-native skeletons:

- R package `statqed` (provisional), with constructors returning typed IR values and `testthat` tests;
- Python package `statqed`, typed with a modern `pyproject.toml`, tests, and CLI bridge;
- Julia package `StatQED.jl`, with tests and shared fixtures.

Generate or share structural definitions rather than hand-maintaining divergent models. Each frontend emits the same trivial semantic object; no model adapter is included yet.

SQ-0016 builds a conformance runner comparing normalized diagnostics, canonical bytes, digests, and failure codes across Rust and all frontends.

## Milestone G — Trust report, CI, and first artifact (SQ-0017–SQ-0020)

### SQ-0017

Define and render the machine/human trust report for the toy artifact. Include mode, claims, external assumptions, TCB, untrusted components, locks, warnings, and nonclaims.

### SQ-0018

Expand CI into separate jobs with pinned toolchains and caches. Add trusted-path scans, generated-file checks, dependency review, clean checkout, and artifact roundtrip.

### SQ-0019

Create one trivial cross-language artifact from R, Python, and Julia. Require byte-identical canonical IR, one Rust-produced bundle, structural validation, a toy Lean theorem lock, and reproducible report.

### SQ-0020

Run an independent foundation review. Attempt malformed inputs, alternate implementations, clean-machine reproduction, and claim-language review. Update the architecture and open follow-up tasks instead of hiding limitations.

## Validation commands

Initially:

```bash
make check
make list-work
```

As tasks land, the plan must replace placeholders with exact commands for Lean, Rust, R, Python, Julia, schemas, conformance, and clean verification.

## Recovery and idempotence

- Toolchain bootstrap scripts must be repeatable.
- Generated files identify source and generator.
- Golden vectors are content-addressed and never rewritten without review.
- Failed prototypes remain documented under research notes.
- Each task can be reverted without invalidating unrelated completed tasks.

## Progress

- [x] Architecture and agent scaffold installed — bootstrap commit.
- [ ] SQ-0001 constitutional baseline ratified.
- [ ] SQ-0002 through SQ-0020.

## Surprises & Discoveries

- None recorded yet.

## Decision Log

- Initial ADRs are Proposed, not accepted implementation mandates.

## Outcomes & Retrospective

To be completed at SQ-0020.
