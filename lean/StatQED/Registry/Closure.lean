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

/-- A root is at edge depth zero; exactly `maxClosureDepth` edges are accepted. -/
def closureDepthAllowed (edgeDepth : Nat) : Bool :=
  edgeDepth <= maxClosureDepth
def maxClosureObservationBytes : Nat := 1048576

def closureUnitCountAllowed (count : Nat) : Bool := count <= maxClosureUnits
def closureWorkAllowed (count : Nat) : Bool := count <= maxClosureWork

private def namesIn (expression : Expr) : Array Name :=
  expression.getUsedConstants

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

private def sortNamesCanonical (names : Array Name) : Except String (Array Name) := do
  for name in names do
    let _ ← canonicalNameBytes name
  pure <| names.qsort canonicalNameLT

private def structuralNames (expression : Expr) : Except String (Array Name) :=
  sortNamesCanonical <| appendUnique (namesIn expression)
    (projectionNames (maxExpressionDepth + 1) expression)

private def familyNames : ConstantInfo → Array Name
  | .inductInfo value =>
      (value.all ++ value.ctors ++ value.all.map (fun name => name.str "rec")).toArray
  | .ctorInfo value => #[value.induct]
  | .recInfo value => value.all.toArray ++ value.rules.toArray.map (·.ctor)
  | _ => #[]

/-- References that carry semantic meaning for one declaration. -/
private def directSemanticReferences (info : ConstantInfo) : Except String (Array Name) := do
  let fromType ← structuralNames info.type
  let fromDefinition ← match info with
    | .defnInfo value => structuralNames value.value
    | .recInfo value => do
        let mut names := #[]
        for rule in value.rules do
          names := appendUnique names (← structuralNames rule.rhs)
        pure names
    | _ => pure #[]
  sortNamesCanonical <| appendUnique (appendUnique fromType fromDefinition) (familyNames info)

/-- References for an atomic declaration unit, including every mutual-family member. -/
def semanticReferences (environment : Environment) (info : ConstantInfo) : Except String (Array Name) := do
  let mut references ← directSemanticReferences info
  if let .inductInfo value := info then
    for familyName in value.all do
      let some familyInfo := environment.find? familyName
        | .error s!"registry.closure.missing_inductive:{familyName}"
      references := appendUnique references (← directSemanticReferences familyInfo)
      let some (.inductInfo familyValue) := environment.find? familyName
        | .error s!"registry.closure.invalid_inductive:{familyName}"
      for constructor in familyValue.ctors do
        let some constructorInfo := environment.find? constructor
          | .error s!"registry.closure.missing_constructor:{constructor}"
        references := appendUnique references (← directSemanticReferences constructorInfo)
      let recursorName := familyName.str "rec"
      let some recursorInfo := environment.find? recursorName
        | .error s!"registry.closure.missing_recursor:{recursorName}"
      references := appendUnique references (← directSemanticReferences recursorInfo)
  sortNamesCanonical references

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
      for familyName in value.all do
        let some (.inductInfo familyInfo) := environment.find? familyName
          | .error s!"registry.closure.missing_inductive:{familyName}"
        if familyName != info.name then
          nodes := nodes + (← expressionStats familyInfo.levelParams familyInfo.type).1
        for constructor in familyInfo.ctors do
          let some (.ctorInfo constructorInfo) := environment.find? constructor
            | .error s!"registry.closure.missing_constructor:{constructor}"
          nodes := nodes + (← expressionStats constructorInfo.levelParams constructorInfo.type).1
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

private def typedConstructorJson
    (environment : Environment) (name : Name) : Except String Json := do
  let some (.ctorInfo value) := environment.find? name
    | .error s!"registry.closure.missing_constructor:{name}"
  let typeJson ← typedDeclarationExprJson value.levelParams value.type
  pure <| Json.mkObj [
    ("constructor_index", toJson value.cidx),
    ("level_parameters", .arr <| value.levelParams.toArray.map nameJson),
    ("name", nameJson value.name), ("num_fields", toJson value.numFields),
    ("num_parameters", toJson value.numParams), ("type", typeJson),
    ("unsafe", .bool value.isUnsafe)
  ]

private def typedRecursorJson
    (environment : Environment) (name : Name) : Except String Json := do
  let some (.recInfo value) := environment.find? name
    | .error s!"registry.closure.missing_recursor:{name}"
  let typeJson ← typedDeclarationExprJson value.levelParams value.type
  let mut rules := #[]
  for rule in value.rules do
    let rhs ← typedDeclarationExprJson value.levelParams rule.rhs
    rules := rules.push <| Json.mkObj [
      ("constructor", nameJson rule.ctor), ("field_count", toJson rule.nfields),
      ("rhs", rhs)
    ]
  pure <| Json.mkObj [
    ("family", nameArrayJson value.all), ("k_reduction", .bool value.k),
    ("level_parameters", .arr <| value.levelParams.toArray.map nameJson),
    ("name", nameJson value.name), ("num_indices", toJson value.numIndices),
    ("num_minors", toJson value.numMinors), ("num_motives", toJson value.numMotives),
    ("num_parameters", toJson value.numParams), ("rules", .arr rules),
    ("type", typeJson), ("unsafe", .bool value.isUnsafe)
  ]

private def inductiveMemberJson
    (environment : Environment) (name : Name) : Except String Json := do
  let some (.inductInfo value) := environment.find? name
    | .error s!"registry.closure.missing_inductive:{name}"
  let typeJson ← declarationExprJson value.levelParams maxExpressionDepth value.type
  let constructors ← value.ctors.mapM (constructorJson environment)
  pure <| Json.mkObj [
    ("constructors", .arr constructors.toArray),
    ("is_recursive", .bool value.isRec),
    ("is_reflexive", .bool value.isReflexive),
    ("level_parameters", .arr <| value.levelParams.toArray.map nameJson),
    ("name", nameJson value.name),
    ("num_indices", toJson value.numIndices),
    ("num_nested", toJson value.numNested),
    ("num_parameters", toJson value.numParams),
    ("type", typeJson),
    ("unsafe", .bool value.isUnsafe)
  ]

private def typedInductiveMemberJson
    (environment : Environment) (name : Name) : Except String Json := do
  let some (.inductInfo value) := environment.find? name
    | .error s!"registry.closure.missing_inductive:{name}"
  let typeJson ← typedDeclarationExprJson value.levelParams value.type
  let constructors ← value.ctors.mapM (typedConstructorJson environment)
  pure <| Json.mkObj [
    ("constructors", .arr constructors.toArray), ("is_recursive", .bool value.isRec),
    ("is_reflexive", .bool value.isReflexive),
    ("level_parameters", .arr <| value.levelParams.toArray.map nameJson),
    ("name", nameJson value.name), ("num_indices", toJson value.numIndices),
    ("num_nested", toJson value.numNested), ("num_parameters", toJson value.numParams),
    ("type", typeJson), ("unsafe", .bool value.isUnsafe)
  ]

/-- Emit one declaration's semantic closure record. -/
def closureRecordJson (environment : Environment) (info : ConstantInfo) : Except String Json := do
  let typeJson ← declarationExprJson info.levelParams maxExpressionDepth info.type
  let bodyJson ← bodyJson info
  let references ← semanticReferences environment info
  let (kind, extra) ← match info with
    | .inductInfo value =>
        let sortedFamily ← sortNamesCanonical value.all.toArray
        let members ← sortedFamily.toList.mapM (inductiveMemberJson environment)
        let recursors ← sortedFamily.toList.mapM (fun name => recursorJson environment (name.str "rec"))
        pure ("inductive_family", #[
          ("family", .arr <| sortedFamily.map nameJson),
          ("members", .arr members.toArray),
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

/--
Export the typed live declaration material from which an independent oracle
can derive references and reconstruct the canonical closure unit.
-/
def typedClosureUnitJson (environment : Environment) (info : ConstantInfo) : Except String Json := do
  let typeJson ← typedDeclarationExprJson info.levelParams info.type
  let bodyJson ← match info with
    | .defnInfo value => typedDeclarationExprJson value.levelParams value.value
    | _ => pure .null
  let (kind, extra) ← match info with
    | .inductInfo value =>
        let sortedFamily ← sortNamesCanonical value.all.toArray
        let members ← sortedFamily.toList.mapM (typedInductiveMemberJson environment)
        let recursors ← sortedFamily.toList.mapM (fun name => typedRecursorJson environment (name.str "rec"))
        pure ("inductive_family", #[
          ("family", .arr <| sortedFamily.map nameJson), ("members", .arr members.toArray),
          ("recursors", .arr recursors.toArray)
        ])
    | _ => pure (kindString info, #[])
  let base := [
    ("body", bodyJson), ("kind", .str kind),
    ("level_parameters", .arr <| info.levelParams.toArray.map nameJson),
    ("name", nameJson info.name), ("origin", .str <| originString info),
    ("reducibility", .str <| reducibilityString info),
    ("type", typeJson), ("unsafe", .bool info.isUnsafe)
  ]
  pure <| Json.mkObj (base ++ extra.toList)

private def inductiveFamilyRoot? (environment : Environment) (name : Name) : Option Name := do
  let info ← environment.find? name
  match info with
  | .inductInfo value => value.all.head?
  | .ctorInfo value =>
      let some (.inductInfo parent) := environment.find? value.induct | none
      parent.all.head?
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
    (work expressionNodes fuel workLimit : Nat) :
    Except String (Array (Name × Json) × Array Name × Nat × Nat) :=
  let current := canonicalUnitName environment current
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
  else if !closureDepthAllowed path.size then
    .error "registry.closure.depth_limit"
  else if !closureUnitCountAllowed (visited.size + 1) then
    .error "registry.closure.unit_limit"
  else match fuel with
    | 0 => .error "registry.closure.depth_limit"
    | fuel + 1 => do
        let some info := environment.find? current
          | .error s!"registry.closure.missing_dependency:{current}"
        if info.isUnsafe then
          .error s!"registry.closure.unsafe_declaration:{current}"
        let declarationNodes ← declarationExpressionNodes environment info
        let expressionNodes := expressionNodes + declarationNodes
        if expressionNodes > maxClosureExpressionNodes then
          .error "registry.closure.expression_node_limit"
        -- Every expression/level visit and declaration emission consumes work.
        let work := work + declarationNodes + 1
        if work > workLimit || !closureWorkAllowed work then
          .error "registry.closure.work_budget_limit"
        let record ← closureRecordJson environment info
        let mut records := #[(current, record)]
        let mut nextVisited := visited.push current
        let mut nextWork := work
        let mut nextExpressionNodes := expressionNodes
        let nextPath := path.push current
        let references ← semanticReferences environment info
        if references.size > maxClosureWidth then
          .error "registry.closure.width_limit"
        for reference in references do
          -- Count every attempted dependency edge, including duplicates.
          nextWork := nextWork + 1
          if nextWork > workLimit || !closureWorkAllowed nextWork then
            throw "registry.closure.work_budget_limit"
          let (nested, nestedVisited, nestedWork, nestedExpressionNodes) ←
            visitClosure environment reference nextPath nextVisited nextWork nextExpressionNodes fuel workLimit
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
def collectClosureNamedWithWorkLimit
    (environment : Environment) (roots : Array Name) (workLimit : Nat) :
    Except String (Array (Name × Json) × Nat × Nat) := do
  if roots.size > maxClosureRoots then
    .error "registry.closure.root_limit"
  let sortedRoots := roots.map (canonicalUnitName environment)
  let sortedRoots ← sortNamesCanonical sortedRoots
  let mut records := #[]
  let mut visited := #[]
  let mut work := 0
  let mut expressionNodes := 0
  for root in sortedRoots do
    let (nested, nestedVisited, nestedWork, nestedExpressionNodes) ←
      -- One extra fuel unit lets the explicit edge-depth check classify the
      -- first rejected node rather than relying on an implicit off-by-one.
      visitClosure environment root #[] visited work expressionNodes (maxClosureDepth + 2) workLimit
    records := records ++ nested
    visited := nestedVisited
    work := nestedWork
    expressionNodes := nestedExpressionNodes
  if !closureUnitCountAllowed records.size then
    .error "registry.closure.work_budget_limit"
  else
    let result := records.qsort (fun left right => canonicalNameLT left.1 right.1)
    if (Json.arr <| result.map (·.2)).compress.toUTF8.size > maxClosureObservationBytes then
      .error "registry.closure.output_limit"
    else
      pure (result, work, expressionNodes)

/-- Production closure collection at the normative fixed work limit. -/
def collectClosureNamed
    (environment : Environment) (roots : Array Name) :
    Except String (Array (Name × Json) × Nat × Nat) :=
  collectClosureNamedWithWorkLimit environment roots maxClosureWork

/-- Collect only the canonical declaration records. -/
def collectClosure
    (environment : Environment) (roots : Array Name) : Except String (Array Json) := do
  let (named, _, _) ← collectClosureNamed environment roots
  pure <| named.map (·.2)

/--
Collect canonical records together with independently consumable typed source
units from the same live environment.
-/
def collectClosureObservation
    (environment : Environment) (roots : Array Name) : Except String Json := do
  let (named, work, expressionNodes) ← collectClosureNamed environment roots
  let mut typedUnits := #[]
  for (name, _) in named do
    let some info := environment.find? name
      | .error s!"registry.closure.missing_dependency:{name}"
    typedUnits := typedUnits.push (← typedClosureUnitJson environment info)
  pure <| Json.mkObj [
    ("records", .arr <| named.map (·.2)),
    ("roots", .arr <| roots.map nameJson),
    ("typed_units", .arr typedUnits),
    ("work", toJson work),
    ("expression_level_visits", toJson expressionNodes)
  ]

/-- Roots referenced by the normalized proposition type. -/
def propositionRoots (type : Expr) : Array Name := namesIn type
  |> appendUnique (projectionNames (maxExpressionDepth + 1) type)
  |>.qsort canonicalNameLT

end StatQED.Registry
