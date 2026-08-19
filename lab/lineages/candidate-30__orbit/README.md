# orbit

The effective world of *this* binary, as a dumpable and diffable object.

`which` names a path. `otool -L` / `ldd` lists libraries of a path. `env` dumps the shell. None of them answer the daily question: **when I type this name, which image actually runs, what will *this copy* load, which env vars does that image name, and which of those the kernel will silently strip?**

The object is an **orbit**. The guise on PATH is not the payload.

## Install / run

```bash
chmod +x ./orbit
./orbit --help
./demo.sh
```

Python 3.10+, stdlib only. Uses `otool`, `codesign`, `file`, `xcrun`, `rustup` when present.

Exit: dump `0` (or `1` if the name is missing). diff `0` same orbit, `1` different, `2` tool error.

## Interaction

```
orbit python3                         # dump this python
orbit diff python3 /usr/bin/python3   # two names, two worlds
orbit --env RUSTUP_TOOLCHAIN=1.70.0 dump cargo
orbit --porcelain cargo | grep payload
orbit paths python3                   # every PATH hit
orbit --json node > /tmp/node.orbit
orbit diff /tmp/node.orbit /tmp/copy.orbit
```

`--path` changes how the *name* is bound. `--env KEY=VAL` overlays the world the image is scored against (empty VAL unsets). `--no-proxy` stops at the guise (do not follow rustup / xcselect / shebang).

## Examples

**1. `python3` is not `/usr/bin/python3`.** Homebrew wins PATH; the Xcode shim is an xcselect proxy onto Python 3.9. `orbit diff` says so in one shot.

```bash
./orbit diff python3 /usr/bin/python3
# payload  cellar/python3.14   vs   Xcode python3.9
# proxy    -                   vs   xcselect
```

**2. `cargo` is rustup in a hat.** The file at `~/.cargo/bin/cargo` *is* rustup. The payload is a toolchain binary, and `RUSTUP_TOOLCHAIN` / cwd `rust-toolchain.toml` pick which one.

```bash
./orbit dump cargo
# guise    ~/.cargo/bin/rustup
# payload  ~/.rustup/toolchains/stable-…/bin/cargo
# proxy    rustup
```

**3. Copying `node` is not `node`.** Homebrew's node is a 68k stub with `@rpath/libnode`. The rpath is `@loader_path`. `cp $(which node) /tmp/node` produces a binary whose orbit is missing libnode — same bytes, different world.

```bash
./orbit dump node                 # libnode resolved next to the cellar stub
cp "$(which node)" /tmp/node
./orbit dump /tmp/node            # MISSING @rpath/libnode.147.dylib
```
