#!/usr/bin/env bash
# demo.sh — must exit 0. Exercises control-flow rhyme, not a screenshot.
set -euo pipefail
cd "$(dirname "$0")"
chmod +x ./chime

echo "== unit tests =="
python3 -m unittest tests.test_chime -q

echo
echo "== exact arm of nested return =="
./chime fixtures/nested.py:13 --exact --explain

echo
echo "== after None-guard (same + deeper supersets) =="
./chime fixtures/nested.py:8 --group

echo
echo "== try body is not the except arm =="
./chime fixtures/nested.py:10 --exact --tsv

echo
echo "== rust fallthrough given a/ (payload, not closing brace) =="
./chime fixtures/guards.rs:11 --explain
./chime fixtures/guards.rs:11 --exact --explain | grep -v 'here   }' | grep -q 'let p'

echo
echo "== swift guard body, not guard-else =="
./chime fixtures/sample.swift:6 --explain

echo
echo "== grep pipe keeps only rhyming hits =="
printf '%s\n' '13:    return "denied"' '6:        audit.warn("missing")' \
  | ./chime fixtures/nested.py:8 --tsv

echo
echo "== --same-as alias =="
./chime --same-as fixtures/nested.py:13 --exact --tsv

echo
echo "demo ok"
