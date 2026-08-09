# Quality Dashboard

Status: **Draft**.

| Area | Draft | Experimental | Candidate | Stable |
|---|---:|---:|---:|---:|
| Lean proof foundation | 0 | 1 | 0 | 0 |
| Rust reference foundation | 0 | 1 | 0 | 0 |
| Deterministic encoding profile | 0 | 1 | 0 | 0 |
| Core ontology | 1 | 0 | 0 | 0 |
| IR/artifact schemas | 1 | 0 | 0 | 0 |
| Public statistical theorems | 0 | 0 | 0 | 0 |
| Sound certificate checkers | 0 | 0 | 0 | 0 |
| Complete method packs | 0 | 0 | 0 | 0 |
| Frontend conformance paths | 0 | 0 | 0 | 0 |
| Verified end-to-end artifacts | 0 | 0 | 0 | 0 |

Current evidence: SQ-0001 independently reviewed and accepted eight high-level
constitutional ADRs while retaining three Proposed ADRs and nine Draft RFC
blockers; see `work/reviews/SQ-0001.md`. SQ-0003 adds one Experimental Lean
proof foundation: an exact Lean/Mathlib lock, minimal test-only project, actual
axiom observations, trust mutations, normal/source builds, and hosted CI.
SQ-0004 adds one Experimental Rust reference foundation: an exact development
pin and offline compatibility floor, dependency-free two-crate workspace,
reproducible lock, bounded deterministic bootstrap CLI behavior, trust
mutations, point-in-time license/advisory evidence, and hosted CI. Neither
foundation is Candidate or Stable. SQ-0005 adds one Experimental deterministic
encoding profile: a bounded data-free semantic subset, strict RFC 8949 core
deterministic bytes, two independently originated prototypes, 273 semantic-first
cases, 69 retained joint goldens, 20 detected deliberate divergences, generic
data-free digest framing, source/security reviews, and permanent static evidence
verification. It is not a production canonicalizer or artifact verifier and
does not define logical-data identity. These foundations add no ontology
interface, schema v0, public statistical theorem, sound certificate checker,
method pack, frontend conformance path, or end-to-end artifact. No statistical
analysis is currently verified by this repository.
