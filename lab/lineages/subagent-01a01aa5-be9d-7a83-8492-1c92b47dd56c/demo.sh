#!/usr/bin/env bash
# Exercise `owe` on a synthetic ugly repo, then smoke real trees.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
OWE="$ROOT/owe"
export OWE

fail() { echo "demo FAIL: $*" >&2; exit 1; }
pass() { echo "demo ok: $*"; }

chmod +x "$OWE"
"$OWE" --selftest || fail "selftest"

FIX="$(mktemp -d "${TMPDIR:-/tmp}/owe-demo.XXXXXX")"
cleanup() { rm -rf "$FIX"; }
trap cleanup EXIT

mkdir -p "$FIX/docs" "$FIX/tests" "$FIX/deploy" "$FIX/generated" "$FIX/src/foo bar" "$FIX/vendor/lib"
git -C "$FIX" init -q
git -C "$FIX" config user.email "owe@example.com"
git -C "$FIX" config user.name "owe"

cat > "$FIX/config.py" << 'EOF'
TIMEOUT = 30
RETRY = 3
PORT = 8080
EOF

cat > "$FIX/docs/how to set (timeout).md" << 'EOF'
# Timeout

The service timeout is 30 seconds.
Retries are 3.
Listen on 8080.
EOF

cat > "$FIX/tests/test_timeout.py" << 'EOF'
from config import TIMEOUT, RETRY

def test_timeout():
    assert TIMEOUT == 30
    assert RETRY == 3
EOF

cat > "$FIX/deploy/timeout.yaml" << 'EOF'
timeout: 30
retry: 3
port: 8080
EOF

cat > "$FIX/generated/timeout.gen.py" << 'EOF'
# generated — do not edit
TIMEOUT = 30
EOF

cat > "$FIX/src/foo bar/timeout.py" << 'EOF'
TIMEOUT = 30  # keep in sync with config.py
EOF

# Nested git repo: owe must keep using the outer tree.
echo 'nested' > "$FIX/vendor/lib/README"
git -C "$FIX/vendor/lib" init -q
git -C "$FIX/vendor/lib" config user.email "n@n"
git -C "$FIX/vendor/lib" config user.name "n"
git -C "$FIX/vendor/lib" add README
git -C "$FIX/vendor/lib" commit -q -m nested

git -C "$FIX" add config.py docs tests deploy generated "src/foo bar"
git -C "$FIX" commit -q -m 'introduce timeout=30 retry=3 port=8080'

cat > "$FIX/config.py" << 'EOF'
TIMEOUT = 60
RETRY = 3
PORT = 8080
EOF
git -C "$FIX" add config.py
git -C "$FIX" commit -q -m 'raise TIMEOUT to 60'

# Default input is a commit, not FILE:LINE.
OUT="$FIX/out-head.txt"
"$OWE" --no-color -C "$FIX" HEAD | tee "$OUT"
grep -E '^owing' "$OUT" >/dev/null || fail "HEAD mutation should report owing"
grep -F 'docs/how to set (timeout).md' "$OUT" >/dev/null || fail "missed weird markdown path"
grep -F 'src/foo bar/timeout.py' "$OUT" >/dev/null || fail "missed path with spaces"
grep -F 'deploy/timeout.yaml' "$OUT" >/dev/null || fail "missed yaml sibling"
grep -F 'tests/test_timeout.py' "$OUT" >/dev/null || fail "missed test sibling"
grep -F 'generated/timeout.gen.py' "$OUT" >/dev/null || fail "missed generated sibling"
# Intact families (RETRY=3, PORT=8080) must stay quiet by default.
# The birth subject mentions port=8080; look at member rows only.
if grep -E '^(owing|paid|ok) +.*(port: 8080|PORT = 8080)' "$OUT" >/dev/null; then
  fail "intact PORT=8080 family should not appear without --all"
fi
pass "owe HEAD found unpaid timeout kin (including ugly paths)"

# FILE:LINE is rejected — that is the mutation.
set +e
"$OWE" --no-color -C "$FIX" config.py:1 >/dev/null 2>"$FIX/err.txt"
LOC=$?
set -e
[ "$LOC" -eq 2 ] || fail "FILE:LINE should exit 2 (got $LOC)"
grep -F 'not FILE:LINE' "$FIX/err.txt" >/dev/null || fail "FILE:LINE error should explain the flip"
pass "FILE:LINE is refused"

set +e
"$OWE" --no-color --check -C "$FIX" HEAD >/dev/null
CHK=$?
set -e
[ "$CHK" -eq 1 ] || fail "--check should exit 1 on owing (got $CHK)"
pass "--check exits 1"

JSON="$FIX/out.json"
"$OWE" --json -C "$FIX" HEAD > "$JSON"
python3 - "$JSON" << 'PY'
import json, sys
d = json.load(open(sys.argv[1]))
assert d["change"]["kind"] == "commit"
assert d["change"]["subject"].startswith("raise TIMEOUT")
assert d["cohorts"], "expected at least one cohort"
owing_paths = []
for c in d["cohorts"]:
    assert "30" in c["abandoned"] or "30" in c["keys"]
    owing_paths.extend([m.get("path") for m in c["owing"]])
assert any(p and p.endswith("timeout.yaml") for p in owing_paths), owing_paths
print("json ok")
PY
pass "json on HEAD mutation"

# Birth commit: the family has already split in HEAD (60 vs 30).
BIRTH="$FIX/out-birth.txt"
"$OWE" --no-color -C "$FIX" HEAD~1 | tee "$BIRTH"
grep -E '^(split|owing)' "$BIRTH" >/dev/null || fail "birth commit should report split/owing at HEAD"
grep -E '60' "$BIRTH" >/dev/null || fail "birth view should see the HEAD 60 faction"
grep -E '30' "$BIRTH" >/dev/null || fail "birth view should see leftover 30s"
pass "owe HEAD~1 reports the natal family already split at HEAD"

# Uncommitted further drift + --wt
cat > "$FIX/config.py" << 'EOF'
TIMEOUT = 90
RETRY = 3
PORT = 8080
EOF
WT_OUT="$FIX/wt.txt"
"$OWE" --no-color --wt -C "$FIX" | tee "$WT_OUT"
grep -E '^owing' "$WT_OUT" >/dev/null || fail "--wt should report unpaid kin"
grep -E '90|60' "$WT_OUT" >/dev/null || fail "--wt should mention the adopted/abandoned side"
pass "--wt on dirty working tree"

# Pipeline form: git diff | owe -
git -C "$FIX" diff -U0 HEAD | "$OWE" --no-color - -C "$FIX" | tee "$FIX/pipe.txt"
grep -E '^owing' "$FIX/pipe.txt" >/dev/null || fail "stdin owe - produced no owing"
pass "git diff | owe -"

# Restore committed config for real-repo smokes (fixture no longer needed).
git -C "$FIX" checkout -q -- config.py

echo
echo "all fixture checks passed"
echo
echo "== dogfood =="

SITBONE="/Users/annenpolka/ghq/github.com/annenpolka/sitbone"
if [ -d "$SITBONE/.git" ]; then
  "$OWE" --no-color -C "$SITBONE" e9b0f75 | tee "$FIX/sitbone.txt" >/dev/null
  grep -F 'change commit' "$FIX/sitbone.txt" >/dev/null || fail "sitbone: no change header"
  grep -F '0.4' "$FIX/sitbone.txt" >/dev/null || fail "sitbone: expected abandoned 0.4"
  grep -F 'PresenceArbiterTests.swift' "$FIX/sitbone.txt" >/dev/null || fail "sitbone: expected leftover 0.4 test"
  pass "sitbone e9b0f75 (0.4 → 0.45 hysteresis, unpaid tests)"
else
  echo "demo skip: sitbone not present"
fi

KIZU="/Users/annenpolka/ghq/github.com/annenpolka/kizu"
if [ -d "$KIZU/.git" ]; then
  "$OWE" --no-color -C "$KIZU" fb355e0 | tee "$FIX/kizu.txt" >/dev/null
  grep -F 'change commit' "$FIX/kizu.txt" >/dev/null || fail "kizu: no change header"
  pass "kizu fb355e0 (JP→EN scar bodies; runs from a commit)"
else
  echo "demo skip: kizu not present"
fi

TENAOSHI="/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi"
if [ -d "$TENAOSHI/.git" ]; then
  "$OWE" --no-color -C "$TENAOSHI" 7505f56 | tee "$FIX/tenaoshi.txt" >/dev/null
  grep -F 'change commit' "$FIX/tenaoshi.txt" >/dev/null || fail "tenaoshi: no change header"
  pass "tenaoshi 7505f56 (adapter timeout birth; runs from a commit)"
else
  echo "demo skip: tenaoshi not present"
fi

VOID="/Users/annenpolka/ghq/github.com/annenpolka/voidtrace"
if [ -d "$VOID/.git" ]; then
  "$OWE" --no-color -C "$VOID" 4c0a717 | tee "$FIX/voidtrace.txt" >/dev/null
  grep -F 'change commit' "$FIX/voidtrace.txt" >/dev/null || fail "voidtrace: no change header"
  pass "voidtrace 4c0a717 (CLI surface; runs from a commit)"
else
  echo "demo skip: voidtrace not present"
fi

echo
echo "all demo checks passed"
