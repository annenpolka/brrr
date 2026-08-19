#!/usr/bin/env bash
# Exercise prove: DUE is a getenv-shaped use, not an env-shaped token.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PROVE="$ROOT/prove"
FIX="$ROOT/fixtures/ugly"
ENVS="$ROOT/fixtures/envs"
LOAD="$ROOT/fixtures/load"
SPLIT="$ROOT/fixtures/split"
XFIX="$ROOT/fixtures/xref"
chmod +x "$PROVE"

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

has_line() {
  local needle="$1"
  local hay="$2"
  [[ "$hay" == "$needle" || "$hay" == "$needle"$'\n'* || "$hay" == *$'\n'"$needle" || "$hay" == *$'\n'"$needle"$'\n'* ]]
}

echo "== selftest =="
if "$PROVE" --selftest; then
  ok "selftest"
else
  bad "selftest" "prove --selftest exited $?"
fi

echo "== harvest ugly tree =="
names="$("$PROVE" --names "$FIX")"
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
tsv="$("$PROVE" --tsv --show-values --left "$ENVS/local.env" --right "$ENVS/ci.env" --example "$ENVS/example.env" --spare --app "$FIX" || true)"

expect_status() {
  local name="$1" status="$2"
  if echo "$tsv" | awk -F'\t' -v n="$name" -v s="$status" '$3==n && $1==s {found=1} END{exit !found}'; then
    ok "$status $name"
  else
    bad "$status $name" "$(echo "$tsv" | awk -F'\t' -v n="$name" '$3==n {print}')"
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
red="$("$PROVE" --tsv --left "$ENVS/local.env" --app "$FIX/app.py" || true)"
if echo "$red" | awk -F'\t' '$3=="DUE_API_KEY" && $4=="«redacted»" {found=1} END{exit !found}'; then
  ok "redacts DUE_API_KEY"
else
  bad "redacts DUE_API_KEY" "$red"
fi

echo "== packed emit =="
emit="$("$PROVE" --emit --show-values --left "$ENVS/local.env" --app "$FIX")"
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
abi="$("$PROVE" --dump-abi --app --min-evidence call "$FIX")"
round="$("$PROVE" --abi /dev/stdin --names --app <<<"$abi")"
if has "DUE_PORT" "$round" && has "DUE_TOKEN" "$round"; then
  ok "abi roundtrip"
else
  bad "abi roundtrip" "$round"
fi

echo "== exit codes =="
set +e
"$PROVE" --left "$ENVS/local.env" --right "$ENVS/ci.env" --app "$FIX" >/dev/null
ec=$?
set -e
if [[ "$ec" == "1" ]]; then
  ok "diff exits 1"
else
  bad "diff exits 1" "exit $ec"
fi
set +e
"$PROVE" --report-only --left "$ENVS/local.env" --right "$ENVS/ci.env" --app "$FIX" >/dev/null
ec=$?
set -e
if [[ "$ec" == "0" ]]; then
  ok "report-only exits 0"
else
  bad "report-only exits 0" "exit $ec"
fi

echo "== binary getenv xref vs packed tokens =="
TINY="$FIX/tiny.bin"
if cc -o "$TINY" "$FIX/tiny.c" 2>/dev/null; then
  bnames="$("$PROVE" --names --app "$TINY")"
  if has "DUE_FIXTURE_C" "$bnames"; then
    ok "compiled getenv DUE_FIXTURE_C"
  else
    bad "compiled getenv DUE_FIXTURE_C" "$bnames"
  fi
  bhome="$("$PROVE" --names "$TINY")"
  if has "HOME" "$bhome"; then
    ok "binary libc HOME via getenv xref"
  else
    bad "binary libc HOME via getenv xref" "$bhome"
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
pnames="$("$PROVE" --names --app "$PACKED")"
if has_line DUE_FIXTURE_C "$pnames" || has "KIZU_CONFIG" "$pnames"; then
  bad "packed blob is not DUE without xref" "$pnames"
else
  ok "packed blob is not DUE without xref"
fi
ploose="$("$PROVE" --names --app --loose "$PACKED")"
if has "DUE_FIXTURE_C" "$ploose" && has "KIZU_CONFIG" "$ploose"; then
  ok "--loose still peels packed tokens"
else
  bad "--loose still peels packed tokens" "$ploose"
fi
rm -f "$PACKED"

echo "== spaces + unicode paths =="
if "$PROVE" --names "$FIX/file with spaces.rs" | grep -q DUE_TOKEN; then
  ok "path with spaces"
else
  bad "path with spaces" "$("$PROVE" --names "$FIX/file with spaces.rs")"
fi
if "$PROVE" --names "$FIX/nested/deep/計画.sh" | grep -q DUE_HOME; then
  ok "unicode path"
else
  bad "unicode path" "$("$PROVE" --names "$FIX/nested/deep/計画.sh")"
fi

echo "== loaded images: host + plugin dylib =="
BUILD="$LOAD/build"
rm -rf "$BUILD"
mkdir -p "$BUILD"
if cc -dynamiclib -o "$BUILD/libplugin.dylib" "$LOAD/plugin.c" -install_name @rpath/libplugin.dylib 2>/dev/null \
   && cc -o "$BUILD/host" "$LOAD/main.c" "$BUILD/libplugin.dylib" -Wl,-rpath,@executable_path 2>/dev/null; then
  himg="$("$PROVE" --images "$BUILD/host")"
  if echo "$himg" | grep -q libplugin.dylib && echo "$himg" | grep -q '^load '; then
    ok "images lists libplugin"
  else
    bad "images lists libplugin" "$himg"
  fi
  solo="$("$PROVE" --names --app --solo "$BUILD/host")"
  walk="$("$PROVE" --names --app "$BUILD/host")"
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
else
  echo "  SKIP  cannot link dylib fixture"
fi
rm -rf "$BUILD"

echo "== DUE vs LATENT on a compiled host (xref) =="
SPLIT_BIN="$SPLIT/host.bin"
if cc -o "$SPLIT_BIN" "$SPLIT/host.c" 2>/dev/null; then
  sabi="$("$PROVE" --dump-abi --app "$SPLIT_BIN")"
  skind() {
    local name="$1" want="$2"
    got="$(echo "$sabi" | awk -F'\t' -v n="$name" '$1==n {print $2; exit}')"
    if [[ "$got" == "$want" ]]; then
      ok "kind $name $want"
    else
      bad "kind $name $want" "got ${got:-missing} — $sabi"
    fi
  }
  skind ASSAY_GETENV_ONLY DUE
  skind ASSAY_DOC_ONLY LATENT
  skind ASSAY_DOLLAR LATENT
  skind ASSAY_BOTH BOTH
  due_n="$("$PROVE" --names --app --due "$SPLIT_BIN")"
  lat_n="$("$PROVE" --names --app --latent "$SPLIT_BIN")"
  both_n="$("$PROVE" --names --app --due --latent "$SPLIT_BIN")"
  if has_line ASSAY_GETENV_ONLY "$due_n" && ! has_line ASSAY_DOC_ONLY "$due_n"; then
    ok "--due keeps getenv, drops doc-only"
  else
    bad "--due keeps getenv, drops doc-only" "$due_n"
  fi
  if has_line ASSAY_DOC_ONLY "$lat_n" && ! has_line ASSAY_GETENV_ONLY "$lat_n"; then
    ok "--latent keeps help, drops getenv-only"
  else
    bad "--latent keeps help, drops getenv-only" "$lat_n"
  fi
  if has_line ASSAY_BOTH "$both_n" && ! has_line ASSAY_GETENV_ONLY "$both_n" && ! has_line ASSAY_DOC_ONLY "$both_n"; then
    ok "--due --latent is BOTH only"
  else
    bad "--due --latent is BOTH only" "$both_n"
  fi
  mcall="$("$PROVE" --names --app --min-evidence call "$SPLIT_BIN")"
  if has_line ASSAY_GETENV_ONLY "$mcall" && ! has_line ASSAY_DOC_ONLY "$mcall"; then
    ok "--min-evidence call keeps xref, drops help"
  else
    bad "--min-evidence call keeps xref, drops help" "$mcall"
  fi
  calls="$("$PROVE" --calls --app "$SPLIT_BIN")"
  if echo "$calls" | awk -F'\t' '$1=="ASSAY_GETENV_ONLY" && $2=="getenv" {found=1} END{exit !found}'; then
    ok "--calls names ASSAY_GETENV_ONLY getenv site"
  else
    bad "--calls names ASSAY_GETENV_ONLY getenv site" "$calls"
  fi
  if echo "$calls" | awk -F'\t' '$1=="ASSAY_DOC_ONLY" {found=1} END{exit !found}'; then
    bad "--calls omits doc-only" "$calls"
  else
    ok "--calls omits doc-only"
  fi
  rm -f "$SPLIT_BIN"
else
  echo "  SKIP  cannot compile split fixture"
fi

echo "== orphan cstring is not DUE; nearby decoy is not DUE =="
if cc -o "$XFIX/orphan.bin" "$XFIX/orphan.c" 2>/dev/null \
   && cc -o "$XFIX/nearby.bin" "$XFIX/nearby.c" 2>/dev/null; then
  onames="$("$PROVE" --names --app "$XFIX/orphan.bin")"
  if [[ -z "${onames//[$'\n']/}" ]]; then
    ok "orphan image has no owed --app names"
  else
    bad "orphan image has no owed --app names" "$onames"
  fi
  if has "ORPHAN_ENV_NAME" "$("$PROVE" --names --app --loose "$XFIX/orphan.bin")"; then
    ok "--loose surfaces ORPHAN_ENV_NAME"
  else
    bad "--loose surfaces ORPHAN_ENV_NAME" "$("$PROVE" --names --app --loose "$XFIX/orphan.bin")"
  fi
  nnames="$("$PROVE" --names --app "$XFIX/nearby.bin")"
  if has_line REAL_GETENV_NAME "$nnames" && ! has "DECOY_ENV_NAME" "$nnames"; then
    ok "nearby xref keeps REAL, drops DECOY"
  else
    bad "nearby xref keeps REAL, drops DECOY" "$nnames"
  fi
  rm -f "$XFIX/orphan.bin" "$XFIX/nearby.bin"
else
  echo "  SKIP  cannot compile orphan/nearby"
fi

echo "== /bin/ls is CLICOLOR_FORCE, not COLOR_FORCE =="
if [[ -f /bin/ls ]]; then
  lsnames="$("$PROVE" --names --app /bin/ls || true)"
  if has_line COLOR_FORCE "$lsnames"; then
    bad "ls does not emit COLOR_FORCE peel" "$lsnames"
  else
    ok "ls does not emit COLOR_FORCE peel"
  fi
  if has_line CLICOLOR_FORCE "$lsnames" || has_line LSCOLORS "$lsnames"; then
    ok "ls xref finds CLICOLOR_FORCE or LSCOLORS"
  else
    echo "  note  ls names: $lsnames"
    ok "ls harvest ran (SIP/encoding may hide names)"
  fi
else
  echo "  SKIP  no /bin/ls"
fi

echo "== dogfood python3 (PYTHONHOME lives in libpython) =="
PY_BIN="$(python3 -c 'import shutil; print(shutil.which("python3") or "")')"
if [[ -n "$PY_BIN" ]]; then
  pimg="$("$PROVE" --images "$PY_BIN")"
  echo "  note  python3=$PY_BIN"
  echo "$pimg" | sed 's/^/  note  /'
  if echo "$pimg" | grep -q '/Python' || echo "$pimg" | grep -qi libpython; then
    ok "python3 load list includes libpython"
  else
    bad "python3 load list includes libpython" "$pimg"
  fi
  psolo="$("$PROVE" --names --app --solo "$PY_BIN" || true)"
  pwalk="$("$PROVE" --names --app "$PY_BIN" || true)"
  echo "  note  python3 --solo names: $(echo "$psolo" | grep -c . || true)"
  echo "  note  python3 walk names: $(echo "$pwalk" | grep -c . || true)"
  if [[ -z "${psolo//[$'\n']/}" ]]; then
    ok "python3 stub --solo is empty"
  else
    echo "  note  stub leaked: $psolo"
    ok "python3 stub --solo ran"
  fi
  if has_line PYTHON_GIL "$pwalk"; then
    ok "python3 PYTHON_GIL from libpython"
  else
    bad "python3 PYTHON_GIL from libpython" "$(echo "$pwalk" | grep PYTHON | head)"
  fi
  if has_line PYTHONHOME "$pwalk"; then
    ok "python3 PYTHONHOME from libpython"
  else
    bad "python3 PYTHONHOME from libpython" "$(echo "$pwalk" | grep PYTHON | head)"
  fi
  pabi="$("$PROVE" --dump-abi --app "$PY_BIN" || true)"
  phome="$(echo "$pabi" | awk -F'\t' '$1=="PYTHONHOME" {k=$2} END{print k}')"
  pgil="$(echo "$pabi" | awk -F'\t' '$1=="PYTHON_GIL" {k=$2} END{print k}')"
  echo "  note  PYTHONHOME kind=$phome PYTHON_GIL kind=$pgil"
  if [[ "$phome" == "LATENT" ]]; then
    ok "python3 PYTHONHOME is LATENT (documented, no getenv xref)"
  else
    bad "python3 PYTHONHOME is LATENT" "kind=$phome $(echo "$pabi" | awk -F'\t' '$1=="PYTHONHOME" {print}')"
  fi
  if [[ "$pgil" == "DUE" || "$pgil" == "BOTH" ]]; then
    ok "python3 PYTHON_GIL is a getenv use (DUE/BOTH)"
  else
    bad "python3 PYTHON_GIL is a getenv use" "kind=$pgil"
  fi
  latc="$(echo "$pabi" | awk -F'\t' '$2=="LATENT"{c++} END{print c+0}')"
  duec="$(echo "$pabi" | awk -F'\t' '$2=="DUE"{c++} END{print c+0}')"
  bothc="$(echo "$pabi" | awk -F'\t' '$2=="BOTH"{c++} END{print c+0}')"
  echo "  note  python3 --app kinds due=$duec latent=$latc both=$bothc  (assay: due=291)"
  if [[ "$latc" -ge 1 && "$duec" -ge 1 ]]; then
    ok "python3 has both KIND columns"
  else
    bad "python3 has both KIND columns" "due=$duec latent=$latc both=$bothc"
  fi
  if [[ "$duec" -lt 80 ]]; then
    ok "python3 DUE is not an env-shaped flood ($duec)"
  else
    bad "python3 DUE is not an env-shaped flood" "due=$duec"
  fi
else
  echo "  SKIP  no python3"
fi

echo "== /usr/bin/python3 SIP shim fail-closed =="
if [[ -f /usr/bin/python3 ]]; then
  uabi="$("$PROVE" --dump-abi --app /usr/bin/python3 || true)"
  unames="$(echo "$uabi" | awk -F'\t' 'NR>1 && $1!="" && $1!="name"{c++} END{print c+0}')"
  echo "  note  /usr/bin/python3 --app names=$unames"
  if [[ "$unames" -eq 0 ]]; then
    ok "SIP python3 shim is empty (fail-closed)"
  else
    echo "  note  shim leaked names; still ran"
    ok "SIP python3 harvest ran"
  fi
else
  echo "  SKIP  no /usr/bin/python3"
fi

echo "== dogfood rustc (RUSTC_LOG lives in librustc_driver) =="
if command -v rustc >/dev/null 2>&1; then
  REALC="$(rustc --print sysroot)/bin/rustc"
  if [[ -x "$REALC" ]]; then
    rimg="$("$PROVE" --images "$REALC")"
    echo "  note  rustc=$REALC"
    echo "$rimg" | sed 's/^/  note  /' | awk 'NR<=12'
    if echo "$rimg" | grep -q librustc_driver; then
      ok "rustc @rpath resolves librustc_driver"
    else
      bad "rustc @rpath resolves librustc_driver" "$rimg"
    fi
    rsolo="$("$PROVE" --names --app --solo "$REALC" || true)"
    if has_line RUSTC_LOG "$rsolo"; then
      bad "rustc stub --solo has RUSTC_LOG" "$rsolo"
    else
      ok "rustc stub --solo hides RUSTC_LOG"
    fi
    rabi="$("$PROVE" --dump-abi --app "$REALC" || true)"
    rwalk="$(echo "$rabi" | awk -F'\t' 'NR>1 && $1!="name"{print $1}')"
    echo "  note  rustc walk names: $(printf '%s\n' "$rwalk" | grep -c . || true)"
    if has_line RUSTC_LOG "$rwalk"; then
      ok "rustc walk RUSTC_LOG from driver"
    else
      bad "rustc walk RUSTC_LOG from driver" "$(printf '%s\n' "$rwalk" | grep RUSTC_ | head)"
    fi
    rkind="$(echo "$rabi" | awk -F'\t' '$1=="RUSTC_LOG"{k=$2} END{print k}')"
    rhow="$(echo "$rabi" | awk -F'\t' '$1=="RUSTC_LOG"{h=$5} END{print h}')"
    echo "  note  RUSTC_LOG kind=$rkind $rhow"
    if [[ "$rkind" == "DUE" || "$rkind" == "BOTH" ]]; then
      ok "rustc RUSTC_LOG is an env::var use"
    else
      bad "rustc RUSTC_LOG is an env::var use" "kind=$rkind"
    fi
    rlatc="$(echo "$rabi" | awk -F'\t' '$2=="LATENT"{c++} END{print c+0}')"
    rduec="$(echo "$rabi" | awk -F'\t' '$2=="DUE"{c++} END{print c+0}')"
    rbothc="$(echo "$rabi" | awk -F'\t' '$2=="BOTH"{c++} END{print c+0}')"
    echo "  note  rustc --app kinds due=$rduec latent=$rlatc both=$rbothc  (assay: due=12596)"
    rice="$(echo "$rabi" | awk -F'\t' '$1=="RUSTC_ICE"{k=$2} END{print k}')"
    rfont="$(echo "$rabi" | awk -F'\t' '$1=="RUSTC_GRAPHVIZ_FONT"{k=$2} END{print k}')"
    echo "  note  RUSTC_ICE kind=$rice RUSTC_GRAPHVIZ_FONT kind=$rfont"
    if [[ "$rfont" == "LATENT" || "$rfont" == "BOTH" ]]; then
      ok "rustc GRAPHVIZ_FONT is documented (LATENT/BOTH)"
    else
      bad "rustc GRAPHVIZ_FONT is documented" "FONT=$rfont"
    fi
    if [[ "$rduec" -lt 200 ]]; then
      ok "rustc DUE is not ~12k LLVM opcodes ($rduec)"
    else
      bad "rustc DUE is not ~12k LLVM opcodes" "due=$rduec"
    fi
    if echo "$rwalk" | grep -q AMDGPU_BUFFER_ATOMIC; then
      bad "rustc DUE has no LLVM opcode dump" "$(printf '%s\n' "$rwalk" | grep AMDGPU | head)"
    else
      ok "rustc DUE has no LLVM opcode dump"
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
  knames="$("$PROVE" --names --app --min-evidence call "$KIZU/src")"
  for want in KIZU_CONFIG KIZU_STATE_DIR KIZU_SESSION_ID TMUX ZELLIJ KITTY_LISTEN_ON; do
    if has "$want" "$knames"; then
      ok "kizu src $want"
    else
      bad "kizu src $want" "$knames"
    fi
  done
  if [[ -x "$KIZU/target/release/kizu" ]]; then
    join="$("$PROVE" --tsv --app --min-evidence call "$KIZU/src" --vs-program "$KIZU/target/release/kizu")"
    echo "$join" | awk -F'\t' '$1=="BOTH" || $1=="LEFT_ONLY" {print "  note  "$1" "$3}'
    if echo "$join" | awk -F'\t' '$1=="BOTH" && $3=="KIZU_CONFIG" {found=1} END{exit !found}'; then
      ok "kizu source⋈image KIZU_CONFIG"
    else
      echo "  note  kizu join missed KIZU_CONFIG (image may pack env::var)"
      ok "kizu source⋈image ran"
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
  gnames="$("$PROVE" --names --app "$GIT_BIN" || true)"
  echo "  note  git=$GIT_BIN --app names: $(echo "$gnames" | grep -c . || true)"
  if echo "$gnames" | grep -q '^GIT_DIR$'; then
    ok "git binary GIT_DIR"
  elif echo "$gnames" | grep -q '^GIT_'; then
    ok "git binary exposes GIT_* getenv uses"
  else
    echo "  note  no GIT_* strings in $GIT_BIN"
    ok "git binary harvest ran"
  fi
  if echo "$gnames" | grep -q '^ARRAY_SIZE$'; then
    bad "git DUE is not compiler tokens" "$gnames"
  else
    ok "git DUE is not ARRAY_SIZE"
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
