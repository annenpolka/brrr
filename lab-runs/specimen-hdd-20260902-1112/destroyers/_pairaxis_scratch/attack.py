#!/usr/bin/env python3
"""Host-executed destroyer attacks against pairaxis. Isolated scratch only."""
from __future__ import annotations

import ast
import hashlib
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

RUN = Path("/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112")
CLI = RUN / "lineages/candidate-pairaxis/pairaxis"
FIX = RUN / "lineages/candidate-pairaxis/fixtures"
WT = Path("/Users/annenpolka/.grok/worktrees/annenpolka-brrr/pairaxis-pairaxis/pairaxis/pairaxis.py")
HERE = Path(__file__).resolve().parent
S017 = RUN / "specimens/specimen-017/files/pair_extras.py"
S072 = RUN / "specimens/specimen-072/files/run_orders_extra.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_cli(*args: str, stdin: bytes | None = None, timeout: float = 5.0):
    proc = subprocess.run(
        [sys.executable, str(CLI), *args],
        input=stdin,
        capture_output=True,
        timeout=timeout,
    )
    return proc.returncode, proc.stdout.decode("utf-8", "replace"), proc.stderr.decode("utf-8", "replace")


def parse_record(text: str) -> dict[str, str]:
    rec: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "\t" in line:
            key, _, rest = line.partition("\t")
            rec[key.strip()] = rest.strip()
            continue
        if "=" in line:
            key, _, rest = line.partition("=")
            rec[key.strip()] = rest.strip()
            continue
        parts = line.split()
        if len(parts) >= 2:
            rec[parts[0]] = " ".join(parts[1:])
    return rec


def maybe_literal(value: str):
    try:
        return ast.literal_eval(value)
    except Exception:
        return value


def replica(left_path: Path, right_path: Path) -> tuple[int, str, str]:
    if not left_path.is_file() or not right_path.is_file():
        missing = left_path if not left_path.is_file() else right_path
        return 2, "", f"pairaxis: file not found: {missing}\n"
    left = parse_record(left_path.read_text(encoding="utf-8"))
    right = parse_record(right_path.read_text(encoding="utf-8"))
    keys = sorted(set(left) | set(right))
    diffs = []
    for key in keys:
        lv = left.get(key, "<absent>")
        rv = right.get(key, "<absent>")
        if maybe_literal(lv) != maybe_literal(rv):
            diffs.append((key, lv, rv))
    lines = [
        f"left   {left_path}",
        f"right  {right_path}",
        f"fields {len(keys)}",
    ]
    if not diffs:
        lines.append("only_axis  none")
        lines.append("n_diff  0")
        return 0, "\n".join(lines) + "\n", ""
    lines.append(f"n_diff  {len(diffs)}")
    lines.append(f"only_axis  {diffs[0][0] if len(diffs) == 1 else 'multiple'}")
    for key, lv, rv in diffs:
        lines.append(f"diff  {key}  left={lv}  right={rv}")
    return 0, "\n".join(lines) + "\n", ""


def write_rec(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def cmp_cli_replica(label: str, left: Path, right: Path) -> dict:
    crc, cout, cerr = run_cli(str(left), str(right))
    rrc, rout, rerr = replica(left, right)
    return {
        "label": label,
        "cli_rc": crc,
        "rep_rc": rrc,
        "stdout_eq": cout == rout,
        "stderr_eq": cerr == rerr,
        "rc_eq": crc == rrc,
        "cli_out": cout,
        "cli_err": cerr,
        "rep_out": rout,
        "n_diff_row": next((ln for ln in cout.splitlines() if ln.startswith("n_diff")), ""),
        "only_axis_row": next((ln for ln in cout.splitlines() if ln.startswith("only_axis")), ""),
    }


def main() -> int:
    rows = []
    print("=== identity ===")
    print("python", sys.version.split()[0])
    print("cli_sha256", sha256(CLI), "bytes", CLI.stat().st_size)
    print("wt_sha256", sha256(WT) if WT.exists() else "MISSING", "bytes", WT.stat().st_size if WT.exists() else 0)
    print("archive_eq_worktree", CLI.read_bytes() == WT.read_bytes() if WT.exists() else False)
    parent = RUN.parent.parent
    ls = subprocess.run(["git", "ls-tree", "-r", "--name-only", "HEAD", "pairaxis"], cwd=str(parent), capture_output=True, text=True)
    print("parent_ls_tree_pairaxis", ls.stdout.strip() or "empty", "rc", ls.returncode)
    branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=str(parent), capture_output=True, text=True).stdout.strip()
    print("parent_branch", branch)
    wt_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(WT.parent.parent), capture_output=True, text=True).stdout.strip()
    wt_branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=str(WT.parent.parent), capture_output=True, text=True).stdout.strip()
    print("worktree_head", wt_head)
    print("worktree_branch", wt_branch)
    print("poetry", subprocess.run(["bash", "-lc", "command -v poetry || true"], capture_output=True, text=True).stdout.strip() or "empty")
    print("pytest_on_path", subprocess.run(["bash", "-lc", "command -v pytest || true"], capture_output=True, text=True).stdout.strip() or "empty")

    print("\n=== demo.sh ===")
    demo = subprocess.run(["bash", str(FIX.parent / "demo.sh")], capture_output=True, text=True)
    print("demo_rc", demo.returncode)
    print(demo.stdout)
    print("demo1_eq_demo2", (FIX.parent / "demo-1.log").read_bytes() == (FIX.parent / "demo-2.log").read_bytes())

    print("\n=== analog pair_extras.py ===")
    analog = subprocess.run([sys.executable, str(S017)], capture_output=True, text=True)
    print(analog.stdout)

    print("\n=== analog run_orders_extra.py ===")
    extra = subprocess.run([sys.executable, str(S072)], capture_output=True, text=True)
    print(extra.stdout)

    print("\n=== unix diff owned ===")
    d = subprocess.run(["diff", "-u", str(FIX / "pair_a.rec"), str(FIX / "pair_b.rec")], capture_output=True, text=True)
    print("diff_rc", d.returncode)
    print(d.stdout)

    print("\n=== unix comm owned ===")
    c = subprocess.run(
        ["bash", "-lc", f"comm -3 <(sort '{FIX / 'pair_a.rec'}') <(sort '{FIX / 'pair_b.rec'}')"],
        capture_output=True,
        text=True,
    )
    print(c.stdout)

    owned = [
        ("owned_pair", FIX / "pair_a.rec", FIX / "pair_b.rec"),
        ("unseen_pair", FIX / "unseen_a.rec", FIX / "unseen_b.rec"),
        ("identical", FIX / "pair_a.rec", FIX / "pair_a.rec"),
        ("unseen_identical", FIX / "unseen_a.rec", FIX / "unseen_a.rec"),
        ("swap_owned", FIX / "pair_b.rec", FIX / "pair_a.rec"),
    ]
    print("\n=== replica vs CLI owned ===")
    for label, a, b in owned:
        r = cmp_cli_replica(label, a, b)
        rows.append(r)
        print(f"{label} rc={r['cli_rc']} stdout_eq={r['stdout_eq']} rc_eq={r['rc_eq']} {r['n_diff_row']!r} {r['only_axis_row']!r}")
        if not r["stdout_eq"]:
            print("CLI\n", r["cli_out"])
            print("REP\n", r["rep_out"])

    scratch = HERE / "cases"
    scratch.mkdir(exist_ok=True)

    cases: list[tuple[str, Path, Path]] = []

    def add(label: str, left_text: str, right_text: str):
        lp = write_rec(scratch / f"{label}_l.rec", left_text)
        rp = write_rec(scratch / f"{label}_r.rec", right_text)
        cases.append((label, lp, rp))

    add("one_axis", "a\t1\nb\t2\n", "a\t1\nb\t9\n")
    add("three_axis", "a\t1\nb\t2\nc\t3\n", "a\t9\nb\t8\nc\t7\n")
    add("absent_right", "k\tv\n", "")
    add("absent_left", "", "k\tv\n")
    add("empty_empty", "", "")
    add("comments_only", "# x\n\n", "# y\n")
    add("list_quote_form", 'recognized\t["B"]\n', "recognized\t['B']\n")
    add("true_vs_True", "flag\ttrue\n", "flag\tTrue\n")
    add("one_vs_1.0", "n\t1\n", "n\t1.0\n")
    add("nan_vs_nan", "n\tnan\n", "n\tnan\n")
    add("key_named_none", "none\t1\n", "none\t2\n")
    add("key_named_multiple", "multiple\t1\n", "multiple\t2\n")
    add("dup_last_wins_same", "k\told\nk\tnew\n", "k\tnew\n")
    add("dup_last_wins_diff", "k\told\nk\tnew\n", "k\told\n")
    add("eq_form", "k=1\n", "k=2\n")
    add("space_form", "k 1\n", "k 2\n")
    add("mixed_forms_equal", "k\t1\n", "k=1\n")
    add("crlf", "k\t1\r\n", "k\t2\r\n")
    add("unicode", "箱\tα\n", "箱\tβ\n")
    add("order_keys", "b\t2\na\t1\n", "a\t1\nb\t2\n")
    add("trailing_ws_value", "k\t1 \n", "k\t1\n")
    add("empty_value", "k\t\n", "k\tx\n")
    add("hash_in_value", "k\tfoo#bar\n", "k\tfoo#bar\n")
    add("s072_shape", "acc\t[]\nflag\tFalse\norder\t('test_b', 'test_a')\ntest_b\tPASS\n", "acc\t['a']\nflag\tTrue\norder\t('test_a', 'test_b')\ntest_b\tFAIL\n")
    add("silentadd_cursor", "status\tok\ncollision\tx\ncursor\t1\n", "status\tok\ncollision\tx\ncursor\t2\n")
    add("huge_one_axis", "keep\t1\nbig\t" + ("A" * 20000) + "\n", "keep\t1\nbig\t" + ("B" * 20000) + "\n")
    add("nested_dict_str", "m\t{'a': 1}\n", 'm\t{"a": 1}\n')
    add("bool_false_vs_0", "x\tFalse\n", "x\t0\n")
    add("none_literal_vs_absent", "x\tNone\n", "")
    add("comment_then_key", "# ignore\nk\t1\n", "k\t1\n")
    add("tab_and_eq_same_key", "k\t1\nk=2\n", "k\t2\n")

    print("\n=== replica vs CLI adversarial ===")
    match = 0
    for label, a, b in cases:
        r = cmp_cli_replica(label, a, b)
        rows.append(r)
        ok = r["stdout_eq"] and r["rc_eq"]
        match += int(ok)
        print(f"{label} ok={ok} rc={r['cli_rc']} {r['n_diff_row']!r} {r['only_axis_row']!r}")
        if not ok:
            print("CLI\n", r["cli_out"][:500])
            print("REP\n", r["rep_out"][:500])
            print("CERR", r["cli_err"][:300])
            print("RERR", r["rep_err"] if False else r.get("cli_err"))
    print(f"adversarial_match {match}/{len(cases)}")

    print("\n=== error paths ===")
    for label, args in [
        ("missing", ["/no/such/pairaxis-left", str(FIX / "pair_a.rec")]),
        ("missing_right", [str(FIX / "pair_a.rec"), "/no/such/pairaxis-right"]),
        ("no_args", []),
        ("one_arg", [str(FIX / "pair_a.rec")]),
        ("dir_left", [str(FIX), str(FIX / "pair_a.rec")]),
        ("devnull", ["/dev/null", "/dev/null"]),
        ("dash", ["-", str(FIX / "pair_a.rec")]),
    ]:
        rc, out, err = run_cli(*args)
        print(f"{label} rc={rc} stdout_bytes={len(out.encode())} stderr={err.strip()[:120]!r} out={out.strip()[:80]!r}")

    print("\n=== stdin /dev/stdin ===")
    rc, out, err = run_cli("/dev/stdin", str(FIX / "pair_b.rec"), stdin=(FIX / "pair_a.rec").read_bytes())
    print("devstdin rc", rc)
    print(out)
    print("err", err.strip()[:200])

    print("\n=== symlink ===")
    sl = scratch / "link_a.rec"
    if sl.exists() or sl.is_symlink():
        sl.unlink()
    sl.symlink_to(FIX / "pair_a.rec")
    rc, out, err = run_cli(str(sl), str(FIX / "pair_b.rec"))
    print("symlink rc", rc)
    print(out.splitlines()[2:6])

    print("\n=== space in filename ===")
    sp = scratch / "pair a.rec"
    sp.write_bytes((FIX / "pair_a.rec").read_bytes())
    rc, out, err = run_cli(str(sp), str(FIX / "pair_b.rec"))
    print("space rc", rc, "n_diff", [ln for ln in out.splitlines() if ln.startswith("n_diff")])

    print("\n=== BOM ===")
    bom_l = write_rec(scratch / "bom_l.rec", "\ufeffk\t1\n")
    bom_r = write_rec(scratch / "bom_r.rec", "k\t1\n")
    rc, out, err = run_cli(str(bom_l), str(bom_r))
    print("bom rc", rc)
    print(out)
    print("err", err.strip()[:200])

    print("\n=== invalid utf8 ===")
    bad = scratch / "bad.rec"
    bad.write_bytes(b"k\t\xff\xfe\n")
    try:
        rc, out, err = run_cli(str(bad), str(FIX / "pair_a.rec"))
        print("utf8 rc", rc, "err", err.strip()[:200], "out", out[:80])
    except Exception as exc:
        print("utf8 exception", type(exc), exc)

    print("\n=== FIFO ===")
    fifo = scratch / "fifo.rec"
    if fifo.exists() or fifo.is_fifo():
        fifo.unlink()
    os.mkfifo(fifo)
    print("fifo_is_file", fifo.is_file(), "fifo_exists", fifo.exists(), "mode", oct(fifo.stat().st_mode))
    try:
        rc, out, err = run_cli(str(fifo), str(FIX / "pair_b.rec"))
        print("fifo rc", rc)
        print(out[:400])
        print("err", err.strip()[:200])
    except subprocess.TimeoutExpired:
        print("fifo TimeoutExpired (blocked on open/read)")
    fifo.unlink()

    print("\n=== does not run poetry/pytest ===")
    src = CLI.read_text(encoding="utf-8")
    for tok in ("poetry", "pytest", "django", "subprocess", "importlib", "runpy"):
        print(f"source_contains {tok}={tok in src}")

    print("\n=== one-liner dict-diff vs only_axis/n_diff ===")
    # independent of replica formatter: just the predicate
    thin_ok = 0
    thin_n = 0
    for label, a, b in owned + cases:
        crc, cout, _ = run_cli(str(a), str(b))
        if crc != 0:
            continue
        left = parse_record(a.read_text(encoding="utf-8"))
        right = parse_record(b.read_text(encoding="utf-8"))
        keys = sorted(set(left) | set(right))
        diffs = [k for k in keys if maybe_literal(left.get(k, "<absent>")) != maybe_literal(right.get(k, "<absent>"))]
        n_diff = len(diffs)
        only = "none" if n_diff == 0 else (diffs[0] if n_diff == 1 else "multiple")
        got_n = next((ln.split()[-1] for ln in cout.splitlines() if ln.startswith("n_diff")), None)
        got_o = None
        for ln in cout.splitlines():
            if ln.startswith("only_axis"):
                got_o = ln.split(None, 1)[1].strip()
        thin_n += 1
        if got_n == str(n_diff) and got_o == only:
            thin_ok += 1
        else:
            print("thin_miss", label, got_n, n_diff, got_o, only)
    print(f"thin_predicate {thin_ok}/{thin_n}")

    print("\n=== owned CLI stdout ===")
    for label, a, b in owned:
        rc, out, err = run_cli(str(a), str(b))
        print(f"--- {label} rc={rc} ---")
        print(out)

    # summary table
    n_eq = sum(1 for r in rows if r["stdout_eq"] and r["rc_eq"])
    print(f"\nREPLICA_SUMMARY {n_eq}/{len(rows)} byte-identical")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
