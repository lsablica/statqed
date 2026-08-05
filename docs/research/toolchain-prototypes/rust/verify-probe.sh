#!/usr/bin/env bash
set -euo pipefail

readonly PROTOTYPE_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly RETAINED_LOG_ROOT="$(cd -- "${PROTOTYPE_ROOT}/../logs/rust" && pwd)"
readonly CACHE_ROOT="${STATQED_RUST_CACHE_ROOT:-/tmp/statqed-sq0002-rust-cache}"
readonly RUSTUP_BIN="${STATQED_RUSTUP_BIN:-$(command -v rustup)}"
readonly CARGO_BIN="${STATQED_CARGO_BIN:-$(command -v cargo)}"
readonly RUSTC_BIN="${STATQED_RUSTC_BIN:-$(command -v rustc)}"
readonly PYTHON_BIN="${STATQED_PYTHON_BIN:-$(command -v python3)}"
readonly LOCK_SHA256="993f587b7dee5a7e18bff312ae76ac7ab84031ccc771b5e9789915d2bfd3883b"
readonly DEV_RUSTC_COMMIT="8bab26f4f68e0e26f0bb7960be334d5b520ea452"
readonly DEV_CARGO_COMMIT="c980f4866141969fab6254a680546a277789d6f0"
readonly MSRV_RUSTC_COMMIT="4eb161250e340c8f48f66e2b929ef4a5bed7c181"
readonly MSRV_CARGO_COMMIT="d73d2caf9e41a39daf2a8d6ce60ec80bf354d2a7"
readonly EXPECTED_RUNTIME='{"arrow_ipc_bytes":776,"archive_bytes":175,"blake3_hex":"ac758c4353bce30e16cc6c1e5387139c1f43b4feca0fe3ffeab81d04a0c5af04","json_bytes":49,"rows":3,"sha256_hex":"0ea463438fdd5d4584bb4a8a33bd98b7f6db6cb5bff484359c59f8c858a9d611"}'

export RUSTUP_HOME="${STATQED_RUSTUP_HOME:-${CACHE_ROOT}/rustup}"
export CARGO_HOME="${STATQED_RUST_CARGO_HOME:-${CACHE_ROOT}/cargo}"
export CARGO_NET_OFFLINE=true
export LC_ALL="C.UTF-8"
export LANG="C.UTF-8"
export TZ="UTC"

if [[ -n "${CARGO_TARGET_DIR:-}" ]]; then
    printf 'refusing caller-supplied CARGO_TARGET_DIR; verification owns disposable targets\n' >&2
    exit 2
fi

readonly VERIFY_ROOT="$(mktemp -d /tmp/statqed-sq0002-rust-verify.XXXXXX)"
case "${VERIFY_ROOT}" in
    /tmp/statqed-sq0002-rust-verify.*) ;;
    *)
        printf 'unexpected verification directory: %s\n' "${VERIFY_ROOT}" >&2
        exit 2
        ;;
esac
case "${VERIFY_ROOT}" in
    "${PROTOTYPE_ROOT}"/*|"${RETAINED_LOG_ROOT}"/*|"${CACHE_ROOT}"/*)
        printf 'refusing retained or cache directory as verification workspace: %s\n' "${VERIFY_ROOT}" >&2
        exit 2
        ;;
esac
cleanup() {
    rm -rf -- "${VERIFY_ROOT}"
}
trap cleanup EXIT

assert_sha256() {
    local expected="$1"
    local path="$2"
    local actual
    actual="$(sha256sum -- "${path}" | awk '{print $1}')"
    if [[ "${actual}" != "${expected}" ]]; then
        printf 'SHA-256 mismatch for %s: expected %s, observed %s\n' \
            "${path}" "${expected}" "${actual}" >&2
        return 1
    fi
}

assert_contains() {
    local observed="$1"
    local expected="$2"
    if [[ "${observed}" != *"${expected}"* ]]; then
        printf 'missing exact version evidence %q in:\n%s\n' "${expected}" "${observed}" >&2
        return 1
    fi
}

assert_runtime() {
    local observed="$1"
    if [[ "${observed}" != "${EXPECTED_RUNTIME}" ]]; then
        printf 'runtime observation drifted\nexpected: %s\nobserved: %s\n' \
            "${EXPECTED_RUNTIME}" "${observed}" >&2
        return 1
    fi
}

check_lock_and_toolchain() {
    local version="$1"
    local rustc_commit="$2"
    local cargo_commit="$3"
    local rustc_version
    local cargo_version
    assert_sha256 "${LOCK_SHA256}" "${PROTOTYPE_ROOT}/Cargo.lock"
    rustc_version="$("${RUSTC_BIN}" "+${version}" --version --verbose)"
    cargo_version="$("${CARGO_BIN}" "+${version}" --version --verbose)"
    assert_contains "${rustc_version}" "release: ${version}"
    assert_contains "${rustc_version}" "commit-hash: ${rustc_commit}"
    assert_contains "${cargo_version}" "release: ${version}"
    assert_contains "${cargo_version}" "commit-hash: ${cargo_commit}"
}

run_development() {
    local target="${VERIFY_ROOT}/target-development"
    local metadata="${VERIFY_ROOT}/development-metadata.json"
    local unsafe_output="${VERIFY_ROOT}/unsafe-rejection.txt"
    local runtime
    check_lock_and_toolchain 1.97.1 "${DEV_RUSTC_COMMIT}" "${DEV_CARGO_COMMIT}"
    cd -- "${PROTOTYPE_ROOT}"
    CARGO_TARGET_DIR="${target}" "${CARGO_BIN}" +1.97.1 metadata --locked --offline --format-version 1 >"${metadata}"
    "${CARGO_BIN}" +1.97.1 fmt --all -- --check
    CARGO_TARGET_DIR="${target}" "${CARGO_BIN}" +1.97.1 clippy --locked --offline --workspace --all-targets --all-features -- -D warnings
    CARGO_TARGET_DIR="${target}" "${CARGO_BIN}" +1.97.1 test --locked --offline --workspace --all-targets --all-features
    runtime="$(CARGO_TARGET_DIR="${target}" "${CARGO_BIN}" +1.97.1 run --quiet --locked --offline --package statqed-rust-compat-probe -- --json)"
    assert_runtime "${runtime}"
    if CARGO_TARGET_DIR="${target}-unsafe" "${CARGO_BIN}" +1.97.1 check --offline --manifest-path rejections/unsafe-code/Cargo.toml >"${unsafe_output}" 2>&1; then
        printf 'unsafe-code rejection fixture unexpectedly compiled\n' >&2
        return 1
    fi
    if ! grep -q 'usage of an `unsafe` block' "${unsafe_output}"; then
        printf 'unsafe-code fixture failed for an unexpected reason\n' >&2
        return 1
    fi
    printf 'Rust development probe passed: 1.97.1, locked/offline, fresh target\n'
}

run_msrv() {
    local target="${VERIFY_ROOT}/target-msrv"
    local runtime
    check_lock_and_toolchain 1.85.1 "${MSRV_RUSTC_COMMIT}" "${MSRV_CARGO_COMMIT}"
    cd -- "${PROTOTYPE_ROOT}"
    CARGO_TARGET_DIR="${target}" "${CARGO_BIN}" +1.85.1 metadata --locked --offline --format-version 1 >"${VERIFY_ROOT}/msrv-metadata.json"
    "${CARGO_BIN}" +1.85.1 fmt --all -- --check
    CARGO_TARGET_DIR="${target}" "${CARGO_BIN}" +1.85.1 clippy --locked --offline --workspace --all-targets --all-features -- -D warnings
    CARGO_TARGET_DIR="${target}" "${CARGO_BIN}" +1.85.1 test --locked --offline --workspace --all-targets --all-features
    runtime="$(CARGO_TARGET_DIR="${target}" "${CARGO_BIN}" +1.85.1 run --quiet --locked --offline --package statqed-rust-compat-probe -- --json)"
    assert_runtime "${runtime}"
    printf 'Rust compatibility-floor probe passed: 1.85.1, locked/offline, fresh target\n'
}

json_field() {
    local path="$1"
    local dotted_key="$2"
    "${PYTHON_BIN}" -c '
import json, sys
value = json.load(open(sys.argv[1], encoding="utf-8"))
for part in sys.argv[2].split("."):
    value = value[part]
print(value)
' "${path}" "${dotted_key}"
}

run_security() {
    local security_lock="${PROTOTYPE_ROOT}/security-lock.json"
    local audit_archive="${STATQED_CARGO_AUDIT_ARCHIVE:-/tmp/statqed-sq0002-cargo-audit-0.22.2.tgz}"
    local rustsec_archive="${STATQED_RUSTSEC_ARCHIVE:-/tmp/statqed-sq0002-rustsec-d91a8fc.tar.gz}"
    local audit_root="${VERIFY_ROOT}/cargo-audit"
    local rustsec_root="${VERIFY_ROOT}/rustsec-db"
    local audit_bin
    local audit_json="${VERIFY_ROOT}/cargo-audit.json"
    local metadata="${VERIFY_ROOT}/security-metadata.json"
    local expected
    check_lock_and_toolchain 1.97.1 "${DEV_RUSTC_COMMIT}" "${DEV_CARGO_COMMIT}"
    for required in "${security_lock}" "${audit_archive}" "${rustsec_archive}"; do
        if [[ ! -f "${required}" ]]; then
            printf 'required immutable security input unavailable: %s\n' "${required}" >&2
            return 1
        fi
    done
    expected="$(json_field "${security_lock}" cargo_audit.archive_sha256)"
    assert_sha256 "${expected}" "${audit_archive}"
    expected="$(json_field "${security_lock}" rustsec_advisory_db.archive_sha256)"
    assert_sha256 "${expected}" "${rustsec_archive}"
    mkdir -p -- "${audit_root}" "${rustsec_root}"
    tar -xzf "${audit_archive}" --strip-components=1 -C "${audit_root}"
    tar -xzf "${rustsec_archive}" --strip-components=1 -C "${rustsec_root}"
    audit_bin="${audit_root}/cargo-audit"
    expected="$(json_field "${security_lock}" cargo_audit.executable_sha256)"
    assert_sha256 "${expected}" "${audit_bin}"
    assert_contains "$("${audit_bin}" --version)" "cargo-audit 0.22.2"
    cd -- "${PROTOTYPE_ROOT}"
    "${audit_bin}" audit --db "${rustsec_root}" --no-fetch --stale --no-yanked --file Cargo.lock --json >"${audit_json}"
    "${PYTHON_BIN}" -c '
import json, sys
report = json.load(open(sys.argv[1], encoding="utf-8"))
assert report["lockfile"]["dependency-count"] == 128, report
assert report["vulnerabilities"] == {"found": False, "count": 0, "list": []}, report
assert report["warnings"] == {}, report
' "${audit_json}"
    CARGO_TARGET_DIR="${VERIFY_ROOT}/target-security" "${CARGO_BIN}" +1.97.1 metadata --locked --offline --format-version 1 >"${metadata}"
    "${PYTHON_BIN}" "${PROTOTYPE_ROOT}/verify_license_inventory.py" \
        --lock "${PROTOTYPE_ROOT}/Cargo.lock" \
        --metadata "${metadata}" \
        --inventory "${PROTOTYPE_ROOT}/dependency-license-inventory.json"
    expected="$(json_field "${security_lock}" dependency_license_inventory_sha256)"
    assert_sha256 "${expected}" "${PROTOTYPE_ROOT}/dependency-license-inventory.json"
    printf 'Rust crate-graph security probe passed: cargo-audit 0.22.2, immutable RustSec snapshot, 128 locked packages\n'
    printf 'Scope: this result covers the locked crate graph only; it does not assess rustc, Cargo, rustup, the operating system, or unmodeled native libraries.\n'
}

case "${1:-all}" in
    development)
        run_development
        ;;
    msrv)
        run_msrv
        ;;
    security)
        run_security
        ;;
    all)
        run_development
        run_msrv
        run_security
        ;;
    *)
        printf 'usage: %s [development|msrv|security|all]\n' "$0" >&2
        exit 2
        ;;
esac
