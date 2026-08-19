# mutation-45 — latent

## Primitive

The env ABI of a program is two columns: **DUE** (getenv names owed by the load-image set) and **LATENT** (names actually consulted on a traced run). The owed set is not the used set.

Parents: due (candidate-28), lode (mutation-21), orbit (candidate-30). lode walks `otool -L`/`ldd` and harvests getenv names (`PYTHONHOME` in libpython). lode discarded `--trace` as a different object. This mutation *is* that object, as a second column. Orbit (which binary will run) is not merged.

## Why this might not exist

`lode python3` prints `PYTHONHOME` because libpython contains the bytes. That is not the same statement as "this `python3 -c 'print(1)'` called `getenv("PYTHONHOME")`". Static harvest over-claims (help tables, packed rodata, unused `KIZU_*`). A traced exec under-claims if you only look at the stub. Nothing in Unix prints both columns.

`strace -e getenv` needs Linux. `DYLD_INSERT_LIBRARIES` from zsh is a lie (the shell is SIP-restricted and strips `DYLD_*`). `DYLD_PRINT_ENV` dumps the inherited environ, not lookups. latent inserts from an unrestricted Python via `posix_spawn`, rebinds `getenv` in first-party images (not libSystem — that recurses), and fail-closes when SIP strips the insert.

## How to run

```
./latent --selftest
./demo.sh
./latent python3 -c 'print(1)'
./latent --due python3
./latent --dry
./latent --images node
./latent --quiet path/to/kizu --help
```

TSV: `name<TAB>source<TAB>due|latent|both`. Exit 1 on SIP fail-closed (DUE still printed). `--dry` is the fixture interposer when the target is platform-signed.

## Empirical transcript

### Before the improvement (v0.1)

`--dry` compiled a probe that `getenv("LATENT_DUE_USED")` and built `LATENT_SYNTH` at runtime, with `LATENT_DUE_IDLE` only as a cstring. First dogfood:

- `DYLD_INTERPOSE` of `getenv` **SIGSEGV** during dyld bootstrap.
- GOT rebind of **libSystem** made the first `getenv` recurse; the probe hung; `LATENT_SYNTH` never appeared.
- Prefix peel of `LATENT_DUE_IDLE` on inner `DUE_` invented `DUE_IDLE` / `LATENT_`.
- `demo.sh` `kind_of` used `printf | awk` on rustc's 12k-row harvest: `pipefail` + SIGPIPE → exit 141 (lode's own false FAIL, repeated).

Static DUE already had the lode gold (`PYTHONHOME` from libpython, `RUSTC_LOG` from `librustc_driver` with a keep-list so 70MB libnode is capped and 204MB rustc_driver is not).

### After the improvement (v0.2)

- Constructor + GOT rebind of first-party images only; never libSystem. Recursion guard as belt.
- Complete runtime tokens are not re-split on an inner `PREFIX_`.
- Demo helpers read TSV with `<<<`; no pipes on huge harvests.
- `GO_` peel requires a left non-token byte (`CARGO_HOME` stays whole).

`./demo.sh`: **23/23**.

```
$ ./latent --dry --quiet
LATENT_DUE_IDLE    …/latent-probe    due
LATENT_DUE_USED    …/latent-probe    both
LATENT_SYNTH       trace             latent
```

```
$ ./latent python3 -c 'print(1)'
PYTHONHOME    …/Python.framework/…/Python    both
# --solo stub: no PYTHONHOME
```

```
$ ./latent --images "$(rustc --print sysroot)/bin/rustc"
keep  …/librustc_driver-….dylib  (204378184)
$ ./latent --quiet $REALC --version
RUSTC_LOG    …/librustc_driver-…    both
```

```
$ ./latent --images node
main  …/bin/node           (68384)
cap   …/libnode.147.dylib  (70269024)
```

```
$ ./latent --quiet /usr/bin/python3 -c 'print(1)'; echo $?
latent: SIP/hardened-runtime stripped the getenv interposer; LATENT is empty (fail closed).
1
```

```
$ ./latent --quiet kizu --help
KIZU_CONFIG    …/kizu    due      # owed, not used on --help
```

PATH `rustc` is rustup. DUE of that file has `RUSTUP_TOOLCHAIN`, not `RUSTC_LOG`. Tracing `rustc --version` still sees `RUSTC_LOG` as **latent** (insert inherited into the payload). That is the flip without merging orbit: we did not ask which binary will run; we asked what this exec consulted.

## Dogfood targets

- `fixtures/latent/probe.c` (`--dry`)
- `fixtures/load` host + `@rpath` plugin (`LODE_PLUGIN_HOME`)
- Homebrew `python3` / framework libpython
- `$(rustc --print sysroot)/bin/rustc` and PATH rustup `rustc`
- Homebrew `node` (70MB libnode capped)
- `/usr/bin/python3` (SIP)
- kizu `target/release/kizu --help`
- sitbone `.build/…/Sitbone` (Metal `AGX_*` / `MTL_*` leak into LATENT)

## Surprises

- `DYLD_INTERPOSE(getenv)` crashes; `puts` interpose does not. dyld uses getenv during bootstrap.
- Rebinding libSystem's getenv GOT infinite-loops even if you saved `orig = getenv` first — libc getenv bounces through that GOT.
- zsh is platform-signed: `DYLD_INSERT_LIBRARIES=… ./host` from the shell never inserts. Spawn from Homebrew python3 does.
- Homebrew `python3 -c 'print(1)'` **does** `getenv("PYTHONHOME")`. The name is both owed and used.
- `kizu --help` owes `KIZU_CONFIG` and does not use it. The columns diverge on a real binary, not just the fixture.
- PATH rustc: DUE is rustup (`RUSTUP_TOOLCHAIN`), LATENT includes the payload (`RUSTC_LOG`). Orbit would have rewritten DUE; latent does not.
- Sitbone LATENT is mostly GPU driver env (`AGX_*`, `MTL_*`) from `/System` frameworks we skip in DUE but still rebound for getenv. Honest, noisy.

## Failures

- Image harvest still emits packed glue (`KIZU_CONFIGXDG_CONFIG_HOME`, `KIZU_STATE_DIRL`) and rustc-driver compiler tokens (~12k `--likely` rows). `--app` is not a proof.
- 204MB `librustc_driver` is kept and costs ~20s (prefix peel). The cap exists so libnode does not.
- macOS interposer does not see `environ` iteration; only `getenv`. Python `os.environ` after the startup copy is silent.
- Sitbone has almost no application env ABI; LATENT is the graphics stack.

## Suggested mutations

- Do not rebind `/System` frameworks, so GUI LATENT is first-party.
- Follow rustup/xcselect for DUE (that is orbit; keep it a different object).
- Needle-first harvest of runtime-family names to make rustc DUE cheap.
- Linux `LD_PRELOAD` path is compiled in but not dogfooded here.

## Kill / keep

**Keep.** The ancestor's object was the owed set. The missed assumption was that owed = used. Two TSV columns, a fixture where they diverge, kizu `--help` where they diverge for real, python3 where they don't (`PYTHONHOME` is both), and SIP fail-closed instead of a fake LATENT. That is a Unix column that lode refused to be.
