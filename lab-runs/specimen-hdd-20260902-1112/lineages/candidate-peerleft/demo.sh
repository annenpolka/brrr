#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/peerleft"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest existing operation (grep the lock for the name) =="
echo "grep no-deps hits optionalPeers in both never-install and after-remove"
echo "(the leftover is a packages identity, not the metadata mention)"
echo
echo "== peerleft specimen-082 owned =="
python3 "$CLI" "$ROOT/fixtures/082-never.rec" "$ROOT/fixtures/082-after-remove.rec" --name no-deps || true
echo
echo "== peerleft unseen widget =="
python3 "$CLI" "$ROOT/fixtures/unseen-never.rec" "$ROOT/fixtures/unseen-after.rec" --name widget || true
echo
echo "== peerleft never vs never (no leftover) =="
python3 "$CLI" "$ROOT/fixtures/082-never.rec" "$ROOT/fixtures/082-never.rec" --name no-deps || true
