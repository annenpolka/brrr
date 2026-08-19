# mutation-21 — lode

## Primitive

The env ABI of a program is the env ABI of its **load image set**. `lode` walks `otool -L` / `ldd` (the binary + libpython/librustc_driver/…) and joins getenv names across those images, not only the main executable.

Ancestor `due` asked the main file. The miss was `python3: PYTHONHOME lives in libpython`.

## Four primitives considered

1. **lode** — walk loaded images for the owed env set. **Implemented.** Mutation of `due`.
2. Keep harvesting only the stub; document the miss. Discarded: that is the ancestor.
3. `--trace` getenv interposer. Discarded: needs a run; SIP on macOS; different object (`DUE` vs `LATENT`).
4. Walk `/proc/pid/maps` of a live process. Leftover: dynamic loads (`dlopen`) after exec.

Not leftover-name hunting, not inverse printf, not a wait-for graph.

## Why this might not exist

`ldd` answers "which libraries will this exec". `strings ./python3 | grep PYTHON` answers "what's in the stub" (nothing). `due python3` followed the symlink to a 52k Mach-O and reported zero application names. The process that actually runs still consults `PYTHONHOME` — the bytes live in the framework dylib the stub loads.

The same shape is rustc: 400k trampoline, 204MB `librustc_driver`, `RUSTC_LOG` not in the trampoline. Nobody joins those two Unix columns.

## How to run

From the worktree root:

```
./lode --help
./lode --selftest
./demo.sh
./lode --images python3
./lode --names --app python3
./lode --names --app --solo python3
./lode --images "$(rustc --print sysroot)/bin/rustc"
./lode --app --min-evidence call /path/to/kizu/src --vs-program /path/to/kizu/target/release/kizu
```

Python 3.10+, stdlib only. `./lode` is the CLI.

## Empirical transcript

### Before the improvement (v0.1: walk the load list)

Ugly fixture, packed rodata, kizu source⋈image, git — inherited from `due` and still pass.

The flip is the load list:

```
$ ./lode --images python3
main  …/python3.14  (52448)
load  …/Python      (5438480)
skip  /usr/lib/libSystem.B.dylib

$ ./lode --names --app --solo python3
# empty

$ ./lode --names --app python3 | grep PYTHON_
PYTHON_BASIC_REPL
PYTHON_GIL
PYTHON_FROZEN_MODULES
…
# 275 --app names; PYTHONHOME still missing (no underscore; help table)
# ./demo.sh v0.1: 60/61 — rustc RUSTC_LOG false FAIL from grep -q SIGPIPE
```

Synthetic host + `@rpath/libplugin.dylib`:

```
$ ./lode --names --app --solo ./host
LODE_MAIN_ONLY
$ ./lode --names --app ./host
LODE_MAIN_ONLY
LODE_PLUGIN_HOME
```

rustc trampoline vs driver:

```
$ ./lode --images "$(rustc --print sysroot)/bin/rustc"
load  …/librustc_driver-….dylib  (204378184)

$ ./lode --names --app --solo $REALC
RJEM_MALLOC_CONF
USED_ZONE_REGISTER

$ ./lode --names --app $REALC | grep RUSTC_LOG
RUSTC_LOG
# also RUSTC_BOOTSTRAP; ~12k --app names; ~19s via prefix-peel (printable-run walk was 60s)
```

`PATH`'s `rustc` is a rustup proxy and does not load the driver — pass the sysroot binary.

### After the improvement (v0.2: help-table / `$VAR` / runtime-bare)

Walking libpython was necessary and not sufficient. `PYTHONHOME` is not a NUL-terminated token and has no underscore, so `is_valid_env_token` dropped it. CPython spells it three ways:

```
PYTHONHOME      : alternate <prefix> directory …
  PYTHONHOME = \x00
Consider setting $PYTHONHOME to <prefix>[:<exec_prefix>]
```

v0.2 harvests those encodings and treats interpreter families (`PYTHONHOME`, `PERL5LIB`, `RUBYOPT`) as valid even without `_`. `--app` keeps them.

```
$ ./lode --names --app python3 | grep -E '^(PYTHONHOME|PYTHONPATH|PYTHONSTARTUP)$'
PYTHONHOME
PYTHONPATH
PYTHONSTARTUP

$ ./lode --dump-abi --app python3 | awk -F'\t' '$1=="PYTHONHOME"'
PYTHONHOME  string  …/Python.framework/…/Python  cstring-assign
```

The stub is still empty (`--solo`). The name is sourced from the loaded image, which is the point.

Demo `grep -q` on the 12k-name rustc harvest also lied: `grep -q` closes the pipe, `echo` gets SIGPIPE, `set -o pipefail` turns a hit into FAIL. Exact-line match is now a bash `[[ ]]` (`has_line`).

```
$ ./lode --names --app $REALC   # has_line RUSTC_LOG → PASS
```

`./demo.sh`: **64/64**.

## Dogfood targets

- `fixtures/ugly` (spaces, `計画.sh`, `node_modules`, packed `.bin`)
- `fixtures/load` (host + plugin dylib, `@rpath` and absolute)
- Homebrew `python3` / framework libpython
- `$(rustc --print sysroot)/bin/rustc` + `librustc_driver`
- kizu `src/` + `target/release/kizu` (system dylibs skipped; join unchanged)
- Homebrew `git`

## Surprises

- `/usr/lib/libSystem.B.dylib` is not a file on modern macOS (dyld shared cache). Treating unresolved `/usr/lib` and `/System` install names as `skip`, not `miss`, is load-bearing.
- `GO_` as a prefix seed slices `CARGO_HOME` into `GO_HOME`. Prefix peel has to live with ancestor `PREFIX_SEEDS`.
- `PYTHONHOME` is not a NUL-terminated cstring in libpython and has no underscore. After the walk it still hid in `PYTHONHOME      :` and `  PYTHONHOME = \x00` until v0.2.
- rustup's `~/.cargo/bin/rustc` is not rustc. Same class of miss as the python3 stub, one wrapper further out.
- `grep -q` + `pipefail` + a 12k-name harvest is a false FAIL (SIGPIPE). The ABI was fine.

## Failures

- Image harvest still emits compiler tokens (`PYTHON_BASIC_REPLFN`, `RUSTC_LOGU`). `--app` is not a proof.
- Full harvest of `librustc_driver` (204MB) is ~19s even with prefix peel.
- macOS `--vs-pid` still uses `ps eww`.
- `JAVA` as a runtime prefix would accept `JAVASCRIPT` if it appeared as a token.
- rustup/pyenv shims are still not followed.

## Suggested mutations

- Follow rustup/pyenv shims to the real image set.
- `--trace`: getenv interposer ∪ static ABI.
- Live `/proc/pid/maps` + `dlopen` images.
- Tighten `RIGHT_ONLY` unicode/Mach-O denylist.

## Kill / keep

**Keep.** The ancestor's object was right; the image it asked was wrong. Walking the load list plus help-table/runtime-bare extraction makes `lode python3` print `PYTHONHOME` from libpython and `lode rustc` print `RUSTC_LOG` from `librustc_driver`. That is the missing Unix column.
