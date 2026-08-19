# lode

The environment a **load image set** is owed. `ldd` for getenv names, of the binary *and* the dylibs it loads.

`due` harvested the main executable. Homebrew `python3` is a 52k Mach-O stub; `PYTHONHOME` lives in libpython. `rustc` is a 400k trampoline; `RUSTC_LOG` lives in `librustc_driver`. `lode` walks `otool -L` / `ldd` and joins those images.

## Install / run

```bash
chmod +x ./lode
./lode --help
./lode --selftest
./demo.sh
```

Python 3.10+, stdlib only. Uses `otool` on macOS, `ldd`/`objdump` on ELF.

## Interaction

```
lode PROGRAM                 # owed names of PROGRAM ∪ its loaded images
lode --solo PROGRAM          # main executable only (the ancestor)
lode --images PROGRAM        # the load list (main / load / skip)
lode --app python3           # application ABI including libpython
lode SRC --vs-program IMAGE  # source ABI ⋈ shipped image set
lode PROGRAM --emit          # packed KEY=VAL (owed ∩ env)
```

`--app` hides libc/runtime names. `--system` includes `/usr/lib` and `/System`. `--closure` BFS-walks non-system dependents. Exit 1 on `MISSING` / `DIFF` / `UNSET_*` / `UNDOCUMENTED`. `--report-only` always 0.

## Examples

Load list of Homebrew python3 — the stub plus libpython, libc skipped:

```bash
./lode --images python3
# main  …/bin/python3.14  (52448)
# load  …/Python          (5438480)
# skip  /usr/lib/libSystem.B.dylib
```

The stub owes nothing; the image set owes `PYTHON_*`:

```bash
./lode --names --app --solo python3    # empty
./lode --names --app python3           # PYTHON_GIL, PYTHON_FROZEN_MODULES, …
```

A rustc trampoline vs its driver dylib (`@rpath` resolved via `LC_RPATH`):

```bash
./lode --images "$(rustc --print sysroot)/bin/rustc"
# load  …/lib/librustc_driver-….dylib  (204MB)
./lode --names --app "$(rustc --print sysroot)/bin/rustc"
# RUSTC_LOG
# RUSTC_BOOTSTRAP
```
