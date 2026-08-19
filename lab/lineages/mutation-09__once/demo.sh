#!/usr/bin/env bash
# demo.sh — exercise once on a synthetic ugly repo, then on real git repos.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
ONCE="$ROOT/once"
chmod +x "$ONCE"

fail() { echo "demo FAIL: $*" >&2; exit 1; }
ok() { echo "demo ok: $*"; }

command -v python3 >/dev/null || fail "python3 required"
command -v git >/dev/null || fail "git required"

FIX="$(mktemp -d "${TMPDIR:-/tmp}/once-demo.XXXXXX")"
cleanup() { rm -rf "$FIX"; }
trap cleanup EXIT

git -C "$FIX" init -q
git -C "$FIX" config user.email "once@demo.local"
git -C "$FIX" config user.name "once demo"
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
ORIG="$(git -C "$FIX" rev-parse HEAD)"

# --- commit 2: exact copy (the kinship event) ------------------------------
cp "$FIX/util.sh" "$FIX/util-backup.sh"
git -C "$FIX" add util-backup.sh
git -C "$FIX" commit -qm "copy util -> util-backup"

# --- commit 3: both sides drift -------------------------------------------
printf '\necho new-in-util\n' >> "$FIX/util.sh"
printf '\necho new-in-backup\n' >> "$FIX/util-backup.sh"
git -C "$FIX" add util.sh util-backup.sh
git -C "$FIX" commit -qm "drift both copies"

# --- commit 4: exact copy into a weird filename ---------------------------
cp "$FIX/util.sh" "$FIX/weird name 日本語.sh"
git -C "$FIX" add "weird name 日本語.sh"
git -C "$FIX" commit -qm "copy to weird filename"
printf '\necho weird\n' >> "$FIX/weird name 日本語.sh"
git -C "$FIX" add "weird name 日本語.sh"
git -C "$FIX" commit -qm "drift weird filename"

# --- known non-kin: copy edited before the first commit of the copy -------
# Never share a blob. Similarity would guess; once must refuse.
cp "$FIX/util.sh" "$FIX/edited-before-add.sh"
printf '\necho sneaky\n' >> "$FIX/edited-before-add.sh"
git -C "$FIX" add edited-before-add.sh
git -C "$FIX" commit -qm "copy edited before add"

# --- known non-kin: similar-looking file, never the same blob -------------
cat > "$FIX/similar.sh" <<'EOF'
#!/bin/sh
# shared helper
echo start
echo work
echo END
EOF
git -C "$FIX" add similar.sh
git -C "$FIX" commit -qm "looks similar, different blob"

# --- frozen twin, then one-sided edit -------------------------------------
cp "$FIX/util.sh" "$FIX/frozen.sh"
git -C "$FIX" add frozen.sh
git -C "$FIX" commit -qm "freeze a copy of util"
printf '\necho onesided\n' >> "$FIX/util.sh"
git -C "$FIX" add util.sh
git -C "$FIX" commit -qm "onesided util change"

# --- currently-identical twins --------------------------------------------
echo "same-now" > "$FIX/ident-a.txt"
cp "$FIX/ident-a.txt" "$FIX/ident-b.txt"
git -C "$FIX" add ident-a.txt ident-b.txt
git -C "$FIX" commit -qm "identical pair"

# --- nested git dir (must not be walked as the repo) ----------------------
mkdir -p "$FIX/nested"
git -C "$FIX/nested" init -q
echo inner > "$FIX/nested/inner.txt"
git -C "$FIX/nested" add inner.txt
git -C "$FIX/nested" -c user.email=n@n -c user.name=n commit -qm inner
echo outer > "$FIX/nested-outer.txt"
git -C "$FIX" add nested-outer.txt
git -C "$FIX" commit -qm "file beside nested git"

# --- echo: restore an old blob onto a new path after the source moved -----
git -C "$FIX" show "$ORIG:util.sh" > "$FIX/ash-util.sh"
git -C "$FIX" add ash-util.sh
git -C "$FIX" commit -qm "archive original util blob"

# --- default listing: drifted exact kin, not identical, not guesses -------
OUT="$("$ONCE" -C "$FIX")"
if echo "$OUT" | grep -q ident-a; then fail "identical pair leaked into default listing"$'\n'"$OUT"; fi
if echo "$OUT" | grep -q edited-before-add; then fail "edited-before-add is not exact kin"$'\n'"$OUT"; fi
if echo "$OUT" | grep -q similar.sh; then fail "similar.sh is not exact kin"$'\n'"$OUT"; fi
echo "$OUT" | grep -q 'util.sh' || fail "expected util.sh kinship"$'\n'"$OUT"
echo "$OUT" | grep -q 'util-backup.sh' || fail "expected util-backup.sh"$'\n'"$OUT"
echo "$OUT" | grep -q 'frozen.sh' || fail "expected frozen.sh"$'\n'"$OUT"
echo "$OUT" | grep -q 'weird name' || fail "expected weird filename"$'\n'"$OUT"
echo "$OUT" | grep -q 'ash-util.sh' || fail "expected echo archive of original blob"$'\n'"$OUT"
ok "default listing is exact-blob kin only (refuses similarity / pre-add edits)"
echo "$OUT"

# --- --identical includes ident-* -----------------------------------------
IDOUT="$("$ONCE" -C "$FIX" --identical --no-header)"
echo "$IDOUT" | grep -q ident-a || fail "expected identical pair with --identical"$'\n'"$IDOUT"
ok "--identical reports current copies"

# --- --check exits 1 on drift ---------------------------------------------
set +e
"$ONCE" -C "$FIX" --check >/dev/null
rc=$?
set -e
[ "$rc" -eq 1 ] || fail "--check should exit 1, got $rc"
ok "--check exits 1 when drifted kin exist"

# --- inspect two paths (TSV one row); frozen.sh still equals base ---------
ROW="$("$ONCE" -C "$FIX" --no-header util.sh frozen.sh)"
echo "$ROW" | grep -q frozen.sh || fail "inspect pair failed"$'\n'"$ROW"
# paths sorted: frozen.sh < util.sh so frozen.sh is column a
echo "$ROW" | awk -F'\t' '{exit ($9=="a"?0:1)}' || fail "frozen.sh should be frozen=a"$'\n'"$ROW"
ok "frozen side detected (a still at shared blob)"

# --- --port FROM TO applies FROM's unique lines onto TO -------------------
PORTED="$("$ONCE" -C "$FIX" --port util.sh frozen.sh)"
echo "$PORTED" | grep -q onesided || fail "port did not carry onesided change"$'\n'"$PORTED"
echo "$PORTED" | grep -q start || fail "port lost shared body"$'\n'"$PORTED"
ok "--port util.sh frozen.sh carries the onesided change"

# --- echo port: apply all post-origin util edits onto the archived blob ---
PORTED2="$("$ONCE" -C "$FIX" --port util.sh ash-util.sh)"
echo "$PORTED2" | grep -q onesided || fail "echo port missed onesided"$'\n'"$PORTED2"
echo "$PORTED2" | grep -q new-in-util || fail "echo port missed later util drift"$'\n'"$PORTED2"
ok "--port util.sh ash-util.sh uses the original blob as merge-base"

# --- refuse --port on non-kin ---------------------------------------------
set +e
ERR="$("$ONCE" -C "$FIX" --port util.sh edited-before-add.sh 2>&1)"
prc=$?
set -e
[ "$prc" -eq 2 ] || fail "--port non-kin should exit 2, got $prc"$'\n'"$ERR"
echo "$ERR" | grep -q 'not kin' || fail "expected not kin error"$'\n'"$ERR"
ok "--port refuses paths that never shared a blob"

# --- pretty + json parse --------------------------------------------------
"$ONCE" -C "$FIX" --pretty | grep -q '↔' || fail "pretty missing arrow"
python3 -c "import json,sys,subprocess
p=subprocess.check_output(['$ONCE','-C','$FIX','--json'])
j=json.loads(p)
assert isinstance(j,list) and j, j
assert {'kind','a','b','base_blob','frozen'} <= set(j[0])
assert all(x['kind'] in ('together','echo') for x in j), j
kinds=set(x['kind'] for x in j)
assert 'echo' in kinds, j
assert 'together' in kinds, j
"
ok "pretty and json work; kinds are together|echo only"

# --- restrict by glob -----------------------------------------------------
G="$("$ONCE" -C "$FIX" --glob '*.txt')"
if echo "$G" | grep -q util.sh; then fail "glob leaked util.sh"$'\n'"$G"; fi
ok "--glob '*.txt' excludes .sh (no drifted txt twins by default)"

# --- --frozen filters to one-sided still-at-base --------------------------
FZ="$("$ONCE" -C "$FIX" --frozen --no-header)"
echo "$FZ" | grep -q frozen.sh || fail "--frozen missed frozen.sh"$'\n'"$FZ"
# both-drifted together pairs have frozen='-'; those must disappear
NONFZ="$(echo "$FZ" | awk -F'\t' '$9!="a" && $9!="b" {print}')"
[ -z "$NONFZ" ] || fail "--frozen included a non-frozen pair"$'\n'"$FZ"
ok "--frozen keeps snapshot twins, drops both-drifted pairs"

# --- echo kind on ash-util ------------------------------------------------
ASH="$("$ONCE" -C "$FIX" --no-header util.sh ash-util.sh)"
echo "$ASH" | awk -F'\t' '{exit ($1=="echo"?0:1)}' || fail "ash-util should be kind=echo"$'\n'"$ASH"
ok "archive of an old blob is echo (never coexisted)"

# --- pretty occupancy span ------------------------------------------------
"$ONCE" -C "$FIX" --pretty | grep -q 'held a ' || fail "pretty missing occupancy span"
ok "pretty shows held a..b occupancy"

# --- --sync FROM updates every frozen twin --------------------------------
SYNC="$("$ONCE" -C "$FIX" --sync util.sh)"
echo "$SYNC" | grep -q onesided || fail "--sync missed onesided"$'\n'"$SYNC"
echo "$SYNC" | grep -q 'once sync' || fail "--sync should header multiple frozen twins"$'\n'"$SYNC"
ok "--sync util.sh prints a 3-way onto each frozen twin"

set +e
"$ONCE" -C "$FIX" --sync similar.sh >/dev/null 2>"$FIX/sync.err"
src=$?
set -e
[ "$src" -eq 1 ] || fail "--sync with no frozen twin should exit 1, got $src"
ok "--sync without a frozen twin exits 1"

"$ONCE" -C "$FIX" --sync util.sh --write 2>/dev/null
grep -q onesided "$FIX/frozen.sh" || fail "--sync --write did not update frozen.sh"
grep -q onesided "$FIX/ash-util.sh" || fail "--sync --write did not update ash-util.sh"
ok "--sync --write materializes FROM onto frozen snapshots"

# --- real repos, read-only ------------------------------------------------
count_pairs() {
  python3 -c "import json,subprocess,sys
j=json.loads(subprocess.check_output(sys.argv[1:]))
print(len(j))
" "$@"
}

SKILLS=/Users/annenpolka/ghq/github.com/annenpolka/skills
if [ -d "$SKILLS/.git" ]; then
  echo "---- once -C skills --pretty ----"
  "$ONCE" -C "$SKILLS" --pretty
  n="$(count_pairs "$ONCE" -C "$SKILLS" --json)"
  echo "skills drifted kin pairs: $n"
  "$ONCE" -C "$SKILLS" --no-header | grep -q 'SKILL_claude.md' \
    || fail "skills should report SKILL.md ↔ SKILL_claude.md via shared old blob"
  PORTED_SK="$("$ONCE" -C "$SKILLS" --port emergent-engine/SKILL.md emergent-engine/SKILL_claude.md)"
  NOW_SK="$(git -C "$SKILLS" show HEAD:emergent-engine/SKILL.md)"
  [ "$PORTED_SK" = "$NOW_SK" ] || fail "port onto frozen SKILL_claude.md should equal current SKILL.md"
  SYNC_SK="$("$ONCE" -C "$SKILLS" --sync emergent-engine/SKILL.md)"
  [ "$SYNC_SK" = "$NOW_SK" ] || fail "--sync SKILL.md should equal current SKILL.md (one frozen twin)"
  ok "skills frozen twin: port is identity with FROM; --sync is the same shot"
else
  echo "demo skip: skills not present" >&2
fi

KIZU=/Users/annenpolka/ghq/github.com/annenpolka/kizu
if [ -d "$KIZU/.git" ]; then
  echo "---- once -C kizu (must refuse 56% init split) ----"
  KOUT="$("$ONCE" -C "$KIZU" --pretty)"
  echo "$KOUT" | head -20
  if echo "$KOUT" | grep -q 'src/init/install.rs'; then
    fail "kizu install.rs never shared a blob with init.rs; similarity is forbidden"
  fi
  ok "kizu: no exact-blob kin for the 56% module split"
else
  echo "demo skip: kizu not present" >&2
fi

SIT=/Users/annenpolka/ghq/github.com/annenpolka/sitbone
if [ -d "$SIT/.git" ]; then
  n="$(count_pairs "$ONCE" -C "$SIT" --json)"
  echo "sitbone drifted exact-blob kin pairs: $n"
  ok "sitbone scan completed"
else
  echo "demo skip: sitbone not present" >&2
fi

DG=/Users/annenpolka/ghq/github.com/annenpolka/dignity-guide
if [ -d "$DG/.git" ]; then
  echo "---- once -C dignity-guide --frozen --pretty ----"
  "$ONCE" -C "$DG" --frozen --pretty | head -40
  n="$(count_pairs "$ONCE" -C "$DG" --json)"
  echo "dignity-guide drifted kin pairs: $n"
  "$ONCE" -C "$DG" --no-header | grep -q 'old-version' \
    || fail "dignity-guide should report old-version snapshots as exact-blob kin"
  ok "dignity-guide old-version snapshots are frozen exact kin"
else
  echo "demo skip: dignity-guide not present" >&2
fi

EL=/Users/annenpolka/ghq/github.com/annenpolka/emergent-loop
if [ -d "$EL/.git" ]; then
  n="$(count_pairs "$ONCE" -C "$EL" --json)"
  echo "emergent-loop drifted kin pairs: $n"
  "$ONCE" -C "$EL" --pretty | head -20
  [ "$n" -ge 1 ] || fail "emergent-loop should have ash/ snapshots of chapter blobs"
  ok "emergent-loop ash snapshots detected"
else
  echo "demo skip: emergent-loop not present" >&2
fi

ok "all demo checks passed"
exit 0
