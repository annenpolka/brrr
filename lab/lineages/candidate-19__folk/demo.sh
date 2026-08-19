#!/usr/bin/env bash
# demo.sh — folk must exit 0. Exercises toy, ugly, and one real-repo command.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
chmod +x "$ROOT/folk"

echo "=== folk --version ==="
"$ROOT/folk" --version

echo
echo "=== pairs on fixtures/toy ==="
"$ROOT/folk" --pairs fixtures/toy

echo
echo "=== orphans on fixtures/toy ==="
"$ROOT/folk" --orphans fixtures/toy

echo
echo "=== --of lock on fixtures/toy ==="
"$ROOT/folk" --all --of lock fixtures/toy

echo
echo "=== --check on fixtures/toy (expect exit 1) ==="
set +e
"$ROOT/folk" --check fixtures/toy
code=$?
set -e
if [ "$code" -ne 1 ]; then
  echo "demo: expected --check to exit 1 on toy orphans, got $code" >&2
  exit 1
fi
echo "ok: --check exited 1"

echo
echo "=== ugly fixtures (spaces, unicode, broken parse, skip generated) ==="
"$ROOT/folk" --pairs --orphans fixtures/ugly

echo
echo "=== JSON shape smoke ==="
"$ROOT/folk" --json --all fixtures/toy | python3 -c "import json,sys; o=json.load(sys.stdin); assert 'pairs' in o and 'orphans' in o; print('json ok', len(o['pairs']), 'pairs', len(o['orphans']), 'orphans')"

echo
echo "=== pipeline: pairs with score>=0.8 ==="
"$ROOT/folk" -q --pairs fixtures/toy | awk -F'\t' 'NR==1{next} $7+0>=0.8 {print}'

echo
echo "=== v0.2: no lock/work collocation; inline finds wrapped_orphan ==="
"$ROOT/folk" -q --pairs fixtures/toy | awk -F'\t' '$1=="lock" && $2=="work" { found=1 } END { if (found) { print "FAIL: lock/work still mined"; exit 1 } print "ok: lock/work not a protocol" }'
"$ROOT/folk" -q --orphans fixtures/toy | awk -F'\t' '$8=="wrapped_orphan" && $5=="begin_tx" { hit=1 } END { if (!hit) { print "FAIL: wrapped_orphan begin_tx not reported"; exit 1 } print "ok: inline exposed wrapped_orphan" }'

echo
echo "=== real repo: sitbone beginConfiguration/commitConfiguration ==="
SITBONE="${SITBONE:-/Users/annenpolka/ghq/github.com/annenpolka/sitbone/Sources}"
if [ -d "$SITBONE" ]; then
  "$ROOT/folk" --pairs --of beginConfiguration "$SITBONE" | awk -F'\t' '
    NR==1 { next }
    $1=="beginConfiguration" && $2=="commitConfiguration" { hit=1; print }
    END { if (!hit) { print "FAIL: sitbone handshake not found"; exit 1 } print "ok: sitbone handshake mined" }
  '
else
  echo "skip: sitbone not present"
fi

echo
echo "demo: toy + ugly + sitbone ok"
exit 0
