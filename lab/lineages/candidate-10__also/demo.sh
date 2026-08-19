#!/usr/bin/env bash
# Exercise `also` on a synthetic ugly repo and one real tree.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
ALSO="$ROOT/also"
export ALSO

fail() { echo "demo FAIL: $*" >&2; exit 1; }
pass() { echo "demo ok: $*"; }

"$ALSO" --selftest || fail "selftest"

FIX="$(mktemp -d "${TMPDIR:-/tmp}/also-demo.XXXXXX")"
cleanup() { rm -rf "$FIX"; }
trap cleanup EXIT

mkdir -p "$FIX/docs" "$FIX/tests" "$FIX/deploy" "$FIX/generated" "$FIX/src/foo bar" "$FIX/vendor/lib"
git -C "$FIX" init -q
git -C "$FIX" config user.email "also@example.com"
git -C "$FIX" config user.name "also"

cat > "$FIX/config.py" << 'EOF'
TIMEOUT = 30
RETRY = 3
EOF

cat > "$FIX/docs/how to set (timeout).md" << 'EOF'
# Timeout

The service timeout is 30 seconds.
Retries are 3.
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
EOF

cat > "$FIX/generated/timeout.gen.py" << 'EOF'
# generated — do not edit
TIMEOUT = 30
EOF

cat > "$FIX/src/foo bar/timeout.py" << 'EOF'
TIMEOUT = 30  # keep in sync with config.py
EOF

# Nested git repo: also must keep using the outer tree.
echo 'nested' > "$FIX/vendor/lib/README"
git -C "$FIX/vendor/lib" init -q
git -C "$FIX/vendor/lib" config user.email "n@n"
git -C "$FIX/vendor/lib" config user.name "n"
git -C "$FIX/vendor/lib" add README
git -C "$FIX/vendor/lib" commit -q -m nested

git -C "$FIX" add config.py docs tests deploy generated "src/foo bar"
git -C "$FIX" commit -q -m 'introduce timeout=30 and retry=3'

cat > "$FIX/config.py" << 'EOF'
TIMEOUT = 60
RETRY = 3
EOF
git -C "$FIX" add config.py
git -C "$FIX" commit -q -m 'raise TIMEOUT to 60'

OUT="$FIX/out.txt"
"$ALSO" --no-color -C "$FIX" config.py:1 | tee "$OUT"
grep -F 'docs/how to set (timeout).md:3' "$OUT" >/dev/null || fail "missed weird markdown path"
grep -F 'src/foo bar/timeout.py:1' "$OUT" >/dev/null || fail "missed path with spaces"
grep -F 'deploy/timeout.yaml:1' "$OUT" >/dev/null || fail "missed yaml sibling"
grep -F 'tests/test_timeout.py:4' "$OUT" >/dev/null || fail "missed test sibling"
grep -F 'generated/timeout.gen.py:2' "$OUT" >/dev/null || fail "missed generated sibling"
grep -E '^drift' "$OUT" >/dev/null || fail "expected drift rows"
if grep -E '^ok +.+: # Timeout' "$OUT" >/dev/null; then
  fail "heading '# Timeout' should not be identifier-only kin"
fi
pass "location mode found drifted birth-siblings (including ugly paths)"

set +e
"$ALSO" --no-color --check -C "$FIX" config.py:1 >/dev/null
CHK=$?
set -e
[ "$CHK" -eq 1 ] || fail "--check should exit 1 on drift (got $CHK)"
pass "--check exits 1"

JSON="$FIX/out.json"
"$ALSO" --json -C "$FIX" -n 1 config.py > "$JSON"
python3 - "$JSON" << 'PY'
import json, sys
d = json.load(open(sys.argv[1]))
assert d["query"]["line"] == 1
assert d["birth"]["commit"] != "UNCOMMITTED"
assert "30" in d["keys"]
statuses = {s["status"] for s in d["siblings"]}
assert "drift" in statuses, statuses
paths = {s.get("path") for s in d["siblings"]}
assert any(p and p.endswith("timeout.yaml") for p in paths)
print("json ok")
PY
pass "json + -n/--line"

# Uncommitted further drift + --diff
cat > "$FIX/config.py" << 'EOF'
TIMEOUT = 90
RETRY = 3
EOF
DIFF_OUT="$FIX/diff.txt"
"$ALSO" --no-color --diff -C "$FIX" | tee "$DIFF_OUT"
grep -F 'TIMEOUT = 90' "$DIFF_OUT" >/dev/null || fail "--diff should analyze working-tree replacement"
grep -E '^drift' "$DIFF_OUT" >/dev/null || fail "--diff should still report unpaid siblings"
pass "--diff on dirty working tree"

# Pipeline form: git diff | also --diff -
git -C "$FIX" diff -U0 HEAD | "$ALSO" --no-color --diff - -C "$FIX" | tee "$FIX/pipe.txt"
grep -E '^drift' "$FIX/pipe.txt" >/dev/null || fail "stdin --diff - produced no drift"
pass "git diff | also --diff -"

# Real repo smoke (read-only). Presence of `birth` is the contract.
SITBONE="/Users/annenpolka/ghq/github.com/annenpolka/sitbone"
if [ -d "$SITBONE/.git" ]; then
  "$ALSO" --no-color -C "$SITBONE" Sources/SitboneCore/SitboneCore.swift:107 \
    | tee "$FIX/sitbone.txt" >/dev/null
  grep -E '^birth' "$FIX/sitbone.txt" >/dev/null || fail "sitbone: no birth line"
  grep -F 'driftDelay: TimeInterval = 15' "$FIX/sitbone.txt" >/dev/null || fail "sitbone: query text missing"
  if grep -F 'query lost init' "$FIX/sitbone.txt" >/dev/null; then
    fail "sitbone: generic key 'init' leaked into classify"
  fi
  grep -E 'T1' "$FIX/sitbone.txt" >/dev/null || fail "sitbone: expected T1=15 documentation sibling"
  pass "sitbone real-repo smoke"
else
  echo "demo skip: sitbone not present"
fi

KIZU="/Users/annenpolka/ghq/github.com/annenpolka/kizu"
if [ -d "$KIZU/.git" ]; then
  "$ALSO" --no-color -C "$KIZU" src/app.rs:64 | tee "$FIX/kizu.txt" >/dev/null
  grep -F 'explain this change' "$FIX/kizu.txt" >/dev/null || fail "kizu: string key missing"
  grep -F 'docs/SPEC.md' "$FIX/kizu.txt" >/dev/null || fail "kizu: expected echo of unique string in docs"
  pass "kizu unique-string echo"
else
  echo "demo skip: kizu not present"
fi

echo
echo "all demo checks passed"
