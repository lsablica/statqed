//! Bounded offline resolution for the StatQED test-only theorem registry v0.
//!
//! The crate intentionally does not implement canonical theorem extraction or
//! artifact parsing. It checks a bounded operational representation against a
//! verifier-selected policy supplied independently of the candidate record.

#![forbid(unsafe_code)]

use std::collections::BTreeMap;
use std::str;

/// Registry format accepted by this resolver.
pub const REGISTRY_FORMAT_VERSION: &str = "statqed.registry-record.v0";
/// Policy format selected by the verifier.
pub const POLICY_VERSION: &str = "statqed.registry-authorization.v0";
/// Normalizer version required by the test-only record.
pub const NORMALIZER_VERSION: &str = "statqed.lean-expr.v0";
/// Meaning-bearing closure version required by the test-only record.
pub const CLOSURE_VERSION: &str = "statqed.lean-environment-closure.v0";
/// Visibly test-only governed identifier.
pub const TEST_ONLY_ID: &str = "statqed.test-only.foundation.true.v0";
/// Only accepted compatibility direction when new material substitutes for old.
pub const USEFUL_DIRECTION: &str = "new_implies_old";

/// Maximum operational input size in bytes.
pub const MAX_INPUT_BYTES: usize = 1_048_576;
/// Maximum number of records accepted by the hostile-input parser.
pub const MAX_REGISTRY_ENTRIES: usize = 16;
/// Number of published records in the intentionally narrow v0 snapshot.
pub const PUBLISHED_REGISTRY_ENTRIES: usize = 1;
/// Maximum governed identifier size in bytes.
pub const MAX_IDENTIFIER_BYTES: usize = 128;
/// Maximum generic field size in bytes.
pub const MAX_STRING_BYTES: usize = 65_536;
/// Maximum expression node budget represented by evidence.
pub const MAX_EXPRESSION_NODES: usize = 65_536;
/// Maximum expression depth represented by evidence.
pub const MAX_EXPRESSION_DEPTH: usize = 256;
/// Maximum closure width represented by evidence.
pub const MAX_CLOSURE_WIDTH: usize = 256;
/// Maximum closure depth represented by evidence.
pub const MAX_CLOSURE_DEPTH: usize = 64;
/// Maximum total dependency/work nodes represented by evidence.
pub const MAX_WORK_NODES: usize = 1_000_000;
/// Maximum axiom entries in one report.
pub const MAX_AXIOM_ENTRIES: usize = 256;
/// Maximum compatibility edges in v0.
pub const MAX_COMPATIBILITY_EDGES: usize = 32;
/// Maximum deterministic diagnostic size.
pub const MAX_DIAGNOSTIC_BYTES: usize = 4_096;

const FIELD_COUNT: usize = 31;
const MAX_FIELDS: usize = 40;

/// Stable failure classes. Messages never include candidate-controlled text.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum ErrorCode {
    /// Operational record is malformed or has unexpected fields.
    MalformedRecord,
    /// Registry-record version is unsupported.
    VersionUnsupported,
    /// Proposition normalization failed upstream.
    NormalizationFailure,
    /// An expression constructor is outside the accepted normalizer grammar.
    UnsupportedExpression,
    /// The closure evidence reports a cycle.
    ClosureCycle,
    /// Closure width, depth, or work budget is exceeded.
    ClosureBudget,
    /// A required environment dependency is absent.
    MissingDependency,
    /// Proposition identity does not match trusted policy.
    PropositionMismatch,
    /// Environment identity does not match trusted policy.
    EnvironmentMismatch,
    /// Statement digest does not match trusted policy.
    StatementDigestMismatch,
    /// Canonical registry-record digest does not match trusted policy.
    RecordDigestMismatch,
    /// Root is structurally known but not selected by policy.
    AuthorizationRootMismatch,
    /// Root is unknown to trusted policy.
    AuthorizationRootUnknown,
    /// Root is revoked by trusted policy.
    AuthorizationRootRevoked,
    /// Authorization policy version is unsupported.
    AuthorizationPolicyUnsupported,
    /// Proof/build lock does not match trusted policy.
    ProofBuildLockMismatch,
    /// Axiom evidence includes prohibited project trust.
    ForbiddenAxiom,
    /// Required compatibility evidence is absent.
    CompatibilityMissing,
    /// Compatibility evidence has the wrong implication direction.
    CompatibilityWrongDirection,
    /// A fixed input, count, or diagnostic limit was exceeded.
    ResourceLimit,
    /// A bounded operational failure occurred.
    OperationalFailure,
}

impl ErrorCode {
    /// Return the stable symbolic error code.
    #[must_use]
    pub const fn as_str(self) -> &'static str {
        match self {
            Self::MalformedRecord => "registry.malformed_record",
            Self::VersionUnsupported => "registry.version_unsupported",
            Self::NormalizationFailure => "registry.normalization_failure",
            Self::UnsupportedExpression => "registry.unsupported_expression",
            Self::ClosureCycle => "registry.closure_cycle",
            Self::ClosureBudget => "registry.closure_budget",
            Self::MissingDependency => "registry.missing_dependency",
            Self::PropositionMismatch => "registry.proposition_mismatch",
            Self::EnvironmentMismatch => "registry.environment_mismatch",
            Self::StatementDigestMismatch => "registry.statement_digest_mismatch",
            Self::RecordDigestMismatch => "registry.record_digest_mismatch",
            Self::AuthorizationRootMismatch => "registry.authorization_root_mismatch",
            Self::AuthorizationRootUnknown => "registry.authorization_root_unknown",
            Self::AuthorizationRootRevoked => "registry.authorization_root_revoked",
            Self::AuthorizationPolicyUnsupported => "registry.authorization_policy_unsupported",
            Self::ProofBuildLockMismatch => "registry.proof_build_lock_mismatch",
            Self::ForbiddenAxiom => "registry.forbidden_axiom",
            Self::CompatibilityMissing => "registry.compatibility_missing",
            Self::CompatibilityWrongDirection => "registry.compatibility_wrong_direction",
            Self::ResourceLimit => "registry.resource_limit",
            Self::OperationalFailure => "registry.operational_failure",
        }
    }
}

/// Bounded operational record submitted to the offline resolver.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct RegistryRecord {
    /// Canonical record schema identifier.
    pub schema: String,
    /// Governed test-only identifier.
    pub id: String,
    /// Governed semantic version.
    pub version: String,
    /// Exact extracted Lean declaration name.
    pub declaration: String,
    /// Proposition-normalizer version.
    pub normalizer: String,
    /// Upstream normalizer outcome conveyed without unstable diagnostics.
    pub normalization_status: String,
    /// Environment-closure version.
    pub closure: String,
    /// Upstream closure outcome conveyed without unstable diagnostics.
    pub closure_status: String,
    /// Proposition digest.
    pub proposition_digest: String,
    /// Meaning-bearing environment digest.
    pub environment_digest: String,
    /// Canonical registry-record digest.
    pub record_digest: String,
    /// Candidate-requested snapshot root; policy, not this field, decides trust.
    pub requested_root: String,
    /// Candidate-declared policy version.
    pub policy_version: String,
    /// Proof/build lock digest.
    pub proof_build_digest: String,
    /// Live axiom-report digest.
    pub axiom_report_digest: String,
    /// Number of observed axioms.
    pub axiom_count: usize,
    /// Reviewed maturity label.
    pub maturity: String,
    /// Reviewed test-only exposure label.
    pub exposure: String,
    /// Reviewed source anchor.
    pub source_anchor: String,
    /// Reviewed original-source attribution rationale.
    pub attribution: String,
    /// Reviewed compact nonclaim-set identifier.
    pub nonclaims: String,
    /// Compatibility target ID.
    pub compatibility_target: String,
    /// Direction of the kernel-checked implication.
    pub compatibility_direction: String,
    /// Compatibility-proof lock digest.
    pub compatibility_digest: String,
    /// Number of compatibility edges represented by the record.
    pub compatibility_edges: usize,
    /// Number of records represented by the snapshot.
    pub registry_entries: usize,
    /// Observed expression-node count.
    pub expression_nodes: usize,
    /// Observed expression depth.
    pub expression_depth: usize,
    /// Observed maximum closure width.
    pub closure_width: usize,
    /// Observed closure depth.
    pub closure_depth: usize,
    /// Observed total dependency work.
    pub work_nodes: usize,
}

/// Verifier-selected policy and exact expected bindings.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct TrustedPolicy {
    /// Policy format version.
    pub version: String,
    /// Current permitted authorization roots.
    pub current_permitted_roots: Vec<String>,
    /// Previously permitted roots still accepted for this check.
    pub historical_permitted_roots: Vec<String>,
    /// Historical roots explicitly forbidden.
    pub historical_forbidden_roots: Vec<String>,
    /// Revoked roots.
    pub revoked_roots: Vec<String>,
    /// Expected governed record identifier.
    pub record_id: String,
    /// Expected semantic version.
    pub semantic_version: String,
    /// Expected exact Lean declaration name.
    pub declaration: String,
    /// Expected proposition digest.
    pub proposition_digest: String,
    /// Expected environment digest.
    pub environment_digest: String,
    /// Expected canonical registry-record digest.
    pub record_digest: String,
    /// Expected proof/build lock digest.
    pub proof_build_digest: String,
    /// Expected live axiom-report digest.
    pub axiom_report_digest: String,
    /// Expected compatibility target.
    pub compatibility_target: String,
    /// Expected compatibility-proof lock digest.
    pub compatibility_digest: String,
}

/// Deterministic successful resolution output.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Resolution {
    /// Resolved governed record identifier.
    pub record_id: String,
    /// Accepted authorization-root classification.
    pub root_status: RootStatus,
    /// Stable semantic identity components, kept separate.
    pub proposition_digest: String,
    /// Stable meaning-bearing environment identity.
    pub environment_digest: String,
    /// Stable proof/build lock, distinct from theorem semantics.
    pub proof_build_digest: String,
}

/// Accepted authorization-root classes.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum RootStatus {
    /// Current verifier-selected root.
    Current,
    /// Historical root explicitly permitted by verifier policy.
    HistoricalPermitted,
}

/// Parse and resolve a bounded operational record entirely offline.
///
/// The input is a strict UTF-8 sequence of `key=value` lines. It is an
/// operational transport, not the normative registry-record byte grammar.
///
/// # Errors
///
/// Returns a stable [`ErrorCode`] for malformed, mismatched, unauthorized, or
/// resource-exceeding input.
pub fn resolve_bytes(input: &[u8], policy: &TrustedPolicy) -> Result<Resolution, ErrorCode> {
    let record = parse_record(input)?;
    resolve(&record, policy)
}

/// Resolve a typed record against independently supplied trusted policy.
///
/// # Errors
///
/// Returns a stable [`ErrorCode`] when any required identity, trust, resource,
/// axiom, or compatibility binding fails.
pub fn resolve(record: &RegistryRecord, policy: &TrustedPolicy) -> Result<Resolution, ErrorCode> {
    validate_policy(policy)?;
    validate_record_shape(record)?;

    if record.schema != REGISTRY_FORMAT_VERSION {
        return Err(ErrorCode::VersionUnsupported);
    }
    if record.policy_version != policy.version || policy.version != POLICY_VERSION {
        return Err(ErrorCode::AuthorizationPolicyUnsupported);
    }
    if record.declaration != policy.declaration {
        return Err(ErrorCode::PropositionMismatch);
    }
    if record.id != policy.record_id
        || record.version != policy.semantic_version
        || record.maturity != "Experimental"
        || record.exposure != "test_only"
        || record.source_anchor != "docs/adr/0011-foundation-toy-slice.md"
        || record.attribution != "not_applicable: definitionally trivial test proposition"
        || record.nonclaims
            != "[\"not a public or statistical theorem\",\"not a non-vacuity witness\",\"not source-fidelity or artifact verification evidence\"]"
    {
        return Err(ErrorCode::RecordDigestMismatch);
    }
    if record.normalizer != NORMALIZER_VERSION {
        return Err(ErrorCode::NormalizationFailure);
    }
    match record.normalization_status.as_str() {
        "ok" => {}
        "unsupported_expression" => return Err(ErrorCode::UnsupportedExpression),
        _ => return Err(ErrorCode::NormalizationFailure),
    }
    if record.closure != CLOSURE_VERSION {
        return Err(ErrorCode::EnvironmentMismatch);
    }
    match record.closure_status.as_str() {
        "ok" => {}
        "cycle" => return Err(ErrorCode::ClosureCycle),
        "missing_dependency" => return Err(ErrorCode::MissingDependency),
        "budget" => return Err(ErrorCode::ClosureBudget),
        _ => return Err(ErrorCode::MalformedRecord),
    }
    if record.proposition_digest != policy.proposition_digest {
        return Err(ErrorCode::StatementDigestMismatch);
    }
    if record.environment_digest != policy.environment_digest {
        return Err(ErrorCode::EnvironmentMismatch);
    }
    if record.record_digest != policy.record_digest {
        return Err(ErrorCode::RecordDigestMismatch);
    }

    let root_status = classify_root(&record.requested_root, policy)?;

    if record.proof_build_digest != policy.proof_build_digest {
        return Err(ErrorCode::ProofBuildLockMismatch);
    }
    if record.axiom_report_digest != policy.axiom_report_digest || record.axiom_count != 0 {
        return Err(ErrorCode::ForbiddenAxiom);
    }
    if record.compatibility_edges > MAX_COMPATIBILITY_EDGES {
        return Err(ErrorCode::ResourceLimit);
    }
    if record.compatibility_edges == 0 {
        if record.compatibility_target != "not_applicable"
            || record.compatibility_direction != "not_applicable"
            || record.compatibility_digest != policy.compatibility_digest
        {
            return Err(ErrorCode::CompatibilityMissing);
        }
    } else if record.compatibility_direction != USEFUL_DIRECTION {
        return Err(ErrorCode::CompatibilityWrongDirection);
    } else if record.compatibility_target != policy.compatibility_target
        || record.compatibility_digest != policy.compatibility_digest
    {
        return Err(ErrorCode::CompatibilityMissing);
    }

    Ok(Resolution {
        record_id: record.id.clone(),
        root_status,
        proposition_digest: record.proposition_digest.clone(),
        environment_digest: record.environment_digest.clone(),
        proof_build_digest: record.proof_build_digest.clone(),
    })
}

fn parse_record(input: &[u8]) -> Result<RegistryRecord, ErrorCode> {
    if input.len() > MAX_INPUT_BYTES {
        return Err(ErrorCode::ResourceLimit);
    }
    let text = str::from_utf8(input).map_err(|_| ErrorCode::MalformedRecord)?;
    if !text.ends_with('\n') {
        return Err(ErrorCode::MalformedRecord);
    }

    let mut fields = BTreeMap::new();
    for line in text.lines() {
        if line.is_empty() || line.len() > MAX_STRING_BYTES || fields.len() >= MAX_FIELDS {
            return Err(ErrorCode::ResourceLimit);
        }
        let (key, value) = line.split_once('=').ok_or(ErrorCode::MalformedRecord)?;
        if key.is_empty() || value.is_empty() || !valid_field_name(key) {
            return Err(ErrorCode::MalformedRecord);
        }
        if fields.insert(key, value).is_some() {
            return Err(ErrorCode::MalformedRecord);
        }
    }
    if fields.len() != FIELD_COUNT {
        return Err(ErrorCode::MalformedRecord);
    }

    Ok(RegistryRecord {
        schema: take(&fields, "schema")?,
        id: take(&fields, "id")?,
        version: take(&fields, "version")?,
        declaration: take(&fields, "declaration")?,
        normalizer: take(&fields, "normalizer")?,
        normalization_status: take(&fields, "normalization_status")?,
        closure: take(&fields, "closure")?,
        closure_status: take(&fields, "closure_status")?,
        proposition_digest: take(&fields, "proposition_digest")?,
        environment_digest: take(&fields, "environment_digest")?,
        record_digest: take(&fields, "record_digest")?,
        requested_root: take(&fields, "requested_root")?,
        policy_version: take(&fields, "policy_version")?,
        proof_build_digest: take(&fields, "proof_build_digest")?,
        axiom_report_digest: take(&fields, "axiom_report_digest")?,
        axiom_count: parse_count(&fields, "axiom_count")?,
        maturity: take(&fields, "maturity")?,
        exposure: take(&fields, "exposure")?,
        source_anchor: take(&fields, "source_anchor")?,
        attribution: take(&fields, "attribution")?,
        nonclaims: take(&fields, "nonclaims")?,
        compatibility_target: take(&fields, "compatibility_target")?,
        compatibility_direction: take(&fields, "compatibility_direction")?,
        compatibility_digest: take(&fields, "compatibility_digest")?,
        compatibility_edges: parse_count(&fields, "compatibility_edges")?,
        registry_entries: parse_count(&fields, "registry_entries")?,
        expression_nodes: parse_count(&fields, "expression_nodes")?,
        expression_depth: parse_count(&fields, "expression_depth")?,
        closure_width: parse_count(&fields, "closure_width")?,
        closure_depth: parse_count(&fields, "closure_depth")?,
        work_nodes: parse_count(&fields, "work_nodes")?,
    })
}

fn validate_policy(policy: &TrustedPolicy) -> Result<(), ErrorCode> {
    if policy.version != POLICY_VERSION {
        return Err(ErrorCode::AuthorizationPolicyUnsupported);
    }
    if policy.current_permitted_roots.len()
        + policy.historical_permitted_roots.len()
        + policy.historical_forbidden_roots.len()
        + policy.revoked_roots.len()
        > MAX_REGISTRY_ENTRIES
    {
        return Err(ErrorCode::ResourceLimit);
    }
    for value in [
        policy.record_id.as_str(),
        policy.semantic_version.as_str(),
        policy.declaration.as_str(),
        policy.compatibility_target.as_str(),
    ] {
        validate_text(value)?;
    }
    for digest in [
        policy.proposition_digest.as_str(),
        policy.environment_digest.as_str(),
        policy.record_digest.as_str(),
        policy.proof_build_digest.as_str(),
        policy.axiom_report_digest.as_str(),
        policy.compatibility_digest.as_str(),
    ] {
        validate_digest(digest)?;
    }
    for root in policy
        .current_permitted_roots
        .iter()
        .chain(&policy.historical_permitted_roots)
        .chain(&policy.historical_forbidden_roots)
        .chain(&policy.revoked_roots)
    {
        validate_digest(root)?;
    }
    Ok(())
}

fn validate_record_shape(record: &RegistryRecord) -> Result<(), ErrorCode> {
    if record.id.len() > MAX_IDENTIFIER_BYTES || !valid_identifier(&record.id) {
        return Err(ErrorCode::ResourceLimit);
    }
    for value in [
        record.schema.as_str(),
        record.version.as_str(),
        record.declaration.as_str(),
        record.normalizer.as_str(),
        record.normalization_status.as_str(),
        record.closure.as_str(),
        record.closure_status.as_str(),
        record.policy_version.as_str(),
        record.maturity.as_str(),
        record.exposure.as_str(),
        record.source_anchor.as_str(),
        record.attribution.as_str(),
        record.nonclaims.as_str(),
        record.compatibility_target.as_str(),
        record.compatibility_direction.as_str(),
    ] {
        validate_text(value)?;
    }
    for digest in [
        record.proposition_digest.as_str(),
        record.environment_digest.as_str(),
        record.record_digest.as_str(),
        record.requested_root.as_str(),
        record.proof_build_digest.as_str(),
        record.axiom_report_digest.as_str(),
        record.compatibility_digest.as_str(),
    ] {
        validate_digest(digest)?;
    }
    if record.axiom_count > MAX_AXIOM_ENTRIES {
        return Err(ErrorCode::ResourceLimit);
    }
    if record.registry_entries > MAX_REGISTRY_ENTRIES
        || record.expression_nodes > MAX_EXPRESSION_NODES
        || record.expression_depth > MAX_EXPRESSION_DEPTH
        || record.closure_width > MAX_CLOSURE_WIDTH
        || record.closure_depth > MAX_CLOSURE_DEPTH
        || record.work_nodes > MAX_WORK_NODES
    {
        return Err(ErrorCode::ResourceLimit);
    }
    if record.registry_entries != PUBLISHED_REGISTRY_ENTRIES {
        return Err(ErrorCode::MalformedRecord);
    }
    Ok(())
}

fn classify_root(root: &str, policy: &TrustedPolicy) -> Result<RootStatus, ErrorCode> {
    if policy.revoked_roots.iter().any(|item| item == root) {
        return Err(ErrorCode::AuthorizationRootRevoked);
    }
    if policy
        .historical_forbidden_roots
        .iter()
        .any(|item| item == root)
    {
        return Err(ErrorCode::AuthorizationRootMismatch);
    }
    if policy
        .current_permitted_roots
        .iter()
        .any(|item| item == root)
    {
        return Ok(RootStatus::Current);
    }
    if policy
        .historical_permitted_roots
        .iter()
        .any(|item| item == root)
    {
        return Ok(RootStatus::HistoricalPermitted);
    }
    Err(ErrorCode::AuthorizationRootUnknown)
}

fn take(fields: &BTreeMap<&str, &str>, key: &str) -> Result<String, ErrorCode> {
    fields
        .get(key)
        .map(|value| (*value).to_owned())
        .ok_or(ErrorCode::MalformedRecord)
}

fn parse_count(fields: &BTreeMap<&str, &str>, key: &str) -> Result<usize, ErrorCode> {
    fields
        .get(key)
        .ok_or(ErrorCode::MalformedRecord)?
        .parse::<usize>()
        .map_err(|_| ErrorCode::MalformedRecord)
}

fn validate_text(value: &str) -> Result<(), ErrorCode> {
    if value.is_empty() || value.len() > MAX_STRING_BYTES || value.contains(['\n', '\r', '=']) {
        return Err(ErrorCode::ResourceLimit);
    }
    Ok(())
}

fn validate_digest(value: &str) -> Result<(), ErrorCode> {
    if value.len() != 64
        || !value
            .bytes()
            .all(|byte| byte.is_ascii_digit() || matches!(byte, b'a'..=b'f'))
    {
        return Err(ErrorCode::MalformedRecord);
    }
    Ok(())
}

fn valid_field_name(value: &str) -> bool {
    value
        .bytes()
        .all(|byte| byte.is_ascii_lowercase() || byte == b'_')
}

fn valid_identifier(value: &str) -> bool {
    let mut bytes = value.bytes();
    let Some(first) = bytes.next() else {
        return false;
    };
    (first.is_ascii_lowercase() || first.is_ascii_digit())
        && bytes.all(|byte| {
            byte.is_ascii_lowercase()
                || byte.is_ascii_digit()
                || matches!(byte, b'.' | b'_' | b':' | b'-')
        })
}
