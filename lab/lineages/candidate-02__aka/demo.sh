#!/usr/bin/env bash
# Exercise aka against a synthetic repo and (when present) real dogfood trees.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
AKA="$ROOT/aka"
export PYTHONUNBUFFERED=1

fail() { echo "demo FAIL: $*" >&2; exit 1; }
pass() { echo "demo ok: $*"; }

[[ -x "$AKA" ]] || chmod +x "$AKA"

echo "== selftest =="
python3 "$AKA" --selftest || fail "selftest"

WORK="$(mktemp -d "${TMPDIR:-/tmp}/aka-demo.XXXXXX")"
cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT

REPO="$WORK/svc"
mkdir -p "$REPO/src" "$REPO/spec" "$REPO/dist" "$REPO/weird dir" "$REPO/nested/src"

# Wire protocol living under three inflections, no shared constant.
cat > "$REPO/src/server.py" << 'EOF'
# producer
HEADER = "X-Request-Id"
def handle(has_more: bool) -> None:
    emit({"has_more": has_more, "source_text": "hi"})
EOF

cat > "$REPO/src/client.ts" << 'EOF'
// consumer — camelCase, no shared import
export function read(hasMore: boolean, xRequestId: string) {
  fetch("/v1", { headers: { "X-Request-Id": xRequestId } });
  return { hasMore, sourceText: "" };
}
EOF

cat > "$REPO/spec/api.yaml" << 'EOF'
headers:
  X-Request-Id:
    required: true
properties:
  has_more: { type: boolean }
  source_text: { type: string }
EOF

# Unicode + space in path (must still be indexed).
cat > "$REPO/weird dir/名前.ts" << 'EOF'
export const SOURCE_TEXT = "source_text";
EOF

# Generated bundle should be ignored even if it repeats the tokens.
cat > "$REPO/dist/app.min.js" << 'EOF'
const has_more=1; const source_text="x"; const XRequestId="X-Request-Id";
EOF

# Single-form clone (same spelling in two files, no inflection).
# Default listing requires two surface forms, so this must stay out.
mkdir -p "$REPO/src/clone"
echo 'tool = "MultiEdit"' > "$REPO/src/clone/a.py"
echo 'also = "MultiEdit"' > "$REPO/src/clone/b.py"

# Nested git repo with its own cognate; default git-ls-files of parent
# will not see it, --walk should.
mkdir -p "$REPO/nested/src"
cat > "$REPO/nested/src/inner.py" << 'EOF'
FLAG = "has_more"
EOF
git -C "$REPO/nested" init -q
git -C "$REPO/nested" config user.email "demo@example.com"
git -C "$REPO/nested" config user.name "demo"
git -C "$REPO/nested" add -A
git -C "$REPO/nested" commit -qm "nested inner"

git -C "$REPO" init -q
git -C "$REPO" config user.email "demo@example.com"
git -C "$REPO" config user.name "demo"
git -C "$REPO" add src spec "weird dir" dist
git -C "$REPO" commit -qm "wire protocol v1"

echo
echo "== list cognates =="
OUT="$(python3 "$AKA" -C "$REPO" --limit 20)"
printf '%s\n' "$OUT"
echo "$OUT" | grep -q 'has.more' || fail "expected has.more pact"
echo "$OUT" | grep -q 'hasMore' || fail "expected hasMore surface"
echo "$OUT" | grep -q 'source.text' || fail "expected source.text pact"
echo "$OUT" | grep -q 'x.request.id' || fail "expected X-Request-Id pact"
echo "$OUT" | grep -q '名前.ts' || fail "expected unicode path hit"
echo "$OUT" | grep -q 'app.min.js' && fail "generated min.js should be skipped" || true
echo "$OUT" | grep -q 'MultiEdit' && fail "single-form clone should not list by default" || true
echo "$OUT" | grep -q 'layers: code,config' || fail "spec/api.yaml should be config, not test"
pass "listing found inflected wire tokens, skipped generated and clones"

echo
echo "== lookup =="
LOOK="$(python3 "$AKA" -C "$REPO" hasMore)"
printf '%s\n' "$LOOK"
echo "$LOOK" | grep -q 'has_more' || fail "lookup hasMore should also show has_more"
echo "$LOOK" | grep -q 'src/server.py' || fail "lookup missing producer"
echo "$LOOK" | grep -q 'src/client.ts' || fail "lookup missing consumer"
pass "lookup by any surface form"

echo
echo "== porcelain / json =="
python3 "$AKA" -C "$REPO" --porcelain has_more | grep -q $'has.more\thas_more\t' \
  || fail "porcelain row"
python3 "$AKA" -C "$REPO" --json has_more | python3 -c \
  'import json,sys; d=json.load(sys.stdin); assert d[0]["canon"]=="has.more"' \
  || fail "json shape"
pass "machine output"

echo
echo "== one-sided edit --check =="
# Rename the wire field in the producer only.
python3 - << PY
from pathlib import Path
p = Path("$REPO/src/server.py")
p.write_text(p.read_text().replace("has_more", "has_extra"))
PY
git -C "$REPO" add src/server.py
SPLIT_OUT="$(python3 "$AKA" -C "$REPO" --check || true)"
printf '%s\n' "$SPLIT_OUT"
echo "$SPLIT_OUT" | grep -q 'SPLIT  has.more' || fail "expected SPLIT has.more"
echo "$SPLIT_OUT" | grep -q 'src/client.ts' || fail "leftover should include client.ts"
echo "$SPLIT_OUT" | grep -q 'spec/api.yaml' || fail "leftover should include api.yaml"
# exit code
set +e
python3 "$AKA" -C "$REPO" --check >/dev/null
rc=$?
set -e
[[ "$rc" -eq 1 ]] || fail "expected exit 1 on split, got $rc"
pass "one-sided rename is a split (exit 1)"

echo
echo "== piped git diff =="
PIPE_OUT="$(git -C "$REPO" diff --cached -U0 | python3 "$AKA" -C "$REPO" || true)"
echo "$PIPE_OUT" | grep -q 'SPLIT  has.more' || fail "stdin diff should auto-check"
pass "git diff | aka auto-enters check mode"

echo
echo "== two-sided fix =="
python3 - << PY
from pathlib import Path
for rel in ("src/client.ts", "spec/api.yaml"):
    p = Path("$REPO") / rel
    p.write_text(p.read_text().replace("has_more", "has_extra").replace("hasMore", "hasExtra"))
PY
git -C "$REPO" add src/client.ts spec/api.yaml
set +e
python3 "$AKA" -C "$REPO" --check
rc=$?
set -e
[[ "$rc" -eq 0 ]] || fail "expected exit 0 after updating leftovers, got $rc"
pass "complete rename is clean (exit 0)"

echo
echo "== nested git =="
# Parent no longer contains has_more (renamed above). The nested repo still does.
WALK="$(python3 "$AKA" -C "$REPO" --walk --porcelain has_more || true)"
printf '%s\n' "$WALK"
echo "$WALK" | grep -q 'nested/src/inner.py' || fail "--walk should see nested repo files"
set +e
DEFAULT="$(python3 "$AKA" -C "$REPO" --porcelain has_more)"
drc=$?
set -e
echo "$DEFAULT" | grep -q 'nested/src/inner.py' && fail "git ls-files should not list nested repo" || true
[[ "$drc" -eq 1 ]] || echo "(parent lookup of old token is empty, as expected)"
pass "nested git hidden by default, visible with --walk"

echo
echo "== real dogfood (read-only) =="
dogfood() {
  local name="$1" path="$2" token="$3"
  if [[ ! -d "$path/.git" && ! -f "$path/.git" ]]; then
    echo "skip $name (not present)"
    return 0
  fi
  echo "--- $name $token ---"
  python3 "$AKA" -C "$path" --limit 5 "$token"
  python3 "$AKA" -C "$path" --porcelain "$token" | grep -q . \
    || fail "$name lookup $token empty"
  if [[ "$name" == tenaoshi ]]; then
    LIST="$(python3 "$AKA" -C "$path" --limit 12)"
    echo "$LIST" | grep -q 'has.more' || fail "tenaoshi list missing has.more"
    echo "$LIST" | grep -q 'OraclesGenerated' && fail "generated oracles leaked into list" || true
    echo "$LIST" | grep -q 'forms: TenaoshiEngineTests' && fail "single-form type name leaked" || true
    pass "tenaoshi list is inflection-only, no generated flood"
  fi
  pass "$name knows $token"
}

dogfood tenaoshi /Users/annenpolka/ghq/github.com/annenpolka/tenaoshi has_more
dogfood kizu /Users/annenpolka/ghq/github.com/annenpolka/kizu hook_event_name
dogfood sitbone /Users/annenpolka/ghq/github.com/annenpolka/sitbone away_recovered
dogfood skills /Users/annenpolka/ghq/github.com/annenpolka/skills input_summary

echo
echo "demo: all checks passed"
exit 0
