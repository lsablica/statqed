# Theorem Lock Specification

Status: **Draft; identity and compatibility blocked on RFC-0005**.

A theorem lock is intended to identify the exact formal meaning and checked build used by an artifact. A name or statement digest alone is insufficient.

Required fields:

- proof backend and version;
- Mathlib/project commit or content lock;
- governed theorem ID/semantic version, canonical registry-record content lock, and independently selected accepted registry snapshot/root plus policy version;
- Lean declaration;
- canonical elaborated proposition bytes, normalizer version, meaning-bearing dependency/environment lock, and statement digest;
- required method-pack version/content hash;
- checker declaration/hash;
- proof/build lock and actual transitive axiom report under a versioned policy that never permits `sorryAx`, `admit`, or project-defined axioms;
- registry resolution result and historical/revocation status;
- compatibility theorem/proof lock, direction, instantiation mapping, and migration references.

A resolver may not substitute a theorem merely because its name, pretty-printed text, or digest matches. An artifact-supplied record has no governed authority until it resolves against the verifier-selected registry root/policy. Replacement requires equality of canonical proposition bytes in the same locked environment or a mode-appropriate checked implication/equivalence proof over the complete propositions whose direction supports the requested claim. Registry metadata alone never authorizes substitution. The resolution/root/status and any compatibility path are recorded in the new verification result.
