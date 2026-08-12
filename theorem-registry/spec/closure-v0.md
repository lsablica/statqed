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
`registry.missing_dependency`.  Units are deduplicated and sorted by canonical
name bytes before encoding.

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
- closure depth: 64;
- total deterministic work units: 1,000,000;
- total expression/dependency nodes: 262,144;
- canonical payload: 1,048,576 bytes;
- diagnostic output: 4,096 bytes.

A work unit is one decoded value, expression/level visit, dependency-edge
attempt, declaration emission, snapshot inspection, or compatibility-edge
inspection.  Width, depth, cycle, work, and missing-dependency failures remain
distinct stable classes.

## Boundary

This is a conservative structural identity.  It deliberately does not use
Lean's incomplete `Level.isEquiv`, alpha equivalence, kernel definitional
equality, or pretty printing.  An unrelated environment change can preserve
semantic identity while changing the proof/build lock.  Digest equality is
conditional integrity evidence, not a proof that two theorems mean the same
thing.
