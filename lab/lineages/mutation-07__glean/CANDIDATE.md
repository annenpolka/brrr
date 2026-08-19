# mutation-07 — glean

## Primitive

Given a command, partition the uncommitted working tree into the 1-minimal **file** set that reproduces the command's current behavior (wheat) and the rest (chaff). Untracked files are first-class units. Never hunks.

This is `git bisect` for dirty files, not for commits, not for hunks.

## Why this might not exist

`winnow` (candidate-15) delta-debugs **hunks**. That is slower, more fragile (patch apply), and the chaff is not something you can `git restore` / `rm`. The recurring question is coarser: "which of these 12 dirty files (including the new one I have not even `git add`ed) made the test red?" File grain is the Unix verb you can actually act on.

## How to run

From this worktree root:

```bash
./demo.sh
./dogfood.sh
./glean --help
./glean -C /path/to/repo --format text -v -- python3 test.py
./glean --format paths -- pytest tests/test_foo.py
./glean --format drop -- pytest tests/test_foo.py
./glean --drop -- pytest tests/test_foo.py
```

Python 3.9+ and `git`. No other deps. The index is never touched; WIP is restored on exit and on SIGINT.

## Empirical transcript

### v1 (file grain + untracked)

`./demo.sh` — 13 cases, exit 0:

- one guilty tracked file among README / helper / untracked notes
- two files jointly required
- irrelevant WIP is all chaff
- spaces and parens in paths
- wheat-only patch; working tree restored (untracked notes still present)
- pycache leak without `PYTHONDONTWRITEBYTECODE` in the caller still isolates `app.py`
- traceback line shift in `test.py` is chaff
- two edits in one file stay **one** wheat file (the killed hunk assumption)
- nested git: wheat is `inner/secret.txt` (untracked-from-outer)
- **untracked `probe.py` is wheat**; tracked README/app.py are chaff
- deleted `flag.txt` is wheat (HEAD resurrection must not be scrubbed as a leftover)
- joint tracked + untracked wheat
- untracked executable bit restored

### Real-repo dogfood (copies; originals never mutated)

`git clone --local` into `/tmp`, then dirtied. `./dogfood.sh` exit 0, 3.83s.

**skills** — untracked `syntax-reference/glean_probe.md` plus noise in `README.md` and `debug-mode/SKILL.md`. Command asserts the probe marker.

```
snapshot 3 uncommitted files
wheat: syntax-reference/glean_probe.md  (untracked)
chaff: README.md, debug-mode/SKILL.md
trials: 5
```

**sitbone** — marker appended to `Sources/Sitbone/SitboneApp.swift`, noise in `Package.swift` and `README.md`. Wheat: the Swift file. 5 trials.

**voidtrace** — untracked `.agents/skills/voidtrace/scripts/glean_probe.ts`, noise in `package.json`. Wheat: the untracked script. 4 trials.

**kizu** — header comment *and* trailing `pub fn glean_probe_marker()` in `src/app.rs`, noise in README + `src/config.rs`. File grain cannot split the two edits:

```
wheat: src/app.rs
chaff: README.md, src/config.rs
trials: 6
```

Second kizu copy: leave `src/app.rs` as comment noise, put the marker in untracked `src/glean_probe.rs`. Wheat: the untracked file. 5 trials.

**tenaoshi** — overlay of the *real* dirty tree (108 files: edits, deletes, untracked EditPlan sources, contract JSON) plus one marker appended to clean `tools/e2e/verify-log.ts`. Command reads that marker.

```
snapshot 108 uncommitted files
wheat: tools/e2e/verify-log.ts
chaff: 107 files
trials: 15
```

Verbose printed every 54-path subset in full. There was no command that *discards* the 107 chaff files — file grain makes that possible (`git restore` / `rm`) and v1 did not emit it.

## Dogfood targets

- `/Users/annenpolka/ghq/github.com/annenpolka/skills` (clone)
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` (clone)
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` (clone)
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` (clone)
- `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` (clone + overlay of live dirty files; original untouched)
- Synthetic fixtures in `./demo.sh`

## Surprises

- Deleting a tracked file and then isolating it as wheat requires resurrecting the file on HEAD trials. The leftover-scrub (needed so `__pycache__` cannot poison isolation) treated that resurrection as "a file the command created" and deleted it again. HEAD and WIP then both lacked the file, wheat was empty. Fix: managed paths are protected from scrub.
- `git ls-files --others` reports a nested git repo as a directory. Walking it (skipping `.git`) is enough; inner dirty files become untracked adds relative to the outer HEAD.
- File grain on kizu `src/app.rs` is honestly coarser than winnow: header comment and probe function travel together. The untracked-probe alternative (`src/glean_probe.rs`) is the move file grain makes cheap.
- 108-file tenaoshi overlay still finished in 15 trials / ~300ms of command time. The log, not the algorithm, is what broke. `--format drop` then emitted 3 shell lines (`git restore` for tracked chaff, two `rm -f` chunks for untracked) and **did not** name `tools/e2e/verify-log.ts`.

### After the improvement (v2: `--drop` / `--format drop` + compact trial log)

Same tenaoshi 108-file overlay:

```
  try 54/108 subset ['AGENTS.md', 'Engine/Sources/TenaoshiEngine/Adapters/AnthropicMessagesClient.swift', ...] ... (+48 more)
  try 1/2 subset ['tools/e2e/verify-log.ts']
wheat: tools/e2e/verify-log.ts
```

`--format drop` (inert; tree unchanged):

```
git restore --worktree --source=HEAD -- AGENTS.md ... tools/spec-gen.ts
rm -f -- Engine/Sources/TenaoshiEngine/EditPlan.swift ... EPC-023.json
rm -f -- contracts/testcases/EPC-024.json ... EPF-008.json
```

3 lines, 0 mentions of the wheat path. `./demo.sh` grew to 16 cases (`--drop` leaves only `app.py` dirty; spaced paths quoted).

**skills --drop** (copy): README noise restored, untracked probe kept.

```
wheat (1 files):
  untracked syntax-reference/glean_probe.md
dropped 1 chaff files; wheat left in the worktree
git status: ?? syntax-reference/glean_probe.md
```

## Failures

1. **v1 leftover-scrub vs deletions** — demo case "deleted file is wheat" returned empty wheat. Fixed: snapshot union managed paths.
2. **v1 fat-tree log / no discard** — tenaoshi 108 files: verbose dumped 54 paths per trial; the useful output (throw away 107 files) did not exist. Fixed: compact `... (+N more)` and `--format drop` / `--drop`.
3. **Still failing / out of scope**
   - Commands that consult the git *index* see a lie: we only rewrite the worktree.
   - Flaky commands abort with exit 3 unless `--fingerprint exit` / `--no-flake-check`.
   - Gitignored untracked files are invisible (`ls-files --exclude-standard`) even if the command reads them.
   - Renames are delete+add (`--no-renames`); both may be wheat if the command cares that the old path vanished.
   - `--format patch` is not `git apply`-guaranteed on binary files.
   - A command that cares about mtime-only changes may over-rebuild.
   - `--max-files` (default 400) aborts rather than walking a dumped `node_modules`.

## Suggested mutations

- `--include-ignored`: see gitignored local config that changes behavior.
- Invert: `--keep-green` — largest subset that keeps the test green, for splitting a refactor out of a bugfix.
- Parallel trials in copies of the tree (file copies are cheap; hunk apply is not).
- Cache fingerprints by file-content digest across invocations.
- `--commit-wheat`: turn the remaining dirty files into a commit, since `--drop` already made that set 1-minimal.
- `--format drop` piped to `git stash push --pathspec-from-file` so chaff is recoverable.

## Kill / keep

**Keep.** The flipped assumption is real: file grain plus untracked units is a different verb from hunk isolation. tenaoshi's 108-file dirty tree is the evidence — 15 trials, one wheat path, then `--format drop` emits the `git restore`/`rm` hunk tools cannot. v2 is the payoff; v1 only reported. Not a wrapper around `git bisect` or `git add -p`.
