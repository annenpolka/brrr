#!/usr/bin/env bash
# Re-run the call-site holes against victim xref. No rewrite.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
XREF="${XREF:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-cb96e7158c54/xref}"
SRC="$ROOT/fixtures/src"
OUT="${OUT:-/tmp/destroy-xref/demo}"
mkdir -p "$OUT"

pass=0
fail=0

ok() { pass=$((pass + 1)); echo "  PASS  $1"; }
bad() { fail=$((fail + 1)); echo "  FAIL  $1"; echo "        $2"; }

need() {
  local hay="$1" needle="$2"
  [[ "$hay" == *"$needle"* ]]
}

if [[ ! -x "$XREF" ]]; then
  echo "demo: xref not executable: $XREF" >&2
  exit 2
fi

echo "== selftest (victim, no rewrite) =="
if "$XREF" --selftest >/dev/null; then
  ok "selftest"
else
  bad "selftest" "exit $?"
fi

echo "== gold: direct getenv is DUE =="
cc -o "$OUT/direct" "$SRC/direct.c"
got=$("$XREF" --app "$OUT/direct")
if need "$got" "DIRECT_ENV_NAME" && need "$got" "DUE"; then
  ok "direct getenv DUE"
else
  bad "direct getenv DUE" "$got"
fi

echo "== gold: orphan default empty =="
VFIX="$(dirname "$XREF")/fixtures/xref/orphan.c"
if [[ -f "$VFIX" ]]; then
  cc -o "$OUT/orphan" "$VFIX"
  got=$("$XREF" --app "$OUT/orphan")
  if need "$got" "(no owed names)"; then
    ok "orphan default empty"
  else
    bad "orphan default empty" "$got"
  fi
  got=$("$XREF" --app --loose "$OUT/orphan")
  if need "$got" "ORPHAN_ENV_NAME" && need "$got" "DUE"; then
    ok "--loose orphan KIND=DUE (hole)"
  else
    bad "--loose orphan KIND=DUE" "$got"
  fi
fi

echo "== hole: *getenv suffix is DUE without libc getenv =="
cc -O0 -fno-inline -o "$OUT/false" "$SRC/false_getenv2.c"
got=$("$XREF" --app "$OUT/false")
if need "$got" "FALSE_DUE_NAME" && need "$got" "DUE"; then
  ok "FALSE_DUE_NAME DUE (false proof)"
else
  bad "FALSE_DUE_NAME DUE" "$got"
fi
if need "$got" "FORGET_ENV_NAME"; then
  ok "FORGET_ENV_NAME DUE (false proof)"
else
  bad "FORGET_ENV_NAME DUE" "$got"
fi

echo "== hole: one-hop wrapper miss at -O0 =="
cc -O0 -o "$OUT/wrap" "$SRC/wrap.c"
got=$("$XREF" --app "$OUT/wrap")
if need "$got" "DIRECT_ENV_NAME"; then
  ok "wrap-O0 keeps DIRECT"
else
  bad "wrap-O0 DIRECT" "$got"
fi
if need "$got" "WRAP_ENV_NAME"; then
  bad "wrap-O0 WRAP should miss" "$got"
else
  ok "wrap-O0 WRAP_ENV_NAME missing (hole)"
fi

echo "== hole: fat native slice hides the other arch =="
if cc -arch arm64 -o "$OUT/fat-arm" "$SRC/fat_arm.c" \
  && cc -arch x86_64 -o "$OUT/fat-x86" "$SRC/fat_x86.c" \
  && lipo -create "$OUT/fat-arm" "$OUT/fat-x86" -output "$OUT/fat"; then
  got=$("$XREF" --app "$OUT/fat")
  if need "$got" "FAT_ARM64_NAME" && ! need "$got" "FAT_X86_NAME"; then
    ok "fat DUE is native slice only"
  else
    bad "fat native slice" "$got"
  fi
else
  echo "  SKIP  fat (no x86_64 cc/lipo)"
fi

echo "== hole: blr GOT getenv miss =="
if cc -o "$OUT/blr" "$SRC/blr.s" 2>/dev/null; then
  got=$("$XREF" --app "$OUT/blr")
  if need "$got" "(no owed names)"; then
    ok "blr getenv unaskable"
  else
    bad "blr should miss" "$got"
  fi
else
  echo "  SKIP  blr.s"
fi

echo "== hole: GPU NAME = is LATENT =="
cc -o "$OUT/gpu" "$SRC/gpu_assign.c"
got=$("$XREF" --app "$OUT/gpu")
if need "$got" "STACK_SIZE" && need "$got" "LATENT"; then
  ok "STACK_SIZE false LATENT"
else
  bad "STACK_SIZE LATENT" "$got"
fi

echo "== dogfood: /bin/ls arm64e (survived) =="
got=$("$XREF" --names --app /bin/ls)
if need "$got" "CLICOLOR_FORCE"; then
  ok "ls CLICOLOR_FORCE"
else
  bad "ls CLICOLOR_FORCE" "$got"
fi
if printf '%s\n' "$got" | grep -qx 'COLOR_FORCE'; then
  bad "ls must not emit COLOR_FORCE as a name" "$got"
else
  ok "ls no COLOR_FORCE peel"
fi

echo "== dogfood: Homebrew python3 poster (survived + hole) =="
if command -v python3 >/dev/null; then
  abi=$("$XREF" --dump-abi --app python3)
  gil=$(printf '%s\n' "$abi" | awk -F'\t' '$1=="PYTHON_GIL" {print $2}')
  home=$(printf '%s\n' "$abi" | awk -F'\t' '$1=="PYTHONHOME" {print $2}')
  if [[ "$gil" == "DUE" ]]; then
    ok "PYTHON_GIL DUE"
  else
    bad "PYTHON_GIL DUE" "$gil"
  fi
  if [[ "$home" == "LATENT" ]]; then
    ok "PYTHONHOME LATENT (wrapper hole)"
  else
    bad "PYTHONHOME LATENT" "$home"
  fi
fi

echo "== dogfood: xcselect shim empty =="
got=$("$XREF" --app /usr/bin/python3)
if need "$got" "(no owed names)"; then
  ok "/usr/bin/python3 empty (shim)"
else
  bad "/usr/bin/python3" "$got"
fi

echo
echo "PASS=$pass FAIL=$fail"
if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
exit 0
