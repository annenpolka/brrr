#!/usr/bin/env bash
# demo.sh — must exit 0. Content-pin seed, not first-locator.
set -euo pipefail
cd "$(dirname "$0")"
chmod +x ./seed

echo "== unit tests =="
python3 -m unittest tests.test_seed -q

echo
echo "== refuses cwd tree-walk =="
set +e
./seed >/dev/null
rc=$?
set -e
test "$rc" -eq 2

echo
echo "== exact arm of nested return (argv seed, scan that file) =="
./seed fixtures/nested.py:13 --exact --explain

echo
echo "== rg -nH locators seed AND scan the file, not the grep lines =="
printf '%s\n' 'fixtures/guards.rs:11:    let p = (bytes.len() - 5) / 2;' \
  | ./seed --explain

echo
echo "== rg -l file list needs --same-as =="
printf '%s\n' fixtures/nested.py | ./seed --same-as fixtures/nested.py:13 --exact --tsv

echo
echo "== unique LINE:text pin recovers the file =="
printf '%s\n' '13:    return "denied"' \
  | ./seed --exact --tsv fixtures/nested.py

echo
echo "== bag of stacks refuses (not first locator) =="
set +e
bag_err="$(printf '%s\n' \
  'fixtures/bag.py:6:        return None' \
  'fixtures/bag.py:8:        return None' \
  | ./seed --explain 2>&1)"
bag_rc=$?
set -e
printf '%s\n' "$bag_err"
test "$bag_rc" -eq 2
printf '%s\n' "$bag_err" | grep -q '2 stacks'
printf '%s\n' "$bag_err" | grep -q -- '--first'

echo
echo "== --hits keeps only locator lines that rhyme =="
printf '%s\n' '13:    return "denied"' '6:        audit.warn("missing")' \
  | ./seed fixtures/nested.py:8 --hits --tsv

echo
echo "== try body is not the except arm =="
./seed fixtures/nested.py:10 --exact --tsv

echo
echo "== swift guard body, not guard-else =="
./seed fixtures/sample.swift:6 --explain

KIZU="${KIZU:-$HOME/ghq/github.com/annenpolka/kizu}"
if [[ -f "$KIZU/src/git/parse.rs" ]]; then
  echo
  echo "== kizu parse.rs:60 rhyme from rg -n (no -H); recover file, scan, not filter =="
  ROOT="$(pwd)"
  kizu_out="$(cd "$KIZU" && rg -n 'let b_side' src/git/parse.rs | "$ROOT/seed" --explain)"
  printf '%s\n' "$kizu_out" | sed -n '1,40p'
  printf '%s\n' "$kizu_out" | grep -q 'let b_side'
  printf '%s\n' "$kizu_out" | grep -q 'bytes_to_path'
  printf '%s\n' "$kizu_out" | grep -v 'here   }' | grep -q 'let b_side'

  echo
  echo "== kizu return None; bag is not the quoted arm =="
  set +e
  none_err="$(cd "$KIZU" && rg -n 'return None;' src/git/parse.rs | "$ROOT/seed" --explain 2>&1)"
  none_rc=$?
  set -e
  printf '%s\n' "$none_err" | sed -n '1,20p'
  test "$none_rc" -eq 2
  printf '%s\n' "$none_err" | grep -q 'stacks'
  printf '%s\n' "$none_err" | grep -q ':34' || true

  echo
  echo "== kizu --same-as :60 on the bag restores gold =="
  gold_out="$(cd "$KIZU" && rg -n 'return None;' src/git/parse.rs | "$ROOT/seed" --same-as :60 --explain)"
  printf '%s\n' "$gold_out" | sed -n '1,24p'
  printf '%s\n' "$gold_out" | grep -q 'let b_side'
  printf '%s\n' "$gold_out" | grep -q 'bytes_to_path'
  printf '%s\n' "$gold_out" | grep -q 'parse.rs:60'
fi

echo
echo "demo ok"
