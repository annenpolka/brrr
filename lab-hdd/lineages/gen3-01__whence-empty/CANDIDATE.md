# CANDIDATE: gen3-01 — whence-empty

```yaml
origin:
  method: hdd
  trial: hdd-merge
  mutation: gen3-fix
  parent: mutation-03__whence-stdin
```

## Primitive

Resolve `<<<<<<<` / `=======` / `>>>>>>>` regions by explicit parent choice
and emit a JSON provenance list of every kept contested span.

Gen-3 FIX of mutation-03 (best stdin peel of candidate-01). Parent already
refuses empty `--hybrid -`. An empty *file* sidecar still resolved the hunk
to nothing and wrote `"mode": "empty"`. This embodiment refuses empty hybrid
from any source (stdin, whitespace-only pipe, 0-byte sidecar) with a nonzero
exit and leaves the conflict markers in FILE. It does not invent `mode: empty`
as a successful tagged merge.

## Why it might not exist

`--ours` / `--theirs` already exist as git checkout. Parent `whence` already
keeps per-span parentage and already refuses a forgotten pipe. What is still
missing is the same refuse for a forgotten empty sidecar file: `touch empty &&
whence resolve FILE --hybrid empty` must not delete the hunk. A tagged hybrid
that is empty is not a merge.

## How to run

```bash
./demo.sh
python3 -m unittest discover -s tests -v
python3 ./whence resolve copy.conflict --hybrid fixtures/hybrid-tagged.txt
cat fixtures/hybrid-tagged.txt | python3 ./whence resolve copy.conflict --hybrid -
python3 ./whence resolve copy.conflict --hybrid - </dev/null   # fails, markers stay
python3 ./whence resolve copy.conflict --hybrid empty-file     # fails, markers stay
printf '<<<<<<< HEAD\nx\n=======\ny\n>>>>>>> feature\n' | python3 ./whence resolve - --ours --prov -  # fails
printf '<<<<<<< HEAD\nx\n=======\ny\n>>>>>>> feature\n' | python3 ./whence resolve - --ours --output out.txt --prov -
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

This FIX closes the empty-hybrid hole DESTROYER_WHENCE named. It does not add
mergetool wiring, unique-vs-shared provenance, or skip-middle coverage.

## Empirical transcript

Worktree: `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/gen3-01-whence-empty`

First working commit refused empty hybrid (stdin and sidecar). After dogfood
(FILE `-` requires `--output`):

```text
$ python3 -m unittest discover -s tests -v
Ran 31 tests in 1.199s
OK
```

`./demo.sh` exit 0. Empty stdin (`--hybrid -` with `""`, `"\n"`, `"  \n\n"`)
exit 3, markers remain, no `.prov`, no `"mode": "empty"`. Empty file sidecar,
same. Tagged hybrid still resolves `simple.conflict` to:

```text
# palette
color = red
size = 2
# end
```

## Dogfood

After the first working commit (`b6f9eca`). DESTROYER_WHENCE §4: `FILE=-`
without `--output` writes a file named `-`.

Before, in a throwaway cwd:

```text
$ printf '<<<<<<< HEAD\nx\n=======\ny\n>>>>>>> feature\n' \
    | python3 whence resolve - --ours --prov -
exit=0
created file named '-': True
content: 'x\n'
```

`--prov -` skipped the sidecar; `atomic_write("-", ...)` still created `-`.

After: the same command is exit 3, stderr `FILE is '-' (stdin); pass --output
PATH`, no file named `-`. With `--output PATH` the blob is `x\n` and cwd has
no `-`.

## Surprises

- Parent `split_hybrid_blocks("")` is one empty block, which `apply_hybrid`
  treated as a successful empty resolve (`mode: empty`) and overwrote FILE.
- Whitespace-only sidecars (`"\n"`, `"  \n\n"`) are the same wipe as 0 bytes:
  `str.strip()` is the emptiness test, matching parent stdin.
- A hybrid block that applies to no spans and no text is also refused, so a
  `%%` empty region cannot delete a hunk either.
- `FILE=- --prov -` looks like a filter (stdin in, JSON out) and still writes
  a file named `-` unless `--output` is required. `--prov -` only skips the
  sidecar.

## Failures

- Still no git mergetool driver.
- Still substring tags, two parents, no binaries.
- BOM on the conflict FILE is still not stripped (hybrid sidecar BOM is).
- `--prov DIRECTORY` can still mutate FILE then error.

## Suggested mutations

- Strip a leading UTF-8 BOM on FILE the same way as hybrid stdin.
- Write resolved + `.prov` as one transaction; refuse a directory dest first.
- Record whether a tagged span was unique to that parent or also in the other.
