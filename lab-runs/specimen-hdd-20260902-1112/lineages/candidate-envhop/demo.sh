#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/envhop"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest existing operation (diff two env dumps) =="
echo "before has TEST-VAR=123; after does not"
echo "(the join is dropped-because-not-POSIX-identifier)"
echo
echo "== envhop specimen-068 owned hop =="
python3 "$CLI" "$ROOT/fixtures/068-before.env" "$ROOT/fixtures/068-after.env"
echo
echo "== envhop unseen survived invalid =="
python3 "$CLI" "$ROOT/fixtures/unseen-before.env" "$ROOT/fixtures/unseen-after.env"
