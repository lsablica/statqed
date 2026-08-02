# Frontend Conformance Guide

R, Python, and Julia share schema-generated structural types and one canonicalization protocol.

Each frontend must test:

- trivial native IR construction;
- numeric type fidelity;
- missing/categorical behavior;
- row identity and ordering;
- deterministic output;
- unsupported feature errors;
- adapter provenance;
- report-language status;
- byte/digest equality against Rust and independent vectors.

Frontend-specific shortcuts never modify normative bytes without a spec change.
