#!/usr/bin/env bash
# Run poslayer on specimen-019 file vs CLI override leftover args.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/poslayer"

candidate_roots() {
  local top common parent
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
  if [ -n "${SPECIMEN:-}" ] && [ -f "$SPECIMEN/files/override_subst.py" ]; then
    printf '%s\n' "$SPECIMEN"
    return 0
  fi
  local root cand
  while IFS= read -r root; do
    [ -z "$root" ] && continue
    cand="$root/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-019"
    if [ -f "$cand/files/override_subst.py" ]; then
      printf '%s\n' "$cand"
      return 0
    fi
  done < <(candidate_roots "$ROOT"; candidate_roots "$(pwd)")
  return 1
}

SPECIMEN="$(find_specimen || true)"
FIXTURE="$ROOT/fixtures/override_subst.py"
if [ -n "${SPECIMEN:-}" ] && [ -f "$SPECIMEN/files/override_subst.py" ]; then
  FIXTURE="$SPECIMEN/files/override_subst.py"
fi

if [ ! -x "$CLI" ]; then
  chmod +x "$CLI"
fi
if [ ! -f "$CLI" ]; then
  echo "demo.sh: missing CLI at $CLI" >&2
  exit 1
fi

echo "== fixture ${FIXTURE} =="
python3 "$FIXTURE"
echo

echo "== nearest existing operation (print argv and the template) =="
echo "file template: pytest {posargs}"
echo "override template: pytest {posargs}"
echo "leftover: tests src"
echo "(printing both argvs does not name expansion layer vs leftover args)"
echo

echo "== poslayer specimen-019 (file expands, override leftover literal) =="
python3 "$CLI" --file "$ROOT/fixtures/019-file.txt" -- tests src
echo

echo "== poslayer unseen {packages} leftover pkg =="
python3 "$CLI" --file "$ROOT/fixtures/unseen-packages.txt" --token '{packages}' -- pkg
echo

echo "== poslayer coincidental leftover word in override (tests is a template word) =="
python3 "$CLI" --file-template 'pytest {posargs}' --override 'pytest tests {posargs}' -- tests src
echo

echo "== poslayer --subst-override (both layers expand) =="
python3 "$CLI" --file-template 'pytest {posargs}' --subst-override -- tests src
