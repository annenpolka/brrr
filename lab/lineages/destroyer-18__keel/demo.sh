#!/usr/bin/env bash
# Re-run the keel origin-identity battery. Does not rewrite the victim.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
chmod +x "$ROOT/attack.py" "$ROOT/attack2.py"
KEEL="${KEEL:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-cb0da2df3d3e/keel}"
chmod +x "$KEEL"
echo "== victim selftest =="
"$KEEL" --selftest
echo "== round 1: remotes / graft / --to-dir / v1 / kizu =="
python3 "$ROOT/attack.py"
echo "== round 2: mint-then-advance (dest tip not in token) =="
python3 "$ROOT/attack2.py"
echo
echo "transcripts: /tmp/destroy-keel/transcript.txt /tmp/destroy-keel/transcript-round2.txt"
echo "report: $ROOT/DESTROYER_KEEL.md"
exit 0
