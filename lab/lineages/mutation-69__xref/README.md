# xref (mutation-69)

The env ABI of a load image set, **by getenv-shaped use**. Ancestor `assay` split DUE vs LATENT by *encoding* (isolated cstring vs help table). `xref` keeps LATENT as documentation and makes DUE a **call-site xref**: an isolated cstring is DUE only if `getenv` / `env::var` / `std::getenv` references it.

| KIND | meaning |
| --- | --- |
| **DUE** | a getenv-shaped call site *uses* this name |
| **LATENT** | the image set *did* document it (help tables, `$VAR`, `NAME =`, `environment variable NAME`) |
| **BOTH** | both columns |

Prefix/packed harvest is a search aid for LATENT and `--loose`, not a KIND promotion. That kills orphan `ORPHAN_ENV_NAME`, `COLOR_FORCE`, and rustc’s ~12k LLVM opcodes without deleting `PYTHON_GIL`.

This is not `strings(1)`. DYLD/`LD_PRELOAD` `--trace` is not the second column (malloc reentry + SIP).

## Install / run

```bash
chmod +x ./xref
./xref --help
./xref --selftest
./demo.sh
```

Python 3.9+, stdlib only. Parses Mach-O (including fat / arm64e auth stubs) and ELF. Uses `otool` on macOS for the load list, `ldd`/`objdump` on ELF.

## Interaction

```
xref PROGRAM                 # KIND NAME table of PROGRAM ∪ loaded images
xref --due PROGRAM           # names a getenv/env::var site uses
xref --latent PROGRAM        # names it documented
xref --due --latent PROGRAM  # BOTH only
xref --solo PROGRAM          # main executable only
xref --images PROGRAM        # the load list
xref --app python3           # application ABI including libpython
xref --loose PROGRAM         # also emit packed/orphan tokens (search aid)
xref --calls PROGRAM         # getenv/env::var sites: name, how, va, source
xref --dump-abi --app python3
```

`--app` hides libc/runtime names. `--min-evidence call` on a binary keeps xref hits (evidence=`call`). `--calls` prints the sites. Prefix/packed harvest runs only with `--loose`. Exit 1 on env-join `MISSING` / `DIFF` / `UNSET_*` / `UNDOCUMENTED`. `--report-only` always 0. SIP shims (`/usr/bin/python3`) fail closed: `(no owed names)`.

## Examples

Homebrew python3: the stub owes nothing; libpython *documents* `PYTHONHOME` and *getenvs* `PYTHON_GIL`.

```bash
./xref --names --app --solo python3    # empty
./xref --dump-abi --app python3 | awk -F'\t' '$1=="PYTHONHOME" || $1=="PYTHON_GIL"'
# PYTHONHOME  LATENT  …  assign+dollar+help
# PYTHON_GIL  DUE     …  call+getenv
```

Compiled host: `strings` dumps every token; xref does not.

```bash
cc -o /tmp/host fixtures/split/host.c
./xref --app /tmp/host
# DUE     ASSAY_GETENV_ONLY   call/getenv
# LATENT  ASSAY_DOC_ONLY      help
# LATENT  ASSAY_DOLLAR        dollar
# BOTH    ASSAY_BOTH          getenv + help
```

Orphan cstring vs nearby decoy:

```bash
cc -o /tmp/orphan fixtures/xref/orphan.c
./xref --app /tmp/orphan          # (no owed names)
./xref --app --loose /tmp/orphan  # ORPHAN_ENV_NAME as search aid
cc -o /tmp/nearby fixtures/xref/nearby.c
./xref --app /tmp/nearby          # REAL_GETENV_NAME only
```

`/bin/ls` (fat arm64e): `CLICOLOR_FORCE`, not the `COLOR_FORCE` peel.

```bash
./xref --names --app /bin/ls
# CLICOLOR_FORCE
# LSCOLORS
```

rustc sysroot + `librustc_driver`: tens of DUE names, not ~12k LLVM opcodes. `RUSTC_LOG` is an `env::var` use; `RUSTC_GRAPHVIZ_FONT` is documented *and* used (BOTH).

```bash
./xref --images "$(rustc --print sysroot)/bin/rustc"
./xref --dump-abi --app "$(rustc --print sysroot)/bin/rustc" \
  | awk -F'\t' '$1=="RUSTC_LOG" || $1=="RUSTC_GRAPHVIZ_FONT"'
```
