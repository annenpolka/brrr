#!/usr/bin/env bash
# End-to-end demo: unit tests + four fixture statuses + --list on a real repo.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
ALIBI=(python3 "$ROOT/alibi.py")
export GIT_AUTHOR_NAME=alibi GIT_AUTHOR_EMAIL=alibi@demo
export GIT_COMMITTER_NAME=alibi GIT_COMMITTER_EMAIL=alibi@demo

echo "======== 1. unit tests ========"
python3 -m unittest discover -s tests -q
echo "unit tests: OK"

DEMO="$ROOT/demo-tmp"
rm -rf "$DEMO"
mkdir -p "$DEMO"

init_repo() {
  local d="$1"
  mkdir -p "$d"
  git -C "$d" init -q
  git -C "$d" config user.email alibi@demo
  git -C "$d" config user.name alibi
  git -C "$d" config commit.gpgsign false
}

expect_status() {
  local label="$1" want="$2" dir="$3"
  local json out code=0
  set +e
  json="$("${ALIBI[@]}" -C "$dir" --json --cmd "python3 -m unittest discover -q" 2>&1)"
  code=$?
  set -e
  out="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["status"])' "$json")"
  echo "---- $label ----"
  python3 -c '
import json,sys
r=json.loads(sys.argv[1])
print("status", r["status"])
print("prod ", r["production_changed"])
print("witnesses", r["witnesses"])
print("NEW   ", r["new_run"]["exit_code"] if r["new_run"] else None, "splice", r["splice_run"]["exit_code"] if r["splice_run"] else None)
' "$json"
  if [[ "$out" != "$want" ]]; then
    echo "EXPECTED $want got $out (exit $code)" >&2
    echo "$json" >&2
    exit 1
  fi
}

echo "======== 2. LOCKED fixture ========"
init_repo "$DEMO/locked"
cat > "$DEMO/locked/adder.py" << 'PY'
def add(a, b):
    return 0
PY
cat > "$DEMO/locked/test_adder.py" << 'PY'
import unittest, adder
class T(unittest.TestCase):
    def test_sum(self):
        self.assertEqual(adder.add(2, 3), 5)
PY
git -C "$DEMO/locked" add -A
git -C "$DEMO/locked" commit -qm 'red add'
cat > "$DEMO/locked/adder.py" << 'PY'
def add(a, b):
    return a + b
PY
expect_status LOCKED LOCKED "$DEMO/locked"

echo "======== 3. LOOSE fixture (comment-only) ========"
init_repo "$DEMO/loose"
cat > "$DEMO/loose/adder.py" << 'PY'
def add(a, b):
    return a + b
PY
cat > "$DEMO/loose/test_adder.py" << 'PY'
import unittest, adder
class T(unittest.TestCase):
    def test_sum(self):
        self.assertEqual(adder.add(2, 3), 5)
PY
git -C "$DEMO/loose" add -A
git -C "$DEMO/loose" commit -qm 'green add'
cat > "$DEMO/loose/adder.py" << 'PY'
def add(a, b):
    # definitely correct
    return a + b
PY
expect_status LOOSE LOOSE "$DEMO/loose"

echo "======== 4. CLEAN fixture (test-only edit) ========"
init_repo "$DEMO/clean"
cat > "$DEMO/clean/adder.py" << 'PY'
def add(a, b):
    return a + b
PY
cat > "$DEMO/clean/test_adder.py" << 'PY'
import unittest, adder
class T(unittest.TestCase):
    def test_sum(self):
        self.assertEqual(adder.add(2, 3), 5)
PY
git -C "$DEMO/clean" add -A
git -C "$DEMO/clean" commit -qm 'green'
echo '# extra note' >> "$DEMO/clean/test_adder.py"
expect_status CLEAN CLEAN "$DEMO/clean"

echo "======== 5. BROKEN fixture (prod + red tests) ========"
init_repo "$DEMO/broken"
cat > "$DEMO/broken/adder.py" << 'PY'
def add(a, b):
    return a + b
PY
cat > "$DEMO/broken/test_adder.py" << 'PY'
import unittest, adder
class T(unittest.TestCase):
    def test_sum(self):
        self.assertEqual(adder.add(2, 3), 5)
PY
git -C "$DEMO/broken" add -A
git -C "$DEMO/broken" commit -qm 'green'
cat > "$DEMO/broken/adder.py" << 'PY'
def add(a, b):
    # also change production so alibi has something to splice
    return a + b
PY
cat > "$DEMO/broken/test_adder.py" << 'PY'
import unittest, adder
class T(unittest.TestCase):
    def test_sum(self):
        self.assertEqual(adder.add(2, 3), 99)
PY
expect_status BROKEN BROKEN "$DEMO/broken"

echo "======== 5b. mixed --per-path ========"
init_repo "$DEMO/mixed"
cat > "$DEMO/mixed/adder.py" << 'PY'
def add(a, b):
    return 0
PY
cat > "$DEMO/mixed/util.py" << 'PY'
def ping():
    return 'ok'
PY
cat > "$DEMO/mixed/test_adder.py" << 'PY'
import unittest, adder
class T(unittest.TestCase):
    def test_sum(self):
        self.assertEqual(adder.add(2, 3), 5)
PY
git -C "$DEMO/mixed" add -A
git -C "$DEMO/mixed" commit -qm 'red add'
cat > "$DEMO/mixed/adder.py" << 'PY'
def add(a, b):
    return a + b
PY
cat > "$DEMO/mixed/util.py" << 'PY'
def ping():
    # comment only
    return 'ok'
PY
set +e
mix_json="$("${ALIBI[@]}" -C "$DEMO/mixed" --json --per-path --cmd "python3 -m unittest discover -q" 2>&1)"
mix_code=$?
set -e
python3 -c '
import json,sys
r=json.loads(sys.argv[1])
print("status", r["status"])
print("per_path", r["per_path"])
assert r["status"]=="LOCKED", r["status"]
assert r["per_path"].get("adder.py")=="LOCKED", r["per_path"]
assert r["per_path"].get("util.py")=="LOOSE", r["per_path"]
' "$mix_json"
echo "per-path mixed: OK (exit $mix_code)"

echo "======== 5c. docs-only dirty tree is CLEAN ========"
init_repo "$DEMO/docs"
cat > "$DEMO/docs/adder.py" << 'PY'
def add(a, b):
    return a + b
PY
cat > "$DEMO/docs/test_adder.py" << 'PY'
import unittest, adder
class T(unittest.TestCase):
    def test_sum(self):
        self.assertEqual(adder.add(2, 3), 5)
PY
cat > "$DEMO/docs/README.md" << 'MD'
# v1
MD
git -C "$DEMO/docs" add -A
git -C "$DEMO/docs" commit -qm 'green'
echo '# dirty docs' > "$DEMO/docs/README.md"
expect_status DOCS_CLEAN CLEAN "$DEMO/docs"

echo "======== 6. --list on kizu (file classification, no test run) ========"
KIZU="/Users/annenpolka/ghq/github.com/annenpolka/kizu"
if [[ -d "$KIZU/.git" ]]; then
  "${ALIBI[@]}" -C "$KIZU" HEAD --list 2>&1 | head -40
else
  echo "(kizu not present, skip)"
fi

echo "======== 7. self --list ========"
"${ALIBI[@]}" -C "$ROOT" HEAD --list 2>&1 | head -30

echo "======== demo OK ========"
