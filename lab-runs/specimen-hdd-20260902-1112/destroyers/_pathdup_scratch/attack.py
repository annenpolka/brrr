#!/usr/bin/env python3
"""pathdup destroyer attacks. Host-executed. No cargo / rustc."""
from __future__ import annotations

import dis
import hashlib
import io
import os
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path

RUN = Path("/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112")
CLI = RUN / "lineages/candidate-pathdup/pathdup"
FIX = RUN / "lineages/candidate-pathdup/fixtures"
S091 = RUN / "specimens/specimen-091"
SCRATCH = RUN / "destroyers/_pathdup_scratch"
PY = sys.executable

# Load inspect/format_report/parse_record by exec, no package import.
ns: dict = {}
exec(compile(CLI.read_text(encoding="utf-8"), str(CLI), "exec"), ns)
inspect_fn = ns["inspect"]
format_report = ns["format_report"]
parse_record = ns["parse_record"]
collapse_fn = ns["collapse"]


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


def thin(a: str, b: str) -> bool:
    """Independent leftover_dotdot: string inequality AND os.path.normpath equality."""
    return a != b and os.path.normpath(a) == os.path.normpath(b)


def thin_clash(a: str, b: str) -> bool:
    return a != b and os.path.normpath(a) != os.path.normpath(b)


def replica(text: str, source: str = "<replica>") -> tuple[int, str]:
    fields = parse_record(text, source=source)
    result = inspect_fn(fields)
    return (1 if result["leftover_dotdot"] else 0), format_report(result)


def rec_body(package: str = "pkg", path_a: str = "", path_b: str = "") -> str:
    return f"package\t{package}\npath_a\t{path_a}\npath_b\t{path_b}\n"


def banner(msg: str) -> None:
    print("\n====", msg, "====")


def compare_case(name: str, body: str, *, via: str | Path | None = None) -> dict:
    if via is None:
        p = write_rec(name if name.endswith(".rec") else name + ".rec", body)
        proc = run_cli(p)
        source = str(p)
    else:
        proc = run_cli(via)
        source = str(via)
        p = Path(str(via))
    try:
        rec_rc, rec_out = replica(body if via is None else Path(via).read_text(encoding="utf-8"), source)
    except Exception as exc:
        rec_rc, rec_out = 99, f"replica-exc: {exc}\n"
    r = rows(proc.stdout)
    a = r.get("path_a", "")
    b = r.get("path_b", "")
    leftover_thin = thin(a, b) if a or b else None
    leftover_cli = r.get("leftover_dotdot") == "yes"
    info = {
        "name": name,
        "cli_rc": proc.returncode,
        "replica_rc": rec_rc,
        "stdout_eq": proc.stdout == rec_out,
        "leftover_cli": leftover_cli,
        "leftover_thin": leftover_thin,
        "thin_eq": leftover_thin == leftover_cli if leftover_thin is not None else None,
        "stderr": proc.stderr.strip(),
        "stdout_n": len(proc.stdout),
        "leftover": r.get("leftover_dotdot"),
        "true_clash": r.get("true_clash"),
        "lexical_dup": r.get("lexical_dup"),
        "same_after": r.get("same_after_collapse"),
        "collapsed_a": r.get("collapsed_a"),
        "collapsed_b": r.get("collapsed_b"),
        "package": r.get("package"),
    }
    return info


def dump(info: dict) -> None:
    keys = (
        "name", "cli_rc", "replica_rc", "stdout_eq", "leftover", "leftover_thin",
        "thin_eq", "true_clash", "lexical_dup", "same_after",
    )
    print({k: info[k] for k in keys})
    if info["stderr"]:
        print("  stderr:", info["stderr"][:200])


def main() -> None:
    banner("meta")
    print("python", sys.version.split()[0])
    print("sha256", hashlib.sha256(CLI.read_bytes()).hexdigest())
    print("bytes", CLI.stat().st_size, "lines", len(CLI.read_text().splitlines()))
    print("cargo", subprocess.run(["which", "cargo"], capture_output=True, text=True).stdout.strip())
    print("rustc", subprocess.run(["which", "rustc"], capture_output=True, text=True).stdout.strip())
    print("NOT executing cargo/rustc")
    print("PurePosixPath call?", "PurePosixPath(" in CLI.read_text())
    print("inspect.co_names", inspect_fn.__code__.co_names)
    print("inspect.co_varnames", inspect_fn.__code__.co_varnames)
    print("collapse.co_names", collapse_fn.__code__.co_names)
    buf = io.StringIO()
    dis.dis(inspect_fn, file=buf)
    dis_text = buf.getvalue()
    (SCRATCH / "inspect.dis").write_text(dis_text)
    print("dis has COMPARE_OP", "COMPARE_OP" in dis_text)
    print("dis has CALL for collapse / normpath names:", [n for n in inspect_fn.__code__.co_names])

    banner("unit tests")
    t = subprocess.run(
        [PY, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=str(CLI.parent),
        capture_output=True,
        text=True,
    )
    print(t.stderr or t.stdout)
    print("tests rc", t.returncode)

    banner("demo twice")
    logs = []
    for i in (1, 2):
        p = subprocess.run(["bash", str(CLI.parent / "demo.sh")], capture_output=True, text=True)
        logp = SCRATCH / f"demo-live-{i}.log"
        logp.write_text(p.stdout)
        logs.append(p.stdout)
        print(f"demo-live-{i} rc={p.returncode} bytes={len(p.stdout)}")
    archived1 = (CLI.parent / "demo-1.log").read_text()
    archived2 = (CLI.parent / "demo-2.log").read_text()
    print("live1==live2", logs[0] == logs[1])
    print("live1==archived1", logs[0] == archived1)
    print("archived1==archived2", archived1 == archived2)
    print("cmp bytes", len(archived1))

    banner("owned fixtures")
    owned = []
    for name in ("091-dotdot.rec", "091-clean.rec", "091-clash.rec"):
        body = (FIX / name).read_text()
        info = compare_case(name, body, via=FIX / name)
        dump(info)
        owned.append(info)
        print("--- stdout ---")
        print(run_cli(FIX / name).stdout, end="")
        print("rc", run_cli(FIX / name).returncode)

    banner("independent python one-liner vs leftover_dotdot")
    for name in ("091-dotdot.rec", "091-clean.rec", "091-clash.rec"):
        fields = parse_record((FIX / name).read_text(), source=name)
        a, b = fields["path_a"], fields["path_b"]
        bit = a != b and os.path.normpath(a) == os.path.normpath(b)
        proc = run_cli(FIX / name)
        leftover = rows(proc.stdout)["leftover_dotdot"] == "yes"
        print(name, "thin", bit, "cli leftover", leftover, "rc", proc.returncode, "match", bit == leftover == (proc.returncode == 1 if leftover else proc.returncode == 0) or (bit == leftover and proc.returncode == (1 if leftover else 0)))

    banner("awk of two path keys")
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
  # leftover_dotdot cannot be computed in POSIX awk without a normpath;
  # print the two caller strings for python to collapse.
  printf "path_a\t%s\npath_b\t%s\n", f["path_a"], f["path_b"]
}
'''
    awk_ok = 0
    awk_n = 0
    for name in ("091-dotdot.rec", "091-clean.rec", "091-clash.rec"):
        p = subprocess.run(["awk", awk, str(FIX / name)], capture_output=True, text=True, check=True)
        fa, fb = None, None
        for line in p.stdout.splitlines():
            k, v = line.split("\t", 1)
            if k == "path_a":
                fa = v
            if k == "path_b":
                fb = v
        bit = thin(fa, fb)
        proc = run_cli(FIX / name)
        leftover = rows(proc.stdout)["leftover_dotdot"] == "yes"
        awk_n += 1
        if bit == leftover:
            awk_ok += 1
        print(name, "awk_paths_thin", bit, "cli", leftover)
    print(f"awk_eq_cli_leftover {awk_ok}/{awk_n}")

    banner("leftover_dotdot WITHOUT .. (name is a lie)")
    no_dotdot_cases = [
        ("dot-prefix", rec_body(path_a="./foo/Cargo.toml", path_b="foo/Cargo.toml")),
        ("double-slash", rec_body(path_a="foo//bar/Cargo.toml", path_b="foo/bar/Cargo.toml")),
        ("trailing-slash", rec_body(path_a="foo/bar/", path_b="foo/bar")),
        ("dot-segment", rec_body(path_a="a/./b", path_b="a/b")),
        ("mixed-dot-slash", rec_body(path_a="a/./b//c/", path_b="a/b/c")),
        ("trailing-dot", rec_body(path_a="a/b/.", path_b="a/b")),
    ]
    for name, body in no_dotdot_cases:
        info = compare_case(name, body)
        dump(info)
        print("  collapsed", info["collapsed_a"], "|", info["collapsed_b"])

    banner("leftover WITH .. but not cargo CARGO_HOME")
    extra_dotdot = [
        ("parent-collapse", rec_body(path_a="a/b/../c", path_b="a/c")),
        ("owned-shape-short", rec_body(path_a="/tmp/subfolder/../cargo/x", path_b="/tmp/cargo/x")),
        ("double-dotdot", rec_body(path_a="a/b/c/../../d", path_b="a/d")),
        ("root-escape", rec_body(path_a="/foo/../bar", path_b="/bar")),
        ("rel-up", rec_body(path_a="foo/../bar", path_b="bar")),
    ]
    for name, body in extra_dotdot:
        info = compare_case(name, body)
        dump(info)

    banner("true_clash vs leftover")
    clash_cases = [
        ("true-two-dirs", rec_body(path_a="dup1/Cargo.toml", path_b="dup2/Cargo.toml")),
        ("dotdot-different-dirs", rec_body(path_a="a/../b", path_b="c")),
        ("same-string", rec_body(path_a="/same/path", path_b="/same/path")),
        ("dotdot-to-different", rec_body(path_a="x/../y", path_b="x/../z")),
    ]
    for name, body in clash_cases:
        info = compare_case(name, body)
        dump(info)
        print("  collapsed", info["collapsed_a"], "|", info["collapsed_b"])

    banner("package is spectator")
    a = "/home/kaspar/tmp/subfolder/../cargo/x"
    b = "/home/kaspar/tmp/cargo/x"
    for pkg in ("serde", "other", "none", "0"):
        info = compare_case(f"pkg-{pkg}", rec_body(package=pkg, path_a=a, path_b=b))
        print(pkg, "leftover", info["leftover"], "rc", info["cli_rc"], "pkg_out", info["package"], "thin_eq", info["thin_eq"])

    banner("swap a/b")
    body = rec_body(
        package="serde",
        path_a="/home/kaspar/tmp/cargo/git/checkouts/serde/Cargo.toml",
        path_b="/home/kaspar/tmp/subfolder/../cargo/git/checkouts/serde/Cargo.toml",
    )
    info = compare_case("swap", body)
    dump(info)

    banner("backslash on POSIX (not a separator)")
    info = compare_case("backslash", rec_body(path_a=r"a\..\b", path_b="b"))
    dump(info)
    print("  collapsed", info["collapsed_a"], "|", info["collapsed_b"])
    print("  normpath backslash", os.path.normpath(r"a\..\b"))

    banner("leading double-slash POSIX")
    info = compare_case("lead-dslash", rec_body(path_a="//foo/bar", path_b="/foo/bar"))
    dump(info)
    print("  collapsed", info["collapsed_a"], "|", info["collapsed_b"])
    print("  normpath //foo", os.path.normpath("//foo/bar"), os.path.normpath("/foo/bar"))

    banner("empty / min fields")
    empty_cases = [
        ("empty-a", "package\tp\npath_a\t\npath_b\tx\n"),  # strip eats tab
        ("need-fields", "package\tp\n"),
        ("unknown", rec_body() + "extra\tz\n"),
        ("no-tab", "package serde\npath_a\ta\npath_b\tb\n"),
        ("spaces", "package serde\npath_a a\npath_b b\n"),
        ("comments-only", "# only\n"),
        ("empty-file", ""),
    ]
    for name, body in empty_cases:
        p = write_rec(name + ".rec", body)
        proc = run_cli(p)
        print(name, "rc", proc.returncode, "stderr", proc.stderr.strip()[:120], "stdout_n", len(proc.stdout))

    banner("last-wins duplicate path_a")
    body = (
        "package\tserde\n"
        "path_a\t/tmp/subfolder/../cargo/x\n"
        "path_a\t/tmp/cargo/x\n"
        "path_b\t/tmp/cargo/x\n"
    )
    info = compare_case("dup-last", body)
    dump(info)

    banner("extra tab after value")
    body = rec_body(path_a="/tmp/subfolder/../cargo/x\textra", path_b="/tmp/cargo/x")
    info = compare_case("extra-tab", body)
    dump(info)
    print("  path_a repr", repr(rows(run_cli(write_rec("extra-tab.rec", body)).stdout).get("path_a")))

    banner("CRLF / unicode / comments / BOM / NUL")
    crlf = "package\tserde\r\npath_a\t./u\r\npath_b\tu\r\n"
    info = compare_case("crlf", crlf)
    dump(info)
    uni = rec_body(package="依存", path_a="./テスト/Cargo.toml", path_b="テスト/Cargo.toml")
    info = compare_case("unicode", uni)
    dump(info)
    comm = "# comment\n\n" + rec_body(path_a="./x", path_b="x")
    info = compare_case("comments", comm)
    dump(info)

    bom = write_rec("bom.rec", "\ufeffpackage\tp\npath_a\ta\npath_b\tb\n")
    proc = run_cli(bom)
    print("bom rc", proc.returncode, "stderr", proc.stderr.strip()[:100])

    nul = write_rec("nul.rec", "package\tp\npath_a\ta\x00x\npath_b\ta\n")
    proc = run_cli(nul)
    print("nul rc", proc.returncode, "stderr", proc.stderr.strip()[:120], "stdout leftover", rows(proc.stdout).get("leftover_dotdot"))

    banner("stdin / fifo / symlink / space name / proc subst")
    leftover_body = rec_body(path_a="./x", path_b="x")
    proc = run_cli("-", stdin=leftover_body)
    rec_rc, rec_out = replica(leftover_body, "<stdin>")
    print("stdin leftover rc", proc.returncode, "stdout_eq", proc.stdout == rec_out, "leftover", rows(proc.stdout).get("leftover_dotdot"))
    proc = run_cli("-", stdin="")
    print("empty stdin rc", proc.returncode, "stderr", proc.stderr.strip()[:80])

    spacep = write_rec("name with space.rec", leftover_body)
    proc = run_cli(spacep)
    print("space-name rc", proc.returncode, "leftover", rows(proc.stdout).get("leftover_dotdot"))

    link = SCRATCH / "leftover.link"
    if link.exists() or link.is_symlink():
        link.unlink()
    link.symlink_to(spacep)
    proc = run_cli(link)
    print("symlink rc", proc.returncode, "leftover", rows(proc.stdout).get("leftover_dotdot"))

    fifo = SCRATCH / "leftover.fifo"
    if fifo.exists() or fifo.is_fifo():
        fifo.unlink()
    os.mkfifo(fifo)
    def writer():
        time.sleep(0.05)
        fifo.write_text(leftover_body)
    import threading
    threading.Thread(target=writer, daemon=True).start()
    proc = run_cli(fifo)
    print("fifo rc", proc.returncode, "leftover", rows(proc.stdout).get("leftover_dotdot"))

    proc = subprocess.run([PY, str(CLI), "/dev/stdin"], input=leftover_body, capture_output=True, text=True)
    print("/dev/stdin rc", proc.returncode, "leftover", rows(proc.stdout).get("leftover_dotdot"))

    banner("refuse origin / cargo warning / JSON / Cargo.toml")
    refuse = [
        ("origin-split", S091 / "files/leftover_identity_split.txt"),
        ("warning", write_rec("warning.txt", "warning: skipping duplicate package `serde v1.0.225`:\n  /home/kaspar/tmp/cargo/git/checkouts/serde/Cargo.toml\nin favor of /home/kaspar/tmp/subfolder/../cargo/git/checkouts/serde/Cargo.toml\n")),
        ("json", write_rec("json.json", '{"package":"serde","path_a":"./x","path_b":"x"}\n')),
        ("rs", S091 / "files/read_nested_packages_failing.rs"),
    ]
    for name, path in refuse:
        proc = run_cli(path)
        print(name, "rc", proc.returncode, "stderr", proc.stderr.strip()[:140], "stdout_n", len(proc.stdout))

    banner("missing / dir / extra argv")
    proc = run_cli("/nope")
    print("missing rc", proc.returncode, "stderr", proc.stderr.strip()[:80])
    proc = run_cli(SCRATCH)
    print("dir rc", proc.returncode, "stderr", proc.stderr.strip()[:80])
    proc = subprocess.run([PY, str(CLI)], capture_output=True, text=True)
    print("noargs rc", proc.returncode)
    proc = subprocess.run([PY, str(CLI), str(FIX / "091-dotdot.rec"), "extra"], capture_output=True, text=True)
    print("extra-arg rc", proc.returncode)

    banner("realpath vs normpath on live symlink (disk not consulted)")
    tree = SCRATCH / "disk"
    if tree.exists():
        import shutil
        shutil.rmtree(tree)
    (tree / "target" / "inner").mkdir(parents=True)
    (tree / "target" / "inner" / "Cargo.toml").write_text("[package]\nname='x'\n")
    (tree / "link").symlink_to(tree / "target")
    # lexical: link/../inner vs target/inner  -- wait link/../inner is sibling of link = disk/inner (missing)
    # leftover we want: link/inner vs target/inner  -- normpath does not follow symlink
    a = str(tree / "link" / "inner" / "Cargo.toml")
    b = str(tree / "target" / "inner" / "Cargo.toml")
    print("normpath a", os.path.normpath(a))
    print("normpath b", os.path.normpath(b))
    print("realpath a", os.path.realpath(a))
    print("realpath b", os.path.realpath(b))
    print("same realpath", os.path.realpath(a) == os.path.realpath(b))
    print("same normpath", os.path.normpath(a) == os.path.normpath(b))
    info = compare_case("symlink-live", rec_body(path_a=a, path_b=b))
    dump(info)
    # leftover_dotdot? strings differ; normpath of link/inner is still .../link/inner (no ..)
    # so leftover no, true_clash yes — CLI does not know they are the same directory
    print("  NOTE: same directory via symlink is true_clash, not leftover_dotdot")

    # lexical leftover that is NOT the same directory if a segment is a symlink:
    # a = disk/link/../other vs disk/other
    (tree / "other").mkdir()
    a2 = str(tree / "link" / ".." / "other")
    b2 = str(tree / "other")
    print("normpath a2", os.path.normpath(a2), "realpath a2", os.path.realpath(a2))
    print("normpath b2", os.path.normpath(b2), "realpath b2", os.path.realpath(b2))
    info = compare_case("symlink-dotdot", rec_body(path_a=a2, path_b=b2))
    dump(info)
    print("  leftover_dotdot yes even if realpath would follow the symlink first")

    banner("huge comments + leftover")
    huge = "#\n" * 10000 + rec_body(path_a="./x", path_b="x")
    t0 = time.perf_counter()
    info = compare_case("huge", huge)
    dt = time.perf_counter() - t0
    dump(info)
    print("  huge dt", round(dt, 4), "stdout_n", info["stdout_n"])

    banner("10000-char path leftover")
    long = "a/" * 2000 + "../b"
    short = "a/" * 1999 + "b"
    t0 = time.perf_counter()
    info = compare_case("longpath", rec_body(path_a=long, path_b=short))
    dt = time.perf_counter() - t0
    dump(info)
    print("  long dt", round(dt, 4), "stdout_n", info["stdout_n"], "collapsed_eq", info["collapsed_a"] == info["collapsed_b"])

    banner("token grid of lexical variants")
    bases = ["foo/bar", "./foo/bar", "foo//bar", "foo/bar/", "foo/./bar", "foo/baz/../bar", "foo/bar/.", "foo/../foo/bar"]
    grid_ok = 0
    grid_n = 0
    mismatches = []
    for i, pa in enumerate(bases):
        for j, pb in enumerate(bases):
            body = rec_body(path_a=pa, path_b=pb)
            info = compare_case(f"grid-{i}-{j}", body)
            grid_n += 1
            expected = thin(pa, pb)
            clash = thin_clash(pa, pb)
            ok = (
                info["stdout_eq"]
                and info["leftover_cli"] == expected
                and info["thin_eq"] is True
                and (info["true_clash"] == "yes") == clash
                and info["cli_rc"] == (1 if expected else 0)
                and info["replica_rc"] == info["cli_rc"]
            )
            if ok:
                grid_ok += 1
            else:
                mismatches.append((pa, pb, info))
    print(f"grid replica+thin {grid_ok}/{grid_n}")
    if mismatches:
        print("MISMATCHES", mismatches[:5])

    banner("harvest replica table")
    harvest_cases = [
        ("owned leftover (B)", (FIX / "091-dotdot.rec").read_text(), FIX / "091-dotdot.rec"),
        ("owned clean (A)", (FIX / "091-clean.rec").read_text(), FIX / "091-clean.rec"),
        ("owned clash (C)", (FIX / "091-clash.rec").read_text(), FIX / "091-clash.rec"),
        ("stdin leftover", leftover_body, None),
        ("dot-prefix leftover", rec_body(path_a="./foo", path_b="foo"), None),
        ("pkg spectator", rec_body(package="other", path_a=a, path_b=b), None),
    ]
    success = 0
    n = 0
    for name, body, via in harvest_cases:
        if via is None:
            p = write_rec("tbl-" + name.replace(" ", "_") + ".rec", body)
            proc = run_cli(p)
        else:
            proc = run_cli(via)
        rec_rc, rec_out = replica(body)
        fields = parse_record(body, source=name)
        bit = thin(fields["path_a"], fields["path_b"])
        leftover = rows(proc.stdout).get("leftover_dotdot") == "yes"
        n += 1
        ok = proc.stdout == rec_out and proc.returncode == rec_rc and leftover == bit and proc.returncode == (1 if leftover else 0)
        if ok:
            success += 1
        print(f"| {name} | {proc.returncode} | {rec_rc} | {proc.stdout == rec_out} | {bit} | {rows(proc.stdout).get('leftover_dotdot')} | {rows(proc.stdout).get('true_clash')} |")
    print(f"harvest replica leftover+rc {success}/{n}")

    # count all compare_case leftover successes from files we wrote
    banner("batch replica over scratch recs + fixtures")
    recs = list(FIX.glob("*.rec")) + list(SCRATCH.glob("*.rec"))
    batch_ok = 0
    batch_n = 0
    parse_err = 0
    for rec in recs:
        try:
            text = rec.read_text(encoding="utf-8")
        except Exception:
            continue
        proc = run_cli(rec)
        if proc.returncode != 0 and not proc.stdout:
            parse_err += 1
            continue
        if not proc.stdout:
            continue
        try:
            rec_rc, rec_out = replica(text, str(rec))
        except Exception:
            parse_err += 1
            continue
        r = rows(proc.stdout)
        if "path_a" not in r:
            parse_err += 1
            continue
        bit = thin(r["path_a"], r["path_b"])
        leftover = r.get("leftover_dotdot") == "yes"
        batch_n += 1
        if proc.stdout == rec_out and proc.returncode == rec_rc and leftover == bit and proc.returncode == (1 if leftover else 0):
            batch_ok += 1
        else:
            print("batch miss", rec.name, proc.returncode, rec_rc, leftover, bit, proc.stdout == rec_out)
    print(f"batch replica leftover+rc {batch_ok}/{batch_n} parse_or_empty {parse_err}")

    banner("nearest ordinary workflow")
    fields = parse_record((FIX / "091-dotdot.rec").read_text(), source="dotdot")
    a, b = fields["path_a"], fields["path_b"]
    print("a != b", a != b)
    print("normpath equal", os.path.normpath(a) == os.path.normpath(b))
    print("normpath(a)", os.path.normpath(a))
    print("python leftover", thin(a, b))
    print("package grep")
    g = subprocess.run(["grep", "-n", "serde", str(FIX / "091-dotdot.rec")], capture_output=True, text=True)
    print(g.stdout)
    g2 = subprocess.run(["grep", "-n", "serde", str(FIX / "091-clean.rec")], capture_output=True, text=True)
    print("clean serde grep rc", g2.returncode)
    print(g2.stdout)

    banner("done")


if __name__ == "__main__":
    main()
