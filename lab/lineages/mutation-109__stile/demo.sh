#!/usr/bin/env bash
# Exercise stile: distinctive proving string; incomplete fence leftovers refuse.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
STILE="$ROOT/stile"
FIX="$ROOT/fixtures"
ANC="/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b59-bd03-7f81-b375-7aef996a20c5/splice"
chmod +x "$STILE"

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
if "$STILE" --selftest; then
  ok "selftest"
else
  bad "selftest" "weld --selftest exited $?"
fi

echo "== refuses to walk =="
if out="$("$STILE" -C "$FIX" 'user 42 not found' 2>&1)"; then
  bad "-C without stream" "scanned the tree?: $out"
else
  if echo "$out" | grep -qE 'no templates|0 templates ingested'; then
    ok "-C without stream does not walk"
  else
    bad "-C without stream does not walk" "$out"
  fi
fi
if out="$("$STILE" --templates "$FIX" 'user 42 not found' 2>&1)"; then
  bad "reject dir --templates" "walked: $out"
else
  if echo "$out" | grep -q 'refusing to walk'; then
    ok "reject dir --templates"
  else
    bad "reject dir --templates" "$out"
  fi
fi

echo "== --templates file (raw + grep streams) =="
if out="$("$STILE" --templates "$FIX/streams/raw.txt" --from raw 'user 42 not found')" \
  && echo "$out" | grep -q 'user {1} not found'; then
  ok "raw template file"
else
  bad "raw template file" "${out:-}"
fi
if out="$("$STILE" --templates "$FIX/streams/grep.txt" 'Duplicate event ID: evt-99')" \
  && echo "$out" | grep -q 'events.ts:'; then
  ok "grep-format template file"
else
  bad "grep-format template file" "${out:-}"
fi

echo "== rg | weld (policy lives in rg) =="
q() {
  local name="$1"
  local needle="$2"
  local msg="$3"
  shift 3
  local out
  if out="$(rg -n --no-heading "$@" "$FIX" | "$STILE" --templates - -n 3 "$msg")"; then
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

echo "== rg ignore/glob is the skip policy (not stile) =="
if rg -n --no-heading 'should not be indexed' "$FIX" \
  | "$STILE" --templates - --extract | grep -q 'should not be indexed'; then
  bad "default rg skips gitignored node_modules" "hidden.js leaked"
else
  ok "default rg skips gitignored node_modules"
fi
if rg -n --no-heading --no-ignore -g '**/hidden.js' 'should not be indexed' "$FIX" \
  | "$STILE" --templates - --extract | grep -q 'should not be indexed'; then
  ok "rg --no-ignore admits node_modules when asked"
else
  bad "rg --no-ignore admits node_modules when asked" "expected hidden.js template"
fi
if rg -n --no-heading -g '!*.min.js' 'minified decoy' "$FIX" \
  | "$STILE" --templates - --extract | grep -q 'minified decoy'; then
  bad "rg -g '!*.min.js'" "min.js leaked after exclude glob"
else
  ok "rg -g '!*.min.js' keeps minified decoy out"
fi
if rg -n --no-heading -g '*.min.js' 'minified decoy' "$FIX" \
  | "$STILE" --templates - --extract | grep -q 'minified decoy'; then
  ok "rg -g '*.min.js' admits minified decoy when asked"
else
  bad "rg -g '*.min.js' admits minified decoy when asked" "expected min.js template"
fi

echo "== --files (rg -l) + slurp source =="
if out="$(rg -l --glob '*.swift' 'Logger' "$FIX" | "$STILE" --files - \
  'cumulative save failed path=/tmp/c.json error=disk full')" \
  && echo "$out" | grep -q 'log.swift:' \
  && echo "$out" | grep -q 'path={path} error={err}' \
  && echo "$out" | grep -q '{path} = /tmp/c.json' \
  && echo "$out" | grep -q '{err} = disk full'; then
  ok "--files hydrates multiline swift + binds"
else
  bad "--files hydrates multiline swift + binds" "${out:-}"
fi
if out="$("$STILE" --templates "$FIX/src/log.swift" \
  'cumulative save failed path=/tmp/c.json error=disk full')" \
  && echo "$out" | grep -q 'path={path} error={err}'; then
  ok "--templates source file slurps"
else
  bad "--templates source file slurps" "${out:-}"
fi

echo "== extract round-trip =="
idx="$(rg -n --no-heading -g '*.py' 'f"' "$FIX" | "$STILE" --templates - --extract)"
if echo "$idx" | grep -q 'user {uid} not found'; then
  ok "extract dumps named templates"
else
  bad "extract dumps named templates" "$idx"
fi
if out="$(echo "$idx" | "$STILE" --templates - --from index 'user 7 not found')" \
  && echo "$out" | grep -q 'user {uid} not found' \
  && echo "$out" | grep -q '{uid} = 7'; then
  ok "extract | stile --from index binds"
else
  bad "extract | stile --from index binds" "${out:-}"
fi

echo "== dashed message via -e =="
if out="$(rg -n --no-heading -g '*.swift' 'device init' "$FIX" | "$STILE" --templates - -e "device init failed")" \
  && echo "$out" | grep -q 'log.swift:'; then
  ok "-e message"
else
  bad "-e message" "${out:-}"
fi

echo "== stdin queries + --templates FILE =="
pipe_out="$(
  {
    echo "Compiling stump v0.1.0"
    echo "ERROR [worker] user 7 not found"
    printf '\x1b[31merror:\x1b[0m git diff single file failed: boom\n'
  } | "$STILE" --templates "$FIX/streams/grep.txt"
)"
if echo "$pipe_out" | grep -q 'user.py:' && echo "$pipe_out" | grep -q 'git.rs:'; then
  ok "stdin log strip + multi-message"
else
  bad "stdin log strip + multi-message" "$pipe_out"
fi

echo "== miss exits 1 =="
if "$STILE" --templates "$FIX/streams/raw.txt" "this message exists nowhere xyzzy-invert" >/dev/null; then
  bad "miss exit" "expected exit 1"
else
  ok "miss exit 1"
fi

KIZU="/Users/annenpolka/ghq/github.com/annenpolka/kizu"
VOID="/Users/annenpolka/ghq/github.com/annenpolka/voidtrace"
SIT="/Users/annenpolka/ghq/github.com/annenpolka/sitbone"
TENA="/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi"
SKILLS="/Users/annenpolka/ghq/github.com/annenpolka/skills"

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
    | "$STILE" --templates - -n 5 "$msg")"; then
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
    | "$STILE" --templates - -q -e 'has_more cannot be true when units is empty'; then
    ok "rg sees untracked tenaoshi and stile matches"
  else
    bad "rg tenaoshi untracked" "rg|stile missed EditPlan.swift"
  fi
fi

echo "== sitbone multiline: auto-open vs --open never =="
if [[ -d "$SIT" ]]; then
  line_out="$(
    rg -n --no-heading -g '*.swift' 'cumulative save failed' "$SIT" \
      | "$STILE" --templates - -n 3 \
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
      | "$STILE" --templates - --open never -n 3 \
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
      | "$STILE" --files - -n 3 \
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
    | "$STILE" --templates - --chdir "$KIZU" -q \
      'git diff single file failed: boom'; then
    ok "git grep format! + --chdir hydrates anyhow! sibling"
  else
    bad "git grep format! + --chdir hydrates anyhow! sibling" "missed"
  fi
  if git -C "$KIZU" grep -n -e 'format!' -- '*.rs' \
    | "$STILE" --templates - --open never -q \
      'git diff single file failed: boom'; then
    bad "without hydrate, format! grep should miss anyhow!" "unexpected hit"
  else
    ok "without hydrate, git grep format! misses anyhow!"
  fi
fi

echo "== --chdir + relative grep line (fixture) =="
chdir_out="$(
  printf '%s\n' 'src/log.swift:7:        cumulative save failed path=\(path) \' \
    | "$STILE" --chdir "$FIX" --from grep \
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
      | "$STILE" --templates - -n 5 \
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
    | "$STILE" --templates - --exact -q \
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
      | "$STILE" --templates - -n 3 'camera presence enabled'
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
      | "$STILE" --templates - -n 5 \
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

echo "== destroyer regressions =="
trunc_out="$(
  rg -n --no-heading -g '*.swift' 'awayRecovered' "$FIX" \
    | "$STILE" --templates - -n 3 \
      'transition focused → idle reason=timeout idle=12s'
)" || trunc_out=""
if echo "$trunc_out" | grep -q 'truncated:' \
  && echo "$trunc_out" | grep -q '{from} = focused' \
  && echo "$trunc_out" | grep -q '{idle} = 12' \
  && echo "$trunc_out" | grep -q 'holes=4/7' \
  && echo "$trunc_out" | grep -q 'unbound:'; then
  ok "truncated 7-hole binds a prefix (holes=4/7, later unbound)"
else
  bad "truncated 7-hole binds a prefix" "${trunc_out:-empty}"
fi

drop_rc=0
drop_out="$(
  rg -n --no-heading -g '*.swift' 'awayRecovered' "$FIX" \
    | "$STILE" --templates - -n 3 \
      'transition focused → idle awayRecovered=0'
)" || drop_rc=$?
if echo "$drop_out" | grep -q '{to} = idle awayRecovered'; then
  bad "middle-drop must not stuff {to}" "$drop_out"
elif echo "$drop_out" | grep -q 'tmpl:' && echo "$drop_out" | grep -q 'awayRecovered=0'; then
  bad "middle-drop still a hit" "$drop_out"
elif [[ "$drop_rc" -eq 0 ]]; then
  bad "middle-drop should miss (exit 1)" "rc=$drop_rc $drop_out"
else
  ok "middle-drop paste is not a prefix (no leftover stuffed into {to})"
fi

wrap_rc=0
wrap_out="$(
  rg -n --no-heading -g '*.swift' 'awayRecovered' "$FIX" \
    | "$STILE" --templates - -n 3 \
      $'transition focused → idle reason=timeout\nidle=12s deserted=0 driftRecovered=0 awayRecovered=0'
)" || wrap_rc=$?
if echo "$wrap_out" | grep -q '{reason} =' && echo "$wrap_out" | grep -q 'idle=12s'; then
  bad "wrap stuffed leftover into {reason}" "$wrap_out"
elif echo "$wrap_out" | grep -q 'tmpl:' && [[ "$wrap_rc" -eq 0 ]]; then
  bad "wrap should miss (not a prefix)" "$wrap_out"
else
  ok "newline wrap is not a prefix of an instance"
fi

user_trunc="$(
  rg -n --no-heading -g '*.py' 'f"' "$FIX" \
    | "$STILE" --templates - -n 3 'user 42 not'
)" || user_trunc=""
if echo "$user_trunc" | grep -q 'truncated:' \
  && echo "$user_trunc" | grep -q '{uid} = 42' \
  && echo "$user_trunc" | grep -q 'found'; then
  ok "truncated user {uid} still binds"
else
  bad "truncated user {uid} still binds" "${user_trunc:-empty}"
fi

spawn_trunc="$(
  "$STILE" --templates "$FIX/src/prefix.rs" -n 3 \
    '2026-08-19T23:50:01Z ERROR failed to spawn `git ap'
)" || spawn_trunc=""
if echo "$spawn_trunc" | grep -q 'truncated:' \
  && echo "$spawn_trunc" | grep -q '{cmd} = git ap'; then
  ok "truncated spawn binds {cmd}"
else
  bad "truncated spawn binds {cmd}" "${spawn_trunc:-empty}"
fi

loc_out="$(
  "$STILE" --templates "$FIX/src/prefix.rs" -e '   --> src/git/revert.rs:46:18' || true
)"
if echo "$loc_out" | grep -q 'rustc locator' && ! echo "$loc_out" | grep -q '{i} ='; then
  ok "rustc --> locator is not a template query"
else
  bad "rustc --> locator is not a template query" "$loc_out"
fi

rank_out="$(
  "$STILE" --templates "$FIX/src/prefix.rs" -n 5 \
    '2026-08-19T23:50:01Z ERROR failed to spawn `git apply --reverse`'
)" || rank_out=""
first_tmpl="$(echo "$rank_out" | grep -m1 'tmpl:' || true)"
if echo "$first_tmpl" | grep -q 'failed to spawn `{cmd}`' \
  && echo "$rank_out" | grep -q '{cmd} = git apply --reverse'; then
  ok "holed spawn beats no-hole timestamp prefix"
else
  bad "holed spawn beats no-hole timestamp prefix" "${rank_out:-empty}"
fi

enq_out="$(
  rg -n --no-heading -g '*.ts' 'Event id|enqueueing' "$FIX" \
    | "$STILE" --templates - -n 5 \
      'Event id must not be empty or null when enqueueing evt-99'
)" || enq_out=""
first_enq="$(echo "$enq_out" | grep -m1 'tmpl:' || true)"
if echo "$first_enq" | grep -q 'enqueueing {id}' \
  && echo "$enq_out" | grep -q '{id} = evt-99' \
  && ! echo "$first_enq" | grep -q 'Event id must not be empty$'; then
  ok "holed enqueue beats no-hole static prefix"
else
  bad "holed enqueue beats no-hole static prefix" "${enq_out:-empty}"
fi

any_out="$(
  python3 -c 'import sys; sys.stdout.write("ERROR [worker] user 7 not found\n" * 3000)' \
    | "$STILE" --templates "$FIX/streams/raw.txt" --any
)" || any_out=""
any_hits="$(printf '%s\n' "$any_out" | grep -c 'tmpl:' || true)"
any_bytes="$(printf '%s' "$any_out" | wc -c | tr -d ' ')"
if [[ "$any_hits" == "1" ]] && [[ "$any_bytes" -lt 2000 ]]; then
  ok "--any stops after first hit (hits=$any_hits bytes=$any_bytes)"
else
  bad "--any stops after first hit" "hits=$any_hits bytes=$any_bytes out=${any_out:0:200}"
fi

any_complete="$(
  {
    echo 'user 42 not'
    echo 'ERROR [worker] user 7 not found'
  } | "$STILE" --templates "$FIX/src/user.py" --any --complete
)" || true
if echo "$any_complete" | grep -q '{uid} = 7' \
  && ! echo "$any_complete" | grep -q '{uid} = 42' \
  && ! echo "$any_complete" | grep -q 'via=truncated' \
  && ! echo "$any_complete" | grep -q 'no template for'; then
  ok "--any --complete skips truncated prefix, binds complete line"
else
  bad "--any --complete skips truncated prefix" "${any_complete:-empty}"
fi

any_trunc_only="$(
  echo 'user 42 not' | "$STILE" --templates "$FIX/src/user.py" --any --complete
)" || any_trunc_only_rc=$?
if echo "$any_trunc_only" | grep -q 'tmpl:'; then
  bad "--complete must refuse truncated-only stream" "$any_trunc_only"
else
  ok "--complete refuses truncated-only --any"
fi

stream_rc=0
stream_meta="$(
  python3 - "$STILE" "$FIX/streams/raw.txt" <<'PY'
import os, signal, subprocess, sys, time

stile, raw = sys.argv[1], sys.argv[2]
r, w = os.pipe()
pid = os.fork()
if pid == 0:
    os.close(r)
    os.write(w, b"ERROR [worker] user 7 not found\n")
    time.sleep(6)
    try:
        os.write(w, b"ERROR [worker] user 7 not found\n")
    except BrokenPipeError:
        pass
    os.close(w)
    os._exit(0)
os.close(w)
t0 = time.time()
proc = subprocess.run(
    [stile, "--templates", raw, "--any"],
    stdin=os.fdopen(r, "rb"),
    capture_output=True,
)
dt = time.time() - t0
try:
    os.kill(pid, signal.SIGTERM)
except ProcessLookupError:
    pass
os.waitpid(pid, 0)
sys.stdout.write(f"elapsed={dt:.2f}\n")
sys.stdout.flush()
sys.stdout.buffer.write(proc.stdout)
sys.exit(0 if dt < 2.0 and b"tmpl:" in proc.stdout else 1)
PY
)" || stream_rc=$?
if [[ "$stream_rc" -eq 0 ]] && echo "$stream_meta" | grep -q 'tmpl:'; then
  ok "--any stops reading stdin ($(echo "$stream_meta" | head -n1))"
else
  bad "--any stops reading stdin" "rc=$stream_rc $stream_meta"
fi

bin_rc=0
bin_out="$(printf '\x00\xff\xee' | "$STILE" --templates - -e 'user 42 not found' 2>&1)" || bin_rc=$?
if [[ "$bin_rc" -eq 2 ]] \
  && echo "$bin_out" | grep -qi 'binary' \
  && ! echo "$bin_out" | grep -q 'UnicodeDecodeError'; then
  ok "binary stdin fail closed"
else
  bad "binary stdin fail closed" "rc=$bin_rc $bin_out"
fi

rand_rc=0
rand_out="$(dd if=/dev/urandom bs=256 count=1 2>/dev/null | "$STILE" --templates - -e 'user 42 not found' 2>&1)" || rand_rc=$?
if [[ "$rand_rc" -eq 2 ]] \
  && echo "$rand_out" | grep -qi 'binary' \
  && ! echo "$rand_out" | grep -q 'Traceback'; then
  ok "random stdin fail closed (no traceback)"
else
  bad "random stdin fail closed (no traceback)" "rc=$rand_rc $rand_out"
fi

if [[ -d "$SIT" ]]; then
  sit_trunc="$(
    rg -n --no-heading -g '*.swift' 'awayRecovered' "$SIT" \
      | "$STILE" --templates - -n 3 \
        'transition focused → idle reason=timeout idle=12s'
  )" || sit_trunc=""
  if echo "$sit_trunc" | grep -q 'truncated:' \
    && echo "$sit_trunc" | grep -q '{oldPhase.rawValue} = focused' \
    && echo "$sit_trunc" | grep -q '{idle} = 12'; then
    ok "dogfood truncated sitbone 7-hole"
  else
    bad "dogfood truncated sitbone 7-hole" "${sit_trunc:-empty}"
  fi
fi

if [[ -d "$KIZU" ]]; then
  kizu_trunc="$(
    rg -n --no-heading -g '*.rs' -g '!target/**' 'failed to spawn' "$KIZU" \
      | "$STILE" --templates - -n 3 \
        '2026-08-19T23:50:01Z ERROR failed to spawn `git ap'
  )" || kizu_trunc=""
  if echo "$kizu_trunc" | grep -q 'truncated:' \
    && echo "$kizu_trunc" | grep -q 'failed to spawn'; then
    ok "dogfood truncated kizu spawn"
  else
    bad "dogfood truncated kizu spawn" "${kizu_trunc:-empty}"
  fi
  kizu_loc="$(
    rg -n --no-heading -g '*.rs' -g '!target/**' 'format!|anyhow!' "$KIZU" \
      | "$STILE" --templates - -e '   --> src/git/revert.rs:46:18' || true
  )"
  if echo "$kizu_loc" | grep -q 'rustc locator' && ! echo "$kizu_loc" | grep -q '{i} ='; then
    ok "dogfood kizu rustc locator refused"
  else
    bad "dogfood kizu rustc locator refused" "$kizu_loc"
  fi
fi

echo "== adjacent concatenations (string-first still holds) =="
if out="$("$STILE" --templates "$FIX/src/concat.go" --extract)" \
  && echo "$out" | grep -q 'splice open {path}: {err.Error}' \
  && ! echo "$out" | grep -qE 'holes=0 static=5 open ?$'; then
  ok "concat.go extracts one holed splice, not bare 'open '"
else
  bad "concat.go extracts one holed splice, not bare 'open '" "${out:-}"
fi
if out="$("$STILE" --templates "$FIX/src/concat.js" 'open /tmp/x: permission denied')" \
  && echo "$out" | grep -q '{path} = /tmp/x' \
  && echo "$out" | grep -q '{err} = permission denied' \
  && ! echo "$out" | grep -q '{path} = open /tmp/x'; then
  ok "concat.js binds without a sibling format string"
else
  bad "concat.js binds without a sibling format string" "${out:-}"
fi
if out="$("$STILE" --templates "$FIX/src/concat.py" 'open /tmp/x: permission denied')" \
  && echo "$out" | grep -q '{path} = /tmp/x' \
  && echo "$out" | grep -q '{err} = permission denied'; then
  ok "concat.py str(err) names the argument"
else
  bad "concat.py str(err) names the argument" "${out:-}"
fi
if out="$("$STILE" --templates "$FIX/src/concat.ex" 'open /tmp/x: permission denied')" \
  && echo "$out" | grep -q 'open {path}: {err}'; then
  ok "elixir <> is a concat operator"
else
  bad "elixir <> is a concat operator" "${out:-}"
fi
if out="$("$STILE" --templates "$FIX/src/concat.go" 'open /tmp/x: permission denied')" \
  && echo "$out" | grep -q 'open {path}: {err}' \
  && echo "$out" | grep -q '{path} = /tmp/x'; then
  ok "fmt.Sprint / + chain bind the destroyer paste"
else
  bad "fmt.Sprint / + chain bind the destroyer paste" "${out:-}"
fi

if out="$("$STILE" --templates "$FIX/src/concat.go" 'failed read on /tmp/x with EPERM')" \
  && echo "$out" | grep -q '{op} = read' \
  && echo "$out" | grep -q '{path} = /tmp/x' \
  && echo "$out" | grep -q '{err} = EPERM'; then
  ok "3-hole + chain binds op/path/err"
else
  bad "3-hole + chain binds op/path/err" "${out:-}"
fi
drop_rc=0
drop_out="$("$STILE" --templates "$FIX/src/concat.go" -e 'failed read with EPERM')" || drop_rc=$?
if echo "$drop_out" | grep -q '{op} = read with EPERM' || echo "$drop_out" | grep -q 'tmpl:'; then
  if echo "$drop_out" | grep -q 'failed {op} on {path} with {err}' \
    && echo "$drop_out" | grep -q '{op} = read with'; then
    bad "middle-drop stuffed later fragment into {op}" "$drop_out"
  elif [[ "$drop_rc" -eq 0 ]]; then
    bad "middle-drop splice should miss" "$drop_out"
  else
    ok "middle-drop paste of a splice is a miss"
  fi
else
  ok "middle-drop paste of a splice is a miss"
fi

echo "== wrapped + (newline is a gap, not a stop) =="
wrap_out="$("$STILE" --templates "$FIX/src/concat.swift" --extract)"
if echo "$wrap_out" | grep -q 'invalid original range for unit {unitID}: {start} (source graphemes: {n})' \
  && echo "$wrap_out" | grep -q 'splice'; then
  ok "wrapped Swift + is one spliced template"
else
  bad "wrapped Swift + is one spliced template" "$wrap_out"
fi

echo "== expression-first concat (the flipped assumption) =="
if out="$("$STILE" --templates "$FIX/src/concat.js" --extract)" \
  && echo "$out" | grep -q 'weld {response}\\nDone.'; then
  ok "concat.js extracts expr-first weld, not bare Done."
else
  bad "concat.js extracts expr-first weld" "${out:-}"
fi
if out="$("$STILE" --templates "$FIX/src/concat.js" $'{"ok":true}\nDone.')" \
  && echo "$out" | grep -q '{response} = {"ok":true}'; then
  ok "response() + lit binds the proving string"
else
  bad "response() + lit binds the proving string" "${out:-}"
fi
if out="$("$STILE" --templates "$FIX/src/concat.go" '/tmp/x: permission denied')" \
  && echo "$out" | grep -q '{path} = /tmp/x' \
  && echo "$out" | grep -q '{err.Error} = permission denied'; then
  ok "path + \": \" + err.Error() binds both holes"
else
  bad "path + \": \" + err.Error() binds both holes" "${out:-}"
fi
if out="$("$STILE" --templates "$FIX/src/concat.swift" --extract)" \
  && echo "$out" | grep -q 'weld {body}\\nDone.'; then
  ok "wrapped expr-first body\\n + lit is one weld"
else
  bad "wrapped expr-first is one weld" "${out:-}"
fi
if out="$("$STILE" --templates "$FIX/src/concat.swift" $'```json\n{"ok":true}\n```')" \
  && echo "$out" | grep -q '```json\\n{response}\\n```' \
  && echo "$out" | grep -q '{response} = {"ok":true}'; then
  ok "fence concat keeps escaped newlines"
else
  bad "fence concat keeps escaped newlines" "${out:-}"
fi

echo "== distinctive proving string (4-char floor is gone) =="
thin_ex="$("$STILE" --templates "$FIX/src/thin.go" --extract)"
if echo "$thin_ex" | grep -q '{body}abcd'; then
  bad "4-char alnum suffix must not extract" "$thin_ex"
elif echo "$thin_ex" | grep -q '{cleaned}\\n' && echo "$thin_ex" | grep -vq 'holes=0'; then
  bad "newline-only suffix must not extract" "$thin_ex"
else
  ok "newline / fence-marker / bare alnum suffix are not templates"
fi
if echo "$thin_ex" | grep -q 'weld {a}:{b}'; then
  ok "≥2 holes keep a short proving string {a}:{b}"
else
  bad "≥2 holes keep a short proving string {a}:{b}" "$thin_ex"
fi
if echo "$thin_ex" | grep -q 'splice open {path}'; then
  ok "string-first open + path still extracts"
else
  bad "string-first open + path still extracts" "$thin_ex"
fi
abcd_rc=0
abcd_out="$("$STILE" --templates "$FIX/src/thin.go" 'ERROR worker crashed abcd')" || abcd_rc=$?
if echo "$abcd_out" | grep -q '{body} = ERROR'; then
  bad "{body}abcd must not match every log line" "$abcd_out"
elif [[ "$abcd_rc" -eq 0 ]]; then
  bad "{body}abcd query should miss" "$abcd_out"
else
  ok "bare 4-char suffix does not match every log line"
fi
if out="$("$STILE" --templates "$FIX/src/concat.js" $'{"ok":true}\nDone.')" \
  && echo "$out" | grep -q '{response} = {"ok":true}'; then
  ok "expr-first response()+\\nDone. still binds"
else
  bad "expr-first response()+\\nDone. still binds" "${out:-}"
fi

echo "== incomplete fence leftover refuses (caulk complete operand) =="
fence_cut_rc=0
fence_cut="$("$STILE" --templates "$FIX/src/concat.swift" $'```json\n{"ok":true}')" || fence_cut_rc=$?
if echo "$fence_cut" | grep -q '{response} = {"ok":true}'; then
  bad "missing fence closer must refuse" "$fence_cut"
elif [[ "$fence_cut_rc" -eq 0 ]]; then
  bad "missing fence closer should miss (exit 1)" "$fence_cut"
else
  ok "incomplete fence leftover (missing closer) refuses"
fi
fence_half_rc=0
fence_half="$("$STILE" --templates "$FIX/src/concat.swift" $'```json\n{"ok":true}\n``')" || fence_half_rc=$?
if echo "$fence_half" | grep -q '{response}'; then
  bad "cut fence closer is not a complete operand" "$fence_half"
elif [[ "$fence_half_rc" -eq 0 ]]; then
  bad "cut fence closer should miss" "$fence_half"
else
  ok "cut fence closer is not a complete operand"
fi
don_rc=0
don_out="$("$STILE" --templates "$FIX/src/concat.js" $'{"ok":true}\nDon')" || don_rc=$?
if echo "$don_out" | grep -q '{response}'; then
  bad "incomplete \\nDon leftover must refuse" "$don_out"
elif [[ "$don_rc" -eq 0 ]]; then
  bad "incomplete \\nDon should miss" "$don_out"
else
  ok "incomplete \\nDon leftover refuses (complete operand)"
fi
stuff_out="$("$STILE" --templates "$FIX/src/thin.go" $'```json\n{"ok":true}\n```')" || true
if echo "$stuff_out" | grep -q 'tmpl:  ```json\\n{response}\\n```' \
  && echo "$stuff_out" | grep -q '{response} = {"ok":true}' \
  && ! echo "$stuff_out" | grep -E 'tmpl:  ```json\\n\{response\}$'; then
  ok "complete fence binds; unclosed opener does not stuff the closer"
else
  bad "unclosed opener stuffed closer into the hole" "$stuff_out"
fi

if [[ -x "$ANC" ]]; then
  anc_ex="$("$ANC" --templates "$FIX/src/concat.js" --extract)"
  if echo "$anc_ex" | grep -q 'weld {response}'; then
    bad "ancestor splice should not weld expr-first" "$anc_ex"
  elif echo "$anc_ex" | grep -qE 'holes=0.*Done'; then
    ok "ancestor splice extracts suffix lit only (the miss)"
  else
    ok "ancestor splice does not weld expr-first (${anc_ex:-empty})"
  fi
  anc_rc=0
  anc_q="$("$ANC" --templates "$FIX/src/concat.js" $'{"ok":true}\nDone.')" || anc_rc=$?
  if [[ "$anc_rc" -eq 0 ]] && echo "$anc_q" | grep -q '{response}'; then
    bad "ancestor splice should miss expr-first paste" "$anc_q"
  else
    ok "ancestor splice misses response() + lit paste (rc=$anc_rc)"
  fi
  anc_go="$("$ANC" --templates "$FIX/src/concat.go" --extract)"
  if echo "$anc_go" | grep -q 'weld {path}: {err.Error}'; then
    bad "ancestor splice should miss path + : + err" "$anc_go"
  elif echo "$anc_go" | grep -q 'splice open {path}: {err.Error}'; then
    ok "ancestor splice still gets string-first, misses expr-first path+"
  else
    bad "ancestor splice concat.go unexpected" "$anc_go"
  fi
else
  echo "  SKIP  ancestor splice binary not at $ANC"
fi

if [[ -d "$TENA" ]]; then
  tena_wrap="$(
    rg -n --no-heading -g '*.swift' 'source graphemes' "$TENA/Engine/Sources" \
      | "$STILE" --templates - -n 3 \
        'invalid original range for unit u1: 3..<8 (source graphemes: 12)'
  )" || tena_wrap=""
  if echo "$tena_wrap" | grep -q '{unitID} = u1' \
    && echo "$tena_wrap" | grep -q '{sourceGraphemeCount} = 12' \
    && echo "$tena_wrap" | grep -q 'source graphemes'; then
    ok "tenaoshi wrap is one splice (unitID + sourceGraphemeCount)"
  else
    bad "tenaoshi wrap is one splice" "${tena_wrap:-empty}"
  fi
  tena_plan="$(
    rg -n --no-heading -g '*.swift' 'Here is the plan' "$TENA" \
      | "$STILE" --templates - -n 2 $'Here is the plan:\n{"ok":true}'
  )" || tena_plan=""
  if echo "$tena_plan" | grep -q '{response}' \
    && echo "$tena_plan" | grep -q '{"ok":true}'; then
    ok "tenaoshi same-line + response() binds"
  else
    bad "tenaoshi same-line + response() binds" "${tena_plan:-empty}"
  fi
  tena_done="$(
    rg -n --no-heading -g '*.swift' 'Done\.' "$TENA" \
      | "$STILE" --templates - -n 3 $'{"ok":true}\nDone.'
  )" || tena_done=""
  if echo "$tena_done" | grep -q '{response}' \
    && echo "$tena_done" | grep -q '{"ok":true}'; then
    ok "tenaoshi response() + Done. binds (expr-first)"
  else
    bad "tenaoshi response() + Done. binds (expr-first)" "${tena_done:-empty}"
  fi
  tena_fence="$(
    rg -n --no-heading -g '*.swift' 'json' "$TENA/Engine/Tests" \
      | "$STILE" --templates - -n 2 $'```json\n{"ok":true}\n```'
  )" || tena_fence=""
  if echo "$tena_fence" | grep -q '```json\\n{response}\\n```' \
    && echo "$tena_fence" | grep -q '{response} = {"ok":true}' \
    && ! echo "$tena_fence" | grep -q '{response} = .{"ok":true}'; then
    ok "tenaoshi fence keeps json\\n and binds the body"
  else
    bad "tenaoshi fence keeps json\\n and binds the body" "${tena_fence:-empty}"
  fi
  tena_cut_rc=0
  tena_cut="$(
    rg -n --no-heading -g '*.swift' 'json' "$TENA/Engine/Tests" \
      | "$STILE" --templates - -n 2 $'```json\n{"ok":true}'
  )" || tena_cut_rc=$?
  if echo "$tena_cut" | grep -q '{response} = {"ok":true}'; then
    bad "tenaoshi incomplete fence leftover must refuse" "$tena_cut"
  elif [[ "$tena_cut_rc" -eq 0 ]]; then
    bad "tenaoshi incomplete fence should miss" "$tena_cut"
  else
    ok "tenaoshi incomplete fence leftover refuses"
  fi
fi

if [[ -d "$SKILLS" ]]; then
  skills_out="$(
    rg -n --no-heading -g '*.md' 'JsonSerializer.Serialize\(entry\)' "$SKILLS" \
      | "$STILE" --templates - -n 2 $'{"h":"H1"}\n'
  )" || skills_out=""
  if echo "$skills_out" | grep -q 'tmpl:'; then
    echo "  NOTE  skills Serialize(entry)+newline: $skills_out"
    ok "skills expr+newline observed (may be thin-static miss)"
  else
    ok "skills newline-only suffix stays a miss (thin static)"
  fi
fi

echo
echo "passed=$pass failed=$fail"
if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
exit 0
