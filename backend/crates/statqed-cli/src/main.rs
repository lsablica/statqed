//! Thin process-I/O adapter for the `statqed` command.

#![forbid(unsafe_code)]

use statqed_core::{Command, VersionFormat, parse_arguments, version_json, version_text};
use std::io::{self, Write};
use std::process::ExitCode;

const MALFORMED_INPUT_EXIT_CODE: u8 = 2;

fn main() -> ExitCode {
    match parse_arguments(std::env::args_os().skip(1)) {
        Ok(Command::Version(VersionFormat::Text)) => emit_stdout(version_text()),
        Ok(Command::Version(VersionFormat::Json)) => emit_stdout(version_json()),
        Err(error) => emit_stderr(error.as_json(), MALFORMED_INPUT_EXIT_CODE),
    }
}

fn emit_stdout(message: &str) -> ExitCode {
    let stdout = io::stdout();
    let mut writer = stdout.lock();
    emit(&mut writer, message, ExitCode::SUCCESS)
}

fn emit_stderr(message: &str, exit_code: u8) -> ExitCode {
    let stderr = io::stderr();
    let mut writer = stderr.lock();
    emit(&mut writer, message, ExitCode::from(exit_code))
}

fn emit(writer: &mut impl Write, message: &str, success: ExitCode) -> ExitCode {
    match write_line(writer, message) {
        Ok(()) => success,
        Err(_) => ExitCode::FAILURE,
    }
}

fn write_line(writer: &mut impl Write, message: &str) -> io::Result<()> {
    writer.write_all(message.as_bytes())?;
    writer.write_all(b"\n")
}

#[cfg(test)]
mod tests {
    use super::emit;
    use std::io::{self, Write};
    use std::process::ExitCode;

    struct RejectWrites;

    impl Write for RejectWrites {
        fn write(&mut self, _buffer: &[u8]) -> io::Result<usize> {
            Err(io::Error::new(io::ErrorKind::BrokenPipe, "test fixture"))
        }

        fn flush(&mut self) -> io::Result<()> {
            Ok(())
        }
    }

    #[test]
    fn broken_output_is_handled_without_panicking() {
        let observed = std::panic::catch_unwind(|| {
            let mut writer = RejectWrites;
            emit(&mut writer, "fixed", ExitCode::SUCCESS)
        });
        assert!(matches!(observed, Ok(code) if code == ExitCode::FAILURE));
    }
}
