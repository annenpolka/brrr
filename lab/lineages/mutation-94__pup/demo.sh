#!/usr/bin/env bash
# Exercise pup: covering predicates in, occupancy eras out, without sh.
# git mv is FOLLOW. cp is COPY. ./demo.sh 0 — fixture + sitbone + kizu.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PUP="$ROOT/pup"
chmod +x "$PUP"
DITTO="${DITTO:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-cb6bc13617db/ditto}"
CHEAP=0
if [[ "${1:-}" == "0" ]]; then
  CHEAP=1
fi

if [[ ! -x "$PUP" ]]; then
  echo "demo: pup is not executable" >&2
  exit 2
fi

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

assert_eq() {
  local name="$1" got="$2" want="$3"
  if [[ "$got" == "$want" ]]; then
    PASS=$((PASS + 1))
    echo "  ok  $name"
  else
    FAIL=$((FAIL + 1))
    echo "  FAIL $name" >&2
    echo "       got:  $got" >&2
    echo "       want: $want" >&2
  fi
}

json_get() {
  python3 -c 'import json,sys; r=json.load(sys.stdin); '"$1"''
}

echo "== fixture: cp vs git mv, dest death, remaining blob, extract-and-edit =="
FIX="$(mktemp -d "${TMPDIR:-/tmp}/pup-demo.XXXXXX")"
cleanup() { rm -rf "$FIX"; }
trap cleanup EXIT

git -C "$FIX" init -q -b main
git -C "$FIX" config user.name "pup-demo"
git -C "$FIX" config user.email "pup@example.test"

mkdir -p "$FIX/nested/deep"
printf 'alpha\nbeta\ngamma\n' > "$FIX/a.rs"
printf 'ghost\n' > "$FIX/old name.txt"
printf 'keep\n' > "$FIX/keep.txt"
printf 'hello\n' > "$FIX/nested/deep/weird (1).txt"
git -C "$FIX" add a.rs "old name.txt" keep.txt "nested/deep/weird (1).txt"
git -C "$FIX" commit -q -m "t0: birth"
T0="$(git -C "$FIX" rev-parse HEAD)"

cp "$FIX/a.rs" "$FIX/b.rs"
git -C "$FIX" add b.rs
git -C "$FIX" commit -q -m "t1: cp a.rs b.rs"
T1="$(git -C "$FIX" rev-parse HEAD)"

git -C "$FIX" mv "old name.txt" "new name.txt"
git -C "$FIX" commit -q -m "t2: rename with spaces"
T2="$(git -C "$FIX" rev-parse HEAD)"

rm "$FIX/b.rs"
git -C "$FIX" add -A
git -C "$FIX" commit -q -m "t3: dest b.rs dies"
T3="$(git -C "$FIX" rev-parse HEAD)"

printf 'keep\n' > "$FIX/計画.md"
git -C "$FIX" add "計画.md"
git -C "$FIX" commit -q -m "t4: copy keep.txt to 計画.md"
T4="$(git -C "$FIX" rev-parse HEAD)"

mkdir -p "$FIX/vendor/nested"
git -C "$FIX/vendor/nested" init -q -b inner
git -C "$FIX/vendor/nested" config user.name "pup-demo"
git -C "$FIX/vendor/nested" config user.email "pup@example.test"
echo inner > "$FIX/vendor/nested/inner.txt"
git -C "$FIX/vendor/nested" add inner.txt
git -C "$FIX/vendor/nested" commit -q -m "inner commit"
echo 'vendor-marker' > "$FIX/vendor/marker.txt"
git -C "$FIX" add vendor/marker.txt
git -C "$FIX" commit -q -m "t5: nested git + marker"

N="$(git -C "$FIX" rev-list --count HEAD)"
assert_eq "fixture commit count" "$N" "6"

echo "-- pup T0 T1: internal ditto; cp is COPY dest occupancy"
CP_JSON="$("$PUP" -C "$FIX" --json "$T0" "$T1" || true)"
CP_KIND="$(json_get 'print(r.get("kind") or r["predicates"][0]["kind"])' <<<"$CP_JSON")"
CP_ID="$(json_get 'p=r["predicates"][0] if r.get("predicates") else r; print(" → ".join(p.get("identity") or []))' <<<"$CP_JSON")"
CP_NOW="$(json_get 'p=r["predicates"][0] if r.get("predicates") else r; print(int(p["holds_now"]), p["true_commits"])' <<<"$CP_JSON")"
CP_HOLD="$(json_get 'p=r["predicates"][0] if r.get("predicates") else r; print(" | ".join(",".join(e["holders"]) for e in p["eras"] if e["value"]))' <<<"$CP_JSON")"
CP_PAT="$(json_get 'p=r["predicates"][0] if r.get("predicates") else r; print("".join("T" if e["value"] else "F" for e in p["eras"]))' <<<"$CP_JSON")"
assert_eq "internal T0 T1 is copy" "$CP_KIND" "copy"
assert_eq "internal T0 T1 identity" "$CP_ID" "a.rs → b.rs"
assert_eq "internal T0 T1 now/true (dest lives t1-t2, dies t3; tip=HEAD)" "$CP_NOW" "0 2"
assert_eq "internal T0 T1 holder is dest" "$CP_HOLD" "b.rs"
assert_eq "internal T0 T1 era pattern dest birth then death" "$CP_PAT" "FTF"

echo "-- pup T1 T2: git mv is FOLLOW, not COPY"
MV_JSON="$("$PUP" -C "$FIX" --json "$T1" "$T2" || true)"
MV_KIND="$(json_get 'print(r.get("kind") or r["predicates"][0]["kind"])' <<<"$MV_JSON")"
MV_ID="$(json_get 'p=r["predicates"][0] if r.get("predicates") else r; print(" → ".join(p.get("identity") or []))' <<<"$MV_JSON")"
MV_NOW="$(json_get 'p=r["predicates"][0] if r.get("predicates") else r; print(int(p["holds_now"]), int(p["never_held"]))' <<<"$MV_JSON")"
assert_eq "internal T1 T2 is follow" "$MV_KIND" "follow"
assert_eq "internal T1 T2 identity" "$MV_ID" "old name.txt → new name.txt"
assert_eq "follow identity still holds" "$MV_NOW" "1 0"

echo "-- piped covering comment (no sh)"
PIPE_JSON="$(printf '%s\n' '# C   11  copy a.rs → b.rs' | "$PUP" -C "$FIX" --json || true)"
PIPE_ID="$(json_get 'p=r["predicates"][0] if r.get("predicates") else r; print(" → ".join(p.get("identity") or []))' <<<"$PIPE_JSON")"
PIPE_KIND="$(json_get 'print(r.get("kind") or r["predicates"][0]["kind"])' <<<"$PIPE_JSON")"
assert_eq "stdin copy glyph kind" "$PIPE_KIND" "copy"
assert_eq "stdin copy glyph identity" "$PIPE_ID" "a.rs → b.rs"

PIPEF_JSON="$(printf '%s\n' "# R   32  follow 'old name.txt' → 'new name.txt'" | "$PUP" -C "$FIX" --json || true)"
PIPEF_KIND="$(json_get 'print(r.get("kind") or r["predicates"][0]["kind"])' <<<"$PIPEF_JSON")"
PIPEF_ID="$(json_get 'p=r["predicates"][0] if r.get("predicates") else r; print(" → ".join(p.get("identity") or []))' <<<"$PIPEF_JSON")"
assert_eq "stdin follow glyph kind" "$PIPEF_KIND" "follow"
assert_eq "stdin follow glyph identity" "$PIPEF_ID" "old name.txt → new name.txt"

echo "-- Japanese dest copy of keep.txt"
KEEP_JSON="$("$PUP" -C "$FIX" --json "$T3" "$T4" || true)"
KEEP_ID="$(json_get 'p=r["predicates"][0] if r.get("predicates") else r; print(" → ".join(p.get("identity") or []))' <<<"$KEEP_JSON")"
KEEP_NOW="$(json_get 'p=r["predicates"][0] if r.get("predicates") else r; print(int(p["holds_now"]), p["true_commits"])' <<<"$KEEP_JSON")"
assert_eq "keep.txt → 計画.md copy identity" "$KEEP_ID" "keep.txt → 計画.md"
assert_eq "keep dest still lives" "$KEEP_NOW" "1 2"

echo "-- exit codes"
set +e
"$PUP" -C "$FIX" -q "$T3" "$T4"
KEEP_RC=$?
"$PUP" -C "$FIX" -q "$T0" "$T1"
DEAD_RC=$?
set -e
assert_eq "living copy dest exit 0" "$KEEP_RC" "0"
assert_eq "dead copy dest exit 1" "$DEAD_RC" "1"

echo "-- empty repo"
EMPTY="$(mktemp -d "${TMPDIR:-/tmp}/pup-empty.XXXXXX")"
git -C "$EMPTY" init -q -b main
set +e
EMPTY_ERR="$(printf '%s\n' '# C  11  copy a.rs → b.rs' | "$PUP" -C "$EMPTY" exists 2>&1)"
# pup does not take exists; covering stdin + empty history
EMPTY_ERR="$(printf '%s\n' '# C  11  copy a.rs → b.rs' | "$PUP" -C "$EMPTY" 2>&1)"
EMPTY_RC=$?
set -e
rm -rf "$EMPTY"
assert_eq "empty repo exit" "$EMPTY_RC" "2"
assert "empty repo mentions empty" grep -q "empty" <<<"$EMPTY_ERR"

echo "-- remaining blob: exclusive same-SHA is COPY of living holder, not FOLLOW of twin"
REMF="$(mktemp -d "${TMPDIR:-/tmp}/pup-remain.XXXXXX")"
git -C "$REMF" init -q -b main
git -C "$REMF" config user.name "pup-demo"
git -C "$REMF" config user.email "pup@example.test"
printf 'same\n' > "$REMF/a.rs"
printf 'same\n' > "$REMF/twin.rs"
git -C "$REMF" add a.rs twin.rs
git -C "$REMF" commit -q -m t0
RT0="$(git -C "$REMF" rev-parse HEAD)"
rm "$REMF/twin.rs"
cp "$REMF/a.rs" "$REMF/b.rs"
git -C "$REMF" add -A
git -C "$REMF" commit -q -m "twin dies, a.rs copied to b.rs"
RT1="$(git -C "$REMF" rev-parse HEAD)"
RJ="$("$PUP" -C "$REMF" --json "$RT0" "$RT1" || true)"
assert_eq "remaining covering is copy a.rs → b.rs" "$(json_get 'p=r["predicates"][0] if r.get("predicates") else r; print(p.get("kind"), " → ".join(p.get("identity") or []))' <<<"$RJ")" "copy a.rs → b.rs"
assert_eq "remaining dest holds now" "$(json_get 'print(int(r["holds_now"]))' <<<"$RJ")" "1"
assert "remaining is not follow twin → b.rs" python3 -c 'import json,sys; r=json.loads(sys.argv[1]);
preds=r.get("predicates") or [r]
sys.exit(0 if all(p.get("kind")!="follow" for p in preds) else 1)' "$RJ"
rm -rf "$REMF"

echo "-- extract-and-edit: dest-on-B vs source-on-A"
SIM="$(mktemp -d "${TMPDIR:-/tmp}/pup-sim.XXXXXX")"
git -C "$SIM" init -q -b main
git -C "$SIM" config user.name "pup-demo"
git -C "$SIM" config user.email "pup@example.test"
python3 - "$SIM" <<'PY'
import sys
root = sys.argv[1]
lines = ["fn keep() {}"] + [f"fn install_{i}() {{ {i} }}" for i in range(20)] + ["fn leftover() {}"]
open(f"{root}/god.rs", "w").write("\n".join(lines) + "\n")
PY
git -C "$SIM" add god.rs
git -C "$SIM" commit -q -m t0
ST0="$(git -C "$SIM" rev-parse HEAD)"
python3 - "$SIM" <<'PY'
import sys
root = sys.argv[1]
lines = open(f"{root}/god.rs").read().splitlines()
open(f"{root}/install.rs", "w").write("\n".join(ln for ln in lines if "install_" in ln) + "\n")
open(f"{root}/god.rs", "w").write("\n".join(ln for ln in lines if "install_" not in ln) + "\n")
PY
git -C "$SIM" add god.rs install.rs
git -C "$SIM" commit -q -m extract
ST1="$(git -C "$SIM" rev-parse HEAD)"
SJ="$("$PUP" -C "$SIM" --json "$ST0" "$ST1" || true)"
assert_eq "extract identity" "$(json_get 'p=r["predicates"][0] if r.get("predicates") else r; print(" → ".join(p.get("identity") or []))' <<<"$SJ")" "god.rs → install.rs"
assert_eq "extract kind copy" "$(json_get 'print(r.get("kind") or r["predicates"][0]["kind"])' <<<"$SJ")" "copy"
assert_eq "extract dest holds" "$(json_get 'print(int(r["holds_now"]))' <<<"$SJ")" "1"
rm -rf "$SIM"

echo "-- --now sees an uncommitted extra holder of a covering dest"
printf 'keep\n' > "$FIX/dirty-copy.txt"
# covering is keep.txt → 計画.md; dirty dest is not that covering
# pipe a copy covering of keep.txt → dirty-copy.txt
NOW_JSON="$(printf '%s\n' '# C  11  copy keep.txt → dirty-copy.txt' | "$PUP" -C "$FIX" --now --json || true)"
NOW_HOLD="$(json_get 'p=r["predicates"][0] if r.get("predicates") else r; print(int(p["holds_now"]), p["eras"][-1]["end"]["kind"])' <<<"$NOW_JSON")"
assert_eq "uncommitted dest via --now" "$NOW_HOLD" "1 worktree"
rm -f "$FIX/dirty-copy.txt"

if [[ -x "$DITTO" ]]; then
  echo "-- ditto | pup (the pipe, not sh)"
  DPIPE="$("$DITTO" -C "$FIX" --color never "$T0" "$T1" | "$PUP" -C "$FIX" --json || true)"
  assert_eq "ditto|pup T0 T1 kind" "$(json_get 'print(r.get("kind") or r["predicates"][0]["kind"])' <<<"$DPIPE")" "copy"
  assert_eq "ditto|pup T0 T1 identity" "$(json_get 'p=r["predicates"][0] if r.get("predicates") else r; print(" → ".join(p.get("identity") or []))' <<<"$DPIPE")" "a.rs → b.rs"
  DWALK="$("$DITTO" -C "$FIX" --walks "$T0" "$T1" | "$PUP" -C "$FIX" --json || true)"
  assert_eq "ditto --walks | pup recovers copy" "$(json_get 'print(r.get("kind") or r["predicates"][0]["kind"])' <<<"$DWALK")" "copy"
  DREN="$("$DITTO" -C "$FIX" --color never "$T1" "$T2" | "$PUP" -C "$FIX" --json || true)"
  assert_eq "ditto|pup rename is follow" "$(json_get 'print(r.get("kind") or r["predicates"][0]["kind"])' <<<"$DREN")" "follow"
else
  echo "skip ditto | pup (ditto not present)"
fi

echo
echo "== real repo: sitbone FocusRiverView is a unique birth, not copy/follow =="
SITBONE="/Users/annenpolka/ghq/github.com/annenpolka/sitbone"
if [[ -d "$SITBONE/.git" || -f "$SITBONE/.git" ]]; then
  if [[ -x "$DITTO" ]]; then
    SF_JSON="$("$DITTO" -C "$SITBONE" --color never --limit 6 14b1d6e^ 14b1d6e | "$PUP" -C "$SITBONE" --json || true)"
  else
    SF_JSON="$("$PUP" -C "$SITBONE" --json 14b1d6e^ 14b1d6e || true)"
  fi
  SF_NEVER="$(json_get 'print(int(r.get("never_held", 1)), r.get("kind") or "none")' <<<"$SF_JSON")"
  SF_HINT="$(json_get 'print(" ".join(r.get("hints") or []))' <<<"$SF_JSON")"
  assert_eq "sitbone covering is not copy/follow" "$SF_NEVER" "1 none"
  assert "sitbone hint points at held / unique" python3 -c 'import sys; h=sys.argv[1].lower(); sys.exit(0 if ("held" in h or "unique" in h or "grep" in h or "not copy" in h) else 1)' "$SF_HINT"
  echo "---- sitbone ditto|pup (human) ----"
  if [[ -x "$DITTO" ]]; then
    "$DITTO" -C "$SITBONE" --color never --limit 6 14b1d6e^ 14b1d6e | "$PUP" -C "$SITBONE" --color never || true
  else
    "$PUP" -C "$SITBONE" --color never 14b1d6e^ 14b1d6e || true
  fi
else
  echo "skip sitbone (not present)"
fi

echo
echo "== real repo: kizu C056 copy vs R100 follow =="
KIZU="/Users/annenpolka/ghq/github.com/annenpolka/kizu"
if [[ -d "$KIZU/.git" || -f "$KIZU/.git" ]]; then
  echo "-- first-parent: dest occupancy of the C056 covering (pipe)"
  if [[ -x "$DITTO" ]]; then
    KF_JSON="$("$DITTO" -C "$KIZU" --color never --limit 6 5671a72^ 5671a72 | "$PUP" -C "$KIZU" --json || true)"
  else
    KF_JSON="$("$PUP" -C "$KIZU" --json 5671a72^ 5671a72 || true)"
  fi
  KF_KIND="$(json_get 'print(r.get("kind") or r["predicates"][0]["kind"])' <<<"$KF_JSON")"
  KF_ID="$(json_get 'p=r["predicates"][0] if r.get("predicates") else r; print(" → ".join(p.get("identity") or []))' <<<"$KF_JSON")"
  KF_NOW="$(json_get 'p=r["predicates"][0] if r.get("predicates") else r; print(int(p["holds_now"]), p["true_commits"], p["commits_scanned"])' <<<"$KF_JSON")"
  KF_HOLD="$(json_get 'p=r["predicates"][0] if r.get("predicates") else r; print(" | ".join(",".join(e["holders"]) for e in p["eras"] if e["value"]))' <<<"$KF_JSON")"
  KF_ORIGIN="$(json_get 'p=r["predicates"][0] if r.get("predicates") else r; trues=[e for e in p["eras"] if e["value"]]; print((trues[0].get("origin") or {}).get("short",""))' <<<"$KF_JSON")"
  assert_eq "kizu first-parent covering is copy" "$KF_KIND" "copy"
  assert_eq "kizu first-parent identity is C056" "$KF_ID" "src/init.rs → src/init/install.rs"
  assert_eq "kizu first-parent now/true/scanned" "$KF_NOW" "1 5 24"
  assert_eq "kizu first-parent holder is install.rs" "$KF_HOLD" "src/init/install.rs"
  assert_eq "kizu first-parent origin is off-mainline copy 5671a72" "$KF_ORIGIN" "5671a72"

  echo "-- --full: dest exists from 5671a72"
  if [[ "$CHEAP" == "1" ]]; then
    KU_JSON="$("$PUP" -C "$KIZU" --full --json 5671a72^ 5671a72 || true)"
  else
    if [[ -x "$DITTO" ]]; then
      KU_JSON="$("$DITTO" -C "$KIZU" --color never --limit 6 5671a72^ 5671a72 | "$PUP" -C "$KIZU" --full --json || true)"
    else
      KU_JSON="$("$PUP" -C "$KIZU" --full --json 5671a72^ 5671a72 || true)"
    fi
  fi
  KU_N="$(json_get 'p=r["predicates"][0] if r.get("predicates") else r; print(int(p["holds_now"]), p["true_commits"])' <<<"$KU_JSON")"
  KU_ID="$(json_get 'p=r["predicates"][0] if r.get("predicates") else r; print(" → ".join(p.get("identity") or []))' <<<"$KU_JSON")"
  assert_eq "kizu --full identity" "$KU_ID" "src/init.rs → src/init/install.rs"
  assert_eq "kizu --full now/true=12" "$KU_N" "1 12"

  echo "-- --walks recovers copy from dest-exists paste"
  if [[ -x "$DITTO" ]]; then
    KW="$("$DITTO" -C "$KIZU" --walks --limit 6 5671a72^ 5671a72 | "$PUP" -C "$KIZU" --json || true)"
    assert_eq "walks-only C056 is copy" "$(json_get 'print(r.get("kind") or r["predicates"][0]["kind"])' <<<"$KW")" "copy"
    assert_eq "walks-only C056 names source" "$(json_get 'p=r["predicates"][0] if r.get("predicates") else r; print(p.get("from"))' <<<"$KW")" "src/init.rs"
  fi

  echo "-- R100 covering is FOLLOW, not COPY"
  if [[ -x "$DITTO" ]]; then
    KR_JSON="$("$DITTO" -C "$KIZU" --color never --limit 6 4e37f16^ 4e37f16 | "$PUP" -C "$KIZU" --json || true)"
  else
    KR_JSON="$("$PUP" -C "$KIZU" --json 4e37f16^ 4e37f16 || true)"
  fi
  KR_KIND="$(json_get 'print(r.get("kind") or r["predicates"][0]["kind"])' <<<"$KR_JSON")"
  KR_ID="$(json_get 'p=r["predicates"][0] if r.get("predicates") else r; print(" → ".join(p.get("identity") or []))' <<<"$KR_JSON")"
  KR_NOW="$(json_get 'p=r["predicates"][0] if r.get("predicates") else r; print(int(p["holds_now"]), p["true_commits"], p["commits_scanned"])' <<<"$KR_JSON")"
  assert_eq "kizu R100 covering is follow" "$KR_KIND" "follow"
  assert_eq "kizu R100 identity" "$KR_ID" "deep-research-ai-agent-hooks.md → docs/deep-research-ai-agent-hooks.md"
  assert_eq "kizu R100 first-parent now/true/scanned" "$KR_NOW" "1 21 24"

  if [[ "$CHEAP" != "1" ]]; then
    KR_FULL="$("$PUP" -C "$KIZU" --full --json 4e37f16^ 4e37f16 || true)"
    assert_eq "kizu R100 --full true=187" "$(json_get 'p=r["predicates"][0] if r.get("predicates") else r; print(int(p["holds_now"]), p["true_commits"])' <<<"$KR_FULL")" "1 187"
  fi

  echo "---- kizu ditto|pup C056 first-parent (human) ----"
  if [[ -x "$DITTO" ]]; then
    "$DITTO" -C "$KIZU" --color never --limit 6 5671a72^ 5671a72 | "$PUP" -C "$KIZU" --color never || true
  else
    "$PUP" -C "$KIZU" --color never 5671a72^ 5671a72 || true
  fi
  echo "---- kizu R100 first-parent (human) ----"
  "$PUP" -C "$KIZU" --color never 4e37f16^ 4e37f16 || true
else
  echo "skip kizu (not present)"
fi

echo
echo "PASS=$PASS FAIL=$FAIL"
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
echo "demo ok"
exit 0
