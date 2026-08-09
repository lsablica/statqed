# Python reference-oracle lineage review

Status: **Experimental review record**

Disposition: **APPROVE**

Review date: 2026-08-09

Reviewer: `/root/sq0005_source_curator`, acting as the independent
reference-oracle lineage reviewer

## Decision

The Python reference oracle is approved as independent, non-normative
interoperability evidence for the exact subject below. The approval covers the
documented direct-from-candidate lineage, the bounded typed-JSON subprocess
contract, the project-original ordered-entry parser and encoder, the stated
profile/result behavior, and the reproduced CPython 3.12.13 environment. It
does not promote the oracle, CPython, OpenSSL, the conformance harness, or any
prototype output into normative or kernel-verified evidence.

This is an independent review role, distinct from the
`/root/sq0005_python_oracle` author role recorded by the task orchestration.
The shared Git author identity `Lukas <33362522+lsablica@users.noreply.github.com>`
does not by itself demonstrate review independence. The oracle author cannot
be the sole reviewer of this lineage claim; this review record and its distinct
role provenance must be retained.

## Exact subject

- Commit: `b5fb813c211317c4e3e48ea8b8c232fbd14cf82b`
- Commit tree: `8e2f4639a013ae91b5414cd5974a1e1da0b89487`
- Parent: `15cd3f081a2e2579b7753726ca110ec9ba7870b8`
- Python-oracle Git tree: `805f386c3aa23c717923da1562de52c1628ae62f`
- Semantic-corpus Git tree: `39414e574e6a703173eecaa3f8df8c58e9bb050d`
- Python-oracle content-tree SHA-256: `697fa37da50ba40c118564a3e40760c508ff092942524ceb63659766d453255d`
- Semantic-corpus content-tree SHA-256: `d538721966242fe1cea9ae7f10bbbbc132bb7b84fe9777b9b426ecbd68a1f885`

The content-tree hashes are SHA-256 over each sorted relative path, one NUL
byte, and the file bytes, excluding `target` and `__pycache__` paths. Review
execution used a `git archive` of the exact commit because the shared worktree
contained later, unrelated corpus and Rust edits.

### Candidate inputs and lineage records

| File | SHA-256 |
|---|---|
| `docs/research/serialization/semantic-value-model.md` | `fc7d86cfe4eae00d25afeb1cd8601dff6d5173dce728c5f4a507b20d5fa34dca` |
| `docs/research/serialization/profile-candidate.md` | `d07816f7f3fadeb07b91196691848f3933a13f96503c86ed24c2ed9d42ed45bb` |
| `schemas/prototypes/lineage.json` | `7a7e48658e81e478c3858f265d24eb0c1402fa6169e7c03eb74363effb8208a4` |
| `source-audits/encoding/SA-SQ0005-CBOR.yaml` | `efb3c29e775a2a0191aa89a86e2b6a31eb5df181e1bc034f30f3ae7c4dba8164` |
| `source-audits/encoding/SA-SQ0005-CRYPTO.yaml` | `aedbd89fea0b3b34e2e11680b04e75623cdf69e2e02f5b176a89a28da7fab103` |
| `source-audits/encoding/SA-SQ0005-PROTOTYPES.yaml` | `e5e1510b8145a06502e953e7ed0b1d71d2b782ff85a6a93af9e2407ceff76c6d` |

### Oracle source, documentation, and tests

| File | SHA-256 |
|---|---|
| `schemas/prototypes/python-oracle/.python-version` | `aa0d6581054e6e4ff3f91839deca7a854ad37221b8784d060b42d0f847ff1a3b` |
| `schemas/prototypes/python-oracle/ENVIRONMENT.md` | `a284ec1c00b8ad0f1ae0bf96f59b7ab2456ca7f81e9a4ab935b9718c017d4d3d` |
| `schemas/prototypes/python-oracle/LINEAGE.md` | `ad59ef6713239db37ccc823924869cbe11ebd2bdeaf7146b10b457c1edb90cee` |
| `schemas/prototypes/python-oracle/PSF-LICENSE-2.0.txt` | `b683dca09ef30505ae793c3948beb1861d8a1af75d03010ee7cf7e20bab2b74f` |
| `schemas/prototypes/python-oracle/README.md` | `e0d06b4708d1e723140eaafc36928498d4d3e1191b80032c18a1e1fee10feb2c` |
| `schemas/prototypes/python-oracle/requirements.txt` | `fe1b58fd32e3f1cc2d11a6a70c8d179ae0b6e150ef651823a100f9343fc27bd0` |
| `schemas/prototypes/python-oracle/statqed_oracle/__init__.py` | `3bcbb5207f8241a011cdc61fc8d5d0c064458a96b531dfc9fdb30cc677dc7fe0` |
| `schemas/prototypes/python-oracle/statqed_oracle/cli.py` | `eed36baf0b98a2bb70f3eb0569ccc4a2f3e547768cc0e1a841376701f8dd0ec9` |
| `schemas/prototypes/python-oracle/statqed_oracle/oracle.py` | `53f9ae6650ee0c9015274cff96e926375b315a36ee43e4d3ad4d313756d5d41d` |
| `schemas/prototypes/python-oracle/tests/test_decoding.py` | `3f1c9a8be9c41c05e99b514f5b3e897bc6c3c67089c5fd4a6970d72948bc14af` |
| `schemas/prototypes/python-oracle/tests/test_digest_and_cli.py` | `0f058ce276f70fe2b0176e5f5b61c73c58460eb01e3c937b6528c95b87eee269` |
| `schemas/prototypes/python-oracle/tests/test_encoding.py` | `fd6afe5bb2518c1b50e6a2609215444bf3cb0844c9bba94db2a51617c8d2223d` |
| `schemas/prototypes/python-oracle/tests/test_resources.py` | `e1104fb200111b7ce69b834b1470ebd00e05dfb11bc903360c13448399553f36` |

`requirements.txt` contains only its explanatory comment; it declares no
package requirement.

### Semantic corpus and structural input

| File | SHA-256 |
|---|---|
| `conformance/prototypes/fixtures/semantic-v1/catalog.json` | `2c5269e37129a27922dbeecbbae63a2bd6a925e434a5da938315a03b423e5e70` |
| `conformance/prototypes/fixtures/semantic-v1/atoms-and-widths.json` | `2ffec8250ace8283959db11a29d2d7c2b55500429065d484394732c59e52dcd9` |
| `conformance/prototypes/fixtures/semantic-v1/differential-mutants.json` | `313a784148be66fa471c2684be27512fbf5e0f446f7681dd27e8317b36c882e6` |
| `conformance/prototypes/fixtures/semantic-v1/digest-framing.json` | `75b11a2b6069f759710cd132d92a8ef1d91a0dbc1488f85f14f3920819277a19` |
| `conformance/prototypes/fixtures/semantic-v1/malformed-and-strictness.json` | `b6af575d7111def454a642fa3052bc626f2aea2a4fee76cf7719677739fcf2af` |
| `conformance/prototypes/fixtures/semantic-v1/maps-and-unicode.json` | `42fa6c9144c353ba6eb9d343b96d8b0e61e5ec4e472ff10e1ee1b769f2b704d6` |
| `conformance/prototypes/fixtures/semantic-v1/numeric-tags-extensions.json` | `2b1be7521420f0f20ce2def17e7e013baa892983f451ca0ea35fea6a47648492` |
| `conformance/prototypes/fixtures/semantic-v1/resources.json` | `7f0f02fa85fe96472884bc15f157f474cebebc7560d36991b69501f7cf067a31` |
| `schemas/prototypes/cddl/profile-v1.cddl` | `05ee85b0d028af588ed9e95e83fdf017259988f05709de85f033cb0ab5badda0` |

## Lineage and behavior findings

The lineage claim is supported, with the epistemic limitation stated below:

- The candidate model/profile hashes in `LINEAGE.md` match the exact files.
  The initial Python implementation commit
  `2c63655ec3c16611786d66038d5c45bc944190de` has the reviewed profile commit
  `ac5ce971eca4f46e7725f56599e5a30e7025bd22` as its parent. The Rust prototype
  first enters tracked history later, at
  `2f0d778fff38bedd512dadd8603fc59e38be75b4`.
- `schemas/prototypes/lineage.json` records empty `calls` and
  `consumes_outputs_from` arrays for both implementations and names the Python
  parser/canonicalizer as direct, project-original code.
- Static inspection found no Rust invocation, Rust path, generated/golden
  input, third-party CBOR package, or shared canonicalizer in the Python
  implementation. It has no subprocess import. Tests contain specification
  examples and independently assembled frames, not Rust-produced expectations.
- The implementation defines its own lossless-enough `RawItem`/`RawEntry`
  representation. `_parse_map` retains the complete entry tuple, and
  `_check_map` validates allowed key types, then typed-equal duplicates, then
  complete canonical-key-byte order. No host dictionary is constructed before
  those decisions. Encoder maps likewise reject typed duplicates and sort by
  complete encoded key bytes, selecting RFC 8949 core order rather than the
  conflicting length-first variant.
- Direct-range integers cover `[-2^64, 2^64-1]` and all 1/2/3/5/9-byte head
  boundaries. Out-of-range integers do not fall back to bignums. Profile tests
  cover preferred heads, definite containers, UTF-8, exact Unicode scalar
  preservation, tag/float/simple rejection, narrow map keys, duplicate/order
  precedence, expectedness, resource classes, semantic unsupported classes,
  extension precedence, and six-component digest construction/verification.
- The stable interface is the bounded typed-JSON CLI. The reviewed fixes make
  quoted 5,000-digit integers lexical, unquoted huge JSON numbers independent
  of `PYTHONINTMAXSTRDIGITS`, excessive JSON/semantic nesting fail closed,
  collection/item limits apply before recursive construction, and Decimal
  interval comparison avoid materialized powers. The specifically requested
  `Integer(True)`, `Integer(1.5)`, and `TextString(7)` direct-helper witnesses
  return `semantic.unsupported_value` Results without exceptions.

The external standards do not themselves select all StatQED behavior. RFC 8949
STD 94, sections 4.1 and 4.2.1, is the primary source for preferred/core
deterministic encoding; sections 5.3 and 5.6 are the primary validity and map
semantics anchors ([RFC 8949](https://www.rfc-editor.org/rfc/rfc8949.html),
DOI `10.17487/RFC8949`). The conflicting length-first variant is section
4.2.3 and is explicitly excluded. FIPS 180-4 sections 5.1.1, 5.2.1, 5.3.3,
and 6.2 define SHA-256, not the project-original StatQED frame
([FIPS 180-4](https://csrc.nist.gov/pubs/fips/180-4/upd1/final), DOI
`10.6028/NIST.FIPS.180-4`). Strict rejection, the accepted value subset,
resource bounds, typed JSON, result precedence, identifiers, and the six-field
frame are reviewed project specializations; they are not attributed to the
standards.

## Environment, dependencies, and license

The exact local runtime reproduced as:

```text
Python 3.12.13 | packaged by conda-forge
build hd63d673_0_cpython; cache tag cpython-312
GCC 14.3.0
Linux 7.0.0-28-generic x86_64; glibc 2.39
OpenSSL 3.6.3 9 Jun 2026
Unicode database 15.0.0; little-endian host
```

The implementation import set is exactly `__future__`, `argparse`,
`dataclasses`, `fractions`, `hashlib`, `hmac`, `json`, `math`, `re`, `struct`,
`sys`, and `typing`; comparison with `sys.stdlib_module_names` found no
non-standard-library import. The full suite passed with `-S`, and `sys.path`
contained no site-packages entry. This supports zero third-party Python
dependencies; it does not remove CPython, its standard library, OpenSSL, libc,
or the operating system from the operational dependency boundary.

The retained `PSF-LICENSE-2.0.txt` hash is recorded above. It is correctly
described as only the PSF License Version 2 portion, not the full runtime
distribution license. The exact installed CPython 3.12.13
`lib/python3.12/LICENSE.txt` hash reproduced as
`3b2f81fe21d181c499c59a256c8e1968455d6689d269aa85373bfb6af41da3bf`;
it includes the current PSF notice, historical licenses, and component terms.
Because this prototype invokes rather than redistributes CPython, the record is
adequate for this Experimental execution evidence. Redistribution remains
blocked on a fresh complete license/notices audit. The official versioned
upstream locator is the [CPython 3.12.13 LICENSE](https://github.com/python/cpython/blob/v3.12.13/LICENSE).

CPython 3.14.7 is explicitly only a planned SQ-0005 CI coverage point. No
3.14.7 oracle run is claimed or inferred here. It becomes evidence only when a
serialization-prototype workflow runs this exact oracle and records the runner
metadata.

## Reproduced commands and results

The exact unit-suite command was:

```bash
env -i PATH=/usr/bin:/bin \
  PYTHONPATH=schemas/prototypes/python-oracle \
  PYTHONDONTWRITEBYTECODE=1 PYTHONWARNINGS=error \
  LANG=C.UTF-8 LC_ALL=C.UTF-8 TZ=UTC \
  /home/lukas/miniconda3/envs/stats/bin/python -S -m unittest discover \
  -s schemas/prototypes/python-oracle/tests -p 'test_*.py' -v
```

Result: **56 tests passed** in 0.738 seconds, with no warning promoted to an
error and no third-party site initialization.

Independent adversarial replay against the same archived subject produced:

| Witness | Result |
|---|---|
| Quoted 5,000-digit integer, 5,029 input bytes | exit 1; `semantic_validity / semantic.integer_range`; zero stderr |
| Typed JSON exactly 2,200,000 bytes | exit 0; accepted; zero stderr |
| Typed JSON 2,200,001 bytes | exit 1; `resource / resource.input_bytes`; zero stderr |
| 2,000 nested typed arrays, 54,015 bytes | exit 1; `resource / resource.depth`; zero stderr |
| Equal Decimal interval endpoints with exponent 1,000,000,000, 176 bytes | exit 1; `semantic_validity / semantic.unsupported_interval`; zero stderr; completed below five seconds |
| Unquoted 5,000-digit JSON number under `PYTHONINTMAXSTRDIGITS=4300` and `0` | byte-identical output SHA-256 `600dec9603e92fbc3fcde78ea3503683e2cd33ae77af4f502c5bacbd39b3fde3`; `semantic.unsupported_value`; zero stderr |
| `Integer(True)`, `Integer(1.5)`, `TextString(7)` | three rejected Results; `semantic.unsupported_value`; no exception |
| Same accepted map under hash seeds `0`, `1`, and `random`, UTC/Vienna timezone variants | one unique exit/stdout/stderr tuple; stdout SHA-256 `8a58d97e87db408738bfeb9e9adf9936fd057fc2c9a2886f93a63a00f111ba45`; zero stderr |

Additional adversarial checks compared 100,000 deterministic random normalized
Decimal pairs against exact `Fraction` arithmetic with zero mismatches. Typed
JSON collection probes returned the expected accepted/bounded diagnostic at
1,024 array children, `resource.array_items` at 1,025, and
`resource.total_items` when the semantic projection crossed 4,096 items.
Twenty additional mistyped direct-helper values across the accepted and
unsupported constructor families probed produced Results with zero leaked
exceptions.

Allocation-focused CLI probes were also run under the harness's 128 MiB
address-space ceiling and five-second timeout. A 2,199,898-byte typed array with
137,492 null children returned `resource.array_items`, and a 2,100,001-byte
generic JSON array containing 700,000 empty objects returned a stable rejection;
both completed below five seconds with zero stderr. These observations support
the reviewed input/collection boundary on the exact platform, but are not a
cross-runtime memory proof.

The read-only Python-side corpus replay used the current untracked harness
snapshot with SHA-256
`c3c6064cbebe41d4af8296ce9fc9ad2e2ee458dc33f3adec20929afbe680575c`,
redirected to the exact archived `b5fb813` roots. Its newer expected-count
constant was set in memory to the exact subject catalogue count; no generated
files were written, no Rust binary was supplied, and no Rust output was read.
It validated 253 catalogue cases, then executed 230 Python-owned and 6
harness-owned non-mutant cases; 17 harness mutation specifications were
excluded. All 236 executed cases matched their precommitted acceptance,
result-class, stable-code, byte, projection, and CDDL expectations: **zero
mismatches**. This replay is supplemental execution evidence, not a
content-addressed harness approval.

`make check` passed: repository guardrails passed with 60 backlog tasks and 21
detailed contracts, and the SQ-0002 evidence verifier reported 75 probes and 6
recommendations. `git diff-tree --check b5fb813^ b5fb813` also passed.

## Corrections resolved before approval

The reviewer withheld disposition until all observed corrections were frozen:

1. `d0f13f1` made the 2,200,000-byte stdin bound explicit, made a quoted
   5,000-digit integer return stable JSON, made mistyped accepted constructors
   fail closed, and corrected the runtime-license description.
2. `028a3fa` corrected a CPython 3.14.7 CI overclaim to planned coverage.
3. `b5fb813` made unquoted JSON integer tokens environment-independent, mapped
   JSON/projection depth and collection exhaustion to stable Results, and
   replaced Decimal interval power materialization with exact bounded
   comparison.

No unresolved blocking finding remains for the exact subject.

## Limitations and nonclaims

- Direct-from-spec origin is supported by the content-addressed attestation,
  commit ordering, aggregate lineage record, source structure, dependency
  scan, and test construction. A repository audit cannot prove the negative
  fact of what an author privately viewed; future review must preserve the
  author/reviewer role record and must not replace it with the shared Git
  identity.
- Approval is for the validated typed-JSON subprocess contract and the tested
  constructor-to-`encode` cases. The direct Python helper surface is not a
  public compatibility contract for arbitrary hostile Python objects:
  deliberately passing a `str` payload to `build_digest_frame` or a `str`
  frame to `verify_digest_frame` raises host `TypeError`. Those values are
  type-checked before dispatch through the approved CLI. Do not broaden the
  direct-helper claim without a separate exception-totality/API review.
- The semantic corpus at this subject is finite. Zero mismatches and mutation
  coverage are not a proof of implementation correctness or parser safety.
- The Python-only replay does not establish differential agreement, because
  Rust was deliberately unavailable to this lineage review. No Rust output is
  an expected truth for the Python oracle.
- The local evidence is Linux x86-64 CPython 3.12.13 only. CPython 3.14.7,
  other supported Python versions, other operating systems, and other crypto
  backends remain untested here.
- The retained PSF-only text is not a complete redistribution record. Full
  runtime and bundled-component terms must be re-audited before redistribution.
- SHA-256 comparison is computational evidence under the external hash and
  runtime assumptions. It does not prove payload equality, provenance,
  identification, inference, numerical correctness, interpretation, or kernel
  verification.
- Status remains Experimental. This review does not accept an RFC, freeze a
  public theorem or artifact signature, or authorize production use.

## Source-audit-compatible classification

```yaml
audit_id: SA-SQ0005-PYTHON-ORACLE-LINEAGE
subject: Independent Python reference-oracle lineage and reproduced behavior
source:
  work: RFC 8949, FIPS 180-4, StatQED serialization candidates, and CPython 3.12.13 runtime
  version: RFC 8949 STD 94; FIPS 180-4 Update 1; StatQED commit b5fb813c211317c4e3e48ea8b8c232fbd14cf82b; CPython 3.12.13
  locator: https://www.rfc-editor.org/rfc/rfc8949.html; https://csrc.nist.gov/pubs/fips/180-4/upd1/final; docs/research/serialization/profile-candidate.md; docs/research/serialization/semantic-value-model.md; schemas/prototypes/python-oracle/LINEAGE.md; schemas/prototypes/python-oracle/ENVIRONMENT.md
  persistent_id: https://doi.org/10.17487/RFC8949; https://doi.org/10.6028/NIST.FIPS.180-4; git:b5fb813c211317c4e3e48ea8b8c232fbd14cf82b
controlled_statement: >-
  The Python oracle at commit b5fb813c211317c4e3e48ea8b8c232fbd14cf82b is an Experimental, non-normative, direct-from-candidate implementation of statqed.cbor-core.v1 whose reviewed stable interface is bounded typed JSON over standard input and output; it preserves ordered raw map entries before allowed-key duplicate and order validation, implements the candidate integer/profile/result and six-component SHA-256 behavior, has no third-party Python or Rust/shared-canonicalizer dependency, and is reproduced locally only on conda-forge CPython 3.12.13. CPython 3.14.7 oracle CI coverage is planned, not evidence at this subject.
hypotheses:
  - name: exact_candidate_inputs
    class: source_explicit
    source_anchor: schemas/prototypes/python-oracle/LINEAGE.md lines 7-12
    notes: Both recorded hashes match the exact reviewed candidate files.
  - name: core_deterministic_order
    class: source_explicit
    source_anchor: RFC 8949 Section 4.2.1; profile-candidate.md lines 23 and 115-157
    notes: Complete canonical key bytes are compared lexicographically; length-first ordering is excluded.
  - name: preferred_and_strict_profile
    class: strengthening_justified
    source_anchor: RFC 8949 Sections 4.1-4.2; profile-candidate.md lines 21-33 and 418-432
    notes: Strict rejection and the narrow value/tag policy are project specializations chosen for unique artifact bytes, not implementation convenience.
  - name: ordered_raw_map_entries
    class: formalization_obligation
    source_anchor: RFC 8949 Sections 5.3 and 5.6; semantic-value-model.md lines 84-105
    notes: The parser must retain entries and compare allowed typed keys before host-map collapse; source and tests satisfy the obligation for this prototype.
  - name: direct_range_integer_model
    class: source_explicit
    source_anchor: profile-candidate.md lines 35-85 and 418-419
    notes: The reviewed domain is -2^64 through 2^64-1 with shortest heads and no bignum fallback.
  - name: sha256_algorithm
    class: source_explicit
    source_anchor: FIPS 180-4 Sections 5.1.1, 5.2.1, 5.3.3, and 6.2
    notes: FIPS defines SHA-256 and its 256-bit result, not the StatQED frame semantics.
  - name: statqed_digest_frame
    class: formalization_obligation
    source_anchor: profile-candidate.md lines 328-415
    notes: The six-component length-prefixed frame is project-original and separately cryptographically reviewed.
  - name: direct_from_spec_independence
    class: source_implicit_justified
    source_anchor: schemas/prototypes/python-oracle/LINEAGE.md lines 7-33; schemas/prototypes/lineage.json
    notes: Content hashes, history, code structure, and dependency scans support the attestation, but cannot prove private author conduct.
  - name: no_third_party_python_dependency
    class: formalization_obligation
    source_anchor: requirements.txt; ENVIRONMENT.md lines 18-23
    notes: Standard-library-only AST imports and successful -S execution discharge the prototype obligation at this subject.
  - name: bounded_deterministic_typed_json
    class: formalization_obligation
    source_anchor: README.md typed-JSON and boundary sections
    notes: Exact and adversarial tests cover byte, nesting, item, collection, integer-token, and Decimal-amplification boundaries.
  - name: exact_cpython_31213_execution
    class: not_applicable
    source_anchor: ENVIRONMENT.md lines 5-16 and local runtime observation
    notes: This is a reproduced software-environment fact, not a mathematical hypothesis.
  - name: cpython_3147_oracle_evidence
    class: not_applicable
    source_anchor: ENVIRONMENT.md lines 25-30
    notes: Explicitly planned and absent at this subject; no 3.14.7 result is inferred.
  - name: complete_runtime_license_is_retained
    class: not_applicable
    source_anchor: ENVIRONMENT.md lines 32-42
    notes: Not claimed. Only PSF-2.0 text is retained; the complete installed license is hash-recorded and redistribution requires re-audit.
  - name: author_may_be_sole_reviewer
    class: strengthening_unjustified
    source_anchor: agents/protocols/source-lineage.md and repository independent-review rule
    notes: Rejected. A distinct reviewer role is required even though the environment uses one Git identity.
variants:
  - name: RFC 8949 core deterministic encoding
    locator: RFC 8949 Section 4.2.1
    conflict: Lexicographic order of full deterministic key encodings.
    disposition: Selected by the candidate and implemented directly.
  - name: RFC 8949 length-first deterministic encoding
    locator: RFC 8949 Section 4.2.3
    conflict: Encoded length is compared before lexical bytes.
    disposition: Explicitly excluded; convenience library canonical modes do not change the candidate.
  - name: lossy host-map decoding
    locator: RFC 8949 Sections 5.3 and 5.6
    conflict: First-wins, last-wins, or collapse can erase duplicate evidence.
    disposition: Excluded; ordered raw entries are retained through validation.
  - name: permissive decode-and-reencode
    locator: RFC 8949 Section 5.4
    conflict: Repairs non-profile bytes instead of rejecting them.
    disposition: Excluded from the strict artifact boundary.
  - name: generic CBOR or shared canonicalizer
    locator: source-audits/encoding/SA-SQ0005-PROTOTYPES.yaml
    conflict: Package defaults can implement a different ordering and share lineage with Rust.
    disposition: Excluded from the Python oracle implementation.
  - name: CPython 3.12.13 local execution
    locator: schemas/prototypes/python-oracle/ENVIRONMENT.md
    conflict: Reproduced on one Linux x86-64 interpreter and crypto backend.
    disposition: Approved as the exact local evidence boundary.
  - name: CPython 3.14.7 CI execution
    locator: schemas/prototypes/python-oracle/ENVIRONMENT.md lines 25-30
    conflict: Planned coverage has no oracle run or runner record at this subject.
    disposition: Retain as planned only.
  - name: PSF-only retained text versus complete runtime license
    locator: schemas/prototypes/python-oracle/ENVIRONMENT.md lines 32-42
    conflict: The retained text omits historical and component terms in the installed distribution.
    disposition: Adequate for non-redistributed execution inventory only; re-audit before redistribution.
concept_mapping:
  - source_concept: core deterministic CBOR
    statqed_concept: statqed.cbor-core.v1 canonical bytes
    obligation: Enforce preferred heads, definite lengths, selected key order, and the closed value subset.
  - source_concept: map key equivalence
    statqed_concept: typed Integer/TextString equality over RawEntry sequences
    obligation: Detect duplicates before map collapse and before ordering disposition.
  - source_concept: SHA-256 message
    statqed_concept: exact six-component StatQED length-prefixed frame bytes
    obligation: Keep algorithm correctness separate from frame injectivity and schema meaning.
  - source_concept: Python package dependency
    statqed_concept: untrusted operational implementation dependency
    obligation: Run without site packages and retain exact runtime/license evidence.
quantifiers:
  - statement: For every typed semantic value admitted by the candidate and its resource limits, encoding yields the selected profile bytes or a stable Result.
    source_status: Project implementation obligation; tested but not formally proved.
  - statement: For every raw input at or below the CBOR input bound, decoding preserves the first item and raw map entries until precedence checks complete.
    source_status: Project implementation obligation; finite corpus and unit evidence only.
  - statement: For all 253 exact corpus cases, 236 non-mutant Python/harness paths were replayed; the 17 mutant specifications were not Python-oracle executions.
    source_status: Exact local observation at the reviewed subject.
  - statement: For every host/runtime configuration, CLI output is identical.
    source_status: Not established; only the exact runtime and reported environment variants were tested.
randomness_scopes: []
nonvacuity_witnesses:
  - name: core_order_discriminator
    value: Integer(-1) and Integer(100) map keys
    purpose: Core order accepts a2 18 64 f6 20 f6 while length-first order is rejected.
  - name: typed_duplicate_before_collapse
    value: Integer(0) encoded as 00 and non-preferred 1800 in one raw map
    purpose: Requires validity.map_duplicate before map repair or order failure.
  - name: integer_width_boundaries
    value: 23/24, 255/256, 65535/65536, 2^32-1/2^32, both signs, and direct-range extrema
    purpose: Exercises every direct integer head transition and range rejection.
  - name: diagnostic_resource_witnesses
    value: 2,200,000/2,200,001 input bytes, 2,000 nested arrays, and Decimal exponent 1,000,000,000
    purpose: Demonstrates bounded, stable subprocess failure rather than host traceback or amplification.
strengthenings:
  - name: strict_profile_rejection
    class: strengthening_justified
    reason: Unique content-addressed bytes require rejection of alternate encodings; this is a reviewed project choice, not a proof convenience.
    approval_required: architecture, conformance, and checker review
  - name: closed_v1_value_and_tag_set
    class: strengthening_justified
    reason: Prevents unstated tag and numeric semantics from entering artifact identity.
    approval_required: architecture and semantic review
  - name: bounded_nonnormative_typed_json
    class: formalization_obligation
    reason: The diagnostic transport must not bypass profile resource or deterministic-result guarantees.
    approval_required: conformance and security review
weakenings:
  - name: future_python_runtime_coverage
    class: candidate_for_weakening
    effect: CPython 3.14.7 and cross-platform evidence may extend the execution boundary only after exact workflow reproduction.
    disposition: Keep absent from current evidence.
  - name: future_public_helper_contract
    class: candidate_for_weakening
    effect: Direct Python helpers could become a supported hostile-input API only after a separate API and exception-totality review.
    disposition: Keep the stable contract at the typed-JSON subprocess boundary.
attribution:
  - kind: reproduced
    work: RFC 8949
    detail: Preferred heads and core deterministic ordering are attributed to the Internet Standard.
  - kind: reproduced
    work: FIPS 180-4
    detail: SHA-256 function and output size are attributed to NIST; hashlib/OpenSSL execution remains operational evidence.
  - kind: specialized
    work: StatQED serialization candidate
    detail: Closed types, tags, limits, precedence, strict rejection, and identifiers are project specializations.
  - kind: original
    work: StatQED SQ-0005
    detail: Typed JSON, stable result envelope, ordered Python implementation, and six-component frame are project-original prototype work.
review:
  status: APPROVED
  reviewers:
    - /root/sq0005_source_curator
  statement_hash: a71301a9f61598096c6be84644b1addfefabacf00a94c49158bc0d03da1cf625
```
