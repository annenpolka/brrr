#!/usr/bin/env python3
"""Host attacks against post-MUTATE-16 KEEP-17 bindname (destroyer-16). Archive CLI only."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import textwrap
import time
from pathlib import Path

RUN = Path("/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112")
CLI = RUN / "lineages/candidate-bind/bindname"
SCRATCH = RUN / "destroyers/_bindname19_scratch"
SPEC013 = RUN / "specimens/specimen-013/files"
SPEC012 = RUN / "specimens/specimen-012/files"

AST_LEFTOVER = "def parse(x):\n    return ('leftover-ast', x)\n"
PARSE_MOVED = "def parse(x):\n    return ('moved', x.strip())\n"
UTIL_LEGACY = "def parse(x):\n    return ('legacy', x)\n"

DIVERGES: list[tuple[str, str]] = []
PARKS: list[tuple[str, str]] = []
HONOR: dict[str, bool] = {}


def banner(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def run_cli(args, *, cwd=None, timeout=8, stdin=None):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        check=False,
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=timeout,
        input=stdin,
    )


def honesty(code: str, *, cwd: str, timeout=8):
    return subprocess.run(
        [sys.executable, "-c", code],
        check=False,
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=timeout,
    )


def show(proc, label="cli"):
    print(f"-- {label} rc={proc.returncode}")
    if proc.stdout:
        print("STDOUT:")
        print(proc.stdout, end="" if proc.stdout.endswith("\n") else "\n")
    else:
        print("STDOUT: <empty>")
    if proc.stderr:
        print("STDERR:")
        print(proc.stderr, end="" if proc.stderr.endswith("\n") else "\n")


def write_fixture(tmp: str, files: dict[str, str | bytes]) -> Path:
    root = Path(tmp)
    for name, body in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(body, bytes):
            path.write_bytes(body)
        else:
            path.write_text(body, encoding="utf-8")
    return root


def list_source_for(listed_stdout: str, mod: str) -> str:
    for row in listed_stdout.split("\n\n"):
        if f"bind\t{mod}.parse" in row:
            return row
    return ""


def list_has_bind(listed_stdout: str, bind: str) -> bool:
    return f"bind\t{bind}" in listed_stdout


def mark_diverge(tag: str, detail: str) -> None:
    DIVERGES.append((tag, detail))
    print(f"DIVERGE {tag}: {detail}")


def mark_park(tag: str, detail: str) -> None:
    PARKS.append((tag, detail))
    print(f"PARK {tag}: {detail}")


def if_both(live: str, dead: str | None = None) -> str:
    body = f"    def parse(x):\n        return {live!r}\n"
    if dead is not None:
        body += f"else:\n    def parse(x):\n        return {dead!r}\n"
    return body


def check_list_vs_honesty(
    tmp: str,
    mod: str,
    *,
    listed: subprocess.CompletedProcess | None = None,
    declared_park: bool = False,
) -> None:
    hon = honesty(f"from {mod} import parse; print(parse('z'))", cwd=tmp)
    q = run_cli(["-C", tmp, "--from", mod, "parse"])
    if listed is None:
        listed = run_cli(["-C", tmp, "parse"])
    row = list_source_for(listed.stdout, mod)
    hon_val = hon.stdout.strip() if hon.returncode == 0 else None
    print(
        f"-- {mod} hon_rc={hon.returncode} hon={hon_val!r} "
        f"qrc={q.returncode} q_has_hon={bool(hon_val) and hon_val in q.stdout} "
        f"list_has_hon={bool(hon_val) and hon_val in row} "
        f"list_bind={list_has_bind(listed.stdout, f'{mod}.parse')}"
    )
    if hon.returncode == 0 and hon_val:
        if hon_val not in q.stdout and q.returncode == 0:
            mark_diverge(f"query_{mod}", f"query != honesty {hon_val}")
            show(q, f"query {mod}")
        if hon_val not in row:
            if declared_park:
                mark_park(f"list_{mod}", f"list last-wins != honesty {hon_val}")
            else:
                mark_diverge(f"list_{mod}", f"list last-wins != honesty {hon_val}; row={row!r}")
                show(q, f"query {mod}")
                print("LIST_ROW", row)
    elif hon.returncode != 0:
        if q.returncode == 0 and "kind\tdef" in q.stdout:
            if declared_park:
                mark_park(f"query_{mod}", "honesty no name, query kind=def")
            else:
                mark_diverge(f"query_{mod}", "honesty no name, query kind=def")
                show(q, f"query {mod}")
        if list_has_bind(listed.stdout, f"{mod}.parse"):
            if declared_park:
                mark_park(f"list_{mod}", "honesty no name, list kind=def")
            else:
                mark_diverge(f"list_{mod}", "honesty no name, list kind=def")
                print("LIST_ROW", row)


def live_dead_kill(tmp: str, mod: str, live: str, dead: str) -> bool:
    hon = honesty(f"from {mod} import parse; print(parse('z'))", cwd=tmp)
    q = run_cli(["-C", tmp, "--from", mod, "parse"])
    listed = run_cli(["-C", tmp, "parse"])
    row = list_source_for(listed.stdout, mod)
    show(hon, f"honesty {mod}")
    show(q, f"query {mod}")
    print(f"LIST_ROW {mod}\n", row)
    fired = hon.stdout.strip() == live and live in q.stdout and dead in row and live not in row
    print(f"KILL_{mod}_list_dead", fired)
    return fired


def for_miss_kill(tmp: str, mod: str, live: str) -> bool:
    hon = honesty(f"from {mod} import parse; print(parse('z'))", cwd=tmp)
    q = run_cli(["-C", tmp, "--from", mod, "parse"])
    listed = run_cli(["-C", tmp, "parse"])
    row = list_source_for(listed.stdout, mod)
    show(hon, f"honesty {mod}")
    show(q, f"query {mod}")
    print(f"LIST_ROW {mod}\n", row)
    fired = hon.stdout.strip() == live and live in q.stdout and not list_has_bind(listed.stdout, f"{mod}.parse")
    print(f"KILL_{mod}_list_miss", fired)
    return fired


def dead_only_kill(tmp: str, mod: str) -> bool:
    hon = honesty(f"from {mod} import parse; print(parse('z'))", cwd=tmp)
    q = run_cli(["-C", tmp, "--from", mod, "parse"])
    listed = run_cli(["-C", tmp, "parse"])
    show(hon, f"honesty {mod}")
    show(q, f"query {mod}")
    show(listed, f"list {mod}")
    fired = q.returncode != 0 and list_has_bind(listed.stdout, f"{mod}.parse")
    print(f"KILL_{mod}_list_kind_def", fired)
    return fired


def main() -> None:
    banner("0. owned specimen-013 leftover vs moved")
    for args, label in [
        (["-C", str(SPEC013), "--from", "pkg_util", "parse"], "from pkg_util"),
        (["-C", str(SPEC013), "--from", "pkg_parse", "parse"], "from pkg_parse"),
        (["-C", str(SPEC013), "parse"], "list parse"),
    ]:
        show(run_cli(args), label)

    banner("H1. leftover ast.py vs honesty (KILL if Cellar / lib/python)")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(tmp, {"ast.py": AST_LEFTOVER, "pkg_parse.py": PARSE_MOVED})
        hon = honesty(
            "from ast import parse; print(parse('z')); import ast; print(ast.__file__)",
            cwd=tmp,
        )
        show(hon, "honesty cwd=tmp")
        proc = run_cli(["-C", tmp, "--from", "ast", "parse"], cwd="/tmp")
        show(proc, "bindname leftover ast from /tmp")
        kill_stdlib = any(s in proc.stdout for s in ("Cellar", "lib/python"))
        print("KILL_stdlib_file", kill_stdlib)
        print("leftover-ast_in_source", "leftover-ast" in proc.stdout)
        print("starts_query", proc.stdout.startswith("query\t"))
        HONOR["1_ast_cellar"] = kill_stdlib
        listed = run_cli(["-C", tmp, "parse"], cwd="/tmp")
        show(listed, "list leftover ast")

    banner("H1b. in-process logical name + restore")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(tmp, {"ast.py": AST_LEFTOVER, "pkg_parse.py": PARSE_MOVED})
        code = textwrap.dedent(
            f"""
            import importlib.machinery, importlib.util, sys
            from pathlib import Path
            loader = importlib.machinery.SourceFileLoader('bindname_cli12', {str(CLI)!r})
            spec = importlib.util.spec_from_loader(loader.name, loader)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[loader.name] = mod
            loader.exec_module(mod)
            root = Path({tmp!r})
            stdlib = sys.modules['ast']
            print('before', stdlib.__file__)
            with mod.isolated_import(root):
                m, logical = mod.load_query(root, 'ast', root/'ast.py')
                print('logical', logical)
                print('mod.__name__', m.__name__)
                print('parse', m.parse('z'))
                print('sys.modules[ast] is leftover', sys.modules.get('ast') is m)
                print('file', getattr(sys.modules.get('ast'), '__file__', None))
            print('restored', sys.modules['ast'] is stdlib)
            print('restored_file', sys.modules['ast'].__file__)
            """
        )
        show(subprocess.run([sys.executable, "-c", code], capture_output=True, text=True), "logical load")

    banner("H2. import_module against sys.modules for the query")
    src = CLI.read_text(encoding="utf-8")
    print("has_import_module", "import_module" in src)
    print("has_spec_from_file_location", "spec_from_file_location" in src)
    print("has__bindname_N", "_bindname_" in src)
    print("has_is_unshadowable", "is_unshadowable" in src)
    print("has_interpreter_preimported", "interpreter_preimported" in src)
    print("has_is_frozen", "is_frozen" in src)
    print("has_unshadowable_reason", "unshadowable_reason" in src)
    HONOR["2_import_module"] = "import_module" in src

    banner("H3. also does not execute siblings (KILL if sys.exit hijack)")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        root = write_fixture(
            tmp,
            {
                "keep.py": "def parse(x):\n    return 'kept'\n",
                "killer.py": "import sys\ndef parse(x):\n    return 'dead'\nsys.exit(9)\n",
                "side.py": "open('SIDE','w').write('ran')\ndef parse(x):\n    return 'side'\n",
                "osexit.py": "import os\ndef parse(x):\n    return 'os'\nos._exit(11)\n",
            },
        )
        proc = run_cli(["-C", tmp, "--from", "keep", "parse"])
        show(proc, "from keep with killer+side+osexit")
        print("SIDE_exists", (root / "SIDE").exists())
        hijack = proc.returncode in (9, 11) or not proc.stdout.startswith("query\t")
        print("KILL_hijack", hijack)
        HONOR["3_also_exec_siblings"] = hijack or (root / "SIDE").exists()

    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "pkg_util.py": UTIL_LEGACY,
                "pkg_parse.py": PARSE_MOVED,
                "aaa_patch.py": (
                    "import pkg_util\n"
                    "pkg_util.parse = lambda x: ('patched', x)\n"
                    "def parse(x):\n    return ('patcher', x)\n"
                ),
            },
        )
        proc = run_cli(["-C", tmp, "--from", "pkg_util", "parse"])
        show(proc, "aaa_patch")
        print("KILL_patched", "patched" in proc.stdout)

    banner("H4. leftover io.py/sys.py kind=def while honesty ImportError")
    kill4 = False
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "io.py": "def parse(x):\n    return ('leftover-io', x)\n",
                "encodings.py": "def parse(x):\n    return ('leftover-encodings', x)\n",
                "os.py": "def parse(x):\n    return ('leftover-os', x)\n",
                "sys.py": "def parse(x):\n    return ('leftover-sys', x)\n",
                "builtins.py": "def parse(x):\n    return ('leftover-builtins', x)\n",
                "pkg_parse.py": PARSE_MOVED,
            },
        )
        for mod in ("io", "encodings", "os", "sys", "builtins"):
            hon = honesty(f"from {mod} import parse; print(parse('z'))", cwd=tmp)
            proc = run_cli(["-C", tmp, "--from", mod, "parse"], cwd="/tmp")
            show(hon, f"honesty {mod}")
            show(proc, f"bindname {mod}")
            kind_def = proc.returncode == 0 and "kind\tdef" in proc.stdout
            leftover_body = f"leftover-{mod}" in proc.stdout
            print(f"KILL_{mod}_kind_def", kind_def)
            print(f"KILL_{mod}_leftover_body", leftover_body)
            if hon.returncode != 0 and (kind_def or leftover_body):
                kill4 = True
    HONOR["4_io_sys_kind_def"] = kill4

    banner("H5. leftover importlib.util kind=def while honesty cannot bind")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "importlib/__init__.py": "def parse(x):\n    return ('leftover-importlib', x)\n",
                "importlib/util.py": "def parse(x):\n    return ('leftover-importlib-util', x)\n",
                "importlib/machinery.py": "def parse(x):\n    return ('leftover-importlib-mach', x)\n",
                "importlib/abc.py": "def parse(x):\n    return ('leftover-importlib-abc', x)\n",
                "pkg_parse.py": PARSE_MOVED,
            },
        )
        hon = honesty("from importlib.util import parse; print(parse('z'))", cwd=tmp)
        proc = run_cli(["-C", tmp, "--from", "importlib.util", "parse"], cwd="/tmp")
        show(hon, "honesty importlib.util")
        show(proc, "bindname importlib.util")
        kill5 = hon.returncode != 0 and (
            (proc.returncode == 0 and "kind\tdef" in proc.stdout)
            or "leftover-importlib-util" in proc.stdout
        )
        print("KILL_importlib_util_kind_def", kill5)
        HONOR["5_importlib_util_kind_def"] = kill5
        listed = run_cli(["-C", tmp, "parse"], cwd="/tmp")
        show(listed, "list importlib tree")
        print("list_has_importlib.util.parse", list_has_bind(listed.stdout, "importlib.util.parse"))
        hon_m = honesty("from importlib.machinery import parse; print(parse('z'))", cwd=tmp)
        q_m = run_cli(["-C", tmp, "--from", "importlib.machinery", "parse"], cwd="/tmp")
        show(hon_m, "honesty importlib.machinery")
        show(q_m, "bindname importlib.machinery")
        kill_m = hon_m.returncode != 0 and (
            (q_m.returncode == 0 and "kind\tdef" in q_m.stdout)
            or "leftover-importlib-mach" in q_m.stdout
        )
        print("KILL_importlib_machinery_kind_def", kill_m)
        if kill_m:
            HONOR["5_importlib_util_kind_def"] = True

    banner("H6. leftover importlib.py file / importlib.abc is miss while honesty leftover")
    kill6 = False
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "importlib.py": "def parse(x):\n    return ('leftover-importlib-file', x)\n",
                "pkg_parse.py": PARSE_MOVED,
            },
        )
        hon = honesty("from importlib import parse; print(parse('z'))", cwd=tmp)
        proc = run_cli(["-C", tmp, "--from", "importlib", "parse"], cwd="/tmp")
        show(hon, "honesty importlib.py file")
        show(proc, "bindname importlib.py file")
        hon_helper = hon.returncode == 0 and "leftover-importlib-file" in hon.stdout
        cli_helper = (
            proc.returncode == 0
            and "kind\tdef" in proc.stdout
            and "leftover-importlib-file" in proc.stdout
            and "Cellar" not in proc.stdout
            and "lib/python" not in proc.stdout.split("file\t")[-1][:80]
        )
        print("importlib_file_honesty_helper", hon_helper)
        print("importlib_file_cli_helper", cli_helper)
        if hon_helper and not cli_helper:
            kill6 = True
            print("KILL_importlib_file_miss")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "importlib/__init__.py": "def parse(x):\n    return ('leftover-importlib', x)\n",
                "importlib/abc.py": "def parse(x):\n    return ('leftover-importlib-abc', x)\n",
                "pkg_parse.py": PARSE_MOVED,
            },
        )
        hon = honesty("from importlib.abc import parse; print(parse('z'))", cwd=tmp)
        proc = run_cli(["-C", tmp, "--from", "importlib.abc", "parse"], cwd="/tmp")
        show(hon, "honesty importlib.abc")
        show(proc, "bindname importlib.abc")
        hon_helper = hon.returncode == 0 and "leftover-importlib-abc" in hon.stdout
        cli_helper = (
            proc.returncode == 0
            and "kind\tdef" in proc.stdout
            and "leftover-importlib-abc" in proc.stdout
        )
        print("importlib_abc_honesty_helper", hon_helper)
        print("importlib_abc_cli_helper", cli_helper)
        if hon_helper and not cli_helper:
            kill6 = True
            print("KILL_importlib_abc_miss")
    HONOR["6_importlib_file_or_abc_miss"] = kill6

    banner("H7. del T.x; if T.x: live else: dead list kind=def while honesty AttributeError")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "delattreelse.py": (
                    "class T:\n"
                    "    x = 1\n"
                    "del T.x\n"
                    "if T.x:\n" + if_both("dae-live", "dae-dead")
                ),
                "pkg_parse.py": PARSE_MOVED,
            },
        )
        kill7 = dead_only_kill(tmp, "delattreelse")
        print("KILL_delattreelse_list_kind_def", kill7)
        HONOR["7_del_Tx_ifelse_list_kind_def"] = kill7

    banner("H8. del x; if x: list kind=def while honesty NameError")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "delname.py": (
                    "x = 1\n"
                    "del x\n"
                    "if x:\n"
                    "    def parse(y):\n"
                    "        return 'dn-dead-only'\n"
                ),
                "pkg_parse.py": PARSE_MOVED,
            },
        )
        kill8 = dead_only_kill(tmp, "delname")
        print("KILL_delname_list_kind_def", kill8)
        HONOR["8_del_x_if_list_kind_def"] = kill8

    banner("H9. t=T(); T.x=0; if t.x list live while honesty dead")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "classafterinst.py": (
                    "class T:\n"
                    "    x = 1\n"
                    "t = T()\n"
                    "T.x = 0\n"
                    "if t.x:\n" + if_both("cai-live", "cai-dead")
                ),
                "pkg_parse.py": PARSE_MOVED,
            },
        )
        kill9 = live_dead_kill(tmp, "classafterinst", "cai-dead", "cai-live")
        print("KILL_classafterinst_list_live", kill9)
        HONOR["9_t_follows_class_list_live"] = kill9

    banner("H10. THIN_WRAPPER of two greps / importlib.util with no leftover-identity join")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(tmp, {"ast.py": AST_LEFTOVER, "pkg_parse.py": PARSE_MOVED})
        naive = honesty(
            "import ast, inspect; print(inspect.getsourcefile(ast.parse)); print(inspect.getsource(ast.parse)[:80])",
            cwd="/tmp",
        )
        show(naive, "naive inspect ast.parse from /tmp (stdlib)")
        grep = subprocess.run(
            ["grep", "-n", "def parse", str(Path(tmp) / "ast.py"), str(Path(tmp) / "pkg_parse.py")],
            capture_output=True,
            text=True,
        )
        show(grep, "grep def parse")
        proc = run_cli(["-C", tmp, "--from", "ast", "parse"], cwd="/tmp")
        naive_stdlib = "Cellar" in naive.stdout or "lib/python" in naive.stdout
        bind_leftover = "leftover-ast" in proc.stdout and "Cellar" not in proc.stdout
        also_moved = "also\tpkg_parse.parse" in proc.stdout
        print("naive_is_stdlib", naive_stdlib)
        print("bindname_is_leftover", bind_leftover)
        print("also_moved", also_moved)
        HONOR["10_thin_wrapper"] = not (naive_stdlib and bind_leftover and also_moved)

    banner("C0. leftover importlib/ package + tokenize still helper")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "importlib/__init__.py": "def parse(x):\n    return ('leftover-importlib-pkg', x)\n",
                "pkg_parse.py": PARSE_MOVED,
            },
        )
        hon = honesty(
            "from importlib import parse; print(parse('z')); import importlib; print('FILE', importlib.__file__)",
            cwd=tmp,
        )
        q = run_cli(["-C", tmp, "--from", "importlib", "parse"], cwd="/tmp")
        show(hon, "honesty importlib pkg")
        show(q, "bindname importlib pkg")
        hon_helper = hon.returncode == 0 and "leftover-importlib-pkg" in hon.stdout
        cli_helper = q.returncode == 0 and "leftover-importlib-pkg" in q.stdout and "kind\tdef" in q.stdout
        print("importlib_pkg_honesty_helper", hon_helper)
        print("importlib_pkg_cli_helper", cli_helper)
        if hon_helper and not cli_helper:
            mark_diverge("importlib_pkg", "honesty leftover package, CLI miss")
        if (not hon_helper) and cli_helper:
            mark_diverge("importlib_pkg", "honesty cannot bind, CLI kind=def")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "tokenize.py": "def parse(x):\n    return ('leftover-tokenize', x)\n",
                "pkg_parse.py": PARSE_MOVED,
            },
        )
        hon = honesty("from tokenize import parse; print(parse('z'))", cwd=tmp)
        q = run_cli(["-C", tmp, "--from", "tokenize", "parse"], cwd="/tmp")
        show(hon, "honesty tokenize")
        show(q, "bindname tokenize")
        if hon.returncode == 0 and "leftover-tokenize" in hon.stdout:
            if q.returncode != 0 or "leftover-tokenize" not in q.stdout:
                mark_diverge("tokenize", "honesty leftover helper, CLI miss")

    banner("C1. other leftover stdlib names honesty vs CLI")
    leftover_cases = [
        ("json", {"json.py": "def parse(x):\n    return ('leftover-json', x)\n", "pkg_parse.py": PARSE_MOVED}),
        ("pathlib", {"pathlib.py": "def parse(x):\n    return ('leftover-pathlib', x)\n", "pkg_parse.py": PARSE_MOVED}),
        ("inspect", {"inspect.py": "def parse(x):\n    return ('leftover-inspect', x)\n", "pkg_parse.py": PARSE_MOVED}),
        ("typing", {"typing.py": "def parse(x):\n    return ('leftover-typing', x)\n", "pkg_parse.py": PARSE_MOVED}),
        ("dataclasses", {"dataclasses.py": "def parse(x):\n    return ('leftover-dataclasses', x)\n", "pkg_parse.py": PARSE_MOVED}),
        ("warnings", {"warnings.py": "def parse(x):\n    return ('leftover-warnings', x)\n", "pkg_parse.py": PARSE_MOVED}),
        ("contextlib", {"contextlib.py": "def parse(x):\n    return ('leftover-contextlib', x)\n", "pkg_parse.py": PARSE_MOVED}),
        ("argparse", {"argparse.py": "def parse(x):\n    return ('leftover-argparse', x)\n", "pkg_parse.py": PARSE_MOVED}),
        ("tempfile", {"tempfile.py": "def parse(x):\n    return ('leftover-tempfile', x)\n", "pkg_parse.py": PARSE_MOVED}),
        ("subprocess", {"subprocess.py": "def parse(x):\n    return ('leftover-subprocess', x)\n", "pkg_parse.py": PARSE_MOVED}),
        ("enum", {"enum.py": "def parse(x):\n    return ('leftover-enum', x)\n", "pkg_parse.py": PARSE_MOVED}),
        ("operator", {"operator.py": "def parse(x):\n    return ('leftover-operator', x)\n", "pkg_parse.py": PARSE_MOVED}),
        ("functools", {"functools.py": "def parse(x):\n    return ('leftover-functools', x)\n", "pkg_parse.py": PARSE_MOVED}),
        ("abc", {"abc.py": "def parse(x):\n    return ('leftover-abc', x)\n", "pkg_parse.py": PARSE_MOVED}),
        ("types", {"types.py": "def parse(x):\n    return ('leftover-types', x)\n", "pkg_parse.py": PARSE_MOVED}),
        ("re", {"re.py": "def parse(x):\n    return ('leftover-re', x)\n", "pkg_parse.py": PARSE_MOVED}),
        ("collections", {"collections.py": "def parse(x):\n    return ('leftover-collections', x)\n", "pkg_parse.py": PARSE_MOVED}),
        ("copyreg", {"copyreg.py": "def parse(x):\n    return ('leftover-copyreg', x)\n", "pkg_parse.py": PARSE_MOVED}),
        ("site", {"site.py": "def parse(x):\n    return ('leftover-site', x)\n", "pkg_parse.py": PARSE_MOVED}),
        ("zipimport", {"zipimport.py": "def parse(x):\n    return ('leftover-zipimport', x)\n", "pkg_parse.py": PARSE_MOVED}),
        ("importlib.resources", {
            "importlib/__init__.py": "def parse(x):\n    return ('leftover-importlib', x)\n",
            "importlib/resources.py": "def parse(x):\n    return ('leftover-resources', x)\n",
            "pkg_parse.py": PARSE_MOVED,
        }),
        ("importlib.metadata", {
            "importlib/__init__.py": "def parse(x):\n    return ('leftover-importlib', x)\n",
            "importlib/metadata.py": "def parse(x):\n    return ('leftover-metadata', x)\n",
            "pkg_parse.py": PARSE_MOVED,
        }),
        ("json.decoder", {
            "json/__init__.py": "def parse(x):\n    return ('leftover-json', x)\n",
            "json/decoder.py": "def parse(x):\n    return ('leftover-json-decoder', x)\n",
            "pkg_parse.py": PARSE_MOVED,
        }),
        ("collections.abc", {
            "collections/__init__.py": "def parse(x):\n    return ('leftover-collections', x)\n",
            "collections/abc.py": "def parse(x):\n    return ('leftover-collections-abc', x)\n",
            "pkg_parse.py": PARSE_MOVED,
        }),
        ("os.path", {
            "os/__init__.py": "def parse(x):\n    return ('leftover-os', x)\n",
            "os/path.py": "def parse(x):\n    return ('leftover-os-path', x)\n",
            "pkg_parse.py": PARSE_MOVED,
        }),
        ("encodings.utf_8", {
            "encodings/__init__.py": "def parse(x):\n    return ('leftover-encodings', x)\n",
            "encodings/utf_8.py": "def parse(x):\n    return ('leftover-encodings-utf8', x)\n",
            "pkg_parse.py": PARSE_MOVED,
        }),
        ("typing_extensions", {
            "typing_extensions.py": "def parse(x):\n    return ('leftover-tex', x)\n",
            "pkg_parse.py": PARSE_MOVED,
        }),
        ("importlib.machinery", {
            "importlib/__init__.py": "def parse(x):\n    return ('leftover-importlib', x)\n",
            "importlib/machinery.py": "def parse(x):\n    return ('leftover-importlib-mach', x)\n",
            "pkg_parse.py": PARSE_MOVED,
        }),
    ]
    for mod, files in leftover_cases:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
            write_fixture(tmp, files)
            hon = honesty(
                f"from {mod} import parse; print(parse('z')); import {mod} as m; print('FILE', getattr(m,'__file__',None))",
                cwd=tmp,
            )
            q = run_cli(["-C", tmp, "--from", mod, "parse"], cwd="/tmp")
            hon_binds = hon.returncode == 0 and "leftover-" in hon.stdout
            cli_binds = q.returncode == 0 and "kind\tdef" in q.stdout and "leftover-" in q.stdout
            cli_stdlib = any(s in q.stdout for s in ("Cellar", "lib/python"))
            if hon_binds and (not cli_binds or cli_stdlib):
                status = "DIVERGE honesty leftover CLI miss/stdlib"
                mark_diverge(mod, status)
                show(hon, f"honesty {mod}")
                show(q, f"bindname {mod}")
            elif (not hon_binds) and cli_binds:
                status = "DIVERGE honesty fail CLI kind=def"
                mark_diverge(mod, status)
                show(hon, f"honesty {mod}")
                show(q, f"bindname {mod}")
            elif hon.returncode != 0 and q.returncode != 0:
                status = "MATCH refuse"
            elif hon_binds and cli_binds and not cli_stdlib:
                status = "MATCH leftover helper"
            else:
                status = f"OTHER hon_rc={hon.returncode} cli_rc={q.returncode}"
                mark_diverge(mod, status)
                show(hon, f"honesty {mod}")
                show(q, f"bindname {mod}")
            print(f"LEFT_CASE {mod}: {status} hon_rc={hon.returncode} cli_rc={q.returncode}")

    banner("C2. mutate-16 claimed fail-If / del-Name / class-body If plus prior still match")
    claimed = {
        "forlive": (
            "for _ in [1]:\n"
            "    def parse(x):\n"
            "        return 'for-live'\n",
            "for-live",
        ),
        "forconst": (
            "xs = [1]\n"
            "for _ in xs:\n"
            "    def parse(x):\n"
            "        return 'fc-live'\n",
            "fc-live",
        ),
        "forif": (
            "for _ in [1]:\n"
            "    if True:\n"
            "        def parse(x):\n"
            "            return 'fi-live'\n",
            "fi-live",
        ),
        "forelse": (
            "for _ in [1]:\n"
            "    def parse(x):\n"
            "        return 'fe-body'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'fe-else'\n",
            "fe-else",
        ),
        "forelseempty": (
            "for _ in ():\n"
            "    def parse(x):\n"
            "        return 'fee-body'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'fee-else'\n",
            "fee-else",
        ),
        "fortup": (
            "for _ in (1,):\n"
            "    def parse(x):\n"
            "        return 'ft-live'\n",
            "ft-live",
        ),
        "forset": (
            "for _ in {1}:\n"
            "    def parse(x):\n"
            "        return 'fs-live'\n",
            "fs-live",
        ),
        "attrreal": ("if (1).real:\n" + if_both("ar-live", "ar-dead"), "ar-live"),
        "attrnum": ("if (1).numerator:\n" + if_both("an-live", "an-dead"), "an-live"),
        "attrbool": ("if True.real:\n" + if_both("ab-live", "ab-dead"), "ab-live"),
        "attrcx": ("if (1+0j).real:\n" + if_both("ax-live", "ax-dead"), "ax-live"),
        "classattr": (
            "class T:\n"
            "    x = 1\n"
            "if T.x:\n" + if_both("ca-live", "ca-dead"),
            "ca-live",
        ),
        "compone": ("if [x for x in [1]]:\n" + if_both("co-live", "co-dead"), "co-live"),
        "genalways": ("if (x for x in []):\n" + if_both("ga-live", "ga-dead"), "ga-live"),
        "genone": ("if (x for x in [1]):\n" + if_both("go-live", "go-dead"), "go-live"),
        "subl": ("if [1][0]:\n" + if_both("subl-live", "subl-dead"), "subl-live"),
        "fstrfmt": ("if f'{1}':\n" + if_both("ff-live", "ff-dead"), "ff-live"),
        "starnonempty": ("if [*[1]]:\n" + if_both("sn-live", "sn-dead"), "sn-live"),
        "uadd": ("if +1:\n" + if_both("uadd-live", "uadd-dead"), "uadd-live"),
        "inlist": ("if 1 in [1]:\n" + if_both("in-live", "in-dead"), "in-live"),
        "add": ("if 1 + 1:\n" + if_both("add-live", "add-dead"), "add-live"),
        "emptyifelse": ("if []:\n" + if_both("empty-live", "empty-dead"), "empty-dead"),
        "tupleunp": ("flag, other = True, True\n" "if flag:\n" + if_both("tu-live", "tu-dead"), "tu-live"),
        "localtc": ("TYPE_CHECKING = True\n" "if TYPE_CHECKING:\n" + if_both("ltc-live", "ltc-dead"), "ltc-live"),
        "nestedunp": (
            "flag, (other,) = True, (True,)\n"
            "if flag:\n" + if_both("nu-live", "nu-dead"),
            "nu-live",
        ),
        "starunp": (
            "flag, *rest = True, True\n"
            "if flag:\n" + if_both("su-live", "su-dead"),
            "su-live",
        ),
        "tupleval": (
            "pair = True, True\n"
            "flag, other = pair\n"
            "if flag:\n" + if_both("tv-live", "tv-dead"),
            "tv-live",
        ),
        "nestedsub": ("if [[1]][0][0]:\n" + if_both("ns-live", "ns-dead"), "ns-live"),
        "fmtconv": ("if f'{1!s}':\n" + if_both("fcv-live", "fcv-dead"), "fcv-live"),
        "matchsub": (
            "match [1][0]:\n"
            "    case 1:\n"
            "        def parse(x):\n"
            "            return 'ms-live'\n"
            "    case _:\n"
            "        def parse(x):\n"
            "            return 'ms-dead'\n",
            "ms-live",
        ),
        "compenv": (
            "xs = [1]\n"
            "if [x for x in xs]:\n" + if_both("ce-live", "ce-dead"),
            "ce-live",
        ),
        "starcomp": ("if [*[x for x in [1]]]:\n" + if_both("stc-live", "stc-dead"), "stc-live"),
        "classann": (
            "class T:\n"
            "    x: int = 1\n"
            "if T.x:\n" + if_both("ann-live", "ann-dead"),
            "ann-live",
        ),
        "classy": (
            "class T:\n"
            "    x = 1\n"
            "    y = x\n"
            "if T.y:\n" + if_both("cy-live", "cy-dead"),
            "cy-live",
        ),
        "forzero": (
            "for _ in [0]:\n"
            "    def parse(x):\n"
            "        return 'fz-live'\n",
            "fz-live",
        ),
        "forxif": (
            "for x in [1]:\n"
            "    if x:\n"
            "        def parse(y):\n"
            "            return 'fx-live'\n",
            "fx-live",
        ),
        "notimag": ("if not (1).imag:\n" + if_both("ni-live", "ni-dead"), "ni-live"),
        "setcomp": ("if {x for x in [1]}:\n" + if_both("sc-live", "sc-dead"), "sc-live"),
        "dictcomp": ("if {x: x for x in [1]}:\n" + if_both("dc-live", "dc-dead"), "dc-live"),
        "dictcompc": ("if {x: 1 for x in [1]}:\n" + if_both("dcc-live", "dcc-dead"), "dcc-live"),
        "compif": ("if [x for x in [1] if x]:\n" + if_both("ci-live", "ci-dead"), "ci-live"),
        "filt": ("if [x for x in [1, 0] if x]:\n" + if_both("filt-live", "filt-dead"), "filt-live"),
        "constelt": ("if [1 for _ in [1]]:\n" + if_both("cte-live", "cte-dead"), "cte-live"),
        "binopelt": ("if [x + 0 for x in [1]]:\n" + if_both("be-live", "be-dead"), "be-live"),
        "nestedcomp": ("if [[y for y in [1]]]:\n" + if_both("nc2-live", "nc2-dead"), "nc2-live"),
        "instattr": (
            "class T:\n"
            "    x = 1\n"
            "t = T()\n"
            "if t.x:\n" + if_both("ia-live", "ia-dead"),
            "ia-live",
        ),
        "iflambda": ("if (lambda: 0):\n" + if_both("il-live", "il-dead"), "il-live"),
        "iflambda1": ("if (lambda: 1):\n" + if_both("il1-live", "il1-dead"), "il1-live"),
        "setcompif": ("if {x for x in [1] if x}:\n" + if_both("sci-live", "sci-dead"), "sci-live"),
        "dictcompif": ("if {x: x for x in [1] if x}:\n" + if_both("dci-live", "dci-dead"), "dci-live"),
        "nestedgen": ("if (x for y in [] for x in y):\n" + if_both("ng-live", "ng-dead"), "ng-live"),
        "fmtspec": ("if f'{1:d}':\n" + if_both("fmt-live", "fmt-dead"), "fmt-live"),
        "fmtwidth": ("if f'{1:02d}':\n" + if_both("fw-live", "fw-dead"), "fw-live"),
        "fmtnested": ("if f'{1:{1}}':\n" + if_both("fn-live", "fn-dead"), "fn-live"),
        "walrusfmt": ("if (s := f'{1:d}'):\n" + if_both("wf-live", "wf-dead"), "wf-live"),
        "genfor1": (
            "for _ in (x for x in [1]):\n"
            "    def parse(x):\n"
            "        return 'gf1-live'\n",
            "gf1-live",
        ),
        "compgeniter": ("if [y for y in (x for x in [1])]:\n" + if_both("cgi-live", "cgi-dead"), "cgi-live"),
        "setgeniter": ("if {y for y in (x for x in [1])}:\n" + if_both("sgi-live", "sgi-dead"), "sgi-live"),
        "stargen": ("if [*(x for x in [1])]:\n" + if_both("sg-live", "sg-dead"), "sg-live"),
        "tupgen": ("if (*(x for x in [1]),):\n" + if_both("tg-live", "tg-dead"), "tg-live"),
        "assignedgen": (
            "xs = (x for x in [1])\n"
            "for _ in xs:\n"
            "    def parse(x):\n"
            "        return 'ag-live'\n",
            "ag-live",
        ),
        "setconstelt": ("if {1 for _ in [1]}:\n" + if_both("sce-live", "sce-dead"), "sce-live"),
        "setbinopelt": ("if {x + 0 for x in [1]}:\n" + if_both("sbe-live", "sbe-dead"), "sbe-live"),
        "dictkv": ("if {k: v for k, v in [(1, 2)]}:\n" + if_both("dkv-live", "dkv-dead"), "dkv-live"),
        "compenvset": (
            "xs = [1]\n"
            "if {x for x in xs}:\n" + if_both("ces-live", "ces-dead"),
            "ces-live",
        ),
        "anninst": (
            "class T:\n"
            "    x: int = 1\n"
            "t = T()\n"
            "if t.x:\n" + if_both("ai-live", "ai-dead"),
            "ai-live",
        ),
        "boolgen": ("if not (x for x in []):\n" + if_both("bg-live", "bg-dead"), "bg-dead"),
        "assignedemptyif": (
            "xs = (x for x in [])\n"
            "if xs:\n" + if_both("aei-live", "aei-dead"),
            "aei-live",
        ),
        "filtgenif": ("if (x for x in [1] if False):\n" + if_both("fgi-live", "fgi-dead"), "fgi-live"),
        "classassign": (
            "class T:\n"
            "    x = 1\n"
            "T.x = 0\n"
            "if T.x:\n" + if_both("cas-live", "cas-dead"),
            "cas-dead",
        ),
        "classassignlive": (
            "class T:\n"
            "    x = 0\n"
            "T.x = 1\n"
            "if T.x:\n" + if_both("cal-live", "cal-dead"),
            "cal-live",
        ),
        "classnewattr": (
            "class T:\n"
            "    x = 0\n"
            "T.y = 1\n"
            "if T.y:\n" + if_both("cna-live", "cna-dead"),
            "cna-live",
        ),
        "instassign": (
            "class T:\n"
            "    x = 1\n"
            "t = T()\n"
            "t.x = 0\n"
            "if t.x:\n" + if_both("ias-live", "ias-dead"),
            "ias-dead",
        ),
        "annassignattr": (
            "class T:\n"
            "    x = 1\n"
            "T.x: int = 0\n"
            "if T.x:\n" + if_both("aa-live", "aa-dead"),
            "aa-dead",
        ),
        "multigen": ("if [x for y in [[1]] for x in y]:\n" + if_both("mg-live", "mg-dead"), "mg-live"),
        "multiset": ("if {x for y in [[1]] for x in y]:\n" + if_both("ms2-live", "ms2-dead"), "ms2-live"),
        "multidict": ("if {x: 1 for y in [[1]] for x in y}:\n" + if_both("md-live", "md-dead"), "md-live"),
        "multigen3": (
            "if [z for a in [[[1]]] for b in a for z in b]:\n" + if_both("mg3-live", "mg3-dead"),
            "mg3-live",
        ),
        "multigenfilt": (
            "if [x for y in [[1, 0]] for x in y if x]:\n" + if_both("mgf-live", "mgf-dead"),
            "mgf-live",
        ),
        "fmtconvspec_s": ("if f'{1!s:s}':\n" + if_both("fcss-live", "fcss-dead"), "fcss-live"),
        "asyncdefcls": (
            "class T:\n"
            "    x = 1\n"
            "    async def go(self):\n"
            "        return 0\n"
            "t = T()\n"
            "if t.x:\n" + if_both("adc-live", "adc-dead"),
            "adc-live",
        ),
        "matchattr": (
            "class T:\n"
            "    x = 1\n"
            "T.x = 0\n"
            "match T.x:\n"
            "    case 0:\n"
            "        def parse(x):\n"
            "            return 'ma-dead'\n"
            "    case _:\n"
            "        def parse(x):\n"
            "            return 'ma-live'\n",
            "ma-dead",
        ),
        "txsub": (
            "class T:\n"
            "    x = 1\n"
            "T.x = T.x - 1\n"
            "if T.x:\n" + if_both("txs-live", "txs-dead"),
            "txs-dead",
        ),
        "classafterinst": (
            "class T:\n"
            "    x = 1\n"
            "t = T()\n"
            "T.x = 0\n"
            "if t.x:\n" + if_both("cai-live", "cai-dead"),
            "cai-dead",
        ),
        "instthenclassy": (
            "class T:\n"
            "    x = 1\n"
            "t = T()\n"
            "T.y = 1\n"
            "if t.y:\n" + if_both("icy-live", "icy-dead"),
            "icy-live",
        ),
        "classflag": (
            "flag = True\n"
            "class T:\n"
            "    x = flag\n"
            "if T.x:\n" + if_both("outer-live", "outer-dead"),
            "outer-live",
        ),
        "classifclaimed": (
            "class T:\n"
            "    if True:\n"
            "        x = 1\n"
            "    else:\n"
            "        x = 0\n"
            "if T.x:\n" + if_both("cif-live", "cif-dead"),
            "cif-live",
        ),
        "classiffalseclaimed": (
            "class T:\n"
            "    if False:\n"
            "        x = 1\n"
            "    else:\n"
            "        x = 0\n"
            "if T.x:\n" + if_both("cff-live", "cff-dead"),
            "cff-dead",
        ),
        "classouter": (
            "class T:\n"
            "    x = 1\n"
            "class U:\n"
            "    y = T.x\n"
            "if U.y:\n" + if_both("co2-live", "co2-dead"),
            "co2-live",
        ),
        "shadowkeep": (
            "class T:\n"
            "    x = 1\n"
            "t = T()\n"
            "t.x = 1\n"
            "T.x = 0\n"
            "if t.x:\n" + if_both("sk-live", "sk-dead"),
            "sk-live",
        ),
        "twoinst": (
            "class T:\n"
            "    x = 1\n"
            "t1 = T()\n"
            "t2 = T()\n"
            "t1.x = 0\n"
            "if t2.x:\n" + if_both("ti-live", "ti-dead"),
            "ti-live",
        ),
        "multiattr": (
            "class T:\n"
            "    x = 1\n"
            "    y = 1\n"
            "T.x = T.y = 0\n"
            "if T.x:\n" + if_both("ma2-live", "ma2-dead"),
            "ma2-dead",
        ),
    }
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        files = {f"{name}.py": body for name, (body, _h) in claimed.items()}
        files["pkg_parse.py"] = PARSE_MOVED
        write_fixture(tmp, files)
        listed = run_cli(["-C", tmp, "parse"])
        for name, (_body, expect) in claimed.items():
            hon = honesty(f"from {name} import parse; print(parse('z'))", cwd=tmp)
            q = run_cli(["-C", tmp, "--from", name, "parse"])
            row = list_source_for(listed.stdout, name)
            hon_val = hon.stdout.strip() if hon.returncode == 0 else None
            print(
                f"-- claimed {name} hon={hon_val!r} expect={expect!r} "
                f"q_ok={expect in q.stdout} list_ok={expect in row}"
            )
            if hon_val != expect:
                mark_diverge(f"honesty_{name}", f"honesty {hon_val} != {expect}")
            if expect not in q.stdout:
                mark_diverge(f"query_{name}", f"query missing {expect}")
            if expect not in row:
                mark_diverge(f"list_{name}", f"list missing {expect}; row={row!r}")

    banner("C3. claimed dead-only without else is not a list bind")
    dead_only = {
        "forempty": "for _ in ():\n    def parse(x):\n        return 'for-empty'\n",
        "foremempty": "for _ in []:\n    def parse(x):\n        return 'for-dead-only'\n",
        "attr0": "if (0).real:\n    def parse(x):\n        return 'a0-dead-only'\n",
        "attrimag": "if (1).imag:\n    def parse(x):\n        return 'ai-dead-only'\n",
        "classattr0": (
            "class T:\n"
            "    x = 0\n"
            "if T.x:\n"
            "    def parse(x):\n"
            "        return 'c0-dead-only'\n"
        ),
        "compempty": "if [x for x in []]:\n    def parse(x):\n        return 'ce-dead-only'\n",
        "setcomp0": "if {x for x in []}:\n    def parse(x):\n        return 'sc0-dead-only'\n",
        "dictcomp0": "if {x: x for x in []}:\n    def parse(x):\n        return 'dc0-dead-only'\n",
        "compif0": "if [x for x in [1] if False]:\n    def parse(x):\n        return 'ci0-dead-only'\n",
        "genfor0": "for _ in (x for x in []):\n    def parse(x):\n        return 'gf0-dead-only'\n",
        "instattr0": (
            "class T:\n"
            "    x = 0\n"
            "t = T()\n"
            "if t.x:\n"
            "    def parse(x):\n"
            "        return 'ia0-dead-only'\n"
        ),
        "sub0": "if [0][0]:\n    def parse(x):\n        return 'sub0-dead-only'\n",
        "fstrempty": "if f'':\n    def parse(x):\n        return 'fe-dead-only'\n",
        "starlist": "if [*[]]:\n    def parse(x):\n        return 'star-dead-only'\n",
        "whilefalse": "while False:\n    def parse(x):\n        return 'wf-dead-only'\n",
        "filtgenfor": (
            "for _ in (x for x in [1] if False):\n"
            "    def parse(x):\n"
            "        return 'fgf-dead-only'\n"
        ),
        "assignedgen0": (
            "xs = (x for x in [])\n"
            "for _ in xs:\n"
            "    def parse(x):\n"
            "        return 'ag0-dead-only'\n"
        ),
        "stargen0": (
            "if [*(x for x in [])]:\n"
            "    def parse(x):\n"
            "        return 'sg0-dead-only'\n"
        ),
        "classassign0": (
            "class T:\n"
            "    x = 1\n"
            "T.x = 0\n"
            "if T.x:\n"
            "    def parse(x):\n"
            "        return 'cas0-dead-only'\n"
        ),
        "multigen0": (
            "if [x for y in [[]] for x in y]:\n"
            "    def parse(x):\n"
            "        return 'mg0-dead-only'\n"
        ),
        "fmtconvspec0": (
            "if f'{1!s:d}':\n"
            "    def parse(x):\n"
            "        return 'fcs0-dead-only'\n"
        ),
        "delattr": (
            "class T:\n"
            "    x = 1\n"
            "del T.x\n"
            "if T.x:\n"
            "    def parse(x):\n"
            "        return 'da-dead-only'\n"
        ),
        "classafter0": (
            "class T:\n"
            "    x = 1\n"
            "t = T()\n"
            "T.x = 0\n"
            "if t.x:\n"
            "    def parse(x):\n"
            "        return 'cai0-dead-only'\n"
        ),
        "delinstlookup": (
            "class T:\n"
            "    x = 1\n"
            "t = T()\n"
            "del T.x\n"
            "if t.x:\n"
            "    def parse(x):\n"
            "        return 'dil-dead-only'\n"
        ),
    }
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        files = {f"{name}.py": body for name, body in dead_only.items()}
        files["pkg_parse.py"] = PARSE_MOVED
        write_fixture(tmp, files)
        listed = run_cli(["-C", tmp, "parse"])
        for name in dead_only:
            hon = honesty(f"from {name} import parse; print(parse('z'))", cwd=tmp)
            q = run_cli(["-C", tmp, "--from", name, "parse"])
            has = list_has_bind(listed.stdout, f"{name}.parse")
            print(
                f"-- dead-only {name} hon_rc={hon.returncode} qrc={q.returncode} list_bind={has}"
            )
            if hon.returncode == 0:
                mark_diverge(f"honesty_{name}", "expected honesty no name")
            if q.returncode == 0:
                mark_diverge(f"query_{name}", "expected query has no name")
            if has:
                if name == "whilefalse":
                    mark_park(f"list_{name}", "while False list bind (While park)")
                elif name == "fmtconvspec0":
                    mark_park(f"list_{name}", "format-error JoinedStr _MISSING both (declared)")
                else:
                    mark_diverge(f"list_{name}", "dead-only without else still a list bind")

    banner("C4. remaining leftover-identity after mutate-16 (not declared parks)")
    remaining = {
        "fmtspec0": (
            "if f'{1:s}':\n"
            "    def parse(x):\n"
            "        return 'fmts-dead-only'\n",
            True,
        ),
        "fmtconvspec": ("if f'{1!s:d}':\n" + if_both("fcs-live", "fcs-dead"), True),
        "fmtdebug": ("if f'{1=}':\n" + if_both("fd-live", "fd-dead"), False),
        "classafterinst": (
            "class T:\n"
            "    x = 1\n"
            "t = T()\n"
            "T.x = 0\n"
            "if t.x:\n" + if_both("cai-live", "cai-dead"),
            False,
        ),
        "instthenclassy": (
            "class T:\n"
            "    x = 1\n"
            "t = T()\n"
            "T.y = 1\n"
            "if t.y:\n" + if_both("icy-live", "icy-dead"),
            False,
        ),
        "shadowkeep": (
            "class T:\n"
            "    x = 1\n"
            "t = T()\n"
            "t.x = 1\n"
            "T.x = 0\n"
            "if t.x:\n" + if_both("sk-live", "sk-dead"),
            False,
        ),
        "twoinst": (
            "class T:\n"
            "    x = 1\n"
            "t1 = T()\n"
            "t2 = T()\n"
            "t1.x = 0\n"
            "if t2.x:\n" + if_both("ti-live", "ti-dead"),
            False,
        ),
        "initzero": (
            "class T:\n"
            "    x = 1\n"
            "    def __init__(self):\n"
            "        self.x = 0\n"
            "t = T()\n"
            "if t.x:\n"
            "    def parse(x):\n"
            "        return 'iz-dead-only'\n",
            True,
        ),
        "initlive": (
            "class T:\n"
            "    x = 0\n"
            "    def __init__(self):\n"
            "        self.x = 1\n"
            "t = T()\n"
            "if t.x:\n" + if_both("izl-live", "izl-dead"),
            True,
        ),
        "initonly": (
            "class T:\n"
            "    def __init__(self):\n"
            "        self.x = 1\n"
            "t = T()\n"
            "if t.x:\n" + if_both("io-live", "io-dead"),
            True,
        ),
        "emptyinit": (
            "class T:\n"
            "    x = 1\n"
            "    def __init__(self):\n"
            "        pass\n"
            "t = T()\n"
            "if t.x:\n" + if_both("ei-live", "ei-dead"),
            True,
        ),
        "delattr": (
            "class T:\n"
            "    x = 1\n"
            "del T.x\n"
            "if T.x:\n"
            "    def parse(x):\n"
            "        return 'da-dead-only'\n",
            False,
        ),
        "delname": (
            "x = 1\n"
            "del x\n"
            "if x:\n"
            "    def parse(y):\n"
            "        return 'dn-dead-only'\n",
            False,
        ),
        "subassign": (
            "xs = [1]\n"
            "xs[0] = 0\n"
            "if xs[0]:\n" + if_both("sa-live", "sa-dead"),
            True,
        ),
        "dictassign": (
            "d = {1: 1}\n"
            "d[1] = 0\n"
            "if d[1]:\n" + if_both("da2-live", "da2-dead"),
            True,
        ),
        "sliceassign": (
            "xs = [1]\n"
            "xs[:] = []\n"
            "if xs:\n" + if_both("sla-live", "sla-dead"),
            True,
        ),
        "classouter": (
            "class T:\n"
            "    x = 1\n"
            "class U:\n"
            "    y = T.x\n"
            "if U.y:\n" + if_both("co2-live", "co2-dead"),
            False,
        ),
        "classifbody": (
            "class T:\n"
            "    if True:\n"
            "        x = 1\n"
            "if T.x:\n" + if_both("cif-live", "cif-dead"),
            False,
        ),
        "unpackattr": (
            "class T:\n"
            "    x = 1\n"
            "    y = 1\n"
            "T.x, T.y = 0, 0\n"
            "if T.x:\n" + if_both("ua-live", "ua-dead"),
            False,
        ),
        "multiattr": (
            "class T:\n"
            "    x = 1\n"
            "    y = 1\n"
            "T.x = T.y = 0\n"
            "if T.x:\n" + if_both("ma2-live", "ma2-dead"),
            False,
        ),
        "methodtruthy": (
            "class T:\n"
            "    def go(self):\n"
            "        return 0\n"
            "if T.go:\n" + if_both("mt-live", "mt-dead"),
            True,
        ),
        "instmethod": (
            "class T:\n"
            "    x = 1\n"
            "    def go(self):\n"
            "        return 0\n"
            "t = T()\n"
            "if t.go:\n" + if_both("im-live", "im-dead"),
            True,
        ),
        "classbase": (
            "class T:\n"
            "    x = 1\n"
            "class U(T):\n"
            "    pass\n"
            "if U.x:\n" + if_both("cb-live", "cb-dead"),
            True,
        ),
        "forattr": (
            "class T:\n"
            "    x = 1\n"
            "for T.x in [0]:\n"
            "    pass\n"
            "if T.x:\n" + if_both("fa-live", "fa-dead"),
            False,
        ),
        "txlistsub": (
            "class T:\n"
            "    x = [1]\n"
            "T.x[0] = 0\n"
            "if T.x[0]:\n" + if_both("tls-live", "tls-dead"),
            True,
        ),
        "txlistif": (
            "class T:\n"
            "    x = [1]\n"
            "if T.x[0]:\n" + if_both("tli-live", "tli-dead"),
            False,
        ),
        "txreal": (
            "class T:\n"
            "    x = 1\n"
            "T.x = 0\n"
            "if T.x.real:\n" + if_both("txr-live", "txr-dead"),
            False,
        ),
        "nottx": (
            "class T:\n"
            "    x = 1\n"
            "T.x = 0\n"
            "if not T.x:\n" + if_both("nt-live", "nt-dead"),
            False,
        ),
        "cmplt": (
            "class T:\n"
            "    x = 1\n"
            "T.x = 0\n"
            "if T.x < 1:\n" + if_both("clt-live", "clt-dead"),
            False,
        ),
        "walruszero": (
            "if (n := 0):\n" + if_both("wz-live", "wz-dead"),
            False,
        ),
        "fmtrspec": ("if f'{1!r:s}':\n" + if_both("frs-live", "frs-dead"), False),
        "fmtaspec": ("if f'{1!a}':\n" + if_both("fas-live", "fas-dead"), False),
        "noneif": (
            "if None:\n"
            "    def parse(x):\n"
            "        return 'ni-dead-only'\n",
            False,
        ),
        "emptyset0": ("if {0}:\n" + if_both("ez-live", "ez-dead"), False),
        "emptystr": (
            "if '':\n"
            "    def parse(x):\n"
            "        return 'es-dead-only'\n",
            False,
        ),
        "ellipsis": ("if ...:\n" + if_both("el-live", "el-dead"), False),
        "modstr": ("if '%s' % 1:\n" + if_both("ms3-live", "ms3-dead"), False),
        "mulzero": (
            "if 'x' * 0:\n"
            "    def parse(x):\n"
            "        return 'mz-dead-only'\n",
            False,
        ),
        "strsub": ("if 'abc'[0]:\n" + if_both("ss-live", "ss-dead"), False),
        "assertfalse": (
            "assert False\n"
            "def parse(x):\n"
            "    return 'af-dead-only'\n",
            True,
        ),
        "raisemod": (
            "raise ValueError('x')\n"
            "def parse(x):\n"
            "    return 'rm-dead-only'\n",
            True,
        ),
        "dunderfile": ("if __file__:\n" + if_both("df-live", "df-dead"), True),
        "dundername": ("if __name__:\n" + if_both("dna-live", "dna-dead"), True),
        "classistrue": (
            "class T:\n"
            "    x = 0\n"
            "if T:\n" + if_both("ct-live", "ct-dead"),
            False,
        ),
        "annnew": (
            "class T:\n"
            "    x = 0\n"
            "T.y: int = 1\n"
            "if T.y:\n" + if_both("an2-live", "an2-dead"),
            False,
        ),
        "compfromattr": (
            "class T:\n"
            "    x = [1]\n"
            "if [y for y in T.x]:\n" + if_both("cfa-live", "cfa-dead"),
            False,
        ),
        "delinstlookup": (
            "class T:\n"
            "    x = 1\n"
            "t = T()\n"
            "del T.x\n"
            "if t.x:\n"
            "    def parse(x):\n"
            "        return 'dil-dead-only'\n",
            False,
        ),
        "forelsebreak": (
            "for _ in [1]:\n"
            "    def parse(x):\n"
            "        return 'feb-live'\n"
            "    break\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'feb-else'\n",
            True,
        ),
        "whiletrue": (
            "while True:\n"
            "    def parse(x):\n"
            "        return 'wt-live'\n"
            "    break\n",
            True,
        ),
        "forrange": (
            "for _ in range(1):\n"
            "    def parse(x):\n"
            "        return 'fr-live'\n",
            True,
        ),
        "forrange0": (
            "for _ in range(0):\n"
            "    def parse(x):\n"
            "        return 'fr0-dead-only'\n",
            True,
        ),
        "aug": (
            "n = 1\n"
            "n += -1\n"
            "if n:\n" + if_both("aug-live", "aug-dead"),
            True,
        ),
        "calllen": (
            "if len([]):\n" + if_both("cl-live", "cl-dead"),
            True,
        ),
        "callset": (
            "if set():\n"
            "    def parse(x):\n"
            "        return 'cs-dead-only'\n",
            True,
        ),
        "runtime": (
            "import os\n"
            "flag = os.environ.get('NO_SUCH_BINDNAME_FLAG')\n"
            "if flag:\n" + if_both("rt-live", "rt-dead"),
            True,
        ),
        "trycan": (
            "try:\n"
            "    def parse(x):\n"
            "        return 'try-body'\n"
            "except Exception:\n"
            "    def parse(x):\n"
            "        return 'except-body'\n",
            True,
        ),
        "lambda_": ("parse = lambda x: ('lam', x)\n", True),
        "matchdyn": (
            "import os\n"
            "match os.name:\n"
            "    case 'posix':\n"
            "        def parse(x):\n"
            "            return 'posix-live'\n"
            "    case _:\n"
            "        def parse(x):\n"
            "            return 'other-dead'\n",
            True,
        ),
        "conjugate": (
            "if (1).conjugate():\n" + if_both("cj-live", "cj-dead"),
            True,
        ),
        "callelt": (
            "if [len(x) for x in ['a']]:\n" + if_both("cec-live", "cec-dead"),
            True,
        ),
        "typecall": (
            "T = type('T', (), {'x': 1})\n"
            "if T.x:\n" + if_both("tc-live", "tc-dead"),
            True,
        ),
        "forsecond": (
            "for x in [0, 1]:\n"
            "    if x:\n"
            "        def parse(y):\n"
            "            return 'fs-live'\n",
            True,
        ),
        "augattr": (
            "class T:\n"
            "    x = 1\n"
            "T.x += -1\n"
            "if T.x:\n" + if_both("aua-live", "aua-dead"),
            True,
        ),
        "delattreelse": (
            "class T:\n"
            "    x = 1\n"
            "del T.x\n"
            "if T.x:\n" + if_both("dae-live", "dae-dead"),
            False,
        ),
        "delnameelse": (
            "x = 1\n"
            "del x\n"
            "if x:\n" + if_both("dne-live", "dne-dead"),
            False,
        ),
        "classiffalse": (
            "class T:\n"
            "    if False:\n"
            "        x = 1\n"
            "    else:\n"
            "        x = 0\n"
            "if T.x:\n" + if_both("cff-live", "cff-dead"),
            False,
        ),
        "classforbody": (
            "class T:\n"
            "    for _ in [1]:\n"
            "        x = 1\n"
            "if T.x:\n" + if_both("cfb-live", "cfb-dead"),
            False,
        ),
        "classunpack": (
            "class T:\n"
            "    x, y = 1, 0\n"
            "if T.x:\n" + if_both("cu-live", "cu-dead"),
            False,
        ),
        "subclassinst": (
            "class T:\n"
            "    x = 1\n"
            "class U(T):\n"
            "    pass\n"
            "t = U()\n"
            "if t.x:\n" + if_both("sbi-live", "sbi-dead"),
            True,
        ),
        "subclassoverride": (
            "class T:\n"
            "    x = 1\n"
            "class U(T):\n"
            "    x = 0\n"
            "if U.x:\n" + if_both("sbo-live", "sbo-dead"),
            False,
        ),
        "unpackoneattr": (
            "class T:\n"
            "    x = 1\n"
            "T.x, = (0,)\n"
            "if T.x:\n" + if_both("uoa-live", "uoa-dead"),
            False,
        ),
        "asyncmethod": (
            "class T:\n"
            "    async def go(self):\n"
            "        return 0\n"
            "if T.go:\n" + if_both("am-live", "am-dead"),
            True,
        ),
        "classnested": (
            "class T:\n"
            "    x = 1\n"
            "    class U:\n"
            "        y = x\n"
            "if T.U.y:\n" + if_both("cn-live", "cn-dead"),
            False,
        ),
        "classanninner": (
            "class T:\n"
            "    if True:\n"
            "        x: int = 1\n"
            "if T.x:\n" + if_both("cai2-live", "cai2-dead"),
            False,
        ),
        "namedelattr": (
            "class T:\n"
            "    x = 1\n"
            "obj = T\n"
            "del obj.x\n"
            "if T.x:\n"
            "    def parse(x):\n"
            "        return 'nda-dead-only'\n",
            False,
        ),
        "instdelclassattr": (
            "class T:\n"
            "    x = 1\n"
            "t = T()\n"
            "del t.x\n"
            "if t.x:\n"
            "    def parse(x):\n"
            "        return 'idc-dead-only'\n",
            True,
        ),
        "classmethod_": (
            "class T:\n"
            "    @classmethod\n"
            "    def go(cls):\n"
            "        return 0\n"
            "if T.go:\n" + if_both("cm-live", "cm-dead"),
            True,
        ),
        "staticmethod_": (
            "class T:\n"
            "    @staticmethod\n"
            "    def go():\n"
            "        return 0\n"
            "if T.go:\n" + if_both("sm-live", "sm-dead"),
            True,
        ),
        "classwalrus": (
            "class T:\n"
            "    if (x := 1):\n"
            "        y = x\n"
            "if T.y:\n" + if_both("cw-live", "cw-dead"),
            False,
        ),
        "basesstar": (
            "class T:\n"
            "    x = 1\n"
            "class U(*(T,)):\n"
            "    pass\n"
            "if U.x:\n" + if_both("bs-live", "bs-dead"),
            True,
        ),
        "matchclassattr": (
            "class T:\n"
            "    x = 1\n"
            "    y = 0\n"
            "match T.x:\n"
            "    case 1:\n"
            "        def parse(x):\n"
            "            return 'mca-live'\n"
            "    case _:\n"
            "        def parse(x):\n"
            "            return 'mca-dead'\n",
            False,
        ),
        "forattrbody": (
            "class T:\n"
            "    x = 1\n"
            "for T.x in [0]:\n"
            "    def parse(x):\n"
            "        return 'fab-live'\n"
            "    break\n",
            False,
        ),
        "classnestedif": (
            "class T:\n"
            "    if True:\n"
            "        if True:\n"
            "            x = 1\n"
            "if T.x:\n" + if_both("cni-live", "cni-dead"),
            False,
        ),
        "classiffor": (
            "class T:\n"
            "    if True:\n"
            "        for _ in [1]:\n"
            "            x = 1\n"
            "if T.x:\n" + if_both("cifor-live", "cifor-dead"),
            False,
        ),
        "classmatch": (
            "class T:\n"
            "    match 1:\n"
            "        case 1:\n"
            "            x = 1\n"
            "        case _:\n"
            "            x = 0\n"
            "if T.x:\n" + if_both("cmh-live", "cmh-dead"),
            False,
        ),
        "classwhile": (
            "class T:\n"
            "    while False:\n"
            "        x = 0\n"
            "    else:\n"
            "        x = 1\n"
            "if T.x:\n" + if_both("cwh-live", "cwh-dead"),
            True,
        ),
        "notdelattreelse": (
            "class T:\n"
            "    x = 1\n"
            "del T.x\n"
            "if not T.x:\n" + if_both("nda2-live", "nda2-dead"),
            False,
        ),
        "ordelattreelse": (
            "class T:\n"
            "    x = 1\n"
            "del T.x\n"
            "if T.x or True:\n" + if_both("oda-live", "oda-dead"),
            False,
        ),
        "anddelattreelse": (
            "class T:\n"
            "    x = 1\n"
            "del T.x\n"
            "if T.x and True:\n" + if_both("ada-live", "ada-dead"),
            False,
        ),
        "cmpdelattreelse": (
            "class T:\n"
            "    x = 1\n"
            "del T.x\n"
            "if T.x == 1:\n" + if_both("cda-live", "cda-dead"),
            False,
        ),
        "bindelattreelse": (
            "class T:\n"
            "    x = 1\n"
            "del T.x\n"
            "if T.x + 1:\n" + if_both("bda-live", "bda-dead"),
            False,
        ),
        "ifexpdelattreelse": (
            "class T:\n"
            "    x = 1\n"
            "del T.x\n"
            "if T.x if True else 0:\n" + if_both("ida-live", "ida-dead"),
            False,
        ),
        "subdelattreelse": (
            "class T:\n"
            "    x = 1\n"
            "del T.x\n"
            "if T.x[0]:\n" + if_both("sda-live", "sda-dead"),
            False,
        ),
        "notdelnameelse": (
            "x = 1\n"
            "del x\n"
            "if not x:\n" + if_both("ndn-live", "ndn-dead"),
            False,
        ),
        "classforfalse": (
            "class T:\n"
            "    for _ in []:\n"
            "        x = 1\n"
            "    else:\n"
            "        x = 0\n"
            "if T.x:\n" + if_both("cff2-live", "cff2-dead"),
            False,
        ),
        "classwalrusassign": (
            "class T:\n"
            "    y = (x := 1)\n"
            "if T.x:\n" + if_both("cwa-live", "cwa-dead"),
            False,
        ),
        "classifwalrus": (
            "class T:\n"
            "    if (x := 1):\n"
            "        y = x\n"
            "if T.y:\n" + if_both("ciw-live", "ciw-dead"),
            False,
        ),
        "classanninner2": (
            "class T:\n"
            "    if True:\n"
            "        x: int = 1\n"
            "if T.x:\n" + if_both("cai3-live", "cai3-dead"),
            False,
        ),
    }
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        files = {f"{name}.py": body for name, (body, _p) in remaining.items()}
        files["pkg_parse.py"] = PARSE_MOVED
        write_fixture(tmp, files)
        listed = run_cli(["-C", tmp, "parse"])
        for name, (_body, park) in remaining.items():
            check_list_vs_honesty(tmp, name, listed=listed, declared_park=park)

    banner("C5. --file remaining alias shapes")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        root = write_fixture(
            tmp,
            {
                "pkg_parse.py": PARSE_MOVED,
                "dictsub.py": "import pkg_parse\nparse = pkg_parse.__dict__['parse']\n",
                "varsget.py": "import pkg_parse\nparse = vars(pkg_parse)['parse']\n",
                "attrget.py": (
                    "import operator, pkg_parse\n"
                    "parse = operator.attrgetter('parse')(pkg_parse)\n"
                ),
                "getattrdef.py": (
                    "import pkg_parse\n"
                    "parse = getattr(pkg_parse, 'parse', None)\n"
                ),
                "dynattr.py": (
                    "import pkg_parse\n"
                    "name = 'parse'\n"
                    "parse = getattr(pkg_parse, name)\n"
                ),
                "ifexpas.py": (
                    "import pkg_parse\n"
                    "parse = pkg_parse.parse if True else None\n"
                ),
                "impmod.py": (
                    "import importlib\n"
                    "m = importlib.import_module('pkg_parse')\n"
                    "parse = m.parse\n"
                ),
                "builtinsget.py": (
                    "import builtins, pkg_parse\n"
                    "parse = builtins.getattr(pkg_parse, 'parse')\n"
                ),
                "annattr.py": (
                    "import pkg_parse\n"
                    "parse: object = pkg_parse.parse\n"
                ),
                "getitem.py": (
                    "import pkg_parse\n"
                    "parse = pkg_parse.__dict__.get('parse')\n"
                ),
                "paren.py": (
                    "import pkg_parse\n"
                    "parse = (pkg_parse.parse)\n"
                ),
                "itemget.py": (
                    "import operator, pkg_parse\n"
                    "parse = operator.itemgetter('parse')(pkg_parse.__dict__)\n"
                ),
                "constget.py": (
                    "import pkg_parse\n"
                    "parse = getattr(pkg_parse, 'parse')\n"
                ),
                "callwrap.py": (
                    "import pkg_parse\n"
                    "parse = (lambda f: f)(pkg_parse.parse)\n"
                ),
                "listsub.py": (
                    "import pkg_parse\n"
                    "parse = [pkg_parse.parse][0]\n"
                ),
            },
        )
        declared_park = {
            "dictsub",
            "varsget",
            "attrget",
            "dynattr",
            "ifexpas",
            "impmod",
            "getitem",
            "itemget",
            "callwrap",
            "listsub",
        }
        for name in (
            "dictsub.py",
            "varsget.py",
            "attrget.py",
            "getattrdef.py",
            "dynattr.py",
            "ifexpas.py",
            "impmod.py",
            "builtinsget.py",
            "annattr.py",
            "getitem.py",
            "paren.py",
            "itemget.py",
            "constget.py",
            "callwrap.py",
            "listsub.py",
        ):
            mod = Path(name).stem
            hon = honesty(f"from {mod} import parse; print(parse(' z '))", cwd=tmp)
            fproc = run_cli(["-C", tmp, "--file", str(root / name), "parse"])
            qproc = run_cli(["-C", tmp, "--from", mod, "parse"])
            file_follows = "pkg_parse.parse" in fproc.stdout and "strip" in fproc.stdout
            from_follows = "pkg_parse.parse" in qproc.stdout and "strip" in qproc.stdout
            print(
                f"-- {mod} hon_rc={hon.returncode} hon={hon.stdout.strip()!r} "
                f"file_rc={fproc.returncode} file_follows={file_follows} "
                f"from_follows={from_follows} file_kind_assign={'kind\\tassign' in fproc.stdout}"
            )
            if hon.returncode == 0 and "moved" in hon.stdout:
                if not file_follows:
                    if mod in declared_park:
                        mark_park(f"file_{mod}", "honesty moved, --file not follow (declared)")
                    else:
                        mark_diverge(f"file_{mod}", "honesty moved, --file not follow (not declared park)")
                        show(fproc, f"--file {mod}")
                        show(qproc, f"--from {mod}")
                if not from_follows:
                    mark_diverge(f"from_{mod}", "honesty moved, --from not follow")
                    show(qproc, f"--from {mod}")

    banner("C6. isolate also still static + leftover ast still helper")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "keep.py": "def parse(x):\n    return 'kept'\n",
                "killer.py": "import sys\ndef parse(x):\n    return 'dead'\nsys.exit(9)\n",
                "ast.py": AST_LEFTOVER,
            },
        )
        proc = run_cli(["-C", tmp, "--from", "keep", "parse"])
        print("also_killer", "also\tkiller.parse" in proc.stdout)
        print("also_ast", "also\tast.parse" in proc.stdout)
        print("keep_ok", proc.returncode == 0 and "kept" in proc.stdout)
        astq = run_cli(["-C", tmp, "--from", "ast", "parse"], cwd="/tmp")
        print("ast_leftover_still", "leftover-ast" in astq.stdout and "Cellar" not in astq.stdout)

    banner("C7. declared parks confirm (not MUTATE)")
    if SPEC012.exists():
        show(run_cli(["-C", str(SPEC012), "test_a"]), "list test_a 012")
        show(run_cli(["-C", str(SPEC012), "--from", "run_orders", "test_a"]), "from run_orders test_a")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        fifo = Path(tmp) / "fifo.py"
        os.mkfifo(fifo)
        t0 = time.time()
        proc = run_cli(["-C", tmp, "--file", str(fifo), "parse"], timeout=3)
        dt = time.time() - t0
        print("fifo_elapsed", round(dt, 3), "not_a_file", "not a file" in proc.stderr, "rc", proc.returncode)
        mark_park("fifo", "declared --file FIFO not a file")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "pkg_parse.py": PARSE_MOVED,
                "starer.py": "from pkg_parse import *\n",
                "peper.py": (
                    "def __getattr__(name):\n"
                    "    if name == 'parse':\n"
                    "        def parse(x):\n"
                    "            return 'pep562'\n"
                    "        return parse\n"
                    "    raise AttributeError(name)\n"
                ),
                "execer.py": "exec(\"def parse(x):\\n    return 'execed'\\n\")\n",
                "lam.py": "parse = lambda x: ('lam', x)\n",
                "trylive.py": (
                    "try:\n"
                    "    def parse(x):\n"
                    "        return 'try-body'\n"
                    "except Exception:\n"
                    "    def parse(x):\n"
                    "        return 'except-body'\n"
                ),
                "hugesrc.py": (
                    "def parse(x):\n"
                    "    '''" + ("H" * 4000) + "'''\n"
                    "    return 'huge'\n"
                ),
                "matchdyn.py": (
                    "import os\n"
                    "match os.name:\n"
                    "    case 'posix':\n"
                    "        def parse(x):\n"
                    "            return 'posix-live'\n"
                    "    case _:\n"
                    "        def parse(x):\n"
                    "            return 'other-dead'\n"
                ),
                "nested.py": (
                    "def run():\n"
                    "    def parse(x):\n"
                    "        return 'nested-inner'\n"
                    "    return parse\n"
                    "def parse(x):\n"
                    "    return 'nested-mod'\n"
                ),
            },
        )
        for mod in ("starer", "peper", "execer", "lam", "trylive", "hugesrc", "matchdyn", "nested"):
            arg = " z " if mod == "starer" else "z"
            hon = honesty(f"from {mod} import parse; print(parse({arg!r}))", cwd=tmp)
            q = run_cli(["-C", tmp, "--from", mod, "parse"])
            listed = run_cli(["-C", tmp, "parse"])
            print(
                f"PARK {mod} hon_rc={hon.returncode} hon={hon.stdout.strip()!r} "
                f"qrc={q.returncode} list_has={list_has_bind(listed.stdout, f'{mod}.parse')} "
                f"huge={'H'*20 in q.stdout if mod=='hugesrc' else 'n/a'}"
            )
            mark_park(mod, "declared park probe")

    banner("C8. NEW leftover-identity after mutate-16 (const-known, not declared parks)")
    new_identity = {
        "andeq": ("if (1 and 2) == 2:\n" + if_both("ae-live", "ae-dead"), False),
        "andistrue": ("if (1 and 2) is True:\n" + if_both("ait-live", "ait-dead"), False),
        "oreq": ("if (0 or 3) == 3:\n" + if_both("oe-live", "oe-dead"), False),
        "andassign": (
            "x = 1 and 2\n"
            "if x == 2:\n" + if_both("aa2-live", "aa2-dead"),
            False,
        ),
        "andzerois": (
            "x = 1 and 0\n"
            "if x is 0:\n" + if_both("az-live", "az-dead"),
            False,
        ),
        "orassign": (
            "x = 0 or 3\n"
            "if x == 3:\n" + if_both("oa-live", "oa-dead"),
            False,
        ),
        "andlistis": ("if ([] and [1]) is False:\n" + if_both("ali-live", "ali-dead"), False),
        "classand": (
            "class T:\n"
            "    x = 1 and 2\n"
            "if T.x == 2:\n" + if_both("caand-live", "caand-dead"),
            False,
        ),
        "classor": (
            "class T:\n"
            "    x = 0 or 3\n"
            "if T.x == 3:\n" + if_both("cor-live", "cor-dead"),
            False,
        ),
        "mixedassign": (
            "class T:\n"
            "    x = 1\n"
            "T.x = y = 0\n"
            "if T.x:\n" + if_both("mx-live", "mx-dead"),
            False,
        ),
        "mixedassigny": (
            "class T:\n"
            "    x = 1\n"
            "y = T.x = 0\n"
            "if T.x:\n" + if_both("mxy-live", "mxy-dead"),
            False,
        ),
        "mixedyval": (
            "class T:\n"
            "    x = 1\n"
            "y = T.x = 0\n"
            "if y:\n" + if_both("myv-live", "myv-dead"),
            False,
        ),
        "mixedinst": (
            "class T:\n"
            "    x = 1\n"
            "t = T()\n"
            "t.x = y = 0\n"
            "if t.x:\n" + if_both("mi-live", "mi-dead"),
            False,
        ),
        "listdelattr": (
            "class T:\n"
            "    x = 1\n"
            "del T.x\n"
            "if [T.x]:\n" + if_both("lda-live", "lda-dead"),
            False,
        ),
        "tupdelattr": (
            "class T:\n"
            "    x = 1\n"
            "del T.x\n"
            "if (T.x,):\n" + if_both("tda-live", "tda-dead"),
            False,
        ),
        "setdelattr": (
            "class T:\n"
            "    x = 1\n"
            "del T.x\n"
            "if {T.x}:\n" + if_both("sda2-live", "sda2-dead"),
            False,
        ),
        "dictdelattr": (
            "class T:\n"
            "    x = 1\n"
            "del T.x\n"
            "if {T.x: 1}:\n" + if_both("dda-live", "dda-dead"),
            False,
        ),
        "dictvdelattr": (
            "class T:\n"
            "    x = 1\n"
            "del T.x\n"
            "if {1: T.x}:\n" + if_both("dvd-live", "dvd-dead"),
            False,
        ),
        "fmtdelattr": (
            "class T:\n"
            "    x = 1\n"
            "del T.x\n"
            "if f'{T.x}':\n" + if_both("fda-live", "fda-dead"),
            False,
        ),
        "gendelattr": (
            "class T:\n"
            "    x = 1\n"
            "del T.x\n"
            "if (y for y in T.x):\n" + if_both("gda-live", "gda-dead"),
            False,
        ),
        "compdelattr": (
            "class T:\n"
            "    x = 1\n"
            "del T.x\n"
            "if [y for y in T.x]:\n" + if_both("cda2-live", "cda2-dead"),
            False,
        ),
        "stardelattr": (
            "class T:\n"
            "    x = 1\n"
            "del T.x\n"
            "if [*[T.x]]:\n" + if_both("startd-live", "startd-dead"),
            False,
        ),
        "matchseq": (
            "match (1,):\n"
            "    case (1,):\n"
            "        def parse(x):\n"
            "            return 'msq-live'\n"
            "    case _:\n"
            "        def parse(x):\n"
            "            return 'msq-dead'\n",
            False,
        ),
        "matchlist": (
            "match [1]:\n"
            "    case [1]:\n"
            "        def parse(x):\n"
            "            return 'ml-live'\n"
            "    case _:\n"
            "        def parse(x):\n"
            "            return 'ml-dead'\n",
            False,
        ),
        "matchmap": (
            "match {1: 1}:\n"
            "    case {1: 1}:\n"
            "        def parse(x):\n"
            "            return 'mm-live'\n"
            "    case _:\n"
            "        def parse(x):\n"
            "            return 'mm-dead'\n",
            False,
        ),
        "classmatchseq": (
            "class T:\n"
            "    match (1,):\n"
            "        case (1,):\n"
            "            x = 1\n"
            "        case _:\n"
            "            x = 0\n"
            "if T.x:\n" + if_both("cms-live", "cms-dead"),
            False,
        ),
        "matchas": (
            "class T:\n"
            "    match 1:\n"
            "        case x:\n"
            "            y = x\n"
            "if T.y:\n" + if_both("mas-live", "mas-dead"),
            False,
        ),
        "matchasval": (
            "class T:\n"
            "    match 1:\n"
            "        case 1 as x:\n"
            "            y = x\n"
            "if T.y:\n" + if_both("mav-live", "mav-dead"),
            False,
        ),
        "matchstar": (
            "match [1, 2]:\n"
            "    case [1, *rest]:\n"
            "        def parse(x):\n"
            "            return 'mst-live'\n"
            "    case _:\n"
            "        def parse(x):\n"
            "            return 'mst-dead'\n",
            False,
        ),
        "nestedcls": (
            "class T:\n"
            "    class U:\n"
            "        y = 1\n"
            "if T.U.y:\n" + if_both("ncl-live", "ncl-dead"),
            False,
        ),
        "mixedunpack": (
            "class T:\n"
            "    x = 1\n"
            "T.x, y = 0, 0\n"
            "if T.x:\n" + if_both("mu-live", "mu-dead"),
            False,
        ),
        "triname": (
            "a = b = c = 0\n"
            "if a:\n" + if_both("tn-live", "tn-dead"),
            False,
        ),
        "matchor": (
            "match 2:\n"
            "    case 1 | 2:\n"
            "        def parse(x):\n"
            "            return 'mo-live'\n"
            "    case _:\n"
            "        def parse(x):\n"
            "            return 'mo-dead'\n",
            False,
        ),
        "and3eq": ("if (1 and 2 and 3) == 3:\n" + if_both("a3-live", "a3-dead"), False),
        "isnottrue": ("if 1 is not True:\n" + if_both("int-live", "int-dead"), False),
        "classdelname": (
            "class T:\n"
            "    x = 1\n"
            "    del x\n"
            "if T.x:\n"
            "    def parse(x):\n"
            "        return 'cdn-live'\n",
            False,
        ),

        "classifexp": (
            "class T:\n"
            "    x = 1 if True else 0\n"
            "if T.x:\n" + if_both("cie-live", "cie-dead"),
            False,
        ),
        "classbinop": (
            "class T:\n"
            "    x = 1 + 0\n"
            "if T.x:\n" + if_both("cbp-live", "cbp-dead"),
            False,
        ),
        "classsub": (
            "class T:\n"
            "    x = [1][0]\n"
            "if T.x:\n" + if_both("csb-live", "csb-dead"),
            False,
        ),
        "classnot": (
            "class T:\n"
            "    x = not 0\n"
            "if T.x:\n" + if_both("cno-live", "cno-dead"),
            False,
        ),
        "classin": (
            "class T:\n"
            "    x = 1 in [1]\n"
            "if T.x:\n" + if_both("cin-live", "cin-dead"),
            False,
        ),
        "classfornested": (
            "class T:\n"
            "    for _ in [1]:\n"
            "        for _ in [1]:\n"
            "            x = 1\n"
            "if T.x:\n" + if_both("cfn-live", "cfn-dead"),
            False,
        ),
        "classforunp": (
            "class T:\n"
            "    for x, y in [(1, 0)]:\n"
            "        z = x\n"
            "if T.z:\n" + if_both("cfu-live", "cfu-dead"),
            False,
        ),
        "classstarunp": (
            "class T:\n"
            "    x, *rest = 1, 2, 3\n"
            "if T.x:\n" + if_both("csu-live", "csu-dead"),
            False,
        ),
        "classdelname": (
            "class T:\n"
            "    x = 1\n"
            "    del x\n"
            "if T.x:\n" + if_both("cdn-live", "cdn-dead"),
            False,
        ),
        "chained": ("if 0 < 1 < 2:\n" + if_both("ch-live", "ch-dead"), False),
        "isconst": ("if 1 is not 0:\n" + if_both("isc-live", "isc-dead"), False),
        "notin": ("if 1 not in []:\n" + if_both("nin-live", "nin-dead"), False),
        "bitor": ("if 1 | 0:\n" + if_both("bo-live", "bo-dead"), False),
        "lshift": ("if 1 << 1:\n" + if_both("ls-live", "ls-dead"), False),
        "pow0": ("if 2 ** 0:\n" + if_both("pw-live", "pw-dead"), False),
        "floordiv": ("if 3 // 2:\n" + if_both("fdv-live", "fdv-dead"), False),
        "emptytuple": (
            "if ():\n"
            "    def parse(x):\n"
            "        return 'et-dead-only'\n",
            False,
        ),
        "zerotuple": ("if (0,):\n" + if_both("zt-live", "zt-dead"), False),
        "dicttruth": ("if {0: 0}:\n" + if_both("dt-live", "dt-dead"), False),
        "bytes1": ("if b'\\x01':\n" + if_both("b1-live", "b1-dead"), False),
        "bytes0": (
            "if b'':\n"
            "    def parse(x):\n"
            "        return 'b0-dead-only'\n",
            False,
        ),
        "complex0": (
            "if 0j:\n"
            "    def parse(x):\n"
            "        return 'cj0-dead-only'\n",
            False,
        ),
        "complex1": ("if 1j:\n" + if_both("cj1-live", "cj1-dead"), False),
        "float0": (
            "if 0.0:\n"
            "    def parse(x):\n"
            "        return 'f0-dead-only'\n",
            False,
        ),
        "istrue": ("if True is True:\n" + if_both("it-live", "it-dead"), False),
        "noneeq": ("if None == None:\n" + if_both("ne-live", "ne-dead"), False),
        "classfstr": (
            "class T:\n"
            "    x = f'{1}'\n"
            "if T.x:\n" + if_both("cfs-live", "cfs-dead"),
            False,
        ),
        "classwalruslist": (
            "class T:\n"
            "    xs = [(x := 1)]\n"
            "if T.x:\n" + if_both("cwl-live", "cwl-dead"),
            False,
        ),
        "matchguard": (
            "match 1:\n"
            "    case 1 if True:\n"
            "        def parse(x):\n"
            "            return 'mg-live'\n"
            "    case _:\n"
            "        def parse(x):\n"
            "            return 'mg-dead'\n",
            False,
        ),
        "matchguardf": (
            "match 1:\n"
            "    case 1 if False:\n"
            "        def parse(x):\n"
            "            return 'mgf-dead'\n"
            "    case _:\n"
            "        def parse(x):\n"
            "            return 'mgf-live'\n",
            False,
        ),
        "starredattr": (
            "class T:\n"
            "    x = 1\n"
            "T.x, *rest = 0, 1\n"
            "if T.x:\n" + if_both("sa3-live", "sa3-dead"),
            False,
        ),
        "andpolarity": ("if 1 and 2:\n" + if_both("ap-live", "ap-dead"), False),
        "orpolarity": (
            "if 0 or 0:\n"
            "    def parse(x):\n"
            "        return 'op-dead-only'\n",
            False,
        ),
    }
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        files = {f"{name}.py": body for name, (body, _p) in new_identity.items()}
        files["pkg_parse.py"] = PARSE_MOVED
        write_fixture(tmp, files)
        listed = run_cli(["-C", tmp, "parse"])
        for name, (_body, park) in new_identity.items():
            check_list_vs_honesty(tmp, name, listed=listed, declared_park=park)

    banner("SUMMARY")
    print("HONOR", HONOR)
    print("HONOR_ANY", any(HONOR.values()))
    print("DIVERGES")
    for tag, detail in DIVERGES:
        print(f"  {tag}: {detail}")
    print("DIVERGE_COUNT", len(DIVERGES))
    print("PARK_COUNT", len(PARKS))
    remaining_keys = (
        "classforbody",
        "classforfalse",
        "classnestedif",
        "classiffor",
        "classmatch",
        "classwalrus",
        "classwalrusassign",
        "classifwalrus",
        "classanninner",
        "classanninner2",
        "classifbody",
        "classiffalse",
        "notdelattreelse",
        "ordelattreelse",
        "anddelattreelse",
        "cmpdelattreelse",
        "bindelattreelse",
        "ifexpdelattreelse",
        "subdelattreelse",
        "notdelnameelse",
        "methodtruthy",
        "instmethod",
        "asyncmethod",
        "classmethod_",
        "staticmethod_",
        "classbase",
        "subclassinst",
        "basesstar",
        "delname",
        "delnameelse",
        "delattreelse",
        "namedelattr",
        "delinstlookup",
        "dunderfile",
        "dundername",
        "assertfalse",
        "raisemod",
        "classwhile",
        "classnested",
        "classunpack",
        "forattr",
        "unpackattr",
        "andeq",
        "andistrue",
        "oreq",
        "andassign",
        "andzerois",
        "orassign",
        "andlistis",
        "classand",
        "classor",
        "mixedassign",
        "mixedassigny",
        "mixedyval",
        "mixedinst",
        "listdelattr",
        "tupdelattr",
        "setdelattr",
        "dictdelattr",
        "dictvdelattr",
        "fmtdelattr",
        "gendelattr",
        "compdelattr",
        "stardelattr",
        "matchseq",
        "matchlist",
        "matchmap",
        "classmatchseq",
        "matchas",
        "matchasval",
        "matchstar",
        "nestedcls",
        "mixedunpack",
        "triname",
        "matchor",
        "and3eq",
        "isnottrue",
        "classdelname",
        "classifexp",
        "classbinop",
        "classsub",
        "classnot",
        "classin",
        "classfornested",
        "classforunp",
        "classstarunp",
        "classdelname",
        "chained",
        "isconst",
        "notin",
        "bitor",
        "lshift",
        "pow0",
        "floordiv",
        "emptytuple",
        "zerotuple",
        "dicttruth",
        "bytes1",
        "bytes0",
        "complex0",
        "complex1",
        "float0",
        "istrue",
        "noneeq",
        "classfstr",
        "classwalruslist",
        "matchguard",
        "matchguardf",
        "starredattr",
        "andpolarity",
        "orpolarity",
    )
    later = [t for t, _ in DIVERGES if any(k in t for k in remaining_keys)]
    print("REMAINING_DIVERGES", later)
    ast_static = [
        t
        for t, _ in DIVERGES
        if any(
            k in t
            for k in (
                "classforbody",
                "classforfalse",
                "classnestedif",
                "classiffor",
                "classmatch",
                "classwalrus",
                "classwalrusassign",
                "classifwalrus",
                "classanninner",
                "classanninner2",
                "classifbody",
                "notdelattreelse",
                "ordelattreelse",
                "anddelattreelse",
                "cmpdelattreelse",
                "bindelattreelse",
                "ifexpdelattreelse",
                "subdelattreelse",
                "notdelnameelse",
                "andeq",
                "andistrue",
                "oreq",
                "andassign",
                "andzerois",
                "orassign",
                "andlistis",
                "classand",
                "classor",
                "mixedassign",
                "mixedassigny",
                "mixedyval",
                "mixedinst",
                "listdelattr",
                "tupdelattr",
                "setdelattr",
                "dictdelattr",
                "dictvdelattr",
                "fmtdelattr",
                "gendelattr",
                "compdelattr",
                "stardelattr",
                "matchseq",
                "matchlist",
                "matchmap",
                "classmatchseq",
                "matchas",
                "matchasval",
                "matchstar",
                "nestedcls",
                "mixedunpack",
                "triname",
                "matchor",
                "and3eq",
                "isnottrue",
                "classdelname",
                "classwalruslist",
                "starredattr",
            )
        )
    ]
    exec_park = [
        t
        for t, _ in PARKS
        if any(
            k in t
            for k in (
                "methodtruthy",
                "instmethod",
                "asyncmethod",
                "classmethod_",
                "staticmethod_",
                "classbase",
                "subclassinst",
                "basesstar",
                "subassign",
                "dictassign",
                "sliceassign",
                "txlistsub",
                "initzero",
                "initlive",
                "initonly",
                "emptyinit",
                "whiletrue",
                "classwhile",
            )
        )
    ]
    print("AST_STATIC_DIVERGES", ast_static)
    print("EXEC_PARK", exec_park)
    print("VERDICT_HINT", "MUTATE" if ast_static else ("KILL" if any(HONOR.values()) else "KEEP"))


if __name__ == "__main__":
    main()
