# mutation-05 — zure

## Primitive
`zure` reports identifier-level conflicts (def vs use, deleted def vs new use, split-brain defs) between **already-committed recent history** and the **uncommitted working tree** (staged, unstaged, untracked). No second branch: a pre-commit semantic merge with yourself.

## Why this might not exist
`git diff` shows only the dirty tree. The callsite you added two commits ago is not in that diff, so a signature change you are about to commit looks locally consistent. `git merge` never runs — there is no other ref. Semantic-merge tools assume two branches. Pre-commit hooks assume the index is the universe. The missing Unix verb is: given HEAD plus a dirty tree, emit the crossed definition/use edits that linear history would hide.

Ancestor `rift` compared two refs. This mutation kills that assumption.

## How to run
From the worktree root:

```bash
./zure --self-test
./demo.sh
./zure                          # worktree vs recent history
./zure --staged -q              # pre-commit gate
./zure --horizon 12
./zure --since origin/main
./zure --replay 20
./zure -C /path/to/repo
```

Exit 0 = clean, 1 = zures, 2 = error.

## What the flipped assumption bought and lost

**Bought**
- Zero-arg daily use. `zure` in a dirty checkout; no `side-a side-b`, no merge-base theatre.
- Untracked files are a changeset. `git merge-tree` cannot see them; a new `extra.rs` calling a function the last commits deleted is exactly the pre-commit case.
- Directional kinds: `break-use` (work changes a def; history added uses you are not looking at) is the high-value polarity. `stale-use` is the ghost callsite you are about to add. `dup-def` is the helper you already committed and are pasting again.
- `--replay` treats each linear commit as a former worktree. GitHub squash/merge history, which made `rift --audit` structurally empty (every merge one-sided), becomes an audit target.
- `--staged` is a real pre-commit hook: the index vs the last N commits, ignoring leftover untracked junk.

**Lost**
- The original silent-merge question. Two living branches that git would merge cleanly are out of scope unless you pass `--diffs`.
- `git merge-tree` as an oracle. Sequential apply is always clean. `hidden` now means “history files are absent from `git diff`,” not “the merge would hide this.”
- Precision vs the merge analog. The working tree *can* see HEAD’s definitions, so a new callsite after a recent signature change is often correct — `stale-use` is a weaker signal than rift’s crossed-branch def-use.
- Horizon is a heuristic (`@{upstream}`, else main, else `HEAD~10`). Too wide: a file-move rewrite looks like a second changeset. Too narrow: the callsite falls out of the window.
- You no longer get a merge-commit audit. `--replay` is the replacement and is noisier on large refactors.

## Empirical transcript

### Before the improvement (v0.1)

Synthetic break-use already worked: commit a callsite, dirty the signature, no second branch.

```
$ ./zure --color never -C syn --horizon 8
zure: worktree vs history HEAD~1..HEAD
1 zure(s)

break-use  parse_config  hidden
  hist  use + src/cli.rs:2  let cfg = parse_config(raw);
  work  def + src/parse.rs:1  pub fn parse_config(s: &str, timeout: u64) -> Config {
  work  def - src/parse.rs:1  pub fn parse_config(s: &str) -> Config {
```

kizu dogfood (commit a new `scan_scars` callsite, dirty an extra `timeout_ms` param) lied about *what* conflicted. History window `HEAD~12` included the hook.rs → hook/scan.rs file move, so both sides “changed the def.” Classification picked `dup-def`. Signature-line *mentions* of `ScarHit` and the parameter `paths` became `stale-use`. Three zures, two of them junk, and the real one mislabeled:

```
3 zure(s)
stale-use  ScarHit   hidden    # return type on the signature line
stale-use  paths     hidden    # parameter name; `let paths =` counted as a def
dup-def    scan_scars hidden    # file-move + later signature tweak
```

`--replay` on kizu’s last 12 non-merge commits dumped 440 hits (`let abs =`, `let after =`, `let row =`) because BINDING_RE treated every local as a definition.

### After the improvement (v0.2)

Fixes from that run: (1) on a definition line, only keep *call-shaped* uses (`foo(`), not types/params; (2) `dup-def` only when both sides *introduce* the name, not when both edit an existing one; (3) BINDING_RE requires `export`/`pub`/`static` — drop inner `let abs =`; (4) ignore `*.html`/`*.css`; (5) cap text hits at 12/side.

Same kizu recipe, now one hit, correctly `break-use`:

```
$ ./zure --color never -C kizu-clone --horizon 12
zure: worktree vs history HEAD~12..345a55dd  (bed252ab..345a55dd)
hist 90 file(s), work 1 file(s)  [worktree+untracked]
1 zure(s)

break-use  scan_scars  hidden
  hist def + src/hook/scan.rs:22  pub fn scan_scars(paths: &[PathBuf]) -> Vec<ScarHit> {
  hist def - src/hook.rs:135  pub fn scan_scars(paths: &[PathBuf]) -> Vec<ScarHit> {
  hist use + src/hook.rs:13  pub use scan::{scan_scars, scan_scars_from_index};
  hist use + src/hook/tests.rs:110  let hits = scan_scars(std::slice::from_ref(&file));
  hist use + src/paths.rs:175  let _ = crate::hook::scan_scars(paths);
  work def + src/hook/scan.rs:22  pub fn scan_scars(..., timeout_ms: u64) -> Vec<ScarHit> {
  work def - src/hook/scan.rs:22  pub fn scan_scars(paths: &[PathBuf]) -> Vec<ScarHit> {
```

sitbone, same recipe (`saveCumulative` extra `flush:` vs a committed probe callsite). Class header noise stays gone:

```
zure: worktree vs history HEAD~12..2a5562d8  (12bc37bc..2a5562d8)
hist 23 file(s), work 1 file(s)  [worktree+untracked]
1 zure(s)

break-use  saveCumulative  hidden
  hist use + Sources/SitboneData/ZureProbe.swift:3  try await store.saveCumulative(CumulativeRecord())
  work def + Sources/SitboneData/JSONSessionStore.swift:40  public func saveCumulative(_ record: CumulativeRecord, flush: Bool) async throws {
  work def - Sources/SitboneData/JSONSessionStore.swift:40  public func saveCumulative(_ record: CumulativeRecord) async throws {
```

voidtrace clone: committed `zure-probe.ts` calling `createWorldState([])`, dirty extra `epochMs` param → `break-use createWorldState`.

tenaoshi *real* dirty tree (copy of uncommitted work, including untracked EditPlan/ReviewSession): 68 zures vs `HEAD~12`. The interesting one is not synthetic — the working tree deletes `class ContractCase` while recent history still constructs it in generated oracles and `specs/tenaoshi.pkl`:

```
break-use  ContractCase  in-diff
  hist  use + Engine/Tests/TenaoshiEngineTests/OraclesGenerated.swift:239  try await ContractHarness.run(ContractCase(
  hist  use + specs/tenaoshi.pkl:227  new patterns.ContractCase {
  work  def - specs/patterns.pkl:49  class ContractCase extends Clause {
```

voidtrace *real* dirty tree: 16 zures vs `HEAD~15` (`evaluateForcedSlashRuntime`, `parseScenarioDomain`, …). Some are hunk-header ghosts (`def ~` on an import line because another hunk in the same file carries the funcname).

`--replay` (read-only, originals):

```
kizu      replayed 12: 9 flagged, 3 clean, 149 zure(s)
sitbone   replayed 10: 3 flagged, 7 clean,   5 zure(s)
voidtrace replayed  8: 3 flagged, 5 clean, 101 zure(s)
tenaoshi  replayed  8: 4 flagged, 4 clean,  31 zure(s)
```

`./demo.sh` — 23 checks, exit 0.

## Dogfood targets
- Synthetic git fixtures (break-use, stale-use via untracked, delete-use, dup-def, ugly unicode/space names, lockfiles, `node_modules`, `--staged`, `--replay`, `--diffs`)
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` (clone + dirty signature; read-only `--replay`)
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` (clone + dirty signature; read-only `--replay`)
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` (copy of real dirty tree; constructed break-use; read-only `--replay`)
- `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` (copy of real dirty tree including untracked; read-only `--replay`)

Originals were never mutated.

## Surprises
- kizu’s last dozen commits *are* a parallel changeset relative to a dirty signature: the hook split moved `scan_scars`. That is the flipped assumption working — and also why v0.1 drowned in `dup-def`.
- tenaoshi’s live dirty tree already contains the textbook pre-commit rift (`ContractCase` deleted in work, still constructed in recent history). No fixture required.
- voidtrace and tenaoshi being dirty is an advantage this mutation has over rift: the second changeset is sitting on disk.
- `set -o pipefail` plus `echo "$out" | grep -q` SIGPIPEs on a large tenaoshi report even when the first line matches. Demo now uses here-strings.

## Failures
- v0.1 file-move + signature → `dup-def`; type/param tokens on the signature line → `stale-use`. Fixed.
- v0.1 `let abs =` as a definition. Fixed (exported/pub/static bindings only).
- Hunk-header `~` defs still attach to the *file*, so editing an import in a large `evaluate.ts` can mark an untouched function as `work def ~`. `--strict` disables this; default keeps continuation-line signatures.
- `--replay` on kizu/voidtrace refactors is still noisy (149 / 101). Usable as a smoke test, not yet as a history auditor.
- `extension NSWindow` vs existing `NSWindow` uses: language-agnostic tokenizer cannot tell stdlib types from yours once they pass the STDLIB list.
- Horizon auto-detect (`@{upstream}` / main / `HEAD~10`) is a guess. On a long-lived main it is “last ten commits,” not “this feature.”

## Suggested mutations
- `--alive`: for work-changed defs, `git grep` HEAD for uses in files the worktree did not touch, even if those uses are older than the horizon. That is the blast radius of the commit you are about to make.
- Three-layer dirty: history vs index vs unstaged+untracked (you staged the signature, left the callsite unstaged).
- Bind hunk headers to their own hunk, not the whole file.
- Rename: `-foo` def plus `+foo2` def vs remaining uses of `foo`.
- Arity/type tokens on call-shaped uses, so `parse_config(raw)` vs `parse_config(s, timeout)` is a fact rather than a heuristic.

## Kill / keep
Keep. The flipped assumption is the whole product: a pre-commit command you run without inventing a second branch, which rift could not be. Empirically hits real signature/callsite pairs in Rust/Swift/TypeScript and a live tenaoshi deletion. Replay on squash-merge history is the leftover weak path; the useful path is `zure` / `zure --staged -q` on a dirty tree.
