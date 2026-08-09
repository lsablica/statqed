# SQ-0005 cryptographic-framing review

Status: Experimental review record

Disposition: **APPROVE**

Reviewer: `/root/sq0002_release_security_adversarial`, acting as the distinct
cryptographic-framing and counterexample reviewer

Review date and source-retrieval date: 2026-08-09

## Scope and exact subject

The requested baseline was commit
`ac5ce971eca4f46e7725f56599e5a30e7025bd22`. Corrections found during review
were integrated before approval. This disposition applies only to the exact
framing subject at commit
`044005f6bddf60bade7b352b02d71baeee50c413` and the following SHA-256 file
hashes:

| Subject | SHA-256 |
|---|---|
| `docs/research/serialization/profile-candidate.md` | `d07816f7f3fadeb07b91196691848f3933a13f96503c86ed24c2ed9d42ed45bb` |
| `source-audits/encoding/SA-SQ0005-CRYPTO.yaml` | `aedbd89fea0b3b34e2e11680b04e75623cdf69e2e02f5b176a89a28da7fab103` |
| `schemas/prototypes/python-oracle/statqed_oracle/oracle.py` | `26040015042df33facd2329801174795c6933ec808d5d896f001909bf60b2f3e` |
| `schemas/prototypes/python-oracle/statqed_oracle/cli.py` | `3c6c8449cf7bd64576db1ce418a0a6f9a13cf48ae26b39ff774b64577200bdbc` |
| `schemas/prototypes/python-oracle/tests/test_digest_and_cli.py` | `0bd70d43ede85beda2600231da6130c2ef8637594f5350bed981bbc18db8863a` |
| `schemas/prototypes/python-oracle/LINEAGE.md` | `ad59ef6713239db37ccc823924869cbe11ebd2bdeaf7146b10b457c1edb90cee` |
| `schemas/prototypes/python-oracle/README.md` | `2ff02e87af5c5c99a1b4389ac0fa9edb310f741a4ca9ab5a40039a4c04ab5ee7` |
| `conformance/prototypes/fixtures/semantic-v1/digest-framing.json` | `75b11a2b6069f759710cd132d92a8ef1d91a0dbc1488f85f14f3920819277a19` |

This review approves the generic, data-free SHA-256 framing candidate and its
Experimental evidence. It does not accept RFC-0001, RFC-0006, or any ADR, and
does not approve the remainder of SQ-0005 outside the exact subject above.

## Primary-source check

I independently refreshed the following official locators on 2026-08-09:

- [NIST FIPS 180-4, Update 1](https://csrc.nist.gov/pubs/fips/180-4/upd1/final),
  Sections 5.1.1, 5.2.1, 5.3.3, and 6.2, with persistent locator
  [DOI 10.6028/NIST.FIPS.180-4](https://doi.org/10.6028/NIST.FIPS.180-4).
  The page identifies the August 2015 publication and the 2023 decision to
  revise it; the current NIST hash-functions page still identifies FIPS 180-4
  as the approved SHA-2 standard at retrieval.
- [NIST Hash Functions](https://csrc.nist.gov/projects/hash-functions),
  especially the SHA-256 row in the security-strength table. Its 128-bit
  collision, 256-bit preimage, and message-length-dependent second-preimage
  entries are computational-strength claims, not proofs of equality.
- [RFC 9380](https://www.rfc-editor.org/rfc/rfc9380.html), Sections 2.2.5,
  3.1, and 10.7, with persistent locator
  [DOI 10.17487/RFC9380](https://doi.org/10.17487/RFC9380). Section 10.7 is
  correctly titled “Domain Separation for expand_message Variants.” These
  sections are design guidance only; they do not standardize the StatQED
  frame.
- [IANA Named Information Hash Algorithm Registry](https://www.iana.org/assignments/named-information/named-information.xhtml),
  last updated 2025-10-14 at retrieval. Row 1 is current `sha-256` with a
  256-bit value; rows 2 through 6 are distinct truncated variants.
- [IANA COSE Algorithms](https://www.iana.org/assignments/cose/cose.xhtml#algorithms),
  last updated 2026-07-17 at retrieval. COSE value `-16` is SHA-256 and `-15`
  is SHA-256/64, but those numbers remain scoped to the COSE registry and are
  not reused by this framing profile.
- [NIST SP 800-185](https://csrc.nist.gov/pubs/sp/800/185/final), December
  2016, with persistent locator
  [DOI 10.6028/NIST.SP.800-185](https://doi.org/10.6028/NIST.SP.800-185).
  cSHAKE and TupleHash are relevant nearby constructions, not standards for a
  SHA-256 StatQED frame. The page records a 2025 decision to revise the
  publication.

The audit correctly separates SHA-256's sourced definition and conditional
security strengths from StatQED's original framing semantics. It neither
misattributes the frame to FIPS 180-4 nor silently imports a registry-local
numeric algorithm identifier.

## Adversarial assessment

### Frame purpose and injectivity

The preimage is the fixed 15-byte `StatQED-Digest` magic including its terminal
zero byte, followed by exactly six ordered `u32be` length-prefixed components:
purpose, algorithm, profile, object-class/schema, framing version, and payload.
All interpretation-bearing identifiers are inside the hashed preimage.

For every admitted component, its length is below `2^32`. The first four bytes
of `LP(x)` uniquely determine the number of following bytes belonging to `x`;
therefore equal `LP` encodings imply equal components. Repeating that argument
over the fixed six-component sequence, and requiring complete consumption,
proves that two equal framed preimages have equal six-tuples. The hash function
is not needed for this framing-injectivity argument.

An independent exhaustive check encoded all `4^6 = 4,096` tuples over
`{"", "a", "b", "ab"}` and found no duplicate LP encoding. This finite test
is a corruption check complementing the general parsing argument, not a
substitute for it.

### Domain binding, downgrade, and replay

The fixed profile closes v1 to `sha-256`, `statqed.cbor-core.v1`, and
`statqed.digest-lp.v1`. Verifiers also receive externally expected purpose,
algorithm, profile, schema, and framing identifiers. A mismatch fails before
digest comparison. Tests confirm that aliases, older profile/framing names,
and even a caller that requests the same unsupported replacement cannot cause
fallback to the supported value.

Changing purpose, algorithm, profile, schema identifier, or framing identifier
changes the framed preimage. Reusing a valid frame and recorded digest with a
different caller-expected purpose fails as `digest.purpose`; the corresponding
schema and fixed-identifier substitutions fail in their own domains. A party
can of course construct and hash a new frame under another admitted test
identifier; that is new content addressing, not authorization. The digest is
unkeyed and makes no authenticity claim.

Cross-protocol separation relies on the StatQED-specific magic and the governed
identifier namespaces. The candidate correctly allocates no production
purpose or schema identifiers and restricts current vectors to `test.` names.
Future production allocations remain a registry-governance obligation.

### Grammar, boundaries, and failure precedence

Identifiers are byte-exact ASCII matching
`[a-z0-9][a-z0-9._:-]{0,127}` with lengths 1 through 128. Independent tests
covered lengths 0, 1, 128, and 129, plus uppercase, slash, leading/trailing
space, non-ASCII, and embedded-zero mutations. No trimming, case folding, or
Unicode normalization is performed. Permanent corpus cases
`DIGEST-PURPOSE-BYTES-129` and `DIGEST-SCHEMA-BYTES-129` lock the one-over
boundary.

The conservative allocation cap is correctly calculated as
`15 + 24 + 5*128 + 1,048,576 = 1,049,255` bytes. Because three identifiers
are fixed at 7, 20, and 20 bytes, the largest attainable valid frame is
`1,048,918` bytes. The implementation accepts that attainable maximum, rejects
a payload declaration of `1,048,577` bytes as `digest.length`, rejects a frame
of `1,049,256` bytes as `digest.length`, and treats one trailing byte after an
otherwise maximum valid frame as `digest.trailing_bytes`.

The implementation follows the published precedence: whole-frame cap and
wrong digest length first; then magic and six complete bounded LP fields;
then complete-consumption/trailing-byte rejection; then expected identifier
binding, fixed-profile checks, and payload-profile validation; and only then
full digest comparison. Truncated prefixes/components select
`digest.component_length`; an oversized encoded payload selects
`digest.length`; empty, malformed, non-profile, or concatenated CBOR payloads
select `digest.payload`; a split payload that leaves a seventh LP field selects
`digest.trailing_bytes`; 31- and 33-byte supplied digests select
`digest.length`; and only an unequal 32-byte digest selects `digest.mismatch`.

Deletion, reordering, duplication, appended components, altered lengths,
empty components, payload split/concatenation, digest truncation/extension,
and exact-length mismatch were all exercised. An independent single-byte
corruption sweep rejected all 28,815 one-byte changes to the 113-byte baseline
frame when retaining its original digest, and all 8,160 one-byte changes to
the corresponding 32-byte digest.

### Comparison and interpretation boundary

The Python verifier requires a 32-byte digest and uses
`hmac.compare_digest` for the final full-length byte comparison. Earlier
framing and identifier comparisons concern public format metadata and are
intentionally used to return stable diagnostics. Constant-time comparison
does not turn SHA-256 into a MAC or signature and does not provide provenance
or authorization.

The verifier establishes canonical-profile payload bytes and exact binding to
an object-class/schema identifier. It does not resolve that identifier or
validate schema conformance. The minimized regression
`test_schema_identifier_is_bound_but_not_resolved` and corpus case
`DIGEST-SCHEMA-BINDING-NOT-CONFORMANCE` accept canonical Integer(0) under the
deliberately suggestive `test.must-be-text.v1` identifier solely as framing
evidence; a schema-owning caller must separately validate or reject the
object.

## RFC-0006 nonownership

I did not inspect or edit RFC-0006. I verified by hash and path diff only that
`rfcs/0006-canonical-logical-data-digest.md` has SHA-256
`e834f805cc38fca2185433c72df4ac7db856c0ae20037fedcb57329a740b3429`
both at SQ-0005's starting commit
`8875d8f6fa8e3b45e706ea567d45448927a02efa` and in the reviewed worktree, and
that `git diff --quiet` reports no change. The reviewed candidate remains
generic and data-free; it defines no logical-table lowering, data identity,
privacy property, or canonical logical-data digest.

## Corrections resolved during review

1. The requested baseline could be read as saying that digest verification
   revalidated object-class/schema conformance. The minimized witness was a
   canonical Integer(0) payload framed under `test.must-be-text.v1`. Commit
   `07b9461fef39dd0d81f1bce57f47e5c581b42956` corrected the profile, README,
   lineage, and oracle documentation to say that framing only binds the schema
   ID. Commit `044005f6bddf60bade7b352b02d71baeee50c413` retained the witness in
   the Python suite and semantic corpus.
2. The Python lineage record contained a stale profile hash. Commit
   `07b9461fef39dd0d81f1bce57f47e5c581b42956` synchronized it to the exact
   reviewed profile hash.
3. The initial executable evidence lacked explicit 129-byte purpose and schema
   one-over cases. Commit
   `d21e411fa5331c57b0e89d2b6bd57384317c1572` added both minimized permanent
   corpus fixtures.
4. The cryptographic source audit paraphrased RFC 9380 Section 10.7 with a
   non-exact title. Commit
   `ebdec127cba52322dfa8f0d18f1b5fa7c1ea7dcf` replaced it with the official
   section title without changing the framing argument.

No blocking correction remains on the exact subject hashes above.

## Executed evidence

- `PYTHONPATH=schemas/prototypes/python-oracle /usr/bin/python3 -m unittest discover -s schemas/prototypes/python-oracle/tests -v`
  — 49 tests passed.
- `python3 -m json.tool conformance/prototypes/fixtures/semantic-v1/digest-framing.json`
  — passed.
- Independent read-only adversarial harness — 23 named structural/domain
  mutations passed; 4,096 small LP tuples were collision-free; all 28,815
  one-byte frame corruptions and 8,160 one-byte digest corruptions were
  rejected; identifier grammar and 0/1/128/129 boundaries passed.
- Semantic corpus count — 253 cases, 70 accepted after the permanent framing
  regressions were added.
- `git diff --check` — passed before this review file was created.
- RFC-0006 starting/current SHA-256 comparison and path-only
  `git diff --quiet` — identical, exit 0.

## Cryptographic nonclaims and decision

Approval is conditional on the stated SHA-256 collision and second-preimage
assumptions, correct implementation of SHA-256, exact framing bytes, governed
identifier meanings, a trusted expected digest where the application requires
integrity, and separate schema validation. A digest match is not proof of
collision-free identity, provenance, authenticity, schema conformance,
semantic equality outside the locked profile, statistical identification,
inference, numerical correctness, or kernel verification.

Subject to those explicit limits, the exact generic data-free framing is
unambiguous, downgrade-closed for v1, replay-bound to caller expectations,
fully length checked, and implemented with full-output SHA-256 comparison.
The cryptographic-framing disposition is **APPROVE**.
