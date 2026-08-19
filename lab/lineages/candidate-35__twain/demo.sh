#!/usr/bin/env bash
# Exercise twain on fixtures and, when present, real dogfood trees.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
TWAIN="$ROOT/twain"
chmod +x "$TWAIN"

pass=0
fail=0

ok() {
  pass=$((pass + 1))
  echo "  PASS  $1"
}

bad() {
  fail=$((fail + 1))
  echo "  FAIL  $1"
  echo "        $2"
}

expect_status() {
  local name="$1"
  local want="$2"
  shift 2
  local out
  local code=0
  out="$("$TWAIN" --report-only --porcelain "$@" 2>&1)" || code=$?
  local got
  got="$(echo "$out" | awk '/^status /{print $2; exit}')"
  if [[ "$got" == "$want" ]]; then
    ok "$name"
  else
    bad "$name" "want status=$want got=$got code=$code out=$(echo "$out" | tr '\n' ' ')"
  fi
}

echo "== selftest =="
if "$TWAIN" --selftest; then
  ok "selftest"
else
  bad "selftest" "twain --selftest exited $?"
fi

echo "== fixture git repos =="
WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/twain-demo.XXXXXX")"
cleanup() { rm -rf "$WORKDIR"; }
trap cleanup EXIT

git_init() {
  local d="$1"
  mkdir -p "$d"
  git -C "$d" init -q
  git -C "$d" config user.email "twain@demo"
  git -C "$d" config user.name "twain"
}

# LOCKED: prod + oracle share bias
LOCKED="$WORKDIR/locked"
git_init "$LOCKED"
mkdir -p "$LOCKED/tests"
printf 'def add(a, b):\n    return a + b\n' > "$LOCKED/app.py"
printf 'def test_add():\n    assert add(1, 1) == 2\n' > "$LOCKED/tests/test_add.py"
git -C "$LOCKED" add -A && git -C "$LOCKED" commit -q -m base
printf 'def add(a, b):\n    return a + b + bias()\n' > "$LOCKED/app.py"
printf 'def test_add():\n    assert add(1, 1) == 2 + bias()\n' > "$LOCKED/tests/test_add.py"
git -C "$LOCKED" add -A && git -C "$LOCKED" commit -q -m 'wire bias'
expect_status "LOCKED vs HEAD" LOCKED -C "$LOCKED" HEAD
expect_status "LOCKED sandwich parent" PENDING -C "$LOCKED" HEAD --against HEAD^

# MUTE: production only
MUTE="$WORKDIR/mute"
git_init "$MUTE"
printf 'def add(a, b):\n    return a + b\n' > "$MUTE/app.py"
git -C "$MUTE" add -A && git -C "$MUTE" commit -q -m base
printf 'def add(a, b):\n    return a + b + 1\n' > "$MUTE/app.py"
git -C "$MUTE" add -A && git -C "$MUTE" commit -q -m 'bump'
expect_status "MUTE vs HEAD" MUTE -C "$MUTE" HEAD

# HOLLOW: tests only
HOLLOW="$WORKDIR/hollow"
git_init "$HOLLOW"
printf 'def add(a, b):\n    return a + b\n' > "$HOLLOW/app.py"
git -C "$HOLLOW" add -A && git -C "$HOLLOW" commit -q -m base
mkdir -p "$HOLLOW/tests"
printf 'def test_add():\n    assert add(1, 1) == 2\n' > "$HOLLOW/tests/test_add.py"
git -C "$HOLLOW" add -A && git -C "$HOLLOW" commit -q -m 'cover add'
expect_status "HOLLOW vs HEAD" HOLLOW -C "$HOLLOW" HEAD

# LOOSE: both halves, no shared tokens
LOOSE="$WORKDIR/loose"
git_init "$LOOSE"
mkdir -p "$LOOSE/tests"
printf 'def add(a, b):\n    return a + b\n' > "$LOOSE/app.py"
printf 'def test_ok():\n    assert True\n' > "$LOOSE/tests/test_add.py"
git -C "$LOOSE" add -A && git -C "$LOOSE" commit -q -m base
printf 'def add(a, b):\n    return a - b\n' > "$LOOSE/app.py"
printf 'def test_ok():\n    assert not False\n' > "$LOOSE/tests/test_add.py"
git -C "$LOOSE" add -A && git -C "$LOOSE" commit -q -m 'unrelated'
expect_status "LOOSE vs HEAD" LOOSE -C "$LOOSE" HEAD

# suffix cut in one hunk (cfg(test) at bottom) splits → LOCKED
CUT="$WORKDIR/cut"
git_init "$CUT"
mkdir -p "$CUT/src"
cat > "$CUT/src/lib.rs" <<'EOF'
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[cfg(test)]
mod tests {
    use super::*;
}
EOF
git -C "$CUT" add -A && git -C "$CUT" commit -q -m base
cat > "$CUT/src/lib.rs" <<'EOF'
pub fn add(a: i32, b: i32) -> i32 {
    a + b + bias()
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn bias_is_wired() {
        assert_eq!(add(1, 1), 2 + bias());
    }
}
EOF
git -C "$CUT" add -A && git -C "$CUT" commit -q -m cut
expect_status "suffix cut LOCKED" LOCKED -C "$CUT" HEAD

# SEAM: interleaved prod / oracle / prod in one hunk
SEAM="$WORKDIR/seam"
git_init "$SEAM"
mkdir -p "$SEAM/src"
cat > "$SEAM/src/lib.rs" <<'EOF'
pub fn add(a: i32, b: i32) -> i32 {
    a
}
#[cfg(test)]
mod tests {
    use super::*;
}
pub fn other() -> i32 {
    1
}
EOF
git -C "$SEAM" add -A && git -C "$SEAM" commit -q -m base
cat > "$SEAM/src/lib.rs" <<'EOF'
pub fn add(a: i32, b: i32) -> i32 {
    a + bias()
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn t() { assert_eq!(add(0, 0), bias()); }
}
pub fn other() -> i32 {
    2
}
EOF
git -C "$SEAM" add -A && git -C "$SEAM" commit -q -m seam
expect_status "interleaved SEAM" SEAM -C "$SEAM" HEAD

# docs-only
DOCS="$WORKDIR/docs"
git_init "$DOCS"
printf 'old\n' > "$DOCS/README.md"
git -C "$DOCS" add -A && git -C "$DOCS" commit -q -m base
printf 'new\n' > "$DOCS/README.md"
git -C "$DOCS" add -A && git -C "$DOCS" commit -q -m docs
expect_status "docs EMPTY" EMPTY -C "$DOCS" HEAD

echo "== emit oracle/prod =="
ORACLE_PATCH="$WORKDIR/oracle.patch"
PROD_PATCH="$WORKDIR/prod.patch"
"$TWAIN" --emit oracle -C "$LOCKED" HEAD > "$ORACLE_PATCH"
"$TWAIN" --emit prod -C "$LOCKED" HEAD > "$PROD_PATCH"
if grep -q 'test_add.py' "$ORACLE_PATCH" && ! grep -q 'app.py' "$ORACLE_PATCH"; then
  ok "emit oracle is tests only"
else
  bad "emit oracle is tests only" "$(head -20 "$ORACLE_PATCH")"
fi
if grep -q 'app.py' "$PROD_PATCH" && ! grep -q 'test_add.py' "$PROD_PATCH"; then
  ok "emit prod is production only"
else
  bad "emit prod is production only" "$(head -20 "$PROD_PATCH")"
fi

# Apply oracle half onto parent → tree occupies oracle, not prod
AHEAD="$WORKDIR/ahead"
git clone -q "$LOCKED" "$AHEAD"
git -C "$AHEAD" reset -q --hard HEAD^
if git -C "$AHEAD" apply --index "$ORACLE_PATCH"; then
  git -C "$AHEAD" commit -q -m 'tests first'
  expect_status "emitted oracle vs original patch" ORACLE_AHEAD \
    --patch <("$TWAIN" --emit oracle -C "$LOCKED" HEAD >/dev/null; git -C "$LOCKED" diff HEAD^ HEAD) \
    -C "$AHEAD" --against HEAD --report-only >/dev/null 2>&1 || true
  # occupy the original mixed patch against the tests-first tree
  git -C "$LOCKED" diff HEAD^ HEAD > "$WORKDIR/mixed.patch"
  expect_status "mixed patch on tests-first tree" ORACLE_AHEAD \
    --patch "$WORKDIR/mixed.patch" -C "$AHEAD" --against HEAD
else
  bad "git apply oracle half" "apply failed"
fi

echo "== ugly path via --patch =="
UGLY="$WORKDIR/ugly"
mkdir -p "$UGLY/src" "$UGLY/tests"
printf 'pub fn add(a: i32, b: i32) -> i32 { a + b }\npub fn 加算(a: i32, b: i32) -> i32 {\n    a + b\n}\n' \
  > "$UGLY/src/file with spaces.rs"
printf '#[test]\nfn 加算_works() { assert_eq!(加算(1,1), 2); }\n' > "$UGLY/tests/加算_test.rs"
cat > "$WORKDIR/ugly.patch" <<'EOF'
diff --git a/src/file with spaces.rs b/src/file with spaces.rs
--- a/src/file with spaces.rs
+++ b/src/file with spaces.rs
@@ -1,3 +1,6 @@
 pub fn add(a: i32, b: i32) -> i32 { a + b }
+pub fn 加算(a: i32, b: i32) -> i32 {
+    a + b
+}
diff --git a/tests/加算_test.rs b/tests/加算_test.rs
new file mode 100644
--- /dev/null
+++ b/tests/加算_test.rs
@@ -0,0 +1,2 @@
+#[test]
+fn 加算_works() { assert_eq!(加算(1,1), 2); }
EOF
expect_status "ugly path LOCKED" LOCKED --patch "$WORKDIR/ugly.patch" -C "$UGLY" --worktree

echo "== dogfood (optional trees) =="
dogfood() {
  local name="$1"
  local repo="$2"
  local rev="$3"
  local want="$4"
  if [[ ! -d "$repo/.git" && ! -d "$repo" ]]; then
    echo "  SKIP  $name (no $repo)"
    return
  fi
  if [[ ! -e "$repo/.git" ]]; then
    echo "  SKIP  $name (not git)"
    return
  fi
  local out got
  out="$("$TWAIN" --report-only --porcelain -C "$repo" "$rev" --against "$rev" 2>&1)" || true
  got="$(echo "$out" | awk '/^status /{print $2; exit}')"
  if [[ -n "$want" && "$got" != "$want" ]]; then
    bad "$name status=$want" "got=$got $(echo "$out" | tr '\n' ' ')"
    return
  fi
  local prod oracle
  prod="$(echo "$out" | awk '/^prod /{print $2; exit}')"
  oracle="$(echo "$out" | awk '/^oracle /{print $2; exit}')"
  # sandwich: occupying a commit against itself, existing halves must be APPLIED
  local ok_s=1
  if [[ "$prod" != "EMPTY" && "$prod" != "APPLIED" ]]; then
    ok_s=0
  fi
  if [[ "$oracle" != "EMPTY" && "$oracle" != "APPLIED" ]]; then
    ok_s=0
  fi
  if [[ $ok_s -eq 1 ]]; then
    ok "$name sandwich ($got prod=$prod oracle=$oracle)"
  else
    bad "$name sandwich" "prod=$prod oracle=$oracle $out"
  fi
}

KIZU="/Users/annenpolka/ghq/github.com/annenpolka/kizu"
SIT="/Users/annenpolka/ghq/github.com/annenpolka/sitbone"
VOID="/Users/annenpolka/ghq/github.com/annenpolka/voidtrace"
TENA="/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi"

# HEAD sandwiches (whatever is currently HEAD)
dogfood "kizu HEAD" "$KIZU" HEAD ""
dogfood "sitbone HEAD" "$SIT" HEAD ""
dogfood "voidtrace HEAD" "$VOID" HEAD ""
dogfood "tenaoshi HEAD" "$TENA" HEAD ""

# Known shapes (status asserted; sandwich is the occupancy invariant)
dogfood "kizu jsx feat" "$KIZU" 04adde1 "LOCKED"
dogfood "sitbone notch MUTE" "$SIT" 094769d "MUTE"
dogfood "tenaoshi contract HOLLOW" "$TENA" 4878b75 "HOLLOW"
dogfood "voidtrace shield" "$VOID" bb4c16d "LOCKED"

echo
echo "demo: $pass passed, $fail failed"
if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
exit 0
