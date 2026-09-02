#!/usr/bin/env bash
# Run silentadd on specimen-014 path lists and specimen-017 extras names.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/silentadd"

candidate_roots() {
  local top common parent
  top="$(git -C "$1" rev-parse --show-toplevel 2>/dev/null || true)"
  [ -n "$top" ] && printf '%s\n' "$top"
  common="$(git -C "$1" rev-parse --git-common-dir 2>/dev/null || true)"
  if [ -n "$common" ]; then
    parent="$(cd "$common/.." && pwd)"
    printf '%s\n' "$parent"
  fi
}

find_run() {
  if [ -n "${RUN_DIR:-}" ] && [ -d "$RUN_DIR/specimens/specimen-014" ]; then
    printf '%s\n' "$RUN_DIR"
    return 0
  fi
  local root cand
  while IFS= read -r root; do
    [ -z "$root" ] && continue
    cand="$root/lab-runs/specimen-hdd-20260902-1112"
    if [ -d "$cand/specimens/specimen-014" ]; then
      printf '%s\n' "$cand"
      return 0
    fi
  done < <(candidate_roots "$ROOT"; candidate_roots "$(pwd)")
  return 1
}

RUN="$(find_run || true)"
S014="${RUN:+$RUN/specimens/specimen-014}"
S017="${RUN:+$RUN/specimens/specimen-017}"

if [ ! -x "$CLI" ]; then
  chmod +x "$CLI"
fi
if [ ! -f "$CLI" ]; then
  echo "demo.sh: missing CLI at $CLI" >&2
  exit 1
fi

echo "== fixture ${S014:-missing}/files/index_scan.py =="
if [ -f "${S014:-}/files/index_scan.py" ]; then
  python3 "$S014/files/index_scan.py"
else
  echo "demo.sh: specimen-014 not found; using local fixtures only" >&2
fi
echo

echo "== silentadd blobtree aaa blobtree/ zzz (scan 0) =="
python3 "$CLI" blobtree aaa 'blobtree/' zzz
echo

echo "== silentadd --scan pos blobtree aaa blobtree/ zzz =="
python3 "$CLI" --scan pos blobtree aaa 'blobtree/' zzz
echo

echo "== silentadd blobtree --file fixtures/014-only-dir.txt (pos 0, scan 0 finds it) =="
python3 "$CLI" --file "$ROOT/fixtures/014-only-dir.txt" blobtree
echo

if [ -f "${S017:-}/files/pair_extras.py" ]; then
  echo "== fixture $S017/files/pair_extras.py =="
  python3 "$S017/files/pair_extras.py"
  echo
fi

echo "== silentadd B B (specimen-017 extra name, not a path index) =="
python3 "$CLI" B B
echo

echo "== silentadd pkg --file fixtures/unseen-pkg.txt (unseen list) =="
python3 "$CLI" --file "$ROOT/fixtures/unseen-pkg.txt" pkg
