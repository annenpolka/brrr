# candidate-07 — zanei (残影)

## Primitive

Print leftover claims a diff just made false.

A *fact* is a bound name/value, rename, or polarity flip extracted from a unified diff. An *afterimage* is a remaining comment, doc, test, string, or config line in the destination tree that still asserts the old fact. Exit `0` if the destination has no afterimages, `1` if any remain (linter-composable), `2` on error.

Discarded (more conventional) primitives: **shear** (import-graph XOR co-change; exists in the software-analysis literature as logical vs structural coupling) and **stringly** (cross-file identifier-string drift; i18n/dead-string linters already nibble this). The other survivor, **clove** (partition dirty hunks into independently commitable atoms), is listed under mutations.

## Why this might not exist

`rg` can find a token. `git grep` can find it at a revision. Neither knows that *this diff* changed `timeout: 10 → 30` or `MAX_RETRIES → MAX_ATTEMPTS`, so they cannot ask the only question that matters after an edit: **what else in the tree still believes the old fact?**

That gap is why READMEs, ADRs, plugin manifests, CLI help, and generated oracles rot one commit behind the implementation. The missing verb is not "search"; it is "belie".

## How to run

From this worktree root (Python 3.10+, `git` on `PATH`, no other deps):

```bash
chmod +x ./zanei ./demo.sh
./zanei self-test
./demo.sh                 # exits 0
./zanei --help
./zanei -C <repo>         # HEAD → worktree
./zanei -C <repo> A B     # tree A → tree B, search B
git diff A B -- path | ./zanei --diff - -C <repo>
```

## Empirical transcript

### Before the improvement (v0.1, commit `18defbd`)

Toy fixture, implementation changed, claims left behind:

```
$ ./zanei --facts-only --no-color -C fixtures/.run/toy HEAD~1 HEAD
zanei: 4 fact(s)  HEAD~1 → HEAD
  rename   MAX_RETRIES: 'MAX_RETRIES' → 'MAX_ATTEMPTS'  (src/retry.py:3)
  value    MAX_RETRIES: '3' → '8'  (src/retry.py:3)
  value    HOOK_TIMEOUT: '10' → '30'  (src/retry.py:4)
  polarity ENABLE_CACHE: 'True' → 'False'  (src/retry.py:5)

$ ./zanei --no-color -C fixtures/.run/toy HEAD~1 HEAD
zanei: 14 afterimages  HEAD~1 → HEAD
RENAME MAX_RETRIES → MAX_ATTEMPTS   src/retry.py:3
   98 assert  tests/test_retry.py:5   assert MAX_RETRIES == 3
   92 docs    README.md:3             The client retries 3 times by default (`MAX_RETRIES`).
FLIP ENABLE_CACHE: True → False
   90 assert  tests/test_retry.py:7   assert ENABLE_CACHE is True
FACT HOOK_TIMEOUT: 10 → 30
   90 assert  tests/test_retry.py:6   assert HOOK_TIMEOUT == 10
   66 config  plugin.json:5           "timeout": 10
   62 docs    docs/help.txt:2         --timeout N   hook timeout seconds (default 10)
```

Real kizu tree — package version moved, plugin manifest did not:

```
$ git -C kizu diff v0.3.0 v0.7.0 -- Cargo.toml | ./zanei --diff - -C kizu --min-score 70
zanei: 3 afterimages  diff → worktree  (.../kizu)

FACT version: 0.3.0 → 0.7.0   Cargo.toml:3
  103 config  plugin/plugin.json:4    "version": "0.3.0",
   84 docs    plans/v0.3.md:103       - [ ] version bump to 0.3.0
   84 docs    plans/v0.3.md:451       "version": "0.3.0"
```

Confirmed on disk: `Cargo.toml` has `version = "0.7.0"`; `plugin/plugin.json` still has `"version": "0.3.0"`.

Real sitbone hysteresis commit (single `threshold: 0.4` → `presentThreshold: 0.45` / `absentThreshold: 0.35`):

```
$ ./zanei --no-color -C sitbone e9b0f75^ e9b0f75 --min-score 50
zanei: 11 afterimages  e9b0f75^ → e9b0f75
RENAME threshold → absentThreshold
   92 docs    CLAUDE.md:329           ... threshold 0.4 ...
   80 code    Sources/SitboneCore/SiteObserver.swift:45
              private let threshold: Double = 0.7
   80 code    Sources/SitboneCore/SiteObserver.swift:101
              if ratio >= threshold { return .flow }
   92 docs    docs/adr/0019-presence-hysteresis.md:12
              ... smoothedScore >= threshold ...
FACT threshold: 0.4 → 0.45
   84 docs    CLAUDE.md:329           ... threshold 0.4 ...
   84 docs    docs/adr/0019-presence-hysteresis.md:76
              既存の `threshold: Double = 0.4` パラメータを削除し...
```

Real voidtrace feature commit (docs + new analysis slice):

```
$ ./zanei --facts-only -C voidtrace 6e3368b^ 6e3368b
zanei: 27 fact(s)   # 21 of them remames
  rename   Exit → exit
  rename   Patch → Patches
  rename   request → requests
  rename   slice → slices
  rename   experiment → ExperimentFailure
  rename   revision → analysisRevision
  ...
$ ./zanei -C voidtrace 6e3368b^ 6e3368b --min-score 60
zanei: 3670 afterimages
```

Ugly fixture: space / Japanese / emoji filenames worked; **nested git files were invisible** (`git ls-files` of the parent does not list the inner tree).

### After the improvement (v0.2)

Same sitbone commit, default-ish threshold 55:

```
$ ./zanei --no-color -C sitbone e9b0f75^ e9b0f75 --min-score 55
zanei: 2 afterimages  e9b0f75^ → e9b0f75

FACT threshold: 0.4 → 0.45   Sources/SitboneCore/PresenceArbiter.swift:30
   84 docs    CLAUDE.md:329   @Test("カメラのみpresent → 総合present（weight 0.50 > threshold 0.4）")
   84 docs    CLAUDE.md:332   @Test("idleのみpresent → 総合absent（weight 0.05 < threshold 0.4）")
```

SiteObserver's unrelated `threshold = 0.7` is gone (homonym). ADR-0019, which *documents* the old value next to the new one, is gone (`file-has-new`). The two CLAUDE.md lines are real: they still describe the pre-hysteresis tests.

Same voidtrace commit:

```
$ ./zanei --facts-only -C voidtrace 6e3368b^ 6e3368b
zanei: 5 fact(s)   # coverage counts only; prose remames dropped
$ ./zanei -C voidtrace 6e3368b^ 6e3368b --min-score 60
zanei: 0 afterimages
  5 fact(s) changed; none left an afterimage (min-score gated).
```

**3670 → 0.** The gold kizu `plugin.json` finding is unchanged.

Nested git after the walk fix (from `./demo.sh`):

```
  ok  nested git file visible
```

Tenaoshi preset-name commit (Japanese intents → English palette names):

```
$ ./zanei --no-color -C tenaoshi 3798ea7^ 3798ea7 --min-score 60
zanei: 26 afterimages
FACT intent: 整えて → Tidy      contracts/testcases/CTR-001.json:4  "intent": "整えて"
FACT intent: 短くして → Compress
FACT intent: 整理して → Organize
FACT intent: 明文化して → Expand
FACT intent: 続けて → Complete
```

`./demo.sh` after the improvement: `passed=24 failed=0`, exit 0.

## Dogfood targets

| Target | What was run | Outcome |
| --- | --- | --- |
| `fixtures/toy` (synthetic git) | worktree + `HEAD~1 HEAD` | 12–14 afterimages, all intended |
| `fixtures/ugly` (spaces, `日本語コメント.md`, `🌀 leftover.md`, generated/, nested git) | worktree + `--diff -` | names work; nested git failed then fixed |
| `/Users/annenpolka/ghq/github.com/annenpolka/kizu` | `git diff v0.3.0 v0.7.0 -- Cargo.toml \| zanei --diff -` | **plugin.json frozen at 0.3.0** vs crate 0.7.0 |
| `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` | `e9b0f75^ e9b0f75` | CLAUDE.md still teaches `threshold 0.4` |
| `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` | `6e3368b^ 6e3368b` | v1 drowned in prose remames; v2 silent |
| `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` | `3798ea7^ 3798ea7` | contracts/oracles still use `整えて` after palette rename |
| `/Users/annenpolka/ghq/github.com/annenpolka/skills` | `6b19433^ 6b19433` | no fact mutations (markdown-only tweak) |
| `/Users/annenpolka/ghq/github.com/annenpolka/stratal` | listed | empty tree, skipped |

## Surprises

- The kizu plugin manifest is a live, checkable inconsistency: crate `0.7.0`, plugin `"version": "0.3.0"`. zanei found it from a two-line version hunk. That is the "why doesn't this exist?" moment.
- Tenaoshi's leftover `整えて` may be *intentional* (saved-command / free-text path vs palette-name path). zanei cannot know which side is canonical; it only reports that a changed fact still has believers.
- Aligning deleted/added lines in a large markdown hunk will invent remames (`Patch`/`Patches`, `Exit`/`exit`) unless you refuse English inflection.

## Failures

- **v1 prose remames** on voidtrace: 21 of 27 facts were wording, which exploded to 3670 findings. Fixed by requiring code-shaped tokens, rejecting inflection, and refusing remames whose old identifier still appears on added lines.
- **v1 homonyms**: sitbone `SiteObserver.threshold = 0.7` is not PresenceArbiter's old `0.4`. Fixed by treating "same name, different bound literal" as a different symbol.
- **v1 historical docs**: ADR-0019 states the old fact *because it is the decision record of the change*. Fixed by downranking files that also contain the new value.
- **v1 nested git**: parent `git ls-files` cannot see `nested/inner/note.md`. Fixed by walking inner worktrees when searching the disk tree.
- **v1 / v2 small integers**: coverage `5 → 6` matched README `` `5` for an internal failure ``. Fixed by refusing prose-bound common numbers (0–10) as facts.
- **Still failing**: no language parser, so `Some(10)` / Swift type annotations are regex-special-cased; unknown syntax will miss bindings. No understanding of "this contract is a different code path." Japanese `タイムアウト` matches `timeout` only via a tiny alias table. Historical trees do not recurse nested repos (no disk checkout).

## Suggested mutations

- **clove**: partition the current dirty hunks into independently commitable atoms (the other Gen-1 survivor).
- **twinlag**: encode/decode, start/stop, left/right pairs ranked by how far apart they last changed.
- Pre-commit / `--staged` CI gate with SARIF.
- Tree-sitter bindings so facts are symbols, not regex pairs.
- `zanei blame <path>:<line>`: invert the verb — given a claim, show the diff that falsified it.
- Learn aliases from the repo (`timeout`/`タイムアウト`, `intent`/`意図`) instead of a hard-coded table.

## Kill / keep

**Keep.** The interaction is a new Unix verb (diff in, leftover claims out, linter exit codes), it found a real version skew in kizu and a real stale test description in sitbone, and the first improvement was forced by an ugly real commit, not by taste. Do not grow it into a review platform; keep it a filter.
