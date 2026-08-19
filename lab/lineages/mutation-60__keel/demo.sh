#!/usr/bin/env bash
# Exercise keel: mint once, resolve later, never re-supply path:line.
# Keeps pin v0.4/v0.5 refuses (leftover stub, extract-and-keep) and adds
# the origin mutation: depth-1 clone of the same repo resolves; foreign
# repo fail-closes; orphan extra root is still the same project.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
KEEL="$ROOT/keel"
chmod +x "$KEEL"

if ! command -v python3 >/dev/null; then
  echo "demo.sh: python3 is required" >&2
  exit 1
fi
if ! command -v git >/dev/null; then
  echo "demo.sh: git is required" >&2
  exit 1
fi

fail() { echo "FAIL: $*" >&2; exit 1; }
pass() { echo "PASS: $*"; }

echo "== 0. selftest =="
"$KEEL" selftest || fail "selftest"
"$KEEL" --selftest >/dev/null || fail "--selftest flag"
pass "selftest"

TMP="$(mktemp -d "${TMPDIR:-/tmp}/keel-demo.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

REPO="$TMP/ugly"
mkdir -p "$REPO/src" "$REPO/notes" "$REPO/vendor/nested"

cat > "$REPO/src/calc.py" <<'PY'
"""tiny calculator."""

def add(a, b):
    """Return the sum of a and b."""
    return a + b

def secret_sauce(x):
    MAGIC = 0xDEADBEEF
    return x ^ MAGIC

def doomed():
    return "this will be deleted"

def helper_keep():
    return "stable helper"
PY

cat > "$REPO/Makefile" <<'MK'
.PHONY: test
test:
	python src/calc.py
MK

cat > "$REPO/notes/file with spaces.txt" <<'TXT'
see src/calc.py for MAGIC
line two of the spaced file
TXT

cat > "$REPO/src/weird:colon.py" <<'PY'
COLON_FILE = True
print("colon-named file")
PY

cat > "$REPO/src/日本語.py" <<'PY'
def greet():
    return "こんにちは"
PY

python3 - "$REPO" <<'PY'
from pathlib import Path
import sys
repo = Path(sys.argv[1])
p = repo / "src" / ("caf" + "\u00e9" + ".py")
p.write_text("def cafe_fn():\n    return 1\n", encoding="utf-8")
PY

mkdir -p "$REPO/vendor/nested/src"
echo 'NESTED = 1' > "$REPO/vendor/nested/src/inner.py"
git -C "$REPO/vendor/nested" init -q
git -C "$REPO/vendor/nested" add src/inner.py
git -C "$REPO/vendor/nested" \
  -c user.name=nested -c user.email=nested@example.com \
  commit -q -m 'nested repo seed'

git -C "$REPO" init -q
git -C "$REPO" add src Makefile notes
git -C "$REPO" \
  -c user.name=keel -c user.email=keel@example.com \
  commit -q -m 'v1: original layout'
# Project identity: a remote, not the set of roots.
git -C "$REPO" remote add origin git@github.com:keel-lab/ugly.git
V1="$(git -C "$REPO" rev-parse HEAD)"

mkdir -p "$REPO/src/math"
cat > "$REPO/src/math/ops.py" <<'PY'
"""tiny calculator, renamed and split."""

def add(a, b):
    """Return the sum of a and b."""
    return a + b


def helper_keep():
    return "stable helper"
PY

cat > "$REPO/src/math/sauce.py" <<'PY'
"""extracted condiment."""

def secret_sauce(x, extra=0):
    MAGIC = 0xDEADBEEF
    return (x ^ MAGIC) + extra
PY

rm -f "$REPO/src/calc.py"

cat > "$REPO/Makefile" <<'MK'
.PHONY: test
test:
	python src/math/ops.py
MK

git -C "$REPO" add -A src Makefile notes
git -C "$REPO" \
  -c user.name=keel -c user.email=keel@example.com \
  commit -q -m 'v2: split calc, drop doomed, tweak sauce'
V2="$(git -C "$REPO" rev-parse HEAD)"

echo "== fixture refs =="
echo "V1=$V1"
echo "V2=$V2"
echo "id=$("$KEEL" id --repo "$REPO" --from "$V1" | head -1)"

echo "== 1. mint helper_keep at v1, resolve at v2 without path:line =="
HELPER="$("$KEEL" mint --repo "$REPO" --from "$V1" src/calc.py:14)"
echo "token: $HELPER"
echo "$HELPER" | grep -q '^keel1\.' || fail "mint did not emit keel1. token: $HELPER"
out="$("$KEEL" resolve --repo "$REPO" --to "$V2" --porcelain "$HELPER")"
echo "$out"
echo "$out" | grep -q $'src/math/ops.py:8' || fail "helper_keep did not land in ops.py: $out"
echo "$out" | grep -Eq $'^(moved|same|edited)\t' || fail "unexpected status: $out"
echo "$out" | grep -q $'1.000' || fail "exact helper_keep copy should score 1.000: $out"
pass "stored keel relocated helper_keep into src/math/ops.py"

echo "== 2. resolve refuses a locator (the flipped assumption) =="
if "$KEEL" resolve --repo "$REPO" --to "$V2" src/calc.py:14 >/tmp/keel-resolve-loc.out 2>/tmp/keel-resolve-loc.err; then
  fail "resolve accepted path:line"
fi
grep -q 'locator' /tmp/keel-resolve-loc.err || grep -q 'not a keel' /tmp/keel-resolve-loc.err \
  || fail "resolve error did not name locator/keel: $(cat /tmp/keel-resolve-loc.err)"
pass "resolve refuses path:line; the token is the object"

echo "== 3. mint secret_sauce, resolve after signature drift =="
SAUCE="$("$KEEL" mint --repo "$REPO" --from "$V1" src/calc.py:7)"
out="$("$KEEL" resolve --repo "$REPO" --to "$V2" --porcelain "$SAUCE")"
echo "$out"
echo "$out" | grep -q 'src/math/sauce.py:' || fail "secret_sauce did not follow extract: $out"
echo "$out" | grep -Eq $'^(edited|moved)\t' || fail "expected edited/moved for signature drift: $out"
pass "keel survived secret_sauce signature drift"

echo "== 4. deleted doomed() =="
DOOMED="$("$KEEL" mint --repo "$REPO" --from "$V1" src/calc.py:11)"
out="$("$KEEL" resolve --repo "$REPO" --to "$V2" --porcelain "$DOOMED")"
echo "$out"
echo "$out" | grep -q $'^deleted\t' || fail "doomed() should be deleted: $out"
pass "doomed() reports deleted"

echo "== 5. identity: mint at v2, resolve at v2 scores 1.000 =="
ADD="$("$KEEL" mint --repo "$REPO" --from "$V2" src/math/ops.py:3)"
out="$("$KEEL" resolve --repo "$REPO" --to "$V2" --porcelain "$ADD")"
echo "$out"
echo "$out" | grep -q $'same\t' || fail "identity should be same: $out"
echo "$out" | grep -q $'1.000' || fail "identity score was not 1.000: $out"
pass "same-snapshot identity scores 1.000"

echo "== 6. mint is canonical =="
AGAIN="$("$KEEL" mint --repo "$REPO" --from "$V1" src/calc.py:14)"
[[ "$HELPER" == "$AGAIN" ]] || fail "mint of the same line was not stable"
pass "canonical mint"

echo "== 7. show decodes provenance and keel identity =="
shown="$("$KEEL" show "$HELPER")"
echo "$shown"
echo "$shown" | grep -q 'src/calc.py:14' || fail "show lost minted path: $shown"
echo "$shown" | grep -q 'helper_keep' || fail "show lost line text: $shown"
echo "$shown" | grep -q 'origin:' || fail "show lost origin: $shown"
echo "$shown" | grep -q 'github.com/keel-lab/ugly' || fail "show lost project remote: $shown"
echo "$shown" | grep -E '^\s+- ' | grep -q doomed && fail "sibling def doomed leaked into neighbors: $shown"
pass "show (neighbors in-scope, remotes present)"

echo "== 8. pinfile names, then resolve the file (no locators) =="
PINS="$TMP/review.pins"
"$KEEL" mint --repo "$REPO" --from "$V1" --file "$PINS" --name helper src/calc.py:14 >/dev/null
"$KEEL" mint --repo "$REPO" --from "$V1" --file "$PINS" --name sauce src/calc.py:7 >/dev/null
"$KEEL" mint --repo "$REPO" --from "$V1" --file "$PINS" --name doomed src/calc.py:11 >/dev/null
out="$("$KEEL" resolve --repo "$REPO" --to "$V2" --file "$PINS" --porcelain)"
echo "$out"
echo "$out" | grep -q $'helper' || fail "pinfile lost name helper: $out"
echo "$out" | grep -q $'ops.py' || fail "pinfile helper did not resolve: $out"
echo "$out" | grep -q $'^deleted\tdoomed' || fail "pinfile doomed not deleted: $out"
pass "pinfile roundtrip"

echo "== 9. gitless from-dir / to-dir =="
mkdir -p "$TMP/from/src" "$TMP/to/pkg"
echo 'UNIQUE_TOKEN_QZX = 1' > "$TMP/from/src/old.py"
echo 'x = UNIQUE_TOKEN_QZX' >> "$TMP/from/src/old.py"
echo 'UNIQUE_TOKEN_QZX = 1' > "$TMP/to/pkg/new.py"
DIRPIN="$("$KEEL" mint --from-dir "$TMP/from" src/old.py:1)"
out="$("$KEEL" resolve --to-dir "$TMP/to" --porcelain "$DIRPIN")"
echo "$out"
echo "$out" | grep -q 'pkg/new.py:1' || fail "dir-to-dir unique token missed: $out"
pass "from-dir mint / to-dir resolve (no git)"

echo "== 10. unicode / colon / spaced filenames =="
UNI="$("$KEEL" mint --repo "$REPO" --from "$V1" 'src/日本語.py:1')"
out="$("$KEEL" resolve --repo "$REPO" --to "$V2" --porcelain "$UNI")"
echo "$out" | grep -q 'src/日本語.py:1' || fail "unicode path lost: $out"
COL="$("$KEEL" mint --repo "$REPO" --from "$V1" 'src/weird:colon.py:1')"
out="$("$KEEL" resolve --repo "$REPO" --to "$V2" --porcelain "$COL")"
echo "$out" | grep -q 'src/weird:colon.py:1' || fail "colon filename lost: $out"
SPC="$("$KEEL" mint --repo "$REPO" --from "$V1" 'notes/file with spaces.txt:1')"
out="$("$KEEL" resolve --repo "$REPO" --to "$V2" --porcelain "$SPC")"
echo "$out" | grep -q 'notes/file with spaces.txt:1' || fail "spaced filename lost: $out"
pass "unicode / colon / spaced filenames"

echo "== 11. json shape =="
out="$("$KEEL" resolve --repo "$REPO" --to "$V2" --json "$HELPER")"
echo "$out"
python3 -c 'import json,sys; o=json.loads(sys.argv[1]); assert o["status"] in ("moved","edited","same"); assert o["to"]["path"].endswith("ops.py"); assert o["keel"].startswith("keel1."); assert o.get("origin") and "keel-lab/ugly" in o["origin"]' "$out"
pass "json output"

echo "== 12. keel1. argv implies resolve, flags on either side =="
out="$("$KEEL" --porcelain "$HELPER" --repo "$REPO" --to "$V2")"
echo "$out" | grep -q 'ops.py' || fail "flags-before-token did not resolve: $out"
out="$("$KEEL" "$HELPER" --repo "$REPO" --to "$V2" --porcelain)"
echo "$out" | grep -q 'ops.py' || fail "bare token did not resolve: $out"
pass "bare keel1. token implies resolve"

echo "== 13. leftover stub at old path must not steal the pin =="
STUB="$TMP/stubrepo"
mkdir -p "$STUB/src"
cat > "$STUB/src/calc.py" <<'PY'
def add(a, b):
    """Return the sum of a and b."""
    return a + b

def helper_keep():
    return "stable helper"
PY
git -C "$STUB" init -q
git -C "$STUB" add src
git -C "$STUB" -c user.name=keel -c user.email=keel@example.com commit -q -m 'stub-v1'
git -C "$STUB" remote add origin git@github.com:keel-lab/stub.git
STUB_V1="$(git -C "$STUB" rev-parse HEAD)"
mkdir -p "$STUB/src/calc" "$STUB/src/legacy"
cat > "$STUB/src/calc.py" <<'PY'
def helper_keep():
    from src.calc.ops import helper_keep as impl
    return impl()

def add(a, b):
    from src.calc.ops import add as _add
    return _add(a, b)
PY
cat > "$STUB/src/calc/ops.py" <<'PY'
def add(a, b):
    """Return the sum of a and b."""
    return a + b

def helper_keep():
    return "stable helper"
PY
cat > "$STUB/src/legacy/calc.py" <<'PY'
def helper_keep():
    return "stable helper"
PY
git -C "$STUB" add -A src
git -C "$STUB" -c user.name=keel -c user.email=keel@example.com commit -q -m 'stub-v2 leftover wrapper'
STUB_V2="$(git -C "$STUB" rev-parse HEAD)"
STUBPIN="$("$KEEL" mint --repo "$STUB" --from "$STUB_V1" src/calc.py:5)"
out="$("$KEEL" resolve --repo "$STUB" --to "$STUB_V2" --porcelain "$STUBPIN")"
echo "$out"
dest="$(printf '%s\n' "$out" | awk -F'\t' '{print $4}')"
echo "$dest" | grep -q '^src/calc/ops.py:' || fail "leftover stub split did not land in ops.py: $out"
echo "$dest" | grep -q '^src/calc.py:' && fail "leftover stub at old path stole the pin: $out"
echo "$out" | grep -q $'^shifted\t' && fail "stub scored as shifted identity: $out"
echo "$dest" | grep -q 'legacy/calc.py' && fail "basename bait stole the pin: $out"
echo "$out" | grep -q 'leftover stub' || fail "note did not name leftover stub: $out"
pass "neighbor body beat leftover stub and basename bait"

echo "== 14. extract-and-keep is not a move =="
KEEP="$TMP/keeprepo"
mkdir -p "$KEEP/src"
cat > "$KEEP/src/calc.py" <<'PY'
def add(a, b):
    return a + b

def helper_keep():
    return "stable helper"
PY
git -C "$KEEP" init -q
git -C "$KEEP" add src
git -C "$KEEP" -c user.name=keel -c user.email=keel@example.com commit -q -m 'keep-v1'
git -C "$KEEP" remote add origin git@github.com:keel-lab/keep.git
KEEP_V1="$(git -C "$KEEP" rev-parse HEAD)"
mkdir -p "$KEEP/src/calc" "$KEEP/src/legacy"
cp "$KEEP/src/calc.py" "$KEEP/src/calc/ops.py"
cat > "$KEEP/src/legacy/calc.py" <<'PY'
def helper_keep():
    return "stable helper"
PY
git -C "$KEEP" add -A src
git -C "$KEEP" -c user.name=keel -c user.email=keel@example.com commit -q -m 'keep-v2 extract, origin untouched'
KEEP_V2="$(git -C "$KEEP" rev-parse HEAD)"
KEEPPIN="$("$KEEL" mint --repo "$KEEP" --from "$KEEP_V1" src/calc.py:4)"
out="$("$KEEL" resolve --repo "$KEEP" --to "$KEEP_V2" --porcelain "$KEEPPIN")"
echo "$out"
dest="$(printf '%s\n' "$out" | awk -F'\t' '{print $4}')"
echo "$dest" | grep -q '^src/calc.py:' || fail "extract-and-keep left the origin: $out"
echo "$dest" | grep -q '^src/calc/ops.py:' && fail "extract-and-keep reported as move to ops.py: $out"
echo "$out" | grep -q $'^moved\t' && fail "extract-and-keep classified as moved: $out"
echo "$out" | grep -q 'basename bait src/calc.py' && fail "origin body called basename bait: $out"
echo "$out" | grep -q 'extracted copy' || fail "note did not name extracted copy: $out"
pass "extract-and-keep stays at origin"

echo "== 15. leftover + renamed package must not tie with basename bait =="
MATH="$TMP/mathrepo"
mkdir -p "$MATH/src"
cat > "$MATH/src/calc.py" <<'PY'
def add(a, b):
    return a + b

def helper_keep():
    return "stable helper"
PY
git -C "$MATH" init -q
git -C "$MATH" add src
git -C "$MATH" -c user.name=keel -c user.email=keel@example.com commit -q -m 'math-v1'
git -C "$MATH" remote add origin git@github.com:keel-lab/math.git
MATH_V1="$(git -C "$MATH" rev-parse HEAD)"
mkdir -p "$MATH/src/math" "$MATH/src/legacy"
cat > "$MATH/src/calc.py" <<'PY'
def helper_keep():
    from src.math.ops import helper_keep as impl
    return impl()

def add(a, b):
    from src.math.ops import add as _add
    return _add(a, b)
PY
cat > "$MATH/src/math/ops.py" <<'PY'
def add(a, b):
    return a + b

def helper_keep():
    return "stable helper"
PY
cat > "$MATH/src/legacy/calc.py" <<'PY'
def helper_keep():
    return "stable helper"
PY
git -C "$MATH" add -A src
git -C "$MATH" -c user.name=keel -c user.email=keel@example.com commit -q -m 'math-v2 leftover wrapper, renamed extract'
MATH_V2="$(git -C "$MATH" rev-parse HEAD)"
MATHPIN="$("$KEEL" mint --repo "$MATH" --from "$MATH_V1" src/calc.py:4)"
out="$("$KEEL" resolve --repo "$MATH" --to "$MATH_V2" --porcelain "$MATHPIN")"
echo "$out"
mdest="$(printf '%s\n' "$out" | awk -F'\t' '{print $4}')"
echo "$out" | grep -q $'^ambiguous\t' && fail "renamed leftover tied with basename bait: $out"
echo "$mdest" | grep -q '^src/math/ops.py:' || fail "renamed leftover did not land in math/ops.py: $out"
echo "$mdest" | grep -q 'legacy/calc.py' && fail "basename bait stole the renamed extract: $out"
echo "$out" | grep -q 'leftover stub' || fail "renamed leftover unnamed stub: $out"
pass "leftover + src/math/ops.py beat basename bait"

echo "== 16. extract-and-keep to a renamed package is still identity =="
KEEPM="$TMP/keepmath"
mkdir -p "$KEEPM/src"
cat > "$KEEPM/src/calc.py" <<'PY'
def add(a, b):
    return a + b

def helper_keep():
    return "stable helper"
PY
git -C "$KEEPM" init -q
git -C "$KEEPM" add src
git -C "$KEEPM" -c user.name=keel -c user.email=keel@example.com commit -q -m 'keepmath-v1'
git -C "$KEEPM" remote add origin git@github.com:keel-lab/keepmath.git
KEEPM_V1="$(git -C "$KEEPM" rev-parse HEAD)"
mkdir -p "$KEEPM/src/math" "$KEEPM/src/legacy"
cp "$KEEPM/src/calc.py" "$KEEPM/src/math/ops.py"
cat > "$KEEPM/src/legacy/calc.py" <<'PY'
def helper_keep():
    return "stable helper"
PY
git -C "$KEEPM" add -A src
git -C "$KEEPM" -c user.name=keel -c user.email=keel@example.com commit -q -m 'keepmath-v2 extract to math, origin untouched'
KEEPM_V2="$(git -C "$KEEPM" rev-parse HEAD)"
KEEPMPIN="$("$KEEL" mint --repo "$KEEPM" --from "$KEEPM_V1" src/calc.py:4)"
out="$("$KEEL" resolve --repo "$KEEPM" --to "$KEEPM_V2" --porcelain "$KEEPMPIN")"
echo "$out"
kmdest="$(printf '%s\n' "$out" | awk -F'\t' '{print $4}')"
echo "$kmdest" | grep -q '^src/calc.py:' || fail "renamed extract-and-keep left the origin: $out"
echo "$out" | grep -q $'^moved\t' && fail "renamed extract-and-keep classified as moved: $out"
echo "$out" | grep -q 'extracted copy' || fail "renamed keep note did not name extract: $out"
pass "extract-and-keep to src/math/ops.py stays at origin"

echo "== 17. leftover import beats same-basename extract bait =="
SAMEB="$TMP/samebase"
mkdir -p "$SAMEB/src"
cat > "$SAMEB/src/calc.py" <<'PY'
def add(a, b):
    return a + b

def helper_keep():
    return "stable helper"
PY
git -C "$SAMEB" init -q
git -C "$SAMEB" add src
git -C "$SAMEB" -c user.name=keel -c user.email=keel@example.com commit -q -m 'sameb-v1'
SAMEB_V1="$(git -C "$SAMEB" rev-parse HEAD)"
mkdir -p "$SAMEB/src/math" "$SAMEB/src/legacy"
cat > "$SAMEB/src/calc.py" <<'PY'
def helper_keep():
    from src.math.calc import helper_keep as impl
    return impl()

def add(a, b):
    from src.math.calc import add as _add
    return _add(a, b)
PY
cat > "$SAMEB/src/math/calc.py" <<'PY'
def add(a, b):
    return a + b

def helper_keep():
    return "stable helper"
PY
cat > "$SAMEB/src/legacy/calc.py" <<'PY'
def helper_keep():
    return "stable helper"
PY
git -C "$SAMEB" add -A src
git -C "$SAMEB" -c user.name=keel -c user.email=keel@example.com commit -q -m 'sameb-v2 leftover names math.calc'
SAMEB_V2="$(git -C "$SAMEB" rev-parse HEAD)"
SAMEBPIN="$("$KEEL" mint --repo "$SAMEB" --from "$SAMEB_V1" src/calc.py:4)"
out="$("$KEEL" resolve --repo "$SAMEB" --to "$SAMEB_V2" --porcelain "$SAMEBPIN")"
echo "$out"
sbdest="$(printf '%s\n' "$out" | awk -F'\t' '{print $4}')"
echo "$out" | grep -q $'^ambiguous\t' && fail "same-basename extract tied with bait: $out"
echo "$sbdest" | grep -q '^src/math/calc.py:' || fail "leftover import did not land on math/calc.py: $out"
pass "leftover import picks src/math/calc.py over src/legacy/calc.py"

echo "== 18. identical helpers are ambiguous =="
IDENT_FROM="$TMP/ident_from"
IDENT_TO="$TMP/ident_to"
mkdir -p "$IDENT_FROM/src" "$IDENT_TO/a" "$IDENT_TO/z"
cat > "$IDENT_FROM/src/calc.py" <<'PY'
def helper_keep():
    return "stable helper"
PY
cat > "$IDENT_TO/a/ops.py" <<'PY'
def helper_keep():
    return "stable helper"
PY
cat > "$IDENT_TO/z/calc.py" <<'PY'
def helper_keep():
    return "stable helper"
PY
IDPIN="$("$KEEL" mint --from-dir "$IDENT_FROM" src/calc.py:1)"
out="$("$KEEL" resolve --to-dir "$IDENT_TO" --porcelain "$IDPIN")"
echo "$out"
echo "$out" | grep -q $'^ambiguous\t' || fail "identical helpers should be ambiguous: $out"
if "$KEEL" resolve --to-dir "$IDENT_TO" --strict --porcelain "$IDPIN" >/tmp/keel-amb.out 2>/tmp/keel-amb.err; then
  fail "strict should fail closed on ambiguous"
fi
pass "identical helpers → ambiguous (strict fails)"

echo "== 19. files >1MB still mint and resolve =="
HUGE="$TMP/huge"
mkdir -p "$HUGE/src"
python3 - "$HUGE" <<'PY'
from pathlib import Path
import sys
root = Path(sys.argv[1])
body = 'def unique_locus_ZEBRA99():\n    return 1\n' + ('#' * 1_200_000) + '\n'
p = root / "src" / "godfile.py"
p.write_text(body, encoding="utf-8")
print(p.stat().st_size)
PY
GOD="$("$KEEL" mint --from-dir "$HUGE" src/godfile.py:1)"
out="$("$KEEL" resolve --to-dir "$HUGE" --porcelain "$GOD")"
echo "$out"
echo "$out" | grep -q 'src/godfile.py:1' || fail "godfile pin did not resolve: $out"
pass "1.2MB godfile minted and resolved"

echo "== 20. NFD locator binds NFC path =="
CAFEPIN="$(python3 - "$KEEL" "$REPO" "$V1" <<'PY'
import subprocess, sys, unicodedata
keel, repo, v1 = sys.argv[1], sys.argv[2], sys.argv[3]
nfd = unicodedata.normalize("NFD", "src/café.py") + ":1"
r = subprocess.run([keel, "mint", "--repo", repo, "--from", v1, nfd], capture_output=True, text=True)
sys.stderr.write(r.stderr)
if r.returncode != 0:
    sys.exit(r.returncode or 1)
print(r.stdout.strip())
PY
)"
echo "$CAFEPIN" | grep -q '^keel1\.' || fail "NFD mint failed: $CAFEPIN"
out="$("$KEEL" resolve --repo "$REPO" --to "$V2" --porcelain "$CAFEPIN")"
echo "$out" | grep -q 'src/caf' || fail "NFC path lost after NFD mint: $out"
pass "NFD mint of NFC café.py"

echo "== 21. missing --to ref is an error, not deleted =="
set +e
out="$("$KEEL" resolve --repo "$REPO" --to this-ref-does-not-exist --porcelain "$HELPER" 2>"$TMP/bad-ref.err")"
rc=$?
set -e
[[ "$rc" -ne 0 ]] || fail "missing --to ref exited 0"
echo "$out" | grep -q $'^deleted\t' && fail "missing --to looked like deletion: $out"
grep -qi 'unknown ref\|not a.*ref\|cannot list' "$TMP/bad-ref.err" \
  || fail "missing --to error was not about the ref: $(cat "$TMP/bad-ref.err")"
pass "missing --to is an error"

echo "== 22. truncated tokens fail closed =="
HALF="${HELPER:0:24}"
set +e
out="$("$KEEL" resolve --repo "$REPO" --to "$V2" --porcelain "$HALF" 2>"$TMP/half.err")"
rc=$?
set -e
[[ "$rc" -ne 0 ]] || fail "truncated token resolve exited 0"
echo "$out" | grep -Eq $'^(unresolved|moved|deleted|shifted|same)\t' \
  && fail "truncated token printed a result row: $out"
grep -qi 'corrupt\|not a keel' "$TMP/half.err" \
  || fail "truncated token stderr was not fail-closed: $(cat "$TMP/half.err")"
pass "truncated tokens fail closed"

echo "== 23. foreign repo fail-closes =="
UNREL="$TMP/unrel"
mkdir -p "$UNREL/pkg"
cat > "$UNREL/pkg/util.py" <<'PY'
def helper_keep():
    return "stable helper"
PY
git -C "$UNREL" init -q
git -C "$UNREL" add pkg/util.py
git -C "$UNREL" -c user.name=keel -c user.email=keel@example.com commit -q -m 'unrelated helper'
git -C "$UNREL" remote add origin git@github.com:other/util.git
set +e
out="$("$KEEL" resolve --repo "$UNREL" --to HEAD --porcelain "$HELPER" 2>"$TMP/unrel.err")"
rc=$?
set -e
echo "unrel rc=$rc stdout=$out"
cat "$TMP/unrel.err"
[[ "$rc" -eq 1 ]] || fail "foreign repo resolve exited $rc (want 1)"
echo "$out" | grep -q $'^moved\t' && fail "foreign repo silently landed: $out"
grep -qi 'different repository\|any-repo' "$TMP/unrel.err" \
  || fail "foreign repo error did not name origin: $(cat "$TMP/unrel.err")"
out="$("$KEEL" resolve --repo "$UNREL" --to HEAD --any-repo --porcelain "$HELPER")"
echo "$out"
echo "$out" | grep -q 'pkg/util.py' || fail "--any-repo should opt into foreign resolve: $out"
# --to-dir of a subdirectory of the foreign repo must inherit origin
set +e
out="$("$KEEL" resolve --to-dir "$UNREL/pkg" --porcelain "$HELPER" 2>"$TMP/unrel-dir.err")"
rc=$?
set -e
[[ "$rc" -eq 1 ]] || fail "foreign --to-dir subdirectory exited $rc (want 1)"
pass "foreign repo refused (root and subdirectory); --any-repo overrides"

echo "== 24. depth-1 clone of the same repo still resolves =="
# Local-path `git clone --depth 1 $REPO` is NOT shallow (git ignores --depth).
# file:// is the real graft: dest root becomes HEAD, mint-time parent is gone.
SHALLOW="$TMP/shallow"
git clone -q --depth 1 "file://$REPO" "$SHALLOW"
[[ "$(git -C "$SHALLOW" rev-parse --is-shallow-repository)" == "true" ]] \
  || fail "file:// --depth 1 was not shallow"
[[ -f "$SHALLOW/.git/shallow" ]] || fail "missing $SHALLOW/.git/shallow"
set +e
git -C "$SHALLOW" cat-file -e "$V1"
v1_in_shallow=$?
set -e
[[ "$v1_in_shallow" -ne 0 ]] || fail "shallow still has V1; this is not a graft"
FULL_ROOTS="$(git -C "$REPO" rev-list --max-parents=0 --all | tr '\n' ' ')"
SH_ROOTS="$(git -C "$SHALLOW" rev-list --max-parents=0 --all | tr '\n' ' ')"
echo "full id:    $("$KEEL" id --repo "$REPO" --from "$V1" | head -1)"
echo "shallow id: $("$KEEL" id --repo "$SHALLOW" | head -1)"
echo "shallow roots: $SH_ROOTS"
echo "full roots:    $FULL_ROOTS"
[[ "$SH_ROOTS" != "$FULL_ROOTS" ]] || fail "shallow roots still equal full roots"
# file:// dest has no network remote of its own; inherit from the hop.
"$KEEL" id --repo "$SHALLOW" | grep -q 'github.com/keel-lab/ugly' \
  || fail "shallow id did not inherit project remote"
out="$("$KEEL" resolve --repo "$SHALLOW" --to HEAD --porcelain "$HELPER")"
echo "$out"
echo "$out" | grep -q 'src/math/ops.py' || fail "depth-1 clone of same repo did not resolve: $out"
echo "$out" | grep -q $'^deleted\t' && fail "depth-1 clone looked like deletion: $out"
pass "file:// depth-1 clone of the same project resolves without --any-repo"

echo "== 24b. remotes-less mint, then advance, then file:// depth-1 =="
# Hard case: token was minted when HEAD was V1. Dest is a graft of V2.
# No network remotes. Dest does not contain V1. Follow dest origin.
BARE="$TMP/barefull"
mkdir -p "$BARE/src"
cat > "$BARE/src/calc.py" <<'PY'
def helper_keep():
    return "stable helper"
PY
git -C "$BARE" init -q
git -C "$BARE" add src
git -C "$BARE" -c user.name=keel -c user.email=keel@example.com commit -q -m 'bare-v1'
BARE_V1="$(git -C "$BARE" rev-parse HEAD)"
BAREPIN="$("$KEEL" mint --repo "$BARE" --from "$BARE_V1" src/calc.py:1)"
echo "bare token origin: $("$KEEL" show "$BAREPIN" | grep origin)"
echo '# later' >> "$BARE/src/calc.py"
git -C "$BARE" add src
git -C "$BARE" -c user.name=keel -c user.email=keel@example.com commit -q -m 'bare-v2'
BARESH="$TMP/bareshallow"
git clone -q --depth 1 "file://$BARE" "$BARESH"
[[ "$(git -C "$BARESH" rev-parse --is-shallow-repository)" == "true" ]] \
  || fail "bare file:// clone was not shallow"
set +e
git -C "$BARESH" cat-file -e "$BARE_V1"
bare_v1=$?
set -e
[[ "$bare_v1" -ne 0 ]] || fail "bare shallow still has V1"
out="$("$KEEL" resolve --repo "$BARESH" --to HEAD --porcelain "$BAREPIN")"
echo "$out"
echo "$out" | grep -q 'src/calc.py:1' || fail "remotes-less file:// shallow did not follow origin: $out"
pass "remotes-less mint + later file:// depth-1 still resolves (follow origin)"

echo "== 25. orphan extra root is still the same repo =="
ORPH="$TMP/orph"
git clone -q "$REPO" "$ORPH"
ORPH_MAIN="$(git -C "$ORPH" rev-parse --abbrev-ref HEAD)"
git -C "$ORPH" checkout --orphan extra-hist
echo 'orphan only' > "$ORPH/orphan-only.txt"
git -C "$ORPH" add orphan-only.txt
git -C "$ORPH" -c user.name=keel -c user.email=keel@example.com commit -q -m 'orphan root'
git -C "$ORPH" checkout -q "$ORPH_MAIN"
echo "orph roots: $(git -C "$ORPH" rev-list --max-parents=0 --all | tr '\n' ' ')"
out="$("$KEEL" resolve --repo "$ORPH" --to "$V2" --porcelain "$HELPER")"
echo "$out"
echo "$out" | grep -q 'src/math/ops.py' || fail "orphan extra root made the repo foreign: $out"
pass "orphan extra root still the same keel"

# --- real repo dogfood (read-only) ---
KIZU="${KIZU:-/Users/annenpolka/ghq/github.com/annenpolka/kizu}"
if [[ -d "$KIZU/.git" || -f "$KIZU/.git" ]]; then
  echo "== 26. kizu app.rs split: mint at b4e6a5d, resolve HEAD (no path:line) =="
  SEEN="$("$KEEL" mint --repo "$KIZU" --from b4e6a5d src/app.rs:529)"
  echo "seen pin length=${#SEEN}"
  echo "kizu id: $("$KEEL" id --repo "$KIZU" --from b4e6a5d | head -1)"
  out="$("$KEEL" resolve --repo "$KIZU" --to HEAD --porcelain "$SEEN")"
  echo "$out"
  echo "$out" | grep -q 'src/app/layout.rs:' || fail "kizu seen_hunk_fingerprint did not land in layout.rs: $out"
  pass "kizu: keel(src/app.rs:529@b4e6a5d) → src/app/layout.rs"

  echo "== 27. kizu nearest_landing_forward =="
  LAND="$("$KEEL" mint --repo "$KIZU" --from b4e6a5d src/app.rs:543)"
  out="$("$KEEL" resolve --repo "$KIZU" --to HEAD --porcelain "$LAND")"
  echo "$out"
  echo "$out" | grep -q 'src/app/navigation.rs:' || fail "kizu nearest_landing_forward missed navigation.rs: $out"
  pass "kizu: keel(src/app.rs:543) → src/app/navigation.rs"
else
  echo "SKIP kizu dogfood (repo not present at $KIZU)"
fi

VOID="${VOID:-/Users/annenpolka/ghq/github.com/annenpolka/voidtrace}"
if [[ -d "$VOID/.git" || -f "$VOID/.git" ]]; then
  echo "== 28. voidtrace identity sanity =="
  file="$(git -C "$VOID" ls-files 'packages/kernel/src/evaluate.ts' | head -1)"
  if [[ -n "$file" ]]; then
    VP="$("$KEEL" mint --repo "$VOID" --from HEAD "${file}:1")"
    out="$("$KEEL" resolve --repo "$VOID" --to HEAD --porcelain "$VP")"
    echo "$out"
    echo "$out" | grep -q $'^same\t' || fail "voidtrace identity should be same: $out"
    vdest="$(printf '%s\n' "$out" | awk -F'\t' '{print $4}')"
    echo "$vdest" | grep -q 'cli.test.ts' && fail "voidtrace import{ clone stole the pin: $out"
    pass "voidtrace HEAD identity on $file:1"
  fi
fi

TENA="${TENA:-/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi}"
if [[ -d "$TENA/.git" || -f "$TENA/.git" ]]; then
  echo "== 29. tenaoshi KinsokuEngine.transform first-commit → HEAD =="
  TP="$("$KEEL" mint --repo "$TENA" --from a41089c Engine/Sources/TenaoshiEngine/KinsokuEngine.swift:12)"
  out="$("$KEEL" resolve --repo "$TENA" --to HEAD --porcelain "$TP")"
  echo "$out"
  echo "$out" | grep -q 'KinsokuEngine.swift:12' || fail "tenaoshi transform did not stay on line 12: $out"
  pass "tenaoshi transform keel a41089c → HEAD line 12"
fi

SIT="${SIT:-/Users/annenpolka/ghq/github.com/annenpolka/sitbone}"
if [[ -d "$SIT/.git" || -f "$SIT/.git" ]]; then
  echo "== 30. sitbone identity (PresenceArbiter.detect) =="
  SP="$("$KEEL" mint --repo "$SIT" --from HEAD Sources/SitboneCore/PresenceArbiter.swift:75)"
  out="$("$KEEL" resolve --repo "$SIT" --to HEAD --porcelain "$SP")"
  echo "$out"
  echo "$out" | grep -q $'^same\t' || fail "sitbone identity should be same: $out"
  echo "$out" | grep -q 'PresenceArbiter.swift:75' || fail "sitbone jumped: $out"
  pass "sitbone HEAD identity on PresenceArbiter.detect"
fi

SKILLS="${SKILLS:-/Users/annenpolka/ghq/github.com/annenpolka/skills}"
if [[ -d "$SKILLS/.git" || -f "$SKILLS/.git" ]]; then
  echo "== 31. skills repo identity (keel id remotes) =="
  sid="$("$KEEL" id --repo "$SKILLS" | head -1)"
  echo "$sid"
  echo "$sid" | grep -q 'github.com/annenpolka/skills' || fail "skills keel missed remote: $sid"
  pass "skills keel id names github.com/annenpolka/skills"
fi

echo
echo "All demo checks passed."
exit 0
