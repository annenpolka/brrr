#!/usr/bin/env bash
# Exercise helm: mint once, resolve later, never re-supply path:line.
# Mutation: leftover is an import relative to the leftover file.
# `from .ops import add` in src/calc.py names dest src/math/ops.py.
# `from src.math import calc` at module level follows.
# `io.fs` ⊂ `audio.fs` stays ambiguous. Origin is remotes + witnesses.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PIN="$ROOT/helm"
chmod +x "$PIN"

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
"$PIN" selftest || fail "selftest"
"$PIN" --selftest >/dev/null || fail "--selftest flag"
pass "selftest"

TMP="$(mktemp -d "${TMPDIR:-/tmp}/pin-demo.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

REPO="$TMP/ugly"
mkdir -p "$REPO/src" "$REPO/notes" "$REPO/vendor/nested"

# --- snapshot v1 ---
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
  -c user.name=helm -c user.email=helm@example.com \
  commit -q -m 'v1: original layout'
V1="$(git -C "$REPO" rev-parse HEAD)"

# --- snapshot v2: rename, split, edit, delete ---
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
  -c user.name=helm -c user.email=helm@example.com \
  commit -q -m 'v2: split calc, drop doomed, tweak sauce'
V2="$(git -C "$REPO" rev-parse HEAD)"
git -C "$REPO" remote add origin git@github.com:keel-lab/ugly.git

echo "== fixture refs =="
echo "V1=$V1"
echo "V2=$V2"

echo "== 1. mint helper_keep at v1, resolve at v2 without path:line =="
HELPER="$("$PIN" mint --repo "$REPO" --from "$V1" src/calc.py:14)"
echo "token: $HELPER"
echo "$HELPER" | grep -q '^helm1\.' || fail "mint did not emit helm1. token: $HELPER"
out="$("$PIN" resolve --repo "$REPO" --to "$V2" --porcelain "$HELPER")"
echo "$out"
echo "$out" | grep -q $'src/math/ops.py:8' || fail "helper_keep did not land in ops.py: $out"
echo "$out" | grep -Eq $'^(moved|same|edited)\t' || fail "unexpected status: $out"
echo "$out" | grep -q $'1.000' || fail "exact helper_keep copy should score 1.000: $out"
pass "stored pin relocated helper_keep into src/math/ops.py"

echo "== 2. resolve refuses a locator (the flipped assumption) =="
if "$PIN" resolve --repo "$REPO" --to "$V2" src/calc.py:14 >/tmp/helm-resolve-loc.out 2>/tmp/helm-resolve-loc.err; then
  fail "resolve accepted path:line"
fi
grep -q 'locator' /tmp/helm-resolve-loc.err || grep -q 'not a pin' /tmp/helm-resolve-loc.err \
  || fail "resolve error did not name locator/pin: $(cat /tmp/helm-resolve-loc.err)"
pass "resolve refuses path:line; the pin is the object"

echo "== 3. mint secret_sauce, resolve after signature drift =="
SAUCE="$("$PIN" mint --repo "$REPO" --from "$V1" src/calc.py:7)"
out="$("$PIN" resolve --repo "$REPO" --to "$V2" --porcelain "$SAUCE")"
echo "$out"
echo "$out" | grep -q 'src/math/sauce.py:' || fail "secret_sauce did not follow extract: $out"
echo "$out" | grep -Eq $'^(edited|moved)\t' || fail "expected edited/moved for signature drift: $out"
pass "pin survived secret_sauce signature drift"

echo "== 4. deleted doomed() =="
DOOMED="$("$PIN" mint --repo "$REPO" --from "$V1" src/calc.py:11)"
out="$("$PIN" resolve --repo "$REPO" --to "$V2" --porcelain "$DOOMED")"
echo "$out"
echo "$out" | grep -q $'^deleted\t' || fail "doomed() should be deleted: $out"
echo "$out" | grep -Eq 'ops.py|sauce.py|helper_keep|gap|context|anchor' || fail "deleted hole had no neighborhood: $out"
pass "doomed() pin reports deleted with neighborhood"

echo "== 5. identity: mint at v2, resolve at v2 scores 1.000 =="
ADD="$("$PIN" mint --repo "$REPO" --from "$V2" src/math/ops.py:3)"
out="$("$PIN" resolve --repo "$REPO" --to "$V2" --porcelain "$ADD")"
echo "$out"
echo "$out" | grep -q $'same\t' || fail "identity should be same: $out"
echo "$out" | grep -q $'1.000' || fail "identity score was not 1.000: $out"
pass "same-snapshot identity scores 1.000"

echo "== 6. mint is canonical =="
AGAIN="$("$PIN" mint --repo "$REPO" --from "$V1" src/calc.py:14)"
[[ "$HELPER" == "$AGAIN" ]] || fail "mint of the same line was not stable"
pass "canonical mint"

echo "== 7. pin show decodes provenance =="
shown="$("$PIN" show "$HELPER")"
echo "$shown"
echo "$shown" | grep -q 'src/calc.py:14' || fail "show lost minted path: $shown"
echo "$shown" | grep -q 'helper_keep' || fail "show lost line text: $shown"
echo "$shown" | grep -q 'origin:' || fail "show lost origin fingerprint: $shown"
echo "$shown" | grep -E '^\s+- ' | grep -q doomed && fail "sibling def doomed leaked into helper_keep neighbors: $shown"
echo "$shown" | grep -E '^\s+- ' | grep -q 'will be deleted' && fail "previous function body leaked into neighbors: $shown"
pass "show (neighbors stay in-scope, origin present)"

echo "== 8. pinfile names, then resolve the file (no locators) =="
PINS="$TMP/review.pins"
"$PIN" mint --repo "$REPO" --from "$V1" --file "$PINS" --name helper src/calc.py:14 >/dev/null
"$PIN" mint --repo "$REPO" --from "$V1" --file "$PINS" --name sauce src/calc.py:7 >/dev/null
"$PIN" mint --repo "$REPO" --from "$V1" --file "$PINS" --name doomed src/calc.py:11 >/dev/null
cat "$PINS"
out="$("$PIN" resolve --repo "$REPO" --to "$V2" --file "$PINS" --porcelain)"
echo "$out"
echo "$out" | grep -q $'helper' || fail "pinfile lost name helper: $out"
echo "$out" | grep -q $'ops.py' || fail "pinfile helper did not resolve: $out"
echo "$out" | grep -q $'sauce.py' || fail "pinfile sauce did not resolve: $out"
echo "$out" | grep -q $'^deleted\tdoomed' || fail "pinfile doomed not deleted: $out"
pass "pinfile roundtrip"

echo "== 9. gitless from-dir / to-dir =="
mkdir -p "$TMP/from/src" "$TMP/to/pkg"
echo 'UNIQUE_TOKEN_QZX = 1' > "$TMP/from/src/old.py"
echo 'x = UNIQUE_TOKEN_QZX' >> "$TMP/from/src/old.py"
echo 'UNIQUE_TOKEN_QZX = 1' > "$TMP/to/pkg/new.py"
DIRPIN="$("$PIN" mint --from-dir "$TMP/from" src/old.py:1)"
out="$("$PIN" resolve --to-dir "$TMP/to" --porcelain "$DIRPIN")"
echo "$out"
echo "$out" | grep -q 'pkg/new.py:1' || fail "dir-to-dir unique token missed: $out"
echo "$out" | grep -q $'1.000' || fail "exact unique-token copy should score 1.000: $out"
pass "from-dir mint / to-dir resolve (no git)"

echo "== 10. unicode path =="
UNI="$("$PIN" mint --repo "$REPO" --from "$V1" 'src/日本語.py:1')"
out="$("$PIN" resolve --repo "$REPO" --to "$V2" --porcelain "$UNI")"
echo "$out"
echo "$out" | grep -q 'src/日本語.py:1' || fail "unicode path lost: $out"
pass "unicode filename"

echo "== 11. colon filename =="
COL="$("$PIN" mint --repo "$REPO" --from "$V1" 'src/weird:colon.py:1')"
out="$("$PIN" resolve --repo "$REPO" --to "$V2" --porcelain "$COL")"
echo "$out"
echo "$out" | grep -q 'src/weird:colon.py:1' || fail "colon filename lost: $out"
pass "colon filename"

echo "== 12. spaced filename =="
SPC="$("$PIN" mint --repo "$REPO" --from "$V1" 'notes/file with spaces.txt:1')"
out="$("$PIN" resolve --repo "$REPO" --to "$V2" --porcelain "$SPC")"
echo "$out"
echo "$out" | grep -q 'notes/file with spaces.txt:1' || fail "spaced filename lost: $out"
pass "spaced filename"

echo "== 13. nested git does not hijack --repo =="
out="$("$PIN" resolve --repo "$REPO" --to "$V2" --porcelain "$HELPER")"
echo "$out"
echo "$out" | grep -q 'src/math/ops.py' || fail "nested git confused outer resolve: $out"
pass "nested git ignored when --repo points at outer"

echo "== 14. json shape =="
out="$("$PIN" resolve --repo "$REPO" --to "$V2" --json "$HELPER")"
echo "$out"
python3 -c 'import json,sys; o=json.loads(sys.argv[1]); assert o["status"] in ("moved","edited","same"); assert o["to"]["path"].endswith("ops.py"); assert o["pin"].startswith("helm1."); assert o.get("origin")' "$out"
pass "json output"

echo "== 15. helm1. argv implies resolve, flags on either side =="
out="$("$PIN" --porcelain "$HELPER" --repo "$REPO" --to "$V2")"
echo "$out"
echo "$out" | grep -q 'ops.py' || fail "flags-before-token did not resolve: $out"
out="$("$PIN" --repo "$REPO" --to "$V2" --porcelain "$HELPER")"
echo "$out"
echo "$out" | grep -q 'ops.py' || fail "repo-flags-then-token did not resolve: $out"
out="$("$PIN" "$HELPER" --repo "$REPO" --to "$V2" --porcelain)"
echo "$out"
echo "$out" | grep -q 'ops.py' || fail "bare pin token did not resolve: $out"
pass "bare helm1. token implies resolve (flags either side)"

echo "== 16. Makefile extensionless =="
MAKE="$("$PIN" mint --repo "$REPO" --from "$V1" Makefile:2)"
out="$("$PIN" resolve --repo "$REPO" --to "$V2" --porcelain "$MAKE")"
echo "$out"
echo "$out" | grep -q $'Makefile:' || fail "Makefile pin lost: $out"
pass "extensionless Makefile"

echo "== 17. stdin pinfile resolve =="
rewritten="$("$PIN" resolve --repo "$REPO" --to "$V2" --porcelain < "$PINS")"
echo "$rewritten"
echo "$rewritten" | grep -q 'ops.py' || fail "stdin pinfile missed ops: $rewritten"
pass "stdin pinfile"

# --- destroyer regressions ---

echo "== 18. leftover stub at old path must not steal the pin =="
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
git -C "$STUB" -c user.name=helm -c user.email=helm@example.com commit -q -m 'stub-v1'
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
git -C "$STUB" -c user.name=helm -c user.email=helm@example.com commit -q -m 'stub-v2 leftover wrapper'
STUB_V2="$(git -C "$STUB" rev-parse HEAD)"
STUBPIN="$("$PIN" mint --repo "$STUB" --from "$STUB_V1" src/calc.py:5)"
out="$("$PIN" resolve --repo "$STUB" --to "$STUB_V2" --porcelain "$STUBPIN")"
echo "$out"
dest="$(printf '%s\n' "$out" | awk -F'\t' '{print $4}')"
echo "$dest" | grep -q '^src/calc/ops.py:' || fail "leftover stub split did not land in ops.py: $out"
echo "$dest" | grep -q '^src/calc.py:' && fail "leftover stub at old path stole the pin: $out"
echo "$out" | grep -q $'^shifted\t' && fail "stub scored as shifted identity: $out"
echo "$dest" | grep -q 'legacy/calc.py' && fail "basename bait stole the pin: $out"
echo "$out" | grep -q 'leftover stub' || fail "note did not name leftover stub: $out"
echo "$out" | grep -q 'basename bait' || fail "note did not name basename bait: $out"
ADDPIN="$("$PIN" mint --repo "$STUB" --from "$STUB_V1" src/calc.py:1)"
addout="$("$PIN" resolve --repo "$STUB" --to "$STUB_V2" --porcelain "$ADDPIN")"
echo "$addout"
adddest="$(printf '%s\n' "$addout" | awk -F'\t' '{print $4}')"
echo "$adddest" | grep -q '^src/calc/ops.py:' || fail "add() leftover stub did not land in ops.py: $addout"
echo "$adddest" | grep -q '^src/calc.py:' && fail "add() leftover stub stole the pin: $addout"
pass "neighbor body beat leftover stub and basename bait"

echo "== 18k. extract-and-keep is not a move =="
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
git -C "$KEEP" -c user.name=helm -c user.email=helm@example.com commit -q -m 'keep-v1'
KEEP_V1="$(git -C "$KEEP" rev-parse HEAD)"
mkdir -p "$KEEP/src/calc" "$KEEP/src/legacy"
# Origin file is byte-identical. Body is copied to stem-split + basename bait.
cp "$KEEP/src/calc.py" "$KEEP/src/calc/ops.py"
cat > "$KEEP/src/legacy/calc.py" <<'PY'
def helper_keep():
    return "stable helper"
PY
git -C "$KEEP" add -A src
git -C "$KEEP" -c user.name=helm -c user.email=helm@example.com commit -q -m 'keep-v2 extract, origin untouched'
KEEP_V2="$(git -C "$KEEP" rev-parse HEAD)"
KEEPPIN="$("$PIN" mint --repo "$KEEP" --from "$KEEP_V1" src/calc.py:4)"
out="$("$PIN" resolve --repo "$KEEP" --to "$KEEP_V2" --porcelain "$KEEPPIN")"
echo "$out"
dest="$(printf '%s\n' "$out" | awk -F'\t' '{print $4}')"
echo "$dest" | grep -q '^src/calc.py:' || fail "extract-and-keep left the origin: $out"
echo "$dest" | grep -q '^src/calc/ops.py:' && fail "extract-and-keep reported as move to ops.py: $out"
echo "$out" | grep -q $'^moved\t' && fail "extract-and-keep classified as moved: $out"
echo "$out" | grep -Eq $'^(same|shifted)\t' || fail "extract-and-keep should be same/shifted: $out"
echo "$out" | grep -q $'1.000' || fail "extract-and-keep identity should score 1.000: $out"
echo "$out" | grep -q 'basename bait src/calc.py' && fail "origin body called basename bait: $out"
echo "$out" | grep -q 'extracted copy' || fail "note did not name extracted copy: $out"
echo "$out" | grep -q 'basename bait src/legacy/calc.py' || fail "legacy bait unnamed: $out"
KEEPADD="$("$PIN" mint --repo "$KEEP" --from "$KEEP_V1" src/calc.py:1)"
addout="$("$PIN" resolve --repo "$KEEP" --to "$KEEP_V2" --porcelain "$KEEPADD")"
echo "$addout"
adddest="$(printf '%s\n' "$addout" | awk -F'\t' '{print $4}')"
echo "$adddest" | grep -q '^src/calc.py:' || fail "extract-and-keep add() left origin: $addout"
echo "$adddest" | grep -q '^src/calc/ops.py:' && fail "extract-and-keep add() moved: $addout"
pass "extract-and-keep stays at origin; stem-split is a copy, not a move"

echo "== 18d. leftover that kept a docstring is still a stub =="
DOC="$TMP/docstub"
mkdir -p "$DOC/src"
cat > "$DOC/src/calc.py" <<'PY'
def add(a, b):
    """Return the sum of a and b."""
    return a + b

def helper_keep():
    return "stable helper"
PY
git -C "$DOC" init -q
git -C "$DOC" add src
git -C "$DOC" -c user.name=helm -c user.email=helm@example.com commit -q -m 'doc-v1'
DOC_V1="$(git -C "$DOC" rev-parse HEAD)"
mkdir -p "$DOC/src/calc"
cat > "$DOC/src/calc.py" <<'PY'
def helper_keep():
    from src.calc.ops import helper_keep as impl
    return impl()

def add(a, b):
    """Return the sum of a and b."""
    from src.calc.ops import add as _add
    return _add(a, b)
PY
cat > "$DOC/src/calc/ops.py" <<'PY'
def add(a, b):
    """Return the sum of a and b."""
    return a + b

def helper_keep():
    return "stable helper"
PY
git -C "$DOC" add -A src
git -C "$DOC" -c user.name=helm -c user.email=helm@example.com commit -q -m 'doc-v2 leftover kept docstring'
DOC_V2="$(git -C "$DOC" rev-parse HEAD)"
DOCPIN="$("$PIN" mint --repo "$DOC" --from "$DOC_V1" src/calc.py:1)"
out="$("$PIN" resolve --repo "$DOC" --to "$DOC_V2" --porcelain "$DOCPIN")"
echo "$out"
docdest="$(printf '%s\n' "$out" | awk -F'\t' '{print $4}')"
echo "$docdest" | grep -q '^src/calc/ops.py:' || fail "docstring leftover did not follow extract: $out"
echo "$docdest" | grep -q '^src/calc.py:' && fail "docstring leftover stole the pin (ns>=0.5 trap): $out"
echo "$out" | grep -q 'leftover stub' || fail "docstring leftover unnamed: $out"
pass "leftover that kept a docstring still loses to the body"

echo "== 18n. origin still holds body past the ctx window =="
NOISY="$TMP/noisykeep"
mkdir -p "$NOISY/src"
cat > "$NOISY/src/calc.py" <<'PY'
def helper_keep():
    return "stable helper"
PY
git -C "$NOISY" init -q
git -C "$NOISY" add src
git -C "$NOISY" -c user.name=helm -c user.email=helm@example.com commit -q -m 'noisy-v1'
NOISY_V1="$(git -C "$NOISY" rev-parse HEAD)"
mkdir -p "$NOISY/src/calc"
cp "$NOISY/src/calc.py" "$NOISY/src/calc/ops.py"
cat > "$NOISY/src/calc.py" <<'PY'
def helper_keep():
    """kept docs"""
    # noisy
    # noisy
    # noisy
    return "stable helper"
PY
git -C "$NOISY" add -A src
git -C "$NOISY" -c user.name=helm -c user.email=helm@example.com commit -q -m 'noisy-v2 comments, body kept'
NOISY_V2="$(git -C "$NOISY" rev-parse HEAD)"
NOISYPIN="$("$PIN" mint --repo "$NOISY" --from "$NOISY_V1" src/calc.py:1)"
out="$("$PIN" resolve --repo "$NOISY" --to "$NOISY_V2" --porcelain "$NOISYPIN")"
echo "$out"
ndest="$(printf '%s\n' "$out" | awk -F'\t' '{print $4}')"
echo "$ndest" | grep -q '^src/calc.py:' || fail "noisy origin should keep the pin: $out"
echo "$ndest" | grep -q '^src/calc/ops.py:' && fail "noisy origin reported as move: $out"
echo "$out" | grep -q $'^moved\t' && fail "noisy extract-and-keep classified as moved: $out"
echo "$out" | grep -q 'leftover stub src/calc.py' && fail "noisy origin labeled leftover stub: $out"
echo "$out" | grep -q 'extracted copy' || fail "noisy note did not name extract: $out"
pass "origin holds body even when comments push it past ctx=3"

echo "== 18r. leftover + renamed package must not tie with basename bait =="
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
git -C "$MATH" -c user.name=helm -c user.email=helm@example.com commit -q -m 'math-v1'
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
git -C "$MATH" -c user.name=helm -c user.email=helm@example.com commit -q -m 'math-v2 leftover wrapper, renamed extract'
MATH_V2="$(git -C "$MATH" rev-parse HEAD)"
MATHPIN="$("$PIN" mint --repo "$MATH" --from "$MATH_V1" src/calc.py:4)"
out="$("$PIN" resolve --repo "$MATH" --to "$MATH_V2" --porcelain "$MATHPIN")"
echo "$out"
mdest="$(printf '%s\n' "$out" | awk -F'\t' '{print $4}')"
echo "$out" | grep -q $'^ambiguous\t' && fail "renamed leftover tied with basename bait: $out"
echo "$mdest" | grep -q '^src/math/ops.py:' || fail "renamed leftover did not land in math/ops.py: $out"
echo "$mdest" | grep -q '^src/calc.py:' && fail "renamed leftover stub stole the pin: $out"
echo "$mdest" | grep -q 'legacy/calc.py' && fail "basename bait stole the renamed extract: $out"
echo "$out" | grep -q 'leftover stub' || fail "renamed leftover unnamed stub: $out"
echo "$out" | grep -q 'basename bait' || fail "renamed leftover unnamed bait: $out"
MATHADD="$("$PIN" mint --repo "$MATH" --from "$MATH_V1" src/calc.py:1)"
addout="$("$PIN" resolve --repo "$MATH" --to "$MATH_V2" --porcelain "$MATHADD")"
echo "$addout"
adddest="$(printf '%s\n' "$addout" | awk -F'\t' '{print $4}')"
echo "$adddest" | grep -q '^src/math/ops.py:' || fail "renamed leftover add() missed extract: $addout"
pass "leftover + src/math/ops.py beat basename bait (no stem-split)"

echo "== 18m. extract-and-keep to a renamed package is still identity =="
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
git -C "$KEEPM" -c user.name=helm -c user.email=helm@example.com commit -q -m 'keepmath-v1'
KEEPM_V1="$(git -C "$KEEPM" rev-parse HEAD)"
mkdir -p "$KEEPM/src/math" "$KEEPM/src/legacy"
cp "$KEEPM/src/calc.py" "$KEEPM/src/math/ops.py"
cat > "$KEEPM/src/legacy/calc.py" <<'PY'
def helper_keep():
    return "stable helper"
PY
git -C "$KEEPM" add -A src
git -C "$KEEPM" -c user.name=helm -c user.email=helm@example.com commit -q -m 'keepmath-v2 extract to math, origin untouched'
KEEPM_V2="$(git -C "$KEEPM" rev-parse HEAD)"
KEEPMPIN="$("$PIN" mint --repo "$KEEPM" --from "$KEEPM_V1" src/calc.py:4)"
out="$("$PIN" resolve --repo "$KEEPM" --to "$KEEPM_V2" --porcelain "$KEEPMPIN")"
echo "$out"
kmdest="$(printf '%s\n' "$out" | awk -F'\t' '{print $4}')"
echo "$kmdest" | grep -q '^src/calc.py:' || fail "renamed extract-and-keep left the origin: $out"
echo "$kmdest" | grep -q '^src/math/ops.py:' && fail "renamed extract-and-keep reported as move: $out"
echo "$out" | grep -q $'^moved\t' && fail "renamed extract-and-keep classified as moved: $out"
echo "$out" | grep -Eq $'^(same|shifted)\t' || fail "renamed extract-and-keep should be same/shifted: $out"
echo "$out" | grep -q 'basename bait src/calc.py' && fail "renamed keep origin called basename bait: $out"
echo "$out" | grep -q 'extracted copy' || fail "renamed keep note did not name extract: $out"
pass "extract-and-keep to src/math/ops.py stays at origin"

echo "== 18s. leftover import beats same-basename extract bait =="
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
git -C "$SAMEB" -c user.name=helm -c user.email=helm@example.com commit -q -m 'sameb-v1'
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
git -C "$SAMEB" -c user.name=helm -c user.email=helm@example.com commit -q -m 'sameb-v2 leftover names math.calc'
SAMEB_V2="$(git -C "$SAMEB" rev-parse HEAD)"
SAMEBPIN="$("$PIN" mint --repo "$SAMEB" --from "$SAMEB_V1" src/calc.py:4)"
out="$("$PIN" resolve --repo "$SAMEB" --to "$SAMEB_V2" --porcelain "$SAMEBPIN")"
echo "$out"
sbdest="$(printf '%s\n' "$out" | awk -F'\t' '{print $4}')"
echo "$out" | grep -q $'^ambiguous\t' && fail "same-basename extract tied with bait: $out"
echo "$sbdest" | grep -q '^src/math/calc.py:' || fail "leftover import did not land on math/calc.py: $out"
echo "$sbdest" | grep -q 'legacy/calc.py' && fail "basename bait stole same-basename extract: $out"
echo "$out" | grep -q 'leftover stub' || fail "same-basename leftover unnamed stub: $out"
echo "$out" | grep -q 'basename bait' || fail "same-basename leftover unnamed bait: $out"
SAMEBADD="$("$PIN" mint --repo "$SAMEB" --from "$SAMEB_V1" src/calc.py:1)"
addout="$("$PIN" resolve --repo "$SAMEB" --to "$SAMEB_V2" --porcelain "$SAMEBADD")"
echo "$addout"
adddest="$(printf '%s\n' "$addout" | awk -F'\t' '{print $4}')"
echo "$adddest" | grep -q '^src/math/calc.py:' || fail "same-basename add() missed extract: $addout"
pass "leftover import picks src/math/calc.py over src/legacy/calc.py"

echo "== 18p. leftover pointer beats abandoned stem-split clone =="
SS="$TMP/stem_over_ptr"
mkdir -p "$SS/src"
cat > "$SS/src/calc.py" <<'PY'
def add(a, b):
    return a + b

def helper_keep():
    return "stable helper"
PY
git -C "$SS" init -q
git -C "$SS" add src
git -C "$SS" -c user.name=helm -c user.email=helm@example.com commit -q -m 'ss-v1'
SS_V1="$(git -C "$SS" rev-parse HEAD)"
mkdir -p "$SS/src/calc" "$SS/src/math" "$SS/src/legacy"
cat > "$SS/src/calc.py" <<'PY'
def helper_keep():
    from src.math.ops import helper_keep as impl
    return impl()

def add(a, b):
    from src.math.ops import add as _add
    return _add(a, b)
PY
cat > "$SS/src/calc/ops.py" <<'PY'
def add(a, b):
    return a + b

def helper_keep():
    return "stable helper"
PY
cat > "$SS/src/math/ops.py" <<'PY'
def add(a, b):
    return a + b

def helper_keep():
    return "stable helper"
PY
cat > "$SS/src/legacy/calc.py" <<'PY'
def helper_keep():
    return "stable helper"
PY
git -C "$SS" add -A src
git -C "$SS" -c user.name=helm -c user.email=helm@example.com commit -q -m 'ss-v2 leftover names math.ops; stem-split clone remains'
SSPIN="$("$PIN" mint --repo "$SS" --from "$SS_V1" src/calc.py:4)"
out="$("$PIN" resolve --repo "$SS" --to HEAD --porcelain "$SSPIN")"
echo "$out"
ssdest="$(printf '%s\n' "$out" | awk -F'\t' '{print $4}')"
echo "$out" | grep -q $'^ambiguous\t' && fail "stem-over-ptr refused: $out"
echo "$ssdest" | grep -q '^src/math/ops.py:' || fail "leftover pointer did not beat stem-split: $out"
echo "$ssdest" | grep -q '^src/calc/ops.py:' && fail "abandoned stem-split clone stole the pin: $out"
pass "leftover pointer beats unique stem-split clone"

echo "== 18q. relative leftover must not land unique-non-basename decoy =="
REL="$TMP/rel_decoy"
mkdir -p "$REL/src"
cat > "$REL/src/calc.py" <<'PY'
def add(a, b):
    return a + b

def helper_keep():
    return "stable helper"
PY
git -C "$REL" init -q
git -C "$REL" add src
git -C "$REL" -c user.name=helm -c user.email=helm@example.com commit -q -m 'rel-v1'
REL_V1="$(git -C "$REL" rev-parse HEAD)"
mkdir -p "$REL/src/pkg" "$REL/src/utils" "$REL/src/legacy"
cat > "$REL/src/calc.py" <<'PY'
def helper_keep():
    from .ops import helper_keep as impl
    return impl()

def add(a, b):
    from .ops import add as _add
    return _add(a, b)
PY
cat > "$REL/src/pkg/calc.py" <<'PY'
def add(a, b):
    return a + b

def helper_keep():
    return "stable helper"
PY
cat > "$REL/src/utils/helpers.py" <<'PY'
def helper_keep():
    return "stable helper"
PY
cat > "$REL/src/legacy/calc.py" <<'PY'
def helper_keep():
    return "stable helper"
PY
git -C "$REL" add -A src
git -C "$REL" -c user.name=helm -c user.email=helm@example.com commit -q -m 'rel-v2 relative leftover, basename extract, helpers decoy'
RELPIN="$("$PIN" mint --repo "$REL" --from "$REL_V1" src/calc.py:4)"
out="$("$PIN" resolve --repo "$REL" --to HEAD --porcelain "$RELPIN")"
echo "$out"
reldest="$(printf '%s\n' "$out" | awk -F'\t' '{print $4}')"
echo "$out" | grep -q $'^moved\t' && echo "$reldest" | grep -q 'src/utils/helpers.py' && fail "relative leftover landed helpers decoy: $out"
echo "$out" | grep -q 'basename bait src/pkg/calc.py' && fail "relative leftover called real extract basename bait: $out"
echo "$reldest" | grep -q 'src/utils/helpers.py' && echo "$out" | grep -Eq $'^(moved|same|shifted)\t' && fail "relative leftover resolved onto decoy: $out"
pass "relative leftover does not land unique-non-basename decoy"

echo "== 18h. from .ops import in leftover src/calc.py names extract src/math/ops.py =="
RELOPS="$TMP/rel_ops"
mkdir -p "$RELOPS/src"
cat > "$RELOPS/src/calc.py" <<'PY'
def add(a, b):
    return a + b

def helper_keep():
    return "stable helper"
PY
git -C "$RELOPS" init -q
git -C "$RELOPS" add src
git -C "$RELOPS" -c user.name=helm -c user.email=helm@example.com commit -q -m 'relops-v1'
RELOPS_V1="$(git -C "$RELOPS" rev-parse HEAD)"
mkdir -p "$RELOPS/src/math" "$RELOPS/src/legacy"
cat > "$RELOPS/src/calc.py" <<'PY'
def helper_keep():
    from .ops import helper_keep as impl
    return impl()

def add(a, b):
    from .ops import add as _add
    return _add(a, b)
PY
cat > "$RELOPS/src/math/ops.py" <<'PY'
def add(a, b):
    return a + b

def helper_keep():
    return "stable helper"
PY
cat > "$RELOPS/src/legacy/calc.py" <<'PY'
def helper_keep():
    return "stable helper"
PY
git -C "$RELOPS" add -A src
git -C "$RELOPS" -c user.name=helm -c user.email=helm@example.com commit -q -m 'relops-v2 leftover from .ops import, extract math/ops.py'
RELOPSPIN="$("$PIN" mint --repo "$RELOPS" --from "$RELOPS_V1" src/calc.py:4)"
out="$("$PIN" resolve --repo "$RELOPS" --to HEAD --porcelain "$RELOPSPIN")"
echo "$out"
relopsdest="$(printf '%s\n' "$out" | awk -F'\t' '{print $4}')"
echo "$out" | grep -q $'^ambiguous\t' && fail "relative .ops leftover tied: $out"
echo "$relopsdest" | grep -q '^src/math/ops.py:' || fail "relative .ops leftover missed extract: $out"
echo "$relopsdest" | grep -q 'legacy/calc.py' && fail "relative .ops leftover landed bait: $out"
echo "$relopsdest" | grep -q '^src/calc.py:' && fail "relative .ops leftover stub stole the pin: $out"
RELOPSADD="$("$PIN" mint --repo "$RELOPS" --from "$RELOPS_V1" src/calc.py:1)"
addout="$("$PIN" resolve --repo "$RELOPS" --to HEAD --porcelain "$RELOPSADD")"
echo "$addout"
adddest="$(printf '%s\n' "$addout" | awk -F'\t' '{print $4}')"
echo "$adddest" | grep -q '^src/math/ops.py:' || fail "relative .ops leftover add() missed extract: $addout"
pass "from .ops import in leftover src/calc.py moved to src/math/ops.py"

echo "== 18h2. from .calc import unique extract names src/math/calc.py =="
RELC="$TMP/rel_calc_one"
mkdir -p "$RELC/src"
cat > "$RELC/src/calc.py" <<'PY'
def add(a, b):
    return a + b

def helper_keep():
    return "stable helper"
PY
git -C "$RELC" init -q
git -C "$RELC" add src
git -C "$RELC" -c user.name=helm -c user.email=helm@example.com commit -q -m 'relc-v1'
RELC_V1="$(git -C "$RELC" rev-parse HEAD)"
mkdir -p "$RELC/src/math"
cat > "$RELC/src/calc.py" <<'PY'
def helper_keep():
    from .calc import helper_keep as impl
    return impl()
PY
cat > "$RELC/src/math/calc.py" <<'PY'
def add(a, b):
    return a + b

def helper_keep():
    return "stable helper"
PY
git -C "$RELC" add -A src
git -C "$RELC" -c user.name=helm -c user.email=helm@example.com commit -q -m 'relc-v2 leftover from .calc import, unique extract'
RELCPIN="$("$PIN" mint --repo "$RELC" --from "$RELC_V1" src/calc.py:4)"
out="$("$PIN" resolve --repo "$RELC" --to HEAD --porcelain "$RELCPIN")"
echo "$out"
relcdest="$(printf '%s\n' "$out" | awk -F'\t' '{print $4}')"
echo "$out" | grep -q $'^ambiguous\t' && fail "unique relative .calc leftover tied: $out"
echo "$relcdest" | grep -q '^src/math/calc.py:' || fail "unique relative .calc leftover missed extract: $out"
pass "from .calc import unique extract names src/math/calc.py"

echo "== 18h3. from .calc import + bait must not land src/legacy/calc.py =="
RELC2="$TMP/rel_calc_bait"
mkdir -p "$RELC2/src"
cat > "$RELC2/src/calc.py" <<'PY'
def add(a, b):
    return a + b

def helper_keep():
    return "stable helper"
PY
git -C "$RELC2" init -q
git -C "$RELC2" add src
git -C "$RELC2" -c user.name=helm -c user.email=helm@example.com commit -q -m 'relc2-v1'
RELC2_V1="$(git -C "$RELC2" rev-parse HEAD)"
mkdir -p "$RELC2/src/math" "$RELC2/src/legacy"
cat > "$RELC2/src/calc.py" <<'PY'
def helper_keep():
    from .calc import helper_keep as impl
    return impl()
PY
cat > "$RELC2/src/math/calc.py" <<'PY'
def add(a, b):
    return a + b

def helper_keep():
    return "stable helper"
PY
cat > "$RELC2/src/legacy/calc.py" <<'PY'
def helper_keep():
    return "stable helper"
PY
git -C "$RELC2" add -A src
git -C "$RELC2" -c user.name=helm -c user.email=helm@example.com commit -q -m 'relc2-v2 leftover from .calc import, extract + bait'
RELC2PIN="$("$PIN" mint --repo "$RELC2" --from "$RELC2_V1" src/calc.py:4)"
out="$("$PIN" resolve --repo "$RELC2" --to HEAD --porcelain "$RELC2PIN")"
echo "$out"
relc2dest="$(printf '%s\n' "$out" | awk -F'\t' '{print $4}')"
echo "$out" | grep -q $'^ambiguous\t' && fail "relative .calc leftover tied with bait: $out"
echo "$relc2dest" | grep -q '^src/math/calc.py:' || fail "relative .calc leftover missed extract: $out"
echo "$relc2dest" | grep -q 'legacy/calc.py' && fail "relative .calc leftover landed bait: $out"
pass "from .calc import + bait names src/math/calc.py"

echo "== 18t. module-level re-export is a leftover pointer =="
MOD="$TMP/modlevel"
mkdir -p "$MOD/src"
cat > "$MOD/src/calc.py" <<'PY'
def add(a, b):
    return a + b

def helper_keep():
    return "stable helper"
PY
git -C "$MOD" init -q
git -C "$MOD" add src
git -C "$MOD" -c user.name=helm -c user.email=helm@example.com commit -q -m 'mod-v1'
MOD_V1="$(git -C "$MOD" rev-parse HEAD)"
mkdir -p "$MOD/src/math" "$MOD/src/legacy"
cat > "$MOD/src/calc.py" <<'PY'
from src.math.calc import helper_keep as _impl
from src.math.calc import add as _add

def helper_keep():
    return _impl()

def add(a, b):
    return _add(a, b)
PY
cat > "$MOD/src/math/calc.py" <<'PY'
def add(a, b):
    return a + b

def helper_keep():
    return "stable helper"
PY
cat > "$MOD/src/legacy/calc.py" <<'PY'
def helper_keep():
    return "stable helper"
PY
git -C "$MOD" add -A src
git -C "$MOD" -c user.name=helm -c user.email=helm@example.com commit -q -m 'mod-v2 module-level import, same-basename extract'
MODPIN="$("$PIN" mint --repo "$MOD" --from "$MOD_V1" src/calc.py:4)"
out="$("$PIN" resolve --repo "$MOD" --to HEAD --porcelain "$MODPIN")"
echo "$out"
moddest="$(printf '%s\n' "$out" | awk -F'\t' '{print $4}')"
echo "$out" | grep -q $'^ambiguous\t' && fail "module-level leftover tied with bait: $out"
echo "$moddest" | grep -q '^src/math/calc.py:' || fail "module-level leftover missed extract: $out"
echo "$moddest" | grep -q 'legacy/calc.py' && fail "module-level leftover landed bait: $out"
pass "module-level from src.math.calc import helper_keep as _impl follows pointer"

echo "== 18u. from src.math import calc is leftover grammar =="
SPLIT="$TMP/splitimp"
mkdir -p "$SPLIT/src"
cat > "$SPLIT/src/calc.py" <<'PY'
def add(a, b):
    return a + b

def helper_keep():
    return "stable helper"
PY
git -C "$SPLIT" init -q
git -C "$SPLIT" add src
git -C "$SPLIT" -c user.name=helm -c user.email=helm@example.com commit -q -m 'split-v1'
SPLIT_V1="$(git -C "$SPLIT" rev-parse HEAD)"
mkdir -p "$SPLIT/src/math" "$SPLIT/src/legacy"
cat > "$SPLIT/src/calc.py" <<'PY'
def helper_keep():
    from src.math import calc
    return calc.helper_keep()

def add(a, b):
    from src.math import calc
    return calc.add(a, b)
PY
cat > "$SPLIT/src/math/calc.py" <<'PY'
def add(a, b):
    return a + b

def helper_keep():
    return "stable helper"
PY
cat > "$SPLIT/src/legacy/calc.py" <<'PY'
def helper_keep():
    return "stable helper"
PY
git -C "$SPLIT" add -A src
git -C "$SPLIT" -c user.name=helm -c user.email=helm@example.com commit -q -m 'split-v2 from src.math import calc'
SPLITPIN="$("$PIN" mint --repo "$SPLIT" --from "$SPLIT_V1" src/calc.py:4)"
out="$("$PIN" resolve --repo "$SPLIT" --to HEAD --porcelain "$SPLITPIN")"
echo "$out"
spdest="$(printf '%s\n' "$out" | awk -F'\t' '{print $4}')"
echo "$out" | grep -q $'^ambiguous\t' && fail "split import tied with bait: $out"
echo "$spdest" | grep -q '^src/math/calc.py:' || fail "split import missed extract: $out"
echo "$spdest" | grep -q 'legacy/calc.py' && fail "split import landed bait: $out"
pass "from src.math import calc follows src/math/calc.py"

echo "== 18v. io.fs ⊂ audio.fs must not land src/io/fs.py =="
IOFS="$TMP/iofs"
mkdir -p "$IOFS/src"
cat > "$IOFS/src/calc.py" <<'PY'
def helper_keep():
    return "stable helper"
PY
git -C "$IOFS" init -q
git -C "$IOFS" add src
git -C "$IOFS" -c user.name=helm -c user.email=helm@example.com commit -q -m 'io-v1'
IOFS_V1="$(git -C "$IOFS" rev-parse HEAD)"
mkdir -p "$IOFS/src/radio" "$IOFS/src/io"
cat > "$IOFS/src/calc.py" <<'PY'
def helper_keep():
    # migrated off audio.fs during the radio rewrite
    from .fs import helper_keep as impl
    return impl()
PY
cat > "$IOFS/src/radio/fs.py" <<'PY'
def helper_keep():
    return "stable helper"
PY
cat > "$IOFS/src/io/fs.py" <<'PY'
def helper_keep():
    return "stable helper"
PY
git -C "$IOFS" add -A src
git -C "$IOFS" -c user.name=helm -c user.email=helm@example.com commit -q -m 'io-v2 comment audio.fs, relative .fs, radio extract'
IOFSPIN="$("$PIN" mint --repo "$IOFS" --from "$IOFS_V1" src/calc.py:1)"
out="$("$PIN" resolve --repo "$IOFS" --to HEAD --porcelain "$IOFSPIN")"
echo "$out"
iodest="$(printf '%s\n' "$out" | awk -F'\t' '{print $4}')"
echo "$out" | grep -Eq $'^(moved|same|shifted)\t' && echo "$iodest" | grep -q '^src/io/fs.py:' && fail "io.fs substring landed bait: $out"
echo "$iodest" | grep -q '^src/io/fs.py:' && echo "$out" | grep -q $'^moved\t' && fail "io.fs ⊂ audio.fs moved to src/io/fs.py: $out"
pass "io.fs ⊂ audio.fs does not land src/io/fs.py"

echo "== 18b. missing --from ref is an error =="
set +e
out="$("$PIN" mint --repo "$REPO" --from this-from-does-not-exist src/calc.py:14 2>"$TMP/bad-from.err")"
rc=$?
set -e
[[ "$rc" -ne 0 ]] || fail "missing --from ref exited 0"
grep -qi 'unknown ref' "$TMP/bad-from.err" || fail "missing --from error was not about the ref: $(cat "$TMP/bad-from.err")"
pass "missing --from ref is an error"

echo "== 19. identical helpers are ambiguous, not walk-order 1.000 =="
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
IDPIN="$("$PIN" mint --from-dir "$IDENT_FROM" src/calc.py:1)"
out="$("$PIN" resolve --to-dir "$IDENT_TO" --porcelain "$IDPIN")"
echo "$out"
echo "$out" | grep -q $'^ambiguous\t' || fail "identical helpers should be ambiguous: $out"
echo "$out" | grep -q 'a/ops.py' || fail "ambiguous did not list a/ops.py: $out"
echo "$out" | grep -q 'z/calc.py' || fail "ambiguous did not list z/calc.py: $out"
echo "$out" | grep -q $'^moved\t' && fail "picked a walk-order landing instead of ambiguous: $out"
if "$PIN" resolve --to-dir "$IDENT_TO" --strict --porcelain "$IDPIN" >/tmp/helm-amb.out 2>/tmp/helm-amb.err; then
  fail "strict should fail closed on ambiguous"
fi
pass "identical helpers → ambiguous (strict fails)"

echo "== 20. files >1MB still mint and resolve =="
HUGE="$TMP/huge"
mkdir -p "$HUGE/src"
python3 - "$HUGE" <<'PY'
from pathlib import Path
import sys
root = Path(sys.argv[1])
body = 'def unique_locus_ZEBRA99():\n    return 1\n' + ('#' * 1_200_000) + '\n'
p = root / "src" / "godfile.py"
p.write_text(body, encoding="utf-8")
assert p.stat().st_size > 1_000_000, p.stat().st_size
print(p.stat().st_size)
PY
GOD="$("$PIN" mint --from-dir "$HUGE" src/godfile.py:1)"
echo "godfile token length=${#GOD}"
out="$("$PIN" resolve --to-dir "$HUGE" --porcelain "$GOD")"
echo "$out"
echo "$out" | grep -q 'src/godfile.py:1' || fail "godfile pin did not resolve: $out"
echo "$out" | grep -q $'1.000' || fail "godfile identity should be 1.000: $out"
# also via git, the path that used to omit
HGREPO="$TMP/hugegit"
mkdir -p "$HGREPO/src"
cp "$HUGE/src/godfile.py" "$HGREPO/src/godfile.py"
git -C "$HGREPO" init -q
git -C "$HGREPO" add src/godfile.py
git -C "$HGREPO" -c user.name=helm -c user.email=helm@example.com commit -q -m 'godfile'
HGOD="$("$PIN" mint --repo "$HGREPO" --from HEAD src/godfile.py:1)"
out="$("$PIN" resolve --repo "$HGREPO" --to HEAD --porcelain "$HGOD")"
echo "$out"
echo "$out" | grep -q $'src/godfile.py:1' || fail "git godfile pin missed: $out"
pass "1.2MB godfile minted and resolved"

echo "== 21. NFD locator binds NFC path =="
CAFEPIN="$(python3 - "$PIN" "$REPO" "$V1" <<'PY'
import subprocess, sys, unicodedata
pin, repo, v1 = sys.argv[1], sys.argv[2], sys.argv[3]
nfd = unicodedata.normalize("NFD", "src/café.py") + ":1"
r = subprocess.run([pin, "mint", "--repo", repo, "--from", v1, nfd], capture_output=True, text=True)
sys.stderr.write(r.stderr)
if r.returncode != 0:
    sys.stderr.write("mint NFD failed\n")
    sys.exit(r.returncode or 1)
print(r.stdout.strip())
PY
)"
echo "cafe pin: $CAFEPIN"
echo "$CAFEPIN" | grep -q '^helm1\.' || fail "NFD mint failed: $CAFEPIN"
out="$("$PIN" resolve --repo "$REPO" --to "$V2" --porcelain "$CAFEPIN")"
echo "$out"
echo "$out" | grep -q 'src/caf' || fail "NFC path lost after NFD mint: $out"
shown="$("$PIN" show "$CAFEPIN")"
echo "$shown"
echo "$shown" | grep -q 'cafe_fn' || fail "cafe pin lost text: $shown"
pass "NFD mint of NFC café.py"

echo "== 22. missing --to ref is an error, not deleted =="
set +e
out="$("$PIN" resolve --repo "$REPO" --to this-ref-does-not-exist --porcelain "$HELPER" 2>"$TMP/bad-ref.err")"
rc=$?
set -e
echo "rc=$rc stdout=$out"
cat "$TMP/bad-ref.err"
[[ "$rc" -ne 0 ]] || fail "missing --to ref exited 0"
echo "$out" | grep -q $'^deleted\t' && fail "missing --to looked like deletion: $out"
grep -qi 'unknown ref\|not a.*ref\|cannot list' "$TMP/bad-ref.err" \
  || fail "missing --to error was not about the ref: $(cat "$TMP/bad-ref.err")"
mkdir -p "$TMP/empty-to"
set +e
out="$("$PIN" resolve --to-dir "$TMP/empty-to" --porcelain "$DIRPIN" 2>"$TMP/empty-dir.err")"
rc=$?
set -e
echo "empty-dir rc=$rc stdout=$out"
[[ "$rc" -ne 0 ]] || fail "empty --to-dir exited 0"
echo "$out" | grep -q $'^deleted\t' && fail "empty --to-dir looked like deletion: $out"
pass "missing --to / empty --to-dir fail as errors"

echo "== 23. truncated pin tokens fail closed =="
HALF="${HELPER:0:24}"
echo "half=$HALF"
set +e
out="$("$PIN" resolve --repo "$REPO" --to "$V2" --porcelain "$HALF" 2>"$TMP/half.err")"
rc=$?
set -e
echo "half rc=$rc stdout=$out"
cat "$TMP/half.err"
[[ "$rc" -ne 0 ]] || fail "truncated token resolve exited 0"
echo "$out" | grep -Eq $'^(unresolved|moved|deleted|shifted|same)\t' \
  && fail "truncated token printed a result row: $out"
grep -qi 'corrupt\|not a pin' "$TMP/half.err" \
  || fail "truncated token stderr was not fail-closed: $(cat "$TMP/half.err")"
set +e
"$PIN" show "$HALF" >/tmp/helm-show-half.out 2>/tmp/helm-show-half.err
show_rc=$?
set -e
[[ "$show_rc" -ne 0 ]] || fail "show truncated token exited 0"
set +e
out="$("$PIN" resolve --repo "$REPO" --to "$V2" --porcelain helm1.xxxx 2>"$TMP/xxxx.err")"
rc=$?
set -e
[[ "$rc" -ne 0 ]] || fail "helm1.xxxx exited 0"
echo "$out" | grep -q $'^unresolved\t' && fail "helm1.xxxx printed unresolved success: $out"
pass "truncated / junk tokens fail closed (resolve matches show)"

echo "== 24. pin refuses an unrelated repo =="
UNREL="$TMP/unrel"
mkdir -p "$UNREL/pkg"
cat > "$UNREL/pkg/util.py" <<'PY'
def helper_keep():
    return "stable helper"
PY
git -C "$UNREL" init -q
git -C "$UNREL" add pkg/util.py
git -C "$UNREL" -c user.name=helm -c user.email=helm@example.com commit -q -m 'unrelated helper'
set +e
out="$("$PIN" resolve --repo "$UNREL" --to HEAD --porcelain "$HELPER" 2>"$TMP/unrel.err")"
rc=$?
set -e
echo "unrel rc=$rc stdout=$out"
cat "$TMP/unrel.err"
[[ "$rc" -ne 0 ]] || fail "foreign repo resolve exited 0"
echo "$out" | grep -q $'^moved\t' && fail "foreign repo silently landed: $out"
grep -qi 'different repository\|any-repo' "$TMP/unrel.err" \
  || fail "foreign repo error did not name origin: $(cat "$TMP/unrel.err")"
out="$("$PIN" resolve --repo "$UNREL" --to HEAD --any-repo --porcelain "$HELPER")"
echo "$out"
echo "$out" | grep -q 'pkg/util.py' || fail "--any-repo should opt into foreign resolve: $out"
pass "foreign repo refused; --any-repo overrides"

echo "== 24b. file:// depth-1 clone of the same repo still resolves =="
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
"$PIN" id --repo "$SHALLOW" | grep -q 'github.com/keel-lab/ugly' \
  || fail "shallow id did not inherit project remote"
out="$("$PIN" resolve --repo "$SHALLOW" --to HEAD --porcelain "$HELPER")"
echo "$out"
echo "$out" | grep -q 'src/math/ops.py' || fail "depth-1 clone of same repo did not resolve: $out"
echo "$out" | grep -q $'^deleted\t' && fail "depth-1 clone looked like deletion: $out"
pass "file:// depth-1 clone of the same project resolves without --any-repo"

echo "== 24c. orphan extra root is still the same repo =="
ORPH="$TMP/orph"
git clone -q "$REPO" "$ORPH"
ORPH_MAIN="$(git -C "$ORPH" rev-parse --abbrev-ref HEAD)"
git -C "$ORPH" checkout --orphan extra-hist
echo 'orphan only' > "$ORPH/orphan-only.txt"
git -C "$ORPH" add orphan-only.txt
git -C "$ORPH" -c user.name=helm -c user.email=helm@example.com commit -q -m 'orphan root'
git -C "$ORPH" checkout -q "$ORPH_MAIN"
out="$("$PIN" resolve --repo "$ORPH" --to "$V2" --porcelain "$HELPER")"
echo "$out"
echo "$out" | grep -q 'src/math/ops.py' || fail "orphan extra root made the repo foreign: $out"
pass "orphan extra root still the same helm"

# --- destroyer fixtures if present ---
FIX="${FIX:-/tmp/destroy-pin-v5/fixtures}"
if [[ -d "$FIX/rel_ok" && -d "$FIX/iofs" ]]; then
  echo "== 24d. DESTROYER_PIN_V5 leftover fixtures =="
  # rel_ok leftover is from .math.ops import → src/math/ops.py
  v1="$(git -C "$FIX/rel_ok" log --reverse --format=%H | head -1)"
  tok="$("$PIN" mint --repo "$FIX/rel_ok" --from "$v1" src/calc.py:4)"
  out="$("$PIN" resolve --repo "$FIX/rel_ok" --to HEAD --porcelain "$tok")"
  echo "rel_ok $out"
  echo "$out" | grep -q 'src/math/ops.py' || fail "destroyer rel_ok missed extract: $out"
  # iofs must not land src/io/fs.py
  v1="$(git -C "$FIX/iofs" log --reverse --format=%H | head -1)"
  tok="$("$PIN" mint --repo "$FIX/iofs" --from "$v1" src/calc.py:1)"
  out="$("$PIN" resolve --repo "$FIX/iofs" --to HEAD --porcelain "$tok")"
  echo "iofs $out"
  iodest="$(printf '%s\n' "$out" | awk -F'\t' '{print $4}')"
  echo "$out" | grep -Eq $'^(moved|same|shifted)\t' && echo "$iodest" | grep -q '^src/io/fs.py:' && fail "destroyer iofs landed bait: $out"
  pass "DESTROYER_PIN_V5 rel_ok / iofs"
else
  echo "SKIP DESTROYER_PIN_V5 fixtures (not at $FIX)"
fi

# --- real repo dogfood (read-only) ---
KIZU="${KIZU:-/Users/annenpolka/ghq/github.com/annenpolka/kizu}"
if [[ -d "$KIZU/.git" || -f "$KIZU/.git" ]]; then
  echo "== 25. kizu app.rs split: mint at b4e6a5d, resolve HEAD (no path:line) =="
  SEEN="$("$PIN" mint --repo "$KIZU" --from b4e6a5d src/app.rs:529)"
  echo "seen pin length=${#SEEN}"
  out="$("$PIN" resolve --repo "$KIZU" --to HEAD --porcelain "$SEEN")"
  echo "$out"
  echo "$out" | grep -q 'src/app/layout.rs:' || fail "kizu seen_hunk_fingerprint did not land in layout.rs: $out"
  pass "kizu: pin(src/app.rs:529@b4e6a5d) → src/app/layout.rs"

  echo "== 26. kizu nearest_landing_forward pin =="
  LAND="$("$PIN" mint --repo "$KIZU" --from b4e6a5d src/app.rs:543)"
  out="$("$PIN" resolve --repo "$KIZU" --to HEAD --porcelain "$LAND")"
  echo "$out"
  echo "$out" | grep -q 'src/app/navigation.rs:' || fail "kizu nearest_landing_forward missed navigation.rs: $out"
  pass "kizu: pin(src/app.rs:543) → src/app/navigation.rs"

  echo "== 27. kizu hunk_fingerprint signature drift =="
  FP="$("$PIN" mint --repo "$KIZU" --from b4e6a5d src/app.rs:602)"
  out="$("$PIN" resolve --repo "$KIZU" --to HEAD --porcelain "$FP")"
  echo "$out"
  echo "$out" | grep -q 'src/app/layout.rs:' || fail "kizu hunk_fingerprint missed layout.rs: $out"
  echo "$out" | grep -Eq $'^(edited|moved)\t' || fail "expected edited/moved for hunk_fingerprint: $out"
  pass "kizu: pin(hunk_fingerprint) survived &crate::git::Hunk → &Hunk"

  echo "== 28. kizu edit_insert_str vis change =="
  INS="$("$PIN" mint --repo "$KIZU" --from b4e6a5d src/app.rs:635)"
  out="$("$PIN" resolve --repo "$KIZU" --to HEAD --porcelain "$INS")"
  echo "$out"
  echo "$out" | grep -q 'src/app/text_input.rs:' || fail "kizu edit_insert_str missed text_input.rs: $out"
  pass "kizu: pin(edit_insert_str) → src/app/text_input.rs"

  echo "== 29. kizu pinfile of the split, resolve with names only =="
  KIZU_PINS="$TMP/kizu.pins"
  "$PIN" mint --repo "$KIZU" --from b4e6a5d --file "$KIZU_PINS" --name seen src/app.rs:529 >/dev/null
  "$PIN" mint --repo "$KIZU" --from b4e6a5d --file "$KIZU_PINS" --name landing src/app.rs:543 >/dev/null
  out="$("$PIN" resolve --repo "$KIZU" --to HEAD --file "$KIZU_PINS" --porcelain seen landing)"
  echo "$out"
  echo "$out" | grep -q $'seen' || fail "kizu pinfile name seen missing: $out"
  echo "$out" | grep -q 'layout.rs' || fail "kizu pinfile seen missed layout: $out"
  echo "$out" | grep -q 'navigation.rs' || fail "kizu pinfile landing missed navigation: $out"
  pass "kizu pinfile resolve by name (still no path:line)"
else
  echo "SKIP kizu dogfood (repo not present at $KIZU)"
fi

VOID="${VOID:-/Users/annenpolka/ghq/github.com/annenpolka/voidtrace}"
if [[ -d "$VOID/.git" || -f "$VOID/.git" ]]; then
  echo "== 30. voidtrace identity sanity =="
  file="$(git -C "$VOID" ls-files 'packages/kernel/src/evaluate.ts' | head -1)"
  if [[ -n "$file" ]]; then
    VP="$("$PIN" mint --repo "$VOID" --from HEAD "${file}:1")"
    out="$("$PIN" resolve --repo "$VOID" --to HEAD --porcelain "$VP")"
    echo "$out"
    echo "$out" | grep -q $'^same\t' || fail "voidtrace identity should be same: $out"
    echo "$out" | grep -q "${file}:1" || fail "voidtrace identity jumped file: $out"
    vdest="$(printf '%s\n' "$out" | awk -F'\t' '{print $4}')"
    echo "$vdest" | grep -q 'cli.test.ts' && fail "voidtrace import{ clone stole the pin: $out"
    echo "$vdest" | grep -q "$file" || fail "voidtrace dest left $file: $out"
    pass "voidtrace HEAD identity on $file:1"
  else
    echo "SKIP voidtrace (packages/kernel/src/evaluate.ts missing)"
  fi
fi

TENA="${TENA:-/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi}"
if [[ -d "$TENA/.git" || -f "$TENA/.git" ]]; then
  echo "== 31. tenaoshi KinsokuEngine.transform first-commit → HEAD =="
  TP="$("$PIN" mint --repo "$TENA" --from a41089c Engine/Sources/TenaoshiEngine/KinsokuEngine.swift:12)"
  out="$("$PIN" resolve --repo "$TENA" --to HEAD --porcelain "$TP")"
  echo "$out"
  echo "$out" | grep -q 'KinsokuEngine.swift:12' || fail "tenaoshi transform did not stay on line 12: $out"
  echo "$out" | grep -q $'1.000' || fail "tenaoshi expected 1.000: $out"
  pass "tenaoshi transform pin a41089c → HEAD line 12 score 1.000"
fi

SIT="${SIT:-/Users/annenpolka/ghq/github.com/annenpolka/sitbone}"
if [[ -d "$SIT/.git" || -f "$SIT/.git" ]]; then
  echo "== 32. sitbone identity (PresenceArbiter.detect) =="
  SP="$("$PIN" mint --repo "$SIT" --from HEAD Sources/SitboneCore/PresenceArbiter.swift:75)"
  out="$("$PIN" resolve --repo "$SIT" --to HEAD --porcelain "$SP")"
  echo "$out"
  echo "$out" | grep -q $'^same\t' || fail "sitbone identity should be same: $out"
  echo "$out" | grep -q 'PresenceArbiter.swift:75' || fail "sitbone jumped: $out"
  pass "sitbone HEAD identity on PresenceArbiter.detect"
fi

echo
echo "All demo checks passed."
exit 0
