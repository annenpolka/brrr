# whence

Resolve git-style conflict markers (`<<<<<<<` / `=======` / `>>>>>>>`) only by
explicit parent choice, and emit a first-class provenance report naming the
parent of every kept contested span.

zsh already has a builtin named `whence`. Run this tool as `./whence` or
`python3 whence`.

## Why

`git checkout --ours` / `--theirs` and `git mergetool` produce a new blob and
forget which parent supplied each contested token. `whence` keeps that
parentage next to the resolved text. It does not understand JS or YAML, does
not open a TUI, and will not invent a merge: unmarked mixed text is refused.

## Commands

```text
python3 whence report FILE
python3 whence resolve FILE --ours
python3 whence resolve FILE --theirs
python3 whence resolve FILE --choice ours,theirs,ours
python3 whence resolve FILE --hybrid SIDECAR
python3 whence resolve FILE --hybrid -          # tagged blocks on stdin
cat sidecar.txt | python3 whence resolve FILE --hybrid -
python3 whence resolve FILE --choice ours,hybrid --hybrid SIDECAR
python3 whence resolve FILE --choice ours,hybrid --hybrid -
python3 whence resolve - --ours --output PATH   # conflict on stdin; --output required
```

`resolve` overwrites `FILE` (or `--output PATH`), prints JSON provenance to
stdout, and writes `FILE.prov` unless `--prov PATH` or `--prov -`. `FILE -`
reads the conflict from stdin and requires `--output PATH` (refusing to write
a file named `-`).

`--hybrid -` and `--hybrid SIDECAR` are the same tagged language. FILE and
`--hybrid` cannot both be `-` (one stdin). Empty stdin, an empty sidecar file,
and a terminal on `--hybrid -` are usage errors; the conflict file is left
unresolved (no silent `mode: empty`). Provenance records
`"hybrid": {"source": "stdin"}` or `"hybrid": {"source": "file", "path": ...}`.

## Hybrid tags

A hybrid sidecar is the intended replacement for each conflict region, with
every contested span wrapped in a parent tag. The sidecar may be a file or
stdin (`--hybrid -`):

```text
[ours:color = red]
size = [theirs:2]
```

- `[ours:...]` must be a substring of the `<<<<<<<` side, consumed in order.
- `[theirs:...]` must be a substring of the `>>>>>>>` side, consumed in order.
- Untagged text must appear in **both** sides (common text).
- A literal `]` inside a tag is written `\]`. Other backslashes stay
  (`\"` in the file is still `\"` inside a tag; it is not an escape).
- Multiple hybrid regions are separate sidecar blocks split by a `%%` line.
- Stdin CRLF is translated to LF so a DOS pipe matches a Unix sidecar file.
- A leading UTF-8 BOM on stdin or a sidecar file is stripped (Notepad/Windows pipes).
- A missing final newline on stdin is literal: `printf '[theirs:2]'` does not
  invent the common newline that a sidecar file usually ends with.

If you want a whole side, use `--ours` / `--theirs`. Pasting that side into
`--hybrid` without tags is an unmarked mix and fails.

## Demo

```text
./demo.sh
```

Requires `python3` and `git`. The demo covers ours-only, theirs-only, tagged
hybrid from a sidecar file, the same tags on stdin, untagged hybrid failure,
and a real two-branch git merge.

## Tests

```text
python3 -m unittest discover -s tests -v
```

Tests import and subprocess the shipped `./whence` file; they do not reimplement it.
