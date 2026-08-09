#![allow(missing_docs)]
#![allow(clippy::expect_used, clippy::panic)]

use sha2::{Digest, Sha256};
use statqed_rust_cbor_prototype::{
    FRAME_MAGIC, FRAMING_ID, Failure, FrameIdentifiers, Key, Limits, MAX_INTEGER, MIN_INTEGER,
    MapEntry, MapOrder, PROFILE_ID, Profile, RawKind, ResultClass, SHA256_ALGORITHM_ID, Value,
    decode, decode_raw, digest_data_free, encode, frame_data_free, hex_encode,
    success_diagnostic_json, validate_raw, validate_raw_with_expectations,
    value_from_diagnostic_json, value_to_diagnostic_json, verify_digest_data_free,
};

fn assert_failure<T: core::fmt::Debug>(
    result: Result<T, Failure>,
    class: ResultClass,
    code: &'static str,
) {
    let failure = result.expect_err("operation unexpectedly succeeded");
    assert_eq!(failure.class, class);
    assert_eq!(failure.code, code);
}

fn megabyte_value() -> Value {
    let mut items = Vec::with_capacity(1_021);
    items.push(Value::Bytes(vec![0; 1_030]));
    for _ in 0..1_020 {
        items.push(Value::Bytes(vec![0; 1_024]));
    }
    Value::Array(items)
}

fn unchecked_frame(identifiers: &FrameIdentifiers<'_>, payload: &[u8]) -> Vec<u8> {
    let components = [
        identifiers.purpose.as_bytes(),
        identifiers.algorithm_id.as_bytes(),
        identifiers.profile_id.as_bytes(),
        identifiers.object_class_schema_id.as_bytes(),
        identifiers.framing_id.as_bytes(),
        payload,
    ];
    let mut frame = FRAME_MAGIC.to_vec();
    for component in components {
        let length = u32::try_from(component.len()).expect("test component length fits u32");
        frame.extend_from_slice(&length.to_be_bytes());
        frame.extend_from_slice(component);
    }
    frame
}

#[test]
fn integer_domain_is_the_full_direct_cbor_range() -> Result<(), Failure> {
    let profile = Profile::default();
    for (value, expected) in [
        (MIN_INTEGER, "3bffffffffffffffff"),
        (-25, "3818"),
        (-24, "37"),
        (23, "17"),
        (24, "1818"),
        (MAX_INTEGER, "1bffffffffffffffff"),
    ] {
        let bytes = encode(&Value::Integer(value), &profile)?;
        assert_eq!(hex_encode(&bytes), expected);
        assert_eq!(decode(&bytes, &profile)?, Value::Integer(value));
    }
    assert_failure(
        encode(&Value::Integer(MIN_INTEGER - 1), &profile),
        ResultClass::SemanticValidity,
        "semantic.integer_range",
    );
    assert_failure(
        encode(&Value::Integer(MAX_INTEGER + 1), &profile),
        ResultClass::SemanticValidity,
        "semantic.integer_range",
    );
    Ok(())
}

#[test]
fn core_order_is_default_and_length_first_is_only_diagnostic() -> Result<(), Failure> {
    let value = Value::Map(vec![
        MapEntry {
            key: Key::Text(String::new()),
            value: Value::Null,
        },
        MapEntry {
            key: Key::Integer(24),
            value: Value::Null,
        },
    ]);
    assert_eq!(
        hex_encode(&encode(&value, &Profile::default())?),
        "a21818f660f6"
    );
    assert_failure(
        decode(&[0xa2, 0x60, 0xf6, 0x18, 0x18, 0xf6], &Profile::default()),
        ResultClass::DeterministicProfile,
        "profile.map_order",
    );

    let diagnostic = Profile {
        map_order: MapOrder::DiagnosticLengthFirst,
        ..Profile::default()
    };
    assert_eq!(hex_encode(&encode(&value, &diagnostic)?), "a260f61818f6");
    Ok(())
}

#[test]
fn raw_map_retains_typed_equivalent_duplicates_before_order_checks() -> Result<(), Failure> {
    let bytes = [0xa2, 0x00, 0xf4, 0x18, 0x00, 0xf5];
    let raw = decode_raw(&bytes, &Limits::default())?;
    let RawKind::Map(entries) = raw.root().kind() else {
        panic!("expected raw map")
    };
    assert_eq!(entries.len(), 2);
    assert_eq!(raw.encoded(entries[0].key()), Some(&[0x00][..]));
    assert_eq!(raw.encoded(entries[1].key()), Some(&[0x18, 0x00][..]));
    assert_failure(
        validate_raw(&raw, &Profile::default()),
        ResultClass::Validity,
        "validity.map_duplicate",
    );
    Ok(())
}

#[test]
fn malformed_validity_expectedness_and_profile_codes_are_exact() {
    let profile = Profile::default();
    for bytes in [&[][..], &[0x18][..]] {
        assert_failure(
            decode(bytes, &profile),
            ResultClass::WellFormedness,
            "wellformed.truncated",
        );
    }
    assert_failure(
        decode(&[0xff], &profile),
        ResultClass::WellFormedness,
        "wellformed.unexpected_break",
    );
    assert_failure(
        decode(&[0x1c], &profile),
        ResultClass::WellFormedness,
        "wellformed.reserved_additional",
    );
    assert_failure(
        decode(&[0xa1, 0x00], &profile),
        ResultClass::WellFormedness,
        "wellformed.map_pair_missing",
    );
    assert_failure(
        decode(&[0x61, 0xff], &profile),
        ResultClass::Validity,
        "validity.invalid_utf8",
    );
    assert_failure(
        decode(&[0x61, 0xff, 0x00], &profile),
        ResultClass::Validity,
        "validity.invalid_utf8",
    );
    assert_failure(
        decode(&[0xa2, 0x00, 0xf4, 0x00, 0xf5, 0x00], &profile),
        ResultClass::Validity,
        "validity.map_duplicate",
    );
    assert_failure(
        decode(&[0x00, 0x00], &profile),
        ResultClass::Expectedness,
        "expected.trailing_bytes",
    );
    assert_failure(
        decode(&[0xa1, 0x40, 0xf6], &profile),
        ResultClass::Expectedness,
        "expected.map_key_type",
    );
    assert_failure(
        decode(&[0x18, 0x00], &profile),
        ResultClass::DeterministicProfile,
        "profile.non_preferred_head",
    );
    assert_failure(
        decode(&[0xf9, 0x00, 0x00], &profile),
        ResultClass::DeterministicProfile,
        "profile.float_forbidden",
    );
    assert_failure(
        decode(&[0xf7], &profile),
        ResultClass::DeterministicProfile,
        "profile.simple_forbidden",
    );
}

#[test]
fn indefinite_string_chunks_count_as_total_items() {
    let profile = Profile::default();
    for (head, empty_chunk) in [(0x5f, 0x40), (0x7f, 0x60)] {
        let mut at_limit = Vec::with_capacity(4_097);
        at_limit.push(head);
        at_limit.extend(core::iter::repeat_n(empty_chunk, 4_095));
        at_limit.push(0xff);
        assert_failure(
            decode(&at_limit, &profile),
            ResultClass::DeterministicProfile,
            "profile.indefinite",
        );

        let mut over_limit = Vec::with_capacity(4_098);
        over_limit.push(head);
        over_limit.extend(core::iter::repeat_n(empty_chunk, 4_096));
        over_limit.push(0xff);
        assert_failure(
            decode(&over_limit, &profile),
            ResultClass::ResourceLimit,
            "resource.total_items",
        );
    }
}

#[test]
fn raw_tree_accessors_are_immutable_and_span_checked() -> Result<(), Failure> {
    let short = decode_raw(&[0x00], &Limits::default())?;
    let longer = decode_raw(&[0x18, 0x18], &Limits::default())?;
    assert_eq!(
        short.root().head_form(),
        statqed_rust_cbor_prototype::HeadForm::Preferred
    );
    assert_eq!(short.root().span(), 0..1);
    assert!(matches!(short.root().kind(), RawKind::Unsigned(0)));
    assert_eq!(short.encoded(short.root()), Some(&[0x00][..]));
    assert_eq!(short.encoded(longer.root()), None);
    Ok(())
}

#[test]
fn indefinite_items_are_fully_parsed_before_profile_rejection() {
    let profile = Profile::default();
    for bytes in [
        &[0x5f, 0x41, 0x00, 0xff][..],
        &[0x7f, 0x61, b'a', 0xff][..],
        &[0x9f, 0x00, 0xff][..],
        &[0xbf, 0x00, 0xf6, 0xff][..],
    ] {
        assert_failure(
            decode(bytes, &profile),
            ResultClass::DeterministicProfile,
            "profile.indefinite",
        );
    }
    assert_failure(
        decode(&[0x5f, 0x61, b'a', 0xff], &profile),
        ResultClass::WellFormedness,
        "wellformed.indefinite_chunk_type",
    );
    assert_failure(
        decode(&[0xbf, 0x00, 0xff], &profile),
        ResultClass::WellFormedness,
        "wellformed.map_pair_missing",
    );
    assert_failure(
        decode(&[0x9f, 0xa2, 0x00, 0xf4, 0x00, 0xf5, 0xff], &profile),
        ResultClass::Validity,
        "validity.map_duplicate",
    );
}

#[test]
fn tags_are_not_interpreted_and_share_the_structural_depth_bound() {
    let profile = Profile::default();
    for bytes in [
        &[0xc2, 0x00][..],
        &[0xc2, 0x41, 0x01][..],
        &[0xc4, 0x82, 0x00, 0x01][..],
        &[0xd8, 0x1e, 0x82, 0x01, 0x02][..],
    ] {
        assert_failure(
            decode(bytes, &profile),
            ResultClass::DeterministicProfile,
            "profile.tag_forbidden",
        );
    }
    assert_failure(
        decode(&[0xd8, 0x00, 0x00], &profile),
        ResultClass::DeterministicProfile,
        "profile.non_preferred_head",
    );
    assert_failure(
        decode(&[0xc0, 0xa2, 0x00, 0xf4, 0x00, 0xf5], &profile),
        ResultClass::Validity,
        "validity.map_duplicate",
    );

    let mut accepted_depth = vec![0xc0; 32];
    accepted_depth.push(0xf6);
    assert_failure(
        decode(&accepted_depth, &profile),
        ResultClass::DeterministicProfile,
        "profile.tag_forbidden",
    );
    let mut rejected_depth = vec![0xc0; 33];
    rejected_depth.push(0xf6);
    assert_failure(
        decode(&rejected_depth, &profile),
        ResultClass::ResourceLimit,
        "resource.depth",
    );
}

#[test]
fn caller_expectations_precede_deterministic_profile_checks() -> Result<(), Failure> {
    let raw = decode_raw(&[0x18, 0x00], &Limits::default())?;
    assert_failure(
        validate_raw_with_expectations(&raw, &Profile::default(), Some("other"), None),
        ResultClass::Expectedness,
        "expected.profile_id",
    );
    assert_failure(
        validate_raw_with_expectations(&raw, &Profile::default(), Some(PROFILE_ID), Some("map")),
        ResultClass::Expectedness,
        "expected.top_level",
    );
    Ok(())
}

#[test]
fn resource_bounds_apply_to_parser_encoder_and_diagnostics() {
    let mut profile = Profile::default();
    profile.limits.max_input_bytes = 0;
    assert_failure(
        decode(&[0x00], &profile),
        ResultClass::ResourceLimit,
        "resource.input_bytes",
    );

    let mut profile = Profile::default();
    profile.limits.max_output_bytes = 0;
    assert_failure(
        encode(&Value::Null, &profile),
        ResultClass::ResourceLimit,
        "resource.output_bytes",
    );

    let mut profile = Profile::default();
    profile.limits.max_nesting_depth = 0;
    assert_failure(
        decode(&[0x81, 0x00], &profile),
        ResultClass::ResourceLimit,
        "resource.depth",
    );

    let limits = Limits {
        max_diagnostic_output_bytes: 1,
        ..Limits::default()
    };
    assert_failure(
        success_diagnostic_json(&[0xf6], &Value::Null, &limits),
        ResultClass::ResourceLimit,
        "resource.diagnostic_bytes",
    );

    let over_hard_cap = Limits {
        max_output_bytes: 1_048_577,
        ..Limits::default()
    };
    assert_failure(
        decode_raw(&[0xf6], &over_hard_cap),
        ResultClass::ResourceLimit,
        "resource.output_bytes",
    );
}

#[test]
fn canonical_megabyte_boundary_is_accepted_without_diagnostic_projection() -> Result<(), Failure> {
    let value = megabyte_value();
    let encoded = encode(&value, &Profile::default())?;
    assert_eq!(encoded.len(), 1_048_576);
    assert_eq!(decode(&encoded, &Profile::default())?, value);
    assert_failure(
        success_diagnostic_json(&encoded, &value, &Limits::default()),
        ResultClass::ResourceLimit,
        "resource.diagnostic_bytes",
    );

    let mut smaller_output = Profile::default();
    smaller_output.limits.max_output_bytes = 1_048_575;
    assert_failure(
        encode(&value, &smaller_output),
        ResultClass::ResourceLimit,
        "resource.output_bytes",
    );
    Ok(())
}

#[test]
fn semantic_duplicate_and_unicode_rules_are_enforced() -> Result<(), Failure> {
    let duplicate = Value::Map(vec![
        MapEntry {
            key: Key::Text("x".to_owned()),
            value: Value::Null,
        },
        MapEntry {
            key: Key::Text("x".to_owned()),
            value: Value::Boolean(false),
        },
    ]);
    assert_failure(
        encode(&duplicate, &Profile::default()),
        ResultClass::SemanticValidity,
        "semantic.map_duplicate",
    );

    assert_failure(
        value_from_diagnostic_json(
            br#"{"type":"map","entries":[{"key":{"type":"boolean","value":true},"value":{"type":"null"}}]}"#,
        ),
        ResultClass::SemanticValidity,
        "semantic.map_key_type",
    );

    let composed = Value::Text("é".to_owned());
    let decomposed = Value::Text("e\u{301}".to_owned());
    assert_ne!(
        encode(&composed, &Profile::default())?,
        encode(&decomposed, &Profile::default())?
    );
    assert_eq!(
        decode(
            &encode(&composed, &Profile::default())?,
            &Profile::default()
        )?,
        composed
    );
    assert_eq!(
        decode(
            &encode(&decomposed, &Profile::default())?,
            &Profile::default()
        )?,
        decomposed
    );
    Ok(())
}

#[test]
fn framing_is_exact_bounded_and_binds_all_components() -> Result<(), Failure> {
    let limits = Limits::default();
    let identifiers = FrameIdentifiers::sha256("test.manifest", "test.object-v1");
    let frame = frame_data_free(&identifiers, &[0xf6], &limits)?;
    assert!(frame.starts_with(FRAME_MAGIC));
    assert_eq!(FRAME_MAGIC.len(), 15);
    assert_eq!(FRAMING_ID, "statqed.digest-lp.v1");
    assert_ne!(
        digest_data_free(&identifiers, &[0xf6], &limits)?,
        digest_data_free(
            &FrameIdentifiers::sha256("test.other", "test.object-v1"),
            &[0xf6],
            &limits,
        )?
    );

    let max_identifier = "t".repeat(128);
    let maximum = FrameIdentifiers::sha256(&max_identifier, &max_identifier);
    let maximum_payload = encode(&megabyte_value(), &Profile::default())?;
    let maximum_frame = frame_data_free(&maximum, &maximum_payload, &limits)?;
    assert_eq!(maximum_frame.len(), 1_048_918);
    assert_failure(
        frame_data_free(&maximum, &vec![0; 1_048_577], &limits),
        ResultClass::DigestVerification,
        "digest.length",
    );
    Ok(())
}

#[test]
fn framing_matches_the_independently_transcribed_baseline() -> Result<(), Failure> {
    let identifiers = FrameIdentifiers::sha256("test.fixture", "test.semantic-value.v1");
    let frame = frame_data_free(&identifiers, &[0x00], &Limits::default())?;
    assert_eq!(
        hex_encode(&frame),
        "537461745145442d446967657374000000000c746573742e66697874757265000000077368612d32353600000014737461747165642e63626f722d636f72652e763100000016746573742e73656d616e7469632d76616c75652e763100000014737461747165642e6469676573742d6c702e76310000000100"
    );
    assert_eq!(frame.len(), 121);
    Ok(())
}

#[test]
fn framing_identifier_grammar_and_fixed_ids_are_exact() {
    let limits = Limits::default();
    let base = FrameIdentifiers::sha256("test.manifest", "test.object-v1");
    for purpose in ["", "Upper", ".leading", "contains/slash"] {
        let identifiers = FrameIdentifiers { purpose, ..base };
        assert_failure(
            frame_data_free(&identifiers, &[0xf6], &limits),
            ResultClass::DigestVerification,
            "digest.purpose",
        );
    }
    assert_failure(
        frame_data_free(
            &FrameIdentifiers {
                algorithm_id: "sha-512",
                ..base
            },
            &[0xf6],
            &limits,
        ),
        ResultClass::DigestVerification,
        "digest.algorithm",
    );
    assert_eq!(base.algorithm_id, SHA256_ALGORITHM_ID);
}

#[test]
fn digest_verification_has_stable_mutation_failures() -> Result<(), Failure> {
    let profile = Profile::default();
    let identifiers = FrameIdentifiers::sha256("test.manifest", "test.object-v1");
    let frame = frame_data_free(&identifiers, &[0xf6], &profile.limits)?;
    let digest = digest_data_free(&identifiers, &[0xf6], &profile.limits)?;
    let verified = verify_digest_data_free(&identifiers, &frame, &digest, &profile)?;
    assert_eq!(verified.payload, &[0xf6]);
    assert_eq!(verified.value, Value::Null);

    let mut bad_magic = frame.clone();
    bad_magic[0] ^= 1;
    assert_failure(
        verify_digest_data_free(&identifiers, &bad_magic, &digest, &profile),
        ResultClass::DigestVerification,
        "digest.magic",
    );
    assert_failure(
        verify_digest_data_free(&identifiers, FRAME_MAGIC, &digest, &profile),
        ResultClass::DigestVerification,
        "digest.component_length",
    );
    let mut trailing = frame.clone();
    trailing.push(0);
    assert_failure(
        verify_digest_data_free(&identifiers, &trailing, &digest, &profile),
        ResultClass::DigestVerification,
        "digest.trailing_bytes",
    );
    assert_failure(
        verify_digest_data_free(&identifiers, &frame, &digest[..31], &profile),
        ResultClass::DigestVerification,
        "digest.length",
    );
    let mut mismatch = digest;
    mismatch[0] ^= 1;
    assert_failure(
        verify_digest_data_free(&identifiers, &frame, &mismatch, &profile),
        ResultClass::DigestVerification,
        "digest.mismatch",
    );

    let invalid_payload = [0x18, 0x00];
    assert_failure(
        frame_data_free(&identifiers, &invalid_payload, &profile.limits),
        ResultClass::DigestVerification,
        "digest.payload",
    );
    let invalid_frame = unchecked_frame(&identifiers, &invalid_payload);
    let invalid_digest: [u8; 32] = Sha256::digest(&invalid_frame).into();
    assert_failure(
        verify_digest_data_free(&identifiers, &invalid_frame, &invalid_digest, &profile),
        ResultClass::DigestVerification,
        "digest.payload",
    );
    Ok(())
}

#[test]
fn digest_schema_identifier_is_bound_but_not_resolved() -> Result<(), Failure> {
    let profile = Profile::default();
    let identifiers = FrameIdentifiers::sha256("test.binding-only", "test.must-be-text.v1");
    // Integer(0) deliberately contradicts the test label. Generic framing
    // binds that exact label but makes no schema-resolution/conformance claim.
    let frame = frame_data_free(&identifiers, &[0x00], &profile.limits)?;
    let digest = digest_data_free(&identifiers, &[0x00], &profile.limits)?;
    let verified = verify_digest_data_free(&identifiers, &frame, &digest, &profile)?;
    assert_eq!(verified.payload, &[0x00]);
    assert_eq!(verified.value, Value::Integer(0));
    Ok(())
}

#[test]
fn typed_json_uses_decimal_strings_and_full_integer_edges() -> Result<(), Failure> {
    for integer in [MIN_INTEGER, MAX_INTEGER] {
        let input = format!(r#"{{"type":"integer","value":"{integer}"}}"#);
        assert_eq!(
            value_from_diagnostic_json(input.as_bytes())?,
            Value::Integer(integer)
        );
    }
    assert_failure(
        value_from_diagnostic_json(br#"{"type":"integer","value":"18446744073709551616"}"#),
        ResultClass::SemanticValidity,
        "semantic.integer_range",
    );
    assert_failure(
        value_from_diagnostic_json(br#"{"type":"integer","value":24}"#),
        ResultClass::SemanticValidity,
        "semantic.unsupported_value",
    );
    let value = Value::Array(vec![Value::Bytes(vec![0, 255]), Value::Null]);
    assert_eq!(
        value_from_diagnostic_json(value_to_diagnostic_json(&value).to_string().as_bytes())?,
        value
    );
    Ok(())
}

#[test]
fn typed_json_preflight_and_conversion_bounds_are_stable() -> Result<(), Failure> {
    fn nested_typed_arrays(wrappers: usize) -> Vec<u8> {
        let mut input = Vec::with_capacity(wrappers * 27 + 15);
        for _ in 0..wrappers {
            input.extend_from_slice(br#"{"type":"array","items":["#);
        }
        input.extend_from_slice(br#"{"type":"null"}"#);
        for _ in 0..wrappers {
            input.extend_from_slice(b"]}");
        }
        input
    }

    let at_semantic_depth = nested_typed_arrays(32);
    let mut expected = Value::Null;
    for _ in 0..32 {
        expected = Value::Array(vec![expected]);
    }
    assert_eq!(value_from_diagnostic_json(&at_semantic_depth)?, expected);
    assert_failure(
        value_from_diagnostic_json(&nested_typed_arrays(33)),
        ResultClass::ResourceLimit,
        "resource.depth",
    );
    assert_failure(
        value_from_diagnostic_json(&nested_typed_arrays(2_000)),
        ResultClass::ResourceLimit,
        "resource.depth",
    );

    // A depth-32 map projection reaches 97 raw JSON object/array levels.
    // The scanner admits that necessary ceiling and rejects the next level
    // before serde's recursion behavior can affect the result.
    let at_raw_depth = format!("{}0{}", "[".repeat(97), "]".repeat(97));
    assert_failure(
        value_from_diagnostic_json(at_raw_depth.as_bytes()),
        ResultClass::Expectedness,
        "expected.top_level",
    );
    let beyond_raw_depth = format!("{}0{}", "[".repeat(98), "]".repeat(98));
    assert_failure(
        value_from_diagnostic_json(beyond_raw_depth.as_bytes()),
        ResultClass::ResourceLimit,
        "resource.depth",
    );

    let at_integer_token_boundary = br#"{"type":"integer","value":99999999999999999999}"#;
    assert_failure(
        value_from_diagnostic_json(at_integer_token_boundary),
        ResultClass::SemanticValidity,
        "semantic.unsupported_value",
    );
    let beyond_integer_token_boundary = br#"{"type":"integer","value":999999999999999999999}"#;
    assert_failure(
        value_from_diagnostic_json(beyond_integer_token_boundary),
        ResultClass::SemanticValidity,
        "semantic.unsupported_value",
    );
    assert_failure(
        value_from_diagnostic_json(br#"{"type":"integer","value":999999999999999999999.0}"#),
        ResultClass::SemanticValidity,
        "semantic.unsupported_value",
    );

    let quoted_digits = "9".repeat(5_000);
    let quoted_integer = format!(r#"{{"type":"integer","value":"{quoted_digits}"}}"#);
    assert_failure(
        value_from_diagnostic_json(quoted_integer.as_bytes()),
        ResultClass::SemanticValidity,
        "semantic.integer_range",
    );
    let escaped_text = format!(
        r#"{{"type":"text","value":"\"{}[[[[{{{{\\\"still text"}}"#,
        "9".repeat(100)
    );
    assert!(matches!(
        value_from_diagnostic_json(escaped_text.as_bytes()),
        Ok(Value::Text(_))
    ));
    Ok(())
}

#[test]
fn typed_json_conversion_checks_collection_total_and_string_limits() {
    fn null_array(items: usize) -> Vec<u8> {
        let mut input = Vec::with_capacity(25 + items * 16);
        input.extend_from_slice(br#"{"type":"array","items":["#);
        for index in 0..items {
            if index != 0 {
                input.push(b',');
            }
            input.extend_from_slice(br#"{"type":"null"}"#);
        }
        input.extend_from_slice(b"]}");
        input
    }

    fn total_items_projection(last_inner_items: usize) -> Vec<u8> {
        let mut input = br#"{"type":"array","items":["#.to_vec();
        for (index, items) in [1_023, 1_023, 1_023, last_inner_items]
            .into_iter()
            .enumerate()
        {
            if index != 0 {
                input.push(b',');
            }
            input.extend_from_slice(&null_array(items));
        }
        input.extend_from_slice(b"]}");
        input
    }

    assert!(matches!(
        value_from_diagnostic_json(&null_array(1_024)),
        Ok(Value::Array(items)) if items.len() == 1_024
    ));
    assert_failure(
        value_from_diagnostic_json(&null_array(1_025)),
        ResultClass::ResourceLimit,
        "resource.array_items",
    );

    let mut map = br#"{"type":"map","entries":["#.to_vec();
    for index in 0..1_024 {
        if index != 0 {
            map.push(b',');
        }
        map.extend_from_slice(
            format!(
                r#"{{"key":{{"type":"integer","value":"{index}"}},"value":{{"type":"null"}}}}"#
            )
            .as_bytes(),
        );
    }
    map.extend_from_slice(b"]}");
    assert!(matches!(
        value_from_diagnostic_json(&map),
        Ok(Value::Map(entries)) if entries.len() == 1_024
    ));
    let insert_at = map.len() - 2;
    map.splice(
        insert_at..insert_at,
        br#",{"key":{"type":"integer","value":"1024"},"value":{"type":"null"}}"#
            .iter()
            .copied(),
    );
    assert_failure(
        value_from_diagnostic_json(&map),
        ResultClass::ResourceLimit,
        "resource.map_entries",
    );

    assert!(value_from_diagnostic_json(&total_items_projection(1_022)).is_ok());
    assert_failure(
        value_from_diagnostic_json(&total_items_projection(1_023)),
        ResultClass::ResourceLimit,
        "resource.total_items",
    );

    let at_text_limit = format!(r#"{{"type":"text","value":"{}"}}"#, "x".repeat(65_536));
    assert!(value_from_diagnostic_json(at_text_limit.as_bytes()).is_ok());
    let beyond_text_limit = format!(r#"{{"type":"text","value":"{}"}}"#, "x".repeat(65_537));
    assert_failure(
        value_from_diagnostic_json(beyond_text_limit.as_bytes()),
        ResultClass::ResourceLimit,
        "resource.string_bytes",
    );
    let at_bytes_limit = format!(r#"{{"type":"bytes","hex":"{}"}}"#, "00".repeat(65_536));
    assert!(value_from_diagnostic_json(at_bytes_limit.as_bytes()).is_ok());
    let beyond_bytes_limit = format!(r#"{{"type":"bytes","hex":"{}"}}"#, "00".repeat(65_537));
    assert_failure(
        value_from_diagnostic_json(beyond_bytes_limit.as_bytes()),
        ResultClass::ResourceLimit,
        "resource.string_bytes",
    );
}

#[test]
fn unsupported_typed_constructors_have_exact_semantic_codes() {
    for (input, code) in [
        (
            br#"{"type":"bignum","value":"18446744073709551616"}"#.as_slice(),
            "semantic.unsupported_bignum",
        ),
        (
            br#"{"kind":"bignum","decimal":"18446744073709551616"}"#.as_slice(),
            "semantic.unsupported_bignum",
        ),
        (
            br#"{"type":"rational","numerator":"1","denominator":"2"}"#.as_slice(),
            "semantic.unsupported_rational",
        ),
        (
            br#"{"type":"rational","numerator":"2","denominator":"4"}"#.as_slice(),
            "semantic.rational_invalid",
        ),
        (
            br#"{"type":"decimal","coefficient":"12","exponent":"-1"}"#.as_slice(),
            "semantic.unsupported_decimal",
        ),
        (
            br#"{"type":"decimal","coefficient":"1200","exponent":"-2"}"#.as_slice(),
            "semantic.decimal_non_normal",
        ),
        (
            br#"{"type":"ieee_bits","width":64,"bits_hex":"8000000000000000"}"#.as_slice(),
            "semantic.unsupported_ieee_bits",
        ),
        (
            br#"{"type":"interval","endpoint_kind":"integer","lower":"1","upper":"2","closure":"closed"}"#.as_slice(),
            "semantic.unsupported_interval",
        ),
        (
            br#"{"type":"interval","endpoint_kind":"integer","lower":"1","upper":"2","closure":"left_closed"}"#.as_slice(),
            "semantic.unsupported_interval",
        ),
        (
            br#"{"type":"interval","endpoint_kind":"integer","lower":"1","upper":"1","closure":"closed"}"#.as_slice(),
            "semantic.unsupported_interval",
        ),
        (
            br#"{"type":"interval","endpoint_kind":"integer","lower":"1","upper":"1","closure":"open"}"#.as_slice(),
            "semantic.interval_invalid",
        ),
        (
            br#"{"type":"interval","endpoint_kind":"integer","lower":"1","upper":"2","closure":"left_open"}"#.as_slice(),
            "semantic.interval_invalid",
        ),
        (
            br#"{"type":"interval","endpoint_kind":"integer","lower":"2","upper":"1","closure":"closed"}"#.as_slice(),
            "semantic.interval_invalid",
        ),
        (
            br#"{"type":"interval","lower":{"type":"integer","value":"2"},"upper":{"type":"integer","value":"1"},"closure":"closed"}"#.as_slice(),
            "semantic.interval_invalid",
        ),
        (
            br#"{"kind":"interval","lower":{"kind":"integer","decimal":"1"},"upper":{"kind":"decimal","coefficient":"2","exponent":"0"},"closure":"closed"}"#.as_slice(),
            "semantic.interval_invalid",
        ),
        (
            br#"{"type":"extension","type_id":"test.one","critical":false,"body":{"type":"null"}}"#.as_slice(),
            "semantic.extension_noncritical_unsupported",
        ),
    ] {
        assert_failure(
            value_from_diagnostic_json(input),
            ResultClass::SemanticValidity,
            code,
        );
    }
}

#[test]
fn extension_sequence_scans_duplicates_then_aggregate_criticality() {
    let duplicate_after_critical = br#"{"type":"extension_sequence","extensions":[{"type_id":"test.critical","critical":true,"body":{"type":"null"}},{"type_id":"test.same","critical":false,"body":{"type":"null"}},{"type_id":"test.same","critical":false,"body":{"type":"integer","value":"1"}}]}"#;
    assert_failure(
        value_from_diagnostic_json(duplicate_after_critical),
        ResultClass::SemanticValidity,
        "semantic.extension_duplicate",
    );
    for input in [
        br#"{"type":"extension_sequence","extensions":[{"type_id":"test.critical","critical":true,"body":{"type":"null"}},{"type_id":"test.other","critical":false,"body":{"type":"null"}}]}"#.as_slice(),
        br#"{"type":"extension_sequence","extensions":[{"type_id":"test.other","critical":false,"body":{"type":"null"}},{"type_id":"test.critical","critical":true,"body":{"type":"null"}}]}"#.as_slice(),
    ] {
        assert_failure(
            value_from_diagnostic_json(input),
            ResultClass::SemanticValidity,
            "semantic.extension_critical_unknown",
        );
    }
    assert_failure(
        value_from_diagnostic_json(
            br#"{"type":"extension_sequence","extensions":[{"type":"extension","type_id":"test.unknown","critical":false,"body":{"type":"null"}}]}"#,
        ),
        ResultClass::SemanticValidity,
        "semantic.extension_noncritical_unsupported",
    );
}
