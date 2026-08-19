#!/usr/bin/env bash
# Exercise yoke against a planted fixture and the three Pkl dogfood repos.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
YOKE="$ROOT/yoke"
chmod +x "$YOKE"

PASS=0
FAIL=0

assert_exit() {
  local got="$1" want="$2" name="$3"
  if [[ "$got" == "$want" ]]; then
    echo "  ok  $name (exit $got)"
    PASS=$((PASS + 1))
  else
    echo "  FAIL $name (exit $got, want $want)" >&2
    FAIL=$((FAIL + 1))
  fi
}

assert_contains() {
  local hay="$1" needle="$2" name="$3"
  if grep -Fq -- "$needle" <<<"$hay"; then
    echo "  ok  $name"
    PASS=$((PASS + 1))
  else
    echo "  FAIL $name" >&2
    echo "    missing: $needle" >&2
    echo "$hay" | sed 's/^/    /' >&2
    FAIL=$((FAIL + 1))
  fi
}

assert_count() {
  local json="$1" key="$2" want="$3" name="$4"
  local got
  got="$(python3 -c "import json,sys; print(json.loads(sys.argv[1]).get('counts',{}).get(sys.argv[2],0))" "$json" "$key")"
  if [[ "$got" == "$want" ]]; then
    echo "  ok  $name ($key=$got)"
    PASS=$((PASS + 1))
  else
    echo "  FAIL $name ($key=$got, want $want)" >&2
    FAIL=$((FAIL + 1))
  fi
}

echo "== self-test =="
set +e
"$YOKE" self-test
st=$?
set -e
assert_exit "$st" 0 "embedded parser tests"

echo
echo "== planted fixture =="
FIX="$(mktemp -d "${TMPDIR:-/tmp}/yoke-demo.XXXXXX")"
cleanup() { rm -rf "$FIX"; }
trap cleanup EXIT

mkdir -p "$FIX/specs" "$FIX/docs" "$FIX/contracts/testcases"
cp "$ROOT/fixtures/app.pkl" "$FIX/specs/app.pkl"
cat > "$FIX/docs/SPEC.md" <<'MD'
<!-- Generated from specs/app.pkl. Do not edit. -->
# fixture spec

| ID | パターン | 保証 | 内容 |
|:---|:---|:---|:---|
| FOO-001 | `example` | example-tested | alpha keeps the door open |
| FOO-002 | `example` | example-tested | stale generated beta |
| BAR-001 | `example` | example-tested | gamma never leaves |
| BAZ-001 | `example` | example-tested | leftover generated orphan |
MD
cat > "$FIX/contracts/testcases/FOO-001.json" <<'JSON'
{"id":"FOO-001","description":"alpha keeps the door open","intent":"open","input":"ping"}
JSON
# FOO-002 shard missing (prefix FOO exists) + body drift in SPEC.md
# leftover shard with no spec parent
cat > "$FIX/contracts/testcases/BAZ-001.json" <<'JSON'
{"id":"BAZ-001","description":"leftover generated orphan"}
JSON
# one witness that still matches spec, one that drifted → split
cat > "$FIX/oracles.generated.rs" <<'RS'
// @generated from specs/app.pkl — DO NOT EDIT
/// FOO-001: alpha keeps the door open
fn foo_001() {}
/// FOO-001: completely different rust title
fn foo_001_other() {}
RS

git -C "$FIX" init -q -b main
git -C "$FIX" config user.name "yoke-demo"
git -C "$FIX" config user.email "yoke@example.test"
git -C "$FIX" add specs docs contracts oracles.generated.rs
git -C "$FIX" commit -q -m "planted slack/hand/split"

set +e
OUT="$("$YOKE" -C "$FIX" --all)"
st=$?
JSON="$("$YOKE" -C "$FIX" --json --all)"
set -e
assert_exit "$st" 1 "fixture is not all-taut"
assert_contains "$OUT" "slack  FOO-002" "FOO-002 body is slack"
assert_contains "$OUT" "hand   BAZ-001" "BAZ-001 generated orphan"
assert_contains "$OUT" "split  FOO-001" "FOO-001 rust witness split"
assert_contains "$OUT" "taut   BAR-001" "BAR-001 still taut"
assert_count "$JSON" "slack" 1 "one slack"
assert_count "$JSON" "hand" 1 "one hand"
assert_count "$JSON" "split" 1 "one split"
assert_count "$JSON" "taut" 1 "one taut"

echo
echo "== dogfood: tenaoshi / voidtrace / relico =="
TENAOSHI="${TENAOSHI:-/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi}"
VOIDTRACE="${VOIDTRACE:-/Users/annenpolka/ghq/github.com/annenpolka/voidtrace}"
RELICO="${RELICO:-/Users/annenpolka/ghq/github.com/annenpolka/relico}"

if [[ -d "$TENAOSHI/specs" ]]; then
  set +e
  TW="$("$YOKE" -C "$TENAOSHI" --json --all)"
  stw=$?
  TX="$("$YOKE" -C "$TENAOSHI" --spec HEAD --gen : --json --all)"
  stx=$?
  PUNCH="$("$YOKE" -C "$TENAOSHI" --punch HEAD)"
  set -e
  # dirty tree regenerated together → taut
  python3 - <<'PY' "$TW"
import json,sys
d=json.loads(sys.argv[1])
c=d["counts"]
assert c.get("taut",0) >= 70, c
assert c.get("slack",0)==0 and c.get("hand",0)==0, c
print("  ok  tenaoshi worktree taut", c)
PY
  PASS=$((PASS + 1))
  python3 - <<'PY' "$TX"
import json,sys
d=json.loads(sys.argv[1])
c=d["counts"]
assert c.get("slack",0) >= 20, c
assert c.get("hand",0) >= 20, c
ids={row["id"] for row in d["clauses"]}
assert "CTR-001" in ids and "EPF-001" in ids, sorted(ids)[:8]
print("  ok  tenaoshi HEAD spec vs worktree gen", c)
PY
  PASS=$((PASS + 1))
  assert_contains "$PUNCH" "removed   CTR-001" "punch sees CTR removal"
  assert_contains "$PUNCH" "added     EPF-001" "punch sees EPF birth"
  assert_contains "$PUNCH" "contracts/testcases/CTR-001.json" "removed id still names its old generated shard"
  assert_exit "$stw" 0 "tenaoshi worktree exit"
else
  echo "  skip tenaoshi (not at $TENAOSHI)"
fi

if [[ -d "$VOIDTRACE/specs" ]]; then
  set +e
  VH="$("$YOKE" -C "$VOIDTRACE" HEAD --json --all)"
  st=$?
  VW="$("$YOKE" -C "$VOIDTRACE" --json --all)"
  set -e
  python3 - <<'PY' "$VH"
import json,sys
d=json.loads(sys.argv[1])
c=d["counts"]
assert c.get("taut",0) >= 60 and c.get("hand",0)==0 and c.get("slack",0)==0, c
print("  ok  voidtrace HEAD taut", c)
PY
  PASS=$((PASS + 1))
  assert_exit "$st" 0 "voidtrace HEAD exit"
  python3 - <<'PY' "$VW"
import json,sys
d=json.loads(sys.argv[1])
c=d["counts"]
# worktree is mid-merge: generated dumps are riven
assert c.get("riven",0) >= 1 or c.get("taut",0) >= 60, c
print("  ok  voidtrace worktree", c)
print("       riven files", len(d.get("riven_files",[])))
PY
  PASS=$((PASS + 1))
else
  echo "  skip voidtrace (not at $VOIDTRACE)"
fi

if [[ -d "$RELICO/specs" ]]; then
  set +e
  RH="$("$YOKE" -C "$RELICO" HEAD --json --all)"
  st=$?
  set -e
  python3 - <<'PY' "$RH"
import json,sys
d=json.loads(sys.argv[1])
c=d["counts"]
assert c.get("taut",0) >= 110 and sum(v for k,v in c.items() if k!="taut")==0, c
print("  ok  relico HEAD taut", c)
PY
  PASS=$((PASS + 1))
  assert_exit "$st" 0 "relico HEAD exit"
else
  echo "  skip relico (not at $RELICO)"
fi

echo
if [[ "$FAIL" -gt 0 ]]; then
  echo "demo FAIL  $PASS passed  $FAIL failed" >&2
  exit 1
fi
echo "demo ok  $PASS passed"
exit 0
