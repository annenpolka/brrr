# mutation-08 — skew

## Primitive

Given a callee, list caller *files* whose save/commit clock is behind the callee file's clock, and diff the definition as it existed at the caller file's clock against HEAD (or the dirty worktree). Clock is **mtime when the file differs from HEAD**, otherwise the **last commit that touched the file**. No `git blame`.

## Why this might not exist

`unseen` (candidate-14) joined blame-of-caller-line with evolution-of-callee. Blame is the wrong clock for the daily question "have I saved this file since that function changed?" A whitespace commit on one line, or an unsaved buffer, makes line history lie. `git log -- path` and `ls -l` already know a coarser clock; nobody joins it to callee diffs. IDEs show the current signature. Review and CI still compile. The missing verb is a **file-clock join**, not another linter.

Flipped assumption: kill per-line history. Accept the false negative (a later unrelated save of the caller file "catches it up") in exchange for speed, dirty-tree honesty, and a unit that matches how people actually save work.

## How to run

```bash
./demo.sh
./skew --repo <git-checkout> [--diff] [--sig] [--dirty] [--ghosts] [--format human|json|tsv] [symbol|path|path:line]
```

Synthetic fixture (weird filenames, unicode paths, nested git, Python + Rust, plus a same-commit "fresh" caller for the dirty-mtime case) is built by `fixtures/mkrepo.sh` and exercised by `./demo.sh`.

## Empirical transcript

### Fixture (v1)

```
$ ./skew --repo ./fixtures/lagrepo --diff greet
greet
  def   src/greet.py:1-7  2024-06-01  …  commit  greet gains prefix; odd_fn gains step
  changed  sig  3 files  lag 882d
    docs/api.md          2022-01-01  commit  :3
    src/app.py           2022-01-01  commit  :1,:5
    tests/test_greet.py  2022-06-01  commit  :1,:5
    --- a/greet@…
    +++ b/greet@HEAD
    -def greet(name):
    -    return "hi " + name
    +def greet(name, excited=False, prefix="hello"):
```

Two mentions in `app.py` collapse to one file row. `src/cli.py` is a second cohort (saw `excited`, slept through `prefix=`). `src/fresh.py` was committed with the prefix change — file clocks match, so it does not lag.

Same-file `odd_caller` / `rust_shout` are silent (a file cannot be behind itself). Cross-file `use_odd.py` and `use_rust.rs` fire. Nested git does not crash. `./demo.sh` exits 0.

Dirty callee (HEAD vs worktree):

```
# edit prefix="hello" → "hey" in greet.py, uncommitted
$ ./skew --repo ./fixtures/lagrepo --diff --dirty greet
greet
  def   src/greet.py:1-7  2026-08-19  WORKTREE  mtime
  changed  sig  1 file  lag 809d
    src/fresh.py  2024-06-01  commit  :1,:5
    --- a/greet@7560c0ff7
    +++ b/greet@WORKTREE
    -def greet(name, excited=False, prefix="hello"):
    +def greet(name, excited=False, prefix="hey"):
```

`fresh.py` only appears once the callee clock is mtime. That is the question blame cannot ask.

### Before the improvement — real repos

Unscoped kizu (~6.5s, vs unseen's ~14s blame walk) ranked a fake `verify_token` (brace-span swallowed most of `src/git.rs`) and *plan files* whose clocks are older, burying the compiled callers:

```
$ ./skew --repo kizu --limit 8
verify_token   changed  sig  3 files  lag 19d   def=src/git.rs:106-1148
insert_scar    changed  sig  1 file   lag 18d   plans/v0.2.md
insert_scar    changed  sig  1 file   lag 18d   plans/v0.3.md
events_dir     changed  sig  1 file   lag 14d   plans/v0.3.md
```

Forced `insert_scar` still reconstructed the real JSX/`ScarInsert` contract, but `--limit 2` stopped at the plans. The compiled callers were a later *body* cohort (they last saw `Result<Option<ScarInsert>>` already; 2026-05-04 was placement, not signature):

```
$ ./skew --repo kizu --limit 8 insert_scar
insert_scar  sig   plans/v0.2.md          lag 18d
insert_scar  sig   plans/v0.3.md          lag 18d
insert_scar  body  CLAUDE.md              lag 17d
insert_scar  body  AGENTS.md, review.rs, app.rs  lag 16d
```

`src/app/review.rs` and `src/app.rs` last-file-commit 2026-04-25; `src/scar.rs` 2026-05-04. File-level clock *does* catch them — ranking hid them. Coarser clock, still the right join.

sitbone `--limit 2 JSONSessionStore` reconstructed the logging wrap around tests *and* the ADR, as two file-clock cohorts (docs 9d, tests 8d) instead of unseen's per-line blob. Unscoped led with `deserted` / `tick` / `activeProfile` (Swift spans still swallow neighbors).

tenaoshi `writeBack` printed nothing: `CaptureService.swift`, `App.swift`, and `PanelSession.swift` are all dirty, and the caller mtimes (20:48, 21:05) are *newer* than the callee mtime (20:36). File-level clock correctly says those files have been saved through the current `writeBack`. That is the false negative we accepted by killing blame (unseen's line clock still saw the AX→Scope edit).

The dirty tree is where skew earns its name. Unscoped tenaoshi (~0.4s) is almost entirely WORKTREE mtime callees:

```
$ ./skew --repo tenaoshi --limit 12
options            mtime  sig   ConfigStore.swift (committed)   lag 1d
TransformRequest   mtime  body  adapters (also dirty) + ContractHarness (committed)
AnthropicMessagesClient mtime  ClientFactory.swift (committed)
```

`--sig` collapses to `options` — but the diff is `capture(contextGraphemes:)` leaking through a Swift property span. Same-session dirty-vs-dirty pairs (RequestComposer vs adapters, both mtime, lag 0d) flood the list: that is not "hasn't been saved through", that is "two buffers in one sitting".

## Dogfood targets

| Target | Result |
| --- | --- |
| `fixtures/lagrepo` | deterministic file-level hits; dirty `fresh.py`; `./demo.sh` exits 0 |
| `/Users/annenpolka/ghq/github.com/annenpolka/kizu` | `insert_scar` JSX/`ScarInsert` reconstructed; compiled callers present but ranked under plans; ~6.5s unscoped |
| `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` | `JSONSessionStore` tests+ADR; `activeProfile` / `tick` / `deserted` |
| `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` | `writeBack` miss (caller mtimes newer); dirty `TransformRequest` / client adapters vs committed factory+harness |

## Surprises

- File-level grouping is the interesting unit: `app.py`'s two `greet` mentions become one row; `cli.py` still splits out because its *file* clock saw a different historical body. The two-era split survived without blame.
- Docs and plans sleep even harder at file granularity than at line granularity — their last-file-commit is "when the document was last edited", which is often never.
- HEAD vs worktree is not a corner case. tenaoshi's live dirty engine is the whole unscoped view. `fresh.py` in the fixture only exists to prove a same-commit caller becomes a sleeper the moment the callee is unsaved.
- kizu `insert_scar` compiled callers are a *body* lag (JSX placement) sitting behind a *signature* lag in old plans. Sig-first ranking, borrowed from unseen, fights the new clock.

## Failures

- Same-file sleep is invisible (by design). Intra-file `odd_caller` will never fire.
- A later unrelated save of a caller file clears the skew (kizu `benches/operations.rs` shares scar.rs's last commit; tenaoshi `writeBack` callers have newer mtimes).
- `git show caller_file_commit:callee_path` still does not follow renames (`missing-then`, hidden by default).
- Naive brace/indent spans: `verify_token` ate 1000 lines of `git.rs`; Swift `options` leaked `capture()`; `activeProfile` swallows neighbors.
- Unscoped English leftovers (`beta`, `missing`) still appear as one-line "defs" in tests.
- `--limit` is per historical-body cohort, so one symbol can occupy the whole page with plan files.

## Suggested mutations

- Follow renames when `git show` at the caller file's commit misses the callee path.
- Language-aware spans (tree-sitter) so Swift properties / Rust `mod` trees cannot pose as callees.
- Inverse query: given a dirty callee, list committed files that mention it (the pre-commit blast list). `--dirty` is the start of that.
- Editor binding: `skew %` on the current file = callees this buffer is behind, using its mtime.

## Kill / keep

**Keep, with a ranking/span fix.** The fixture and kizu `insert_scar` prove the join still answers the ancestor's question without blame, and the dirty-`fresh.py` / tenaoshi WORKTREE view is a new verb unseen could not say. Kill only if compiled callers cannot be ranked above sleeping plans, or if same-session dirty-vs-dirty noise is the whole tool. v1 ranking almost hid the primitive the same way unseen v1 hid `insert_scar` under word-frequency ghosts.
