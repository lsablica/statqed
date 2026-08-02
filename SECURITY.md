# Security Policy

StatQED artifacts may be processed from untrusted sources. Parsers, decoders, archive handling, certificate checkers, report rendering, and plugin execution are security-sensitive.

## Supported versions

The project is pre-alpha. No version is currently security-supported. This policy will be updated before the first public executable release.

## Reporting

Report suspected vulnerabilities privately to the repository owner through GitHub's private vulnerability reporting mechanism when enabled. Do not publish an exploit before a coordinated fix.

Include:

- affected commit or release;
- artifact or input required to reproduce;
- expected and observed behavior;
- impact on integrity, confidentiality, availability, or soundness;
- whether the issue changes a verification conclusion;
- a minimal reproducer where safe.

## Threats in scope

- malformed CBOR/CDDL or archive inputs;
- path traversal and decompression bombs;
- hash or canonicalization inconsistencies;
- parser differentials across languages;
- unsafe native-code/FFI boundaries;
- denial of service in checkers;
- theorem-lock substitution;
- certificate type confusion;
- untrusted report content;
- supply-chain compromise;
- incorrect trust-report generation;
- proof/checker mismatch.

## Security design requirements

- Verification must not require network access.
- Artifact extraction must be bounded and path-safe.
- Canonical encoders and decoders require differential and fuzz testing.
- Unknown critical fields must fail closed.
- The trusted verifier must never execute bundled code.
- Signatures, if added, complement but do not replace content hashing.
- Security fixes that alter accepted semantics require artifact-version analysis.
