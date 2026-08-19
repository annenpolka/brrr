#!/usr/bin/env bash
# Exercise pin: mint once, resolve later, never re-supply path:line.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PIN="$ROOT/pin"
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
  -c user.name=pin -c user.email=pin@example.com \
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
  -c user.name=pin -c user.email=pin@example.com \
  commit -q -m 'v2: split calc, drop doomed, tweak sauce'
V2="$(git -C "$REPO" rev-parse HEAD)"

echo "== fixture refs =="
echo "V1=$V1"
echo "V2=$V2"

echo "== 1. mint helper_keep at v1, resolve at v2 without path:line =="
HELPER="$("$PIN" mint --repo "$REPO" --from "$V1" src/calc.py:14)"
echo "token: $HELPER"
echo "$HELPER" | grep -q '^pin1\.' || fail "mint did not emit pin1. token: $HELPER"
out="$("$PIN" resolve --repo "$REPO" --to "$V2" --porcelain "$HELPER")"
echo "$out"
echo "$out" | grep -q $'src/math/ops.py:8' || fail "helper_keep did not land in ops.py: $out"
echo "$out" | grep -Eq $'^(moved|same|edited)\t' || fail "unexpected status: $out"
echo "$out" | grep -q $'1.000' || fail "exact helper_keep copy should score 1.000: $out"
pass "stored pin relocated helper_keep into src/math/ops.py"

echo "== 2. resolve refuses a locator (the flipped assumption) =="
if "$PIN" resolve --repo "$REPO" --to "$V2" src/calc.py:14 >/tmp/pin-resolve-loc.out 2>/tmp/pin-resolve-loc.err; then
  fail "resolve accepted path:line"
fi
grep -q 'locator' /tmp/pin-resolve-loc.err || grep -q 'not a pin' /tmp/pin-resolve-loc.err \
  || fail "resolve error did not name locator/pin: $(cat /tmp/pin-resolve-loc.err)"
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
echo "$shown" | grep -E '^\s+- ' | grep -q doomed && fail "sibling def doomed leaked into helper_keep neighbors: $shown"
echo "$shown" | grep -E '^\s+- ' | grep -q 'will be deleted' && fail "previous function body leaked into neighbors: $shown"
pass "show (neighbors stay in-scope)"

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
python3 -c 'import json,sys; o=json.loads(sys.argv[1]); assert o["status"] in ("moved","edited","same"); assert o["to"]["path"].endswith("ops.py"); assert o["pin"].startswith("pin1.")' "$out"
pass "json output"

echo "== 15. pin1. argv implies resolve, flags on either side =="
out="$("$PIN" --porcelain "$HELPER" --repo "$REPO" --to "$V2")"
echo "$out"
echo "$out" | grep -q 'ops.py' || fail "flags-before-token did not resolve: $out"
out="$("$PIN" --repo "$REPO" --to "$V2" --porcelain "$HELPER")"
echo "$out"
echo "$out" | grep -q 'ops.py' || fail "repo-flags-then-token did not resolve: $out"
out="$("$PIN" "$HELPER" --repo "$REPO" --to "$V2" --porcelain)"
echo "$out"
echo "$out" | grep -q 'ops.py' || fail "bare pin token did not resolve: $out"
pass "bare pin1. token implies resolve (flags either side)"

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

# --- real repo dogfood (read-only) ---
KIZU="${KIZU:-/Users/annenpolka/ghq/github.com/annenpolka/kizu}"
if [[ -d "$KIZU/.git" || -f "$KIZU/.git" ]]; then
  echo "== 18. kizu app.rs split: mint at b4e6a5d, resolve HEAD (no path:line) =="
  SEEN="$("$PIN" mint --repo "$KIZU" --from b4e6a5d src/app.rs:529)"
  echo "seen pin length=${#SEEN}"
  out="$("$PIN" resolve --repo "$KIZU" --to HEAD --porcelain "$SEEN")"
  echo "$out"
  echo "$out" | grep -q 'src/app/layout.rs:' || fail "kizu seen_hunk_fingerprint did not land in layout.rs: $out"
  pass "kizu: pin(src/app.rs:529@b4e6a5d) → src/app/layout.rs"

  echo "== 19. kizu nearest_landing_forward pin =="
  LAND="$("$PIN" mint --repo "$KIZU" --from b4e6a5d src/app.rs:543)"
  out="$("$PIN" resolve --repo "$KIZU" --to HEAD --porcelain "$LAND")"
  echo "$out"
  echo "$out" | grep -q 'src/app/navigation.rs:' || fail "kizu nearest_landing_forward missed navigation.rs: $out"
  pass "kizu: pin(src/app.rs:543) → src/app/navigation.rs"

  echo "== 20. kizu hunk_fingerprint signature drift =="
  FP="$("$PIN" mint --repo "$KIZU" --from b4e6a5d src/app.rs:602)"
  out="$("$PIN" resolve --repo "$KIZU" --to HEAD --porcelain "$FP")"
  echo "$out"
  echo "$out" | grep -q 'src/app/layout.rs:' || fail "kizu hunk_fingerprint missed layout.rs: $out"
  echo "$out" | grep -Eq $'^(edited|moved)\t' || fail "expected edited/moved for hunk_fingerprint: $out"
  pass "kizu: pin(hunk_fingerprint) survived &crate::git::Hunk → &Hunk"

  echo "== 21. kizu edit_insert_str vis change =="
  INS="$("$PIN" mint --repo "$KIZU" --from b4e6a5d src/app.rs:635)"
  out="$("$PIN" resolve --repo "$KIZU" --to HEAD --porcelain "$INS")"
  echo "$out"
  echo "$out" | grep -q 'src/app/text_input.rs:' || fail "kizu edit_insert_str missed text_input.rs: $out"
  pass "kizu: pin(edit_insert_str) → src/app/text_input.rs"

  echo "== 22. kizu pinfile of the split, resolve with names only =="
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
  echo "== 23. voidtrace identity sanity =="
  file="$(git -C "$VOID" ls-files 'packages/kernel/src/evaluate.ts' | head -1)"
  if [[ -n "$file" ]]; then
    VP="$("$PIN" mint --repo "$VOID" --from HEAD "${file}:1")"
    out="$("$PIN" resolve --repo "$VOID" --to HEAD --porcelain "$VP")"
    echo "$out"
    echo "$out" | grep -q $'^same\t' || fail "voidtrace identity should be same: $out"
    echo "$out" | grep -q "${file}:1" || fail "voidtrace identity jumped file: $out"
    echo "$out" | grep -q 'cli.test.ts' && fail "voidtrace import{ clone stole the pin: $out"
    pass "voidtrace HEAD identity on $file:1"
  else
    echo "SKIP voidtrace (packages/kernel/src/evaluate.ts missing)"
  fi
fi

TENA="${TENA:-/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi}"
if [[ -d "$TENA/.git" || -f "$TENA/.git" ]]; then
  echo "== 24. tenaoshi KinsokuEngine.transform first-commit → HEAD =="
  TP="$("$PIN" mint --repo "$TENA" --from a41089c Engine/Sources/TenaoshiEngine/KinsokuEngine.swift:12)"
  out="$("$PIN" resolve --repo "$TENA" --to HEAD --porcelain "$TP")"
  echo "$out"
  echo "$out" | grep -q 'KinsokuEngine.swift:12' || fail "tenaoshi transform did not stay on line 12: $out"
  echo "$out" | grep -q $'1.000' || fail "tenaoshi expected 1.000: $out"
  pass "tenaoshi transform pin a41089c → HEAD line 12 score 1.000"
fi

echo
echo "All demo checks passed."
exit 0
