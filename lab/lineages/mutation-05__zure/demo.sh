#!/usr/bin/env bash
# Exercise zure: self-test, synthetic dirty trees, ugly names, real repos.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
ZURE="$ROOT/zure"
export GIT_AUTHOR_NAME=zure
export GIT_AUTHOR_EMAIL=zure@example.com
export GIT_COMMITTER_NAME=zure
export GIT_COMMITTER_EMAIL=zure@example.com

if [ ! -x "$ZURE" ]; then
  echo "zure is not executable at $ZURE" >&2
  exit 2
fi

tmp="$(mktemp -d "${TMPDIR:-/tmp}/zure-demo.XXXXXX")"
cleanup() { rm -rf "$tmp"; }
trap cleanup EXIT

pass=0
fail=0

ok() {
  pass=$((pass + 1))
  echo "  ok  $*"
}

die() {
  fail=$((fail + 1))
  echo "FAIL $*" >&2
  exit 1
}

section() {
  echo
  echo "== $* =="
}

run_zure() {
  set +e
  out="$("$ZURE" --color never "$@" 2>&1)"
  rc=$?
  set -e
}

# Here-string so `set -o pipefail` + `grep -q` cannot SIGPIPE on large reports.
has() { grep -Eq "$1" <<<"$out"; }

expect_rc() {
  local want=$1
  shift
  run_zure "$@"
  if [ "$rc" -ne "$want" ]; then
    printf '%s\n' "$out"
    die "expected exit $want got $rc  ($(printf '%q ' "$ZURE" "$@"))"
  fi
}

init_repo() {
  local dir=$1
  mkdir -p "$dir"
  git -C "$dir" init -q
  git -C "$dir" checkout -q -b main
  git -C "$dir" config user.email zure@example.com
  git -C "$dir" config user.name zure
}

commit() {
  git -C "$1" add -A
  git -C "$1" commit -q -m "$2"
}

copy_dirty() {
  local src=$1
  local dst=$2
  git clone -q --local -- "$src" "$dst"
  rsync -a --delete \
    --exclude .git \
    --exclude target \
    --exclude node_modules \
    --exclude .build \
    --exclude dist \
    --exclude coverage \
    --exclude .next \
    --exclude .venv \
    "$src/" "$dst/"
}

section "self-test"
expect_rc 0 --self-test
has "self-test: ok" || die "self-test banner"
ok "self-test"

section "break-use: recent commit added a callsite, worktree changes the def"
repo="$tmp/break"
init_repo "$repo"
mkdir -p "$repo/src"
cat > "$repo/src/parse.rs" <<'EOF'
pub fn parse_config(s: &str) -> Config {
    Config::from(s)
}
EOF
cat > "$repo/src/cli.rs" <<'EOF'
fn main() {}
EOF
commit "$repo" "base"
cat > "$repo/src/cli.rs" <<'EOF'
fn main() {
    let cfg = parse_config(raw);
    println!("{cfg:?}");
}
EOF
commit "$repo" "history: new parse_config callsite"
# Uncommitted signature change — git commit would hide the callsite.
cat > "$repo/src/parse.rs" <<'EOF'
pub fn parse_config(s: &str, timeout: u64) -> Config {
    Config::from_timeout(s, timeout)
}
EOF
expect_rc 1 -C "$repo" --horizon 8
has "parse_config" || die "missing parse_config: $out"
has "break-use" || die "missing break-use: $out"
has "hidden" || die "missing hidden: $out"
has "worktree" || die "missing worktree label: $out"
ok "break-use hidden on parse_config"

expect_rc 1 -C "$repo" -o json --horizon 8
has '"ident": "parse_config"' || die "json ident: $out"
has '"kind": "break-use"' || die "json kind: $out"
ok "json output"

expect_rc 1 -C "$repo" -o tsv --horizon 8
has "^break-use	parse_config" || die "tsv: $out"
ok "tsv output"

section "stale-use: committed signature change, untracked file still calls old arity"
repo="$tmp/stale"
init_repo "$repo"
mkdir -p "$repo/src"
cat > "$repo/src/parse.rs" <<'EOF'
pub fn parse_config(s: &str) -> Config {
    Config::from(s)
}
EOF
echo 'fn main() {}' > "$repo/src/cli.rs"
commit "$repo" "base"
cat > "$repo/src/parse.rs" <<'EOF'
pub fn parse_config(s: &str, timeout: u64) -> Config {
    Config::from_timeout(s, timeout)
}
EOF
commit "$repo" "history: extra timeout arg"
# Untracked — git status shows a new file, not the signature commit.
cat > "$repo/src/extra.rs" <<'EOF'
pub fn extra() {
    parse_config("hi");
}
EOF
expect_rc 1 -C "$repo" --horizon 8
has "stale-use" || die "stale-use kind: $out"
has "parse_config" || die "stale ident: $out"
has "extra.rs" || die "untracked path missing: $out"
ok "stale-use via untracked file"

section "unrelated dirty edit is silent"
repo="$tmp/clean"
init_repo "$repo"
mkdir -p "$repo/src"
echo 'pub fn alpha_unique(x: u32) -> u32 { x }' > "$repo/src/a.rs"
echo 'pub fn beta_unique(x: u32) -> u32 { x }' > "$repo/src/b.rs"
commit "$repo" "base"
echo 'pub fn alpha_unique(x: u32) -> u32 { x + 1 }' > "$repo/src/a.rs"
commit "$repo" "history: alpha"
echo 'pub fn beta_unique(x: u32) -> u32 { x + 2 }' > "$repo/src/b.rs"
expect_rc 0 -C "$repo" --horizon 8
has "no identifier conflicts" || die "clean case: $out"
ok "unrelated dirty edit exit 0"

section "working tree clean"
repo="$tmp/pristine"
init_repo "$repo"
echo 'a' > "$repo/f.txt"
commit "$repo" "one"
expect_rc 0 -C "$repo"
has "working tree clean" || die "clean banner: $out"
ok "clean worktree"

section "delete in history, untracked use"
repo="$tmp/del"
init_repo "$repo"
mkdir -p "$repo/src"
echo 'pub fn doomed_symbol() {}' > "$repo/src/lib.rs"
echo 'fn main() {}' > "$repo/src/main.rs"
commit "$repo" "base"
echo '// gone' > "$repo/src/lib.rs"
commit "$repo" "history deletes doomed_symbol"
cat > "$repo/src/extra.rs" <<'EOF'
fn extra() { doomed_symbol(); }
EOF
expect_rc 1 -C "$repo" --horizon 8
has "stale-use" || die "delete-use kind: $out"
has "doomed_symbol" || die "delete-use ident: $out"
ok "history-delete vs untracked use"

section "dup-def: committed helper, untracked twin"
repo="$tmp/dup"
init_repo "$repo"
echo 'fn placeholder() {}' > "$repo/keep.rs"
commit "$repo" "base"
echo 'pub fn shared_helper_zzz() {}' > "$repo/left.rs"
commit "$repo" "history adds helper"
echo 'pub fn shared_helper_zzz() {}' > "$repo/right.rs"
expect_rc 1 -C "$repo" --horizon 8
has "dup-def" || die "dup-def: $out"
has "shared_helper_zzz" || die "dup ident: $out"
ok "dup-def untracked twin"

section "ugly filenames, lockfile, generated, untracked"
repo="$tmp/ugly"
init_repo "$repo"
mkdir -p "$repo/src/a/b/c" "$repo/dist" "$repo/node_modules/pkg"
printf 'pub fn weird_ident_zzz(x: u32) -> u32 { x }\n' > "$repo/src/weird file-文.rs"
echo 'fn call() { weird_ident_zzz(1); }' > "$repo/src/a/b/c/deep.rs"
echo 'pub fn lock_only_ident() {}' > "$repo/Cargo.lock"
echo 'pub fn generated_bundle() {}' > "$repo/dist/bundle.min.js"
commit "$repo" "base"
printf 'pub fn weird_ident_zzz(x: u32, y: u32) -> u32 { x + y }\n' > "$repo/src/weird file-文.rs"
echo 'pub fn lock_only_ident(x: u32) {}' > "$repo/Cargo.lock"
echo 'pub fn generated_bundle(x: u32) {}' > "$repo/dist/bundle.min.js"
commit "$repo" "history: signature + noise"
echo 'fn call() { weird_ident_zzz(1, 2); }' > "$repo/src/a/b/c/deep.rs"
echo 'lock_only_ident(1);' > "$repo/src/lock_user.rs"
expect_rc 1 -C "$repo" --horizon 8
has "weird_ident_zzz" || die "ugly ident: $out"
has "weird file" || die "ugly path: $out"
if has "lock_only_ident"; then
  die "lockfile ident leaked: $out"
fi
if has "generated_bundle"; then
  die "min.js ident leaked: $out"
fi
ok "ugly path + ignore lock/generated"

section "quiet mode"
repo="$tmp/break"
expect_rc 1 -C "$repo" -q --horizon 8
[ -z "$out" ] || die "quiet should be empty, got: $out"
ok "quiet"

section "--staged ignores untracked"
repo="$tmp/staged"
init_repo "$repo"
mkdir -p "$repo/src"
echo 'pub fn parse_config(s: &str) -> Config { Config::from(s) }' > "$repo/src/parse.rs"
echo 'fn main() { let _ = parse_config(raw); }' > "$repo/src/cli.rs"
commit "$repo" "base"
# History: add another callsite (committed).
echo 'fn other() { let _ = parse_config(raw); }' > "$repo/src/other.rs"
commit "$repo" "history: extra callsite"
# Staged: signature change. Untracked: unrelated file that should not be required for --staged.
cat > "$repo/src/parse.rs" <<'EOF'
pub fn parse_config(s: &str, timeout: u64) -> Config { Config::from_timeout(s, timeout) }
EOF
git -C "$repo" add src/parse.rs
echo 'fn leftover() {}' > "$repo/src/untracked.rs"
expect_rc 1 -C "$repo" --staged --horizon 8
has "break-use" || die "staged break-use: $out"
has "parse_config" || die "staged ident: $out"
if has "untracked.rs"; then
  die "untracked leaked into --staged: $out"
fi
ok "--staged break-use, untracked ignored"

section "--replay treats a linear commit as a former worktree"
repo="$tmp/replay"
init_repo "$repo"
mkdir -p "$repo/src"
echo 'pub fn parse_config(s: &str) -> Config { Config::from(s) }' > "$repo/src/parse.rs"
echo 'fn main() {}' > "$repo/src/cli.rs"
commit "$repo" "base"
echo 'fn main() { let _ = parse_config(raw); }' > "$repo/src/cli.rs"
commit "$repo" "add callsite"
echo 'pub fn parse_config(s: &str, timeout: u64) -> Config { Config::from_timeout(s, timeout) }' > "$repo/src/parse.rs"
commit "$repo" "change signature"
expect_rc 1 -C "$repo" --replay 5 --horizon 8
has "parse_config" || die "replay missed parse_config: $out"
has "break-use|stale-use" || die "replay kind: $out"
has "flagged" || die "replay summary: $out"
ok "replay flags the signature commit"

section "--diffs mode"
repo="$tmp/break"
git -C "$repo" diff HEAD~1 HEAD > "$tmp/hist.diff"
git -C "$repo" diff HEAD > "$tmp/work.diff"
expect_rc 1 --diffs "$tmp/hist.diff" "$tmp/work.diff"
has "parse_config" || die "--diffs: $out"
ok "--diffs"

# --- real repos (copy; never mutate the originals) ---

KIZU="/Users/annenpolka/ghq/github.com/annenpolka/kizu"
SITBONE="/Users/annenpolka/ghq/github.com/annenpolka/sitbone"
VOIDTRACE="/Users/annenpolka/ghq/github.com/annenpolka/voidtrace"
TENAOSHI="/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi"

section "dogfood kizu (commit a callsite, dirty the signature — no second branch)"
if [ ! -d "$KIZU/.git" ]; then
  die "kizu not found at $KIZU"
fi
git clone -q --local -- "$KIZU" "$tmp/kizu"
scan="$tmp/kizu/src/hook/scan.rs"
if ! grep -Fq 'pub fn scan_scars(paths: &[PathBuf])' "$scan"; then
  die "kizu scan_scars signature moved; update demo"
fi
# Committed history: new callsite.
cat >> "$tmp/kizu/src/paths.rs" <<'EOF'

#[allow(dead_code)]
fn zure_probe_scan_scars(paths: &[std::path::PathBuf]) {
    let _ = crate::hook::scan_scars(paths);
}
EOF
git -C "$tmp/kizu" add src/paths.rs
git -C "$tmp/kizu" -c user.email=zure@example.com -c user.name=zure commit -q -m "zure: new scan_scars callsite"
# Uncommitted: signature change.
perl -0pi -e 's/pub fn scan_scars\(paths: &\[PathBuf\]\) -> Vec<ScarHit> \{/pub fn scan_scars(paths: \&[PathBuf], timeout_ms: u64) -> Vec<ScarHit> {\n    let _ = timeout_ms;/' "$scan"
expect_rc 1 -C "$tmp/kizu" --horizon 12
has "scan_scars" || die "kizu missed scan_scars: $out"
has "break-use" || die "kizu kind: $out"
if has '^(stale-use|dup-def|break-use)[[:space:]]+(ScarHit|paths)[[:space:]]'; then
  die "kizu type/param noise: $out"
fi
ok "kizu scan_scars break-use against own last commit"

# Original kizu is clean; replay may flag refactors. Must not crash (exit 2).
# -q keeps the one-line summary without dumping hundreds of hits.
run_zure -C "$KIZU" -q --replay 12 --horizon 8
if [ "$rc" -eq 2 ]; then
  die "kizu replay crashed: $out"
fi
has "replayed" || die "kizu replay summary: $out"
ok "kizu --replay (read-only linear history)"

section "dogfood sitbone (commit a callsite, dirty saveCumulative)"
if [ ! -d "$SITBONE/.git" ]; then
  die "sitbone not found at $SITBONE"
fi
git clone -q --local -- "$SITBONE" "$tmp/sitbone"
store="$tmp/sitbone/Sources/SitboneData/JSONSessionStore.swift"
if ! grep -q 'public func saveCumulative(_ record: CumulativeRecord) async throws' "$store"; then
  die "sitbone saveCumulative signature moved; update demo"
fi
mkdir -p "$tmp/sitbone/Sources/SitboneData"
cat > "$tmp/sitbone/Sources/SitboneData/ZureProbe.swift" <<'EOF'
enum ZureProbe {
    static func ping(_ store: JSONSessionStore) async throws {
        try await store.saveCumulative(CumulativeRecord())
    }
}
EOF
git -C "$tmp/sitbone" add Sources/SitboneData/ZureProbe.swift
git -C "$tmp/sitbone" -c user.email=zure@example.com -c user.name=zure commit -q -m "zure: new saveCumulative callsite"
perl -pi -e 's/public func saveCumulative\(_ record: CumulativeRecord\) async throws/public func saveCumulative(_ record: CumulativeRecord, flush: Bool) async throws/' "$store"
expect_rc 1 -C "$tmp/sitbone" --horizon 12
has "saveCumulative" || die "sitbone missed saveCumulative: $out"
if has '^(break-use|stale-use|dup-def)[[:space:]]+JSONSessionStore[[:space:]]'; then
  die "enclosing class false positive: $out"
fi
ok "sitbone saveCumulative break-use (no class header noise)"

run_zure -C "$SITBONE" -q --replay 10 --horizon 8
if [ "$rc" -eq 2 ]; then
  die "sitbone replay crashed: $out"
fi
has "replayed" || die "sitbone replay summary: $out"
ok "sitbone --replay (read-only)"

section "dogfood voidtrace (copy dirty tree as-is + constructed break-use)"
if [ -d "$VOIDTRACE/.git" ]; then
  copy_dirty "$VOIDTRACE" "$tmp/voidtrace-dirty"
  run_zure -C "$tmp/voidtrace-dirty" --horizon 15
  if [ "$rc" -eq 2 ]; then
    die "voidtrace dirty crashed: $out"
  fi
  has "^zure:" || die "voidtrace dirty header: $out"
  ok "voidtrace real dirty worktree (exit $rc, $(grep -c 'zure(s)' <<<"$out" || true))"

  git clone -q --local -- "$VOIDTRACE" "$tmp/voidtrace"
  git -C "$tmp/voidtrace" checkout -q -- .
  git -C "$tmp/voidtrace" clean -qfd
  ws="$tmp/voidtrace/packages/kernel/src/world-state.ts"
  if ! grep -Fq 'export function createWorldState(entities: Iterable<WorldEntity> = []): WorldState' "$ws"; then
    die "voidtrace createWorldState signature moved; update demo"
  fi
  cat > "$tmp/voidtrace/packages/kernel/src/zure-probe.ts" <<'EOF'
import { createWorldState } from "./world-state.ts";

export function zureProbe() {
  return createWorldState([]);
}
EOF
  git -C "$tmp/voidtrace" add packages/kernel/src/zure-probe.ts
  git -C "$tmp/voidtrace" -c user.email=zure@example.com -c user.name=zure commit -q -m "zure: new createWorldState callsite"
  perl -pi -e 's/export function createWorldState\(entities: Iterable<WorldEntity> = \[\]\): WorldState \{/export function createWorldState(entities: Iterable<WorldEntity> = [], epochMs = 0): WorldState {\n  void epochMs;/' "$ws"
  expect_rc 1 -C "$tmp/voidtrace" --horizon 12
  has "createWorldState" || die "voidtrace missed createWorldState: $out"
  ok "voidtrace createWorldState break-use"

  run_zure -C "$VOIDTRACE" -q --replay 8 --horizon 8
  if [ "$rc" -eq 2 ]; then
    die "voidtrace replay crashed: $out"
  fi
  has "replayed" || die "voidtrace replay summary: $out"
  ok "voidtrace --replay (read-only)"
else
  echo "  skip voidtrace (missing)"
fi

section "dogfood tenaoshi (copy dirty tree as-is, including untracked)"
if [ -d "$TENAOSHI/.git" ]; then
  copy_dirty "$TENAOSHI" "$tmp/tenaoshi-dirty"
  run_zure -C "$tmp/tenaoshi-dirty" --horizon 12
  if [ "$rc" -eq 2 ]; then
    die "tenaoshi dirty crashed: $out"
  fi
  has "^zure:" || die "tenaoshi dirty header: $out"
  ok "tenaoshi real dirty worktree+untracked (exit $rc)"

  run_zure -C "$TENAOSHI" -q --replay 8 --horizon 8
  if [ "$rc" -eq 2 ]; then
    die "tenaoshi replay crashed: $out"
  fi
  has "replayed" || die "tenaoshi replay summary: $out"
  ok "tenaoshi --replay (read-only)"
else
  echo "  skip tenaoshi (missing)"
fi

echo
echo "ALL PASSED ($pass checks)"
exit 0
