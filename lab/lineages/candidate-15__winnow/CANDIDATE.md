# candidate-15 — winnow

## Primitive

Given a command, partition the uncommitted working tree into the smallest hunk set that reproduces the command's current behavior (wheat) and the rest (chaff).

This is `git bisect` for the dirty diff, not for commits. `git add -p` asks you to decide; `winnow` asks the command.

## Why this might not exist

Developers constantly mix a bugfix, a refactor, a README tweak, and an accidental debug print in one working tree. `git bisect` walks commits. `git stash -p` is manual. `git add -p` is also manual. Snapshot tests pin *success*. `pytest -xfail` / `#[should_panic]` pin *any* failure. Nothing takes an arbitrary Unix command and delta-debugs the *uncommitted hunks* that change its fingerprint.

The recurring annoyance: "which of these 12 dirty files (or 3 hunks in one file) actually made the test red?" — a 20-minute `stash -p` loop.

## How to run

From this worktree root:

```bash
./demo.sh
./winnow --help
./winnow -C /path/to/repo --format text -v -- python3 test.py
./winnow --format paths -- pytest tests/test_foo.py
./winnow --format patch -- cargo test -q > guilty.patch
```

Python 3.9+ and `git`. No other deps. The index is never touched; WIP is restored on exit and on SIGINT.

## Empirical transcript

### Before the improvement (v1, file-level, naive fingerprint)

v1 demo passed only with `PYTHONDONTWRITEBYTECODE=1`. Without it:

```
env -u PYTHONDONTWRITEBYTECODE ./winnow -C $A --format json -v -- python3 test.py
```

```
snapshot 2 uncommitted paths
  -> exit=1 Traceback (most recent call last): [24ms]
  -> exit=1 Traceback (most recent call last): [24ms]
  -> exit=1 Traceback (most recent call last): [24ms]
HEAD: exit=1  WIP: exit=1  (same fingerprint)
wheat: []     chaff: README.md, app.py
?? __pycache__/   leftover after the run
```

HEAD was supposed to pass. Bytecode from the first (broken) trial poisoned the HEAD trial. Isolation reported "WIP does not change this command."

Comment inserted at the top of `test.py` plus a real bug in `app.py` (line numbers in the traceback change):

```
wheat (2/3):
  modify app.py
  modify test.py     ← false wheat
chaff (1/3):
  modify README.md
```

Two hunks in one file (header comment + `return a - b`) reported the whole file as wheat — file-level cannot split.

Nested git: `git status` on the outer repo showed `?? nested/`. v1 skipped directories, so inner dirty files were invisible. The command still saw `INNER_CHANGED` on the supposed HEAD tree.

### After the improvement (v2: hunks + trial scrub + loc-stripped fingerprint + nested walk)

Same pycache fixture, no `PYTHONDONTWRITEBYTECODE` in the caller:

```
wheat: app.py#1  @@ -2 +2 @@ def add(a,b):
chaff: README.md#1
pycache cleaned
HEAD exit=0 pass   WIP exit=1
```

Same test.py line-shift fixture:

```
wheat (1 units / 1 files):
  modify app.py  #1 @@ -2 +2 @@ def add(a,b):
chaff (2 units / 2 files):
  modify README.md  #1 @@ -1 +1 @@
  modify test.py  #1 @@ -0,0 +1 @@
```

Same two-hunk file:

```
  try 1/2 subset ['app.py#1']  -> exit=0 pass
  try 1/2 subset ['app.py#2']  -> exit=1 ...
wheat: app.py  #2 @@ -10 +10 @@ def add(a, b):
chaff: app.py  #1 @@ -1 +1 @@
```

`./demo.sh` after the improvement, without the bytecode workaround: 9 cases, exit 0.

### Real-repo dogfood (copies; originals never mutated)

Allowed targets, cloned with `git clone --local` into `/tmp`, then dirtied.

**kizu** — noise in `README.md`, `src/config.rs`, a header comment at the top of `src/app.rs`, plus `pub fn winnow_probe_marker()` appended at the bottom of `src/app.rs`. Command: assert the marker is present.

v1 would have marked the whole `src/app.rs` as wheat. v2:

```
snapshot 4 uncommitted units (hunk)
wheat (1 units / 1 files):
  modify src/app.rs  #2 @@ -6128,0 +6130,2 @@ mod tests {
chaff (3 units / 3 files):
  modify README.md  #1 ...
  modify src/app.rs  #1 @@ -0,0 +1 @@
  modify src/config.rs  #1 ...
```

`--format patch` emitted only the probe function, not the header comment:

```
--- a/src/app.rs
+++ b/src/app.rs
@@ -6126,3 +6126,5 @@
         );
     }
 }
+
+pub fn winnow_probe_marker() {}
```

Working tree restored (`git status` still showed the original three dirty files).

**skills** — marker in `syntax-reference/SKILL.md`, noise in `README.md` and `debug-mode/SKILL.md`. Wheat: `syntax-reference/SKILL.md`.

**sitbone** — marker in `Sources/Sitbone/SitboneApp.swift`, noise in `Package.swift` and `README.md`. Wheat: `Sources/Sitbone/SitboneApp.swift`.

**tenaoshi** — marker in `tools/e2e/verify-log.ts`, noise in `AGENTS.md` and `justfile`. Wheat: `tools/e2e/verify-log.ts#1`.

**voidtrace** — marker in `.agents/skills/voidtrace/scripts/run-breakpoint.ts`, noise in `package.json`. Wheat: the breakpoint script.

**nested git fixture** — outer `root.txt` dirty, inner repo `secret.txt` dirty. Command reads the inner file. Wheat: `inner/secret.txt` (new-file add from the outer repo's point of view). Chaff: `root.txt`.

## Dogfood targets

- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` (clone)
- `/Users/annenpolka/ghq/github.com/annenpolka/skills` (clone)
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` (clone)
- `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` (clone)
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` (clone)
- Synthetic fixtures: spaces/parens in paths, joint two-file wheat, pycache leak, traceback line shift, two hunks in one file, nested git

## Surprises

- Git's default `-U3` merges nearby edits into one hunk. Isolation uses `git diff -U0` so a header comment and a `return` change 9 lines apart become two units. `--format patch` then re-diffs wheat against HEAD with context, so the human patch is readable.
- Python 3.14 wrote `__pycache__` that made even the HEAD tree fail. The command under test is not a pure function of the snapshotted files.
- `git ls-files --others` reports a nested git repo as `nested/` (a directory) and refuses to descend. Walking that directory (skipping `.git`) is enough to see inner dirty files, treated as untracked adds relative to the outer HEAD.
- A fingerprint that keeps `file:line` will call a one-line comment in the test file "wheat" because the traceback moved. Stripping locations while keeping filenames and exception text was the difference between "almost useful" and "correct."

## Failures

1. **v1 pycache leak** — without `PYTHONDONTWRITEBYTECODE`, HEAD and WIP fingerprints matched (both fail); wheat empty. Fixed: child env sets `PYTHONDONTWRITEBYTECODE=1`, generated paths are ignored, files created during a trial are scrubbed.
2. **v1 traceback line numbers** — chaff in `test.py` became wheat. Fixed: default fingerprint rewrites `File "...", line N` and `path:line[:col]`.
3. **v1 file-level** — cannot split two hunks in one file. Fixed: default `--granularity hunk`.
4. **v1 nested git** — inner changes invisible. Fixed: expand untracked directories.
5. **Still failing / out of scope**
   - Commands that consult the git *index* (`git diff --cached`) see a lie: we only rewrite the worktree.
   - Flaky commands (time, network) abort with exit 3 unless `--fingerprint exit` / `--no-flake-check`.
   - `--format patch` is not `git apply`-guaranteed on binary files.
   - Hunk apply is UTF-8 text; mixed hunks on a binary path fall back to whole-file.
   - `target/`, `node_modules` if *not* gitignored and huge would be walked; we skip only well-known generated dir names when expanding, and `--exclude-standard` handles gitignored trees.
   - A command that cares about mtime-only changes (a build system) may over-rebuild; we do not restore original mtimes.

## Suggested mutations

- `--commit-wheat` / `--stash-chaff`: actually split the WIP into two commits or a stash, not just report.
- `--watch`: re-run isolation as the tree changes (kizu-adjacent).
- Cache fingerprints keyed by `(subset, file-digests)` across invocations.
- Symbol granularity: isolate a single function, not a U0 hunk.
- Invert: `--chaff-command` — "find the largest subset that *keeps* the test green" for splitting a green refactor out of a red bugfix.
- Landlock/sandbox so the command cannot leak state through `$HOME` caches.
- Read `blame` of wheat hunks and print the last committed context ("you are undoing alice's 2024-06 fix").

## Kill / keep

**Keep.** The verb is new, the interaction is Unix (command in, patch/paths out, restore the tree), and dogfood on kizu/skills/sitbone/tenaoshi/voidtrace plus the ugly fixtures actually changed the tool. v1 was wrong on Python tests; v2 is not. Not a wrapper around `git bisect` — bisect has no uncommitted-hunk object.

Discarded conventional primitives: error-log annotator with `git blame`; "deadname" search for lingering pre-rename identifiers. The other unconventional candidate was `still` (succeed iff a command still fails the same way). `winnow` ate that fingerprint as an internal primitive and added attribution.
