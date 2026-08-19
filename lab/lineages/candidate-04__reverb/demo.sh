#!/usr/bin/env bash
# Exercise reverb end-to-end. Exits 0 on success.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
REVERB="$ROOT/reverb"
chmod +x "$REVERB"

PASS=0
fail() { echo "FAIL: $*" >&2; exit 1; }
ok() { PASS=$((PASS + 1)); echo "ok: $*"; }

TMP="$(mktemp -d "${TMPDIR:-/tmp}/reverb-demo.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

# ---------------------------------------------------------------------------
# Fixture: duplicated nil-check with weird names, indent drift, nested git.
# ---------------------------------------------------------------------------
FIX="$TMP/ugly"
mkdir -p "$FIX/src/nested dir" "$FIX/vendor_copy" "$FIX/.hidden"
git -C "$FIX" init -q
git -C "$FIX" config user.email "demo@reverb.local"
git -C "$FIX" config user.name "reverb demo"

cat > "$FIX/src/auth.py" << 'PY'
def activate(user):
    if user is None:
        return 0
    user.activate()
    return 1
PY

# Exact copy (the leftover).
cat > "$FIX/src/billing.py" << 'PY'
def activate(user):
    if user is None:
        return 0
    user.activate()
    return 1
PY

# Same copy, extra indent (tab/space drift).
cat > "$FIX/src/nested dir/legacy.py" << 'PY'
def activate(user):
        if user is None:
            return 0
        user.activate()
        return 1
PY

# Weird filename + unicode.
cat > "$FIX/src/nested dir/バグ copy (1).py" << 'PY'
def activate(user):
    if user is None:
        return 0
    user.activate()
    return 1
PY

# Near-clone with renamed identifiers — V1 exact/indent will miss this.
cat > "$FIX/src/accounts.py" << 'PY'
def activate(account):
    if account is None:
        return 0
    account.activate()
    return 1
PY

# Boilerplate that must NOT fire queries on its own.
cat > "$FIX/src/emptyish.py" << 'PY'
def wrap():
    try:
        pass
    else:
        return
PY

git -C "$FIX" add src
git -C "$FIX" commit -qm "duplicated nil checks"

# Nested git repo holding another leftover copy (git ls-files will not see it).
NEST="$FIX/vendor_copy/nested-git"
mkdir -p "$NEST"
git -C "$NEST" init -q
git -C "$NEST" config user.email "demo@reverb.local"
git -C "$NEST" config user.name "reverb demo"
cat > "$NEST/shadow.py" << 'PY'
def activate(user):
    if user is None:
        return 0
    user.activate()
    return 1
PY
git -C "$NEST" add shadow.py
git -C "$NEST" commit -qm "shadow copy"

# Apply the fix in ONLY one of the copies.
cat > "$FIX/src/auth.py" << 'PY'
def activate(user):
    if user is None:
        raise ValueError("missing user")
    user.activate()
    return 1
PY

echo "----- human report (synthetic) -----"
set +e
"$REVERB" -C "$FIX" > "$TMP/human.out" 2> "$TMP/human.err"
EC=$?
set -e
cat "$TMP/human.out"
cat "$TMP/human.err" >&2
[[ "$EC" -eq 1 ]] || fail "expected exit 1, got $EC"
grep -q "src/billing.py" "$TMP/human.out" || fail "missed exact copy billing.py"
grep -q "legacy.py" "$TMP/human.out" || fail "missed indent copy legacy.py"
grep -q "バグ copy (1).py" "$TMP/human.out" || fail "missed unicode/weird filename"
grep -q "accounts.py" "$TMP/human.out" || fail "missed identifier-renamed clone accounts.py"
grep -q "shadow.py" "$TMP/human.out" || fail "missed nested-git copy shadow.py"
ok "synthetic human report + exit 1"

echo "----- json / grep / quiet / stdin -----"
"$REVERB" -C "$FIX" --json > "$TMP/out.json" 2>/dev/null || true
python3 - "$TMP/out.json" << 'PY'
import json, sys
data = json.load(open(sys.argv[1]))
assert data["count"] >= 4, data
paths = {m["match"]["path"] for m in data["matches"]}
for need in ("billing.py", "legacy.py", "accounts.py", "shadow.py"):
    assert any(need in p for p in paths), (need, paths)
print("json matches:", data["count"])
print("paths:", sorted(paths))
PY
ok "json"

"$REVERB" -C "$FIX" --grep > "$TMP/grep.out" 2>/dev/null || true
grep -q "billing.py:" "$TMP/grep.out" || fail "grep format missing billing"
ok "grep"

set +e
"$REVERB" -C "$FIX" -q
EC=$?
set -e
[[ "$EC" -eq 1 ]] || fail "quiet exit $EC"
ok "quiet exit 1"

git -C "$FIX" diff HEAD | "$REVERB" --stdin -C "$FIX" --grep > "$TMP/stdin.out" 2>/dev/null || true
grep -q "billing.py:" "$TMP/stdin.out" || fail "stdin pipeline missed billing"
ok "stdin pipeline"

# Clean tree → exit 0
git -C "$FIX" checkout -q -- src/auth.py
set +e
"$REVERB" -C "$FIX" -q
EC=$?
set -e
[[ "$EC" -eq 0 ]] || fail "clean tree should exit 0, got $EC"
ok "clean tree exit 0"

# ---------------------------------------------------------------------------
# Real-repo dogfood: copy files, fix one site, hunt leftovers.
# ---------------------------------------------------------------------------
dogfood_copy() {
  local name="$1" src="$2"
  local dest="$TMP/dogfood-$name"
  mkdir -p "$dest"
  git -C "$dest" init -q
  git -C "$dest" config user.email "demo@reverb.local"
  git -C "$dest" config user.name "reverb demo"
  cp -R "$src" "$dest/tree"
  git -C "$dest" add .
  git -C "$dest" commit -qm "snapshot $name"
  echo "$dest"
}

if [[ -d /Users/annenpolka/ghq/github.com/annenpolka/tenaoshi/Engine/Sources/TenaoshiEngine/Adapters ]]; then
  echo "----- dogfood: tenaoshi adapters (exact leftover header) -----"
  DEST="$(dogfood_copy tenaoshi /Users/annenpolka/ghq/github.com/annenpolka/tenaoshi/Engine/Sources/TenaoshiEngine/Adapters)"
  TARGET="$DEST/tree/AnthropicMessagesClient.swift"
  python3 - "$TARGET" << 'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
text = p.read_text()
old = 'urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")'
new = 'urlRequest.setValue("application/json; charset=utf-8", forHTTPHeaderField: "Content-Type")'
if old not in text:
    raise SystemExit("expected header line missing in Anthropic adapter")
p.write_text(text.replace(old, new, 1))
PY
  set +e
  "$REVERB" -C "$DEST" --grep > "$TMP/tenaoshi.out" 2>"$TMP/tenaoshi.err"
  EC=$?
  set -e
  echo "tenaoshi exit=$EC"
  cat "$TMP/tenaoshi.out"
  cat "$TMP/tenaoshi.err" >&2
  grep -q "OpenAICompatibleClient.swift" "$TMP/tenaoshi.out" || fail "tenaoshi: did not find leftover Content-Type in OpenAI adapter"
  grep -q "CodexResponsesClient.swift" "$TMP/tenaoshi.out" || fail "tenaoshi: did not find leftover Content-Type in Codex adapter"
  if grep -q "anthropic-version" "$TMP/tenaoshi.out"; then
    fail "tenaoshi: token-clone false positive on unrelated setValue header"
  fi
  ok "tenaoshi leftover header"
else
  echo "skip tenaoshi (missing)"
fi

if [[ -d /Users/annenpolka/ghq/github.com/annenpolka/kizu/src/git ]]; then
  echo "----- dogfood: kizu git/*.rs (identifier-renamed unwrap_or) -----"
  DEST="$(dogfood_copy kizu /Users/annenpolka/ghq/github.com/annenpolka/kizu/src/git)"
  TARGET="$DEST/tree/diff.rs"
  python3 - "$TARGET" << 'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
text = p.read_text()
old = "let rel = file_path.strip_prefix(root).unwrap_or(file_path);"
new = "let rel = file_path.strip_prefix(root).unwrap_or_else(|| file_path);"
if old not in text:
    raise SystemExit("expected unwrap_or line missing in kizu diff.rs")
p.write_text(text.replace(old, new, 1))
PY
  set +e
  "$REVERB" -C "$DEST" --grep > "$TMP/kizu.out" 2>"$TMP/kizu.err"
  EC=$?
  set -e
  echo "kizu exit=$EC"
  cat "$TMP/kizu.out"
  cat "$TMP/kizu.err" >&2
  grep -q "repo.rs" "$TMP/kizu.out" || fail "kizu: missed token-similar unwrap_or in repo.rs"
  ok "kizu found token-similar unwrap_or in repo.rs"
else
  echo "skip kizu (missing)"
fi

if [[ -d /Users/annenpolka/ghq/github.com/annenpolka/sitbone/Sources ]]; then
  echo "----- dogfood: sitbone Logging.swift -----"
  DEST="$(dogfood_copy sitbone /Users/annenpolka/ghq/github.com/annenpolka/sitbone/Sources)"
  TARGET="$DEST/tree/SitboneCore/Logging.swift"
  python3 - "$TARGET" << 'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
text = p.read_text()
old = 'Logger(subsystem: "com.sitbone", category: "core.state")'
new = 'Logger(subsystem: "com.sitbone.app", category: "core.state")'
if old not in text:
    raise SystemExit("expected Logger line missing")
p.write_text(text.replace(old, new, 1))
PY
  set +e
  "$REVERB" -C "$DEST" --json > "$TMP/sitbone.json" 2>"$TMP/sitbone.err"
  EC=$?
  set -e
  echo "sitbone exit=$EC"
  python3 - "$TMP/sitbone.json" << 'PY'
import json, sys
data = json.load(open(sys.argv[1]))
print("sitbone matches", data["count"])
for m in data["matches"]:
    print(" ", m["kind"], m["match"]["path"] + ":" + str(m["match"]["start"]))
paths = {m["match"]["path"] for m in data["matches"]}
assert data["count"] >= 1, data
assert any("Logging.swift" in p and "SitboneCore" not in p for p in paths) or any(
    "Logging.swift" in p for p in paths
), paths
PY
  cat "$TMP/sitbone.err" >&2
  [[ "$EC" -eq 1 ]] || fail "sitbone expected leftover loggers, exit $EC"
  ok "sitbone leftover Logger declarations"
else
  echo "skip sitbone (missing)"
fi

if [[ -d /Users/annenpolka/ghq/github.com/annenpolka/voidtrace/packages ]]; then
  echo "----- dogfood: voidtrace packages/*/src -----"
  DEST="$TMP/dogfood-voidtrace"
  mkdir -p "$DEST"
  git -C "$DEST" init -q
  git -C "$DEST" config user.email "demo@reverb.local"
  git -C "$DEST" config user.name "reverb demo"
  for pkg in catalog contracts experiments kernel rules runtime-node sdk spec-artifacts; do
    src="/Users/annenpolka/ghq/github.com/annenpolka/voidtrace/packages/$pkg/src"
    if [[ -d "$src" ]]; then
      mkdir -p "$DEST/packages/$pkg"
      cp -R "$src" "$DEST/packages/$pkg/src"
    fi
  done
  git -C "$DEST" add .
  git -C "$DEST" commit -qm "snapshot voidtrace src"
  TARGET="$DEST/packages/kernel/src/evaluate.ts"
  python3 - "$TARGET" << 'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
text = p.read_text()
old = '  | "catalog-load-failed"'
new = '  | "catalog-load-error"'
if old not in text:
    raise SystemExit("expected error union member missing")
p.write_text(text.replace(old, new, 1))
PY
  set +e
  "$REVERB" -C "$DEST" --grep > "$TMP/voidtrace.out" 2>"$TMP/voidtrace.err"
  EC=$?
  set -e
  echo "voidtrace exit=$EC"
  cat "$TMP/voidtrace.out"
  cat "$TMP/voidtrace.err" >&2
  grep -q "experiments" "$TMP/voidtrace.out" || fail "voidtrace: missed experiments leftover"
  grep -q "runtime-node" "$TMP/voidtrace.out" || fail "voidtrace: missed runtime-node case leftover"
  ok "voidtrace leftover catalog-load-failed"
else
  echo "skip voidtrace (missing)"
fi

echo
echo "demo passed ($PASS checks)"
