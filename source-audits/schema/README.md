# SQ-0006 schema source audits

Status: Draft. Sources and currentness checks were retrieved on 2026-08-10.

| Audit | Scope | Disposition |
|---|---|---|
| `SA-SQ0006-CDDL.yaml` | RFC 8610, errata, RFC 9682, published extensions, and active drafts | Use RFC 8610 as updated by RFC 9682, apply Verified EID 6526, record but do not elevate Held errata, and prohibit draft syntax. |
| `SA-SQ0006-CDDL-VALIDATOR.yaml` | `cddl` 0.10.6 provenance, license, toolchain, features, and advisory evidence | Conditionally suitable as an isolated untrusted `cddl_shape` development/CI tool; it is not a normative authority. |

## Audited boundary

The closed six-field CDDL map structurally covers exact field presence, unknown-field rejection, four literal values, `analysis_id` being a text string, and `features` being exactly `[]`. It deliberately does not cover the ASCII identifier grammar or its 1–128 byte bound. The independent semantic validator owns those predicates.

The RFC-0001 raw/profile stage runs before CDDL and owns framing, preferred encodings, definite lengths, duplicate-key rejection, UTF-8 policy, and deterministic map ordering. A successful CDDL invocation therefore supports only `cddl_shape`; it is not deterministic-byte, semantic, provenance, digest, statistical, or artifact verification.

## Standards disposition

The current published base is RFC 8610 plus its sole Verified erratum, EID 6526, as updated by RFC 9682. The other four RFC 8610 errata are Held for Document Update and are recorded without being promoted. RFCs 9165 and 9741 are published optional control extensions and are unnecessary here. `draft-ietf-cbor-cddl-modules-06`, `draft-bormann-cbor-cddl-freezer-17`, and the validator's documented CSV draft are Work in Progress; no module, import, freezer, CSV, or other draft-only syntax is permitted in the normative schema.

## Validator disposition

The selected candidate is crates.io `cddl` 0.10.6 from source commit `a42a702cf977179236523e5559c81e7bbd5dfa7e`:

- crate SHA-256: `69f7305ff73327bd9ce5e5cdd81223dd91b4969e260ea6cdb8f1da94390be191`
- packaged lockfile SHA-256: `193467cae8f59b079960f6678cc7a0951f9391a7854fbe636489d30cdfddcb93`
- license: MIT; retain its copyright and permission notices
- declared Rust minimum: 1.88.0

The project Rust 1.85.1 support floor cannot build this version. Prior retained evidence shows failure at 1.85.1 and success with Rust/Cargo 1.97.1 on Ubuntu 24.04 x86_64, so the validator needs a separately pinned development/CI toolchain. Its default executable includes support for optional RFC controls and active drafts. Feature-ablation tests did not produce a useful draft-free CLI: smaller sets failed to compile, while the smallest tested successful set still included CSV/freezer support. Normative syntax is therefore controlled by schema review and an allowlist, never by what the executable happens to parse.

Use exact, noninteractive, explicit-file invocations:

```console
cargo install cddl --version 0.10.6 --locked
cddl --ci compile-cddl --cddl schemas/v0/compiled/foundation-structural.cddl
cddl --ci validate --cddl schemas/v0/compiled/foundation-structural.cddl --cbor VALID_FIXTURE
```

Avoid stdin for normative CBOR tests because the CLI auto-detects valid UTF-8 input as JSON. A direct OSV query for `crates.io:cddl:0.10.6` returned no matching record on 2026-08-10. A separately retained cargo-audit 0.22.2 observation bound to RustSec database commit `309ad29d8fe448bf986019e05d47b9e0e29a2218`, the exact 154-package lock, tool/archive hashes, and 1,197 loaded advisories reported zero vulnerabilities and zero warnings. Both observations are point-in-time evidence, not a security clearance; the committed record and reproduction checker are `cddl-advisory-observation.json` and `scripts/schema/check_cddl_advisory.py`.

These records remain `DRAFT`; they do not freeze a schema, approve a toolchain, or replace independent schema, conformance, security, and trust review.
