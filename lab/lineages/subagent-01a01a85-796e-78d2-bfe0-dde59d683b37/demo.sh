#!/usr/bin/env bash
# demo.sh — exercise akin on a synthetic ugly repo, then on a real git repo.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
AKIN="$ROOT/akin"
chmod +x "$AKIN"

fail() { echo "demo FAIL: $*" >&2; exit 1; }
ok() { echo "demo ok: $*"; }

command -v python3 >/dev/null || fail "python3 required"
command -v git >/dev/null || fail "git required"

FIX="$(mktemp -d "${TMPDIR:-/tmp}/akin-demo.XXXXXX")"
cleanup() { rm -rf "$FIX"; }
trap cleanup EXIT

git -C "$FIX" init -q
git -C "$FIX" config user.email "akin@demo.local"
git -C "$FIX" config user.name "akin demo"
git -C "$FIX" config core.quotepath false

# --- commit 1: a shared ancestor file -------------------------------------
cat > "$FIX/util.sh" <<'EOF'
#!/bin/sh
# shared helper
echo start
echo work
echo end
EOF
git -C "$FIX" add util.sh
git -C "$FIX" commit -qm "init util"

# --- commit 2: exact copy (the kinship event) ------------------------------
cp "$FIX/util.sh" "$FIX/util-backup.sh"
git -C "$FIX" add util-backup.sh
git -C "$FIX" commit -qm "copy util -> util-backup"

# --- commit 3: both sides drift -------------------------------------------
printf '\necho new-in-util\n' >> "$FIX/util.sh"
printf '\necho new-in-backup\n' >> "$FIX/util-backup.sh"
git -C "$FIX" add util.sh util-backup.sh
git -C "$FIX" commit -qm "drift both copies"

# --- commit 4: exact copy into a weird filename, then drift in commit 4b --
cp "$FIX/util.sh" "$FIX/weird name 日本語.sh"
git -C "$FIX" add "weird name 日本語.sh"
git -C "$FIX" commit -qm "copy to weird filename"
printf '\necho weird\n' >> "$FIX/weird name 日本語.sh"
git -C "$FIX" add "weird name 日本語.sh"
git -C "$FIX" commit -qm "drift weird filename"

# --- known gap: copy edited before the first commit of the copy -----------
# (never share a blob at any commit; v1 misses this on purpose)
cp "$FIX/util.sh" "$FIX/edited-before-add.sh"
printf '\necho sneaky\n' >> "$FIX/edited-before-add.sh"
git -C "$FIX" add edited-before-add.sh
git -C "$FIX" commit -qm "copy edited before add"

# --- commit 5: frozen twin, then one-sided edit ---------------------------
cp "$FIX/util.sh" "$FIX/frozen.sh"
git -C "$FIX" add frozen.sh
git -C "$FIX" commit -qm "freeze a copy of util"
printf '\necho onesided\n' >> "$FIX/util.sh"
git -C "$FIX" add util.sh
git -C "$FIX" commit -qm "onesided util change"

# --- commit 6: currently-identical twins ----------------------------------
echo "same-now" > "$FIX/ident-a.txt"
cp "$FIX/ident-a.txt" "$FIX/ident-b.txt"
git -C "$FIX" add ident-a.txt ident-b.txt
git -C "$FIX" commit -qm "identical pair"

# --- commit 7: nested git dir (must not be walked as the repo) ------------
mkdir -p "$FIX/nested"
git -C "$FIX/nested" init -q
echo inner > "$FIX/nested/inner.txt"
git -C "$FIX/nested" add inner.txt
git -C "$FIX/nested" -c user.email=n@n -c user.name=n commit -qm inner
# leave nested/.git in the tree untracked; the file we care about is tracked
echo outer > "$FIX/nested-outer.txt"
git -C "$FIX" add nested-outer.txt
git -C "$FIX" commit -qm "file beside nested git"

# --- currently-identical pair should be hidden without --identical --------
OUT="$("$AKIN" -C "$FIX")"
if echo "$OUT" | grep -q ident-a; then fail "identical pair leaked into default listing"$'\n'"$OUT"; fi
echo "$OUT" | grep -q 'util.sh' || fail "expected util.sh kinship"$'\n'"$OUT"
echo "$OUT" | grep -q 'util-backup.sh' || fail "expected util-backup.sh"$'\n'"$OUT"
echo "$OUT" | grep -q 'frozen.sh' || fail "expected frozen.sh"$'\n'"$OUT"
echo "$OUT" | grep -q 'weird name' || fail "expected weird filename"$'\n'"$OUT"
ok "default listing contains drifted twins, not identical pair"
echo "$OUT"
echo "$OUT" | grep -q edited-before-add || fail "copy-edited-before-add should be detected as git copy"$'\n'"$OUT"
ok "copy edited before git add is detected"

# --- --identical includes ident-* -----------------------------------------
IDOUT="$("$AKIN" -C "$FIX" --identical --no-header)"
echo "$IDOUT" | grep -q ident-a || fail "expected identical pair with --identical"$'\n'"$IDOUT"
ok "--identical reports current copies"

# --- --check exits 1 on drift ---------------------------------------------
set +e
"$AKIN" -C "$FIX" --check >/dev/null
rc=$?
set -e
[ "$rc" -eq 1 ] || fail "--check should exit 1, got $rc"
ok "--check exits 1 when drifted kin exist"

# --- inspect two paths (TSV one row) --------------------------------------
ROW="$("$AKIN" -C "$FIX" --no-header util.sh frozen.sh)"
echo "$ROW" | grep -q frozen.sh || fail "inspect pair failed"$'\n'"$ROW"
# paths are sorted: frozen.sh < util.sh, so frozen.sh is column a and still equals base
# cols: kind score a b base_blob base_commit base_time insertions deletions frozen
echo "$ROW" | awk -F'\t' '{exit ($10=="a"?0:1)}' || fail "frozen.sh should be frozen=a (still at base)"$'\n'"$ROW"
ok "frozen side detected (a still at shared blob)"

# --- --port FROM TO applies FROM's unique lines onto TO -------------------
PORTED="$("$AKIN" -C "$FIX" --port util.sh frozen.sh)"
echo "$PORTED" | grep -q onesided || fail "port did not carry onesided change"$'\n'"$PORTED"
echo "$PORTED" | grep -q start || fail "port lost shared body"$'\n'"$PORTED"
ok "--port util.sh frozen.sh carries the onesided change"

# --- pretty + json parse --------------------------------------------------
"$AKIN" -C "$FIX" --pretty | grep -q '↔' || fail "pretty missing arrow"
python3 -c "import json,sys,subprocess
p=subprocess.check_output(['$AKIN','-C','$FIX','--json'])
j=json.loads(p)
assert isinstance(j,list) and j, j
assert {'kind','a','b','base_blob','frozen'} <= set(j[0])
"
ok "pretty and json work"

# --- restrict by glob -----------------------------------------------------
G="$("$AKIN" -C "$FIX" --glob '*.txt')"
if echo "$G" | grep -q util.sh; then fail "glob leaked util.sh"$'\n'"$G"; fi
ok "--glob '*.txt' excludes .sh (no drifted txt twins by default)"

# --- real repos, read-only ------------------------------------------------
count_pairs() {
  python3 -c "import json,subprocess,sys
j=json.loads(subprocess.check_output(sys.argv[1:]))
print(len(j))
" "$@"
}

has_pair() {
  local repo="$1" needle="$2"
  "$AKIN" -C "$repo" --no-header | grep -q -- "$needle"
}

REAL=/Users/annenpolka/ghq/github.com/annenpolka/sitbone
if [ -d "$REAL/.git" ]; then
  echo "---- akin -C sitbone --pretty ----"
  "$AKIN" -C "$REAL" --pretty | head -40
  n="$(count_pairs "$AKIN" -C "$REAL" --json)"
  echo "sitbone drifted kin pairs: $n"
  has_pair "$REAL" Logging.swift || fail "sitbone should report Logging.swift same-basename twins"
  ok "sitbone scan completed"
else
  echo "demo skip: sitbone not present" >&2
fi

KIZU=/Users/annenpolka/ghq/github.com/annenpolka/kizu
if [ -d "$KIZU/.git" ]; then
  echo "---- akin -C kizu (init split) ----"
  "$AKIN" -C "$KIZU" --pretty | head -40
  has_pair "$KIZU" 'src/init/install.rs' || fail "kizu should report init.rs copy to init/install.rs"
  ok "kizu copy-then-drift detected"
else
  echo "demo skip: kizu not present" >&2
fi

VT=/Users/annenpolka/ghq/github.com/annenpolka/voidtrace
if [ -d "$VT/.git" ]; then
  n="$(count_pairs "$AKIN" -C "$VT" --json)"
  echo "voidtrace drifted kin pairs: $n"
  [ "$n" -ge 1 ] || fail "voidtrace should have fixture copies"
  ok "voidtrace scan completed"
else
  echo "demo skip: voidtrace not present" >&2
fi

ok "all demo checks passed"
exit 0
