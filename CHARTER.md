# StatQED Project Charter

Status: **Draft**.

## Mission

StatQED will establish a rigorous, reusable, language-independent foundation for proof-carrying statistical analysis.

Its central research object is a machine-checkable chain from a declared scientific target to a concrete reported claim. The project will make every deductive step, numerical witness, data-derived fact, external assumption, diagnostic, and provenance dependency explicit.

The project is successful when independent researchers can:

- express a statistical analysis without depending on one programming language;
- attach a concrete computation to a formally stated statistical guarantee;
- identify precisely which parts are proved, computed, observed, attested, or unresolved;
- verify the resulting artifact independently;
- extend the system through reviewed method packs;
- cite stable theorem and artifact identifiers;
- use the corpus to study formal statistical reasoning and automated formalization.

## Research thesis

A statistical analysis is not adequately represented by source code plus output. It requires a typed semantic object containing, at minimum:

\[
(\text{population or state space},
\text{data-generating or assignment mechanism},
\text{estimand},
\text{procedure},
\text{claim},
\text{assumptions},
\text{probability context and quantifier scope},
\text{evidence},
\text{provenance},
\text{interpretation and nonclaims}).
\]

The project thesis is that this object can be made compositional, portable, and checkable without requiring the entire source-language runtime or numerical solver to enter the trusted computing base.

## Long-horizon objectives

1. Define the standard semantic vocabulary for machine-checkable statistical claims.
2. Build a high-quality Lean library of applied statistical inference over Mathlib.
3. Define an open, deterministic artifact format for proof-carrying analyses.
4. Support R, Python, and Julia through thin, conformant frontends.
5. Establish a method-pack ecosystem with stable theorem identifiers and review metadata.
6. Create the canonical benchmark for formal statistical reasoning and assurance.
7. Produce new statistical insights through assumption minimization, counterexamples, explicit constants, and composition theorems.
8. Make verified analysis artifacts usable in papers, teaching, reproducibility reviews, and AI-generated workflows.
9. Preserve artifacts across toolchain upgrades through theorem locks, migrations, and archival verification.
10. Build governance that can outlive the founding researcher and founding implementation.

## Non-goals

StatQED does not initially aim to:

- verify arbitrary R, Python, or Julia programs;
- formalize complete interpreters for those languages;
- replace Mathlib probability foundations;
- replace numerical libraries with Lean implementations;
- prove that a scientific protocol was followed in the physical world;
- infer causal assumptions, exchangeability, independence, or measurement validity from a finite dataset;
- assign scientific meaning to an analysis automatically;
- use an LLM as part of the trusted verification path;
- provide a universal binary “correct analysis” decision;
- claim regulatory approval or legal sufficiency.

## Constitutional separations

### Identification

Whether a scientific estimand follows from an observed-data distribution under stated assumptions.

### Statistical inference

Whether a procedure has a stated operating characteristic under a sampling, assignment, model, or sequential regime.

### Numerical computation

Whether the concrete reported value satisfies a checkable mathematical obligation.

### Data and provenance binding

Whether the checked mathematical object is tied to declared bytes, tables, transformations, software, and agents.

### Interpretation

Whether prose conclusions remain within the scope of the formal and empirical evidence.

No layer may silently stand in for another.

## Public-interest commitments

- The verifier, core semantics, artifact format, and fundamental theorem interfaces will remain open.
- A valid artifact must not require a proprietary verification service.
- The project will preserve attribution to original theorem authors and software contributors.
- Method packs will disclose assumptions and limitations in machine-readable and human-readable forms.
- The project will publish negative results, failed formalizations, and discovered counterexamples where scientifically useful.
- Security, privacy, accessibility, and reproducibility are design requirements rather than later additions.

## Decision hierarchy

1. Mathematical and scientific correctness.
2. Explicit trust boundaries and honest claims.
3. Stable semantics and interoperability.
4. Independent reproducibility.
5. Maintainability by humans and agents.
6. Performance.
7. Frontend convenience.

A lower item may not override a higher item without an accepted RFC explaining the trade-off.

## Change control

Changes to any of the following require an RFC and architecture/statistical review:

- core statistical ontology;
- evidence categories or assurance lattice;
- normative artifact encoding;
- theorem identifier semantics;
- trusted computing base;
- public method-pack contract;
- compatibility policy;
- interpretation of a guarantee class;
- source-lineage requirements;
- definition of “verified,” “certified,” or related status language.

See `docs/governance/rfc-process.md`.

## Founding success criterion

The first scientifically complete release must independently verify three end-to-end exemplars:

1. an exact randomized experiment;
2. a linear-model contrast with a certified numerical solution;
3. a finite-sample conformal or sequential procedure.

Each exemplar must work through at least two frontends, produce the same canonical IR, emit a portable artifact, pass independent verification, and show unresolved assumptions explicitly.
