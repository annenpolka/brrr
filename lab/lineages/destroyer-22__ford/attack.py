#!/usr/bin/env python3
"""Adversarial lattice attacks on ford. No rewrites of the victim."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path("/tmp/destroy-ford")
FIX = ROOT / "fixtures"
LOG = ROOT / "logs"
TRANS = ROOT / "transcript.txt"
FORD = Path("/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-cb2e776f004a/ford")
WEIR = Path("/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bad-eb91-7d80-9aa0-109aeaf41ba5/weir")
KIZU = Path("/Users/annenpolka/ghq/github.com/annenpolka/kizu")
SIT = Path("/Users/annenpolka/ghq/github.com/annenpolka/sitbone")
SKILLS = Path("/Users/annenpolka/ghq/github.com/annenpolka/skills")

lines: list[str] = []


def log(msg: str = "") -> None:
    lines.append(msg)
    print(msg, flush=True)


def git(repo: Path, *args: str, env: dict | None = None, check: bool = True) -> subprocess.CompletedProcess:
    e = os.environ.copy()
    e.update(
        {
            "GIT_AUTHOR_NAME": "ford-destroyer",
            "GIT_AUTHOR_EMAIL": "destroyer@example.test",
            "GIT_COMMITTER_NAME": "ford-destroyer",
            "GIT_COMMITTER_EMAIL": "destroyer@example.test",
            "GIT_AUTHOR_DATE": e.get("GIT_AUTHOR_DATE", "2022-01-01T00:00:00"),
            "GIT_COMMITTER_DATE": e.get("GIT_COMMITTER_DATE", "2022-01-01T00:00:00"),
        }
    )
    if env:
        e.update(env)
    return subprocess.run(
        ["git", "-c", "commit.gpgsign=false", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        env=e,
        check=check,
    )


def init_repo(name: str) -> Path:
    p = FIX / name
    if p.exists():
        shutil.rmtree(p)
    p.mkdir(parents=True)
    git(p, "init", "-q", "-b", "main")
    git(p, "config", "user.name", "ford-destroyer")
    git(p, "config", "user.email", "destroyer@example.test")
    git(p, "config", "commit.gpgsign", "false")
    return p


def dated(iso: str) -> dict:
    return {"GIT_AUTHOR_DATE": iso, "GIT_COMMITTER_DATE": iso}


def write(repo: Path, rel: str, content: str) -> None:
    dest = repo / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content)


def sha(repo: Path, rev: str = "HEAD") -> str:
    return git(repo, "rev-parse", rev).stdout.strip()


def short(repo: Path, rev: str = "HEAD") -> str:
    return git(repo, "rev-parse", "--short=7", rev).stdout.strip()


def run_tool(tool: Path, args: list[str], cwd: Path | None = None) -> dict:
    cmd = [str(tool), *args]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd) if cwd else None)
    out = {
        "cmd": " ".join(cmd),
        "rc": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "json": None,
    }
    if "--json" in args and proc.stdout.strip().startswith(("{", "[")):
        try:
            out["json"] = json.loads(proc.stdout)
        except json.JSONDecodeError:
            pass
    return out


def save(name: str, result: dict) -> dict:
    (LOG / f"{name}.json").write_text(
        json.dumps(
            {
                "cmd": result["cmd"],
                "rc": result["rc"],
                "stderr": result["stderr"],
                "report": result["json"],
                "stdout": result["stdout"] if result["json"] is None else None,
            },
            indent=2,
            default=str,
        )
    )
    (LOG / f"{name}.out").write_text(result["stdout"] or "")
    (LOG / f"{name}.err").write_text(result["stderr"] or "")
    (LOG / f"{name}.rc").write_text(str(result["rc"]))
    return result


def era_summary(rep: dict | None) -> str:
    if not rep:
        return "(no json)"
    bits = []
    for e in rep.get("eras") or []:
        st = e.get("status")
        kind = e.get("kind")
        start = (e.get("start") or {}).get("short") or (e.get("start") or {}).get("sha", "")[:7]
        end = (e.get("end") or {}).get("short") or ""
        join = e.get("join") or ""
        origin = ((e.get("origin") or {}) or {}).get("short") or ""
        cont = ((e.get("continued_from") or {}) or {}).get("short") or ""
        tree = e.get("tree")
        extra = []
        if join:
            extra.append(join)
        if origin:
            extra.append(f"origin={origin}")
        if cont:
            extra.append(f"from={cont}")
        if tree:
            extra.append(f"tree={tree}")
        span = start if start == end or not end else f"{start}..{end}"
        bits.append(f"{st}/{kind}[{span} n={e.get('count')}]" + ((" " + " ".join(extra)) if extra else ""))
    now = rep.get("holds_now")
    tree_now = rep.get("tree_now")
    fords = rep.get("fords")
    weirs = rep.get("weirs")
    true_n = rep.get("true_commits")
    scanned = rep.get("commits_scanned")
    walk = rep.get("walk")
    never = rep.get("never_held")
    warn = "; ".join(rep.get("warnings") or [])
    tail = f"now={now} tree_now={tree_now} true={true_n}/{scanned} fords={fords} weirs={weirs} walk={walk} never={never}"
    if warn:
        tail += f" warn={warn[:180]}"
    return " | ".join(bits) + "\n    " + tail


def header(title: str) -> None:
    log()
    log("=" * 72)
    log(title)
    log("=" * 72)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def build_diamond() -> dict:
    r = init_repo("diamond")
    write(r, "README", "base\n")
    git(r, "add", "README", env=dated("2022-01-01T00:00:00"))
    git(r, "commit", "-q", "-m", "A base", env=dated("2022-01-01T00:00:00"))
    A = sha(r)
    git(r, "checkout", "-q", "-b", "topic")
    write(r, "src/app.py", "TOKEN\nif x > 0:\n    return 1\n")
    git(r, "add", "src/app.py", env=dated("2022-01-02T00:00:00"))
    git(r, "commit", "-q", "-m", "C TOKEN born on topic", env=dated("2022-01-02T00:00:00"))
    C = sha(r)
    write(r, "src/app.py", "TOKEN\nif x > 0:\n    return 1\nstill\n")
    git(r, "add", "src/app.py", env=dated("2022-01-03T00:00:00"))
    git(r, "commit", "-q", "-m", "D still holds on topic", env=dated("2022-01-03T00:00:00"))
    D = sha(r)
    git(r, "checkout", "-q", "main")
    write(r, "README", "base\nmainline\n")
    git(r, "add", "README", env=dated("2022-01-04T00:00:00"))
    git(r, "commit", "-q", "-m", "B main no occupancy", env=dated("2022-01-04T00:00:00"))
    B = sha(r)
    git(r, "merge", "-q", "--no-ff", "topic", "-m", "M merge topic", env=dated("2022-01-05T00:00:00"))
    M = sha(r)
    return {"A": A, "B": B, "C": C, "D": D, "M": M, "repo": r}


def build_octopus() -> dict:
    """3-parent merge. Two occupancy patterns: 1-of-3 vs 2-of-3 TRUE parents."""
    out = {}
    for name, t1_has, t2_has in (
        ("octopus-1of3", True, False),
        ("octopus-2of3", True, True),
    ):
        r = init_repo(name)
        write(r, "README", "root\n")
        git(r, "add", "README", env=dated("2022-02-01T00:00:00"))
        git(r, "commit", "-q", "-m", "A root no occupancy", env=dated("2022-02-01T00:00:00"))
        A = sha(r)
        git(r, "checkout", "-q", "-b", "t1")
        if t1_has:
            write(r, "src/app.py", "from t1\n")
            git(r, "add", "src/app.py", env=dated("2022-02-02T00:00:00"))
        else:
            write(r, "t1.txt", "side\n")
            git(r, "add", "t1.txt", env=dated("2022-02-02T00:00:00"))
        git(r, "commit", "-q", "-m", "T1 " + ("has" if t1_has else "no") + " occupancy", env=dated("2022-02-02T00:00:00"))
        T1 = sha(r)
        git(r, "checkout", "-q", "main")
        git(r, "checkout", "-q", "-b", "t2")
        if t2_has:
            write(r, "src/app.py", "from t2\n")
            git(r, "add", "src/app.py", env=dated("2022-02-03T00:00:00"))
        else:
            write(r, "t2.txt", "side\n")
            git(r, "add", "t2.txt", env=dated("2022-02-03T00:00:00"))
        git(r, "commit", "-q", "-m", "T2 " + ("has" if t2_has else "no") + " occupancy", env=dated("2022-02-03T00:00:00"))
        T2 = sha(r)
        git(r, "checkout", "-q", "main")
        # octopus: merge both topics. allow conflict on src/app.py if both have it.
        proc = git(r, "merge", "--no-ff", "-m", "M octopus t1 t2", "t1", "t2", env=dated("2022-02-04T00:00:00"), check=False)
        if proc.returncode != 0:
            if t1_has and t2_has:
                write(r, "src/app.py", "merged from t1 and t2\n")
                git(r, "add", "src/app.py")
            git(r, "add", "-A")
            git(r, "commit", "-q", "-m", "M octopus t1 t2", env=dated("2022-02-04T00:00:00"))
        M = sha(r)
        parents = git(r, "rev-parse", "HEAD^1", "HEAD^2", "HEAD^3", check=False)
        nparents = len([p for p in git(r, "log", "-1", "--format=%P").stdout.split() if p])
        out[name] = {
            "repo": r,
            "A": A,
            "T1": T1,
            "T2": T2,
            "M": M,
            "nparents": nparents,
            "t1_has": t1_has,
            "t2_has": t2_has,
            "parents": git(r, "log", "-1", "--format=%P").stdout.strip(),
        }
    return out


def build_mom() -> dict:
    """Merge-of-merges: M1 is F⊓T (tree TRUE); M2's merge-parent is M1 (trees T⊓T)."""
    r = init_repo("merge-of-merges")
    write(r, "README", "A\n")
    git(r, "add", "README", env=dated("2022-03-01T00:00:00"))
    git(r, "commit", "-q", "-m", "A base no occupancy", env=dated("2022-03-01T00:00:00"))
    A = sha(r)
    git(r, "checkout", "-q", "-b", "topic1")
    write(r, "src/app.py", "born on topic1\n")
    git(r, "add", "src/app.py", env=dated("2022-03-02T00:00:00"))
    git(r, "commit", "-q", "-m", "C born on topic1", env=dated("2022-03-02T00:00:00"))
    C = sha(r)
    write(r, "src/app.py", "born on topic1\nstill\n")
    git(r, "add", "src/app.py", env=dated("2022-03-03T00:00:00"))
    git(r, "commit", "-q", "-m", "D still holds", env=dated("2022-03-03T00:00:00"))
    D = sha(r)
    git(r, "checkout", "-q", "main")
    write(r, "README", "A\nB main\n")
    git(r, "add", "README", env=dated("2022-03-04T00:00:00"))
    git(r, "commit", "-q", "-m", "B main no occupancy", env=dated("2022-03-04T00:00:00"))
    B = sha(r)
    git(r, "merge", "-q", "--no-ff", "topic1", "-m", "M1 merge topic1 (introducing)", env=dated("2022-03-05T00:00:00"))
    M1 = sha(r)
    # second topic from M1? No: from an ancestor that already has the file, so
    # M2's *trees* are T⊓T. Use a topic branched from D (has file) after M1 is done.
    git(r, "checkout", "-q", "-b", "topic2", D)
    write(r, "side.txt", "topic2\n")
    git(r, "add", "side.txt", env=dated("2022-03-06T00:00:00"))
    git(r, "commit", "-q", "-m", "E topic2 still has app.py", env=dated("2022-03-06T00:00:00"))
    E = sha(r)
    git(r, "checkout", "-q", "main")  # at M1
    git(r, "merge", "-q", "--no-ff", "topic2", "-m", "M2 merge-of-merges (parent is M1)", env=dated("2022-03-07T00:00:00"), check=False)
    # might be clean
    if git(r, "rev-parse", "--verify", "HEAD", check=False).returncode == 0:
        pass
    M2 = sha(r)
    # then a non-merge on main so first-parent TRUE can start after M2
    write(r, "after.txt", "post\n")
    git(r, "add", "after.txt", env=dated("2022-03-08T00:00:00"))
    git(r, "commit", "-q", "-m", "X non-merge after M2", env=dated("2022-03-08T00:00:00"))
    X = sha(r)
    return {"repo": r, "A": A, "B": B, "C": C, "D": D, "M1": M1, "E": E, "M2": M2, "X": X}


def build_nested_merges() -> dict:
    """Cascade of merges after an introducing ford, like kizu PR#2..#6."""
    r = init_repo("nested-merges")
    write(r, "README", "A\n")
    git(r, "add", "README", env=dated("2022-04-01T00:00:00"))
    git(r, "commit", "-q", "-m", "A no occupancy", env=dated("2022-04-01T00:00:00"))
    A = sha(r)
    git(r, "checkout", "-q", "-b", "t0")
    write(r, "src/app.py", "born\n")
    git(r, "add", "src/app.py", env=dated("2022-04-02T00:00:00"))
    git(r, "commit", "-q", "-m", "topic birth", env=dated("2022-04-02T00:00:00"))
    BIRTH = sha(r)
    git(r, "checkout", "-q", "main")
    git(r, "merge", "-q", "--no-ff", "t0", "-m", "M0 introducing", env=dated("2022-04-03T00:00:00"))
    M0 = sha(r)
    merges = [M0]
    for i in range(1, 5):
        git(r, "checkout", "-q", "-b", f"t{i}")
        write(r, f"t{i}.txt", f"{i}\n")
        git(r, "add", f"t{i}.txt", env=dated(f"2022-04-{3+i:02d}T00:00:00"))
        git(r, "commit", "-q", "-m", f"topic {i}", env=dated(f"2022-04-{3+i:02d}T00:00:00"))
        git(r, "checkout", "-q", "main")
        git(r, "merge", "-q", "--no-ff", f"t{i}", "-m", f"M{i} preserve-looking", env=dated(f"2022-04-{10+i:02d}T00:00:00"))
        merges.append(sha(r))
    write(r, "end.txt", "done\n")
    git(r, "add", "end.txt", env=dated("2022-04-20T00:00:00"))
    git(r, "commit", "-q", "-m", "non-merge tail", env=dated("2022-04-20T00:00:00"))
    TAIL = sha(r)
    return {"repo": r, "A": A, "BIRTH": BIRTH, "merges": merges, "TAIL": TAIL}


def build_rename() -> dict:
    r = init_repo("rename")
    write(r, "old.txt", "TOKEN_RENAME body\n")
    git(r, "add", "old.txt", env=dated("2022-05-01T00:00:00"))
    git(r, "commit", "-q", "-m", "birth old.txt", env=dated("2022-05-01T00:00:00"))
    git(r, "mv", "old.txt", "new name.txt")
    git(r, "commit", "-q", "-m", "rename to new name.txt", env=dated("2022-05-02T00:00:00"))
    git(r, "mv", "new name.txt", "計画.md")
    git(r, "commit", "-q", "-m", "rename to CJK", env=dated("2022-05-03T00:00:00"))
    # rename across a merge: branch, edit, merge
    git(r, "checkout", "-q", "-b", "side")
    write(r, "計画.md", "TOKEN_RENAME body\nside\n")
    git(r, "add", "計画.md", env=dated("2022-05-04T00:00:00"))
    git(r, "commit", "-q", "-m", "side edits CJK", env=dated("2022-05-04T00:00:00"))
    git(r, "checkout", "-q", "main")
    write(r, "other.txt", "x\n")
    git(r, "add", "other.txt", env=dated("2022-05-05T00:00:00"))
    git(r, "commit", "-q", "-m", "main other", env=dated("2022-05-05T00:00:00"))
    git(r, "merge", "-q", "--no-ff", "side", "-m", "M merge side (CJK lives on both)", env=dated("2022-05-06T00:00:00"))
    return {"repo": r}


def build_timeout_merge() -> dict:
    r = init_repo("timeout-merge")
    write(r, "keep.txt", "fast\n")
    git(r, "add", "keep.txt", env=dated("2022-06-01T00:00:00"))
    git(r, "commit", "-q", "-m", "A fast", env=dated("2022-06-01T00:00:00"))
    git(r, "checkout", "-q", "-b", "slow")
    write(r, "slow", "slow\n")
    git(r, "add", "slow", env=dated("2022-06-02T00:00:00"))
    git(r, "commit", "-q", "-m", "B slow", env=dated("2022-06-02T00:00:00"))
    git(r, "checkout", "-q", "main")
    git(r, "merge", "-q", "--no-ff", "slow", "-m", "M timeout parent", env=dated("2022-06-03T00:00:00"))
    return {"repo": r}


def build_binary() -> dict:
    r = init_repo("binary")
    write(r, "visible.txt", "TOKEN_BIN visible\n")
    (r / "secret.bin").write_bytes(b"TOKEN_BIN\x00hidden\n")
    git(r, "add", "visible.txt", "secret.bin", env=dated("2022-07-01T00:00:00"))
    git(r, "commit", "-q", "-m", "text + binary", env=dated("2022-07-01T00:00:00"))
    (r / "visible.txt").unlink()
    git(r, "add", "-A", env=dated("2022-07-02T00:00:00"))
    git(r, "commit", "-q", "-m", "remove text", env=dated("2022-07-02T00:00:00"))
    return {"repo": r}


def build_merge_added() -> dict:
    r = init_repo("merge-added")
    write(r, "a.txt", "a\n")
    git(r, "add", "a.txt", env=dated("2022-08-01T00:00:00"))
    git(r, "commit", "-q", "-m", "A", env=dated("2022-08-01T00:00:00"))
    git(r, "checkout", "-q", "-b", "side")
    write(r, "b.txt", "b\n")
    git(r, "add", "b.txt", env=dated("2022-08-02T00:00:00"))
    git(r, "commit", "-q", "-m", "B", env=dated("2022-08-02T00:00:00"))
    git(r, "checkout", "-q", "main")
    git(r, "merge", "--no-ff", "--no-commit", "side", check=False)
    write(r, "new.txt", "newborn\n")
    git(r, "add", "new.txt")
    git(r, "commit", "-q", "-m", "M adds new.txt neither parent had", env=dated("2022-08-03T00:00:00"))
    return {"repo": r}


def clone_shallow(src: Path, name: str) -> Path:
    dest = FIX / name
    if dest.exists():
        shutil.rmtree(dest)
    subprocess.run(["git", "clone", "-q", "--depth", "1", f"file://{src}", str(dest)], check=True)
    return dest


# ---------------------------------------------------------------------------
# Attacks
# ---------------------------------------------------------------------------

def main() -> int:
    log("DESTROYER_FORD transcript")
    log(f"ford={FORD}")
    log(f"weir={WEIR}")
    log()

    header("0. victim still runs (no rewrite)")
    help_out = run_tool(FORD, ["--help"])
    log(f"ford --help rc={help_out['rc']} lines={len(help_out['stdout'].splitlines())}")
    lat = save("lattice", run_tool(FORD, ["--json", "lattice"]))
    log(f"lattice rc={lat['rc']} meet T⊓F={lat['json']['all']['table'][1][lat['json']['all']['table'][0].index('FALSE')] if lat['json'] else '?'}")

    header("build fixtures")
    diamond = build_diamond()
    octopus = build_octopus()
    mom = build_mom()
    nested = build_nested_merges()
    rename = build_rename()
    tmerge = build_timeout_merge()
    binary = build_binary()
    madd = build_merge_added()
    log(f"diamond M={diamond['M'][:7]} parents B={diamond['B'][:7]} D={diamond['D'][:7]}")
    for k, v in octopus.items():
        log(f"{k} M={v['M'][:7]} nparents={v['nparents']} parents={v['parents'][:40]} t1={v['t1_has']} t2={v['t2_has']}")
    log(f"mom M1={mom['M1'][:7]} M2={mom['M2'][:7]} X={mom['X'][:7]} C={mom['C'][:7]}")
    log(f"nested merges={[m[:7] for m in nested['merges']]} birth={nested['BIRTH'][:7]} tail={nested['TAIL'][:7]}")

    # ---- 1. now=FALSE at merge HEAD whose tree has the file ----
    header("1. now=FALSE at merge HEAD whose tree has the file (diamond)")
    for flag, name in (("", "diamond-all"), ("--any", "diamond-any"), ("--tree", "diamond-tree"), ("--boolean", "diamond-boolean")):
        args = ["-C", str(diamond["repo"]), "--json", "--human", "--color", "never"]
        if flag:
            args.append(flag)
        args += ["exists", "src/app.py"]
        r = save(name, run_tool(FORD, args))
        log(f"ford {flag or '--all'} rc={r['rc']}")
        log("    " + era_summary(r["json"]))
        if r["json"]:
            human = run_tool(FORD, ["-C", str(diamond["repo"]), "--human", "--color", "never"] + ([flag] if flag else []) + ["exists", "src/app.py"])
            (LOG / f"{name}.human").write_text(human["stdout"])
            log(textwrap.indent(human["stdout"].rstrip(), "    | "))

    # confirm HEAD tree has the file
    tree_has = subprocess.run(
        ["git", "-C", str(diamond["repo"]), "cat-file", "-e", "HEAD:src/app.py"]
    ).returncode == 0
    log(f"HEAD:src/app.py exists in tree? {tree_has}")
    log(f"ford --all exit={save('diamond-all', run_tool(FORD, ['-C', str(diamond['repo']), '--json', 'exists', 'src/app.py']))['rc']}  (1 = FALSE occupancy)")

    # ---- 2. octopus folds ----
    header("2. octopus folds (1-of-3 vs 2-of-3 is the same meet)")
    for name, meta in octopus.items():
        for flag, tag in (("", "all"), ("--any", "any")):
            args = ["-C", str(meta["repo"]), "--json", "--human", "--color", "never"]
            if flag:
                args.append(flag)
            args += ["exists", "src/app.py"]
            r = save(f"{name}-{tag}", run_tool(FORD, args))
            log(f"{name} {flag or '--all'} rc={r['rc']} nparents={meta['nparents']}")
            log("    " + era_summary(r["json"]))
            human = run_tool(FORD, ["-C", str(meta["repo"]), "--human", "--color", "never"] + ([flag] if flag else []) + ["exists", "src/app.py"])
            (LOG / f"{name}-{tag}.human").write_text(human["stdout"])
            log(textwrap.indent(human["stdout"].rstrip(), "    | "))
        # weir peel
        if WEIR.exists():
            r = save(f"{name}-weir-all", run_tool(WEIR, ["-C", str(meta["repo"]), "--json", "--human", "--color", "never", "exists", "src/app.py"]))
            log(f"  weir --all rc={r['rc']}  {era_summary(r['json'])}")

    # ---- 3. --boolean downcast ----
    header("3. --boolean downcast (UNKNOWN/SHALLOW/EMPTY → FALSE; skip horizon)")
    tm = tmerge["repo"]
    exec_cmd = ["exec", "--", "bash", "-c", "if test -f slow; then sleep 8; exit 0; else exit 0; fi"]
    r_all = save("timeout-all", run_tool(FORD, ["-C", str(tm), "--json", "--timeout", "0.2"] + exec_cmd))
    r_bool = save("timeout-boolean", run_tool(FORD, ["-C", str(tm), "--json", "--boolean", "--timeout", "0.2"] + exec_cmd))
    log(f"timeout-merge --all     rc={r_all['rc']}  {era_summary(r_all['json'])}")
    log(f"timeout-merge --boolean rc={r_bool['rc']}  {era_summary(r_bool['json'])}")
    human = run_tool(FORD, ["-C", str(tm), "--human", "--color", "never", "--timeout", "0.2"] + exec_cmd)
    (LOG / "timeout-all.human").write_text(human["stdout"])
    humanb = run_tool(FORD, ["-C", str(tm), "--human", "--color", "never", "--boolean", "--timeout", "0.2"] + exec_cmd)
    (LOG / "timeout-boolean.human").write_text(humanb["stdout"])
    log(textwrap.indent(human["stdout"].rstrip(), "    |all "))
    log(textwrap.indent(humanb["stdout"].rstrip(), "    |bool "))

    # weir --boolean refuse
    if WEIR.exists():
        r_w = save("timeout-weir-boolean", run_tool(WEIR, ["-C", str(tm), "--json", "--boolean", "--timeout", "0.2"] + exec_cmd))
        log(f"weir --boolean timeout rc={r_w['rc']} stderr={r_w['stderr'].strip()[:200]}")

    # binary EMPTY --boolean
    r_e = save("binary-all", run_tool(FORD, ["-C", str(binary["repo"]), "--json", "grep", "TOKEN_BIN"]))
    r_eb = save("binary-boolean", run_tool(FORD, ["-C", str(binary["repo"]), "--json", "--boolean", "grep", "TOKEN_BIN"]))
    log(f"binary --all     rc={r_e['rc']}  {era_summary(r_e['json'])}")
    log(f"binary --boolean rc={r_eb['rc']}  {era_summary(r_eb['json'])}")

    # ---- 4. kizu gold ----
    header("4. kizu gold SHAs — 0ea3916 / e1098c8 / 21ae074")
    kz_cmds = [
        ("kizu-all", []),
        ("kizu-any", ["--any"]),
        ("kizu-tree", ["--tree"]),
        ("kizu-boolean", ["--boolean"]),
        ("kizu-full", ["--full"]),
        ("kizu-full-tree-list", ["--full", "--tree", "--list"]),
    ]
    for name, flags in kz_cmds:
        r = save(name, run_tool(FORD, ["-C", str(KIZU), "--json", *flags, "exists", "CLAUDE.md"]))
        log(f"ford {' '.join(flags) or '--all'} rc={r['rc']}")
        log("    " + era_summary(r["json"]))
        if r["json"]:
            eras = r["json"]["eras"]
            for e in eras:
                start = (e.get("start") or {})
                log(f"      era {e['status']:8} kind={e['kind']:10} start={start.get('short')} {start.get('subject','')[:60]}")
                if e.get("join"):
                    log(f"           join {e['join']}")
                if e.get("origin"):
                    log(f"           origin {e['origin'].get('short')} {e['origin'].get('subject','')[:50]}")
                if e.get("continued_from"):
                    log(f"           continued_from {e['continued_from'].get('short')}")
        human = run_tool(FORD, ["-C", str(KIZU), "--human", "--color", "never", *flags, "exists", "CLAUDE.md"])
        (LOG / f"{name}.human").write_text(human["stdout"])
        if name in ("kizu-all", "kizu-boolean", "kizu-tree", "kizu-any"):
            log(textwrap.indent(human["stdout"].rstrip(), "    | "))

    if WEIR.exists():
        for name, flags in (("weir-kizu-all", []), ("weir-kizu-any", ["--any"]), ("weir-kizu-boolean", ["--boolean"])):
            r = save(name, run_tool(WEIR, ["-C", str(KIZU), "--json", *flags, "exists", "CLAUDE.md"]))
            log(f"weir {' '.join(flags) or '--all'} rc={r['rc']}")
            log("    " + era_summary(r["json"]))
            human = run_tool(WEIR, ["-C", str(KIZU), "--human", "--color", "never", *flags, "exists", "CLAUDE.md"])
            (LOG / f"{name}.human").write_text(human["stdout"])
            if name == "weir-kizu-all":
                log(textwrap.indent(human["stdout"].rstrip(), "    | "))

    # shallow --boolean
    kizu_sh = clone_shallow(KIZU, "kizu-shallow")
    r_sh = save("kizu-shallow-all", run_tool(FORD, ["-C", str(kizu_sh), "--json", "exists", "CLAUDE.md"]))
    r_shb = save("kizu-shallow-boolean", run_tool(FORD, ["-C", str(kizu_sh), "--json", "--boolean", "exists", "CLAUDE.md"]))
    log(f"kizu depth-1 --all     rc={r_sh['rc']}  {era_summary(r_sh['json'])}")
    log(f"kizu depth-1 --boolean rc={r_shb['rc']}  {era_summary(r_shb['json'])}")
    human = run_tool(FORD, ["-C", str(kizu_sh), "--human", "--color", "never", "--boolean", "exists", "CLAUDE.md"])
    (LOG / "kizu-shallow-boolean.human").write_text(human["stdout"])
    log(textwrap.indent(human["stdout"].rstrip(), "    | "))

    # ---- 5. merge-of-merges: parent trees not occupancy ----
    header("5. merge-of-merges — ford joins parent TREES (weir peel: occupancy)")
    r = save("mom-ford-all", run_tool(FORD, ["-C", str(mom["repo"]), "--json", "exists", "src/app.py"]))
    log(f"ford --all rc={r['rc']}  {era_summary(r['json'])}")
    human = run_tool(FORD, ["-C", str(mom["repo"]), "--human", "--color", "never", "exists", "src/app.py"])
    (LOG / "mom-ford-all.human").write_text(human["stdout"])
    log(textwrap.indent(human["stdout"].rstrip(), "    |ford "))
    if r["json"]:
        for e in r["json"]["eras"]:
            log(f"      {e['status']} kind={e['kind']} start={e['start']['short']} {e['start']['subject'][:50]} join={e.get('join')} tree={e.get('tree')}")
            if e.get("join_parents"):
                for pj in e["join_parents"]:
                    log(f"        parent {pj.get('short')}={pj.get('status')} {pj.get('subject','')[:40]}")
    if WEIR.exists():
        r = save("mom-weir-all", run_tool(WEIR, ["-C", str(mom["repo"]), "--json", "exists", "src/app.py"]))
        log(f"weir --all rc={r['rc']}  {era_summary(r['json'])}")
        human = run_tool(WEIR, ["-C", str(mom["repo"]), "--human", "--color", "never", "exists", "src/app.py"])
        (LOG / "mom-weir-all.human").write_text(human["stdout"])
        log(textwrap.indent(human["stdout"].rstrip(), "    |weir "))
        if r["json"]:
            for e in r["json"]["eras"]:
                log(f"      {e['status']} kind={e.get('kind')} start={e['start']['short']} {e['start']['subject'][:50]} join={e.get('join')} tree={e.get('tree')} reason={e.get('weir_reason') or e.get('reason')}")

    header("5b. nested merges cascade (kizu-shaped)")
    r = save("nested-ford-all", run_tool(FORD, ["-C", str(nested["repo"]), "--json", "exists", "src/app.py"]))
    log(f"ford --all rc={r['rc']}  {era_summary(r['json'])}")
    human = run_tool(FORD, ["-C", str(nested["repo"]), "--human", "--color", "never", "exists", "src/app.py"])
    (LOG / "nested-ford-all.human").write_text(human["stdout"])
    log(textwrap.indent(human["stdout"].rstrip(), "    |ford "))
    if WEIR.exists():
        r = save("nested-weir-all", run_tool(WEIR, ["-C", str(nested["repo"]), "--json", "exists", "src/app.py"]))
        log(f"weir --all rc={r['rc']}  {era_summary(r['json'])}")
        human = run_tool(WEIR, ["-C", str(nested["repo"]), "--human", "--color", "never", "exists", "src/app.py"])
        (LOG / "nested-weir-all.human").write_text(human["stdout"])
        log(textwrap.indent(human["stdout"].rstrip(), "    |weir "))

    # ---- 6. rename as path death ----
    header("6. rename is path death (berth's object, not this one)")
    for path, tag in (("old.txt", "old"), ("new name.txt", "new"), ("計画.md", "cjk")):
        r = save(f"rename-{tag}", run_tool(FORD, ["-C", str(rename["repo"]), "--json", "exists", path]))
        log(f"exists {path!r} rc={r['rc']}  {era_summary(r['json'])}")
        human = run_tool(FORD, ["-C", str(rename["repo"]), "--human", "--color", "never", "exists", path])
        (LOG / f"rename-{tag}.human").write_text(human["stdout"])
        log(textwrap.indent(human["stdout"].rstrip(), "    | "))
    r = save("rename-grep", run_tool(FORD, ["-C", str(rename["repo"]), "--json", "grep", "TOKEN_RENAME"]))
    log(f"grep TOKEN_RENAME rc={r['rc']}  {era_summary(r['json'])}")
    human = run_tool(FORD, ["-C", str(rename["repo"]), "--human", "--color", "never", "grep", "TOKEN_RENAME"])
    (LOG / "rename-grep.human").write_text(human["stdout"])
    log(textwrap.indent(human["stdout"].rstrip(), "    | "))

    # ---- 7. sitbone ----
    header("7. sitbone FocusRiverView — island, zero disagreeing merges")
    path = "Sources/SitboneUI/FocusRiverView.swift"
    r = save("sit-fp", run_tool(FORD, ["-C", str(SIT), "--json", "exists", path]))
    log(f"sitbone first-parent rc={r['rc']}  {era_summary(r['json'])}")
    human = run_tool(FORD, ["-C", str(SIT), "--human", "--color", "never", "exists", path])
    (LOG / "sit-fp.human").write_text(human["stdout"])
    log(textwrap.indent(human["stdout"].rstrip(), "    | "))
    r = save("sit-full", run_tool(FORD, ["-C", str(SIT), "--full", "--json", "exists", path]))
    log(f"sitbone --full rc={r['rc']}  {era_summary(r['json'])}")
    if r["json"]:
        for e in r["json"]["eras"]:
            if e["status"] == "TRUE" or e.get("kind") == "ford":
                log(f"      {e['status']} kind={e['kind']} n={e['count']} start={e['start']['short']} {e['start']['subject'][:50]} fords_in_era={e.get('is_ford')}")
    sit_sh = clone_shallow(SIT, "sitbone-shallow")
    r = save("sit-shallow", run_tool(FORD, ["-C", str(sit_sh), "--json", "exists", path]))
    r2 = save("sit-shallow-boolean", run_tool(FORD, ["-C", str(sit_sh), "--json", "--boolean", "exists", path]))
    log(f"sitbone depth-1 --all     rc={r['rc']}  {era_summary(r['json'])}")
    log(f"sitbone depth-1 --boolean rc={r2['rc']}  {era_summary(r2['json'])}")

    # ---- 8. merge-added + --boolean birth ----
    header("8. merge-added file is F⊓F with tree=TRUE; --boolean names the merge as birth")
    r = save("madd-all", run_tool(FORD, ["-C", str(madd["repo"]), "--json", "exists", "new.txt"]))
    r2 = save("madd-boolean", run_tool(FORD, ["-C", str(madd["repo"]), "--json", "--boolean", "exists", "new.txt"]))
    log(f"--all     rc={r['rc']}  {era_summary(r['json'])}")
    log(f"--boolean rc={r2['rc']}  {era_summary(r2['json'])}")
    human = run_tool(FORD, ["-C", str(madd["repo"]), "--human", "--color", "never", "exists", "new.txt"])
    (LOG / "madd-all.human").write_text(human["stdout"])
    log(textwrap.indent(human["stdout"].rstrip(), "    | "))

    # ---- 9. skills sanity (occupancy still lives) ----
    header("9. skills grep preact-zero-mock (survived occupancy; still TRUE)")
    if SKILLS.exists():
        r = save("skills-grep", run_tool(FORD, ["-C", str(SKILLS), "--json", "grep", "preact-zero-mock"]))
        log(f"grep rc={r['rc']}  {era_summary(r['json'])}")
    else:
        log("skip skills")

    # ---- 10. --boolean does not run the join ----
    header("10. --boolean never computes the lattice (apply_join skipped)")
    r = save("diamond-boolean-join", run_tool(FORD, ["-C", str(diamond["repo"]), "--json", "--boolean", "exists", "src/app.py"]))
    if r["json"]:
        fords = r["json"].get("fords")
        kinds = [e["kind"] for e in r["json"]["eras"]]
        joins = [e.get("join") for e in r["json"]["eras"]]
        log(f"fords={fords} kinds={kinds} joins={joins} now={r['json']['holds_now']} tree_now={r['json'].get('tree_now')}")
        log("  --boolean is held, not a downcast of the printed join")

    header("done")
    TRANS.write_text("\n".join(lines) + "\n")
    (ROOT / "shas.json").write_text(
        json.dumps(
            {
                "diamond": {k: v if not isinstance(v, Path) else str(v) for k, v in diamond.items()},
                "octopus": {
                    k: {kk: (str(vv) if isinstance(vv, Path) else vv) for kk, vv in meta.items()}
                    for k, meta in octopus.items()
                },
                "mom": {k: (str(v) if isinstance(v, Path) else v) for k, v in mom.items()},
                "nested": {k: (str(v) if isinstance(v, Path) else ([x for x in v] if k == "merges" else v)) for k, v in nested.items()},
            },
            indent=2,
        )
    )
    log(f"wrote {TRANS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
