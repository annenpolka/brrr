#!/usr/bin/env bash
# Exercise due against synthetic fixtures and, when present, real trees.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
DUE="$ROOT/due"
FIX="$ROOT/fixtures/ugly"
ENVS="$ROOT/fixtures/envs"
chmod +x "$DUE"

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

echo "== selftest =="
if "$DUE" --selftest; then
  ok "selftest"
else
  bad "selftest" "due --selftest exited $?"
fi

echo "== harvest ugly tree =="
names="$("$DUE" --names "$FIX")"
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
tsv="$("$DUE" --tsv --show-values --left "$ENVS/local.env" --right "$ENVS/ci.env" --example "$ENVS/example.env" --spare --app "$FIX" || true)"

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
red="$("$DUE" --tsv --left "$ENVS/local.env" --app "$FIX/app.py" || true)"
if echo "$red" | awk -F'\t' '$2=="DUE_API_KEY" && $3=="«redacted»" {found=1} END{exit !found}'; then
  ok "redacts DUE_API_KEY"
else
  bad "redacts DUE_API_KEY" "$red"
fi

echo "== packed emit =="
emit="$("$DUE" --emit --show-values --left "$ENVS/local.env" --app "$FIX")"
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
abi="$("$DUE" --dump-abi --app --min-evidence call "$FIX")"
round="$("$DUE" --abi /dev/stdin --names --app <<<"$abi")"
if has "DUE_PORT" "$round" && has "DUE_TOKEN" "$round"; then
  ok "abi roundtrip"
else
  bad "abi roundtrip" "$round"
fi

echo "== exit codes =="
set +e
"$DUE" --left "$ENVS/local.env" --right "$ENVS/ci.env" --app "$FIX" >/dev/null
ec=$?
set -e
if [[ "$ec" == "1" ]]; then
  ok "diff exits 1"
else
  bad "diff exits 1" "exit $ec"
fi
set +e
"$DUE" --report-only --left "$ENVS/local.env" --right "$ENVS/ci.env" --app "$FIX" >/dev/null
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
  bnames="$("$DUE" --names --app "$TINY")"
  if has "DUE_FIXTURE_C" "$bnames"; then
    ok "binary has DUE_FIXTURE_C"
  else
    bad "binary has DUE_FIXTURE_C" "$bnames"
  fi
  bhome="$("$DUE" --names "$TINY")"
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
pnames="$("$DUE" --names --app "$PACKED")"
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
pall="$("$DUE" --names "$PACKED")"
if has "XDG_CONFIG_HOME" "$pall"; then
  ok "packed raw has XDG_CONFIG_HOME"
else
  bad "packed raw has XDG_CONFIG_HOME" "$pall"
fi
rm -f "$PACKED"

echo "== spaces + unicode paths =="
if "$DUE" --names "$FIX/file with spaces.rs" | grep -q DUE_TOKEN; then
  ok "path with spaces"
else
  bad "path with spaces" "$("$DUE" --names "$FIX/file with spaces.rs")"
fi
if "$DUE" --names "$FIX/nested/deep/計画.sh" | grep -q DUE_HOME; then
  ok "unicode path"
else
  bad "unicode path" "$("$DUE" --names "$FIX/nested/deep/計画.sh")"
fi

KIZU="${DUE_KIZU:-$HOME/ghq/github.com/annenpolka/kizu}"
echo "== dogfood kizu =="
if [[ -d "$KIZU/src" ]]; then
  knames="$("$DUE" --names --app --min-evidence call "$KIZU/src")"
  for want in KIZU_CONFIG KIZU_STATE_DIR KIZU_SESSION_ID TMUX ZELLIJ KITTY_LISTEN_ON; do
    if has "$want" "$knames"; then
      ok "kizu src $want"
    else
      bad "kizu src $want" "$knames"
    fi
  done
  if [[ -x "$KIZU/target/release/kizu" ]]; then
    join="$("$DUE" --tsv --app --min-evidence call "$KIZU/src" --vs-program "$KIZU/target/release/kizu")"
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
  gnames="$("$DUE" --names --app "$GIT_BIN" || true)"
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
