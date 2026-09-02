#!/usr/bin/env bash
# Run leakorder on specimen-009, class-attribute Box.bucket, and a helper-module pair.
set -euo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)

if [ -f "$HERE/leakorder" ]; then
  CLI="$HERE/leakorder"
elif [ -f "$HERE/leakorder.py" ]; then
  CLI="$HERE/leakorder.py"
else
  echo "demo.sh: missing leakorder CLI under $HERE" >&2
  exit 1
fi

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
  local id="$1"
  local file="$2"
  local root cand
  while IFS= read -r root; do
    [ -z "$root" ] && continue
    cand="$root/lab-runs/specimen-hdd-20260902-1112/specimens/$id"
    if [ -f "$cand/files/$file" ]; then
      printf '%s\n' "$cand"
      return 0
    fi
  done < <(candidate_roots "$HERE"; candidate_roots "$(pwd)")
  cand="$HERE/../../specimens/$id"
  if [ -f "$cand/files/$file" ]; then
    printf '%s\n' "$(cd "$cand" && pwd)"
    return 0
  fi
  return 1
}

S009="$(find_specimen specimen-009 test_order.py || true)"
S060="$(find_specimen specimen-060 test_class_leak.py || true)"

if [ -n "$S009" ]; then
  FILE009="$S009/files/test_order.py"
else
  FILE009="$HERE/fixtures/specimen009.py"
fi
if [ -n "$S060" ]; then
  FILE060="$S060/files/test_class_leak.py"
else
  FILE060="$HERE/fixtures/test_class_attr.py"
fi
FILEHELP="$HERE/fixtures/helper_pair/test_helper.py"

if [ ! -f "$FILE009" ]; then
  echo "demo.sh: specimen-009 fixture not found" >&2
  exit 1
fi
if [ ! -f "$FILE060" ]; then
  echo "demo.sh: class-attribute fixture not found" >&2
  exit 1
fi
if [ ! -f "$FILEHELP" ]; then
  echo "demo.sh: helper-module fixture not found" >&2
  exit 1
fi

run_cli() {
  local title="$1"
  local file="$2"
  echo "== $title =="
  set +e
  python3 "$CLI" "$file"
  local code=$?
  set -e
  echo "exit: $code"
  echo
}

run_cli "leakorder specimen-009 (module global acc)" "$FILE009"
run_cli "leakorder class-attribute Box.bucket" "$FILE060"
run_cli "leakorder helper-module bucket" "$FILEHELP"
