# SQ-0003 Lean evidence

Status: **Experimental**.

These records preserve exact observed commands and results for the production
Lean bootstrap. They are reproducibility evidence, not a theorem lock,
platform guarantee, artifact verification record, or statistical claim.

- `environment.json`: directly observed host and tool identities.
- `normal-build.json`: cache-enabled project-clean build and example evidence.
- `manifest-reproduction.json`: fresh, no-cache manifest regeneration and byte comparison.
- `kernel-regression.json`: expected pinned-kernel rejection of Lean issue #14576.
- `mutation-tests.json`: exact 33-case trust mutation and regression result,
  generated with `python3 scripts/check_lean_trust.py --run-mutations
  --write-json lean/evidence/mutation-tests.json` from the repository root.
- `native-trust-controls.json`: pinned-kernel axiom closures for six direct and
  indirect native-evaluation controls.
- `bodyless-assumption.json`: accepted checked `.axiomDecl` control which trust checks must reject.
- `bodyless-constant-language.json`: pinned parser evidence that `constant` is not a Lean 4 command.
- `no-cache-source-build-initial.json`: the first successful isolated source
  build, retained after its report schema was superseded by formal review.
- `no-cache-source-build.json`: the repeated isolated source build against the
  corrected immutable candidate and current axiom report.
- `failures/`: preserved failed attempts and their resolutions, including the
  sandbox DNS boundary and initial hosted workflow-configuration rejection.

`Reports/axioms.json` is kept outside this directory because it is a generated,
machine-checked project report rather than a hand-written command transcript.
