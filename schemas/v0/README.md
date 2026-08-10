# Foundation structural schema v0

Status: Experimental.

The embedded identity is the inseparable pair
`("statqed.foundation-structural.v0", 0)`. There is no version negotiation:
changing either member, or changing both to a correlated unreviewed pair,
requires a different reviewed schema identity/version.

`schema.duplicate_field` is a defensive result of the independent semantic
validator when it is invoked directly on an ordered typed map. In the five-layer
fixture pipeline, RFC-0001 rejects duplicate raw keys first as
`validity.map_duplicate`; the defensive schema code is not a substitute for
pre-collapse profile validation.

`statqed.foundation-structural.v0` is one closed, data-free structural fixture.
It is not the general StatQED IR and gives no statistical, provenance,
artifact, theorem, certificate, or logical-data guarantee.

## Exact semantic value

The value is a map with exactly these six text keys. Every field is required;
every unlisted field is rejected; intentional absence is never represented by
`null`.

| Field | Exact semantic constraint | Example | Nonexample | Serialization consequence | Migration consequence |
|---|---|---|---|---|---|
| `schema_id` | Text exactly `statqed.foundation-structural.v0`. | the exact literal | `statqed.foundation-structural.v1` | encoded as unnormalized UTF-8 text | any change requires a new schema identity |
| `schema_version` | CBOR integer exactly `0`. | integer 0 | text `"0"`, float 0.0 | preferred unsigned integer head | any value-domain change requires a new schema identity |
| `fixture_kind` | Text exactly `foundation_structural`. | the exact literal | `foundation-structural` | encoded as unnormalized UTF-8 text | any change requires a new schema identity |
| `analysis_id` | Opaque ASCII fixture label matching `[a-z0-9][a-z0-9._:-]{0,127}`; equality is exact bytes/scalars. It asserts neither global uniqueness nor provenance. | `foundation.example-0001` | empty, uppercase, Unicode, 129 bytes | no normalization or coercion; one to 128 UTF-8 bytes | grammar or meaning changes require a new schema identity |
| `probability_context` | Text exactly `not_applicable`; no probability statement or random/fixed/conditioned object is represented. | the exact literal | `observational`, `null` | encoded as unnormalized UTF-8 text | any probability semantics require a new schema identity and separate ontology review |
| `features` | Array exactly `[]`; v0 declares no features and defines no feature-element ontology. | `[]` | any nonempty array or non-array | definite empty array only | feature behavior requires a new schema identity |

The CDDL intentionally leaves the `analysis_id` ASCII grammar to the
independent semantic validator. Consequently a CDDL-success/semantic-failure
case is retained. CDDL success is only structural evidence: it does not imply
deterministic bytes, semantic validity, digest validity, provenance, or
statistical validity.

## Validation layers

Results are recorded separately in this order:

1. RFC-0001 profile decoding;
2. exact deterministic-byte conformance;
3. published-syntax CDDL shape;
4. fixture semantic validity;
5. fixture digest verification.

The aggregate primary failure follows RFC-0001 precedence, but the retained
record includes every layer that could be evaluated. A CDDL rejection is not
relabeled as a field-specific semantic rejection.

## Versioning and digest boundary

Field names, requiredness, types, constants, cardinality, grammar, equality,
or meaning are schema identity. Unknown fields fail closed. Documentation-only
corrections may retain the identity only after review; no general backward
compatibility or migration promise is made. RFC-0007 remains responsible for
the future general migration policy.

Accepted fixture bytes are framed with purpose `statqed.fixture.golden`,
algorithm `sha-256`, profile `statqed.cbor-core.v1`, object class
`statqed.foundation-structural.v0`, and framing `statqed.digest-lp.v1`.
This is a data-free fixture digest. It is not logical-data identity, does not
resolve RFC-0006, and proves neither collision absence nor provenance truth.

Generate the compiled CDDL with:

```bash
python3 scripts/schema/compile_schema_v0.py
```

The generator concatenates exact UTF-8 source bytes in manifest order. Each
source must use LF and end with exactly one LF; no draft CDDL module/import
syntax is used.
