# DESTROYER — xref

Adversarial pass on **DUE as a getenv call-site proof**. No rewrites of the victim. Failures are conceptual: DUE is a 24-instruction window onto a symbol whose *name* ends in `getenv` / `env::var`, in the *native fat slice*, with no wrapper hop and no `blr`. That is not a proof of use. Assay’s 12k flood is gone; the KIND column still lies in both directions.

- **xref** (mutation-69, v0.2.0) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-cb96e7158c54`
- Transcript: `/tmp/destroy-xref/transcript.txt`
- Follow-up: `/tmp/destroy-xref/followup.txt`
- Fixtures: `/tmp/destroy-xref/src/` compiled to `/tmp/destroy-xref/bins/`
- Attack driver: `/tmp/destroy-xref/attack.py`
- `./xref --selftest` → `selftest: ok` (0.17s) after the attacks. Version `0.2.0`. No rewrite.

Peels already named leftovers (do not re-run as this pass): **lash** (one-hop wrappers), **wad** (inlined Rust CString), **prove** (clean-room reimpl). This destroyer is the call-site column itself.

Attacks: `*getenv` false DUE, one- and two-hop wrappers, `key+4` offset, `--loose` KIND=DUE, inlined `env::var` / packed `(ptr,len)`, `--vs-program` needle occupancy, fat native-slice, `blr`/far-window/spill/computed, rustup/xcselect SIP shims, false LATENT `NAME =` GPU tables.

Verdict: **mutate, do not kill.** Direct `getenv("DIRECT_ENV_NAME")` is still DUE. Orphan cstrings are still not DUE by default. Homebrew libpython still prints `PYTHON_GIL DUE` / `PYTHONHOME LATENT`. Sysroot rustc is 44 names (`due=38 latent=3 both=3`), not 12,596 LLVM opcodes. `/bin/ls` is `CLICOLOR_FORCE`, not the `COLOR_FORCE` peel. That is not `strings(1)`. DUE-as-proof has holes you can name in one sentence each.

---

## Primitive restated

The env ABI of a load image set has two columns, and **DUE is claimed to be a getenv-shaped *use***:

| KIND | claimed meaning | actual harvest |
| --- | --- | --- |
| **DUE** | a `getenv` / `env::var` call site *uses* this name | `bl`/`b` to a stub or defined symbol matching `*getenv` / `*3env3var*`, with `x0` recovered in a 24-insn window (Rust: `(x0,w1)` length) on the **native fat slice** |
| **LATENT** | the image *did* document it | help-table `NAME      :`, `$VAR`, `NAME =`, `environment variable NAME` |
| **BOTH** | intersection | both hows |

`kind_of` (`xref:746`): `due and latent → BOTH`; `latent → LATENT`; **else `DUE`**. There is no “neither” KIND. `--loose` packed/orphan tokens and `--vs-program` needles therefore print as DUE without a call site. Prefix/packed harvest is `--loose` only on the default path; KIND still promotes them.

---

## 1. `*getenv` suffix is not a getenv proof — false DUE (conceptual, load-bearing)

`getenv_sym_kind` (`xref:1253`): `n.endswith("getenv")` or `"3env3var" in name`. Defined symbols are getenv *targets*. A function that is not libc `getenv` still promotes its argument cstring to DUE.

```c
char *not_a_getenv(const char *n) { puts(n); return 0; }
void forgetenv(const char *n) { (void)n; }
int main(void) {
    not_a_getenv("FALSE_DUE_NAME");
    forgetenv("FORGET_ENV_NAME");
}
```

```
$ nm bins/false-O0 | grep getenv
0000000100000460 T _not_a_getenv
0000000100000490 T _forgetenv

$ otool -tv bins/false-O0   # _main
bl _not_a_getenv     ; x0 = "FALSE_DUE_NAME"
bl _forgetenv        ; x0 = "FORGET_ENV_NAME"
# no bl _getenv

$ ./xref --app --calls bins/false-O0
FALSE_DUE_NAME   getenv  0x1000004c8
FORGET_ENV_NAME  getenv  0x1000004d4

$ ./xref --app bins/false-O0
DUE  FALSE_DUE_NAME   call  getenv
DUE  FORGET_ENV_NAME  call  getenv
```

`--calls` *labels* `getenv`. KIND is DUE. libc `getenv` is never called. `-O2` without `noinline` inlines `puts` and the lie disappears; `-O0` / `-fno-inline` is the object the symbol table actually contains.

Same heuristic: `getenv_sym_kind("foo3env3variable") == "env::var"` because `"3env3var" in name`.

**Inductive hole:** DUE is “a call to something *named* getenv,” not “a call to getenv.”

---

## 2. Wrappers, second hops, `x3`, `key+4` — real getenv is not DUE (conceptual, load-bearing)

CPython *does* `getenv("PYTHONHOME")` at runtime through `_env_to_dict(&key[4])` and `_config_get_env_dup` (`mov x0, x3`). Direct xref keeps it LATENT. Confirmed on Homebrew libpython 3.14 (5.4MB):

```
$ ./xref --dump-abi --app python3
# 37 names  due=19  latent=10  both=8
PYTHONHOME   LATENT  assign+dollar+help
PYTHONPATH   LATENT  assign+help
PYTHON_GIL   DUE     getenv          # bl _getenv at 0x1f6b9c
PYTHONBREAKPOINT BOTH getenv         # _Py_GETENV is already *GETENV

$ ./xref --calls --app python3 | awk -F'\t' '$1=="PYTHONHOME" || $1=="PYTHONPATH"'
# empty
```

Lab fixture, `-O0` so the hop exists (lash already needed stack slots here):

```
$ cc -O0 -o bins/wrap-O0 fixtures/src/wrap.c
$ otool -tv bins/wrap-O0
_wrap_dup:  ldr x0, [sp, #8]; bl _getenv
_main:      adrp+add "WRAP_ENV_NAME"; bl _wrap_dup
            adrp+add "DIRECT_ENV_NAME"; bl _getenv

$ ./xref --app bins/wrap-O0
DUE  DIRECT_ENV_NAME  call  getenv
# WRAP_ENV_NAME missing
```

`-O2` inlines `wrap_dup` to `bl _getenv` next to the literal; WRAP becomes DUE. The column is an inlining accident, not a capability.

Same shape:

| fixture | real getenv? | xref |
| --- | --- | --- |
| `hop2-O0` (`hop2→hop1→getenv`) | yes | `(no owed names)` |
| `hop2-O2` (inlined) | yes | `HOP2_ENV_NAME DUE` |
| `wrapx3-O0` (name in x3) | yes | miss |
| `offset-O0` (`getenv(key+4)` on `"ENV_OFFSET_NAME"`) | yes, reads `OFFSET_NAME` | miss |
| `offset-O2` (inlined add) | yes | `OFFSET_NAME DUE` (not `ENV_OFFSET_NAME`) |
| `docwrap-O0` (documented wrapper) | yes | `WRAP_ENV_NAME LATENT` — the poster lie |
| `spill-O0` | yes | miss |

A documented wrapper is **LATENT**: the image getenv’s it and the column says it only documented it. That is assay’s encoding split leaking back into a column that claimed to be use.

lash follows exactly one hop. A second hop is still a miss. This pass does not rewrite; it names the hole.

---

## 3. `kind_of` else-DUE — `--loose` is the assay flood with a getenv badge (conceptual, load-bearing)

```
def kind_of(need):
    due = uses_getenv(need)
    latent = is_documented(need)
    if due and latent: return "BOTH"
    if latent: return "LATENT"
    return "DUE"          # neither is still DUE
```

Default extract drops orphans (`filter_needs`: not due, not latent, not loose, not needle). `--loose` keeps them. KIND has no third value:

```
$ ./xref --app bins/orphan
(no owed names)

$ ./xref --app --loose bins/orphan
DUE  APP_SECRET_TOKEN  string  cstring+prefix+rodata
DUE  DATA_CONST        string  cstring-packed+packed    # invented
DUE  ORPHAN_ENV_NAME   string  rodata
```

kizu release, `--loose --solo --app`: **70 names**, KIND=DUE, including `BITSET_CANONICAL`, `COLOR_FORCE`, `DATA_CONST`, `KIZU_CONFIG`. The search aid is indistinguishable from a getenv proof. CANDIDATE said packed/prefix is “not a KIND promotion.” `kind_of` did not get that memo.

Needles (`--vs-program`) take the same else-DUE branch, then `classify_abi` prints occupancy `BOTH` with KIND copied from the *source* call. See §4.

---

## 4. Inlined `env::var`, packed `(ptr,len)`, kizu source⋈image (conceptual, load-bearing)

Rust `env::var` is `(ptr, len)` in `x0,w1`. Packed literals (`KIZU_CONFIGXDG_CONFIG_HOME`) are not cstrings. A debug image still has `std::env::__var` and xref hits it. A stripped LTO image inlines to a stack `CString` + `getenv`; `x0` at the `bl` is the stack buffer, not the packed `&str`.

```
$ rustc -O -C lto=thin -C strip=symbols -o bins/inline fixtures/src/inline.rs
$ ./xref --app --min-evidence call bins/inline
(no owed names)
$ ./xref --calls --app bins/inline
name	how	va	source
# empty

$ rustc -o bins/inline-dbg fixtures/src/inline.rs
$ ./xref --app --min-evidence call bins/inline-dbg
DUE  KIZU_CONFIG      call  env::var
DUE  WAD_INLINE_NAME  call  env::var
```

kizu `target/release/kizu` (stripped, `lto=thin`):

```
$ ./xref --names --app --due /path/to/kizu/src
KITTY_LISTEN_ON
KIZU_CONFIG
KIZU_EVENT_TTL_SECS
KIZU_SESSION_ID
KIZU_STARTUP_TIMING_FILE
KIZU_STATE_DIR
TMUX
ZELLIJ

$ ./xref --app --min-evidence call --solo target/release/kizu
(no owed names)
$ ./xref --calls --app --solo target/release/kizu
# empty

$ ./xref --app src --vs-program target/release/kizu
BOTH  DUE  KIZU_CONFIG  …/paths.rs:10  …/kizu  call
# every source name is occupancy-BOTH
```

`--vs-program` harvests the image with `needles=[left names]`. Packed bytes match. Status `BOTH` means “the bytes exist,” not “a getenv site uses them.” KIND is DUE because the *source* extractor saw `env::var("KIZU_CONFIG")`. The image column of the join is assay’s encoding. wad recovers the CString hop; xref does not.

`option_env!("OPTION_ENV_NAME")` is source DUE (regex) and image `LEFT_ONLY`: compile-time, never getenv. The source extractor is not the binary proof.

PATH `rustc` is a rustup symlink (11MB trampoline). `--solo --app rustc`:

```
HOMEXDG_CONFIG_HOME  LATENT  dollar    # $HOME glued to XDG_CONFIG_HOME
OPENSSL_armcap       DUE     getenv
RUSTUP_TOOLCHAIN     LATENT  prose
# RUSTC_LOG missing
```

Sysroot `$(rustc --print sysroot)/bin/rustc` + 204MB `librustc_driver`: 44 names, `RUSTC_LOG DUE env::var_os`, `RUSTC_GRAPHVIZ_FONT BOTH`. Packed length is load-bearing *when the `__var` symbol survives*. kizu’s release image is the other object.

---

## 5. Fat Mach-O — DUE is a proof of the native slice, not the image (conceptual)

```
$ cc -arch arm64   -o bins/fat-arm fixtures/src/fat_arm.c   # getenv("FAT_ARM64_NAME")
$ cc -arch x86_64  -o bins/fat-x86 fixtures/src/fat_x86.c   # getenv("FAT_X86_NAME")
$ lipo -create bins/fat-arm bins/fat-x86 -output bins/fat
$ file bins/fat
Mach-O universal binary with 2 architectures: [x86_64] [arm64]

$ ./xref --app bins/fat-arm   # DUE FAT_ARM64_NAME
$ ./xref --app bins/fat-x86   # DUE FAT_X86_NAME   (x64 recoverer works on a thin slice)
$ ./xref --app bins/fat
DUE  FAT_ARM64_NAME  call  getenv
# FAT_X86_NAME missing — real getenv in the image, other architecture
$ ./xref --calls --app bins/fat
FAT_ARM64_NAME  getenv  0x100000480
```

`macho_native_slice` prefers host arm64. The x86_64 getenv is unaskable from the fat file on this machine. `/bin/ls` is fat `x86_64+arm64e`; auth stubs happened to work on the arm64e slice (`CLICOLOR_FORCE` / `LSCOLORS` / `LS_COLWIDTHS` / `LS_SAMESORT`). That survival is not “fat is a proof of the image.”

---

## 6. `blr`, 24-insn window, stack, computed names, `environ[]` (conceptual)

`_arm64_bl_target` matches `bl`/`b` immediates only. `recover_regs` looks back **24 instructions** and tracks adrp/add/mov/movz/movk, not `ldr` from SP, not GOT.

```
$ otool -tv bins/blr
adrp x16, _getenv@GOTPAGE
ldr  x16, [x16]
adrp+add x0, "BLR_ENV_NAME"
blr  x16                 # real getenv
$ ./xref --app bins/blr
(no owed names)

$ otool -tv bins/far
adrp+add x19, "FAR_WINDOW_NAME"
nop × 30
mov x0, x19
bl _getenv               # real getenv, 30 insns from adrp
$ ./xref --app bins/far
(no owed names)
```

Window is 24. `mov x0, x19` is in range; `x19` is not, because the adrp is not. Callee-saved forwarding is not a proof.

```
$ ./xref --app bins/computed     # memcpy to stack, getenv(buf)
(no owed names)
$ ./xref --app bins/walk         # environ[] prefix walk, no getenv
(no owed names)
$ ./xref --app bins/setenv       # setenv only
(no owed names)
$ cc -O2 -o bins/indirect2 …     # volatile fn ptr = getenv; f("INDIRECT_ENV_NAME")
$ ./xref --app bins/indirect2
(no owed names)
```

`setenv` / `environ[]` / computed buffers are honest misses if the claim is “direct literal getenv.” They are holes if the claim is “could read.” `PYTHONHOME` is the same miss with a help table glued on (LATENT, not empty).

---

## 7. rustup / xcselect / SIP — `(no owed names)` is three objects (operational)

```
$ codesign -dv /usr/bin/python3
Identifier=com.apple.dt.xcode_select.tool-shim-public
Format=Mach-O universal (x86_64 arm64e)

$ ./xref --images /usr/bin/python3
main  /usr/bin/python3  (118928)
skip  /usr/lib/libxcselect.dylib
skip  /usr/lib/libSystem.B.dylib

$ ./xref --dump-abi --app /usr/bin/python3
name	kind	evidence	source	detail	hows
# 0 names. PYTHONHOME MISSING.

$ ./xref --app /usr/bin/python3
(no owed names)
```

`csrutil` enabled. `/usr/lib/libxcselect.dylib` is not a file (dyld shared cache). `--system --images /bin/ls` prints `miss  /usr/lib/libSystem.B.dylib`. libc’s getenv names are unaskable.

PATH `rustc` → `rustup` (symlink). `--images rustc` is the 11MB trampoline, not `librustc_driver`. `RUSTC_LOG` missing. Homebrew `python3` *does* follow `@rpath` to libpython (5.4MB) — the load-list object still works when the payload is a real dylib on disk.

`(no owed names)` on `/usr/bin/python3`, on `bins/blr` (real getenv via GOT), on kizu release (inlined `env::var`), and on a silent `int main(){return 0;}` is the same porcelain.

---

## 8. False LATENT `NAME =` — GPU tables and packed `$HOME` (conceptual)

`ASSIGN_ENV_RE` / `HELP_ENV_RE` fire on any `ALLCAPS =` / `ALLCAPS      :` with an env-shaped token (`SIZE` is an `ENV_SUFFIXES` member).

```
$ ./xref --app bins/gpu
LATENT  AMDGPU_BUFFER_ATOMIC_ADD  string  help     # "NAME      : opcode"
LATENT  STACK_SIZE                string  assign   # "SQ_PGM_RESOURCES:STACK_SIZE ="
```

Sysroot rustc, 44 names, LATENT=3:

```
CARGO_INCREMENTAL   LATENT  prose
CARGO_TARGET_DIR    LATENT  prose
STACK_SIZE          LATENT  assign     # GPU assembler table, not an env var
```

`$HOMEXDG_CONFIG_HOME` on rustup is LATENT-dollar: `$HOME` packed against `XDG_CONFIG_HOME`. AMDGPU opcodes are gone from DUE (the xref win). They can still arrive as LATENT help. Destroyer-assay mutation 4, still open; it is not this column’s gold, but it is a KIND lie.

Source `echo set $DOC_SHELL_NAME` is **DUE** (`evidence=shell`, `$VAR` ∈ `STRONG_READ_HOWS`). A comment-shaped dollar in a script is a getenv-shaped use. Binary `$VAR` is LATENT. The two extractors do not agree what a dollar is.

---

## What survived

- Gold split host: `ASSAY_GETENV_ONLY` DUE `getenv`, `ASSAY_DOC_ONLY` LATENT `help`, `ASSAY_BOTH` BOTH, `ASSAY_DOLLAR` LATENT. `--min-evidence call` keeps the two uses.
- Orphan default: `(no owed names)`. Nearby decoy is not the getenv argument (inherited fixture, not re-attacked as assay).
- Homebrew python3 walk: stub empty, libpython 37 names, `PYTHON_GIL DUE` at `0x1f6b9c`, not 309/291.
- `/bin/ls` fat arm64e `__auth_stubs`: `CLICOLOR_FORCE`, `LSCOLORS`, `LS_COLWIDTHS`, `LS_SAMESORT`. Not `COLOR_FORCE` as its own name.
- Sysroot rustc: 44 names, due=38, `RUSTC_LOG` `env::var_os`, no `AMDGPU_BUFFER_ATOMIC_ADD` as DUE.
- Homebrew git: 78 `--app` names, `GIT_DIR` BOTH, `ARRAY_SIZE` gone.
- Direct `getenv("DIRECT_ENV_NAME")` DUE. `setenv`-only / `environ[]` walk / computed buffer: empty (honest relative to *literal* getenv).
- `./xref --selftest` ok. No rewrite.

---

## Kill / keep

**Keep. Mutate. Do not rewrite in this pass.**

The object is still “this image *uses* this name via getenv-shaped code, and *documents* that name in help/prose.” Direct literals, `PYTHON_GIL`, rustc’s tens-not-12k, `CLICOLOR_FORCE` — all still true. Nothing in this battery turned that into `strings(1)`. Do not kill because wrappers, `*getenv` suffix, fat slices, or `--loose`. Those are mutations. Killing them would throw away a real call-site column to hide a name match.

| do not kill because | mutate toward |
| --- | --- |
| Direct `getenv` DUE; orphan default empty; `PYTHON_GIL` DUE; rustc 38 not 12k; `/bin/ls` `CLICOLOR_FORCE`; git `GIT_DIR` BOTH / no `ARRAY_SIZE`; `--min-evidence call` keeps compiled uses | **DUE is a call to libc `getenv` / rust `__var`, not a symbol suffix.** `not_a_getenv` / `forgetenv` must not DUE. Keep `_Py_GETENV` / `secure_getenv` as an allowlist, not `endswith`. |
| | **One-hop wrappers** (lash): arg-register → `x0` → `bl getenv`, including `+imm` (`ENV_PYTHONHOME`+4 → `PYTHONHOME`). `PYTHONHOME` / `PYTHONPATH` become BOTH. Second hop stays leftover unless a named miss appears. |
| | **Inlined Rust `env::var`** (wad): memcpy `(ptr,len)` onto the stack that feeds getenv is env::var-shaped. kizu `KIZU_CONFIG` becomes DUE on the release image. |
| | **`kind_of` has a neither.** Orphan / packed / needle is not DUE. `--loose` is a search aid (`WEAK` / omit KIND), not assay with a badge. `--vs-program` needles are occupancy of bytes, not KIND BOTH-as-use. |
| | **Fat: both slices, or print the slice.** `FAT_X86_NAME` is a getenv in the image. Native-only is a host accident. |
| | **`blr` / GOT / callee-saved / SP.** A 24-insn adrp window is not a proof. Track `x19` across nops, `ldr x0, [sp]`, `blr x16`. |
| | **Shims are a role.** Follow rustup/xcselect or print `shim`, not `(no owed names)`. `/usr/bin/python3` and `~/.cargo/bin/rustc` are the default operands. |
| | **False LATENT:** `NAME =` / `NAME      :` need env-ish left context. `STACK_SIZE` from GPU tables and `$HOMEXDG_CONFIG_HOME` are not documentation. Binary `$VAR` and shell `$VAR` must not disagree about KIND. |

Do not revive DYLD `--trace` as the second column (malloc reentry + SIP, already discarded). A runtime READ union on unsigned fixtures is leftover, not this mutation.

Do not grow a review platform. The next mutation is *DUE is a libc-getenv / `__var` use, including one hop*, not a prettier dump of `--loose`.

---

## Evidence of run

- `./xref --selftest` → `selftest: ok` real 0.17s. Version `0.2.0`.
- Homebrew `python3 --app`: 37 names, `DUE=19 LATENT=10 BOTH=8`, `PYTHONHOME` LATENT / `PYTHON_GIL` DUE `0x1f6b9c`. `/tmp/destroy-xref/logs/py.app.abi.txt`.
- `/usr/bin/python3 --app`: 0 names. xcselect shim. `/tmp/destroy-xref/logs/usrpy.images`.
- Sysroot rustc `--app`: 44 names, `DUE=38 LATENT=3 BOTH=3`, `STACK_SIZE` LATENT assign. `/tmp/destroy-xref/logs/rustc.real.abi.txt`.
- PATH `rustc`: rustup image, `RUSTC_LOG` missing, `HOMEXDG_CONFIG_HOME` LATENT-dollar.
- kizu source `--due`: 8 names. Release `--calls --solo`: empty. `--vs-program`: 8× occupancy BOTH. `--loose --solo`: 70 DUE packed tokens.
- `/bin/ls --app --names`: `CLICOLOR_FORCE LSCOLORS LS_COLWIDTHS LS_SAMESORT`.
- False DUE / wrappers / fat / `blr` / far / gpu: `/tmp/destroy-xref/bins/`, logs under `/tmp/destroy-xref/logs/`.
- SIP: `csrutil` enabled; `/usr/bin/python3` `com.apple.dt.xcode_select.tool-shim-public`; `/usr/lib/libSystem.B.dylib` not a file.
