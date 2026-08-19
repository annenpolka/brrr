# visa

Emit the **machine condition** a test oracle implies.

`lees` subtracts the live env/host dictionary from an oracle so two transcripts compare modulo substitution. `visa` is the unary flip: one oracle in, a skip/apply predicate out. The snapshot that recorded `/Users/alice` on Darwin is not a failing test on a GitHub runner — it is a visa the runner does not hold.

## Install / run

Python 3.10+, stdlib only.

```bash
chmod +x ./visa
./visa --help
./demo.sh
./visa --self-test
```

## Three examples

### 1. What machine does this golden demand?

```bash
./visa tests/snapshots/cli.snap
# visa  tests/snapshots/cli.snap  BOUND
#   require  platform=Darwin
#   require  HOME=/Users/alice
#   require  USER=alice
#   apply    [ "$(uname -s)" = Darwin ] && [ "${HOME}" = /Users/alice ]
```

OPEN means portable (apply anywhere). BOUND is a skip unless the host matches. SPEC means machine-shaped strings are the spec of a parser/quoter, not a skip. UNSAT means a *snapshot* contradicts itself as a single machine.

### 2. Apply or skip on *this* host

```bash
./visa --apply local.snap; echo $?
# 1   # MISS — you are not alice
./visa --apply portable.snap; echo $?
# 0   # OPEN
./visa --emit pytest local.snap
# not (sys.platform == 'darwin' and pathlib.Path.home().as_posix() == '/Users/alice')
./visa --emit gha ci.snap
# ubuntu-latest
```

`--emit shell` is the apply predicate (true → run). `--emit pytest` is skipif polarity (true → skip). `--emit gha` is a coarse `runs-on` projection — a specific HOME cannot be expressed there; the shell/pytest predicate is the real visa.

### 3. Pipe a red test, or scan a repo

```bash
pytest -q | ./visa --from-fail
# visas the *expected* side (the oracle), not the two-transcript comparison

./visa --scan -C /path/to/repo --porcelain
```

`--match` prints MATCH/MISS against the live host without changing the default exit. `--apply` exits 0/1/2 (apply / skip / unsatisfiable).

## Why this is not lees

lees needs a dictionary, then a second transcript, then a residue. visa never subtracts this host: it reads path/platform *shapes* the oracle already contains and names the condition. A GitHub handle in a window-title fixture does not become `USER=you` just because you are logged in.
