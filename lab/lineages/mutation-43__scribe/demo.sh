#!/usr/bin/env bash
# Exercise scribe as a SARIF / clang JSON / Swift diagnostic rewriter.
# Two directory snapshots, never git refs. The binary itself never calls git.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SCRIBE="$ROOT/scribe"
chmod +x "$SCRIBE"

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
echo "scribe must not invoke git: $*" >&2
exit 99
STUB
  chmod +x "$bin/git"
  out="$(PATH="$bin:$PATH" "$SCRIBE" --from-dir "$1" --to-dir "$2" < "$3")" \
    || fail "scribe failed (or called git) with a stub git on PATH"
  printf '%s\n' "$out"
}

TMP="$(mktemp -d "${TMPDIR:-/tmp}/scribe-demo.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

FROM="$TMP/from"
TO="$TMP/to"
mkdir -p "$FROM/src" "$FROM/notes" "$FROM/Sources/SitboneCore" "$FROM/Engine/Sources/TenaoshiEngine"
mkdir -p "$TO/src/math" "$TO/src/app" "$TO/notes" "$TO/Sources/SitboneCore" "$TO/Engine/Sources/TenaoshiEngine"

# --- from snapshot ---
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

# ---------------------------------------------------------------------------
# 1. Mixed SARIF + clang array + Swift SourceKit + chatter (no git)
# ---------------------------------------------------------------------------
MIXED="$TMP/mixed.jsonl"
python3 - "$MIXED" <<'PY'
import json, sys
path = sys.argv[1]
sarif = {
    "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
    "version": "2.1.0",
    "runs": [{
        "tool": {"driver": {"name": "scribe-fixture", "rules": [{"id": "E0599"}]}},
        "artifacts": [
            {"location": {"uri": "src/app.rs"}},
        ],
        "results": [
            {
                "ruleId": "E0599",
                "level": "error",
                "message": {
                    "text": (
                        "no method named seen_hunk_fingerprint\n"
                        "  --> src/app.rs:4:1\n"
                        "   |\n"
                        " 4 | pub fn seen_hunk_fingerprint(\n"
                    )
                },
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": {"uri": "src/app.rs"},
                        "region": {
                            "startLine": 4,
                            "startColumn": 1,
                            "endLine": 4,
                            "endColumn": 24,
                            "byteOffset": 120,
                            "charOffset": 120,
                            "snippet": {"text": "pub fn seen_hunk_fingerprint("},
                        },
                    }
                }],
                "fixes": [{
                    "artifactChanges": [{
                        "artifactLocation": {"uri": "src/app.rs"},
                        "replacements": [{
                            "deletedRegion": {
                                "startLine": 4,
                                "startColumn": 1,
                                "endLine": 4,
                                "endColumn": 24,
                            },
                            "insertedContent": {"text": "pub fn seen_hunk_fingerprint("},
                        }]
                    }]
                }],
            },
            {
                "ruleId": "landing",
                "message": {"text": 'File "src/app.rs", line 14, in nearest_landing_forward'},
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": "file:///home/runner/work/ugly/ugly/src/app.rs",
                        },
                        "region": {
                            "startLine": 14,
                            "startColumn": 5,
                            "byteOffset": 4004,
                        },
                    }
                }],
            },
            {
                "ruleId": "doomed",
                "message": {"text": "doomed is gone"},
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": {"uri": "src/calc.py"},
                        "region": {"startLine": 11, "startColumn": 1},
                    }
                }],
            },
        ],
    }],
}
clang = [
    {
        "kind": "error",
        "message": "no method named seen_hunk_fingerprint",
        "locations": [{
            "caret": {
                "file": "src/app.rs",
                "line": 4,
                "column": 1,
                "offset": 120,
            },
            "ranges": [{
                "start": {"file": "src/app.rs", "line": 4, "column": 1, "offset": 120},
                "end": {"file": "src/app.rs", "line": 4, "column": 24, "offset": 142},
            }],
        }],
        "children": [],
        "fixits": [],
    }
]
swift_sk = {
    "key.diagnostics": [
        {
            "key.severity": "source.diagnostic.severity.error",
            "key.line": 12,
            "key.column": 20,
            "key.filepath": "Sources/SitboneCore/PresenceArbiter.swift",
            "key.description": "cannot find 'threshold' in scope",
            "key.offset": 400,
        }
    ]
}
swift_ser = {
    "diagnostics": [
        {
            "level": "error",
            "filename": "Engine/Sources/TenaoshiEngine/KinsokuEngine.swift",
            "line": 12,
            "column": 5,
            "offset": 500,
            "spelling": "type 'TransformRequest' is not a member",
            "message": "KinsokuEngine.swift:12:5: error: type 'TransformRequest' is not a member",
        }
    ]
}
# cargo schema: MUST stay stale. That is the flipped assumption.
cargo = {
    "reason": "compiler-message",
    "target": {"src_path": "/home/runner/work/ugly/ugly/src/app.rs"},
    "message": {
        "spans": [{"file_name": "src/app.rs", "line_start": 4, "line_end": 4}],
    },
}
with open(path, "w", encoding="utf-8") as f:
    f.write("   Compiling ugly v0.1.0\n")
    f.write("12:34:56 INFO starting build\n")
    f.write(json.dumps(sarif, ensure_ascii=False) + "\n")
    f.write(json.dumps(clang, ensure_ascii=False) + "\n")
    f.write(json.dumps(swift_sk, ensure_ascii=False) + "\n")
    f.write(json.dumps(swift_ser, ensure_ascii=False) + "\n")
    f.write(json.dumps(cargo, ensure_ascii=False) + "\n")
    f.write("not a locator, just chatting about foo:bar and error:1\n")
PY

echo "== 1. mixed SARIF / clang / Swift (no git on PATH) =="
rewritten="$(assert_no_git_needed "$FROM" "$TO" "$MIXED")"
echo "$rewritten"

python3 - "$rewritten" <<'PY' || fail "mixed schema assertions failed"
import json, sys
text = sys.argv[1]
json_vals = []
raw_rows = []
dec = json.JSONDecoder()
i = 0
while i < len(text):
    while i < len(text) and text[i] in " \t\r":
        i += 1
    if i >= len(text):
        break
    if text[i] in "{[":
        val, end = dec.raw_decode(text, i)
        json_vals.append(val)
        i = end
        continue
    nl = text.find("\n", i)
    if nl < 0:
        raw_rows.append(text[i:])
        break
    raw_rows.append(text[i:nl])
    i = nl + 1

assert any("Compiling ugly" in r for r in raw_rows), raw_rows
assert any("foo:bar and error:1" in r for r in raw_rows), raw_rows

sarif = next(v for v in json_vals if isinstance(v, dict) and v.get("version") == "2.1.0")
res0 = sarif["runs"][0]["results"][0]
pl = res0["locations"][0]["physicalLocation"]
assert pl["artifactLocation"]["uri"] == "src/app/layout.rs", pl
assert pl["region"]["startLine"] == 4, pl
assert isinstance(pl["region"]["startLine"], int)
assert pl["region"]["endLine"] == 4
assert "src/app.rs" not in pl["artifactLocation"]["uri"]
assert pl["region"]["byteOffset"] != 120, pl
assert isinstance(pl["region"]["byteOffset"], int)
assert pl["region"]["snippet"]["text"].startswith("pub fn seen_hunk_fingerprint("), pl
msg = res0["message"]["text"]
assert "src/app/layout.rs:4:1" in msg, msg
assert "src/app.rs:4" not in msg, msg
assert "4 | pub fn seen_hunk_fingerprint(" in msg, msg
fix_uri = res0["fixes"][0]["artifactChanges"][0]["artifactLocation"]["uri"]
assert fix_uri == "src/app/layout.rs", fix_uri
fix_line = res0["fixes"][0]["artifactChanges"][0]["replacements"][0]["deletedRegion"]["startLine"]
assert fix_line == 4 and isinstance(fix_line, int)

res1 = sarif["runs"][0]["results"][1]
pl1 = res1["locations"][0]["physicalLocation"]
assert pl1["artifactLocation"]["uri"] == "file:///home/runner/work/ugly/ugly/src/app/navigation.rs", pl1
assert pl1["region"]["startLine"] == 1, pl1
assert isinstance(pl1["region"]["startLine"], int)
assert pl1["region"]["byteOffset"] != 4004, pl1
assert 'File "src/app/navigation.rs", line 1' in res1["message"]["text"], res1["message"]

# deletion passes through
res2 = sarif["runs"][0]["results"][2]
pl2 = res2["locations"][0]["physicalLocation"]
assert pl2["artifactLocation"]["uri"] == "src/calc.py", pl2
assert pl2["region"]["startLine"] == 11, pl2

# path-only artifact catalog is not a locator
assert sarif["runs"][0]["artifacts"][0]["location"]["uri"] == "src/app.rs", sarif["runs"][0]["artifacts"]

clang = next(v for v in json_vals if isinstance(v, list) and v and v[0].get("kind") == "error")
caret = clang[0]["locations"][0]["caret"]
assert caret["file"] == "src/app/layout.rs", caret
assert caret["line"] == 4 and isinstance(caret["line"], int)
assert caret["offset"] != 120, caret
rng = clang[0]["locations"][0]["ranges"][0]
assert rng["start"]["file"] == "src/app/layout.rs"
assert rng["start"]["line"] == 4

sk = next(v for v in json_vals if isinstance(v, dict) and "key.diagnostics" in v)
d0 = sk["key.diagnostics"][0]
assert d0["key.line"] != 12, d0
assert d0["key.filepath"].endswith("PresenceArbiter.swift"), d0
assert isinstance(d0["key.line"], int)
assert d0["key.offset"] != 400, d0

ser = next(v for v in json_vals if isinstance(v, dict) and "diagnostics" in v and "key.diagnostics" not in v)
s0 = ser["diagnostics"][0]
assert s0["line"] == 12 and isinstance(s0["line"], int), s0
assert "KinsokuEngine.swift" in s0["filename"]
assert "KinsokuEngine.swift:12" in s0["message"]

# THE FLIP: cargo file_name + line_start is not our schema
cargo = next(v for v in json_vals if isinstance(v, dict) and v.get("reason") == "compiler-message")
span = cargo["message"]["spans"][0]
assert span["file_name"] == "src/app.rs", span
assert span["line_start"] == 4, span
assert cargo["target"]["src_path"].endswith("src/app.rs")
print("mixed assertions ok", len(json_vals), "values")
PY
pass "mixed SARIF / clang / Swift + cargo-is-not-a-locator + chatter"

echo "== 2. --trace maps on stderr, stdout stays JSON =="
trace_out="$TMP/trace.tsv"
stdout_out="$TMP/stdout.jsonl"
"$SCRIBE" --from-dir "$FROM" --to-dir "$TO" --trace < "$MIXED" > "$stdout_out" 2> "$trace_out"
grep -q $'moved\tsrc/app.rs:4' "$trace_out" || fail "trace missing app.rs move: $(cat "$trace_out")"
grep -q 'src/app/layout.rs:4' "$trace_out" || fail "trace missing layout dest: $(cat "$trace_out")"
grep -q 'Compiling ugly' "$stdout_out" || fail "stdout lost noise when tracing"
python3 -c 'import json,sys
ok=0
raw=open(sys.argv[1],encoding="utf-8").read()
dec=json.JSONDecoder()
i=0
while i<len(raw):
    while i<len(raw) and raw[i] in " \t\r\n":
        i+=1
    if i>=len(raw): break
    if raw[i] in "{[":
        dec.raw_decode(raw,i); ok+=1
        _,e=dec.raw_decode(raw,i); i=e
    else:
        i=raw.find("\n",i)+1 or len(raw)
assert ok>=4, ok
' "$stdout_out" || fail "traced stdout is not valid JSON"
pass "trace is stderr; stdout remains JSON"

echo "== 3. positional args are JSON files, not locators =="
cp "$MIXED" "$TMP/a.jsonl"
python3 - "$TMP/b.json" <<'PY'
import json, sys
open(sys.argv[1], "w").write(json.dumps({
    "version": "2.1.0",
    "runs": [{
        "tool": {"driver": {"name": "x"}},
        "results": [{
            "message": {"text": "helper"},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": "src/calc.py"},
                    "region": {"startLine": 14},
                }
            }],
        }],
    }],
}) + "\n")
PY
out="$("$SCRIBE" --from-dir "$FROM" --to-dir "$TO" "$TMP/a.jsonl" "$TMP/b.json")"
echo "$out" | grep -q 'src/app/layout.rs' || fail "log-file args missed a.jsonl rewrite"
echo "$out" | grep -q 'src/math/ops.py' || fail "log-file args missed b.json rewrite"
echo "$out" | grep -q '"startLine": 14' && fail "stale helper line left in b.json"
pass "args are extra JSON streams"

echo "== 4. identity rewrite is a no-op on a fresh SARIF locator =="
python3 - "$TMP/id.sarif" <<'PY'
import json, sys
open(sys.argv[1], "w").write(json.dumps({
    "version": "2.1.0",
    "runs": [{
        "tool": {"driver": {"name": "x"}},
        "results": [{
            "message": {"text": "def add"},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": "src/math/ops.py"},
                    "region": {"startLine": 3},
                }
            }],
        }],
    }],
}) + "\n")
PY
out="$("$SCRIBE" --from-dir "$TO" --to-dir "$TO" < "$TMP/id.sarif")"
echo "$out"
python3 -c 'import json,sys
o=json.loads(sys.argv[1])
pl=o["runs"][0]["results"][0]["locations"][0]["physicalLocation"]
assert pl["artifactLocation"]["uri"]=="src/math/ops.py"
assert pl["region"]["startLine"]==3
' "$out" || fail "identity changed an already-fresh locator: $out"
pass "same-tree identity"

echo "== 5. unique-token dir-to-dir (no shared history) =="
mkdir -p "$TMP/old/src" "$TMP/new/pkg"
printf 'UNIQUE_TOKEN_QZX = 1\nx = UNIQUE_TOKEN_QZX\n' > "$TMP/old/src/old.py"
printf 'UNIQUE_TOKEN_QZX = 1\n' > "$TMP/new/pkg/new.py"
python3 - "$TMP/tok.sarif" <<'PY'
import json, sys
open(sys.argv[1], "w").write(json.dumps({
    "version": "2.1.0",
    "runs": [{
        "tool": {"driver": {"name": "x"}},
        "results": [{
            "message": {"text": "src/old.py:1: token"},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": "src/old.py"},
                    "region": {"startLine": 1},
                }
            }],
        }],
    }],
}) + "\n")
PY
out="$("$SCRIBE" --from-dir "$TMP/old" --to-dir "$TMP/new" < "$TMP/tok.sarif")"
echo "$out"
python3 -c 'import json,sys
o=json.loads(sys.argv[1])
pl=o["runs"][0]["results"][0]["locations"][0]["physicalLocation"]
assert pl["artifactLocation"]["uri"]=="pkg/new.py" and pl["region"]["startLine"]==1, pl
assert "pkg/new.py:1" in o["runs"][0]["results"][0]["message"]["text"]
' "$out" || fail "unique token missed: $out"
pass "from-dir/to-dir unique token"

echo "== 6. pretty-printed SARIF stays pretty; NDJSON stays compact =="
python3 - "$TMP/pretty.sarif" <<'PY'
import json, sys
obj = {
    "version": "2.1.0",
    "runs": [{
        "tool": {"driver": {"name": "x"}},
        "results": [{
            "message": {"text": "see src/calc.py:3"},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": "src/app.rs"},
                    "region": {"startLine": 4, "endLine": 8},
                }
            }],
        }],
    }],
}
open(sys.argv[1], "w").write(json.dumps(obj, indent=2) + "\n")
PY
out="$("$SCRIBE" --from-dir "$FROM" --to-dir "$TO" < "$TMP/pretty.sarif")"
echo "$out"
python3 -c 'import json,sys
raw=sys.argv[1]
assert "\n" in raw.strip(), "pretty input collapsed to one line"
o=json.loads(raw)
pl=o["runs"][0]["results"][0]["locations"][0]["physicalLocation"]
assert pl["artifactLocation"]["uri"]=="src/app/layout.rs", pl
assert pl["region"]["startLine"]==4
assert isinstance(pl["region"]["startLine"], int)
assert pl["region"]["endLine"]==8
assert "src/math/ops.py:3" in o["runs"][0]["results"][0]["message"]["text"]
' "$out" || fail "pretty SARIF missed: $out"
# NDJSON two objects stay one-per-line compact
python3 - "$TMP/nd.jsonl" <<'PY'
import json, sys
a = {"kind":"error","message":"x","locations":[{"caret":{"file":"src/app.rs","line":4,"column":1,"offset":1}}]}
b = {"kind":"error","message":"y","locations":[{"caret":{"file":"src/calc.py","line":3,"column":1,"offset":1}}]}
open(sys.argv[1],"w").write(json.dumps(a)+"\n"+json.dumps(b)+"\n")
PY
ndout="$("$SCRIBE" --from-dir "$FROM" --to-dir "$TO" < "$TMP/nd.jsonl")"
python3 -c 'import json,sys
raw=sys.argv[1]
lines=[l for l in raw.splitlines() if l.strip()]
assert len(lines)==2, lines
assert "\n  " not in raw, raw
o0=json.loads(lines[0]); o1=json.loads(lines[1])
assert o0["locations"][0]["caret"]["file"]=="src/app/layout.rs"
assert o1["locations"][0]["caret"]["file"]=="src/math/ops.py"
assert o1["locations"][0]["caret"]["line"]==3
' "$ndout" || fail "NDJSON shape lost: $ndout"
pass "pretty stays pretty; NDJSON stays compact"

echo "== 7. dest path that would break a text splice =="
mkdir -p "$TMP/qfrom/src" "$TMP/qto/src"
printf 'QUOTE_MARK = 1\n' > "$TMP/qfrom/src/plain.py"
printf 'QUOTE_MARK = 1\n' > "$TMP/qto/src/quo\"te.py"
python3 - "$TMP/quote.sarif" <<'PY'
import json, sys
open(sys.argv[1], "w").write(json.dumps({
    "version": "2.1.0",
    "runs": [{
        "tool": {"driver": {"name": "x"}},
        "results": [{
            "message": {"text": "quoted dest"},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": "src/plain.py"},
                    "region": {"startLine": 1},
                }
            }],
        }],
    }],
}) + "\n")
PY
out="$("$SCRIBE" --from-dir "$TMP/qfrom" --to-dir "$TMP/qto" < "$TMP/quote.sarif")"
echo "$out"
python3 -c 'import json,sys
raw=sys.argv[1]
o=json.loads(raw)  # must parse — dest quote must be JSON-escaped
pl=o["runs"][0]["results"][0]["locations"][0]["physicalLocation"]
uri=pl["artifactLocation"]["uri"]
assert "quo" in uri and "te.py" in uri and "\"" in uri, uri
assert pl["region"]["startLine"]==1
' "$out" || fail "quote path broke JSON: $out"
pass "JSON re-serialize survives dest quote in SARIF uri"

echo "== 7b. ANSI inside rendered / message =="
python3 - "$TMP/ansi.sarif" <<'PY'
import json, sys
esc = "\x1b"
msg = (
    f"{esc}[1m{esc}[31merror{esc}[0m: no method\n"
    f"  --> {esc}[1msrc/app.rs{esc}[0m:4:1\n"
    f"   |\n"
    f"{esc}[32m 4{esc}[0m | pub fn seen_hunk_fingerprint(\n"
)
open(sys.argv[1], "w").write(json.dumps({
    "version": "2.1.0",
    "runs": [{
        "tool": {"driver": {"name": "x"}},
        "results": [{
            "message": {"text": msg},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": "src/app.rs"},
                    "region": {"startLine": 4, "startColumn": 1},
                }
            }],
        }],
    }],
}) + "\n")
PY
out="$("$SCRIBE" --from-dir "$FROM" --to-dir "$TO" < "$TMP/ansi.sarif")"
echo "$out"
python3 -c 'import json,sys
o=json.loads(sys.argv[1])
msg=o["runs"][0]["results"][0]["message"]["text"]
pl=o["runs"][0]["results"][0]["locations"][0]["physicalLocation"]
assert pl["artifactLocation"]["uri"]=="src/app/layout.rs"
plain=msg
for seq in ("\x1b[1m","\x1b[0m","\x1b[31m","\x1b[32m"):
    plain=plain.replace(seq,"")
assert "src/app/layout.rs" in plain
assert "src/app.rs:4" not in plain
# wrapping reset after the path and after the gutter number must survive
assert "\x1b[1msrc/app/layout.rs\x1b[0m:4:1" in msg, msg
assert "\x1b[32m 4\x1b[0m |" in msg, msg
' "$out" || fail "ANSI rewrite missed: $out"
pass "ANSI-wrapped locators inside message.text"

echo "== 7c. --strict exits 1 when a locator cannot be read =="
python3 - "$TMP/missing.sarif" <<'PY'
import json, sys
open(sys.argv[1], "w").write(json.dumps({
    "version": "2.1.0",
    "runs": [{
        "tool": {"driver": {"name": "x"}},
        "results": [{
            "message": {"text": "ghost"},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": "src/does-not-exist.rs"},
                    "region": {"startLine": 1},
                }
            }],
        }],
    }],
}) + "\n")
PY
set +e
"$SCRIBE" --from-dir "$FROM" --to-dir "$TO" --strict < "$TMP/missing.sarif" > "$TMP/strict.out" 2> "$TMP/strict.err"
rc=$?
set -e
[[ "$rc" -eq 1 ]] || fail "--strict should exit 1, got $rc stdout=$(cat "$TMP/strict.out") err=$(cat "$TMP/strict.err")"
# confirmed deletion is not an error
python3 - "$TMP/del.sarif" <<'PY'
import json, sys
open(sys.argv[1], "w").write(json.dumps({
    "version": "2.1.0",
    "runs": [{
        "tool": {"driver": {"name": "x"}},
        "results": [{
            "message": {"text": "gone"},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": "src/calc.py"},
                    "region": {"startLine": 11},
                }
            }],
        }],
    }],
}) + "\n")
PY
"$SCRIBE" --from-dir "$FROM" --to-dir "$TO" --strict < "$TMP/del.sarif" >/dev/null \
  || fail "--strict should pass on a confirmed deletion"
pass "--strict unresolved=1; deletion is an answer"

# --- real repo dogfood: copies of kizu / sitbone / voidtrace ---
copy_tree() {
  local repo="$1" ref="$2" dest="$3"
  mkdir -p "$dest"
  git -C "$repo" archive "$ref" | tar -x -C "$dest"
}

KIZU="${KIZU:-/Users/annenpolka/ghq/github.com/annenpolka/kizu}"
if [[ -d "$KIZU/.git" || -f "$KIZU/.git" ]]; then
  echo "== 8. kizu SARIF: app.rs split (b4e6a5d → HEAD) =="
  copy_tree "$KIZU" b4e6a5d "$TMP/kizu-from"
  copy_tree "$KIZU" HEAD "$TMP/kizu-to"
  klog="$TMP/kizu.sarif"
  python3 - "$klog" <<'PY'
import json, sys
sarif = {
    "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
    "version": "2.1.0",
    "runs": [{
        "tool": {"driver": {"name": "rustc", "rules": [{"id": "E0599"}]}},
        "results": [
            {
                "ruleId": "E0599",
                "level": "error",
                "message": {
                    "text": (
                        "error[E0599]: no method named seen_hunk_fingerprint\n"
                        "  --> /home/runner/work/kizu/kizu/src/app.rs:529:5\n"
                        "   |\n"
                        "529 | pub fn seen_hunk_fingerprint(\n"
                    )
                },
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": "file:///home/runner/work/kizu/kizu/src/app.rs"
                        },
                        "region": {
                            "startLine": 529,
                            "startColumn": 5,
                            "endLine": 529,
                            "endColumn": 28,
                            "byteOffset": 18000,
                            "charOffset": 18000,
                            "snippet": {"text": "pub fn seen_hunk_fingerprint("},
                        },
                    }
                }],
            },
            {
                "ruleId": "landing",
                "message": {"text": 'File "src/app.rs", line 543, in nearest_landing_forward'},
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": {"uri": "src/app.rs"},
                        "region": {"startLine": 543, "startColumn": 1, "byteOffset": 19000},
                    }
                }],
            },
        ],
    }],
}
open(sys.argv[1], "w").write(json.dumps(sarif, indent=2) + "\n")
PY
  rewritten="$("$SCRIBE" --from-dir "$TMP/kizu-from" --to-dir "$TMP/kizu-to" < "$klog")"
  echo "$rewritten"
  python3 - "$rewritten" <<'PY' || fail "kizu SARIF assertions failed"
import json, sys
raw = sys.argv[1]
assert "\n" in raw.strip(), "pretty kizu SARIF collapsed"
o = json.loads(raw)
pl = o["runs"][0]["results"][0]["locations"][0]["physicalLocation"]
assert pl["artifactLocation"]["uri"] == "file:///home/runner/work/kizu/kizu/src/app/layout.rs", pl
assert pl["region"]["startLine"] == 17, pl
assert isinstance(pl["region"]["startLine"], int)
assert "src/app.rs" not in pl["artifactLocation"]["uri"]
ren = o["runs"][0]["results"][0]["message"]["text"]
assert "src/app/layout.rs:17:5" in ren or "src/app/layout.rs:17" in ren, ren
assert "src/app.rs:529" not in ren
assert "529 | pub fn seen_hunk_fingerprint(" not in ren, ren
assert "17 | pub fn seen_hunk_fingerprint(" in ren, ren
assert pl["region"]["byteOffset"] != 18000, pl
assert isinstance(pl["region"]["byteOffset"], int) and pl["region"]["byteOffset"] > 0
assert pl["region"]["snippet"]["text"].startswith("pub fn seen_hunk_fingerprint(")
nav = o["runs"][0]["results"][1]
npl = nav["locations"][0]["physicalLocation"]
assert npl["artifactLocation"]["uri"] == "src/app/navigation.rs", npl
assert npl["region"]["startLine"] == 22, npl
assert 'File "src/app/navigation.rs", line' in nav["message"]["text"]
print("kizu ok", pl["artifactLocation"]["uri"], pl["region"]["startLine"])
PY
  pass "kizu SARIF via directory copies (app.rs:529 → layout.rs:17)"

  echo "== 8b. kizu read-only working tree as --to-dir =="
  rewritten="$("$SCRIBE" --from-dir "$TMP/kizu-from" --to-dir "$KIZU" < "$klog")"
  echo "$rewritten" | grep -q 'src/app/layout.rs' || fail "kizu live tree missed layout.rs: $rewritten"
  pass "kizu live working tree as to-dir"

  echo "== 8c. kizu clang JSON array of the same locator =="
  python3 - "$TMP/kizu-clang.json" <<'PY'
import json, sys
arr = [{
    "kind": "error",
    "message": "no method named seen_hunk_fingerprint at src/app.rs:529:5",
    "locations": [{
        "caret": {
            "file": "/home/runner/work/kizu/kizu/src/app.rs",
            "line": 529,
            "column": 5,
            "offset": 18000,
        }
    }],
}]
open(sys.argv[1], "w").write(json.dumps(arr) + "\n")
PY
  rewritten="$("$SCRIBE" --from-dir "$TMP/kizu-from" --to-dir "$TMP/kizu-to" < "$TMP/kizu-clang.json")"
  echo "$rewritten"
  python3 -c 'import json,sys
o=json.loads(sys.argv[1])
c=o[0]["locations"][0]["caret"]
assert c["file"].endswith("src/app/layout.rs"), c
assert c["line"]==17 and isinstance(c["line"], int)
assert c["offset"]!=18000
assert "layout.rs:17" in o[0]["message"]
' "$rewritten" || fail "kizu clang missed: $rewritten"
  pass "kizu clang JSON array"
else
  echo "SKIP kizu dogfood (repo not present at $KIZU)"
fi

SIT="${SIT:-/Users/annenpolka/ghq/github.com/annenpolka/sitbone}"
if [[ -d "$SIT/.git" || -f "$SIT/.git" ]]; then
  echo "== 9. sitbone Swift SourceKit JSON: detect() 45 → 75 =="
  copy_tree "$SIT" a95da43 "$TMP/sit-from"
  copy_tree "$SIT" HEAD "$TMP/sit-to"
  slog="$TMP/sit.json"
  python3 - "$slog" <<'PY'
import json, sys
doc = {
    "key.diagnostics": [
        {
            "key.severity": "source.diagnostic.severity.error",
            "key.line": 45,
            "key.column": 17,
            "key.filepath": "Sources/SitboneCore/PresenceArbiter.swift",
            "key.description": "cannot find 'threshold' in scope",
            "key.offset": 1200,
        },
        {
            "key.severity": "source.diagnostic.severity.error",
            "key.line": 45,
            "key.column": 17,
            "key.filepath": "PresenceArbiter.swift",
            "key.description": "PresenceArbiter.swift:45:17: error: cannot find 'threshold' in scope",
        },
    ]
}
# also a serialized-diag record
ser = {
    "diagnostics": [{
        "level": "error",
        "filename": "/Users/runner/work/sitbone/sitbone/Sources/SitboneCore/PresenceArbiter.swift",
        "line": 45,
        "column": 17,
        "offset": 1200,
        "spelling": "cannot find 'threshold' in scope",
        "message": "timeout:5 and retry:3 see http://127.0.0.1:9090/metrics",
    }]
}
open(sys.argv[1], "w").write(json.dumps(doc) + "\n" + json.dumps(ser) + "\n")
PY
  rewritten="$("$SCRIBE" --from-dir "$TMP/sit-from" --to-dir "$TMP/sit-to" < "$slog")"
  echo "$rewritten"
  python3 - "$rewritten" <<'PY' || fail "sitbone Swift assertions failed"
import json, sys
rows = []
dec = json.JSONDecoder()
raw = sys.argv[1]
i = 0
while i < len(raw):
    while i < len(raw) and raw[i] in " \t\r\n":
        i += 1
    if i >= len(raw):
        break
    val, end = dec.raw_decode(raw, i)
    rows.append(val)
    i = end
sk = next(r for r in rows if "key.diagnostics" in r)
d1 = sk["key.diagnostics"][0]
assert d1["key.line"] != 45, d1
assert d1["key.filepath"].endswith("PresenceArbiter.swift"), d1
assert isinstance(d1["key.line"], int)
d2 = sk["key.diagnostics"][1]
assert ":45:" not in d2["key.description"], d2
ser = next(r for r in rows if "diagnostics" in r)
s0 = ser["diagnostics"][0]
assert s0["line"] != 45, s0
assert s0["message"] == "timeout:5 and retry:3 see http://127.0.0.1:9090/metrics"
print("sitbone ok", d1["key.line"])
PY
  pass "sitbone Swift SourceKit + serialized-diag"

  echo "== 9b. sitbone read-only working tree as --to-dir =="
  rewritten="$("$SCRIBE" --from-dir "$TMP/sit-from" --to-dir "$SIT" < "$slog")"
  echo "$rewritten" | grep -q ':45' && fail "sitbone live tree still on 45: $rewritten"
  pass "sitbone live working tree as to-dir"
else
  echo "SKIP sitbone dogfood (repo not present at $SIT)"
fi

VT="${VT:-/Users/annenpolka/ghq/github.com/annenpolka/voidtrace}"
if [[ -d "$VT/.git" || -f "$VT/.git" ]]; then
  echo "== 10. voidtrace SARIF: evaluate.ts identity, no import{ jump =="
  copy_tree "$VT" HEAD "$TMP/vt-from"
  copy_tree "$VT" HEAD "$TMP/vt-to"
  vlog="$TMP/vt.sarif"
  python3 - "$vlog" <<'PY'
import json, sys
sarif = {
    "version": "2.1.0",
    "runs": [{
        "tool": {"driver": {"name": "tsc"}},
        "results": [
            {
                "ruleId": "unique",
                "message": {"text": "KERNEL_ENGINE_VERSION"},
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": {"uri": "packages/kernel/src/evaluate.ts"},
                        "region": {"startLine": 40},
                    }
                }],
            },
            {
                "ruleId": "import-clone",
                "message": {"text": "import {"},
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": {"uri": "packages/kernel/src/evaluate.ts"},
                        "region": {"startLine": 1},
                    }
                }],
            },
        ],
    }],
}
open(sys.argv[1], "w").write(json.dumps(sarif) + "\n")
PY
  rewritten="$("$SCRIBE" --from-dir "$TMP/vt-from" --to-dir "$TMP/vt-to" < "$vlog")"
  echo "$rewritten"
  python3 -c 'import json,sys
o=json.loads(sys.argv[1])
a=o["runs"][0]["results"][0]["locations"][0]["physicalLocation"]
b=o["runs"][0]["results"][1]["locations"][0]["physicalLocation"]
assert a["artifactLocation"]["uri"]=="packages/kernel/src/evaluate.ts", a
assert a["region"]["startLine"]==40, a
assert b["artifactLocation"]["uri"]=="packages/kernel/src/evaluate.ts", b
assert b["region"]["startLine"]==1, b
# must not jump to cli.test.ts / cli.ts clones
assert "cli.ts" not in json.dumps(o)
' "$rewritten" || fail "voidtrace identity jumped: $rewritten"
  pass "voidtrace evaluate.ts identity (no leftover-name jump)"
else
  echo "SKIP voidtrace dogfood (repo not present at $VT)"
fi

echo
echo "All demo checks passed."
exit 0
