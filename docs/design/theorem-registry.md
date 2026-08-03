# Theorem Registry Design

Status: **Draft; theorem identity blocked on RFC-0005**.

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
