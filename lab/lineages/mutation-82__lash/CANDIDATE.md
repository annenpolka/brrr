# mutation-82 — lash

## Primitive

DUE is a getenv-shaped use, **including one-hop wrappers**. If a function moves an argument register into `x0` (optionally `+imm`) and `bl getenv`, that function is getenv-shaped at that argv index. CPython `PYTHONHOME` (`_env_to_dict` key+4) and `PYTHONPATH` (`_config_get_env_dup` x3) become BOTH. A second hop is not followed. Orphan env-shaped bytes stay not-DUE. rustc’s 12k LLVM opcodes stay out. `--min-evidence call` remains a real filter.

## Why this might not exist

`xref` made DUE a getenv *call-site* proof and killed assay’s 12k LLVM flood. Its leftover, named in CANDIDATE, was wrappers whose names are not `*getenv`: `_config_get_env_dup` (`mov x0, x3; bl getenv`), `_Py_get_env_flag` (`mov x0, x2`), `_env_to_dict` (`add x0, x1, #4` so `ENV_PYTHONHOME` → `PYTHONHOME`). Direct xref printed `PYTHONHOME LATENT` — a lie about runtime capability. Nobody treats “arg register → x0 → getenv” as a getenv-shaped callee at that argv index.

Forbidden: `strings(1)`, a third ambit, DYLD interpose of getenv (SIP + malloc reentry).

## How to run

From the worktree root:

```
./lash --help
./lash --selftest
./demo.sh
./lash --app python3
./lash --dump-abi --app python3 | awk -F'\t' '$1=="PYTHONHOME" || $1=="PYTHONPATH" || $1=="PYTHON_GIL"'
./lash --calls --app python3 | awk -F'\t' '$1=="PYTHONHOME" || $1=="PYTHONPATH"'
./lash --wrappers --app python3
cc -O0 -o /tmp/wrap fixtures/wrap/host.c && ./lash --app /tmp/wrap
./lash --names --app /bin/ls
./lash --dump-abi --app "$(rustc --print sysroot)/bin/rustc" | awk -F'\t' '$1=="RUSTC_LOG" || $1=="RUSTC_GRAPHVIZ_FONT"'
```

Python 3.9+, stdlib only. `./lash` is the CLI.

## Empirical transcript

### v0.1: one-hop wrapper follow

Inherited from xref and still pass: ugly tree, packed blob is not DUE, load-list walk, split host (`ASSAY_GETENV_ONLY` DUE / `ASSAY_DOC_ONLY` LATENT), orphan not DUE, nearby decoy dropped, `/bin/ls` is `CLICOLOR_FORCE` not `COLOR_FORCE`, `/usr/bin/python3` empty (xcselect shim), rustc DUE is tens not 12k, kizu source⋈image, git `GIT_DIR` BOTH / no `ARRAY_SIZE`.

New fixture `fixtures/wrap/host.c` (`-O0` so args spill; stack-slot tracking required):

```
$ cc -O0 -o /tmp/wrap fixtures/wrap/host.c
$ ./lash --app /tmp/wrap
DUE     LASH_WRAP_ARG3    call  wrapper   # wrap_dup x3→getenv
BOTH    LASH_WRAP_BOTH    call  wrapper+help
DUE     LASH_OFFSET       call  wrapper   # env_to(key+4), not ENV_LASH_OFFSET
DUE     LASH_DIRECT       call  getenv
LATENT  LASH_DOC_ONLY     string help
$ ./lash --wrappers --app /tmp/wrap
0x…  3  0  _wrap_dup
0x…  0  4  _env_to
$ ./lash --names --app --min-evidence call /tmp/wrap
LASH_DIRECT
LASH_OFFSET
LASH_WRAP_ARG3
LASH_WRAP_BOTH
# not LASH_DOC_ONLY
```

Homebrew python3 (libpython 5.4MB, 0.54s):

```
# 45 names  due=27  latent=4  both=14     (xref: 37 / due=19 / both=8; assay: 309 / due=291)
PYTHONHOME   BOTH   assign+call+dollar+help+wrapper
PYTHONPATH   BOTH   assign+call+help+wrapper
PYTHON_GIL   DUE    getenv
PYTHONCASEOK LATENT help          # Windows-oriented, no Unix getenv site
```

`--wrappers --app python3`:

```
0x1f681c  3  0  _config_get_env_dup
0x207f6c  2  0  __Py_get_env_flag
0x2c14a0  1  4  _env_to_dict
```

`/usr/bin/python3` (xcselect, SIP): 0 names. Fail-closed.

Sysroot rustc + 204MB `librustc_driver` (16.4s):

```
# 44 names  due=38  latent=3  both=3     (assay: 12602 / due=12596)
RUSTC_LOG              DUE   env::var_os
RUSTC_GRAPHVIZ_FONT    BOTH  env::var + prose
RUSTC_ICE              BOTH  env::var_os + prose
# no AMDGPU_BUFFER_ATOMIC_ADD
# 7 wrappers (rustc env helpers); DUE count unchanged from xref
```

Homebrew git: 144 `--app` names (wrapper hops through `_git_env_bool` / `_getenv_safe`), `GIT_DIR` BOTH, `ARRAY_SIZE` gone.

`./lash --selftest` v0.1: ok (wrapper fixture included).

### After the improvement (v0.2)

`--calls` names the wrapper **symbol**, not a generic `wrapper` how. The hop is inspectable without joining `--wrappers` by hand. Generic `wrapper` stays in `hows` so KIND/filter stay stable.

```
$ ./lash --calls --app python3 | awk -F'\t' '$1=="PYTHONHOME" || $1=="PYTHONPATH" || $1=="PYTHON_GIL"'
PYTHON_GIL    getenv                 0x1f6b9c  …/Python
PYTHONPATH    _config_get_env_dup    0x1f6a94  …/Python
PYTHONHOME    _env_to_dict           0x2c0d30  …/Python
```

That is the poster: `PYTHON_GIL` is a direct `bl getenv`; `PYTHONPATH` is argv3 of `_config_get_env_dup`; `PYTHONHOME` is argv1+4 of `_env_to_dict` (`getenv(&"ENV_PYTHONHOME"[4])`).

## Dogfood targets

- `fixtures/ugly` (spaces, `計画.sh`, `node_modules`, packed `.bin`)
- `fixtures/load` (host + plugin dylib, `@rpath`)
- `fixtures/split/host.c` (getenv-only / doc-only / `$VAR` / both)
- `fixtures/xref/orphan.c`, `nearby.c`
- `fixtures/wrap/host.c` (arg3 wrapper, ENV_+4 offset, documented both)
- Homebrew `python3` / framework libpython 3.14
- `/usr/bin/python3` (SIP xcselect shim)
- `/bin/ls` (fat arm64e)
- `$(rustc --print sysroot)/bin/rustc` + `librustc_driver`
- kizu `src/` + `target/release/kizu`
- Homebrew `git`

## Surprises

- CPython `PYTHONHOME` is **not** a NUL-terminated `getenv("PYTHONHOME")` cstring at all. Frozen getpath does `env_to_dict(dict, "ENV_PYTHONHOME")` → `getenv(&key[4])`. The hop is offset 4 on argv 1, not a missing literal. Recovering without the offset would DUE `ENV_PYTHONHOME`, which is not an env var.
- `_config_get_env_dup` on Unix drops the unused `wchar_t *wname` from the ABI (static function), so the UTF-8 name lands in `x3` after the hidden `PyStatus*` return. Matching the assembly, not the C prototype, is load-bearing.
- `-O0` fixtures spill args (`str x3, [sp]; ldr x0, [sp]`) before `bl getenv`. Optimized libpython does `mov x0, x3`. Wrapper discovery has to track SP/FP slots or the lab fixture fails while CPython works.
- `_Py_GETENV` is already a getenv-shaped *symbol* (`*GETENV`); xref already followed its callers. The leftover was wrappers **not** named getenv.
- rustc grows 7 wrappers (`env_var_os`, `LoggerConfig::from_env`, …) and **zero** extra DUE names vs xref. The hop does not re-open the LLVM flood.
- git DUE grows (78 → 144 `--app` names) because `_git_env_bool` / `_getenv_safe` are real hops. `ARRAY_SIZE` still absent.

## Failures

- `PYTHONCASEOK` / `PYTHONUSERBASE` / `PYTHON_COLORS` / `PYTHON_HISTORY` stay LATENT: help-table only on this Unix image (CASEOK is Windows; HISTORY is frozen Python). Honest, not a missed `_config_get_env_dup`.
- rustc harvest of 204MB `librustc_driver` is still ~16s (doc regex + xref). Wrapper discovery itself is ~3s.
- Inlined Rust `env::var` (kizu release image) is still not a DUE xref; `--vs-program` needles still join packed bytes as BOTH.
- rustup/xcselect shims still fail closed (`(no owed names)` on `/usr/bin/python3`).
- No runtime READ column. No second hop (wrapper-of-wrapper).
- False LATENT `STACK_SIZE` from GPU `NAME =` tables remains (destroyer mutation 4, not this column).

## Suggested mutations

- Second hop, or a cap: if FOO is getenv-shaped and BAR moves an arg into FOO’s argv register, BAR is too. Easy to flood; keep one hop unless a named miss appears.
- Follow rustup/xcselect shims, or print `shim` instead of `(no owed names)`.
- Recover inlined Rust `env::var` via the `CString` construction that feeds `getenv` (kizu).
- Tighten false LATENT `NAME =` (GPU tables).

## Kill / keep

**Keep.** Xref made DUE a getenv proof and left a hole you can name in one sentence: wrappers. lash follows exactly that hop. `PYTHONHOME` / `PYTHONPATH` become BOTH; orphans and 12k LLVM opcodes stay out; `--min-evidence call` still means call. `--calls` prints `_env_to_dict` / `_config_get_env_dup`. That is not `strings(1)`, and it is not a second column.
