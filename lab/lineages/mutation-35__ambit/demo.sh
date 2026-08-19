#!/usr/bin/env bash
# demo.sh — must exit 0. Exercises stdin-locator scan, not a screenshot.
set -euo pipefail
cd "$(dirname "$0")"
chmod +x ./ambit

echo "== unit tests =="
python3 -m unittest tests.test_ambit -q

echo
echo "== refuses cwd tree-walk =="
set +e
./ambit 'user.locked' >/dev/null
rc=$?
set -e
test "$rc" -eq 2

echo
echo "== argv file (explicit scan) =="
./ambit 'user.locked' fixtures/nested.py --explain

echo
echo "== rg -nH locators name the file; scan, do not filter lines =="
# the rg hit is the inverted !starts_with arm. ambit still emits let p.
printf '%s\n' 'fixtures/guards.rs:8:        if !bytes.starts_with(b"a/") {' \
  | ./ambit 'starts_with(a/)' --explain

echo
echo "== rg -l file list =="
printf '%s\n' fixtures/nested.py | ./ambit 'user.locked' --tsv | head -n 5

echo
echo "== LINE:text recovers the file from git pins (no FILE operand) =="
printf '%s\n' '13:    return "denied"' '34:            return "drained"' \
  | ./ambit 'user.locked' --tsv | head -n 3

echo
echo "== LINE:text + FILE operand (rg FILE without -H) =="
printf '%s\n' '13:    return "denied"' '34:            return "drained"' \
  | ./ambit 'user.locked' fixtures/nested.py --tsv

echo
echo "== --hits keeps only locator lines =="
printf '%s\n' '13:    return "denied"' '34:            return "drained"' \
  | ./ambit 'user.locked' fixtures/nested.py --hits --tsv

echo
echo "== rust fallthrough given a/ =="
./ambit 'starts_with(a/)' fixtures/guards.rs --explain

echo
echo "== swift guard isEnabled =="
./ambit 'isEnabled' fixtures/sample.swift --explain

echo
echo "== unapplied patch filtered by condition =="
./ambit 'can_delete' --diff fixtures/sample.diff --group

KIZU="${KIZU:-$HOME/ghq/github.com/annenpolka/kizu}"
if [[ -f "$KIZU/src/git/parse.rs" ]]; then
  echo
  echo "== kizu parse.rs: rg FILE | ambit recovers the file, scans, not filters =="
  ROOT="$(pwd)"
  kizu_out="$(cd "$KIZU" && rg -n 'return None;' src/git/parse.rs \
    | "$ROOT/ambit" --kind given 'a/' --explain)"
  printf '%s\n' "$kizu_out" | sed -n '1,28p'
  printf '%s\n' "$kizu_out" | grep -q 'let b_side'
fi

echo
echo "demo ok"
