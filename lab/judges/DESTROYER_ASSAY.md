# DESTROYER — assay

Adversarial pass on **DUE vs LATENT** of a load image set. No rewrites. Failures are conceptual: the KIND column is a partition of a strings harvest, not a getenv proof.

- **assay** (mutation-36, v0.2.0) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b56-ac5a-7b03-a99f-4358171642bb`
- Transcript / fixtures: `/tmp/destroy-assay/`
- Logs: `/tmp/destroy-assay/logs/{host,py.app,rustc.real,usrpy,orphan,nearby}.abi`
- `./assay --selftest` still `selftest: ok` (0.04s) after the attacks.

Attacks: rustc 12k DUE names, system python, tiny fixtures, false getenv cstrings, SIP binaries, empty ABI.

Verdict: **mutate, do not kill.** This is not `strings(1)`. On the 40-byte split fixture and on Homebrew libpython the two columns are real (`ASSAY_GETENV_ONLY` DUE / `ASSAY_DOC_ONLY` LATENT; `PYTHON_GIL` DUE / `PYTHONHOME` LATENT). DUE on any large image is a flood of env-shaped bytes. KIND is encoding, not “could read.”

---

## Primitive restated

The env ABI of a **load image set** (`otool -L` / `ldd` + harvest) has two columns:

| KIND | claimed meaning | actual harvest |
| --- | --- | --- |
| **DUE** | names the image *could* getenv | isolated / packed / prefix-peeled ALLCAPS tokens |
| **LATENT** | names it *did* document | help-table `NAME      :`, `$VAR`, `NAME =`, `environment variable NAME` |
| **BOTH** | intersection | strong-read how ∪ doc how |

`kind_of` (`assay:692`): prefix-peel of a documented name stays LATENT (weak read + doc does not promote). There is **no Mach-O xref** to a `getenv` call site. Binary evidence is always `string`. `--app` hides `LIBC_ENV` and drops names that fail `is_likely_env_name`.

---

## 1. Tiny fixtures — KIND is real on a compiled host; source C has no LATENT column (conceptual)

Compiled `fixtures/split/host.c`:

```
$ cc -o /tmp/destroy-assay/bins/host fixtures/split/host.c
$ ./assay --app /tmp/destroy-assay/bins/host
KIND    NAME               EVIDENCE  SOURCE                                HOW
------  -----------------  --------  ------------------------------------  ----------------------------------------
BOTH    ASSAY_BOTH         string    …/bins/host                           cstring+help+packed+prefix+rodata+string
DUE     ASSAY_GETENV_ONLY  string    …/bins/host                           cstring+prefix+rodata+string
LATENT  ASSAY_DOC_ONLY     string    …/bins/host                           help+packed+prefix+string
LATENT  ASSAY_DOLLAR       string    …/bins/host                           dollar+packed+prefix+string
```

`strings -a` on the same binary dumps the help lines undifferentiated:

```
ASSAY_DOC_ONLY      : documented, never getenv
ASSAY_BOTH      : getenv and documented
Consider setting $ASSAY_DOLLAR to x
ASSAY_GETENV_ONLY
ASSAY_BOTH
```

strings cannot tell `ASSAY_DOC_ONLY` from `ASSAY_GETENV_ONLY`. assay can. That is the primitive. Not `strings(1)`.

`--due` drops `ASSAY_DOC_ONLY`. `--latent` drops `ASSAY_GETENV_ONLY`. `--due --latent` is `ASSAY_BOTH` only. Load-list walk on `fixtures/load` still joins `LODE_PLUGIN_HOME` from the dylib; `--solo` hides it.

The same `host.c` **as source** has no LATENT column. The C extractor is only `getenv("…")`:

```
$ ./assay --app fixtures/split/host.c
DUE   ASSAY_BOTH         call  host.c:12  getenv
DUE   ASSAY_GETENV_ONLY  call  host.c:11  getenv

$ ./assay --app --latent fixtures/split/host.c
(no owed names)
```

KIND is a **blob** object. Help-table string literals in C are invisible until compiled. `--min-evidence call` on the compiled host is also empty (every binary row is `evidence=string`):

```
$ ./assay --names --app --min-evidence call /tmp/destroy-assay/bins/host
# (empty)  rc=0
```

`--min-evidence call` is unusable on the load image the tool exists to name.

Empty / silent Mach-O (`int main(){return 0;}` / `return 42`) and a comment-only `/* getenv("DEAD_GETENV_NAME"); */` binary: `(no owed names)` rc=0. Honest.

Compiled `tiny.c` (`getenv("DUE_FIXTURE_C"); getenv("HOME");`): `--app` keeps `DUE_FIXTURE_C` as DUE `prefix+rodata` (packed against a code byte, same shape lode already named). `HOME` is a clean cstring, hidden by `--app`. The peel is load-bearing for a real getenv **and** for the false ones in §4.

---

## 2. System python — Homebrew split holds; `/usr/bin/python3` is empty air (operational)

PATH `python3` is Homebrew 3.14. Stub `--solo` is empty. Walk loads libpython (5.4MB):

```
$ ./assay --images python3
main  …/Python.framework/Versions/3.14/bin/python3.14  (52448)
load  …/Python.framework/Versions/3.14/Python          (5438480)
skip  /usr/lib/libSystem.B.dylib

$ ./assay --dump-abi --app python3
# 309 names  due=291  latent=5  both=13   real 2.28s
PYTHONHOME   LATENT  assign+cstring-assign+dollar+help+string
PYTHON_GIL   DUE     cstring+cstring-packed+packed+prefix+rodata+string
PYTHONPATH   BOTH    assign+cstring+cstring-assign+help+rodata+string
```

Byte context in libpython (not NUL-split `strings`):

```
PYTHONHOME   before=LF  after=SPACE   "PYTHONHOME      : alternate <prefi"   # help table
PYTHON_GIL   before=NUL after=NUL     "\0PYTHON_GIL\0PYTHONHASHSEED\0"       # getenv cstring
PYTHONPATH   first hit is prose       "such as PYTHONPATH)\n-h     :"
```

That is the poster. CPython **does** `getenv("PYTHONHOME")` at runtime; KIND says LATENT because those bytes are not a NUL-terminated token. The column is **encoding**, not capability. CANDIDATE already named this. Confirmed.

LATENT-only: `PYTHONHOME`, `PYTHONCASEOK`, `PYTHONUSERBASE`, `PYTHON_COLORS`, `PYTHON_HISTORY`. BOTH is the help-table names that also exist as cstrings (`PYTHONPATH`, `PYTHONSTARTUP`, `PYTHONHASHSEED`, …).

The other 265 DUE names are not `PYTHON_*`. Sample: `BOM_UTF16_BE`, `CLOCK_MONOTONIC_RAW`, `CAN_USE_PYREPL`, `CF_ONLY_AST`, `COPYFILE_DATA`. Packed peel invents `PYTHON_BASIC_REPLFN` next to real `PYTHON_BASIC_REPL`. `--app` is not an application filter; it is “not in `LIBC_ENV` and looks like `FOO_BAR_BAZ`.”

**`/usr/bin/python3` is an xcselect shim (SIP, Apple-signed).** It does not load libpython. assay does not follow it to Xcode’s `python3.9`:

```
$ codesign -dv /usr/bin/python3
Identifier=com.apple.dt.xcode_select.tool-shim-public
Authority=Software Signing

$ ./assay --images /usr/bin/python3
main  /usr/bin/python3  (118928)
skip  /usr/lib/libxcselect.dylib
skip  /usr/lib/libSystem.B.dylib

$ ./assay --dump-abi --app /usr/bin/python3
name	kind	evidence	source	detail	hows
# 0 names. PYTHONHOME MISSING.  real 0.09s
```

`--system` / `--closure` still empty: `/usr/lib/libxcselect.dylib` is **not a file** (dyld shared cache). `Path.exists()` is false. `--system` prints `miss  /usr/lib/libxcselect.dylib`. The stub’s payload is unaskable. `(no owed names)` on `/usr/bin/python3` looks like “python owes nothing,” not “this is a 119k selector.”

Same empty ABI: `/usr/bin/git` (same xcselect identifier), `/usr/bin/true`, `/bin/cat`.

---

## 3. rustc 12k DUE — the poster split is a 6-row LATENT island in an LLVM opcode dump (operational, load-bearing)

`assay rustc` follows PATH to **rustup**, not `librustc_driver`. `RUSTC_LOG` is missing. 101 `--app` names, 99 DUE (`AWS_LC_TRAMPOLINE_SHA3_256_I`, `AES_NOHW_BATCH_SIZE`, `HOMEXDG_CONFIG_HOME` as LATENT-dollar). The trampoline is a different image set. CANDIDATE said shims are not followed. Confirmed: the default invocation of the dogfood target misses the dogfood name.

Sysroot binary + 204MB driver (the README command):

```
$ REALC="$(rustc --print sysroot)/bin/rustc"
$ ./assay --images "$REALC"
main  …/bin/rustc  (412504)
load  …/lib/librustc_driver-e331a45a468a48ee.dylib  (204378184)

$ ./assay --dump-abi --app "$REALC"
# n=12602  due=12596  latent=6  both=0   real 32.94s
# every evidence=string
```

The two-column poster still holds **inside** that flood:

```
RUSTC_LOG              DUE     prefix
RUSTC_GRAPHVIZ_FONT    LATENT  prefix+prose+string
RUSTC_ICE              LATENT  prefix+prose+string
```

Driver bytes:

```
RUSTC_LOG              …RUSTC_LOGUnable to install ctrlc handler…     # packed, not a cstring
RUSTC_GRAPHVIZ_FONT    setting environment variable `RUSTC_GRAPHVIZ_FONT` (default: `Courier…`)
RUSTC_ICE              the environment variable `RUSTC_ICE` is set to `{$env_var}`
CARGO_INCREMENTAL      environment variable CARGO_INCREMENTAL=0         # LATENT prose, real
RUST_DEP_GRAPH         dump the dependency graph to $RUST_DEP_GRAPH     # LATENT dollar, real
STACK_SIZE             SQ_PGM_RESOURCES:STACK_SIZE = .R600 Clause Merge # LATENT assign, LIE
```

v0.2’s prose harvest is why FONT/ICE are LATENT instead of DUE (prefix-peel of a documented name must not promote). `BOTH=0` because packed `env::var` literals never look like isolated cstrings — CANDIDATE named this. A name rustc both getenv’s and documents still classifies LATENT.

The other 12,590 DUE names are not env. First-segment histogram: `BUFFER` 1681, `TEX` 459, `SUST` 420, `ATOMIC` 351, `SULD` 330 (AMDGPU/RISC-V/LLVM). Samples: `AMDGPU_BUFFER_ATOMIC_ADD`, `VWADD_VV_M1_MASK`, `XTENSA_SLOT0_OP`, `ABI_PCS_GOT`. Seed/suffix-ish (RUSTC_/CARGO_/LOG/PATH/…): **61 / 12596**.

`--app` did not denylist them. `is_likely_env_name` treats “≥3 underscore parts with two long alphas” as env. That is the LLVM instruction-name shape.

False DUE peels on real prefixes: `RUSTC_LOGU`, `RUSTC_` (bare prefix), `RUSTC_MUST_MATCH_EXHAUSTIVELY0`, `RUSTC_TYPE_IR0`. `--due --latent` (BOTH only) is empty. `--min-evidence call` is empty. `--names --app --due` is the 12596.

This is the flood CANDIDATE already confessed. Destroyer confirms it is not a few extras: it is the object a reader sees if they type `assay --app rustc` after following the README’s sysroot hint.

---

## 4. False getenv cstrings — DUE means “env-shaped bytes exist” (conceptual, load-bearing)

Compiled orphans, no `getenv`:

```
$ ./assay --app /tmp/destroy-assay/bins/orphan
DUE   APP_SECRET_TOKEN  cstring+prefix+rodata
DUE   ORPHAN_ENV_NAME   rodata
```

Lookup-table keys (`APP_CONFIG_PATH`, `APP_CACHE_DIR`, `APP_LOG_LEVEL`) are DUE. Nearby decoy vs real:

```
getenv("REAL_GETENV_NAME"); puts("DECOY_ENV_NAME");
# both DUE. decoy=rodata  real=cstring+rodata
```

Compiler/log tokens (`RUSTC_DRIVER_VERSION`, `PYTHON_OPCODE_NAME`, `HTTP_STATUS_CODE`, `TY_PARAM_ENV`, `ERROR_CODE_TIMEOUT`) are DUE. `BITSET_CANONICAL` / `LLVM_ON` drop unless `--loose`. `--loose` also invents `DATA_CONST` from compiler cruft.

Packed blob with **no** getenv, plus fake docs:

```
\xd6ORPHAN_PACKED_NAME\0 junkRUSTC_FAKE_TOKENXDG_CONFIG_HOME…
environment variable `LIE_PROSE`\0
FAKE_HELP      : not getenv
$FALSE_DOLLAR in a sentence
```

Default `--app`: `ORPHAN_PACKED_NAME` DUE, `RUSTC_FAKE_TOKEN` DUE, `TY_PARAM_ENV` DUE. The LATENT lies (`LIE_PROSE`, `FAKE_HELP`, `FALSE_DOLLAR`) are **invisible** until `--loose`, because `is_likely_env_name` gates the KIND column. Documented names that do not match `PREFIX_SEEDS` / `ENV_SUFFIXES` / 3-part shape never get to speak.

Compiled false help table (`FLAG_VERBOSE      : print more`, `environment variable \`FAKE_PROSE_NAME\``):

```
$ ./assay --app falsehelp
LATENT  FAKE_PROSE_NAME   packed+prose     # 3 parts, NAME ∈ ENV_SUFFIXES
LATENT  NOT_AN_ENV        dollar           # ENV ∈ ENV_SUFFIXES
# FLAG_VERBOSE / FLAG_QUIET absent

$ ./assay --app --loose falsehelp
LATENT  FLAG_VERBOSE      help             # now visible
DUE     NAME_EQUALS       packed           # `NAME_EQUALS =` assign form, not getenv
```

Macro `getenv(NAME)` with `#define NAME "MACRO_GETENV_NAME"` is DUE `rodata` — the bytes exist; there is still no xref. That one happens to be a real getenv. The orphan next to it is the same how.

**`/bin/ls` (SIP, 155k) is the tiny-binary version of the same lie.** `strings` has the real names `CLICOLOR_FORCE` and `LSCOLORS`. `--app` prints one name:

```
$ ./assay --names --app /bin/ls
COLOR_FORCE

$ ./assay --names --app --loose /bin/ls
CLICOLOR_FORCE
COLOR_FORCE
DATA_CONST
LS_COLWIDTHS
LS_SAMESORT
```

`COLOR_FORCE` is a prefix-peel of `CLICOLOR_FORCE` off `PREFIX_SEEDS["COLOR_"]`. The real name fails `is_likely_env_name` (two parts, `FORCE` not an env suffix, `CLICOLOR_` not a seed). `LSCOLORS` has no underscore, not in `BARE_APP`. `--app` on ls is **worse than `strings | grep COLOR`**.

---

## 5. SIP binaries — load list cannot enter the shared cache; DYLD is not a column (operational)

csrutil: enabled. Apple-signed platform binaries ignore `DYLD_INSERT_LIBRARIES` (`/usr/bin/true` still rc=0). That matches CANDIDATE discarding the interposer: SIP plus malloc-reentry. Destroyer did not inject; the static tool already has no READ column.

`--images` on SIP binaries lists `skip  /usr/lib/libSystem.B.dylib`. The skip is policy. `--system` cannot flip it to a harvest: the path is not on disk (dyld shared cache). libc’s real getenv names are unaskable from `/bin/ls` the same way libpython is unaskable from `/usr/bin/python3`.

`/bin/ls` without `--app` still does not emit `LSCOLORS` or `CLICOLOR_FORCE` (see §4). It does emit libc `TERM` / `COLUMNS` / `CLICOLOR` as DUE cstrings — isolated bytes in the ls image, not a walk into libncurses (also skipped).

---

## 6. Empty ABI — fail-open silence; header-only is success (operational)

| input | output | rc |
| --- | --- | --- |
| empty file / empty dir / `/dev/null` | `(no owed names)` | 0 |
| silent Mach-O | dump-abi header only | 0 |
| `--abi -` empty stdin | empty names / header | 0 |
| 4-byte `\xcf\xfa\xed\xfe` | `miss  … is not an object file`; `(no owed names)` | 0 |
| no programs | `assay: need a program/tree or --abi` | 2 |
| missing path | `not a file, directory, or PATH command` | 2 |
| `/usr/bin/python3` `--app` | `(no owed names)` | 0 |
| `--min-evidence call` on rustc / host.bin | empty | 0 |
| `python3 --solo --app` | `(no owed names)` | 0 |
| rustc `--solo --app` | `RJEM_MALLOC_CONF` / `USED_ZONE_REGISTER` | 0 |

Empty of a silent binary is honest. Empty of an xcselect shim, empty of `--min-evidence call` on a program that only exists as a blob, and empty of `python3 --solo` are three different objects with the same porcelain. There is no `status EMPTY` / `role shim`. A reader of `(no owed names)` cannot tell “this program getenv’s nothing” from “you pointed at the trampoline.”

zsh `which git` is a shell function; `assay git` then fails `not a file, directory, or PATH command` with the function body as the operand. `shutil.which("git")` is `/opt/homebrew/bin/git` and works (304 `--app` names, **298 DUE**, including `ARRAY_SIZE`, `ALLOC_GROW_BY`, `BAD_DATE_OVERFLOW`). Git is the same flood as rustc at 1% the size. LATENT=1 (`GIT_COMMONDIR` dollar). BOTH=5 (`GIT_DIR`, `GIT_AUTHOR_NAME`, …).

---

## Kill test: is it `strings(1)`?

No. Three things `strings` cannot do:

1. **KIND on mixed encodings.** Split host and libpython `PYTHONHOME` vs `PYTHON_GIL` are a comm of help-table/prose/dollar against isolated cstrings. strings dumps both as printable.
2. **Load image set.** Stub python3 / rustc trampoline vs libpython / `librustc_driver`. `otool -L` + `@rpath` is the ancestor `lode` object and still works.
3. **Prefix-peel of a documented name stays LATENT.** v0.2 rule. `RUSTC_GRAPHVIZ_FONT` packed against `options` would be DUE without prose.

Yes, for the **DUE column on any non-toy image**. DUE is env-shaped bytes (`cstring` / `prefix` / `packed` / `rodata`) with a weak `is_likely_env_name` gate. No `getenv` xref. Orphan cstrings, LLVM opcodes, `COLOR_FORCE`, `BOM_UTF16_BE`, `AWS_LC_TRAMPOLINE_*` are the same how as `PYTHON_GIL`. `--app` does not mean application.

The user rule: kill if it is strings; mutate if DUE/LATENT is real but flooded. The split is real. The flood is the object.

---

## Suggested mutation

Do not rewrite assay in a drive-by. Next mutation, one column at a time:

1. **DUE is a getenv-shaped use, not an env-shaped token.** Mach-O/ELF xref: isolated cstring counted DUE only if a `getenv` / `env::var` call site references it. Prefix/packed stay a search aid for LATENT and for `--loose`, not a KIND promotion. That kills orphan `ORPHAN_ENV_NAME`, `COLOR_FORCE`, and 12k LLVM opcodes without deleting `PYTHON_GIL`.
2. **`--app` must not emit a proper substring of a longer token.** `COLOR_FORCE` ⊂ `CLICOLOR_FORCE`; `RUSTC_LOGU` ⊂ packed `RUSTC_LOGUnable`; `PYTHON_BASIC_REPLFN`. Refuse a peel that is a prefix of another harvested name.
3. **Throw away the 3-part `is_likely_env_name` clause** (or require `PREFIX_SEEDS` / `ENV_SUFFIXES`). That clause *is* the rustc flood. Tightening it is the denylist CANDIDATE already asked for.
4. **False LATENT:** `NAME =` / `NAME      :` must not fire on GPU assembler tables (`SQ_PGM_RESOURCES:STACK_SIZE =`). Require a word boundary and env-ish left context (`environment variable`, `Consider setting $`, help-table column), not any `ALLCAPS      :`.
5. **Shims are a role, not an empty ABI.** Follow rustup / xcselect / pyenv to the payload, or print `shim` / `miss` instead of `(no owed names)`. `/usr/bin/python3` and `~/.cargo/bin/rustc` are the default operands.
6. **Leave `--min-evidence call` off binaries** (or map blob `cstring` to call-rank when xref exists). Today it deletes the object.

Keep the static split. Do not revive DYLD `--trace` as the second column (malloc reentry + SIP, already discarded). A reentrancy-safe READ union on **unsigned fixtures** is leftover, not this mutation.

---

## Evidence of run

- `./assay --selftest` → `selftest: ok` real 0.04s. Version `0.2.0`.
- Homebrew `python3 --app`: 309 names, kinds `DUE=291 LATENT=5 BOTH=13`, `PYTHONHOME` LATENT / `PYTHON_GIL` DUE. `/tmp/destroy-assay/logs/py.app.abi`.
- `/usr/bin/python3 --app`: 0 names. xcselect shim. `/tmp/destroy-assay/logs/usrpy.images`.
- Sysroot rustc `--app`: 12602 names, `DUE=12596 LATENT=6 BOTH=0`, 32.94s, 204MB driver. `/tmp/destroy-assay/logs/rustc.real.abi`.
- PATH `rustc`: rustup image, `RUSTC_LOG` missing, 101 names.
- Split host / orphan / nearby / falsehelp / ls / empty: `/tmp/destroy-assay/bins/`, logs under `/tmp/destroy-assay/logs/`.
- SIP: `csrutil` enabled; `/usr/bin/python3` `com.apple.dt.xcode_select.tool-shim-public`; `/usr/lib/libSystem.B.dylib` not a file.
