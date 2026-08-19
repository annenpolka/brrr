#!/usr/bin/env bash
# Exercise invert as a filter: templates from rg/git/files, named hole bindings.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
INVERT="$ROOT/invert"
FIX="$ROOT/fixtures"
chmod +x "$INVERT"

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
if "$INVERT" --selftest; then
  ok "selftest"
else
  bad "selftest" "invert --selftest exited $?"
fi

echo "== refuses to walk =="
if out="$("$INVERT" -C "$FIX" 'user 42 not found' 2>&1)"; then
  bad "-C without stream" "scanned the tree?: $out"
else
  if echo "$out" | grep -qE 'no templates|0 templates ingested'; then
    ok "-C without stream does not walk"
  else
    bad "-C without stream does not walk" "$out"
  fi
fi
if out="$("$INVERT" --templates "$FIX" 'user 42 not found' 2>&1)"; then
  bad "reject dir --templates" "walked: $out"
else
  if echo "$out" | grep -q 'refusing to walk'; then
    ok "reject dir --templates"
  else
    bad "reject dir --templates" "$out"
  fi
fi

echo "== --templates file (raw + grep streams) =="
if out="$("$INVERT" --templates "$FIX/streams/raw.txt" --from raw 'user 42 not found')" \
  && echo "$out" | grep -q 'user {1} not found'; then
  ok "raw template file"
else
  bad "raw template file" "${out:-}"
fi
if out="$("$INVERT" --templates "$FIX/streams/grep.txt" 'Duplicate event ID: evt-99')" \
  && echo "$out" | grep -q 'events.ts:'; then
  ok "grep-format template file"
else
  bad "grep-format template file" "${out:-}"
fi

echo "== rg | invert (policy lives in rg) =="
q() {
  local name="$1"
  local needle="$2"
  local msg="$3"
  shift 3
  local out
  if out="$(rg -n --no-heading "$@" "$FIX" | "$INVERT" --templates - -n 3 "$msg")"; then
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
q "named rust + backticks" "{rest} = diff --git a/foo b/foo" \
  "unparseable \`diff --git\` header: diff --git a/foo b/foo" \
  -g '*.rs' 'format!'
q "two named rust holes" "{display} = src/weird.rs" \
  $'diff --git a/src/weird.rs b/src/weird.rs\n' \
  -g '*.rs' 'format!'
q "python f-string binds uid" "{uid} = 42" \
  "user 42 not found" \
  -g '*.py' 'f"'
q "python host:port holes" "{host} = db.internal" \
  "cannot reach db.internal:5432 after 3 retries" \
  -g '*.py' 'f"'
q "js template binds id" "{id} = evt-99" \
  "Duplicate event ID: evt-99" \
  -g '*.ts' 'Error|TypeError|RangeError'
q "js two-hole template" "{processed} = 1200" \
  "Cannot enqueue event before processed time 1200: 800" \
  -g '*.ts' 'RangeError|enqueue'
q "js exact literal" "src/events.ts:" \
  "Event id must not be empty" \
  -g '*.ts' 'TypeError|empty'
q "swift interpolation binds name" "{name} = Focus" \
  "session started profile=Focus" \
  -g '*.swift' 'Logger|session started'
q "nested swift quotes bind ternary" "{enabled} = enabled" \
  "camera presence enabled" \
  -g '*.swift' 'camera presence'
q "fixture 7-hole binds from" "{from} = focused" \
  "transition focused → idle reason=timeout idle=12s deserted=0 driftRecovered=0 awayRecovered=0" \
  -g '*.swift' 'awayRecovered'
q "go printf numbered holes" "{1} = /tmp/x" \
  "open /tmp/x: permission denied" \
  -g '*.go' 'fmt.Errorf'
q "spaces in path" "file with spaces.rs:" \
  "cannot open strange file: /tmp/a b.txt" \
  -g '*.rs' 'strange'
q "nested secret" "nested/repo/secret.py:" \
  "nested secret key hunter2 leaked" \
  -g '*.py' 'secret'

echo "== rg ignore/glob is the skip policy (not invert) =="
if rg -n --no-heading 'should not be indexed' "$FIX" \
  | "$INVERT" --templates - --extract | grep -q 'should not be indexed'; then
  bad "default rg skips gitignored node_modules" "hidden.js leaked"
else
  ok "default rg skips gitignored node_modules"
fi
if rg -n --no-heading --no-ignore -g '**/hidden.js' 'should not be indexed' "$FIX" \
  | "$INVERT" --templates - --extract | grep -q 'should not be indexed'; then
  ok "rg --no-ignore admits node_modules when asked"
else
  bad "rg --no-ignore admits node_modules when asked" "expected hidden.js template"
fi
if rg -n --no-heading -g '!*.min.js' 'minified decoy' "$FIX" \
  | "$INVERT" --templates - --extract | grep -q 'minified decoy'; then
  bad "rg -g '!*.min.js'" "min.js leaked after exclude glob"
else
  ok "rg -g '!*.min.js' keeps minified decoy out"
fi
if rg -n --no-heading -g '*.min.js' 'minified decoy' "$FIX" \
  | "$INVERT" --templates - --extract | grep -q 'minified decoy'; then
  ok "rg -g '*.min.js' admits minified decoy when asked"
else
  bad "rg -g '*.min.js' admits minified decoy when asked" "expected min.js template"
fi

echo "== --files (rg -l) + slurp source =="
if out="$(rg -l --glob '*.swift' 'Logger' "$FIX" | "$INVERT" --files - \
  'cumulative save failed path=/tmp/c.json error=disk full')" \
  && echo "$out" | grep -q 'log.swift:' \
  && echo "$out" | grep -q 'path={path} error={err}' \
  && echo "$out" | grep -q '{path} = /tmp/c.json' \
  && echo "$out" | grep -q '{err} = disk full'; then
  ok "--files hydrates multiline swift + binds"
else
  bad "--files hydrates multiline swift + binds" "${out:-}"
fi
if out="$("$INVERT" --templates "$FIX/src/log.swift" \
  'cumulative save failed path=/tmp/c.json error=disk full')" \
  && echo "$out" | grep -q 'path={path} error={err}'; then
  ok "--templates source file slurps"
else
  bad "--templates source file slurps" "${out:-}"
fi

echo "== extract round-trip =="
idx="$(rg -n --no-heading -g '*.py' 'f"' "$FIX" | "$INVERT" --templates - --extract)"
if echo "$idx" | grep -q 'user {uid} not found'; then
  ok "extract dumps named templates"
else
  bad "extract dumps named templates" "$idx"
fi
if out="$(echo "$idx" | "$INVERT" --templates - --from index 'user 7 not found')" \
  && echo "$out" | grep -q 'user {uid} not found' \
  && echo "$out" | grep -q '{uid} = 7'; then
  ok "extract | invert --from index binds"
else
  bad "extract | invert --from index binds" "${out:-}"
fi

echo "== dashed message via -e =="
if out="$(rg -n --no-heading -g '*.swift' 'device init' "$FIX" | "$INVERT" --templates - -e "device init failed")" \
  && echo "$out" | grep -q 'log.swift:'; then
  ok "-e message"
else
  bad "-e message" "${out:-}"
fi

echo "== stdin queries + --templates FILE =="
pipe_out="$(
  {
    echo "Compiling invert v0.1.0"
    echo "ERROR [worker] user 7 not found"
    printf '\x1b[31merror:\x1b[0m git diff single file failed: boom\n'
  } | "$INVERT" --templates "$FIX/streams/grep.txt" --any
)"
if echo "$pipe_out" | grep -q 'user.py:' && echo "$pipe_out" | grep -q 'git.rs:'; then
  ok "stdin log strip + multi-message"
else
  bad "stdin log strip + multi-message" "$pipe_out"
fi

echo "== miss exits 1 =="
if "$INVERT" --templates "$FIX/streams/raw.txt" "this message exists nowhere xyzzy-invert" >/dev/null; then
  bad "miss exit" "expected exit 1"
else
  ok "miss exit 1"
fi

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
    | "$INVERT" --templates - -n 5 "$msg")"; then
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
    | "$INVERT" --templates - -q -e 'has_more cannot be true when units is empty'; then
    ok "rg sees untracked tenaoshi and invert matches"
  else
    bad "rg tenaoshi untracked" "rg|invert missed EditPlan.swift"
  fi
fi

echo "== sitbone multiline: auto-open vs --open never =="
if [[ -d "$SIT" ]]; then
  line_out="$(
    rg -n --no-heading -g '*.swift' 'cumulative save failed' "$SIT" \
      | "$INVERT" --templates - -n 3 \
        'cumulative save failed path=/Users/x/Library/cumulative.json error=The file could not be saved'
  )"
  if echo "$line_out" | grep -q 'holes=2' \
    && echo "$line_out" | grep -q 'error='; then
    ok "sitbone cumulative via rg -n (auto-open file)"
  else
    bad "sitbone cumulative via rg -n (auto-open file)" "${line_out:-empty}"
  fi
  never_out="$(
    rg -n --no-heading -g '*.swift' 'cumulative save failed' "$SIT" \
      | "$INVERT" --templates - --open never -n 3 \
        'cumulative save failed path=/Users/x/Library/cumulative.json error=The file could not be saved' \
      || true
  )"
  if echo "$never_out" | grep -q 'holes=2'; then
    bad "--open never should stay 1-hole" "$never_out"
  elif echo "$never_out" | grep -q 'holes=1'; then
    ok "--open never stays a 1-hole fragment"
  else
    bad "--open never fragment" "${never_out:-empty}"
  fi
  files_out="$(
    rg -l -g '*.swift' 'cumulative save failed' "$SIT" \
      | "$INVERT" --files - -n 3 \
        'cumulative save failed path=/Users/x/Library/cumulative.json error=The file could not be saved'
  )"
  if echo "$files_out" | grep -q 'holes=2' && echo "$files_out" | grep -q 'error='; then
    ok "sitbone cumulative via rg -l | --files"
  else
    bad "sitbone cumulative via rg -l | --files" "$files_out"
  fi
fi

echo "== --chdir lets git -C grep hydrate relative paths =="
if [[ -d "$KIZU" ]]; then
  if git -C "$KIZU" grep -n -e 'format!' -- '*.rs' \
    | "$INVERT" --templates - --chdir "$KIZU" -q \
      'git diff single file failed: boom'; then
    ok "git grep format! + --chdir hydrates anyhow! sibling"
  else
    bad "git grep format! + --chdir hydrates anyhow! sibling" "missed"
  fi
  if git -C "$KIZU" grep -n -e 'format!' -- '*.rs' \
    | "$INVERT" --templates - --open never -q \
      'git diff single file failed: boom'; then
    bad "without hydrate, format! grep should miss anyhow!" "unexpected hit"
  else
    ok "without hydrate, git grep format! misses anyhow!"
  fi
fi

echo "== --chdir + relative grep line (fixture) =="
chdir_out="$(
  printf '%s\n' 'src/log.swift:7:        cumulative save failed path=\(path) \' \
    | "$INVERT" --chdir "$FIX" --from grep \
      'cumulative save failed path=/tmp/c.json error=disk full'
)"
if echo "$chdir_out" | grep -q 'path={path} error={err}'; then
  ok "--chdir hydrates relative fixture path"
else
  bad "--chdir hydrates relative fixture path" "$chdir_out"
fi

echo "== dogfood: kizu timestamp prefix (anyhow context) =="
if [[ -d "$KIZU" ]]; then
  pref_out="$(
    rg -n --no-heading -g '*.rs' -g '!target/**' 'failed to spawn' "$KIZU" \
      | "$INVERT" --templates - -n 5 \
        '2026-08-19T23:50:01Z ERROR failed to spawn `git apply --reverse`'
  )" || pref_out=""
  if echo "$pref_out" | grep -q 'src/git/revert.rs:' \
    && echo "$pref_out" | grep -q 'failed to spawn `git apply --reverse`' \
    && echo "$pref_out" | grep -q '2026-08-19T23:50:01Z' \
    && echo "$pref_out" | grep -q 'prefix:'; then
    ok "kizu prefix span reports timestamp leftover"
  else
    bad "kizu prefix span reports timestamp leftover" "${pref_out:-empty}"
  fi
  if rg -n --no-heading -g '*.rs' -g '!target/**' 'failed to spawn' "$KIZU" \
    | "$INVERT" --templates - --exact -q \
      '2026-08-19T23:50:01Z ERROR failed to spawn `git apply --reverse`'; then
    bad "--exact should refuse timestamp prefix" "unexpected hit"
  else
    ok "--exact refuses timestamp prefix"
  fi
fi

echo "== dogfood: sitbone nested quotes (camera ternary) =="
if [[ -d "$SIT" ]]; then
  cam_out="$(
    rg -n --no-heading -g '*.swift' 'camera presence' "$SIT" \
      | "$INVERT" --templates - -n 3 'camera presence enabled'
  )" || cam_out=""
  if echo "$cam_out" | grep -q 'SitboneCore.swift:' \
    && echo "$cam_out" | grep -q '{self.isCameraEnabled} = enabled'; then
    ok "sitbone camera nested quotes bind"
  else
    bad "sitbone camera nested quotes bind" "${cam_out:-empty}"
  fi
fi

echo "== dogfood: sitbone 7-hole Logger line with names =="
if [[ -d "$SIT" ]]; then
  seven_out="$(
    rg -n --no-heading -g '*.swift' 'awayRecovered' "$SIT" \
      | "$INVERT" --templates - -n 5 \
        'transition focused → idle reason=timeout idle=12s deserted=0 driftRecovered=0 awayRecovered=0'
  )" || seven_out=""
  if echo "$seven_out" | grep -q 'SitboneCore.swift:' \
    && echo "$seven_out" | grep -q '{oldPhase.rawValue} = focused' \
    && echo "$seven_out" | grep -q '{newPhase.rawValue} = idle' \
    && echo "$seven_out" | grep -q '{reason.name} = timeout' \
    && echo "$seven_out" | grep -q '{idle} = 12' \
    && echo "$seven_out" | grep -q '{counters.deserted.value} = 0' \
    && echo "$seven_out" | grep -q '{counters.driftRecovered.value} = 0' \
    && echo "$seven_out" | grep -q '{counters.awayRecovered.value} = 0'; then
    ok "sitbone 7-hole binds named interpolations"
  else
    bad "sitbone 7-hole binds named interpolations" "${seven_out:-empty}"
  fi
fi

echo
echo "passed=$pass failed=$fail"
if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
exit 0
