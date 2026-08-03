# RFC-0003: Artifact Decoder and Lean Trust Boundary

- Status: Draft
- Author: foundation verification team
- Reviewers: formal-methods reviewer, interoperability reviewer, security reviewer, counterexample reviewer
- Created: 2026-08-02
- Task: SQ-0012
- Supersedes: Draft placeholder installed at repository bootstrap

## Decision boundary

Select the byte-to-term path for kernel-mode artifact verification and define the logical, semantic-review, cryptographic, and operational trust bases of kernel, compiled-checker, and structural modes. Specify the adequacy obligation connecting artifact bytes to the exact Lean proposition reported.

## Motivation

The Lean kernel can correctly accept a proof of one proposition while a faulty decoder or bridge attributes it to different artifact bytes. “Lean checked something” is therefore insufficient for an artifact-level kernel-verification claim.

## Terminology and source background

- The **logical kernel TCB** is the mechanism whose defect could make the proof system accept a non-derivable proposition.
- The **semantic review base** contains governed definitions, statements, source mappings, and interpretations whose adequacy is not established merely by kernel execution.
- The **artifact-binding TCB/obligation** covers decoding, canonicalization, and the mapping between accepted bytes and checked terms.
- The **operational TCB** includes any compiler, runtime, platform, native checker, code generator, or bridge whose output is relied upon without independent rebinding/checking.
- **Cryptographic assumptions** include collision/second-preimage assumptions for named digests; digest equality is not mathematical injectivity over arbitrary messages.
- **External premises** remain outside formal derivation regardless of mode.

Official Lean kernel/validation sources and exact locators are recorded in `docs/research/SQ-0001-constitutional-source-audit.md`.

## Examples and nonexamples

Examples:

- Kernel acceptance may be reported for the exact elaborated proposition, locked environment, and actual axiom report.
- A compiled checker report names the compiler/runtime/platform that joins its operational TCB.
- Structural mode reports schema/reference/digest checks and no mathematical guarantee.

Nonexamples:

- A bridge maps bytes intended to claim `False` into a checked Lean term for `True`; kernel acceptance does not validate the byte-level claim.
- A decoder/native checker is described as untrusted while its unchecked output determines the reported proposition.
- A theorem-lock resolution is reported as proof of the theorem.
- A matching digest is reported as proof that physical data collection/provenance was truthful.

## Alternatives

### Direct Lean decoding

Potentially simple trust story if decoding and binding execute in checked Lean definitions, but parser complexity and resource behavior require evidence.

### Generate Lean source from a validated representation

Keeps the kernel as final proof checker but trusts or independently checks the generator's faithful byte-to-source binding.

### Compiled/native checker only

Potentially faster and simpler operationally, but compiler/runtime/platform enter the TCB and the result is not kernel mode.

### Hybrid bridge with independently checked manifest/binding proof

May reduce trusted parsing while retaining performance, but the exact proof object and re-binding path require a prototype.

### Defer artifact-level kernel claims

Accepted until one option passes review and implementation. Documentation may say “kernel-checked proposition” only when that proposition/environment is exact; it may not call a `.statqed` artifact kernel-verified.

## Proposed semantics

1. Every verification-result record names exactly one verification mode. A document may contain several separately identified results, but it never unions their evidence or emits an overall status stronger than any one result supports.
2. Kernel mode requires a reviewed byte-to-term adequacy path, exact theorem/environment/proof locks, actual axiom report, and a final kernel check.
3. Compiled-checker mode names all relied-upon compiler/runtime/platform components.
4. Structural mode establishes only the structural propositions it explicitly checks.
5. A component is outside a mode's TCB only when its output is independently rebound and checked for the proposition used.
6. No mode establishes external-premise truth, source fidelity, physical provenance truth, or scientific interpretation merely from mechanical acceptance.

## Formal and implementation consequences

- SQ-0012 must prototype and select one byte-to-term path before implementing an artifact-level kernel report.
- RFC-0001 and RFC-0006 provide the exact bytes/logical-binding profile consumed by the chosen path.
- RFC-0005 governs theorem/environment/proof and axiom locks.
- SQ-0017 renders the distinct trust categories and explicit nonclaims.

## Trust, security, privacy, and accessibility

Threats include differential decoding, misbinding, type confusion, unbounded parsing, code execution, theorem-lock substitution, generated-source injection, compiler/runtime defects, and misleading report language. Verification remains offline and never executes bundled code. Reports must describe mode and nonclaims in plain text.

## Compatibility and migration

Changing a relied-upon bridge, decoder, binding proof, compiler/runtime, or mode changes the verification record and may change artifact compatibility. Historical verification requires archived exact components or a reviewed migration with a new result identity.

## Validation plan

- competing byte-to-term prototypes and documented TCB comparison;
- malicious misbinding and type-confusion fixtures;
- malformed/resource and generated-source injection tests;
- exact axiom/environment report integration;
- independent formal, interoperability, security, adversarial, and integration review;
- trust-report overclaim tests.
- multi-result tests proving structural success cannot inherit a kernel label and a kernel result cannot hide structural-only failures.

## Objections and resolution

- **Objection:** The kernel is enough because it checks the proof. **Resolution:** it checks the proposition it receives, not whether untrusted bytes were mapped to the intended proposition.
- **Objection:** The Rust decoder is already the reference implementation. **Resolution:** reference behavior does not remove it from an operational TCB when its output is relied upon unchecked.

## Decision

Deferred to SQ-0012. Until this RFC is Accepted and its chosen path implemented, StatQED may not claim artifact-level kernel verification. ADR-0008 records only the minimal-TCB direction and untrusted-producer rule.
