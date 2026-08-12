//! Adversarial and policy-bound resolver tests.

#![forbid(unsafe_code)]

use statqed_registry::{
    ErrorCode, MAX_IDENTIFIER_BYTES, POLICY_VERSION, RegistryRecord, RootStatus, TrustedPolicy,
    resolve, resolve_bytes,
};

const A: &str = "5393c485f51ec859474a250a577d5a266559d26738dbdd440f67082c2ddea71d";
const B: &str = "1111111111111111111111111111111111111111111111111111111111111111";
const C: &str = "2222222222222222222222222222222222222222222222222222222222222222";
const D: &str = "3333333333333333333333333333333333333333333333333333333333333333";
const E: &str = "68a6c0b4a9c83cc7c29c251b900d5a3c265fe9b4856df78a590aef99492513c4";
const F: &str = "e72ddf98e90bda2fa5ea0228f4fd316e02713fc75da5c56e40ca5aff2eb2f8ab";
const ZERO: &str = "0bdbb64aed12a2da31d4143fac4d1177ccd7ba6be3c6102670403b572dbb2f79";
const ONE: &str = "21133bcee092289c03469a9dd2174877d6b48e609766f79a3948e5011adb1966";
const TWO: &str = "b6626d7bb8b331327a1177dd9cd03e00d869d0598924ae14f8b2a848e6e26d4e";
const THREE: &str = "a0daf0ed5302f5257e0848e2ed936642bc57ecc9e1fc0b4d3b47f5ace0941bc6";

type RecordMutation = (fn(&mut RegistryRecord), ErrorCode);

fn policy() -> TrustedPolicy {
    TrustedPolicy {
        version: POLICY_VERSION.to_owned(),
        current_permitted_roots: vec![A.to_owned()],
        historical_permitted_roots: vec![B.to_owned()],
        historical_forbidden_roots: vec![C.to_owned()],
        revoked_roots: vec![D.to_owned()],
        record_id: "statqed.test-only.foundation.true.v0".to_owned(),
        semantic_version: "0.0.1".to_owned(),
        declaration: "StatQED.Registry.Tests.testOnlyTrue".to_owned(),
        proposition_digest: E.to_owned(),
        environment_digest: F.to_owned(),
        record_digest: ZERO.to_owned(),
        proof_build_digest: ONE.to_owned(),
        axiom_report_digest: TWO.to_owned(),
        compatibility_target: "statqed.test-only.foundation.true.v0".to_owned(),
        compatibility_digest: THREE.to_owned(),
    }
}

fn record() -> RegistryRecord {
    RegistryRecord {
        schema: "statqed.registry-record.v0".to_owned(),
        id: "statqed.test-only.foundation.true.v0".to_owned(),
        version: "0.0.1".to_owned(),
        declaration: "StatQED.Registry.Tests.testOnlyTrue".to_owned(),
        normalizer: "statqed.lean-expr.v0".to_owned(),
        normalization_status: "ok".to_owned(),
        closure: "statqed.lean-environment-closure.v0".to_owned(),
        closure_status: "ok".to_owned(),
        proposition_digest: E.to_owned(),
        environment_digest: F.to_owned(),
        record_digest: ZERO.to_owned(),
        requested_root: A.to_owned(),
        policy_version: POLICY_VERSION.to_owned(),
        proof_build_digest: ONE.to_owned(),
        axiom_report_digest: TWO.to_owned(),
        axiom_count: 0,
        maturity: "Experimental".to_owned(),
        exposure: "test_only".to_owned(),
        source_anchor: "docs/adr/0011-foundation-toy-slice.md".to_owned(),
        attribution: "not_applicable: definitionally trivial test proposition".to_owned(),
        nonclaims: "[\"not a public or statistical theorem\",\"not a non-vacuity witness\",\"not source-fidelity or artifact verification evidence\"]".to_owned(),
        compatibility_target: "statqed.test-only.foundation.true.v0".to_owned(),
        compatibility_direction: "new_implies_old".to_owned(),
        compatibility_digest: THREE.to_owned(),
        compatibility_edges: 1,
        registry_entries: 1,
        expression_nodes: 1,
        expression_depth: 1,
        closure_width: 1,
        closure_depth: 1,
        work_nodes: 1,
    }
}

fn wire(record: &RegistryRecord) -> Vec<u8> {
    format!(
        concat!(
            "attribution={}\n",
            "axiom_count={}\n",
            "axiom_report_digest={}\n",
            "closure={}\n",
            "closure_status={}\n",
            "closure_depth={}\n",
            "closure_width={}\n",
            "compatibility_digest={}\n",
            "compatibility_direction={}\n",
            "compatibility_edges={}\n",
            "compatibility_target={}\n",
            "declaration={}\n",
            "environment_digest={}\n",
            "expression_depth={}\n",
            "expression_nodes={}\n",
            "exposure={}\n",
            "id={}\n",
            "maturity={}\n",
            "nonclaims={}\n",
            "normalizer={}\n",
            "normalization_status={}\n",
            "policy_version={}\n",
            "proof_build_digest={}\n",
            "proposition_digest={}\n",
            "record_digest={}\n",
            "registry_entries={}\n",
            "requested_root={}\n",
            "schema={}\n",
            "source_anchor={}\n",
            "version={}\n",
            "work_nodes={}\n",
        ),
        record.attribution,
        record.axiom_count,
        record.axiom_report_digest,
        record.closure,
        record.closure_status,
        record.closure_depth,
        record.closure_width,
        record.compatibility_digest,
        record.compatibility_direction,
        record.compatibility_edges,
        record.compatibility_target,
        record.declaration,
        record.environment_digest,
        record.expression_depth,
        record.expression_nodes,
        record.exposure,
        record.id,
        record.maturity,
        record.nonclaims,
        record.normalizer,
        record.normalization_status,
        record.policy_version,
        record.proof_build_digest,
        record.proposition_digest,
        record.record_digest,
        record.registry_entries,
        record.requested_root,
        record.schema,
        record.source_anchor,
        record.version,
        record.work_nodes,
    )
    .into_bytes()
}

#[test]
fn current_policy_resolves_deterministically() {
    let result = resolve_bytes(&wire(&record()), &policy());
    assert_eq!(
        result.map(|value| value.root_status),
        Ok(RootStatus::Current)
    );
}

#[test]
fn historical_permitted_root_is_explicitly_accepted() {
    let mut candidate = record();
    candidate.requested_root = B.to_owned();
    assert_eq!(
        resolve(&candidate, &policy()).map(|value| value.root_status),
        Ok(RootStatus::HistoricalPermitted)
    );
}

#[test]
fn unknown_revoked_and_forbidden_roots_are_distinct() {
    for (root, expected) in [
        (C, ErrorCode::AuthorizationRootHistoricalForbidden),
        (D, ErrorCode::AuthorizationRootRevoked),
        (
            "9999999999999999999999999999999999999999999999999999999999999999",
            ErrorCode::AuthorizationRootUnknown,
        ),
    ] {
        let mut candidate = record();
        candidate.requested_root = root.to_owned();
        assert_eq!(resolve(&candidate, &policy()), Err(expected));
    }
}

#[test]
fn candidate_cannot_select_policy_or_replacement_root() {
    let mut candidate = record();
    candidate.policy_version = "candidate.policy.v9".to_owned();
    assert_eq!(
        resolve(&candidate, &policy()),
        Err(ErrorCode::AuthorizationPolicyUnsupported)
    );
    candidate = record();
    candidate.requested_root = ZERO.to_owned();
    assert_eq!(
        resolve(&candidate, &policy()),
        Err(ErrorCode::AuthorizationRootUnknown)
    );
}

#[test]
fn governed_record_and_distinct_identity_layers_are_checked() {
    let mutations: &[RecordMutation] = &[
        (
            |r| r.id = "statqed.test-only.forged.v0".to_owned(),
            ErrorCode::RecordDigestMismatch,
        ),
        (
            |r| r.proposition_digest = A.to_owned(),
            ErrorCode::StatementDigestMismatch,
        ),
        (
            |r| r.environment_digest = A.to_owned(),
            ErrorCode::EnvironmentMismatch,
        ),
        (
            |r| r.record_digest = A.to_owned(),
            ErrorCode::RecordDigestMismatch,
        ),
        (
            |r| r.proof_build_digest = A.to_owned(),
            ErrorCode::ProofBuildLockMismatch,
        ),
        (
            |r| r.maturity = "Stable".to_owned(),
            ErrorCode::RecordDigestMismatch,
        ),
    ];
    for (mutate, expected) in mutations {
        let mut candidate = record();
        mutate(&mut candidate);
        assert_eq!(resolve(&candidate, &policy()), Err(*expected));
    }
}

#[test]
fn normalization_and_closure_failures_keep_stable_ownership() {
    for (status, expected) in [
        ("unsupported_expression", ErrorCode::ExpressionUnsupported),
        ("failure", ErrorCode::NormalizationFailure),
    ] {
        let mut candidate = record();
        candidate.normalization_status = status.to_owned();
        assert_eq!(resolve(&candidate, &policy()), Err(expected));
    }
    for (status, expected) in [
        ("cycle", ErrorCode::ClosureCycle),
        ("missing_dependency", ErrorCode::MissingDependency),
        ("width_limit", ErrorCode::ClosureWidthLimit),
        ("depth_limit", ErrorCode::ClosureDepthLimit),
        ("work_budget_limit", ErrorCode::ClosureWorkBudgetLimit),
    ] {
        let mut candidate = record();
        candidate.closure_status = status.to_owned();
        assert_eq!(resolve(&candidate, &policy()), Err(expected));
    }
}

#[test]
fn forbidden_axiom_or_report_substitution_fails() {
    let mut candidate = record();
    candidate.axiom_count = 1;
    assert_eq!(
        resolve(&candidate, &policy()),
        Err(ErrorCode::ForbiddenAxiom)
    );
    candidate = record();
    candidate.axiom_report_digest = A.to_owned();
    assert_eq!(
        resolve(&candidate, &policy()),
        Err(ErrorCode::ForbiddenAxiom)
    );
}

#[test]
fn compatibility_is_bound_and_directional_when_present() {
    let mut candidate = record();
    candidate.compatibility_direction = "old_implies_new".to_owned();
    assert_eq!(
        resolve(&candidate, &policy()),
        Err(ErrorCode::CompatibilityWrongDirection)
    );
    candidate = record();
    candidate.compatibility_digest = A.to_owned();
    assert_eq!(
        resolve(&candidate, &policy()),
        Err(ErrorCode::CompatibilityMissing)
    );
}

#[test]
fn direct_identity_can_have_no_compatibility_edge() {
    let mut candidate = record();
    candidate.compatibility_edges = 0;
    candidate.compatibility_target = "not_applicable".to_owned();
    candidate.compatibility_direction = "not_applicable".to_owned();
    assert!(resolve(&candidate, &policy()).is_ok());
}

#[test]
fn malformed_duplicate_unknown_and_non_utf8_inputs_fail_closed() {
    let valid = wire(&record());
    let without_newline = valid.strip_suffix(b"\n").unwrap_or(&valid);
    assert_eq!(
        resolve_bytes(without_newline, &policy()),
        Err(ErrorCode::MalformedRecord)
    );
    let mut duplicate = valid.clone();
    duplicate.extend_from_slice(b"id=statqed.test-only.foundation.true.v0\n");
    assert_eq!(
        resolve_bytes(&duplicate, &policy()),
        Err(ErrorCode::MalformedRecord)
    );
    let mut unknown = valid.clone();
    unknown.extend_from_slice(b"unknown=value\n");
    assert_eq!(
        resolve_bytes(&unknown, &policy()),
        Err(ErrorCode::MalformedRecord)
    );
    assert_eq!(
        resolve_bytes(&[0xff, b'\n'], &policy()),
        Err(ErrorCode::MalformedRecord)
    );
}

#[test]
fn identifier_boundary_and_one_over_are_bounded() {
    let mut at_limit = record();
    at_limit.id = format!("a{}", "a".repeat(MAX_IDENTIFIER_BYTES - 1));
    let mut matching = policy();
    matching.record_id.clone_from(&at_limit.id);
    assert!(resolve(&at_limit, &matching).is_ok());

    let mut over = at_limit;
    over.id.push('a');
    assert_eq!(resolve(&over, &matching), Err(ErrorCode::ResourceLimit));
}

#[test]
fn input_and_collection_limits_are_bounded() {
    let oversized = vec![b'a'; statqed_registry::MAX_INPUT_BYTES + 1];
    assert_eq!(
        resolve_bytes(&oversized, &policy()),
        Err(ErrorCode::ResourceLimit)
    );
    let mut candidate = record();
    candidate.compatibility_edges = statqed_registry::MAX_COMPATIBILITY_EDGES + 1;
    assert_eq!(
        resolve(&candidate, &policy()),
        Err(ErrorCode::ResourceLimit)
    );

    let mut excessive_policy = policy();
    excessive_policy.current_permitted_roots =
        vec![A.to_owned(); statqed_registry::MAX_REGISTRY_ENTRIES + 1];
    assert_eq!(
        resolve(&record(), &excessive_policy),
        Err(ErrorCode::ResourceLimit)
    );
}

fn assert_record_limit(set: fn(&mut RegistryRecord, usize), maximum: usize) {
    let mut at_limit = record();
    set(&mut at_limit, maximum);
    assert!(resolve(&at_limit, &policy()).is_ok());

    let mut one_over = record();
    set(&mut one_over, maximum + 1);
    assert_eq!(resolve(&one_over, &policy()), Err(ErrorCode::ResourceLimit));
}

#[test]
fn evidence_budget_boundaries_accept_maximum_and_reject_one_over() {
    assert_record_limit(
        |record, value| record.expression_nodes = value,
        statqed_registry::MAX_EXPRESSION_NODES,
    );
    assert_record_limit(
        |record, value| record.expression_depth = value,
        statqed_registry::MAX_EXPRESSION_DEPTH,
    );
    assert_record_limit(
        |record, value| record.closure_width = value,
        statqed_registry::MAX_CLOSURE_WIDTH,
    );
    assert_record_limit(
        |record, value| record.closure_depth = value,
        statqed_registry::MAX_CLOSURE_DEPTH,
    );
    assert_record_limit(
        |record, value| record.work_nodes = value,
        statqed_registry::MAX_WORK_NODES,
    );
}

#[test]
fn structural_maxima_remain_narrower_than_parser_resource_maxima() {
    let mut axioms_at_parser_limit = record();
    axioms_at_parser_limit.axiom_count = statqed_registry::MAX_AXIOM_ENTRIES;
    assert_eq!(
        resolve(&axioms_at_parser_limit, &policy()),
        Err(ErrorCode::ForbiddenAxiom)
    );
    axioms_at_parser_limit.axiom_count += 1;
    assert_eq!(
        resolve(&axioms_at_parser_limit, &policy()),
        Err(ErrorCode::ResourceLimit)
    );

    let mut entries_at_parser_limit = record();
    entries_at_parser_limit.registry_entries = statqed_registry::MAX_REGISTRY_ENTRIES;
    assert_eq!(
        resolve(&entries_at_parser_limit, &policy()),
        Err(ErrorCode::MalformedRecord)
    );
    entries_at_parser_limit.registry_entries += 1;
    assert_eq!(
        resolve(&entries_at_parser_limit, &policy()),
        Err(ErrorCode::ResourceLimit)
    );

    let mut compatibility_at_limit = record();
    compatibility_at_limit.compatibility_edges = statqed_registry::MAX_COMPATIBILITY_EDGES;
    assert!(resolve(&compatibility_at_limit, &policy()).is_ok());
    compatibility_at_limit.compatibility_edges += 1;
    assert_eq!(
        resolve(&compatibility_at_limit, &policy()),
        Err(ErrorCode::ResourceLimit)
    );
}

#[test]
fn repeated_randomized_bytes_never_panic() {
    let mut state = 0x1234_5678_9abc_def0_u64;
    for length in 0..512_usize {
        let mut bytes = Vec::with_capacity(length);
        for _ in 0..length {
            state ^= state << 13;
            state ^= state >> 7;
            state ^= state << 17;
            bytes.push(state.to_le_bytes()[0]);
        }
        let _ = resolve_bytes(&bytes, &policy());
    }
}

#[test]
fn all_error_codes_are_stable_and_bounded() {
    let codes = [
        ErrorCode::MalformedRecord,
        ErrorCode::VersionUnsupported,
        ErrorCode::NormalizationFailure,
        ErrorCode::ExpressionUnsupported,
        ErrorCode::ClosureCycle,
        ErrorCode::ClosureWidthLimit,
        ErrorCode::ClosureDepthLimit,
        ErrorCode::ClosureWorkBudgetLimit,
        ErrorCode::MissingDependency,
        ErrorCode::PropositionMismatch,
        ErrorCode::EnvironmentMismatch,
        ErrorCode::StatementDigestMismatch,
        ErrorCode::RecordDigestMismatch,
        ErrorCode::AuthorizationRootMismatch,
        ErrorCode::AuthorizationRootUnknown,
        ErrorCode::AuthorizationRootRevoked,
        ErrorCode::AuthorizationRootHistoricalForbidden,
        ErrorCode::AuthorizationPolicyUnsupported,
        ErrorCode::ProofBuildLockMismatch,
        ErrorCode::ForbiddenAxiom,
        ErrorCode::CompatibilityMissing,
        ErrorCode::CompatibilityWrongDirection,
        ErrorCode::ResourceLimit,
        ErrorCode::OperationalFailure,
    ];
    for code in codes {
        assert!(code.as_str().starts_with("registry."));
        assert!(code.as_str().len() <= statqed_registry::MAX_DIAGNOSTIC_BYTES);
    }
}
