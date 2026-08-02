# Schema Scope Instructions

Scope: `schemas/**`.

Every semantic schema change updates controlled prose, CDDL, examples, negatives, canonical vectors, migration analysis, and generated bindings together.

- Use explicit semantic numeric types.
- Reject duplicate keys and unknown critical extensions.
- Golden bytes require independent semantic approval.
- Do not edit generated outputs here.
- Security/resource limits are part of the schema contract.
