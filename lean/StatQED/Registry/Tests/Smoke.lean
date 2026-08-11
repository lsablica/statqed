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

end StatQED.Registry.Tests
