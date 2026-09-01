#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="${1:-}"
for d in "$ROOT"/lab-hdd/lineages/candidate-*; do
  name=$(basename "$d")
  echo "======== $name unittest ========"
  (cd "$d" && python3 -m unittest discover -s tests -q)
  echo "======== $name demo ========"
  (cd "$d" && ./demo.sh)
done
echo ALL_OK
