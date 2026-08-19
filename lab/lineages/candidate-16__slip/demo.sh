#!/usr/bin/env bash
# Exercise slip against a synthetic ugly git history and, when present, kizu.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SLIP="$ROOT/slip"
chmod +x "$SLIP"

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

TMP="$(mktemp -d "${TMPDIR:-/tmp}/slip-demo.XXXXXX")"
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

# colon in the filename — a locator-grammar trap
cat > "$REPO/src/weird:colon.py" <<'PY'
COLON_FILE = True
print("colon-named file")
PY

cat > "$REPO/src/日本語.py" <<'PY'
def greet():
    return "こんにちは"
PY

# nested git repo that must not hijack discovery when we --repo the outer
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
  -c user.name=slip -c user.email=slip@example.com \
  commit -q -m 'v1: original layout'
V1="$(git -C "$REPO" rev-parse HEAD)"

# --- snapshot v2: rename, split, edit, delete, unicode stays ---
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
# doomed() is gone on purpose

cat > "$REPO/Makefile" <<'MK'
.PHONY: test
test:
	python src/math/ops.py
MK

git -C "$REPO" add -A src Makefile notes
git -C "$REPO" \
  -c user.name=slip -c user.email=slip@example.com \
  commit -q -m 'v2: split calc, drop doomed, tweak sauce'
V2="$(git -C "$REPO" rev-parse HEAD)"

echo "== fixture refs =="
echo "V1=$V1"
echo "V2=$V2"

# Line numbers in v1 calc.py:
# 3 def add
# 7 def secret_sauce
# 11 def doomed
# 14 def helper_keep
# Makefile:2 test:
# notes/file with spaces.txt:1
# src/日本語.py:1 def greet
# src/weird:colon.py:1 COLON_FILE

echo "== 1. unchanged helper after file rename/split =="
out="$("$SLIP" --repo "$REPO" --from "$V1" --to "$V2" --porcelain src/calc.py:14)"
echo "$out"
echo "$out" | grep -q $'src/math/ops.py:8' || fail "helper_keep did not follow split+rename: $out"
echo "$out" | grep -Eq $'^(moved|same|edited)\t' || fail "unexpected status: $out"
pass "helper_keep relocated into src/math/ops.py"

echo "== 2. extracted+edited function =="
out="$("$SLIP" --repo "$REPO" --from "$V1" --to "$V2" --porcelain src/calc.py:7)"
echo "$out"
echo "$out" | grep -q 'src/math/sauce.py:' || fail "secret_sauce did not follow extract: $out"
echo "$out" | grep -Eq $'^(edited|moved)\t' || fail "expected edited/moved for signature drift: $out"
pass "secret_sauce relocated into src/math/sauce.py despite signature drift"

echo "== 3. deleted function =="
out="$("$SLIP" --repo "$REPO" --from "$V1" --to "$V2" --porcelain src/calc.py:11)"
echo "$out"
echo "$out" | grep -q $'^deleted\t' || fail "doomed() should be deleted: $out"
pass "doomed() reported deleted"

echo "== 4. stdin compiler-log rewrite =="
log="$TMP/log.txt"
cat > "$log" <<EOF
error: src/calc.py:3: undefined name
note: also see src/calc.py:14
EOF
rewritten="$("$SLIP" --repo "$REPO" --from "$V1" --to "$V2" < "$log")"
echo "$rewritten"
echo "$rewritten" | grep -q 'src/math/ops.py:' || fail "stdin rewrite missed ops.py: $rewritten"
echo "$rewritten" | grep -q 'src/calc.py:3' && fail "stdin rewrite left stale calc.py: $rewritten"
pass "stdin filter rewrote stale compiler locations"

echo "== 5. directory snapshots without git refs =="
mkdir -p "$TMP/from/src" "$TMP/to/src"
echo 'UNIQUE_TOKEN_QZX = 1' > "$TMP/from/src/old.py"
echo 'x = UNIQUE_TOKEN_QZX' >> "$TMP/from/src/old.py"
mkdir -p "$TMP/to/pkg"
echo 'UNIQUE_TOKEN_QZX = 1' > "$TMP/to/pkg/new.py"
out="$("$SLIP" --from-dir "$TMP/from" --to-dir "$TMP/to" --porcelain src/old.py:1)"
echo "$out"
echo "$out" | grep -q 'pkg/new.py:1' || fail "dir-to-dir unique token missed: $out"
pass "from-dir/to-dir unique-token match"

echo "== 6. identity on HEAD =="
out="$("$SLIP" --repo "$REPO" --from "$V2" --to "$V2" --porcelain src/math/ops.py:3)"
echo "$out"
echo "$out" | grep -q $'^same\t' || fail "identity should be same: $out"
pass "same-snapshot identity"

echo "== 7. per-locator ref syntax =="
out="$("$SLIP" --repo "$REPO" --to "$V2" --porcelain "$V1:src/calc.py:3")"
echo "$out"
echo "$out" | grep -q 'src/math/ops.py:' || fail "ref:path:line form failed: $out"
pass "ref:path:line argument form"

echo "== 8. unicode path still addressable =="
out="$("$SLIP" --repo "$REPO" --from "$V1" --to "$V2" --porcelain 'src/日本語.py:1')"
echo "$out"
echo "$out" | grep -q 'src/日本語.py:1' || fail "unicode path lost: $out"
pass "unicode filename"

echo "== 9. nested git does not hijack --repo =="
out="$("$SLIP" --repo "$REPO" --from "$V1" --to "$V2" --porcelain src/calc.py:3)"
echo "$out"
echo "$out" | grep -q 'src/math/ops.py' || fail "nested git confused outer resolve: $out"
pass "nested git ignored when --repo points at outer"

echo "== 10. json shape =="
out="$("$SLIP" --repo "$REPO" --from "$V1" --to "$V2" --json src/calc.py:3)"
echo "$out"
python3 -c 'import json,sys; o=json.loads(sys.argv[1]); assert o["status"] in ("moved","edited","same"); assert o["to"]["path"].endswith("ops.py")' "$out"
pass "json output"

echo "== 14. python traceback grammar =="
tb='  File "src/calc.py", line 3, in add'
rewritten="$(printf '%s\n' "$tb" | "$SLIP" --repo "$REPO" --from "$V1" --to "$V2")"
echo "$rewritten"
echo "$rewritten" | grep -q 'File "src/math/ops.py", line' || fail "python traceback not rewritten: $rewritten"
echo "$rewritten" | grep -q 'src/calc.py' && fail "python traceback left stale path: $rewritten"
pass "python traceback File/line rewrite"

echo "== 15. extensionless Makefile stdin =="
rewritten="$(printf '%s\n' 'Makefile:2: recipe failed' | "$SLIP" --repo "$REPO" --from "$V1" --to "$V2" --map --porcelain)"
echo "$rewritten"
echo "$rewritten" | grep -q $'Makefile:2' || fail "Makefile:2 not parsed: $rewritten"
pass "extensionless Makefile locator"

echo "== 16. colon filename in stdin =="
rewritten="$(printf '%s\n' 'error src/weird:colon.py:1: boom' | "$SLIP" --repo "$REPO" --from "$V1" --to "$V2")"
echo "$rewritten"
echo "$rewritten" | grep -q 'src/weird:colon.py:1' || fail "colon filename not preserved: $rewritten"
echo "$rewritten" | grep -q 'error src/weird:colon.py:1: boom' || fail "colon filename rewrite mangled the line: $rewritten"
pass "colon filename stdin"

echo "== 17. spaced filename in stdin =="
rewritten="$(printf '%s\n' 'notes/file with spaces.txt:1: see MAGIC' | "$SLIP" --repo "$REPO" --from "$V1" --to "$V2")"
echo "$rewritten"
echo "$rewritten" | grep -q 'notes/file with spaces.txt:1' || fail "spaced filename not parsed: $rewritten"
pass "spaced filename stdin"

echo "== 18. absolute CI path suffix =="
rewritten="$(printf '%s\n' '/home/runner/work/ugly/ugly/src/calc.py:14: error' | "$SLIP" --repo "$REPO" --from "$V1" --to "$V2")"
echo "$rewritten"
echo "$rewritten" | grep -q 'src/math/ops.py:' || fail "absolute path did not relocate: $rewritten"
pass "absolute CI path suffix bind"

echo "== 19. exact identity scores 1.000 =="
out="$("$SLIP" --repo "$REPO" --from "$V2" --to "$V2" --porcelain src/math/ops.py:3)"
echo "$out"
echo "$out" | grep -q $'same\tsrc/math/ops.py:3\tsrc/math/ops.py:3\t1.000\t' || fail "identity score was not 1.000: $out"
pass "exact same-path match scores 1.000"

echo "== 20. deleted line reports surviving neighborhood =="
out="$("$SLIP" --repo "$REPO" --from "$V1" --to "$V2" --porcelain src/calc.py:11)"
echo "$out"
echo "$out" | grep -q $'^deleted\t' || fail "doomed() should be deleted: $out"
echo "$out" | grep -Eq 'ops.py|sauce.py|helper_keep|gap' || fail "deleted hole had no neighborhood: $out"
pass "deleted line hole / last-context"

# --- real repo dogfood (read-only) ---
KIZU="${KIZU:-/Users/annenpolka/ghq/github.com/annenpolka/kizu}"
if [[ -d "$KIZU/.git" || -f "$KIZU/.git" ]]; then
  echo "== 11. kizu app.rs split (b4e6a5d → HEAD) =="
  # seen_hunk_fingerprint lived at src/app.rs:529 before the split.
  out="$("$SLIP" --repo "$KIZU" --from b4e6a5d --to HEAD --porcelain src/app.rs:529)"
  echo "$out"
  echo "$out" | grep -q 'src/app/layout.rs:' || fail "kizu seen_hunk_fingerprint did not land in layout.rs: $out"
  pass "kizu: src/app.rs:529 → src/app/layout.rs (file split)"

  echo "== 12. kizu nearest_landing_forward =="
  out="$("$SLIP" --repo "$KIZU" --from b4e6a5d --to HEAD --porcelain src/app.rs:543)"
  echo "$out"
  echo "$out" | grep -q 'src/app/navigation.rs:' || fail "kizu nearest_landing_forward missed navigation.rs: $out"
  pass "kizu: src/app.rs:543 → src/app/navigation.rs"

  echo "== 12b. kizu rustc/CI/python mixed log =="
  mixed="$TMP/kizu-log.txt"
  cat > "$mixed" <<EOF
error[E0599]: no method named seen_hunk_fingerprint
  --> /home/runner/work/kizu/kizu/src/app.rs:529:5
  File "src/app.rs", line 543, in nearest_landing_forward
LICENSE:1: copyright
EOF
  rewritten="$("$SLIP" --repo "$KIZU" --from b4e6a5d --to HEAD < "$mixed")"
  echo "$rewritten"
  echo "$rewritten" | grep -q 'src/app/layout.rs:' || fail "kizu CI abs path missed layout.rs: $rewritten"
  echo "$rewritten" | grep -q 'File "src/app/navigation.rs", line' || fail "kizu python tb missed navigation.rs: $rewritten"
  echo "$rewritten" | grep -q 'LICENSE:1' || fail "kizu LICENSE not parsed: $rewritten"
  pass "kizu mixed compiler/CI/python/LICENSE log"
else
  echo "SKIP kizu dogfood (repo not present at $KIZU)"
fi

VOID="${VOID:-/Users/annenpolka/ghq/github.com/annenpolka/voidtrace}"
if [[ -d "$VOID/.git" || -f "$VOID/.git" ]]; then
  echo "== 13. voidtrace identity sanity =="
  # A stable current file should map to itself HEAD→HEAD.
  file="$(git -C "$VOID" ls-files 'packages/kernel/src/evaluate.ts' | head -1)"
  if [[ -n "$file" ]]; then
    out="$("$SLIP" --repo "$VOID" --from HEAD --to HEAD --porcelain "${file}:1")"
    echo "$out"
    echo "$out" | grep -Eq $'^(same|edited|moved|unresolved)\t' || fail "voidtrace identity produced junk: $out"
    pass "voidtrace HEAD identity on $file:1"
  else
    echo "SKIP voidtrace (packages/kernel/src/evaluate.ts missing)"
  fi
fi

echo
echo "All demo checks passed."
exit 0
