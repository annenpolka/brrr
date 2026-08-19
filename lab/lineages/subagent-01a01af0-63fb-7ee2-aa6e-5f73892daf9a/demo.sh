#!/usr/bin/env bash
# End-to-end demo. Extra args (e.g. ./demo.sh 0) are ignored.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
chmod +x "$ROOT/tide"
TIDE=("$ROOT/tide")

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
"${TIDE[@]}" --selftest
echo "======== 2. unit tests ========"
python3 -m unittest discover -s tests -q
echo "unit tests: OK"

echo "======== 3. fixture history ========"
FIX="$(mktemp -d "${TMPDIR:-/tmp}/tide-demo.XXXXXX")"
cleanup() { rm -rf "$FIX"; }
trap cleanup EXIT

git -C "$FIX" init -q -b main
git -C "$FIX" config user.name tide
git -C "$FIX" config user.email tide@demo
git -C "$FIX" config commit.gpgsign false
export GIT_AUTHOR_NAME=tide GIT_AUTHOR_EMAIL=tide@demo
export GIT_COMMITTER_NAME=tide GIT_COMMITTER_EMAIL=tide@demo

commit() {
  local date="$1" msg="$2"
  GIT_AUTHOR_DATE="$date" GIT_COMMITTER_DATE="$date" git -C "$FIX" add -A
  GIT_AUTHOR_DATE="$date" GIT_COMMITTER_DATE="$date" git -C "$FIX" commit -q -m "$msg"
}

mkdir -p "$FIX/src" "$FIX/tests" "$FIX/golden" "$FIX/contracts/testcases"

cat > "$FIX/src/app.py" << 'PY'
TIMEOUT = 30
RETRIES = 3
LIMIT = 1
def add(a, b):
    return a + b
PY
cat > "$FIX/tests/test_app.py" << 'PY'
import sys
sys.path.insert(0, "src")
import app
def test_timeout():
    assert app.TIMEOUT == 30
def test_retries():
    assert app.RETRIES == 3
def test_limit():
    assert app.LIMIT == 1
def test_add():
    assert app.add(2, 3) == 5
PY
cat > "$FIX/golden/damage.expected.json" << 'JSON'
{"id": "golden.damage", "metrics": {"damage": 100}}
JSON
cat > "$FIX/contracts/testcases/CTR-008.json" << 'JSON'
{
  "id": "CTR-008",
  "intent": "短くして",
  "input": "hello world",
  "expected_properties": {
    "max_length_ratio": 0.95,
    "contains": ["hello"]
  }
}
JSON
commit "2026-01-01T00:00:00 +0000" "t0: birth"

# BLESS: only the test oracle moves
cat > "$FIX/tests/test_app.py" << 'PY'
import sys
sys.path.insert(0, "src")
import app
def test_timeout():
    assert app.TIMEOUT == 60
def test_retries():
    assert app.RETRIES == 3
def test_limit():
    assert app.LIMIT == 1
def test_add():
    assert app.add(2, 3) == 5
PY
commit "2026-01-02T00:00:00 +0000" "t1: bless timeout 30->60"

# COUPLED drift: production and oracle together
cat > "$FIX/src/app.py" << 'PY'
TIMEOUT = 120
RETRIES = 3
LIMIT = 1
def add(a, b):
    return a + b
PY
cat > "$FIX/tests/test_app.py" << 'PY'
import sys
sys.path.insert(0, "src")
import app
def test_timeout():
    assert app.TIMEOUT == 120
def test_retries():
    assert app.RETRIES == 3
def test_limit():
    assert app.LIMIT == 1
def test_add():
    assert app.add(2, 3) == 5
PY
commit "2026-01-03T00:00:00 +0000" "t2: timeout 60->120 with prod"

# RATCHET LIMIT 1->2->4 coupled
cat > "$FIX/src/app.py" << 'PY'
TIMEOUT = 120
RETRIES = 3
LIMIT = 2
def add(a, b):
    return a + b
PY
cat > "$FIX/tests/test_app.py" << 'PY'
import sys
sys.path.insert(0, "src")
import app
def test_timeout():
    assert app.TIMEOUT == 120
def test_retries():
    assert app.RETRIES == 3
def test_limit():
    assert app.LIMIT == 2
def test_add():
    assert app.add(2, 3) == 5
PY
commit "2026-01-04T00:00:00 +0000" "t3: limit 2"

cat > "$FIX/src/app.py" << 'PY'
TIMEOUT = 120
RETRIES = 3
LIMIT = 4
def add(a, b):
    return a + b
PY
cat > "$FIX/tests/test_app.py" << 'PY'
import sys
sys.path.insert(0, "src")
import app
def test_timeout():
    assert app.TIMEOUT == 120
def test_retries():
    assert app.RETRIES == 3
def test_limit():
    assert app.LIMIT == 4
def test_add():
    assert app.add(2, 3) == 5
PY
commit "2026-01-05T00:00:00 +0000" "t4: limit 4"

# FLIPFLOP retries 3->5->3
cat > "$FIX/src/app.py" << 'PY'
TIMEOUT = 120
RETRIES = 5
LIMIT = 4
def add(a, b):
    return a + b
PY
cat > "$FIX/tests/test_app.py" << 'PY'
import sys
sys.path.insert(0, "src")
import app
def test_timeout():
    assert app.TIMEOUT == 120
def test_retries():
    assert app.RETRIES == 5
def test_limit():
    assert app.LIMIT == 4
def test_add():
    assert app.add(2, 3) == 5
PY
commit "2026-01-06T00:00:00 +0000" "t5: retries 5"

cat > "$FIX/src/app.py" << 'PY'
TIMEOUT = 120
RETRIES = 3
LIMIT = 4
def add(a, b):
    return a + b
PY
cat > "$FIX/tests/test_app.py" << 'PY'
import sys
sys.path.insert(0, "src")
import app
def test_timeout():
    assert app.TIMEOUT == 120
def test_retries():
    assert app.RETRIES == 3
def test_limit():
    assert app.LIMIT == 4
def test_add():
    assert app.add(2, 3) == 5
PY
commit "2026-01-07T00:00:00 +0000" "t6: retries back to 3"

# JSON golden coupled
cat > "$FIX/src/app.py" << 'PY'
TIMEOUT = 120
RETRIES = 3
LIMIT = 4
DAMAGE = 200
def add(a, b):
    return a + b
PY
cat > "$FIX/golden/damage.expected.json" << 'JSON'
{"id": "golden.damage", "metrics": {"damage": 200}}
JSON
commit "2026-01-08T00:00:00 +0000" "t7: damage 100->200"

# Stimulus-only: change input, not expected_properties (naive tracks this)
cat > "$FIX/contracts/testcases/CTR-008.json" << 'JSON'
{
  "id": "CTR-008",
  "intent": "短くして",
  "input": "hello world (edited)",
  "expected_properties": {
    "max_length_ratio": 0.95,
    "contains": ["hello"]
  }
}
JSON
commit "2026-01-09T00:00:00 +0000" "t8: edit testcase input only"

# Then actually change the oracle
cat > "$FIX/contracts/testcases/CTR-008.json" << 'JSON'
{
  "id": "CTR-008",
  "intent": "短くして",
  "input": "hello world (edited)",
  "expected_properties": {
    "max_length_ratio": 0.99,
    "contains": ["hello"]
  }
}
JSON
commit "2026-01-10T00:00:00 +0000" "t9: relax max_length_ratio 0.95->0.99"

echo "---- fixture porcelain ----"
"${TIDE[@]}" -C "$FIX" --walk 20
echo "---- fixture json classes ----"
python3 - "$FIX" "${TIDE[0]}" << 'PY'
import json, subprocess, sys
fix, tide = sys.argv[1], sys.argv[2]
raw = subprocess.check_output([tide, "-C", fix, "--json", "--walk", "20"], text=True)
doc = json.loads(raw)
classes = {}
for o in doc["oracles"]:
    classes.setdefault(o["class"], []).append(o)
    if o.get("bless"):
        classes.setdefault("BLESS", []).append(o)
print("n", len(doc["oracles"]))
for k, vs in sorted(classes.items()):
    print(k, [o["lhs"] for o in vs])
want_flip = any(o["lhs"] == "app.RETRIES" and o["class"] == "FLIPFLOP" for o in doc["oracles"])
want_ratchet = any(o["lhs"] == "app.LIMIT" and o["class"] == "RATCHET" for o in doc["oracles"])
want_bless = any(o["lhs"] == "app.TIMEOUT" and o["bless"] for o in doc["oracles"])
want_input = any("input" in o["lhs"] for o in doc["oracles"])
want_ratio = any("max_length_ratio" in o["lhs"] for o in doc["oracles"])
want_damage = any(o["lhs"].endswith("damage") or o["lhs"].endswith(".damage") for o in doc["oracles"])
assert want_flip, "retries flipflop"
assert want_ratchet, "limit ratchet"
assert want_bless, "timeout bless"
assert want_input, "naive json should track stimulus input"
assert want_ratio, "max_length_ratio"
assert want_damage, "golden damage"
print("fixture assertions: OK")
PY

echo "---- --check should fail (BLESS+FLIPFLOP) ----"
set +e
"${TIDE[@]}" -C "$FIX" --check --walk 20 >/dev/null
code=$?
set -e
assert "check-exits-1" test "$code" -eq 1

echo "======== 4. dogfood real repos ========"
dogfood() {
  local name="$1" repo="$2"
  shift 2
  if [[ ! -d "$repo/.git" ]]; then
    echo "  skip $name (missing $repo)"
    return
  fi
  echo "---- $name ----"
  "${TIDE[@]}" -C "$repo" --json --walk 250 "$@" | python3 -c '
import json,sys
d=json.load(sys.stdin)
print("oracles_shown", len(d["oracles"]))
from collections import Counter
c=Counter(o["class"] for o in d["oracles"])
b=sum(1 for o in d["oracles"] if o["bless"])
print("classes", dict(c), "bless", b)
for o in d["oracles"][:8]:
    vals=" → ".join(o["values"][:6])
    print(f"  {o[\"class\"]:<8} bless={int(o[\"bless\"])} {o[\"path\"]} {o[\"lhs\"]} {vals}")
'
}

KIZU=/Users/annenpolka/ghq/github.com/annenpolka/kizu
VOID=/Users/annenpolka/ghq/github.com/annenpolka/voidtrace
TENA=/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi
SIT=/Users/annenpolka/ghq/github.com/annenpolka/sitbone

dogfood kizu "$KIZU" --kind inline
dogfood voidtrace "$VOID"
dogfood tenaoshi "$TENA" --kind json
dogfood sitbone "$SIT" --kind inline

echo "---- kizu: scar-message oracle should drift ----"
if [[ -d "$KIZU/.git" ]]; then
  "${TIDE[@]}" -C "$KIZU" --json --walk 250 --kind inline | python3 -c '
import json,sys
d=json.load(sys.stdin)
hits=[o for o in d["oracles"] if "message" in o["lhs"] and "scar" in "".join(o["values"]).lower()]
print("scar-message oracles", len(hits))
for o in hits:
    print(o["class"], o["path"], o["lhs"])
    print(" ", " → ".join(o["values"]))
ok=any("real scar outside fence" in v for o in hits for v in o["values"])
assert ok, "expected kizu scar-message oracle series"
print("kizu scar-message: OK")
'
fi

echo "---- tenaoshi: max_length_ratio should move ----"
if [[ -d "$TENA/.git" ]]; then
  "${TIDE[@]}" -C "$TENA" --json --walk 50 --kind json | python3 -c '
import json,sys
d=json.load(sys.stdin)
hits=[o for o in d["oracles"] if "max_length_ratio" in o["lhs"] or "max_diff_ratio" in o["lhs"] or "input" in o["lhs"]]
print("tenaoshi interesting", len(hits))
for o in hits[:12]:
    print(o["class"], o["bless"], o["path"], o["lhs"], " → ".join(o["values"][:5]))
ok=any("max_length_ratio" in o["lhs"] and o["class"]!="STABLE" for o in d["oracles"])
assert ok, "expected CTR-008 max_length_ratio change"
print("tenaoshi ratio: OK")
'
fi

echo "---- voidtrace: engineVersion series ----"
if [[ -d "$VOID/.git" ]]; then
  "${TIDE[@]}" -C "$VOID" --json --walk 80 --kind inline | python3 -c '
import json,sys
d=json.load(sys.stdin)
hits=[o for o in d["oracles"] if "engineVersion" in o["lhs"]]
print("engineVersion oracles", len(hits))
for o in hits[:6]:
    print(o["class"], o["path"], " → ".join(o["values"][:8]))
if hits:
    print("voidtrace engineVersion: OK")
else:
    print("voidtrace engineVersion: none (not fatal)")
'
fi

echo
if [[ "$FAIL" -ne 0 ]]; then
  echo "demo FAIL $FAIL  pass $PASS" >&2
  exit 1
fi
echo "demo PASS $PASS"
exit 0
