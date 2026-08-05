#!/usr/bin/env bash
set -euo pipefail

readonly probe_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly python_archive=/tmp/statqed-sq0002-python-pinned-assets/downloads/cpython-3.14.7+20260805.tar.gz
readonly pyarrow_wheel=/tmp/statqed-sq0002-arrow-assets/pyarrow-25.0.0-cp314-cp314-manylinux_2_28_x86_64.whl
readonly uv_bin=/tmp/statqed-sq0002-python-tools/uv
readonly rust_cache=/tmp/statqed-sq0002-rust-cache
readonly rustup_home="${rust_cache}/rustup"
readonly cargo_home="${rust_cache}/cargo"

for artifact in "${python_archive}" "${pyarrow_wheel}" "${uv_bin}"; do
    [ -f "${artifact}" ] || { printf 'UNAVAILABLE: required hash-bound preparation is absent: %s\n' "${artifact}" >&2; exit 77; }
done
[ -d "${rustup_home}" ] && [ -d "${cargo_home}" ] || { printf 'UNAVAILABLE: exact Rust toolchain/cache preparation is absent\n' >&2; exit 77; }
printf '%s  %s\n' a3a4e4b81b138960c7c546694df8a77578c0b6aa46d47e96f49b9e10e8f860c9 "${python_archive}" | /usr/bin/sha256sum --check --status
printf '%s  %s\n' 447df764beb07c544f0178a5f6b70ef44b9ecf382b3cdfad4c2d7867353c3887 "${pyarrow_wheel}" | /usr/bin/sha256sum --check --status
printf '%s  %s\n' da15297d6879b2cfbe5ea3cb03725c1613d51ba72892cc996468d871f0a532fb "${uv_bin}" | /usr/bin/sha256sum --check --status
printf '%s  %s\n' b48ca90c270c065266d625e8d26a024217ac1559247d530de6b9348969bedaed "${probe_root}/Cargo.lock" | /usr/bin/sha256sum --check --status
printf '%s  %s\n' bfd009e1da9d19fc65296c52f9d94b7666f468ce146f2437de435984a59439f3 "${probe_root}/probe-requirements.lock" | /usr/bin/sha256sum --check --status

readonly rustup_bin="$(command -v rustup || true)"
readonly rustc_bin="$(command -v rustc || true)"
readonly cargo_bin="$(command -v cargo || true)"
for tool in "${rustup_bin}" "${rustc_bin}" "${cargo_bin}"; do
    [ -x "${tool}" ] || { printf 'UNAVAILABLE: rustup proxy tool is absent\n' >&2; exit 77; }
done
RUSTUP_HOME="${rustup_home}" "${rustup_bin}" toolchain list | /usr/bin/grep -F '1.97.1-x86_64-unknown-linux-gnu' >/dev/null || { printf 'UNAVAILABLE: Rust 1.97.1 is absent\n' >&2; exit 77; }
RUSTUP_HOME="${rustup_home}" "${rustc_bin}" +1.97.1 --version --verbose | /usr/bin/grep -Fx 'commit-hash: 8bab26f4f68e0e26f0bb7960be334d5b520ea452' >/dev/null
RUSTUP_HOME="${rustup_home}" "${cargo_bin}" +1.97.1 --version --verbose | /usr/bin/grep -Fx 'commit-hash: c980f4866141969fab6254a680546a277789d6f0' >/dev/null

readonly verify_root="$(mktemp -d /tmp/statqed-sq0002-arrow-verify-XXXXXX)"
cleanup() {
    case "${verify_root}" in
        /tmp/statqed-sq0002-arrow-verify-*) /bin/rm -rf -- "${verify_root}" ;;
        *) printf 'refusing unsafe cleanup target: %s\n' "${verify_root}" >&2 ;;
    esac
}
trap cleanup EXIT
/bin/mkdir -p "${verify_root}/runtime" "${verify_root}/uv-cache" "${verify_root}/xdg-cache" "${verify_root}/home"
/usr/bin/tar --extract --gzip --file "${python_archive}" --directory "${verify_root}/runtime" --no-same-owner --no-same-permissions
readonly python_bin="${verify_root}/runtime/python/bin/python3.14"
[ -x "${python_bin}" ] || { printf 'verified archive did not contain CPython 3.14 runtime\n' >&2; exit 1; }
"${python_bin}" --version 2>&1 | /usr/bin/grep -Fx 'Python 3.14.7' >/dev/null

STATQED_ARROW_PYTHON="${python_bin}" \
STATQED_UV="${uv_bin}" \
STATQED_PYARROW_WHEEL="${pyarrow_wheel}" \
STATQED_ARROW_CARGO_HOME="${cargo_home}" \
RUSTUP_HOME="${rustup_home}" \
RUSTUP_TOOLCHAIN=1.97.1 \
CARGO_NET_OFFLINE=true \
HOME="${verify_root}/home" \
UV_CACHE_DIR="${verify_root}/uv-cache" \
XDG_CACHE_HOME="${verify_root}/xdg-cache" \
LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONHASHSEED=0 \
    /usr/bin/bash "${probe_root}/run-probes.sh"
printf 'verified hash-bound Arrow cross-lineage probe\n'
