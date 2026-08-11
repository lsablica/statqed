# SQ-0006 Successor-Lifecycle Review

## Subject and boundary

This supplemental maintenance review preserves the historical SQ-0006
scientific review in `work/reviews/SQ-0006.md`. It reviews only the evidence
lifecycle and path-ownership correction based on post-merge main
`718216d3ecd0022593b12925c6e0173a87e6d522`.

- Original SQ-0006 normal merge:
  `e4bd2f0e739aaf480170d16a3424b40af1e9cf5b`.
- SQ-0006 post-merge record:
  `718216d3ecd0022593b12925c6e0173a87e6d522`.
- Original evidence-manifest SHA-256:
  `eefe309c3ab16d05321e5071698009b716721b8c1119c7c48bf4fa37d60521eb`.
- Unchanged historical scientific-subject digest:
  `4bfd5fad7f9884d592d5c8c320dbd4efd735c990f3b23d6b3cb5d8e9854df5f0`.
- Unchanged RFC-0006 SHA-256:
  `e834f805cc38fca2185433c72df4ac7db856c0ae20037fedcb57329a740b3429`.

No schema, fixture, golden, conformance result, prototype, production Rust,
production Lean, frontend, RFC, ADR, or successor-contract content changed.
No successor was claimed.

## Defect reproduction and correction

The v1 live verifier compared successor non-status contract projections with
their values at SQ-0006 completion. That made reviewed planning evolution fail
as though it changed SQ-0006 science. It also gated whole `lean/`, `backend/`,
and `frontends/` trees by one owner's lifecycle, rejecting legitimate changes
to independently owned subtrees.

Evidence spec `statqed.sq0006-evidence-spec.v2` and manifest
`statqed.sq0006-evidence.v2` now separate:

- a complete, canonically authenticated nested v1 completion manifest;
- immutable scientific subjects derived directly from that historical
  manifest rather than from a mutable replacement list;
- exact historical full-file and non-status hashes for all six successors;
- live contract/backlog/status and repository-ledger consistency;
- checker-constant-bound legal and authorizing lifecycle states; and
- checker-constant-bound static path partitions, owners, baseline hashes, and
  baseline file counts.

Future reviewed successor planning prose is not compared with the historical
contract values. SQ-0006 remains required to be DONE, and contract/backlog/
ledger disagreement, illegal states, noncanonical ledger order, decision
drift, scientific drift, and unauthorized protected-path drift still fail.

The static ownership policy does not trust mutable successor `allowed_paths`.
It permits only the Registry subtrees for active SQ-0007, Assurance/Guarantee
for active SQ-0008, backend broadly for active SQ-0011, and the corresponding
language frontend for active SQ-0013/SQ-0014/SQ-0015. Unowned remainders and
`schemas/prototypes/**` remain frozen. Symlinks and special files fail before
cache exclusions; ignored cache files are accepted only in a live Git checkout
where Git confirms they are untracked. Tracked-only temporary simulations
cannot silently add ignored content.

## Exact candidate hashes

- evidence spec:
  `76255b647a18df29ee690bd6bcd537646e6bd225820a3047d78276e9a9f01e30`;
- evidence manifest:
  `5c6b3081846ba8ec2bc1ac17bf7d9014ee4d8f2dedb9e7d625a1226d2957b752`;
- verifier:
  `70faef49b95bbe18d235c342a190f655370e5e53952cbb16f16f9a7a4e40b1f0`;
- manifest generator:
  `8453ec6730b328ab1677bee00f2d754a7f57bf340a9cabc0e8fc2c7e0badc4ae`;
- regression suite:
  `7c35930fb972286fb9ccf447749be875d6269b26b66a87ccb4c2085580cd622b`;
- manager launch contract:
  `af1756a4280001d6d1867584d83f6ed053d4db7ea9f72f3332b4346fbaf1eaea`;
- active plan:
  `c4d5b07825dca2a36966d6ae6b30f9ed065ef4a51678b7b2c69fa468be756ed5`.

The v2 manifest contains 49 live subjects and derives 44 byte-identical
immutable scientific subjects from the complete nested v1 history. The nested
historical manifest remains exactly
`eefe309c3ab16d05321e5071698009b716721b8c1119c7c48bf4fa37d60521eb`.

## Historical successor bindings

All six contracts remained byte-identical throughout this maintenance:

- SQ-0007: `bddf4334bbef4391b6024010f6073bcec34c272d9e15809f54d6ee927de5c4e2`;
- SQ-0008: `8ca1d8f0a50abc6d081cd2b3b73456a334f6ac43a2572576b6b452553ec8d471`;
- SQ-0011: `a6dd037dc74e81c681161b79ac324fae8093bef5f8449a0322d93f45962a7b12`;
- SQ-0013: `8132e0887c5d5765b608944761946a046ee4ea2597e1e7eb90eea825780e9290`;
- SQ-0014: `0faa9eac82339efb08d55e8cc633de29988366dfb599dd9f968e92d24c38468b`;
- SQ-0015: `c17d1c85574980ead5a7224f213d3277d14e3c21e3145d1c74ef76ba4624227b`.

These values remain historical completion evidence. They are not live
successor-planning requirements.

## Tests and retained evidence

The 22 pre-maintenance schema tests remain, and 29 named Phase-A regressions
were added, for 51 schema tests total. The regressions cover all six READY
contract expansions without regeneration, historical-binding preservation,
SQ-0006 regression, lifecycle disagreement and illegality, baseline/status
policy redefinition after manifest rebinding, RFC/ADR/schema/prototype/golden
drift, path-owner activation and isolation, overlapping Registry ownership,
broad SQ-0011 ownership, canonical ledger order, ignored-cache symlink/special/
unverifiable-file rejection, and frozen remainders.

Local gates passed:

- `make check` and `make list-work`;
- `git diff --check`;
- SQ-0005 evidence verification and 273-case conformance with 69 joint
  goldens and 20 detected deliberate divergences;
- SQ-0006 static verification and dynamic schema verification with five
  positives, 85 negatives, and three detected deliberate mutations;
- 51 schema tests and 59 predecessor evidence/lifecycle tests; and
- byte-identical v2 manifest regeneration.

The ledger remained DONE=6, READY=6, ACTIVE=none, BLOCKED=48. RFC-0001 and
ADR-0004 remain Accepted with matching marked scope; RFC-0006 remains Draft
under SQ-0027.

## Independent dispositions

- Evidence-lifecycle review: `APPROVE_EVIDENCE_LIFECYCLE` by the distinct
  lifecycle-model reviewer, bound to the seven candidate hashes above. The
  reviewer independently confirmed the complete v1 embedding, exact 44-entry
  historical/current equality, hard-bound policies, unchanged contracts and
  RFC-0006, 51 schema tests, 59 predecessor tests, and unchanged ledger.
- Path-ownership/security review: `APPROVE_PATH_OWNERSHIP` by the distinct
  path-security reviewer, bound to the same candidate. The reviewer reproduced
  and then confirmed closure of ignored-path symlink/special handling,
  overlapping Registry ownership, broad SQ-0011 ownership, canonical ledger
  ordering, static baseline binding, and all 15 required path simulations.
- Adversarial regression review: `APPROVE_PHASE_A_ADVERSARIAL` by the distinct
  adversarial reviewer, bound to the same technical candidate. The reviewer
  independently reproduced the former READY-authorization, baseline-
  redefinition, and unsorted-ledger bypasses, confirmed each now fails for its
  intended reason after manifest rebinding, and verified the tracked-only
  `.codex/` boundary plus all local evidence/conformance gates.
- Integration review: `APPROVE_PHASE_A_INTEGRATION` by the distinct
  integrator after all three specialist approvals. The integrator verified the
  exact seven tracked-file changes plus this supplemental record, all frozen
  hashes and task/RFC boundaries, all local gates, and an isolated committed
  candidate whose manifest regenerated byte-identically and whose worktree
  remained clean. Hosted exact-head and post-merge checks remain separate.

Final local disposition: `APPROVE_PHASE_A_INTEGRATION`; protected exact-head
CI and main reproduction remain mandatory merge gates.
