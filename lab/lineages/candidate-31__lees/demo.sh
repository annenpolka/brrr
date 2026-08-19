#!/usr/bin/env bash
# Exercise lees. Exit 0 only if every case holds.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
chmod +x "$ROOT/lees"
PY="${PYTHON:-python3}"
LEES=("$PY" "$ROOT/lees.py")
FIX="$ROOT/fixtures"
FACTS=(--clean-dict --dict-json "$FIX/facts.json")
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

echo "======== 1. self-test + unittest ========"
"${LEES[@]}" --self-test
ok "lees --self-test"
"$PY" -m unittest discover -s tests -q
ok "unittest discover"

echo "======== 2. stain fixture dict ========"
json="$("${LEES[@]}" "${FACTS[@]}" --json --check "$FIX/local.snap" || true)"
status="$(printf '%s' "$json" | "$PY" -c 'import json,sys; print(json.load(sys.stdin)["files"][0]["status"])')"
assert_eq "$status" "TAINTED" "local.snap TAINTED under alice dict"

code=0
"${LEES[@]}" "${FACTS[@]}" --check "$FIX/spec_only.snap" >/dev/null || code=$?
assert_exit "$code" 0 "spec_only.snap CLEAN --check"

echo "======== 3. holes ========"
holed="$("${LEES[@]}" "${FACTS[@]}" --holes "$FIX/local.snap")"
if [[ "$holed" != *"/Users/alice"* && "$holed" == *"{HOME}"* && "$holed" == *"timeout: 30"* ]]; then
  ok "holes hide HOME keep spec"
else
  fail "holes hide HOME keep spec" "$holed"
fi

echo "======== 4. --par local vs CI ========"
verdict="$("${LEES[@]}" "${FACTS[@]}" --json --check --par "$FIX/local.snap" "$FIX/ci.snap" | "$PY" -c 'import json,sys; print(json.load(sys.stdin)["verdict"])')"
assert_eq "$verdict" "MACHINE" "par local/ci MACHINE"

code=0
"${LEES[@]}" "${FACTS[@]}" --json --check --par "$FIX/local.snap" "$FIX/mixed.snap" >/dev/null || code=$?
assert_exit "$code" 1 "par local/mixed fails --check"

verdict="$("${LEES[@]}" "${FACTS[@]}" --json --par "$FIX/spec_only.snap" "$FIX/spec_only_60.snap" | "$PY" -c 'import json,sys; print(json.load(sys.stdin)["verdict"])')"
assert_eq "$verdict" "SPEC" "par 30 vs 60 SPEC"

echo "======== 5. --from-fail ========"
verdict="$("${LEES[@]}" "${FACTS[@]}" --from-fail --json --check < "$FIX/pytest_fail.txt" | "$PY" -c 'import json,sys; d=json.load(sys.stdin); print(d["pairs"][0]["verdict"])')"
assert_eq "$verdict" "MACHINE" "pytest fail is MACHINE"

verdict="$("${LEES[@]}" "${FACTS[@]}" --from-fail --json < "$FIX/cargo_fail.txt" | "$PY" -c 'import json,sys; print(json.load(sys.stdin)["pairs"][0]["verdict"])')"
assert_eq "$verdict" "MACHINE" "cargo fail is MACHINE"

code=0
"${LEES[@]}" "${FACTS[@]}" --from-fail --json --check < "$FIX/spec_fail.txt" >/dev/null || code=$?
assert_exit "$code" 1 "spec fail --check 1"

echo "======== 6. --probe ========"
verdict="$("${LEES[@]}" --probe --json -- "$PY" "$FIX/echo_world.py" | "$PY" -c 'import json,sys; print(json.load(sys.stdin)["verdict"])')"
assert_eq "$verdict" "ENV-TIED" "echo_world ENV-TIED"

verdict="$("${LEES[@]}" --probe --json -- "$PY" "$FIX/echo_spec.py" | "$PY" -c 'import json,sys; print(json.load(sys.stdin)["verdict"])')"
assert_eq "$verdict" "STABLE" "echo_spec STABLE"

echo "======== 7. ugly paths ========"
n="$("${LEES[@]}" "${FACTS[@]}" --json "$FIX/ugly/dir with spaces/snap.txt" | "$PY" -c 'import json,sys; print(len(json.load(sys.stdin)["files"][0]["hits"]))')"
if [[ "$n" -ge 1 ]]; then
  ok "ugly space path stained"
else
  fail "ugly space path stained" "hits=$n"
fi
n="$("${LEES[@]}" "${FACTS[@]}" --json "$FIX/ugly/日本語/期待.txt" | "$PY" -c 'import json,sys; print(len(json.load(sys.stdin)["files"][0]["hits"]))')"
if [[ "$n" -ge 1 ]]; then
  ok "ugly unicode path stained"
else
  fail "ugly unicode path stained" "hits=$n"
fi

echo "======== 8. live machine snap ========"
LIVE="$ROOT/demo-tmp"
rm -rf "$LIVE"
mkdir -p "$LIVE"
home="$("$PY" -c 'from pathlib import Path; print(Path.home())')"
user="$("$PY" -c 'import getpass; print(getpass.getuser())')"
printf 'spec:ok\nhome:%s\nuser:%s\ntimeout:30\n' "$home" "$user" > "$LIVE/live.snap"
printf 'spec:ok\ntimeout:30\n' > "$LIVE/portable.snap"
code=0
"${LEES[@]}" --check "$LIVE/live.snap" >/dev/null || code=$?
assert_exit "$code" 1 "live snap TAINTED on this host"
code=0
"${LEES[@]}" --check "$LIVE/portable.snap" >/dev/null || code=$?
assert_exit "$code" 0 "portable snap CLEAN on this host"

echo "======== 9. dogfood --scan --check ========"
DOGFOOD_ROOT="${DOGFOOD_ROOT:-/Users/annenpolka/ghq/github.com/annenpolka}"
for repo in kizu sitbone voidtrace tenaoshi; do
  dir="$DOGFOOD_ROOT/$repo"
  if [[ ! -d "$dir" ]]; then
    echo "skip  dogfood $repo (missing)"
    continue
  fi
  set +e
  "${LEES[@]}" --scan --check --porcelain -C "$dir" >/tmp/lees-dogfood-$$.tsv 2>/tmp/lees-dogfood-$$.err
  code=$?
  set -e
  tainted=$(grep -c $'^status\tTAINTED' /tmp/lees-dogfood-$$.tsv 2>/dev/null || true)
  clean=$(grep -c $'^status\tCLEAN' /tmp/lees-dogfood-$$.tsv 2>/dev/null || true)
  echo "dogfood $repo  exit=$code  tainted=${tainted:-0}  clean=${clean:-0}"
  if [[ "$code" -eq 0 || "$code" -eq 1 ]]; then
    ok "dogfood $repo ran"
  else
    fail "dogfood $repo ran" "exit=$code $(head -c 200 /tmp/lees-dogfood-$$.err)"
  fi
done
# sitbone v1 flagged USER inside github.com/annenpolka/... titles. After the
# fixture rule those are CLEAN — the tests are *about* that identity.
if [[ -d "$DOGFOOD_ROOT/sitbone" ]]; then
  set +e
  "${LEES[@]}" --scan --check -C "$DOGFOOD_ROOT/sitbone" >/dev/null 2>&1
  code=$?
  set -e
  assert_exit "$code" 0 "sitbone --check CLEAN after fixture rule"
fi
# kizu tests lock /home/user as a path oracle; --foreign must see them,
# --check must not fail (they are not this host).
if [[ -d "$DOGFOOD_ROOT/kizu" ]]; then
  n="$("${LEES[@]}" --scan --foreign --json -C "$DOGFOOD_ROOT/kizu" | "$PY" -c 'import json,sys; d=json.load(sys.stdin); print(sum(1 for f in d["files"] for h in f["hits"] if h["kind"]=="path"))')"
  if [[ "$n" -ge 1 ]]; then
    ok "kizu --foreign sees /home/user path oracles ($n)"
  else
    fail "kizu --foreign sees /home/user path oracles" "n=$n"
  fi
fi
rm -f /tmp/lees-dogfood-$$.tsv /tmp/lees-dogfood-$$.err

echo "======== 10. dump-dict ========"
n="$("${LEES[@]}" --dump-dict --json | "$PY" -c 'import json,sys; print(len(json.load(sys.stdin)))')"
if [[ "$n" -ge 3 ]]; then
  ok "dump-dict $n facts"
else
  fail "dump-dict" "n=$n"
fi

echo
echo "passed=$passed failed=$failed"
if [[ "$failed" -ne 0 ]]; then
  exit 1
fi
exit 0
