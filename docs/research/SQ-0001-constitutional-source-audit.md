# SQ-0001 Constitutional Source Audit

Status: **Candidate**

Retrieval date: **2026-08-03**. Repository baseline: `2ad5c72f7adc402024152d6fa4af9c86cdf9b588`. Frozen candidate constitutional surface: **77 changed files**, bound by the sorted `sha256sum`-lines digest `sha256:5793ce0b5c7e819090c74480e93e7167f6821897b96567c8b6c737bc8fa1ff96` under the manifest recipe recorded below.

Audit outcome: **source reviewed at Candidate maturity, with explicit blockers and deferrals**. The monorepo, Lean/Mathlib, Rust reference-backend, MIT/CFF, theorem-registry direction, shared RFC-aware readiness calculation, two-state registered-decision vocabulary and Draft-owner lifecycle gates, SQ-0027 logical-data ownership, SQ-0020 completion gates, provenance-redaction identity rules, and ADR-0011 toy-slice scope are supportable as project decisions. RFC-0001 through RFC-0009 retain their stated Draft/deferred boundaries; their presence in the decision register is not acceptance. Rejection, withdrawal, supersession, and successor relations remain deferred rather than silently receiving semantics. This audit does not establish exclusive name availability, trademark clearance, a finalized canonical encoding profile, theorem normalization or registry authorization behavior, logical-data digest semantics, an implemented artifact envelope/privacy/security mechanism, toolchain compatibility, package publication, community-body authority, or any implemented verification behavior.

The YAML record below follows `agents/templates/source-audit.yaml`. `Candidate` records source-curator disposition of the exact manifest only; it does not claim completion of the independent statistical, formal, interoperability, adversarial, security/trust, privacy, or integration reviews. Exact endpoint responses reported by the SQ-0001 integration manager are identified as such; they are not silently upgraded into availability claims. No language toolchain, package publisher, encoder, decoder, CDDL validator, theorem hasher, artifact verifier, archive parser, or privacy/security implementation was run for this audit.

```yaml
audit_id: "SA-SQ-0001-CONSTITUTION"
subject: "SQ-0001 candidate constitutional surface: naming, package boundaries, Lean/Mathlib, Rust, deterministic CBOR/CDDL, license/citation, theorem registry authorization, decision-owner gates, deferred interfaces, and the data-free foundation slice"
source:
  work: |-
    Baseline provenance: StatQED repository commit
    2ad5c72f7adc402024152d6fa4af9c86cdf9b588.

    Reviewed frozen candidate constitutional surface: the 77 paths changed from that
    baseline, including tracked modifications and untracked candidate files,
    after excluding `.codex/`, this audit, `work/reviews/SQ-0001.md`,
    `work/handoffs/SQ-0001.md`, and `work/status.yaml`. For each selected path,
    compute the ordinary `sha256sum` line, sort the complete lines bytewise in
    the C locale, and SHA-256 hash their newline-terminated concatenation. The
    resulting manifest digest is
    sha256:5793ce0b5c7e819090c74480e93e7167f6821897b96567c8b6c737bc8fa1ff96.

    External lineage consists of the official standards, language/package
    documentation, registries, and identifier/citation specifications listed
    under locator.
  version: |-
    Repository baseline 2ad5c72f7adc402024152d6fa4af9c86cdf9b588;
    frozen candidate manifest count 77 and sorted sha256sum-lines digest
    sha256:5793ce0b5c7e819090c74480e93e7167f6821897b96567c8b6c737bc8fa1ff96;
    RFC 8949 / STD 94 (December 2020); RFC 8610 (June 2019), as updated by
    RFC 9682 (November 2024), plus RFC 9165 (December 2021) and RFC 9741
    (March 2025); Lean documentation observed for 4.32.1 and the then-latest
    4.33.0-rc1 manual; CFF schema 1.2.0; SWHID specification 1.2;
    official web state retrieved 2026-08-03.
  locator: |-
    INTERNAL, exact headings:
    - CHARTER.md: Mission; Non-goals; Constitutional separations; Public-interest commitments; Change control.
    - ARCHITECTURE.md: 1. Statistical semantics; 3. Canonicalization backend; 7. Artifact bundle; 8. Theorem registry; Repository modules; Trust modes; Version boundaries; Architectural prohibitions.
    - README.md: Intended project family; Scientific rules; Scope of trust; License and citation.
    - ROADMAP.md: Phase 1 — Executable foundation; Phase 2 — First complete method: randomization inference; Phase 3 — Certified linear statistical computing; Phase 4 — Modern finite-sample inference.
    - GOVERNANCE.md: Current authority; Planned bodies; Decision classes; Transparency; Releases.
    - docs/adr/0001-monorepo-first.md: Decision; Consequences; Validation and evidence; Review.
    - docs/adr/0002-lean4-normative-proof-backend.md: Decision; Consequences; Validation and evidence; Review.
    - docs/adr/0003-rust-reference-backend.md: Decision; Constraints and consequences; Validation and evidence; Review.
    - docs/adr/0004-deterministic-cbor-cddl.md: Candidate decision; Consequences; Validation and evidence; Review.
    - docs/adr/0005-typed-assurance-graph.md: Decision; Prohibitions and consequences; Validation and evidence; Review.
    - docs/adr/0006-thin-frontends.md: Decision; Consequences; Validation and evidence; Review.
    - docs/adr/0007-versioned-theorem-registry.md: Candidate decision; Consequences; Validation and evidence; Review.
    - docs/adr/0008-minimal-tcb-and-untrusted-producers.md: Decision; Consequences; Validation and evidence; Review.
    - docs/adr/0009-project-and-package-naming.md: Decision; Consequences; Validation and evidence; Review.
    - docs/adr/0010-license-citation-and-attribution.md: Decision; Consequences; Validation and evidence; Review.
    - docs/adr/0011-foundation-toy-slice.md: Decision; Verification result and nonclaims; Validation and evidence; Review.
    - rfcs/0001-deterministic-encoding.md: Decision boundary; Proposed semantics; Validation plan; Decision.
    - rfcs/0002-evidence-taxonomy.md: Decision boundary; Proposed semantics; Validation plan; Decision.
    - rfcs/0003-artifact-decoder-trust.md: Decision boundary; Proposed semantics; Validation plan; Decision.
    - rfcs/0004-core-statistical-ontology.md: Decision boundary; Proposed semantics; Validation plan; Decision.
    - rfcs/0005-theorem-identity-and-compatibility.md: Terminology and source background; Proposed semantics; Validation plan; Decision.
    - rfcs/0006-canonical-logical-data-digest.md: Decision boundary; Omit data from the foundation fixture; Proposed semantics; Formal and implementation consequences; Validation plan; Decision.
    - rfcs/0007-compatibility-and-migration.md: Decision boundary; Proposed semantics; Validation plan; Decision.
    - rfcs/0008-artifact-envelope-and-offline-resolution.md: Decision boundary; Proposed semantics; Trust, security, privacy, and accessibility; Decision.
    - rfcs/0009-community-governance-structure.md: Decision boundary; Proposed semantics; Decision.
    - docs/design/naming-and-packages.md: complete document.
    - docs/design/theorem-registry.md: complete document.
    - docs/design/trust-model.md: Trust categories; Explicitly untrusted by default; Verification modes; Threats.
    - docs/governance/authorship-and-credit.md: complete document.
    - docs/governance/review-policy.md: complete document.
    - docs/governance/rfc-process.md: complete document.
    - docs/spec/artifact.md: complete document.
    - docs/spec/canonicalization.md: complete document.
    - docs/spec/provenance.md: complete document.
    - docs/spec/theorem-lock.md: complete document.
    - docs/spec/versioning.md: complete document.
    - docs/exec-plans/active/0001-foundation-bootstrap.md: Observable exit condition; Milestone A — Ratify the constitution (SQ-0001); Milestone C — Settle an encoding prototype (SQ-0005–SQ-0007); Milestone E — Artifact and reference backend (SQ-0010–SQ-0012); Milestone G — Trust report, CI, and first artifact (SQ-0017–SQ-0020); Surprises & Discoveries; Decision Log.
    - work/backlog.yaml: decision_register; tasks[*].decision_prerequisites.
    - work/README.md: Scheduling.
    - scripts/check_repository.py: ALLOWED_DECISION_STATUS; document_status; decision_owner_state_valid; prerequisites_satisfied; check_readiness_regression_fixtures, including the complete supported-status by active/completed-owner matrix and invalid `Accepetd` cases for IN_PROGRESS and DONE; check_backlog, including numbered-RFC coverage, unique owner/path, owner write authority, Draft/Accepted decision status, Accepted-only prerequisites, Draft-owner lifecycle and owner-handoff consistency, READY/active eligibility, and decision-prerequisite checks; check_status, including status.in_progress and blocked_count consistency with backlog state.
    - scripts/list_work.py: main, which consumes check_backlog's shared RFC-aware ready and active sets and renders Dependency-ready tasks separately from Active tasks.
    - work/contracts/SQ-0001.yaml: objective; assumptions; steps; reviewers; acceptance.
    - work/contracts/SQ-0006.yaml: objective; steps; acceptance.
    - work/contracts/SQ-0010.yaml: objective; steps; tests; acceptance.
    - work/contracts/SQ-0011.yaml: objective; steps; acceptance.
    - work/contracts/SQ-0020.yaml: objective; steps; acceptance.
    - work/contracts/SQ-0027.yaml: objective; dependencies; allowed_paths; steps; acceptance.
    - LICENSE: complete MIT text.
    - CITATION.cff: complete file.

    PRIMARY/OFFICIAL EXTERNAL, exact locators:
    - RFC 8949 / STD 94, sections 4.1, 4.2, 4.2.1-4.2.3, 5.3-5.6.1, 9.3:
      https://www.rfc-editor.org/rfc/rfc8949.html
    - RFC 8610, sections 1, 2-4, Appendix B, Appendix D, plus current errata:
      https://www.rfc-editor.org/rfc/rfc8610.html
      https://www.rfc-editor.org/errata/rfc8610
    - RFC 9165, sections 1-4:
      https://www.rfc-editor.org/rfc/rfc9165.html
    - RFC 9682, sections 1-3 and Appendix A:
      https://www.rfc-editor.org/rfc/rfc9682.html
    - RFC 9741, sections 1-7:
      https://www.rfc-editor.org/rfc/rfc9741.html
    - IETF CBOR WG document index, active/expired status as of retrieval date:
      https://datatracker.ietf.org/group/cbor/documents/
    - draft-ietf-cbor-serialization-08, status page and sections 1-5
      (Work in Progress, not a standard):
      https://datatracker.ietf.org/doc/draft-ietf-cbor-serialization/
    - draft-ietf-cbor-cddl-modules-06, status page and sections 1-3
      (Work in Progress, not a standard):
      https://datatracker.ietf.org/doc/draft-ietf-cbor-cddl-modules/
    - Unicode Standard 17.0.0, Core Specification section 3.11; UAX #15 revision 57:
      https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-3/#G49537
      https://www.unicode.org/reports/tr15/tr15-57.html
    - Lean Language Reference, Elaboration and Compilation section 2.3; Validating a Lean Proof; Axioms; Lake:
      https://lean-lang.org/doc/reference/4.32.1/Elaboration-and-Compilation/#the-kernel
      https://lean-lang.org/doc/reference/4.32.1/ValidatingProofs/
      https://lean-lang.org/doc/reference/4.32.1/Axioms/
      https://lean-lang.org/doc/reference/4.32.1/Build-Tools-and-Distribution/Lake/
    - Lean 4.32.1 release note (soundness fix; no pin recommendation inferred):
      https://lean-lang.org/doc/reference/latest/releases/v4.32.1/
    - Lean API, Environment and Declaration:
      https://lean-lang.org/doc/api/Lean/Environment.html
      https://lean-lang.org/doc/api/Lean/Declaration.html
    - Mathlib Markov-kernel definitions and official contribution guidance:
      https://leanprover-community.github.io/mathlib4_docs/Mathlib/Probability/Kernel/Defs.html
      https://leanprover-community.github.io/contribute/index.html
      https://leanprover-community.github.io/contribute/how-to-contribute.html
    - Cargo Workspaces; manifest name field; registry-index name restrictions; unsafe-code lint and lint levels:
      https://doc.rust-lang.org/cargo/reference/workspaces.html
      https://doc.rust-lang.org/cargo/reference/manifest.html#the-name-field
      https://doc.rust-lang.org/cargo/reference/registry-index.html#name-restrictions
      https://doc.rust-lang.org/rustc/lints/listing/allowed-by-default.html#unsafe-code
      https://doc.rust-lang.org/rustc/lints/levels.html#forbid
    - Python packaging name normalization, name retention, and distribution/import distinction:
      https://packaging.python.org/en/latest/specifications/name-normalization/
      https://docs.pypi.org/project-management/name-retention/
      https://packaging.python.org/en/latest/discussions/distribution-package-vs-import-package/
    - R Writing R Extensions, section 1.1.1, Package field:
      https://cran.r-project.org/doc/manuals/r-release/R-exts.html#The-DESCRIPTION-file
    - Julia Pkg Project.toml name/UUID fields; creating/registering packages; General Registry AutoMerge rules:
      https://pkgdocs.julialang.org/v1/toml-files/#The-name-field
      https://pkgdocs.julialang.org/dev/creating-packages/#Package-naming-guidelines
      https://juliaregistries.github.io/RegistryCI.jl/stable/guidelines/#New-packages
      https://juliaregistries.github.io/Registrator.jl/stable/webui/#Before-Registering
    - GitHub Username Policy and username-change limitations:
      https://docs.github.com/en/site-policy/other-site-policies/github-username-policy
      https://docs.github.com/en/account-and-profile/concepts/username-changes
    - EUIPO search-availability FAQ; USPTO comprehensive-clearance guidance:
      https://www.euipo.europa.eu/the-office/help-centre/tm/faq-search-availability
      https://www.uspto.gov/trademarks/search/comprehensive-clearance-search-similar-trademarks
    - OSI MIT license; SPDX MIT identifier:
      https://opensource.org/license/mit
      https://spdx.org/licenses/MIT.html
    - Citation File Format schema guide 1.2.0:
      https://github.com/citation-file-format/citation-file-format/blob/main/schema-guide.md
    - SWHID specification 1.2, clauses 4-5 (nearby identifier model, not adopted here):
      https://www.swhid.org/specification/v1.2/4.Syntax/
      https://www.swhid.org/specification/v1.2/5.Core_identifiers/

    MANAGER-REPORTED EXACT OFFICIAL ENDPOINT RESPONSES, 2026-08-03:
    - https://pypi.org/pypi/statqed/json -> HTTP 404.
    - https://cran.r-project.org/web/packages/statqed/index.html -> HTTP 404.
    - https://raw.githubusercontent.com/JuliaRegistries/General/master/S/StatQED/Package.toml -> HTTP 404.
    - https://crates.io/api/v1/crates/statqed -> HTTP 403 data-access denial; inconclusive.
  persistent_id: |-
    RFC 8949: https://doi.org/10.17487/RFC8949
    RFC 8610: https://doi.org/10.17487/RFC8610
    RFC 9165: https://doi.org/10.17487/RFC9165
    RFC 9682: https://doi.org/10.17487/RFC9682
    RFC 9741: https://doi.org/10.17487/RFC9741
    Repository baseline: git:2ad5c72f7adc402024152d6fa4af9c86cdf9b588
    Frozen candidate surface manifest: sha256:5793ce0b5c7e819090c74480e93e7167f6821897b96567c8b6c737bc8fa1ff96
controlled_statement: "Against baseline git:2ad5c72f7adc402024152d6fa4af9c86cdf9b588, the frozen SQ-0001 candidate constitutional surface is the 77 changed files selected by the stated exclusions and bound by sorted sha256sum-lines digest sha256:5793ce0b5c7e819090c74480e93e7167f6821897b96567c8b6c737bc8fa1ff96. Source review supports StatQED as the project/family name and a foundation-phase monorepo; Lean 4 with a pinned Mathlib revision as the initial normative proof backend; Rust as a non-semantic reference operational backend; MIT plus CFF/source-lineage attribution; a versioned theorem-registry direction separating canonical-record integrity from verifier-selected authorization; and a shared RFC-aware scheduler in which READY and active work are distinct. Registered RFC status is limited to Draft or Accepted, decision prerequisites may require only Accepted, and a Draft RFC with a DONE or SUPERSEDED owner fails. Rejected, Withdrawn, Superseded, and successor-disposition semantics remain unavailable until reviewed non-cyclic successor relations and negative tests exist. Every verification-result record has exactly one mode; a document may display several separately identified results but never unions their evidence or emits an overall stronger status. RFC-0001 through RFC-0009 retain their stated Draft or deferred boundaries, not Accepted implementation status. RFC-0006 is owned by detailed task SQ-0027, while SQ-0006 and SQ-0011 remain strictly data-free; SQ-0020 cannot complete before accepting RFC-0007 and RFC-0009. Changing or redacting committed or normative provenance always creates a new normative artifact identity and, where applicable, a new verification-result identity. Inert non-normative report-only redaction preserves normative artifact identity but changes the physical bundle bytes/file commitment and records the report/disclosure transformation. An unresolved leaf is limited to an external or uncommitted reference or a newly identified normative object/result and cannot preserve changed committed bytes. Canonical encoding, public evidence types, artifact byte-to-term binding, the core statistical ontology, theorem normalization, bounded environment closure and authorization policy, logical-data digests, compatibility implementation, the exact artifact-envelope/offline/privacy/security mechanism, and community-governance authority remain deferred to their named RFC/task gates. ADR-0011 fixes only a data-free structural toy slice with probability context not_applicable and a definitionally trivial, test-only `True` record; it freezes no canonical bytes, provides no public-theorem non-vacuity witness, and proves no real statistical guarantee. Package, organization, domain, and trademark availability remains unresolved beyond the recorded point-in-time observations, and no toolchain or deferred implementation behavior is validated here."
hypotheses:
  - name: "H01_project_family_name_is_StatQED"
    class: "source_explicit"
    source_anchor: "docs/design/naming-and-packages.md, opening sentence; README.md, Name"
    notes: "A governed project choice, not evidence of exclusivity or legal clearance."
  - name: "H02_R_name_statqed_is_syntactically_admissible"
    class: "source_explicit"
    source_anchor: "R Writing R Extensions section 1.1.1, Package field"
    notes: "Lowercase ASCII letters satisfy the documented Package-field syntax. Syntax is not CRAN acceptance."
  - name: "H03_Python_distribution_name_statqed_is_syntactically_admissible"
    class: "source_explicit"
    source_anchor: "Python Packaging User Guide, Names and normalization, Name format"
    notes: "The normalized distribution name is `statqed`; distribution and import names remain distinct concepts."
  - name: "H04_Julia_name_StatQED_is_syntactically_admissible"
    class: "source_explicit"
    source_anchor: "Julia Pkg Project.toml name field; RegistryCI AutoMerge, New packages items 1-4"
    notes: "It is a Julia identifier and fits the capitalization/length rules. Registration also requires a UUID, package-root/repository conventions, license, install/load checks, and name-similarity checks."
  - name: "H05_Rust_names_statqed_and_statqed_core_are_syntactically_admissible"
    class: "source_explicit"
    source_anchor: "Cargo manifest name field; Registry Index, Name restrictions"
    notes: "Cargo/crates.io syntax permits ASCII alphanumeric, hyphen, and underscore subject to registry restrictions."
  - name: "H06_PyPI_exact_endpoint_had_no_project_record"
    class: "source_explicit"
    source_anchor: "Manager-reported GET https://pypi.org/pypi/statqed/json, 2026-08-03 -> HTTP 404"
    notes: "Point-in-time endpoint fact only. PyPI may preemptively reserve names and applies retention, dispute, IP, and anti-squatting rules."
  - name: "H07_CRAN_exact_current_package_endpoint_had_no_record"
    class: "source_explicit"
    source_anchor: "Manager-reported GET https://cran.r-project.org/web/packages/statqed/index.html, 2026-08-03 -> HTTP 404"
    notes: "Does not cover archived packages, incoming submissions, policy review, or future claims."
  - name: "H08_Julia_General_exact_registry_path_had_no_record"
    class: "source_explicit"
    source_anchor: "Manager-reported GET Julia General raw S/StatQED/Package.toml, 2026-08-03 -> HTTP 404"
    notes: "Does not establish that General's current similarity and registration checks will accept the name."
  - name: "H09_crates_io_name_availability"
    class: "strengthening_unjustified"
    source_anchor: "Manager-reported GET https://crates.io/api/v1/crates/statqed, 2026-08-03 -> HTTP 403"
    notes: "The response is a data-access denial, not a missing-record result. Availability is unresolved."
  - name: "H10_exact_404_means_name_is_reservable_and_future_available"
    class: "strengthening_unjustified"
    source_anchor: "PyPI Name Retention; Julia RegistryCI AutoMerge rules; GitHub Username Policy"
    notes: "A missing public record neither reserves a name nor guarantees future publication. This strengthening must not appear in an Accepted naming decision."
  - name: "H11_GitHub_statqed_account_or_organization_name_is_available"
    class: "strengthening_unjustified"
    source_anchor: "GitHub Username Policy, What if the username I want is already taken?; Username changes"
    notes: "GitHub says not all activity is public and a 404 can follow a rename. No authoritative availability/reservation action was recorded."
  - name: "H12_StatQED_has_trademark_clearance"
    class: "strengthening_unjustified"
    source_anchor: "EUIPO Search availability FAQ; USPTO Comprehensive clearance search"
    notes: "EUIPO says even its similarity report is non-exhaustive; USPTO says comprehensive clearance includes federal, state, international, domain, and common-law searches. Exact-name web search is not legal clearance."
  - name: "H13_cli_name_and_dot_statqed_extension_are_exclusive"
    class: "not_applicable"
    source_anchor: "docs/design/naming-and-packages.md"
    notes: "These are project conventions. No exclusive global CLI-name or filename-extension registry was identified. A future media-type registration would be a separate decision."
  - name: "H14_foundation_phase_uses_one_monorepo"
    class: "source_explicit"
    source_anchor: "ADR-0001, Decision; ARCHITECTURE.md, Repository modules"
    notes: "The decision is bounded to the foundation phase and expressly allows later splits."
  - name: "H15_monorepo_is_proven_optimal_for_all_ecosystems"
    class: "strengthening_unjustified"
    source_anchor: "ADR-0001, Alternatives and Validation and evidence; official package-tool documents listed in source.locator"
    notes: "Atomic change and shared-fixture benefits are project judgments. Official tooling establishes feasibility constraints, not global optimality."
  - name: "H16_Cargo_workspace_can_manage_multiple_Rust_packages_together"
    class: "source_explicit"
    source_anchor: "Cargo Book, Workspaces"
    notes: "Cargo documents shared commands, lockfile, target directory, and root-level configuration for workspace members."
  - name: "H17_Lake_can_pin_transitive_dependencies"
    class: "source_explicit"
    source_anchor: "Lean Language Reference, Lake, package configuration and manifest"
    notes: "A manifest plus package configuration specifies a unique transitive set and should be committed. SQ-0001 does not choose or validate a concrete set."
  - name: "H18_R_and_Python_package_sources_may_be_built_from_monorepo_subdirectories"
    class: "source_implicit_justified"
    source_anchor: "R Writing R Extensions section 1.1; Python packaging project/distribution specifications"
    notes: "Both define package-local roots and artifacts without requiring a one-package repository. Actual publication commands remain SQ-0013/SQ-0014 obligations."
  - name: "H19_General_will_register_StatQED_jl_directly_from_frontends_julia"
    class: "strengthening_unjustified"
    source_anchor: "RegistryCI AutoMerge, New packages item 5; Registrator Web UI, Validating Project.toml"
    notes: "The standard workflow expects a repository URL ending `/StatQED.jl.git` and Project.toml at repository root. The monorepo path therefore needs a tested publication/mirror/split strategy or an explicit non-General decision."
  - name: "H20_Lean_4_is_the_initial_normative_proof_backend"
    class: "source_explicit"
    source_anchor: "ADR-0002, Decision; CHARTER.md, Non-goals; ARCHITECTURE.md, 1. Statistical semantics"
    notes: "A project architecture choice; official Lean/Mathlib sources show relevant capabilities but do not mandate this choice."
  - name: "H21_Lean_kernel_checks_declarations_before_environment_admission"
    class: "source_explicit"
    source_anchor: "Lean Reference, Elaboration and Compilation section 2.3; Lean.Environment API, Kernel.Environment"
    notes: "Supports kernel-mode language only for the exact elaborated statement, imports, and axioms. It does not establish source fidelity or external assumptions."
  - name: "H22_Mathlib_contains_Markov_kernel_infrastructure"
    class: "source_explicit"
    source_anchor: "Mathlib.Probability.Kernel.Defs, Markov Kernels and Main definitions"
    notes: "`Kernel` and `IsMarkovKernel` exist with measurable-space obligations. This is a concept-mapping fact, not coverage of StatQED's full statistical roadmap."
  - name: "H23_Mathlib_is_already_sufficient_for_all_planned_probability_and_statistics"
    class: "strengthening_unjustified"
    source_anchor: "Mathlib kernel documentation; Mathlib contribution guidance, What to contribute"
    notes: "A single relevant module cannot establish complete coverage. Missing abstractions and exact version compatibility must be researched and prototyped later."
  - name: "H24_every_general_lemma_will_be_accepted_upstream"
    class: "strengthening_unjustified"
    source_anchor: "Mathlib contribution guidance, What to contribute"
    notes: "Mathlib explicitly says its remit is not all mathematics and suggests standalone dependent repositories in some cases. Preserve `when feasible`; do not promise acceptance."
  - name: "H25_pinning_Lean_and_Mathlib_is_sufficient_for_soundness_and_reproducibility"
    class: "formalization_obligation"
    source_anchor: "Lean 4.32.1 release note; Lake documentation; Validating a Lean Proof"
    notes: "Pinning is necessary evidence, not sufficient. The 4.32.1 soundness-fix note shows version-specific risk; clean builds, axiom reports, source locks, and trust-mode reporting remain required. No version is selected here."
  - name: "H26_Rust_is_reference_operational_backend_not_semantic_authority"
    class: "source_explicit"
    source_anchor: "ADR-0003, Decision and Constraints and consequences; ARCHITECTURE.md, 3. Canonicalization backend"
    notes: "The normative spec and Lean model remain authorities. Rust's role is reference behavior under the named verification mode."
  - name: "H27_forbid_unsafe_code_eliminates_all_unsafe_from_operational_TCB"
    class: "strengthening_unjustified"
    source_anchor: "rustc unsafe-code lint; rustc lint levels, forbid"
    notes: "The lint constrains occurrences it diagnoses in a compiled crate and lint levels can be capped; it does not prove dependencies, compiler, runtime, FFI, or platform safe."
  - name: "H28_Rust_backend_is_deterministic_offline_bounded_and_panic_free"
    class: "formalization_obligation"
    source_anchor: "ADR-0003, Constraints and consequences; Cargo and rustc documentation"
    notes: "These are acceptance properties to establish with design, dependency review, resource limits, hostile tests, and conformance evidence. Rust does not confer them automatically."
  - name: "H29_shared_Rust_canonicalization_and_independent_prototypes_are_compatible"
    class: "source_explicit"
    source_anchor: "ADR-0003, Constraints and consequences; ADR-0004, Validation and evidence; Plan 0001, Milestone C — Settle an encoding prototype (SQ-0005–SQ-0007) and Milestone F — Frontend skeletons (SQ-0013–SQ-0016)"
    notes: "A production shared backend can coexist with two independent prototype/oracle implementations. The independent path must not merely call the same encoder."
  - name: "H30_RFC_8949_defines_a_deterministic_encoding_base"
    class: "source_explicit"
    source_anchor: "RFC 8949 sections 4.2-4.2.3"
    notes: "Core deterministic requirements include preferred serialization, definite lengths, and bytewise lexicographic ordering of deterministically encoded map keys; length-first ordering is a distinct legacy-compatible variant."
  - name: "H31_saying_deterministic_CBOR_uniquely_fixes_StatQED_bytes"
    class: "strengthening_unjustified"
    source_anchor: "RFC 8949 sections 4.2.2, 4.2.3, 5.5, and 5.6"
    notes: "RFC 8949 requires application choices for tags, integer/float interchange, large numbers, NaNs/signed zero, map-key equivalence, and other semantics. The exact profile remains RFC-0001/SQ-0005 work."
  - name: "H32_duplicate_map_keys_may_be_rejected"
    class: "source_explicit"
    source_anchor: "RFC 8949 sections 3.1 and 5.6"
    notes: "A map with duplicates can be well formed but invalid; a protocol must define handling and may require decoder failure. StatQED's rejection direction is source-supported."
  - name: "H33_Unicode_normalization_policy_is_fixed_by_CBOR"
    class: "strengthening_unjustified"
    source_anchor: "RFC 8949 text-string rules; Unicode 17.0 section 3.11; UAX #15 revision 57"
    notes: "Valid UTF-8 alone does not collapse canonically equivalent sequences. StatQED must choose exact-source semantics or a named normalization form/version and define reject-versus-normalize behavior."
  - name: "H34_CDDL_describes_and_can_check_data_structure"
    class: "source_explicit"
    source_anchor: "RFC 8610 section 1 goals G1-G6"
    notes: "CDDL is a data-structure/schema notation for CBOR and JSON. It does not by itself define canonical byte serialization or all semantic invariants."
  - name: "H35_CDDL_base_is_currently_RFC_8610_alone"
    class: "candidate_for_weakening"
    source_anchor: "RFC 9682 section 1; RFC 9165; RFC 9741; RFC 8610 errata page"
    notes: "Any frozen CDDL profile should name RFC 8610 as updated by RFC 9682 and list permitted control-operator RFCs and errata policy. Saying only `CDDL` is underspecified."
  - name: "H36_CDDL_module_structure_is_a_final_standard"
    class: "strengthening_unjustified"
    source_anchor: "IETF CBOR WG index; draft-ietf-cbor-cddl-modules-06 status"
    notes: "As of retrieval it was an active WG Internet-Draft, not an RFC. `CDDL modules` in the plan must mean ordinary versioned schema files unless adoption of the draft syntax is explicitly experimental and pinned."
  - name: "H37_RFC_8949_is_the_only_relevant_current_determinism_variant"
    class: "candidate_for_weakening"
    source_anchor: "IETF CBOR WG index; draft-ietf-cbor-serialization-08 sections 1-5"
    notes: "RFC 8949 remains the authoritative standard, but a WG-last-call draft dated 2026-07-29 proposes new preferred-plus and deterministic serializations. It is a nearby Work-in-Progress variant to monitor, not normative evidence to adopt now."
  - name: "H38_two_independent_implementations_and_golden_vectors_are_required_before_encoding_acceptance"
    class: "strengthening_justified"
    source_anchor: "ADR-0004, Validation and evidence; docs/spec/canonicalization.md, complete document; RFC 8949 sections 4.2 and 5.2"
    notes: "This project-strengthened gate addresses allowed implementation variation and cross-library differentials. It strengthens the RFC baseline for a hash-critical protocol without changing a sourced theorem."
  - name: "H39_repository_MIT_text_matches_the_standard_MIT_license"
    class: "source_explicit"
    source_anchor: "LICENSE; OSI MIT License; SPDX MIT"
    notes: "The grant, notice-retention condition, and warranty disclaimer match the standard MIT form with repository year/holder filled in. This is not a legal opinion about ownership of every future contribution."
  - name: "H40_MIT_automatically_covers_inbound_third_party_material"
    class: "strengthening_unjustified"
    source_anchor: "LICENSE; docs/governance/authorship-and-credit.md"
    notes: "StatQED can license only material for which contributors have adequate rights. Imported code, schemas, RFC code components, figures, data, and text retain their own licenses/conditions."
  - name: "H41_CITATION_cff_fields_follow_schema_1_2_0_structure"
    class: "source_explicit"
    source_anchor: "CITATION.cff; CFF schema guide, required keys, authors, license, repository-code, type, and version"
    notes: "The file contains the required keys and uses permitted person/entity author forms and SPDX `MIT`. No validator was run, so this is a source inspection, not a tooling-validation claim."
  - name: "H42_one_software_citation_is_sufficient_for_method_artifacts"
    class: "strengthening_unjustified"
    source_anchor: "CFF schema guide, Referencing other work; docs/governance/authorship-and-credit.md"
    notes: "Artifacts and theorem records must also cite original mathematics, data, software, formalization, and method packs as applicable. MIT notice retention and scholarly attribution are separate obligations."
  - name: "H43_public_theorem_identity_separates_stable_ID_statement_and_proof_body"
    class: "source_explicit"
    source_anchor: "ADR-0007, Candidate decision and Consequences; docs/design/theorem-registry.md, complete document; Lean.Declaration and Lean.Environment APIs"
    notes: "Lean stores a unique declaration Name and ConstantInfo in one environment, with signature/type and theorem value. Long-term StatQED identity is a governed layer above that environment-local name."
  - name: "H44_pretty_printed_Lean_statement_is_a_canonical_statement_hash_input"
    class: "strengthening_unjustified"
    source_anchor: "Lean Reference, Interacting with Lean, #print; Reading Proof States printing limits"
    notes: "Printing is a presentation operation and can hide/truncate terms under options. SQ-0007 must specify a versioned normalization over exact core data, universes, binder/type information, referenced definitions, and environment locks."
  - name: "H45_statement_hash_algorithm_preserves_semantic_identity"
    class: "formalization_obligation"
    source_anchor: "docs/spec/theorem-lock.md; docs/design/theorem-registry.md"
    notes: "No algorithm or prototype exists at SQ-0001. It needs collision domain, normalization, dependency context, test vectors, and change/compatibility policy before a lock can be frozen."
  - name: "H46_same_Lean_name_permits_theorem_substitution"
    class: "strengthening_unjustified"
    source_anchor: "Lean.Environment API; docs/spec/theorem-lock.md, complete document"
    notes: "Names are unique only within an environment. Artifacts require exact locks; replacement needs identical accepted statement identity or a registered implication/equivalence path in the needed direction."
  - name: "H47_content_identifier_and_citation_identifier_are_interchangeable"
    class: "strengthening_unjustified"
    source_anchor: "SWHID specification clauses 4-5; CFF schema guide; docs/design/theorem-registry.md"
    notes: "An intrinsic content hash establishes object identity/integrity under its algorithm; it does not supply authorship, source lineage, semantic compatibility, or a maintained citation record."
  - name: "H48_first_foundation_slice_is_a_fixed_toy_structural_artifact"
    class: "source_explicit"
    source_anchor: "ADR-0011, Decision and Verification result and nonclaims; Plan 0001, Observable exit condition and Milestone G — Trust report, CI, and first artifact (SQ-0017–SQ-0020)"
    notes: "The fixed fixture kind is `foundation_structural`: it is data-free, has probability context `not_applicable`, and uses a separate definitionally trivial, test-only `True` record. `True` is not a public theorem or non-vacuity witness. Later tasks own exact schemas, bytes, locks, graph, envelope, and composition; these are planned acceptance conditions, not current behavior."
  - name: "H49_first_foundation_slice_contains_a_real_statistical_method_or_guarantee"
    class: "not_applicable"
    source_anchor: "ADR-0011, Decision and Verification result and nonclaims; Plan 0001, Observable exit condition; SQ-0001 contract assumptions and acceptance"
    notes: "Expressly excluded. No estimand, assignment/sampling law, inferential theorem, numerical certificate, or scientific claim may be inferred from the toy slice."
  - name: "H50_SQ_0001_validates_toolchains_or_implementations"
    class: "not_applicable"
    source_anchor: "SQ-0001 contract assumptions; Plan 0001 dependency graph"
    notes: "SQ-0002 through SQ-0019 own toolchain, encoding, schema, registry, frontend, and artifact evidence. This audit makes no build, runtime, publication, conformance, or verification claim."
  - name: "H51_candidate_constitutional_surface_manifest"
    class: "source_explicit"
    source_anchor: "Git working tree relative to baseline 2ad5c72f7adc402024152d6fa4af9c86cdf9b588; source.work manifest recipe"
    notes: "The frozen reviewed candidate contains 77 changed paths after the stated exclusions. Sorting their complete sha256sum lines bytewise before hashing gives sha256:5793ce0b5c7e819090c74480e93e7167f6821897b96567c8b6c737bc8fa1ff96. The immutable baseline commit remains separate provenance."
  - name: "H52_candidate_manifest_digest_proves_semantic_correctness_or_review_completion"
    class: "strengthening_unjustified"
    source_anchor: "docs/governance/review-policy.md, complete document; source.work manifest recipe"
    notes: "The digest binds exact bytes only under the stated manifest/algorithm assumptions. It does not prove semantic equality, scientific validity, review independence, reviewer approval, or implementation behavior."
  - name: "H53_every_numbered_RFC_has_one_registered_owner_and_path"
    class: "source_explicit"
    source_anchor: "work/backlog.yaml, decision_register; work/README.md, Scheduling; scripts/check_repository.py, check_backlog"
    notes: "The frozen candidate register covers RFC-0001 through RFC-0009 and the guardrail checks complete numbered-RFC coverage, unique IDs/paths, Draft/Accepted status parsing, and one non-complete owner whose detailed contract can edit the decision path. This is scheduling and write-authority evidence."
  - name: "H54_decision_register_entry_confers_Accepted_status_or_semantic_authority"
    class: "strengthening_unjustified"
    source_anchor: "work/README.md, Scheduling; rfcs/0001-deterministic-encoding.md through rfcs/0009-community-governance-structure.md, Status and Decision"
    notes: "Registration prevents an ownerless or silently assumed decision. It neither changes a document's Draft status nor replaces the required evidence and independent review."
  - name: "H55_downstream_readiness_respects_decision_prerequisites"
    class: "source_explicit"
    source_anchor: "work/README.md, Scheduling; work/backlog.yaml, tasks[*].decision_prerequisites; scripts/check_repository.py, prerequisites_satisfied, check_readiness_regression_fixtures, and check_backlog; scripts/list_work.py, main"
    notes: "The shared calculation excludes a downstream task from both READY and active eligibility until each named decision document reports `Accepted`; no other prerequisite value is permitted. An owner may resolve its own RFC without a circular self-prerequisite; this does not authorize it to bypass review."
  - name: "H56_universal_statistical_ontology_or_randomness_type_is_frozen"
    class: "strengthening_unjustified"
    source_anchor: "RFC-0004, Decision boundary, Proposed semantics, and Decision"
    notes: "RFC-0004 is Deferred. Only the required distinctions and validation obligations are constitutional; SQ-0008 or narrower successors must obtain source, statistical, formal, interoperability, and adversarial evidence before a public type freezes."
  - name: "H57_theorem_registry_integrity_is_separate_from_authorization"
    class: "source_explicit"
    source_anchor: "ARCHITECTURE.md, 8. Theorem registry; ADR-0007, Candidate decision; RFC-0005, Terminology and source background and Proposed semantics; docs/design/theorem-registry.md, complete document"
    notes: "A canonical registry record/digest binds content under named algorithms. Verification policy independently selects an accepted registry root/snapshot, policy, and historical/revocation rules; integrity alone confers no governed ID, maturity, review, or compatibility authority."
  - name: "H58_artifact_supplied_consistent_registry_root_confers_governed_authority"
    class: "strengthening_unjustified"
    source_anchor: "RFC-0005, Examples and nonexamples, Proposed semantics item 7, and Validation plan"
    notes: "An artifact-supplied replacement registry remains untrusted unless it resolves against the verifier-selected authorization root/policy. Whole-registry replacement, forged governance metadata, root mismatch, historical/revoked roots, bounded-closure failures, and revocation are required security/negative cases."
  - name: "H59_canonical_logical_data_or_digest_is_frozen_by_the_toy_slice"
    class: "strengthening_unjustified"
    source_anchor: "RFC-0006, Proposed semantics and Decision; ADR-0011, Decision"
    notes: "RFC-0006 is Deferred, and ADR-0011 deliberately omits data/table content. No raw-file checksum or future canonical IR digest may be silently promoted to a logical-data binding."
  - name: "H60_cross_component_compatibility_is_established_by_readability_or_semver"
    class: "strengthening_unjustified"
    source_anchor: "RFC-0007, Terminology and source background, Proposed semantics, and Decision"
    notes: "No compatibility promise beyond exact current locks is Accepted. Readability, byte identity, semantic equivalence, directional implication, loss, and new result identity remain distinct."
  - name: "H61_artifact_envelope_offline_privacy_and_security_behavior_is_frozen"
    class: "strengthening_unjustified"
    source_anchor: "RFC-0008, Decision boundary, Proposed semantics, Trust, security, privacy, and accessibility, and Decision; docs/spec/artifact.md, complete document"
    notes: "No `.statqed` container is Accepted. SQ-0010 must select and test manifest authority, paths, entry types, compression, budgets, inactive reports, local-only resolution, provenance allowlisting, privacy/linkability disclosure, redaction identity, deterministic errors, and hostile cases."
  - name: "H62_planned_community_bodies_have_current_governance_authority"
    class: "strengthening_unjustified"
    source_anchor: "GOVERNANCE.md, Current authority and Planned bodies; RFC-0009, Proposed semantics and Decision"
    notes: "RFC-0009 is Deferred. The planned bodies have no present membership or voting authority; the current owner cannot waive mandatory independent scientific/formal evidence."
  - name: "H63_source_curator_candidate_review_completes_other_required_reviews"
    class: "strengthening_unjustified"
    source_anchor: "SQ-0001 contract reviewers and acceptance; docs/governance/review-policy.md, complete document"
    notes: "This Candidate disposition covers only primary-source fidelity, exact locators, assumption classification, attribution, and the candidate manifest. Statistical, formal, interoperability, adversarial, security/trust, privacy, and integration dispositions remain independent records."
  - name: "H64_test_only_True_record_is_a_public_theorem_or_nonvacuity_witness"
    class: "strengthening_unjustified"
    source_anchor: "ADR-0011, Decision and Verification result and nonclaims"
    notes: "`True` is definitionally trivial and test-only. It cannot satisfy a public-theorem non-vacuity gate. A bytes-for-`False` mapped-to-`True` mutation tests only the exact byte-to-proposition binding path and does not establish general decoder, registry, or formalization capability."
  - name: "H65_work_listing_and_repository_check_share_RFC_aware_readiness"
    class: "source_explicit"
    source_anchor: "scripts/check_repository.py, prerequisites_satisfied and check_backlog; scripts/list_work.py, import of check_backlog and main; work/README.md, Scheduling"
    notes: "`list_work.py` consumes the guardrail's computed ready/active sets instead of reimplementing dependency-only readiness. It renders unclaimed `READY` tasks separately from `IN_PROGRESS`/`IN_REVIEW` active tasks; active eligibility is not a second ready queue."
  - name: "H66_unresolved_RFC_owner_may_be_DONE_or_SUPERSEDED_without_handoff"
    class: "strengthening_unjustified"
    source_anchor: "work/README.md, Scheduling; scripts/check_repository.py, ALLOWED_DECISION_STATUS, document_status, decision_owner_state_valid, check_readiness_regression_fixtures, and check_backlog Draft-owner check; Plan 0001, Surprises & Discoveries and Decision Log"
    notes: "The only registered status other than `Accepted` is `Draft`, and a Draft RFC's owner cannot be DONE or SUPERSEDED. The pure lifecycle helper is exercised over both supported decision statuses crossed with every active and completed owner state; invalid `Accepetd` fixtures for both IN_PROGRESS and DONE make removal of the status allowlist detectable. Rejection, withdrawal, supersession, and successor handoff are not approved variants: they remain invalid until a reviewed non-cyclic successor relation and negative tests are implemented."
  - name: "H67_RFC_0006_is_owned_by_SQ_0027_and_foundation_tasks_are_data_free"
    class: "source_explicit"
    source_anchor: "work/backlog.yaml, decision_register RFC-0006 and tasks SQ-0006, SQ-0011, SQ-0027; RFC-0006, Task, Omit data from the foundation fixture, Formal and implementation consequences, and Decision; work/contracts/SQ-0006.yaml, steps and acceptance; work/contracts/SQ-0011.yaml, steps and acceptance; work/contracts/SQ-0027.yaml, objective and acceptance"
    notes: "Detailed task SQ-0027 owns RFC-0006 and the first normative real-data schema, logical digest, witness, and backend path. SQ-0006 and SQ-0011 may handle only the data-free foundation fixture and its non-data content digests."
  - name: "H68_SQ_0020_may_complete_with_RFC_0007_or_RFC_0009_unresolved"
    class: "strengthening_unjustified"
    source_anchor: "RFC-0007, Decision; RFC-0009, Task, Proposed semantics, and Decision; work/contracts/SQ-0020.yaml, steps and acceptance; Plan 0001, Decision Log"
    notes: "SQ-0020 owns both Draft RFCs and must Accept both before it completes. Completing or superseding that owner while either decision remains Draft would violate the frozen completion gate; no successor-status relation is available as an alternative."
  - name: "H69_provenance_redaction_identity_depends_on_normative_status"
    class: "source_explicit"
    source_anchor: "RFC-0008, Proposed semantics; docs/spec/provenance.md, complete document; work/contracts/SQ-0010.yaml, tests and acceptance"
    notes: "Changing or redacting committed or normative provenance always creates a new normative artifact identity and, where applicable, a new verification-result identity. Redacting only an inert non-normative report preserves normative artifact identity, changes the physical bundle bytes/file commitment, and records the report/disclosure transformation."
  - name: "H70_unresolved_leaf_preserves_identity_after_committed_bytes_change"
    class: "strengthening_unjustified"
    source_anchor: "RFC-0008, Proposed semantics; docs/spec/provenance.md, complete document; work/contracts/SQ-0010.yaml, tests"
    notes: "An unresolved leaf is permitted only for an external or uncommitted reference or inside a newly identified normative object/result. It never preserves the old identity or dependency closure after committed bytes or normative provenance change."
  - name: "H71_document_may_union_separate_verification_result_evidence"
    class: "strengthening_unjustified"
    source_anchor: "ARCHITECTURE.md, Trust modes; docs/design/trust-model.md, Verification modes; RFC-0003, Proposed semantics item 1; ADR-0011, Review"
    notes: "Each verification-result record names exactly one mode. A document may render multiple separately identified results but cannot union their evidence or emit an overall status stronger than any supported result; structural success cannot inherit a kernel label."
  - name: "H72_decision_status_vocabulary_is_allowlisted"
    class: "source_explicit"
    source_anchor: "scripts/check_repository.py, ALLOWED_DECISION_STATUS, document_status, decision_owner_state_valid, check_readiness_regression_fixtures, and decision-prerequisite validation; work/README.md, Scheduling; Plan 0001, Surprises & Discoveries and Decision Log"
    notes: "Machine-readable registered-RFC statuses are limited to `Draft` and `Accepted`, while every decision prerequisite must require `Accepted`. An absent or other value, including `Rejected`, `Withdrawn`, or `Superseded`, fails rather than being interpreted permissively. The permanent fixture crosses both supported statuses with active and completed owner states and separately rejects the invalid `Accepetd` status for IN_PROGRESS and DONE owners, so deleting allowlist validation changes an asserted outcome."
variants:
  - name: "package-name evidence variants"
    source_anchor: "official endpoint responses; registry policies"
    comparison: |-
      HTTP 404 at an exact official endpoint means no record was returned there at that time.
      It does not mean the name is reserved, publishable, free of similarity conflicts, or free
      of trademark/common-law claims. HTTP 403 at crates.io is wholly inconclusive.
    disposition: "Keep StatQED/package names provisional or accept them only with explicit point-in-time limitations and a pre-publication live recheck."
  - name: "monorepo publication variants"
    source_anchor: "ADR-0001, Decision and Consequences; Cargo Workspaces; Registrator and RegistryCI guidance"
    comparison: |-
      A monorepo is directly natural for Cargo workspaces and package-local R/Python builds.
      Julia General's ordinary workflow expects a package repository/root layout that does not
      match `frontends/julia`.
    disposition: "Accept the foundation source monorepo; require a later tested Julia mirror/split/publication strategy before promising General registration."
  - name: "Lean trust variants"
    source_anchor: "Lean ValidatingProofs; ARCHITECTURE.md, Trust modes"
    comparison: |-
      Kernel acceptance checks an elaborated declaration relative to its imports and axioms.
      Compiled checking adds compiler/runtime/platform trust; structural checking makes no
      mathematical guarantee. Source fidelity and external premises remain separate in every mode.
    disposition: "Accept Lean as initial normative proof backend without calling every Lean-adjacent execution kernel verification."
  - name: "Rust production and independent-oracle variants"
    source_anchor: "ADR-0003, Constraints and consequences; ADR-0004, Validation and evidence; Plan 0001, Milestone C — Settle an encoding prototype (SQ-0005–SQ-0007)"
    comparison: |-
      The planned production path centralizes canonicalization in Rust. Encoding acceptance first
      requires at least two genuinely independent implementations or oracles over the same vectors.
    disposition: "Require independence at the prototype/conformance gate; sharing production code must not masquerade as independent agreement."
  - name: "CBOR deterministic ordering variants"
    source_anchor: "RFC 8949 sections 4.2.1 and 4.2.3"
    comparison: |-
      Core deterministic encoding sorts map keys bytewise by their deterministic encodings.
      Length-first core deterministic encoding preserves the RFC 7049-era ordering. They can
      produce different byte strings for the same map.
    disposition: "RFC-0001 must name exactly one ordering and reject/normalize non-profile inputs as specified."
  - name: "CBOR current-standard and emerging-WG variants"
    source_anchor: "RFC 8949; draft-ietf-cbor-serialization-08 status and sections 1-5"
    comparison: |-
      RFC 8949 is the authoritative standard. The 2026 WG-last-call draft proposes newly named
      preferred-plus and deterministic serializations and is explicitly Work in Progress.
    disposition: "Base SQ-0005 on the accepted RFC corpus; monitor and record the draft without treating it as final or silently switching profiles."
  - name: "CDDL file and module variants"
    source_anchor: "RFCs 8610/9165/9682/9741; draft-ietf-cbor-cddl-modules-06"
    comparison: |-
      Versioned CDDL files using the accepted RFC grammar/control operators are standard-based.
      Import/include module directives are still specified by an active Internet-Draft.
    disposition: "Avoid normative module-directive syntax unless an RFC exists or the experiment pins the draft revision and labels it Experimental."
  - name: "theorem identity, integrity, and authorization variants"
    source_anchor: "Lean.Environment; ADR-0007, Candidate decision; RFC-0005, Terminology and source background and Proposed semantics; docs/design/theorem-registry.md; docs/spec/theorem-lock.md"
    comparison: |-
      Lean declaration name identifies a constant within an environment; a normalized statement
      digest is intended as an integrity/lookup key over canonical proposition and environment data;
      a proof body can change without a statement change; source anchors and reviews bind attribution
      and intended informal meaning; a verifier-selected registry root/policy supplies authorization.
    disposition: "Keep identity, statement integrity, proof/build lock, source review, and registry authorization distinct. No name-only substitution and no artifact-supplied-root authority."
  - name: "decision registration and acceptance variants"
    source_anchor: "work/backlog.yaml, decision_register; work/README.md, Scheduling; scripts/check_repository.py, ALLOWED_DECISION_STATUS, document_status, decision_owner_state_valid, check_readiness_regression_fixtures, and check_backlog; scripts/list_work.py, main"
    comparison: |-
      Registering every numbered RFC with one path and non-complete write-authorized owner prevents
      ownerless decisions and lets Accepted-only prerequisites block READY and active eligibility.
      The current registered-status variant is deliberately two-state: Draft blocks owner
      DONE/SUPERSEDED status, and Accepted releases that lifecycle gate. Rejected, Withdrawn,
      Superseded, and successor relations are a conflicting future variant that remains invalid until
      reviewed non-cyclic successor semantics and negative tests are implemented. Registration and
      lifecycle consistency remain distinct from semantic acceptance.
    disposition: "Retain the Draft/Accepted status, Draft-owner, Accepted-only-prerequisite, and shared-listing gates; do not infer successor semantics or present register coverage as semantic acceptance."
  - name: "READY and active scheduling variants"
    source_anchor: "work/backlog.yaml, task status; scripts/check_repository.py, check_backlog; scripts/list_work.py, main"
    comparison: |-
      READY identifies dependency/decision-eligible work not yet claimed; active identifies eligible
      IN_PROGRESS or IN_REVIEW work. The union must equal the computed eligible set, but the work list
      renders the states separately so active SQ-0001 is not mislabeled as unclaimed READY work.
    disposition: "Use one RFC-aware eligibility calculation while preserving the READY/active state distinction."
  - name: "logical data and foundation-fixture variants"
    source_anchor: "RFC-0006, Omit data from the foundation fixture, Formal and implementation consequences, and Decision; work/contracts/SQ-0006.yaml; work/contracts/SQ-0011.yaml; work/contracts/SQ-0027.yaml"
    comparison: |-
      A toy table would prematurely select row, type, missingness, and digest semantics. The
      accepted candidate scope instead keeps SQ-0006/SQ-0011 data-free and assigns the first
      normative real-data schema/digest/backend path to RFC-0006 owner SQ-0027; a physical-file
      checksum remains a different, weaker commitment.
    disposition: "Keep the foundation fixture/backend strictly data-free; resolve and Accept RFC-0006 in SQ-0027 before any real-data path."
  - name: "artifact envelope variants"
    source_anchor: "RFC-0008, Alternatives, Proposed semantics, and Decision"
    comparison: |-
      A constrained standard archive and a custom framed container remain candidates; a directory
      is useful only for development, and network-resolved thin bundles are rejected for archival
      verification. No container or implemented resource/privacy mechanism is yet normative. The
      candidate nevertheless fixes the identity distinction between committed/normative provenance
      and inert non-normative report-only disclosure transformations.
    disposition: "Defer container selection to SQ-0010 and retain all hostile-input, offline, privacy, redaction-identity, and result-identity gates."
  - name: "provenance-redaction identity variants"
    source_anchor: "RFC-0008, Proposed semantics; docs/spec/provenance.md, complete document; work/contracts/SQ-0010.yaml, tests and acceptance"
    comparison: |-
      Changing committed or normative provenance changes normative artifact/result identity.
      Redacting only an inert non-normative report preserves normative artifact identity, but the
      physical bundle bytes and file commitment change and the report/disclosure transformation is
      recorded. An unresolved external/uncommitted reference can remain a leaf; changed committed
      bytes require a newly identified normative object/result and cannot retain the old dependency closure.
    disposition: "Classify the changed material before redaction and apply the exact identity rule; never use an unresolved leaf to mask committed changes."
  - name: "current and planned governance variants"
    source_anchor: "GOVERNANCE.md, Current authority and Planned bodies; RFC-0009, Alternatives, Proposed semantics, and Decision"
    comparison: |-
      The founder-led repository owner currently has merge authority subject to mandatory review.
      Planned councils are not constituted; permanent founder control, immediate multi-council
      constitution, and a single steering committee are explicitly distinct variants for RFC-0009.
    disposition: "Describe only current authority; keep SQ-0020 blocked until it Accepts RFC-0009 and defer community-body authority until that acceptance."
  - name: "foundation and scientific vertical slices"
    source_anchor: "ADR-0011, Decision and Verification result and nonclaims; Plan 0001, Observable exit condition; ROADMAP.md, Phase 1 — Executable foundation through Phase 4 — Modern finite-sample inference; CHARTER.md, Founding success criterion"
    comparison: |-
      The data-free foundation slice is structural/toy and uses a definitionally trivial, test-only
      `True` record that is not a public theorem or non-vacuity witness. The later
      randomized-experiment, linear-model, and conformal/sequential slices are intended to carry
      real conditional statistical guarantees after their own source, theorem, and checker gates.
    disposition: "Do not call the SQ-0019 toy artifact a scientifically complete method or founding-success exemplar."
concept_mapping:
  - source_concept: "baseline commit and candidate manifest digest"
    statqed_concept: "immutable base provenance plus exact 77-file frozen SQ-0001 review surface"
    notes: "The sorted sha256sum-lines digest binds candidate file bytes under the recorded recipe; it is not a semantic-review or theorem identity."
  - source_concept: "Lean kernel-checked declaration"
    statqed_concept: "kernel-mode deductive node under exact theorem/dependency lock"
    notes: "Does not map to truth of external assumptions, data provenance, or interpretation."
  - source_concept: "Mathlib `Kernel α β` plus `IsMarkovKernel κ`"
    statqed_concept: "candidate basis for experiment/procedure Markov-kernel semantics"
    notes: "Requires measurable spaces and the Mathlib convention that probability-kernel status is a separate predicate/typeclass. No universal StatQED experiment signature is frozen here."
  - source_concept: "Cargo workspace member"
    statqed_concept: "Rust reference-backend crate within the foundation monorepo"
    notes: "Workspace membership and publication identity are separate."
  - source_concept: "Python distribution name versus import package"
    statqed_concept: "PyPI project `statqed` versus Python import namespace `statqed`"
    notes: "The matching spelling is a convention, not registry-enforced equivalence."
  - source_concept: "Julia package name plus UUID"
    statqed_concept: "`StatQED` frontend package identity"
    notes: "UUID, not name alone, disambiguates Julia packages; exact UUID is not selected by SQ-0001."
  - source_concept: "RFC 8949 deterministic encoding"
    statqed_concept: "candidate canonical byte profile for normative objects"
    notes: "StatQED adds semantic-normalization and rejection rules not supplied by core CBOR."
  - source_concept: "CDDL data model"
    statqed_concept: "versioned structural schema"
    notes: "Schema match is structural evidence, not canonical-byte equality or inferential validity."
  - source_concept: "MIT license identifier"
    statqed_concept: "outbound repository license"
    notes: "Does not replace third-party license review or citation/source-lineage records."
  - source_concept: "CFF software citation record"
    statqed_concept: "top-level StatQED software citation metadata"
    notes: "Method/theorem/artifact-level citations remain separate and more granular."
  - source_concept: "Lean declaration Name, signature/type, and theorem value"
    statqed_concept: "registry ID/version, canonical statement/environment material, and proof body/build lock"
    notes: "The normalizer, closure, digest, axiom baseline, and compatibility proof relation remain future governed work."
  - source_concept: "registry record integrity versus authorization root"
    statqed_concept: "content-bound theorem metadata versus verifier-selected accepted registry root/policy/status"
    notes: "An internally consistent artifact record cannot grant itself governed ID, maturity, review, revocation, or compatibility authority."
  - source_concept: "decision register owner and prerequisite"
    statqed_concept: "one non-complete write-authorized RFC owner plus Draft/Accepted status, Accepted-only prerequisites, and READY/active gates"
    notes: "Ownership, two-state status, lifecycle, and prerequisite enforcement prevent silent assumptions; none is decision acceptance, and successor semantics remain deferred."
  - source_concept: "RFC-0006 logical-data owner"
    statqed_concept: "SQ-0027 source audit, acceptance, schema/witness, and bounded first real-data backend path"
    notes: "SQ-0006 and SQ-0011 remain strictly data-free and cannot silently consume this later scope."
  - source_concept: "committed/normative versus inert-report provenance"
    statqed_concept: "normative-identity-changing redaction versus normative-identity-preserving but physical-bundle-changing report transformation"
    notes: "Inert report-only redaction changes bundle bytes/file commitment and records disclosure. Unresolved leaves apply only to external/uncommitted references or newly identified normative objects/results."
  - source_concept: "artifact envelope profile"
    statqed_concept: "future deterministic container, offline resolution, resource, provenance, privacy, and report-separation policy"
    notes: "RFC-0008/SQ-0010 are Deferred; no archive behavior is normative at SQ-0001."
quantifiers:
  - scope: "candidate constitutional surface"
    order: "collect every tracked change and untracked candidate path relative to baseline 2ad5c72f7adc402024152d6fa4af9c86cdf9b588; apply the five stated exclusions; require exactly 77 paths; hash each current file; bytewise-sort complete sha256sum lines in the C locale; hash their newline-terminated concatenation"
  - scope: "work eligibility"
    order: "for every non-DONE/non-SUPERSEDED task, first require every dependency DONE and every declared decision prerequisite at Accepted; then require the computed eligible set to equal the separately rendered union of declared READY and active IN_PROGRESS/IN_REVIEW tasks"
  - scope: "unresolved decision owner lifecycle"
    order: "first require every registered RFC status to be Draft or Accepted and every decision prerequisite to require Accepted; for every Draft RFC, require its owner not DONE or SUPERSEDED; reject every other status until reviewed non-cyclic successor semantics and negative tests extend the ledger"
  - scope: "provenance redaction"
    order: "for every proposed removal or change, classify whether it touches committed/normative provenance or only an inert non-normative report; the former creates new normative artifact and applicable result identity, while the latter preserves normative artifact identity but changes physical bundle bytes/file commitment and records the report/disclosure transformation"
  - scope: "registry endpoint observations"
    order: "for each exact URL, at retrieval instant 2026-08-03, record the returned status; make no claim for other endpoints, hidden state, archived state, or future time"
  - scope: "package publication"
    order: "for each ecosystem, at actual publication time, recheck exact name, syntax, ownership, policy, similarity, and required package behavior"
  - scope: "deterministic encoding"
    order: "for every accepted semantic object in the frozen profile, every conforming encoder emits one identical byte string; every checking decoder either accepts that profile byte string or returns the specified error"
  - scope: "theorem lock"
    order: "for every artifact theorem reference, the verifier independently selects the accepted registry root/policy and then resolves the exact canonical record, backend/environment/statement/proof/checker locks and historical/revocation status before accepting the dependent claim"
  - scope: "toy cross-language slice"
    order: "for the one data-free foundation_structural fixture, each of R, Python, and Julia must lower to the same accepted semantic object and shared production bytes/digests; independent encoder/oracle evidence is a separate RFC-0001 gate and may not reuse that production canonicalizer"
randomness_scopes:
  - name: "SQ-0001 constitutional audit"
    scope: "none"
    notes: "No probabilistic theorem or empirical sampling claim is made. Registry observations are time-indexed facts, not random-sample estimates."
  - name: "first foundation artifact"
    scope: "none"
    notes: "ADR-0011 requires probability context `not_applicable`; the toy object must not introduce an assignment, sampling, bootstrap, Monte Carlo, algorithmic, privacy, or posterior randomness claim."
nonvacuity_witnesses:
  - name: "candidate manifest witness"
    witness: "77 selected paths and sorted sha256sum-lines digest sha256:5793ce0b5c7e819090c74480e93e7167f6821897b96567c8b6c737bc8fa1ff96"
    limitation: "Binds current candidate bytes only under the recorded recipe and exclusions; it supplies no semantic or review-completion proof."
  - name: "package-name syntax witness"
    witness: "`statqed`, `statqed-core`, and `StatQED` satisfy the cited ecosystem grammar rules"
    limitation: "Syntactic admissibility does not witness registry acceptance."
  - name: "Lean probability-infrastructure witness"
    witness: "Published Mathlib declarations `ProbabilityTheory.Kernel` and `ProbabilityTheory.IsMarkovKernel`"
    limitation: "Does not witness a complete StatQED theorem or toolchain-compatible prototype."
  - name: "license/citation witness"
    witness: "Repository `LICENSE` and `CITATION.cff` exist at immutable baseline 2ad5c72f7adc402024152d6fa4af9c86cdf9b588 and remain outside the 77 changed paths"
    limitation: "No CFF validator or license-scanning tool was run."
  - name: "decision-owner gate witness"
    witness: "work/backlog.yaml registers RFC-0001 through RFC-0009 with one non-complete owner/path each; decision_owner_state_valid and check_readiness_regression_fixtures exhaust the Draft/Accepted by active/completed-owner matrix and reject invalid `Accepetd` for IN_PROGRESS and DONE; check_backlog enforces coverage, ownership, write authority, Draft-owner lifecycle, Accepted-only prerequisites, and READY/active eligibility; list_work consumes those shared sets"
    limitation: "A scheduling/guardrail witness is not Accepted-decision or implementation evidence."
  - name: "toy artifact witness"
    witness: "none; ADR-0011's definitionally trivial `True` record is test-only and explicitly cannot satisfy a public-theorem non-vacuity gate"
    limitation: "SQ-0019 may test the exact fixture and byte-to-proposition binding path, but that test remains neither a public-theorem non-vacuity witness nor evidence of general decoder, registry, or formalization capability."
strengthenings:
  - premise: "Treat exact endpoint 404 as guaranteed availability or reservation"
    class: "strengthening_unjustified"
    disposition: "prohibited; recheck live and retain the point-in-time limitation"
  - premise: "Treat exact-name web search as trademark clearance"
    class: "strengthening_unjustified"
    disposition: "prohibited; record search scope and obtain appropriate clearance before a claim"
  - premise: "Treat Rust `forbid(unsafe_code)` as elimination of unsafe dependencies/TCB"
    class: "strengthening_unjustified"
    disposition: "prohibited; inventory dependencies and report the actual mode-specific TCB"
  - premise: "Treat RFC 8949 core deterministic requirements as a complete StatQED canonicalization specification"
    class: "strengthening_unjustified"
    disposition: "blocks encoding freeze; RFC-0001/SQ-0005 must settle every application choice"
  - premise: "Require two independent implementations before accepting hash-critical bytes"
    class: "strengthening_justified"
    disposition: "retain as a project conformance gate; it is evidence discipline, not a source-theorem premise"
  - premise: "Treat CDDL validation as proof of semantic or inferential validity"
    class: "strengthening_unjustified"
    disposition: "prohibited; CDDL evidence is structural only"
  - premise: "Treat Lean kernel acceptance as proof of source fidelity or external premises"
    class: "strengthening_unjustified"
    disposition: "prohibited; require separate source, semantic, and external-evidence nodes/reviews"
  - premise: "Treat a declaration name or pretty-printed statement as a stable theorem lock"
    class: "strengthening_unjustified"
    disposition: "blocks theorem-lock freeze until the normalization/locking algorithm is specified and tested"
  - premise: "Treat a content-bound theorem registry record or artifact-supplied root as governed authorization"
    class: "strengthening_unjustified"
    disposition: "prohibited; verification policy independently selects the accepted root/policy and records historical/revocation status"
  - premise: "Treat an RFC's presence in decision_register as Accepted status"
    class: "strengthening_unjustified"
    disposition: "prohibited; the register supplies ownership and readiness gating, while the document status and review evidence govern acceptance"
  - premise: "Treat eligible active work as unclaimed READY work or compute it without RFC prerequisites"
    class: "strengthening_unjustified"
    disposition: "prohibited; repository checking and work listing share one dependency/RFC-aware eligibility calculation and render READY separately from IN_PROGRESS/IN_REVIEW"
  - premise: "Allow a Draft RFC owner to become DONE or SUPERSEDED, or treat an unsupported successor status as resolved"
    class: "strengthening_unjustified"
    disposition: "prohibited; Draft owners remain non-complete, only Accepted resolves the owner gate, and rejection/withdrawal/supersession remain invalid until reviewed non-cyclic successor semantics and negative tests exist"
  - premise: "Let SQ-0006 or SQ-0011 define a logical-data schema, digest, or real-data backend path"
    class: "strengthening_unjustified"
    disposition: "prohibited; those foundation tasks remain strictly data-free and detailed task SQ-0027 owns RFC-0006 and the first real-data path"
  - premise: "Let SQ-0020 complete while RFC-0007 or RFC-0009 remains unresolved"
    class: "strengthening_unjustified"
    disposition: "prohibited by both RFC Decisions and the SQ-0020 steps/acceptance gate"
  - premise: "Treat a readable archive or library-default extraction as a safe deterministic `.statqed` envelope"
    class: "strengthening_unjustified"
    disposition: "prohibited; RFC-0008/SQ-0010 must settle hostile path, entry, compression, resource, offline, provenance, privacy, and identity behavior"
  - premise: "Treat source-curator Candidate disposition as completion of all independent review"
    class: "strengthening_unjustified"
    disposition: "prohibited; statistical, formal, interoperability, adversarial, security/trust, privacy, and integration review records remain separate"
  - premise: "Treat every provenance redaction as identity-preserving or every report redaction as identity-changing"
    class: "strengthening_unjustified"
    disposition: "prohibited; committed/normative changes create new normative identity, while inert non-normative report-only redaction preserves normative artifact identity but changes physical bundle bytes/file commitment and records the report/disclosure transformation"
  - premise: "Use an unresolved leaf to preserve identity after committed bytes change"
    class: "strengthening_unjustified"
    disposition: "prohibited; unresolved leaves are limited to external/uncommitted references or newly identified normative objects/results"
  - premise: "Union evidence from separately identified verification modes into one stronger document status"
    class: "strengthening_unjustified"
    disposition: "prohibited; each verification-result record has one mode and documents preserve result separation"
  - premise: "Treat the toy structural artifact as a real statistical guarantee"
    class: "strengthening_unjustified"
    disposition: "prohibited public overclaim"
weakenings:
  - premise: "All provisional package names are available"
    weaker_form: "The proposed spellings are syntactically admissible; three exact endpoints returned 404 at one retrieval time; crates.io, reservation, GitHub organization, confusion, and legal clearance remain unresolved"
    disposition: "use until authoritative reservation/publication evidence exists"
  - premise: "Mathlib already supplies the required probability infrastructure"
    weaker_form: "Mathlib supplies specific relevant primitives, including Markov kernels; roadmap-wide coverage and exact-version compatibility remain research obligations"
    disposition: "supported"
  - premise: "CDDL modules are standard"
    weaker_form: "Use versioned CDDL schema files under RFC 8610 as updated by RFC 9682 and explicitly selected control-operator RFCs; module directives remain experimental"
    disposition: "required as of 2026-08-03"
  - premise: "Rust is safe and deterministic"
    weaker_form: "Rust is the planned reference operational implementation; safety, determinism, bounds, panic behavior, and cross-language agreement are properties to test and report"
    disposition: "required trust language"
  - premise: "The theorem statement hash identifies meaning"
    weaker_form: "A future versioned normalization algorithm and statement digest will bind selected canonical proposition/environment data for integrity and lookup; verifier-selected registry authorization, proof/build trust, source fidelity, and compatibility remain separate relations"
    disposition: "required until SQ-0007 evidence"
  - premise: "All registered constitutional decisions are accepted"
    weaker_form: "Every numbered RFC is registered to one non-complete write-authorized owner/path; registered statuses are only `Draft` or `Accepted`; decision prerequisites require only `Accepted`; downstream READY/active eligibility is status-gated; and rejection, withdrawal, supersession, and successor relations remain invalid until reviewed non-cyclic semantics and negative tests exist"
    disposition: "required owner-gate language"
  - premise: "The foundation backend includes canonical logical data and its digest"
    weaker_form: "SQ-0006 and SQ-0011 cover only the data-free foundation fixture and its non-data content digests; SQ-0027 must source-audit and Accept RFC-0006 before the first logical-data schema/digest/backend path"
    disposition: "required scope boundary"
  - premise: "Provenance can be redacted without affecting identity"
    weaker_form: "Only inert non-normative report-only redaction preserves normative artifact identity; it still changes physical bundle bytes/file commitment and records the report/disclosure transformation. Committed or normative provenance changes always create new normative artifact and applicable result identity"
    disposition: "required identity boundary"
  - premise: "The `.statqed` envelope is deterministic, secure, private, and offline-verifiable"
    weaker_form: "RFC-0008 records the required threat model and design obligations; SQ-0010 must select and test an exact envelope profile before any of those properties are claimed"
    disposition: "required deferral language"
  - premise: "The first vertical slice verifies a statistical analysis"
    weaker_form: "The first foundation slice, when implemented, checks only the data-free `foundation_structural` fixture, its explicit locks, and the separate definitionally trivial, test-only `True` record under each named single verification mode; it supplies no public-theorem non-vacuity witness"
    disposition: "constitutional nonclaim"
attribution:
  - work: "CBOR"
    authors: "Carsten Bormann and Paul Hoffman"
    citation: "RFC 8949 / STD 94, DOI 10.17487/RFC8949"
    license_notes: "Cite the RFC. Code components extracted from IETF documents are subject to the IETF Trust Legal Provisions; do not copy standards text into MIT files without preserving applicable terms."
  - work: "CDDL and updates"
    authors: "Henk Birkholz, Carsten Vigano, Carsten Bormann, and update RFC authors"
    citation: "RFCs 8610, 9165, 9682, and 9741 with the DOIs above"
    license_notes: "CDDL schemas written for StatQED may be MIT, but copied RFC code components/examples require their stated IETF Trust/Revised BSD treatment."
  - work: "Lean 4 and Mathlib"
    authors: "Lean developers and the Mathlib community"
    citation: "Exact Lean release/project commit and exact Mathlib commit must be recorded in theorem locks and releases"
    license_notes: "Preserve upstream notices and package licenses. A StatQED formalization does not transfer authorship of Mathlib or source mathematics."
  - work: "Rust, Cargo, Python packaging, R, and Julia package documentation"
    authors: "Their respective official projects/communities"
    citation: "Use the exact official locators above and record tested versions in later compatibility reports"
    license_notes: "Documentation licenses differ by project; links and paraphrase are used here."
  - work: "Citation File Format 1.2.0 and SPDX MIT identifier"
    authors: "Citation File Format and SPDX contributors"
    citation: "CFF schema guide 1.2.0; SPDX identifier MIT"
    license_notes: "CFF metadata complements, but does not replace, original theorem/software/data citations."
  - work: "StatQED constitutional design"
    authors: "Lukas Sablica and StatQED contributors"
    citation: "baseline repository commit 2ad5c72f7adc402024152d6fa4af9c86cdf9b588; frozen candidate constitutional-surface manifest sha256:5793ce0b5c7e819090c74480e93e7167f6821897b96567c8b6c737bc8fa1ff96"
    license_notes: "Repository material is MIT unless a file states otherwise; inbound rights and source attribution still require review."
review:
  status: "CANDIDATE"
  reviewers:
    - "source-curator — primary-source, exact-locator, hypothesis, attribution, and candidate-manifest review only (2026-08-03)"
  statement_hash: "sha256:2025a42db6b6ba2207e682b8879b922a0494a7dcdb53a041c2ac123e2733158a"
```

The `statement_hash` is SHA-256 over the exact UTF-8 bytes of `controlled_statement`, without a trailing newline. It is an audit-record integrity aid, not a theorem lock or semantic-equivalence proof.

Material premise ablations:

- Without the baseline-plus-exclusions manifest recipe, a candidate digest does not identify which working-tree files were reviewed; without sorting complete `sha256sum` lines, the recorded digest is not reproducible by the stated procedure.
- Without one shared RFC-aware readiness calculation, `make check` and `make list-work` can disagree or present active work as unclaimed READY work.
- Without the Draft/Accepted status vocabulary, Accepted-only prerequisite rule, Draft-owner gate, and explicit deferral of successor relations, an unsupported status can be treated as resolved or a Draft RFC can become ownerless when its task finishes.
- Without an explicit CBOR profile, RFC 8949 permits byte-distinct representations and distinct deterministic ordering variants; byte identity is not derivable.
- Without a verifier-selected registry authorization root/policy, an internally consistent artifact can substitute its own registry and self-assert governed theorem ID, maturity, review, or compatibility authority.
- Without exact dependency/environment and statement locks, a matching Lean name can resolve to a different declaration context; without a separate proof/build lock and actual axiom report, a proposition-preserving proof change can alter trust.
- Without source anchors and separate attribution metadata, a content hash cannot prevent source/credit drift.
- Without the registered owner and decision-prerequisite gates, downstream tasks can silently rely on ownerless Draft semantics; the gates still cannot substitute for acceptance review.
- Without the SQ-0027 ownership and strict SQ-0006/SQ-0011 data-free boundary, the foundation can silently freeze logical-data and digest semantics before their source audit.
- Without the SQ-0020 acceptance gate, compatibility or community-governance ownership can remain unresolved when the owning milestone-review task completes.
- Without the ADR-0011 data-free/toy-only qualifier, the first slice can be misreported as a logical-data model or statistical guarantee even though it has no data, estimand, probability law, real method, or inferential theorem.
- Without the RFC-0008 envelope deferral, a decodable archive can be misreported as deterministic, bounded, offline-safe, privacy-minimized, or secure without hostile-input evidence.
- Without the provenance classification rule, redaction can silently preserve an invalid normative identity or unnecessarily change it for an inert report-only transformation; even identity-preserving inert-report redaction changes physical bundle bytes/file commitment and must record disclosure, while an unresolved leaf cannot repair changed committed bytes.
- Without one mode per result and the no-union rule, separate structural and kernel-mode evidence can be combined into an unsupported stronger document status.
- Without a Julia publication boundary, monorepo source layout does not by itself satisfy General's ordinary package-root/repository workflow.
- Without exact toolchain pins plus reproduction and axiom evidence, a successful proof claim cannot be archived or audited reliably.

Blocking or explicitly deferred items:

1. Live crates.io, GitHub account/organization, documentation-host, and any desired domain checks remain unresolved; the three 404 observations are not reservations.
2. Trademark/confusion clearance remains outside this technical audit and must not be claimed from exact-name web search.
3. RFC-0001/SQ-0005 must choose the complete CBOR numeric, tag, key-order, duplicate, Unicode, extension, and decoder-checking profile and test independent implementations.
4. CDDL module directives are Work in Progress as of retrieval; pin accepted RFC syntax or label draft use Experimental.
5. RFC-0002 remains Draft; its constitutional distinctions constrain the candidate, but no Lean constructor, IR tag, assurance lattice, report schema, or other public evidence type is frozen until acceptance and downstream review.
6. RFC-0003/SQ-0012 must select and test the artifact byte-to-term adequacy path before artifact-level kernel-verification language is allowed.
7. RFC-0004 remains Deferred; no universal statistical ontology or randomness type is frozen, and method-specific source audits remain mandatory.
8. RFC-0005/SQ-0007 must define and adversarially/security-test theorem normalization, bounded meaning-bearing dependency closure, axiom baseline, canonical registry records, statement-digest domain, verifier-selected authorization root/policy, historical/revocation behavior, and compatibility direction.
9. RFC-0006 remains Deferred to detailed owner SQ-0027; SQ-0006/SQ-0011 and the data-free toy slice do not select or implement a canonical logical-data model, digest, or real-data backend path.
10. RFC-0007 remains Deferred; readability and semver provide no accepted cross-component claim-preservation promise, and SQ-0020 must remain blocked until it Accepts this RFC.
11. RFC-0008/SQ-0010 must select and hostile-test the envelope, offline/local resolution, resource, privacy/provenance, redaction, and result-identity mechanisms; the candidate redaction-identity distinctions do not establish implemented `.statqed` archive behavior.
12. RFC-0009 remains Deferred; planned community bodies have no current authority, and SQ-0020 must remain blocked until it Accepts this RFC.
13. The Julia frontend needs a later tested General-registry publication/mirror/split decision; a monorepo subdirectory is not enough evidence.
14. SQ-0002 and later tasks own all toolchain, build, publisher, runtime, conformance, artifact, privacy/security, and verification evidence.
15. Statistical, formal, interoperability, adversarial, security/trust, privacy, and integration review dispositions remain outside this source-curator review and must not be inferred from `review.status: CANDIDATE`.
