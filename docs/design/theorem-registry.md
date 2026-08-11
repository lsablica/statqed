# Theorem Registry Design

Status: **Experimental candidate; normative identity remains Draft until RFC-0005 acceptance**.

The registry makes formal results discoverable, citable, reviewable, and lockable.

Each public theorem records:

- governed stable ID and semantic version;
- Lean declaration, canonical elaborated proposition bytes, normalizer/environment version, and statement digest;
- maturity, registry-record content lock, and proof-backend/environment lock;
- independently selected registry authorization root/policy and historical/revocation status;
- claim class and randomness scopes;
- quantifier/conditioning profile;
- assumptions and conclusion;
- primary source anchors;
- source, statistical, and formal reviews;
- proof/build lock and actual transitive axiom report;
- non-vacuity models and ablation tests;
- examples and counterexamples;
- predecessor/successor implications or equivalences locked to checked proofs in explicit directions;
- original-source and formalization citations.

Changing a proof body need not change semantic proposition identity in the same locked environment, but it creates a new proof/build lock and axiom report. Changing formal meaning creates a new version and compatibility record. Meaning-bearing reviewed metadata changes expire the affected reviews even when the proposition is unchanged. A fixed-width digest is an integrity/lookup aid under named cryptographic assumptions, not theorem equality or source-fidelity proof.

SQ-0007 implements only `statqed.test-only.foundation.true.v0`. The eleven
layers and their v0 byte/digest domains are specified in
`theorem-registry/spec/registry-v0.md`. Proposition identity deliberately uses
a conservative versioned structural Lean grammar and may overdistinguish
kernel-definitionally equal propositions. The meaning-bearing closure is
kind-specific and smaller than the whole imported environment; complete
toolchain and build inputs remain in the proof/build lock.

Authorization is verifier-selected. Candidate records and transported registry
snapshots are untrusted until their recomputed roots resolve under local current,
historical, forbidden, and revocation policy. Internal consistency never grants
governance authority.

The v0 entry is definitionally trivial, vacuous, Experimental, and test-only.
It carries no public theorem, statistical meaning, source fidelity,
non-vacuity, artifact verification, certificate, logical-data, provenance, or
interpretation claim.
