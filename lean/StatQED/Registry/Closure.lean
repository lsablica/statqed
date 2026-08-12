import StatQED.Registry.Normalize
import Lean.Util.FoldConsts

/-!
# Conservative meaning-bearing closure observation

The closure traverses declaration types and definition bodies. Theorem and
opaque proof bodies are deliberately excluded from semantic closure and belong
to the separate proof/build lock. Inductive families add their constructors
and recursor as an atomic family.
-/

open Lean

namespace StatQED.Registry

def closureVersion : String := "statqed.lean-environment-closure.v0"
def maxClosureRoots : Nat := 256
def maxClosureUnits : Nat := 1024
def maxClosureWidth : Nat := 256
def maxClosureDepth : Nat := 64
def maxClosureWork : Nat := 1000000
def maxClosureExpressionNodes : Nat := 262144
def maxClosureObservationBytes : Nat := 1048576

private def namesIn (expression : Expr) : Array Name :=
  expression.getUsedConstants.qsort (fun left right => Name.quickCmp left right == .lt)

private def projectionNames (fuel : Nat) : Expr → Array Name
  | expression => match fuel with
    | 0 => #[]
    | fuel + 1 => match expression with
      | .app function argument => projectionNames fuel function ++ projectionNames fuel argument
      | .lam _ type body _ | .forallE _ type body _ =>
          projectionNames fuel type ++ projectionNames fuel body
      | .letE _ type value body _ =>
          projectionNames fuel type ++ projectionNames fuel value ++ projectionNames fuel body
      | .mdata _ inner => projectionNames fuel inner
      | .proj typeName _ subject => #[typeName] ++ projectionNames fuel subject
      | _ => #[]
termination_by fuel

private def appendUnique (names more : Array Name) : Array Name :=
  more.foldl (fun acc name => if acc.contains name then acc else acc.push name) names

private def structuralNames (expression : Expr) : Array Name :=
  appendUnique (namesIn expression) (projectionNames maxExpressionDepth expression)
    |>.qsort (fun left right => Name.quickCmp left right == .lt)

private def familyNames : ConstantInfo → Array Name
  | .inductInfo value =>
      (value.all ++ value.ctors ++ value.all.map (fun name => name.str "rec")).toArray
  | .ctorInfo value => #[value.induct]
  | .recInfo value => value.all.toArray ++ value.rules.toArray.map (·.ctor)
  | _ => #[]

/-- References that carry semantic meaning for a declaration record. -/
def semanticReferences (info : ConstantInfo) : Array Name :=
  let fromType := structuralNames info.type
  let fromDefinition := match info with
    | .defnInfo value => structuralNames value.value
    | .recInfo value =>
        value.rules.foldl (fun names rule => appendUnique names (structuralNames rule.rhs)) #[]
    | _ => #[]
  appendUnique (appendUnique fromType fromDefinition) (familyNames info)
    |>.qsort (fun left right => Name.quickCmp left right == .lt)

private def kindString : ConstantInfo → String
  | .axiomInfo _ => "axiom"
  | .defnInfo _ => "definition"
  | .thmInfo _ => "theorem"
  | .opaqueInfo _ => "opaque"
  | .quotInfo _ => "quotient"
  | .inductInfo _ => "inductive"
  | .ctorInfo _ => "constructor"
  | .recInfo _ => "recursor"

private def reducibilityString : ConstantInfo → String
  | .defnInfo value => match value.hints with
    | .abbrev => "abbreviation"
    | .opaque => "opaque"
    | .regular _ => "regular"
  | _ => "not_applicable"

private def bodyJson : ConstantInfo → Except String Json
  | .defnInfo value => declarationExprJson value.levelParams maxExpressionDepth value.value
  | _ => .ok .null

private def declarationExpressionNodes
    (environment : Environment) (info : ConstantInfo) : Except String Nat := do
  let mut nodes := (← expressionStats info.levelParams info.type).1
  match info with
  | .defnInfo value =>
      nodes := nodes + (← expressionStats value.levelParams value.value).1
  | .inductInfo value =>
      for constructor in value.ctors do
        let some (.ctorInfo constructorInfo) := environment.find? constructor
          | .error s!"registry.closure.missing_constructor:{constructor}"
        nodes := nodes + (← expressionStats constructorInfo.levelParams constructorInfo.type).1
      for familyName in value.all do
        let recursorName := familyName.str "rec"
        let some (.recInfo recursorInfo) := environment.find? recursorName
          | .error s!"registry.closure.missing_recursor:{recursorName}"
        nodes := nodes + (← expressionStats recursorInfo.levelParams recursorInfo.type).1
        for rule in recursorInfo.rules do
          nodes := nodes + (← expressionStats recursorInfo.levelParams rule.rhs).1
  | .recInfo value =>
      for rule in value.rules do
        nodes := nodes + (← expressionStats value.levelParams rule.rhs).1
  | _ => pure ()
  pure nodes

private def originString (info : ConstantInfo) : String :=
  if info.name.toString.startsWith "StatQED." then "project" else "imported"

private def nameArrayJson (names : List Name) : Json :=
  .arr <| names.toArray.map nameJson

private def constructorJson (environment : Environment) (name : Name) : Except String Json := do
  let some (.ctorInfo value) := environment.find? name
    | .error s!"registry.closure.missing_constructor:{name}"
  let typeJson ← declarationExprJson value.levelParams maxExpressionDepth value.type
  pure <| Json.mkObj [
    ("constructor_index", toJson value.cidx),
    ("name", nameJson value.name),
    ("num_fields", toJson value.numFields),
    ("num_parameters", toJson value.numParams),
    ("type", typeJson),
    ("unsafe", .bool value.isUnsafe)
  ]

private def recursorJson (environment : Environment) (name : Name) : Except String Json := do
  let some (.recInfo value) := environment.find? name
    | .error s!"registry.closure.missing_recursor:{name}"
  let typeJson ← declarationExprJson value.levelParams maxExpressionDepth value.type
  let mut rules := #[]
  for rule in value.rules do
    let rhs ← declarationExprJson value.levelParams maxExpressionDepth rule.rhs
    rules := rules.push <| Json.mkObj [
      ("constructor", nameJson rule.ctor),
      ("field_count", toJson rule.nfields),
      ("rhs", rhs)
    ]
  pure <| Json.mkObj [
    ("family", nameArrayJson value.all),
    ("k_reduction", .bool value.k),
    ("name", nameJson value.name),
    ("num_indices", toJson value.numIndices),
    ("num_minors", toJson value.numMinors),
    ("num_motives", toJson value.numMotives),
    ("num_parameters", toJson value.numParams),
    ("rules", .arr rules),
    ("type", typeJson),
    ("unsafe", .bool value.isUnsafe)
  ]

/-- Emit one declaration's semantic closure record. -/
def closureRecordJson (environment : Environment) (info : ConstantInfo) : Except String Json := do
  let typeJson ← declarationExprJson info.levelParams maxExpressionDepth info.type
  let bodyJson ← bodyJson info
  let references := semanticReferences info
  let (kind, extra) ← match info with
    | .inductInfo value =>
        let constructors ← value.ctors.mapM (constructorJson environment)
        let recursors ← value.all.mapM (fun name => recursorJson environment (name.str "rec"))
        pure ("inductive_family", #[
          ("constructors", .arr constructors.toArray),
          ("family", nameArrayJson value.all),
          ("is_recursive", .bool value.isRec),
          ("is_reflexive", .bool value.isReflexive),
          ("num_indices", toJson value.numIndices),
          ("num_nested", toJson value.numNested),
          ("num_parameters", toJson value.numParams),
          ("recursors", .arr recursors.toArray)
        ])
    | _ => pure (kindString info, #[])
  let base := [
    ("body", bodyJson),
    ("kind", .str kind),
    ("level_parameters", .arr <| info.levelParams.toArray.map nameJson),
    ("name", nameJson info.name),
    ("origin", .str <| originString info),
    ("reducibility", .str <| reducibilityString info),
    ("references", .arr <| references.map nameJson),
    ("type", typeJson),
    ("unsafe", .bool info.isUnsafe)
  ]
  pure <| Json.mkObj (base ++ extra.toList)

private def inductiveFamilyRoot? (environment : Environment) (name : Name) : Option Name := do
  let info ← environment.find? name
  match info with
  | .inductInfo value => value.all.head?
  | .ctorInfo value => some value.induct
  | .recInfo value => value.all.head?
  | _ => none

private def canonicalUnitName (environment : Environment) (name : Name) : Name :=
  (inductiveFamilyRoot? environment name).getD name

private def sameInductiveFamily
    (environment : Environment) (left right : Name) : Bool :=
  match inductiveFamilyRoot? environment left, inductiveFamilyRoot? environment right with
  | some leftRoot, some rightRoot => leftRoot == rightRoot
  | _, _ => false

private def visitClosure
    (environment : Environment)
    (current : Name)
    (path visited : Array Name)
    (work expressionNodes fuel : Nat) :
    Except String (Array (Name × Json) × Array Name × Nat × Nat) :=
  let current := canonicalUnitName environment current
  let work := work + 1
  if work > maxClosureWork then
    .error "registry.closure.work_budget_limit"
  else
  if path.contains current then
    match path.back? with
    | some parent =>
        if sameInductiveFamily environment parent current then
          .ok (#[], visited, work, expressionNodes)
        else
          .error s!"registry.closure.cycle:{current}"
    | none => .error s!"registry.closure.cycle:{current}"
  else if visited.contains current then
    .ok (#[], visited, work, expressionNodes)
  else if visited.size + path.size >= maxClosureUnits then
    .error "registry.closure.unit_limit"
  else match fuel with
    | 0 => .error "registry.closure.depth_limit"
    | fuel + 1 => do
        let some info := environment.find? current
          | .error s!"registry.closure.missing_dependency:{current}"
        if info.isUnsafe then
          .error s!"registry.closure.unsafe_declaration:{current}"
        let expressionNodes := expressionNodes + (← declarationExpressionNodes environment info)
        if expressionNodes > maxClosureExpressionNodes then
          .error "registry.closure.expression_node_limit"
        let record ← closureRecordJson environment info
        let mut records := #[(current, record)]
        let mut nextVisited := visited.push current
        let mut nextWork := work
        let mut nextExpressionNodes := expressionNodes
        let nextPath := path.push current
        let references := semanticReferences info
        if references.size > maxClosureWidth then
          .error "registry.closure.width_limit"
        for reference in references do
          let (nested, nestedVisited, nestedWork, nestedExpressionNodes) ←
            visitClosure environment reference nextPath nextVisited nextWork nextExpressionNodes fuel
          records := records ++ nested
          nextVisited := nestedVisited
          nextWork := nestedWork
          nextExpressionNodes := nestedExpressionNodes
        pure (records, nextVisited, nextWork, nextExpressionNodes)
termination_by fuel

/--
Collect a deterministic transitive closure with an explicit record budget.
Missing declarations and cycles through the active recursion path fail closed.
-/
def collectClosure
    (environment : Environment) (roots : Array Name) : Except String (Array Json) := do
  if roots.size > maxClosureRoots then
    .error "registry.closure.root_limit"
  let sortedRoots := roots.map (canonicalUnitName environment)
    |>.qsort (fun left right => Name.quickCmp left right == .lt)
  let mut records := #[]
  let mut visited := #[]
  let mut work := 0
  let mut expressionNodes := 0
  for root in sortedRoots do
    let (nested, nestedVisited, nestedWork, nestedExpressionNodes) ←
      visitClosure environment root #[] visited work expressionNodes maxClosureDepth
    records := records ++ nested
    visited := nestedVisited
    work := nestedWork
    expressionNodes := nestedExpressionNodes
  if records.size > maxClosureUnits then
    .error "registry.closure.work_budget_limit"
  else
    let result := records
      |>.qsort (fun left right => Name.quickCmp left.1 right.1 == .lt)
      |>.map (·.2)
    if (Json.arr result).compress.toUTF8.size > maxClosureObservationBytes then
      .error "registry.closure.output_limit"
    else
      pure result

/-- Roots referenced by the normalized proposition type. -/
def propositionRoots (type : Expr) : Array Name := namesIn type
  |> appendUnique (projectionNames maxExpressionDepth type)
  |>.qsort (fun left right => Name.quickCmp left right == .lt)

end StatQED.Registry
