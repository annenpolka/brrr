#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
chmod +x "$ROOT/inprobe" 2>/dev/null || true
echo "== nearest: cat cgroup plus grep mountinfo =="
echo "cgroup v2 has no docker bytes; mountinfo still names a container path"
echo
echo "== inprobe specimen-065 =="
python3 "$ROOT/inprobe" "$ROOT/fixtures/065-cgroupv2.rec"
echo
echo "== inprobe unseen cgroup v1 =="
python3 "$ROOT/inprobe" "$ROOT/fixtures/unseen-v1.rec"
