# Workflow: Execute an Active Plan

1. Read the plan entirely, including Progress, Surprises, Decision Log, and Outcomes.
2. Parse `work/backlog.yaml`; select a task whose dependencies are `DONE` and status is `READY`.
3. Create a task contract and isolated branch/worktree.
4. Name author and independent reviewers before implementation.
5. Resolve required sources and accepted RFC/ADR references.
6. Implement only allowed files; create dependency tasks for discovered out-of-scope work.
7. Run task tests continuously and preserve failure evidence.
8. Obtain semantic/source, formal/conformance, adversarial, and integration reviews as applicable.
9. Run `agents/workflows/run-quality-gates.md`.
10. Update plan sections and `work/status.yaml`.
11. Produce a handoff and merge only after gates pass.
12. Recompute dependency-ready tasks; do not skip ahead because a later task appears easier.
