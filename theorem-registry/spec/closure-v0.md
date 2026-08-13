# Meaning-bearing environment closure v0

Status: Experimental candidate for RFC-0005.  The identifier is
`statqed.lean-environment-closure.v0`.

## Algorithm

The root set is every constant and projection type name in the canonical
proposition.  Roots are resolved from the exact pinned `Lean.Environment`.
The deterministic frontier is ordered by canonical name bytes.  A declaration
unit is emitted once, but every attempted edge consumes work.

- a definition contributes kind, name, universe arity, normalized type,
  normalized value, safety, and reducibility kind;
- a theorem contributes kind, name, universe arity, and normalized type; its
  proof body belongs only in the proof/build lock;
- an opaque declaration or axiom contributes kind, name, universe arity,
  normalized type, unsafe status, and origin classification, but no body;
- an inductive family is one atomic unit containing the ordered mutual family,
  parameter/index counts, constructors and structural fields;
- a constructor resolves to its family unit;
- a recursor contributes its type, structural counts, safety, ordered rules
  and parent family;
- a quotient primitive binds its exact kind/type and pinned Lean source.

References are traversed through every included type or value.  Selected
instances are already explicit constants in elaborated expressions; the global
instance table is not included.  Imports, attributes, module names, source
positions, pretty-printer settings, unrelated declarations, theorem bodies,
and opaque bodies are excluded from semantic closure.  They remain build-lock
material where relevant.

Inductive-family grouping removes constructor/parent pseudo-cycles.  Any other
gray-stack cycle is `registry.closure_cycle`.  Missing names are
`registry.missing_dependency`. Units are deduplicated and sorted by canonical
CBOR name bytes before encoding. This ordering is deliberately not Lean's
`Name.quickCmp` and is covered by a discriminating vector. Every member,
constructor, and recursor of a mutual inductive family is emitted in one atomic
unit.

Roots must be an array of valid names, declarations a map, each selected
declaration a map, and `references` an array of valid names. Non-array roots,
non-map declaration tables or records, and non-array references fail as
`registry.normalization_failure`; no host-language iteration or attribute
error is observable.

The closure payload is canonical CBOR of:

```text
["statqed.lean-environment-closure.v0",
 "f3b06c705e6c85f5314019d5d3baab0fec5b580c",
 "statqed.lean-expr.v0",
 [canonical-declaration-units...]]
```

Its digest purpose is `statqed.theorem.environment.v0`, object class
`statqed.lean-environment-closure.v0`, profile `statqed.cbor-core.v1`, and
framing `statqed.digest-lp.v1`.

## Limits

- roots: 256;
- closure units: 1,024;
- outgoing edges per unit: 256;
- closure depth: 64 dependency edges from a root at depth zero;
- total deterministic work units: 1,000,000;
- total expression/dependency nodes: 262,144;
- canonical payload: 1,048,576 bytes;
- diagnostic output: 4,096 bytes.

A work unit is one decoded value, expression/level visit, dependency-edge
attempt, declaration emission, snapshot inspection, or compatibility-edge
inspection.  Width, depth, cycle, work, and missing-dependency failures remain
distinct stable classes.

The 1,000,000 work cap is a fail-closed outer safety cap. Under the other v0
limits, the closure traversal's reachable upper bound is 525,312 work units
(262,144 expression/level visits, 1,024 declaration emissions, and at most
1,024 × 256 edge attempts), so expression, unit, or width limits necessarily
dominate first. The implementation tests the exact cap predicate at 1,000,000
and one over, and separately tests traversal accounting at an exact reachable
required-work/one-under boundary; it does not claim a reachable closure can
trigger the outer cap in v0.

Live environment fixtures bind a referenced definition body, a project-local
selected instance, a complete mutual-inductive family, exact depth 64/65, and
the exact required-work/one-under boundary. A separate Python lineage derives
references, family aliases, reachability, canonical records, expression visits,
edge attempts, and payload bytes from the exported typed units.

## Boundary

This is a conservative structural identity.  It deliberately does not use
Lean's incomplete `Level.isEquiv`, alpha equivalence, kernel definitional
equality, or pretty printing.  An unrelated environment change can preserve
semantic identity while changing the proof/build lock.  Digest equality is
conditional integrity evidence, not a proof that two theorems mean the same
thing.
