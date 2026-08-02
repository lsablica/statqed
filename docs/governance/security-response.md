# Security and Soundness Incident Response

Triage whether a report affects confidentiality, availability, artifact integrity, canonicalization, theorem resolution, checker soundness, or scientific interpretation.

For conclusion-changing issues:

1. restrict details if exploitation is possible;
2. identify affected versions/artifact hashes;
3. reproduce independently;
4. pause affected releases;
5. patch with tests and formal/semantic review;
6. publish an advisory and verification impact;
7. archive revoked or superseded locks without deleting history;
8. perform a root-cause review.
