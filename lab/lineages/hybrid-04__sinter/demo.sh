#!/usr/bin/env bash
# Exercise sinter: fuse testimony + recipe, assay RAGGED/STALE/CLEAN.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SINTER="$ROOT/sinter"
chmod +x "$SINTER"

PASS=0
FAIL=0

ok() { PASS=$((PASS + 1)); echo "  ok  $1"; }
bad() { FAIL=$((FAIL + 1)); echo "  FAIL $1" >&2; echo "       $2" >&2; }

assert_grep() {
  local name="$1" needle="$2" hay="$3"
  if grep -F -q -- "$needle" <<<"$hay"; then
    ok "$name"
  else
    bad "$name" "missing '$needle' in: ${hay:0:400}"
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
if python3 "$SINTER" --selftest; then
  ok "selftest"
else
  bad "selftest" "sinter --selftest failed"
fi

echo "== help =="
if python3 "$SINTER" --help | grep -q 'RAGGED'; then
  ok "help names RAGGED"
else
  bad "help names RAGGED" "missing primitive in --help"
fi

echo "== fixture =="
FIX="$(mktemp -d "${TMPDIR:-/tmp}/sinter-demo.XXXXXX")"
cleanup() { rm -rf "$FIX"; }
trap cleanup EXIT
python3 "$SINTER" --write-fixture "$FIX/repo" >/dev/null
FIXREPO="$FIX/repo"

out="$(python3 "$SINTER" -C "$FIXREPO" -v || true)"
assert_grep "fixture ragged firing" "RAGGED" "$out"
assert_grep "fixture content why" "why=content" "$out"
assert_grep "fixture cites root.pkl" "specs/root.pkl" "$out"
assert_grep "fixture recipe-only json" "EPC-001.json" "$out"
assert_grep "fixture via recipe" "via=recipe" "$out"
assert_grep "fixture unicode" "計画.md" "$out"
assert_grep "fixture stale sibling b.md" "out/b.md" "$out"
assert_no "fixture no justfile parent" "specs/、" "$out"
assert_no "fixture no cargo.lock" "Cargo.lock" "$out"

why="$(python3 "$SINTER" -C "$FIXREPO" why out/b.md || true)"
assert_grep "why names firing" "specs/root.pkl" "$why"
assert_grep "why names sibling a.md" "out/a.md" "$why"

tsv="$(python3 "$SINTER" -C "$FIXREPO" --tsv || true)"
assert_grep "tsv header" "firing_verdict" "$tsv"
assert_grep "tsv recipe member" "extra/EPC-001.json" "$tsv"

jsfile="$FIX/out.json"
python3 "$SINTER" -C "$FIXREPO" --json >"$jsfile" || true
python3 - "$jsfile" <<'PY'
import json, sys
data = json.load(open(sys.argv[1]))
assert data["firings"], "no firings"
parents = {c["id"] for c in data["firings"]}
assert any("root.pkl" in p for p in parents), parents
print("json-firings", len(data["firings"]),
      "members", sum(len(f["members"]) for f in data["firings"]))
PY
ok "json parse"

GHQ="${GHQ:-$HOME/ghq/github.com/annenpolka}"
VT="$GHQ/voidtrace"
TE="$GHQ/tenaoshi"
RE="$GHQ/relico"
KZ="$GHQ/kizu"
SB="$GHQ/sitbone"

if [[ -d "$RE/.git" ]]; then
  echo "== dogfood relico =="
  set +e
  re="$(python3 "$SINTER" -C "$RE" -v)"
  st=$?
  set -e
  echo "$re" | head -80
  echo "  (exit $st)"
  assert_grep "relico parent" "specs/notifier.pkl" "$re"
  assert_grep "relico ragged or stale" "RAGGED" "$re"
  assert_grep "relico unit oracle" "oracles_generated.test.ts" "$re"
  assert_grep "relico rust oracle" "oracles_generated.rs" "$re"
  assert_grep "relico patterns import or reason" "patterns.pkl" "$re"
  assert_no "relico no justfile comma parent" "specs/、" "$re"
  assert_no "relico no wdio-logs" "wdio-logs" "$re"
  whyre="$(python3 "$SINTER" -C "$RE" why tests/unit/oracles_generated.test.ts || true)"
  echo "$whyre" | head -40
  assert_grep "relico why content" "content" "$whyre"
fi

if [[ -d "$TE/.git" ]]; then
  echo "== dogfood tenaoshi =="
  set +e
  te="$(python3 "$SINTER" -C "$TE" -v)"
  st=$?
  set -e
  echo "$te" | head -80
  echo "  (exit $st)"
  assert_grep "tenaoshi parent" "specs/tenaoshi.pkl" "$te"
  assert_grep "tenaoshi oracles" "OraclesGenerated.swift" "$te"
  assert_grep "tenaoshi recipe json" "contracts/testcases/" "$te"
  assert_no "tenaoshi no jp-comma parent" "specs/、" "$te"
  assert_no "tenaoshi no AGENTS glob" "specs/*.pkl" "$te"
  if echo "$te" | grep -E '^  (STALE|CLEAN) .+tools/spec-gen\.ts'; then
    bad "tenaoshi no spec-gen member" "spec-gen.ts listed as a generated member"
  else
    ok "tenaoshi no spec-gen member"
  fi
fi

if [[ -d "$VT/.git" ]]; then
  echo "== dogfood voidtrace =="
  set +e
  vt="$(python3 "$SINTER" -C "$VT" -v)"
  st=$?
  set -e
  echo "$vt" | head -80
  echo "  (exit $st)"
  assert_grep "voidtrace parent" "specs/main.pkl" "$vt"
  assert_grep "voidtrace AI_UX" "AI_UX.md" "$vt"
  assert_grep "voidtrace SPEC" "SPEC.md" "$vt"
  assert_grep "voidtrace stamp-join or capabilities" "capabilities.generated.json" "$vt"
  assert_no "voidtrace no pnpm-store" ".pnpm-store" "$vt"
  if echo "$vt" | grep -E '^  (STALE|CLEAN) .+tools/spec-gen/src/render\.ts'; then
    bad "voidtrace no render.ts artifact" "render.ts listed as a generated member"
  else
    ok "voidtrace no render.ts artifact"
  fi
fi

if [[ -d "$KZ/.git" ]]; then
  echo "== dogfood kizu (negative) =="
  set +e
  kz="$(python3 "$SINTER" -C "$KZ")"
  set -e
  echo "$kz" | head -20
  ok "kizu ran"
fi

if [[ -d "$SB/.git" ]]; then
  echo "== dogfood sitbone (negative) =="
  set +e
  sb="$(python3 "$SINTER" -C "$SB")"
  set -e
  echo "$sb" | head -20
  ok "sitbone ran"
fi

echo
echo "== results: $PASS passed, $FAIL failed =="
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
exit 0
