#!/usr/bin/env bash
# Exercise unseen on a synthetic lagging repo and fail if the primitive is dead.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
UNSEEN="$HERE/unseen"
REPO="$HERE/fixtures/lagrepo"

chmod +x "$UNSEEN" "$HERE/fixtures/mkrepo.sh"
"$HERE/fixtures/mkrepo.sh" "$REPO" >/dev/null

fail() {
  echo "demo FAIL: $*" >&2
  exit 1
}

echo "== unseen --version =="
ver="$("$UNSEEN" --version 2>/dev/null)"
echo "$ver"
echo "$ver" | grep -q . || fail "no version"

echo "== unseen greet (human + diff) =="
out="$("$UNSEEN" --repo "$REPO" --diff greet)"
echo "$out"
echo "$out" | grep -q '^greet$' || fail "expected symbol greet"
echo "$out" | grep -q 'src/app.py' || fail "app.py should have slept"
echo "$out" | grep -q 'tests/test_greet.py' || fail "tests should have slept"
echo "$out" | grep -q 'docs/api.md' || fail "docs should have slept"
echo "$out" | grep -q 'prefix' || fail "diff should show prefix parameter"
echo "$out" | grep -q 'hello' || fail "diff should show hi -> hello"
# cli.py was added after the excited-flag change; it should still sleep through prefix
echo "$out" | grep -q 'src/cli.py' || fail "cli.py should have slept through prefix"

echo "== unseen greet (tsv) =="
tsv="$("$UNSEEN" --repo "$REPO" --format tsv greet)"
echo "$tsv"
echo "$tsv" | grep -q '^name	' || fail "tsv header"
echo "$tsv" | awk -F'\t' 'NR>1 && $1=="greet" && $9=="src/app.py" {found=1} END{exit !found}' \
  || fail "tsv missing app.py row"
echo "$tsv" | awk -F'\t' 'NR>1 && $1=="greet" && $3=="1" {found=1} END{exit !found}' \
  || fail "greet signature should have changed"

echo "== unseen greet (json) =="
json="$("$UNSEEN" --repo "$REPO" --format json greet)"
python3 - "$json" << 'PY'
import json, sys
data = json.loads(sys.argv[1])
assert data, "empty json"
names = {c["name"] for c in data}
assert "greet" in names
refs = [r["path"] for c in data if c["name"]=="greet" for r in c["refs"]]
for need in ("src/app.py", "tests/test_greet.py", "docs/api.md"):
    assert need in refs, need
assert any(c.get("diff") for c in data), "json missing diff"
print("json ok", len(data), "cohorts")
PY

echo "== weird filename + unicode =="
out="$("$UNSEEN" --repo "$REPO" --diff odd_fn zenkaku_add)"
echo "$out"
echo "$out" | grep -q 'odd_fn' || fail "odd_fn missing"
echo "$out" | grep -q 'weird name (1).py' || fail "weird filename missing"
echo "$out" | grep -q 'zenkaku_add' || fail "zenkaku_add missing"
echo "$out" | grep -q 'use_zenkaku.py' || fail "unicode caller missing"

echo "== --at pin =="
# app.py: the greet("world") line should report greet
at_out="$("$UNSEEN" --repo "$REPO" --format tsv src/app.py:5)"
echo "$at_out"
echo "$at_out" | grep -q 'greet' || fail "--at did not find greet"

echo "== --check exit code =="
set +e
"$UNSEEN" --repo "$REPO" --check greet >/dev/null
code=$?
set -e
[ "$code" -eq 1 ] || fail "--check should exit 1, got $code"

echo "== nested git does not crash =="
"$UNSEEN" --repo "$REPO" --format tsv --limit 5 >/dev/null || fail "parent scan crashed"

echo "== unscoped ranking prefers signature diffs =="
rank="$("$UNSEEN" --repo "$REPO" --limit 8)"
echo "$rank"
echo "$rank" | grep -q 'changed  sig' || fail "expected sig marker"
echo "$rank" | grep -q 'greet' || fail "unscoped should still surface greet"
if echo "$rank" | grep -q missing-then; then
  fail "unscoped leaked ghosts"
fi

echo "== --sig =="
sig="$("$UNSEEN" --repo "$REPO" --sig --format tsv greet)"
echo "$sig"
echo "$sig" | awk -F'\t' 'NR>1 && $1=="greet" && $3=="1" {found=1} END{exit !found}' \
  || fail "--sig dropped greet"

echo "== rust_greet cross-language =="
out="$("$UNSEEN" --repo "$REPO" --diff rust_greet)"
echo "$out"
echo "$out" | grep -q 'rust_greet' || fail "rust_greet missing"
echo "$out" | grep -q 'excited' || fail "rust diff missing excited"

echo
echo "demo OK"
