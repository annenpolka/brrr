#!/usr/bin/env bash
# Run freshmiss on the specimen-011 input-hash cache pair.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/freshmiss"

candidate_roots() {
  local top common parent
  top="$(git -C "$1" rev-parse --show-toplevel 2>/dev/null || true)"
  [ -n "$top" ] && printf '%s\n' "$top"
  common="$(git -C "$1" rev-parse --git-common-dir 2>/dev/null || true)"
  if [ -n "$common" ]; then
    parent="$(cd "$1" && cd "$common/.." && pwd)"
    printf '%s\n' "$parent"
  fi
}

find_specimen() {
  if [ -n "${SPECIMEN:-}" ] && [ -f "$SPECIMEN/files/cache_build.py" ]; then
    printf '%s\n' "$SPECIMEN"
    return 0
  fi
  local root cand
  while IFS= read -r root; do
    [ -z "$root" ] && continue
    cand="$root/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-011"
    if [ -f "$cand/files/cache_build.py" ]; then
      printf '%s\n' "$cand"
      return 0
    fi
  done < <(candidate_roots "$ROOT"; candidate_roots "$(pwd)")
  return 1
}

SPECIMEN="$(find_specimen || true)"

if [ ! -x "$CLI" ]; then
  chmod +x "$CLI"
fi
if [ ! -f "$CLI" ]; then
  echo "demo.sh: missing CLI at $CLI" >&2
  exit 1
fi
if [ ! -f "$SPECIMEN/files/cache_build.py" ]; then
  echo "demo.sh: specimen-011 fixture not found at $SPECIMEN" >&2
  echo "demo.sh: set SPECIMEN to the specimen-011 directory" >&2
  exit 1
fi

WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/freshmiss-demo.XXXXXX")"
cleanup() { rm -rf "$WORKDIR"; }
trap cleanup EXIT

echo "== fixture $SPECIMEN/files/cache_build.py =="
python3 "$SPECIMEN/files/cache_build.py"
echo

# Replay the same two-build sequence with a kept outdir so present is observed.
python3 - "$SPECIMEN/files/cache_build.py" "$WORKDIR" <<'PY'
import importlib.machinery
import importlib.util
import sys
from pathlib import Path

fixture, workdir = Path(sys.argv[1]), Path(sys.argv[2])
loader = importlib.machinery.SourceFileLoader("cache_build", str(fixture))
spec = importlib.util.spec_from_loader(loader.name, loader)
mod = importlib.util.module_from_spec(spec)
loader.exec_module(mod)

outdir = workdir / "out"
outdir.mkdir()
cache = set()
inputs = {"src": "hello"}
s1, _e1, k1 = mod.build(cache, outdir, inputs, extra=False)
s2, _e2, k2 = mod.build(cache, outdir, inputs, extra=True)

(workdir / "first.rec").write_text(
    f"status\t{s1}\nidentity\t{k1}\nrequested\tout.bin\ndir\t{outdir}\n",
    encoding="utf-8",
)
(workdir / "second.rec").write_text(
    f"status\t{s2}\nidentity\t{k2}\nrequested\tout.bin\t"
    f"out.sbom\ndir\t{outdir}\n",
    encoding="utf-8",
)
print(f"replay_first\t{s1}\t{k1}")
print(f"replay_second\t{s2}\t{k2}")
print(f"outdir\t{outdir}")
PY
echo

echo "== ls of replay outdir (nearest existing operation) =="
ls -1 "$WORKDIR/out"
echo "missing_check out.sbom: $( [ -e "$WORKDIR/out/out.sbom" ] && echo present || echo absent )"
echo

echo "== freshmiss first second (present observed from outdir) =="
python3 "$CLI" "$WORKDIR/first.rec" "$WORKDIR/second.rec"
