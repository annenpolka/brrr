# lash (mutation-82)

The env ABI of a load image set, **by getenv-shaped use, including one-hop wrappers**. Ancestor `xref` made DUE a call-site proof: an isolated cstring is DUE only if `getenv` / `env::var` references it. That left CPython `PYTHONHOME` / `PYTHONPATH` LATENT, because they go through `_env_to_dict` (`add x0, x1, #4`) and `_config_get_env_dup` (`mov x0, x3`).

`lash` keeps xref’s two columns and follows **one hop**: if a function moves an argument register into `x0` (optionally plus a small constant) and `bl getenv`, that function is getenv-shaped at that argv index.

| KIND | meaning |
| --- | --- |
| **DUE** | a getenv-shaped call site *uses* this name (direct or one wrapper) |
| **LATENT** | the image set *did* document it |
| **BOTH** | both columns |

A second hop is not followed. Orphan env-shaped bytes stay not-DUE. rustc’s ~12k LLVM opcodes stay out. `--min-evidence call` stays a real filter.

This is not `strings(1)`. DYLD/`LD_PRELOAD` is not the second column (malloc reentry + SIP).

## Install / run

```bash
chmod +x ./lash
./lash --help
./lash --selftest
./demo.sh
```

Python 3.9+, stdlib only. Parses Mach-O (fat / arm64e auth stubs) and ELF. Uses `otool` on macOS for the load list.

## Interaction

```
lash PROGRAM                 # KIND NAME table of PROGRAM ∪ loaded images
lash --due PROGRAM           # names a getenv/wrapper/env::var site uses
lash --latent PROGRAM        # names it documented
lash --due --latent PROGRAM  # BOTH only
lash --calls PROGRAM         # sites: name, how (getenv or wrapper symbol), va, source
lash --wrappers PROGRAM      # one-hop wrappers: va, arg, offset, symbol
lash --app python3           # application ABI including libpython
lash --min-evidence call PROGRAM
```

## Examples

Homebrew python3: libpython *documents* `PYTHONHOME` and *getenvs* it through `_env_to_dict(&key[4])`. Direct xref called that LATENT. lash makes it BOTH.

```bash
./lash --dump-abi --app python3 | awk -F'\t' '$1=="PYTHONHOME" || $1=="PYTHON_GIL" || $1=="PYTHONPATH"'
# PYTHONHOME   BOTH   …  wrapper + help
# PYTHONPATH   BOTH   …  _config_get_env_dup
# PYTHON_GIL   DUE    …  getenv

./lash --calls --app python3 | awk -F'\t' '$1=="PYTHONHOME" || $1=="PYTHONPATH"'
# PYTHONHOME  _env_to_dict           0x2c0d30  …/Python
# PYTHONPATH  _config_get_env_dup    0x1f6a94  …/Python

./lash --wrappers --app python3
# 0x1f681c  3  0  _config_get_env_dup
# 0x207f6c  2  0  __Py_get_env_flag
# 0x2c14a0  1  4  _env_to_dict
```

Compiled wrapper fixture vs orphan cstring:

```bash
cc -O0 -o /tmp/wrap fixtures/wrap/host.c
./lash --app /tmp/wrap
# DUE     LASH_WRAP_ARG3    wrap_dup (x3 → getenv)
# DUE     LASH_OFFSET       env_to (key+4), not ENV_LASH_OFFSET
# BOTH    LASH_WRAP_BOTH
# LATENT  LASH_DOC_ONLY
cc -o /tmp/orphan fixtures/xref/orphan.c
./lash --app /tmp/orphan          # (no owed names)
```

rustc sysroot + `librustc_driver`: tens of DUE names, not ~12k LLVM opcodes.

```bash
./lash --dump-abi --app "$(rustc --print sysroot)/bin/rustc" \
  | awk -F'\t' '$1=="RUSTC_LOG" || $1=="RUSTC_GRAPHVIZ_FONT"'
```
