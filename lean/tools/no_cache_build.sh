#!/usr/bin/env bash
set -euo pipefail

STATQED_LEAN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -z "${STATQED_LEAN_ELAN_HOME:-}" ]]; then
  echo "STATQED_LEAN_ELAN_HOME must name a prepared exact Elan home" >&2
  exit 2
fi

if [[ -z "${STATQED_LEAN_ISOLATION_ROOT:-}" ]]; then
  echo "STATQED_LEAN_ISOLATION_ROOT must name a dedicated isolation directory" >&2
  exit 2
fi

if [[ -e "$STATQED_LEAN_ROOT/.lake" ]]; then
  echo "refusing no-cache build because $STATQED_LEAN_ROOT/.lake already exists" >&2
  exit 2
fi

STATQED_LEAN_ISOLATION_ROOT="$(cd "$STATQED_LEAN_ISOLATION_ROOT" && pwd)"
STATQED_LEAN_ELAN_HOME="$(cd "$STATQED_LEAN_ELAN_HOME" && pwd)"

case "$STATQED_LEAN_ISOLATION_ROOT" in
  /|/tmp|"$STATQED_LEAN_ROOT")
    echo "refusing broad or project isolation root: $STATQED_LEAN_ISOLATION_ROOT" >&2
    exit 2
    ;;
esac

case "$STATQED_LEAN_ELAN_HOME" in
  "$STATQED_LEAN_ISOLATION_ROOT"/*) ;;
  *)
    echo "STATQED_LEAN_ELAN_HOME must be below STATQED_LEAN_ISOLATION_ROOT" >&2
    exit 2
    ;;
esac

if [[ ! -x "$STATQED_LEAN_ELAN_HOME/bin/lake" ]]; then
  echo "prepared Lake executable is absent from STATQED_LEAN_ELAN_HOME" >&2
  exit 2
fi

for directory in xdg-cache xdg-config xdg-data curl-home gnupg tmp; do
  if [[ -e "$STATQED_LEAN_ISOLATION_ROOT/$directory" ]]; then
    echo "refusing reused isolation state: $STATQED_LEAN_ISOLATION_ROOT/$directory" >&2
    exit 2
  fi
  mkdir "$STATQED_LEAN_ISOLATION_ROOT/$directory"
done

cd "$STATQED_LEAN_ROOT"
STATQED_LEAN_ENV=(
  env -i
  "CURL_HOME=$STATQED_LEAN_ISOLATION_ROOT/curl-home"
  "ELAN_HOME=$STATQED_LEAN_ELAN_HOME"
  "GIT_CONFIG_GLOBAL=/dev/null"
  "GIT_CONFIG_NOSYSTEM=1"
  "GIT_TERMINAL_PROMPT=0"
  "GNUPGHOME=$STATQED_LEAN_ISOLATION_ROOT/gnupg"
  "LAKE_NO_CACHE=1"
  "LC_ALL=C.UTF-8"
  "MATHLIB_NO_CACHE_ON_UPDATE=1"
  "PATH=$STATQED_LEAN_ELAN_HOME/bin:/usr/bin:/bin"
  "TMPDIR=$STATQED_LEAN_ISOLATION_ROOT/tmp"
  "XDG_CACHE_HOME=$STATQED_LEAN_ISOLATION_ROOT/xdg-cache"
  "XDG_CONFIG_HOME=$STATQED_LEAN_ISOLATION_ROOT/xdg-config"
  "XDG_DATA_HOME=$STATQED_LEAN_ISOLATION_ROOT/xdg-data"
)

"${STATQED_LEAN_ENV[@]}" lake update --keep-toolchain
"${STATQED_LEAN_ENV[@]}" lake build
"${STATQED_LEAN_ENV[@]}" lake env lean --trust=0 Examples/Smoke.lean
"${STATQED_LEAN_ENV[@]}" python3 tools/axiom_report.py --check Reports/axioms.json
