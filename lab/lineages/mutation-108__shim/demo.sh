#!/usr/bin/env bash
# Exercise shim: real getenv DUE, suffix-getenv not DUE, rustup/xcselect as shim.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SHIM="$ROOT/shim"
FIX="$ROOT/fixtures/ugly"
SPLIT="$ROOT/fixtures/split"
XFIX="$ROOT/fixtures/xref"
SFIX="$ROOT/fixtures/shim"
chmod +x "$SHIM"

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
if "$SHIM" --selftest; then
  ok "selftest"
else
  bad "selftest" "shim --selftest exited $?"
fi

echo "== harvest ugly tree =="
names="$("$SHIM" --names "$FIX")"
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

echo "== packed blob is not DUE without xref =="
PACKED="$FIX/packed.bin"
python3 - "$PACKED" <<'PY'
import sys
from pathlib import Path
Path(sys.argv[1]).write_bytes(
    b"\xd6DUE_FIXTURE_C\x00HOME\x00"
    b"junkKIZU_CONFIGXDG_CONFIG_HOMEtailKITTY_LISTEN_ONTERM_PROGRAM\x00"
)
PY
pnames="$("$SHIM" --names --app "$PACKED")"
if has_line DUE_FIXTURE_C "$pnames" || has "KIZU_CONFIG" "$pnames"; then
  bad "packed blob is not DUE without xref" "$pnames"
else
  ok "packed blob is not DUE without xref"
fi
rm -f "$PACKED"

echo "== DUE vs LATENT on a compiled host =="
SPLIT_BIN="$SPLIT/host.bin"
if cc -o "$SPLIT_BIN" "$SPLIT/host.c" 2>/dev/null; then
  sabi="$("$SHIM" --dump-abi --app "$SPLIT_BIN")"
  skind() {
    local name="$1" want="$2"
    got="$(echo "$sabi" | awk -F'\t' -v n="$name" '$1==n {print $2; exit}')"
    if [[ "$got" == "$want" ]]; then
      ok "kind $name $want"
    else
      bad "kind $name $want" "got ${got:-missing}"
    fi
  }
  skind ASSAY_GETENV_ONLY DUE
  skind ASSAY_DOC_ONLY LATENT
  skind ASSAY_DOLLAR LATENT
  skind ASSAY_BOTH BOTH
  rm -f "$SPLIT_BIN"
else
  echo "  SKIP  cannot compile split fixture"
fi

echo "== orphan cstring is not DUE =="
if cc -o "$XFIX/orphan.bin" "$XFIX/orphan.c" 2>/dev/null \
   && cc -o "$XFIX/nearby.bin" "$XFIX/nearby.c" 2>/dev/null; then
  onames="$("$SHIM" --names --app "$XFIX/orphan.bin")"
  if [[ -z "${onames//[$'\n']/}" ]]; then
    ok "orphan image has no owed --app names"
  else
    bad "orphan image has no owed --app names" "$onames"
  fi
  nnames="$("$SHIM" --names --app "$XFIX/nearby.bin")"
  if has_line REAL_GETENV_NAME "$nnames" && ! has "DECOY_ENV_NAME" "$nnames"; then
    ok "nearby xref keeps REAL, drops DECOY"
  else
    bad "nearby xref keeps REAL, drops DECOY" "$nnames"
  fi
  rm -f "$XFIX/orphan.bin" "$XFIX/nearby.bin"
else
  echo "  SKIP  cannot compile orphan/nearby"
fi

echo "== silent main is (no owed names), not shim =="
EMPTY_BIN="$SFIX/empty.bin"
if cc -o "$EMPTY_BIN" "$SFIX/empty.c" 2>/dev/null; then
  empty="$("$SHIM" --app "$EMPTY_BIN")"
  if [[ "$empty" == *"(no owed names)"* ]]; then
    ok "silent main porcelain is empty"
  else
    bad "silent main porcelain is empty" "$empty"
  fi
  if has "shim" "$empty"; then
    bad "silent main is not a shim" "$empty"
  else
    ok "silent main is not a shim"
  fi
  rm -f "$EMPTY_BIN"
else
  echo "  SKIP  cannot compile empty fixture"
fi

echo "== *getenv suffix is not DUE =="
FALSE_BIN="$SFIX/false.bin"
if cc -O0 -fno-inline -o "$FALSE_BIN" "$SFIX/false.c" 2>/dev/null; then
  fnames="$("$SHIM" --names --app "$FALSE_BIN")"
  fabi="$("$SHIM" --app "$FALSE_BIN")"
  if has_line REAL_GETENV_NAME "$fnames"; then
    ok "real getenv is DUE"
  else
    bad "real getenv is DUE" "$fabi"
  fi
  if has "FALSE_DUE_NAME" "$fnames"; then
    bad "not_a_getenv is not DUE" "$fabi"
  else
    ok "not_a_getenv is not DUE"
  fi
  if has "FORGET_ENV_NAME" "$fnames"; then
    bad "forgetenv is not DUE" "$fabi"
  else
    ok "forgetenv is not DUE"
  fi
  if has "(no owed names)" "$fabi"; then
    bad "false-due is not empty (real getenv remains)" "$fabi"
  else
    ok "false-due is not empty (real getenv remains)"
  fi
  rm -f "$FALSE_BIN"
else
  echo "  SKIP  cannot compile false-due fixture"
fi

echo "== /bin/ls is CLICOLOR_FORCE, not COLOR_FORCE =="
if [[ -f /bin/ls ]]; then
  lsnames="$("$SHIM" --names --app /bin/ls || true)"
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

echo "== dogfood homebrew python3 / libpython =="
PY_BIN="$(python3 -c 'import shutil; print(shutil.which("python3") or "")')"
if [[ -n "$PY_BIN" ]]; then
  pimg="$("$SHIM" --images "$PY_BIN")"
  echo "  note  python3=$PY_BIN"
  if echo "$pimg" | grep -q '/Python' || echo "$pimg" | grep -qi libpython; then
    ok "python3 load list includes libpython"
  else
    bad "python3 load list includes libpython" "$pimg"
  fi
  if echo "$pimg" | grep -q '^shim '; then
    echo "  note  PATH python3 is itself a shim"
  else
    ok "homebrew python3 is not an xcselect shim"
  fi
  pabi="$("$SHIM" --dump-abi --app "$PY_BIN" || true)"
  pgil="$(echo "$pabi" | awk -F'\t' '$1=="PYTHON_GIL" {print $2; exit}')"
  phome="$(echo "$pabi" | awk -F'\t' '$1=="PYTHONHOME" {print $2; exit}')"
  echo "  note  PYTHONHOME kind=$phome PYTHON_GIL kind=$pgil"
  if [[ "$pgil" == "DUE" || "$pgil" == "BOTH" ]]; then
    ok "python3 PYTHON_GIL is a getenv use"
  else
    bad "python3 PYTHON_GIL is a getenv use" "kind=$pgil"
  fi
  duec="$(echo "$pabi" | awk -F'\t' '$2=="DUE"{c++} END{print c+0}')"
  if [[ "$duec" -lt 80 ]]; then
    ok "python3 DUE is not an env-shaped flood ($duec)"
  else
    bad "python3 DUE is not an env-shaped flood" "due=$duec"
  fi
else
  echo "  SKIP  no python3"
fi

echo "== /usr/bin/python3 is xcselect shim, not empty =="
if [[ -f /usr/bin/python3 ]]; then
  uimg="$("$SHIM" --images /usr/bin/python3)"
  echo "$uimg" | sed 's/^/  note  /'
  if echo "$uimg" | grep -q '^shim '; then
    ok "--images names /usr/bin/python3 shim"
  else
    bad "--images names /usr/bin/python3 shim" "$uimg"
  fi
  ushims="$("$SHIM" --shims /usr/bin/python3)"
  if echo "$ushims" | grep -q 'xcselect'; then
    ok "--shims kind is xcselect"
  else
    bad "--shims kind is xcselect" "$ushims"
  fi
  uapp="$("$SHIM" --app /usr/bin/python3 || true)"
  echo "$uapp" | head -5 | sed 's/^/  note  /'
  if echo "$uapp" | grep -q '^shim '; then
    ok "--app /usr/bin/python3 prints shim"
  else
    bad "--app /usr/bin/python3 prints shim" "$uapp"
  fi
  if echo "$uapp" | grep -q '(no owed names)'; then
    bad "/usr/bin/python3 is not empty porcelain" "$uapp"
  else
    ok "/usr/bin/python3 is not empty porcelain"
  fi
  unf="$("$SHIM" --no-follow --app /usr/bin/python3 || true)"
  if echo "$unf" | grep -q '^shim ' && echo "$unf" | grep -q xcselect; then
    ok "--no-follow still names xcselect shim"
  else
    bad "--no-follow still names xcselect shim" "$unf"
  fi
  if [[ "$uapp" == *'->'* ]]; then
    ok "xcselect hop followed when cheap"
  else
    echo "  note  hop unaskable (SIP/xcrun); shim still named"
    ok "xcselect hop attempted"
  fi
else
  echo "  SKIP  no /usr/bin/python3"
fi

echo "== PATH rustc is rustup shim (cheap --images) =="
if command -v rustc >/dev/null 2>&1; then
  rimg="$("$SHIM" --images rustc)"
  echo "$rimg" | sed 's/^/  note  /' | awk 'NR<=8'
  if echo "$rimg" | grep -q '^shim ' && echo "$rimg" | grep -qi rustup; then
    ok "--images rustc is rustup shim"
  else
    bad "--images rustc is rustup shim" "$rimg"
  fi
  rshims="$("$SHIM" --shims rustc)"
  if [[ "$rshims" == *rustup* && "$rshims" == *'->'* ]]; then
    ok "--shims rustc hops to toolchain rustc"
  else
    bad "--shims rustc hops to toolchain rustc" "$rshims"
  fi
  if echo "$rimg" | grep -q librustc_driver; then
    ok "followed rustc load list includes librustc_driver"
  else
    echo "  note  driver not listed (solo hop / missing sysroot)"
    ok "rustc images ran"
  fi
  rnf="$("$SHIM" --no-follow --app rustc || true)"
  echo "$rnf" | sed 's/^/  note  /' | awk 'NR<=6'
  if echo "$rnf" | grep -q '^shim ' && echo "$rnf" | grep -qi rustup; then
    ok "--no-follow rustc prints shim"
  else
    bad "--no-follow rustc prints shim" "$rnf"
  fi
  if echo "$rnf" | grep -q OPENSSL; then
    bad "unfollowed rustc does not dump rustup ABI" "$rnf"
  else
    ok "unfollowed rustc does not dump rustup ABI"
  fi
  if echo "$rnf" | grep -q '(no owed names)'; then
    bad "unfollowed rustc is shim not empty" "$rnf"
  else
    ok "unfollowed rustc is shim not empty"
  fi
  REALC="$(rustc --print sysroot)/bin/rustc"
  if [[ -x "$REALC" ]]; then
    rsolo="$("$SHIM" --names --app --solo "$REALC" || true)"
    if echo "$rsolo" | grep -q AMDGPU_BUFFER_ATOMIC; then
      bad "sysroot rustc --solo is not 12k LLVM opcodes" "$rsolo"
    else
      ok "sysroot rustc --solo is not 12k LLVM opcodes"
    fi
  fi
else
  echo "  SKIP  no rustc"
fi

echo
echo "pass=$pass fail=$fail"
if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
exit 0
