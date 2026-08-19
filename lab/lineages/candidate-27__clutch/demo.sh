#!/usr/bin/env bash
# Exercise clutch on a synthetic generation lot, then nearby real trees.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
CLUTCH="$ROOT/clutch"
chmod +x "$CLUTCH"

PASS=0
FAIL=0

ok() { PASS=$((PASS + 1)); echo "  ok  $1"; }
bad() { FAIL=$((FAIL + 1)); echo "  FAIL $1" >&2; echo "       $2" >&2; }

assert_grep() {
  local name="$1" needle="$2" hay="$3"
  if grep -F -q -- "$needle" <<<"$hay"; then
    ok "$name"
  else
    bad "$name" "missing '$needle' in: $hay"
  fi
}

assert_no() {
  local name="$1" needle="$2" hay="$3"
  if grep -F -q -- "$needle" <<<"$hay"; then
    bad "$name" "unexpected '$needle'"
  else
    ok "$name"
  fi
}

echo "== selftest =="
if "$CLUTCH" --selftest; then
  ok "selftest"
else
  bad "selftest" "clutch --selftest exited $?"
fi

echo "== fixture =="
FIX="$(mktemp -d "${TMPDIR:-/tmp}/clutch-demo.XXXXXX")"
cleanup() { rm -rf "$FIX"; }
trap cleanup EXIT
"$CLUTCH" --write-fixture "$FIX/repo" >/dev/null
FIXREPO="$FIX/repo"

out="$("$CLUTCH" -C "$FIXREPO" --ok-cold -v || true)"
assert_grep "fixture split clutch" "SPLIT" "$out"
assert_grep "fixture stale sibling b.md" "STALE" "$out"
assert_grep "fixture cites main.pkl" "specs/main.pkl" "$out"
assert_grep "fixture orphan" "ghost.md" "$out"
assert_grep "fixture mute" "mute.md" "$out"
assert_grep "fixture honban" "specs/honban.pkl" "$out"
assert_grep "fixture unicode" "計画.md" "$out"
assert_grep "fixture host-a" "builder-a" "$out"
assert_grep "fixture host-b" "builder-b" "$out"
assert_grep "fixture json stamp" "manifest.json" "$out"

tsv="$("$CLUTCH" -C "$FIXREPO" --tsv --ok-cold || true)"
assert_grep "tsv header" "verdict" "$tsv"
assert_grep "tsv parent column" "specs/main.pkl" "$tsv"

jsfile="$FIX/out.json"
"$CLUTCH" -C "$FIXREPO" --json --ok-cold >"$jsfile" || true
python3 - "$jsfile" <<'PY'
import json, sys
data = json.load(open(sys.argv[1]))
assert data["clutches"], "no clutches"
parents = {c["clutch"] for c in data["clutches"]}
assert any("main.pkl" in p for p in parents), parents
print("json-clutches", len(data["clutches"]), "members", len(data["members"]))
PY
ok "json parse"

echo "== explain =="
exp="$("$CLUTCH" -C "$FIXREPO" --explain out/a.md)"
assert_grep "explain parent" "specs/main.pkl" "$exp"
assert_grep "explain stamp" "sha256:" "$exp"
assert_grep "explain generated-from" "generated-from" "$exp"

dogfood() {
  local name="$1" repo="$2"
  shift 2
  if [[ ! -d "$repo/.git" && ! -d "$repo" ]]; then
    echo "  skip $name (missing $repo)"
    return
  fi
  echo "== dogfood $name =="
  local extra=("$@")
  local text
  set +e
  text="$("$CLUTCH" -C "$repo" --summary "${extra[@]}")"
  local st=$?
  set -e
  echo "$text" | head -40
  echo "  (exit $st)"
  if [[ -n "$text" ]]; then
    ok "$name ran"
  else
    # empty is legal (no receipts)
    ok "$name ran empty"
  fi
}

VT="/Users/annenpolka/ghq/github.com/annenpolka/voidtrace"
TE="/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi"
RE="/Users/annenpolka/ghq/github.com/annenpolka/relico"
KZ="/Users/annenpolka/ghq/github.com/annenpolka/kizu"
SB="/Users/annenpolka/ghq/github.com/annenpolka/sitbone"
KO="/Users/annenpolka/ghq/github.com/annenpolka/koyomi-trace"
SK="/Users/annenpolka/ghq/github.com/annenpolka/skills"

if [[ -d "$VT" ]]; then
  echo "== dogfood voidtrace (whole tree) =="
  set +e
  vt="$("$CLUTCH" -C "$VT" --ok-cold -v)"
  st=$?
  set -e
  echo "$vt" | head -60
  echo "  (exit $st)"
  assert_grep "voidtrace clutch parent" "specs/main.pkl" "$vt"
  assert_grep "voidtrace AI_UX COLD" "AI_UX.md" "$vt"
  assert_grep "voidtrace SPEC present" "SPEC.md" "$vt"
  assert_grep "voidtrace stamp-join capabilities" "capabilities.generated.json" "$vt"
  assert_grep "voidtrace ragged" "RAGGED" "$vt"
  assert_no "voidtrace no pnpm-store" ".pnpm-store" "$vt"
fi

if [[ -d "$TE" ]]; then
  echo "== dogfood tenaoshi =="
  set +e
  te="$("$CLUTCH" -C "$TE" -v)"
  st=$?
  set -e
  echo "$te"
  echo "  (exit $st)"
  assert_grep "tenaoshi parent" "specs/tenaoshi.pkl" "$te"
  assert_grep "tenaoshi oracles" "OraclesGenerated.swift" "$te"
  assert_no "tenaoshi no jp-comma parent" "specs/、" "$te"
  assert_no "tenaoshi no AGENTS glob" "specs/*.pkl" "$te"
  assert_no "tenaoshi no spec-gen prose" "tools/spec-gen.ts" "$te"
fi

if [[ -d "$RE" ]]; then
  echo "== dogfood relico =="
  set +e
  re="$("$CLUTCH" -C "$RE" --ok-cold -v)"
  st=$?
  set -e
  echo "$re"
  echo "  (exit $st)"
  assert_grep "relico ragged clutch" "RAGGED" "$re"
  assert_grep "relico rust oracle" "oracles_generated.rs" "$re"
  assert_no "relico no justfile orphan" "specs/、" "$re"
  assert_no "relico no wdio-logs" "wdio-logs" "$re"
fi
# tenaoshi/relico handled above with tighter assertions
dogfood kizu-locks "$KZ" --locks
dogfood sitbone "$SB" --locks
dogfood koyomi "$KO"
dogfood skills "$SK"

echo
echo "== results: $PASS passed, $FAIL failed =="
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
exit 0
