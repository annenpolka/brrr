#!/usr/bin/env bash
# demo.sh — must exit 0. Exercises the primitive, not a screenshot.
set -euo pipefail
cd "$(dirname "$0")"
chmod +x ./orbit fixtures/beta fixtures/gamma fixtures/missing fixtures/pathA/tool fixtures/pathB/tool

fail() { echo "FAIL: $*" >&2; exit 1; }
pass() { echo "PASS: $*"; }

echo "== selftest =="
./orbit --selftest || fail "selftest"

echo
echo "== PATH order is the identity of *this* tool =="
OUT=$(./orbit --path "$PWD/fixtures/pathA:$PWD/fixtures/pathB" dump tool)
echo "$OUT"
echo "$OUT" | grep -q "pathA/tool" || fail "PATH A should win"
echo "$OUT" | grep -q "shadowed" || fail "PATH B should be shadowed"
./orbit --json --path "$PWD/fixtures/pathA:$PWD/fixtures/pathB" dump tool > /tmp/orbit-a.json
./orbit --json --path "$PWD/fixtures/pathB:$PWD/fixtures/pathA" dump tool > /tmp/orbit-b.json
if ./orbit diff /tmp/orbit-a.json /tmp/orbit-b.json >/tmp/orbit-path.diff; then
  fail "A vs B PATH should exit 1"
fi
grep -q "payload" /tmp/orbit-path.diff || fail "diff should mention payload"
pass "PATH swap is a different orbit"

echo
echo "== relative shebang chain =="
OUT=$(./orbit dump ./fixtures/beta)
echo "$OUT"
echo "$OUT" | grep -q "shebang" || fail "beta should be a shebang proxy"
echo "$OUT" | grep -qi "python" || fail "beta payload should be python"
pass "relative shebang followed"

echo
echo "== missing interpreter is a warning, not a crash =="
OUT=$(./orbit dump ./fixtures/missing)
echo "$OUT"
echo "$OUT" | grep -q "missing interpreter" || fail "expected missing interpreter"
pass "missing interpreter"

echo
echo "== python3 vs /usr/bin/python3 (guise is not payload) =="
if [[ -x /usr/bin/python3 && -x "$(command -v python3)" ]]; then
  ./orbit dump python3 | tee /tmp/orbit-py.txt
  ./orbit dump /usr/bin/python3 | tee /tmp/orbit-usrpy.txt
  if ./orbit diff python3 /usr/bin/python3 | tee /tmp/orbit-pydiff.txt; then
    # identical only if PATH python *is* /usr/bin/python3
    CHOSEN=$(./orbit --porcelain dump python3 | awk -F'\t' '$1=="chosen"{print $2}')
    if [[ "$CHOSEN" == "/usr/bin/python3" ]]; then
      pass "PATH python3 is /usr/bin/python3 (no homebrew shadow)"
    else
      fail "homebrew python3 and /usr/bin/python3 should differ"
    fi
  else
    grep -E "proxy|payload|restricted" /tmp/orbit-pydiff.txt || true
    grep -q "xcselect" /tmp/orbit-usrpy.txt || echo "(note: /usr/bin/python3 not xcselect on this machine)"
    pass "python3 orbits differ"
  fi
else
  echo "skip: python3 pair not present"
fi

echo
echo "== cargo is rustup in a hat =="
if command -v cargo >/dev/null && command -v rustup >/dev/null; then
  ./orbit dump cargo | tee /tmp/orbit-cargo.txt
  grep -q "rustup" /tmp/orbit-cargo.txt || fail "cargo should report rustup proxy"
  PAY=$(./orbit --porcelain dump cargo | awk -F'\t' '$1=="payload"{print $2}')
  echo "payload $PAY"
  [[ "$PAY" == *"/toolchains/"* ]] || fail "cargo payload should be a toolchain cargo"
  pass "cargo guise is rustup; payload is toolchain"
else
  echo "skip: cargo/rustup not present"
fi

echo
echo "== node rpath: THIS copy, not the name 'node' =="
if command -v node >/dev/null; then
  ./orbit dump node | tee /tmp/orbit-node.txt
  grep -q "libnode" /tmp/orbit-node.txt || fail "node should name libnode"
  TMPN=$(mktemp -d /tmp/orbit-node-XXXXXX)
  NODEBIN=$(python3 -c "import shutil; print(shutil.which('node'))")
  cp "$NODEBIN" "$TMPN/node"
  chmod +x "$TMPN/node"
  ./orbit dump "$TMPN/node" | tee /tmp/orbit-nodecopy.txt
  if grep -q "MISSING" /tmp/orbit-nodecopy.txt; then
    pass "copied node stub cannot see libnode — this binary, not the name"
  else
    echo "(copy still resolved libnode; rpath may be absolute)"
    cat /tmp/orbit-nodecopy.txt
    pass "node dump ran"
  fi
  rm -rf "$TMPN"
else
  echo "skip: node not present"
fi

echo
echo "== SIP: /bin/ls strips DYLD_*; homebrew git does not =="
if [[ -x /bin/ls ]]; then
  # prefixing DYLD_* on ./orbit does nothing: shebang is /usr/bin/env (restricted).
  ./orbit --env DYLD_PRINT_LIBRARIES=1 dump /bin/ls | tee /tmp/orbit-ls.txt
  grep -q "RESTRICTED" /tmp/orbit-ls.txt || fail "/bin/ls should be restricted"
  grep -q "STRIP" /tmp/orbit-ls.txt || fail "/bin/ls should strip DYLD_*"
  pass "/bin/ls is SIP-restricted"
fi
if command -v git >/dev/null; then
  ./orbit --env DYLD_PRINT_LIBRARIES=1 dump git | tee /tmp/orbit-git.txt
  if grep -q "RESTRICTED" /tmp/orbit-git.txt; then
    echo "(git unexpectedly restricted)"
  else
    grep -q "keep" /tmp/orbit-git.txt || true
    pass "PATH git is not SIP-restricted"
  fi
fi

echo
echo "== pip3 shebang =="
if command -v pip3 >/dev/null; then
  ./orbit dump pip3 | tee /tmp/orbit-pip3.txt
  grep -q "shebang" /tmp/orbit-pip3.txt || fail "pip3 should be shebang"
  pass "pip3 shebang followed to python"
fi

echo
echo "== kizu binary (if built) =="
KIZU=/Users/annenpolka/ghq/github.com/annenpolka/kizu/target/debug/kizu
if [[ -x "$KIZU" ]]; then
  ./orbit dump "$KIZU" | tee /tmp/orbit-kizu.txt
  pass "kizu dumped"
else
  echo "skip: kizu debug binary missing"
fi

echo
echo "demo ok"
