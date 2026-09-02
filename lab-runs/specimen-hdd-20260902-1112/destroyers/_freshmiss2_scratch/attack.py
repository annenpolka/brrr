#!/usr/bin/env python3
"""Independent replica vs freshmiss CLI. Does not import the CLI module."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path("/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112")
CLI = ROOT / "lineages/candidate-freshmiss/freshmiss"
FIX = ROOT / "lineages/candidate-freshmiss/tests/fixtures"
SCRATCH = Path(__file__).resolve().parent
KNOWN = ("status", "identity", "requested", "present", "dir", "bytes")


def unique(items):
    seen, out = set(), []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def split_values(rest: str):
    parts = rest.split("\t") if "\t" in rest else rest.split()
    return [p for p in parts if p]


def parse_record(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    status = identity = None
    requested, present = [], []
    directory = None
    sizes: dict[str, int] = {}
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "\t" not in line:
            raise ValueError(f"{path}:{lineno}: expected key<TAB>value")
        key, rest = line.split("\t", 1)
        key, rest = key.strip(), rest.strip()
        if key not in KNOWN:
            raise ValueError(f"{path}:{lineno}: unknown field {key!r}")
        if key == "status":
            if not rest:
                raise ValueError(f"{path}:{lineno}: empty status")
            status = rest
        elif key == "identity":
            if not rest:
                raise ValueError(f"{path}:{lineno}: empty identity")
            identity = rest
        elif key == "requested":
            requested.extend(split_values(rest))
        elif key == "present":
            present.extend(split_values(rest))
        elif key == "dir":
            if not rest:
                raise ValueError(f"{path}:{lineno}: empty dir")
            directory = Path(rest)
        elif key == "bytes":
            parts = rest.split("\t")
            if len(parts) != 2:
                raise ValueError(f"{path}:{lineno}: bytes needs name<TAB>size")
            name, size_s = parts[0], parts[1]
            sizes[name] = int(size_s)
    if status is None:
        raise ValueError(f"{path}: missing status")
    if identity is None:
        raise ValueError(f"{path}: missing identity")
    return {
        "status": status,
        "identity": identity,
        "requested": unique(requested),
        "present": unique(present),
        "dir": directory,
        "sizes": sizes,
        "source": str(path),
    }


def path_in_dir(root: Path, name: str) -> Path:
    candidate = Path(name)
    if candidate.is_absolute():
        return candidate
    return root / candidate


def observe(build: dict, override: Path | None = None) -> dict:
    root = override if override is not None else build["dir"]
    if root is None:
        return build
    if not root.is_dir():
        raise ValueError(f"not a directory: {root}")
    present = []
    sizes = dict(build["sizes"])
    for name in build["requested"]:
        path = path_in_dir(root, name)
        if path.exists():
            present.append(name)
            try:
                sizes[name] = path.stat().st_size
            except OSError:
                pass
    build["present"] = unique(present)
    build["dir"] = root
    build["sizes"] = sizes
    return build


def replica_compare(first: dict, second: dict) -> dict:
    extra = [n for n in second["requested"] if n not in set(first["requested"])]
    missing = [n for n in second["requested"] if n not in set(second["present"])]
    stubs = [
        n
        for n in extra
        if n in set(second["present"]) and second["sizes"].get(n, -1) == 0
    ]
    same = first["identity"] == second["identity"]
    if not same:
        verdict, omitted = "identity-changed", []
    elif second["status"] == "FRESH" and missing:
        verdict, omitted = "FRESH-but-missing", list(missing)
    elif second["status"] == "FRESH" and stubs:
        verdict, omitted = "FRESH-but-stub", list(stubs)
    elif second["status"] == "FRESH":
        verdict, omitted = "FRESH-complete", []
    else:
        verdict, omitted = "rebuilt", []
    return {
        "verdict": verdict,
        "same_identity": same,
        "requested_extra": extra,
        "missing": missing,
        "stub": stubs,
        "omitted_from_identity": omitted,
        "first": first,
        "second": second,
    }


def fmt_list(items):
    return "\t".join(items) if items else "none"


def replica_format(result: dict) -> str:
    first, second = result["first"], result["second"]
    lines = [
        f"verdict\t{result['verdict']}",
        f"identity\t{second['identity']}",
        f"same_identity\t{str(result['same_identity']).lower()}",
        f"first_status\t{first['status']}",
        f"second_status\t{second['status']}",
        f"requested_extra\t{fmt_list(result['requested_extra'])}",
        f"missing\t{fmt_list(result['missing'])}",
        f"stub\t{fmt_list(result['stub'])}",
        f"omitted_from_identity\t{fmt_list(result['omitted_from_identity'])}",
    ]
    return "\n".join(lines) + "\n"


def replica_run(first_path: Path, second_path: Path, extra_args=None) -> tuple[str, str, int]:
    extra_args = extra_args or []
    first_dir = second_dir = None
    args = list(extra_args)
    i = 0
    leftover = []
    while i < len(args):
        if args[i] == "--dir" and i + 1 < len(args):
            second_dir = Path(args[i + 1])
            i += 2
        elif args[i] == "--first-dir" and i + 1 < len(args):
            first_dir = Path(args[i + 1])
            i += 2
        else:
            leftover.append(args[i])
            i += 1
    try:
        first = parse_record(first_path)
        second = parse_record(second_path)
        observe(first, first_dir)
        observe(second, second_dir)
        out = replica_format(replica_compare(first, second))
        return out, "", 0
    except (OSError, ValueError) as err:
        return "", f"freshmiss: {err}\n", 1


def cli_run(first_path: Path, second_path: Path, extra_args=None) -> tuple[str, str, int]:
    cmd = [sys.executable, str(CLI), str(first_path), str(second_path)]
    if extra_args:
        cmd.extend(extra_args)
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(CLI.parent))
    return proc.stdout, proc.stderr, proc.returncode


def write_rec(path: Path, text: str) -> Path:
    path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")
    return path


def rec(path: Path, **fields) -> Path:
    lines = []
    for k, v in fields.items():
        if isinstance(v, (list, tuple)):
            lines.append(k + "\t" + "\t".join(map(str, v)))
        else:
            lines.append(f"{k}\t{v}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def compare_pair(name: str, first: Path, second: Path, extra_args=None) -> dict:
    c_out, c_err, c_rc = cli_run(first, second, extra_args)
    r_out, r_err, r_rc = replica_run(first, second, extra_args)
    return {
        "name": name,
        "stdout_eq": c_out == r_out,
        "rc_eq": c_rc == r_rc,
        "cli_rc": c_rc,
        "rep_rc": r_rc,
        "cli_out": c_out,
        "rep_out": r_out,
        "cli_err": c_err,
        "rep_err": r_err,
    }


def main() -> int:
    results = []
    td = Path(tempfile.mkdtemp(prefix="freshmiss2-", dir=str(SCRATCH)))

    first011 = FIX / "specimen-011-first.rec"
    second011 = FIX / "specimen-011-second.rec"
    results.append(compare_pair("owned-011", first011, second011))

    # swap / same twice
    results.append(compare_pair("swap-011", second011, first011))
    results.append(compare_pair("same-first-twice", first011, first011))
    results.append(compare_pair("same-second-twice", second011, second011))

    # FRESH-complete declared
    f = rec(td / "c1.rec", status="BUILT", identity="k", requested=["out.bin"], present=["out.bin"])
    s = rec(
        td / "c2.rec",
        status="FRESH",
        identity="k",
        requested=["out.bin", "out.sbom"],
        present=["out.bin", "out.sbom"],
    )
    results.append(compare_pair("fresh-complete-declared", f, s))

    # stub bytes 0
    s = write_rec(
        td / "stub.rec",
        "status\tFRESH\nidentity\tk\nrequested\tout.bin\tout.sbom\npresent\tout.bin\tout.sbom\nbytes\tout.sbom\t0\n",
    )
    results.append(compare_pair("stub-bytes-0", f, s))

    # produced bytes 12
    s = write_rec(
        td / "prod.rec",
        "status\tFRESH\nidentity\tk\nrequested\tout.bin\tout.sbom\npresent\tout.bin\tout.sbom\nbytes\tout.sbom\t12\n",
    )
    results.append(compare_pair("produced-bytes-12", f, s))

    # missing wins over stub
    s = write_rec(
        td / "misswin.rec",
        "status\tFRESH\nidentity\tk\nrequested\tout.bin\tout.sbom\tout.cdx\npresent\tout.bin\tout.sbom\nbytes\tout.sbom\t0\n",
    )
    results.append(compare_pair("missing-wins-over-stub", f, s))

    # vanished primary, no extra
    s = rec(td / "vanish.rec", status="FRESH", identity="k", requested=["out.bin"])
    results.append(compare_pair("vanished-primary-no-extra", f, s))

    # extra present, original gone
    s = rec(
        td / "origmiss.rec",
        status="FRESH",
        identity="k",
        requested=["out.bin", "out.sbom"],
        present=["out.sbom"],
    )
    results.append(compare_pair("extra-present-orig-gone", f, s))

    # filename none missing / present
    s = rec(
        td / "none-miss.rec",
        status="FRESH",
        identity="k",
        requested=["out.bin", "none"],
        present=["out.bin"],
    )
    results.append(compare_pair("filename-none-missing", f, s))
    s = rec(
        td / "none-pres.rec",
        status="FRESH",
        identity="k",
        requested=["out.bin", "none"],
        present=["out.bin", "none"],
    )
    results.append(compare_pair("filename-none-present", f, s))

    # forgotten present
    s = rec(td / "nopres.rec", status="FRESH", identity="k", requested=["out.bin", "out.sbom"])
    results.append(compare_pair("forgotten-present", f, s))

    # empty present line
    s = write_rec(td / "emptypres.rec", "status\tFRESH\nidentity\tk\nrequested\tout.bin\npresent\t\n")
    results.append(compare_pair("empty-present-tab", f, s))

    # identity-changed
    s = rec(
        td / "idchg.rec",
        status="FRESH",
        identity="OTHER",
        requested=["out.bin", "out.sbom"],
        present=["out.bin"],
    )
    results.append(compare_pair("identity-changed", f, s))

    # rebuilt
    s = rec(
        td / "reb.rec",
        status="BUILT",
        identity="k",
        requested=["out.bin", "out.sbom"],
        present=["out.bin"],
    )
    results.append(compare_pair("rebuilt-missing", f, s))

    # status vocabulary
    for st, name in [
        ("fresh", "status-fresh-lc"),
        ("Fresh", "status-Fresh"),
        ("CACHED", "status-CACHED"),
        ("HIT", "status-HIT"),
        ("UP-TO-DATE", "status-UPTODATE"),
        ("SUCCESS", "status-SUCCESS"),
        ("FRESH ", "status-FRESH-trailspace"),
    ]:
        s = rec(
            td / f"{name}.rec",
            status=st,
            identity="k",
            requested=["out.bin", "out.sbom"],
            present=["out.bin"],
        )
        results.append(compare_pair(name, f, s))

    # extra tab on status
    s = write_rec(
        td / "statustab.rec",
        "status\tFRESH\tignored\nidentity\tk\nrequested\tout.bin\tout.sbom\npresent\tout.bin\n",
    )
    results.append(compare_pair("status-extra-tab", f, s))

    # duplicate status last-win
    s = write_rec(
        td / "dupstat.rec",
        "status\tBUILT\nstatus\tFRESH\nidentity\tk\nrequested\tout.bin\tout.sbom\npresent\tout.bin\n",
    )
    results.append(compare_pair("dup-status-lastwin", f, s))

    # zwsp identity
    s = write_rec(
        td / "zwsp.rec",
        "status\tFRESH\nidentity\tk\u200b\nrequested\tout.bin\tout.sbom\npresent\tout.bin\n",
    )
    results.append(compare_pair("zwsp-identity", f, s))

    # path spelling
    s = rec(
        td / "dotslash.rec",
        status="FRESH",
        identity="k",
        requested=["out.bin", "./out.sbom"],
        present=["out.bin", "out.sbom"],
    )
    results.append(compare_pair("dotslash-extra", f, s))

    # space-split grammar
    s = write_rec(
        td / "spacesplit.rec",
        "status\tFRESH\nidentity\tk\nrequested\tout.bin my file.sbom\npresent\tout.bin\n",
    )
    results.append(compare_pair("space-split", f, s))

    # three extras
    s = rec(
        td / "three.rec",
        status="FRESH",
        identity="k",
        requested=["out.bin", "a", "b", "c"],
        present=["out.bin"],
    )
    results.append(compare_pair("three-extras", f, s))

    # unicode extra
    s = rec(
        td / "uni.rec",
        status="FRESH",
        identity="k",
        requested=["out.bin", "出.sbom"],
        present=["out.bin"],
    )
    results.append(compare_pair("unicode-extra", f, s))

    # env/flag fields (MUTATE.md 1/2 not implemented)
    s = write_rec(
        td / "env.rec",
        "status\tFRESH\nidentity\tk\nrequested\tout.bin\npresent\tout.bin\nenv\tPYTHONEXECUTABLE\n",
    )
    results.append(compare_pair("unknown-env-field", f, s))
    s = write_rec(
        td / "flag.rec",
        "status\tFRESH\nidentity\tk\nrequested\tout.bin\npresent\tout.bin\nflag\t-Zpublic-dependency\n",
    )
    results.append(compare_pair("unknown-flag-field", f, s))

    # --dir observed missing / complete / stub / dir-occupies / escape
    outdir = td / "out"
    outdir.mkdir()
    (outdir / "out.bin").write_text("bin:hello", encoding="utf-8")
    s = rec(
        td / "dir-lie.rec",
        status="FRESH",
        identity="k",
        requested=["out.bin", "out.sbom"],
        present=["out.bin", "out.sbom"],
    )
    results.append(compare_pair("dir-override-lying-present", f, s, ["--dir", str(outdir)]))

    (outdir / "out.sbom").write_text("", encoding="utf-8")  # 0 bytes
    results.append(compare_pair("dir-observed-stub-0byte", f, s, ["--dir", str(outdir)]))

    (outdir / "out.sbom").write_text("notempty", encoding="utf-8")
    results.append(compare_pair("dir-observed-produced", f, s, ["--dir", str(outdir)]))

    (outdir / "out.sbom").unlink()
    (outdir / "out.sbom").mkdir()
    results.append(compare_pair("dir-occupies-directory", f, s, ["--dir", str(outdir)]))
    (outdir / "out.sbom").rmdir()

    s = rec(
        td / "escape.rec",
        status="FRESH",
        identity="k",
        requested=["../../../../../../../../etc/passwd"],
        present=[],
    )
    f2 = rec(td / "f2.rec", status="BUILT", identity="k", requested=["out.bin"], present=["out.bin"])
    results.append(compare_pair("dir-escape-passwd", f2, s, ["--dir", str(outdir)]))

    # broken symlink
    os.symlink(str(outdir / "nope-target"), outdir / "out.sbom")
    s = rec(
        td / "broken.rec",
        status="FRESH",
        identity="k",
        requested=["out.bin", "out.sbom"],
        present=["out.bin", "out.sbom"],
    )
    results.append(compare_pair("dir-broken-symlink", f, s, ["--dir", str(outdir)]))
    (outdir / "out.sbom").unlink()

    # char device via /dev/null symlink
    os.symlink("/dev/null", outdir / "out.sbom")
    results.append(compare_pair("dir-symlink-devnull", f, s, ["--dir", str(outdir)]))
    (outdir / "out.sbom").unlink()

    # identity-changed with stub bytes
    s = write_rec(
        td / "idstub.rec",
        "status\tFRESH\nidentity\tOTHER\nrequested\tout.bin\tout.sbom\npresent\tout.bin\tout.sbom\nbytes\tout.sbom\t0\n",
    )
    results.append(compare_pair("identity-changed-stub", f, s))

    # stub on primary not extra
    s = write_rec(
        td / "primstub.rec",
        "status\tFRESH\nidentity\tk\nrequested\tout.bin\tout.sbom\npresent\tout.bin\tout.sbom\nbytes\tout.bin\t0\n",
    )
    results.append(compare_pair("stub-on-primary-not-extra", f, s))

    # extra not present, bytes 0 still missing
    s = write_rec(
        td / "missbytes.rec",
        "status\tFRESH\nidentity\tk\nrequested\tout.bin\tout.sbom\npresent\tout.bin\nbytes\tout.sbom\t0\n",
    )
    results.append(compare_pair("bytes0-but-not-present", f, s))

    # bytes -1
    s = write_rec(
        td / "neg.rec",
        "status\tFRESH\nidentity\tk\nrequested\tout.bin\tout.sbom\npresent\tout.bin\tout.sbom\nbytes\tout.sbom\t-1\n",
    )
    results.append(compare_pair("bytes-neg1", f, s))

    # bytes 1
    s = write_rec(
        td / "one.rec",
        "status\tFRESH\nidentity\tk\nrequested\tout.bin\tout.sbom\npresent\tout.bin\tout.sbom\nbytes\tout.sbom\t1\n",
    )
    results.append(compare_pair("produced-bytes-1", f, s))

    # comments drop extra
    s = write_rec(
        td / "comment.rec",
        "status\tFRESH\nidentity\tk\nrequested\tout.bin\n#requested\tout.sbom\npresent\tout.bin\n",
    )
    results.append(compare_pair("comment-drops-extra", f, s))

    # CRLF
    s = write_rec(
        td / "crlf.rec",
        "status\tFRESH\r\nidentity\tk\r\nrequested\tout.bin\tout.sbom\r\npresent\tout.bin\r\n",
    )
    results.append(compare_pair("crlf", f, s))

    # missing status
    s = write_rec(td / "nostat.rec", "identity\tk\nrequested\tout.bin\n")
    results.append(compare_pair("missing-status", f, s))

    # unknown field
    s = write_rec(td / "magic.rec", "status\tFRESH\nidentity\tk\nmagic\tyes\n")
    results.append(compare_pair("unknown-magic", f, s))

    # empty file
    s = write_rec(td / "empty.rec", "")
    results.append(compare_pair("empty-file", f, s))

    # native fixture log
    s = write_rec(
        td / "log.rec",
        "first BUILT extra_exists False key 9280cc7e16e9\nsecond FRESH extra_exists False key 9280cc7e16e9\n",
    )
    results.append(compare_pair("native-log", f, s))

    # FRESH-but-env-omitted as identity-same complete (no extra)
    s = rec(td / "envsame.rec", status="FRESH", identity="k", requested=["out.bin"], present=["out.bin"])
    results.append(compare_pair("same-req-fresh-complete", f, s))

    # two different hashes, extra missing
    fdiff = rec(td / "fd.rec", status="BUILT", identity="aaa", requested=["out.bin"], present=["out.bin"])
    sdiff = rec(
        td / "sd.rec",
        status="FRESH",
        identity="bbb",
        requested=["out.bin", "out.sbom"],
        present=["out.bin"],
    )
    results.append(compare_pair("two-hashes-differ", fdiff, sdiff))

    # two identical hashes, extra missing (owned shape)
    fsame = rec(
        td / "fs.rec", status="BUILT", identity="9280cc7e16e9", requested=["out.bin"], present=["out.bin"]
    )
    ssame = rec(
        td / "ss.rec",
        status="FRESH",
        identity="9280cc7e16e9",
        requested=["out.bin", "out.sbom"],
        present=["out.bin"],
    )
    results.append(compare_pair("two-hashes-same-missing", fsame, ssame))

    # two identical hashes, extra stub
    sstub = write_rec(
        td / "sstub.rec",
        "status\tFRESH\nidentity\t9280cc7e16e9\nrequested\tout.bin\tout.sbom\npresent\tout.bin\tout.sbom\nbytes\tout.sbom\t0\n",
    )
    results.append(compare_pair("two-hashes-same-stub", fsame, sstub))

    # two identical hashes, extra produced
    sprod = write_rec(
        td / "sprod.rec",
        "status\tFRESH\nidentity\t9280cc7e16e9\nrequested\tout.bin\tout.sbom\npresent\tout.bin\tout.sbom\nbytes\tout.sbom\t12\n",
    )
    results.append(compare_pair("two-hashes-same-produced", fsame, sprod))

    # --dir not a directory
    results.append(compare_pair("dir-not-dir", f, s, ["--dir", str(td / "nope")]))

    # first-dir
    firstdir = td / "firstout"
    firstdir.mkdir()
    (firstdir / "out.bin").write_text("x", encoding="utf-8")
    fdir = rec(td / "fdir.rec", status="BUILT", identity="k", requested=["out.bin"])
    results.append(compare_pair("first-dir-observe", fdir, ssame, ["--first-dir", str(firstdir)]))

    # NUL in identity
    s = write_rec(
        td / "nul.rec",
        "status\tFRESH\nidentity\tk\x00x\nrequested\tout.bin\tout.sbom\npresent\tout.bin\n",
    )
    results.append(compare_pair("nul-identity", f, s))

    # bytes on unrequested name
    s = write_rec(
        td / "unreq.rec",
        "status\tFRESH\nidentity\tk\nrequested\tout.bin\tout.sbom\npresent\tout.bin\tout.sbom\nbytes\tout.cdx\t0\n",
    )
    results.append(compare_pair("bytes-unrequested-name", f, s))

    # FRESH-complete no extra
    s = rec(td / "noex.rec", status="FRESH", identity="k", requested=["out.bin"], present=["out.bin"])
    results.append(compare_pair("no-extra-fresh-complete", f, s))

    # rebuilt with stub bytes (not FRESH)
    s = write_rec(
        td / "rebstub.rec",
        "status\tBUILT\nidentity\tk\nrequested\tout.bin\tout.sbom\npresent\tout.bin\tout.sbom\nbytes\tout.sbom\t0\n",
    )
    results.append(compare_pair("rebuilt-with-stub-bytes", f, s))

    # lowercase fresh with stub
    s = write_rec(
        td / "freshstub.rec",
        "status\tfresh\nidentity\tk\nrequested\tout.bin\tout.sbom\npresent\tout.bin\tout.sbom\nbytes\tout.sbom\t0\n",
    )
    results.append(compare_pair("fresh-lc-with-stub", f, s))

    # CACHED with stub
    s = write_rec(
        td / "cachedstub.rec",
        "status\tCACHED\nidentity\tk\nrequested\tout.bin\tout.sbom\npresent\tout.bin\tout.sbom\nbytes\tout.sbom\t0\n",
    )
    results.append(compare_pair("cached-with-stub", f, s))

    ok = 0
    mismatches = []
    for r in results:
        match = r["stdout_eq"] and r["rc_eq"]
        if match:
            ok += 1
        else:
            mismatches.append(r)
        print(
            f"{r['name']}\tstdout_eq={r['stdout_eq']}\trc_eq={r['rc_eq']}\tcli_rc={r['cli_rc']}\trep_rc={r['rep_rc']}"
        )
        if not match:
            print("  CLI_OUT:", repr(r["cli_out"][:400]))
            print("  REP_OUT:", repr(r["rep_out"][:400]))
            print("  CLI_ERR:", repr(r["cli_err"][:300]))
            print("  REP_ERR:", repr(r["rep_err"][:300]))

    print(f"\nREPLICA {ok}/{len(results)} byte-identical stdout+rc")
    print(f"MISMATCHES {len(mismatches)}")
    summary = td / "replica-summary.txt"
    summary.write_text(
        f"ok={ok} total={len(results)} mismatches={len(mismatches)}\n"
        + "\n".join(
            f"{r['name']} stdout_eq={r['stdout_eq']} rc_eq={r['rc_eq']} cli_rc={r['cli_rc']}"
            for r in results
        )
        + "\n",
        encoding="utf-8",
    )
    return 0 if not mismatches else 1


if __name__ == "__main__":
    raise SystemExit(main())
