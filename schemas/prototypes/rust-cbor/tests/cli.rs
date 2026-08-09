#![allow(missing_docs)]
#![allow(clippy::expect_used)]

use std::io::{self, Write};
use std::process::{Command, Output, Stdio};

use serde_json::Value as JsonValue;

fn invoke(command: &str, input: &[u8]) -> io::Result<Output> {
    let mut child = Command::new(env!("CARGO_BIN_EXE_statqed-rust-cbor-prototype"))
        .arg(command)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()?;
    let Some(mut stdin) = child.stdin.take() else {
        return Err(io::Error::other("child stdin unavailable"));
    };
    stdin.write_all(input)?;
    drop(stdin);
    child.wait_with_output()
}

fn json_output(output: &Output) -> JsonValue {
    assert!(output.stderr.is_empty());
    assert_eq!(output.stdout.last(), Some(&b'\n'));
    assert!(!output.stdout[..output.stdout.len() - 1].contains(&b'\n'));
    serde_json::from_slice(&output.stdout).expect("CLI output must be JSON")
}

#[test]
fn encode_cli_has_stable_one_line_output() -> io::Result<()> {
    let input = br#"{"type":"map","entries":[{"key":{"type":"text","value":""},"value":{"type":"integer","value":"0"}},{"key":{"type":"integer","value":"24"},"value":{"type":"integer","value":"0"}}]}"#;
    let output = invoke("encode", input)?;
    assert!(output.status.success());
    assert!(output.stderr.is_empty());
    assert_eq!(
        output.stdout,
        b"{\"cbor_hex\":\"a21818006000\",\"code\":\"accepted\",\"profile_id\":\"statqed.cbor-core.v1\",\"result_class\":\"accepted\",\"value\":{\"entries\":[{\"key\":{\"type\":\"integer\",\"value\":\"24\"},\"value\":{\"type\":\"integer\",\"value\":\"0\"}},{\"key\":{\"type\":\"text\",\"value\":\"\"},\"value\":{\"type\":\"integer\",\"value\":\"0\"}}],\"type\":\"map\"}}\n"
    );
    Ok(())
}

#[test]
fn decode_cli_accepts_request_envelope_and_reports_exact_failure() -> io::Result<()> {
    let accepted = invoke(
        "decode",
        br#"{"cbor_hex":"a21864f620f6","profile_id":"statqed.cbor-core.v1","expected_top_level":"map"}"#,
    )?;
    assert!(accepted.status.success());
    let accepted_json = json_output(&accepted);
    assert_eq!(accepted_json["result_class"], "accepted");
    assert_eq!(accepted_json["code"], "accepted");
    assert_eq!(accepted_json["cbor_hex"], "a21864f620f6");

    let rejected = invoke("decode", br#"{"cbor_hex":"a260f61818f6"}"#)?;
    assert_eq!(rejected.status.code(), Some(2));
    assert_eq!(
        rejected.stdout,
        b"{\"code\":\"profile.map_order\",\"offset\":3,\"result_class\":\"deterministic_profile\"}\n"
    );
    Ok(())
}

#[test]
fn decode_cli_preserves_validity_before_trailing_and_chunk_resource_precedence() -> io::Result<()> {
    for (cbor_hex, expected_code) in [
        ("61ff00", "validity.invalid_utf8"),
        ("a200f400f500", "validity.map_duplicate"),
    ] {
        let request = format!("{{\"cbor_hex\":\"{cbor_hex}\"}}");
        let output = invoke("decode", request.as_bytes())?;
        assert_eq!(output.status.code(), Some(2));
        assert_eq!(json_output(&output)["code"], expected_code);
    }

    let mut over_limit = Vec::with_capacity(4_098);
    over_limit.push(0x5f);
    over_limit.extend(core::iter::repeat_n(0x40, 4_096));
    over_limit.push(0xff);
    let request = format!(
        "{{\"cbor_hex\":\"{}\"}}",
        statqed_rust_cbor_prototype::hex_encode(&over_limit)
    );
    let output = invoke("decode", request.as_bytes())?;
    assert_eq!(output.status.code(), Some(2));
    assert_eq!(json_output(&output)["code"], "resource.total_items");
    Ok(())
}

#[test]
fn frame_and_verify_digest_commands_round_trip_exact_fields() -> io::Result<()> {
    let frame_request = br#"{"algorithm_id":"sha-256","cbor_hex":"f6","framing_id":"statqed.digest-lp.v1","object_class_schema_id":"test.object-v1","profile_id":"statqed.cbor-core.v1","purpose_id":"test.manifest"}"#;
    let framed = invoke("frame", frame_request)?;
    assert!(framed.status.success());
    let framed_json = json_output(&framed);
    assert_eq!(framed_json["result_class"], "accepted");
    assert_eq!(framed_json["code"], "accepted");
    assert_eq!(framed_json["cbor_hex"], "f6");
    assert_eq!(framed_json["digest_hex"].as_str().map(str::len), Some(64));
    assert!(
        framed_json["frame_hex"]
            .as_str()
            .is_some_and(|value| value.starts_with("537461745145442d44696765737400"))
    );

    let raw_frame = invoke("frame-raw", frame_request)?;
    assert!(raw_frame.status.success());
    assert!(raw_frame.stderr.is_empty());
    assert_eq!(
        raw_frame.stdout,
        statqed_rust_cbor_prototype::hex_decode(
            framed_json["frame_hex"].as_str().unwrap_or_default()
        )
        .expect("diagnostic frame hex must decode")
    );

    let verify_request = format!(
        "{{\"algorithm_id\":\"sha-256\",\"digest_hex\":\"{}\",\"frame_hex\":\"{}\",\"framing_id\":\"statqed.digest-lp.v1\",\"object_class_schema_id\":\"test.object-v1\",\"profile_id\":\"statqed.cbor-core.v1\",\"purpose_id\":\"test.manifest\"}}",
        framed_json["digest_hex"].as_str().unwrap_or_default(),
        framed_json["frame_hex"].as_str().unwrap_or_default(),
    );
    let verified = invoke("verify-digest", verify_request.as_bytes())?;
    assert!(verified.status.success());
    assert_eq!(json_output(&verified), framed_json);
    Ok(())
}

#[test]
fn all_failures_expose_result_class_and_code() -> io::Result<()> {
    let output = invoke("unknown", b"")?;
    assert_eq!(output.status.code(), Some(2));
    assert_eq!(
        output.stdout,
        b"{\"code\":\"expected.top_level\",\"offset\":0,\"result_class\":\"expectedness\"}\n"
    );
    Ok(())
}

#[test]
fn raw_evidence_commands_bypass_only_the_diagnostic_envelope() -> io::Result<()> {
    let text = "a".repeat(5_000);
    let typed = format!("{{\"type\":\"text\",\"value\":\"{text}\"}}");

    let diagnostic = invoke("encode", typed.as_bytes())?;
    assert_eq!(diagnostic.status.code(), Some(2));
    assert_eq!(
        json_output(&diagnostic)["code"],
        "resource.diagnostic_bytes"
    );

    let encoded = invoke("encode-raw", typed.as_bytes())?;
    assert!(encoded.status.success());
    assert!(encoded.stderr.is_empty());
    assert_eq!(&encoded.stdout[..3], &[0x79, 0x13, 0x88]);
    assert_eq!(encoded.stdout.len(), 5_003);

    let request = format!(
        "{{\"cbor_hex\":\"{}\"}}",
        statqed_rust_cbor_prototype::hex_encode(&encoded.stdout)
    );
    let decoded = invoke("decode-raw", request.as_bytes())?;
    assert!(decoded.status.success());
    assert!(decoded.stderr.is_empty());
    assert!(!decoded.stdout.ends_with(b"\n"));
    let projection: JsonValue =
        serde_json::from_slice(&decoded.stdout).expect("raw evidence must be typed JSON");
    assert_eq!(projection["type"], "text");
    assert_eq!(projection["value"], text);
    Ok(())
}

#[test]
fn json_transport_input_cap_is_exact_and_not_a_profile_limit() -> io::Result<()> {
    let at_cap = invoke("unknown", &vec![b' '; 2_200_000])?;
    assert_eq!(at_cap.status.code(), Some(2));
    assert_eq!(json_output(&at_cap)["code"], "expected.top_level");

    let over_cap = invoke("unknown", &vec![b' '; 2_200_001])?;
    assert_eq!(over_cap.status.code(), Some(2));
    assert_eq!(json_output(&over_cap)["code"], "resource.input_bytes");
    Ok(())
}

#[test]
fn frame_raw_exposes_the_attainable_maximum_binary_frame() -> io::Result<()> {
    let first_hex = "00".repeat(1_030);
    let regular_hex = "00".repeat(1_024);
    let mut typed = String::with_capacity(2_117_593);
    typed.push_str("{\"type\":\"array\",\"items\":[");
    typed.push_str("{\"type\":\"bytes\",\"hex\":\"");
    typed.push_str(&first_hex);
    typed.push_str("\"}");
    for _ in 0..1_020 {
        typed.push(',');
        typed.push_str("{\"type\":\"bytes\",\"hex\":\"");
        typed.push_str(&regular_hex);
        typed.push_str("\"}");
    }
    typed.push_str("]}\n");
    assert_eq!(typed.len(), 2_117_593);

    let encoded = invoke("encode-raw", typed.as_bytes())?;
    assert!(encoded.status.success());
    assert_eq!(encoded.stdout.len(), 1_048_576);

    let purpose = format!("test.{}", "p".repeat(123));
    let schema = format!("test.{}", "s".repeat(123));
    let request = format!(
        "{{\"algorithm_id\":\"sha-256\",\"cbor_hex\":\"{}\",\"framing_id\":\"statqed.digest-lp.v1\",\"object_class_schema_id\":\"{schema}\",\"profile_id\":\"statqed.cbor-core.v1\",\"purpose_id\":\"{purpose}\"}}",
        statqed_rust_cbor_prototype::hex_encode(&encoded.stdout),
    );
    let framed = invoke("frame-raw", request.as_bytes())?;
    assert!(framed.status.success());
    assert!(framed.stderr.is_empty());
    assert_eq!(framed.stdout.len(), 1_048_918);
    assert!(framed.stdout.starts_with(b"StatQED-Digest\0"));

    let mut oversized_payload = encoded.stdout;
    oversized_payload.push(0);
    let oversized_request = format!(
        "{{\"algorithm_id\":\"sha-256\",\"cbor_hex\":\"{}\",\"framing_id\":\"statqed.digest-lp.v1\",\"object_class_schema_id\":\"{schema}\",\"profile_id\":\"statqed.cbor-core.v1\",\"purpose_id\":\"{purpose}\"}}",
        statqed_rust_cbor_prototype::hex_encode(&oversized_payload),
    );
    let oversized = invoke("frame-raw", oversized_request.as_bytes())?;
    assert_eq!(oversized.status.code(), Some(2));
    assert_eq!(json_output(&oversized)["code"], "digest.length");
    Ok(())
}
