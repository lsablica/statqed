# RFC-0001: Deterministic Normative Encoding

- Status: Draft
- Author: foundation serialization team
- Reviewers: interoperability reviewer, security reviewer, formal-methods reviewer
- Created: 2026-08-02
- Task: SQ-0005
- Supersedes: Draft placeholder installed at repository bootstrap

## Decision boundary

Select the exact structured encoding, deterministic profile, schema language/version, numeric/tag model, map-key order, duplicate behavior, Unicode policy, extension behavior, decoder acceptance behavior, hash algorithms/domain separation, resource limits, and independent-conformance requirements for normative StatQED objects.

The outer `.statqed` archive/container, entry ordering, compression, metadata, path rules, and envelope resource limits are separate SQ-0010 decisions. The canonical logical data model and digest are governed by RFC-0006.

## Motivation

Normative hashing and cross-language interchange require one accepted byte representation per accepted semantic object and specified rejection of ambiguous inputs. “CBOR,” “deterministic CBOR,” and “CDDL-valid” are not complete application profiles.

## Terminology and source background

- RFC 8949 / STD 94 sections 4.1-4.2.3 define CBOR deterministic-encoding options, including distinct core and length-first ordering variants.
- RFC 8610 defines CDDL and has accepted extensions in RFCs 9165, 9682, and 9741.
- CDDL constrains data shape; it does not by itself determine canonical bytes, semantic normalization, duplicate handling, Unicode normalization, or extension policy.
- CDDL module/import syntax remains an IETF Work in Progress as of 2026-08-03 and is not treated as an accepted standard by this RFC.

Exact primary locators and current-status limitations are recorded in `docs/research/SQ-0001-constitutional-source-audit.md`.

## Examples and nonexamples

Required examples and failure cases include:

- reversed map insertion order;
- exact duplicate keys and keys duplicated after the selected Unicode treatment;
- composed/decomposed Unicode and invalid UTF-8;
- preferred and non-preferred integer encodings at boundaries;
- rational `1/2` versus `2/4`, denominator zero, and decimal/rational type distinction;
- IEEE `+0`/`-0`, distinct NaN payloads, and invalid/reversed intervals;
- unknown critical/noncritical extensions and duplicate extension IDs;
- non-profile but decodable CBOR to settle reject versus normalize;
- unsupported profile/schema versions and bounded malformed inputs.
- purpose/algorithm/profile/schema/framing mutations and cross-domain replay among IR, manifest, registry, theorem-statement, proof/build, and data-digest domains;
- unsupported or policy-disallowed algorithm fallback, truncation, and downgrade attempts.

Nonexamples:

- Two encoders that share the same canonicalizer counted as independent evidence.
- Golden bytes accepted only because the Rust reference backend emitted them.
- CDDL validation reported as semantic, inferential, or kernel verification.
- A digest match reported as proof of collision-free object identity.

## Alternatives

### Deterministic CBOR with versioned CDDL

Provisional preferred direction. It supports typed binary values and standard deterministic options, but still requires a complete StatQED application profile.

### Canonical JSON

Retained as a prototype/diagnostic alternative. Binary/numeric distinctions, extension behavior, and exact-value conventions require additional rules.

### A custom binary format

Rejected for the foundation unless both standard-based options fail measured requirements; it would increase parser, tooling, and governance burden.

### Accept any decodable representation and normalize silently

Not decided. Strict rejection versus normalization is a security and interoperability choice that SQ-0005 must test per input class.

## Proposed semantics

The current candidate is deterministic CBOR under one explicitly selected RFC 8949 ordering/profile, with versioned CDDL files using accepted RFC syntax. JSON/YAML are diagnostic/authoring projections only.

No deterministic profile, tag assignment, Unicode normalization rule, numeric normal form, extension rule, digest, or decoder behavior is Accepted by this Draft.

## Formal and implementation consequences

- SQ-0005 compares at least two genuinely independent implementations or oracles.
- SQ-0006 freezes reviewed semantic fixtures before golden bytes and records profile/schema versions.
- Production frontends construct the accepted semantic IR; calling the shared Rust encoder tests integration but is not independent encoder conformance.
- The Rust backend implements the accepted profile but does not define it.
- Lean-side decoding/bridging and its byte-to-term adequacy remain governed by RFC-0003.

## Trust, security, privacy, and accessibility

Differential parsing, duplicate keys, Unicode confusion, type confusion, unbounded nesting/length, resource exhaustion, unknown critical features, cross-domain replay, algorithm/profile downgrade, truncation, and malicious normalization are in scope. Normative verification is offline. Diagnostic renderings must preserve type distinctions and visibly identify non-normative views.

## Compatibility and migration

The encoding profile is independently versioned. A semantic or canonical-byte change creates a new profile and migration record; golden vectors are content-addressed and never silently rewritten. A decoder's ability to read an old profile does not imply preservation of claim semantics.

## Validation plan

- complete positive, boundary, malformed, resource, Unicode, numeric, tag, and extension vector catalogue;
- independent byte/digest comparison with implementation-lineage record;
- divergent-implementation mutation proving the harness detects disagreement;
- domain-separation vectors mutating purpose, algorithm, profile, schema version, and framing across every normative digest domain, plus downgrade/fallback/truncation rejection;
- security review and bounded-input tests;
- migration impact and explicit failure codes;
- resolution of every example above before acceptance.

## Objections and resolution

- **Objection:** Choosing CBOR direction now prematurely freezes bytes. **Resolution:** SQ-0001 accepts only the research direction and gate; this RFC remains Draft until prototype evidence exists.
- **Objection:** CDDL modules simplify schemas. **Resolution:** accepted RFC syntax may be used; module draft syntax must be pinned and labeled Experimental or avoided until standardized.

## Decision

Deferred to SQ-0005. Deterministic CBOR plus versioned CDDL is the provisional candidate only. ADR-0004 and all present-tense normative encoding claims remain Proposed/Draft until this RFC passes its validation plan and is Accepted.
