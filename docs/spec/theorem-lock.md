# Theorem Lock Specification

Status: **Experimental v0 candidate; normative use blocked until RFC-0005 acceptance**.

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

## V0 lock ordering

The nonrecursive dependency order is:

1. canonical proposition and environment closure;
2. proof/build lock and live axiom observation;
3. canonical registry record;
4. authorization snapshot/root;
5. optional compatibility lock over endpoint identities and its own proof/build evidence.

The six digest purposes are distinct and listed in RFC-0005. The proposition
digest does not silently include the environment. Full semantic identity is
the governed ID/version, normalizer, proposition digest, and environment
digest tuple.

V0 direct substitution requires identical proposition bytes and environment
digest. Otherwise the only supported compatibility edge is a locked,
kernel-checked `T_new -> T_old`, where new material substitutes for the old
requirement. The reverse implication and metadata-only labels are rejected.

The test-only `True` lock is not an artifact-level theorem lock and cannot be
used to claim that arbitrary artifact bytes reconstruct or prove a Lean
proposition.
