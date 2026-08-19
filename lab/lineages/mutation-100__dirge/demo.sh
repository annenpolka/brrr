#!/usr/bin/env bash
# demo.sh — clustered overlay-deaths of an unapplied patch. Must exit 0.
set -euo pipefail
cd "$(dirname "$0")"
chmod +x ./dirge

PASS=0
FAIL=0
assert() {
  local name="$1"
  shift
  if "$@"; then
    PASS=$((PASS + 1))
    echo "  ok  $name"
  else
    FAIL=$((FAIL + 1))
    echo "  FAIL $name" >&2
  fi
}

echo "== selftest =="
./dirge --selftest
assert "selftest exit 0" true

echo
echo "== 1. island delete: one obituary for if/elif; births silent; no write =="
out="$(./dirge --base :wt --diff fixtures/island.diff --limit 6)"
echo "$out"
assert "names flow_score" grep -q "flow_score" <<<"$out"
assert "does not name unique_mod births" bash -c '! grep -q unique_mod <<<"$out"'
assert "one clustered covering row (dirge=1)" grep -Eq 'dirge=1  ' <<<"$out"
assert "arms>=2 (not N sibling covering rows)" grep -Eq 'arms=[2-9]' <<<"$out"
assert "born count differs from dirge" grep -Eq 'dirge=[1-9][0-9]*  deaths=[1-9].*born=[1-9]' <<<"$out"
assert "mod0.py never written" test ! -e fixtures/mod0.py
assert "river.py still on disk" test -f fixtures/river.py

echo
echo "== 2. sequential if + elif + given-else are one obituary =="
out="$(./dirge --base :wt --diff fixtures/seq.diff --json)"
echo "$out" | python3 -c 'import json,sys; d=json.load(sys.stdin); print("dirge",len(d["dirge"]),"arms",d["dirge"][0]["arm_n"] if d["dirge"] else None)'
python3 - <<'PY'
import json, subprocess, sys
out = subprocess.check_output(["./dirge","--base",":wt","--diff","fixtures/seq.diff","--json"], text=True)
d = json.loads(out)
assert len(d["dirge"]) == 1, d["dirge"]
assert d["dirge"][0]["arm_n"] >= 3, d["dirge"][0]
print("seq clustered arms=%s" % d["dirge"][0]["arm_n"])
PY
assert "seq.swift never deleted on disk" test -f fixtures/seq.swift

echo
echo "== 3. two independent if-chains stay two obituaries =="
python3 - <<'PY'
import json, subprocess
out = subprocess.check_output(["./dirge","--base",":wt","--diff","fixtures/twochain.diff","--json"], text=True)
d = json.loads(out)
assert len(d["dirge"]) == 2, d["dirge"]
assert all(o["arm_n"] == 2 for o in d["dirge"]), d["dirge"]
print("twochain dirge=%s arms=%s" % (len(d["dirge"]), [o["arm_n"] for o in d["dirge"]]))
PY
assert "twochain.py still on disk" test -f fixtures/twochain.py

echo
echo "== 4. newif is a birth: default overlay-deaths empty =="
set +e
./dirge --base :wt --diff fixtures/newif.diff --json > /tmp/dirge-newif.json
rc=$?
set -e
echo "newif rc=$rc (want 1)"
python3 - /tmp/dirge-newif.json <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
assert d["dirge"] == [], d["dirge"]
assert d["born"] > 0, d
print("newif covering empty, born=%s deaths=%s" % (d["born"], d["deaths"]))
assert d["deaths"] == 0, d
PY
assert "newif silent covering" test "$rc" -eq 1

echo
echo "== 5. rename is a move: silent; parse_moved.py never written =="
set +e
./dirge --base :wt --diff fixtures/move.diff --json > /tmp/dirge-move.json
rc=$?
set -e
python3 - /tmp/dirge-move.json <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
assert d["dirge"] == [], d
assert d["moves"] > 0, d
print("move covering empty, moves=%s" % d["moves"])
PY
assert "move rc=1" test "$rc" -eq 1
assert "parse_moved.py absent" test ! -e fixtures/parse_moved.py

echo
echo "== 6. no diff is usage (2); directory operand refused =="
set +e
./dirge >/tmp/dirge-usage.err 2>&1
rc=$?
set -e
echo "usage rc=$rc (want 2)"
assert "usage rc=2" test "$rc" -eq 2
set +e
./dirge --diff fixtures/island.diff fixtures >/tmp/dirge-walk.err 2>&1
rc=$?
set -e
echo "walk-refuse rc=$rc (want 2)"
assert "walk refuse rc=2" test "$rc" -eq 2

echo
echo "== 7. HEAD-only stacks are not overlay-deaths =="
python3 - <<'PY'
from pathlib import Path
from dirgepkg.overlay import overlay_diff
from dirgepkg.stacks import dirge_from_images, stacks_in_source
root = Path(".")
keep = stacks_in_source((root / "fixtures/keep.py").read_text(), "fixtures/keep.py")
river = stacks_in_source((root / "fixtures/river.py").read_text(), "fixtures/river.py")
head = set(keep) | set(river)
rep = dirge_from_images(overlay_diff((root / "fixtures/island.diff").read_text(), root, base=":wt"))
deaths = {s.key for o in rep.covering for s in o.members}
assert deaths, deaths
assert deaths != head
assert any("keep" in " ".join(p for _k,p in k) for k in keep)
assert not any("keep" in s.label for o in rep.covering for s in o.members)
assert len(rep.covering) == 1
assert rep.covering[0].arm_n >= 2
print("HEAD-only has keep_flag; overlay-deaths of island.diff do not")
print("obituaries=%s arms=%s born=%s head_stacks=%s" % (len(rep.covering), rep.covering[0].arm_n, rep.born_n, len(head)))
PY
assert "HEAD-only ≠ overlay-deaths" true

KIZU="${KIZU:-/Users/annenpolka/ghq/github.com/annenpolka/kizu}"
SITBONE="${SITBONE:-/Users/annenpolka/ghq/github.com/annenpolka/sitbone}"

if [[ -d "$KIZU/.git" ]]; then
  echo
  echo "== dogfood: kizu git.rs→parse.rs is a move (silent) =="
  before="$(git -C "$KIZU" status --porcelain)"
  set +e
  git -C "$KIZU" diff 3b3e0a9^ 3b3e0a9 | ./dirge -C "$KIZU" --base 3b3e0a9^ --limit 6 > /tmp/dirge-kizu.txt
  rc=$?
  set -e
  cat /tmp/dirge-kizu.txt
  after="$(git -C "$KIZU" status --porcelain)"
  assert "kizu silent rc=1" test "$rc" -eq 1
  assert "kizu covering empty" grep -q "empty — nothing died" /tmp/dirge-kizu.txt
  assert "kizu worktree clean" test "$before" = "$after"
fi

if [[ -d "$SITBONE/.git" ]]; then
  echo
  echo "== dogfood: sitbone island 14b1d6e vs HEAD =="
  before="$(git -C "$SITBONE" status --porcelain)"
  git -C "$SITBONE" diff 14b1d6e HEAD | ./dirge -C "$SITBONE" --base 14b1d6e --limit 6 > /tmp/dirge-sit.txt
  cat /tmp/dirge-sit.txt
  after="$(git -C "$SITBONE" status --porcelain)"
  assert "sitbone names FocusRiverView" grep -q FocusRiverView /tmp/dirge-sit.txt
  assert "sitbone names flowScore death" grep -q flowScore /tmp/dirge-sit.txt
  assert "sitbone true-arm headline" grep -q "if app.flowScore > 0.2" /tmp/dirge-sit.txt
  assert "sitbone pin is wane L121" grep -q "FocusRiverView.swift:121" /tmp/dirge-sit.txt
  assert "sitbone headline is not sequential given" bash -c '! grep -q "A   exclusive_a  given ¬(app.flowScore" /tmp/dirge-sit.txt'
  # clustered: not 4 sibling covering rows. dirge < 4, one flowScore obituary has arms>=3
  assert "sitbone dirge≠4 sibling rows" bash -c '! grep -Eq "^dirge=4  " /tmp/dirge-sit.txt'
  python3 - <<'PY'
from pathlib import Path
text = Path("/tmp/dirge-sit.txt").read_text()
# top-level exclusive_a rows (not the · arm list)
rows = [ln for ln in text.splitlines() if ln.startswith("  A   exclusive_a")]
assert len(rows) < 4, rows
print("sitbone top-level obituaries=%s" % len(rows))
PY
  assert "sitbone does not list camera births as covering" bash -c '! grep -q exclusive_b /tmp/dirge-sit.txt'
  assert "sitbone born ≠ dirge" bash -c 'grep -E "dirge=[1-9].*born=[1-9]" /tmp/dirge-sit.txt | grep -vq "born=0"'
  if git -C "$SITBONE" cat-file -e HEAD:Sources/SitboneUI/FocusRiverView.swift 2>/dev/null; then
    echo "unexpected: FocusRiverView lives on HEAD"
  else
    echo "HEAD has no FocusRiverView.swift; overlay-deaths still named it from --base 14b1d6e"
  fi
  assert "sitbone worktree clean" test "$before" = "$after"
fi

echo
if [[ "$FAIL" -ne 0 ]]; then
  echo "demo FAIL=$FAIL PASS=$PASS" >&2
  exit 1
fi
echo "demo ok  PASS=$PASS"
exit 0
