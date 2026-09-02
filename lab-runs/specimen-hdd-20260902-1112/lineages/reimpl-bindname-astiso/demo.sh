#!/usr/bin/env bash
# Run bindiso on the specimen-013 leftover-vs-moved parse fixture.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/bindiso"

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

SPECIMEN="$(find_specimen || true)"

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

echo "== grep def parse (both files) =="
grep -n "def parse" "$FILES/pkg_util.py" "$FILES/pkg_parse.py"
echo

echo "== fixture $FILES/test_parse_identity.py =="
python3 "$FILES/test_parse_identity.py"
echo

echo "== bindiso parse (all binds) =="
python3 "$CLI" -C "$FILES" parse
echo

echo "== bindiso --from pkg_util parse (stale import / leftover helper) =="
python3 "$CLI" -C "$FILES" --from pkg_util parse
echo

echo "== bindiso --import 'from pkg_parse import parse' (moved definition) =="
python3 "$CLI" -C "$FILES" --import 'from pkg_parse import parse'
echo

echo "== bindiso --file test_parse_identity.py parse =="
python3 "$CLI" -C "$FILES" --file "$FILES/test_parse_identity.py" parse
echo

echo "== leftover ast.py (not stdlib ast.parse) =="
ASTDIR="$(mktemp -d)"
cleanup() { rm -rf "$ASTDIR"; }
trap cleanup EXIT
printf '%s\n' "def parse(x):" "    return ('leftover-ast', x)" >"$ASTDIR/ast.py"
printf '%s\n' "def parse(x):" "    return ('moved', x)" >"$ASTDIR/pkg_parse.py"
echo "-- honesty (cwd leftover dir) --"
(cd "$ASTDIR" && python3 -c "from ast import parse; print(parse('z'))")
echo "-- bindiso --from ast parse --"
python3 "$CLI" -C "$ASTDIR" --from ast parse
