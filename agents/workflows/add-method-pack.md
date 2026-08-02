# Workflow: Add an End-to-End Method Pack

A pack is complete only when semantics, theorem, witness, checker, producer, frontends, tests, provenance, and citations compose.

1. Approve scope, estimand, procedure, guarantee, assumptions, randomness, and nonclaims.
2. Build the source corpus and theorem dependency graph.
3. Freeze public theorem signatures.
4. Design the numerical obligation and witness independently of a solver.
5. Implement a small checker and prove checker soundness.
6. Implement at least one untrusted producer and an independent oracle.
7. Define IR and artifact payloads with canonical vectors.
8. Implement at least two frontend paths before Candidate maturity.
9. Add positive, boundary, malformed, corrupted, ablation, and overclaim fixtures.
10. Add theorem-registry and citation metadata.
11. Produce one complete `.statqed` exemplar and trust report.
12. Run performance/resource tests and all merge gates.
