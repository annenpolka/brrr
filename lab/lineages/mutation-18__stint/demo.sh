#!/usr/bin/env bash
# Exercise stint on a synthetic ugly repo and on skills + sitbone.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
STINT="$ROOT/stint"
export NO_COLOR=1

fail() { echo "demo: FAIL: $*" >&2; exit 1; }
pass() { echo "demo: ok: $*"; }

chmod +x "$STINT"
command -v python3 >/dev/null || fail "python3 required"
command -v git >/dev/null || fail "git required"

"$STINT" --version >/dev/null || fail "stint --version"
"$STINT" --help >/dev/null || fail "stint --help"

TMP="$ROOT/.demo-tmp"
rm -rf "$TMP"
mkdir -p "$TMP"
REPO="$TMP/haunt"
mkdir -p "$REPO"
git -C "$REPO" init -q
git -C "$REPO" config user.email "stint@example.test"
git -C "$REPO" config user.name "stint"
git -C "$REPO" config core.quotepath false

# Commit 1: living code
cat > "$REPO/app.py" <<'PY'
def keep():
    return 1
PY
git -C "$REPO" add app.py
git -C "$REPO" commit -q -m "base: keep"

# Commit 2: ghosts, weird names, unicode, generated, plugin tree
mkdir -p "$REPO/実験" "$REPO/codegen" "$REPO/plugin" "$REPO/nested-lib"
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
cat > "$REPO/plugin/detect.sh" <<'SH'
#!/bin/sh
echo v1
SH
cat > "$REPO/plugin/init.sh" <<'SH'
#!/bin/sh
echo init-v1
SH
echo "nested working copy" > "$REPO/nested-lib/inside.txt"
printf '\0\1\2' > "$REPO/binary.dat"

git -C "$REPO" add -A
git -C "$REPO" commit -q -m "add ghosts, unicode, spaces, generated, plugin"

# Commit 3: last blob of the plugin changes (occupancy continues)
cat > "$REPO/plugin/detect.sh" <<'SH'
#!/bin/sh
echo v2-last
SH
git -C "$REPO" add plugin/detect.sh
git -C "$REPO" commit -q -m "plugin last body"

# Commit 4: delete the experiment, leave comments (stint must ignore remnants)
cat > "$REPO/app.py" <<'PY'
def keep():
    return 1

# used by LegacyParser.try_parse_legacy
legacy_mode = True
# see 幽霊.py leftover
# generated_helper still documented here
PY
git -C "$REPO" rm -q \
  "my file (copy).py" \
  "実験/幽霊.py" \
  "codegen/generated.py" \
  "plugin/detect.sh" \
  "plugin/init.sh" \
  "binary.dat"
git -C "$REPO" add app.py
git -C "$REPO" commit -q -m "delete ghosts"

# Commit 5: second occupancy of the unicode path
mkdir -p "$REPO/実験"
cat > "$REPO/実験/幽霊.py" <<'PY'
def ghost():
    return 99
PY
git -C "$REPO" add "実験/幽霊.py"
git -C "$REPO" commit -q -m "readd unicode ghost"

# Commit 6: kill it again (two spans)
git -C "$REPO" rm -q "実験/幽霊.py"
git -C "$REPO" commit -q -m "delete unicode ghost again"

# Nested git appears after the parent already tracked the files.
git -C "$REPO/nested-lib" init -q
git -C "$REPO/nested-lib" config user.email "stint@example.test"
git -C "$REPO/nested-lib" config user.name "stint"
git -C "$REPO/nested-lib" add inside.txt
git -C "$REPO/nested-lib" commit -q -m "nested commit"

echo "== fixture: human =="
"$STINT" --root -C "$REPO" --no-color

JSON="$TMP/out.json"
"$STINT" --root -C "$REPO" --json > "$JSON"

python3 - "$JSON" <<'PY' || fail "fixture assertions"
import json, sys
d = json.load(open(sys.argv[1]))
if "remnants" in d:
    raise SystemExit("remnants key must not exist")
files = {f["path"]: f for f in d["files"]}
syms = {s["name"] for s in d["symbols"]}
want = {
    "my file (copy).py",
    "実験/幽霊.py",
    "codegen/generated.py",
    "plugin/detect.sh",
    "plugin/init.sh",
    "binary.dat",
}
missing = want - set(files)
if missing:
    raise SystemExit(f"missing ephemeral files {missing}; got {set(files)}")
ghost = files["実験/幽霊.py"]
if len(ghost["spans"]) != 2:
    raise SystemExit(f"幽霊.py should have 2 occupancy spans, got {len(ghost['spans'])}")
if ghost["commits"] < 2:
    raise SystemExit(f"幽霊.py occupancy too small: {ghost['commits']}")
plugin = files["plugin/detect.sh"]
if plugin["commits"] < 2:
    raise SystemExit(f"detect.sh should occupy >=2 commits, got {plugin['commits']}")
if plugin["bytes"] < 10:
    raise SystemExit(f"detect.sh last blob size missing: {plugin['bytes']}")
copy = files["my file (copy).py"]
if copy["bytes"] < 4:
    raise SystemExit(f"copy file size missing: {copy['bytes']}")
for name in ("LegacyParser", "try_parse_legacy", "ghost", "generated_helper"):
    if name not in syms:
        raise SystemExit(f"missing ephemeral symbol {name}; got {syms}")
if d["commits"] < 6:
    raise SystemExit(f"expected >=6 commits, got {d['commits']}")
print(
    f"fixture json ok files={len(files)} symbols={len(d['symbols'])} "
    f"幽霊.spans={len(ghost['spans'])} detect.commits={plugin['commits']}"
)
PY
pass "ugly fixture (spaces, unicode, two-span occupancy, no remnants)"

# --pick last blob
picked=$("$STINT" --root -C "$REPO" --pick "my file (copy).py" 2>/dev/null | tr -d '\n')
[ "$picked" = "scratch" ] || fail "--pick copy file, got ${picked!r}"
pass "--pick exact path with spaces"

picked=$("$STINT" --root -C "$REPO" --pick detect.sh 2>/dev/null | tr -d '\n')
[ "$picked" = "#!/bin/shecho v2-last" ] || fail "--pick detect.sh last blob, got ${picked!r}"
pass "--pick unique basename restores last (v2) blob"

picked=$("$STINT" --root -C "$REPO" --pick 幽霊.py 2>/dev/null)
echo "$picked" | grep -q "return 99" || fail "--pick 幽霊.py should be second occupancy body"
pass "--pick unicode suffix restores last span"

# --pick --to
"$STINT" --root -C "$REPO" --pick "codegen/generated.py" --to "$TMP/restored"
[ -f "$TMP/restored/codegen/generated.py" ] || fail "--pick --to did not write"
grep -q generated_helper "$TMP/restored/codegen/generated.py" || fail "restored generated.py wrong"
pass "--pick --to writes last blob"

# --pick PREFIX/ restores a deleted tree of last blobs
"$STINT" --root -C "$REPO" --pick plugin/ --to "$TMP/plugin-tree"
[ -f "$TMP/plugin-tree/plugin/detect.sh" ] || fail "tree pick missing detect.sh"
[ -f "$TMP/plugin-tree/plugin/init.sh" ] || fail "tree pick missing init.sh"
grep -q v2-last "$TMP/plugin-tree/plugin/detect.sh" || fail "tree pick detect.sh not last blob"
grep -q init-v1 "$TMP/plugin-tree/plugin/init.sh" || fail "tree pick init.sh wrong"
pass "--pick plugin/ restores last tree"

# nested git must not crash
"$STINT" --root -C "$REPO/nested-lib" --json >/dev/null
pass "nested git repo scanned without crash"

# --check exits 1 when ephemeral files exist
set +e
"$STINT" --root -C "$REPO" --check -q
rc=$?
set -e
[ "$rc" = "1" ] || fail "--check should exit 1 on ephemeral files, got $rc"
pass "--check exit 1"

# TSV is pipeable
rows=$("$STINT" --root -C "$REPO" --tsv | wc -l | tr -d ' ')
[ "$rows" -ge 6 ] || fail "expected several TSV rows, got $rows"
pass "tsv output ($rows rows)"

# No remnant rows in TSV
if "$STINT" --root -C "$REPO" --tsv | grep -q '^remnant'; then
  fail "TSV must not emit remnant rows"
fi
pass "tsv has no remnant rows"

# Real dogfood: skills circuit-breaker + sitbone FocusRiverView
SKILLS="/Users/annenpolka/ghq/github.com/annenpolka/skills"
SITBONE="/Users/annenpolka/ghq/github.com/annenpolka/sitbone"

if [ -d "$SKILLS/.git" ]; then
  "$STINT" --root -C "$SKILLS" --files --json > "$TMP/skills.json"
  python3 - "$TMP/skills.json" <<'PY' || fail "skills dogfood"
import json, sys
d = json.load(open(sys.argv[1]))
files = {f["path"]: f for f in d["files"]}
need = "circuit-breaker/skills/circuit-breaker/SKILL.md"
if need not in files:
    alt = [p for p in files if "circuit-breaker" in p]
    if not alt:
        raise SystemExit(f"expected deleted circuit-breaker files, got {sorted(files)[:20]}")
    need = alt[0]
cb = [f for p, f in files.items() if p.startswith("circuit-breaker/")]
if not cb:
    raise SystemExit("no circuit-breaker occupancy")
skill = files.get("circuit-breaker/skills/circuit-breaker/SKILL.md")
if skill and skill["commits"] < 1:
    raise SystemExit("circuit-breaker SKILL.md occupancy < 1")
print(
    f"skills ephemeral={len(files)} circuit-breaker={len(cb)} "
    f"SKILL.md occupied={skill['commits'] if skill else '?'} "
    f"score.jq occupied={files.get('circuit-breaker/scripts/score.jq', {}).get('commits', '?')}"
)
PY
  pass "skills --root --files finds circuit-breaker occupancy"
  body=$("$STINT" --root -C "$SKILLS" --pick "circuit-breaker/skills/circuit-breaker/SKILL.md" 2>/dev/null)
  echo "$body" | grep -q "circuit-breaker" || fail "pick SKILL.md missing circuit-breaker text"
  pass "skills --pick last circuit-breaker SKILL.md blob"
  "$STINT" --root -C "$SKILLS" --pick circuit-breaker/ --to "$TMP/cb-tree"
  python3 - "$TMP/cb-tree" <<'PY' || fail "skills tree pick"
import os, sys
root = sys.argv[1]
need = [
    "circuit-breaker/skills/circuit-breaker/SKILL.md",
    "circuit-breaker/scripts/score.jq",
    "circuit-breaker/scripts/detect.sh",
    "circuit-breaker/scripts/init.sh",
    "circuit-breaker/.claude-plugin/plugin.json",
    "circuit-breaker/hooks/hooks.json",
]
missing = [p for p in need if not os.path.isfile(os.path.join(root, p))]
if missing:
    raise SystemExit(f"circuit-breaker tree pick missing {missing}")
text = open(os.path.join(root, need[0]), encoding="utf-8").read()
if "circuit-breaker" not in text:
    raise SystemExit("restored SKILL.md lacks circuit-breaker")
print(f"restored {len(need)} circuit-breaker last blobs")
PY
  pass "skills --pick circuit-breaker/ restores last plugin tree"
fi

if [ -d "$SITBONE/.git" ]; then
  "$STINT" --root -C "$SITBONE" --json --hide-tests > "$TMP/sitbone.json"
  python3 - "$TMP/sitbone.json" <<'PY' || fail "sitbone dogfood"
import json, sys
d = json.load(open(sys.argv[1]))
files = {f["path"]: f for f in d["files"]}
path = "Sources/SitboneUI/FocusRiverView.swift"
if path not in files:
    raise SystemExit(f"missing FocusRiverView.swift; got {sorted(files)}")
fr = files[path]
if fr["commits"] < 2:
    raise SystemExit(f"FocusRiverView occupancy too small: {fr['commits']}")
if fr["bytes"] < 100:
    raise SystemExit(f"FocusRiverView last blob size missing: {fr['bytes']}")
syms = {s["name"] for s in d["symbols"]}
if "FocusRiverView" not in syms:
    raise SystemExit(f"missing FocusRiverView symbol; got {sorted(syms)[:20]}")
print(
    f"sitbone commits={d['commits']} files={len(files)} symbols={len(d['symbols'])} "
    f"FocusRiverView occupied={fr['commits']} bytes={fr['bytes']}"
)
PY
  pass "sitbone --root finds FocusRiverView occupancy"
  body=$("$STINT" --root -C "$SITBONE" --pick FocusRiverView.swift 2>/dev/null)
  echo "$body" | grep -q "struct FocusRiverView" || fail "pick FocusRiverView.swift missing struct"
  pass "sitbone --pick FocusRiverView.swift last blob"
fi

echo
echo "demo: all checks passed"
exit 0
