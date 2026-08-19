#!/usr/bin/env bash
# demo.sh — must exit 0. Exercises the post-image primitive, not a screenshot.
set -euo pipefail
cd "$(dirname "$0")"
chmod +x ./graft

echo "== unit tests =="
python3 -m unittest tests.test_overlay tests.test_engines tests.test_graft tests.test_dogfood -q

echo
echo "== 1. overlay an insert already in the same arm =="
./graft --base :wt --diff fixtures/insert.diff --explain

echo
echo "== 2. overlay a NEW if that HEAD does not contain =="
echo "-- graft (post-image): the added return runs under if bytes.len()>100"
./graft --base :wt --diff fixtures/newif.diff --explain
echo
echo "-- contrast: looking up the same new-line numbers in HEAD is the wrong file"
echo "   (this is what when --diff did). HEAD line 11 is still 'let p = ...':"
sed -n '11p' fixtures/guards.rs

echo
echo "== 3. new file: every added line is placed on a file that does not exist yet =="
./graft --base :wt --diff fixtures/newfile.diff --group

echo
echo "== 4. nested-total quoted-path given (the when/whence hole) =="
./graft --now fixtures/quoted.rs:32 --explain

echo
echo "== 5. unplaced hunk exits 1 =="
set +e
./graft --base :wt --diff fixtures/mismatch.diff --tsv >/dev/null
rc=$?
set -e
echo "mismatch rc=$rc (want 1)"
test "$rc" -eq 1

echo
echo "== 6. no diff / no --now is usage (exit 2) =="
set +e
./graft --tsv >/dev/null 2>/tmp/graft-usage.err
rc=$?
set -e
echo "usage rc=$rc (want 2)"
test "$rc" -eq 2

KIZU="${KIZU:-/Users/annenpolka/ghq/github.com/annenpolka/kizu}"
SITBONE="${SITBONE:-/Users/annenpolka/ghq/github.com/annenpolka/sitbone}"

if [[ -f "$KIZU/src/git/parse.rs" ]]; then
  echo
  echo "== dogfood: kizu parse.rs sandwich (git diff A B | graft --base A) =="
  git -C "$KIZU" diff 3b3e0a9^ 3b3e0a9 -- src/git/parse.rs \
    | ./graft -C "$KIZU" --base 3b3e0a9^ --tsv \
    | awk -F'\t' '$1=="src/git/parse.rs:60"{print; found=1} END{exit found?0:1}'
  echo
  echo "== dogfood: kizu parse.rs:60 --now (quoted-path given) =="
  ./graft --now "$KIZU/src/git/parse.rs:60" --explain
fi

if [[ -f "$SITBONE/Sources/SitboneCore/PresenceArbiter.swift" ]]; then
  echo
  echo "== dogfood: sitbone PresenceArbiter hysteresis sandwich =="
  git -C "$SITBONE" diff e9b0f75^ e9b0f75 -- Sources/SitboneCore/PresenceArbiter.swift \
    | ./graft -C "$SITBONE" --base e9b0f75^ --explain \
    | awk '
        /applyHysteresis\(smoothedScore: smoothedScore\)/ { print; hit=1 }
        /return smoothedScore < absentThreshold/ { print; hit=1 }
        END { if (!hit) { print "sitbone sandwich miss" > "/dev/stderr"; exit 1 } }
      '
fi

echo
echo "demo ok"
