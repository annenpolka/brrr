#!/usr/bin/env bash
# demo.sh — must exit 0. Exercises the inverted primitive, not a screenshot.
set -euo pipefail
cd "$(dirname "$0")"
chmod +x ./under

echo "== unit tests =="
python3 -m unittest tests.test_under -q

echo
echo "== under user.locked (python body, not the if-line) =="
./under 'user.locked' fixtures/nested.py --explain

echo
echo "== under given None-guard =="
./under 'user is not None' --kind given fixtures/nested.py --tsv | head -n 8

echo
echo "== AND path: locked + can_delete =="
./under 'user.locked | can_delete' fixtures/nested.py --explain

echo
echo "== rust fallthrough given a/ =="
./under 'starts_with(a/)' fixtures/guards.rs --explain

echo
echo "== swift guard isEnabled =="
./under 'isEnabled' fixtures/sample.swift --explain

echo
echo "== grep pipe: keep only returns under locked =="
printf '%s\n' '13:    return "denied"' '34:            return "drained"' \
  | ./under 'user.locked' fixtures/nested.py --tsv

echo
echo "== unapplied patch filtered by condition =="
./under 'can_delete' --diff fixtures/sample.diff --group

echo
echo "== group remaining stacks under user is not None =="
./under 'user is not None' fixtures/nested.py --group | head -n 20

echo
echo "demo ok"
