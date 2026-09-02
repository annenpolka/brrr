#!/usr/bin/env bash
# Concatenate specimen-013 leftover+moved into one pathless module; ask leftover vs moved.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/bindslot"

candidate_roots() {
  local top common abs parent
  top="$(git -C "$1" rev-parse --show-toplevel 2>/dev/null || true)"
  [ -n "$top" ] && printf '%s\n' "$top"
  common="$(git -C "$1" rev-parse --git-common-dir 2>/dev/null || true)"
  if [ -n "$common" ]; then
    case "$common" in
      /*) abs="$common" ;;
      *) abs="$(cd "$1" && cd "$common" && pwd)" ;;
    esac
    parent="$(cd "$abs/.." && pwd)"
    printf '%s\n' "$parent"
  fi
}

find_specimen() {
  if [ -n "${SPECIMEN:-}" ] && [ -f "$SPECIMEN/files/pkg_util.py" ]; then
    printf '%s\n' "$SPECIMEN"
    return 0
  fi
  local root cand
  while IFS= read -r root; do
    [ -z "$root" ] && continue
    cand="$root/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-013"
    if [ -f "$cand/files/pkg_util.py" ]; then
      printf '%s\n' "$cand"
      return 0
    fi
  done < <(candidate_roots "$ROOT"; candidate_roots "$(pwd)")
  return 1
}

find_bindname() {
  if [ -n "${BINDNAME:-}" ] && [ -f "$BINDNAME" ]; then
    printf '%s\n' "$BINDNAME"
    return 0
  fi
  local root cand
  while IFS= read -r root; do
    [ -z "$root" ] && continue
    cand="$root/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname"
    if [ -f "$cand" ]; then
      printf '%s\n' "$cand"
      return 0
    fi
  done < <(candidate_roots "$ROOT"; candidate_roots "$(pwd)")
  return 1
}

SPECIMEN="$(find_specimen || true)"
PARENT_CLI="$(find_bindname || true)"

if [ ! -x "$CLI" ]; then
  chmod +x "$CLI"
fi
if [ ! -f "$CLI" ]; then
  echo "demo.sh: missing CLI at $CLI" >&2
  exit 1
fi
if [ ! -f "${SPECIMEN:-}/files/pkg_util.py" ]; then
  echo "demo.sh: specimen-013 fixture not found at $SPECIMEN" >&2
  echo "demo.sh: set SPECIMEN to the specimen-013 directory" >&2
  exit 1
fi

FILES="$SPECIMEN/files"

echo "== grep def parse (path-split files) =="
grep -n "def parse" "$FILES/pkg_util.py" "$FILES/pkg_parse.py"
echo

echo "== concatenate into one module (no path split) =="
CONCAT="$(mktemp "${TMPDIR:-/tmp}/bindslot-concat.XXXXXX.py")"
cleanup() { rm -f "$CONCAT"; }
trap cleanup EXIT
cat "$FILES/pkg_util.py" "$FILES/pkg_parse.py" >"$CONCAT"
grep -n "def parse" "$CONCAT"
echo

echo "== honesty: exec blob with no __file__ =="
python3 - "$CONCAT" <<'PY'
import sys
import types
from pathlib import Path

src = Path(sys.argv[1]).read_text(encoding="utf-8")
mod = types.ModuleType("nopath_blob")
exec(src, mod.__dict__)
print("parse", mod.parse("  z  "))
print("has_file", hasattr(mod, "__file__"))
print("same_as_legacy", mod.parse("  z  ")[0] == "legacy")
PY
echo

echo "== bindslot --concat (one module, leftover vs moved) =="
python3 "$CLI" parse --concat "$FILES/pkg_util.py" --concat "$FILES/pkg_parse.py"
echo

echo "== bindslot stdin (pathless) =="
python3 "$CLI" parse <"$CONCAT"
echo

if [ -n "${PARENT_CLI:-}" ]; then
  echo "== parent bindname on concatenated dir (path identity) =="
  TMPDIR_BN="$(mktemp -d "${TMPDIR:-/tmp}/bindslot-bn.XXXXXX")"
  cp "$CONCAT" "$TMPDIR_BN/concat.py"
  python3 "$PARENT_CLI" -C "$TMPDIR_BN" parse || true
  rm -rf "$TMPDIR_BN"
fi
