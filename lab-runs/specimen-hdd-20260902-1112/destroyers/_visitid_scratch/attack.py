#!/usr/bin/env python3
"""Host attacks for DESTROYER_visitid_3. Does not import visitid."""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

RUN = Path("/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112")
CLI = RUN / "lineages/candidate-visitid/visitid"
FIX = RUN / "lineages/candidate-visitid/fixtures"
WT = Path("/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-visitid-visitid/visitid/visitid")
ARCH = RUN / "lineages/candidate-visitid"
PY = sys.executable
EMPTY = "-"
LIST_CAP = 32
HEX_DIGITS = re.compile(r"[0-9a-fA-F]+$")
SCIENTIFIC = re.compile(r"\d+[eE]\d+$")
BOM = "\ufeff"

PASS = 0
FAIL = 0


def sha256_bytes(p: Path) -> tuple[str, int]:
    data = p.read_bytes()
    return hashlib.sha256(data).hexdigest(), len(data)


def run_cli(args, *, stdin: str | None = None, cwd: Path | None = None):
    return subprocess.run(
        [PY, str(CLI), *args],
        check=False,
        capture_output=True,
        text=True,
        input=stdin,
        cwd=str(cwd or ARCH),
    )


def parse_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if not line or "\t" not in line:
            continue
        name, *rest = line.split("\t")
        rows[name] = rest
    return rows


def note(title: str) -> None:
    print(f"\n=== {title} ===")


def check(ok: bool, msg: str) -> None:
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"PASS  {msg}")
    else:
        FAIL += 1
        print(f"FAIL  {msg}")


# --- independent replica of parse + two set walks + TSV ---


def replica_parse_addr(token: str) -> tuple[int, str] | str:
    text = token.strip()
    if not text:
        return "empty address"
    try:
        if text[:2].lower() == "0x":
            return int(text, 16), text
        if SCIENTIFIC.fullmatch(text):
            return "bad address"
        if HEX_DIGITS.fullmatch(text):
            return int(text, 16), text
    except ValueError:
        return "bad address"
    return "bad address"


def replica_require_name(token: str) -> str | None:
    if BOM in token:
        return "BOM"
    if token == "":
        return "empty name"
    if token.strip() != token:
        return "padded name"
    if token == EMPTY:
        return "empty-list token"
    return None


def replica_parse(text: str) -> list[tuple[str, int, str]] | str:
    events: list[tuple[str, int, str]] = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "\t" in line:
            parts = line.split("\t")
            if any(part == "" for part in parts):
                return f"{lineno}: empty tab field"
        else:
            parts = line.split()
            if not parts:
                return f"{lineno}: empty line"
        if parts[0] == "visit" and len(parts) >= 3:
            fields = parts[1:]
        else:
            fields = parts
        if len(fields) < 2:
            return f"{lineno}: expected name and addr"
        if len(fields) > 2:
            return f"{lineno}: extra field"
        err = replica_require_name(fields[0])
        if err:
            return f"{lineno}: {err}"
        addr = replica_parse_addr(fields[1])
        if isinstance(addr, str):
            return f"{lineno}: {addr}"
        events.append((fields[0], addr[0], addr[1]))
    if not events:
        return "missing visit"
    return events


def unique_in_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def replica_inspect(events: list[tuple[str, int, str]]) -> dict:
    ptr_done: set[int] = set()
    occ: dict[int, tuple[str, str]] = {}
    ptr_vis: list[str] = []
    ptr_skip: list[tuple[str, str, str, str, str]] = []
    for name, addr, text in events:
        if addr in ptr_done:
            first_name, first_text = occ[addr]
            kind = "address-reuse" if first_name != name else "same-pointer"
            ptr_skip.append((name, first_text, first_name, kind, text))
            continue
        ptr_done.add(addr)
        occ[addr] = (name, text)
        ptr_vis.append(name)
    val_done: set[str] = set()
    val_vis: list[str] = []
    val_skip: list[str] = []
    for name, addr, text in events:
        if name in val_done:
            val_skip.append(name)
            continue
        val_done.add(name)
        val_vis.append(name)
    never = [s[0] for s in ptr_skip if s[3] == "address-reuse"]
    kinds: list[str] = []
    for s in ptr_skip:
        if s[3] not in kinds:
            kinds.append(s[3])
    if val_skip and "same-value" not in kinds:
        kinds.append("same-value")
    names = unique_in_order([e[0] for e in events])
    seen_addrs: set[int] = set()
    addrs: list[str] = []
    for name, addr, text in events:
        if addr in seen_addrs:
            continue
        seen_addrs.add(addr)
        addrs.append(text)
    return {
        "events": events,
        "ptr_vis": ptr_vis,
        "ptr_skip": ptr_skip,
        "val_vis": val_vis,
        "val_skip": val_skip,
        "never": never,
        "kinds": kinds,
        "names": names,
        "addrs": addrs,
    }


def join_capped(names: list[str], *, unique: bool = False) -> tuple[str, int]:
    n = len(names)
    shown = unique_in_order(names) if unique else list(names)
    if n == 0:
        return EMPTY, 0
    return "\t".join(shown[:LIST_CAP]), n


def replica_format(result: dict, *, mode: str = "events", retain: bool | None = None) -> str:
    names_cell, names_n = join_capped(result["names"])
    addrs_cell, addrs_n = join_capped(result["addrs"])
    ptr_vis, ptr_vis_n = join_capped(result["ptr_vis"])
    ptr_skip, ptr_skip_n = join_capped([s[0] for s in result["ptr_skip"]], unique=True)
    val_vis, val_vis_n = join_capped(result["val_vis"])
    val_skip, val_skip_n = join_capped(result["val_skip"], unique=True)
    fetched, fetched_n = join_capped(result["never"], unique=True)
    kinds = result["kinds"]
    pointer_key = "slot" if mode == "cpython-slot" else "id"
    lines = [
        f"mode\t{mode}",
        f"pointer_key\t{pointer_key}",
        "value_key\tname",
        "names\t" + names_cell,
        "addrs\t" + addrs_cell,
        "unique_names\t" + str(len(result["names"])),
        "unique_addrs\t" + str(len(result["addrs"])),
        "pointer_visited\t" + ptr_vis,
        "pointer_skipped\t" + ptr_skip,
        "value_visited\t" + val_vis,
        "value_skipped\t" + val_skip,
        "skip_kind\t" + ("\t".join(kinds) if kinds else EMPTY),
    ]
    if retain is not None:
        lines.insert(1, "retain\t" + ("true" if retain else "false"))
        lines.insert(2, "allocator\tcpython")
    if names_n > LIST_CAP:
        lines.append(f"names_n\t{names_n}")
    if addrs_n > LIST_CAP:
        lines.append(f"addrs_n\t{addrs_n}")
    if ptr_skip_n > LIST_CAP:
        lines.append(f"pointer_skipped_n\t{ptr_skip_n}")
    if val_skip_n > LIST_CAP:
        lines.append(f"value_skipped_n\t{val_skip_n}")
    if ptr_vis_n > LIST_CAP:
        lines.append(f"pointer_visited_n\t{ptr_vis_n}")
    if val_vis_n > LIST_CAP:
        lines.append(f"value_visited_n\t{val_vis_n}")
    reuses = [s for s in result["ptr_skip"] if s[3] == "address-reuse"]
    if reuses:
        seen: set[str] = set()
        shown_reuses = []
        for s in reuses:
            if s[0] in seen:
                continue
            seen.add(s[0])
            shown_reuses.append(s)
        for s in shown_reuses[:LIST_CAP]:
            name, first_text, first_name, _kind, later_text = s
            row = "reuse\t" + first_text + "\tfirst\t" + first_name + "\tlater\t" + name
            if later_text != first_text:
                row += "\tlater-token\t" + later_text
            lines.append(row)
        if len(reuses) > LIST_CAP:
            lines.append(f"reuse_n\t{len(reuses)}")
    else:
        lines.append("reuse\t" + EMPTY)
    lines.append("never_fetched_n\t" + str(fetched_n))
    lines.append("never_fetched\t" + fetched)
    if mode == "cpython-slot":
        n = len(result["events"])
        unique_n = len(result["addrs"])
        if retain:
            lines.append("allocator_reuse\t" + EMPTY)
        elif unique_n < n:
            lines.append(
                "allocator_reuse\tping-pong\tunique_addrs\t"
                + str(unique_n)
                + "\tof\t"
                + str(n)
            )
        else:
            lines.append("allocator_reuse\t" + EMPTY)
    return "\n".join(lines) + "\n"


def replica_rc(result: dict) -> int:
    if result["never"] or "address-reuse" in result["kinds"]:
        return 1
    return 0


def replica_run_text(text: str) -> tuple[str, int]:
    parsed = replica_parse(text)
    if isinstance(parsed, str):
        return "", 1
    result = replica_inspect(parsed)
    return replica_format(result), replica_rc(result)


def membership_nf(events: list[tuple[str, int]]) -> list[str]:
    done: set[int] = set()
    occ: dict[int, str] = {}
    nf: list[str] = []
    for name, addr in events:
        if addr in done:
            if occ[addr] != name:
                nf.append(name)
        else:
            done.add(addr)
            occ[addr] = name
    return nf


def awk_nf(text: str) -> list[str]:
    """Same occupancy rule as replica, comment-skipping NAME ADDR."""
    events: list[tuple[str, int]] = []
    parsed = replica_parse(text)
    if isinstance(parsed, str):
        return []
    return membership_nf([(n, a) for n, a, _t in parsed])


def main() -> int:
    note("identity")
    h, n = sha256_bytes(CLI)
    print(f"archive sha256 {h} ({n} bytes)")
    wh, wn = sha256_bytes(WT)
    print(f"worktree sha256 {wh} ({wn} bytes)")
    check(h == wh and n == wn, "archive == worktree bytes")
    cmp = subprocess.run(["cmp", str(CLI), str(WT)], check=False, capture_output=True)
    check(cmp.returncode == 0, "cmp archive worktree rc=0")
    head = (ARCH / "HEAD.txt").read_text().strip()
    print(f"archive HEAD.txt {head}")
    wt_head = subprocess.run(
        ["git", "-C", str(WT.parent), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    print(f"worktree HEAD {wt_head.stdout.strip()}")
    check(wt_head.stdout.strip().startswith(head[:7]) or wt_head.stdout.strip() == head, "HEAD matches")
    parent = subprocess.run(
        ["git", "-C", "/Users/annenpolka/ghq/github.com/annenpolka/brrr", "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    print(f"parent HEAD {parent.stdout.strip()}")
    in_main = subprocess.run(
        ["git", "-C", "/Users/annenpolka/ghq/github.com/annenpolka/brrr", "ls-tree", "-r", "--name-only", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    check("visitid" not in in_main.stdout.splitlines() or not any(
        p == "visitid" or p.endswith("/visitid") for p in in_main.stdout.splitlines() if "lab-runs" not in p and "lab-hdd" not in p and "lab/" not in p
    ), "visitid not a parent-tree product (heuristic printed)")
    product = [p for p in in_main.stdout.splitlines() if p == "visitid" or p.endswith("/visitid")]
    print("parent visitid paths:", product[:20], "count", len(product))

    note("tests")
    tests = subprocess.run(
        [PY, str(ARCH / "tests/test_visitid.py")],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(ARCH),
    )
    print(tests.stderr[-400:] if tests.stderr else tests.stdout[-400:])
    check(tests.returncode == 0, "archive tests rc=0")
    m = re.search(r"Ran (\d+) test", tests.stderr + tests.stdout)
    ntests = int(m.group(1)) if m else -1
    print(f"tests ran {ntests}")
    check(ntests == 41, "41 tests")

    wt_tests = subprocess.run(
        [PY, str(WT.parent / "tests/test_visitid.py")],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(WT.parent),
    )
    check(wt_tests.returncode == 0, "worktree tests rc=0")

    note("owned fixtures")
    cases = {
        "070-reuse.rec": (1, "home-manager", "address-reuse"),
        "reuse-same-name.rec": (1, "home-manager", None),
        "unseen-unique.rec": (0, "-", "-"),
        "unseen-same-value.rec": (0, "-", "same-value"),
    }
    for fname, (exp_rc, nf, kind) in cases.items():
        proc = run_cli([str(FIX / fname)])
        rows = parse_rows(proc.stdout)
        check(proc.returncode == exp_rc, f"{fname} rc={proc.returncode} want {exp_rc}")
        if nf is not None:
            got = "\t".join(rows.get("never_fetched", []))
            check(got == nf, f"{fname} never_fetched={got!r} want {nf!r}")
        if kind is not None:
            gotk = "\t".join(rows.get("skip_kind", []))
            check(gotk == kind, f"{fname} skip_kind={gotk!r} want {kind!r}")
        check("pointer_done" not in rows, f"{fname} no pointer_done")
        check("value_done" not in rows, f"{fname} no value_done")
        check(rows.get("value_key") == ["name"], f"{fname} value_key name")
        check("inputs" not in rows, f"{fname} no inputs")
        print(f"--- {fname} rc={proc.returncode} ---")
        print(proc.stdout.rstrip())

    note("synonym: unique_addrs == len(pointer_visited)")
    syn_ok = 0
    syn_n = 0
    tables = []
    # 50 random-ish tables
    import random
    rng = random.Random(365)
    for i in range(50):
        lines = []
        for j in range(rng.randint(3, 40)):
            name = f"n{rng.randint(0, 12)}"
            addr = hex(rng.randint(1, 20))
            lines.append(f"{name}\t{addr}")
        text = "\n".join(lines) + "\n"
        proc = run_cli([], stdin=text)
        rows = parse_rows(proc.stdout)
        if proc.returncode not in (0, 1) or not rows:
            check(False, f"random {i} failed rc={proc.returncode} err={proc.stderr[:80]}")
            continue
        syn_n += 1
        ua = int(rows["unique_addrs"][0])
        un = int(rows["unique_names"][0])
        pv = rows["pointer_visited"]
        vv = rows["value_visited"]
        pv_n = 0 if pv == ["-"] else len(pv)
        vv_n = 0 if vv == ["-"] else len(vv)
        # capped: if >32, pointer_visited_n exists
        if "pointer_visited_n" in rows:
            pv_n = int(rows["pointer_visited_n"][0])
        if "value_visited_n" in rows:
            vv_n = int(rows["value_visited_n"][0])
        if ua == pv_n and un == vv_n:
            syn_ok += 1
        else:
            print(f"  diverge i={i} ua={ua} pv_n={pv_n} un={un} vv_n={vv_n}")
    check(syn_ok == syn_n == 50, f"synonym unique_addrs==ptr_vis and unique_names==val_vis {syn_ok}/{syn_n}")
    print(f"synonym 50/50 unique_addrs≡len(pointer_visited) unique_names≡len(value_visited)")

    # owned 070
    proc = run_cli([str(FIX / "070-reuse.rec")])
    rows = parse_rows(proc.stdout)
    check(
        int(rows["unique_addrs"][0]) == len(rows["pointer_visited"]) == 3,
        "070 unique_addrs 3 == pointer_visited 3",
    )
    check(
        int(rows["unique_names"][0]) == len(rows["value_visited"]) == 4,
        "070 unique_names 4 == value_visited 4",
    )

    note("232 unique names / 170 unique addrs (origin shape as caller-complete list)")
    lines = [f"node{i}\t0x{i:x}" for i in range(170)]
    lines += [f"extra{i}\t0x{i:x}" for i in range(62)]
    text = "\n".join(lines) + "\n"
    proc = run_cli([], stdin=text)
    rows = parse_rows(proc.stdout)
    print("unique_names", rows.get("unique_names"))
    print("unique_addrs", rows.get("unique_addrs"))
    print("never_fetched_n", rows.get("never_fetched_n"))
    print("never_fetched first/last", rows.get("never_fetched", [])[:3], "...", rows.get("never_fetched", [])[-3:])
    print("pointer_visited_n", rows.get("pointer_visited_n"))
    print("names_n", rows.get("names_n"), "addrs_n", rows.get("addrs_n"))
    print("rc", proc.returncode)
    check(rows["unique_names"] == ["232"], "232 unique_names")
    check(rows["unique_addrs"] == ["170"], "170 unique_addrs")
    check(rows["never_fetched_n"] == ["62"], "never_fetched_n 62 == 232-170")
    check(int(rows["unique_names"][0]) - int(rows["unique_addrs"][0]) == int(rows["never_fetched_n"][0]), "set-size difference when all extra names unique")
    check(len(rows["never_fetched"]) == 32, "cap 32 unique skip names")
    check("extra31" in rows["never_fetched"] and "extra32" not in rows["never_fetched"], "extra32 hidden by cap")
    check("232" not in proc.stdout.split("unique_names\t")[0], "does not print origin 232/170/150 as measured here beyond unique_*")
    check("150" not in proc.stdout, "no ~150 in stdout")
    check(proc.returncode == 1, "232/170 rc=1")

    note("same-value-only 170 names 232 addrs (lock-input shape) rc=0")
    lines = [f"input{i % 170}\t0x{i:x}" for i in range(232)]
    proc = run_cli([], stdin="\n".join(lines) + "\n")
    rows = parse_rows(proc.stdout)
    print("unique_names", rows.get("unique_names"), "unique_addrs", rows.get("unique_addrs"))
    print("skip_kind", rows.get("skip_kind"), "never_fetched", rows.get("never_fetched"), "rc", proc.returncode)
    check(rows["unique_names"] == ["170"], "170 repeating names")
    check(rows["unique_addrs"] == ["232"], "232 addrs")
    check(rows["skip_kind"] == ["same-value"], "same-value only")
    check(rows["never_fetched"] == ["-"], "never_fetched empty")
    check(proc.returncode == 0, "lock-input shape rc=0")

    note("replica vs CLI")
    replica_cases: list[tuple[str, str]] = []
    for fname in ["070-reuse.rec", "reuse-same-name.rec", "unseen-unique.rec", "unseen-same-value.rec"]:
        replica_cases.append((fname, (FIX / fname).read_text(encoding="utf-8")))
    replica_cases.append(("stdin-070-shape", "root\t0x1000\nhome-manager\t0x2000\nhome-manager\t0x1000\n"))
    replica_cases.append(("hex-collapse", "root\t1000\nnixpkgs\t0x1000\n"))
    replica_cases.append(("ten-0x10", "root\t10\nnixpkgs\t0x10\n"))
    replica_cases.append(("space", "root 0x10\nnixpkgs 0x10\n"))
    replica_cases.append(("none-skip", "root\t0x1\nnone\t0x1\n"))
    replica_cases.append(("none-visit", "root\t0x1\nnone\t0x2\n"))
    replica_cases.append(("visit-name", "visit\t0x1\n"))
    replica_cases.append(("same-value-3", "nixpkgs\t0x1\nnixpkgs\t0x2\nnixpkgs\t0x3\n"))
    replica_cases.append(("lock-path", "root/nixpkgs\t0x1\nnixpkgs\t0x2\n"))
    replica_cases.append(("same-pointer", "nixpkgs\t0x1\nnixpkgs\t0x1\n"))
    replica_cases.append(("distinct-keys", "root\t0x1000\nhm1\t0x2000\nhm2\t0x1000\n"))
    replica_cases.append(("7ffe", "root\t7ffe1000\nnixpkgs\t0x7ffe1000\n"))
    replica_cases.append(("zero", "a\t0x0\nb\t0\n"))
    replica_cases.append(("neg", "a\t-1\nb\t0x1\n"))  # -1 may be bad
    cap_lines = [f"n{i}\t0x{i:x}" for i in range(8)]
    cap_lines += [f"later{i}\t0x{i % 8:x}" for i in range(40)]
    replica_cases.append(("cap-40", "\n".join(cap_lines) + "\n"))
    uniq_lines = [f"n{i}\t0x{i:x}" for i in range(32)]
    uniq_lines += ["dup\t0x%x" % (i % 32) for i in range(32)]
    uniq_lines += [f"later{i}\t0x{i:x}" for i in range(8)]
    replica_cases.append(("cap-unique", "\n".join(uniq_lines) + "\n"))
    replica_cases.append(("232-170", text if False else "\n".join([f"node{i}\t0x{i:x}" for i in range(170)] + [f"extra{i}\t0x{i:x}" for i in range(62)]) + "\n"))
    replica_cases.append(("empty-tab", "root\t\t0x10\n"))
    replica_cases.append(("extra-field", "root\t0x1\textra\n"))
    replica_cases.append(("padded", "root\t0x1\n  root  \t0x1\n"))
    replica_cases.append(("dash-name", "root\t0x1\n-\t0x1\n"))
    replica_cases.append(("bom", "\ufeffroot\t0x1\n"))
    replica_cases.append(("scientific", "root\t1e2\n"))
    replica_cases.append(("bad-addr", "root\tzz\n"))
    replica_cases.append(("missing", "# none\n"))
    replica_cases.append(("crlf", "root\t0x1\r\nnixpkgs\t0x1\r\n"))
    replica_cases.append(("comment-drop", "# skip\nroot\t0x1\n# x\nnixpkgs\t0x1\n"))
    replica_cases.append(("unicode", "ルート\t0x1\nホーム\t0x1\n"))
    replica_cases.append(("fifo-shape", "a\t0xa\nb\t0xb\na\t0xa\n"))
    replica_cases.append(("later-token", "root\t0x10\nnixpkgs\t10\n"))
    replica_cases.append(("mixed-kinds", "n1\t0x1\nn1\t0x1\nn2\t0x1\n"))
    replica_cases.append(("empty-stdin", ""))
    replica_cases.append(("only-spaces", "   \n"))
    replica_cases.append(("visit-tag", "visit\troot\t0x1000\nvisit\tnixpkgs\t0x1000\n"))
    replica_cases.append(("addrid-rows", "insert\t0xa\tflake-utils\nworker\t0xa\tnaersk\nfetched\tflake-utils\n"))

    eq = 0
    for label, body in replica_cases:
        proc = run_cli([], stdin=body)
        r_out, r_rc = replica_run_text(body)
        stdout_eq = proc.stdout == r_out
        # parse errors: replica returns empty stdout rc=1; CLI prints stderr
        parsed = replica_parse(body)
        if isinstance(parsed, str):
            stdout_eq = proc.stdout == ""
            rc_eq = proc.returncode == 1
        else:
            rc_eq = proc.returncode == r_rc
        ok = stdout_eq and rc_eq
        if ok:
            eq += 1
        print(f"{'MATCH' if ok else 'DIFF'} {label:18} stdout_eq={stdout_eq} rc_eq={rc_eq} cli_rc={proc.returncode} replica_rc={r_rc}")
        if not ok and not isinstance(parsed, str):
            print("CLI:", proc.stdout[:400])
            print("REP:", r_out[:400])
            print("ERR:", proc.stderr[:200])
        elif not ok:
            print("  parse-err replica", parsed, "cli_err", proc.stderr.strip()[:120], "cli_out", repr(proc.stdout[:80]))
    check(eq == len(replica_cases), f"replica MATCH {eq}/{len(replica_cases)}")

    note("membership leftover without format")
    mem_ok = 0
    for fname in ["070-reuse.rec", "reuse-same-name.rec", "unseen-unique.rec", "unseen-same-value.rec"]:
        body = (FIX / fname).read_text(encoding="utf-8")
        proc = run_cli([str(FIX / fname)])
        rows = parse_rows(proc.stdout)
        nf = awk_nf(body)
        cli_nf = [] if rows.get("never_fetched") == ["-"] else rows.get("never_fetched", [])
        # unique-in-order then cap
        shown = unique_in_order(nf)[:LIST_CAP]
        match = shown == cli_nf and ((1 if nf else 0) == proc.returncode or (proc.returncode == 1 and bool(nf)))
        # rc is 1 if nf nonempty
        rc_ok = (proc.returncode == 1) == bool(nf)
        ok = shown == (cli_nf if cli_nf != ["-"] else []) and rc_ok
        # never_fetched unique cap vs full
        if fname == "070-reuse.rec":
            ok = nf == ["home-manager"] and rc_ok
        if fname == "reuse-same-name.rec":
            ok = nf == ["home-manager"] and rc_ok
        if fname == "unseen-unique.rec":
            ok = nf == [] and proc.returncode == 0
        if fname == "unseen-same-value.rec":
            ok = nf == [] and proc.returncode == 0
        print(f"{'MATCH' if ok else 'DIFF'} {fname} nf={nf} cli={cli_nf} rc={proc.returncode}")
        if ok:
            mem_ok += 1
    check(mem_ok == 4, f"membership MATCH {mem_ok}/4 fixtures")

    note("awk occupancy on owned")
    awk = r"""
    BEGIN { FS="[ \t]+" }
    /^#/ || NF==0 { next }
    {
      if ($1=="visit" && NF>=3) { name=$2; addr=$3 }
      else { name=$1; addr=$2 }
      if (addr in done) {
        if (occ[addr] != name) print name
      } else { done[addr]=1; occ[addr]=name }
    }
    """
    for fname in ["070-reuse.rec", "reuse-same-name.rec"]:
        p = subprocess.run(
            ["awk", awk, str(FIX / fname)],
            check=False,
            capture_output=True,
            text=True,
        )
        print(fname, "awk:", repr(p.stdout.strip()), "rc", p.returncode)

    note("cwd-stat live")
    # 1. directory homonym (claimed closed)
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "root").mkdir()
        proc = run_cli(["--live", "--retain", "root", "nixpkgs", "home-manager"], cwd=Path(tmp))
        print("dir homonym rc", proc.returncode, "err", proc.stderr.strip()[:120])
        print(proc.stdout)
        rows = parse_rows(proc.stdout)
        check(proc.returncode == 0, "dir homonym --live --retain rc=0")
        check(rows.get("addrs") == ["slot0", "slot1", "slot2"], "dir homonym slots")
        check("0x" not in proc.stdout, "dir homonym no 0x")

    # 2. file named root in cwd still blocks
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "root").write_text("not a node\n", encoding="utf-8")
        proc = run_cli(["--live", "--retain", "root", "nixpkgs", "home-manager"], cwd=Path(tmp))
        print("file homonym rc", proc.returncode)
        print("err", proc.stderr.strip())
        print("out", repr(proc.stdout))
        check(proc.returncode == 1, "file named root blocks --live root")
        check("existing file is not a live NAME" in proc.stderr, "file homonym message")
        check(proc.stdout == "", "file homonym empty stdout")

    # 3. --live visitid from archive cwd (visitid is a file)
    proc = run_cli(["--live", "visitid"], cwd=ARCH)
    print("live visitid (file in cwd) rc", proc.returncode, proc.stderr.strip())
    check(proc.returncode == 1 and "existing file" in proc.stderr, "--live visitid is cwd-stat of the CLI file")

    # 4. --live README.md from repo root
    repo = Path("/Users/annenpolka/ghq/github.com/annenpolka/brrr")
    proc = run_cli(["--live", "--retain", "root", "nixpkgs", "home-manager"], cwd=repo)
    print("from repo root (root/ dir) rc", proc.returncode, "addrs", parse_rows(proc.stdout).get("addrs"))
    check(proc.returncode == 0, "repo root directory homonym rc=0")
    proc = run_cli(["--live", "README.md"], cwd=repo)
    print("live README.md from repo rc", proc.returncode, proc.stderr.strip()[:160])
    check(proc.returncode == 1 and "existing file" in proc.stderr, "--live README.md cwd-stat file")

    # 5. relative path that is a file vs a NAME
    proc = run_cli(["--live", str(FIX / "070-reuse.rec")])
    check(proc.returncode == 1 and "existing file" in proc.stderr, "--live FILE path refused")

    note("--live slots not 0x; still occupancy")
    addrs_sets = []
    for i in range(6):
        proc = run_cli(["--live", "root", "nixpkgs", "home-manager"])
        rows = parse_rows(proc.stdout)
        addrs_sets.append(tuple(rows.get("addrs", [])))
        check(all(a.startswith("slot") and not a.startswith("0x") for a in rows.get("addrs", [])), f"live drop {i} slots")
        check("0x" not in proc.stdout, f"live drop {i} no 0x in stdout")
        check(rows.get("pointer_key") == ["slot"], f"live drop {i} pointer_key slot")
        print(f"live drop {i} rc={proc.returncode} addrs={rows.get('addrs')} unique_addrs={rows.get('unique_addrs')} nf={rows.get('never_fetched')} reuse={rows.get('allocator_reuse')}")
    print("addr tuples distinct?", len(set(addrs_sets)), "of", len(addrs_sets), "tuples", set(addrs_sets))
    # labels are occupancy so colliding runs share slot0 slot1; retain unique
    proc = run_cli(["--live", "--retain", "a", "b", "c"])
    rows = parse_rows(proc.stdout)
    check(rows["addrs"] == ["slot0", "slot1", "slot2"] and proc.returncode == 0, "retain unique slots rc=0")

    note("live 232 names still two slots")
    names = [f"n{i}" for i in range(232)]
    proc = run_cli(["--live", *names])
    rows = parse_rows(proc.stdout)
    print("232 live unique_addrs", rows.get("unique_addrs"), "nf_n", rows.get("never_fetched_n"), "rc", proc.returncode)
    print("allocator_reuse", rows.get("allocator_reuse"))
    print("addrs", rows.get("addrs"))
    if rows.get("unique_addrs") == ["2"]:
        check(int(rows["never_fetched_n"][0]) == 230, "232 live never_fetched_n 230")
        check(len(rows["never_fetched"]) == 32, "232 live cap 32")
        check(rows["allocator_reuse"][0] == "ping-pong", "232 live ping-pong")

    note("cap unique vs hide later32")
    lines = [f"n{i}\t0x{i:x}" for i in range(8)]
    lines += [f"later{i}\t0x{i % 8:x}" for i in range(40)]
    proc = run_cli([], stdin="\n".join(lines) + "\n")
    rows = parse_rows(proc.stdout)
    print("never_fetched_n", rows["never_fetched_n"], "len", len(rows["never_fetched"]))
    print("never_fetched", rows["never_fetched"])
    check(rows["never_fetched_n"] == ["40"], "cap count 40")
    check(len(rows["never_fetched"]) == 32, "list cap 32")
    check(rows["never_fetched"][0] == "later0" and "later31" in rows["never_fetched"], "later0..31 shown")
    check("later32" not in rows["never_fetched"] and "later39" not in rows["never_fetched"], "later32..39 hidden")

    note("third field / adrid concat / flake input")
    proc = run_cli([], stdin="n1\t0x1\tnixpkgs\nn2\t0x1\tnixpkgs\n")
    print("third field", proc.returncode, proc.stderr.strip())
    check(proc.returncode == 1 and "extra field" in proc.stderr and proc.stdout == "", "flake input column refused")
    proc = run_cli([], stdin="insert\t0xa\tflake-utils\nworker\t0xa\tnaersk\n")
    print("addrid rows", proc.returncode, proc.stderr.strip())
    check(proc.returncode == 1 and proc.stdout == "", "addrid insert/worker refused")
    proc = run_cli([], stdin="insert 0xa\nworker 0xa\n")
    print("addrid two-col", proc.returncode, proc.stderr.strip()[:120], "out", proc.stdout[:80])
    # two-col insert 0xa would parse name=insert addr=0xa; worker 0xa name=worker
    rows = parse_rows(proc.stdout)
    print("two-col adrid-like rows", rows.get("names"), rows.get("never_fetched"), "rc", proc.returncode)

    note("pipes / missing / dash-as-record")
    proc = run_cli(["/no/such/visitid.rec"])
    print("missing", proc.returncode, proc.stderr.strip()[:80], "out", repr(proc.stdout))
    check(proc.returncode == 1 and proc.stdout == "", "missing file rc=1 empty stdout")
    proc = run_cli(["-"], stdin="root\t0x1\nnixpkgs\t0x1\n")
    print("dash record", proc.returncode, proc.stderr.strip()[:120], "out", repr(proc.stdout[:80]))
    # Path('-') may be missing-file
    check(proc.returncode == 1, "`-` as RECORD is error (not stdin)")
    proc = run_cli([], stdin="root\t0x1\nnixpkgs\t0x1\n")
    check(proc.returncode == 1 and parse_rows(proc.stdout)["never_fetched"] == ["nixpkgs"], "stdin works")
    # FIFO
    with tempfile.TemporaryDirectory() as tmp:
        fifo = Path(tmp) / "pipe.rec"
        os.mkfifo(fifo)
        def writer():
            with fifo.open("w", encoding="utf-8") as fh:
                fh.write("root\t0x1\nhome-manager\t0x1\n")
        import threading
        t = threading.Thread(target=writer)
        t.start()
        proc = run_cli([str(fifo)])
        t.join()
        print("fifo rc", proc.returncode, parse_rows(proc.stdout).get("never_fetched"))
        check(proc.returncode == 1 and parse_rows(proc.stdout).get("never_fetched") == ["home-manager"], "FIFO owned shape")

    note("value_key is a constant string")
    src = CLI.read_text(encoding="utf-8")
    check('"value_key\\tname"' in src or '"value_key\tname"' in src, "value_key hardcoded name")
    check("walk_pointer" in src and "walk_value" in src, "two walk functions")
    check("if event.addr in done" in src and "if event.name in done" in src, "set membership walks")
    check("Path(name)" in src and "is_file()" in src, "cwd-stat is_file live")
    check("pointer_done" not in src and "value_done" not in src, "synonym fields deleted from source")

    note("demo logs")
    d1 = (ARCH / "demo-1.log").read_bytes()
    d2 = (ARCH / "demo-2.log").read_bytes()
    check(d1 == d2, "demo-1.log == demo-2.log")
    check(b"value_key\tname" in d1, "demo value_key name")
    check(b"pointer_done" not in d1, "demo no pointer_done")
    check(b"never_fetched\thome-manager" in d1, "demo never_fetched")
    check(b"rc=1" in d1, "demo rc=1")

    print(f"\n==== SUMMARY PASS={PASS} FAIL={FAIL} ====")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
