# SQ-0005 Rust CBOR prototype

Status: **Experimental**. Candidate profile: `statqed.cbor-core.v1`.

This is an isolated research prototype, not a production verifier or semantic
authority. It makes no artifact, statistical, inferential, provenance, or
kernel-verification claim. RFC-0001 and the required independent reviews still
govern any profile decision; RFC-0006 logical-data semantics remain out of
scope.

## Candidate boundary

The default uses RFC 8949 section 4.2.1 core deterministic encoding and
unsigned bytewise lexicographic order over complete canonical map-key bytes.
The RFC 7049-compatible length-first order exists only as a diagnostic mutant.
For `{Integer(24): Null, TextString(""): Null}` the candidate bytes are
`a21818f660f6`; length-first produces the rejected `a260f61818f6`.

Accepted values are direct CBOR integers in `[-2^64, 2^64-1]`, definite byte
strings, exact valid UTF-8 text, definite arrays, definite maps, booleans, and
null. Map keys are only integers or text. The parser retains ordered raw map
entries and detects typed-equal duplicates before any native-map collapse.
Text is never normalized.

All tags, floats, indefinite items, and simple values other than false, true,
and null are rejected. Attempted tags are parsed without interpreting tags 2,
3, 4, 30, or any other tag. A preferred valid tag therefore receives
`profile.tag_forbidden`; a non-preferred tag head receives
`profile.non_preferred_head`. Malformed, invalid, duplicate, or resource faults
inside its child keep their earlier classification.

## Limits and staged results

| Bound | Inclusive candidate limit |
|---|---:|
| input CBOR bytes | 1,048,576 |
| canonical output bytes | 1,048,576 |
| one byte/text string | 65,536 content bytes |
| array items | 1,024 |
| map entries | 1,024 |
| total items, including map keys and values | 4,096 |
| open array/map/tag levels | 32 |
| diagnostic JSON | 4,096 UTF-8 bytes |
| digest-frame allocation | 1,049,255 bytes |

Configuration cannot raise these profile caps. The external conformance
harness, not this library, owns the five-second and 128-MiB operational limits.

Failures expose exactly one lowercase result class and stable dotted code.
Apart from fail-early resource checks, validation precedence is
`well_formedness`, `validity`, `expectedness`, `deterministic_profile`,
`cddl_shape`, `semantic_validity`, `digest_verification`, then `accepted`.
Empty input is `wellformed.truncated`; trailing bytes are
`expected.trailing_bytes`. The implementation emits only the vocabulary in
the candidate profile and semantic-value-model notes.

`decode_raw` owns the input and returns source-spanned nodes. `validate_raw`
then performs validity, allowed-key, deterministic-head, and order checks.
This separation is evidence that duplicates and forbidden raw distinctions
remain observable; successful library decoding or replay is not proof of
schema, scientific, or kernel validity.

## Library boundary

`minicbor` 2.3.0 emits preferred primitive and container heads. It does not
define the semantic model, map ordering, duplicates, accepted types, Unicode,
tags, or limits. `serde_json` is used only for non-normative typed JSON and CLI
evidence transport. `sha2` implements the generic test-only SHA-256 framing.
Exact versions, checksums, lineage, and licenses are in
[`DEPENDENCIES.md`](DEPENDENCIES.md), [`LINEAGE.md`](LINEAGE.md), and
`Cargo.lock`.

## CLI

The diagnostic commands read one strict JSON value and write one compact JSON
line:

```text
statqed-rust-cbor-prototype encode
statqed-rust-cbor-prototype decode
statqed-rust-cbor-prototype frame
statqed-rust-cbor-prototype verify-digest
```

`encode` reads typed JSON directly. `decode` reads an object with required
`cbor_hex` and optional `profile_id` and `expected_top_level` fields. Accepted
results contain `result_class: "accepted"`, `code: "accepted"`, `profile_id`,
`cbor_hex`, and the typed `value`. Rejections contain `result_class`, `code`,
and a diagnostic byte `offset`. `frame` and `verify-digest` use the exact
fields `purpose_id`, `algorithm_id`, `profile_id`,
`object_class_schema_id`, and `framing_id`, plus `cbor_hex` for framing or
`frame_hex` and `digest_hex` for verification.

Typed accepted values use explicit constructors; integers are decimal strings:

```json
{"type":"integer","value":"18446744073709551615"}
{"type":"bytes","hex":"00ff"}
{"type":"text","value":"é"}
{"type":"array","items":[{"type":"boolean","value":false},{"type":"null"}]}
{"type":"map","entries":[{"key":{"type":"text","value":"x"},"value":{"type":"null"}}]}
```

The input layer also recognizes `bignum`, `rational`, `decimal`, `ieee_bits`,
`interval`, `extension`, and `extension_sequence`. These constructors never
fall back to CBOR. Invalid normal forms and well-formed unsupported values
receive their exact `semantic.*` codes. Extension sequences are scanned in
full for duplicate `type_id` values before the presence of any critical entry
determines the order-independent criticality result.

All CLI commands accept at most exactly 2,200,000 bytes of typed/evidence JSON
on standard input. This transport-only cap admits the reviewed 2,117,593-byte
maximal canonical-output projection; it does not alter the 1,048,576-byte CBOR
input/output profile limits or become normative artifact semantics.

Three explicitly test-only evidence commands avoid truncating accepted maximal
fixtures through the 4,096-byte diagnostic envelope:

```text
statqed-rust-cbor-prototype encode-raw   # typed JSON -> exact CBOR bytes
statqed-rust-cbor-prototype decode-raw   # decode request -> full typed JSON
statqed-rust-cbor-prototype frame-raw    # frame request -> exact frame bytes
```

They have no acceptance envelope and write no trailing newline. `encode-raw`
is bounded by the 1,048,576-byte canonical-output cap. `decode-raw` still
accepts at most 1,048,576 CBOR bytes and has an 8,388,608-byte evidence-output
cap derived for worst-case JSON escaping. `frame-raw` uses the same typed input
as `frame` and is bounded by the 1,049,255-byte frame-allocation cap. Their
rejection diagnostics remain bounded at 4,096 bytes. These are conformance
evidence channels, not production or diagnostic APIs.

Diagnostic success exits 0, stable failure exits 2, and stdout write failure
exits 3. Output contains no timestamps, paths, locale-dependent prose, or
library exception text.

## Generic data-free SHA-256 framing

The framing bytes are the exact 15-byte `StatQED-Digest\0` magic followed by
six u32-big-endian length-prefixed components: purpose, algorithm, profile,
object-class/schema, framing, and nonempty canonical payload. The fixed IDs are
`sha-256`, `statqed.cbor-core.v1`, and `statqed.digest-lp.v1`. All five
identifiers are 1–128 ASCII bytes matching
`[a-z0-9][a-z0-9._:-]{0,127}`.

Frame construction as well as verification strictly validates that the payload
is one complete canonical candidate-profile item. Neither operation interprets
the object-class/schema identifier.

Verification consumes exactly six components, checks caller-supplied expected
identifiers without fallback, revalidates the payload under the candidate
profile, and compares an exact 32-byte SHA-256 digest. It does not resolve or
validate the named object schema; that remains the schema-owning caller's
separate obligation. A digest match does not establish provenance truth or
collision-free identity.

## Reproduction

Run from this directory; the lock is exact and these commands do not update it:

```bash
rustc +1.97.1 -Vv
cargo +1.97.1 -V
CARGO_TARGET_DIR=/tmp/statqed-sq0005-rust-cbor-target cargo +1.97.1 fmt --all -- --check
CARGO_TARGET_DIR=/tmp/statqed-sq0005-rust-cbor-target cargo +1.97.1 clippy --all-targets --locked --offline -- -D warnings
CARGO_TARGET_DIR=/tmp/statqed-sq0005-rust-cbor-target cargo +1.97.1 test --locked --offline
CARGO_TARGET_DIR=/tmp/statqed-sq0005-rust-cbor-target cargo +1.97.1 build --locked --offline
```

The configured target is outside the repository. No cache, `target/`, generated
vector, or evidence log belongs in this prototype directory.
