#!/usr/bin/env bash
# Compose first; occupy the nits with NFC keys; refuse JAM/SPLIT.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
TILDE="$ROOT/tilde"
chmod +x "$TILDE"

PASS=0
FAIL=0

ok() { PASS=$((PASS + 1)); echo "  PASS  $1"; }
bad() { FAIL=$((FAIL + 1)); echo "  FAIL  $1" >&2; echo "        $2" >&2; }

assert_eq() {
  local name="$1" got="$2" want="$3"
  if [[ "$got" == "$want" ]]; then
    ok "$name"
  else
    bad "$name" "got=$got want=$want"
  fi
}

assert_contains() {
  local name="$1" hay="$2" needle="$3"
  if [[ "$hay" == *"$needle"* ]]; then
    ok "$name"
  else
    bad "$name" "missing '$needle' in: ${hay:0:240}"
  fi
}

jget() {
  python3 -c 'import json,sys; r=json.load(open(sys.argv[1])); print(eval(sys.argv[2], {"r": r, "len": len}))' "$1" "$2"
}

echo "======== 1. selftest ========"
if "$TILDE" --selftest; then
  ok "selftest"
else
  bad "selftest" "exit $?"
fi

DEMO="$(mktemp -d "${TMPDIR:-/tmp}/tilde-demo.XXXXXX")"
cleanup() { rm -rf "$DEMO"; }
trap cleanup EXIT

echo "======== 2. gold COMMUTE occupy of the nits (not a live-gap canvas) ========"
"$TILDE" --json -C "$ROOT/fixtures/trees/commute" "$ROOT/fixtures/commute.jsonl" > "$DEMO/commute.json"
assert_eq "commute compose" "$(jget "$DEMO/commute.json" 'r["compose"]')" "PARALLEL"
assert_eq "commute occupy" "$(jget "$DEMO/commute.json" 'r["occupy"]')" "PENDING"
assert_eq "commute occupied" "$(jget "$DEMO/commute.json" 'r["occupied"]')" "True"
assert_eq "commute one composed" "$(jget "$DEMO/commute.json" 'len(r["composed"])')" "1"
assert_eq "commute both ids" "$(jget "$DEMO/commute.json" '",".join(r["composed"][0]["strands"])')" "alice,bob"
assert_eq "commute covering false (nits, not live gap)" "$(jget "$DEMO/commute.json" 'r["composed"][0]["covering"]')" "False"
assert_eq "commute nits after-image" "$(jget "$DEMO/commute.json" 'r["composed"][0]["after"]')" "['ALPHA', 'GAMMA']"
pretty="$("$TILDE" --report-only -C "$ROOT/fixtures/trees/commute" "$ROOT/fixtures/commute.jsonl")"
assert_contains "commute pretty occupy PENDING" "$pretty" "occupy=PENDING"
assert_contains "commute pretty one occupy line" "$pretty" "PENDING    app.py"

echo "======== 3. A already applied: SUPERSEDED of the composed image ========"
"$TILDE" --json -C "$ROOT/fixtures/trees/commute-a-only" "$ROOT/fixtures/commute.jsonl" > "$DEMO/aonly.json"
assert_eq "a-only occupy SUPERSEDED" "$(jget "$DEMO/aonly.json" 'r["occupy"]')" "SUPERSEDED"
assert_eq "a-only still occupied (composed ok)" "$(jget "$DEMO/aonly.json" 'r["occupied"]')" "True"
"$TILDE" --json -C "$ROOT/fixtures/trees/commute-applied" "$ROOT/fixtures/commute.jsonl" > "$DEMO/applied.json"
assert_eq "both-applied occupy APPLIED" "$(jget "$DEMO/applied.json" 'r["occupy"]')" "APPLIED"

echo "======== 4. gold JAM rc=2, do not occupy ========"
set +e
"$TILDE" "$ROOT/fixtures/jam.jsonl" >"$DEMO/jam.out" 2>"$DEMO/jam.err"
jam_rc=$?
set -e
assert_eq "jam exit 2" "$jam_rc" "2"
assert_contains "jam refused" "$(cat "$DEMO/jam.out")" "occupy=—"
assert_contains "jam no occupy section" "$(cat "$DEMO/jam.out")" "refused occupy"
"$TILDE" --json --report-only "$ROOT/fixtures/jam.jsonl" > "$DEMO/jam.json"
assert_eq "jam occupied false" "$(jget "$DEMO/jam.json" 'r["occupied"]')" "False"
assert_eq "jam occupy null" "$(jget "$DEMO/jam.json" 'r["occupy"]')" "None"
assert_eq "jam composed empty" "$(jget "$DEMO/jam.json" 'r["composed"]')" "[]"

echo "======== 5. SPLIT rc=1, replacement not union ========"
set +e
"$TILDE" "$ROOT/fixtures/split.jsonl" >/dev/null
split_rc=$?
"$TILDE" "$ROOT/fixtures/same-line-split.jsonl" >/dev/null
word_rc=$?
"$TILDE" "$ROOT/fixtures/same-line-overlap-same-after.jsonl" >/dev/null
ov_rc=$?
set -e
assert_eq "split exit 1" "$split_rc" "1"
assert_eq "same-line two afters SPLIT" "$word_rc" "1"
assert_eq "overlap same-join JAM" "$ov_rc" "2"

echo "======== 6. STACK fold occupancy (not each round) ========"
"$TILDE" --json -C "$ROOT/fixtures/trees/stack" "$ROOT/fixtures/stack.jsonl" > "$DEMO/stack.json"
assert_eq "stack compose SERIES" "$(jget "$DEMO/stack.json" 'r["compose"]')" "SERIES"
assert_eq "stack origin occupy PENDING" "$(jget "$DEMO/stack.json" 'r["occupy"]')" "PENDING"
assert_eq "stack fold after" "$(jget "$DEMO/stack.json" 'r["composed"][0]["after"]')" "['beta3']"
"$TILDE" --json -C "$ROOT/fixtures/trees/stack-after" "$ROOT/fixtures/stack.jsonl" > "$DEMO/stack-after.json"
assert_eq "stack after APPLIED" "$(jget "$DEMO/stack-after.json" 'r["occupy"]')" "APPLIED"
"$TILDE" --json -C "$ROOT/fixtures/trees/stack-mid" "$ROOT/fixtures/stack.jsonl" > "$DEMO/stack-mid.json"
assert_eq "stack mid SUPERSEDED of fold" "$(jget "$DEMO/stack-mid.json" 'r["occupy"]')" "SUPERSEDED"
"$TILDE" --json -C "$ROOT/fixtures/trees/stack-both" "$ROOT/fixtures/stack.jsonl" > "$DEMO/stack-both.json"
both="$(jget "$DEMO/stack-both.json" 'r["occupy"]')"
if [[ "$both" == "APPLIED" ]]; then
  bad "stack-both must not APPLIED of the wrong tree" "occupy=$both"
else
  ok "stack-both not APPLIED (got $both)"
fi

echo "======== 7. ECHO is a locus; two sites commute and occupy the union ========"
"$TILDE" --json -C "$ROOT/fixtures/trees/echo" "$ROOT/fixtures/echo.jsonl" > "$DEMO/echo.json"
assert_eq "echo compose" "$(jget "$DEMO/echo.json" 'r["compose"]')" "ECHO"
assert_eq "echo one part" "$(jget "$DEMO/echo.json" 'len(r["composed"][0]["parts"])')" "1"
"$TILDE" --json -C "$ROOT/fixtures/trees/dup-sites" "$ROOT/fixtures/echo-dup-sites.jsonl" > "$DEMO/dup.json"
assert_eq "dup-sites compose PARALLEL" "$(jget "$DEMO/dup.json" 'r["compose"]')" "PARALLEL"
assert_eq "dup-sites two parts" "$(jget "$DEMO/dup.json" 'len(r["composed"][0]["parts"])')" "2"
assert_eq "dup-sites occupy PENDING" "$(jget "$DEMO/dup.json" 'r["occupy"]')" "PENDING"

echo "======== 8. empty markdown before is COMMUTE, not SPLIT ========"
"$TILDE" --json --report-only "$ROOT/fixtures/md-commute-noquote.md" > "$DEMO/mdnq.json"
assert_eq "md-noquote compose PARALLEL" "$(jget "$DEMO/mdnq.json" 'r["compose"]')" "PARALLEL"
assert_eq "md-noquote recon none" "$(jget "$DEMO/mdnq.json" 'r["strands"][0]["recon"]')" "none"
"$TILDE" --json -C "$ROOT/fixtures/trees/commute" "$ROOT/fixtures/md-commute-noquote.md" > "$DEMO/mdnq-tree.json"
assert_eq "md-noquote occupy PENDING of after-image" "$(jget "$DEMO/mdnq-tree.json" 'r["occupy"]')" "PENDING"
assert_eq "md-noquote nits after" "$(jget "$DEMO/mdnq-tree.json" 'r["composed"][0]["after"]')" "['ALPHA', 'GAMMA']"
assert_eq "md-noquote not a live covering" "$(jget "$DEMO/mdnq-tree.json" 'r["composed"][0]["covering"]')" "False"

echo "======== 9. quoted markdown matches JSON commute ========"
"$TILDE" --json -C "$ROOT/fixtures/trees/commute" "$ROOT/fixtures/stream.md" > "$DEMO/stream.json"
assert_eq "stream.md compose PARALLEL" "$(jget "$DEMO/stream.json" 'r["compose"]')" "PARALLEL"
assert_eq "stream.md occupy PENDING" "$(jget "$DEMO/stream.json" 'r["occupy"]')" "PENDING"

echo "======== 10. subset STACK is the series fold ========"
"$TILDE" --json -C "$ROOT/fixtures/trees/insert-fn" "$ROOT/fixtures/stack-subset.jsonl" > "$DEMO/subset.json"
assert_eq "subset compose SERIES" "$(jget "$DEMO/subset.json" 'r["compose"]')" "SERIES"
assert_eq "subset fold after" "$(jget "$DEMO/subset.json" 'r["composed"][0]["after"][-2]')" "    return 2"

echo "======== 11. A↔B cycle JAM, no occupy ========"
set +e
"$TILDE" "$ROOT/fixtures/stack-cycle.jsonl" >/dev/null
cyc=$?
set -e
assert_eq "cycle exit 2" "$cyc" "2"

echo "======== 12. cli/cli PR #7 commuting pair, one occupancy of the nits ========"
"$TILDE" --json -C "$ROOT/fixtures/trees/cli-orig" "$ROOT/fixtures/cli-pr7.json" > "$DEMO/cli.json"
assert_eq "cli n=2 suggestions" "$(jget "$DEMO/cli.json" 'r["n"]')" "2"
assert_eq "cli compose PARALLEL" "$(jget "$DEMO/cli.json" 'r["compose"]')" "PARALLEL"
assert_eq "cli occupy PENDING" "$(jget "$DEMO/cli.json" 'r["occupy"]')" "PENDING"
assert_eq "cli one composed" "$(jget "$DEMO/cli.json" 'len(r["composed"])')" "1"
assert_eq "cli covering false" "$(jget "$DEMO/cli.json" 'r["composed"][0]["covering"]')" "False"
assert_contains "cli ids" "$(jget "$DEMO/cli.json" '",".join(r["composed"][0]["strands"])')" "333030758"
assert_contains "cli ids 216" "$(jget "$DEMO/cli.json" '",".join(r["composed"][0]["strands"])')" "333031216"

echo "======== 13. empty / binary / junk jsonl / TTY ========"
set +e
printf '' | "$TILDE" - >/dev/null
empty_rc=$?
printf '\x00\xff' | "$TILDE" - >/dev/null 2>"$DEMO/bin.err"
bin_rc=$?
printf '%s\n' '{"id":"a","path":"app.py","line":1,"before":["alpha"],"after":["ALPHA"]}' 'this is not json' | "$TILDE" - >/dev/null 2>"$DEMO/junk.err"
junk_rc=$?
tty_out="$(python3 -c '
import pty, subprocess, sys
master, slave = pty.openpty()
p = subprocess.run([sys.argv[1]], stdin=slave, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print(p.returncode)
' "$TILDE")"
set -e
assert_eq "empty stdin rc 0" "$empty_rc" "0"
assert_eq "binary stdin rc 3" "$bin_rc" "3"
assert_eq "junk jsonl rc 3" "$junk_rc" "3"
assert_eq "TTY no args rc 3" "$tty_out" "3"

echo "======== 14. braid gold fixtures (dogfood) ========"
"$TILDE" --json -C "$ROOT/fixtures/trees/commute" "$ROOT/fixtures/commute.jsonl" > "$DEMO/bgold.json"
assert_eq "braid-gold commute occupy PENDING" "$(jget "$DEMO/bgold.json" 'r["occupy"]')" "PENDING"
set +e
"$TILDE" "$ROOT/fixtures/jam.jsonl" >/dev/null
bgjam=$?
set -e
assert_eq "braid-gold jam rc 2" "$bgjam" "2"

echo "======== 15. shift insert+edit is one PENDING union of nits ========"
"$TILDE" --json -C "$ROOT/fixtures/trees/shift" "$ROOT/fixtures/shift.jsonl" > "$DEMO/shift.json"
assert_eq "shift compose PARALLEL" "$(jget "$DEMO/shift.json" 'r["compose"]')" "PARALLEL"
assert_eq "shift occupy PENDING" "$(jget "$DEMO/shift.json" 'r["occupy"]')" "PENDING"
assert_eq "shift nits after" "$(jget "$DEMO/shift.json" 'r["composed"][0]["after"]')" "['a', 'a2', 'D']"

echo "======== 16. NFC café path pair is one occupy ========"
"$TILDE" --json --report-only "$ROOT/fixtures/nfc-two-paths.jsonl" > "$DEMO/nfc-paths.json"
assert_eq "nfc paths files=1" "$(jget "$DEMO/nfc-paths.json" 'r["files"]')" "1"
assert_eq "nfc paths compose PARALLEL" "$(jget "$DEMO/nfc-paths.json" 'r["compose"]')" "PARALLEL"
assert_eq "nfc paths one composed" "$(jget "$DEMO/nfc-paths.json" 'len(r["composed"])')" "1"
"$TILDE" --json -C "$ROOT/fixtures/trees/nfc-file" "$ROOT/fixtures/nfc-two-paths.jsonl" > "$DEMO/nfc-file.json"
assert_eq "nfc-file occupy PENDING" "$(jget "$DEMO/nfc-file.json" 'r["occupy"]')" "PENDING"
assert_eq "nfc-file one occupy" "$(jget "$DEMO/nfc-file.json" 'len(r["composed"])')" "1"
"$TILDE" --json -C "$ROOT/fixtures/trees/nfd-file" "$ROOT/fixtures/nfc-two-paths.jsonl" > "$DEMO/nfd-file.json"
assert_eq "nfd-file occupy PENDING" "$(jget "$DEMO/nfd-file.json" 'r["occupy"]')" "PENDING"

echo "======== 17. NFC line image vs NFD tree is PENDING, not SUPERSEDED ========"
"$TILDE" --json -C "$ROOT/fixtures/trees/nfd-word" "$ROOT/fixtures/nfc-content.jsonl" > "$DEMO/nfc-vs-nfd.json"
assert_eq "nfc-content vs nfd-word PENDING" "$(jget "$DEMO/nfc-vs-nfd.json" 'r["occupy"]')" "PENDING"
"$TILDE" --json -C "$ROOT/fixtures/trees/nfc-word" "$ROOT/fixtures/nfd-content.jsonl" > "$DEMO/nfd-vs-nfc.json"
assert_eq "nfd-content vs nfc-word PENDING" "$(jget "$DEMO/nfd-vs-nfc.json" 'r["occupy"]')" "PENDING"
"$TILDE" --json -C "$ROOT/fixtures/trees/nfc-word" "$ROOT/fixtures/nfc-content.jsonl" > "$DEMO/nfc-match.json"
assert_eq "matched NFC PENDING" "$(jget "$DEMO/nfc-match.json" 'r["occupy"]')" "PENDING"

echo "======== 18. covering occupancy is of the nits, not a chimera ========"
"$TILDE" --json -C "$ROOT/fixtures/trees/window-drift-mid" "$ROOT/fixtures/window-commute.jsonl" > "$DEMO/drift.json"
assert_eq "gap-drift occupy PENDING" "$(jget "$DEMO/drift.json" 'r["occupy"]')" "PENDING"
assert_eq "gap-drift covering false" "$(jget "$DEMO/drift.json" 'r["composed"][0]["covering"]')" "False"
assert_eq "gap-drift before is nits" "$(jget "$DEMO/drift.json" 'r["composed"][0]["before"]')" "['alpha', 'gamma']"
"$TILDE" --json -C "$ROOT/fixtures/trees/window-pad1" "$ROOT/fixtures/window-commute.jsonl" > "$DEMO/pad.json"
assert_eq "pad-shift occupy PENDING (not chimera SUPERSEDED)" "$(jget "$DEMO/pad.json" 'r["occupy"]')" "PENDING"
"$TILDE" --json -C "$ROOT/fixtures/trees/window-a-only" "$ROOT/fixtures/window-commute.jsonl" > "$DEMO/waonly.json"
assert_eq "window a-only SUPERSEDED of nits" "$(jget "$DEMO/waonly.json" 'r["occupy"]')" "SUPERSEDED"

echo "======== 19. --ignore-space occupy of a claimed before ========"
"$TILDE" --json -C "$ROOT/fixtures/trees/commute" "$ROOT/fixtures/ws-before.jsonl" > "$DEMO/ws-raw.json"
assert_eq "trailing space occupy SUPERSEDED" "$(jget "$DEMO/ws-raw.json" 'r["occupy"]')" "SUPERSEDED"
"$TILDE" --ignore-space --json -C "$ROOT/fixtures/trees/commute" "$ROOT/fixtures/ws-before.jsonl" > "$DEMO/ws-ign.json"
assert_eq "ignore-space occupy PENDING" "$(jget "$DEMO/ws-ign.json" 'r["occupy"]')" "PENDING"
"$TILDE" --ignore-space --json -C "$ROOT/fixtures/trees/stack-mid" "$ROOT/fixtures/stack.jsonl" > "$DEMO/ws-mid.json"
assert_eq "ignore-space stack-mid still SUPERSEDED" "$(jget "$DEMO/ws-mid.json" 'r["occupy"]')" "SUPERSEDED"

echo
echo "PASS=$PASS FAIL=$FAIL"
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
exit 0
