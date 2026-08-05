#!/usr/bin/env bash
set -euo pipefail

readonly probe_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly mode="${1:-}"
readonly asset_root=/tmp/statqed-sq0002-python-pinned-assets/downloads
readonly uv_bin=/tmp/statqed-sq0002-python-tools/uv
readonly wheelhouse=/tmp/statqed-sq0002-python-wheelhouse

case "${mode}" in
    development)
        readonly archive="${asset_root}/cpython-3.14.7+20260805.tar.gz"
        readonly archive_sha=a3a4e4b81b138960c7c546694df8a77578c0b6aa46d47e96f49b9e10e8f860c9
        readonly expected_version='Python 3.14.7'
        readonly runtime_relative=python/bin/python3.14
        readonly explicit_variable=SQ0002_PYTHON_DEVELOPMENT
        ;;
    floor)
        readonly archive="${asset_root}/cpython-3.11.15+20260718.tar.gz"
        readonly archive_sha=23ccae6f1ff73e8aa8378436f869da003b8eb7d6c95f2bc706f494115ba1447d
        readonly expected_version='Python 3.11.15'
        readonly runtime_relative=python/bin/python3.11
        readonly explicit_variable=SQ0002_PYTHON_FLOOR
        ;;
    *)
        printf 'usage: %s {development|floor}\n' "$0" >&2
        exit 64
        ;;
esac

for required in "${archive}" "${uv_bin}" "${wheelhouse}"; do
    [ -e "${required}" ] || {
        printf 'UNAVAILABLE: hash-bound Python preparation is absent: %s\n' "${required}" >&2
        exit 77
    }
done
printf '%s  %s\n' "${archive_sha}" "${archive}" | /usr/bin/sha256sum --check --status
printf '%s  %s\n' da15297d6879b2cfbe5ea3cb03725c1613d51ba72892cc996468d871f0a532fb "${uv_bin}" | /usr/bin/sha256sum --check --status
printf '%s  %s\n' 0fcf65ff2348ef6356caad22169b7b907f6899069749b70660ef76e7ba7730b3 "${probe_root}/probe-requirements.lock" | /usr/bin/sha256sum --check --status

readonly verify_root="$(mktemp -d /tmp/statqed-sq0002-python-verify-XXXXXX)"
cleanup() {
    case "${verify_root}" in
        /tmp/statqed-sq0002-python-verify-*) /bin/rm -rf -- "${verify_root}" ;;
        *) printf 'refusing unsafe cleanup target: %s\n' "${verify_root}" >&2 ;;
    esac
}
trap cleanup EXIT
/bin/mkdir -p "${verify_root}/runtime" "${verify_root}/logs" "${verify_root}/cache" "${verify_root}/pip-cache"
/usr/bin/tar --extract --gzip --file "${archive}" --directory "${verify_root}/runtime" --no-same-owner --no-same-permissions
readonly python_bin="${verify_root}/runtime/${runtime_relative}"
[ -x "${python_bin}" ] || { printf 'verified archive lacks %s\n' "${runtime_relative}" >&2; exit 1; }
"${python_bin}" --version 2>&1 | /usr/bin/grep -Fx "${expected_version}" >/dev/null

export "${explicit_variable}=${python_bin}"
export SQ0002_PYTHON_TMP="${verify_root}/work"
export SQ0002_PYTHON_LOG_ROOT="${verify_root}/logs"
export SQ0002_PYTHON_WHEELHOUSE="${wheelhouse}"
export SQ0002_UV="${uv_bin}"
export UV_CACHE_DIR="${verify_root}/cache"
export PIP_CACHE_DIR="${verify_root}/pip-cache"
export HOME="${verify_root}/home"
export XDG_CACHE_HOME="${verify_root}/xdg-cache"
export LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONHASHSEED=0
/bin/mkdir -p "${HOME}" "${XDG_CACHE_HOME}"

"${python_bin}" "${probe_root}/run_probes.py" --probe "${mode}"
/usr/bin/grep -F '2 passed' "${verify_root}/logs/${mode}-$(cut -d' ' -f2 <<<"${expected_version}" | tr . -)-pytest.stdout" >/dev/null
printf 'verified hash-bound Python %s probe\n' "${mode}"
