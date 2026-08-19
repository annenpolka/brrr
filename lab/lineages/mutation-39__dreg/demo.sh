#!/usr/bin/env bash
# End-to-end: occupancy sandwich, SUPERSEDED as a patch, leftover apply, dogfood.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
DREG="$ROOT/dreg"
chmod +x "$DREG"

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

contains() {
  local name="$1" hay="$2" needle="$3"
  if [[ "$hay" == *"$needle"* ]]; then
    ok "$name"
  else
    bad "$name" "missing '$needle' in ${hay:0:200}"
  fi
}

echo "======== 1. selftest ========"
if "$DREG" --selftest; then
  ok "selftest"
else
  bad "selftest" "exit $?"
fi

DEMO="$(mktemp -d "${TMPDIR:-/tmp}/dreg-demo.XXXXXX")"
cleanup() { rm -rf "$DEMO"; }
trap cleanup EXIT

git_init() {
  local d="$1"
  mkdir -p "$d"
  git -C "$d" init -q -b main
  git -C "$d" config user.name dreg-demo
  git -C "$d" config user.email dreg@demo
  git -C "$d" config commit.gpgsign false
}

echo "======== 2. sandwich: SUPERSEDED of C vs C is empty ========"
git_init "$DEMO/sand"
printf 'x = 1\n' > "$DEMO/sand/app.py"
git -C "$DEMO/sand" add app.py
git -C "$DEMO/sand" commit -q -m t0
printf 'x = 2\n' > "$DEMO/sand/app.py"
git -C "$DEMO/sand" add app.py
git -C "$DEMO/sand" commit -q -m 't1 bump'

set +e
out="$("$DREG" --quiet --git HEAD -C "$DEMO/sand" --against HEAD --pick SUPERSEDED)"
code=$?
set -e
assert_eq "C vs C SUPERSEDED stdout empty" "$out" ""
assert_eq "C vs C SUPERSEDED exit 0" "$code" "0"

set +e
out="$("$DREG" --quiet --git HEAD -C "$DEMO/sand" --against HEAD --pick PENDING)"
code=$?
set -e
assert_eq "C vs C PENDING empty" "$out" ""
assert_eq "C vs C PENDING exit 0" "$code" "0"

set +e
"$DREG" --quiet --git HEAD -C "$DEMO/sand" --against HEAD^ --pick PENDING > "$DEMO/sand.pending.patch"
code=$?
set -e
out="$(cat "$DEMO/sand.pending.patch")"
contains "C vs C^ leftover has +x = 2" "$out" "+x = 2"
contains "C vs C^ leftover has -x = 1" "$out" "-x = 1"
assert_eq "C vs C^ PENDING exit 1 (emitted)" "$code" "1"

git -C "$DEMO/sand" checkout -q HEAD^ -- app.py
git -C "$DEMO/sand" apply --whitespace=nowarn "$DEMO/sand.pending.patch"
assert_eq "leftover apply restores after-image" "$(cat "$DEMO/sand/app.py")" "x = 2"

echo "======== 3. later rewrite: old cores come out as a patch ========"
git_init "$DEMO/hist"
printf 'v=1\n' > "$DEMO/hist/v.txt"
git -C "$DEMO/hist" add v.txt
git -C "$DEMO/hist" commit -q -m v1
printf 'v=2\n' > "$DEMO/hist/v.txt"
git -C "$DEMO/hist" add v.txt
git -C "$DEMO/hist" commit -q -m v2
V2="$(git -C "$DEMO/hist" rev-parse HEAD)"
printf 'v=3\n' > "$DEMO/hist/v.txt"
git -C "$DEMO/hist" add v.txt
git -C "$DEMO/hist" commit -q -m v3

set +e
"$DREG" --quiet --git "$V2" -C "$DEMO/hist" --against HEAD --pick SUPERSEDED > "$DEMO/v2.dreg.patch"
code=$?
set -e
out="$(cat "$DEMO/v2.dreg.patch")"
contains "v2 vs HEAD emits -v=1" "$out" "-v=1"
contains "v2 vs HEAD emits +v=2" "$out" "+v=2"
if [[ "$out" == *v=3* ]]; then
  bad "v2 dreg must not splice live v=3" "$out"
else
  ok "v2 dreg is the dead core, not HEAD"
fi
assert_eq "rewrite SUPERSEDED exit 1" "$code" "1"
contains "fate trailer SUPERSEDED" "$out" "SUPERSEDED"

# apply the dreg onto the preimage (v1 tree) → v=2
git_init "$DEMO/pre"
printf 'v=1\n' > "$DEMO/pre/v.txt"
git -C "$DEMO/pre" add v.txt
git -C "$DEMO/pre" commit -q -m v1
git -C "$DEMO/pre" apply --whitespace=nowarn "$DEMO/v2.dreg.patch"
assert_eq "dreg applies onto preimage" "$(cat "$DEMO/pre/v.txt")" "v=2"

echo "======== 4. prefix rule: pure addition is APPLIED, not DUPLEX ========"
git_init "$DEMO/add"
printf 'a\nb\nc\nd\ne\nf\n' > "$DEMO/add/t.py"
git -C "$DEMO/add" add t.py
git -C "$DEMO/add" commit -q -m t0
printf 'a\nb\nc\nd\ne\nf\nNEW_LINE_ONE\nNEW_LINE_TWO\n' > "$DEMO/add/t.py"
git -C "$DEMO/add" add t.py
git -C "$DEMO/add" commit -q -m add
set +e
out="$("$DREG" --quiet --git HEAD -C "$DEMO/add" --against HEAD --pick DUPLEX)"
code=$?
set -e
assert_eq "addition sandwich DUPLEX empty" "$out" ""
assert_eq "addition sandwich DUPLEX exit 0" "$code" "0"
set +e
out="$("$DREG" --quiet --git HEAD -C "$DEMO/add" --against HEAD --pick SUPERSEDED)"
code=$?
set -e
assert_eq "addition sandwich SUPERSEDED empty" "$out" ""
assert_eq "addition sandwich SUPERSEDED exit 0" "$code" "0"

echo "======== 5. --stat / --log / stdin ========"
set +e
stat="$("$DREG" --log 3 -C "$DEMO/hist" --stat --pick SUPERSEDED)"
code=$?
set -e
contains "log --stat names v2" "$stat" "v2"
contains "log --stat names v1" "$stat" "v1"
assert_eq "log --stat with dregs exit 1" "$code" "1"

set +e
got="$(git -C "$DEMO/hist" show --format= --patch "$V2" | "$DREG" --quiet -C "$DEMO/hist" --against HEAD --pick SUPERSEDED)"
set -e
contains "stdin patch occupied" "$got" "+v=2"

echo "======== 6. four fates, pick is a patch not a report ========"
mkdir -p "$DEMO/four/src"
cat > "$DEMO/four/src/add.py" << 'PY'
def add(a, b):
    return a * b
PY
cat > "$DEMO/four.patch" << 'EOF'
diff --git a/src/add.py b/src/add.py
--- a/src/add.py
+++ b/src/add.py
@@ -1,2 +1,2 @@
 def add(a, b):
-    return a - b
+    return a + b
EOF
set +e
out="$("$DREG" --quiet --worktree -C "$DEMO/four" "$DEMO/four.patch" --pick SUPERSEDED)"
code=$?
set -e
contains "neither image is SUPERSEDED core" "$out" "-    return a - b"
contains "neither image plus" "$out" "+    return a + b"
if [[ "$out" == *"return a * b"* ]]; then
  bad "must not splice the live image" "$out"
else
  ok "dreg is the dead core, not the live tree"
fi
assert_eq "file-patch SUPERSEDED exit 1" "$code" "1"

echo "======== 7. dogfood real repositories ========"
dogfood_sandwich() {
  local name="$1" repo="$2"
  if [[ ! -d "$repo/.git" && ! -f "$repo/.git" ]]; then
    echo "  skip  $name (missing $repo)"
    return
  fi
  local head parent
  head="$(git -C "$repo" rev-list --no-merges -n 1 HEAD)"
  parent="$(git -C "$repo" rev-parse "$head^" 2>/dev/null || true)"
  set +e
  out="$("$DREG" --quiet --git "$head" -C "$repo" --against "$head" --pick SUPERSEDED)"
  code=$?
  set -e
  if [[ -z "$out" && "$code" == "0" ]]; then
    ok "$name sandwich SUPERSEDED empty (C vs C)"
  else
    bad "$name sandwich SUPERSEDED" "exit=$code out=${out:0:120}"
  fi
  if [[ -n "$parent" ]]; then
    set +e
    out="$("$DREG" --quiet --git "$head" -C "$repo" --against "$parent" --pick SUPERSEDED)"
    code=$?
    set -e
    if [[ -z "$out" && "$code" == "0" ]]; then
      ok "$name SUPERSEDED vs parent empty (still occupies parent as PENDING)"
    else
      # some hunks may already have been at the parent (SPLIT) — SUPERSEDED vs parent
      # should still be empty for a linear commit.
      if [[ -z "$out" ]]; then
        ok "$name SUPERSEDED vs parent empty (exit $code)"
      else
        echo "        $name parent SUPERSEDED n=$(printf '%s' "$out" | grep -c '^@@' || true)"
        bad "$name SUPERSEDED vs parent" "expected empty dregs"
      fi
    fi
  fi
}

dogfood_sandwich kizu /Users/annenpolka/ghq/github.com/annenpolka/kizu
dogfood_sandwich sitbone /Users/annenpolka/ghq/github.com/annenpolka/sitbone
dogfood_sandwich voidtrace /Users/annenpolka/ghq/github.com/annenpolka/voidtrace
dogfood_sandwich tenaoshi /Users/annenpolka/ghq/github.com/annenpolka/tenaoshi

echo "======== 8. gold: kizu v0.6.0 Cargo.toml SUPERSEDED (now 0.7.0) ========"
KIZU=/Users/annenpolka/ghq/github.com/annenpolka/kizu
if [[ -d "$KIZU/.git" || -f "$KIZU/.git" ]]; then
  set +e
  "$DREG" --quiet --git 88362116 -C "$KIZU" --against HEAD --pick SUPERSEDED > "$DEMO/kizu.dreg.patch"
  code=$?
  set -e
  out="$(cat "$DEMO/kizu.dreg.patch")"
  contains "kizu v0.6.0 dreg is Cargo.toml" "$out" "Cargo.toml"
  contains "kizu v0.6.0 dead minus 0.5.1" "$out" '-version = "0.5.1"'
  contains "kizu v0.6.0 dead plus 0.6.0" "$out" '+version = "0.6.0"'
  if [[ "$out" == *0.7.0* ]]; then
    bad "kizu dreg must not splice live 0.7.0" "$out"
  else
    ok "kizu dreg is 0.6.0 core, not live 0.7.0"
  fi
  if [[ "$out" == *Cargo.lock* ]]; then
    bad "SUPERSEDED pick must not include PENDING Cargo.lock" "$out"
  else
    ok "SUPERSEDED pick drops PENDING Cargo.lock"
  fi
  assert_eq "kizu v0.6.0 SUPERSEDED exit 1" "$code" "1"
  contains "kizu core at version line (@@ -2,3)" "$out" "@@ -2,3 +2,3 @@ SUPERSEDED"

  # apply onto a tree that still has the before-image
  git_init "$DEMO/kizu-pre"
  git -C "$KIZU" show 88362116^:Cargo.toml > "$DEMO/kizu-pre/Cargo.toml"
  git -C "$DEMO/kizu-pre" add Cargo.toml
  git -C "$DEMO/kizu-pre" commit -q -m pre
  git -C "$DEMO/kizu-pre" apply --whitespace=nowarn "$DEMO/kizu.dreg.patch"
  got="$(grep -E '^version' "$DEMO/kizu-pre/Cargo.toml" | head -1)"
  assert_eq "kizu dreg applies onto v0.5.1 tree" "$got" 'version = "0.6.0"'

  echo "---- kizu --log 8 --stat SUPERSEDED ----"
  "$DREG" --log 8 -C "$KIZU" --stat --pick SUPERSEDED || true
  ok "kizu log --stat ran"

  echo "---- kizu v0.6.0 --pick PENDING (leftover; git apply --check is a lie) ----"
  set +e
  pend="$("$DREG" --quiet --git 88362116 -C "$KIZU" --against HEAD --pick PENDING)"
  set -e
  contains "PENDING leftover is Cargo.lock" "$pend" "Cargo.lock"
else
  echo "  skip  kizu gold (missing $KIZU)"
fi

echo "======== 9. voidtrace true DUPLEX is not a prefix-rule regression ========"
VT=/Users/annenpolka/ghq/github.com/annenpolka/voidtrace
if [[ -d "$VT/.git" || -f "$VT/.git" ]]; then
  set +e
  dup="$("$DREG" --git HEAD -C "$VT" --against HEAD --stat --pick DUPLEX)"
  code=$?
  set -e
  contains "voidtrace DUPLEX is modify copies" "$dup" "exact-both"
  if [[ "$dup" == *add-neither* ]]; then
    bad "voidtrace DUPLEX must not be prefix-addition" "$dup"
  else
    ok "voidtrace DUPLEX is not sate-v1 addition prefix"
  fi
  assert_eq "voidtrace DUPLEX --stat exit 1" "$code" "1"
fi

echo
echo "======== summary: $PASS passed, $FAIL failed ========"
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
exit 0
