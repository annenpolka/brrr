#!/usr/bin/env python3
"""cssleft destroyer attacks. Host-executed. No webpack / npx / node."""
from __future__ import annotations

import dis
import io
import json
import os
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path

RUN = Path("/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112")
CLI = RUN / "lineages/candidate-cssleft/cssleft"
FIX = RUN / "lineages/candidate-cssleft/fixtures"
S090 = RUN / "specimens/specimen-090"
SCRATCH = RUN / "destroyers/_cssleft_scratch"
PY = sys.executable

# Load inspect/format_report/parse_record by exec, no package import.
ns: dict = {}
exec(CLI.read_text(encoding="utf-8"), ns)
inspect = ns["inspect"]
format_report = ns["format_report"]
parse_record = ns["parse_record"]


def run_cli(path: str | Path, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    args = [PY, str(CLI)]
    if path == "-":
        args.append("-")
        return subprocess.run(args, input=stdin or "", capture_output=True, text=True, check=False)
    args.append(str(path))
    return subprocess.run(args, capture_output=True, text=True, check=False, input=stdin)


def write_rec(name: str, body: str) -> Path:
    p = SCRATCH / name
    p.write_text(body, encoding="utf-8")
    return p


def rows(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        k, v = line.split("\t", 1)
        out[k] = v
    return out


def thin_from_fields(fields: dict[str, str]) -> tuple[bool, bool, bool]:
    css = fields["css_name"]
    url = fields["url_in_css"]
    png = fields["png_emitted"]
    prev = fields.get("prev_css_name") or ""
    leftover_url = url != png
    leftover_css = bool(prev) and css == prev
    leftover = leftover_url or leftover_css
    return leftover_url, leftover_css, leftover


def replica(text: str, source: str = "<replica>") -> tuple[int, str]:
    fields = parse_record(text, source=source)
    result = inspect(fields)
    return (1 if result["leftover"] else 0), format_report(result)


def rec_body(**kw: str) -> str:
    lines = []
    for k in ("css_name", "url_in_css", "png_emitted", "prev_css_name"):
        if k in kw:
            lines.append(f"{k}\t{kw[k]}")
    return "\n".join(lines) + "\n"


print("=== inspect metadata ===")
print("co_names", inspect.__code__.co_names)
print("co_varnames", inspect.__code__.co_varnames)
print("co_consts", inspect.__code__.co_consts)
buf = io.StringIO()
dis.dis(inspect, file=buf)
print(buf.getvalue())

print("=== unit tests ===")
proc = subprocess.run(
    [PY, "-m", "unittest", "discover", "-s", str(RUN / "lineages/candidate-cssleft/tests"), "-v"],
    capture_output=True,
    text=True,
    check=False,
    cwd=str(RUN / "lineages/candidate-cssleft"),
)
print(proc.stderr)
print(proc.stdout)
print("unittest_rc", proc.returncode)

print("=== demo twice vs archive ===")
demo = RUN / "lineages/candidate-cssleft/demo.sh"
live1 = SCRATCH / "demo-live-1.log"
live2 = SCRATCH / "demo-live-2.log"
for dest in (live1, live2):
    d = subprocess.run(["bash", str(demo)], capture_output=True, text=True, check=False)
    dest.write_text(d.stdout, encoding="utf-8")
    print(dest.name, "rc", d.returncode, "bytes", dest.stat().st_size)
a1 = RUN / "lineages/candidate-cssleft/demo-1.log"
a2 = RUN / "lineages/candidate-cssleft/demo-2.log"
for a, b in ((live1, live2), (live1, a1), (live2, a2), (a1, a2)):
    c = subprocess.run(["cmp", str(a), str(b)], capture_output=True)
    print(f"cmp {a.name} {b.name} rc={c.returncode}")

print("=== owned happy path ===")
owned = {}
for name in ("090-leftover.rec", "090-fresh.rec", "090-css-only.rec"):
    p = FIX / name
    r = run_cli(p)
    owned[name] = r
    print(f"--- {name} rc={r.returncode} bytes={len(r.stdout)} stderr={r.stderr!r}")
    print(r.stdout, end="")

print("=== replica vs CLI harvest shapes ===")
cases = []
for name in ("090-leftover.rec", "090-fresh.rec", "090-css-only.rec"):
    text = (FIX / name).read_text(encoding="utf-8")
    cli = run_cli(FIX / name)
    rc, out = replica(text, source=str(FIX / name))
    fields = parse_record(text, source=str(FIX / name))
    tu, tc, tl = thin_from_fields(fields)
    row = rows(cli.stdout)
    rec = {
        "case": name,
        "cli_rc": cli.returncode,
        "replica_rc": rc,
        "stdout_eq": cli.stdout == out,
        "leftover_thin": tl,
        "leftover_url": row.get("leftover_url"),
        "leftover_css_hash": row.get("leftover_css_hash"),
        "leftover": row.get("leftover"),
        "thin_url": tu,
        "thin_css": tc,
        "thin_matches_cli": (row.get("leftover_url") == ("yes" if tu else "no")
                             and row.get("leftover_css_hash") == ("yes" if tc else "no")
                             and row.get("leftover") == ("yes" if tl else "no")
                             and cli.returncode == (1 if tl else 0)),
    }
    cases.append(rec)
    print(json.dumps(rec))

print("=== extra host cases ===")
extra_specs = [
    ("url_only", dict(css_name="H_css1", url_in_css="H_png0", png_emitted="H_png1", prev_css_name="H_css0")),
    ("css_only_leftover", dict(css_name="H_css1", url_in_css="H_png1", png_emitted="H_png1", prev_css_name="H_css1")),
    ("both_leftover", dict(css_name="H_css1", url_in_css="H_png0", png_emitted="H_png1", prev_css_name="H_css1")),
    ("neither", dict(css_name="H_css0", url_in_css="H_png0", png_emitted="H_png0", prev_css_name="H_css0")),
    ("omit_prev", dict(css_name="H_css1", url_in_css="H_png0", png_emitted="H_png1")),
    ("omit_prev_match_url", dict(css_name="H_css1", url_in_css="H_png0", png_emitted="H_png0")),
    ("prev_dash", dict(css_name="H_css0", url_in_css="H_png0", png_emitted="H_png0", prev_css_name="-")),
    ("hyphen_collision", dict(css_name="-", url_in_css="H_png0", png_emitted="H_png0", prev_css_name="-")),
    ("prev_empty_omitted_key", dict(css_name="H_css1", url_in_css="H_png1", png_emitted="H_png1")),
    ("unseen_widget", dict(css_name="W_css1", url_in_css="W_png0", png_emitted="W_png1", prev_css_name="W_css1")),
    ("url_token_with_urlfn", dict(css_name="H_css1", url_in_css="url(H_png0)", png_emitted="H_png1", prev_css_name="H_css0")),
    ("hashed_filenames", dict(css_name="style.abc.css", url_in_css="logo.old.png", png_emitted="logo.new.png", prev_css_name="style.abc.css")),
    ("case_d_never_url_same", dict(css_name="H_css0", url_in_css="H_png0", png_emitted="H_png0")),
    ("swap_url_png", dict(css_name="H_css1", url_in_css="H_png1", png_emitted="H_png0", prev_css_name="H_css0")),
    ("unicode", dict(css_name="依存1", url_in_css="画像0", png_emitted="画像1", prev_css_name="依存1")),
    ("empty_css", dict(css_name="", url_in_css="H_png0", png_emitted="H_png1", prev_css_name="H_css1")),
    ("same_all", dict(css_name="X", url_in_css="X", png_emitted="X", prev_css_name="X")),
    ("prev_zero", dict(css_name="0", url_in_css="H_png0", png_emitted="H_png0", prev_css_name="0")),
    ("extra_tab_url", None),  # handled below
]

extra_results = []
for name, spec in extra_specs:
    if spec is None:
        continue
    body = rec_body(**spec)
    p = write_rec(f"{name}.rec", body)
    cli = run_cli(p)
    try:
        rc, out = replica(body, source=str(p))
        replica_ok = True
    except Exception as e:
        rc, out, replica_ok = -1, str(e), False
    row = rows(cli.stdout)
    try:
        fields = parse_record(body, source=str(p))
        tu, tc, tl = thin_from_fields(fields)
        thin_ok = True
    except Exception as e:
        tu = tc = tl = None
        thin_ok = False
    rec = {
        "case": name,
        "cli_rc": cli.returncode,
        "replica_rc": rc,
        "stdout_eq": cli.stdout == out if replica_ok else False,
        "stderr": cli.stderr.strip(),
        "leftover_url": row.get("leftover_url"),
        "leftover_css_hash": row.get("leftover_css_hash"),
        "leftover": row.get("leftover"),
        "prev_printed": row.get("prev_css_name"),
        "thin_url": tu,
        "thin_css": tc,
        "thin_leftover": tl,
        "thin_ok": thin_ok,
        "stdout": cli.stdout,
    }
    extra_results.append(rec)
    print(f"--- {name} rc={cli.returncode} leftover={row.get('leftover')} url={row.get('leftover_url')} css={row.get('leftover_css_hash')} stdout_eq={rec['stdout_eq']} stderr={cli.stderr.strip()!r}")
    print(cli.stdout, end="")

# extra tab after url value
body = "css_name\tH_css1\nurl_in_css\tH_png0\textra\npng_emitted\tH_png1\nprev_css_name\tH_css1\n"
p = write_rec("extra_tab_url.rec", body)
cli = run_cli(p)
print("--- extra_tab_url rc", cli.returncode)
print(cli.stdout, end="")
print("stderr", cli.stderr.strip())
fields = parse_record(body, source=str(p))
print("parsed url_in_css", repr(fields["url_in_css"]))
tu, tc, tl = thin_from_fields(fields)
print("thin", tu, tc, tl, "cli leftover", rows(cli.stdout).get("leftover"))

# extra tab before value
body = "css_name\tH_css1\nurl_in_css\t\tH_png0\npng_emitted\tH_png1\nprev_css_name\tH_css1\n"
p = write_rec("leading_tab_url.rec", body)
cli = run_cli(p)
print("--- leading_tab_url rc", cli.returncode)
print("stdout", cli.stdout, "stderr", cli.stderr.strip())
print("parsed", repr(parse_record(body, source=str(p)).get("url_in_css")))

# trailing tab empty prev
body = "css_name\tH_css1\nurl_in_css\tH_png1\npng_emitted\tH_png1\nprev_css_name\t\n"
p = write_rec("empty_prev_field.rec", body)
cli = run_cli(p)
print("--- empty_prev_field rc", cli.returncode, "stderr", cli.stderr.strip())
print(cli.stdout, end="")

# last-wins duplicate css_name
body = "css_name\tH_css0\ncss_name\tH_css1\nurl_in_css\tH_png0\npng_emitted\tH_png1\nprev_css_name\tH_css1\n"
p = write_rec("dup_css.rec", body)
cli = run_cli(p)
print("--- dup_css rc", cli.returncode)
print(cli.stdout, end="")

print("=== stdin ===")
text = (FIX / "090-leftover.rec").read_text(encoding="utf-8")
r = run_cli("-", stdin=text)
print("stdin leftover rc", r.returncode, "bytes", len(r.stdout))
print(r.stdout, end="")
print("stderr", r.stderr.strip())
rc, out = replica(text)
print("stdin stdout_eq", r.stdout == out, "rc_eq", r.returncode == rc)

r = run_cli("/dev/stdin", stdin=text)
print("/dev/stdin leftover rc", r.returncode)
print(r.stdout, end="")

r = subprocess.run([PY, str(CLI)], capture_output=True, text=True, check=False)
print("noargs rc", r.returncode, "stderr_head", r.stderr.splitlines()[:2])

r = subprocess.run([PY, str(CLI), str(FIX / "090-leftover.rec"), "extra"], capture_output=True, text=True, check=False)
print("extra positional rc", r.returncode)

print("=== origin / refuse ===")
origin = S090 / "files/leftover_identity_split.txt"
r = run_cli(origin)
print("origin rc", r.returncode, "stderr", r.stderr.strip()[:200])

for label, body in [
    ("json", '{"css_name":"H_css1","url_in_css":"H_png0","png_emitted":"H_png1"}\n'),
    ("css_source", '.a { background: url("./logo.png"); }\n'),
    ("stats", '{"assets":[{"name":"H_css1"},{"name":"H_png1"}]}\n'),
    ("unknown_field", "css_name\tH_css1\nurl_in_css\tH_png0\npng_emitted\tH_png1\ncontenthash\tH_css1\n"),
    ("Css_name", "Css_name\tH_css1\nurl_in_css\tH_png0\npng_emitted\tH_png1\n"),
    ("missing_png", "css_name\tH_css1\nurl_in_css\tH_png0\n"),
    ("comments_only", "# only\n"),
    ("spaces_not_tab", "css_name H_css1\nurl_in_css H_png0\npng_emitted H_png1\n"),
]:
    p = write_rec(f"refuse_{label}.txt", body)
    r = run_cli(p)
    print(f"refuse {label} rc={r.returncode} stderr={r.stderr.strip()[:160]!r}")

# BOM
p = SCRATCH / "bom.rec"
p.write_bytes(b"\xef\xbb\xbfcss_name\tH_css1\nurl_in_css\tH_png0\npng_emitted\tH_png1\n")
r = run_cli(p)
print("BOM rc", r.returncode, "stderr", r.stderr.strip()[:160])

# NUL
p = SCRATCH / "nul.rec"
p.write_bytes(b"css_name\tH_css1\n\x00url_in_css\tH_png0\npng_emitted\tH_png1\n")
r = run_cli(p)
print("NUL rc", r.returncode, "stderr", r.stderr.strip()[:160])

# invalid utf-8
p = SCRATCH / "badutf.rec"
p.write_bytes(b"css_name\tH_css1\nurl_in_css\tH_png0\npng_emitted\tH_png1\nprev_css_name\t\xff\n")
r = run_cli(p)
print("badutf rc", r.returncode, "stderr", r.stderr.strip()[:160])

print("=== missing path / directory ===")
r = run_cli("/nope")
print("missing rc", r.returncode, "stderr", r.stderr.strip())
r = run_cli(SCRATCH)
print("directory rc", r.returncode, "stderr", r.stderr.strip()[:160])

print("=== CRLF ===")
body = rec_body(css_name="H_css1", url_in_css="H_png0", png_emitted="H_png1", prev_css_name="H_css1").replace("\n", "\r\n")
p = write_rec("crlf.rec", body)
r = run_cli(p)
print("crlf rc", r.returncode, r.stdout)

print("=== space in filename ===")
p = write_rec("name with space.rec", rec_body(css_name="H_css1", url_in_css="H_png0", png_emitted="H_png1", prev_css_name="H_css1"))
r = run_cli(p)
print("space name rc", r.returncode, "leftover", rows(r.stdout).get("leftover"))

print("=== symlink ===")
target = FIX / "090-leftover.rec"
link = SCRATCH / "leftover.link"
if link.exists() or link.is_symlink():
    link.unlink()
link.symlink_to(target)
r = run_cli(link)
print("symlink rc", r.returncode, "leftover", rows(r.stdout).get("leftover"))

print("=== FIFO ===")
fifo = SCRATCH / "leftover.fifo"
if fifo.exists():
    fifo.unlink()
os.mkfifo(fifo)

def writer():
    time.sleep(0.05)
    with open(fifo, "w", encoding="utf-8") as fh:
        fh.write((FIX / "090-leftover.rec").read_text(encoding="utf-8"))

import threading
t = threading.Thread(target=writer)
t.start()
r = run_cli(fifo)
t.join()
print("fifo rc", r.returncode, "leftover", rows(r.stdout).get("leftover"))

print("=== process substitution via /dev/fd simulated: already FIFO ===")

print("=== huge comments ===")
huge = "#\n" * 10000 + rec_body(css_name="H_css1", url_in_css="H_png0", png_emitted="H_png1", prev_css_name="H_css1")
p = write_rec("huge.rec", huge)
t0 = time.perf_counter()
r = run_cli(p)
dt = time.perf_counter() - t0
print("huge leftover rc", r.returncode, "stdout_bytes", len(r.stdout), "dt", round(dt, 4), "leftover", rows(r.stdout).get("leftover"))
huge_ok = "#\n" * 10000 + rec_body(css_name="H_css0", url_in_css="H_png0", png_emitted="H_png0", prev_css_name="-")
p = write_rec("huge_fresh.rec", huge_ok)
t0 = time.perf_counter()
r = run_cli(p)
dt = time.perf_counter() - t0
print("huge fresh rc", r.returncode, "stdout_bytes", len(r.stdout), "dt", round(dt, 4), "leftover", rows(r.stdout).get("leftover"))

print("=== awk vs CLI load-bearing ===")
awk = r'''
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
  css=f["css_name"]; url=f["url_in_css"]; png=f["png_emitted"]; prev=f["prev_css_name"]
  leftover_url = (url != png)
  leftover_css = (prev != "" && css == prev)
  leftover = leftover_url || leftover_css
  printf "leftover_url\t%s\n", leftover_url?"yes":"no"
  printf "leftover_css_hash\t%s\n", leftover_css?"yes":"no"
  printf "leftover\t%s\n", leftover?"yes":"no"
}
'''
awk_cases = [
    FIX / "090-leftover.rec",
    FIX / "090-fresh.rec",
    FIX / "090-css-only.rec",
    SCRATCH / "url_only.rec",
    SCRATCH / "css_only_leftover.rec",
    SCRATCH / "omit_prev.rec",
    SCRATCH / "hyphen_collision.rec",
    SCRATCH / "unseen_widget.rec",
    SCRATCH / "unicode.rec",
    SCRATCH / "same_all.rec",
    SCRATCH / "prev_zero.rec",
    SCRATCH / "huge.rec",
]
awk_ok = 0
awk_n = 0
for p in awk_cases:
    cli = run_cli(p)
    a = subprocess.run(["awk", awk, str(p)], capture_output=True, text=True, check=False)
    crow = rows(cli.stdout)
    arow = rows(a.stdout)
    match = (
        crow.get("leftover_url") == arow.get("leftover_url")
        and crow.get("leftover_css_hash") == arow.get("leftover_css_hash")
        and crow.get("leftover") == arow.get("leftover")
        and cli.returncode == (1 if crow.get("leftover") == "yes" else 0)
    )
    awk_n += 1
    awk_ok += int(match)
    print(f"awk {p.name} match={match} cli={crow.get('leftover')} awk={arow.get('leftover')} rc={cli.returncode}")
print(f"awk_eq_cli_loadbearing {awk_ok}/{awk_n}")

print("=== python one-liner vs leftover+rc grid ===")
# grid of string pairs
tokens = ["", "-", "H_css0", "H_css1", "H_png0", "H_png1", "0", "yes"]
match = 0
n = 0
mismatch = []
# sample systematically rather than 8^4
from itertools import product
# keep bounded: vary url/png/css/prev independently on a smaller set
small = ["", "-", "A", "B"]
for css, url, png, prev in product(small, repeat=4):
    body = rec_body(css_name=css, url_in_css=url, png_emitted=png, prev_css_name=prev)
    p = write_rec("_grid.rec", body)
    cli = run_cli(p)
    n += 1
    if cli.returncode not in (0, 1) or (cli.returncode == 1 and not cli.stdout):
        # parse error?
        leftover_url = url != png
        leftover_css = bool(prev) and css == prev
        leftover = leftover_url or leftover_css
        # empty prev field: prev_css_name\t\n after strip of line
        if not cli.stdout:
            mismatch.append(("parse", css, url, png, prev, cli.returncode, cli.stderr.strip()[:80]))
            continue
    row = rows(cli.stdout)
    leftover_url = url != png
    leftover_css = bool(prev) and css == prev
    leftover = leftover_url or leftover_css
    ok = (
        row.get("leftover_url") == ("yes" if leftover_url else "no")
        and row.get("leftover_css_hash") == ("yes" if leftover_css else "no")
        and row.get("leftover") == ("yes" if leftover else "no")
        and cli.returncode == (1 if leftover else 0)
    )
    if ok:
        match += 1
    else:
        mismatch.append((css, url, png, prev, cli.returncode, row, leftover_url, leftover_css, leftover, cli.stderr.strip()[:80]))
print(f"grid_match {match}/{n} mismatches={len(mismatch)}")
for m in mismatch[:12]:
    print(" mismatch", m)

print("=== grep nearest workflow ===")
for name in ("090-leftover.rec", "090-fresh.rec", "090-css-only.rec"):
    g = subprocess.run(["grep", "-n", "H_css1", str(FIX / name)], capture_output=True, text=True, check=False)
    print(name, "H_css1 rc", g.returncode, "hits", g.stdout.strip().replace("\n", " | ") or "-")
    g = subprocess.run(["grep", "-n", "H_png0", str(FIX / name)], capture_output=True, text=True, check=False)
    print(name, "H_png0 rc", g.returncode, "hits", g.stdout.strip().replace("\n", " | ") or "-")

print("=== replica  all extra stdout_eq count ===")
# recount harvest + extras that parsed
print("done")
PY
