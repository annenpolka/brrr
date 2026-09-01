# CANDIDATE: mutation-03 — whence-stdin

```yaml
origin:
  method: hdd
  trial: hdd-merge
  mutation: ordinary
  parent: candidate-01__whence
```

## Primitive

Resolve `<<<<<<<` / `=======` / `>>>>>>>` regions by explicit parent choice
and emit a JSON provenance list of every kept contested span.

Ordinary mutation of candidate-01: `whence resolve FILE --hybrid -` reads
the tagged hybrid sidecar from stdin. `--hybrid PATH` still reads a file.
The tagged language is unchanged (`[ours:...]` / `[theirs:...]`, `%%` between
regions). Provenance records which of those two sources supplied the tags.

Empty stdin, a terminal on `--hybrid -`, and `FILE` plus `--hybrid` both `-`
are usage errors. The conflict file is left unresolved. Parent `--hybrid -`
treated an empty pipe as an empty hybrid and wiped the region (`mode: empty`).

## Why it might not exist

`--ours` / `--theirs` already exist as git checkout. Parent `whence` already
keeps per-span parentage from a sidecar file. What is missing as a pipe
contract is: another process emits tags, whence consumes them, and the
provenance says `stdin` not a path. `cat sidecar | whence resolve FILE --hybrid -`
must match `--hybrid sidecar`. A forgotten pipe must not delete the hunk.

## How to run

```bash
./demo.sh
python3 -m unittest discover -s tests -v
python3 ./whence resolve copy.conflict --hybrid fixtures/hybrid-tagged.txt
cat fixtures/hybrid-tagged.txt | python3 ./whence resolve copy.conflict --hybrid -
python3 ./whence resolve copy.conflict --hybrid - </dev/null   # fails
```

zsh has a builtin `whence`. Use `./whence` or `python3 whence`. Python 3 stdlib.

## Pre-implementation Reality assessment

Copied from the harvest, before the parent implementation existed (still in force):

- Classification: USEFUL_COMPOSITION
- Core operation: resolve conflict markers by explicit parent tags and report
  which parent kept each contested span
- Nearest existing: git mergetool / `git checkout --ours/--theirs` / `git merge-file`
- Observable delta: mergetools produce a new blob and forget which parent
  supplied each contested token
- Removed magic: semantic JS/YAML, TUI, hidden AI merge
- Research boundary: not semantic merge, not binaries, not more than two parents

This mutation adds stdin as a hybrid source. It does not add mergetool wiring,
diff3 ancestors, or token LCS.

## Empirical transcript

Worktree: `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/mutation-03-whence-stdin`

First working mutation commit `e549596`. `python3 -m unittest discover -s tests -v`: 24 tests, OK. After dogfood: 28 tests, OK.

```text
$ python3 -m unittest discover -s tests -v
Ran 28 tests in 0.984s
OK
```

`./demo.sh` exit 0. File sidecar and stdin hybrid on `simple.conflict` both
resolved to:

```text
# palette
color = red
size = 2
# end
```

`cmp` of the two resolved files succeeded. Provenance differs only in source:

```json
"hybrid": {"source": "file", "path": "fixtures/hybrid-tagged.txt"}
```

```json
"hybrid": {"source": "stdin"}
```

`--hybrid - </dev/null` exit 3, markers remain. `whence resolve - --hybrid -`
exit 3 (cannot consume stdin twice). Untagged mix still exit 1. 28 unittests
inside the demo, OK. After dogfood: BOM stdin and generated `print` tags
`cmp` equal to the file sidecar.

## Dogfood

Fed real pipes after the first commit (`e549596`).

UTF-8 BOM (Notepad / some Windows pipes) prepended `\xef\xbb\xbf` to the same
sidecar bytes. Before: untagged text `"﻿"` (U+FEFF), exit 1, markers left.
After: BOM stripped; resolved bytes match the file sidecar.

Python `print("[ours:color = red]"); print("size = [theirs:2]")` piped into
`--hybrid -` matches `--hybrid fixtures/hybrid-tagged.txt` (`cmp` equal).
That is the composition the mutation is for: another process emits tags.

`printf '[ours:color = red]\nsize = [theirs:2]'` (no final newline) succeeds
and concatenates `size = 2` onto `# end` → `size = 2# end`. Honest: the
sidecar file's trailing NL was common text. Do not invent it. Use `cat` or a
heredoc when you want the file sidecar's bytes.

`cat fixtures/messy-hybrid.txt | --hybrid -` matches the three-region file
sidecar (spans and resolved bytes). `--choice hybrid,theirs --hybrid -` on
`two.conflict` with `[ours:one]\n` keeps `one` then `TWO`.

## Surprises

- Parent already accepted `--hybrid -` as a path alias for stdin. It did not
  refuse an empty pipe: `split_hybrid_blocks("")` is one empty block, which
  resolved the hunk to nothing (`mode: empty`) and wrote `.prov`.
- `FILE - --hybrid -` consumed the conflict as FILE and treated leftover
  stdin as an empty hybrid, then `atomic_write("-", ...)` could create a
  file named `-`.
- Python 3 on this machine keeps `\r\n` on `sys.stdin.read()` for a pipe.
  Stdin hybrid now translates CRLF to LF so a DOS pipe matches a Unix sidecar.
- A UTF-8 BOM on the pipe was untagged text `"﻿"`, not a decode error.
- `printf` without a final newline is not `cat sidecar.txt`; the sidecar's
  trailing NL is common text and is not implied by EOF.

## Failures

- Still no git mergetool driver.
- Still substring tags, two parents, no binaries.
- FILE `-` with a *file* sidecar still writes resolved text to a file named
  `-` unless `--output` is given (not this mutation).
- An empty *file* sidecar still wipes the region (parent behavior; only the
  stdin forgotten-pipe case is refused).
- Extra blank lines after the tags are untagged text and fail (not trimmed).

## Suggested mutations

- Require `--output` when FILE is `-`.
- Optionally refuse an empty file sidecar the same way as empty stdin.
- git mergetool driver that writes `.prov`.
- Align untagged mix with `difflib.SequenceMatcher` and propose tags.
