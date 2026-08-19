#!/usr/bin/env bash
# Exercise clink on a synthetic lagging repo and fail if the primitive is dead.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
CLINK="$HERE/clink"
REPO="$HERE/fixtures/lagrepo"

chmod +x "$CLINK" "$HERE/fixtures/mkrepo.sh"
"$HERE/fixtures/mkrepo.sh" "$REPO" >/dev/null

fail() {
  echo "demo FAIL: $*" >&2
  exit 1
}

echo "== clink --version =="
ver="$("$CLINK" --version 2>/dev/null)"
echo "$ver"
echo "$ver" | grep -q . || fail "no version"

echo "== clink greet (compiled callers; last-saw/HEAD signatures) =="
out="$("$CLINK" --repo "$REPO" greet)"
echo "$out"
echo "$out" | grep -q '^greet$' || fail "expected symbol greet"
echo "$out" | grep -q 'src/app.py' || fail "app.py should have slept"
echo "$out" | grep -q 'tests/test_greet.py' || fail "tests should have slept"
if echo "$out" | grep -q 'src/app.py:2'; then
  fail "comment mention treated as compiled caller"
fi
echo "$out" | grep -q 'last-saw' || fail "should print last-saw signature"
echo "$out" | grep -q 'HEAD' || fail "should print HEAD signature"
echo "$out" | grep -q 'prefix' || fail "HEAD signature should show prefix"
echo "$out" | grep -q 'compiled caller' || fail "default unit is compiled callers"
# cli.py was added after the excited-flag change; it should still sleep through prefix
echo "$out" | grep -q 'src/cli.py' || fail "cli.py should have slept through prefix"
if echo "$out" | grep -q 'docs/api.md'; then
  fail "docs/api.md leaked into default compiled-caller output"
fi
if echo "$out" | grep -q 'plans/v0.md'; then
  fail "plans/v0.md leaked into default compiled-caller output"
fi

echo "== --docs includes plan/markdown mentions =="
docs="$("$CLINK" --repo "$REPO" --docs greet)"
echo "$docs"
echo "$docs" | grep -q 'docs/api.md' || fail "--docs should show docs/api.md"
echo "$docs" | grep -q 'plans/v0.md' || fail "--docs should show plans/v0.md"
echo "$docs" | grep -q 'src/app.py' || fail "--docs should still show compiled callers"
echo "$docs" | grep -q 'use-site' || fail "--docs unit is use-sites"

echo "== default hides body-only trim =="
scoped="$("$CLINK" --repo "$REPO" --limit 20)"
echo "$scoped"
echo "$scoped" | grep -q '^greet$' || fail "unscoped should still surface greet"
if echo "$scoped" | grep -q '^trim$'; then
  fail "body-only trim leaked into default signature-only output"
fi
if echo "$scoped" | grep -q missing-then; then
  fail "unscoped leaked ghosts"
fi
if echo "$scoped" | grep -q 'docs/api.md'; then
  fail "unscoped leaked docs"
fi

echo "== --body surfaces trim =="
body="$("$CLINK" --repo "$REPO" --body trim)"
echo "$body"
echo "$body" | grep -q '^trim$' || fail "--body should show trim"
echo "$body" | grep -q 'src/app.py' || fail "trim caller should have slept"

echo "== clink greet (tsv) =="
tsv="$("$CLINK" --repo "$REPO" --format tsv greet)"
echo "$tsv"
echo "$tsv" | grep -q '^name	' || fail "tsv header"
echo "$tsv" | awk -F'\t' 'NR>1 && $1=="greet" && $9=="src/app.py" {found=1} END{exit !found}' \
  || fail "tsv missing app.py row"
echo "$tsv" | awk -F'\t' 'NR>1 && $1=="greet" && $3=="1" {found=1} END{exit !found}' \
  || fail "greet signature should have changed"
echo "$tsv" | awk -F'\t' 'NR>1 && $1=="greet" && $15 ~ /prefix/ {found=1} END{exit !found}' \
  || fail "tsv new_sig should include prefix"
echo "$tsv" | awk -F'\t' 'NR>1 && $9=="docs/api.md" {found=1} END{exit found}' \
  || fail "tsv default leaked docs/api.md"
echo "$tsv" | awk -F'\t' 'NR>1 && $9=="plans/v0.md" {found=1} END{exit found}' \
  || fail "tsv default leaked plans/v0.md"
echo "$tsv" | awk -F'\t' 'NR>1 && $9=="src/app.py" && $10=="2" {found=1} END{exit found}' \
  || fail "tsv listed comment line as compiled caller"

echo "== clink greet --docs (tsv) =="
tsv_docs="$("$CLINK" --repo "$REPO" --docs --format tsv greet)"
echo "$tsv_docs" | awk -F'\t' 'NR>1 && $9=="docs/api.md" {found=1} END{exit !found}' \
  || fail "tsv --docs missing docs/api.md"
echo "$tsv_docs" | awk -F'\t' 'NR>1 && $9=="plans/v0.md" {found=1} END{exit !found}' \
  || fail "tsv --docs missing plans/v0.md"

echo "== clink greet (json) =="
json="$("$CLINK" --repo "$REPO" --format json greet)"
python3 - "$json" << 'PY'
import json, sys
data = json.loads(sys.argv[1])
assert data, "empty json"
names = {c["name"] for c in data}
assert "greet" in names
refs = [r["path"] for c in data if c["name"]=="greet" for r in c["refs"]]
for need in ("src/app.py", "tests/test_greet.py"):
    assert need in refs, need
assert "docs/api.md" not in refs, "json default leaked docs"
assert "plans/v0.md" not in refs, "json default leaked plans"
assert any(c.get("sig_changed") for c in data), "json missing sig_changed"
assert any("prefix" in (c.get("new_sig") or "") for c in data), "json missing new_sig"
print("json ok", len(data), "cohorts")
PY

echo "== clink greet --docs (json) =="
json_docs="$("$CLINK" --repo "$REPO" --docs --format json greet)"
python3 - "$json_docs" << 'PY'
import json, sys
data = json.loads(sys.argv[1])
refs = [r["path"] for c in data if c["name"]=="greet" for r in c["refs"]]
for need in ("src/app.py", "docs/api.md", "plans/v0.md"):
    assert need in refs, need
print("json --docs ok")
PY

echo "== weird filename + unicode =="
out="$("$CLINK" --repo "$REPO" odd_fn zenkaku_add)"
echo "$out"
echo "$out" | grep -q 'odd_fn' || fail "odd_fn missing"
echo "$out" | grep -q 'weird name (1).py' || fail "weird filename missing"
echo "$out" | grep -q 'zenkaku_add' || fail "zenkaku_add missing"
echo "$out" | grep -q 'use_zenkaku.py' || fail "unicode caller missing"

echo "== --at pin =="
at_out="$("$CLINK" --repo "$REPO" --format tsv src/app.py:6)"
echo "$at_out"
echo "$at_out" | grep -q 'greet' || fail "--at did not find greet"

echo "== --check exit 1 on signature lag (compiled callers only) =="
set +e
check_out="$("$CLINK" --repo "$REPO" --check greet 2>&1)"
code=$?
set -e
echo "$check_out"
[ "$code" -eq 1 ] || fail "--check greet should exit 1, got $code"
echo "$check_out" | grep -q 'src/app.py:' || fail "--check should name sleeping compiled callers"
echo "$check_out" | grep -q 'last-saw' || fail "--check should print last-saw"
echo "$check_out" | grep -q 'HEAD' || fail "--check should print HEAD"
if echo "$check_out" | grep -q 'docs/api.md'; then
  fail "--check should not name docs without --docs"
fi
if echo "$check_out" | grep -q 'plans/v0.md'; then
  fail "--check should not name plans without --docs"
fi
echo "$check_out" | grep -q 'compiled caller' || fail "--check default unit is compiled callers"

echo "== --check --docs names markdown =="
set +e
check_docs="$("$CLINK" --repo "$REPO" --check --docs greet 2>&1)"
code=$?
set -e
echo "$check_docs"
[ "$code" -eq 1 ] || fail "--check --docs greet should exit 1, got $code"
echo "$check_docs" | grep -q 'docs/api.md:' || fail "--check --docs should name docs"
echo "$check_docs" | grep -q 'plans/v0.md:' || fail "--check --docs should name plans"

echo "== --check exit 0 on body-only =="
set +e
"$CLINK" --repo "$REPO" --check trim >/dev/null
code=$?
set -e
[ "$code" -eq 0 ] || fail "--check trim should exit 0 (signature unchanged), got $code"

echo "== --check --body still ignores body-only (CI is signatures) =="
set +e
"$CLINK" --repo "$REPO" --check --body trim >/dev/null
code=$?
set -e
[ "$code" -eq 0 ] || fail "--check --body trim should still exit 0, got $code"

echo "== nested git does not crash =="
"$CLINK" --repo "$REPO" --format tsv --limit 5 >/dev/null || fail "parent scan crashed"

echo "== rust_greet cross-language =="
out="$("$CLINK" --repo "$REPO" rust_greet)"
echo "$out"
echo "$out" | grep -q 'rust_greet' || fail "rust_greet missing"
echo "$out" | grep -q 'excited' || fail "rust signature missing excited"
echo "$out" | grep -q 'HEAD      pub fn rust_greet(name: &str, excited: bool) -> String' \
  || fail "collapsed HEAD signature should be one line"

echo
echo "demo OK"
