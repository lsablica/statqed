# Supplemental review: SQ-0003 compositional axiom coverage

Status: **IMPLEMENTATION CANDIDATE — INDEPENDENT DISPOSITION REQUIRED**

## Scope and preserved history

This maintenance does not rewrite the SQ-0003 scientific or completion
record. It adds a versioned live project-wide check so future reviewed Lean
owners can add modules without mutating the original global report.

- SQ-0003 normal merge: `92e3b331b1ae795a21d6e030a21e8ce8d7da03dd`.
- Historical `lean/Tests/AxiomReport.lean`: SHA-256
  `bf1acd71f1b32f4b2e80b24114318a44903c9eb19a7fcd9ff57d90e4e667d23e`.
- Historical `lean/tools/axiom_report.py`: SHA-256
  `487d89eb6d6703f428c1d4043af931bc80665e623dc717419c7aacaec986c498`.
- Historical `lean/Reports/axioms.json`: SHA-256
  `96a2b221dcc7f0a08607fbc935f31c5c4846486b0d4edcb585bddfad2298346b`.

Those three files are byte-identical. The new
`foundation-axiom-history.json` explicitly records that their two-module
surface is an SQ-0003 completion snapshot, not live coverage of later modules.

## Live policy and subjects

| Subject | SHA-256 |
|---|---|
| `lean/Tests/ProjectAxiomProbe.lean` | `1937b31ae83163408a2654628d593e88475924f738cb6d1e007ddbe844b9a227` |
| `lean/tools/project_axiom_report.py` | `898e60def7dee4c6725bf92954d93933d7b07de1661324e67c26f082dd963627` |
| `lean/tools/check_all_modules.py` | `8a33ca751a1d2faa019dcd73e3f6a7442ffa0bbea23e13fe07aa73300160d79e` |
| `lean/tools/tests/test_project_trust.py` | `a43318abd6bd3fa00f9d138edf03b54331294ac94d0bef8d3d6c0c6e5f629ad8` |
| `lean/Tests/Trust/expectations.json` | `07f879123539a21b38a09b10021243cb4a80112ccf4b507b0c45f118eeb73027` |
| `lean/Tests/Trust/registry_axiom.lean.fixture` | `fdbc5ae37a9120765d17b15d1da9f511c10a1d3187ddc0e3959c93bf637e37cb` |
| `lean/Tests/Trust/registry_native.lean.fixture` | `aeb78a41b2f8ee5c9f593c0608bb9d620d4f78842409e6e1698d806cb46399eb` |
| `lean/Tests/Trust/registry_safe.lean.fixture` | `1236c38813556d6455f7b811535710047146312a48e582178579b92375caf6da` |
| `lean/Tests/Trust/registry_sorry.lean.fixture` | `73ca9a0f83afa2ed4dab69329fccc7d278184f5082c0b99a39c1ff04ae660aa9` |
| `lean/Tests/Trust/registry_unimportable.lean.fixture` | `4a705c992a3d9c80919042b71b46890b17e7fc96cf82b8113321729c690b6ccd` |
| `lean/Tests/Trust/registry_unsafe.lean.fixture` | `4749255e3682b2df1151418ccd6f804476cc7a1a5dea8032319c8b3e42ac12c2` |
| `lean/Reports/foundation-axiom-history.json` | `4295ec84023209cf794f2172a960f938f296020379e867fc3e1939a0f1fa7042` |
| `scripts/check_lean_trust.py` | `0ee817504633cfff0d1dfac7e2ca2567c2a7bed5474bf3ae678c0e3214537215` |
| `.github/workflows/lean.yml` | `80f3f254e2741ff0f5c509d38d463921f2dc3a96cbcea6ab2dcf0e99ec34e2c6` |
| `lean/tools/no_cache_build.sh` | `e853f1795bb2d15d584ecee5e664b5d24faf485e86c6e6a8461d77648f464805` |
| `lean/README.md` | `21fee646dce90e02f474d76daf4e2b56105a43b8dcb1115bff0909487abf942f` |
| `docs/implementation/lean-core.md` | `ac45bf90ed2e41ac7910b83124486f2318650c0787b764f31f0adc365858bfbe` |

The live checker derives modules from both the Git index and the regular-file
source tree. It rejects disagreement, symlinks, special files, invalid or
duplicate module names, missing imports, and imported project modules without
tracked source. An ephemeral wrapper imports the exact derived set and embeds
the reviewed reusable probe command. The probe records each project
declaration's module, kind, unsafe flag, diagnostic `Lean.Expr` representation,
and sorted transitive axiom set from the live environment. It rejects project
axioms, unsafe declarations, `sorryAx`, project-owned axiom closure, and the
listed native-trust axioms.

The fresh checker uses that independently derived sorted module set and runs a
bounded `lake env leanchecker --fresh` command for every module. It fails the
whole result on one replay failure or count disagreement. No globally
committed mutable live report is introduced.

## Tests and observations

- `python3 -m unittest discover -s lean/tools/tests -p 'test_*.py' -v`:
  **PASS, 24 tests**.
- `python3 -m py_compile ...`: **PASS**.
- `git diff --check`: **PASS**.
- `lake build`: **PASS, 88 jobs**, exact Lean v4.32.2/Mathlib checkout cache.
- `python3 lean/tools/project_axiom_report.py --verify`: **PASS** with two
  modules and one project declaration on the maintenance main surface; two
  clean observations were byte-identical.
- `python3 lean/tools/check_all_modules.py --json`: **PASS, two of two tracked
  modules replayed successfully with `lake env leanchecker --fresh`**. The
  Mathlib-heavy replay completed inside the configured 180-second per-module
  bound.
- The focused corpus covers foundation enumeration, one and five Registry
  additions, untracked modules, symlinks, special files, tracked symlink mode,
invalid names, a deterministic unimportable generated wrapper, a direct
generated-wrapper omission guard, omitted/extra observed modules, project
axioms, unsafe declarations,
  `sorryAx`, native trust, duplicate declarations, deterministic wrapper
  generation, all-module replay, replay failure, and five-module replay count.
- The existing live mutation corpus remains wired to the compositional report
  for actual `sorryAx`, project-axiom, unsafe, and native-trust rejection.
- `python3 scripts/check_lean_trust.py --run-mutations`: **PASS, 36 of 36
  intended differentials**, retaining 29 inherited controls and adding two
  live positive Registry surfaces plus live `sorryAx`, project-axiom, unsafe,
  native-trust, and unimportable-module rejection.

The first short interactive observation was stopped without claiming success;
the subsequent integration run used real hard-linked package directories,
rebuilt 88 jobs, and recorded successful replay for both modules. Exact hosted
success remains a merge gate rather than an inference from this local result.

## TCB and nonclaims

The TCB and evidence boundary include the pinned Lean kernel, structural
`.olean` decoding, imported logical axioms, exact toolchain and dependency
lock, Git index, filesystem type observations, Python orchestration, and review
of this policy. Python and CI produce evidence; they do not prove theorem
meaning.

This maintenance does not establish an independent kernel implementation,
source fidelity, theorem identity, authorization, compatibility, statistical
validity, artifact-byte binding, or absence of Lean/kernel defects. It changes
no public theorem, statistical definition, RFC decision, Registry
implementation, or SQ-0003 historical subject.

## Independent review dispositions

The independent Lean/formal-trust reviewer approved the exact implementation
commit `50947998ed62806ff42f51c7b850a55465594f12` with dispositions
`APPROVE_PHASE_M_FORMAL_TRUST` and
`APPROVE_PHASE_M_AXIOM_COMPOSITION`. The review independently reproduced:

- a deterministic project axiom report for two modules and one declaration,
  SHA-256 `13f62b97d944b45e8ec1501a6dc95498079ae7610175d97057582106979cb40c`;
- two of two successful fresh module replays, output SHA-256
  `0ad2b83992af25857d4e5bd99be1ae117a2d3ba832ece56943be689e9507f1de`;
- a passing trust JSON observation with no findings, SHA-256
  `69ddad56f7999b05686958bb0c62ac78e1cb88df6ddd20e64d00ee96afc723b1`;
- all 24 focused composition tests and all 36 inherited/live trust mutations;
  and
- byte-identical preservation of the three historical SQ-0003 subjects.

The independent adversarial and CI reviewer separately approved the bounded
wrapper-omission guard, module-count bound, smuggling rejections, exact action
pins, read-only permissions, cached/source-path parity, and clean-tree gates
(`APPROVE_PHASE_M_ADVERSARIAL_AND_CI`).

Hosted exact-head success and independent integration approval remain merge
gates. These reviews establish compositional live coverage; they do not make
any theorem-identity, source-fidelity, Registry-authorization, artifact, or
statistical-validity claim.

Final formal/composition disposition: APPROVE_PHASE_M_FORMAL_AND_COMPOSITION
