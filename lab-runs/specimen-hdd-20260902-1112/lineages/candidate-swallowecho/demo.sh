#!/usr/bin/env bash
# Run swallowecho on || echo last-status lies, including specimen-043's step.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/swallowecho"

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
  if [ -n "${SPECIMEN:-}" ] && [ -f "$SPECIMEN/files/workflows/staleness_check.yml" ]; then
    printf '%s\n' "$SPECIMEN"
    return 0
  fi
  local root cand
  while IFS= read -r root; do
    [ -z "$root" ] && continue
    cand="$root/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-043"
    if [ -f "$cand/files/workflows/staleness_check.yml" ]; then
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

echo "== nearest existing: bash + \$? on false || echo ok =="
set +e
bash -c 'false || echo ok'
echo "bash_step_status:$?"
set -e
echo

echo "== swallowecho 'false || echo ok' =="
python3 "$CLI" 'false || echo ok'
echo

echo "== swallowecho 'true && echo ok' =="
python3 "$CLI" 'true && echo ok'
echo

echo "== swallowecho -- false '||' echo ok (argv list) =="
python3 "$CLI" -- false '||' echo ok
echo

THEN_BODY='bazel query '\''attr(tags, "staleness_test", //...)'\'' | xargs bazel test $BAZEL_FLAGS || echo "Please run ./regenerate_stale_files.sh to regenerate stale files"'

echo "== then-branch analogue (recorded bazel pipeline status 1) =="
python3 "$CLI" --status 1 "$THEN_BODY"
echo

if [ -f "${SPECIMEN:-}/files/workflows/staleness_check.yml" ]; then
  echo "== fixture $SPECIMEN/files/workflows/staleness_check.yml =="
  python3 - "$SPECIMEN/files/workflows/staleness_check.yml" "$CLI" <<'PY'
import subprocess, sys
from pathlib import Path

yaml_path = Path(sys.argv[1])
cli = sys.argv[2]
text = yaml_path.read_text(encoding="utf-8")
lines = text.splitlines()
start = None
for i, line in enumerate(lines):
    if line.strip() == "bash: >":
        start = i + 1
        break
if start is None:
    raise SystemExit("demo.sh: no bash: > block in workflow yaml")
block = []
for line in lines[start:]:
    if line.startswith("            "):
        block.append(line[12:])
        continue
    if line.strip() == "":
        continue
    break
snippet = " ".join(part.strip() for part in block if part.strip())
print("extracted_bash:", flush=True)
print(snippet, flush=True)
print(flush=True)
then_at = snippet.find("then ")
else_at = snippet.find("; else")
if then_at < 0 or else_at < 0 or else_at <= then_at:
    raise SystemExit("demo.sh: then/else not found in extracted bash")
then_body = snippet[then_at + 5 : else_at].strip()
print("extracted_then:", flush=True)
print(then_body, flush=True)
print(flush=True)
print("== swallowecho --status 1 on extracted then-body ==", flush=True)
then_proc = subprocess.run(
    [sys.executable, cli, "--status", "1", then_body],
    check=False,
)
print(flush=True)
print("== swallowecho --status 1 on full workflow bash (scheduled, vars unset) ==", flush=True)
full = subprocess.run(
    [
        sys.executable,
        cli,
        "--no-process-env",
        "--unset",
        "COMMIT_TRIGGERED_RUN",
        "--unset",
        "MAIN_RUN",
        "--status",
        "1",
        snippet,
    ],
    check=False,
)
print(flush=True)
print("== unseen: make test || true (recorded make status 1) ==", flush=True)
unseen = subprocess.run(
    [sys.executable, cli, "--status", "1", "make test || true"],
    check=False,
)
if then_proc.returncode != 0:
    raise SystemExit(then_proc.returncode)
if full.returncode != 0:
    raise SystemExit(full.returncode)
raise SystemExit(unseen.returncode)
PY
else
  echo "demo.sh: specimen-043 not found; then-branch analogue only" >&2
fi
