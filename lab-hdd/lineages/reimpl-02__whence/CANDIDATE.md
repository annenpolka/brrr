# CANDIDATE: whence (reimpl-02)

```yaml
origin:
  method: hdd
  trial: hdd-merge
  kind: clean-room
  parent: candidate-01__whence
```

## Primitive

Parse `<<<<<<<` / `=======` / `>>>>>>>` regions. Replace each region only by
an explicit parent (`--ours`, `--theirs`, per-region `--choice`, or tagged
`[ours:...]` / `[theirs:...]` hybrid). Write the resolved text and a JSON
provenance list of every kept contested span. Untagged mixed text is refused
with a nonzero exit; conflict markers stay in the file.

## Why this might not exist

Taking ours or theirs is already `git checkout --ours` and `git merge-file`.
What is missing is a merge product that still says, for each contested span,
which parent it came from — including a hybrid that is illegal unless every
non-common span is tagged. Editors and mergetools treat parentage as
scaffolding to throw away.

## Pre-implementation Reality assessment

Copied from `lab-hdd/hdd-origins/hdd-merge.md` before this implementation
existed:

- Classification: USEFUL_COMPOSITION
- Core operation: resolve conflict markers by explicit parent tags and report
  which parent kept each contested span
- Nearest existing: git mergetool / editing `<<<<<<<` markers /
  `git checkout --ours/--theirs` / `git merge-file --ours|--theirs`
- Observable delta: ordinary merge tools produce a new blob and forget which
  parent supplied each contested token. This keeps per-span parent provenance
- Removed magic: semantic JS/YAML understanding, TUI, hidden AI merge
- Research boundary: not semantic merge, not binaries, not more than two
  parents (diff3 `|||||||` ancestor markers are refused)

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

First working commit, 2026-09-02. Independent code. Tests and fixtures copied
from `candidate-01__whence`; the CLI file was not.

Command: `python3 -m unittest discover -s tests -v`

```
Ran 18 tests in 0.574s
OK
```

After the dogfood commit: 20 tests, OK. `./demo.sh` exit 0.

Command: `./demo.sh` → exit 0.

### ours-only

Resolved file:

```text
# palette
color = red
size = 1
# end
```

Provenance: `mode: ours`, span parent `ours`, text `color = red\nsize = 1\n`.

### theirs-only

`mode: theirs`, span `color = blue\nsize = 2\n`.

### hybrid tagged success

`--hybrid fixtures/hybrid-tagged.txt` kept ours `color = red` and theirs `2`.

### untagged hybrid failure

exit 1. `untagged text "color = red\nsize = 2\n" is not a substring of ours
or theirs (unmarked mix or invented text)`. Markers left in the file. No
`.prov`.

### diff3

exit 2. `diff3 ancestor marker (|||||||) … whence tracks two parents only`.

### nearest existing

`git merge-file -p --ours` printed `color = red\nsize = 1\n` and stopped; no
per-span parent list.

### real two-branch git merge

Throwaway repo, `merge.conflictStyle=merge`, overlapping `value = 1` vs
`value = 2`. `whence resolve --ours` kept `value = 1\n` and recorded
`mode: ours`.

### messy three-region hybrid

Short sidecar named `region 3/3 … MISSING tagged block`. Wrong-parent quoted
name pointed at theirs. Successful hybrid left `# eof` with no trailing
newline (`xxd` tail `23 2065 6f66`).

SHA-256 of this CLI differs from `candidate-01__whence/whence`.

## Dogfood

After the first working commit (`e070166`), a live two-parent merge of
one-line JSON objects was tagged as a whole ours blob:

```text
[ours:{"items": ["a", "b"], "n": 1}]
```

**Before:** the first `]` (end of the array) closed the tag. Inner text
`{"items": ["a", "b"` matched ours, leftover `, "n": 1}]\n` was unmarked
mix, exit 1, markers left in the file. `\]` still worked; wrapping the
object the way a person writes a JSON merge did not.

**Change:** close `[ours:...]` / `[theirs:...]` at the longest unescaped
`]` whose inner text is a substring of the remaining named parent. The
first `]` is still used when no later closer matches (wrong-parent and
unclosed errors unchanged). `\]` still inserts a literal `]`.

**After:** the same sidecar resolves to `{"items": ["a", "b"], "n": 1}\n`
with span parent `ours`. Mixed sidecar `items` from ours and `n` from
theirs also works. Fixtures `json-array.conflict` /
`json-array-hybrid.txt` / `json-array-mixed.txt`.

## Surprises

- zsh's `whence` builtin means a bare `whence resolve` never runs this tool.
- `--hybrid` of an untagged exact ours side is refused: whole-side choice is
  `--ours`, not an implicit hybrid.
- `git merge-file --ours` already implements whole-hunk ours/theirs and emits
  no parentage.
- Nested quotes in source (`\"`) look like escapes but are file content.

## Failures

- No git mergetool driver wiring.
- Span matching is ordered substring, not a token LCS / syntax tree.
- Two parents only; octopus and diff3 base hunks are refused.
- Binaries and non-UTF-8 files are refused.
- A `]` inside tagged text is taken as the longest closer that still matches
  the named parent; `\]` remains the explicit escape when that rule is wrong.

## Suggested mutations

- git mergetool / `merge` driver that writes `.prov` beside the worktree file.
- Record provenance in a git note instead of a sidecar.
- Align hybrid text with `difflib.SequenceMatcher` and propose tags.
- Optionally strip a diff3 ancestor hunk and still track only ours/theirs.
