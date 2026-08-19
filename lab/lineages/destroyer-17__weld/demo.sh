#!/usr/bin/env bash
# Money-shot probes from DESTROYER_WELD. Does not rewrite weld.
set -euo pipefail

WELD="${WELD:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-caff208a0972/weld}"
FIX="${WELD_FIX:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-caff208a0972/fixtures}"
KIZU="${KIZU:-/Users/annenpolka/ghq/github.com/annenpolka/kizu}"
SIT="${SIT:-/Users/annenpolka/ghq/github.com/annenpolka/sitbone}"
TENA="${TENA:-/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi}"
chmod +x "$WELD"

echo "== selftest (must stay ok) =="
"$WELD" --selftest

echo "== leftover proving newline stripped =="
"$WELD" --templates "$FIX/src/concat.js" $'\nDone.' || true

echo "== expr-first control =="
"$WELD" --templates "$FIX/src/concat.js" $'{"ok":true}\nDone.' || true

echo "== incomplete fence truncated success =="
"$WELD" --templates "$FIX/src/concat.swift" $'```json\n{"ok":true}' || true

echo "== suffix weld decoy when longer splice absent =="
"$WELD" --templates "$FIX/src/concat.js" --extract | rg weld \
  | "$WELD" --templates - --from index 'open /tmp/x: permission denied' || true

echo "== user 42 found stuffs uid =="
"$WELD" --templates "$FIX/src/user.py" 'user 42 found' || true

if [[ -d "$KIZU" ]]; then
  echo "== kizu cleaned+newline =="
  rg -n --no-heading -g '*.rs' -g '!target/**' 'cleaned \+' "$KIZU" \
    | "$WELD" --templates - $'keep\n' || true
fi

if [[ -d "$SIT" ]]; then
  echo "== sitbone sibling middle-drop =="
  rg -n --no-heading -g '*.swift' awayRecovered "$SIT" \
    | "$WELD" --templates - -n 3 'transition focused → idle awayRecovered=0' || true
fi

if [[ -d "$TENA" ]]; then
  echo "== tenaoshi wrap 4-hole control =="
  rg -n --no-heading -g '*.swift' 'source graphemes' "$TENA/Engine/Sources" \
    | "$WELD" --templates - -n 1 \
      'invalid original range for unit u1: 3..<8 (source graphemes: 12)' || true
fi
