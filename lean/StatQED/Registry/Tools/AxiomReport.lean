import StatQED.Registry.Tests.Smoke
import StatQED.Registry.Normalize
import Lean.Util.CollectAxioms

/-! Emit actual transitive axiom observations from the live environment. -/

open Lean Elab Command

namespace StatQED.Registry.Tools.AxiomReport

private def projectPrefix : Name := `StatQED.Registry

private def declarations : Array Name := #[
  `StatQED.Registry.Tests.testOnlyTrue,
  `StatQED.Registry.Tests.testOnlyTrueRefactor,
  `StatQED.Registry.Tests.falseImpliesTrue,
  `True.intro
]

private def nameLt (left right : Name) : Bool := left.toString < right.toString

private def kindString : ConstantInfo → String
  | .axiomInfo _ => "axiom"
  | .defnInfo _ => "definition"
  | .thmInfo _ => "theorem"
  | .opaqueInfo _ => "opaque"
  | .quotInfo _ => "quotient"
  | .inductInfo _ => "inductive"
  | .ctorInfo _ => "constructor"
  | .recInfo _ => "recursor"

private def isProjectDeclaration (environment : Environment) (name : Name) : Bool :=
  projectPrefix.isPrefixOf name && (environment.find? name).isSome

elab "#statqed_registry_axiom_report" : command => do
  let environment ← getEnv
  let mut records := #[]
  for declaration in declarations.qsort nameLt do
    let some info := environment.find? declaration
      | throwError "registry axiom-report declaration '{declaration}' is missing"
    if isProjectDeclaration environment declaration && info.isUnsafe then
      throwError "project registry declaration '{declaration}' is unsafe"
    if isProjectDeclaration environment declaration && info.isAxiom then
      throwError "project registry declaration '{declaration}' is an axiom"
    let axioms := (← collectAxioms declaration).qsort nameLt
    if isProjectDeclaration environment declaration && axioms.contains ``sorryAx then
      throwError "project registry declaration '{declaration}' depends on sorryAx"
    if isProjectDeclaration environment declaration && (axioms.any fun name =>
        isProjectDeclaration environment name) then
      throwError "project registry declaration '{declaration}' depends on a project axiom"
    let normalizedType ← match StatQED.Registry.declarationExprJson
        info.levelParams StatQED.Registry.maxExpressionDepth info.type with
      | .ok value => pure value
      | .error reason => throwError "failed to normalize type for '{declaration}': {reason}"
    records := records.push <| Json.mkObj [
      ("axioms", .arr <| axioms.map fun name => .str name.toString),
      ("declaration", .str declaration.toString),
      ("kind", .str <| kindString info),
      ("normalized_type", normalizedType),
      ("normalizer", .str StatQED.Registry.normalizerVersion),
      ("origin", .str <| if isProjectDeclaration environment declaration then "project" else "imported"),
      ("type_repr_diagnostic", .str <| toString (repr info.type)),
      ("unsafe", .bool info.isUnsafe)
    ]
  let report := Json.mkObj [
    ("declarations", .arr records),
    ("schema", .str "statqed.registry-axioms.v0")
  ]
  IO.println "STATQED_REGISTRY_AXIOM_REPORT_BEGIN"
  IO.println report.compress
  IO.println "STATQED_REGISTRY_AXIOM_REPORT_END"

end StatQED.Registry.Tools.AxiomReport

#statqed_registry_axiom_report
