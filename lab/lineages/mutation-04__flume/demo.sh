#!/usr/bin/env bash
# Exercise flume as a pure stream rewriter: mixed Python/Rust/Swift logs,
# noise lines, and directory snapshots (never git refs, never locator args).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
FLUME="$ROOT/flume"
chmod +x "$FLUME"

if ! command -v python3 >/dev/null; then
  echo "demo.sh: python3 is required" >&2
  exit 1
fi

fail() { echo "FAIL: $*" >&2; exit 1; }
pass() { echo "PASS: $*"; }

# The tool must not invoke git. A stub `git` on PATH dies if it is touched.
assert_no_git_needed() {
  local out bin
  bin="$TMP/nogit"
  mkdir -p "$bin"
  cat > "$bin/git" <<'STUB'
#!/bin/sh
echo "flume must not invoke git: $*" >&2
exit 99
STUB
  chmod +x "$bin/git"
  out="$(PATH="$bin:$PATH" "$FLUME" --from-dir "$1" --to-dir "$2" < "$3")" || fail "flume failed (or called git) with a stub git on PATH"
  printf '%s\n' "$out"
}

TMP="$(mktemp -d "${TMPDIR:-/tmp}/flume-demo.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

FROM="$TMP/from"
TO="$TMP/to"
mkdir -p "$FROM/src" "$FROM/notes" "$FROM/Sources/SitboneCore" "$FROM/Engine/Sources/TenaoshiEngine"
mkdir -p "$TO/src/math" "$TO/src/app" "$TO/notes" "$TO/Sources/SitboneCore" "$TO/Engine/Sources/TenaoshiEngine"

# --- from snapshot ---
cat > "$FROM/src/calc.py" <<'PY'
"""tiny calculator."""

def add(a, b):
    """Return the sum of a and b."""
    return a + b

def secret_sauce(x):
    MAGIC = 0xDEADBEEF
    return x ^ MAGIC

def doomed():
    return "this will be deleted"

def helper_keep():
    return "stable helper"
PY

cat > "$FROM/src/app.rs" <<'RS'
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

pub fn seen_hunk_fingerprint(
    seen: &BTreeMap<(PathBuf, usize), u64>,
    path: &Path,
    old_start: usize,
) -> Option<u64> {
    seen.iter()
        .find(|((p, o), _)| *o == old_start && p.as_path() == path)
        .map(|(_, fp)| *fp)
}

fn nearest_landing_forward(next_run: Option<usize>, next_hh: Option<usize>) -> Option<usize> {
    match (next_run, next_hh) {
        (Some(r), Some(h)) => Some(r.min(h)),
        (Some(r), None) => Some(r),
        (None, Some(h)) => Some(h),
        (None, None) => None,
    }
}

fn helper_keep_rs() {
    let _ = "stable rust helper";
}
RS

cat > "$FROM/Engine/Sources/TenaoshiEngine/KinsokuEngine.swift" <<'SW'
/// kinsoku契約の実行体。変換プロンプト(contracts/prompt.md)とLLMClientを束ねる。
/// アダプタ実装を知らない(LLMClientインターフェースのみに依存する)。
public struct KinsokuEngine: Sendable {
    public let client: any LLMClient
    public let systemPrompt: String

    public init(client: any LLMClient, systemPrompt: String) {
        self.client = client
        self.systemPrompt = systemPrompt
    }

    public func transform(_ request: TransformRequest) async throws -> TransformResult {
        try await client.transform(request, systemPrompt: systemPrompt)
    }
}
SW

cat > "$FROM/Sources/SitboneCore/PresenceArbiter.swift" <<'SW'
public final class PresenceArbiter: PresenceDetectorProtocol {
    private let sensors: [any SensorProtocol]
    private let threshold: Double
    private let emaAlpha: Double

    public init(sensors: [any SensorProtocol], threshold: Double = 0.4, emaAlpha: Double = 0.3) {
        self.sensors = sensors
        self.threshold = threshold
        self.emaAlpha = emaAlpha
    }

    public func detect() async -> PresenceReading {
        let readings = await readAllSensors()
        return PresenceReading(status: .unknown, confidence: 0)
    }

    private func readAllSensors() async -> [SensorResult] {
        []
    }
}
SW

cat > "$FROM/Makefile" <<'MK'
.PHONY: test
test:
	python src/calc.py
MK

cat > "$FROM/LICENSE" <<'TXT'
copyright notice line
second license line
TXT

cat > "$FROM/notes/file with spaces.txt" <<'TXT'
see src/calc.py for MAGIC
line two of the spaced file
TXT

cat > "$FROM/src/weird:colon.py" <<'PY'
COLON_FILE = True
print("colon-named file")
PY

cat > "$FROM/src/日本語.py" <<'PY'
def greet():
    return "こんにちは"
PY

# --- to snapshot: split, rename, edit, delete, shift ---
cat > "$TO/src/math/ops.py" <<'PY'
"""tiny calculator, renamed and split."""

def add(a, b):
    """Return the sum of a and b."""
    return a + b


def helper_keep():
    return "stable helper"
PY

cat > "$TO/src/math/sauce.py" <<'PY'
"""extracted condiment."""

def secret_sauce(x, extra=0):
    MAGIC = 0xDEADBEEF
    return (x ^ MAGIC) + extra
PY

cat > "$TO/src/app/layout.rs" <<'RS'
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

pub fn seen_hunk_fingerprint(
    seen: &BTreeMap<(PathBuf, usize), u64>,
    path: &Path,
    old_start: usize,
) -> Option<u64> {
    seen.iter()
        .find(|((p, o), _)| *o == old_start && p.as_path() == path)
        .map(|(_, fp)| *fp)
}
RS

cat > "$TO/src/app/navigation.rs" <<'RS'
fn nearest_landing_forward(next_run: Option<usize>, next_hh: Option<usize>) -> Option<usize> {
    match (next_run, next_hh) {
        (Some(r), Some(h)) => Some(r.min(h)),
        (Some(r), None) => Some(r),
        (None, Some(h)) => Some(h),
        (None, None) => None,
    }
}

fn helper_keep_rs() {
    let _ = "stable rust helper";
}
RS

cat > "$TO/Engine/Sources/TenaoshiEngine/KinsokuEngine.swift" <<'SW'
/// kinsoku契約の実行体。変換プロンプト(contracts/prompt.md)とLLMClientを束ねる。
/// アダプタ実装を知らない(LLMClientインターフェースのみに依存する)。
public struct KinsokuEngine: Sendable {
    public let client: any LLMClient
    public let systemPrompt: String

    public init(client: any LLMClient, systemPrompt: String) {
        self.client = client
        self.systemPrompt = systemPrompt
    }

    public func transform(_ request: TransformRequest) async throws -> TransformResult {
        try await client.transform(request, systemPrompt: systemPrompt)
    }
}
SW

cat > "$TO/Sources/SitboneCore/PresenceArbiter.swift" <<'SW'
public final class PresenceArbiter: PresenceDetectorProtocol {
    private let sensors: [any SensorProtocol]
    private let presentThreshold: Double
    private let absentThreshold: Double
    private let emaAlpha: Double

    public init(
        sensors: [any SensorProtocol],
        presentThreshold: Double = 0.45,
        absentThreshold: Double = 0.35,
        emaAlpha: Double = 0.3
    ) {
        self.sensors = sensors
        self.presentThreshold = presentThreshold
        self.absentThreshold = absentThreshold
        self.emaAlpha = emaAlpha
    }

    public func stopCamera() {
        // added later
    }

    public func detect() async -> PresenceReading {
        let readings = await readAllSensors()
        return PresenceReading(status: .unknown, confidence: 0)
    }

    private func readAllSensors() async -> [SensorResult] {
        []
    }
}
SW

cat > "$TO/Makefile" <<'MK'
.PHONY: test
test:
	python src/math/ops.py
MK

cp "$FROM/LICENSE" "$TO/LICENSE"
cp "$FROM/notes/file with spaces.txt" "$TO/notes/file with spaces.txt"
cp "$FROM/src/weird:colon.py" "$TO/src/weird:colon.py"
cp "$FROM/src/日本語.py" "$TO/src/日本語.py"

# Mixed Python / rustc / Swift / noise stream. Line numbers in FROM:
# calc.py:3 add, :7 secret_sauce, :11 doomed, :14 helper_keep
# app.rs:4 seen_hunk_fingerprint, :14 nearest_landing_forward
# PresenceArbiter.swift:12 detect, :3 threshold (deleted)
# KinsokuEngine.swift:12 transform
MIXED="$TMP/mixed.log"
cat > "$MIXED" <<'LOG'
12:34:56 INFO starting build
error[E0599]: no method named seen_hunk_fingerprint
  --> src/app.rs:4:1
   |
 4 | pub fn seen_hunk_fingerprint(
   | -----------------------------
  File "src/calc.py", line 3, in add
pytest src/calc.py:14: in test_helper
note: also see src/calc.py:7
http://localhost:8080/health
error: src/calc.py:11: doomed is gone
LICENSE:1: copyright
  File "src/weird:colon.py", line 1, in <module>
notes/file with spaces.txt:1: see MAGIC
src/日本語.py:1: greet
PresenceArbiter.swift:12:20: error: cannot find 'threshold' in scope
KinsokuEngine.swift:12:5: error: type 'TransformRequest' is not a member
Makefile:2: recipe failed
  --> /home/runner/work/ugly/ugly/src/app.rs:14:5
   |
14 | fn nearest_landing_forward(next_run: Option<usize>, next_hh: Option<usize>) -> Option<usize> {
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
not a locator, just chatting about foo:bar and error:1
LOG

echo "== 1. mixed stream rewrite (no git on PATH) =="
rewritten="$(assert_no_git_needed "$FROM" "$TO" "$MIXED")"
echo "$rewritten"

echo "$rewritten" | grep -q 'src/app/layout.rs:4' || fail "rustc arrow did not follow app.rs split: $rewritten"
echo "$rewritten" | grep -q 'File "src/math/ops.py", line 3' || fail "python traceback missed ops.py: $rewritten"
echo "$rewritten" | grep -q 'src/math/ops.py:' || fail "pytest locator missed ops.py: $rewritten"
echo "$rewritten" | grep -q 'src/math/sauce.py:' || fail "secret_sauce did not follow extract: $rewritten"
echo "$rewritten" | grep -q 'src/calc.py:11' || fail "deleted doomed() should pass through: $rewritten"
echo "$rewritten" | grep -q 'http://localhost:8080/health' || fail "URL noise was eaten: $rewritten"
echo "$rewritten" | grep -q '12:34:56 INFO starting build' || fail "timestamp noise was eaten: $rewritten"
echo "$rewritten" | grep -q 'error\[E0599\]' || fail "rustc error code was eaten: $rewritten"
echo "$rewritten" | grep -q 'foo:bar and error:1' || fail "chatty noise was eaten: $rewritten"
echo "$rewritten" | grep -q 'LICENSE:1' || fail "LICENSE locator lost: $rewritten"
echo "$rewritten" | grep -q 'File "src/weird:colon.py", line 1' || fail "colon filename traceback mangled: $rewritten"
echo "$rewritten" | grep -q 'notes/file with spaces.txt:1' || fail "spaced filename lost: $rewritten"
echo "$rewritten" | grep -q 'src/日本語.py:1' || fail "unicode path lost: $rewritten"
echo "$rewritten" | grep -q 'PresenceArbiter.swift:' || fail "swift basename locator lost: $rewritten"
echo "$rewritten" | grep -q 'PresenceArbiter.swift:12:' && fail "swift detect() did not shift off line 12: $rewritten"
echo "$rewritten" | grep -q 'KinsokuEngine.swift:12' || fail "swift transform identity lost: $rewritten"
echo "$rewritten" | grep -q 'src/app/navigation.rs:' || fail "absolute CI rustc path missed navigation.rs: $rewritten"
echo "$rewritten" | grep -q '/home/runner/work/ugly/ugly/src/app/navigation.rs:' || fail "CI prefix was not preserved: $rewritten"
echo "$rewritten" | grep -q ' 4 | pub fn seen_hunk_fingerprint(' || fail "rustc gutter noise was eaten: $rewritten"
echo "$rewritten" | grep -q '14 | fn nearest_landing_forward' && fail "stale rustc gutter 14 left in stream: $rewritten"
echo "$rewritten" | grep -E -q '1 \| fn nearest_landing_forward' || fail "rustc gutter did not follow 14→1: $rewritten"
echo "$rewritten" | grep -q 'src/app.rs:4' && fail "stale rustc path left in stream: $rewritten"
echo "$rewritten" | grep -q 'src/calc.py:3' && fail "stale python path left in stream: $rewritten"
pass "mixed Python/Rust/Swift/noise stream"

echo "== 2. --trace maps on stderr, stdout stays a stream =="
trace_out="$TMP/trace.tsv"
stdout_out="$TMP/stdout.log"
"$FLUME" --from-dir "$FROM" --to-dir "$TO" --trace < "$MIXED" > "$stdout_out" 2> "$trace_out"
grep -q $'moved\tsrc/app.rs:4' "$trace_out" || fail "trace missing app.rs move: $(cat "$trace_out")"
grep -q 'src/app/layout.rs:4' "$trace_out" || fail "trace missing layout dest: $(cat "$trace_out")"
grep -q '12:34:56 INFO starting build' "$stdout_out" || fail "stdout lost noise when tracing"
# stdout must not be TSV
grep -qv $'^moved\t' "$stdout_out" || fail "stdout leaked trace TSV"
pass "trace is stderr; stdout remains the stream"

echo "== 3. positional args are log files, not locators =="
cp "$MIXED" "$TMP/a.log"
printf 'extra src/calc.py:14\n' > "$TMP/b.log"
out="$("$FLUME" --from-dir "$FROM" --to-dir "$TO" "$TMP/a.log" "$TMP/b.log")"
echo "$out" | grep -q 'src/app/layout.rs' || fail "log-file args missed a.log rewrite"
echo "$out" | grep -q 'src/math/ops.py' || fail "log-file args missed b.log rewrite"
echo "$out" | grep -q 'src/calc.py:14' && fail "locator-style arg interpretation crept back"
pass "args are extra streams"

echo "== 4. identity rewrite is a no-op on the path =="
idlog="$TMP/id.log"
printf 'src/math/ops.py:3: def add\n' > "$idlog"
# from=to
out="$("$FLUME" --from-dir "$TO" --to-dir "$TO" < "$idlog")"
echo "$out"
echo "$out" | grep -qx 'src/math/ops.py:3: def add' || fail "identity changed an already-fresh locator: $out"
pass "same-tree identity"

echo "== 5. unique-token dir-to-dir (no shared history) =="
mkdir -p "$TMP/old/src" "$TMP/new/pkg"
printf 'UNIQUE_TOKEN_QZX = 1\nx = UNIQUE_TOKEN_QZX\n' > "$TMP/old/src/old.py"
printf 'UNIQUE_TOKEN_QZX = 1\n' > "$TMP/new/pkg/new.py"
printf 'src/old.py:1: token\n' > "$TMP/tok.log"
out="$("$FLUME" --from-dir "$TMP/old" --to-dir "$TMP/new" < "$TMP/tok.log")"
echo "$out"
echo "$out" | grep -q 'pkg/new.py:1' || fail "unique token missed: $out"
pass "from-dir/to-dir unique token"

echo "== 6. line endings preserved =="
printf 'src/calc.py:14: helper\r\n' > "$TMP/crlf.log"
python3 - "$FLUME" "$FROM" "$TO" "$TMP/crlf.log" <<'PY'
import subprocess, sys
flume, src, dst, log = sys.argv[1:]
data = subprocess.check_output([flume, "--from-dir", src, "--to-dir", dst, log])
assert data.endswith(b"\r\n"), data
assert b"ops.py" in data, data
print("crlf ok", data)
PY
pass "CRLF preserved"

echo "== 7. --annotate keeps original text =="
out="$("$FLUME" --from-dir "$FROM" --to-dir "$TO" --annotate < "$MIXED")"
echo "$out" | grep -q 'src/app.rs:4' || fail "annotate should keep original locators: $out"
echo "$out" | grep -q 'layout.rs' || fail "annotate should mention dest: $out"
pass "annotate"

# --- real repo dogfood: copies of kizu / sitbone / tenaoshi ---
copy_tree() {
  local repo="$1" ref="$2" dest="$3"
  mkdir -p "$dest"
  git -C "$repo" archive "$ref" | tar -x -C "$dest"
}

KIZU="${KIZU:-/Users/annenpolka/ghq/github.com/annenpolka/kizu}"
if [[ -d "$KIZU/.git" || -f "$KIZU/.git" ]]; then
  echo "== 8. kizu copy: app.rs split (b4e6a5d → HEAD) =="
  copy_tree "$KIZU" b4e6a5d "$TMP/kizu-from"
  copy_tree "$KIZU" HEAD "$TMP/kizu-to"
  klog="$TMP/kizu.log"
  cat > "$klog" <<'LOG'
error[E0599]: no method named seen_hunk_fingerprint
  --> /home/runner/work/kizu/kizu/src/app.rs:529:5
   |
529 | pub fn seen_hunk_fingerprint(
  File "src/app.rs", line 543, in nearest_landing_forward
LICENSE:1: copyright
12:34:56 INFO cargo test
http://localhost:8080/health
LOG
  rewritten="$("$FLUME" --from-dir "$TMP/kizu-from" --to-dir "$TMP/kizu-to" < "$klog")"
  echo "$rewritten"
  echo "$rewritten" | grep -q 'src/app/layout.rs:' || fail "kizu CI path missed layout.rs: $rewritten"
  echo "$rewritten" | grep -q 'File "src/app/navigation.rs", line' || fail "kizu python tb missed navigation.rs: $rewritten"
  echo "$rewritten" | grep -q 'LICENSE:1' || fail "kizu LICENSE not parsed: $rewritten"
  echo "$rewritten" | grep -q 'http://localhost:8080/health' || fail "kizu URL eaten: $rewritten"
  echo "$rewritten" | grep -q 'src/app.rs:529' && fail "kizu left stale app.rs: $rewritten"
  echo "$rewritten" | grep -q '529 |' && fail "kizu rustc gutter left stale 529: $rewritten"
  echo "$rewritten" | grep -E -q '17 \| pub fn seen_hunk_fingerprint' || fail "kizu rustc gutter did not follow 529→17: $rewritten"
  pass "kizu mixed rustc/python/LICENSE log via directory copies"

  echo "== 8b. kizu read-only working tree as --to-dir =="
  rewritten="$("$FLUME" --from-dir "$TMP/kizu-from" --to-dir "$KIZU" < "$klog")"
  echo "$rewritten" | grep -q 'src/app/layout.rs:' || fail "kizu live tree missed layout.rs: $rewritten"
  pass "kizu live working tree as to-dir"
else
  echo "SKIP kizu dogfood (repo not present at $KIZU)"
fi

SIT="${SIT:-/Users/annenpolka/ghq/github.com/annenpolka/sitbone}"
if [[ -d "$SIT/.git" || -f "$SIT/.git" ]]; then
  echo "== 9. sitbone copy: PresenceArbiter detect() shift =="
  copy_tree "$SIT" a95da43 "$TMP/sit-from"
  copy_tree "$SIT" HEAD "$TMP/sit-to"
  slog="$TMP/sit.log"
  cat > "$slog" <<'LOG'
[10:15:03] swift build
Sources/SitboneCore/PresenceArbiter.swift:45:17: error: cannot find 'threshold' in scope
PresenceArbiter.swift:45:17: error: cannot find 'threshold' in scope
/Users/runner/work/sitbone/sitbone/Sources/SitboneCore/PresenceArbiter.swift:9:14: error: class PresenceArbiter
http://127.0.0.1:9090/metrics
note: talking about timeout:5 and retry:3
LOG
  rewritten="$("$FLUME" --from-dir "$TMP/sit-from" --to-dir "$TMP/sit-to" < "$slog")"
  echo "$rewritten"
  echo "$rewritten" | grep -q 'PresenceArbiter.swift:' || fail "sitbone swift locator lost: $rewritten"
  echo "$rewritten" | grep -q 'PresenceArbiter.swift:45:' && fail "sitbone detect() still on 45: $rewritten"
  echo "$rewritten" | grep -q 'http://127.0.0.1:9090/metrics' || fail "sitbone URL eaten: $rewritten"
  echo "$rewritten" | grep -q 'timeout:5 and retry:3' || fail "sitbone noise eaten: $rewritten"
  pass "sitbone Swift diagnostic stream"

  echo "== 9b. sitbone read-only working tree as --to-dir =="
  rewritten="$("$FLUME" --from-dir "$TMP/sit-from" --to-dir "$SIT" < "$slog")"
  echo "$rewritten" | grep -q 'PresenceArbiter.swift:45:' && fail "sitbone live tree still on 45: $rewritten"
  pass "sitbone live working tree as to-dir"
else
  echo "SKIP sitbone dogfood (repo not present at $SIT)"
fi

TENA="${TENA:-/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi}"
if [[ -d "$TENA/.git" || -f "$TENA/.git" ]]; then
  echo "== 10. tenaoshi copy: KinsokuEngine.transform identity =="
  copy_tree "$TENA" a41089c "$TMP/tena-from"
  copy_tree "$TENA" HEAD "$TMP/tena-to"
  tlog="$TMP/tena.log"
  cat > "$tlog" <<'LOG'
swiftc: compiling
Engine/Sources/TenaoshiEngine/KinsokuEngine.swift:12:17: error: cannot find type 'TransformRequest' in scope
KinsokuEngine.swift:12:17: error: cannot find type 'TransformRequest' in scope
  File "Engine/Sources/TenaoshiEngine/KinsokuEngine.swift", line 12, in transform
12:00:01 INFO ok
LOG
  rewritten="$("$FLUME" --from-dir "$TMP/tena-from" --to-dir "$TMP/tena-to" < "$tlog")"
  echo "$rewritten"
  echo "$rewritten" | grep -q 'KinsokuEngine.swift:12' || fail "tenaoshi transform line lost: $rewritten"
  echo "$rewritten" | grep -q 'File "Engine/Sources/TenaoshiEngine/KinsokuEngine.swift", line 12' || fail "tenaoshi python form lost: $rewritten"
  pass "tenaoshi Swift identity stream"

  echo "== 10b. tenaoshi read-only working tree as --to-dir =="
  rewritten="$("$FLUME" --from-dir "$TMP/tena-from" --to-dir "$TENA" < "$tlog")"
  echo "$rewritten" | grep -q 'KinsokuEngine.swift:12' || fail "tenaoshi live tree lost transform: $rewritten"
  pass "tenaoshi live working tree as to-dir"
else
  echo "SKIP tenaoshi dogfood (repo not present at $TENA)"
fi

echo
echo "All demo checks passed."
exit 0
