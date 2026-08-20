#!/usr/bin/env bash
# Write one file and exit with no children.
set -euo pipefail
root="${1:?root}"
printf 'only\n' >"$root/out.txt"
exit 0
