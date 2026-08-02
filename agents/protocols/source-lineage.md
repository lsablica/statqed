# Source-Lineage Protocol

## Purpose

Prevent source drift, theorem-variant conflation, and appropriation of prior results.

## Procedure

1. Identify the exact work, edition/version, and locator.
2. Transcribe the theorem in controlled informal notation.
3. List every explicit assumption.
4. List source-implicit conventions.
5. Compare nearby variants and software conventions.
6. Map each source concept to StatQED/Mathlib concepts.
7. Explain library/typing obligations not present in prose.
8. Flag every strengthening, weakening, and altered quantifier.
9. State whether the result is reproduced, generalized, specialized, corrected, or original.
10. Record citation/license implications.

## Hypothesis classes

- `source_explicit`
- `source_implicit_justified`
- `formalization_obligation`
- `strengthening_justified`
- `strengthening_unjustified`
- `candidate_for_weakening`
- `not_applicable`

Unjustified strengthening blocks signature freeze.

## Source quality

Prefer primary sources. Secondary sources may clarify but cannot silently replace the primary theorem. For software semantics, cite official package documentation and test actual versioned behavior.

## Output

Use `agents/templates/source-audit.yaml` and attach reviewer approval.
