# Frontend Scope Instructions

Scope: `frontends/**`.

Frontends are thin, untrusted producers over the shared IR/reference backend.

- Preserve rows, missingness, categories, weights, offsets, targets, and provenance explicitly.
- Unsupported semantics fail; no silent fallback or approximation.
- Do not implement a private normative canonicalizer.
- Use shared conformance fixtures and exact numeric conversions.
- Reports may not upgrade assurance status.
