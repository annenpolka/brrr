# candidate-30 — orbit

## Primitive

A command name has an **orbit**: the guise PATH bound, the payload that will actually run (rustup / xcselect / shebang), the libraries *this copy* will load at *this* path, the env vars those images name, and the SIP/hardened-runtime filter that silently drops DYLD_*. Dump it. Diff it.

Not leftover names. Not format inversion. Not `env`. Not `ldd`.

## Four primitives considered

1. **orbit** — environment-diff for *this* binary. **Implemented.**
2. **coin** — promote last N shell commands into a named tested verb. *Discarded:* `fc` + `just` + `script` already occupy the wrapper; the "tested" part is a product, not a new object.
3. **scene** — narrative-split of a commit by identifier-dataflow of hunks. Unusual, parked as a mutation; needs a compile-oracle to be more than `git add -p` with clustering.
4. **whence** — generalized `git config --show-origin` for any CLI. *Discarded:* conventional (`git config --show-origin`, `systemd-analyze cat-config`).

## Why this might not exist

"It works on my machine" is an orbit mismatch. People paste `env` and `which python3`. That is the wrong object:

- `/usr/bin/python3` is an xcselect shim; the payload is Xcode's 3.9.
- `~/.cargo/bin/cargo` *is rustup*; `RUSTUP_TOOLCHAIN` picks the payload.
- Homebrew `node` is a stub whose `@loader_path` rpath makes *this copy* the identity, not the filename `node`.
- `/bin/ls` is platform-signed: `DYLD_PRINT_LIBRARIES=1` is a lie.
- `#!/usr/bin/env python3` runs `/usr/bin/env` first, which is itself restricted, so prefixing `DYLD_*` on a shebang script never reaches the interpreter.

`ldd` does not follow rustup. `otool -L` does not know SIP. `which` does not know xcselect. `env` is the shell's, not the image's.

## How to run

```
./orbit --selftest
./orbit dump python3
./orbit diff python3 /usr/bin/python3
./orbit dump cargo
./orbit dump node
./orbit --env DYLD_PRINT_LIBRARIES=1 dump /bin/ls
./demo.sh
```

## Empirical transcript

### v0.1 (this commit)

Selftest ok. `./demo.sh` 0.

PATH swap of two `tool` scripts is a different orbit (exit 1). Relative shebang `beta → gamma → python3` follows. Missing interpreter warns.

Real binaries (2026-08-20, this machine):

| name | guise | payload | proxy | surprise |
| --- | --- | --- | --- | --- |
| python3 | cellar python3.14 | same | - | `/usr/bin/python3` shadowed |
| /usr/bin/python3 | the shim | Xcode python3.9 | xcselect | payload sign is *unrestricted*; the shim's platform bit is dropped |
| cargo | rustup | stable-aarch64 cargo | rustup | **the point** |
| node | cellar stub | same | - | `@rpath/libnode` resolved; copy to /tmp → MISSING libnode |
| /bin/ls | itself | itself | - | RESTRICTED, DYLD_* STRIP |
| git (brew) | cellar git | same | - | unrestricted, 404 garbage "env" names |
| pip3 | pip3 script | python3.14 | shebang | |
| kizu debug | itself | itself | - | `KIZU_CONFIGXDG_CONFIG_HOMEKIZU_STATE_DIR` glued |

v0.1 failures (the improvement target):

1. `/usr/lib/libSystem.B.dylib` is **MISSING** on every Mach-O. It lives in the dyld shared cache. Verdict lies: "this copy will not load."
2. Env harvest of the *stub* does not see `PYTHONPATH` (it lives in `Python.framework`) or `NODE_*` (it lives in `libnode`, 70MB). python3 named `DARWIN_EXTSN`, `DATA_CONST`, `PYVENV_LAUNCHER__`.
3. cargo named `JID9_`, `R_CD` — Mach-O noise. git named 404 ALL_CAPS macros.
4. `pyvenv.cfg absent` on `/bin/ls` and cargo. Noise.
5. Prefixing `DYLD_PRINT_LIBRARIES=1 ./orbit` does not work: orbit's shebang is `/usr/bin/env`, a restricted binary. Had to `--env`. That is the primitive eating its own tail.
6. `--path A:B` for `tool` replaced PATH, so `#!/usr/bin/env python3` became "not on PATH" and the payload stayed the script.

## Dogfood targets

- `/opt/homebrew/bin/python3` vs `/usr/bin/python3`
- `cargo` / rustup toolchain
- Homebrew `node` stub vs `/tmp` copy
- `/bin/ls` vs Homebrew `git`
- `pip3`
- `kizu` at `/Users/annenpolka/ghq/github.com/annenpolka/kizu/target/debug/kizu`
- fixtures in `fixtures/`

## Surprises

- macOS system dylibs are not files. `is_file("/usr/lib/libSystem.B.dylib")` is false. Every naive `otool -L` wrapper will cry MISSING.
- `DYLD_PRINT_LIBRARIES=1 /usr/bin/python3` is silent; the same var on Xcode's python3.9 *payload* prints loads. The shim is the filter.
- Homebrew node is 68k. The world is `@loader_path/../lib/libnode.147.dylib`.
- The shell `git` is a zsh function; orbit PATH-binds `/opt/homebrew/bin/git`. Functions are outside the binary orbit.

## Failures

See v0.1 list above. The primitive is right; the harvest is looking at the wrong image and calling the shared cache a broken link.

## Suggested mutations

- `orbit --ask` : optionally exec the payload (`python -c 'import sys,os'`, `node -p process.execPath`) and join runtime sys.path / NODE_PATH onto the static orbit.
- cwd-sensitive rustup: `orbit --cwd kizu cargo` vs `orbit --cwd other cargo` when a `rust-toolchain.toml` exists.
- `orbit --via-shell` : ask the user's `$SHELL -i` what `type` says, so zsh functions show up as a guise kind.
- scene (discarded #3) as a later candidate.

## Kill / keep

**Keep.** The object (guise vs payload vs this-copy rpath vs SIP filter) is not `ldd` and not `env`. v0.1 is loud and wrong about shared-cache "missing" and named-env; that is a harvest bug, not a primitive bug.
