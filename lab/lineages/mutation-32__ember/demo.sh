#!/usr/bin/env bash
# Exercise ember on synthetic fixtures and fail if the primitive is broken.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
EMBER="$ROOT/ember"
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

assert_not_contains() {
  local haystack="$1"
  local needle="$2"
  local label="$3"
  if grep -Fq -- "$needle" <<<"$haystack"; then
    echo "  FAIL $label"
    echo "    unexpectedly found: $needle"
    echo "    --- output ---"
    echo "$haystack" | sed 's/^/    /'
    fail=$((fail + 1))
  else
    echo "  ok  $label"
    pass=$((pass + 1))
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
"$EMBER" self-test
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
git -C "$TOY" config user.email "ember@example.test"
git -C "$TOY" config user.name "ember"
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
OUT="$("$EMBER" --no-color --explain -C "$TOY" 2>&1)"
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
FACTS="$("$EMBER" --facts-only --no-color -C "$TOY" 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "facts-only exits 0"
assert_contains "$FACTS" "rename" "facts-only reports rename"

set +e
TSV="$("$EMBER" --tsv --no-color -C "$TOY" 2>&1)"
st=$?
set -e
assert_contains "$TSV" $'score\tclaim\tpath' "TSV header"

# Commit the mutations: destination tree matches the diff, leftovers remain.
git -C "$TOY" add src/retry.py plugin.json
git -C "$TOY" commit -qm "change facts, forget the claims"
set +e
RANGE="$("$EMBER" --no-color -C "$TOY" HEAD~1 HEAD 2>&1)"
st=$?
set -e
assert_exit "$st" 1 "range HEAD~1 HEAD still sees leftover claims"
assert_contains "$RANGE" "MAX_RETRIES" "range finds old ident in tests"

# Empty working tree after commit: default ember vs HEAD should be clean.
set +e
CLEAN="$("$EMBER" --no-color -C "$TOY" 2>&1)"
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
git -C "$UGLY/nested" config user.email "ember@example.test"
git -C "$UGLY/nested" config user.name "ember"
git -C "$UGLY/nested" add .
git -C "$UGLY/nested" commit -qm "nested"

git -C "$UGLY" init -q
git -C "$UGLY" config user.email "ember@example.test"
git -C "$UGLY" config user.name "ember"
# generated/ should be searchable unless ignored — leave it tracked
git -C "$UGLY" add .
git -C "$UGLY" commit -qm "ugly baseline"
printf 'MAX_ATTEMPTS = 8\nTIMEOUT = 30\n' > "$UGLY/src/config.py"

set +e
UGLY_OUT="$("$EMBER" --no-color -C "$UGLY" 2>&1)"
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
STDIN_OUT="$(cat "$DIFF" | "$EMBER" --no-color --diff - -C "$UGLY" 2>&1)"
st=$?
set -e
assert_exit "$st" 1 "stdin diff yields findings"
assert_contains "$STDIN_OUT" "TIMEOUT" "stdin-bound timeout fact"

echo
echo "== destroyer JSON-only hunk (quoted key + prose leftover) =="
# zanei extracted 0 facts from this hunk. nagori extracted version 0.3.0
# then discarded the README leftover by truncating the bind to 0.3.
KIZU="$RUN/kizu-toy"
mkdir -p "$KIZU"
cat > "$KIZU/plugin.json" <<'EOF'
{
  "name": "toy",
  "version": "0.7.0",
  "hooks": {
    "timeout": 10
  }
}
EOF
cat > "$KIZU/README.md" <<'EOF'
plugin version 0.3.0, hook timeout 10 seconds.
EOF
cat > "$KIZU/docs-help.txt" <<'EOF'
--timeout N   default 10
EOF
git -C "$KIZU" init -q
git -C "$KIZU" config user.email "ember@example.test"
git -C "$KIZU" config user.name "ember"
git -C "$KIZU" add .
git -C "$KIZU" commit -qm "dest still claims 0.3.0 in prose"

JSONDIFF="$RUN/plugin.diff"
cat > "$JSONDIFF" <<'EOF'
diff --git a/plugin.json b/plugin.json
--- a/plugin.json
+++ b/plugin.json
@@ -1,6 +1,6 @@
 {
   "name": "toy",
-  "version": "0.3.0",
+  "version": "0.7.0",
   "hooks": {
     "timeout": 10
   }
 }
EOF

set +e
JSON_FACTS="$(cat "$JSONDIFF" | "$EMBER" --facts-only --no-color --diff - -C "$KIZU" 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "json facts-only exits 0"
assert_contains "$JSON_FACTS" "version" "json quoted key is a named fact"
assert_contains "$JSON_FACTS" "0.3.0" "json old version is the full token"
assert_not_contains "$JSON_FACTS" "0.3'" "json old version is not truncated to 0.3"

set +e
JSON_OUT="$(cat "$JSONDIFF" | "$EMBER" --no-color --explain --diff - -C "$KIZU" 2>&1)"
st=$?
set -e
assert_exit "$st" 1 "json hunk finds dest leftovers"
assert_contains "$JSON_OUT" "0.3.0" "leftover reports the full version"
assert_contains "$JSON_OUT" "plugin version 0.3.0" "prose leftover is not homonym-skipped"
assert_contains "$JSON_OUT" "README.md" "prose leftover path"
assert_not_contains "$JSON_OUT" "none left an afterimage" "must not pretend the leftover was gated"

echo
echo "== destroyer date-in-version (month 10 is not timeout 10) =="
DATES="$RUN/dates"
mkdir -p "$DATES/src" "$DATES/docs"
printf 'HOOK_TIMEOUT = 30\nMAX_RETRIES = 8\n' > "$DATES/src/config.py"
cat > "$DATES/CHANGELOG.md" <<'EOF'
## timeout
shipped 2024-10-01
EOF
cat > "$DATES/docs/dates.md" <<'EOF'
hook timeout default was documented the day we shipped, 2024-10-01.
retries=3 landed.
landed 2024-03-01.
EOF
git -C "$DATES" init -q
git -C "$DATES" config user.email "ember@example.test"
git -C "$DATES" config user.name "ember"
git -C "$DATES" add .
git -C "$DATES" commit -qm "dest with ISO dates"

DATE_DIFF="$RUN/timeout.diff"
cat > "$DATE_DIFF" <<'EOF'
diff --git a/src/config.py b/src/config.py
--- a/src/config.py
+++ b/src/config.py
@@ -1 +1 @@
-HOOK_TIMEOUT = 10
+HOOK_TIMEOUT = 30
EOF

set +e
DATE_OUT="$(cat "$DATE_DIFF" | "$EMBER" --no-color --explain --diff - -C "$DATES" 2>&1)"
st=$?
set -e
assert_not_contains "$DATE_OUT" "2024-10-01" "October is not leftover timeout 10"
assert_not_contains "$DATE_OUT" "CHANGELOG.md" "heading+date is not an afterimage"

# Same dest, plus a real leftover sentence — find the sentence, still skip October.
cat > "$DATES/docs/help.md" <<'EOF'
timeout default is 10
shipped 2024-10-01
EOF
set +e
DATE_REAL="$(cat "$DATE_DIFF" | "$EMBER" --no-color --explain --diff - -C "$DATES" 2>&1)"
st=$?
set -e
assert_exit "$st" 1 "real timeout leftover still fires"
assert_contains "$DATE_REAL" "timeout default is 10" "real leftover sentence"
assert_not_contains "$DATE_REAL" "2024-10-01" "date line still not an afterimage"

# Isolated retries 3→8: retries=3 is leftover; March is not.
RETRY_DIFF="$RUN/retries.diff"
cat > "$RETRY_DIFF" <<'EOF'
diff --git a/src/config.py b/src/config.py
--- a/src/config.py
+++ b/src/config.py
@@ -1 +1 @@
-MAX_RETRIES = 3
+MAX_RETRIES = 8
EOF
set +e
RETRY_OUT="$(cat "$RETRY_DIFF" | "$EMBER" --no-color --explain --diff - -C "$DATES" 2>&1)"
st=$?
set -e
assert_contains "$RETRY_OUT" "retries=3" "retries=3 is a leftover claim"
assert_not_contains "$RETRY_OUT" "2024-03-01" "March on its own line is not leftover 3"

echo
echo "== polarity True is not a nearby-name leftover =="
POLAR="$RUN/polar"
mkdir -p "$POLAR/src"
printf 'ENABLE_CACHE = False\n' > "$POLAR/src/flags.py"
cat > "$POLAR/README.md" <<'EOF'
the cache is enabled

DEBUG is True

assert ENABLE_CACHE is True
EOF
git -C "$POLAR" init -q
git -C "$POLAR" config user.email "ember@example.test"
git -C "$POLAR" config user.name "ember"
git -C "$POLAR" add .
git -C "$POLAR" commit -qm "polar dest"
POLAR_DIFF="$RUN/polar.diff"
cat > "$POLAR_DIFF" <<'EOF'
diff --git a/src/flags.py b/src/flags.py
--- a/src/flags.py
+++ b/src/flags.py
@@ -1 +1 @@
-ENABLE_CACHE = True
+ENABLE_CACHE = False
EOF
set +e
POLAR_OUT="$(cat "$POLAR_DIFF" | "$EMBER" --no-color --explain --diff - -C "$POLAR" 2>&1)"
st=$?
set -e
assert_exit "$st" 1 "real ENABLE_CACHE leftover still fires"
assert_contains "$POLAR_OUT" "ENABLE_CACHE is True" "same-line polarity leftover"
assert_not_contains "$POLAR_OUT" "DEBUG is True" "nearby True is not this flip"

echo
echo "passed=$pass failed=$fail"
if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
exit 0
