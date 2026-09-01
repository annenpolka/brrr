# CANDIDATE: whence

origin:
  method: hdd
  trial: hdd-merge

## Reality assessment (pre-implementation, preserved)

Classification: USEFUL_COMPOSITION

Core operation: resolve conflict markers by explicit parent tags and report
which parent kept each contested span.

Nearest existing operation: git mergetool / editing `<<<<<<<` markers /
`git checkout --ours/--theirs` / `git merge-file --ours|--theirs`.

Observable delta: ordinary merge tools produce a new blob and forget which
parent supplied each contested token. This keeps per-span parent provenance.

Removed magic: semantic JS/YAML understanding, TUI, hidden AI merge.

Research boundary: not semantic merge, not binaries, not more than two
parents (diff3 `|||||||` ancestor markers are refused).

## Primitive

A one-shot CLI that parses `<<<<<<<` / `=======` / `>>>>>>>` regions, accepts
only an explicit parent choice per region (`--ours`, `--theirs`, `--choice`)
or per tagged span (`[ours:...]` / `[theirs:...]`), writes the resolved text,
and writes a JSON provenance list of every kept contested span. Untagged
mixed text is refused with a nonzero exit.

## Why this might not exist

Taking ours or theirs is already `git checkout --ours` and `git merge-file`.
What is missing is a merge product that still says, for each contested span,
which parent it came from — including a hybrid that is illegal unless every
non-common span is tagged. Editors and mergetools treat parentage as
scaffolding to throw away.

## How to run

zsh has a builtin `whence`. Use `./whence` or `python3 whence`.

```text
python3 whence report fixtures/simple.conflict
python3 whence resolve copy.conflict --ours
python3 whence resolve copy.conflict --theirs
python3 whence resolve copy.conflict --hybrid fixtures/hybrid-tagged.txt
python3 whence resolve copy.conflict --hybrid fixtures/untagged-mix.txt  # fails
./demo.sh
python3 -m unittest discover -s tests -v
```

Python 3 stdlib only. `./demo.sh` also needs `git`.

## Empirical transcript

Captured from a real `./demo.sh` on 2026-09-01. Full output: `demo-transcript.txt`.
zsh builtin `whence` is not used; commands are `python3 ./whence`.

### ours-only

```text
$ python3 ./whence resolve simple.conflict --ours
```

Resolved file:

```text
# palette
color = red
size = 1
# end
```

Provenance (stdout and `simple.conflict.prov`):

```json
{
  "tool": "whence",
  "region_count": 1,
  "trailing_newline": true,
  "input_trailing_newline": true,
  "regions": [
    {
      "index": 1,
      "lines": [2, 8],
      "ours_label": "HEAD",
      "theirs_label": "feature",
      "mode": "ours",
      "spans": [{"parent": "ours", "text": "color = red\nsize = 1\n"}]
    }
  ]
}
```

### theirs-only

Resolved file:

```text
# palette
color = blue
size = 2
# end
```

mode `theirs`, span parent `theirs`, text `color = blue\nsize = 2\n`.

### hybrid tagged success

```text
$ python3 ./whence resolve hybrid.conflict --hybrid fixtures/hybrid-tagged.txt
```

Resolved:

```text
# palette
color = red
size = 2
# end
```

spans: `ours` `"color = red"`, `theirs` `"2"`.

### untagged hybrid failure

```text
$ python3 ./whence resolve untagged.conflict --hybrid fixtures/untagged-mix.txt
region 1/1 lines 2-8 (HEAD vs feature): untagged text "color = red\nsize = 2\n" is not a substring of ours or theirs (unmarked mix or invented text). Tag each contested span [ours:...] or [theirs:...].
  ours (HEAD):
    color = red
    size = 1
  theirs (feature):
    color = blue
    size = 2
exit=1
```

Conflict markers remain in the file. No `.prov` is written.

### nearest existing

```text
$ git merge-file -p --ours ours.txt base.txt theirs.txt
color = red
size = 1
```

git wrote a blob and stopped; no per-span parent list.

### real two-branch git merge

A throwaway repo with overlapping edits to `config.txt` (`value = 1` vs `value = 2`)
produced two-parent markers after `merge.conflictStyle=merge`. `whence resolve
--ours` kept `value = 1\n` and recorded `mode: ours`. This environment's default
style is diff3; without the local config, git emitted `|||||||` and whence
refused (see Failures).

18 unittest cases against the shipped `./whence` file: OK.

## Dogfood

After the first working commit (`e755291`, simple one-region fixtures),
`fixtures/messy.conflict` was run for real: three regions, nested `\"` quotes,
and no trailing newline.

Observed before the second commit:

1. `[ours:name = "Bob \"staff\""]` was reported as not in *either* parent.
   The tag parser treated every `\X` as an escape, so `\"` became `"`.
   The file's real bytes are backslash-quote. Only `\]` and `\\` are now
   escapes.
2. Untagged-mix errors used `snippet()` then `!r`, so the demo printed
   `'color = red\\nsize = 2\\n'` (double-escaped). Errors now use one JSON
   encode and print both parent bodies.
3. A two-block sidecar for a three-region file said "2 blocks but 3 hybrid
   regions" without saying *which* region lacked a block. It now lists
   `region 3/3 ... MISSING tagged block`.
4. Provenance now records `trailing_newline` / `input_trailing_newline`.
   The messy resolve keeps `# eof` without a final NL (xxd tail: `23 2065 6f66`).

Successful messy hybrid (ours name + theirs role, theirs timeout, ours debug)
is in `demo-transcript.txt` and `tests/test_whence.py`.

## Surprises

- zsh's `whence` builtin means a bare `whence resolve` never runs this tool.
- `--hybrid` of an untagged exact ours side is refused: whole-side choice is
  `--ours`, not an implicit hybrid.
- `git merge-file --ours` already implements whole-hunk ours/theirs/union and
  emits no parentage.
- This machine's git writes diff3 `|||||||` markers unless the repo overrides
  `merge.conflictStyle`. That is a third hunk, not a second parent, and is
  refused on purpose.
- Nested quotes in source (`\"`) look like escapes but are file content.

## Failures

- No git mergetool driver wiring.
- Span matching is ordered substring, not a token LCS / syntax tree.
- Two parents only; octopus and diff3 base hunks are refused.
- Binaries and non-UTF-8 files are refused.
- A `]` inside tagged text must be escaped as `\]`.
- Untagged mixed text is diagnosed as "not a substring of either parent"
  rather than token-split into the two contributing sides.

## Suggested mutations

- git mergetool / `merge` driver that writes `.prov` beside the worktree file.
- Record provenance in a git note instead of a sidecar.
- Align hybrid text with `difflib.SequenceMatcher` and propose tags.
- Optionally strip a diff3 ancestor hunk and still track only ours/theirs.
- Allow `--choice` values as a sidecar JSON of per-region decisions.

## Kill/keep

KEEP. The composition is small and the delta is observable: same marker parse
as every mergetool, plus a refuse-unmarked-mix contract and a per-span
parentage report that `git merge-file` does not produce.
