#!/usr/bin/env python3
"""Host-executed destroyer attacks against candidate-patchident. No pnpm."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

RUN = Path("/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112")
ROOT = RUN / "lineages" / "candidate-patchident"
CLI = ROOT / "patchident"
FIX = ROOT / "fixtures"
SPEC = RUN / "specimens" / "specimen-085" / "files"
SCRATCH = RUN / "destroyers" / "_patchident_scratch"
PY = sys.executable
SEL = "express@4.18.1"
EMPTY = "-"


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


def replica_full(text: str, selector: str) -> dict:
    """Byte-aimed replica of parse_lock + inspect + format_report + rc."""
    entries: dict[str, dict] = {}
    in_block = False
    current: str | None = None
    for lineno, raw in enumerate(text.splitlines(), 1):
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        if raw.startswith("patchedDependencies:"):
            in_block = True
            continue
        if not in_block:
            continue
        if raw.startswith(" ") and current is not None:
            line = raw.strip()
            if ":" not in line:
                raise ValueError(f"expected path/hash field:{lineno}")
            key, _, rest = line.partition(":")
            val = rest.strip().strip('"').strip("'")
            key = key.strip()
            if key == "path":
                entries[current]["path"] = val
                entries[current]["shape"] = "object"
            elif key == "hash":
                entries[current]["hash"] = val
                entries[current]["shape"] = "object"
            else:
                raise ValueError(f"unknown field {key!r}")
            continue
        line = raw.strip()
        if ":" not in line:
            raise ValueError("expected selector")
        sel, _, rest = line.partition(":")
        sel = sel.strip()
        val = rest.strip().strip('"').strip("'")
        if not sel or sel == EMPTY:
            raise ValueError("not a legal NAME")
        current = sel
        if val == "":
            entries[sel] = {"shape": "empty", "path": "", "hash": ""}
        else:
            entries[sel] = {"shape": "string", "path": "", "hash": val}
    rec = entries.get(selector)
    if rec is None:
        identity = "omitted"
        path = ""
        hash_v = ""
        shape = "omitted"
        legacy = ""
    else:
        shape = rec["shape"]
        path = rec.get("path") or ""
        hash_v = rec.get("hash") or ""
        if shape == "object":
            identity = "object"
            legacy = hash_v
        elif shape == "empty" or hash_v == "":
            identity = "empty"
            legacy = ""
        else:
            identity = "hash-only"
            legacy = ""
    report = (
        f"selector\t{selector}\n"
        f"identity\t{identity}\n"
        f"shape\t{shape}\n"
        f"path\t{path or EMPTY}\n"
        f"hash\t{hash_v or EMPTY}\n"
        f"legacy_dot_hash\t{legacy or EMPTY}\n"
    )
    return {"identity": identity, "shape": shape, "rc": 0 if identity == "object" else 1, "stdout": report}


def two_grep_sticker(text: str, selector: str) -> dict:
    """Independent mapping-vs-string classifier + identity sticker. No nested YAML parser."""
    in_block = False
    last_line = None
    nested_path = ""
    nested_hash = ""
    saw_nested = False
    for raw in text.splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        if raw.startswith("patchedDependencies:"):
            in_block = True
            continue
        if not in_block:
            continue
        m = re.match(r"^(\s*)([^:]+):(.*)$", raw)
        if not m:
            continue
        indent, key, rest = m.group(1), m.group(2).strip(), m.group(3).strip().strip('"').strip("'")
        if len(indent) == 0:
            # same as CLI: unindented line is another selector
            if key == selector:
                last_line = rest
                nested_path = ""
                nested_hash = ""
                saw_nested = False
            continue
        if key == selector and (len(indent) == 2 or last_line is None or key == selector):
            # indent-2 selector line (also 4-space if current is None, CLI treats as selector)
            if len(indent) == 2 or (not saw_nested and key == selector and last_line is None):
                last_line = rest
                nested_path = ""
                nested_hash = ""
                saw_nested = False
                continue
        if last_line is not None and len(indent) >= 2 and key in ("path", "hash"):
            saw_nested = True
            if key == "path":
                nested_path = rest
            else:
                nested_hash = rest
    if last_line is None and not saw_nested:
        # search indent-2 selector only
        for raw in text.splitlines():
            m = re.match(r"^  ([^:]+):(.*)$", raw)
            if not m:
                continue
            key = m.group(1).strip()
            rest = m.group(2).strip().strip('"').strip("'")
            if key != selector:
                continue
            last_line = rest
            break
        else:
            identity = "omitted"
            shape = "omitted"
            path = EMPTY
            hash_v = EMPTY
            legacy = EMPTY
            rc = 1
            return {
                "identity": identity,
                "shape": shape,
                "path": path,
                "hash": hash_v,
                "legacy_dot_hash": legacy,
                "rc": rc,
            }

    if saw_nested:
        identity = "object"
        shape = "object"
        path = nested_path or EMPTY
        hash_v = nested_hash or EMPTY
        legacy = nested_hash or EMPTY
        rc = 0
    elif last_line == "":
        identity = "empty"
        shape = "empty"
        path = EMPTY
        hash_v = EMPTY
        legacy = EMPTY
        rc = 1
    else:
        identity = "hash-only"
        shape = "string"
        path = EMPTY
        hash_v = last_line or EMPTY
        legacy = EMPTY
        rc = 1
    return {
        "identity": identity,
        "shape": shape,
        "path": path,
        "hash": hash_v,
        "legacy_dot_hash": legacy,
        "rc": rc,
    }


def sticker_report(sel: str, st: dict) -> str:
    return (
        f"selector\t{sel}\n"
        f"identity\t{st['identity']}\n"
        f"shape\t{st['shape']}\n"
        f"path\t{st['path']}\n"
        f"hash\t{st['hash']}\n"
        f"legacy_dot_hash\t{st['legacy_dot_hash']}\n"
    )


log: list[str] = []


def rec(title: str, **kv):
    line = title + " | " + " ".join(f"{k}={v!r}" for k, v in kv.items())
    log.append(line)
    print(line, flush=True)


SCRATCH.mkdir(parents=True, exist_ok=True)

# --- identity ---
sha = subprocess.run(["shasum", "-a", "256", str(CLI)], capture_output=True, text=True, check=False)
rec("SHA256", out=sha.stdout.strip(), bytes=CLI.stat().st_size)
wt = (ROOT / "WORKTREE.txt").read_text().strip()
rec("WORKTREE", path=wt, exists=Path(wt).exists())
wt_cli = Path(wt) / "patchident" / "patchident"
if wt_cli.is_file():
    rec("WORKTREE_EQ_ARCHIVE", eq=wt_cli.read_bytes() == CLI.read_bytes(), wt_cli=str(wt_cli))
else:
    rec("WORKTREE_CLI_MISSING", path=str(wt_cli))
pnpm = subprocess.run(["command", "-v", "pnpm"], capture_output=True, text=True, check=False, shell=True)
rec("PNPM_ON_PATH", path=pnpm.stdout.strip(), executed=False)
pyv = subprocess.run([PY, "-V"], capture_output=True, text=True, check=False)
rec("PYTHON", v=pyv.stdout.strip() or pyv.stderr.strip())

# --- tests ---
t = subprocess.run(
    [PY, "-m", "unittest", "discover", "-s", str(ROOT / "tests"), "-v"],
    capture_output=True,
    text=True,
    check=False,
    cwd=str(ROOT),
)
rec("UNITTEST", rc=t.returncode, tail=(t.stderr.strip().splitlines()[-4:] + t.stdout.strip().splitlines()[-4:]))

# --- demo ---
d1 = subprocess.run(["bash", str(ROOT / "demo.sh")], capture_output=True, text=True, check=False, cwd=str(ROOT))
(SCRATCH / "demo-live.log").write_text(d1.stdout, encoding="utf-8")
rec(
    "DEMO",
    rc=d1.returncode,
    stdout_len=len(d1.stdout),
    stderr=d1.stderr.strip()[:200],
    matches_demo1=d1.stdout == (ROOT / "demo-1.log").read_text(),
    matches_demo2=d1.stdout == (ROOT / "demo-2.log").read_text(),
)

# --- owned ---
owned = [
    ("object", FIX / "patcheddeps.object.yaml", "express@4.18.1"),
    ("hash", FIX / "patcheddeps.hash.yaml", "express@4.18.1"),
    ("empty", FIX / "patcheddeps.empty.yaml", "express@4.18.1"),
    ("omitted", FIX / "patcheddeps.hash.yaml", "missing-package@1.0.0"),
]
for label, path, sel in owned:
    p = run(str(path), sel)
    rows = parse_rows(p.stdout)
    rec(
        f"OWNED_{label}",
        rc=p.returncode,
        identity=rows.get("identity"),
        shape=rows.get("shape"),
        path=rows.get("path"),
        hash=rows.get("hash"),
        legacy=rows.get("legacy_dot_hash"),
        stderr=p.stderr.strip(),
    )

# fixtures vs spec
for name in ("patcheddeps.object.yaml", "patcheddeps.hash.yaml"):
    rec(f"FIX_EQ_{name}", eq=(FIX / name).read_text() == (SPEC / name).read_text())

# --- two greps ---
obj = SPEC / "patcheddeps.object.yaml"
hsh = SPEC / "patcheddeps.hash.yaml"
for label, path in (("object", obj), ("hash", hsh)):
    g = subprocess.run(["grep", "express@4.18.1", str(path)], capture_output=True, text=True, check=False)
    rec(f"GREP_SELECTOR_{label}", rc=g.returncode, nlines=len(g.stdout.splitlines()), hits=g.stdout.splitlines())

g_map_obj = subprocess.run(["grep", "-E", r"^  express@4\.18\.1:$", str(obj)], capture_output=True, text=True, check=False)
g_map_hsh = subprocess.run(["grep", "-E", r"^  express@4\.18\.1:$", str(hsh)], capture_output=True, text=True, check=False)
g_str_obj = subprocess.run(["grep", "-E", r"^  express@4\.18\.1: .+", str(obj)], capture_output=True, text=True, check=False)
g_str_hsh = subprocess.run(["grep", "-E", r"^  express@4\.18\.1: .+", str(hsh)], capture_output=True, text=True, check=False)
g_empty = subprocess.run(
    ["grep", "-E", r'^  express@4\.18\.1: ""$', str(FIX / "patcheddeps.empty.yaml")],
    capture_output=True,
    text=True,
    check=False,
)
g_omit_obj = subprocess.run(["grep", "-E", r"^  missing-package@1\.0\.0:", str(hsh)], capture_output=True, text=True, check=False)
rec("GREP_MAPPING_object", rc=g_map_obj.returncode, out=g_map_obj.stdout.strip())
rec("GREP_MAPPING_hash", rc=g_map_hsh.returncode, out=g_map_hsh.stdout.strip())
rec("GREP_STRING_object", rc=g_str_obj.returncode, out=g_str_obj.stdout.strip())
rec("GREP_STRING_hash", rc=g_str_hsh.returncode, out=g_str_hsh.stdout.strip())
rec("GREP_EMPTY", rc=g_empty.returncode, out=g_empty.stdout.strip())
rec("GREP_OMITTED", rc=g_omit_obj.returncode, out=g_omit_obj.stdout.strip())

# nested path/hash greps on object
g_path = subprocess.run(["grep", "-E", r"^    path:", str(obj)], capture_output=True, text=True, check=False)
g_hashf = subprocess.run(["grep", "-E", r"^    hash:", str(obj)], capture_output=True, text=True, check=False)
g_path_h = subprocess.run(["grep", "-E", r"^    path:", str(hsh)], capture_output=True, text=True, check=False)
rec("GREP_NESTED_path_object", rc=g_path.returncode, out=g_path.stdout.strip())
rec("GREP_NESTED_hash_object", rc=g_hashf.returncode, out=g_hashf.stdout.strip())
rec("GREP_NESTED_path_hashfile", rc=g_path_h.returncode, out=g_path_h.stdout.strip())

# --- hashes unused ---
obj_aaa = write_tmp(
    "object-aaa.yaml",
    "patchedDependencies:\n  express@4.18.1:\n    path: patches/express@4.18.1.patch\n    hash: AAA\n",
)
hash_aaa = write_tmp("hash-aaa.yaml", "patchedDependencies:\n  express@4.18.1: AAA\n")
p_aaa_o = run(str(obj_aaa), SEL)
p_aaa_h = run(str(hash_aaa), SEL)
p_obj = run(str(FIX / "patcheddeps.object.yaml"), SEL)
p_hash = run(str(FIX / "patcheddeps.hash.yaml"), SEL)
rec("HASH_UNUSED_object_AAA", rc=p_aaa_o.returncode, identity=parse_rows(p_aaa_o.stdout).get("identity"), hash=parse_rows(p_aaa_o.stdout).get("hash"), legacy=parse_rows(p_aaa_o.stdout).get("legacy_dot_hash"))
rec("HASH_UNUSED_hash_AAA", rc=p_aaa_h.returncode, identity=parse_rows(p_aaa_h.stdout).get("identity"), hash=parse_rows(p_aaa_h.stdout).get("hash"), legacy=parse_rows(p_aaa_h.stdout).get("legacy_dot_hash"))
rec(
    "HASH_UNUSED_kind_stable",
    object_id_same=parse_rows(p_obj.stdout)["identity"] == parse_rows(p_aaa_o.stdout)["identity"],
    hash_id_same=parse_rows(p_hash.stdout)["identity"] == parse_rows(p_aaa_h.stdout)["identity"],
    object_rc_same=p_obj.returncode == p_aaa_o.returncode,
    hash_rc_same=p_hash.returncode == p_aaa_h.returncode,
    object_legacy_follows_hash=parse_rows(p_aaa_o.stdout)["legacy_dot_hash"] == "AAA",
    hash_legacy_dash=parse_rows(p_aaa_h.stdout)["legacy_dot_hash"] == "-",
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
    p = run(str(FIX / "patcheddeps.object.yaml"), sel)
    rec("PREFIX_object", selector=sel, rc=p.returncode, identity=parse_rows(p.stdout).get("identity"), stderr=p.stderr.strip()[:80])
    p = run(str(FIX / "patcheddeps.hash.yaml"), sel)
    rec("PREFIX_hash", selector=sel, rc=p.returncode, identity=parse_rows(p.stdout).get("identity"))

both = write_tmp(
    "prefix-pair.yaml",
    "patchedDependencies:\n  express@4.18.1: hash-short\n  express@4.18.10: hash-long\n",
)
for sel in ("express@4.18.1", "express@4.18.10", "express@4.18", "express@4.18.1 "):
    p = run(str(both), sel)
    rec("PREFIX_pair", selector=sel, rc=p.returncode, identity=parse_rows(p.stdout).get("identity"), hash=parse_rows(p.stdout).get("hash"))

# --- stdin / missing ---
p = run("-", SEL, stdin=(FIX / "patcheddeps.object.yaml").read_text())
rec("STDIN_object", rc=p.returncode, identity=parse_rows(p.stdout).get("identity"), legacy=parse_rows(p.stdout).get("legacy_dot_hash"))
p = run("-", SEL, stdin=(FIX / "patcheddeps.hash.yaml").read_text())
rec("STDIN_hash", rc=p.returncode, identity=parse_rows(p.stdout).get("identity"), legacy=parse_rows(p.stdout).get("legacy_dot_hash"))
p = run("-", SEL, stdin=(FIX / "patcheddeps.empty.yaml").read_text())
rec("STDIN_empty", rc=p.returncode, identity=parse_rows(p.stdout).get("identity"))
p = run("/no/such.yaml", SEL)
rec("MISSING", rc=p.returncode, stdout=p.stdout, stderr=p.stderr.strip())
p = run(str(FIX), SEL)
rec("DIRECTORY", rc=p.returncode, stderr=p.stderr.strip())
p = subprocess.run([PY, str(CLI)], capture_output=True, text=True, check=False)
rec("NOARGS", rc=p.returncode, stderr=p.stderr.strip().splitlines()[-1:])
p = subprocess.run([PY, str(CLI), str(FIX / "patcheddeps.hash.yaml")], capture_output=True, text=True, check=False)
rec("NOSELECTOR", rc=p.returncode, stderr=p.stderr.strip().splitlines()[-1:])
p = subprocess.run(
    [PY, str(CLI), str(FIX / "patcheddeps.hash.yaml"), "--selector", SEL],
    input="patchedDependencies:\n  express@4.18.1: FROMSTDIN\n",
    capture_output=True,
    text=True,
    check=False,
)
rec("STDIN_IGNORED_WHEN_FILE", rc=p.returncode, identity=parse_rows(p.stdout).get("identity"), hash=parse_rows(p.stdout).get("hash"))

# --- replica cases ---
cases = [
    ("owned-object", (FIX / "patcheddeps.object.yaml").read_text(), SEL),
    ("owned-hash", (FIX / "patcheddeps.hash.yaml").read_text(), SEL),
    ("owned-empty", (FIX / "patcheddeps.empty.yaml").read_text(), SEL),
    ("owned-omitted", (FIX / "patcheddeps.hash.yaml").read_text(), "missing-package@1.0.0"),
    ("aaa-object", obj_aaa.read_text(), SEL),
    ("aaa-hash", hash_aaa.read_text(), SEL),
    ("bare-object-no-body", "patchedDependencies:\n  express@4.18.1:\n", SEL),
    ("path-only", "patchedDependencies:\n  express@4.18.1:\n    path: patches/x.patch\n", SEL),
    ("hash-field-only", "patchedDependencies:\n  express@4.18.1:\n    hash: onlyhash\n", SEL),
    ("quoted-sel-hash", "patchedDependencies:\n  'express@4.18.1': fixture-patch-hash\n", SEL),
    ("quoted-sel-obj", 'patchedDependencies:\n  "express@4.18.1":\n    path: p\n    hash: h\n', SEL),
    ("lockfileVersion-before", "lockfileVersion: '9.0'\n\npatchedDependencies:\n  express@4.18.1: abc\npackages:\n  /express@4.18.1:\n    resolution: {integrity: x}\n", SEL),
    ("comment", "# c\npatchedDependencies:\n  # inner\n  express@4.18.1: abc\n", SEL),
    ("dup-last-wins", "patchedDependencies:\n  express@4.18.1: first\n  express@4.18.1:\n    path: p\n    hash: second\n", SEL),
    ("hash-then-nested", "patchedDependencies:\n  express@4.18.1: first\n    path: sneaky\n", SEL),
    ("flow", "patchedDependencies:\n  express@4.18.1: {path: p, hash: h}\n", SEL),
    ("null-token", "patchedDependencies:\n  express@4.18.1: null\n", SEL),
    ("tilde", "patchedDependencies:\n  express@4.18.1: ~\n", SEL),
    ("no-block", "packages:\n  express@4.18.1: x\n", SEL),
    ("tab-indent", "patchedDependencies:\n\texpress@4.18.1: abc\n", SEL),
    ("four-space-sel", "patchedDependencies:\n    express@4.18.1: abc\n", SEL),
    ("crlf", "patchedDependencies:\r\n  express@4.18.1: abc\r\n", SEL),
    ("prefix-pair-short", both.read_text(), "express@4.18.1"),
    ("prefix-pair-long", both.read_text(), "express@4.18.10"),
    ("empty-sq", "patchedDependencies:\n  express@4.18.1: ''\n", SEL),
    ("colon-trailing-space", "patchedDependencies:\n  express@4.18.1:   \n", SEL),
    ("spec-object", (SPEC / "patcheddeps.object.yaml").read_text(), SEL),
    ("spec-hash", (SPEC / "patcheddeps.hash.yaml").read_text(), SEL),
]

replica_rows = []
for label, text, sel in cases:
    tmp = write_tmp(f"case-{label}.yaml", text)
    p = run(str(tmp), sel)
    cli_id = parse_rows(p.stdout).get("identity")
    try:
        full = replica_full(text, sel)
        full_ok = full["stdout"] == p.stdout and full["rc"] == p.returncode
        full_err = ""
    except Exception as e:
        full_ok = False
        full_err = str(e)
        full = {"identity": "ERR", "rc": None, "stdout": ""}
    st = two_grep_sticker(text, sel)
    st_report = sticker_report(sel, st)
    # sticker compared on identity+rc primarily; full stdout when parseable
    ks_ok = st["identity"] == cli_id and st["rc"] == p.returncode
    replica_rows.append(
        {
            "label": label,
            "cli_identity": cli_id,
            "cli_rc": p.returncode,
            "cli_stderr": p.stderr.strip()[:120],
            "cli_stdout": p.stdout,
            "full_ok": full_ok,
            "full_identity": full.get("identity"),
            "full_err": full_err,
            "st_identity": st["identity"],
            "st_rc": st["rc"],
            "st_ok": ks_ok,
            "st_stdout_eq": st_report == p.stdout,
        }
    )
    rec(
        "REPLICA",
        label=label,
        cli_identity=cli_id,
        cli_rc=p.returncode,
        full_ok=full_ok,
        st_ok=ks_ok,
        st_identity=st["identity"],
        st_stdout_eq=(st_report == p.stdout),
        stderr=p.stderr.strip()[:80],
    )

# extra field
extra = "patchedDependencies:\n  express@4.18.1:\n    path: p\n    hash: h\n    extra: z\n"
p = run(str(write_tmp("extra.yaml", extra)), SEL)
rec("EXTRA_FIELD", rc=p.returncode, stdout=p.stdout, stderr=p.stderr.strip())

# BOM
bom = "\ufeffpatchedDependencies:\n  express@4.18.1: abc\n"
p = run(str(write_tmp("bom.yaml", bom)), SEL)
rec("BOM", rc=p.returncode, identity=parse_rows(p.stdout).get("identity"), stderr=p.stderr.strip()[:80])

# emptyish
for label, text in (("emptyfile", ""), ("comments", "# only\n"), ("devnull_like", "\n")):
    p = run(str(write_tmp(f"{label}.yaml", text)), SEL)
    rec("EMPTYISH", label=label, rc=p.returncode, identity=parse_rows(p.stdout).get("identity"), stderr=p.stderr.strip()[:80])

# huge
lines = ["patchedDependencies:"]
for i in range(5000):
    lines.append(f"  other@{i}: hash{i}")
lines.append("  express@4.18.1: targethash")
huge = write_tmp("huge.yaml", "\n".join(lines) + "\n")
p = run(str(huge), SEL)
rec("HUGE", rc=p.returncode, identity=parse_rows(p.stdout).get("identity"), hash=parse_rows(p.stdout).get("hash"), bytes=huge.stat().st_size)

# YAML | multiline
p = run(str(write_tmp("pipe.yaml", "patchedDependencies:\n  express@4.18.1: |\n    abc\n")), SEL)
rec("PIPE_MULTILINE", rc=p.returncode, identity=parse_rows(p.stdout).get("identity"), hash=parse_rows(p.stdout).get("hash"), shape=parse_rows(p.stdout).get("shape"), stderr=p.stderr.strip()[:80])

# symlink
link = SCRATCH / "link-hash.yaml"
if link.exists() or link.is_symlink():
    link.unlink()
link.symlink_to(FIX / "patcheddeps.hash.yaml")
p = run(str(link), SEL)
rec("SYMLINK", rc=p.returncode, identity=parse_rows(p.stdout).get("identity"))

# /dev/stdin
p = subprocess.run(
    [PY, str(CLI), "/dev/stdin", "--selector", SEL],
    input=(FIX / "patcheddeps.hash.yaml").read_text(),
    capture_output=True,
    text=True,
    check=False,
)
rec("DEV_STDIN", rc=p.returncode, identity=parse_rows(p.stdout).get("identity"), legacy=parse_rows(p.stdout).get("legacy_dot_hash"))

# after-block packages swallowed as selectors
swallow = write_tmp(
    "after-block.yaml",
    "patchedDependencies:\n  express@4.18.1: abc\npackages:\n  /express@4.18.1:\n    resolution: {integrity: x}\n",
)
p = run(str(swallow), SEL)
rec("AFTER_BLOCK_hash", rc=p.returncode, identity=parse_rows(p.stdout).get("identity"), hash=parse_rows(p.stdout).get("hash"))
p = run(str(swallow), "packages")
rec("AFTER_BLOCK_packages_as_selector", rc=p.returncode, identity=parse_rows(p.stdout).get("identity"), shape=parse_rows(p.stdout).get("shape"), stdout=p.stdout)
p = run(str(swallow), "/express@4.18.1")
rec("AFTER_BLOCK_pkg_key", rc=p.returncode, identity=parse_rows(p.stdout).get("identity"), stdout=p.stdout, stderr=p.stderr.strip()[:80])

# header with extra
p = run(str(write_tmp("header-extra.yaml", "patchedDependencies: leftover\n  express@4.18.1: abc\n")), SEL)
rec("HEADER_EXTRA", rc=p.returncode, identity=parse_rows(p.stdout).get("identity"), hash=parse_rows(p.stdout).get("hash"), stderr=p.stderr.strip()[:80])

# quoted selector lookup vs stored key
p = run(str(write_tmp("quoted-lookup.yaml", "patchedDependencies:\n  'express@4.18.1': abc\n")), SEL)
rec("QUOTED_SEL_UNSTRIPPED", rc=p.returncode, identity=parse_rows(p.stdout).get("identity"), stderr=p.stderr.strip()[:80])
p = run(str(write_tmp("quoted-lookup.yaml", "patchedDependencies:\n  'express@4.18.1': abc\n")), "'express@4.18.1'")
rec("QUOTED_SEL_WITH_QUOTES", rc=p.returncode, identity=parse_rows(p.stdout).get("identity"), hash=parse_rows(p.stdout).get("hash"))

# patchident vs patchid rc polarity
PID = RUN / "lineages" / "candidate-patchid" / "patchid"
if PID.exists():
    for label, path in (("object", FIX / "patcheddeps.object.yaml"), ("hash", FIX / "patcheddeps.hash.yaml")):
        a = run(str(path), SEL)
        b = subprocess.run([PY, str(PID), str(path), "--selector", SEL], capture_output=True, text=True, check=False)
        rec(
            "POLARITY",
            label=label,
            patchident_rc=a.returncode,
            patchident_id=parse_rows(a.stdout).get("identity"),
            patchid_rc=b.returncode,
            patchid_kind=parse_rows(b.stdout).get("kind"),
        )

# inspect names
src = CLI.read_text()
rec(
    "SOURCE",
    has_pnpm="pnpm" in src.lower(),
    has_hashlib="hashlib" in src,
    has_compare_patch=".patch" in src and "read_bytes" in src,
    legacy_comment="originalPatchFile" in src,
    lines=src.count("\n") + 1,
)

# sticker on owned four
sticker_owned = []
for label, path, sel in owned:
    text = path.read_text()
    p = run(str(path), sel)
    st = two_grep_sticker(text, sel)
    full = replica_full(text, sel)
    sticker_owned.append(
        {
            "label": label,
            "cli": parse_rows(p.stdout),
            "cli_rc": p.returncode,
            "st": st,
            "st_stdout_eq": sticker_report(sel, st) == p.stdout,
            "full_ok": full["stdout"] == p.stdout and full["rc"] == p.returncode,
        }
    )
    rec("STICKER_OWNED", label=label, st_stdout_eq=(sticker_report(sel, st) == p.stdout), full_ok=True, st=st, cli_rc=p.returncode)

summary = {
    "replica_full_all": all(r["full_ok"] for r in replica_rows if r["cli_stderr"] == ""),
    "sticker_identity_rc_when_cli_ok": all(r["st_ok"] for r in replica_rows if r["cli_identity"] is not None and r["cli_stderr"] == ""),
    "sticker_stdout_eq_when_cli_ok": all(r["st_stdout_eq"] for r in replica_rows if r["cli_stderr"] == ""),
    "sticker_mismatches": [r["label"] for r in replica_rows if not r["st_ok"]],
    "sticker_stdout_mismatches": [r["label"] for r in replica_rows if not r["st_stdout_eq"]],
    "full_mismatches": [r["label"] for r in replica_rows if not r["full_ok"]],
    "n_cases": len(replica_rows),
    "owned_sticker_eq": all(x["st_stdout_eq"] for x in sticker_owned),
}
rec("SUMMARY", **summary)
(SCRATCH / "replica.json").write_text(json.dumps({"rows": replica_rows, "owned": sticker_owned, "summary": summary}, indent=2), encoding="utf-8")
(SCRATCH / "attacks.log").write_text("\n".join(log) + "\n", encoding="utf-8")
print("---SUMMARY---")
print(json.dumps(summary, indent=2))
