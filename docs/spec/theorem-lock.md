# Theorem Lock Specification

A theorem lock identifies the exact formal meaning used by an artifact.

Required fields:

- proof backend and version;
- Mathlib/project commit or content lock;
- theorem ID/version;
- Lean declaration;
- normalized statement hash;
- required method-pack version/content hash;
- checker declaration/hash;
- accepted axiom baseline;
- compatibility/migration references.

A resolver may not substitute a theorem merely because its name matches. Replacement requires identical statement hash or a registered implication/equivalence path whose direction supports the claim.
