# ADR-0003: Rust reference operational backend

- Status: Proposed

## Decision

Use Rust for the reference parser, canonicalizer, deterministic encoder, digest tooling, registry utilities, archive handling, and CLI.

## Constraints

Rust implements accepted semantics; it does not define them. Verification code is deterministic, offline, bounded, panic-free on untrusted input, and forbids unsafe code by default.

## Consequences

Frontend packages call or bind to shared Rust functionality rather than reimplementing canonicalization independently.
