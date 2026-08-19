#!/usr/bin/env bash
# Exercise inlay as a JSON stream rewriter: cargo / rustc / generic
# JSON locators, noise lines, and directory snapshots (never git refs).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
INLAY="$ROOT/inlay"
chmod +x "$INLAY"

if ! command -v python3 >/dev/null; then
  echo "demo.sh: python3 is required" >&2
  exit 1
fi

fail() { echo "FAIL: $*" >&2; exit 1; }
pass() { echo "PASS: $*"; }

assert_json_line() {
  python3 -c 'import json,sys; json.loads(sys.stdin.read())' <<<"$1" \
    || fail "output is not valid JSON: $1"
}

# The tool must not invoke git. A stub `git` on PATH dies if it is touched.
assert_no_git_needed() {
  local out bin
  bin="$TMP/nogit"
  mkdir -p "$bin"
  cat > "$bin/git" <<'STUB'
#!/bin/sh
echo "inlay must not invoke git: $*" >&2
exit 99
STUB
  chmod +x "$bin/git"
  out="$(PATH="$bin:$PATH" "$INLAY" --from-dir "$1" --to-dir "$2" < "$3")" \
    || fail "inlay failed (or called git) with a stub git on PATH"
  printf '%s\n' "$out"
}

TMP="$(mktemp -d "${TMPDIR:-/tmp}/inlay-demo.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

FROM="$TMP/from"
TO="$TMP/to"
mkdir -p "$FROM/src" "$FROM/notes" "$FROM/Sources/SitboneCore" "$FROM/Engine/Sources/TenaoshiEngine"
mkdir -p "$TO/src/math" "$TO/src/app" "$TO/notes" "$TO/Sources/SitboneCore" "$TO/Engine/Sources/TenaoshiEngine"

# --- from snapshot ---
# Line numbers are part of the contract:
# 3 add, 7 secret_sauce, 11 doomed, 14 helper_keep
python3 - "$FROM/src/calc.py" <<'PY'
from pathlib import Path
Path(__import__("sys").argv[1]).write_text(
    "\n".join(
        [
            '"""tiny calculator."""',
            "",
            "def add(a, b):",
            '    """Return the sum of a and b."""',
            "    return a + b",
            "",
            "def secret_sauce(x):",
            "    MAGIC = 0xDEADBEEF",
            "    return x ^ MAGIC",
            "",
            "def doomed():",
            '    return "this will be deleted"',
            "",
            "def helper_keep():",
            '    return "stable helper"',
            "",
        ]
    ),
    encoding="utf-8",
)
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
# dest: ops.py:3 add, ops.py:7 helper_keep; sauce.py:3 secret_sauce
python3 - "$TO/src/math/ops.py" "$TO/src/math/sauce.py" <<'PY'
from pathlib import Path
import sys
Path(sys.argv[1]).write_text(
    "\n".join(
        [
            '"""tiny calculator, renamed and split."""',
            "",
            "def add(a, b):",
            '    """Return the sum of a and b."""',
            "    return a + b",
            "",
            "def helper_keep():",
            '    return "stable helper"',
            "",
        ]
    ),
    encoding="utf-8",
)
Path(sys.argv[2]).write_text(
    "\n".join(
        [
            '"""extracted condiment."""',
            "",
            "def secret_sauce(x, extra=0):",
            "    MAGIC = 0xDEADBEEF",
            "    return (x ^ MAGIC) + extra",
            "",
        ]
    ),
    encoding="utf-8",
)
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

# cargo --message-format=json + rustc JSON + generic pairs + chatter
MIXED="$TMP/mixed.jsonl"
python3 - "$MIXED" <<'PY'
import json, sys
path = sys.argv[1]
rows = [
    {"reason": "compiler-artifact", "package_id": "ugly@0.1.0", "fresh": True},
    {
        "reason": "compiler-message",
        "package_id": "ugly@0.1.0",
        "manifest_path": "/home/runner/work/ugly/ugly/Cargo.toml",
        "target": {
            "name": "ugly",
            "src_path": "/home/runner/work/ugly/ugly/src/app.rs",
        },
        "message": {
            "$message_type": "diagnostic",
            "message": "no method named seen_hunk_fingerprint",
            "code": {"code": "E0599", "explanation": "see the book"},
            "level": "error",
            "spans": [
                {
                    "file_name": "src/app.rs",
                    "byte_start": 120,
                    "byte_end": 142,
                    "line_start": 4,
                    "line_end": 4,
                    "column_start": 1,
                    "column_end": 24,
                    "is_primary": True,
                    "text": [
                        {
                            "text": "pub fn seen_hunk_fingerprint(",
                            "highlight_start": 1,
                            "highlight_end": 24,
                        }
                    ],
                    "label": None,
                    "suggested_replacement": None,
                    "suggestion_applicability": None,
                    "expansion": None,
                }
            ],
            "children": [],
            "rendered": (
                "error[E0599]: no method named seen_hunk_fingerprint\n"
                "  --> src/app.rs:4:1\n"
                "   |\n"
                " 4 | pub fn seen_hunk_fingerprint(\n"
                "   | ----------------------------\n"
            ),
        },
    },
    {
        "$message_type": "diagnostic",
        "level": "error",
        "message": "landing",
        "spans": [
            {
                "file_name": "/home/runner/work/ugly/ugly/src/app.rs",
                "line_start": 14,
                "line_end": 14,
                "column_start": 5,
                "column_end": 28,
                "byte_start": 4004,
                "byte_end": 4030,
                "text": [
                    {
                        "text": "fn nearest_landing_forward(next_run: Option<usize>, next_hh: Option<usize>) -> Option<usize> {"
                    }
                ],
            }
        ],
        "rendered": (
            "  --> /home/runner/work/ugly/ugly/src/app.rs:14:5\n"
            "   |\n"
            "14 | fn nearest_landing_forward(next_run: Option<usize>, next_hh: Option<usize>) -> Option<usize> {\n"
        ),
    },
    {
        "ts": "12:34:56",
        "file": "src/calc.py",
        "line": 3,
        "msg": 'File "src/calc.py", line 3, in add',
    },
    {"tool": "pytest", "filename": "src/calc.py", "lineno": 14, "when": "call"},
    {"note": "also see src/calc.py:7", "url": "http://localhost:8080/health"},
    {"error": "doomed is gone", "path": "src/calc.py", "line": 11},
    {"file": "LICENSE", "line": 1, "msg": "copyright"},
    {"filename": "src/weird:colon.py", "line": 1},
    {"file": "notes/file with spaces.txt", "line": 1},
    {"file": "src/日本語.py", "line": 1},
    {
        "file": "Sources/SitboneCore/PresenceArbiter.swift",
        "line": 12,
        "column": 20,
        "level": "error",
        "msg": "PresenceArbiter.swift:12:20: error: cannot find 'threshold' in scope",
    },
    {
        "file_name": "Engine/Sources/TenaoshiEngine/KinsokuEngine.swift",
        "line_start": 12,
        "column_start": 5,
        "msg": "KinsokuEngine.swift:12:5: error: type 'TransformRequest' is not a member",
    },
    {"file": "Makefile", "line": 2},
    {"reason": "build-finished", "success": False},
]
with open(path, "w", encoding="utf-8") as f:
    f.write("   Compiling ugly v0.1.0\n")
    f.write("12:34:56 INFO starting build\n")
    for row in rows:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    f.write("not a locator, just chatting about foo:bar and error:1\n")
PY

echo "== 1. mixed cargo/rustc/generic JSON (no git on PATH) =="
rewritten="$(assert_no_git_needed "$FROM" "$TO" "$MIXED")"
echo "$rewritten"

python3 - "$rewritten" <<'PY' || fail "python assertions failed"
import json, sys
text = sys.argv[1]
json_rows = []
raw_rows = []
for line in text.splitlines():
    s = line.strip()
    if s.startswith("{") or s.startswith("["):
        json_rows.append(json.loads(line))
    else:
        raw_rows.append(line)

assert any("Compiling ugly" in r for r in raw_rows), raw_rows
assert any("12:34:56 INFO" in r for r in raw_rows), raw_rows
assert any("foo:bar and error:1" in r for r in raw_rows), raw_rows

# cargo wrapper: structured span
cargo = next(r for r in json_rows if r.get("reason") == "compiler-message")
span = cargo["message"]["spans"][0]
assert span["file_name"] == "src/app/layout.rs", span
assert span["line_start"] == 4, span
assert isinstance(span["line_start"], int), type(span["line_start"])
assert span["line_end"] == 4, span
assert "src/app.rs" not in span["file_name"]
# dest layout.rs is tiny: byte offset of line 4 col 1 is not the old 120
assert span["byte_start"] != 120, span
assert isinstance(span["byte_start"], int) and span["byte_start"] >= 0
rendered = cargo["message"]["rendered"]
assert "src/app/layout.rs:4:1" in rendered, rendered
assert "src/app.rs:4" not in rendered
assert "pub fn seen_hunk_fingerprint(" in rendered, rendered

# rustc diagnostic, absolute CI prefix, integer line
rustc = next(r for r in json_rows if r.get("$message_type") == "diagnostic" and r.get("reason") is None)
sp = rustc["spans"][0]
assert sp["file_name"].endswith("src/app/navigation.rs"), sp
assert "/home/runner/work/ugly/ugly/src/app/navigation.rs" == sp["file_name"], sp
assert sp["line_start"] == 1, sp
assert isinstance(sp["line_start"], int)
assert sp["byte_start"] != 4004, "stale byte_start left in span: %r" % (sp,)
assert sp["text"][0]["text"].startswith("fn nearest_landing_forward"), sp["text"]
assert "src/app.rs" not in rustc["rendered"]
assert "/home/runner/work/ugly/ugly/src/app/navigation.rs:1:5" in rustc["rendered"]
assert "14 | fn nearest_landing_forward" not in rustc["rendered"], rustc["rendered"]
assert "1 | fn nearest_landing_forward" in rustc["rendered"], rustc["rendered"]

# generic pairs
add = next(r for r in json_rows if r.get("ts") == "12:34:56")
assert add["file"] == "src/math/ops.py", add
assert add["line"] == 3, add
assert 'File "src/math/ops.py", line 3' in add["msg"], add

pytest = next(r for r in json_rows if r.get("tool") == "pytest")
assert pytest["filename"] == "src/math/ops.py", pytest
assert pytest["lineno"] == 7, pytest  # helper_keep moved 14 -> 7

sauce = next(r for r in json_rows if "also see" in str(r.get("note", "")))
assert "src/math/sauce.py:" in sauce["note"], sauce
assert sauce["url"] == "http://localhost:8080/health"

doomed = next(r for r in json_rows if r.get("error") == "doomed is gone")
assert doomed["path"] == "src/calc.py" and doomed["line"] == 11, doomed

lic = next(r for r in json_rows if r.get("msg") == "copyright")
assert lic["file"] == "LICENSE" and lic["line"] == 1

colon = next(r for r in json_rows if str(r.get("filename","")).endswith("colon.py") or "colon" in str(r.get("filename","")))
assert colon["filename"] == "src/weird:colon.py" and colon["line"] == 1

spaces = next(r for r in json_rows if "spaces" in str(r.get("file","")))
assert spaces["file"] == "notes/file with spaces.txt"

jp = next(r for r in json_rows if "日本語" in str(r.get("file","")))
assert jp["file"] == "src/日本語.py"

swift = next(r for r in json_rows if "threshold" in str(r.get("msg","")))
assert swift["line"] != 12, swift
assert "PresenceArbiter.swift:" in swift["msg"]
assert "PresenceArbiter.swift:12:" not in swift["msg"], swift

tena = next(r for r in json_rows if "TransformRequest" in str(r.get("msg","")))
assert tena["line_start"] == 12, tena
assert "KinsokuEngine.swift:12" in tena["msg"]

# cargo target src_path is path-only: do not invent a line rewrite
assert cargo["target"]["src_path"].endswith("src/app.rs"), cargo["target"]
assert cargo["manifest_path"].endswith("Cargo.toml")

art = next(r for r in json_rows if r.get("reason") == "compiler-artifact")
assert art["fresh"] is True
fin = next(r for r in json_rows if r.get("reason") == "build-finished")
assert fin["success"] is False
print("json assertions ok", len(json_rows), "objects")
PY
pass "mixed cargo/rustc/generic JSON + chatter"

echo "== 2. --trace maps on stderr, stdout stays JSON =="
trace_out="$TMP/trace.tsv"
stdout_out="$TMP/stdout.jsonl"
"$INLAY" --from-dir "$FROM" --to-dir "$TO" --trace < "$MIXED" > "$stdout_out" 2> "$trace_out"
grep -q $'moved\tsrc/app.rs:4' "$trace_out" || fail "trace missing app.rs move: $(cat "$trace_out")"
grep -q 'src/app/layout.rs:4' "$trace_out" || fail "trace missing layout dest: $(cat "$trace_out")"
grep -q 'Compiling ugly' "$stdout_out" || fail "stdout lost noise when tracing"
grep -qv $'^moved\t' "$stdout_out" || fail "stdout leaked trace TSV"
python3 -c 'import json,sys
ok=0
for line in open(sys.argv[1],encoding="utf-8"):
    s=line.strip()
    if s.startswith("{") or s.startswith("["):
        json.loads(line); ok+=1
assert ok>=10, ok
' "$stdout_out" || fail "traced stdout is not valid JSON"
pass "trace is stderr; stdout remains JSON"

echo "== 3. positional args are JSON files, not locators =="
cp "$MIXED" "$TMP/a.jsonl"
printf '%s\n' '{"file":"src/calc.py","line":14}' > "$TMP/b.jsonl"
out="$("$INLAY" --from-dir "$FROM" --to-dir "$TO" "$TMP/a.jsonl" "$TMP/b.jsonl")"
echo "$out" | grep -q 'src/app/layout.rs' || fail "log-file args missed a.jsonl rewrite"
echo "$out" | grep -q 'src/math/ops.py' || fail "log-file args missed b.jsonl rewrite"
echo "$out" | grep -q '"line":14' && fail "stale helper line left in b.jsonl"
pass "args are extra JSON streams"

echo "== 4. identity rewrite is a no-op on a fresh locator =="
printf '%s\n' '{"file":"src/math/ops.py","line":3,"msg":"def add"}' > "$TMP/id.json"
out="$("$INLAY" --from-dir "$TO" --to-dir "$TO" < "$TMP/id.json")"
echo "$out"
python3 -c 'import json,sys
o=json.loads(sys.argv[1])
assert o=={"file":"src/math/ops.py","line":3,"msg":"def add"}, o
' "$out" || fail "identity changed an already-fresh locator: $out"
pass "same-tree identity"

echo "== 5. unique-token dir-to-dir (no shared history) =="
mkdir -p "$TMP/old/src" "$TMP/new/pkg"
printf 'UNIQUE_TOKEN_QZX = 1\nx = UNIQUE_TOKEN_QZX\n' > "$TMP/old/src/old.py"
printf 'UNIQUE_TOKEN_QZX = 1\n' > "$TMP/new/pkg/new.py"
printf '%s\n' '{"file":"src/old.py","line":1,"msg":"src/old.py:1: token"}' > "$TMP/tok.json"
out="$("$INLAY" --from-dir "$TMP/old" --to-dir "$TMP/new" < "$TMP/tok.json")"
echo "$out"
echo "$out" | grep -q 'pkg/new.py' || fail "unique token missed: $out"
python3 -c 'import json,sys
o=json.loads(sys.argv[1])
assert o["file"]=="pkg/new.py" and o["line"]==1, o
assert "pkg/new.py:1" in o["msg"], o
' "$out" || fail "unique token JSON fields missed: $out"
pass "from-dir/to-dir unique token"

echo "== 6. pretty-printed JSON value (not NDJSON) =="
python3 - "$TMP/pretty.json" <<'PY'
import json, sys
obj = {
    "spans": [{"file_name": "src/app.rs", "line_start": 4, "line_end": 8}],
    "note": "see src/calc.py:3",
}
open(sys.argv[1], "w").write(json.dumps(obj, indent=2) + "\n")
PY
out="$("$INLAY" --from-dir "$FROM" --to-dir "$TO" < "$TMP/pretty.json")"
echo "$out"
python3 -c 'import json,sys
o=json.loads(sys.argv[1])
assert o["spans"][0]["file_name"]=="src/app/layout.rs", o
assert o["spans"][0]["line_start"]==4
assert o["spans"][0]["line_end"]==8
assert "src/math/ops.py:3" in o["note"], o
' "$out" || fail "pretty JSON missed: $out"
pass "pretty-printed JSON object"

echo "== 7. dest path that would break a text splice =="
mkdir -p "$TMP/qfrom/src" "$TMP/qto/src"
printf 'QUOTE_MARK = 1\n' > "$TMP/qfrom/src/plain.py"
printf 'QUOTE_MARK = 1\n' > "$TMP/qto/src/quo\"te.py"
printf '%s\n' '{"file":"src/plain.py","line":1}' > "$TMP/quote.json"
out="$("$INLAY" --from-dir "$TMP/qfrom" --to-dir "$TMP/qto" < "$TMP/quote.json")"
echo "$out"
python3 -c 'import json,sys
o=json.loads(sys.argv[1])
assert o["file"]=="src/quo\"te.py" or o["file"]=="src/quo\"te.py".replace("\\\"","\"")
assert "quo" in o["file"] and "te.py" in o["file"], o
assert o["line"]==1
' "$out" || fail "quote path broke JSON: $out"
pass "JSON re-serialize survives dest quote in path"

# --- real repo dogfood: copies of kizu / sitbone / tenaoshi ---
copy_tree() {
  local repo="$1" ref="$2" dest="$3"
  mkdir -p "$dest"
  git -C "$repo" archive "$ref" | tar -x -C "$dest"
}

KIZU="${KIZU:-/Users/annenpolka/ghq/github.com/annenpolka/kizu}"
if [[ -d "$KIZU/.git" || -f "$KIZU/.git" ]]; then
  echo "== 8. kizu cargo JSON: app.rs split (b4e6a5d → HEAD) =="
  copy_tree "$KIZU" b4e6a5d "$TMP/kizu-from"
  copy_tree "$KIZU" HEAD "$TMP/kizu-to"
  klog="$TMP/kizu.jsonl"
  python3 - "$klog" <<'PY'
import json, sys
msg = {
    "reason": "compiler-message",
    "package_id": "kizu@0.1.0",
    "manifest_path": "/home/runner/work/kizu/kizu/Cargo.toml",
    "target": {"name": "kizu", "src_path": "/home/runner/work/kizu/kizu/src/app.rs"},
    "message": {
        "$message_type": "diagnostic",
        "message": "no method named seen_hunk_fingerprint",
        "code": {"code": "E0599"},
        "level": "error",
        "spans": [
            {
                "file_name": "/home/runner/work/kizu/kizu/src/app.rs",
                "byte_start": 18000,
                "byte_end": 18024,
                "line_start": 529,
                "line_end": 529,
                "column_start": 1,
                "column_end": 24,
                "is_primary": True,
                "text": [{"text": "pub fn seen_hunk_fingerprint(", "highlight_start": 1, "highlight_end": 24}],
            }
        ],
        "children": [],
        "rendered": (
            "error[E0599]: no method named seen_hunk_fingerprint\n"
            "  --> /home/runner/work/kizu/kizu/src/app.rs:529:5\n"
            "   |\n"
            "529 | pub fn seen_hunk_fingerprint(\n"
        ),
    },
}
nav = {
    "$message_type": "diagnostic",
    "level": "error",
    "message": "landing",
    "spans": [{"file_name": "src/app.rs", "line_start": 543, "line_end": 543, "column_start": 1, "byte_start": 19000}],
    "rendered": 'File "src/app.rs", line 543, in nearest_landing_forward',
}
open(sys.argv[1], "w").write(json.dumps(msg) + "\n" + json.dumps(nav) + "\n")
PY
  rewritten="$("$INLAY" --from-dir "$TMP/kizu-from" --to-dir "$TMP/kizu-to" < "$klog")"
  echo "$rewritten"
  python3 - "$rewritten" <<'PY' || fail "kizu JSON assertions failed"
import json, sys
rows = [json.loads(l) for l in sys.argv[1].splitlines() if l.strip().startswith("{")]
cargo = rows[0]
sp = cargo["message"]["spans"][0]
assert "src/app/layout.rs" in sp["file_name"], sp
assert "/home/runner/work/kizu/kizu/src/app/layout.rs" == sp["file_name"], sp
assert sp["line_start"] == 17, sp
assert isinstance(sp["line_start"], int)
assert "src/app.rs" not in sp["file_name"]
ren = cargo["message"]["rendered"]
assert "src/app/layout.rs:17:5" in ren or "src/app/layout.rs:17" in ren, ren
assert "src/app.rs:529" not in ren
assert "529 | pub fn seen_hunk_fingerprint(" not in ren, ren
assert "17 | pub fn seen_hunk_fingerprint(" in ren, ren
assert sp["byte_start"] != 18000, sp
assert isinstance(sp["byte_start"], int) and sp["byte_start"] > 0
assert sp["text"][0]["text"].startswith("pub fn seen_hunk_fingerprint("), sp["text"]
nav = rows[1]
assert nav["spans"][0]["file_name"] == "src/app/navigation.rs", nav
assert "navigation.rs" in nav["rendered"]
assert 'File "src/app/navigation.rs", line' in nav["rendered"], nav["rendered"]
print("kizu ok", sp["file_name"], sp["line_start"])
PY
  pass "kizu cargo/rustc JSON via directory copies"

  echo "== 8b. kizu read-only working tree as --to-dir =="
  rewritten="$("$INLAY" --from-dir "$TMP/kizu-from" --to-dir "$KIZU" < "$klog")"
  echo "$rewritten" | grep -q 'src/app/layout.rs' || fail "kizu live tree missed layout.rs: $rewritten"
  pass "kizu live working tree as to-dir"
else
  echo "SKIP kizu dogfood (repo not present at $KIZU)"
fi

SIT="${SIT:-/Users/annenpolka/ghq/github.com/annenpolka/sitbone}"
if [[ -d "$SIT/.git" || -f "$SIT/.git" ]]; then
  echo "== 9. sitbone Swift JSON: PresenceArbiter detect() shift =="
  copy_tree "$SIT" a95da43 "$TMP/sit-from"
  copy_tree "$SIT" HEAD "$TMP/sit-to"
  slog="$TMP/sit.jsonl"
  python3 - "$slog" <<'PY'
import json, sys
rows = [
    {"ts": "10:15:03", "event": "swift build"},
    {
        "file": "Sources/SitboneCore/PresenceArbiter.swift",
        "line": 45,
        "column": 17,
        "level": "error",
        "msg": "Sources/SitboneCore/PresenceArbiter.swift:45:17: error: cannot find 'threshold' in scope",
    },
    {
        "file": "PresenceArbiter.swift",
        "line": 45,
        "column": 17,
        "msg": "PresenceArbiter.swift:45:17: error: cannot find 'threshold' in scope",
    },
    {
        "file_name": "/Users/runner/work/sitbone/sitbone/Sources/SitboneCore/PresenceArbiter.swift",
        "line_start": 9,
        "msg": "class PresenceArbiter",
        "url": "http://127.0.0.1:9090/metrics",
        "chatter": "timeout:5 and retry:3",
    },
]
open(sys.argv[1], "w").write("\n".join(json.dumps(r) for r in rows) + "\n")
PY
  rewritten="$("$INLAY" --from-dir "$TMP/sit-from" --to-dir "$TMP/sit-to" < "$slog")"
  echo "$rewritten"
  python3 - "$rewritten" <<'PY' || fail "sitbone JSON assertions failed"
import json, sys
rows = [json.loads(l) for l in sys.argv[1].splitlines() if l.strip().startswith("{")]
d1 = next(r for r in rows if r.get("level")=="error")
assert d1["line"] != 45, d1
assert d1["file"].endswith("PresenceArbiter.swift"), d1
assert ":45:" not in d1["msg"], d1
d2 = next(r for r in rows if r.get("file")=="PresenceArbiter.swift" or r.get("file","").endswith("PresenceArbiter.swift") and "msg" in r and r.get("level") is None)
# basename form may stay basename
assert ":45:" not in d2["msg"], d2
absr = next(r for r in rows if "metrics" in str(r.get("url","")))
assert absr["url"] == "http://127.0.0.1:9090/metrics"
assert absr["chatter"] == "timeout:5 and retry:3"
print("sitbone ok", d1["line"])
PY
  pass "sitbone Swift JSON diagnostic stream"

  echo "== 9b. sitbone read-only working tree as --to-dir =="
  rewritten="$("$INLAY" --from-dir "$TMP/sit-from" --to-dir "$SIT" < "$slog")"
  echo "$rewritten" | grep -q ':45' && fail "sitbone live tree still on 45: $rewritten"
  pass "sitbone live working tree as to-dir"
else
  echo "SKIP sitbone dogfood (repo not present at $SIT)"
fi

TENA="${TENA:-/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi}"
if [[ -d "$TENA/.git" || -f "$TENA/.git" ]]; then
  echo "== 10. tenaoshi JSON: KinsokuEngine.transform identity =="
  copy_tree "$TENA" a41089c "$TMP/tena-from"
  copy_tree "$TENA" HEAD "$TMP/tena-to"
  tlog="$TMP/tena.jsonl"
  python3 - "$tlog" <<'PY'
import json, sys
rows = [
    {"event": "swiftc"},
    {
        "file_name": "Engine/Sources/TenaoshiEngine/KinsokuEngine.swift",
        "line_start": 12,
        "column_start": 17,
        "msg": "Engine/Sources/TenaoshiEngine/KinsokuEngine.swift:12:17: error: cannot find type 'TransformRequest' in scope",
    },
    {
        "file": "KinsokuEngine.swift",
        "line": 12,
        "msg": 'File "Engine/Sources/TenaoshiEngine/KinsokuEngine.swift", line 12, in transform',
    },
]
open(sys.argv[1], "w").write("\n".join(json.dumps(r) for r in rows) + "\n")
PY
  rewritten="$("$INLAY" --from-dir "$TMP/tena-from" --to-dir "$TMP/tena-to" < "$tlog")"
  echo "$rewritten"
  python3 - "$rewritten" <<'PY' || fail "tenaoshi JSON assertions failed"
import json, sys
rows = [json.loads(l) for l in sys.argv[1].splitlines() if l.strip().startswith("{")]
a = next(r for r in rows if "line_start" in r)
assert a["line_start"] == 12, a
assert "KinsokuEngine.swift" in a["file_name"]
b = next(r for r in rows if r.get("file")=="KinsokuEngine.swift" or "File " in str(r.get("msg","")))
assert "line 12" in b["msg"], b
print("tenaoshi ok")
PY
  pass "tenaoshi Swift identity JSON stream"

  echo "== 10b. tenaoshi read-only working tree as --to-dir =="
  rewritten="$("$INLAY" --from-dir "$TMP/tena-from" --to-dir "$TENA" < "$tlog")"
  echo "$rewritten" | grep -q 'KinsokuEngine.swift' || fail "tenaoshi live tree lost transform: $rewritten"
  pass "tenaoshi live working tree as to-dir"
else
  echo "SKIP tenaoshi dogfood (repo not present at $TENA)"
fi

echo
echo "All demo checks passed."
exit 0
