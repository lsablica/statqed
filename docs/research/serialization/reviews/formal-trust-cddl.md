# SQ-0005 formal, CDDL, and trust-boundary review

Status: **Experimental review record**

Disposition: **APPROVE**

Review date: 2026-08-09

Reviewer: `/root/sq0003_integrator`, acting as the independent formal,
published-syntax CDDL, and trust-boundary reviewer

## Decision

The exact subject below is approved for the SQ-0005 formal/CDDL/trust-boundary
gate. The candidate keeps CBOR structure, deterministic bytes, producer
semantic validity, separately owned object-schema validity, optional CDDL
shape, and digest verification as distinct phases. Provenance, proof validity,
and statistical validity are outside this profile and remain explicit
nonclaims.

The CDDL file is a small RFC 8610 published-syntax structural view. Its
restricted harness checks that exact source and matches only the recursively
allowed value shape after strict CBOR/profile validation. Neither the CDDL nor
its harness is treated as a byte canonicalizer, duplicate detector, Unicode
normalizer, schema validator, digest verifier, proof checker, or statistical
validator.

This reviewer did not author or edit the candidate, RFC, ADR, specification,
CDDL, fixtures, implementations, harness, or generated evidence. This record
does not by itself accept RFC-0001 or ADR-0004, approve either prototype for a
normative trusted path, or grant integration approval.

## Exact subject

The review was performed against commit
`410465d773fc011ee01e38e6e76a79a60efe8837`, exported to a clean review
directory. The disposition is hash-bound and does not extend to later edits.

| Subject | SHA-256 or identity |
|---|---|
| Reviewed commit | `410465d773fc011ee01e38e6e76a79a60efe8837` |
| `docs/research/serialization/semantic-value-model.md` | `a94588e54fdc3e2aa08e73f5f6e76bb71128940bb245305b2dec9dffa2ffcfb2` |
| `docs/research/serialization/profile-candidate.md` | `6cbf0f686a1f35b5c6fac8411ef5abc708c9c4410b5fdb2ee510c513df067d2f` |
| `rfcs/0001-deterministic-encoding.md` | `d4258501486affdaf99ec95322bae1e1212806c896e33360a17c137fd2f51106` |
| `docs/adr/0004-deterministic-cbor-cddl.md` | `004b41b65dc8450de6f0bd8431f7de2e1f885e95dfd985f50981e1c1c5c9e49d` |
| Matching RFC/ADR marked scope block | `737847efcdb917f8c3db8c05c314c85f62775fa8ca80638a56de69cadb0fc060` |
| `docs/spec/canonicalization.md` | `e0bc0628fd0ac05a43f06ac478c029e83a5daeb4fe88f2b00579d4f892cce61a` |
| `schemas/prototypes/cddl/profile-v1.cddl` | `05ee85b0d028af588ed9e95e83fdf017259988f05709de85f033cb0ab5badda0` |
| `schemas/prototypes/cddl/README.md` | `cae220ba606f6f9007a0b1a955465828f48442546a2a591d892f45dcd9ad6764` |
| `scripts/serialization/run_conformance.py` | `8a61f6deeeba7bed4e8bb7e0c8202fa0ce730d5328036365d8536ed5950fe01c` |
| Fixture catalog | `d5bf3079d9ff8119a2372873a1b116601011e78c30067bc1d05228211659b4d3` |
| Semantic fixture frozen commit | `b4d92a39e30fa5736c58bc71c57790ec215fbad7` |
| Semantic fixture content tree | `90fc4b5a1346f0693b84a0fa9a6a1e1fa4ac535aff2b83d6177313c6779fa3c8` |
| Digest-framing fixture | `36895de279202434a1511bb1bf552c199e55d57ee8a57a7d724772a737824d0b` |
| Python behavioral implementation commit | `89af5a7dbb837ea7d1557d1a715b34a814afdf95` |
| Python/Rust whitespace-clean frozen tree | `fd8dd9e344ff6bbe1488cb143f8b700c6c795efe` |
| Python implementation/lock subjects | `cc05dbf3d4996f44e204099ad335df843557571ae61aac8044903de5f9e41a9f` |
| Rust implementation/lock subjects | `cb3c03907bc7cdf6f495be7d98d795347b3b51c1415637a6b1e8d71f558027ea` |
| Generated result manifest | `e69e863053fad44faf2511cedbd53a13725e309cbdb0551621e217c2095dd6cd` |
| Generated results | `4e48d962644cec0f83b868ba13bcc62f3bc8cee4dca748fed10e3ad911195274` |
| Generated goldens index | `d5e572e44e7930e50f0d44fdf4ece04e7a01ab7d9a6817dda62cbec074183e1c` |
| Binary golden manifest | `8db0e43760421ea694e0e2d7095ade93a821ce5f3b7c66eaf954d7fe969af7a1` |
| Generated mutation results | `1b6c448a29ce76b83c5e85673731382dc24bba8a1902a7686988626015d22da6` |
| Generated failure results | `dbda36bd8752d5662f77fb2be3feb6d519e8164c7fe41fad734c05376114970b` |
| Primary-source audit manifest | `b3f70746a36c350590f2f77ffebb0e550773337d79db4103317426be94ac0a40` |
| Independent-lineage declaration | `7a7e48658e81e478c3858f265d24eb0c1402fa6169e7c03eb74363effb8208a4` |
| Evidence specification | `26fccac7ca0ab94e9ae270e92016aacc3d7ade25a28ee548347d0322dfc394c6` |
| Unchanged Draft RFC-0006 | `e834f805cc38fca2185433c72df4ac7db856c0ae20037fedcb57329a740b3429` |

The RFC and ADR marked scope blocks are byte-identical. RFC-0006 is
byte-identical to baseline commit
`8875d8f6fa8e3b45e706ea567d45448927a02efa` and remains Draft.

## Phase-separation audit

| Concern | Candidate owner and result | Review finding |
|---|---|---|
| Structural CBOR | `well_formedness` and `validity` | Parsing and CBOR validity precede profile checks. Raw map entries survive until typed duplicate checks complete. |
| Canonical bytes | `deterministic_profile` | Preferred heads, definite lengths, allowed types, and complete canonical-key byte ordering are checked independently of CDDL. Decode/re-encode is not accepted as proof of input conformance. |
| Producer semantic validity | `semantic_validity` | Explicit semantic atoms are classified before encoding and do not absorb object-schema invariants. |
| Object-schema validity | separately requested `schema_mismatch` | No object-schema validator is implemented or claimed by SQ-0005. The generic profile, CDDL matcher, and digest frame cannot manufacture this result. Future schema-owning work must provide its own vectors and validator. |
| CDDL structural shape | `cddl_shape` | Optional, separately requested shape evidence only. It runs after raw/profile validation. |
| Digest verification | `digest_verification` | The six-component length-prefixed frame binds exact identifiers and payload. Binding an object-class/schema identifier neither resolves the identifier nor proves payload conformance. |
| Provenance | outside the profile | Digest or replay evidence does not establish source lineage or truth. |
| Proof validity | outside the profile | No Lean declaration, theorem identity, proof lock, certificate semantics, or kernel-verification claim is introduced. |
| Statistical validity | outside the profile | No identification, inference, numerical correctness, or interpretation claim follows from structural, CDDL, digest, or differential agreement. |

The result precedence in the profile and RFC explicitly orders resource,
well-formedness, validity, expectedness, deterministic-profile, optional CDDL,
producer semantics, optional object schema, digest, and acceptance. Provenance,
proof, and statistical judgments are not smuggled into `accepted`.

The final digest-verification clarification also preserves the boundary: a
missing length prefix or incomplete declared component is
`digest.component_length`, while a fully present identifier that violates its
length, ASCII, grammar, fixed-value, or caller expectation receives the
field-specific `digest.*` code. The two added raw-frame fixtures exercise
overlong purpose and object-class/schema identifiers; Python, Rust, and the
reviewed expectation agree on `digest.purpose` and
`digest.object_class_schema`, respectively. Both cases leave CDDL not
applicable and establish no object-schema conformance.

## Published-syntax CDDL audit

`profile-v1.cddl` uses only the RFC 8610 prelude names and grammar needed for
five rules: `int`, `bstr`, `tstr`, arrays, maps, `bool`, and `nil`. It contains
no module/import draft syntax, control operators, tags, embedded CBOR, floats,
or wildcard `any` escape. The profile is intentionally more restrictive than
the CDDL data model; the strict profile decoder supplies the byte, range,
duplicate, ordering, Unicode, and resource checks before shape matching.

The harness's `validate_cddl_source` accepts only the reviewed five-rule text
after comment/whitespace handling and rejects excluded syntax. Its
`cddl_matches_typed` routine is a deliberately restricted recursive shape
matcher, not a general CDDL implementation. The generated results retain that
boundary:

- 66 accepted typed projections have `cddl.matched = true`;
- the one dedicated shape-negative fixture reports
  `cddl_shape / shape.cddl_mismatch`;
- 206 cases for earlier failures or non-shape operations record CDDL as not
  reached or not applicable;
- duplicate-map and non-preferred-byte failures are rejected before CDDL;
- composed and decomposed Unicode values both match the same text shape while
  remaining byte- and scalar-distinct; and
- the accepted schema-binding digest fixture remains explicitly not evidence
  of schema conformance.

Consequently CDDL cannot establish preferred heads, map order, duplicate
absence, Unicode or numeric normalization, canonical bytes, digest validity,
schema meaning, provenance, proof validity, or statistical validity. The
candidate states these limitations consistently in the profile, RFC, ADR,
specification, and CDDL README.

## Trust-boundary audit

The normative candidate is prose plus reviewed evidence; the Python and Rust
prototypes, their runtimes and dependencies, Cargo, the restricted CDDL
matcher, SHA-256 implementation, operating system, CI runner, and agents are
untrusted evidence producers outside a future normative verification-mode
trusted computing base. Differential agreement and byte-identical replay are
interoperability and reproducibility evidence, not proof.

The changed scope contains no production backend/frontend/Lean code, no
artifact envelope, no theorem-registry authority, no certificate checker, and
no logical-data identity. RFC-0006 remains unchanged and Draft. The candidate
does not claim arbitrary `.statqed` artifacts are kernel verified.

## Commands and evidence results

Executed from a clean archive of the exact reviewed commit:

```text
python3 scripts/serialization/run_conformance.py --verify
  PASS: 273 cases; 0 failures; 69 joint goldens; 20 mutations

git diff --quiet 8875d8f6fa8e3b45e706ea567d45448927a02efa \
  410465d773fc011ee01e38e6e76a79a60efe8837 -- \
  rfcs/0006-canonical-logical-data-digest.md
  PASS: RFC-0006 unchanged

git diff --check 8875d8f6fa8e3b45e706ea567d45448927a02efa \
  410465d773fc011ee01e38e6e76a79a60efe8837
  PASS: no whitespace errors

make check
  PASS for the pre-transition repository ledger and existing permanent gates

make list-work
  PASS: SQ-0005 IN_PROGRESS; SQ-0008 READY
```

The 273-case result contains 70 accepted, 203 rejected, 66 positive CDDL shape
observations, one negative CDDL shape observation, and zero conformance
failures. The class counts preserve the separate result owners: 15
well-formedness, 10 validity, 6 expectedness, 63 deterministic-profile, 1
CDDL-shape, 39 semantic-validity, 33 digest-verification, 15 resource, 17
differential-detection, and 4 operational-failure cases.

## Integration conditions and limitations

This specialist approval is not a clean-integration disposition. At the exact
reviewed pre-transition commit, the final content-addressed evidence manifest
and final ledger/review record did not yet exist, so
`scripts/serialization/check_evidence.py` correctly failed closed on the
missing `conformance/prototypes/evidence/evidence-manifest.json`. The final
integrator must add all review records, perform the atomic task transition,
generate and verify that manifest, run the permanent evidence and corruption
tests, reproduce the hosted workflow, and run all merge gates from a clean
checkout.

The three previously identified blank-line-at-EOF defects were removed at
`fd8dd9e344ff6bbe1488cb143f8b700c6c795efe`. The executable-tree hashes,
lineage records, generated manifest, harness bindings, and RFC evidence table
were regenerated around that exact whitespace-clean tree. The 273-case replay
remains byte-identical, and branch-wide `git diff --check` now passes; no
behavioral or trust-boundary change was introduced by that correction.

Any later edit to a hash-bound semantic, normative, CDDL, fixture,
implementation, or harness subject requires review of the new exact subject;
this approval must not be represented as covering such edits.
