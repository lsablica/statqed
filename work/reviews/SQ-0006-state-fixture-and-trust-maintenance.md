# SQ-0006 State-Fixture and Trust-Maintenance Review

## Subject and boundary

This supplemental review covers only the versioned SQ-0006 evidence-lifecycle
adaptation needed by the compositional predecessor-trust maintenance. It does
not revise the historical scientific review in `work/reviews/SQ-0006.md` or
the successor-lifecycle review in
`work/reviews/SQ-0006-successor-lifecycle.md`.

The v3 package preserves these immutable historical bindings:

- completion evidence v1 manifest:
  `eefe309c3ab16d05321e5071698009b716721b8c1119c7c48bf4fa37d60521eb`;
- successor-lifecycle evidence v2 manifest:
  `5c6b3081846ba8ec2bc1ac17bf7d9014ee4d8f2dedb9e7d625a1226d2957b752`;
- SQ-0006 historical scientific-subject digest:
  `4bfd5fad7f9884d592d5c8c320dbd4efd735c990f3b23d6b3cb5d8e9854df5f0`;
- RFC-0006 baseline:
  `e834f805cc38fca2185433c72df4ac7db856c0ae20037fedcb57329a740b3429`.

The 49 v1 completion subjects, schema sources, published-syntax CDDL,
fixtures, goldens, results, mutations, and scientific meaning are unchanged.
The v3 package records maintenance-only live trust baselines separately; it
does not absorb them into the SQ-0006 scientific subject.

## Defect and correction

Two SQ-0006 ownership regressions inherited the copied repository's ambient
SQ-0007 state. A copied SQ-0007 branch in `IN_REVIEW` therefore made scenarios
named `SQ-0007 READY` and `SQ-0008-only owner` exercise a different policy
than their names and assertions specified.

Every ownership scenario now establishes every relevant owner state before it
changes a protected path. In particular:

- `test_phase_a_15_sq0007_ready_registry_change_rejected` explicitly sets
  SQ-0007 to `READY`;
- the first scenario of
  `test_phase_a_21_sq0008_active_registry_change_rejected` explicitly sets
  SQ-0007 to `READY` and SQ-0008 to `IN_PROGRESS`;
- shared Registry/backend and frontend partitions explicitly set their other
  relevant owner to `READY`; and
- the no-owner backend cases explicitly set both SQ-0007 and SQ-0011 to
  `READY`.

A meta-regression starts copies in both SQ-0007 `READY` and `IN_REVIEW`, then
constructs the same READY/no-owner scenarios and requires identical rejection
results. Historical manifests and scientific evidence are not regenerated to
match either ambient state.

The evidence identifiers are versioned to
`statqed.sq0006-evidence-spec.v3` and `statqed.sq0006-evidence.v3`. The v3
manifest embeds and canonically authenticates the complete v2 lifecycle
manifest, which itself embeds the complete v1 completion manifest. It also
records content hashes for the maintenance-only live Lean trust inputs and a
new reviewed `lean_remainder` baseline. Those values protect the new live
trust infrastructure while keeping it outside the historical scientific
subject.

## Evidence and tests

The original 51 schema tests remain. Four additional regressions cover:

1. mutation of the embedded v2 lifecycle manifest;
2. drift in a maintenance-only live trust baseline; and
3. ambient SQ-0007 `IN_REVIEW` versus `READY` equivalence for explicitly
   constructed READY/no-owner scenarios; and
4. pruning an untracked ignored operational cache even when a dependency
   checkout contains a symlink, while retaining fail-closed Git-index checks.

The resulting schema suite has 55 tests. Dynamic evidence remains five
positive fixtures, 85 negative fixtures, and three detected deliberate
mutations. Exact v3 bindings for the reviewed local candidate are:

- evidence specification: `271a8d205be6247f3c89f8d76310144ead33f94a526feffd429aac94c496b1d2`;
- evidence manifest: `954964f556c1954bfab537b124348862913931006ae57c606ec9ae97d383dc23`;
- manifest generator: `be48cbd4f081fbdbacfd2c96688ca1eac2febea0b86600c2d15bf862e5472b99`;
- verifier: `540091772ca57322f490c492234c17b892f84b9c13947f4d75d144148613d2ae`;
- regression suite: `fb4750929e20df3ed88f37c2b2851d15ef30de557208df3d9330bd22903355cf`.

Hosted workflow bindings remain a merge gate and are appended only after an
exact committed head exists; this supplemental review remains outside the
recursively hashed evidence subject.

## Trust boundary and nonclaims

This maintenance corrects test isolation and binds new live trust
infrastructure. It does not change schema-v0 semantics, establish a public
statistical IR, prove source fidelity, authorize a theorem registry, accept
RFC-0005, accept ADR-0007, define logical-data identity, or alter RFC-0006.
All successor tasks remain READY and unclaimed on the maintenance branch.

Independent evidence-lifecycle, Lean/formal-trust, adversarial, CI, and final
integration dispositions are separate merge gates and must bind the exact
committed maintenance head.

## Independent evidence-lifecycle disposition

The independent evidence-lifecycle reviewer approved this v3 maintenance
package (`APPROVE_PHASE_M_EVIDENCE`) at implementation commit
`50947998ed62806ff42f51c7b850a55465594f12`. The reviewer reproduced all 55
tests (51 retained plus four maintenance regressions), byte-identical manifest
generation, explicit READY/no-owner scenario construction, ambient-state
independence, unchanged 49-subject scientific evidence, and the unchanged
historical scientific digest
`4bfd5fad7f9884d592d5c8c320dbd4efd735c990f3b23d6b3cb5d8e9854df5f0`.

Final SQ-0006 lifecycle-fixture disposition: APPROVE_PHASE_M_EVIDENCE
