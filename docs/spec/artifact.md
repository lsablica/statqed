# `.statqed` Artifact Specification

Status: **Draft**.

A `.statqed` artifact is provisionally planned as a deterministic, bounded archive. The exact container, manifest, ordering, compression, and resource rules remain SQ-0010 decisions.

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

The candidate normative encoding is deterministic CBOR governed by versioned CDDL files, pending RFC-0001/SQ-0005. Reports are inert and never trusted inputs. RFC-0008/SQ-0010 must specify and test path/name normalization, links/devices/unsupported features, manifest authority, compression and pre-extraction resource budgets, trailing/concatenated/nested ambiguity, unknown critical features, missing locks, privacy-minimized provenance, and digest mismatches. External references resolve only from explicitly supplied local content or remain unresolved. Archival verification must work offline when implemented.
