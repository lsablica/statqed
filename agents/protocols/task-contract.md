# Task Contract Protocol

Every implementation task begins with a machine-readable contract derived from `agents/templates/task.yaml`.

## Required contract fields

- task ID and title;
- plan/milestone;
- objective stated as an observable outcome;
- dependencies and their evidence;
- allowed files/directories;
- forbidden files/interfaces;
- public API/signature changes permitted;
- source inputs;
- assumptions;
- implementation steps;
- tests;
- review roles;
- acceptance criteria;
- commands;
- expected handoff artifacts.

## Scope rules

- An agent edits only allowed paths.
- A discovered need outside scope becomes a dependency or follow-up task.
- Public semantic changes require an RFC/accepted design reference.
- A proof executor cannot edit a frozen theorem signature.
- A certificate producer task cannot alter checker semantics.
- Generated files are changed through their generator.

## Status

Allowed statuses:

- `READY`
- `IN_PROGRESS`
- `BLOCKED`
- `IN_REVIEW`
- `DONE`
- `SUPERSEDED`

A `BLOCKED` task records:

- blocking fact;
- minimal reproduction/evidence;
- attempted approaches;
- exact decision or dependency needed;
- recommended next action.

## Completion

The integrator confirms contract compliance, merge gates, plan/status updates, and a handoff record. A task is not DONE merely because code compiles.
