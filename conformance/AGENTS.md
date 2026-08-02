# Conformance Scope Instructions

Scope: `conformance/**`.

Fixtures are reviewed semantic evidence.

- Keep positive, negative, boundary, malformed, corruption, and differential cases.
- Never regenerate golden bytes as an unreviewed snapshot update.
- Record schema/version/tool provenance.
- Minimize disagreements and preserve them as regression cases.
- Expected errors are stable classes, not language-specific prose.
