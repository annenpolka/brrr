#!/usr/bin/env bash
# Extra args (e.g. ./demo.sh 0) are ignored.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
chmod +x "$ROOT/ply"
PLY="$ROOT/ply"

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
assert_not() {
  local name="$1"
  shift
  if "$@"; then
    FAIL=$((FAIL + 1))
    echo "  FAIL $name (expected failure)" >&2
  else
    PASS=$((PASS + 1))
    echo "  ok  $name"
  fi
}

echo "======== 1. selftest ========"
"$PLY" --selftest

echo "======== 2. fixture patch ========"
FIX="$(mktemp -d "${TMPDIR:-/tmp}/ply-demo.XXXXXX")"
cleanup() { rm -rf "$FIX"; }
trap cleanup EXIT

git -C "$FIX" init -q -b main
git -C "$FIX" config user.name ply
git -C "$FIX" config user.email ply@demo
git -C "$FIX" config commit.gpgsign false

cat > "$FIX/src.rs" << 'RS'
fn main() {
    let timeout = 30; // seconds
    let retries = 3;
    println!("boot");
}
RS
git -C "$FIX" add src.rs
git -C "$FIX" commit -q -m "seed"

cat > "$FIX/src.rs" << 'RS'
fn main() {
    let timeout = 60; // secs
    let retries = 3;
    println!("boot");
}
RS
git -C "$FIX" add src.rs
git -C "$FIX" commit -q -m "docs+number on same line"

cat > "$FIX/src.rs" << 'RS'
fn start() {
    let timeout = 60; // secs
    let retries = 3;
    println!("boot");
}
RS
git -C "$FIX" add src.rs
git -C "$FIX" commit -q -m "rename main -> start"

echo "----- mixed ply (number + comment, same line) -----"
out1="$("$PLY" --repo "$FIX" --git HEAD~2..HEAD~1 --tsv)"
echo "$out1"
assert "number 30→60" grep -q $'number\tchg\t30\t60' <<<"$out1"
assert "comment seconds→secs" grep -q $'comment\tchg\tseconds\tsecs' <<<"$out1"
assert_not "mixed line did not invent ident chg" grep -q $'ident\tchg' <<<"$out1"

echo "----- ident rename, numbers untouched -----"
out2="$("$PLY" --repo "$FIX" --git HEAD~1..HEAD --class ident --tsv)"
echo "$out2"
assert "ident main→start" grep -q $'ident\tchg\tmain\tstart' <<<"$out2"
assert "rename has no number ply" "$PLY" --repo "$FIX" --git HEAD~1..HEAD --class number --check
assert_not "rename fails --only docs" "$PLY" --repo "$FIX" --git HEAD~1..HEAD --check --only docs,comment

echo "----- comment-only commit -----"
cat > "$FIX/src.rs" << 'RS'
fn start() {
    let timeout = 60; // timeout
    let retries = 3;
    println!("boot");
}
RS
git -C "$FIX" add src.rs
git -C "$FIX" commit -q -m "comment only"
assert "comment-only passes --only comment" "$PLY" --repo "$FIX" --git HEAD~1..HEAD --check --only comment

echo "======== 3. --files ========"
printf 'x = 1  // old\n' > "$FIX/a.py"
printf 'x = 2  // old\n' > "$FIX/b.py"
out3="$("$PLY" --files "$FIX/a.py" "$FIX/b.py" --class number --tsv)"
echo "$out3"
assert "files number 1→2" grep -q $'number\tchg\t1\t2' <<<"$out3"
assert_not "files number --check fails" "$PLY" --files "$FIX/a.py" "$FIX/b.py" --class number --check
assert "files comment --check clean" "$PLY" --files "$FIX/a.py" "$FIX/b.py" --class comment --check

echo "======== 4. dogfood ========"
dogfood() {
  local name="$1" repo="$2" range="$3"
  shift 3
  if [[ ! -d "$repo/.git" ]]; then
    echo "  skip $name (missing $repo)"
    return 0
  fi
  echo "----- $name $range $* -----"
  "$PLY" --repo "$repo" --git "$range" "$@"
}

dogfood kizu /Users/annenpolka/ghq/github.com/annenpolka/kizu HEAD~3..HEAD --op chg
dogfood sitbone /Users/annenpolka/ghq/github.com/annenpolka/sitbone HEAD~5..HEAD --class number,ident --op chg
dogfood tenaoshi /Users/annenpolka/ghq/github.com/annenpolka/tenaoshi HEAD~3..HEAD --class docs --op chg
dogfood voidtrace /Users/annenpolka/ghq/github.com/annenpolka/voidtrace HEAD~1..HEAD --class number --op chg

if [[ -d /Users/annenpolka/ghq/github.com/annenpolka/sitbone/.git ]]; then
  sb="$("$PLY" --repo /Users/annenpolka/ghq/github.com/annenpolka/sitbone --git HEAD~5..HEAD --class number,ident --tsv --op chg || true)"
  if grep -q $'0.4\t0.45' <<<"$sb"; then
    assert "sitbone hysteresis 0.4→0.45" true
  else
    echo "  note sitbone 0.4→0.45 not in HEAD~5 (history moved)"
  fi
  if grep -q $'threshold\tpresentThreshold' <<<"$sb"; then
    assert "sitbone threshold→presentThreshold" true
  else
    echo "  note sitbone rename not in HEAD~5 (history moved)"
  fi
fi
if [[ -d /Users/annenpolka/ghq/github.com/annenpolka/kizu/.git ]]; then
  kz="$("$PLY" --repo /Users/annenpolka/ghq/github.com/annenpolka/kizu --git HEAD~3..HEAD --class string --tsv --op chg || true)"
  if grep -q '0.5.1' <<<"$kz"; then
    assert "kizu version string ply" true
  else
    echo "  note kizu 0.5.1 not in HEAD~3 (history moved)"
  fi
fi

echo "======== 5. CJK prose is text, not punct ========"
printf '契約は蒸留\n' > "$FIX/old.md"
printf '契約は資産\n' > "$FIX/new.md"
out4="$("$PLY" --files "$FIX/old.md" "$FIX/new.md" --tsv)"
echo "$out4"
assert_not "CJK not punct" grep -q $'\tpunct\t' <<<"$out4"
assert "CJK is text" grep -q $'\ttext\t' <<<"$out4"

echo
echo "PASS=$PASS FAIL=$FAIL"
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
echo "demo ok"
exit 0
