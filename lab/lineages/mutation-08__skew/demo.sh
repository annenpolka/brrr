#!/usr/bin/env bash
# Exercise skew on a synthetic lagging repo and fail if the primitive is dead.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SKEW="$HERE/skew"
REPO="$HERE/fixtures/lagrepo"

chmod +x "$SKEW" "$HERE/fixtures/mkrepo.sh"
"$HERE/fixtures/mkrepo.sh" "$REPO" >/dev/null

fail() {
  echo "demo FAIL: $*" >&2
  exit 1
}

echo "== skew --version =="
ver="$("$SKEW" --version 2>/dev/null)"
echo "$ver"
echo "$ver" | grep -q . || fail "no version"

echo "== skew greet (human + diff) =="
out="$("$SKEW" --repo "$REPO" --diff greet)"
echo "$out"
echo "$out" | grep -q '^greet$' || fail "expected symbol greet"
echo "$out" | grep -q 'src/app.py' || fail "app.py should have slept"
echo "$out" | grep -q 'tests/test_greet.py' || fail "tests should have slept"
echo "$out" | grep -q 'docs/api.md' || fail "docs should have slept"
echo "$out" | grep -q 'prefix' || fail "diff should show prefix parameter"
echo "$out" | grep -q 'hello' || fail "diff should show hi -> hello"
# cli.py was added after the excited-flag change; it should still sleep through prefix
echo "$out" | grep -q 'src/cli.py' || fail "cli.py should have slept through prefix"
# file clock of fresh.py matches greet.py — must not lag while committed
if echo "$out" | grep -q 'src/fresh.py'; then
  fail "fresh.py shares greet.py's file clock; should not lag"
fi
# same-file shout must not appear as a skewed caller (def line mentions the path)
if echo "$out" | grep -E '^    src/greet\.py' >/dev/null; then
  fail "same-file greet.py must not skew against itself"
fi
# unit is files, not blamed lines
echo "$out" | grep -q 'file' || fail "expected file-unit wording"
# clock kind is commit, not blame
echo "$out" | grep -q ' commit ' || fail "expected commit clock"

echo "== one row per caller file (not per line) =="
# app.py mentions greet twice; file clock collapses them
app_lines="$(echo "$out" | grep -c 'src/app.py' || true)"
[ "$app_lines" -eq 1 ] || fail "app.py should appear once, got $app_lines"

echo "== skew greet (tsv) =="
tsv="$("$SKEW" --repo "$REPO" --format tsv greet)"
echo "$tsv"
echo "$tsv" | grep -q '^name	' || fail "tsv header"
echo "$tsv" | awk -F'\t' 'NR>1 && $1=="greet" && $10=="src/app.py" {found=1} END{exit !found}' \
  || fail "tsv missing app.py row"
echo "$tsv" | awk -F'\t' 'NR>1 && $1=="greet" && $3=="1" {found=1} END{exit !found}' \
  || fail "greet signature should have changed"
echo "$tsv" | awk -F'\t' 'NR>1 && $8=="commit" {found=1} END{exit !found}' \
  || fail "tsv should label commit clocks"

echo "== skew greet (json) =="
json="$("$SKEW" --repo "$REPO" --format json greet)"
python3 - "$json" << 'PY'
import json, sys
data = json.loads(sys.argv[1])
assert data, "empty json"
names = {c["name"] for c in data}
assert "greet" in names
refs = [r["path"] for c in data if c["name"]=="greet" for r in c["refs"]]
for need in ("src/app.py", "tests/test_greet.py", "docs/api.md"):
    assert need in refs, need
assert "src/fresh.py" not in refs, "fresh.py should not lag on committed clocks"
assert any(c.get("diff") for c in data), "json missing diff"
clocks = {c["def"]["clock"] for c in data}
assert "commit" in clocks
print("json ok", len(data), "cohorts")
PY

echo "== weird filename + unicode (cross-file) =="
out="$("$SKEW" --repo "$REPO" --diff odd_fn zenkaku_add)"
echo "$out"
echo "$out" | grep -q 'odd_fn' || fail "odd_fn missing"
echo "$out" | grep -q 'use_odd.py' || fail "cross-file odd_fn caller missing"
echo "$out" | grep -q 'weird name (1).py' || fail "weird filename missing from def"
echo "$out" | grep -q 'zenkaku_add' || fail "zenkaku_add missing"
echo "$out" | grep -q 'use_zenkaku.py' || fail "unicode caller missing"
echo "$out" | grep -q 'step' || fail "odd_fn diff should show step"

echo "== --at pin (file clock, line only selects tokens) =="
at_out="$("$SKEW" --repo "$REPO" --format tsv src/app.py:5)"
echo "$at_out"
echo "$at_out" | grep -q 'greet' || fail "--at did not find greet"

echo "== --check exit code =="
set +e
"$SKEW" --repo "$REPO" --check greet >/dev/null
code=$?
set -e
[ "$code" -eq 1 ] || fail "--check should exit 1, got $code"

echo "== nested git does not crash =="
"$SKEW" --repo "$REPO" --format tsv --limit 5 >/dev/null || fail "parent scan crashed"

echo "== unscoped ranking prefers signature diffs =="
rank="$("$SKEW" --repo "$REPO" --limit 8)"
echo "$rank"
echo "$rank" | grep -q 'changed  sig' || fail "expected sig marker"
echo "$rank" | grep -q 'greet' || fail "unscoped should still surface greet"
if echo "$rank" | grep -q missing-then; then
  fail "unscoped leaked ghosts"
fi

echo "== --sig =="
sig="$("$SKEW" --repo "$REPO" --sig --format tsv greet)"
echo "$sig"
echo "$sig" | awk -F'\t' 'NR>1 && $1=="greet" && $3=="1" {found=1} END{exit !found}' \
  || fail "--sig dropped greet"

echo "== rust_greet cross-file =="
out="$("$SKEW" --repo "$REPO" --diff rust_greet)"
echo "$out"
echo "$out" | grep -q 'rust_greet' || fail "rust_greet missing"
echo "$out" | grep -q 'use_rust.rs' || fail "use_rust.rs should lag"
echo "$out" | grep -q 'excited' || fail "rust diff missing excited"
if echo "$out" | grep -E '^    src/lib\.rs' >/dev/null; then
  fail "same-file lib.rs must not skew against itself"
fi

echo "== HEAD vs worktree: dirty callee mtime =="
# fresh.py matched greet.py's file clock while committed. Dirtied greet.py
# must make fresh.py lag, with an mtime/WORKTREE clock and the new prefix.
python3 - "$REPO" << 'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1]) / "src" / "greet.py"
text = p.read_text()
p.write_text(text.replace('prefix="hello"', 'prefix="hey"'))
PY
dirty="$("$SKEW" --repo "$REPO" --diff greet)"
echo "$dirty"
echo "$dirty" | grep -q 'src/fresh.py' || fail "fresh.py should lag behind dirty greet.py"
echo "$dirty" | grep -q 'mtime' || fail "dirty callee should use mtime clock"
echo "$dirty" | grep -q 'WORKTREE' || fail "dirty callee rev should be WORKTREE"
echo "$dirty" | grep -q 'hey' || fail "diff should show uncommitted prefix hey"

echo "== --dirty keeps only mtime callees =="
only_dirty="$("$SKEW" --repo "$REPO" --dirty --format tsv greet)"
echo "$only_dirty"
echo "$only_dirty" | awk -F'\t' 'NR>1 && $8=="mtime" {found=1} END{exit !found}' \
  || fail "--dirty should report mtime callee"
# rust_greet's file is clean; --dirty should hide it
set +e
"$SKEW" --repo "$REPO" --dirty --check rust_greet >/dev/null
code=$?
set -e
[ "$code" -eq 0 ] || fail "--dirty rust_greet should be clean, got $code"

echo "== same-session dirty-vs-dirty (lag 0d) is skipped =="
# cli.py was a committed sleeper. Make it dirty with an mtime *before*
# greet.py but the same calendar day — two buffers in one sitting.
python3 - "$REPO" << 'PY'
import os, sys
from pathlib import Path
repo = Path(sys.argv[1])
cli = repo / "src" / "cli.py"
greet = repo / "src" / "greet.py"
cli.write_text(cli.read_text() + "\n# session\n")
g = greet.stat().st_mtime
os.utime(cli, (g - 7200, g - 7200))
PY
pair="$("$SKEW" --repo "$REPO" --diff greet)"
echo "$pair"
if echo "$pair" | grep -E '^    src/cli\.py' >/dev/null; then
  fail "same-day dirty cli.py should not skew against dirty greet.py"
fi
echo "$pair" | grep -q 'src/fresh.py' || fail "committed fresh.py should still lag dirty greet.py"

echo "== unscoped ranks code callers (app.py) with greet =="
rank2="$("$SKEW" --repo "$REPO" --limit 8)"
echo "$rank2"
echo "$rank2" | grep -q 'src/app.py' || fail "code caller app.py should stay visible unscoped"

echo
echo "demo OK"
