# Versioning and Compatibility Specification

StatQED versions IR, artifact, assurance graph, theorem registry, method packs, proof backend, adapters, and CLI protocol independently.

Compatibility classes:

- byte-identical;
- semantic-equivalent by proof/reviewed migration;
- backward-readable without claim preservation;
- convertible with explicit loss;
- incompatible.

Semantic version numbers are informative, not sufficient evidence. Artifacts pin exact content hashes. Historical verifiers and schemas are archived. A migration that changes accepted claims must produce a new artifact identity and disclose the change.
