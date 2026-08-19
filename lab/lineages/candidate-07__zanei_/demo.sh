#!/usr/bin/env bash
# Exercise zanei on synthetic fixtures and fail if the primitive is broken.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
ZANEI="$ROOT/zanei"
RUN="$ROOT/fixtures/.run"
rm -rf "$RUN"
mkdir -p "$RUN"

pass=0
fail=0
assert_contains() {
  local haystack="$1"
  local needle="$2"
  local label="$3"
  if grep -Fq -- "$needle" <<<"$haystack"; then
    echo "  ok  $label"
    pass=$((pass + 1))
  else
    echo "  FAIL $label"
    echo "    missing: $needle"
    echo "    --- output ---"
    echo "$haystack" | sed 's/^/    /'
    fail=$((fail + 1))
  fi
}

assert_exit() {
  local got="$1"
  local want="$2"
  local label="$3"
  if [[ "$got" == "$want" ]]; then
    echo "  ok  $label (exit $got)"
    pass=$((pass + 1))
  else
    echo "  FAIL $label (exit $got, want $want)"
    fail=$((fail + 1))
  fi
}

echo "== self-test =="
set +e
"$ZANEI" self-test
st=$?
set -e
assert_exit "$st" 0 "embedded parser/scorer tests"

echo
echo "== toy working-tree afterimages =="
TOY="$RUN/toy"
mkdir -p "$TOY/src" "$TOY/tests" "$TOY/docs"
cp "$ROOT/fixtures/toy/src/retry.py" "$TOY/src/"
cp "$ROOT/fixtures/toy/README.md" "$TOY/"
cp "$ROOT/fixtures/toy/tests/test_retry.py" "$TOY/tests/"
cp "$ROOT/fixtures/toy/docs/help.txt" "$TOY/docs/"
cp "$ROOT/fixtures/toy/plugin.json" "$TOY/"
git -C "$TOY" init -q
git -C "$TOY" config user.email "zanei@example.test"
git -C "$TOY" config user.name "zanei"
git -C "$TOY" add .
git -C "$TOY" commit -qm "initial facts: retries=3 timeout=10 cache=true version=0.3.0"

# Mutate implementation; leave docs/tests/plugin claiming the old facts.
python3 - <<'PY' "$TOY/src/retry.py" "$TOY/plugin.json"
from pathlib import Path
import sys
retry = Path(sys.argv[1])
text = retry.read_text()
text = text.replace("MAX_RETRIES = 3", "MAX_ATTEMPTS = 8")
text = text.replace("retries=MAX_RETRIES", "retries=MAX_ATTEMPTS")
text = text.replace("HOOK_TIMEOUT = 10", "HOOK_TIMEOUT = 30")
text = text.replace("ENABLE_CACHE = True", "ENABLE_CACHE = False")
# keep the comments stale on purpose
retry.write_text(text)
plugin = Path(sys.argv[2])
plugin.write_text(plugin.read_text().replace('"version": "0.3.0"', '"version": "0.7.0"'))
# leave hooks.timeout: 10 stale
PY

set +e
OUT="$("$ZANEI" --no-color --explain -C "$TOY" 2>&1)"
st=$?
set -e
assert_exit "$st" 1 "findings yield exit 1"
assert_contains "$OUT" "MAX_RETRIES" "rename leftover name"
assert_contains "$OUT" "3" "old retry count"
assert_contains "$OUT" "timeout" "timeout fact"
assert_contains "$OUT" "ENABLE_CACHE" "polarity leftover"
assert_contains "$OUT" "README.md" "docs afterimage"
assert_contains "$OUT" "test_retry.py" "test afterimage"
assert_contains "$OUT" "help.txt" "cli help afterimage"
assert_contains "$OUT" "plugin.json" "config afterimage"

echo
echo "== --facts-only / --tsv / clean tree =="
set +e
FACTS="$("$ZANEI" --facts-only --no-color -C "$TOY" 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "facts-only exits 0"
assert_contains "$FACTS" "rename" "facts-only reports rename"

set +e
TSV="$("$ZANEI" --tsv --no-color -C "$TOY" 2>&1)"
st=$?
set -e
assert_contains "$TSV" $'score\tclaim\tpath' "TSV header"

# Commit the mutations: destination tree matches the diff, leftovers remain.
git -C "$TOY" add src/retry.py plugin.json
git -C "$TOY" commit -qm "change facts, forget the claims"
set +e
RANGE="$("$ZANEI" --no-color -C "$TOY" HEAD~1 HEAD 2>&1)"
st=$?
set -e
assert_exit "$st" 1 "range HEAD~1 HEAD still sees leftover claims"
assert_contains "$RANGE" "MAX_RETRIES" "range finds old ident in tests"

# Empty working tree after commit: default zanei vs HEAD should be clean.
set +e
CLEAN="$("$ZANEI" --no-color -C "$TOY" 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "clean worktree vs HEAD is empty"
assert_contains "$CLEAN" "no fact mutations" "clean-tree message"

echo
echo "== ugly filenames + nested git =="
UGLY="$RUN/ugly"
mkdir -p "$UGLY/src" "$UGLY/nested" "$UGLY/generated" "$UGLY/emoji"
cp "$ROOT/fixtures/ugly/README.md" "$UGLY/"
cp "$ROOT/fixtures/ugly/file with spaces.md" "$UGLY/"
cp "$ROOT/fixtures/ugly/日本語コメント.md" "$UGLY/"
cp "$ROOT/fixtures/ugly/generated/vendor_bundle.js" "$UGLY/generated/"
printf 'MAX_RETRIES = 3\nTIMEOUT = 10\n' > "$UGLY/src/config.py"
printf 'still claims MAX_RETRIES\n' > "$UGLY/emoji/🌀 leftover.md"
# nested repo that parent git will not track
mkdir -p "$UGLY/nested/inner"
printf '# nested still says timeout is 10\n' > "$UGLY/nested/inner/note.md"
git -C "$UGLY/nested" init -q
git -C "$UGLY/nested" config user.email "zanei@example.test"
git -C "$UGLY/nested" config user.name "zanei"
git -C "$UGLY/nested" add .
git -C "$UGLY/nested" commit -qm "nested"

git -C "$UGLY" init -q
git -C "$UGLY" config user.email "zanei@example.test"
git -C "$UGLY" config user.name "zanei"
# generated/ should be searchable unless ignored — leave it tracked
git -C "$UGLY" add .
git -C "$UGLY" commit -qm "ugly baseline"
printf 'MAX_ATTEMPTS = 8\nTIMEOUT = 30\n' > "$UGLY/src/config.py"

set +e
UGLY_OUT="$("$ZANEI" --no-color -C "$UGLY" 2>&1)"
st=$?
set -e
assert_exit "$st" 1 "ugly tree finds leftovers"
assert_contains "$UGLY_OUT" "file with spaces.md" "space in filename"
assert_contains "$UGLY_OUT" "日本語コメント.md" "unicode filename"
assert_contains "$UGLY_OUT" "🌀 leftover.md" "emoji filename"
assert_contains "$UGLY_OUT" "nested/inner/note.md" "nested git file visible"

echo
echo "== stdin diff against fixture tree =="
DIFF="$RUN/change.diff"
cat > "$DIFF" <<'EOF'
diff --git a/src/config.py b/src/config.py
--- a/src/config.py
+++ b/src/config.py
@@ -1,2 +1,2 @@
-MAX_RETRIES = 3
-TIMEOUT = 10
+MAX_ATTEMPTS = 8
+TIMEOUT = 30
EOF
set +e
STDIN_OUT="$(cat "$DIFF" | "$ZANEI" --no-color --diff - -C "$UGLY" 2>&1)"
st=$?
set -e
assert_exit "$st" 1 "stdin diff yields findings"
assert_contains "$STDIN_OUT" "TIMEOUT" "stdin-bound timeout fact"

echo
echo "passed=$pass failed=$fail"
if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
exit 0
