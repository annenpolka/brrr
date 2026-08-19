#!/usr/bin/env bash
# Exercise binom: leftover FILE:LINE in, falsifying commit of *that package* out.
# Homonym version is not the falsifier. Ash answers regenerate.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
BINOM="$ROOT/binom"
RUN="$ROOT/fixtures/.run"
rm -rf "$RUN"
mkdir -p "$RUN"

pass=0
fail=0
assert_contains() {
  local haystack="$1"
  local needle="$2"
  local label="$3"
  if grep -Fq -- "$needle" <<<"$haystack"; then
    echo "  ok  $label"
    pass=$((pass + 1))
  else
    echo "  FAIL $label"
    echo "    missing: $needle"
    echo "    --- output ---"
    echo "$haystack" | sed 's/^/    /'
    fail=$((fail + 1))
  fi
}

assert_not_contains() {
  local haystack="$1"
  local needle="$2"
  local label="$3"
  if grep -Fq -- "$needle" <<<"$haystack"; then
    echo "  FAIL $label"
    echo "    unexpectedly found: $needle"
    echo "    --- output ---"
    echo "$haystack" | sed 's/^/    /'
    fail=$((fail + 1))
  else
    echo "  ok  $label"
    pass=$((pass + 1))
  fi
}

assert_exit() {
  local got="$1"
  local want="$2"
  local label="$3"
  if [[ "$got" == "$want" ]]; then
    echo "  ok  $label (exit $got)"
    pass=$((pass + 1))
  else
    echo "  FAIL $label (exit $got, want $want)"
    fail=$((fail + 1))
  fi
}

git_init() {
  local repo="$1"
  git -C "$repo" init -q
  git -C "$repo" config user.email "binom@example.test"
  git -C "$repo" config user.name "binom"
}

echo "== self-test =="
set +e
"$BINOM" self-test
st=$?
set -e
assert_exit "$st" 0 "embedded parser/scorer/package-identity tests"

echo
echo "== toy: same-package leftover still names the falsifier =="
TOY="$RUN/toy"
mkdir -p "$TOY/src" "$TOY/tests" "$TOY/docs"
cp "$ROOT/fixtures/toy/src/retry.py" "$TOY/src/"
cp "$ROOT/fixtures/toy/README.md" "$TOY/"
cp "$ROOT/fixtures/toy/tests/test_retry.py" "$TOY/tests/" 2>/dev/null || printf 'assert MAX_RETRIES == 3\n' > "$TOY/tests/test_retry.py"
cp "$ROOT/fixtures/toy/docs/help.txt" "$TOY/docs/" 2>/dev/null || printf 'timeout default is 10\n' > "$TOY/docs/help.txt"
cp "$ROOT/fixtures/toy/plugin.json" "$TOY/"
git_init "$TOY"
git -C "$TOY" add .
git -C "$TOY" commit -qm "initial facts: retries=3 timeout=10 cache=true version=0.3.0"

python3 - <<'PY' "$TOY/src/retry.py" "$TOY/plugin.json"
from pathlib import Path
import sys
retry = Path(sys.argv[1])
text = retry.read_text()
text = text.replace("MAX_RETRIES = 3", "MAX_ATTEMPTS = 8")
text = text.replace("retries=MAX_RETRIES", "retries=MAX_ATTEMPTS")
text = text.replace("HOOK_TIMEOUT = 10", "HOOK_TIMEOUT = 30")
text = text.replace("ENABLE_CACHE = True", "ENABLE_CACHE = False")
retry.write_text(text)
Path(sys.argv[2]).write_text(Path(sys.argv[2]).read_text().replace('"version": "0.3.0"', '"version": "0.7.0"'))
PY

git -C "$TOY" add src/retry.py plugin.json
git -C "$TOY" commit -qm "change facts, forget the claims"

set +e
COMMITTED="$("$BINOM" --no-color --explain --no-hunk -C "$TOY" README.md:7 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "same-package prose leftover is found"
assert_contains "$COMMITTED" "change facts, forget the claims" "names the falsifying commit"
assert_contains "$COMMITTED" "plugin.json" "JSON quoted version is the origin"
assert_contains "$COMMITTED" "0.3.0" "old token"
assert_contains "$COMMITTED" "package plugin:toy" "fact is scoped to the plugin package"
assert_contains "$COMMITTED" "10 → 30" "same prose line also leftover-claims timeout 10"

set +e
HELP="$("$BINOM" --no-color --no-hunk -C "$TOY" docs/help.txt:2 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "timeout leftover is found"
assert_contains "$HELP" "10 → 30" "timeout 10→30"

echo
echo "== workspace: two packages named version are not one noun =="
WS="$RUN/workspace"
mkdir -p "$WS/pkg_a" "$WS/pkg_b"
cat > "$WS/pkg_a/Cargo.toml" <<'EOF'
[package]
name = "pkg_a"
version = "0.3.0"
EOF
cat > "$WS/pkg_b/Cargo.toml" <<'EOF'
[package]
name = "pkg_b"
version = "0.3.0"
EOF
printf 'pkg_a version 0.3.0\n' > "$WS/pkg_a/README.md"
printf 'pkg_b version 0.3.0\n' > "$WS/pkg_b/README.md"
printf 'pkg_b version 0.3.0 still ships with pkg_a.\n' > "$WS/README.md"
git_init "$WS"
git -C "$WS" add .
git -C "$WS" commit -qm "both packages 0.3.0"
python3 - <<'PY' "$WS/pkg_a/Cargo.toml"
from pathlib import Path
import sys
Path(sys.argv[1]).write_text(Path(sys.argv[1]).read_text().replace('version = "0.3.0"', 'version = "0.7.0"'))
PY
git -C "$WS" add pkg_a/Cargo.toml
git -C "$WS" commit -qm "bump pkg_a only to 0.7.0"

set +e
WS_B_TOML="$("$BINOM" --no-color --explain --no-hunk -C "$WS" pkg_b/Cargo.toml:3 2>&1)"
st=$?
set -e
assert_exit "$st" 1 "pkg_b Cargo.toml is not leftover of pkg_a"
assert_contains "$WS_B_TOML" "none" "pkg_b binding reports none"
assert_contains "$WS_B_TOML" "package cargo:pkg_b" "dest is scoped to pkg_b"
assert_not_contains "$WS_B_TOML" "FALSIFIED" "homonym version is not the falsifier"
assert_contains "$WS_B_TOML" "homonym" "rejected pkg_a bump is printed as homonym"
assert_contains "$WS_B_TOML" "cargo:pkg_a" "homonym names pkg_a"
assert_contains "$WS_B_TOML" "is not this package" "homonym is not the falsifier"

set +e
WS_B_DOC="$("$BINOM" --no-color --explain --no-hunk -C "$WS" pkg_b/README.md:1 2>&1)"
st=$?
set -e
assert_exit "$st" 1 "pkg_b README is not leftover of pkg_a"
assert_contains "$WS_B_DOC" "none" "pkg_b docs report none"
assert_not_contains "$WS_B_DOC" "FALSIFIED" "pkg_b prose does not name pkg_a bump"

set +e
WS_ROOT="$("$BINOM" --no-color --explain --no-hunk -C "$WS" README.md:1 2>&1)"
st=$?
set -e
assert_exit "$st" 1 "root README naming pkg_b is not leftover of pkg_a"
assert_not_contains "$WS_ROOT" "FALSIFIED" "dest-line package name binds pkg_b"

set +e
WS_A="$("$BINOM" --no-color --explain --no-hunk -C "$WS" pkg_a/README.md:1 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "pkg_a README leftover of pkg_a is found"
assert_contains "$WS_A" "FALSIFIED" "pkg_a leftover names a commit"
assert_contains "$WS_A" "0.3.0 → 0.7.0" "pkg_a version moved"
assert_contains "$WS_A" "pkg_a/Cargo.toml" "origin is pkg_a, not pkg_b"
assert_contains "$WS_A" "package cargo:pkg_a" "fact package is pkg_a"

echo
echo "== leftover-name is not a fact (string kind opt-in) =="
HUNGRY="$RUN/hungry"
mkdir -p "$HUNGRY/docs" "$HUNGRY/tests/e2e" "$HUNGRY/src"
printf 'HOOK_TIMEOUT = 10\n' > "$HUNGRY/src/config.py"
printf '{ "command": "toy hook-post-tool", "timeout": 10 }\n' > "$HUNGRY/docs/hooks.md"
printf 'expect("toy hook-post-tool")\n' > "$HUNGRY/tests/e2e/init.test.ts"
git_init "$HUNGRY"
git -C "$HUNGRY" add .
git -C "$HUNGRY" commit -qm "timeout 10 and command quote"
printf 'expect("toy'\'' hook-post-tool")\n' > "$HUNGRY/tests/e2e/init.test.ts"
git -C "$HUNGRY" add tests/e2e/init.test.ts
git -C "$HUNGRY" commit -qm "tweak quote in test string"

set +e
HUNGRY_OUT="$("$BINOM" --no-color --no-hunk -C "$HUNGRY" docs/hooks.md:1 2>&1)"
st=$?
set -e
assert_exit "$st" 1 "dest quote leftover-name is none (timeout still 10)"
assert_contains "$HUNGRY_OUT" "none" "hungry dest reports none"
assert_not_contains "$HUNGRY_OUT" "FALSIFIED" "does not name the quote tweak"
assert_not_contains "$HUNGRY_OUT" "STR " "string kind is not default"

echo
echo "== ash: regenerate, do not blame a comment =="
ASH="$RUN/ash"
mkdir -p "$ASH/src" "$ASH/generated" "$ASH/oracle"
cp "$ROOT/fixtures/ash/src/config.py" "$ASH/src/"
cp "$ROOT/fixtures/ash/README.md" "$ASH/"
cp "$ROOT/fixtures/ash/generated/vendor_bundle.js" "$ASH/generated/"
cp "$ROOT/fixtures/ash/oracle/timeout.json" "$ASH/oracle/"
cp "$ROOT/fixtures/ash/package-lock.json" "$ASH/"
cp "$ROOT/fixtures/ash/Cargo.lock" "$ASH/"
cp "$ROOT/fixtures/ash/plugin.json" "$ASH/"
cp "$ROOT/fixtures/ash/OraclesGenerated.swift" "$ASH/"
cp "$ROOT/fixtures/ash/hook_bundle.js" "$ASH/"
git_init "$ASH"
git -C "$ASH" add .
git -C "$ASH" commit -qm "ash plant baseline"
python3 - <<'PY' "$ASH/src/config.py" "$ASH/plugin.json"
from pathlib import Path
import sys
Path(sys.argv[1]).write_text(
    Path(sys.argv[1]).read_text().replace("TIMEOUT = 10", "TIMEOUT = 30").replace("MAX_RETRIES = 3", "MAX_RETRIES = 8")
)
Path(sys.argv[2]).write_text(
    Path(sys.argv[2]).read_text().replace('"version": "0.3.0"', '"version": "0.7.0"').replace('"timeout": 10', '"timeout": 30')
)
PY
git -C "$ASH" add src/config.py plugin.json
git -C "$ASH" commit -qm "change facts, leave generated dest"

set +e
LOCK="$("$BINOM" --no-color -C "$ASH" Cargo.lock:6 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "lockfile ash is an answer"
assert_contains "$LOCK" "regenerate" "lockfile says regenerate"
assert_contains "$LOCK" "cargo" "lockfile names cargo"
assert_not_contains "$LOCK" "FALSIFIED" "lockfile does not blame a commit"

set +e
DOCS="$("$BINOM" --no-color --no-hunk -C "$ASH" README.md:3 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "docs leftover on the ash plant is still a believer"
assert_contains "$DOCS" "FALSIFIED" "docs leftover names a falsifying commit"
assert_contains "$DOCS" "10 → 30" "docs leftover of timeout 10"

echo
echo "== October is not leftover timeout 10 =="
DATES="$RUN/dates"
mkdir -p "$DATES/src" "$DATES/docs"
printf 'HOOK_TIMEOUT = 10\n' > "$DATES/src/config.py"
cat > "$DATES/CHANGELOG.md" <<'EOF'
## timeout
shipped 2024-10-01
EOF
cat > "$DATES/docs/help.md" <<'EOF'
timeout default is 10
shipped 2024-10-01
EOF
git_init "$DATES"
git -C "$DATES" add .
git -C "$DATES" commit -qm "timeout 10 with ISO dates"
printf 'HOOK_TIMEOUT = 30\n' > "$DATES/src/config.py"
git -C "$DATES" add src/config.py
git -C "$DATES" commit -qm "timeout 10 to 30"

set +e
DATE_NONE="$("$BINOM" --no-color -C "$DATES" CHANGELOG.md:2 2>&1)"
st=$?
set -e
assert_exit "$st" 1 "date-only locator is not a leftover timeout"
assert_contains "$DATE_NONE" "none" "date line reports none"
assert_not_contains "$DATE_NONE" "FALSIFIED" "October is not a falsified timeout 10"

set +e
DATE_REAL="$("$BINOM" --no-color --no-hunk -C "$DATES" docs/help.md:1 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "real timeout leftover still resolves"
assert_contains "$DATE_REAL" "10 → 30" "real leftover names the timeout bump"

echo
echo "== usage errors fail closed =="
set +e
USAGE="$("$BINOM" --no-color 2>&1)"
st=$?
set -e
assert_exit "$st" 2 "no locators is exit 2"
assert_contains "$USAGE" "FILE:LINE" "usage mentions FILE:LINE"

set +e
KINDS="$("$BINOM" --kinds "" --no-color -C "$TOY" README.md:3 2>&1)"
st=$?
set -e
assert_exit "$st" 2 "empty --kinds is exit 2"

echo
echo "== gold dogfood (kizu / sitbone) if present =="
KIZU_REPO="${KIZU_REPO:-$HOME/ghq/github.com/annenpolka/kizu}"
SIT_REPO="${SIT_REPO:-$HOME/ghq/github.com/annenpolka/sitbone}"
if [[ -d "$KIZU_REPO/.git" ]]; then
  set +e
  KIZU_OUT="$("$BINOM" --no-color --explain --no-hunk -C "$KIZU_REPO" plugin/plugin.json:4 2>&1)"
  st=$?
  set -e
  assert_exit "$st" 1 "kizu plugin.json is not leftover of Cargo.toml"
  assert_contains "$KIZU_OUT" "none" "plugin dest reports none"
  assert_contains "$KIZU_OUT" "package plugin:kizu" "dest package is the plugin, not the crate"
  assert_not_contains "$KIZU_OUT" "FALSIFIED" "homonym crate version is not the falsifier"
  assert_contains "$KIZU_OUT" "homonym" "crate bump is printed as homonym"
  assert_contains "$KIZU_OUT" "cargo:kizu" "homonym is the cargo crate"
  assert_contains "$KIZU_OUT" "Cargo.toml" "homonym origin is Cargo.toml"
  assert_contains "$KIZU_OUT" "53cbd1a" "53cbd1a is named as homonym, not FALSIFIED"
  assert_contains "$KIZU_OUT" "is not this package" "stop: homonym version is not the falsifier"
  set +e
  KIZU_LOCK="$("$BINOM" --no-color -C "$KIZU_REPO" Cargo.lock:168 2>&1)"
  st=$?
  set -e
  assert_exit "$st" 0 "kizu Cargo.lock is ash"
  assert_contains "$KIZU_LOCK" "regenerate" "kizu lockfile says regenerate"
  assert_contains "$KIZU_LOCK" "cargo" "kizu lockfile names cargo"
  assert_not_contains "$KIZU_LOCK" "FALSIFIED" "kizu lockfile does not blame a commit"
  set +e
  KIZU_CRATE="$("$BINOM" --no-color --no-hunk -C "$KIZU_REPO" Cargo.toml:3 2>&1)"
  st=$?
  set -e
  assert_exit "$st" 1 "live crate version 0.7.0 is not leftover"
  assert_contains "$KIZU_CRATE" "package cargo:kizu" "crate dest is cargo:kizu"
else
  echo "  skip kizu (not at $KIZU_REPO)"
fi
if [[ -d "$SIT_REPO/.git" ]]; then
  set +e
  SIT_OUT="$("$BINOM" --no-color --no-hunk -C "$SIT_REPO" CLAUDE.md:329 2>&1)"
  st=$?
  set -e
  assert_exit "$st" 0 "sitbone CLAUDE.md leftover is found"
  assert_contains "$SIT_OUT" "threshold 0.4" "sitbone threshold 0.4 leftover"
  assert_contains "$SIT_OUT" "0.4 → 0.45" "sitbone falsifier is 0.4→0.45"
  assert_contains "$SIT_OUT" "e9b0f75" "sitbone still names the hysteresis commit"
  assert_contains "$SIT_OUT" "PresenceArbiter" "sitbone origin is PresenceArbiter"
  set +e
  SIT2="$("$BINOM" --no-color --no-hunk -C "$SIT_REPO" CLAUDE.md:332 2>&1)"
  st=$?
  set -e
  assert_contains "$SIT2" "e9b0f75" "second CLAUDE.md line names the hysteresis commit"
else
  echo "  skip sitbone (not at $SIT_REPO)"
fi

echo
echo "passed=$pass failed=$fail"
if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
exit 0
