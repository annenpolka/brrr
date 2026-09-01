#!/usr/bin/env bash
# Show whence on real conflict-marker fixtures: ours, theirs, tagged hybrid, untagged refusal.
set -euo pipefail
cd "$(dirname "$0")"
PYTHON="${PYTHON:-python3}"
WHENCE=("$PYTHON" ./whence)
SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/whence-demo.XXXXXX")
cleanup() { rm -rf "$SCRATCH"; }
trap cleanup EXIT

copy() {
  cp "fixtures/$1" "$SCRATCH/$1"
}

banner() {
  printf '\n======== %s ========\n' "$1"
}

banner "report simple.conflict"
"${WHENCE[@]}" report fixtures/simple.conflict

banner "ours-only"
copy simple.conflict
"${WHENCE[@]}" resolve "$SCRATCH/simple.conflict" --ours
printf '%s\n' '--- resolved ---'
cat "$SCRATCH/simple.conflict"
printf '%s\n' '--- provenance file ---'
cat "$SCRATCH/simple.conflict.prov"

banner "theirs-only"
copy simple.conflict
cp fixtures/simple.conflict "$SCRATCH/theirs.conflict"
"${WHENCE[@]}" resolve "$SCRATCH/theirs.conflict" --theirs
printf '%s\n' '--- resolved ---'
cat "$SCRATCH/theirs.conflict"

banner "hybrid tagged success (ours color, theirs size)"
copy simple.conflict
cp fixtures/simple.conflict "$SCRATCH/hybrid.conflict"
"${WHENCE[@]}" resolve "$SCRATCH/hybrid.conflict" --hybrid fixtures/hybrid-tagged.txt
printf '%s\n' '--- resolved ---'
cat "$SCRATCH/hybrid.conflict"

banner "untagged hybrid failure (mixed red + size 2, no tags)"
copy simple.conflict
cp fixtures/simple.conflict "$SCRATCH/untagged.conflict"
set +e
"${WHENCE[@]}" resolve "$SCRATCH/untagged.conflict" --hybrid fixtures/untagged-mix.txt
untagged_rc=$?
set -e
printf 'exit=%s (expect nonzero)\n' "$untagged_rc"
printf '%s\n' '--- file left unresolved ---'
grep -n '<<<<<<\|======\|>>>>>>\|color' "$SCRATCH/untagged.conflict"

banner "diff3 ancestor markers refused (two parents only)"
set +e
"${WHENCE[@]}" resolve fixtures/diff3.conflict --ours --output "$SCRATCH/diff3.out"
diff3_rc=$?
set -e
printf 'exit=%s (expect nonzero)\n' "$diff3_rc"

banner "nearest existing: git merge-file --ours has no provenance"
mkdir -p "$SCRATCH/git"
printf 'color = red\nsize = 1\n' > "$SCRATCH/git/ours.txt"
printf 'color = blue\nsize = 2\n' > "$SCRATCH/git/theirs.txt"
printf 'color = green\nsize = 0\n' > "$SCRATCH/git/base.txt"
printf 'git merge-file --ours stdout:\n'
git merge-file -p --ours "$SCRATCH/git/ours.txt" "$SCRATCH/git/base.txt" "$SCRATCH/git/theirs.txt"
printf '(git wrote a blob and stopped; no per-span parent list)\n'

banner "real git merge of two overlapping branches"
repo="$SCRATCH/repo"
mkdir -p "$repo"
git -C "$repo" init -q -b main
git -C "$repo" config user.name whence-demo
git -C "$repo" config user.email whence-demo@example.invalid
# This environment may default to diff3/zdiff3; whence tracks two parents only.
git -C "$repo" config merge.conflictStyle merge
printf 'shared\nvalue = 0\nshared-end\n' > "$repo/config.txt"
git -C "$repo" add config.txt
git -C "$repo" commit -q -m 'base'
git -C "$repo" checkout -q -b feature
printf 'shared\nvalue = 2\nshared-end\n' > "$repo/config.txt"
git -C "$repo" commit -q -am 'feature sets 2'
git -C "$repo" checkout -q main
printf 'shared\nvalue = 1\nshared-end\n' > "$repo/config.txt"
git -C "$repo" commit -q -am 'main sets 1'
set +e
git -C "$repo" merge --no-edit --no-ff feature >/dev/null 2>"$SCRATCH/merge.err"
merge_rc=$?
set -e
printf 'git merge exit=%s\n' "$merge_rc"
printf '%s\n' '--- conflicted file ---'
cat "$repo/config.txt"
printf '%s\n' '--- whence --ours on the real conflict ---'
"${WHENCE[@]}" resolve "$repo/config.txt" --ours

banner "tests (shipped CLI)"
"$PYTHON" -m unittest discover -s tests -v
printf '\nall demo steps finished (untagged hybrid exit=%s)\n' "$untagged_rc"
if [ "$untagged_rc" -eq 0 ]; then
  printf 'expected untagged hybrid to fail\n' >&2
  exit 1
fi
exit 0
