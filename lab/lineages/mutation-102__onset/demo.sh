#!/usr/bin/env bash
# Exercise onset. Exit 0 only if every case holds.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
chmod +x "$ROOT/onset"
PY="${PYTHON:-python3}"
ONSET=("$PY" "$ROOT/onset.py")
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
  "${ONSET[@]}" --json "$1" | "$PY" -c 'import json,sys; print(json.load(sys.stdin)["status"])'
}

field_of() {
  local file="$1" field="$2"
  "${ONSET[@]}" --json "$file" | "$PY" -c "import json,sys; print(json.load(sys.stdin).get('$field',''))"
}

echo "======== 1. self-test + unittest ========"
"${ONSET[@]}" --self-test
ok "onset --self-test"
"$PY" -m unittest discover -s tests -q
ok "unittest discover"

echo "======== 2. gold: comment vs expected vs actual ========"
assert_eq "$(status_of "$FIX/comment_only.py")" "OPEN" "comment # ran on alice is OPEN"
assert_eq "$(field_of "$FIX/comment_only.py" actual_bound)" "0" "comment is not actual-bound"
assert_eq "$(status_of "$FIX/env_assert.py")" "EXPECTED-BOUND" "assert USER==alice is EXPECTED-BOUND"
assert_eq "$(field_of "$FIX/env_assert.py" actual_bound)" "0" "env assert actual-bound=0"
assert_eq "$(status_of "$FIX/actual_literal.swift")" "ACTUAL-BOUND" "XCTAssertEqual alice path is ACTUAL-BOUND"

echo "======== 3. sitbone-shaped title is FIXTURE, not TAINTED ========"
assert_eq "$(status_of "$FIX/title.swift")" "FIXTURE" "title.swift FIXTURE"
assert_eq "$(field_of "$FIX/title.swift" actual_bound)" "0" "title not actual-bound"

echo "======== 4. kizu quoting is SPEC; nested call is not actual ========"
st="$(status_of "$FIX/payload.rs")"
if [[ "$st" == "SPEC" || "$st" == "OPEN" ]]; then
  ok "payload.rs $st (quoting is spec)"
else
  fail "payload.rs SPEC/OPEN" "$st"
fi
assert_eq "$(field_of "$FIX/payload.rs" actual_bound)" "0" "payload not actual-bound"
assert_eq "$(field_of "$FIX/nested.rs" actual_bound)" "0" "nested call arg not actual-bound"

echo "======== 5. fail dump: actual=/Users/alice expected=tmp ========"
assert_eq "$(status_of "$FIX/xctest_fail.txt")" "ACTUAL-BOUND" "xctest dump ACTUAL-BOUND"
code=0
"${ONSET[@]}" --from-fail < "$FIX/xctest_fail.txt" >/dev/null || code=$?
assert_exit "$code" 0 "from-fail dump with actual-bound exits 0"

echo "======== 6. synthetic git: first-actual ≠ first-assertion ========"
DEMO="$(mktemp -d "${TMPDIR:-/tmp}/onset-demo.XXXXXX")"
cleanup() { rm -rf "$DEMO"; }
trap cleanup EXIT

git -C "$DEMO" init -q -b main
git -C "$DEMO" config user.name "onset-demo"
git -C "$DEMO" config user.email "onset@lab"

mkdir -p "$DEMO/tests"
printf 'assert got == 1\n' > "$DEMO/tests/test_open.py"
git -C "$DEMO" add tests/test_open.py
git -C "$DEMO" commit -q -m "t0: assertion born OPEN"

printf '# ran on alice\nassert got == 1\n' > "$DEMO/tests/test_open.py"
git -C "$DEMO" add tests/test_open.py
git -C "$DEMO" commit -q -m "t1: comment is not an oath"

printf "assert os.environ['USER'] == 'alice'\n" > "$DEMO/tests/test_user.py"
git -C "$DEMO" add tests/test_user.py
git -C "$DEMO" commit -q -m "t2: EXPECTED-BOUND alice"

cp "$FIX/title.swift" "$DEMO/tests/test_title.swift"
git -C "$DEMO" add tests/test_title.swift
git -C "$DEMO" commit -q -m "t3: FIXTURE annenpolka title"

printf 'XCTAssertEqual("%s/Library", "/tmp/x")\n' "$HOME" > "$DEMO/tests/test_actual.swift"
git -C "$DEMO" add tests/test_actual.swift
git -C "$DEMO" commit -q -m "t4: ACTUAL-BOUND this host"

out="$("${ONSET[@]}" -C "$DEMO" --porcelain)"
echo "$out"
a_sha="$(printf '%s\n' "$out" | awk -F'\t' '$1=="first-assertion"{print $2}')"
x_sha="$(printf '%s\n' "$out" | awk -F'\t' '$1=="first-actual"{print $2}')"
e_sha="$(printf '%s\n' "$out" | awk -F'\t' '$1=="first-expected"{print $2}')"
f_sha="$(printf '%s\n' "$out" | awk -F'\t' '$1=="first-fixture"{print $2}')"
dist="$(printf '%s\n' "$out" | awk -F'\t' '$1=="distinct"{print $2}')"
assert_eq "$dist" "yes" "synthetic distinct yes"
if [[ -n "$a_sha" && -n "$x_sha" && "$a_sha" != "$x_sha" ]]; then
  ok "first-actual sha ≠ first-assertion sha"
else
  fail "first-actual sha ≠ first-assertion sha" "a=$a_sha x=$x_sha"
fi
if [[ -n "$e_sha" && "$e_sha" != "$a_sha" && "$e_sha" != "$x_sha" ]]; then
  ok "first-expected is a third commit"
else
  fail "first-expected is a third commit" "e=$e_sha a=$a_sha x=$x_sha"
fi
if [[ -n "$f_sha" && "$f_sha" != "$x_sha" ]]; then
  ok "first-fixture ≠ first-actual"
else
  fail "first-fixture ≠ first-actual" "f=$f_sha x=$x_sha"
fi

subj_a="$(git -C "$DEMO" log -1 --format=%s "$a_sha")"
subj_x="$(git -C "$DEMO" log -1 --format=%s "$x_sha")"
assert_eq "$subj_a" "t0: assertion born OPEN" "first-assertion is t0"
assert_eq "$subj_x" "t4: ACTUAL-BOUND this host" "first-actual is t4"

echo "======== 7. dogfood sitbone / kizu (read-only) ========"
SITBONE="${SITBONE:-/Users/annenpolka/ghq/github.com/annenpolka/sitbone}"
KIZU="${KIZU:-/Users/annenpolka/ghq/github.com/annenpolka/kizu}"

if [[ -d "$SITBONE/.git" ]]; then
  s_out="$("${ONSET[@]}" -C "$SITBONE" --porcelain)"
  echo "$s_out"
  s_dist="$(printf '%s\n' "$s_out" | awk -F'\t' '$1=="distinct"{print $2}')"
  s_act="$(printf '%s\n' "$s_out" | awk -F'\t' '$1=="first-actual"{print $2}')"
  s_as="$(printf '%s\n' "$s_out" | awk -F'\t' '$1=="first-assertion"{print $2}')"
  s_fx="$(printf '%s\n' "$s_out" | awk -F'\t' '$1=="first-fixture"{print $2}')"
  assert_eq "$s_dist" "yes" "sitbone distinct"
  if [[ -n "$s_as" ]]; then
    ok "sitbone has first-assertion"
  else
    fail "sitbone has first-assertion" "empty"
  fi
  if [[ -z "$s_act" ]]; then
    ok "sitbone first-actual is none (not TAINTED)"
  else
    fail "sitbone first-actual is none" "$s_act"
  fi
  if [[ -n "$s_fx" ]]; then
    ok "sitbone names FIXTURE birth"
  else
    fail "sitbone names FIXTURE birth" "empty"
  fi
  if [[ -n "$s_as" && -n "$s_fx" && "$s_as" != "$s_fx" ]]; then
    ok "sitbone first-fixture ≠ first-assertion"
  else
    fail "sitbone first-fixture ≠ first-assertion" "as=$s_as fx=$s_fx"
  fi
  s_human="$("${ONSET[@]}" -C "$SITBONE")"
  if printf '%s\n' "$s_human" | grep -q 'rerun with --full'; then
    ok "sitbone first-parent hints --full"
  else
    fail "sitbone first-parent hints --full" "$s_human"
  fi
  s_full="$("${ONSET[@]}" -C "$SITBONE" --full --porcelain)"
  echo "$s_full"
  s_fx_path="$(printf '%s\n' "$s_full" | awk -F'\t' '$1=="first-fixture"{print $3}')"
  if [[ "$s_fx_path" == *WindowTitleParserTests* ]]; then
    ok "sitbone --full fixture is WindowTitleParserTests"
  else
    fail "sitbone --full fixture is WindowTitleParserTests" "$s_fx_path"
  fi
else
  fail "sitbone repo" "missing $SITBONE"
fi

if [[ -d "$KIZU/.git" ]]; then
  k_out="$("${ONSET[@]}" -C "$KIZU" --porcelain)"
  echo "$k_out"
  k_dist="$(printf '%s\n' "$k_out" | awk -F'\t' '$1=="distinct"{print $2}')"
  k_act="$(printf '%s\n' "$k_out" | awk -F'\t' '$1=="first-actual"{print $2}')"
  k_as="$(printf '%s\n' "$k_out" | awk -F'\t' '$1=="first-assertion"{print $2}')"
  assert_eq "$k_dist" "yes" "kizu distinct"
  if [[ -n "$k_as" ]]; then
    ok "kizu has first-assertion"
  else
    fail "kizu has first-assertion" "empty"
  fi
  if [[ -z "$k_act" ]]; then
    ok "kizu first-actual is none (John Doe /home/user are not ACTUAL-BOUND)"
  else
    fail "kizu first-actual is none" "$k_act"
  fi
  k_spec="$(printf '%s\n' "$k_out" | awk -F'\t' '$1=="first-spec"{print $2}')"
  if [[ -n "$k_spec" ]]; then
    ok "kizu names first-spec (quoting, not ACTUAL-BOUND)"
  else
    fail "kizu names first-spec" "empty"
  fi
  k_human="$("${ONSET[@]}" -C "$KIZU")"
  if printf '%s\n' "$k_human" | grep -q 'rerun with --full'; then
    ok "kizu first-parent hints --full"
  else
    fail "kizu first-parent hints --full" "$k_human"
  fi
  k_full="$("${ONSET[@]}" -C "$KIZU" --full --porcelain)"
  echo "$k_full"
  k_as_path="$(printf '%s\n' "$k_full" | awk -F'\t' '$1=="first-assertion"{print $3}')"
  if [[ "$k_as_path" == *src/git.rs* ]]; then
    ok "kizu --full first-assertion is src/git.rs"
  else
    fail "kizu --full first-assertion is src/git.rs" "$k_as_path"
  fi
else
  fail "kizu repo" "missing $KIZU"
fi

echo
echo "passed=$passed failed=$failed"
if [[ "$failed" -ne 0 ]]; then
  exit 1
fi
exit 0
