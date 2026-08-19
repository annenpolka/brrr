# mutation-36 — assay

## Primitive

The env ABI of a load image set has **two columns**. `assay` splits names the image set *could* read (`getenv` / call cstrings → **DUE**) from names it *did* document (help tables, `$VAR`, `NAME =`, `environment variable NAME` → **LATENT**). **BOTH** is the intersection.

Ancestor `lode` unioned those sets. The miss was `python3: PYTHONHOME is documented; PYTHON_GIL is a getenv cstring`.

## Four primitives considered

1. **assay** — static DUE vs LATENT on the load image set. **Implemented.** Mutation of `lode`.
2. DYLD/`LD_PRELOAD` getenv interposer as the second column. Tried: not cheap. `DYLD_INTERPOSE(getenv)` re-enters through malloc (`MallocDebugReport` recursion, SIGSEGV). SIP blocks insert on system binaries. Discarded as the object; leftover for unsigned fixtures with a reentrancy-safe hook.
3. Keep the lode union; document the mix. Discarded: that is the ancestor.
4. Live `/proc/pid/maps` + `dlopen` images. Leftover: dynamic loads after exec.

Not leftover-name hunting, not inverse printf, not a wait-for graph.

## Why this might not exist

`lode python3` prints 309 `--app` names. Some are getenv arguments (`PYTHON_GIL\0`). Some are help-table rows (`PYTHONHOME      : alternate <prefix>`). Some are `$PYTHONHOME` in a sentence. The union answers "what env exists in the image set". It does not answer **which of those the binary could read vs which it wrote down**.

`strings` cannot tell. `lode --dump-abi` kept one winning `detail` and dropped the others. `strace -e getenv` needs a run (and on macOS, SIP). Nobody `comm`s help tables against getenv cstrings.

## How to run

From the worktree root:

```
./assay --help
./assay --selftest
./demo.sh
./assay --app python3
./assay --dump-abi --app python3 | awk -F'\t' '$1=="PYTHONHOME" || $1=="PYTHON_GIL"'
./assay --names --app --due python3
./assay --names --app --latent python3
./assay --names --app --due --latent python3   # BOTH only
./assay --images "$(rustc --print sysroot)/bin/rustc"
./assay --dump-abi --app "$(rustc --print sysroot)/bin/rustc" | awk -F'\t' '$1=="RUSTC_LOG" || $1=="RUSTC_GRAPHVIZ_FONT"'
```

Python 3.10+, stdlib only. `./assay` is the CLI.

## Empirical transcript

### Before the improvement (v0.1: help-table / `$VAR` / `NAME =`)

Ugly fixture, packed rodata, load-list walk, kizu source⋈image, git — inherited from `lode` and still pass.

The flip is the KIND column. Compiled `fixtures/split/host.c`:

```
$ cc -o /tmp/host fixtures/split/host.c
$ ./assay --dump-abi --app /tmp/host
ASSAY_GETENV_ONLY  DUE     cstring
ASSAY_DOC_ONLY     LATENT  help
ASSAY_DOLLAR       LATENT  dollar
ASSAY_BOTH         BOTH    cstring+help
```

`--due` drops `ASSAY_DOC_ONLY`. `--latent` drops `ASSAY_GETENV_ONLY`. `--due --latent` is `ASSAY_BOTH` only.

Homebrew python3 (libpython 5.4MB):

```
$ ./assay --dump-abi --app python3
PYTHONHOME   LATENT   assign+dollar+help     # no getenv cstring
PYTHON_GIL   DUE      cstring
PYTHONPATH   BOTH     cstring+help
# --app kinds: due=291 latent=5 both=13  (309 names)
```

LATENT-only in libpython: `PYTHONHOME`, `PYTHONCASEOK`, `PYTHONUSERBASE`, `PYTHON_COLORS`, `PYTHON_HISTORY`.

rustc trampoline vs `librustc_driver` (204MB):

```
$ ./assay --dump-abi --app $REALC
RUSTC_LOG   DUE   prefix
# --app kinds: due=12598 latent=2 both=0
```

`RUSTC_GRAPHVIZ_FONT` and `RUSTC_ICE` were **DUE** — prefix-peel of the help sentence `setting environment variable \`RUSTC_GRAPHVIZ_FONT\``. That was a lie: those bytes are documentation, not a getenv cstring.

A DYLD getenv interposer on an unsigned `host` compiled with `DYLD_INTERPOSE` crashed (malloc → getenv → hook → dlsym → malloc). Not the second column.

`./demo.sh` v0.1: **75/75** (before rustc prose).

### After the improvement (v0.2: `environment variable NAME` prose)

rustc documents env vars as English, not `NAME      :` tables. v0.2 harvests `environment variable \`NAME\`` / `environment variable NAME=` as **prose** (LATENT). Prefix-peel of a documented name does not promote it to DUE — that was the v0.1 false column.

```
$ ./assay --dump-abi --app $REALC
RUSTC_LOG             DUE     prefix
RUSTC_GRAPHVIZ_FONT   LATENT  prose
RUSTC_ICE             LATENT  prose
# --app kinds: due=12596 latent=6 both=0
```

Same binary, two columns: `RUSTC_LOG` is a packed getenv literal rustc did not write down as prose; `RUSTC_GRAPHVIZ_FONT` is prose rustc did write down and is not an isolated getenv cstring.

python3 unchanged (`PYTHONHOME` LATENT / `PYTHON_GIL` DUE) — CPython already used help-table encoding.

`./demo.sh`: **77/77**.

## Dogfood targets

- `fixtures/ugly` (spaces, `計画.sh`, `node_modules`, packed `.bin`)
- `fixtures/load` (host + plugin dylib, `@rpath`)
- `fixtures/split/host.c` (getenv-only / doc-only / `$VAR` / both)
- Homebrew `python3` / framework libpython
- `$(rustc --print sysroot)/bin/rustc` + `librustc_driver`
- kizu `src/` + `target/release/kizu`
- Homebrew `git`

## Surprises

- DYLD interposing `getenv` is not a column. malloc consults `MallocDebugReport` via getenv during the hook. The ancestor discarded `--trace` for SIP; the crash is prior to SIP.
- CPython `PYTHONHOME` is still not a NUL-terminated getenv token. Help-table / `PYTHONHOME =` / `$PYTHONHOME` are LATENT. `PYTHON_GIL` is a real cstring (DUE). `PYTHONPATH` is BOTH.
- rustc does not use `NAME      :` help tables. v0.1's two LATENT names were `$RUST_DEP_GRAPH` and `STACK_SIZE =`. The names rustc actually documents (`RUSTC_ICE`, `RUSTC_GRAPHVIZ_FONT`) were misfiled as DUE by prefix-peel of the prose.
- Prefix-peel of a documented name must not count as getenv. That rule is load-bearing for both packed C help (`\xd6ASSAY_DOC_ONLY      :`) and rustc English.
- `grep -q` / `awk … exit` on a 12k-row rustc ABI still SIGPIPEs under `pipefail`. Consume the harvest.

## Failures

- rustc `--app` is still ~12k DUE names (compiler tokens). KIND is not a proof; it is a partition of a noisy harvest.
- rustc BOTH=0: packed `env::var` literals never look like isolated cstrings, so a name that is both getenv'd and documented still classifies LATENT if the only getenv evidence is prefix-peel.
- Full harvest of `librustc_driver` (204MB) is still ~19s.
- macOS `--vs-pid` still uses `ps eww`.
- rustup/pyenv shims are still not followed.
- No runtime READ column (interposer not cheap).

## Suggested mutations

- Reentrancy-safe getenv interposer for unsigned fixtures; union READ with static KIND.
- Mach-O xref: only count a cstring as DUE if a `getenv` call site references it.
- Follow rustup/pyenv shims to the real image set.
- Tighten `--app` / `RIGHT_ONLY` denylist so rustc DUE is not 12k compiler tokens.

## Kill / keep

**Keep.** The ancestor's object was the load image set; the column it printed was a union. Distinguishing names the binary *could* read from names it *did* document is the missing Unix `comm` of getenv vs help. `assay python3` prints `PYTHONHOME LATENT` / `PYTHON_GIL DUE`. `assay rustc` prints `RUSTC_LOG DUE` / `RUSTC_GRAPHVIZ_FONT LATENT`. That is the second column.
