# Versioning and Compatibility Specification

Status: **Draft; constitutional compatibility RFC remains required before Candidate artifacts**.

StatQED versions IR, artifact, assurance graph, theorem registry, method packs, proof backend, adapters, and CLI protocol independently.

Compatibility classes:

- byte-identical;
- semantic-equivalent by proof/reviewed migration;
- backward-readable without claim preservation;
- convertible with explicit loss;
- incompatible.

Semantic version numbers are informative, not sufficient evidence. Artifacts pin exact canonical records, bytes, and content digests under named algorithms; digests are integrity aids under cryptographic assumptions. Historical verifiers and schemas are archived. A migration that changes canonical bytes, logical digests, accepted propositions/claims, theorem compatibility paths, or relevant TCB creates and discloses a new result/artifact identity as governed by the future compatibility RFC.
