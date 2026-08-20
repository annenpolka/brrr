#!/usr/bin/env bash
# Build two tiny git repos that flip hatch/sow's assumption:
# the subject name at HEAD is the identity.
#
# leftover/  — isWebApp renamed to isBrowser; production still calls isWebApp("Brave Browser")
# hist/      — same rename, but callers became dynamic; Brave lives only in history
set -euo pipefail

DEST="${1:?usage: build.sh DEST_DIR}"
rm -rf "$DEST"
mkdir -p "$DEST/leftover/src" "$DEST/leftover/tests" "$DEST/hist/src" "$DEST/hist/tests"

git_init() {
  local repo="$1"
  git -C "$repo" init -q -b main
  git -C "$repo" config user.name till
  git -C "$repo" config user.email till@example.com
}

git_commit() {
  local repo="$1" msg="$2"
  git -C "$repo" add -A
  git -C "$repo" -c commit.gpgsign=false commit -q -m "$msg"
}

# --- leftover: incomplete rename, old-name callers still at HEAD ---
L="$DEST/leftover"
git_init "$L"
cat > "$L/src/web.py" <<'PY'
def isWebApp(name):
    return name in ("Safari", "Chrome", "Brave Browser")

def tick(app):
    isWebApp("Brave Browser")
    isWebApp(app)
PY
: > "$L/src/__init__.py"
cat > "$L/tests/test_web.py" <<'PY'
from src.web import isWebApp

def test_safari():
    isWebApp("Safari")
PY
cat > "$L/src/App.swift" <<'SW'
public enum WindowTitleParser {
    public static func isWebApp(_ appName: String) -> Bool {
        return appName == "Safari" || appName == "Brave Browser"
    }
}
public func tick(app: String) {
    _ = WindowTitleParser.isWebApp("Brave Browser")
}
SW
cat > "$L/tests/ParserTests.swift" <<'SW'
import XCTest
final class WindowTitleParserTests: XCTestCase {
    func testSafari() {
        _ = WindowTitleParser.isWebApp("Safari")
    }
}
SW
git_commit "$L" "seed isWebApp"

cat > "$L/src/web.py" <<'PY'
def isBrowser(name):
    return name in ("Safari", "Chrome", "Brave Browser")

def tick(app):
    isWebApp("Brave Browser")
    isBrowser(app)
PY
cat > "$L/tests/test_web.py" <<'PY'
from src.web import isBrowser

def test_safari():
    isBrowser("Safari")
PY
cat > "$L/src/App.swift" <<'SW'
public enum WindowTitleParser {
    public static func isBrowser(_ appName: String) -> Bool {
        return appName == "Safari" || appName == "Brave Browser"
    }
}
public func tick(app: String) {
    _ = WindowTitleParser.isWebApp("Brave Browser")
}
SW
cat > "$L/tests/ParserTests.swift" <<'SW'
import XCTest
final class WindowTitleParserTests: XCTestCase {
    func testSafari() {
        _ = WindowTitleParser.isBrowser("Safari")
    }
}
SW
git_commit "$L" "rename isWebApp -> isBrowser, leftover old callers"

# --- hist: callers went dynamic; Brave exists only as last week's isWebApp literal ---
H="$DEST/hist"
git_init "$H"
cat > "$H/src/web.py" <<'PY'
def isWebApp(name):
    return name in ("Safari", "Chrome", "Brave Browser")

def tick(app):
    isWebApp("Brave Browser")
    isWebApp(app)
PY
: > "$H/src/__init__.py"
cat > "$H/tests/test_web.py" <<'PY'
from src.web import isWebApp

def test_safari():
    isWebApp("Safari")
PY
git_commit "$H" "seed isWebApp"

cat > "$H/src/web.py" <<'PY'
def isBrowser(name):
    return name in ("Safari", "Chrome", "Brave Browser")

def tick(app):
    isBrowser(app)
PY
cat > "$H/tests/test_web.py" <<'PY'
from src.web import isBrowser

def test_safari():
    isBrowser("Safari")
PY
git_commit "$H" "rename isWebApp -> isBrowser, callers now dynamic"

echo "built leftover=$L hist=$H"
