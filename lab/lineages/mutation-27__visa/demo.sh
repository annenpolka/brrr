#!/usr/bin/env bash
# Exercise visa. Exit 0 only if every case holds.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
chmod +x "$ROOT/visa"
PY="${PYTHON:-python3}"
VISA=("$PY" "$ROOT/visa.py")
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
  "${VISA[@]}" --json "$1" | "$PY" -c 'import json,sys; print(json.load(sys.stdin)["status"])'
}

req_of() {
  local file="$1" axis="$2"
  "${VISA[@]}" --json "$file" | "$PY" -c "import json,sys; print(json.load(sys.stdin)['require'].get('$axis',''))"
}

echo "======== 1. self-test + unittest ========"
"${VISA[@]}" --self-test
ok "visa --self-test"
"$PY" -m unittest discover -s tests -q
ok "unittest discover"

echo "======== 2. unary visa of snapshots ========"
assert_eq "$(status_of "$FIX/local.snap")" "BOUND" "local.snap BOUND"
assert_eq "$(req_of "$FIX/local.snap" HOME)" "/Users/alice" "local HOME=/Users/alice"
assert_eq "$(req_of "$FIX/local.snap" platform)" "Darwin" "local platform=Darwin"
assert_eq "$(status_of "$FIX/ci.snap")" "BOUND" "ci.snap BOUND"
assert_eq "$(req_of "$FIX/ci.snap" CI)" "github-actions" "ci CI=github-actions"
assert_eq "$(status_of "$FIX/spec_only.snap")" "OPEN" "spec_only OPEN"
assert_eq "$(status_of "$FIX/conflict.snap")" "UNSAT" "conflict UNSAT"
assert_eq "$(status_of "$FIX/title.swift")" "OPEN" "github title OPEN (no live-dict USER stain)"

tmp_status="$(status_of "$FIX/tmp_only.rs")"
if [[ "$tmp_status" == "OPEN" || "$tmp_status" == "SPEC" ]]; then
  ok "tmp_only not BOUND ($tmp_status)"
else
  fail "tmp_only not BOUND" "$tmp_status"
fi

# v0.2: two layouts in source are quoting/path-parser spec, not a skip.
assert_eq "$(status_of "$FIX/payload.rs")" "SPEC" "payload.rs two layouts SPEC (not a machine visa)"

echo "======== 3. emit + apply ========"
pred="$("${VISA[@]}" --emit shell "$FIX/local.snap")"
if [[ "$pred" == *"Darwin"* && "$pred" == *"/Users/alice"* ]]; then
  ok "emit shell is Darwin ∧ HOME=alice"
else
  fail "emit shell is Darwin ∧ HOME=alice" "$pred"
fi
gha="$("${VISA[@]}" --emit gha "$FIX/local.snap")"
assert_eq "$gha" "macos-latest" "emit gha macos-latest"
gha="$("${VISA[@]}" --emit gha "$FIX/ci.snap")"
assert_eq "$gha" "ubuntu-latest" "emit gha ubuntu-latest"

code=0
"${VISA[@]}" --apply "$FIX/spec_only.snap" >/dev/null || code=$?
assert_exit "$code" 0 "OPEN --apply 0"

code=0
"${VISA[@]}" --apply "$FIX/conflict.snap" >/dev/null || code=$?
assert_exit "$code" 2 "UNSAT --apply 2"

code=0
"${VISA[@]}" --apply "$FIX/local.snap" >/dev/null || code=$?
home="$("$PY" -c 'from pathlib import Path; print(Path.home())')"
if [[ "$home" == "/Users/alice" ]]; then
  assert_exit "$code" 0 "alice snap MATCH on alice host"
else
  assert_exit "$code" 1 "alice snap MISS on this host ($home)"
fi

echo "======== 4. live machine snap MATCH ========"
LIVE="$ROOT/demo-tmp"
rm -rf "$LIVE"
mkdir -p "$LIVE"
user="$("$PY" -c 'import getpass; print(getpass.getuser())')"
printf 'spec:ok\nhome:%s\nuser:%s\ntimeout:30\n' "$home" "$user" > "$LIVE/live.snap"
printf 'spec:ok\ntimeout:30\n' > "$LIVE/portable.snap"
code=0
"${VISA[@]}" --apply --match "$LIVE/live.snap" >/dev/null || code=$?
assert_exit "$code" 0 "live snap MATCH --apply 0"
code=0
"${VISA[@]}" --apply "$LIVE/portable.snap" >/dev/null || code=$?
assert_exit "$code" 0 "portable snap OPEN --apply 0"
st="$(status_of "$LIVE/live.snap")"
assert_eq "$st" "BOUND" "live snap BOUND to this host"

echo "======== 5. ugly paths ========"
st="$(status_of "$FIX/ugly/dir with spaces/snap.txt")"
assert_eq "$st" "BOUND" "space path snap BOUND"
st="$(status_of "$FIX/ugly/日本語/期待.txt")"
assert_eq "$st" "BOUND" "unicode path snap BOUND"

echo "======== 6. --from-fail visas the expected side ========"
plat="$("${VISA[@]}" --from-fail --json < "$FIX/pytest_fail.txt" | "$PY" -c 'import json,sys; print(json.load(sys.stdin)["files"][0]["require"].get("platform",""))')"
assert_eq "$plat" "Darwin" "pytest expected is Darwin visa"

echo "======== 7. dogfood kizu / sitbone ========"
DOGFOOD_ROOT="${DOGFOOD_ROOT:-/Users/annenpolka/ghq/github.com/annenpolka}"
count_status() {
  local tsv="$1" st="$2"
  grep -c $'^status\t'"$st" "$tsv" 2>/dev/null || true
}
for repo in kizu sitbone; do
  dir="$DOGFOOD_ROOT/$repo"
  if [[ ! -d "$dir" ]]; then
    echo "skip  dogfood $repo (missing)"
    continue
  fi
  tsv="/tmp/visa-dogfood-$$-$repo.tsv"
  set +e
  "${VISA[@]}" --scan --porcelain -C "$dir" >"$tsv" 2>/tmp/visa-dogfood-$$.err
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
    fail "dogfood $repo ran" "exit=$code $(head -c 200 /tmp/visa-dogfood-$$.err)"
  fi
  if [[ "$repo" == sitbone ]]; then
    # Flip vs lees: we do not stain live USER, so GitHub titles are not a USER visa.
    if [[ "${bound:-0}" -eq 0 && "${unsat:-0}" -eq 0 ]]; then
      ok "sitbone has no BOUND/UNSAT machine visa"
    else
      fail "sitbone has no BOUND/UNSAT machine visa" "BOUND=$bound UNSAT=$unsat"
    fi
  fi
  if [[ "$repo" == kizu ]]; then
    # v0.2: textbook /home/user and /Users/John Doe are SPEC payload.
    if [[ "${bound:-0}" -eq 0 && "${unsat:-0}" -eq 0 && "${spec:-0}" -ge 1 ]]; then
      ok "kizu textbook paths are SPEC not BOUND/UNSAT (SPEC=$spec)"
    else
      fail "kizu textbook paths are SPEC not BOUND/UNSAT" "BOUND=$bound UNSAT=$unsat SPEC=$spec"
    fi
  fi
  rm -f "$tsv"
done
rm -f /tmp/visa-dogfood-$$.err

echo
echo "passed=$passed failed=$failed"
if [[ "$failed" -ne 0 ]]; then
  exit 1
fi
exit 0
