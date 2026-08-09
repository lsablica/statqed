# Python reference-oracle lineage review

Status: **Experimental review record**

Disposition: **APPROVE**

Review date: 2026-08-09

Reviewer: `/root/sq0005_source_curator`, acting as the independent
reference-oracle lineage reviewer

## Decision

The Python reference oracle is approved as independent, non-normative
interoperability evidence for the exact subjects below. The approval covers the
content-addressed final candidate inputs, the Python executable and lock tree,
the bounded typed-JSON subprocess contract, the project-original ordered-entry
parser and encoder, the integer-only interval diagnostic rule, the final raw
digest-identifier failure precedence, and the reproduced CPython 3.12.13
behavior. It does not promote the oracle, CPython, OpenSSL, the conformance
harness, generated evidence, or any prototype output into normative or
kernel-verified evidence.

This review is independent of the `/root/sq0005_python_oracle` author role.
The shared Git author identity does not by itself establish independence. The
direct-from-specification no-read statement remains a provenance attestation;
repository history and static/runtime evidence can support it but cannot prove
what an author privately viewed.

No blocking lineage, dependency, semantic-binding, test, documentation, or
bounded-failure finding remains for this Experimental subject. The final README
now states the same integer-only, fail-before-arithmetic interval rule as the
candidate, executable, tests, and corpus.

## Exact subjects

- Reviewed repository commit:
  `410465d773fc011ee01e38e6e76a79a60efe8837`.
- Commit tree: `a93ac8fe4befe4da52ff0ef5ee928ea04679b85c`.
- Parent and final evidence-rebinding commit:
  `7d83204d5ebde9e86e7493e2c9be89506afcd2ee`.
- Evidence-rebinding commit tree:
  `4f6abb15787d07cafce03e5369ddf49c5a42ad24`.
- Exact executable-tree source:
  `fd8dd9e344ff6bbe1488cb143f8b700c6c795efe`.
- Executable-tree source commit tree:
  `10eef0c7a01321764803ff49a64f53b4d0878d91`.
- Python behavioral implementation source:
  `89af5a7dbb837ea7d1557d1a715b34a814afdf95`.
- Python implementation commit tree:
  `f5c461c2ab4fab471cee001af10ad0bc5ad6c551`.
- Frozen semantic-fixture source:
  `b4d92a39e30fa5736c58bc71c57790ec215fbad7`.
- Semantic-fixture commit tree:
  `fc9c299a5119ccedb0e2f94a649c19f84f76b2dd`.
- Python-oracle Git tree at the reviewed commit:
  `b1c74193c6f8568f6c6c6425cfb89f98250236bb`.
- Semantic-corpus Git tree at the reviewed commit:
  `feacd909067e41cf4107d4de415f044d689402cd`.
- Python executable/lock subject SHA-256:
  `cc05dbf3d4996f44e204099ad335df843557571ae61aac8044903de5f9e41a9f`.
- Python-oracle content-tree SHA-256:
  `0c1f7303b4b67024f362e288a00cc06842056f865a433d1b0d20205c6869b6b2`.
- Semantic-corpus content-tree SHA-256:
  `90fc4b5a1346f0693b84a0fa9a6a1e1fa4ac535aff2b83d6177313c6779fa3c8`.

The executable/lock subject hashes the sorted paths `.python-version`,
`requirements.txt`, `statqed_oracle/__init__.py`, `statqed_oracle/cli.py`, and
`statqed_oracle/oracle.py`, with each relative path and file body separated by
NUL bytes. The content-tree hashes use the tracked harness's sorted relative
path, NUL, file-body, NUL construction, excluding build/cache paths.

The five executable/lock files are byte-identical between exact-tree commit
`fd8dd9e` and the reviewed repository commit. That exact-tree commit differs
from behavioral commit `89af5a7` only by removal of one trailing blank line
from `statqed_oracle/__init__.py`; no executable behavior changed. Commit
`89af5a7` directly follows profile-clarification commit
`cda86d8f1f373b6648134b71c88683fd699485e2` and changes only the Python oracle,
its Python tests, and the language-neutral harness; it does not change Rust
source, lock files, or outputs. The earlier Python origin commit
`2c63655ec3c16611786d66038d5c45bc944190de` directly follows candidate commit
`ac5ce971eca4f46e7725f56599e5a30e7025bd22`, before Rust first enters tracked
history at `2f0d778fff38bedd512dadd8603fc59e38be75b4`.

### Final candidate and acceptance-document bindings

| File | SHA-256 |
|---|---|
| `docs/research/serialization/semantic-value-model.md` | `a94588e54fdc3e2aa08e73f5f6e76bb71128940bb245305b2dec9dffa2ffcfb2` |
| `docs/research/serialization/profile-candidate.md` | `6cbf0f686a1f35b5c6fac8411ef5abc708c9c4410b5fdb2ee510c513df067d2f` |
| `docs/spec/canonicalization.md` | `e0bc0628fd0ac05a43f06ac478c029e83a5daeb4fe88f2b00579d4f892cce61a` |
| `docs/adr/0004-deterministic-cbor-cddl.md` | `004b41b65dc8450de6f0bd8431f7de2e1f885e95dfd985f50981e1c1c5c9e49d` |
| `rfcs/0001-deterministic-encoding.md` | `d4258501486affdaf99ec95322bae1e1212806c896e33360a17c137fd2f51106` |
| `schemas/prototypes/lineage.json` | `7a7e48658e81e478c3858f265d24eb0c1402fa6169e7c03eb74363effb8208a4` |

The first two hashes exactly match `LINEAGE.md` lines 16-17. At this exact
subject RFC-0001 remains Draft, ADR-0004 remains Proposed, and the
canonicalization specification remains a Draft acceptance candidate. This
lineage approval does not silently upgrade those statuses.

### Python source, lock, documentation, and tests

| File | SHA-256 |
|---|---|
| `schemas/prototypes/python-oracle/.python-version` | `aa0d6581054e6e4ff3f91839deca7a854ad37221b8784d060b42d0f847ff1a3b` |
| `schemas/prototypes/python-oracle/requirements.txt` | `fe1b58fd32e3f1cc2d11a6a70c8d179ae0b6e150ef651823a100f9343fc27bd0` |
| `schemas/prototypes/python-oracle/statqed_oracle/__init__.py` | `2124b3275cec5d49a7b907e6b022f762293a15354cff51ff0f95c74f30dcfc05` |
| `schemas/prototypes/python-oracle/statqed_oracle/cli.py` | `eed36baf0b98a2bb70f3eb0569ccc4a2f3e547768cc0e1a841376701f8dd0ec9` |
| `schemas/prototypes/python-oracle/statqed_oracle/oracle.py` | `784bbbef227bdff5728622e35d9c46071ea776dd5c0bbbd2eb5ddcc2f1e04d00` |
| `schemas/prototypes/python-oracle/ENVIRONMENT.md` | `a284ec1c00b8ad0f1ae0bf96f59b7ab2456ca7f81e9a4ab935b9718c017d4d3d` |
| `schemas/prototypes/python-oracle/LINEAGE.md` | `8dfe50d1a4010984881c77cd48fa3eca14e307e71d8cc0b5afed48d3e6babd92` |
| `schemas/prototypes/python-oracle/PSF-LICENSE-2.0.txt` | `b683dca09ef30505ae793c3948beb1861d8a1af75d03010ee7cf7e20bab2b74f` |
| `schemas/prototypes/python-oracle/README.md` | `be2e588dc7d78bc12ce9f45c879b359f912c8ec8eaf11ff491dd1bb14b2d742b` |
| `schemas/prototypes/python-oracle/tests/test_decoding.py` | `3f1c9a8be9c41c05e99b514f5b3e897bc6c3c67089c5fd4a6970d72948bc14af` |
| `schemas/prototypes/python-oracle/tests/test_digest_and_cli.py` | `d826b8fbf8a4896fcb11a85ddaa789ea003fe551c308b3072128b294dbfb7ff4` |
| `schemas/prototypes/python-oracle/tests/test_encoding.py` | `41dea8852d602275c665b8c6bcf8266302ce6685ec7fd12889b553c1d3bf2e6f` |
| `schemas/prototypes/python-oracle/tests/test_resources.py` | `e1104fb200111b7ce69b834b1470ebd00e05dfb11bc903360c13448399553f36` |

`requirements.txt` is a 76-byte explanatory comment and has zero effective
requirements.

### Corpus and permanent execution evidence

| File | SHA-256 |
|---|---|
| `conformance/prototypes/fixtures/semantic-v1/atoms-and-widths.json` | `2ffec8250ace8283959db11a29d2d7c2b55500429065d484394732c59e52dcd9` |
| `conformance/prototypes/fixtures/semantic-v1/catalog.json` | `d5bf3079d9ff8119a2372873a1b116601011e78c30067bc1d05228211659b4d3` |
| `conformance/prototypes/fixtures/semantic-v1/differential-mutants.json` | `313a784148be66fa471c2684be27512fbf5e0f446f7681dd27e8317b36c882e6` |
| `conformance/prototypes/fixtures/semantic-v1/digest-framing.json` | `36895de279202434a1511bb1bf552c199e55d57ee8a57a7d724772a737824d0b` |
| `conformance/prototypes/fixtures/semantic-v1/malformed-and-strictness.json` | `b6af575d7111def454a642fa3052bc626f2aea2a4fee76cf7719677739fcf2af` |
| `conformance/prototypes/fixtures/semantic-v1/maps-and-unicode.json` | `c1053fc27be0e8afb60ef655038daca71b43e93c98a2abe5c0dae56e29efb110` |
| `conformance/prototypes/fixtures/semantic-v1/numeric-tags-extensions.json` | `5c50a8ed96b4e1a032f818b9ecec0ae2e6db9b4e2e746e1ed47bcd8cca739329` |
| `conformance/prototypes/fixtures/semantic-v1/resources.json` | `984a142eb002a38d4f137a98d44c222fe2bf56dd2147808608372cb0f7ad0039` |
| `schemas/prototypes/cddl/profile-v1.cddl` | `05ee85b0d028af588ed9e95e83fdf017259988f05709de85f033cb0ab5badda0` |
| `scripts/serialization/run_conformance.py` | `8a61f6deeeba7bed4e8bb7e0c8202fa0ce730d5328036365d8536ed5950fe01c` |
| `conformance/prototypes/evidence/evidence-spec.json` | `26fccac7ca0ab94e9ae270e92016aacc3d7ade25a28ee548347d0322dfc394c6` |
| `conformance/prototypes/generated-v1/manifest.json` | `e69e863053fad44faf2511cedbd53a13725e309cbdb0551621e217c2095dd6cd` |
| `conformance/prototypes/generated-v1/results.json` | `4e48d962644cec0f83b868ba13bcc62f3bc8cee4dca748fed10e3ad911195274` |
| `.github/workflows/serialization-prototypes.yml` | `ee7b9643374d001cd595f4232d42780bdf70b8c78c2cbe0396551501d3674117` |

The 273-case result body was first frozen at
`ff479c0bbe24792878cd1905676bb35f3fe9d4f0` and is byte-identical at the
reviewed subject. The final manifest was rebound at `7d83204` after the
whitespace-only executable-tree commit. It records 70 accepted, 203 rejected,
zero failures, fixture commit `b4d92a3`, fixture content-tree SHA-256
`90fc4b5a...`, and Python exact-tree commit `fd8dd9e` with executable/lock
SHA-256 `cc05dbf3...`. These generated files are content-addressed subjects, not
truth consumed by the Python-only replay described below.

### Source-audit lineage

| File | SHA-256 |
|---|---|
| `source-audits/encoding/manifest.json` | `b3f70746a36c350590f2f77ffebb0e550773337d79db4103317426be94ac0a40` |
| `source-audits/encoding/SA-SQ0005-CBOR.yaml` | `f61098ab0a0a4bd8ff6b1c866772023a5ad2f283d0f7e78801cffaafc7196185` |
| `source-audits/encoding/SA-SQ0005-CRYPTO.yaml` | `d3feb17277b3fccafa2201f36290d2c89be5a98ab953fd75dfd749bb6da3ae36` |
| `source-audits/encoding/SA-SQ0005-PROTOTYPES.yaml` | `90ed358716e9d9f27de60d75d2eda4c5f1d8ae1c5fec38187dc3c2b962e9d506` |

## Independent lineage findings

- `schemas/prototypes/lineage.json` records Python `calls: []`,
  `consumes_outputs_from: []`, a direct-from-profile canonicalizer, and the
  project-original ordered-entry parser. `LINEAGE.md` lines 25-30 attest that
  no Rust source, output, test vector, package, shared encoder, or expected
  truth was consumed.
- Static AST inspection of executable source found only `__future__`,
  `argparse`, `dataclasses`, `hashlib`, `hmac`, `json`, `math`, `re`, `struct`,
  `sys`, and `typing`. Comparison with the exact runtime's standard-library
  module set found no third-party import. The implementation contains no
  subprocess import.
- Static text inspection found no `cargo`, `rustc`, Rust-prototype path,
  generated/golden path, `cbor2`, `ciborium`, `minicbor`, `serde`, or shared
  canonicalizer reference in Python executable or test source. Tests use the
  standard-library `subprocess` module only to invoke the Python CLI under the
  current interpreter; executable source itself has no subprocess import.
- The implementation defines its own raw item/entry parser. Raw maps retain all
  entries until allowed-key, typed-duplicate, and complete canonical-key-byte
  order checks finish. No host dictionary erases duplicate evidence first.
- Direct-range integers cover `[-2^64, 2^64-1]`; preferred heads, definite
  containers, UTF-8, typed map keys, strict core order, all-tag and all-float
  rejection, result precedence, and the six-component SHA-256 frame are
  implemented directly.
- Final interval behavior matches semantic-model line 77, profile line 169,
  source lines 649-665, unit tests, and corpus cases: both endpoints must be
  accepted-range `Integer` values; recognized closures are `closed`, `open`,
  `left_closed`, and `right_closed`; equal endpoints are valid only for
  `closed`. Valid shapes return `semantic.unsupported_interval`; reversed,
  empty, unknown-closure, rational, Decimal, IEEE, and mixed endpoint shapes
  return `semantic.interval_invalid`.
- Final digest behavior matches profile lines 389-401, source lines 1163-1227,
  the two fixtures introduced at frozen fixture commit `b4d92a3`, and the new
  unit test. A complete 129-byte purpose or object-class/schema identifier is
  structurally parseable and returns its field-specific code; a component
  shorter than its declared length remains `digest.component_length`.
- The later result-taxonomy change gives `schema_mismatch` only to a separately
  requested schema validator. The generic Python profile does not emit or
  manufacture `schema.mismatch`, so that profile-only clarification added no
  implementation dependency.

The evidence supports code and algorithm independence. It does not prove the
author's private no-read claim. The implementation commit's Python-plus-harness
scope and the shared Git identity are recorded rather than treated as
independent-origin proof.

## Reproduced behavior

All commands ran from a read-only `git archive` extraction of exact commit
`410465d773fc011ee01e38e6e76a79a60efe8837`; no later worktree file was used.

The unit suite ran with an empty environment except the explicit path,
`PYTHONPATH`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONWARNINGS=error`, `C.UTF-8`
locale, UTC, and the pinned interpreter:

```text
/home/lukas/miniconda3/envs/stats/bin/python -S -m unittest discover
  -s schemas/prototypes/python-oracle/tests -p test_*.py -v
```

Result: **57 of 57 tests passed** in 0.704 seconds, with no warning or
third-party site initialization.

A Python-only in-memory run of the exact tracked harness used
`Implementations(None)`: no Rust binary was supplied, built, invoked, or read;
no generated result was read or written. It loaded 273 catalogue cases: 250
Python-owned paths, 6 harness-owned paths, and 17 mutant specifications. The
256 non-mutant cases executed with **zero mismatches**; all 70 acceptances and
all rejection class/code, byte, projection, digest, and CDDL expectations
matched.

The exact unit and Python-only corpus replays covered these bounded adversarial
witnesses with stable Results and zero stderr:

| Witness | Exact result |
|---|---|
| Quoted 5,000-digit integer | exit 1; `semantic_validity / semantic.integer_range` |
| Typed JSON of 2,200,000 bytes | exit 0; accepted |
| Typed JSON of 2,200,001 bytes | exit 1; `resource / resource.input_bytes` |
| 2,000 nested typed arrays, 54,015 bytes | exit 1; `resource / resource.depth` |
| Decimal interval with exponent 1,000,000,000, 176 bytes | exit 1; `semantic_validity / semantic.interval_invalid`; no power materialization |
| Unquoted 5,000-digit JSON integer under `PYTHONINTMAXSTRDIGITS=4300` and `0` | byte-identical result SHA-256 `600dec9603e92fbc3fcde78ea3503683e2cd33ae77af4f502c5bacbd39b3fde3`; `semantic.unsupported_value` |
| `Integer(True)`, `Integer(1.5)`, and `TextString(7)` | three `semantic.unsupported_value` Results; no exception |
| Dense 2,199,898-byte typed array with 137,492 children under 128 MiB and 5 seconds | `resource.array_items` |
| Complete raw 129-byte purpose identifier | `digest_verification / digest.purpose` |
| Complete raw 129-byte object-class/schema identifier | `digest_verification / digest.object_class_schema` |
| Declared 129-byte identifier with only 128 content bytes | `digest_verification / digest.component_length` |

Malformed byte witnesses `18`, `1c`, `61ff`, `a200f400f500`, and `5f6161ff`
returned, respectively, stable truncated, reserved-additional, invalid-UTF-8,
duplicate-before-trailing, and indefinite-chunk-type diagnostics. Final interval
witnesses distinguished closed singleton, non-closed equal bounds, four known
closure spellings, unknown `left_open`, and non-Integer endpoints exactly as
the final candidate specifies.

The local runtime reproduced as conda-forge CPython 3.12.13 build
`hd63d673_0_cpython`, cache tag `cpython-312`, GCC 14.3.0, Linux
7.0.0-28-generic x86-64, glibc 2.39, OpenSSL 3.6.3, Unicode 15.0.0,
and little-endian host. The full installed CPython license SHA-256 was
`3b2f81fe21d181c499c59a256c8e1968455d6689d269aa85373bfb6af41da3bf`.

The workflow configures exact CPython 3.12.13 and 3.14.7 oracle jobs with `-S`
and runner metadata capture. This review did not inspect a hosted run, so the
workflow configuration is not evidence that 3.14.7 executed successfully.

`python3 scripts/serialization/source_audit_manifest.py` passed with 9 files
and source tree
`75f8fe98338e4800230a7b9a9da7988f728bdf2516b170e969134482511686f2`.
`make check` passed with 60 backlog tasks, 21 detailed contracts, 75 probes,
and 6 recommendations. `git diff-tree --check 410465d^ 410465d` passed.

## Primary sources and project specializations

RFC 8949, STD 94, sections 4.1 and 4.2.1 are the primary anchors for preferred
and core deterministic encoding; sections 5.3 and 5.6 anchor validity and map
semantics ([RFC 8949](https://www.rfc-editor.org/rfc/rfc8949.html), DOI
`10.17487/RFC8949`). Section 4.2.3 is the conflicting length-first variant and
is explicitly excluded.

FIPS 180-4 sections 5.1.1, 5.2.1, 5.3.3, and 6.2 define SHA-256, not the
project-original StatQED frame
([FIPS 180-4](https://csrc.nist.gov/pubs/fips/180-4/upd1/final), DOI
`10.6028/NIST.FIPS.180-4`). Strict rejection, the closed semantic subset,
integer-only intervals, resource limits, typed JSON, result precedence,
identifiers, and six-field framing are project specializations rather than
requirements attributed to either standard.

The official versioned runtime-license locator is the
[CPython 3.12.13 LICENSE](https://github.com/python/cpython/blob/v3.12.13/LICENSE).
The retained `PSF-LICENSE-2.0.txt` is only the PSF License Version 2 portion,
not the complete runtime distribution license. Redistribution requires a new
complete license and notices audit.

## Limitations and nonclaims

- The direct-from-specification no-read assertion is an attestation. Commit
  ordering, separate logical roles, source structure, empty lineage edges, and
  dependency scans support it; they cannot prove private author conduct.
- Behavioral anchor `89af5a7` changes the Python oracle, its tests, and the
  language-neutral harness. Exact-tree anchor `fd8dd9e` later removes one blank
  EOF line from Python `__init__.py` while also normalizing two Rust metadata
  files. Neither commit scope nor whitespace identity establishes independent
  authorship by itself.
- `ENVIRONMENT.md` lines 20-23 conservatively list `fractions` among permitted
  standard-library imports, but the final executable AST no longer imports it.
  This over-approximation does not introduce a dependency.
- Approval covers the typed-JSON subprocess interface and tested accepted
  constructor-to-`encode` paths. Arbitrary hostile values passed directly to
  helper functions can still raise host `TypeError`; those helpers are not the
  approved compatibility contract.
- The finite corpus and tests are evidence, not proof of total implementation
  correctness, parser safety, or cross-runtime behavior. No differential
  agreement is claimed because no Rust output was consumed in this review.
- The frozen generated evidence contains separately produced Rust observations.
  This review validates its commit and file hashes and the Python binding in its
  manifest; it does not use those Rust observations as expected truth.
- Direct execution evidence is Linux x86-64 CPython 3.12.13 only. The configured
  3.14.7 job is not a reviewed hosted result.
- The retained PSF-only license text is not a complete redistribution record.
- SHA-256 comparison is computational evidence. It does not establish
  provenance, scientific identification, inference, numerical certification,
  interpretation, or kernel verification.
- Status remains Experimental. This approval does not accept RFC-0001, adopt
  ADR-0004, freeze a public artifact signature, or authorize production use.

## Source-audit-compatible classification

```yaml
audit_id: SA-SQ0005-PYTHON-ORACLE-LINEAGE-410465D
subject: Exact final independent Python reference-oracle lineage and behavior
source:
  work: RFC 8949, FIPS 180-4, StatQED serialization candidates, and CPython 3.12.13
  version: RFC 8949 STD 94; FIPS 180-4 Update 1; StatQED commit 410465d773fc011ee01e38e6e76a79a60efe8837; Python exact-tree commit fd8dd9e344ff6bbe1488cb143f8b700c6c795efe; Python behavioral commit 89af5a7dbb837ea7d1557d1a715b34a814afdf95; fixture commit b4d92a39e30fa5736c58bc71c57790ec215fbad7; evidence-rebinding commit 7d83204d5ebde9e86e7493e2c9be89506afcd2ee; CPython 3.12.13
  locator: RFC 8949 Sections 4.1, 4.2.1, 4.2.3, 5.3, and 5.6; FIPS 180-4 Sections 5.1.1, 5.2.1, 5.3.3, and 6.2; docs/research/serialization/semantic-value-model.md line 77; docs/research/serialization/profile-candidate.md lines 20-34, 53-68, 113-169, 208-247, and 330-419; schemas/prototypes/python-oracle/LINEAGE.md lines 5-36; schemas/prototypes/python-oracle/ENVIRONMENT.md lines 5-48
  persistent_id: https://doi.org/10.17487/RFC8949; https://doi.org/10.6028/NIST.FIPS.180-4; git:410465d773fc011ee01e38e6e76a79a60efe8837
controlled_statement: >-
  The Python oracle executable/lock subjects frozen at exact-tree commit fd8dd9e344ff6bbe1488cb143f8b700c6c795efe, with behavior rooted at 89af5a7dbb837ea7d1557d1a715b34a814afdf95, and reviewed in repository subject 410465d773fc011ee01e38e6e76a79a60efe8837 are an Experimental, non-normative, standard-library implementation of statqed.cbor-core.v1, independently originated from semantic-model hash a94588e54fdc3e2aa08e73f5f6e76bb71128940bb245305b2dec9dffa2ffcfb2 and profile hash 6cbf0f686a1f35b5c6fac8411ef5abc708c9c4410b5fdb2ee510c513df067d2f, with no Rust source, output, or library consumed by the Python source or tests. Its bounded typed-JSON interface, ordered raw-map handling, integer/profile/result behavior, integer-only interval diagnostics, and complete-overlong digest-identifier precedence reproduce under CPython 3.12.13. The current 273-case manifest hash e69e863053fad44faf2511cedbd53a13725e309cbdb0551621e217c2095dd6cd binds fixture commit b4d92a39e30fa5736c58bc71c57790ec215fbad7 and Python executable/lock hash cc05dbf3d4996f44e204099ad335df843557571ae61aac8044903de5f9e41a9f to results hash 4e48d962644cec0f83b868ba13bcc62f3bc8cee4dca748fed10e3ad911195274; this Python-only review does not consume its Rust observations. CPython 3.14.7 is configured in the hosted workflow but is not local evidence in this review.
hypotheses:
  - name: exact_final_candidate_inputs
    class: source_explicit
    source_anchor: schemas/prototypes/python-oracle/LINEAGE.md lines 5-17
    notes: The exact-tree commit, behavioral commit, and both final SHA-256 inputs exactly match the reviewed subjects.
  - name: core_deterministic_order
    class: source_explicit
    source_anchor: RFC 8949 Section 4.2.1; profile-candidate.md lines 20-24 and 113-157
    notes: Compare complete deterministic key encodings lexicographically; length-first order is excluded.
  - name: preferred_strict_closed_profile
    class: strengthening_justified
    source_anchor: RFC 8949 Sections 4.1-4.2; profile-candidate.md lines 13-34 and 418-436
    notes: Strict rejection and the closed value/tag set are project choices for unique artifact bytes, not formalization conveniences.
  - name: ordered_raw_map_entries
    class: formalization_obligation
    source_anchor: RFC 8949 Sections 5.3 and 5.6; semantic-value-model.md lines 18-55 and 84-105
    notes: Preserve every entry until allowed-key, typed-duplicate, and complete-byte order checks finish.
  - name: direct_range_integer_model
    class: source_explicit
    source_anchor: semantic-value-model.md line 65; profile-candidate.md lines 53-85
    notes: The domain is -2^64 through 2^64-1, shortest heads only, with no bignum fallback.
  - name: integer_only_interval_shape
    class: source_explicit
    source_anchor: semantic-value-model.md line 77; profile-candidate.md line 169
    notes: Only accepted-range Integer endpoints and four closure tokens form valid research shapes; equal bounds require closed.
  - name: interval_validation_before_unsupported_disposition
    class: formalization_obligation
    source_anchor: oracle.py lines 649-665 and 753-755; test_encoding.py lines 138-183
    notes: Invalid shapes return semantic.interval_invalid; valid but unencoded shapes return semantic.unsupported_interval.
  - name: sha256_algorithm
    class: source_explicit
    source_anchor: FIPS 180-4 Sections 5.1.1, 5.2.1, 5.3.3, and 6.2
    notes: FIPS specifies SHA-256, not the StatQED frame semantics.
  - name: statqed_digest_frame
    class: formalization_obligation
    source_anchor: profile-candidate.md lines 330-419
    notes: The six-component unsigned-32-bit length-prefixed frame is project-original.
  - name: complete_identifier_failure_precedence
    class: source_explicit
    source_anchor: profile-candidate.md lines 389-401; digest-framing.json DIGEST-RAW-PURPOSE-BYTES-129 and DIGEST-RAW-SCHEMA-BYTES-129
    notes: A complete invalid identifier receives its field code; only a prefix or component shorter than its declared length receives digest.component_length.
  - name: direct_from_spec_no_read_provenance
    class: source_implicit_justified
    source_anchor: schemas/prototypes/python-oracle/LINEAGE.md lines 25-36; schemas/prototypes/lineage.json lines 2-14
    notes: Attestation, history, role separation, empty lineage edges, source structure, and scans support but cannot prove private conduct.
  - name: no_rust_source_output_or_library_consumption
    class: formalization_obligation
    source_anchor: schemas/prototypes/python-oracle/LINEAGE.md lines 19-30; schemas/prototypes/lineage.json lines 2-14
    notes: Static imports/references, test construction, empty edges, and Python-only execution find no Rust consumption.
  - name: no_third_party_python_dependency
    class: formalization_obligation
    source_anchor: requirements.txt; ENVIRONMENT.md lines 18-23
    notes: The effective lock is empty, AST imports are standard-library-only, and the full suite passes under -S.
  - name: bounded_deterministic_typed_json
    class: formalization_obligation
    source_anchor: README.md lines 42-52 and 67-109; cli.py lines 54-82; oracle.py resource constants and checks
    notes: Exact-bound, nesting, item, malformed, diagnostic, integer-token, and invalid-interval probes fail with stable bounded Results.
  - name: frozen_fixture_and_generated_evidence_binding
    class: formalization_obligation
    source_anchor: run_conformance.py lines 49-58; generated-v1/manifest.json
    notes: The 273-case manifest binds fixture commit b4d92a3, Python exact-tree commit fd8dd9e, both content hashes, and zero recorded failures; Rust observations are not expected truth for this review.
  - name: separate_schema_mismatch_class
    class: source_explicit
    source_anchor: profile-candidate.md lines 208-247
    notes: Only a separately identified schema validator can emit schema.mismatch; the generic oracle does not.
  - name: exact_cpython_31213_execution
    class: not_applicable
    source_anchor: ENVIRONMENT.md lines 5-16 and reproduced local runtime
    notes: This is an observed software-environment fact, not a mathematical hypothesis.
  - name: cpython_3147_execution_evidence
    class: not_applicable
    source_anchor: ENVIRONMENT.md lines 25-30; serialization-prototypes.yml lines 23-66
    notes: The exact version is configured, but no hosted run was inspected and no success is inferred.
  - name: complete_runtime_license_retained
    class: not_applicable
    source_anchor: ENVIRONMENT.md lines 32-42
    notes: Not claimed; only PSF-2.0 text is retained and redistribution requires re-audit.
  - name: author_or_shared_git_identity_suffices_for_review
    class: strengthening_unjustified
    source_anchor: agents/protocols/source-lineage.md; repository independent-review rule
    notes: Rejected; distinct author and reviewer roles must remain recorded.
variants:
  - name: RFC 8949 core deterministic encoding
    locator: RFC 8949 Section 4.2.1
    conflict: Lexicographic order of full deterministic key encodings.
    disposition: Selected and directly implemented.
  - name: RFC 8949 length-first deterministic encoding
    locator: RFC 8949 Section 4.2.3
    conflict: Encoded length is compared before lexical bytes.
    disposition: Explicitly excluded; library convenience cannot change the profile.
  - name: lossy host-map decoding
    locator: RFC 8949 Sections 5.3 and 5.6
    conflict: First-wins, last-wins, or native-map collapse can erase duplicate evidence.
    disposition: Excluded; ordered raw entries survive through validation.
  - name: permissive decode-and-reencode
    locator: RFC 8949 Section 5.4
    conflict: Repairs non-profile input rather than rejecting it.
    disposition: Excluded from the strict artifact boundary.
  - name: generic CBOR package or shared canonicalizer
    locator: source-audits/encoding/SA-SQ0005-PROTOTYPES.yaml
    conflict: Package defaults may select another order and a shared component defeats implementation independence.
    disposition: Excluded from the Python oracle.
  - name: early overlong-identifier component-length failure
    locator: Python oracle before implementation commit 89af5a7dbb837ea7d1557d1a715b34a814afdf95
    conflict: A fully present identifier over 128 bytes was classified as digest.component_length before its bytes were parsed.
    disposition: Superseded; complete invalid identifiers now receive their field-specific code, while actual truncation retains digest.component_length.
  - name: broad numeric interval endpoints
    locator: semantic-value-model.md at commit b5fb813c211317c4e3e48ea8b8c232fbd14cf82b
    conflict: An earlier candidate admitted rational, Decimal, IEEE, and mixed endpoint comparison.
    disposition: Superseded by the final accepted-range Integer-only research shape; no strengthening is approved merely for formalization ease.
  - name: integer-only interval README prose
    locator: schemas/prototypes/python-oracle/README.md lines 84-87
    conflict: The earlier Decimal-comparator prose at commit 4d77d28 described a mechanism removed by the final interval narrowing.
    disposition: Corrected at the reviewed subject to rejection of non-Integer endpoints before comparison or power materialization.
  - name: schema mismatch from generic profile
    locator: profile-candidate.md lines 208-247
    conflict: Earlier combined taxonomies could imply that generic profile validation emits schema.mismatch.
    disposition: Excluded; schema.mismatch belongs only to a separately requested schema validator.
  - name: CPython 3.12.13 local execution
    locator: schemas/prototypes/python-oracle/ENVIRONMENT.md lines 5-16
    conflict: Reproduced on one Linux x86-64 runtime and crypto backend.
    disposition: Approved only as the exact local evidence boundary.
  - name: CPython 3.14.7 configured execution
    locator: .github/workflows/serialization-prototypes.yml lines 23-66
    conflict: Configuration is not a reviewed hosted result.
    disposition: Retain as configured only, not reproduced evidence.
  - name: PSF-only retained text versus complete runtime license
    locator: schemas/prototypes/python-oracle/ENVIRONMENT.md lines 32-42
    conflict: The retained text omits historical and component terms.
    disposition: Adequate for execution inventory only; re-audit before redistribution.
concept_mapping:
  - source_concept: core deterministic CBOR
    statqed_concept: statqed.cbor-core.v1 canonical bytes
    obligation: Enforce preferred heads, definite lengths, selected key order, and the closed value subset.
  - source_concept: map key equivalence
    statqed_concept: typed Integer/TextString equality over raw entry sequences
    obligation: Detect duplicates before map collapse and before ordering disposition.
  - source_concept: unsupported interval research shape
    statqed_concept: Integer-only shape validation followed by unsupported disposition
    obligation: Reject invalid endpoint kinds and closure/bound combinations before returning unsupported_interval.
  - source_concept: SHA-256 message
    statqed_concept: exact six-component StatQED length-prefixed frame bytes
    obligation: Keep hash-algorithm correctness separate from frame injectivity and schema meaning.
  - source_concept: complete versus truncated length-prefixed component
    statqed_concept: field-specific digest identifier failure versus digest.component_length
    obligation: Parse a complete declared component before identifier validation; reserve component_length for an absent prefix or insufficient declared bytes.
  - source_concept: Python package dependency
    statqed_concept: untrusted operational implementation dependency
    obligation: Run without site packages and retain exact runtime/license evidence.
quantifiers:
  - statement: For every typed semantic value admitted by the candidate within its resource limits, encoding yields selected profile bytes or a stable Result.
    source_status: Project implementation obligation; tested but not formally proved.
  - statement: For every raw input within the CBOR input bound, decoding retains raw entries until precedence checks complete and returns an accepted value or stable Result.
    source_status: Project implementation obligation; finite evidence only.
  - statement: For every interval diagnostic, only accepted-range Integer endpoints and the four named closures can reach unsupported_interval; every other shape reaches interval_invalid.
    source_status: Final project semantic obligation; source, unit tests, corpus, and adversarial witnesses agree.
  - statement: For all 273 catalogue cases, 256 non-mutant Python/harness paths were executed without Rust and matched; 17 mutant specifications were not Python executions.
    source_status: Exact local observation for the reviewed subject.
  - statement: For every runtime or platform, CLI output is identical.
    source_status: Not established; only the recorded CPython 3.12.13 platform and limited environment variants were tested.
randomness_scopes: []
nonvacuity_witnesses:
  - name: core_order_discriminator
    value: Integer(-1) and Integer(100) map keys
    purpose: Core order accepts a2 18 64 f6 20 f6 while length-first order is rejected.
  - name: typed_duplicate_before_trailing
    value: a200f400f500
    purpose: Produces validity.map_duplicate before trailing-byte disposition, showing raw-entry preservation and precedence.
  - name: integer_width_boundaries
    value: 23/24, 255/256, 65535/65536, 2^32-1/2^32, both signs, and direct-range extrema
    purpose: Exercises every direct integer head transition and range rejection.
  - name: interval_shape_boundary
    value: closed/open/left_closed/right_closed over 1 and 2; closed/open over equal 1; Decimal, rational, IEEE, mixed, out-of-range, reversed, and left_open cases
    purpose: Distinguishes valid-but-unsupported integer intervals from every final invalid shape.
  - name: malformed_and_resource_boundary
    value: malformed hex witnesses, 2,200,000/2,200,001 typed-JSON bytes, 2,000 nested arrays, and a 137,492-child dense array
    purpose: Demonstrates stable bounded failure rather than host traceback or uncontrolled allocation.
  - name: digest_identifier_completion_boundary
    value: Complete raw 129-byte purpose and schema identifiers, plus a 129-byte declaration with only 128 content bytes
    purpose: Distinguishes digest.purpose and digest.object_class_schema from true digest.component_length truncation.
strengthenings:
  - name: strict_profile_rejection
    class: strengthening_justified
    reason: Unique content-addressed bytes require rejecting alternate encodings; this is a reviewed project choice, not proof convenience.
    approval_required: architecture, conformance, and checker review
  - name: closed_v1_value_tag_and_interval_set
    class: strengthening_justified
    reason: Prevents unstated tag, numeric, and interval semantics from entering artifact identity; source review, not ease of formalization, supplies the rationale.
    approval_required: architecture and semantic review
  - name: bounded_nonnormative_typed_json
    class: formalization_obligation
    reason: Diagnostic transport must not bypass resource or deterministic-result guarantees.
    approval_required: conformance and security review
  - name: field_specific_complete_identifier_failure
    class: formalization_obligation
    reason: Complete syntactically framed bytes must be classified by the invalid field rather than conflated with truncation; this refines result semantics without strengthening the accepted-input hypothesis set.
    approval_required: semantic, conformance, and cryptographic review
weakenings:
  - name: future_python_runtime_coverage
    class: candidate_for_weakening
    effect: CPython 3.14.7 and cross-platform evidence may extend the execution boundary only after exact workflow reproduction.
    disposition: Keep absent from current evidence.
  - name: future_public_helper_contract
    class: candidate_for_weakening
    effect: Direct helpers could become a hostile-input compatibility API only after separate exception-totality review.
    disposition: Keep the stable contract at the typed-JSON subprocess boundary.
  - name: future_interval_profile
    class: candidate_for_weakening
    effect: A versioned future profile could admit a broader endpoint domain only after defining exact equality, order, representation, and resource semantics.
    disposition: Do not infer or implement such support in statqed.cbor-core.v1.
attribution:
  - kind: reproduced
    work: RFC 8949
    detail: Preferred heads and core deterministic ordering are attributed to the Internet Standard.
  - kind: reproduced
    work: FIPS 180-4
    detail: SHA-256 function and output size are attributed to NIST; hashlib/OpenSSL execution remains operational evidence.
  - kind: specialized
    work: StatQED serialization candidate
    detail: Closed types, tags, integer-only interval shape, limits, strict rejection, identifiers, and complete-versus-truncated digest precedence are project specializations.
  - kind: original
    work: StatQED SQ-0005
    detail: Typed JSON, stable result envelope, ordered Python implementation, and six-component frame are project-original prototype work.
  - kind: reproduced
    work: CPython 3.12.13
    detail: Exact runtime behavior and license identity are operational observations, not normative semantics.
review:
  status: APPROVED
  reviewers:
    - /root/sq0005_source_curator
  statement_hash: 30ce16d0bc3fbb728f91820dbddf7335ed40f3c2f6815085dd392ef672cae414
```
