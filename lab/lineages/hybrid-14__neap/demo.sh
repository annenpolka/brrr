#!/usr/bin/env bash
# demo.sh — overlay-deaths of an unapplied patch. Must exit 0.
set -euo pipefail
cd "$(dirname "$0")"
chmod +x ./neap

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
./neap --selftest
assert "selftest exit 0" true

echo
echo "== 1. island delete: exclusive-A flow_score; births silent; no write =="
out="$(./neap --base :wt --diff fixtures/island.diff --limit 6)"
echo "$out"
assert "names flow_score" grep -q "flow_score" <<<"$out"
assert "does not name unique_mod births" bash -c '! grep -q unique_mod <<<"$out"'
assert "born count differs from neap" grep -Eq 'neap=[1-9][0-9]*  deaths=[1-9].*born=[1-9]' <<<"$out"
assert "mod0.py never written" test ! -e fixtures/mod0.py
assert "river.py still on disk" test -f fixtures/river.py

echo
echo "== 2. newif is a birth: default overlay-deaths empty =="
set +e
./neap --base :wt --diff fixtures/newif.diff --json > /tmp/neap-newif.json
rc=$?
set -e
echo "newif rc=$rc (want 1)"
python3 - /tmp/neap-newif.json <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
assert d["neap"] == [], d["neap"]
assert d["born"] > 0, d
print("newif covering empty, born=%s deaths=%s" % (d["born"], d["deaths"]))
assert d["deaths"] == 0, d
PY
assert "newif silent covering" test "$rc" -eq 1

echo
echo "== 3. rename is a move: silent; parse_moved.py never written =="
set +e
./neap --base :wt --diff fixtures/move.diff --json > /tmp/neap-move.json
rc=$?
set -e
python3 - /tmp/neap-move.json <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
assert d["neap"] == [], d
assert d["moves"] > 0, d
print("move covering empty, moves=%s" % d["moves"])
PY
assert "move rc=1" test "$rc" -eq 1
assert "parse_moved.py absent" test ! -e fixtures/parse_moved.py

echo
echo "== 4. no diff is usage (2); directory operand refused =="
set +e
./neap >/tmp/neap-usage.err 2>&1
rc=$?
set -e
echo "usage rc=$rc (want 2)"
assert "usage rc=2" test "$rc" -eq 2
set +e
./neap --diff fixtures/island.diff fixtures >/tmp/neap-walk.err 2>&1
rc=$?
set -e
echo "walk-refuse rc=$rc (want 2)"
assert "walk refuse rc=2" test "$rc" -eq 2

echo
echo "== 5. HEAD-only stacks are not overlay-deaths =="
python3 - <<'PY'
from pathlib import Path
from neappkg.overlay import overlay_diff
from neappkg.stacks import neap_from_images, stacks_in_source
root = Path(".")
keep = stacks_in_source((root / "fixtures/keep.py").read_text(), "fixtures/keep.py")
river = stacks_in_source((root / "fixtures/river.py").read_text(), "fixtures/river.py")
head = set(keep) | set(river)
rep = neap_from_images(overlay_diff((root / "fixtures/island.diff").read_text(), root, base=":wt"))
deaths = {s.key for s in rep.covering}
assert deaths, deaths
assert deaths != head
assert any("keep" in " ".join(p for _k,p in k) for k in keep)
assert not any("keep" in s.label for s in rep.covering)
print("HEAD-only has keep_flag; overlay-deaths of island.diff do not")
print("deaths=%s born=%s head_stacks=%s" % (len(deaths), rep.born_n, len(head)))
PY
assert "HEAD-only ≠ overlay-deaths" true

KIZU="${KIZU:-/Users/annenpolka/ghq/github.com/annenpolka/kizu}"
SITBONE="${SITBONE:-/Users/annenpolka/ghq/github.com/annenpolka/sitbone}"

if [[ -d "$KIZU/.git" ]]; then
  echo
  echo "== dogfood: kizu git.rs→parse.rs is a move (silent) =="
  before="$(git -C "$KIZU" status --porcelain)"
  set +e
  git -C "$KIZU" diff 3b3e0a9^ 3b3e0a9 | ./neap -C "$KIZU" --base 3b3e0a9^ --limit 6 > /tmp/neap-kizu.txt
  rc=$?
  set -e
  cat /tmp/neap-kizu.txt
  after="$(git -C "$KIZU" status --porcelain)"
  assert "kizu silent rc=1" test "$rc" -eq 1
  assert "kizu covering empty" grep -q "empty — nothing died" /tmp/neap-kizu.txt
  assert "kizu worktree clean" test "$before" = "$after"
fi

if [[ -d "$SITBONE/.git" ]]; then
  echo
  echo "== dogfood: sitbone island 14b1d6e vs HEAD =="
  before="$(git -C "$SITBONE" status --porcelain)"
  git -C "$SITBONE" diff 14b1d6e HEAD | ./neap -C "$SITBONE" --base 14b1d6e --limit 6 > /tmp/neap-sit.txt
  cat /tmp/neap-sit.txt
  after="$(git -C "$SITBONE" status --porcelain)"
  assert "sitbone names FocusRiverView" grep -q FocusRiverView /tmp/neap-sit.txt
  assert "sitbone names flowScore death" grep -q flowScore /tmp/neap-sit.txt
  assert "sitbone does not spend leftover on if-let window" bash -c '! grep -q "if let w = window" /tmp/neap-sit.txt'
  assert "sitbone does not list camera births as covering" bash -c '! grep -q exclusive_b /tmp/neap-sit.txt'
  assert "sitbone born ≠ neap" bash -c 'grep -E "neap=[1-9].*born=[1-9]" /tmp/neap-sit.txt | grep -vq "born=0"'
  # HEAD-only of current sitbone cannot name FocusRiverView — the file is gone.
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
