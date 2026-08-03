# RFC-0004: Core Statistical Ontology and Probability Context

- Status: Draft
- Author: SQ-0001 manager
- Reviewers: statistical architect, formal-methods reviewer, interoperability reviewer, counterexample reviewer
- Created: 2026-08-03
- Task: SQ-0008 and method-specific ontology tasks
- Supersedes: none

## Decision boundary

Define the governed relationships among experiment, design, model, state/population, observed data, estimand, procedure, claim, premise, identification, statistical guarantee, interpretation, and probability context. Specify how randomness, conditioning, nesting, coupling, fixed objects, and quantifier scope are represented.

This RFC blocks a universal public experiment or randomness-scope type. SQ-0008 may implement only a minimal reviewed subset that does not silently settle this boundary.

## Motivation

The scaffold currently mixes probability sources, inferential regimes, computational randomization, temporal structure, and interpretations in a flat list. A bare claim label cannot preserve whether a guarantee is pointwise or uniform, conditional or unconditional, finite-sample or asymptotic, or which objects are random and fixed.

## Terminology and source background

`CHARTER.md` requires separate identification, inference, numerical correctness, provenance, and interpretation arguments. `ARCHITECTURE.md` proposes Markov kernels as one useful abstraction but does not freeze a universal representation. Method-specific primary sources will be required because design-based, model-based, sequential, resampling, privacy, and Bayesian probability contexts do not share one informal convention.

## Examples and nonexamples

Examples:

- An assignment-randomization claim names the assignment law; observed/potential outcomes, statistic rule, and null family that are fixed; and the quantified threshold range.
- A Monte Carlo approximation to an assignment p-value records assignment randomness and simulation randomness as nested, distinct contexts.
- An identification claim connects a scientific estimand to an observed-data functional under named external premises, separately from an estimator or confidence procedure.

Nonexamples:

- A generic `probability` enum with no law, conditioning, or fixed-object references.
- Treating `finite_population`, `sequential`, `posterior`, and `monte_carlo` as interchangeable sources of randomness.
- Treating a fitted coefficient, p-value, or checked numeric result as an estimand or identification result.
- Upgrading an asymptotic statement into a finite-sample guarantee.

## Alternatives

### Freeze a universal Markov-kernel interface immediately

Deferred. It is mathematically attractive but has not been tested against the finite, sequential, resampling, causal, and artifact-executable cases.

### Define only method-specific disconnected schemas

Rejected as the long-term architecture because composition would be opaque. It remains a valid prototyping strategy while common structure is reviewed.

### Use a flat randomness-scope enumeration

Rejected for public semantics. Enumerated tags may classify contexts, but cannot replace laws, conditioning, nesting, and quantifiers.

## Proposed semantics

No full semantics are proposed in SQ-0001. Any accepted successor must:

1. distinguish probability sources from regimes, temporal/index structures, computational purposes, and interpretations;
2. record what is random, fixed, conditioned upon, and coupled;
3. state quantifier order and pointwise/uniform scope;
4. distinguish identification targets, observed functionals, procedures, numeric outputs, guarantees, and interpretations;
5. type external assumptions without deriving their empirical truth;
6. support method-specific specializations without silently claiming universal equivalence.

## Formal and implementation consequences

- SQ-0008 may define claim/evidence scaffolding only after statistical and formal review of its exact subset.
- Method packs must supply source-audited probability contexts and cannot reuse a tag with changed semantics.
- IR serialization must use structured references for laws, fixed/conditioned objects, nesting, and quantifier profiles rather than relying on prose labels.
- The first foundation fixture uses `not_applicable` for statistical probability context and makes no statistical claim.

## Trust, security, privacy, and accessibility

Omitted or substituted probability context is an overclaim and type-confusion risk. Reports must render the random/fixed/conditioned partition and external premises in text, not only machine identifiers. Probability-context records may expose design or privacy information and therefore need disclosure review.

## Compatibility and migration

Before acceptance, all ontology documents remain Draft. After type freeze, changing a probability source, conditioning set, quantifier order, estimand, or guarantee creates a new semantic version and claim identity; a display-only migration is insufficient.

## Validation plan

- source variants from the first three scientific slices;
- nontrivial models satisfying each proposed interface;
- assumption ablations and quantifier/randomness mutations;
- examples of nested assignment/Monte Carlo and sequential contexts;
- statistical, formal, interoperability, and adversarial review;
- serialization prototypes before public schema freeze.

## Objections and resolution

- **Objection:** Deferral delays Lean bootstrap. **Resolution:** SQ-0003 can bootstrap the toolchain without statistical abstractions; SQ-0008 is the governed boundary.
- **Objection:** A flat enum is easier for frontends. **Resolution:** frontends may offer ergonomic constructors, but the canonical object must preserve the full context.

## Decision

Deferred. The required distinctions and validation obligations are constitutional constraints, but no universal ontology or randomness type is Accepted. SQ-0008 and all method-specific public definitions remain blocked on review and acceptance of this RFC or a narrower successor.
