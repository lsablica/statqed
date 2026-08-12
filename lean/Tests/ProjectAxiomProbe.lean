import Lean.Util.CollectAxioms

/-!
# Compositional project axiom probe

This module defines a command used by a generated wrapper which imports every
tracked `StatQED` module.  It intentionally does not import `StatQED` itself:
the Python orchestrator owns the complete, deterministic import surface.
-/

open Lean Elab Command

namespace StatQED.Tests.ProjectAxiomProbe

private def projectPrefix : Name := `StatQED

private def prohibitedNativeAxioms : Array Name := #[
  `Lean.trustCompiler,
  `Lean.ofReduceBool,
  `Lean.ofReduceNat
]

private def nameLt (left right : Name) : Bool :=
  left.toString < right.toString

private def kindString : ConstantKind → String
  | .defn => "definition"
  | .thm => "theorem"
  | .axiom => "axiom"
  | .opaque => "opaque"
  | .quot => "quotient"
  | .induct => "inductive"
  | .ctor => "constructor"
  | .recursor => "recursor"

private def moduleOf (env : Environment) (declName : Name) : CommandElabM Name := do
  let some moduleIdx := env.getModuleIdxFor? declName
    | throwError "project declaration '{declName}' has no defining module"
  let some moduleName := env.header.moduleNames[moduleIdx.toNat]?
    | throwError "project declaration '{declName}' has an invalid module index"
  return moduleName

private def isProjectModule (moduleName : Name) : Bool :=
  projectPrefix.isPrefixOf moduleName

private def isProjectDeclaration (env : Environment) (declName : Name) : Bool :=
  match env.getModuleIdxFor? declName with
  | none => false
  | some moduleIdx =>
      match env.header.moduleNames[moduleIdx.toNat]? with
      | none => false
      | some moduleName => isProjectModule moduleName

private def renderDeclaration
    (env : Environment) (projectAxioms : Array Name) (declName : Name) :
    CommandElabM Json := do
  let some info := env.find? declName
    | throwError "project declaration '{declName}' has no ConstantInfo"
  let moduleName ← moduleOf env declName
  let kind := ConstantKind.ofConstantInfo info
  if kind == .axiom then
    throwError "project declaration '{declName}' is an axiom declaration"
  if info.isUnsafe then
    throwError "project declaration '{declName}' is unsafe"
  let axioms := (← collectAxioms declName).qsort nameLt
  if axioms.contains ``sorryAx then
    throwError "project declaration '{declName}' depends on sorryAx"
  if axioms.any prohibitedNativeAxioms.contains then
    throwError "project declaration '{declName}' depends on a prohibited native-trust axiom"
  if axioms.any projectAxioms.contains then
    throwError "project declaration '{declName}' depends on a project axiom declaration"
  return Json.mkObj [
    ("axioms", .arr <| axioms.map fun name => .str name.toString),
    ("declaration", .str declName.toString),
    ("kind", .str <| kindString kind),
    ("module", .str moduleName.toString),
    ("type", .str <| toString (repr info.type)),
    ("unsafe", .bool info.isUnsafe)
  ]

elab "#statqed_project_axiom_report" : command => do
  let env ← getEnv
  let projectModules := env.header.moduleNames
    |>.filter isProjectModule
    |>.qsort nameLt
  -- `const2ModIdx` can include compiler bookkeeping names with no
  -- `ConstantInfo`; those are not declarations and are excluded explicitly.
  let projectDeclarations := env.const2ModIdx.keysArray
    |>.filter (fun declName => isProjectDeclaration env declName && (env.find? declName).isSome)
    |>.qsort nameLt
  let projectAxioms := projectDeclarations.filter fun declName =>
    match env.find? declName with
    | some info => ConstantKind.ofConstantInfo info == .axiom
    | none => false
  let mut declarations := #[]
  for declName in projectDeclarations do
    declarations := declarations.push (← renderDeclaration env projectAxioms declName)
  let report := Json.mkObj [
    ("declarations", .arr declarations),
    ("project_modules", .arr <| projectModules.map fun name => .str name.toString),
    ("schema_version", .str "statqed.project-axiom-observation.v1")
  ]
  IO.println "STATQED_PROJECT_AXIOM_REPORT_BEGIN"
  IO.println report.compress
  IO.println "STATQED_PROJECT_AXIOM_REPORT_END"

end StatQED.Tests.ProjectAxiomProbe
