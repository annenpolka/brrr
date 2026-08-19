#!/usr/bin/env bash
# Exercise lede as a filter: prefix-of-instance inverse printf, named holes.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
LEDE="$ROOT/lede"
FIX="$ROOT/fixtures"
chmod +x "$LEDE"

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
if "$LEDE" --selftest; then
  ok "selftest"
else
  bad "selftest" "lede --selftest exited $?"
fi

echo "== refuses to walk =="
if out="$("$LEDE" -C "$FIX" 'user 42 not found' 2>&1)"; then
  bad "-C without stream" "scanned the tree?: $out"
else
  if echo "$out" | grep -qE 'no templates|0 templates ingested'; then
    ok "-C without stream does not walk"
  else
    bad "-C without stream does not walk" "$out"
  fi
fi
if out="$("$LEDE" --templates "$FIX" 'user 42 not found' 2>&1)"; then
  bad "reject dir --templates" "walked: $out"
else
  if echo "$out" | grep -q 'refusing to walk'; then
    ok "reject dir --templates"
  else
    bad "reject dir --templates" "$out"
  fi
fi

echo "== --templates file (raw + grep streams) =="
if out="$("$LEDE" --templates "$FIX/streams/raw.txt" --from raw 'user 42 not found')" \
  && echo "$out" | grep -q 'user {1} not found'; then
  ok "raw template file"
else
  bad "raw template file" "${out:-}"
fi
if out="$("$LEDE" --templates "$FIX/streams/grep.txt" 'Duplicate event ID: evt-99')" \
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
  if out="$(rg -n --no-heading "$@" "$FIX" | "$LEDE" --templates - -n 3 "$msg")"; then
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
  | "$LEDE" --templates - --extract | grep -q 'should not be indexed'; then
  bad "default rg skips gitignored node_modules" "hidden.js leaked"
else
  ok "default rg skips gitignored node_modules"
fi
if rg -n --no-heading --no-ignore -g '**/hidden.js' 'should not be indexed' "$FIX" \
  | "$LEDE" --templates - --extract | grep -q 'should not be indexed'; then
  ok "rg --no-ignore admits node_modules when asked"
else
  bad "rg --no-ignore admits node_modules when asked" "expected hidden.js template"
fi
if rg -n --no-heading -g '!*.min.js' 'minified decoy' "$FIX" \
  | "$LEDE" --templates - --extract | grep -q 'minified decoy'; then
  bad "rg -g '!*.min.js'" "min.js leaked after exclude glob"
else
  ok "rg -g '!*.min.js' keeps minified decoy out"
fi
if rg -n --no-heading -g '*.min.js' 'minified decoy' "$FIX" \
  | "$LEDE" --templates - --extract | grep -q 'minified decoy'; then
  ok "rg -g '*.min.js' admits minified decoy when asked"
else
  bad "rg -g '*.min.js' admits minified decoy when asked" "expected min.js template"
fi

echo "== --files (rg -l) + slurp source =="
if out="$(rg -l --glob '*.swift' 'Logger' "$FIX" | "$LEDE" --files - \
  'cumulative save failed path=/tmp/c.json error=disk full')" \
  && echo "$out" | grep -q 'log.swift:' \
  && echo "$out" | grep -q 'path={path} error={err}' \
  && echo "$out" | grep -q '{path} = /tmp/c.json' \
  && echo "$out" | grep -q '{err} = disk full'; then
  ok "--files hydrates multiline swift + binds"
else
  bad "--files hydrates multiline swift + binds" "${out:-}"
fi
if out="$("$LEDE" --templates "$FIX/src/log.swift" \
  'cumulative save failed path=/tmp/c.json error=disk full')" \
  && echo "$out" | grep -q 'path={path} error={err}'; then
  ok "--templates source file slurps"
else
  bad "--templates source file slurps" "${out:-}"
fi

echo "== extract round-trip =="
idx="$(rg -n --no-heading -g '*.py' 'f"' "$FIX" | "$LEDE" --templates - --extract)"
if echo "$idx" | grep -q 'user {uid} not found'; then
  ok "extract dumps named templates"
else
  bad "extract dumps named templates" "$idx"
fi
if out="$(echo "$idx" | "$LEDE" --templates - --from index 'user 7 not found')" \
  && echo "$out" | grep -q 'user {uid} not found' \
  && echo "$out" | grep -q '{uid} = 7'; then
  ok "extract | invert --from index binds"
else
  bad "extract | invert --from index binds" "${out:-}"
fi

echo "== dashed message via -e =="
if out="$(rg -n --no-heading -g '*.swift' 'device init' "$FIX" | "$LEDE" --templates - -e "device init failed")" \
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
  } | "$LEDE" --templates "$FIX/streams/grep.txt"
)"
if echo "$pipe_out" | grep -q 'user.py:' && echo "$pipe_out" | grep -q 'git.rs:'; then
  ok "stdin log strip + multi-message"
else
  bad "stdin log strip + multi-message" "$pipe_out"
fi

echo "== miss exits 1 =="
if "$LEDE" --templates "$FIX/streams/raw.txt" "this message exists nowhere xyzzy-invert" >/dev/null; then
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
    | "$LEDE" --templates - -n 5 "$msg")"; then
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
    | "$LEDE" --templates - -q -e 'has_more cannot be true when units is empty'; then
    ok "rg sees untracked tenaoshi and invert matches"
  else
    bad "rg tenaoshi untracked" "rg|invert missed EditPlan.swift"
  fi
fi

echo "== sitbone multiline: auto-open vs --open never =="
if [[ -d "$SIT" ]]; then
  line_out="$(
    rg -n --no-heading -g '*.swift' 'cumulative save failed' "$SIT" \
      | "$LEDE" --templates - -n 3 \
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
      | "$LEDE" --templates - --open never -n 3 \
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
      | "$LEDE" --files - -n 3 \
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
    | "$LEDE" --templates - --chdir "$KIZU" -q \
      'git diff single file failed: boom'; then
    ok "git grep format! + --chdir hydrates anyhow! sibling"
  else
    bad "git grep format! + --chdir hydrates anyhow! sibling" "missed"
  fi
  if git -C "$KIZU" grep -n -e 'format!' -- '*.rs' \
    | "$LEDE" --templates - --open never -q \
      'git diff single file failed: boom'; then
    bad "without hydrate, format! grep should miss anyhow!" "unexpected hit"
  else
    ok "without hydrate, git grep format! misses anyhow!"
  fi
fi

echo "== --chdir + relative grep line (fixture) =="
chdir_out="$(
  printf '%s\n' 'src/log.swift:7:        cumulative save failed path=\(path) \' \
    | "$LEDE" --chdir "$FIX" --from grep \
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
      | "$LEDE" --templates - -n 5 \
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
    | "$LEDE" --templates - --exact -q \
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
      | "$LEDE" --templates - -n 3 'camera presence enabled'
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
      | "$LEDE" --templates - -n 5 \
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
    | "$LEDE" --templates - -n 3 \
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
    | "$LEDE" --templates - -n 3 \
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
    | "$LEDE" --templates - -n 3 \
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
    | "$LEDE" --templates - -n 3 'user 42 not'
)" || user_trunc=""
if echo "$user_trunc" | grep -q 'truncated:' \
  && echo "$user_trunc" | grep -q '{uid} = 42' \
  && echo "$user_trunc" | grep -q 'found'; then
  ok "truncated user {uid} still binds"
else
  bad "truncated user {uid} still binds" "${user_trunc:-empty}"
fi

spawn_trunc="$(
  "$LEDE" --templates "$FIX/src/prefix.rs" -n 3 \
    '2026-08-19T23:50:01Z ERROR failed to spawn `git ap'
)" || spawn_trunc=""
if echo "$spawn_trunc" | grep -q 'truncated:' \
  && echo "$spawn_trunc" | grep -q '{cmd} = git ap'; then
  ok "truncated spawn binds {cmd}"
else
  bad "truncated spawn binds {cmd}" "${spawn_trunc:-empty}"
fi

loc_out="$(
  "$LEDE" --templates "$FIX/src/prefix.rs" -e '   --> src/git/revert.rs:46:18' || true
)"
if echo "$loc_out" | grep -q 'rustc locator' && ! echo "$loc_out" | grep -q '{i} ='; then
  ok "rustc --> locator is not a template query"
else
  bad "rustc --> locator is not a template query" "$loc_out"
fi

rank_out="$(
  "$LEDE" --templates "$FIX/src/prefix.rs" -n 5 \
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
    | "$LEDE" --templates - -n 5 \
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
    | "$LEDE" --templates "$FIX/streams/raw.txt" --any
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
  } | "$LEDE" --templates "$FIX/src/user.py" --any --complete
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
  echo 'user 42 not' | "$LEDE" --templates "$FIX/src/user.py" --any --complete
)" || any_trunc_only_rc=$?
if echo "$any_trunc_only" | grep -q 'tmpl:'; then
  bad "--complete must refuse truncated-only stream" "$any_trunc_only"
else
  ok "--complete refuses truncated-only --any"
fi

stream_rc=0
stream_meta="$(
  python3 - "$LEDE" "$FIX/streams/raw.txt" <<'PY'
import os, signal, subprocess, sys, time

lede, raw = sys.argv[1], sys.argv[2]
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
    [lede, "--templates", raw, "--any"],
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
bin_out="$(printf '\x00\xff\xee' | "$LEDE" --templates - -e 'user 42 not found' 2>&1)" || bin_rc=$?
if [[ "$bin_rc" -eq 2 ]] \
  && echo "$bin_out" | grep -qi 'binary' \
  && ! echo "$bin_out" | grep -q 'UnicodeDecodeError'; then
  ok "binary stdin fail closed"
else
  bad "binary stdin fail closed" "rc=$bin_rc $bin_out"
fi

rand_rc=0
rand_out="$(dd if=/dev/urandom bs=256 count=1 2>/dev/null | "$LEDE" --templates - -e 'user 42 not found' 2>&1)" || rand_rc=$?
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
      | "$LEDE" --templates - -n 3 \
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
      | "$LEDE" --templates - -n 3 \
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
      | "$LEDE" --templates - -e '   --> src/git/revert.rs:46:18' || true
  )"
  if echo "$kizu_loc" | grep -q 'rustc locator' && ! echo "$kizu_loc" | grep -q '{i} ='; then
    ok "dogfood kizu rustc locator refused"
  else
    bad "dogfood kizu rustc locator refused" "$kizu_loc"
  fi
fi

echo
echo "passed=$pass failed=$fail"
if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
exit 0
