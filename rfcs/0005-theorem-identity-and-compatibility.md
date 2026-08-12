# RFC-0005: Theorem Identity, Proof Trust, and Compatibility

- Status: Draft
- Author: SQ-0001 manager; completed by SQ-0007
- Reviewers: source, theorem-semantics, formal, conformance, cryptographic, authorization/security, compatibility, CI, integration
- Created: 2026-08-03
- Completed candidate: 2026-08-11
- Task: SQ-0003 and SQ-0007
- Supersedes: none

## Decision boundary

This RFC defines the v0 identity and trust layers needed for one deliberately
vacuous test-only registry record.  It does not define a public statistical
theorem, artifact verification, logical-data identity, or source fidelity.

<!-- SQ-0007-NORMATIVE-SCOPE-BEGIN -->
The v0 theorem-registry decision keeps eleven layers distinct: governed ID and
semantic version; canonical elaborated proposition bytes; a meaning-bearing
environment closure; proposition digest; canonical registry record and digest;
verifier-selected authorization root/policy; proof/build lock; live transitive
axiom observation; directional compatibility-proof lock; and reviewed
annotations. The versioned `statqed.lean-expr.v0` grammar preserves structural
Lean expression and universe constructors, de Bruijn indices, binder
information, names, literals, projections, and argument order; erases metadata,
binder display names, and `letE.nondep`; performs no reduction or unfolding;
and fails closed on unsupported or unscoped terms and finite resource limits.
The versioned environment closure starts from proposition constants and
projection type names, includes declaration-kind-specific meaning-bearing
types and definition/recursor bodies, groups inductive families atomically,
sorts and deduplicates deterministically, and fails closed on missing names,
unexpected cycles, width, depth, and work limits. Proposition and environment
digests remain separate; full semantic identity is the tuple of governed ID,
version, normalizer, proposition digest, and environment digest. Canonical
record, proof/build, authorization snapshot, and compatibility locks use
separate SHA-256 domains through `statqed.digest-lp.v1`. Authorization policy
and permitted/current/historical/forbidden/revoked roots are selected locally
by the verifier; candidate or artifact bytes cannot grant authority. The
proof/build lock separately binds exact Lean/Lake/Mathlib/project material,
the proof subject, same-kernel checks, live axiom observation, and the empty v0
allowed-axiom policy. Compatibility is directional and requires a locked,
kernel-checked `T_new -> T_old`; metadata alone never authorizes substitution.
The only v0 entry is `statqed.test-only.foundation.true.v0` for
`StatQED.Registry.Tests.testOnlyTrue : True`, maturity Experimental and exposure
test-only. It is not a public/statistical theorem, source-fidelity result,
non-vacuity witness, artifact-byte binding, logical-data identity, certificate,
checker-soundness proof, provenance truth, or interpretation approval. Digest
matches are conditional integrity evidence, not mathematical equality,
authorization, truth, provenance, collision-freedom, or statistical validity.
<!-- SQ-0007-NORMATIVE-SCOPE-END -->

## Source-grounded identity relation

Pinned Lean provides several materially different relations: raw structural
`Expr.equal`, alpha-oriented `Expr.eqv`, and kernel definitional equality.
`Level.isEquiv` documents an incomplete normalization-based universe test.  No
one of these is a stable cross-language serialization.

V0 therefore chooses a conservative, project-versioned interface identity. It
may distinguish terms the kernel considers definitionally equal.  That is a
documented compatibility cost, not a claim that raw syntax is complete
mathematical meaning.  Later profiles require a new normalizer identifier and
checked compatibility, never a silent reinterpretation.

The exact semantic grammar and limits are in
`theorem-registry/spec/normalizer-v0.md`.  All accepted `Expr` and `Level`
constructors have a fixed semantic-array form under Accepted
`statqed.cbor-core.v1`.  Free variables, metavariables, loose bound variables,
undeclared universe parameters, unsupported constructors, invalid UTF-8, and
limit violations fail closed.

Binder information is retained as a deliberate interface strengthening even
though the kernel ignores it in definitional equality.  Binder display names,
metadata, and `letE.nondep` are erased.  Literal and projection constructors are
retained.  No beta, delta, iota, zeta, eta, universe algebra, unfolding, or
Unicode normalization occurs.

## Meaning-bearing closure

The closure algorithm is specified in
`theorem-registry/spec/closure-v0.md`.  Proposition constants and projection
type names form the roots.  Definition types and values are meaning-bearing;
theorem, opaque, and axiom types are meaning-bearing while their proof/opaque
bodies are not.  Inductive families, constructors, recursors, projections, and
quotient primitives have explicit kind-specific payloads.

The algorithm does not include unrelated imports, global instance tables,
attributes, source positions, module names, pretty-printer state, theorem
bodies, or opaque bodies.  Selected instances occur as explicit constants
after elaboration.  Inductive families are atomic so ordinary constructor
backedges do not create false cycle failures.  Any remaining active-path cycle,
missing declaration, unsafe declaration, or budget failure is rejected.

This is the smallest closure supported by the retained referenced-definition,
import, instance, missing-dependency, cycle, width, depth, and work mutations.
Complete Mathlib/Lake/project material remains in the proof/build lock.

## Digest domains

All domains use SHA-256 with the Accepted `statqed.digest-lp.v1` frame and
explicit algorithm, profile, object, framing, length, and payload components:

| Layer | Purpose | Object class |
|---|---|---|
| proposition | `statqed.theorem.proposition.v0` | `statqed.lean-proposition.v0` |
| environment | `statqed.theorem.environment.v0` | `statqed.lean-environment-closure.v0` |
| record | `statqed.registry.record.v0` | `statqed.registry-record.v0` |
| proof/build | `statqed.theorem.proof-build.v0` | `statqed.proof-build-lock.v0` |
| authorization snapshot | `statqed.registry.snapshot.v0` | `statqed.registry-snapshot.v0` |
| compatibility | `statqed.theorem.compatibility.v0` | `statqed.compatibility-proof-lock.v0` |

The proposition digest hashes proposition bytes only.  The environment digest
is a separate identity component.  Record and lock dependencies form an acyclic
ordering; no object hashes an ancestor that already contains its digest.

## Registry record and authorization

The closed record distinguishes mechanically extracted fields, governed
metadata, reviewed annotations, authorization state, and proof/build evidence.
The only ID is visibly test-only.  Its source anchor is ADR-0011 and its
original mathematical attribution is `not_applicable` because `True` is
definitionally trivial.

Trusted local policy supplies disjoint current-permitted,
historical-permitted, historical-forbidden, and revoked root sets. Revocation
dominates.  Resolution recomputes the snapshot root, applies the selected local
policy, locates exactly one ID/version, compares canonical record bytes and
digest, then checks proposition, closure, proof lock, axiom report, and any
compatibility lock.  Candidate-provided policy is ignored.  An internally
consistent whole-registry replacement remains unknown or forbidden.

The composed Python resolver performs those canonical-byte and framing
recomputations over the retained record, snapshot, lock, and policy subjects.
The standalone Rust component consumes a deliberately non-normative bounded
transport and compares its separated digest fields with independently supplied
trusted bindings. It does not parse Lean expressions, canonical CBOR, or lock
payloads and is not independent evidence that those bytes were recomputed.

## Proof/build and axiom policy

The proof/build lock binds the exact Lean release/source, Lake, Mathlib commit,
manifest digest, project-source manifest, declaration, canonical proof subject,
semantic identity, live `Lean.collectAxioms` observation, `--trust=0` result,
same-kernel fresh replay, and trust policy.

`collectAxioms` uses imported extension data and silently contributes nothing
for an unknown declaration.  V0 first requires declaration presence and
cross-checks the explicit environment closure.  Fresh `leanchecker` replay is
same-kernel corruption evidence, not an external verifier, and its unsafe/
partial exclusions are separately rejected.

The v0 allowed imported-axiom set is empty. `sorry`, `admit`, `sorryAx`, project
axioms, bodyless assumptions, unsafe/partial declarations, and native/compiler
trust shortcuts are prohibited.  A proof refactor can preserve proposition and
environment identity but changes the proof/build lock when proof material
changes.

## Directional compatibility

Direct substitution requires identical canonical proposition bytes and
environment digest. Otherwise the verifier requires a locally authorized lock
for a kernel-checked implication in the useful direction `T_new -> T_old`,
including complete propositions and explicit universe instantiations. V0 does
not infer term mappings, peel premises, chain edges, or accept equivalence/
implication metadata. Compatibility permits disclosed substitution only; it
does not merge identities or transfer semantic, source, maturity, or
interpretation review.

The only v0 compatibility fixture is the vacuous test-only implication
`False -> True`. It demonstrates lock construction, direction checking, axiom
observation, and substitution-rejection plumbing; it is not evidence of a
nontrivial theorem migration or a public compatibility relation.

## Stable failures and resources

V0 publishes deterministic `registry.*` classes for malformed/version,
normalization/unsupported expression, cycle/width/depth/work/missing closure,
proposition/environment/digest/record/root/policy/proof mismatches, unknown/
revoked/forbidden roots, forbidden axioms, compatibility missing/direction,
resource, and operational failures.  Diagnostic text is bounded and contains
no host paths, locale text, timestamps, random identifiers, or dependency debug
strings.

The exact limits are recorded in the registry specification and tested at the
maximum and one over it: 1 MiB input/object, 2 MiB output, 16 parser fixture
entries (one published), expression depth 256/nodes 65,536, level depth 64,
closure width 256/units 1,024/depth 64/work 1,000,000, 128-byte identifiers,
256 axioms, 32 compatibility edges/path length one, and 4 KiB diagnostics.

## Evidence and implementation independence

The primary extractor reads the live pinned Lean environment and emits typed
expressions, kind-specific closure, proof subjects, and axiom observations.  A
separate standard-library Python oracle independently implements the expression
grammar, environment-closure walk/canonicalization, CBOR encoder, and six digest frames without importing the primary
normalizer, Rust resolver, or SQ-0005 oracle.  A standalone std-only Rust
workspace performs bounded offline binding resolution under verifier-selected
policy; it is not a second canonical-byte parser.

Agreement is evidence, not authority.  Deliberately wrong encoders, closure
walks, record/root selection, proof/axiom checks, and compatibility direction
are detected.  Permanent content-addressed evidence binds sources, specs,
implementations, locks, fixtures, retained failures, supply-chain observations,
reviews, and decision status.

## Alternatives rejected

- theorem name or semantic-version range only;
- pretty-printed text, Lean `repr`, cached hashes, or `.olean` bytes;
- full repository/import hash as semantic identity;
- proof-body hash as semantic identity;
- imported `collectAxioms` data or fresh replay as independent verification;
- artifact-supplied roots or internally consistent replacement registries;
- metadata-only compatibility;
- one digest reused across logical domains;
- silent expansion to public statistical theorems.

## Compatibility and migration

Any grammar, closure, record, authorization, lock, axiom-policy, resource, or
error-semantic change requires a new version.  Proof refactors may preserve
semantic identity but create new proof/build locks.  Meaning changes create new
theorem versions.  A checked implication supports disclosed migration without
making identities equal.  RFC-0007 retains ownership of broader migration
policy.

## Validation disposition

Every original validation item has a retained positive, negative, mutation, or
explicitly scoped exclusion.  The `True` entry is intentionally vacuous and
cannot validate statistical theorem content.  Acceptance remains contingent on
the exact-subject source, semantic, formal, conformance, cryptographic,
authorization/security, compatibility, CI, and integration dispositions in the
SQ-0007 review record.

## Decision

Draft pending those exact-subject independent dispositions and hosted CI.  Once
they all approve the identical candidate, this line and the header may change
to Accepted without changing the marked normative scope.
