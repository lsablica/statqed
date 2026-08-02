# Workflow: Formalize a Public Theorem

1. Create a source audit with exact locator and theorem variant.
2. Write a controlled informal statement.
3. Map concepts to Mathlib and StatQED; ask a Mathlib scout for exact candidates.
4. Expand all effective hypotheses and randomness scopes.
5. Produce nontrivial models satisfying the premises.
6. Search for counterexamples and test assumption ablations.
7. Draft the Lean signature and theorem-registry metadata.
8. Obtain source, statistical, and formal signature review.
9. Freeze and hash the signature.
10. Delegate proof construction without signature-edit permission.
11. Run build, theorem examples, mutations, and axiom report.
12. Review interpretation/nonclaims and register compatibility relations.
13. Merge only after independent integration review.

If proof work suggests a signature change, return to step 6 through a reviewed revision; never patch the signature silently.
