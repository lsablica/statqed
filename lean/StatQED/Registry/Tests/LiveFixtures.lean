import StatQED.Registry.Closure
import StatQED.Registry.Tests.Smoke

/-!
# Live cross-lineage registry fixtures

These fixtures are emitted from Lean's actual environment or from explicitly
constructed Lean `Expr`/`Level` values.  They retain a typed constructor tree
for the independent oracle and a separate primary-normalizer result.
-/

open Lean

namespace StatQED.Registry.Tests.LiveFixtures

open StatQED.Registry

private def declarationFixture
    (environment : Environment) (fixtureId : String) (name : Name) : Except String Json := do
  let some info := environment.find? name
    | .error s!"registry.fixture.missing_declaration:{name}"
  let typed ← typedDeclarationExprJson info.levelParams info.type
  let normalized ← propositionJson info.levelParams info.type
  pure <| Json.mkObj [
    ("declaration", .str name.toString), ("expected", .str "accepted"),
    ("fixture_id", .str fixtureId),
    ("level_parameters", .arr <| info.levelParams.toArray.map nameJson),
    ("normalized", normalized), ("typed_expression", typed)
  ]

private def nestedApplications (count : Nat) : Expr :=
  List.range count |>.foldl
    (fun expression _ => .app (.const `StatQED.Registry.Tests.liveMeaningBearingDefinition []) expression)
    (.const ``True [])

private def successorLevel (count : Nat) : Level :=
  List.range count |>.foldl (fun level _ => .succ level) .zero

private def normalizationFixture
    (fixtureId expected : String) (expression : Expr) (typedFuel : Nat) : Except String Json := do
  let typed ← typedExprJsonWithContext [] 0 typedFuel expression
  let result := propositionJson [] expression
  match expected, result with
  | "accepted", .ok normalized => pure <| Json.mkObj [
      ("expected", .str expected), ("fixture_id", .str fixtureId),
      ("level_parameters", .arr #[]), ("normalized", normalized),
      ("typed_expression", typed)
    ]
  | "rejected", .error code => pure <| Json.mkObj [
      ("code", .str code), ("expected", .str expected),
      ("fixture_id", .str fixtureId), ("level_parameters", .arr #[]),
      ("typed_expression", typed)
    ]
  | _, _ => .error s!"registry.fixture.unexpected_result:{fixtureId}"

private def levelBoundaryFixture
    (fixtureId expected : String) (successors : Nat) : Except String Json := do
  let level := successorLevel successors
  -- The typed export uses one extra unit only to retain the one-over input.
  let typedLevel ← levelJson [] (successors + 1) level
  let typed := Json.mkObj [("level", typedLevel), ("tag", .str "sort")]
  let result := propositionJson [] (.sort level)
  match expected, result with
  | "accepted", .ok normalized => pure <| Json.mkObj [
      ("expected", .str expected), ("fixture_id", .str fixtureId),
      ("level_parameters", .arr #[]), ("normalized", normalized),
      ("typed_expression", typed)
    ]
  | "rejected", .error code => pure <| Json.mkObj [
      ("code", .str code), ("expected", .str expected),
      ("fixture_id", .str fixtureId), ("level_parameters", .arr #[]),
      ("typed_expression", typed)
    ]
  | _, _ => .error s!"registry.fixture.unexpected_result:{fixtureId}"

private def closureFixture
    (environment : Environment) (fixtureId : String) (roots : Array Name)
    (requiredUnits : Array Name := #[]) : Except String Json := do
  let observation ← collectClosureObservation environment roots
  pure <| Json.mkObj [
    ("expected", .str "accepted"), ("fixture_id", .str fixtureId),
    ("observation", observation), ("required_units", .arr <| requiredUnits.map nameJson)
  ]

private def depthBoundaryFixture (environment : Environment) : Except String Json := do
  let accepted ← collectClosureObservation environment #[`StatQED.Registry.Tests.liveDepth63]
  let rejectionCode ← match collectClosureNamed environment #[`StatQED.Registry.Tests.liveDepthOver] with
    | .ok _ => .error "registry.fixture.depth_over_accepted"
    | .error code => pure code
  if rejectionCode != "registry.closure.depth_limit" then
    .error s!"registry.fixture.depth_wrong_error:{rejectionCode}"
  let some overInfo := environment.find? `StatQED.Registry.Tests.liveDepthOver
    | .error "registry.fixture.depth_over_missing"
  let overUnit ← typedClosureUnitJson environment overInfo
  pure <| Json.mkObj [
    ("accepted", accepted), ("accepted_root", nameJson `StatQED.Registry.Tests.liveDepth63),
    ("fixture_id", .str "LIVE-CLOSURE-DEPTH-BOUNDARY"),
    ("over_code", .str rejectionCode), ("over_root", nameJson `StatQED.Registry.Tests.liveDepthOver),
    ("over_typed_unit", overUnit)
  ]

private def workBoundaryFixture
    (environment : Environment) (root : Name) : Except String Json := do
  let roots := #[root]
  let (_, required, expressionVisits) ← collectClosureNamed environment roots
  let accepted := match collectClosureNamedWithWorkLimit environment roots required with
    | .ok _ => true
    | .error _ => false
  let oneUnder := required - 1
  let (rejected, code) := match collectClosureNamedWithWorkLimit environment roots oneUnder with
    | .ok _ => (false, "accepted")
    | .error code => (code == "registry.closure.work_budget_limit", code)
  if !accepted || !rejected then
    .error "registry.fixture.work_boundary_mismatch"
  pure <| Json.mkObj [
    ("accepted_at_required", .bool accepted), ("expression_level_visits", toJson expressionVisits),
    ("fixture_id", .str "LIVE-CLOSURE-WORK-BOUNDARY"),
    ("one_under_code", .str code), ("one_under_limit", toJson oneUnder),
    ("required_work", toJson required), ("root", nameJson root)
  ]

/-- Emit all live inputs and primary observations for independent comparison. -/
def report (environment : Environment) : Except String Json := do
  let expressionFixtures ← #[
    ("LIVE-UNIVERSE-BINDERS", `StatQED.Registry.Tests.liveUniverseBinderFixture),
    ("LIVE-PROJECTION", `StatQED.Registry.Tests.liveProjectionFixture),
    ("LIVE-NATURAL-LITERAL", `StatQED.Registry.Tests.liveNaturalLiteralFixture),
    ("LIVE-STRING-LITERAL", `StatQED.Registry.Tests.liveStringLiteralFixture),
    ("LIVE-LAMBDA", `StatQED.Registry.Tests.liveLambdaFixture),
    ("LIVE-LET", `StatQED.Registry.Tests.liveLetFixture)
  ].mapM fun (fixtureId, name) => declarationFixture environment fixtureId name
  let metadataBase ← normalizationFixture "LIVE-METADATA-BASE" "accepted"
    (.const ``True []) 1
  let metadata ← normalizationFixture "LIVE-METADATA-ERASURE" "accepted"
    (.mdata MData.empty (.const ``True [])) 2
  let lambdaConstructor ← normalizationFixture "LIVE-LAMBDA-CONSTRUCTOR" "accepted"
    (.lam `value (.const ``Nat []) (.bvar 0) .default) 3
  let letConstructor ← normalizationFixture "LIVE-LET-CONSTRUCTOR" "accepted"
    (.letE `value (.const ``Nat []) (.lit (.natVal 0)) (.bvar 0) false) 3
  let projectionConstructor ← normalizationFixture "LIVE-PROJECTION-CONSTRUCTOR" "accepted"
    (.proj `StatQED.Registry.Tests.LiveProjectionFixture 0
      (.const `StatQED.Registry.Tests.liveProjectionFixture [])) 2
  let depthMax ← normalizationFixture "LIVE-EXPRESSION-DEPTH-MAX" "accepted"
    (nestedApplications maxExpressionDepth) (maxExpressionDepth + 1)
  let depthOver ← normalizationFixture "LIVE-EXPRESSION-DEPTH-OVER" "rejected"
    (nestedApplications (maxExpressionDepth + 1)) (maxExpressionDepth + 2)
  let levelMax ← levelBoundaryFixture "LIVE-LEVEL-DEPTH-MAX" "accepted" maxLevelDepth
  let levelOver ← levelBoundaryFixture "LIVE-LEVEL-DEPTH-OVER" "rejected" (maxLevelDepth + 1)
  let closureFixtures ← #[
    ("LIVE-CLOSURE-TRUE-FAMILY", #[``True], #[]),
    ("LIVE-CLOSURE-DEFINITION", #[`StatQED.Registry.Tests.liveDefinitionReferenceFixture], #[]),
    ("LIVE-CLOSURE-SELECTED-INSTANCE", #[`StatQED.Registry.Tests.liveSelectedInstanceFixture],
      #[`StatQED.Registry.Tests.liveSelectedInstance]),
    ("LIVE-CLOSURE-MUTUAL-FAMILY", #[`StatQED.Registry.Tests.LiveMutualLeft], #[])
  ].mapM fun (fixtureId, roots, requiredUnits) =>
    closureFixture environment fixtureId roots requiredUnits
  let depthBoundary ← depthBoundaryFixture environment
  let workBoundary ← workBoundaryFixture environment ``True
  pure <| Json.mkObj [
    ("closure_fixtures", .arr closureFixtures),
    ("depth_boundary", depthBoundary),
    ("expression_fixtures", .arr <| expressionFixtures ++ #[metadataBase, metadata,
      lambdaConstructor, letConstructor, projectionConstructor, depthMax, depthOver, levelMax, levelOver]),
    ("schema", .str "statqed.registry-live-fixtures.v0"),
    ("work_boundary", workBoundary)
  ]

end StatQED.Registry.Tests.LiveFixtures
