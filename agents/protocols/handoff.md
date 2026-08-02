# Handoff Protocol

A handoff lets another agent or human continue without conversational context.

## Required content

- task ID and objective;
- status;
- commits/branch;
- files changed;
- public interfaces changed;
- semantic decisions made;
- commands run and exact results;
- tests added;
- source/review records;
- trust-boundary impact;
- unresolved issues;
- next dependency-ready task;
- cleanup needed.

Use `agents/templates/handoff.md`.

## Rules

- State failures and skipped checks explicitly.
- Do not use “all tests pass” without naming the command.
- Do not claim a review that was not performed.
- Include generated-file provenance.
- Link decisions to RFC/ADR/plan entries.
