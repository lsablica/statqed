# StatQED Architecture

This document is the top-level architectural map. Detailed specifications live under `docs/design/`, `docs/spec/`, and accepted ADRs.

## System decomposition

```text
R / Python / Julia / declarative files / future agents
                         │
                         ▼
               frontend analysis object
                         │
                checked canonicalization
                         ▼
                StatQED Statistical IR
                         │
        ┌────────────────┼─────────────────┐
        ▼                ▼                 ▼
 theorem selection   numeric obligations  provenance binding
        │                │                 │
        ▼                ▼                 ▼
 Lean theorem pack   untrusted producer   canonical digests
        │                │                 │
        └───────────┬────┴─────────────────┘
                    ▼
          Statistical Assurance Graph
                    │
                    ▼
         deterministic `.statqed` bundle
                    │
          ┌─────────┴──────────┐
          ▼                    ▼
     Lean verifier       human-readable report
```

## Architectural layers

### 1. Statistical semantics

Lean definitions for experiments, randomness scopes, designs, models, estimands, procedures, guarantees, evidence, and claims.

The abstract experiment interface should align with Markov kernels where possible:

\[
P : \Theta \leadsto \mathcal X.
\]

A possibly randomized procedure is similarly represented:

\[
\delta : \mathcal X \leadsto \mathcal A.
\]

Finite, computable specializations are introduced where artifact checking requires executable representations.

### 2. Statistical IR

A small, typed, language-neutral representation. Planned dialects:

- data;
- design;
- experiment/model;
- estimand;
- procedure;
- claim;
- numerical obligation;
- evidence;
- provenance.

The IR records probability sources explicitly. Assignment randomness, sampling randomness, bootstrap randomness, Monte Carlo randomness, algorithmic randomness, and posterior uncertainty are not interchangeable.

### 3. Canonicalization backend

A Rust reference implementation will:

- parse versioned source representations;
- validate structural constraints;
- lower supported constructs to canonical form;
- encode deterministic CBOR;
- compute logical data and theorem-lock digests;
- expose a stable CLI;
- generate or consume language bindings;
- run shared conformance vectors.

Rust is not the semantic authority. The normative specification and Lean model remain authoritative. Rust is the reference operational implementation and is treated according to the trust mode used.

### 4. Certificate producers

R, Python, Julia, Rust, C++, BLAS/LAPACK, optimization systems, and other tools may produce witnesses. They are not trusted merely because they produced a witness.

Examples:

- exact integer counts;
- matrix factorizations;
- normal-equation residuals;
- primal-dual pairs;
- interval enclosures;
- finite traces;
- rank orderings;
- transition traces.

### 5. Certificate checkers

Small checkers consume an IR instance and witness. Each checker has a soundness theorem linking acceptance to a mathematical proposition.

The preferred pattern is:

```lean
check : Spec → Witness → Bool

check_sound :
  check spec witness = true →
  NumericFact spec witness
```

The method’s inferential theorem is separate:

```lean
inferential_sound :
  Assumptions spec →
  NumericFact spec witness →
  Guarantee spec
```

This prevents numerical verification from manufacturing evidence for external assumptions.

### 6. Assurance graph

A typed directed acyclic graph records:

- claims;
- premises;
- evidence;
- theorem applications;
- computation checks;
- transformations;
- attestations;
- diagnostics;
- unresolved obligations;
- provenance.

Graph composition is valid only when node and edge types align. Diagnostics cannot be promoted to assumptions without an explicit theorem or attestation rule.

### 7. Artifact bundle

The provisional extension is `.statqed`.

The bundle contains:

- canonical manifest;
- claims;
- assurance graph;
- theorem lock;
- data bindings;
- certificate payloads or references;
- provenance;
- citations;
- optional reports.

Normative structured objects use deterministic CBOR governed by CDDL schemas. JSON/YAML views are for inspection and authoring only. Arrow is used as an interoperable tabular transport, while the logical data digest is defined independently of Arrow’s physical encoding.

### 8. Theorem registry

Every public theorem has:

- stable identifier;
- Lean declaration;
- normalized statement hash;
- version and maturity;
- claim class;
- randomness scopes;
- assumptions;
- conclusion;
- source anchors;
- source-fidelity review;
- statistical-semantic review;
- proof status and axiom report;
- examples, nonexamples, and ablation tests;
- compatibility relations to predecessor versions.

### 9. Frontends

Frontends operate in three assurance modes:

1. **Native declarative mode:** build the IR directly using supported typed constructors.
2. **Checked adapter mode:** inspect common language objects and independently lower them to canonical form.
3. **Opaque capture mode:** commit an external output and verify only downstream obligations.

A frontend may improve ergonomics but must not redefine core semantics.

## Repository modules

```text
lean/              normative semantics, proofs, checkers, verifier
backend/           Rust reference backend and CLI
schemas/           CDDL, JSON Schema projections, golden examples
frontends/         R, Python, and Julia packages
methods/           method-pack source and cross-language fixtures
theorem-registry/  stable metadata and statement locks
benchmark/         StatQEDBench data and evaluation harness
examples/          complete user-facing analyses
agents/            canonical workflows and role contracts
work/              dependency-aware task ledger
docs/              system of record for design and execution
```

## Trust modes

### Kernel mode

The artifact is decoded into Lean terms or verified structures, a proof is constructed/replayed, and the Lean kernel checks the final result.

### Compiled-checker mode

A compiled checker validates the artifact. This is faster, but the operational trusted computing base includes the compiler/runtime and platform named in the verification report.

### Structural mode

Only schema, digest, and reference integrity are checked. No mathematical verification claim is made.

Every report names its mode.

## Version boundaries

StatQED versions separately:

- IR schema;
- artifact schema;
- assurance graph schema;
- theorem registry;
- method packs;
- proof backend;
- frontend adapters;
- CLI protocol.

An artifact contains exact versions and content hashes. “Compatible” must be justified by a migration or implication/equivalence proof, not merely by semantic version ranges.

## Architectural prohibitions

- No frontend-specific object in the normative IR.
- No raw floating-point decimal interpreted as an exact real.
- No mutable global registry during verification.
- No network access required by archival verification.
- No theorem selected solely by natural-language similarity.
- No hidden fallback from failed verification to replay-only output.
- No certificate accepted without a checker-to-proposition soundness path.
- No public guarantee without an explicit randomness scope and quantifier structure.
