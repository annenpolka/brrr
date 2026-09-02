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
echo "== identjson JSON null vs nil schema (typed-null) =="
python3 "$CLI" "$ROOT/fixtures/081-typed-null.rec" || true
echo
echo "== identjson JSON null vs present schema (typed-null) =="
python3 "$CLI" "$ROOT/fixtures/081-typed-null-present.rec" || true
echo
echo "== identjson present schema omitted JSON (not typed-null) =="
python3 "$CLI" "$ROOT/fixtures/081-present-omitted.rec" || true
echo
echo "== identjson empty JSON object vs nil schema (EmptyObject) =="
python3 "$CLI" "$ROOT/fixtures/081-empty-object.rec" || true
echo
echo "== identjson schema list with spaces =="
python3 "$CLI" "$ROOT/fixtures/081-schema-spaces.rec" || true
echo
echo "== identjson schema list with comma-spaces =="
python3 "$CLI" "$ROOT/fixtures/081-schema-comma-spaces.rec" || true
