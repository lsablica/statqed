import Mathlib.Data.Set.Defs

/-!
# Internal build smoke declaration

This module is test-only infrastructure for SQ-0003. It is not imported by the
top-level `StatQED` module and does not define a public StatQED theorem,
statistical result, non-vacuity witness, registry record, or artifact claim.
-/

namespace StatQED.Internal

/--
Definitionally trivial, test-only evidence that the pinned Lean/Mathlib project
can elaborate a project declaration after a narrow Mathlib import.
-/
theorem testOnlySmoke : True := True.intro

end StatQED.Internal
