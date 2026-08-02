# Lean Core Implementation Guide

Bootstrap only after toolchain RFC/ADR ratification.

Planned modules:

```text
StatQED/Foundation
StatQED/Experiment
StatQED/Target
StatQED/Procedure
StatQED/Guarantee
StatQED/Assurance
StatQED/Certificate
StatQED/Artifact
StatQED/Registry
```

Use Mathlib idioms, narrow imports, namespaced declarations, executable finite specializations, and explicit bridges between computable and abstract probability. Public theorem signatures require registry/source review. CI checks builds, lints, examples, axiom reports, and forbidden trusted-path constructs.
