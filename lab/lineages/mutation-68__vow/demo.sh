#!/usr/bin/env bash
# Exercise vow. Exit 0 only if every case holds.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
chmod +x "$ROOT/vow"
PY="${PYTHON:-python3}"
VOW=("$PY" "$ROOT/vow.py")
FIX="$ROOT/fixtures"
passed=0
failed=0

ok() {
  passed=$((passed + 1))
  echo "ok  $1"
}

fail() {
  failed=$((failed + 1))
  echo "FAIL  $1" >&2
  echo "      $2" >&2
}

assert_eq() {
  local got="$1" want="$2" label="$3"
  if [[ "$got" == "$want" ]]; then
    ok "$label"
  else
    fail "$label" "want=$want got=$got"
  fi
}

assert_exit() {
  local got="$1" want="$2" label="$3"
  if [[ "$got" -eq "$want" ]]; then
    ok "$label"
  else
    fail "$label" "exit want=$want got=$got"
  fi
}

status_of() {
  "${VOW[@]}" --json "$1" | "$PY" -c 'import json,sys; print(json.load(sys.stdin)["status"])'
}

req_of() {
  local file="$1" axis="$2"
  "${VOW[@]}" --json "$file" | "$PY" -c "import json,sys; print(json.load(sys.stdin)['require'].get('$axis',''))"
}

pair_of() {
  "${VOW[@]}" --from-fail --json < "$1" | "$PY" -c 'import json,sys; d=json.load(sys.stdin); print(d.get("pair") or d["pairs"][0]["pair"])'
}

side_req() {
  local file="$1" side="$2" axis="$3"
  "${VOW[@]}" --from-fail --json < "$file" | "$PY" -c "import json,sys; d=json.load(sys.stdin); p=d['pairs'][0]; print(p['$side']['require'].get('$axis',''))"
}

echo "======== 1. self-test + unittest ========"
"${VOW[@]}" --self-test
ok "vow --self-test"
"$PY" -m unittest discover -s tests -q
ok "unittest discover"

echo "======== 2. gold: comment vs assert (oath window) ========"
assert_eq "$(status_of "$FIX/comment_only.py")" "OPEN" "comment # ran on alice is OPEN"
assert_eq "$(req_of "$FIX/comment_only.py" USER)" "" "comment does not require USER"
assert_eq "$(status_of "$FIX/env_assert.py")" "BOUND" "assert environ USER == alice is BOUND"
assert_eq "$(req_of "$FIX/env_assert.py" USER)" "alice" "env assert USER=alice"
assert_eq "$(status_of "$FIX/comment.snap")" "OPEN" "snap comment is OPEN"

echo "======== 3. unary snapshots still two machines, not lees ========"
assert_eq "$(status_of "$FIX/local.snap")" "BOUND" "local.snap BOUND"
assert_eq "$(req_of "$FIX/local.snap" HOME)" "/Users/alice" "local HOME=/Users/alice"
assert_eq "$(status_of "$FIX/ci.snap")" "BOUND" "ci.snap BOUND"
assert_eq "$(req_of "$FIX/ci.snap" HOME)" "/home/runner" "ci HOME=/home/runner"
assert_eq "$(status_of "$FIX/spec_only.snap")" "OPEN" "spec_only OPEN"
assert_eq "$(status_of "$FIX/conflict.snap")" "UNSAT" "conflict UNSAT"

echo "======== 4. sitbone-shaped title is fixture, not TAINTED ========"
st="$(status_of "$FIX/title.swift")"
if [[ "$st" == "OPEN" || "$st" == "FIXTURE" ]]; then
  ok "title.swift $st (not BOUND, not TAINTED)"
else
  fail "title.swift OPEN/FIXTURE" "$st"
fi
assert_eq "$(req_of "$FIX/title.swift" USER)" "" "title does not require USER"

echo "======== 5. kizu quoting fixture is SPEC; comments silent ========"
st="$(status_of "$FIX/payload.rs")"
if [[ "$st" == "SPEC" || "$st" == "OPEN" ]]; then
  ok "payload.rs $st (quoting is spec)"
else
  fail "payload.rs SPEC/OPEN" "$st"
fi
assert_eq "$(req_of "$FIX/payload.rs" HOME)" "" "John Doe quote does not require HOME"

echo "======== 6. --from-fail pair: two oaths, not residue ========"
assert_eq "$(pair_of "$FIX/pytest_fail.txt")" "EXPECTED-BOUND vs ACTUAL-BOUND" "pytest pair two BOUND"
assert_eq "$(side_req "$FIX/pytest_fail.txt" expected HOME)" "/Users/alice" "pytest expected HOME=alice"
assert_eq "$(side_req "$FIX/pytest_fail.txt" actual HOME)" "/home/runner" "pytest actual HOME=runner"
assert_eq "$(side_req "$FIX/pytest_fail.txt" expected platform)" "Darwin" "pytest expected Darwin"
assert_eq "$(side_req "$FIX/pytest_fail.txt" actual platform)" "Linux" "pytest actual Linux"

echo "======== 7. actual=/Users/alice expected=tmp → EXPECTED-OPEN vs ACTUAL-BOUND ========"
assert_eq "$(pair_of "$FIX/xctest_fail.txt")" "EXPECTED-OPEN vs ACTUAL-BOUND" "xctest tmp vs alice"
assert_eq "$(side_req "$FIX/xctest_fail.txt" actual HOME)" "/Users/alice" "xctest actual HOME=alice"
assert_eq "$(side_req "$FIX/xctest_fail.txt" expected HOME)" "" "xctest expected tmp has no HOME"
assert_eq "$(pair_of "$FIX/pytest_vv_tmp.txt")" "EXPECTED-OPEN vs ACTUAL-BOUND" "pytest -vv tmp vs alice"
assert_eq "$(side_req "$FIX/pytest_vv_tmp.txt" actual HOME)" "/Users/alice" "pytest -vv actual alice"
assert_eq "$(pair_of "$FIX/junit_tmp.txt")" "EXPECTED-OPEN vs ACTUAL-BOUND" "junit tmp vs alice"
assert_eq "$(pair_of "$FIX/junit_xml.xml")" "EXPECTED-OPEN vs ACTUAL-BOUND" "junit xml tmp vs alice"

echo "======== 8. # ran on in a fail dump does not bind ========"
pair="$(pair_of "$FIX/comment_in_fail.txt")"
if [[ "$pair" == *"OPEN"*"OPEN"* ]]; then
  ok "comment-in-fail pair is OPEN vs OPEN ($pair)"
else
  fail "comment-in-fail OPEN vs OPEN" "$pair"
fi
assert_eq "$(side_req "$FIX/comment_in_fail.txt" expected USER)" "" "ran-on comment does not bind expected USER"
assert_eq "$(side_req "$FIX/comment_in_fail.txt" actual USER)" "" "ran-on comment does not bind actual USER"
assert_eq "$(side_req "$FIX/comment_in_fail.txt" expected HOME)" "" "ran-on comment does not bind HOME"

echo "======== 9. emit + apply (unary + pair side) ========"
pred="$("${VOW[@]}" --emit shell "$FIX/local.snap")"
if [[ "$pred" == *"Darwin"* && "$pred" == *"/Users/alice"* ]]; then
  ok "emit shell is Darwin ∧ HOME=alice"
else
  fail "emit shell is Darwin ∧ HOME=alice" "$pred"
fi
pred="$("${VOW[@]}" --from-fail --side actual --emit shell < "$FIX/pytest_fail.txt")"
if [[ "$pred" == *"/home/runner"* ]]; then
  ok "emit actual side is runner HOME"
else
  fail "emit actual side is runner HOME" "$pred"
fi

code=0
"${VOW[@]}" --apply "$FIX/spec_only.snap" >/dev/null || code=$?
assert_exit "$code" 0 "OPEN --apply 0"

code=0
"${VOW[@]}" --apply "$FIX/conflict.snap" >/dev/null || code=$?
assert_exit "$code" 2 "UNSAT --apply 2"

code=0
"${VOW[@]}" --apply "$FIX/local.snap" >/dev/null || code=$?
home="$("$PY" -c 'from pathlib import Path; print(Path.home())')"
if [[ "$home" == "/Users/alice" ]]; then
  assert_exit "$code" 0 "alice snap MATCH on alice host"
else
  assert_exit "$code" 1 "alice snap MISS on this host ($home)"
fi

echo "======== 10. live machine snap MATCH ========"
LIVE="$ROOT/demo-tmp"
rm -rf "$LIVE"
mkdir -p "$LIVE"
user="$("$PY" -c 'import getpass; print(getpass.getuser())')"
printf 'spec:ok\nhome:%s\nuser:%s\ntimeout:30\n' "$home" "$user" > "$LIVE/live.snap"
printf 'spec:ok\ntimeout:30\n' > "$LIVE/portable.snap"
code=0
"${VOW[@]}" --apply --match "$LIVE/live.snap" >/dev/null || code=$?
assert_exit "$code" 0 "live snap MATCH --apply 0"
st="$(status_of "$LIVE/live.snap")"
assert_eq "$st" "BOUND" "live snap BOUND to this host"

echo "======== 11. ugly paths ========"
st="$(status_of "$FIX/ugly/dir with spaces/snap.txt")"
assert_eq "$st" "BOUND" "space path snap BOUND"
st="$(status_of "$FIX/ugly/日本語/期待.txt")"
assert_eq "$st" "BOUND" "unicode path snap BOUND"

echo "======== 12. dogfood sitbone / kizu (read-only) ========"
DOGFOOD_ROOT="${DOGFOOD_ROOT:-/Users/annenpolka/ghq/github.com/annenpolka}"
count_status() {
  local tsv="$1" st="$2"
  grep -c $'^status\t'"$st" "$tsv" 2>/dev/null || true
}
for repo in sitbone kizu; do
  dir="$DOGFOOD_ROOT/$repo"
  if [[ ! -d "$dir" ]]; then
    echo "skip  dogfood $repo (missing)"
    continue
  fi
  tsv="/tmp/vow-dogfood-$$-$repo.tsv"
  set +e
  "${VOW[@]}" --scan --porcelain -C "$dir" >"$tsv" 2>/tmp/vow-dogfood-$$.err
  code=$?
  set -e
  bound=$(count_status "$tsv" BOUND)
  open=$(count_status "$tsv" OPEN)
  spec=$(count_status "$tsv" SPEC)
  unsat=$(count_status "$tsv" UNSAT)
  fixture=$(count_status "$tsv" FIXTURE)
  echo "dogfood $repo  exit=$code  BOUND=$bound OPEN=$open SPEC=$spec UNSAT=$unsat FIXTURE=$fixture"
  if [[ "$code" -eq 0 ]]; then
    ok "dogfood $repo ran"
  else
    fail "dogfood $repo ran" "exit=$code $(head -c 200 /tmp/vow-dogfood-$$.err)"
  fi
  if [[ "$repo" == sitbone ]]; then
    if [[ "${bound:-0}" -eq 0 && "${unsat:-0}" -eq 0 ]]; then
      ok "sitbone has no BOUND/UNSAT (stays FIXTURE, not TAINTED)"
    else
      fail "sitbone has no BOUND/UNSAT" "BOUND=$bound UNSAT=$unsat"
    fi
    title="$DOGFOOD_ROOT/sitbone/Tests/SitboneCoreTests/WindowTitleParserTests.swift"
    if [[ -f "$title" ]]; then
      tu="$(req_of "$title" USER)"
      assert_eq "$tu" "" "sitbone WindowTitleParserTests USER empty"
      tst="$(status_of "$title")"
      if [[ "$tst" == "OPEN" || "$tst" == "FIXTURE" ]]; then
        ok "sitbone title status=$tst kind=fixture/open"
      else
        fail "sitbone title OPEN/FIXTURE" "$tst"
      fi
    fi
  fi
  if [[ "$repo" == kizu ]]; then
    if [[ "${unsat:-0}" -eq 0 ]]; then
      ok "kizu has no UNSAT (quoting both layouts is spec)"
    else
      fail "kizu has no UNSAT" "UNSAT=$unsat"
    fi
    init="$DOGFOOD_ROOT/kizu/src/init/tests.rs"
    if [[ -f "$init" ]]; then
      ih="$(req_of "$init" HOME)"
      assert_eq "$ih" "" "kizu init/tests.rs HOME empty"
      ist="$(status_of "$init")"
      if [[ "$ist" == "SPEC" || "$ist" == "OPEN" ]]; then
        ok "kizu init/tests.rs status=$ist (SPEC quoting, comments silent)"
      else
        fail "kizu init/tests.rs SPEC/OPEN" "$ist"
      fi
    fi
  fi
  rm -f "$tsv"
done
rm -f /tmp/vow-dogfood-$$.err

echo "======== 13. host role in the pair ========"
host_of() {
  "${VOW[@]}" --from-fail --json < "$1" | "$PY" -c 'import json,sys; print(json.load(sys.stdin).get("host",""))'
}
h="$(host_of "$FIX/pytest_fail.txt")"
if [[ "$home" == "/Users/alice" ]]; then
  assert_eq "$h" "EXPECTED" "alice host is EXPECTED on alice-vs-runner"
elif [[ "$home" == "/home/runner" ]]; then
  assert_eq "$h" "ACTUAL" "runner host is ACTUAL on alice-vs-runner"
else
  assert_eq "$h" "NEITHER" "this host is NEITHER on alice-vs-runner"
fi
printf 'E   - /tmp/x\nE   + %s/proj\n' "$home" > "$LIVE/live_actual.txt"
h="$(host_of "$LIVE/live_actual.txt")"
assert_eq "$h" "ACTUAL" "dump actual=\$HOME → host ACTUAL"
assert_eq "$(pair_of "$LIVE/live_actual.txt")" "EXPECTED-OPEN vs ACTUAL-BOUND" "live actual pair OPEN vs BOUND"
h="$(host_of "$FIX/xctest_fail.txt")"
if [[ "$home" == "/Users/alice" ]]; then
  assert_eq "$h" "ACTUAL" "xctest tmp-vs-alice: alice host is ACTUAL"
else
  assert_eq "$h" "NEITHER" "xctest tmp-vs-alice: this host is NEITHER"
fi

echo
echo "passed=$passed failed=$failed"
if [[ "$failed" -ne 0 ]]; then
  exit 1
fi
exit 0
