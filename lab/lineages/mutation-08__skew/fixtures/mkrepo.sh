#!/usr/bin/env bash
# Build a deterministic git repo whose *files* sleep through definition changes.
# Clock is last-commit-touching-the-file (and later, worktree mtime) — not blame.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
DEST="${1:-"$ROOT/lagrepo"}"

rm -rf "$DEST"
mkdir -p "$DEST"
cd "$DEST"

git init -q -b main
git -c user.name='skew' -c user.email='skew@example.test' config user.name skew
git -c user.name='skew' -c user.email='skew@example.test' config user.email skew@example.test

commit() {
  local when="$1"
  local msg="$2"
  GIT_AUTHOR_DATE="$when" GIT_COMMITTER_DATE="$when" \
    git -c user.name='skew' -c user.email='skew@example.test' \
    commit -q --allow-empty-message -m "$msg"
}

mkdir -p src tests docs "src/sub dir"

# --- t0: original API + cross-file callers -----------------------------------
cat > src/greet.py << 'EOF'
def greet(name):
    return "hi " + name


def shout(name):
    return greet(name) + "!"
EOF

cat > src/app.py << 'EOF'
from greet import greet


def run():
    print(greet("world"))
EOF

cat > docs/api.md << 'EOF'
# API

`greet(name)` returns a string starting with `hi`.
EOF

cat > "src/weird name (1).py" << 'EOF'
def odd_fn(x):
    return x + 1


def odd_caller(x):
    return odd_fn(x)
EOF

cat > src/use_odd.py << 'EOF'
def run_odd(x):
    return odd_fn(x)
EOF

cat > "src/日本語.py" << 'EOF'
def zenkaku_add(a, b):
    return a + b
EOF

cat > "src/sub dir/use_zenkaku.py" << 'EOF'
from 日本語 import zenkaku_add


def twice(a, b):
    return zenkaku_add(a, b) + zenkaku_add(a, b)
EOF

cat > src/lib.rs << 'EOF'
pub fn rust_greet(name: &str) -> String {
    format!("hi {}", name)
}

pub fn rust_shout(name: &str) -> String {
    rust_greet(name)
}
EOF

cat > src/use_rust.rs << 'EOF'
fn call_rust() {
    let _ = rust_greet("x");
}
EOF

git add src docs
commit "2022-01-01T00:00:00 +0000" "add greet(name) and callers"

# --- t1: tests pin the old contract ------------------------------------------
cat > tests/test_greet.py << 'EOF'
from greet import greet


def test_greet():
    assert greet("x") == "hi x"
EOF

git add tests/test_greet.py
commit "2022-06-01T00:00:00 +0000" "test old greet contract"

# --- t2: signature change; same-file shout updated; other files sleep --------
cat > src/greet.py << 'EOF'
def greet(name, excited=False):
    base = "hello " + name
    if excited:
        return base + "!!"
    return base


def shout(name):
    return greet(name, excited=True)
EOF

cat > src/lib.rs << 'EOF'
pub fn rust_greet(name: &str, excited: bool) -> String {
    if excited {
        format!("hello {}!!", name)
    } else {
        format!("hello {}", name)
    }
}

pub fn rust_shout(name: &str) -> String {
    rust_greet(name)
}
EOF

git add src/greet.py src/lib.rs
commit "2023-01-01T00:00:00 +0000" "greet: hello + excited flag"

# --- t3: a new caller file that saw the excited signature --------------------
cat > src/cli.py << 'EOF'
from greet import greet


def main():
    print(greet("cli", excited=True))
EOF

git add src/cli.py
commit "2024-01-01T00:00:00 +0000" "cli uses new greet"

# --- t4: another definition change; cli sleeps through this one --------------
# fresh.py is saved in the *same* commit as the prefix change, so its file
# clock matches greet.py — it should NOT lag until greet.py is dirtied.
cat > src/greet.py << 'EOF'
def greet(name, excited=False, prefix="hello"):
    base = prefix + " " + name
    if excited:
        return base + "!!"
    return base


def shout(name):
    return greet(name, excited=True)
EOF

cat > src/fresh.py << 'EOF'
from greet import greet


def fresh_main():
    print(greet("fresh", prefix="hello"))
EOF

cat > "src/weird name (1).py" << 'EOF'
def odd_fn(x, step=2):
    return x + step


def odd_caller(x):
    return odd_fn(x)
EOF

cat > "src/日本語.py" << 'EOF'
def zenkaku_add(a, b, scale=1):
    return (a + b) * scale
EOF

git add src/greet.py src/fresh.py "src/weird name (1).py" "src/日本語.py"
commit "2024-06-01T00:00:00 +0000" "greet gains prefix; odd_fn gains step"

# Nested git repo (not tracked by parent). Must not crash the parent scan.
mkdir -p nested
git -C nested init -q -b main
echo 'def nested_only(): pass' > nested/only.py
git -C nested -c user.name='nested' -c user.email='n@n.test' add only.py
GIT_AUTHOR_DATE="2020-01-01T00:00:00 +0000" \
GIT_COMMITTER_DATE="2020-01-01T00:00:00 +0000" \
  git -C nested -c user.name='nested' -c user.email='n@n.test' commit -q -m "nested-only"

echo "$DEST"
