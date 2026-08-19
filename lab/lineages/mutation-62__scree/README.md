# scree

Emit the **largest production subset the current tests do not lock**.

cinch and tock emit the 1-minimal production hunks the tests *veto* (wheat).
**scree** inverts the object: chaff. Tests stay at NEW. They are the lock,
never unlocked. The predicate is pass/fail of that suite, not a command
fingerprint, and not `alibi`.

A hunk is unlocked only after we **observe a passing trial with it dropped**.
A timeout is unknown: never locked, never unlocked. An empty suite is
`EMPTY`, not a giant unlocked set.

## Install / run

Python 3.10+, git. No third-party packages.

```bash
chmod +x ./scree
./scree --help
./demo.sh
./scree -- python3 -m unittest discover -s tests -q
./scree --format patch -- python3 test.py
./scree --timeout 0.5 -- python3 test.py
```

The user worktree is never rewritten. Each trial is a temp tree: tests@NEW,
production reconstructed from a hunk subset.

## Three examples

### 1. Mixed WIP: fix + debug print + new tests + README

```bash
./scree -- python3 test.py
```

```
scree  base=HEAD  status=SLACK  trials=4
unlocked (1):  modify app.py  #1   print("debug")
locked   (1):  modify app.py  #2   return a + b
```

`--format patch` is the *unlocked* extra (the print), not the return.

### 2. Joint lock + unused file

`a.py` and `b.py` are required together; `c.py` is noise.

```bash
./scree --format paths -- python3 test.py
# c.py
```

cinch `--format paths` prints `a.py` and `b.py`. Complements.

### 3. FAST+VALUE under a tight `--timeout`

Production flips `FAST=False`→`True` and `VALUE=0`→`1`. Tests sleep unless
`FAST`, then `assert VALUE==1`. Dropping `FAST` times out. Dropping `VALUE`
fails the assertion.

```
status TIGHT  unlocked=[]  locked=['app.py#2']  unknown=['app.py#1']
```

FAST is not slack. We never observed a pass without it. `--format patch`
is empty. cinch 0.3 wheat is VALUE (budget=FAST). tock wheat is VALUE
(chaff=FAST). scree refuses to call FAST unlocked.

Empty suite (`unittest discover` on no tests) is `EMPTY`, `unlocked=[]`,
not a giant unlocked set.

## Statuses and exit codes

| status        | meaning                                                      | exit |
| ------------- | ------------------------------------------------------------ | ---- |
| `SLACK`       | observed unlocked production                                 | 0    |
| `CLEAN`       | no production unit differs from base; NEW tests passed       | 0    |
| `TIGHT`       | nothing observed-unlocked; every unit is locked or unknown   | 1    |
| `LOOSE`       | tests still pass with every production hunk reverted         | 2    |
| `BROKEN`      | tests already fail or time out on the new tree               | 3    |
| `UNBUILDABLE` | no production subset makes the tests load                    | 4    |
| `EMPTY`       | test command collected no tests (not a giant unlocked set)   | 5    |
| `TIMEOUT`     | a drop timed out; timeout is not locked and not unlocked     | 6    |
