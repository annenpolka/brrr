#!/usr/bin/env bash
# demo.sh — must exit 0. Exercises locator-seeded rhyme, not a screenshot.
set -euo pipefail
cd "$(dirname "$0")"
chmod +x ./peal

echo "== unit tests =="
python3 -m unittest tests.test_peal -q

echo
echo "== refuses cwd tree-walk =="
set +e
./peal >/dev/null
rc=$?
set -e
test "$rc" -eq 2

echo
echo "== exact arm of nested return (argv seed, scan that file) =="
./peal fixtures/nested.py:13 --exact --explain

echo
echo "== rg -nH locators seed AND scan the file, not the grep lines =="
# locator is let p; scanning still emits Some(p) which rg never printed.
printf '%s\n' 'fixtures/guards.rs:11:    let p = (bytes.len() - 5) / 2;' \
  | ./peal --explain

echo
echo "== rg -l file list needs --same-as =="
printf '%s\n' fixtures/nested.py | ./peal --same-as fixtures/nested.py:13 --exact --tsv

echo
echo "== LINE:text recovers the file from git pins (no FILE operand) =="
printf '%s\n' '13:    return "denied"' '34:            return "drained"' \
  | ./peal --exact --tsv

echo
echo "== LINE:text + FILE operand (rg FILE without -H) =="
printf '%s\n' '13:    return "denied"' \
  | ./peal --exact --tsv fixtures/nested.py

echo
echo "== --hits keeps only locator lines that rhyme =="
printf '%s\n' '13:    return "denied"' '6:        audit.warn("missing")' \
  | ./peal fixtures/nested.py:8 --hits --tsv

echo
echo "== try body is not the except arm =="
./peal fixtures/nested.py:10 --exact --tsv

echo
echo "== swift guard body, not guard-else =="
./peal fixtures/sample.swift:6 --explain

KIZU="${KIZU:-$HOME/ghq/github.com/annenpolka/kizu}"
if [[ -f "$KIZU/src/git/parse.rs" ]]; then
  echo
  echo "== kizu parse.rs:60 rhyme from rg -n (no -H); recover file, scan, not filter =="
  ROOT="$(pwd)"
  kizu_out="$(cd "$KIZU" && rg -n 'let b_side' src/git/parse.rs | "$ROOT/peal" --explain)"
  printf '%s\n' "$kizu_out" | sed -n '1,40p'
  printf '%s\n' "$kizu_out" | grep -q 'let b_side'
  printf '%s\n' "$kizu_out" | grep -q 'bytes_to_path'
  printf '%s\n' "$kizu_out" | grep -v 'here   }' | grep -q 'let b_side'
fi

echo
echo "demo ok"
