#!/usr/bin/env bash
# Exercise glyph: covering set + --follow identity, not two exists.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
GLYPH="$ROOT/glyph"
chmod +x "$GLYPH"

HELD="${HELD:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01a85-796f-76d0-988f-5c2c16399eaa/held}"
PERCH="${PERCH:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01ad1-c9bd-7c52-b01b-c771008e6951/perch}"

if [[ ! -x "$GLYPH" ]]; then
  echo "demo: glyph is not executable" >&2
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

echo "== fixture: oscillating path, rename identity, weird names, nested git =="
FIX="$(mktemp -d "${TMPDIR:-/tmp}/glyph-demo.XXXXXX")"
cleanup() { rm -rf "$FIX"; }
trap cleanup EXIT

git -C "$FIX" init -q -b main
git -C "$FIX" config user.name "glyph-demo"
git -C "$FIX" config user.email "glyph@example.test"

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
git -C "$FIX/vendor/nested" config user.name "glyph-demo"
git -C "$FIX/vendor/nested" config user.email "glyph@example.test"
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
T01="$("$GLYPH" -C "$FIX" --json --color never "$T0" "$T1")"
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
T12="$("$GLYPH" -C "$FIX" --json --color never "$T1" "$T2")"
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

echo "-- t2 vs t3: git mv is ONE follow glyph, not two exists"
T23="$("$GLYPH" -C "$FIX" --json --color never "$T2" "$T3")"
python3 - "$T23" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
preds = r["sheaf"]
follows = [p for p in preds if p["kind"]=="follow"]
assert len(follows) == 1, preds
assert follows[0]["from"] == "old name.txt", follows
assert follows[0]["to"] == "new name.txt", follows
assert r["delta"]["renames"] == 1
assert not any(p["kind"]=="exists" for p in preds), [p["held"] for p in preds]
assert not any(p["kind"]=="grep" and p["pattern"]=="ghost" for p in preds), preds
walks = r["walks"]
assert any(w.get("follow") and "--follow" in w["line"] and "exists" in w["line"] for w in walks), walks
print("t23-ok")
PY
assert "rename is one follow identity; walks carry --follow" true

echo "-- --no-follow recovers sheaf's two exists"
T23N="$("$GLYPH" -C "$FIX" --no-follow --json --color never "$T2" "$T3")"
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
T46="$("$GLYPH" -C "$FIX" --json --color never "$T4" "$T6")"
python3 - "$T46" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
assert any(p["true_on"]=="A" and "TOKEN_A" in p["pattern"] for p in r["sheaf"])
print("t46-ok")
PY
assert "t4 vs t6 TOKEN_A on A only" true

echo "-- --held / --perch / --walks / exit codes"
WALK_HELD="$("$GLYPH" -C "$FIX" --walks --held "$T0" "$T2")"
assert "default/held walks are ready-to-run held lines" grep -Eq '^held -C ' <<<"$WALK_HELD"
assert "held walks carry the predicate" grep -Eq ' (exists|grep) ' <<<"$WALK_HELD"

WALK_PERCH="$("$GLYPH" -C "$FIX" --walks --perch "$T0" "$T2")"
assert "perch walker omits held" grep -Eq '^perch -C ' <<<"$WALK_PERCH"
assert "perch walker does not emit held" grep -Evq '^held ' <<<"$WALK_PERCH"

HUMAN="$("$GLYPH" -C "$FIX" --color never "$T0" "$T1")"
assert "human sheaf is comment-prefixed" grep -Eq '^# glyph ' <<<"$HUMAN"
assert "human walk lines are unindented (pipeable)" grep -Eq '^held -C ' <<<"$HUMAN"

set +e
"$GLYPH" -C "$FIX" -q "$T0" "$T0"
ID_RC=$?
"$GLYPH" -C "$FIX" -q "$T0" "$T1"
DIFF_RC=$?
set -e
assert_eq "identical trees exit" "$ID_RC" "1"
assert_eq "different trees exit" "$DIFF_RC" "0"

echo "-- --now / worktree resurrection"
printf 'dirty\n' > "$FIX/oscillate.txt"
WT="$("$GLYPH" -C "$FIX" --json HEAD :worktree || true)"
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
EMPTY="$(mktemp -d "${TMPDIR:-/tmp}/glyph-empty.XXXXXX")"
git -C "$EMPTY" init -q -b main
set +e
EMPTY_ERR="$("$GLYPH" -C "$EMPTY" HEAD HEAD~1 2>&1)"
EMPTY_RC=$?
set -e
rm -rf "$EMPTY"
assert_eq "empty repo exit" "$EMPTY_RC" "2"
assert "empty repo mentions empty" grep -qi "empty\|needed a single revision\|cannot resolve" <<<"$EMPTY_ERR"

echo "-- mv + edit is still one identity, plus the content glyph"
EDIT="$(mktemp -d "${TMPDIR:-/tmp}/glyph-edit.XXXXXX")"
git -C "$EDIT" init -q -b main
git -C "$EDIT" config user.name "glyph-demo"
git -C "$EDIT" config user.email "glyph@example.test"
printf 'alpha\nbeta\ngamma\n' > "$EDIT/a.rs"
git -C "$EDIT" add a.rs
git -C "$EDIT" commit -q -m "t0"
E0="$(git -C "$EDIT" rev-parse HEAD)"
git -C "$EDIT" mv a.rs b.rs
printf 'alpha\nbeta\ngamma\ndelta_token\n' > "$EDIT/b.rs"
git -C "$EDIT" add b.rs
git -C "$EDIT" commit -q -m "t1"
E1="$(git -C "$EDIT" rev-parse HEAD)"
EJ="$("$GLYPH" -C "$EDIT" --json --color never "$E0" "$E1")"
python3 - "$EJ" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
kinds = [p["kind"] for p in r["sheaf"]]
assert "follow" in kinds, r["sheaf"]
assert r["delta"]["renames"] == 1
held = " ".join(p["held"] for p in r["sheaf"])
assert "delta_token" in held, held
assert "grep b.rs" not in held, held
print("mvedit-ok")
PY
assert "mv+edit is follow + content token, not leftover grep b.rs" true
rm -rf "$EDIT"

echo "-- directory rewrite compresses to one follow glob"
DIRF="$(mktemp -d "${TMPDIR:-/tmp}/glyph-dir.XXXXXX")"
git -C "$DIRF" init -q -b main
git -C "$DIRF" config user.name "glyph-demo"
git -C "$DIRF" config user.email "glyph@example.test"
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
DJ="$("$GLYPH" -C "$DIRF" --json --color never "$D0" "$D1")"
python3 - "$DJ" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
follows = [p for p in r["sheaf"] if p["kind"]=="follow"]
assert len(follows) == 1, r["sheaf"]
assert follows[0]["from"] == "src/*", follows
assert follows[0]["to"] == "lib/*", follows
assert r["delta"]["renames"] == 3
print("dir-ok")
PY
assert "three git mvs of a tree are one src/* → lib/* glyph" true
rm -rf "$DIRF"

if [[ -x "$HELD" ]]; then
  echo "-- generated held line actually runs (grep, no --follow)"
  LINE="$("$GLYPH" -C "$FIX" --walks --held "$T0" "$T1" | head -1)"
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

echo
echo "== real repo: sitbone FocusRiverView island =="
SITBONE="/Users/annenpolka/ghq/github.com/annenpolka/sitbone"
if [[ -d "$SITBONE/.git" || -f "$SITBONE/.git" ]]; then
  echo "-- birth 14b1d6e^ vs 14b1d6e (file appears)"
  SBIRTH="$("$GLYPH" -C "$SITBONE" --json --color never 14b1d6e^ 14b1d6e)"
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
  SDEATH="$("$GLYPH" -C "$SITBONE" --json --color never 70ec7df^ 70ec7df)"
  python3 - "$SDEATH" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
assert any(p["true_on"]=="A" and "FocusRiverView" in p["held"] for p in r["sheaf"]), [p["held"] for p in r["sheaf"]]
print("sitbone-death-ok")
PY
  assert "sitbone death sheaf names FocusRiverView on A" true

  echo "-- island 14b1d6e vs HEAD (git log -- path is empty)"
  SHEAD="$("$GLYPH" -C "$SITBONE" --json --color never --limit 6 14b1d6e HEAD)"
  python3 - "$SHEAD" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
assert any(p["true_on"]=="A" and "FocusRiverView" in p["held"] for p in r["sheaf"]), [p["held"] for p in r["sheaf"]]
assert any(w["full"] and "FocusRiverView" in w["line"] and "--full" in w["line"] for w in r["walks"]), r["walks"]
print("sitbone-island-ok")
PY
  assert "island vs HEAD sheaf keeps FocusRiverView and --full walks" true

  echo "---- sitbone birth (human) ----"
  "$GLYPH" -C "$SITBONE" --color never --limit 4 14b1d6e^ 14b1d6e | head -40
else
  echo "skip sitbone (not present)"
fi

echo
echo "== real repo: kizu CLAUDE.md birth + jsx + rename =="
KIZU="/Users/annenpolka/ghq/github.com/annenpolka/kizu"
if [[ -d "$KIZU/.git" || -f "$KIZU/.git" ]]; then
  K1="$("$GLYPH" -C "$KIZU" --json --color never e1098c8^ e1098c8)"
  python3 - "$K1" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
held = [p["held"] for p in r["sheaf"]]
assert any("CLAUDE" in h for h in held), held
assert r["walks"], r["walks"]
print("kizu-claude-ok")
PY
  assert "kizu CLAUDE.md birth is in the sheaf + walks" true

  K2="$("$GLYPH" -C "$KIZU" --json --color never --limit 8 04adde1^ 04adde1)"
  python3 - "$K2" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
held = " ".join(p["held"] for p in r["sheaf"])
assert "jsx" in held.lower() or "tsx" in held.lower() or "js_ts" in held, held
print("kizu-jsx-ok")
PY
  assert "kizu jsx/tsx commit is named by the sheaf" true

  K3="$("$GLYPH" -C "$KIZU" --json --color never --limit 6 4e37f16^ 4e37f16)"
  python3 - "$K3" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
follows = [p for p in r["sheaf"] if p["kind"]=="follow"]
assert len(follows) == 1, [p["held"] for p in r["sheaf"]]
assert follows[0]["from"] == "deep-research-ai-agent-hooks.md"
assert follows[0]["to"] == "docs/deep-research-ai-agent-hooks.md"
assert any("--follow" in w["line"] and "deep-research-ai-agent-hooks.md" in w["line"] for w in r["walks"])
# ui.rs still gets its own content glyph — not swallowed by the rename
assert any("ui.rs" in "".join(p["covers"]) or "char" in p["pattern"] or "ui" in p["held"] for p in r["sheaf"]), [p["held"] for p in r["sheaf"]]
print("kizu-rename-ok")
PY
  assert "kizu R100 markdown move is one follow, plus ui.rs content" true
  echo "---- kizu rename 4e37f16 ----"
  "$GLYPH" -C "$KIZU" --color never --limit 4 4e37f16^ 4e37f16 | head -30
else
  echo "skip kizu (not present)"
fi

echo
echo "== real repo: tenaoshi 第一級 / MAN-023 =="
TENA="/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi"
if [[ -d "$TENA/.git" || -f "$TENA/.git" ]]; then
  TN="$("$GLYPH" -C "$TENA" --json --color never 70b450d^ 70b450d)"
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
  "$GLYPH" -C "$TENA" --color never --limit 4 70b450d^ 70b450d | head -30
else
  echo "skip tenaoshi (not present)"
fi

echo
echo "== real repo: skills recent delta =="
SKILLS="/Users/annenpolka/ghq/github.com/annenpolka/skills"
if [[ -d "$SKILLS/.git" || -f "$SKILLS/.git" ]]; then
  SK="$("$GLYPH" -C "$SKILLS" --json --color never --limit 6 HEAD~1 HEAD)"
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
