#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/addrid"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest existing operation (print fetch log plus pointer set) =="
echo "insert 0xa flake-utils then worker 0xa naersk; fetched flake-utils nixpkgs"
echo "(address equality does not name the swapped lock node)"
echo
echo "== adrid specimen-070 owned reuse =="
python3 "$CLI" "$ROOT/fixtures/070-reuse.rec"
echo
echo "== adrid unseen stable addresses =="
python3 "$CLI" "$ROOT/fixtures/unseen-stable.rec"
