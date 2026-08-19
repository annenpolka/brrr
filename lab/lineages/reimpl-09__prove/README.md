# prove (reimpl-09)

The env ABI of a load image set, **by getenv-shaped use**. Ancestor `assay` split DUE vs LATENT by *encoding* (isolated cstring vs help table). `prove` keeps LATENT as documentation and makes DUE a **call-site xref**: a name is DUE only if `getenv` / `env::var` / `env::var_os` / `std::getenv` references it.

| KIND | meaning |
| --- | --- |
| **DUE** | a getenv-shaped call site *uses* this name |
| **LATENT** | the image set *did* document it (help tables, `$VAR`, `NAME =`, `environment variable NAME`) |
| **BOTH** | both columns |

Prefix/packed harvest is `--loose` only, not a KIND promotion. That kills orphan `ORPHAN_ENV_NAME`, prefix-peel `COLOR_FORCE`, and rustc’s ~12k LLVM opcodes without deleting `PYTHON_GIL`.

This is not `strings(1)`. DYLD/`LD_PRELOAD` `--trace` is not the second column (malloc reentry + SIP).

## Install / run

```bash
chmod +x ./prove
./prove --help
./prove --selftest
./demo.sh
```

Python 3.9+, stdlib only. Parses Mach-O (fat / arm64e auth stubs) and ELF. Walks `LC_LOAD_DYLIB` + `LC_RPATH` on macOS, `DT_NEEDED` on ELF.

## Interaction

```
prove PROGRAM                 # KIND NAME table of PROGRAM ∪ loaded images
prove --due PROGRAM           # names a getenv/env::var site uses
prove --latent PROGRAM        # names it documented
prove --due --latent PROGRAM  # BOTH only
prove --solo PROGRAM          # main executable only
prove --images PROGRAM        # the load list
prove --app python3           # application ABI including libpython
prove --loose PROGRAM         # packed/orphan tokens (search aid)
prove --calls PROGRAM         # getenv/env::var sites: name, how, va, source
prove --dump-abi --app python3
```

`--app` hides libc/runtime names. `--min-evidence call` on a binary keeps xref hits (`evidence=call`). SIP shims (`/usr/bin/python3`) fail closed: `(no owed names)`.

## Examples

Homebrew python3: the stub owes nothing; libpython *documents* `PYTHONHOME` and *getenvs* `PYTHON_GIL`.

```bash
./prove --names --app --solo python3    # empty
./prove --dump-abi --app python3 | awk -F'\t' '$1=="PYTHONHOME" || $1=="PYTHON_GIL"'
# PYTHONHOME  LATENT  …  assign+dollar+help
# PYTHON_GIL  DUE     …  getenv
./prove --calls --app python3 | awk -F'\t' '$1=="PYTHON_GIL"'
# PYTHON_GIL  getenv  0x1f6b9c  …/Python
```

Compiled host: `strings` dumps every token; prove does not.

```bash
cc -o /tmp/host fixtures/split/host.c
./prove --app /tmp/host
# BOTH    ASSAY_BOTH         call  getenv+help
# DUE     ASSAY_GETENV_ONLY  call  getenv
# LATENT  ASSAY_DOC_ONLY     string  help
# LATENT  ASSAY_DOLLAR       string  dollar
```

rustc sysroot + `librustc_driver`: tens of DUE names, not ~12k LLVM opcodes. `RUSTC_LOG` is an `env::var_os` use; `RUSTC_GRAPHVIZ_FONT` is documented *and* used (BOTH).

```bash
./prove --images "$(rustc --print sysroot)/bin/rustc"
./prove --dump-abi --app "$(rustc --print sysroot)/bin/rustc" \
  | awk -F'\t' '$1=="RUSTC_LOG" || $1=="RUSTC_GRAPHVIZ_FONT"'
```
