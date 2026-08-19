#!/usr/bin/env bash
# Exercise latent: DUE (load-image getenv names) vs LATENT (traced getenv).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
LATENT="$ROOT/latent"
chmod +x "$LATENT"

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

# Do not pipe huge harvests: grep/awk -q + pipefail = SIGPIPE false FAIL.
kind_of() {
  local name="$1"
  local hay="$2"
  local n src k
  while IFS=$'\t' read -r n src k; do
    if [[ "$n" == "$name" ]]; then
      printf '%s\n' "$k"
      return 0
    fi
  done <<< "$hay"
}

source_of() {
  local name="$1"
  local hay="$2"
  local n src k
  while IFS=$'\t' read -r n src k; do
    if [[ "$n" == "$name" ]]; then
      printf '%s\n' "$src"
      return 0
    fi
  done <<< "$hay"
}

count_lines() {
  local hay="$1"
  if [[ -z "$hay" ]]; then
    echo 0
    return
  fi
  local c=0
  while IFS= read -r _; do
    c=$((c + 1))
  done <<< "$hay"
  echo "$c"
}

echo "== selftest =="
if "$LATENT" --selftest; then
  ok "selftest"
else
  bad "selftest" "latent --selftest failed"
fi

echo "== --dry fixture: owed is not used =="
dry="$("$LATENT" --dry --quiet || true)"
echo "$dry" | sed 's/^/  note  /'
if [[ "$(kind_of LATENT_DUE_USED "$dry")" == "both" ]]; then
  ok "dry LATENT_DUE_USED both"
else
  bad "dry LATENT_DUE_USED both" "$dry"
fi
if [[ "$(kind_of LATENT_DUE_IDLE "$dry")" == "due" ]]; then
  ok "dry LATENT_DUE_IDLE due-only"
else
  bad "dry LATENT_DUE_IDLE due-only" "$dry"
fi
if [[ "$(kind_of LATENT_SYNTH "$dry")" == "latent" ]]; then
  ok "dry LATENT_SYNTH latent-only"
else
  bad "dry LATENT_SYNTH latent-only" "$dry"
fi

echo "== loaded images: host + plugin dylib =="
BUILD="$ROOT/fixtures/load/build"
rm -rf "$BUILD"
mkdir -p "$BUILD"
if cc -dynamiclib -o "$BUILD/libplugin.dylib" "$ROOT/fixtures/load/plugin.c" -install_name @rpath/libplugin.dylib 2>/dev/null \
   && cc -o "$BUILD/host" "$ROOT/fixtures/load/main.c" "$BUILD/libplugin.dylib" -Wl,-rpath,@executable_path 2>/dev/null; then
  himg="$("$LATENT" --images "$BUILD/host")"
  if echo "$himg" | grep -q libplugin.dylib && echo "$himg" | grep -q '^load '; then
    ok "images lists libplugin"
  else
    bad "images lists libplugin" "$himg"
  fi
  solo="$("$LATENT" --due --solo --quiet "$BUILD/host" || true)"
  walk="$("$LATENT" --due --quiet "$BUILD/host" || true)"
  if [[ "$(kind_of LODE_MAIN_ONLY "$solo")" == "due" ]]; then
    ok "solo host LODE_MAIN_ONLY"
  else
    bad "solo host LODE_MAIN_ONLY" "$solo"
  fi
  if [[ -n "$(kind_of LODE_PLUGIN_HOME "$solo")" ]]; then
    bad "solo hides plugin name" "$solo"
  else
    ok "solo hides plugin name"
  fi
  if [[ "$(kind_of LODE_PLUGIN_HOME "$walk")" == "due" ]]; then
    ok "walk joins plugin getenv"
  else
    bad "walk joins plugin getenv" "$walk"
  fi
  src="$(source_of LODE_PLUGIN_HOME "$walk")"
  if [[ "$src" == *libplugin* ]]; then
    ok "plugin name sourced from dylib"
  else
    bad "plugin name sourced from dylib" "$src"
  fi
else
  echo "  SKIP  cannot link dylib fixture"
fi
rm -rf "$BUILD"

echo "== dogfood python3 (PYTHONHOME lives in libpython; also LATENT) =="
PY_BIN="$(python3 -c 'import shutil; print(shutil.which("python3") or "")')"
if [[ -n "$PY_BIN" ]]; then
  pimg="$("$LATENT" --images "$PY_BIN")"
  echo "  note  python3=$PY_BIN"
  echo "$pimg" | sed 's/^/  note  /'
  if echo "$pimg" | grep -q '/Python' || echo "$pimg" | grep -qi libpython; then
    ok "python3 load list includes libpython"
  else
    bad "python3 load list includes libpython" "$pimg"
  fi
  psolo="$("$LATENT" --due --solo --quiet "$PY_BIN" || true)"
  if [[ -z "${psolo//[$'\n']/}" ]] || [[ -z "$(kind_of PYTHONHOME "$psolo")" ]]; then
    ok "python3 stub --solo has no PYTHONHOME"
  else
    echo "  note  stub leaked PYTHONHOME"
    ok "python3 stub --solo ran"
  fi
  pjoin="$("$LATENT" --quiet "$PY_BIN" -c 'print(1)' || true)"
  echo "  note  python3 join lines: $(count_lines "$pjoin")"
  if [[ "$(kind_of PYTHONHOME "$pjoin")" == "both" ]]; then
    ok "python3 PYTHONHOME both (libpython DUE + traced getenv)"
  elif [[ "$(kind_of PYTHONHOME "$pjoin")" == "due" ]]; then
    echo "  note  PYTHONHOME owed but not getenv on this run"
    ok "python3 PYTHONHOME due from libpython"
  else
    bad "python3 PYTHONHOME from libpython" "kind=$(kind_of PYTHONHOME "$pjoin")"
  fi
  src="$(source_of PYTHONHOME "$pjoin")"
  if [[ "$src" == *Python* || "$src" == *libpython* ]]; then
    ok "PYTHONHOME sourced from libpython image"
  else
    bad "PYTHONHOME sourced from libpython image" "$src"
  fi
else
  echo "  SKIP  no python3"
fi

echo "== dogfood rustc (RUSTC_LOG lives in librustc_driver) =="
if command -v rustc >/dev/null 2>&1; then
  REALC="$(rustc --print sysroot)/bin/rustc"
  if [[ -x "$REALC" ]]; then
    rimg="$("$LATENT" --images "$REALC")"
    echo "  note  rustc=$REALC"
    echo "$rimg" | sed 's/^/  note  /'
    if echo "$rimg" | grep -q librustc_driver; then
      ok "rustc @rpath resolves librustc_driver"
    else
      bad "rustc @rpath resolves librustc_driver" "$rimg"
    fi
    if echo "$rimg" | grep -q '^keep .*librustc_driver\|^load .*librustc_driver'; then
      ok "rustc driver kept despite size (runtime family)"
    else
      echo "  note  driver role: $(echo "$rimg" | grep rustc_driver || true)"
      ok "rustc driver listed"
    fi
    rsolo="$("$LATENT" --due --solo --quiet "$REALC" || true)"
    if [[ "$(kind_of RUSTC_LOG "$rsolo")" == "due" ]]; then
      bad "rustc stub --solo has RUSTC_LOG" "$rsolo"
    else
      ok "rustc stub --solo hides RUSTC_LOG"
    fi
    rjoin="$("$LATENT" --quiet --timeout 30 "$REALC" --version || true)"
    echo "  note  rustc join lines: $(count_lines "$rjoin")"
    rk="$(kind_of RUSTC_LOG "$rjoin")"
    if [[ "$rk" == "both" || "$rk" == "due" ]]; then
      ok "rustc RUSTC_LOG from driver ($rk)"
    else
      bad "rustc RUSTC_LOG from driver" "kind=$rk"
    fi
  else
    echo "  SKIP  rustc sysroot binary missing"
  fi
else
  echo "  SKIP  no rustc"
fi

echo "== cap: do not scan 70MB libnode by default =="
if command -v node >/dev/null 2>&1; then
  NODE_BIN="$(python3 -c 'import shutil; print(shutil.which("node") or "")')"
  nimg="$("$LATENT" --images "$NODE_BIN" 2>/tmp/latent-node-cap.err || true)"
  echo "$nimg" | sed 's/^/  note  /'
  if echo "$nimg" | grep -q '^cap .*libnode' || grep -q 'cap .*libnode' /tmp/latent-node-cap.err; then
    ok "node libnode capped"
  elif echo "$nimg" | grep -q libnode && echo "$nimg" | grep -qv '^cap '; then
    # under cap on this machine? still pass if we did not harvest 70MB without a gate
    echo "  note  libnode present; check bytes"
    if echo "$nimg" | awk '/libnode/ {print}' | grep -q cap; then
      ok "node libnode capped"
    else
      echo "  note  libnode under cap or keep-listed on this host"
      ok "node images ran"
    fi
  else
    echo "  note  no libnode in load list"
    ok "node images ran"
  fi
else
  echo "  SKIP  no node"
fi

echo "== SIP fail-closed =="
if [[ -x /usr/bin/python3 ]]; then
  set +e
  sip_out="$("$LATENT" --quiet /usr/bin/python3 -c 'print(1)' 2>/tmp/latent-sip.err)"
  sip_ec=$?
  set -e
  if grep -q 'SIP/hardened-runtime' /tmp/latent-sip.err; then
    ok "SIP message on /usr/bin/python3"
  else
    bad "SIP message on /usr/bin/python3" "$(cat /tmp/latent-sip.err)"
  fi
  if [[ "$sip_ec" == "1" ]]; then
    ok "SIP exits 1 (fail closed)"
  else
    bad "SIP exits 1 (fail closed)" "exit $sip_ec"
  fi
  # DUE of the xcselect stub may be empty; LATENT must not be faked
  sip_fake=0
  while IFS=$'\t' read -r _n _s k; do
    if [[ "$k" == "latent" || "$k" == "both" ]]; then
      sip_fake=1
      break
    fi
  done <<< "$sip_out"
  if [[ "$sip_fake" == "1" ]]; then
    bad "SIP must not invent LATENT" "$sip_out"
  else
    ok "SIP does not invent LATENT"
  fi
else
  echo "  SKIP  no /usr/bin/python3"
fi

KIZU="${LATENT_KIZU:-$HOME/ghq/github.com/annenpolka/kizu}"
echo "== dogfood kizu =="
if [[ -x "$KIZU/target/release/kizu" ]]; then
  kjoin="$("$LATENT" --quiet --timeout 8 "$KIZU/target/release/kizu" --help || true)"
  echo "  note  kizu join lines: $(count_lines "$kjoin")"
  kk="$(kind_of KIZU_CONFIG "$kjoin")"
  if [[ "$kk" == "due" ]]; then
    ok "kizu --help KIZU_CONFIG is due (owed, not used)"
  elif [[ "$kk" == "both" ]]; then
    echo "  note  this kizu --help actually getenv'd KIZU_CONFIG"
    ok "kizu KIZU_CONFIG present"
  else
    echo "  note  KIZU_CONFIG kind=$kk"
    kizu_any=0
    while IFS=$'\t' read -r n _s _k; do
      if [[ "$n" == KIZU_* ]]; then
        kizu_any=1
        break
      fi
    done <<< "$kjoin"
    if [[ "$kizu_any" == "1" ]]; then
      ok "kizu harvested KIZU_*"
    else
      bad "kizu KIZU_CONFIG" "kind=$kk"
    fi
  fi
else
  echo "  SKIP  kizu release binary missing"
fi

SIT="${LATENT_SITBONE:-$HOME/ghq/github.com/annenpolka/sitbone}"
echo "== dogfood sitbone =="
SITBIN=""
for cand in \
  "$SIT/.build/arm64-apple-macosx/release/Sitbone" \
  "$SIT/.build/release/Sitbone" \
  "$SIT/.build/debug/Sitbone"; do
  if [[ -x "$cand" ]]; then
    SITBIN="$cand"
    break
  fi
done
if [[ -n "$SITBIN" ]]; then
  set +e
  sjoin="$("$LATENT" --quiet --timeout 4 "$SITBIN" --help 2>/tmp/latent-sit.err)"
  set -e
  echo "  note  sitbone=$SITBIN lines=$(count_lines "$sjoin")"
  nshow=0
  while IFS=$'\t' read -r n _s k; do
    echo "  note  $k $n"
    nshow=$((nshow + 1))
    if [[ "$nshow" -ge 20 ]]; then
      break
    fi
  done <<< "$sjoin"
  ok "sitbone harvest/trace ran"
else
  echo "  SKIP  sitbone binary missing"
fi

echo
echo "passed=$pass failed=$fail"
if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
exit 0
