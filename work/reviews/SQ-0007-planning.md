# SQ-0007 executable-contract planning review

Status: **APPROVE_PLANNING**. This record reviews planning only. SQ-0007
remains `READY`; it does not approve an RFC decision, theorem-registry
implementation, task claim, or merge of a future implementation.

## Subject

- Reviewed base and Phase-A merge:
  `f2baf677a71a30923d4d63ecf0667c51fb179795` (PR #19).
- Branch: `planning/SQ-0007-executable-contract`.
- Expanded contract SHA-256:
  `2be5ff48bd9d6d17d6b62de6ca0a536f90288ab453ce06819f692b92d8efe0ef`.
- `START_HERE.md` SHA-256:
  `06c8fb5481942f008728ad96fd2c0ec7321412af71f1b8038b9e6951e9adff2c`.
- Active execution-plan SHA-256:
  `51c6dde9274af46c9499fef089dc36f19812da819c557b7a71f26ff6b1423b6f`.
- Unchanged RFC-0005 SHA-256:
  `e009007110d65a182eacb55d290f7307e9dfbd38a6d29b60941694ac50c5f6ed`;
  status `Draft`.
- Unchanged ADR-0007 SHA-256:
  `96ea0ba0e9bfbd26d65f85fcbcf1ed03de2ddafa430ea529bc01a91e8dbb5ff8`;
  status `Proposed`.
- Unchanged RFC-0006 SHA-256:
  `e834f805cc38fca2185433c72df4ac7db856c0ae20037fedcb57329a740b3429`;
  status `Draft`, owner SQ-0027.
- Unchanged SQ-0006 scientific-subject digest:
  `4bfd5fad7f9884d592d5c8c320dbd4efd735c990f3b23d6b3cb5d8e9854df5f0`.
- Unchanged SQ-0006 v2 evidence-manifest SHA-256:
  `5c6b3081846ba8ec2bc1ac17bf7d9014ee4d8f2dedb9e7d625a1226d2957b752`.

The planning diff contains no theorem-registry implementation, RFC or ADR
status change, task-state change, schema/prototype/golden change, production
Lean/Rust/frontend change, or successor claim.

## Contract disposition

`APPROVE_PLANNING`. The executable contract:

- authorizes the complete registry-specific implementation, evidence,
  documentation, workflow, review, handoff, and readiness-only successor
  surface while forbidding unrelated assurance, general-backend, frontend,
  artifact, data, method, and statistical-ontology work;
- owns RFC-0005 for completion, keeps matching ADR-0007 conditional on that
  acceptance, and makes RFC-0006 read-only;
- requires current exact-pinned Lean/Mathlib and cryptographic/dependency
  primary-source research before freezing semantics;
- separates governed ID/version, proposition, environment closure, statement
  digest, registry record, record digest, verifier policy/root, proof/build
  lock, actual axiom report, compatibility lock, and review annotations;
- requires a versioned expression grammar rather than pretty-printed text, a
  bounded meaning-bearing closure, two independently originated observations,
  and a visibly test-only ADR-0011 `True` record;
- makes authorization state verifier-selected, compatibility directional and
  kernel-checked, and each digest domain explicitly separate;
- specifies deterministic errors, finite resource limits, hostile/mutation
  cases, permanent evidence verification, pinned least-privilege CI, distinct
  specialist reviews, fail-closed status transitions, and exhaustive
  nonclaims; and
- forbids SQ-0007 from becoming `DONE` while RFC-0005 remains `Draft`.

The standalone Rust registry package remains confined to
`backend/crates/statqed-registry/**`, and Lean registry material remains
confined to `lean/StatQED/Registry/**`. Root workspace/toolchain files and
pre-existing production namespaces remain outside scope.

## Independent dispositions

### Executable-contract planning

The first read-only planning review by `/root/sq0006_contract_review` returned
`REVISE` on predecessor hash
`03bf56c20c7c8d9112f3147b228fc6b511146126b9df265f6775d7a957d19359`.
It required an explicit `sources` field, executable live-axiom/trust/fresh-
checker/supply-chain/clean-tree commands, an unambiguous standalone Cargo
boundary, mandatory source anchors/original attribution for the toy record,
and non-premature planning wording. The corrected contract addresses all five
findings and the reviewer returned `APPROVE_SQ0007_PLANNING` for the exact hash
above after also correcting `leanchecker --fresh` to use a module name and
running the live axiom extractor under `--trust=0`.

### Formal and trust boundary

`APPROVE_FORMAL_TRUST_PLANNING` by
`/root/sq0006_path_ownership_review`, a
distinct read-only formal/trust reviewer. The reviewer confirmed separation of
all eleven layers, verifier-selected authorization, live axiom observation,
useful-direction kernel compatibility, six digest domains, the `True`
fixture's nonclaims, and the registry-only Lean/Rust path boundary.

The reviewer notes an execution obligation already present in the contract:
the later source audit must bind the Lean-core source anchor/original
attribution for the test-only declaration, and normalizer/exporter and resolver
components remain operational/evidence producers unless independently rebound.

### Evidence-lifecycle regression

`APPROVE_EVIDENCE_LIFECYCLE_PLANNING` by
`/root/sq0006_lifecycle_model_review`, a distinct read-only evidence reviewer.
The exact non-status contract expansion passed the SQ-0006 verifier without
regenerating its v2 manifest, nested v1 completion snapshot, or scientific
digest. The ledger remained `DONE=6`, `READY=6`, `ACTIVE=none`, `BLOCKED=48`;
all other successor contracts retained their reviewed hashes. The contract's
Registry-only Lean/Rust paths match the static Phase-A ownership partitions,
and mutable `allowed_paths` do not become predecessor authority.

### Integration

The independent integration reviewer must approve the exact committed planning
head, confirm the four-file planning/governance-only scope, rerun the local
gates, verify hosted PR checks, and authorize only the protected normal merge
of this planning change. That later disposition does not authorize claiming or
implementing SQ-0007.

## Commands and results

At the planning candidate:

```text
python3 -m json.tool work/contracts/SQ-0007.yaml
  PASS
git diff --check
  PASS
make check
  PASS — repository, SQ-0002, SQ-0005, and SQ-0006 permanent checks
make list-work
  PASS — DONE=6 READY=6 BLOCKED=48; active=none
python3 scripts/serialization/check_evidence.py
  PASS — 158 historical, 155 live, 203 negative
python3 scripts/schema/check_schema_v0.py
  PASS — 49 subjects, 5 positive, 85 negative, 3 mutations
python3 scripts/schema/build_evidence_manifest.py --check
  PASS — byte-identical
```

The focused synthetic READY-state non-status SQ-0007 planning mutation passed
the SQ-0006 verifier. No evidence subject was regenerated to match the expanded
contract.

## Remaining boundaries

RFC-0005 remains Draft and ADR-0007 remains Proposed. Their exact normalizer,
closure, registry record, authorization policy, axiom/proof locks, compatibility
semantics, resources, and digest framing remain work for a separately claimed
SQ-0007 execution. The contract is executable planning, not evidence that any
registry or theorem-lock interface exists. SQ-0008, SQ-0011, SQ-0013, SQ-0014,
and SQ-0015 remain independently READY and unstarted.
