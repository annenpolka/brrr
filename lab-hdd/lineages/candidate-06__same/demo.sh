#!/usr/bin/env bash
# Empirical demo for `same`. Captures real exit codes; does not hide failures.
set -u
ROOT="$(cd "$(dirname "$0")" && pwd)"
SAME=(python3 "$ROOT/same")
FIX="$ROOT/fixtures"

ln -f "$FIX/hardlink/a" "$FIX/hardlink/b"
if [[ ! -L "$FIX/symlink/link" ]]; then
  ln -sfn file "$FIX/symlink/link"
fi

run() {
  local label="$1"
  shift
  echo "== $label =="
  echo "+ $*"
  set +e
  "$@"
  local rc=$?
  set -e
  echo "exit $rc"
  echo
  return 0
}

echo "same demo — identity kind is required"
echo

run "omit-kind failure" "${SAME[@]}" "$FIX/empty/a" "$FIX/empty/b"
run "inode hardlink identical" "${SAME[@]}" --inode "$FIX/hardlink/a" "$FIX/hardlink/b"
run "inode two empties distinct" "${SAME[@]}" --inode "$FIX/empty/a" "$FIX/empty/b"
run "bytes two empties identical" "${SAME[@]}" --bytes "$FIX/empty/a" "$FIX/empty/b"
run "json key order identical" "${SAME[@]}" --json "$FIX/json/order-ba.json" "$FIX/json/order-ab.json"
run "bytes symlink follows" "${SAME[@]}" --bytes "$FIX/symlink/file" "$FIX/symlink/link"
run "missing file error" "${SAME[@]}" --bytes "$FIX/empty/a" "$FIX/no-such"
run "binary vs json" "${SAME[@]}" --json "$FIX/binary.bin" "$FIX/json/order-ab.json"
