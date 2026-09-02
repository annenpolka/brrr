#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/dockpath"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest existing operation (cat cgroup plus grep mountinfo) =="
echo "cgroup v2: 0::/system.slice/containerd.service"
echo "mountinfo: /var/lib/docker/containers/<id>/hostname"
echo "(two files, one decision; the join is the object)"
echo
echo "== dockpath specimen-065 cgroup v2 (owned miss; remap did not run) =="
python3 "$CLI" "$ROOT/fixtures/cgroup_v2.excerpt" "$ROOT/fixtures/mountinfo_v2.hostname.excerpt" --cwd /builds/project/src
echo
echo "== dockpath specimen-065 cgroup v1+v2 mixed (remapped unsupported) =="
python3 "$CLI" "$ROOT/fixtures/cgroup_v1.excerpt" "$ROOT/fixtures/mountinfo_v2.hostname.excerpt" --cwd /builds/project/src
echo
echo "== dockpath unseen podman overlay =="
python3 "$CLI" "$ROOT/fixtures/unseen-cgroup.excerpt" "$ROOT/fixtures/unseen-mountinfo.excerpt" --cwd /work/src
