#!/usr/bin/env bash
# Empirical demo for spoor. Fixtures first, then real repos. Exit 0 on success.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
chmod +x "$ROOT/spoor"
SPOOR="$ROOT/spoor"
PY="${PYTHON:-python3}"
WORK="$ROOT/fixtures/work"
mkdir -p "$WORK"
export PATH="$ROOT:$PATH"

pass() { echo "  PASS  $*"; }
fail() { echo "  FAIL  $*" >&2; exit 1; }

echo "== parser unit checks =="
"$PY" - "$SPOOR" <<'PY'
import sys
from importlib.machinery import SourceFileLoader
m = SourceFileLoader("spoor", sys.argv[1]).load_module()
assert m.parse_test_line("test foo::bar ... ok")["name"] == "foo::bar"
assert m.parse_test_line("test foo::bar ... ok")["status"] == "passed"
assert m.parse_test_line("test foo::bar ... FAILED")["status"] == "failed"
assert m.parse_test_line("test afterexit::during ... ok")["runner"] == "libtest"
assert m.parse_test_line("tests/x.py::test_a PASSED")["runner"] == "pytest"
assert m.parse_test_line("Test Case '-[WindowTitleParserTests testFoo]' passed")["runner"] == "xctest"
assert m.parse_test_line("✓ src/foo.test.ts > does a thing")["runner"] == "vitest"
assert m.parse_test_line("hello world") is None
hdr = '// Generated from specs/main.pkl. Do not edit.\n'
assert m.parse_declared_source(hdr) == "specs/main.pkl"
jhdr = '{\n  "kind": "x",\n  "source": "specs/main.pkl"\n}\n'
assert m.parse_declared_source(jhdr) == "specs/main.pkl"
print("parser ok")
PY
pass "parse_test_line"

echo "== inspect: generated residue on a tiny ugly tree =="
# Make the declared product older than specs/main.pkl.
touch -t 202001010101.00 "$ROOT/fixtures/gen_tree/out/demo.generated.ts"
touch "$ROOT/fixtures/gen_tree/specs/main.pkl"
"$SPOOR" inspect --json --out "$WORK/inspect-fixture.json" "$ROOT/fixtures/gen_tree"
"$PY" - "$WORK/inspect-fixture.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
by = {g["path"].replace("\\", "/"): g for g in r["generated"]}
# paths may be out/demo.generated.ts
stale = [g for g in r["generated"] if g["status"] == "stale"]
orphan = [g for g in r["generated"] if g["status"] == "orphan-source"]
inherited = [g for g in r["generated"] if g.get("inherited_source")]
assert stale, r["generated"]
assert orphan, r["generated"]
assert inherited, r["generated"]
print(f"stale={len(stale)} orphan={len(orphan)} inherited={len(inherited)}")
PY
pass "inspect fixture tree (stale/orphan/undeclared)"

echo "== afterexit: waitpid is not completion =="
OUT="$WORK/afterexit-out"
rm -rf "$OUT"
mkdir -p "$OUT"
"$SPOOR" run --quiet --settle-ms 450 --settle-timeout-ms 3000 \
  --watch "$OUT" --out "$WORK/afterexit.json" \
  -- "$PY" "$ROOT/fixtures/afterexit.py" "$OUT"
"$PY" - "$WORK/afterexit.json" "$OUT" <<'PY'
import json, sys, os
r = json.load(open(sys.argv[1]))
out = sys.argv[2]
late_paths = [w["path"] for w in r["late_writes"]]
joined = "\n".join(late_paths)
assert os.path.exists(os.path.join(out, "during.txt")), "missing during.txt"
assert os.path.exists(os.path.join(out, "late.txt")), "missing late.txt"
assert any(p.endswith("late.txt") for p in late_paths), ("no late write recorded", r["late_writes"], r["watch_backend"])
assert r["tests"]["count"] >= 1
print("late_writes", len(r["late_writes"]), "backend", r["watch_backend"], "settle_ms", r["settle_ms"])
PY
pass "late write after waitpid"

echo "== leak: descendant outlives waitpid =="
"$SPOOR" run --quiet --kill-leaked --settle-ms 200 --settle-timeout-ms 800 \
  --out "$WORK/leak.json" \
  -- "$PY" "$ROOT/fixtures/leak.py"
"$PY" - "$WORK/leak.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
assert r["leaked_processes"], ("expected leaked pid", r.get("leaked_processes"), r.get("timeline_events"))
print("leaked", [(p["pid"], p["command"][:60]) for p in r["leaked_processes"]])
assert r.get("killed_leaked"), "kill-leaked did not record pids"
PY
pass "leaked process + kill-leaked"

echo "== collide: two tests, one path =="
"$SPOOR" run --quiet --sandbox-tmp --settle-ms 250 --settle-timeout-ms 1500 \
  --out "$WORK/collide.json" \
  -- "$PY" "$ROOT/fixtures/collide.py"
"$PY" - "$WORK/collide.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
assert r["tests"]["count"] == 2, r["tests"]
coll = r["collisions"]
assert coll, ("expected collision", r["tests"], r.get("per_test_fs"), r["watch_backend"], r.get("tmp_residue"))
print("collisions", coll)
names = set()
for c in coll:
    names.update(c["tests"])
assert "collide::alpha" in names and "collide::beta" in names, names
PY
pass "test isolation collision"

echo "== real repos: inspect generated artifacts =="
for repo in \
  /Users/annenpolka/ghq/github.com/annenpolka/voidtrace \
  /Users/annenpolka/ghq/github.com/annenpolka/tenaoshi \
  /Users/annenpolka/ghq/github.com/annenpolka/kizu \
  /Users/annenpolka/ghq/github.com/annenpolka/sitbone \
  /Users/annenpolka/ghq/github.com/annenpolka/skills
do
  name="$(basename "$repo")"
  if [[ ! -d "$repo" ]]; then
    echo "  skip missing $repo"
    continue
  fi
  "$SPOOR" inspect --json --out "$WORK/inspect-$name.json" "$repo"
  "$PY" - "$WORK/inspect-$name.json" "$name" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
name = sys.argv[2]
st = r["generated_status"]
print(f"  {name}: scanned={r['scanned_files']} generated={r['generated_count']} status={st} bursts={len(r['write_bursts'])}")
assert r["scanned_files"] >= 1
PY
  pass "inspect $name"
done

echo "== wrap a real kizu unit test (already-built tree) =="
KIZU=/Users/annenpolka/ghq/github.com/annenpolka/kizu
if [[ -x "$KIZU/target/debug/kizu" ]] && command -v cargo >/dev/null; then
  "$SPOOR" run --quiet --sandbox-tmp --kill-leaked --settle-ms 300 --settle-timeout-ms 2000 \
    --cwd "$KIZU" --out "$WORK/kizu-test.json" \
    -- cargo test --lib scan_scars_finds_ask -- --test-threads=1
  "$PY" - "$WORK/kizu-test.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
print(f"  kizu cargo test exit={r['exit_code']} duration={r['duration_ms']}ms waitpid={r['waitpid_ms']}ms settle={r['settle_ms']}ms")
print(f"  tests={r['tests']['count']} passed={r['tests']['passed']} leaked={len(r['leaked_processes'])} late={len(r['late_writes'])} git+={len(r['git_residue']['introduced'])} tmp={len(r['tmp_residue'])} coll={len(r['collisions'])}")
assert r["exit_code"] == 0, r["exit_code"]
assert r["tests"]["passed"] >= 1, r["tests"]
PY
  pass "kizu cargo test wrap"
else
  echo "  skip kizu wrap (no debug binary)"
fi

echo
echo "ALL CHECKS PASSED"
echo "reports under $WORK"
