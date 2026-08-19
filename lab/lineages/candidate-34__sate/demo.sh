#!/usr/bin/env bash
# End-to-end: selftest, four occupancy fates, suggestions, sandwich, real repos.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SATE="$ROOT/sate"
chmod +x "$SATE"

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
  # stdin: sate --json
  python3 -c 'import json,sys; print(json.load(sys.stdin)["unanimous"])'
}

echo "======== 1. selftest ========"
if "$SATE" --selftest --no-fuzz; then
  ok "selftest (no-fuzz)"
else
  bad "selftest (no-fuzz)" "exit $?"
fi
if "$SATE" --selftest --fuzz; then
  ok "selftest (fuzz)"
else
  bad "selftest (fuzz)" "exit $?"
fi

DEMO="$(mktemp -d "${TMPDIR:-/tmp}/sate-demo.XXXXXX")"
cleanup() { rm -rf "$DEMO"; }
trap cleanup EXIT

git_init() {
  local d="$1"
  mkdir -p "$d"
  git -C "$d" init -q -b main
  git -C "$d" config user.name sate-demo
  git -C "$d" config user.email sate@demo
  git -C "$d" config commit.gpgsign false
}

echo "======== 2. occupancy sandwich (patch(C) vs C / C^) ========"
git_init "$DEMO/sand"
printf 'x = 1\n' > "$DEMO/sand/app.py"
git -C "$DEMO/sand" add app.py
git -C "$DEMO/sand" commit -q -m t0
printf 'x = 2\n' > "$DEMO/sand/app.py"
git -C "$DEMO/sand" add app.py
git -C "$DEMO/sand" commit -q -m 't1 bump'
got="$("$SATE" --json --report-only -C "$DEMO/sand" --against HEAD --git HEAD | unanimous_of)"
assert_eq "sandwich HEAD is APPLIED" "$got" "APPLIED"
got="$("$SATE" --json --report-only -C "$DEMO/sand" --against HEAD^ --git HEAD | unanimous_of)"
assert_eq "sandwich parent is PENDING" "$got" "PENDING"
# worktree dirty back to old value → PENDING against worktree
printf 'x = 1\n' > "$DEMO/sand/app.py"
got="$("$SATE" --json --report-only -C "$DEMO/sand" --git HEAD | unanimous_of)"
assert_eq "uncommitted revert is PENDING" "$got" "PENDING"

echo "======== 3. four fates in one tree ========"
git_init "$DEMO/four"
mkdir -p "$DEMO/four/src" "$DEMO/four/docs"
cat > "$DEMO/four/src/add.py" << 'PY'
def add(a, b):
    return a - b
PY
cat > "$DEMO/four/src/mix.py" << 'PY'
def f():
    a = 1
    b = 2
    return a + b
PY
printf 'hello\n' > "$DEMO/four/docs/plan.md"
printf 'keep\n' > "$DEMO/four/src/keep.py"
git -C "$DEMO/four" add -A
git -C "$DEMO/four" commit -q -m t0

# patches written as files (not yet applied, except we apply some by editing the tree)
cat > "$DEMO/pending.patch" << 'EOF'
diff --git a/src/add.py b/src/add.py
--- a/src/add.py
+++ b/src/add.py
@@ -1,2 +1,2 @@
 def add(a, b):
-    return a - b
+    return a + b
EOF

# APPLIED: tree already has the after-image
cat > "$DEMO/four/src/add.py" << 'PY'
def add(a, b):
    return a + b
PY
got="$("$SATE" --json --report-only -C "$DEMO/four" "$DEMO/pending.patch" | unanimous_of)"
assert_eq "after-image present → APPLIED" "$got" "APPLIED"

# PENDING: restore before
cat > "$DEMO/four/src/add.py" << 'PY'
def add(a, b):
    return a - b
PY
got="$("$SATE" --json --report-only -C "$DEMO/four" "$DEMO/pending.patch" | unanimous_of)"
assert_eq "before-image present → PENDING" "$got" "PENDING"
code=0
set +e
"$SATE" --quiet --report-only -C "$DEMO/four" "$DEMO/pending.patch" >/dev/null
# without --report-only, PENDING exits 1
"$SATE" --quiet -C "$DEMO/four" "$DEMO/pending.patch" >/dev/null
code=$?
set -e
assert_eq "PENDING exit 1" "$code" "1"

# SUPERSEDED
cat > "$DEMO/four/src/add.py" << 'PY'
def add(a, b):
    return a * b
PY
got="$("$SATE" --json --report-only -C "$DEMO/four" "$DEMO/pending.patch" | unanimous_of)"
assert_eq "neither image → SUPERSEDED" "$got" "SUPERSEDED"
code=0
set +e
"$SATE" --quiet -C "$DEMO/four" "$DEMO/pending.patch" >/dev/null
code=$?
set -e
assert_eq "SUPERSEDED exit 2" "$code" "2"

# MIXED
cat > "$DEMO/mix.patch" << 'EOF'
diff --git a/src/mix.py b/src/mix.py
--- a/src/mix.py
+++ b/src/mix.py
@@ -1,5 +1,5 @@
 def f():
-    a = 1
-    b = 2
+    a = 10
+    b = 20
     return a + b
EOF
cat > "$DEMO/four/src/mix.py" << 'PY'
def f():
    a = 10
    b = 2
    return a + b
PY
got="$("$SATE" --json --report-only -C "$DEMO/four" "$DEMO/mix.patch" | unanimous_of)"
assert_eq "partial apply → MIXED" "$got" "MIXED"

# DUPLEX: both exact before and after blocks live in the file
cat > "$DEMO/four/src/add.py" << 'PY'
def add(a, b):
    return a - b

def add(a, b):
    return a + b
PY
got="$("$SATE" --json --report-only -C "$DEMO/four" "$DEMO/pending.patch" | unanimous_of)"
assert_eq "both images copied → DUPLEX" "$got" "DUPLEX"

echo "======== 4. create / delete / stdin ========"
cat > "$DEMO/create.patch" << 'EOF'
diff --git a/docs/計画.md b/docs/計画.md
new file mode 100644
--- /dev/null
+++ b/docs/計画.md
@@ -0,0 +1,2 @@
+step one
+step two
EOF
got="$("$SATE" --json --report-only -C "$DEMO/four" "$DEMO/create.patch" | unanimous_of)"
assert_eq "create missing → PENDING" "$got" "PENDING"
mkdir -p "$DEMO/four/docs"
printf 'step one\nstep two\n' > "$DEMO/four/docs/計画.md"
got="$("$SATE" --json --report-only -C "$DEMO/four" "$DEMO/create.patch" | unanimous_of)"
assert_eq "create present → APPLIED" "$got" "APPLIED"

cat > "$DEMO/delete.patch" << 'EOF'
diff --git a/src/keep.py b/src/keep.py
deleted file mode 100644
--- a/src/keep.py
+++ /dev/null
@@ -1 +0,0 @@
-keep
EOF
got="$("$SATE" --json --report-only -C "$DEMO/four" "$DEMO/delete.patch" | unanimous_of)"
assert_eq "delete still there → PENDING" "$got" "PENDING"
rm -f "$DEMO/four/src/keep.py"
got="$("$SATE" --json --report-only -C "$DEMO/four" "$DEMO/delete.patch" | unanimous_of)"
assert_eq "delete gone → APPLIED" "$got" "APPLIED"

# stdin
got="$(git -C "$DEMO/sand" show --format= --patch HEAD | "$SATE" --json --report-only -C "$DEMO/sand" --against HEAD - | unanimous_of)"
assert_eq "stdin sandwich HEAD" "$got" "APPLIED"

echo "======== 5. review suggestions as patches ========"
mkdir -p "$DEMO/rev"
cat > "$DEMO/rev/mod.py" << 'PY'
TIMEOUT = 60
retries = 3
PY
# r1 taken, r2 open, r3 superseded (file gone)
"$SATE" --json --report-only -C "$DEMO/rev" --suggest "$ROOT/fixtures/suggest.jsonl" > "$DEMO/sug.json"
python3 - "$DEMO/sug.json" << 'PY'
import json,sys
r=json.load(open(sys.argv[1]))
fates=[h["fate"] for h in r["hunks"]]
assert r["unanimous"]=="SPLIT", r
assert fates[0]=="APPLIED", fates
assert fates[1]=="PENDING", fates
assert fates[2] in ("SUPERSEDED","PENDING"), fates
print("suggest fates", fates)
PY
ok "suggest JSONL TAKEN/OPEN/gone"

# GitHub body extract: tree has return a+b so suggestion 2 (int()) is PENDING
mkdir -p "$DEMO/gh/src"
cat > "$DEMO/gh/src/add.py" << 'PY'
def add(a, b):
    return a + b
PY
"$SATE" --json --report-only -C "$DEMO/gh" --suggest "$ROOT/fixtures/github-comments.json" > "$DEMO/gh.json"
python3 - "$DEMO/gh.json" << 'PY'
import json,sys
r=json.load(open(sys.argv[1]))
fates=[h["fate"] for h in r["hunks"]]
# first suggestion after-image is return a+b, which is already in the tree → APPLIED
# second suggestion wants int(a+b) → PENDING
assert "APPLIED" in fates, fates
assert "PENDING" in fates, fates
print("github fates", fates)
PY
ok "github suggestion extract TAKEN+OPEN"

echo "======== 6. sate log on a tiny history ========"
git_init "$DEMO/hist"
printf 'v=1\n' > "$DEMO/hist/v.txt"
git -C "$DEMO/hist" add v.txt
git -C "$DEMO/hist" commit -q -m 'v1'
printf 'v=2\n' > "$DEMO/hist/v.txt"
git -C "$DEMO/hist" add v.txt
git -C "$DEMO/hist" commit -q -m 'v2'
printf 'v=3\n' > "$DEMO/hist/v.txt"
git -C "$DEMO/hist" add v.txt
git -C "$DEMO/hist" commit -q -m 'v3'
# HEAD's own patch still occupies HEAD; v1's after-image (v=2) does not
"$SATE" --json --log 3 -C "$DEMO/hist" > "$DEMO/log.json"
python3 - "$DEMO/log.json" << 'PY'
import json,sys
r=json.load(open(sys.argv[1]))
unis=[c["unanimous"] for c in r["commits"]]
# newest first: v3 APPLIED, v2 SUPERSEDED (v=2 gone), v1 SUPERSEDED (v=1 gone)
assert unis[0]=="APPLIED", unis
assert unis[1]=="SUPERSEDED", unis
assert unis[2]=="SUPERSEDED", unis
print("log", unis)
PY
ok "log: newest occupies, older version bumps superseded"

echo "======== 7. dogfood real repositories ========"
dogfood() {
  local name="$1" repo="$2"
  if [[ ! -d "$repo/.git" && ! -f "$repo/.git" ]]; then
    echo "  skip  $name (missing $repo)"
    return
  fi
  local head parent
  head="$(git -C "$repo" rev-list --no-merges -n 1 HEAD)"
  parent="$(git -C "$repo" rev-parse "$head^" 2>/dev/null || true)"
  if [[ -z "$parent" ]]; then
    echo "  skip  $name (no parent)"
    return
  fi
  local j u
  j="$("$SATE" --json --report-only -C "$repo" --against "$head" --git "$head")"
  u="$(printf '%s' "$j" | unanimous_of)"
  if [[ "$u" == "APPLIED" || "$u" == "EMPTY" ]]; then
    ok "$name sandwich HEAD ($u)"
  else
    echo "        $name HEAD unanimous=$u counts=$(printf '%s' "$j" | python3 -c 'import json,sys; print(json.load(sys.stdin)["counts"])')"
    bad "$name sandwich HEAD" "unanimous=$u (want APPLIED after v2 prefix fix)"
  fi
  j="$("$SATE" --json --report-only -C "$repo" --against "$parent" --git "$head")"
  u="$(printf '%s' "$j" | unanimous_of)"
  if [[ "$u" == "PENDING" || "$u" == "EMPTY" ]]; then
    ok "$name sandwich parent ($u)"
  else
    echo "        $name parent unanimous=$u counts=$(printf '%s' "$j" | python3 -c 'import json,sys; print(json.load(sys.stdin)["counts"])')"
    if [[ "$u" == "SPLIT" ]]; then
      ok "$name sandwich parent (SPLIT — some hunks already at parent)"
    else
      bad "$name sandwich parent" "unanimous=$u"
    fi
  fi
}

dogfood kizu /Users/annenpolka/ghq/github.com/annenpolka/kizu
dogfood sitbone /Users/annenpolka/ghq/github.com/annenpolka/sitbone
dogfood voidtrace /Users/annenpolka/ghq/github.com/annenpolka/voidtrace
dogfood tenaoshi /Users/annenpolka/ghq/github.com/annenpolka/tenaoshi
dogfood relico /Users/annenpolka/ghq/github.com/annenpolka/relico

echo "======== 8. sate log sample (kizu, if present) ========"
KIZU=/Users/annenpolka/ghq/github.com/annenpolka/kizu
if [[ -d "$KIZU/.git" || -f "$KIZU/.git" ]]; then
  echo "---- kizu --log 8 ----"
  "$SATE" --log 8 -C "$KIZU" || true
  ok "kizu log ran"
else
  echo "  skip  kizu log"
fi

echo
echo "======== summary: $PASS passed, $FAIL failed ========"
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
exit 0
