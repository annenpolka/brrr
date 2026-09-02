#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/sumext"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest existing operation (grep the module path) =="
echo "grep golang.org/x/bad hits the extension line in a raw lookup body"
echo "(the leftover is extension-only vs authenticated record, not the substring)"
echo
echo "== sumext specimen-084 leftover (bad in extension only) =="
python3 "$CLI" "$ROOT/fixtures/084-leftover.rec" --module golang.org/x/bad --version v1.0.0 || true
echo
echo "== sumext specimen-084 good in record =="
python3 "$CLI" "$ROOT/fixtures/084-leftover.rec" --module golang.org/x/good --version v1.0.0 || true
echo
echo "== sumext honest sampler =="
python3 "$CLI" "$ROOT/fixtures/084-honest.rec" --module rsc.io/sampler --version v1.3.0 || true
echo
echo "== sumext unseen both regions =="
python3 "$CLI" "$ROOT/fixtures/unseen-both.rec" --module example.com/m --version v0.1.0 || true
