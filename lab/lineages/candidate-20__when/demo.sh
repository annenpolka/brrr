#!/usr/bin/env bash
# demo.sh — must exit 0. Exercises the primitive, not a screenshot.
set -euo pipefail
cd "$(dirname "$0")"
chmod +x ./when

echo "== unit tests =="
python3 -m unittest tests.test_whenline -q

echo
echo "== locus: nested return (python-ast) =="
./when fixtures/nested.py:13 --explain

echo
echo "== fallthrough givens after early return =="
./when fixtures/nested.py:8 --explain
./when fixtures/guards.rs:11 --explain

echo
echo "== grep pipe (file:line) =="
printf '%s\n' 'fixtures/nested.py:13:return denied' 'fixtures/contradict.py:4:impossible' | ./when --tsv

echo
echo "== rg-style bare LINE:text + FILE =="
printf '%s\n' '13:    return "denied"' | ./when fixtures/nested.py --tsv

echo
echo "== unapplied patch =="
./when --diff fixtures/sample.diff --group

echo
echo "== rust match / swift guard =="
./when fixtures/sample.rs:16 --explain
./when fixtures/sample.swift:6 --explain

echo
echo "== scan deep python fixture =="
./when --scan fixtures/nested.py --min-depth 5 --tsv | head -n 6

echo
echo "demo ok"
