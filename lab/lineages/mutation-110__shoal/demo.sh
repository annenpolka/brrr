#!/usr/bin/env bash
# Exercise shoal: origin is signed remotes at mint + required witnesses.
# Live `git remote add` is not origin. A fetched SHA is not the project.
# A true file:// --depth 1 clone of the signed project still resolves.
# Does not re-run leftover-stub / extract-and-keep / pin-v0.5 batteries.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SHOAL="$ROOT/shoal"
chmod +x "$SHOAL"

if ! command -v python3 >/dev/null; then
  echo "demo.sh: python3 is required" >&2
  exit 1
fi
if ! command -v git >/dev/null; then
  echo "demo.sh: git is required" >&2
  exit 1
fi

fail() { echo "FAIL: $*" >&2; exit 1; }
pass() { echo "PASS: $*"; }

echo "== 0. selftest =="
"$SHOAL" selftest || fail "selftest"
"$SHOAL" --selftest >/dev/null || fail "--selftest flag"
pass "selftest"

TMP="$(mktemp -d "${TMPDIR:-/tmp}/shoal-demo.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

git_init() {
  local repo="$1"
  git -C "$repo" init -q -b main
}

git_commit() {
  local repo="$1"
  local msg="$2"
  git -C "$repo" \
    -c user.name=shoal -c user.email=shoal@example.com \
    commit -q -m "$msg"
}

REPO="$TMP/ugly"
mkdir -p "$REPO/src"
cat > "$REPO/src/calc.py" <<'PY'
"""tiny calculator."""

def add(a, b):
    return a + b

def helper_keep():
    return "stable helper"
PY
git_init "$REPO"
git -C "$REPO" add src
git_commit "$REPO" "v1: original layout"
git -C "$REPO" remote add origin git@github.com:keel-lab/ugly.git
V1="$(git -C "$REPO" rev-parse HEAD)"

mkdir -p "$REPO/src/math"
cat > "$REPO/src/math/ops.py" <<'PY'
"""tiny calculator, renamed and split."""

def add(a, b):
    return a + b

def helper_keep():
    return "stable helper"
PY
rm -f "$REPO/src/calc.py"
git -C "$REPO" add -A src
git_commit "$REPO" "v2: split calc"
V2="$(git -C "$REPO" rev-parse HEAD)"

echo "== fixture refs =="
echo "V1=$V1"
echo "V2=$V2"
echo "id=$("$SHOAL" id --repo "$REPO" --from "$V1" | head -1)"

echo "== 1. mint helper_keep at v1, resolve at v2 without path:line =="
HELPER="$("$SHOAL" mint --repo "$REPO" --from "$V1" src/calc.py:6)"
echo "token: $HELPER"
echo "$HELPER" | grep -q '^shoal1\.' || fail "mint did not emit shoal1. token: $HELPER"
"$SHOAL" show "$HELPER"
out="$("$SHOAL" resolve --repo "$REPO" --to "$V2" --porcelain "$HELPER")"
echo "$out"
echo "$out" | grep -q $'src/math/ops.py:' || fail "helper_keep did not land in ops.py: $out"
echo "$out" | grep -Eq $'^(moved|same|edited)\t' || fail "unexpected status: $out"
pass "signed shoal relocated helper_keep into src/math/ops.py"

echo "== 2. resolve refuses a locator =="
set +e
out="$("$SHOAL" resolve --repo "$REPO" --to "$V2" src/calc.py:6 2>"$TMP/loc.err")"
rc=$?
set -e
[[ "$rc" -eq 2 ]] || fail "locator resolve exited $rc (want 2)"
grep -qi 'locator\|path:line' "$TMP/loc.err" || fail "locator error: $(cat "$TMP/loc.err")"
pass "resolve refuses path:line"

echo "== 3. foreign repo fail-closes =="
UNREL="$TMP/unrel"
mkdir -p "$UNREL/pkg"
cat > "$UNREL/pkg/util.py" <<'PY'
def helper_keep():
    return "stable helper"
PY
git_init "$UNREL"
git -C "$UNREL" add pkg/util.py
git_commit "$UNREL" "unrelated helper"
git -C "$UNREL" remote add origin git@github.com:other/util.git
set +e
out="$("$SHOAL" resolve --repo "$UNREL" --to HEAD --porcelain "$HELPER" 2>"$TMP/unrel.err")"
rc=$?
set -e
echo "unrel rc=$rc stdout=$out"
cat "$TMP/unrel.err"
[[ "$rc" -eq 1 ]] || fail "foreign repo resolve exited $rc (want 1)"
echo "$out" | grep -q $'^moved\t' && fail "foreign repo silently landed: $out"
grep -qi 'different repository\|any-repo' "$TMP/unrel.err" \
  || fail "foreign repo error did not name origin: $(cat "$TMP/unrel.err")"
pass "foreign repo refused"

echo "== 4. git remote add extra is not origin =="
git -C "$UNREL" remote add extra git@github.com:keel-lab/ugly.git
id_extra="$("$SHOAL" id --repo "$UNREL" | head -1)"
echo "id after extra: $id_extra"
echo "$id_extra" | grep -q 'keel-lab/ugly' \
  && fail "extra remote leaked into shoal id: $id_extra"
echo "$id_extra" | grep -q 'other/util' || fail "origin remote vanished: $id_extra"
set +e
out="$("$SHOAL" resolve --repo "$UNREL" --to HEAD --porcelain "$HELPER" 2>"$TMP/extra.err")"
rc=$?
set -e
echo "extra rc=$rc stdout=$out"
cat "$TMP/extra.err"
[[ "$rc" -eq 1 ]] || fail "remote-add extra landed the pin (rc=$rc)"
echo "$out" | grep -q $'^moved\t' && fail "remote-add extra printed a move: $out"
pass "git remote add extra did not land the pin"

echo "== 5. shared graft (fetch witness SHA) fail-closes =="
set +e
git -C "$UNREL" fetch -q "$REPO" "$V1"
fetch_rc=$?
set -e
[[ "$fetch_rc" -eq 0 ]] || git -C "$UNREL" fetch -q "file://$REPO" "$V1"
git -C "$UNREL" cat-file -e "$V1" || fail "fetch did not plant V1"
set +e
out="$("$SHOAL" resolve --repo "$UNREL" --to HEAD --porcelain "$HELPER" 2>"$TMP/graft.err")"
rc=$?
set -e
echo "graft rc=$rc stdout=$out"
cat "$TMP/graft.err"
[[ "$rc" -eq 1 ]] || fail "fetched SHA occupancy landed the pin (rc=$rc)"
echo "$out" | grep -q $'^moved\t' && fail "shared graft printed a move: $out"
pass "fetched SHA is not the project"

echo "== 6. set-url origin to victim, no lineage, still refuse =="
git -C "$UNREL" remote set-url origin https://github.com/keel-lab/ugly.git
id_set="$("$SHOAL" id --repo "$UNREL" | head -1)"
echo "id after set-url: $id_set"
set +e
out="$("$SHOAL" resolve --repo "$UNREL" --to HEAD --porcelain "$HELPER" 2>"$TMP/seturl.err")"
rc=$?
set -e
echo "set-url rc=$rc stdout=$out"
cat "$TMP/seturl.err"
[[ "$rc" -eq 1 ]] || fail "set-url without lineage landed the pin (rc=$rc)"
pass "set-url without witness lineage refused"

echo "== 7. --any-repo still overrides a stranger =="
out="$("$SHOAL" resolve --repo "$UNREL" --to HEAD --any-repo --porcelain "$HELPER")"
echo "$out"
echo "$out" | grep -q 'pkg/util.py' || fail "--any-repo should opt into foreign resolve: $out"
pass "--any-repo still lands a stranger (explicit override)"

echo "== 8. file:// --depth 1 of the signed project still resolves =="
SHALLOW="$TMP/shallow"
git clone -q --depth 1 "file://$REPO" "$SHALLOW"
[[ "$(git -C "$SHALLOW" rev-parse --is-shallow-repository)" == "true" ]] \
  || fail "file:// --depth 1 was not shallow"
[[ -f "$SHALLOW/.git/shallow" ]] || fail "missing $SHALLOW/.git/shallow"
set +e
git -C "$SHALLOW" cat-file -e "$V1"
v1_in_shallow=$?
set -e
[[ "$v1_in_shallow" -ne 0 ]] || fail "shallow still has V1; this is not a graft"
FULL_ROOTS="$(git -C "$REPO" rev-list --max-parents=0 --all | tr '\n' ' ')"
SH_ROOTS="$(git -C "$SHALLOW" rev-list --max-parents=0 --all | tr '\n' ' ')"
echo "full id:    $("$SHOAL" id --repo "$REPO" --from "$V1" | head -1)"
echo "shallow id: $("$SHOAL" id --repo "$SHALLOW" | head -1)"
echo "shallow roots: $SH_ROOTS"
echo "full roots:    $FULL_ROOTS"
[[ "$SH_ROOTS" != "$FULL_ROOTS" ]] || fail "shallow roots still equal full roots"
"$SHOAL" id --repo "$SHALLOW" | grep -q 'github.com/keel-lab/ugly' \
  || fail "shallow id did not inherit origin remotes"
out="$("$SHOAL" resolve --repo "$SHALLOW" --to HEAD --porcelain "$HELPER")"
echo "$out"
echo "$out" | grep -q 'src/math/ops.py' || fail "file:// depth-1 of same project did not resolve: $out"
echo "$out" | grep -q $'^deleted\t' && fail "file:// depth-1 looked like deletion: $out"
pass "file:// depth-1 clone of the signed project resolves"

echo "== 9. remotes-less mint, then advance, then file:// depth-1 =="
BARE="$TMP/barefull"
mkdir -p "$BARE/src"
cat > "$BARE/src/calc.py" <<'PY'
def helper_keep():
    return "stable helper"
PY
git_init "$BARE"
git -C "$BARE" add src
git_commit "$BARE" "bare-v1"
BARE_V1="$(git -C "$BARE" rev-parse HEAD)"
BAREPIN="$("$SHOAL" mint --repo "$BARE" --from "$BARE_V1" src/calc.py:1)"
echo "bare token origin: $("$SHOAL" show "$BAREPIN" | grep origin)"
echo '# later' >> "$BARE/src/calc.py"
git -C "$BARE" add src
git_commit "$BARE" "bare-v2"
BARESH="$TMP/bareshallow"
git clone -q --depth 1 "file://$BARE" "$BARESH"
[[ "$(git -C "$BARESH" rev-parse --is-shallow-repository)" == "true" ]] \
  || fail "bare file:// clone was not shallow"
set +e
git -C "$BARESH" cat-file -e "$BARE_V1"
bare_v1=$?
set -e
[[ "$bare_v1" -ne 0 ]] || fail "bare shallow still has V1"
out="$("$SHOAL" resolve --repo "$BARESH" --to HEAD --porcelain "$BAREPIN")"
echo "$out"
echo "$out" | grep -q 'src/calc.py:1' || fail "remotes-less file:// shallow did not follow origin: $out"
pass "remotes-less mint + later file:// depth-1 still resolves (origin hop)"

echo "== 10. remotes-less token does not land on a stranger =="
set +e
out="$("$SHOAL" resolve --repo "$UNREL" --to HEAD --porcelain "$BAREPIN" 2>"$TMP/bare-unrel.err")"
rc=$?
set -e
[[ "$rc" -eq 1 ]] || fail "remotes-less token landed on stranger (rc=$rc)"
pass "remotes-less token still fail-closes on a stranger"

echo "== 11. orphan extra root is still the same project =="
ORPH="$TMP/orph"
git clone -q "$REPO" "$ORPH"
ORPH_MAIN="$(git -C "$ORPH" rev-parse --abbrev-ref HEAD)"
git -C "$ORPH" checkout --orphan extra-hist
echo 'orphan only' > "$ORPH/orphan-only.txt"
git -C "$ORPH" add orphan-only.txt
git_commit "$ORPH" "orphan root"
# stay on the orphan; resolve --to the original V2
echo "orph roots: $(git -C "$ORPH" rev-list --max-parents=0 --all | tr '\n' ' ')"
out="$("$SHOAL" resolve --repo "$ORPH" --to "$V2" --porcelain "$HELPER")"
echo "$out"
echo "$out" | grep -q 'src/math/ops.py' || fail "orphan extra root made the repo foreign: $out"
pass "orphan extra root still the same shoal (--to original)"

echo "== 12. missing origin / gitless dest fail-closes =="
GITLESS="$TMP/gitless-pkg"
mkdir -p "$GITLESS"
cp "$UNREL/pkg/util.py" "$GITLESS/util.py"
set +e
out="$("$SHOAL" resolve --to-dir "$GITLESS" --porcelain "$HELPER" 2>"$TMP/gitless.err")"
rc=$?
set -e
[[ "$rc" -eq 1 ]] || fail "gitless --to-dir exited $rc (want 1)"
FROMDIR="$TMP/fromdir"
mkdir -p "$FROMDIR"
printf 'def helper_keep():\n    return "stable helper"\n' > "$FROMDIR/calc.py"
NAKED="$("$SHOAL" mint --from-dir "$FROMDIR" calc.py:1)"
set +e
out="$("$SHOAL" resolve --repo "$REPO" --to HEAD --porcelain "$NAKED" 2>"$TMP/naked.err")"
rc=$?
set -e
[[ "$rc" -eq 1 ]] || fail "from-dir token (no signed remotes) landed (rc=$rc)"
pass "missing origin fail-closes unless --any-repo"

echo "== 13. truncated tokens fail closed =="
HALF="${HELPER:0:24}"
set +e
out="$("$SHOAL" resolve --repo "$REPO" --to "$V2" --porcelain "$HALF" 2>"$TMP/half.err")"
rc=$?
set -e
[[ "$rc" -ne 0 ]] || fail "truncated token resolve exited 0"
echo "$out" | grep -Eq $'^(unresolved|moved|deleted|shifted|same)\t' \
  && fail "truncated token printed a result row: $out"
grep -qi 'corrupt\|not a shoal' "$TMP/half.err" \
  || fail "truncated token stderr was not fail-closed: $(cat "$TMP/half.err")"
pass "truncated tokens fail closed"

echo "== 14. ssh vs https of the same signed remote still matches =="
HTTPS="$TMP/https-clone"
git clone -q --depth 1 "file://$REPO" "$HTTPS"
git -C "$HTTPS" remote set-url origin https://github.com/keel-lab/ugly.git
# file:// dest after set-url: origin is now network. Dest HEAD is V2, which
# is a stored witness (mint stored HEAD-at-mint as well as --from).
out="$("$SHOAL" resolve --repo "$HTTPS" --to HEAD --porcelain "$HELPER")"
echo "$out"
echo "$out" | grep -q 'src/math/ops.py' || fail "https origin of same project refused: $out"
pass "ssh/https of the same signed host/path still resolves"

# --- real repo dogfood (read-only) ---
KIZU="${KIZU:-/Users/annenpolka/ghq/github.com/annenpolka/kizu}"
if [[ -d "$KIZU/.git" || -f "$KIZU/.git" ]]; then
  echo "== 15. kizu app.rs split: mint at b4e6a5d, resolve HEAD =="
  SEEN="$("$SHOAL" mint --repo "$KIZU" --from b4e6a5d src/app.rs:529)"
  echo "seen pin length=${#SEEN}"
  echo "kizu id: $("$SHOAL" id --repo "$KIZU" --from b4e6a5d | head -1)"
  out="$("$SHOAL" resolve --repo "$KIZU" --to HEAD --porcelain "$SEEN")"
  echo "$out"
  echo "$out" | grep -q 'src/app/layout.rs:' || fail "kizu seen_hunk_fingerprint did not land in layout.rs: $out"
  pass "kizu: shoal(src/app.rs:529@b4e6a5d) → src/app/layout.rs"

  echo "== 16. kizu steal: copy layout.rs + fetch SHA + extra remote =="
  STEAL="$TMP/kizu-steal"
  mkdir -p "$STEAL/src/app"
  git_init "$STEAL"
  # copy the landing file only
  if [[ -f "$KIZU/src/app/layout.rs" ]]; then
    cp "$KIZU/src/app/layout.rs" "$STEAL/src/app/layout.rs"
  else
    fail "kizu layout.rs missing on disk"
  fi
  git -C "$STEAL" add src
  git_commit "$STEAL" "stolen layout"
  git -C "$STEAL" remote add origin git@github.com:other/util.git
  git -C "$STEAL" remote add extra git@github.com:annenpolka/kizu.git
  KIZU_HEAD="$(git -C "$KIZU" rev-parse HEAD)"
  set +e
  git -C "$STEAL" fetch -q "$KIZU" "$KIZU_HEAD"
  steal_fetch=$?
  set -e
  [[ "$steal_fetch" -eq 0 ]] || git -C "$STEAL" fetch -q "file://$KIZU" "$KIZU_HEAD"
  git -C "$STEAL" cat-file -e "$KIZU_HEAD" || fail "steal fixture did not plant kizu HEAD"
  steal_id="$("$SHOAL" id --repo "$STEAL" | head -1)"
  echo "steal id: $steal_id"
  echo "$steal_id" | grep -q 'annenpolka/kizu' \
    && fail "kizu extra remote leaked into steal id: $steal_id"
  set +e
  out="$("$SHOAL" resolve --repo "$STEAL" --to HEAD --porcelain "$SEEN" 2>"$TMP/steal.err")"
  rc=$?
  set -e
  echo "steal rc=$rc stdout=$out"
  cat "$TMP/steal.err"
  [[ "$rc" -eq 1 ]] || fail "kizu steal (copy + fetch + extra remote) landed (rc=$rc)"
  echo "$out" | grep -q 'layout.rs' && fail "kizu steal printed a landing: $out"
  pass "kizu steal (copied file + fetched SHA + extra remote) refused"
else
  echo "SKIP kizu dogfood (repo not present at $KIZU)"
fi

echo "== 17. 3-hop file:// of mint-at-V1 still resolves (hop cap is not a project) =="
# Mint while HEAD is V1 so dest V2 is not a stored witness. Each hop is shallow.
HOP0="$TMP/hop0"
mkdir -p "$HOP0/src"
cat > "$HOP0/src/calc.py" <<'PY'
def helper_keep():
    return "stable helper"
PY
git_init "$HOP0"
git -C "$HOP0" add src
git_commit "$HOP0" "hop-v1"
git -C "$HOP0" remote add origin git@github.com:keel-lab/ugly.git
HOP_V1="$(git -C "$HOP0" rev-parse HEAD)"
HOPPIN="$("$SHOAL" mint --repo "$HOP0" --from "$HOP_V1" src/calc.py:1)"
echo '# later' >> "$HOP0/src/calc.py"
git -C "$HOP0" add src
git_commit "$HOP0" "hop-v2"
H1="$TMP/hop1"
H2="$TMP/hop2"
H3="$TMP/hop3"
git clone -q --depth 1 "file://$HOP0" "$H1"
git clone -q --depth 1 "file://$H1" "$H2"
git clone -q --depth 1 "file://$H2" "$H3"
echo "h3 id: $("$SHOAL" id --repo "$H3" | head -1)"
set +e
git -C "$H3" cat-file -e "$HOP_V1"
h3_v1=$?
set -e
[[ "$h3_v1" -ne 0 ]] || fail "3-hop dest still has V1"
out="$("$SHOAL" resolve --repo "$H3" --to HEAD --porcelain "$HOPPIN")"
echo "$out"
echo "$out" | grep -q 'src/calc.py:1' || fail "3-hop file:// of signed project refused: $out"
pass "3-hop file:// of mint-at-V1 still resolves"

echo "== 18. www.github.com / ssh.github.com of the signed path =="
ALIAS="$TMP/alias"
git clone -q --depth 1 "file://$REPO" "$ALIAS"
git -C "$ALIAS" remote set-url origin https://www.github.com/keel-lab/ugly.git
echo "www id: $("$SHOAL" id --repo "$ALIAS" | head -1)"
"$SHOAL" id --repo "$ALIAS" | grep -q 'github.com/keel-lab/ugly' \
  || fail "www.github.com did not fold to github.com"
out="$("$SHOAL" resolve --repo "$ALIAS" --to HEAD --porcelain "$HELPER")"
echo "$out"
echo "$out" | grep -q 'src/math/ops.py' || fail "www.github.com of signed path refused: $out"
git -C "$ALIAS" remote set-url origin ssh://git@ssh.github.com/keel-lab/ugly.git
out="$("$SHOAL" resolve --repo "$ALIAS" --to HEAD --porcelain "$HELPER")"
echo "$out"
echo "$out" | grep -q 'src/math/ops.py' || fail "ssh.github.com of signed path refused: $out"
git -C "$ALIAS" remote set-url origin https://gitlab.com/keel-lab/ugly.git
set +e
out="$("$SHOAL" resolve --repo "$ALIAS" --to HEAD --porcelain "$HELPER" 2>"$TMP/gitlab.err")"
rc=$?
set -e
[[ "$rc" -eq 1 ]] || fail "gitlab same-path dest landed (rc=$rc)"
pass "github host aliases fold; gitlab same-path does not"

echo
echo "All demo checks passed."
exit 0
