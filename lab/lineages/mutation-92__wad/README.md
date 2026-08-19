# wad (mutation-92)

The env ABI of a load image set, **by getenv-shaped use, including the CString that feeds getenv**.

Ancestor `xref` made DUE a call-site proof. `lash` followed one-hop wrappers (`mov x0, x3; bl getenv`). That still left inlined Rust `env::var` (kizu) LATENT: the compiler builds a stack `CString` then `getenv` — packed literals never sit in `x0` at the `bl`.

`wad` keeps the two columns, keeps one-hop wrappers, and treats a function that memcpy’s `(ptr, len)` onto the stack and feeds that buffer to getenv as **env::var-shaped**. Callers that pass a packed `&str` become DUE.

| KIND | meaning |
| --- | --- |
| **DUE** | a getenv-shaped site *uses* this name (direct, one wrapper, or CString) |
| **LATENT** | the image set *did* document it |
| **BOTH** | both columns |

Orphan env-shaped bytes stay not-DUE. rustc’s ~12k LLVM opcodes stay out. `--min-evidence call` stays a real filter.

This is not `strings(1)`. DYLD/`LD_PRELOAD` is not the second column (malloc reentry + SIP).

## Install / run

```bash
chmod +x ./wad
./wad --help
./wad --selftest
./demo.sh
```

Python 3.9+, stdlib only. Parses Mach-O (fat / arm64e auth stubs) and ELF.

## Interaction

```
wad PROGRAM                 # KIND NAME table of PROGRAM ∪ loaded images
wad --due PROGRAM           # names a getenv/wrapper/cstring/env::var site uses
wad --latent PROGRAM        # names it documented
wad --calls PROGRAM         # sites: name, how (getenv, wrapper symbol, or CString), va
wad --wrappers PROGRAM      # one-hop wrappers: va, arg, offset, symbol
wad --cstrings PROGRAM      # CString→getenv helpers: va, ptr_arg, len_arg, symbol
wad --app python3           # application ABI including libpython
wad --min-evidence call PROGRAM
```

## Examples

Inlined Rust `env::var` (kizu release): packed `KIZU_CONFIGXDG_CONFIG_HOME` is not a getenv cstring. wad recovers the CString hop.

```bash
./wad --names --app --min-evidence call /path/to/kizu
# KIZU_CONFIG
# KIZU_STATE_DIR
# KIZU_SESSION_ID
# …

./wad --calls --app --solo /path/to/kizu | awk -F'\t' '$1=="KIZU_CONFIG"'
# KIZU_CONFIG  CString  0x1000ccb60  …/kizu
```

CPython wrappers still hold: `PYTHONHOME` is BOTH via `_env_to_dict(&key[4])`.

```bash
./wad --dump-abi --app python3 | awk -F'\t' '$1=="PYTHONHOME" || $1=="PYTHON_GIL"'
# PYTHONHOME  BOTH  wrapper + help
# PYTHON_GIL  DUE   getenv
```

Compiled CString fixture vs orphan:

```bash
cc -O1 -o /tmp/cstr fixtures/wad/host.c
./wad --app /tmp/cstr
# DUE     WAD_CSTRING        CString (memcpy + getenv)
# BOTH    WAD_CSTRING_BOTH
# LATENT  WAD_DOC_ONLY
cc -o /tmp/orphan fixtures/xref/orphan.c
./wad --app /tmp/orphan          # (no owed names)
```
