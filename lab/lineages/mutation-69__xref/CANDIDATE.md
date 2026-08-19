# mutation-69 — xref

## Primitive

The env ABI of a load image set has **two columns**, and **DUE is a getenv-shaped use, not an env-shaped token**. `xref` walks `otool -L` / `ldd` like `lode`/`assay`, keeps LATENT as names the image *did* document (help tables, `$VAR`, `NAME =`, `environment variable NAME`), and counts an isolated cstring as DUE **only if** a `getenv` / `env::var` / `std::getenv` call site references it. BOTH is the intersection. Prefix/packed harvest is a search aid for LATENT and `--loose`, not a KIND promotion.

## Why this might not exist

`assay python3` printed `PYTHONHOME LATENT` / `PYTHON_GIL DUE` — a real split `strings(1)` cannot make. Then `assay rustc` printed **12,596 DUE names**, almost all LLVM opcodes, because DUE meant “env-shaped bytes exist.” `/bin/ls --app` printed `COLOR_FORCE` (a prefix-peel of `CLICOLOR_FORCE`) and missed the real getenv. Orphan `ORPHAN_ENV_NAME` with no `getenv` was DUE. Nobody xrefs Mach-O/ELF call sites against getenv stubs and `comm`s that set with help-table documentation.

`strace -e getenv` needs a run (SIP on macOS). DYLD interposing `getenv` re-enters malloc. The missing Unix column is a **static xref**.

## How to run

From the worktree root:

```
./xref --help
./xref --selftest
./demo.sh
./xref --app python3
./xref --dump-abi --app python3 | awk -F'\t' '$1=="PYTHONHOME" || $1=="PYTHON_GIL"'
./xref --names --app --due python3
./xref --names --app --latent python3
./xref --names --app --due --latent python3
./xref --app /bin/ls
cc -o /tmp/host fixtures/split/host.c && ./xref --app /tmp/host
./xref --calls --app python3
./xref --images "$(rustc --print sysroot)/bin/rustc"
./xref --dump-abi --app "$(rustc --print sysroot)/bin/rustc" | awk -F'\t' '$1=="RUSTC_LOG" || $1=="RUSTC_GRAPHVIZ_FONT"'
```

Python 3.9+, stdlib only. `./xref` is the CLI.

## Empirical transcript

### v0.1: Mach-O/ELF getenv xref as DUE

Ugly fixture, load-list walk, env join, kizu source names — inherited from `assay`/`lode` and still pass. Packed `.bin` tokens are **no longer DUE** without a call site (`--loose` still peels them).

Compiled `fixtures/split/host.c`:

```
$ cc -o /tmp/host fixtures/split/host.c
$ ./xref --app /tmp/host
BOTH    ASSAY_BOTH         call  getenv+help
DUE     ASSAY_GETENV_ONLY  call  getenv
LATENT  ASSAY_DOC_ONLY     string  help
LATENT  ASSAY_DOLLAR       string  dollar
```

`--min-evidence call` keeps `ASSAY_GETENV_ONLY` (destroyer: assay printed empty). Evidence is `call`, not `string`.

Orphan / nearby:

```
$ ./xref --app fixtures/xref/orphan.bin     # (no owed names)
$ ./xref --app fixtures/xref/nearby.bin     # REAL_GETENV_NAME only
```

`/bin/ls` (fat arm64e, auth stubs):

```
$ ./xref --names --app /bin/ls
CLICOLOR_FORCE
LSCOLORS
LS_COLWIDTHS
LS_SAMESORT
# not COLOR_FORCE
```

Homebrew python3 (libpython 5.4MB, 2.46s):

```
# 37 names  due=19  latent=10  both=8     (assay: 309 / due=291)
PYTHONHOME   LATENT  assign+dollar+help
PYTHON_GIL   DUE     call+getenv
```

`/usr/bin/python3` (xcselect, SIP): 0 names. Fail-closed.

Sysroot rustc + 204MB `librustc_driver` (37s):

```
# 44 names  due=38  latent=3  both=3     (assay: 12602 / due=12596)
RUSTC_LOG              DUE   env::var_os
RUSTC_GRAPHVIZ_FONT    BOTH  env::var + prose
RUSTC_ICE              BOTH  env::var_os + prose
# no AMDGPU_BUFFER_ATOMIC_ADD
```

FONT/ICE are BOTH, not LATENT-only: rustc *does* `env::var` them, and it documents them. Assay could not see the use (packed `&str`, not a cstring).

Homebrew git: 78 `--app` names, `GIT_DIR` BOTH, `ARRAY_SIZE` gone (assay: 304 / 298 DUE).

`./demo.sh` v0.1: **76/76**.

### After the improvement (v0.2)

Three load-bearing fixes, none of them a second column:

1. **Packed/prefix harvest is `--loose` only.** Default binary extract is xref + doc. rustc 204MB: **37s → 15s**. HOW for `RUSTC_LOG` is `env::var_os`, not `call+prefix+string`.
2. **`--calls`** prints the sites: `PYTHON_GIL  getenv  0x1f6b9c  …/Python` (0.17s). The primitive is inspectable.
3. **`--vs-program` needles survive the weak-only filter.** kizu source⋈image: `KIZU_CONFIG` **BOTH** (v0.1 was LEFT_ONLY because packed literals in the image are not getenv xrefs, and the needle how was dropped).

```
$ ./xref --calls --app python3 | awk -F'\t' '$1=="PYTHON_GIL"'
PYTHON_GIL	getenv	0x1f6b9c	…/Python.framework/…/Python

$ ./xref --dump-abi --app $REALC   # 15.2s, still due=38 latent=3 both=3
RUSTC_LOG   DUE   env::var_os
```

`./demo.sh` v0.2: **78/78**.

## Dogfood targets

- `fixtures/ugly` (spaces, `計画.sh`, `node_modules`, packed `.bin`)
- `fixtures/load` (host + plugin dylib, `@rpath`)
- `fixtures/split/host.c` (getenv-only / doc-only / `$VAR` / both)
- `fixtures/xref/orphan.c`, `nearby.c`
- Homebrew `python3` / framework libpython
- `/usr/bin/python3` (SIP xcselect shim)
- `/bin/ls` (fat arm64e)
- `$(rustc --print sysroot)/bin/rustc` + `librustc_driver`
- kizu `src/` + `target/release/kizu`
- Homebrew `git`

## Surprises

- CPython `PYTHON_GIL` is a direct `bl _getenv`, not `_Py_GETENV`. `_Py_GETENV` is a wrapper used for a handful of names (`PYTHONBREAKPOINT`, …). Name-matching `*getenv` catches both.
- `PYTHONHOME` really is not a getenv *literal* in libpython 3.14: it goes through `_config_get_env_dup` (name in `x3`). Direct xref keeps it LATENT. That matches the poster and is still a lie about runtime capability — wrapper-arg xref is leftover.
- Rust `env::var` passes `(ptr, len)` in `x0,w1`. The bytes are packed (`RUSTC_LOGUnable to install…`). Length is load-bearing; treating it as a cstring would glue the next sentence on.
- `/bin/ls` is fat + arm64e `__auth_stubs` (16-byte slots). Ordinary `bl` to the stub still works. SIP does not block a static xref of an on-disk image.
- kizu’s *source* still xrefs; the release image inlines `env::var` into a stack `CString` + `getenv`, so packed literals do not sit in `x0` at the `bl`. Source⋈image LEFT_ONLY. Honest about inlining.

## Failures

- Full harvest of `librustc_driver` is ~15s (doc regex + xref). Prefix peel no longer runs by default.
- Wrapper getenv (`_config_get_env_dup`, `_Py_get_env_flag`) is not followed, so some real CPython reads stay LATENT (`PYTHONHOME`, `PYTHONPATH`).
- Inlined Rust `env::var` (kizu) is not a DUE xref; `--vs-program` needles still join the packed bytes as BOTH.
- False LATENT `STACK_SIZE` from GPU assembler `NAME =` tables remains (destroyer mutation 4, not this column).
- rustup/pyenv/xcselect shims are still not followed (`(no owed names)` on `/usr/bin/python3`).
- No runtime READ column.

## Suggested mutations

- One-hop wrappers: if a function moves an argument register into `x0` and `bl getenv`, treat that function as getenv-shaped with that argv index (`PYTHONHOME` would become BOTH).
- Follow rustup/xcselect shims, or print `shim` instead of `(no owed names)`.
- Tighten false LATENT `NAME =` (GPU tables).
- Recover inlined Rust `env::var` via the `CString` construction that feeds `getenv` (kizu).

## Kill / keep

**Keep.** Assay’s split is real and its DUE column is a flood. Xref keeps the load image set and the LATENT harvest, and makes DUE a proof of use: `PYTHON_GIL` stays, `ORPHAN_ENV_NAME` / `COLOR_FORCE` / 12k LLVM opcodes go, rustc DUE is 38, `--min-evidence call` works on binaries. That is not `strings(1)`.
