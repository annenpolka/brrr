# stain

CI: **production leaked no machine**.

`hatch` writes the tests production already inhabits. `visa` writes the skip an oracle demands. `admit` fuses them into a clearance and **prints a test file**. Even `admit --check --bound` on a clean tree emits a pytest stub.

`stain` is that check with the generator turned off. Default grain is BOUND due worlds only. Empty stdout and exit 0 means no HOME/USER/platform/CI literal stained production. OPEN Brave and dyn timeouts are not a stain. Tests are `--emit`.

## Install / run

Python 3.10+, stdlib only. v0.2.

```bash
chmod +x ./stain
./stain --help
./demo.sh
./stain --self-test
```

## Three examples

### 1. Clean tree — empty, exit 0

sitbone's untested browser names are not a machine:

```bash
./stain -C ~/ghq/github.com/annenpolka/sitbone
# (no stdout)
# exit 0
```

`--check --bound` is the default. CI can `./stain -C .`.

### 2. Alice's home stained production — debt, exit 1

```bash
./stain -C fixtures/ugly
# stain  machines=1  worlds=3  miss=1
#   MISS  BOUND  HOME=/Users/alice USER=alice platform=Darwin
#     load_profile  load_profile("/Users/alice")  src/profile.py:12
#     load_profile  load_profile("/Users/alice/Library")  src/profile.py:13
#     loadHome  loadHome("/Users/alice/Library/sitbone")  src/App.swift:32
```

Brave in the same Swift file is OPEN and does not appear. File-level `macOS` comments are not a world.

A hatch-style `assert load_profile("/Users/alice")` would fail on this host. stain fails *before* that, because the leak exists.

This host's own `$HOME` in production is also a stain (`MATCH`). CI does not care that the laptop holds the visa.

### 3. Tests are opt-in

```bash
./stain --emit -C fixtures/ugly isBrowser
# import XCTest
# XCTAssertTrue(…isBrowser("Brave Browser"))   # visa OPEN, no skip
```

| code | meaning |
| --- | --- |
| 0 | no machine-tied debt (or `--emit` wrote tests) |
| 1 | production leaked a machine (or `--due` found any due world) |
| 2 | usage / IO error |
