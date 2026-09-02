#!/usr/bin/env bash
# FIRST is earlier, SECOND is later. Harvest is a verdict, not three flags.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/refpin"
chmod +x "$CLI" 2>/dev/null || true

run_cli() {
  local rc=0
  python3 "$CLI" "$@" || rc=$?
  echo "rc=$rc"
}

echo "== nearest existing operation (diff the two lock records) =="
diff -u "$ROOT/fixtures/064-expected.rec" "$ROOT/fixtures/064-got.rec" || true
echo "(diff names narHash and ref; it does not name pinned-rev-default-ref-changed-hash)"
echo

echo "== native mismatch log (discovers master; not a handwritten rec) =="
run_cli "$ROOT/fixtures/narhash_mismatch.txt"
echo

echo "== nix error with JSON lock blobs =="
run_cli "$ROOT/fixtures/nix-error.txt"
echo

echo "== JSON lock objects (url/type present, ignored) =="
run_cli "$ROOT/fixtures/064-expected.json" "$ROOT/fixtures/064-got.json"
echo

echo "== refpin specimen-064 owned rec pair =="
run_cli "$ROOT/fixtures/064-expected.rec" "$ROOT/fixtures/064-got.rec"
echo

echo "== swapped owned pair (ref_removed, not attach) =="
run_cli "$ROOT/fixtures/064-got.rec" "$ROOT/fixtures/064-expected.rec"
echo

echo "== hash changed, no ref (harvest miss) =="
TD="$(mktemp -d)"
printf 'rev\te374a4ebd0dbf7b23e077a94fd5cefb7a9d65ffa\nnarHash\tsha256-UEzJabo6ObaQc0Rc5XJOf43NR5Rp3e0WwpWi55c79R8=\n' >"$TD/a.rec"
printf 'rev\te374a4ebd0dbf7b23e077a94fd5cefb7a9d65ffa\nnarHash\tsha256-q2mgMIPLqHSx0pSEJ42rrZpYxcjkgL1U1UvCTHTw+Oo=\n' >"$TD/b.rec"
run_cli "$TD/a.rec" "$TD/b.rec"
rm -rf "$TD"
echo

echo "== refpin unseen identical records =="
run_cli "$ROOT/fixtures/unseen-same.rec" "$ROOT/fixtures/unseen-same-b.rec"
