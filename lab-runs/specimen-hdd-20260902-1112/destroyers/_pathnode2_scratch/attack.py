#!/usr/bin/env python3
"""Host attacks on mutated pathnode. Does not import the CLI module."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path("/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112")
CLI = ROOT / "lineages/candidate-pathnode/pathnode"
FIX = ROOT / "lineages/candidate-pathnode/fixtures"
SCRATCH = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRATCH))
from replica import format_report  # noqa: E402

PY = sys.executable


def run_text(text: str, extra_args: list[str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PY, str(CLI), *(extra_args or [])],
        input=text,
        capture_output=True,
        text=True,
        check=False,
    )


def run_file(path: Path, extra_args: list[str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PY, str(CLI), str(path), *(extra_args or [])],
        capture_output=True,
        text=True,
        check=False,
    )


def banner(title: str) -> None:
    print(f"\n===== {title} =====")


def show(name: str, proc: subprocess.CompletedProcess, *, expect_stdout: str | None = None) -> None:
    print(f"-- {name} rc={proc.returncode}")
    if proc.stdout:
        sys.stdout.write(proc.stdout if proc.stdout.endswith("\n") else proc.stdout + "\n")
    if proc.stderr:
        sys.stdout.write("STDERR: " + proc.stderr)
    if expect_stdout is not None:
        ok = proc.stdout == expect_stdout
        print(f"replica_eq={ok}")
        if not ok:
            print("REPLICA:\n" + expect_stdout)
            print("CLI:\n" + proc.stdout)


def main() -> int:
    cases: list[tuple[str, str]] = []
    replica_ok = 0
    replica_fail = 0

    banner("OWNED 003")
    owned = (FIX / "003-collect.rec").read_text(encoding="utf-8")
    proc = run_file(FIX / "003-collect.rec")
    show("003-collect.rec", proc, expect_stdout=format_report(owned))

    banner("UNSEEN same-node twice")
    unseen = (FIX / "unseen-collect.rec").read_text(encoding="utf-8")
    proc = run_file(FIX / "unseen-collect.rec")
    show("unseen-collect.rec", proc, expect_stdout=format_report(unseen))

    # --- mutation claims / kill leftovers ---
    kill_rows: list[tuple[str, str, bool]] = []

    banner("KILL leftover (1): found lookup never registered")
    t = "collect\td\tn1\nlookup\tfx\tn1\tfound\n"
    proc = run_text(t)
    show("unbound-found", proc, expect_stdout=format_report(t))
    still_miss_none = proc.stdout.strip().splitlines()[-1] == "miss\tnone"
    has_unbound_yes = "unbound\tyes" in proc.stdout
    has_miss_row = proc.stdout.strip().splitlines()[-1].startswith("miss\tfx")
    print(f"still_miss_none={still_miss_none} has_miss_row={has_miss_row} unbound_yes={has_unbound_yes} rc={proc.returncode}")
    kill_rows.append(("1 found-never-registered still miss none", "still miss none (not unbound/miss)", still_miss_none))

    banner("KILL leftover (1b): harvest shape with found bit flipped")
    t = "collect\td\tn1\ncollect\td\tn3\nregister\tfx\tn1\nlookup\tfx\tn3\tfound\n"
    proc = run_text(t)
    show("found-on-later-node", proc, expect_stdout=format_report(t))
    still_miss_none = "miss\tnone" in proc.stdout.splitlines()
    print(f"flipped-found still_miss_none={still_miss_none} rc={proc.returncode}")

    banner("KILL leftover (2): two paths, one node id")
    t = "collect\ta\tn1\ncollect\tb\tn1\nregister\tfx\tn1\nlookup\tfx\tn1\tfound\n"
    proc = run_text(t)
    show("two-paths-one-node", proc, expect_stdout=format_report(t))
    dup_none = "dup_path\tnone" in proc.stdout.splitlines()
    shared_none = "shared_node\tnone" in proc.stdout.splitlines()
    has_shared = any(line.startswith("shared_node\tn1") for line in proc.stdout.splitlines())
    print(f"dup_path_none={dup_none} shared_node_none={shared_none} has_shared_n1={has_shared} rc={proc.returncode}")
    kill_rows.append(("2 two-paths-one-node still no shared_node", "still dup_path none / no shared_node", (not has_shared) or shared_none))

    banner("KILL leftover (7): miss still rc=0, no --check")
    t = owned
    proc = run_file(FIX / "003-collect.rec")
    print(f"owned miss rc={proc.returncode}")
    proc2 = subprocess.run([PY, str(CLI), "--check", str(FIX / "003-collect.rec")], capture_output=True, text=True)
    print(f"--check rc={proc2.returncode} stderr={proc2.stderr.strip()!r}")
    proc3 = run_text("collect\td\tn1\nlookup\tfx\tn1\tfound\n")
    print(f"unbound-found rc={proc3.returncode}")
    kill_rows.append(("7 miss still always rc=0 no --check", "miss rc=0 and --check unrecognized", proc.returncode == 0 and proc3.returncode == 0 and proc2.returncode == 2))

    banner("labeled-missing-but-bound (caller lie)")
    t = "collect\td\tn1\nregister\tfx\tn1\nlookup\tfx\tn1\tmissing\n"
    proc = run_text(t)
    show("caller-lie-missing-but-bound", proc, expect_stdout=format_report(t))
    print(f"still formatted as miss rc={proc.returncode}")

    banner("path identity ./dir1 vs dir1")
    t = "collect\tdir1\tn1\ncollect\t./dir1\tn3\nregister\tfx\tn1\nlookup\tfx\tn3\tmissing\n"
    proc = run_text(t)
    show("dir1-vs-dot-dir1", proc, expect_stdout=format_report(t))
    print(f"dup_path_none={('dup_path\\tnone' in proc.stdout.splitlines())}")

    banner("path identity dir1 vs dir1/")
    t = "collect\tdir1\tn1\ncollect\tdir1/\tn3\nregister\tfx\tn1\nlookup\tfx\tn3\tmissing\n"
    proc = run_text(t)
    show("dir1-vs-dir1-slash", proc, expect_stdout=format_report(t))

    banner("leading space path")
    t = "collect\t dir1\tn1\ncollect\tdir1\tn3\n"
    proc = run_text(t)
    show("leading-space", proc, expect_stdout=format_report(t))

    banner("n1 vs N1")
    t = "collect\tdir1\tn1\ncollect\tdir1\tN1\n"
    proc = run_text(t)
    show("n1-vs-N1", proc, expect_stdout=format_report(t))

    banner("empty tab fields slide")
    t = "collect\tdir1\t\tn99\n"
    proc = run_text(t)
    show("empty-node-then-n99", proc, expect_stdout=format_report(t))
    print(f"node became n99? {'nodes\\tn99' in proc.stdout} rc={proc.returncode}")

    t = "collect\tdir1\t\t\tn99\n"
    proc = run_text(t)
    show("double-empty-then-n99", proc, expect_stdout=format_report(t))

    t = "collect\tdir1\tn1\textra\n"
    proc = run_text(t)
    show("extra-collect-field", proc, expect_stdout=format_report(t))

    t = "collect\td\tn1\nlookup\tfx\tn1\tmissing\textra\n"
    proc = run_text(t)
    show("extra-lookup-field", proc, expect_stdout=format_report(t))

    banner("newline in path")
    t = "collect\tdir\n1\tn1\n"
    proc = run_text(t)
    show("newline-in-path", proc)

    banner("ghost register")
    t = "collect\td\tn1\nregister\tfx\tn99\nlookup\tfx\tn1\tmissing\n"
    proc = run_text(t)
    show("ghost-register", proc, expect_stdout=format_report(t))
    print(f"ghost rc={proc.returncode}")

    banner("ghost lookup never collected never registered")
    t = "collect\td\tn1\nlookup\tfx\tn3\tmissing\n"
    proc = run_text(t)
    show("ghost-lookup", proc, expect_stdout=format_report(t))

    banner("no register, lookup missing")
    t = "collect\td\tn1\nlookup\tfx\tn1\tmissing\n"
    proc = run_text(t)
    show("no-register-missing", proc, expect_stdout=format_report(t))

    banner("register no lookup")
    t = "collect\td\tn1\nregister\tfx\tn1\n"
    proc = run_text(t)
    show("register-no-lookup", proc, expect_stdout=format_report(t))

    banner("duplicate register fx on n1 then n3, lookup n3 missing")
    t = "collect\td\tn1\ncollect\td\tn3\nregister\tfx\tn1\nregister\tfx\tn3\nlookup\tfx\tn3\tmissing\n"
    proc = run_text(t)
    show("dup-register", proc, expect_stdout=format_report(t))

    banner("none-as-fixture")
    t = "collect\td\tn1\nlookup\tnone\tn1\tmissing\n"
    proc = run_text(t)
    show("fixture-named-none", proc, expect_stdout=format_report(t))

    banner("path named none, two nodes")
    t = "collect\tnone\tn1\ncollect\tnone\tn2\n"
    proc = run_text(t)
    show("path-named-none", proc, expect_stdout=format_report(t))

    banner("harvest without lookup missing row (only n1 found)")
    t = "collect\tdir1\tn1\ncollect\tdir2\tn2\ncollect\tdir1\tn3\nregister\tshared_fixture\tn1\nlookup\tshared_fixture\tn1\tfound\n"
    proc = run_text(t)
    show("harvest-without-n3-lookup", proc, expect_stdout=format_report(t))
    print("If miss none here, harvest miss still requires caller lookup on n3")

    banner("NUL in path")
    t = "collect\td\x00x\tn1\ncollect\td\tn3\n"
    proc = run_text(t)
    show("nul-in-path", proc, expect_stdout=format_report(t))

    banner("YES/true/FALSE/miss/maybe")
    for token in ("YES", "true", "FALSE", "miss", "maybe", "Found", "MISSING"):
        t = f"collect\td\tn1\nregister\tfx\tn1\nlookup\tfx\tn1\t{token}\n"
        proc = run_text(t)
        print(f"token={token!r} rc={proc.returncode} last={proc.stdout.strip().splitlines()[-1] if proc.stdout else proc.stderr.strip()}")

    banner("BOM")
    t = "\ufeffcollect\td\tn1\n"
    proc = run_text(t)
    show("utf8-bom", proc)

    banner("CRLF")
    t = "collect\td\tn1\r\nregister\tfx\tn1\r\nlookup\tfx\tn1\tfound\r\n"
    proc = run_text(t)
    show("crlf", proc, expect_stdout=format_report(t))

    banner("comments and blanks")
    t = "# hi\n\ncollect\td\tn1\n"
    proc = run_text(t)
    show("comments", proc, expect_stdout=format_report(t))

    banner("empty stdin /dev/null")
    proc = run_file(Path("/dev/null"))
    show("dev-null", proc)

    banner("missing path")
    proc = run_file(Path("/no/such/pathnode.rec"))
    show("missing-file", proc)

    banner("directory as record")
    proc = run_file(FIX)
    show("directory", proc)

    banner("two positional")
    proc = subprocess.run([PY, str(CLI), "a", "b"], capture_output=True, text=True)
    show("two-args", proc)

    banner("JSON object")
    proc = run_text('{"collect":"dir1"}\n')
    show("json", proc)

    banner("dash as RECORD")
    proc = subprocess.run([PY, str(CLI), "-"], capture_output=True, text=True)
    show("dash-record", proc)

    banner("spaces in path / unicode")
    t = "collect\tmy dir\tn1\ncollect\tテスト\tn2\n"
    proc = run_text(t)
    show("space-and-unicode", proc, expect_stdout=format_report(t))

    banner("FIFO")
    with tempfile.TemporaryDirectory() as td:
        fifo = Path(td) / "f.rec"
        os.mkfifo(fifo)
        text = "collect\td\tn1\nregister\tfx\tn1\nlookup\tfx\tn1\tfound\n"

        def writer() -> None:
            fifo.write_text(text, encoding="utf-8")

        import threading

        th = threading.Thread(target=writer)
        th.start()
        proc = run_file(fifo)
        th.join()
        show("fifo", proc, expect_stdout=format_report(text))

    banner("symlink")
    with tempfile.TemporaryDirectory() as td:
        real = Path(td) / "real.rec"
        link = Path(td) / "link.rec"
        real.write_text("collect\td\tn1\n", encoding="utf-8")
        link.symlink_to(real)
        proc = run_file(link)
        show("symlink", proc, expect_stdout=format_report("collect\td\tn1\n"))

    banner("filename with space")
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "my rec.rec"
        p.write_text("collect\td\tn1\n", encoding="utf-8")
        proc = run_file(p)
        show("space-filename", proc, expect_stdout=format_report("collect\td\tn1\n"))

    banner("process substitution equivalent (python pipe)")
    proc = run_text("collect\td\tn1\n")
    show("stdin", proc, expect_stdout=format_report("collect\td\tn1\n"))

    banner("three collects dir1 as n1 n2 n3")
    t = "collect\tdir1\tn1\ncollect\tdir1\tn2\ncollect\tdir1\tn3\n"
    proc = run_text(t)
    show("three-nodes", proc, expect_stdout=format_report(t))

    banner("crossed fixtures")
    t = (
        "collect\ta\tn1\ncollect\tb\tn3\n"
        "register\tfx\tn1\nregister\tother\tn3\n"
        "lookup\tfx\tn3\tmissing\nlookup\tother\tn1\tmissing\n"
    )
    proc = run_text(t)
    show("crossed", proc, expect_stdout=format_report(t))

    banner("duplicate register same node uniqued")
    t = "collect\td\tn1\nregister\tfx\tn1\nregister\tfx\tn1\nlookup\tfx\tn1\tmissing\n"
    proc = run_text(t)
    show("dup-register-same-node", proc, expect_stdout=format_report(t))

    banner("shared_node plus dup_path together")
    t = "collect\ta\tn1\ncollect\tb\tn1\ncollect\ta\tn2\n"
    proc = run_text(t)
    show("shared-and-dup", proc, expect_stdout=format_report(t))

    banner("2000-char not needed; modest huge path")
    huge = "p" * 2000
    t = f"collect\t{huge}\tn1\ncollect\t{huge}\tn3\n"
    proc = run_text(t)
    print(f"huge-path rc={proc.returncode} stdout_bytes={len(proc.stdout)} has_dup={'dup_path' in proc.stdout}")
    try:
        replica = format_report(t)
        print(f"huge replica_eq={proc.stdout == replica}")
        if proc.stdout == replica:
            replica_ok += 1
        else:
            replica_fail += 1
    except Exception as err:
        print(f"huge replica error {err}")
        replica_fail += 1

    # replica tally from logged cases: re-run a grid
    banner("REPLICA GRID")
    grid = [
        ("003", owned),
        ("unseen", unseen),
        ("unbound-found", "collect\td\tn1\nlookup\tfx\tn1\tfound\n"),
        ("flip-found", "collect\td\tn1\ncollect\td\tn3\nregister\tfx\tn1\nlookup\tfx\tn3\tfound\n"),
        ("two-paths", "collect\ta\tn1\ncollect\tb\tn1\nregister\tfx\tn1\nlookup\tfx\tn1\tfound\n"),
        ("lie", "collect\td\tn1\nregister\tfx\tn1\nlookup\tfx\tn1\tmissing\n"),
        ("dot", "collect\tdir1\tn1\ncollect\t./dir1\tn3\nregister\tfx\tn1\nlookup\tfx\tn3\tmissing\n"),
        ("slash", "collect\tdir1\tn1\ncollect\tdir1/\tn3\nregister\tfx\tn1\nlookup\tfx\tn3\tmissing\n"),
        ("empty-tab", "collect\tdir1\t\tn99\n"),
        ("ghost-reg", "collect\td\tn1\nregister\tfx\tn99\nlookup\tfx\tn1\tmissing\n"),
        ("ghost-lu", "collect\td\tn1\nlookup\tfx\tn3\tmissing\n"),
        ("none-fx", "collect\td\tn1\nlookup\tnone\tn1\tmissing\n"),
        ("none-path", "collect\tnone\tn1\ncollect\tnone\tn2\n"),
        ("no-lu", "collect\td\tn1\nregister\tfx\tn1\n"),
        ("harvest-no-n3", "collect\tdir1\tn1\ncollect\tdir2\tn2\ncollect\tdir1\tn3\nregister\tshared_fixture\tn1\nlookup\tshared_fixture\tn1\tfound\n"),
        ("single", "collect\tonly\tn1\nregister\tfx\tn1\nlookup\tfx\tn1\tfound\n"),
        ("space", "collect\tmy dir\tn1\n"),
        ("jp", "collect\tテスト\tn1\n"),
        ("three", "collect\tdir1\tn1\ncollect\tdir1\tn2\ncollect\tdir1\tn3\n"),
        ("crossed", "collect\ta\tn1\ncollect\tb\tn3\nregister\tfx\tn1\nregister\tother\tn3\nlookup\tfx\tn3\tmissing\nlookup\tother\tn1\tmissing\n"),
        ("dup-reg", "collect\td\tn1\ncollect\td\tn3\nregister\tfx\tn1\nregister\tfx\tn3\nlookup\tfx\tn3\tmissing\n"),
        ("same-reg", "collect\td\tn1\nregister\tfx\tn1\nregister\tfx\tn1\nlookup\tfx\tn1\tmissing\n"),
        ("shared-dup", "collect\ta\tn1\ncollect\tb\tn1\ncollect\ta\tn2\n"),
        ("crlf", "collect\td\tn1\r\nregister\tfx\tn1\r\nlookup\tfx\tn1\tfound\r\n"),
        ("comment", "# hi\n\ncollect\td\tn1\n"),
        ("lead-space", "collect\t dir1\tn1\ncollect\tdir1\tn3\n"),
        ("case-node", "collect\tdir1\tn1\ncollect\tdir1\tN1\n"),
        ("extra-col", "collect\tdir1\tn1\textra\n"),
        ("extra-lu", "collect\td\tn1\nlookup\tfx\tn1\tmissing\textra\n"),
        ("nul", "collect\td\x00x\tn1\ncollect\td\tn3\n"),
        ("double-empty", "collect\tdir1\t\t\tn99\n"),
        ("yes-token", "collect\td\tn1\nregister\tfx\tn1\nlookup\tfx\tn1\tYES\n"),
        ("false-token", "collect\td\tn1\nregister\tfx\tn1\nlookup\tfx\tn1\tFALSE\n"),
        ("unbound-missing", "collect\td\tn1\nlookup\tfx\tn1\tmissing\n"),
        ("found-bound", "collect\td\tn1\nregister\tfx\tn1\nlookup\tfx\tn1\tfound\n"),
        ("two-fx-one-node", "collect\td\tn1\nregister\ta\tn1\nregister\tb\tn1\nlookup\ta\tn1\tfound\nlookup\tb\tn1\tfound\n"),
        ("unbound-other-fx", "collect\td\tn1\nregister\ta\tn1\nlookup\tb\tn1\tfound\n"),
        ("same-path-same-node", "collect\td\tn1\ncollect\td\tn1\n"),
        ("shared-three-paths", "collect\ta\tn1\ncollect\tb\tn1\ncollect\tc\tn1\n"),
        ("register-order", "collect\td\tn3\ncollect\td\tn1\nregister\tfx\tn3\nregister\tfx\tn1\nlookup\tfx\tn1\tmissing\n"),
    ]
    for name, text in grid:
        proc = run_text(text)
        try:
            replica = format_report(text)
            eq = proc.stdout == replica and proc.returncode == 0
        except Exception:
            replica = None
            eq = False
        if eq:
            replica_ok += 1
            print(f"GRID {name}: stdout_eq=True rc_eq=True rc={proc.returncode}")
        else:
            replica_fail += 1
            print(f"GRID {name}: FAIL rc={proc.returncode} replica_exc={replica is None}")
            if replica is not None and proc.stdout != replica:
                print(" CLI:", repr(proc.stdout[:200]))
                print(" REP:", repr(replica[:200]))

    banner("ERROR GRID (replica should also fail parse; CLI rc=1)")
    err_grid = [
        ("empty", ""),
        ("json", '{"x":1}\n'),
        ("incomplete-collect", "collect\tdir1\n"),
        ("incomplete-lookup", "collect\td\tn1\nlookup\tfx\tn1\n"),
        ("maybe", "collect\td\tn1\nlookup\tfx\tn1\tmaybe\n"),
        ("unknown", "foo\tbar\n"),
        ("no-tab", "collect dir1 n1\n"),
        ("hash-only", "#collect\td\tn1\n"),
        ("register-only", "register\tfx\tn1\n"),
    ]
    err_ok = 0
    for name, text in err_grid:
        proc = run_text(text)
        replica_err = False
        try:
            format_report(text)
        except Exception:
            replica_err = True
        cli_err = proc.returncode != 0
        match = replica_err and cli_err
        if match:
            err_ok += 1
        print(f"ERR {name}: cli_rc={proc.returncode} replica_raises={replica_err} match={match}")

    banner("HONOR-KILL CHECKLIST")
    for item, meaning, still in kill_rows:
        print(f"{item}: still={still}  ({meaning})")

    print(f"\nreplica_grid_ok={replica_ok} replica_grid_fail={replica_fail} err_grid_match={err_ok}/{len(err_grid)}")
    print("DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
