# SQ-0006 Post-Merge Review

## Integration subject

- External merge authorization covered only exact reviewed PR #15 head
  `b569f24e95a2465f71a16affa344d57164a23b27` and bounded post-merge records.
- PR #15 merged normally through the protected pull-request mechanism as
  `e4bd2f0e739aaf480170d16a3424b40af1e9cf5b` at
  `2026-08-11T12:00:29Z`.
- The merge first parent is
  `aac98bae3ecb27cba8cea895bc64454a890cde7a`; its second parent is the exact
  authorized PR head.
- The schema evidence-manifest SHA-256 remains
  `eefe309c3ab16d05321e5071698009b716721b8c1119c7c48bf4fa37d60521eb`.
- The scientific-subject digest remains
  `4bfd5fad7f9884d592d5c8c320dbd4efd735c990f3b23d6b3cb5d8e9854df5f0`.
- RFC-0006 remains byte-identical at
  `e834f805cc38fca2185433c72df4ac7db856c0ae20037fedcb57329a740b3429`,
  Draft, and owned by SQ-0027.

The historically bound `work/reviews/SQ-0006.md` is unchanged. This
supplement records integration and main reproduction only; it does not rewrite
the scientific review history.

## Hosted main verification

All five normal push workflows completed successfully on exact merge commit
`e4bd2f0e739aaf480170d16a3424b40af1e9cf5b`:

- repository guardrails `31489194387`;
- Serialization prototypes `31489194324`;
- Schema v0 `31489194383`;
- Rust reference workspace `31489194316`; and
- Lean proof backend `31489194370`.

Two manual exact-merge dispatches also completed successfully:

- Schema v0 `31489484813`; and
- Serialization prototypes `31489483135`.

Job-level logs and local reproduction reported:

- 59 predecessor evidence/lifecycle tests;
- 273 serialization cases, zero failures, 69 joint goldens, and all 20
  deliberate divergences detected;
- 49 schema evidence subjects, five positive fixtures, 85 negative fixtures,
  and three deliberate schema mutations;
- 22 schema unit/corruption tests; and
- byte-identical compiled CDDL and schema/serialization evidence regeneration.

The local checkout under `/home` and its `/tmp` shadow directories are on
different filesystems, so the unchanged 22-test schema corruption suite could
not use its hard-link copy optimization from that checkout. The same suite
passed on hosted CI and in a clean detached `/tmp` worktree at the exact merge
commit. This is a recorded host-filesystem limitation, not a schema or test
correction.

## Final ledger and decision boundary

The checked ledger remains:

- DONE: SQ-0001 through SQ-0006;
- READY: SQ-0007, SQ-0008, SQ-0011, SQ-0013, SQ-0014, and SQ-0015;
- ACTIVE: none; and
- BLOCKED: 48.

SQ-0008 remains unstarted. RFC-0001 and ADR-0004 retain their Accepted
statuses and matching marked scope. No RFC, ADR, schema-v0 scientific subject,
fixture, golden, validator, evidence specification, evidence manifest,
production Rust path, Lean path, or frontend path changed during post-merge
recording.

## Successor-contract lifecycle boundary

SQ-0006 evidence currently binds non-status semantic projections of SQ-0007,
SQ-0008, SQ-0011, SQ-0013, SQ-0014, and SQ-0015 contracts. The current SQ-0007
contract is not detailed enough for implementation, but direct expansion would
fail the permanent SQ-0006 evidence checker. A separate independently reviewed
evidence-lifecycle/planning maintenance must preserve the immutable SQ-0006
completion subject while permitting legitimate successor-contract planning
evolution.

This is a planning and evidence-lifecycle issue, not a defect in the accepted
schema subject. It does not change SQ-0006 DONE status. No successor was
claimed, expanded, or implemented in this record branch.

## Trust boundary and nonclaims

The merged result remains Experimental structural evidence for one closed,
data-free fixture. It does not establish a general statistical IR, source
fidelity, identification, inference, numerical certification, provenance
truth, logical-data identity, artifact-envelope semantics, theorem identity or
authorization, certificate soundness, production canonicalizer authority, or
verification of arbitrary `.statqed` artifacts.

Disposition: `APPROVE_SQ0006_MERGED`; the record-only pull request remains
subject to its own independent integration review and required checks.
