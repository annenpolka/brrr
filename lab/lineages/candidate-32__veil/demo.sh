#!/usr/bin/env bash
# End-to-end demo: unit tests + self-test + three cover types + optional dogfood.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
chmod +x "$ROOT/veil" "$ROOT/demo.sh"
VEIL=(python3 "$ROOT/veil.py")

echo "======== 1. unit tests ========"
python3 -m unittest discover -s tests -q
echo "unit tests: OK"

echo "======== 2. --self-test ========"
"${VEIL[@]}" --self-test

echo "======== 3. replay ugly fixture via CLI ========"
DEMO="$ROOT/demo-tmp"
rm -rf "$DEMO"
mkdir -p "$DEMO"
python3 - << PY
import sys
from pathlib import Path
sys.path.insert(0, "$ROOT")
import veil
repo = veil.build_ugly_fixture(Path("$DEMO"))
print(repo)
PY
UGLY="$DEMO/ugly"
BASE="$(git -C "$UGLY" rev-parse HEAD~1)"

echo "---- text ----"
"${VEIL[@]}" -C "$UGLY" --from "$BASE" --to HEAD
echo "---- porcelain ----"
"${VEIL[@]}" -C "$UGLY" --from "$BASE" --to HEAD --porcelain
echo "---- json status ----"
"${VEIL[@]}" -C "$UGLY" --from "$BASE" --to HEAD --json | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["status"], d["counts"])'

porc="$("${VEIL[@]}" -C "$UGLY" --from "$BASE" --to HEAD --porcelain)"
echo "$porc" | grep -q $'LIVE\tadd\tshop.py' || { echo "missing LIVE add"; echo "$porc"; exit 1; }
echo "$porc" | grep -q $'VEIL\tcheckout\tshop.py' || { echo "missing VEIL checkout"; echo "$porc"; exit 1; }
echo "$porc" | grep -q $'BARE\tretry_budget\tshop.py' || { echo "missing BARE retry_budget"; echo "$porc"; exit 1; }
echo "$porc" | grep -q $'VEIL\tloadTemplate\tsrc/loader.ts' || { echo "missing VEIL loadTemplate"; echo "$porc"; exit 1; }
echo "$porc" | grep -q $'LIVE\tcompose\tsrc/composer.ts' || { echo "missing LIVE compose"; echo "$porc"; exit 1; }
echo "$porc" | grep -q $'status\tOPEN' || { echo "want OPEN"; echo "$porc"; exit 1; }

set +e
"${VEIL[@]}" -C "$UGLY" --from "$BASE" --to HEAD --check >/dev/null
code=$?
set -e
if [[ "$code" -ne 1 ]]; then
  echo "--check should exit 1 on OPEN, got $code" >&2
  exit 1
fi
echo "ugly fixture: OK"

echo "======== 4. dogfood (read-only, skip if missing) ========"
dogfood() {
  local name="$1" path="$2" range="${3:-HEAD~1}"
  if [[ ! -d "$path/.git" && ! -f "$path/.git" ]]; then
    echo "skip $name (not present)"
    return 0
  fi
  echo "---- $name $range..HEAD ----"
  "${VEIL[@]}" -C "$path" --from "$range" --to HEAD --json \
    | python3 -c '
import json,sys
d=json.load(sys.stdin)
print("status", d["status"], "counts", d["counts"], "prod", len(d["production_files"]))
for n in d["names"][:12]:
    print("  %-5s %s  %s" % (n["status"], n["qualname"], n["file"]))
if len(d["names"])>12:
    print("  … %d more" % (len(d["names"])-12))
'
}

GHQ="${GHQ:-/Users/annenpolka/ghq/github.com/annenpolka}"
dogfood soul-writer "$GHQ/soul-writer" HEAD~3
dogfood voidtrace "$GHQ/voidtrace" HEAD~1
dogfood kizu "$GHQ/kizu" HEAD~1
dogfood sitbone "$GHQ/sitbone" HEAD~1
dogfood skills "$GHQ/skills" HEAD~1
dogfood tenaoshi "$GHQ/tenaoshi" HEAD~1

echo "======== demo OK ========"
