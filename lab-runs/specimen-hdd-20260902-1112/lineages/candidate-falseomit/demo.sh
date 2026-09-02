#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/falseomit"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest existing operation (json.dumps + key membership) =="
echo 'A {"name": "x"}  flag not in object'
echo 'B {"flag": false, "name": "x"}  flag present false'
echo
echo "== falseomit owned encodings =="
python3 "$CLI" "$ROOT/fixtures/a.json" "$ROOT/fixtures/b.json"
echo
echo "== falseomit unseen enabled:false omitted vs present =="
python3 "$CLI" "$ROOT/fixtures/unseen-a.json" "$ROOT/fixtures/unseen-b.json"
