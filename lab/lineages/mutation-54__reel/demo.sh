#!/usr/bin/env bash
# End-to-end demo. Extra args (e.g. ./demo.sh 0) are ignored.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
chmod +x "$ROOT/reel"
C=("$ROOT/reel")

PASS=0
FAIL=0
assert() {
  local name="$1"
  shift
  if "$@"; then
    PASS=$((PASS + 1))
    echo "  ok  $name"
  else
    FAIL=$((FAIL + 1))
    echo "  FAIL $name" >&2
  fi
}

echo "======== 1. selftest ========"
"${C[@]}" --selftest

echo "======== 2. unit tests ========"
python3 -m unittest discover -s tests -q
echo "unit tests: OK"

echo "======== 3. fixture: mixed feature, then squash ========"
FIX="$(mktemp -d "${TMPDIR:-/tmp}/reel-demo.XXXXXX")"
SPLIT="$(mktemp -d "${TMPDIR:-/tmp}/reel-split.XXXXXX")"
cleanup() { rm -rf "$FIX" "$SPLIT"; }
trap cleanup EXIT

git -C "$FIX" init -q -b main
git -C "$FIX" config user.name reel
git -C "$FIX" config user.email reel@demo
git -C "$FIX" config commit.gpgsign false
export GIT_AUTHOR_NAME=reel GIT_AUTHOR_EMAIL=reel@demo
export GIT_COMMITTER_NAME=reel GIT_COMMITTER_EMAIL=reel@demo

commit() {
  git -C "$FIX" add -A
  git -C "$FIX" commit -q -m "$1"
}

mkdir -p "$FIX/pkg" "$FIX/tests"
cat > "$FIX/pkg/__init__.py" << 'PY'
PY
commit "init"

# C1 — types/lexer
cat > "$FIX/pkg/lexer.py" << 'PY'
class Lexer:
    def __init__(self, src):
        self.src = src
    def tokens(self):
        return self.src.split()
PY
commit "add Lexer"

# C2 — parser uses Lexer
cat > "$FIX/pkg/parse.py" << 'PY'
from pkg.lexer import Lexer
class Parser:
    def __init__(self, src):
        self.lexer = Lexer(src)
    def parse(self):
        return self.lexer.tokens()
PY
commit "add Parser"

# C3 — tests of Parser/Lexer
cat > "$FIX/tests/test_parse.py" << 'PY'
from pkg.parse import Parser
from pkg.lexer import Lexer
def test_parse_splits():
    assert Parser("a b").parse() == ["a", "b"]
def test_lexer():
    assert Lexer("x y").tokens() == ["x", "y"]
PY
commit "add tests"

# uncoupled util + docs land in the squash too (separate track / aside)
cat > "$FIX/pkg/util.py" << 'PY'
def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x
PY
cat > "$FIX/README.md" << 'MD'
# demo parser
MD
commit "add util and readme"

C0=$(git -C "$FIX" rev-parse HEAD~4)
C1=$(git -C "$FIX" rev-parse HEAD~3)
C2=$(git -C "$FIX" rev-parse HEAD~2)
C3=$(git -C "$FIX" rev-parse HEAD~1)
HEAD=$(git -C "$FIX" rev-parse HEAD)

echo "----- default emit is a mailbox, not a report -----"
OUT=$("${C[@]}" -C "$FIX" "$C0" "$HEAD")
echo "$OUT" | head -n 24
echo "$OUT" | grep -q "^From " && assert "mbox From line" true
echo "$OUT" | grep -q "Subject: \[PATCH" && assert "mbox PATCH subjects" true
echo "$OUT" | grep -q "PRELUDE: lexer.py" && assert "lexer is PRELUDE patch" true
echo "$OUT" | grep -q "PAYOFF: test_parse.py" && assert "tests are PAYOFF patch" true
echo "$OUT" | grep -q "ASIDE: README.md" && assert "readme is ASIDE patch" true
echo "$OUT" | grep -q "^reel .*acts" && assert "default is NOT porcelain" false || assert "default is NOT porcelain" true

python3 - "$OUT" << 'PY'
import sys, re
text = sys.argv[1]
subs = re.findall(r"Subject: \[PATCH \d+/\d+\] (\w+): (\S+)", text)
def idx(token):
    for i, (_kind, name) in enumerate(subs):
        if token in name:
            return i
    raise SystemExit(f"missing {token} in {subs}")
i_lex, i_par, i_test = idx("lexer.py"), idx("parse.py"), idx("test_parse.py")
print(f"  order lexer={i_lex} parse={i_par} tests={i_test} subjects={subs}")
sys.exit(0 if i_lex < i_par < i_test else 1)
PY
assert "lexer < parse < tests in mailbox" true

echo "----- --report still names the plot -----"
REP=$("${C[@]}" -C "$FIX" --report "$C0" "$HEAD")
echo "$REP" | head -n 16
echo "$REP" | grep -q "PRELUDE" && assert "report has PRELUDE" true
echo "$REP" | grep -q "PAYOFF" && assert "report has PAYOFF" true

echo "----- --against original 3 story commits (drop util) -----"
AG=$("${C[@]}" -C "$FIX" --against "$C0" "$C3")
echo "$AG" | tail -n 8
python3 - "$AG" << 'PY'
import sys, re
text = sys.argv[1]
m = re.search(r"mean_jaccard=([0-9.]+)", text)
if not m:
    sys.exit(1)
print("  mean_jaccard", m.group(1))
sys.exit(0 if float(m.group(1)) >= 0.66 else 1)
PY
assert "against recovers story commits" true

echo "----- -o DIR --verify (git am reconstitutes TO) -----"
"${C[@]}" -C "$FIX" -o "$SPLIT" --verify "$C0" "$HEAD"
assert "split patches written" test -f "$SPLIT"/0001-PRELUDE-lexer.py.patch
ls "$SPLIT"/*.patch >/dev/null
assert "patches written" true
# no APPLY.txt — format-patch style
assert "no APPLY.txt" test ! -f "$SPLIT/APPLY.txt"

echo "----- --check on clean fixture squash (no spoil) -----"
set +e
"${C[@]}" -C "$FIX" --check "$C0" "$HEAD" >/dev/null
RC=$?
set -e
assert "check exit 0 on clean story" test "$RC" -eq 0

echo "----- stdin spoil --check -----"
set +e
"${C[@]}" --stdin --check >/dev/null << 'DIFF'
diff --git a/src/mixed.py b/src/mixed.py
new file mode 100644
index 0000000..1
--- /dev/null
+++ b/src/mixed.py
@@ -0,0 +1,8 @@
+class Widget:
+    def run(self):
+        return 1
+def test_widget():
+    assert Widget().run() == 1
DIFF
RC=$?
set -e
assert "spoil --check exits 1" test "$RC" -eq 1

echo "======== 4. dogfood ========"
SITBONE=/Users/annenpolka/ghq/github.com/annenpolka/sitbone
KIZU=/Users/annenpolka/ghq/github.com/annenpolka/kizu
TENAOSHI=/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi

if [[ -d "$SITBONE/.git" ]]; then
  echo "----- sitbone e9b0f75 default mailbox -----"
  OUT=$("${C[@]}" -C "$SITBONE" e9b0f75)
  echo "$OUT" | grep "^Subject:" || true
  python3 - "$OUT" << 'PY'
import sys, re
text = sys.argv[1]
assert text.startswith("From "), "not a mailbox"
subs = re.findall(r"Subject: \[PATCH \d+/\d+\] (\w+): (\S+)", text)
kinds = [k for k, _ in subs]
files = [f for _, f in subs]
blob = " ".join(files)
assert "PresenceArbiter.swift" in blob
assert "PresenceHysteresisTests.swift" in blob
i_prod = next(i for i, f in enumerate(files) if "PresenceArbiter.swift" in f and "Tests" not in f)
i_test = next(i for i, f in enumerate(files) if "PresenceHysteresisTests.swift" in f)
assert kinds[i_prod] == "PRELUDE"
assert kinds[i_test] == "PAYOFF"
assert i_prod < i_test
i_aside = next(i for i, f in enumerate(files) if "PresenceArbiterTests.swift" in f)
assert kinds[i_aside] == "ASIDE"
assert i_test < i_aside, (subs, "ASIDE must not interrupt PRELUDE→PAYOFF")
print(f"  subjects={subs}")
print(f"  prelude#{i_prod+1} payoff#{i_test+1} aside#{i_aside+1} (last)")
PY
  assert "sitbone mailbox prelude then payoff" true
  set +e
  "${C[@]}" -C "$SITBONE" --check e9b0f75 >/dev/null
  RC=$?
  set -e
  assert "sitbone --check 0 (no spoil)" test "$RC" -eq 0
  SDIR="$(mktemp -d "${TMPDIR:-/tmp}/reel-sitbone.XXXXXX")"
  set +e
  "${C[@]}" -C "$SITBONE" -o "$SDIR" --verify e9b0f75
  RC=$?
  set -e
  echo "  sitbone patches:" "$(ls "$SDIR"/*.patch 2>/dev/null | xargs -n1 basename)"
  assert "sitbone --verify git am" test "$RC" -eq 0
  rm -rf "$SDIR"
fi

if [[ -d "$KIZU/.git" ]]; then
  echo "----- kizu 04adde1 (docs ASIDE, lock ASIDE, spoil --check) -----"
  REP=$("${C[@]}" -C "$KIZU" --report 04adde1)
  echo "$REP" | head -n 24
  python3 - "$REP" << 'PY'
import sys
text = sys.argv[1]
asides = [ln for ln in text.splitlines() if "ASIDE" in ln]
blob = "\n".join(asides)
assert "Cargo.lock" in blob
assert "README.md" in blob
assert "docs/SPEC.md" in blob or "SPEC.md" in blob
assert "js_ts" in text or "language.rs" in text
print("  asides include lock+docs; language still in plot")
PY
  assert "kizu jsx docs/lock are ASIDE" true
  set +e
  "${C[@]}" -C "$KIZU" --check 04adde1 >/dev/null
  RC=$?
  set -e
  assert "kizu jsx --check 1 (in-file test spoil)" test "$RC" -eq 1

  echo "----- kizu edf2de9 mailbox: types before revert -----"
  OUT=$("${C[@]}" -C "$KIZU" edf2de9)
  echo "$OUT" | grep "^Subject:" || true
  python3 - "$OUT" << 'PY'
import sys, re
text = sys.argv[1]
subs = re.findall(r"Subject: \[PATCH \d+/\d+\] (\w+): (\S+)", text)
def idx(tok):
    for i, (_k, f) in enumerate(subs):
        if tok in f:
            return i
    return None
i_types = idx("types.rs")
i_revert = idx("revert.rs")
assert i_types is not None and i_revert is not None, subs
assert i_types < i_revert, (i_types, i_revert, subs)
print(f"  types#{i_types+1} before revert#{i_revert+1} n={len(subs)}")
PY
  assert "kizu types.rs before revert.rs" true
fi

if [[ -d "$TENAOSHI/.git" ]]; then
  echo "----- tenaoshi 4878b75 mailbox (oracle tweak) -----"
  OUT=$("${C[@]}" -C "$TENAOSHI" 4878b75)
  echo "$OUT" | grep "^Subject:" || true
  echo "$OUT" | grep -q "ASIDE"
  assert "tenaoshi has asides" true
fi

echo
echo "======== demo $PASS passed, $FAIL failed ========"
test "$FAIL" -eq 0
