#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/omitfalse"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest existing operation (print both JSON strings) =="
echo 'A {"name":"x"}  B {"flag":false,"name":"x"}'
echo "(printing both still leaves missing-as-true as a hand join)"
echo
echo "== omitfalse owned flag =="
python3 "$CLI" "$ROOT/fixtures/a.json" "$ROOT/fixtures/b.json" --key flag
echo
echo "== omitfalse unseen debug =="
python3 "$CLI" "$ROOT/fixtures/unseen-a.json" "$ROOT/fixtures/unseen-b.json" --key debug
