#!/usr/bin/env bash
# Exercise flare as the inverse of gist/blot: 1-based locators in,
# 0-based publishDiagnostics out. The binary itself never calls git.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
FLARE="$ROOT/flare"
chmod +x "$FLARE"

if ! command -v python3 >/dev/null; then
  echo "demo.sh: python3 is required" >&2
  exit 1
fi

fail() { echo "FAIL: $*" >&2; exit 1; }
pass() { echo "PASS: $*"; }

# Parse dest-owned LSP frames or NDJSON into a JSON array of notifications.
parse_pubs() {
  python3 - "$1" <<'PY'
import json, re, sys
raw = open(sys.argv[1], "rb").read()
vals = []
if b"Content-Length:" in raw:
    i = 0
    while i < len(raw):
        m = re.match(br"Content-Length:\s*(\d+)\r\n(?:Content-Type:[^\r\n]*\r\n)?\r\n", raw[i:])
        if not m:
            nl = raw.find(b"\n", i)
            if nl < 0:
                break
            i = nl + 1
            continue
        clen = int(m.group(1))
        hdr = i + m.end()
        body = raw[hdr:hdr + clen]
        assert len(body) == clen, (clen, len(body))
        vals.append(json.loads(body.decode("utf-8")))
        i = hdr + clen
else:
    text = raw.decode("utf-8")
    dec = json.JSONDecoder()
    i = 0
    while i < len(text):
        while i < len(text) and text[i] in " \t\r\n":
            i += 1
        if i >= len(text):
            break
        if text[i] not in "{[":
            nl = text.find("\n", i)
            i = len(text) if nl < 0 else nl + 1
            continue
        val, end = dec.raw_decode(text, i)
        vals.append(val)
        i = end
print(json.dumps(vals))
PY
}

TMP="$(mktemp -d "${TMPDIR:-/tmp}/flare-demo.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

# The tool must not invoke git. A stub `git` on PATH dies if it is touched.
assert_no_git_needed() {
  local bin
  bin="$TMP/nogit"
  mkdir -p "$bin"
  cat > "$bin/git" <<'STUB'
#!/bin/sh
echo "flare must not invoke git: $*" >&2
exit 99
STUB
  chmod +x "$bin/git"
  PATH="$bin:$PATH" "$FLARE" "$@" >"$TMP/nogit.out" 2>"$TMP/nogit.err" \
    || fail "flare failed (or called git) with a stub git on PATH"
}

echo "== 0. usage =="
set +e
"$FLARE" --not-a-flag >/dev/null 2>"$TMP/help.err"
rc=$?
set -e
[[ "$rc" -eq 2 ]] || fail "expected exit 2 on unknown flag, got $rc"
"$FLARE" --help >"$TMP/help.out" 2>&1 || true
grep -q 'publishDiagnostics' "$TMP/help.out" || fail "help missing primitive: $(cat "$TMP/help.out")"
pass "exit 2 on usage; help names publishDiagnostics"

echo "== 1. SARIF startLine 529 → range.start.line 528 (not 529, not 17) =="
python3 - "$TMP/kizu.sarif" <<'PY'
import json, sys
sarif = {
    "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
    "version": "2.1.0",
    "runs": [{
        "tool": {"driver": {"name": "rustc"}},
        "results": [{
            "ruleId": "E0599",
            "level": "error",
            "message": {"text": "no method named seen_hunk_fingerprint"},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": "file:///home/runner/work/kizu/kizu/src/app.rs"},
                    "region": {
                        "startLine": 529,
                        "startColumn": 5,
                        "endLine": 529,
                        "endColumn": 27,
                        "byteOffset": 18000,
                        "snippet": {"text": "pub fn seen_hunk_fingerprint("},
                    },
                }
            }],
        }],
    }],
}
open(sys.argv[1], "w").write(json.dumps(sarif, indent=2) + "\n")
PY
assert_no_git_needed --trace < "$TMP/kizu.sarif"
python3 - "$TMP/nogit.out" "$TMP/nogit.err" <<'PY' || fail "SARIF 529 did not become LSP 528"
import json, re, sys
raw = open(sys.argv[1], "rb").read()
err = open(sys.argv[2], encoding="utf-8").read()
assert raw.startswith(b"Content-Length:"), raw[:40]
m = re.match(br"Content-Length:\s*(\d+)\r\nContent-Type:[^\r\n]*\r\n\r\n", raw)
assert m, raw[:120]
clen = int(m.group(1))
body = raw[m.end(): m.end() + clen]
assert len(body) == clen
o = json.loads(body.decode("utf-8"))
assert o["method"] == "textDocument/publishDiagnostics", o
p = o["params"]
assert p["uri"] == "file:///home/runner/work/kizu/kizu/src/app.rs", p
d = p["diagnostics"][0]
assert d["range"]["start"]["line"] == 528, d  # NOT 529, NOT 17
assert isinstance(d["range"]["start"]["line"], int)
assert d["range"]["start"]["character"] == 4, d
assert d["range"]["end"]["line"] == 528, d
# SARIF endColumn is inclusive 1-based 27 → exclusive 0-based 27
assert d["range"]["end"]["character"] == 27, d
assert d["severity"] == 1
assert d["code"] == "E0599"
assert d["source"] == "rustc"
assert d["data"]["flare"]["schema"] == "sarif"
assert d["data"]["flare"]["line_1"] == 529
assert "byteOffset" not in d["range"]
assert "converted\tsarif" in err
assert "\t529\t528\t" in err, err
print("sarif ok", d["range"]["start"]["line"], d["range"]["start"]["character"], "clen", clen)
PY
pass "SARIF 529 → LSP 528; startColumn 5 → character 4; dest-owned frame"

echo "== 2. cargo/rustc JSON line_start 529 → 528; column 5 → character 4 =="
python3 - "$TMP/kizu.cargo.jsonl" <<'PY'
import json, sys
doc = {
    "reason": "compiler-message",
    "package_id": "kizu@0.1.0",
    "manifest_path": "/home/runner/work/kizu/kizu/Cargo.toml",
    "target": {"name": "kizu", "src_path": "/home/runner/work/kizu/kizu/src/app.rs"},
    "message": {
        "$message_type": "diagnostic",
        "message": "no method named seen_hunk_fingerprint",
        "code": {"code": "E0599", "explanation": "see the book"},
        "level": "error",
        "spans": [{
            "file_name": "file:///home/runner/work/kizu/kizu/src/app.rs",
            "byte_start": 18000,
            "byte_end": 18023,
            "line_start": 529,
            "line_end": 529,
            "column_start": 5,
            "column_end": 28,
            "is_primary": True,
            "text": [{"text": "pub fn seen_hunk_fingerprint(", "highlight_start": 5, "highlight_end": 28}],
            "label": None,
        }],
        "children": [],
        "rendered": (
            "error[E0599]: no method named seen_hunk_fingerprint\n"
            "  --> /home/runner/work/kizu/kizu/src/app.rs:529:5\n"
            "   |\n"
            "529 | pub fn seen_hunk_fingerprint(\n"
        ),
    },
}
# a second span on the same godfile (landing helper) + chatter + artifact
rows = [
    "   Compiling kizu v0.1.0",
    {"reason": "compiler-artifact", "package_id": "kizu@0.1.0", "fresh": True},
    doc,
    {
        "$message_type": "diagnostic",
        "level": "error",
        "message": "landing",
        "spans": [{
            "file_name": "file:///home/runner/work/kizu/kizu/src/app.rs",
            "line_start": 543,
            "line_end": 543,
            "column_start": 1,
            "column_end": 25,
            "is_primary": True,
            "text": [{"text": "fn nearest_landing_forward("}],
        }],
        "rendered": "  --> /home/runner/work/kizu/kizu/src/app.rs:543:1\n",
    },
]
with open(sys.argv[1], "w", encoding="utf-8") as fp:
    fp.write(rows[0] + "\n")
    for row in rows[1:]:
        fp.write(json.dumps(row) + "\n")
PY
"$FLARE" --trace < "$TMP/kizu.cargo.jsonl" >"$TMP/cargo.out" 2>"$TMP/cargo.err"
parse_pubs "$TMP/cargo.out" >"$TMP/cargo.pubs.json"
python3 - "$TMP/cargo.pubs.json" "$TMP/cargo.err" "$TMP/cargo.out" <<'PY' || fail "cargo grouping / 529→528 missed"
import json, sys
vals = json.loads(open(sys.argv[1], encoding="utf-8").read())
err = open(sys.argv[2], encoding="utf-8").read()
raw = open(sys.argv[3], "rb").read()
assert b"Compiling" not in raw, "chatter leaked onto the LSP stream"
assert len(vals) == 1, ("v0.2 groups by uri; expected one document", len(vals), vals)
diags = vals[0]["params"]["diagnostics"]
assert len(diags) == 2, ("two spans on app.rs must share the document", len(diags))
d0, d1 = diags
assert d0["range"]["start"]["line"] == 528, d0
assert d0["range"]["start"]["character"] == 4, d0
assert d0["range"]["end"]["character"] == 27, d0  # rustc exclusive 1-based 28 → 27
assert d0["code"] == "E0599"
assert d0["data"]["flare"]["line_1"] == 529
assert "src/app.rs:529:5" in d0["message"], d0["message"]  # 1-based survives inside the string
assert d1["range"]["start"]["line"] == 542, d1
assert "\t529\t528\t" in err and "\t543\t542\t" in err, err
print("cargo ok", [d["range"]["start"]["line"] for d in diags])
PY
pass "cargo grouped: one uri, diagnostics 528 and 542; chatter dropped"

echo "== 3. rustc text arrow  src/app.rs:529:5 → line 528 character 4 =="
cat > "$TMP/kizu.log" <<'LOG'
error[E0599]: no method named seen_hunk_fingerprint
  --> /home/runner/work/kizu/kizu/src/app.rs:529:5
   |
529 | pub fn seen_hunk_fingerprint(
not a locator, just chatting about foo:bar and error:1
http://localhost:8080/health
LOG
"$FLARE" < "$TMP/kizu.log" >"$TMP/text.out" 2>"$TMP/text.err"
parse_pubs "$TMP/text.out" >"$TMP/text.pubs.json"
python3 - "$TMP/text.pubs.json" <<'PY' || fail "text locator missed"
import json, sys
vals = json.loads(open(sys.argv[1], encoding="utf-8").read())
assert len(vals) == 1, vals
d = vals[0]["params"]["diagnostics"][0]
assert vals[0]["params"]["uri"].endswith("src/app.rs"), vals[0]
assert d["range"]["start"]["line"] == 528, d
assert d["range"]["start"]["character"] == 4, d
assert d["severity"] == 1
assert "error[E0599]" in d["message"]
print("text ok", d["range"]["start"]["line"], d["range"]["start"]["character"])
PY
pass "rustc text 529:5 → LSP 528/4; error:1 and URL are not locators"

echo "== 4. already-0-based LSP is NOT converted (528 stays 528, not 527) =="
python3 - "$TMP/already.lsp.json" <<'PY'
import json, sys
doc = {
    "jsonrpc": "2.0",
    "method": "textDocument/publishDiagnostics",
    "params": {
        "uri": "file:///home/runner/work/kizu/kizu/src/app.rs",
        "diagnostics": [{
            "range": {"start": {"line": 528, "character": 4}, "end": {"line": 528, "character": 27}},
            "message": "already LSP",
        }],
    },
}
open(sys.argv[1], "w").write(json.dumps(doc) + "\n")
PY
"$FLARE" --trace < "$TMP/already.lsp.json" >"$TMP/lsp.out" 2>"$TMP/lsp.err"
python3 - "$TMP/lsp.out" "$TMP/lsp.err" <<'PY' || fail "LSP was shifted — that is a gist clone"
import sys
raw = open(sys.argv[1], encoding="utf-8").read().strip()
err = open(sys.argv[2], encoding="utf-8").read()
assert raw == "", raw  # LSP is not converted; it is ignored
assert "ignored\tlsp" in err, err
assert "527" not in raw
print("lsp ignored ok")
PY
pass "LSP range.start.line 528 is ignored, not shifted to 527"

echo "== 5. dest path with quote stays json.loads =="
python3 - "$TMP/quote.sarif" <<'PY'
import json, sys
open(sys.argv[1], "w").write(json.dumps({
    "version": "2.1.0",
    "runs": [{"results": [{"message": {"text": "x"},
        "locations": [{"physicalLocation": {
            "artifactLocation": {"uri": "src/quo\"te.py"},
            "region": {"startLine": 1, "startColumn": 1},
        }}]}]}]
}) + "\n")
PY
"$FLARE" < "$TMP/quote.sarif" >"$TMP/quote.out"
parse_pubs "$TMP/quote.out" >"$TMP/quote.pubs.json"
python3 - "$TMP/quote.pubs.json" <<'PY' || fail "quote unsealed the document"
import json, sys
vals = json.loads(open(sys.argv[1], encoding="utf-8").read())
o = vals[0]
uri = o["params"]["uri"]
assert 'quo"te.py' in uri, uri
assert o["params"]["diagnostics"][0]["range"]["start"]["line"] == 0
print("quote ok", uri)
PY
pass "uri with quote still json.loads; startLine 1 → line 0"

echo "== 6. default dest-owns Content-Length (client-shaped frame) =="
"$FLARE" < "$TMP/kizu.sarif" >"$TMP/framed.bin"
python3 - "$TMP/framed.bin" <<'PY' || fail "Content-Length dest-own missed"
import json, sys, re
raw = open(sys.argv[1], "rb").read()
assert raw.startswith(b"Content-Length:"), raw[:40]
m = re.match(br"Content-Length:\s*(\d+)\r\nContent-Type:[^\r\n]*\r\n\r\n", raw)
assert m, raw[:120]
clen = int(m.group(1))
body = raw[m.end(): m.end() + clen]
assert len(body) == clen, (clen, len(body))
assert len(raw) == m.end() + clen, "trailing junk after dest-owned frame"
val = json.loads(body.decode("utf-8"))
assert val["method"] == "textDocument/publishDiagnostics"
assert val["params"]["diagnostics"][0]["range"]["start"]["line"] == 528
print("frame ok", clen)
PY
pass "default Content-Length equals UTF-8 body length; 528 inside the frame"

echo "== 7. sitbone SourceKit key.line 45 → 44 =="
python3 - "$TMP/sit.json" <<'PY'
import json, sys
open(sys.argv[1], "w").write(json.dumps({
    "key.diagnostics": [{
        "key.line": 45,
        "key.column": 17,
        "key.filepath": "Sources/SitboneCore/PresenceArbiter.swift",
        "key.description": "cannot find 'threshold' in scope",
        "key.severity": "error",
    }]
}) + "\n")
PY
"$FLARE" < "$TMP/sit.json" >"$TMP/sit.out"
parse_pubs "$TMP/sit.out" >"$TMP/sit.pubs.json"
python3 - "$TMP/sit.pubs.json" <<'PY' || fail "sitbone 45 did not become 44"
import json, sys
vals = json.loads(open(sys.argv[1], encoding="utf-8").read())
o = vals[0]
assert o["params"]["uri"].endswith("PresenceArbiter.swift"), o
d = o["params"]["diagnostics"][0]
assert d["range"]["start"]["line"] == 44, d  # NOT 45, NOT 74
assert d["range"]["start"]["character"] == 16, d
assert d["severity"] == 1
print("sitbone ok", d["range"]["start"]["line"])
PY
pass "sitbone detect() SourceKit 45 → LSP 44"

echo "== 8. clang caret + pytest generic pair + mixed chatter =="
python3 - "$TMP/mixed.jsonl" <<'PY'
import json, sys
rows = [
    {"kind": "error", "message": "boom", "locations": [
        {"caret": {"file": "src/app.rs", "line": 4, "col": 1}}
    ]},
    {"tool": "pytest", "filename": "src/calc.py", "lineno": 11, "when": "call", "msg": "doomed"},
    {"reason": "compiler-artifact", "fresh": True},
]
open(sys.argv[1], "w").write("12:34:56 INFO starting\n" + "\n".join(json.dumps(r) for r in rows) + "\n")
PY
"$FLARE" < "$TMP/mixed.jsonl" >"$TMP/mixed.out"
parse_pubs "$TMP/mixed.out" >"$TMP/mixed.pubs.json"
python3 - "$TMP/mixed.pubs.json" <<'PY' || fail "mixed harvest missed"
import json, sys
vals = json.loads(open(sys.argv[1], encoding="utf-8").read())
uris = [v["params"]["uri"] for v in vals]
lines = [v["params"]["diagnostics"][0]["range"]["start"]["line"] for v in vals]
assert any("app.rs" in u for u in uris), uris
assert 3 in lines, lines  # clang caret line 4 → 3
assert 10 in lines, lines  # pytest lineno 11 → 10
print("mixed ok", list(zip(uris, lines)))
PY
pass "clang 4→3 and pytest 11→10 in a mixed stream"

echo "== 8b. UTF-16 character clamp from snippet (not Python len()) =="
python3 - "$TMP/wide.sarif" <<'PY'
import json, sys
# 😀 is one code point, two UTF-16 units. Optional VS-16 makes Python len 16 vs utf16 17
# on blot's WIDE_TOKEN_QZX string; we include the VS-16 so the two lengths diverge.
snip = "WIDE_TOKEN_QZX 😀\uFE0F"
open(sys.argv[1], "w").write(json.dumps({
    "version": "2.1.0",
    "runs": [{"results": [{"message": {"text": "wide"},
        "locations": [{"physicalLocation": {
            "artifactLocation": {"uri": "src/wide.py"},
            "region": {"startLine": 1, "startColumn": 40, "snippet": {"text": snip}},
        }}]}]}]
}) + "\n")
open(sys.argv[1] + ".snip", "w").write(snip)
PY
"$FLARE" --ndjson < "$TMP/wide.sarif" >"$TMP/wide.out"
python3 - "$TMP/wide.out" "$TMP/wide.sarif.snip" <<'PY' || fail "UTF-16 clamp missed"
import json, sys
snip = open(sys.argv[2], encoding="utf-8").read()
def utf16_len(text):
    n = 0
    for ch in text:
        n += 2 if ord(ch) > 0xFFFF else 1
    return n
cap = utf16_len(snip)
assert cap != len(snip), (cap, len(snip), [hex(ord(c)) for c in snip])
o = json.loads(open(sys.argv[1], encoding="utf-8").readline())
ch = o["params"]["diagnostics"][0]["range"]["start"]["character"]
# 1-based column 40 → 39 without clamp; dest-own clamps to utf16_len, not len()
assert ch != 39, ch
assert ch != len(snip), (ch, len(snip))
assert ch == cap, (ch, cap, len(snip))
print("utf16 ok", "character", ch, "utf16", cap, "codepoints", len(snip))
PY
pass "character dest-owned as UTF-16 and clamped; not Python len()"

echo "== 8c. --ndjson --per-span restores the v0.1 hole (two documents) =="
"$FLARE" --ndjson --per-span < "$TMP/kizu.cargo.jsonl" >"$TMP/per-span.out"
python3 - "$TMP/per-span.out" <<'PY' || fail "per-span did not restore two notifications"
import json, sys
vals = [json.loads(line) for line in open(sys.argv[1], encoding="utf-8") if line.strip()]
assert len(vals) == 2, len(vals)
assert all(len(v["params"]["diagnostics"]) == 1 for v in vals)
print("per-span ok", len(vals))
PY
pass "--per-span still one notification per locator (v0.1 hole opt-in)"

echo "== 9. empty / chatter-only is empty stdout, exit 0 =="
printf 'not a locator, just chatting about foo:bar and error:1\n' | "$FLARE" >"$TMP/empty.out"
[[ ! -s "$TMP/empty.out" ]] || fail "chatter-only leaked: $(cat "$TMP/empty.out")"
pass "chatter-only → empty LSP stream"

# --- real repo dogfood: copies of kizu (flare never talks to git) ---
copy_tree() {
  local repo="$1" ref="$2" dest="$3"
  mkdir -p "$dest"
  git -C "$repo" archive "$ref" | tar -x -C "$dest"
}

KIZU="${KIZU:-/Users/annenpolka/ghq/github.com/annenpolka/kizu}"
if [[ -d "$KIZU/.git" || -f "$KIZU/.git" ]]; then
  echo "== 10. kizu b4e6a5d app.rs:529 is seen_hunk_fingerprint (1-based gold) =="
  copy_tree "$KIZU" b4e6a5d "$TMP/kizu-from"
  copy_tree "$KIZU" HEAD "$TMP/kizu-to"
  python3 - "$TMP/kizu-from/src/app.rs" <<'PY' || fail "kizu b4e6a5d gold line drifted"
from pathlib import Path
import sys
lines = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
# 1-based 529 → index 528
assert "seen_hunk_fingerprint" in lines[528], lines[528]
assert "nearest_landing_forward" in lines[542], lines[542]
print("kizu from gold", lines[528][:40])
PY
  python3 - "$TMP/kizu-to/src/app/layout.rs" "$TMP/kizu-to/src/app/navigation.rs" <<'PY' || fail "kizu HEAD dest gold drifted"
from pathlib import Path
import sys
layout = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
nav = Path(sys.argv[2]).read_text(encoding="utf-8").splitlines()
assert "seen_hunk_fingerprint" in layout[16], layout[16]  # 1-based 17 → 0-based 16
assert "nearest_landing_forward" in nav[21], nav[21]
print("kizu dest gold", layout[16][:40], nav[21][:40])
PY
  "$FLARE" < "$TMP/kizu.cargo.jsonl" >"$TMP/kizu-flare.bin"
  parse_pubs "$TMP/kizu-flare.bin" >"$TMP/kizu-flare.pubs.json"
  python3 - "$TMP/kizu-flare.pubs.json" <<'PY' || fail "kizu cargo through flare missed 528"
import json, sys
vals = json.loads(open(sys.argv[1], encoding="utf-8").read())
assert len(vals) == 1, len(vals)
lines = [d["range"]["start"]["line"] for d in vals[0]["params"]["diagnostics"]]
assert lines == [528, 542], lines
print("kizu flare grouped", lines)
PY
  pass "kizu cargo gold: one framed document, 529/543 → 528/542"

  BLOT="${BLOT:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bad-eb91-7d80-9aa0-106220b8e2a1/blot}"
  if [[ -x "$BLOT" ]]; then
    echo "== 10b. composability: grouped flare | blot  528→16 and 542→21 + origin-clear =="
    "$FLARE" < "$TMP/kizu.cargo.jsonl" | "$BLOT" --from-dir "$TMP/kizu-from" --to-dir "$TMP/kizu-to" \
      >"$TMP/kizu-pipe.bin" 2>"$TMP/kizu-pipe.err" || fail "flare|blot failed"
    python3 - "$TMP/kizu-pipe.bin" <<'PY' || fail "flare|blot did not fission 16 and 21"
import json, sys, re
raw = open(sys.argv[1], "rb").read()
text = raw.decode("utf-8", "surrogateescape")
vals = []
if b"Content-Length:" in raw:
    i = 0
    while i < len(raw):
        m = re.match(br"Content-Length:\s*(\d+)\r\n(?:Content-Type:[^\r\n]*\r\n)?\r\n", raw[i:])
        if not m:
            nl = raw.find(b"\n", i)
            if nl < 0:
                break
            i = nl + 1
            continue
        clen = int(m.group(1))
        body = raw[i + m.end(): i + m.end() + clen]
        vals.append(json.loads(body.decode("utf-8")))
        i = i + m.end() + clen
else:
    dec = json.JSONDecoder()
    i = 0
    while i < len(text):
        while i < len(text) and text[i] in " \t\r\n":
            i += 1
        if i >= len(text):
            break
        if text[i] not in "{[":
            nl = text.find("\n", i)
            i = len(text) if nl < 0 else nl + 1
            continue
        val, end = dec.raw_decode(text, i)
        vals.append(val)
        i = end
pubs = [v for v in vals if isinstance(v, dict) and v.get("method") == "textDocument/publishDiagnostics"]
uris = [p["params"]["uri"] for p in pubs]
layout = next((p for p in pubs if "layout.rs" in p["params"]["uri"]), None)
nav = next((p for p in pubs if "navigation.rs" in p["params"]["uri"]), None)
clears = [p for p in pubs if p["params"]["uri"].endswith("src/app.rs") and p["params"]["diagnostics"] == []]
assert layout is not None, uris
assert nav is not None, uris
assert layout["params"]["diagnostics"][0]["range"]["start"]["line"] == 16, layout  # NOT 17
assert nav["params"]["diagnostics"][0]["range"]["start"]["line"] == 21, nav  # NOT 22
assert clears, ("missing origin diagnostics:[]", uris)
print("pipe ok", "layout", 16, "nav", 21, "cleared", bool(clears))
PY
    pass "flare | blot : 529→528→16 and 543→542→21 plus origin diagnostics:[]"
  else
    echo "SKIP flare|blot (blot not at $BLOT)"
  fi
else
  echo "SKIP kizu dogfood (repo not present at $KIZU)"
fi

SIT="${SIT:-/Users/annenpolka/ghq/github.com/annenpolka/sitbone}"
if [[ -d "$SIT/.git" || -f "$SIT/.git" ]]; then
  echo "== 11. sitbone a95da43 detect() is 1-based 45 =="
  copy_tree "$SIT" a95da43 "$TMP/sit-from"
  python3 - "$TMP/sit-from/Sources/SitboneCore/PresenceArbiter.swift" <<'PY' || fail "sitbone gold drifted"
from pathlib import Path
import sys
lines = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
assert "func detect()" in lines[44], lines[44]
print("sit from gold", lines[44].strip())
PY
  pass "sitbone tree confirms 1-based 45; flare already emitted 44"
else
  echo "SKIP sitbone tree (repo not present at $SIT)"
fi

echo "ALL DEMO CHECKS PASSED"
