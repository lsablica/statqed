# SQ-0005 evidence-lifecycle maintenance review

Status: IN_REVIEW

This supplemental record reviews only the lifecycle interpretation of the
permanent SQ-0005 evidence. It does not replace or rewrite
`work/reviews/SQ-0005.md`. PR #11 and PR #12 remain the historical scientific,
profile, prototype, conformance, and integration evidence. PR #13 exposed the
fail-closed defect before SQ-0006 was claimed: the v1 verifier compared the
live global task ledger to the frozen SQ-0005 completion state.

## Maintenance subject

The v2 evidence model separates:

- `historical_completion_state`, which preserves the exact SQ-0005 completion
  state and the original 158-subject v1 manifest; and
- `live_invariants`, which protect SQ-0005 decisions, subjects, retained
  failures, lineage, production-path boundaries, and successor-contract
  integrity without freezing the entire live task graph.

The v2 manifest retains the original v1 manifest hash
`0512a79a42cc6c6b70e5c139044841827b3ac3103968892fe6f135f02436a233`
and its subject-map aggregate
`59aa64011c7afea1ed923a50479f151999cfcd16f7fa125114f6558c9a2b9105`.
The original SQ-0005 review remains bound at
`a45c57c5abf9d99b89a5c5b86143da34651728a86b3b72d8ca7d5886a62f3ff7`.
The unchanged semantic fixture tree remains explicitly bound at
`90fc4b5a1346f0693b84a0fa9a6a1e1fa4ac535aff2b83d6177313c6779fa3c8`.
The full historical SQ-0006 and SQ-0008 contract hashes are retained as
separate completion bindings in addition to the original subject map.

No RFC-0001 normative bytes, ADR-0004 normative bytes, profile semantics,
prototype source, semantic fixtures, golden vectors, generated conformance
results, RFC-0006 bytes, production implementation, or SQ-0008 contract bytes
changed in this maintenance subject. SQ-0006 and SQ-0008 remained READY while
the repair was authored.

## Lifecycle policy reviewed

- SQ-0005 must remain DONE in its contract, backlog, and live ledger.
- RFC-0001 and ADR-0004 must remain Accepted with byte-identical marked scope.
- RFC-0006 must remain byte-identical, Draft, and owned by SQ-0027.
- SQ-0006 and SQ-0008 contract/backlog statuses must agree and may be only
  READY, IN_PROGRESS, IN_REVIEW, or DONE after SQ-0005 completion.
- SQ-0008 live integrity uses a canonical parsed projection that omits only its
  top-level `status`; the original whole-file hash remains in the frozen v1
  manifest.
- The repository guardrail, rather than SQ-0005 evidence, owns global task-set
  and blocked-count consistency.
- Shared successor-owned planning and documentation paths remain historically
  bound but are not falsely live-frozen by SQ-0005. Deterministic section
  projections preserve SQ-0005-owned canonicalization and dashboard content
  while allowing separately reviewed successor sections and claims.
- The Makefile must contain exactly one SQ-0005 evidence target with the exact
  verifier recipe; include/SHELL indirection and target shadowing are rejected.

A static verifier cannot prove temporal monotonicity between two otherwise
allowed successor statuses without history. Contract/backlog agreement,
allowed-state membership, live-ledger membership, repository guardrails, and
reviewed commits jointly enforce the lifecycle boundary.

## Regression evidence

The original 12 evidence-corruption tests remain present. Thirty-eight
additional lifecycle-model tests cover the frozen completion snapshot and
historical successor contracts; SQ-0006 READY,
IN_PROGRESS, IN_REVIEW, and DONE; SQ-0008 status-only evolution; SQ-0005
regression; contract/backlog disagreement; illegal status; historical-state
mutation; RFC/ADR regression and scope divergence; RFC-0006 ownership drift;
SQ-0008 semantic drift; production-path drift; scientific-subject drift; and
the distinction between local evidence invariants and global ledger checks.
They also cover active-review redirection; plain, grouped, multi-target,
indented, and variable-expanded Makefile shadowing; assignments, inline
comments/recipes, phony, and special-target bypasses; shared-document content
and rendering-context corruption; and permitted successor-owned documentation
additions.

Exact local and hosted command dispositions are added to this record only
after the content-addressed candidate passes them. The SQ-0006 preclaim gate
must remain unresolved until that review and hosted CI are complete.

## Independent review dispositions

- Evidence-model semantics: PENDING exact candidate review.
- Verifier implementation: PENDING exact candidate review.
- Corruption and lifecycle regression tests: PENDING exact candidate review.
- Manifest reproducibility and historical preservation: PENDING exact
  candidate review.
- SQ-0006 preclaim-gate resolution: PENDING hosted exact-head checks.
- Integration scope: PENDING exact candidate review.

## Bound subjects

<!-- SQ-0005-REVIEW-SUBJECTS-BEGIN -->
```json
{
  ".github/workflows/serialization-prototypes.yml": "3cb67d26721258413ff80150df453dca77f76ea77374fe6a5a92bd7494cd8536",
  "ARCHITECTURE.md": "482523d5cf858b1674852074695ecab54623bbbe0814f5e9417eca32f060005a",
  "conformance/prototypes/evidence/evidence-manifest.json": "e0745ae5bf4cde30eeeb6148600bd00c324ca9de7c4061e150d7da67d27a403f",
  "conformance/prototypes/evidence/evidence-spec.json": "666706ba320ea092d3b3d5af27842563dbdcbe85d5ead907a7f1d8d1df82d976",
  "conformance/prototypes/fixtures/semantic-v1/catalog.json": "d5bf3079d9ff8119a2372873a1b116601011e78c30067bc1d05228211659b4d3",
  "conformance/prototypes/fixtures/semantic-v1/digest-framing.json": "36895de279202434a1511bb1bf552c199e55d57ee8a57a7d724772a737824d0b",
  "conformance/prototypes/generated-v1/manifest.json": "e69e863053fad44faf2511cedbd53a13725e309cbdb0551621e217c2095dd6cd",
  "conformance/prototypes/generated-v1/mutations.json": "1b6c448a29ce76b83c5e85673731382dc24bba8a1902a7686988626015d22da6",
  "conformance/prototypes/generated-v1/results.json": "4e48d962644cec0f83b868ba13bcc62f3bc8cee4dca748fed10e3ad911195274",
  "conformance/prototypes/golden/serialization-v1/manifest.json": "8db0e43760421ea694e0e2d7095ade93a821ce5f3b7c66eaf954d7fe969af7a1",
  "docs/adr/0004-deterministic-cbor-cddl.md": "a27be26c3d4e89518943b08a4d042ef9a2c824612df77c45ad07abd5bcb587f4",
  "docs/research/serialization/profile-candidate.md": "6cbf0f686a1f35b5c6fac8411ef5abc708c9c4410b5fdb2ee510c513df067d2f",
  "docs/research/serialization/semantic-value-model.md": "a94588e54fdc3e2aa08e73f5f6e76bb71128940bb245305b2dec9dffa2ffcfb2",
  "rfcs/0001-deterministic-encoding.md": "0f542ba487e77a2008a71ef6c92b642cf89503d96d8da63680575e109a97741f",
  "schemas/prototypes/cddl/profile-v1.cddl": "05ee85b0d028af588ed9e95e83fdf017259988f05709de85f033cb0ab5badda0",
  "schemas/prototypes/lineage.json": "7a7e48658e81e478c3858f265d24eb0c1402fa6169e7c03eb74363effb8208a4",
  "schemas/prototypes/python-oracle/.python-version": "aa0d6581054e6e4ff3f91839deca7a854ad37221b8784d060b42d0f847ff1a3b",
  "schemas/prototypes/python-oracle/LINEAGE.md": "8dfe50d1a4010984881c77cd48fa3eca14e307e71d8cc0b5afed48d3e6babd92",
  "schemas/prototypes/rust-cbor/Cargo.lock": "2e9c4f95aa0aa54ab2338e980d388f9f0223be8964d94f82d82f086f2dadb180",
  "schemas/prototypes/rust-cbor/LINEAGE.md": "6136314a0c7ac9b971f636e520e8d9dd0d94548f39a96a891d34a37ac9e1dd1a",
  "schemas/prototypes/rust-cbor/evidence/advisory-report.json": "abe01dc61e4f02fb179f39457077b832491c3503d8461fe82f1835712482cd55",
  "schemas/prototypes/rust-cbor/evidence/crates-io-yanked.json": "fd69cb31758d9f3da5f674a3b14b731bda03ba77e9ca1295e03663d67e571e2b",
  "schemas/prototypes/rust-cbor/evidence/dependency-license-inventory.json": "3d44e9d26c756c2aa950779f9fcf557f11efc28a50d20f27c2ec1a501aaadfa9",
  "scripts/serialization/build_evidence_manifest.py": "3a0f29acabbdec759526f50f53394a77c47df035cd90495c81e60c677b04be09",
  "scripts/serialization/check_evidence.py": "59d7015214adde42a698e2dba547a4b8993a010e14a90c7f508f361f73dbc6be",
  "scripts/serialization/run_conformance.py": "8a61f6deeeba7bed4e8bb7e0c8202fa0ce730d5328036365d8536ed5950fe01c",
  "scripts/serialization/tests/test_check_evidence.py": "5959c3abfcc50bdcf88def50d5518dfc566894680aff18fa6ffa13c497518e36",
  "source-audits/encoding/manifest.json": "b3f70746a36c350590f2f77ffebb0e550773337d79db4103317426be94ac0a40",
  "work/reviews/SQ-0005.md": "a45c57c5abf9d99b89a5c5b86143da34651728a86b3b72d8ca7d5886a62f3ff7"
}
```
<!-- SQ-0005-REVIEW-SUBJECTS-END -->

## Seven integration questions

1. Preserve immutable SQ-0005 historical evidence: PENDING.
2. Accept legitimate SQ-0006 lifecycle evolution without regeneration:
   PENDING.
3. Reject SQ-0005 regression: PENDING.
4. Preserve RFC-0006 exactly: PENDING.
5. Preserve SQ-0008 semantics while allowing status-only evolution: PENDING.
6. Leave actual SQ-0006 READY: PENDING.
7. Avoid general weakening of evidence validation: PENDING.

Final disposition: PENDING
