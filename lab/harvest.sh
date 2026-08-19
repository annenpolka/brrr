#!/usr/bin/env bash
# Copy candidate reports from isolated worktrees into lab/lineages/.
# Parent-tree only. Does not merge code.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${WORKTREE_ROOT:-$HOME/.grok/worktrees/annenpolka-brrr}"
DEST="$ROOT/lab/lineages"
mkdir -p "$DEST"
ts="$(TZ=Asia/Tokyo date '+%Y-%m-%d %H:%M:%S JST')"
echo "# harvest $ts"
if [[ ! -d "$SRC" ]]; then
  echo "no worktree root: $SRC"
  exit 0
fi
for d in "$SRC"/subagent-*; do
  [[ -d "$d" ]] || continue
  id="$(basename "$d")"
  name=""
  if [[ -f "$d/CANDIDATE.md" ]]; then
    name="$(sed -n '1s/^# //p' "$d/CANDIDATE.md" | tr '/ ' '__' | tr -cd 'A-Za-z0-9._-')"
  fi
  out="$DEST/${name:-$id}"
  mkdir -p "$out"
  for f in CANDIDATE.md README.md demo.sh; do
    if [[ -e "$d/$f" ]]; then
      cp "$d/$f" "$out/$f"
    fi
  done
  git -C "$d" log --oneline -8 > "$out/COMMITS.txt" 2>/dev/null || true
  git -C "$d" rev-parse --abbrev-ref HEAD > "$out/BRANCH.txt" 2>/dev/null || true
  git -C "$d" rev-parse HEAD > "$out/HEAD.txt" 2>/dev/null || true
  echo "$d" > "$out/WORKTREE.txt"
  echo "harvested $id -> $out"
done
