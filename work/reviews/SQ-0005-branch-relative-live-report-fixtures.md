# SQ-0005 branch-relative live-report fixture binding review

Status: IN_REVIEW — exact-head hosted and integration dispositions pending

The SQ-0005 v3 evidence policy and verifier are byte-identical. Because its
ownerless Lean-remainder baseline protects future trust infrastructure, the
manifest generator now applies a minimal content-addressed overlay for exactly
the changed expectation file and its focused regression file. Overlay hashes
are literal reviewed values; generation rejects missing, symlinked, or
different current bytes. A corruption regression proves arbitrary current-tree
drift cannot be absorbed. The historical v3 baseline at
`e6e6fcf5a4dc58037be506b67eb25deee9298979` remains the source for every
other protected path.

| Subject | Before SHA-256 | Candidate SHA-256 |
|---|---|---|
| `conformance/prototypes/evidence/evidence-manifest.json` | `bb5ec8f4b1e30dbe7be9f6f26787d6e231aeac4c207dd6215147b513f1384812` | `22b771b5aa71a72fe3979e9dd29ff8a5ae0b8e082bd0b971036baa0d554a4a7a` |
| `scripts/serialization/build_evidence_manifest.py` | `5c8389c38b5a993289a10532dbf3466bc393b984258e427284ca1658e21f4cd4` | `b9d140e80e363f59c62f59aec575902456de55089751079b3e0992c4ff244c94` |
| `conformance/prototypes/evidence/evidence-spec.json` | `39fd75ffb754a7f9f7a5a3dafb3653973e65af2f944ae782c6e70e29db3c54b4` | unchanged |

All 273 serialization cases, 69 joint goldens, and 20 deliberate divergences
remain scientific/profile evidence. The overlay is maintenance infrastructure,
not a scientific subject. RFC-0001, ADR-0004, and RFC-0006 are unchanged.
This record supplements, and does not rewrite, the original and lifecycle
reviews.
