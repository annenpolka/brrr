#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/fingerhid"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest existing operation (diff two rustc -vV; compare path and mtime) =="
echo "path /usr/bin/rustc and mtime 2024-10-17 match; vv fc42 vs fc40 differ"
echo "(the leftover is hidden_by_fingerprint, not either observation alone)"
echo
echo "== fingerhid specimen-086 fc42 vs fc40 =="
python3 "$CLI" "$ROOT/fixtures/086-fc42.rec" "$ROOT/fixtures/086-fc40.rec" || true
echo
echo "== fingerhid same vv is not hidden =="
python3 "$CLI" "$ROOT/fixtures/086-fc42.rec" "$ROOT/fixtures/unseen-agree.rec" || true
