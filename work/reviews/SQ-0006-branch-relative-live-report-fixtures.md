# SQ-0006 branch-relative live-report fixture binding review

Status: IN_REVIEW — exact-head hosted and integration dispositions pending

The expectation and focused regression files are in the unowned
`lean_remainder` partition protected by SQ-0006 v3. Its reviewed live baseline
therefore moves from 66 files / digest
`685c9a62b4f7b27a96a1a12b0566321d26c349ff3d018cde6433b1591e5578e7`
to 67 files / digest
`5fe397a8b53bfb2488f8dd81e9d7d0d8896c65f754ae8a280db5a8f2125ff184`.
The exact tuple is duplicated in the fail-closed checker; manifest-only
regeneration is rejected. Evidence identifiers remain v3 because ownership
and lifecycle semantics do not change.

| Subject | Before SHA-256 | Candidate SHA-256 |
|---|---|---|
| `conformance/schema-v0/evidence/evidence-spec.json` | `271a8d205be6247f3c89f8d76310144ead33f94a526feffd429aac94c496b1d2` | `2323d77227ba5d8b1ef618aa7f0c38201a2e462471ec5a2f80e9673914a1abc8` |
| `conformance/schema-v0/evidence/evidence-manifest.json` | `22dc468e115470be62db55c0b6beffd3e10770030768bc88e380b177adf0fb0b` | `3a5c97ab4aea0f8c3eb8c0f5ac9f3d30d7f04f22898b7ecefd8e64321f103a40` |
| `scripts/schema/check_schema_v0.py` | `540091772ca57322f490c492234c17b892f84b9c13947f4d75d144148613d2ae` | `e0fc5d627389cb8c1c869dee956efb7dd46765f365821de580617e3a218e788b` |

The historical scientific digest remains
`4bfd5fad7f9884d592d5c8c320dbd4efd735c990f3b23d6b3cb5d8e9854df5f0`.
The 49 v1 completion evidence subjects, including the immutable 44-subject
scientific subset, five positive fixtures, 85 negative fixtures, three
deliberate mutations, schema sources, CDDL, goldens, and semantics are
unchanged. This is a live maintenance baseline rebind, not a schema change.
RFC-0006 remains byte-identical, Draft, and owned by SQ-0027.
