# candidate-37 — ply

## Primitive

A unified diff is a superposition of syntactic classes. `ply` projects the patch onto one class and emits the **ply-edit** `(path, line, class, op, old, new)`.

Same line can carry two plies: `30 → 60` is a number edit, `seconds → secs` is a comment edit. `--class number` hides the comment. `--check --only docs` fails if a "docs PR" leaked idents.

## Four primitives considered

1. **ply** — Syntactic strata of a patch. **Implemented.**
2. **bane** — The poison predecessor: smallest earlier test that makes this test fail (order dependence). Keep as a mutation; ddmin-adjacent to `winnow`, needs a suite runner.
3. **nett** — Classify each commit in a range SURVIVED / CANCELLED / TRIMMED by whether its line-level effect is still in the tip. **Discarded:** occupancy-adjacent (`sate` / `plea` / `held`).
4. **lull** — Interval from a production symbol's last change to the next test-file mention. **Discarded:** a clock metric; overlaps `unseen` / `skew`.

`bane` is real but slow to dogfood. `nett` and `lull` sit on occupied objects. ply's object (the typed atomic edit) is not leftover-names, inverse-printf, occupancy, path-conditions, wait-for, generation lots, or env-ABI.

## Why this might not exist

`git diff` is untyped. `delta` colors it. `difftastic` shows a tree. `git log -G` / `-S` search one token. Nobody asks: *partition this PR by syntactic class.*

The recurring review cheat is silent: a "comment-only" commit that also bumped a timeout; a rename that also changed three literals; a formatter that hid a number change. ply is that partition as a Unix filter.

## How to run

From the worktree root:

```bash
./demo.sh
./demo.sh 0
./ply --selftest
./ply --help
./ply --git HEAD~3..HEAD --op chg
./ply -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone --git HEAD~5..HEAD --class number
./ply -C /Users/annenpolka/ghq/github.com/annenpolka/kizu --git HEAD~3..HEAD --class string --op chg
```

Python 3.9+, stdlib, `git`. `./ply` is the CLI.

## Empirical transcript

### v0.1 — positional projection, every class, every file

`--selftest` 32/32. Fixture: mixed line splits `30→60` and `seconds→secs`; whitespace-only is empty; JSON keys ≠ string values; import paths are class `import`.

Real repos (HEAD ranges as of 2026-08-20):

- **kizu** `HEAD~3..HEAD` — **15315 edits**, `punct=10059`, `ins=15286`. Cargo.lock and new files exploded. The actual signal (`0.5.1→0.7.0`, scar string `real scar outside fence -->` → `real scar outside fence`, `render_diff_line → render_diff_line_with_tokens`) was buried. Japanese in SPEC.md was **per-character punct**.
- **tenaoshi** — AGENTS.md CJK as punct firehose (`契→は`, `約→向`).
- **sitbone** — money shot already visible under the noise: `threshold → presentThreshold`, `0.4 → 0.45`, `8 → 0`. Also `out → Some` false chg from n-to-m positional pairing on a rewritten line.

### v0.2 — after dogfood (one improvement)

Four changes, one object: *the default ply-edit has to be a reviewable mutation, not a tokenizer dump.*

1. **CJK / prose → class `text`**, not punct.
2. **Default drop punct**; skip lockfiles; skip added/deleted file bodies (`added=N` in the header).
3. **n-to-m rewrites del+ins unless values look like the same entity**; 1-to-1 stays `chg` (so `foo→bar` is a rename, `out→Some` is not).
4. **`--check` prints a verdict line**, not thousands of rows. SIGPIPE-safe.

After:

- **kizu** `HEAD~3..HEAD --op chg` — **10 edits**: version string, scar test string, six `_with_tokens` renames, `and_then → map`. `added=5 skipped_lock=1`.
- **sitbone** `--class number,ident --op chg` — **12 edits**: hysteresis `0.4→0.45` (twice), scroll `8→0`, `threshold→presentThreshold` (the dual-threshold rename).
- **tenaoshi** `--class docs --op chg` — Japanese as `text` (`蒸留の取りこぼし → 取りこぼし`), preset labels `整えて → Tidy` as strings.
- **voidtrace** last commit `--class number` — coverage counts `65→67` plus one test `47→48`.

`--selftest` 36/36.

## Dogfood targets

- Fixture git repo in `./demo.sh` (mixed line, rename, comment-only, CJK).
- kizu, sitbone, tenaoshi, voidtrace.

## Surprises

- Per-class projection is *too* faithful on new files: adding `fn hello` is a bag of `ins` tokens. The interesting verb is **chg on modified files**.
- `threshold → presentThreshold` (substring) is the rename ply; `PresenceStatus → applyHysteresis` still slips through as 1-to-1 leftover after SM equals. Honest-ish, slightly loud.
- Lockfiles are a ply of version *strings*, not numbers (`"0.5.1"`). Default skip is right; `--locks --class string` is the version-bump report.

## Failures

- Hyphenated Cargo keys (`tree-sitter`) split on `-`.
- Cross-hunk moves of a function still need `--moves` to see; default hides them.
- `--diff` reconstruction is hunk-lossy (no git index lines). Enough to read, not to `git apply`.
- Markdown tables with ASCII art still leak punct if you `--class all`.

## Suggested mutations

- `bane` (poison predecessor) as a sibling tool, not a flag.
- Ply-aware `git add -p` (stage only the number ply).
- `--net` bag-difference per class (moves vanish even without pairing).
- Language-aware hyphen/raw-string (Rust `r#"..."#`).
- JSON pointer path as the locus instead of line, for key plies.

## Kill / keep

**Keep.** The primitive is one sentence, the default output after v0.2 is something a reviewer would paste tomorrow (`--class number` on sitbone's hysteresis; `--check --only docs` on a supposed comment PR), and it is not an occupied cluster.
