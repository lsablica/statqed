# Test-only theorem registry and lock v0

Status: Experimental candidate for RFC-0005.

## Separated layers

The v0 design keeps separate: (1) governed ID/version, (2) canonical
proposition, (3) meaning-bearing environment closure, (4) proposition digest,
(5) canonical registry record, (6) record digest, (7) verifier-selected
authorization root and policy, (8) proof/build lock, (9) live axiom report,
(10) compatibility proof lock, and (11) reviewed annotations.  No digest is a
synonym for all eleven.

## Only v0 record

The only entry is `statqed.test-only.foundation.true.v0`, version `0.0.1`, for
`StatQED.Registry.Tests.testOnlyTrue : True`.  The source anchor is ADR-0011.
Original mathematical attribution is `not_applicable` because the proposition
is definitionally trivial and intentionally test-only.

The canonical record is a closed ordered semantic array containing:

1. `statqed.registry-record.v0`;
2. governed ID and semantic version;
3. exact Lean declaration name and kind;
4. normalizer and closure identifiers;
5. proposition and environment digests;
6. proof/build-lock digest and axiom-report digest;
7. maturity `Experimental` and exposure `test_only`;
8. reviewed source anchor, attribution rationale, limitations and nonclaims.

Mechanically extracted fields, governed metadata, reviewed annotations,
authorization state, and proof/build evidence remain distinct in source files
even though the closed record binds their reviewed values.

## Digest framing

All domains use SHA-256 and Accepted `statqed.digest-lp.v1` framing:

| Purpose | Object class |
|---|---|
| `statqed.theorem.proposition.v0` | `statqed.lean-proposition.v0` |
| `statqed.theorem.environment.v0` | `statqed.lean-environment-closure.v0` |
| `statqed.registry.record.v0` | `statqed.registry-record.v0` |
| `statqed.theorem.proof-build.v0` | `statqed.proof-build-lock.v0` |
| `statqed.registry.snapshot.v0` | `statqed.registry-snapshot.v0` |
| `statqed.theorem.compatibility.v0` | `statqed.compatibility-proof-lock.v0` |

Every frame binds purpose, algorithm, profile, object class, framing version,
component lengths and payload.  Cross-domain replay, reordered/truncated
fields, identifier downgrade, and unsupported fallback are rejected.

## Authorization

The verifier receives `statqed.registry-authorization.v0` policy independently
of candidate bytes.  Disjoint local sets classify current permitted,
historical permitted, historical forbidden, revoked, and unknown snapshot
roots; revocation dominates.  The candidate cannot select policy or add a
root. Resolution recomputes the snapshot root, applies local policy, locates
exactly one ID/version, compares the full closed record against the
verifier-selected `record_binding` and `record_digest`, then checks proposition,
closure, proof lock, axiom report and any compatibility lock.
An internally consistent replacement registry remains unauthorized.
The composed Python verifier performs these canonical-byte and framing
recomputations over the retained subjects. The standalone Rust operational
resolver compares the separated results with exact verifier-selected bindings;
it intentionally does not parse canonical CBOR or Lean/lock payloads and is not
an independent canonical-byte oracle.

## Proof/build lock and axioms

`statqed.proof-build-lock.v0` binds the exact Lean release/source, Lake,
Mathlib revision, manifest digest, project-source manifest, declaration and
canonical proof subject, semantic identities, live `Lean.collectAxioms`
observation, `--trust=0` build/check result, and trust-policy version.  The v0
allowed imported-axiom set is empty.  `sorryAx`, project axioms, bodyless
assumptions, unsafe/partial declarations, and native/compiler trust shortcuts
are forbidden.  `collectAxioms` is an environment observation, not an external
kernel verifier; its unknown-constant behavior and extension dependence are
recorded in the source audit.

A proof-only refactor can preserve proposition/environment identity, but must
change the proof/build lock whenever its canonical proof subject changes.

## Directional compatibility

Direct substitution requires byte-identical proposition bytes and environment
digest.  Otherwise a locally authorized compatibility lock must bind a
kernel-checked declaration with exact normalized type `T_new -> T_old`, where
the new theorem replaces an old requirement. The lock separately binds both
proposition digests, the exact compatibility-declaration environment digest,
the canonical proof subject, its proof/build-lock digest, and the actual live
axiom-report digest. Reversed direction, metadata-only implication/equivalence,
changed assumptions or referenced definitions, environment mismatch, missing
proofs/locks, and substituted proof locks are rejected. Compatibility does not
merge identities or transfer review annotations.

The retained `False -> True` fixture is intentionally vacuous and test-only;
it exercises directional proof-lock plumbing and makes no nontrivial migration
claim.

## Stable failure classes and resources

Stable errors include every `registry.*` code in the SQ-0007 contract plus the
more specific `registry.expression_unsupported`,
`registry.closure_width_limit`, `registry.closure_depth_limit`,
`registry.closure_work_budget_limit`, and
`registry.authorization_root_historical_forbidden` classes.  They cover
malformed/version, normalization/expression, closure cycle/width/depth/work,
missing dependency, proposition/environment/digest/record/root/policy/proof
mismatches, forbidden axiom, compatibility missing/direction, resource and
operational failures. Deterministic precedence is resource,
syntax/schema, version, normalization, closure, proposition/environment,
digests, authorization, proof/axiom, compatibility, operational.

Limits are: input and individual canonical objects 1 MiB, output 2 MiB,
published entries exactly one, parser fixture entries 16, compatibility edges
32/path length one, expression depth 256/nodes 65,536, closure width 256/units
1,024/depth 64/work 1,000,000, identifier 128 ASCII bytes, axiom entries 256,
and diagnostics 4 KiB. Maximum and one-over cases are tested. The 1,000,000
closure-work cap is an outer safety cap dominated by the v0 expression/unit/
width limits; its exact predicate is tested while traversal accounting is
tested at a reachable required-work/one-under boundary.

## Nonclaims

The record is vacuous, test-only and Experimental.  It is not a public or
statistical theorem, source-fidelity claim, non-vacuity witness, artifact-byte
binding, logical-data identity, certificate, checker-soundness proof,
provenance truth, or interpretation approval.  Hash agreement is conditional
integrity evidence; it is not mathematical equality, authorization, truth, or
collision-freedom.
