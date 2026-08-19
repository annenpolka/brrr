#!/usr/bin/env bash
# Exercise rime: inverse printf of leftover remainder, not a fresh log line.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
RIME="$ROOT/rime"
FIX="$ROOT/fixtures"
WELD="/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-caff208a0972/weld"
chmod +x "$RIME"

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
if "$RIME" --selftest; then
  ok "selftest"
else
  bad "selftest" "rime --selftest exited $?"
fi

echo "== refuses to walk =="
if out="$("$RIME" --templates "$FIX" --matched '{"ok":true}' --remainder $'\nDone.' 2>&1)"; then
  bad "reject dir --templates" "walked: $out"
else
  if echo "$out" | grep -q 'refusing to walk'; then
    ok "reject dir --templates"
  else
    bad "reject dir --templates" "$out"
  fi
fi

echo "== extract leftover-only newline splice =="
if out="$("$RIME" --templates "$FIX/src/leftover.js" --extract)" \
  && echo "$out" | grep -q 'leftover {cleaned}\\n' \
  && echo "$out" | grep -q 'weld {body}\\nDone.' \
  && echo "$out" | grep -q '```json\\n{response}\\n```'; then
  ok "extract leftover-only + weld + wrap"
else
  bad "extract leftover-only + weld + wrap" "${out:-}"
fi

echo "== leftover suffix is the proving string =="
if out="$("$RIME" --templates "$FIX/src/leftover.js" --matched '{"ok":true}' --remainder $'\nDone.')" \
  && echo "$out" | grep -q 'via=leftover' \
  && echo "$out" | grep -q '{body} = {"ok":true}' \
  && echo "$out" | grep -q '{body}\\nDone.'; then
  ok "remainder \\nDone. binds prior"
else
  bad "remainder \\nDone. binds prior" "${out:-}"
fi

if [[ -x "$WELD" ]]; then
  anc_rc=0
  anc_out="$("$WELD" --templates "$FIX/src/leftover.js" $'\nDone.')" || anc_rc=$?
  if [[ "$anc_rc" -eq 0 ]] && echo "$anc_out" | grep -q '{body}'; then
    bad "ancestor weld should miss leftover remainder as a fresh line" "$anc_out"
  else
    ok "ancestor weld misses leftover remainder (rc=$anc_rc)"
  fi
else
  echo "  SKIP  ancestor weld not at $WELD"
fi

echo "== wrap from prefix leftover + remainder =="
if out="$("$RIME" --templates "$FIX/src/leftover.js" \
    --matched '{"ok":true}' --prefix $'```json\n' --remainder $'\n```')" \
  && echo "$out" | grep -q 'via=wrap' \
  && echo "$out" | grep -q '{response} = {"ok":true}' \
  && echo "$out" | grep -q '```json\\n{response}\\n```'; then
  ok "prefix+remainder reconstruct fence wrap"
else
  bad "prefix+remainder reconstruct fence wrap" "${out:-}"
fi

echo "== prefix leftover is the next concat =="
if out="$("$RIME" --templates "$FIX/src/leftover.js" \
    --matched 'failed to spawn `git apply --reverse`' \
    --prefix '2026-08-19T23:50:01Z ERROR ')" \
  && echo "$out" | grep -q 'via=lead' \
  && echo "$out" | grep -q '{ts} = 2026-08-19T23:50:01Z' \
  && echo "$out" | grep -q '{body} = failed to spawn'; then
  ok "prefix leftover binds stamp concat"
else
  bad "prefix leftover binds stamp concat" "${out:-}"
fi

echo "== weld record on stdin (prefix leftover, no trailing space) =="
pipe_out="$(
  printf '%s\n' \
    'leftover.js:14:10: score=0.48 lang=js holes=1 via=span from=file' \
    '  query: 2026-08-19T23:50:01Z ERROR failed to spawn `git apply --reverse`' \
    '  tmpl:  failed to spawn `{cmd}`' \
    '  {cmd} = git apply --reverse' \
    '  prefix: 2026-08-19T23:50:01Z ERROR' \
    | "$RIME" --templates "$FIX/src/leftover.js"
)" || true
if echo "$pipe_out" | grep -q '{ts} = 2026-08-19T23:50:01Z' \
  && echo "$pipe_out" | grep -q '{body} = failed to spawn'; then
  ok "weld prefix leftover on stdin binds stamp"
else
  bad "weld prefix leftover on stdin binds stamp" "${pipe_out:-}"
fi

echo "== leftover-only newline after contentful prior =="
if out="$("$RIME" --templates "$FIX/src/leftover.go" \
    --matched $'#!/bin/sh\necho keep' --remainder $'\n')" \
  && echo "$out" | grep -q 'leftover {cleaned}\\n\|tmpl:  {cleaned}\\n' \
  && echo "$out" | grep -q '{cleaned} ='; then
  ok "cleaned + newline binds after contentful leftover"
else
  bad "cleaned + newline binds after contentful leftover" "${out:-}"
fi

fresh_rc=0
fresh_out="$("$RIME" --templates "$FIX/src/leftover.go" $'#!/bin/sh\necho keep')" || fresh_rc=$?
if echo "$fresh_out" | grep -q '{cleaned}'; then
  bad "newline-only must not match a fresh log line" "$fresh_out"
elif [[ "$fresh_rc" -eq 0 ]]; then
  bad "fresh newline-only should miss" "rc=$fresh_rc $fresh_out"
else
  ok "newline-only suffix is not a fresh-line template"
fi

echo "== middle-drop leftover is a miss =="
drop_rc=0
drop_out="$("$RIME" --templates "$FIX/src/leftover.js" --matched 'failed read' --remainder ' with EPERM')" || drop_rc=$?
if echo "$drop_out" | grep -q '{op}'; then
  bad "middle-drop leftover stuffed a hole" "$drop_out"
elif [[ "$drop_rc" -eq 0 ]]; then
  bad "middle-drop leftover should miss" "$drop_out"
else
  ok "middle-drop leftover is a miss"
fi

echo "== same-template truncated remainder is not a proving string =="
trunc_rc=0
trunc_out="$(
  printf '%s\n' \
    'log.swift:20:27: holes=4/7 via=truncated' \
    '  tmpl:  transition {from} → {to} reason={reason} idle={idle}s deserted={0}' \
    '  {from} = focused' \
    '  truncated:  deserted={0} driftRecovered={0} awayRecovered={0}' \
    | "$RIME" --templates "$FIX/src/log.swift" --from leftover
)" || trunc_rc=$?
if echo "$trunc_out" | grep -q 'tmpl:'; then
  bad "same-template truncated should not invent a next concat" "$trunc_out"
elif [[ "$trunc_rc" -eq 2 ]]; then
  bad "same-template truncated should miss (exit 1), not usage 2" "$trunc_out"
else
  ok "same-template truncated remainder is a miss (rc=$trunc_rc)"
fi

echo "== truncated proving string still binds =="
if out="$("$RIME" --templates "$FIX/src/leftover.js" --matched '{"ok":true}' --remainder $'\nDon')" \
  && echo "$out" | grep -q '{body} = {"ok":true}' \
  && echo "$out" | grep -q 'truncated:'; then
  ok "truncated remainder of \\nDone. still binds"
else
  bad "truncated remainder of \\nDone. still binds" "${out:-}"
fi

KIZU="/Users/annenpolka/ghq/github.com/annenpolka/kizu"
TENA="/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi"
SKILLS="/Users/annenpolka/ghq/github.com/annenpolka/skills"
SIT="/Users/annenpolka/ghq/github.com/annenpolka/sitbone"

echo "== dogfood =="
if [[ -d "$TENA" ]]; then
  tena_done="$(
    rg -n --no-heading -g '*.swift' 'Done\.' "$TENA" \
      | "$RIME" --templates - --matched '{"ok":true}' --remainder $'\nDone.'
  )" || tena_done=""
  if echo "$tena_done" | grep -q 'EditPlanParserTests.swift' \
    && echo "$tena_done" | grep -q '{response} = {"ok":true}'; then
    ok "dogfood tenaoshi response()+\\nDone. leftover"
  else
    bad "dogfood tenaoshi response()+\\nDone. leftover" "${tena_done:-empty}"
  fi
  tena_fence="$(
    rg -n --no-heading -g '*.swift' 'json' "$TENA/Engine/Tests" \
      | "$RIME" --templates - --matched '{"ok":true}' --prefix $'```json\n' --remainder $'\n```'
  )" || tena_fence=""
  if echo "$tena_fence" | grep -q '```json\\n{response}\\n```' \
    && echo "$tena_fence" | grep -q '{response} = {"ok":true}'; then
    ok "dogfood tenaoshi fence wrap leftover"
  else
    bad "dogfood tenaoshi fence wrap leftover" "${tena_fence:-empty}"
  fi
else
  echo "  SKIP  tenaoshi"
fi

if [[ -d "$KIZU" ]]; then
  kizu_out="$(
    rg -n --no-heading -g '*.rs' -g '!target/**' 'cleaned \+' "$KIZU" \
      | "$RIME" --templates - --matched $'#!/bin/sh\necho keep' --remainder $'\n'
  )" || kizu_out=""
  if echo "$kizu_out" | grep -q 'teardown.rs' \
    && echo "$kizu_out" | grep -q '{cleaned}'; then
    ok "dogfood kizu cleaned+\\\\n leftover"
  else
    bad "dogfood kizu cleaned+\\\\n leftover" "${kizu_out:-empty}"
  fi
else
  echo "  SKIP  kizu"
fi

if [[ -d "$SKILLS" ]]; then
  skills_out="$(
    rg -n --no-heading -F 'Serialize(entry)' "$SKILLS" \
      | "$RIME" --templates - --matched '{"h":"H1"}' --remainder $'\n'
  )" || skills_out=""
  if echo "$skills_out" | grep -q '{entry} = {"h":"H1"}'; then
    ok "dogfood skills Serialize(entry)+newline leftover"
  else
    bad "dogfood skills Serialize(entry)+newline leftover" "${skills_out:-empty}"
  fi
else
  echo "  SKIP  skills"
fi

if [[ -d "$SIT" ]]; then
  sit_rc=0
  sit_out="$(
    rg -n --no-heading -g '*.swift' 'awayRecovered' "$SIT" \
      | "$RIME" --templates - --matched 'transition focused → idle' --remainder ' awayRecovered=0'
  )" || sit_rc=$?
  if echo "$sit_out" | grep -q '{to} = idle awayRecovered'; then
    bad "sitbone middle-drop leftover must miss" "$sit_out"
  elif [[ "$sit_rc" -eq 0 ]]; then
    bad "sitbone middle-drop leftover should miss" "$sit_out"
  else
    ok "dogfood sitbone middle-drop leftover is a miss"
  fi
else
  echo "  SKIP  sitbone"
fi

echo "== binary stdin fail closed =="
bin_rc=0
bin_out="$(printf '\x00\xff\xee' | "$RIME" --templates - -e 'user 42 not found' 2>&1)" || bin_rc=$?
if [[ "$bin_rc" -eq 2 ]] \
  && echo "$bin_out" | grep -qi 'binary' \
  && ! echo "$bin_out" | grep -q 'UnicodeDecodeError'; then
  ok "binary stdin fail closed"
else
  bad "binary stdin fail closed" "rc=$bin_rc $bin_out"
fi

echo
echo "passed=$pass failed=$fail"
if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
exit 0
