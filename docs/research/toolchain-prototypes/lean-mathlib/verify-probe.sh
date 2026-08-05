#!/usr/bin/env bash
set -euo pipefail

readonly PROBE_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly EXPECTED_LEAN_TOOLCHAIN="leanprover/lean4:v4.32.2"
readonly EXPECTED_LEAN_COMMIT="f3b06c705e6c85f5314019d5d3baab0fec5b580c"
readonly EXPECTED_MATHLIB_COMMIT="905b95818eb32af7874a58b427f50c1711a5e96c"
readonly EXPECTED_LAKE_VERSION="Lake version 5.0.0-src+f3b06c7 (Lean version 4.32.2)"
readonly EXPECTED_AXIOMS="[propext, Classical.choice, Quot.sound]"
readonly ELAN_ROOT="${STATQED_LEAN_ELAN_HOME:-/tmp/statqed-sq0002-elan-home}"

scratch_roots=""
cleanup() {
    local scratch
    for scratch in $scratch_roots; do
        case "$scratch" in
            /tmp/statqed-sq0002-lean-probe.*) rm -rf -- "$scratch" ;;
            *) printf 'refusing unsafe cleanup target: %s\n' "$scratch" >&2 ;;
        esac
    done
}
trap cleanup EXIT

new_scratch() {
    scratch=$(mktemp -d /tmp/statqed-sq0002-lean-probe.XXXXXX)
    scratch_roots="$scratch_roots $scratch"
}

check_sha256() {
    local expected=$1
    local path=$2
    local actual
    actual=$(sha256sum "$path" | awk '{print $1}')
    if [[ "$actual" != "$expected" ]]; then
        printf 'unexpected SHA-256 for %s: expected %s, got %s\n' "$path" "$expected" "$actual" >&2
        return 1
    fi
}

run_static_controls() {
    local scratch
    local mutated

    check_sha256 ff2ecf31ced1cb1cff770a54d281c92a9c6bd9fa3826b243eac4dac2d5dca93f \
        "$PROBE_ROOT/recommended/lake-manifest.json"
    check_sha256 0dc9be6725815434799a9ed732f335924ac4daf6f9ff38c59bae4ed2cd8be73c \
        "$PROBE_ROOT/no-binary-cache/lake-manifest.json"
    check_sha256 0a30181171c157d4034b6e286b30dc79420c39d2010f4ff25940bb1369393637 \
        "$PROBE_ROOT/rejected-lean-4.32.1-mathlib-4.32.2/lake-manifest.json"

    grep -Fxq "$EXPECTED_LEAN_TOOLCHAIN" "$PROBE_ROOT/recommended/lean-toolchain"
    grep -Fxq "$EXPECTED_LEAN_TOOLCHAIN" "$PROBE_ROOT/no-binary-cache/lean-toolchain"
    grep -Fq "$EXPECTED_MATHLIB_COMMIT" "$PROBE_ROOT/recommended/lakefile.toml"
    grep -Fq "$EXPECTED_MATHLIB_COMMIT" "$PROBE_ROOT/no-binary-cache/lakefile.toml"

    new_scratch
    mutated="$scratch/mutated-lake-manifest.json"
    cp -- "$PROBE_ROOT/recommended/lake-manifest.json" "$mutated"
    sed -i "s/$EXPECTED_MATHLIB_COMMIT/520045ab14e26149ee970e2e617ca04b09bde5d6/g" "$mutated"
    if cmp -s -- "$PROBE_ROOT/recommended/lake-manifest.json" "$mutated"; then
        printf 'mutated manifest unexpectedly matched the reviewed manifest\n' >&2
        return 1
    fi
    printf 'static controls: exact locks and altered-manifest rejection passed\n'
}

require_preparation() {
    local mode=$1
    if [[ ! -x "$ELAN_ROOT/bin/elan" ]]; then
        printf 'Lean probe preparation unavailable: expected %s/bin/elan\n' "$ELAN_ROOT" >&2
        return 77
    fi
    export ELAN_HOME="$ELAN_ROOT"
    export PATH="$ELAN_ROOT/bin:/usr/bin:/bin"
    export LANG=C.UTF-8
    export LC_ALL=C.UTF-8
    export TZ=UTC

    local lean_output
    local lake_output
    local toolchains
    toolchains=$(elan toolchain list)
    if ! grep -Fq "$EXPECTED_LEAN_TOOLCHAIN" <<<"$toolchains"; then
        printf 'Lean probe preparation unavailable: %s is not installed in %s\n' \
            "$EXPECTED_LEAN_TOOLCHAIN" "$ELAN_ROOT" >&2
        return 77
    fi
    if [[ "$mode" == mismatch || "$mode" == all ]] && \
        ! grep -Fq 'leanprover/lean4:v4.32.1' <<<"$toolchains"; then
        printf 'Lean mismatch preparation unavailable: leanprover/lean4:v4.32.1 is not installed in %s\n' \
            "$ELAN_ROOT" >&2
        return 77
    fi
    lean_output=$(elan run "$EXPECTED_LEAN_TOOLCHAIN" lean --version)
    lake_output=$(elan run "$EXPECTED_LEAN_TOOLCHAIN" lake --version)
    printf '%s\n%s\n' "$lean_output" "$lake_output"
    grep -Fq "$EXPECTED_LEAN_COMMIT" <<<"$lean_output"
    grep -Fxq "$EXPECTED_LAKE_VERSION" <<<"$lake_output"
}

copy_project_without_manifest() {
    local fixture=$1
    local destination=$2
    mkdir -p -- "$destination"
    cp -- "$fixture/lakefile.toml" "$fixture/lean-toolchain" "$destination/"
    find "$fixture" -maxdepth 1 -type f -name '*.lean' -exec cp -- '{}' "$destination/" ';'
}

compare_regenerated_manifest() {
    local fixture=$1
    local destination=$2
    if ! cmp -s -- "$fixture/lake-manifest.json" "$destination/lake-manifest.json"; then
        printf 'regenerated manifest differs from reviewed fixture: %s\n' "$fixture" >&2
        diff -u -- "$fixture/lake-manifest.json" "$destination/lake-manifest.json" >&2 || true
        return 1
    fi
    printf 'manifest regeneration matched: %s\n' "${fixture#$PROBE_ROOT/}"
}

check_axioms() {
    local project=$1
    local source=$2
    local theorem=$3
    local output
    local expected_line

    output=$(cd -- "$project" && lake env lean "$source" 2>&1)
    printf '%s\n' "$output"
    expected_line="'$theorem' depends on axioms: $EXPECTED_AXIOMS"
    grep -Fxq "$expected_line" <<<"$output"
    if grep -Fq 'sorryAx' <<<"$output"; then
        printf 'unexpected sorryAx in successful axiom report\n' >&2
        return 1
    fi
}

run_recommended() {
    local fixture="$PROBE_ROOT/recommended"
    local scratch
    local project
    new_scratch
    project="$scratch/recommended"
    copy_project_without_manifest "$fixture" "$project"
    (
        cd -- "$project"
        lake update --keep-toolchain
        lake build
    )
    compare_regenerated_manifest "$fixture" "$project"
    check_axioms "$project" StatQEDLeanProbe.lean StatQEDLeanProbe.pmf_total_mass
}

run_no_binary_cache() {
    local fixture="$PROBE_ROOT/no-binary-cache"
    local scratch
    local project
    new_scratch
    project="$scratch/no-binary-cache"
    copy_project_without_manifest "$fixture" "$project"
    (
        cd -- "$project"
        MATHLIB_NO_CACHE_ON_UPDATE=1 LAKE_NO_CACHE=1 lake update --keep-toolchain
        MATHLIB_NO_CACHE_ON_UPDATE=1 LAKE_NO_CACHE=1 lake build
    )
    compare_regenerated_manifest "$fixture" "$project"
    check_axioms "$project" StatQEDLeanNoBinaryCacheProbe.lean \
        StatQEDLeanNoBinaryCacheProbe.pmf_total_mass
}

run_mismatch_rejection() {
    local fixture="$PROBE_ROOT/rejected-lean-4.32.1-mathlib-4.32.2"
    local scratch
    local project
    local root_toolchain
    local mathlib_toolchain
    new_scratch
    project="$scratch/mismatch"
    copy_project_without_manifest "$fixture" "$project"
    (
        cd -- "$project"
        MATHLIB_NO_CACHE_ON_UPDATE=1 LAKE_NO_CACHE=1 lake update --keep-toolchain
    )
    compare_regenerated_manifest "$fixture" "$project"
    root_toolchain=$(tr -d '\r\n' <"$project/lean-toolchain")
    mathlib_toolchain=$(tr -d '\r\n' <"$project/.lake/packages/mathlib/lean-toolchain")
    if [[ "$root_toolchain" == "$mathlib_toolchain" ]]; then
        printf 'mismatch fixture unexpectedly selected Mathlib\x27s required toolchain\n' >&2
        return 1
    fi
    [[ "$root_toolchain" == 'leanprover/lean4:v4.32.1' ]]
    [[ "$mathlib_toolchain" == "$EXPECTED_LEAN_TOOLCHAIN" ]]
    printf 'mismatch rejection passed: root=%s, Mathlib requires=%s\n' \
        "$root_toolchain" "$mathlib_toolchain"
}

mode=${1:-all}
run_static_controls
case "$mode" in
    static|--static)
        exit 0
        ;;
    recommended|no-binary-cache|mismatch|all)
        if require_preparation "$mode"; then
            :
        else
            status=$?
            [[ "$status" -eq 77 ]] && exit 77
            exit "$status"
        fi
        ;;
    *)
        printf 'usage: %s [static|recommended|no-binary-cache|mismatch|all]\n' "$0" >&2
        exit 64
        ;;
esac

case "$mode" in
    recommended) run_recommended ;;
    no-binary-cache) run_no_binary_cache ;;
    mismatch) run_mismatch_rejection ;;
    all)
        run_recommended
        run_no_binary_cache
        run_mismatch_rejection
        ;;
esac
