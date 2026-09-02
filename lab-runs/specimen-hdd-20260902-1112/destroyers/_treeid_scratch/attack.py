#!/usr/bin/env python3
from __future__ import annotations

import os
import stat
import subprocess
import sys
import time
import types
from pathlib import Path

ROOT = Path(
    "/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-treeid"
)
CLI = ROOT / "treeid"
FIX = ROOT / "fixtures"
SCRATCH = Path(__file__).resolve().parent

mod = types.ModuleType("treeid")
exec(compile(CLI.read_text(), str(CLI), "exec"), mod.__dict__)
print("inspect.co_names", mod.inspect.__code__.co_names)
print("parse_record.co_names", mod.parse_record.__code__.co_names)
print("format_report.co_names", mod.format_report.__code__.co_names)
print("KNOWN", mod.KNOWN)


def sh(*args, input=None, timeout=15):
    return subprocess.run(list(args), input=input, capture_output=True, text=True, timeout=timeout)


def run_cli(path_or_dash, stdin=None, timeout=15):
    return sh(sys.executable, str(CLI), path_or_dash, input=stdin, timeout=timeout)


def replica(text, source="rec"):
    fields = mod.parse_record(text, source=source)
    result = mod.inspect(fields)
    out = mod.format_report(result)
    rc = 1 if result["hidden_by_omitted_names"] else 0
    return out, rc, result


def write_rec(name, lines):
    p = SCRATCH / name
    p.write_text("\n".join(lines) + "\n")
    return p


def awk_two_flags(text):
    ident = load = ""
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "\t" not in line:
            continue
        k, v = line.split("\t", 1)
        k, v = k.strip(), v.strip()
        if k == "stored_identity":
            ident = v
        elif k == "load_after_add":
            load = v
    omitted = ident in {"dir+pattern", "dir-pattern", "tree"}
    loadb = load in {"yes", "true", "load"}
    return omitted, loadb, omitted and loadb


def is_regular(p: Path) -> bool:
    try:
        return stat.S_ISREG(p.stat().st_mode)
    except OSError:
        return False


print("\n=== OWNED ===")
for f in sorted(FIX.iterdir()):
    if not is_regular(f):
        continue
    text = f.read_text()
    proc = run_cli(str(f))
    out_r, rc_r, _ = replica(text, source=str(f))
    print(
        f.name,
        "cli_rc",
        proc.returncode,
        "replica_eq",
        proc.stdout == out_r and proc.returncode == rc_r,
        "bytes",
        len(proc.stdout),
    )
    print(proc.stdout, end="")

print("\n=== ATTACKS ===")
attacks = {
    "contradict-omit-noload.rec": [
        "kind\tfileTree",
        "dir\tsrc",
        "pattern\t*",
        "names\tfile1,file2",
        "added\tfile3",
        "stored_identity\tdir+pattern",
        "load_after_add\tno",
    ],
    "contradict-names-load.rec": [
        "kind\tnamed",
        "names\tfile1,file2",
        "added\tfile3",
        "stored_identity\tnames",
        "load_after_add\tyes",
    ],
    "case-c-never-queried.rec": [
        "kind\tfileTree",
        "dir\tsrc",
        "pattern\t*",
        "names\t-",
        "added\tfile3",
        "stored_identity\tdir+pattern",
        "load_after_add\tyes",
    ],
    "only-two-flags-hidden.rec": ["stored_identity\tdir+pattern", "load_after_add\tyes"],
    "only-two-flags-miss.rec": ["stored_identity\tnames", "load_after_add\tno"],
    "ident-dir-pattern.rec": ["stored_identity\tdir-pattern", "load_after_add\tyes"],
    "ident-tree.rec": ["stored_identity\ttree", "load_after_add\tyes"],
    "ident-TREE.rec": ["stored_identity\tTREE", "load_after_add\tyes"],
    "ident-Dir+Pattern.rec": ["stored_identity\tDir+Pattern", "load_after_add\tyes"],
    "ident-dir_pattern.rec": ["stored_identity\tdir_pattern", "load_after_add\tyes"],
    "ident-dir+pattern+names.rec": ["stored_identity\tdir+pattern+names", "load_after_add\tyes"],
    "ident-contents.rec": ["stored_identity\tcontents", "load_after_add\tyes"],
    "ident-fingerprint.rec": ["stored_identity\tfingerprint", "load_after_add\tyes"],
    "ident-WorkInputs.rec": ["stored_identity\tWorkInputs", "load_after_add\tyes"],
    "ident-dash.rec": ["stored_identity\t-", "load_after_add\tyes"],
    "load-true.rec": ["stored_identity\tdir+pattern", "load_after_add\ttrue"],
    "load-load.rec": ["stored_identity\tdir+pattern", "load_after_add\tload"],
    "load-YES.rec": ["stored_identity\tdir+pattern", "load_after_add\tYES"],
    "load-True.rec": ["stored_identity\tdir+pattern", "load_after_add\tTrue"],
    "load-1.rec": ["stored_identity\tdir+pattern", "load_after_add\t1"],
    "load-hit.rec": ["stored_identity\tdir+pattern", "load_after_add\thit"],
    "load-reused.rec": ["stored_identity\tdir+pattern", "load_after_add\treused"],
    "load-missing.rec": ["stored_identity\tdir+pattern"],
    "spectator-wrong.rec": [
        "kind\tnamed",
        "dir\tNOTSRC",
        "pattern\tNONE",
        "names\tNEVER",
        "added\tALSO",
        "stored_identity\tdir+pattern",
        "load_after_add\tyes",
    ],
    "added-in-names-still-hidden.rec": [
        "kind\tfileTree",
        "names\tfile1,file2,file3",
        "added\tfile3",
        "stored_identity\tdir+pattern",
        "load_after_add\tyes",
    ],
    "last-wins-ident.rec": [
        "stored_identity\tnames",
        "load_after_add\tyes",
        "stored_identity\tdir+pattern",
    ],
    "last-wins-load.rec": [
        "stored_identity\tdir+pattern",
        "load_after_add\tyes",
        "load_after_add\tno",
    ],
    "kind-filetree-names-ident.rec": [
        "kind\tfileTree",
        "stored_identity\tnames",
        "load_after_add\tno",
    ],
    "comments-ok.rec": ["# comment", "", "stored_identity\tdir+pattern", "load_after_add\tyes"],
    "unicode-names.rec": [
        "stored_identity\tdir+pattern",
        "names\tファイル1",
        "added\tファイル3",
        "load_after_add\tyes",
    ],
}
for name, lines in attacks.items():
    p = write_rec(name, lines)
    proc = run_cli(str(p))
    try:
        out_r, rc_r, _ = replica(p.read_text(), source=name)
        eq = proc.stdout == out_r and proc.returncode == rc_r
    except Exception as e:
        eq = f"err {e}"
    awk = awk_two_flags(p.read_text())
    d = {}
    for ln in proc.stdout.splitlines():
        if "\t" in ln:
            k, v = ln.split("\t", 1)
            d[k] = v
    hidden = d.get("hidden_by_omitted_names") or proc.stderr.strip()[:80]
    print(
        f"{name}\trc={proc.returncode}\tident={d.get('stored_identity')}\tomitted={d.get('omitted_names')}\tload={d.get('load_after_add')}\thidden={hidden}\treplica_eq={eq}\tawk={awk}"
    )
    if proc.stderr:
        print("  stderr:", proc.stderr.strip()[:180])

print("\n=== trailing empty values ===")
p = SCRATCH / "load-empty.rec"
p.write_text("stored_identity\tdir+pattern\nload_after_add\t\n")
proc = run_cli(str(p))
print("load-empty rc", proc.returncode, "stderr", proc.stderr.strip(), "out", repr(proc.stdout[:80]))
p = SCRATCH / "ident-empty.rec"
p.write_text("stored_identity\t\nload_after_add\tyes\n")
proc = run_cli(str(p))
print("ident-empty rc", proc.returncode, "stderr", proc.stderr.strip(), "out", repr(proc.stdout[:80]))

print("\n=== PARSE/IO ===")
proc = run_cli("/no/such/treeid")
print("missing", proc.returncode, proc.stderr.strip())
proc = run_cli(str(ROOT))
print("directory", proc.returncode, proc.stderr.strip())
p = SCRATCH / "empty.rec"
p.write_text("")
proc = run_cli(str(p))
print("empty", proc.returncode, proc.stderr.strip(), repr(proc.stdout))
p = SCRATCH / "comments-only.rec"
p.write_text("# hi\n\n")
proc = run_cli(str(p))
print("comments-only", proc.returncode, proc.stderr.strip())
proc = run_cli("/dev/null")
print("devnull", proc.returncode, proc.stderr.strip())
proc = sh(sys.executable, str(CLI))
print("noargs", proc.returncode, proc.stderr.strip().splitlines()[-1] if proc.stderr else "")
proc = sh(sys.executable, str(CLI), str(FIX / "088-filetree.rec"), "extra")
print("extraarg", proc.returncode, proc.stderr.strip().splitlines()[0] if proc.stderr else "")
p = write_rec("unknown.rec", ["stored_identity\tdir+pattern", "foo\tbar", "load_after_add\tyes"])
proc = run_cli(str(p))
print("unknown", proc.returncode, proc.stderr.strip())
p = write_rec("spaces.rec", ["stored_identity dir+pattern"])
proc = run_cli(str(p))
print("spaces", proc.returncode, proc.stderr.strip())
p = write_rec("capital.rec", ["Stored_identity\tdir+pattern", "load_after_add\tyes"])
proc = run_cli(str(p))
print("capital", proc.returncode, proc.stderr.strip())
p = SCRATCH / "bom.rec"
p.write_bytes(b"\xef\xbb\xbfstored_identity\tdir+pattern\nload_after_add\tyes\n")
proc = run_cli(str(p))
print("bom", proc.returncode, proc.stderr.strip()[:140], "out", proc.stdout[:40].replace("\n", "|"))
p = SCRATCH / "badutf.rec"
p.write_bytes(b"stored_identity\tdir+pattern\nload_after_add\t\xff\n")
proc = run_cli(str(p))
print("badutf", proc.returncode, proc.stderr.strip()[:160])
p = SCRATCH / "crlf.rec"
p.write_bytes(b"stored_identity\tdir+pattern\r\nload_after_add\tyes\r\n")
proc = run_cli(str(p))
print("crlf", proc.returncode, [ln for ln in proc.stdout.splitlines() if ln.startswith("hidden")])
body = (FIX / "088-filetree.rec").read_text()
proc = run_cli("-", stdin=body)
print(
    "stdin-dash",
    proc.returncode,
    [ln for ln in proc.stdout.splitlines() if ln.startswith("hidden")],
    "stderr",
    proc.stderr.strip()[:90],
)
proc = subprocess.run(
    [sys.executable, str(CLI)], input=body, capture_output=True, text=True, timeout=10
)
print("argvless-pipe", proc.returncode, proc.stderr.strip().splitlines()[0] if proc.stderr else "")
proc = subprocess.run(
    [sys.executable, str(CLI), "/dev/stdin"],
    input=body,
    capture_output=True,
    text=True,
    timeout=10,
)
print("devstdin", proc.returncode, [ln for ln in proc.stdout.splitlines() if ln.startswith("hidden")])
proc = subprocess.run(
    ["bash", "-lc", f"python3 '{CLI}' <(cat '{FIX / '088-filetree.rec'}')"],
    capture_output=True,
    text=True,
    timeout=10,
)
print("procsub", proc.returncode, [ln for ln in proc.stdout.splitlines() if ln.startswith("hidden")])
link = SCRATCH / "link.rec"
if link.exists() or link.is_symlink():
    link.unlink()
link.symlink_to(FIX / "088-filetree.rec")
proc = run_cli(str(link))
print("symlink", proc.returncode, [ln for ln in proc.stdout.splitlines() if ln.startswith("hidden")])
sp = SCRATCH / "has space.rec"
sp.write_text(body)
proc = run_cli(str(sp))
print("space-name", proc.returncode, [ln for ln in proc.stdout.splitlines() if ln.startswith("hidden")])
huge = ",".join(f"f{i}" for i in range(10000))
p = write_rec(
    "huge-names.rec",
    [f"names\t{huge}", "added\tf99999", "stored_identity\tdir+pattern", "load_after_add\tyes"],
)
t0 = time.perf_counter()
proc = run_cli(str(p))
dt = time.perf_counter() - t0
names_row = [ln for ln in proc.stdout.splitlines() if ln.startswith("names\t")][0]
print(
    "huge-names",
    proc.returncode,
    "stdout_bytes",
    len(proc.stdout),
    "s",
    round(dt, 4),
    [ln for ln in proc.stdout.splitlines() if ln.startswith("hidden")],
    "names_len",
    len(names_row),
)
p = write_rec(
    "tab-in-value.rec",
    ["stored_identity\tdir+pattern", "names\tfile1\tfile2", "load_after_add\tyes"],
)
proc = run_cli(str(p))
print("tab-in-value", proc.returncode, [ln for ln in proc.stdout.splitlines() if ln.startswith("names")])
p = write_rec("no-ident.rec", ["load_after_add\tyes", "kind\tfileTree"])
proc = run_cli(str(p))
print("no-ident", proc.returncode, proc.stderr.strip())
print("help", sh(sys.executable, str(CLI), "-h").returncode)

print("\n=== AWK ===")
awk_script = r"""BEGIN{FS="\t"} $1=="stored_identity"{i=$2} $1=="load_after_add"{l=$2} END{ omitted=(i=="dir+pattern"||i=="dir-pattern"||i=="tree"); load=(l=="yes"||l=="true"||l=="load"); hidden=(omitted && load); printf "omitted_names\t%s\n", omitted?"yes":"no"; printf "load_after_add\t%s\n", load?"yes":"no"; printf "hidden_by_omitted_names\t%s\n", hidden?"yes":"no"}"""
for f in [FIX / "088-filetree.rec", FIX / "088-named.rec"]:
    awk = sh("awk", awk_script, str(f))
    cli = run_cli(str(f))
    cli_rows = (
        "\n".join(
            ln
            for ln in cli.stdout.splitlines()
            if ln.startswith(("omitted_names", "load_after_add", "hidden_by_omitted_names"))
        )
        + "\n"
    )
    print(f.name, "awk==cli", awk.stdout == cli_rows)
    print(awk.stdout, end="")

print("\n=== ONE-LINER + REPLICA COUNTS ===")
ok = fail = skip = 0
n_eq = n_tot = 0
for rec in sorted(list(FIX.glob("*.rec")) + list(SCRATCH.glob("*.rec"))):
    if not is_regular(rec):
        skip += 1
        continue
    try:
        text = rec.read_text(encoding="utf-8")
    except Exception:
        skip += 1
        continue
    proc = run_cli(str(rec))
    if "hidden_by_omitted_names\t" not in proc.stdout:
        skip += 1
        continue
    omitted, loadb, hidden = awk_two_flags(text)
    want = "yes" if hidden else "no"
    got = [
        ln.split("\t", 1)[1]
        for ln in proc.stdout.splitlines()
        if ln.startswith("hidden_by_omitted_names\t")
    ][0]
    if got == want and proc.returncode == (1 if hidden else 0):
        ok += 1
    else:
        fail += 1
        print("MISMATCH", rec.name, want, got, proc.returncode)
    try:
        out_r, rc_r, _ = replica(text, source=str(rec))
        n_tot += 1
        if proc.stdout == out_r and proc.returncode == rc_r:
            n_eq += 1
        else:
            print("REPLICA_NE", rec.name)
    except Exception as e:
        print("REPLICA_ERR", rec.name, e)
print(f"oneliner {ok} fail {fail} skip {skip}; replica {n_eq}/{n_tot}")

print("\n=== HOST REPLICA cmp ===")


def host_inspect(fields):
    ident = fields["stored_identity"]
    omitted = ident in {"dir+pattern", "dir-pattern", "tree"}
    load = fields.get("load_after_add", "") in {"yes", "true", "load"}
    hidden = omitted and load
    yn = lambda v: "yes" if v else "no"
    lines = [
        f"kind\t{fields.get('kind') or '-'}",
        f"stored_identity\t{ident}",
        f"names\t{fields.get('names') or '-'}",
        f"added\t{fields.get('added') or '-'}",
        f"omitted_names\t{yn(omitted)}",
        f"load_after_add\t{yn(load)}",
        f"hidden_by_omitted_names\t{yn(hidden)}",
    ]
    return "\n".join(lines) + "\n", (1 if hidden else 0)


for f in [FIX / "088-filetree.rec", FIX / "088-named.rec"]:
    fields = mod.parse_record(f.read_text(), source=str(f))
    out, rc = host_inspect(fields)
    proc = run_cli(str(f))
    a = SCRATCH / f"host-{f.name}.out"
    b = SCRATCH / f"cli-{f.name}.out"
    a.write_text(out)
    b.write_text(proc.stdout)
    c = sh("cmp", str(a), str(b))
    print(f.name, "cmp", c.returncode, "rc_eq", rc == proc.returncode, "bytes", len(proc.stdout))

print("\n=== DISK TREE NEVER READ ===")
p1 = write_rec(
    "dir-missing-disk.rec",
    [
        "dir\t/no/such/src",
        "pattern\t*",
        "names\tfile1",
        "added\tfile3",
        "stored_identity\tdir+pattern",
        "load_after_add\tyes",
    ],
)
p2 = write_rec(
    "dir-this-repo.rec",
    [
        "dir\t" + str(ROOT),
        "pattern\t*",
        "names\tfile1",
        "added\tfile3",
        "stored_identity\tdir+pattern",
        "load_after_add\tyes",
    ],
)
a = run_cli(str(p1))
b = run_cli(str(p2))
print("stdout_eq", a.stdout == b.stdout, "rc", a.returncode, b.returncode)
print(
    "dir printed",
    any(ln.startswith("dir\t") for ln in a.stdout.splitlines()),
    "pattern printed",
    any(ln.startswith("pattern\t") for ln in a.stdout.splitlines()),
)

print("\n=== date ===")
print(
    sh(
        "python3",
        "-c",
        "from datetime import datetime; from zoneinfo import ZoneInfo; print(datetime.now(ZoneInfo('Asia/Tokyo')).strftime('%Y-%m-%d %H:%M JST'))",
    ).stdout.strip()
)
