# Workflow: Create a Certificate Checker

1. State the exact proposition established by checker acceptance.
2. List all semantic inputs and bind them in the witness or checked spec.
3. Choose exact arithmetic, intervals, decompositions, or proof traces appropriate to the obligation.
4. Define malformed-input and resource-limit behavior.
5. Implement an independent small-instance oracle.
6. Add valid, boundary, corrupted, truncated, oversized, and type-confused witnesses.
7. Prove or schedule `check = true → NumericFact` in Lean.
8. Benchmark verification cost separately from production cost.
9. Document what acceptance does not establish.
