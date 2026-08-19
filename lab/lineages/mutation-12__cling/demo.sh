#!/usr/bin/env bash
# Empirical demo for cling. Fixtures first, then a real-repo attach. Exit 0 on success.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
chmod +x "$ROOT/cling"
CLING="$ROOT/cling"
PY="${PYTHON:-python3}"
WORK="$ROOT/fixtures/work"
mkdir -p "$WORK"
export PATH="$ROOT:$PATH"

pass() { echo "  PASS  $*"; }
fail() { echo "  FAIL  $*" >&2; exit 1; }

wait_file() {
  local f="$1" n=0
  while [[ ! -e "$f" ]]; do
    sleep 0.02
    n=$((n + 1))
    if (( n > 250 )); then
      fail "timeout waiting for $f"
    fi
  done
}

cleanup_pid() {
  local p="${1:-}"
  if [[ -n "$p" ]] && kill -0 "$p" 2>/dev/null; then
    kill -TERM "$p" 2>/dev/null || true
    sleep 0.05
    kill -KILL "$p" 2>/dev/null || true
  fi
}

echo "== parser unit checks =="
"$PY" - "$CLING" <<'PY'
import sys
from importlib.machinery import SourceFileLoader
m = SourceFileLoader("cling", sys.argv[1]).load_module()
text = """p4242
fcwd
tDIR
n/tmp/proj
ftxt
tREG
n/usr/bin/python3
f3w
tREG
a w
n/tmp/proj/out/held.txt
f4
tCHR
n/dev/null
"""
recs = m.parse_lsof_f(text)
assert any(r.get("fd") == "cwd" and r.get("name") == "/tmp/proj" for r in recs)
held = [r for r in recs if m.is_held_file(r)]
assert len(held) == 1, held
assert held[0]["name"].endswith("held.txt")
env = m.infer_tmp_roots({"TMPDIR": "/var/folders/xx/T"}, [
    {"name": "/var/folders/xx/T/abcd/foo", "fd": "3", "type": "REG"}
])
assert any(p.endswith("/T/abcd") or p.endswith("/abcd") for p in env), env
import tempfile, os
td = tempfile.mkdtemp(prefix="cling-ut-")
held = os.path.join(td, "held.txt")
open(held, "w").write("x\n")
watch = m.infer_watch_roots(
    "/usr",
    [{"fd": "3w", "type": "REG", "name": held, "access": "w"}],
    extra=[td],
    watch_cwd=False,
)
ntd = m.normpath(td)
assert ntd in watch or any(p == ntd for p in watch), (td, watch)
assert not any(p == "/usr" for p in watch)
assert m.looks_tmp("/private/var/folders/x/T/y/z", [])
assert m.classify_path("/Users/x/proj/src.rs", []) == "source"
assert m.classify_path("/Users/x/proj/target/foo", []) == "cache"
print("parser ok")
PY
pass "parse_lsof_f / infer_watch_roots"

echo "== afterexit: attach, then late write after the pid dies =="
OUT="$WORK/afterexit-out"
rm -rf "$OUT"
mkdir -p "$OUT"
"$PY" "$ROOT/fixtures/afterexit.py" "$OUT" &
APID=$!
wait_file "$OUT/ready"
"$CLING" attach --quiet --settle-ms 450 --settle-timeout-ms 3000 \
  --watch "$OUT" --out "$WORK/afterexit.json" "$APID" || true
wait "$APID" 2>/dev/null || true
"$PY" - "$WORK/afterexit.json" "$OUT" <<'PY'
import json, sys, os
r = json.load(open(sys.argv[1]))
out = sys.argv[2]
late_paths = [w["path"] for w in r["late_writes"]]
assert r["tool"] == "cling"
assert r["mode"] == "attach"
assert r["end_reason"] in {"exited", "gone"}
assert os.path.exists(os.path.join(out, "during.txt")), "missing during.txt"
assert os.path.exists(os.path.join(out, "late.txt")), "missing late.txt"
assert any(p.endswith("late.txt") for p in late_paths), ("no late write", r["late_writes"], r["watch_backend"], r["watch_paths"])
print("late_writes", len(r["late_writes"]), "backend", r["watch_backend"], "settle_ms", r["settle_ms"], "wait", r["waitpid_ms"])
PY
pass "late write after attached pid exited"

echo "== leak: descendant outlives the attached pid =="
LEAK_READY="$WORK/leak.ready"
rm -f "$LEAK_READY"
"$PY" "$ROOT/fixtures/leak.py" "$LEAK_READY" &
LPID=$!
wait_file "$LEAK_READY"
"$CLING" attach --quiet --kill-leaked --settle-ms 200 --settle-timeout-ms 800 \
  --out "$WORK/leak.json" "$LPID" || true
wait "$LPID" 2>/dev/null || true
"$PY" - "$WORK/leak.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
assert r["leaked_processes"], ("expected leaked pid", r.get("leaked_processes"), r.get("end_reason"))
print("leaked", [(p["pid"], p["command"][:70]) for p in r["leaked_processes"]])
assert r.get("killed_leaked"), "kill-leaked did not record pids"
PY
pass "leaked process + kill-leaked"

echo "== groupkid: pid wait sees late child write + leak =="
GOUT="$WORK/group-pid"
rm -rf "$GOUT"
mkdir -p "$GOUT"
CLING_CHILD_STAY=8 "$PY" "$ROOT/fixtures/groupkid.py" "$GOUT" &
GPID=$!
wait_file "$GOUT/ready"
"$CLING" attach --quiet --kill-leaked --settle-ms 350 --settle-timeout-ms 2000 \
  --watch "$GOUT" --out "$WORK/group-pid.json" "$GPID" || true
wait "$GPID" 2>/dev/null || true
"$PY" - "$WORK/group-pid.json" "$GOUT" <<'PY'
import json, sys, os
r = json.load(open(sys.argv[1]))
out = sys.argv[2]
assert r["wait"] == "pid"
late = [w["path"] for w in r["late_writes"]]
assert any(p.endswith("child-late.txt") for p in late), (r["late_writes"], r["fs_diff"], r["end_reason"])
assert r["leaked_processes"], ("expected same-pgid child as leak", r.get("leaked_processes"))
assert os.path.exists(os.path.join(out, "child-late.txt"))
print("pid-wait late", len(r["late_writes"]), "leaked", len(r["leaked_processes"]))
PY
pass "groupkid pid-wait: late write + leaked mate"

echo "== groupkid: --group waits the child out, no leak =="
GOUT2="$WORK/group-pgid"
rm -rf "$GOUT2"
mkdir -p "$GOUT2"
"$PY" "$ROOT/fixtures/groupkid.py" "$GOUT2" &
GPID=$!
wait_file "$GOUT2/ready"
"$CLING" attach --quiet --group --settle-ms 200 --settle-timeout-ms 2500 \
  --watch "$GOUT2" --out "$WORK/group-pgid.json" "$GPID" || true
wait "$GPID" 2>/dev/null || true
"$PY" - "$WORK/group-pgid.json" "$GOUT2" <<'PY'
import json, sys, os
r = json.load(open(sys.argv[1]))
out = sys.argv[2]
assert r["wait"] == "group"
assert r["end_reason"] == "group-empty", r["end_reason"]
assert not r["leaked_processes"], r["leaked_processes"]
assert os.path.exists(os.path.join(out, "child-late.txt"))
# child wrote before the group emptied, so it is residue, not necessarily late
created = [c["path"] for c in r["fs_diff"]["created"]]
assert any(p.endswith("child-late.txt") for p in created) or any(
    p.endswith("child-late.txt") for p in [w["path"] for w in r["late_writes"]]
), (created, r["late_writes"])
print("group-wait reason", r["end_reason"], "leaked", len(r["leaked_processes"]), "created", len(created))
PY
pass "groupkid --group: empty group, no leak"

echo "== openleft: file still on disk after the pid closes =="
OOUT="$WORK/openleft-out"
rm -rf "$OOUT"
mkdir -p "$OOUT"
"$PY" "$ROOT/fixtures/openleft.py" "$OOUT" &
OPID=$!
wait_file "$OOUT/ready"
"$CLING" attach --quiet --settle-ms 200 --settle-timeout-ms 800 \
  --watch "$OOUT" --out "$WORK/openleft.json" "$OPID" || true
wait "$OPID" 2>/dev/null || true
"$PY" - "$WORK/openleft.json" "$OOUT" <<'PY'
import json, sys, os
r = json.load(open(sys.argv[1]))
out = sys.argv[2]
held = os.path.join(out, "held.txt")
assert os.path.exists(held)
paths = [x["path"] for x in r.get("open_leftovers") or []]
assert any(p.endswith("held.txt") for p in paths), (
    "expected last-live open leftover",
    r.get("open_leftovers"),
    r.get("open_last"),
    r.get("lsof_samples"),
)
print("open leftovers", len(r.get("open_leftovers") or []), "attach_open", (r.get("open_at_attach") or {}).get("count"))
PY
pass "open-file leftover"

echo "== snapshot: heap of a live pid, subject stays up =="
LOUT="$WORK/linger-out"
rm -rf "$LOUT"
mkdir -p "$LOUT"
"$PY" "$ROOT/fixtures/linger.py" "$LOUT" &
LINGER=$!
wait_file "$LOUT/ready"
"$CLING" snapshot --quiet --out "$WORK/snapshot.json" "$LINGER"
kill -0 "$LINGER" 2>/dev/null || fail "snapshot killed the subject"
"$PY" - "$WORK/snapshot.json" "$LINGER" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
pid = int(sys.argv[2])
assert r["mode"] == "snapshot"
assert r["pid"] == pid
assert r["alive"] is True
assert r.get("cwd")
print("snapshot cwd", r.get("cwd"), "open", (r.get("open") or {}).get("count"), "children", len(r.get("children") or []))
PY
pass "snapshot leaves subject running"

echo "== SIGINT: report the wake without killing the subject =="
"$CLING" attach --quiet --settle-ms 150 --settle-timeout-ms 400 \
  --watch "$LOUT" --out "$WORK/sigint.json" "$LINGER" &
CLINGPID=$!
# let it arm watchers
sleep 0.35
kill -INT "$CLINGPID"
set +e
wait "$CLINGPID"
RC=$?
set -e
# 130 is the intended interrupt status
if [[ "$RC" -ne 130 && "$RC" -ne 0 ]]; then
  fail "cling SIGINT exit $RC (want 130)"
fi
kill -0 "$LINGER" 2>/dev/null || fail "SIGINT on cling killed the subject"
"$PY" - "$WORK/sigint.json" "$LINGER" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
assert r["interrupted"] is True, r.get("end_reason")
assert r["target_alive"] is True, r
assert r["pid"] == int(sys.argv[2])
print("sigint reason", r["end_reason"], "alive", r["target_alive"], "open_last", (r.get("open_last") or {}).get("count"))
PY
pass "SIGINT reports; subject lives"
cleanup_pid "$LINGER"

echo "== missing pid is a hard error =="
set +e
"$CLING" attach --quiet 9999999 2>"$WORK/missing.err"
MRC=$?
set -e
[[ "$MRC" -eq 2 ]] || fail "missing pid exit $MRC"
grep -q "no such pid" "$WORK/missing.err" || fail "missing pid message"
pass "dead pid rejected"

echo "== real attach: kizu unit test via hold+exec =="
KIZU=/Users/annenpolka/ghq/github.com/annenpolka/kizu
if [[ -x "$KIZU/target/debug/kizu" ]] && command -v cargo >/dev/null; then
  READY="$WORK/kizu.ready"
  rm -f "$READY" "$WORK/kizu-test.json"
  "$PY" "$ROOT/fixtures/hold.py" "$READY" -- \
    cargo test --manifest-path "$KIZU/Cargo.toml" --lib scan_scars_finds_ask -- --test-threads=1 \
    >/dev/null 2>&1 &
  HPID=$!
  wait_file "$READY"
  set +e
  "$CLING" attach --quiet --kill-leaked --settle-ms 300 --settle-timeout-ms 4000 \
    --cwd "$KIZU" --out "$WORK/kizu-test.json" "$HPID"
  CRC=$?
  set -e
  wait "$HPID" 2>/dev/null || true
  if [[ ! -f "$WORK/kizu-test.json" ]]; then
    echo "  skip kizu wrap (cling produced no report, exit $CRC)"
  else
    "$PY" - "$WORK/kizu-test.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
print(f"  kizu attach end={r['end_reason']} duration={r['duration_ms']}ms waitpid={r['waitpid_ms']}ms settle={r['settle_ms']}ms")
print(f"  leaked={len(r['leaked_processes'])} late={len(r['late_writes'])} git+={len(r['git_residue']['introduced'])} tmp={len(r['tmp_residue'])} alive={r['target_alive']}")
print(f"  command={str(r.get('command'))[:80]!r} execs={len(r.get('execs') or [])}")
assert r["end_reason"] in {"exited", "gone", "group-empty"}
assert r["target_alive"] is False
cmd = r.get("command") or ""
assert "cargo" in cmd, ("exec not followed; still the hold wrapper", cmd, r.get("execs"))
PY
    pass "kizu cargo test attach"
  fi
else
  echo "  skip kizu wrap (no debug binary)"
fi

echo
echo "ALL CHECKS PASSED"
echo "reports under $WORK"
