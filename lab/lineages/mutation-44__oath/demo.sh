#!/usr/bin/env bash
# Exercise oath. Exit 0 only if every case holds.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
chmod +x "$ROOT/oath"
PY="${PYTHON:-python3}"
OATH=("$PY" "$ROOT/oath.py")
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
  "${OATH[@]}" --json "$1" | "$PY" -c 'import json,sys; print(json.load(sys.stdin)["status"])'
}

req_of() {
  local file="$1" axis="$2"
  "${OATH[@]}" --json "$file" | "$PY" -c "import json,sys; print(json.load(sys.stdin)['require'].get('$axis',''))"
}

echo "======== 1. self-test + unittest ========"
"${OATH[@]}" --self-test
ok "oath --self-test"
"$PY" -m unittest discover -s tests -q
ok "unittest discover"

echo "======== 2. gold: comment vs assert ========"
assert_eq "$(status_of "$FIX/comment_only.py")" "OPEN" "comment # ran on alice is OPEN"
assert_eq "$(req_of "$FIX/comment_only.py" USER)" "" "comment does not require USER"
assert_eq "$(status_of "$FIX/env_assert.py")" "BOUND" "assert environ USER == alice is BOUND"
assert_eq "$(req_of "$FIX/env_assert.py" USER)" "alice" "env assert USER=alice"
assert_eq "$(status_of "$FIX/comment.snap")" "OPEN" "snap comment is OPEN"

echo "======== 3. unary oath of snapshots ========"
assert_eq "$(status_of "$FIX/local.snap")" "BOUND" "local.snap BOUND"
assert_eq "$(req_of "$FIX/local.snap" HOME)" "/Users/alice" "local HOME=/Users/alice"
assert_eq "$(req_of "$FIX/local.snap" platform)" "Darwin" "local platform=Darwin"
assert_eq "$(status_of "$FIX/ci.snap")" "BOUND" "ci.snap BOUND"
assert_eq "$(req_of "$FIX/ci.snap" CI)" "github-actions" "ci CI=github-actions"
assert_eq "$(status_of "$FIX/spec_only.snap")" "OPEN" "spec_only OPEN"
assert_eq "$(status_of "$FIX/conflict.snap")" "UNSAT" "conflict UNSAT"

# lees --par local vs ci is MACHINE / empty residue.
# oath is unary: two machines, not a substitution.
echo "======== 4. lees --par gold as two oaths ========"
assert_eq "$(req_of "$FIX/local.snap" HOME)" "/Users/alice" "par-left HOME alice"
assert_eq "$(req_of "$FIX/ci.snap" HOME)" "/home/runner" "par-right HOME runner"

echo "======== 5. sitbone-shaped title is fixture ========"
st="$(status_of "$FIX/title.swift")"
if [[ "$st" == "OPEN" || "$st" == "FIXTURE" ]]; then
  ok "title.swift $st (not BOUND)"
else
  fail "title.swift OPEN/FIXTURE" "$st"
fi
assert_eq "$(req_of "$FIX/title.swift" USER)" "" "title does not require USER"

echo "======== 6. emit + apply ========"
pred="$("${OATH[@]}" --emit shell "$FIX/local.snap")"
if [[ "$pred" == *"Darwin"* && "$pred" == *"/Users/alice"* ]]; then
  ok "emit shell is Darwin ∧ HOME=alice"
else
  fail "emit shell is Darwin ∧ HOME=alice" "$pred"
fi
gha="$("${OATH[@]}" --emit gha "$FIX/local.snap")"
assert_eq "$gha" "macos-latest" "emit gha macos-latest"
gha="$("${OATH[@]}" --emit gha "$FIX/ci.snap")"
assert_eq "$gha" "ubuntu-latest" "emit gha ubuntu-latest"

code=0
"${OATH[@]}" --apply "$FIX/spec_only.snap" >/dev/null || code=$?
assert_exit "$code" 0 "OPEN --apply 0"

code=0
"${OATH[@]}" --apply "$FIX/conflict.snap" >/dev/null || code=$?
assert_exit "$code" 2 "UNSAT --apply 2"

code=0
"${OATH[@]}" --apply "$FIX/local.snap" >/dev/null || code=$?
home="$("$PY" -c 'from pathlib import Path; print(Path.home())')"
if [[ "$home" == "/Users/alice" ]]; then
  assert_exit "$code" 0 "alice snap MATCH on alice host"
else
  assert_exit "$code" 1 "alice snap MISS on this host ($home)"
fi

echo "======== 7. live machine snap MATCH ========"
LIVE="$ROOT/demo-tmp"
rm -rf "$LIVE"
mkdir -p "$LIVE"
user="$("$PY" -c 'import getpass; print(getpass.getuser())')"
printf 'spec:ok\nhome:%s\nuser:%s\ntimeout:30\n' "$home" "$user" > "$LIVE/live.snap"
printf 'spec:ok\ntimeout:30\n' > "$LIVE/portable.snap"
code=0
"${OATH[@]}" --apply --match "$LIVE/live.snap" >/dev/null || code=$?
assert_exit "$code" 0 "live snap MATCH --apply 0"
code=0
"${OATH[@]}" --apply "$LIVE/portable.snap" >/dev/null || code=$?
assert_exit "$code" 0 "portable snap OPEN --apply 0"
st="$(status_of "$LIVE/live.snap")"
assert_eq "$st" "BOUND" "live snap BOUND to this host"

echo "======== 8. ugly paths ========"
st="$(status_of "$FIX/ugly/dir with spaces/snap.txt")"
assert_eq "$st" "BOUND" "space path snap BOUND"
st="$(status_of "$FIX/ugly/日本語/期待.txt")"
assert_eq "$st" "BOUND" "unicode path snap BOUND"

echo "======== 9. --from-fail more grammars ========"
plat="$("${OATH[@]}" --from-fail --json < "$FIX/pytest_fail.txt" | "$PY" -c 'import json,sys; print(json.load(sys.stdin)["files"][0]["require"].get("platform",""))')"
assert_eq "$plat" "Darwin" "pytest expected is Darwin oath"

plat="$("${OATH[@]}" --from-fail --json < "$FIX/cargo_fail.txt" | "$PY" -c 'import json,sys; print(json.load(sys.stdin)["files"][0]["require"].get("platform",""))')"
assert_eq "$plat" "Darwin" "cargo expected is Darwin oath"

home_j="$("${OATH[@]}" --from-fail --json < "$FIX/jest_fail.txt" | "$PY" -c 'import json,sys; print(next(f["require"].get("HOME","") for f in json.load(sys.stdin)["files"] if f["require"].get("HOME")))')"
assert_eq "$home_j" "/Users/alice" "jest expected HOME=alice"

home_g="$("${OATH[@]}" --from-fail --json < "$FIX/go_fail.txt" | "$PY" -c 'import json,sys; print(next(f["require"].get("HOME","") for f in json.load(sys.stdin)["files"] if f["require"].get("HOME")))')"
assert_eq "$home_g" "/Users/alice" "go expected HOME=alice"

home_u="$("${OATH[@]}" --from-fail --json < "$FIX/junit_fail.txt" | "$PY" -c 'import json,sys; print(next(f["require"].get("HOME","") for f in json.load(sys.stdin)["files"] if f["require"].get("HOME")))')"
assert_eq "$home_u" "/Users/alice" "junit expected HOME=alice"

echo "======== 10. dogfood sitbone / kizu / voidtrace / tenaoshi ========"
DOGFOOD_ROOT="${DOGFOOD_ROOT:-/Users/annenpolka/ghq/github.com/annenpolka}"
count_status() {
  local tsv="$1" st="$2"
  grep -c $'^status\t'"$st" "$tsv" 2>/dev/null || true
}
for repo in sitbone kizu voidtrace tenaoshi; do
  dir="$DOGFOOD_ROOT/$repo"
  if [[ ! -d "$dir" ]]; then
    echo "skip  dogfood $repo (missing)"
    continue
  fi
  tsv="/tmp/oath-dogfood-$$-$repo.tsv"
  set +e
  "${OATH[@]}" --scan --porcelain -C "$dir" >"$tsv" 2>/tmp/oath-dogfood-$$.err
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
    fail "dogfood $repo ran" "exit=$code $(head -c 200 /tmp/oath-dogfood-$$.err)"
  fi
  if [[ "$repo" == sitbone ]]; then
    # Gold: annenpolka in a window-title fixture is not a USER oath.
    if [[ "${bound:-0}" -eq 0 && "${unsat:-0}" -eq 0 ]]; then
      ok "sitbone has no BOUND/UNSAT machine oath"
    else
      fail "sitbone has no BOUND/UNSAT machine oath" "BOUND=$bound UNSAT=$unsat"
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
    # Comments about /Users/John Doe and textbook /home/user are not BOUND.
    if [[ "${unsat:-0}" -eq 0 ]]; then
      ok "kizu has no UNSAT (quoting both layouts is spec)"
    else
      fail "kizu has no UNSAT" "UNSAT=$unsat"
    fi
  fi
  rm -f "$tsv"
done
rm -f /tmp/oath-dogfood-$$.err

echo
echo "passed=$passed failed=$failed"
if [[ "$failed" -ne 0 ]]; then
  exit 1
fi
exit 0
