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
def normalizerVersion : String := "statqed.lean-expr.v0"

/-- Maximum accepted expression nesting depth for the Lean-side extractor. -/
def maxExpressionDepth : Nat := 256
def maxLevelDepth : Nat := 64
def maxExpressionNodes : Nat := 65536
def maxUniverseArguments : Nat := 256
def maxNameSegments : Nat := 64
def maxNameSegmentBytes : Nat := 256
def maxQualifiedNameBytes : Nat := 1024
def maxStringLiteralBytes : Nat := 65536
def maxAggregateStringBytes : Nat := 262144
def maxObservationBytes : Nat := 1048576
def maxUnsignedInteger : Nat := 18446744073709551615

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

private def nameStats : Name → Nat × Nat
  | .anonymous => (0, 0)
  | .str parent segment =>
      let (segments, bytes) := nameStats parent
      (segments + 1, bytes + segment.toUTF8.size)
  | .num parent _ =>
      let (segments, bytes) := nameStats parent
      (segments + 1, bytes)

private def checkedNameJson (name : Name) : Except String Json := do
  let (segments, bytes) := nameStats name
  if segments == 0 then
    .error "registry.normalization.anonymous_name"
  else if segments > maxNameSegments then
    .error "registry.normalization.name_segment_limit"
  else if bytes > maxQualifiedNameBytes then
    .error "registry.normalization.name_byte_limit"
  else
    let rec checkSegments : Name → Except String Unit
      | .anonymous => .ok ()
      | .str parent segment => do
          if segment.toUTF8.size > maxNameSegmentBytes then
            .error "registry.normalization.name_segment_byte_limit"
          else
            checkSegments parent
      | .num parent segment =>
          if segment > maxUnsignedInteger then
            .error "registry.normalization_failure"
          else
            checkSegments parent
    checkSegments name
    pure <| nameJson name

private def uintHeadBytes (major value : Nat) : ByteArray :=
  let first := major * 32
  if value < 24 then
    ByteArray.empty.push (UInt8.ofNat (first + value))
  else if value < 256 then
    (ByteArray.empty.push (UInt8.ofNat (first + 24))).push (UInt8.ofNat value)
  else if value < 65536 then
    ((ByteArray.empty.push (UInt8.ofNat (first + 25))).push
      (UInt8.ofNat (value / 256))).push (UInt8.ofNat value)
  else if value < 4294967296 then
    let result := ByteArray.empty.push (UInt8.ofNat (first + 26))
    let result := result.push (UInt8.ofNat (value / 16777216))
    let result := result.push (UInt8.ofNat (value / 65536))
    let result := result.push (UInt8.ofNat (value / 256))
    result.push (UInt8.ofNat value)
  else
    let result := ByteArray.empty.push (UInt8.ofNat (first + 27))
    let result := result.push (UInt8.ofNat (value / 72057594037927936))
    let result := result.push (UInt8.ofNat (value / 281474976710656))
    let result := result.push (UInt8.ofNat (value / 1099511627776))
    let result := result.push (UInt8.ofNat (value / 4294967296))
    let result := result.push (UInt8.ofNat (value / 16777216))
    let result := result.push (UInt8.ofNat (value / 65536))
    let result := result.push (UInt8.ofNat (value / 256))
    result.push (UInt8.ofNat value)

private def canonicalNameParts : Name → Except String (Nat × ByteArray)
  | .anonymous => .ok (0, ByteArray.empty)
  | .str parent segment => do
      let (count, beforeBytes) ← canonicalNameParts parent
      let raw := segment.toUTF8
      if raw.size > maxNameSegmentBytes then
        .error "registry.normalization.name_segment_byte_limit"
      let item := ((ByteArray.empty.push 0x82).push 0x00) ++ uintHeadBytes 3 raw.size ++ raw
      pure (count + 1, beforeBytes ++ item)
  | .num parent segment => do
      let (count, beforeBytes) ← canonicalNameParts parent
      if segment >= 18446744073709551616 then
        .error "registry.normalization.name_numeric_limit"
      let item := ((ByteArray.empty.push 0x82).push 0x01) ++ uintHeadBytes 0 segment
      pure (count + 1, beforeBytes ++ item)

/-- Canonical CBOR bytes of the language-neutral name-segment array. -/
def canonicalNameBytes (name : Name) : Except String ByteArray := do
  let _ ← checkedNameJson name
  let (count, parts) ← canonicalNameParts name
  pure <| uintHeadBytes 4 count ++ parts

private def byteListLT : List UInt8 → List UInt8 → Bool
  | [], [] => false
  | [], _ :: _ => true
  | _ :: _, [] => false
  | left :: leftRest, right :: rightRest =>
      if left < right then true
      else if right < left then false
      else byteListLT leftRest rightRest

/-- Ordering predicate for exact canonical name bytes. -/
def canonicalNameLT (left right : Name) : Bool :=
  match canonicalNameBytes left, canonicalNameBytes right with
  | .ok leftBytes, .ok rightBytes => byteListLT leftBytes.data.toList rightBytes.data.toList
  | _, _ => false

/-- Encode a universe level structurally, rejecting metavariables. -/
def levelJson (parameters : List Name) (fuel : Nat) : Level → Except String Json
  | level => match fuel with
    | 0 => .error "registry.normalization.level_depth_limit"
    | fuel + 1 => match level with
      | .zero => .ok <| obj [("tag", .str "zero")]
      | .succ inner => do
          let innerJson ← levelJson parameters fuel inner
          pure <| obj [("level", innerJson), ("tag", .str "succ")]
      | .max left right => do
          let leftJson ← levelJson parameters fuel left
          let rightJson ← levelJson parameters fuel right
          pure <| obj [("left", leftJson), ("right", rightJson), ("tag", .str "max")]
      | .imax left right => do
          let leftJson ← levelJson parameters fuel left
          let rightJson ← levelJson parameters fuel right
          pure <| obj [("left", leftJson), ("right", rightJson), ("tag", .str "imax")]
      | .param name => do
          if !parameters.contains name then
            .error "registry.normalization.undeclared_universe_parameter"
          else
            let encoded ← checkedNameJson name
            .ok <| obj [("name", encoded), ("tag", .str "parameter")]
      | .mvar _ => .error "registry.normalization.universe_metavariable"
termination_by fuel

private def binderInfoString : BinderInfo → String
  | .default => "explicit"
  | .implicit => "implicit"
  | .strictImplicit => "strict_implicit"
  | .instImplicit => "instance_implicit"

private def levelsJson (parameters : List Name) (levels : List Level) : Except String Json := do
  if levels.length > maxUniverseArguments then
    .error "registry.normalization.universe_argument_limit"
  let encoded ← levels.mapM (levelJson parameters (maxLevelDepth + 1))
  pure <| .arr encoded.toArray

private def combineStats (left right : Nat × Nat) : Nat × Nat :=
  (left.1 + right.1, left.2 + right.2)

private def levelStats (parameters : List Name) (fuel : Nat) : Level → Except String (Nat × Nat)
  | level => match fuel with
    | 0 => .error "registry.normalization.level_depth_limit"
    | fuel + 1 => match level with
      | .zero => .ok (1, 0)
      | .succ inner => do
          let stats ← levelStats parameters fuel inner
          pure (stats.1 + 1, stats.2)
      | .max left right | .imax left right => do
          let leftStats ← levelStats parameters fuel left
          let rightStats ← levelStats parameters fuel right
          let combined := combineStats leftStats rightStats
          pure (combined.1 + 1, combined.2)
      | .param name => do
          if !parameters.contains name then
            .error "registry.normalization.undeclared_universe_parameter"
          else
            let (segments, bytes) := nameStats name
            if segments == 0 || segments > maxNameSegments || bytes > maxQualifiedNameBytes then
              .error "registry.normalization.name_limit"
            else
              pure (1, bytes)
      | .mvar _ => .error "registry.normalization.universe_metavariable"
termination_by fuel

private def exprStats
    (parameters : List Name) (bound fuel : Nat) : Expr → Except String (Nat × Nat)
  | expression => match fuel with
    | 0 => .error "registry.normalization.expression_depth_limit"
    | fuel + 1 => match expression with
      | .bvar index =>
          if index < bound then .ok (1, 0)
          else .error "registry.normalization.loose_bound_variable"
      | .fvar _ => .error "registry.normalization.free_variable"
      | .mvar _ => .error "registry.normalization.expression_metavariable"
      | .sort level => do
          let stats ← levelStats parameters (maxLevelDepth + 1) level
          pure (stats.1 + 1, stats.2)
      | .const name levels => do
          if levels.length > maxUniverseArguments then
            .error "registry.normalization.universe_argument_limit"
          let (segments, nameBytes) := nameStats name
          if segments == 0 || segments > maxNameSegments || nameBytes > maxQualifiedNameBytes then
            .error "registry.normalization.name_limit"
          let mut stats := (1, nameBytes)
          for level in levels do
            stats := combineStats stats (← levelStats parameters (maxLevelDepth + 1) level)
          pure stats
      | .app function argument => do
          let functionStats ← exprStats parameters bound fuel function
          let argumentStats ← exprStats parameters bound fuel argument
          let combined := combineStats functionStats argumentStats
          pure (combined.1 + 1, combined.2)
      | .lam _ type body _ | .forallE _ type body _ => do
          let typeStats ← exprStats parameters bound fuel type
          let bodyStats ← exprStats parameters (bound + 1) fuel body
          let combined := combineStats typeStats bodyStats
          pure (combined.1 + 1, combined.2)
      | .letE _ type value body _ => do
          let typeStats ← exprStats parameters bound fuel type
          let valueStats ← exprStats parameters bound fuel value
          let bodyStats ← exprStats parameters (bound + 1) fuel body
          let combined := combineStats (combineStats typeStats valueStats) bodyStats
          pure (combined.1 + 1, combined.2)
      | .lit (.natVal value) =>
          if value > maxUnsignedInteger then
            .error "registry.normalization_failure"
          else .ok (1, 0)
      | .lit (.strVal value) =>
          if value.toUTF8.size > maxStringLiteralBytes then
            .error "registry.normalization.string_literal_limit"
          else
            .ok (1, value.toUTF8.size)
      | .mdata _ inner => exprStats parameters bound fuel inner
      | .proj typeName index subject => do
          if index > maxUnsignedInteger then
            .error "registry.normalization_failure"
          let (segments, nameBytes) := nameStats typeName
          if segments == 0 || segments > maxNameSegments || nameBytes > maxQualifiedNameBytes then
            .error "registry.normalization.name_limit"
          let subjectStats ← exprStats parameters bound fuel subject
          pure (subjectStats.1 + 1, subjectStats.2 + nameBytes)
termination_by fuel

/-- Return the bounded expression/level-node and UTF-8 string totals. -/
def expressionStats
    (levelParameters : List Name) (expression : Expr) : Except String (Nat × Nat) :=
  exprStats levelParameters 0 (maxExpressionDepth + 1) expression

/--
Encode a kernel expression structurally. The fuel bounds depth. Free and meta
variables are rejected because registry subjects must be closed elaborated
declaration types.
-/
def exprJsonWithContext
    (parameters : List Name) (bound fuel : Nat) : Expr → Except String Json
  | expression => match fuel with
    | 0 => .error "registry.normalization.expression_depth_limit"
    | fuel + 1 => match expression with
      | .bvar index =>
          if index < bound then
            .ok <| obj [("index", toJson index), ("tag", .str "bound_variable")]
          else
            .error "registry.normalization.loose_bound_variable"
      | .fvar _ => .error "registry.normalization.free_variable"
      | .mvar _ => .error "registry.normalization.expression_metavariable"
      | .sort level => do
          let levelJson ← levelJson parameters (maxLevelDepth + 1) level
          pure <| obj [("level", levelJson), ("tag", .str "sort")]
      | .const name levels => do
          let encodedName ← checkedNameJson name
          let encodedLevels ← levelsJson parameters levels
          pure <| obj [
            ("name", encodedName),
            ("tag", .str "constant"),
            ("universes", encodedLevels)
          ]
      | .app function argument => do
          let functionJson ← exprJsonWithContext parameters bound fuel function
          let argumentJson ← exprJsonWithContext parameters bound fuel argument
          pure <| obj [
            ("argument", argumentJson),
            ("function", functionJson),
            ("tag", .str "application")
          ]
      | .lam _ type body binderInfo => do
          let typeJson ← exprJsonWithContext parameters bound fuel type
          let bodyJson ← exprJsonWithContext parameters (bound + 1) fuel body
          pure <| obj [
            ("binder_info", .str <| binderInfoString binderInfo),
            ("body", bodyJson),
            ("tag", .str "lambda"),
            ("type", typeJson)
          ]
      | .forallE _ type body binderInfo => do
          let typeJson ← exprJsonWithContext parameters bound fuel type
          let bodyJson ← exprJsonWithContext parameters (bound + 1) fuel body
          pure <| obj [
            ("binder_info", .str <| binderInfoString binderInfo),
            ("body", bodyJson),
            ("tag", .str "forall"),
            ("type", typeJson)
          ]
      | .letE _ type value body _ => do
          let typeJson ← exprJsonWithContext parameters bound fuel type
          let valueJson ← exprJsonWithContext parameters bound fuel value
          let bodyJson ← exprJsonWithContext parameters (bound + 1) fuel body
          pure <| obj [
            ("body", bodyJson),
            ("tag", .str "let"),
            ("type", typeJson),
            ("value", valueJson)
          ]
      | .lit (.natVal value) =>
          if value > maxUnsignedInteger then
            .error "registry.normalization_failure"
          else .ok <| obj [
            ("kind", .str "natural"), ("tag", .str "literal"),
            ("value", .str value.repr)
          ]
      | .lit (.strVal value) =>
          if value.toUTF8.size > maxStringLiteralBytes then
            .error "registry.normalization.string_literal_limit"
          else
            .ok <| obj [
              ("kind", .str "string"),
              ("tag", .str "literal"),
              ("value", .str value)
            ]
      | .mdata _ inner => exprJsonWithContext parameters bound fuel inner
      | .proj typeName index subject => do
          if index > maxUnsignedInteger then
            .error "registry.normalization_failure"
          let encodedName ← checkedNameJson typeName
          let structureJson ← exprJsonWithContext parameters bound fuel subject
          pure <| obj [
            ("index", toJson index),
            ("structure", structureJson),
            ("tag", .str "projection"),
            ("type_name", encodedName)
          ]
termination_by fuel

/-- Encode a closed expression under an explicit declaration-universe context. -/
def declarationExprJson
    (levelParameters : List Name) (fuel : Nat) (expression : Expr) : Except String Json := do
  if levelParameters.length > maxUniverseArguments then
    .error "registry.normalization.universe_argument_limit"
  let encodedParameters ← levelParameters.mapM checkedNameJson
  if encodedParameters.eraseDups.length != encodedParameters.length then
    .error "registry.normalization.duplicate_universe_parameter"
  let (nodes, stringBytes) ← exprStats levelParameters 0 (fuel + 1) expression
  if nodes > maxExpressionNodes || stringBytes > maxAggregateStringBytes then
    .error "registry.normalization.resource_limit"
  else
    exprJsonWithContext levelParameters 0 (fuel + 1) expression

/-- Encode a closed expression with no universe parameters. -/
def exprJson (fuel : Nat) (expression : Expr) : Except String Json :=
  declarationExprJson [] fuel expression

/--
Export the live typed constructor tree for an independent normalizer. Unlike
`exprJsonWithContext`, this retains binder display names, `letE.nondep`, and
the presence (but not the implementation-specific payload) of metadata nodes.
It applies the same finite depth, scoping, universe, name, and string bounds.
-/
def typedExprJsonWithContext
    (parameters : List Name) (bound fuel : Nat) : Expr → Except String Json
  | expression => match fuel with
    | 0 => .error "registry.normalization.expression_depth_limit"
    | fuel + 1 => match expression with
      | .bvar index =>
          if index < bound then
            .ok <| obj [("index", toJson index), ("tag", .str "bound_variable")]
          else .error "registry.normalization.loose_bound_variable"
      | .fvar _ => .error "registry.normalization.free_variable"
      | .mvar _ => .error "registry.normalization.expression_metavariable"
      | .sort level => do
          let encoded ← levelJson parameters (maxLevelDepth + 1) level
          pure <| obj [("level", encoded), ("tag", .str "sort")]
      | .const name levels => do
          let encodedName ← checkedNameJson name
          let encodedLevels ← levelsJson parameters levels
          pure <| obj [
            ("name", encodedName), ("tag", .str "constant"),
            ("universes", encodedLevels)
          ]
      | .app function argument => do
          let functionJson ← typedExprJsonWithContext parameters bound fuel function
          let argumentJson ← typedExprJsonWithContext parameters bound fuel argument
          pure <| obj [
            ("argument", argumentJson), ("function", functionJson),
            ("tag", .str "application")
          ]
      | .lam binderName type body binderInfo => do
          let typeJson ← typedExprJsonWithContext parameters bound fuel type
          let bodyJson ← typedExprJsonWithContext parameters (bound + 1) fuel body
          pure <| obj [
            ("binder_info", .str <| binderInfoString binderInfo),
            ("binder_name", .str binderName.toString), ("body", bodyJson),
            ("tag", .str "lambda"), ("type", typeJson)
          ]
      | .forallE binderName type body binderInfo => do
          let typeJson ← typedExprJsonWithContext parameters bound fuel type
          let bodyJson ← typedExprJsonWithContext parameters (bound + 1) fuel body
          pure <| obj [
            ("binder_info", .str <| binderInfoString binderInfo),
            ("binder_name", .str binderName.toString), ("body", bodyJson),
            ("tag", .str "forall"), ("type", typeJson)
          ]
      | .letE binderName type value body nondep => do
          let typeJson ← typedExprJsonWithContext parameters bound fuel type
          let valueJson ← typedExprJsonWithContext parameters bound fuel value
          let bodyJson ← typedExprJsonWithContext parameters (bound + 1) fuel body
          pure <| obj [
            ("binder_name", .str binderName.toString), ("body", bodyJson),
            ("nondep", .bool nondep), ("tag", .str "let"),
            ("type", typeJson), ("value", valueJson)
          ]
      | .lit (.natVal value) => .ok <| obj [
          ("kind", .str "natural"), ("tag", .str "literal"),
          ("value", .str value.repr)
        ]
      | .lit (.strVal value) =>
          if value.toUTF8.size > maxStringLiteralBytes then
            .error "registry.normalization.string_literal_limit"
          else .ok <| obj [
            ("kind", .str "string"), ("tag", .str "literal"),
            ("value", .str value)
          ]
      | .mdata _ inner => do
          let innerJson ← typedExprJsonWithContext parameters bound fuel inner
          pure <| obj [
            ("expression", innerJson), ("metadata", .str "present"),
            ("tag", .str "metadata")
          ]
      | .proj typeName index subject => do
          let encodedName ← checkedNameJson typeName
          let structureJson ← typedExprJsonWithContext parameters bound fuel subject
          pure <| obj [
            ("index", toJson index), ("structure", structureJson),
            ("tag", .str "projection"), ("type_name", encodedName)
          ]
termination_by fuel

/-- Bounded typed observation for one closed declaration expression. -/
def typedDeclarationExprJson
    (levelParameters : List Name) (expression : Expr) : Except String Json := do
  let (nodes, stringBytes) ← exprStats levelParameters 0 (maxExpressionDepth + 1) expression
  if nodes > maxExpressionNodes || stringBytes > maxAggregateStringBytes then
    .error "registry.normalization.resource_limit"
  typedExprJsonWithContext levelParameters 0 (maxExpressionDepth + 1) expression

/-- Encode a closed proposition type using the versioned structural grammar. -/
def propositionJson (levelParameters : List Name) (type : Expr) : Except String Json := do
  if levelParameters.length > maxUniverseArguments then
    .error "registry.normalization.universe_argument_limit"
  let encodedParameters ← levelParameters.mapM checkedNameJson
  if encodedParameters.eraseDups.length != encodedParameters.length then
    .error "registry.normalization.duplicate_universe_parameter"
  let (nodes, stringBytes) ← exprStats levelParameters 0 (maxExpressionDepth + 1) type
  if nodes > maxExpressionNodes || stringBytes > maxAggregateStringBytes then
    .error "registry.normalization.resource_limit"
  let expression ← exprJsonWithContext levelParameters 0 (maxExpressionDepth + 1) type
  let result := obj [
    ("expression", expression),
    ("level_parameters", .arr encodedParameters.toArray),
    ("normalizer", .str normalizerVersion)
  ]
  if result.compress.toUTF8.size > maxObservationBytes then
    .error "registry.normalization.output_limit"
  else
    pure result

end StatQED.Registry
