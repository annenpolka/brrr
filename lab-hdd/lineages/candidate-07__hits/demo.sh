#!/usr/bin/env bash
# Real runs of the shipped hits CLI. Empty is success; binaries skipped.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
HITS="$ROOT/hits"
cd "$ROOT"

echo "== hit =="
"$HITS" needle fixtures/has
echo "exit=$?"

echo
echo "== miss (must be exit 0 so && still runs) =="
"$HITS" needle fixtures/miss
echo "exit=$?"
"$HITS" needle fixtures/miss && echo "still-running"

echo
echo "== literal is not regex =="
"$HITS" 'n.edle' fixtures/regex
echo "exit=$?"

echo
echo "== regex hit =="
"$HITS" --regex 'n.edle' fixtures/regex
echo "exit=$?"

echo
echo "== bad regex (must be exit 2) =="
set +e
"$HITS" --regex '[' fixtures/has
echo "exit=$?"
set -e

echo
echo "== usage (must be exit 1) =="
set +e
"$HITS"
echo "exit=$?"
set -e

echo
echo "== mixed tree: skip binary, keep text (exit 0) =="
"$HITS" needle fixtures/mixed
echo "exit=$?"

echo
echo "== --glob '*.txt' on mixed (exit 0) =="
"$HITS" --glob '*.txt' needle fixtures/mixed
echo "exit=$?"

echo
echo "== --glob miss is still success =="
"$HITS" --glob '*.md' needle fixtures/mixed && echo still-running

echo
echo "== unreadable DIR (must be exit 3) =="
if tmp="$(mktemp -d "${TMPDIR:-/tmp}/hits-unreadable.XXXXXX")" && chmod 000 "$tmp"; then
  set +e
  "$HITS" needle "$tmp"
  echo "exit=$?"
  set -e
  chmod 700 "$tmp"
  rmdir "$tmp"
else
  echo "(skip unreadable DIR demo: chmod/mktemp not usable here)"
  if [ -n "${tmp:-}" ]; then
    chmod 700 "$tmp" 2>/dev/null || true
    rmdir "$tmp" 2>/dev/null || true
  fi
fi
