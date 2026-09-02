#!/usr/bin/env python3
"""Host attacks against post-MUTATE bindname. Archive CLI only."""
from __future__ import annotations

import os
import shlex
import stat
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

RUN = Path("/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112")
CLI = RUN / "lineages/candidate-bind/bindname"
SCRATCH = RUN / "destroyers/_bindname2_scratch"
SPEC013 = RUN / "specimens/specimen-013/files"
SPEC010 = RUN / "specimens/specimen-010/files"
SPEC012 = RUN / "specimens/specimen-012/files"
SPEC015 = RUN / "specimens/specimen-015/files"

AST_LEFTOVER = "def parse(x):\n    return ('leftover-ast', x)\n"
PARSE_MOVED = "def parse(x):\n    return ('moved', x.strip())\n"
UTIL_LEGACY = "def parse(x):\n    return ('legacy', x)\n"


def banner(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def run_cli(args, *, cwd=None, timeout=8, stdin=None):
    proc = subprocess.run(
        [sys.executable, str(CLI), *args],
        check=False,
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=timeout,
        input=stdin,
    )
    return proc


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


def main() -> None:
    banner("0. owned specimen-013")
    proc = run_cli(["-C", str(SPEC013), "--from", "pkg_util", "parse"])
    show(proc, "from pkg_util")
    proc = run_cli(["-C", str(SPEC013), "--from", "pkg_parse", "parse"])
    show(proc, "from pkg_parse")
    proc = run_cli(["-C", str(SPEC013), "parse"])
    show(proc, "list parse")

    banner("1. leftover ast.py vs honesty (KILL if stdlib / Cellar)")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        root = write_fixture(
            tmp,
            {"ast.py": AST_LEFTOVER, "pkg_parse.py": PARSE_MOVED},
        )
        hon = honesty("from ast import parse; print(parse('z')); import ast; print(ast.__file__)", cwd=tmp)
        show(hon, "honesty cwd=tmp")
        proc = run_cli(["-C", tmp, "--from", "ast", "parse"], cwd="/tmp")
        show(proc, "bindname -C leftover ast from /tmp")
        print("stdlib markers in file field:", "Cellar" in proc.stdout or "lib/python" in proc.stdout)
        print("leftover-ast in stdout:", "leftover-ast" in proc.stdout)
        print("stdout starts query:", proc.stdout.startswith("query\t"))
        proc2 = run_cli(["-C", tmp, "--import", "from ast import parse"], cwd="/tmp")
        show(proc2, "--import from ast import parse")
        listed = run_cli(["-C", tmp, "parse"], cwd="/tmp")
        show(listed, "list parse with leftover ast.py")

    banner("1b. leftover ast.py unique name in-process")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        root = write_fixture(tmp, {"ast.py": AST_LEFTOVER, "pkg_parse.py": PARSE_MOVED})
        code = textwrap.dedent(
            f"""
            import importlib.util, sys
            from pathlib import Path
            loader = importlib.machinery.SourceFileLoader if False else None
            spec = importlib.util.spec_from_file_location("bn", {str(CLI)!r})
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            root = Path({tmp!r})
            stdlib = sys.modules['ast']
            with mod.isolated_import(root):
                m, u = mod.load_query(root, 'ast', root/'ast.py')
                print('unique', u)
                print('mod.__name__', m.__name__)
                print('parse', m.parse('z'))
                print('sys.modules ast is leftover unique', sys.modules.get('ast') is m)
                print('sys.modules ast file', getattr(sys.modules.get('ast'), '__file__', None))
            print('restored ast is stdlib', sys.modules['ast'] is stdlib)
            print('stdlib file', stdlib.__file__)
            """
        )
        # SourceFileLoader path:
        code = textwrap.dedent(
            f"""
            import importlib.machinery, importlib.util, sys
            from pathlib import Path
            loader = importlib.machinery.SourceFileLoader('bindname_cli', {str(CLI)!r})
            spec = importlib.util.spec_from_loader(loader.name, loader)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[loader.name] = mod
            loader.exec_module(mod)
            root = Path({tmp!r})
            stdlib = sys.modules['ast']
            print('before ast file', stdlib.__file__)
            with mod.isolated_import(root):
                m, u = mod.load_query(root, 'ast', root/'ast.py')
                print('unique', u)
                print('mod.__name__', m.__name__)
                print('parse', m.parse('z'))
                print('unique is not ast', u != 'ast')
                print('sys.modules[ast] is unique mod', sys.modules.get('ast') is m)
                ast_now = sys.modules.get('ast')
                print('sys.modules[ast] file', getattr(ast_now, '__file__', None))
            print('restored ast is stdlib', sys.modules['ast'] is stdlib)
            """
        )
        proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        show(proc, "in-process unique load")

    banner("2. sibling sys.exit / SIDE / aaa_patch (KILL if also executes siblings)")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        root = write_fixture(
            tmp,
            {
                "keep.py": "def parse(x):\n    return 'kept'\n",
                "killer.py": "import sys\ndef parse(x):\n    return 'dead'\nsys.exit(9)\n",
                "side.py": "open('SIDE','w').write('ran')\ndef parse(x):\n    return 'side'\n",
            },
        )
        proc = run_cli(["-C", tmp, "--from", "keep", "parse"])
        show(proc, "from keep with killer+side siblings")
        print("SIDE exists", (root / "SIDE").exists())

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
        show(proc, "aaa_patch does not rewrite")

    banner("3. __name__ gated leftover ast.py")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "ast.py": (
                    "if __name__ == 'ast':\n"
                    "    def parse(x):\n"
                    "        return ('name-gated-leftover', x)\n"
                ),
                "pkg_parse.py": PARSE_MOVED,
            },
        )
        hon = honesty(
            "from ast import parse; print(parse('z')); print(__import__('ast').__name__)",
            cwd=tmp,
        )
        show(hon, "honesty __name__==ast gated")
        proc = run_cli(["-C", tmp, "--from", "ast", "parse"], cwd="/tmp")
        show(proc, "bindname __name__==ast gated")

    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "ast.py": (
                    "if __name__ != 'ast':\n"
                    "    def parse(x):\n"
                    "        return ('unique-only', x)\n"
                    "else:\n"
                    "    def parse(x):\n"
                    "        return ('honesty-leftover', x)\n"
                ),
            },
        )
        hon = honesty("from ast import parse; print(parse('z'))", cwd=tmp)
        show(hon, "honesty __name__ branch")
        proc = run_cli(["-C", tmp, "--from", "ast", "parse"], cwd="/tmp")
        show(proc, "bindname __name__ branch")

    banner("4. leftover inspect.py / json.py as query")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "inspect.py": "def parse(x):\n    return ('leftover-inspect', x)\n",
                "json.py": "def parse(x):\n    return ('leftover-json', x)\n",
            },
        )
        hon_i = honesty("from inspect import parse; print(parse('z'))", cwd=tmp)
        hon_j = honesty("from json import parse; print(parse('z'))", cwd=tmp)
        show(hon_i, "honesty inspect")
        show(hon_j, "honesty json")
        proc_i = run_cli(["-C", tmp, "--from", "inspect", "parse"], cwd="/tmp")
        proc_j = run_cli(["-C", tmp, "--from", "json", "parse"], cwd="/tmp")
        show(proc_i, "bindname inspect leftover")
        show(proc_j, "bindname json leftover")

    banner("5. sibling leftover ast.py while querying keep that import ast")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "ast.py": AST_LEFTOVER,
                "keep.py": (
                    "import ast\n"
                    "def parse(x):\n"
                    "    return ('keep', getattr(ast, 'parse', None) and ast.parse(x))\n"
                ),
            },
        )
        hon = honesty("from keep import parse; print(parse('z')); import ast; print(ast.__file__)", cwd=tmp)
        show(hon, "honesty keep+leftover ast")
        proc = run_cli(["-C", tmp, "--from", "keep", "parse"], cwd="/tmp")
        show(proc, "bindname keep with leftover ast sibling")

    banner("6. from pkg import parse when parse is a submodule")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "pkg/__init__.py": "",
                "pkg/parse.py": "def parse(x):\n    return ('submodule', x)\nvalue = 'mod'\n",
            },
        )
        hon = honesty(
            "from pkg import parse; print(type(parse), getattr(parse,'value',None), getattr(parse,'parse',None))",
            cwd=tmp,
        )
        show(hon, "honesty submodule")
        proc = run_cli(["-C", tmp, "--from", "pkg", "parse"], cwd="/tmp")
        show(proc, "bindname from pkg import parse submodule")
        listed = run_cli(["-C", tmp, "parse"], cwd="/tmp")
        show(listed, "list parse with submodule")

    banner("7. relative import in package (unique name)")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "pkg/__init__.py": "",
                "pkg/moved.py": PARSE_MOVED,
                "pkg/util.py": "from .moved import parse\n",
            },
        )
        hon = honesty("from pkg.util import parse; print(parse(' z '))", cwd=tmp)
        show(hon, "honesty relative")
        proc = run_cli(["-C", tmp, "--from", "pkg.util", "parse"], cwd="/tmp")
        show(proc, "bindname relative reexport")

    banner("7b. parent __init__ sys.exit hostage")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "pkg/__init__.py": "import sys\nsys.exit(7)\n",
                "pkg/keep.py": "def parse(x):\n    return 'kept'\n",
            },
        )
        hon = honesty("from pkg.keep import parse; print(parse('z'))", cwd=tmp)
        show(hon, "honesty parent exit")
        proc = run_cli(["-C", tmp, "--from", "pkg.keep", "parse"], cwd="/tmp")
        show(proc, "bindname parent exit")

    banner("8. functools.partial / decorator / lambda / class")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "partialer.py": (
                    "import functools\n"
                    "def _p(pre, x):\n    return pre+x\n"
                    "parse = functools.partial(_p, 'pre')\n"
                ),
                "decer.py": (
                    "def wrap(fn):\n"
                    "    def inner(x):\n"
                    "        return ('wrapped', fn(x))\n"
                    "    return inner\n"
                    "@wrap\n"
                    "def parse(x):\n    return x\n"
                ),
                "lam.py": "parse = lambda x: ('lam', x)\n",
                "cls.py": "class parse:\n    def __init__(self, x):\n        self.x = x\n",
            },
        )
        for mod in ("partialer", "decer", "lam", "cls"):
            hon = honesty(f"from {mod} import parse; print(type(parse), getattr(parse,'__name__',None))", cwd=tmp)
            proc = run_cli(["-C", tmp, "--from", mod, "parse"], cwd="/tmp")
            show(hon, f"honesty {mod}")
            show(proc, f"bindname {mod}")

    banner("9. if False def list vs query")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "dead.py": (
                    "if False:\n"
                    "    def parse(x):\n"
                    "        return 'dead'\n"
                ),
                "pkg_parse.py": PARSE_MOVED,
            },
        )
        hon = honesty("import dead; print(hasattr(dead,'parse'))", cwd=tmp)
        show(hon, "honesty if False")
        listed = run_cli(["-C", tmp, "parse"])
        show(listed, "list if False")
        proc = run_cli(["-C", tmp, "--from", "dead", "parse"])
        show(proc, "from dead")
        also = run_cli(["-C", tmp, "--from", "pkg_parse", "parse"])
        show(also, "from pkg_parse also includes if False?")

    banner("10. import pkg_parse as parse / star / exec / getattr")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "pkg_parse.py": PARSE_MOVED,
                "aliasmod.py": "import pkg_parse as parse\n",
                "star.py": "from pkg_parse import *\n",
                "execer.py": "exec(\"def parse(x):\\n    return ('execed', x)\\n\")\n",
                "peppy.py": (
                    "def __getattr__(name):\n"
                    "    if name == 'parse':\n"
                    "        def parse(x):\n"
                    "            return ('pep562', x)\n"
                    "        return parse\n"
                    "    raise AttributeError(name)\n"
                ),
            },
        )
        for mod, expr in [
            ("aliasmod", "from aliasmod import parse; print(parse(' z '))"),
            ("star", "from star import parse; print(parse(' z '))"),
            ("execer", "from execer import parse; print(parse('z'))"),
            ("peppy", "from peppy import parse; print(parse('z'))"),
        ]:
            hon = honesty(expr, cwd=tmp)
            proc = run_cli(["-C", tmp, "--from", mod, "parse"])
            show(hon, f"honesty {mod}")
            show(proc, f"bindname {mod}")
        listed = run_cli(["-C", tmp, "parse"])
        show(listed, "list parse alias/star/exec/pep")

    banner("11. --file FIFO / stdin / as-alias already tested")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        root = write_fixture(tmp, {"pkg_util.py": UTIL_LEGACY, "importer.py": "from pkg_util import parse\n"})
        fifo = root / "fifo"
        os.mkfifo(fifo)
        proc = run_cli(["-C", tmp, "--file", str(fifo), "parse"])
        show(proc, "--file fifo")
        proc = run_cli(["-C", tmp, "--file", "/dev/stdin", "parse"], stdin="from pkg_util import parse\n")
        show(proc, "--file /dev/stdin")

    banner("12. specimen-010 stdout / specimen-012 nested / specimen-015")
    if SPEC010.exists():
        proc = run_cli(["-C", str(SPEC010), "--from", "loader", "load_skip_empty"])
        show(proc, "specimen-010")
        print("skip_empty in stdout", "skip_empty" in proc.stdout)
    if SPEC012.exists():
        proc = run_cli(["-C", str(SPEC012), "--from", "test_order", "test_a"])
        show(proc, "specimen-012 test_a")
        listed = run_cli(["-C", str(SPEC012), "test_a"])
        show(listed, "specimen-012 list test_a")
    if SPEC015.exists():
        proc = run_cli(["-C", str(SPEC015), "side"])
        show(proc, "specimen-015 list side")

    banner("13. stderr from queried module; stdout redirected")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "noisy.py": (
                    "import sys\n"
                    "print('OUT')\n"
                    "print('ERR', file=sys.stderr)\n"
                    "def parse(x):\n    return x\n"
                )
            },
        )
        proc = run_cli(["-C", tmp, "--from", "noisy", "parse"])
        show(proc, "noisy stdout/stderr")

    banner("14. os._exit sibling vs query (sibling should not fire)")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "keep.py": "def parse(x):\n    return 'kept'\n",
                "bomb.py": "import os\ndef parse(x):\n    return 'bomb'\nos._exit(11)\n",
            },
        )
        proc = run_cli(["-C", tmp, "--from", "keep", "parse"])
        show(proc, "os._exit sibling")

    banner("15. tuple unpack / AnnAssign value / walrus / match")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "unpack.py": "parse, other = (lambda x: x), 1\n",
                "annval.py": "from typing import Callable\nparse: Callable = lambda x: ('ann', x)\n",
                "walrus.py": "(parse := lambda x: ('walrus', x))\n",
                "matcher.py": (
                    "cmd = 'def'\n"
                    "match cmd:\n"
                    "    case 'def':\n"
                    "        def parse(x):\n"
                    "            return ('match', x)\n"
                ),
            },
        )
        for mod in ("unpack", "annval", "walrus", "matcher"):
            hon = honesty(f"from {mod} import parse; print(parse('z') if callable(parse) else parse)", cwd=tmp)
            proc = run_cli(["-C", tmp, "--from", mod, "parse"])
            show(hon, f"honesty {mod}")
            show(proc, f"bindname {mod}")

    banner("16. huge body + 80 extra defs")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        body = "def parse(x):\n    s = '" + ("A" * 200000) + "'\n    return s\n"
        extras = "\n".join(f"def parse_{i}(x):\n    return {i}\n" for i in range(80))
        write_fixture(tmp, {"huge.py": body + extras, "other.py": PARSE_MOVED})
        proc = run_cli(["-C", tmp, "--from", "huge", "parse"])
        print("huge rc", proc.returncode, "stdout bytes", len(proc.stdout), "starts query", proc.stdout.startswith("query\t"))

    banner("17. encoding latin-1 / BOM")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        root = Path(tmp)
        (root / "latin.py").write_bytes(
            b"# -*- coding: latin-1 -*-\ndef parse(x):\n    return 'caf\xe9'\n"
        )
        (root / "bom.py").write_bytes(
            b"\xef\xbb\xbfdef parse(x):\n    return 'bom'\n"
        )
        proc_l = run_cli(["-C", tmp, "--from", "latin", "parse"])
        proc_b = run_cli(["-C", tmp, "--from", "bom", "parse"])
        show(proc_l, "latin-1")
        show(proc_b, "bom")

    banner("18. namespace package no __init__")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(tmp, {"ns/keep.py": "def parse(x):\n    return 'ns'\n"})
        hon = honesty("from ns.keep import parse; print(parse('z'))", cwd=tmp)
        proc = run_cli(["-C", tmp, "--from", "ns.keep", "parse"])
        show(hon, "honesty namespace")
        show(proc, "bindname namespace")

    banner("19. weird name.py")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(tmp, {"weird name.py": "def parse(x):\n    return 'space'\n"})
        listed = run_cli(["-C", tmp, "parse"])
        proc = run_cli(["-C", tmp, "--from", "weird name", "parse"])
        show(listed, "list weird name")
        show(proc, "from weird name")

    banner("20. queried module imports killer sibling")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "keep.py": "import killer\ndef parse(x):\n    return 'kept'\n",
                "killer.py": "import sys\nsys.exit(9)\n",
            },
        )
        proc = run_cli(["-C", tmp, "--from", "keep", "parse"])
        show(proc, "query imports killer")

    banner("21. drop importlib leftover")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "importlib/__init__.py": "def parse(x):\n    return ('leftover-importlib', x)\n",
            },
        )
        hon = honesty("from importlib import parse; print(parse('z')); import importlib; print(importlib.__file__)", cwd=tmp)
        proc = run_cli(["-C", tmp, "--from", "importlib", "parse"], cwd="/tmp")
        show(hon, "honesty leftover importlib")
        show(proc, "bindname leftover importlib")

    banner("22. same_function True after silent if/else miss on list")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "pkg_util.py": (
                    "flag = False\n"
                    "if flag:\n"
                    "    def parse(x):\n"
                    "        return ('legacy', x)\n"
                ),
                "pkg_parse.py": PARSE_MOVED,
            },
        )
        listed = run_cli(["-C", tmp, "parse"])
        hon = honesty("import pkg_util, pkg_parse; print(hasattr(pkg_util,'parse'), pkg_parse.parse(' z '))", cwd=tmp)
        show(hon, "honesty flag False")
        show(listed, "list flag False still counts pkg_util?")

    banner("23. TYPE_CHECKING")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "typed.py": (
                    "from typing import TYPE_CHECKING\n"
                    "if TYPE_CHECKING:\n"
                    "    def parse(x):\n"
                    "        return 'typed'\n"
                )
            },
        )
        hon = honesty("import typed; print(hasattr(typed,'parse'))", cwd=tmp)
        proc = run_cli(["-C", tmp, "--from", "typed", "parse"])
        listed = run_cli(["-C", tmp, "parse"])
        show(hon, "honesty TYPE_CHECKING")
        show(proc, "from typed")
        show(listed, "list typed")

    banner("24. --file last binding vs mention of importlib")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        root = write_fixture(
            tmp,
            {
                "pkg_parse.py": PARSE_MOVED,
                "dyn.py": (
                    "import importlib\n"
                    "m = importlib.import_module('pkg_parse')\n"
                    "parse = m.parse\n"
                ),
            },
        )
        hon = honesty("from dyn import parse; print(parse(' z '))", cwd=tmp)
        proc = run_cli(["-C", tmp, "--file", str(root / "dyn.py"), "parse"])
        q = run_cli(["-C", tmp, "--from", "dyn", "parse"])
        show(hon, "honesty dyn import_module")
        show(proc, "--file dyn")
        show(q, "--from dyn")

    banner("25. empty / missing / star / mismatch")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(tmp, {"pkg_util.py": UTIL_LEGACY})
        for args in (
            ["-C", tmp, "nope"],
            ["-C", "/no/such/dir", "parse"],
            ["-C", tmp, "--import", "from pkg_util import *"],
            ["-C", tmp, "--import", "from pkg_util import parse", "other"],
            ["-C", tmp],
            ["-C", tmp, "--from", "pkg_util", "--file", str(Path(tmp)/"pkg_util.py"), "parse"],
        ):
            proc = run_cli(args)
            print("args", args, "rc", proc.returncode, "err", proc.stderr.strip()[:120])

    banner("26. __name__ == '__main__' leftover")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "ast.py": (
                    "if __name__ == '__main__':\n"
                    "    def parse(x):\n"
                    "        return ('main', x)\n"
                    "else:\n"
                    "    def parse(x):\n"
                    "        return ('leftover-ast', x)\n"
                )
            },
        )
        hon = honesty("from ast import parse; print(parse('z'))", cwd=tmp)
        proc = run_cli(["-C", tmp, "--from", "ast", "parse"])
        show(hon, "honesty main-gate")
        show(proc, "bindname main-gate")

    banner("27. in-process drop_shadowed_modules does not leak")
    code = textwrap.dedent(
        f"""
        import importlib.machinery, importlib.util, sys, tempfile
        from pathlib import Path
        loader = importlib.machinery.SourceFileLoader('bindname_cli', {str(CLI)!r})
        spec = importlib.util.spec_from_loader(loader.name, loader)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[loader.name] = mod
        loader.exec_module(mod)
        stdlib_ast = sys.modules['ast']
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, 'ast.py').write_text({AST_LEFTOVER!r})
            Path(tmp, 'keep.py').write_text('def parse(x):\\n    return 1\\n')
            root = Path(tmp)
            with mod.isolated_import(root):
                loaded, unique = mod.load_query(root, 'keep', root/'keep.py')
                print('inside ast in sys.modules', 'ast' in sys.modules)
                print('inside ast file', getattr(sys.modules.get('ast'), '__file__', None))
            print('after ast is stdlib', sys.modules['ast'] is stdlib_ast)
        """
    )
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    show(proc, "drop_shadowed leak check")

    banner("DONE")


if __name__ == "__main__":
    main()
