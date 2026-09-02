#!/usr/bin/env python3
"""Host attacks against post-MUTATE-4 bindname. Archive CLI only."""
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
SCRATCH = RUN / "destroyers/_bindname4_scratch"
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


def src_has(token: str) -> bool:
    return token in CLI.read_text(encoding="utf-8")


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
            loader = importlib.machinery.SourceFileLoader('bindname_cli4', {str(CLI)!r})
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
    print("has_builtin_module_names", "builtin_module_names" in src)

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

    banner("H4. leftover sys.py / builtins.py kind=def while honesty ImportError")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "sys.py": "def parse(x):\n    return ('leftover-sys', x)\n",
                "builtins.py": "def parse(x):\n    return ('leftover-builtins', x)\n",
                "pkg_parse.py": PARSE_MOVED,
            },
        )
        for mod in ("sys", "builtins"):
            hon = honesty(f"from {mod} import parse; print(parse('z'))", cwd=tmp)
            proc = run_cli(["-C", tmp, "--from", mod, "parse"], cwd="/tmp")
            show(hon, f"honesty {mod}")
            show(proc, f"bindname {mod}")
            print(
                f"KILL_{mod}_kind_def",
                proc.returncode == 0 and "kind\tdef" in proc.stdout,
            )
            print(f"KILL_{mod}_leftover_body", f"leftover-{mod}" in proc.stdout)
        listed = run_cli(["-C", tmp, "parse"], cwd="/tmp")
        show(listed, "list with builtin leftovers")
        print("list_has_sys.parse", "sys.parse" in listed.stdout)
        print("list_has_builtins.parse", "builtins.parse" in listed.stdout)
        inspect_tree = write_fixture(
            tmp,
            {
                "inspect.py": "def parse(x):\n    return ('leftover-inspect', x)\n",
                "sys.py": "def parse(x):\n    return ('leftover-sys', x)\n",
                "builtins.py": "def parse(x):\n    return ('leftover-builtins', x)\n",
                "pkg_parse.py": PARSE_MOVED,
            },
        )
        proc = run_cli(["-C", str(inspect_tree), "--from", "inspect", "parse"], cwd="/tmp")
        show(proc, "from inspect with builtin ghosts")
        print("also_sys", "also\tsys.parse" in proc.stdout)
        print("also_builtins", "also\tbuiltins.parse" in proc.stdout)

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

    banner("C1. leftover already-imported stdlib (os/io/importlib/encodings)")
    pre = honesty(
        "import sys; print(' '.join(sorted(k for k in ('os','io','importlib','encodings','codecs','tokenize','types','functools','collections','pathlib','inspect','json','ast','sys','builtins') if k in sys.modules)))",
        cwd="/tmp",
    )
    show(pre, "preimported names in python -c")
    names = [
        "os",
        "io",
        "importlib",
        "encodings",
        "codecs",
        "tokenize",
        "types",
        "functools",
        "collections",
        "pathlib",
        "posixpath",
        "genericpath",
        "stat",
        "time",
        "_collections_abc",
        "_sitebuiltins",
        "inspect",
        "json",
        "ast",
        "_thread",
        "marshal",
        "posix",
        "gc",
        "itertools",
        "errno",
    ]
    for mod in names:
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
            print(
                f"SHADOW {mod}: honesty_rc={hon.returncode} honesty_leftover={hon_binds} "
                f"cli_rc={proc.returncode} cli_leftover={cli_binds} cli_stdlib={cli_stdlib}"
            )
            if hon.returncode != 0 and cli_binds:
                print(f"  DIVERGE_honesty_ImportError_cli_kind_def {mod}")
                show(hon, f"honesty {mod}")
                show(proc, f"bindname {mod}")
            elif hon_binds and (not cli_binds or cli_stdlib):
                print(f"  DIVERGE_honesty_leftover_cli_miss_or_stdlib {mod}")
                show(hon, f"honesty {mod}")
                show(proc, f"bindname {mod}")
            elif hon.returncode != 0 and proc.returncode == 0:
                print(f"  DIVERGE_honesty_fail_cli_ok {mod}")
                show(hon, f"honesty {mod}")
                show(proc, f"bindname {mod}")

    banner("C2. mutate-3 claimed: if not TYPE_CHECKING list is live")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "nottyped.py": (
                    "from typing import TYPE_CHECKING\n"
                    "if not TYPE_CHECKING:\n"
                    "    def parse(x):\n"
                    "        return 'live'\n"
                    "else:\n"
                    "    def parse(x):\n"
                    "        return 'typed-else'\n"
                )
            },
        )
        hon = honesty("from nottyped import parse; print(parse('z'))", cwd=tmp)
        q = run_cli(["-C", tmp, "--from", "nottyped", "parse"])
        listed = run_cli(["-C", tmp, "parse"])
        show(hon, "honesty nottyped")
        show(q, "query nottyped")
        show(listed, "list nottyped")
        print("list_typed_else", "typed-else" in listed.stdout)

    banner("C3. mutate-3 claimed: --file attr assign follows moved body")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        root = write_fixture(
            tmp,
            {
                "pkg_parse.py": PARSE_MOVED,
                "assign.py": "import pkg_parse\nparse = pkg_parse.parse\n",
            },
        )
        hon = honesty("from assign import parse; print(parse(' z '))", cwd=tmp)
        fproc = run_cli(["-C", tmp, "--file", str(root / "assign.py"), "parse"])
        qproc = run_cli(["-C", tmp, "--from", "assign", "parse"])
        show(hon, "honesty assign")
        show(fproc, "--file assign")
        show(qproc, "--from assign")

    banner("C4. mutate-3 claimed: functools.partial runs wrapped")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "partialer.py": (
                    "import functools\n"
                    "def _p(pre, x):\n    return pre+x\n"
                    "parse = functools.partial(_p, 'pre')\n"
                )
            },
        )
        hon = honesty(
            "from partialer import parse; print(type(parse).__name__, parse(' z'))",
            cwd=tmp,
        )
        q = run_cli(["-C", tmp, "--from", "partialer", "parse"])
        listed = run_cli(["-C", tmp, "parse"])
        show(hon, "honesty partial")
        show(q, "query partial")
        show(listed, "list partial")
        print("runs_functools.parse", "functools.parse" in q.stdout)

    banner("R1. if flag: both branches / const-assigned flag")
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
                "flagfalse.py": (
                    "flag = False\n"
                    "if flag:\n"
                    "    def parse(x):\n"
                    "        return 'dead-body'\n"
                    "else:\n"
                    "    def parse(x):\n"
                    "        return 'live-else'\n"
                ),
                "runtime.py": (
                    "import os\n"
                    "flag = os.environ.get('BINDNAME_FLAG')\n"
                    "if flag:\n"
                    "    def parse(x):\n"
                    "        return 'env-live'\n"
                    "else:\n"
                    "    def parse(x):\n"
                    "        return 'env-else'\n"
                ),
            },
        )
        for mod in ("flagtrue", "flagfalse", "runtime"):
            hon = honesty(f"from {mod} import parse; print(parse('z'))", cwd=tmp)
            q = run_cli(["-C", tmp, "--from", mod, "parse"])
            listed = run_cli(["-C", tmp, "parse"])
            show(hon, f"honesty {mod}")
            show(q, f"query {mod}")
            # extract that module's list source
            print(f"-- list snippet {mod}")
            for line in listed.stdout.splitlines():
                if mod in line or "source" in line.split("\t")[0:1]:
                    print(line)
            print(
                f"DIVERGE_{mod}_list_vs_query",
                ("live-flag" in q.stdout) != ("live-flag" in listed.stdout)
                or ("dead-else" in listed.stdout and "dead-else" not in q.stdout)
                or ("live-else" in q.stdout and "dead-body" in listed.stdout and "live-else" not in listed.stdout.split(mod)[-1] if False else False),
            )
        show(run_cli(["-C", tmp, "parse"]), "list all flag modules")

    banner("R2. TYPE_CHECKING alias TC")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "aliased.py": (
                    "from typing import TYPE_CHECKING as TC\n"
                    "if TC:\n"
                    "    def parse(x):\n"
                    "        return 'typed-alias'\n"
                    "else:\n"
                    "    def parse(x):\n"
                    "        return 'live-alias'\n"
                )
            },
        )
        hon = honesty("from aliased import parse; print(parse('z'))", cwd=tmp)
        q = run_cli(["-C", tmp, "--from", "aliased", "parse"])
        listed = run_cli(["-C", tmp, "parse"])
        show(hon, "honesty alias")
        show(q, "query alias")
        show(listed, "list alias")

    banner("R3. try/except last-wins")
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
                )
            },
        )
        hon = honesty("from trylive import parse; print(parse('z'))", cwd=tmp)
        q = run_cli(["-C", tmp, "--from", "trylive", "parse"])
        listed = run_cli(["-C", tmp, "parse"])
        show(hon, "honesty try")
        show(q, "query try")
        show(listed, "list try")

    banner("R4. nested defs specimen-012")
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

    banner("R5. FIFO --file / /dev/stdin")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        fifo = Path(tmp) / "fifo.py"
        os.mkfifo(fifo)
        t0 = time.time()
        proc = run_cli(["-C", tmp, "--file", str(fifo), "parse"], timeout=3)
        dt = time.time() - t0
        show(proc, "fifo --file")
        print("fifo_elapsed", round(dt, 3))
        proc2 = run_cli(["-C", tmp, "--file", "/dev/stdin", "parse"], stdin="def parse(x):\n    return 1\n")
        show(proc2, "/dev/stdin --file")

    banner("R6. exec / PEP562 / star as list bind")
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
                f"from {mod} import parse; print(getattr(parse,'__name__',type(parse).__name__), parse(' z ' ) if callable(parse) else parse)",
                cwd=tmp,
            )
            q = run_cli(["-C", tmp, "--from", mod, "parse"])
            listed = run_cli(["-C", tmp, "parse"])
            show(hon, f"honesty {mod}")
            show(q, f"query {mod}")
            print(f"list_has_{mod}.parse", f"{mod}.parse" in listed.stdout)
        show(run_cli(["-C", tmp, "parse"]), "list exec/pep/star")

    banner("R7. huge source dump")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        body = "def parse(x):\n    s = '" + ("A" * 200000) + "'\n    return s\n"
        write_fixture(tmp, {"huge.py": body})
        t0 = time.time()
        proc = run_cli(["-C", tmp, "--from", "huge", "parse"], timeout=8)
        dt = time.time() - t0
        print("huge_rc", proc.returncode, "elapsed", round(dt, 3), "stdout_bytes", len(proc.stdout))
        print("huge_starts_query", proc.stdout.startswith("query\t"))

    banner("R8. if True and False / if 1==1 / if __debug__")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "andfalse.py": (
                    "if True and False:\n"
                    "    def parse(x):\n"
                    "        return 'and-dead'\n"
                    "else:\n"
                    "    def parse(x):\n"
                    "        return 'and-live'\n"
                ),
                "eq.py": (
                    "if 1 == 1:\n"
                    "    def parse(x):\n"
                    "        return 'eq-live'\n"
                    "else:\n"
                    "    def parse(x):\n"
                    "        return 'eq-dead'\n"
                ),
                "dbg.py": (
                    "if __debug__:\n"
                    "    def parse(x):\n"
                    "        return 'debug-live'\n"
                    "else:\n"
                    "    def parse(x):\n"
                    "        return 'debug-dead'\n"
                ),
                "notnot.py": (
                    "if not not False:\n"
                    "    def parse(x):\n"
                    "        return 'nn-dead'\n"
                    "else:\n"
                    "    def parse(x):\n"
                    "        return 'nn-live'\n"
                ),
            },
        )
        for mod in ("andfalse", "eq", "dbg", "notnot"):
            hon = honesty(f"from {mod} import parse; print(parse('z'))", cwd=tmp)
            q = run_cli(["-C", tmp, "--from", mod, "parse"])
            listed = run_cli(["-C", tmp, "parse"])
            show(hon, f"honesty {mod}")
            show(q, f"query {mod}")
            # find list source for this module
            rows = listed.stdout.split("\n\n")
            for row in rows:
                if f"bind\t{mod}.parse" in row:
                    print(f"-- list {mod}\n{row}")

    banner("R9. match without static subject / walrus")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
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
                "walrus.py": (
                    "if (flag := True):\n"
                    "    def parse(x):\n"
                    "        return 'walrus-live'\n"
                    "else:\n"
                    "    def parse(x):\n"
                    "        return 'walrus-dead'\n"
                ),
            },
        )
        for mod in ("dynmatch", "walrus"):
            hon = honesty(f"from {mod} import parse; print(parse('z'))", cwd=tmp)
            q = run_cli(["-C", tmp, "--from", mod, "parse"])
            listed = run_cli(["-C", tmp, "parse"])
            show(hon, f"honesty {mod}")
            show(q, f"query {mod}")
            rows = listed.stdout.split("\n\n")
            for row in rows:
                if f"bind\t{mod}.parse" in row:
                    print(f"-- list {mod}\n{row}")

    banner("R10. --file getattr / import as / chained")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        root = write_fixture(
            tmp,
            {
                "pkg_parse.py": PARSE_MOVED,
                "getattrer.py": "import pkg_parse\nparse = getattr(pkg_parse, 'parse')\n",
                "asalias.py": "import pkg_parse as p\nparse = p.parse\n",
                "fromas.py": "from pkg_parse import parse as p\nparse = p\n",
                "multi.py": "import pkg_parse\nparse = other = pkg_parse.parse\n",
            },
        )
        for name in ("getattrer.py", "asalias.py", "fromas.py", "multi.py"):
            hon = honesty(
                f"import importlib.util; s=importlib.util.spec_from_file_location('m', {str(root/name)!r}); "
                f"mod=__import__('importlib.util').module_from_spec(s); s.loader.exec_module(mod); print(mod.parse(' z '))",
                cwd=tmp,
            )
            # simpler honesty
            mod = Path(name).stem
            hon = honesty(f"from {mod} import parse; print(parse(' z '))", cwd=tmp)
            fproc = run_cli(["-C", tmp, "--file", str(root / name), "parse"])
            qproc = run_cli(["-C", tmp, "--from", mod, "parse"])
            show(hon, f"honesty {mod}")
            show(fproc, f"--file {mod}")
            show(qproc, f"--from {mod}")

    banner("R11. class parse / lambda / decorator")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "clser.py": "class parse:\n    def __init__(self, x): self.x = x\n",
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
                "wraps.py": (
                    "import functools\n"
                    "def wrap(fn):\n"
                    "    @functools.wraps(fn)\n"
                    "    def inner(x):\n"
                    "        return ('wrap', fn(x))\n"
                    "    return inner\n"
                    "@wrap\n"
                    "def parse(x):\n"
                    "    return ('inner', x)\n"
                ),
            },
        )
        for mod in ("clser", "lam", "decer", "wraps"):
            hon = honesty(
                f"from {mod} import parse; print(type(parse).__name__, getattr(parse,'__name__',None))",
                cwd=tmp,
            )
            q = run_cli(["-C", tmp, "--from", mod, "parse"])
            listed = run_cli(["-C", tmp, "parse"])
            show(hon, f"honesty {mod}")
            show(q, f"query {mod}")
            rows = listed.stdout.split("\n\n")
            for row in rows:
                if f"bind\t{mod}.parse" in row:
                    print(f"-- list {mod}\n{row}")

    banner("R12. parent __init__ sys.exit / dependency killer")
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

    banner("R13. if __name__ == '__main__' leftover")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "mainish.py": (
                    "if __name__ == '__main__':\n"
                    "    def parse(x):\n"
                    "        return 'main-only'\n"
                    "else:\n"
                    "    def parse(x):\n"
                    "        return 'import-body'\n"
                )
            },
        )
        hon = honesty("from mainish import parse; print(parse('z'))", cwd=tmp)
        q = run_cli(["-C", tmp, "--from", "mainish", "parse"])
        listed = run_cli(["-C", tmp, "parse"])
        show(hon, "honesty mainish")
        show(q, "query mainish")
        show(listed, "list mainish")

    banner("R14. leftover importlib/util.py submodule")
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

    banner("R15. while False / for empty / AnnAssign alias")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "pkg_parse.py": PARSE_MOVED,
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
                "ann.py": "import pkg_parse\nparse: object = pkg_parse.parse\n",
            },
        )
        for mod in ("whiler", "forer", "ann"):
            hon = honesty(f"from {mod} import parse; print(parse(' z ') if callable(parse) else parse)", cwd=tmp)
            q = run_cli(["-C", tmp, "--from", mod, "parse"])
            listed = run_cli(["-C", tmp, "parse"])
            show(hon, f"honesty {mod}")
            show(q, f"query {mod}")
            rows = listed.stdout.split("\n\n")
            for row in rows:
                if f"bind\t{mod}.parse" in row:
                    print(f"-- list {mod}\n{row}")

    banner("R16. keep.py that imports leftover ast sibling (query dependency)")
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

    banner("R17. leftover typing.py")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(tmp, {"typing.py": "def parse(x):\n    return ('leftover-typing', x)\n"})
        hon = honesty("from typing import parse; print(parse('z'))", cwd=tmp)
        proc = run_cli(["-C", tmp, "--from", "typing", "parse"], cwd="/tmp")
        show(hon, "honesty typing")
        show(proc, "bindname typing")

    banner("DONE")


if __name__ == "__main__":
    main()
