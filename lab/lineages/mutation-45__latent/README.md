# latent

Env ABI of a program as two columns: **DUE** (names the load image *owes*) vs **LATENT** (names a traced exec actually `getenv`'d).

`ldd` lists libraries. `lode` harvests getenv names from those libraries. `latent` keeps that owed set and adds the used set. They are not the same.

TSV columns: `name`, `source`, `due|latent|both`.

## Install / run

```bash
chmod +x ./latent
./latent --help
./latent --selftest
./demo.sh
```

Python 3.10+, stdlib only. Needs `cc` to build the getenv interposer. Uses `otool` on macOS, `ldd` on ELF.

## Interaction

```
latent python3 -c 'print(1)'     # DUE from images ∪ LATENT from this run
latent --due python3             # owed column only (no exec)
latent --dry                     # fixture: owed-idle vs used-synth
latent --images node             # load list; libnode is capped
latent --solo python3            # main executable only (the ancestor miss)
```

Default output is TSV. `--human` / `--json` exist. libc names (`PATH`, `HOME`, `LC_*`) are hidden unless `--libc`.

Exit 0 on a successful join. Exit 1 if SIP/hardened-runtime stripped the interposer (fail closed: DUE still prints, LATENT is not invented). Exit 2 on usage errors.

macOS note: a SIP-restricted *shell* strips `DYLD_*` from children. `latent` inserts from an unrestricted `python3` via `posix_spawn`, not by exporting `DYLD_INSERT_LIBRARIES` in zsh. Platform binaries (`/usr/bin/python3`, `/bin/ls`) still strip insert — that is the fail-closed path. `--dry` always uses an adhoc fixture.

## Examples

**1. Homebrew `python3` — `PYTHONHOME` lives in libpython, and this run actually asks for it.**

```bash
./latent python3 -c 'print(1)'
# PYTHONHOME    …/Python.framework/…/Python    both
```

`--solo` (the stub) has no `PYTHONHOME`. That was lode's gold; latent adds that the name is also *used*.

**2. `kizu --help` — owed is not used.**

```bash
./latent path/to/kizu --help
# KIZU_CONFIG    …/kizu    due
```

The binary names `KIZU_CONFIG`. `--help` never `getenv`s it.

**3. PATH `rustc` is rustup. DUE is the stub; LATENT includes the payload.**

```bash
./latent --due rustc              # RUSTUP_TOOLCHAIN; no RUSTC_LOG
./latent rustc --version          # RUSTC_LOG is latent (insert inherited)
```

Orbit would have rewritten DUE to the sysroot binary. latent does not: which binary will run is a different object.

**4. `node` — do not scan 70MB `libnode` without a cap.**

```bash
./latent --images node
# main  …/bin/node  (68k)
# cap   …/libnode.147.dylib  (70MB)
```

`librustc_driver` is larger still, but it is a runtime driver and is *kept* so `RUSTC_LOG` stays in DUE.
