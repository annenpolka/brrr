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

See `demo-transcript.txt` for a full captured run. Filled after the first
working execution; updated after dogfood.

## Dogfood

First working commit uses `fixtures/simple.conflict` (one region). After that
commit, a messier fixture (nested quotes, missing newline, three regions) is
run for real and error messages are tightened from those failures.

## Surprises

- zsh's `whence` builtin means a bare `whence resolve` never runs this tool.
- `--hybrid` of an untagged exact ours side is refused: whole-side choice is
  `--ours`, not an implicit hybrid.
- `git merge-file --ours` already implements whole-hunk ours/theirs/union and
  emits no parentage.

## Failures

- No git mergetool driver wiring.
- Span matching is ordered substring, not a token LCS / syntax tree.
- Two parents only; octopus and diff3 base hunks are refused.
- Binaries and non-UTF-8 files are refused.
- A `]` inside tagged text must be escaped as `\]`.

## Suggested mutations

- git mergetool / `merge` driver that writes `.prov` beside the worktree file.
- Record provenance in a git note instead of a sidecar.
- Align hybrid text with `difflib.SequenceMatcher` and propose tags.
- Allow `--choice` values as a sidecar JSON of per-region decisions.

## Kill/keep

KEEP. The composition is small and the delta is observable: same marker parse
as every mergetool, plus a refuse-unmarked-mix contract and a per-span
parentage report that `git merge-file` does not produce.
