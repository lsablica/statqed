# Workflow: Add a Frontend Adapter

1. Pin the supported source package/version range.
2. Document source-language semantics and ambiguities from official sources and experiments.
3. Define the canonical normal form and unsupported features.
4. Extract rows, transformations, factor/categorical encodings, weights, offsets, targets, and provenance explicitly.
5. Compare against shared golden and differential fixtures.
6. Verify exact numeric conversions and missing-value behavior.
7. Fail closed on unknown or version-divergent semantics.
8. Add report-language tests so adapter fidelity is not overstated.
9. Record adapter ID and conformance version in artifacts.
