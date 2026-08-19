#!/usr/bin/env bash
# End-to-end: selftest, reconstruction vs sate-all-plus, occupancy sandwich,
# stream collide, real GitHub suggestion comments against snapshot trees.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PLEA="$ROOT/plea"
chmod +x "$PLEA"

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

unanimous_of() {
  python3 -c 'import json,sys; print(json.load(sys.stdin)["unanimous"])'
}

fates_of() {
  python3 -c 'import json,sys; print(" ".join(c["fate"] for c in json.load(sys.stdin)["claims"]))'
}

echo "======== 1. selftest ========"
if "$PLEA" --selftest; then
  ok "selftest"
else
  bad "selftest" "exit $?"
fi

DEMO="$(mktemp -d "${TMPDIR:-/tmp}/plea-demo.XXXXXX")"
cleanup() { rm -rf "$DEMO"; }
trap cleanup EXIT

git_init() {
  local d="$1"
  mkdir -p "$d"
  git -C "$d" init -q -b main
  git -C "$d" config user.name plea-demo
  git -C "$d" config user.email plea@demo
  git -C "$d" config commit.gpgsign false
}

echo "======== 2. occupancy sandwich (suggestion vs HEAD / parent, not a git range) ========"
git_init "$DEMO/sand"
printf 'x = 1\n' > "$DEMO/sand/app.py"
git -C "$DEMO/sand" add app.py
git -C "$DEMO/sand" commit -q -m t0
T0="$(git -C "$DEMO/sand" rev-parse HEAD)"
printf 'x = 2\n' > "$DEMO/sand/app.py"
git -C "$DEMO/sand" add app.py
git -C "$DEMO/sand" commit -q -m t1
# review stream: the plea that turned 1 into 2, made at t0
cat > "$DEMO/sand-comments.jsonl" << EOF
{"path":"app.py","before":["x = 1"],"after":["x = 2"],"id":"bump","original_commit_id":"$T0"}
EOF
got="$("$PLEA" --json --report-only -C "$DEMO/sand" "$DEMO/sand-comments.jsonl" | unanimous_of)"
assert_eq "default against HEAD is APPLIED" "$got" "APPLIED"
got="$("$PLEA" --json --report-only -C "$DEMO/sand" --against HEAD^ "$DEMO/sand-comments.jsonl" | unanimous_of)"
assert_eq "against parent is PENDING" "$got" "PENDING"
printf 'x = 1\n' > "$DEMO/sand/app.py"
got="$("$PLEA" --json --report-only -C "$DEMO/sand" "$DEMO/sand-comments.jsonl" | unanimous_of)"
assert_eq "dirty worktree is ignored (still HEAD/APPLIED)" "$got" "APPLIED"
got="$("$PLEA" --json --report-only -C "$DEMO/sand" --worktree "$DEMO/sand-comments.jsonl" | unanimous_of)"
assert_eq "--worktree sees the revert as PENDING" "$got" "PENDING"
got="$("$PLEA" --json --report-only --sandwich -C "$DEMO/sand" "$DEMO/sand-comments.jsonl" | python3 -c 'import json,sys; print(json.load(sys.stdin)["claims"][0]["sandwich"])')"
assert_eq "sandwich then=PENDING at original_commit" "$got" "PENDING"

echo "======== 3. four occupancy fates on a review stream ========"
mkdir -p "$DEMO/four/src"
cat > "$DEMO/four/src/add.py" << 'PY'
def add(a, b):
    return a + b
PY
cat > "$DEMO/four/src/mix.py" << 'PY'
def f():
    a = 10
    b = 2
    return a + b
PY
cat > "$DEMO/four/src/dup.py" << 'PY'
def add(a, b):
    return a - b

def add(a, b):
    return a + b
PY
cat > "$DEMO/four/src/gone.py" << 'PY'
def add(a, b):
    return a * b
PY
cat > "$DEMO/four.jsonl" << 'EOF'
{"path":"src/add.py","before":["    return a - b"],"after":["    return a + b"],"id":"taken"}
{"path":"src/mix.py","before":["    a = 1","    b = 2"],"after":["    a = 10","    b = 20"],"id":"partial"}
{"path":"src/dup.py","before":["    return a - b"],"after":["    return a + b"],"id":"copied"}
{"path":"src/gone.py","before":["    return a - b"],"after":["    return a + b"],"id":"moved-on"}
EOF
got="$("$PLEA" --json --report-only --worktree -C "$DEMO/four" "$DEMO/four.jsonl" | fates_of)"
assert_eq "four fates TAKEN MIXED DUPLEX STALE" "$got" "APPLIED MIXED DUPLEX SUPERSEDED"
code=0
set +e
"$PLEA" --quiet --worktree -C "$DEMO/four" "$DEMO/four.jsonl" >/dev/null
code=$?
set -e
assert_eq "SPLIT exit 2" "$code" "2"

echo "======== 4. stdin JSONL + suggest TAKEN/OPEN/gone ========"
mkdir -p "$DEMO/rev"
printf 'TIMEOUT = 60\nretries = 3\n' > "$DEMO/rev/mod.py"
got="$(cat "$ROOT/fixtures/suggest.jsonl" | "$PLEA" --json --report-only --worktree -C "$DEMO/rev" - | fates_of)"
assert_eq "suggest JSONL TAKEN/OPEN/gone" "$got" "APPLIED PENDING SUPERSEDED"
code=0
set +e
cat "$ROOT/fixtures/suggest.jsonl" | "$PLEA" --quiet --worktree -C "$DEMO/rev" - >/dev/null
code=$?
set -e
assert_eq "SPLIT stream exit 2" "$code" "2"

echo "======== 5. markdown suggestion stream ========"
mkdir -p "$DEMO/md/src"
cat > "$DEMO/md/src/add.py" << 'PY'
def add(a, b):
    return a + b
PY
printf 'TIMEOUT = 30\n' > "$DEMO/md/src/timeout.py"
got="$("$PLEA" --json --report-only --worktree -C "$DEMO/md" "$ROOT/fixtures/stream.md" | fates_of)"
assert_eq "markdown TAKEN + OPEN" "$got" "APPLIED PENDING"

echo "======== 6. two reviewers collide, third echoes ========"
mkdir -p "$DEMO/col/src"
cat > "$DEMO/col/src/add.py" << 'PY'
def add(a, b):
    return a - b
PY
"$PLEA" --json --report-only --worktree -C "$DEMO/col" "$ROOT/fixtures/collide.jsonl" > "$DEMO/col.json"
python3 - "$DEMO/col.json" << 'PY'
import json,sys
r=json.load(open(sys.argv[1]))
by={c["claim"]:c for c in r["claims"]}
assert r["unanimous"]=="PENDING", r
assert "bob" in by["alice"]["collide"], by["alice"]
assert "cara" in by["alice"]["echo"], by["alice"]
assert "alice" in by["bob"]["collide"]
print("collide", {k: (v["collide"], v["echo"]) for k,v in by.items()})
PY
ok "stream collide + echo"

echo "======== 7. GitHub range reconstruction + locus (not all + lines) ========"
"$PLEA" --json --report-only --worktree -C "$ROOT/fixtures/trees/cli-orig" "$ROOT/fixtures/cli-pr7.json" > "$DEMO/cli.json"
python3 - "$DEMO/cli.json" << 'PY'
import json,sys
r=json.load(open(sys.argv[1]))
by={str(c["claim"]):c for c in r["claims"]}
c=by["333030758"]
assert c["recon"]=="range", c
# v1 was DUPLEX: after-image `return nil, err` already exists 7 lines later.
# v2 locus: the commented line still holds the before-image → OPEN.
assert c["fate"]=="PENDING", c
assert c["method"]=="exact-before-locus", c
print("cli#333030758", c["fate"], c["recon"], c["method"], c["note"])
c2=by["333031216"]
assert c2["fate"]=="PENDING", c2
print("cli#333031216", c2["fate"], c2["method"], c2["note"])
PY
ok "cli/cli #333030758 range-OPEN at locus (not DUPLEX)"

echo "======== 8. real GitHub suggestions vs orig / head snapshots ========"
got="$("$PLEA" --json --report-only --worktree -C "$ROOT/fixtures/trees/iotest-orig" "$ROOT/fixtures/go-iotest.json" | unanimous_of)"
assert_eq "iotest orig is OPEN" "$got" "PENDING"
got="$("$PLEA" --json --report-only --worktree -C "$ROOT/fixtures/trees/iotest-head" "$ROOT/fixtures/go-iotest.json" | unanimous_of)"
assert_eq "iotest HEAD is TAKEN (period added)" "$got" "APPLIED"

got="$("$PLEA" --json --report-only --worktree -C "$ROOT/fixtures/trees/unixsock-orig" "$ROOT/fixtures/go-unixsock.json" | unanimous_of)"
assert_eq "unixsock orig is OPEN" "$got" "PENDING"
got="$("$PLEA" --json --report-only --worktree -C "$ROOT/fixtures/trees/unixsock-head" "$ROOT/fixtures/go-unixsock.json" | unanimous_of)"
assert_eq "unixsock HEAD is STALE (build tag rewritten again)" "$got" "SUPERSEDED"

got="$("$PLEA" --json --report-only --worktree -C "$ROOT/fixtures/trees/zip-orig" "$ROOT/fixtures/go-zip.json" | unanimous_of)"
assert_eq "zip orig (blank+call) is OPEN" "$got" "PENDING"
got="$("$PLEA" --json --report-only --worktree -C "$ROOT/fixtures/trees/zip-head" "$ROOT/fixtures/go-zip.json" | unanimous_of)"
assert_eq "zip HEAD is STALE (call gone)" "$got" "SUPERSEDED"

echo "======== 9. empty suggestion deletes the stray line ========"
mkdir -p "$DEMO/empty/doc"
printf '<p>\nw\n</p>\n' > "$DEMO/empty/doc/code.html"
got="$("$PLEA" --json --report-only --worktree -C "$DEMO/empty" "$ROOT/fixtures/go-empty.json" | unanimous_of)"
assert_eq "empty-suggestion still-there is OPEN" "$got" "PENDING"
printf '<p>\n</p>\n' > "$DEMO/empty/doc/code.html"
got="$("$PLEA" --json --report-only --worktree -C "$DEMO/empty" "$ROOT/fixtures/go-empty.json" | unanimous_of)"
assert_eq "empty-suggestion gone is TAKEN" "$got" "APPLIED"

echo "======== 10. --pick OPEN / TAKEN aliases + tsv ========"
got="$("$PLEA" --tsv --report-only --pick OPEN --worktree -C "$DEMO/rev" "$ROOT/fixtures/suggest.jsonl" | awk -F'\t' 'NR>1{print $1,$2,$4}')"
assert_eq "pick OPEN is retries" "$got" "PENDING OPEN r2"

echo "======== 11. live dogfood if golang/go is checked out ========"
dogfood_go() {
  local repo="$1"
  if [[ ! -d "$repo/.git" && ! -f "$repo/.git" ]]; then
    echo "  skip  golang/go (missing $repo)"
    return
  fi
  local j u
  j="$("$PLEA" --json --report-only -C "$repo" "$ROOT/fixtures/go-iotest.json")"
  u="$(printf '%s' "$j" | unanimous_of)"
  echo "        golang/go iotest against HEAD unanimous=$u"
  if [[ "$u" == "APPLIED" ]]; then
    ok "live golang/go iotest TAKEN at HEAD"
  else
    bad "live golang/go iotest" "unanimous=$u (want APPLIED; period on ErrTimeout)"
  fi
  j="$("$PLEA" --json --report-only -C "$repo" "$ROOT/fixtures/go-unixsock.json")"
  u="$(printf '%s' "$j" | unanimous_of)"
  echo "        golang/go unixsock against HEAD unanimous=$u"
  if [[ "$u" == "SUPERSEDED" || "$u" == "APPLIED" ]]; then
    ok "live golang/go unixsock $u at HEAD"
  else
    bad "live golang/go unixsock" "unanimous=$u"
  fi
}
dogfood_go /Users/annenpolka/ghq/github.com/golang/go

echo
echo "======== summary: $PASS passed, $FAIL failed ========"
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
exit 0
