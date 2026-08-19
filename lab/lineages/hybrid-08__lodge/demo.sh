#!/usr/bin/env bash
# End-to-end: selftest, fused sandwich, collide, one vocabulary, real trees.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
LODGE="$ROOT/lodge"
chmod +x "$LODGE"

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

via_of() {
  python3 -c 'import json,sys; print(" ".join(sorted(json.load(sys.stdin)["via"].items())))'
}

n_of() {
  python3 -c 'import json,sys; print(len(json.load(sys.stdin)["claims"]))'
}

echo "======== 1. selftest ========"
if "$LODGE" --selftest; then
  ok "selftest"
else
  bad "selftest" "exit $?"
fi

DEMO="$(mktemp -d "${TMPDIR:-/tmp}/lodge-demo.XXXXXX")"
cleanup() { rm -rf "$DEMO"; }
trap cleanup EXIT

git_init() {
  local d="$1"
  mkdir -p "$d"
  git -C "$d" init -q -b main
  git -C "$d" config user.name lodge-demo
  git -C "$d" config user.email lodge@demo
  git -C "$d" config commit.gpgsign false
}

echo "======== 2. fused occupancy sandwich (the joint, not two CLIs) ========"
git_init "$DEMO/sand"
printf 'x = 1\n' > "$DEMO/sand/app.py"
git -C "$DEMO/sand" add app.py
git -C "$DEMO/sand" commit -q -m t0
T0="$(git -C "$DEMO/sand" rev-parse HEAD)"
printf 'x = 2\n' > "$DEMO/sand/app.py"
git -C "$DEMO/sand" add app.py
git -C "$DEMO/sand" commit -q -m t1
cat > "$DEMO/sand-comments.jsonl" << EOF
{"path":"app.py","before":["x = 1"],"after":["x = 2"],"id":"bump","original_commit_id":"$T0","line":1}
EOF

# concatenation would be two rows (sate hunk APPLIED + plea APPLIED).
# lodge fuses equal cores into one occupancy via=both.
"$LODGE" --json --report-only -C "$DEMO/sand" --git HEAD "$DEMO/sand-comments.jsonl" > "$DEMO/fused.json"
python3 - "$DEMO/fused.json" << 'PY'
import json,sys
r=json.load(open(sys.argv[1]))
assert r["n"]==1, r
assert r["via"]=={"both":1}, r["via"]
assert r["unanimous"]=="APPLIED", r
assert "alias" not in r["claims"][0], r["claims"][0]
assert r["claims"][0]["via"]=="both"
assert len(r["claims"][0]["witnesses"])==2
print("fused", r["claims"][0]["fate"], r["claims"][0]["via"], r["claims"][0]["witnesses"])
PY
ok "HEAD mixed is 1 claim via=both APPLIED (not 2 reports)"

got="$("$LODGE" --json --report-only -C "$DEMO/sand" --against HEAD^ --git HEAD "$DEMO/sand-comments.jsonl" | unanimous_of)"
assert_eq "fused against parent is PENDING" "$got" "PENDING"

printf 'x = 1\n' > "$DEMO/sand/app.py"
got="$("$LODGE" --json --report-only -C "$DEMO/sand" --git HEAD "$DEMO/sand-comments.jsonl" | unanimous_of)"
assert_eq "dirty worktree ignored (still HEAD/APPLIED)" "$got" "APPLIED"
got="$("$LODGE" --json --report-only -C "$DEMO/sand" --worktree --git HEAD "$DEMO/sand-comments.jsonl" | unanimous_of)"
assert_eq "--worktree sees the revert as PENDING" "$got" "PENDING"

# --no-fuse is the concatenation the joint refuses: two rows, no via=both
got="$("$LODGE" --json --report-only --no-fuse -C "$DEMO/sand" --git HEAD "$DEMO/sand-comments.jsonl" | n_of)"
assert_eq "--no-fuse concatenation is 2 rows" "$got" "2"

echo "======== 3. collide: different cores stay two occupancies ========"
git_init "$DEMO/col"
mkdir -p "$DEMO/col/src"
cat > "$DEMO/col/src/add.py" << 'PY'
def add(a, b):
    return a - b
PY
git -C "$DEMO/col" add -A
git -C "$DEMO/col" commit -q -m t0
cat > "$DEMO/col/src/add.py" << 'PY'
def add(a, b):
    return a + b
PY
git -C "$DEMO/col" add -A
git -C "$DEMO/col" commit -q -m 'take plus'
cat > "$DEMO/col-bob.jsonl" << 'EOF'
{"path":"src/add.py","before":["    return a - b"],"after":["    return a * b"],"id":"bob","line":2}
EOF
"$LODGE" --json --report-only -C "$DEMO/col" --git HEAD "$DEMO/col-bob.jsonl" > "$DEMO/col.json"
python3 - "$DEMO/col.json" << 'PY'
import json,sys
r=json.load(open(sys.argv[1]))
assert r["n"]==2, r
assert "both" not in r["via"], r["via"]
assert r["via"].get("hunk")==1 and r["via"].get("plea")==1, r["via"]
by={c["claim"]:c for c in r["claims"]}
h=[c for c in r["claims"] if c["via"]=="hunk"][0]
assert h["fate"]=="APPLIED", h
assert by["bob"]["fate"] in ("SUPERSEDED","PENDING"), by["bob"]
assert by["bob"]["claim"] in h["collide"] or h["claim"] in by["bob"]["collide"]
print("collide", r["via"], h["fate"], by["bob"]["fate"])
PY
ok "different after-images collide, do not fuse"

echo "======== 4. four fates, one vocabulary, no TAKEN/OPEN ========"
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
"$LODGE" --json --report-only --worktree -C "$DEMO/four" "$DEMO/four.jsonl" > "$DEMO/four.out.json"
python3 - "$DEMO/four.out.json" << 'PY'
import json,sys
r=json.load(open(sys.argv[1]))
fates=[c["fate"] for c in r["claims"]]
assert fates==["APPLIED","MIXED","DUPLEX","SUPERSEDED"], fates
for c in r["claims"]:
    assert "alias" not in c
    assert c["via"]=="plea"
print("fates", fates)
PY
ok "four fates APPLIED MIXED DUPLEX SUPERSEDED (no aliases)"
code=0
set +e
"$LODGE" --quiet --worktree -C "$DEMO/four" "$DEMO/four.jsonl" >/dev/null
code=$?
set -e
assert_eq "SPLIT exit 2" "$code" "2"

echo "======== 5. sniffed stdin patch vs stream ========"
mkdir -p "$DEMO/rev"
printf 'TIMEOUT = 60\nretries = 3\n' > "$DEMO/rev/mod.py"
got="$(cat "$ROOT/fixtures/suggest.jsonl" | "$LODGE" --json --report-only --worktree -C "$DEMO/rev" - | python3 -c 'import json,sys; print(" ".join(c["fate"] for c in json.load(sys.stdin)["claims"]))')"
assert_eq "suggest JSONL APPLIED PENDING SUPERSEDED" "$got" "APPLIED PENDING SUPERSEDED"

git_init "$DEMO/sniff"
printf 'x = 1\n' > "$DEMO/sniff/app.py"
git -C "$DEMO/sniff" add app.py
git -C "$DEMO/sniff" commit -q -m t0
printf 'x = 2\n' > "$DEMO/sniff/app.py"
git -C "$DEMO/sniff" add app.py
git -C "$DEMO/sniff" commit -q -m t1
got="$(git -C "$DEMO/sniff" show --format= --patch HEAD | "$LODGE" --json --report-only -C "$DEMO/sniff" --against HEAD - | unanimous_of)"
assert_eq "sniffed stdin patch sandwich HEAD" "$got" "APPLIED"

echo "======== 6. markdown stream ========"
mkdir -p "$DEMO/md/src"
cat > "$DEMO/md/src/add.py" << 'PY'
def add(a, b):
    return a + b
PY
printf 'TIMEOUT = 30\n' > "$DEMO/md/src/timeout.py"
got="$("$LODGE" --json --report-only --worktree -C "$DEMO/md" "$ROOT/fixtures/stream.md" | python3 -c 'import json,sys; print(" ".join(c["fate"] for c in json.load(sys.stdin)["claims"]))')"
assert_eq "markdown APPLIED + PENDING" "$got" "APPLIED PENDING"

echo "======== 7. cli/cli range reconstruction + locus (not all-plus, not DUPLEX) ========"
"$LODGE" --json --report-only --worktree -C "$ROOT/fixtures/trees/cli-orig" "$ROOT/fixtures/cli-pr7.json" > "$DEMO/cli.json"
python3 - "$DEMO/cli.json" << 'PY'
import json,sys
r=json.load(open(sys.argv[1]))
by={str(c["claim"]):c for c in r["claims"]}
c=by["333030758"]
assert c["recon"]=="range", c
assert c["fate"]=="PENDING", c
assert c["method"]=="exact-before-locus", c
assert "alias" not in c
print("cli#333030758", c["fate"], c["recon"], c["method"])
c2=by["333031216"]
assert c2["fate"]=="PENDING", c2
print("cli#333031216", c2["fate"], c2["method"])
PY
ok "cli/cli #333030758 range-PENDING at locus (not DUPLEX)"

echo "======== 8. real GitHub suggestions vs orig / head snapshots ========"
got="$("$LODGE" --json --report-only --worktree -C "$ROOT/fixtures/trees/iotest-orig" "$ROOT/fixtures/go-iotest.json" | unanimous_of)"
assert_eq "iotest orig is PENDING" "$got" "PENDING"
got="$("$LODGE" --json --report-only --worktree -C "$ROOT/fixtures/trees/iotest-head" "$ROOT/fixtures/go-iotest.json" | unanimous_of)"
assert_eq "iotest HEAD is APPLIED (period added)" "$got" "APPLIED"

got="$("$LODGE" --json --report-only --worktree -C "$ROOT/fixtures/trees/unixsock-orig" "$ROOT/fixtures/go-unixsock.json" | unanimous_of)"
assert_eq "unixsock orig is PENDING" "$got" "PENDING"
got="$("$LODGE" --json --report-only --worktree -C "$ROOT/fixtures/trees/unixsock-head" "$ROOT/fixtures/go-unixsock.json" | unanimous_of)"
assert_eq "unixsock HEAD is SUPERSEDED (build tag rewritten again)" "$got" "SUPERSEDED"

got="$("$LODGE" --json --report-only --worktree -C "$ROOT/fixtures/trees/zip-orig" "$ROOT/fixtures/go-zip.json" | unanimous_of)"
assert_eq "zip orig is PENDING" "$got" "PENDING"
got="$("$LODGE" --json --report-only --worktree -C "$ROOT/fixtures/trees/zip-head" "$ROOT/fixtures/go-zip.json" | unanimous_of)"
assert_eq "zip HEAD is SUPERSEDED" "$got" "SUPERSEDED"

echo "======== 9. empty suggestion deletes the stray line ========"
mkdir -p "$DEMO/empty/doc"
printf '<p>\nw\n</p>\n' > "$DEMO/empty/doc/code.html"
got="$("$LODGE" --json --report-only --worktree -C "$DEMO/empty" "$ROOT/fixtures/go-empty.json" | unanimous_of)"
assert_eq "empty-suggestion still-there is PENDING" "$got" "PENDING"
printf '<p>\n</p>\n' > "$DEMO/empty/doc/code.html"
got="$("$LODGE" --json --report-only --worktree -C "$DEMO/empty" "$ROOT/fixtures/go-empty.json" | unanimous_of)"
assert_eq "empty-suggestion gone is APPLIED" "$got" "APPLIED"

echo "======== 10. mixed git range + stream on positional patch file ========"
git_init "$DEMO/pos"
printf 'TIMEOUT = 30\nretries = 3\n' > "$DEMO/pos/mod.py"
git -C "$DEMO/pos" add mod.py
git -C "$DEMO/pos" commit -q -m t0
printf 'TIMEOUT = 60\nretries = 3\n' > "$DEMO/pos/mod.py"
git -C "$DEMO/pos" add mod.py
git -C "$DEMO/pos" commit -q -m t1
git -C "$DEMO/pos" show --format= --patch HEAD > "$DEMO/pos.patch"
"$LODGE" --json --report-only --worktree -C "$DEMO/pos" "$DEMO/pos.patch" "$ROOT/fixtures/suggest.jsonl" > "$DEMO/pos.json"
python3 - "$DEMO/pos.json" << 'PY'
import json,sys
r=json.load(open(sys.argv[1]))
vias=r["via"]
# TIMEOUT 30→60 fuses with r1; retries plea stays PENDING; gone.py SUPERSEDED
assert vias.get("both")==1, r
assert r["unanimous"]=="SPLIT", r
fates=sorted((c["via"], c["fate"], c["path"]) for c in r["claims"])
print("positional mixed", fates, "via", vias)
PY
ok "positional patch+jsonl fuses TIMEOUT, leaves retries/gone"

echo "======== 11. --pick / --via + tsv ========"
got="$("$LODGE" --tsv --report-only --pick PENDING --worktree -C "$DEMO/rev" "$ROOT/fixtures/suggest.jsonl" | awk -F'\t' 'NR>1{print $1,$2,$4}')"
assert_eq "pick PENDING is r2" "$got" "PENDING plea r2"
got="$("$LODGE" --json --report-only --via both -C "$DEMO/sand" --git HEAD "$DEMO/sand-comments.jsonl" --against HEAD | n_of)"
assert_eq "via both n=1" "$got" "1"

echo "======== 12. v2: range rewrite (comment on old path, range moved it) ========"
git_init "$DEMO/mv"
mkdir -p "$DEMO/mv/command"
printf 'return err\n' > "$DEMO/mv/command/pr.go"
git -C "$DEMO/mv" add -A
git -C "$DEMO/mv" commit -q -m t0
mkdir -p "$DEMO/mv/pkg/cmd/pr"
printf 'return nil\n' > "$DEMO/mv/pkg/cmd/pr/pr.go"
git -C "$DEMO/mv" add -A
git -C "$DEMO/mv" rm -q command/pr.go
git -C "$DEMO/mv" commit -q -m 'move and take suggestion'
cat > "$DEMO/mv.jsonl" << 'EOF'
{"path":"command/pr.go","before":["return err"],"after":["return nil"],"id":"mislav","line":1}
EOF
"$LODGE" --json --report-only -C "$DEMO/mv" --git HEAD "$DEMO/mv.jsonl" > "$DEMO/mv.out.json"
python3 - "$DEMO/mv.out.json" << 'PY'
import json,sys
r=json.load(open(sys.argv[1]))
both=[c for c in r["claims"] if c["via"]=="both"]
assert both, r
assert both[0]["fate"]=="APPLIED", both[0]
assert both[0]["path"]=="pkg/cmd/pr/pr.go", both[0]
assert both[0]["moved_from"]=="command/pr.go", both[0]
assert not any(c["via"]=="plea" and c["fate"]=="SUPERSEDED" for c in r["claims"]), r
assert r["unanimous"]=="APPLIED", r
print("moved", both[0]["path"], "from", both[0]["moved_from"], "via", r["via"])
PY
ok "rename+take fuses via=both at new path (not SUPERSEDED missing-file)"

echo "======== 13. v2: GitHub iotest comment is a subset of the file range ========"
python3 - "$ROOT" "$DEMO" << 'PY'
import difflib, pathlib, sys
root = pathlib.Path(sys.argv[1]) / "fixtures/trees"
a = (root/"iotest-orig/src/testing/iotest/reader.go").read_text().splitlines(True)
b = (root/"iotest-head/src/testing/iotest/reader.go").read_text().splitlines(True)
path = "src/testing/iotest/reader.go"
patch = "".join(difflib.unified_diff(a, b, fromfile="a/"+path, tofile="b/"+path, n=3))
(pathlib.Path(sys.argv[2])/"iotest.patch").write_text(patch)
PY
"$LODGE" --json --report-only --worktree -C "$ROOT/fixtures/trees/iotest-head" \
  "$DEMO/iotest.patch" "$ROOT/fixtures/go-iotest.json" > "$DEMO/iotest.mixed.json"
python3 - "$DEMO/iotest.mixed.json" << 'PY'
import json,sys
r=json.load(open(sys.argv[1]))
by={str(c["claim"]):c for c in r["claims"]}
c=by["466704840"]
assert c["via"]=="both", c
assert c["fate"]=="APPLIED", c
h=by["hunk:src/testing/iotest/reader.go#2"]
assert "466704840" not in h["collide"], h
assert "466704840" in h["echo"] or h["claim"] in c["echo"] or "466704840" in h["covers"]
assert r["unanimous"]=="APPLIED", r
print("iotest mixed via", r["via"], "comment", c["via"], c["fate"], "covers", c["covers"])
PY
ok "iotest period-suggestion via=both subset of hunk (echo, not collide)"

echo "======== 14. live dogfood ========"
dogfood_git() {
  local name="$1" repo="$2"
  if [[ ! -d "$repo/.git" && ! -f "$repo/.git" ]]; then
    echo "  skip  $name (missing $repo)"
    return
  fi
  local head parent j u
  head="$(git -C "$repo" rev-list --no-merges -n 1 HEAD 2>/dev/null || true)"
  if [[ -z "$head" ]]; then
    echo "  skip  $name (no commit)"
    return
  fi
  parent="$(git -C "$repo" rev-parse "$head^" 2>/dev/null || true)"
  j="$("$LODGE" --json --report-only -C "$repo" --against "$head" --git "$head")"
  u="$(printf '%s' "$j" | unanimous_of)"
  if [[ "$u" == "APPLIED" || "$u" == "EMPTY" ]]; then
    ok "$name sandwich HEAD ($u)"
  else
    echo "        $name HEAD unanimous=$u via=$(printf '%s' "$j" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("via"))')"
    if [[ "$u" == "SPLIT" ]]; then
      ok "$name sandwich HEAD (SPLIT — some hunks already at HEAD otherwise)"
    else
      bad "$name sandwich HEAD" "unanimous=$u"
    fi
  fi
  if [[ -n "$parent" ]]; then
    j="$("$LODGE" --json --report-only -C "$repo" --against "$parent" --git "$head")"
    u="$(printf '%s' "$j" | unanimous_of)"
    if [[ "$u" == "PENDING" || "$u" == "EMPTY" || "$u" == "SPLIT" ]]; then
      ok "$name sandwich parent ($u)"
    else
      echo "        $name parent unanimous=$u"
      bad "$name sandwich parent" "unanimous=$u"
    fi
  fi
}

dogfood_git kizu /Users/annenpolka/ghq/github.com/annenpolka/kizu
dogfood_git sitbone /Users/annenpolka/ghq/github.com/annenpolka/sitbone
dogfood_git voidtrace /Users/annenpolka/ghq/github.com/annenpolka/voidtrace
dogfood_git tenaoshi /Users/annenpolka/ghq/github.com/annenpolka/tenaoshi
dogfood_git relico /Users/annenpolka/ghq/github.com/annenpolka/relico

dogfood_go() {
  local repo="$1"
  if [[ ! -d "$repo/.git" && ! -f "$repo/.git" ]]; then
    echo "  skip  golang/go (missing $repo)"
    return
  fi
  local j u
  j="$("$LODGE" --json --report-only -C "$repo" "$ROOT/fixtures/go-iotest.json")"
  u="$(printf '%s' "$j" | unanimous_of)"
  echo "        golang/go iotest against HEAD unanimous=$u"
  if [[ "$u" == "APPLIED" ]]; then
    ok "live golang/go iotest APPLIED at HEAD"
  else
    bad "live golang/go iotest" "unanimous=$u (want APPLIED)"
  fi
}
dogfood_go /Users/annenpolka/ghq/github.com/golang/go

echo
echo "======== summary: $PASS passed, $FAIL failed ========"
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
exit 0
