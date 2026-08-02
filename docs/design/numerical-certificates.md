# Numerical Certificate Design

The producer is optimized for finding an answer; the checker is optimized for establishing a proposition cheaply and independently.

## Preferred witness families

- exact counts for finite tests;
- residual plus invertibility/conditioning witness for linear systems;
- normal equations plus rank/positive-definiteness witness for least squares;
- primal/dual feasibility, KKT residuals, and duality gap for convex optimization;
- interval Newton/Krawczyk enclosures for roots;
- interval quadrature and tail bounds for integrals/distribution functions;
- decomposition/product witnesses for matrices;
- rank/order witnesses for conformal procedures;
- transition trace for replay plus separate convergence evidence for MCMC.

Every witness binds the canonical spec and relevant data digest. Acceptance establishes only the checker’s proposition. Inferential and identification theorems are separate graph nodes.
