# SQ-0005 source-currentness and attribution review

Status: **Experimental review record**

Disposition: **APPROVE**

Review and retrieval date: 2026-08-09

Reviewer: `/root/sq0003_build_engineer`, acting as the independent
CBOR/CDDL/Unicode/cryptographic source-currentness reviewer

## Decision

The corrected nine-file source audit below passes its manifest, currentness,
status/errata, license-boundary, and attribution checks. The initially
reviewed audit had two blocking errors: it called
`draft-ietf-cbor-serialization-06` current after revision `-08` had appeared,
and it misclassified RFC 9380 as Standards Track. Before this approval, the
source author independently corrected the draft to `-08`/WG Last Call,
corrected RFC 9380 to Informational IRTF/CFRG status, recorded Verified
Editorial EID 7844, retained the exact OSV request/response observation, and
regenerated the source manifest.

The final RFC-0001 subject correctly says that only RFC 9682 formally updates
RFC 8610 and classifies RFCs 9165 and 9741 as optional published extensions
that the minimum profile does not require. No unsupported attribution or
missing primary source remains for the selected normative dependencies. The
limitations below remain nonblocking and must not be widened into stronger
claims.

The changes after the preceding source review clarify project-defined digest
failure precedence, expand the retained corpus, and refresh evidence hashes;
they do not change an external-source statement, normative-scope block, or
source-audit member.

This reviewer is distinct from the source-audit author and did not edit the
candidate, RFC, ADR, or `source-audits/encoding/` content. This approval does
not accept RFC-0001, accept ADR-0004, approve the project-original digest
frame cryptographically, or promote any implementation or external tool into
the trusted computing base.

## Exact subject

The final committed subject was checked at HEAD
`410465d773fc011ee01e38e6e76a79a60efe8837`. File and framed-tree hashes
define the reviewed bytes precisely.

| Subject | SHA-256 or identity |
|---|---|
| `docs/research/serialization/profile-candidate.md` | `6cbf0f686a1f35b5c6fac8411ef5abc708c9c4410b5fdb2ee510c513df067d2f` |
| `rfcs/0001-deterministic-encoding.md` | `d4258501486affdaf99ec95322bae1e1212806c896e33360a17c137fd2f51106` |
| `docs/adr/0004-deterministic-cbor-cddl.md` | `004b41b65dc8450de6f0bd8431f7de2e1f885e95dfd985f50981e1c1c5c9e49d` |
| RFC/ADR marked normative-scope block | `737847efcdb917f8c3db8c05c314c85f62775fa8ca80638a56de69cadb0fc060` |
| `rfcs/0006-canonical-logical-data-digest.md` | `e834f805cc38fca2185433c72df4ac7db856c0ae20037fedcb57329a740b3429` |
| `source-audits/encoding/manifest.json` | `b3f70746a36c350590f2f77ffebb0e550773337d79db4103317426be94ac0a40` |
| Source-audit framed tree | `75f8fe98338e4800230a7b9a9da7988f728bdf2516b170e969134482511686f2` |
| `scripts/serialization/source_audit_manifest.py` | `5b0d14e39000c707a95205d1ded2389fa96c435b97f5c631225d77877f2c5d03` |
| `work/contracts/SQ-0005.yaml` | `d3e4361470e1238346118fb5083261544d0f68d294e6d1e72de2e7ef7436f6e9` |
| `agents/protocols/source-lineage.md` | `0774c9959e2dd630dff16f4a78b1c39edf176805821acd52fa75d3ae229eaf5e` |

RFC-0001 was Draft and ADR-0004 was Proposed at review. Their text between and
including the `SQ-0005-NORMATIVE-SCOPE-BEGIN` and
`SQ-0005-NORMATIVE-SCOPE-END` markers compared byte-for-byte equal and produced
the marked-scope hash above. RFC-0006 was byte-identical to its
`8875d8f6fa8e3b45e706ea567d45448927a02efa` pre-SQ-0005 baseline and remained
Draft. This review does not license a status transition.

### Source-audit manifest members

| Manifest member | SHA-256 |
|---|---|
| `README.md` | `80630d625bee1c21c901f81932c6077479846697a35b3b8ec9d4da9ddf2ba4cc` |
| `SA-SQ0005-CBOR.yaml` | `f61098ab0a0a4bd8ff6b1c866772023a5ad2f283d0f7e78801cffaafc7196185` |
| `SA-SQ0005-CDDL.yaml` | `714bb59f260517468487f7ead7fbf8cc2a5d5e32c14f4818fc738d0af0ac6da4` |
| `SA-SQ0005-CRYPTO.yaml` | `d3feb17277b3fccafa2201f36290d2c89be5a98ab953fd75dfd749bb6da3ae36` |
| `SA-SQ0005-PROTOTYPES.yaml` | `90ed358716e9d9f27de60d75d2eda4c5f1d8ae1c5fec38187dc3c2b962e9d506` |
| `SA-SQ0005-UNICODE.yaml` | `9c722257cc62032e6ee2087f44ec9e55834e1ae00d1532e4e0982d57be4553b2` |
| `osv-direct-prototype-observation.json` | `419eac674c87f86b3adff12e57fe55d58b12f88fe8829dffc18576ad298a339a` |
| `osv-direct-prototype-request.json` | `6efff00478c1722fa295792fd09465156e474ae16ac083ae14f8997c59c2bd56` |
| `osv-direct-prototype-response.json` | `3212e2cbaa17d6a3b3cdbafe016d0425f1740c3b78a53925a1d841193090a600` |

The repository verifier reported nine files and the tree hash above. A second,
independently written calculation reproduced the tree using sorted repository
paths and
`sha256(u64be(path_len) || path || u64be(content_len) || content)`.

## CBOR, CDDL, and errata findings

| Source | Official status/currentness at retrieval | Review disposition |
|---|---|---|
| [RFC 8949 / STD 94](https://www.rfc-editor.org/info/rfc8949/) | Internet Standard, December 2020; obsoletes RFC 7049 | Correct source for well-formedness, validity, preferred serialization, core ordering in Section 4.2.1, and the distinct length-first variant in Section 4.2.3. |
| [RFC 8949 errata](https://www.rfc-editor.org/errata/rfc8949) | One erratum: EID 8589, Verified/Technical | Audit correctly applies the NaN sign-bit correction when NaN map keys are in scope. V1 forbids floats, so it does not change accepted v1 values. |
| [RFC 8610](https://www.rfc-editor.org/info/rfc8610/) | Proposed Standard, June 2019; updated by RFC 9682 | Correct structural-schema source; it does not determine CBOR bytes, map serialization order, normalization, or StatQED semantic validity. |
| [RFC 8610 errata](https://www.rfc-editor.org/errata/rfc8610) | EID 6526 Verified/Editorial; EIDs 6278, 6527, 6543, and 6575 Held for Document Update | Audit correctly does not elevate Held errata and uses RFC 9682's published grammar update. |
| [RFC 9165](https://www.rfc-editor.org/info/rfc9165/) | Proposed Standard, December 2021; no matching errata | Optional additional controls are correctly excluded from the minimum schema, not described as invalid. |
| [RFC 9682](https://www.rfc-editor.org/info/rfc9682/) | Proposed Standard, November 2024; explicitly updates RFC 8610; no matching errata | Appendix A is correctly treated as the current published collected grammar. Mixed-tool parsing remains a documented risk. |
| [RFC 9741](https://www.rfc-editor.org/info/rfc9741/) | Proposed Standard, March 2025; no matching errata | Optional text conversion/processing controls are correctly excluded from the minimum schema. |

The [IANA CBOR Tags registry](https://www.iana.org/assignments/cbor-tags/cbor-tags.xhtml)
was last updated 2026-07-20. The audited rows and linked individual
specifications for tags 30, 264-265, and 268-270 agree with the registry. No
registered entry described a mathematical interval at that snapshot. The
candidate's empty tag allowlist is a project specialization: IANA allocation
does not imply standards maturity, a unique semantic normal form, or profile
acceptance. Because v1 rejects every tag, no unreviewed tag semantics enter the
accepted language.

Two separate draft boundaries were checked:

- [CBOR Serialization and Determinism](https://datatracker.ietf.org/doc/draft-ietf-cbor-serialization/)
  is currently `draft-ietf-cbor-serialization-08`, dated 2026-07-29,
  expiring 2027-01-30, active in WG Last Call. The audit now records it only
  as nearby Work in Progress and does not let it amend RFC 8949.
- [CDDL Module Structure](https://datatracker.ietf.org/doc/draft-ietf-cbor-cddl-modules/)
  remains `draft-ietf-cbor-cddl-modules-06`, last updated 2026-03-01 and
  expiring 2026-09-02. The draft text says intended Standards Track while
  Datatracker metadata says no intended RFC status. Both still identify an
  active Internet-Draft, not an RFC. Normative module/import exclusion is
  therefore correctly sourced.

## UTF-8 and Unicode boundary

[RFC 3629 / STD 63](https://www.rfc-editor.org/info/rfc3629/) and RFC 8949
support the candidate's strict boundary: accepted CBOR text uses shortest-form
valid UTF-8 over Unicode scalar values through U+10FFFF, excludes surrogates,
overlong encodings, and malformed sequences, and performs no replacement
decoding. Neither RFC requires Unicode normalization.

[Unicode 17.0.0](https://www.unicode.org/versions/Unicode17.0.0/) is the
current published Unicode version, and
[UAX 15 Revision 57](https://www.unicode.org/reports/tr15/tr15-57.html) is the
corresponding normalization annex. The audit correctly distinguishes NFC/NFD
from compatibility forms NFKC/NFKD and records the risk that compatibility
normalization can erase meaningful mathematical distinctions. Preserving the
exact scalar sequence, including structurally valid controls, noncharacters,
and unassigned scalar values, is an explicit StatQED choice rather than a
claim imposed by RFC 3629, RFC 8949, or Unicode.

The Unicode 17 post-release corrections page was available at retrieval, but
none of its listed corrections alters the v1 no-normalization boundary. A
future normalization profile would still need a fresh exact Unicode/UAX pin,
normalization data, collision policy, unassigned-code-point policy, and
cross-implementation evidence.

## SHA-256 and domain-separation attribution

[FIPS 180-4 Update 1](https://csrc.nist.gov/pubs/fips/180-4/upd1/final) is
the current published Secure Hash Standard at retrieval. Its August 2015
publication defines SHA-256 and its 256-bit output; NIST's 2023 planning note
says the standard will be revised, but no replacement was published. The
[NIST Hash Functions page](https://csrc.nist.gov/projects/hash-functions)
supports the audit's conditional 128-bit collision, 256-bit preimage, and
message-length-dependent second-preimage strength statements.

[RFC 9380](https://www.rfc-editor.org/info/rfc9380/) is Informational on the
IRTF stream and records CFRG consensus; it is not an Internet Standards Track
specification. Sections 2.2.5, 3.1, and 10.7 support only the stated design
guidance about distinct, injectively encoded domains and prefix/suffix-free
inputs. Section 10.7 is specifically about separating uses from
`expand_message` variants. The audit and candidate now correctly state that
StatQED does not adopt RFC 9380's hash-to-curve construction and that the exact
six-component length-framed preimage is project-original. The sole RFC 9380
erratum, [EID 7844](https://www.rfc-editor.org/errata/eid7844), is
Verified/Editorial and corrects a Section 10.6 cross-reference; it does not
alter the cited domain-separation passages.

The [IANA Named Information Hash Algorithm registry](https://www.iana.org/assignments/named-information/named-information.xhtml)
correctly supports textual `sha-256` and the full 256-bit output while keeping
truncated variants distinct. The
[IANA COSE Algorithms registry](https://www.iana.org/assignments/cose/cose.xhtml#algorithms)
correctly records COSE-local value `-16` for SHA-256; the candidate does not
misuse that registry-local integer as a universal identifier.

[NIST SP 800-185](https://csrc.nist.gov/pubs/sp/800/185/final) remains the
published December 2016 recommendation for cSHAKE and TupleHash and is
correctly treated as an unselected nearby construction. Its page also carries
a 2025 planning note that NIST decided to revise it. The audit's “current
recommendation” statement is true, but future refreshes should continue to
check that planning note and any eventual replacement.

## Implementation source, license, and currentness findings

Official publisher records and exact-version documentation support the
software statements:

| Software source | Verified currentness and boundary |
|---|---|
| [cbor2 6.1.4](https://pypi.org/pypi/cbor2/6.1.4/json) | Current PyPI release at retrieval; first upload `2026-08-01T20:40:24Z`; Python `>=3.10`; all files not yanked; MIT expression. Its current implementation is Rust, its canonical sort is length-first, permissive decoder options require explicit restriction, and its documentation disclaims malicious-input testing. The 6.1.4 changelog supports the three cited decoder/hash regressions. |
| [ciborium 0.2.2](https://crates.io/api/v1/crates/ciborium/0.2.2) | Current non-yanked crates.io release; Apache-2.0; Rust 1.58; `CanonicalValue` implements the excluded length-first ordering. |
| [minicbor 2.3.0](https://crates.io/api/v1/crates/minicbor/2.3.0) | Current non-yanked release, published 2026-07-23; BlueOak-1.0.0; no publisher-declared Rust version. Its low-level APIs leave profile ordering and validation to project code. |
| [cddl 0.10.6](https://crates.io/api/v1/crates/cddl/0.10.6) | Current non-yanked release, published 2026-06-29; MIT; Rust 1.88.0. Default features include controls/extensions beyond the selected minimum, so tool support cannot define normative syntax. |
| [serde_cbor repository](https://github.com/pyfisch/cbor) | Archived by its owner in August 2021 and explicitly unmaintained; exclusion is correctly recorded. |

For the selected Rust prototype, `Cargo.lock` SHA-256
`2e9c4f95aa0aa54ab2338e980d388f9f0223be8964d94f82d82f086f2dadb180`
contains 22 registry packages. The complete license inventory SHA-256 is
`3d44e9d26c756c2aa950779f9fcf557f11efc28a50d20f27c2ec1a501aaadfa9`.
The retained crates.io observation says all exact versions were not yanked.
The hash-locked RustSec/cargo-audit observation uses database commit
`309ad29d8fe448bf986019e05d47b9e0e29a2218` and reports zero vulnerabilities
and zero warnings. These are dated registry/database observations, not legal
advice, maintenance assurances, or security guarantees.

The Python oracle records conda-forge CPython 3.12.13, an empty third-party
requirements file, and a standard-library-only implementation.
[Python 3.12.13](https://www.python.org/downloads/release/python-31213/) is an
official March 2026 security-only release of the legacy 3.12 line. The
[versioned Python license page](https://docs.python.org/3.12/license.html)
confirms the PSF License Version 2 plus historical and incorporated-component
terms. The local record correctly says its retained PSF-license excerpt is
not the complete runtime-distribution license and that redistribution would
require a fresh complete license audit.

The retained OSV observation binds the four exact direct-package queries, a
normalized response containing four empty objects, and the raw API-response
hash. An independent POST of the same request to the
[official OSV querybatch endpoint](https://api.osv.dev/v1/querybatch) on the
review date again returned four aligned empty, unpaginated results. This is a
current no-record observation only and does not cover undisclosed issues or
unqueried dependencies.

## Findings and limits

- **No blocking source defect remains.** The stale serialization-draft record,
  RFC 9380 status error, omitted RFC 9380 erratum, and unretained OSV response
  were corrected before the final hash check.
- The selected core ordering, empty tag/extension allowlists, exact Unicode
  preservation, strict rejection, bounded value model, identifiers, failure
  taxonomy, and six-component frame are StatQED specializations. The sources
  motivate or constrain them but do not mandate them.
- Registry “no entry,” “current release,” “not yanked,” and “no matching
  errata/advisory” claims are snapshot-relative to 2026-08-09 and require a
  fresh check after source or release drift.
- The source manifest is not a complete legal bill of materials. Exact Rust
  transitive licenses and Python runtime/component terms live in the separately
  hash-bound implementation evidence. No redistribution approval is given.
- This review checks source fidelity and currentness, not the mathematical
  injectivity proof, cryptographic security of the original frame, parser
  soundness, semantic-model quality, differential conformance, CI behavior,
  provenance, or statistical validity. Those remain owned by their distinct
  reviews.

Within those limits, the exact subject is **APPROVED** for the SQ-0005
source-currentness gate.
