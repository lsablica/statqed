#!/usr/bin/env bash
set -euo pipefail

probe_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
python_bin=${STATQED_ARROW_PYTHON:-python3}
uv_bin=${STATQED_UV:-}
scratch_root=$(mktemp -d /tmp/statqed-sq0002-arrow.XXXXXX)
cargo_home="$scratch_root/cargo"
target_dir="$scratch_root/target"
venv_dir="$scratch_root/venv"
exchange_dir="$scratch_root/exchange"
wheelhouse_dir="$scratch_root/wheelhouse"

cleanup() {
    case "$scratch_root" in
        /tmp/statqed-sq0002-arrow.*) rm -rf -- "$scratch_root" ;;
        *) printf 'refusing unsafe cleanup target: %s\n' "$scratch_root" >&2 ;;
    esac
}
trap cleanup EXIT
mkdir -p -- "$exchange_dir" "$cargo_home" "$target_dir" "$wheelhouse_dir"
"$python_bin" --version
if test -n "$uv_bin"; then "$uv_bin" --version; fi
rustc --version
cargo --version
sha256sum "$probe_root/Cargo.lock" "$probe_root/probe-requirements.lock"
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

"$venv_dir/bin/python" "$probe_root/probe.py" self
cargo run --locked --manifest-path "$probe_root/Cargo.toml" -- self

"$venv_dir/bin/python" "$probe_root/probe.py" write-file "$exchange_dir/python.arrow"
cargo run --locked --manifest-path "$probe_root/Cargo.toml" -- read-file "$exchange_dir/python.arrow"
cargo run --locked --manifest-path "$probe_root/Cargo.toml" -- write-file "$exchange_dir/rust.arrow"
"$venv_dir/bin/python" "$probe_root/probe.py" read-file "$exchange_dir/rust.arrow"

printf 'ARROW1' > "$exchange_dir/magic-only.arrow"
"$venv_dir/bin/python" "$probe_root/probe.py" reject-file "$exchange_dir/magic-only.arrow"
cargo run --locked --manifest-path "$probe_root/Cargo.toml" -- reject-file "$exchange_dir/magic-only.arrow"
