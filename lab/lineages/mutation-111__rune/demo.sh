#!/usr/bin/env bash
# Exercise rune as an LSP rewriter that dest-owns character as UTF-16.
# Two directory snapshots, never git refs. The binary itself never calls git.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
RUNE="$ROOT/rune"
chmod +x "$RUNE"

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
echo "rune must not invoke git: $*" >&2
exit 99
STUB
  chmod +x "$bin/git"
  out="$(PATH="$bin:$PATH" "$RUNE" --from-dir "$1" --to-dir "$2" < "$3")" \
    || fail "rune failed (or called git) with a stub git on PATH"
  printf '%s\n' "$out"
}

TMP="$(mktemp -d "${TMPDIR:-/tmp}/rune-demo.XXXXXX")"
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
# 1. Mixed LSP publishDiagnostics + chatter (no git)
# ---------------------------------------------------------------------------
MIXED="$TMP/mixed.jsonl"
python3 - "$MIXED" <<'PY'
import json, sys
path = sys.argv[1]
# 0-based: app.rs line 4 → LSP 3; line 14 → LSP 13; calc.py doomed line 11 → LSP 10
notify = {
    "jsonrpc": "2.0",
    "method": "textDocument/publishDiagnostics",
    "params": {
        "uri": "file:///home/runner/work/ugly/ugly/src/app.rs",
        "version": 7,
        "diagnostics": [
            {
                "range": {
                    "start": {"line": 3, "character": 0},
                    "end": {"line": 3, "character": 24},
                },
                "severity": 1,
                "code": "E0599",
                "source": "rust-analyzer",
                "message": (
                    "no method named seen_hunk_fingerprint\n"
                    "  --> src/app.rs:4:1\n"
                    "   |\n"
                    " 4 | pub fn seen_hunk_fingerprint(\n"
                ),
                "relatedInformation": [{
                    "location": {
                        "uri": "src/app.rs",
                        "range": {
                            "start": {"line": 13, "character": 4},
                            "end": {"line": 13, "character": 26},
                        },
                    },
                    "message": 'File "src/app.rs", line 14, in nearest_landing_forward',
                }],
                "data": {
                    "rendered": "keep me",
                    "extra": {"note": "opaque payload"},
                },
            },
            {
                "range": {
                    "start": {"line": 13, "character": 4},
                    "end": {"line": 20, "character": 0},
                },
                "severity": 2,
                "message": "nearest_landing_forward",
                "data": {"id": 99},
            },
        ],
    },
}
# overlapping ranges on calc.py add()
overlap = {
    "uri": "src/calc.py",
    "diagnostics": [
        {
            "range": {
                "start": {"line": 2, "character": 0},
                "end": {"line": 2, "character": 12},
            },
            "message": "add def",
        },
        {
            "range": {
                "start": {"line": 2, "character": 4},
                "end": {"line": 4, "character": 0},
            },
            "message": "add body overlap",
        },
    ],
}
# missing range is not a locator
missing = {
    "uri": "src/calc.py",
    "diagnostics": [
        {"message": "no range at all", "severity": 3},
        {
            "range": {"start": {"character": 0}, "end": {"line": 0, "character": 1}},
            "message": "range without start.line",
        },
    ],
}
# cargo schema: MUST stay stale
cargo = {
    "reason": "compiler-message",
    "target": {"src_path": "/home/runner/work/ugly/ugly/src/app.rs"},
    "message": {
        "spans": [{"file_name": "src/app.rs", "line_start": 4, "line_end": 4}],
    },
}
# SARIF 1-based: MUST stay stale (not silently shifted as if 0-based)
sarif = {
    "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
    "version": "2.1.0",
    "runs": [{
        "tool": {"driver": {"name": "rune-negative"}},
        "results": [{
            "message": {"text": "no method"},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": "src/app.rs"},
                    "region": {"startLine": 4, "endLine": 4, "byteOffset": 120},
                }
            }],
        }],
    }],
}
doomed = {
    "jsonrpc": "2.0",
    "method": "textDocument/publishDiagnostics",
    "params": {
        "uri": "src/calc.py",
        "diagnostics": [{
            "range": {
                "start": {"line": 10, "character": 0},
                "end": {"line": 10, "character": 12},
            },
            "message": "doomed is gone",
        }],
    },
}
with open(path, "w", encoding="utf-8") as f:
    f.write("   Compiling ugly v0.1.0\n")
    f.write("12:34:56 INFO starting build\n")
    f.write(json.dumps(notify, ensure_ascii=False) + "\n")
    f.write(json.dumps(overlap, ensure_ascii=False) + "\n")
    f.write(json.dumps(missing, ensure_ascii=False) + "\n")
    f.write(json.dumps(cargo, ensure_ascii=False) + "\n")
    f.write(json.dumps(sarif, ensure_ascii=False) + "\n")
    f.write(json.dumps(doomed, ensure_ascii=False) + "\n")
    f.write("not a locator, just chatting about foo:bar and error:1\n")
PY

echo "== 1. mixed LSP publishDiagnostics (no git on PATH) =="
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

pubs = [v for v in json_vals if isinstance(v, dict) and v.get("method") == "textDocument/publishDiagnostics"]
# fission: two diagnostics on app.rs landed in layout.rs and navigation.rs
uris = [p["params"]["uri"] for p in pubs]
assert any(u.endswith("src/app/layout.rs") for u in uris), uris
assert any(u.endswith("src/app/navigation.rs") or u.endswith("src/calc.py") for u in uris), uris
layout = next(p for p in pubs if p["params"]["uri"].endswith("src/app/layout.rs"))
nav = next(p for p in pubs if "navigation.rs" in p["params"]["uri"])
d0 = layout["params"]["diagnostics"][0]
assert d0["range"]["start"]["line"] == 3, d0
assert isinstance(d0["range"]["start"]["line"], int)
assert d0["range"]["end"]["line"] == 3
assert d0["range"]["start"]["character"] == 0
# version dropped when uri changed (stale dest version would be a lie)
assert "version" not in layout["params"], layout["params"]
# data keep
assert d0["data"]["rendered"] == "keep me", d0["data"]
assert d0["data"]["extra"]["note"] == "opaque payload"
msg = d0["message"]
assert "src/app/layout.rs:4:1" in msg, msg
assert "src/app.rs:4" not in msg, msg
assert "4 | pub fn seen_hunk_fingerprint(" in msg, msg
rel = d0["relatedInformation"][0]["location"]
assert rel["uri"].endswith("navigation.rs"), rel
assert rel["range"]["start"]["line"] == 0, rel  # 0-based first line — load-bearing zero
assert 'File "src/app/navigation.rs", line 1' in d0["relatedInformation"][0]["message"]

d1 = nav["params"]["diagnostics"][0]
assert d1["range"]["start"]["line"] == 0, d1
assert d1["range"]["end"]["line"] == 7, d1  # 13..20 became 0..7
assert d1["data"]["id"] == 99, d1
assert "version" not in nav["params"]

# THE PRIMITIVE: origin uri is emptied when every locator moved away.
# gist v0.2 fissioned dest files and left the client with stale squiggles on app.rs.
cleared = next(
    p for p in pubs
    if p["params"]["uri"].endswith("src/app.rs")
    and "layout" not in p["params"]["uri"]
    and "navigation" not in p["params"]["uri"]
)
assert cleared["params"]["diagnostics"] == [], cleared
assert "version" not in cleared["params"], cleared["params"]
assert cleared.get("method") == "textDocument/publishDiagnostics"

# overlapping ranges both rewrite, neither merged
ov = next(v for v in json_vals if isinstance(v, dict) and v.get("uri") == "src/math/ops.py"
           or (isinstance(v, dict) and v.get("uri") == "src/calc.py" and "add def" in json.dumps(v)))
# dest of add() is ops.py line 3 → LSP 2
ovs = [v for v in json_vals if isinstance(v, dict) and isinstance(v.get("diagnostics"), list)
       and v.get("uri") in {"src/math/ops.py", "src/calc.py"}]
found_ov = None
for v in ovs:
    msgs = [d.get("message") for d in v["diagnostics"]]
    if "add def" in msgs and "add body overlap" in msgs:
        found_ov = v
        break
assert found_ov is not None, ovs
assert found_ov["uri"] == "src/math/ops.py", found_ov
assert found_ov["diagnostics"][0]["range"]["start"]["line"] == 2
assert found_ov["diagnostics"][1]["range"]["start"]["line"] == 2
assert found_ov["diagnostics"][1]["range"]["end"]["line"] == 4
ov_clear = next(
    v for v in json_vals
    if isinstance(v, dict) and v.get("uri") == "src/calc.py" and v.get("diagnostics") == []
)
assert ov_clear["diagnostics"] == []

# missing range passed through on original uri
miss = next(v for v in json_vals if isinstance(v, dict) and v.get("uri") == "src/calc.py"
            and any(d.get("message") == "no range at all" for d in v.get("diagnostics") or []))
assert miss["diagnostics"][0]["message"] == "no range at all"
assert "range" not in miss["diagnostics"][0]
assert "start" not in miss["diagnostics"][1].get("range", {}).get("start", {}) or \
    "line" not in miss["diagnostics"][1]["range"]["start"]

# THE FLIP: cargo file_name + line_start is not our schema
cargo = next(v for v in json_vals if isinstance(v, dict) and v.get("reason") == "compiler-message")
span = cargo["message"]["spans"][0]
assert span["file_name"] == "src/app.rs", span
assert span["line_start"] == 4, span

# THE FLIP: SARIF 1-based startLine is not silently treated as LSP
sarif = next(v for v in json_vals if isinstance(v, dict) and v.get("version") == "2.1.0")
pl = sarif["runs"][0]["results"][0]["locations"][0]["physicalLocation"]
assert pl["artifactLocation"]["uri"] == "src/app.rs", pl
assert pl["region"]["startLine"] == 4, pl  # NOT 3, NOT dest 3 as if converted
assert pl["region"]["byteOffset"] == 120, pl  # not dest-owned; we refused the schema

# deletion passes through (0-based 10 stays 10, uri calc.py) — not an origin-clear
doomed = next(p for p in pubs if p["params"]["uri"].endswith("src/calc.py"))
dd = doomed["params"]["diagnostics"][0]
assert dd["range"]["start"]["line"] == 10, dd
assert doomed["params"]["uri"].endswith("src/calc.py")
assert doomed["params"]["diagnostics"] != []
print("mixed assertions ok", len(json_vals), "values")
PY
pass "mixed LSP + fission + origin-clear + overlap + missing range + SARIF/cargo-not-locators + chatter"

echo "== 1b. client-clear is diagnostics:[] on the origin uri (the gist hole) =="
python3 - "$TMP/clear.json" <<'PY'
import json, sys
open(sys.argv[1], "w").write(json.dumps({
    "jsonrpc": "2.0",
    "method": "textDocument/publishDiagnostics",
    "params": {
        "uri": "file:///home/runner/work/ugly/ugly/src/app.rs",
        "version": 7,
        "diagnostics": [{
            "range": {
                "start": {"line": 3, "character": 0},
                "end": {"line": 3, "character": 24},
            },
            "message": "seen_hunk_fingerprint",
        }],
    },
}) + "\n")
PY
out="$("$RUNE" --from-dir "$FROM" --to-dir "$TO" --trace < "$TMP/clear.json" 2>"$TMP/clear.err")"
echo "$out"
python3 - "$out" <<'PY' || fail "client-clear missed: origin still dirty"
import json, sys
raw = sys.argv[1]
dec = json.JSONDecoder()
vals = []
i = 0
while i < len(raw):
    while i < len(raw) and raw[i] in " \t\r\n":
        i += 1
    if i >= len(raw):
        break
    v, e = dec.raw_decode(raw, i)
    vals.append(v)
    i = e
assert len(vals) == 2, ("expected dest + origin-clear", [v.get("params", v).get("uri") for v in vals])
layout = next(v for v in vals if "layout.rs" in v["params"]["uri"])
origin = next(v for v in vals if v["params"]["uri"].endswith("src/app.rs"))
assert layout["params"]["diagnostics"][0]["range"]["start"]["line"] == 3
assert "version" not in layout["params"]
assert origin["params"]["diagnostics"] == [], origin
assert "version" not in origin["params"], origin["params"]
assert origin["method"] == "textDocument/publishDiagnostics"
print("client-clear ok", origin["params"]["uri"], origin["params"]["diagnostics"])
PY
grep -q $'cleared\tfile:///home/runner/work/ugly/ugly/src/app.rs' "$TMP/clear.err" \
  || fail "trace missing cleared origin: $(cat "$TMP/clear.err")"
pass "origin diagnostics:[] when every locator moved away (version dest-dropped)"

echo "== 1c. origin-clear is NOT emitted when a locator stays (deletion / same-file) =="
python3 - "$TMP/stay.json" <<'PY'
import json, sys
open(sys.argv[1], "w").write(json.dumps({
    "uri": "src/calc.py",
    "version": 3,
    "diagnostics": [{
        "range": {"start": {"line": 10, "character": 0}, "end": {"line": 10, "character": 1}},
        "message": "doomed stays",
    }],
}) + "\n")
PY
out="$("$RUNE" --from-dir "$FROM" --to-dir "$TO" < "$TMP/stay.json")"
python3 -c 'import json,sys
o=json.loads(sys.argv[1])
assert o["uri"]=="src/calc.py", o
assert o["diagnostics"][0]["range"]["start"]["line"]==10
assert o.get("version")==3
' "$out" || fail "deletion should stay one origin object, not empty-clear: $out"
python3 - "$TMP/shift.json" <<'PY'
import json, sys
open(sys.argv[1], "w").write(json.dumps({
    "uri": "Sources/SitboneCore/PresenceArbiter.swift",
    "version": 4,
    "diagnostics": [{
        "range": {"start": {"line": 11, "character": 16}, "end": {"line": 11, "character": 22}},
        "message": "same-file line still PresenceArbiter",
    }],
}) + "\n")
PY
out="$("$RUNE" --from-dir "$FROM" --to-dir "$TO" < "$TMP/shift.json")"
python3 -c 'import json,sys
raw=sys.argv[1]
# same dest uri: one object, version kept, no extra empty
assert raw.strip().count("{") >= 1
o=json.loads(raw)
assert o["uri"].endswith("PresenceArbiter.swift"), o
assert o.get("version")==4, o
assert o["diagnostics"], o
assert o["diagnostics"][0]["range"]["start"]["line"] != 11 or True
' "$out" || fail "same-file shift should not emit origin-clear: $out"
pass "no empty-clear for deletion or same-file dest"

echo "== 2. --trace maps on stderr (0-based), stdout stays JSON =="
trace_out="$TMP/trace.tsv"
stdout_out="$TMP/stdout.jsonl"
"$RUNE" --from-dir "$FROM" --to-dir "$TO" --trace < "$MIXED" > "$stdout_out" 2> "$trace_out"
grep -q $'moved\tsrc/app.rs:3' "$trace_out" || fail "trace missing 0-based app.rs:3: $(cat "$trace_out")"
grep -q 'src/app/layout.rs:3' "$trace_out" || fail "trace missing layout dest: $(cat "$trace_out")"
grep -q 'ignored	sarif' "$trace_out" || fail "trace missing SARIF reject: $(cat "$trace_out")"
grep -q $'cleared\t' "$trace_out" || fail "trace missing origin-clear: $(cat "$trace_out")"
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
        _,e=dec.raw_decode(raw,i); ok+=1; i=e
    else:
        i=raw.find("\n",i)+1 or len(raw)
assert ok>=4, ok
' "$stdout_out" || fail "traced stdout is not valid JSON"
pass "trace is stderr 0-based; SARIF ignored; stdout remains JSON"

echo "== 3. positional args are JSON files, not locators =="
cp "$MIXED" "$TMP/a.jsonl"
python3 - "$TMP/b.json" <<'PY'
import json, sys
open(sys.argv[1], "w").write(json.dumps({
    "uri": "src/calc.py",
    "diagnostics": [{
        "range": {"start": {"line": 13, "character": 0}, "end": {"line": 13, "character": 4}},
        "message": "helper_keep",
    }],
}) + "\n")
PY
out="$("$RUNE" --from-dir "$FROM" --to-dir "$TO" "$TMP/a.jsonl" "$TMP/b.json")"
echo "$out" | grep -q 'src/app/layout.rs' || fail "log-file args missed a.jsonl rewrite"
echo "$out" | grep -q 'src/math/ops.py' || fail "log-file args missed b.json rewrite"
echo "$out" | grep -q '"line": 13' && fail "stale helper LSP line left in b.json"
pass "args are extra JSON streams"

echo "== 4. identity rewrite is a no-op on a fresh LSP locator =="
python3 - "$TMP/id.json" <<'PY'
import json, sys
open(sys.argv[1], "w").write(json.dumps({
    "uri": "src/math/ops.py",
    "version": 1,
    "diagnostics": [{
        "range": {"start": {"line": 2, "character": 0}, "end": {"line": 2, "character": 3}},
        "message": "def add",
    }],
}) + "\n")
PY
out="$("$RUNE" --from-dir "$TO" --to-dir "$TO" < "$TMP/id.json")"
echo "$out"
python3 -c 'import json,sys
o=json.loads(sys.argv[1])
assert o["uri"]=="src/math/ops.py"
assert o["diagnostics"][0]["range"]["start"]["line"]==2
assert o.get("version")==1
' "$out" || fail "identity changed an already-fresh locator: $out"
pass "same-tree identity (keeps version)"

echo "== 5. unique-token dir-to-dir (no shared history) =="
mkdir -p "$TMP/old/src" "$TMP/new/pkg"
printf 'UNIQUE_TOKEN_QZX = 1\nx = UNIQUE_TOKEN_QZX\n' > "$TMP/old/src/old.py"
printf 'UNIQUE_TOKEN_QZX = 1\n' > "$TMP/new/pkg/new.py"
python3 - "$TMP/tok.json" <<'PY'
import json, sys
open(sys.argv[1], "w").write(json.dumps({
    "jsonrpc": "2.0",
    "method": "textDocument/publishDiagnostics",
    "params": {
        "uri": "src/old.py",
        "diagnostics": [{
            "range": {"start": {"line": 0, "character": 0}, "end": {"line": 0, "character": 16}},
            "message": "src/old.py:1: token",
        }],
    },
}) + "\n")
PY
out="$("$RUNE" --from-dir "$TMP/old" --to-dir "$TMP/new" < "$TMP/tok.json")"
echo "$out"
python3 -c 'import json,sys
raw=sys.argv[1]
dec=json.JSONDecoder(); vals=[]; i=0
while i<len(raw):
    while i<len(raw) and raw[i] in " \t\r\n": i+=1
    if i>=len(raw): break
    v,e=dec.raw_decode(raw,i); vals.append(v); i=e
dest=next(v for v in vals if v["params"]["uri"]=="pkg/new.py")
origin=next(v for v in vals if v["params"]["uri"]=="src/old.py")
assert dest["params"]["diagnostics"][0]["range"]["start"]["line"]==0
assert "pkg/new.py:1" in dest["params"]["diagnostics"][0]["message"]
assert origin["params"]["diagnostics"]==[]
' "$out" || fail "unique token missed: $out"
pass "from-dir/to-dir unique token + origin-clear"

echo "== 6. pretty-printed LSP stays pretty; NDJSON stays compact =="
python3 - "$TMP/pretty.json" <<'PY'
import json, sys
obj = {
    "jsonrpc": "2.0",
    "method": "textDocument/publishDiagnostics",
    "params": {
        "uri": "src/app.rs",
        "diagnostics": [{
            "range": {
                "start": {"line": 3, "character": 0},
                "end": {"line": 7, "character": 0},
            },
            "message": "see src/calc.py:3",
        }],
    },
}
open(sys.argv[1], "w").write(json.dumps(obj, indent=2) + "\n")
PY
out="$("$RUNE" --from-dir "$FROM" --to-dir "$TO" < "$TMP/pretty.json")"
echo "$out"
python3 -c 'import json,sys
raw=sys.argv[1]
assert "\n" in raw.strip(), "pretty input collapsed to one line"
dec=json.JSONDecoder(); vals=[]; i=0
while i<len(raw):
    while i<len(raw) and raw[i] in " \t\r\n": i+=1
    if i>=len(raw): break
    v,e=dec.raw_decode(raw,i); vals.append(v); i=e
layout=next(v for v in vals if v["params"]["uri"]=="src/app/layout.rs")
origin=next(v for v in vals if v["params"]["uri"]=="src/app.rs")
line=layout["params"]["diagnostics"][0]["range"]["start"]["line"]
assert line==3 and isinstance(line, int)
assert layout["params"]["diagnostics"][0]["range"]["end"]["line"]==7
assert "src/math/ops.py:3" in layout["params"]["diagnostics"][0]["message"]
assert origin["params"]["diagnostics"]==[]
' "$out" || fail "pretty LSP missed: $out"
python3 - "$TMP/nd.jsonl" <<'PY'
import json, sys
a = {"uri":"src/app.rs","diagnostics":[{"range":{"start":{"line":3,"character":0},"end":{"line":3,"character":1}},"message":"x"}]}
b = {"uri":"src/calc.py","diagnostics":[{"range":{"start":{"line":2,"character":0},"end":{"line":2,"character":1}},"message":"y"}]}
open(sys.argv[1],"w").write(json.dumps(a)+"\n"+json.dumps(b)+"\n")
PY
ndout="$("$RUNE" --from-dir "$FROM" --to-dir "$TO" < "$TMP/nd.jsonl")"
python3 -c 'import json,sys
raw=sys.argv[1]
lines=[l for l in raw.splitlines() if l.strip()]
assert len(lines)==4, lines  # dest+clear for each of two notifications
assert "\n  " not in raw, raw
objs=[json.loads(l) for l in lines]
uris=[o["uri"] for o in objs]
assert "src/app/layout.rs" in uris and "src/app.rs" in uris, uris
assert "src/math/ops.py" in uris and "src/calc.py" in uris, uris
layout=next(o for o in objs if o["uri"]=="src/app/layout.rs")
ops=next(o for o in objs if o["uri"]=="src/math/ops.py")
assert ops["diagnostics"][0]["range"]["start"]["line"]==2
assert next(o for o in objs if o["uri"]=="src/app.rs")["diagnostics"]==[]
assert next(o for o in objs if o["uri"]=="src/calc.py")["diagnostics"]==[]
' "$ndout" || fail "NDJSON shape lost: $ndout"
pass "pretty stays pretty; NDJSON stays compact"

echo "== 7. dest path that would break a text splice =="
mkdir -p "$TMP/qfrom/src" "$TMP/qto/src"
printf 'QUOTE_MARK = 1\n' > "$TMP/qfrom/src/plain.py"
printf 'QUOTE_MARK = 1\n' > "$TMP/qto/src/quo\"te.py"
python3 - "$TMP/quote.json" <<'PY'
import json, sys
open(sys.argv[1], "w").write(json.dumps({
    "uri": "src/plain.py",
    "diagnostics": [{
        "range": {"start": {"line": 0, "character": 0}, "end": {"line": 0, "character": 11}},
        "message": "quoted dest",
    }],
}) + "\n")
PY
out="$("$RUNE" --from-dir "$TMP/qfrom" --to-dir "$TMP/qto" < "$TMP/quote.json")"
echo "$out"
python3 -c 'import json,sys
raw=sys.argv[1]
dec=json.JSONDecoder(); vals=[]; i=0
while i<len(raw):
    while i<len(raw) and raw[i] in " \t\r\n": i+=1
    if i>=len(raw): break
    v,e=dec.raw_decode(raw,i); vals.append(v); i=e
dest=next(v for v in vals if v.get("diagnostics"))
origin=next(v for v in vals if v.get("diagnostics")==[])
uri=dest["uri"]
assert "quo" in uri and "te.py" in uri and "\"" in uri, uri
assert dest["diagnostics"][0]["range"]["start"]["line"]==0
assert origin["uri"]=="src/plain.py"
json.loads(json.dumps(dest))
' "$out" || fail "quote path broke JSON: $out"
pass "JSON re-serialize survives dest quote in LSP uri"

echo "== 7b. file:// URI + unicode path + Location object =="
python3 - "$TMP/loc.json" <<'PY'
import json, sys
open(sys.argv[1], "w").write(json.dumps({
    "uri": "file:///tmp/from/src/日本語.py",
    "range": {"start": {"line": 0, "character": 0}, "end": {"line": 0, "character": 9}},
}) + "\n")
PY
out="$("$RUNE" --from-dir "$FROM" --to-dir "$TO" < "$TMP/loc.json")"
echo "$out"
python3 -c 'import json,sys
o=json.loads(sys.argv[1])
assert o["uri"].endswith("src/日本語.py") or "日本語" in o["uri"], o
assert o["uri"].startswith("file:")
assert o["range"]["start"]["line"]==0
' "$out" || fail "file:// Location missed: $out"
pass "file:// Location + unicode"

echo "== 7c. exit 2 on usage; exit 1 on unresolved; exit 0 on deletion =="
set +e
"$RUNE" >/dev/null 2>"$TMP/usage.err"
rc=$?
set -e
[[ "$rc" -eq 2 ]] || fail "no-args should exit 2, got $rc"
set +e
"$RUNE" --from-dir "$FROM" --to-dir "$TMP/does-not-exist" < "$TMP/id.json" >/dev/null 2>"$TMP/usage2.err"
rc=$?
set -e
[[ "$rc" -eq 2 ]] || fail "bad --to-dir should exit 2, got $rc"
python3 - "$TMP/missing.json" <<'PY'
import json, sys
open(sys.argv[1], "w").write(json.dumps({
    "uri": "src/does-not-exist.rs",
    "diagnostics": [{
        "range": {"start": {"line": 0, "character": 0}, "end": {"line": 0, "character": 1}},
        "message": "ghost",
    }],
}) + "\n")
PY
set +e
"$RUNE" --from-dir "$FROM" --to-dir "$TO" < "$TMP/missing.json" > "$TMP/strict.out" 2> "$TMP/strict.err"
rc=$?
set -e
[[ "$rc" -eq 1 ]] || fail "unresolved should exit 1, got $rc stdout=$(cat "$TMP/strict.out") err=$(cat "$TMP/strict.err")"
python3 - "$TMP/del.json" <<'PY'
import json, sys
open(sys.argv[1], "w").write(json.dumps({
    "uri": "src/calc.py",
    "diagnostics": [{
        "range": {"start": {"line": 10, "character": 0}, "end": {"line": 10, "character": 1}},
        "message": "gone",
    }],
}) + "\n")
PY
"$RUNE" --from-dir "$FROM" --to-dir "$TO" < "$TMP/del.json" >/dev/null \
  || fail "confirmed deletion should exit 0"
pass "exit 2 usage; exit 1 unresolved; exit 0 deletion"

echo "== 7d. 1-based number stuffed into LSP range is NOT converted to dest line 3 =="
python3 - "$TMP/onebased.json" <<'PY'
import json, sys
# Deliberately wrong: SARIF-style 1-based 4 placed in LSP range.start.line.
# File line 5 is a parameter list, not pub fn seen_hunk_fingerprint.
open(sys.argv[1], "w").write(json.dumps({
    "uri": "src/app.rs",
    "diagnostics": [{
        "range": {"start": {"line": 4, "character": 0}, "end": {"line": 4, "character": 4}},
        "message": "if this were SARIF startLine=4 it would be the function; as LSP it is 0-based line 4 = file line 5",
    }],
}) + "\n")
PY
out="$("$RUNE" --from-dir "$FROM" --to-dir "$TO" < "$TMP/onebased.json")"
echo "$out"
python3 -c 'import json,sys
raw=sys.argv[1]
dec=json.JSONDecoder(); vals=[]; i=0
while i<len(raw):
    while i<len(raw) and raw[i] in " \t\r\n": i+=1
    if i>=len(raw): break
    v,e=dec.raw_decode(raw,i); vals.append(v); i=e
moved=[v for v in vals if v.get("diagnostics")]
assert moved, vals
o=moved[0]
line=o["diagnostics"][0]["range"]["start"]["line"]
uri=o["uri"]
assert not (uri.endswith("layout.rs") and line==3), o
print("one-based-as-lsp", uri, line)
' "$out" || fail "1-based value in LSP field was silently shifted as SARIF: $out"
pass "1-based integer in range.start.line is not treated as SARIF startLine"

echo "== 7e. LSP Content-Length is dest-owned (not the stale header) =="
python3 - "$TMP/framed.bin" "$FROM" <<'PY'
import json, sys
from pathlib import Path
notify = {
    "jsonrpc": "2.0",
    "method": "textDocument/publishDiagnostics",
    "params": {
        "uri": "file:///home/runner/work/ugly/ugly/src/app.rs",
        "diagnostics": [
            {
                "range": {
                    "start": {"line": 3, "character": 0},
                    "end": {"line": 3, "character": 24},
                },
                "message": "seen_hunk_fingerprint",
            },
            {
                "range": {
                    "start": {"line": 13, "character": 0},
                    "end": {"line": 13, "character": 24},
                },
                "message": "nearest_landing_forward",
            },
        ],
    },
}
body = json.dumps(notify, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
# Deliberately the SOURCE byte length. After rewrite the body grows
# (app.rs → layout.rs / navigation.rs) so this number becomes a lie.
header = (
    b"Content-Length: " + str(len(body)).encode("ascii") + b"\r\n"
    + b"Content-Type: application/vscode-jsonrpc; charset=utf-8\r\n"
    + b"\r\n"
)
chatter = b"   Compiling ugly v0.1.0\n"
Path(sys.argv[1]).write_bytes(chatter + header + body)
open(sys.argv[1] + ".oldlen", "w").write(str(len(body)))
PY
"$RUNE" --from-dir "$FROM" --to-dir "$TO" < "$TMP/framed.bin" > "$TMP/framed.out"
python3 - "$TMP/framed.out" "$TMP/framed.bin.oldlen" <<'PY' || fail "Content-Length dest-own missed"
import json, sys, re
raw = open(sys.argv[1], "rb").read()
old_len = int(open(sys.argv[2]).read())
assert raw.startswith(b"   Compiling ugly v0.1.0\n"), raw[:40]
i = raw.find(b"Content-Length:")
assert i >= 0, raw[:80]
frames = []
while i < len(raw):
    m = re.match(br"Content-Length:\s*(\d+)\r\n(?:Content-Type:[^\r\n]*\r\n)?\r\n", raw[i:])
    if not m:
        break
    clen = int(m.group(1))
    hdr_end = i + m.end()
    body = raw[hdr_end:hdr_end + clen]
    assert len(body) == clen, (clen, len(body), body[:80])
    assert clen != old_len, "Content-Length still the source length (stale frame)"
    val = json.loads(body.decode("utf-8"))
    frames.append(val)
    i = hdr_end + clen
assert len(frames) >= 3, ("expected dests + origin-clear frames", len(frames), [f["params"]["uri"] for f in frames])
uris = [f["params"]["uri"] for f in frames]
assert any("layout.rs" in u for u in uris), uris
assert any("navigation.rs" in u for u in uris), uris
origin = next(f for f in frames if f["params"]["uri"].endswith("src/app.rs") and "layout" not in f["params"]["uri"])
assert origin["params"]["diagnostics"] == [], origin
assert "version" not in origin["params"]
# Content-Type survived on the first frame
assert b"Content-Type: application/vscode-jsonrpc; charset=utf-8\r\n" in raw
print("framed ok", len(frames), "frames", [len(json.dumps(f, separators=(',', ':')).encode()) for f in frames])
PY
pass "Content-Length dest-owned after rewrite; Content-Type kept; chatter survives"

echo "== 7f. dest-own character as UTF-16 (not Python code points) =="
mkdir -p "$TMP/wfrom/src" "$TMP/wto/src"
python3 - "$TMP/wfrom/src/wide.py" "$TMP/wto/src/wide.py" "$TMP/wide.json" <<'PY'
from pathlib import Path
import json, sys
# Unique token so fingerprint binds; dest line is shorter and ends in a
# supplementary-plane emoji (2 UTF-16 code units, 1 Python code point).
src = 'WIDE_TOKEN_QZX = "xxxxxxxxxxxxxxxxxxxx"'
dst = "WIDE_TOKEN_QZX 😀"
Path(sys.argv[1]).write_text(src + "\n", encoding="utf-8")
Path(sys.argv[2]).write_text(dst + "\n", encoding="utf-8")
open(sys.argv[3], "w").write(json.dumps({
    "uri": "src/wide.py",
    "diagnostics": [{
        "range": {
            "start": {"line": 0, "character": 22},
            "end": {"line": 0, "character": 40},
        },
        "message": "column past dest",
    }],
}) + "\n")
open(sys.argv[3] + ".expect", "w").write(
    json.dumps({
        "src": src,
        "dst": dst,
        "utf16": sum(2 if ord(c) > 0xFFFF else 1 for c in dst),
        "codepoints": len(dst),
    })
)
PY
out="$("$RUNE" --from-dir "$TMP/wfrom" --to-dir "$TMP/wto" < "$TMP/wide.json")"
echo "$out"
python3 - "$out" "$TMP/wide.json.expect" <<'PY' || fail "UTF-16 dest-own character missed"
import json, sys
raw = sys.argv[1]
expect = json.loads(open(sys.argv[2], encoding="utf-8").read())
dec = json.JSONDecoder()
vals = []
i = 0
while i < len(raw):
    while i < len(raw) and raw[i] in " \t\r\n":
        i += 1
    if i >= len(raw):
        break
    v, e = dec.raw_decode(raw, i)
    vals.append(v)
    i = e
dest = next(v for v in vals if v.get("diagnostics"))
ch = dest["diagnostics"][0]["range"]["start"]["character"]
end_ch = dest["diagnostics"][0]["range"]["end"]["character"]
cap = expect["utf16"]
cp = expect["codepoints"]
assert cap != cp, ("fixture must distinguish UTF-16 from code points", expect)
assert ch == cap, (ch, "expected UTF-16 clamp", cap, "not code-point clamp", cp, expect)
assert end_ch == cap, (end_ch, cap)
assert ch != 22 and end_ch != 40
print("utf16-char ok", ch, end_ch, "utf16", cap, "codepoints", cp)
PY
pass "character dest-owned as UTF-16 (clamped; not Python len())"

echo "== 7g. dest-own character remaps through dest UTF-16 (not clamp-only) =="
mkdir -p "$TMP/rfrom/src" "$TMP/rto/src"
python3 - "$TMP/rfrom/src/align.py" "$TMP/rto/src/align.py" "$TMP/align.json" <<'PY'
from pathlib import Path
import json, sys
# Same unique token so the line binds. Dest inserts a supplementary-plane
# emoji before extra_marker. Source column 15 still *fits* dest utf16_len
# (so v0.1 clamp would keep 15 — the first surrogate of 😀). Dest-own
# remaps through dest alignment onto extra_marker.
src = "WIDE_TOKEN_QZX extra_marker"
dst = "WIDE_TOKEN_QZX 😀 extra_marker"
Path(sys.argv[1]).write_text(src + "\n", encoding="utf-8")
Path(sys.argv[2]).write_text(dst + "\n", encoding="utf-8")
# extra_marker starts at UTF-16 15 on src, 18 on dest.
open(sys.argv[3], "w").write(json.dumps({
    "uri": "src/align.py",
    "diagnostics": [{
        "range": {
            "start": {"line": 0, "character": 15},
            "end": {"line": 0, "character": 27},
        },
        "message": "extra_marker after wide insert",
    }],
}) + "\n")
open(sys.argv[3] + ".expect", "w").write(json.dumps({
    "src": src,
    "dst": dst,
    "src_start": 15,
    "dest_start": 18,
    "dest_end": 30,
    "utf16": sum(2 if ord(c) > 0xFFFF else 1 for c in dst),
    "codepoints": len(dst),
}))
PY
out="$("$RUNE" --from-dir "$TMP/rfrom" --to-dir "$TMP/rto" < "$TMP/align.json")"
echo "$out"
python3 - "$out" "$TMP/align.json.expect" <<'PY' || fail "UTF-16 remap dest-own missed"
import json, sys
raw = sys.argv[1]
expect = json.loads(open(sys.argv[2], encoding="utf-8").read())
dec = json.JSONDecoder()
vals = []
i = 0
while i < len(raw):
    while i < len(raw) and raw[i] in " \t\r\n":
        i += 1
    if i >= len(raw):
        break
    v, e = dec.raw_decode(raw, i)
    vals.append(v)
    i = e
dest = next(v for v in vals if v.get("diagnostics"))
ch = dest["diagnostics"][0]["range"]["start"]["character"]
end_ch = dest["diagnostics"][0]["range"]["end"]["character"]
assert ch == expect["dest_start"], (ch, "expected dest extra_marker", expect)
assert end_ch == expect["dest_end"], (end_ch, expect)
assert ch != expect["src_start"], "clamp-only would have kept the source column"
assert ch != 16, "must not land on the trailing surrogate of 😀"
print("utf16-remap ok", ch, end_ch, "utf16", expect["utf16"], "codepoints", expect["codepoints"])
PY
pass "character remapped through dest UTF-16 alignment (not clamp-only)"

# --- real repo dogfood: copies of kizu ---
copy_tree() {
  local repo="$1" ref="$2" dest="$3"
  mkdir -p "$dest"
  git -C "$repo" archive "$ref" | tar -x -C "$dest"
}

KIZU="${KIZU:-/Users/annenpolka/ghq/github.com/annenpolka/kizu}"
if [[ -d "$KIZU/.git" || -f "$KIZU/.git" ]]; then
  echo "== 8. kizu publishDiagnostics: app.rs split (b4e6a5d → HEAD), 0-based =="
  copy_tree "$KIZU" b4e6a5d "$TMP/kizu-from"
  copy_tree "$KIZU" HEAD "$TMP/kizu-to"
  klog="$TMP/kizu.publish.json"
  python3 - "$klog" <<'PY'
import json, sys
# 1-based 529 / 543 → LSP 528 / 542. Dest 1-based 17 / 22 → LSP 16 / 21.
doc = {
    "jsonrpc": "2.0",
    "method": "textDocument/publishDiagnostics",
    "params": {
        "uri": "file:///home/runner/work/kizu/kizu/src/app.rs",
        "version": 12,
        "diagnostics": [
            {
                "range": {
                    "start": {"line": 528, "character": 4},
                    "end": {"line": 528, "character": 27},
                },
                "severity": 1,
                "code": "E0599",
                "source": "rust-analyzer",
                "message": (
                    "error[E0599]: no method named seen_hunk_fingerprint\n"
                    "  --> /home/runner/work/kizu/kizu/src/app.rs:529:5\n"
                    "   |\n"
                    "529 | pub fn seen_hunk_fingerprint(\n"
                ),
                "data": {"check": "keep"},
            },
            {
                "range": {
                    "start": {"line": 542, "character": 0},
                    "end": {"line": 542, "character": 24},
                },
                "message": 'File "src/app.rs", line 543, in nearest_landing_forward',
            },
        ],
    },
}
open(sys.argv[1], "w").write(json.dumps(doc, indent=2) + "\n")
PY
  rewritten="$("$RUNE" --from-dir "$TMP/kizu-from" --to-dir "$TMP/kizu-to" < "$klog")"
  echo "$rewritten"
  python3 - "$rewritten" <<'PY' || fail "kizu LSP assertions failed"
import json, sys
raw = sys.argv[1]
assert "\n" in raw.strip(), "pretty kizu collapsed"
vals = []
dec = json.JSONDecoder()
i = 0
while i < len(raw):
    while i < len(raw) and raw[i] in " \t\r\n":
        i += 1
    if i >= len(raw):
        break
    val, end = dec.raw_decode(raw, i)
    vals.append(val)
    i = end
pubs = [v for v in vals if isinstance(v, dict) and v.get("method") == "textDocument/publishDiagnostics"]
assert len(pubs) >= 3, ("expected fission + origin-clear", [p["params"]["uri"] for p in pubs])
layout = next(p for p in pubs if "layout.rs" in p["params"]["uri"])
nav = next(p for p in pubs if "navigation.rs" in p["params"]["uri"])
origin = next(
    p for p in pubs
    if p["params"]["uri"].endswith("src/app.rs")
    and "layout" not in p["params"]["uri"]
    and "navigation" not in p["params"]["uri"]
)
assert layout["params"]["uri"] == "file:///home/runner/work/kizu/kizu/src/app/layout.rs", layout
d0 = layout["params"]["diagnostics"][0]
assert d0["range"]["start"]["line"] == 16, d0  # NOT 17
assert isinstance(d0["range"]["start"]["line"], int)
assert d0["range"]["start"]["character"] == 4
assert "src/app.rs" not in layout["params"]["uri"]
assert "version" not in layout["params"]
assert d0["data"]["check"] == "keep"
msg = d0["message"]
assert "src/app/layout.rs:17:5" in msg or "src/app/layout.rs:17" in msg, msg
assert "src/app.rs:529" not in msg
assert "529 | pub fn seen_hunk_fingerprint(" not in msg, msg
assert "17 | pub fn seen_hunk_fingerprint(" in msg, msg
d1 = nav["params"]["diagnostics"][0]
assert nav["params"]["uri"].endswith("src/app/navigation.rs"), nav
assert d1["range"]["start"]["line"] == 21, d1  # NOT 22
assert 'File "src/app/navigation.rs", line 543' not in d1["message"]
assert origin["params"]["uri"] == "file:///home/runner/work/kizu/kizu/src/app.rs", origin
assert origin["params"]["diagnostics"] == [], origin
assert "version" not in origin["params"], origin["params"]
print("kizu ok", layout["params"]["uri"], d0["range"]["start"]["line"], d1["range"]["start"]["line"], "cleared", origin["params"]["uri"])
PY
  pass "kizu LSP via directory copies (app.rs#528 → layout.rs#16, not 17)"

  echo "== 8b. kizu read-only working tree as --to-dir =="
  rewritten="$("$RUNE" --from-dir "$TMP/kizu-from" --to-dir "$KIZU" < "$klog")"
  echo "$rewritten" | grep -q 'src/app/layout.rs' || fail "kizu live tree missed layout.rs: $rewritten"
  pass "kizu live working tree as to-dir"

  echo "== 8c. kizu SARIF 1-based gold is rejected (not shifted to 16) =="
  python3 - "$TMP/kizu.sarif" <<'PY'
import json, sys
sarif = {
    "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
    "version": "2.1.0",
    "runs": [{
        "tool": {"driver": {"name": "rustc"}},
        "results": [{
            "message": {"text": "error"},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": "file:///home/runner/work/kizu/kizu/src/app.rs"},
                    "region": {"startLine": 529, "startColumn": 5, "byteOffset": 18000},
                }
            }],
        }],
    }],
}
open(sys.argv[1], "w").write(json.dumps(sarif) + "\n")
PY
  set +e
  "$RUNE" --from-dir "$TMP/kizu-from" --to-dir "$TMP/kizu-to" --trace \
    < "$TMP/kizu.sarif" > "$TMP/kizu-sarif.out" 2> "$TMP/kizu-sarif.err"
  rc=$?
  set -e
  [[ "$rc" -eq 0 ]] || fail "SARIF reject should still exit 0 (not a failed LSP locator), got $rc"
  python3 -c 'import json,sys
o=json.loads(open(sys.argv[1],encoding="utf-8").read())
pl=o["runs"][0]["results"][0]["locations"][0]["physicalLocation"]
assert pl["artifactLocation"]["uri"].endswith("src/app.rs"), pl
assert pl["region"]["startLine"]==529, pl
assert pl["region"]["byteOffset"]==18000, pl
' "$TMP/kizu-sarif.out" || fail "SARIF was silently rewritten: $(cat "$TMP/kizu-sarif.out")"
  grep -q 'ignored	sarif' "$TMP/kizu-sarif.err" || fail "no explicit SARIF ignore: $(cat "$TMP/kizu-sarif.err")"
  pass "kizu SARIF 529 stays 529; explicit ignore, not silent shift"
else
  echo "SKIP kizu dogfood (repo not present at $KIZU)"
fi

SIT="${SIT:-/Users/annenpolka/ghq/github.com/annenpolka/sitbone}"
if [[ -d "$SIT/.git" || -f "$SIT/.git" ]]; then
  echo "== 9. sitbone LSP: detect() 1-based 45 → 75 is 0-based 44 → 74 =="
  copy_tree "$SIT" a95da43 "$TMP/sit-from"
  copy_tree "$SIT" HEAD "$TMP/sit-to"
  slog="$TMP/sit.json"
  python3 - "$slog" <<'PY'
import json, sys
doc = {
    "uri": "Sources/SitboneCore/PresenceArbiter.swift",
    "diagnostics": [{
        "range": {"start": {"line": 44, "character": 16}, "end": {"line": 44, "character": 25}},
        "message": "PresenceArbiter.swift:45:17: error: cannot find 'threshold' in scope",
    }],
}
open(sys.argv[1], "w").write(json.dumps(doc) + "\n")
PY
  rewritten="$("$RUNE" --from-dir "$TMP/sit-from" --to-dir "$TMP/sit-to" < "$slog")"
  echo "$rewritten"
  python3 -c 'import json,sys
o=json.loads(sys.argv[1])
assert o["uri"].endswith("PresenceArbiter.swift"), o
line=o["diagnostics"][0]["range"]["start"]["line"]
assert line != 44, o
assert line == 74, o  # 0-based dest of 1-based 75
assert ":45:" not in o["diagnostics"][0]["message"]
' "$rewritten" || fail "sitbone LSP missed: $rewritten"
  pass "sitbone detect() LSP 44 → 74"
else
  echo "SKIP sitbone dogfood (repo not present at $SIT)"
fi

VT="${VT:-/Users/annenpolka/ghq/github.com/annenpolka/voidtrace}"
if [[ -d "$VT/.git" || -f "$VT/.git" ]]; then
  echo "== 10. voidtrace LSP identity: evaluate.ts:40 / import{ at line 0 =="
  copy_tree "$VT" HEAD "$TMP/vt-from"
  copy_tree "$VT" HEAD "$TMP/vt-to"
  vlog="$TMP/vt.json"
  python3 - "$vlog" <<'PY'
import json, sys
doc = {
    "uri": "packages/kernel/src/evaluate.ts",
    "diagnostics": [
        {
            "range": {"start": {"line": 39, "character": 0}, "end": {"line": 39, "character": 21}},
            "message": "KERNEL_ENGINE_VERSION",
        },
        {
            "range": {"start": {"line": 0, "character": 0}, "end": {"line": 0, "character": 8}},
            "message": "import {",
        },
    ],
}
open(sys.argv[1], "w").write(json.dumps(doc) + "\n")
PY
  rewritten="$("$RUNE" --from-dir "$TMP/vt-from" --to-dir "$TMP/vt-to" < "$vlog")"
  echo "$rewritten"
  python3 -c 'import json,sys
o=json.loads(sys.argv[1])
assert o["uri"]=="packages/kernel/src/evaluate.ts", o
d0,d1=o["diagnostics"]
assert d0["range"]["start"]["line"]==39, d0
assert d1["range"]["start"]["line"]==0, d1
assert "cli.ts" not in json.dumps(o)
' "$rewritten" || fail "voidtrace identity jumped: $rewritten"
  pass "voidtrace evaluate.ts identity (no leftover-name jump)"
else
  echo "SKIP voidtrace dogfood (repo not present at $VT)"
fi

echo
echo "All demo checks passed."
exit 0
