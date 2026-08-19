#!/usr/bin/env bash
# demo.sh — must exit 0. Stream locators, scan the same file, not a tree.
set -euo pipefail
cd "$(dirname "$0")"
chmod +x ./amid

echo "== unit tests =="
python3 -m unittest tests.test_amid -q

echo
echo "== named file (no stdin, no walk) =="
./amid 'user.locked' fixtures/nested.py --explain

echo
echo "== rg | amid: locators name the file; scan expands past the hit =="
printf '%s\n' 'fixtures/nested.py:13:    return "denied"' \
  | ./amid 'user.locked' --explain

echo
echo "== bare LINE:text + FILE operand (rg FILE omits the name) =="
printf '%s\n' '13:    return "denied"' '34:            return "drained"' \
  | ./amid 'user.locked' fixtures/nested.py --tsv

echo
echo "== --pin keeps the old filter (only the piped lines) =="
printf '%s\n' 'fixtures/nested.py:13:    return "denied"' \
              'fixtures/nested.py:34:            return "drained"' \
  | ./amid 'user.locked' --pin --tsv

echo
echo "== rust: pipe the if-line, get the fallthrough given =="
printf '%s\n' 'fixtures/guards.rs:8:    if !bytes.starts_with(b"a/") {' \
  | ./amid 'starts_with(a/)' --explain

echo
echo "== heading stream (rg --heading) =="
printf '%s\n' 'fixtures/sample.swift' '6:    let readings = await readAllSensors()' \
  | ./amid 'isEnabled' --explain

echo
echo "== AND path =="
./amid 'user.locked | can_delete' fixtures/nested.py --explain

echo
echo "== unapplied patch names the file; scan it =="
./amid 'can_delete' --diff fixtures/sample.diff --group

echo
echo "== rg --json names the file; locator names the condition (no snippet) =="
python3 - <<'PY' | ./amid --explain
import json
from pathlib import Path
p = Path("fixtures/guards.rs")
print(json.dumps({
    "type": "match",
    "data": {
        "path": {"text": str(p)},
        "line_number": 8,
        "lines": {"text": "    if !bytes.starts_with(b\"a/\") {\n"},
    },
}))
PY

echo
echo "demo ok"
