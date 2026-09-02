#!/usr/bin/env python3
"""Host attacks on post-MUTATE envlayers. Writes attack.log."""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

RUN = Path("/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112")
CLI = RUN / "lineages/candidate-envlayers/envlayers"
WT = Path("/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-envlayers-envlayers/envlayers")
SCRATCH = Path(__file__).resolve().parent
LOG = SCRATCH / "attack.log"

KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def log(msg: str) -> None:
    LOG.write_text(LOG.read_text(encoding="utf-8") + msg + "\n", encoding="utf-8") if LOG.exists() else LOG.write_text(msg + "\n", encoding="utf-8")
    print(msg)


def parse_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        parts = line.split("\t")
        rows[parts[0]] = parts
    return rows


def run(args: list[str], *, env: dict[str, str] | None = None, extra_env: dict | None = None) -> subprocess.CompletedProcess[str]:
    base = os.environ.copy()
    base.pop("KEY", None)
    base.pop("OTHER", None)
    if extra_env:
        for k, v in extra_env.items():
            if v is None:
                base.pop(k, None)
            else:
                base[k] = v
    if env is not None:
        # env is the subprocess env entirely if we want, but we overlay
        base.update({k: v for k, v in env.items() if v is not None})
        for k, v in env.items():
            if v is None:
                base.pop(k, None)
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        check=False,
        capture_output=True,
        text=True,
        env=base,
    )


def write_env(name: str, text: str | bytes) -> Path:
    path = SCRATCH / name
    if isinstance(text, bytes):
        path.write_bytes(text)
    else:
        path.write_text(text, encoding="utf-8")
    return path


# --- reconstruction of the two policies + declared grammar (THIN_WRAPPER probe) ---

def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        inner = value[1:-1]
        if value[0] == '"':
            inner = (
                inner.replace(r"\\", "\0")
                .replace(r"\"", '"')
                .replace(r"\n", "\n")
                .replace("\0", "\\")
            )
        return inner
    return value


def iter_assignments(env_text: str):
    text = env_text[1:] if env_text.startswith("\ufeff") else env_text
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export") and (len(line) == 6 or line[6].isspace()):
            line = line[6:].lstrip()
            if not line:
                raise ValueError(f"not an assignment: {raw}")
        if "=" not in line:
            raise ValueError(f"not an assignment: {raw}")
        key, _, value = line.partition("=")
        key = key.strip()
        value = _unquote(value.strip())
        if not key:
            raise ValueError(f"empty key in {raw!r}")
        if not KEY_RE.match(key):
            raise ValueError(f"bad key: {key!r}")
        if "\0" in key or "\0" in value:
            raise ValueError(f"nul in assignment: {raw!r}")
        yield key, value


def replica_layers(key, *, inherited, file_text, process_env, inherited_origins=None, process_source="os.environ"):
    origins = inherited_origins or {name: "caller" for name in inherited}
    events = [] if file_text is None else list(iter_assignments(file_text))
    file_map = None if file_text is None else {}
    if file_text is not None:
        for k, v in events:
            file_map[k] = v
    skip = dict(inherited)
    assign = dict(inherited)
    if file_text is not None:
        for k, v in events:
            if v:
                skip[k] = v
            assign[k] = v
    key_events = [(k, v) for k, v in events if k == key]
    nonempty = [v for _, v in key_events if v]
    inherited_val = inherited.get(key) if key in inherited else None
    file_val = None if file_map is None else (file_map.get(key) if key in file_map else None)
    skip_val = skip.get(key) if key in skip else None
    assign_val = assign.get(key) if key in assign else None
    if key not in process_env:
        process_val = None
        process_presence = "unset"
    else:
        process_val = process_env[key]
        process_presence = "empty" if process_val == "" else "present"
    if file_text is None:
        file_presence, file_source = "omitted", "none"
    elif file_val is None:
        file_presence, file_source = "absent", "text"
    elif file_val == "":
        file_presence, file_source = "empty-assignment", "text"
    else:
        file_presence, file_source = "value", "text"
    if nonempty:
        skip_source = "file"
    elif key in inherited:
        skip_source = "inherited"
    else:
        skip_source = "none"
    if key_events:
        assign_source = "file-empty" if key_events[-1][1] == "" else "file"
    elif key in inherited:
        assign_source = "inherited"
    else:
        assign_source = "none"
    inherited_source = "none" if inherited_val is None else origins.get(key, "caller")

    def pres(v):
        if v is None:
            return "absent"
        if v == "":
            return "empty"
        return "present"

    VALUE_CAP = 256

    def drepr(v):
        if v is None:
            return "None"
        shown = v if len(v) <= VALUE_CAP else v[:VALUE_CAP] + "…"
        return repr(shown)

    lines = [f"key\t{key}\tquery\t"]
    for name, val, pr, src in (
        ("inherited", inherited_val, pres(inherited_val), inherited_source),
        ("file", file_val, file_presence, file_source),
        ("skip_empty", skip_val, pres(skip_val), skip_source),
        ("assign", assign_val, pres(assign_val), assign_source),
        ("process", process_val, process_presence, process_source),
    ):
        lines.append(f"{name}\t{drepr(val)}\t{pr}\t{src}")
    lines.append(f"file_n\t{len(key_events)}\tassignments\t")
    lines.append(f"policies_disagree\t{str(skip_val != assign_val).lower()}\t\t")
    return "\n".join(lines) + "\n"


def case(title: str) -> None:
    log(f"\n===== {title} =====")


def main() -> int:
    if LOG.exists():
        LOG.unlink()
    LOG.write_text("", encoding="utf-8")

    identical = 0
    differ = 0
    notes: list[str] = []

    def compare(title, args, *, file_text=None, inherited=None, process=None, extra_env=None, expect_rc=0):
        nonlocal identical, differ
        inherited = inherited or {}
        process = process if process is not None else {}
        extra_env = extra_env or {}
        cli_args = list(args)
        path = None
        if file_text is not None:
            path = write_env("case.env", file_text)
            cli_args = ["--file", str(path), *cli_args]
        for k, v in inherited.items():
            cli_args = ["--inherited", f"{k}={v}", *cli_args]
        proc = run(cli_args, extra_env=extra_env)
        try:
            replica = replica_layers(
                cli_args[-1] if cli_args else "KEY",
                inherited=inherited,
                file_text=file_text,
                process_env=process if process is not None else {},
                process_source="os.environ" if not any(a == "--process" or a.startswith("--process") for a in args) else "injected",
            )
        except ValueError as err:
            replica = f"PARSE_ERROR {err}"
        match = proc.stdout == replica and proc.returncode == expect_rc
        if match:
            identical += 1
            flag = "IDENTICAL"
        else:
            differ += 1
            flag = "DIFFER"
        log(f"{flag} {title} rc={proc.returncode} expect={expect_rc}")
        if not match:
            log("STDOUT:\n" + proc.stdout)
            log("STDERR:\n" + proc.stderr)
            log("REPLICA:\n" + replica)
        return proc

    case("owned 010 empty assignment")
    p = compare(
        "010 KEY=",
        ["KEY"],
        file_text="KEY=\nOTHER=2\n",
        inherited={"KEY": "/x", "OTHER": "1"},
        process={},
        extra_env={"KEY": None},
    )
    rows = parse_rows(p.stdout)
    log(repr(p.stdout))
    log(f"file={rows.get('file')} skip={rows.get('skip_empty')} assign={rows.get('assign')} process={rows.get('process')}")

    case("duplicate assignment events")
    p = compare(
        "dup fromfile then empty",
        ["KEY"],
        file_text="KEY=fromfile\nKEY=\n",
        inherited={"KEY": "/x"},
        process={},
    )
    log(repr(p.stdout))

    case("quoted empty")
    p = compare("KEY=\"\"", ["KEY"], file_text='KEY=""\n', inherited={"KEY": "/x"}, process={})
    log(repr(p.stdout))

    case("default inherited not process copy")
    p = run(["KEY"], extra_env={"KEY": "live"})
    rows = parse_rows(p.stdout)
    log(repr(p.stdout))
    log(f"inherited={rows.get('inherited')} process={rows.get('process')} inherit_src={rows.get('inherited')}")
    assert rows["inherited"][1] == "None"
    assert rows["process"][1] == "'live'"
    notes.append("default inherited is NOT os.environ copy")

    case("process empty vs unset")
    unset = run(["KEY"], extra_env={"KEY": None})
    empty = run(["KEY"], extra_env={"KEY": ""})
    log("UNSET:\n" + repr(unset.stdout))
    log("EMPTY:\n" + repr(empty.stdout))
    u = parse_rows(unset.stdout)
    e = parse_rows(empty.stdout)
    notes.append(f"process unset {u['process']} vs empty {e['process']}")

    case("printenv host empty vs unset")
    pe_unset = subprocess.run(["env", "-u", "KEY", "printenv", "KEY"], capture_output=True, text=True)
    pe_empty = subprocess.run(["env", "KEY=", "printenv", "KEY"], capture_output=True, text=True)
    pe_set = subprocess.run(["env", "KEY=/x", "printenv", "KEY"], capture_output=True, text=True)
    log(f"printenv unset rc={pe_unset.returncode} out={pe_unset.stdout!r}")
    log(f"printenv empty rc={pe_empty.returncode} out={pe_empty.stdout!r}")
    log(f"printenv set rc={pe_set.returncode} out={pe_set.stdout!r}")

    case("host skip-empty loader then printenv cannot see file KEY=")
    # Simulate: inherited KEY=/x, skip-empty load of KEY=, then printenv
    # After skip-empty, process would still have KEY=/x. printenv shows /x.
    # envlayers with caller-labeled inherited shows file empty-assignment.
    loader = write_env(
        "skip_loader.py",
        "import os\n"
        "from pathlib import Path\n"
        "text = Path('file.env').read_text()\n"
        "env = dict(os.environ)\n"
        "for line in text.splitlines():\n"
        "    if '=' not in line: continue\n"
        "    k,_,v = line.partition('=')\n"
        "    if v: env[k]=v\n"
        "os.execvpe('printenv', ['printenv','KEY'], env)\n",
    )
    write_env("file.env", "KEY=\nOTHER=2\n")
    after = subprocess.run(
        [sys.executable, str(loader)],
        capture_output=True,
        text=True,
        env={**os.environ, "KEY": "/x"},
        cwd=str(SCRATCH),
    )
    log(f"after skip-empty loader printenv KEY rc={after.returncode} out={after.stdout!r} err={after.stderr!r}")
    el = run(["--inherited", "KEY=/x", "--file", str(SCRATCH / "file.env"), "KEY"], extra_env={"KEY": "/x"})
    log("envlayers same situation:\n" + el.stdout)

    case("parser holes")
    holes = [
        ("inline comment", "KEY=value # comment\n", 0),
        ("KEY=0 truthy skip", "KEY=0\n", 0),
        ("KEY=false", "KEY=false\n", 0),
        ("quoted space", 'KEY=" "\n', 0),
        ("unquoted space", "KEY= \n", 0),
        ("CRLF", "KEY=\r\nOTHER=2\r\n", 0),
        ("KEY with dash", "FOO-BAR=1\n", 1),
        ("interpolation", "KEY=${OTHER}\n", 0),
        ("backslash n unquoted", "KEY=a\\nb\n", 0),
        ("double quoted escape", 'KEY="a\\nb"\n', 0),
        ("multiline quote", 'KEY="a\nb"\n', 1),  # newline inside quotes: splitlines breaks
        ("export KEY=", "export KEY=\n", 0),
        ("export KEY=\"\"", 'export KEY=""\n', 0),
        ("KEY+=x bash", "KEY+=x\n", 1),
        ("set KEY=x", "set KEY=x\n", 1),
        ("JSON", '{"KEY":""}\n', 1),
        ("tab indent", "\tKEY = value\n", 0),
        ("spaces around eq", "KEY = value\n", 0),
        ("empty name line", "=novalue\n", 1),
        ("nul in utf8", "KEY=foo\x00bar\n", 1),
        ("KEY=fromfile then KEY=\"\"", 'KEY=fromfile\nKEY=""\n', 0),
        ("KEY=\"\" then KEY=fromfile", 'KEY=""\nKEY=fromfile\n', 0),
        ("three dups", "KEY=a\nKEY=b\nKEY=\n", 0),
        ("comment after value unquoted", "KEY=secret#no\n", 0),
        ("single quote keep backslash", "KEY='a\\n'\n", 0),
        ("BOM+export", "\ufeffexport KEY=\n", 0),
        ("windows path value", "KEY=C:\\Users\\x\n", 0),
        ("unicode value", "KEY=値\n", 0),
        ("posix digit start", "1KEY=x\n", 1),
        ("query FOO=BAR already tested in unit", "KEY=x\n", 0),
    ]
    for name, text, expect in holes:
        path = write_env("hole.env", text)
        proc = run(["--inherited", "KEY=/x", "--file", str(path), "KEY"])
        log(f"HOLE {name!r} rc={proc.returncode} expect_err={expect} stderr={proc.stderr.strip()!r}")
        if proc.returncode == 0:
            r = parse_rows(proc.stdout)
            log(f"  file={r.get('file')} skip={r.get('skip_empty')} assign={r.get('assign')} file_n={r.get('file_n')} skip_src={r.get('skip_empty')}")
        else:
            log(f"  stdout={proc.stdout!r}")

    case("inherited empty vs absent")
    p1 = run(["--inherited", "KEY=", "KEY"])
    p2 = run(["KEY"])
    log("inherited empty:\n" + p1.stdout)
    log("inherited omitted:\n" + p2.stdout)

    case("--from-process-env with file empty")
    p = run(
        ["--from-process-env", "--file", str(write_env("e.env", "KEY=\n")), "KEY"],
        extra_env={"KEY": "/x"},
    )
    log(p.stdout)

    case("both --from-process-env and --no-process-env")
    p = run(["--from-process-env", "--no-process-env", "KEY"], extra_env={"KEY": "live"})
    log(p.stdout)
    r = parse_rows(p.stdout)
    notes.append(f"--from + --no inherited={r['inherited'][1]} process={r['process'][1]}")

    case("huge value cap")
    p = run(["--file", str(write_env("huge.env", "KEY=" + ("H" * 5000) + "\n")), "KEY"])
    r = parse_rows(p.stdout)
    log(f"huge stdout_len={len(p.stdout)} file_field={r['file'][1][:40]}… presence={r['file'][2]}")

    case("display cap 256 vs 257")
    p256 = run(["--file", str(write_env("c256.env", "KEY=" + ("H" * 256) + "\n")), "KEY"])
    p257 = run(["--file", str(write_env("c257.env", "KEY=" + ("H" * 257) + "\n")), "KEY"])
    log(f"256 ellipsis={'…' in p256.stdout} 257 ellipsis={'…' in p257.stdout}")

    case("FIFO timeout")
    fifo = SCRATCH / "fifo.env"
    if fifo.exists():
        fifo.unlink()
    os.mkfifo(fifo)
    try:
        proc = subprocess.run(
            [sys.executable, str(CLI), "--file", str(fifo), "KEY"],
            capture_output=True,
            text=True,
            timeout=1.5,
            env={k: v for k, v in os.environ.items() if k != "KEY"},
        )
        log(f"fifo rc={proc.returncode} out={proc.stdout!r} err={proc.stderr!r}")
    except subprocess.TimeoutExpired:
        log("fifo TIMEOUT 1.5s (blocks in open)")

    case("stdin --file -")
    p = run(["--file", "-", "KEY"])
    log(f"--file - rc={p.returncode} err={p.stderr.strip()!r} out={p.stdout!r}")

    case("/dev/stdin")
    p = subprocess.run(
        [sys.executable, str(CLI), "--file", "/dev/stdin", "KEY"],
        input="KEY=\n",
        capture_output=True,
        text=True,
        env={k: v for k, v in os.environ.items() if k != "KEY"},
    )
    log(f"/dev/stdin rc={p.returncode}\n{p.stdout}{p.stderr}")

    case("symlink file")
    target = write_env("real.env", "KEY=\n")
    link = SCRATCH / "link.env"
    if link.exists() or link.is_symlink():
        link.unlink()
    link.symlink_to(target)
    p = run(["--file", str(link), "--inherited", "KEY=/x", "KEY"])
    log(p.stdout)

    case("direct exec vs python3")
    p1 = subprocess.run(
        [str(CLI), "--inherited", "KEY=/x", "--file", str(write_env("e.env", "KEY=\n")), "KEY"],
        capture_output=True,
        text=True,
        env={k: v for k, v in os.environ.items() if k != "KEY"},
    )
    p2 = run(["--inherited", "KEY=/x", "--file", str(SCRATCH / "e.env"), "KEY"])
    log(f"direct==python3 {p1.stdout == p2.stdout} direct_rc={p1.returncode}")

    case("worktree envlayers.py vs archive")
    p_py = subprocess.run(
        [sys.executable, str(WT / "envlayers.py"), "--inherited", "KEY=/x", "--file", str(write_env("e.env", "KEY=\n")), "KEY"],
        capture_output=True,
        text=True,
        env={k: v for k, v in os.environ.items() if k != "KEY"},
    )
    p_ar = run(["--inherited", "KEY=/x", "--file", str(SCRATCH / "e.env"), "KEY"])
    log(f"envlayers.py==archive {p_py.stdout == p_ar.stdout}")

    case("policies_disagree both absent")
    p = run(["KEY"])
    log(p.stdout)

    case("query empty / equals / dash")
    for k in ("", "FOO=BAR", "FOO-BAR", "1KEY", "KEY\n"):
        p = run([k])
        log(f"query {k!r} rc={p.returncode} err={p.stderr.strip()!r}")

    case("inherited overlay last wins")
    p = run(["--inherited", "KEY=/x", "--inherited", "KEY=/y", "--file", str(write_env("e.env", "KEY=\n")), "KEY"])
    log(p.stdout)

    case("--process last wins")
    p = run(["--process", "KEY=a", "--process", "KEY=", "KEY"], extra_env={"KEY": "live"})
    log(p.stdout)

    case("tabs/newlines in values")
    p = run(["--file", str(write_env("t.env", 'KEY="a\\tb\\n"\n')), "KEY"])
    log(repr(p.stdout))

    case("reconstruction sweep")
    sweep = [
        ("010", "KEY=\nOTHER=2\n", {"KEY": "/x", "OTHER": "1"}, {}, ["KEY"]),
        ("absent", "OTHER=2\n", {"KEY": "/x"}, {}, ["KEY"]),
        ("dup", "KEY=fromfile\nKEY=\n", {"KEY": "/x"}, {}, ["KEY"]),
        ("quoted", 'KEY=""\n', {"KEY": "/x"}, {}, ["KEY"]),
        ("export", "export KEY=exported\n", {"KEY": "/x"}, {}, ["KEY"]),
        ("comment", "# KEY=secret\n", {}, {}, ["KEY"]),
        ("bom", "\ufeffKEY=\n", {"KEY": "/x"}, {}, ["KEY"]),
        ("value", "KEY=fromfile\n", {"KEY": "/x"}, {}, ["KEY"]),
        ("zero", "KEY=0\n", {"KEY": "/x"}, {}, ["KEY"]),
        ("spaceq", 'KEY=" "\n', {"KEY": "/x"}, {}, ["KEY"]),
        ("ws", "KEY= \n", {"KEY": "/x"}, {}, ["KEY"]),
        ("triple", "KEY=a\nKEY=b\nKEY=\n", {"KEY": "/x"}, {}, ["KEY"]),
        ("empty then value", 'KEY=""\nKEY=fromfile\n', {"KEY": "/x"}, {}, ["KEY"]),
        ("omitted file via compare skip", None, {}, {}, ["KEY"]),
    ]
    for name, text, inh, proc, args in sweep:
        compare(name, args, file_text=text, inherited=inh, process=proc)

    # extra replica cases with live process empty/unset via extra_env handled separately
    case("replica vs CLI process empty/unset")
    for label, extra in (("unset", {"KEY": None}), ("empty", {"KEY": ""}), ("live", {"KEY": "live"})):
        p = run(["KEY"], extra_env=extra)
        process_env = {}
        if extra.get("KEY") is not None:
            process_env = {"KEY": extra["KEY"]}
        # CLI process is full os.environ of child. replica using only KEY is wrong for other keys
        # but we only query KEY. For process column, replica needs the child's KEY membership.
        replica = replica_layers("KEY", inherited={}, file_text=None, process_env=process_env)
        match = p.stdout == replica
        log(f"process-{label} match={match}")
        if not match:
            log("CLI " + repr(p.stdout))
            log("REP " + repr(replica))
        if match:
            identical += 1
        else:
            differ += 1

    case("awk/printenv cannot see file empty after skip")
    # Nearest ordinary workflow
    log("printenv after skip-empty shows /x; file KEY= is invisible")
    log("envlayers requires caller to pass --inherited KEY=/x --file file.env")

    case("SUMMARY")
    log(f"replica identical={identical} differ={differ}")
    log("notes: " + " | ".join(notes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
