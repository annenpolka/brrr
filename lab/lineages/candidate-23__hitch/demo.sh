#!/usr/bin/env bash
# Empirical demo: hitch must exit 0. Fixtures prove the wait-graph;
# kizu + voidtrace prove it survives real test runners.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
HITCH="$ROOT/hitch"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/hitch-demo.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

need() {
  command -v "$1" >/dev/null || { echo "missing $1" >&2; exit 1; }
}
need python3
need lsof
need ps

check_json() {
  python3 - "$1" "$2" <<'PY'
import json, sys
path, spec = sys.argv[1], sys.argv[2]
rep = json.load(open(path))
assert rep.get("samples", 0) >= 1, rep
kinds = {s.get("wait", {}).get("kind") for s in rep.get("snags") or []}
kinds |= {g.get("kind") for g in rep.get("graph") or []}
want = [k for k in spec.split(",") if k]
missing = [k for k in want if k not in kinds]
if missing:
    sys.stderr.write(f"{path}: missing {missing}; saw {sorted(kinds)}\n")
    sys.stderr.write(json.dumps({k: rep[k] for k in ("wall_s", "samples", "snags", "graph") if k in rep}, indent=2)[:2000] + "\n")
    sys.exit(1)
print(f"  ok {path.split('/')[-1]}  wall={rep.get('wall_s')}s  kinds={sorted(kinds)}")
PY
}

echo "== hitch selftest"
"$HITCH" selftest

echo "== pipe-read (child blocked on parent writer)"
"$HITCH" --json -o "$TMP/pipe.json" --ignore-exit --expect-kind pipe-read \
  --interval 0.08 --min-block 0.08 --min-idle 0.12 \
  -- python3 "$ROOT/fixtures/pipe_block.py" 0.65
check_json "$TMP/pipe.json" "pipe-read"

echo "== tcp (client recv, server silent)"
"$HITCH" --json -o "$TMP/tcp.json" --ignore-exit --expect-kind tcp \
  --interval 0.08 --min-block 0.08 \
  -- python3 "$ROOT/fixtures/tcp_block.py" 0.65
check_json "$TMP/tcp.json" "tcp"

echo "== fifo (reader blocked on empty fifo)"
"$HITCH" --json -o "$TMP/fifo.json" --ignore-exit --expect-kind fifo \
  --interval 0.08 --min-block 0.08 \
  -- python3 "$ROOT/fixtures/fifo_block.py" 0.65
check_json "$TMP/fifo.json" "fifo"

echo "== sleep (timer-only test)"
"$HITCH" --json -o "$TMP/sleep.json" --ignore-exit --expect-kind sleep \
  --interval 0.08 --min-block 0.08 \
  -- python3 "$ROOT/fixtures/sleep_block.py" 0.45
check_json "$TMP/sleep.json" "sleep"

echo "== fold JSONL samples"
"$HITCH" --samples "$TMP/pipe.jsonl" --json -o "$TMP/pipe-run.json" --ignore-exit \
  --interval 0.08 --min-block 0.08 \
  -- python3 "$ROOT/fixtures/pipe_block.py" 0.45
"$HITCH" --json fold "$TMP/pipe.jsonl" > "$TMP/folded.json"
check_json "$TMP/folded.json" "pipe-read"

echo "== snap -p on a live sleeper"
python3 "$ROOT/fixtures/sleep_block.py" 1.4 &
spid=$!
sleep 0.2
"$HITCH" --json -p "$spid" > "$TMP/snap.json" || true
kill "$spid" 2>/dev/null || true
wait "$spid" 2>/dev/null || true
check_json "$TMP/snap.json" "sleep"

echo "== dogfood: kizu cargo test"
if command -v cargo >/dev/null && [[ -d /Users/annenpolka/ghq/github.com/annenpolka/kizu ]]; then
  (
    cd /Users/annenpolka/ghq/github.com/annenpolka/kizu
    "$HITCH" --json -o "$TMP/kizu.json" --ignore-exit --expect-kind child-wait \
      --interval 0.12 --min-block 0.08 --timeout 45 \
      -- cargo test --offline --lib \
         watcher::tests::writes_inside_git_dir_do_not_emit_worktree_event \
         -- --exact
  )
  check_json "$TMP/kizu.json" "child-wait"
else
  echo "  skip kizu (no cargo/repo)"
fi

echo "== dogfood: voidtrace vitest"
if command -v pnpm >/dev/null && [[ -d /Users/annenpolka/ghq/github.com/annenpolka/voidtrace ]]; then
  (
    cd /Users/annenpolka/ghq/github.com/annenpolka/voidtrace
    "$HITCH" --json -o "$TMP/voidtrace.json" --ignore-exit \
      --interval 0.08 --min-block 0.05 --timeout 40 \
      -- pnpm exec vitest run \
         packages/contracts/src/canonical-json.test.ts \
         packages/contracts/src/validator.test.ts
  )
  python3 - "$TMP/voidtrace.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
assert r["samples"] >= 1 and r["wall_s"] > 0, r
kinds = {s.get("wait", {}).get("kind") for s in r.get("snags") or []}
kinds |= {g.get("kind") for g in r.get("graph") or []}
print(f"  ok voidtrace.json  wall={r['wall_s']}s  samples={r['samples']}  kinds={sorted(kinds)}")
PY
else
  echo "  skip voidtrace (no pnpm/repo)"
fi

echo
echo "demo ok  reports in $TMP (cleaned on exit)"
