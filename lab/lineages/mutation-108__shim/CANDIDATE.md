# mutation-108 — shim

## Primitive

DUE is a libc-getenv / rust `__var` *use*, not a `*getenv` suffix, and rustup/xcselect are a **shim** (one cheap hop, else the word `shim`). `(no owed names)` is only a silent image. `COLOR_FORCE` peel stays not-DUE. rustc’s 12k LLVM opcodes stay out.

## Why this might not exist

`xref` made DUE a call-site column and killed assay’s 12k flood. Destroyer-xref then named two holes in one sentence each: a function named `not_a_getenv` is DUE because `endswith("getenv")`, and `/usr/bin/python3` / PATH `rustc` print the same `(no owed names)` as `int main(){return 0;}`. lash followed getenv *wrappers*. Nobody treated the *operand* as a trampoline with a role, or replaced suffix-match with an allowlist.

Forbidden: leftover-name, runtime DYLD interpose, `strings(1)`.

## How to run

From the worktree root:

```
./shim --help
./shim --selftest
./demo.sh
./shim --app /usr/bin/python3
./shim --no-follow --app /usr/bin/python3
./shim --shims /usr/bin/python3 rustc
./shim --images rustc
./shim --names --app /bin/ls
./shim --dump-abi --app python3 | awk -F'\t' '$1=="PYTHON_GIL" || $1=="PYTHONHOME"'
cc -O0 -fno-inline -o /tmp/false fixtures/shim/false.c && ./shim --app /tmp/false
cc -o /tmp/empty fixtures/shim/empty.c && ./shim --app /tmp/empty
```

Python 3.9+, stdlib only. `./shim` is the CLI.

## Empirical transcript

### v0.1: allowlist + shim role + one cheap hop

Inherited from xref and still pass: ugly tree, packed blob is not DUE, split host (`ASSAY_GETENV_ONLY` DUE / `ASSAY_DOC_ONLY` LATENT), orphan not DUE, nearby decoy dropped, `/bin/ls` is `CLICOLOR_FORCE` not `COLOR_FORCE`, Homebrew python3 `PYTHON_GIL DUE` / `PYTHONHOME LATENT`, rustc DUE is tens not 12k.

New:

```
$ cc -O0 -fno-inline -o /tmp/false fixtures/shim/false.c
$ ./shim --app /tmp/false
DUE  REAL_GETENV_NAME  call  getenv
# FALSE_DUE_NAME / FORGET_ENV_NAME absent (xref DUE’d both)

$ cc -o /tmp/empty fixtures/shim/empty.c
$ ./shim --app /tmp/empty
(no owed names)

$ ./shim --app /usr/bin/python3
shim  xcselect  /usr/bin/python3 -> …/Python3.framework/Versions/3.9/bin/python3.9
BOTH  PYTHONHOME   …
DUE   PYTHONUTF8   getenv
# xref: (no owed names)

$ ./shim --no-follow --app /usr/bin/python3
shim  xcselect  /usr/bin/python3

$ ./shim --images rustc
shim  ~/.cargo/bin/rustc  (11MB)  rustup
main  ~/.rustup/toolchains/stable-aarch64-apple-darwin/bin/rustc  payload
load  …/librustc_driver-….dylib  (204MB)
```

`--shims rustc` / `--shims /usr/bin/python3` print the hop without harvesting the payload.

Homebrew `python3` is not a shim (cellar stub + 5.4MB libpython). `PYTHON_GIL` stays DUE.

### After the improvement (v0.2)

An unfollowed trampoline is not the program. `--no-follow` (and a failed hop) print `shim` and stop. rustup’s `OPENSSL_armcap` / `$HOMEXDG_CONFIG_HOME` no longer leak as rustc’s ABI.

```
$ ./shim --no-follow --app rustc
shim  rustup  ~/.cargo/bin/rustc
# not OPENSSL_armcap, not (no owed names)

$ ./shim --no-follow --app /usr/bin/python3
shim  xcselect  /usr/bin/python3
```

`--shims` / `--images` still show the hop. Default `--app rustc` still follows to the toolchain rustc.

## Dogfood targets

- `fixtures/shim/false.c`, `empty.c`
- `fixtures/split/host.c`, `fixtures/xref/orphan.c`
- `/usr/bin/python3` (SIP xcselect)
- PATH `rustc` (rustup symlink) via `--images` / `--shims` (cheap)
- Homebrew `python3` / framework libpython 3.14
- `/bin/ls` (fat arm64e)

## Surprises

- Xcode 3.9’s libpython *does* `getenv("PYTHONHOME")` (BOTH after the hop). Homebrew 3.14 still goes through `_env_to_dict` and stays LATENT without lash. Following the shim surfaces a different object, not a different column.
- `xcrun --find python3` is 4ms; `rustup which rustc` is 7ms. The hop is cheaper than reading the trampoline.
- Harvesting PATH `rustc` without follow *was* rustup’s ABI (`OPENSSL_armcap` DUE, `$HOMEXDG_CONFIG_HOME` LATENT). v0.2 refuses that harvest: the trampoline is not the program.

## Failures

- One hop only. pyenv shell shims are scripts, not this object.
- Inlined Rust `env::var` (kizu release) is still not DUE. Wrapper argv (`PYTHONHOME` on Homebrew 3.14) is still LATENT. False LATENT `STACK_SIZE` remains.
- Failed hop (no Xcode, SIP-blocked `xcrun`) prints `shim` with no payload. Honest.
- `--app rustc` following into `librustc_driver` is still ~15s; `--images` / `--shims` are the cheap porcelain.

## Suggested mutations

- One-hop getenv wrappers (lash) on the *payload* (Xcode 3.9 already getenv’s PYTHONHOME; Homebrew 3.14 still needs the wrapper hop).
- Inlined CString `env::var` (wad).
- pyenv/asdf script shims as a second role, or refuse them with `shim  script`.

## Kill / keep

**Keep.** The three-way split is nameable in one line: suffix-`getenv` is not DUE, silent main is empty, rustup/xcselect print `shim` and hop when cheap. That is not `strings(1)`, and it is not leftover-name.
