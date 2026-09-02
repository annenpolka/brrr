#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
from pathlib import Path

RUN = Path("/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112")
CLI = RUN / "lineages/candidate-pnpbuilt/pnpbuilt"
FIX = RUN / "lineages/candidate-pnpbuilt/fixtures"
SCR = RUN / "destroyers/_pnpbuilt_scratch"
S089 = RUN / "specimens/specimen-089"
SCR.mkdir(parents=True, exist_ok=True)
src = CLI.read_text(encoding="utf-8")
ns: dict = {}
exec(compile(src, str(CLI), "exec"), ns)

YES = {"yes", "true", "1", "present"}


def run(args, stdin=None, timeout=10):
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
    rc = 1 if result["leftover_built"] else 0
    return out, rc, result


def thin_from_fields(fields):
    stored = (fields.get("stored_hash") or "") in YES
    ready = (fields.get("unplugged_ready") or "") in YES
    leftover = stored and not ready
    return stored, ready, leftover


def parse_simple(text):
    fields = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "\t" not in line:
            continue
        k, r = line.split("\t", 1)
        fields[k.strip()] = r.split("\t", 1)[0].strip()
    return fields


def rec(**kw):
    return "".join(f"{k}\t{v}\n" for k, v in kw.items())


def slug(s: str) -> str:
    out = []
    for ch in s:
        out.append(ch if ch.isalnum() or ch in "._-" else "_")
    return "".join(out)[:80]


def write_tmp(name, text):
    p = SCR / slug(name)
    p.write_text(text, encoding="utf-8")
    return p


def rows_of(stdout: str) -> dict[str, str]:
    d = {}
    for line in stdout.splitlines():
        if "\t" in line:
            k, v = line.split("\t", 1)
            d[k] = v
    return d


print("=== CASES ===")
cases = [
    ("owned leftover", (FIX / "089-leftover.rec").read_text(), str(FIX / "089-leftover.rec")),
    ("owned built", (FIX / "089-built.rec").read_text(), str(FIX / "089-built.rec")),
    ("owned never", (FIX / "089-never.rec").read_text(), str(FIX / "089-never.rec")),
    ("unseen widget leftover", rec(locator="widget@npm:0.1.0", stored_hash="yes", unplugged_ready="no", binary="no"), None),
    ("unseen widget built", rec(locator="widget@npm:0.1.0", stored_hash="yes", unplugged_ready="yes", binary="yes"), None),
    ("unseen widget never", rec(locator="widget@npm:0.1.0", stored_hash="no", unplugged_ready="no", binary="no"), None),
    ("ready without hash", rec(locator="@sentry/cli@npm:1.62.0", stored_hash="no", unplugged_ready="yes", binary="no"), None),
    ("leftover binary yes", rec(locator="@sentry/cli@npm:1.62.0", stored_hash="yes", unplugged_ready="no", binary="yes"), None),
    ("built binary no", rec(locator="@sentry/cli@npm:1.62.0", stored_hash="yes", unplugged_ready="yes", binary="no"), None),
    ("no binary leftover", rec(locator="@sentry/cli@npm:1.62.0", stored_hash="yes", unplugged_ready="no"), None),
    ("no binary built", rec(locator="@sentry/cli@npm:1.62.0", stored_hash="yes", unplugged_ready="yes"), None),
    ("true false leftover", rec(locator="x", stored_hash="true", unplugged_ready="false"), None),
    ("one zero leftover", rec(locator="x", stored_hash="1", unplugged_ready="0"), None),
    ("present absent leftover", rec(locator="x", stored_hash="present", unplugged_ready="absent"), None),
    ("YES uppercase", rec(locator="x", stored_hash="YES", unplugged_ready="NO"), None),
    ("sha512 leftover shaped", rec(locator="@sentry/cli@npm:1.62.0", stored_hash="sha512-deadbeef", unplugged_ready="no", binary="no"), None),
    ("sha512 built shaped", rec(locator="@sentry/cli@npm:1.62.0", stored_hash="sha512-deadbeef", unplugged_ready="yes", binary="yes"), None),
    ("missing stored", rec(locator="x", unplugged_ready="no"), None),
    ("missing ready leftover shaped", rec(locator="x", stored_hash="yes"), None),
    ("empty stored", rec(locator="x", stored_hash="", unplugged_ready="no"), None),
    ("locator only", rec(locator="x"), None),
    ("extra cols", "locator\tx\textra\nstored_hash\tyes\textra\nunplugged_ready\tno\n", None),
    ("tab before stored value", "locator\tx\nstored_hash\t\tyes\nunplugged_ready\tno\n", None),
    ("CRLF leftover", "locator\tx\r\nstored_hash\tyes\r\nunplugged_ready\tno\r\n", None),
    ("unicode locator", rec(locator="依存@npm:1", stored_hash="yes", unplugged_ready="no"), None),
    ("both no", rec(locator="x", stored_hash="no", unplugged_ready="no"), None),
    ("both yes", rec(locator="x", stored_hash="yes", unplugged_ready="yes"), None),
    ("ws around tokens", "  locator  \t  x  \n  stored_hash  \t  yes  \n  unplugged_ready  \t  no  \n", None),
    ("duplicate stored last no", "locator\tx\nstored_hash\tyes\nstored_hash\tno\nunplugged_ready\tno\n", None),
    ("duplicate stored last yes", "locator\tx\nstored_hash\tno\nstored_hash\tyes\nunplugged_ready\tno\n", None),
]

thin_m = thin_n = 0
rep_m = rep_n = 0
print("label | cli_rc | replica_rc | stdout_eq | leftover_thin | stored | ready | identity | leftover_row | binary | thin_match")
for label, text, path in cases:
    if path is None:
        p = write_tmp(label + ".rec", text)
        path = str(p)
    proc = run([path])
    fields = parse_simple(text)
    stored, ready, leftover = thin_from_fields(fields)
    try:
        out2, rc2, res = replica(text)
        stdout_eq = proc.stdout == out2 and proc.returncode == rc2
    except Exception as e:
        out2, rc2, res = "", None, {"err": str(e)}
        stdout_eq = False
    row = rows_of(proc.stdout)
    leftover_row = row.get("leftover_built")
    ident = row.get("identity")
    binary = row.get("binary")
    if leftover_row is not None:
        thin_match = leftover_row == ("yes" if leftover else "no") and (proc.returncode == 1) == leftover
    else:
        thin_match = False
    thin_n += 1
    thin_m += int(thin_match)
    if rc2 is not None:
        rep_n += 1
        rep_m += int(stdout_eq)
    print(
        f"{label} | {proc.returncode} | {rc2} | {stdout_eq} | {leftover} | {stored} | {ready} | {ident} | {leftover_row} | {binary} | {thin_match} | {proc.stderr.strip()[:80]}"
    )

print(f"thin_match {thin_m}/{thin_n}")
print(f"replica_byte {rep_m}/{rep_n}")

print("=== STDIN ===")
text = (FIX / "089-leftover.rec").read_text()
proc = run(["-"], stdin=text)
out2, rc2, res = replica(text, source="<stdin>")
print("stdin leftover rc", proc.returncode, "eq", proc.stdout == out2, "bytes", len(proc.stdout.encode()))
print(proc.stdout, end="")
proc = run(["-"], stdin="")
print("empty stdin rc", proc.returncode, "stderr", proc.stderr.strip())
proc = subprocess.run([sys.executable, str(CLI), "/dev/stdin"], input=text, capture_output=True, text=True)
print("/dev/stdin leftover rc", proc.returncode, rows_of(proc.stdout).get("leftover_built"))
proc = run([])
print("noargs rc", proc.returncode, (proc.stderr.splitlines() or [""])[0][:80])
proc = run(["a", "b"])
print("extra pos rc", proc.returncode)
proc = run(["/no/such.rec"])
print("missing rc", proc.returncode, proc.stderr.strip()[:120])
proc = run([str(SCR)])
print("dir rc", proc.returncode, proc.stderr.strip()[:120])

print("=== ORIGIN ===")
origin = (S089 / "files/leftover_identity_split.txt").read_text()
p = write_tmp("origin_split.rec", origin)
proc = run([str(p)])
print("origin split rc", proc.returncode, proc.stderr.strip()[:180])
p = write_tmp("build-state.yml", '"@sentry/cli@npm:1.62.0": "sha512-abc"\n')
proc = run([str(p)])
print("yamlish rc", proc.returncode, proc.stderr.strip()[:180])
p = write_tmp("state.json", '{"storedBuildState": {"x": "hash"}}\n')
proc = run([str(p)])
print("json rc", proc.returncode, proc.stderr.strip()[:180])
p = write_tmp("unknown.rec", rec(locator="x", stored_hash="yes", unplugged_ready="no", packageLocation="unplugged"))
proc = run([str(p)])
print("unknown field rc", proc.returncode, proc.stderr.strip())
p = write_tmp("Packages.rec", "Locator\tx\nstored_hash\tyes\nunplugged_ready\tno\n")
proc = run([str(p)])
print("Locator capital rc", proc.returncode, proc.stderr.strip()[:180])
p = write_tmp("bom.rec", "\ufefflocator\tx\nstored_hash\tyes\nunplugged_ready\tno\n")
proc = run([str(p)])
print("BOM rc", proc.returncode, proc.stderr.strip()[:180])
p = SCR / "nul.rec"
p.write_bytes(b"locator\tx\n\x00stored_hash\tyes\nunplugged_ready\tno\n")
proc = subprocess.run([sys.executable, str(CLI), str(p)], capture_output=True)
print("NUL rc", proc.returncode, proc.stderr[:180])
p = SCR / "badutf.rec"
p.write_bytes(b"locator\tx\nstored_hash\tyes\nunplugged_ready\tno\n\xff\xfe")
proc = subprocess.run([sys.executable, str(CLI), str(p)], capture_output=True)
print("badutf rc", proc.returncode, proc.stderr[:180])

print("=== IDENTITY MATRIX ===")
seen_ident = set()
for stored in ["yes", "no"]:
    for ready in ["yes", "no"]:
        for binary in ["yes", "no"]:
            t = rec(locator="x", stored_hash=stored, unplugged_ready=ready, binary=binary)
            p = write_tmp(f"id_{stored}_{ready}_{binary}.rec", t)
            proc = run([str(p)])
            row = rows_of(proc.stdout)
            seen_ident.add(row.get("identity"))
            print(
                f"stored={stored} ready={ready} binary={binary} leftover={row.get('leftover_built')} ident={row.get('identity')} bin={row.get('binary')} rc={proc.returncode}"
            )
print("seen identity labels", seen_ident)
print("ready-without-hash reachable", "ready-without-hash" in seen_ident)

print("=== GREP LOCATOR vs LS READY ===")
for name in ["089-leftover.rec", "089-built.rec", "089-never.rec"]:
    path = FIX / name
    g = subprocess.run(["grep", "-n", "@sentry/cli", str(path)], capture_output=True, text=True)
    print(name, "grep_rc", g.returncode)
    print(g.stdout, end="")
print("ls .ready in fixtures", list(FIX.glob("**/.ready")))
print("ls unplugged", list(FIX.rglob("unplugged")))
# grep stored_hash yes vs unplugged_ready no
for name in ["089-leftover.rec", "089-built.rec", "089-never.rec"]:
    path = FIX / name
    g1 = subprocess.run(["grep", "-E", "^stored_hash\t", str(path)], capture_output=True, text=True)
    g2 = subprocess.run(["grep", "-E", "^unplugged_ready\t", str(path)], capture_output=True, text=True)
    print(name, "stored", g1.stdout.strip(), "ready", g2.stdout.strip())

print("=== AWK ===")
awk = r"""
BEGIN{FS="\t"}
/^#/ {next}
NF<2 {next}
{
  k=$1; v=$2
  gsub(/^[ \t]+|[ \t]+$/,"",k)
  gsub(/^[ \t]+|[ \t]+$/,"",v)
  f[k]=v
}
END{
  stored = (f["stored_hash"]=="yes" || f["stored_hash"]=="true" || f["stored_hash"]=="1" || f["stored_hash"]=="present")
  ready = (f["unplugged_ready"]=="yes" || f["unplugged_ready"]=="true" || f["unplugged_ready"]=="1" || f["unplugged_ready"]=="present")
  leftover = stored && !ready
  printf "stored_hash\t%s\n", stored?"yes":"no"
  printf "unplugged_ready\t%s\n", ready?"yes":"no"
  printf "leftover_built\t%s\n", leftover?"yes":"no"
}
"""
awk_m = awk_n = 0
awk_paths = [
    ("owned leftover", FIX / "089-leftover.rec"),
    ("owned built", FIX / "089-built.rec"),
    ("owned never", FIX / "089-never.rec"),
]
for label, text, path in cases:
    if path is None:
        p = write_tmp(label + ".rec", text)
        pathp = p
    else:
        pathp = Path(path)
    proc = run([str(pathp)])
    a = subprocess.run(["awk", awk, str(pathp)], capture_output=True, text=True)
    cli_load = {k: rows_of(proc.stdout).get(k) for k in ("stored_hash", "unplugged_ready", "leftover_built")}
    awk_load = rows_of(a.stdout)
    eq = cli_load == awk_load and None not in cli_load.values()
    awk_n += 1
    awk_m += int(eq)
    if not eq:
        print("awk mismatch", label, "cli", cli_load, "awk", awk_load, "stderr", proc.stderr.strip()[:80])
print(f"awk_eq_cli_loadbearing {awk_m}/{awk_n}")

print("=== HUGE ===")
huge = "\n".join(["# pad"] * 10000 + ["locator\tx", "stored_hash\tyes", "unplugged_ready\tno", "binary\tno"]) + "\n"
p = write_tmp("huge.rec", huge)
t0 = time.perf_counter()
proc = run([str(p)], timeout=30)
t1 = time.perf_counter()
print("huge leftover rc", proc.returncode, "bytes", len(proc.stdout.encode()), "s", round(t1 - t0, 4))
print(proc.stdout, end="")
huge2 = "\n".join(["# pad"] * 10000 + ["locator\tx", "stored_hash\tyes", "unplugged_ready\tyes", "binary\tyes"]) + "\n"
p = write_tmp("huge_built.rec", huge2)
t0 = time.perf_counter()
proc = run([str(p)], timeout=30)
t1 = time.perf_counter()
print("huge built rc", proc.returncode, "bytes", len(proc.stdout.encode()), "s", round(t1 - t0, 4))

print("=== NODES ===")
p = SCR / "file with space.rec"
p.write_text(rec(locator="x", stored_hash="yes", unplugged_ready="no"), encoding="utf-8")
proc = run([str(p)])
print("space name rc", proc.returncode, rows_of(proc.stdout).get("leftover_built"))
link = SCR / "link.rec"
if link.exists() or link.is_symlink():
    link.unlink()
link.symlink_to(FIX / "089-leftover.rec")
proc = run([str(link)])
print("symlink rc", proc.returncode, rows_of(proc.stdout).get("leftover_built"))
fifo = SCR / "fifo.rec"
if fifo.exists():
    fifo.unlink()
os.mkfifo(fifo)


def writer():
    time.sleep(0.05)
    with open(fifo, "w", encoding="utf-8") as fh:
        fh.write((FIX / "089-leftover.rec").read_text())


th = threading.Thread(target=writer)
th.start()
proc = run([str(fifo)])
th.join()
print("fifo rc", proc.returncode, rows_of(proc.stdout).get("leftover_built"))
proc = subprocess.run(
    ["bash", "-lc", f'python3 "{CLI}" <(cat "{FIX}/089-leftover.rec"); echo rc=$?'],
    capture_output=True,
    text=True,
)
print("procsubst stdout\n", proc.stdout)

print("=== TOKEN GRID ===")
tokens = ["yes", "true", "1", "present", "no", "false", "0", "absent", "", "YES", "Yes", "sha512-abc", "hash", "ready", "-", "on"]
n = m = 0
for s in tokens:
    for rdy in tokens:
        t = rec(locator="loc", stored_hash=s, unplugged_ready=rdy, binary="no")
        p = write_tmp("pair.rec", t)
        proc = run([str(p)])
        stored = s in YES
        ready = rdy in YES
        leftover = stored and not ready
        row = rows_of(proc.stdout)
        ok = row.get("leftover_built") == ("yes" if leftover else "no") and (proc.returncode == 1) == leftover
        n += 1
        m += int(ok)
        if not ok:
            print("MISMATCH", repr(s), repr(rdy), proc.returncode, row, leftover)
print(f"one_liner_token_grid {m}/{n}")

print("=== REPLICA EXTRA STDIN ===")
proc = run(["-"], stdin=text)
out2, rc2, res = replica(text, source="<stdin>")
print("stdin replica eq", proc.stdout == out2, proc.returncode == rc2)

print("DONE")
