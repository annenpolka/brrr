#!/usr/bin/env bash
# Exercise stencil on synthetic fixtures and, when present, real dogfood trees.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
TOOL="$ROOT/stencil"
FIX="$ROOT/fixtures/ugly"
chmod +x "$TOOL"

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
if "$TOOL" --selftest; then
  ok "selftest"
else
  bad "selftest" "stencil --selftest exited $?"
fi

echo "== fixture index (walk, skip node_modules + min.js) =="
idx="$("$TOOL" --walk --index -C "$FIX")"
if echo "$idx" | grep -q 'user.py:'; then
  ok "indexed python f-string"
else
  bad "indexed python f-string" "$idx"
fi
if echo "$idx" | grep -q 'file with spaces.rs:'; then
  ok "indexed weird filename"
else
  bad "indexed weird filename" "$idx"
fi
if echo "$idx" | grep -q 'nested/repo/secret.py:'; then
  ok "indexed nested file"
else
  bad "indexed nested file" "$idx"
fi
if echo "$idx" | grep -q 'node_modules'; then
  bad "skipped node_modules" "index leaked node_modules"
else
  ok "skipped node_modules"
fi
if echo "$idx" | grep -q 'bundle.min.js'; then
  bad "skipped min.js" "index leaked min.js"
else
  ok "skipped min.js"
fi

echo "== fixture queries =="
q() {
  local name="$1"
  local needle="$2"
  shift 2
  local out
  if out="$("$TOOL" --walk -C "$FIX" -n 3 "$@")"; then
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
  "git diff single file failed: fatal: not a git repository"
q "named rust + backticks" "src/git.rs:" \
  "unparseable \`diff --git\` header: diff --git a/foo b/foo"
q "two named rust holes" "src/git.rs:" \
  $'diff --git a/src/weird.rs b/src/weird.rs\n'
q "python f-string" "src/user.py:" \
  "user 42 not found"
q "python host:port hole" "src/user.py:" \
  "cannot reach db.internal:5432 after 3 retries"
q "js template" "src/events.ts:" \
  "Duplicate event ID: evt-99"
q "js two-hole template" "src/events.ts:" \
  "Cannot enqueue event before processed time 1200: 800"
q "js exact literal" "src/events.ts:" \
  "Event id must not be empty"
q "swift interpolation" "src/log.swift:" \
  "session started profile=Focus"
q "go printf" "src/printf.go:" \
  "open /tmp/x: permission denied"
q "spaces in path" "weird names/file with spaces.rs:" \
  "cannot open strange file: /tmp/a b.txt"
q "nested secret" "nested/repo/secret.py:" \
  "nested secret key hunter2 leaked"
q "swift multiline join" "src/log.swift:" \
  "cumulative save failed path=/tmp/c.json error=disk full"

if echo "$idx" | grep -q 'schema_version'; then
  bad "skipped json literal" "index leaked JSON blob"
else
  ok "skipped json literal"
fi

echo "== dashed message via -e =="
if out="$("$TOOL" --walk -C "$FIX" -e "device init failed")" && echo "$out" | grep -q 'log.swift:'; then
  ok "-e message"
else
  bad "-e message" "${out:-}"
fi

echo "== stdin pipeline + decorations =="
pipe_out="$(
  {
    echo "Compiling stencil v0.1.0"
    echo "ERROR [worker] user 7 not found"
    printf '\x1b[31merror:\x1b[0m git diff single file failed: boom\n'
  } | "$TOOL" --walk -C "$FIX" --any
)"
if echo "$pipe_out" | grep -q 'user.py:' && echo "$pipe_out" | grep -q 'git.rs:'; then
  ok "stdin log strip + multi-message"
else
  bad "stdin log strip + multi-message" "$pipe_out"
fi

echo "== miss exits 1 =="
if "$TOOL" --walk -C "$FIX" "this message exists nowhere in the fixtures xyzzy-stencil" >/dev/null; then
  bad "miss exit" "expected exit 1"
else
  ok "miss exit 1"
fi

dogfood() {
  local repo="$1"
  local needle="$2"
  local msg="$3"
  if [[ ! -d "$repo" ]]; then
    echo "  SKIP  dogfood $repo (missing)"
    return 0
  fi
  local out
  if out="$("$TOOL" -C "$repo" -n 3 "$msg")"; then
    if echo "$out" | grep -F -q "$needle"; then
      ok "dogfood $(basename "$repo"): $needle"
    else
      bad "dogfood $(basename "$repo"): $needle" "$out"
    fi
  else
    bad "dogfood $(basename "$repo"): $needle" "exit $? out=$out"
  fi
}

echo "== dogfood (if present) =="
dogfood "/Users/annenpolka/ghq/github.com/annenpolka/kizu" \
  "src/git/diff.rs:" \
  "git diff single file failed: fatal: not a git repository (or any of the parent directories): /tmp/nope"
dogfood "/Users/annenpolka/ghq/github.com/annenpolka/voidtrace" \
  "packages/kernel/src/event-queue.ts:" \
  "Duplicate event ID: evt-abc"
dogfood "/Users/annenpolka/ghq/github.com/annenpolka/sitbone" \
  "Sources/SitboneCore/SitboneCore.swift:" \
  "session started profile=DeepWork"
dogfood "/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi" \
  "Engine/Sources/TenaoshiEngine/EditPlan.swift:" \
  "has_more cannot be true when units is empty"
dogfood "/Users/annenpolka/ghq/github.com/annenpolka/sitbone" \
  "Sources/SitboneData/JSONSessionStore.swift:" \
  "cumulative save failed path=/Users/x/Library/cumulative.json error=The file could not be saved"
dogfood "/Users/annenpolka/ghq/github.com/annenpolka/sitbone" \
  "Sources/SitboneCore/SitboneCore.swift:" \
  "camera presence enabled"

echo
echo "passed=$pass failed=$fail"
if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
exit 0
