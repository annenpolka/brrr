#!/usr/bin/env bash
# Create an isolated git worktree for an embodiment. Does not merge onto main.
# Usage: make_worktree.sh <id> <branch-suffix>
set -euo pipefail
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
RUN_DIR="$(cd "$SCRIPTS/.." && pwd)"
REPO="$(cd "$RUN_DIR/../.." && pwd)"
ID="${1:?id e.g. candidate-01}"
SUFFIX="${2:?branch suffix e.g. gist}"
BRANCH="specimen-hdd/${ID}-${SUFFIX}"
DEST="${HDD_WORKTREE_ROOT:-$HOME/.grok/worktrees/annenpolka-brrr}/${ID}-${SUFFIX}"
mkdir -p "$(dirname "$DEST")"
git -C "$REPO" worktree add -b "$BRANCH" "$DEST" HEAD
echo "$DEST" >"$RUN_DIR/lineages/${ID}.worktree"
echo "$DEST"
