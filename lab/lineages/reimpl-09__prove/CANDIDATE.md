# reimpl-09 — prove

## Primitive

The env ABI of a load image set has **two columns**, and **DUE is a getenv-shaped use, not an env-shaped token**. `prove` walks the load list (`LC_LOAD_DYLIB` / `DT_NEEDED` + `@rpath`), keeps LATENT as names the image *did* document (help tables, `$VAR`, `NAME =`, `environment variable NAME`), and counts a name as DUE **only if** a `getenv` / `env::var` / `env::var_os` call site references it. BOTH is the intersection.

## Why this might not exist

`assay python3` printed `PYTHONHOME LATENT` / `PYTHON_GIL DUE` — a real split `strings(1)` cannot make. Then `assay rustc` printed **12,596 DUE names**, almost all LLVM opcodes, because DUE meant “env-shaped bytes exist.” `/bin/ls --app` printed `COLOR_FORCE` (a prefix-peel of `CLICOLOR_FORCE`) and missed the real getenv. Orphan `ORPHAN_ENV_NAME` with no `getenv` was DUE. Nobody xrefs Mach-O/ELF call sites against getenv stubs and `comm`s that set with help-table documentation.

`strace -e getenv` needs a run (SIP on macOS). DYLD interposing `getenv` re-enters malloc. The missing Unix column is a **static xref**.

This is a clean-room reimplementation of that mutation (xref / DESTROYER_ASSAY). The xref Python/Rust sources were never opened. Behavior was recovered from DESTROYER_ASSAY, assay’s published split, and xref’s CANDIDATE claims + failures.

## How to run

From the worktree root:

```
./prove --help
./prove --selftest
./demo.sh
./prove --app python3
./prove --dump-abi --app python3 | awk -F'\t' '$1=="PYTHONHOME" || $1=="PYTHON_GIL"'
./prove --names --app --due python3
./prove --names --app --latent python3
./prove --names --app --due --latent python3
./prove --app /bin/ls
cc -o /tmp/host fixtures/split/host.c && ./prove --app /tmp/host
./prove --calls --app python3
./prove --images "$(rustc --print sysroot)/bin/rustc"
./prove --dump-abi --app "$(rustc --print sysroot)/bin/rustc" | awk -F'\t' '$1=="RUSTC_LOG" || $1=="RUSTC_GRAPHVIZ_FONT"'
```

Python 3.9+, stdlib only. `./prove` is the CLI.

## Empirical transcript

### v0.1: Mach-O getenv / `std::env::__var` xref as DUE

Independently: parse fat Mach-O, map `__stubs` / `__auth_stubs` via the indirect symbol table, scan `bl`/`b` to `getenv` and to rustc v0-mangled `std::env::__var` / `__var_os` / `unix::getenv`. Recover C `adrp+add` cstrings and Rust `(ptr,len)` in `x0,w1`.

Compiled `fixtures/split/host.c` (assay’s 40-byte split is real, evidence is now `call`):

```
$ cc -o /tmp/host fixtures/split/host.c
$ ./prove --app /tmp/host
BOTH    ASSAY_BOTH         call  getenv+help
DUE     ASSAY_GETENV_ONLY  call  getenv
LATENT  ASSAY_DOC_ONLY     string  help
LATENT  ASSAY_DOLLAR       string  dollar
```

`--min-evidence call` keeps `ASSAY_GETENV_ONLY` (destroyer: assay printed empty).

Orphan / nearby:

```
$ ./prove --app fixtures/xref/orphan.bin     # (no owed names)
$ ./prove --app fixtures/xref/nearby.bin     # REAL_GETENV_NAME only
```

`/bin/ls` (fat arm64e, auth stubs): `CLICOLOR_FORCE`, `LSCOLORS` — not `COLOR_FORCE`.

Homebrew python3 (libpython 5.4MB, 0.60s):

```
# 41 names  due=20  latent=13  both=8     (assay: 309 / due=291)
PYTHONHOME   LATENT  assign+dollar+help
PYTHON_GIL   DUE     getenv
```

`--calls`: `PYTHON_GIL  getenv  0x1f6b9c  …/Python` (matches the claimed site).

Sysroot rustc + 204MB `librustc_driver` (20.5s):

```
# 116 names  due=37  latent=76  both=3     (assay: 12602 / due=12596)
RUSTC_LOG              DUE   env::var_os
RUSTC_GRAPHVIZ_FONT    BOTH  env::var + prose
RUSTC_ICE              BOTH  env::var_os + prose
# no AMDGPU_BUFFER_ATOMIC_ADD
```

DUE collapse held (37 vs claimed 38). LATENT did not: whole-file regex treated GPU assembler / code bytes as `NAME      :` and `$VAR` (`A0H`, `TTTTTTTT…`). Stale `w1` truncated `LLVM_DISABLE_SYMBOLIZATION` to `LLVM_DISABLE_SY`.

### After the improvement (v0.2)

Two load-bearing fixes, not a second column:

1. **LATENT scans string-bearing sections**, not `__text`. Help / `$VAR` / `NAME =` also require an env-shaped name (`_` or a known bare token such as `PYTHONHOME`). That is destroyer mutation 4 (GPU `NAME =` tables) done as a harvest bound, not a denylist.
2. **Rust `&str` length is only trusted when `w1` was written next to `x0`.** Packed `RUSTC_LOGUnable…` still uses length 9; a leftover `w1` no longer peels `LLVM_DISABLE_SY`.

```
$ ./prove --dump-abi --app python3     # 0.45s
# 35 names  due=19  latent=8  both=8     (xref claim: 37 / due=19)
PYTHONHOME   LATENT
PYTHON_GIL   DUE     getenv  (0x1f6b9c)

$ ./prove --dump-abi --app $REALC      # 14.3s
# 42 names  due=35  latent=4  both=3     (xref claim: 44 / due=38)
RUSTC_LOG              DUE   env::var_os
RUSTC_GRAPHVIZ_FONT    BOTH  env::var+prose
RUSTC_ICE              BOTH  env::var_os+prose
LLVM_DISABLE_SYMBOLIZATION DUE   # full name, not LLVM_DISABLE_SY
# LATENT: CARGO_INCREMENTAL, CARGO_TARGET_DIR, SESSION_GLOBALS, SOME_CONST
```

`./demo.sh` v0.2: **78/78**.

## Dogfood targets

- `fixtures/split/host.c` (getenv-only / doc-only / `$VAR` / both) — assay KIND split, evidence=call
- `fixtures/xref/orphan.c`, `nearby.c`
- `fixtures/load` (host + plugin dylib, `@rpath`)
- `fixtures/ugly` (spaces, `計画.sh`, `node_modules`)
- Homebrew `python3` / framework libpython
- `/usr/bin/python3` (SIP xcselect shim)
- `/bin/ls` (fat arm64e)
- `$(rustc --print sysroot)/bin/rustc` + `librustc_driver`
- Homebrew `git`
- kizu `src/` + `target/release/kizu` (`--vs-program` needles)

## Surprises

- CPython `PYTHON_GIL` is a direct `bl _getenv` at `0x1f6b9c`, not `_Py_GETENV`. Name-matching `*getenv` plus the stub table catches it. `_Py_GETENV` is a passthrough that still preserves `x0`.
- `PYTHONHOME` / `PYTHONPATH` really are not getenv *literals* in libpython 3.14. Direct xref keeps them LATENT. That matches the poster and is still a lie about runtime capability — wrapper-arg xref is leftover.
- Rust `env::var` is not a public symbol on `librustc_driver`. The callees are v0-mangled `std::env::__var` / `__var_os`, ABI `(ptr, len)` in `x0,w1`. Packed `RUSTC_LOGUnable to install…` needs that length.
- `/bin/ls` is fat + arm64e `__auth_stubs` (16-byte slots). Ordinary `bl` to the stub still works. SIP does not block a static xref of an on-disk image.
- Assay’s rustc DUE flood is the 3-part `is_likely_env_name` clause plus prefix-peel. Once DUE is a call site, `--app` only needs to hide `LIBC_ENV`. Throwing away that clause is not a denylist; it is the column.

## Failures

- rustc DUE is **35**, not the claimed **38**. Honest: `__var` xref + freshness drops stale peels (`TER`, `LLVM_DISABLE_SY`) that a looser `w1` would have counted. No AMDGPU opcodes either way.
- Wrapper getenv (`_config_get_env_dup`, `_Py_get_env_flag`) is not followed, so some real CPython reads stay LATENT (`PYTHONHOME`, `PYTHONPATH`). The poster split survives; capability does not.
- Inlined Rust `env::var` (kizu release) is not a DUE xref; `--vs-program` needles still join packed bytes as BOTH.
- False LATENT `SESSION_GLOBALS` / `SOME_CONST` remain (dollar/assign in const). `STACK_SIZE` from GPU `NAME =` is gone.
- rustup/pyenv/xcselect shims are still not followed (`(no owed names)` on `/usr/bin/python3`; PATH `rustc` is the trampoline).
- No runtime READ column.
- Full harvest of `librustc_driver` is ~14s (doc regex + 97MB `bl` scan).

## Suggested mutations

- One-hop wrappers: if a function moves an argument register into `x0` and `bl getenv`, treat that function as getenv-shaped (`PYTHONHOME` would become BOTH).
- Follow rustup/xcselect shims, or print `shim` instead of `(no owed names)`.
- Recover inlined Rust `env::var` via the `CString` construction that feeds `getenv` (kizu).
- Drop remaining false LATENT (`SOME_CONST =`) by requiring env-ish left context on assign.

## Kill / keep

**Keep.** Assay’s split is real and its DUE column is a flood. Rebuilt from DESTROYER_ASSAY without reading xref sources, `prove` keeps the load image set and the LATENT harvest, and makes DUE a proof of use: `PYTHON_GIL` stays, `ORPHAN_ENV_NAME` / `COLOR_FORCE` / 12k LLVM opcodes go, rustc DUE is 35 (claimed 38), `--min-evidence call` works on binaries. The primitive survived a clean-room rebuild.

## Compare to assay’s published split

| target | assay KIND | prove KIND |
| --- | --- | --- |
| split `host.c` compiled | DUE `ASSAY_GETENV_ONLY` / LATENT `ASSAY_DOC_ONLY` / BOTH `ASSAY_BOTH` (evidence=`string`) | **same partition**, evidence=`call` |
| Homebrew libpython | `PYTHONHOME` LATENT / `PYTHON_GIL` DUE; `--app` 309 names, due=291 | **same poster**; 35 names, due=19 |
| `/usr/bin/python3` | empty (xcselect shim) | empty (fail-closed) |
| sysroot rustc | `RUSTC_LOG` DUE prefix / `RUSTC_GRAPHVIZ_FONT` LATENT prose; due=12596 | `RUSTC_LOG` DUE `env::var_os` / FONT **BOTH** (use+prose); due=35 |
| `/bin/ls --app` | `COLOR_FORCE` peel | `CLICOLOR_FORCE` xref |
| orphan cstring | DUE | not DUE |
