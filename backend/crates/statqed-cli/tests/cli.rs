//! Process-level conformance tests for deterministic and adversarial input handling.

#![forbid(unsafe_code)]

use statqed_core::{ErrorCode, MAX_ARGUMENT_BYTES, MAX_ARGUMENTS, version_json, version_text};
use std::ffi::OsStr;
use std::io;
use std::process::{Command, Output};

const MALFORMED_INPUT_EXIT_CODE: i32 = 2;

#[test]
fn version_output_is_exact_and_repeatable() -> io::Result<()> {
    let plain = run(["--version"])?;
    assert!(plain.status.success());
    assert_eq!(plain.stdout, format!("{}\n", version_text()).into_bytes());
    assert!(plain.stderr.is_empty());

    let baseline = run(["version", "--format", "json"])?;
    assert!(baseline.status.success());
    assert_eq!(
        baseline.stdout,
        format!("{}\n", version_json()).into_bytes()
    );
    assert!(baseline.stderr.is_empty());
    for _ in 0..32 {
        let repeated = run(["version", "--format", "json"])?;
        assert_eq!(repeated.status, baseline.status);
        assert_eq!(repeated.stdout, baseline.stdout);
        assert_eq!(repeated.stderr, baseline.stderr);
    }
    Ok(())
}

#[test]
fn malformed_categories_have_exact_json_and_exit_code() -> io::Result<()> {
    let cases = [
        (Vec::<&str>::new(), ErrorCode::MissingCommand),
        (vec!["unknown"], ErrorCode::UnknownCommand),
        (vec!["--unknown"], ErrorCode::UnknownOption),
        (vec!["version", "--unknown"], ErrorCode::UnknownOption),
        (vec!["version", "--format"], ErrorCode::MissingValue),
        (vec!["version", "--format", ""], ErrorCode::EmptyValue),
        (vec!["version", "--format", "{"], ErrorCode::InvalidValue),
        (
            vec!["version", "--format", "json", "--format"],
            ErrorCode::RepeatedOption,
        ),
        (vec!["version", "extra"], ErrorCode::UnexpectedArgument),
    ];
    for (arguments, expected) in cases {
        let output = run(arguments)?;
        assert_eq!(output.status.code(), Some(MALFORMED_INPUT_EXIT_CODE));
        assert!(output.stdout.is_empty());
        assert_eq!(output.stderr, error_line(expected));
    }
    Ok(())
}

#[test]
fn oversized_and_repeated_inputs_are_bounded() -> io::Result<()> {
    let oversized = "x".repeat(MAX_ARGUMENT_BYTES + 1);
    let long_output = run([oversized])?;
    assert_eq!(long_output.status.code(), Some(MALFORMED_INPUT_EXIT_CODE));
    assert!(long_output.stdout.is_empty());
    assert_eq!(
        long_output.stderr,
        error_line(ErrorCode::InputLimitExceeded)
    );

    let repeated = vec!["version"; MAX_ARGUMENTS + 1];
    let repeated_output = run(repeated)?;
    assert_eq!(
        repeated_output.status.code(),
        Some(MALFORMED_INPUT_EXIT_CODE)
    );
    assert!(repeated_output.stdout.is_empty());
    assert_eq!(
        repeated_output.stderr,
        error_line(ErrorCode::InputLimitExceeded)
    );
    Ok(())
}

#[cfg(unix)]
#[test]
fn non_utf8_unix_input_has_stable_error_output() -> io::Result<()> {
    use std::ffi::OsString;
    use std::os::unix::ffi::OsStringExt;

    let invalid = OsString::from_vec(vec![0xff, 0xfe]);
    let output = run([invalid])?;
    assert_eq!(output.status.code(), Some(MALFORMED_INPUT_EXIT_CODE));
    assert!(output.stdout.is_empty());
    assert_eq!(
        output.stderr,
        error_line(ErrorCode::InvalidArgumentEncoding)
    );
    Ok(())
}

#[test]
fn deterministic_randomized_sequences_do_not_panic() -> io::Result<()> {
    let mut state = 0x5eed_d15c_a11e_u64;
    for _ in 0..256 {
        let count = (next_u64(&mut state) as usize) % 12;
        let mut arguments = Vec::with_capacity(count);
        for _ in 0..count {
            let length = (next_u64(&mut state) as usize) % 48;
            let byte = b'a' + (next_u64(&mut state) % 26) as u8;
            arguments.push(std::iter::repeat_n(char::from(byte), length).collect::<String>());
        }
        let output = run(arguments)?;
        assert!(output.status.success() || output.status.code() == Some(MALFORMED_INPUT_EXIT_CODE));
        assert!(output.status.code().is_some());
    }
    Ok(())
}

fn run<I, S>(arguments: I) -> io::Result<Output>
where
    I: IntoIterator<Item = S>,
    S: AsRef<OsStr>,
{
    Command::new(env!("CARGO_BIN_EXE_statqed"))
        .args(arguments)
        .output()
}

fn error_line(error: ErrorCode) -> Vec<u8> {
    let expected = match error {
        ErrorCode::MissingCommand => {
            r#"{"protocol_version":1,"error":{"code":"missing_command","message":"a command is required"}}"#
        }
        ErrorCode::UnknownCommand => {
            r#"{"protocol_version":1,"error":{"code":"unknown_command","message":"the command is not supported"}}"#
        }
        ErrorCode::UnknownOption => {
            r#"{"protocol_version":1,"error":{"code":"unknown_option","message":"the option is not supported"}}"#
        }
        ErrorCode::MissingValue => {
            r#"{"protocol_version":1,"error":{"code":"missing_value","message":"the option requires a value"}}"#
        }
        ErrorCode::RepeatedOption => {
            r#"{"protocol_version":1,"error":{"code":"repeated_option","message":"the option may be provided only once"}}"#
        }
        ErrorCode::EmptyValue => {
            r#"{"protocol_version":1,"error":{"code":"empty_value","message":"the option value must not be empty"}}"#
        }
        ErrorCode::InvalidValue => {
            r#"{"protocol_version":1,"error":{"code":"invalid_value","message":"the option value is not supported"}}"#
        }
        ErrorCode::UnexpectedArgument => {
            r#"{"protocol_version":1,"error":{"code":"unexpected_argument","message":"the command has an unexpected argument"}}"#
        }
        ErrorCode::InvalidArgumentEncoding => {
            r#"{"protocol_version":1,"error":{"code":"invalid_argument_encoding","message":"command-line arguments must be valid UTF-8"}}"#
        }
        ErrorCode::InputLimitExceeded => {
            r#"{"protocol_version":1,"error":{"code":"input_limit_exceeded","message":"command-line input exceeds a fixed resource limit"}}"#
        }
    };
    format!("{expected}\n").into_bytes()
}

fn next_u64(state: &mut u64) -> u64 {
    *state = state
        .wrapping_mul(6_364_136_223_846_793_005)
        .wrapping_add(1_442_695_040_888_963_407);
    *state
}
