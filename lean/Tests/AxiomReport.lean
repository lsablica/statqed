import StatQED
import StatQED.Internal.Smoke
import Lean.Util.CollectAxioms

/-!
# Live axiom-report probe

This test command reads declaration ownership, kinds, types, and transitive
axioms from the elaborated `Lean.Environment`. Its output is an intermediate
machine-readable observation. `tools/axiom_report.py` binds that observation to
the exact project lock, tool versions, and checked-out Mathlib revision.
-/

open Lean Elab Command

namespace StatQED.Tests.AxiomReport

private def projectModulePrefix : Name := `StatQED

private def importedDeclarations : Array Name := #[`Set.ext]

private def prohibitedImportedNativeAxioms : Array Name := #[
  `Lean.trustCompiler,
  `Lean.ofReduceBool,
  `Lean.ofReduceNat
]

private def nameStringLt (left right : Name) : Bool :=
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
    | throwError "declaration '{declName}' has no defining module in the imported environment"
  let some moduleName := env.header.moduleNames[moduleIdx.toNat]?
    | throwError "declaration '{declName}' has an invalid defining module index"
  return moduleName

private def isProjectDeclaration (env : Environment) (declName : Name) : Bool :=
  match env.getModuleIdxFor? declName with
  | none => false
  | some moduleIdx =>
      match env.header.moduleNames[moduleIdx.toNat]? with
      | none => false
      | some moduleName => projectModulePrefix.isPrefixOf moduleName

private def renderDeclaration
    (env : Environment) (origin : String) (declName : Name) : CommandElabM Json := do
  let some info := env.find? declName
    | throwError "declaration '{declName}' is absent from the elaborated environment"
  let moduleName ← moduleOf env declName
  let kind := ConstantKind.ofConstantInfo info
  if origin == "project" && kind == .axiom then
    throwError "project declaration '{declName}' is an axiom declaration"
  let axioms ← collectAxioms declName
  let axioms := axioms.qsort nameStringLt
  if origin == "project" && axioms.contains ``sorryAx then
    throwError "project declaration '{declName}' depends on sorryAx"
  if origin == "project" && axioms.any prohibitedImportedNativeAxioms.contains then
    throwError "project declaration '{declName}' depends on a prohibited native-trust axiom"
  if origin == "project" && axioms.any (isProjectDeclaration env) then
    throwError "project declaration '{declName}' depends on a project axiom declaration"
  return Json.mkObj [
    ("axioms", .arr <| axioms.map fun name => .str name.toString),
    ("declaration", .str declName.toString),
    ("kind", .str <| kindString kind),
    ("module", .str moduleName.toString),
    ("origin", .str origin),
    ("type", .str <| toString (repr info.type))
  ]

elab "#statqed_axiom_report" : command => do
  let env ← getEnv
  let projectModules := env.header.moduleNames
    |>.filter (projectModulePrefix.isPrefixOf ·)
    |>.qsort nameStringLt
  let projectDeclarations := env.const2ModIdx.keysArray
    |>.filter (fun declName =>
      match env.getModuleIdxFor? declName with
      | none => false
      | some moduleIdx =>
          match env.header.moduleNames[moduleIdx.toNat]? with
          | none => false
          | some moduleName => projectModulePrefix.isPrefixOf moduleName)
    |>.qsort nameStringLt
  let mut declarationSpecs := #[]
  for declName in projectDeclarations do
    declarationSpecs := declarationSpecs.push (declName, "project")
  for declName in importedDeclarations.qsort nameStringLt do
    declarationSpecs := declarationSpecs.push (declName, "imported_mathlib")
  declarationSpecs := declarationSpecs.qsort fun left right => nameStringLt left.1 right.1
  let mut declarations := #[]
  for (declName, origin) in declarationSpecs do
    declarations := declarations.push (← renderDeclaration env origin declName)
  let report := Json.mkObj [
    ("declarations", .arr declarations),
    ("project_modules", .arr <| projectModules.map fun name => .str name.toString),
    ("schema_version", .num 1)
  ]
  IO.println "STATQED_AXIOM_REPORT_BEGIN"
  IO.println report.compress
  IO.println "STATQED_AXIOM_REPORT_END"

end StatQED.Tests.AxiomReport

#statqed_axiom_report
