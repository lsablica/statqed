#!/usr/bin/env bash
set -euo pipefail

probe_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
python_bin=${STATQED_CBOR_PYTHON:-python3}
uv_bin=${STATQED_UV:-}
scratch_root=$(mktemp -d /tmp/statqed-sq0002-cbor-cddl.XXXXXX)
cargo_home="$scratch_root/cargo"
target_dir="$scratch_root/target"
venv_dir="$scratch_root/venv"
vectors_dir="$scratch_root/vectors"
install_root="$scratch_root/cddl-install"
wheelhouse_dir="$scratch_root/wheelhouse"

cleanup() {
    case "$scratch_root" in
        /tmp/statqed-sq0002-cbor-cddl.*) rm -rf -- "$scratch_root" ;;
        *) printf 'refusing unsafe cleanup target: %s\n' "$scratch_root" >&2 ;;
    esac
}
trap cleanup EXIT
mkdir -p -- "$cargo_home" "$target_dir" "$vectors_dir" "$wheelhouse_dir"
"$python_bin" --version
if test -n "$uv_bin"; then "$uv_bin" --version; fi
rustc --version
cargo --version
sha256sum "$probe_root/Cargo.lock" "$probe_root/cddl-msrv/Cargo.lock" "$probe_root/probe-requirements.lock"
"$python_bin" "$probe_root/fetch_wheel.py" "$wheelhouse_dir"

if test -n "$uv_bin"; then
    "$uv_bin" venv --no-project --python "$python_bin" --no-python-downloads "$venv_dir"
    "$uv_bin" pip install --python "$venv_dir/bin/python" --no-cache --no-index --find-links "$wheelhouse_dir" --require-hashes --only-binary=:all: --requirements "$probe_root/probe-requirements.lock"
else
    "$python_bin" -m venv "$venv_dir"
    "$venv_dir/bin/python" -m pip install --disable-pip-version-check --no-cache-dir --no-index --find-links "$wheelhouse_dir" --require-hashes --only-binary=:all: --requirement "$probe_root/probe-requirements.lock"
fi

export CARGO_HOME="$cargo_home"
export CARGO_TARGET_DIR="$target_dir"
export LANG=C.UTF-8
export LC_ALL=C.UTF-8

"$venv_dir/bin/python" "$probe_root/probe.py" --vectors "$vectors_dir"
cargo run --locked --manifest-path "$probe_root/Cargo.toml"

cargo install cddl --version 0.10.6 --locked --root "$install_root"
"$python_bin" "$probe_root/capture_cddl_install_lock.py" "$cargo_home" "$probe_root/cddl-install-lock.json"
"$install_root/bin/cddl" --version
"$install_root/bin/cddl" --ci compile-cddl --cddl "$probe_root/schema.cddl"
"$install_root/bin/cddl" --ci validate --cddl "$probe_root/schema.cddl" --cbor "$vectors_dir/valid.cbor"
if "$install_root/bin/cddl" --ci validate --cddl "$probe_root/schema.cddl" --cbor "$vectors_dir/invalid-shape.cbor"; then
    printf 'invalid shape unexpectedly accepted\n' >&2
    exit 1
else
    printf 'invalid shape rejected as expected\n'
fi
"$install_root/bin/cddl" --ci validate --cddl "$probe_root/map-order.cddl" --cbor "$vectors_dir/core-4.2.1.cbor"
"$install_root/bin/cddl" --ci validate --cddl "$probe_root/map-order.cddl" --cbor "$vectors_dir/length-first-4.2.3.cbor"
