# SQ-0005 cryptographic-framing review

Status: Experimental review record

Disposition: **APPROVE**

Reviewer: `/root/sq0002_release_security_adversarial`, acting as the distinct
cryptographic-framing and counterexample reviewer

Review date and source-retrieval date: 2026-08-09

## Decision and exact subject

The final review was executed from an isolated archive of commit
`410465d773fc011ee01e38e6e76a79a60efe8837`, repository tree
`a93ac8fe4befe4da52ff0ef5ee928ea04679b85c`. The last three commits after the
substantive framing correction removed three end-of-file blank lines, rebound
the prototype source-tree identities, and refreshed RFC-0001's evidence table;
they did not change the framing algorithm or its observable behavior.

This disposition approves only the exact generic, data-free SHA-256 framing
candidate and its Experimental evidence identified below. It does not by
itself accept Draft RFC-0001, update ADR-0004, approve a production backend or
artifact format, or resolve RFC-0006.

### Candidate and source subjects

| Subject | SHA-256 |
|---|---|
| `docs/research/serialization/profile-candidate.md` | `6cbf0f686a1f35b5c6fac8411ef5abc708c9c4410b5fdb2ee510c513df067d2f` |
| `rfcs/0001-deterministic-encoding.md` | `d4258501486affdaf99ec95322bae1e1212806c896e33360a17c137fd2f51106` |
| `docs/spec/canonicalization.md` | `e0bc0628fd0ac05a43f06ac478c029e83a5daeb4fe88f2b00579d4f892cce61a` |
| `source-audits/encoding/SA-SQ0005-CRYPTO.yaml` | `d3feb17277b3fccafa2201f36290d2c89be5a98ab953fd75dfd749bb6da3ae36` |
| `source-audits/encoding/manifest.json` | `b3f70746a36c350590f2f77ffebb0e550773337d79db4103317426be94ac0a40` |

The verified nine-file source-audit tree is
`75f8fe98338e4800230a7b9a9da7988f728bdf2516b170e969134482511686f2`.

### Implementation subjects

| Subject | SHA-256 |
|---|---|
| Python executable/lock subject | `cc05dbf3d4996f44e204099ad335df843557571ae61aac8044903de5f9e41a9f` |
| `schemas/prototypes/python-oracle/statqed_oracle/oracle.py` | `784bbbef227bdff5728622e35d9c46071ea776dd5c0bbbd2eb5ddcc2f1e04d00` |
| `schemas/prototypes/python-oracle/statqed_oracle/cli.py` | `eed36baf0b98a2bb70f3eb0569ccc4a2f3e547768cc0e1a841376701f8dd0ec9` |
| `schemas/prototypes/python-oracle/tests/test_digest_and_cli.py` | `d826b8fbf8a4896fcb11a85ddaa789ea003fe551c308b3072128b294dbfb7ff4` |
| `schemas/prototypes/python-oracle/LINEAGE.md` | `8dfe50d1a4010984881c77cd48fa3eca14e307e71d8cc0b5afed48d3e6babd92` |
| Rust executable/lock subject | `cb3c03907bc7cdf6f495be7d98d795347b3b51c1415637a6b1e8d71f558027ea` |
| `schemas/prototypes/rust-cbor/src/lib.rs` | `bf5cd89521f4151197beeb8a9e07d9a92503e615de9c9da2aec1d6f73834d70d` |
| `schemas/prototypes/rust-cbor/src/main.rs` | `a48b67f10d0a7a77d553b226c73d02dae48057d66be83cfd6c517c8ae925f211` |
| `schemas/prototypes/rust-cbor/tests/profile.rs` | `f278b61f959f4f71b707c2a424b879fbb71922a85e5b79ecbf3258ee729d1ae3` |
| `schemas/prototypes/rust-cbor/tests/cli.rs` | `311f5f7faa50664e1f89dc4cb6f7a7a39abf65a1a05f8b809e9b23c1987d2ba9` |
| `schemas/prototypes/rust-cbor/Cargo.lock` | `2e9c4f95aa0aa54ab2338e980d388f9f0223be8964d94f82d82f086f2dadb180` |
| `schemas/prototypes/rust-cbor/LINEAGE.md` | `6136314a0c7ac9b971f636e520e8d9dd0d94548f39a96a891d34a37ac9e1dd1a` |

The manifest freezes both prototype source subjects at the whitespace-clean
commit `fd8dd9e344ff6bbe1488cb143f8b700c6c795efe`. Python and Rust remain
independent, non-normative implementations; agreement between them is
interoperability evidence, not an authority transfer.

### Corpus, results, and golden subjects

| Subject | SHA-256 |
|---|---|
| Digest-framing fixture | `36895de279202434a1511bb1bf552c199e55d57ee8a57a7d724772a737824d0b` |
| Semantic fixture tree | `90fc4b5a1346f0693b84a0fa9a6a1e1fa4ac535aff2b83d6177313c6779fa3c8` |
| Generated manifest | `e69e863053fad44faf2511cedbd53a13725e309cbdb0551621e217c2095dd6cd` |
| Differential results | `4e48d962644cec0f83b868ba13bcc62f3bc8cee4dca748fed10e3ad911195274` |
| Deliberate mutations | `1b6c448a29ce76b83c5e85673731382dc24bba8a1902a7686988626015d22da6` |
| Binary golden manifest | `8db0e43760421ea694e0e2d7095ade93a821ce5f3b7c66eaf954d7fe969af7a1` |
| `DIGEST-FRAME-BASELINE.frame` | `53c209c1a299f073ec8f66ef4fe28581b6c1ad282731b357def61f2f77ef4749` |
| `DIGEST-SCHEMA-BINDING-NOT-CONFORMANCE.frame` | `a041b193bc01ee5a13c88c0944f12b6373a11d843c6aaea4021e33fbd01ba8d9` |
| `DIGEST-FRAME-ATTAINABLE-MAX.frame` | `c0ef40eaa288a90d68ab665d482a544cd335d464d90480cbcdb6d2c5a93dab48` |
| Conformance runner | `8a61f6deeeba7bed4e8bb7e0c8202fa0ce730d5328036365d8536ed5950fe01c` |
| Permanent evidence verifier | `864568ef80e2c1f0517999cf45130f744c6599eab34040932f1fa0258e0c7d0e` |
| Serialization workflow | `ee7b9643374d001cd595f4232d42780bdf70b8c78c2cbe0396551501d3674117` |

## Primary-source assessment

The final cryptographic audit correctly distinguishes sourced SHA-256 facts
from StatQED's project-defined protocol semantics:

- NIST FIPS 180-4, Update 1 (August 2015), Sections 5.1.1, 5.2.1, 5.3.3,
  and 6.2 define SHA-256 preprocessing, state, computation, and its 256-bit
  output. NIST's 2023 decision to revise the standard had not produced a
  replacement at the 2026-08-09 retrieval date.
- NIST's Hash Functions security table records 128-bit collision strength,
  256-bit preimage strength, and message-length-dependent second-preimage
  strength for SHA-256. These are conditional computational-strength claims,
  not a proof that equal digests imply equal messages.
- RFC 9380 is an Informational IRTF-stream publication reflecting CFRG
  consensus, not an Internet Standards Track specification. Sections 2.2.5,
  3.1, and 10.7 provide design guidance for domain separation; Section 10.7's
  exact title is “Domain Separation for expand_message Variants.” Verified
  Editorial erratum EID 7844 changes a Section 10.6 cross-reference and does
  not affect the cited guidance.
- The IANA Named Information registry's row 1 names full `sha-256` with 256
  bits; its rows 2 through 6 are separately named truncated variants. COSE
  values `-16` for SHA-256 and `-15` for SHA-256/64 remain COSE-local and are
  not imported into this frame.
- NIST SP 800-185 cSHAKE customization and TupleHash are relevant nearby
  constructions, but they use SHA-3-derived functions and do not standardize
  this SHA-256 preimage frame.

FIPS 180-4 therefore supplies the hash function, not the meaning or
injectivity of the StatQED frame. The latter remains a reviewed, original
project construction.

## Exact frame and injectivity

The hashed preimage is exactly:

```text
ASCII("StatQED-Digest") || 00
|| LP32(purpose_id)
|| LP32(algorithm_id)
|| LP32(profile_id)
|| LP32(object_class_schema_id)
|| LP32(framing_id)
|| LP32(payload)
```

`LP32(x)` is `u32be(len(x)) || x`. The magic is the exact 15-byte sequence
`53 74 61 74 51 45 44 2d 44 69 67 65 73 74 00`. Exactly six ordered
components follow, with no count, terminator, padding, seventh component, or
accepted tail.

For every admitted tuple, each four-byte prefix uniquely fixes the boundary
of its following component. Inducting over the fixed six positions shows that
equal framed bytes imply equal purpose, algorithm, profile, schema, framing,
and payload components. Complete consumption excludes a shared prefix with a
different tail. This is an injectivity argument about pre-hash bytes and does
not rely on collision resistance. An exhaustive finite corruption check over
all `4^6 = 4,096` tuples drawn from `{empty, "a", "b", "ab"}` found 4,096
distinct LP encodings.

The algorithm, profile, and framing identifiers are fixed respectively to
`sha-256`, `statqed.cbor-core.v1`, and `statqed.digest-lp.v1`. Purpose and
object-class/schema identifiers are caller- and registry-owned. All five
identifiers are inside the hashed preimage and must be 1 through 128 exact
ASCII bytes matching `[a-z0-9][a-z0-9._:-]{0,127}`. There is no case folding,
trimming, Unicode normalization, aliasing, or fallback. The candidate assigns
only `test.` vector names and creates no production purpose or schema domain.

The payload is the nonempty exact encoding of one already accepted
`statqed.cbor-core.v1` value. Framing binds the object-class/schema identifier
but does not resolve that identifier or validate payload conformance to the
named schema.

## Downgrade, replay, tails, and error precedence

Verification receives externally expected purpose, algorithm, profile,
object-class/schema, and framing identifiers. Substitution of any identifier,
including asking for the same unsupported algorithm/profile/framing value
found in a supplied frame, fails its field-specific code before digest
comparison. Replaying a frame under a different expected purpose or schema
therefore fails even when its recorded digest remains byte-for-byte valid.
Changing a domain component and hashing a new frame creates a different
unkeyed content address; it does not grant authorization.

The exact failure order is coherent and executable:

- a frame above 1,049,255 bytes, a declared payload above 1,048,576 bytes, or
  a supplied digest not exactly 32 bytes is `digest.length`;
- a missing/truncated four-byte prefix or a body shorter than its declared
  length is `digest.component_length`;
- after all declared bytes of an identifier are present, empty, over-128,
  non-ASCII, grammar-invalid, fixed-value, or caller-expected mismatches use
  that field's code: `digest.purpose`, `digest.algorithm`, `digest.profile`,
  `digest.object_class_schema`, or `digest.framing`;
- bytes after the complete sixth component are `digest.trailing_bytes`;
- an empty, malformed, non-profile, split, or concatenated payload is
  `digest.payload` unless the bytes instead form an explicit trailing field;
  and
- only an otherwise valid frame with an unequal exact 32-byte digest reaches
  `digest.mismatch`.

This distinguishes a complete invalid component from an incomplete frame.
The initially reviewed Python parser incorrectly returned
`digest.component_length` for a fully present 129-byte purpose while Rust
returned `digest.purpose`. The minimized witness was retained permanently as
`DIGEST-RAW-PURPOSE-BYTES-129`; the analogous schema witness is
`DIGEST-RAW-SCHEMA-BYTES-129`. Commit
`cda86d8f1f373b6648134b71c88683fd699485e2` fixed the normative precedence,
and `89af5a7dbb837ea7d1557d1a715b34a814afdf95` fixed Python and added its unit
regression. In the final 273-case replay, both implementations return
`digest.purpose` and `digest.object_class_schema` for those complete overlong
identifiers, while truncated prefixes and bodies remain
`digest.component_length`.

The conservative allocation cap is exactly
`15 + 6*4 + 5*128 + 1,048,576 = 1,049,255` bytes. Because the three fixed
identifiers have lengths 7, 20, and 20, the largest attainable valid frame is
1,048,918 bytes. The corpus covers that exact accepted maximum, a one-over
payload declaration, the allocation cap plus one, and a trailing byte after
an otherwise complete maximum frame. Empty identifiers and payloads, wrong
magic, deleted/reordered/duplicated/appended components, inconsistent lengths,
payload splitting/concatenation, digest truncation/extension, fallback, and
replay are all rejected under stable codes.

No randomness is consumed by construction or verification. Repeated inputs
produce repeated frames and digests; this review makes no probabilistic
assurance or randomness-quality claim.

## Implementation and schema boundary

Both implementations validate the fixed six-component frame, expected domain
identifiers, full payload profile, and exact 32-byte SHA-256 result. Python
uses `hashlib.sha256` and `hmac.compare_digest` for the final full-length
comparison. Rust uses `sha2::Sha256` and ordinary full-slice equality; it does
not claim constant-time equality. That distinction is acceptable for this
public, unkeyed content digest because neither the digest nor frame is secret.
It would not be acceptable evidence for a future MAC, authentication token,
secret verifier, or other protocol with a timing-secrecy requirement; such a
use needs a different primitive and a new threat review.

The schema-binding limit is non-vacuously tested in both native suites and in
the binary golden `DIGEST-SCHEMA-BINDING-NOT-CONFORMANCE.frame`. Canonical
Integer(0) is accepted under the deliberately suggestive identifier
`test.must-be-text.v1`. This proves the implemented claim is only exact schema
identifier binding. A schema-owning caller must separately resolve and
validate that identifier before calling an object schema conformant.

## Executed evidence

All final commands ran in an isolated archive of the exact reviewed commit:

- Python unit discovery: 57 tests passed, including the complete-overlong
  precedence and schema-binding/non-resolution regressions.
- `cargo test --locked --offline`: 31 Rust tests passed (9 CLI and 22 profile
  tests; no unit or doc tests were defined).
- `python3 scripts/serialization/run_conformance.py --verify`: 273 cases, zero
  failures, 69 joint goldens, and all 20 deliberate mutants detected. The
  digest subset contains 36 cases: 3 accepted and 33 rejected. The three
  digest mutants detect unframed-payload hashing, digest-prefix comparison,
  and unknown-algorithm fallback as `differential.digest_domain`.
- The three digest frame goldens are exactly 121, 119, and 1,048,918 bytes and
  match the hashes recorded above.
- `python3 scripts/serialization/source_audit_manifest.py`: 9 files verified,
  tree `75f8fe98338e4800230a7b9a9da7988f728bdf2516b170e969134482511686f2`.
- `make check`: repository checks and the 75 SQ-0002 toolchain probes passed.
- Independent adversarial harness: all 4,096 small LP tuples were distinct;
  all 28,815 one-byte changes to a 113-byte baseline frame were rejected with
  the original digest; all 8,160 one-byte changes to its 32-byte digest were
  rejected; identifier 0/1/128/129 boundaries, invalid grammar, complete
  overlong versus truncation precedence, and schema-binding nonconformance
  passed.

The earlier schema-conformance overclaim was minimized to the Integer(0)
witness and corrected before this final review. Explicit 129-byte builder
boundaries, the exact RFC 9380 Section 10.7 title, stale lineage hashes, raw
129-byte verifier precedence, and the regenerated 273-case evidence are all
now permanent corpus, test, source-audit, or evidence records. No unresolved
cryptographic-framing counterexample remains.

## RFC-0006 boundary

I did not inspect or edit RFC-0006. Path-only comparison shows that
`rfcs/0006-canonical-logical-data-digest.md` has SHA-256
`e834f805cc38fca2185433c72df4ac7db856c0ae20037fedcb57329a740b3429`
and Git blob `721eb5169877571620ea44c18970f528dbe683ec` both at SQ-0005's starting
commit `8875d8f6fa8e3b45e706ea567d45448927a02efa` and at the reviewed commit;
the path diff is empty. The reviewed frame remains generic and data-free. It
defines no logical table, lowering, row/column identity, privacy property,
data digest, or logical-data equality.

## Nonclaims and disposition

Approval is conditional on correct SHA-256 implementation, its collision and
second-preimage assumptions, exact framing bytes, governed identifier
meanings, trusted caller expectations, and separate schema validation. Digest
equality does not prove collision absence, provenance, authenticity,
authorization, source fidelity, schema conformance, semantic equality outside
the locked profile and caller-owned schema, logical-data identity, privacy,
theorem correctness, statistical identification or inference, numerical
correctness, interpretation, or kernel verification.

Within those explicit limits, the exact final frame is injective before
hashing, binds all six components, rejects downgrade/fallback/replay/tails and
truncation, has fixed resource and error precedence, uses the full SHA-256
output, and agrees across the two independent prototypes and frozen evidence.
The final cryptographic-framing disposition is **APPROVE**.
