#!/usr/bin/env bash
# Exercise haunt on a synthetic ugly repo and on real dogfood targets.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
HAUNT="${ROOT}/haunt"
PYTHON="${PYTHON:-python3}"

if [[ ! -x "$HAUNT" ]]; then
  chmod +x "$HAUNT"
fi

pass() { printf 'ok  %s\n' "$*"; }
fail() { printf 'FAIL  %s\n' "$*" >&2; exit 1; }

echo "== self-test =="
"$PYTHON" "$HAUNT" --self-test || fail "self-test"

echo
echo "== ugly fixture (spaces in names, nested git, generated noise) =="
FIX="$(mktemp -d "${TMPDIR:-/tmp}/haunt-demo.XXXXXX")"
cleanup() { rm -rf "$FIX"; }
trap cleanup EXIT

git_fix() {
  git -C "$FIX" \
    -c user.name=haunt-demo \
    -c user.email=haunt-demo@test.local \
    "$@"
}

git_fix init -q -b main
mkdir -p "$FIX/src" "$FIX/scripts" "$FIX/generated" "$FIX/docs"

cat > "$FIX/src/parser.py" <<'PY'
def parse_legacy_widget(src):
    return src

def parse_ok(src):
    return src
PY

cat > "$FIX/src/we ird file.py" <<'PY'
def odd_name_helper():
    return 2
PY

cat > "$FIX/scripts/deploy_legacy.sh" <<'SH'
#!/bin/sh
echo deploy
SH

cat > "$FIX/README.md" <<'MD'
# demo

Call `parse_legacy_widget` or pass `--legacy-widget`.
Ship with scripts/deploy_legacy.sh.
`odd_name_helper` is documented here too.
MD

cat > "$FIX/src/cli.py" <<'PY'
import argparse
p = argparse.ArgumentParser()
p.add_argument('--legacy-widget', action='store_true')
PY

# generated file that mentions everything — haunt must skip it
cat > "$FIX/generated/all_names.generated.py" <<'PY'
# generated — do not edit
parse_legacy_widget
odd_name_helper
deploy_legacy
PY

printf 'nested/\n' > "$FIX/.gitignore"
git_fix add src/parser.py "src/we ird file.py" scripts/deploy_legacy.sh README.md src/cli.py generated/all_names.generated.py .gitignore
git_fix commit -q -m "birth of legacy surface"

# nested git that must not poison the parent index
mkdir -p "$FIX/nested"
git init -q "$FIX/nested"
echo 'def nested_trap(): return 1' > "$FIX/nested/trap.py"
git -C "$FIX/nested" -c user.name=x -c user.email=x@x add trap.py
git -C "$FIX/nested" -c user.name=x -c user.email=x@x commit -q -m "trap"

# delete living defs, leave docs talking
cat > "$FIX/src/parser.py" <<'PY'
def parse_ok(src):
    return src
PY
cat > "$FIX/src/cli.py" <<'PY'
import argparse
p = argparse.ArgumentParser()
PY
rm -f "$FIX/scripts/deploy_legacy.sh"
cat > "$FIX/src/we ird file.py" <<'PY'
def other():
    return 0
PY
git_fix add -A
git_fix commit -q -m "drop legacy surface"

JSON="$FIX/out.json"
"$PYTHON" "$HAUNT" -C "$FIX" --json --color never > "$JSON"

"$PYTHON" - "$JSON" <<'PY' || fail "ugly fixture assertions"
import json, sys
path = sys.argv[1]
data = json.load(open(path))
haunts = {(h["kind"], h["name"]) for h in data}
wanted = {
    ("fn", "parse_legacy_widget"),
    ("flag", "legacy-widget"),
    ("fn", "odd_name_helper"),
}
missing = wanted - haunts
if missing:
    raise SystemExit(f"missing haunts {missing}; got {haunts}")
# generated file must not be the only remnant source; preferably not a remnant at all
for h in data:
    if h["name"] == "parse_legacy_widget":
        paths = [r["path"] for r in h["remnants"]]
        if any("generated" in p for p in paths):
            raise SystemExit(f"generated file leaked into remnants: {paths}")
        if "README.md" not in paths:
            raise SystemExit(f"README.md should still mention parse_legacy_widget, got {paths}")
files = [h["name"] for h in data if h["kind"] == "file"]
if not any(n.endswith("deploy_legacy.sh") for n in files):
    raise SystemExit(f"deleted script not reported as file haunt: {files}")
print("ugly fixture haunts:", sorted(f"{k}:{n}" for k, n in haunts))
PY
pass "ugly fixture"

echo
echo "== --strict on haunted fixture (expect exit 1) =="
set +e
"$PYTHON" "$HAUNT" -C "$FIX" --strict --json >/dev/null
code=$?
set -e
[[ "$code" -eq 1 ]] || fail "--strict expected 1, got $code"
pass "--strict exits 1 when haunted"

echo
echo "== dogfood (read-only) =="
dogfood() {
  local name="$1" repo="$2"
  if [[ ! -d "$repo/.git" && ! -d "$repo" ]]; then
    echo "skip $name (missing $repo)"
    return 0
  fi
  echo "--- $name ---"
  "$PYTHON" "$HAUNT" -C "$repo" --tsv --color never -v 2>"$FIX/$name.err" | head -20
  cat "$FIX/$name.err" || true
  echo
}

dogfood skills /Users/annenpolka/ghq/github.com/annenpolka/skills
dogfood tenaoshi /Users/annenpolka/ghq/github.com/annenpolka/tenaoshi
dogfood sitbone /Users/annenpolka/ghq/github.com/annenpolka/sitbone
dogfood kizu /Users/annenpolka/ghq/github.com/annenpolka/kizu
dogfood voidtrace /Users/annenpolka/ghq/github.com/annenpolka/voidtrace

echo
pass "demo complete"
exit 0
