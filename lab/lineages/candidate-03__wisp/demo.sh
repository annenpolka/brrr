#!/usr/bin/env bash
# Exercise wisp on a synthetic ugly repo and on a real dogfood target.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
WISP="$ROOT/wisp"
export NO_COLOR=1

fail() { echo "demo: FAIL: $*" >&2; exit 1; }
pass() { echo "demo: ok: $*"; }

chmod +x "$WISP"

"$WISP" --version >/dev/null || fail "wisp --version"
"$WISP" --help >/dev/null || fail "wisp --help"

TMP="$ROOT/.demo-tmp"
rm -rf "$TMP"
mkdir -p "$TMP"
REPO="$TMP/haunt"
mkdir -p "$REPO"
git -C "$REPO" init -q
git -C "$REPO" config user.email "wisp@example.test"
git -C "$REPO" config user.name "wisp"
git -C "$REPO" config core.quotepath false

# Commit 1: living code
cat > "$REPO/app.py" <<'PY'
def keep():
    return 1
PY
git -C "$REPO" add app.py
git -C "$REPO" commit -q -m "base: keep"

# Commit 2: ghosts, weird names, unicode path, generated file
mkdir -p "$REPO/実験" "$REPO/codegen" "$REPO/nested-lib"
cat > "$REPO/app.py" <<'PY'
def keep():
    return 1

class LegacyParser:
    def try_parse_legacy(self, s):
        return s
PY
printf 'scratch\n' > "$REPO/my file (copy).py"
cat > "$REPO/実験/幽霊.py" <<'PY'
def ghost():
    return 0
PY
cat > "$REPO/codegen/generated.py" <<'PY'
# AUTO-GENERATED FILE. Do not edit.
def generated_helper():
    return 2
PY
echo "nested working copy" > "$REPO/nested-lib/inside.txt"
printf '\0\1\2' > "$REPO/binary.dat"

git -C "$REPO" add -A
git -C "$REPO" commit -q -m "add ghosts, unicode, spaces, generated, nested"

# Commit 3: delete the experiment, leave remnants in comments and a leftover flag
cat > "$REPO/app.py" <<'PY'
def keep():
    return 1

# used by LegacyParser.try_parse_legacy
legacy_mode = True
# see 幽霊.py leftover
# generated_helper still documented here
PY
git -C "$REPO" rm -q "my file (copy).py" "実験/幽霊.py" "codegen/generated.py"
git -C "$REPO" add app.py
git -C "$REPO" commit -q -m "delete ghosts, leave remnants"

# Nested git appears *after* the parent already tracked the files, so the
# parent is not a submodule situation — just an ugly on-disk tree.
git -C "$REPO/nested-lib" init -q
git -C "$REPO/nested-lib" config user.email "wisp@example.test"
git -C "$REPO/nested-lib" config user.name "wisp"
git -C "$REPO/nested-lib" add inside.txt
git -C "$REPO/nested-lib" commit -q -m "nested commit"

echo "== fixture: human =="
"$WISP" --root -C "$REPO" --no-color

JSON="$TMP/out.json"
"$WISP" --root -C "$REPO" --json > "$JSON"

python3 - "$JSON" <<'PY' || fail "fixture assertions"
import json, sys
d = json.load(open(sys.argv[1]))
files = {f["path"] for f in d["files"]}
syms = {s["name"] for s in d["symbols"]}
rems = {(r["name"], r["role"]) for r in d["remnants"]}
want_files = {"my file (copy).py", "実験/幽霊.py", "codegen/generated.py"}
missing = want_files - files
if missing:
    raise SystemExit(f"missing ephemeral files {missing}; got {files}")
for name in ("LegacyParser", "try_parse_legacy", "ghost", "generated_helper"):
    if name not in syms:
        raise SystemExit(f"missing ephemeral symbol {name}; got {syms}")
if ("LegacyParser", "comment") not in rems:
    raise SystemExit(f"missing LegacyParser comment remnant; got {rems}")
if ("try_parse_legacy", "comment") not in rems:
    raise SystemExit(f"missing try_parse_legacy remnant; got {rems}")
if not any(n == "幽霊" for n, _ in rems):
    raise SystemExit(f"missing unicode remnant; got {rems}")
if d["commits"] < 3:
    raise SystemExit(f"expected >=3 commits, got {d['commits']}")
print("fixture json assertions passed")
PY
pass "ugly fixture (spaces, unicode, generated, remnants)"

# nested git must not crash wisp
"$WISP" --root -C "$REPO/nested-lib" --json >/dev/null
pass "nested git repo scanned without crash"

# --check exits 1 when remnants exist
set +e
"$WISP" --root -C "$REPO" --check -q
rc=$?
set -e
[ "$rc" = "1" ] || fail "--check should exit 1 on remnants, got $rc"
pass "--check exit 1"

# TSV is pipeable
rows=$("$WISP" --root -C "$REPO" --tsv | wc -l | tr -d ' ')
[ "$rows" -ge 6 ] || fail "expected several TSV rows, got $rows"
pass "tsv output ($rows rows)"

# Real dogfood: skills (deleted experiments) and kizu (must not crash)
SKILLS="/Users/annenpolka/ghq/github.com/annenpolka/skills"
KIZU="/Users/annenpolka/ghq/github.com/annenpolka/kizu"
if [ -d "$SKILLS/.git" ]; then
  "$WISP" --root -C "$SKILLS" --files --json > "$TMP/skills.json"
  python3 - "$TMP/skills.json" <<'PY' || fail "skills dogfood"
import json, sys
d = json.load(open(sys.argv[1]))
files = {f["path"] for f in d["files"]}
# These skill trees were added and later deleted in history.
need = "circuit-breaker/skills/circuit-breaker/SKILL.md"
if need not in files and not any(p.startswith("circuit-breaker/") for p in files):
    raise SystemExit(f"expected deleted circuit-breaker files, got {sorted(files)[:20]}")
print(f"skills ephemeral files: {len(files)}")
PY
  pass "skills --root --files finds deleted skill trees"
fi
if [ -d "$KIZU/.git" ]; then
  "$WISP" --root -C "$KIZU" --json --hide-tests > "$TMP/kizu.json"
  python3 - "$TMP/kizu.json" <<'PY' || fail "kizu dogfood"
import json, sys
d = json.load(open(sys.argv[1]))
if d["commits"] < 10:
    raise SystemExit(f"kizu commit count looks wrong: {d['commits']}")
print(f"kizu commits={d['commits']} files={len(d['files'])} symbols={len(d['symbols'])} remnants={len(d['remnants'])}")
PY
  pass "kizu --root completes"
fi

echo
echo "demo: all checks passed"
exit 0
