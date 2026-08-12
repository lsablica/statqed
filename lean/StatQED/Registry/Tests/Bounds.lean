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

example : closureVersion = "statqed.lean-environment-closure.v0" := rfl
example : maxClosureRoots = 256 := rfl
example : maxClosureUnits = 1024 := rfl
example : maxClosureWidth = 256 := rfl
example : maxClosureDepth = 64 := rfl
example : maxClosureWork = 1000000 := rfl
example : maxClosureExpressionNodes = 262144 := rfl

#guard match exprJson maxExpressionDepth (.bvar 0) with
  | .error "registry.normalization.loose_bound_variable" => true
  | _ => false

#guard match declarationExprJson [`u] maxExpressionDepth (.sort (.param `v)) with
  | .error "registry.normalization.undeclared_universe_parameter" => true
  | _ => false

end StatQED.Registry.Tests.Bounds
