import Mathlib.Probability.ProbabilityMassFunction.Basic

namespace StatQEDLeanProbe

/-- A data-free smoke theorem exercising Mathlib's probability API. -/
theorem pmf_total_mass (p : PMF Bool) : p.toMeasure Set.univ = 1 := by
  letI : MeasureTheory.IsProbabilityMeasure p.toMeasure := PMF.toMeasure.isProbabilityMeasure p
  exact MeasureTheory.measure_univ

#check PMF.toMeasure.isProbabilityMeasure
#print axioms StatQEDLeanProbe.pmf_total_mass

end StatQEDLeanProbe
