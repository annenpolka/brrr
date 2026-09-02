#!/usr/bin/env bash
# Run hunkland on specimen-020 empty-range insert and one unseen insert.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/hunkland"
LOCAL_APPLY="$ROOT/fixtures/patch_insert.py"

candidate_roots() {
  local top common parent
  top="$(git -C "$1" rev-parse --show-toplevel 2>/dev/null || true)"
  [ -n "$top" ] && printf '%s\n' "$top"
  common="$(git -C "$1" rev-parse --git-common-dir 2>/dev/null || true)"
  if [ -n "$common" ]; then
    parent="$(cd "$1" && cd "$common/.." && pwd)"
    printf '%s\n' "$parent"
  fi
}

find_specimen() {
  if [ -n "${SPECIMEN:-}" ] && [ -f "$SPECIMEN/files/patch_insert.py" ]; then
    printf '%s\n' "$SPECIMEN"
    return 0
  fi
  local root cand
  while IFS= read -r root; do
    [ -z "$root" ] && continue
    cand="$root/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-020"
    if [ -f "$cand/files/patch_insert.py" ]; then
      printf '%s\n' "$cand"
      return 0
    fi
  done < <(candidate_roots "$ROOT"; candidate_roots "$(pwd)")
  return 1
}

SPECIMEN="$(find_specimen || true)"
APPLY="${SPECIMEN:+$SPECIMEN/files/patch_insert.py}"
if [ -z "${APPLY:-}" ] || [ ! -f "$APPLY" ]; then
  APPLY="$LOCAL_APPLY"
fi

if [ ! -x "$CLI" ]; then
  chmod +x "$CLI"
fi
if [ ! -f "$CLI" ]; then
  echo "demo.sh: missing CLI at $CLI" >&2
  exit 1
fi

echo "== fixture $APPLY =="
python3 "$APPLY"
echo

echo "== nearest existing: cat orig and result, read @@ header =="
echo "-- orig --"
cat "$ROOT/fixtures/020-orig.txt"
echo "-- result --"
cat "$ROOT/fixtures/020-result.txt"
echo "-- hunk --"
echo "@@ -2,0 +3 @@"
echo "apply_exit 0"
echo

echo "== hunkland --applier (owned apply_hunk) vs @@ -2,0 +3 =="
python3 "$CLI" "$ROOT/fixtures/020-orig.txt" \
  --applier "$APPLY" --hunk '@@ -2,0 +3 @@' --insert inserted --apply-exit 0
echo

echo "== hunkland 020-orig 020-result files (same insert, no applier) =="
python3 "$CLI" "$ROOT/fixtures/020-orig.txt" "$ROOT/fixtures/020-result.txt" \
  --hunk '@@ -2,0 +3 @@' --apply-exit 0
echo

echo "== hunkland aligned result (insert after line 2) =="
python3 "$CLI" "$ROOT/fixtures/020-orig.txt" "$ROOT/fixtures/020-aligned.txt" \
  --hunk '@@ -2,0 +3 @@' --apply-exit 0
echo

echo "== hunkland unseen --applier @@ -3,0 +4 @@ +mid =="
python3 "$CLI" "$ROOT/fixtures/unseen-orig.txt" \
  --applier "$APPLY" --hunk '@@ -3,0 +4 @@' --insert mid --apply-exit 0
echo

echo "== hunkland --applier @@ -0,0 +1 @@ (empty range at 0) =="
python3 "$CLI" "$ROOT/fixtures/020-orig.txt" \
  --applier "$APPLY" --hunk '@@ -0,0 +1 @@' --insert inserted --apply-exit 0
