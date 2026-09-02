#!/usr/bin/env python3
"""Host-only destroyer-2 attacks against fingerhid. No cargo/rustc."""
from __future__ import annotations

import hashlib
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(
    "/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112"
)
CLI = ROOT / "lineages/candidate-fingerhid/fingerhid"
FIX = ROOT / "lineages/candidate-fingerhid/fixtures"
SCRATCH = Path(__file__).resolve().parent
WT_POINTER = ROOT / "lineages/candidate-fingerhid/WORKTREE.txt"
PY = sys.executable

KNOWN = ("path", "mtime", "vv", "size", "birth")


def parse_record(text: str, *, source: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "\t" not in line:
            raise ValueError(f"{source}:{lineno}: expected key<TAB>value")
        key, rest = line.split("\t", 1)
        key, rest = key.strip(), rest.strip()
        if key not in KNOWN:
            raise ValueError(f"{source}:{lineno}: unknown field {key!r}")
        if not rest or rest == "-":
            raise ValueError(f"{source}:{lineno}: not a legal NAME")
        fields[key] = rest
    for need in ("path", "mtime", "vv"):
        if need not in fields:
            raise ValueError(f"{source}: missing {need}")
    return fields


def inspect(a: dict[str, str], b: dict[str, str]) -> dict:
    same_path = a["path"] == b["path"]
    same_mtime = a["mtime"] == b["mtime"]
    vv_mismatch = a["vv"] != b["vv"]
    same_size = a.get("size") == b.get("size") if ("size" in a and "size" in b) else None
    same_birth = a.get("birth") == b.get("birth") if ("birth" in a and "birth" in b) else None
    hidden = same_path and same_mtime and vv_mismatch
    return {
        "path_a": a["path"],
        "path_b": b["path"],
        "mtime_a": a["mtime"],
        "mtime_b": b["mtime"],
        "vv_a": a["vv"],
        "vv_b": b["vv"],
        "same_path": same_path,
        "same_mtime": same_mtime,
        "vv_mismatch": vv_mismatch,
        "same_size": same_size,
        "same_birth": same_birth,
        "hidden_by_fingerprint": hidden,
    }


def yn(v):
    if v is None:
        return "-"
    return "yes" if v else "no"


def format_report(result: dict) -> str:
    lines = [
        f"same_path\t{yn(result['same_path'])}",
        f"same_mtime\t{yn(result['same_mtime'])}",
        f"vv_mismatch\t{yn(result['vv_mismatch'])}",
        f"same_size\t{yn(result['same_size'])}",
        f"same_birth\t{yn(result['same_birth'])}",
        f"hidden_by_fingerprint\t{yn(result['hidden_by_fingerprint'])}",
        f"vv_a\t{result['vv_a']}",
        f"vv_b\t{result['vv_b']}",
    ]
    return "\n".join(lines) + "\n"


def replica_run(a_path: Path, b_path: Path) -> tuple[str, str, int]:
    try:
        a = parse_record(a_path.read_text(encoding="utf-8"), source=str(a_path))
        b = parse_record(b_path.read_text(encoding="utf-8"), source=str(b_path))
    except (OSError, ValueError) as err:
        return "", f"fingerhid: {err}\n", 1
    result = inspect(a, b)
    return format_report(result), "", 1 if result["hidden_by_fingerprint"] else 0


def cli_run(a: str, b: str, extra: list[str] | None = None) -> subprocess.CompletedProcess[str]:
    cmd = [PY, str(CLI)]
    if extra:
        cmd.extend(extra)
    cmd.extend([a, b])
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def write(name: str, body: str) -> Path:
    p = SCRATCH / name
    p.write_text(body, encoding="utf-8")
    return p


def sh(cmd: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)


def awk_three(a: Path, b: Path) -> str:
    script = r"""
BEGIN{FS="\t"}
FNR==1{file++}
$1=="path"{p[file]=$2}
$1=="mtime"{m[file]=$2}
$1=="vv"{v[file]=$2}
END{
  hidden=(p[1]==p[2] && m[1]==m[2] && v[1]!=v[2])
  printf "hidden %s rc %s\n", hidden?"yes":"no", hidden?1:0
}
"""
    proc = subprocess.run(
        ["awk", script, str(a), str(b)],
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.stdout.strip()


def main() -> int:
    log: list[str] = []

    def note(s: str = "") -> None:
        log.append(s)
        print(s)

    data = CLI.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    note(f"sha256 {digest} ({len(data)} bytes, {len(CLI.read_text().splitlines())} lines)")
    note(f"python {sys.version.split()[0]}")
    note(f"which rustc: {sh('command -v rustc').stdout.strip() or '(empty)'}")
    note(f"which cargo: {sh('command -v cargo').stdout.strip() or '(empty)'}")
    note("rustc/cargo NOT executed")
    note(f"os.stat in CLI: {'os.stat' in CLI.read_text()}")
    note(f"subprocess in CLI: {'subprocess' in CLI.read_text()}")
    note(f"hashlib in CLI: {'hashlib' in CLI.read_text()}")

    wt = WT_POINTER.read_text().strip()
    wt_cli = Path(wt) / "fingerhid" / "fingerhid"
    if not wt_cli.exists():
        # some worktrees nest differently
        candidates = list(Path(wt).rglob("fingerhid"))
        note(f"worktree pointer {wt}")
        note(f"rglob fingerhid: {candidates[:8]}")
        for c in candidates:
            if c.is_file() and c.name == "fingerhid":
                wt_cli = c
                break
    if wt_cli.exists():
        same = wt_cli.read_bytes() == data
        note(f"worktree CLI {wt_cli} byte-identical={same}")
    else:
        note(f"worktree CLI missing under {wt}")

    git = sh("git -C /Users/annenpolka/ghq/github.com/annenpolka/brrr rev-parse --abbrev-ref HEAD")
    head = sh("git -C /Users/annenpolka/ghq/github.com/annenpolka/brrr rev-parse --short HEAD")
    lstree = sh("git -C /Users/annenpolka/ghq/github.com/annenpolka/brrr ls-tree HEAD -- fingerhid")
    note(f"parent HEAD {head.stdout.strip()} branch {git.stdout.strip()}")
    note(f"ls-tree fingerhid: {lstree.stdout.strip() or '(empty — not on main)'}")

    tests = subprocess.run(
        [PY, "-m", "unittest", "discover", "-s", str(CLI.parent / "tests"), "-v"],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(CLI.parent),
    )
    note("=== unittest ===")
    note(tests.stderr.strip() or tests.stdout.strip())
    note(f"unittest rc={tests.returncode}")

    demo1 = SCRATCH / "demo-live-1.log"
    demo2 = SCRATCH / "demo-live-2.log"
    d1 = subprocess.run(
        ["bash", str(CLI.parent / "demo.sh")],
        capture_output=True,
        text=True,
        check=False,
    )
    demo1.write_text(d1.stdout, encoding="utf-8")
    d2 = subprocess.run(
        ["bash", str(CLI.parent / "demo.sh")],
        capture_output=True,
        text=True,
        check=False,
    )
    demo2.write_text(d2.stdout, encoding="utf-8")
    arch1 = (CLI.parent / "demo-1.log").read_bytes()
    arch2 = (CLI.parent / "demo-2.log").read_bytes()
    note("=== demo ===")
    note(f"live1==live2 {d1.stdout == d2.stdout} bytes={len(d1.stdout)}")
    note(f"live1==arch1 {d1.stdout.encode() == arch1}")
    note(f"live2==arch2 {d2.stdout.encode() == arch2}")
    note(f"demo rc live1={d1.returncode} live2={d2.returncode}")

    owned_a = FIX / "086-fc42.rec"
    owned_b = FIX / "086-fc40.rec"
    agree = FIX / "unseen-agree.rec"

    cases: list[tuple[str, Path, Path]] = []

    def add(name: str, a: Path, b: Path) -> None:
        cases.append((name, a, b))

    add("owned", owned_a, owned_b)
    add("same-file", owned_a, owned_a)
    add("agree", owned_a, agree)
    add("swap", owned_b, owned_a)

    path_diff = write(
        "path-diff.rec",
        "path\t/usr/local/bin/rustc\nmtime\t2024-10-17 00:00:00\nvv\t(Fedora 1.82.0-1.fc40)\nsize\t2\nbirth\ty\n",
    )
    add("path-diff", owned_a, path_diff)

    mtime_diff = write(
        "mtime-diff.rec",
        "path\t/usr/bin/rustc\nmtime\t2024-10-18 00:00:00\nvv\t(Fedora 1.82.0-1.fc40)\nsize\t2\nbirth\ty\n",
    )
    add("mtime-diff", owned_a, mtime_diff)

    same_size = write(
        "same-size.rec",
        "path\t/usr/bin/rustc\nmtime\t2024-10-17 00:00:00\nvv\t(Fedora 1.82.0-1.fc40)\nsize\t1\nbirth\ty\n",
    )
    add("same-size-diff-birth", owned_a, same_size)

    same_birth = write(
        "same-birth.rec",
        "path\t/usr/bin/rustc\nmtime\t2024-10-17 00:00:00\nvv\t(Fedora 1.82.0-1.fc40)\nsize\t2\nbirth\tx\n",
    )
    add("diff-size-same-birth", owned_a, same_birth)

    omit_size = write(
        "omit-size.rec",
        "path\t/usr/bin/rustc\nmtime\t2024-10-17 00:00:00\nvv\t(Fedora 1.82.0-1.fc40)\nbirth\ty\n",
    )
    add("omit-size-b", owned_a, omit_size)

    min_b = write(
        "min.rec",
        "path\t/usr/bin/rustc\nmtime\t2024-10-17 00:00:00\nvv\t(Fedora 1.82.0-1.fc40)\n",
    )
    add("min-fields", owned_a, min_b)

    min_a = write(
        "min-a.rec",
        "path\t/usr/bin/rustc\nmtime\t2024-10-17 00:00:00\nvv\t(Fedora 1.82.0-1.fc42)\n",
    )
    add("min-min", min_a, min_b)

    garbage = write(
        "garbage.rec",
        "path\t/usr/bin/rustc\nmtime\t2024-10-17 00:00:00\nvv\tnot-even-a-rustc-string\n",
    )
    add("garbage-vv", owned_a, garbage)

    commented = write(
        "commented.rec",
        "# comment\npath\t/usr/bin/rustc\n# skip\nmtime\t2024-10-17 00:00:00\nvv\t(Fedora 1.82.0-1.fc40)\nsize\t2\nbirth\ty\n",
    )
    add("comments", owned_a, commented)

    crlf = write(
        "crlf.rec",
        "path\t/usr/bin/rustc\r\nmtime\t2024-10-17 00:00:00\r\nvv\t(Fedora 1.82.0-1.fc40)\r\nsize\t2\r\nbirth\ty\r\n",
    )
    add("crlf", owned_a, crlf)

    space = write(
        "file with space.rec",
        owned_b.read_text(encoding="utf-8"),
    )
    add("space-name", owned_a, space)

    dup = write(
        "dup-last.rec",
        "path\t/usr/bin/rustc\nmtime\t2024-10-17 00:00:00\nvv\tFIRST\nvv\t(Fedora 1.82.0-1.fc40)\nsize\t2\nbirth\ty\n",
    )
    add("dup-vv-last-wins", owned_a, dup)

    trail = write(
        "ws-vv.rec",
        "path\t/usr/bin/rustc\nmtime\t2024-10-17 00:00:00\nvv\t(Fedora 1.82.0-1.fc40)  \nsize\t2\nbirth\ty\n",
    )
    add("stripped-trailing-space", owned_a, trail)

    huge = write("huge.rec", f"path\t{'/x' * 5000}\nmtime\t2024-10-17 00:00:00\nvv\tA\n")
    huge2 = write("huge2.rec", f"path\t{'/x' * 5000}\nmtime\t2024-10-17 00:00:00\nvv\tB\n")
    add("huge-path", huge, huge2)

    same_vv_noise = write(
        "samevv-size.rec",
        "path\t/usr/bin/rustc\nmtime\t2024-10-17 00:00:00\nvv\t(Fedora 1.82.0-1.fc42)\nsize\t999\nbirth\tz\n",
    )
    add("same-vv-size-birth-noise", owned_a, same_vv_noise)

    host_only = write(
        "host-only.rec",
        "path\t/usr/bin/rustc\nmtime\t2024-10-17 00:00:00\nvv\trustc 1.82.0 (f6e511eec 2024-10-15) (Fedora 1.82.0-1.fc40)\n",
    )
    add("full-rustc-vv-string", owned_a, host_only)

    # parse-error leftovers
    novv = write("b-novv.rec", "path\t/usr/bin/rustc\nmtime\t2024-10-17 00:00:00\nsize\t2\nbirth\ty\n")
    add("missing-vv", owned_a, novv)

    dash_vv = write(
        "dash-vv.rec",
        "path\t/usr/bin/rustc\nmtime\t2024-10-17 00:00:00\nvv\t-\n",
    )
    add("dash-vv", owned_a, dash_vv)

    empty_vv = write(
        "empty-vv.rec",
        "path\t/usr/bin/rustc\nmtime\t2024-10-17 00:00:00\nvv\t\n",
    )
    add("empty-vv-value", owned_a, empty_vv)

    size_dash = write(
        "size-dash.rec",
        "path\t/usr/bin/rustc\nmtime\t2024-10-17 00:00:00\nvv\t(Fedora 1.82.0-1.fc40)\nsize\t-\n",
    )
    add("size-dash", owned_a, size_dash)

    empty_path = write(
        "empty-path.rec",
        "path\t\nmtime\t2024-10-17 00:00:00\nvv\tX\n",
    )
    add("empty-path", owned_a, empty_path)

    missing_mtime = write("missing-mtime.rec", "path\t/usr/bin/rustc\nvv\tX\n")
    add("missing-mtime", owned_a, missing_mtime)

    unknown = write("unknown.rec", "path\t/usr/bin/rustc\nmtime\t2024-10-17 00:00:00\nvv\tX\nfingerprint\t1\n")
    add("unknown-field", owned_a, unknown)

    notab = write("no-tab.rec", "path /usr/bin/rustc\n")
    add("no-tab", owned_a, notab)

    jsonf = write("json.rec", '{"path":"/usr/bin/rustc"}\n')
    add("json", owned_a, jsonf)

    bom = write("bom.rec", "\ufeffpath\t/usr/bin/rustc\nmtime\t2024-10-17 00:00:00\nvv\tX\n")
    add("bom", owned_a, bom)

    empty = write("empty.rec", "")
    add("empty-file", owned_a, empty)

    fingerid_a = ROOT / "lineages/candidate-fingerid/fixtures/086-fc42.rec"
    fingerid_b = ROOT / "lineages/candidate-fingerid/fixtures/086-fc40.rec"
    add("fingerid-owned-fixtures", fingerid_a, fingerid_b)

    replica_ok = 0
    replica_n = 0
    awk_ok = 0
    awk_n = 0
    note("=== cases ===")
    leftovers: dict[str, dict] = {}
    for name, a, b in cases:
        proc = cli_run(str(a), str(b))
        rout, rerr, rrc = replica_run(a, b)
        match = proc.stdout == rout and proc.returncode == rrc and proc.stderr == rerr
        replica_n += 1
        if match:
            replica_ok += 1
        leftovers[name] = {
            "rc": proc.returncode,
            "out": proc.stdout,
            "err": proc.stderr,
            "replica": match,
        }
        hidden_row = ""
        for line in proc.stdout.splitlines():
            if line.startswith("hidden_by_fingerprint") or line.startswith("same_size") or line.startswith("same_birth") or line.startswith("vv_mismatch"):
                hidden_row += line + " | "
        note(f"CASE {name} rc={proc.returncode} replica={match}")
        if proc.stdout:
            for line in proc.stdout.splitlines():
                note(f"  {line}")
        if proc.stderr:
            note(f"  STDERR {proc.stderr.strip()}")
        # awk only on success harvests
        if proc.returncode in (0, 1) and proc.stdout.startswith("same_path"):
            awk = awk_three(a, b)
            cli_hidden = "yes" if "hidden_by_fingerprint\tyes" in proc.stdout else "no"
            awk_hidden = "yes" if awk.startswith("hidden yes") else "no"
            awk_rc = awk.split()[-1] if awk else "?"
            ok = awk_hidden == cli_hidden and str(proc.returncode) == awk_rc
            awk_n += 1
            if ok:
                awk_ok += 1
            note(f"  AWK {awk} match={ok}")

    note(f"REPLICA {replica_ok}/{replica_n}")
    note(f"AWK {awk_ok}/{awk_n}")

    # shell three-equality on owned
    pa, pb = "/usr/bin/rustc", "/usr/bin/rustc"
    ma, mb = "2024-10-17 00:00:00", "2024-10-17 00:00:00"
    va, vb = "(Fedora 1.82.0-1.fc42)", "(Fedora 1.82.0-1.fc40)"
    shell = sh(f'test "{pa}" = "{pb}" && test "{ma}" = "{mb}" && test "{va}" != "{vb}"; echo rc=$?')
    note(f"SHELL three-eq owned rc={shell.stdout.strip()}")

    # missing path
    miss = cli_run("/no/such/fingerhid", str(owned_b))
    note(f"MISSING rc={miss.returncode} err={miss.stderr.strip()!r} out={miss.stdout!r}")

    # /dev/null
    devnull = cli_run("/dev/null", str(owned_b))
    note(f"DEVNULL rc={devnull.returncode} err={devnull.stderr.strip()!r}")

    # directory
    dirc = cli_run(str(FIX), str(owned_b))
    note(f"DIR rc={dirc.returncode} err={dirc.stderr.strip()!r}")

    # argparse
    noargs = subprocess.run([PY, str(CLI)], capture_output=True, text=True, check=False)
    onearg = subprocess.run([PY, str(CLI), str(owned_a)], capture_output=True, text=True, check=False)
    extra = subprocess.run(
        [PY, str(CLI), str(owned_a), str(owned_b), "x"],
        capture_output=True,
        text=True,
        check=False,
    )
    help_ = subprocess.run([PY, str(CLI), "--help"], capture_output=True, text=True, check=False)
    note(f"NOARGS rc={noargs.returncode}")
    note(f"ONEARG rc={onearg.returncode}")
    note(f"EXTRA rc={extra.returncode}")
    note(f"HELP rc={help_.returncode}")

    # stdin dash
    dash = cli_run("-", str(owned_b))
    note(f"DASH-PATH rc={dash.returncode} err={dash.stderr.strip()!r}")

    # symlink
    link = SCRATCH / "link-fc40.rec"
    if link.exists() or link.is_symlink():
        link.unlink()
    link.symlink_to(owned_b)
    linkp = cli_run(str(owned_a), str(link))
    note(f"SYMLINK rc={linkp.returncode} hidden={'hidden_by_fingerprint	yes' in linkp.stdout}")

    # FIFO
    fifo = SCRATCH / "fifo.rec"
    if fifo.exists() or fifo.is_fifo():
        fifo.unlink()
    os.mkfifo(fifo)
    # write in background
    def _fill_fifo():
        with open(fifo, "w", encoding="utf-8") as fh:
            fh.write(owned_b.read_text(encoding="utf-8"))

    import threading

    t = threading.Thread(target=_fill_fifo)
    t.start()
    fifop = cli_run(str(owned_a), str(fifo))
    t.join(timeout=5)
    note(f"FIFO rc={fifop.returncode} hidden={'hidden_by_fingerprint	yes' in fifop.stdout} err={fifop.stderr.strip()!r}")

    # process substitution via bash
    body = owned_b.read_text(encoding="utf-8")
    procsub = subprocess.run(
        ["bash", "-c", f'python3 "$1" "$2" <(printf %s "$3")', "_", str(CLI), str(owned_a), body],
        capture_output=True,
        text=True,
        check=False,
    )
    note(f"PROCSUB rc={procsub.returncode} hidden={'hidden_by_fingerprint	yes' in procsub.stdout}")

    # invalid utf-8
    badutf = SCRATCH / "badutf.rec"
    badutf.write_bytes(b"path\t/usr/bin/rustc\nmtime\t2024-10-17 00:00:00\nvv\t\xff\xfe\n")
    badp = cli_run(str(owned_a), str(badutf))
    note(f"BADUTF rc={badp.returncode} err={badp.stderr.strip()!r}")

    # NUL in vv (text mode)
    nul = write("nul.rec", "path\t/usr/bin/rustc\nmtime\t2024-10-17 00:00:00\nvv\tfc40\x00suffix\n")
    nulp = cli_run(str(owned_a), str(nul))
    note(f"NUL rc={nulp.returncode} out={nulp.stdout!r} err={nulp.stderr.strip()!r}")

    # inspect.co_names via exec
    ns: dict = {}
    exec(CLI.read_text(encoding="utf-8"), ns)
    note(f"inspect.co_names {ns['inspect'].__code__.co_names}")
    note(f"parse_record.co_names {ns['parse_record'].__code__.co_names}")
    note(f"format_report.co_names {ns['format_report'].__code__.co_names}")

    rustcinfo = write("rustcinfo.json", '{"rustc_fingerprint":1}\n')
    jsonp = cli_run(str(owned_a), rustcinfo)
    note(f"RUSTCINFO rc={jsonp.returncode} err={jsonp.stderr.strip()!r}")

    (SCRATCH / "attack.log").write_text("\n".join(log) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
