#!/usr/bin/env bash
# Exercise deja against a synthetic repo with a known security hole,
# a later fix, a later relapse, and an undone bugfix.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
DEJA="$ROOT/deja"
chmod +x "$DEJA"

if ! command -v python3 >/dev/null; then
  echo "demo: python3 is required" >&2
  exit 1
fi
if ! command -v git >/dev/null; then
  echo "demo: git is required" >&2
  exit 1
fi

TMP="$(mktemp -d "${TMPDIR:-/tmp}/deja-demo.XXXXXX")"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

git init -q "$TMP/repo"
REPO="$TMP/repo"
git -C "$REPO" config user.name "deja-demo"
git -C "$REPO" config user.email "deja@example.test"

# 1. Introduce an auth bypass and a parser without a guard.
cat > "$REPO/auth.py" <<'PY'
def allowed(user):
    if user.role == "god" or user.has_backdoor_token:
        return True
    return user.role in {"admin", "member"}
PY
cat > "$REPO/parser.py" <<'PY'
def parse_token(raw):
    kind, _, rest = raw.partition(":")
    return {"kind": kind, "value": rest}
PY
git -C "$REPO" add auth.py parser.py
git -C "$REPO" commit -q -m "feat: add auth roles and token parser"

# 2. Delete the bypass (the historical incident).
cat > "$REPO/auth.py" <<'PY'
def allowed(user):
    return user.role in {"admin", "member"}
PY
git -C "$REPO" add auth.py
git -C "$REPO" commit -q -m "fix: remove god-role auth bypass"

# 3. Add a real bugfix guard.
cat > "$REPO/parser.py" <<'PY'
def parse_token(raw):
    if raw is None or raw == "":
        raise ValueError("empty token")
    kind, _, rest = raw.partition(":")
    return {"kind": kind, "value": rest}
PY
git -C "$REPO" add parser.py
git -C "$REPO" commit -q -m "fix: reject empty tokens"

# 4. Unrelated work so the incidents are not HEAD.
cat > "$REPO/util.py" <<'PY'
def slugify(name):
    return name.strip().lower().replace(" ", "-")
PY
git -C "$REPO" add util.py
git -C "$REPO" commit -q -m "feat: add slugify helper"

fail=0
passc=0
ok() { passc=$((passc + 1)); echo "ok  - $1"; }
bad() { fail=$((fail + 1)); echo "FAIL- $1" >&2; }

# Working tree: relapse the bypass (reformatted) and undo the empty-token guard.
cat > "$REPO/auth.py" <<'PY'
def allowed(user):
    if user.role == "god" or user.has_backdoor_token:
        return True
    return user.role in {"admin", "member"}
PY
cat > "$REPO/parser.py" <<'PY'
def parse_token(raw):
    kind, _, rest = raw.partition(":")
    return {"kind": kind, "value": rest}
PY
echo 'def ping(): return "pong"' >> "$REPO/util.py"

echo "== worktree: expect RELAPSE + UNDOFIX =="
set +e
"$DEJA" --repo "$REPO" --porcelain > "$TMP/work.tsv"
rc=$?
set -e
echo "(exit $rc)"
cat "$TMP/work.tsv"

if [[ "$rc" -eq 1 ]] && grep -q $'^RELAPSE\thigh\tauth.py' "$TMP/work.tsv" \
   && grep -q $'^UNDOFIX\thigh\tparser.py' "$TMP/work.tsv"; then
  ok "worktree flags relapse and undone fix"
else
  bad "worktree should exit 1 with RELAPSE+UNDOFIX"
fi

# Innocent extra line must not be flagged.
if grep -q ping "$TMP/work.tsv"; then
  bad "innocent slugify/ping edit was flagged"
else
  ok "innocent addition ignored"
fi

echo
echo "== clean tree: expect exit 0 =="
git -C "$REPO" checkout -q -- .
set +e
"$DEJA" --repo "$REPO" --porcelain > "$TMP/clean.tsv"
rc=$?
set -e
if [[ "$rc" -eq 0 && ! -s "$TMP/clean.tsv" ]]; then
  ok "clean worktree is silent"
else
  bad "clean worktree should be empty/0 (exit $rc)"
  cat "$TMP/clean.tsv" || true
fi

echo
echo "== stdin inverted deletion of the bypass =="
# Re-apply the hole as a piped diff (the inverse of the fix commit).
FIX=$(git -C "$REPO" log --grep='god-role' --format=%H -n1)
git -C "$REPO" diff "$FIX" "$FIX^" > "$TMP/readd-bypass.diff"
set +e
"$DEJA" --repo "$REPO" --stdin --porcelain < "$TMP/readd-bypass.diff" > "$TMP/stdin.tsv"
rc=$?
set -e
cat "$TMP/stdin.tsv"
if [[ "$rc" -eq 1 ]] && grep -q '^RELAPSE' "$TMP/stdin.tsv"; then
  ok "stdin inverse-of-fix is a RELAPSE"
else
  bad "stdin inverse-of-fix should be RELAPSE"
fi

echo
echo "== review the slugify commit: expect clean =="
SLUG=$(git -C "$REPO" log --grep='slugify' --format=%H -n1)
set +e
"$DEJA" --repo "$REPO" -c "$SLUG" --porcelain > "$TMP/slug.tsv"
rc=$?
set -e
if [[ "$rc" -eq 0 && ! -s "$TMP/slug.tsv" ]]; then
  ok "unrelated feature commit is clean"
else
  bad "slugify commit should be clean (exit $rc)"
  cat "$TMP/slug.tsv" || true
fi

echo
echo "== human output still parses =="
git -C "$REPO" checkout -q -- .
# restore dirty tree
cat > "$REPO/auth.py" <<'PY'
def allowed(user):
    if user.role == "god" or user.has_backdoor_token:
        return True
    return user.role in {"admin", "member"}
PY
set +e
"$DEJA" --repo "$REPO" > "$TMP/human.txt"
set -e
if grep -q RELAPSE "$TMP/human.txt" && grep -q has_backdoor_token "$TMP/human.txt"; then
  ok "human format names the relapsed identifier"
else
  bad "human format missing relapse body"
  cat "$TMP/human.txt" || true
fi

echo
echo "== move a bugfix to a new file: expect clean =="
git -C "$REPO" checkout -q -- .
mkdir -p "$REPO/guards"
cat > "$REPO/parser.py" <<'PY'
def parse_token(raw):
    from guards.empty import reject_empty
    reject_empty(raw)
    kind, _, rest = raw.partition(":")
    return {"kind": kind, "value": rest}
PY
cat > "$REPO/guards/empty.py" <<'PY'
def reject_empty(raw):
    if raw is None or raw == "":
        raise ValueError("empty token")
PY
git -C "$REPO" add parser.py guards/empty.py
set +e
"$DEJA" --repo "$REPO" --porcelain > "$TMP/moved.tsv"
rc=$?
set -e
if [[ "$rc" -eq 0 && ! -s "$TMP/moved.tsv" ]]; then
  ok "moved guard is not an UNDOFIX"
else
  bad "moving a fix-line to another file should be clean (exit $rc)"
  cat "$TMP/moved.tsv" || true
fi

echo
echo "== resurrect a deleted file path =="
git -C "$REPO" reset -q --hard HEAD
git -C "$REPO" clean -qfd
# history: add then delete a debug shell
cat > "$REPO/debug_shell.py" <<'PY'
def debug_shell(user):
    if user.has_backdoor_token:
        return True
    return False
PY
git -C "$REPO" add debug_shell.py
git -C "$REPO" commit -q -m "feat: temporary debug shell"
git -C "$REPO" rm -q debug_shell.py
git -C "$REPO" commit -q -m "fix: remove debug admin shell"
# working tree puts the file back
cat > "$REPO/debug_shell.py" <<'PY'
def debug_shell(user):
    if user.has_backdoor_token:
        return True
    return False
PY
set +e
"$DEJA" --repo "$REPO" --porcelain > "$TMP/resurrect.tsv"
rc=$?
set -e
cat "$TMP/resurrect.tsv"
if [[ "$rc" -eq 1 ]] && grep -q $'^RESURRECT\thigh\tdebug_shell.py' "$TMP/resurrect.tsv"; then
  ok "deleted path coming back is RESURRECT"
else
  bad "expected RESURRECT for debug_shell.py"
fi
# line-level RELAPSE of the same file should be suppressed
if grep -q $'^RELAPSE' "$TMP/resurrect.tsv"; then
  bad "RESURRECT should suppress per-line RELAPSE of the same path"
else
  ok "RESURRECT clusters the file instead of per-line noise"
fi

echo
echo "== 'fixed-width' is not a bugfix commit =="
git -C "$REPO" checkout -q -- .
rm -f "$REPO/debug_shell.py"
# A feature commit whose subject contains 'fixed' must not mark layout lines sacred.
cat > "$REPO/layout.py" <<'PY'
def gutter():
    return 4
PY
git -C "$REPO" add layout.py
git -C "$REPO" commit -q -m "feat: add fixed-width gutter helper"
cat > "$REPO/layout.py" <<'PY'
def gutter():
    return 8
PY
set +e
"$DEJA" --repo "$REPO" --porcelain > "$TMP/fixedword.tsv"
rc=$?
set -e
if grep -q UNDOFIX "$TMP/fixedword.tsv"; then
  bad "'fixed-width' feature was treated as a bugfix"
  cat "$TMP/fixedword.tsv" || true
else
  ok "adjective 'fixed' does not mint an UNDOFIX"
fi

echo
echo "== ugly paths: spaces, unicode, nested junk =="
git -C "$REPO" reset -q --hard HEAD
git -C "$REPO" clean -qfd
mkdir -p "$REPO/old copies/v1"
cat > "$REPO/old copies/v1/バックドア.py" <<'PY'
def allow_backdoor_operator(user):
    return user.has_backdoor_token
PY
git -C "$REPO" add "old copies/v1/バックドア.py"
git -C "$REPO" commit -q -m "feat: stash backup of backdoor helper"
git -C "$REPO" rm -q "old copies/v1/バックドア.py"
git -C "$REPO" commit -q -m "fix: delete leftover backdoor helper"
mkdir -p "$REPO/old copies/v1"
cat > "$REPO/old copies/v1/バックドア.py" <<'PY'
def allow_backdoor_operator(user):
    return user.has_backdoor_token
PY
set +e
"$DEJA" --repo "$REPO" --porcelain > "$TMP/ugly.tsv"
rc=$?
set -e
cat "$TMP/ugly.tsv"
if [[ "$rc" -eq 1 ]] && grep -q $'^RESURRECT\thigh\told copies/v1/バックドア.py' "$TMP/ugly.tsv"; then
  ok "resurrects unicode/space path without git-add"
else
  bad "ugly path resurrection missed"
fi

echo
echo "demo: $passc passed, $fail failed"
if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
exit 0
