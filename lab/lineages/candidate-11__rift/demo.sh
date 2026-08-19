#!/usr/bin/env bash
# Exercise rift end-to-end: self-test, synthetic git, ugly names, real repos.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
RIFT="$ROOT/rift"
export GIT_AUTHOR_NAME=rift
export GIT_AUTHOR_EMAIL=rift@example.com
export GIT_COMMITTER_NAME=rift
export GIT_COMMITTER_EMAIL=rift@example.com

if [ ! -x "$RIFT" ]; then
  echo "rift is not executable at $RIFT" >&2
  exit 2
fi

tmp="$(mktemp -d "${TMPDIR:-/tmp}/rift-demo.XXXXXX")"
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

run_rift() {
  # Capture stdout+stderr; do not abort on rift's exit 1.
  set +e
  out="$("$RIFT" --color never "$@" 2>&1)"
  rc=$?
  set -e
}

expect_rc() {
  local want=$1
  shift
  run_rift "$@"
  if [ "$rc" -ne "$want" ]; then
    printf '%s\n' "$out"
    die "expected exit $want got $rc  ($(printf '%q ' "$RIFT" "$@"))"
  fi
}

init_repo() {
  local dir=$1
  mkdir -p "$dir"
  git -C "$dir" init -q
  git -C "$dir" checkout -q -b main
  git -C "$dir" config user.email rift@example.com
  git -C "$dir" config user.name rift
}

commit() {
  git -C "$1" add -A
  git -C "$1" commit -q -m "$2"
}

section "self-test"
expect_rc 0 --self-test
echo "$out" | grep -q "self-test: ok" || die "self-test banner"
ok "self-test"

section "synthetic def-use (clean merge, crossed ident)"
repo="$tmp/syn"
init_repo "$repo"
mkdir -p "$repo/src"
cat > "$repo/src/parse.rs" <<'EOF'
pub fn parse_config(s: &str) -> Config {
    Config::from(s)
}
EOF
cat > "$repo/src/cli.rs" <<'EOF'
fn main() {
    let cfg = parse_config(raw);
    println!("{cfg:?}");
}
EOF
commit "$repo" "base"

git -C "$repo" checkout -q -b side-a
cat > "$repo/src/parse.rs" <<'EOF'
pub fn parse_config(s: &str, timeout: u64) -> Config {
    Config::from_timeout(s, timeout)
}
EOF
commit "$repo" "A: change parse_config signature"

git -C "$repo" checkout -q main
git -C "$repo" checkout -q -b side-b
cat > "$repo/src/cli.rs" <<'EOF'
fn main() {
    let cfg = parse_config(raw, None);
    println!("{cfg:?}");
}
EOF
commit "$repo" "B: change parse_config callsite"

expect_rc 1 -C "$repo" side-a side-b
echo "$out" | grep -q "parse_config" || die "missing parse_config in output: $out"
echo "$out" | grep -q "def-use" || die "missing def-use: $out"
echo "$out" | grep -q "hidden" || die "missing hidden: $out"
echo "$out" | grep -q "merge-tree: clean" || die "expected clean merge-tree: $out"
ok "def-use hidden conflict on parse_config"

expect_rc 1 -C "$repo" -o json side-a side-b
echo "$out" | grep -q '"ident": "parse_config"' || die "json ident: $out"
ok "json output"

expect_rc 1 -C "$repo" -o tsv side-a side-b
echo "$out" | grep -q "^def-use	parse_config" || die "tsv: $out"
ok "tsv output"

# Two-sided merge on a throwaway branch so side-a/side-b stay diverged.
git -C "$repo" checkout -q -b merged side-a
git -C "$repo" merge --no-ff --no-edit -m "merge sides" side-b
expect_rc 1 -C "$repo" --audit 5
echo "$out" | grep -q "parse_config" || die "audit missed parse_config: $out"
echo "$out" | grep -q "two-sided" || die "audit summary missing: $out"
ok "audit two-sided merge"

section "unrelated parallel edits are silent-clean"
repo="$tmp/clean"
init_repo "$repo"
mkdir -p "$repo/src"
echo 'pub fn alpha_unique(x: u32) -> u32 { x }' > "$repo/src/a.rs"
echo 'pub fn beta_unique(x: u32) -> u32 { x }' > "$repo/src/b.rs"
commit "$repo" "base"
git -C "$repo" checkout -q -b side-a
echo 'pub fn alpha_unique(x: u32) -> u32 { x + 1 }' > "$repo/src/a.rs"
commit "$repo" "A"
git -C "$repo" checkout -q main
git -C "$repo" checkout -q -b side-b
echo 'pub fn beta_unique(x: u32) -> u32 { x + 2 }' > "$repo/src/b.rs"
commit "$repo" "B"
expect_rc 0 -C "$repo" side-a side-b
echo "$out" | grep -q "no silent identifier conflicts" || die "clean case: $out"
ok "unrelated edits exit 0"

section "delete-use"
repo="$tmp/del"
init_repo "$repo"
mkdir -p "$repo/src"
echo 'pub fn doomed_symbol() {}' > "$repo/src/lib.rs"
echo 'fn main() {}' > "$repo/src/main.rs"
commit "$repo" "base"
git -C "$repo" checkout -q -b side-a
echo '// gone' > "$repo/src/lib.rs"
commit "$repo" "A deletes doomed_symbol"
git -C "$repo" checkout -q main
git -C "$repo" checkout -q -b side-b
echo 'fn main() { doomed_symbol(); }' > "$repo/src/main.rs"
commit "$repo" "B adds callsite"
expect_rc 1 -C "$repo" side-a side-b
echo "$out" | grep -q "delete-use" || die "delete-use kind: $out"
echo "$out" | grep -q "doomed_symbol" || die "delete-use ident: $out"
ok "delete-use"

section "ugly filenames, nested git-ignored generated, lockfile noise"
repo="$tmp/ugly"
init_repo "$repo"
mkdir -p "$repo/src/a/b/c" "$repo/dist" "$repo/node_modules/pkg"
printf 'pub fn weird_ident_zzz(x: u32) -> u32 { x }\n' > "$repo/src/weird file-文.rs"
echo 'fn call() { weird_ident_zzz(1); }' > "$repo/src/a/b/c/deep.rs"
echo 'pub fn lock_only_ident() {}' > "$repo/Cargo.lock"
echo 'pub fn generated_bundle() {}' > "$repo/dist/bundle.min.js"
echo 'pub fn vendored_ident() {}' > "$repo/node_modules/pkg/index.js"
commit "$repo" "base"
git -C "$repo" checkout -q -b side-a
printf 'pub fn weird_ident_zzz(x: u32, y: u32) -> u32 { x + y }\n' > "$repo/src/weird file-文.rs"
echo 'pub fn lock_only_ident(x: u32) {}' > "$repo/Cargo.lock"
echo 'pub fn generated_bundle(x: u32) {}' > "$repo/dist/bundle.min.js"
commit "$repo" "A"
git -C "$repo" checkout -q main
git -C "$repo" checkout -q -b side-b
echo 'fn call() { weird_ident_zzz(1, 2); }' > "$repo/src/a/b/c/deep.rs"
echo 'lock_only_ident(1);' > "$repo/src/lock_user.rs"
git -C "$repo" add "src/lock_user.rs"
commit "$repo" "B"
expect_rc 1 -C "$repo" side-a side-b
echo "$out" | grep -q "weird_ident_zzz" || die "ugly ident: $out"
echo "$out" | grep -q "weird file" || die "ugly path: $out"
if echo "$out" | grep -q "lock_only_ident"; then
  die "lockfile ident leaked: $out"
fi
if echo "$out" | grep -q "generated_bundle"; then
  die "min.js ident leaked: $out"
fi
ok "ugly path + ignore lock/generated"

section "one-sided history"
repo="$tmp/linear"
init_repo "$repo"
echo 'a' > "$repo/f.txt"
commit "$repo" "one"
echo 'b' > "$repo/f.txt"
commit "$repo" "two"
expect_rc 0 -C "$repo" HEAD~1 HEAD
echo "$out" | grep -q "one-sided" || die "one-sided banner: $out"
ok "one-sided ancestor pair"

section "dup-def across files, merge-tree still clean"
repo="$tmp/dup"
init_repo "$repo"
echo 'fn placeholder() {}' > "$repo/keep.rs"
commit "$repo" "base"
git -C "$repo" checkout -q -b side-a
echo 'pub fn shared_helper_zzz() {}' > "$repo/left.rs"
commit "$repo" "A"
git -C "$repo" checkout -q main
git -C "$repo" checkout -q -b side-b
echo 'pub fn shared_helper_zzz() {}' > "$repo/right.rs"
commit "$repo" "B"
expect_rc 1 -C "$repo" side-a side-b
echo "$out" | grep -q "dup-def" || die "dup-def: $out"
echo "$out" | grep -q "shared_helper_zzz" || die "dup ident: $out"
ok "dup-def"

section "quiet mode"
repo="$tmp/syn"
expect_rc 1 -C "$repo" -q side-a side-b
[ -z "$out" ] || die "quiet should be empty, got: $out"
ok "quiet"

section "--diffs mode"
base=$(git -C "$tmp/syn" merge-base side-a side-b)
git -C "$tmp/syn" diff "$base" side-a > "$tmp/a.diff"
git -C "$tmp/syn" diff "$base" side-b > "$tmp/b.diff"
expect_rc 1 --diffs "$tmp/a.diff" "$tmp/b.diff"
echo "$out" | grep -q "parse_config" || die "--diffs: $out"
ok "--diffs"

# --- real repos (copy; never mutate the originals) ---

KIZU="/Users/annenpolka/ghq/github.com/annenpolka/kizu"
SITBONE="/Users/annenpolka/ghq/github.com/annenpolka/sitbone"
VOIDTRACE="/Users/annenpolka/ghq/github.com/annenpolka/voidtrace"

section "dogfood kizu (clone + parallel signature/callsite branches)"
if [ ! -d "$KIZU/.git" ]; then
  die "kizu not found at $KIZU"
fi
git clone -q --local -- "$KIZU" "$tmp/kizu"
# Branch A: change scan_scars signature.
git -C "$tmp/kizu" checkout -q -B rift-a main
scan="$tmp/kizu/src/hook/scan.rs"
if ! grep -Fq 'pub fn scan_scars(paths: &[PathBuf])' "$scan"; then
  die "kizu scan_scars signature moved; update demo"
fi
perl -0pi -e 's/pub fn scan_scars\(paths: &\[PathBuf\]\) -> Vec<ScarHit> \{/pub fn scan_scars(paths: \&[PathBuf], timeout_ms: u64) -> Vec<ScarHit> {\n    let _ = timeout_ms;/' "$scan"
git -C "$tmp/kizu" add src/hook/scan.rs
git -C "$tmp/kizu" commit -q -m "A: add timeout_ms to scan_scars"
# Branch B from main: add a new callsite in a file that did not change on A.
git -C "$tmp/kizu" checkout -q -B rift-b main
cat >> "$tmp/kizu/src/paths.rs" <<'EOF'

#[allow(dead_code)]
fn rift_probe_scan_scars(paths: &[std::path::PathBuf]) {
    let _ = crate::hook::scan_scars(paths);
}
EOF
git -C "$tmp/kizu" add src/paths.rs
git -C "$tmp/kizu" commit -q -m "B: new scan_scars callsite in paths.rs"
expect_rc 1 -C "$tmp/kizu" rift-a rift-b
echo "$out" | grep -q "scan_scars" || die "kizu dogfood missed scan_scars: $out"
echo "$out" | grep -q "def-use\|delete-use\|dup-def" || die "kizu dogfood kind: $out"
ok "kizu scan_scars def-use"
# --audit on GitHub-style merges should not crash
expect_rc 0 -C "$tmp/kizu" --audit 20
echo "$out" | grep -q "one-sided" || die "kizu audit summary: $out"
ok "kizu --audit (GitHub one-sided merges)"

section "dogfood sitbone (clone + saveCumulative signature vs new call)"
if [ ! -d "$SITBONE/.git" ]; then
  die "sitbone not found at $SITBONE"
fi
git clone -q --local -- "$SITBONE" "$tmp/sitbone"
git -C "$tmp/sitbone" checkout -q -B rift-a main
store="$tmp/sitbone/Sources/SitboneData/JSONSessionStore.swift"
if ! grep -q 'public func saveCumulative(_ record: CumulativeRecord) async throws' "$store"; then
  die "sitbone saveCumulative signature moved; update demo"
fi
perl -pi -e 's/public func saveCumulative\(_ record: CumulativeRecord\) async throws/public func saveCumulative(_ record: CumulativeRecord, flush: Bool) async throws/' "$store"
git -C "$tmp/sitbone" add Sources/SitboneData/JSONSessionStore.swift
git -C "$tmp/sitbone" commit -q -m "A: extra flush param on saveCumulative"
git -C "$tmp/sitbone" checkout -q -B rift-b main
# New file so merge-tree stays clean.
mkdir -p "$tmp/sitbone/Sources/SitboneData"
cat > "$tmp/sitbone/Sources/SitboneData/RiftProbe.swift" <<'EOF'
enum RiftProbe {
    static func ping(_ store: JSONSessionStore) async throws {
        try await store.saveCumulative(CumulativeRecord())
    }
}
EOF
git -C "$tmp/sitbone" add Sources/SitboneData/RiftProbe.swift
git -C "$tmp/sitbone" commit -q -m "B: new saveCumulative callsite"
expect_rc 1 -C "$tmp/sitbone" rift-a rift-b
echo "$out" | grep -q "saveCumulative" || die "sitbone dogfood missed saveCumulative: $out"
if echo "$out" | grep -Eq '^(def-use|dup-def|delete-use)[[:space:]]+JSONSessionStore[[:space:]]'; then
  die "enclosing class false positive: $out"
fi
ok "sitbone saveCumulative def-use (no class header noise)"

section "dogfood voidtrace --audit / one-sided HEAD~1"
if [ -d "$VOIDTRACE/.git" ]; then
  expect_rc 0 -C "$VOIDTRACE" --audit 10
  ok "voidtrace --audit (read-only)"
  expect_rc 0 -C "$VOIDTRACE" HEAD~1 HEAD
  ok "voidtrace one-sided HEAD~1 HEAD"

  git clone -q --local -- "$VOIDTRACE" "$tmp/voidtrace"
  git -C "$tmp/voidtrace" checkout -q -B rift-a main
  ws="$tmp/voidtrace/packages/kernel/src/world-state.ts"
  if ! grep -Fq 'export function createWorldState(entities: Iterable<WorldEntity> = []): WorldState' "$ws"; then
    die "voidtrace createWorldState signature moved; update demo"
  fi
  perl -pi -e 's/export function createWorldState\(entities: Iterable<WorldEntity> = \[\]\): WorldState \{/export function createWorldState(entities: Iterable<WorldEntity> = [], epochMs = 0): WorldState {\n  void epochMs;/' "$ws"
  git -C "$tmp/voidtrace" add packages/kernel/src/world-state.ts
  git -C "$tmp/voidtrace" commit -q -m "A: extra epochMs on createWorldState"
  git -C "$tmp/voidtrace" checkout -q -B rift-b main
  cat > "$tmp/voidtrace/packages/kernel/src/rift-probe.ts" <<'EOF'
import { createWorldState } from "./world-state.ts";

export function riftProbe() {
  return createWorldState([]);
}
EOF
  git -C "$tmp/voidtrace" add packages/kernel/src/rift-probe.ts
  git -C "$tmp/voidtrace" commit -q -m "B: new createWorldState callsite"
  expect_rc 1 -C "$tmp/voidtrace" rift-a rift-b
  echo "$out" | grep -q "createWorldState" || die "voidtrace dogfood missed createWorldState: $out"
  ok "voidtrace createWorldState def-use"
else
  echo "  skip voidtrace (missing)"
fi

echo
echo "ALL PASSED ($pass checks)"
exit 0
