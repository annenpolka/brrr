#!/usr/bin/env bash
# Exercise glean against synthetic git repos. Exit 0 only if every case holds.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
GLEAN="$ROOT/glean"
PYTHON="${PYTHON:-python3}"
BASE="${TMPDIR:-/tmp}/glean-demo-$$"
trap 'rm -rf "$BASE"' EXIT

chmod +x "$GLEAN"
mkdir -p "$BASE"

git_init() {
  local dir="$1"
  mkdir -p "$dir"
  git -C "$dir" init -q
  git -C "$dir" config user.email "glean@example.com"
  git -C "$dir" config user.name "glean"
  git -C "$dir" config commit.gpgsign false
}

commit_all() {
  local dir="$1"
  git -C "$dir" add -A
  git -C "$dir" commit -qm "$2"
}

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

# --- Case 1: one guilty tracked file among unrelated WIP ---
case1="$BASE/one-guilty"
git_init "$case1"
cat > "$case1/app.py" <<'PY'
def add(a, b):
    return a + b
PY
cat > "$case1/helper.py" <<'PY'
NOTE = "untouched"
PY
cat > "$case1/test.py" <<'PY'
from app import add
assert add(2, 3) == 5
print("pass")
PY
echo "hello" > "$case1/README.md"
commit_all "$case1" "base"
echo "hello world" > "$case1/README.md"
cat > "$case1/helper.py" <<'PY'
NOTE = "rewritten comment only"
PY
echo "untracked noise" > "$case1/notes.txt"
cat > "$case1/app.py" <<'PY'
def add(a, b):
    return a - b
PY

got="$("$PYTHON" "$GLEAN" -C "$case1" --format paths -- "$PYTHON" test.py)"
assert_eq "$got" "app.py" "one guilty file among chaff"

# --- Case 2: two files jointly required ---
case2="$BASE/joint"
git_init "$case2"
echo 'KEY = "a"' > "$case2/a.py"
echo 'KEY = "b"' > "$case2/b.py"
echo 'noise = 1' > "$case2/c.py"
cat > "$case2/test.py" <<'PY'
import a, b
assert not (a.KEY == "AX" and b.KEY == "BX")
print("pass")
PY
commit_all "$case2" "base"
echo 'KEY = "AX"' > "$case2/a.py"
echo 'KEY = "BX"' > "$case2/b.py"
echo 'noise = 2' > "$case2/c.py"

got="$("$PYTHON" "$GLEAN" -C "$case2" --format paths -- "$PYTHON" test.py)"
assert_eq "$got" $'a.py\nb.py' "joint wheat keeps both required files"

# --- Case 3: WIP does not affect the command ---
case3="$BASE/irrelevant"
git_init "$case3"
echo 'x = 1' > "$case3/keep.py"
echo 'y = 1' > "$case3/noise.py"
cat > "$case3/test.py" <<'PY'
import keep
assert keep.x == 1
print("pass")
PY
commit_all "$case3" "base"
echo 'y = 99' > "$case3/noise.py"
echo extra > "$case3/README.md"

got="$("$PYTHON" "$GLEAN" -C "$case3" --format json -- "$PYTHON" test.py)"
echo "$got" | "$PYTHON" -c 'import json,sys; d=json.load(sys.stdin); assert d["same"] is True and d["wheat"]==[] and len(d["chaff"])==2, d'
echo "ok  irrelevant WIP is all chaff"

# --- Case 4: weird filenames + nested untracked ---
case4="$BASE/ugly"
git_init "$case4"
mkdir -p "$case4/sub dir"
echo 'VAL = 1' > "$case4/sub dir/weird (x).py"
echo 'other = 1' > "$case4/ok.py"
cat > "$case4/test.py" <<'PY'
import importlib.util, pathlib
p = pathlib.Path(__file__).parent / "sub dir" / "weird (x).py"
spec = importlib.util.spec_from_file_location("weird", p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
assert m.VAL == 1
print("pass")
PY
commit_all "$case4" "base"
echo 'VAL = 2' > "$case4/sub dir/weird (x).py"
echo 'other = 2' > "$case4/ok.py"
mkdir -p "$case4/sub dir/nested"
echo 'nope' > "$case4/sub dir/nested/new file.txt"

got="$("$PYTHON" "$GLEAN" -C "$case4" --format paths -- "$PYTHON" test.py)"
assert_eq "$got" "sub dir/weird (x).py" "spaces and parens in paths"

# --- Case 5: human text + wheat-only patch + restore ---
text="$("$PYTHON" "$GLEAN" -C "$case1" --format text -- "$PYTHON" test.py)"
echo "$text" | grep -q "wheat"
echo "$text" | grep -q "app.py"
echo "$text" | grep -q "untracked"
echo "ok  text format names untracked chaff"
patch="$("$PYTHON" "$GLEAN" -C "$case1" --format patch -- "$PYTHON" test.py)"
echo "$patch" | grep -q "a/app.py"
echo "$patch" | grep -q "return a - b"
echo "$patch" | grep -qv "notes.txt"
echo "ok  patch format is wheat-only"
test -f "$case1/notes.txt"
grep -q "a - b" "$case1/app.py"
echo "ok  working tree restored"

# --- Case 6: python bytecode must not poison isolation ---
case6="$BASE/pycache"
git_init "$case6"
printf '%s\n' 'def add(a,b):' '    return a+b' > "$case6/app.py"
printf '%s\n' 'from app import add' 'assert add(2,3)==5' 'print("pass")' > "$case6/test.py"
echo noise > "$case6/README.md"
commit_all "$case6" "base"
printf '%s\n' 'def add(a,b):' '    return a-b' > "$case6/app.py"
echo more > "$case6/README.md"
got="$(env -u PYTHONDONTWRITEBYTECODE "$PYTHON" "$GLEAN" -C "$case6" --format paths -- "$PYTHON" test.py)"
assert_eq "$got" "app.py" "pycache leak does not hide the guilty file"

# --- Case 7: comment in the test file must be chaff (line-number fingerprint) ---
case7="$BASE/linenos"
git_init "$case7"
printf '%s\n' 'def add(a,b):' '    return a+b' > "$case7/app.py"
printf '%s\n' 'from app import add' 'assert add(2,3)==5' 'print("pass")' > "$case7/test.py"
echo noise > "$case7/README.md"
commit_all "$case7" "base"
printf '%s\n' 'def add(a,b):' '    return a-b' > "$case7/app.py"
printf '%s\n' '# chaff comment' 'from app import add' 'assert add(2,3)==5' 'print("pass")' > "$case7/test.py"
echo more > "$case7/README.md"
got="$("$PYTHON" "$GLEAN" -C "$case7" --format paths -- "$PYTHON" test.py)"
assert_eq "$got" "app.py" "traceback line shift in test.py is chaff"

# --- Case 8: two edits in one file stay one unit (file granularity, not hunks) ---
case8="$BASE/whole-file"
git_init "$case8"
cat > "$case8/app.py" <<'PY'
# header
# pad1
# pad2
# pad3
# pad4
# pad5
# pad6
# pad7
def add(a, b):
    return a + b

def extra():
    return 0
PY
cat > "$case8/test.py" <<'PY'
from app import add
assert add(2, 3) == 5
print("pass")
PY
echo noise > "$case8/README.md"
commit_all "$case8" "base"
cat > "$case8/app.py" <<'PY'
# header changed (would be chaff at hunk grain)
# pad1
# pad2
# pad3
# pad4
# pad5
# pad6
# pad7
def add(a, b):
    return a - b

def extra():
    return 0
PY
echo more > "$case8/README.md"
json8="$("$PYTHON" "$GLEAN" -C "$case8" --format json -- "$PYTHON" test.py)"
echo "$json8" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
wheat=d["wheat"]; chaff=d["chaff"]
assert [w["path"] for w in wheat]==["app.py"], wheat
assert len(wheat)==1, wheat
assert not any("hunk" in w for w in wheat), wheat
assert [c["path"] for c in chaff]==["README.md"], chaff
print("ok  file grain keeps the whole guilty file (no hunk split)")
'

# --- Case 9: nested git repo is visible to the outer glean ---
case9="$BASE/nested"
git_init "$case9"
echo outer > "$case9/root.txt"
commit_all "$case9" "outer"
git_init "$case9/inner"
echo inner > "$case9/inner/secret.txt"
commit_all "$case9/inner" "inner"
echo OUTER > "$case9/root.txt"
echo INNER_CHANGED > "$case9/inner/secret.txt"
got="$("$PYTHON" "$GLEAN" -C "$case9" --format paths -- "$PYTHON" -c "from pathlib import Path; t=Path('inner/secret.txt').read_text(); assert 'INNER_CHANGED' in t; print('ok')")"
assert_eq "$got" "inner/secret.txt" "nested git files are wheat when the command reads them"

# --- Case 10: untracked file is the wheat (the flipped assumption) ---
case10="$BASE/untracked-wheat"
git_init "$case10"
cat > "$case10/app.py" <<'PY'
def add(a, b):
    return a + b
PY
echo "docs" > "$case10/README.md"
commit_all "$case10" "base"
echo "docs changed" > "$case10/README.md"
cat > "$case10/app.py" <<'PY'
def add(a, b):
    return a + b  # comment-only chaff
PY
cat > "$case10/probe.py" <<'PY'
# untracked file the command notices
RAISED = True
PY
got="$("$PYTHON" "$GLEAN" -C "$case10" --format json -- "$PYTHON" -c "from pathlib import Path; t=Path('probe.py').read_text(); assert 'RAISED' in t; print('ok')")"
echo "$got" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
wheat=d["wheat"]
assert [w["path"] for w in wheat]==["probe.py"], wheat
assert wheat[0]["kind"]=="untracked", wheat
chaff={c["path"] for c in d["chaff"]}
assert "README.md" in chaff and "app.py" in chaff, d
print("ok  untracked file is wheat; tracked noise is chaff")
'

# --- Case 11: deleted file is wheat ---
case11="$BASE/deleted"
git_init "$case11"
echo "present" > "$case11/flag.txt"
echo "noise" > "$case11/README.md"
commit_all "$case11" "base"
rm "$case11/flag.txt"
echo "noise2" > "$case11/README.md"
got="$("$PYTHON" "$GLEAN" -C "$case11" --format json -- "$PYTHON" -c "from pathlib import Path; assert not Path('flag.txt').exists(); print('absent')")"
echo "$got" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
wheat=d["wheat"]
assert [w["path"] for w in wheat]==["flag.txt"], wheat
assert wheat[0]["kind"]=="delete", wheat
assert [c["path"] for c in d["chaff"]]==["README.md"], d
print("ok  deleted file is wheat")
'

# --- Case 12: untracked + tracked jointly required ---
case12="$BASE/joint-untracked"
git_init "$case12"
echo 'BASE = "old"' > "$case12/app.py"
cat > "$case12/test.py" <<'PY'
import app
from pathlib import Path
extra = Path("extra.py")
assert not (app.BASE == "new" and extra.exists() and "NEED" in extra.read_text())
print("pass")
PY
echo noise > "$case12/README.md"
commit_all "$case12" "base"
echo 'BASE = "new"' > "$case12/app.py"
echo 'NEED = 1' > "$case12/extra.py"
echo more > "$case12/README.md"
got="$("$PYTHON" "$GLEAN" -C "$case12" --format json -- "$PYTHON" test.py)"
echo "$got" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
paths=[w["path"] for w in d["wheat"]]
kinds={w["path"]: w["kind"] for w in d["wheat"]}
assert paths==["app.py","extra.py"], paths
assert kinds["app.py"]=="modify" and kinds["extra.py"]=="untracked", kinds
print("ok  joint tracked+untracked wheat")
'

# --- Case 13: executable bit on untracked script is restored ---
case13="$BASE/execbit"
git_init "$case13"
echo 'print("ok")' > "$case13/run.py"
commit_all "$case13" "base"
cat > "$case13/probe.sh" <<'SH'
#!/bin/sh
echo PROBE
SH
chmod +x "$case13/probe.sh"
echo noise > "$case13/README.md"
got="$("$PYTHON" "$GLEAN" -C "$case13" --format paths -- sh -c 'test -x probe.sh && grep -q PROBE probe.sh')"
assert_eq "$got" "probe.sh" "untracked executable is wheat"
test -x "$case13/probe.sh"
echo "ok  executable bit restored"

# --- Case 14: --format drop names restore/rm of chaff, not wheat ---
drop="$("$PYTHON" "$GLEAN" -C "$case1" --format drop -- "$PYTHON" test.py)"
echo "$drop" | grep -q "git restore --worktree --source=HEAD"
echo "$drop" | grep -q "README.md"
echo "$drop" | grep -q "helper.py"
echo "$drop" | grep -q "rm -f --"
echo "$drop" | grep -q "notes.txt"
echo "$drop" | grep -qv "app.py"
test -f "$case1/notes.txt"
grep -q "hello world" "$case1/README.md"
echo "ok  drop format is chaff-only and does not mutate by default"

# --- Case 15: --drop actually discards chaff, keeps wheat ---
got="$("$PYTHON" "$GLEAN" -C "$case1" --drop --format paths -- "$PYTHON" test.py)"
assert_eq "$got" "app.py" "drop mode still reports wheat"
grep -q "a - b" "$case1/app.py"
test ! -f "$case1/notes.txt"
grep -qx "hello" "$case1/README.md"
grep -q "untouched" "$case1/helper.py"
echo "ok  --drop leaves only wheat in the worktree"

# --- Case 16: drop quotes paths with spaces ---
drop4="$("$PYTHON" "$GLEAN" -C "$case4" --format drop -- "$PYTHON" test.py)"
echo "$drop4" | grep -q "ok.py"
echo "$drop4" | grep -q "new file.txt"
echo "$drop4" | grep -qv "weird"
echo "ok  drop format quotes spaced chaff paths"

echo
echo "all demo cases passed"
exit 0
