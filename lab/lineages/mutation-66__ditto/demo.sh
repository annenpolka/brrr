#!/usr/bin/env bash
# Exercise ditto: covering set; copy vs follow, not two exists / not a false follow.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
DITTO="$ROOT/ditto"
chmod +x "$DITTO"

HELD="${HELD:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01a85-796f-76d0-988f-5c2c16399eaa/held}"
BERTH="${BERTH:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b6b-7144-7812-8fcb-cbf1c493bd9a/berth}"

if [[ ! -x "$DITTO" ]]; then
  echo "demo: ditto is not executable" >&2
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

echo "== fixture: oscillating path, copy vs rename, remaining blob, nested git =="
FIX="$(mktemp -d "${TMPDIR:-/tmp}/ditto-demo.XXXXXX")"
cleanup() { rm -rf "$FIX"; }
trap cleanup EXIT

git -C "$FIX" init -q -b main
git -C "$FIX" config user.name "ditto-demo"
git -C "$FIX" config user.email "ditto@example.test"

mkdir -p "$FIX/nested/deep"
printf 'keep\nTOKEN_A\n' > "$FIX/keep.txt"
printf 'born\n' > "$FIX/oscillate.txt"
printf 'ghost\n' > "$FIX/old name.txt"
printf 'hello\n' > "$FIX/nested/deep/weird (1).txt"
git -C "$FIX" add keep.txt oscillate.txt "old name.txt" "nested/deep/weird (1).txt"
git -C "$FIX" commit -q -m "t0: birth"
T0="$(git -C "$FIX" rev-parse HEAD)"

rm "$FIX/oscillate.txt"
git -C "$FIX" add -A
git -C "$FIX" commit -q -m "t1: kill oscillate"
T1="$(git -C "$FIX" rev-parse HEAD)"

printf 'reborn\n' > "$FIX/oscillate.txt"
printf 'keep\n' > "$FIX/keep.txt"
printf '計画\n' > "$FIX/計画.md"
git -C "$FIX" add oscillate.txt keep.txt "計画.md"
git -C "$FIX" commit -q -m "t2: revive oscillate, drop TOKEN_A"
T2="$(git -C "$FIX" rev-parse HEAD)"

git -C "$FIX" mv "old name.txt" "new name.txt"
git -C "$FIX" commit -q -m "t3: rename with spaces"
T3="$(git -C "$FIX" rev-parse HEAD)"

rm "$FIX/oscillate.txt"
printf 'other\nTOKEN_A\n' > "$FIX/other.txt"
git -C "$FIX" add -A
git -C "$FIX" commit -q -m "t4: kill oscillate, TOKEN_A reincarnates"
T4="$(git -C "$FIX" rev-parse HEAD)"

mkdir -p "$FIX/vendor/nested"
git -C "$FIX/vendor/nested" init -q -b inner
git -C "$FIX/vendor/nested" config user.name "ditto-demo"
git -C "$FIX/vendor/nested" config user.email "ditto@example.test"
echo inner > "$FIX/vendor/nested/inner.txt"
git -C "$FIX/vendor/nested" add inner.txt
git -C "$FIX/vendor/nested" commit -q -m "inner commit"
echo 'vendor-marker' > "$FIX/vendor/marker.txt"
git -C "$FIX" add vendor/marker.txt
git -C "$FIX" commit -q -m "t5: nested git + marker"
T5="$(git -C "$FIX" rev-parse HEAD)"

printf 'keep\n' > "$FIX/other.txt"
git -C "$FIX" add other.txt
git -C "$FIX" commit -q -m "t6: TOKEN_A gone again"
T6="$(git -C "$FIX" rev-parse HEAD)"

N="$(git -C "$FIX" rev-list --count HEAD)"
assert_eq "fixture commit count" "$N" "7"

echo "-- t0 vs t1: oscillate.txt dies, TOKEN_A still shared"
T01="$("$DITTO" -C "$FIX" --json --color never "$T0" "$T1")"
python3 - "$T01" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
preds = r["sheaf"]
held = [p["held"] for p in preds]
assert any("oscillate" in h for h in held), held
assert not any("TOKEN_A" in p["pattern"] for p in preds), preds
assert any(p["true_on"]=="A" and "oscillate" in p["pattern"] for p in preds), held
walks = r["walks"]
assert walks, walks
assert any(w["tool"]=="held" and "oscillate" in w["line"] for w in walks), walks
assert all(w["line"].startswith("held ") for w in walks), walks
print("t01-ok")
PY
assert "t0 vs t1 oscillate sheaf + held walks, TOKEN_A silent" true

echo "-- t1 vs t2: TOKEN_A dies, 計画.md born, oscillate revives"
T12="$("$DITTO" -C "$FIX" --json --color never "$T1" "$T2")"
python3 - "$T12" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
preds = r["sheaf"]
held = [p["held"] for p in preds]
assert any(p["true_on"]=="A" and ("TOKEN_A" in p["pattern"] or p["pattern"]=="TOKEN") for p in preds), held
assert any(p["true_on"]=="B" and ("計画" in p["held"] or (p["kind"]=="exists" and ".md" in p["pattern"])) for p in preds), held
assert any(p["true_on"]=="B" and "oscillate" in p["pattern"] for p in preds), held
assert 1 <= len(preds) <= 8, len(preds)
print("t12-ok")
PY
assert "t1 vs t2 TOKEN_A / 計画.md / oscillate in sheaf" true

echo "-- t2 vs t3: git mv is ONE follow, not two exists, not a copy"
T23="$("$DITTO" -C "$FIX" --json --color never "$T2" "$T3")"
python3 - "$T23" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
preds = r["sheaf"]
follows = [p for p in preds if p["kind"]=="follow"]
copies = [p for p in preds if p["kind"]=="copy"]
assert len(follows) == 1, preds
assert copies == [], copies
assert follows[0]["from"] == "old name.txt", follows
assert follows[0]["to"] == "new name.txt", follows
assert r["delta"]["renames"] == 1
assert r["delta"]["copies"] == 0
assert not any(p["kind"]=="exists" for p in preds), [p["held"] for p in preds]
walks = r["walks"]
assert any(w.get("follow") and "--follow" in w["line"] and "exists" in w["line"] for w in walks), walks
assert not any(w.get("copy") for w in walks), walks
print("t23-ok")
PY
assert "rename is one follow identity; walks carry --follow; not a copy" true

echo "-- --no-follow recovers sheaf's two exists"
T23N="$("$DITTO" -C "$FIX" --no-follow --json --color never "$T2" "$T3")"
python3 - "$T23N" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
preds = r["sheaf"]
assert not any(p["kind"]=="follow" for p in preds), preds
held = [p["held"] for p in preds]
assert any("old name" in h for h in held), held
assert any("new name" in h for h in held), held
assert len(preds) >= 2, held
print("t23-nofollow-ok")
PY
assert "--no-follow is two path predicates, not one identity" true

echo "-- t4 vs t6: TOKEN_A reincarnation then death"
T46="$("$DITTO" -C "$FIX" --json --color never "$T4" "$T6")"
python3 - "$T46" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
assert any(p["true_on"]=="A" and "TOKEN_A" in p["pattern"] for p in r["sheaf"])
print("t46-ok")
PY
assert "t4 vs t6 TOKEN_A on A only" true

echo "-- --held / --berth / --walks / exit codes"
WALK_HELD="$("$DITTO" -C "$FIX" --walks --held "$T0" "$T2")"
assert "default/held walks are ready-to-run held lines" grep -Eq '^held -C ' <<<"$WALK_HELD"
assert "held walks carry the predicate" grep -Eq ' (exists|grep) ' <<<"$WALK_HELD"

WALK_BERTH="$("$DITTO" -C "$FIX" --walks --berth "$T0" "$T2")"
assert "berth walker omits held" grep -Eq '^berth -C ' <<<"$WALK_BERTH"
assert "berth walker does not emit held" grep -Evq '^held ' <<<"$WALK_BERTH"

HUMAN="$("$DITTO" -C "$FIX" --color never "$T0" "$T1")"
assert "human sheaf is comment-prefixed" grep -Eq '^# ditto ' <<<"$HUMAN"
assert "human walk lines are unindented (pipeable)" grep -Eq '^held -C ' <<<"$HUMAN"

set +e
"$DITTO" -C "$FIX" -q "$T0" "$T0"
ID_RC=$?
"$DITTO" -C "$FIX" -q "$T0" "$T1"
DIFF_RC=$?
set -e
assert_eq "identical trees exit" "$ID_RC" "1"
assert_eq "different trees exit" "$DIFF_RC" "0"

echo "-- --now / worktree resurrection"
printf 'dirty\n' > "$FIX/oscillate.txt"
WT="$("$DITTO" -C "$FIX" --json HEAD :worktree || true)"
python3 - "$WT" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
assert r["b"]["kind"]=="worktree"
assert any(p["true_on"]=="B" and "oscillate" in p["pattern"] for p in r["sheaf"]), [p["held"] for p in r["sheaf"]]
assert any(w.get("now") for w in r["walks"]), r["walks"]
print("wt-ok")
PY
assert "HEAD vs :worktree sees uncommitted oscillate and --now walks" true
rm -f "$FIX/oscillate.txt"

echo "-- empty repo is a clean error, not a stacktrace"
EMPTY="$(mktemp -d "${TMPDIR:-/tmp}/ditto-empty.XXXXXX")"
git -C "$EMPTY" init -q -b main
set +e
EMPTY_ERR="$("$DITTO" -C "$EMPTY" HEAD HEAD~1 2>&1)"
EMPTY_RC=$?
set -e
rm -rf "$EMPTY"
assert_eq "empty repo exit" "$EMPTY_RC" "2"
assert "empty repo mentions empty" grep -qi "empty\|needed a single revision\|cannot resolve" <<<"$EMPTY_ERR"

echo "-- cp a.rs b.rs (both exist) is COPY, not follow, not leftover exists-as-birth only"
COPYF="$(mktemp -d "${TMPDIR:-/tmp}/ditto-cp.XXXXXX")"
git -C "$COPYF" init -q -b main
git -C "$COPYF" config user.name "ditto-demo"
git -C "$COPYF" config user.email "ditto@example.test"
printf 'alpha\nbeta\ngamma\n' > "$COPYF/a.rs"
git -C "$COPYF" add a.rs
git -C "$COPYF" commit -q -m "t0"
C0="$(git -C "$COPYF" rev-parse HEAD)"
cp "$COPYF/a.rs" "$COPYF/b.rs"
git -C "$COPYF" add b.rs
git -C "$COPYF" commit -q -m "t1: cp a.rs b.rs"
C1="$(git -C "$COPYF" rev-parse HEAD)"
CJ="$("$DITTO" -C "$COPYF" --json --color never "$C0" "$C1")"
python3 - "$CJ" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
copies = [p for p in r["sheaf"] if p["kind"]=="copy"]
follows = [p for p in r["sheaf"] if p["kind"]=="follow"]
assert len(copies) == 1, r["sheaf"]
assert follows == [], follows
assert copies[0]["from"] == "a.rs", copies
assert copies[0]["to"] == "b.rs", copies
assert r["delta"]["copies"] == 1
assert r["delta"]["renames"] == 0
walks = r["walks"]
assert any(w.get("copy") and "exists b.rs" in w["line"] for w in walks), walks
assert not any("--follow" in w["line"] for w in walks), walks
print("cp-ok")
PY
assert "exact cp is copy a.rs → b.rs; walks exist dest without --follow" true

echo "-- copy + edit dest is still copy, plus the content glyph (not leftover grep b.rs)"
printf 'alpha\nbeta\ngamma\nextra_token\n' > "$COPYF/b.rs"
git -C "$COPYF" add b.rs
git -C "$COPYF" commit -q -m "t2: edit dest"
C2="$(git -C "$COPYF" rev-parse HEAD)"
# A=t0 (a.rs only) vs C2 (a.rs + edited b.rs) — still a copy of the A blob
CEJ="$("$DITTO" -C "$COPYF" --json --color never "$C0" "$C2")"
python3 - "$CEJ" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
copies = [p for p in r["sheaf"] if p["kind"]=="copy"]
follows = [p for p in r["sheaf"] if p["kind"]=="follow"]
assert len(copies) == 1, r["sheaf"]
assert follows == [], follows
assert copies[0]["from"]=="a.rs" and copies[0]["to"]=="b.rs", copies
held = " ".join(p["held"] for p in r["sheaf"])
assert "extra_token" in held, held
assert "grep b.rs" not in held, held
print("cpedit-ok")
PY
assert "copy+edit is copy + extra_token, not leftover grep b.rs, not follow" true

echo "-- --no-copy downcasts dest to a birth"
CJN="$("$DITTO" -C "$COPYF" --no-copy --json --color never "$C0" "$C1")"
python3 - "$CJN" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
assert not any(p["kind"]=="copy" for p in r["sheaf"]), r["sheaf"]
assert any("b.rs" in p["held"] or "b.rs" in p["pattern"] for p in r["sheaf"]), [p["held"] for p in r["sheaf"]]
print("nocopy-ok")
PY
assert "--no-copy treats dest as a birth, not a copy identity" true
rm -rf "$COPYF"

echo "-- remaining blob: exclusive same-SHA is COPY not FOLLOW"
REMF="$(mktemp -d "${TMPDIR:-/tmp}/ditto-remain.XXXXXX")"
git -C "$REMF" init -q -b main
git -C "$REMF" config user.name "ditto-demo"
git -C "$REMF" config user.email "ditto@example.test"
printf 'same\n' > "$REMF/a.rs"
printf 'same\n' > "$REMF/twin.rs"
git -C "$REMF" add a.rs twin.rs
git -C "$REMF" commit -q -m "t0"
R0="$(git -C "$REMF" rev-parse HEAD)"
rm "$REMF/twin.rs"
cp "$REMF/a.rs" "$REMF/b.rs"
git -C "$REMF" add -A
git -C "$REMF" commit -q -m "t1: twin dies, a.rs copied to b.rs"
R1="$(git -C "$REMF" rev-parse HEAD)"
RJ="$("$DITTO" -C "$REMF" --json --color never "$R0" "$R1")"
python3 - "$RJ" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
kinds = [(i["kind"], i["a"], i["b"]) for i in r["delta"]["identities"]]
assert ("copied", "a.rs", "b.rs") in kinds, kinds
assert any(i["kind"]=="died" and i["a"]=="twin.rs" for i in r["delta"]["identities"]), kinds
assert r["delta"]["renames"] == 0
assert r["delta"]["copies"] == 1
assert not any(p["kind"]=="follow" for p in r["sheaf"]), r["sheaf"]
copies = [p for p in r["sheaf"] if p["kind"]=="copy"]
assert copies[0]["from"]=="a.rs" and copies[0]["to"]=="b.rs", copies
assert any("twin" in p["held"] or "twin" in p["pattern"] for p in r["sheaf"]), [p["held"] for p in r["sheaf"]]
print("remain-ok")
PY
assert "blob still on A: copy a.rs → b.rs plus twin death, not follow twin → b.rs" true
rm -rf "$REMF"

echo "-- mv + edit is still one identity, plus the content glyph"
EDIT="$(mktemp -d "${TMPDIR:-/tmp}/ditto-edit.XXXXXX")"
git -C "$EDIT" init -q -b main
git -C "$EDIT" config user.name "ditto-demo"
git -C "$EDIT" config user.email "ditto@example.test"
printf 'alpha\nbeta\ngamma\n' > "$EDIT/a.rs"
git -C "$EDIT" add a.rs
git -C "$EDIT" commit -q -m "t0"
E0="$(git -C "$EDIT" rev-parse HEAD)"
git -C "$EDIT" mv a.rs b.rs
printf 'alpha\nbeta\ngamma\ndelta_token\n' > "$EDIT/b.rs"
git -C "$EDIT" add b.rs
git -C "$EDIT" commit -q -m "t1"
E1="$(git -C "$EDIT" rev-parse HEAD)"
EJ="$("$DITTO" -C "$EDIT" --json --color never "$E0" "$E1")"
python3 - "$EJ" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
kinds = [p["kind"] for p in r["sheaf"]]
assert "follow" in kinds, r["sheaf"]
assert "copy" not in kinds, r["sheaf"]
assert r["delta"]["renames"] == 1
held = " ".join(p["held"] for p in r["sheaf"])
assert "delta_token" in held, held
assert "grep b.rs" not in held, held
print("mvedit-ok")
PY
assert "mv+edit is follow + content token, not leftover grep b.rs, not copy" true
rm -rf "$EDIT"

echo "-- directory rewrite compresses to one follow glob"
DIRF="$(mktemp -d "${TMPDIR:-/tmp}/ditto-dir.XXXXXX")"
git -C "$DIRF" init -q -b main
git -C "$DIRF" config user.name "ditto-demo"
git -C "$DIRF" config user.email "ditto@example.test"
mkdir -p "$DIRF/src"
echo one > "$DIRF/src/one.rs"
echo two > "$DIRF/src/two.rs"
echo three > "$DIRF/src/three.rs"
git -C "$DIRF" add src
git -C "$DIRF" commit -q -m "t0"
D0="$(git -C "$DIRF" rev-parse HEAD)"
mkdir -p "$DIRF/lib"
git -C "$DIRF" mv src/one.rs lib/one.rs
git -C "$DIRF" mv src/two.rs lib/two.rs
git -C "$DIRF" mv src/three.rs lib/three.rs
git -C "$DIRF" commit -q -m "t1"
D1="$(git -C "$DIRF" rev-parse HEAD)"
DJ="$("$DITTO" -C "$DIRF" --json --color never "$D0" "$D1")"
python3 - "$DJ" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
follows = [p for p in r["sheaf"] if p["kind"]=="follow"]
assert len(follows) == 1, r["sheaf"]
assert follows[0]["from"] == "src/*", follows
assert follows[0]["to"] == "lib/*", follows
assert r["delta"]["renames"] == 3
assert r["delta"]["copies"] == 0
print("dir-ok")
PY
assert "three git mvs of a tree are one src/* → lib/* follow" true
rm -rf "$DIRF"

echo "-- directory copy (src remains) compresses to one copy glob"
DIRC="$(mktemp -d "${TMPDIR:-/tmp}/ditto-dircp.XXXXXX")"
git -C "$DIRC" init -q -b main
git -C "$DIRC" config user.name "ditto-demo"
git -C "$DIRC" config user.email "ditto@example.test"
mkdir -p "$DIRC/src"
echo one > "$DIRC/src/one.rs"
echo two > "$DIRC/src/two.rs"
echo three > "$DIRC/src/three.rs"
git -C "$DIRC" add src
git -C "$DIRC" commit -q -m "t0"
DC0="$(git -C "$DIRC" rev-parse HEAD)"
mkdir -p "$DIRC/lib"
cp "$DIRC/src/one.rs" "$DIRC/lib/one.rs"
cp "$DIRC/src/two.rs" "$DIRC/lib/two.rs"
cp "$DIRC/src/three.rs" "$DIRC/lib/three.rs"
git -C "$DIRC" add lib
git -C "$DIRC" commit -q -m "t1: copy src to lib"
DC1="$(git -C "$DIRC" rev-parse HEAD)"
DCJ="$("$DITTO" -C "$DIRC" --json --color never "$DC0" "$DC1")"
python3 - "$DCJ" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
copies = [p for p in r["sheaf"] if p["kind"]=="copy"]
follows = [p for p in r["sheaf"] if p["kind"]=="follow"]
assert len(copies) == 1, r["sheaf"]
assert follows == [], follows
assert copies[0]["from"] == "src/*", copies
assert copies[0]["to"] == "lib/*", copies
assert r["delta"]["copies"] == 3
assert r["delta"]["renames"] == 0
assert not any("--follow" in w["line"] for w in r["walks"]), r["walks"]
print("dircp-ok")
PY
assert "three cps of a tree while src remains are one src/* → lib/* copy" true
rm -rf "$DIRC"

if [[ -x "$HELD" ]]; then
  echo "-- generated held line actually runs (grep / exists dest, no --follow)"
  LINE="$("$DITTO" -C "$FIX" --walks --held "$T0" "$T1" | head -1)"
  RUN="${LINE/#held /$HELD }"
  set +e
  HELD_ERR="$(eval "$RUN" 2>&1)"
  HELD_RC=$?
  set -e
  assert "held walk is parseable (exit 0 or 1)" test "$HELD_RC" -eq 0 -o "$HELD_RC" -eq 1
  assert "held walk printed eras" grep -Eq 'TRUE|FALSE|now=' <<<"$HELD_ERR"
else
  echo "skip live held (binary not present)"
fi

if [[ -x "$BERTH" ]]; then
  echo "-- generated berth --follow line actually runs on the rename"
  BLINE="$("$DITTO" -C "$FIX" --walks --berth "$T2" "$T3" | head -1)"
  BRUN="${BLINE/#berth /$BERTH }"
  set +e
  BERTH_ERR="$(eval "$BRUN" 2>&1)"
  BERTH_RC=$?
  set -e
  assert "berth follow walk is parseable (exit 0 or 1)" test "$BERTH_RC" -eq 0 -o "$BERTH_RC" -eq 1
  assert "berth follow walk printed occupancy" grep -Eq 'TRUE|FALSE|now=|identity' <<<"$BERTH_ERR"
else
  echo "skip live berth (binary not present)"
fi

echo
echo "== real repo: sitbone FocusRiverView island =="
SITBONE="/Users/annenpolka/ghq/github.com/annenpolka/sitbone"
if [[ -d "$SITBONE/.git" || -f "$SITBONE/.git" ]]; then
  echo "-- birth 14b1d6e^ vs 14b1d6e (file appears)"
  SBIRTH="$("$DITTO" -C "$SITBONE" --json --color never 14b1d6e^ 14b1d6e)"
  python3 - "$SBIRTH" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
held = [p["held"] for p in r["sheaf"]]
assert any("FocusRiverView" in h for h in held), held
assert not any("がるパ" in h for h in held), held
assert any(p["true_on"]=="B" and "FocusRiverView" in p["held"] for p in r["sheaf"])
assert any(w["tool"]=="held" and "FocusRiverView" in w["line"] for w in r["walks"]), r["walks"]
print("sitbone-birth-ok")
PY
  assert "sitbone birth cover is grep FocusRiverView, not leftover CJK" true

  echo "-- death 70ec7df^ vs 70ec7df (file disappears)"
  SDEATH="$("$DITTO" -C "$SITBONE" --json --color never 70ec7df^ 70ec7df)"
  python3 - "$SDEATH" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
assert any(p["true_on"]=="A" and "FocusRiverView" in p["held"] for p in r["sheaf"]), [p["held"] for p in r["sheaf"]]
print("sitbone-death-ok")
PY
  assert "sitbone death sheaf names FocusRiverView on A" true

  echo "-- island 14b1d6e vs HEAD (git log -- path is empty)"
  SHEAD="$("$DITTO" -C "$SITBONE" --json --color never --limit 6 14b1d6e HEAD)"
  python3 - "$SHEAD" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
assert any(p["true_on"]=="A" and "FocusRiverView" in p["held"] for p in r["sheaf"]), [p["held"] for p in r["sheaf"]]
assert any(w["full"] and "FocusRiverView" in w["line"] and "--full" in w["line"] for w in r["walks"]), r["walks"]
print("sitbone-island-ok")
PY
  assert "island vs HEAD sheaf keeps FocusRiverView and --full walks" true

  echo "---- sitbone birth (human) ----"
  "$DITTO" -C "$SITBONE" --color never --limit 4 14b1d6e^ 14b1d6e | head -40
else
  echo "skip sitbone (not present)"
fi

echo
echo "== real repo: kizu CLAUDE.md birth + jsx + R100 rename vs C056 copy =="
KIZU="/Users/annenpolka/ghq/github.com/annenpolka/kizu"
if [[ -d "$KIZU/.git" || -f "$KIZU/.git" ]]; then
  K1="$("$DITTO" -C "$KIZU" --json --color never e1098c8^ e1098c8)"
  python3 - "$K1" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
held = [p["held"] for p in r["sheaf"]]
assert any("CLAUDE" in h for h in held), held
assert r["walks"], r["walks"]
print("kizu-claude-ok")
PY
  assert "kizu CLAUDE.md birth is in the sheaf + walks" true

  K2="$("$DITTO" -C "$KIZU" --json --color never --limit 8 04adde1^ 04adde1)"
  python3 - "$K2" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
held = " ".join(p["held"] for p in r["sheaf"])
assert "jsx" in held.lower() or "tsx" in held.lower() or "js_ts" in held, held
print("kizu-jsx-ok")
PY
  assert "kizu jsx/tsx commit is named by the sheaf" true

  K3="$("$DITTO" -C "$KIZU" --json --color never --limit 6 4e37f16^ 4e37f16)"
  python3 - "$K3" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
follows = [p for p in r["sheaf"] if p["kind"]=="follow"]
copies = [p for p in r["sheaf"] if p["kind"]=="copy"]
assert len(follows) == 1, [p["held"] for p in r["sheaf"]]
assert copies == [], copies
assert follows[0]["from"] == "deep-research-ai-agent-hooks.md"
assert follows[0]["to"] == "docs/deep-research-ai-agent-hooks.md"
assert any("--follow" in w["line"] and "deep-research-ai-agent-hooks.md" in w["line"] for w in r["walks"])
assert any("ui.rs" in "".join(p["covers"]) or "char" in p["pattern"] or "ui" in p["held"] for p in r["sheaf"]), [p["held"] for p in r["sheaf"]]
print("kizu-rename-ok")
PY
  assert "kizu R100 markdown move is one follow, not copy, plus ui.rs content" true
  echo "---- kizu rename 4e37f16 ----"
  "$DITTO" -C "$KIZU" --color never --limit 4 4e37f16^ 4e37f16 | head -30

  echo "-- kizu C056: src/init.rs still present, install.rs born (git recorded copy)"
  K4="$("$DITTO" -C "$KIZU" --json --color never --limit 6 5671a72^ 5671a72)"
  python3 - "$K4" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
copies = [p for p in r["sheaf"] if p["kind"]=="copy"]
follows = [p for p in r["sheaf"] if p["kind"]=="follow"]
assert follows == [], [p["held"] for p in r["sheaf"]]
assert len(copies) == 1, [p["held"] for p in r["sheaf"]]
assert copies[0]["from"] == "src/init.rs", copies
assert copies[0]["to"] == "src/init/install.rs", copies
assert r["delta"]["copies"] == 1
assert r["delta"]["renames"] == 0
held = " ".join(p["held"] for p in r["sheaf"])
assert "exists *install*" not in held, held
assert not any("--follow" in w["line"] for w in r["walks"] if w.get("copy")), r["walks"]
assert any(w.get("copy") and "install.rs" in w["line"] for w in r["walks"]), r["walks"]
print("kizu-copy-ok")
PY
  assert "kizu C056 is copy src/init.rs → src/init/install.rs, not follow, not exists *install*" true
  echo "---- kizu copy 5671a72 ----"
  "$DITTO" -C "$KIZU" --color never --limit 4 5671a72^ 5671a72 | head -30
else
  echo "skip kizu (not present)"
fi

echo
echo "== real repo: tenaoshi 第一級 / MAN-023 =="
TENA="/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi"
if [[ -d "$TENA/.git" || -f "$TENA/.git" ]]; then
  TN="$("$DITTO" -C "$TENA" --json --color never 70b450d^ 70b450d)"
  python3 - "$TN" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
held = " ".join(p["held"] for p in r["sheaf"])
assert "MAN-023" in held or "第一級" in held, held
assert "向けに調整" not in held, held
assert "がるパ" not in held, held
print("tenaoshi-ok")
PY
  assert "tenaoshi cover is MAN-023/第一級, not leftover CJK" true
  echo "---- tenaoshi policy ----"
  "$DITTO" -C "$TENA" --color never --limit 4 70b450d^ 70b450d | head -30
else
  echo "skip tenaoshi (not present)"
fi

echo
echo "== real repo: skills recent delta =="
SKILLS="/Users/annenpolka/ghq/github.com/annenpolka/skills"
if [[ -d "$SKILLS/.git" || -f "$SKILLS/.git" ]]; then
  SK="$("$DITTO" -C "$SKILLS" --json --color never --limit 6 HEAD~1 HEAD)"
  python3 - "$SK" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
assert r["sheaf"], r
assert r["walks"], r
assert all(w["tool"]=="held" for w in r["walks"])
print("skills-ok")
PY
  assert "skills HEAD~1..HEAD emits a sheaf + held walks" true
else
  echo "skip skills (not present)"
fi

echo
echo "PASS=$PASS FAIL=$FAIL"
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
echo "demo ok"
exit 0
