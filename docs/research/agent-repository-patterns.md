# Agent-Repository Design Patterns Used by StatQED

The scaffold applies current high-leverage patterns for long-running coding/formalization agents:

- concise root instructions plus nested scoped `AGENTS.md` files;
- tool-neutral canonical workflows with thin tool-specific skills/subagents;
- living execution plans rather than disposable chat plans;
- machine-readable dependency DAG and task contracts;
- one task per isolated branch/worktree;
- frozen public statements before broad proof execution;
- independent source, semantic, formal, adversarial, and integration roles;
- explicit escalation instead of assumption-changing improvisation;
- small reviewable changes and green default branch;
- reproducible handoffs and retained agent provenance;
- guardrails that test instruction/ledger invariants;
- benchmark-driven evaluation of agent process quality.

StatQED’s distinctive extension is semantic zoning: abundant agents may work on proof bodies and implementation internals, while public statistical meaning remains tightly reviewed.
