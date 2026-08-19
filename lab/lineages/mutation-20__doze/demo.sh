#!/usr/bin/env bash
# Exercise doze on a synthetic lagging repo and fail if the primitive is dead.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DOZE="$HERE/doze"
REPO="$HERE/fixtures/lagrepo"

chmod +x "$DOZE" "$HERE/fixtures/mkrepo.sh"
"$HERE/fixtures/mkrepo.sh" "$REPO" >/dev/null

fail() {
  echo "demo FAIL: $*" >&2
  exit 1
}

echo "== doze --version =="
ver="$("$DOZE" --version 2>/dev/null)"
echo "$ver"
echo "$ver" | grep -q . || fail "no version"

echo "== doze greet (human + last-saw/HEAD signatures) =="
out="$("$DOZE" --repo "$REPO" greet)"
echo "$out"
echo "$out" | grep -q '^greet$' || fail "expected symbol greet"
echo "$out" | grep -q 'src/app.py' || fail "app.py should have slept"
echo "$out" | grep -q 'tests/test_greet.py' || fail "tests should have slept"
echo "$out" | grep -q 'docs/api.md' || fail "docs should have slept"
echo "$out" | grep -q 'last-saw' || fail "should print last-saw signature"
echo "$out" | grep -q 'HEAD' || fail "should print HEAD signature"
echo "$out" | grep -q 'prefix' || fail "HEAD signature should show prefix"
# cli.py was added after the excited-flag change; it should still sleep through prefix
echo "$out" | grep -q 'src/cli.py' || fail "cli.py should have slept through prefix"

echo "== default hides body-only trim =="
scoped="$("$DOZE" --repo "$REPO" --limit 20)"
echo "$scoped"
echo "$scoped" | grep -q '^greet$' || fail "unscoped should still surface greet"
if echo "$scoped" | grep -q '^trim$'; then
  fail "body-only trim leaked into default signature-only output"
fi
if echo "$scoped" | grep -q missing-then; then
  fail "unscoped leaked ghosts"
fi

echo "== --body surfaces trim =="
body="$("$DOZE" --repo "$REPO" --body trim)"
echo "$body"
echo "$body" | grep -q '^trim$' || fail "--body should show trim"
echo "$body" | grep -q 'src/app.py' || fail "trim caller should have slept"

echo "== doze greet (tsv) =="
tsv="$("$DOZE" --repo "$REPO" --format tsv greet)"
echo "$tsv"
echo "$tsv" | grep -q '^name	' || fail "tsv header"
echo "$tsv" | awk -F'\t' 'NR>1 && $1=="greet" && $9=="src/app.py" {found=1} END{exit !found}' \
  || fail "tsv missing app.py row"
echo "$tsv" | awk -F'\t' 'NR>1 && $1=="greet" && $3=="1" {found=1} END{exit !found}' \
  || fail "greet signature should have changed"
echo "$tsv" | awk -F'\t' 'NR>1 && $1=="greet" && $15 ~ /prefix/ {found=1} END{exit !found}' \
  || fail "tsv new_sig should include prefix"

echo "== doze greet (json) =="
json="$("$DOZE" --repo "$REPO" --format json greet)"
python3 - "$json" << 'PY'
import json, sys
data = json.loads(sys.argv[1])
assert data, "empty json"
names = {c["name"] for c in data}
assert "greet" in names
refs = [r["path"] for c in data if c["name"]=="greet" for r in c["refs"]]
for need in ("src/app.py", "tests/test_greet.py", "docs/api.md"):
    assert need in refs, need
assert any(c.get("sig_changed") for c in data), "json missing sig_changed"
assert any("prefix" in (c.get("new_sig") or "") for c in data), "json missing new_sig"
print("json ok", len(data), "cohorts")
PY

echo "== weird filename + unicode =="
out="$("$DOZE" --repo "$REPO" odd_fn zenkaku_add)"
echo "$out"
echo "$out" | grep -q 'odd_fn' || fail "odd_fn missing"
echo "$out" | grep -q 'weird name (1).py' || fail "weird filename missing"
echo "$out" | grep -q 'zenkaku_add' || fail "zenkaku_add missing"
echo "$out" | grep -q 'use_zenkaku.py' || fail "unicode caller missing"

echo "== --at pin =="
at_out="$("$DOZE" --repo "$REPO" --format tsv src/app.py:5)"
echo "$at_out"
echo "$at_out" | grep -q 'greet' || fail "--at did not find greet"

echo "== --check exit 1 on signature lag =="
set +e
check_out="$("$DOZE" --repo "$REPO" --check greet 2>&1)"
code=$?
set -e
echo "$check_out"
[ "$code" -eq 1 ] || fail "--check greet should exit 1, got $code"
echo "$check_out" | grep -q 'src/app.py:' || fail "--check should name sleeping use-sites"
echo "$check_out" | grep -q 'last-saw' || fail "--check should print last-saw"
echo "$check_out" | grep -q 'HEAD' || fail "--check should print HEAD"

echo "== --check exit 0 on body-only =="
set +e
"$DOZE" --repo "$REPO" --check trim >/dev/null
code=$?
set -e
[ "$code" -eq 0 ] || fail "--check trim should exit 0 (signature unchanged), got $code"

echo "== --check --body still ignores body-only (CI is signatures) =="
set +e
"$DOZE" --repo "$REPO" --check --body trim >/dev/null
code=$?
set -e
[ "$code" -eq 0 ] || fail "--check --body trim should still exit 0, got $code"

echo "== nested git does not crash =="
"$DOZE" --repo "$REPO" --format tsv --limit 5 >/dev/null || fail "parent scan crashed"

echo "== rust_greet cross-language =="
out="$("$DOZE" --repo "$REPO" rust_greet)"
echo "$out"
echo "$out" | grep -q 'rust_greet' || fail "rust_greet missing"
echo "$out" | grep -q 'excited' || fail "rust signature missing excited"
echo "$out" | grep -q 'HEAD      pub fn rust_greet(name: &str, excited: bool) -> String' \
  || fail "collapsed HEAD signature should be one line"

echo
echo "demo OK"
