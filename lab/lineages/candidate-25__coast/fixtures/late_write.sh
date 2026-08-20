#!/usr/bin/env bash
# Main process exits; a child writes later.
set -euo pipefail
root="${1:?root}"
printf 'during\n' >"$root/out.txt"
(
  sleep 0.35
  printf 'after\n' >"$root/late.txt"
) &
printf 'parent-done\n'
exit 0
