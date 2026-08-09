# SQ-0005 differential conformance review

Status: **Experimental review record**

Disposition: **APPROVE**

Review date: 2026-08-09

Reviewer: `/root/sq0004_api_conformance`, acting as the independent
differential/conformance engineer, distinct from the Python-oracle and Rust
prototype author roles

## Decision

The exact SQ-0005 conformance subject below is approved as Experimental,
non-normative interoperability evidence. The semantic corpus was frozen before
the final run. A clean regeneration found exact Python/Rust agreement with the
reviewed expectations on all 271 cases, and an immediate replay reproduced all
generated JSON and binary goldens byte-for-byte.

This disposition supersedes the earlier 262-case review and the interim
271-case rejection. The interim rejection identified false frozen-commit
fields in the generated manifest. Commit
`efbdf09335110bc34e274d6ee41ddb01638d5eaf` corrected those fields and
regenerated the evidence. The final independent replay confirms that the
manifest now binds the semantic corpus to `b2ec69d` and both executable
implementation subjects to `14f1ffb`.

This approval does not make either implementation an oracle. It does not
approve uncommitted RFC, ADR, canonicalization, or source-audit changes
elsewhere in the shared worktree, and it does not promote CDDL, Python, Rust,
Cargo, SHA-256, the harness, or generated output into the trusted kernel.

## Exact subject

| Subject | Exact identity |
|---|---|
| Current repository head | `fc7a4fc145a610106110df21654fafde41857c33` |
| Semantic candidate and fixture catalog | `b2ec69de45a3406cdcf29aec3243f81e8a42432f` |
| Semantic fixture content tree | SHA-256 `61aca5d116ab07bae26265a35c112668c34dbfae2c274dda428d856cdbdfb2b6` |
| Fixture catalog | SHA-256 `d5bf3079d9ff8119a2372873a1b116601011e78c30067bc1d05228211659b4d3` |
| Python implementation | `14f1ffb0646b280fea805fbec6ba6bb8b3d1a282`; selected-source SHA-256 `3b25890342ebacfbc5ac0cf62dfcd190aa0836e6af757a2b37ed5d79fdb669cd` |
| Rust implementation | `14f1ffb0646b280fea805fbec6ba6bb8b3d1a282`; selected-source SHA-256 `8983150cd08f36ef0c3f1dc84534593aaf8e694f25fed05817e118c09284e515` |
| Harness and regenerated evidence commit | `efbdf09335110bc34e274d6ee41ddb01638d5eaf` |
| Harness file | SHA-256 `e78edf3b0cb4411755bd67a2019567eecd61e81e7821d590d251a0eca34cb0cd` |
| Restricted CDDL input | SHA-256 `05ee85b0d028af588ed9e95e83fdf017259988f05709de85f033cb0ab5badda0` |
| Generated evidence content tree | SHA-256 `bf8caad258725ca159d72956ea3881f6e0eefa735d1f0cb4e59b224e13860170` |
| Binary golden content tree | SHA-256 `df15e89ec9adc12248e1066db16fe8692d234801b5698534506cbbdd827c887b` |
| Retained-failure content tree | SHA-256 `a4bf2b45d7743e2c052c56dcd1ff2baa3eb81455bfdf019f0a8e4af5cc1140f2` |

The selected-source hashes cover executable source plus locked dependency and
toolchain inputs identified by the harness; they exclude later review prose.
The content-tree hashes cover sorted relative paths, a NUL separator, exact
file bytes, and another NUL separator.

### Generated files

| File | SHA-256 |
|---|---|
| `conformance/prototypes/generated-v1/manifest.json` | `9157bf5cc331b026353e12de4adbe9a623509aac9ef6e2a1e8fc22eba71f1d0d` |
| `conformance/prototypes/generated-v1/results.json` | `4ad3b4c121e0a1008ce783d8aaa5f80a43df187b8725ad918bbd78fa244dcdf0` |
| `conformance/prototypes/generated-v1/goldens.json` | `d5e572e44e7930e50f0d44fdf4ece04e7a01ab7d9a6817dda62cbec074183e1c` |
| `conformance/prototypes/generated-v1/failures.json` | `dbda36bd8752d5662f77fb2be3feb6d519e8164c7fe41fad734c05376114970b` |
| `conformance/prototypes/generated-v1/mutations.json` | `1b6c448a29ce76b83c5e85673731382dc24bba8a1902a7686988626015d22da6` |
| `conformance/prototypes/golden/serialization-v1/manifest.json` | `8db0e43760421ea694e0e2d7095ade93a821ce5f3b7c66eaf954d7fe969af7a1` |

The binary manifest records each vector's exact path, byte length, SHA-256,
expectation kind, and Python/Rust agreement. The independent audit recomputed
all 69 listed binary lengths and hashes and found no discrepancy.

## Full differential result

The final corpus contains 271 cases: 70 accepted and 201 rejected. Its result
classes include the newly separated `schema_mismatch` vocabulary; no producer
semantic failure was reclassified as schema mismatch. The observed class
counts are:

| Result class | Cases |
|---|---:|
| accepted | 70 |
| well formedness | 15 |
| validity | 10 |
| expectedness | 6 |
| deterministic profile | 63 |
| CDDL shape | 1 |
| semantic validity | 39 |
| digest verification | 31 |
| resource | 15 |
| differential detection | 17 |
| operational failure | 4 |

There are zero Python expectation mismatches, zero Rust expectation
mismatches, zero cross-implementation mismatches, and zero generated failure
records. Sixty-nine accepted cases have joint binary goldens: 66 CBOR values
and three framed artifacts, totalling 3,551,955 bytes. The largest is the
1,048,918-byte attainable digest frame. The remaining accepted case is the
exact diagnostic-rendering boundary, whose rendering is deliberately
non-normative and therefore has no binary golden.

All 20 mutation checks were detected. These include the three executed bad
implementations for length-first map ordering, last-wins duplicate collapse,
and decode/re-encode acceptance of non-profile input, in addition to the 17
reviewed mutation specifications.

## Interval-shape audit

The nine added interval fixtures all use the producer semantic result class;
none is mislabeled as a schema mismatch. Expected, Python, and Rust result
classes and codes agree exactly:

| Added fixture | Exact result |
|---|---|
| `SEM-INTERVAL-OPEN-UNSUPPORTED` | `semantic_validity / semantic.unsupported_interval` |
| `SEM-INTERVAL-LEFT-CLOSED-UNSUPPORTED` | `semantic_validity / semantic.unsupported_interval` |
| `SEM-INTERVAL-RIGHT-CLOSED-UNSUPPORTED` | `semantic_validity / semantic.unsupported_interval` |
| `SEM-INTERVAL-CLOSURE-UNKNOWN` | `semantic_validity / semantic.interval_invalid` |
| `SEM-INTERVAL-EMPTY-OPEN` | `semantic_validity / semantic.interval_invalid` |
| `SEM-INTERVAL-SINGLETON-CLOSED` | `semantic_validity / semantic.unsupported_interval` |
| `SEM-INTERVAL-RATIONAL-ENDPOINTS` | `semantic_validity / semantic.interval_invalid` |
| `SEM-INTERVAL-DECIMAL-ENDPOINTS` | `semantic_validity / semantic.interval_invalid` |
| `SEM-INTERVAL-IEEE-NAN-ENDPOINTS` | `semantic_validity / semantic.interval_invalid` |

The four existing interval fixtures and the large-exponent typed-JSON
regression were also checked. Valid integer intervals remain unsupported,
reversed or mixed-kind intervals remain invalid, and the decimal exponent
`1000000000` case now reaches `semantic.interval_invalid` because decimals are
outside the integer-only interval shape. Neither implementation materializes
an enormous host power or coerces an IEEE NaN payload.

The closure vocabulary is explicit: `closed`, `open`, `left_closed`, and
`right_closed`. Equal open bounds are invalid/empty; equal closed bounds are a
well-formed singleton but unsupported for v1 encoding. The inverse-style token
`left_open` remains invalid and acquires no implementation-specific meaning.

## Other conformance boundaries

- The CDDL source remains a separately checked structural subset. It does not
  select bytes or license producer semantics.
- The 31 digest cases cover the six-component length-prefixed frame, exact
  SHA-256 digest length, full comparison, truncation, trailing bytes,
  identifier substitution, payload validation, and resource precedence.
- Fixture subprocesses use a five-second timeout and 128 MiB address-space
  ceiling on Linux. Timeout, allocation, crash, and exception outcomes remain
  operational failures, never profile acceptance.
- Historical missing-tool, malformed-fixture, implementation-differential,
  digest-precedence, and adversarial failures remain retained. No failed
  implementation output was installed as a golden.

## Commands and results

```text
PYTHONDONTWRITEBYTECODE=1 python3 scripts/serialization/run_conformance.py --verify
  PASS: 271 cases; 0 failures; 69 joint goldens; 20 mutations

PYTHONDONTWRITEBYTECODE=1 python3 scripts/serialization/run_conformance.py --regenerate
  PASS: 271 cases; 0 failures; 69 joint goldens; 20 mutations

PYTHONDONTWRITEBYTECODE=1 python3 scripts/serialization/run_conformance.py --verify
  PASS: byte-identical generated evidence and binary golden set

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=schemas/prototypes/python-oracle \
  python3 -m unittest discover -s schemas/prototypes/python-oracle/tests -p 'test_*.py' -v
  PASS: 56 tests

cargo test --locked --offline --target-dir /tmp/statqed-sq0005-final-interval-rust-target
  PASS: 31 tests (9 CLI, 22 profile); 0 failures
```

The Rust test target was external to the repository and was removed after the
run. No Python bytecode or conformance temporary directory remains.

## Trust boundary and limitations

- Reviewed semantic fixtures, not implementation output, determine expected
  acceptance, class, code, and candidate bytes.
- Goldens are written only after both independent implementations match every
  precommitted accepted expectation and the full suite passes.
- Agreement is interoperability evidence, not proof of canonicalization
  uniqueness, collision resistance, schema meaning, provenance,
  identification, inference, numerical correctness, or interpretation.
- Replay demonstrates deterministic reproduction; it is not kernel
  verification.
- The status remains Experimental. No production backend, frontend, Lean
  module, RFC, ADR, task ledger, workflow, or source-audit disposition is
  approved by this record.

Within this exact scope, the earlier provenance blocker is resolved and there
is no remaining conformance blocker.
