# Plan 0001: Foundation Bootstrap

- Status: Active
- Backlog: SQ-0001 through SQ-0020
- Objective: turn the architecture-first scaffold into a reproducible executable foundation without prematurely freezing incorrect statistical semantics.

## Observable exit condition

From a clean checkout:

1. Lean and Rust workspaces build with pinned toolchains.
2. Draft versioned CDDL files and reviewed canonical vectors are versioned under an Accepted RFC-0001 profile; draft module syntax is not silently treated as a standard.
3. R, Python, and Julia construct the same data-free `foundation_structural` semantic fixture defined by ADR-0011.
4. The Rust backend produces byte-identical canonical bytes and domain-separated fixture digests. A logical-data digest is included only after RFC-0006 is Accepted; the data-free slice does not require one.
5. Lean checks the exact toy proposition only through an Accepted RFC-0003 byte-to-term path and RFC-0005 theorem/environment/proof locks; lock resolution alone is structural evidence.
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
  │       └─ SQ-0012 Lean structural decoder (also depends on SQ-0007)
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
- Research current package-name evidence and official tool/package constraints before accepting source-tree conventions; record that point-in-time checks are not reservations, publication approval, or legal clearance.
- Convert unresolved decisions into RFCs; do not bury them in code.
- Mark accepted ADRs with date and reviewers.
- Confirm the exact first artifact and nonclaims.

### Required review

Source curator, statistical architect, formal-methods reviewer, interoperability reviewer, adversarial reviewer, security reviewer where trust/encoding is affected, and integrator.

### Acceptance

No known unresolved contradiction remains in the content-addressed review surface, all constitutional choices have an Accepted ADR/RFC or an explicit blocked research task, and `make check` passes.

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

Implement competing prototypes for deterministic CBOR behavior using at least two independently originated libraries/implementations or oracles. Test integer/rational tags, byte strings, map ordering, Unicode, duplicate keys, IEEE bits, intervals, missing values, unknown extensions, non-profile encodings, and resource behavior. Resolve RFC-0001 and the encoding-relevant portion of RFC-0006 without using Rust output as the semantic oracle.

### SQ-0006

Create versioned CDDL files for numeric atoms, identifiers, extensions, and the exact data-free `foundation_structural` fixture. Avoid draft CDDL module/import syntax unless its revision is pinned and labeled Experimental. Add diagnostic JSON Schema projections, valid/invalid examples, reviewed canonical bytes/digests, and a schema-version policy. The artifact envelope remains SQ-0010 scope; the first normative logical-data schema/digest is explicitly deferred to RFC-0006/SQ-0027.

### SQ-0007

After RFC-0005 is Accepted, implement the registry metadata/lock schema and test-only, definitionally trivial `True` conformance record. It is not a public theorem or non-vacuity witness. Bind canonical elaborated proposition bytes, normalization/environment version, canonical registry record, independently selected registry authorization root/policy and status, statement digest, proof/build lock, actual axiom report, and compatibility-proof path. Keep semantic identity separate from proof-body/build trust, and require the exact bytes-for-`False` mapped to `True` misbinding mutation without treating it as evidence of a general decoder or theorem capability.

### Acceptance

Two implementations agree on all accepted golden vectors. Every negative vector has a named rejection reason.

## Milestone D — Create formal semantic skeleton (SQ-0008–SQ-0009)

### SQ-0008

After RFC-0002 is Accepted and RFC-0004 supplies an accepted narrow boundary, define only the minimal Lean types/interfaces needed by the toy subset for claim class, assurance input/evidence category, verification mode, external assumption, and typed claim reference. Supply examples/nonexamples. Do not freeze a universal experiment or flat randomness-scope abstraction.

### SQ-0009

Define assurance node/edge kinds and DAG well-formedness for the toy subset. Prove that diagnostics, attestations, citations, provenance, unresolved obligations, and policy classifications cannot discharge deductive premises. Establish deterministic node identity rules.

### Acceptance

Public definitions have source/semantic reviews and frozen hashes; no `sorry` or project axiom.

## Milestone E — Artifact and reference backend (SQ-0010–SQ-0012)

### SQ-0010

Define the safe deterministic archive envelope, entry limits, required manifest fields, content hashes, critical feature behavior, and report separation. Add path traversal, duplicate entry, oversized, and unknown-critical fixtures.

### SQ-0011

Implement Rust parsing, validation, canonical encoding, domain-separated content digests, and machine-readable inspect/validate commands for the data-free fixture. Theorem-registry/lock resolution belongs to SQ-0007. Do not implement a logical-data schema, lowering, or digest; RFC-0006/SQ-0027 owns that first real-data backend path. Parser behavior must be bounded and panic-free.

### SQ-0012

Implement the minimal Lean-side decoder/bridge for the toy structural object or generate checked Lean source from a validated representation, according to the accepted trust RFC. Document exactly which parser/bridge components enter each mode’s TCB.

### Acceptance

Rust and Lean agree on the toy object; malformed artifacts fail consistently.

## Milestone F — Frontend skeletons (SQ-0013–SQ-0016)

Create package-native skeletons:

- R package source `statqed`, with a live pre-publication name/policy recheck, constructors returning typed IR values, and `testthat` tests;
- Python distribution/import source `statqed`, with a live pre-publication name/policy recheck, modern `pyproject.toml`, tests, and CLI bridge;
- Julia package source `StatQED`, with a live name/policy recheck, a tested General-compatible publication/mirror/split strategy, tests, and shared fixtures.

Generate or share structural definitions rather than hand-maintaining divergent models. Each frontend emits the same trivial semantic object; no model adapter is included yet.

SQ-0016 builds a conformance runner comparing semantic objects, normalized diagnostics, canonical bytes, digests, and failure codes across Rust and all frontends. Shared-Rust caller agreement is integration evidence; encoder acceptance also requires an implementation/oracle with independent lineage and a mutation proving the harness detects Rust divergence.

## Milestone G — Trust report, CI, and first artifact (SQ-0017–SQ-0020)

### SQ-0017

Define and render the machine/human trust report for the toy artifact. Include mode, claims, external assumptions, TCB, untrusted components, locks, warnings, and nonclaims.

### SQ-0018

Expand CI into separate jobs with pinned toolchains and caches. Add trusted-path scans, generated-file checks, dependency review, clean checkout, and artifact roundtrip.

### SQ-0019

Compose the ADR-0011 data-free fixture from R, Python, and Julia. Require byte-identical canonical IR under the Accepted profile, one Rust-produced bundle, structural validation, toy `True` theorem/environment/proof locks, the Accepted RFC-0003 path for any kernel claim, and a reproducible report containing every ADR-0011 nonclaim.

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
- [x] SQ-0001 constitutional baseline ratified and integrated — DONE 2026-08-03; distinct source, statistical, formal, interoperability, security, adversarial, and integration reviews approved the content-addressed surface.
- [ ] SQ-0002 toolchain research — IN_REVIEW 2026-08-03 on `agent/SQ-0002-toolchain-research`, starting from `9bf99227240550a6c84f417eccd99c48f43be6ec`; 60 attempted combinations, five toolchain recommendations, 72 primary-source records, and 88 content-addressed prototype subjects are frozen for independent review. Direct probes ran only on Ubuntu 24.04.4 LTS, Linux 7.0.0-28-generic, x86_64.
- [ ] SQ-0003 through SQ-0020.

## Surprises & Discoveries

- The scaffold guardrail hardcoded SQ-0001 as permanently ready, which would reject the required post-integration transition to SQ-0002; SQ-0001 now makes that check ledger-driven.
- RFC 8949 supplies multiple deterministic choices and CDDL does not define canonical bytes; CDDL module/import syntax remains an active draft as of 2026-08-03.
- Exact registry 404s are point-in-time observations, not reservations or trademark clearance; crates.io returned a data-access 403 and remains inconclusive.
- A surface statement digest cannot identify theorem meaning without canonical elaborated proposition bytes, a locked environment, a separate proof/build lock, and an actual axiom report.
- A self-consistent theorem-registry record is not authorized merely by being content-addressed; verifier policy must select the accepted registry root and its historical or revocation rules.
- A data-free first fixture avoids prematurely freezing logical-table/digest semantics while still exercising the IR, registry, graph, envelope, and trust-report path.
- Task dependencies alone cannot enforce constitutional prerequisites, so the work ledger now records Draft-decision owners and machine-checked decision prerequisites.
- A second work-list implementation that ignores decision prerequisites can contradict the repository guardrail; both commands now share one readiness calculation and distinguish eligible active work from unclaimed READY work.
- Registered RFCs support only Draft and Accepted until a reviewed, non-cyclic successor relation exists; invalid or mistyped statuses cannot silently release downstream work. The lifecycle guard fails closed and has exhaustive supported-status/owner-state corruption fixtures.
- A non-Accepted RFC cannot remain assigned to a completed task. RFC-0006 is therefore assigned to detailed task SQ-0027 before real data, while RFC-0007/RFC-0009 keep SQ-0020 blocked until acceptance.
- The newest standalone Lean release was not the newest proven Lean/Mathlib pair: Lean 4.32.2 existed at retrieval time, while Mathlib's current stable immutable revision selected Lean 4.32.1. A no-cache source build and separate binary-cache run were both required; a stale cache link failed and was retained.
- Python packaging became reproducible only after binding the exact CPython standalone archives, uv archive, wheelhouse, and built artifacts by SHA-256. R development required a SHA-locked CRAN source closure because conda-forge's R 4.6.1/testthat 3.3.2 combination was unsatisfiable; the R floor was independently recreated offline from an explicit conda lock.
- A fresh Julia depot still tried to bootstrap the mutable General registry. A fixed empty local registry made the dependency-free package probes deterministic. Arrow file and stream IPC forms differed physically, CBOR libraries exposed permissive and divergent edge behavior, and `cddl` 0.10.6 required Rust 1.88 despite the proposed Rust 1.85.1 floor.

## Decision Log

- 2026-08-03: Initial ADRs remain Proposed until the corrected content-addressed surface receives independent re-review.
- 2026-08-03: Opened RFC-0004 (core ontology), RFC-0005 (theorem identity/proof trust), RFC-0006 (logical data/digest), RFC-0007 (compatibility), RFC-0008 (artifact envelope/offline resolution), and RFC-0009 (community governance); RFC-0001 and RFC-0003 remain explicit downstream blockers.
- 2026-08-03: Selected ADR-0011's data-free `foundation_structural` slice with a toy proposition `True`; no canonical bytes or statistical semantics are frozen by SQ-0001.
- 2026-08-03: Selected source-tree package names as conventions only; public registry names and publication layouts require live task-specific rechecks.
- 2026-08-03: Added a machine-checked constitutional decision register. Each Draft RFC has one contract with write authority, and downstream tasks name Accepted-decision prerequisites where dependency completion alone is insufficient.
- 2026-08-03: Separated theorem-record integrity from registry authorization; an artifact-supplied root cannot confer governed theorem identity, maturity, review, revocation, or compatibility authority.
- 2026-08-03: Assigned RFC-0006 to detailed task SQ-0027 and kept SQ-0006/SQ-0011 data-free. No normative real-data schema, digest, or backend path may land before RFC-0006 acceptance.
- 2026-08-03: Required SQ-0020 to accept RFC-0007 and RFC-0009 rather than complete with an unresolved owner; the ledger rejects non-atomic owner handoff.
- 2026-08-03: Fixed provenance-redaction identity: changing committed/normative provenance always creates new normative artifact/result identity; inert-report-only redaction preserves normative identity but changes physical bundle bytes/file commitment and records disclosure; unresolved leaves apply only to external/uncommitted references or newly identified objects/results.
- 2026-08-03: Constrained registered RFCs to Draft/Accepted and decision prerequisites to Accepted until successor semantics are reviewed. Every completed/superseded owner must have an Accepted RFC; a pure exhaustive fixture covers all supported decision/owner states and a non-vacuous typo rejection.
- 2026-08-03: Classified ADR-0011's definitionally trivial `True` as a test-only conformance record that cannot satisfy public-theorem non-vacuity.
- 2026-08-03: Accepted ADR-0001, ADR-0002, ADR-0003, ADR-0006, ADR-0008, ADR-0009, ADR-0010, and ADR-0011 against the reviewed surface preserved in commit `31fbd22`. ADR-0004, ADR-0005, and ADR-0007 remain Proposed behind their named RFC/tasks.
- 2026-08-03: Kept RFC-0001 through RFC-0009 Draft. RFC-0002 is review-eligible but remains owned by SQ-0008 so the evidence taxonomy, narrow statistical ontology, and concrete public types are resolved together without silent semantics.
- 2026-08-03: Independent integration review approved the immutable candidate and the disposition-only delta, integrated in commit `ab5e937c0f36d605dd75fef86a84ada0868ab326`. SQ-0001 is DONE and SQ-0002 is the sole READY task; no language toolchain was initialized.
- 2026-08-03: Proposed distinct SQ-0002 development pins and support floors: Lean 4.32.1 with Mathlib `520045ab14e26149ee970e2e617ca04b09bde5d6` as an exact pair; Rust 1.97.1 with Rust 1.85.1 MSRV; Python 3.14.6 with Python 3.11.15 floor; R 4.6.1 with R 4.4.3 tested floor; Julia 1.12.6 with Julia 1.10.11 LTS floor. The CI proposal separates directly tested Linux entries from planned macOS and Windows validation.
- 2026-08-03: Kept Arrow 25.0.0, the tested CBOR libraries, and `cddl` 0.10.6 as experimental compatibility candidates only. SQ-0002 does not define canonical bytes, logical-data identity, decoder acceptance, artifact envelopes, or accept RFC-0001/RFC-0006.

## Outcomes & Retrospective

SQ-0001 outcome: eight high-level architectural ADRs are Accepted; three narrower ADRs and all nine RFCs remain explicitly Proposed/Draft with machine-checked owners and gates. The exact first slice is data-free, test-only, and non-statistical. Distinct source, statistical, formal, interoperability, security, adversarial, and integration reviewers approved the frozen surface preserved in commit `31fbd22` and its disposition-only integration delta. SQ-0001 is complete, SQ-0002 is the sole READY task, and no language toolchain was initialized. Full Plan 0001 retrospective remains SQ-0020 work.

SQ-0002 candidate outcome: a strict verifier binds the report to 60 successful, failed, or unknown attempts, five exact toolchain recommendations, primary sources, logs, locks, and 88 prototype subjects; corruption fixtures test mutable recommendations, platform-evidence laundering, arbitrary reruns, failure normalization, and empty locks. Independent review is pending, so the task is not DONE and SQ-0003/SQ-0004 remain blocked. No production toolchain, package, RFC, schema, or workflow was changed.
