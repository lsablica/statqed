import Mathlib.Probability.ProbabilityMassFunction.Basic

namespace StatQEDLeanRejectedProbe

theorem pmf_total_mass (p : PMF Bool) : p.toMeasure Set.univ = 1 := by
  letI : MeasureTheory.IsProbabilityMeasure p.toMeasure := PMF.toMeasure.isProbabilityMeasure p
  exact MeasureTheory.measure_univ

end StatQEDLeanRejectedProbe
