# StatQED Architecture

Status: **Draft**.

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
- encode according to the Accepted `statqed.cbor-core.v1` deterministic CBOR profile from RFC-0001;
- compute logical data and theorem-lock digests;
- expose a stable CLI;
- generate or consume language bindings;
- run shared conformance vectors.

Rust is not the semantic authority. Accepted normative specifications govern cross-language meaning; reviewed Lean definitions and statements govern the propositions checked by the initial proof backend. Rust is the reference operational implementation and is treated according to the named verification mode.

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

Graph composition is valid only when node and edge types align. A diagnostic may inform a non-deductive judgment, but neither a diagnostic nor an attestation discharges an external assumption. A registered theorem may derive a distinct formal proposition only from all of its explicit premises.

### 7. Artifact bundle

The provisional extension is `.statqed`. The exact outer container remains a Draft SQ-0010 decision.

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

Normative data-free structured objects use the bounded deterministic CBOR profile accepted by RFC-0001/SQ-0005 and may use versioned published-syntax CDDL for structural subsets. JSON/YAML views remain for inspection and authoring only. Arrow is a candidate interoperable tabular transport; RFC-0006 must define any transport-independent logical data object and digest.

### 8. Theorem registry

Every public theorem has:

- stable identifier;
- Lean declaration;
- canonical elaborated statement bytes, normalization/environment version, and statement digest;
- version and maturity;
- claim class;
- randomness scopes;
- assumptions;
- conclusion;
- source anchors;
- source-fidelity review;
- statistical-semantic review;
- canonical registry record and its content lock;
- proof/build lock, proof status, and actual transitive axiom report;
- examples, nonexamples, and ablation tests;
- compatibility relations to predecessor versions.

Registry resolution also records the independently selected authorization root/policy, its historical or revocation status, and the exact resolution result. An artifact-supplied registry record or root has no governed authority merely because it is self-consistent.

### 9. Frontends

Frontends operate in three assurance modes:

1. **Native declarative mode:** build the IR directly using supported typed constructors.
2. **Checked adapter mode:** inspect common language objects and independently lower them to the accepted semantic IR.
3. **Opaque capture mode:** commit an external output and verify only downstream obligations.

A frontend may improve ergonomics but must not redefine core semantics. Production frontends may share the Rust canonical encoder; agreement among callers of that same encoder is an integration test, not independent encoder-conformance evidence.

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

The exact artifact bytes are rebound to Lean terms or verified structures through an accepted RFC-0003 path, and the Lean kernel checks the resulting exact proposition under locked dependencies and an actual axiom report. Until that path is implemented, documentation may describe a kernel-checked proposition but not an artifact-level kernel-verification result.

### Compiled-checker mode

A compiled checker establishes only its exact accepted checker propositions under the reported operational trusted computing base, which includes the relied-upon compiler/runtime and platform. It does not globally validate every artifact claim or any external premise.

### Structural mode

Only schema, digest, and reference integrity are checked. No mathematical verification claim is made.

Every verification-result record names exactly one mode. A document may contain several separately identified results, but it never unions their evidence or emits an overall stronger status.

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

An artifact contains the exact semantic and verification locks it uses: IR, encoding profile, envelope, assurance graph, data-digest profile when applicable, theorem/method/checker records, and proof environment. Frontend, CLI, and report-generator versions are provenance unless their transformation semantics are referenced by a claim. Wire and error protocols are versioned separately. “Compatible” must be justified by canonical equality in the same locked environment or by a checked migration/implication/equivalence in the required direction, not merely by semantic-version ranges or registry metadata.

## Architectural prohibitions

- No frontend-specific object in the normative IR.
- No raw floating-point decimal interpreted as an exact real.
- No mutable global registry during verification.
- No network access required by archival verification.
- No theorem selected solely by natural-language similarity.
- No hidden fallback from failed verification to replay-only output.
- No certificate accepted without a checker-to-proposition soundness path.
- No public guarantee without an explicit randomness scope and quantifier structure.
