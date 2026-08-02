# StatQED

**Proof-carrying statistical analysis across R, Python, Julia, and Lean.**

StatQED is an academic infrastructure project for expressing, checking, and publishing statistical claims as portable assurance artifacts. It is not a wrapper that sends arbitrary source code to a theorem prover. Its intended contribution is a language-independent semantic layer connecting:

\[
\text{scientific target}
\rightarrow
\text{design and model}
\rightarrow
\text{estimand}
\rightarrow
\text{procedure}
\rightarrow
\text{computation}
\rightarrow
\text{reported claim}.
\]

R, Python, and Julia are planned as user-facing frontends. Lean 4 is the initial normative proof backend. A small Rust implementation is planned for canonicalization, serialization, hashing, command-line verification, and shared cross-language infrastructure.

> **Repository status:** constitutional and execution-planning phase. The repository currently specifies what must be built, how agents must build it, and which scientific claims are in or out of scope. It does not yet claim to verify statistical analyses.

## Why StatQED

A statistical result can fail for several distinct reasons:

1. the scientific estimand was not identified by the assumptions;
2. the inferential procedure did not have the claimed operating characteristics;
3. the concrete numerical result was computed incorrectly;
4. the result was not actually derived from the declared data and workflow;
5. the prose conclusion exceeded what any of the preceding layers established.

Existing systems usually address only part of this chain. StatQED will represent the chain explicitly as a typed **Statistical Assurance Graph**. Every conclusion will expose its dependencies, evidence types, randomness scopes, unresolved assumptions, and verification boundary.

StatQED will never use a single undifferentiated “verified” badge. It will report an assurance profile covering data binding, transformations, numerical computation, statistical guarantees, identification, external assumptions, source-language fidelity, and provenance.

## Intended project family

| Component | Planned role |
|---|---|
| `StatQED` Lean library | Statistical semantics, theorem interfaces, certificate checkers, artifact verification |
| `statqed-core` Rust crates | Canonical IR, deterministic encodings, digests, registry tooling, CLI |
| `statqed` CLI | Build, inspect, validate, and verify `.statqed` artifacts |
| `statqed` for R | R-native constructors, model adapters, reports, certificate producers |
| `statqed` for Python | Python-native constructors, adapters, reports, certificate producers |
| `StatQED.jl` | Julia-native constructors, adapters, reports, certificate producers |
| StatQED Method Packs | End-to-end formal methods, witnesses, checkers, examples, and citations |
| StatQEDBench | Source-aligned benchmark for formal statistical reasoning and agent systems |
| StatQED Registry | Stable theorem identifiers, statement hashes, assumptions, provenance, and review metadata |

Package names remain provisional until registry availability and naming policies are formally checked.

## First three vertical slices

1. **Exact randomized experiment**  
   Complete and blocked randomization, exact randomization \(p\)-values, confidence-set inversion, and Bonferroni/Holm multiplicity. The mathematical result is finite-sample and the computational witness can be exact.

2. **Linear model with an explicit contrast**  
   Cross-language lowering to a canonical model matrix, certified least-squares computation, rank and factorization witnesses, and a strict separation between optimization correctness and inferential validity.

3. **Conformal or sequential inference**  
   A finite-sample prediction or anytime-valid guarantee that exercises ranks, martingales, stopping rules, and multiple sources of randomness.

## Scientific rules

The following constraints are constitutional:

- External scientific assumptions are never presented as kernel-verified facts.
- Identification, inferential validity, numerical correctness, and data provenance are separate proof layers.
- A certificate producer may be fast and untrusted; the checker must be small, deterministic, and formally connected to its conclusion.
- Frontend source languages are not semantic authorities. They lower to a canonical statistical IR.
- An agent may not make a theorem easier by silently strengthening assumptions or changing a frozen statement.
- Every public theorem requires source lineage, non-vacuity evidence, assumption-ablation tests where meaningful, and an axiom report.
- No unresolved `sorry` or project-introduced axiom is permitted in a trusted release path.
- General mathematics should be upstreamed to Mathlib when appropriate.
- Statistical diagnostics are evidence, not automatic proofs of model assumptions.
- Asymptotic validity is not silently upgraded to finite-sample accuracy.

See [CHARTER.md](CHARTER.md), [ARCHITECTURE.md](ARCHITECTURE.md), and [docs/design/core-beliefs.md](docs/design/core-beliefs.md).

## Starting work

Humans should read:

1. [START_HERE.md](START_HERE.md)
2. [AGENTS.md](AGENTS.md)
3. [docs/exec-plans/active/0001-foundation-bootstrap.md](docs/exec-plans/active/0001-foundation-bootstrap.md)
4. [work/backlog.yaml](work/backlog.yaml)

Coding agents should use the exact launch contract in `START_HERE.md`, select only dependency-ready tasks, and keep the active execution plan current.

Repository checks:

```bash
make check
make list-work
```

## Scope of trust

The intended trusted computing base is deliberately small:

- the Lean kernel and pinned formal sources;
- the artifact decoder used by the trusted verifier;
- certificate checkers and their soundness proofs;
- cryptographic/data-binding primitives named by the artifact.

R, Python, Julia, numerical solvers, BLAS/LAPACK, report generators, LLM agents, and certificate producers are treated as untrusted unless a narrower component is separately verified.

## Project maturity

StatQED uses explicit maturity labels:

- **Draft:** exploratory and changeable;
- **Experimental:** implemented but not stable;
- **Candidate:** semantics frozen for review;
- **Stable:** versioned, reviewed, conformance-tested, and migration-governed;
- **Archived:** retained for verification of historical artifacts.

Nothing in the initial scaffold is Stable.

## License and citation

Code, specifications, and documentation are licensed under MIT License unless a file states otherwise. Citation metadata is in [CITATION.cff](CITATION.cff). Original mathematical and software sources must be cited alongside StatQED; formalization does not transfer authorship of prior results.

## Name

“QED” is used in its ordinary mathematical sense: *quod erat demonstrandum*. The project name does not imply that empirical assumptions can be proved from data merely by running software.
