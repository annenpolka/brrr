#!/usr/bin/env bash
# Leave a long-lived child in the process group.
set -euo pipefail
root="${1:?root}"
printf 'started\n' >"$root/flag.txt"
sleep 30 &
printf 'parent-done\n'
exit 0
