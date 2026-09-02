#!/usr/bin/env bash
# Run envlayers on the specimen-010 empty-assignment fixture.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/envlayers"

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

find_specimen() {
  if [ -n "${SPECIMEN:-}" ] && [ -f "$SPECIMEN/files/loader.py" ]; then
    printf '%s\n' "$SPECIMEN"
    return 0
  fi
  local root cand
  while IFS= read -r root; do
    [ -z "$root" ] && continue
    cand="$root/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-010"
    if [ -f "$cand/files/loader.py" ]; then
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
if [ ! -f "$SPECIMEN/files/loader.py" ]; then
  echo "demo.sh: specimen-010 fixture not found at $SPECIMEN" >&2
  echo "demo.sh: set SPECIMEN to the specimen-010 directory" >&2
  exit 1
fi

WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/envlayers-demo.XXXXXX")"
cleanup() { rm -rf "$WORKDIR"; }
trap cleanup EXIT

# Same file text as files/loader.py: KEY= (empty) and OTHER=2
printf 'KEY=\nOTHER=2\n' >"$WORKDIR/file.env"

echo "== fixture $SPECIMEN/files/loader.py =="
env -u KEY python3 "$SPECIMEN/files/loader.py"
echo

echo "== envlayers KEY (inherited KEY=/x, file KEY=, process unset) =="
env -u KEY -u OTHER python3 "$CLI" --no-process-env \
  --inherited KEY=/x --inherited OTHER=1 \
  --file "$WORKDIR/file.env" KEY
echo

echo "== envlayers OTHER =="
env -u KEY -u OTHER python3 "$CLI" --no-process-env \
  --inherited KEY=/x --inherited OTHER=1 \
  --file "$WORKDIR/file.env" OTHER
