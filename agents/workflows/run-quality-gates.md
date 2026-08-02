# Workflow: Run Quality Gates

Run the gates required by the task contract and `agents/protocols/merge-gates.md`.

Minimum sequence:

```bash
make check
```

When available, also run the scoped format, lint, build, unit, property, conformance, fuzz-smoke, Lean axiom, artifact-verification, package-check, and clean-checkout commands documented in the nearest `AGENTS.md`.

Record every command, working directory, tool version, exit status, and material warning. A skipped command must be named with a reason. Do not summarize partial testing as “all tests pass.”
