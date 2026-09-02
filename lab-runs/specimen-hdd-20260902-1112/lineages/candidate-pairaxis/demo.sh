#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
python3 "$HERE/pairaxis" "$HERE/fixtures/pair_a.rec" "$HERE/fixtures/pair_b.rec"
python3 "$HERE/pairaxis" "$HERE/fixtures/unseen_a.rec" "$HERE/fixtures/unseen_b.rec"
