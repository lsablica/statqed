import StatQED.Registry.Closure
import StatQED.Registry.Tests.Smoke

/-! Emit the live, typed proposition and closure observation. -/

open Lean Elab Command

namespace StatQED.Registry.Tools.Extract

private def declarations : Array Name := #[
  `StatQED.Registry.Tests.testOnlyTrue,
  `StatQED.Registry.Tests.testOnlyTrueRefactor,
  `StatQED.Registry.Tests.falseImpliesTrue
]

private def kindString : ConstantInfo → String
  | .axiomInfo _ => "axiom"
  | .defnInfo _ => "definition"
  | .thmInfo _ => "theorem"
  | .opaqueInfo _ => "opaque"
  | .quotInfo _ => "quotient"
  | .inductInfo _ => "inductive"
  | .ctorInfo _ => "constructor"
  | .recInfo _ => "recursor"

elab "#statqed_registry_extract" : command => do
  let environment ← getEnv
  let mut records := #[]
  for declaration in declarations do
    let some info := environment.find? declaration
      | throwError "registry declaration '{declaration}' is missing"
    let proposition ← match StatQED.Registry.propositionJson info.levelParams info.type with
      | .ok value => pure value
      | .error reason => throwError "failed to normalize '{declaration}': {reason}"
    let some proofValue := info.value? (allowOpaque := true)
      | throwError "registry declaration '{declaration}' has no proof/value subject"
    let proofSubject ← match StatQED.Registry.declarationExprJson
        info.levelParams StatQED.Registry.maxExpressionDepth proofValue with
      | .ok value => pure value
      | .error reason => throwError "failed to normalize proof/value for '{declaration}': {reason}"
    let closure ← match StatQED.Registry.collectClosure environment
        (StatQED.Registry.propositionRoots info.type) with
      | .ok value => pure value
      | .error reason => throwError "failed to collect closure for '{declaration}': {reason}"
    records := records.push <| Json.mkObj [
      ("closure", .arr closure),
      ("closure_version", .str StatQED.Registry.closureVersion),
      ("declaration", .str declaration.toString),
      ("kind", .str <| kindString info),
      ("proof_subject", proofSubject),
      ("proof_subject_version", .str StatQED.Registry.normalizerVersion),
      ("proposition", proposition)
    ]
  let report := Json.mkObj [
    ("declarations", .arr records),
    ("schema", .str "statqed.registry-lean-observation.v0")
  ]
  IO.println "STATQED_REGISTRY_EXTRACT_BEGIN"
  IO.println report.compress
  IO.println "STATQED_REGISTRY_EXTRACT_END"

end StatQED.Registry.Tools.Extract

#statqed_registry_extract
