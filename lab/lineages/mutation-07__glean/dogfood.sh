#!/usr/bin/env bash
# Dogfood glean on copies of nearby repos. Never mutates the originals.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
GLEAN="$ROOT/glean"
PYTHON="${PYTHON:-python3}"
BASE="${TMPDIR:-/tmp}/glean-dogfood-$$"
GHQ="${GHQ:-/Users/annenpolka/ghq/github.com/annenpolka}"
trap 'rm -rf "$BASE"' EXIT

chmod +x "$GLEAN"
mkdir -p "$BASE"

assert_eq() {
  local got="$1" want="$2" label="$3"
  if [[ "$got" != "$want" ]]; then
    echo "FAIL $label" >&2
    echo "  want: $(printf %q "$want")" >&2
    echo "  got:  $(printf %q "$got")" >&2
    exit 1
  fi
  echo "ok  $label"
}

clone_clean() {
  local src="$1" dst="$2"
  git clone --local --quiet "$src" "$dst"
  git -C "$dst" config commit.gpgsign false
  git -C "$dst" config user.email "glean@example.com"
  git -C "$dst" config user.name "glean"
}

# Overlay another repo's dirty files onto a clean clone (copy, don't mutate src).
overlay_dirty() {
  local src="$1" dst="$2"
  "$PYTHON" - "$src" "$dst" <<'PY'
import os, shutil, subprocess, sys
from pathlib import Path

src, dst = Path(sys.argv[1]), Path(sys.argv[2])

def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True)

raw = git(src, "diff", "--name-status", "--no-renames", "-z", "HEAD").stdout.split(b"\0")
parts = [p for p in raw if p]
if len(parts) % 2 != 0:
    raise SystemExit("bad name-status")
for i in range(0, len(parts), 2):
    st = parts[i].decode("ascii", "replace")[:1]
    path = os.fsdecode(parts[i + 1])
    s, d = src / path, dst / path
    if st == "D":
        try:
            d.unlink()
        except FileNotFoundError:
            pass
        continue
    if s.is_file():
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(s, d)

raw = git(src, "ls-files", "-z", "--others", "--exclude-standard").stdout.split(b"\0")
for p in raw:
    if not p:
        continue
    path = os.fsdecode(p)
    s, d = src / path, dst / path
    if s.is_dir():
        if d.exists():
            shutil.copytree(s, d, dirs_exist_ok=True, symlinks=True)
        else:
            shutil.copytree(s, d, symlinks=True)
    elif s.is_file():
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(s, d)
print(f"overlayed dirty tree from {src} -> {dst}")
PY
}

echo "== skills: untracked probe among markdown noise =="
skills_src="$GHQ/skills"
skills="$BASE/skills"
clone_clean "$skills_src" "$skills"
echo "noise $(date)" >> "$skills/README.md"
echo "noise $(date)" >> "$skills/debug-mode/SKILL.md"
printf '%s\n' 'GLEAN_PROBE_MARKER' > "$skills/syntax-reference/glean_probe.md"
json="$("$PYTHON" "$GLEAN" -C "$skills" --format json -v -- "$PYTHON" -c "from pathlib import Path; t=Path('syntax-reference/glean_probe.md').read_text(); assert 'GLEAN_PROBE_MARKER' in t; print('ok')")"
echo "$json" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert [w["path"] for w in d["wheat"]]==["syntax-reference/glean_probe.md"], d
assert d["wheat"][0]["kind"]=="untracked", d
chaff={c["path"] for c in d["chaff"]}
assert "README.md" in chaff and "debug-mode/SKILL.md" in chaff, d
print("ok  skills untracked wheat; %d chaff files, %d trials" % (len(d["chaff"]), d["trials"]))
'
test -f "$skills/syntax-reference/glean_probe.md"
grep -q "noise" "$skills/README.md"
echo "ok  skills working tree restored"

echo "== sitbone: marker in Swift source, noise elsewhere =="
sit_src="$GHQ/sitbone"
sit="$BASE/sitbone"
clone_clean "$sit_src" "$sit"
echo "// noise" >> "$sit/Package.swift"
echo "noise" >> "$sit/README.md"
printf '\nfunc glean_probe_marker() {}\n' >> "$sit/Sources/Sitbone/SitboneApp.swift"
json="$("$PYTHON" "$GLEAN" -C "$sit" --format json -v -- "$PYTHON" -c "from pathlib import Path; t=Path('Sources/Sitbone/SitboneApp.swift').read_text(); assert 'glean_probe_marker' in t; print('ok')")"
echo "$json" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert [w["path"] for w in d["wheat"]]==["Sources/Sitbone/SitboneApp.swift"], d
chaff={c["path"] for c in d["chaff"]}
assert "README.md" in chaff and "Package.swift" in chaff, d
print("ok  sitbone file wheat; %d trials" % d["trials"])
'

echo "== voidtrace: untracked script vs package.json noise =="
vt_src="$GHQ/voidtrace"
vt="$BASE/voidtrace"
clone_clean "$vt_src" "$vt"
echo "// noise" >> "$vt/package.json"
mkdir -p "$vt/.agents/skills/voidtrace/scripts"
printf '%s\n' 'export const glean_probe_marker = true;' > "$vt/.agents/skills/voidtrace/scripts/glean_probe.ts"
json="$("$PYTHON" "$GLEAN" -C "$vt" --format json -v -- "$PYTHON" -c "from pathlib import Path; t=Path('.agents/skills/voidtrace/scripts/glean_probe.ts').read_text(); assert 'glean_probe_marker' in t; print('ok')")"
echo "$json" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert [w["path"] for w in d["wheat"]]==[".agents/skills/voidtrace/scripts/glean_probe.ts"], d
assert d["wheat"][0]["kind"]=="untracked", d
print("ok  voidtrace untracked wheat; %d trials" % d["trials"])
'

echo "== kizu: whole-file wheat (two edits in app.rs cannot split) =="
kz_src="$GHQ/kizu"
kz="$BASE/kizu"
clone_clean "$kz_src" "$kz"
echo "noise" >> "$kz/README.md"
echo "// noise" >> "$kz/src/config.rs"
# two spatially separated edits in one file: header comment + trailing probe
printf '%s\n' '// glean chaff header' | cat - "$kz/src/app.rs" > "$kz/src/app.rs.tmp" && mv "$kz/src/app.rs.tmp" "$kz/src/app.rs"
printf '\n\npub fn glean_probe_marker() {}\n' >> "$kz/src/app.rs"
json="$("$PYTHON" "$GLEAN" -C "$kz" --format json -v -- "$PYTHON" -c "from pathlib import Path; t=Path('src/app.rs').read_text(); assert 'glean_probe_marker' in t; print('ok')")"
echo "$json" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert [w["path"] for w in d["wheat"]]==["src/app.rs"], d
chaff={c["path"] for c in d["chaff"]}
assert "README.md" in chaff and "src/config.rs" in chaff, d
print("ok  kizu whole-file wheat (cannot split header vs probe); %d trials" % d["trials"])
'

echo "== kizu: untracked probe instead of editing app.rs =="
kz2="$BASE/kizu2"
clone_clean "$kz_src" "$kz2"
echo "noise" >> "$kz2/README.md"
echo "// noise" >> "$kz2/src/app.rs"
printf '%s\n' 'pub fn glean_probe_marker() {}' > "$kz2/src/glean_probe.rs"
json="$("$PYTHON" "$GLEAN" -C "$kz2" --format json -- "$PYTHON" -c "from pathlib import Path; t=Path('src/glean_probe.rs').read_text(); assert 'glean_probe_marker' in t; print('ok')")"
echo "$json" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert [w["path"] for w in d["wheat"]]==["src/glean_probe.rs"], d
assert d["wheat"][0]["kind"]=="untracked", d
print("ok  kizu untracked wheat vs dirty app.rs; %d trials" % d["trials"])
'

echo "== tenaoshi: overlay real dirty tree + one guilty file =="
tn_src="$GHQ/tenaoshi"
tn="$BASE/tenaoshi"
clone_clean "$tn_src" "$tn"
overlay_dirty "$tn_src" "$tn"
# marker in a file that was clean in HEAD relative to the overlay
if grep -q GLEAN_PROBE_MARKER "$tn/tools/e2e/verify-log.ts" 2>/dev/null; then
  echo "unexpected marker already present" >&2
  exit 1
fi
printf '\nexport const GLEAN_PROBE_MARKER = true;\n' >> "$tn/tools/e2e/verify-log.ts"
nfiles="$("$PYTHON" - <<PY
import subprocess
from pathlib import Path
repo = Path("$tn")
# count via glean json later
print("counted after glean")
PY
)"
tn_err="$BASE/tenaoshi.err"
json="$("$PYTHON" "$GLEAN" -C "$tn" --format json -v -- "$PYTHON" -c "from pathlib import Path; t=Path('tools/e2e/verify-log.ts').read_text(); assert 'GLEAN_PROBE_MARKER' in t; print('ok')" 2>"$tn_err")"
echo "$json" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
print("tenaoshi dirty files:", len(d["wheat"])+len(d["chaff"]), "wheat:", [w["path"] for w in d["wheat"]], "trials:", d["trials"])
assert [w["path"] for w in d["wheat"]]==["tools/e2e/verify-log.ts"], d
assert len(d["chaff"]) >= 10, "expected a fat real dirty tree, got %s" % len(d["chaff"])
print("ok  tenaoshi real-dirt overlay; wheat is the one marker file")
'
grep -q "more)" "$tn_err"
! grep -q "contracts/testcases/CTR-020.json" "$tn_err"
echo "ok  tenaoshi verbose log is compact"
drop="$("$PYTHON" "$GLEAN" -C "$tn" --format drop -- "$PYTHON" -c "from pathlib import Path; t=Path('tools/e2e/verify-log.ts').read_text(); assert 'GLEAN_PROBE_MARKER' in t; print('ok')")"
echo "$drop" | grep -q "git restore --worktree --source=HEAD"
echo "$drop" | grep -q "rm -f --"
echo "$drop" | grep -qv "tools/e2e/verify-log.ts"
echo "$drop" | grep -q "EditPlan.swift"
echo "ok  tenaoshi drop script restores/rms chaff only"
grep -q GLEAN_PROBE_MARKER "$tn/tools/e2e/verify-log.ts"
test -f "$tn/Engine/Sources/TenaoshiEngine/EditPlan.swift"
echo "ok  tenaoshi restored (drop format is inert)"

echo
echo "all dogfood cases passed"
exit 0
