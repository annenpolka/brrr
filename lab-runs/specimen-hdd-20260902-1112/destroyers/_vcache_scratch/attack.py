#!/usr/bin/env python3
from __future__ import annotations

import dis
import os
import stat
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

RUN = Path("/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112")
CLI = RUN / "lineages/candidate-vcache/vcache"
FIX = RUN / "lineages/candidate-vcache/fixtures"
SCR = RUN / "destroyers/_vcache_scratch"
S094 = RUN / "specimens/specimen-094"
SCR.mkdir(parents=True, exist_ok=True)
src = CLI.read_text(encoding="utf-8")
ns: dict = {}
exec(compile(src, str(CLI), "exec"), ns)

YES = {"yes", "true", "1"}


def run(args, stdin=None, timeout=15):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
    )


def replica(text, source="rec"):
    fields = ns["parse_record"](text, source=source)
    result = ns["inspect"](fields)
    out = ns["format_report"](result)
    rc = 1 if result["leftover_key"] else 0
    return out, rc, result


def thin_from_fields(fields):
    ext = (fields.get("externalize") or "") in YES
    key = fields.get("cache_key") or "-"
    disk = (fields.get("disk_write") or "") in YES
    leftover = ext and key not in {"", "-"} and not disk
    return ext, key, disk, leftover


def parse_simple(text):
    fields = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "\t" not in line:
            continue
        k, r = line.split("\t", 1)
        fields[k.strip()] = r.strip()
    return fields


def rec(**kw):
    return "".join(f"{k}\t{v}\n" for k, v in kw.items())


def slug(s: str) -> str:
    out = []
    for ch in s:
        out.append(ch if ch.isalnum() or ch in "._-" else "_")
    return "".join(out)[:90]


def write_tmp(name, text, encoding="utf-8", errors="strict"):
    p = SCR / slug(name)
    p.write_text(text, encoding=encoding, errors=errors)
    return p


def rows_of(stdout: str) -> dict[str, str]:
    d = {}
    for line in stdout.splitlines():
        if "\t" in line:
            k, v = line.split("\t", 1)
            d[k] = v
    return d


def awk_loadbearing(path: Path) -> dict[str, str]:
    script = r"""
BEGIN{FS="\t"}
/^#/ {next}
NF<2 {next}
{
  k=$1; v=$2
  gsub(/^[ \t]+|[ \t]+$/, "", k)
  gsub(/^[ \t]+|[ \t]+$/, "", v)
  f[k]=v
}
END{
  ext = (f["externalize"]=="yes" || f["externalize"]=="true" || f["externalize"]=="1")
  key = f["cache_key"]
  if (key == "") key = "-"
  disk = (f["disk_write"]=="yes" || f["disk_write"]=="true" || f["disk_write"]=="1")
  leftover = ext && (key != "") && (key != "-") && !disk
  printf "externalize\t%s\n", ext?"yes":"no"
  printf "cache_key\t%s\n", (f["cache_key"]==""?"-":f["cache_key"])
  printf "disk_write\t%s\n", disk?"yes":"no"
  printf "leftover_key\t%s\n", leftover?"yes":"no"
}
"""
    proc = subprocess.run(
        ["awk", script, str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    return rows_of(proc.stdout)


print("=== INSPECT BYTECODE ===")
fn = ns["inspect"]
print("co_names", fn.__code__.co_names)
print("co_varnames", fn.__code__.co_varnames)
print("co_consts", fn.__code__.co_consts)
print("--- dis ---")
dis.dis(fn)
print("yn_in", ns["yn_in"].__code__.co_consts)
print("KNOWN", ns["KNOWN"])

print("\n=== UNITTEST ===")
ut = subprocess.run(
    [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
    cwd=str(CLI.parent),
    capture_output=True,
    text=True,
    check=False,
)
print(ut.stderr)
print(ut.stdout)
print("unittest_rc", ut.returncode)

print("\n=== DEMO TWICE ===")
demo = CLI.parent / "demo.sh"
d1 = subprocess.run(["bash", str(demo)], capture_output=True, text=True, check=False)
d2 = subprocess.run(["bash", str(demo)], capture_output=True, text=True, check=False)
(SCR / "demo-live-1.log").write_text(d1.stdout)
(SCR / "demo-live-2.log").write_text(d2.stdout)
arch1 = (CLI.parent / "demo-1.log").read_bytes()
arch2 = (CLI.parent / "demo-2.log").read_bytes()
live1 = d1.stdout.encode()
live2 = d2.stdout.encode()
print("demo_rc", d1.returncode, d2.returncode)
print("live_eq", live1 == live2, "bytes", len(live1))
print("arch_eq_each_other", arch1 == arch2, "bytes", len(arch1))
print("live_eq_arch", live1 == arch1 and live2 == arch2)

print("\n=== CASES ===")
cases = [
    ("owned leftover", (FIX / "094-ext.rec").read_text(), str(FIX / "094-ext.rec")),
    ("owned inline", (FIX / "094-inline.rec").read_text(), str(FIX / "094-inline.rec")),
    ("unseen widget leftover", rec(id="widget", externalize="yes", cache_key="H_w", disk_write="no"), None),
    ("unseen widget inline", rec(id="widget", externalize="no", cache_key="H_w", disk_write="yes"), None),
    ("stdin leftover body", rec(id="lodash-es", externalize="yes", cache_key="H_ext", disk_write="no"), None),
    ("ext yes key present disk yes", rec(id="x", externalize="yes", cache_key="H_ext", disk_write="yes"), None),
    ("ext no key present disk no", rec(id="x", externalize="no", cache_key="H_ext", disk_write="no"), None),
    ("ext no key present disk yes", rec(id="x", externalize="no", cache_key="H_ext", disk_write="yes"), None),
    ("true false leftover", rec(id="x", externalize="true", cache_key="H_ext", disk_write="false"), None),
    ("one zero leftover", rec(id="x", externalize="1", cache_key="H_ext", disk_write="0"), None),
    ("present not yes-set", rec(id="x", externalize="present", cache_key="H_ext", disk_write="no"), None),
    ("YES uppercase", rec(id="x", externalize="YES", cache_key="H_ext", disk_write="NO"), None),
    ("omitted cache_key", rec(id="x", externalize="yes", disk_write="no"), None),
    ("hyphen cache_key", rec(id="x", externalize="yes", cache_key="-", disk_write="no"), None),
    ("empty cache_key field", "id\tx\nexternalize\tyes\ncache_key\t\ndisk_write\tno\n", None),
    ("cache_key yes token", rec(id="x", externalize="yes", cache_key="yes", disk_write="no"), None),
    ("cache_key no token", rec(id="x", externalize="yes", cache_key="no", disk_write="no"), None),
    ("cache_key 0 token", rec(id="x", externalize="yes", cache_key="0", disk_write="no"), None),
    ("cache_key sha1 leftover shaped", rec(id="x", externalize="yes", cache_key="sha1-deadbeef", disk_write="no"), None),
    ("missing disk leftover shaped", rec(id="x", externalize="yes", cache_key="H_ext"), None),
    ("missing ext", rec(id="x", cache_key="H_ext", disk_write="no"), None),
    ("id only", rec(id="x"), None),
    ("case C omitted key", rec(id="data:text/js", externalize="yes", cache_key="-", disk_write="no"), None),
    ("case D bail null", rec(id="./glob.js", externalize="no", cache_key="-", disk_write="no"), None),
    ("case E cache off", rec(id="./sum.js", externalize="no", cache_key="-", disk_write="no"), None),
    ("extra cols", "id\tx\textra\nexternalize\tyes\textra\ncache_key\tH_ext\ndisk_write\tno\n", None),
    ("tab before ext value", "id\tx\nexternalize\t\tyes\ncache_key\tH_ext\ndisk_write\tno\n", None),
    ("CRLF leftover", "id\tx\r\nexternalize\tyes\r\ncache_key\tH_ext\r\ndisk_write\tno\r\n", None),
    ("unicode id", rec(id="依存1", externalize="yes", cache_key="鍵0", disk_write="no"), None),
    ("ws around tokens", "  id  \t  x  \n  externalize  \t  yes  \n  cache_key  \t  H_ext  \n  disk_write  \t  no  \n", None),
    ("duplicate ext last no", "id\tx\nexternalize\tyes\nexternalize\tno\ncache_key\tH_ext\ndisk_write\tno\n", None),
    ("duplicate ext last yes", "id\tx\nexternalize\tno\nexternalize\tyes\ncache_key\tH_ext\ndisk_write\tno\n", None),
    ("duplicate disk last yes", "id\tx\nexternalize\tyes\ncache_key\tH_ext\ndisk_write\tno\ndisk_write\tyes\n", None),
    ("both flags yes key present", rec(id="x", externalize="yes", cache_key="H_ext", disk_write="yes"), None),
    ("both flags no key present", rec(id="x", externalize="no", cache_key="H_ext", disk_write="no"), None),
]

thin_m = thin_n = 0
rep_m = rep_n = 0
awk_m = awk_n = 0
print(
    "label | cli_rc | replica_rc | stdout_eq | leftover_thin | ext | key | disk | leftover_row | thin_match | awk_eq"
)
awk_paths = []
for label, text, path in cases:
    if path is None:
        p = write_tmp(label + ".rec", text)
        path = str(p)
    proc = run([path])
    fields = parse_simple(text)
    ext, key, disk, leftover = thin_from_fields(fields)
    try:
        out2, rc2, res = replica(text)
        stdout_eq = proc.stdout == out2 and proc.returncode == rc2
    except Exception as e:
        out2, rc2, res = "", None, {"err": str(e)}
        stdout_eq = False
    row = rows_of(proc.stdout)
    leftover_row = row.get("leftover_key")
    if leftover_row is not None:
        thin_match = leftover_row == ("yes" if leftover else "no") and (proc.returncode == 1) == leftover
    else:
        thin_match = False
    thin_n += 1
    thin_m += int(thin_match)
    if rc2 is not None:
        rep_n += 1
        rep_m += int(stdout_eq)
    awk_eq = None
    if leftover_row is not None:
        awk_n += 1
        a = awk_loadbearing(Path(path))
        awk_eq = (
            a.get("leftover_key") == leftover_row
            and a.get("externalize") == row.get("externalize")
            and a.get("disk_write") == row.get("disk_write")
        )
        awk_m += int(bool(awk_eq))
    print(
        f"{label} | {proc.returncode} | {rc2} | {stdout_eq} | {leftover} | {ext} | {key!r} | {disk} | {leftover_row} | {thin_match} | {awk_eq}"
    )
    if proc.stderr:
        print("  stderr", proc.stderr.strip()[:200])
print(f"replica_eq {rep_m}/{rep_n}")
print(f"thin_match {thin_m}/{thin_n}")
print(f"awk_eq {awk_m}/{awk_n}")

print("\n=== HARVEST STDOUT ===")
for name in ("094-ext.rec", "094-inline.rec"):
    proc = run([str(FIX / name)])
    print(f"-- {name} rc={proc.returncode} bytes={len(proc.stdout.encode())} --")
    print(proc.stdout, end="")
    print("stderr", repr(proc.stderr))

print("\n=== STDIN ===")
body = (FIX / "094-ext.rec").read_text()
p_stdin = run(["-"], stdin=body)
print("stdin leftover rc", p_stdin.returncode, "bytes", len(p_stdin.stdout.encode()), "eq_owned", p_stdin.stdout == run([str(FIX / "094-ext.rec")]).stdout)
print(p_stdin.stdout, end="")
p_empty = run(["-"], stdin="")
print("empty stdin rc", p_empty.returncode, "stderr", p_empty.stderr.strip())
p_dev = run(["/dev/stdin"], stdin=body)
print("/dev/stdin rc", p_dev.returncode, "leftover", rows_of(p_dev.stdout).get("leftover_key"))
# process substitution via bash
ps = subprocess.run(
    ["bash", "-c", f'python3 "{CLI}" <(cat "{FIX / "094-ext.rec"}"); echo rc=$?'],
    capture_output=True,
    text=True,
    check=False,
)
print("procsubst", ps.stdout, "stderr", ps.stderr[:200])
p_noargs = subprocess.run([sys.executable, str(CLI)], capture_output=True, text=True, check=False)
print("noargs rc", p_noargs.returncode, "stderr", p_noargs.stderr.strip()[:200])
p_extra = subprocess.run([sys.executable, str(CLI), "a", "b"], capture_output=True, text=True, check=False)
print("extra pos rc", p_extra.returncode, "stderr", p_extra.stderr.strip()[:200])

print("\n=== TOKEN GRID yn x key x disk ===")
yn_toks = ["yes", "true", "1", "no", "false", "0", "-", "present", "YES", "on", "hash"]
key_toks = ["H_ext", "H_inlined", "-", "yes", "no", "0", "x", "sha1-dead"]
grid_m = grid_n = 0
grid_fail = []
for e in yn_toks:
    for k in key_toks:
        for d in yn_toks:
            text = rec(id="g", externalize=e, cache_key=k, disk_write=d)
            p = write_tmp(f"grid_{e}_{k}_{d}.rec", text)
            proc = run([str(p)])
            try:
                out2, rc2, res = replica(text)
                stdout_eq = proc.stdout == out2 and proc.returncode == rc2
            except Exception:
                stdout_eq = False
                rc2 = None
            fields = parse_simple(text)
            ext, key, disk, leftover = thin_from_fields(fields)
            row = rows_of(proc.stdout)
            leftover_row = row.get("leftover_key")
            thin_ok = leftover_row == ("yes" if leftover else "no") and (proc.returncode == 1) == leftover
            grid_n += 1
            if stdout_eq and thin_ok:
                grid_m += 1
            else:
                if len(grid_fail) < 8:
                    grid_fail.append((e, k, d, proc.returncode, leftover_row, leftover, stdout_eq, proc.stderr[:80]))
print(f"grid replica+thin {grid_m}/{grid_n}")
print("grid_fail sample", grid_fail)

print("\n=== EMPTY-FIELD PAIRS ===")
# trailing tab eaten by strip
empty_cases = [
    ("empty ext", "id\tx\nexternalize\t\ncache_key\tH_ext\ndisk_write\tno\n"),
    ("empty key", "id\tx\nexternalize\tyes\ncache_key\t\ndisk_write\tno\n"),
    ("empty disk", "id\tx\nexternalize\tyes\ncache_key\tH_ext\ndisk_write\t\n"),
    ("spaces not tab", "id x\nexternalize yes\ncache_key H_ext\ndisk_write no\n"),
]
for label, text in empty_cases:
    p = write_tmp(label + ".rec", text)
    proc = run([str(p)])
    print(label, "rc", proc.returncode, "stdout_bytes", len(proc.stdout.encode()), "stderr", proc.stderr.strip()[:160])

print("\n=== ORIGIN BYTES REFUSE ===")
origin_files = [
    ("leftover_identity_split", S094 / "files/leftover_identity_split.txt"),
    ("fetch_order", S094 / "files/fetch_order_failing.ts"),
    ("generate_cache_path", S094 / "files/generate_cache_path_failing.ts"),
    ("early_externalize", S094 / "files/early_externalize_omit.ts"),
]
for label, path in origin_files:
    proc = run([str(path)])
    print(label, "rc", proc.returncode, "stderr", proc.stderr.strip()[:180], "stdout_bytes", len(proc.stdout.encode()))

json_body = '{"id":"lodash-es","externalize":"yes","cache_key":"H_ext","disk_write":"no"}\n'
p = write_tmp("json.rec", json_body)
proc = run([str(p)])
print("json rc", proc.returncode, "stderr", proc.stderr.strip()[:160])

unknown = rec(id="x", externalize="yes", cache_key="H_ext", disk_write="no", contenthash="abc")
p = write_tmp("unknown.rec", unknown)
proc = run([str(p)])
print("unknown field rc", proc.returncode, "stderr", proc.stderr.strip()[:160])

cased = "Id\tx\nexternalize\tyes\ncache_key\tH_ext\ndisk_write\tno\n"
p = write_tmp("cased.rec", cased)
proc = run([str(p)])
print("Id capital rc", proc.returncode, "stderr", proc.stderr.strip()[:160])

bom = "\ufeffid\tx\nexternalize\tyes\ncache_key\tH_ext\ndisk_write\tno\n"
p = write_tmp("bom.rec", bom)
proc = run([str(p)])
print("BOM rc", proc.returncode, "stderr", proc.stderr.strip()[:180])

nul = "id\tx\n\x00externalize\tyes\ncache_key\tH_ext\ndisk_write\tno\n"
p = write_tmp("nul.rec", nul)
proc = run([str(p)])
print("NUL rc", proc.returncode, "stderr", proc.stderr.strip()[:180])

bad = b"id\tx\nexternalize\tyes\ncache_key\tH_ext\ndisk_write\tno\n\xff\xfe"
(SCR / "badutf.rec").write_bytes(bad)
proc = run([str(SCR / "badutf.rec")])
print("badutf rc", proc.returncode, "stderr", proc.stderr.strip()[:180])

comments_only = "# only\n# still\n"
p = write_tmp("comments.rec", comments_only)
proc = run([str(p)])
print("comments-only rc", proc.returncode, "stderr", proc.stderr.strip()[:160])

print("\n=== MISSING / DIR ===")
proc = run(["/nope"])
print("missing rc", proc.returncode, "stderr", proc.stderr.strip()[:180])
proc = run([str(SCR)])
print("dir rc", proc.returncode, "stderr", proc.stderr.strip()[:180])

print("\n=== SYMLINK FIFO SPACE ===")
link = SCR / "link.rec"
if link.exists() or link.is_symlink():
    link.unlink()
link.symlink_to(FIX / "094-ext.rec")
proc = run([str(link)])
print("symlink rc", proc.returncode, "leftover", rows_of(proc.stdout).get("leftover_key"))

space = SCR / "file with space.rec"
space.write_text(rec(id="x", externalize="yes", cache_key="H_ext", disk_write="no"))
proc = run([str(space)])
print("space name rc", proc.returncode, "leftover", rows_of(proc.stdout).get("leftover_key"))

fifo = SCR / "fifo.rec"
if fifo.exists() or fifo.is_fifo():
    fifo.unlink()
os.mkfifo(fifo)
body = rec(id="x", externalize="yes", cache_key="H_ext", disk_write="no")

def writer():
    with open(fifo, "w", encoding="utf-8") as f:
        f.write(body)

t = threading.Thread(target=writer)
t.start()
proc = run([str(fifo)])
t.join()
print("fifo rc", proc.returncode, "leftover", rows_of(proc.stdout).get("leftover_key"))

print("\n=== HUGE DUMP ===")
pad = "\n".join(f"# pad {i}" for i in range(10000))
huge_left = pad + "\n" + rec(id="x", externalize="yes", cache_key="H_ext", disk_write="no")
huge_inline = pad + "\n" + rec(id="x", externalize="no", cache_key="H_inlined", disk_write="yes")
p1 = write_tmp("huge.rec", huge_left)
p2 = write_tmp("huge_inline.rec", huge_inline)
t0 = time.perf_counter()
proc1 = run([str(p1)])
t1 = time.perf_counter()
proc2 = run([str(p2)])
t2 = time.perf_counter()
print(
    "huge leftover rc",
    proc1.returncode,
    "bytes",
    len(proc1.stdout.encode()),
    "s",
    round(t1 - t0, 4),
    "leftover",
    rows_of(proc1.stdout).get("leftover_key"),
)
print(
    "huge inline rc",
    proc2.returncode,
    "bytes",
    len(proc2.stdout.encode()),
    "s",
    round(t2 - t1, 4),
    "leftover",
    rows_of(proc2.stdout).get("leftover_key"),
)
print("huge leftover stdout:")
print(proc1.stdout, end="")
print("huge inline stdout:")
print(proc2.stdout, end="")

print("\n=== GREP NEAREST ===")
for name in ("094-ext.rec", "094-inline.rec"):
    g = subprocess.run(["grep", "-n", "H_ext", str(FIX / name)], capture_output=True, text=True)
    print(name, "H_ext rc", g.returncode, "out", g.stdout.strip())
    g2 = subprocess.run(["grep", "-n", "lodash-es", str(FIX / name)], capture_output=True, text=True)
    print(name, "lodash-es rc", g2.returncode, "out", g2.stdout.strip())
    g3 = subprocess.run(["grep", "-n", "externalize", str(FIX / name)], capture_output=True, text=True)
    print(name, "externalize lines", g3.stdout.strip())

print("\n=== ONE-LINER ===")
oneliner = subprocess.run(
    [
        sys.executable,
        "-c",
        """
import sys
YES={"yes","true","1"}
fields={}
for raw in open(sys.argv[1], encoding="utf-8"):
    line=raw.strip()
    if not line or line.startswith("#") or "\\t" not in line: continue
    k,r=line.split("\\t",1)
    fields[k.strip()]=r.strip()
ext=fields.get("externalize","") in YES
key=fields.get("cache_key") or "-"
disk=fields.get("disk_write","") in YES
print("externalize", ext)
print("cache_key", key)
print("disk_write", disk)
print("leftover", ext and key not in {"", "-"} and not disk)
""",
        str(FIX / "094-ext.rec"),
    ],
    capture_output=True,
    text=True,
    check=False,
)
print(oneliner.stdout)

print("\n=== PRINTF VS OWNED ===")
owned = run([str(FIX / "094-ext.rec")])
printf = (
    "id\tlodash-es\n"
    "externalize\tyes\n"
    "cache_key\tH_ext\n"
    "disk_write\tno\n"
    "leftover_key\tyes\n"
)
print("owned==printf", owned.stdout == printf, "bytes", len(owned.stdout.encode()))
inline = run([str(FIX / "094-inline.rec")])
printf_i = (
    "id\t./sum.js\n"
    "externalize\tno\n"
    "cache_key\tH_inlined\n"
    "disk_write\tyes\n"
    "leftover_key\tno\n"
)
print("inline==printf", inline.stdout == printf_i, "bytes", len(inline.stdout.encode()))

print("\n=== 2x2x2 yes/no matrix ===")
print("ext disk key leftover rc identity-ish")
for e in ("yes", "no"):
    for d in ("yes", "no"):
        for k in ("H_ext", "-"):
            text = rec(id="m", externalize=e, cache_key=k, disk_write=d)
            p = write_tmp(f"m_{e}_{k}_{d}.rec", text)
            proc = run([str(p)])
            row = rows_of(proc.stdout)
            print(e, d, k, row.get("leftover_key"), proc.returncode, dict(row))

print("DONE")
