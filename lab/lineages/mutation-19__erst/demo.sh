#!/usr/bin/env bash
# Exercise `erst` on a synthetic ugly repo, then smoke real trees.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
ERST="$ROOT/erst"
export ERST

fail() { echo "demo FAIL: $*" >&2; exit 1; }
pass() { echo "demo ok: $*"; }

chmod +x "$ERST"
"$ERST" --selftest || fail "selftest"

FIX="$(mktemp -d "${TMPDIR:-/tmp}/erst-demo.XXXXXX")"
cleanup() { rm -rf "$FIX"; }
trap cleanup EXIT

mkdir -p "$FIX/docs" "$FIX/tests" "$FIX/deploy" "$FIX/src/foo bar" "$FIX/vendor/lib"
git -C "$FIX" init -q
git -C "$FIX" config user.email "erst@example.com"
git -C "$FIX" config user.name "erst"

# Natal family: t1 + present_threshold + a quiet PORT.
cat > "$FIX/core.py" << 'EOF'
t1 = 15
present_threshold = 0.4
PORT = 8080
EOF

cat > "$FIX/docs/how to set (t1).md" << 'EOF'
# Timing

T1 is 15 seconds.
The present_threshold is 0.4.
Listen on 8080.
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
EOF

cat > "$FIX/src/foo bar/t1.py" << 'EOF'
t1 = 15  # keep in sync with core.py
EOF

# Nested git: erst must keep using the outer tree.
echo 'nested' > "$FIX/vendor/lib/README"
git -C "$FIX/vendor/lib" init -q
git -C "$FIX/vendor/lib" config user.email "n@n"
git -C "$FIX/vendor/lib" config user.name "n"
git -C "$FIX/vendor/lib" add README
git -C "$FIX/vendor/lib" commit -q -m nested

git -C "$FIX" add core.py docs tests deploy "src/foo bar"
git -C "$FIX" commit -q -m 'introduce t1=15 present_threshold=0.4 port=8080'

# Mutation: rename only core.py. Siblings keep the erstwhile names.
cat > "$FIX/core.py" << 'EOF'
driftDelay = 15
presentThreshold = 0.45
PORT = 8080
EOF
git -C "$FIX" add core.py
git -C "$FIX" commit -q -m 'rename t1→driftDelay and present_threshold→presentThreshold'

# Default input is a commit, not FILE:LINE.
OUT="$FIX/out-head.txt"
"$ERST" --no-color -C "$FIX" HEAD | tee "$OUT"
grep -E '^owing' "$OUT" >/dev/null || fail "HEAD mutation should report owing"
grep -E 't1|T1' "$OUT" >/dev/null || fail "HEAD should mention erstwhile t1/T1"
grep -F 'present_threshold' "$OUT" >/dev/null || fail "HEAD should mention leftover snake"
grep -F 'docs/how to set (t1).md' "$OUT" >/dev/null || fail "missed weird markdown path"
grep -F 'src/foo bar/t1.py' "$OUT" >/dev/null || fail "missed path with spaces"
grep -F 'deploy/timing.yaml' "$OUT" >/dev/null || fail "missed yaml sibling"
grep -F 'tests/test_core.py' "$OUT" >/dev/null || fail "missed test sibling"
grep -E 't1↔driftDelay|driftDelay' "$OUT" >/dev/null || fail "missing t1↔driftDelay pair"
# Intact PORT family must stay quiet.
if grep -E '^(owing|paid|ok) +.*(port: 8080|PORT = 8080)' "$OUT" >/dev/null; then
  fail "intact PORT=8080 family should not appear without --all"
fi
pass "erst HEAD found unpaid renamed kin (t1/T1 and snake/camel, ugly paths)"

# FILE:LINE is rejected — that is owe's flip, kept.
set +e
"$ERST" --no-color -C "$FIX" core.py:1 >/dev/null 2>"$FIX/err.txt"
LOC=$?
set -e
[ "$LOC" -eq 2 ] || fail "FILE:LINE should exit 2 (got $LOC)"
grep -F 'not FILE:LINE' "$FIX/err.txt" >/dev/null || fail "FILE:LINE error should explain"
pass "FILE:LINE is refused"

set +e
"$ERST" --no-color --check -C "$FIX" HEAD >/dev/null
CHK=$?
set -e
[ "$CHK" -eq 1 ] || fail "--check should exit 1 on owing (got $CHK)"
pass "--check exits 1"

JSON="$FIX/out.json"
"$ERST" --json -C "$FIX" HEAD > "$JSON"
python3 - "$JSON" << 'PY'
import json, sys
d = json.load(open(sys.argv[1]))
assert d["change"]["kind"] == "commit"
assert "rename" in d["change"]["subject"]
assert d["cohorts"], "expected at least one cohort"
owing_paths = []
keys = []
pairs = []
for c in d["cohorts"]:
    keys.extend(c.get("keys") or [])
    pairs.extend(c.get("pairs") or [])
    owing_paths.extend([m.get("path") for m in c.get("owing") or []])
    owing_paths.extend([m.get("path") for m in c.get("echo") or []])
blob = " ".join(keys + pairs).lower()
assert "t1" in blob or "driftdelay" in blob, (keys, pairs)
assert any(p and ("timing.yaml" in p or p.endswith("t1.py") or "test_core" in p or "t1).md" in p)
           for p in owing_paths), owing_paths
print("json ok")
PY
pass "json on HEAD mutation"

# Birth commit: family already split at HEAD (driftDelay vs t1).
BIRTH="$FIX/out-birth.txt"
"$ERST" --no-color -C "$FIX" HEAD~1 | tee "$BIRTH"
grep -E '^(split|owing)' "$BIRTH" >/dev/null || fail "birth commit should report split/owing at HEAD"
grep -E 't1|T1|driftDelay' "$BIRTH" >/dev/null || fail "birth view should see erstwhile or adopted name"
pass "erst HEAD~1 reports the natal family already split at HEAD"

# Pipeline form
git -C "$FIX" diff -U0 HEAD~1 HEAD | "$ERST" --no-color - -C "$FIX" | tee "$FIX/pipe.txt"
grep -E '^owing|^change' "$FIX/pipe.txt" >/dev/null || fail "stdin erst - produced nothing"
pass "git diff | erst -"

echo
echo "all fixture checks passed"
echo
echo "== dogfood =="

SITBONE="/Users/annenpolka/ghq/github.com/annenpolka/sitbone"
if [ -d "$SITBONE/.git" ]; then
  "$ERST" --no-color -C "$SITBONE" e9b0f75 | tee "$FIX/sitbone-pa.txt"
  grep -F 'change commit' "$FIX/sitbone-pa.txt" >/dev/null || fail "sitbone: no change header"
  grep -E '0\.4|threshold|presentThreshold' "$FIX/sitbone-pa.txt" >/dev/null \
    || fail "sitbone PresenceArbiter: expected 0.4 or threshold↔presentThreshold"
  grep -F 'PresenceArbiter' "$FIX/sitbone-pa.txt" >/dev/null \
    || fail "sitbone: expected PresenceArbiter in report"
  grep -F 'threshold↔presentThreshold' "$FIX/sitbone-pa.txt" >/dev/null \
    || fail "sitbone: expected threshold↔presentThreshold natal pair"
  if grep -F 'SiteObserver.swift' "$FIX/sitbone-pa.txt" >/dev/null; then
    fail "sitbone: SiteObserver.threshold=0.7 is a different domain"
  fi
  pass "sitbone e9b0f75 PresenceArbiter (hysteresis + ident natal keys)"

  "$ERST" --no-color -C "$SITBONE" 1fcdec6 | tee "$FIX/sitbone-t1.txt"
  grep -F 'change commit' "$FIX/sitbone-t1.txt" >/dev/null || fail "sitbone t1: no change header"
  grep -E 't1|T1|driftDelay' "$FIX/sitbone-t1.txt" >/dev/null \
    || fail "sitbone 1fcdec6: expected t1↔driftDelay leftovers"
  grep -E 'SPEC.md|README.md|CLAUDE.md|FocusStateMachine' "$FIX/sitbone-t1.txt" >/dev/null \
    || fail "sitbone 1fcdec6: expected leftover T1 in docs/tests"
  grep -F 't1↔driftDelay' "$FIX/sitbone-t1.txt" >/dev/null \
    || fail "sitbone 1fcdec6: expected t1↔driftDelay pair"
  if grep -E 'counters↔updatedCounters|radius↔cornerRadius|window↔focusedWindow' "$FIX/sitbone-t1.txt" >/dev/null; then
    fail "sitbone 1fcdec6: local lint renames should not be natal pairs"
  fi
  pass "sitbone 1fcdec6 (t1→driftDelay, leftover T1 kin)"
else
  echo "demo skip: sitbone not present"
fi

KIZU="/Users/annenpolka/ghq/github.com/annenpolka/kizu"
if [ -d "$KIZU/.git" ]; then
  "$ERST" --no-color -C "$KIZU" fb355e0 | tee "$FIX/kizu.txt" >/dev/null
  grep -F 'change commit' "$FIX/kizu.txt" >/dev/null || fail "kizu: no change header"
  pass "kizu fb355e0 smoked"
else
  echo "demo skip: kizu not present"
fi

echo
echo "all demo checks passed"
