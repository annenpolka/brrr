# assay (mutation-36)

The env ABI of a load image set, **split**. `lode` unioned getenv strings and help-table names. `assay` prints two columns:

| KIND | meaning |
| --- | --- |
| **DUE** | the image set *could* read this name (`getenv` / call cstrings) |
| **LATENT** | the image set *did* document it (help tables, `$VAR`, `NAME =`) |
| **BOTH** | both columns |

A DYLD getenv interposer is not cheap (malloc re-enters `getenv`; SIP). The split is static.

## Install / run

```bash
chmod +x ./assay
./assay --help
./assay --selftest
./demo.sh
```

Python 3.10+, stdlib only. Uses `otool` on macOS, `ldd`/`objdump` on ELF.

## Interaction

```
assay PROGRAM                 # KIND NAME table of PROGRAM ∪ its loaded images
assay --due PROGRAM           # names it could getenv
assay --latent PROGRAM        # names it documented
assay --due --latent PROGRAM  # BOTH only
assay --solo PROGRAM          # main executable only (the due ancestor)
assay --images PROGRAM        # the load list
assay --app python3           # application ABI including libpython
assay --dump-abi --app python3
```

`--app` hides libc/runtime names. Exit 1 on env-join `MISSING` / `DIFF` / `UNSET_*` / `UNDOCUMENTED`. `--report-only` always 0.

## Examples

Homebrew python3: the stub owes nothing; libpython *documents* `PYTHONHOME` and *can getenv* `PYTHON_GIL`.

```bash
./assay --names --app --solo python3    # empty
./assay --dump-abi --app python3 | awk -F'\t' '$1=="PYTHONHOME" || $1=="PYTHON_GIL"'
# PYTHONHOME  LATENT  …  assign+dollar+help
# PYTHON_GIL  DUE     …  cstring
```

A compiled host with mixed encodings:

```bash
cc -o /tmp/host fixtures/split/host.c
./assay --app /tmp/host
# DUE     ASSAY_GETENV_ONLY
# LATENT  ASSAY_DOC_ONLY
# LATENT  ASSAY_DOLLAR
# BOTH    ASSAY_BOTH
```

rustc trampoline vs driver (`@rpath` resolved via `LC_RPATH`). rustc documents some names as `environment variable NAME` prose (LATENT) and packs others as getenv literals (DUE):

```bash
./assay --images "$(rustc --print sysroot)/bin/rustc"
./assay --dump-abi --app "$(rustc --print sysroot)/bin/rustc" \
  | awk -F'\t' '$1=="RUSTC_LOG" || $1=="RUSTC_GRAPHVIZ_FONT"'
# RUSTC_LOG             DUE     prefix
# RUSTC_GRAPHVIZ_FONT   LATENT  prose
```
