import Lean

/-!
# Versioned structural observation of Lean propositions

This module emits an unambiguous typed JSON tree from the live Lean
environment. It performs no reduction. Binder names and expression metadata
are erased; binder information, de Bruijn indices, names, universes, literals,
and projections remain explicit.
-/

open Lean

namespace StatQED.Registry

/-- Version identifier for the test-only structural observation. -/
def normalizerVersion : String := "statqed.lean-proposition.v0"

/-- Maximum accepted expression nesting depth for the Lean-side extractor. -/
def maxExpressionDepth : Nat := 64

private def obj (fields : List (String × Json)) : Json := Json.mkObj fields

/-- Encode a Lean name without relying on pretty-printing for its structure. -/
def nameJson : Name → Json
  | .anonymous => obj [("tag", .str "anonymous")]
  | .str parent segment => obj [
      ("parent", nameJson parent),
      ("segment", .str segment),
      ("tag", .str "string")
    ]
  | .num parent segment => obj [
      ("parent", nameJson parent),
      ("segment", toJson segment),
      ("tag", .str "numeric")
    ]

/-- Encode a universe level structurally, rejecting metavariables. -/
def levelJson (fuel : Nat) : Level → Except String Json
  | level => match fuel with
    | 0 => .error "registry.normalization.level_depth_limit"
    | fuel + 1 => match level with
      | .zero => .ok <| obj [("tag", .str "zero")]
      | .succ inner => do
          let innerJson ← levelJson fuel inner
          pure <| obj [("level", innerJson), ("tag", .str "succ")]
      | .max left right => do
          let leftJson ← levelJson fuel left
          let rightJson ← levelJson fuel right
          pure <| obj [("left", leftJson), ("right", rightJson), ("tag", .str "max")]
      | .imax left right => do
          let leftJson ← levelJson fuel left
          let rightJson ← levelJson fuel right
          pure <| obj [("left", leftJson), ("right", rightJson), ("tag", .str "imax")]
      | .param name => .ok <| obj [("name", nameJson name), ("tag", .str "parameter")]
      | .mvar _ => .error "registry.normalization.universe_metavariable"

private def binderInfoString : BinderInfo → String
  | .default => "explicit"
  | .implicit => "implicit"
  | .strictImplicit => "strict_implicit"
  | .instImplicit => "instance_implicit"

private def levelsJson (levels : List Level) : Except String Json := do
  let encoded ← levels.mapM (levelJson maxExpressionDepth)
  pure <| .arr encoded.toArray

/--
Encode a kernel expression structurally. The fuel bounds depth. Free and meta
variables are rejected because registry subjects must be closed elaborated
declaration types.
-/
def exprJson (fuel : Nat) : Expr → Except String Json
  | expression => match fuel with
    | 0 => .error "registry.normalization.expression_depth_limit"
    | fuel + 1 => match expression with
      | .bvar index => .ok <| obj [("index", toJson index), ("tag", .str "bound_variable")]
      | .fvar _ => .error "registry.normalization.free_variable"
      | .mvar _ => .error "registry.normalization.expression_metavariable"
      | .sort level => do
          let levelJson ← levelJson maxExpressionDepth level
          pure <| obj [("level", levelJson), ("tag", .str "sort")]
      | .const name levels => do
          let encodedLevels ← levelsJson levels
          pure <| obj [
            ("name", nameJson name),
            ("tag", .str "constant"),
            ("universes", encodedLevels)
          ]
      | .app function argument => do
          let functionJson ← exprJson fuel function
          let argumentJson ← exprJson fuel argument
          pure <| obj [
            ("argument", argumentJson),
            ("function", functionJson),
            ("tag", .str "application")
          ]
      | .lam _ type body binderInfo => do
          let typeJson ← exprJson fuel type
          let bodyJson ← exprJson fuel body
          pure <| obj [
            ("binder_info", .str <| binderInfoString binderInfo),
            ("body", bodyJson),
            ("tag", .str "lambda"),
            ("type", typeJson)
          ]
      | .forallE _ type body binderInfo => do
          let typeJson ← exprJson fuel type
          let bodyJson ← exprJson fuel body
          pure <| obj [
            ("binder_info", .str <| binderInfoString binderInfo),
            ("body", bodyJson),
            ("tag", .str "forall"),
            ("type", typeJson)
          ]
      | .letE _ type value body _ => do
          let typeJson ← exprJson fuel type
          let valueJson ← exprJson fuel value
          let bodyJson ← exprJson fuel body
          pure <| obj [
            ("body", bodyJson),
            ("tag", .str "let"),
            ("type", typeJson),
            ("value", valueJson)
          ]
      | .lit (.natVal value) => .ok <| obj [
          ("kind", .str "natural"),
          ("tag", .str "literal"),
          ("value", .str value.repr)
        ]
      | .lit (.strVal value) => .ok <| obj [
          ("kind", .str "string"),
          ("tag", .str "literal"),
          ("value", .str value)
        ]
      | .mdata _ inner => exprJson fuel inner
      | .proj typeName index subject => do
          let structureJson ← exprJson fuel subject
          pure <| obj [
            ("index", toJson index),
            ("structure", structureJson),
            ("tag", .str "projection"),
            ("type_name", nameJson typeName)
          ]

/-- Encode a closed proposition type using the versioned structural grammar. -/
def propositionJson (type : Expr) : Except String Json := do
  let expression ← exprJson maxExpressionDepth type
  pure <| obj [
    ("expression", expression),
    ("normalizer", .str normalizerVersion)
  ]

end StatQED.Registry
