//! Bounded parsing and deterministic output for the initial StatQED command surface.
//!
//! This crate intentionally contains no statistical, schema, artifact, encoding,
//! digest, registry, certificate, or verification semantics.

#![forbid(unsafe_code)]

use std::ffi::OsStr;

/// Version of the bootstrap CLI response shape.
pub const CLI_PROTOCOL_VERSION: u8 = 1;

/// Maximum number of command-line arguments accepted after the executable name.
pub const MAX_ARGUMENTS: usize = 64;

/// Maximum UTF-8 byte length of one command-line argument.
pub const MAX_ARGUMENT_BYTES: usize = 4_096;

/// Maximum aggregate UTF-8 byte length of all command-line arguments.
pub const MAX_TOTAL_ARGUMENT_BYTES: usize = 8_192;

/// The only commands supported by the initial operational workspace.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum Command {
    /// Emit deterministic package version metadata.
    Version(VersionFormat),
}

/// Supported presentation formats for deterministic version metadata.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum VersionFormat {
    /// Conventional one-line version text.
    Text,
    /// Versioned, deterministic JSON metadata.
    Json,
}

/// Stable classes for malformed or unsupported command-line input.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum ErrorCode {
    /// No command was provided.
    MissingCommand,
    /// An unrecognized command was provided.
    UnknownCommand,
    /// An unrecognized option was provided.
    UnknownOption,
    /// A required option value was omitted.
    MissingValue,
    /// An option was repeated.
    RepeatedOption,
    /// An empty option value was provided.
    EmptyValue,
    /// An option value is outside the supported bootstrap vocabulary.
    InvalidValue,
    /// A supported command was followed by an unexpected argument.
    UnexpectedArgument,
    /// An operating-system argument is not valid UTF-8.
    InvalidArgumentEncoding,
    /// An argument count or byte-length limit was exceeded.
    InputLimitExceeded,
}

impl ErrorCode {
    /// Render the complete deterministic JSON error envelope.
    ///
    /// The envelope never includes rejected input, timestamps, paths, random
    /// identifiers, locale text, stack traces, or dependency diagnostics.
    #[must_use]
    pub const fn as_json(self) -> &'static str {
        match self {
            Self::MissingCommand => {
                r#"{"protocol_version":1,"error":{"code":"missing_command","message":"a command is required"}}"#
            }
            Self::UnknownCommand => {
                r#"{"protocol_version":1,"error":{"code":"unknown_command","message":"the command is not supported"}}"#
            }
            Self::UnknownOption => {
                r#"{"protocol_version":1,"error":{"code":"unknown_option","message":"the option is not supported"}}"#
            }
            Self::MissingValue => {
                r#"{"protocol_version":1,"error":{"code":"missing_value","message":"the option requires a value"}}"#
            }
            Self::RepeatedOption => {
                r#"{"protocol_version":1,"error":{"code":"repeated_option","message":"the option may be provided only once"}}"#
            }
            Self::EmptyValue => {
                r#"{"protocol_version":1,"error":{"code":"empty_value","message":"the option value must not be empty"}}"#
            }
            Self::InvalidValue => {
                r#"{"protocol_version":1,"error":{"code":"invalid_value","message":"the option value is not supported"}}"#
            }
            Self::UnexpectedArgument => {
                r#"{"protocol_version":1,"error":{"code":"unexpected_argument","message":"the command has an unexpected argument"}}"#
            }
            Self::InvalidArgumentEncoding => {
                r#"{"protocol_version":1,"error":{"code":"invalid_argument_encoding","message":"command-line arguments must be valid UTF-8"}}"#
            }
            Self::InputLimitExceeded => {
                r#"{"protocol_version":1,"error":{"code":"input_limit_exceeded","message":"command-line input exceeds a fixed resource limit"}}"#
            }
        }
    }
}

/// Parse an argument stream with fixed count and byte limits.
///
/// Parsing stores at most [`MAX_TOTAL_ARGUMENT_BYTES`] of validated UTF-8 and
/// never includes caller-controlled text in an error. Encoding and resource
/// errors take precedence because the complete bounded stream is validated
/// before its command grammar is interpreted.
///
/// # Errors
///
/// Returns a stable [`ErrorCode`] for malformed, unsupported, non-UTF-8, or
/// resource-limit-exceeding input.
pub fn parse_arguments<I, S>(arguments: I) -> Result<Command, ErrorCode>
where
    I: IntoIterator<Item = S>,
    S: AsRef<OsStr>,
{
    let mut count = 0_usize;
    let mut total_bytes = 0_usize;
    let mut validated = Vec::with_capacity(MAX_ARGUMENTS);

    for argument in arguments {
        count = count.checked_add(1).ok_or(ErrorCode::InputLimitExceeded)?;
        if count > MAX_ARGUMENTS {
            return Err(ErrorCode::InputLimitExceeded);
        }

        let argument = argument.as_ref();
        let argument_bytes = argument.len();
        if argument_bytes > MAX_ARGUMENT_BYTES {
            return Err(ErrorCode::InputLimitExceeded);
        }

        total_bytes = total_bytes
            .checked_add(argument_bytes)
            .ok_or(ErrorCode::InputLimitExceeded)?;
        if total_bytes > MAX_TOTAL_ARGUMENT_BYTES {
            return Err(ErrorCode::InputLimitExceeded);
        }

        let text = argument
            .to_str()
            .ok_or(ErrorCode::InvalidArgumentEncoding)?;
        validated.push(text.to_owned());
    }

    parse_validated(validated.iter().map(String::as_str))
}

fn parse_validated<'a>(mut arguments: impl Iterator<Item = &'a str>) -> Result<Command, ErrorCode> {
    let first = arguments.next().ok_or(ErrorCode::MissingCommand)?;
    match first {
        "--version" => match arguments.next() {
            None => Ok(Command::Version(VersionFormat::Text)),
            Some(extra) => Err(classify_extra(extra)),
        },
        "version" => parse_version(arguments),
        unknown if unknown.starts_with('-') => Err(ErrorCode::UnknownOption),
        _ => Err(ErrorCode::UnknownCommand),
    }
}

fn parse_version<'a>(mut arguments: impl Iterator<Item = &'a str>) -> Result<Command, ErrorCode> {
    let Some(option) = arguments.next() else {
        return Ok(Command::Version(VersionFormat::Text));
    };
    if option != "--format" {
        return Err(classify_extra(option));
    }

    let value = arguments.next().ok_or(ErrorCode::MissingValue)?;
    let format = match value {
        "" => return Err(ErrorCode::EmptyValue),
        "json" => VersionFormat::Json,
        "text" => VersionFormat::Text,
        _ => return Err(ErrorCode::InvalidValue),
    };

    match arguments.next() {
        None => Ok(Command::Version(format)),
        Some(extra) => Err(classify_extra(extra)),
    }
}

fn classify_extra(extra: &str) -> ErrorCode {
    if matches!(extra, "--format" | "--version") {
        ErrorCode::RepeatedOption
    } else if extra.starts_with('-') {
        ErrorCode::UnknownOption
    } else {
        ErrorCode::UnexpectedArgument
    }
}

/// Render conventional deterministic version text.
#[must_use]
pub const fn version_text() -> &'static str {
    concat!("statqed ", env!("CARGO_PKG_VERSION"))
}

/// Render deterministic, versioned package and Rust-policy metadata as JSON.
#[must_use]
pub const fn version_json() -> &'static str {
    concat!(
        r#"{"protocol_version":1,"program":"statqed","version":""#,
        env!("CARGO_PKG_VERSION"),
        r#"","rust":{"reference":"1.97.1","compatibility_floor":"1.85.1","edition":"2024"}}"#
    )
}

#[cfg(test)]
mod tests {
    use super::{
        Command, ErrorCode, MAX_ARGUMENT_BYTES, MAX_ARGUMENTS, MAX_TOTAL_ARGUMENT_BYTES,
        VersionFormat, parse_arguments, version_json, version_text,
    };
    use std::ffi::OsString;

    #[test]
    fn parses_supported_version_forms() {
        assert_eq!(
            parse_arguments(["version"]),
            Ok(Command::Version(VersionFormat::Text))
        );
        assert_eq!(
            parse_arguments(["--version"]),
            Ok(Command::Version(VersionFormat::Text))
        );
        assert_eq!(
            parse_arguments(["version", "--format", "json"]),
            Ok(Command::Version(VersionFormat::Json))
        );
        assert_eq!(
            parse_arguments(["version", "--format", "text"]),
            Ok(Command::Version(VersionFormat::Text))
        );
    }

    #[test]
    fn classifies_malformed_and_unsupported_forms() {
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
            (vec!["--version", "--version"], ErrorCode::RepeatedOption),
            (vec!["version", "extra"], ErrorCode::UnexpectedArgument),
        ];
        for (arguments, expected) in cases {
            assert_eq!(parse_arguments(arguments), Err(expected));
        }
    }

    #[test]
    fn version_and_error_json_are_exact_and_deterministic() {
        assert_eq!(version_text(), "statqed 0.1.0");
        assert_eq!(
            version_json(),
            r#"{"protocol_version":1,"program":"statqed","version":"0.1.0","rust":{"reference":"1.97.1","compatibility_floor":"1.85.1","edition":"2024"}}"#
        );
        assert_eq!(version_json(), version_json());
        assert!(
            ErrorCode::MissingCommand
                .as_json()
                .starts_with(r#"{"protocol_version":1,"#)
        );
        assert!(
            ErrorCode::UnknownCommand
                .as_json()
                .contains(r#""code":"unknown_command""#)
        );
        assert!(
            ErrorCode::UnknownOption
                .as_json()
                .contains(r#""code":"unknown_option""#)
        );
        assert!(
            ErrorCode::MissingValue
                .as_json()
                .contains(r#""code":"missing_value""#)
        );
        assert!(
            ErrorCode::RepeatedOption
                .as_json()
                .contains(r#""code":"repeated_option""#)
        );
        assert!(
            ErrorCode::EmptyValue
                .as_json()
                .contains(r#""code":"empty_value""#)
        );
        assert!(
            ErrorCode::InvalidValue
                .as_json()
                .contains(r#""code":"invalid_value""#)
        );
        assert!(
            ErrorCode::UnexpectedArgument
                .as_json()
                .contains(r#""code":"unexpected_argument""#)
        );
    }

    #[test]
    fn enforces_resource_limits_at_both_sides() {
        let boundary = "x".repeat(MAX_ARGUMENT_BYTES);
        assert_eq!(parse_arguments([boundary]), Err(ErrorCode::UnknownCommand));
        let oversized = "x".repeat(MAX_ARGUMENT_BYTES + 1);
        assert_eq!(
            parse_arguments([oversized]),
            Err(ErrorCode::InputLimitExceeded)
        );

        let repeated_at_limit = vec!["x"; MAX_ARGUMENTS];
        assert_eq!(
            parse_arguments(repeated_at_limit),
            Err(ErrorCode::UnknownCommand)
        );
        let repeated_over_limit = vec!["x"; MAX_ARGUMENTS + 1];
        assert_eq!(
            parse_arguments(repeated_over_limit),
            Err(ErrorCode::InputLimitExceeded)
        );

        let aggregate_half = "x".repeat(MAX_TOTAL_ARGUMENT_BYTES / 2);
        assert_eq!(
            parse_arguments([aggregate_half.clone(), aggregate_half.clone()]),
            Err(ErrorCode::UnknownCommand)
        );
        assert_eq!(
            parse_arguments([aggregate_half.clone(), aggregate_half, "x".to_owned()]),
            Err(ErrorCode::InputLimitExceeded)
        );
    }

    #[test]
    fn randomized_argument_sequences_never_panic() {
        let mut state = 0x5eed_5eed_d15c_a11e_u64;

        for case_index in 0..1_024 {
            let count = (next_u64(&mut state) as usize) % (MAX_ARGUMENTS + 17);
            let mut arguments = Vec::with_capacity(count);
            for argument_index in 0..count {
                let random_length = (next_u64(&mut state) as usize) % 96;
                let length = if (case_index + argument_index) % 97 == 0 {
                    MAX_ARGUMENT_BYTES + 1
                } else {
                    random_length
                };
                let byte = b'a' + (next_u64(&mut state) % 26) as u8;
                let text = std::iter::repeat_n(char::from(byte), length).collect::<String>();
                arguments.push(OsString::from(text));
            }

            let observed = std::panic::catch_unwind(move || parse_arguments(arguments));
            assert!(observed.is_ok(), "case {case_index} panicked");
        }
    }

    #[cfg(unix)]
    #[test]
    fn rejects_non_utf8_unix_arguments_without_panicking() {
        use std::os::unix::ffi::OsStringExt;

        let invalid = OsString::from_vec(vec![0xff, 0xfe, 0xfd]);
        let observed = std::panic::catch_unwind(|| parse_arguments([invalid]));
        assert!(matches!(
            observed,
            Ok(Err(ErrorCode::InvalidArgumentEncoding))
        ));

        let oversized_invalid = OsString::from_vec(vec![0xff; MAX_ARGUMENT_BYTES + 1]);
        assert_eq!(
            parse_arguments([oversized_invalid]),
            Err(ErrorCode::InputLimitExceeded)
        );
    }

    fn next_u64(state: &mut u64) -> u64 {
        *state = state
            .wrapping_mul(6_364_136_223_846_793_005)
            .wrapping_add(1_442_695_040_888_963_407);
        *state
    }
}
