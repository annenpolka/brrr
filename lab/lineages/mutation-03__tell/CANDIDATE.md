# mutation-03 — tell

## Primitive

`tell` takes two git trees and emits the shortest distinguishing predicates (`exists` / `grep` / `path` / `content`) that are true on one side and false on the other.

`held` walks history given a predicate. `tell` is the inverse: two snapshots in, the predicate you would have typed out.

## Why this might not exist

Diff shows the delta. Bisect / held need you to already know the question. The recurring annoyance is the other direction: *I am looking at two trees and I do not know what to grep.* Feature islands, merge-vs-topic, "what unique name did this PR introduce?", a Japanese policy sentence you cannot guess.

There is no Unix verb whose value is a **minimal unary predicate** that splits two trees. `git diff --stat` is a file list, not a question.

Discarded as too conventional: wrapping `git diff --name-status`, ranking files by churn, dumping unique lines.

## How to run

```bash
./tell --help
./demo.sh
./tell -C /path/to/repo HEAD~1 HEAD
./tell -C /path/to/repo --held --kind exists,grep 14b1d6e HEAD
./tell -C /path/to/repo --json 70b450d^ 70b450d
./tell HEAD :worktree
```

## Empirical transcript

### Before the improvement

Naive "shortest" meant sliding CJK windows and leftover camel humps. Real queries:

```
$ ./tell -C sitbone --oneline --limit 6 14b1d6e^ 14b1d6e
grep    A  13  grep -F 'がるパ'
grep    A  13  grep -F 'が一瞬'
grep    B   9  grep Apps
grep    B   9  grep Drag
exists  B  23  exists *FocusRiverView*
# FocusRiverView as grep: dominated away by the prefix "Focus", then hidden by limit.

$ ./tell -C tenaoshi --oneline --limit 6 70b450d^ 70b450d
grep    B  13  grep -F 'い改変'
grep    B  13  grep -F 'けに調'
# 第一級 drowned. Content lines still had it, 80 characters down.

$ ./tell -C sitbone --cover 14b1d6e HEAD
cover
  B   9  grep site     22 files
  B   9  grep base     11 files
# occupancy-greedy cover: a 4-letter accident beat WindowTitleParser / FocusRiverView.
```

### After the improvement

Well-formed names only (no CJK n-grams, no interior camel humps). Rank: name-like, then path-stem, then length. Cover prefers stems over occupancy.

```
$ ./tell -C sitbone --cover 14b1d6e^ 14b1d6e
cover
  B  19  grep FocusRiverView   1 file
  B  15  grep onSettings       2 files
TRUE on B only
  exists *FocusRiverView*
  grep FocusRiverView

$ ./tell -C sitbone 70ec7df^ 70ec7df
TRUE on A only
  exists *FocusRiverView*
  grep FocusRiverView
# death certificate is the same predicate, opposite side.

$ ./tell -C sitbone 14b1d6e HEAD
cover
  B  17  grep SiteObserver        16 files
  B  18  grep SensorReading        8 files
  B  19  grep SessionProfile       7 files
  B  22  grep WindowTitleParser    7 files
  A  19  grep FocusRiverView       1 file
# the island's unique name survives a 72-path delta against HEAD.
# git log -- Sources/SitboneUI/FocusRiverView.swift  → empty.

$ ./tell -C voidtrace --cover 66d6fa1 6e3368b
cover
  B  34  grep -F finite-breakpoint-analysis   10 files
  B  22  grep -F run-breakpoint                5 files
  B  27  exists *finite-breakpoint.*           3 files
# "breakpoint" is already true on A (the slice commit). tell refuses it.

$ ./tell -C kizu --cover e1098c8^ e1098c8
cover
  B  15  exists *CLAUDE*
  B  12  exists *.yml
  B  13  grep awaiting
# birth of CLAUDE.md + CI, plus the one token that marks the main.rs edit.

$ ./tell -C kizu --limit 3 04adde1^ 04adde1
cover
  B  10  grep js_ts          7 files
  B  14  grep read_file      4 files
exists *js_ts* / *jsx-tsx.test* / *0020-tree-sitter-for-jsx-tsx*

$ ./tell -C tenaoshi 70b450d^ 70b450d
cover
  B  15  grep -F MAN-023     4 files     # contract id, every changed path
TRUE on B
  grep -F '第一級'            3 files     # the policy word
```

`./demo.sh` — 18 assertions, exit 0.

## Dogfood targets

- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` — FocusRiverView birth, death, and island-vs-HEAD (`git log -- path` empty)
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` — finite-breakpoint implementation vs a slice that already contains the word "breakpoint"
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — CLAUDE.md birth; jsx/tsx feature commit
- `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` — Japanese policy `第一級` / contract `MAN-023`
- synthetic fixture in `demo.sh`: oscillating path, rename with spaces, `計画.md`, nested git, `:worktree` dirty resurrection, empty repo

## Surprises

- Shortest-as-substring is a trap in Japanese. `がるパ` is uniquely absent from the other tree and three characters long. It is also useless. "Shortest *well-formed* predicate" is a different primitive than "shortest unique n-gram".
- Covering occupancy fights characteristic names. `grep site` split sitbone island-vs-HEAD in 22 files and beat `FocusRiverView`. After ranking path-stems first, the cover reads like a module index.
- `grep breakpoint` is the question a human types for voidtrace and it is *wrong*: the previous commit already said it. The distinguishing names are `finite-breakpoint-analysis` and `run-breakpoint`. tell's job is to refuse the question you thought of.
- A rename with shared blob content produces exists on both sides and no grep. That is correct (path identity) and surprising if you wanted content lineage — the same surprise `held exists` documented.
- tenaoshi's *shortest cover* is `MAN-023` (4 files), not `第一級` (3 files). The contract id is a better splitter than the slogan. Both are true; cover picked the one that explains the whole delta.
- Exclusive `*.yml` / `*.md` globs are shorter than the filename. kizu's CI birth is `exists *.yml` if that side is the first yaml. Characteristic and shortest disagree; we keep both kinds.

## Failures

- v1 CJK sliding windows drowned `第一級` and `FocusRiverView`.
- v1 dominate() let `Focus` delete `FocusRiverView`, then hid `Focus` for not being name-like — the useful token vanished from both lists.
- v1 cover maximized file count: `grep site` / `grep base` on a 72-path island.
- Cover lists for large deltas (voidtrace 41 paths, sitbone island 72) still grow a tail of unique fixture filenames. Glob compression of `*scenario-patch*` is incomplete.
- `path` kind still leaks common words (`grep weak -- file`) into the quota; they are ranked last but they print.
- Distant trees (island vs HEAD) emit many true predicates. `--limit` / `--cover` / `--kind` are required; the default human form is busy.
- Binary-only modifies have no unary grep; they remain unexplained except by "blob differs", which is not a held predicate.
- `exists` does not follow renames (same as held).
- Full-tree token uniqueness loads both blobs. Fine for these repos (~60–260 files), not argued for a monorepo.

## Suggested mutations

- Emit a `held` command line that *walks* the predicate just found (`tell A B | held --range A..main`) so reverse-and-forward is one pipe.
- Shortest *set* under a length budget rather than greedy cover.
- `--follow` so a rename is one identity, not two exists.
- Phrase-mode for English (unique 2-grams) to match what CJK runs already give.
- Index vs worktree vs stash as first-class sides without magic refs.
- Cache tree token sets in `.git/tell-cache/`.

## Flipped assumption: bought and lost

Ancestor `held` assumed **the user already knows the predicate**.

**Bought**

- You can start from two trees you are already staring at. No need to invent `FocusRiverView` or `第一級` before asking.
- The output *is* the input of held: composable, unary, checkable. `--held` prints the language.
- Discovers the predicate that `git log -S` / bisect would have needed, including the one that is *not* the word in the commit subject (`breakpoint` vs `run-breakpoint`).
- Works on deleted-path islands that `git log -- PATH` erases.

**Lost**

- Time disappears. No eras, no "when". That is still held's job; tell only names the question.
- "Shortest" is not unique. N-grams, stems, contract ids, slogans all split the trees. We had to impose well-formedness or the primitive becomes unique-substring search.
- Two snapshots, not a walk. A three-state reincarnation (`TOKEN_A` in keep.txt then other.txt) is two pairwise tells, not one occupancy interval.
- No `exec`. Arbitrary predicates stay on the held side; tell only invents exists/grep/path/content.
- Far-apart trees produce a cloud of true predicates. held's answer is one boolean time series; tell's answer is a ranked list that needs a limit.

## Kill / keep

**Keep.** It is a small verb, it is not a diff wrapper, and on the first real deleted file it emitted `grep FocusRiverView` — the predicate held was built to walk — without being told the name. The v1→v2 change was forced by sitbone/tenaoshi output, not polish.
