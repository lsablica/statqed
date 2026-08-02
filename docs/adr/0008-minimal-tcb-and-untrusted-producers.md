# ADR-0008: Minimal trusted base and untrusted producers

- Status: Proposed

## Decision

Keep language runtimes, numerical solvers, reports, and AI agents outside the trusted base. They emit candidates and witnesses checked by reviewed/formal components.

## Consequences

Every checker has a precise acceptance proposition, corruption tests, resource bounds, and a soundness path. Verification reports enumerate the actual TCB by mode.
