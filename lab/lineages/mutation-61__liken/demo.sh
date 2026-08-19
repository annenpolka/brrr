#!/usr/bin/env bash
# demo.sh — must exit 0. Exercises the invert: shared stacks on a post-image overlay.
set -euo pipefail
cd "$(dirname "$0")"
chmod +x ./liken

echo "== unit tests =="
python3 -m unittest tests.test_overlay tests.test_stack tests.test_liken tests.test_dogfood -q

echo
echo "== 1. two added lines share given starts_with(a/); quoted-form does not =="
./liken --base :wt --diff fixtures/kin.diff --same-as 'fn parse_header | given starts_with(a/)' --explain
echo
echo "-- quoted-form return Some(1) is a different stack (must be absent above) --"
out=$(./liken --base :wt --diff fixtures/kin.diff --same-as 'fn parse_header | given starts_with(a/)' --tsv)
echo "$out" | grep -q 'let a_side' || { echo "missing a_side"; exit 1; }
echo "$out" | grep -q 'let b_side' || { echo "missing b_side"; exit 1; }
if echo "$out" | grep -q 'return Some(1)'; then
  echo "quoted-form leaked into given starts_with(a/)" >&2
  exit 1
fi
echo "quoted-form excluded ok"

echo
echo "== 2. overlay a NEW if that HEAD does not contain =="
echo "-- liken (post-image): added return is under if bytes.len() > 100"
./liken --base :wt --diff fixtures/newif.diff --same-as 'if bytes.len() > 100' --explain
echo
echo "-- contrast: HEAD line 11 is still 'let p = ...' (when --diff's lie) --"
sed -n '11p' fixtures/guards.rs

echo
echo "== 3. overlay does not write the worktree =="
test ! -e fixtures/kin.rs
./liken --base :wt --diff fixtures/kin.diff --same-as 'given starts_with(a/)' -q
test ! -e fixtures/kin.rs
echo "fixtures/kin.rs still absent (never applied)"

echo
echo "== 4. unplaced hunk / no match exits 1 =="
set +e
./liken --base :wt --diff fixtures/mismatch.diff --same-as 'given starts_with(a/)' --tsv >/dev/null
rc=$?
set -e
echo "mismatch rc=$rc (want 1)"
test "$rc" -eq 1

echo
echo "== 5. no diff is usage (exit 2); directory operand refused =="
set +e
./liken --tsv >/dev/null 2>/tmp/liken-usage.err
rc=$?
set -e
echo "usage rc=$rc (want 2)"
test "$rc" -eq 2
set +e
./liken --diff fixtures/kin.diff fixtures >/dev/null 2>/tmp/liken-walk.err
rc=$?
set -e
echo "walk-refuse rc=$rc (want 2)"
test "$rc" -eq 2

KIZU="${KIZU:-/Users/annenpolka/ghq/github.com/annenpolka/kizu}"
SITBONE="${SITBONE:-/Users/annenpolka/ghq/github.com/annenpolka/sitbone}"

if [[ -f "$KIZU/src/git/parse.rs" ]]; then
  echo
  echo "== dogfood: kizu parse.rs birth, two lines under given starts_with(a/) =="
  before=$(git -C "$KIZU" status --porcelain -- src/git/parse.rs)
  echo "-- --same-as parse.rs:60 is exact (let b_side only; a_side is a shallower stack) --"
  git -C "$KIZU" diff 3b3e0a9^ 3b3e0a9 -- src/git/parse.rs \
    | ./liken -C "$KIZU" --base 3b3e0a9^ --same-as src/git/parse.rs:60 --explain
  git -C "$KIZU" diff 3b3e0a9^ 3b3e0a9 -- src/git/parse.rs \
    | ./liken -C "$KIZU" --base 3b3e0a9^ --same-as 'fn parse_diff_git_header | given starts_with(a/)' --payload --tsv \
    | awk -F'\t' '
        $0 ~ /let a_side/ { a=1; print }
        $0 ~ /let b_side/ { b=1; print }
        $0 ~ /return Some\(bytes_to_path\(&b_decoded/ { leak=1; print }
        END {
          if (!a || !b) { print "kizu a_side/b_side miss" > "/dev/stderr"; exit 1 }
          if (leak) { print "quoted-form leaked" > "/dev/stderr"; exit 1 }
        }
      '
  after=$(git -C "$KIZU" status --porcelain -- src/git/parse.rs)
  test "$before" = "$after" || { echo "kizu worktree dirtied" >&2; exit 1; }
  echo "kizu overlay left worktree clean"
fi

if [[ -f "$SITBONE/Sources/SitboneCore/PresenceArbiter.swift" ]]; then
  echo
  echo "== dogfood: sitbone hysteresis, applyHysteresis under guards; init precondition does not =="
  before=$(git -C "$SITBONE" status --porcelain -- Sources/SitboneCore/PresenceArbiter.swift)
  git -C "$SITBONE" diff e9b0f75^ e9b0f75 -- Sources/SitboneCore/PresenceArbiter.swift \
    | ./liken -C "$SITBONE" --base e9b0f75^ --same-as 'guard isEnabled' --payload --tsv \
    | awk -F'\t' '
        /applyHysteresis\(smoothedScore: smoothedScore\)/ { hit=1; print }
        /precondition/ { leak=1; print }
        END {
          if (!hit) { print "sitbone guard miss" > "/dev/stderr"; exit 1 }
          if (leak) { print "init precondition leaked into guard isEnabled" > "/dev/stderr"; exit 1 }
        }
      '
  after=$(git -C "$SITBONE" status --porcelain -- Sources/SitboneCore/PresenceArbiter.swift)
  test "$before" = "$after" || { echo "sitbone worktree dirtied" >&2; exit 1; }
  echo "sitbone overlay left worktree clean"
fi

echo
echo "demo ok"
