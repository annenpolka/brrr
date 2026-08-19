#!/usr/bin/env bash
# demo.sh — must exit 0. Exercises the primitive, not a screenshot.
set -euo pipefail
cd "$(dirname "$0")"
chmod +x ./whence

echo "== unit tests =="
python3 -m unittest tests.test_whence -q

echo
echo "== locus: nested return (python-ast) =="
./whence fixtures/nested.py:13 --explain

echo
echo "== fallthrough givens after early return =="
./whence fixtures/nested.py:8 --explain
./whence fixtures/guards.rs:11 --explain

echo
echo "== grep pipe (file:line) =="
printf '%s\n' 'fixtures/nested.py:13:return denied' 'fixtures/contradict.py:4:impossible' | ./whence --tsv

echo
echo "== rg-style bare LINE:text + FILE =="
printf '%s\n' '13:    return "denied"' | ./whence fixtures/nested.py --tsv

echo
echo "== unapplied patch =="
./whence --diff fixtures/sample.diff --group

echo
echo "== rust match / swift guard =="
./whence fixtures/sample.rs:16 --explain
./whence fixtures/sample.swift:6 --explain

echo
echo "== scan deep python fixture =="
./whence --scan fixtures/nested.py --min-depth 5 --tsv | head -n 6

KIZU="${KIZU:-/Users/annenpolka/ghq/github.com/annenpolka/kizu/src/git/parse.rs}"
if [[ -f "$KIZU" ]]; then
  echo
  echo "== kizu parse.rs:60 four-given stack =="
  ./whence "$KIZU:60" --explain
  ./whence "$KIZU:60" --json | python3 -c '
import json,sys
rec=json.load(sys.stdin)
g=[f["pred"] for f in rec["frames"] if f["kind"]=="given"]
assert len(g)==4, g
print("four givens:", *g, sep="\n  ")
'
fi

echo
echo "demo ok"
