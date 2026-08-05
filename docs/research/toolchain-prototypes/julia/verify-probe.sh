#!/usr/bin/env bash
set -euo pipefail

readonly probe_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly mode="${1:-}"
case "${mode}" in
    development)
        readonly archive=/tmp/julia-1.12.6-linux-x86_64.tar.gz
        readonly expected_sha=bbabf3bef19421a9dbd24a767d807606ab85e444323b5a1c73ffe293fa3d079a
        readonly expected_version=1.12.6
        readonly archive_dir=julia-1.12.6
        readonly binary_variable=SQ0002_JULIA_DEVELOPMENT_BINARY
        readonly archive_variable=SQ0002_JULIA_DEVELOPMENT_ARCHIVE
        ;;
    floor)
        readonly archive=/tmp/julia-1.10.11-linux-x86_64.tar.gz
        readonly expected_sha=fb49c6b174600cd2051e37ba3f7330f8acf06dd00bce609bab6611387fdb37bf
        readonly expected_version=1.10.11
        readonly archive_dir=julia-1.10.11
        readonly binary_variable=SQ0002_JULIA_FLOOR_BINARY
        readonly archive_variable=SQ0002_JULIA_FLOOR_ARCHIVE
        ;;
    *) printf 'usage: %s {development|floor}\n' "$0" >&2; exit 64 ;;
esac
[ -f "${archive}" ] || { printf 'UNAVAILABLE: exact Julia archive is absent: %s\n' "${archive}" >&2; exit 77; }
printf '%s  %s\n' "${expected_sha}" "${archive}" | /usr/bin/sha256sum --check --status

readonly verify_root="$(mktemp -d /tmp/statqed-sq0002-julia-verify-XXXXXX)"
cleanup() {
    case "${verify_root}" in
        /tmp/statqed-sq0002-julia-verify-*) /bin/rm -rf -- "${verify_root}" ;;
        *) printf 'refusing unsafe cleanup target: %s\n' "${verify_root}" >&2 ;;
    esac
}
trap cleanup EXIT
/bin/mkdir -p "${verify_root}/runtime" "${verify_root}/logs" "${verify_root}/home"
/usr/bin/tar --extract --gzip --file "${archive}" --directory "${verify_root}/runtime" --no-same-owner --no-same-permissions
readonly julia_bin="${verify_root}/runtime/${archive_dir}/bin/julia"
[ -x "${julia_bin}" ] || { printf 'verified archive lacks Julia executable\n' >&2; exit 1; }
"${julia_bin}" --version | /usr/bin/grep -Fx "julia version ${expected_version}" >/dev/null

export "${binary_variable}=${julia_bin}"
export "${archive_variable}=${archive}"
export SQ0002_JULIA_LOG_ROOT="${verify_root}/logs"
export HOME="${verify_root}/home"
export LANG=C.UTF-8 LC_ALL=C.UTF-8 TZ=UTC
/usr/bin/python3 "${probe_root}/run_probes.py" --run-id "${mode}" --mode "${mode}"
/usr/bin/grep -F 'Test Summary:' "${verify_root}/logs/${mode}/$([ "${mode}" = development ] && printf development-julia-1-12-6-linux-x86-64 || printf floor-lts-julia-1-10-11-linux-x86-64)-test.stderr" >/dev/null
printf 'verified hash-bound Julia %s probe\n' "${mode}"
