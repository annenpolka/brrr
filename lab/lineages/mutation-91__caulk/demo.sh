#!/usr/bin/env bash
# Exercise caulk: leftover must be a complete concat operand.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
CAULK="$ROOT/caulk"
FIX="$ROOT/fixtures"
RIME="/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bad-eb91-7d80-9aa0-102692b0ef4e/rime"
chmod +x "$CAULK"

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
if "$CAULK" --selftest; then
  ok "selftest"
else
  bad "selftest" "caulk --selftest exited $?"
fi

echo "== refuses to walk =="
if out="$("$CAULK" --templates "$FIX" --matched '{"ok":true}' --remainder $'\nDone.' 2>&1)"; then
  bad "reject dir --templates" "walked: $out"
else
  if echo "$out" | grep -q 'refusing to walk'; then
    ok "reject dir --templates"
  else
    bad "reject dir --templates" "$out"
  fi
fi

echo "== extract leftover-only newline splice =="
if out="$("$CAULK" --templates "$FIX/src/leftover.js" --extract)" \
  && echo "$out" | grep -q 'leftover {cleaned}\\n' \
  && echo "$out" | grep -q 'weld {body}\\nDone.' \
  && echo "$out" | grep -q '```json\\n{response}\\n```'; then
  ok "extract leftover-only + weld + wrap"
else
  bad "extract leftover-only + weld + wrap" "${out:-}"
fi

echo "== complete leftover suffix is the proving string =="
if out="$("$CAULK" --templates "$FIX/src/leftover.js" --matched '{"ok":true}' --remainder $'\nDone.')" \
  && echo "$out" | grep -q 'via=leftover' \
  && echo "$out" | grep -q '{body} = {"ok":true}' \
  && echo "$out" | grep -q '{body}\\nDone.' \
  && ! echo "$out" | grep -q 'truncated:'; then
  ok "complete remainder \\nDone. binds prior"
else
  bad "complete remainder \\nDone. binds prior" "${out:-}"
fi

echo "== truncated leftover proving string is a miss =="
trunc_rc=0
trunc_out="$("$CAULK" --templates "$FIX/src/leftover.js" --matched '{"ok":true}' --remainder $'\nDon')" || trunc_rc=$?
if echo "$trunc_out" | grep -q '{body} = {"ok":true}'; then
  bad "truncated leftover \\nDon must not bind" "$trunc_out"
elif [[ "$trunc_rc" -eq 2 ]]; then
  bad "truncated leftover should miss (exit 1), not usage 2" "$trunc_out"
elif echo "$trunc_out" | grep -q 'not a complete operand' \
  && echo "$trunc_out" | grep -q '\\nDon' \
  && echo "$trunc_out" | grep -q '\\nDone\.'; then
  ok "truncated remainder of \\nDone. is not a complete operand (rc=$trunc_rc)"
else
  bad "truncated leftover diagnosis" "rc=$trunc_rc $trunc_out"
fi

if [[ -x "$RIME" ]]; then
  anc_rc=0
  anc_out="$("$RIME" --templates "$FIX/src/leftover.js" --matched '{"ok":true}' --remainder $'\nDon')" || anc_rc=$?
  if [[ "$anc_rc" -eq 0 ]] && echo "$anc_out" | grep -q '{body}' && echo "$anc_out" | grep -q 'truncated:'; then
    ok "ancestor rime still binds truncated leftover \\nDon"
  else
    bad "ancestor rime should bind truncated leftover" "rc=$anc_rc $anc_out"
  fi
  pipe_rc=0
  pipe_trunc="$(
    "$RIME" --templates "$FIX/src/leftover.js" --matched '{"ok":true}' --remainder $'\nDon' \
      | "$CAULK" --templates "$FIX/src/leftover.js"
  )" || pipe_rc=$?
  if echo "$pipe_trunc" | grep -q '{body} = {"ok":true}'; then
    bad "rime|caulk truncated leftover must miss" "$pipe_trunc"
  elif [[ "$pipe_rc" -eq 1 ]] \
    && echo "$pipe_trunc" | grep -q 'not a complete operand' \
    && echo "$pipe_trunc" | grep -q '\\nDon' \
    && echo "$pipe_trunc" | grep -q '\\nDone\.'; then
    ok "rime|caulk leftover rem is truncated proving string, not rest-of-operand"
  else
    bad "rime|caulk truncated leftover diagnosis" "rc=$pipe_rc $pipe_trunc"
  fi
else
  echo "  SKIP  ancestor rime not at $RIME"
fi

echo "== --complete leftover truncated still refuses =="
comp_rc=0
comp_out="$("$CAULK" --complete --templates "$FIX/src/leftover.js" --matched '{"ok":true}' --remainder $'\nDon')" || comp_rc=$?
if echo "$comp_out" | grep -q '{body}'; then
  bad "--complete leftover truncated must miss" "$comp_out"
elif [[ "$comp_rc" -eq 1 ]] && echo "$comp_out" | grep -q 'not a complete operand'; then
  ok "--complete leftover refuses truncated proving string"
else
  bad "--complete leftover truncated" "rc=$comp_rc $comp_out"
fi

echo "== wrap from complete prefix leftover + remainder =="
if out="$("$CAULK" --templates "$FIX/src/leftover.js" \
    --matched '{"ok":true}' --prefix $'```json\n' --remainder $'\n```')" \
  && echo "$out" | grep -q 'via=wrap' \
  && echo "$out" | grep -q '{response} = {"ok":true}' \
  && echo "$out" | grep -q '```json\\n{response}\\n```' \
  && ! echo "$out" | grep -q 'truncated:'; then
  ok "complete prefix+remainder reconstruct fence wrap"
else
  bad "complete prefix+remainder reconstruct fence wrap" "${out:-}"
fi

wrap_rc=0
wrap_out="$("$CAULK" --templates "$FIX/src/leftover.js" \
    --matched '{"ok":true}' --prefix $'```json\n' --remainder $'\n`')" || wrap_rc=$?
if echo "$wrap_out" | grep -q '{response}'; then
  bad "truncated wrap remainder must miss" "$wrap_out"
elif [[ "$wrap_rc" -eq 1 ]] && echo "$wrap_out" | grep -q 'not a complete operand'; then
  ok "truncated wrap remainder is not a complete operand"
else
  bad "truncated wrap remainder" "rc=$wrap_rc $wrap_out"
fi

pre_rc=0
pre_out="$("$CAULK" --templates "$FIX/src/leftover.js" \
    --matched '{"ok":true}' --prefix $'```json' --remainder $'\n```')" || pre_rc=$?
if echo "$pre_out" | grep -q '{response}'; then
  bad "truncated wrap prefix leftover must miss" "$pre_out"
elif [[ "$pre_rc" -eq 1 ]] \
  && echo "$pre_out" | grep -q 'not a complete operand' \
  && echo "$pre_out" | grep -q '```json' \
  && ! echo "$pre_out" | grep -q 'of \\n```'; then
  ok "truncated wrap prefix leftover diagnoses prefix operand"
else
  bad "truncated wrap prefix leftover" "rc=$pre_rc $pre_out"
fi

echo "== prefix leftover is the next concat =="
if out="$("$CAULK" --templates "$FIX/src/leftover.js" \
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
    | "$CAULK" --templates "$FIX/src/leftover.js"
)" || true
if echo "$pipe_out" | grep -q '{ts} = 2026-08-19T23:50:01Z' \
  && echo "$pipe_out" | grep -q '{body} = failed to spawn'; then
  ok "weld prefix leftover on stdin binds stamp"
else
  bad "weld prefix leftover on stdin binds stamp" "${pipe_out:-}"
fi

echo "== leftover-only newline after contentful prior (complete operand) =="
if out="$("$CAULK" --templates "$FIX/src/leftover.go" \
    --matched $'#!/bin/sh\necho keep' --remainder $'\n')" \
  && echo "$out" | grep -q 'leftover {cleaned}\\n\|tmpl:  {cleaned}\\n' \
  && echo "$out" | grep -q '{cleaned} ='; then
  ok "cleaned + newline binds after contentful leftover"
else
  bad "cleaned + newline binds after contentful leftover" "${out:-}"
fi

fresh_rc=0
fresh_out="$("$CAULK" --templates "$FIX/src/leftover.go" $'#!/bin/sh\necho keep')" || fresh_rc=$?
if echo "$fresh_out" | grep -q '{cleaned}'; then
  bad "newline-only must not match a fresh log line" "$fresh_out"
elif [[ "$fresh_rc" -eq 0 ]]; then
  bad "fresh newline-only should miss" "rc=$fresh_rc $fresh_out"
else
  ok "newline-only suffix is not a fresh-line template"
fi

echo "== leftover-only does not steal truncated proving string =="
steal_rc=0
steal_out="$("$CAULK" --templates "$FIX/src/leftover.js" --matched 'keep' --remainder $'\nDon')" || steal_rc=$?
if echo "$steal_out" | grep -q '{cleaned}'; then
  bad "truncated \\nDon must not bind leftover-only {cleaned}\\n" "$steal_out"
elif [[ "$steal_rc" -eq 1 ]]; then
  ok "truncated leftover is not leftover-only newline"
else
  bad "truncated leftover vs leftover-only" "rc=$steal_rc $steal_out"
fi

echo "== middle-drop leftover is a miss =="
drop_rc=0
drop_out="$("$CAULK" --templates "$FIX/src/leftover.js" --matched 'failed read' --remainder ' with EPERM')" || drop_rc=$?
if echo "$drop_out" | grep -q '{op}'; then
  bad "middle-drop leftover stuffed a hole" "$drop_out"
elif [[ "$drop_rc" -eq 0 ]]; then
  bad "middle-drop leftover should miss" "$drop_out"
else
  ok "middle-drop leftover is a miss"
fi

echo "== same-template truncated remainder is not a proving string =="
same_rc=0
same_out="$(
  printf '%s\n' \
    'log.swift:20:27: holes=4/7 via=truncated' \
    '  tmpl:  transition {from} → {to} reason={reason} idle={idle}s deserted={0}' \
    '  {from} = focused' \
    '  truncated:  deserted={0} driftRecovered={0} awayRecovered={0}' \
    | "$CAULK" --templates "$FIX/src/log.swift" --from leftover
)" || same_rc=$?
if echo "$same_out" | grep -q 'tmpl:'; then
  bad "same-template truncated should not invent a next concat" "$same_out"
elif [[ "$same_rc" -eq 2 ]]; then
  bad "same-template truncated should miss (exit 1), not usage 2" "$same_out"
else
  ok "same-template truncated remainder is a miss (rc=$same_rc)"
fi

KIZU="/Users/annenpolka/ghq/github.com/annenpolka/kizu"
TENA="/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi"
SIT="/Users/annenpolka/ghq/github.com/annenpolka/sitbone"

echo "== dogfood =="
if [[ -d "$TENA" ]]; then
  tena_done="$(
    rg -n --no-heading -g '*.swift' 'Done\.' "$TENA" \
      | "$CAULK" --templates - --matched '{"ok":true}' --remainder $'\nDone.'
  )" || tena_done=""
  if echo "$tena_done" | grep -q 'EditPlanParserTests.swift' \
    && echo "$tena_done" | grep -q '{response} = {"ok":true}'; then
    ok "dogfood tenaoshi complete leftover response()+\\nDone."
  else
    bad "dogfood tenaoshi complete leftover response()+\\nDone." "${tena_done:-empty}"
  fi
  tena_trunc_rc=0
  tena_trunc="$(
    rg -n --no-heading -g '*.swift' 'Done\.' "$TENA" \
      | "$CAULK" --templates - --matched '{"ok":true}' --remainder $'\nDon'
  )" || tena_trunc_rc=$?
  if echo "$tena_trunc" | grep -q '{response}'; then
    bad "dogfood tenaoshi truncated leftover \\nDon must miss" "$tena_trunc"
  elif [[ "$tena_trunc_rc" -eq 1 ]]; then
    ok "dogfood tenaoshi truncated leftover \\nDon is a miss"
  else
    bad "dogfood tenaoshi truncated leftover" "rc=$tena_trunc_rc ${tena_trunc:-empty}"
  fi
  tena_fence="$(
    rg -n --no-heading -g '*.swift' 'json' "$TENA/Engine/Tests" \
      | "$CAULK" --templates - --matched '{"ok":true}' --prefix $'```json\n' --remainder $'\n```'
  )" || tena_fence=""
  if echo "$tena_fence" | grep -q '```json\\n{response}\\n```' \
    && echo "$tena_fence" | grep -q '{response} = {"ok":true}'; then
    ok "dogfood tenaoshi fence wrap complete leftover"
  else
    bad "dogfood tenaoshi fence wrap complete leftover" "${tena_fence:-empty}"
  fi
else
  echo "  SKIP  tenaoshi"
fi

if [[ -d "$KIZU" ]]; then
  kizu_out="$(
    rg -n --no-heading -g '*.rs' -g '!target/**' 'cleaned \+' "$KIZU" \
      | "$CAULK" --templates - --matched $'#!/bin/sh\necho keep' --remainder $'\n'
  )" || kizu_out=""
  if echo "$kizu_out" | grep -q 'teardown.rs' \
    && echo "$kizu_out" | grep -q '{cleaned}'; then
    ok "dogfood kizu cleaned+\\\\n complete leftover"
  else
    bad "dogfood kizu cleaned+\\\\n complete leftover" "${kizu_out:-empty}"
  fi
  kizu_trunc_rc=0
  kizu_trunc="$(
    rg -n --no-heading -g '*.rs' -g '!target/**' 'cleaned \+' "$KIZU" \
      | "$CAULK" --templates - --matched $'#!/bin/sh\necho keep' --remainder $'\nD'
  )" || kizu_trunc_rc=$?
  if echo "$kizu_trunc" | grep -q '{cleaned}'; then
    bad "dogfood kizu leftover-only must not hit truncated leftover" "$kizu_trunc"
  elif [[ "$kizu_trunc_rc" -eq 1 ]]; then
    ok "dogfood kizu leftover-only hits only when leftover is complete"
  else
    bad "dogfood kizu truncated leftover-only" "rc=$kizu_trunc_rc ${kizu_trunc:-empty}"
  fi
else
  echo "  SKIP  kizu"
fi

if [[ -d "$SIT" ]]; then
  sit_rc=0
  sit_out="$(
    rg -n --no-heading -g '*.swift' 'awayRecovered' "$SIT" \
      | "$CAULK" --templates - --matched 'transition focused → idle' --remainder ' awayRecovered=0'
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
bin_out="$(printf '\x00\xff\xee' | "$CAULK" --templates - -e 'user 42 not found' 2>&1)" || bin_rc=$?
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
