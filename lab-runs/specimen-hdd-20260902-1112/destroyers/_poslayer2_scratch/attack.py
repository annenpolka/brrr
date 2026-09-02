#!/usr/bin/env python3
"""Host attack: replica vs poslayer CLI. Does not import poslayer."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

SCRATCH = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRATCH))
import replica  # noqa: E402

RUN = Path(
    "/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112"
)
CLI = RUN / "lineages/candidate-poslayer/poslayer"
FIX = RUN / "lineages/candidate-poslayer/fixtures"
S019 = RUN / "specimens/specimen-019/files/override_subst.py"


def run_cli(
    args: list[str],
    *,
    file_text: str | None = None,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    with tempfile.TemporaryDirectory() as tmp:
        cmd = [sys.executable, str(CLI)]
        if file_text is not None:
            path = Path(tmp) / "template.txt"
            path.write_bytes(
                file_text.encode("utf-8") if isinstance(file_text, str) else file_text
            ) if False else None
            # write as given: str uses utf-8
            if isinstance(file_text, bytes):
                path.write_bytes(file_text)
            else:
                path.write_text(file_text, encoding="utf-8")
            cmd.extend(["--file", str(path)])
        cmd.extend(args)
        return subprocess.run(
            cmd, check=False, capture_output=True, text=True, env=env
        )


def run_cli_raw(args: list[str], *, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        check=False,
        capture_output=True,
        text=True,
        input=stdin,
    )


def compare(
    name: str,
    *,
    file_template: str,
    leftover: list[str],
    override: str | None = None,
    token: str = "{posargs}",
    exit_code: int = 0,
    subst_override: bool = False,
) -> dict:
    expected = replica.report(
        file_template,
        leftover,
        override=override,
        token=token,
        exit_code=exit_code,
        subst_override=subst_override,
    )
    args: list[str] = ["--file-template", file_template]
    if override is not None:
        args.extend(["--override", override])
    if token != "{posargs}":
        args.extend(["--token", token])
    if exit_code != 0:
        args.extend(["--exit", str(exit_code)])
    if subst_override:
        args.append("--subst-override")
    args.append("--")
    args.extend(leftover)
    proc = run_cli_raw(args)
    ok = proc.returncode == 0 and proc.stdout == expected and proc.stderr == ""
    return {
        "name": name,
        "ok": ok,
        "rc": proc.returncode,
        "stdout_eq": proc.stdout == expected,
        "stderr_empty": proc.stderr == "",
        "stdout": proc.stdout,
        "expected": expected,
        "stderr": proc.stderr,
    }


CASES = [
    dict(
        name="owned-019",
        file_template="pytest {posargs}",
        leftover=["tests", "src"],
    ),
    dict(
        name="unseen-packages",
        file_template="pytest {packages}",
        leftover=["pkg"],
        token="{packages}",
    ),
    dict(
        name="coincidental-tests",
        file_template="pytest {posargs}",
        leftover=["tests", "src"],
        override="pytest tests {posargs}",
    ),
    dict(
        name="subst-override",
        file_template="pytest {posargs}",
        leftover=["tests", "src"],
        subst_override=True,
    ),
    dict(
        name="leftover-is-token",
        file_template="pytest {posargs}",
        leftover=["{posargs}"],
    ),
    dict(
        name="leftover-is-token-subst-override",
        file_template="pytest {posargs}",
        leftover=["{posargs}"],
        subst_override=True,
    ),
    dict(
        name="quoted-token-override",
        file_template="pytest {posargs}",
        leftover=["tests", "src"],
        override="pytest '{posargs}'",
    ),
    dict(
        name="glued-token",
        file_template="pytest {posargs}-extra",
        leftover=["tests"],
    ),
    dict(
        name="trailing-tb-short",
        file_template="pytest {posargs} --tb=short",
        leftover=["tests", "src"],
    ),
    dict(
        name="trailing-tb-subst-override",
        file_template="pytest {posargs} --tb=short",
        leftover=["tests", "src"],
        subst_override=True,
    ),
    dict(
        name="exit-sticker-1",
        file_template="pytest {posargs}",
        leftover=["tests", "src"],
        exit_code=1,
    ),
    dict(
        name="exit-sticker-neg1",
        file_template="pytest {posargs}",
        leftover=["tests", "src"],
        exit_code=-1,
    ),
    dict(
        name="empty-leftover",
        file_template="pytest {posargs}",
        leftover=[],
    ),
    dict(
        name="leftover-dash",
        file_template="pytest {posargs}",
        leftover=["-"],
    ),
    dict(
        name="override-has-dash-word",
        file_template="pytest {posargs}",
        leftover=["-"],
        override="pytest - {posargs}",
    ),
    dict(
        name="space-in-one-leftover",
        file_template="pytest {posargs}",
        leftover=["tests src"],
    ),
    dict(
        name="override-pytest-no-token",
        file_template="pytest {posargs}",
        leftover=["tests", "src"],
        override="pytest",
    ),
    dict(
        name="override-pytest-no-token-subst",
        file_template="pytest {posargs}",
        leftover=["tests", "src"],
        override="pytest",
        subst_override=True,
    ),
    dict(
        name="unicode-leftover",
        file_template="pytest {posargs}",
        leftover=["テスト"],
    ),
    dict(
        name="unicode-token",
        file_template="pytest {引数}",
        leftover=["tests"],
        token="{引数}",
    ),
    dict(
        name="empty-token",
        file_template="pytest {posargs}",
        leftover=["X"],
        token="",
    ),
    dict(
        name="substring-test",
        file_template="pytest tests",
        leftover=["FOO"],
        token="test",
    ),
    dict(
        name="partial-token-prefix",
        file_template="pytest {posargs}",
        leftover=["X"],
        token="{pos",
    ),
    dict(
        name="double-token",
        file_template="pytest {posargs} {posargs}",
        leftover=["a", "b"],
    ),
    dict(
        name="not-token-yes",
        file_template="pytest not{posargs}yes",
        leftover=["X"],
    ),
    dict(
        name="empty-leftover-entered-file",
        file_template="pytest {posargs}",
        leftover=[],
        subst_override=False,
    ),
    dict(
        name="whitespace-only-template",
        file_template="   ",
        leftover=["tests"],
    ),
    dict(
        name="tab-only-template",
        file_template="\t",
        leftover=["tests"],
    ),
    dict(
        name="empty-override-argv",
        file_template="pytest {posargs}",
        leftover=["tests"],
        override="",
    ),
    dict(
        name="leftover-equals-dash-subst",
        file_template="pytest {posargs}",
        leftover=["-"],
        subst_override=True,
    ),
    dict(
        name="k-flag-leftover",
        file_template="pytest {posargs}",
        leftover=["-k", "test_foo"],
    ),
    dict(
        name="quoted-leftover-item",
        file_template="pytest {posargs}",
        leftover=['"tests src"'],
    ),
    dict(
        name="cafe-leftover",
        file_template="pytest {posargs}",
        leftover=["café"],
    ),
    dict(
        name="same-spelling-override-explicit",
        file_template="pytest {posargs}",
        leftover=["tests", "src"],
        override="pytest {posargs}",
    ),
    dict(
        name="override-literal-plus-flag",
        file_template="pytest {posargs}",
        leftover=["tests"],
        override="pytest {posargs} --tb=short",
    ),
    dict(
        name="token-with-space",
        file_template="pytest POS ARGS",
        leftover=["tests"],
        token="POS ARGS",
    ),
    dict(
        name="duplicate-leftover-word",
        file_template="pytest {posargs}",
        leftover=["tests", "tests"],
    ),
    dict(
        name="in-override-count-one",
        file_template="pytest {posargs}",
        leftover=["pytest", "src"],
        override="pytest {posargs}",
    ),
    dict(
        name="absent-both",
        file_template="pytest",
        leftover=["tests"],
        override="pytest",
    ),
    dict(
        name="exit-0-explicit",
        file_template="pytest {posargs}",
        leftover=["tests", "src"],
        exit_code=0,
    ),
]


def file_cases() -> list[dict]:
    """CLI --file vs replica after one trailing newline strip."""
    out = []
    pairs = [
        ("file-019", "pytest {posargs}\n", ["tests", "src"], "{posargs}"),
        ("file-unseen", "pytest {packages}\n", ["pkg"], "{packages}"),
        ("file-no-nl", "pytest {posargs}", ["tests", "src"], "{posargs}"),
        ("file-two-nl", "pytest {posargs}\n\n", ["tests"], "{posargs}"),
        ("file-crlf", "pytest {posargs}\r\n", ["tests", "src"], "{posargs}"),
    ]
    for name, text, leftover, token in pairs:
        # match CLI read_template: strip one trailing \n only
        tmpl = text[:-1] if text.endswith("\n") else text
        expected = replica.report(tmpl, leftover, token=token)
        args = ["--"] + leftover
        if token != "{posargs}":
            args = ["--token", token] + args
        proc = run_cli(args, file_text=text)
        ok = proc.returncode == 0 and proc.stdout == expected and proc.stderr == ""
        out.append(
            {
                "name": name,
                "ok": ok,
                "rc": proc.returncode,
                "stdout_eq": proc.stdout == expected,
                "stderr_empty": proc.stderr == "",
                "stdout": proc.stdout,
                "expected": expected,
                "stderr": proc.stderr,
            }
        )
    return out


def mutate_leftovers() -> list[str]:
    notes: list[str] = []
    # (1) leftover-is-token still literal
    proc = run_cli_raw(
        ["--file-template", "pytest {posargs}", "--", "{posargs}"]
    )
    notes.append(
        f"leftover-is-token file={_cell(proc.stdout,'file')} entered={_cell(proc.stdout,'entered')} silent={_cell(proc.stdout,'silent')} rc={proc.returncode}"
    )
    proc = run_cli_raw(
        [
            "--file-template",
            "pytest {posargs}",
            "--subst-override",
            "--",
            "{posargs}",
        ]
    )
    notes.append(
        f"leftover-is-token-subst override={_cell(proc.stdout,'override')} entered={_cell(proc.stdout,'entered')} silent={_cell(proc.stdout,'silent')} missed={_cell(proc.stdout,'missed')} rc={proc.returncode}"
    )
    # quoted
    proc = run_cli_raw(
        [
            "--file-template",
            "pytest {posargs}",
            "--override",
            "pytest '{posargs}'",
            "--",
            "tests",
            "src",
        ]
    )
    notes.append(
        f"quoted override={_cell(proc.stdout,'override')} ran_against={_cell(proc.stdout,'ran_against')} silent={_cell(proc.stdout,'silent')}"
    )
    # glued
    proc = run_cli_raw(
        ["--file-template", "pytest {posargs}-extra", "--", "tests"]
    )
    notes.append(
        f"glued file={_cell(proc.stdout,'file')} ran_against={_cell(proc.stdout,'ran_against')} silent={_cell(proc.stdout,'silent')}"
    )
    # ran_against last word
    proc = run_cli_raw(
        ["--file-template", "pytest {posargs} --tb=short", "--", "tests", "src"]
    )
    notes.append(
        f"tb-short override={_cell(proc.stdout,'override')} ran_against={_cell(proc.stdout,'ran_against')} silent={_cell(proc.stdout,'silent')}"
    )
    # exit sticker
    proc = run_cli_raw(
        ["--file-template", "pytest {posargs}", "--exit", "1", "--", "tests", "src"]
    )
    notes.append(
        f"exit-1 exit={_cell(proc.stdout,'exit')} silent={_cell(proc.stdout,'silent')} rc={proc.returncode}"
    )
    # empty leftover still entered file
    proc = run_cli_raw(["--file-template", "pytest {posargs}"])
    notes.append(
        f"empty leftover leftover={_cell(proc.stdout,'leftover')} entered={_cell(proc.stdout,'entered')} silent={_cell(proc.stdout,'silent')}"
    )
    # dash collision
    a = run_cli_raw(["--file-template", "pytest {posargs}"])
    b = run_cli_raw(["--file-template", "pytest {posargs}", "--", "-"])
    notes.append(
        f"empty leftover row={_cell(a.stdout,'leftover')!r} dash leftover row={_cell(b.stdout,'leftover')!r} leftover_eq={_cell(a.stdout,'leftover')==_cell(b.stdout,'leftover')}"
    )
    # override pytest no append
    proc = run_cli_raw(
        [
            "--file-template",
            "pytest {posargs}",
            "--override",
            "pytest",
            "--",
            "tests",
            "src",
        ]
    )
    notes.append(
        f"override-pytest override={_cell(proc.stdout,'override')} missed={_cell(proc.stdout,'missed')} ran_against={_cell(proc.stdout,'ran_against')}"
    )
    # empty token
    proc = run_cli_raw(
        ["--file-template", "pytest {posargs}", "--token", "", "--", "X"]
    )
    notes.append(
        f"empty-token file={_cell(proc.stdout,'file')} rc={proc.returncode} stdout_len={len(proc.stdout)}"
    )
    return notes


def _cell(text: str, name: str) -> str:
    for line in text.splitlines():
        if line.startswith(name + "\t") or line == name:
            return line.split("\t", 1)[1] if "\t" in line else ""
    return "<missing>"


def error_cases() -> list[dict]:
    rows = []
    proc = run_cli_raw([])
    rows.append(("no-args", proc.returncode, proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else ""))
    proc = run_cli_raw(["--file", "/no/such/poslayer.tmpl", "--", "tests"])
    rows.append(("missing-file", proc.returncode, proc.stderr.strip()))
    proc = run_cli_raw(["--file-template", "", "--", "tests"])
    rows.append(("empty-template", proc.returncode, proc.stderr.strip()))
    proc = run_cli_raw(
        ["--file", str(FIX / "019-file.txt"), "--file-template", "pytest {posargs}"]
    )
    rows.append(("both-flags", proc.returncode, proc.stderr.strip()))
    proc = run_cli_raw(["--file", "-", "--", "tests"])
    rows.append(("file-dash", proc.returncode, proc.stderr.strip()))
    proc = run_cli_raw(["--file-template", "pytest {posargs}", "-k", "test_foo"])
    rows.append(("leftover-flag-no-dd", proc.returncode, proc.stderr.strip().splitlines()[-1] if proc.stderr else ""))
    return rows


def fixture_vs_cli() -> dict:
    fx = subprocess.run(
        [sys.executable, str(FIX / "override_subst.py")],
        check=False,
        capture_output=True,
        text=True,
    )
    cli = run_cli_raw(
        ["--file-template", "pytest {posargs}", "--", "tests", "src"]
    )
    spec = subprocess.run(
        [sys.executable, str(S019)],
        check=False,
        capture_output=True,
        text=True,
    )
    return {
        "fixture_rc": fx.returncode,
        "fixture_out": fx.stdout,
        "specimen_out": spec.stdout,
        "fixture_eq_specimen": fx.stdout == spec.stdout,
        "cli_out": cli.stdout,
        "cli_has_expanded": "file\texpanded\tpytest\ttests\tsrc" in cli.stdout,
        "cli_has_literal": "override\tliteral\tpytest\t{posargs}" in cli.stdout,
        "fixture_has_file_argv": "file_argv ['pytest', 'tests', 'src']" in fx.stdout,
        "fixture_has_override_argv": "override_argv ['pytest', '{posargs}']" in fx.stdout,
        "fixture_has_ran": "override_ran_against {posargs}" in fx.stdout,
    }


def printf_owned() -> dict:
    """printf of the harvest TSV the caller already named."""
    text = (
        "token\t{posargs}\n"
        "leftover\ttests\tsrc\n"
        "file\texpanded\tpytest\ttests\tsrc\n"
        "override\tliteral\tpytest\t{posargs}\n"
        "entered\tfile\n"
        "in_override\t-\n"
        "missed\ttests\tsrc\n"
        "ran_against\t{posargs}\n"
        "exit\t0\n"
        "silent\tyes\n"
    )
    proc = run_cli_raw(
        ["--file-template", "pytest {posargs}", "--", "tests", "src"]
    )
    return {
        "eq": proc.stdout == text,
        "cli_sha": _sha(proc.stdout),
        "printf_sha": _sha(text),
        "n": 10,
    }


def _sha(s: str) -> str:
    import hashlib

    return hashlib.sha256(s.encode()).hexdigest()


def inspect_co_names() -> dict:
    import ast

    src = CLI.read_text(encoding="utf-8")
    tree = ast.parse(src)
    out = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in {
            "inspect",
            "token_state",
            "subst",
            "to_argv",
            "leftover_present",
        }:
            names = [n.id for n in ast.walk(node) if isinstance(n, ast.Name)]
            out[node.name] = sorted(set(names))
    # source probes
    out["has_tox"] = "tox" in src.lower()
    out["has_subprocess"] = "subprocess" in src
    out["has_shlex"] = "shlex" in src
    out["has_replace"] = "template.replace" in src
    out["has_split"] = "command.split" in src or ".split()" in src
    return out


def main() -> int:
    results = [compare(**c) for c in CASES]
    results.extend(file_cases())
    ok_n = sum(1 for r in results if r["ok"])
    fail = [r for r in results if not r["ok"]]
    lines = [
        f"replica_vs_cli {ok_n}/{len(results)}",
        f"success_ok {sum(1 for r in results if r['ok'] and r['rc']==0)}",
    ]
    for r in results:
        mark = "OK" if r["ok"] else "FAIL"
        lines.append(
            f"  {mark} {r['name']} rc={r['rc']} stdout_eq={r['stdout_eq']} stderr_empty={r['stderr_empty']}"
        )
        if not r["ok"]:
            lines.append("    --- stdout ---")
            lines.append(r["stdout"][:400])
            lines.append("    --- expected ---")
            lines.append(r["expected"][:400])
            lines.append("    --- stderr ---")
            lines.append(r["stderr"][:200])
    lines.append("=== mutate leftovers ===")
    lines.extend(mutate_leftovers())
    lines.append("=== errors ===")
    for name, rc, err in error_cases():
        lines.append(f"  {name} rc={rc} err={err[:120]}")
    fx = fixture_vs_cli()
    lines.append("=== fixture ===")
    lines.append(f"fixture_eq_specimen={fx['fixture_eq_specimen']}")
    lines.append(f"fixture_has_file_argv={fx['fixture_has_file_argv']}")
    lines.append(f"fixture_has_override_argv={fx['fixture_has_override_argv']}")
    lines.append(f"fixture_has_ran={fx['fixture_has_ran']}")
    lines.append(f"cli_has_expanded={fx['cli_has_expanded']}")
    lines.append(f"cli_has_literal={fx['cli_has_literal']}")
    lines.append("fixture_out:")
    lines.append(fx["fixture_out"])
    pf = printf_owned()
    lines.append("=== printf owned ===")
    lines.append(f"printf_eq_cli={pf['eq']} sha={pf['cli_sha']}")
    lines.append("=== source ===")
    for k, v in inspect_co_names().items():
        lines.append(f"  {k}={v}")
    # 10x printf identity
    n_match = 0
    text = (
        "token\t{posargs}\n"
        "leftover\ttests\tsrc\n"
        "file\texpanded\tpytest\ttests\tsrc\n"
        "override\tliteral\tpytest\t{posargs}\n"
        "entered\tfile\n"
        "in_override\t-\n"
        "missed\ttests\tsrc\n"
        "ran_against\t{posargs}\n"
        "exit\t0\n"
        "silent\tyes\n"
    )
    for _ in range(10):
        proc = run_cli_raw(
            ["--file-template", "pytest {posargs}", "--", "tests", "src"]
        )
        if proc.stdout == text and proc.returncode == 0:
            n_match += 1
    lines.append(f"printf_vs_cli_10={n_match}/10")
    report = "\n".join(lines) + "\n"
    (SCRATCH / "attack.log").write_text(report, encoding="utf-8")
    sys.stdout.write(report)
    return 0 if ok_n == len(results) and not fail else 1


if __name__ == "__main__":
    raise SystemExit(main())
