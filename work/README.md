# Work Ledger

`backlog.yaml` is JSON-compatible YAML and is the scheduling source of truth. `status.yaml` records the current integrated state. Detailed contracts live in `work/contracts/`.

## Scheduling

A task is dependency-ready only when:

- its declared dependencies are `DONE`;
- it is not superseded;
- accepted RFC/ADR prerequisites exist;
- required reviewers can be assigned;
- the active plan permits it.

`backlog.yaml` records every numbered RFC in `decision_register`, with one non-complete owner task whose contract can edit the decision file. Until a reviewed successor relation is implemented, registered RFCs support only `Draft` and `Accepted`; rejection, withdrawal, or supersession must first extend the ledger with non-cyclic successor semantics and negative tests. The repository guardrail rejects unregistered or stale RFC paths, invalid decision statuses, and any non-Accepted RFC whose owner is already DONE or SUPERSEDED. A task may declare only an `Accepted` `decision_prerequisite`; both repository checking and work listing exclude the task from the ready set until that status is present. A task that owns and resolves an RFC does not list that RFC as its own prerequisite; owner completion itself proves the owned RFC is Accepted.

The initial ready set must contain only SQ-0001.

## Updating state

After merge, the integrator changes the task status, adds commit/review evidence to `status.yaml`, updates the active plan, and runs:

```bash
make check
make list-work
```

Do not edit task dependencies merely to unblock work. Record a planning decision and review the effect on the DAG.
