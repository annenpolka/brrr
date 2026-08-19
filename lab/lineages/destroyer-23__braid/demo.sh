#!/usr/bin/env bash
# Reproduce braid fold-occupancy money shots. Does not rewrite the victim.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
BRAID="${BRAID:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-cbac00204512/braid}"
PLEA="${PLEA:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b0f-7ef0-76c0-9975-2d17551b311f/plea}"
PLAIT="${PLAIT:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b56-ac5a-7b03-a99f-437a44b4b3bf/plait}"
VICTIM="$(cd "$(dirname "$BRAID")" && pwd)"
chmod +x "$BRAID" "$HERE/attack.py" 2>/dev/null || true

PASS=0
FAIL=0
ok() { PASS=$((PASS + 1)); echo "  PASS  $1"; }
bad() { FAIL=$((FAIL + 1)); echo "  FAIL  $1" >&2; echo "        $2" >&2; }

jget() {
  python3 -c 'import json,sys; r=json.load(open(sys.argv[1])); print(eval(sys.argv[2], {"r": r, "len": len}))' "$1" "$2"
}

TMP="$(mktemp -d "${TMPDIR:-/tmp}/destroy-braid-demo.XXXXXX")"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

echo "======== 1. victim selftest ========"
if "$BRAID" --selftest >/dev/null; then
  ok "braid --selftest"
else
  bad "braid --selftest" "exit $?"
fi

echo "======== 2. STACK mid SUPERSEDED of beta3 (plea APPLIED+PENDING) ========"
"$BRAID" --json -C "$VICTIM/fixtures/trees/stack-mid" "$VICTIM/fixtures/stack.jsonl" >"$TMP/mid.json"
assert_occ="$(jget "$TMP/mid.json" 'r["occupy"]')"
assert_cmp="$(jget "$TMP/mid.json" 'r["compose"]')"
if [[ "$assert_cmp" == "SERIES" && "$assert_occ" == "SUPERSEDED" ]]; then
  ok "braid stack-mid occupy=SUPERSEDED of fold"
else
  bad "braid stack-mid" "compose=$assert_cmp occupy=$assert_occ"
fi
if [[ -x "$PLEA" ]]; then
  "$PLEA" --json --worktree -C "$VICTIM/fixtures/trees/stack-mid" "$VICTIM/fixtures/stack.jsonl" >"$TMP/plea.json" || true
  pc="$(jget "$TMP/plea.json" 'sorted(r["counts"].items())')"
  if [[ "$pc" == *APPLIED* && "$pc" == *PENDING* ]]; then
    ok "plea stack-mid APPLIED+PENDING of rounds"
  else
    bad "plea stack-mid" "counts=$pc"
  fi
else
  ok "plea missing (skipped)"
fi

echo "======== 3. inverted-clock fold, no same-tree ========"
pretty="$("$BRAID" -C "$VICTIM/fixtures/trees/stack-both" "$VICTIM/fixtures/stack.jsonl")"
if [[ "$pretty" == *"occupy=PENDING"* && "$pretty" != *"same-tree"* ]]; then
  ok "stack-both PENDING of origin, no same-tree table"
else
  bad "stack-both" "${pretty:0:200}"
fi

echo "======== 4. three-round STACK is SPLIT (no occupy) ========"
python3 - <<'PY' >"$TMP/stack-three.jsonl"
import json
rows = [
  ("r1","v1","v2","c1","2020-01-03T00:00:00Z"),
  ("r2","v2","v3","c2","2020-01-02T00:00:00Z"),
  ("r3","v3","v4","c3","2020-01-01T00:00:00Z"),
]
for i,b,a,c,t in rows:
    print(json.dumps({"id":i,"path":"app.py","start_line":2,"line":2,"before":[b],"after":[a],"original_commit_id":c,"created_at":t}))
PY
set +e
"$BRAID" "$TMP/stack-three.jsonl" >/dev/null
trc=$?
set -e
if [[ "$trc" == "1" ]]; then
  ok "three-round STACK rc=1 SPLIT (fold unaskable)"
else
  bad "three-round STACK" "rc=$trc want 1"
fi
if [[ -x "$PLAIT" ]]; then
  set +e
  "$PLAIT" "$TMP/stack-three.jsonl" >"$TMP/plait-3.out"
  prc=$?
  set -e
  if [[ "$prc" == "0" && "$(cat "$TMP/plait-3.out")" == *"SERIES"* ]]; then
    ok "plait three-round still SERIES"
  else
    bad "plait three-round" "rc=$prc"
  fi
fi

echo "======== 5. covering gap-fill absorbs unclaimed drift ========"
mkdir -p "$TMP/drift"
printf 'alpha\nBETA\ngamma\n' >"$TMP/drift/app.py"
"$BRAID" --json -C "$TMP/drift" "$VICTIM/fixtures/commute.jsonl" >"$TMP/drift.json"
d_occ="$(jget "$TMP/drift.json" 'r["occupy"]')"
d_aft="$(jget "$TMP/drift.json" 'r["composed"][0]["after"]')"
if [[ "$d_occ" == "PENDING" && "$d_aft" == *"BETA"* ]]; then
  ok "gap-fill PENDING of live canvas (BETA absorbed)"
else
  bad "gap-fill" "occupy=$d_occ after=$d_aft"
fi

echo "======== 6. replacement-as-union refused ========"
set +e
"$BRAID" "$VICTIM/fixtures/same-line-overlap-same-after.jsonl" >/dev/null
jrc=$?
"$BRAID" "$VICTIM/fixtures/jam.jsonl" >/dev/null
jam=$?
set -e
if [[ "$jrc" == "2" && "$jam" == "2" ]]; then
  ok "overlap-same-join + gold jam refuse occupy rc=2"
else
  bad "replacement refuse" "overlap_rc=$jrc jam_rc=$jam"
fi

echo "======== 7. empty-before disjoint is COMMUTE ========"
"$BRAID" --json --report-only "$VICTIM/fixtures/md-commute-noquote.md" >"$TMP/md.json"
mdc="$(jget "$TMP/md.json" 'r["compose"]')"
if [[ "$mdc" == "PARALLEL" ]]; then
  ok "md-noquote compose=PARALLEL (not SPLIT)"
else
  bad "md-noquote" "compose=$mdc"
fi

echo "======== 8. no --emit (hank's verb) ========"
set +e
"$BRAID" --emit >/dev/null 2>"$TMP/emit.err"
erc=$?
set -e
if [[ "$erc" != "0" ]] && grep -q "unrecognized arguments: --emit" "$TMP/emit.err"; then
  ok "braid has no --emit"
else
  bad "--emit" "rc=$erc $(cat "$TMP/emit.err")"
fi

echo
echo "PASS=$PASS FAIL=$FAIL"
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
exit 0
