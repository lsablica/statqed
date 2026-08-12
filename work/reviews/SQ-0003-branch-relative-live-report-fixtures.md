# SQ-0003 branch-relative live-report fixture review

Status: IN_REVIEW — exact-head hosted and integration dispositions pending

## Defect and correction

The two successful live-report mutation controls previously asserted the fixed
JSON substrings `"module_count": 3` and `"module_count": 7`. Those totals
were valid only for the historical two-module foundation tree. The mutation
runner copies the current branch, so a legitimate successor tree with eight
tracked modules produced nine and thirteen modules and was incorrectly
rejected.

Mutation-expectation schema v2 replaces the totals with an exact-set rule. The
runner uses `source_modules` from the copied production reporter to discover
the sorted, unique baseline before mutation. It verifies each declared added
module against its target path, parses successful output as one canonical JSON
document, and requires the observed modules to equal exactly the baseline
union the declared additions. Missing, unexpected, duplicate, unsorted, wrong
schema, inconsistent count, noncanonical JSON, and unexpected stderr are
rejected. The five negative live-report cases retain their exact intended
diagnostics for sorry, project axiom, unsafe declaration, native trust, and an
unimportable module.

The production reporter, project probe, all-module checker, report schema,
fresh-kernel policy, and workflow are byte-identical to main
`950ebf5f591f7d58d089d215c9c76863bc50f7f6`.

## Bound maintenance subjects

| Subject | Before SHA-256 | Candidate SHA-256 |
|---|---|---|
| `lean/Tests/Trust/expectations.json` | `07f879123539a21b38a09b10021243cb4a80112ccf4b507b0c45f118eeb73027` | `042f07079be02de8ad6185eb15be5a33f7157785d8e955e9592f589f1d1bc878` |
| `scripts/check_lean_trust.py` | `0ee817504633cfff0d1dfac7e2ca2567c2a7bed5474bf3ae678c0e3214537215` | `e3c5a2e9366b455769be682bff0171c947cd62a126065e4f24c170f393414c46` |
| `lean/tools/tests/test_branch_relative_live_reports.py` | absent | `eda6a4994a8ef5d38be81963a1900923f3a1a57a643259b024507e66fdba5142` |

The live mutation corpus remains 36 cases. Twenty focused v2 regressions cover
the historical two-module case, a tracked synthetic eight-module repository,
the actual discovery/mutation/result-assembly wiring with controlled Lean
subprocesses, and exact-union failures. This focused regression observes final
counts three/seven and nine/thirteen as derived results; it is not represented
as the complete mutation gate. No fixed total is stored in the expectation
format.

The unmodified full gate was also run in a disposable clone with six staged
`StatQED.Registry.ExistingA`–`ExistingF` modules in addition to the two
foundation modules:

```text
PATH=<pinned-elan>/bin ELAN_HOME=<pinned-elan> \
  python3 scripts/check_lean_trust.py --run-mutations
```

After `lake build` completed 94 jobs, production discovery reported the exact
eight-module baseline; all eight modules passed fresh replay and all 36
intended differentials passed without expectation filtering or mocked build or
report execution. The first pre-build invocation was retained as an
operational setup failure (`unknown module prefix 'StatQED'`) and is not
counted as verification evidence.

## Trust boundary and nonclaims

Python orchestration, Git's tracked-file view, the pinned Lean reporter, the
Lean toolchain, and review of the exact-set rule are in the evidence TCB. This
maintenance changes test expectations, not theorem meaning or production
acceptance policy. It establishes neither source fidelity nor theorem
identity, authorization, artifact verification, or statistical validity.

Independent Lean, project-report, adversarial, reproducibility, and final
integration dispositions must bind the exact committed head before merge.
