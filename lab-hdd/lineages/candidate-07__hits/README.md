# hits

Search a directory tree. Zero matches is a successful empty result, not a failure.

origin.method: hdd
origin.trial: hdd-empty

## Primitive

`hits PATTERN && next` still runs after a legitimate miss. A bad query and an unreadable path are different exits.

## Run

```bash
./hits PATTERN [DIR]
./hits --regex PATTERN [DIR]
./hits --glob '*.txt' PATTERN [DIR]
```

Python 3 stdlib only. DIR defaults to `.`. Recurses files, skips `.git` and files with a NUL in the first 8KiB. Default match is a literal substring. `--glob` uses fnmatch on the relative path or basename.

| result | stdout | exit |
| --- | --- | --- |
| one or more hits | `file:line:text` | 0 |
| zero hits | `0 matches` | 0 |
| usage | stderr | 1 |
| bad `--regex` | stderr | 2 |
| unreadable DIR | stderr | 3 |

## Examples

```bash
./hits needle fixtures/has
# fixtures/has/hello.txt:1:hello needle world
# fixtures/has/nested/more.txt:1:another needle here

./hits needle fixtures/miss && echo still-running
# 0 matches
# still-running

./hits --regex '[' fixtures/has; echo $?
# hits: bad regex: ...
# 2

./hits needle fixtures/mixed
# fixtures/mixed/note.txt:1:text needle in notes
# (blob.bin skipped: NUL in the first 8KiB)
```

## Tests

```bash
python3 -m unittest tests.test_hits -v
./demo.sh
```
