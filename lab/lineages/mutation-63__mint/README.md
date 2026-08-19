# mint

When a production world **newly acquired a visa**.

`stain` asks whether HEAD currently leaks a machine (CI empty stdout). `mint` asks *when*: held-style occupancy of clearance polarity, **OPEN→BOUND** across revisions.

Default stdout is a report of births — **commit, world, machine**. Not a test file. `--check` fails if this range minted a visa the parent did not have.

## Install / run

Python 3.10+, stdlib only, `git` on PATH. v0.2.

```bash
chmod +x ./mint
./mint --help
./demo.sh
./mint --self-test
```

## Three examples

### 1. This commit minted Alice — birth, exit 1

```bash
./mint -C some-repo <sha-that-pinned-HOME>
# mint  births=1  worlds=1  commit=abc1234  parent=def5678
#   pin Alice home
#   BIRTH  SPEC→BOUND  HOME=/Users/alice USER=alice platform=Darwin
#     load_profile  load_profile("/Users/alice")  src/profile.py
#     was  SPEC  load_profile("/tmp/cache")  src/profile.py
```

`/tmp` is payload (SPEC), not a machine. A portable string (`nick("desktop")`) becoming a home is `OPEN→BOUND`. Root commits with Alice already pinned are `ABSENT→BOUND`.

Brave in the same Swift file is OPEN and does not appear. A textbook `/home/user` is SPEC, not a visa. File-level `macOS` comments are not a world.

`--check` is the default. CI can `./mint -C . origin/main..HEAD`.

### 2. Clean range — empty, exit 0

sitbone never recorded a machine in production. Walking recent first-parent commits stays silent:

```bash
./mint -C ~/ghq/github.com/annenpolka/sitbone
# (no stdout)
# exit 0
```

Pre-existing Alice in another file is not a mint. Spreading the same visa into a new call is `--spread` (exit 0): the parent already had that machine.

### 3. Occupancy of a range, not leftover names

```bash
./mint --walk --max 20 -C . HEAD
./mint --porcelain origin/main..HEAD
./mint --json --check abc123
```

| code | meaning |
| --- | --- |
| 0 | this range minted no visa (or only SPREAD) |
| 1 | a production world became BOUND to a machine the parent did not have |
| 2 | usage / not a git repo |

No `--emit`. Tests are stain/admit's projection; mint's object is the birth.
