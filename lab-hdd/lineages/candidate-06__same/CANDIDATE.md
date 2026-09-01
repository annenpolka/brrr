# candidate-06 — same

origin:
  method: hdd
  trial: hdd-ident

## Primitive

Compare two local names under exactly one explicit identity kind (`inode`, `bytes`, or canonical JSON) and refuse if the kind is omitted or mixed.

## Why this might not exist

`stat`, `cmp`, and `jq -S` each implement one identity, and callers mix them by habit. Nothing forces the kind to be named, so “are these the same file?” silently means inode, bytes, or JSON depending on who typed the pipeline.

## How to run

From the worktree root (`$HOME/.grok/worktrees/annenpolka-brrr/candidate-06-same`):

```bash
./same --inode A B
./same --bytes A B
./same --json A B
./demo.sh
python3 -m unittest tests.test_same -v
```

## Reality assessment (pre-implementation)

Copied from harvest before code:

- Classification: USEFUL_COMPOSITION
- Nearest: stat; cmp; jq -S
- Delta: identity kind is a required argument
- Mapping: os.stat st_ino; file bytes comparison or hashlib; json.dumps(sort_keys=True) after json.load
- Full copy: `REALITY.md`

`--inode` uses `os.lstat` so a symlink and its target are DISTINCT. `--bytes` follows symlinks for content.

## Empirical transcript

### First working commit (`00d95cb`)

`python3 -m unittest tests.test_same -v`: 11 tests, OK. `./demo.sh` (paths abbreviated):

```
== omit-kind failure ==
usage: same --inode|--bytes|--json A B
available kinds: inode, bytes, json
exit 1

== inode hardlink identical ==
IDENTICAL inode 16777233:128975122
exit 0

== inode two empties distinct ==
DISTINCT inode 16777233:128975119 16777233:128975120
exit 2

== bytes two empties identical ==
IDENTICAL bytes sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
exit 0

== json key order identical ==
IDENTICAL json {"a":2,"b":1}
exit 0

== bytes symlink follows ==
IDENTICAL bytes sha256:5891b5b522d5df086d0ff0b110fbd9d21bb4fc7163af34d08286a2e846f6be03
exit 0
```

Dogfood on that same commit (real runs, exit 1, interpreter traceback):

```
$ git rev-parse --short HEAD
00d95cb

$ ./same --bytes fixtures/empty/a fixtures/no-such
FileNotFoundError: [Errno 2] No such file or directory: 'fixtures/no-such'
exit 1

$ ./same --json fixtures/binary.bin fixtures/json/order-ab.json
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 6: invalid start byte
exit 1
```

### After dogfood

Named-path errors, no traceback. `python3 -m unittest tests.test_same -v`: 13 tests, OK.

```
$ ./same --bytes fixtures/empty/a fixtures/no-such
same: .../fixtures/no-such: No such file or directory
exit 1

$ ./same --json fixtures/binary.bin fixtures/json/order-ab.json
same: .../fixtures/binary.bin: not JSON (not UTF-8 text)
exit 1
```

## Dogfood targets

Done in the second commit:

- Missing path is a one-line `same: PATH: No such file or directory`.
- `--json` on binary (`hello\x00\xffworld`) is `same: PATH: not JSON (not UTF-8 text)`.

## Surprises

- Two empty files that `cmp` would call equal are DISTINCT under `--inode` on this volume (`16777233:128975119` vs `16777233:128975120`). That is the whole point of requiring the kind.
- SHA-256 of the empty file matched the known digest `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
- `json.dumps(..., sort_keys=True, separators=(",", ":"))` collapsed `{"b": 1, "a": 2}` and `{"a": 2, "b": 1}` to `{"a":2,"b":1}`.

## Failures

- Git does not preserve hard links; `demo.sh` / tests recreate `fixtures/hardlink/b` with `ln` / `os.link`.
- `--json` still follows the path `open()` follows; a symlink to JSON is compared as JSON, not as a symlink object. That is only surprising if you expected `--json` to lstat like `--inode`.

## Suggested mutations

- `--inode` vs `--bytes` vs `--json` table for N paths, still one kind.
- Refuse `--json` on a symlink unless `--bytes`-style follow is named.
- Canonical JSON with `parse_float=decimal.Decimal` so `1.0` and `1` stay distinct on purpose.

## Kill / keep

Keep while the required kind stays the interaction. Kill if it becomes a flag soup around `cmp`.
