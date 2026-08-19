#!/usr/bin/env bash
# Exercise sluice as a filter: templates from rg/git/files, never a walk.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SLUICE="$ROOT/sluice"
FIX="$ROOT/fixtures"
chmod +x "$SLUICE"

pass=0
fail=0

ok() {
  pass=$((pass + 1))
  echo "  PASS  $1"
}

bad() {
  fail=$((fail + 1))
  echo "  FAIL  $1"
  echo "        $2"
}

echo "== selftest =="
if "$SLUICE" --selftest; then
  ok "selftest"
else
  bad "selftest" "sluice --selftest exited $?"
fi

echo "== refuses to walk =="
# -C is chdir (path prefix), not a scan. Without a stream there are no templates.
if out="$("$SLUICE" -C "$FIX" 'user 42 not found' 2>&1)"; then
  bad "-C without stream" "scanned the tree?: $out"
else
  if echo "$out" | grep -qE 'no templates|0 templates ingested'; then
    ok "-C without stream does not walk"
  else
    bad "-C without stream does not walk" "$out"
  fi
fi
if out="$("$SLUICE" --templates "$FIX" 'user 42 not found' 2>&1)"; then
  bad "reject dir --templates" "walked: $out"
else
  if echo "$out" | grep -q 'refusing to walk'; then
    ok "reject dir --templates"
  else
    bad "reject dir --templates" "$out"
  fi
fi

echo "== --templates file (raw + grep streams) =="
if out="$("$SLUICE" --templates "$FIX/streams/raw.txt" --from raw 'user 42 not found')" \
  && echo "$out" | grep -q 'user {} not found'; then
  ok "raw template file"
else
  bad "raw template file" "${out:-}"
fi
if out="$("$SLUICE" --templates "$FIX/streams/grep.txt" 'Duplicate event ID: evt-99')" \
  && echo "$out" | grep -q 'events.ts:'; then
  ok "grep-format template file"
else
  bad "grep-format template file" "${out:-}"
fi

echo "== rg | sluice (policy lives in rg) =="
q() {
  local name="$1"
  local needle="$2"
  local msg="$3"
  shift 3
  local out
  if out="$(rg -n --no-heading "$@" "$FIX" | "$SLUICE" --templates - -n 3 "$msg")"; then
    if echo "$out" | grep -F -q "$needle"; then
      ok "$name"
    else
      bad "$name" "expected '$needle' in: $out"
    fi
  else
    bad "$name" "exit $? out=$out"
  fi
}

q "filled rust anyhow" "src/git.rs:" \
  "git diff single file failed: fatal: not a git repository" \
  -g '*.rs' 'format!'
q "named rust + backticks" "src/git.rs:" \
  "unparseable \`diff --git\` header: diff --git a/foo b/foo" \
  -g '*.rs' 'format!'
q "two named rust holes" "src/git.rs:" \
  $'diff --git a/src/weird.rs b/src/weird.rs\n' \
  -g '*.rs' 'format!'
q "python f-string" "src/user.py:" \
  "user 42 not found" \
  -g '*.py' 'f"'
q "python host:port hole" "src/user.py:" \
  "cannot reach db.internal:5432 after 3 retries" \
  -g '*.py' 'f"'
q "js template" "src/events.ts:" \
  "Duplicate event ID: evt-99" \
  -g '*.ts' 'Error|TypeError|RangeError'
q "js two-hole template" "src/events.ts:" \
  "Cannot enqueue event before processed time 1200: 800" \
  -g '*.ts' 'RangeError|enqueue'
q "js exact literal" "src/events.ts:" \
  "Event id must not be empty" \
  -g '*.ts' 'TypeError|empty'
q "swift interpolation" "src/log.swift:" \
  "session started profile=Focus" \
  -g '*.swift' 'Logger|session started'
q "go printf" "src/printf.go:" \
  "open /tmp/x: permission denied" \
  -g '*.go' 'fmt.Errorf'
q "spaces in path" "file with spaces.rs:" \
  "cannot open strange file: /tmp/a b.txt" \
  -g '*.rs' 'strange'
q "nested secret" "nested/repo/secret.py:" \
  "nested secret key hunter2 leaked" \
  -g '*.py' 'secret'

echo "== rg ignore/glob is the skip policy (not sluice) =="
# node_modules/ is gitignored in this tree; default rg hides hidden.js
if rg -n --no-heading 'should not be indexed' "$FIX" \
  | "$SLUICE" --templates - --extract | grep -q 'should not be indexed'; then
  bad "default rg skips gitignored node_modules" "hidden.js leaked"
else
  ok "default rg skips gitignored node_modules"
fi
if rg -n --no-heading --no-ignore -g '**/hidden.js' 'should not be indexed' "$FIX" \
  | "$SLUICE" --templates - --extract | grep -q 'should not be indexed'; then
  ok "rg --no-ignore admits node_modules when asked"
else
  bad "rg --no-ignore admits node_modules when asked" "expected hidden.js template"
fi
# *.min.js is NOT ignored by default; the caller must glob it out
if rg -n --no-heading -g '!*.min.js' 'minified decoy' "$FIX" \
  | "$SLUICE" --templates - --extract | grep -q 'minified decoy'; then
  bad "rg -g '!*.min.js'" "min.js leaked after exclude glob"
else
  ok "rg -g '!*.min.js' keeps minified decoy out"
fi
if rg -n --no-heading -g '*.min.js' 'minified decoy' "$FIX" \
  | "$SLUICE" --templates - --extract | grep -q 'minified decoy'; then
  ok "rg -g '*.min.js' admits minified decoy when asked"
else
  bad "rg -g '*.min.js' admits minified decoy when asked" "expected min.js template"
fi

echo "== --files (rg -l) + slurp source =="
if out="$(rg -l --glob '*.swift' 'Logger' "$FIX" | "$SLUICE" --files - \
  'cumulative save failed path=/tmp/c.json error=disk full')" \
  && echo "$out" | grep -q 'log.swift:' \
  && echo "$out" | grep -q 'path={} error={}'; then
  ok "--files hydrates multiline swift"
else
  bad "--files hydrates multiline swift" "${out:-}"
fi
if out="$("$SLUICE" --templates "$FIX/src/log.swift" \
  'cumulative save failed path=/tmp/c.json error=disk full')" \
  && echo "$out" | grep -q 'path={} error={}'; then
  ok "--templates source file slurps"
else
  bad "--templates source file slurps" "${out:-}"
fi

echo "== extract round-trip =="
idx="$(rg -n --no-heading -g '*.py' 'f"' "$FIX" | "$SLUICE" --templates - --extract)"
if echo "$idx" | grep -q 'user {} not found'; then
  ok "extract dumps templates"
else
  bad "extract dumps templates" "$idx"
fi
if out="$(echo "$idx" | "$SLUICE" --templates - --from index 'user 7 not found')" \
  && echo "$out" | grep -q 'user {} not found'; then
  ok "extract | sluice --from index"
else
  bad "extract | sluice --from index" "${out:-}"
fi

echo "== dashed message via -e =="
if out="$(rg -n --no-heading -g '*.swift' 'device init' "$FIX" | "$SLUICE" --templates - -e "device init failed")" \
  && echo "$out" | grep -q 'log.swift:'; then
  ok "-e message"
else
  bad "-e message" "${out:-}"
fi

echo "== stdin queries + --templates FILE =="
pipe_out="$(
  {
    echo "Compiling sluice v0.1.0"
    echo "ERROR [worker] user 7 not found"
    printf '\x1b[31merror:\x1b[0m git diff single file failed: boom\n'
  } | "$SLUICE" --templates "$FIX/streams/grep.txt" --any
)"
if echo "$pipe_out" | grep -q 'user.py:' && echo "$pipe_out" | grep -q 'git.rs:'; then
  ok "stdin log strip + multi-message"
else
  bad "stdin log strip + multi-message" "$pipe_out"
fi

echo "== miss exits 1 =="
if "$SLUICE" --templates "$FIX/streams/raw.txt" "this message exists nowhere xyzzy-sluice" >/dev/null; then
  bad "miss exit" "expected exit 1"
else
  ok "miss exit 1"
fi

# Real trees: templates via rg/git, never sluice -C.
KIZU="/Users/annenpolka/ghq/github.com/annenpolka/kizu"
VOID="/Users/annenpolka/ghq/github.com/annenpolka/voidtrace"
SIT="/Users/annenpolka/ghq/github.com/annenpolka/sitbone"
TENA="/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi"

dogfood_rg() {
  local name="$1"
  local repo="$2"
  local glob="$3"
  local pat="$4"
  local needle="$5"
  local msg="$6"
  if [[ ! -d "$repo" ]]; then
    echo "  SKIP  dogfood $name (missing $repo)"
    return 0
  fi
  local out
  if out="$(rg -n --no-heading -g "$glob" -g '!target/**' -g '!node_modules/**' "$pat" "$repo" \
    | "$SLUICE" --templates - -n 5 "$msg")"; then
    if echo "$out" | grep -F -q "$needle"; then
      ok "dogfood rg $name: $needle"
    else
      bad "dogfood rg $name: $needle" "$out"
    fi
  else
    bad "dogfood rg $name: $needle" "exit $? out=$out"
  fi
}

echo "== dogfood via rg (if present) =="
dogfood_rg "kizu" "$KIZU" '*.rs' 'format!|anyhow!' \
  "src/git/diff.rs:" \
  "git diff single file failed: fatal: not a git repository (or any of the parent directories): /tmp/nope"
dogfood_rg "voidtrace" "$VOID" '*.ts' 'Duplicate event ID|throw new' \
  "packages/kernel/src/event-queue.ts:" \
  "Duplicate event ID: evt-abc"
dogfood_rg "sitbone" "$SIT" '*.swift' 'session started profile' \
  "Sources/SitboneCore/SitboneCore.swift:" \
  "session started profile=DeepWork"
dogfood_rg "tenaoshi" "$TENA" '*.swift' 'has_more cannot be true' \
  "Engine/Sources/TenaoshiEngine/EditPlan.swift:" \
  "has_more cannot be true when units is empty"

echo "== policy contrast: git grep vs rg on untracked tenaoshi =="
if [[ -d "$TENA" ]]; then
  git_out="$(git -C "$TENA" grep -n -e 'has_more cannot be true' -- '*.swift' 2>/dev/null || true)"
  if [[ -z "$git_out" ]]; then
    ok "git grep misses untracked EditPlan.swift (caller policy)"
  else
    echo "  NOTE  git grep unexpectedly hit untracked file"
    ok "git grep produced templates"
  fi
  if rg -n --no-heading -g '*.swift' 'has_more cannot be true' "$TENA" \
    | "$SLUICE" --templates - -q -e 'has_more cannot be true when units is empty'; then
    ok "rg sees untracked tenaoshi and sluice matches"
  else
    bad "rg tenaoshi untracked" "rg|sluice missed EditPlan.swift"
  fi
fi

echo "== sitbone multiline: auto-open vs --open never =="
if [[ -d "$SIT" ]]; then
  line_out="$(
    rg -n --no-heading -g '*.swift' 'cumulative save failed' "$SIT" \
      | "$SLUICE" --templates - -n 3 \
        'cumulative save failed path=/Users/x/Library/cumulative.json error=The file could not be saved'
  )"
  if echo "$line_out" | grep -q 'path={} error={}'; then
    ok "sitbone cumulative via rg -n (auto-open file)"
  else
    bad "sitbone cumulative via rg -n (auto-open file)" "${line_out:-empty}"
  fi
  never_out="$(
    rg -n --no-heading -g '*.swift' 'cumulative save failed' "$SIT" \
      | "$SLUICE" --templates - --open never -n 3 \
        'cumulative save failed path=/Users/x/Library/cumulative.json error=The file could not be saved' \
      || true
  )"
  if echo "$never_out" | grep -q 'path={} error={}'; then
    bad "--open never should stay 1-hole" "$never_out"
  elif echo "$never_out" | grep -q 'path={}'; then
    ok "--open never stays a 1-hole fragment"
  else
    bad "--open never fragment" "${never_out:-empty}"
  fi
  files_out="$(
    rg -l -g '*.swift' 'cumulative save failed' "$SIT" \
      | "$SLUICE" --files - -n 3 \
        'cumulative save failed path=/Users/x/Library/cumulative.json error=The file could not be saved'
  )"
  if echo "$files_out" | grep -q 'path={} error={}'; then
    ok "sitbone cumulative via rg -l | --files"
  else
    bad "sitbone cumulative via rg -l | --files" "$files_out"
  fi
fi

echo "== --chdir lets git -C grep hydrate relative paths =="
if [[ -d "$KIZU" ]]; then
  # format! does not appear on the anyhow! line; hydration of files that
  # *also* contain format! is what recovers the runtime template.
  if git -C "$KIZU" grep -n -e 'format!' -- '*.rs' \
    | "$SLUICE" --templates - --chdir "$KIZU" -q \
      'git diff single file failed: boom'; then
    ok "git grep format! + --chdir hydrates anyhow! sibling"
  else
    bad "git grep format! + --chdir hydrates anyhow! sibling" "missed"
  fi
  if git -C "$KIZU" grep -n -e 'format!' -- '*.rs' \
    | "$SLUICE" --templates - --open never -q \
      'git diff single file failed: boom'; then
    bad "without hydrate, format! grep should miss anyhow!" "unexpected hit"
  else
    ok "without hydrate, git grep format! misses anyhow!"
  fi
fi

echo "== --chdir + relative grep line (fixture) =="
chdir_out="$(
  printf '%s\n' 'src/log.swift:7:        cumulative save failed path=\(path) \' \
    | "$SLUICE" --chdir "$FIX" --from grep \
      'cumulative save failed path=/tmp/c.json error=disk full'
)"
if echo "$chdir_out" | grep -q 'path={} error={}'; then
  ok "--chdir hydrates relative fixture path"
else
  bad "--chdir hydrates relative fixture path" "$chdir_out"
fi

echo
echo "passed=$pass failed=$fail"
if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
exit 0
