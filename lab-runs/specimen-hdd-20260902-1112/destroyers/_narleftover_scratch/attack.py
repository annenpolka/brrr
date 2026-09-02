#!/usr/bin/env python3
"""Host attacks on narleftover. Isolation: RUN_DIR scratch only. No nix."""
from __future__ import annotations

import hashlib
import os
import stat
import subprocess
import sys
import types
from pathlib import Path

RUN = Path(
    "/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112"
)
ROOT = RUN / "lineages/candidate-narleftover"
CLI = ROOT / "narleftover"
FIX = ROOT / "fixtures"
S092 = RUN / "specimens/specimen-092"
SCRATCH = Path(__file__).resolve().parent
REPO = Path("/Users/annenpolka/ghq/github.com/annenpolka/brrr")

mod = types.ModuleType("narleftover")
exec(compile(CLI.read_text(encoding="utf-8"), str(CLI), "exec"), mod.__dict__)


def sh(*args, input=None, timeout=20, cwd=None):
    return subprocess.run(
        list(args),
        input=input,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
    )


def run_cli(path_or_dash, stdin=None, timeout=20):
    return sh(sys.executable, str(CLI), path_or_dash, input=stdin, timeout=timeout)


def replica_independent(text: str) -> tuple[str, int, dict]:
    """Independent reconstruction: leftover = cache_nar != lock_nar. No import of inspect."""
    fields: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "\t" not in line:
            raise ValueError("expected tab")
        k, v = line.split("\t", 1)
        k, v = k.strip(), v.strip()
        if k in {"rev", "lock_nar", "cache_nar"}:
            fields[k] = v
    lock = fields["lock_nar"]
    cache = fields["cache_nar"]
    leftover = cache != lock
    lines = [
        f"rev\t{fields.get('rev', '')}",
        f"lock_nar\t{lock}",
        f"cache_nar\t{cache}",
        f"leftover_stale_nar\t{'yes' if leftover else 'no'}",
    ]
    out = "\n".join(lines) + "\n"
    return out, (1 if leftover else 0), fields | {"leftover": leftover}


def awk_two_hashes(text: str) -> str:
    lock = cache = ""
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "\t" not in line:
            continue
        k, v = line.split("\t", 1)
        k, v = k.strip(), v.strip()
        if k == "lock_nar":
            lock = v
        elif k == "cache_nar":
            cache = v
    return "yes" if cache != lock else "no"


def write_rec(name: str, body: str) -> Path:
    p = SCRATCH / name
    p.write_text(body if body.endswith("\n") else body + "\n", encoding="utf-8")
    return p


def is_regular(p: Path) -> bool:
    try:
        return stat.S_ISREG(p.stat().st_mode)
    except OSError:
        return False


print("=== META ===")
raw = CLI.read_bytes()
print("sha256", hashlib.sha256(raw).hexdigest())
print("bytes", len(raw), "lines", raw.count(b"\n"))
print("python", sys.version.split()[0])
print("nix", sh("bash", "-lc", "command -v nix || true").stdout.strip() or "ABSENT")
print("inspect.co_names", mod.inspect.__code__.co_names)
print("parse_record.co_names", mod.parse_record.__code__.co_names)
print("format_report.co_names", mod.format_report.__code__.co_names)
print("KNOWN", mod.KNOWN)
print("main has narleftover?", sh("git", "ls-tree", "main", "--", "narleftover", cwd=REPO).stdout.strip() or "no")
print("archive tracked?", sh("git", "ls-files", "--", str(ROOT.relative_to(REPO)), cwd=REPO).stdout.strip() or "untracked")
print("HEAD", sh("git", "rev-parse", "--short", "HEAD", cwd=REPO).stdout.strip())

print("\n=== TESTS ===")
t = sh(sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / "tests"), "-v", timeout=30)
print(t.stdout)
print(t.stderr)
print("tests_rc", t.returncode)

print("\n=== DEMO ===")
d1 = sh("bash", str(ROOT / "demo.sh"), timeout=20)
d2 = sh("bash", str(ROOT / "demo.sh"), timeout=20)
(SCRATCH / "demo-live-1.log").write_text(d1.stdout)
(SCRATCH / "demo-live-2.log").write_text(d2.stdout)
print("demo_identical", d1.stdout == d2.stdout)
print("demo_vs_archived_1", d1.stdout == (ROOT / "demo-1.log").read_text())
print("demo_vs_archived_2", d2.stdout == (ROOT / "demo-2.log").read_text())
print("demo_rc", d1.returncode, d2.returncode)

print("\n=== OWNED + REPLICA ===")
owned_ok = 0
owned_n = 0
for f in sorted(FIX.iterdir()):
    if not is_regular(f):
        continue
    owned_n += 1
    text = f.read_text(encoding="utf-8")
    proc = run_cli(str(f))
    out_r, rc_r, _ = replica_independent(text)
    awk = awk_two_hashes(text)
    leftover_line = [ln for ln in proc.stdout.splitlines() if ln.startswith("leftover_stale_nar\t")][0]
    awk_match = leftover_line.endswith("\t" + awk)
    ident = proc.stdout == out_r and proc.returncode == rc_r
    if ident:
        owned_ok += 1
    (SCRATCH / f"cli-{f.name}.out").write_text(proc.stdout)
    (SCRATCH / f"host-{f.name}.out").write_text(out_r)
    print(
        f.name,
        "rc",
        proc.returncode,
        "replica_rc",
        rc_r,
        "identical",
        ident,
        "awk",
        awk,
        "awk_match",
        awk_match,
        "bytes",
        len(proc.stdout),
        "stderr",
        repr(proc.stderr),
    )
    print(proc.stdout, end="")
print("owned_replica", f"{owned_ok}/{owned_n}")

print("\n=== SHELL test != ===")
for f in sorted(FIX.iterdir()):
    if not is_regular(f):
        continue
    lock = cache = ""
    for raw in f.read_text().splitlines():
        if raw.startswith("lock_nar\t"):
            lock = raw.split("\t", 1)[1]
        elif raw.startswith("cache_nar\t"):
            cache = raw.split("\t", 1)[1]
    shell = sh("bash", "-lc", 'if [ "$1" != "$2" ]; then echo yes; else echo no; fi', "_", lock, cache)
    proc = run_cli(str(f))
    leftover = [ln.split("\t", 1)[1] for ln in proc.stdout.splitlines() if ln.startswith("leftover_stale_nar\t")][0]
    print(f.name, "shell", shell.stdout.strip(), "cli", leftover, "match", shell.stdout.strip() == leftover)

print("\n=== SPECTATOR REV ===")
poison = (FIX / "092-poison.rec").read_text()
# same hashes, different rev
p = write_rec(
    "spectator-rev.rec",
    "rev\tDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEF\n"
    "lock_nar\tsha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=\n"
    "cache_nar\tsha256-4cKMeE/8GptnxWnB6LliJy3gCvjVI34TXTwQHEsHcUA=\n",
)
proc_p = run_cli(str(FIX / "092-poison.rec"))
proc_s = run_cli(str(p))
# leftover column + rc identical; only rev line differs
def leftover_and_rc(proc):
    row = [ln for ln in proc.stdout.splitlines() if ln.startswith("leftover_stale_nar\t")][0]
    return row, proc.returncode

print("poison leftover", leftover_and_rc(proc_p))
print("spectator leftover", leftover_and_rc(proc_s))
print("leftover_rc_same", leftover_and_rc(proc_p) == leftover_and_rc(proc_s))
print("stdout_differs_only_rev", proc_p.stdout.replace(
    "5297592395d1dbd46e88247e459896838c854340",
    "DEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEF",
) == proc_s.stdout)

# same leftover hashes, empty-looking but valid rev of different length
p2 = write_rec(
    "rev-r1-not-r2.rec",
    "rev\t1111111111111111111111111111111111111111\n"
    "lock_nar\tsha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=\n"
    "cache_nar\tsha256-4cKMeE/8GptnxWnB6LliJy3gCvjVI34TXTwQHEsHcUA=\n",
)
print("other-rev leftover", leftover_and_rc(run_cli(str(p2))))

# consistent hashes, poison rev
p3 = write_rec(
    "fresh-hashes-poison-rev.rec",
    "rev\t5297592395d1dbd46e88247e459896838c854340\n"
    "lock_nar\tsha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=\n"
    "cache_nar\tsha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=\n",
)
print("owned-rev-fresh leftover", leftover_and_rc(run_cli(str(p3))))

print("\n=== TWO HASHES ONLY ===")
p4 = write_rec(
    "two-hashes-only.rec",
    "rev\t-\n"
    "lock_nar\tA\n"
    "cache_nar\tB\n",
)
proc = run_cli(str(p4))
print("two-hashes-only rc", proc.returncode)
print(proc.stdout, end="")
print("replica", replica_independent(p4.read_text())[0] == proc.stdout)

print("\n=== SEMANTIC / TOKEN ===")
cases = {
    "sri-vs-hex.rec": (
        "rev\t5297592395d1dbd46e88247e459896838c854340\n"
        "lock_nar\tsha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=\n"
        "cache_nar\t611f9c7a67e6e00304092544affb66d1c8acdeb58a4343474f15c0fc4071dc40\n"
    ),
    "quoted.rec": (
        "rev\t5297592395d1dbd46e88247e459896838c854340\n"
        "lock_nar\t\"sha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=\"\n"
        "cache_nar\tsha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=\n"
    ),
    "space-pad.rec": (
        "rev\t5297592395d1dbd46e88247e459896838c854340\n"
        "lock_nar\t sha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=\n"
        "cache_nar\tsha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=\n"
    ),
    "case-sri.rec": (
        "rev\t5297592395d1dbd46e88247e459896838c854340\n"
        "lock_nar\tSHA256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=\n"
        "cache_nar\tsha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=\n"
    ),
    "last-wins.rec": (
        "rev\t5297592395d1dbd46e88247e459896838c854340\n"
        "lock_nar\tsha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=\n"
        "cache_nar\tsha256-4cKMeE/8GptnxWnB6LliJy3gCvjVI34TXTwQHEsHcUA=\n"
        "cache_nar\tsha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=\n"
    ),
    "empty-cache.rec": (
        "rev\t5297592395d1dbd46e88247e459896838c854340\n"
        "lock_nar\tsha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=\n"
        "cache_nar\t-\n"
    ),
    "identical-dash.rec": (
        "rev\t-\n"
        "lock_nar\t-\n"
        "cache_nar\t-\n"
    ),
    "unicode.rec": (
        "rev\tリビジョン\n"
        "lock_nar\tハッシュ1\n"
        "cache_nar\tハッシュ2\n"
    ),
    "inner-tab.rec": (
        "rev\t5297592395d1dbd46e88247e459896838c854340\n"
        "lock_nar\tsha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=\n"
        "cache_nar\tsha256-4cKMeE/8GptnxWnB6LliJy3gCvjVI34TXTwQHEsHcUA=\textra\n"
    ),
}
for name, body in cases.items():
    p = write_rec(name, body)
    proc = run_cli(str(p))
    try:
        out_r, rc_r, _ = replica_independent(p.read_text())
        ident = proc.stdout == out_r and proc.returncode == rc_r
    except Exception as e:
        ident = f"replica_err {e}"
    leftover = leftover_and_rc(proc) if proc.returncode in (0, 1) and "leftover_stale_nar" in proc.stdout else (proc.stderr.strip(), proc.returncode)
    print(name, leftover, "identical", ident)

print("\n=== PARSE / IO ===")
parse_cases = []

def show_parse(label, proc):
    err = (proc.stderr or "").strip().splitlines()
    err0 = err[0] if err else ""
    print(f"{label}\trc={proc.returncode}\tstdout_len={len(proc.stdout)}\tstderr={err0!r}")
    parse_cases.append((label, proc.returncode, err0))

show_parse("missing", run_cli("/nope"))
show_parse("dir", run_cli(str(ROOT)))
empty = write_rec("empty.rec", "")
show_parse("empty", run_cli(str(empty)))
comments = write_rec("comments-only.rec", "# only\n# still\n")
show_parse("comments-only", run_cli(str(comments)))
show_parse("/dev/null", run_cli("/dev/null"))
unknown = write_rec("unknown.rec", "rev\tx\nlock_nar\ta\ncache_nar\tb\nnarHash\tc\n")
show_parse("unknown-field", run_cli(str(unknown)))
spaces = write_rec("spaces.rec", "rev x\nlock_nar a\ncache_nar b\n")
show_parse("spaces-not-tabs", run_cli(str(spaces)))
bom = write_rec("bom.rec", "\ufeffrev\tx\nlock_nar\ta\ncache_nar\tb\n")
show_parse("bom", run_cli(str(bom)))
need = write_rec("no-cache.rec", "rev\tx\nlock_nar\ta\n")
show_parse("missing-cache", run_cli(str(need)))
crlf = write_rec("crlf.rec", poison.replace("\n", "\r\n"))
proc = run_cli(str(crlf))
print("crlf leftover", leftover_and_rc(proc), "identical_owned", proc.stdout == proc_p.stdout)
bad = SCRATCH / "badutf.rec"
bad.write_bytes(b"rev\tx\nlock_nar\ta\ncache_nar\t\xff\xfe\n")
show_parse("badutf", run_cli(str(bad)))
show_parse("no-args", sh(sys.executable, str(CLI)))
show_parse("extra-pos", sh(sys.executable, str(CLI), str(FIX / "092-poison.rec"), "extra"))
h = sh(sys.executable, str(CLI), "-h")
print("help rc", h.returncode, "prog", "narleftover" in h.stdout)

# stdin
proc_stdin = run_cli("-", stdin=poison)
print("stdin-dash leftover", leftover_and_rc(proc_stdin), "eq_owned", proc_stdin.stdout == proc_p.stdout)
proc_pipe = sh("bash", "-lc", f"cat {FIX / '092-poison.rec'} | {sys.executable} {CLI} -")
print("pipe leftover", leftover_and_rc(proc_pipe))
proc_devstdin = run_cli("/dev/stdin", stdin=poison)
print("/dev/stdin leftover", leftover_and_rc(proc_devstdin), "eq", proc_devstdin.stdout == proc_p.stdout)

link = SCRATCH / "link.rec"
if link.exists() or link.is_symlink():
    link.unlink()
link.symlink_to(FIX / "092-poison.rec")
print("symlink leftover", leftover_and_rc(run_cli(str(link))))

spacef = write_rec("has space.rec", poison)
print("space-name leftover", leftover_and_rc(run_cli(str(spacef))))

# last-wins empty tab
empty_val = write_rec("empty-token.rec", "rev\tx\nlock_nar\ta\ncache_nar\t\n")
show_parse("empty-cache-token", run_cli(str(empty_val)))

print("\n=== ORIGIN PACKET ===")
for rel in [
    "files/lock_identity_split.txt",
    "files/github_fingerprint_failing.cc",
    "files/fetchers_fastpath_failing.cc",
    "files/compute_store_path_failing.cc",
    "TASK.md",
]:
    p = S092 / rel
    proc = run_cli(str(p))
    err = (proc.stderr or "").strip().splitlines()
    print(rel, "rc", proc.returncode, err[0] if err else proc.stdout[:80])

print("\n=== HOST REPLICA SWEEP ===")
# build many parseable records
sweep = []
base_lock = "sha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94="
base_cache = "sha256-4cKMeE/8GptnxWnB6LliJy3gCvjVI34TXTwQHEsHcUA="
variants = [
    ("owned-poison", "5297592395d1dbd46e88247e459896838c854340", base_lock, base_cache),
    ("owned-fresh", "5297592395d1dbd46e88247e459896838c854340", base_lock, base_lock),
    ("rev-other", "0" * 40, base_lock, base_cache),
    ("rev-dash", "-", base_lock, base_cache),
    ("A-vs-B", "r", "A", "B"),
    ("A-vs-A", "r", "A", "A"),
    ("empty-lock-dash", "r", "-", "H"),
    ("unicode", "リビ", "ハ1", "ハ2"),
    ("unicode-same", "リビ", "ハ", "ハ"),
    ("long", "r" * 8, "H" * 200, "G" * 200),
    ("sri-vs-hex", "r", base_lock, "611f9c7a67e6e00304092544affb66d1c8acdeb58a4343474f15c0fc4071dc40"),
    ("quoted", "r", f'"{base_lock}"', base_lock),
    ("case", "r", base_lock.upper(), base_lock),
    ("inner-tab-cache", "r", base_lock, base_cache + "\textra"),
    ("last-wins-fresh", "r", base_lock, base_lock),
]
fail = 0
for i, (name, rev, lock, cache) in enumerate(variants):
    body = f"rev\t{rev}\nlock_nar\t{lock}\ncache_nar\t{cache}\n"
    p = write_rec(f"sweep-{i:02d}-{name}.rec", body)
    proc = run_cli(str(p))
    out_r, rc_r, _ = replica_independent(p.read_text())
    awk = awk_two_hashes(p.read_text())
    leftover = leftover_and_rc(proc)[0].split("\t", 1)[1]
    ok = proc.stdout == out_r and proc.returncode == rc_r and leftover == awk
    if not ok:
        fail += 1
        print("FAIL", name, leftover, awk, proc.returncode, rc_r, proc.stdout != out_r)
    sweep.append(ok)
print("sweep_identical", f"{len(sweep)-fail}/{len(sweep)}")

# huge
huge_lock = "H" * 10000
huge_cache = "C" * 10000
p = write_rec("huge.rec", f"rev\tr\nlock_nar\t{huge_lock}\ncache_nar\t{huge_cache}\n")
proc = run_cli(str(p))
out_r, rc_r, _ = replica_independent(p.read_text())
print("huge identical", proc.stdout == out_r and proc.returncode == rc_r, "rc", proc.returncode, "bytes", len(proc.stdout))

print("\n=== LOCKIDENT DISTINCTION ===")
lockident = Path(
    "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/lockident-lockident/lockident/lockident.py"
)
print("lockident exists", lockident.is_file())
print("narleftover has hashlib?", b"hashlib" in raw)
print("narleftover has sha256?", b"sha256" in raw)
print("narleftover has identity?", b"identity" in raw)
print("narleftover leftover line", "leftover = cache != lock" in CLI.read_text())

print("\n=== REFPIN DISTINCTION ===")
refpin = RUN / "lineages/candidate-refpin/refpin"
print("refpin exists", refpin.is_file())
if refpin.is_file():
    rp = refpin.read_text()
    print("refpin has two records?", "FIRST" in rp or "rev_a" in rp or "second" in rp.lower())
    print("narleftover two records?", "FIRST" in CLI.read_text() or "rev_a" in CLI.read_text())

print("\nDONE")
