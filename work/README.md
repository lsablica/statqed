# Work Ledger

`backlog.yaml` is JSON-compatible YAML and is the scheduling source of truth. `status.yaml` records the current integrated state. Detailed contracts live in `work/contracts/`.

## Scheduling

A task is dependency-ready only when:

- its declared dependencies are `DONE`;
- it is not superseded;
- accepted RFC/ADR prerequisites exist;
- required reviewers can be assigned;
- the active plan permits it.

The initial ready set must contain only SQ-0001.

## Updating state

After merge, the integrator changes the task status, adds commit/review evidence to `status.yaml`, updates the active plan, and runs:

```bash
make check
make list-work
```

Do not edit task dependencies merely to unblock work. Record a planning decision and review the effect on the DAG.
