# whence

Resolve git-style conflict markers (`<<<<<<<` / `=======` / `>>>>>>>`) only
by an explicit parent, and emit a provenance list naming the parent of every
kept contested span.

zsh already has a builtin named `whence`. Run this tool as `./whence` or
`python3 whence`.

Clean-room reimplementation of the `whence` primitive (behavior + tests, not
the original file).

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
python3 whence resolve FILE --choice ours,hybrid --hybrid SIDECAR
```

`resolve` overwrites `FILE` (or `--output PATH`), prints JSON provenance to
stdout, and writes `FILE.prov` unless `--prov PATH` or `--prov -`.

Exit codes: 0 ok, 1 refuse (unmarked mix / bad tags), 2 parse, 3 usage.

## Hybrid tags

A hybrid sidecar is the intended replacement for each conflict region, with
every contested span wrapped in a parent tag:

```text
[ours:color = red]
size = [theirs:2]
```

- `[ours:...]` must be a substring of the `<<<<<<<` side, consumed in order.
- `[theirs:...]` must be a substring of the `>>>>>>>` side, consumed in order.
- Untagged text must appear in **both** sides (common text).
- A literal `]` inside a tag may be written `\]`. Other backslashes stay
  (`\"` in the file is still `\"` inside a tag; it is not an escape).
  If the tagged span itself contains `]` (JSON arrays, `foo[bar]`), the
  closer is the **longest** unescaped `]` whose inner text is still a
  substring of the named parent, so `[ours:{"items": ["a", "b"]}]` works
  without escaping the array bracket.
- Multiple hybrid regions are separate sidecar blocks split by a `%%` line.

If you want a whole side, use `--ours` / `--theirs`. Pasting that side into
`--hybrid` without tags is an unmarked mix and fails.

## Demo

```text
./demo.sh
```

Requires `python3` and `git`. The demo covers ours-only, theirs-only, tagged
hybrid success, untagged hybrid failure, and a real two-branch git merge.

## Tests

```text
python3 -m unittest discover -s tests -v
```

Tests import and subprocess the shipped `./whence` file; they do not reimplement it.

Copied fixtures cover ours/theirs, tagged hybrid, untagged mix, diff3, and
messy three-region files. `json-array.conflict` is the dogfood case: a JSON
object whose ours side contains `]`, tagged without `\]`.
