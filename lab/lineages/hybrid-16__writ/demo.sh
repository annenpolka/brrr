#!/usr/bin/env bash
# Exercise writ. Exit 0 only if every case holds.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
chmod +x "$ROOT/writ" "$ROOT/writ.py"
PY="${PYTHON:-python3}"
WRIT=("$PY" "$ROOT/writ.py")
passed=0
failed=0
HOME_NOW="$(python3 -c 'from pathlib import Path; print(Path.home())')"

ok() { passed=$((passed + 1)); echo "ok  $1"; }
fail() { failed=$((failed + 1)); echo "FAIL  $1" >&2; echo "      $2" >&2; }

assert_contains() {
  local hay="$1" needle="$2" label="$3"
  if [[ "$hay" == *"$needle"* ]]; then ok "$label"
  else fail "$label" "missing: $needle"
  fi
}
assert_absent() {
  local hay="$1" needle="$2" label="$3"
  if [[ "$hay" != *"$needle"* ]]; then ok "$label"
  else fail "$label" "should not contain: $needle"
  fi
}
assert_exit() {
  local got="$1" want="$2" label="$3"
  if [[ "$got" -eq "$want" ]]; then ok "$label"
  else fail "$label" "exit want=$want got=$got"
  fi
}
assert_eq() {
  local got="$1" want="$2" label="$3"
  if [[ "$got" == "$want" ]]; then ok "$label"
  else fail "$label" "want=$want got=$got"
  fi
}
assert_empty() {
  local hay="$1" label="$2"
  if [[ -z "$hay" ]]; then ok "$label"
  else fail "$label" "stdout not empty: ${hay:0:200}"
  fi
}

json_field() {
  "$PY" -c 'import json,sys; d=json.load(sys.stdin); print(d.get(sys.argv[1],"") or "")' "$1"
}

echo "======== 0. self-test + unittest ========"
set +e
out="$("${WRIT[@]}" --self-test 2>&1)"
rc=$?
set -e
assert_exit "$rc" 0 "self-test"
assert_contains "$out" "self-test ok" "self-test ok line"
set +e
uout="$("$PY" -m unittest discover -s tests -q 2>&1)"
urc=$?
set -e
assert_exit "$urc" 0 "unittest discover"
[[ -n "$uout" ]] && echo "$uout"

FIX="$(mktemp -d "${TMPDIR:-/tmp}/writ-demo-XXXX")"
cleanup() { rm -rf "$FIX"; }
trap cleanup EXIT

init_repo() {
  local d="$1"
  mkdir -p "$d"
  git -C "$d" init -q
  git -C "$d" config user.email writ@lab
  git -C "$d" config user.name writ
  git -C "$d" config commit.gpgsign false
}

CMD='python3 -m unittest discover -q'

echo "======== 1. portable lock: EXPECTED-OPEN vs ACTUAL-OPEN (not cinch) ========"
init_repo "$FIX/open"
cat > "$FIX/open/adder.py" <<'PY'
def add(a, b):
    return 0
PY
cat > "$FIX/open/test.py" <<'PY'
import unittest, adder
class T(unittest.TestCase):
    def test_sum(self):
        self.assertEqual(adder.add(2, 3), 5)
PY
git -C "$FIX/open" add -A && git -C "$FIX/open" commit -qm 'red'
cat > "$FIX/open/adder.py" <<'PY'
def add(a, b):
    print("debug")
    return a + b
PY
set +e
j="$("${WRIT[@]}" -C "$FIX/open" --json --cmd "$CMD" 2>/dev/null)"
rc=$?
set -e
assert_eq "$(printf '%s' "$j" | json_field status)" "LOCKED" "open lock status"
assert_eq "$(printf '%s' "$j" | json_field lock)" "LOCKED-and-EXPECTED-OPEN vs LOCKED-and-ACTUAL-OPEN" "open pair"
assert_exit "$rc" 0 "portable lock exit 0"
assert_eq "$(printf '%s' "$j" | "$PY" -c 'import json,sys; print(json.load(sys.stdin)["wheat"])')" "[]" "no wheat (not cinch)"
assert_eq "$(printf '%s' "$j" | "$PY" -c 'import json,sys; print(json.load(sys.stdin)["hunks"])')" "[]" "no hunks (not cinch)"
set +e
human="$("${WRIT[@]}" -C "$FIX/open" --cmd "$CMD" 2>/dev/null)"
set -e
assert_contains "$human" "not a cinch" "human names not-cinch"
assert_absent "$human" "wheat" "human has no wheat peel"

echo "======== 2. LOCKED-and-ACTUAL-BOUND (gage would say OPEN) ========"
init_repo "$FIX/actual"
python3 - "$FIX/actual" "$HOME_NOW" <<'PY'
import pathlib, sys
d, home = pathlib.Path(sys.argv[1]), sys.argv[2]
(d / "who.py").write_text(f"def who():\n    return {home!r}\n")
(d / "test_who.py").write_text(
    "import unittest, who\n"
    "class T(unittest.TestCase):\n"
    "    def test_tmp(self):\n"
    "        self.assertEqual(who.who(), '/tmp/x')\n"
)
PY
git -C "$FIX/actual" add -A && git -C "$FIX/actual" commit -qm 'leaky home'
cat > "$FIX/actual/who.py" <<'PY'
def who():
    return '/tmp/x'
PY
set +e
j="$("${WRIT[@]}" -C "$FIX/actual" --json --cmd "$CMD" 2>/dev/null)"
rc=$?
set -e
assert_eq "$(printf '%s' "$j" | json_field status)" "LOCKED" "actual-bound status"
assert_eq "$(printf '%s' "$j" | json_field lock)" "LOCKED-and-EXPECTED-OPEN vs LOCKED-and-ACTUAL-BOUND" "actual-bound pair"
assert_eq "$(printf '%s' "$j" | json_field host)" "ACTUAL" "host ACTUAL"
assert_eq "$(printf '%s' "$j" | json_field apply)" "APPLY" "OPEN expected still APPLY"
assert_exit "$rc" 1 "actual-bound default exit 1"
set +e
aj="$("${WRIT[@]}" -C "$FIX/actual" --apply --json --cmd "$CMD" 2>/dev/null)"
arc=$?
fix="$("${WRIT[@]}" -C "$FIX/actual" --fixture --cmd "$CMD" 2>/dev/null)"
frc=$?
set -e
assert_exit "$arc" 0 "--apply 0 (OPEN expected ∪ ACTUAL-BOUND)"
assert_exit "$frc" 0 "--fixture 0 (this host produced the fail)"
assert_contains "$fix" "HOME" "fixture names HOME"
assert_absent "$fix" "false" "fixture is not false"

echo "======== 3. LOCKED-and-EXPECTED-BOUND (laptop golden) ========"
init_repo "$FIX/expected"
cat > "$FIX/expected/who.py" <<'PY'
def who():
    return '/tmp/x'
PY
cat > "$FIX/expected/test_who.py" <<'PY'
import unittest, who
class T(unittest.TestCase):
    def test_alice(self):
        self.assertEqual(who.who(), '/Users/alice/proj')
PY
git -C "$FIX/expected" add -A && git -C "$FIX/expected" commit -qm 'tmp'
cat > "$FIX/expected/who.py" <<'PY'
def who():
    return '/Users/alice/proj'
PY
set +e
j="$("${WRIT[@]}" -C "$FIX/expected" --json --cmd "$CMD" 2>/dev/null)"
rc=$?
set -e
assert_eq "$(printf '%s' "$j" | json_field lock)" "LOCKED-and-EXPECTED-BOUND vs LOCKED-and-ACTUAL-OPEN" "expected-bound pair"
assert_eq "$(printf '%s' "$j" | json_field host)" "NEITHER" "alice lock host NEITHER"
assert_eq "$(printf '%s' "$j" | json_field apply)" "SKIP" "alice expected SKIP here"
assert_exit "$rc" 1 "expected-bound default exit 1"
set +e
arc=0
"${WRIT[@]}" -C "$FIX/expected" --apply --cmd "$CMD" >/dev/null 2>&1 || arc=$?
frc=0
fout="$("${WRIT[@]}" -C "$FIX/expected" --fixture --cmd "$CMD" 2>/dev/null)" || frc=$?
set -e
assert_exit "$arc" 1 "--apply 1 (no legal side)"
assert_exit "$frc" 1 "--fixture 1 (not ACTUAL)"
assert_eq "$(printf '%s' "$fout" | tr -d '\n')" "false" "fixture false on NEITHER"

echo "======== 4. skip is not a lock; comments are not oaths ========"
init_repo "$FIX/skip"
cat > "$FIX/skip/who.py" <<'PY'
def who():
    return '/tmp/x'
PY
cat > "$FIX/skip/test_who.py" <<'PY'
import os, unittest, who
class T(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("HOME") == "/Users/alice", "alice")
    def test_alice(self):
        self.assertEqual(who.who(), "/Users/alice")
PY
git -C "$FIX/skip" add -A && git -C "$FIX/skip" commit -qm 'tmp'
cat > "$FIX/skip/who.py" <<'PY'
def who():
    return '/Users/alice'
PY
set +e
j="$("${WRIT[@]}" -C "$FIX/skip" --json --cmd "$CMD" 2>/dev/null)"
rc=$?
set -e
assert_eq "$(printf '%s' "$j" | json_field status)" "SKIP" "skip status"
assert_exit "$rc" 0 "skip default exit 0"
set +e
drc=0
"${WRIT[@]}" -C "$FIX/skip" --due --cmd "$CMD" >/dev/null 2>&1 || drc=$?
set -e
assert_exit "$drc" 1 "--due names hidden skip"

init_repo "$FIX/comment"
cat > "$FIX/comment/adder.py" <<'PY'
def add(a, b):
    return 0
PY
cat > "$FIX/comment/test_adder.py" <<'PY'
import unittest, adder
class T(unittest.TestCase):
    def test_sum(self):
        # ran on alice
        self.assertEqual(adder.add(2, 3), 5)
PY
git -C "$FIX/comment" add -A && git -C "$FIX/comment" commit -qm 'red'
cat > "$FIX/comment/adder.py" <<'PY'
def add(a, b):
    return a + b
PY
set +e
j="$("${WRIT[@]}" -C "$FIX/comment" --json --cmd "$CMD" 2>/dev/null)"
set -e
assert_eq "$(printf '%s' "$j" | json_field lock)" "LOCKED-and-EXPECTED-OPEN vs LOCKED-and-ACTUAL-OPEN" "comment not an oath"

echo "======== 5. BROKEN / LOOSE / CLEAN / --clearance ========"
init_repo "$FIX/broken"
cat > "$FIX/broken/adder.py" <<'PY'
def add(a, b):
    return a + b
PY
cat > "$FIX/broken/test_adder.py" <<'PY'
import unittest, adder
class T(unittest.TestCase):
    def test_sum(self):
        self.assertEqual(adder.add(2, 3), 5)
PY
git -C "$FIX/broken" add -A && git -C "$FIX/broken" commit -qm 'green'
cat > "$FIX/broken/test_adder.py" <<'PY'
import unittest, adder
class T(unittest.TestCase):
    def test_sum(self):
        self.assertEqual(adder.add(2, 3), 99)
PY
set +e
j="$("${WRIT[@]}" -C "$FIX/broken" --json --cmd "$CMD" 2>/dev/null)"
rc=$?
set -e
assert_eq "$(printf '%s' "$j" | json_field status)" "BROKEN" "test-only red BROKEN"
assert_exit "$rc" 3 "BROKEN exit 3"

init_repo "$FIX/loose"
cat > "$FIX/loose/adder.py" <<'PY'
def add(a, b):
    return a + b
PY
cat > "$FIX/loose/test_adder.py" <<'PY'
import unittest, adder
class T(unittest.TestCase):
    def test_sum(self):
        self.assertEqual(adder.add(2, 3), 5)
PY
git -C "$FIX/loose" add -A && git -C "$FIX/loose" commit -qm 'green'
cat > "$FIX/loose/adder.py" <<'PY'
def add(a, b):
    # note
    return a + b
PY
set +e
j="$("${WRIT[@]}" -C "$FIX/loose" --json --cmd "$CMD" 2>/dev/null)"
rc=$?
set -e
assert_eq "$(printf '%s' "$j" | json_field status)" "LOOSE" "comment prod LOOSE"
assert_exit "$rc" 2 "LOOSE exit 2"

set +e
cout="$("${WRIT[@]}" -C "$FIX/open" --clearance --cmd "$CMD" 2>/dev/null)"
crc=$?
bout="$("${WRIT[@]}" -C "$FIX/actual" --clearance --cmd "$CMD" 2>/dev/null)"
brc=$?
set -e
assert_empty "$cout" "--clearance empty on OPEN vs OPEN"
assert_exit "$crc" 0 "--clearance portable exit 0"
assert_contains "$bout" "LOCKED-and-ACTUAL-BOUND" "--clearance prints ACTUAL-BOUND"
assert_exit "$brc" 1 "--clearance bound exit 1"

echo "======== 6. dogfood sitbone / kizu --list ========"
for repo in /Users/annenpolka/ghq/github.com/annenpolka/sitbone /Users/annenpolka/ghq/github.com/annenpolka/kizu; do
  name="$(basename "$repo")"
  set +e
  lst="$("${WRIT[@]}" -C "$repo" --list --json 2>/dev/null)"
  lrc=$?
  set -e
  assert_exit "$lrc" 0 "$name --list exit 0"
  nprod="$(printf '%s' "$lst" | "$PY" -c 'import json,sys; print(len(json.load(sys.stdin)["production_changed"]))')"
  assert_eq "$nprod" "0" "$name no production source diff"
  agents="$(printf '%s' "$lst" | "$PY" -c 'import json,sys; print(any(p["path"]=="AGENTS.md" and p["role"]=="production" for p in json.load(sys.stdin)["plan"]))')"
  assert_eq "$agents" "False" "$name AGENTS.md is not production"
done

echo "======== 7. this worktree --list ========"
set +e
self="$("${WRIT[@]}" --list --json 2>/dev/null)"
set -e
nlab="$(printf '%s' "$self" | "$PY" -c 'import json,sys; print(sum(1 for p in json.load(sys.stdin)["production_changed"] if p.startswith("lab/")))')"
assert_eq "$nlab" "0" "lab/ is not production of this tool"
echo "$self" | "$PY" -c 'import json,sys; d=json.load(sys.stdin); print("self prod", d["production_changed"]); print("self tests", d["tests_kept"][:8])'

echo
echo "passed=$passed failed=$failed"
if [[ "$failed" -ne 0 ]]; then
  exit 1
fi
exit 0
