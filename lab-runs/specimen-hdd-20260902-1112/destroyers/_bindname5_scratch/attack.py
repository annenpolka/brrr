#!/usr/bin/env python3
"""Host attacks against post-MUTATE-5 bindname. Archive CLI only."""
from __future__ import annotations

import os
import stat
import subprocess
import sys
import tempfile
import textwrap
import time
from pathlib import Path

RUN = Path("/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112")
CLI = RUN / "lineages/candidate-bind/bindname"
SCRATCH = RUN / "destroyers/_bindname5_scratch"
SPEC013 = RUN / "specimens/specimen-013/files"
SPEC010 = RUN / "specimens/specimen-010/files"
SPEC012 = RUN / "specimens/specimen-012/files"

AST_LEFTOVER = "def parse(x):\n    return ('leftover-ast', x)\n"
PARSE_MOVED = "def parse(x):\n    return ('moved', x.strip())\n"
UTIL_LEGACY = "def parse(x):\n    return ('legacy', x)\n"


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
        print("KILL_stdlib_file", any(s in proc.stdout for s in ("Cellar", "lib/python")))
        print("leftover-ast_in_source", "leftover-ast" in proc.stdout)
        print("starts_query", proc.stdout.startswith("query\t"))
        listed = run_cli(["-C", tmp, "parse"], cwd="/tmp")
        show(listed, "list leftover ast")

    banner("H1b. in-process logical name + restore")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(tmp, {"ast.py": AST_LEFTOVER, "pkg_parse.py": PARSE_MOVED})
        code = textwrap.dedent(
            f"""
            import importlib.machinery, importlib.util, sys
            from pathlib import Path
            loader = importlib.machinery.SourceFileLoader('bindname_cli5', {str(CLI)!r})
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
        print("KILL_hijack", proc.returncode in (9, 11) or not proc.stdout.startswith("query\t"))

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

    banner("H4. leftover sys/builtins/io/encodings/os kind=def while honesty ImportError")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "sys.py": "def parse(x):\n    return ('leftover-sys', x)\n",
                "builtins.py": "def parse(x):\n    return ('leftover-builtins', x)\n",
                "io.py": "def parse(x):\n    return ('leftover-io', x)\n",
                "encodings.py": "def parse(x):\n    return ('leftover-encodings', x)\n",
                "os.py": "def parse(x):\n    return ('leftover-os', x)\n",
                "pkg_parse.py": PARSE_MOVED,
            },
        )
        for mod in ("sys", "builtins", "io", "encodings", "os"):
            hon = honesty(f"from {mod} import parse; print(parse('z'))", cwd=tmp)
            proc = run_cli(["-C", tmp, "--from", mod, "parse"], cwd="/tmp")
            show(hon, f"honesty {mod}")
            show(proc, f"bindname {mod}")
            kind_def = proc.returncode == 0 and "kind\tdef" in proc.stdout
            leftover_body = f"leftover-{mod}" in proc.stdout
            print(f"KILL_{mod}_kind_def", kind_def)
            print(f"KILL_{mod}_leftover_body", leftover_body)
            print(f"KILL_{mod}_os.stat", "has no attribute 'stat'" in proc.stderr)
        listed = run_cli(["-C", tmp, "parse"], cwd="/tmp")
        show(listed, "list with unshadowable leftovers")
        for ghost in ("sys.parse", "builtins.parse", "io.parse", "encodings.parse", "os.parse"):
            print(f"list_has_{ghost}", ghost in listed.stdout)

    banner("H5. THIN_WRAPPER? grep+inspect vs leftover ast isolate")
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
        print("naive_is_stdlib", "Cellar" in naive.stdout or "lib/python" in naive.stdout)
        print("bindname_is_leftover", "leftover-ast" in proc.stdout and "Cellar" not in proc.stdout)
        print("also_moved", "also\tpkg_parse.parse" in proc.stdout)

    banner("C1. leftover tokenize.py honesty leftover vs tokenize.open miss")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "tokenize.py": "def parse(x):\n    return ('leftover-tokenize', x)\n",
                "pkg_parse.py": PARSE_MOVED,
            },
        )
        hon = honesty(
            "from tokenize import parse; print(parse('z')); import tokenize; print(tokenize.__file__)",
            cwd=tmp,
        )
        proc = run_cli(["-C", tmp, "--from", "tokenize", "parse"], cwd="/tmp")
        show(hon, "honesty tokenize")
        show(proc, "bindname tokenize")
        print("tokenize_honesty_leftover", hon.returncode == 0 and "leftover-tokenize" in hon.stdout)
        print("tokenize_cli_leftover", proc.returncode == 0 and "leftover-tokenize" in proc.stdout)
        print("tokenize_open_miss", "has no attribute 'open'" in proc.stderr)
        print("tokenize_stdlib_file", any(s in proc.stdout for s in ("Cellar", "lib/python")))
        listed = run_cli(["-C", tmp, "parse"], cwd="/tmp")
        show(listed, "list tokenize")

    banner("C2. leftover stdlib name sweep honesty vs bindname")
    names = [
        "os", "io", "importlib", "encodings", "codecs", "tokenize", "types",
        "functools", "collections", "pathlib", "posixpath", "genericpath", "stat",
        "time", "_collections_abc", "_sitebuiltins", "inspect", "json", "ast",
        "_thread", "marshal", "posix", "gc", "itertools", "errno", "sys", "builtins",
        "abc", "re", "warnings", "weakref", "traceback", "linecache", "copyreg",
        "enum", "operator", "keyword", "site", "zipimport", "typing", "dataclasses",
        "argparse", "contextlib", "subprocess", "tempfile", "unittest", "textwrap",
        "reprlib", "sitecustomize", "fnmatch", "glob", "shutil", "signal",
        "threading", "_thread", "posixpath", "ntpath", "genericpath",
        "importlib.util",  # skipped as filename
        "copy", "pprint", "decimal", "fractions", "random", "hashlib",
        "base64", "binascii", "struct", "array", "select", "socket",
        "ssl", "http", "urllib", "email", "html", "xml", "json",
        "pickle", "shelve", "sqlite3", "csv", "configparser",
        "logging", "getopt", "getpass", "curses", "platform",
        "sysconfig", "pkgutil", "modulefinder", "runpy", "pydoc",
        "doctest", "unittest", "test", "bdb", "faulthandler",
        "pdb", "profile", "timeit", "trace", "tracemalloc",
        "gc", "inspect", "dis", "pickletools", "tabnanny",
        "py_compile", "compileall", "pyclbr", "venv", "ensurepip",
        "zipapp", "symtable", "token", "keyword", "tokenize",
        "ast", "_ast", "parser", "code", "codeop",
        "codecs", "encodings", "unicodedata", "stringprep",
        "readline", "rlcompleter", "atexit", "traceback",
        "gc", "inspect", "site", "sys", "builtins", "io",
        "os", "_imp", "posix", "nt", "winreg", "msvcrt",
        "fcntl", "grp", "pwd", "spwd", "termios", "tty",
        "pty", "pipes", "posixpath", "genericpath", "stat",
        "filecmp", "fileinput", "stat", "linecache",
        "shutil", "macpath",
        "types", "copyreg", "weakref", "abc", "collections",
        "heapq", "bisect", "array", "weakref", "types",
        "copy", "pprint", "reprlib", "enum",
        "numbers", "math", "cmath", "decimal", "fractions",
        "random", "statistics",
        "itertools", "functools", "operator",
        "pathlib", "os.path",
        "contextlib", "abc", "atexit",
        "dataclasses", "graphlib",
    ]
    # unique preserve order
    seen: set[str] = set()
    uniq = []
    for n in names:
        if n in seen or "." in n:
            continue
        seen.add(n)
        uniq.append(n)
    diverges = []
    match_refuse = []
    match_bind = []
    for mod in uniq:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
            write_fixture(
                tmp,
                {
                    f"{mod}.py": f"def parse(x):\n    return ('leftover-{mod}', x)\n",
                    "pkg_parse.py": PARSE_MOVED,
                },
            )
            hon = honesty(
                f"from {mod} import parse; print(parse('z')); import {mod} as m; print('FILE', getattr(m,'__file__',None))",
                cwd=tmp,
            )
            proc = run_cli(["-C", tmp, "--from", mod, "parse"], cwd="/tmp")
            hon_binds = hon.returncode == 0 and f"leftover-{mod}" in hon.stdout
            cli_binds = (
                proc.returncode == 0
                and "kind\tdef" in proc.stdout
                and f"leftover-{mod}" in proc.stdout
            )
            cli_stdlib = any(s in proc.stdout for s in ("Cellar", "lib/python"))
            if hon.returncode != 0 and cli_binds:
                diverges.append((mod, "honesty_ImportError_cli_kind_def"))
                print(f"DIVERGE honesty_ImportError_cli_kind_def {mod}")
                show(hon, f"honesty {mod}")
                show(proc, f"bindname {mod}")
            elif hon_binds and (not cli_binds or cli_stdlib):
                diverges.append((mod, "honesty_leftover_cli_miss_or_stdlib"))
                print(f"DIVERGE honesty_leftover_cli_miss_or_stdlib {mod}")
                show(hon, f"honesty {mod}")
                show(proc, f"bindname {mod}")
            elif hon.returncode != 0 and proc.returncode == 0:
                diverges.append((mod, "honesty_fail_cli_ok"))
                print(f"DIVERGE honesty_fail_cli_ok {mod}")
                show(hon, f"honesty {mod}")
                show(proc, f"bindname {mod}")
            elif hon.returncode != 0 and proc.returncode != 0:
                match_refuse.append(mod)
            elif hon_binds and cli_binds and not cli_stdlib:
                match_bind.append(mod)
            else:
                diverges.append((mod, "other"))
                print(f"DIVERGE other {mod} hon_rc={hon.returncode} cli_rc={proc.returncode}")
                show(hon, f"honesty {mod}")
                show(proc, f"bindname {mod}")
    print("SWEEP_match_refuse", " ".join(match_refuse))
    print("SWEEP_match_bind", " ".join(match_bind))
    print("SWEEP_diverge", diverges)

    banner("C3. mutate-5 claimed: const-known If list is live")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "flagtrue.py": (
                    "flag = True\n"
                    "if flag:\n"
                    "    def parse(x):\n"
                    "        return 'live-flag'\n"
                    "else:\n"
                    "    def parse(x):\n"
                    "        return 'dead-else'\n"
                ),
                "eq.py": (
                    "if 1 == 1:\n"
                    "    def parse(x):\n"
                    "        return 'eq-live'\n"
                    "else:\n"
                    "    def parse(x):\n"
                    "        return 'eq-dead'\n"
                ),
                "tcalias.py": (
                    "from typing import TYPE_CHECKING as TC\n"
                    "if not TC:\n"
                    "    def parse(x):\n"
                    "        return 'live-not-tc'\n"
                    "else:\n"
                    "    def parse(x):\n"
                    "        return 'typed-else-tc'\n"
                ),
            },
        )
        for mod, live, dead in (
            ("flagtrue", "live-flag", "dead-else"),
            ("eq", "eq-live", "eq-dead"),
            ("tcalias", "live-not-tc", "typed-else-tc"),
        ):
            hon = honesty(f"from {mod} import parse; print(parse('z'))", cwd=tmp)
            q = run_cli(["-C", tmp, "--from", mod, "parse"])
            listed = run_cli(["-C", tmp, "parse"])
            row = list_source_for(listed.stdout, mod)
            print(f"-- {mod} honesty={hon.stdout.strip()!r} query_has_live={live in q.stdout} list_has_live={live in row} list_has_dead={dead in row}")
            print(f"DIVERGE_{mod}_list_dead", dead in row and live not in row)

    banner("C4. mutate-5 claimed: --file getattr / Name alias follow")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        root = write_fixture(
            tmp,
            {
                "pkg_parse.py": PARSE_MOVED,
                "getattrer.py": "import pkg_parse\nparse = getattr(pkg_parse, 'parse')\n",
                "aliaser.py": "from pkg_parse import parse as p\nparse = p\n",
            },
        )
        for name in ("getattrer.py", "aliaser.py"):
            mod = Path(name).stem
            hon = honesty(f"from {mod} import parse; print(parse(' z '))", cwd=tmp)
            fproc = run_cli(["-C", tmp, "--file", str(root / name), "parse"])
            qproc = run_cli(["-C", tmp, "--from", mod, "parse"])
            show(hon, f"honesty {mod}")
            show(fproc, f"--file {mod}")
            show(qproc, f"--from {mod}")
            print(f"file_follows_{mod}", "pkg_parse.parse" in fproc.stdout and "strip" in fproc.stdout)

    banner("R1. nested defs specimen-012 + holder")
    if SPEC012.exists():
        show(run_cli(["-C", str(SPEC012), "test_a"]), "list test_a 012")
        show(run_cli(["-C", str(SPEC012), "--from", "run_orders", "test_a"]), "from run_orders test_a")
        show(run_cli(["-C", str(SPEC012), "--from", "test_order", "test_a"]), "from test_order test_a")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "holder.py": (
                    "def run():\n"
                    "    def parse(x):\n"
                    "        return 'nested'\n"
                    "    return parse\n"
                    "def parse(x):\n"
                    "    return 'module-level'\n"
                )
            },
        )
        hon = honesty("from holder import parse; print(parse('z'))", cwd=tmp)
        q = run_cli(["-C", tmp, "--from", "holder", "parse"])
        listed = run_cli(["-C", tmp, "parse"])
        show(hon, "honesty nested")
        show(q, "query nested")
        show(listed, "list nested")
        print("nested_not_in_source", "nested" not in q.stdout or "module-level" in q.stdout)

    banner("R2. FIFO --file / /dev/stdin")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        fifo = Path(tmp) / "fifo.py"
        os.mkfifo(fifo)
        t0 = time.time()
        proc = run_cli(["-C", tmp, "--file", str(fifo), "parse"], timeout=3)
        dt = time.time() - t0
        show(proc, "fifo --file")
        print("fifo_elapsed", round(dt, 3))
        print("fifo_not_a_file", "not a file" in proc.stderr)
        proc2 = run_cli(["-C", tmp, "--file", "/dev/stdin", "parse"], stdin="def parse(x):\n    return 1\n")
        show(proc2, "/dev/stdin --file")
        print("stdin_elapsed_ok", True)

    banner("R3. exec / PEP562 / star as list bind")
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
                "execer.py": 'exec("def parse(x):\\n    return \'execed\'\\n")\n',
            },
        )
        for mod in ("starer", "peper", "execer"):
            hon = honesty(
                f"from {mod} import parse; print(parse(' z ' ) if callable(parse) else parse)",
                cwd=tmp,
            )
            q = run_cli(["-C", tmp, "--from", mod, "parse"])
            listed = run_cli(["-C", tmp, "parse"])
            show(hon, f"honesty {mod}")
            show(q, f"query {mod}")
            print(f"list_has_{mod}.parse", f"{mod}.parse" in listed.stdout)
            print(f"query_ok_{mod}", q.returncode == 0)
        show(run_cli(["-C", tmp, "parse"]), "list exec/pep/star")

    banner("R4. huge source dump")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        body = "def parse(x):\n    s = '" + ("A" * 200000) + "'\n    return s\n"
        write_fixture(tmp, {"huge.py": body})
        t0 = time.time()
        proc = run_cli(["-C", tmp, "--from", "huge", "parse"], timeout=8)
        dt = time.time() - t0
        print("huge_rc", proc.returncode, "elapsed", round(dt, 3), "stdout_bytes", len(proc.stdout))
        print("huge_starts_query", proc.stdout.startswith("query\t"))

    banner("R5. const-eval ceiling: BinOp / empty collections / IfExp / multi-target / AugAssign")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "add.py": (
                    "if 1 + 1:\n"
                    "    def parse(x):\n"
                    "        return 'add-live'\n"
                    "else:\n"
                    "    def parse(x):\n"
                    "        return 'add-dead'\n"
                ),
                "emptylist.py": (
                    "if []:\n"
                    "    def parse(x):\n"
                    "        return 'list-dead'\n"
                    "else:\n"
                    "    def parse(x):\n"
                    "        return 'list-live'\n"
                ),
                "emptytuple.py": (
                    "if ():\n"
                    "    def parse(x):\n"
                    "        return 'tup-dead'\n"
                    "else:\n"
                    "    def parse(x):\n"
                    "        return 'tup-live'\n"
                ),
                "ifexp.py": (
                    "flag = True if True else False\n"
                    "if flag:\n"
                    "    def parse(x):\n"
                    "        return 'ifexp-live'\n"
                    "else:\n"
                    "    def parse(x):\n"
                    "        return 'ifexp-dead'\n"
                ),
                "multi.py": (
                    "flag = other = True\n"
                    "if flag:\n"
                    "    def parse(x):\n"
                    "        return 'multi-live'\n"
                    "else:\n"
                    "    def parse(x):\n"
                    "        return 'multi-dead'\n"
                ),
                "aug.py": (
                    "n = 1\n"
                    "n += -1\n"
                    "if n:\n"
                    "    def parse(x):\n"
                    "        return 'aug-live'\n"
                    "else:\n"
                    "    def parse(x):\n"
                    "        return 'aug-dead'\n"
                ),
                "calllen.py": (
                    "if len([]):\n"
                    "    def parse(x):\n"
                    "        return 'len-dead'\n"
                    "else:\n"
                    "    def parse(x):\n"
                    "        return 'len-live'\n"
                ),
            },
        )
        for mod in ("add", "emptylist", "emptytuple", "ifexp", "multi", "aug", "calllen"):
            hon = honesty(f"from {mod} import parse; print(parse('z'))", cwd=tmp)
            q = run_cli(["-C", tmp, "--from", mod, "parse"])
            listed = run_cli(["-C", tmp, "parse"])
            row = list_source_for(listed.stdout, mod)
            print(
                f"-- {mod} honesty={hon.stdout.strip()!r} qrc={q.returncode} "
                f"query_src_has_honesty={hon.stdout.strip() in q.stdout} "
                f"list_row=\n{row}"
            )
            hon_val = hon.stdout.strip()
            list_mismatch = hon_val and hon_val not in row and q.returncode == 0
            print(f"LIST_VS_HONESTY_{mod}", list_mismatch)

    banner("R6. try/except last-wins / match without static subject")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "trylive.py": (
                    "try:\n"
                    "    def parse(x):\n"
                    "        return 'try-body'\n"
                    "except Exception:\n"
                    "    def parse(x):\n"
                    "        return 'except-body'\n"
                ),
                "dynmatch.py": (
                    "import os\n"
                    "x = os.environ.get('K', '1')\n"
                    "match x:\n"
                    "    case '1':\n"
                    "        def parse(y):\n"
                    "            return 'm-one'\n"
                    "    case _:\n"
                    "        def parse(y):\n"
                    "            return 'm-wild'\n"
                ),
            },
        )
        for mod in ("trylive", "dynmatch"):
            hon = honesty(f"from {mod} import parse; print(parse('z'))", cwd=tmp)
            q = run_cli(["-C", tmp, "--from", mod, "parse"])
            listed = run_cli(["-C", tmp, "parse"])
            show(hon, f"honesty {mod}")
            show(q, f"query {mod}")
            print("-- list", mod)
            print(list_source_for(listed.stdout, mod))

    banner("R7. --file remaining alias shapes")
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
            },
        )
        for name in (
            "dictsub.py",
            "varsget.py",
            "attrget.py",
            "getattrdef.py",
            "dynattr.py",
            "ifexpas.py",
            "impmod.py",
            "builtinsget.py",
        ):
            mod = Path(name).stem
            hon = honesty(f"from {mod} import parse; print(parse(' z '))", cwd=tmp)
            fproc = run_cli(["-C", tmp, "--file", str(root / name), "parse"])
            qproc = run_cli(["-C", tmp, "--from", mod, "parse"])
            print(
                f"-- {mod} honesty={hon.stdout.strip()!r} hon_rc={hon.returncode} "
                f"file_rc={fproc.returncode} file_runs_moved={'pkg_parse.parse' in fproc.stdout and 'strip' in fproc.stdout} "
                f"from_runs_moved={'pkg_parse.parse' in qproc.stdout and 'strip' in qproc.stdout} "
                f"file_kind_assign={'kind\\tassign' in fproc.stdout}"
            )
            if hon.returncode == 0 and "moved" in hon.stdout:
                if "pkg_parse.parse" not in fproc.stdout or "strip" not in fproc.stdout:
                    print(f"FILE_SPLIT_{mod}")
                    show(fproc, f"--file {mod}")
                    show(qproc, f"--from {mod}")

    banner("R8. lambda vs list / unwrapped decorator")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "lam.py": "parse = lambda x: ('lam', x)\n",
                "decer.py": (
                    "def wrap(fn):\n"
                    "    def inner(x):\n"
                    "        return ('wrap', fn(x))\n"
                    "    return inner\n"
                    "@wrap\n"
                    "def parse(x):\n"
                    "    return ('inner', x)\n"
                ),
            },
        )
        for mod in ("lam", "decer"):
            hon = honesty(
                f"from {mod} import parse; print(type(parse).__name__, getattr(parse,'__name__',None), parse('z'))",
                cwd=tmp,
            )
            q = run_cli(["-C", tmp, "--from", mod, "parse"])
            listed = run_cli(["-C", tmp, "parse"])
            show(hon, f"honesty {mod}")
            show(q, f"query {mod}")
            print(list_source_for(listed.stdout, mod))

    banner("R9. parent __init__ sys.exit / dependency killer")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "pkg/__init__.py": "import sys\nsys.exit(7)\n",
                "pkg/keep.py": "def parse(x):\n    return 'pkg-keep'\n",
                "dep.py": "import killer\ndef parse(x):\n    return 'dep'\n",
                "killer.py": "import sys\nsys.exit(9)\n",
            },
        )
        show(run_cli(["-C", tmp, "--from", "pkg.keep", "parse"]), "pkg.keep parent exit")
        show(run_cli(["-C", tmp, "--from", "dep", "parse"]), "dep imports killer")

    banner("R10. while False / for empty / if __name__==__main__")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "whiler.py": (
                    "def parse(x):\n    return 'before-while'\n"
                    "while False:\n"
                    "    def parse(x):\n"
                    "        return 'while-dead'\n"
                ),
                "forer.py": (
                    "def parse(x):\n    return 'before-for'\n"
                    "for _ in ():\n"
                    "    def parse(x):\n"
                    "        return 'for-dead'\n"
                ),
                "mainish.py": (
                    "if __name__ == '__main__':\n"
                    "    def parse(x):\n"
                    "        return 'main-only'\n"
                    "else:\n"
                    "    def parse(x):\n"
                    "        return 'import-body'\n"
                ),
            },
        )
        for mod in ("whiler", "forer", "mainish"):
            hon = honesty(f"from {mod} import parse; print(parse('z'))", cwd=tmp)
            q = run_cli(["-C", tmp, "--from", mod, "parse"])
            listed = run_cli(["-C", tmp, "parse"])
            show(hon, f"honesty {mod}")
            show(q, f"query {mod}")
            print(list_source_for(listed.stdout, mod))
            hon_val = hon.stdout.strip()
            row = list_source_for(listed.stdout, mod)
            print(f"LIST_VS_HONESTY_{mod}", hon_val not in row)

    banner("R11. leftover importlib package / typing / pathlib")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "importlib/__init__.py": "def parse(x):\n    return ('leftover-importlib', x)\n",
                "importlib/util.py": "def parse(x):\n    return ('leftover-importlib-util', x)\n",
            },
        )
        hon = honesty("from importlib import parse; print(parse('z'))", cwd=tmp)
        q = run_cli(["-C", tmp, "--from", "importlib", "parse"], cwd="/tmp")
        show(hon, "honesty leftover importlib pkg")
        show(q, "bindname leftover importlib pkg")
        hon2 = honesty("from importlib.util import parse; print(parse('z'))", cwd=tmp)
        q2 = run_cli(["-C", tmp, "--from", "importlib.util", "parse"], cwd="/tmp")
        show(hon2, "honesty leftover importlib.util")
        show(q2, "bindname leftover importlib.util")

    banner("R12. keep.py that imports leftover ast sibling")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "ast.py": AST_LEFTOVER,
                "keep.py": (
                    "import ast\n"
                    "def parse(x):\n"
                    "    return ('keep', ast.parse(x))\n"
                ),
            },
        )
        hon = honesty("from keep import parse; print(parse('z'))", cwd=tmp)
        proc = run_cli(["-C", tmp, "--from", "keep", "parse"], cwd="/tmp")
        show(hon, "honesty keep+ast")
        show(proc, "bindname keep+ast")

    banner("R13. TYPE_CHECKING without import / typing_extensions alias")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "bare.py": (
                    "if TYPE_CHECKING:\n"
                    "    def parse(x):\n"
                    "        return 'typed-bare'\n"
                    "else:\n"
                    "    def parse(x):\n"
                    "        return 'live-bare'\n"
                ),
                "tex.py": (
                    "from typing_extensions import TYPE_CHECKING as TC\n"
                    "if not TC:\n"
                    "    def parse(x):\n"
                    "        return 'live-tex'\n"
                    "else:\n"
                    "    def parse(x):\n"
                    "        return 'typed-tex'\n"
                ),
            },
        )
        for mod in ("bare", "tex"):
            hon = honesty(f"from {mod} import parse; print(parse('z'))", cwd=tmp)
            q = run_cli(["-C", tmp, "--from", mod, "parse"])
            listed = run_cli(["-C", tmp, "parse"])
            show(hon, f"honesty {mod}")
            show(q, f"query {mod}")
            print(list_source_for(listed.stdout, mod))

    banner("R14. runtime-unknown if flag both branches (declared)")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "runtime.py": (
                    "import os\n"
                    "flag = os.environ.get('BINDNAME_FLAG')\n"
                    "if flag:\n"
                    "    def parse(x):\n"
                    "        return 'env-live'\n"
                    "else:\n"
                    "    def parse(x):\n"
                    "        return 'env-else'\n"
                )
            },
        )
        hon = honesty("from runtime import parse; print(parse('z'))", cwd=tmp)
        q = run_cli(["-C", tmp, "--from", "runtime", "parse"])
        listed = run_cli(["-C", tmp, "parse"])
        show(hon, "honesty runtime")
        show(q, "query runtime")
        show(listed, "list runtime")

    banner("R15. leftover encodings/utf_8.py package member")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "encodings/__init__.py": "def parse(x):\n    return ('leftover-encodings-pkg', x)\n",
                "encodings/utf_8.py": "def parse(x):\n    return ('leftover-utf8', x)\n",
            },
        )
        hon = honesty("from encodings import parse; print(parse('z'))", cwd=tmp)
        q = run_cli(["-C", tmp, "--from", "encodings", "parse"], cwd="/tmp")
        hon2 = honesty("from encodings.utf_8 import parse; print(parse('z'))", cwd=tmp)
        q2 = run_cli(["-C", tmp, "--from", "encodings.utf_8", "parse"], cwd="/tmp")
        show(hon, "honesty encodings pkg")
        show(q, "bindname encodings pkg")
        show(hon2, "honesty encodings.utf_8")
        show(q2, "bindname encodings.utf_8")

    banner("R16. del flag / AnnAssign flag: bool = True")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "delflag.py": (
                    "flag = True\n"
                    "del flag\n"
                    "if flag:\n"
                    "    def parse(x):\n"
                    "        return 'del-live'\n"
                    "else:\n"
                    "    def parse(x):\n"
                    "        return 'del-dead'\n"
                ),
                "annflag.py": (
                    "flag: bool = True\n"
                    "if flag:\n"
                    "    def parse(x):\n"
                    "        return 'ann-live'\n"
                    "else:\n"
                    "    def parse(x):\n"
                    "        return 'ann-dead'\n"
                ),
            },
        )
        for mod in ("delflag", "annflag"):
            hon = honesty(f"from {mod} import parse; print(parse('z'))", cwd=tmp)
            q = run_cli(["-C", tmp, "--from", mod, "parse"])
            listed = run_cli(["-C", tmp, "parse"])
            show(hon, f"honesty {mod}")
            show(q, f"query {mod}")
            print(list_source_for(listed.stdout, mod))

    banner("DONE")


if __name__ == "__main__":
    main()
