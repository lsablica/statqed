import Mathlib.Data.Set.Defs

/-!
# Test-only theorem-registry declarations

These declarations exercise extraction, axiom observation, kernel replay, and
directional compatibility. They are not public statistical theorems and are
not non-vacuity witnesses.
-/

namespace StatQED.Registry.Tests

/-- Definitionally trivial, test-only registry proposition from ADR-0011. -/
theorem testOnlyTrue : True := by
  trivial

/-- A proof-only refactor fixture with the same proposition as `testOnlyTrue`. -/
theorem testOnlyTrueRefactor : True := (fun (_ : Unit) => True.intro) ()

/--
Directional compatibility fixture: new, stronger material (`False`) implies
the old required proposition (`True`). The reverse direction is deliberately
not asserted.
-/
theorem falseImpliesTrue : False → True := fun impossible => False.elim impossible

/-- Live universe/binder fixture; it is observation-only and not registered. -/
theorem liveUniverseBinderFixture.{u}
    {α : Sort u} (_explicit : α) {_implicit : α} ⦃_strict : α⦄
    [_instanceArg : Inhabited α] : True := by
  trivial

/-- Structure used to force a live `Expr.proj` into a declaration type. -/
structure LiveProjectionFixture where
  value : Nat

/-- Live projection fixture; observation-only. -/
theorem liveProjectionFixture (input : LiveProjectionFixture) :
    input.value = input.value := rfl

/-- Live natural-literal fixture; observation-only. -/
theorem liveNaturalLiteralFixture : (37 : Nat) = 37 := rfl

/-- Live string-literal fixture; observation-only. -/
theorem liveStringLiteralFixture : "registry" = "registry" := rfl

/-- Live lambda fixture; observation-only. -/
theorem liveLambdaFixture :
    (fun value : Nat => value) = (fun value : Nat => value) := rfl

/-- Live let-expression fixture; observation-only. -/
theorem liveLetFixture : (let proposition : Prop := True; proposition) := by
  trivial

/-- Live definition-body closure fixture; observation-only. -/
def liveMeaningBearingDefinition : Nat := 37

/-- Live definition-reference closure fixture; observation-only. -/
theorem liveDefinitionReferenceFixture : liveMeaningBearingDefinition = 37 := rfl

/-- Project-local class used to observe a selected instance constant. -/
class LiveSelectedInstance where
  selected : Nat

/-- The uniquely selected project-local instance. -/
instance liveSelectedInstance : LiveSelectedInstance := ⟨37⟩

/-- Live selected-instance body fixture; observation-only. -/
def liveSelectedInstanceFixture : Nat := LiveSelectedInstance.selected

/-- Live closure-depth chain unit 00; observation-only. -/
def liveDepth00 : Prop := True
/-- Live closure-depth chain unit 01; observation-only. -/
def liveDepth01 : Prop := liveDepth00
/-- Live closure-depth chain unit 02; observation-only. -/
def liveDepth02 : Prop := liveDepth01
/-- Live closure-depth chain unit 03; observation-only. -/
def liveDepth03 : Prop := liveDepth02
/-- Live closure-depth chain unit 04; observation-only. -/
def liveDepth04 : Prop := liveDepth03
/-- Live closure-depth chain unit 05; observation-only. -/
def liveDepth05 : Prop := liveDepth04
/-- Live closure-depth chain unit 06; observation-only. -/
def liveDepth06 : Prop := liveDepth05
/-- Live closure-depth chain unit 07; observation-only. -/
def liveDepth07 : Prop := liveDepth06
/-- Live closure-depth chain unit 08; observation-only. -/
def liveDepth08 : Prop := liveDepth07
/-- Live closure-depth chain unit 09; observation-only. -/
def liveDepth09 : Prop := liveDepth08
/-- Live closure-depth chain unit 10; observation-only. -/
def liveDepth10 : Prop := liveDepth09
/-- Live closure-depth chain unit 11; observation-only. -/
def liveDepth11 : Prop := liveDepth10
/-- Live closure-depth chain unit 12; observation-only. -/
def liveDepth12 : Prop := liveDepth11
/-- Live closure-depth chain unit 13; observation-only. -/
def liveDepth13 : Prop := liveDepth12
/-- Live closure-depth chain unit 14; observation-only. -/
def liveDepth14 : Prop := liveDepth13
/-- Live closure-depth chain unit 15; observation-only. -/
def liveDepth15 : Prop := liveDepth14
/-- Live closure-depth chain unit 16; observation-only. -/
def liveDepth16 : Prop := liveDepth15
/-- Live closure-depth chain unit 17; observation-only. -/
def liveDepth17 : Prop := liveDepth16
/-- Live closure-depth chain unit 18; observation-only. -/
def liveDepth18 : Prop := liveDepth17
/-- Live closure-depth chain unit 19; observation-only. -/
def liveDepth19 : Prop := liveDepth18
/-- Live closure-depth chain unit 20; observation-only. -/
def liveDepth20 : Prop := liveDepth19
/-- Live closure-depth chain unit 21; observation-only. -/
def liveDepth21 : Prop := liveDepth20
/-- Live closure-depth chain unit 22; observation-only. -/
def liveDepth22 : Prop := liveDepth21
/-- Live closure-depth chain unit 23; observation-only. -/
def liveDepth23 : Prop := liveDepth22
/-- Live closure-depth chain unit 24; observation-only. -/
def liveDepth24 : Prop := liveDepth23
/-- Live closure-depth chain unit 25; observation-only. -/
def liveDepth25 : Prop := liveDepth24
/-- Live closure-depth chain unit 26; observation-only. -/
def liveDepth26 : Prop := liveDepth25
/-- Live closure-depth chain unit 27; observation-only. -/
def liveDepth27 : Prop := liveDepth26
/-- Live closure-depth chain unit 28; observation-only. -/
def liveDepth28 : Prop := liveDepth27
/-- Live closure-depth chain unit 29; observation-only. -/
def liveDepth29 : Prop := liveDepth28
/-- Live closure-depth chain unit 30; observation-only. -/
def liveDepth30 : Prop := liveDepth29
/-- Live closure-depth chain unit 31; observation-only. -/
def liveDepth31 : Prop := liveDepth30
/-- Live closure-depth chain unit 32; observation-only. -/
def liveDepth32 : Prop := liveDepth31
/-- Live closure-depth chain unit 33; observation-only. -/
def liveDepth33 : Prop := liveDepth32
/-- Live closure-depth chain unit 34; observation-only. -/
def liveDepth34 : Prop := liveDepth33
/-- Live closure-depth chain unit 35; observation-only. -/
def liveDepth35 : Prop := liveDepth34
/-- Live closure-depth chain unit 36; observation-only. -/
def liveDepth36 : Prop := liveDepth35
/-- Live closure-depth chain unit 37; observation-only. -/
def liveDepth37 : Prop := liveDepth36
/-- Live closure-depth chain unit 38; observation-only. -/
def liveDepth38 : Prop := liveDepth37
/-- Live closure-depth chain unit 39; observation-only. -/
def liveDepth39 : Prop := liveDepth38
/-- Live closure-depth chain unit 40; observation-only. -/
def liveDepth40 : Prop := liveDepth39
/-- Live closure-depth chain unit 41; observation-only. -/
def liveDepth41 : Prop := liveDepth40
/-- Live closure-depth chain unit 42; observation-only. -/
def liveDepth42 : Prop := liveDepth41
/-- Live closure-depth chain unit 43; observation-only. -/
def liveDepth43 : Prop := liveDepth42
/-- Live closure-depth chain unit 44; observation-only. -/
def liveDepth44 : Prop := liveDepth43
/-- Live closure-depth chain unit 45; observation-only. -/
def liveDepth45 : Prop := liveDepth44
/-- Live closure-depth chain unit 46; observation-only. -/
def liveDepth46 : Prop := liveDepth45
/-- Live closure-depth chain unit 47; observation-only. -/
def liveDepth47 : Prop := liveDepth46
/-- Live closure-depth chain unit 48; observation-only. -/
def liveDepth48 : Prop := liveDepth47
/-- Live closure-depth chain unit 49; observation-only. -/
def liveDepth49 : Prop := liveDepth48
/-- Live closure-depth chain unit 50; observation-only. -/
def liveDepth50 : Prop := liveDepth49
/-- Live closure-depth chain unit 51; observation-only. -/
def liveDepth51 : Prop := liveDepth50
/-- Live closure-depth chain unit 52; observation-only. -/
def liveDepth52 : Prop := liveDepth51
/-- Live closure-depth chain unit 53; observation-only. -/
def liveDepth53 : Prop := liveDepth52
/-- Live closure-depth chain unit 54; observation-only. -/
def liveDepth54 : Prop := liveDepth53
/-- Live closure-depth chain unit 55; observation-only. -/
def liveDepth55 : Prop := liveDepth54
/-- Live closure-depth chain unit 56; observation-only. -/
def liveDepth56 : Prop := liveDepth55
/-- Live closure-depth chain unit 57; observation-only. -/
def liveDepth57 : Prop := liveDepth56
/-- Live closure-depth chain unit 58; observation-only. -/
def liveDepth58 : Prop := liveDepth57
/-- Live closure-depth chain unit 59; observation-only. -/
def liveDepth59 : Prop := liveDepth58
/-- Live closure-depth chain unit 60; observation-only. -/
def liveDepth60 : Prop := liveDepth59
/-- Live closure-depth chain unit 61; observation-only. -/
def liveDepth61 : Prop := liveDepth60
/-- Live closure-depth chain unit 62; observation-only. -/
def liveDepth62 : Prop := liveDepth61
/-- Live closure-depth chain unit 63; observation-only. -/
def liveDepth63 : Prop := liveDepth62

/-- One edge beyond the live closure-depth boundary. -/
def liveDepthOver : Prop := liveDepth63

mutual
  /-- First member of a live mutual-inductive atomic-family fixture. -/
  inductive LiveMutualLeft where
    | leaf
    | branch : LiveMutualRight → LiveMutualLeft

  /-- Second member of a live mutual-inductive atomic-family fixture. -/
  inductive LiveMutualRight where
    | branch : LiveMutualLeft → LiveMutualRight
end

/-- Live mutual-family closure fixture; observation-only. -/
theorem liveMutualFixture : Nonempty LiveMutualLeft := ⟨.leaf⟩

end StatQED.Registry.Tests
