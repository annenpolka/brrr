#!/usr/bin/env python3
"""Host attacks against post-MUTATE-6 bindname. Archive CLI only."""
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
SCRATCH = RUN / "destroyers/_bindname6_scratch"
SPEC013 = RUN / "specimens/specimen-013/files"
SPEC012 = RUN / "specimens/specimen-012/files"
SPEC010 = RUN / "specimens/specimen-010/files"

AST_LEFTOVER = "def parse(x):\n    return ('leftover-ast', x)\n"
PARSE_MOVED = "def parse(x):\n    return ('moved', x.strip())\n"
UTIL_LEGACY = "def parse(x):\n    return ('legacy', x)\n"

DIVERGES: list[tuple[str, str]] = []
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


def if_both(live: str, dead: str | None = None) -> str:
    body = f"    def parse(x):\n        return {live!r}\n"
    if dead is not None:
        body += f"else:\n    def parse(x):\n        return {dead!r}\n"
    return body


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
            loader = importlib.machinery.SourceFileLoader('bindname_cli6', {str(CLI)!r})
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

    banner("H7. leftover importlib.machinery kind=def while honesty cannot bind")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "importlib/__init__.py": "def parse(x):\n    return ('leftover-importlib', x)\n",
                "importlib/machinery.py": "def parse(x):\n    return ('leftover-importlib-mach', x)\n",
                "pkg_parse.py": PARSE_MOVED,
            },
        )
        hon = honesty("from importlib.machinery import parse; print(parse('z'))", cwd=tmp)
        proc = run_cli(["-C", tmp, "--from", "importlib.machinery", "parse"], cwd="/tmp")
        show(hon, "honesty importlib.machinery")
        show(proc, "bindname importlib.machinery")
        kill7 = hon.returncode != 0 and (
            (proc.returncode == 0 and "kind\tdef" in proc.stdout)
            or "leftover-importlib-mach" in proc.stdout
        )
        print("KILL_importlib_machinery_kind_def", kill7)
        HONOR["7_importlib_machinery_kind_def"] = kill7

    banner("H8. leftover importlib.py file / importlib.abc is miss while honesty leftover")
    kill8 = False
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
            kill8 = True
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
            kill8 = True
            print("KILL_importlib_abc_miss")
    HONOR["8_importlib_file_or_abc_miss"] = kill8

    banner("H9. list last-wins if 1+1 else as add-dead while query add-live")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "add.py": (
                    "if 1 + 1:\n"
                    + if_both("add-live", "add-dead")
                )
            },
        )
        hon = honesty("from add import parse; print(parse('z'))", cwd=tmp)
        q = run_cli(["-C", tmp, "--from", "add", "parse"])
        listed = run_cli(["-C", tmp, "parse"])
        row = list_source_for(listed.stdout, "add")
        show(hon, "honesty add")
        show(q, "query add")
        print("LIST_ROW add\n", row)
        kill9 = (
            hon.stdout.strip() == "add-live"
            and "add-live" in q.stdout
            and "add-dead" in row
            and "add-live" not in row
        )
        print("KILL_add_list_dead", kill9)
        HONOR["9_list_add_dead"] = kill9

    banner("H10. list if []: def parse without else as kind=def while query has no name")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        write_fixture(
            tmp,
            {
                "emptyif.py": (
                    "if []:\n"
                    "    def parse(x):\n"
                    "        return 'dead-only'\n"
                ),
                "pkg_parse.py": PARSE_MOVED,
            },
        )
        hon = honesty("from emptyif import parse; print(parse('z'))", cwd=tmp)
        q = run_cli(["-C", tmp, "--from", "emptyif", "parse"])
        listed = run_cli(["-C", tmp, "parse"])
        show(hon, "honesty emptyif")
        show(q, "query emptyif")
        show(listed, "list emptyif")
        kill10 = q.returncode != 0 and list_has_bind(listed.stdout, "emptyif.parse")
        print("KILL_emptyif_list_kind_def", kill10)
        HONOR["10_list_emptyif_kind_def"] = kill10

    banner("H11. THIN_WRAPPER of two greps / importlib.util with no leftover-identity join")
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
        HONOR["11_thin_wrapper"] = not (naive_stdlib and bind_leftover and also_moved)

    banner("C0. frozen map on host")
    frozen_code = textwrap.dedent(
        """
        import _imp, sys
        names = [
            'importlib','importlib.util','importlib.machinery','importlib.abc',
            'importlib.resources','importlib.metadata','importlib.readers',
            'importlib.simple','importlib._bootstrap','importlib._bootstrap_external',
            'importlib.resources.abc','importlib.metadata._meta',
            'encodings','encodings.utf_8','encodings.aliases','encodings.latin_1',
            'zipimport','_frozen_importlib','_frozen_importlib_external',
            'io','os','sys','builtins','tokenize','ast','inspect','json',
            'codecs','collections','collections.abc','os.path','posixpath',
            'typing','pathlib','abc','re','types','functools',
            'importlib.machinery.ModuleSpec',
        ]
        print('preimported', sorted(m for m in sys.modules if '.' not in m)[:80])
        print('PRE_HAS_importlib', 'importlib' in sys.modules)
        print('PRE_HAS_importlib.util', 'importlib.util' in sys.modules)
        print('PRE_HAS_encodings', 'encodings' in sys.modules)
        print('PRE_HAS_zipimport', 'zipimport' in sys.modules)
        print('PRE_HAS__frozen_importlib', '_frozen_importlib' in sys.modules)
        for n in names:
            top = n.split('.',1)[0]
            try:
                fr = _imp.is_frozen(n)
            except Exception as e:
                fr = f'ERR {e}'
            try:
                fr_top = _imp.is_frozen(top)
            except Exception as e:
                fr_top = f'ERR {e}'
            builtin = top in sys.builtin_module_names
            print(f'FROZEN {n} frozen={fr} top_frozen={fr_top} builtin={builtin} pre={n in sys.modules}')
        """
    )
    show(subprocess.run([sys.executable, "-c", frozen_code], capture_output=True, text=True), "frozen map")

    banner("C1. leftover importlib/ package directory honesty leftover vs CLI")
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
        listed = run_cli(["-C", tmp, "parse"], cwd="/tmp")
        show(hon, "honesty importlib pkg")
        show(q, "bindname importlib pkg")
        show(listed, "list importlib pkg")
        hon_helper = hon.returncode == 0 and "leftover-importlib-pkg" in hon.stdout
        cli_helper = q.returncode == 0 and "leftover-importlib-pkg" in q.stdout and "kind\tdef" in q.stdout
        print("importlib_pkg_honesty_helper", hon_helper)
        print("importlib_pkg_cli_helper", cli_helper)
        if hon_helper and not cli_helper:
            mark_diverge("importlib_pkg", "honesty leftover package, CLI miss")
        if (not hon_helper) and cli_helper:
            mark_diverge("importlib_pkg", "honesty cannot bind, CLI kind=def")

    banner("C2. other frozen submodules vs path-shadowable leftovers")
    frozen_cases = [
        ("encodings.utf_8", {"encodings/__init__.py": "def parse(x):\n    return ('leftover-encodings', x)\n",
                             "encodings/utf_8.py": "def parse(x):\n    return ('leftover-encodings-utf8', x)\n",
                             "pkg_parse.py": PARSE_MOVED}),
        ("encodings.aliases", {"encodings/__init__.py": "",
                               "encodings/aliases.py": "def parse(x):\n    return ('leftover-encodings-aliases', x)\n",
                               "pkg_parse.py": PARSE_MOVED}),
        ("zipimport", {"zipimport.py": "def parse(x):\n    return ('leftover-zipimport', x)\n",
                       "pkg_parse.py": PARSE_MOVED}),
        ("_frozen_importlib", {"_frozen_importlib.py": "def parse(x):\n    return ('leftover-frozen-il', x)\n",
                               "pkg_parse.py": PARSE_MOVED}),
        ("_frozen_importlib_external", {"_frozen_importlib_external.py": "def parse(x):\n    return ('leftover-frozen-ext', x)\n",
                                        "pkg_parse.py": PARSE_MOVED}),
        ("importlib._bootstrap", {"importlib/__init__.py": "def parse(x):\n    return ('leftover-importlib', x)\n",
                                  "importlib/_bootstrap.py": "def parse(x):\n    return ('leftover-bootstrap', x)\n",
                                  "pkg_parse.py": PARSE_MOVED}),
        ("importlib._bootstrap_external", {"importlib/__init__.py": "def parse(x):\n    return ('leftover-importlib', x)\n",
                                           "importlib/_bootstrap_external.py": "def parse(x):\n    return ('leftover-bootext', x)\n",
                                           "pkg_parse.py": PARSE_MOVED}),
        ("importlib.resources", {"importlib/__init__.py": "def parse(x):\n    return ('leftover-importlib', x)\n",
                                 "importlib/resources.py": "def parse(x):\n    return ('leftover-resources', x)\n",
                                 "pkg_parse.py": PARSE_MOVED}),
        ("importlib.metadata", {"importlib/__init__.py": "def parse(x):\n    return ('leftover-importlib', x)\n",
                                "importlib/metadata.py": "def parse(x):\n    return ('leftover-metadata', x)\n",
                                "pkg_parse.py": PARSE_MOVED}),
        ("importlib.readers", {"importlib/__init__.py": "def parse(x):\n    return ('leftover-importlib', x)\n",
                               "importlib/readers.py": "def parse(x):\n    return ('leftover-readers', x)\n",
                               "pkg_parse.py": PARSE_MOVED}),
        ("importlib.simple", {"importlib/__init__.py": "def parse(x):\n    return ('leftover-importlib', x)\n",
                              "importlib/simple.py": "def parse(x):\n    return ('leftover-simple', x)\n",
                              "pkg_parse.py": PARSE_MOVED}),
        ("collections.abc", {"collections/__init__.py": "def parse(x):\n    return ('leftover-collections', x)\n",
                             "collections/abc.py": "def parse(x):\n    return ('leftover-collections-abc', x)\n",
                             "pkg_parse.py": PARSE_MOVED}),
        ("os.path", {"os/__init__.py": "def parse(x):\n    return ('leftover-os', x)\n",
                     "os/path.py": "def parse(x):\n    return ('leftover-os-path', x)\n",
                     "pkg_parse.py": PARSE_MOVED}),
        ("json.decoder", {"json/__init__.py": "def parse(x):\n    return ('leftover-json', x)\n",
                          "json/decoder.py": "def parse(x):\n    return ('leftover-json-decoder', x)\n",
                          "pkg_parse.py": PARSE_MOVED}),
        ("typing_extensions", {"typing_extensions.py": "def parse(x):\n    return ('leftover-tex', x)\n",
                               "pkg_parse.py": PARSE_MOVED}),
        ("importlib.resources.abc", {"importlib/__init__.py": "def parse(x):\n    return ('leftover-importlib', x)\n",
                                     "importlib/resources/__init__.py": "def parse(x):\n    return ('leftover-resources', x)\n",
                                     "importlib/resources/abc.py": "def parse(x):\n    return ('leftover-resources-abc', x)\n",
                                     "pkg_parse.py": PARSE_MOVED}),
    ]
    for mod, files in frozen_cases:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
            write_fixture(tmp, files)
            hon = honesty(
                f"from {mod} import parse; print(parse('z')); import {mod} as m; print('FILE', getattr(m,'__file__',None))",
                cwd=tmp,
            )
            q = run_cli(["-C", tmp, "--from", mod, "parse"], cwd="/tmp")
            leftover_tag = f"leftover-{mod.replace('.', '-')}"
            # also match explicit tags used above
            hon_binds = hon.returncode == 0 and "leftover-" in hon.stdout
            cli_binds = q.returncode == 0 and "kind\tdef" in q.stdout and "leftover-" in q.stdout
            cli_stdlib = any(s in q.stdout for s in ("Cellar", "lib/python"))
            status = "MATCH"
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
            print(f"FROZEN_CASE {mod}: {status} hon_rc={hon.returncode} cli_rc={q.returncode}")

    banner("C3. leftover tokenize.py still helper")
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
        print("tokenize_match", hon.returncode == 0 and q.returncode == 0 and "leftover-tokenize" in q.stdout)
        if hon.returncode == 0 and "leftover-tokenize" in hon.stdout:
            if q.returncode != 0 or "leftover-tokenize" not in q.stdout:
                mark_diverge("tokenize", "honesty leftover helper, CLI miss")

    banner("C4. const-known remaining If tests list vs query vs honesty")
    cases = {
        "notempty": (
            "if not []:\n" + if_both("notempty-live", "notempty-dead"),
            "notempty-live",
            "notempty-dead",
        ),
        "subzero": (
            "if 1 - 1:\n" + if_both("sub-live", "sub-dead"),
            "sub-dead",
            "sub-live",
        ),
        "emptydict": (
            "if {}:\n" + if_both("dict-live", "dict-dead"),
            "dict-dead",
            "dict-live",
        ),
        "emptytup": (
            "if ():\n" + if_both("tup-live", "tup-dead"),
            "tup-dead",
            "tup-live",
        ),
        "mulzero": (
            "if 2 * 0:\n" + if_both("mul-live", "mul-dead"),
            "mul-dead",
            "mul-live",
        ),
        "chainadd": (
            "if 1 + 1 + 1:\n" + if_both("chain-live", "chain-dead"),
            "chain-live",
            "chain-dead",
        ),
        "multifalse": (
            "flag = other = False\n"
            "if flag:\n" + if_both("multiF-live", "multiF-dead"),
            "multiF-dead",
            "multiF-live",
        ),
        "lt": (
            "if 1 < 2:\n" + if_both("lt-live", "lt-dead"),
            "lt-live",
            "lt-dead",
        ),
        "uadd": (
            "if +1:\n" + if_both("uadd-live", "uadd-dead"),
            "uadd-live",
            "uadd-dead",
        ),
        "uadd0": (
            "if +0:\n" + if_both("uadd0-live", "uadd0-dead"),
            "uadd0-dead",
            "uadd0-live",
        ),
        "invert": (
            "if ~0:\n" + if_both("inv-live", "inv-dead"),
            "inv-live",
            "inv-dead",
        ),
        "inlist": (
            "if 1 in [1]:\n" + if_both("in-live", "in-dead"),
            "in-live",
            "in-dead",
        ),
        "notin": (
            "if 1 not in []:\n" + if_both("notin-live", "notin-dead"),
            "notin-live",
            "notin-dead",
        ),
        "instr": (
            "if 'a' in 'ab':\n" + if_both("instr-live", "instr-dead"),
            "instr-live",
            "instr-dead",
        ),
        "bitand": (
            "if 1 & 0:\n" + if_both("and-live", "and-dead"),
            "and-dead",
            "and-live",
        ),
        "bitor": (
            "if 1 | 0:\n" + if_both("or-live", "or-dead"),
            "or-live",
            "or-dead",
        ),
        "bitxor": (
            "if 1 ^ 1:\n" + if_both("xor-live", "xor-dead"),
            "xor-dead",
            "xor-live",
        ),
        "lshift": (
            "if 1 << 0:\n" + if_both("ls-live", "ls-dead"),
            "ls-live",
            "ls-dead",
        ),
        "rshift": (
            "if 8 >> 4:\n" + if_both("rs-live", "rs-dead"),
            "rs-dead",
            "rs-live",
        ),
        "floordiv": (
            "if 1 // 2:\n" + if_both("fd-live", "fd-dead"),
            "fd-dead",
            "fd-live",
        ),
        "mod": (
            "if 2 % 2:\n" + if_both("mod-live", "mod-dead"),
            "mod-dead",
            "mod-live",
        ),
        "pow": (
            "if 2 ** 0:\n" + if_both("pow-live", "pow-dead"),
            "pow-live",
            "pow-dead",
        ),
        "div": (
            "if 1 / 1:\n" + if_both("div-live", "div-dead"),
            "div-live",
            "div-dead",
        ),
        "nestedsub": (
            "if 10 - 5 - 5:\n" + if_both("nsub-live", "nsub-dead"),
            "nsub-dead",
            "nsub-live",
        ),
        "prec": (
            "if 1 + 1 * 0:\n" + if_both("prec-live", "prec-dead"),
            "prec-live",
            "prec-dead",
        ),
        "paren0": (
            "if (1 + 1) * 0:\n" + if_both("par-live", "par-dead"),
            "par-dead",
            "par-live",
        ),
        "nonelist": (
            "if [0]:\n" + if_both("nl-live", "nl-dead"),
            "nl-live",
            "nl-dead",
        ),
        "noneset": (
            "if {0}:\n" + if_both("ns-live", "ns-dead"),
            "ns-live",
            "ns-dead",
        ),
        "nonedict": (
            "if {0: 0}:\n" + if_both("nd-live", "nd-dead"),
            "nd-live",
            "nd-dead",
        ),
        "nonetup": (
            "if (0,):\n" + if_both("nt-live", "nt-dead"),
            "nt-live",
            "nt-dead",
        ),
        "noneconst": (
            "if None:\n" + if_both("none-live", "none-dead"),
            "none-dead",
            "none-live",
        ),
        "ellipsis": (
            "if ...:\n" + if_both("ell-live", "ell-dead"),
            "ell-live",
            "ell-dead",
        ),
        "zerofloat": (
            "if 0.0:\n" + if_both("zf-live", "zf-dead"),
            "zf-dead",
            "zf-live",
        ),
        "zerocomplex": (
            "if 0j:\n" + if_both("zc-live", "zc-dead"),
            "zc-dead",
            "zc-live",
        ),
        "emptystr": (
            "if '':\n" + if_both("es-live", "es-dead"),
            "es-dead",
            "es-live",
        ),
        "emptybytes": (
            "if b'':\n" + if_both("eb-live", "eb-dead"),
            "eb-dead",
            "eb-live",
        ),
        "emptyfstr": (
            "if f'':\n" + if_both("ef-live", "ef-dead"),
            "ef-dead",
            "ef-live",
        ),
        "iscmp": (
            "if 1 is 1:\n" + if_both("is-live", "is-dead"),
            "is-live",
            "is-dead",
        ),
        "isnot": (
            "if 1 is not None:\n" + if_both("isn-live", "isn-dead"),
            "isn-live",
            "isn-dead",
        ),
        "chaincmp": (
            "if 1 < 2 < 3:\n" + if_both("cc-live", "cc-dead"),
            "cc-live",
            "cc-dead",
        ),
        "andbool": (
            "if True and []:\n" + if_both("ab-live", "ab-dead"),
            "ab-dead",
            "ab-live",
        ),
        "orbool": (
            "if False or 1:\n" + if_both("ob-live", "ob-dead"),
            "ob-live",
            "ob-dead",
        ),
        "notnot": (
            "if not not []:\n" + if_both("nn-live", "nn-dead"),
            "nn-dead",
            "nn-live",
        ),
        "notzero": (
            "if not 0:\n" + if_both("nz-live", "nz-dead"),
            "nz-live",
            "nz-dead",
        ),
        "usub": (
            "if -1:\n" + if_both("us-live", "us-dead"),
            "us-live",
            "us-dead",
        ),
        "usub0": (
            "if -0:\n" + if_both("us0-live", "us0-dead"),
            "us0-dead",
            "us0-live",
        ),
        "annflag": (
            "flag: bool = True\n"
            "if flag:\n" + if_both("ann-live", "ann-dead"),
            "ann-live",
            "ann-dead",
        ),
        "triple": (
            "a = b = c = False\n"
            "if a:\n" + if_both("tri-live", "tri-dead"),
            "tri-dead",
            "tri-live",
        ),
        "tupleunp": (
            "flag, other = True, True\n"
            "if flag:\n" + if_both("tu-live", "tu-dead"),
            "tu-live",
            "tu-dead",
        ),
        "localtc": (
            "TYPE_CHECKING = True\n"
            "if TYPE_CHECKING:\n" + if_both("ltc-live", "ltc-dead"),
            "ltc-live",
            "ltc-dead",
        ),
        "walrusempty": (
            "if (flag := []):\n" + if_both("we-live", "we-dead"),
            "we-dead",
            "we-live",
        ),
        "starlist": (
            "if [*[]]:\n" + if_both("sl-live", "sl-dead"),
            "sl-dead",
            "sl-live",
        ),
        "callset": (
            "if set():\n" + if_both("cs-live", "cs-dead"),
            "cs-dead",
            "cs-live",
        ),
        "calllen": (
            "if len([]):\n" + if_both("cl-live", "cl-dead"),
            "cl-dead",
            "cl-live",
        ),
        "aug": (
            "n = 1\n"
            "n += -1\n"
            "if n:\n" + if_both("aug-live", "aug-dead"),
            "aug-dead",
            "aug-live",
        ),
        "runtime": (
            "import os\n"
            "flag = os.environ.get('NO_SUCH_BINDNAME_FLAG')\n"
            "if flag:\n" + if_both("rt-live", "rt-dead"),
            None,
            None,
        ),
    }
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        files = {f"{name}.py": body for name, (body, _h, _d) in cases.items()}
        write_fixture(tmp, files)
        listed = run_cli(["-C", tmp, "parse"])
        for name, (_body, hon_expect, dead) in cases.items():
            hon = honesty(f"from {name} import parse; print(parse('z'))", cwd=tmp)
            q = run_cli(["-C", tmp, "--from", name, "parse"])
            row = list_source_for(listed.stdout, name)
            hon_val = hon.stdout.strip() if hon.returncode == 0 else None
            q_ok = q.returncode == 0
            q_src = q.stdout
            list_has_hon = bool(hon_val) and hon_val in row
            list_has_dead = bool(dead) and dead in row
            list_has_live_only = bool(hon_val) and hon_val in row and (not dead or dead not in row)
            print(
                f"-- {name} hon_rc={hon.returncode} hon={hon_val!r} "
                f"qrc={q.returncode} q_has_hon={bool(hon_val) and hon_val in q_src} "
                f"list_has_hon={list_has_hon} list_has_dead={list_has_dead} "
                f"expect={hon_expect!r}"
            )
            if hon.returncode == 0 and hon_val:
                if hon_val not in q_src and q_ok:
                    mark_diverge(f"query_{name}", f"query != honesty {hon_val}")
                    show(q, f"query {name}")
                if hon_val not in row:
                    mark_diverge(f"list_{name}", f"list last-wins != honesty {hon_val}; row={row!r}")
            elif hon.returncode != 0:
                if q_ok and "kind\tdef" in q.stdout:
                    mark_diverge(f"query_{name}", "honesty no name, query kind=def")
                if list_has_bind(listed.stdout, f"{name}.parse") and name in ("callset",):
                    # Call both is declared park if list both
                    pass

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
            "annattr.py",
            "getitem.py",
            "paren.py",
            "itemget.py",
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
            declared_park = {
                "dictsub",
                "varsget",
                "attrget",
                "dynattr",
                "ifexpas",
                "impmod",
                "getitem",
                "itemget",
            }
            if hon.returncode == 0 and "moved" in hon.stdout:
                if not file_follows and mod not in declared_park:
                    mark_diverge(f"file_{mod}", "honesty moved, --file not follow (not declared park)")
                    show(fproc, f"--file {mod}")
                    show(qproc, f"--from {mod}")

    banner("C6. isolate also still static + leftover ast still helper")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        root = write_fixture(
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
            },
        )
        for mod in ("starer", "peper", "execer", "lam", "trylive"):
            arg = " z " if mod == "starer" else "z"
            hon = honesty(f"from {mod} import parse; print(parse({arg!r}))", cwd=tmp)
            q = run_cli(["-C", tmp, "--from", mod, "parse"])
            listed = run_cli(["-C", tmp, "parse"])
            print(
                f"PARK {mod} hon_rc={hon.returncode} hon={hon.stdout.strip()!r} "
                f"qrc={q.returncode} list_has={list_has_bind(listed.stdout, f'{mod}.parse')}"
            )

    banner("C8. leftover importlib.util file (not package) vs honesty")
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        # util as top-level file named importlib.util.py is not a module name.
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
    print("DIVERGES", DIVERGES)
    print("DIVERGE_COUNT", len(DIVERGES))


if __name__ == "__main__":
    main()
