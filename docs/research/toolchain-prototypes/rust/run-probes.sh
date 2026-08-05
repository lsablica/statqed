#!/usr/bin/env bash
set -euo pipefail

readonly PROTOTYPE_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly RETAINED_LOG_DIR="${PROTOTYPE_ROOT}/../logs/rust/run-20260803"
readonly LOG_DIR="${STATQED_RUST_LOG_DIR:-${RETAINED_LOG_DIR}}"
readonly CACHE_ROOT="${STATQED_RUST_CACHE_ROOT:-/tmp/statqed-sq0002-rust-cache}"
readonly RUSTUP_BIN="${STATQED_RUSTUP_BIN:-$(command -v rustup)}"
readonly CARGO_BIN="${STATQED_CARGO_BIN:-$(command -v cargo)}"
readonly RUSTC_BIN="${STATQED_RUSTC_BIN:-$(command -v rustc)}"
readonly RUSTUP_PROXY_BIN_DIR="$(dirname -- "${RUSTUP_BIN}")"
readonly RUSTUP_PROXY_HOME="${STATQED_RUSTUP_PROXY_HOME:-$(dirname -- "${RUSTUP_PROXY_BIN_DIR}")}"

export RUSTUP_HOME="${CACHE_ROOT}/rustup"
export CARGO_HOME="${CACHE_ROOT}/cargo"
export LC_ALL="C.UTF-8"
export LANG="C.UTF-8"
export TZ="UTC"

if [[ -e "${LOG_DIR}" ]] && find "${LOG_DIR}" -mindepth 1 -print -quit | grep -q .; then
    printf 'refusing to overwrite retained evidence directory: %s\n' "${LOG_DIR}" >&2
    printf 'use verify-probe.sh for owned verification, or set STATQED_RUST_LOG_DIR to a new empty path\n' >&2
    exit 2
fi
mkdir -p -- "${LOG_DIR}" "${RUSTUP_HOME}" "${CARGO_HOME}"

capture() {
    local log_name="$1"
    shift
    local stem="${log_name%.log}"
    local stdout_path="${LOG_DIR}/${stem}.stdout"
    local stderr_path="${LOG_DIR}/${stem}.stderr"
    local started_at
    local ended_at
    local command_status
    started_at="$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
    set +e
    "$@" >"${stdout_path}" 2>"${stderr_path}"
    command_status=$?
    set -e
    ended_at="$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
    {
        printf 'timestamp_start=%s\n' "${started_at}"
        printf 'timestamp_end=%s\n' "${ended_at}"
        printf 'cwd=%s\n' "$(pwd)"
        printf 'RUSTUP_HOME=%s\n' "${RUSTUP_HOME}"
        printf 'CARGO_HOME=%s\n' "${CARGO_HOME}"
        printf 'LC_ALL=%s\n' "${LC_ALL}"
        printf 'TZ=%s\n' "${TZ}"
        printf 'command='
        printf '%q ' "$@"
        printf '\n'
        printf 'stdout_path=%s\n' "${stdout_path}"
        printf 'stderr_path=%s\n' "${stderr_path}"
        printf 'exit_code=%s\n' "${command_status}"
    } >"${LOG_DIR}/${log_name}"
    return "${command_status}"
}

expect_success() {
    local log_name="$1"
    shift
    if ! capture "${log_name}" "$@"; then
        printf 'unexpected failure; see %s/%s\n' "${LOG_DIR}" "${log_name}" >&2
        return 1
    fi
}

expect_failure() {
    local log_name="$1"
    shift
    if capture "${log_name}" "$@"; then
        printf 'unexpected success; see %s/%s\n' "${LOG_DIR}" "${log_name}" >&2
        return 1
    fi
}

install_toolchains() {
    # rustup discovers its proxy via the installed CARGO_HOME while keeping
    # downloaded toolchains isolated in the task cache.
    expect_success install-dev.log env CARGO_HOME="${RUSTUP_PROXY_HOME}" "${RUSTUP_BIN}" toolchain install 1.97.1 --profile minimal --component clippy --component rustfmt
    expect_success install-msrv.log env CARGO_HOME="${RUSTUP_PROXY_HOME}" "${RUSTUP_BIN}" toolchain install 1.85.1 --profile minimal --component clippy --component rustfmt
}

record_environment() {
    expect_success environment.log bash -c 'date -u +%Y-%m-%dT%H:%M:%SZ; uname -a; cat /etc/os-release; locale; getconf GNU_LIBC_VERSION'
    expect_success rustup-version.log "${RUSTUP_BIN}" --version
    expect_success rustup-toolchains.log "${RUSTUP_BIN}" toolchain list
    expect_success dev-rustc-version.log "${RUSTC_BIN}" +1.97.1 --version --verbose
    expect_success dev-cargo-version.log "${CARGO_BIN}" +1.97.1 --version --verbose
    expect_success msrv-rustc-version.log "${RUSTC_BIN}" +1.85.1 --version --verbose
    expect_success msrv-cargo-version.log "${CARGO_BIN}" +1.85.1 --version --verbose
    expect_success dev-host-cfg.log "${RUSTC_BIN}" +1.97.1 --print cfg
    expect_success dev-targets-installed.log "${RUSTUP_BIN}" target list --installed --toolchain 1.97.1
    expect_success msrv-targets-installed.log "${RUSTUP_BIN}" target list --installed --toolchain 1.85.1
    expect_success dev-components-installed.log "${RUSTUP_BIN}" component list --installed --toolchain 1.97.1
    expect_success msrv-components-installed.log "${RUSTUP_BIN}" component list --installed --toolchain 1.85.1
    expect_success cargo-lock-digest.log sha256sum "${PROTOTYPE_ROOT}/Cargo.lock"
    expect_success prototype-input-digests.log sha256sum \
        "${PROTOTYPE_ROOT}/rust-toolchain.toml" \
        "${PROTOTYPE_ROOT}/Cargo.toml" \
        "${PROTOTYPE_ROOT}/Cargo.lock" \
        "${PROTOTYPE_ROOT}/crates/compat-probe/Cargo.toml" \
        "${PROTOTYPE_ROOT}/crates/compat-probe/src/lib.rs" \
        "${PROTOTYPE_ROOT}/crates/compat-probe/src/main.rs" \
        "${PROTOTYPE_ROOT}/dependency-license-inventory.json" \
        "${PROTOTYPE_ROOT}/security-lock.json"
}

run_fresh_resolution() {
    cd -- "${PROTOTYPE_ROOT}"
    expect_success fresh-resolution.log bash -c '
        set -euo pipefail
        project="$(mktemp -d /tmp/statqed-sq0002-rust-resolution.XXXXXX)"
        cleanup() { rm -rf -- "${project}"; }
        trap cleanup EXIT
        cp -R -- "$1/Cargo.toml" "$1/crates" "$1/rust-toolchain.toml" "${project}/"
        cd -- "${project}"
        "$2" +1.97.1 generate-lockfile
        observed="$(sha256sum Cargo.lock | awk "{print \$1}")"
        expected="$(sha256sum "$1/Cargo.lock" | awk "{print \$1}")"
        printf "reviewed_lock_sha256=%s\nfresh_resolution_sha256=%s\n" "${expected}" "${observed}"
        test "${observed}" = "${expected}"
    ' _ "${PROTOTYPE_ROOT}" "${CARGO_BIN}"
    expect_success fetch-locked.log "${CARGO_BIN}" +1.97.1 fetch --locked
}

run_development_checks() {
    cd -- "${PROTOTYPE_ROOT}"
    expect_success development-verify.log env \
        STATQED_RUST_CACHE_ROOT="${CACHE_ROOT}" \
        "${PROTOTYPE_ROOT}/verify-probe.sh" development
}

run_msrv_checks() {
    cd -- "${PROTOTYPE_ROOT}"
    expect_success msrv-verify.log env \
        STATQED_RUST_CACHE_ROOT="${CACHE_ROOT}" \
        "${PROTOTYPE_ROOT}/verify-probe.sh" msrv
}

run_policy_and_rejection_checks() {
    local target
    local result=0
    target="$(mktemp -d /tmp/statqed-sq0002-rust-rejections.XXXXXX)"
    cd -- "${PROTOTYPE_ROOT}"
    if ! expect_failure unsafe-policy-rejection.log env CARGO_TARGET_DIR="${target}/unsafe" "${CARGO_BIN}" +1.97.1 check --offline --manifest-path rejections/unsafe-code/Cargo.toml; then
        result=1
    fi
    if ! expect_success archive-8.1-dev-compatible.log env CARGO_TARGET_DIR="${target}/archive-dev" "${CARGO_BIN}" +1.97.1 check --offline --locked --manifest-path rejections/archive-msrv/Cargo.toml; then
        result=1
    fi
    if ! expect_failure archive-8.1-msrv-rejection.log env CARGO_TARGET_DIR="${target}/archive-msrv" "${CARGO_BIN}" +1.85.1 check --offline --locked --manifest-path rejections/archive-msrv/Cargo.toml; then
        result=1
    fi
    rm -rf -- "${target}"
    return "${result}"
}

run_security_and_license_checks() {
    cd -- "${PROTOTYPE_ROOT}"
    expect_success security-verify.log env \
        STATQED_RUST_CACHE_ROOT="${CACHE_ROOT}" \
        STATQED_CARGO_AUDIT_ARCHIVE="${STATQED_CARGO_AUDIT_ARCHIVE:-/tmp/statqed-sq0002-cargo-audit-0.22.2.tgz}" \
        STATQED_RUSTSEC_ARCHIVE="${STATQED_RUSTSEC_ARCHIVE:-/tmp/statqed-sq0002-rustsec-d91a8fc.tar.gz}" \
        "${PROTOTYPE_ROOT}/verify-probe.sh" security
}

run_stale_lock_rejection() {
    cd -- "${PROTOTYPE_ROOT}"
    expect_failure reviewed-stale-lock-rejection.log bash -c '
        printf "%s  %s\n" \
            "8db0b054ed47a9eb63678ea96644fd5791acd1cab0a3441754c0d70229b55040" \
            "$1" | sha256sum -c -
    ' _ "${PROTOTYPE_ROOT}/Cargo.lock"
}

run_registry_observations() {
    cd -- "${PROTOTYPE_ROOT}"
    expect_success candidate-registry-metadata.log bash -c '
        for specification in \
            serde@1.0.229 serde_json@1.0.151 arrow@59.1.0 \
            zip@7.2.0 zip@8.1.0 zip@9.0.0-pre2 blake3@1.8.5 \
            sha2@0.11.0 clap@4.6.5 cargo-audit@0.22.2
        do
            "$1" +1.97.1 info "${specification}"
        done
    ' _ "${CARGO_BIN}"
}

case "${1:-all}" in
    install)
        install_toolchains
        ;;
    checks)
        record_environment
        run_fresh_resolution
        run_development_checks
        run_msrv_checks
        run_policy_and_rejection_checks
        ;;
    development)
        record_environment
        run_fresh_resolution
        run_development_checks
        ;;
    msrv)
        record_environment
        run_msrv_checks
        ;;
    security)
        run_security_and_license_checks
        ;;
    policy)
        run_policy_and_rejection_checks
        ;;
    stale-lock)
        run_stale_lock_rejection
        ;;
    metadata)
        run_registry_observations
        ;;
    all)
        install_toolchains
        record_environment
        run_fresh_resolution
        run_development_checks
        run_msrv_checks
        run_policy_and_rejection_checks
        run_security_and_license_checks
        run_registry_observations
        ;;
    *)
        printf 'usage: %s [install|checks|development|msrv|policy|stale-lock|security|metadata|all]\n' "$0" >&2
        exit 2
        ;;
esac
