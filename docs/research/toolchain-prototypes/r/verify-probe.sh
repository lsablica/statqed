#!/usr/bin/env bash
set -euo pipefail

readonly probe_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly repository_root="$(cd -- "${probe_root}/../../../.." && pwd)"
readonly mode="${1:-}"
readonly verify_root="$(mktemp -d /tmp/statqed-sq0002-r-verify-XXXXXX)"
cleanup() {
    case "${verify_root}" in
        /tmp/statqed-sq0002-r-verify-*) /bin/rm -rf -- "${verify_root}" ;;
        *) printf 'refusing unsafe cleanup target: %s\n' "${verify_root}" >&2 ;;
    esac
}
trap cleanup EXIT
/bin/mkdir -p "${verify_root}/logs"

export STATQED_R_STATE_ROOT="${verify_root}/state"
export STATQED_R_LOG_DIR="${verify_root}/logs"
export STATQED_R_RUN_TAG=verify
export STATQED_R_RUN_INSTANCE="${mode}"
export XDG_CACHE_HOME="${verify_root}/xdg-cache"
export CONDA_PKGS_DIRS="${verify_root}/state/pkgs"
export CONDA_ENVS_PATH="${verify_root}/state/envs"
export HOME="${verify_root}/home"
export R_ENVIRON_USER=/dev/null R_PROFILE_USER=/dev/null
export LANG=C.UTF-8 LC_ALL=C.UTF-8 TZ=UTC
/bin/mkdir -p "${HOME}" "${XDG_CACHE_HOME}"

case "${mode}" in
    development)
        command -v R >/dev/null || { printf 'UNAVAILABLE: R is not installed\n' >&2; exit 77; }
        R --version 2>&1 | /usr/bin/grep -F 'R version 4.6.1' >/dev/null || {
            printf 'UNAVAILABLE: installed R is not 4.6.1\n' >&2
            exit 77
        }
        readonly source_cache=/tmp/statqed-sq0002-r/dev-cran-sources
        [ -d "${source_cache}" ] || { printf 'UNAVAILABLE: R source preparation is absent\n' >&2; exit 77; }
        printf '%s  %s\n' 34578de2ad22a24e2ffb1f5584731618f9862a1a063623b6c5523a635a5f9721 "${probe_root}/development-cran-source-lock.tsv" | /usr/bin/sha256sum --check --status
        export STATQED_R_DEV_SOURCE_CACHE="${source_cache}"
        /usr/bin/bash "${probe_root}/run-probes.sh" development
        /usr/bin/grep -F 'Status: OK' "${verify_root}/logs/development-check-tarball.stdout" >/dev/null
        /usr/bin/grep -F 'installed smoke ok' "${verify_root}/logs/development-installed-smoke.stdout" >/dev/null
        ;;
    floor)
        command -v conda >/dev/null || { printf 'UNAVAILABLE: conda is not installed\n' >&2; exit 77; }
        readonly source_cache=/tmp/statqed-sq0002-r/pkgs
        [ -d "${source_cache}" ] || { printf 'UNAVAILABLE: conda archive preparation is absent\n' >&2; exit 77; }
        readonly retained_lock="${repository_root}/docs/research/toolchain-prototypes/logs/r/run-20260803/floor-conda-explicit-lock.stdout"
        readonly local_lock="${verify_root}/floor-local-explicit-lock.txt"
        /usr/bin/python3 "${probe_root}/verify_conda_lock.py" --prepare \
            --lock "${retained_lock}" --cache "${source_cache}" \
            --destination "${CONDA_PKGS_DIRS}" --local-lock "${local_lock}"
        readonly prefix="${verify_root}/state/envs/r-4.4.3"
        conda create --offline --yes --prefix "${prefix}" --file "${local_lock}"
        export STATQED_R_FLOOR_PREFIX="${prefix}"
        /usr/bin/bash "${probe_root}/run-probes.sh" floor
        /usr/bin/python3 "${probe_root}/verify_conda_lock.py" --compare \
            --lock "${retained_lock}" --observed "${verify_root}/logs/floor-conda-explicit-lock.stdout"
        /usr/bin/grep -F 'R version 4.4.3' "${verify_root}/logs/floor-r-version.stdout" >/dev/null
        /usr/bin/grep -F 'Status: OK' "${verify_root}/logs/floor-check-tarball.stdout" >/dev/null
        /usr/bin/grep -F 'installed smoke ok' "${verify_root}/logs/floor-installed-smoke.stdout" >/dev/null
        ;;
    *)
        printf 'usage: %s {development|floor}\n' "$0" >&2
        exit 64
        ;;
esac
printf 'verified hash-bound R %s probe\n' "${mode}"
