# First Selection — Heretic

Judge: Heretic. Stance: keep a tool only if the *interaction* is unfamiliar. A new name on grep, diff, env, cmp, or mergetool is a kill even when the demo is green. Multiple KEEP is required; polish is not a score.

All seven `./demo.sh` runs and shipped test suites were executed in the candidate directories on 2026-09-02. Every demo exited 0. Every test suite exited 0. Empirical credibility below is therefore not a differentiator; the cut is the remaining operation after the name is stripped.

Unix-shaped disagreement is called out per candidate. The live disagreement is **hits** (Unix would keep an exit-code hole; this judge kills grep-with-the-empty-bit-flipped) and **capdiff** (Unix would keep a capture/diff/replay trio; this judge kills named dumps).

---

## candidate-01__whence — KEEP

Shipped CLI: `./whence` (`python3 whence`; zsh already owns the word).

Ran: `./demo.sh` exit 0 (includes a real two-branch `git merge` and 18 unittests). `python3 -m unittest discover -s tests -v`: 18 tests, OK.

The interaction that is not mergetool: a hybrid sidecar whose contested spans must be tagged `[ours:…]` / `[theirs:…]`, untagged text must be a substring of *both* parents, and a JSON provenance list names the parent of every kept contested span. Untagged mix leaves the conflict markers in the file and writes no `.prov`.

```text
[ours:color = red]
size = [theirs:2]
```

resolved to `color = red` / `size = 2` with spans `ours "color = red"`, `theirs "2"`. The same sidecar without tags:

```text
region 1/1 lines 2-8 (HEAD vs feature): untagged text "color = red\nsize = 2\n"
is not a substring of ours or theirs (unmarked mix or invented text).
```

exit 1, file still conflicted. `git merge-file -p --ours` on the same parents printed a blob and stopped.

| Axis | Score |
| --- | --- |
| Novelty | 4 |
| Utility | 4 |
| Primitive strength | 5 |
| Composability | 4 |
| Empirical credibility | 5 |
| Evolution potential | 4 |
| Reality-Stripped Strength | 4 |

**Novelty (4).** Conflict markers are old. The contract is not: you may not emit a hybrid unless every non-common span is parent-tagged, and the product is the resolved text *plus* the parentage list. That is not `git checkout --ours` with extra JSON. Whole-side paste into `--hybrid` is refused on purpose (`--ours` exists; an untagged ours copy is not a hybrid). Diff3 `|||||||` is refused, not papered over. The tagging language is the unfamiliar part.

**Utility (4).** Real merge of overlapping `value = 1` vs `value = 2` produced two-parent markers; `whence resolve --ours` kept `value = 1\n` and recorded `mode: ours`. Messy three-region fixture with nested `\"` and no trailing newline resolved, and a short sidecar named the missing region (`region 3/3 … MISSING tagged block`) instead of dying opaquely. This is a thing you would run on a conflicted file. It is not a mergetool driver yet.

**Primitive strength (5).** One primitive: every kept contested span has an explicit parent, or the tool refuses. Report, ours, theirs, per-region `--choice`, and tagged hybrid are all that primitive. No JS/YAML intelligence, no TUI, no invented merge. Strong and small.

**Composability (4).** Provenance is JSON on stdout and `FILE.prov`. `--prov -` skips the sidecar. `--output` and `--hybrid -` are filter-shaped. Hybrid blocks split on `%%`. The tagging language is a second syntax you have to learn; Unix would score this down for not being a pure text filter. The heretic keeps the language because it *is* the interaction.

**Empirical credibility (5).** Demo covered ours, theirs, tagged hybrid, untagged refusal, diff3 refusal, `git merge-file` contrast, a throwaway two-branch merge, messy quotes, short sidecar, wrong-parent tag, xxd tail (`23 2065 6f66` = `# eof` with no final NL). 18 tests against the shipped file, including `test_untagged_ours_copy_refused`.

**Evolution potential (4).** Natural next cuts: mergetool/`merge` driver that writes `.prov`, git notes instead of a sidecar, SequenceMatcher-proposed tags, optional strip of a diff3 ancestor hunk while still tracking only two parents. Death mode is becoming a semantic merge engine. The refuse-unmarked-mix contract should stay.

**Reality-Stripped Strength (4).** Ignore the name. Operation: parse `<<<<<<<` / `=======` / `>>>>>>>`, accept only an explicit parent choice per region or per tagged span, write text, write parentage. Nearest ordinary workflow: edit the markers, or `git merge-file --ours|--theirs`, or a mergetool. What is lost if that workflow replaces this: the per-span parent list, and the hard fail on unmarked mix (ordinary tools will happily emit `color = red` + `size = 2` with no record that those tokens came from different parents). That loss is real.

Unix would likely KEEP too, but would grumble that `--ours` is `git checkout --ours`. The heretic KEEP is for the tagged hybrid and the refusal, not for whole-hunk ours/theirs.

---

## candidate-02__stated — KEEP

Shipped CLI: `./stated`.

Ran: `./demo.sh` exit 0. `python3 -m unittest tests.test_stated -v`: 14 tests, OK.

The interaction that is not `rg timeout`: the observable is a *disagreement pair* (declaration site vs contradicting site), or an honest non-comparison. Demo, disagree fixture (`config.yaml` `timeout: 5` vs `app.py` `timeout = 10`):

```text
status: DISAGREE
disagreement:
  declared     5	config.yaml:1	timeout: 5	value=5
  contradicted 10	app.py:3	timeout = 10	value=10
exit: 2
```

Interpolation vs `os.getenv("WAIT")` printed `UNKNOWN` / `not comparable: interpolation` / `not comparable: call`, exit 0. Comments and docstrings listing `99` were labeled and ignored; real `int timeout = 5` still counted.

| Axis | Score |
| --- | --- |
| Novelty | 3 |
| Utility | 4 |
| Primitive strength | 3 |
| Composability | 4 |
| Empirical credibility | 5 |
| Evolution potential | 3 |
| Reality-Stripped Strength | 3 |

**Novelty (3).** Walking a tree for `KEY:` / `KEY=` is grep. The cut that is not grep is: pair comparable scalars across config-shaped files and source-shaped files, refuse to compare interpolations and calls, and treat comment hits as a third list. That is a small unfamiliar output, not a new search. Close to a rename; the pair keeps it alive.

**Utility (4).** “It only broke after I changed the timeout” is a real session. Exit 2 on comparable disagreement is something a script can branch on. Nested keys (`server.timeout`) are invisible; that is an honest limit, not a hidden one.

**Primitive strength (3).** The primitive is the disagreement pair, not the hit list. Implementation is line regex plus a comment tracker, not parsers. Same-side contradiction is handled. It will lie on `/* x */ int timeout = 5;` on one line. Strong enough to keep, not a new law of nature.

**Composability (4).** `stated KEY [DIR]`, `--json`, exit 0/1/2. JSON carries pairs, declarations, assignments, comments. Pipeable. Does not try to repair.

**Empirical credibility (5).** Five fixtures in the demo (disagree, agree, declared-only, unknown, comments) plus JSON. 14 tests, including identifier-boundary (`timeout` vs `timeout_ms`) and comment separation. Dogfood of the comments fixture is visible in the output I ran: four comment hits, two real assignments at 5, status AGREE.

**Evolution potential (3).** Nested key paths, case-insensitive env keys, typed Python assignments. The death is “becomes a config linter / typechecker.” Keep the pair; do not add auto-fix.

**Reality-Stripped Strength (3).** Ignore the name. Operation: given a key, find declaration-shaped lines and assignment-shaped lines, compare literals when both look like scalars. Nearest ordinary workflow: `rg KEY` in yaml and py, then read both. What is lost: automatic pair emission, exit 2, UNKNOWN instead of a false equal, comment hits parked off to the side. You can do this by eye on a small tree. The tool is the eye-skip, not a new object.

Unix would KEEP this as a useful composition and might score novelty 2. This judge keeps it for the pair-as-observable, not for the scanner. Mild disagreement on how new it is, not on the verdict.

---

## candidate-03__owes — KEEP

Shipped CLI: `./owes`.

Ran: `./demo.sh` exit 0. `python3 tests/test_owes.py -v`: 10 tests, OK.

The interaction: a change (unified diff, or before/after snapshots) plus the remaining tree, then two obligation kinds — removed identifiers still mentioned, and companion paths remaining docs still require.

Deleted-function fixture:

```text
unkept references:
  validate_input
    README.md:3: Call `validate_input` before saving user data.
exit: 2
```

Missing-companion fixture (after dogfood: `must run \`make test\`` is no longer a file):

```text
missing companions:
  SECURITY.decision.md
    named in docs/CONTRIBUTING.md:5: MUST exist: SECURITY.decision.md
  docs/adr.md
    named in docs/CONTRIBUTING.md:9: must read `docs/adr.md`
  docs/threat-model.md
    named in docs/CONTRIBUTING.md:7: required file: docs/threat-model.md
exit: 2
```

Clean helper-delete: `no unkept obligations`, exit 0.

| Axis | Score |
| --- | --- |
| Novelty | 3 |
| Utility | 3 |
| Primitive strength | 3 |
| Composability | 4 |
| Empirical credibility | 5 |
| Evolution potential | 4 |
| Reality-Stripped Strength | 3 |

**Novelty (3).** “Names the diff deleted that remaining files still mention” is `git diff` plus `rg`. The slightly unfamiliar question is *what does this change still owe*, including a missing companion named by remaining docs. The `MUST exist:` / `required file:` phrases are a planted mini-DSL — the fixture was written for the matcher. That is a smell, not a kill. The leftover-identifier scan is the realer half.

**Utility (3).** Stale README after deleting `validate_input` is a review moment. A moved function is still reported (false unkept). Comment-only leftovers count. Companion check only looks at `*.md`. Useful on the fixtures; noisy on a real rename.

**Primitive strength (3).** Two related obligations, one scan. Identifier extraction is `def|class|function|fn|…` and `CONST =`. Companion paths are three regexes plus a filename-like filter (`/` or `.`, no spaces) that existed because the first demo falsely owed `make test`. The primitive is real; the extraction is thin.

**Composability (4).** `owes DIR` with two snapshot layouts, or `--tree` + `--diff`. `--json`. Exit 0/2/1. Tests invoke the shipped process. Fits a pre-commit or review pipeline without becoming a policy engine.

**Empirical credibility (5).** Demo asserted three fixtures. Tests cover JSON shape, `--tree/--diff`, plus-line changelog skip (`Removed validate_input` in CHANGELOG is not an unkept ref; leftover README still is), usage errors. I re-ran all of that.

**Evolution potential (4).** Skip identifiers that still have a definition in the remaining tree (kills the move false-positive). Optionally ignore comment-only mentions. Search tests for MUST-like phrases. Bind missing companions to files the diff actually touched. Those mutations deepen the same primitive. Death: CVE/ticket oracles.

**Reality-Stripped Strength (3).** Ignore the name. Operation: parse removed identifiers from a unified diff; search the remaining tree; also look in remaining markdown for required-path phrases and test existence. Nearest ordinary workflow: `git diff` + `rg validate_input` + `test -f`. What is lost: the change and the leftover mentions as one report, and the companion miss as a first-class row. Most of the value is recoverable with two Unix tools; the bundling is the delta.

Unix would KEEP this more warmly (it is exactly a composition). This judge KEEP is reluctant: the identifier half is familiar, the companion half is half-invented. Still a survivor because the *question* is not “grep the repo”, it is “what did this change fail to keep”.

---

## candidate-04__capdiff — KILL

Shipped CLI: `./capdiff`.

Ran: `./demo.sh` exit 0. `python3 -m unittest discover -s tests -v`: 11 tests, OK. Empirically fine. Conceptually a named folder of dumps.

Demo captured fixture env-a vs env-b, printed ENV modified `API_KEY` local vs remote, FILES extra `extra.txt`, exit 2; replay printed `local-ci-key` / `remote-ci-key`; missing `.env` captured as empty env map and diffs as `ENV missing: API_KEY=…`.

| Axis | Score |
| --- | --- |
| Novelty | 2 |
| Utility | 3 |
| Primitive strength | 2 |
| Composability | 3 |
| Empirical credibility | 5 |
| Evolution potential | 3 |
| Reality-Stripped Strength | 2 |

**Novelty (2).** Named snapshot of `.env` plus sha256 of relative paths, then diff, then `exec` with overlayed env. That is `sha256sum` + `diff` + `env KEY=val cmd` with a `.capdiff/NAME` directory as the label. “Labeled capture not ad-hoc dump” is a filing convention, not a new operation. ENV vs FILES both reporting `.env` (parsed keys *and* bytes, including comments) is a mild twist, not an unfamiliar interaction.

**Utility (3).** Local-CI key vs remote-CI key is a real “why did this job see a different secret” moment. Replay does not restore file bodies — capture never stored them — so `--files` writes only `.env`. Overlay does not unset host vars absent from the capture. Useful as a reminder; not a reproducer.

**Primitive strength (2).** The compared object is a directory of `{env map, file hashes}`. That is a bundle, not a primitive. Three subcommands (capture / diff / replay) already want to be a small product. Replay is `os.execvpe` after copying env.

**Composability (3).** Names, exit 2 on delta, JSON manifest on disk. You can `capdiff diff a b` in CI. You cannot compose it as a filter. The store is hidden state in cwd.

**Empirical credibility (5).** Demo and 11 tests did what they claimed, including “missing `.env` is empty, not crash” and env-only replay in a tree that has no live `API_KEY`. Green is not a keep.

**Evolution potential (3).** Could grow a real snapshot (store bodies, `env -i` unset, include/exclude globs, env-from-`os.environ`). Those mutations make it rsync/direnv. The current object is too thin to deepen without becoming those tools.

**Reality-Stripped Strength (2).** Ignore the name. Operation: copy `.env` if present, hash files, diff two such records, overlay env and exec. Nearest ordinary workflow: `diff -ru`, `sha256sum`, `env`. What is lost: a name on the pair so you do not forget which dump was local. That is bookkeeping. If the ordinary workflow replaces this tool, almost nothing operational is gone; you still see `API_KEY` differ and `extra.txt` exist.

**Unix disagreement.** A Unix judge is likely to KEEP this as a tidy composition (three verbs, text output, exit 2). This judge kills it: familiar tools with a store directory. The experiment does not need another named `diff`.

---

## candidate-05__envfrom — KEEP

Shipped CLI: `./envfrom`.

Ran: `./demo.sh` exit 0. `python3 -m unittest tests.test_envfrom -v`: 14 tests, OK.

The interaction that is not `printenv`: a key can be inherited, assigned at a dotenv `file:path:line` (including emptying it), or unset — and `--run` without `--load` prints the *would-apply* override while the child still has the inherited value.

With process `LIBRARY_PATH=/usr/local/lib:/usr/lib` and fixture `.env` line 2 `LIBRARY_PATH=`:

```text
LIBRARY_PATH
VALUE=
SOURCE: file:…/fixtures/empty-override/.env:2
EMPTY_OVERRIDE: yes
INHERITED: /usr/local/lib:/usr/lib
```

`--fail-empty` exit 2. `--run` without `--load`: child `LIBRARY_PATH=/usr/local/lib:/usr/lib`. `--run --load`: child `LIBRARY_PATH=''`. Quoted-export fixture: `export PREFIX`, `"hello world"`, `'Ada Lovelace'`, inline `#` comment stripped, `KEY=""` still empty-override, `"# not a comment"` kept.

| Axis | Score |
| --- | --- |
| Novelty | 4 |
| Utility | 4 |
| Primitive strength | 4 |
| Composability | 4 |
| Empirical credibility | 5 |
| Evolution potential | 3 |
| Reality-Stripped Strength | 4 |

**Novelty (4).** `env` prints values. `direnv status` prints loading. Neither answers “which file line would wipe `LIBRARY_PATH`, and what did I inherit.” Empty file assignment vs inherited process value, plus would-apply vs did-apply (`--run` without `--load`), is an unfamiliar pair of facts in one block. Not `env` with a new name.

**Utility (4).** People paste `.env` next to inherited `LIBRARY_PATH` / `PYTHONPATH` and then cannot tell why a child is empty. `--fail-empty` is a gate. `--load` is an explicit apply, not a silent side effect of reporting. PATH dump is honest and noisy; the interesting row is next to it.

**Primitive strength (4).** Per-key source: `env` | `file:<path>:<line>` | `unset`, with empty-override as a first-class flag and inherited value retained. Later files win (`.env.local`). That is one primitive. `--run`/`--load` are the same primitive applied to a child, not a second product.

**Composability (4).** Keys as args, `--dir`, `--fail-empty` exit 2, `--run -- CMD` exec. Block-formatted stdout is a bit rigid (newlines in values would smash it) but grepable. Does not edit files.

**Empirical credibility (5).** Demo hit empty-override, fail-empty, would-apply vs load, quoted/export/inline-comment/empty-quoted. 14 tests including `.env.local` wins and `--fail-empty` blocking exec.

**Evolution potential (3).** Source *chain* when both `.env` and `.env.local` set the key; relative SOURCE paths; newline encoding in VALUE. Interpolation / `KEY+=` is how it becomes direnv. Keep provenance; do not become a loader with extra verbs.

**Reality-Stripped Strength (4).** Ignore the name. Operation: for each requested key, say whether the effective value is process env, a dotenv assignment at file:line, or unset, and whether a file assignment is empty (including the inherited value it would wipe). Nearest ordinary workflow: `printenv KEY` plus `cat .env`. What is lost: the empty-override fact when the process still has a value (because the loader has not run), the file:line, and the would-vs-did split. `printenv` cannot show a wipe that has not happened yet. That is the whole point.

Unix would KEEP. Agreement.

---

## candidate-06__same — KEEP

Shipped CLI: `./same`.

Ran: `./demo.sh` exit 0. `python3 -m unittest tests.test_same -v`: 13 tests, OK.

The interaction: identity kind is a required argument. Omit it and the tool lists the kinds and dies. Two empty files on this volume:

```text
$ ./same fixtures/empty/a fixtures/empty/b
usage: same --inode|--bytes|--json A B
available kinds: inode, bytes, json
exit 1

$ ./same --inode fixtures/empty/a fixtures/empty/b
DISTINCT inode 16777233:128975855 16777233:128975856
exit 2

$ ./same --bytes fixtures/empty/a fixtures/empty/b
IDENTICAL bytes sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
exit 0
```

Hardlink: `IDENTICAL inode 16777233:128975858`. JSON key order: `IDENTICAL json {"a":2,"b":1}`. Missing path and binary `--json` are one-line named errors, not tracebacks. `--inode` uses `lstat` (symlink vs target DISTINCT); `--bytes` follows.

| Axis | Score |
| --- | --- |
| Novelty | 3 |
| Utility | 3 |
| Primitive strength | 4 |
| Composability | 5 |
| Empirical credibility | 5 |
| Evolution potential | 3 |
| Reality-Stripped Strength | 4 |

**Novelty (3).** `--bytes` is `cmp`/`sha256`. `--inode` is `[ a -ef b ]` / `stat`. `--json` is `jq -S`. The unfamiliar interaction is the *refusal to guess*. “Are these the same file?” silently means inode or bytes or JSON depending on who typed the pipeline; this CLI will not join that conspiracy. The operations are old; the required kind is not a rename, it is a constraint. That is enough.

**Utility (3).** You already have the three tools. You do not already have a thing that *won't* let you mix them. The demo of two empties flipping IDENTICAL/DISTINCT by kind is the teaching and the use. Hardlinks are not preserved by git; demo/tests recreate them. Fine.

**Primitive strength (4).** One kind, two paths, IDENTICAL or DISTINCT, or refuse. Mixing kinds is usage. That is a strong small primitive. Implementation is ~90 lines and does not apologize.

**Composability (5).** One required flag, two operands, exit 0/2/1, one stdout line. Filter-shaped. Kind name is in the output so a log is not ambiguous later.

**Empirical credibility (5).** Demo: omit-kind, hardlink, two empties both ways, JSON order, symlink follow, missing file, binary-vs-json. 13 tests including two-kinds-at-once refuse, JSON parse error, inode symlink vs file.

**Evolution potential (3).** N-path table still under one kind is the honest mutation. `parse_float=Decimal` so `1.0` and `1` stay distinct. Death: flag soup around `cmp` (follow/no-follow as extra kinds without discipline, extra identity kinds until it is `diff`). Kill it the day the kind is optional.

**Reality-Stripped Strength (4).** Ignore the name. Operation: compare two local names under exactly one explicit identity kind; refuse if omitted or mixed. Nearest ordinary workflow: `stat` / `cmp` / `jq -S` chosen by the human. What is lost if that workflow replaces this: the forced naming. Ordinary tools will happily answer a different question than the one you thought you asked. The lost thing *is* the product. That is why this is not a thin wrapper even though each kind is a thin wrapper.

Unix would KEEP, possibly as the poster child. Agreement on verdict. Unix might call the operations the point; this judge calls the refusal the point.

---

## candidate-07__hits — KILL

Shipped CLI: `./hits`.

Ran: `./demo.sh` exit 0. `python3 -m unittest tests.test_hits -v`: 19 tests, OK. The most thoroughly tested grep in the set.

Demo: hits print `file:line:text` exit 0; miss prints `0 matches` exit 0 and `&& echo still-running` still runs; literal `n.edle` is not a regex; `--regex '['` exit 2; no args exit 1; unreadable DIR exit 3; NUL binary skipped; `--glob '*.md'` miss is still success.

| Axis | Score |
| --- | --- |
| Novelty | 1 |
| Utility | 2 |
| Primitive strength | 2 |
| Composability | 3 |
| Empirical credibility | 5 |
| Evolution potential | 2 |
| Reality-Stripped Strength | 1 |

**Novelty (1).** Search a tree for a substring. That is grep. The claimed delta is exit 0 on zero matches so `hits PAT && next` still runs, with exit 2 on bad regex and exit 3 on unreadable root. That is grep’s empty-bit flipped, plus a tiny status taxonomy. `grep … || true` is the ordinary move; it collapses miss and error, which this tool un-collapses. Un-collapsing an exit code is not an unfamiliar interaction. It is a policy. Default output is grep’s `file:line:text`. `--glob` is fnmatch. Binary skip is grep-ish (grep at least *says* “Binary file matches”; after dogfood this tool skips silently, which is fine and still grep).

**Utility (2).** `set -e` plus “absence is fine” is a real footgun. People already write `grep … || true` or `rg --quiet || [ $? -eq 1 ]`. Distinguishing miss from bad pattern from I/O is correct and almost nobody will type `hits` instead of `rg`. The demo’s `still-running` is the entire user-facing delta.

**Primitive strength (2).** “Empty search is success” is a policy on grep, not a primitive. The 0/2/3 split is the only structure. Nested EACCES is skipped, so a tree you cannot fully read can still print `0 matches` / exit 0 — the taxonomy does not even apply recursively.

**Composability (3).** `hits PAT && next` is the composition it exists for. stdout on hit, `0 matches` on miss (so you cannot tell glob-miss from content-miss without reading text). Exit codes are the composable surface. That surface is real and still not enough to keep a grep clone.

**Empirical credibility (5).** 19 tests, unreadable DIR via `chmod 000`, binary-only tree as empty success, `.git` skip, glob miss, `&&` after miss. Best test suite, wrong object.

**Evolution potential (2).** Quiet empty, count on stderr, nested EACCES warnings, gitignore globs. Every mutation makes it GNU grep. There is nowhere to evolve except into the tool it is renaming.

**Reality-Stripped Strength (1).** Ignore the name. Operation: recursive substring/regex search; zero matches is exit 0; bad pattern 2; unreadable root 3. Nearest ordinary workflow: `grep -R` / `rg`, or `grep … || true`. What is lost: the 2-vs-3 distinction, and not having to write `|| true`. If grep replaces this, you lose almost nothing you would actually compose on. Familiar tool, new name. Kill.

**Unix disagreement (the live one).** A Unix judge is likely to KEEP `hits`. Empty-as-failure is a famous `set -e` footgun; splitting miss / bad pattern / I/O is the Unix-shaped hole; the CLI is small and honest. This judge still kills it. Exit-code hygiene on grep is not an unfamiliar interaction. The experiment should not spend a survivor slot on a searcher.

---

## Summary

| Candidate | Novelty | Utility | Primitive | Composability | Empirical | Evolution | Reality-Stripped | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| candidate-01__whence | 4 | 4 | 5 | 4 | 5 | 4 | 4 | **KEEP** |
| candidate-02__stated | 3 | 4 | 3 | 4 | 5 | 3 | 3 | **KEEP** |
| candidate-03__owes | 3 | 3 | 3 | 4 | 5 | 4 | 3 | **KEEP** |
| candidate-04__capdiff | 2 | 3 | 2 | 3 | 5 | 3 | 2 | **KILL** |
| candidate-05__envfrom | 4 | 4 | 4 | 4 | 5 | 3 | 4 | **KEEP** |
| candidate-06__same | 3 | 3 | 4 | 5 | 5 | 3 | 4 | **KEEP** |
| candidate-07__hits | 1 | 2 | 2 | 3 | 5 | 2 | 1 | **KILL** |

KEEP (5): **whence**, **stated**, **owes**, **envfrom**, **same**.

KILL (2): **capdiff**, **hits**.

What survived is not polish. **whence** keeps a parent-tagged resolve that mergetools throw away. **envfrom** keeps empty-override vs inherited and would-apply vs did-apply. **same** keeps the refusal to guess identity. **stated** keeps the disagreement pair (not a hit list). **owes** keeps “what this change still owes,” even though half of it is grep-after-diff.

What died is a named `diff` of env+hashes and a grep whose entire personality is exit 0 on miss.

Execution (all in the candidate directories, 2026-09-02):

| Candidate | `./demo.sh` | tests |
| --- | --- | --- |
| whence | 0 | 18 OK |
| stated | 0 | 14 OK |
| owes | 0 | 10 OK |
| capdiff | 0 | 11 OK |
| envfrom | 0 | 14 OK |
| same | 0 | 13 OK |
| hits | 0 | 19 OK |
