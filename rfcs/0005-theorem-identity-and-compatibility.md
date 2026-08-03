# RFC-0005: Theorem Identity, Proof Trust, and Compatibility

- Status: Draft
- Author: SQ-0001 manager
- Reviewers: formal-methods reviewer, statistical architect, interoperability reviewer, security reviewer, counterexample reviewer
- Created: 2026-08-03
- Task: SQ-0003 and SQ-0007
- Supersedes: none

## Decision boundary

Define theorem semantic identity, statement normalization, environment/dependency locks, registry-record binding, proof/build locks, transitive axiom reports, and directional compatibility. Decide what may remain stable across proof refactors and what an artifact must pin.

## Motivation

A digest of surface theorem text is not exact formal meaning. Referenced definitions, elaboration, imports, axioms, or normalization rules can change while printed text remains the same. A proof-body refactor can preserve the proposition while introducing an unacceptable axiom. Registry metadata can also drift from the formal declaration.

## Terminology and source background

- **Semantic theorem identity:** governed theorem ID plus version, canonical elaborated proposition bytes, normalization-algorithm version, and locked meaning-bearing environment.
- **Statement digest:** a collision-resistant lookup/integrity value computed over those canonical bytes and context; not proof of equality by itself.
- **Proof/build lock:** proof source or artifact, toolchain/environment, and actual transitive axiom report used for one checked build.
- **Registry record:** the canonical meaning-bearing theorem metadata plus reviewed annotations, itself content-bound.
- **Registry authorization root:** an independently selected verifier-policy input naming an accepted registry snapshot/root, policy version, and historical/revocation rules. Record integrity does not confer governed ID, review, maturity, or compatibility authority.
- **Compatibility theorem:** a kernel-checked proposition relating complete old and new propositions in an explicitly useful direction.

Exact Lean normalization and environment-lock mechanics require the pinned toolchain and prototypes in SQ-0003/SQ-0007.

## Examples and nonexamples

Examples:

- A proof refactor under the same canonical proposition/environment preserves the semantic theorem version but creates a new proof/build lock and axiom report.
- Replacing a locked old theorem `T_old` with `T_new` for verification of the old claim requires a checked implication `T_new → T_old`, including all assumptions and instantiation mappings.
- Claim class and source-fidelity annotations may be reviewed metadata even when they cannot be mechanically extracted; their changes expire those reviews.

Nonexamples:

- Equal theorem names or equal pretty-printed text imply equal meaning.
- Equal fixed-width digests prove theorem equality or collision-freedom.
- A registry row saying `implies` authorizes substitution without a locked proof.
- An artifact-supplied, internally consistent replacement registry inherits a governed theorem ID or review status without resolving against the verifier-selected authorization root.
- An unchanged statement digest permits a proof body containing `sorryAx`, `admit`, a project-defined axiom, or an unreviewed native/unsafe shortcut.
- A statement hash validates source fidelity, claim classification, or the truth of external premises.

## Alternatives

### Name and semantic-version range only

Rejected. Names and semver do not bind formal meaning.

### Hash pretty-printed source text only

Rejected. Formatting/elaboration instability and dependency drift make it insufficient.

### Hash the complete repository or proof body as theorem identity

Rejected as semantic identity because harmless proof refactors would create new theorem meanings. A separate proof/build lock is still required.

### Defer the exact normalizer and lock closure

Accepted for SQ-0001. Their selection requires pinned Lean/Mathlib prototypes and independent vectors; SQ-0007 cannot freeze a registry format before resolving them.

## Proposed semantics

1. A public theorem has a governed stable ID and explicit semantic version.
2. Identity binds canonical elaborated proposition bytes, normalizer version, and the meaning-bearing dependency environment. The statement digest is a lookup/integrity key over that material, subject to named cryptographic assumptions.
3. Proof bodies are not part of semantic proposition identity, but every accepted build has a separate proof/build lock and actual transitive axiom report.
4. The trusted-path policy rejects `sorryAx`, `admit`, project-defined axioms, and unreviewed unsafe/native trust shortcuts. The exact allowed kernel/Mathlib axiom baseline is versioned after SQ-0003 reports it; it is never a license to add project axioms.
5. Kernel acceptance is reported as derivability of the exact proposition relative to the named environment and axiom set, not unconditional truth or source fidelity.
6. The canonical registry record is content-bound. Mechanically extracted fields and reviewed annotations are distinguished.
7. Verification policy independently selects an accepted registry snapshot/root and policy version. Artifact-supplied records remain untrusted unless they resolve against that root. The result records the root/policy, resolution, historical/revocation status, and nonclaims.
8. Any change to meaning-bearing annotations, assumptions, randomness/quantifier profiles, or source mappings expires the relevant semantic/source review even when formal proposition bytes are unchanged.
9. Compatibility or replacement requires identical canonical proposition bytes in the same locked environment or a kernel-checked compatibility theorem over complete propositions in the required direction. Metadata alone is insufficient.

## Formal and implementation consequences

- SQ-0003 must produce an actual axiom report and propose the versioned baseline before any trusted-path claim.
- SQ-0007 must specify canonical elaboration/normalization, bounded dependency closure, registry-record canonical bytes, verifier-selected registry authorization root/policy, statement digest, proof/build lock, revocation/historical behavior, and compatibility-proof lock.
- Artifacts pin the exact registry record and proof/environment material required by their verification mode.
- The theorem resolver never performs natural-language, name-only, semver-only, or metadata-only substitution.

## Trust, security, privacy, and accessibility

Threats include whole-registry replacement, forged ID/review/maturity metadata, root mismatch, revoked/historical roots, digest collision/substitution, environment drift, forged compatibility metadata, hidden axioms, source-review drift, closure cycles, and denial of service from unbounded width/depth. Locks and registry resolution must be deterministic, bounded, offline-resolvable, and rendered with human-readable theorem IDs, root/policy/status, assumptions, axiom status, and nonclaims.

## Compatibility and migration

Proof refactors can preserve semantic versions only when proposition/environment identity is preserved, but they create new proof/build locks. Meaning changes create new theorem versions. A directional implication can support a disclosed migration but does not make old and new theorem identities equal.

## Validation plan

- two independent normalization/hash implementations or a documented independent oracle;
- fixtures changing a referenced definition, import environment, implicit argument, universe parameter, and typeclass instance;
- proof-body mutation introducing a forbidden axiom without changing the proposition;
- forged and wrong-direction compatibility records;
- whole-registry replacement, forged governance metadata, root mismatch, revoked/historical roots, closure cycles, and deterministic width/depth/work-budget failures;
- collision-assumption and canonical-byte reporting;
- source, statistical, formal, interoperability, security, adversarial, and integration review.

## Objections and resolution

- **Objection:** Full dependency locking is expensive. **Resolution:** SQ-0007 must prototype the smallest closure that preserves meaning; cost cannot justify name/hash-only substitution.
- **Objection:** A trusted registry administrator can mark compatibility. **Resolution:** governance approval may publish metadata, but deductive substitution still requires checked evidence.
- **Objection:** Proof bodies should be irrelevant. **Resolution:** they are irrelevant to proposition identity but material to the axiom/trust report for a checked build.

## Decision

Draft. The constitutional separations and prohibitions above are proposed; the exact normalizer, bounded dependency/environment closure, registry canonical record, verifier-selected authorization root/policy, historical/revocation rules, digest profile, and axiom baseline remain blocking deliverables for SQ-0003/SQ-0007. ADR-0007 must remain Proposed until this RFC is Accepted.
