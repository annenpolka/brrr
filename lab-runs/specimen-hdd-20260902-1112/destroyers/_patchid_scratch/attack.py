#!/usr/bin/env python3
"""Host-executed destroyer attacks against candidate-patchid. No pnpm."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

RUN = Path("/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112")
ROOT = RUN / "lineages" / "candidate-patchid"
CLI = ROOT / "patchid"
FIX = ROOT / "fixtures"
SPEC = RUN / "specimens" / "specimen-085" / "files"
SCRATCH = RUN / "destroyers" / "_patchid_scratch"
PY = sys.executable


def parse_rows(text: str) -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        name, rest = line.split("\t", 1)
        rows[name] = rest
    return rows


def run(path: str, selector: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [PY, str(CLI), path, "--selector", selector],
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )


def write_tmp(name: str, text: str) -> Path:
    p = SCRATCH / name
    p.write_text(text, encoding="utf-8")
    return p


def replica_kind_switch(text: str, selector: str) -> tuple[str, int]:
    """Independent YAML mapping-vs-string classifier. No nested parse for kind."""
    in_block = False
    last: str | None = None
    for raw in text.splitlines():
        if raw.strip().startswith("#") or not raw.strip():
            continue
        if raw.rstrip() == "patchedDependencies:":
            in_block = True
            continue
        if not in_block:
            continue
        if not raw.startswith(" "):
            in_block = False
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        if indent != 2 or ":" not in line:
            continue
        sel, rest = line.split(":", 1)
        sel = sel.strip().strip("'\"")
        rest = rest.strip().strip("'\"")
        if sel != selector:
            continue
        if rest == "" and line.endswith(":"):
            last = "object"
        elif rest == "":
            last = "empty"
        else:
            last = "hash-only"
    kind = last or "omitted"
    rc = 0 if kind == "hash-only" else 1
    return kind, rc


def replica_full(text: str, selector: str) -> dict:
    """Byte-aimed replica of parse_patched + inspect + rc (stdlib only)."""
    entries: dict[str, dict] = {}
    in_block = False
    current: str | None = None
    for lineno, raw in enumerate(text.splitlines(), 1):
        if raw.strip().startswith("#") or not raw.strip():
            continue
        if raw.rstrip() == "patchedDependencies:":
            in_block = True
            current = None
            continue
        if not in_block:
            continue
        if not raw.startswith(" "):
            in_block = False
            current = None
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        if indent == 2 and line.endswith(":") and not line.startswith("path:") and not line.startswith("hash:"):
            sel = line[:-1].strip().strip("'\"")
            current = sel
            entries[sel] = {"kind": "object", "path": "", "hash": ""}
            continue
        if indent == 2 and ":" in line:
            sel, rest = line.split(":", 1)
            sel = sel.strip().strip("'\"")
            rest = rest.strip().strip("'\"")
            current = sel
            if rest == "":
                entries[sel] = {"kind": "empty", "path": "", "hash": ""}
            else:
                entries[sel] = {"kind": "hash-only", "path": "", "hash": rest}
            continue
        if indent >= 4 and current is not None and ":" in line:
            key, rest = line.split(":", 1)
            key = key.strip()
            rest = rest.strip().strip("'\"")
            rec = entries.setdefault(current, {"kind": "object", "path": "", "hash": ""})
            rec["kind"] = "object"
            if key == "path":
                rec["path"] = rest
            elif key == "hash":
                rec["hash"] = rest
            else:
                raise ValueError(f"unknown field {key!r}")
            continue
        raise ValueError("unparsed")
    rec = entries.get(selector)
    if rec is None:
        kind = "omitted"
        path = "-"
        hashv = "-"
        has_path = False
        has_hash = False
    else:
        kind = rec["kind"]
        path = rec.get("path") or "-"
        hashv = rec.get("hash") or "-"
        has_path = bool(rec.get("path"))
        has_hash = bool(rec.get("hash"))
    rc = 0 if kind == "hash-only" else 1
    report = (
        f"selector\t{selector}\n"
        f"kind\t{kind}\n"
        f"path\t{path}\n"
        f"hash\t{hashv}\n"
        f"has_path\t{'yes' if has_path else 'no'}\n"
        f"has_hash\t{'yes' if has_hash else 'no'}\n"
    )
    return {"kind": kind, "rc": rc, "stdout": report}


log: list[str] = []


def rec(title: str, **kv):
    line = title + " | " + " ".join(f"{k}={v!r}" for k, v in kv.items())
    log.append(line)
    print(line)


# --- tests ---
t = subprocess.run(
    [PY, "-m", "unittest", "discover", "-s", str(ROOT / "tests"), "-v"],
    capture_output=True,
    text=True,
    check=False,
    cwd=str(ROOT),
)
rec("UNITTEST", rc=t.returncode, tail=t.stderr.strip().splitlines()[-3:])

# --- demo ---
d1 = subprocess.run(["bash", str(ROOT / "demo.sh")], capture_output=True, text=True, check=False, cwd=str(ROOT))
(ROOT / "demo-live.log").write_text(d1.stdout, encoding="utf-8")
rec(
    "DEMO",
    rc=d1.returncode,
    stdout_len=len(d1.stdout),
    stderr=d1.stderr.strip()[:200],
    matches_demo1=d1.stdout == (ROOT / "demo-1.log").read_text(),
    object_in_stdout=("kind\tobject" in d1.stdout),
    hash_in_stdout=("kind\thash-only" in d1.stdout),
)

# --- owned ---
owned = [
    ("object", SPEC / "patcheddeps.object.yaml", "express@4.18.1"),
    ("hash", SPEC / "patcheddeps.hash.yaml", "express@4.18.1"),
    ("omitted", SPEC / "patcheddeps.hash.yaml", "missing@1.0.0"),
]
for label, path, sel in owned:
    p = run(str(path), sel)
    rows = parse_rows(p.stdout)
    rec(f"OWNED_{label}", rc=p.returncode, kind=rows.get("kind"), hash=rows.get("hash"), path=rows.get("path"), has_path=rows.get("has_path"), has_hash=rows.get("has_hash"), stderr=p.stderr.strip())

empty = run("-", "express@4.18.1", stdin='patchedDependencies:\n  express@4.18.1: ""\n')
rec("OWNED_empty", rc=empty.returncode, kind=parse_rows(empty.stdout).get("kind"), stdout=empty.stdout)

# fixtures vs spec
for name in ("patcheddeps.object.yaml", "patcheddeps.hash.yaml"):
    rec(f"FIX_EQ_{name}", eq=(FIX / name).read_text() == (SPEC / name).read_text())

# --- grep nearest ---
for name in ("patcheddeps.object.yaml", "patcheddeps.hash.yaml"):
    g = subprocess.run(["grep", "express@4.18.1", str(SPEC / name)], capture_output=True, text=True, check=False)
    rec(f"GREP_{name}", rc=g.returncode, nlines=len(g.stdout.splitlines()), hits=g.stdout.splitlines())

# --- hashes unused ---
obj_aaa = write_tmp(
    "object-aaa.yaml",
    "patchedDependencies:\n  express@4.18.1:\n    path: patches/express@4.18.1.patch\n    hash: AAA\n",
)
hash_aaa = write_tmp("hash-aaa.yaml", "patchedDependencies:\n  express@4.18.1: AAA\n")
p = run(str(obj_aaa), "express@4.18.1")
rec("HASH_UNUSED_object_AAA", rc=p.returncode, kind=parse_rows(p.stdout).get("kind"), hash=parse_rows(p.stdout).get("hash"))
p = run(str(hash_aaa), "express@4.18.1")
rec("HASH_UNUSED_hash_AAA", rc=p.returncode, kind=parse_rows(p.stdout).get("kind"), hash=parse_rows(p.stdout).get("hash"))
# same kind as fixture-patch-hash
p_obj = run(str(SPEC / "patcheddeps.object.yaml"), "express@4.18.1")
p_hash = run(str(SPEC / "patcheddeps.hash.yaml"), "express@4.18.1")
rec(
    "HASH_UNUSED_kind_stable",
    object_kind_same=parse_rows(p_obj.stdout)["kind"] == parse_rows(run(str(obj_aaa), "express@4.18.1").stdout)["kind"],
    hash_kind_same=parse_rows(p_hash.stdout)["kind"] == parse_rows(run(str(hash_aaa), "express@4.18.1").stdout)["kind"],
    object_rc_same=p_obj.returncode == run(str(obj_aaa), "express@4.18.1").returncode,
    hash_rc_same=p_hash.returncode == run(str(hash_aaa), "express@4.18.1").returncode,
)

# --- selector prefix ---
for sel in (
    "express",
    "express@4.18",
    "express@4.18.1",
    "express@4.18.10",
    "patches/express@4.18.1.patch",
    "express@4.18.1:",
    "fixture-patch-hash",
):
    p = run(str(SPEC / "patcheddeps.object.yaml"), sel)
    rec("PREFIX_object", selector=sel, rc=p.returncode, kind=parse_rows(p.stdout).get("kind"), stderr=p.stderr.strip()[:80])
    p = run(str(SPEC / "patcheddeps.hash.yaml"), sel)
    rec("PREFIX_hash", selector=sel, rc=p.returncode, kind=parse_rows(p.stdout).get("kind"))

# two selectors, prefix of each other
both = write_tmp(
    "prefix-pair.yaml",
    "patchedDependencies:\n  express@4.18.1: hash-short\n  express@4.18.10: hash-long\n",
)
for sel in ("express@4.18.1", "express@4.18.10", "express@4.18", "express@4.18.1 "):
    p = run(str(both), sel)
    rec("PREFIX_pair", selector=sel, rc=p.returncode, kind=parse_rows(p.stdout).get("kind"), hash=parse_rows(p.stdout).get("hash"))

# --- stdin / missing ---
p = run("-", "express@4.18.1", stdin=(SPEC / "patcheddeps.object.yaml").read_text())
rec("STDIN_object", rc=p.returncode, kind=parse_rows(p.stdout).get("kind"), has_path=parse_rows(p.stdout).get("has_path"))
p = run("-", "express@4.18.1", stdin=(SPEC / "patcheddeps.hash.yaml").read_text())
rec("STDIN_hash", rc=p.returncode, kind=parse_rows(p.stdout).get("kind"))
p = run("/no/such.yaml", "express@4.18.1")
rec("MISSING", rc=p.returncode, stdout=p.stdout, stderr=p.stderr.strip())
p = run(str(SPEC), "express@4.18.1")
rec("DIRECTORY", rc=p.returncode, stderr=p.stderr.strip())

# argv-less / no selector
p = subprocess.run([PY, str(CLI)], capture_output=True, text=True, check=False)
rec("NOARGS", rc=p.returncode, stderr=p.stderr.strip().splitlines()[-1:])
p = subprocess.run([PY, str(CLI), str(SPEC / "patcheddeps.hash.yaml")], capture_output=True, text=True, check=False)
rec("NOSELECTOR", rc=p.returncode, stderr=p.stderr.strip().splitlines()[-1:])

# stdin without dash: body on pipe, path is file
p = subprocess.run(
    [PY, str(CLI), str(SPEC / "patcheddeps.hash.yaml"), "--selector", "express@4.18.1"],
    input="patchedDependencies:\n  express@4.18.1: FROMSTDIN\n",
    capture_output=True,
    text=True,
    check=False,
)
rec("STDIN_IGNORED_WHEN_FILE", rc=p.returncode, kind=parse_rows(p.stdout).get("kind"), hash=parse_rows(p.stdout).get("hash"))

# --- replica match on owned + extra ---
cases = []
cases.append(("owned-object", (SPEC / "patcheddeps.object.yaml").read_text(), "express@4.18.1"))
cases.append(("owned-hash", (SPEC / "patcheddeps.hash.yaml").read_text(), "express@4.18.1"))
cases.append(("owned-omitted", (SPEC / "patcheddeps.hash.yaml").read_text(), "missing@1.0.0"))
cases.append(("empty", 'patchedDependencies:\n  express@4.18.1: ""\n', "express@4.18.1"))
cases.append(("empty-sq", "patchedDependencies:\n  express@4.18.1: ''\n", "express@4.18.1"))
cases.append(("aaa-object", obj_aaa.read_text(), "express@4.18.1"))
cases.append(("aaa-hash", hash_aaa.read_text(), "express@4.18.1"))
cases.append(("bare-object-no-body", "patchedDependencies:\n  express@4.18.1:\n", "express@4.18.1"))
cases.append(("path-only", "patchedDependencies:\n  express@4.18.1:\n    path: patches/x.patch\n", "express@4.18.1"))
cases.append(("hash-field-only", "patchedDependencies:\n  express@4.18.1:\n    hash: onlyhash\n", "express@4.18.1"))
cases.append(("quoted-sel-hash", "patchedDependencies:\n  'express@4.18.1': fixture-patch-hash\n", "express@4.18.1"))
cases.append(("quoted-sel-obj", "patchedDependencies:\n  \"express@4.18.1\":\n    path: p\n    hash: h\n", "express@4.18.1"))
cases.append(("lockfileVersion-before", "lockfileVersion: '9.0'\n\npatchedDependencies:\n  express@4.18.1: abc\npackages:\n  /express@4.18.1:\n    resolution: {integrity: x}\n", "express@4.18.1"))
cases.append(("comment", "# c\npatchedDependencies:\n  # inner\n  express@4.18.1: abc\n", "express@4.18.1"))
cases.append(("dup-last-wins", "patchedDependencies:\n  express@4.18.1: first\n  express@4.18.1:\n    path: p\n    hash: second\n", "express@4.18.1"))
cases.append(("hash-then-nested", "patchedDependencies:\n  express@4.18.1: first\n    path: sneaky\n", "express@4.18.1"))
cases.append(("flow", "patchedDependencies:\n  express@4.18.1: {path: p, hash: h}\n", "express@4.18.1"))
cases.append(("null-token", "patchedDependencies:\n  express@4.18.1: null\n", "express@4.18.1"))
cases.append(("tilde", "patchedDependencies:\n  express@4.18.1: ~\n", "express@4.18.1"))
cases.append(("no-block", "packages:\n  express@4.18.1: x\n", "express@4.18.1"))
cases.append(("tab-indent", "patchedDependencies:\n\texpress@4.18.1: abc\n", "express@4.18.1"))
cases.append(("four-space-sel", "patchedDependencies:\n    express@4.18.1: abc\n", "express@4.18.1"))
cases.append(("crlf", "patchedDependencies:\r\n  express@4.18.1: abc\r\n", "express@4.18.1"))
cases.append(("prefix-pair-short", both.read_text(), "express@4.18.1"))
cases.append(("prefix-pair-long", both.read_text(), "express@4.18.10"))

replica_rows = []
kind_switch_rows = []
for label, text, sel in cases:
    tmp = write_tmp(f"case-{label}.yaml", text)
    p = run(str(tmp), sel) if label != "empty" else run("-", sel, stdin=text)
    if label == "empty":
        p = run("-", sel, stdin=text)
    else:
        p = run(str(tmp), sel)
    cli_kind = parse_rows(p.stdout).get("kind")
    try:
        full = replica_full(text, sel)
        full_ok = full["stdout"] == p.stdout and full["rc"] == p.returncode
        full_err = ""
    except Exception as e:
        full_ok = False
        full_err = str(e)
        full = {"kind": "ERR", "rc": None, "stdout": ""}
    ks_kind, ks_rc = replica_kind_switch(text, sel)
    ks_ok = ks_kind == cli_kind and ks_rc == p.returncode
    replica_rows.append(
        {
            "label": label,
            "cli_kind": cli_kind,
            "cli_rc": p.returncode,
            "cli_stderr": p.stderr.strip()[:80],
            "full_ok": full_ok,
            "full_kind": full["kind"],
            "full_err": full_err,
            "ks_kind": ks_kind,
            "ks_rc": ks_rc,
            "ks_ok": ks_ok,
            "stdout": p.stdout,
        }
    )
    rec(
        "REPLICA",
        label=label,
        cli_kind=cli_kind,
        cli_rc=p.returncode,
        full_ok=full_ok,
        ks_ok=ks_ok,
        ks_kind=ks_kind,
        stderr=p.stderr.strip()[:60],
    )

# extra field should fail replica_full and CLI
extra = "patchedDependencies:\n  express@4.18.1:\n    path: p\n    hash: h\n    extra: z\n"
p = run(str(write_tmp("extra.yaml", extra)), "express@4.18.1")
rec("EXTRA_FIELD", rc=p.returncode, stdout=p.stdout, stderr=p.stderr.strip())

# BOM
bom = "\ufeffpatchedDependencies:\n  express@4.18.1: abc\n"
p = run(str(write_tmp("bom.yaml", bom)), "express@4.18.1")
rec("BOM", rc=p.returncode, kind=parse_rows(p.stdout).get("kind"), stderr=p.stderr.strip()[:80])

# empty file / comments only / no patchedDependencies
for label, text in (
    ("emptyfile", ""),
    ("comments", "# only\n"),
    ("devnull_like", "\n"),
):
    p = run(str(write_tmp(f"{label}.yaml", text)), "express@4.18.1")
    rec("EMPTYISH", label=label, rc=p.returncode, kind=parse_rows(p.stdout).get("kind"), stderr=p.stderr.strip()[:80])

# huge: 5000 other selectors + target
lines = ["patchedDependencies:"]
for i in range(5000):
    lines.append(f"  other@{i}: hash{i}")
lines.append("  express@4.18.1: targethash")
huge = write_tmp("huge.yaml", "\n".join(lines) + "\n")
p = run(str(huge), "express@4.18.1")
rec("HUGE", rc=p.returncode, kind=parse_rows(p.stdout).get("kind"), hash=parse_rows(p.stdout).get("hash"), bytes=huge.stat().st_size)

# unknown field vs replica_full exception: CLI rc=1 no TSV
# already EXTRA_FIELD

# awk/grep kind switch on owned
def grep_kind(path: Path, selector: str) -> str:
    text = path.read_text()
    in_block = False
    for raw in text.splitlines():
        if raw.rstrip() == "patchedDependencies:":
            in_block = True
            continue
        if not in_block:
            continue
        m = re.match(r"^  ([^:]+):(.*)$", raw)
        if not m:
            continue
        sel = m.group(1).strip().strip("'\"")
        rest = m.group(2).strip().strip("'\"")
        if sel != selector:
            continue
        if rest == "":
            return "object"
        if rest == "":
            return "empty"
        return "hash-only"
    return "omitted"


rec("AWK_object", k=grep_kind(SPEC / "patcheddeps.object.yaml", "express@4.18.1"))
rec("AWK_hash", k=grep_kind(SPEC / "patcheddeps.hash.yaml", "express@4.18.1"))
rec("AWK_omitted", k=grep_kind(SPEC / "patcheddeps.hash.yaml", "missing@1.0.0"))

# object line vs hash line via grep -E
g_obj = subprocess.run(
    ["grep", "-n", "-E", r"^  express@4\.18\.1:", str(SPEC / "patcheddeps.object.yaml")],
    capture_output=True,
    text=True,
    check=False,
)
g_hash = subprocess.run(
    ["grep", "-n", "-E", r"^  express@4\.18\.1:", str(SPEC / "patcheddeps.hash.yaml")],
    capture_output=True,
    text=True,
    check=False,
)
rec("GREP_SEL_LINE_object", line=g_obj.stdout.strip(), mapping=g_obj.stdout.strip().endswith(":"))
rec("GREP_SEL_LINE_hash", line=g_hash.stdout.strip(), mapping=g_hash.stdout.strip().endswith(":"))

# empty vs bare object: key: vs key: ""
p_bare = run(str(write_tmp("bare.yaml", "patchedDependencies:\n  express@4.18.1:\n")), "express@4.18.1")
p_empty = run("-", "express@4.18.1", stdin='patchedDependencies:\n  express@4.18.1: ""\n')
rec(
    "KIND_SWITCH_bare_vs_empty",
    bare_kind=parse_rows(p_bare.stdout).get("kind"),
    bare_rc=p_bare.returncode,
    empty_kind=parse_rows(p_empty.stdout).get("kind"),
    empty_rc=p_empty.returncode,
    same_has_path=parse_rows(p_bare.stdout).get("has_path") == parse_rows(p_empty.stdout).get("has_path"),
    same_has_hash=parse_rows(p_bare.stdout).get("has_hash") == parse_rows(p_empty.stdout).get("has_hash"),
)

# trailing space after colon on selector line (strip -> object)
p = run(str(write_tmp("colon-space.yaml", "patchedDependencies:\n  express@4.18.1:   \n")), "express@4.18.1")
rec("COLON_TRAILING_SPACE", rc=p.returncode, kind=parse_rows(p.stdout).get("kind"), stderr=p.stderr.strip()[:80], stdout=p.stdout)

# YAML | multiline
p = run(str(write_tmp("pipe.yaml", "patchedDependencies:\n  express@4.18.1: |\n    abc\n")), "express@4.18.1")
rec("PIPE_MULTILINE", rc=p.returncode, kind=parse_rows(p.stdout).get("kind"), hash=parse_rows(p.stdout).get("hash"), stderr=p.stderr.strip()[:80])

# symlink
link = SCRATCH / "link-hash.yaml"
if link.exists() or link.is_symlink():
    link.unlink()
link.symlink_to(SPEC / "patcheddeps.hash.yaml")
p = run(str(link), "express@4.18.1")
rec("SYMLINK", rc=p.returncode, kind=parse_rows(p.stdout).get("kind"))

# process substitution analog: /dev/stdin
p = subprocess.run(
    [PY, str(CLI), "/dev/stdin", "--selector", "express@4.18.1"],
    input=(SPEC / "patcheddeps.hash.yaml").read_text(),
    capture_output=True,
    text=True,
    check=False,
)
rec("DEV_STDIN", rc=p.returncode, kind=parse_rows(p.stdout).get("kind"))

# compare replica_full vs CLI on owned files using stdin vs path
summary = {
    "replica_full_all": all(r["full_ok"] for r in replica_rows if r["cli_stderr"] == ""),
    "kind_switch_all_when_cli_ok": all(r["ks_ok"] for r in replica_rows if r["cli_kind"] is not None),
    "kind_switch_mismatches": [r["label"] for r in replica_rows if not r["ks_ok"]],
    "full_mismatches": [r["label"] for r in replica_rows if not r["full_ok"]],
    "n_cases": len(replica_rows),
}
rec("SUMMARY", **summary)
(SCRATCH / "replica.json").write_text(json.dumps(replica_rows, indent=2), encoding="utf-8")
(SCRATCH / "attacks.log").write_text("\n".join(log) + "\n", encoding="utf-8")
print("---SUMMARY---")
print(json.dumps(summary, indent=2))
