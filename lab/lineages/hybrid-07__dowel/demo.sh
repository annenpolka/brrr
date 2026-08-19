#!/usr/bin/env bash
# Exercise dowel: mint a contract token, resolve onto a later tree.
# The object is (template fingerprint + bound holes + locus), not pin | invert.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
DOWEL="$ROOT/dowel"
chmod +x "$DOWEL"

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
"$DOWEL" --selftest || fail "selftest"
pass "selftest"

TMP="$(mktemp -d "${TMPDIR:-/tmp}/dowel-demo.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

REPO="$TMP/ugly"
mkdir -p "$REPO/src" "$REPO/notes"

cat > "$REPO/src/user.py" <<'PY'
"""user messages."""

def report(uid):
    raise Error(f"user {uid} not found")

def reach(host, port, n):
    raise Error(f"cannot reach {host}:{port} after {n} retries")

def spawn(cmd):
    raise Error(f"failed to spawn `{cmd}`")
PY

cat > "$REPO/src/events.ts" <<'TS'
export function enqueue(id: string, processed: number, time: number) {
  throw new RangeError(`Cannot enqueue event before processed time ${processed}: ${time}`);
}
TS

cat > "$REPO/notes/file with spaces.py" <<'PY'
def weird(name):
    raise Error(f"cannot open strange file: {name}")
PY

python3 - "$REPO" <<'PY'
from pathlib import Path
import sys
repo = Path(sys.argv[1])
p = repo / "src" / ("caf" + "\u00e9" + ".py")
p.write_text('def cafe_fn(uid):\n    raise Error(f"café user {uid} gone")\n', encoding="utf-8")
PY

git -C "$REPO" init -q
git -C "$REPO" add src notes
git -C "$REPO" -c user.name=dowel -c user.email=dowel@example.com commit -q -m 'v1: original templates'
V1="$(git -C "$REPO" rev-parse HEAD)"

# v2: extract+rename user template, drop port, leftover stub, basename bait
mkdir -p "$REPO/src/user" "$REPO/src/legacy"
cat > "$REPO/src/user.py" <<'PY'
"""re-export leftover."""

def report(uid):
    from src.user.messages import report as impl
    return impl(uid)
PY

cat > "$REPO/src/user/messages.py" <<'PY'
"""extracted body."""

def report(user_id):
    raise Error(f"user {user_id} not found")

def reach(host, n):
    raise Error(f"cannot reach {host} after {n} retries")

def spawn(cmd):
    raise Error(f"failed to spawn `{cmd}`")
PY

cat > "$REPO/src/legacy/user.py" <<'PY'
def report(uid):
    raise Error(f"user {uid} not found")
PY

git -C "$REPO" add -A src notes
git -C "$REPO" -c user.name=dowel -c user.email=dowel@example.com commit -q -m 'v2: extract, rename uid, drop port'
V2="$(git -C "$REPO" rev-parse HEAD)"

echo "== fixture refs =="
echo "V1=$V1"
echo "V2=$V2"

echo "== 1. mint user {uid}, resolve: extracted body + renamed hole =="
USER="$("$DOWEL" mint --repo "$REPO" --from "$V1" src/user.py:4 'user 42 not found')"
echo "token: $USER"
echo "$USER" | grep -q '^dowel1\.' || fail "mint did not emit dowel1. token: $USER"
out="$("$DOWEL" resolve --repo "$REPO" --to "$V2" --porcelain "$USER")"
echo "$out"
echo "$out" | grep -q $'^renamed\t' || fail "expected renamed: $out"
echo "$out" | grep -q 'src/user/messages.py:' || fail "did not seat extracted body: $out"
echo "$out" | grep -q 'uid→user_id' || fail "did not report uid→user_id: $out"
dest="$(printf '%s\n' "$out" | awk -F'\t' '{print $4}')"
echo "$dest" | grep -q 'legacy/user.py' && fail "basename bait stole the seat: $out"
echo "$dest" | grep -q '^src/user.py:' && fail "leftover stub stole the seat: $out"
echo "$out" | grep -q 'basename bait' || fail "note did not name basename bait: $out"
echo "$out" | grep -q 'leftover stub' || fail "note did not name leftover stub: $out"
pass "renamed uid→user_id at extracted body; leftover and bait lost"

echo "== 2. resolve refuses a locator (the flipped assumption) =="
if "$DOWEL" resolve --repo "$REPO" --to "$V2" src/user.py:4 >/tmp/dowel-resolve-loc.out 2>/tmp/dowel-resolve-loc.err; then
  fail "resolve accepted path:line"
fi
grep -q 'locator' /tmp/dowel-resolve-loc.err || fail "resolve error did not name locator: $(cat /tmp/dowel-resolve-loc.err)"
pass "resolve refuses path:line; the dowel is the object"

echo "== 3. same holes after a move (spawn) =="
SPAWN="$("$DOWEL" mint --repo "$REPO" --from "$V1" src/user.py:10 'failed to spawn `git apply --reverse`')"
out="$("$DOWEL" resolve --repo "$REPO" --to "$V2" --porcelain "$SPAWN")"
echo "$out"
echo "$out" | grep -q $'^shifted\t' || fail "spawn should be shifted: $out"
echo "$out" | grep -q 'src/user/messages.py:' || fail "spawn did not follow extract: $out"
echo "$out" | grep -q $'\tcmd\t' || fail "spawn holes should still be cmd: $out"
pass "spawn template moved; {cmd} still binds"

echo "== 4. dropped hole is unbound, not a silent rebind =="
REACH="$("$DOWEL" mint --repo "$REPO" --from "$V1" src/user.py:7 'cannot reach db.internal:5432 after 3 retries')"
out="$("$DOWEL" resolve --repo "$REPO" --to "$V2" --porcelain "$REACH")"
echo "$out"
echo "$out" | grep -q $'^unbound\t' || fail "dropped port should be unbound: $out"
echo "$out" | grep -q 'port' || fail "unbound did not name port: $out"
pass "dropped {port} → unbound"

echo "== 5. identity: mint at v2, resolve at v2 is seated =="
ADD="$("$DOWEL" mint --repo "$REPO" --from "$V2" src/user/messages.py:4 'user 9 not found')"
out="$("$DOWEL" resolve --repo "$REPO" --to "$V2" --porcelain "$ADD")"
echo "$out"
echo "$out" | grep -q $'^seated\t' || fail "identity should be seated: $out"
pass "same-snapshot identity is seated"

echo "== 6. mint is canonical =="
AGAIN="$("$DOWEL" mint --repo "$REPO" --from "$V1" src/user.py:4 'user 42 not found')"
[[ "$USER" == "$AGAIN" ]] || fail "mint of the same contract was not stable"
pass "canonical mint"

echo "== 7. dowel show decodes the contract =="
shown="$("$DOWEL" show "$USER")"
echo "$shown"
echo "$shown" | grep -q 'src/user.py:' || fail "show lost minted path: $shown"
echo "$shown" | grep -q '{uid}' || fail "show lost bound hole: $shown"
echo "$shown" | grep -q 'user 42 not found' || fail "show lost instance: $shown"
echo "$shown" | grep -q 'origin:' || fail "show lost origin: $shown"
pass "show (template + bound holes + origin)"

echo "== 8. gitless from-dir / to-dir =="
mkdir -p "$TMP/from/src" "$TMP/to/pkg"
echo 'raise Error(f"unique token {qzx} landed")' > "$TMP/from/src/old.py"
echo 'raise Error(f"unique token {qzx} landed")' > "$TMP/to/pkg/new.py"
DIRPIN="$("$DOWEL" mint --from-dir "$TMP/from" src/old.py:1 'unique token ZEBRA99 landed')"
out="$("$DOWEL" resolve --to-dir "$TMP/to" --porcelain "$DIRPIN")"
echo "$out"
echo "$out" | grep -q 'pkg/new.py:' || fail "dir-to-dir missed: $out"
echo "$out" | grep -Eq $'^(shifted|seated)\t' || fail "dir-to-dir status: $out"
pass "from-dir mint / to-dir resolve (no git)"

echo "== 9. unicode path =="
UNI="$("$DOWEL" mint --repo "$REPO" --from "$V1" 'src/café.py:2' 'café user 7 gone')"
out="$("$DOWEL" resolve --repo "$REPO" --to "$V2" --porcelain "$UNI")"
echo "$out"
echo "$out" | grep -q 'src/caf' || fail "unicode path lost: $out"
echo "$out" | grep -q $'^seated\t' || fail "unicode should stay seated: $out"
pass "unicode filename"

echo "== 10. spaced filename =="
SPC="$("$DOWEL" mint --repo "$REPO" --from "$V1" 'notes/file with spaces.py:2' 'cannot open strange file: /tmp/a b.txt')"
out="$("$DOWEL" resolve --repo "$REPO" --to "$V2" --porcelain "$SPC")"
echo "$out"
echo "$out" | grep -q 'notes/file with spaces.py' || fail "spaced filename lost: $out"
pass "spaced filename"

echo "== 11. json shape =="
out="$("$DOWEL" resolve --repo "$REPO" --to "$V2" --json "$USER")"
echo "$out"
python3 -c 'import json,sys; o=json.loads(sys.argv[1]); assert o["status"]=="renamed"; assert o["to"]["path"].endswith("messages.py"); assert o["dowel"].startswith("dowel1."); assert o["rename"][0]["from"]=="uid"' "$out"
pass "json output"

echo "== 12. bare dowel1. token implies resolve =="
out="$("$DOWEL" --porcelain --repo "$REPO" --to "$V2" "$SPAWN")"
echo "$out"
echo "$out" | grep -q 'messages.py' || fail "flags-before-token did not resolve: $out"
pass "bare dowel1. token implies resolve"

echo "== 13. two-hole js template =="
JS="$("$DOWEL" mint --repo "$REPO" --from "$V1" src/events.ts:2 'Cannot enqueue event before processed time 1200: 800')"
out="$("$DOWEL" resolve --repo "$REPO" --to "$V2" --porcelain "$JS")"
echo "$out"
echo "$out" | grep -q $'^seated\t' || fail "js template should stay: $out"
echo "$out" | grep -q 'processed' || fail "js holes lost: $out"
pass "js two-hole seated"

echo "== 14. missing --to ref is an error, not gone =="
set +e
out="$("$DOWEL" resolve --repo "$REPO" --to this-ref-does-not-exist --porcelain "$USER" 2>"$TMP/bad-ref.err")"
rc=$?
set -e
echo "rc=$rc stdout=$out"
cat "$TMP/bad-ref.err"
[[ "$rc" -ne 0 ]] || fail "missing --to ref exited 0"
echo "$out" | grep -q $'^gone\t' && fail "missing --to looked like gone: $out"
grep -qi 'unknown ref' "$TMP/bad-ref.err" || fail "missing --to error was not about the ref: $(cat "$TMP/bad-ref.err")"
pass "missing --to is an error"

echo "== 15. truncated tokens fail closed =="
HALF="${USER:0:24}"
set +e
out="$("$DOWEL" resolve --repo "$REPO" --to "$V2" --porcelain "$HALF" 2>"$TMP/half.err")"
rc=$?
set -e
[[ "$rc" -ne 0 ]] || fail "truncated token resolve exited 0"
echo "$out" | grep -Eq $'^(gone|shifted|seated|renamed|unbound)\t' && fail "truncated token printed a result row: $out"
grep -qi 'corrupt' "$TMP/half.err" || fail "truncated token stderr was not fail-closed: $(cat "$TMP/half.err")"
pass "truncated token fail closed"

echo "== 16. rustc locator is refused at mint =="
set +e
out="$("$DOWEL" mint --repo "$REPO" --from "$V1" src/user.py:4 -e '   --> src/git/revert.rs:46:18' 2>"$TMP/loc.err")"
rc=$?
set -e
[[ "$rc" -ne 0 ]] || fail "locator mint exited 0"
grep -qi 'locator' "$TMP/loc.err" || fail "locator mint error: $(cat "$TMP/loc.err")"
pass "rustc locator refused at mint"

echo "== 17. foreign repo refused =="
UNREL="$TMP/unrel"
mkdir -p "$UNREL/pkg"
echo 'raise Error(f"user {uid} not found")' > "$UNREL/pkg/util.py"
git -C "$UNREL" init -q
git -C "$UNREL" add pkg/util.py
git -C "$UNREL" -c user.name=dowel -c user.email=dowel@example.com commit -q -m 'unrelated'
set +e
out="$("$DOWEL" resolve --repo "$UNREL" --to HEAD --porcelain "$USER" 2>"$TMP/unrel.err")"
rc=$?
set -e
[[ "$rc" -ne 0 ]] || fail "foreign repo resolve exited 0"
echo "$out" | grep -q $'^renamed\t' && fail "foreign repo silently landed: $out"
grep -qi 'different repository' "$TMP/unrel.err" || fail "foreign repo error: $(cat "$TMP/unrel.err")"
out="$("$DOWEL" resolve --repo "$UNREL" --to HEAD --any-repo --porcelain "$USER")"
echo "$out"
echo "$out" | grep -q 'pkg/util.py' || fail "--any-repo should opt into foreign resolve: $out"
pass "foreign repo refused; --any-repo overrides"

echo "== 18. not pin | invert: pin does not know the hole rename =="
PIN="${PIN:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01afa-49e6-7b70-a5b5-bd46235631d2/pin}"
INVERT="${INVERT:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01ad1-c9bb-74f2-a42f-2d465380e59f/invert}"
if [[ -x "$PIN" ]]; then
  PP="$("$PIN" mint --repo "$REPO" --from "$V1" src/user.py:4)"
  pout="$("$PIN" resolve --repo "$REPO" --to "$V2" --porcelain "$PP")"
  echo "pin: $pout"
  echo "$pout" | grep -q 'user_id' && fail "pin unexpectedly named the hole rename: $pout"
  pdest="$(printf '%s\n' "$pout" | awk -F'\t' '{print $4}')"
  echo "$pdest" | grep -q 'legacy/user.py' || echo "NOTE pin dest (expected bait): $pdest"
  pass "pin relocates the line and is silent on uid→user_id (often the basename bait)"
else
  echo "SKIP pin contrast (no pin binary)"
fi
if [[ -x "$INVERT" ]]; then
  iout="$(
    printf '%s\n' 'src/user/messages.py:4:    raise Error(f"user {user_id} not found")' \
      | "$INVERT" --templates - 'user 42 not found' || true
  )"
  echo "invert: $iout"
  echo "$iout" | grep -q '{user_id} = 42' || fail "invert should bind dest name: $iout"
  echo "$iout" | grep -q 'uid→' && fail "invert unexpectedly knew the rename: $iout"
  pass "invert binds {user_id}=42 and does not know it was {uid}"
else
  echo "SKIP invert contrast (no invert binary)"
fi

echo "== 19. --instance rebinds a new paste against dest =="
out="$("$DOWEL" resolve --repo "$REPO" --to "$V2" --instance 'user 99 not found' --json "$USER")"
echo "$out"
python3 -c 'import json,sys; o=json.loads(sys.argv[1]); assert o["status"]=="renamed", o; vals=[b["value"] for b in o["bindings"]]; assert "99" in vals, o; assert o["rename"][0]["from"]=="uid"' "$out"
pass "rebind new instance still reports the rename"

# --- real repo dogfood (read-only) ---
KIZU="${KIZU:-/Users/annenpolka/ghq/github.com/annenpolka/kizu}"
if [[ -d "$KIZU/.git" || -f "$KIZU/.git" ]]; then
  echo "== 20. kizu {rest} template: mint HEAD, resolve HEAD seated =="
  REST="$("$DOWEL" mint --repo "$KIZU" --from HEAD src/git/parse.rs:171 \
    'unparseable `diff --git` header: a/foo b/foo')"
  out="$("$DOWEL" resolve --repo "$KIZU" --to HEAD --porcelain "$REST")"
  echo "$out"
  echo "$out" | grep -q $'^seated\t' || fail "kizu rest should be seated: $out"
  echo "$out" | grep -q 'rest' || fail "kizu rest hole missing: $out"
  pass "kizu: unparseable header {rest} seated at parse.rs:171"

  echo "== 21. kizu git-diff {} hole =="
  DIFF="$("$DOWEL" mint --repo "$KIZU" --from HEAD src/git/diff.rs:34 \
    'git diff single file failed: fatal: not a git repository')"
  out="$("$DOWEL" resolve --repo "$KIZU" --to HEAD --porcelain "$DIFF")"
  echo "$out"
  echo "$out" | grep -q $'^seated\t' || fail "kizu diff should be seated: $out"
  pass "kizu: git diff single file failed: {1} seated"
else
  echo "SKIP kizu dogfood (repo not present at $KIZU)"
fi

SIT="${SIT:-/Users/annenpolka/ghq/github.com/annenpolka/sitbone}"
if [[ -d "$SIT/.git" || -f "$SIT/.git" ]]; then
  echo "== 22. sitbone 7-hole Logger line =="
  SEVEN="$("$DOWEL" mint --repo "$SIT" --from HEAD \
    Sources/SitboneCore/SitboneCore.swift:554 \
    'transition focused → idle reason=timeout idle=12s deserted=0 driftRecovered=0 awayRecovered=0')"
  out="$("$DOWEL" resolve --repo "$SIT" --to HEAD --porcelain "$SEVEN")"
  echo "$out"
  echo "$out" | grep -q $'^seated\t' || fail "sitbone 7-hole should be seated: $out"
  shown="$("$DOWEL" show "$SEVEN")"
  echo "$shown"
  echo "$shown" | grep -q 'oldPhase.rawValue' || fail "sitbone lost oldPhase: $shown"
  echo "$shown" | grep -q 'idle' || fail "sitbone lost idle: $shown"
  echo "$shown" | grep -q 'awayRecovered' || fail "sitbone lost awayRecovered: $shown"
  pass "sitbone 7-hole contract seated"

  echo "== 23. sitbone camera nested quotes =="
  CAM="$("$DOWEL" mint --repo "$SIT" --from HEAD \
    Sources/SitboneCore/SitboneCore.swift:361 \
    'camera presence enabled')"
  out="$("$DOWEL" resolve --repo "$SIT" --to HEAD --porcelain "$CAM")"
  echo "$out"
  echo "$out" | grep -q $'^seated\t' || fail "camera should be seated: $out"
  shown="$("$DOWEL" show "$CAM")"
  echo "$shown"
  echo "$shown" | grep -q 'self.isCameraEnabled' || fail "camera hole name lost: $shown"
  echo "$shown" | grep -q 'enabled' || fail "camera binding lost: $shown"
  pass "sitbone camera nested quotes bind"
else
  echo "SKIP sitbone dogfood (repo not present at $SIT)"
fi

VOID="${VOID:-/Users/annenpolka/ghq/github.com/annenpolka/voidtrace}"
if [[ -d "$VOID/.git" || -f "$VOID/.git" ]]; then
  echo "== 24. voidtrace two-hole enqueue =="
  VQ="$("$DOWEL" mint --repo "$VOID" --from HEAD \
    packages/kernel/src/event-queue.ts:65 \
    'Cannot enqueue event before processed time 1200: 800')"
  out="$("$DOWEL" resolve --repo "$VOID" --to HEAD --porcelain "$VQ")"
  echo "$out"
  echo "$out" | grep -q $'^seated\t' || fail "voidtrace enqueue should be seated: $out"
  echo "$out" | grep -q 'event-queue.ts' || fail "voidtrace jumped file: $out"
  pass "voidtrace enqueue two-hole seated"
else
  echo "SKIP voidtrace dogfood (repo not present at $VOID)"
fi

TENA="${TENA:-/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi}"
if [[ -d "$TENA/.git" || -f "$TENA/.git" ]]; then
  echo "== 25. tenaoshi Japanese HTTP holes =="
  JP="$("$DOWEL" mint --repo "$TENA" --from HEAD \
    Engine/Sources/TenaoshiEngine/Adapters/AnthropicMessagesClient.swift:86 \
    'Anthropic APIがHTTP 429を返した: rate limited')"
  out="$("$DOWEL" resolve --repo "$TENA" --to HEAD --porcelain "$JP")"
  echo "$out"
  echo "$out" | grep -q $'^seated\t' || fail "tenaoshi Japanese should be seated: $out"
  shown="$("$DOWEL" show "$JP")"
  echo "$shown"
  echo "$shown" | grep -q 'http.statusCode' || fail "tenaoshi lost statusCode: $shown"
  echo "$shown" | grep -q '429' || fail "tenaoshi lost 429: $shown"
  echo "$shown" | grep -q 'rate limited' || fail "tenaoshi lost detail: $shown"
  pass "tenaoshi Japanese HTTP contract seated"
else
  echo "SKIP tenaoshi dogfood (repo not present at $TENA)"
fi

if [[ -d "$KIZU/.git" || -f "$KIZU/.git" ]]; then
  echo "== 26. kizu historical split: git.rs:609@3b3e0a9^ → parse.rs:171 =="
  RESTOLD="$("$DOWEL" mint --repo "$KIZU" --from '3b3e0a9^' src/git.rs:609 \
    'unparseable `diff --git` header: a/foo b/foo')"
  out="$("$DOWEL" resolve --repo "$KIZU" --to HEAD --porcelain "$RESTOLD")"
  echo "$out"
  echo "$out" | grep -q $'^shifted\t' || fail "kizu split should be shifted: $out"
  echo "$out" | grep -q 'src/git/parse.rs:171' || fail "kizu split missed parse.rs: $out"
  echo "$out" | grep -q $'\trest\t' || fail "kizu split lost {rest}: $out"
  pass "kizu: pin would move the line; dowel keeps {rest} across the split"
fi

if [[ -d "$SIT/.git" || -f "$SIT/.git" ]]; then
  echo "== 27. truncated sitbone 7-hole remainder names the next hole =="
  TR="$("$DOWEL" mint --repo "$SIT" --from HEAD \
    Sources/SitboneCore/SitboneCore.swift:554 \
    'transition focused → idle reason=timeout idle=12s')"
  shown="$("$DOWEL" show "$TR")"
  echo "$shown"
  echo "$shown" | grep -q 'truncated:' || fail "truncated mint lost flag: $shown"
  echo "$shown" | grep -q '{counters.deserted.value}' || fail "remainder swallowed next hole: $shown"
  echo "$shown" | grep -q '{idle}' || fail "truncated mint lost idle: $shown"
  echo "$shown" | grep -q 'awayRecovered' && echo "$shown" | grep -q 'bound:.*awayRecovered' && fail "truncated mint should not contract awayRecovered: $shown"
  out="$("$DOWEL" resolve --repo "$SIT" --to HEAD --porcelain "$TR")"
  echo "$out"
  echo "$out" | grep -q $'^seated\t' || fail "truncated contract should still seat: $out"
  pass "truncated 7-hole remainder keeps {counters.deserted.value}; contract is 4 holes"
fi

echo
echo "All demo checks passed."
exit 0
