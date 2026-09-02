#!/usr/bin/env python3
"""Host attacks against post-MUTATE-7 bindname. Archive CLI only."""
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
SCRATCH = RUN / "destroyers/_bindname7_scratch"
SPEC013 = RUN / "specimens/specimen-013/files"
SPEC012 = RUN / "specimens/specimen-012/files"
SPEC010 = RUN / "specimens/specimen-010/files"

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
            loader = importlib.machinery.SourceFileLoader('bindname_cli7', {str(CLI)!r})
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

    banner("H4. leftover io/encodings/os kind=def while honesty ImportError")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "io.py": "def parse(x):\n    return ('leftover-io', x)\n",
                "encodings.py": "def parse(x):\n    return ('leftover-encodings', x)\n",
                "os.py": "def parse(x):\n    return ('leftover-os', x)\n",
                "pkg_parse.py": PARSE_MOVED,
            },
        )
        kill4 = False
        for mod in ("io", "encodings", "os"):
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
        HONOR["4_io_encodings_os_kind_def"] = kill4

    banner("H5. leftover sys.py kind=def while honesty ImportError")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "sys.py": "def parse(x):\n    return ('leftover-sys', x)\n",
                "builtins.py": "def parse(x):\n    return ('leftover-builtins', x)\n",
                "pkg_parse.py": PARSE_MOVED,
            },
        )
        kill5 = False
        for mod in ("sys", "builtins"):
            hon = honesty(f"from {mod} import parse; print(parse('z'))", cwd=tmp)
            proc = run_cli(["-C", tmp, "--from", mod, "parse"], cwd="/tmp")
            show(hon, f"honesty {mod}")
            show(proc, f"bindname {mod}")
            kind_def = proc.returncode == 0 and "kind\tdef" in proc.stdout
            leftover_body = f"leftover-{mod}" in proc.stdout
            print(f"KILL_{mod}_kind_def", kind_def)
            if hon.returncode != 0 and (kind_def or leftover_body):
                kill5 = True
        HONOR["5_sys_kind_def"] = kill5

    banner("H6. leftover importlib.util kind=def while honesty cannot bind")
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
        kill6 = hon.returncode != 0 and (
            (proc.returncode == 0 and "kind\tdef" in proc.stdout)
            or "leftover-importlib-util" in proc.stdout
        )
        print("KILL_importlib_util_kind_def", kill6)
        HONOR["6_importlib_util_kind_def"] = kill6
        listed = run_cli(["-C", tmp, "parse"], cwd="/tmp")
        show(listed, "list importlib tree")
        print("list_has_importlib.util.parse", list_has_bind(listed.stdout, "importlib.util.parse"))

    banner("H7. leftover importlib.py file / importlib.abc is miss while honesty leftover")
    kill7 = False
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
            kill7 = True
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
            kill7 = True
            print("KILL_importlib_abc_miss")
    HONOR["7_importlib_file_or_abc_miss"] = kill7

    banner("H8. list last-wins if +1 / if ~0 as dead else while query live")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "uadd.py": "if +1:\n" + if_both("uadd-live", "uadd-dead"),
                "invert.py": "if ~0:\n" + if_both("inv-live", "inv-dead"),
                "uzero.py": (
                    "if +0:\n"
                    "    def parse(x):\n"
                    "        return 'uadd-dead-only'\n"
                ),
                "pkg_parse.py": PARSE_MOVED,
            },
        )
        kill8 = False
        for mod, live, dead in (("uadd", "uadd-live", "uadd-dead"), ("invert", "inv-live", "inv-dead")):
            hon = honesty(f"from {mod} import parse; print(parse('z'))", cwd=tmp)
            q = run_cli(["-C", tmp, "--from", mod, "parse"])
            listed = run_cli(["-C", tmp, "parse"])
            row = list_source_for(listed.stdout, mod)
            show(hon, f"honesty {mod}")
            show(q, f"query {mod}")
            print(f"LIST_ROW {mod}\n", row)
            fired = (
                hon.stdout.strip() == live
                and live in q.stdout
                and dead in row
                and live not in row
            )
            print(f"KILL_{mod}_list_dead", fired)
            kill8 = kill8 or fired
        hon0 = honesty("from uzero import parse; print(parse('z'))", cwd=tmp)
        q0 = run_cli(["-C", tmp, "--from", "uzero", "parse"])
        listed0 = run_cli(["-C", tmp, "parse"])
        show(hon0, "honesty uzero")
        show(q0, "query uzero")
        show(listed0, "list uzero")
        fired0 = q0.returncode != 0 and list_has_bind(listed0.stdout, "uzero.parse")
        print("KILL_uzero_list_kind_def", fired0)
        HONOR["8_list_uadd_invert_dead"] = kill8 or fired0

    banner("H9. list if 1 in [1] as dead while query live")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "inin.py": "if 1 in [1]:\n" + if_both("in-live", "in-dead"),
                "inempty.py": (
                    "if 1 in []:\n"
                    "    def parse(x):\n"
                    "        return 'in-empty-dead'\n"
                ),
                "pkg_parse.py": PARSE_MOVED,
            },
        )
        hon = honesty("from inin import parse; print(parse('z'))", cwd=tmp)
        q = run_cli(["-C", tmp, "--from", "inin", "parse"])
        listed = run_cli(["-C", tmp, "parse"])
        row = list_source_for(listed.stdout, "inin")
        show(hon, "honesty inin")
        show(q, "query inin")
        print("LIST_ROW inin\n", row)
        kill9 = (
            hon.stdout.strip() == "in-live"
            and "in-live" in q.stdout
            and "in-dead" in row
            and "in-live" not in row
        )
        hon_e = honesty("from inempty import parse; print(parse('z'))", cwd=tmp)
        q_e = run_cli(["-C", tmp, "--from", "inempty", "parse"])
        listed_e = run_cli(["-C", tmp, "parse"])
        show(hon_e, "honesty inempty")
        show(q_e, "query inempty")
        show(listed_e, "list inempty")
        kill9e = q_e.returncode != 0 and list_has_bind(listed_e.stdout, "inempty.parse")
        print("KILL_in_list_dead", kill9)
        print("KILL_inempty_list_kind_def", kill9e)
        HONOR["9_list_in_dead"] = kill9 or kill9e

    banner("H10. list flag, other = True, True; if flag as dead while query live")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "tupleunp.py": (
                    "flag, other = True, True\n"
                    "if flag:\n" + if_both("tu-live", "tu-dead")
                )
            },
        )
        hon = honesty("from tupleunp import parse; print(parse('z'))", cwd=tmp)
        q = run_cli(["-C", tmp, "--from", "tupleunp", "parse"])
        listed = run_cli(["-C", tmp, "parse"])
        row = list_source_for(listed.stdout, "tupleunp")
        show(hon, "honesty tupleunp")
        show(q, "query tupleunp")
        print("LIST_ROW tupleunp\n", row)
        kill10 = (
            hon.stdout.strip() == "tu-live"
            and "tu-live" in q.stdout
            and "tu-dead" in row
            and "tu-live" not in row
        )
        print("KILL_tupleunp_list_dead", kill10)
        HONOR["10_list_tupleunp_dead"] = kill10

    banner("H11. list TYPE_CHECKING = True; if TYPE_CHECKING as dead while query live")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "localtc.py": (
                    "TYPE_CHECKING = True\n"
                    "if TYPE_CHECKING:\n" + if_both("ltc-live", "ltc-dead")
                )
            },
        )
        hon = honesty("from localtc import parse; print(parse('z'))", cwd=tmp)
        q = run_cli(["-C", tmp, "--from", "localtc", "parse"])
        listed = run_cli(["-C", tmp, "parse"])
        row = list_source_for(listed.stdout, "localtc")
        show(hon, "honesty localtc")
        show(q, "query localtc")
        print("LIST_ROW localtc\n", row)
        kill11 = (
            hon.stdout.strip() == "ltc-live"
            and "ltc-live" in q.stdout
            and "ltc-dead" in row
            and "ltc-live" not in row
        )
        print("KILL_localtc_list_dead", kill11)
        HONOR["11_list_localtc_dead"] = kill11

    banner("H12. THIN_WRAPPER of two greps / importlib.util with no leftover-identity join")
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
        HONOR["12_thin_wrapper"] = not (naive_stdlib and bind_leftover and also_moved)

    banner("C0. frozen map on host")
    frozen_code = textwrap.dedent(
        """
        import _imp, sys
        names = [
            'importlib','importlib.util','importlib.machinery','importlib.abc',
            'importlib.resources','importlib.metadata','importlib.readers',
            'importlib.simple','importlib._bootstrap','importlib._bootstrap_external',
            'importlib.resources.abc','encodings','encodings.utf_8','zipimport',
            '_frozen_importlib','io','os','sys','builtins','tokenize','ast','inspect',
            'json','codecs','collections','collections.abc','os.path','posixpath',
            'typing','pathlib','abc','re','types','functools','dataclasses','enum',
            'operator','copyreg','site','linecache','keyword','stat','genericpath',
            'reprlib','contextlib','argparse','warnings','tempfile','subprocess',
        ]
        print('PRE_HAS_importlib', 'importlib' in sys.modules)
        print('PRE_HAS_json', 'json' in sys.modules)
        print('PRE_HAS_pathlib', 'pathlib' in sys.modules)
        print('PRE_HAS_inspect', 'inspect' in sys.modules)
        print('PRE_HAS_typing', 'typing' in sys.modules)
        print('PRE_HAS_dataclasses', 'dataclasses' in sys.modules)
        print('PRE_HAS_warnings', 'warnings' in sys.modules)
        print('PRE_HAS_contextlib', 'contextlib' in sys.modules)
        for n in names:
            top = n.split('.',1)[0]
            try:
                fr = _imp.is_frozen(n)
            except Exception as e:
                fr = f'ERR {e}'
            builtin = top in sys.builtin_module_names
            print(f'FROZEN {n} frozen={fr} builtin={builtin} pre={n in sys.modules} top_pre={top in sys.modules}')
        """
    )
    show(subprocess.run([sys.executable, "-c", frozen_code], capture_output=True, text=True), "frozen map")

    banner("C1. leftover importlib/ package + tokenize still helper")
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

    banner("C2. other leftover stdlib names honesty vs CLI")
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

    banner("C3. mutate-7 claimed const-known If still match")
    claimed = {
        "uadd": ("if +1:\n" + if_both("uadd-live", "uadd-dead"), "uadd-live"),
        "invert": ("if ~0:\n" + if_both("inv-live", "inv-dead"), "inv-live"),
        "inlist": ("if 1 in [1]:\n" + if_both("in-live", "in-dead"), "in-live"),
        "notin": ("if 1 not in []:\n" + if_both("notin-live", "notin-dead"), "notin-live"),
        "instr": ("if 'a' in 'ab':\n" + if_both("instr-live", "instr-dead"), "instr-live"),
        "inset": ("if 1 in {1}:\n" + if_both("inset-live", "inset-dead"), "inset-live"),
        "indict": ("if 1 in {1: 2}:\n" + if_both("indict-live", "indict-dead"), "indict-live"),
        "intup": ("if 1 in (1,):\n" + if_both("intup-live", "intup-dead"), "intup-live"),
        "inbytes": ("if b'a' in b'ab':\n" + if_both("inb-live", "inb-dead"), "inb-live"),
        "tupleunp": ("flag, other = True, True\n" "if flag:\n" + if_both("tu-live", "tu-dead"), "tu-live"),
        "listunp": ("[flag, other] = [True, True]\n" "if flag:\n" + if_both("lu-live", "lu-dead"), "lu-live"),
        "localtc": ("TYPE_CHECKING = True\n" "if TYPE_CHECKING:\n" + if_both("ltc-live", "ltc-dead"), "ltc-live"),
        "anntc": ("TYPE_CHECKING: bool = True\n" "if TYPE_CHECKING:\n" + if_both("atc-live", "atc-dead"), "atc-live"),
        "add": ("if 1 + 1:\n" + if_both("add-live", "add-dead"), "add-live"),
        "emptyifelse": ("if []:\n" + if_both("empty-live", "empty-dead"), "empty-dead"),
        "ifexp": ("flag = True if 1 else False\n" "if flag:\n" + if_both("ie-live", "ie-dead"), "ie-live"),
        "multi": ("flag = other = True\n" "if other:\n" + if_both("mt-live", "mt-dead"), "mt-live"),
        "notempty": ("if not []:\n" + if_both("ne-live", "ne-dead"), "ne-live"),
        "chaincmp": ("if 1 < 2 < 3:\n" + if_both("cc-live", "cc-dead"), "cc-live"),
        "binopn": ("n = 1\nn = n + -1\nif n:\n" + if_both("bn-live", "bn-dead"), "bn-dead"),
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

    banner("C4. remaining const-known If / unpack / env (not declared parks)")
    remaining = {
        "subl": ("if [1][0]:\n" + if_both("subl-live", "subl-dead"), False),
        "sub0": (
            "if [0][0]:\n"
            "    def parse(x):\n"
            "        return 'sub0-dead-only'\n",
            False,
        ),
        "subd": ("if {0: 1}[0]:\n" + if_both("subd-live", "subd-dead"), False),
        "subt": ("if (1,)[0]:\n" + if_both("subt-live", "subt-dead"), False),
        "subs": ("if 'x'[0]:\n" + if_both("subs-live", "subs-dead"), False),
        "subb": ("if b'a'[0]:\n" + if_both("subb-live", "subb-dead"), False),
        "subassign": ("flag = [True][0]\nif flag:\n" + if_both("sa-live", "sa-dead"), False),
        "slice1": ("if [1][:1]:\n" + if_both("sl-live", "sl-dead"), False),
        "slice0": (
            "if [1][1:]:\n"
            "    def parse(x):\n"
            "        return 'slice0-dead-only'\n",
            False,
        ),
        "fstr": ("if f'x':\n" + if_both("fs-live", "fs-dead"), False),
        "fstrfmt": ("if f'{1}':\n" + if_both("ff-live", "ff-dead"), False),
        "fstrempty": (
            "if f'':\n"
            "    def parse(x):\n"
            "        return 'fe-dead-only'\n",
            False,
        ),
        "starlist": (
            "if [*[]]:\n"
            "    def parse(x):\n"
            "        return 'star-dead-only'\n",
            False,
        ),
        "starnonempty": ("if [*[1]]:\n" + if_both("sn-live", "sn-dead"), False),
        "dictunp": (
            "if {**{}}:\n"
            "    def parse(x):\n"
            "        return 'du-dead-only'\n",
            False,
        ),
        "dictunp1": ("if {**{0: 1}}:\n" + if_both("d1-live", "d1-dead"), False),
        "attrreal": ("if (1).real:\n" + if_both("ar-live", "ar-dead"), False),
        "attr0": (
            "if (0).real:\n"
            "    def parse(x):\n"
            "        return 'a0-dead-only'\n",
            False,
        ),
        "nestedunp": (
            "flag, (other,) = True, (True,)\n"
            "if flag:\n" + if_both("nu-live", "nu-dead"),
            False,
        ),
        "starunp": (
            "flag, *rest = True, True\n"
            "if flag:\n" + if_both("su-live", "su-dead"),
            False,
        ),
        "starunprest": (
            "flag, *rest = False, True\n"
            "if rest:\n" + if_both("sr-live", "sr-dead"),
            False,
        ),
        "otherfalse": (
            "flag, other = True, False\n"
            "if other:\n"
            "    def parse(x):\n"
            "        return 'of-dead-only'\n",
            False,
        ),
        "compempty": (
            "if [x for x in []]:\n"
            "    def parse(x):\n"
            "        return 'ce-dead-only'\n",
            False,
        ),
        "compone": ("if [x for x in [1]]:\n" + if_both("co-live", "co-dead"), False),
        "genalways": ("if (x for x in []):\n" + if_both("ga-live", "ga-dead"), False),
        "forlive": (
            "for _ in [1]:\n"
            "    def parse(x):\n"
            "        return 'for-live'\n",
            False,
        ),
        "forempty": (
            "for _ in []:\n"
            "    def parse(x):\n"
            "        return 'for-dead-only'\n",
            False,
        ),
        "whilefalse": (
            "while False:\n"
            "    def parse(x):\n"
            "        return 'wf-dead-only'\n",
            False,
        ),
        "matchsub": (
            "match [1][0]:\n"
            "    case 1:\n"
            "        def parse(x):\n"
            "            return 'ms-live'\n"
            "    case _:\n"
            "        def parse(x):\n"
            "            return 'ms-dead'\n",
            False,
        ),
        "matchconst": (
            "match 1:\n"
            "    case 1:\n"
            "        def parse(x):\n"
            "            return 'mc-live'\n"
            "    case _:\n"
            "        def parse(x):\n"
            "            return 'mc-dead'\n",
            False,
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
        "ifexpfile": (
            "flag = True if True else False\n"
            "if flag:\n" + if_both("ix-live", "ix-dead"),
            False,
        ),
        "invertm1": (
            "if ~-1:\n"
            "    def parse(x):\n"
            "        return 'im-dead-only'\n",
            False,
        ),
        "uaddtrue": ("if +True:\n" + if_both("ut-live", "ut-dead"), False),
        "notnot1": ("if not not 1:\n" + if_both("nn-live", "nn-dead"), False),
        "ellipsis": ("if ...:\n" + if_both("ell-live", "ell-dead"), False),
        "complex0": (
            "if 0j:\n"
            "    def parse(x):\n"
            "        return 'z0-dead-only'\n",
            False,
        ),
        "bytesempty": (
            "if b'':\n"
            "    def parse(x):\n"
            "        return 'be-dead-only'\n",
            False,
        ),
        "joinedstar": ("if f'{1}' in f'{1}':\n" + if_both("js-live", "js-dead"), False),
        "subneg": ("if [1, 2][-1]:\n" + if_both("sn1-live", "sn1-dead"), False),
        "subslice2": ("if [0, 1][1:2]:\n" + if_both("ss2-live", "ss2-dead"), False),
        "nameconst": ("X = 1\nif [X][0]:\n" + if_both("nc-live", "nc-dead"), False),
        "tc_rebind": (
            "from typing import TYPE_CHECKING\n"
            "TYPE_CHECKING = True\n"
            "if TYPE_CHECKING:\n" + if_both("tr-live", "tr-dead"),
            False,
        ),
        "nestedif": (
            "if True:\n"
            "    if [1][0]:\n" + if_both("ni-live", "ni-dead"),
            False,
        ),
        "walrussub": ("if (flag := [1][0]):\n" + if_both("ws-live", "ws-dead"), False),
        "boolop_sub": ("if [1][0] and [1][0]:\n" + if_both("bs-live", "bs-dead"), False),
        "compare_sub": ("if [1][0] == 1:\n" + if_both("csb-live", "csb-dead"), False),
        "in_sub": ("if 1 in [1][:]:\n" + if_both("isb-live", "isb-dead"), False),
        "tupleval": (
            "pair = True, True\n"
            "flag, other = pair\n"
            "if flag:\n" + if_both("tv-live", "tv-dead"),
            False,
        ),
        "starfirst": (
            "*rest, flag = False, True\n"
            "if flag:\n" + if_both("sf-live", "sf-dead"),
            False,
        ),
        "classattr": (
            "class T:\n"
            "    x = 1\n"
            "if T.x:\n" + if_both("ca-live", "ca-dead"),
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
            },
        )
        for mod in ("starer", "peper", "execer", "lam", "trylive", "hugesrc", "matchdyn"):
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

    banner("C8. leftover importlib.util file (not package) vs honesty")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "importlib.py": "def parse(x):\n    return ('leftover-importlib-file', x)\n",
                "util.py": "def parse(x):\n    return ('leftover-util', x)\n",
            },
        )
        hon = honesty("from importlib.util import parse; print(parse('z'))", cwd=tmp)
        q = run_cli(["-C", tmp, "--from", "importlib.util", "parse"], cwd="/tmp")
        show(hon, "honesty importlib.util with leftover importlib.py file (no package)")
        show(q, "bindname importlib.util with leftover importlib.py file")

    banner("SUMMARY")
    print("HONOR", HONOR)
    print("HONOR_ANY", any(HONOR.values()))
    print("DIVERGES")
    for tag, detail in DIVERGES:
        print(f"  {tag}: {detail}")
    print("DIVERGE_COUNT", len(DIVERGES))
    print("PARK_COUNT", len(PARKS))


if __name__ == "__main__":
    main()
