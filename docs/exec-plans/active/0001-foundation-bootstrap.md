# Plan 0001: Foundation Bootstrap

- Status: Active
- Backlog: SQ-0001 through SQ-0020
- Objective: turn the architecture-first scaffold into a reproducible executable foundation without prematurely freezing incorrect statistical semantics.

## Observable exit condition

From a clean checkout:

1. Lean and Rust workspaces build with pinned toolchains.
2. Versioned CDDL files and reviewed canonical vectors exist under an Accepted RFC-0001 profile; draft module syntax is never silently treated as a standard.
3. R, Python, and Julia construct the same data-free `foundation_structural` semantic fixture defined by ADR-0011.
4. The Rust backend produces byte-identical accepted canonical bytes and domain-separated fixture digests. A logical-data digest appears only after RFC-0006 is Accepted; the data-free slice does not require one.
5. Lean checks the exact toy proposition only through an Accepted RFC-0003 byte-to-term path and Accepted RFC-0005 theorem/environment/proof/authorization locks; lock resolution alone is structural evidence.
6. CI runs repository, language, conformance, trusted-path, malformed-input, and clean-checkout checks.
7. A machine and human trust report states exactly which structural/toy obligations were checked and exposes every unresolved or external dependency.

No real statistical method is claimed complete at this milestone.

## Context

StatQED's main foundation risk is semantic incoherence, not insufficient generated code. The project therefore freezes only small interfaces after prototypes, negative tests, and independent review. The first vertical slice must exercise the complete cross-language and proof path while remaining data-free, non-statistical, and test-only.

SQ-0001 established the constitutional boundaries. SQ-0002 selected reviewed toolchain recommendations but initialized no production project and accepted no Draft RFC semantics. SQ-0003 and SQ-0004 are the first production bootstrap tasks.

## Dependency and decision graph

```text
SQ-0001 constitutional baseline                       DONE
  └─ SQ-0002 toolchain research                      DONE
       ├─ SQ-0003 Lean bootstrap                     DONE
       └─ SQ-0004 Rust bootstrap                     READY
            └─ SQ-0005 serialization prototype
                 └─ RFC-0001 acceptance
                      └─ SQ-0006 schema v0
                           ├─ SQ-0007 theorem registry + RFC-0005
                           ├─ SQ-0010 artifact envelope + RFC-0008
                           ├─ SQ-0011 canonical backend
                           └─ SQ-0012 Lean structural path + RFC-0003

SQ-0003 ─ SQ-0008 core Lean types + RFC-0002/RFC-0004  READY
              └─ SQ-0009 assurance graph
                   └─ SQ-0017 trust report

SQ-0006 ─ SQ-0013/14/15 frontend skeletons
              └─ SQ-0016 conformance harness

SQ-0003 + SQ-0004 + frontends + conformance ─ SQ-0018 expanded CI
SQ-0007 + SQ-0010 + SQ-0012 + SQ-0016 + SQ-0017 + SQ-0018 ─ SQ-0019
SQ-0019 ─ SQ-0020 independent foundation review + RFC-0007/RFC-0009
```

Task eligibility is computed by `work/backlog.yaml`, accepted decision prerequisites, and `scripts/check_repository.py`. This diagram explains the intended path but does not override the ledger.

SQ-0003 and SQ-0004 were independent READY tasks. SQ-0003 is now DONE after
establishing the proof-backend build and trust-reporting surface. The computed
successor set is SQ-0004 and SQ-0008 READY. Neither successor has begun; each
requires a separate isolated execution and review transition.

## Milestone A — Ratify the constitution (SQ-0001)

Status: **DONE**.

### Completed result

- Reviewed charter, architecture, glossary, trust model, maturity language, naming, package boundaries, evidence taxonomy, serialization direction, theorem identity, and the first slice.
- Accepted ADR-0001, ADR-0002, ADR-0003, ADR-0006, ADR-0008, ADR-0009, ADR-0010, and ADR-0011.
- Kept ADR-0004, ADR-0005, ADR-0007 and RFC-0001 through RFC-0009 explicitly Draft/Proposed with machine-checked owners.
- Established source, statistical, formal, interoperability, security, adversarial, and integration review records.
- Selected the exact data-free `foundation_structural` fixture and exhaustive nonclaims.
- Replaced hard-coded scheduling with dependency- and decision-aware readiness.

### Evidence

See `work/reviews/SQ-0001.md`, `work/handoffs/SQ-0001.md`, and `docs/research/SQ-0001-constitutional-source-audit.md`.

## Milestone B — Pin and bootstrap toolchains (SQ-0002–SQ-0004)

### SQ-0002 — toolchain research

Status: **DONE**.

The reviewed evidence surface contains:

- 75 attempted combinations: 31 successes, 37 failures, seven unknowns;
- six recommendation records;
- 90 dated source records;
- 115 tracked, content-addressed prototype subjects after the packaging correction;
- a strict standard-library verifier with eight corruption regressions;
- distinct source, Lean, Rust, frontend, interoperability, statistical/trust, security/adversarial, integration, and packaging-integrity reviews.

Final evidence-packaging merge: `01c5b6e1bfacf332dbb01259aa19258a3edd0f9e`.

Reviewed recommendations:

| Area | Development/reference recommendation | Floor or boundary |
|---|---|---|
| Lean/Mathlib/Lake | Lean 4.32.2 commit `f3b06c705e6c85f5314019d5d3baab0fec5b580c`; Mathlib `905b95818eb32af7874a58b427f50c1711a5e96c`; Lake `5.0.0-src+f3b06c7` | exact pair only |
| Rust/Cargo | Rust 1.97.1 | compatibility-only Rust 1.85.1; offline compilation/API check, not networked acquisition |
| Python | CPython 3.14.7 | project floor Python 3.11; exact tested patch 3.11.15 |
| R | R 4.6.1/testthat 3.3.2 | project floor R 4.4; exact tested patch R 4.4.3/testthat 3.2.3 |
| Julia | Julia 1.12.6 | maintained LTS policy; exact tested LTS 1.10.11 |
| Arrow | PyArrow/Arrow C++ 25.0.0 and arrow-rs 59.1.0 | Experimental transport candidates only |
| CBOR/CDDL | cbor2 6.1.4 narrow current probe; retained historical differentials; cddl 0.10.6 | Experimental only; cddl 0.10.6 fails the Rust 1.85.1 floor |

Direct execution evidence is Linux x86-64 only. macOS, Windows, ARM, hosted-runner, publication, and intermediate-version coverage remains planned or unknown.

The permanent repository guardrail now runs `python3 scripts/bootstrap/run_toolchain_probes.py --verify` through `make check`, so later matrix, report, or retained-evidence drift fails CI.

### SQ-0003 — Lean/Mathlib project bootstrap

Status: **DONE**.

Follow `work/contracts/SQ-0003.yaml`.

Required result:

- production `lean/` project pinned to the exact reviewed Lean/Mathlib pair;
- reproducible `lake-manifest.json`;
- minimal namespace, internal/test-only smoke declaration, and test/example;
- normal and isolated no-binary-cache builds;
- actual machine-readable transitive axiom reports for named declarations;
- fail-closed mutations for `sorry`, `admit`, `sorryAx`, project axioms, toolchain/manifest changes, and unreviewed native trust;
- least-privilege Lean CI with pinned actions and observed runner metadata;
- exact documentation, source/formal/adversarial/CI/integration reviews, and handoff.

No statistical ontology, inference theorem, artifact checker, theorem-registry semantics, or public theorem is permitted in SQ-0003.

### SQ-0004 — Rust reference workspace bootstrap

Status: **IN_PROGRESS**.

Follow `work/contracts/SQ-0004.yaml` in a separate execution.

Required result:

- minimal `backend/` workspace pinned to Rust 1.97.1, Edition 2024, resolver 3, and `rust-version = "1.85.1"`;
- one exact Cargo lock acquired with current Cargo and tested under Rust 1.85.1 offline;
- workspace-level `unsafe_code = "forbid"` and strict lints;
- deterministic version/error CLI only, without IR/schema/canonicalization/artifact semantics;
- malformed-input/panic, unsafe, lock, registry/credential, output, license, and advisory tests;
- least-privilege Rust CI and independent reviews.

### Milestone-B acceptance

- Both projects build from clean, pinned environments.
- Each project records exact locks, normal and adverse paths, trust limitations, and successful CI.
- Neither project imports Experimental Arrow/CBOR/CDDL behavior into normative code.
- No task claims statistical verification.

## Milestone C — Settle an encoding prototype (SQ-0005–SQ-0007)

### SQ-0005

After SQ-0004, implement competing deterministic-CBOR prototypes using at least two independently originated implementations or oracles. Test integers/rationals, bytes, map ordering, Unicode, duplicate keys, IEEE bit patterns, intervals, missing values, extensions, non-profile encodings, and resource behavior. Resolve RFC-0001 and only the encoding-relevant boundary of RFC-0006. Rust output is not the semantic oracle.

### SQ-0006

After RFC-0001 is Accepted, create versioned CDDL files for numeric atoms, identifiers, extensions, and the exact data-free `foundation_structural` fixture. Avoid draft CDDL module/import syntax unless the revision is pinned and labeled Experimental. Add diagnostic JSON projections, valid and invalid examples, independently reviewed canonical bytes/digests, and migration/version policy. The artifact envelope remains SQ-0010. Real logical-data schema/digest remains RFC-0006/SQ-0027.

### SQ-0007

After RFC-0005 is Accepted, implement registry metadata/lock schema and a test-only definitionally trivial `True` conformance record. Bind canonical elaborated proposition bytes, normalization/environment version, canonical registry record, independently selected authorization root/policy/status, statement digest, proof/build lock, actual axiom report, and compatibility-proof path. Keep semantic identity, registry authorization, proof/build trust, and axiom evidence separate. Include a bytes-for-`False` mapped to `True` misbinding mutation. The toy record is not a public theorem or non-vacuity witness.

### Acceptance

- Independent implementations agree on every accepted golden vector.
- Every negative vector has a named rejection class.
- Draft RFC behavior is never implemented as accepted semantics.

## Milestone D — Create the minimal formal semantic skeleton (SQ-0008–SQ-0009)

### SQ-0008

After RFC-0002 and a narrow RFC-0004 boundary are Accepted, define only the minimal Lean interfaces required by the toy subset: claim class, assurance-input/evidence category, verification mode, external assumption, and typed claim reference. Supply source-grounded examples/nonexamples. Do not freeze a universal experiment or flat randomness abstraction.

### SQ-0009

Define toy assurance node/edge kinds and DAG well-formedness. Prove or structurally ensure that diagnostics, attestations, citations, provenance, unresolved obligations, and policy classifications cannot discharge deductive premises. Establish deterministic node identity for the toy subset.

### Acceptance

Public definitions have source/statistical/formal review and frozen hashes; no `sorry`, project axiom, or evidence promotion exists.

## Milestone E — Artifact and reference backend (SQ-0010–SQ-0012)

### SQ-0010

Resolve RFC-0008 and define the bounded deterministic artifact envelope, required manifest fields, content coverage, critical-feature behavior, offline resolution, report separation, privacy/redaction identity, and resource limits. Add path traversal, duplicate entry, oversized/decompression, truncation, lock-substitution, and unknown-critical fixtures.

### SQ-0011

Implement Rust parsing, validation, canonical encoding, domain-separated content digests, and inspect/validate commands for the data-free fixture only. Theorem registry/lock resolution belongs to SQ-0007. Do not implement logical-data schema, lowering, or digest before RFC-0006/SQ-0027. Hostile input must be bounded and panic-free as tested behavior.

### SQ-0012

Resolve RFC-0003 and implement the minimal Lean byte-to-term/verified-structure path for the toy object. Bind exact bytes, schema/profile, theorem/environment/proof locks, and proposition. Report every parser, decoder, generator, compiler, runtime, and platform component that enters each verification mode's TCB.

### Acceptance

Rust and Lean agree on the exact toy object and proposition. Malformed/misbinding inputs fail. Artifact-level kernel wording is prohibited until the accepted RFC-0003 path succeeds.

## Milestone F — Frontend skeletons and conformance (SQ-0013–SQ-0016)

Create package-native source skeletons after schema v0:

- R package source `statqed`, with live naming/policy recheck and `testthat`;
- Python distribution/import source `statqed`, with live naming/policy recheck and typed modern packaging;
- Julia package source `StatQED`, with live naming/policy recheck and tested General-compatible publication/mirror/split strategy.

Each frontend constructs the same data-free semantic object and delegates normative canonicalization to the accepted reference path. No model adapter is included.

SQ-0016 compares semantic objects, normalized diagnostics, canonical bytes, digests, and error classes. Shared-Rust caller agreement is integration evidence only; encoder acceptance also needs independent lineage and a mutation proving the harness detects Rust divergence.

## Milestone G — Trust report, CI, composed artifact, and review (SQ-0017–SQ-0020)

### SQ-0017

Define machine and human trust reports for the toy artifact. Include exact verification result/mode, checked claims, external assumptions, unresolved leaves, TCB, untrusted producers, locks, warnings, and exhaustive nonclaims. Never collapse multiple results into an aggregate stronger status.

### SQ-0018

Expand CI into pinned, least-privilege language jobs. Add generated-file checks, dependency review, trusted-path scans, cross-language conformance, malformed-input tests, clean-checkout reproduction, and artifact roundtrip.

### SQ-0019

Compose the ADR-0011 fixture from R, Python, and Julia. Require identical accepted semantic IR and canonical bytes, one Rust-produced bundle, structural validation, test-only `True` locks, the Accepted RFC-0003 path for any kernel result, and a report containing every ADR-0011 nonclaim.

### SQ-0020

Run an independent foundation review. Reproduce on clean environments; attack malformed inputs, locks, authorization, byte binding, resource behavior, and report language; resolve RFC-0007 and RFC-0009 or perform an explicitly reviewed owner handoff; update architecture and follow-up tasks rather than hiding limitations.

## Validation commands

Current repository-wide commands:

```bash
make check
make list-work
git diff --check
```

`make check` includes repository/ledger guardrails and the immutable SQ-0002 evidence verifier. Each later task adds exact scoped commands to its contract and nearest `AGENTS.md`/implementation guide.

## Recovery and idempotence

- Bootstrap scripts are repeatable and distinguish preparation from offline/clean execution.
- Generated files name source, generator, version, and reproducible command.
- Golden vectors and review subjects are content-addressed and never snapshot-updated without semantic review.
- Failed prototypes and counterexamples remain retained.
- Toolchain, dependency, schema, theorem, and artifact updates have atomic rollback instructions.
- Each task can be reverted without silently invalidating unrelated completed tasks.
- Task-state changes are atomic across contract, backlog, status, plan, review, and handoff.

## Progress

- [x] Architecture and agent scaffold installed — bootstrap commit.
- [x] SQ-0001 constitutional baseline — DONE 2026-08-03.
- [x] SQ-0002 toolchain research — DONE 2026-08-05; final evidence-packaging merge `01c5b6e1bfacf332dbb01259aa19258a3edd0f9e`; 75 probes, six recommendations, 90 sources, and 115 durable tracked subjects.
- [x] SQ-0003 Lean/Mathlib bootstrap — DONE 2026-08-08 from `d32c50adaec62543e1a7fbc52f62e33ce8f373bb` on `agent/SQ-0003-lean-bootstrap`; review package `34e4d856e3ee5c85aab91a0427f9b4176aa7aac7`. Exact pair: Lean `leanprover/lean4:v4.32.2` / commit `f3b06c705e6c85f5314019d5d3baab0fec5b580c`, Mathlib `905b95818eb32af7874a58b427f50c1711a5e96c`, Lake `5.0.0-src+f3b06c7`. Distinct Mathlib/source, build, formal trust, adversarial mutation, CI/reproducibility, and integration roles approved the package. Exact-package Lean run `31279603416` and guardrails run `31279603408` passed cached and isolated-source gates.
- [ ] SQ-0004 Rust bootstrap — IN_PROGRESS since 2026-08-09T09:27:36+02:00 from `726821bf1a29995756dc10cbbecfd452dccad7e5` on `agent/SQ-0004-rust-bootstrap` in `/tmp/statqed-sq0004`. Fixed policy: Rust 1.97.1 for development/acquisition, Rust 1.85.1 for locked offline compatibility only, Edition 2024, resolver 3, and `rust-version = "1.85.1"`. Assigned distinct Rust/source, workspace/MSRV, API/error-conformance, security/adversarial, CI/reproducibility, and integration reviewer roles. Starting platform: Linux 7.0.0-28-generic x86_64 GNU/Linux.
- [ ] SQ-0008 core Lean types/RFC ownership — READY by dependency calculation; independently unstarted, with RFC-0002/RFC-0004 still Draft for that task to resolve.
- [ ] SQ-0005 through SQ-0020.

## Surprises & Discoveries

- The original guardrail hard-coded SQ-0001 as permanently ready; readiness is now ledger- and decision-derived.
- RFC 8949 permits multiple deterministic choices, CDDL does not define canonical bytes, and CDDL module/import syntax remains draft work; RFC-0001 must select the complete profile.
- Registry 404s are point-in-time observations, not reservations or trademark clearance; publication names require live task-specific checks.
- A surface theorem digest cannot identify meaning without canonical elaborated proposition bytes, a locked environment, separate registry authorization, proof/build lock, and actual axiom report.
- A self-consistent artifact-supplied registry root has no governed authority merely because it is content-addressed.
- A data-free first fixture avoids freezing unresolved logical-table/digest semantics while exercising IR, registry, graph, envelope, Lean, and reporting paths.
- Task dependencies alone cannot enforce constitutional prerequisites; the ledger records Draft decision owners and Accepted-only prerequisites.
- Registered RFCs support only Draft and Accepted until non-cyclic successor semantics are reviewed; invalid statuses and completed Draft owners fail closed.
- RFC-0006 is owned by detailed task SQ-0027 so no real-data schema/digest/backend path lands prematurely.
- Exact Lean/Mathlib compatibility required the full Mathlib revision and its toolchain body; adjacent release-label combinations failed the immutable controls.
- SQ-0002's Lean evidence included both a binary-cache path and a 1,710-job no-cache source build; a restricted sandbox later failed closed on DNS rather than being normalized to success.
- Reproducible Python packaging required exact CPython standalone archives, uv, a hash-locked wheelhouse, and built-artifact digests.
- R development required a SHA-locked CRAN source closure after the proposed conda-forge combination proved unsatisfiable; the floor used an independent explicit conda lock.
- A fresh Julia depot tried to bootstrap mutable General; a fixed empty local registry made the dependency-free probes deterministic.
- Arrow file and stream IPC forms differed physically; CBOR libraries exposed permissive/divergent edge behavior; cddl 0.10.6 requires Rust 1.88 and cannot satisfy the Rust 1.85.1 floor.
- Python and Rust recommendations changed during review as new releases/source evidence appeared; superseded evidence was retained instead of rewritten.
- Rust 1.85.1 remains useful only as an offline compiler/API floor because the recorded Cargo advisories prohibit using it for general acquisition.
- SQ-0004's dependency-free production graph made the offline floor cheap and auditable, but it could not by itself prove that missing dependencies fail closed. A separate empty-Cargo-home fixture with an absent crate now demonstrates that Cargo 1.85.1 does not acquire while `--offline` is enforced.
- Rust 1.85.0, rather than the selected 1.85.1 patch, introduced Edition 2024. The task records 1.85.1 as the directly tested floor without rewriting release history or treating resolver 3 as compatibility proof.
- Current 2026 Cargo/tar, third-party-registry, and libssh2 advisories make the development/acquisition versus compatibility-floor distinction a security boundary: Cargo 1.97.1 acquires; Cargo 1.85.1 sees only the exact locked graph offline.
- Readiness appears in backlog and detailed contracts; status transitions must update both atomically.
- The first SQ-0002 merge referenced four ignored `.pytest_cache` files. The correction removed only those non-durable subjects and independently reverified 115 tracked hashes.
- A successful repository-guardrails run on the final SQ-0002 merge checked the ledger but did not run the strict evidence verifier because `make check` did not include it. The 2026-08-08 post-merge maintenance made the verifier a permanent guardrail.
- SQ-0003/SQ-0004 were technically READY but their original short contracts did not authorize complete task transitions/reviews or encode the reviewed negative tests. Their contracts are now executable without semantic improvisation.
- During SQ-0003, official Lean issue #14576 initially appeared to postdate the fixed Lean 4.32.2 pin and potentially affect kernel soundness. Exact ancestry showed release commit `f3b06c705e6c85f5314019d5d3baab0fec5b580c` immediately follows backport `8be817b3f6310f62f220861b0c92dbabb951115d` of the #14577 fix; the official minimized exploit is rejected under `lean --trust=0` with `(kernel) invalid projection` on the pinned binary.
- Text scanning alone could not establish the trusted declaration surface. The accepted path obtains module ownership, declaration kind, `isUnsafe`, types, and transitive axioms from the live Lean environment, then uses a comment/string-aware source scanner as a supplementary gate.
- A root-level hosted identity probe did not select the project-local Lean channel automatically. Explicit `elan run leanprover/lean4:v4.32.2` made tool identity independent of working-directory selection; the failed hosted attempt remains retained.
- The narrow production import built 88 jobs from source in about one minute locally and on the hosted runner. Local dependency/build state can nevertheless grow to several gigabytes, so `.lake` remains ignored and disposable while the small exact evidence records remain committed.
- Completing SQ-0003 makes SQ-0008 READY even while RFC-0002/RFC-0004 remain Draft because SQ-0008 owns and must resolve those RFCs. Contract/backlog/status parity required a readiness-only SQ-0008 contract update; this does not begin SQ-0008.

## Decision Log

- 2026-08-03: Opened RFC-0004 through RFC-0009 and retained RFC-0001 through RFC-0003 as explicit downstream decisions.
- 2026-08-03: Selected ADR-0011's data-free `foundation_structural` slice with a test-only proposition `True`; SQ-0001 froze no canonical bytes.
- 2026-08-03: Selected source-tree names only; registry names, publication topology, reservation, and legal clearance remain live checks.
- 2026-08-03: Added a machine-checked decision register, Accepted-only prerequisites, and fail-closed owner lifecycle.
- 2026-08-03: Separated theorem-record integrity, verifier-selected registry authorization, proposition/environment identity, proof/build trust, and actual axiom reporting.
- 2026-08-03: Assigned RFC-0006 and the first normative logical-data path to SQ-0027; SQ-0006/SQ-0011 remain data-free.
- 2026-08-03: Required SQ-0020 to resolve RFC-0007/RFC-0009 or perform a reviewed owner transition.
- 2026-08-03: Defined provenance-redaction identity: normative provenance changes create a new normative identity; inert report-only redaction changes physical bundle identity and records disclosure.
- 2026-08-03: Classified the toy `True` record as definitionally trivial, test-only, and ineligible for public-theorem non-vacuity.
- 2026-08-03: Accepted ADR-0001, ADR-0002, ADR-0003, ADR-0006, ADR-0008, ADR-0009, ADR-0010, and ADR-0011; retained ADR-0004, ADR-0005, ADR-0007 and all nine RFCs behind their owners.
- 2026-08-05: Finalized SQ-0002 development pins and floors listed under Milestone B; direct support claims remain Linux x86-64 only.
- 2026-08-05: Retained Arrow, CBOR, and CDDL findings as Experimental compatibility evidence only; no canonicalization/data semantics were accepted.
- 2026-08-05: Independent integration review approved package `c43b90e39eebe500d70f6d0957a61a549c90545e` and atomic DONE transition `7a0b726189155d4131b30df63aee6c60f19671d9`.
- 2026-08-05: Packaging correction removed four ignored test-runner cache files, preserved all substantive evidence, and was merged as `01c5b6e1bfacf332dbb01259aa19258a3edd0f9e` after independent re-review.
- 2026-08-08: Post-merge review approved SQ-0002 with planning maintenance, made its strict verifier part of `make check`, corrected current-task/status/count metadata, and expanded SQ-0003/SQ-0004 contracts without changing recommendations or task states.
- 2026-08-08: Recommended SQ-0003 as the next isolated task because it establishes the proof-backend build and axiom/trust surface; SQ-0004 remains independently READY.
- 2026-08-08: Retained the exact reviewed Lean/Mathlib pair after verifying that Lean 4.32.2 includes the #14577 kernel-fix backport and independently rejects the official #14576 exploit. This regression becomes additional SQ-0003 trust evidence rather than a reason to substitute a toolchain.
- 2026-08-08: Kept the SQ-0003 library deliberately non-statistical: one internal/test-only `True` smoke declaration and narrow `Mathlib.Data.Set.Defs` import, with no registry, artifact, certificate, ontology, or public theorem surface.
- 2026-08-08: Bound the Experimental proof environment to the exact Lean/Mathlib pair, Lake-generated full dependency lock, live axiom report, and 33 mutation cases; the report is observation rather than authorization or RFC-0005 resolution.
- 2026-08-08: Required both normal and independently isolated no-binary-cache source paths. Hosted source revalidation runs weekly, manually, and on lock changes, with a 14-day fail-closed review age.
- 2026-08-08: Independent integration review approved package `34e4d856e3ee5c85aab91a0427f9b4176aa7aac7` and corrected the successor calculation to SQ-0004/SQ-0008 READY with `blocked_count: 55`; neither successor begins in SQ-0003.
- 2026-08-08: Atomic transition `3194f12b1b14f48813e98db60cac9c42f5c7280c` recorded SQ-0003 DONE, SQ-0004/SQ-0008 READY, 55 blocked tasks, no active task, and Experimental-only Lean dashboard evidence.
- 2026-08-08: Independent final review approved head `94a6381e25c18fbd317e119e8f6b80d91239ce61`; PR #5 merged as `92e3b331b1ae795a21d6e030a21e8ce8d7da03dd`, and main guardrails `31280203088` plus cached/source Lean run `31280203112` passed.
- 2026-08-09: Kept the SQ-0004 production graph dependency-free and limited it to `statqed-core` plus a thin `statqed-cli`; no speculative schema, encoding, artifact, registry, certificate, or frontend crate was created.
- 2026-08-09: Fixed the bootstrap CLI protocol at version 1 only for deterministic version and malformed-invocation responses, with exit 2, stable symbolic errors, literal response fixtures, and fixed 64-argument/4,096-byte-per-argument/8,192-byte-total limits. This is not an artifact-verifier schema or Draft-RFC decision.
- 2026-08-09: Required Rust 1.97.1 for all acquisition and release-oriented tooling while restricting Rust/Cargo 1.85.1 to the exact committed graph under `--locked --offline`; the floor cannot read credentials or alternate registries and may not regenerate `Cargo.lock`.
- 2026-08-09: Bound the Experimental workspace candidate to full rustc/Cargo source identities, a byte-reproducible local-only lock, 20 adversarial mutations, ten deterministic process fixtures, a normalized license inventory, and cargo-audit 0.22.2 against immutable RustSec database commit `1237bbe09d2701e14e6593a630fbaf28928df712`.

## Outcomes & Retrospective

### SQ-0001

Eight high-level architectural ADRs are Accepted. Three narrower ADRs and nine RFCs remain explicitly governed. The exact first slice is data-free, test-only, and non-statistical. The task established source-aligned review, explicit trust boundaries, and a decision-aware work ledger.

### SQ-0002

A strict verifier binds the compatibility report to 75 successful, failed, or unknown attempts, six recommendation records, 90 dated sources, retained logs/locks, and 115 durable tracked subjects. Corruption cases detect mutable recommendations, platform laundering, arbitrary reruns, failure normalization, empty locks, advisory corruption, environment inheritance, and unavailable recommended tooling. Distinct specialist and integration reviews approved the surface. No production toolchain, package, RFC, schema, or statistical semantics were introduced.

Post-merge review found no blocking research defect. It converted the SQ-0002 verifier into a permanent repository guardrail and repaired stale successor planning. It made SQ-0003 and SQ-0004 READY; SQ-0003 subsequently completed while SQ-0004 remains unstarted. Full foundation retrospective remains SQ-0020 work.

### SQ-0003

The repository now contains a minimal Experimental Lean project pinned to Lean
4.32.2 and exact Mathlib commit
`905b95818eb32af7874a58b427f50c1711a5e96c`. Its Lake-generated manifest
reproduced byte-for-byte, normal and isolated source builds passed, and a live
environment report observed no axioms for the internal smoke theorem and
`Quot.sound`/`propext` for imported `Set.ext`. Thirty-three positive,
negative, lock, report, native-trust, and kernel-regression mutations pass.

Distinct source, build, formal, adversarial, CI/reproducibility, and integration
reviewers approved the exact package. The exact-package hosted run exercised
both cached and isolated-source paths. This is build, trust-surface, and axiom
observation evidence only: no statistical semantics, source-fidelity claim,
artifact-byte binding, theorem authorization, checker soundness, or verified
analysis was introduced. The computed next READY set is SQ-0004 and SQ-0008;
both remain unstarted. Full foundation retrospective remains SQ-0020 work.
