# `.statqed` Artifact Specification

Status: **Draft 0**.

A `.statqed` artifact is a deterministic archive with a canonical manifest and bounded entries.

Provisional layout:

```text
manifest.cbor
ir.cbor
assurance-graph.cbor
theorem-lock.cbor
data/schema.cbor
data/logical-digest.txt
certificates/*
provenance/ro-crate-metadata.json
citations/references.bib
report/*                 # non-normative
```

Normative objects use deterministic CBOR governed by versioned CDDL. Reports are never trusted inputs. The verifier rejects path traversal, duplicate names, ambiguous Unicode, oversized entries, unknown critical features, missing locks, and digest mismatches. Archival verification must work offline.
