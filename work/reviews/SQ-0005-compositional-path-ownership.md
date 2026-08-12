# SQ-0005 compositional path-ownership maintenance review

Status: IN_REVIEW

This supplemental record reviews only the v3 live path-ownership policy for
the permanent SQ-0005 evidence verifier. It does not replace or rewrite the
scientific review in `work/reviews/SQ-0005.md` or the v2 lifecycle review in
`work/reviews/SQ-0005-evidence-lifecycle.md`.

## Historical preservation

The accepted serialization profile, semantic value model, fixture catalogue,
goldens, retained results and failures, implementation lineage, RFC-0001,
ADR-0004, and RFC-0006 bytes are unchanged. The v3 policy retains:

- the v1 completion manifest SHA-256
  `0512a79a42cc6c6b70e5c139044841827b3ac3103968892fe6f135f02436a233`;
- the v1 subject-map SHA-256
  `59aa64011c7afea1ed923a50479f151999cfcd16f7fa125114f6558c9a2b9105`;
- the v2 lifecycle manifest SHA-256
  `1259049334d6413e9a84e13592bec1eba3bc0a6e36607c2f4a2c96f71a894845`;
- the v2 historical protected-file snapshot SHA-256
  `75f1b0f6266791e55777a87530c7f46c62a89b932e81196b27877eec93f0a7fb`;
- the original review SHA-256
  `a45c57c5abf9d99b89a5c5b86143da34651728a86b3b72d8ca7d5886a62f3ff7`;
  and
- the v2 lifecycle review SHA-256
  `ae2753b4b74c6c297bfe75556d940579f16696565821ffdae0d9cda9f3b746ba`.

The v1 and v2 values remain historical evidence. They are not regenerated to
match a successor's live implementation tree.

## Live policy reviewed

The static v3 policy partitions the historically protected `lean/`,
`backend/`, and `frontends/` trees by reviewed owner. Only IN_PROGRESS,
IN_REVIEW, and DONE authorize an owner partition. READY and BLOCKED do not.
Registry paths are owned by SQ-0007 (and, for the standalone backend subtree,
also SQ-0011); Assurance and Guarantee by SQ-0008; backend remainder by
SQ-0011; and R, Python, and Julia frontend partitions by SQ-0013, SQ-0014, and
SQ-0015 respectively. Every remainder is fail-closed. The policy is a literal
independently bound verifier constant and is not derived from mutable
`allowed_paths` contract prose.

The live scan rejects owner-status disagreement, illegal lifecycle values,
unowned additions/deletions/changes, symlinks, special files, generated Python
bytecode, and force-added tracked content hidden below ignored build/cache
directories. Ordinary untracked build caches remain outside scientific
evidence; tracked content cannot use those exclusions to escape a partition.

## Regression evidence

The original 59 corruption and lifecycle tests remain present. Thirty-eight
additional v3 tests cover SQ-0007 READY/IN_PROGRESS/IN_REVIEW/DONE and legal
non-authorizing SUPERSEDED behavior, SQ-0008 legal non-authorizing behavior, and Registry
behavior; unrelated Lean and backend changes; SQ-0011 backend ownership;
SQ-0008 Assurance versus Registry ownership; language-specific frontend
partitions; no-owner behavior; symlink, FIFO, bytecode, and tracked-target
smuggling; historical v2 mutation; policy mutation; owner status disagreement;
and illegal owner status. The resulting focused suite passes all 97 tests.

## TCB and nonclaims

The live path classifier and owner-status reader enter the evidence-verifier
TCB. Git is used only to expose tracked files hidden under ignored operational
directories; filesystem traversal remains authoritative for normal paths.
This maintenance does not authorize a successor, validate Registry semantics,
prove source fidelity, alter canonical bytes, or confer production authority.

## Bound subjects

<!-- SQ-0005-REVIEW-SUBJECTS-BEGIN -->
```json
{
  ".github/workflows/serialization-prototypes.yml": "3cb67d26721258413ff80150df453dca77f76ea77374fe6a5a92bd7494cd8536",
  "ARCHITECTURE.md": "482523d5cf858b1674852074695ecab54623bbbe0814f5e9417eca32f060005a",
  "conformance/prototypes/evidence/evidence-manifest.json": "33d7a0b5898d45e5cc88b18dafc81e3933f7b7a025562d0c2f1c722ac5a31bb6",
  "conformance/prototypes/evidence/evidence-spec.json": "39fd75ffb754a7f9f7a5a3dafb3653973e65af2f944ae782c6e70e29db3c54b4",
  "conformance/prototypes/fixtures/semantic-v1/catalog.json": "d5bf3079d9ff8119a2372873a1b116601011e78c30067bc1d05228211659b4d3",
  "conformance/prototypes/fixtures/semantic-v1/digest-framing.json": "36895de279202434a1511bb1bf552c199e55d57ee8a57a7d724772a737824d0b",
  "conformance/prototypes/generated-v1/manifest.json": "e69e863053fad44faf2511cedbd53a13725e309cbdb0551621e217c2095dd6cd",
  "conformance/prototypes/generated-v1/mutations.json": "1b6c448a29ce76b83c5e85673731382dc24bba8a1902a7686988626015d22da6",
  "conformance/prototypes/generated-v1/results.json": "4e48d962644cec0f83b868ba13bcc62f3bc8cee4dca748fed10e3ad911195274",
  "conformance/prototypes/golden/serialization-v1/manifest.json": "8db0e43760421ea694e0e2d7095ade93a821ce5f3b7c66eaf954d7fe969af7a1",
  "docs/adr/0004-deterministic-cbor-cddl.md": "a27be26c3d4e89518943b08a4d042ef9a2c824612df77c45ad07abd5bcb587f4",
  "docs/research/serialization/profile-candidate.md": "6cbf0f686a1f35b5c6fac8411ef5abc708c9c4410b5fdb2ee510c513df067d2f",
  "docs/research/serialization/semantic-value-model.md": "a94588e54fdc3e2aa08e73f5f6e76bb71128940bb245305b2dec9dffa2ffcfb2",
  "rfcs/0001-deterministic-encoding.md": "0f542ba487e77a2008a71ef6c92b642cf89503d96d8da63680575e109a97741f",
  "schemas/prototypes/cddl/profile-v1.cddl": "05ee85b0d028af588ed9e95e83fdf017259988f05709de85f033cb0ab5badda0",
  "schemas/prototypes/lineage.json": "7a7e48658e81e478c3858f265d24eb0c1402fa6169e7c03eb74363effb8208a4",
  "schemas/prototypes/python-oracle/.python-version": "aa0d6581054e6e4ff3f91839deca7a854ad37221b8784d060b42d0f847ff1a3b",
  "schemas/prototypes/python-oracle/LINEAGE.md": "8dfe50d1a4010984881c77cd48fa3eca14e307e71d8cc0b5afed48d3e6babd92",
  "schemas/prototypes/rust-cbor/Cargo.lock": "2e9c4f95aa0aa54ab2338e980d388f9f0223be8964d94f82d82f086f2dadb180",
  "schemas/prototypes/rust-cbor/LINEAGE.md": "6136314a0c7ac9b971f636e520e8d9dd0d94548f39a96a891d34a37ac9e1dd1a",
  "schemas/prototypes/rust-cbor/evidence/advisory-report.json": "abe01dc61e4f02fb179f39457077b832491c3503d8461fe82f1835712482cd55",
  "schemas/prototypes/rust-cbor/evidence/crates-io-yanked.json": "fd69cb31758d9f3da5f674a3b14b731bda03ba77e9ca1295e03663d67e571e2b",
  "schemas/prototypes/rust-cbor/evidence/dependency-license-inventory.json": "3d44e9d26c756c2aa950779f9fcf557f11efc28a50d20f27c2ec1a501aaadfa9",
  "scripts/serialization/build_evidence_manifest.py": "3d7367c471f3307093ffe91ee1011c953aed87d76857646f28dc327d570509ca",
  "scripts/serialization/check_evidence.py": "920487821d11ab335130c1bffb3f7e4378265b57872ff61e2fe72dc82fa54381",
  "scripts/serialization/run_conformance.py": "8a61f6deeeba7bed4e8bb7e0c8202fa0ce730d5328036365d8536ed5950fe01c",
  "scripts/serialization/tests/test_check_evidence.py": "9e352056f1a9a0fc7671d1f9fa82f56894b475f7efb84f155ebf4671624de85b",
  "source-audits/encoding/manifest.json": "b3f70746a36c350590f2f77ffebb0e550773337d79db4103317426be94ac0a40",
  "work/reviews/SQ-0005-evidence-lifecycle.md": "ae2753b4b74c6c297bfe75556d940579f16696565821ffdae0d9cda9f3b746ba",
  "work/reviews/SQ-0005.md": "a45c57c5abf9d99b89a5c5b86143da34651728a86b3b72d8ca7d5886a62f3ff7"
}
```
<!-- SQ-0005-REVIEW-SUBJECTS-END -->

## Independent review disposition

Evidence-lifecycle, adversarial path, CI/reproducibility, and integration
review remain pending for the exact content-addressed candidate. No merge is
approved by this authoring record.

Final disposition: PENDING_INDEPENDENT_REVIEW
