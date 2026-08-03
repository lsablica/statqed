#!/usr/bin/env bash
set -euo pipefail

readonly PROTOTYPE_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_DIR="${PROTOTYPE_ROOT}/../logs/rust/run-20260803"
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

mkdir -p -- "${LOG_DIR}" "${RUSTUP_HOME}" "${CARGO_HOME}" "${CACHE_ROOT}/target"

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
    # rustup requires CARGO_HOME to identify the directory containing its proxy
    # binary. Toolchains remain isolated by RUSTUP_HOME; Cargo registry/git data
    # remain isolated for all Cargo commands below.
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
}

run_online_resolution() {
    cd -- "${PROTOTYPE_ROOT}"
    expect_success dev-generate-lockfile-online.log "${CARGO_BIN}" +1.97.1 generate-lockfile
    expect_success dev-fetch-locked-online.log "${CARGO_BIN}" +1.97.1 fetch --locked
    expect_success dev-metadata-locked.log "${CARGO_BIN}" +1.97.1 metadata --locked --format-version 1
    cp -- "${LOG_DIR}/dev-metadata-locked.stdout" "${LOG_DIR}/metadata-dev.json"
    expect_success cargo-lock-digest.log sha256sum Cargo.lock
    expect_success prototype-input-digests.log sha256sum rust-toolchain.toml Cargo.toml crates/compat-probe/Cargo.toml crates/compat-probe/src/lib.rs crates/compat-probe/src/main.rs
}

run_development_checks() {
    cd -- "${PROTOTYPE_ROOT}"
    export CARGO_NET_OFFLINE=true
    export CARGO_TARGET_DIR="${CACHE_ROOT}/target/dev-1.97.1"
    expect_success dev-metadata-offline.log "${CARGO_BIN}" +1.97.1 metadata --locked --offline --format-version 1
    expect_success dev-fmt-check.log "${CARGO_BIN}" +1.97.1 fmt --all -- --check
    expect_success dev-clippy-deny-warnings.log "${CARGO_BIN}" +1.97.1 clippy --locked --offline --workspace --all-targets --all-features -- -D warnings
    expect_success dev-tests.log "${CARGO_BIN}" +1.97.1 test --locked --offline --workspace --all-targets --all-features
    expect_success dev-run.log "${CARGO_BIN}" +1.97.1 run --locked --offline --package statqed-rust-compat-probe -- --json
    unset CARGO_NET_OFFLINE
    unset CARGO_TARGET_DIR
}

run_msrv_checks() {
    cd -- "${PROTOTYPE_ROOT}"
    export CARGO_NET_OFFLINE=true
    export CARGO_TARGET_DIR="${CACHE_ROOT}/target/msrv-1.85.1"
    expect_success msrv-metadata-offline.log "${CARGO_BIN}" +1.85.1 metadata --locked --offline --format-version 1
    expect_success msrv-fmt-check.log "${CARGO_BIN}" +1.85.1 fmt --all -- --check
    expect_success msrv-clippy-deny-warnings.log "${CARGO_BIN}" +1.85.1 clippy --locked --offline --workspace --all-targets --all-features -- -D warnings
    expect_success msrv-tests.log "${CARGO_BIN}" +1.85.1 test --locked --offline --workspace --all-targets --all-features
    expect_success msrv-run.log "${CARGO_BIN}" +1.85.1 run --locked --offline --package statqed-rust-compat-probe -- --json
    unset CARGO_NET_OFFLINE
    unset CARGO_TARGET_DIR
}

run_policy_and_rejection_checks() {
    cd -- "${PROTOTYPE_ROOT}"
    export CARGO_TARGET_DIR="${CACHE_ROOT}/target/rejections"
    expect_failure unsafe-policy-rejection.log "${CARGO_BIN}" +1.97.1 check --manifest-path rejections/unsafe-code/Cargo.toml
    expect_success archive-8.1-dev-compatible.log "${CARGO_BIN}" +1.97.1 check --manifest-path rejections/archive-msrv/Cargo.toml
    expect_failure archive-8.1-msrv-rejection.log "${CARGO_BIN}" +1.85.1 check --manifest-path rejections/archive-msrv/Cargo.toml
    unset CARGO_TARGET_DIR
}

run_security_and_license_checks() {
    cd -- "${PROTOTYPE_ROOT}"
    export CARGO_TARGET_DIR="${CACHE_ROOT}/target/cargo-audit-install"
    expect_success cargo-audit-install.log "${CARGO_BIN}" +1.97.1 install cargo-audit --version 0.22.2 --locked --root "${CACHE_ROOT}/cargo-audit"
    unset CARGO_TARGET_DIR
    expect_success cargo-audit-version.log "${CACHE_ROOT}/cargo-audit/bin/cargo-audit" audit --version
    expect_success cargo-audit-rustsec.log "${CACHE_ROOT}/cargo-audit/bin/cargo-audit" audit --file Cargo.lock --json
    expect_success dependency-tree.log "${CARGO_BIN}" +1.97.1 tree --locked --workspace --all-features
    expect_success dependency-license-inventory.log jq -c '[.packages[] | {name, version, license, rust_version, repository, source}] | sort_by(.name, .version)' "${LOG_DIR}/metadata-dev.json"
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
        run_online_resolution
        run_development_checks
        run_msrv_checks
        run_policy_and_rejection_checks
        ;;
    development)
        record_environment
        run_online_resolution
        run_development_checks
        ;;
    msrv)
        record_environment
        run_msrv_checks
        ;;
    security)
        run_security_and_license_checks
        ;;
    metadata)
        run_registry_observations
        ;;
    all)
        install_toolchains
        record_environment
        run_online_resolution
        run_development_checks
        run_msrv_checks
        run_policy_and_rejection_checks
        run_security_and_license_checks
        run_registry_observations
        ;;
    *)
        printf 'usage: %s [install|checks|development|msrv|security|metadata|all]\n' "$0" >&2
        exit 2
        ;;
esac
