#!/usr/bin/env bash
# End-to-end demo. Extra args (e.g. ./demo.sh 0) are ignored.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
chmod +x "$ROOT/canto"
C=("$ROOT/canto")

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
FIX="$(mktemp -d "${TMPDIR:-/tmp}/canto-demo.XXXXXX")"
SPLIT="$(mktemp -d "${TMPDIR:-/tmp}/canto-split.XXXXXX")"
cleanup() { rm -rf "$FIX" "$SPLIT"; }
trap cleanup EXIT

git -C "$FIX" init -q -b main
git -C "$FIX" config user.name canto
git -C "$FIX" config user.email canto@demo
git -C "$FIX" config commit.gpgsign false
export GIT_AUTHOR_NAME=canto GIT_AUTHOR_EMAIL=canto@demo
export GIT_COMMITTER_NAME=canto GIT_COMMITTER_EMAIL=canto@demo

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

echo "----- porcelain of the squash (Lexer..HEAD) -----"
OUT=$("${C[@]}" -C "$FIX" --grain file "$C0" "$HEAD")
echo "$OUT"

echo "$OUT" | grep -q "PRELUDE" && assert "squash has PRELUDE" true
echo "$OUT" | grep -q "PAYOFF" && assert "squash has PAYOFF" true
echo "$OUT" | grep -q "ASIDE" && assert "readme is ASIDE" true

python3 - "$OUT" << 'PY'
import sys
text = sys.argv[1]
# act index of lexer < parse < tests
def idx(token):
    for line in text.splitlines():
        if token in line and line.strip().startswith("#"):
            return int(line.split()[0][1:])
    raise SystemExit(f"missing {token}")
i_lex, i_par, i_test = idx("lexer.py"), idx("parse.py"), idx("test_parse.py")
print(f"  order lexer={i_lex} parse={i_par} tests={i_test}")
sys.exit(0 if i_lex < i_par < i_test else 1)
PY
assert "lexer < parse < tests" true

echo "----- --against original 3 story commits (drop util) -----"
AG=$("${C[@]}" -C "$FIX" --grain file --against "$C0" "$C3")
echo "$AG" | tail -n 8
echo "$AG" | grep -q "mean_jaccard=1.0" || echo "$AG" | grep -q "mean_jaccard=1"
# 3 commits vs acts; allow 0.66+ (readme not in this range)
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

echo "----- --split --verify (tree equals TO) -----"
"${C[@]}" -C "$FIX" --grain file --split "$SPLIT" --verify "$C0" "$HEAD" | tail -n 5
assert "split verify ok" test -f "$SPLIT/APPLY.txt"
ls "$SPLIT"/*.patch >/dev/null
assert "patches written" true

echo "----- --check on clean fixture squash (no spoil) -----"
set +e
"${C[@]}" -C "$FIX" --grain file --check "$C0" "$HEAD" >/dev/null
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
dogfood() {
  local name="$1" repo="$2" rev="$3"
  shift 3
  if [[ ! -d "$repo/.git" ]]; then
    echo "  skip $name (no $repo)"
    return 0
  fi
  local out
  out=$("${C[@]}" -C "$repo" --grain file "$rev")
  echo "----- $name $rev -----"
  echo "$out" | head -n 24
  python3 - "$name" "$out" "$@" << 'PY'
import sys
name, text, *needles = sys.argv[1:]
ok = True
for n in needles:
    if n not in text:
        print(f"  missing {n!r} in {name}", file=sys.stderr)
        ok = False
sys.exit(0 if ok else 1)
PY
  assert "dogfood $name needles" true
}

SITBONE=/Users/annenpolka/ghq/github.com/annenpolka/sitbone
KIZU=/Users/annenpolka/ghq/github.com/annenpolka/kizu
TENAOSHI=/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi

if [[ -d "$SITBONE/.git" ]]; then
  OUT=$("${C[@]}" -C "$SITBONE" --grain file e9b0f75)
  echo "----- sitbone e9b0f75 -----"
  echo "$OUT"
  python3 - "$OUT" << 'PY'
import sys
text = sys.argv[1]
def idx(tok):
    for line in text.splitlines():
        if tok in line and line.strip().startswith("#"):
            return int(line.split()[0][1:])
    raise SystemExit("missing " + tok)
i_prod = idx("PresenceArbiter.swift")
i_test = idx("PresenceHysteresisTests.swift")
assert "PRELUDE" in text and "PAYOFF" in text
assert i_prod < i_test
# blank-line sibling test file is not a payoff
for line in text.splitlines():
    if "PresenceArbiterTests.swift" in line:
        assert "ASIDE" in line or "SOLO" in line
print(f"  prelude#{i_prod} payoff#{i_test}")
PY
  assert "sitbone hysteresis is prelude then payoff" true
  set +e
  "${C[@]}" -C "$SITBONE" --check --grain file e9b0f75 >/dev/null
  RC=$?
  set -e
  assert "sitbone --check 0 (no spoil)" test "$RC" -eq 0
fi

if [[ -d "$KIZU/.git" ]]; then
  OUT=$("${C[@]}" -C "$KIZU" --grain file 04adde1)
  echo "----- kizu 04adde1 (docs must be ASIDE, lock ASIDE) -----"
  echo "$OUT" | head -n 30
  python3 - "$OUT" << 'PY'
import sys
text = sys.argv[1]
asides = []
for line in text.splitlines():
    if "ASIDE" in line:
        asides.append(line)
blob = "\n".join(asides)
assert "Cargo.lock" in blob
assert "README.md" in blob
assert "docs/SPEC.md" in blob or "SPEC.md" in blob
# language module is a prelude in the jsx track
assert "js_ts" in text or "language.rs" in text
print("  asides include lock+docs; language still in plot")
PY
  assert "kizu jsx docs/lock are ASIDE" true
  set +e
  "${C[@]}" -C "$KIZU" --check --grain file 04adde1 >/dev/null
  RC=$?
  set -e
  assert "kizu jsx --check 1 (in-file test spoil)" test "$RC" -eq 1

  OUT=$("${C[@]}" -C "$KIZU" --grain file edf2de9)
  echo "----- kizu edf2de9 split git types -----"
  echo "$OUT"
  python3 - "$OUT" << 'PY'
import sys
text = sys.argv[1]
def idx(tok):
    for line in text.splitlines():
        if tok in line and line.strip().startswith("#"):
            return int(line.split()[0][1:])
    return None
i_types = idx("types.rs")
i_revert = idx("revert.rs")
assert i_types is not None and i_revert is not None
assert i_types < i_revert, (i_types, i_revert)
assert "plans/" in text and "ASIDE" in text
print(f"  types#{i_types} before revert#{i_revert}")
PY
  assert "kizu types.rs before revert.rs" true
fi

if [[ -d "$TENAOSHI/.git" ]]; then
  OUT=$("${C[@]}" -C "$TENAOSHI" --grain file 4878b75)
  echo "----- tenaoshi 4878b75 (oracle tweak, mostly asides) -----"
  echo "$OUT"
  echo "$OUT" | grep -q "ASIDE" 
  assert "tenaoshi has asides" true
fi

echo
echo "======== demo $PASS passed, $FAIL failed ========"
test "$FAIL" -eq 0
