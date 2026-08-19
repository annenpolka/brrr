# shim (mutation-108)

The env ABI of a load image set, **by real getenv-shaped use**, with **shims as a role**. Ancestor `xref` made DUE a call-site proof and then printed `(no owed names)` for three different objects: a silent `main`, a rustup trampoline, and an xcselect SIP stub. A symbol named `*getenv` was treated as getenv.

`shim` keeps the two columns and closes those holes:

| KIND / role | meaning |
| --- | --- |
| **DUE** | a libc `getenv` / `secure_getenv` / `_Py_GETENV` / rust `std::env::__var` call site *uses* this name |
| **LATENT** | the image set *did* document it |
| **BOTH** | both columns |
| **shim** | the operand is rustup or xcselect; one cheap hop (`rustup which`, `xcrun --find`) if the payload is on disk |

`not_a_getenv` / `forgetenv` are not DUE. A silent binary is `(no owed names)`. `/usr/bin/python3` and PATH `rustc` print `shim`, not empty. `COLOR_FORCE` peel stays not-DUE. rustc’s ~12k LLVM opcodes stay out.

This is not `strings(1)`. DYLD/`LD_PRELOAD` is not the second column.

## Install / run

```bash
chmod +x ./shim
./shim --help
./shim --selftest
./demo.sh
```

Python 3.9+, stdlib only. Parses Mach-O (fat / arm64e auth stubs) and ELF.

## Interaction

```
shim PROGRAM                 # KIND table; rustup/xcselect prefixed as shim
shim --shims PROGRAM         # hop: kind, path, payload
shim --images PROGRAM        # load list; trampoline role is shim
shim --no-follow PROGRAM     # name the shim, do not hop
shim --due / --latent PROGRAM
shim --calls PROGRAM         # libc-getenv / __var sites
shim --app python3           # application ABI including libpython
```

## Examples

`/usr/bin/python3` is xcselect. xref printed `(no owed names)`. shim names the role and hops to Xcode’s python when `xcrun --find` is cheap.

```bash
./shim --app /usr/bin/python3
# shim  xcselect  /usr/bin/python3 -> …/Python3.framework/…/python3.9
# BOTH  PYTHONHOME  …

./shim --no-follow --app /usr/bin/python3
# shim  xcselect  /usr/bin/python3
# (not empty; not the trampoline's leftover names)
```

PATH `rustc` is rustup. `--images` shows the trampoline, then the toolchain rustc and `librustc_driver`.

```bash
./shim --images rustc
# shim  ~/.cargo/bin/rustc  rustup
# main  ~/.rustup/toolchains/…/bin/rustc  payload
# load  …/librustc_driver-….dylib
```

Suffix match is not a getenv proof. Direct `getenv` still is.

```bash
cc -O0 -fno-inline -o /tmp/false fixtures/shim/false.c
./shim --app /tmp/false
# DUE  REAL_GETENV_NAME
# not FALSE_DUE_NAME, not FORGET_ENV_NAME

cc -o /tmp/empty fixtures/shim/empty.c
./shim --app /tmp/empty
# (no owed names)
```
