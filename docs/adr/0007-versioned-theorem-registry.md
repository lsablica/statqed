# ADR-0007: Versioned theorem registry and statement locks

- Status: Proposed
- Blocking RFC/task: RFC-0005 / SQ-0007
- Decision owner: SQ-0007

## Context

Theorem names, pretty-printed statements, or one undifferentiated hash cannot
identify formal meaning, proof trust, governed authorization, and compatibility
across environments.

## Candidate decision

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

## Consequences

Proof-only refactors can preserve semantic identity but create new proof/build
locks.  Meaning changes require a new theorem version.  The verifier, never an
artifact, selects authorization state.  Compatibility is useful-direction
kernel evidence, not metadata.

The only v0 record is Experimental, visibly test-only, and intentionally
vacuous.  It establishes registry plumbing, not a public theorem or artifact
verification.

## Alternatives rejected

Name-only, semver-only, pretty-print-only, one-digest-for-all, complete-import
hashing as semantic identity, proof-body-as-meaning, artifact-selected roots,
and metadata-only compatibility are rejected.

## Validation and evidence

RFC-0005 and the SQ-0007 content-addressed evidence define exact grammar,
closure, frames, locks, authorization policy, resources, errors, independent
observations, hostile mutations, supply-chain state, and trust nonclaims.

## Review

This ADR remains Proposed until RFC-0005 receives exact-subject independent
approval.  If accepted, only the status/disposition prose changes; the marked
scope must remain byte-identical to the Accepted RFC scope.
