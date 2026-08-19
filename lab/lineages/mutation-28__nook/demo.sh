#!/usr/bin/env bash
# Exercise nook against a synthetic repo and (when present) real dogfood trees.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
NOOK="$ROOT/nook"
export PYTHONUNBUFFERED=1

fail() { echo "demo FAIL: $*" >&2; exit 1; }
pass() { echo "demo ok: $*"; }

[[ -x "$NOOK" ]] || chmod +x "$NOOK"

echo "== selftest =="
python3 "$NOOK" --selftest || fail "selftest"

WORK="$(mktemp -d "${TMPDIR:-/tmp}/nook-demo.XXXXXX")"
cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT

REPO="$WORK/svc"
mkdir -p "$REPO/src" "$REPO/spec" "$REPO/dist" "$REPO/weird dir" "$REPO/nested/src"

# Two objects, same leaf. sic would merge these; nook must not.
cat > "$REPO/src/server.py" << 'EOF'
# producer
HEADER = "X-Request-Id"
def handle(has_more: bool) -> None:
    emit({"pagination": {"has_more": has_more}, "meta": {"has_more": False, "source_text": "hi"}})
EOF

cat > "$REPO/src/client.ts" << 'EOF'
// consumer — camelCase identifiers are not the wire
export function read(hasMore: boolean, xRequestId: string) {
  fetch("/v1", { headers: { "X-Request-Id": xRequestId } });
  return { hasMore, page: data["pagination"]["has_more"], meta: extra["meta"]["has_more"] };
}
EOF

cat > "$REPO/spec/api.yaml" << 'EOF'
headers:
  X-Request-Id:
    required: true
properties:
  has_more: { type: boolean }
pagination:
  has_more: true
meta:
  has_more: false
  source_text: hi
units:
  - id: u
    source_text: nested
EOF

# A second serialized spelling of the *same path*: a protocol FORK.
cat > "$REPO/spec/legacy.json" << 'EOF'
{ "pagination": { "hasMore": false }, "sourceText": "" }
EOF

# A file that only speaks meta.has_more — must not leftover a pagination rename.
cat > "$REPO/spec/meta-only.json" << 'EOF'
{ "meta": { "has_more": false } }
EOF

# Instance document with pagination + meta.
cat > "$REPO/spec/page.json" << 'EOF'
{
  "pagination": { "has_more": true, "next_cursor": "abc" },
  "meta": { "has_more": false, "source_text": "hi" }
}
EOF

# Unicode + space in path.
cat > "$REPO/weird dir/名前.ts" << 'EOF'
export const SOURCE_TEXT = "source_text";
const n = obj["pagination"]["has_more"];
EOF

# Generated bundle should be ignored.
cat > "$REPO/dist/app.min.js" << 'EOF'
const has_more=1; const source_text="x"; const XRequestId="X-Request-Id";
EOF

# Identifier-only noise must stay out.
cat > "$REPO/src/color.swift" << 'EOF'
let backgroundColor = 1
func hasMore() {}
EOF

# Nested git repo with its own path; default git-ls-files of parent
# will not see it, --walk should.
mkdir -p "$REPO/nested/src"
cat > "$REPO/nested/src/inner.py" << 'EOF'
FLAG = data["pagination"]["has_more"]
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
echo "== list key paths =="
OUT="$(python3 "$NOOK" -C "$REPO" --limit 30)"
printf '%s\n' "$OUT"
echo "$OUT" | grep -q '^pagination.has_more' || fail "expected pagination.has_more path"
echo "$OUT" | grep -q '^meta.has_more' || fail "expected meta.has_more path"
echo "$OUT" | grep -q 'source_text\|meta.source_text' || fail "expected source_text path"
echo "$OUT" | grep -q 'x-request-id\|X-Request-Id\|headers.x-request-id' || fail "expected X-Request-Id"
echo "$OUT" | grep -q '名前.ts' || fail "expected unicode path hit"
echo "$OUT" | grep -q 'app.min.js' && fail "generated min.js should be skipped" || true
echo "$OUT" | grep -q 'backgroundColor' && fail "identifier backgroundColor leaked" || true
pass "listing found distinct key paths, skipped identifiers and generated"

echo
echo "== lookup is the path, not the leaf =="
LOOK="$(python3 "$NOOK" -C "$REPO" pagination.has_more)"
printf '%s\n' "$LOOK"
echo "$LOOK" | grep -q 'src/server.py' || fail "lookup missing producer"
echo "$LOOK" | grep -q 'src/client.ts' || fail "lookup missing chained subscript"
echo "$LOOK" | grep -q 'spec/api.yaml' || fail "lookup missing yaml path"
echo "$LOOK" | grep -q 'spec/page.json' || fail "lookup missing json path"
echo "$LOOK" | grep -q 'spec/meta-only.json' && fail "pagination lookup leaked meta-only file" || true
echo "$LOOK" | grep -q '^meta.has_more' && fail "lookup collapsed into sibling path" || true
META="$(python3 "$NOOK" -C "$REPO" meta.has_more)"
printf '%s\n' "$META"
echo "$META" | grep -q 'spec/meta-only.json' || fail "meta lookup missing meta-only"
echo "$META" | grep -q 'spec/page.json' || fail "meta lookup missing page.json"
echo "$META" | grep -q 'weird dir' && fail "meta lookup leaked pagination-only unicode file" || true
pass "lookup is path-exact; pagination.has_more is not meta.has_more"

echo
echo "== miss on a leaf hints homonyms =="
set +e
MISS="$(python3 "$NOOK" -C "$REPO" has_more 2>&1)"
mrc=$?
set -e
printf '%s\n' "$MISS"
if [[ "$mrc" -eq 0 ]]; then
  # unrooted has_more may exist from quoted leftovers; it must not include EPF-style wrapping
  echo "$MISS" | grep -q 'spec/meta-only.json' && fail "bare has_more should not own meta.has_more files" || true
else
  echo "$MISS" | grep -q 'homonym' || fail "miss should hint leaf homonyms"
  echo "$MISS" | grep -q 'pagination.has_more' || fail "hint missing pagination.has_more"
  echo "$MISS" | grep -q 'meta.has_more' || fail "hint missing meta.has_more"
fi
pass "bare has_more does not swallow nested paths"

echo
echo "== homonyms =="
HOM="$(python3 "$NOOK" -C "$REPO" --homonyms --limit 20)"
printf '%s\n' "$HOM"
echo "$HOM" | grep -q 'HOMONYM  has_more' || fail "homonym missing has_more leaf"
echo "$HOM" | grep -q 'pagination.has_more' || fail "homonym missing pagination path"
echo "$HOM" | grep -q 'meta.has_more' || fail "homonym missing meta path"
pass "same leaf under different parents is a homonym, not one token"

echo
echo "== forks are same-path inflections =="
FORKS="$(python3 "$NOOK" -C "$REPO" --forks)"
printf '%s\n' "$FORKS"
echo "$FORKS" | grep -q 'pagination.has_more' || fail "fork missing pagination.has_more"
echo "$FORKS" | grep -q 'pagination.hasMore' || fail "fork missing pagination.hasMore"
echo "$FORKS" | grep -q 'pagination.has_more.*meta.has_more\|meta.has_more.*pagination.has_more' \
  && fail "homonym pair listed as a fork" || true
pass "inflection neighbors of the same path are forks"

echo
echo "== porcelain / json =="
python3 "$NOOK" -C "$REPO" --porcelain pagination.has_more | grep -q $'pagination.has_more\t' \
  || fail "porcelain row"
python3 "$NOOK" -C "$REPO" --json pagination.has_more | python3 -c \
  'import json,sys; d=json.load(sys.stdin); assert d[0]["token"]=="pagination.has_more"; assert d[0]["leaf"]=="has_more"' \
  || fail "json shape"
pass "machine output"

echo
echo "== one-sided edit --check (path, not leaf) =="
python3 - << PY
from pathlib import Path
p = Path("$REPO/src/server.py")
text = p.read_text()
# Rename only the pagination slot. Leave meta.has_more alone.
p.write_text(text.replace(
    '{"pagination": {"has_more":',
    '{"pagination": {"has_extra":',
    1,
))
PY
git -C "$REPO" add src/server.py
SPLIT_OUT="$(python3 "$NOOK" -C "$REPO" --check || true)"
printf '%s\n' "$SPLIT_OUT"
echo "$SPLIT_OUT" | grep -q 'SPLIT  pagination.has_more' || fail "expected SPLIT pagination.has_more"
echo "$SPLIT_OUT" | grep -q 'src/client.ts' || fail "leftover should include client.ts"
echo "$SPLIT_OUT" | grep -q 'spec/api.yaml' || fail "leftover should include api.yaml"
echo "$SPLIT_OUT" | grep -q 'spec/page.json' || fail "leftover should include page.json"
# leftover must NOT include the meta-only file — that is a different path
echo "$SPLIT_OUT" | grep -q 'meta-only.json' && fail "meta.has_more file is not leftover of pagination.has_more" || true
echo "$SPLIT_OUT" | grep -q 'SPLIT  meta.has_more' && fail "did not touch meta.has_more" || true
echo "$SPLIT_OUT" | grep -q 'SPLIT  has_more' && fail "collapsed to bare has_more split" || true
set +e
python3 "$NOOK" -C "$REPO" --check >/dev/null
rc=$?
set -e
[[ "$rc" -eq 1 ]] || fail "expected exit 1 on split, got $rc"
pass "one-sided rename of a path is a split; sibling has_more is not leftover"

echo
echo "== piped git diff =="
PIPE_OUT="$(git -C "$REPO" diff --cached -U0 | python3 "$NOOK" -C "$REPO" || true)"
echo "$PIPE_OUT" | grep -q 'SPLIT  pagination.has_more' || fail "stdin diff should auto-check"
pass "git diff | nook auto-enters check mode"

echo
echo "== two-sided path fix (meta.has_more remains) =="
python3 - << PY
from pathlib import Path
root = Path("$REPO")
# client chain
p = root / "src/client.ts"
p.write_text(p.read_text().replace('data["pagination"]["has_more"]', 'data["pagination"]["has_extra"]'))
# yaml pagination key only
p = root / "spec/api.yaml"
text = p.read_text()
text = text.replace("pagination:\n  has_more:", "pagination:\n  has_extra:", 1)
p.write_text(text)
# page.json pagination key
p = root / "spec/page.json"
p.write_text(p.read_text().replace(
    '"pagination": { "has_more":',
    '"pagination": { "has_extra":',
    1,
))
# unicode chain
p = root / "weird dir/名前.ts"
p.write_text(p.read_text().replace('obj["pagination"]["has_more"]', 'obj["pagination"]["has_extra"]'))
PY
git -C "$REPO" add src/client.ts spec/api.yaml spec/page.json "weird dir/名前.ts"
set +e
python3 "$NOOK" -C "$REPO" --check
rc=$?
set -e
[[ "$rc" -eq 0 ]] || fail "expected exit 0 after updating pagination leftovers, got $rc"
# meta.has_more must still be findable
python3 "$NOOK" -C "$REPO" meta.has_more | grep -q 'spec/meta-only.json' \
  || fail "meta.has_more vanished after pagination rename"
pass "complete path rename is clean (exit 0) even with sibling has_more remaining"

echo
echo "== nested git =="
WALK="$(python3 "$NOOK" -C "$REPO" --walk --porcelain pagination.has_more || true)"
printf '%s\n' "$WALK"
echo "$WALK" | grep -q 'nested/src/inner.py' || fail "--walk should see nested repo files"
set +e
DEFAULT="$(python3 "$NOOK" -C "$REPO" --porcelain pagination.has_more)"
set -e
echo "$DEFAULT" | grep -q 'nested/src/inner.py' && fail "git ls-files should not list nested repo" || true
pass "nested git hidden by default, visible with --walk"

echo
echo "== real dogfood (read-only) =="
dogfood_path() {
  local name="$1" path="$2" token="$3"
  if [[ ! -d "$path/.git" && ! -f "$path/.git" ]]; then
    echo "skip $name (not present)"
    return 0
  fi
  echo "--- $name $token ---"
  python3 "$NOOK" -C "$path" --limit 5 "$token" || true
  python3 "$NOOK" -C "$path" --porcelain "$token" | grep -q . \
    || fail "$name lookup $token empty"
  pass "$name knows key path $token"
}

if [[ -d /Users/annenpolka/ghq/github.com/annenpolka/tenaoshi/.git ]]; then
  TEN="/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi"
  dogfood_path tenaoshi "$TEN" mock_plan.has_more
  TEN_PORC="$(python3 "$NOOK" -C "$TEN" --porcelain mock_plan.has_more)"
  echo "$TEN_PORC" | grep -q 'EPF-001.json' || fail "tenaoshi mock_plan.has_more should hit EPF fixtures"
  # The flip: EPF fixtures are NOT the same leftover as the plan's root has_more.
  set +e
  TEN_ROOT="$(python3 "$NOOK" -C "$TEN" --porcelain has_more)"
  ten_rc=$?
  set -e
  if [[ "$ten_rc" -eq 0 ]]; then
    echo "$TEN_ROOT" | grep -q 'EPF-001.json' \
      && fail "tenaoshi collapsed mock_plan.has_more into bare has_more" || true
  fi
  TEN_HOM="$(python3 "$NOOK" -C "$TEN" --homonyms --leaf has_more --limit 20)"
  echo "$TEN_HOM"
  echo "$TEN_HOM" | grep -q 'mock_plan.has_more' || fail "tenaoshi homonym missing mock_plan.has_more"
  echo "$TEN_HOM" | grep -q 'WirePlan.has_more' || fail "tenaoshi CodingKeys should be WirePlan.has_more"
  echo "$TEN_HOM" | grep -q 'Batch.has_more' || fail "tenaoshi review batch has_more is Batch.has_more, not WirePlan"
  python3 "$NOOK" -C "$TEN" --porcelain WirePlan.has_more \
    | grep -q 'EditPlan.swift' \
    || fail "WirePlan.has_more should hit EditPlan.swift"
  python3 "$NOOK" -C "$TEN" --porcelain Batch.has_more \
    | grep -q 'EditPlanInvocationLog.swift' \
    || fail "Batch.has_more should hit InvocationLog"
  pass "tenaoshi treats mock_plan.has_more as a different path than has_more"
fi

if [[ -d /Users/annenpolka/ghq/github.com/annenpolka/kizu/.git ]]; then
  KIZU="/Users/annenpolka/ghq/github.com/annenpolka/kizu"
  dogfood_path kizu "$KIZU" hook_event_name
  KIZU_HOM="$(python3 "$NOOK" -C "$KIZU" --homonyms --limit 20)"
  echo "$KIZU_HOM" | head -80
  pass "kizu homonym scan ran"
fi

if [[ -d /Users/annenpolka/ghq/github.com/annenpolka/voidtrace/.git ]]; then
  VT="/Users/annenpolka/ghq/github.com/annenpolka/voidtrace"
  python3 "$NOOK" -C "$VT" --limit 8 || true
  python3 "$NOOK" -C "$VT" --homonyms --limit 12 || true
  pass "voidtrace path scan ran"
fi

if [[ -d /Users/annenpolka/ghq/github.com/annenpolka/sitbone/.git ]]; then
  SIT="/Users/annenpolka/ghq/github.com/annenpolka/sitbone"
  python3 "$NOOK" -C "$SIT" --porcelain lifetimeAwayRecovered \
    | grep -q 'SitboneCore.swift' \
    || fail "sitbone subscript lifetimeAwayRecovered should be a path/leaf"
  python3 "$NOOK" -C "$SIT" --limit 8 || true
  pass "sitbone subscripts counted"
fi

echo
echo "demo: all checks passed"
exit 0
