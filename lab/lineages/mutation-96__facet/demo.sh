#!/usr/bin/env bash
# Extra args (e.g. ./demo.sh 0) are ignored.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
chmod +x "$ROOT/facet"
FACET="$ROOT/facet"

KIZU="${KIZU:-/Users/annenpolka/ghq/github.com/annenpolka/kizu}"

PASS=0
FAIL=0
assert() {
  local name="$1"
  shift
  if "$@"; then
    PASS=$((PASS + 1))
    echo "  ok  $name"
  else
    FAIL=$((FAIL + 1))
    echo "  FAIL $name" >&2
  fi
}

jtrue() {
  local name="$1" file="$2" expr="$3"
  if python3 -c "import json,sys; r=json.load(open(sys.argv[1])); assert $expr, r" "$file"; then
    PASS=$((PASS + 1))
    echo "  ok  $name"
  else
    FAIL=$((FAIL + 1))
    echo "  FAIL $name ($expr)" >&2
  fi
}

TMP="$(mktemp -d "${TMPDIR:-/tmp}/facet-demo.XXXXXX")"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

FIXTURE='{"packages":[{"name":"kizu","version":"0.7.0","id":"path+kizu#0.7.0"},{"name":"notify-debouncer-full","version":"0.7.0","id":"reg#notify-debouncer-full@0.7.0"}]}'

echo "======== 0. selftest ========"
"$FACET" --selftest

echo "======== 1. fixture: siblings vs greedy coincidence ========"
printf '%s' "$FIXTURE" | "$FACET" --json -n 'kizu@0.7.0' >"$TMP/fix.json"
echo "--- facet ---"
printf '%s' "$FIXTURE" | "$FACET" -n 'kizu@0.7.0'
jtrue "kind siblings" "$TMP/fix.json" "r['kind']=='siblings'"
jtrue "object packages[0]" "$TMP/fix.json" "r['object']['path']=='$.packages[0]'"
jtrue "object name kizu" "$TMP/fix.json" "r['object']['name']=='kizu'"
jtrue "keys name,version" "$TMP/fix.json" "r['object']['keys']==['name','version']"
jtrue "glue is @" "$TMP/fix.json" "any(p['kind']=='glue' and p['text']=='@' for p in r['pieces'])"
jtrue "greedy coincidence" "$TMP/fix.json" "r['greedy']['coincidence'] is True"
jtrue "greedy @0.7.0 from foreign id" "$TMP/fix.json" \
  "any(p['kind']=='from' and p['text']=='@0.7.0' and p['obj']=='$.packages[1]' and p['key']=='id' for p in r['greedy']['pieces'])"
jtrue "greedy foreign name" "$TMP/fix.json" \
  "any(p.get('obj_name')=='notify-debouncer-full' for p in r['greedy']['pieces'])"

echo "======== 2. skeptic: greedy longest-match is the wrong object ========"
python3 - "$FIXTURE" "$TMP" <<'PY'
import sys
doc = sys.argv[1].encode()
needle = b"kizu@0.7.0"
# beck-style greedy min_len=4
p, min_len, pieces = 0, 4, []
while p < len(needle):
    found = None
    for L in range(len(needle) - p, min_len - 1, -1):
        frag = needle[p:p+L]
        off = doc.find(frag)
        if off >= 0:
            found = (frag, off)
            break
    if found is None:
        p += 1
        continue
    pieces.append(found)
    p += len(found[0])
open(sys.argv[2] + "/greedy.txt", "w").write(repr(pieces))
assert pieces[0][0] == b"kizu"
assert pieces[1][0] == b"@0.7.0"
foreign = doc.find(b"notify-debouncer-full@0.7.0")
assert pieces[1][1] > foreign  # @0.7.0 sits inside the foreign pkgid
print("  greedy pieces", pieces)
PY
assert "skeptic greedy crossed packages" test -s "$TMP/greedy.txt"

echo "======== 3. nested name/version is NOT siblings ========"
printf '%s' '{"name":"kizu","inner":{"version":"0.7.0"}}' | "$FACET" --json -n 'kizu@0.7.0' >"$TMP/nest.json"
jtrue "nested not siblings" "$TMP/nest.json" "r['kind']!='siblings'"

echo "======== 4. split array is NOT siblings ========"
printf '%s' '[{"name":"kizu"},{"version":"0.7.0","id":"x@0.7.0"}]' | "$FACET" --json -n 'kizu@0.7.0' >"$TMP/split.json"
jtrue "split not siblings" "$TMP/split.json" "r['kind']!='siblings'"
jtrue "split greedy coincidence" "$TMP/split.json" "r['greedy']['coincidence'] is True"

echo "======== 5. pipeline printf | jq wrap ========"
if command -v jq >/dev/null; then
  "$FACET" --quiet --json -n 'kizu@0.7.0' \
    --sh "printf '%s' '$FIXTURE' | jq -r '.packages[] | select(.name==\"kizu\") | .name + \"@\" + .version'" \
    >"$TMP/jq.json"
  echo "--- facet ---"
  "$FACET" --quiet -n 'kizu@0.7.0' \
    --sh "printf '%s' '$FIXTURE' | jq -r '.packages[] | select(.name==\"kizu\") | .name + \"@\" + .version'"
  jtrue "jq wrap stage 1" "$TMP/jq.json" "r['wrap'] is not None and r['wrap']['stage']==1"
  jtrue "jq siblings still packages[0]" "$TMP/jq.json" "r['kind']=='siblings' and r['object']['path']=='$.packages[0]'"
  jtrue "jq json stage 0" "$TMP/jq.json" "r['object']['stage']==0"
else
  echo "  skip jq (missing)"
fi

echo "======== 6. kizu cargo metadata | facet ========"
if [[ -d "$KIZU" ]] && command -v cargo >/dev/null; then
  cargo metadata --format-version 1 --offline --manifest-path "$KIZU/Cargo.toml" >"$TMP/kizu-meta.json" 2>/dev/null
  "$FACET" --json -n 'kizu@0.7.0' --doc "$TMP/kizu-meta.json" >"$TMP/kizu.json"
  echo "--- facet ---"
  "$FACET" -n 'kizu@0.7.0' --doc "$TMP/kizu-meta.json"
  jtrue "kizu siblings" "$TMP/kizu.json" "r['kind']=='siblings'"
  jtrue "kizu package name" "$TMP/kizu.json" "r['object']['name']=='kizu'"
  jtrue "kizu keys name,version" "$TMP/kizu.json" "r['object']['keys']==['name','version']"
  jtrue "kizu path is a packages[N]" "$TMP/kizu.json" "r['object']['path'].startswith('\$.packages[')"
  jtrue "kizu greedy coincidence" "$TMP/kizu.json" "r['greedy']['coincidence'] is True"
  jtrue "kizu greedy foreign notify-debouncer-full" "$TMP/kizu.json" \
    "any(p.get('obj_name')=='notify-debouncer-full' and p['text']=='@0.7.0' for p in r['greedy']['pieces'])"
  jtrue "kizu glue not absorbed" "$TMP/kizu.json" "any(p['kind']=='glue' and p['text']=='@' for p in r['pieces'])"

  echo "======== 7. kizu cargo | jq pipeline ========"
  "$FACET" --quiet --cwd "$KIZU" --json -n 'kizu@0.7.0' --timeout 30 \
    --sh 'cargo metadata --format-version 1 --offline | jq -r ".packages[] | select(.name==\"kizu\") | .name + \"@\" + .version"' \
    >"$TMP/kizu-sh.json"
  echo "--- facet ---"
  "$FACET" --quiet --cwd "$KIZU" -n 'kizu@0.7.0' --timeout 30 \
    --sh 'cargo metadata --format-version 1 --offline | jq -r ".packages[] | select(.name==\"kizu\") | .name + \"@\" + .version"'
  jtrue "pipeline siblings kizu" "$TMP/kizu-sh.json" "r['kind']=='siblings' and r['object']['name']=='kizu'"
  jtrue "pipeline wrap jq" "$TMP/kizu-sh.json" "r['wrap'] is not None and r['wrap']['stage']==1 and 'jq' in r['wrap']['argv']"
  jtrue "pipeline json is cargo" "$TMP/kizu-sh.json" "r['object']['stage']==0 and 'cargo' in (r['object']['argv'] or '')"
  jtrue "pipeline greedy still coincidence" "$TMP/kizu-sh.json" "r['greedy']['coincidence'] is True"

  echo "======== 8. notify-debouncer-full@0.7.0 siblings, greedy ECHO of .id ========"
  "$FACET" --json -n 'notify-debouncer-full@0.7.0' --doc "$TMP/kizu-meta.json" >"$TMP/ndf.json"
  echo "--- facet ---"
  "$FACET" -n 'notify-debouncer-full@0.7.0' --doc "$TMP/kizu-meta.json"
  jtrue "ndf siblings" "$TMP/ndf.json" "r['kind']=='siblings' and r['object']['name']=='notify-debouncer-full'"
  jtrue "ndf not kizu" "$TMP/ndf.json" "r['object']['name']!='kizu'"
  jtrue "ndf keys name,version" "$TMP/ndf.json" "r['object']['keys']==['name','version']"
  jtrue "ndf greedy is echo not coincidence" "$TMP/ndf.json" "r['greedy']['echo'] is True and r['greedy']['coincidence'] is False"
  jtrue "ndf echo from .id" "$TMP/ndf.json" "any(p['kind']=='from' and p.get('key')=='id' for p in r['greedy']['pieces'])"

  echo "======== 9. version-only 0.7.0 is ambiguous occupancy ========"
  "$FACET" --json -n '0.7.0' --doc "$TMP/kizu-meta.json" >"$TMP/ver.json"
  echo "--- facet ---"
  "$FACET" -n '0.7.0' --doc "$TMP/kizu-meta.json"
  jtrue "version-only is field not siblings" "$TMP/ver.json" "r['kind']=='field'"
  jtrue "version-only is ambiguous" "$TMP/ver.json" "r['ambiguous'] is True"
  jtrue "version-only also notify-debouncer-full" "$TMP/ver.json" \
    "any(a.get('name')=='notify-debouncer-full' for a in r['also'])"
  jtrue "version-only also ratatui-macros" "$TMP/ver.json" \
    "any(a.get('name')=='ratatui-macros' for a in r['also'])"
  jtrue "composite needle is not ambiguous" "$TMP/kizu.json" "r['ambiguous'] is False"
else
  echo "  skip kizu cargo (missing $KIZU or cargo)"
fi

echo
echo "passed $PASS  failed $FAIL"
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
exit 0
