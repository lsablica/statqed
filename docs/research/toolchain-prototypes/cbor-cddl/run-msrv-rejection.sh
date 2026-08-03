#!/usr/bin/env bash
set -u

probe_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
scratch_root=$(mktemp -d /tmp/statqed-sq0002-cddl-msrv.XXXXXX)
rustup_home=${STATQED_RUSTUP_HOME:-/tmp/statqed-sq0002-rust-cache/rustup}

cleanup() {
    case "$scratch_root" in
        /tmp/statqed-sq0002-cddl-msrv.*) rm -rf -- "$scratch_root" ;;
        *) printf 'refusing unsafe cleanup target: %s\n' "$scratch_root" >&2 ;;
    esac
}
trap cleanup EXIT

RUSTUP_HOME="$rustup_home" \
CARGO_HOME="$scratch_root/cargo" \
CARGO_TARGET_DIR="$scratch_root/target" \
LANG=C.UTF-8 \
LC_ALL=C.UTF-8 \
cargo +1.85.1 check --locked --manifest-path "$probe_root/cddl-msrv/Cargo.toml"
