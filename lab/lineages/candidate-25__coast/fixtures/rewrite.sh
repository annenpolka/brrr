#!/usr/bin/env bash
# A bundler-like rewriter: same path, several generations, then exit clean.
set -euo pipefail
root="${1:?root}"
printf 'layer-1\n' >"$root/bundle.js"
sleep 0.08
printf 'layer-2\n' >"$root/bundle.js"
sleep 0.08
printf 'layer-3\n' >"$root/bundle.js"
exit 0
