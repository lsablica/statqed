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
def maxClosureRecords : Nat := 4096

private def namesIn (expression : Expr) : Array Name :=
  expression.getUsedConstants.qsort (fun left right => left.toString < right.toString)

private def appendUnique (names more : Array Name) : Array Name :=
  more.foldl (fun acc name => if acc.contains name then acc else acc.push name) names

private def familyNames : ConstantInfo → Array Name
  | .inductInfo value =>
      (value.all ++ value.ctors).toArray
  | .ctorInfo value => #[value.induct]
  | .recInfo value => value.all.toArray ++ value.rules.toArray.map (·.ctor)
  | _ => #[]

/-- References that carry semantic meaning for a declaration record. -/
def semanticReferences (info : ConstantInfo) : Array Name :=
  let fromType := namesIn info.type
  let fromDefinition := match info with
    | .defnInfo value => namesIn value.value
    | .recInfo value =>
        value.rules.foldl (fun names rule => appendUnique names (namesIn rule.rhs)) #[]
    | _ => #[]
  appendUnique (appendUnique fromType fromDefinition) (familyNames info)
    |>.qsort (fun left right => left.toString < right.toString)

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
  | .defnInfo value => exprJson maxExpressionDepth value.value
  | _ => .ok .null

/-- Emit one declaration's semantic closure record. -/
def closureRecordJson (info : ConstantInfo) : Except String Json := do
  let typeJson ← exprJson maxExpressionDepth info.type
  let bodyJson ← bodyJson info
  let references := semanticReferences info
  pure <| Json.mkObj [
    ("body", bodyJson),
    ("kind", .str <| kindString info),
    ("level_parameters", .arr <| info.levelParams.toArray.map nameJson),
    ("name", nameJson info.name),
    ("reducibility", .str <| reducibilityString info),
    ("references", .arr <| references.map nameJson),
    ("type", typeJson),
    ("unsafe", .bool info.isUnsafe)
  ]

private def inductiveFamilyRoot? (environment : Environment) (name : Name) : Option Name := do
  let info ← environment.find? name
  match info with
  | .inductInfo value => value.all.head?
  | .ctorInfo value => some value.induct
  | .recInfo value => value.all.head?
  | _ => none

private def sameInductiveFamily
    (environment : Environment) (left right : Name) : Bool :=
  match inductiveFamilyRoot? environment left, inductiveFamilyRoot? environment right with
  | some leftRoot, some rightRoot => leftRoot == rightRoot
  | _, _ => false

private def visitClosure
    (environment : Environment)
    (current : Name)
    (path visited : Array Name)
    (fuel : Nat) : Except String (Array (Name × Json) × Array Name) :=
  if path.contains current then
    match path.back? with
    | some parent =>
        if sameInductiveFamily environment parent current then
          .ok (#[], visited)
        else
          .error s!"registry.closure.cycle:{current}"
    | none => .error s!"registry.closure.cycle:{current}"
  else if visited.contains current then
    .ok (#[], visited)
  else match fuel with
    | 0 => .error "registry.closure.depth_limit"
    | fuel + 1 => do
        let some info := environment.find? current
          | .error s!"registry.closure.missing_dependency:{current}"
        if info.isUnsafe then
          .error s!"registry.closure.unsafe_declaration:{current}"
        let record ← closureRecordJson info
        let mut records := #[(current, record)]
        let mut nextVisited := visited.push current
        let nextPath := path.push current
        for reference in semanticReferences info do
          let (nested, nestedVisited) ←
            visitClosure environment reference nextPath nextVisited fuel
          records := records ++ nested
          nextVisited := nestedVisited
        pure (records, nextVisited)
termination_by fuel

/--
Collect a deterministic transitive closure with an explicit record budget.
Missing declarations and cycles through the active recursion path fail closed.
-/
def collectClosure
    (environment : Environment) (roots : Array Name) : Except String (Array Json) := do
  let sortedRoots := roots.qsort (fun left right => left.toString < right.toString)
  let mut records := #[]
  let mut visited := #[]
  for root in sortedRoots do
    let (nested, nestedVisited) ←
      visitClosure environment root #[] visited maxClosureRecords
    records := records ++ nested
    visited := nestedVisited
  if records.size > maxClosureRecords then
    .error "registry.closure.work_budget_limit"
  else
    pure <| records
      |>.qsort (fun left right => left.1.toString < right.1.toString)
      |>.map (·.2)

/-- Roots referenced by the normalized proposition type. -/
def propositionRoots (type : Expr) : Array Name := namesIn type

end StatQED.Registry
