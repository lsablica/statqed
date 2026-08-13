import StatQED.Registry.Closure

/-!
# Registry extractor boundary constants

These compile-time checks bind the Lean implementation to the reviewed v0
normalizer and closure identifiers and resource constants. Adversarial value
construction and maximum/one-over behavior are exercised by the independent
language-neutral conformance corpus.
-/

namespace StatQED.Registry.Tests.Bounds

open StatQED.Registry

example : normalizerVersion = "statqed.lean-expr.v0" := rfl
example : maxExpressionDepth = 256 := rfl
example : maxLevelDepth = 64 := rfl
example : maxExpressionNodes = 65536 := rfl
example : maxUniverseArguments = 256 := rfl
example : maxNameSegments = 64 := rfl
example : maxNameSegmentBytes = 256 := rfl
example : maxQualifiedNameBytes = 1024 := rfl
example : maxStringLiteralBytes = 65536 := rfl
example : maxAggregateStringBytes = 262144 := rfl
example : maxUnsignedInteger = 18446744073709551615 := rfl

example : closureVersion = "statqed.lean-environment-closure.v0" := rfl
example : maxClosureRoots = 256 := rfl
example : maxClosureUnits = 1024 := rfl
example : maxClosureWidth = 256 := rfl
example : maxClosureDepth = 64 := rfl
example : maxClosureWork = 1000000 := rfl
example : maxClosureExpressionNodes = 262144 := rfl

#guard closureDepthAllowed maxClosureDepth
#guard !closureDepthAllowed (maxClosureDepth + 1)
#guard closureUnitCountAllowed maxClosureUnits
#guard !closureUnitCountAllowed (maxClosureUnits + 1)
#guard closureWorkAllowed maxClosureWork
#guard !closureWorkAllowed (maxClosureWork + 1)

#guard match propositionJson [] (.lit (.natVal maxUnsignedInteger)) with
  | .ok _ => true
  | _ => false

#guard match propositionJson [] (.lit (.natVal (maxUnsignedInteger + 1))) with
  | .error "registry.normalization_failure" => true
  | _ => false

#guard match exprJson maxExpressionDepth (.bvar 0) with
  | .error "registry.normalization.loose_bound_variable" => true
  | _ => false

#guard match declarationExprJson [`u] maxExpressionDepth (.sort (.param `v)) with
  | .error "registry.normalization.undeclared_universe_parameter" => true
  | _ => false

private def nestedApplications (count : Nat) : Lean.Expr :=
  List.range count |>.foldl
    (fun expression _ => Lean.Expr.app (Lean.Expr.const `f []) expression)
    (Lean.Expr.const `x [])

private def successorLevel (count : Nat) : Lean.Level :=
  List.range count |>.foldl (fun level _ => Lean.Level.succ level) Lean.Level.zero

#guard match propositionJson [] (nestedApplications maxExpressionDepth) with
  | .ok _ => true
  | _ => false

#guard match propositionJson [] (nestedApplications (maxExpressionDepth + 1)) with
  | .error "registry.normalization.expression_depth_limit" => true
  | _ => false

#guard match propositionJson [] (.sort <| successorLevel maxLevelDepth) with
  | .ok _ => true
  | _ => false

#guard match propositionJson [] (.sort <| successorLevel (maxLevelDepth + 1)) with
  | .error "registry.normalization.level_depth_limit" => true
  | _ => false

-- Canonical CBOR name-byte ordering is length-first for these text segments;
-- it deliberately differs from ordinary lexical `Name` ordering.
#guard canonicalNameLT `b `aa
#guard !canonicalNameLT `aa `b

end StatQED.Registry.Tests.Bounds
