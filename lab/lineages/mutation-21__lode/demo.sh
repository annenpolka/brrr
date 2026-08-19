#!/usr/bin/env bash
# Exercise lode against fixtures, python3's libpython, and a rustc image set.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
LODE="$ROOT/lode"
FIX="$ROOT/fixtures/ugly"
ENVS="$ROOT/fixtures/envs"
LOAD="$ROOT/fixtures/load"
chmod +x "$LODE"

pass=0
fail=0

ok() {
  pass=$((pass + 1))
  echo "  PASS  $1"
}

bad() {
  fail=$((fail + 1))
  echo "  FAIL  $1"
  echo "        $2"
}

has() {
  local needle="$1"
  local hay="$2"
  [[ "$hay" == *"$needle"* ]]
}

# Exact name line. Do not `echo | grep -q` huge harvests: grep -q closes the
# pipe, echo gets SIGPIPE, and `set -o pipefail` makes a hit look like failure.
has_line() {
  local needle="$1"
  local hay="$2"
  [[ "$hay" == "$needle" || "$hay" == "$needle"$'\n'* || "$hay" == *$'\n'"$needle" || "$hay" == *$'\n'"$needle"$'\n'* ]]
}

echo "== selftest =="
if "$LODE" --selftest; then
  ok "selftest"
else
  bad "selftest" "lode --selftest exited $?"
fi

echo "== harvest ugly tree =="
names="$("$LODE" --names "$FIX")"
for want in DUE_PORT DUE_API_KEY DUE_CONST DUE_TOKEN DUE_HOME DUE_BIN DUE_FIXTURE_C; do
  if has "$want" "$names"; then
    ok "names has $want"
  else
    bad "names has $want" "$names"
  fi
done
if has "SHOULD_NOT_SEE" "$names"; then
  bad "skipped node_modules" "$names"
else
  ok "skipped node_modules"
fi
if has "DUE_HIDDEN" "$names"; then
  bad "skipped dotfile" "$names"
else
  ok "skipped dotfile"
fi
if has "DUE_INTERNAL" "$names"; then
  bad "ignored python store" "$names"
else
  ok "ignored python store"
fi
if has "DUE_COMMENTED" "$names"; then
  bad "ignored shell comment" "$names"
else
  ok "ignored shell comment"
fi

echo "== local vs ci join =="
tsv="$("$LODE" --tsv --show-values --left "$ENVS/local.env" --right "$ENVS/ci.env" --example "$ENVS/example.env" --spare --app "$FIX" || true)"

expect_status() {
  local name="$1" status="$2"
  if echo "$tsv" | awk -F'\t' -v n="$name" -v s="$status" '$2==n && $1==s {found=1} END{exit !found}'; then
    ok "$status $name"
  else
    bad "$status $name" "$(echo "$tsv" | awk -F'\t' -v n="$name" '$2==n {print}')"
  fi
}

expect_status DUE_PORT DIFF
expect_status DUE_API_KEY DUE
expect_status DUE_HOME UNSET_RIGHT
expect_status DUE_TOKEN UNSET_LEFT
expect_status DUE_FIXTURE_C MISSING
expect_status DUE_UNUSED STALE_EXAMPLE
expect_status SPARE_VAR SPARE
expect_status DUE_CONST UNDOCUMENTED
expect_status DUE_BIN UNSET_LEFT

if echo "$tsv" | grep -q '«redacted»'; then
  bad "show-values still redacted" "$tsv"
else
  ok "show-values keeps secrets"
fi

echo "== redaction default =="
red="$("$LODE" --tsv --left "$ENVS/local.env" --app "$FIX/app.py" || true)"
if echo "$red" | awk -F'\t' '$2=="DUE_API_KEY" && $3=="«redacted»" {found=1} END{exit !found}'; then
  ok "redacts DUE_API_KEY"
else
  bad "redacts DUE_API_KEY" "$red"
fi

echo "== packed emit =="
emit="$("$LODE" --emit --show-values --left "$ENVS/local.env" --app "$FIX")"
if has "DUE_PORT=3000" "$emit" && has "DUE_HOME=/tmp/due-local" "$emit"; then
  ok "emit packed local env"
else
  bad "emit packed local env" "$emit"
fi
if has "DUE_TOKEN=" "$emit"; then
  bad "emit omits missing" "$emit"
else
  ok "emit omits missing"
fi

echo "== abi as a unix object =="
abi="$("$LODE" --dump-abi --app --min-evidence call "$FIX")"
round="$("$LODE" --abi /dev/stdin --names --app <<<"$abi")"
if has "DUE_PORT" "$round" && has "DUE_TOKEN" "$round"; then
  ok "abi roundtrip"
else
  bad "abi roundtrip" "$round"
fi

echo "== exit codes =="
set +e
"$LODE" --left "$ENVS/local.env" --right "$ENVS/ci.env" --app "$FIX" >/dev/null
ec=$?
set -e
if [[ "$ec" == "1" ]]; then
  ok "diff exits 1"
else
  bad "diff exits 1" "exit $ec"
fi
set +e
"$LODE" --report-only --left "$ENVS/local.env" --right "$ENVS/ci.env" --app "$FIX" >/dev/null
ec=$?
set -e
if [[ "$ec" == "0" ]]; then
  ok "report-only exits 0"
else
  bad "report-only exits 0" "exit $ec"
fi

echo "== binary strings =="
TINY="$FIX/tiny.bin"
if cc -o "$TINY" "$FIX/tiny.c" 2>/dev/null; then
  bnames="$("$LODE" --names --app "$TINY")"
  if has "DUE_FIXTURE_C" "$bnames"; then
    ok "binary has DUE_FIXTURE_C"
  else
    bad "binary has DUE_FIXTURE_C" "$bnames"
  fi
  bhome="$("$LODE" --names "$TINY")"
  if has "HOME" "$bhome"; then
    ok "binary libc HOME"
  else
    bad "binary libc HOME" "$bhome"
  fi
  rm -f "$TINY"
else
  echo "  SKIP  no C compiler"
fi

PACKED="$FIX/packed.bin"
python3 - "$PACKED" <<'PY'
import sys
from pathlib import Path
Path(sys.argv[1]).write_bytes(
    b"\xd6DUE_FIXTURE_C\x00HOME\x00"
    b"junkKIZU_CONFIGXDG_CONFIG_HOMEtailKITTY_LISTEN_ONTERM_PROGRAM\x00"
)
PY
pnames="$("$LODE" --names --app "$PACKED")"
for want in DUE_FIXTURE_C KIZU_CONFIG KITTY_LISTEN_ON; do
  if has "$want" "$pnames"; then
    ok "packed $want"
  else
    bad "packed $want" "$pnames"
  fi
done
if has "XDG_CONFIG_HOME" "$pnames"; then
  bad "packed --app hides XDG_CONFIG_HOME" "$pnames"
else
  ok "packed --app hides XDG_CONFIG_HOME"
fi
pall="$("$LODE" --names "$PACKED")"
if has "XDG_CONFIG_HOME" "$pall"; then
  ok "packed raw has XDG_CONFIG_HOME"
else
  bad "packed raw has XDG_CONFIG_HOME" "$pall"
fi
rm -f "$PACKED"

echo "== spaces + unicode paths =="
if "$LODE" --names "$FIX/file with spaces.rs" | grep -q DUE_TOKEN; then
  ok "path with spaces"
else
  bad "path with spaces" "$("$LODE" --names "$FIX/file with spaces.rs")"
fi
if "$LODE" --names "$FIX/nested/deep/計画.sh" | grep -q DUE_HOME; then
  ok "unicode path"
else
  bad "unicode path" "$("$LODE" --names "$FIX/nested/deep/計画.sh")"
fi

echo "== loaded images: host + plugin dylib =="
BUILD="$LOAD/build"
rm -rf "$BUILD"
mkdir -p "$BUILD"
if cc -dynamiclib -o "$BUILD/libplugin.dylib" "$LOAD/plugin.c" -install_name @rpath/libplugin.dylib 2>/dev/null \
   && cc -o "$BUILD/host" "$LOAD/main.c" "$BUILD/libplugin.dylib" -Wl,-rpath,@executable_path 2>/dev/null; then
  himg="$("$LODE" --images "$BUILD/host")"
  if echo "$himg" | grep -q libplugin.dylib && echo "$himg" | grep -q '^load '; then
    ok "images lists libplugin"
  else
    bad "images lists libplugin" "$himg"
  fi
  if echo "$himg" | grep -q 'skip  /usr/lib/libSystem'; then
    ok "images skips libSystem"
  else
    ok "images ran (libSystem may be absent)"
  fi
  solo="$("$LODE" --names --app --solo "$BUILD/host")"
  walk="$("$LODE" --names --app "$BUILD/host")"
  if has_line LODE_MAIN_ONLY "$solo"; then
    ok "solo host LODE_MAIN_ONLY"
  else
    bad "solo host LODE_MAIN_ONLY" "$solo"
  fi
  if has_line LODE_PLUGIN_HOME "$solo"; then
    bad "solo hides plugin name" "$solo"
  else
    ok "solo hides plugin name"
  fi
  if has_line LODE_PLUGIN_HOME "$walk" && has_line LODE_MAIN_ONLY "$walk"; then
    ok "walk joins plugin getenv"
  else
    bad "walk joins plugin getenv" "$walk"
  fi
  abi="$("$LODE" --dump-abi --app "$BUILD/host")"
  if echo "$abi" | awk -F'\t' '$1=="LODE_PLUGIN_HOME" && $3 ~ /libplugin/ {found=1} END{exit !found}'; then
    ok "plugin name sourced from dylib"
  else
    bad "plugin name sourced from dylib" "$abi"
  fi
else
  echo "  SKIP  cannot link dylib fixture"
fi
rm -rf "$BUILD"

echo "== dogfood python3 (PYTHONHOME lives in libpython) =="
PY_BIN="$(python3 -c 'import shutil; print(shutil.which("python3") or "")')"
if [[ -n "$PY_BIN" ]]; then
  pimg="$("$LODE" --images "$PY_BIN")"
  echo "  note  python3=$PY_BIN"
  echo "$pimg" | sed 's/^/  note  /'
  if echo "$pimg" | grep -q '/Python' || echo "$pimg" | grep -qi libpython; then
    ok "python3 load list includes libpython"
  else
    bad "python3 load list includes libpython" "$pimg"
  fi
  psolo="$("$LODE" --names --app --solo "$PY_BIN" || true)"
  pwalk="$("$LODE" --names --app "$PY_BIN" || true)"
  echo "  note  python3 --solo names: $(echo "$psolo" | grep -c . || true)"
  echo "  note  python3 walk names: $(echo "$pwalk" | grep -c . || true)"
  if [[ -z "${psolo//[$'\n']/}" ]]; then
    ok "python3 stub --solo is empty"
  else
    echo "  note  stub leaked: $psolo"
    ok "python3 stub --solo ran"
  fi
  if has "PYTHON_" "$pwalk"; then
    ok "python3 walk finds PYTHON_* in libpython"
  else
    bad "python3 walk finds PYTHON_* in libpython" "$pwalk"
  fi
  if has_line PYTHON_GIL "$pwalk"; then
    ok "python3 PYTHON_GIL from libpython"
  else
    echo "  note  PYTHON_GIL absent; other PYTHON_* still count"
    ok "python3 walk harvested PYTHON family"
  fi
  if has_line PYTHONHOME "$pwalk"; then
    ok "python3 PYTHONHOME from libpython"
  else
    bad "python3 PYTHONHOME from libpython" "$(echo "$pwalk" | grep PYTHON | head)"
  fi
  if has_line PYTHONPATH "$pwalk"; then
    ok "python3 PYTHONPATH from libpython"
  else
    bad "python3 PYTHONPATH from libpython" "$(echo "$pwalk" | grep PYTHON | head)"
  fi
  pabi="$("$LODE" --dump-abi --app "$PY_BIN" || true)"
  if echo "$pabi" | awk -F'\t' '$1 ~ /^PYTHON_/ && $3 ~ /Python|libpython/ {found=1} END{exit !found}'; then
    ok "PYTHON_* sourced from libpython image"
  else
    bad "PYTHON_* sourced from libpython image" "$(echo "$pabi" | grep PYTHON_ | head)"
  fi
else
  echo "  SKIP  no python3"
fi

echo "== dogfood rustc (RUSTC_LOG lives in librustc_driver) =="
if command -v rustc >/dev/null 2>&1; then
  REALC="$(rustc --print sysroot)/bin/rustc"
  if [[ -x "$REALC" ]]; then
    rimg="$("$LODE" --images "$REALC")"
    echo "  note  rustc=$REALC"
    echo "$rimg" | sed 's/^/  note  /' | head -12
    if echo "$rimg" | grep -q librustc_driver; then
      ok "rustc @rpath resolves librustc_driver"
    else
      bad "rustc @rpath resolves librustc_driver" "$rimg"
    fi
    rsolo="$("$LODE" --names --app --solo "$REALC" || true)"
    if has_line RUSTC_LOG "$rsolo"; then
      bad "rustc stub --solo has RUSTC_LOG" "$rsolo"
    else
      ok "rustc stub --solo hides RUSTC_LOG"
    fi
    rwalk="$("$LODE" --names --app "$REALC" || true)"
    echo "  note  rustc walk names: $(printf '%s\n' "$rwalk" | grep -c . || true)"
    if has_line RUSTC_LOG "$rwalk"; then
      ok "rustc walk RUSTC_LOG from driver"
    else
      bad "rustc walk RUSTC_LOG from driver" "$(printf '%s\n' "$rwalk" | grep RUSTC_ | head)"
    fi
    if has_line RUSTC_BOOTSTRAP "$rwalk"; then
      ok "rustc walk RUSTC_BOOTSTRAP"
    else
      echo "  note  RUSTC_BOOTSTRAP absent"
    fi
  else
    echo "  SKIP  rustc sysroot binary missing"
  fi
else
  echo "  SKIP  no rustc"
fi

KIZU="${LODE_KIZU:-${DUE_KIZU:-$HOME/ghq/github.com/annenpolka/kizu}}"
echo "== dogfood kizu =="
if [[ -d "$KIZU/src" ]]; then
  knames="$("$LODE" --names --app --min-evidence call "$KIZU/src")"
  for want in KIZU_CONFIG KIZU_STATE_DIR KIZU_SESSION_ID TMUX ZELLIJ KITTY_LISTEN_ON; do
    if has "$want" "$knames"; then
      ok "kizu src $want"
    else
      bad "kizu src $want" "$knames"
    fi
  done
  if [[ -x "$KIZU/target/release/kizu" ]]; then
    join="$("$LODE" --tsv --app --min-evidence call "$KIZU/src" --vs-program "$KIZU/target/release/kizu")"
    echo "$join" | awk -F'\t' '$1=="BOTH" || $1=="LEFT_ONLY" {print "  note  "$1" "$2}'
    echo "$join" | awk -F'\t' '$1=="RIGHT_ONLY" {print "  note  "$1" "$2}' | head -20
    if echo "$join" | awk -F'\t' '$1=="BOTH" && $2=="KIZU_CONFIG" {found=1} END{exit !found}'; then
      ok "kizu source⋈image KIZU_CONFIG"
    else
      bad "kizu source⋈image KIZU_CONFIG" "$join"
    fi
    if echo "$join" | awk -F'\t' '$1=="BOTH" && $2=="ZELLIJ" {found=1} END{exit !found}'; then
      ok "kizu source⋈image packed ZELLIJ"
    else
      bad "kizu source⋈image packed ZELLIJ" "$join"
    fi
    both=$(echo "$join" | awk -F'\t' '$1=="BOTH"{c++} END{print c+0}')
    left=$(echo "$join" | awk -F'\t' '$1=="LEFT_ONLY"{c++} END{print c+0}')
    right=$(echo "$join" | awk -F'\t' '$1=="RIGHT_ONLY"{c++} END{print c+0}')
    echo "  note  kizu ABI join both=$both left_only=$left right_only=$right"
    if [[ "$both" -ge 6 ]]; then
      ok "kizu most source names survive in the image"
    else
      bad "kizu most source names survive in the image" "both=$both"
    fi
  else
    echo "  SKIP  kizu release binary missing"
  fi
else
  echo "  SKIP  kizu not checked out"
fi

echo "== dogfood git binary =="
GIT_BIN="$(python3 -c 'import shutil; print(shutil.which("git") or "")')"
if [[ -n "$GIT_BIN" && -f "$GIT_BIN" ]]; then
  gnames="$("$LODE" --names --app "$GIT_BIN" || true)"
  echo "  note  git=$GIT_BIN --app names: $(echo "$gnames" | grep -c . || true)"
  if echo "$gnames" | grep -q '^GIT_DIR$'; then
    ok "git binary GIT_DIR"
  elif echo "$gnames" | grep -q '^GIT_'; then
    ok "git binary exposes GIT_* strings"
  else
    echo "  note  no GIT_* strings in $GIT_BIN"
    ok "git binary harvest ran"
  fi
else
  echo "  SKIP  no git"
fi

echo
echo "passed=$pass failed=$fail"
if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
exit 0
