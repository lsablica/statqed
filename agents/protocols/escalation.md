# Escalation Protocol

Agents must stop and escalate rather than silently resolve the following:

- conflicting primary sources;
- unsupported or unexpectedly strong hypothesis;
- theorem appears false or vacuous;
- frozen signature must change;
- core definition/IR meaning is missing;
- trust boundary expands;
- canonicalization is ambiguous;
- package/toolchain versions are incompatible;
- task needs forbidden files;
- security issue;
- conformance implementations disagree;
- implementation cannot meet acceptance criteria.

## Escalation record

Include:

- task ID;
- exact blocker;
- minimal example;
- relevant files/sources;
- attempts and results;
- impact;
- decision required;
- recommended options with trade-offs;
- whether other tasks can proceed safely.

Create an RFC when the decision is constitutional. Create a dependency task for bounded implementation/research. Mark the original task BLOCKED.
