#!/usr/bin/env python3
"""Host attacks against post-MUTATE-2 bindname. Archive CLI only."""
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
SCRATCH = RUN / "destroyers/_bindname3_scratch"
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


def load_bn():
    import importlib.machinery
    import importlib.util

    loader = importlib.machinery.SourceFileLoader("bindname_cli3", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = mod
    loader.exec_module(mod)
    return mod


def main() -> None:
    banner("0. owned specimen-013 leftover vs moved")
    for args, label in [
        (["-C", str(SPEC013), "--from", "pkg_util", "parse"], "from pkg_util"),
        (["-C", str(SPEC013), "--from", "pkg_parse", "parse"], "from pkg_parse"),
        (["-C", str(SPEC013), "parse"], "list parse"),
        (["-C", str(SPEC013), "--import", "from pkg_util import parse"], "--import util"),
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
            loader = importlib.machinery.SourceFileLoader('bindname_cli3', {str(CLI)!r})
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
                print('unique_id_in_name', '_bindname_' in m.__name__)
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

    banner("H4. if __name__=='ast' leftover (KILL if unique-only / missing)")
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
        hon = honesty("from ast import parse; print(parse('z'))", cwd=tmp)
        proc = run_cli(["-C", tmp, "--from", "ast", "parse"], cwd="/tmp")
        show(hon, "honesty gated")
        show(proc, "bindname gated")
        print("KILL_missing_gated", proc.returncode != 0 or "name-gated-leftover" not in proc.stdout)

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
        proc = run_cli(["-C", tmp, "--from", "ast", "parse"], cwd="/tmp")
        show(hon, "honesty branch")
        show(proc, "bindname branch")
        print("KILL_unique_only", "unique-only" in proc.stdout or "honesty-leftover" not in proc.stdout)

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

    banner("R1. leftover inspect/json + builtin sys.py")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "inspect.py": "def parse(x):\n    return ('leftover-inspect', x)\n",
                "json.py": "def parse(x):\n    return ('leftover-json', x)\n",
                "sys.py": "def parse(x):\n    return ('leftover-sys', x)\n",
                "builtins.py": "def parse(x):\n    return ('leftover-builtins', x)\n",
            },
        )
        for mod in ("inspect", "json", "sys", "builtins"):
            hon = honesty(f"from {mod} import parse; print(parse('z'))", cwd=tmp)
            proc = run_cli(["-C", tmp, "--from", mod, "parse"], cwd="/tmp")
            show(hon, f"honesty {mod}")
            show(proc, f"bindname {mod}")
            print(
                f"DIVERGE_{mod}",
                (hon.returncode == 0) != (proc.returncode == 0)
                or ("leftover-" in hon.stdout) != ("leftover-" in proc.stdout),
            )

    banner("R2. keep.py that imports leftover ast sibling")
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

    banner("R3. from pkg import parse submodule + init override")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "pkg/__init__.py": "",
                "pkg/parse.py": "def parse(x):\n    return ('submodule', x)\n",
            },
        )
        hon = honesty(
            "from pkg import parse; print(type(parse).__name__, parse.__name__)",
            cwd=tmp,
        )
        proc = run_cli(["-C", tmp, "--from", "pkg", "parse"])
        listed = run_cli(["-C", tmp, "parse"])
        show(hon, "honesty submodule")
        show(proc, "bindname submodule")
        show(listed, "list submodule")

    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "pkg/__init__.py": "def parse(x):\n    return ('init-def', x)\n",
                "pkg/parse.py": "def parse(x):\n    return ('submodule', x)\n",
            },
        )
        hon = honesty(
            "from pkg import parse; print(parse('z'), type(parse).__name__)",
            cwd=tmp,
        )
        proc = run_cli(["-C", tmp, "--from", "pkg", "parse"])
        show(hon, "honesty init-def wins over submodule")
        show(proc, "bindname init-def vs submodule")

    banner("R4. relative reexport + parent __init__ sys.exit")
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
        proc = run_cli(["-C", tmp, "--from", "pkg.util", "parse"])
        show(hon, "honesty relative")
        show(proc, "bindname relative")

    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "pkg/__init__.py": "import sys\nsys.exit(7)\n",
                "pkg/keep.py": "def parse(x):\n    return 'kept'\n",
            },
        )
        hon = honesty("from pkg.keep import parse; print(parse('z'))", cwd=tmp)
        proc = run_cli(["-C", tmp, "--from", "pkg.keep", "parse"])
        show(hon, "honesty parent exit")
        show(proc, "bindname parent exit")

    banner("R5. functools.partial / decorator wraps / no wraps / lambda / class / import as")
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
                "wraps.py": (
                    "import functools\n"
                    "def wrap(fn):\n"
                    "    @functools.wraps(fn)\n"
                    "    def inner(x):\n"
                    "        return ('wrapped', fn(x))\n"
                    "    return inner\n"
                    "@wrap\n"
                    "def parse(x):\n    return x\n"
                ),
                "lam.py": "parse = lambda x: ('lam', x)\n",
                "cls.py": "class parse:\n    def __init__(self, x):\n        self.x = x\n",
                "pkg_parse.py": PARSE_MOVED,
                "aliasmod.py": "import pkg_parse as parse\n",
                "assign.py": "import pkg_parse\nparse = pkg_parse.parse\n",
            },
        )
        for mod in ("partialer", "decer", "wraps", "lam", "cls", "aliasmod", "assign"):
            hon = honesty(
                f"from {mod} import parse; print(type(parse).__name__, getattr(parse,'__name__',None), getattr(parse,'__module__',None)); "
                f"print('call', parse(' z ') if callable(parse) and {mod!r}!='cls' else parse)",
                cwd=tmp,
            )
            proc = run_cli(["-C", tmp, "--from", mod, "parse"])
            show(hon, f"honesty {mod}")
            show(proc, f"bindname {mod}")
        listed = run_cli(["-C", tmp, "parse"])
        show(listed, "list kind noise")

    banner("R6. --file import_module last-binding vs --from")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        root = write_fixture(
            tmp,
            {
                "pkg_parse.py": PARSE_MOVED,
                "pkg_util.py": UTIL_LEGACY,
                "dyn.py": (
                    "import importlib\n"
                    "m = importlib.import_module('pkg_parse')\n"
                    "parse = m.parse\n"
                ),
                "assign.py": "import pkg_parse\nparse = pkg_parse.parse\n",
                "fromimp.py": "from pkg_parse import parse\n",
            },
        )
        for name in ("dyn.py", "assign.py", "fromimp.py"):
            hon = honesty(f"import {Path(name).stem} as m; print(m.parse(' z '))", cwd=tmp)
            fproc = run_cli(["-C", tmp, "--file", str(root / name), "parse"])
            qproc = run_cli(["-C", tmp, "--from", Path(name).stem, "parse"])
            show(hon, f"honesty {name}")
            show(fproc, f"--file {name}")
            show(qproc, f"--from {Path(name).stem}")

    banner("R7. FIFO --file / /dev/stdin")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        root = write_fixture(tmp, {"pkg_util.py": UTIL_LEGACY})
        fifo = root / "fifo"
        os.mkfifo(fifo)
        t0 = time.time()
        proc = run_cli(["-C", tmp, "--file", str(fifo), "parse"], timeout=3)
        print("fifo_elapsed", round(time.time() - t0, 3), "mode", oct(stat.S_IFMT(fifo.stat().st_mode)))
        show(proc, "--file fifo")
        proc = run_cli(["-C", tmp, "--file", "/dev/stdin", "parse"], stdin="from pkg_util import parse\n")
        show(proc, "--file /dev/stdin")

    banner("R8. nested defs specimen-012")
    proc = run_cli(["-C", str(SPEC012), "test_a"])
    show(proc, "specimen-012 test_a")
    proc = run_cli(["-C", str(SPEC012), "--from", "run_orders", "test_a"])
    show(proc, "from run_orders test_a")
    proc = run_cli(["-C", str(SPEC012), "--from", "test_order", "test_a"])
    show(proc, "from test_order test_a")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "outer.py": (
                    "def run():\n"
                    "    def parse(x):\n"
                    "        return ('nested', x)\n"
                    "    return parse\n"
                    "def parse(x):\n"
                    "    return ('module-level', x)\n"
                ),
            },
        )
        hon = honesty(
            "from outer import parse, run; print('mod', parse('z')); print('nested', run()('z'))",
            cwd=tmp,
        )
        proc = run_cli(["-C", tmp, "--from", "outer", "parse"])
        show(hon, "honesty nested")
        show(proc, "bindname nested")

    banner("R9. star / PEP562 / exec list vs query")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "pkg_parse.py": PARSE_MOVED,
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
            ("star", "from star import parse; print(parse(' z '))"),
            ("execer", "from execer import parse; print(parse('z'))"),
            ("peppy", "from peppy import parse; print(parse('z'))"),
        ]:
            hon = honesty(expr, cwd=tmp)
            proc = run_cli(["-C", tmp, "--from", mod, "parse"])
            show(hon, f"honesty {mod}")
            show(proc, f"bindname {mod}")
        listed = run_cli(["-C", tmp, "parse"])
        show(listed, "list star/exec/pep")

    banner("R10. huge source dump")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        body = "def parse(x):\n    s = '" + ("A" * 200000) + "'\n    return s\n"
        write_fixture(tmp, {"huge.py": body, "pkg_parse.py": PARSE_MOVED})
        t0 = time.time()
        proc = run_cli(["-C", tmp, "--from", "huge", "parse"], timeout=10)
        print("huge_elapsed", round(time.time() - t0, 3), "stdout_bytes", len(proc.stdout), "rc", proc.returncode)
        print("starts_query", proc.stdout.startswith("query\t"))
        print("also_moved", "pkg_parse.parse" in proc.stdout)

    banner("R11. if not TYPE_CHECKING / match / if flag")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "pkg_parse.py": PARSE_MOVED,
                "nottyped.py": (
                    "from typing import TYPE_CHECKING\n"
                    "if not TYPE_CHECKING:\n"
                    "    def parse(x):\n"
                    "        return 'live'\n"
                    "else:\n"
                    "    def parse(x):\n"
                    "        return 'typed-else'\n"
                ),
                "matched.py": (
                    "x = 1\n"
                    "match x:\n"
                    "    case 0:\n"
                    "        def parse(y):\n"
                    "            return 'dead-match'\n"
                    "    case 1:\n"
                    "        def parse(y):\n"
                    "            return 'live-match'\n"
                ),
            },
        )
        for mod in ("nottyped", "matched"):
            hon = honesty(f"from {mod} import parse; print(parse('z'))", cwd=tmp)
            proc = run_cli(["-C", tmp, "--from", mod, "parse"])
            listed = run_cli(["-C", tmp, "parse"])
            show(hon, f"honesty {mod}")
            show(proc, f"bindname {mod}")
        listed = run_cli(["-C", tmp, "parse"])
        show(listed, "list nottyped+match")

    banner("R12. latin-1 self + TYPE_CHECKING also + stderr (mutate-2 claims)")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        root = Path(tmp)
        (root / "latin.py").write_bytes(
            "# -*- coding: latin-1 -*-\ndef parse(x):\n    return 'café'\n".encode("latin-1")
        )
        (root / "pkg_parse.py").write_text(PARSE_MOVED, encoding="utf-8")
        (root / "typed.py").write_text(
            "from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    def parse(x):\n        return 'typed'\n",
            encoding="utf-8",
        )
        (root / "err.py").write_text(
            "import sys\nprint('ERR', file=sys.stderr)\ndef parse(x):\n    return 'e'\n",
            encoding="utf-8",
        )
        hon = honesty("from latin import parse; print(parse('z'))", cwd=tmp)
        proc = run_cli(["-C", tmp, "--from", "latin", "parse"])
        show(hon, "honesty latin")
        show(proc, "bindname latin")
        print("self_miss", any("latin.py" in line and "miss" in line for line in proc.stdout.splitlines()))
        also = run_cli(["-C", tmp, "--from", "pkg_parse", "parse"])
        show(also, "also typed?")
        err = run_cli(["-C", tmp, "--from", "err", "parse"])
        show(err, "stderr redirected")

    banner("R13. queried module imports killer (dependency, not also)")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "killer.py": "import sys\ndef parse(x):\n    return 'k'\nsys.exit(9)\n",
                "dep.py": "import killer\ndef parse(x):\n    return 'd'\n",
            },
        )
        hon = honesty("from dep import parse; print(parse('z'))", cwd=tmp)
        proc = run_cli(["-C", tmp, "--from", "dep", "parse"])
        show(hon, "honesty dep->killer")
        show(proc, "bindname dep->killer")

    banner("R14. also class.parse method vs class named parse")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "pkg_parse.py": PARSE_MOVED,
                "methods.py": (
                    "class Holder:\n"
                    "    def parse(self, x):\n"
                    "        return ('method', x)\n"
                ),
                "cls.py": "class parse:\n    pass\n",
            },
        )
        proc = run_cli(["-C", tmp, "--from", "pkg_parse", "parse"])
        listed = run_cli(["-C", tmp, "parse"])
        show(proc, "also methods/class")
        show(listed, "list methods/class")

    banner("R15. namespace package keep.py")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(tmp, {"ns/keep.py": "def parse(x):\n    return 'ns'\n", "pkg_parse.py": PARSE_MOVED})
        hon = honesty("from ns.keep import parse; print(parse('z'))", cwd=tmp)
        proc = run_cli(["-C", tmp, "--from", "ns.keep", "parse"])
        show(hon, "honesty ns")
        show(proc, "bindname ns")

    banner("DONE")


if __name__ == "__main__":
    main()
