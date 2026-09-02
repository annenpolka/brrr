#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/sumident"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest existing operation (grep the module path) =="
echo "grep rsc.io/quote hits /go.mod and zip lines"
echo "(the leftover is which identity class, not the substring)"
echo
echo "== sumident specimen-083 download (mod-only) =="
python3 "$CLI" "$ROOT/fixtures/go.sum.download" --module rsc.io/quote --version v1.5.2 || true
echo
echo "== sumident specimen-083 tidy (both) =="
python3 "$CLI" "$ROOT/fixtures/go.sum.tidy" --module rsc.io/quote --version v1.5.2 || true
echo
echo "== sumident unseen sampler download =="
python3 "$CLI" "$ROOT/fixtures/go.sum.download" --module rsc.io/sampler --version v1.3.0 || true
echo
echo "== sumident zip-only =="
python3 "$CLI" "$ROOT/fixtures/go.sum.zip-only" --module rsc.io/quote --version v1.5.2 || true
echo
echo "== sumident missing module =="
python3 "$CLI" "$ROOT/fixtures/go.sum.download" --module example.com/missing --version v0.0.1 || true
