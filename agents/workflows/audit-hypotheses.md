# Workflow: Audit Hypotheses

1. Identify the exact statement/schema digest.
2. Expand definitions, typeclass assumptions, implicit variables, and imported conventions.
3. Classify each effective premise using `agents/protocols/source-lineage.md`.
4. Check joint satisfiability with a concrete nontrivial model.
5. Determine whether the conclusion is vacuous or definitionally trivial.
6. Remove each material premise and search finite cases/literature for failure.
7. Search for weaker sufficient premises.
8. Review quantifier order, conditioning, and probability source.
9. Compare the effective statement to the source and intended applied claim.
10. Emit an outcome code and blocking issues.

An audit is invalid if it reviews only the pretty-printed theorem headline while ignoring definitions.
