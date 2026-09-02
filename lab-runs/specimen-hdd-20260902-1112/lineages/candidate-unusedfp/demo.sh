#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/unusedfp"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest existing operation (print two hashes) =="
echo "all snapshot changes; used-only snapshot does not"
echo "(the two hashes do not name the unread key)"
echo
echo "== unusedfp specimen-076 owned =="
python3 "$CLI" "$ROOT/fixtures/076-first.env" "$ROOT/fixtures/076-second.env" --used path || true
echo
echo "== unusedfp unseen ORG_GRADLE_PROJECT =="
python3 "$CLI" "$ROOT/fixtures/unseen-first.env" "$ROOT/fixtures/unseen-second.env" --used src || true
