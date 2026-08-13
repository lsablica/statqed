# Lean proposition normalizer v0

Status: Experimental candidate for RFC-0005.

## Identity and encoding

The grammar identifier is `statqed.lean-expr.v0`.  Values below are semantic
arrays encoded with the Accepted `statqed.cbor-core.v1` profile.  Pretty-printed
Lean text is never identity material.

Names are arrays of segments: `[0, text]` for a string segment and `[1, uint]`
for a numeric segment.  Universe levels are `[0]` (zero), `[1, level]` (succ),
`[2, left, right]` (max), `[3, left, right]` (imax), or `[4, parameter-index]`.
Declaration universe parameters are numbered in declaration order.

Binder information is encoded as `0` (explicit), `1` (implicit), `2` (strict
implicit), or `3` (instance implicit).

Expressions are:

| Lean constructor | Semantic form |
|---|---|
| bound variable | `[0, de-bruijn-index]` |
| sort | `[1, level]` |
| constant | `[2, name, [level-arguments...]]` |
| application | `[3, function, argument]` |
| lambda | `[4, binder-info, domain, body]` |
| forall | `[5, binder-info, domain, body]` |
| let | `[6, type, value, body]` |
| natural literal | `[7, uint]` |
| string literal | `[8, text]` |
| projection | `[9, type-name, index, structure]` |

`Expr.mdata` wrappers, binder display names, cached hashes, sharing, source
locations, and `letE.nondep` are erased.  The normalizer performs no beta,
delta, iota, zeta, eta, literal-desugaring, unfolding, universe algebra, or
Unicode normalization.  It rejects free variables, metavariables, universe
metavariables, loose bound variables, undeclared universe parameters, invalid
UTF-8, unsupported constructors, and out-of-range integers.
Every semantic integer position is an unsigned integer in
`0..18446744073709551615`; booleans are not integers. This applies to tags,
binder information, de Bruijn indices, numeric name segments, natural
literals, projection indices, and universe-parameter indices.

The proposition payload is the canonical CBOR representation of:

```text
["statqed.lean-expr.v0", normalized-expression]
```

Its digest uses purpose `statqed.theorem.proposition.v0`, profile
`statqed.cbor-core.v1`, object class `statqed.lean-proposition.v0`, and framing
`statqed.digest-lp.v1`.  The `statement_digest` is proposition-only.  Full
semantic identity is the tuple `(governed-id, semantic-version, normalizer-id,
proposition-digest, environment-digest)`.

## Limits

- expression depth: 256 constructor edges from a root at depth zero;
- level depth: 64 constructor edges from a root at depth zero;
- total expression and level nodes: 65,536;
- universe arguments: 256 per constant;
- name segments: 64;
- name/string segment: 256 UTF-8 bytes;
- fully qualified name: 1,024 UTF-8 bytes;
- string literal: 65,536 UTF-8 bytes;
- aggregate strings: 262,144 bytes;
- canonical payload: 1,048,576 bytes.

The canonical-CBOR traversal budget is derived from the 1 MiB payload bound
(at most 1,048,576 encoded nodes, each consuming at least one byte) with a
336-level structural recursion cap covering the independently bounded
256-expression-plus-64-level shape and fixed envelope. These serialization
guards do not consume the semantic expression-node or aggregate-string
budgets a second time.

Each boundary is checked before allocation or recursion crosses it.  A limit
failure is `registry.resource_limit`; an unsupported or ill-scoped expression
is `registry.normalization_failure` or `registry.expression_unsupported` as
recorded by the conformance fixture.

The retained live comparison exports independently consumable typed trees from
the pinned Lean runtime. It covers every accepted constructor, all four binder
classes, declared universes, metadata erasure, and exact maximum/one-over
expression and level depths. The Python oracle derives its own bytes and result
class from those typed trees; it does not consume the primary normalized bytes
as expected truth.

## Examples and nonexamples

Renaming a binder or adding metadata preserves bytes.  Changing explicit to
instance-implicit, `True` to `False`, a constant name, a universe parameter, a
projection index, or material expression structure changes bytes.  Kernel
definitional equality does not imply byte equality.  Structural byte equality
does not prove mathematical equality, truth, authorization, source fidelity,
or absence of hash collisions.
