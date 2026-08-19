#!/usr/bin/env bash
# Exercise kith: natal-record leftovers (typed claims ∪ inflected kin).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
KITH="$ROOT/kith"
chmod +x "$KITH"

pass=0
fail=0

assert_contains() {
  local haystack="$1" needle="$2" label="$3"
  if grep -Fq -- "$needle" <<<"$haystack"; then
    echo "  ok  $label"
    pass=$((pass + 1))
  else
    echo "  FAIL $label"
    echo "    missing: $needle"
    echo "$haystack" | sed 's/^/    /' | head -80
    fail=$((fail + 1))
  fi
}

assert_not_contains() {
  local haystack="$1" needle="$2" label="$3"
  if grep -Fq -- "$needle" <<<"$haystack"; then
    echo "  FAIL $label"
    echo "    unexpectedly found: $needle"
    echo "$haystack" | sed 's/^/    /' | head -80
    fail=$((fail + 1))
  else
    echo "  ok  $label"
    pass=$((pass + 1))
  fi
}

assert_exit() {
  local got="$1" want="$2" label="$3"
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
"$KITH" self-test
st=$?
set -e
assert_exit "$st" 0 "embedded natal/via/fuse tests"

RUN="$ROOT/fixtures/.run"
rm -rf "$RUN"
mkdir -p "$RUN"

echo
echo "== joint fixture: rename+value+json, leftovers fused =="
FIX="$RUN/joint"
mkdir -p "$FIX/docs" "$FIX/tests" "$FIX/deploy" "$FIX/src/foo bar" "$FIX/vendor/lib"
git -C "$FIX" init -q
git -C "$FIX" config user.email "kith@example.test"
git -C "$FIX" config user.name "kith"

cat > "$FIX/core.py" << 'EOF'
t1 = 15
present_threshold = 0.4
PORT = 8080
HOOK_TIMEOUT = 10
ENABLE_CACHE = True
EOF

cat > "$FIX/plugin.json" << 'EOF'
{
  "name": "toy",
  "version": "0.3.0",
  "hooks": {
    "timeout": 10
  }
}
EOF

cat > "$FIX/docs/how to set (t1).md" << 'EOF'
# Timing

T1 is 15 seconds.
The present_threshold is 0.4.
plugin version 0.3.0, hook timeout 10 seconds.
Listen on 8080.
Cache is enabled (`ENABLE_CACHE = True`).
shipped 2024-10-01
EOF

cat > "$FIX/tests/test_core.py" << 'EOF'
from core import t1, present_threshold

def test_t1():
    assert t1 == 15
    assert present_threshold == 0.4
EOF

cat > "$FIX/deploy/timing.yaml" << 'EOF'
t1: 15
present_threshold: 0.4
port: 8080
timeout: 10
EOF

cat > "$FIX/src/foo bar/t1.py" << 'EOF'
t1 = 15  # keep in sync with core.py
EOF

cat > "$FIX/README.md" << 'EOF'
the cache is enabled

DEBUG is True

assert ENABLE_CACHE is True
EOF

echo 'nested' > "$FIX/vendor/lib/README"
git -C "$FIX/vendor/lib" init -q
git -C "$FIX/vendor/lib" config user.email "n@n"
git -C "$FIX/vendor/lib" config user.name "n"
git -C "$FIX/vendor/lib" add README
git -C "$FIX/vendor/lib" commit -q -m nested

git -C "$FIX" add core.py plugin.json docs tests deploy "src/foo bar" README.md
git -C "$FIX" commit -q -m 'introduce t1=15 present_threshold=0.4 version=0.3.0 timeout=10'

cat > "$FIX/core.py" << 'EOF'
driftDelay = 15
presentThreshold = 0.45
PORT = 8080
HOOK_TIMEOUT = 30
ENABLE_CACHE = False
EOF

cat > "$FIX/plugin.json" << 'EOF'
{
  "name": "toy",
  "version": "0.7.0",
  "hooks": {
    "timeout": 10
  }
}
EOF

git -C "$FIX" add core.py plugin.json
git -C "$FIX" commit -q -m 'rename t1→driftDelay, bump threshold/timeout/version, flip cache'

OUTFILE="$FIX/out-head.txt"
set +e
OUT="$("$KITH" --no-color -C "$FIX" HEAD 2>&1)"
st=$?
set -e
printf '%s\n' "$OUT" | tee "$OUTFILE"
assert_exit "$st" 1 "HEAD mutation yields leftovers"
assert_contains "$OUT" "t1↔driftDelay" "natal pair t1↔driftDelay"
assert_contains "$OUT" "T1 is 15 seconds" "inflected T1 leftover"
assert_contains "$OUT" "both" "joint via=both exists"
assert_contains "$OUT" "present_threshold" "snake leftover of camel bump"
assert_contains "$OUT" "The present_threshold is 0.4" "docs snake leftover with sentence period"
assert_contains "$OUT" "0.3.0" "typed version leftover is the full token"
assert_contains "$OUT" "plugin version 0.3.0" "prose version leftover not homonym-skipped"
assert_contains "$OUT" "docs/how to set (t1).md" "weird markdown path"
assert_contains "$OUT" "src/foo bar/t1.py" "path with spaces"
assert_contains "$OUT" "deploy/timing.yaml" "yaml sibling"
assert_contains "$OUT" "tests/test_core.py" "test sibling"
assert_contains "$OUT" "ENABLE_CACHE is True" "same-line polarity leftover"
assert_not_contains "$OUT" "DEBUG is True" "nearby True is not this flip"
assert_not_contains "$OUT" "2024-10-01" "October is not leftover timeout 10"
assert_not_contains "$OUT" "0.3'" "version not truncated to 0.3"

# Intact PORT family stays quiet unless it rides another natal.
if grep -E 'port: 8080|Listen on 8080' <<<"$OUT" >/dev/null; then
  echo "  FAIL intact PORT=8080 should not be its own leftover"
  fail=$((fail + 1))
else
  echo "  ok  intact PORT=8080 is quiet"
  pass=$((pass + 1))
fi

# The joint object: T1 is 15 is via=both on one row (claim ∧ kin), not two.
BOTH_LINE="$(grep -F 'T1 is 15 seconds' <<<"$OUT" || true)"
assert_contains "$BOTH_LINE" "both" "T1 is 15 seconds is via=both (claim∧kin)"
T1_ROWS="$(grep -c -F 'T1 is 15 seconds' <<<"$OUT" || true)"
if [[ "$T1_ROWS" -eq 1 ]]; then
  echo "  ok  T1 leftover is one natal row (via=both, not claim+kin split)"
  pass=$((pass + 1))
else
  echo "  FAIL T1 leftover rows=$T1_ROWS (want 1)"
  fail=$((fail + 1))
fi

# Dest-line fuse: one prose line speaks version AND timeout. --no-fuse is concat.
PROSE='plugin version 0.3.0, hook timeout 10 seconds.'
FUSED_PROSE="$(grep -c -F "$PROSE" <<<"$OUT" || true)"
if [[ "$FUSED_PROSE" -eq 1 ]]; then
  echo "  ok  version+timeout prose fused to one dest-line leftover"
  pass=$((pass + 1))
else
  echo "  FAIL fused prose rows=$FUSED_PROSE (want 1)"
  fail=$((fail + 1))
fi

set +e
NOFUSE="$("$KITH" --no-color --no-fuse -C "$FIX" HEAD)"
st=$?
set -e
NOFUSE_PROSE="$(grep -c -F "$PROSE" <<<"$NOFUSE" || true)"
if [[ "$NOFUSE_PROSE" -ge 2 ]]; then
  echo "  ok  --no-fuse is the concatenation ($NOFUSE_PROSE rows for version+timeout prose)"
  pass=$((pass + 1))
else
  echo "  FAIL --no-fuse prose rows=$NOFUSE_PROSE (want >=2: version natal + timeout natal)"
  echo "$NOFUSE" | sed 's/^/    /' | head -50
  fail=$((fail + 1))
fi

set +e
"$KITH" --no-color --check -C "$FIX" HEAD >/dev/null
CHK=$?
set -e
assert_exit "$CHK" 1 "--check exits 1 on leftovers"

JSON="$FIX/out.json"
set +e
"$KITH" --json --no-color -C "$FIX" HEAD > "$JSON"
set -e
python3 - "$JSON" << 'PY'
import json, sys
d = json.load(open(sys.argv[1]))
assert d["natals"], "expected natal records"
assert d["leftovers"], "expected leftovers"
vias = {L["via"] for L in d["leftovers"]}
assert "both" in vias, vias
excerpts = " ".join(L["excerpt"] for L in d["leftovers"])
assert "T1 is 15" in excerpts, excerpts
assert "0.3.0" in excerpts, excerpts
paths = [L["path"] for L in d["leftovers"]]
assert any("t1).md" in p or "how to set" in p for p in paths), paths
print("json ok")
PY
echo "  ok  json leftovers carry via=both + T1 + 0.3.0"
pass=$((pass + 1))

echo
echo "== FILE:LINE is refused =="
set +e
"$KITH" --no-color -C "$FIX" core.py:1 >/dev/null 2>"$FIX/err.txt"
LOC=$?
set -e
assert_exit "$LOC" 2 "FILE:LINE exits 2"
assert_contains "$(cat "$FIX/err.txt")" "not FILE:LINE" "FILE:LINE error explains"

echo
echo "== stdin diff against dest with JSON leftover =="
KIZU="$RUN/kizu-toy"
mkdir -p "$KIZU"
cat > "$KIZU/plugin.json" << 'EOF'
{
  "name": "toy",
  "version": "0.7.0",
  "hooks": {
    "timeout": 10
  }
}
EOF
cat > "$KIZU/README.md" << 'EOF'
plugin version 0.3.0, hook timeout 10 seconds.
EOF
git -C "$KIZU" init -q
git -C "$KIZU" config user.email "kith@example.test"
git -C "$KIZU" config user.name "kith"
git -C "$KIZU" add .
git -C "$KIZU" commit -qm "dest still claims 0.3.0 in prose"

JSONDIFF="$RUN/plugin.diff"
cat > "$JSONDIFF" << 'EOF'
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
FACTS="$(cat "$JSONDIFF" | "$KITH" --facts-only --no-color --diff - -C "$KIZU" 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "json facts-only exits 0"
assert_contains "$FACTS" "0.3.0" "json old version is the full token"
assert_not_contains "$FACTS" "0.3'" "not truncated"

set +e
JSON_OUT="$(cat "$JSONDIFF" | "$KITH" --no-color --explain --diff - -C "$KIZU" 2>&1)"
st=$?
set -e
assert_exit "$st" 1 "json hunk finds dest leftovers"
assert_contains "$JSON_OUT" "plugin version 0.3.0" "prose leftover of typed version"
assert_contains "$JSON_OUT" "README.md" "prose leftover path"

echo
echo "== destroyer date-in-version =="
DATES="$RUN/dates"
mkdir -p "$DATES/src" "$DATES/docs"
printf 'HOOK_TIMEOUT = 30\nMAX_RETRIES = 8\n' > "$DATES/src/config.py"
cat > "$DATES/CHANGELOG.md" << 'EOF'
## timeout
shipped 2024-10-01
EOF
cat > "$DATES/docs/dates.md" << 'EOF'
hook timeout default was documented the day we shipped, 2024-10-01.
retries=3 landed.
landed 2024-03-01.
EOF
git -C "$DATES" init -q
git -C "$DATES" config user.email "kith@example.test"
git -C "$DATES" config user.name "kith"
git -C "$DATES" add .
git -C "$DATES" commit -qm "dest with ISO dates"

DATE_DIFF="$RUN/timeout.diff"
cat > "$DATE_DIFF" << 'EOF'
diff --git a/src/config.py b/src/config.py
--- a/src/config.py
+++ b/src/config.py
@@ -1 +1 @@
-HOOK_TIMEOUT = 10
+HOOK_TIMEOUT = 30
EOF
set +e
DATE_OUT="$(cat "$DATE_DIFF" | "$KITH" --no-color --explain --diff - -C "$DATES" 2>&1)"
st=$?
set -e
assert_not_contains "$DATE_OUT" "2024-10-01" "October is not leftover timeout 10"
assert_not_contains "$DATE_OUT" "CHANGELOG.md" "heading+date is not a leftover"

cat > "$DATES/docs/help.md" << 'EOF'
timeout default is 10
shipped 2024-10-01
EOF
set +e
DATE_REAL="$(cat "$DATE_DIFF" | "$KITH" --no-color --explain --diff - -C "$DATES" 2>&1)"
st=$?
set -e
assert_exit "$st" 1 "real timeout leftover still fires"
assert_contains "$DATE_REAL" "timeout default is 10" "real leftover sentence"
assert_not_contains "$DATE_REAL" "2024-10-01" "date line still not a leftover"

RETRY_DIFF="$RUN/retries.diff"
cat > "$RETRY_DIFF" << 'EOF'
diff --git a/src/config.py b/src/config.py
--- a/src/config.py
+++ b/src/config.py
@@ -1 +1 @@
-MAX_RETRIES = 3
+MAX_RETRIES = 8
EOF
set +e
RETRY_OUT="$(cat "$RETRY_DIFF" | "$KITH" --no-color --explain --diff - -C "$DATES" 2>&1)"
st=$?
set -e
assert_contains "$RETRY_OUT" "retries=3" "retries=3 is a leftover claim"
assert_not_contains "$RETRY_OUT" "2024-03-01" "March on its own line is not leftover 3"

echo
echo "== ugly filenames + nested git =="
UGLY="$RUN/ugly"
mkdir -p "$UGLY/src" "$UGLY/nested/inner" "$UGLY/generated" "$UGLY/emoji"
printf 'MAX_RETRIES = 3\nTIMEOUT = 10\n' > "$UGLY/src/config.py"
printf 'still claims MAX_RETRIES is 3\n' > "$UGLY/emoji/🌀 leftover.md"
printf '# nested still says timeout is 10\n' > "$UGLY/nested/inner/note.md"
printf 'timeout leftover 10\n' > "$UGLY/file with spaces.md"
printf 'タイムアウトは 10 秒\n' > "$UGLY/日本語コメント.md"
git -C "$UGLY/nested" init -q
git -C "$UGLY/nested" config user.email "kith@example.test"
git -C "$UGLY/nested" config user.name "kith"
git -C "$UGLY/nested" add .
git -C "$UGLY/nested" commit -qm nested
git -C "$UGLY" init -q
git -C "$UGLY" config user.email "kith@example.test"
git -C "$UGLY" config user.name "kith"
git -C "$UGLY" add .
git -C "$UGLY" commit -qm "ugly baseline"
printf 'MAX_ATTEMPTS = 8\nTIMEOUT = 30\n' > "$UGLY/src/config.py"
set +e
UGLY_OUT="$("$KITH" --no-color -C "$UGLY" 2>&1)"
st=$?
set -e
assert_exit "$st" 1 "ugly tree finds leftovers"
assert_contains "$UGLY_OUT" "file with spaces.md" "space in filename"
assert_contains "$UGLY_OUT" "日本語コメント.md" "unicode filename"
assert_contains "$UGLY_OUT" "🌀 leftover.md" "emoji filename"
assert_contains "$UGLY_OUT" "nested/inner/note.md" "nested git file visible"

echo
echo "== dogfood sitbone e9b0f75 =="
SITBONE="/Users/annenpolka/ghq/github.com/annenpolka/sitbone"
if [ -d "$SITBONE/.git" ]; then
  set +e
  SIT="$("$KITH" --no-color -C "$SITBONE" e9b0f75 2>&1)"
  st=$?
  set -e
  echo "$SIT" | tee "$RUN/sitbone-e9b0f75.txt" | head -60
  assert_contains "$SIT" "threshold" "sitbone natal mentions threshold"
  assert_contains "$SIT" "0.4" "sitbone leftover 0.4"
  assert_contains "$SIT" "presentThreshold" "sitbone adopted presentThreshold"
  assert_not_contains "$SIT" "SiteObserver.swift" "SiteObserver.threshold=0.7 is another domain"
  if echo "$SIT" | grep -E 'CLAUDE.md|PresenceArbiterTests|0019-presence' >/dev/null; then
    echo "  ok  sitbone leftover in docs/tests/ADR"
    pass=$((pass + 1))
  else
    echo "  FAIL sitbone: expected leftover in CLAUDE.md / tests / ADR"
    echo "$SIT" | sed 's/^/    /' | head -40
    fail=$((fail + 1))
  fi
  if echo "$SIT" | grep -E '^  both' >/dev/null; then
    echo "  ok  sitbone has via=both leftover"
    pass=$((pass + 1))
  else
    echo "  FAIL sitbone: expected via=both (threshold + 0.4 on one line)"
    fail=$((fail + 1))
  fi
  assert_contains "$SIT" "PresenceArbiterTests.swift" "sitbone test comment leftover of natal 0.4"
  # v0.2: competing rename threshold↔absentThreshold is folded into one record
  if echo "$SIT" | grep -E '^NATAL threshold↔absentThreshold  ' >/dev/null; then
    echo "  FAIL sitbone: threshold↔absentThreshold should not be its own natal"
    fail=$((fail + 1))
  else
    echo "  ok  1-to-N split folded (no competing absentThreshold natal)"
    pass=$((pass + 1))
  fi
else
  echo "  skip sitbone not present"
fi

echo
echo "passed=$pass failed=$fail"
if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
exit 0
