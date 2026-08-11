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

SQ-0001 established the constitutional boundaries. SQ-0002 selected reviewed toolchain recommendations but initialized no production project and accepted no Draft RFC semantics. SQ-0003 and SQ-0004 completed the separately reviewed Lean and Rust production bootstraps. SQ-0005 accepted the bounded data-free RFC-0001 profile after independent prototype and conformance review. SQ-0006 completed the separately reviewed data-free fixture schema. The ledger has no active task; SQ-0007, SQ-0008, SQ-0011, SQ-0013, SQ-0014, and SQ-0015 are independently READY and unstarted.

## Dependency and decision graph

```text
SQ-0001 constitutional baseline                       DONE
  └─ SQ-0002 toolchain research                      DONE
       ├─ SQ-0003 Lean bootstrap                     DONE
       └─ SQ-0004 Rust bootstrap                     DONE
            └─ SQ-0005 serialization prototype       DONE
                 └─ RFC-0001                         ACCEPTED
                      └─ SQ-0006 schema v0            DONE
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

SQ-0003, SQ-0004, SQ-0005, and SQ-0006 are DONE after separately reviewed
proof-backend, reference-workspace, encoding-profile, and data-free schema
foundations. The computed READY set is SQ-0007, SQ-0008, SQ-0011, SQ-0013,
SQ-0014, and SQ-0015. No successor is active.

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

Completed result:

- production `lean/` project pinned to the exact reviewed Lean/Mathlib pair;
- reproducible `lake-manifest.json`;
- minimal namespace, internal/test-only smoke declaration, and test/example;
- normal and isolated no-binary-cache builds;
- actual machine-readable transitive axiom reports for named declarations;
- fail-closed mutations for `sorry`, `admit`, `sorryAx`, project axioms, toolchain/manifest changes, and unreviewed native trust;
- least-privilege Lean CI with pinned actions and observed runner metadata;
- fresh same-kernel replay of the compiled smoke module and imports through `leanchecker --fresh`;
- exact documentation, source/formal/adversarial/CI/integration reviews, and handoff.

No statistical ontology, inference theorem, artifact checker, theorem-registry semantics, or public theorem is introduced by SQ-0003.

### SQ-0004 — Rust reference workspace bootstrap

Status: **DONE**.

Completed result:

- minimal `backend/` workspace pinned to Rust 1.97.1, Edition 2024, resolver 3, and `rust-version = "1.85.1"`;
- one exact Cargo lock acquired with current Cargo and tested under Rust 1.85.1 offline;
- workspace-level `unsafe_code = "forbid"` and strict lints;
- deterministic version/error CLI only, without IR/schema/canonicalization/artifact semantics;
- malformed-input/panic, unsafe, lock, registry/credential, output, license, and advisory tests;
- least-privilege Rust CI and independent reviews;
- final merge/workflow evidence recorded in PR #9 / commit `4aa0b9c145ce2595f3630d17abcfb7e4248579b4`.

### Milestone-B acceptance

- Both projects build from clean, pinned environments.
- Each project records exact locks, normal and adverse paths, trust limitations, and successful CI.
- Neither project imports Experimental Arrow/CBOR/CDDL behavior into normative code.
- No task claims statistical verification.

## Milestone C — Settle an encoding prototype (SQ-0005–SQ-0007)

### SQ-0005

Use the detailed contract in `work/contracts/SQ-0005.yaml`. Implement a data-free deterministic-encoding prototype using at least two genuinely independent canonicalization implementations or oracles. Resolve RFC-0001 only after current primary-source audit, explicit semantic and byte-profile decisions, raw duplicate-key handling, exact byte vectors, deliberate-divergence detection, numeric/Unicode/tag/extension tests, strict decoder-result classes, resource bounds, generic data-free domain framing, permanent evidence verification, and independent review all pass.

RFC-0006 is read-only in SQ-0005. It remains owned by SQ-0027 and governs the first logical table, physical-to-logical lowering, privacy-sensitive data commitments, and canonical logical-data digest. SQ-0005 may record generic atom and framing requirements for later work, but it must not resolve or edit RFC-0006. Rust prototype output is not the semantic oracle and must not modify the production `backend/` workspace.

### SQ-0006

Under Accepted RFC-0001, define only the exact closed six-field data-free
`statqed.foundation-structural.v0` fixture. Use published RFC 8610 syntax as
updated by RFC 9682, deterministic source concatenation, an independent
standard-library semantic validator, semantic-first positive/negative cases,
two read-only SQ-0005 implementation comparisons, direct-from-spec expected
bytes, and `statqed.fixture.golden` digest framing. No numeric atom family,
extension channel, public ontology, artifact envelope, or logical-data schema
is introduced. RFC-0006 remains read-only under SQ-0027.

### SQ-0007

After RFC-0005 is Accepted, implement registry metadata/lock schema and a test-only definitionally trivial `True` conformance record. Bind canonical elaborated proposition bytes, normalization/environment version, canonical registry record, independently selected authorization root/policy/status, statement digest, proof/build lock, actual axiom report, and compatibility-proof path. Keep semantic identity, registry authorization, proof/build trust, and axiom evidence separate. Include a bytes-for-`False` mapped to `True` misbinding mutation. The toy record is not a public theorem or non-vacuity witness.

### Acceptance

- Independent implementations agree on every accepted golden vector.
- Every negative vector has a named rejection class.
- Deliberate encoder and decoder divergences are detected before golden vectors can change.
- Draft RFC behavior is never implemented as accepted semantics.
- RFC-0006 logical-data semantics remain untouched until SQ-0027.

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

`make check` includes repository/ledger guardrails, the immutable SQ-0002 toolchain-evidence verifier, and the permanent SQ-0005 serialization-evidence verifier. Each later task adds exact scoped commands to its contract and nearest `AGENTS.md`/implementation guide.

## Recovery and idempotence

- Bootstrap scripts are repeatable and distinguish preparation from offline/clean execution.
- Generated files name source, generator, version, and reproducible command.
- Golden vectors and review subjects are content-addressed and never snapshot-updated without semantic review.
- Failed prototypes and counterexamples remain retained.
- Toolchain, dependency, schema, theorem, and artifact updates have atomic rollback instructions.
- Each task can be reverted without silently invalidating unrelated completed tasks.
- Task-state changes are atomic across contract, backlog, status, plan, review, and handoff.
- RFC ownership is respected: a task may record cross-cutting requirements but may not edit or accept another task's decision document.

## Progress

- [x] Architecture and agent scaffold installed — bootstrap commit.
- [x] SQ-0001 constitutional baseline — DONE 2026-08-03.
- [x] SQ-0002 toolchain research — DONE 2026-08-05; final evidence-packaging merge `01c5b6e1bfacf332dbb01259aa19258a3edd0f9e`; 75 probes, six recommendations, 90 sources, and 115 durable tracked subjects.
- [x] SQ-0003 Lean/Mathlib bootstrap — DONE 2026-08-08 from `d32c50adaec62543e1a7fbc52f62e33ce8f373bb` on `agent/SQ-0003-lean-bootstrap`; review package `34e4d856e3ee5c85aab91a0427f9b4176aa7aac7`. Exact pair: Lean `leanprover/lean4:v4.32.2` / commit `f3b06c705e6c85f5314019d5d3baab0fec5b580c`, Mathlib `905b95818eb32af7874a58b427f50c1711a5e96c`, Lake `5.0.0-src+f3b06c7`. Distinct Mathlib/source, build, formal trust, adversarial mutation, CI/reproducibility, and integration roles approved the package. Exact-package Lean run `31279603416` and guardrails run `31279603408` passed cached and isolated-source gates.
- [x] SQ-0004 Rust bootstrap — DONE 2026-08-09 from `726821bf1a29995756dc10cbbecfd452dccad7e5` on `agent/SQ-0004-rust-bootstrap`; implementation `33d7a50f98996d01ce2a210e304d376e7d310e53`, corrected review package `cecbaa318f043bedd9898afe20e9f930c39eb732`, atomic transition `a8e886386cbef9437f0c6912f96d6d29ac6023c4`, final reviewed head `35a8404920dee19ecda6e8c6a0e549cacd06b069`, task merge `7a83eb843a216886816553897bf541aeb0270c22`, and post-merge evidence commit `4aa0b9c145ce2595f3630d17abcfb7e4248579b4`. Exact policy: Rust 1.97.1 for development/acquisition, Rust 1.85.1 for locked offline compatibility only, Edition 2024, resolver 3, and `rust-version = "1.85.1"`. Distinct Rust/source, workspace/MSRV, API/error-conformance, security/adversarial, CI/reproducibility, and integration reviewers approved the package; final main Rust, guardrail, and Lean workflows passed.
- [x] SQ-0005 deterministic-serialization/RFC prototype — DONE 2026-08-09 from `8875d8f6fa8e3b45e706ea567d45448927a02efa` on `agent/SQ-0005-deterministic-serialization`; frozen implementation `410465d773fc011ee01e38e6e76a79a60efe8837`, independently approved pre-transition package `8e041fbe34742a0f32db776ee39cc5c2534f7f8d`, atomic transition `cc1021e33441b4bfba5c1459d644d2c5a6b79127`, focused hosted-evidence correction `9cd4fa315c17919e25351d474cf579a7b6909bd5`, Accepted-status correction `77c924a078c1481b9cead5979746109e51b85364`, scope amendment `34337cbcf89d24b7b29a5fa0d20616343dd5a316`, accepted-state synchronization `18eb333712a1475067bc7730ae1cd8f81f8d25e5`, final reviewed head `c6e90b118b691a819d617bb6d411c96382ea197c`, and PR #11 normal merge `62707add05fcebb7cabbb3d4cff3cd97b22dfa4c`. Direct local platform: Ubuntu 24.04.4 LTS, Linux 7.0.0-28-generic, x86_64. Main guardrails `31327728104`, serialization `31327728110`, Rust `31327728156`, and Lean `31327728117` passed at the exact merge commit; serialization covered both exact Python jobs, locked Rust gates, 273 cases, supply-chain observations, 158-subject evidence verification, 12 corruption tests, and byte-identical manifest regeneration. RFC-0001 and matching ADR-0004 accept the bounded data-free `statqed.cbor-core.v1` profile and generic `statqed.digest-lp.v1` framing. Distinct source, semantic, Rust, Python-lineage, conformance, parser/security, cryptographic, formal/CDDL, CI/release, and integration roles approved the transition and merge. RFC-0006 remains byte-identical and Draft under SQ-0027; no logical-data semantics entered this task.
- [ ] SQ-0008 core Lean types/RFC ownership — independently READY and unstarted, with RFC-0002/RFC-0004 still Draft for that task to resolve.
- [x] SQ-0006 schema v0 — DONE 2026-08-10 from `d9afd96460afb3c5902a93f134044168bc4e4df3` at 2026-08-10T08:57:10+02:00 on `agent/SQ-0006-schema-v0` in `/tmp/statqed-sq0006-schema-v0`; synchronized through normal branch merge `b857e8941c1f64a0baf459f7a2a85f83647fad49` with verified maintenance main `aac98bae3ecb27cba8cea895bc64454a890cde7a`. Direct environment Ubuntu 24.04.4 LTS, Linux 7.0.0-28-generic, x86-64. Assigned distinct schema/CDDL source curator, field-semantics architect, schema engineer, independent semantic-validator engineer, golden/conformance reviewer, malformed/security reviewer, versioning reviewer, CI/reproducibility reviewer, and independent integrator. RFC-0006 remained read-only under SQ-0027 and SQ-0008 remained READY/unstarted.
- [x] SQ-0006 implementation evidence — `5093a3d7afca0e98ec47a67de1364a378f97741a` freezes five accepted semantic fixtures, 85 retained negatives, three detected deliberate divergences, exact `cddl` 0.10.6 shape checks, two read-only SQ-0005 comparisons plus a direct standards recipe, a 154-package lock-bound license inventory, and permanent static corruption checks. Distinct source, semantic, formal/schema, conformance, adversarial, versioning, CI/reproducibility, and integration reviewers approved exact review head `542c6c516e17bba883691ce1d00972ef1d3077ea`; guardrails `31372523046`, Serialization prototypes `31372523061`, Schema v0 `31372523282`, Rust `31372523049`, and Lean `31372523110` passed before the atomic DONE transition.
- [x] SQ-0006 protected integration — final reviewed head `b569f24e95a2465f71a16affa344d57164a23b27` merged normally through PR #15 as `e4bd2f0e739aaf480170d16a3424b40af1e9cf5b` on 2026-08-11. Main guardrails `31489194387`, Serialization prototypes `31489194324`, Schema v0 `31489194383`, Rust `31489194316`, and Lean `31489194370` passed; exact-merge Schema v0 dispatch `31489484813` and Serialization prototypes dispatch `31489483135` independently reproduced the bound counts and byte-identical regeneration. The checked READY set is SQ-0007, SQ-0008, SQ-0011, SQ-0013, SQ-0014, and SQ-0015; no successor was claimed.
- [x] SQ-0006 successor-evidence maintenance — the v2 evidence model retains the complete v1 completion manifest and original scientific digest as immutable history, permits independently reviewed READY-state contract planning without evidence regeneration, and replaces whole-tree gates with static path-granular ownership. The original 22 schema tests plus 29 lifecycle/path regressions pass; all six successor contracts remain byte-identical, READY, and unclaimed during the maintenance.
- [x] SQ-0006 successor-evidence maintenance integration — exact reviewed head `272db072f574a085a8fa3a619f50673e7bcc31ce` merged normally through PR #19 as `f2baf677a71a30923d4d63ecf0667c51fb179795`. Five normal main workflows and exact-main Schema/Serialization dispatches passed; the replacement Serialization dispatch `31501154760` completed successfully after run `31500674505` remained stuck at parent-run state despite all three jobs succeeding. The historical scientific digest remains `4bfd5fad7f9884d592d5c8c320dbd4efd735c990f3b23d6b3cb5d8e9854df5f0`.
- [x] SQ-0007 executable planning contract — expanded and independently reviewed on `planning/SQ-0007-executable-contract` with explicit RFC-0005 ownership, eleven separate identity/trust layers, exact pinned-source research, versioned normalizer and bounded closure obligations, verifier-selected authorization, proof/build and axiom locks, directional compatibility, six digest domains, stable errors/resources, permanent evidence, pinned CI, distinct reviews, and exhaustive nonclaims. Hosted checks and a protected planning merge remain required before launch from main; SQ-0007 and every other successor remain READY and unclaimed.
- [ ] SQ-0007 theorem registry and lock v0 — claimed `IN_PROGRESS` on 2026-08-11T21:56:01+02:00 from reviewed main `6148589f10ee58a8cba58f959aec25c6f5207e8d` in `/tmp/statqed-sq0007-theorem-registry` on `agent/SQ-0007-theorem-registry`. Launch contract SHA-256: `2be5ff48bd9d6d17d6b62de6ca0a536f90288ab453ce06819f692b92d8efe0ef`. Direct platform: Ubuntu 24.04.4 LTS, Linux 7.0.0-28-generic, x86_64. Distinct source/Lean-internals, theorem-semantics, Lean-extractor, independent-normalization, Rust-resolver, cryptographic, authorization/security, compatibility/counterexample, CI/reproducibility, and integration roles were assigned. The task is now `IN_REVIEW` with an explicit blocking disposition because the shared ledger represents dependency-eligible tasks only as READY or active; RFC-0005 remains Draft, ADR-0007 remains Proposed, RFC-0006 is read-only, and every other READY task remains unstarted.
- [ ] SQ-0007 fail-closed integration blocker — the inherited SQ-0003 trust scanner correctly requires the global live axiom report to enumerate every project module, while SQ-0005 evidence rejects the five new Registry Lean files, nine standalone Registry Rust files, and any regenerated global report as protected production drift. Both independent formal-trust and integration review reject ignoring the new modules or weakening either predecessor verifier. A separate reviewed SQ-0003/SQ-0005 lifecycle maintenance must preserve the historical snapshots, introduce exact compositional module/declaration coverage, and authorize only the two static Registry subtrees before SQ-0007 can resume.
- [ ] SQ-0007 predecessor regression fixtures — at the legitimate `IN_REVIEW` state, 13 of 59 SQ-0005 evidence tests fail behind the same path-set rejection, and two of 51 SQ-0006 lifecycle/path tests fail because their READY-owner scenarios inherit the live SQ-0007 state instead of explicitly constructing READY. These predecessor tests remain untouched and must be made successor-state-independent in the separate maintenance.
- [ ] SQ-0007 and SQ-0009 through SQ-0020.

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
- SQ-0004 integration review found that a handoff attributed separate build and doctest commands to the 15-command isolated JSON transcript. Those gates had passed independently and in CI, but the retained transcript contains identity, lock-generation, acquisition, metadata, fmt, Clippy, test, and version-output commands. The corrected package now keeps those evidence classes explicit.
- The SQ-0004 post-merge review found no Rust defect but exposed a planning boundary error: the old SQ-0005 contract allowed direct edits to RFC-0006 despite SQ-0027 ownership. The corrected contract makes RFC-0006 read-only and requires independent encoding lineage, durable evidence, and explicit data-free scope.
- RFC 8949's core and length-first deterministic profiles produce different map order for real key pairs. The accepted v1 profile selects complete-key-byte core order explicitly; library defaults cannot silently select the compatibility alternative.
- Duplicate evidence disappears if a decoder constructs a native map too early. Both prototypes therefore retain ordered raw entries through validity, key-class, typed-duplicate, preferred-head, and ordering checks.
- Independent cryptographic review found one initially inconsistent boundary: complete 129-byte identifiers and truncated length-prefixed components were classified alike by one oracle. Two semantic-first raw-frame fixtures now preserve the reviewed field-specific-versus-truncation distinction across both implementations.
- A normal working-tree `git diff --check` did not expose three blank lines at EOF already committed on the branch. Branch-wide comparison against the reviewed base did; the exact tree bindings and generated manifest were regenerated after the cleanup.
- The accepted profile is intentionally narrower than generic CBOR: no tags, floats, bignums, rationals, decimals, normalization, intervals, or extensions become normative merely because a library can decode them. Explicit exclusion keeps future semantics reviewable.
- The source-only Rust prototype has complete lock-bound license expressions and point-in-time RustSec evidence, but binary redistribution still requires a reviewed third-party notice bundle.
- A one-commit hosted checkout can verify the current evidence package yet still fail a baseline-relative provenance check. The first serialization run retained this failure; the narrowly reviewed correction fetches full read-only history only for the baseline-dependent job and leaves Python-only jobs shallow.
- Status headers alone were insufficient to keep the accepted decision record coherent: final integration review found stale Draft/Proposed closing prose in otherwise Accepted RFC/ADR documents. The corrected evidence now binds status-consistent decision prose without changing the marked normative bytes.
- The protected normal merge preserved the exact reviewed SQ-0005 tree. Main then independently reran repository, serialization, Rust, and Lean workflows at the merge commit; post-merge planning can therefore advance to SQ-0006/SQ-0008 without changing the accepted profile or treating prototypes as production authority.
- The six fixed text keys sort identically under RFC core and length-first map ordering, so no schema-specific identifier can discriminate those algorithms. SQ-0006 retains the SQ-0005 generic integer-key discriminator and tests only reverse producer insertion versus strict raw order for this fixture.
- Exact closed CDDL rejects many malformed objects before schema semantics. The evidence therefore records five independent layer results and follows RFC-0001 precedence rather than relabeling a CDDL mismatch as a field-specific schema failure.
- `cddl` 0.10.6 accepts duplicate map members and rejects some below-i64 CDDL integer literals even while its generic `int` accepts the corresponding CBOR value. Duplicate validity and RFC-0001 integer range remain outside CDDL authority; both limitations are retained.
- The SQ-0005 dashboard projection intentionally protects its historical paragraph. SQ-0006 evidence is appended without rewriting that paragraph, keeping the permanent predecessor verifier green while adding evidence-supported Experimental status.
- The first SQ-0006 hosted schema run `31370432183` received HTTP 403 from the crates.io API download endpoint before executing schema code. The failure is retained; CI now uses the official static crates.io archive URL and verifies the same immutable package SHA-256 before extraction.
- The first green schema head exposed two latent SQ-0005 lifecycle-test assumptions: a successor-owned path was treated as necessarily absent, and a Makefile mutation anchor assumed no intervening successor target. Separately reviewed PR #16 made those tests successor-safe without weakening the verifier or changing any schema, profile, fixture, golden, or production subject.
- The SQ-0006 DONE candidate exposed one further predecessor simulation-only omission: moving SQ-0006 backward from DONE did not re-block its dependent successors. Three-file PR #17 added two regressions, retained all earlier coverage, and passed 59 tests without changing schema, profile, fixture, golden, RFC, ADR, production, or SQ-0008 subjects.
- Post-merge planning exposed a distinct successor-contract lifecycle boundary: SQ-0006 evidence correctly preserves non-status successor-contract semantics, but the existing SQ-0007 contract still needs expansion before implementation and direct expansion would fail that permanent projection. A separate reviewed evidence-lifecycle/planning maintenance is required before any successor is claimed; this is not a schema defect.
- The original whole-tree contamination gate assigned all of `lean/`, `backend/`, or `frontends/` to one successor state. Static disjoint partitions are required instead: SQ-0007 can own only registry subtrees, SQ-0008 only assurance/guarantee subtrees, and each frontend task only its language subtree, while unowned remainder and `schemas/prototypes/**` stay frozen.
- Hard-link shadow copies crossed filesystem boundaries and traversed user-owned `.codex/` state. The lifecycle suite now copies only Git-tracked files with metadata-preserving ordinary copies, making the tests filesystem-independent and keeping user-owned untracked content outside the test surface.
- Expanding a successor contract is repository planning, not predecessor science: SQ-0006 evidence v2 accepted the reviewed SQ-0007 planning change without regenerating its historical manifest or scientific digest. The executable contract therefore owns future theorem-registry decisions while SQ-0006 continues to protect only its completed schema subject and static path boundary.
- SQ-0007 exposed a separate earlier-predecessor boundary: SQ-0006 v2 correctly recognizes Registry path ownership, but SQ-0005 still freezes all Lean and backend paths, and SQ-0003's single global axiom report is both live coverage and a frozen historical subject. Sound composition requires historical/live separation plus complete, non-overlapping coverage; filtering out Registry modules would be a trust regression.
- Predecessor mutation tests must construct the lifecycle state they claim to test. Once SQ-0007 became active, two SQ-0006 simulations that implicitly assumed READY ceased testing their stated case; correcting those fixtures is predecessor maintenance, not authority to edit them from SQ-0007.

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
- 2026-08-09: Independent integration review approved corrected package `cecbaa318f043bedd9898afe20e9f930c39eb732` after the isolated-transcript attribution was repaired. Atomic transition `a8e886386cbef9437f0c6912f96d6d29ac6023c4` records SQ-0004 DONE, SQ-0005/SQ-0008 READY, 54 blocked tasks, and no active task; neither successor begins in this execution.
- 2026-08-09: Final reviewed head `35a8404920dee19ecda6e8c6a0e549cacd06b069` was green and PR #8 merged as `7a83eb843a216886816553897bf541aeb0270c22`. Main Rust run `31305247261`, guardrails `31305247241`, and unchanged Lean run `31305247233` passed before post-merge metadata recording.
- 2026-08-09: PR #9 recorded final SQ-0004 merge/workflow evidence in main commit `4aa0b9c145ce2595f3630d17abcfb7e4248579b4`; main Rust `31305825523`, guardrails `31305825572`, and Lean `31305825538` passed.
- 2026-08-09: Independent post-merge review approved SQ-0004 without changing Rust code or task state, selected SQ-0005 as the next isolated task, and rebuilt its contract around RFC-0001 ownership, genuinely independent canonicalization evidence, permanent evidence verification, and strict non-ownership of RFC-0006.
- 2026-08-09: Selected `statqed.cbor-core.v1`: RFC 8949 Section 4.2.1 core deterministic ordering, preferred definite-length encoding, direct-range integers, exact Unicode preservation without normalization, integer/text map keys, and a closed tag/float/extension-free v1 subset.
- 2026-08-09: Selected staged strict verification rather than decode-and-reencode repair. Well-formedness, CBOR validity, application expectedness, deterministic profile, CDDL shape, semantic validity, schema validation, digest verification, resources, and operational failure remain separate result classes.
- 2026-08-09: Selected the generic data-free `statqed.digest-lp.v1` SHA-256 frame with purpose, algorithm, profile, object-class/schema, framing version, explicit lengths, and payload. It binds identifiers but grants no schema authority and resolves no RFC-0006 logical-data decision.
- 2026-08-09: Independent integration authorized package `8e041fbe34742a0f32db776ee39cc5c2534f7f8d` after eight specialist review records approved frozen implementation `410465d773fc011ee01e38e6e76a79a60efe8837`; hosted CI and final evidence verification remain fail-closed merge gates.
- 2026-08-09: Accepted RFC-0001 and matching ADR-0004, marked SQ-0005 DONE, and made only SQ-0006 readiness state READY. SQ-0008 remains READY/unstarted; RFC-0006 remains unchanged Draft under SQ-0027. The decision-aware ledger reports 53 blocked tasks and no active task.
- 2026-08-09: Retained hosted run `31320961923` as a reproducibility-environment failure when final evidence regeneration could not read base `8875d8f...` from a one-commit checkout. Independent CI review approved focused correction `9cd4fa315c17919e25351d474cf579a7b6909bd5`, which gives only the conformance job full read-only history; serialization run `31321428088` then passed every job and regenerated the 157-subject manifest byte-identically.
- 2026-08-09: Final integration audit blocked merge because stale closing paragraphs still called RFC-0001 Draft and ADR-0004 Proposed. Correction `77c924a078c1481b9cead5979746109e51b85364` made that post-decision prose consistent with the Accepted headers and atomic transition, preserved the byte-identical marked scope, and regenerated the content-addressed evidence package.
- 2026-08-09: A separate reviewed scope amendment authorized only two current-state wording corrections in `ARCHITECTURE.md`, which otherwise remained outside SQ-0005 scope. The amendment permits replacing stale RFC-0001 candidate language with the Accepted bounded data-free decision and forbids any architecture, trust, package-boundary, or normative-scope change.
- 2026-08-09: Accepted-state synchronization `18eb333712a1475067bc7730ae1cd8f81f8d25e5` used that narrow authority for exactly two architecture sentences, corrected RFC/ADR/spec disposition language, and added `ARCHITECTURE.md` to the permanent evidence and review subject map. The marked RFC/ADR scope remained byte-identical; the regenerated manifest binds 158 subjects.
- 2026-08-09: Synchronized content head `6787022a4fb23bde589e62796fb13c3e8d4d78bf` passed exact-head serialization run `31322606288` and the complete PR regression set: serialization `31322603702`, repository guardrails `31322603705`, Rust development/offline floor `31322603706`, and Lean trust/mutations `31322603742`.
- 2026-08-09: Independent integration approved final head `c6e90b118b691a819d617bb6d411c96382ea197c`; PR #11 merged it normally as `62707add05fcebb7cabbb3d4cff3cd97b22dfa4c`. Main guardrails `31327728104`, serialization `31327728110`, Rust `31327728156`, and Lean `31327728117` passed before post-merge planning advanced SQ-0006 as the recommended next isolated task while preserving SQ-0008 READY/unstarted.
- 2026-08-10: SQ-0006 fixed the schema candidate at exactly six required fields and no extension or feature-element ontology. Five validation layers remain independently observable; the primary result follows RFC-0001 precedence.
- 2026-08-10: Selected published RFC 8610 syntax as updated by RFC 9682, exact `cddl` 0.10.6 as an untrusted CI/development shape producer, and direct byte concatenation with the closed root rule first. Draft module/import syntax remains prohibited.
- 2026-08-10: Selected `statqed.fixture.golden` framing for data-free fixture bytes only. This creates neither a schema resolver nor the RFC-0006 logical-data digest.
- 2026-08-10: Independent integration approved exact hosted-green head `542c6c516e17bba883691ce1d00972ef1d3077ea`; SQ-0006 became DONE. The shared calculation made SQ-0007, SQ-0008, SQ-0011, SQ-0013, SQ-0014, and SQ-0015 READY with 48 blocked tasks and no active task. No successor was claimed, and RFC-0006 remained unchanged Draft under SQ-0027.
- 2026-08-11: Independently approved three-file predecessor lifecycle PR #17 merged normally as `aac98bae3ecb27cba8cea895bc64454a890cde7a`; its four main workflows passed before merge commit `b857e8941c1f64a0baf459f7a2a85f83647fad49` brought that verified main into the SQ-0006 branch. The correction changed no SQ-0006 scientific subject or successor task state.
- 2026-08-11: External authorization merged exact reviewed PR #15 head `b569f24e95a2465f71a16affa344d57164a23b27` normally as `e4bd2f0e739aaf480170d16a3424b40af1e9cf5b`. Five normal main workflows and exact-merge Schema/Serialization dispatches passed without changing evidence manifest `eefe309c3ab16d05321e5071698009b716721b8c1119c7c48bf4fa37d60521eb`, scientific digest `4bfd5fad7f9884d592d5c8c320dbd4efd735c990f3b23d6b3cb5d8e9854df5f0`, or RFC-0006.
- 2026-08-11: Recorded SQ-0007 as the expected next scientific task only after a separate successor-contract lifecycle/planning maintenance. SQ-0008 and every other READY successor remain unstarted; no successor contract is expanded by the SQ-0006 post-merge record.
- 2026-08-11: Separated immutable SQ-0006 completion history from live successor lifecycle. Evidence v2 nests and authenticates the complete v1 manifest, retains all six historical successor hashes, and treats later reviewed successor planning as repository-governance state rather than SQ-0006 scientific identity.
- 2026-08-11: Selected a static path-ownership policy rather than trusting mutable successor `allowed_paths`: registry, assurance/guarantee, backend, and language-specific frontend partitions unfreeze only for their explicitly listed active owners; all unowned partitions remain at their historical baseline.
- 2026-08-11: Expanded SQ-0007 planning without claiming it. RFC-0005 remains Draft and must be accepted from current pinned Lean/Mathlib and independent prototype evidence before SQ-0007 can become DONE; matching ADR-0007 remains Proposed, and RFC-0006 remains read-only under SQ-0027.
- 2026-08-11: Claimed only SQ-0007 after exact main, ledger, predecessor-evidence, RFC/ADR, contract-hash, and remote-overlap preflight. The implementation boundary is the test-only ADR-0011 `True` record and eleven separately reported identity/trust layers; no digest, resolver result, or kernel observation may silently stand for source fidelity, authorization, artifact verification, non-vacuity, or statistical validity.
- 2026-08-11: Moved SQ-0007 to `IN_REVIEW` with a blocking disposition after independent formal-trust and integration review reproduced predecessor evidence failures. The shared ledger cannot label a dependency-eligible task BLOCKED, but no in-task exception is permitted: the next operation is a separate reviewed SQ-0003/SQ-0005 lifecycle repair preserving historical evidence while adding static Registry ownership and complete compositional axiom coverage.

## Outcomes & Retrospective

### SQ-0006

The completed Experimental foundation separates profile decode,
deterministic-byte conformance, CDDL shape, fixture semantics, and
fixture-digest verification. Its scope is one data-free six-field fixture and
explicit nonclaims. Five positives, 85 negatives, three deliberate
divergences, exact CDDL validation, independent encoder observations, retained
failures, static evidence, and clean hosted/local gates passed distinct source,
semantic, formal/schema, conformance, adversarial, versioning,
CI/reproducibility, and integration review. It does not define the general IR,
logical data, an artifact envelope, theorem identity, a certificate, a
production canonicalizer, provenance truth, or statistical validity.

PR #15 preserved that exact reviewed subject through normal merge
`e4bd2f0e739aaf480170d16a3424b40af1e9cf5b`. Seven main runs reproduced the
permanent predecessor, serialization, schema, mutation, and regeneration
gates. The ledger now exposes six READY successors and no active task, but
successor execution remains paused until SQ-0007 receives a complete reviewed
planning contract. The exact contract is now complete and independently
reviewed; once its planning-only PR is green and merged, a future isolated
execution may claim SQ-0007 only after a fresh preflight. The
successor-evidence maintenance preserves the complete
v1 completion manifest and historical scientific digest, adds 29 regressions,
and gives future tasks only path-granular authority. SQ-0006 remains DONE; no
scientific or normative subject changed at that maintenance boundary.

### SQ-0001

Eight high-level architectural ADRs are Accepted. Three narrower ADRs and nine RFCs remain explicitly governed. The exact first slice is data-free, test-only, and non-statistical. The task established source-aligned review, explicit trust boundaries, and a decision-aware work ledger.

### SQ-0002

A strict verifier binds the compatibility report to 75 successful, failed, or unknown attempts, six recommendation records, 90 dated sources, retained logs/locks, and 115 durable tracked subjects. Corruption cases detect mutable recommendations, platform laundering, arbitrary reruns, failure normalization, empty locks, advisory corruption, environment inheritance, and unavailable recommended tooling. Distinct specialist and integration reviews approved the surface. No production toolchain, package, RFC, schema, or statistical semantics were introduced.

Post-merge review found no blocking research defect. It converted the SQ-0002 verifier into a permanent repository guardrail and repaired stale successor planning. It made SQ-0003 and SQ-0004 READY; both subsequently completed in separate reviewed executions. Full foundation retrospective remains SQ-0020 work.

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
analysis was introduced. At SQ-0003 completion the computed next READY set was
SQ-0004 and SQ-0008; SQ-0004 has since completed, while SQ-0008 remains READY
and unstarted. Full foundation retrospective remains SQ-0020 work.

### SQ-0004

The repository now contains a minimal Experimental Rust reference workspace
with dependency-free `statqed-core` and `statqed-cli` crates. Rust 1.97.1 owns
acquisition, lock generation, development, formatting, Clippy, tests, and
security tooling; Rust 1.85.1 compiles and tests only the exact lock offline.
The lock reproduced byte-for-byte, both roles passed locally and on hosted
runners, and 20 unsafe, policy, lock, credential, registry, output, panic, and
workflow mutations fail closed. The exact two-package inventory is MIT-only;
the hash-bound RustSec observation reported no finding at the recorded database
commit.

Distinct source, workspace/MSRV, API, security, CI/reproducibility, and
integration reviewers approved the corrected package. This is workspace,
bounded bootstrap CLI, reproducibility, and point-in-time supply-chain evidence
only: it introduces no statistical objects, schema, canonical bytes, digests,
artifact verification, theorem registry, certificate system, frontend
protocol, or Draft-RFC decision.

Post-merge review found no blocking Rust defect. It corrected the final
integration record, selected SQ-0005 as the recommended next task, and removed
RFC-0006 from SQ-0005's writable scope. The computed READY set remains SQ-0005
and SQ-0008; both are unstarted. Full foundation retrospective remains SQ-0020
work.

### SQ-0005

RFC-0001 and ADR-0004 now define one bounded data-free deterministic encoding
profile. `statqed.cbor-core.v1` selects RFC 8949 core map order, preferred
definite-length bytes, exact Unicode preservation, narrow map keys, and a
closed semantic subset. `statqed.digest-lp.v1` provides generic length-prefixed
SHA-256 framing without defining logical-data identity or schema authority.

Independent Rust and Python implementations preserve raw map entries and agree
across 273 semantic-first cases: 70 accepted, 203 rejected, zero differential
failures, 69 retained joint goldens, and 20 detected deliberate divergences.
The permanent evidence verifier binds the source audit, profile, fixtures,
goldens, failures, implementation lineage, dependencies, reviews, RFC/ADR
state, RFC-0006 baseline, SQ-0008, and protected production trees.

The first hosted run failed closed on missing Git history rather than weakening
the baseline comparison. The retained failure and independently reviewed
checkout correction were then exercised by successful hosted run
`31321428088` on observed Ubuntu 24.04.4/x86-64 image `20260720.247.2`.

Final reviewed head `c6e90b118b691a819d617bb6d411c96382ea197c`
merged normally through PR #11 as
`62707add05fcebb7cabbb3d4cff3cd97b22dfa4c`. Main guardrails
`31327728104`, serialization `31327728110`, Rust `31327728156`, and Lean
`31327728117` all passed at that merge commit. The current checked READY set is
SQ-0006 and SQ-0008; SQ-0006 is recommended next and SQ-0008 remains unstarted.

This is Experimental semantics and conformance evidence. Neither prototype is
production authority or part of the proof TCB; CDDL is structural only; digest
equality is conditional; and no artifact, logical table, provenance,
certificate, theorem, numerical, inferential, or statistical validity claim is
introduced. The computed successor set is SQ-0006 and SQ-0008 READY, both
unstarted. Full foundation retrospective remains SQ-0020 work.
