# Trusted-path mutation fixtures

These files are declarative inputs for the repository trust scanner. Files with
the `.fixture` suffix are intentionally not part of the accepted Lean build.
`expectations.json` states how a runner copies or mutates each input and the
distinct reason it must observe. The corpus includes positive controls so a
scanner cannot reject comments or strings merely because they contain a banned
token.

`kernel_projection_14576.lean.fixture` is the verbatim reproducer from
Lean issue #14576. The exact pinned Lean 4.32.2 kernel must reject it under
`--trust=0`; this regression is operational security evidence, not a claim
that the pin is defect-free.

Lean 4.32.2 has no `constant` declaration command. The retained
`constant_syntax_impossible.lean.fixture` fails in the parser and is language
evidence only. The non-vacuous bodyless-assumption mutation instead uses the
ordinary checked `addDecl` path to insert an `.axiomDecl`. A right-hand-side-free
`opaque` declaration is not classified as an axiom: Lean supplies a default
implementation when the type is inhabited.

The native-evaluation controls cover `Lean.trustCompiler`, `bv_decide`,
`Lean.ofReduceBool`, `Lean.ofReduceNat`, and the indirect `Lean.reduceBool` and
`Lean.reduceNat` dependencies. All are kernel-accepted under `--trust=0` and
retain native trust axioms, so both the source scan and the live axiom-closure
gate must reject them before they can enter the accepted source tree. The live
report mutation ensures this policy is not tested only through source tokens.
Separate live-report cases also build and reject `sorryAx`, checked
`.axiomDecl`, and an unsafe project declaration, so those environment gates
cannot be removed while the source-only mutations continue to pass.
