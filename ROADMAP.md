# StatQED Roadmap

The roadmap is organized by scientific capability, not calendar promises. Execution is controlled by dependency-ready tasks in `work/backlog.yaml` and living plans in `docs/exec-plans/`.

## Phase 0 — Constitution and repository harness

Exit criteria:

- project charter and architectural decisions accepted;
- agent instructions scoped and tested;
- task, review, source-lineage, and handoff contracts in place;
- repository checks enforce documentation and workflow invariants;
- toolchain selection plan approved;
- no implementation claim exceeds current evidence.

Current status: **active**.

## Phase 1 — Executable foundation

Deliverables:

- pinned Lean/Mathlib toolchain;
- Rust workspace and `statqed` CLI skeleton;
- CDDL schemas and deterministic encoding test vectors;
- Lean core types for claims, evidence, assurance nodes, and method packs;
- theorem registry parser and lock format;
- R, Python, and Julia package skeletons;
- cross-language golden-test harness;
- structural `.statqed` bundle validation;
- reproducible development environment.

Exit criterion: all three frontends can emit byte-identical canonical IR for a trivial analysis, and Lean can validate a structural artifact without trusting frontend code.

## Phase 2 — First complete method: randomization inference

Deliverables:

- finite assignment mechanisms;
- exact randomization test semantics;
- super-uniformity theorem under explicit assumptions;
- exact integer-count certificate checker;
- confidence-set inversion;
- Bonferroni and Holm packs;
- R/Python/Julia frontend constructors;
- positive, negative, corrupted, and assumption-ablation fixtures;
- first end-to-end publication-ready exemplar.

Exit criterion: an independently verified `.statqed` artifact establishes a finite-sample guarantee conditional on a visibly attested randomization design.

## Phase 3 — Certified linear statistical computing

Deliverables:

- canonical model-matrix normal form;
- typed weights and contrasts;
- OLS/WLS objective semantics;
- rank, normal-equation, and factorization witnesses;
- rigorous coefficient/contrast intervals;
- exact Gaussian-model theorem pack;
- clearly separated asymptotic/sandwich claims;
- cross-language adapters for selected model objects.

Exit criterion: R, Python, and Julia produce equivalent IR for a fixed model specification, and the same concrete contrast is independently certified.

## Phase 4 — Modern finite-sample inference

Deliverables:

- split conformal prediction;
- one full conformal finite case;
- e-values or test martingales;
- one confidence-sequence family;
- typed stopping rules and randomness scopes;
- external black-box predictor integration.

Exit criterion: a complex untrusted predictor can participate in a verified finite-sample guarantee without entering the trusted computing base.

## Phase 5 — Identification and causal semantics

Deliverables:

- potential-outcome and observed-data semantic layers;
- formal identification interfaces;
- randomized treatment identification;
- back-door and selected instrumental-variable results;
- partial-identification objects;
- sensitivity-analysis evidence types;
- explicit estimand-to-estimator links.

Exit criterion: artifacts visibly distinguish a causal estimand, its identification theorem, the observed-data functional, estimator, inferential guarantee, and numerical result.

## Phase 6 — Convex statistical estimation

Deliverables:

- GLM, ridge, lasso, elastic-net, and quantile-regression packs;
- primal-dual, KKT, duality-gap, and separation/nonexistence certificates;
- interval-certified likelihood and link calculations;
- solver-independent result verification.

## Phase 7 — Asymptotic and high-dimensional bridges

Deliverables:

- stable interfaces to existing Lean empirical-process and asymptotic-statistics work;
- finite-versus-asymptotic claim classes;
- explicit remainder terms and convergence modes;
- M-estimation, LAN, efficiency, and sparse-estimation method bridges;
- finite-\(n\) approximation evidence where available.

## Phase 8 — Difficult empirical workflows

Research towers:

- missing data and multiple imputation;
- complex surveys;
- bootstrap and resampling;
- survival analysis;
- mixed and hierarchical models;
- meta-analysis;
- selective inference;
- adaptive designs;
- differential privacy and federated analysis;
- Bayesian posterior computation and nonasymptotic MCMC error.

## Phase 9 — Ecosystem and independent implementations

Deliverables:

- stable plugin/method-pack protocol;
- independent frontend and verifier implementations;
- cross-prover validation experiments;
- journal/repository integration;
- proof-carrying notebooks;
- archival verification policy;
- community governance beyond the founding repository.

## Continuous research programmes

Across every phase, StatQED will study:

- minimum sufficient assumption sets;
- theorem non-vacuity;
- quantifier and randomness-scope errors;
- source-faithful automated formalization;
- explicit constants and finite-sample refinements;
- semantic equivalence across statistical software;
- efficient certificate formats;
- human and agent review effectiveness;
- theorem and artifact discoverability;
- formalization-driven counterexamples and corrections.
