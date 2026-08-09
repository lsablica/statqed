# SQ-0005 encoding source audits

Status: Draft source-curator evidence retrieved 2026-08-09. These records do not approve a profile or replace the required independent reviews.

## Recommended source disposition

| Subject | Recommended disposition | Unresolved authority |
|---|---|---|
| Deterministic CBOR ordering | Use RFC 8949 Section 4.2.1 core ordering as the candidate basis. Do not choose Section 4.2.3 length-first merely because `cbor2` and `ciborium` expose it as canonical. | Architecture/profile review |
| Decoder policy | Validate one complete raw item; reject trailing bytes, invalid UTF-8, duplicates, indefinite lengths, non-preferred arguments, unknown tags, and non-profile bytes before lossy conversion. | Checker-soundness and security review; exact resource limits remain open |
| Tags 2 and 3 | Candidate for arbitrary integers, with shortest bignum payload and an exact boundary against major types 0/1. | Numeric semantic model |
| Tag 4 | Candidate for exact decimal fractions only if exponent/mantissa and semantic-value normal forms are explicitly fixed. | Numeric semantic model |
| Tag 30 | Conditional candidate for rationals. The registered specification permits non-lowest terms; StatQED would need a project specialization such as nonzero positive denominator, gcd one, and unique zero/denominator-one rules. | RFC/semantic review; do not claim the tag supplies normalization |
| Interval | No interval tag exists in the IANA registry snapshot last updated 2026-07-20. Use an application-level structure or separately reviewed registration plan. | RFC/semantic review |
| Tags 5, 24, 80-87, 264-270, 55799 | Exclude from the minimum profile: bigfloat, embedded-CBOR recursion, typed arrays, arbitrary/extended numbers, and semantics-free self-description add unused or nonunique surface. | A later versioned extension can reconsider exact tags |
| Other/unknown tags | Reject in v1 unless a schema and profile explicitly admit an exact tag and content invariant. | Extension policy |
| CDDL grammar | Use RFC 8610 as updated by RFC 9682. Apply Verified EID 6526 through the published update; do not independently elevate Held errata. | Cross-tool conformance testing |
| CDDL controls | Exclude RFC 9165 and RFC 9741 controls from the minimum schema unless an exact necessary use is justified and tested. | Schema review |
| CDDL modules/imports | Normative exclusion. `draft-ietf-cbor-cddl-modules-06` is active Work in Progress (2026-03-01, expires 2026-09-02); pin `-06` only in an Experimental prototype. | Publication/currentness and RFC decision |
| Unicode | Strict RFC 3629 UTF-8, no replacement decoding, and preserve scalar sequences without normalization. Do not silently apply NFC or NFKC. | Any future identifier normalization must pin Unicode 17.0.0 or a later audited version and define collisions/errors |
| Digest | Full 32-octet SHA-256 from FIPS 180-4, textual identifier `sha-256`, and a project-defined injective/versioned frame covering purpose, algorithm, profile, schema, framing version, and payload. | Exact frame is original StatQED protocol work requiring cryptographic review |
| Prototype tools | Pin exact versions and flags; treat all output as untrusted differential evidence. `cbor2` 6.1.4 is implemented in Rust, so it is not independent Python implementation lineage. | Transitive license/advisory closure and independent-oracle proof |

## Currentness and conflict record

- RFC 8949 has one Verified Technical erratum: EID 8589, verified 2025-11-07, adding the NaN sign-bit condition to Section 5.6.1 map-key equivalence.
- RFC 8610 has EID 6526 Verified/Editorial and EIDs 6278, 6527, 6543, and 6575 Held for Document Update. RFC 9682 is the published grammar update and addresses these grammar topics.
- RFCs 9165, 9682, and 9741 had no matching errata in the official records on 2026-08-09.
- The CDDL module draft text says intended status Standards Track, while the Datatracker metadata reports no intended RFC status. Both agree that revision `-06` is only an active Internet-Draft.
- The current CBOR serialization draft is `draft-ietf-cbor-serialization-06` (2026-04-23, expires 2026-10-25). It is nearby Work in Progress and cannot silently amend the RFC 8949 profile.
- IANA registration proves allocation, not standards maturity or canonical semantic form. Tags 30, 264, 265, and 268-270 rely on individual specifications rather than RFCs.
- NIST announced in 2023 that FIPS 180-4 will be revised, but no replacement was published by the retrieval date.
- Direct exact-version OSV queries returned no records for `cbor2` 6.1.4, `ciborium` 0.2.2, `minicbor` 2.3.0, and `cddl` 0.10.6. This is neither a security guarantee nor a transitive graph audit.

## Files

- `SA-SQ0005-CBOR.yaml`: RFC 8949, EID 8589, IANA tags, numeric-tag conflicts, and deterministic variants.
- `SA-SQ0005-CDDL.yaml`: RFCs 8610/9165/9682/9741, all RFC 8610 errata statuses, and module-draft currentness.
- `SA-SQ0005-UNICODE.yaml`: RFC 3629, Unicode 17.0.0, and UAX 15 Revision 57.
- `SA-SQ0005-CRYPTO.yaml`: FIPS 180-4, algorithm registries, RFC 9380 guidance, and original frame obligations.
- `SA-SQ0005-PROTOTYPES.yaml`: exact package versions, semantics, top-level licenses, lineage, and dated advisory evidence.

All audit review records remain `DRAFT` with empty reviewer lists and hashes. Unjustified strengthenings block any signature or profile freeze.
