# candidate-07 — hits

origin.method: hdd
origin.trial: hdd-empty

## Primitive

Search a tree such that zero hits is success, a bad query is exit 2, and an unreadable path is exit 3.

## Why this might not exist

grep and rg treat "no match" as failure (exit 1). That is right for "assert this exists", and wrong for `set -e` / `cmd && next` when absence is a normal outcome. People write `grep ... || true` and lose the distinction between miss, bad pattern, and I/O error.

## How to run

From the worktree root:

```bash
./hits PATTERN [DIR]
./hits --regex PATTERN [DIR]
./hits --glob '*.txt' PATTERN [DIR]
python3 -m unittest tests.test_hits -v
./demo.sh
```

## Empirical transcript

All commands run in the worktree. Dreamer text is not evidence.

### Working commit (3620fb2)

`python3 -m unittest tests.test_hits -v`: 14 tests, OK.

`./demo.sh` (abridged to observed stdout/stderr and exits):

```
== hit ==
fixtures/has/hello.txt:1:hello needle world
fixtures/has/nested/more.txt:1:another needle here
exit=0

== miss (must be exit 0 so && still runs) ==
0 matches
exit=0
0 matches
still-running

== literal is not regex ==
0 matches
exit=0

== regex hit ==
fixtures/regex/sample.txt:1:needle
exit=0

== bad regex (must be exit 2) ==
hits: bad regex: unterminated character set at position 0
exit=2

== usage (must be exit 1) ==
hits: usage: hits [--regex] PATTERN [DIR]
exit=1

== unreadable DIR (must be exit 3) ==
hits: unreadable directory: /var/folders/t2/89bbgzfj41q22bwkdyr_sgth0000gn/T/hits-unreadable.SjbBIC
exit=3
```

Same miss fixture, grep contrast (real run):

```
$ grep -R needle fixtures/miss; echo exit=$?
exit=1
```

`./hits needle fixtures/miss && echo still-running` stays exit 0.

### Dogfood (before second commit)

Built `fixtures/mixed/note.txt` (text needle) and `fixtures/mixed/blob.bin` (PNG-ish header, NULs, the bytes `needle`). Naive decode treated the binary as a hit:

```
$ ./hits needle fixtures/mixed | cat -v
fixtures/mixed/blob.bin:3:^@^@needle^@�� binary junk
fixtures/mixed/note.txt:1:text needle in notes
exit=0

$ grep -R needle fixtures/mixed | cat -v
fixtures/mixed/note.txt:text needle in notes
Binary file fixtures/mixed/blob.bin matches
```

grep at least *said* it was binary. hits printed a forged text line.

### After skip + --glob

`python3 -m unittest tests.test_hits -v`: 19 tests, OK.

```
$ ./hits needle fixtures/mixed
fixtures/mixed/note.txt:1:text needle in notes
exit=0

$ ./hits --glob '*.txt' needle fixtures/mixed
fixtures/mixed/note.txt:1:text needle in notes
exit=0

$ ./hits --glob '*.md' needle fixtures/mixed && echo still-running
0 matches
still-running
```

A tree whose only "match" is inside a NUL file is still empty success (exit 0, `0 matches`), not I/O failure.

## Dogfood targets

- `fixtures/has` (needle present)
- `fixtures/miss` (needle absent)
- `fixtures/regex` (literal vs `--regex`)
- `fixtures/mixed` (text + NUL binary)
- temporary unreadable directory via `chmod 000`
- temporary tree with a `.git/` that contains the needle
- temporary tree of only a binary containing the needle

## Surprises

- UTF-8 `errors=replace` turns a PNG-with-needle into a plausible `file:line:text` hit. The interesting bug is not a crash; it is a fake line of source.
- Empty glob (no path matches) is the same success path as "searched files, none contained PATTERN". That is consistent with the primitive and easy to miss in the UI (`0 matches` does not say *why*).

## Failures

- Unreadable *nested* files are skipped, not exit 3. Exit 3 is the root DIR only. A tree you cannot fully read can still report `0 matches` / exit 0.
- `--glob` is fnmatch, not gitignore. `**/*.txt` is not recursive in the gitignore sense; `*.txt` matches any basename via the extra name check.
- No `-i`, no context lines, no follow-symlink-to-file.

## Suggested mutations

- Quiet empty: print nothing on miss, still exit 0
- Count on stderr (`N matches`) so scripts can tell miss from glob-miss without parsing
- Treat nested EACCES as a distinct warning on stderr without failing the search
- `--glob` gitignore semantics

## Kill / keep

Keep if `hits PAT && next` after a miss is something you would actually type instead of `grep ... || true`. Kill if the only delta is exit 0 and nobody composes on it.

## Reality

See `REALITY.md` (pre-implementation assessment). Classification: USEFUL_COMPOSITION.
