#!/usr/bin/env bash
# Exercise tinder: leftover FILE:LINE in, fact-falsifying commit out.
# Dest-file identity follows; a dest rename is not the falsifier.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
TINDER="$ROOT/tinder"
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
  git -C "$repo" config user.email "tinder@example.test"
  git -C "$repo" config user.name "tinder"
}

echo "== self-test =="
set +e
"$TINDER" self-test
st=$?
set -e
assert_exit "$st" 0 "embedded parser/scorer/dest-identity tests"

echo
echo "== dest-file rename: leftover moved, fact commit is not the rename =="
SLIP="$RUN/slip"
mkdir -p "$SLIP/src" "$SLIP/docs"
printf 'HOOK_TIMEOUT = 10\nMAX_RETRIES = 3\n' > "$SLIP/src/config.py"
printf 'timeout default is 10\n' > "$SLIP/docs/help.md"
git_init "$SLIP"
git -C "$SLIP" add .
git -C "$SLIP" commit -qm "timeout 10 with dest leftover"
printf 'HOOK_TIMEOUT = 30\nMAX_RETRIES = 3\n' > "$SLIP/src/config.py"
git -C "$SLIP" add src/config.py
git -C "$SLIP" commit -qm "timeout 10 to 30"
FACT_SHA="$(git -C "$SLIP" rev-parse --short=12 HEAD)"
git -C "$SLIP" mv docs/help.md docs/guide.md
git -C "$SLIP" commit -qm "move leftover dest help.md → guide.md"
RENAME_SHA="$(git -C "$SLIP" rev-parse --short=12 HEAD)"
PATH_LIE="$(git -C "$SLIP" log --oneline -S 10 -- docs/guide.md | head -1 || true)"

set +e
NEW="$("$TINDER" --no-color --no-hunk -C "$SLIP" docs/guide.md:1 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "dest leftover at new name is found"
assert_contains "$NEW" "timeout default is 10" "claim is still timeout 10"
assert_contains "$NEW" "10 → 30" "names the timeout fact"
assert_contains "$NEW" "$FACT_SHA" "names the fact-falsifying commit"
assert_not_contains "$NEW" "$RENAME_SHA" "does not name the dest-file rename"
assert_contains "$NEW" "docs/help.md → docs/guide.md" "prints dest identity"
assert_contains "$PATH_LIE" "move leftover dest" "path-limited pickaxe names the rename (the hole)"

set +e
OLD="$("$TINDER" --no-color --no-hunk -C "$SLIP" docs/help.md:1 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "dead dest name still follows"
assert_contains "$OLD" "10 → 30" "old dest name names the fact, not missing"
assert_contains "$OLD" "$FACT_SHA" "old dest name names the fact commit"
assert_not_contains "$OLD" "$RENAME_SHA" "old dest name does not name the rename"
assert_contains "$OLD" "docs/guide.md" "old dest name resolved to live holder"

set +e
NOFOL="$("$TINDER" --no-follow --no-color --no-hunk -C "$SLIP" docs/help.md:1 2>&1)"
st=$?
set -e
assert_exit "$st" 1 " --no-follow dead dest name is missing"
assert_contains "$NOFOL" "missing" "--no-follow reports missing"

# 3-hop dest identity + CJK dest name
git -C "$SLIP" mv docs/guide.md "docs/最終.md"
git -C "$SLIP" commit -qm "second dest hop to 最終.md"
set +e
HOP="$("$TINDER" --no-color --no-hunk -C "$SLIP" docs/help.md:1 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "3-hop dead dest name still follows"
assert_contains "$HOP" "10 → 30" "3-hop still names the timeout fact"
assert_contains "$HOP" "最終.md" "3-hop live holder is CJK dest name"
assert_not_contains "$HOP" "$RENAME_SHA" "3-hop does not name the first rename"

# Copy is not dest identity. Querying the copy still leftover-matches the fact
# (the copy also claims timeout 10) but dest identity stays the copy.
cp "$SLIP/docs/最終.md" "$SLIP/docs/copy.md"
git -C "$SLIP" add docs/copy.md
git -C "$SLIP" commit -qm "copy dest leftover, not a rename"
set +e
COPY="$("$TINDER" --no-color --json --no-hunk -C "$SLIP" docs/copy.md:1 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "copied dest leftover still finds the fact"
assert_contains "$COPY" "10" "copy leftover still claims 10"
assert_not_contains "$COPY" "docs/help.md" "copy is not dest identity of the rename"

# Dest rewrite after the move: old FILE:LINE must slip onto the leftover.
printf '# Guide\n\n' > "$SLIP/docs/最終.md.tmp"
cat "$SLIP/docs/最終.md" >> "$SLIP/docs/最終.md.tmp"
mv "$SLIP/docs/最終.md.tmp" "$SLIP/docs/最終.md"
git -C "$SLIP" add "docs/最終.md"
git -C "$SLIP" commit -qm "prepend dest heading after the move"
set +e
SLIPPED="$("$TINDER" --no-color --json --no-hunk -C "$SLIP" docs/help.md:1 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "dest-line slip still finds the fact"
assert_contains "$SLIPPED" '"slipped": true' "dest leftover line slipped past the new heading"
assert_contains "$SLIPPED" "timeout default is 10" "slipped dest still claims timeout 10"
assert_contains "$SLIPPED" "10" "slipped dest still names the timeout fact"
assert_not_contains "$SLIPPED" "# Guide" "slipped dest is not the new heading"

echo
echo "== ash dest rename is still regenerate, never the dest mv =="
ASHMV="$RUN/ash-mv"
mkdir -p "$ASHMV/src" "$ASHMV/generated"
printf 'TIMEOUT = 10\n' > "$ASHMV/src/config.py"
printf '// generated — do not edit\nconst TIMEOUT = 10;\n' > "$ASHMV/generated/vendor_bundle.js"
git_init "$ASHMV"
git -C "$ASHMV" add .
git -C "$ASHMV" commit -qm "ash dest plant"
printf 'TIMEOUT = 30\n' > "$ASHMV/src/config.py"
git -C "$ASHMV" add src/config.py
git -C "$ASHMV" commit -qm "timeout 10 to 30, leave generated dest"
git -C "$ASHMV" mv generated/vendor_bundle.js generated/out.js
git -C "$ASHMV" commit -qm "rename generated dest"
set +e
ASHNEW="$("$TINDER" --no-color -C "$ASHMV" generated/out.js:2 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "renamed ash dest is an answer"
assert_contains "$ASHNEW" "regenerate" "renamed ash says regenerate"
assert_not_contains "$ASHNEW" "FALSIFIED" "renamed ash does not blame a commit"
set +e
ASHOLD="$("$TINDER" --no-color -C "$ASHMV" generated/vendor_bundle.js:2 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "dead ash dest name follows to regenerate"
assert_contains "$ASHOLD" "regenerate" "followed ash dest still regenerate"
assert_not_contains "$ASHOLD" "FALSIFIED" "followed ash dest does not name the rename"

echo
echo "== toy: uncommitted falsifier, then committed =="
TOY="$RUN/toy"
mkdir -p "$TOY/src" "$TOY/tests" "$TOY/docs"
cp "$ROOT/fixtures/toy/src/retry.py" "$TOY/src/"
cp "$ROOT/fixtures/toy/README.md" "$TOY/"
cp "$ROOT/fixtures/toy/tests/test_retry.py" "$TOY/tests/"
cp "$ROOT/fixtures/toy/docs/help.txt" "$TOY/docs/"
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

set +e
WT="$("$TINDER" --no-color --no-hunk -C "$TOY" README.md:3 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "worktree leftover is found"
assert_contains "$WT" "WORKTREE" "uncommitted falsifier labeled WORKTREE"
assert_contains "$WT" "MAX_RETRIES" "rename leftover names old ident"
assert_contains "$WT" "MAX_ATTEMPTS" "rename leftover names new ident"

set +e
VER="$("$TINDER" --no-color --no-hunk -C "$TOY" README.md:7 2>&1)"
st=$?
set -e
assert_contains "$VER" "0.3.0" "prose leftover is the full version token"
assert_contains "$VER" "0.7.0" "falsifier new version"
assert_not_contains "$VER" "0.3 →" "version is not truncated to 0.3"

git -C "$TOY" add src/retry.py plugin.json
git -C "$TOY" commit -qm "change facts, forget the claims"

set +e
COMMITTED="$("$TINDER" --no-color --explain --no-hunk -C "$TOY" README.md:7 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "committed leftover is found"
assert_contains "$COMMITTED" "change facts, forget the claims" "names the falsifying commit subject"
assert_contains "$COMMITTED" "plugin.json" "JSON quoted version is the origin"
assert_contains "$COMMITTED" "0.3.0" "old token"
assert_contains "$COMMITTED" "10 → 30" "same prose line also leftover-claims timeout 10"

set +e
HELP="$("$TINDER" --no-color --no-hunk -C "$TOY" docs/help.txt:2 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "cli help leftover is found"
assert_contains "$HELP" "HOOK_TIMEOUT" "timeout help names the bound fact"
assert_contains "$HELP" "10 → 30" "timeout 10→30"

set +e
TEST="$("$TINDER" --no-color --no-hunk -C "$TOY" tests/test_retry.py:5 2>&1)"
st=$?
set -e
assert_contains "$TEST" "MAX_RETRIES" "assert leftover names the rename"

set +e
FLIP="$("$TINDER" --no-color --no-hunk -C "$TOY" README.md:9 2>&1)"
st=$?
set -e
assert_contains "$FLIP" "ENABLE_CACHE" "polarity leftover names the flip"
assert_contains "$FLIP" "True → False" "polarity True→False"

echo
echo "== stdin locators + FILE:LINE with spaces / Japanese =="
mkdir -p "$TOY/emoji"
printf 'still claims MAX_RETRIES\n' > "$TOY/emoji/🌀 leftover.md"
cp "$ROOT/fixtures/ugly/file with spaces.md" "$TOY/" 2>/dev/null || printf 'MAX_RETRIES is 3, always.\n' > "$TOY/file with spaces.md"
cp "$ROOT/fixtures/ugly/日本語コメント.md" "$TOY/" 2>/dev/null || printf 'タイムアウトは 10 秒です。MAX_RETRIES はまだ 3 のまま。\n' > "$TOY/日本語コメント.md"
git -C "$TOY" add -A
if ! git -C "$TOY" diff --quiet; then
  git -C "$TOY" add -A
  git -C "$TOY" commit -qm "ugly leftover names"
fi

set +e
STDIN="$(printf 'README.md:7\ndocs/help.txt:2\n' | "$TINDER" --no-color --no-hunk -C "$TOY" 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "stdin locators found"
assert_contains "$STDIN" "plugin version 0.3.0" "stdin first locator"
assert_contains "$STDIN" "hook timeout seconds" "stdin second locator"

set +e
SPACES="$("$TINDER" --no-color --no-hunk -C "$TOY" "file with spaces.md:3" 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "space in filename is a legal locator"
assert_contains "$SPACES" "MAX_RETRIES" "space-filename leftover"

set +e
JP="$("$TINDER" --no-color --no-hunk -C "$TOY" "日本語コメント.md:3" 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "unicode filename leftover is found"
assert_contains "$JP" "タイムアウトは 10" "Japanese leftover sentence"
assert_contains "$JP" "FALSIFIED" "Japanese leftover of an English fact still names the falsifying commit"
assert_contains "$JP" "MAX_RETRIES" "same line still names the rename leftover"
assert_contains "$JP" "10 → 30" "same line also names the timeout leftover (not max-score only)"

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
LOCK="$("$TINDER" --no-color -C "$ASH" Cargo.lock:6 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "lockfile ash is an answer"
assert_contains "$LOCK" "regenerate" "lockfile says regenerate"
assert_contains "$LOCK" "cargo" "lockfile names cargo"
assert_not_contains "$LOCK" "FALSIFIED" "lockfile does not blame a commit"
assert_not_contains "$LOCK" "edit" "ash does not say edit this line"

set +e
PKG="$("$TINDER" --no-color -C "$ASH" package-lock.json:7 2>&1)"
st=$?
set -e
assert_contains "$PKG" "regenerate" "package-lock says regenerate"
assert_contains "$PKG" "npm" "package-lock names npm"

set +e
GEN="$("$TINDER" --no-color -C "$ASH" generated/vendor_bundle.js:2 2>&1)"
st=$?
set -e
assert_contains "$GEN" "ASH" "generated/ is ash"
assert_contains "$GEN" "regenerate" "generated says regenerate"
assert_not_contains "$GEN" "FALSIFIED" "generated dest is not a blamed leftover claim"

set +e
ORACLE="$("$TINDER" --no-color -C "$ASH" oracle/timeout.json:1 2>&1)"
st=$?
set -e
assert_contains "$ORACLE" "regenerate" "oracle dest says regenerate"

set +e
SWIFT="$("$TINDER" --no-color -C "$ASH" OraclesGenerated.swift:1 2>&1)"
st=$?
set -e
assert_contains "$SWIFT" "regenerate" "OraclesGenerated says regenerate"
assert_contains "$SWIFT" "spec-gen.ts" "banner names the generator"

set +e
BANNER="$("$TINDER" --no-color -C "$ASH" hook_bundle.js:2 2>&1)"
st=$?
set -e
assert_contains "$BANNER" "regenerate" "banner-generated file says regenerate"
assert_contains "$BANNER" "ASH" "banner dest is ash"

set +e
DOCS="$("$TINDER" --no-color --no-hunk -C "$ASH" README.md:3 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "docs leftover on the ash plant is still a believer"
assert_contains "$DOCS" "FALSIFIED" "docs leftover names a falsifying commit"
assert_contains "$DOCS" "10 → 30" "docs leftover of timeout 10"

echo
echo "== JSON-only quoted version hunk (destroyer) =="
KIZU_TOY="$RUN/kizu-toy"
mkdir -p "$KIZU_TOY"
cat > "$KIZU_TOY/plugin.json" <<'EOF'
{
  "name": "toy",
  "version": "0.3.0",
  "hooks": {
    "timeout": 10
  }
}
EOF
cat > "$KIZU_TOY/README.md" <<'EOF'
plugin version 0.3.0, hook timeout 10 seconds.
EOF
cat > "$KIZU_TOY/package-lock.json" <<'EOF'
{
  "name": "toy",
  "lockfileVersion": 3,
  "packages": {
    "": { "version": "0.3.0" }
  }
}
EOF
git_init "$KIZU_TOY"
git -C "$KIZU_TOY" add .
git -C "$KIZU_TOY" commit -qm "dest still claims 0.3.0 in prose"
python3 - <<'PY' "$KIZU_TOY/plugin.json"
from pathlib import Path
import sys
Path(sys.argv[1]).write_text(Path(sys.argv[1]).read_text().replace('"version": "0.3.0"', '"version": "0.7.0"'))
PY
git -C "$KIZU_TOY" add plugin.json
git -C "$KIZU_TOY" commit -qm "json-only version bump"

set +e
JSON_OUT="$("$TINDER" --no-color --explain --no-hunk -C "$KIZU_TOY" README.md:1 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "JSON-only bump falsifies prose leftover"
assert_contains "$JSON_OUT" "0.3.0" "full version token"
assert_contains "$JSON_OUT" "0.7.0" "new version"
assert_contains "$JSON_OUT" "plugin.json" "quoted JSON key is the origin"
assert_not_contains "$JSON_OUT" "package-lock.json" "lockfile is not the falsifying origin"

set +e
JSON_ASH="$("$TINDER" --no-color -C "$KIZU_TOY" package-lock.json:4 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "JSON lockfile leftover is ash"
assert_contains "$JSON_ASH" "regenerate" "JSON lockfile says regenerate"
assert_not_contains "$JSON_ASH" "FALSIFIED" "JSON lockfile does not blame a comment"

JSONDIFF="$RUN/plugin.diff"
cat > "$JSONDIFF" <<'EOF'
diff --git a/plugin.json b/plugin.json
--- a/plugin.json
+++ b/plugin.json
@@ -1,6 +1,6 @@
 {
   "name": "toy",
-  "version": "0.3.0",
+  "version": "0.7.0",
   "hooks": {
     "timeout": 10
   }
 }
EOF
set +e
DIFF_OUT="$("$TINDER" --no-color --no-hunk --diff "$JSONDIFF" -C "$KIZU_TOY" README.md:1 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "--diff JSON hunk falsifies plugin version 0.3.0"
assert_contains "$DIFF_OUT" "DIFF" "supplied diff is the falsifier"
assert_contains "$DIFF_OUT" "0.3.0 → 0.7.0" "full token in --diff mode"

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
git -C "$DATES" mv docs/help.md docs/guide.md
git -C "$DATES" commit -qm "rename dest leftover after timeout bump"

set +e
DATE_NONE="$("$TINDER" --no-color -C "$DATES" CHANGELOG.md:2 2>&1)"
st=$?
set -e
assert_exit "$st" 1 "date-only locator is not a leftover timeout"
assert_contains "$DATE_NONE" "none" "date line reports none"
assert_not_contains "$DATE_NONE" "FALSIFIED" "October is not a falsified timeout 10"
assert_not_contains "$DATE_NONE" "HOOK_TIMEOUT" "date line does not name HOOK_TIMEOUT"

set +e
DATE_REAL="$("$TINDER" --no-color --no-hunk -C "$DATES" docs/guide.md:1 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "real timeout leftover still resolves after dest rename"
assert_contains "$DATE_REAL" "timeout default is 10" "real leftover sentence"
assert_contains "$DATE_REAL" "10 → 30" "real leftover names the timeout bump"
assert_not_contains "$DATE_REAL" "rename dest leftover" "October plant dest rename is not the falsifier"

echo
echo "== usage errors fail closed =="
set +e
USAGE="$("$TINDER" --no-color 2>&1)"
st=$?
set -e
assert_exit "$st" 2 "no locators is exit 2"
assert_contains "$USAGE" "FILE:LINE" "usage mentions FILE:LINE"

set +e
KINDS="$("$TINDER" --kinds "" --no-color -C "$TOY" README.md:3 2>&1)"
st=$?
set -e
assert_exit "$st" 2 "empty --kinds is exit 2"

set +e
BAD="$("$TINDER" --no-color -C "$TOY" README.md 2>&1)"
st=$?
set -e
assert_exit "$st" 2 "bare path without line is exit 2"

echo
echo "== gold dogfood (kizu / sitbone / tenaoshi) if present =="
KIZU_REPO="${KIZU_REPO:-$HOME/ghq/github.com/annenpolka/kizu}"
SIT_REPO="${SIT_REPO:-$HOME/ghq/github.com/annenpolka/sitbone}"
TENA_REPO="${TENA_REPO:-$HOME/ghq/github.com/annenpolka/tenaoshi}"
if [[ -d "$KIZU_REPO/.git" ]]; then
  set +e
  KIZU_OUT="$("$TINDER" --no-color --explain --no-hunk -C "$KIZU_REPO" plugin/plugin.json:4 2>&1)"
  st=$?
  set -e
  assert_exit "$st" 0 "kizu plugin.json leftover is found"
  assert_contains "$KIZU_OUT" "0.3.0" "kizu plugin still claims 0.3.0"
  assert_contains "$KIZU_OUT" "Cargo.toml" "kizu falsifier is Cargo.toml, not a comment"
  assert_not_contains "$KIZU_OUT" "Cargo.lock" "kizu lockfile is not the falsifying origin"
  set +e
  KIZU_PLAN="$("$TINDER" --no-color --no-hunk -C "$KIZU_REPO" plans/v0.3.md:103 2>&1)"
  st=$?
  set -e
  assert_contains "$KIZU_PLAN" "0.3.0" "kizu plan leftover still resolves"
  set +e
  KIZU_LOCK="$("$TINDER" --no-color -C "$KIZU_REPO" Cargo.lock:168 2>&1)"
  st=$?
  set -e
  assert_exit "$st" 0 "kizu Cargo.lock is ash"
  assert_contains "$KIZU_LOCK" "regenerate" "kizu lockfile says regenerate"
  assert_contains "$KIZU_LOCK" "cargo" "kizu lockfile names cargo"
  assert_not_contains "$KIZU_LOCK" "FALSIFIED" "kizu lockfile does not blame a commit"

  # The dest leftover that *moved* with kizu's R100. Path-limited pickaxe
  # names 4e37f16 (the rename). v0.1 named a hungry string in init.test.ts.
  # timeout is still 10 in the installer — dest leftover is not leftover-name.
  set +e
  KIZU_DEST="$("$TINDER" --no-color --no-hunk -C "$KIZU_REPO" docs/deep-research-ai-agent-hooks.md:84 2>&1)"
  st=$?
  set -e
  assert_exit "$st" 1 "kizu dest leftover of still-true timeout 10 is none"
  assert_contains "$KIZU_DEST" "none" "kizu dest leftover reports none"
  assert_not_contains "$KIZU_DEST" "4e37f16" "kizu dest leftover does not name the dest rename"
  assert_not_contains "$KIZU_DEST" "FALSIFIED" "kizu dest leftover is not leftover-name of a quote tweak"
  set +e
  KIZU_OLD="$("$TINDER" --no-color --no-hunk -C "$KIZU_REPO" deep-research-ai-agent-hooks.md:84 2>&1)"
  st=$?
  set -e
  assert_exit "$st" 1 "kizu dead dest name follows to the same none"
  assert_not_contains "$KIZU_OLD" "missing" "kizu dead dest name follows"
  assert_not_contains "$KIZU_OLD" "4e37f16" "followed kizu dest leftover does not name the rename"
  assert_contains "$KIZU_OLD" "docs/deep-research-ai-agent-hooks.md" "old dest name resolved to live holder"
else
  echo "  skip kizu (not at $KIZU_REPO)"
fi
if [[ -d "$SIT_REPO/.git" ]]; then
  set +e
  SIT_OUT="$("$TINDER" --no-color --no-hunk -C "$SIT_REPO" CLAUDE.md:329 2>&1)"
  st=$?
  set -e
  assert_exit "$st" 0 "sitbone CLAUDE.md leftover is found"
  assert_contains "$SIT_OUT" "threshold 0.4" "sitbone threshold 0.4 leftover"
  assert_contains "$SIT_OUT" "0.4 → 0.45" "sitbone falsifier is 0.4→0.45"
  assert_contains "$SIT_OUT" "PresenceArbiter" "sitbone origin is PresenceArbiter"
  set +e
  SIT2="$("$TINDER" --no-color --no-hunk -C "$SIT_REPO" CLAUDE.md:332 2>&1)"
  st=$?
  set -e
  assert_contains "$SIT2" "e9b0f75" "second CLAUDE.md line names the hysteresis commit"
else
  echo "  skip sitbone (not at $SIT_REPO)"
fi
if [[ -d "$TENA_REPO/.git" ]]; then
  set +e
  TENA="$("$TINDER" --no-color -C "$TENA_REPO" Engine/Tests/TenaoshiEngineTests/OraclesGenerated.swift:1 2>&1)"
  st=$?
  set -e
  assert_exit "$st" 0 "tenaoshi generated oracle is ash"
  assert_contains "$TENA" "regenerate" "tenaoshi oracle says regenerate"
  assert_not_contains "$TENA" "FALSIFIED" "tenaoshi oracle is not a blamed leftover claim"
else
  echo "  skip tenaoshi (not at $TENA_REPO)"
fi

echo
echo "passed=$pass failed=$fail"
if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
exit 0
