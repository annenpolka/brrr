#!/usr/bin/env bash
# Exercise moor: bind a log instance to a current locator and a source hole.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
MOOR="$ROOT/moor"
chmod +x "$MOOR"

if ! command -v python3 >/dev/null; then
  echo "demo.sh: python3 is required" >&2
  exit 1
fi
if ! command -v git >/dev/null; then
  echo "demo.sh: git is required" >&2
  exit 1
fi

pass=0
fail=0

ok() { pass=$((pass + 1)); echo "  PASS  $1"; }
bad() { fail=$((fail + 1)); echo "  FAIL  $1"; echo "        $2"; }

TMP="$(mktemp -d "${TMPDIR:-/tmp}/moor-demo.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

echo "== selftest =="
if "$MOOR" --selftest; then
  ok "selftest"
else
  bad "selftest" "moor --selftest failed"
fi

# --- synthetic tree: format strings + file split + test decoy ---
REPO="$TMP/ugly"
mkdir -p "$REPO/src" "$REPO/tests" "$REPO/notes" "$REPO/vendor/nested/src"

cat > "$REPO/src/auth.py" <<'PY'
"""login helpers."""

def find_user(uid):
    if uid is None:
        raise KeyError(f"user {uid} not found")
    return uid

def secret_sauce(x):
    MAGIC = 0xDEADBEEF
    return x ^ MAGIC

def doomed():
    return "this will be deleted"
PY

cat > "$REPO/src/git.rs" <<'RS'
fn diff_one(stderr: &str) -> Result<(), anyhow::Error> {
    return Err(anyhow!("git diff single file failed: {}", stderr.trim()));
}
RS

cat > "$REPO/src/log.swift" <<'SW'
func started(profile: String) {
    Logger.core.info("session started profile=\(profile, privacy: .private)")
}
SW

cat > "$REPO/tests/test_auth.py" <<'PY'
def test_missing():
    # exact filled-in literal: a better raw unfmt match than the production template
    assert "user 42 not found" in "err"
PY

cat > "$REPO/Makefile" <<'MK'
.PHONY: test
test:
	python src/auth.py
MK

cat > "$REPO/notes/file with spaces.txt" <<'TXT'
see src/auth.py for MAGIC
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

echo 'NESTED = 1' > "$REPO/vendor/nested/src/inner.py"
git -C "$REPO/vendor/nested" init -q
git -C "$REPO/vendor/nested" add src/inner.py
git -C "$REPO/vendor/nested" \
  -c user.name=nested -c user.email=nested@example.com \
  commit -q -m 'nested repo seed'

git -C "$REPO" init -q
git -C "$REPO" add src tests Makefile notes
git -C "$REPO" \
  -c user.name=moor -c user.email=moor@example.com \
  commit -q -m 'v1: original layout'
V1="$(git -C "$REPO" rev-parse HEAD)"

mkdir -p "$REPO/src/users"
cat > "$REPO/src/users/lookup.py" <<'PY'
"""extracted user lookup."""

def find_user(uid):
    if uid is None:
        raise KeyError(f"user {uid} not found")
    return uid
PY

cat > "$REPO/src/math_sauce.py" <<'PY'
"""extracted condiment."""

def secret_sauce(x, extra=0):
    MAGIC = 0xDEADBEEF
    return (x ^ MAGIC) + extra
PY

rm -f "$REPO/src/auth.py"
# doomed() is gone

git -C "$REPO" add -A src tests Makefile notes
git -C "$REPO" \
  -c user.name=moor -c user.email=moor@example.com \
  commit -q -m 'v2: split auth, drop doomed'
V2="$(git -C "$REPO" rev-parse HEAD)"

echo "== fixture refs =="
echo "V1=$V1"
echo "V2=$V2"

echo "== 1. bind stale locator + interpolated message in one pass =="
out="$("$MOOR" --repo "$REPO" --from "$V1" --to "$V2" --porcelain 'src/auth.py:5: user 42 not found')"
echo "$out"
if echo "$out" | grep -q 'src/users/lookup.py' && echo "$out" | grep -q 'user {uid} not found' && echo "$out" | grep -q 'uid=42'; then
  ok "stale path + hole bind → lookup.py uid=42"
else
  bad "stale path + hole bind" "$out"
fi

echo "== 2. test literal must lose to production (joint, not unfmt) =="
if echo "$out" | grep -q 'tests/test_auth.py'; then
  bad "decoy test literal won" "$out"
else
  ok "production beats exact test literal via locator proximity"
fi
if echo "$out" | grep -Eq $'^(bound|matched)\t'; then
  ok "status is bound/matched"
else
  bad "status" "$out"
fi

echo "== 3. stdin rewrite: locators move AND holes unpack =="
log="$TMP/log.txt"
cat > "$log" <<EOF
ERROR src/auth.py:5 user 42 not found
note: also see src/auth.py:8
EOF
rewritten="$("$MOOR" --repo "$REPO" --from "$V1" --to "$V2" --rewrite --annotate < "$log")"
echo "$rewritten"
if echo "$rewritten" | grep -q 'src/users/lookup.py' && echo "$rewritten" | grep -q 'uid=42'; then
  ok "stdin rewrite + hole trailer"
else
  bad "stdin rewrite + hole trailer" "$rewritten"
fi
if echo "$rewritten" | grep -q 'src/auth.py:5'; then
  bad "left stale auth.py:5" "$rewritten"
else
  ok "stale auth.py:5 rewritten away"
fi

echo "== 4. rust anyhow template, no locator on the message line =="
out="$("$MOOR" --repo "$REPO" --from "$V1" --to "$V2" --porcelain --records line 'git diff single file failed: fatal: not a git repository')"
echo "$out"
if echo "$out" | grep -q 'git.rs' && echo "$out" | grep -q 'git diff single file failed: {}' && echo "$out" | grep -q 'fatal: not a git repository'; then
  ok "message-only bind of anyhow template"
else
  bad "message-only anyhow" "$out"
fi

echo "== 5. panic record groups locator line with the next message =="
panic_log="$TMP/panic.txt"
cat > "$panic_log" <<EOF
thread 'git::diff' panicked at src/git.rs:2:12:
git diff single file failed: boom
EOF
out="$("$MOOR" --repo "$REPO" --from "$V1" --to "$V2" --porcelain < "$panic_log")"
echo "$out"
if echo "$out" | grep -q 'git.rs' && echo "$out" | grep -q '0=boom\|boom'; then
  ok "panic two-liner binds locator + hole"
else
  bad "panic two-liner" "$out"
fi

echo "== 6. python traceback record + exception message =="
tb="$TMP/tb.txt"
cat > "$tb" <<EOF
Traceback (most recent call last):
  File "src/auth.py", line 5, in find_user
    raise KeyError(f"user {uid} not found")
KeyError: user 42 not found
EOF
rewritten="$("$MOOR" --repo "$REPO" --from "$V1" --to "$V2" --rewrite --annotate < "$tb")"
echo "$rewritten"
if echo "$rewritten" | grep -q 'File "src/users/lookup.py", line' && echo "$rewritten" | grep -q 'uid=42'; then
  ok "traceback File/line rewrite + hole bind"
else
  bad "traceback record" "$rewritten"
fi

echo "== 7. from-dir / to-dir (gitless) =="
mkdir -p "$TMP/from/src" "$TMP/to/pkg"
printf '%s\n' 'def boom():' '    raise RuntimeError(f"open {path}: {err}")' > "$TMP/from/src/old.py"
printf '%s\n' 'def boom():' '    raise RuntimeError(f"open {path}: {err}")' > "$TMP/to/pkg/new.py"
out="$("$MOOR" --from-dir "$TMP/from" --to-dir "$TMP/to" --porcelain 'src/old.py:2: open /tmp/x: permission denied')"
echo "$out"
if echo "$out" | grep -q 'pkg/new.py' && echo "$out" | grep -q 'path=/tmp/x' && echo "$out" | grep -q 'err=permission denied'; then
  ok "from-dir/to-dir bind named holes"
else
  bad "from-dir/to-dir" "$out"
fi

echo "== 8. swift interpolation name =="
out="$("$MOOR" --repo "$REPO" --from "$V1" --to "$V2" --porcelain 'session started profile=DeepWork')"
echo "$out"
if echo "$out" | grep -q 'log.swift' && echo "$out" | grep -q 'profile=DeepWork\|DeepWork'; then
  ok "swift profile hole"
else
  bad "swift profile hole" "$out"
fi

echo "== 9. rustc two-line record relocates the arrow locator =="
rustc="$TMP/rustc.txt"
cat > "$rustc" <<EOF
error[E0599]: no method named secret_sauce
  --> src/auth.py:8:5
EOF
rewritten="$("$MOOR" --repo "$REPO" --from "$V1" --to "$V2" --rewrite --no-annotate < "$rustc")"
echo "$rewritten"
if echo "$rewritten" | grep -q 'math_sauce.py' && echo "$rewritten" | grep -q 'secret_sauce'; then
  ok "rustc --> locator relocated across split"
else
  bad "rustc record" "$rewritten"
fi

echo "== 10. deleted doomed() stays deleted =="
out="$("$MOOR" --repo "$REPO" --from "$V1" --to "$V2" --porcelain src/auth.py:12)"
echo "$out"
if echo "$out" | grep -q $'^deleted\t'; then
  ok "deleted line reported"
else
  bad "deleted doomed" "$out"
fi

echo "== 11. json shape =="
out="$("$MOOR" --repo "$REPO" --from "$V1" --to "$V2" --json 'src/auth.py:5: user 42 not found')"
echo "$out"
if python3 -c 'import json,sys; o=json.loads(sys.argv[1]); assert o["to"]["path"].endswith("lookup.py"); assert o["holes"].get("uid")=="42"' "$out"; then
  ok "json holes.uid == 42"
else
  bad "json shape" "$out"
fi

echo "== 12. colon filename + spaced filename + absolute CI prefix =="
rewritten="$(printf '%s\n' 'error src/weird:colon.py:1: boom' 'notes/file with spaces.txt:1: see MAGIC' '/home/runner/work/ugly/ugly/src/auth.py:5: user 42 not found' | "$MOOR" --repo "$REPO" --from "$V1" --to "$V2" --rewrite --annotate)"
echo "$rewritten"
if echo "$rewritten" | grep -q 'src/weird:colon.py:1' && echo "$rewritten" | grep -q 'notes/file with spaces.txt:1' && echo "$rewritten" | grep -q 'src/users/lookup.py'; then
  ok "ugly path grammars"
else
  bad "ugly path grammars" "$rewritten"
fi

echo "== 12b. dest-only locator against an old --from (mixed log) =="
# v2 path does not exist in v1; v0.1 silently dropped it.
out="$("$MOOR" --repo "$REPO" --from "$V1" --to "$V2" --porcelain 'src/users/lookup.py:5: user 7 not found')"
echo "$out"
if echo "$out" | grep -q 'src/users/lookup.py' && echo "$out" | grep -q 'uid=7'; then
  ok "already-current dest path still binds holes"
else
  bad "dest-only locator" "$out"
fi

echo "== 13. nested git does not hijack --repo =="
out="$("$MOOR" --repo "$REPO" --from "$V1" --to "$V2" --porcelain 'src/auth.py:5: user 9 not found')"
if echo "$out" | grep -q 'src/users/lookup.py'; then
  ok "nested git ignored"
else
  bad "nested git" "$out"
fi

# --- real repo dogfood ---
KIZU="${KIZU:-/Users/annenpolka/ghq/github.com/annenpolka/kizu}"
SITBONE="${SITBONE:-/Users/annenpolka/ghq/github.com/annenpolka/sitbone}"
TENAOSHI="${TENAOSHI:-/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi}"

if [[ -d "$KIZU/.git" || -f "$KIZU/.git" ]]; then
  echo "== 14. kizu mixed CI log (stale app.rs + interpolated anyhow) =="
  mixed="$TMP/kizu-log.txt"
  cat > "$mixed" <<EOF
error[E0599]: no method named seen_hunk_fingerprint
  --> /home/runner/work/kizu/kizu/src/app.rs:529:5
  File "src/app.rs", line 543, in nearest_landing_forward
thread 'git::diff' panicked at src/git/diff.rs:34:28:
git diff single file failed: fatal: not a git repository (or any of the parent directories): /tmp/nope
EOF
  rewritten="$("$MOOR" --repo "$KIZU" --from b4e6a5d --to HEAD --rewrite --annotate < "$mixed")"
  echo "$rewritten"
  if echo "$rewritten" | grep -q 'src/app/layout.rs:'; then
    ok "kizu: app.rs:529 → layout.rs"
  else
    bad "kizu layout.rs" "$rewritten"
  fi
  if echo "$rewritten" | grep -q 'src/app/navigation.rs'; then
    ok "kizu: app.rs:543 → navigation.rs (python File grammar)"
  else
    bad "kizu navigation.rs" "$rewritten"
  fi
  if echo "$rewritten" | grep -q 'git diff single file failed: {}' && echo "$rewritten" | grep -q 'fatal: not a git repository'; then
    ok "kizu: anyhow template + bound hole in the same pass"
  else
    bad "kizu anyhow bind" "$rewritten"
  fi
  echo "== 14b. kizu rustc method name binds to slipped dest line =="
  out="$("$MOOR" --repo "$KIZU" --from b4e6a5d --to HEAD --porcelain --records auto <<'EOF'
error[E0599]: no method named seen_hunk_fingerprint
  --> src/app.rs:529:5
EOF
)"
  echo "$out"
  if echo "$out" | grep -q 'layout.rs' && echo "$out" | grep -q 'seen_hunk_fingerprint' && echo "$out" | grep -q 'no method named'; then
    ok "kizu rustc ident hole on slipped line"
  else
    bad "kizu rustc ident hole" "$out"
  fi
  echo "== 14c. kizu dest-only layout.rs against --from b4e6a5d =="
  rewritten="$("$MOOR" --repo "$KIZU" --from b4e6a5d --to HEAD --rewrite --annotate <<'EOF'
error src/app/layout.rs:17: no method named seen_hunk_fingerprint
EOF
)"
  echo "$rewritten"
  if echo "$rewritten" | grep -q 'src/app/layout.rs:17' && echo "$rewritten" | grep -q 'seen_hunk_fingerprint'; then
    ok "kizu dest-only path kept and ident-bound"
  else
    bad "kizu dest-only path" "$rewritten"
  fi
else
  echo "== 14. skip kizu (not present) =="
fi

if [[ -d "$SITBONE/.git" || -f "$SITBONE/.git" ]]; then
  echo "== 15. sitbone swift interpolation =="
  out="$("$MOOR" --repo "$SITBONE" --porcelain 'session started profile=DeepWork')"
  echo "$out"
  if echo "$out" | grep -q 'SitboneCore.swift' && echo "$out" | grep -q 'DeepWork'; then
    ok "sitbone session started profile hole"
  else
    bad "sitbone session started" "$out"
  fi
  out="$("$MOOR" --repo "$SITBONE" --porcelain 'cumulative save failed path=/tmp/c.json error=disk full')"
  echo "$out"
  if echo "$out" | grep -q 'JSONSessionStore.swift' && echo "$out" | grep -q 'cumulative save failed'; then
    ok "sitbone multiline cumulative save"
  else
    bad "sitbone cumulative save" "$out"
  fi
else
  echo "== 15. skip sitbone (not present) =="
fi

if [[ -d "$TENAOSHI/.git" || -f "$TENAOSHI/.git" ]]; then
  echo "== 16. tenaoshi untracked engine source =="
  out="$("$MOOR" --repo "$TENAOSHI" --porcelain 'has_more cannot be true when units is empty')"
  echo "$out"
  if echo "$out" | grep -q 'EditPlan.swift'; then
    ok "tenaoshi untracked EditPlan.swift"
  else
    bad "tenaoshi EditPlan" "$out"
  fi
else
  echo "== 16. skip tenaoshi (not present) =="
fi

echo
echo "passed=$pass failed=$fail"
if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
exit 0
