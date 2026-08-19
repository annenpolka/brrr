# mutation-92 — wad

## Primitive

DUE is a getenv-shaped use, **including the CString construction that feeds getenv**. If a function memcpy’s `(ptr, len)` onto the stack and passes that buffer to `getenv` (or a one-hop getenv wrapper), that function is env::var-shaped. Packed Rust `&str` literals at its callers become DUE. One-hop wrappers stay. Orphans stay not-DUE. rustc’s 12k LLVM opcodes stay out. `--min-evidence call` remains a real filter.

## Why this might not exist

`xref` made DUE a getenv *call-site* proof. `lash` followed wrappers whose names are not `*getenv`. Both named the leftover in one sentence: inlined Rust `env::var` (kizu) builds a `CString` then `getenv` — packed literals never sit in `x0` at the `bl`. Direct xref / wrapper follow print `KIZU_CONFIG` as source-only. Nobody treats “memcpy ARG0 of ARG1 bytes onto the stack, NUL, getenv(stack)” as env::var-shaped.

Forbidden: `strings(1)`, a third ambit, DYLD interpose of getenv (SIP + malloc reentry). leftover-name as the product.

## How to run

From the worktree root:

```
./wad --help
./wad --selftest
./demo.sh
# 108/108
./wad --app python3
./wad --dump-abi --app python3 | awk -F'\t' '$1=="PYTHONHOME" || $1=="PYTHONPATH" || $1=="PYTHON_GIL"'
./wad --calls --app python3 | awk -F'\t' '$1=="PYTHONHOME" || $1=="PYTHONPATH"'
./wad --cstrings --app "$(ls target/release/kizu 2>/dev/null || echo /Users/annenpolka/ghq/github.com/annenpolka/kizu/target/release/kizu)"
cc -O1 -o /tmp/cstr fixtures/wad/host.c && ./wad --app /tmp/cstr
rustc -O -C lto=thin -C codegen-units=1 -C strip=symbols -o /tmp/inline fixtures/wad/inline.rs && ./wad --app --min-evidence call /tmp/inline
```

Python 3.9+, stdlib only. `./wad` is the CLI.

## Empirical transcript

### v0.1: CString-from-(ptr,len) is env::var-shaped

Inherited from lash/xref and still pass: ugly tree, packed blob is not DUE, load-list walk, split host (`ASSAY_GETENV_ONLY` DUE / `ASSAY_DOC_ONLY` LATENT), orphan not DUE, nearby decoy dropped, wrap fixture (`LASH_WRAP_ARG3` DUE, `ENV_LASH_OFFSET` not DUE), `/bin/ls` is `CLICOLOR_FORCE`, `/usr/bin/python3` empty, rustc DUE is tens not 12k, git `GIT_DIR` BOTH / no `ARRAY_SIZE`.

New fixture `fixtures/wad/host.c` (`-O1` so memcpy is a call):

```
$ cc -O1 -o /tmp/cstr fixtures/wad/host.c
$ ./wad --app /tmp/cstr
DUE     WAD_CSTRING         call  CString
BOTH    WAD_CSTRING_BOTH    call  CString+help
DUE     WAD_DIRECT          call  getenv
LATENT  WAD_DOC_ONLY        string help
$ ./wad --cstrings --app /tmp/cstr
0x…  0  1  _wad_var
```

Stripped rustc `-O -C lto=thin` fixture (`fixtures/wad/inline.rs`):

```
$ ./wad --names --app --min-evidence call /tmp/inline
WAD_INLINE_NAME
WAD_PACKED_TOKEN
$ ./wad --calls --app /tmp/inline
WAD_INLINE_NAME   CString  0x…
WAD_PACKED_TOKEN  CString  0x…
```

kizu release (7.9MB, stripped, `lto=thin`, inlined `env::var`):

```
$ ./wad --names --app --min-evidence call target/release/kizu
KIZU_CONFIG
KIZU_STATE_DIR
KIZU_SESSION_ID
KIZU_EVENT_TTL_SECS
KIZU_STARTUP_TIMING_FILE
KITTY_LISTEN_ON
TMUX
ZELLIJ
# also CI / CLICOLOR_FORCE / RUST_BACKTRACE (real libc/runtime uses via the same hop)
$ ./wad --cstrings --solo --app target/release/kizu
0x1001e2ab4  0  1
0x1001e2d00  0  1
```

Source⋈image `KIZU_CONFIG` is BOTH from a real image xref, not a needle join.

Homebrew python3: wrappers unchanged (`PYTHONHOME` BOTH via `_env_to_dict`, `PYTHONPATH` BOTH via `_config_get_env_dup`, `PYTHON_GIL` DUE getenv).

### After the improvement (v0.2)

Stack immediates at a getenv site were a lone `movz` (`0x4f48` → `HO`). `movk` is now applied onto the `movz`, so `HOME` is the whole word (then `--app` hides it). A stack peel that is not an env-shaped token is dropped.

```
$ ./wad --names --app --min-evidence call $KIZU/target/release/kizu
# KIZU_CONFIG … TMUX ZELLIJ   — not HO
$ ./wad --names --min-evidence call $KIZU/target/release/kizu | grep -E '^(HO|HOME)$'
HOME
```

`--cstrings` names the two stripped helpers (`0x1001e2ab4`, `0x1001e2d00`) as `(ptr=0, len=1)`. `--calls` prints `CString` so the hop is inspectable without joining `--cstrings` by hand. Weak isolated `cstring` tokens stay weak (the how is `CString`, not `cstring`).

## Dogfood targets

- `fixtures/ugly`, `fixtures/load`, `fixtures/split`, `fixtures/xref`, `fixtures/wrap`
- `fixtures/wad/host.c` (C memcpy+getenv), `fixtures/wad/inline.rs` (stripped LTO rust)
- Homebrew `python3` / framework libpython 3.14
- `/usr/bin/python3` (SIP xcselect shim)
- `/bin/ls` (fat arm64e)
- `$(rustc --print sysroot)/bin/rustc` + `librustc_driver`
- kizu `src/` + `target/release/kizu`
- Homebrew `git`

## Surprises

- kizu has **one** `bl getenv` in the whole image. It lives in a tiny helper (`mov x0, x1; bl getenv`). The CString hop is a *second* function: memcpy `(x0, x1)` onto `sp+32`, NUL-check, `add x1, sp, #32`, `bl` that helper. Wrapper follow alone never sees the packed `&str`.
- The CString helper is stripped (`sub sp` prologue, no symbol). Function starts have to include `bl` targets that begin with `sub sp`, or a stripped rust image has no containing function.
- `__memcpy_chk` (C `-O1` + FORTIFY) is the memcpy; dest/src/n stay `x0/x1/x2`.
- `RUST_BACKTRACE` at a getenv-wrapper site is a stack copy of rodata (ldr/str + `strb wzr`), not the `(ptr,len)` helper. Stack-materialized CStrings are a second recovery, not a second column.
- rustc `env::var` is still a public `__var` / `__var_os` symbol on `librustc_driver`. The CString hop does not re-open the LLVM flood.

## Failures

- `PYTHONCASEOK` / `PYTHON_HISTORY` stay LATENT (help-table only on this Unix image).
- rustc harvest of 204MB `librustc_driver` is still ~15s.
- rustup/xcselect shims still fail closed.
- No runtime READ column. No second *wrapper* hop (wrapper-of-wrapper).
- ELF memcpy PLT is not wired as tightly as Mach-O stubs.

## Suggested mutations

- Finish movz+movk assembly so `HOME` / short immediates are whole names (or drop sub-token stack peels).
- Second wrapper hop, or a cap.
- Follow rustup/xcselect shims, or print `shim`.
- Tighten false LATENT `NAME =` (GPU tables).

## Kill / keep

**Keep.** lash followed wrappers and left a hole you can name in one sentence: inlined Rust `env::var`. wad recovers exactly that hop via the CString that feeds getenv. kizu’s packed `KIZU_CONFIG` becomes DUE; orphans and 12k LLVM opcodes stay out; `--min-evidence call` still means call. `--calls` prints `CString`. That is not `strings(1)`, and it is not a leftover-name harvest.
