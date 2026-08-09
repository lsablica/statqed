//! Deterministic, non-normative typed-JSON/hex conformance CLI.

#![forbid(unsafe_code)]

use std::io::{self, Read, Write};
use std::process::ExitCode;

use serde_json::{Map as JsonMap, Value as JsonValue};
use statqed_rust_cbor_prototype::{
    Failure, FrameIdentifiers, Profile, ResultClass, decode, decode_raw,
    diagnostic_json_with_limit, digest_data_free, failure_diagnostic_json, frame_data_free,
    hex_decode, hex_encode, success_diagnostic_json, validate_raw_with_expectations,
    value_from_diagnostic_json, value_to_diagnostic_json, verify_digest_data_free,
};

const CLI_INPUT_LIMIT: usize = 2_200_000;
const EVIDENCE_JSON_OUTPUT_LIMIT: usize = 8 * 1_048_576;

enum CommandOutput {
    Diagnostic(String),
    Evidence(Vec<u8>),
}

fn expected_failure(code: &'static str) -> Failure {
    Failure {
        class: ResultClass::Expectedness,
        code,
        offset: 0,
    }
}

fn read_stdin() -> Result<Vec<u8>, Failure> {
    let mut input = Vec::new();
    io::stdin()
        .lock()
        .take((CLI_INPUT_LIMIT + 1) as u64)
        .read_to_end(&mut input)
        .map_err(|_| expected_failure("expected.top_level"))?;
    if input.len() > CLI_INPUT_LIMIT {
        Err(Failure {
            class: ResultClass::ResourceLimit,
            code: "resource.input_bytes",
            offset: 0,
        })
    } else {
        Ok(input)
    }
}

fn parse_object(input: &[u8]) -> Result<JsonMap<String, JsonValue>, Failure> {
    serde_json::from_slice::<JsonValue>(input)
        .map_err(|_| expected_failure("expected.top_level"))?
        .as_object()
        .cloned()
        .ok_or_else(|| expected_failure("expected.top_level"))
}

fn exact_fields(object: &JsonMap<String, JsonValue>, required: &[&str], optional: &[&str]) -> bool {
    required.iter().all(|field| object.contains_key(*field))
        && object
            .keys()
            .all(|field| required.contains(&field.as_str()) || optional.contains(&field.as_str()))
}

fn text_field<'a>(object: &'a JsonMap<String, JsonValue>, field: &str) -> Result<&'a str, Failure> {
    object
        .get(field)
        .and_then(JsonValue::as_str)
        .ok_or_else(|| expected_failure("expected.top_level"))
}

fn emit(line: &str) -> ExitCode {
    if writeln!(io::stdout().lock(), "{line}").is_err() {
        ExitCode::from(3)
    } else {
        ExitCode::SUCCESS
    }
}

fn emit_evidence(bytes: &[u8]) -> ExitCode {
    if io::stdout().lock().write_all(bytes).is_err() {
        ExitCode::from(3)
    } else {
        ExitCode::SUCCESS
    }
}

fn emit_failure(failure: &Failure, profile: &Profile) -> ExitCode {
    let line = failure_diagnostic_json(failure, &profile.limits).unwrap_or_else(|_| {
        "{\"code\":\"resource.diagnostic_bytes\",\"offset\":0,\"result_class\":\"resource\"}"
            .to_owned()
    });
    let emitted = emit(&line);
    if emitted == ExitCode::SUCCESS {
        ExitCode::from(2)
    } else {
        emitted
    }
}

fn frame_identifiers(object: &JsonMap<String, JsonValue>) -> Result<FrameIdentifiers<'_>, Failure> {
    Ok(FrameIdentifiers {
        purpose: text_field(object, "purpose_id")?,
        algorithm_id: text_field(object, "algorithm_id")?,
        profile_id: text_field(object, "profile_id")?,
        object_class_schema_id: text_field(object, "object_class_schema_id")?,
        framing_id: text_field(object, "framing_id")?,
    })
}

fn frame_success_json(
    frame: &[u8],
    digest: &[u8],
    payload: &[u8],
    value: &statqed_rust_cbor_prototype::Value,
    profile: &Profile,
) -> Result<String, Failure> {
    let mut output = JsonMap::new();
    output.insert(
        "cbor_hex".to_owned(),
        JsonValue::String(hex_encode(payload)),
    );
    output.insert("code".to_owned(), JsonValue::String("accepted".to_owned()));
    output.insert(
        "digest_hex".to_owned(),
        JsonValue::String(hex_encode(digest)),
    );
    output.insert("frame_hex".to_owned(), JsonValue::String(hex_encode(frame)));
    output.insert(
        "profile_id".to_owned(),
        JsonValue::String(statqed_rust_cbor_prototype::PROFILE_ID.to_owned()),
    );
    output.insert(
        "result_class".to_owned(),
        JsonValue::String("accepted".to_owned()),
    );
    output.insert("value".to_owned(), value_to_diagnostic_json(value));
    diagnostic_json_with_limit(&JsonValue::Object(output), &profile.limits)
}

fn run_encode(input: &[u8], profile: &Profile) -> Result<String, Failure> {
    let value = value_from_diagnostic_json(input)?;
    let bytes = statqed_rust_cbor_prototype::encode(&value, profile)?;
    let accepted = decode(&bytes, profile)?;
    success_diagnostic_json(&bytes, &accepted, &profile.limits)
}

fn run_encode_raw(input: &[u8], profile: &Profile) -> Result<Vec<u8>, Failure> {
    let value = value_from_diagnostic_json(input)?;
    statqed_rust_cbor_prototype::encode(&value, profile)
}

fn decode_request(
    input: &[u8],
    profile: &Profile,
) -> Result<(Vec<u8>, statqed_rust_cbor_prototype::Value), Failure> {
    let object = parse_object(input)?;
    if !exact_fields(
        &object,
        &["cbor_hex"],
        &["profile_id", "expected_top_level"],
    ) {
        return Err(expected_failure("expected.top_level"));
    }
    let bytes = hex_decode(text_field(&object, "cbor_hex")?)?;
    let document = decode_raw(&bytes, &profile.limits)?;
    let expected_profile = object.get("profile_id").and_then(JsonValue::as_str);
    if object.contains_key("profile_id") && expected_profile.is_none() {
        return Err(expected_failure("expected.profile_id"));
    }
    let expected_top = object.get("expected_top_level").and_then(JsonValue::as_str);
    if object.contains_key("expected_top_level") && expected_top.is_none() {
        return Err(expected_failure("expected.top_level"));
    }
    let value = validate_raw_with_expectations(&document, profile, expected_profile, expected_top)?;
    Ok((bytes, value))
}

fn run_decode(input: &[u8], profile: &Profile) -> Result<String, Failure> {
    let (bytes, value) = decode_request(input, profile)?;
    success_diagnostic_json(&bytes, &value, &profile.limits)
}

fn run_decode_raw(input: &[u8], profile: &Profile) -> Result<Vec<u8>, Failure> {
    let (_, value) = decode_request(input, profile)?;
    let output = serde_json::to_vec(&value_to_diagnostic_json(&value))
        .map_err(|_| expected_failure("expected.top_level"))?;
    if output.len() > EVIDENCE_JSON_OUTPUT_LIMIT {
        Err(Failure {
            class: ResultClass::ResourceLimit,
            code: "resource.output_bytes",
            offset: 0,
        })
    } else {
        Ok(output)
    }
}

fn run_frame(input: &[u8], profile: &Profile) -> Result<String, Failure> {
    let object = parse_object(input)?;
    let required = [
        "purpose_id",
        "algorithm_id",
        "profile_id",
        "object_class_schema_id",
        "framing_id",
        "cbor_hex",
    ];
    if !exact_fields(&object, &required, &[]) {
        return Err(expected_failure("expected.top_level"));
    }
    let payload = hex_decode(text_field(&object, "cbor_hex")?)?;
    let identifiers = frame_identifiers(&object)?;
    let frame = frame_data_free(&identifiers, &payload, &profile.limits)?;
    let value = decode(&payload, profile)?;
    let digest = digest_data_free(&identifiers, &payload, &profile.limits)?;
    frame_success_json(&frame, &digest, &payload, &value, profile)
}

fn run_frame_raw(input: &[u8], profile: &Profile) -> Result<Vec<u8>, Failure> {
    let object = parse_object(input)?;
    let required = [
        "purpose_id",
        "algorithm_id",
        "profile_id",
        "object_class_schema_id",
        "framing_id",
        "cbor_hex",
    ];
    if !exact_fields(&object, &required, &[]) {
        return Err(expected_failure("expected.top_level"));
    }
    let payload = hex_decode(text_field(&object, "cbor_hex")?)?;
    let identifiers = frame_identifiers(&object)?;
    frame_data_free(&identifiers, &payload, &profile.limits)
}

fn run_verify(input: &[u8], profile: &Profile) -> Result<String, Failure> {
    let object = parse_object(input)?;
    let required = [
        "purpose_id",
        "algorithm_id",
        "profile_id",
        "object_class_schema_id",
        "framing_id",
        "frame_hex",
        "digest_hex",
    ];
    if !exact_fields(&object, &required, &[]) {
        return Err(expected_failure("expected.top_level"));
    }
    let frame = hex_decode(text_field(&object, "frame_hex")?)?;
    let digest = hex_decode(text_field(&object, "digest_hex")?)?;
    let identifiers = frame_identifiers(&object)?;
    let verified = verify_digest_data_free(&identifiers, &frame, &digest, profile)?;
    frame_success_json(&frame, &digest, &verified.payload, &verified.value, profile)
}

fn run() -> ExitCode {
    let profile = Profile::default();
    let mut arguments = std::env::args_os();
    let _program = arguments.next();
    let command = arguments.next();
    if arguments.next().is_some() {
        return emit_failure(&expected_failure("expected.top_level"), &profile);
    }
    let result = read_stdin().and_then(|input| {
        match command.as_deref().and_then(|argument| argument.to_str()) {
            Some("encode") => run_encode(&input, &profile).map(CommandOutput::Diagnostic),
            Some("decode") => run_decode(&input, &profile).map(CommandOutput::Diagnostic),
            Some("frame") => run_frame(&input, &profile).map(CommandOutput::Diagnostic),
            Some("verify-digest") => run_verify(&input, &profile).map(CommandOutput::Diagnostic),
            Some("encode-raw") => run_encode_raw(&input, &profile).map(CommandOutput::Evidence),
            Some("decode-raw") => run_decode_raw(&input, &profile).map(CommandOutput::Evidence),
            Some("frame-raw") => run_frame_raw(&input, &profile).map(CommandOutput::Evidence),
            _ => Err(expected_failure("expected.top_level")),
        }
    });
    match result {
        Ok(CommandOutput::Diagnostic(line)) => emit(&line),
        Ok(CommandOutput::Evidence(bytes)) => emit_evidence(&bytes),
        Err(failure) => emit_failure(&failure, &profile),
    }
}

fn main() -> ExitCode {
    run()
}
