# SQ-0005 differential conformance and golden-vector review

Status: **Experimental review record**

Disposition: **APPROVE**

Review date: 2026-08-09

Reviewer: `/root/sq0004_api_conformance`, acting as the independent
differential/conformance engineer, distinct from the Python-oracle and Rust
prototype author roles

## Decision

The exact implementation subject
`410465d773fc011ee01e38e6e76a79a60efe8837` is approved for SQ-0005
Experimental differential-conformance and golden-vector evidence. Its Git tree
is `a93ac8fe4befe4da52ff0ef5ee928ea04679b85c`.

The current head during review was
`5704fca2173012a2e8d5de4a39e9390dba5a37ce`. The complete diff after the
approved subject changes only independent review records. It does not change
the semantic fixtures, CDDL input, harness, generated evidence, golden vectors,
retained failures, or either executable implementation.

A no-write replay passed before regeneration. A clean regeneration then
produced the same evidence, and a second no-write replay verified all generated
JSON and binary files byte-for-byte: 273 cases, zero failures, 69 joint
goldens, and 20 detected mutations.

This approval does not make either implementation an oracle. It does not
promote the semantic corpus, CDDL, Python, Rust, Cargo, SHA-256, the harness, or
generated output into the trusted kernel, and it does not approve production
backends, frontends, Lean modules, RFC status, or statistical claims.

## Exact subject and hashes

| Subject | Exact identity |
|---|---|
| Approved implementation subject | commit `410465d773fc011ee01e38e6e76a79a60efe8837`; tree `a93ac8fe4befe4da52ff0ef5ee928ea04679b85c` |
| Frozen semantic fixtures | commit `b4d92a39e30fa5736c58bc71c57790ec215fbad7`; content-tree SHA-256 `90fc4b5a1346f0693b84a0fa9a6a1e1fa4ac535aff2b83d6177313c6779fa3c8` |
| Fixture catalog | SHA-256 `d5bf3079d9ff8119a2372873a1b116601011e78c30067bc1d05228211659b4d3` |
| Python executable subject | last direct source commit `fd8dd9e344ff6bbe1488cb143f8b700c6c795efe`; selected-source SHA-256 `cc05dbf3d4996f44e204099ad335df843557571ae61aac8044903de5f9e41a9f` |
| Rust executable subject | last direct source commit `fd8dd9e344ff6bbe1488cb143f8b700c6c795efe`; selected-source SHA-256 `cb3c03907bc7cdf6f495be7d98d795347b3b51c1415637a6b1e8d71f558027ea` |
| Conformance harness | SHA-256 `8a61f6deeeba7bed4e8bb7e0c8202fa0ce730d5328036365d8536ed5950fe01c` |
| Restricted CDDL source | SHA-256 `05ee85b0d028af588ed9e95e83fdf017259988f05709de85f033cb0ab5badda0` |
| Generated evidence content tree | SHA-256 `56cc44b248f251e481280481600f2dedc4e32c606e2a4cb03079700332beb389` |
| Binary golden content tree | SHA-256 `df15e89ec9adc12248e1066db16fe8692d234801b5698534506cbbdd827c887b` |
| Retained-failure content tree | SHA-256 `a4bf2b45d7743e2c052c56dcd1ff2baa3eb81455bfdf019f0a8e4af5cc1140f2` |

The selected-source hashes cover executable source plus the locked dependency
and toolchain inputs selected by the harness. They deliberately exclude review
prose. Content-tree hashes cover each sorted relative path, a NUL separator,
the exact file bytes, and another NUL separator.

### Generated evidence and golden manifest

| File | SHA-256 |
|---|---|
| `conformance/prototypes/generated-v1/manifest.json` | `e69e863053fad44faf2511cedbd53a13725e309cbdb0551621e217c2095dd6cd` |
| `conformance/prototypes/generated-v1/results.json` | `4e48d962644cec0f83b868ba13bcc62f3bc8cee4dca748fed10e3ad911195274` |
| `conformance/prototypes/generated-v1/goldens.json` | `d5e572e44e7930e50f0d44fdf4ece04e7a01ab7d9a6817dda62cbec074183e1c` |
| `conformance/prototypes/generated-v1/failures.json` | `dbda36bd8752d5662f77fb2be3feb6d519e8164c7fe41fad734c05376114970b` |
| `conformance/prototypes/generated-v1/mutations.json` | `1b6c448a29ce76b83c5e85673731382dc24bba8a1902a7686988626015d22da6` |
| `conformance/prototypes/golden/serialization-v1/manifest.json` | `8db0e43760421ea694e0e2d7095ade93a821ce5f3b7c66eaf954d7fe969af7a1` |

The binary manifest records each vector's exact path, byte length, SHA-256,
expectation kind, and Python/Rust agreement. The independent audit recomputed
all 69 file lengths and hashes and found no discrepancy. The set contains 66
CBOR values and three digest frames, totalling 3,551,955 bytes. Its largest
file is the 1,048,918-byte attainable digest frame.

## Semantic-first provenance

Expectations come from the reviewed semantic/raw fixture corpus, not from
implementation output. The corpus commit and content-tree hash above are
recorded in the generated manifest. The Python and Rust observations are
compared independently against each expectation and then against one another.
Binary goldens are written only if the complete suite passes and both
implementations agree with the precommitted accepted expectation.

The corpus contains 273 cases: 70 accepted and 203 rejected. Class counts are:

| Result class | Cases |
|---|---:|
| accepted | 70 |
| well formedness | 15 |
| validity | 10 |
| expectedness | 6 |
| deterministic profile | 63 |
| CDDL shape | 1 |
| semantic validity | 39 |
| digest verification | 33 |
| resource | 15 |
| differential detection | 17 |
| operational failure | 4 |

There are zero Python expectation mismatches, zero Rust expectation
mismatches, zero cross-implementation mismatches, and zero current generated
failure records. One accepted diagnostic-rendering boundary intentionally has
no binary golden because diagnostic rendering is non-normative.

## Raw duplicate and map-order evidence

The two accepted semantic maps encode in core lexicographic order:

- `MAP-CORE-NEG1-100` -> `a21864f620f6`;
- `MAP-CORE-24-EMPTY-TEXT` -> `a21818f660f6`.

Python and Rust both reject the length-first alternatives with
`deterministic_profile / profile.map_order`. Both also preserve raw map-entry
sequences long enough to reject:

- exact duplicate Integer(0);
- duplicate-before-trailing compound input;
- equivalent preferred/nonpreferred encodings of Integer(0) and Integer(-1);
- equivalent preferred/nonpreferred text key `a`.

Every duplicate case returns `validity / validity.map_duplicate` in both
implementations, with no class/code or cross-comparison error. The executed
last-wins decoder mutant and the two duplicate-collapse mutation specifications
are detected, showing that native-map collapse would not pass this suite.

## Raw overlong digest identifiers

The two added raw-frame cases are complete, structurally parseable frames;
they are not component truncations:

| Fixture | Reviewed/Python/Rust result |
|---|---|
| `DIGEST-RAW-PURPOSE-BYTES-129` | `digest_verification / digest.purpose` |
| `DIGEST-RAW-SCHEMA-BYTES-129` | `digest_verification / digest.object_class_schema` |

Both implementations apply the field-specific 128-byte identifier boundary
after parsing the complete length-prefixed component. They do not misclassify
either case as `digest.component_length`, trailing bytes, or a generic schema
result. These cases increase digest-verification coverage from 31 to 33 while
leaving the accepted golden set unchanged.

The remaining digest corpus covers the fixed six-component length-prefixed
frame, exact SHA-256 digest length, full comparison, component truncation,
trailing bytes, identifier substitution, payload validation, payload/frame
limits, and error precedence. This is data-free framing evidence; it does not
resolve a schema identifier or establish artifact identity.

## CDDL boundary

The exact restricted CDDL source is loaded and validated separately from the
byte profile and producer semantics. Sixty-six accepted CBOR typed projections
match `statqed-value`. The explicit map-only counterexample reaches
`cddl_shape / shape.cddl_mismatch` in both implementation observations after
the harness-owned structural phase. The other 206 cases do not reach or do not
use that phase.

CDDL neither selects canonical bytes nor licenses a producer-semantic,
statistical, provenance, artifact, or kernel claim.

## Deliberate mutations and retained failures

All 20 mutation checks are detected. Seventeen are reviewed semantic mutation
specifications. Three execute minimized bad implementations:

- length-first map-key ordering;
- last-wins duplicate collapse;
- decode/re-encode acceptance of non-profile input.

Historical failure evidence remains retained and parseable:

| Record | SHA-256 |
|---|---|
| `lock-reproduction-missing-targets.json` | `76d84d663a1d3ef9c0fd79c91473b707c9afeabd98d38c67d3781fd082595b7f` |
| `python-only-rust-unavailable-v1.json` | `e41b03f63c4edbee1f6eca8bbebfbf9e5826b5eaefc4ab58e2659538228d8d70` |
| `rust-adversarial-reject-v1.json` | `0e016692b7e7e2816b0da52f08e3ce345ebed4170f61f0c233b30e3df1a2b594` |
| `rust-digest-payload-length-precedence-v1.json` | `cb1fd18e44c6c64734ba5324703c29478941e4a92aee37944907a4789ca5c30e` |
| `rust-first-full-differential-v1.json` | `b446359044108bf0fd25a4cfc20c2a7edd707d90f92049d3df636f7e0d8a00cd` |
| `simple-24-malformed-fixture-v1.json` | `9622a62de7b366296334a182c6190bb6235853fc62d5f26547487bec67f243e5` |

These records preserve missing-tool, dependency, semantic-fixture,
implementation, adversarial, and error-precedence failures. No failed
implementation output was used to change an expectation or install a golden.

## Reproduction and implementation tests

```text
PYTHONDONTWRITEBYTECODE=1 python3 scripts/serialization/run_conformance.py --verify
  PASS: 273 cases; 0 failures; 69 joint goldens; 20 mutations

PYTHONDONTWRITEBYTECODE=1 python3 scripts/serialization/run_conformance.py --regenerate
  PASS: 273 cases; 0 failures; 69 joint goldens; 20 mutations

PYTHONDONTWRITEBYTECODE=1 python3 scripts/serialization/run_conformance.py --verify
  PASS: byte-identical generated evidence and binary golden set

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=schemas/prototypes/python-oracle \
  python3 -m unittest discover -s schemas/prototypes/python-oracle/tests -p 'test_*.py' -v
  PASS: 57 tests

cargo test --locked --offline --target-dir /tmp/statqed-sq0005-final-273-rust-target
  PASS: 31 tests (9 CLI, 22 profile); 0 failures
```

Each fixture subprocess uses a five-second timeout and a 128 MiB address-space
ceiling on Linux. The Rust test target was external to the repository and was
removed. No Python bytecode or conformance temporary directory remains.

## Trust boundary and limitations

- Agreement is interoperability evidence, not proof of canonicalization
  uniqueness, collision resistance, schema meaning, provenance,
  identification, inference, numerical correctness, or interpretation.
- Replay demonstrates deterministic reproduction; it is not kernel
  verification.
- The evidence is data-free and Experimental.
- No production backend, frontend, Lean theorem, statistical method, task
  status, or RFC maturity claim is approved by this record.

Within this exact scope, there is no differential-conformance or golden-vector
blocker.
