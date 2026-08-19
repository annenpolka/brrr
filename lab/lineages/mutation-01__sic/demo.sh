#!/usr/bin/env bash
# Exercise sic against a synthetic repo and (when present) real dogfood trees.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SIC="$ROOT/sic"
export PYTHONUNBUFFERED=1

fail() { echo "demo FAIL: $*" >&2; exit 1; }
pass() { echo "demo ok: $*"; }

[[ -x "$SIC" ]] || chmod +x "$SIC"

echo "== selftest =="
python3 "$SIC" --selftest || fail "selftest"

WORK="$(mktemp -d "${TMPDIR:-/tmp}/sic-demo.XXXXXX")"
cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT

REPO="$WORK/svc"
mkdir -p "$REPO/src" "$REPO/spec" "$REPO/dist" "$REPO/weird dir" "$REPO/nested/src"

# Exact wire key "has_more" in JSON / YAML / quoted code. The identifier
# hasMore is a local adapter and must NOT join the token.
cat > "$REPO/src/server.py" << 'EOF'
# producer
HEADER = "X-Request-Id"
def handle(has_more: bool) -> None:
    emit({"has_more": has_more, "source_text": "hi"})
EOF

cat > "$REPO/src/client.ts" << 'EOF'
// consumer — camelCase identifiers are not the wire
export function read(hasMore: boolean, xRequestId: string) {
  fetch("/v1", { headers: { "X-Request-Id": xRequestId } });
  return { hasMore, sourceText: data["has_more"] };
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

# A second serialized spelling of the same idea: a protocol FORK, not a synonym.
cat > "$REPO/spec/legacy.json" << 'EOF'
{ "hasMore": false, "sourceText": "" }
EOF

# Unicode + space in path.
cat > "$REPO/weird dir/名前.ts" << 'EOF'
export const SOURCE_TEXT = "source_text";
EOF

# Generated bundle should be ignored.
cat > "$REPO/dist/app.min.js" << 'EOF'
const has_more=1; const source_text="x"; const XRequestId="X-Request-Id";
EOF

# Exact clone of a quoted protocol string in two files (no inflection).
# aka hid this; sic should list it — the token is the string as written.
mkdir -p "$REPO/src/clone"
echo 'tool = "MultiEdit"' > "$REPO/src/clone/a.py"
echo 'also = "MultiEdit"' > "$REPO/src/clone/b.py"

# Identifier-only noise must stay out.
cat > "$REPO/src/color.swift" << 'EOF'
let backgroundColor = 1
func hasMore() {}
EOF

# Nested git repo with its own quoted key; default git-ls-files of parent
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
echo "== list exact wire keys =="
OUT="$(python3 "$SIC" -C "$REPO" --limit 20)"
printf '%s\n' "$OUT"
echo "$OUT" | grep -q '^has_more' || fail "expected has_more token"
echo "$OUT" | grep -q 'source_text' || fail "expected source_text token"
echo "$OUT" | grep -q 'x-request-id\|X-Request-Id' || fail "expected X-Request-Id header"
echo "$OUT" | grep -q '名前.ts' || fail "expected unicode path hit"
echo "$OUT" | grep -q 'app.min.js' && fail "generated min.js should be skipped" || true
echo "$OUT" | grep -q 'backgroundColor' && fail "identifier backgroundColor leaked" || true
# Identifier hasMore must not be merged into has_more.
if echo "$OUT" | grep -A20 '^has_more' | grep -q 'hasMore'; then
  # ~forks line is allowed; hits must not claim hasMore is has_more
  echo "$OUT" | grep -A20 '^has_more' | grep -E 'json|yaml|quoted' | grep -q 'hasMore' \
    && fail "hasMore identifier/json leaked into has_more hits" || true
fi
pass "listing found exact wire keys, skipped identifiers and generated"

echo
echo "== lookup is exact =="
LOOK="$(python3 "$SIC" -C "$REPO" has_more)"
printf '%s\n' "$LOOK"
echo "$LOOK" | grep -q 'src/server.py' || fail "lookup missing producer"
echo "$LOOK" | grep -q 'src/client.ts' || fail "lookup missing consumer quoted key"
echo "$LOOK" | grep -q 'spec/api.yaml' || fail "lookup missing yaml key"
# The Swift/TS identifier hasMore is not this token.
echo "$LOOK" | grep -v '~forks' | grep -q 'hasMore' && fail "lookup has_more should not include hasMore surface" || true
set +e
MISS="$(python3 "$SIC" -C "$REPO" hasMore 2>&1)"
mrc=$?
set -e
printf '%s\n' "$MISS"
# hasMore exists as a JSON key in legacy.json — lookup should find THAT token,
# not has_more. If it finds hasMore, it must not list yaml has_more as the same.
if [[ "$mrc" -eq 0 ]]; then
  echo "$MISS" | grep -q 'spec/legacy.json' || fail "lookup hasMore should be the json key"
  echo "$MISS" | grep -q '^has_more' && fail "lookup hasMore collapsed into has_more" || true
else
  echo "$MISS" | grep -q 'forks' || fail "miss should hint the has_more fork"
fi
pass "lookup is exact; hasMore is not has_more"

echo
echo "== forks =="
FORKS="$(python3 "$SIC" -C "$REPO" --forks)"
printf '%s\n' "$FORKS"
echo "$FORKS" | grep -q 'has_more' || fail "fork missing has_more"
echo "$FORKS" | grep -q 'hasMore' || fail "fork missing hasMore"
echo "$FORKS" | grep -q 'source_text' || fail "fork missing source_text"
echo "$FORKS" | grep -q 'sourceText' || fail "fork missing sourceText"
pass "inflection neighbors are forks, not synonyms"

echo
echo "== porcelain / json =="
python3 "$SIC" -C "$REPO" --porcelain has_more | grep -q $'has_more\t' \
  || fail "porcelain row"
python3 "$SIC" -C "$REPO" --json has_more | python3 -c \
  'import json,sys; d=json.load(sys.stdin); assert d[0]["token"]=="has_more"' \
  || fail "json shape"
pass "machine output"

echo
echo "== one-sided edit --check =="
python3 - << PY
from pathlib import Path
p = Path("$REPO/src/server.py")
p.write_text(p.read_text().replace('"has_more"', '"has_extra"'))
PY
git -C "$REPO" add src/server.py
SPLIT_OUT="$(python3 "$SIC" -C "$REPO" --check || true)"
printf '%s\n' "$SPLIT_OUT"
echo "$SPLIT_OUT" | grep -q 'SPLIT  has_more' || fail "expected SPLIT has_more"
echo "$SPLIT_OUT" | grep -q 'src/client.ts' || fail "leftover should include client.ts"
echo "$SPLIT_OUT" | grep -q 'spec/api.yaml' || fail "leftover should include api.yaml"
# leftover must NOT include spec/legacy.json (that file speaks hasMore)
echo "$SPLIT_OUT" | grep -q 'legacy.json' && fail "hasMore file is not leftover of has_more" || true
set +e
python3 "$SIC" -C "$REPO" --check >/dev/null
rc=$?
set -e
[[ "$rc" -eq 1 ]] || fail "expected exit 1 on split, got $rc"
pass "one-sided rename of the exact key is a split (exit 1)"

echo
echo "== piped git diff =="
PIPE_OUT="$(git -C "$REPO" diff --cached -U0 | python3 "$SIC" -C "$REPO" || true)"
echo "$PIPE_OUT" | grep -q 'SPLIT  has_more' || fail "stdin diff should auto-check"
pass "git diff | sic auto-enters check mode"

echo
echo "== two-sided fix =="
python3 - << PY
from pathlib import Path
for rel in ("src/client.ts", "spec/api.yaml", "weird dir/名前.ts"):
    p = Path("$REPO") / rel
    p.write_text(p.read_text().replace("has_more", "has_extra").replace('"source_text"', '"source_text"'))
PY
# yaml unquoted key
python3 - << PY
from pathlib import Path
p = Path("$REPO/spec/api.yaml")
p.write_text(p.read_text().replace("has_more:", "has_extra:"))
PY
git -C "$REPO" add src/client.ts spec/api.yaml "weird dir/名前.ts"
set +e
python3 "$SIC" -C "$REPO" --check
rc=$?
set -e
[[ "$rc" -eq 0 ]] || fail "expected exit 0 after updating leftovers, got $rc"
pass "complete exact-key rename is clean (exit 0)"

echo
echo "== nested git =="
WALK="$(python3 "$SIC" -C "$REPO" --walk --porcelain has_more || true)"
printf '%s\n' "$WALK"
echo "$WALK" | grep -q 'nested/src/inner.py' || fail "--walk should see nested repo files"
set +e
DEFAULT="$(python3 "$SIC" -C "$REPO" --porcelain has_more)"
drc=$?
set -e
echo "$DEFAULT" | grep -q 'nested/src/inner.py' && fail "git ls-files should not list nested repo" || true
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
  python3 "$SIC" -C "$path" --limit 5 "$token" || true
  python3 "$SIC" -C "$path" --porcelain "$token" | grep -q . \
    || fail "$name lookup $token empty"
  pass "$name knows exact key $token"
}

# tenaoshi: wire is "has_more" (JSON + CodingKeys raw value). Identifier hasMore is not the token.
if [[ -d /Users/annenpolka/ghq/github.com/annenpolka/tenaoshi/.git ]]; then
  dogfood tenaoshi /Users/annenpolka/ghq/github.com/annenpolka/tenaoshi has_more
  TEN_LIST="$(python3 "$SIC" -C /Users/annenpolka/ghq/github.com/annenpolka/tenaoshi --limit 15)"
  echo "$TEN_LIST" | grep -q '^has_more' || fail "tenaoshi list missing has_more"
  TEN_PORC="$(python3 "$SIC" -C /Users/annenpolka/ghq/github.com/annenpolka/tenaoshi --porcelain has_more)"
  echo "$TEN_PORC" | grep -E 'EPF-001.json|EditPlan.swift' \
    || fail "untracked tenaoshi fixtures/CodingKeys should be indexed"
  echo "$TEN_PORC" | grep -q $'\tjson\t' || fail "tenaoshi has_more should have a json-key witness"
  set +e
  TEN_CAMEL="$(python3 "$SIC" -C /Users/annenpolka/ghq/github.com/annenpolka/tenaoshi hasMore 2>&1)"
  ten_rc=$?
  set -e
  if [[ "$ten_rc" -eq 0 ]]; then
    echo "$TEN_CAMEL" | grep -q '^has_more' && fail "tenaoshi collapsed hasMore into has_more" || true
  else
    echo "$TEN_CAMEL" | grep -q 'has_more' || fail "tenaoshi hasMore miss should hint has_more fork"
  fi
  pass "tenaoshi treats has_more as the wire key, not hasMore"
fi

dogfood kizu /Users/annenpolka/ghq/github.com/annenpolka/kizu hook_event_name
if [[ -d /Users/annenpolka/ghq/github.com/annenpolka/kizu/.git ]]; then
  KIZU_FORKS="$(python3 "$SIC" -C /Users/annenpolka/ghq/github.com/annenpolka/kizu --forks --limit 20)"
  echo "$KIZU_FORKS" | grep -q 'hook_event_name' || fail "kizu forks missing hook_event_name"
  echo "$KIZU_FORKS" | grep -q 'hookEventName' || fail "kizu forks missing hookEventName"
  pass "kizu input hook_event_name vs output hookEventName is a fork"
fi

dogfood voidtrace /Users/annenpolka/ghq/github.com/annenpolka/voidtrace resolved-beam-ticks
if [[ -d /Users/annenpolka/ghq/github.com/annenpolka/voidtrace/.git ]]; then
  VT_FORKS="$(python3 "$SIC" -C /Users/annenpolka/ghq/github.com/annenpolka/voidtrace --forks --limit 30 resolved-beam-ticks)"
  echo "$VT_FORKS" | grep -q 'resolved-beam-ticks' || fail "voidtrace fork missing kebab"
  echo "$VT_FORKS" | grep -q 'resolved_beam_ticks' || fail "voidtrace fork missing snake"
  pass "voidtrace kebab vs snake mechanic ids are a wire fork"
fi

if [[ -d /Users/annenpolka/ghq/github.com/annenpolka/sitbone/.git ]]; then
  dogfood sitbone /Users/annenpolka/ghq/github.com/annenpolka/sitbone lifetimeAwayRecovered
  python3 "$SIC" -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone --porcelain t1 \
    | grep -q 'SessionProfile.swift' \
    || fail "sitbone CodingKeys raw value t1 should be a wire key"
  SIT_LIST="$(python3 "$SIC" -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone --limit 12)"
  echo "$SIT_LIST" | grep -q 'yyyy-MM-dd' && fail "date format should not be an HTTP header" || true
  echo "$SIT_LIST" | grep -q '^YouTube' && fail "Pascal product name should not list" || true
  pass "sitbone subscripts/CodingKeys counted; date/product noise gone"
fi

echo
echo "demo: all checks passed"
exit 0
