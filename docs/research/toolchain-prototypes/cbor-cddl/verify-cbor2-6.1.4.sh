#!/usr/bin/env bash
set -euo pipefail

readonly probe_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly python_archive=/tmp/statqed-sq0002-python-pinned-assets/downloads/cpython-3.14.7+20260805.tar.gz
readonly cbor2_wheel=/tmp/statqed-sq0002-python-assets/cbor2-6.1.4-cp314-cp314-manylinux_2_28_x86_64.whl
readonly uv_bin=/tmp/statqed-sq0002-python-tools/uv

for artifact in "${python_archive}" "${cbor2_wheel}" "${uv_bin}"; do
    [ -f "${artifact}" ] || {
        printf 'UNAVAILABLE: required hash-bound preparation is absent: %s\n' "${artifact}" >&2
        exit 77
    }
done
printf '%s  %s\n' a3a4e4b81b138960c7c546694df8a77578c0b6aa46d47e96f49b9e10e8f860c9 "${python_archive}" | /usr/bin/sha256sum --check --status
printf '%s  %s\n' c0f5f2d6d3b58e44146860c049f3c082207a4005588b8926d51bf937ab66773c "${cbor2_wheel}" | /usr/bin/sha256sum --check --status
printf '%s  %s\n' da15297d6879b2cfbe5ea3cb03725c1613d51ba72892cc996468d871f0a532fb "${uv_bin}" | /usr/bin/sha256sum --check --status
printf '%s  %s\n' 547717250bbd70c0857bedfd3a0ab7ddf8f78e86f1b0c523b5dc6ed510de7667 "${probe_root}/cbor2-6.1.4-requirements.lock" | /usr/bin/sha256sum --check --status

readonly verify_root="$(mktemp -d /tmp/statqed-sq0002-cbor2-verify-XXXXXX)"
cleanup() {
    case "${verify_root}" in
        /tmp/statqed-sq0002-cbor2-verify-*) /bin/rm -rf -- "${verify_root}" ;;
        *) printf 'refusing unsafe cleanup target: %s\n' "${verify_root}" >&2 ;;
    esac
}
trap cleanup EXIT
/bin/mkdir -p "${verify_root}/runtime" "${verify_root}/wheelhouse" "${verify_root}/home" "${verify_root}/uv-cache" "${verify_root}/xdg-cache"
/usr/bin/tar --extract --gzip --file "${python_archive}" --directory "${verify_root}/runtime" --no-same-owner --no-same-permissions
readonly python_bin="${verify_root}/runtime/python/bin/python3.14"
[ -x "${python_bin}" ] || { printf 'verified archive did not contain CPython 3.14\n' >&2; exit 1; }
"${python_bin}" --version 2>&1 | /usr/bin/grep -Fx 'Python 3.14.7' >/dev/null
/bin/cp -- "${cbor2_wheel}" "${verify_root}/wheelhouse/"

HOME="${verify_root}/home" UV_CACHE_DIR="${verify_root}/uv-cache" XDG_CACHE_HOME="${verify_root}/xdg-cache" \
    "${uv_bin}" venv --no-project --python "${python_bin}" --no-python-downloads "${verify_root}/venv"
HOME="${verify_root}/home" UV_CACHE_DIR="${verify_root}/uv-cache" XDG_CACHE_HOME="${verify_root}/xdg-cache" \
    "${uv_bin}" pip install --python "${verify_root}/venv/bin/python" --no-cache --no-index \
    --find-links "${verify_root}/wheelhouse" --require-hashes --only-binary=:all: \
    --requirements "${probe_root}/cbor2-6.1.4-requirements.lock"
HOME="${verify_root}/home" XDG_CACHE_HOME="${verify_root}/xdg-cache" LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONHASHSEED=0 \
    "${verify_root}/venv/bin/python" "${probe_root}/probe_cbor2_6_1_4.py"
printf 'verified cbor2 6.1.4 security-regression probe\n'
