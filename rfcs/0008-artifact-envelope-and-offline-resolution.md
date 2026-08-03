# RFC-0008: Artifact Envelope and Offline Resolution

- Status: Draft
- Author: foundation artifact team
- Reviewers: interoperability reviewer, security reviewer, formal-methods reviewer, privacy reviewer
- Created: 2026-08-03
- Task: SQ-0010
- Supersedes: none

## Decision boundary

Select the deterministic outer `.statqed` container, manifest authority, entry-name/path model, ordering and metadata rules, compression policy, resource limits, external-reference policy, normative/report separation, and provenance disclosure/redaction behavior.

Structured-object bytes remain governed by RFC-0001. Logical data/digests remain governed by RFC-0006.

## Motivation

A self-consistent structured payload can still be ambiguously or unsafely packaged. Archive traversal, duplicate normalized paths, link/device entries, decompression bombs, alternate manifests, trailing archives, active reports, network resolution, and secret-bearing provenance can compromise integrity, availability, privacy, or archival verification.

## Terminology and source background

- **Normative entry:** content referenced by the manifest and eligible to affect a verification result.
- **Report entry:** inert, non-normative content that cannot affect verification.
- **External reference:** content not carried in the envelope; it resolves only from explicitly supplied local material or remains unresolved.
- **Resource budget:** deterministic per-entry and aggregate limits on bytes, expansion, count, depth, allocation, and work.

Primary archive/container and provenance/privacy sources must be audited before acceptance.

## Examples and nonexamples

Required hostile cases:

- absolute, drive, and UNC paths; separator variants; `.`, `..`, NULs, Unicode aliases, and duplicate normalized names;
- symlinks, hardlinks, devices, alternate data streams, encryption, multipart/nested archives, and unsupported compression;
- duplicate/alternate manifests, unmanifested normative entries, conflicting metadata, trailing bytes, and concatenated archives;
- per-entry/aggregate compressed and uncompressed sizes, expansion ratio, count, depth, allocation, and work exhaustion;
- active report content and implicit network fetches;
- tokens, secrets, raw environment dumps, unnecessary user paths, or private identifiers captured as provenance.

Nonexamples:

- Extract first and enforce limits afterward.
- Use archive library default path normalization as the normative rule.
- Fetch a missing reference from the network during archival verification.
- Redact meaning-bearing or committed provenance while preserving the old artifact/result identity silently.

## Alternatives

### A constrained standard archive

Provisional direction, pending hostile-input evidence and an exact allowed feature subset.

### A custom framed container

Retained as an alternative if standard archive ambiguity cannot be bounded safely.

### Directory-only artifacts

Useful for development but insufficient as the sole deterministic portable envelope.

### Network-resolved thin bundles

Rejected for archival verification. Explicit local supplemental content may resolve a reference under a named policy; otherwise the obligation remains unresolved.

## Proposed semantics

No container is Accepted. SQ-0010 must define one authoritative manifest, normalized entry identity, exact allowed entry types/compression, deterministic metadata/order, pre-extraction resource enforcement where possible, inert reports, offline local-only resolution, and privacy-minimized provenance.

Required provenance fields are allowlisted. Tokens, secrets, raw environment dumps, unnecessary user paths, and private identifiers are excluded. Commitments can enable linkability or guessing of low-entropy values and reports disclose that risk. Changing or redacting committed or normative provenance always creates a new normative artifact identity and, where applicable, a new verification-result identity. Redacting only an inert non-normative report leaves the normative artifact identity unchanged, but changes the physical bundle bytes/file commitment and records the report/disclosure transformation. An unresolved leaf is permitted only for an external/uncommitted reference or inside a newly identified normative object/result; it is never an alternative to changing the identity of committed bytes.

## Formal and implementation consequences

- SQ-0010 owns the schema, hostile fixtures, privacy/disclosure rules, and exact error taxonomy.
- SQ-0017 owns accessible report projection and privacy/nonclaim rendering.
- Verification never executes bundled code or active report content.
- External content is never fetched implicitly.

## Trust, security, privacy, and accessibility

The hostile cases above are mandatory. The implementation reports which parser/container library and platform enter the operational TCB. Human reports expose unresolved local references, redactions, privacy/linkability warnings, and limits in text.

## Compatibility and migration

Changing container type, normalization, compression, resource policy, manifest authority, digest coverage, provenance commitment, or external-resolution policy creates a new envelope profile and result identity under RFC-0007.

## Validation plan

- every hostile case above with named deterministic failure class;
- differential parser/container tests where practical;
- bounded processing before extraction and deterministic budget exhaustion;
- no-network and no-active-content checks;
- privacy-leak and redaction-identity fixtures;
- interoperability, security, formal, privacy, adversarial, and integration review.

## Objections and resolution

- **Objection:** A common archive library already handles these cases. **Resolution:** library behavior is version/platform dependent and cannot silently define normative semantics or resource policy.

## Decision

Deferred to SQ-0010. No `.statqed` container or archive behavior is normative until this RFC is Accepted.
