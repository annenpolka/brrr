#!/usr/bin/env python3
"""Host attacks for DESTROYER_refpin_3. Archive only. No nix. No worktree edits."""
from __future__ import annotations

import hashlib
import importlib.machinery
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path("/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112")
CLI = ROOT / "lineages/candidate-refpin/refpin"
FIX = ROOT / "lineages/candidate-refpin/fixtures"
SCRATCH = Path(__file__).resolve().parent
REPLICA = SCRATCH / "replica.py"
WT = Path("/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-refpin-refpin/candidate-refpin/refpin")
LOG = SCRATCH / "attack.log"

REV = "e374a4ebd0dbf7b23e077a94fd5cefb7a9d65ffa"
HASH_A = "sha256-UEzJabo6ObaQc0Rc5XJOf43NR5Rp3e0WwpWi55c79R8="
HASH_B = "sha256-q2mgMIPLqHSx0pSEJ42rrZpYxcjkgL1U1UvCTHTw+Oo="
HARVEST = "pinned-rev-default-ref-changed-hash"
LOADBEARING = (
    "verdict",
    "same_rev",
    "rev",
    "rev_a",
    "rev_b",
    "narHash_a",
    "narHash_b",
    "identity_changed",
    "ref_present_a",
    "ref_present_b",
    "ref_a",
    "ref_b",
    "ref_attached",
    "attached_ref",
    "removed_ref",
    "equal",
    "diverged",
    "present_only_a",
    "present_only_b",
    "narHash_capped",
)

sys.path.insert(0, str(SCRATCH))
import replica as R  # noqa: E402


def log(msg: str) -> None:
    print(msg, flush=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(msg + "\n")


def sha256_file(path: Path) -> tuple[str, int]:
    data = path.read_bytes()
    return hashlib.sha256(data).hexdigest(), len(data)


def run_cli(args, *, stdin=None, timeout=20):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True,
        text=True,
        check=False,
        input=stdin,
        timeout=timeout,
    )


def parse_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if not line or "\t" not in line:
            continue
        name, *rest = line.split("\t")
        rows[name] = rest
    return rows


def rec(*lines: str) -> str:
    return "\n".join(lines) + "\n"


def write_pair(td: Path, a: str, b: str, na="a.rec", nb="b.rec") -> tuple[Path, Path]:
    pa = td / na
    pb = td / nb
    pa.write_text(a, encoding="utf-8")
    pb.write_text(b, encoding="utf-8")
    return pa, pb


def loadbearing(text: str) -> dict[str, list[str]]:
    rows = parse_rows(text)
    return {k: rows[k] for k in LOADBEARING if k in rows}


def replica_pair(a_text: str, b_text: str | None) -> tuple[str, int]:
    first, second = R.parse_pair(a_text, b_text)
    result = R.inspect(first, second)
    return R.format_report(result), R.exit_status(result["verdict"])


def thin_of(a_text: str, b_text: str | None) -> dict[str, str]:
    first, second = R.parse_pair(a_text, b_text)
    return R.thin_harvest(first, second)


def awk_tsv_pair(a_path: Path, b_path: Path) -> dict[str, str]:
    script = r"""
BEGIN{FS="\t"}
FNR==NR {
  if($1=="rev") ra=$2
  if($1=="narHash") ha=$2
  if($1=="ref") {refa=$2; pa=1}
  next
}
{
  if($1=="rev") rb=$2
  if($1=="narHash") hb=$2
  if($1=="ref") {refb=$2; pb=1}
}
END{
  same = (ra==rb)
  idch = (ha!=hb)
  attached = (!pa && pb)
  harvest = (same && idch && attached)
  printf "same_rev\t%s\n", same?"yes":"no"
  printf "identity_changed\t%s\n", idch?"yes":"no"
  printf "ref_attached\t%s\n", attached?"attached":"other"
  printf "harvest\t%s\n", harvest?"yes":"no"
  printf "attached_ref\t%s\n", attached?refb:"-"
}
"""
    proc = subprocess.run(
        ["awk", script, str(a_path), str(b_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    out: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        if "\t" in line:
            k, v = line.split("\t", 1)
            out[k] = v
    return out


def section(title: str) -> None:
    log("\n" + "=" * 72)
    log(title)
    log("=" * 72)


def main() -> int:
    if LOG.exists():
        LOG.unlink()
    results: dict[str, object] = {}

    section("IDENTITY")
    h, n = sha256_file(CLI)
    log(f"archive sha256 {h} ({n} bytes)")
    results["sha256"] = h
    results["bytes"] = n
    log(f"python {sys.version.split()[0]}")
    nix = shutil.which("nix")
    log(f"nix PATH={nix!r}")
    results["nix"] = nix
    if WT.exists():
        cmp = subprocess.run(["cmp", str(CLI), str(WT)], capture_output=True)
        log(f"worktree cmp rc={cmp.returncode}")
        results["wt_cmp"] = cmp.returncode
        wh, wn = sha256_file(WT)
        log(f"worktree sha256 {wh} ({wn} bytes)")
    else:
        log("worktree missing")
        results["wt_cmp"] = None
    parent = subprocess.run(
        ["git", "-C", str(ROOT.parent.parent), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
    )
    log(f"parent HEAD {parent.stdout.strip()}")
    ls = subprocess.run(
        ["git", "-C", str(ROOT.parent.parent), "ls-tree", "-r", "--name-only", "HEAD"],
        capture_output=True,
        text=True,
    )
    in_main = [p for p in ls.stdout.splitlines() if "refpin" in p and "candidate-refpin" not in p]
    log(f"refpin product on main: {in_main[:8]!r} count={len(in_main)}")
    results["in_main"] = in_main

    section("TESTS")
    tests = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(FIX.parent / "tests"), "-v"],
        capture_output=True,
        text=True,
        cwd=str(FIX.parent),
        timeout=60,
    )
    log(tests.stderr[-2000:] if tests.stderr else tests.stdout[-2000:])
    log(f"tests rc={tests.returncode}")
    results["tests_rc"] = tests.returncode
    results["tests_tail"] = (tests.stderr or tests.stdout)[-400:]

    section("INSPECT BYTECODE")
    loader = importlib.machinery.SourceFileLoader("refpin_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = mod
    loader.exec_module(mod)
    log(f"inspect.co_names={mod.inspect.__code__.co_names}")
    log(f"inspect.co_varnames={mod.inspect.__code__.co_varnames}")
    log(f"verdict_of.co_names={mod.verdict_of.__code__.co_names}")
    log(f"ref_attached_of.co_names={mod.ref_attached_of.__code__.co_names}")
    src = CLI.read_text(encoding="utf-8")
    for forbidden in ("fetchGit", "subprocess", "nix", "nar", "git", "hashlib", "sha256"):
        hits = [i + 1 for i, line in enumerate(src.splitlines()) if forbidden in line]
        log(f"source token {forbidden!r} lines={hits[:20]}")
    results["co_names"] = list(mod.inspect.__code__.co_names)

    section("OWNED + SWAP + IDENTICAL + NATIVE")
    owned_cases = [
        ("owned-rec", [str(FIX / "064-expected.rec"), str(FIX / "064-got.rec")], None),
        ("swap-rec", [str(FIX / "064-got.rec"), str(FIX / "064-expected.rec")], None),
        ("identical", [str(FIX / "unseen-same.rec"), str(FIX / "unseen-same-b.rec")], None),
        ("native-log", [str(FIX / "narhash_mismatch.txt")], None),
        ("nix-error", [str(FIX / "nix-error.txt")], None),
        ("json", [str(FIX / "064-expected.json"), str(FIX / "064-got.json")], None),
        ("lock", [str(FIX / "064-expected.json"), str(FIX / "064-got.lock")], None),
        ("stdin-first", ["-", str(FIX / "064-got.rec")], (FIX / "064-expected.rec").read_text()),
    ]
    replica_eq = []
    thin_eq = []
    for name, args, stdin in owned_cases:
        proc = run_cli(args, stdin=stdin)
        rows = parse_rows(proc.stdout)
        log(f"\n--- {name} rc={proc.returncode} ---")
        log(proc.stdout)
        if stdin is not None:
            a_text = stdin
            b_text = Path(args[1]).read_text(encoding="utf-8") if len(args) > 1 else None
        elif len(args) == 1:
            a_text = Path(args[0]).read_text(encoding="utf-8")
            b_text = None
        else:
            a_text = Path(args[0]).read_text(encoding="utf-8")
            b_text = Path(args[1]).read_text(encoding="utf-8")
        r_out, r_rc = replica_pair(a_text, b_text)
        lb_cli = loadbearing(proc.stdout)
        lb_rep = loadbearing(r_out)
        eq = lb_cli == lb_rep and proc.returncode == r_rc
        replica_eq.append((name, eq, proc.returncode, r_rc, lb_cli.get("verdict"), lb_rep.get("verdict")))
        log(f"replica loadbearing_eq={eq} cli_rc={proc.returncode} replica_rc={r_rc}")
        if not eq:
            log(f"  cli={lb_cli}")
            log(f"  rep={lb_rep}")
        thin = thin_of(a_text, b_text)
        cli_harvest = rows.get("verdict", [""])[0] == HARVEST
        thin_match = (thin["harvest"] == "yes") == cli_harvest
        thin_eq.append((name, thin_match, thin, cli_harvest, rows.get("verdict")))
        log(f"thin harvest={thin} cli_harvest={cli_harvest} match={thin_match}")

    results["replica_eq"] = replica_eq
    results["thin_eq"] = thin_eq
    log(f"\nreplica loadbearing IDENTICAL {sum(1 for x in replica_eq if x[1])}/{len(replica_eq)}")
    log(f"thin harvest MATCH {sum(1 for x in thin_eq if x[1])}/{len(thin_eq)}")

    section("AWK of caller-labeled TSV rows")
    awk_cases = []
    for name, a, b in [
        ("owned", FIX / "064-expected.rec", FIX / "064-got.rec"),
        ("swap", FIX / "064-got.rec", FIX / "064-expected.rec"),
        ("identical", FIX / "unseen-same.rec", FIX / "unseen-same-b.rec"),
    ]:
        proc = run_cli([str(a), str(b)])
        rows = parse_rows(proc.stdout)
        awk = awk_tsv_pair(a, b)
        cli_harvest = rows.get("verdict", [""])[0] == HARVEST
        awk_harvest = awk.get("harvest") == "yes"
        match = (
            awk.get("same_rev") == rows.get("same_rev", [""])[0]
            and awk.get("identity_changed") == rows.get("identity_changed", [""])[0]
            and (awk_harvest == cli_harvest)
        )
        awk_cases.append((name, match, awk, rows.get("verdict"), rows.get("ref_attached")))
        log(f"awk {name}: {awk} cli_verdict={rows.get('verdict')} match={match}")
    results["awk"] = awk_cases

    section("LEFTOVER (1) unrelated ref + owned hash pair still harvest")
    with tempfile.TemporaryDirectory() as tmp:
        td = Path(tmp)
        a, b = write_pair(
            td,
            rec(f"rev\t{REV}", f"narHash\t{HASH_A}"),
            rec(f"rev\t{REV}", f"narHash\t{HASH_B}", "ref\tunrelated-topic-branch"),
        )
        proc = run_cli([str(a), str(b)])
        rows = parse_rows(proc.stdout)
        log(proc.stdout)
        log(f"rc={proc.returncode} verdict={rows.get('verdict')} attached_ref={rows.get('attached_ref')}")
        results["unrelated_ref"] = {
            "rc": proc.returncode,
            "verdict": rows.get("verdict"),
            "attached_ref": rows.get("attached_ref"),
            "still_harvest": rows.get("verdict") == [HARVEST],
        }
        a2, b2 = write_pair(
            td,
            rec(f"rev\t{REV}", f"narHash\t{HASH_A}"),
            rec(f"rev\t{REV}", f"narHash\t{HASH_B}", "ref\tHEAD"),
            "c.rec",
            "d.rec",
        )
        proc2 = run_cli([str(a2), str(b2)])
        rows2 = parse_rows(proc2.stdout)
        log(f"HEAD attach verdict={rows2.get('verdict')} attached_ref={rows2.get('attached_ref')} rc={proc2.returncode}")
        results["head_ref"] = {
            "verdict": rows2.get("verdict"),
            "still_harvest": rows2.get("verdict") == [HARVEST],
        }

    section("LEFTOVER (2) sha256: vs sha256- same payload is identity_changed")
    with tempfile.TemporaryDirectory() as tmp:
        td = Path(tmp)
        dash = rec(f"rev\t{REV}", f"narHash\t{HASH_A}")
        colon_hash = HASH_A.replace("sha256-", "sha256:", 1)
        colon = rec(f"rev\t{REV}", f"narHash\t{colon_hash}")
        a, b = write_pair(td, dash, colon)
        proc = run_cli([str(a), str(b)])
        rows = parse_rows(proc.stdout)
        log(proc.stdout)
        log(f"prefix-only rc={proc.returncode} verdict={rows.get('verdict')} identity={rows.get('identity_changed')}")
        results["hash_form_no_ref"] = {
            "verdict": rows.get("verdict"),
            "identity_changed": rows.get("identity_changed"),
            "still_yes": rows.get("identity_changed") == ["yes"],
        }
        colon_ref = rec(f"rev\t{REV}", f"narHash\t{colon_hash}", "ref\tmaster")
        a, b = write_pair(td, dash, colon_ref, "e.rec", "f.rec")
        proc = run_cli([str(a), str(b)])
        rows = parse_rows(proc.stdout)
        log(proc.stdout)
        log(f"prefix+attach rc={proc.returncode} verdict={rows.get('verdict')}")
        results["hash_form_attach"] = {
            "verdict": rows.get("verdict"),
            "still_harvest": rows.get("verdict") == [HARVEST],
        }
        sha_upper = HASH_A.replace("sha256-", "SHA256-", 1)
        a, b = write_pair(
            td,
            rec(f"rev\t{REV}", f"narHash\t{HASH_A}"),
            rec(f"rev\t{REV}", f"narHash\t{sha_upper}", "ref\tmaster"),
            "g.rec",
            "h.rec",
        )
        proc = run_cli([str(a), str(b)])
        rows = parse_rows(proc.stdout)
        log(f"SHA256- attach verdict={rows.get('verdict')} identity={rows.get('identity_changed')}")
        results["hash_form_upper"] = {
            "verdict": rows.get("verdict"),
            "still_harvest": rows.get("verdict") == [HARVEST],
        }
        # JSON trailing space vs TSV strip
        js = td / "space.json"
        js.write_text(
            json.dumps({"rev": REV, "narHash": HASH_A + " "}),
            encoding="utf-8",
        )
        tsv = td / "space.rec"
        tsv.write_text(rec(f"rev\t{REV}", f"narHash\t{HASH_A}"), encoding="utf-8")
        proc = run_cli([str(tsv), str(js)])
        rows = parse_rows(proc.stdout)
        log(f"json trailing space verdict={rows.get('verdict')} identity={rows.get('identity_changed')} stderr={proc.stderr.strip()!r}")
        results["json_space"] = {
            "rc": proc.returncode,
            "verdict": rows.get("verdict"),
            "identity_changed": rows.get("identity_changed"),
            "stderr": proc.stderr.strip(),
        }

    section("LEFTOVER (3) lastModified placeholders 1/1")
    expected = (FIX / "064-expected.rec").read_text()
    got = (FIX / "064-got.rec").read_text()
    log("owned rec contains lastModified 1 / revCount 1:")
    log(repr(expected))
    log(repr(got))
    proc = run_cli([str(FIX / "064-expected.rec"), str(FIX / "064-got.rec")])
    rows = parse_rows(proc.stdout)
    log(f"owned equal={rows.get('equal')}")
    proc_log = run_cli([str(FIX / "narhash_mismatch.txt")])
    rows_log = parse_rows(proc_log.stdout)
    log(f"native log equal={rows_log.get('equal')}")
    results["owned_equal"] = rows.get("equal")
    results["log_equal"] = rows_log.get("equal")
    with tempfile.TemporaryDirectory() as tmp:
        td = Path(tmp)
        a, b = write_pair(
            td,
            rec(f"rev\t{REV}", f"narHash\t{HASH_A}", "lastModified\t1"),
            rec(f"rev\t{REV}", f"narHash\t{HASH_A}", "lastModified\t1710000000"),
        )
        proc = run_cli([str(a), str(b)])
        rows = parse_rows(proc.stdout)
        log(f"placeholder vs recovered-looking: verdict={rows.get('verdict')} rc={proc.returncode} diverged={rows.get('diverged')}")
        results["placeholder_vs_clock"] = {
            "verdict": rows.get("verdict"),
            "rc": proc.returncode,
            "diverged": rows.get("diverged"),
        }

    section("MULTI-NODE flake.lock refused")
    with tempfile.TemporaryDirectory() as tmp:
        td = Path(tmp)
        multi = {
            "nodes": {
                "root": {"inputs": {"src": "src", "nixpkgs": "nixpkgs"}},
                "src": {
                    "locked": {
                        "lastModified": 1,
                        "narHash": HASH_B,
                        "ref": "master",
                        "rev": REV,
                        "revCount": 1,
                        "type": "git",
                        "url": "file:///workspace/build/buildkite",
                    }
                },
                "nixpkgs": {
                    "locked": {
                        "lastModified": 2,
                        "narHash": "sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
                        "rev": "cccccccccccccccccccccccccccccccccccccccc",
                        "type": "github",
                    }
                },
            },
            "root": "root",
            "version": 7,
        }
        p = td / "multi.lock"
        p.write_text(json.dumps(multi), encoding="utf-8")
        proc = run_cli([str(FIX / "064-expected.json"), str(p)])
        log(f"stdout={proc.stdout!r}")
        log(f"stderr={proc.stderr.strip()!r} rc={proc.returncode}")
        results["multi_node"] = {
            "rc": proc.returncode,
            "stderr": proc.stderr.strip(),
            "stdout": proc.stdout,
        }

    section("HEAD warning using 'master' is not ingest")
    with tempfile.TemporaryDirectory() as tmp:
        td = Path(tmp)
        stripped = """warning: could not read HEAD ref from repo at '/workspace/build/buildkite', using 'master'
error: mismatch in field 'narHash' of input
  expected: sha256-UEzJabo6ObaQc0Rc5XJOf43NR5Rp3e0WwpWi55c79R8=  (no ref field)
  got:      sha256-q2mgMIPLqHSx0pSEJ42rrZpYxcjkgL1U1UvCTHTw+Oo=  (no ref field)
rev in both records: e374a4ebd0dbf7b23e077a94fd5cefb7a9d65ffa
"""
        p = td / "no-annot.txt"
        p.write_text(stripped, encoding="utf-8")
        proc = run_cli([str(p)])
        rows = parse_rows(proc.stdout)
        log(proc.stdout)
        log(f"stderr={proc.stderr.strip()!r} rc={proc.returncode}")
        results["warning_not_ingest"] = {
            "verdict": rows.get("verdict"),
            "ref_present_b": rows.get("ref_present_b"),
            "ref_attached": rows.get("ref_attached"),
            "rc": proc.returncode,
        }

    section("original.ref / url?ref= ignored")
    with tempfile.TemporaryDirectory() as tmp:
        td = Path(tmp)
        orig = {
            "locked": {
                "rev": REV,
                "narHash": HASH_B,
                "type": "git",
                "url": "file:///x?ref=master",
            },
            "original": {"ref": "master", "type": "git", "url": "file:///x"},
        }
        p = td / "orig.json"
        p.write_text(json.dumps(orig), encoding="utf-8")
        a = td / "a.rec"
        a.write_text(rec(f"rev\t{REV}", f"narHash\t{HASH_A}"), encoding="utf-8")
        proc = run_cli([str(a), str(p)])
        rows = parse_rows(proc.stdout)
        log(proc.stdout)
        log(f"stderr={proc.stderr.strip()!r} rc={proc.returncode}")
        results["original_ref_ignored"] = {
            "verdict": rows.get("verdict"),
            "ref_present_b": rows.get("ref_present_b"),
            "ref_b": rows.get("ref_b"),
        }

    section("/dev/stdin twice")
    proc = run_cli(
        ["/dev/stdin", "/dev/stdin"],
        stdin=(FIX / "064-expected.rec").read_text(),
    )
    log(f"stdout={proc.stdout!r}")
    log(f"stderr={proc.stderr.strip()!r} rc={proc.returncode}")
    results["dev_stdin_twice"] = {
        "rc": proc.returncode,
        "stderr": proc.stderr.strip(),
        "stdout": proc.stdout,
    }
    proc = run_cli(["-", "-"], stdin=(FIX / "064-expected.rec").read_text())
    log(f"- - stderr={proc.stderr.strip()!r} rc={proc.returncode}")

    section("both-disagree swallows hash")
    with tempfile.TemporaryDirectory() as tmp:
        td = Path(tmp)
        a, b = write_pair(
            td,
            rec(f"rev\t{REV}", f"narHash\t{HASH_A}", "ref\tHEAD"),
            rec(f"rev\t{REV}", f"narHash\t{HASH_B}", "ref\trefs/heads/master"),
        )
        proc = run_cli([str(a), str(b)])
        rows = parse_rows(proc.stdout)
        log(proc.stdout)
        results["both_disagree"] = {
            "verdict": rows.get("verdict"),
            "identity_changed": rows.get("identity_changed"),
            "diverged": rows.get("diverged"),
        }

    section("HOST CASES replica vs CLI (generated TSV)")
    generated = []
    cases = [
        ("owned-shape", rec(f"rev\t{REV}", f"narHash\t{HASH_A}", "lastModified\t1", "revCount\t1"),
         rec(f"rev\t{REV}", f"narHash\t{HASH_B}", "ref\tmaster", "lastModified\t1", "revCount\t1")),
        ("no-meta", rec(f"rev\t{REV}", f"narHash\t{HASH_A}"),
         rec(f"rev\t{REV}", f"narHash\t{HASH_B}", "ref\tmaster")),
        ("unrelated-ref", rec(f"rev\t{REV}", f"narHash\t{HASH_A}"),
         rec(f"rev\t{REV}", f"narHash\t{HASH_B}", "ref\tunrelated-topic-branch")),
        ("same-hash-attach", rec(f"rev\t{REV}", f"narHash\t{HASH_A}"),
         rec(f"rev\t{REV}", f"narHash\t{HASH_A}", "ref\tmaster")),
        ("hash-no-ref", rec(f"rev\t{REV}", f"narHash\t{HASH_A}"),
         rec(f"rev\t{REV}", f"narHash\t{HASH_B}")),
        ("swap-shape", rec(f"rev\t{REV}", f"narHash\t{HASH_B}", "ref\tmaster"),
         rec(f"rev\t{REV}", f"narHash\t{HASH_A}")),
        ("identical-shape", rec(f"rev\t{REV}", f"narHash\t{HASH_A}"),
         rec(f"rev\t{REV}", f"narHash\t{HASH_A}")),
        ("rev-diverged", rec(f"rev\t{REV}", f"narHash\t{HASH_A}"),
         rec("rev\tbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", f"narHash\t{HASH_A}")),
        ("both-disagree", rec(f"rev\t{REV}", f"narHash\t{HASH_A}", "ref\tmain"),
         rec(f"rev\t{REV}", f"narHash\t{HASH_B}", "ref\tmaster")),
        ("both-same-ref-hash", rec(f"rev\t{REV}", f"narHash\t{HASH_A}", "ref\tmaster"),
         rec(f"rev\t{REV}", f"narHash\t{HASH_B}", "ref\tmaster")),
        ("none-token", rec(f"rev\t{REV}", f"narHash\t{HASH_A}"),
         rec(f"rev\t{REV}", f"narHash\t{HASH_B}", "ref\tnone")),
        ("empty-ref", rec(f"rev\t{REV}", f"narHash\t{HASH_A}"),
         rec(f"rev\t{REV}", f"narHash\t{HASH_A}", "ref\t")),
        ("lastmod-only", rec(f"rev\t{REV}", f"narHash\t{HASH_A}", "lastModified\t100"),
         rec(f"rev\t{REV}", f"narHash\t{HASH_A}", "lastModified\t200")),
        ("meta-presence", rec(f"rev\t{REV}", f"narHash\t{HASH_A}", "lastModified\t100"),
         rec(f"rev\t{REV}", f"narHash\t{HASH_A}")),
        ("prefix-form", rec(f"rev\t{REV}", f"narHash\t{HASH_A}"),
         rec(f"rev\t{REV}", f"narHash\t{HASH_A.replace('sha256-', 'sha256:', 1)}", "ref\tmaster")),
        ("huge-hash", rec(f"rev\t{REV}", "narHash\tsha256-" + ("A" * 400)),
         rec(f"rev\t{REV}", "narHash\tsha256-" + ("B" * 400), "ref\tmaster")),
        ("crlf", rec(f"rev\t{REV}", f"narHash\t{HASH_A}").replace("\n", "\r\n"),
         rec(f"rev\t{REV}", f"narHash\t{HASH_B}", "ref\tmaster").replace("\n", "\r\n")),
        ("bom", "\ufeff" + rec(f"rev\t{REV}", f"narHash\t{HASH_A}"),
         rec(f"rev\t{REV}", f"narHash\t{HASH_B}", "ref\tmaster")),
        ("comment", "# note\n" + rec(f"rev\t{REV}", f"narHash\t{HASH_A}"),
         rec(f"rev\t{REV}", f"narHash\t{HASH_B}", "ref\tmaster")),
        ("url-ignored", rec(f"rev\t{REV}", f"narHash\t{HASH_A}", "url\tgit+file:///x", "type\tgit"),
         rec(f"rev\t{REV}", f"narHash\t{HASH_B}", "ref\tmaster", "url\tgit+file:///x", "type\tgit")),
        ("space-name", rec(f"rev\t{REV}", f"narHash\t{HASH_A}"),
         rec(f"rev\t{REV}", f"narHash\t{HASH_B}", "ref\tmaster"), "a rec.txt", "b rec.txt"),
    ]
    with tempfile.TemporaryDirectory() as tmp:
        td = Path(tmp)
        for item in cases:
            if len(item) == 3:
                name, a_text, b_text = item
                na, nb = "a.rec", "b.rec"
            else:
                name, a_text, b_text, na, nb = item
            a, b = write_pair(td, a_text, b_text, na, nb)
            proc = run_cli([str(a), str(b)])
            r_out, r_rc = replica_pair(a_text, b_text)
            lb_cli = loadbearing(proc.stdout)
            lb_rep = loadbearing(r_out)
            eq = lb_cli == lb_rep and proc.returncode == r_rc
            thin = thin_of(a_text, b_text)
            cli_harvest = parse_rows(proc.stdout).get("verdict", [""])[0] == HARVEST
            thin_match = (thin["harvest"] == "yes") == cli_harvest
            generated.append({
                "name": name,
                "eq": eq,
                "thin": thin_match,
                "cli_rc": proc.returncode,
                "rep_rc": r_rc,
                "verdict": parse_rows(proc.stdout).get("verdict"),
                "thin_harvest": thin["harvest"],
            })
            log(f"{name}: loadbearing_eq={eq} thin_match={thin_match} verdict={parse_rows(proc.stdout).get('verdict')} rc={proc.returncode}")
            if not eq:
                log(f"  CLI {lb_cli}")
                log(f"  REP {lb_rep}")
                log(f"  stderr={proc.stderr.strip()!r}")
            if na != "a.rec":
                (td / na).unlink(missing_ok=True)
                (td / nb).unlink(missing_ok=True)
    results["generated"] = generated
    log(f"generated loadbearing IDENTICAL {sum(1 for x in generated if x['eq'])}/{len(generated)}")
    log(f"generated thin MATCH {sum(1 for x in generated if x['thin'])}/{len(generated)}")

    section("NEAREST: diff already names the field delta")
    diff = subprocess.run(
        ["diff", "-u", str(FIX / "064-expected.rec"), str(FIX / "064-got.rec")],
        capture_output=True,
        text=True,
    )
    log(diff.stdout)
    log(f"diff names harvest token? {HARVEST in diff.stdout}")
    results["diff_has_harvest_name"] = HARVEST in diff.stdout

    section("SUMMARY")
    leftover = {
        "unrelated_ref_still_harvest": results["unrelated_ref"]["still_harvest"],
        "hash_form_still_identity": results["hash_form_no_ref"]["still_yes"],
        "hash_form_attach_still_harvest": results["hash_form_attach"]["still_harvest"],
        "owned_equal_has_placeholders": "lastModified" in (results["owned_equal"] or [])
        and "revCount" in (results["owned_equal"] or []),
        "native_log_equal_rev_only": results["log_equal"] == ["rev"],
        "multi_node_refused": "2 locked nodes" in results["multi_node"]["stderr"],
        "warning_not_ingest": results["warning_not_ingest"]["verdict"] == ["hash-changed-no-ref"],
        "dev_stdin_twice_not_same_as_dash": "cannot read stdin twice" not in results["dev_stdin_twice"]["stderr"],
    }
    log(json.dumps(leftover, indent=2))
    n_rep = sum(1 for x in replica_eq if x[1]) + sum(1 for x in generated if x["eq"])
    n_rep_tot = len(replica_eq) + len(generated)
    n_thin = sum(1 for x in thin_eq if x[1]) + sum(1 for x in generated if x["thin"])
    n_thin_tot = len(thin_eq) + len(generated)
    log(f"TOTAL replica loadbearing {n_rep}/{n_rep_tot}")
    log(f"TOTAL thin harvest AND {n_thin}/{n_thin_tot}")
    results["leftover"] = leftover
    results["totals"] = {"replica": f"{n_rep}/{n_rep_tot}", "thin": f"{n_thin}/{n_thin_tot}"}
    (SCRATCH / "summary.json").write_text(json.dumps(results, indent=2, default=str) + "\n", encoding="utf-8")
    log(f"wrote {SCRATCH / 'summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
