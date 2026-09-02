#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/identjson"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest existing operation (print IdentityJSON and Identity: nil) =="
echo 'leftover {"id":"foo"} against Identity: nil'
echo "(the leftover bytes look like identity; decode class is the miss)"
echo
echo "== identjson specimen-081 nil schema leftover JSON =="
python3 "$CLI" "$ROOT/fixtures/081-nil-leftover.rec" || true
echo
echo "== identjson schema present =="
python3 "$CLI" "$ROOT/fixtures/081-schema-present.rec" || true
echo
echo "== identjson nil JSON omitted =="
python3 "$CLI" "$ROOT/fixtures/081-nil-json.rec" || true
echo
echo "== identjson mismatch arn vs id =="
python3 "$CLI" "$ROOT/fixtures/081-mismatch.rec" || true
echo
echo "== identjson leftover JSON document (same facts) =="
python3 "$CLI" "$ROOT/fixtures/081-nil-leftover.json" || true
