# First Selection — Reality-Stripped

Judge: Reality-Stripped. Date: 2026-09-02.

Scope: shipped CLIs under `lab-hdd/lineages/candidate-01__whence` … `candidate-07__hits`. Names and branding are ignored; the question is what operation remains if the label is peeled off.

Method: read README.md and CANDIDATE.md; inspect the shipped CLI; run `./demo.sh` and the unittest suite in each worktree. Did not read `EVOLUTION_REPORT.md`, `lab/`, previous lineages, previous judge reports, or `.hdd/` transcripts.

Empirical rule: a score on Empirical credibility is taken from this run, not from README claims. All seven demos exited 0. All seven test suites exited 0.

| Candidate | Demo | Tests | Observed in this run |
| --- | --- | --- | --- |
| 01 | `./demo.sh` exit 0 | 18 OK | Tagged hybrid wrote `color = red` / `size = 2` with spans `ours`/`theirs`. Untagged mix left markers, exit 1. Real two-branch `git merge` then `--ours` kept `value = 1`. `git merge-file --ours` wrote a blob and stopped. |
| 02 | `./demo.sh` exit 0 | 14 OK | `timeout: 5` vs `timeout = 10` → DISAGREE exit 2. `${WAIT}` vs `os.getenv("WAIT")` → UNKNOWN exit 0. Docstring/`/* */` `99` labeled comments; `int timeout = 5` counted as assignment. |
| 03 | `./demo.sh` exit 0 | 10 OK | Deleted `validate_input` still in README → exit 2. Remaining docs naming absent `SECURITY.decision.md` / `docs/adr.md` / `docs/threat-model.md` → exit 2. Clean helper delete → `no unkept obligations` exit 0. |
| 04 | `./demo.sh` exit 0 | 11 OK | Named captures `a`/`b`/`none`. Diff `a b` exit 2: ENV `API_KEY` local vs remote, FILES extra `extra.txt`, FILES modified `.env` hashes. Replay printed `local-ci-key` then `remote-ci-key`. Missing `.env` captured as empty map. |
| 05 | `./demo.sh` exit 0 | 14 OK | `LIBRARY_PATH=` at `.env:2` reported EMPTY_OVERRIDE with inherited `/usr/local/lib:/usr/lib`. `--run` without `--load`: child kept inherited. `--run --load`: child `LIBRARY_PATH=''`. `--fail-empty` exit 2. |
| 06 | `./demo.sh` exit 0 | 13 OK | Omit kind → usage exit 1. Hardlink IDENTICAL inode. Two empty files DISTINCT inode, IDENTICAL bytes (`e3b0c442…`). JSON key order IDENTICAL. `--bytes` follows symlink. Missing path and binary-as-JSON are path-named errors, no traceback. |
| 07 | `./demo.sh` exit 0 | 19 OK | Miss prints `0 matches` exit 0 and `&& still-running` fires. Bad regex exit 2. Unreadable DIR exit 3. NUL binary skipped; text hit kept. |

Multiple KEEP is required. This report keeps six and kills one. Kill is for a missing remainder, not for lack of polish.

---

## candidate-01 — parent-tagged two-way resolve + per-span parent ledger

Shipped file: `whence` (invoked as `python3 ./whence`; a shell builtin of the same word is irrelevant).

### 1. Operation that remains

Parse `<<<<<<<` / `=======` / `>>>>>>>` regions. Resolve only by an explicit parent choice: whole-side ours, whole-side theirs, per-region choice list, or a hybrid sidecar in which every contested span is tagged `[ours:…]` / `[theirs:…]`. Untagged text must be common to both parents. Emit JSON naming the parent of every kept contested span, and write the same document beside the resolved file. Refuse unmarked mixes, invented text, wrong-parent tags, diff3 `|||||||` ancestor hunks, binaries, and a hybrid sidecar with the wrong number of blocks. Do not invent a merge.

### 2. Nearest ordinary workflow

`git checkout --ours/--theirs`, `git merge-file --ours|--theirs|--union`, a mergetool, or hand-editing the markers until the file looks right.

### 3. What is lost if that workflow replaces this tool

The merge product stops being a blob-with-forgotten-parents. Ordinary mergetools throw the markers away and leave no record of which parent supplied each contested token. `git merge-file --ours` in this run printed `color = red` / `size = 1` and stopped; it did not say that both lines came from ours, and it cannot say that a hybrid took ours' color and theirs' size. The tagged-hybrid contract is also lost: pasting `color = red` + `size = 2` without tags is currently a nonzero refusal that leaves the conflict in place. After replacement, that unmarked mix becomes a silent new file.

### Scores

- **Novelty 4.** Whole-hunk ours/theirs is old. A first-class per-span parent list plus a refuse-unmarked-mix hybrid grammar is not how merge tools work. The remaining idea is “resolution is a provenance event,” not “resolution is a new blob.”
- **Utility 4.** After a hybrid merge, “which parent did this token come from?” is a real question, and it is unanswerable from the blob. Two-parent text only; that is a honest boundary, not a toy.
- **Primitive strength 4.** The primitive is small and sharp: explicit parent or tagged span, else refuse. It does not understand YAML or JS. Diff3 is refused rather than half-handled. That refusal is part of the primitive.
- **Composability 4.** JSON on stdout, sidecar `.prov`, `--prov -`, hybrid on stdin, `--choice ours,theirs,hybrid`, atomic overwrite. A mergetool driver or git-note writer can sit on top without changing the core.
- **Empirical credibility 5.** This run: report, ours, theirs, tagged hybrid, untagged refusal (file still conflicted), diff3 refusal, `git merge-file` contrast, a real two-branch merge with `merge.conflictStyle=merge`, three-region messy quotes and missing trailing newline, 18/18 tests. Not a transcript from a README.
- **Evolution potential 4.** Mergetool driver, provenance as a git note, SequenceMatcher-proposed tags, optional strip of a diff3 ancestor while still tracking only two parents. Growth stays inside the same primitive instead of becoming a semantic merger.
- **Reality-Stripped Strength 4.** Peel the name off and the operation is still there: tagged two-parent resolve that will not write a blend it cannot attribute.

**KEEP**

---

## candidate-02 — declaration site vs assignment site as a disagreement pair

Shipped file: `stated`.

### 1. Operation that remains

Name a key. Walk config-like files for `KEY:` / `KEY=` declarations and source files for assignments of the same identifier. Parse a trailing token as a comparable scalar, or as not comparable (interpolation, call, identifier, expression). The observable is a disagreement pair (declaration site vs contradicting site), or a confirmation that comparable scalars agree, that only one side exists, or that comparison is refused. Whole-line `#` / `//`, `/* */`, and Python docstrings are labeled comments and ignored for comparison.

### 2. Nearest ordinary workflow

`rg KEY` (or `git grep`) across config and source, then read both hits and compare the numbers by eye.

### 3. What is lost if that workflow replaces this tool

Grep returns a hit list. This returns a pair, or an honest non-pair. In this run, `config.yaml:1 timeout: 5` vs `app.py:3 timeout = 10` was one DISAGREE object with exit 2, not six lines of `timeout`. `${WAIT}` vs `os.getenv("WAIT")` was UNKNOWN exit 0, not a false match and not a false conflict. Comment `99` in a docstring and a C block comment were listed as comments; `int timeout = 5` counted as an assignment. Replacing with `rg timeout` loses the pair, the exit-on-comparable-disagreement, the comment/code split, and the refusal to compare interpolations.

### Scores

- **Novelty 3.** The walk-and-regex is ordinary. The cut that remains is “pair, don’t list” plus “unknown is not disagree.” That is a real cut, not a new search engine.
- **Utility 4.** “It only broke after I changed the timeout” is a daily debug. Config scalar vs hardcoded assignment is the usual shape. Exit 2 is usable in CI without pretending to be a full config linter.
- **Primitive strength 3.** The primitive is coherent: one key, two sides, comparable-or-not. Nested keys are only line tokens (`timeout:`, not `server.timeout`). That limit is visible in the operation, not hidden.
- **Composability 4.** `--json` emits the pair as data. Exit 2 on comparable disagreement, 0 otherwise, 1 on usage. A script can ask one key at a time.
- **Empirical credibility 5.** Demo covered disagree / agree / declared-only / unknown / comments / JSON pair. 14/14 tests against the shipped file, including “does not match a longer identifier.”
- **Evolution potential 3.** Nested key paths and more languages would help. Richer parsers and markdown KEY hits would start turning this into a product. The pair-or-unknown contract is already the interesting part.
- **Reality-Stripped Strength 3.** Peel the name off and this is grep-plus-compare. The remainder that is not grep is the disagreement pair and the unknown refusal. That remainder is enough to keep; it is not a new universe.

**KEEP**

---

## candidate-03 — remaining-tree obligations a change fails to keep

Shipped file: `owes`.

### 1. Operation that remains

Take a unified diff (or before/after snapshots) plus the remaining tree. Report (a) identifiers that appear on minus lines as definitions and still appear in remaining files, skipping mentions whose stripped line text was introduced on a plus line of the same change; (b) paths that remaining `*.md` files name with `MUST exist:`, `required file:`, or a filename-like backtick after “must,” when those paths are absent. Shell commands such as `must run \`make test\`` are not files. Exit 2 if anything is unkept, 0 if not.

### 2. Nearest ordinary workflow

`git diff`, then `rg` the deleted names through docs and tests, then read CONTRIBUTING for required files and `test -e` them.

### 3. What is lost if that workflow replaces this tool

The binding is lost. Diff stops at hunks. `rg validate_input` does not know the name was removed *by this change*, and it will also hit the changelog line the change itself just wrote. Companion absence is usually a separate human pass. In this run, deleting `validate_input` produced an unkept reference at `README.md:3` and exit 2; a clean unused-helper delete produced `no unkept obligations`; remaining docs naming three absent paths produced missing companions and did not name `make test`. A separate plus-line changelog fixture is in the test suite: the leftover README mention still fires, the changelog “Removed …” line does not. Hand `diff`+`rg` does not do that skip unless someone writes it every time.

Honesty limit, still part of the remainder: missing companions are scanned from remaining docs and do not consult the diff. They are “true of the remaining tree,” not “caused by this hunk.” Unkept identifier references *are* change-tied.

### Scores

- **Novelty 3.** Stale-reference search exists in IDEs. Scoping it to identifiers the *change* removed, plus doc-named missing companions as a first-class miss, is a composition that is not a stock command. Not a new theory of obligations.
- **Utility 4.** Leftover README calls after a delete, and CONTRIBUTING naming a file that is not there, are review misses people actually make. False positives remain (moved functions, comment leftovers).
- **Primitive strength 3.** Two scans share an “unkept” exit. Identifier extraction is regex over `def`/`function`/`CONST =`. Policy language is not understood. The composition is real; it is not one irreducible atom.
- **Composability 4.** DIR snapshot, or `--tree` + `--diff`. `--json` with `unkept_references` / `missing_companions`. Exit 2 is scriptable. No git subprocess required for the DIR layout.
- **Empirical credibility 5.** Three demo fixtures behaved as asserted. 10/10 tests, including plus-line changelog skip, JSON shape, and usage errors.
- **Evolution potential 4.** Skip identifiers that still have a definition; bind companions to files the diff touched; search tests for MUST-like phrases. Next cuts are obvious and stay inside the same question.
- **Reality-Stripped Strength 3.** Peel the name off and this is diff-removed names still in the tree, plus docs-named files that are missing. Ordinary tools can approximate it; they do not emit the bound report or the changelog exception by default.

**KEEP**

---

## candidate-04 — named {env map, file hashes} capture, dual diff, env replay

Shipped file: `capdiff`.

### 1. Operation that remains

Under a name, store a directory’s parsed `.env` (missing `.env` = empty map, not an error) and a sha256 manifest of relative files. Diff two names as ENV modified/extra/missing and FILES modified/extra/missing. Replay overlays captured env vars onto the current environment and execs a command in a directory. `--files` writes only the captured `.env`; other file bodies were never stored. The compared object is the labeled capture, not an ad-hoc pair of live trees.

### 2. Nearest ordinary workflow

`diff -ru` of two checkouts; `find | sort | xargs sha256sum`; `export $(grep -v '^#' .env)` / `env KEY=val cmd`; `direnv` for loading, not for named historical snapshots.

### 3. What is lost if that workflow replaces this tool

Two things, both observed in this run. First, the dual report: `API_KEY` local vs remote is an ENV delta, and `.env` also appears under FILES modified because the bytes (including comments `# local CI` vs `# remote CI`) changed. `diff -ru` on `.env` files mixes those into one hunk and does not name the key. Second, the capture outlives the original directory as a fingerprint-plus-env-map: replay printed `local-ci-key` / `remote-ci-key` from the capture, and a directory with no `.env` still captured (empty env, file hashes). `direnv` loads a live `.envrc`; it does not keep a named pair you can diff later. What is *not* lost, and must not be claimed: restoring hashed file bodies. Capture never stored them.

### Scores

- **Novelty 2.** Dump, hash, diff, and `env` prefix are ordinary. Naming the dump and splitting parsed ENV from hashed FILES is a small composition, not a new object type.
- **Utility 3.** Local-vs-remote CI “what env and what files” is a real debug. Replay of env into a tree that does not hold the secrets is useful. File-body restore is honestly absent, so this is not a backup tool.
- **Primitive strength 3.** The object `{name → (env map, path→sha256)}` with diff and env-exec is a real object. Weakened by overlay-not-unset (host keys absent from the capture stay) and by the 5000-file cap.
- **Composability 4.** Three verbs: capture, diff, replay. Exit 2 on any delta, 0 if identical. Replay is an exec, so it composes as a prefix. Store is `.capdiff/NAME/` in cwd.
- **Empirical credibility 5.** Demo and 11/11 tests. Missing `.env` is empty, not a crash. Replay does not require the host to already have `API_KEY`. `--files` writes dotenv (tested).
- **Evolution potential 3.** Capture a listed subset of process env; `--env-only` / `--files-only`; explicit unset-missing-keys. Storing file bodies would destroy the primitive by turning it into tar.
- **Reality-Stripped Strength 3.** Peel the name off and this is still more than `diff -ru`: a labeled fingerprint with parsed env vs hashed files, plus env replay. It is also the candidate closest to shell glue. Keep as a composition, not as a flagship.

**KEEP**

---

## candidate-05 — per-variable env provenance, including empty file override

Shipped file: `envfrom`.

### 1. Operation that remains

Name a variable. Report its would-apply value and source: process env, a dotenv `file:path:line`, or unset. A `.env` line `KEY=` (or `KEY=""`) is an empty override even when the process already has `KEY`; the report shows `VALUE=`, `EMPTY_OVERRIDE: yes`, and the inherited value that would be wiped. Later files win (`.env` then `.env.local`). `--run` prints that provenance then execs; `--load` actually applies file assignments onto the child; without `--load` the child keeps inherited values. `--fail-empty` exits 2 if a reported key is empty-overridden.

### 2. Nearest ordinary workflow

`printenv KEY`; `grep KEY .env`; `set -a; source .env`; `direnv status`; `bash -x`.

### 3. What is lost if that workflow replaces this tool

`printenv` shows the current map, not which file emptied a key, and not the inherited value that an empty assignment would destroy. `source .env` applies; it does not explain. `direnv status` shows loader activity, not per-variable file:line vs inherited vs unset. In this run, `LIBRARY_PATH=` at `.env:2` reported empty override while inherited was `/usr/local/lib:/usr/lib`; `--run` without `--load` still gave the child the inherited path; `--run --load` gave the child `''`. That would-apply vs actually-loaded split is the remainder. Replacing with `printenv` loses source, empty-override, inherited-alongside-empty, and the fail-empty gate.

### Scores

- **Novelty 3.** Env dumping is old. Treating “file assigned empty” as a different event from “unset” and from “inherited,” with a file:line, is a clean cut that the usual dumpers do not make.
- **Utility 4.** “Why is LIBRARY_PATH empty in the child?” is a real, expensive debug. The empty-override case is not hypothetical; the demo fixture is that case.
- **Primitive strength 4.** Name a key, get source. Empty override is a named phenomenon. Would-apply (`--run`) versus apply (`--load`) is an honest split, not a bug. No interpolation, no `KEY+=`; those absences keep the primitive small.
- **Composability 4.** Keys as arguments. `--fail-empty` for scripts. `--run [--load] -- CMD` as a wrapper. `.env.local` last-wins. Output is block-structured (`KEY` / `VALUE=` / `SOURCE:`).
- **Empirical credibility 5.** Demo plus 14/14 tests: inherited vs file vs unset, fail-empty, run with and without load, `.env.local` wins, quoted `export`, inline comments, `KEY=""` as empty override, quoted `# not a comment`.
- **Evolution potential 3.** Source chain when both files set the same key is the natural next cut. Interpolation and `+=` would start cloning a shell. Relative SOURCE paths are cosmetic.
- **Reality-Stripped Strength 4.** Peel the name off and the operation is still not `printenv`: report which file:line would override this variable, including emptying it, and optionally exec under that story.

**KEEP**

---

## candidate-06 — exclusive identity kind, then IDENTICAL or DISTINCT

Shipped file: `same`.

### 1. Operation that remains

Compare two local paths under exactly one named identity kind: inode (`lstat` dev:ino), bytes (sha256 of followed content), or canonical JSON (`json.dumps` with sorted keys). Refuse if the kind is omitted or if two kinds are given. Print IDENTICAL (exit 0) or DISTINCT (exit 2) plus the discriminator. Missing paths and non-JSON `--json` are path-named errors (exit 1), not tracebacks.

### 2. Nearest ordinary workflow

`stat` / `ls -i` for inode; `cmp` / `sha256sum` for bytes; `jq -S` then `diff` for JSON. Callers pick one by habit and often mix them.

### 3. What is lost if that workflow replaces this tool

The inability to ask an untyped “are these the same?” In this run, two empty files were DISTINCT under inode (`16777233:128975855` vs `…856`) and IDENTICAL under bytes (`sha256:e3b0c442…`). A hardlink was IDENTICAL inode. JSON `{"b":1,"a":2}` vs `{"a":2,"b":1}` was IDENTICAL json and would be DISTINCT bytes (tested). A symlink and its target were IDENTICAL bytes and are DISTINCT inode (tested). `cmp` on the empties would have said equal and never mentioned that “equal” meant bytes. The ordinary tools can each answer one kind; they will not refuse to answer until the kind is named.

### Scores

- **Novelty 3.** None of the three discriminators is new. Requiring the kind as the interaction, and refusing a default, is a design stance that ordinary comparators do not take.
- **Utility 3.** Hardlink vs copy vs JSON-equal is a real confusion. People who already know to type `cmp` vs `stat` get less. People who type “same file?” get a footgun removed.
- **Primitive strength 4.** The primitive is the refusal. Computationally this is three thin dispatches. Interactionally it is one typed-equality atom. Ugly and small on purpose.
- **Composability 3.** Two paths, one kind, exit 0/2/1. Easy in a script. No N-way table. The kinds are deliberately non-composable with each other.
- **Empirical credibility 5.** Demo and 13/13 tests: omit kind, two kinds, hardlink, two empties, JSON order, JSON distinct values, symlink follow vs lstat, missing file, binary-as-JSON, parse error. Inodes and the empty SHA-256 are real numbers from this machine.
- **Evolution potential 3.** N-path table still under one kind; refuse `--json` on a symlink unless follow is named. Flag soup around `cmp` is the documented death.
- **Reality-Stripped Strength 4.** Peel the name off and the remainder is still “typed equality with no default.” That is not `cmp`. Preserve a strange strong primitive even if the implementation is a dispatcher.

**KEEP**

---

## candidate-07 — tree search whose empty result is success

Shipped file: `hits`.

### 1. Operation that remains

Search a directory tree for a literal substring (or `--regex`). Print `file:line:text` on hits. On zero hits print `0 matches` and exit 0. Usage is exit 1, bad regex exit 2, unreadable root DIR exit 3. Skip `.git` and files with NUL in the first 8KiB. `--glob` is fnmatch on relative path or basename.

### 2. Nearest ordinary workflow

`grep -R` / `rg`, then `|| true` or `case $? in 0|1)` so a miss does not fail `set -e`. `rg` already documents exit 0 match, 1 no match, 2 error.

### 3. What is lost if that workflow replaces this tool

Almost nothing computational. What is lost is a policy: miss is success, and miss is not collapsed with bad pattern or unreadable DIR the way `grep … || true` collapses them. In this run, `needle` in `fixtures/miss` printed `0 matches`, exit 0, and `&& still-running` fired; `grep -R` on the same fixture is exit 1 (claimed in the candidate text; this judge did not re-run grep, and does not need to — POSIX grep no-match is 1). Bad regex was exit 2; chmod-000 DIR was exit 3. Those distinctions are real and small. `rg` already separates no-match (1) from error (2). The remaining unique surface is “print `0 matches` and exit 0 so `&&` continues,” plus exit 3 for a bad root. Nested EACCES is skipped, not exit 3, so a partially unreadable tree can still claim empty success.

### Scores

- **Novelty 1.** Inverting grep’s no-match exit is a known complaint with a known one-line workaround. Distinct exits for bad regex vs I/O are ordinary.
- **Utility 2.** `cmd && next` after a legitimate miss is a real shell itch. `|| true` is the ordinary cream. Few people will type a new searcher only to flip that bit.
- **Primitive strength 2.** “Empty search is success” is a stance on an existing primitive (search), not a new operation. The stance is coherent. It is not strong.
- **Composability 3.** The tool exists to live on the left of `&&`. Distinct exits compose with the shell. `--glob` is extra surface that starts cloning grep.
- **Empirical credibility 5.** Demo and 19/19 tests exercise hit, miss, `&&`, literal-vs-regex, bad regex, usage, binary skip, glob miss, unreadable DIR, `.git` skip, file-as-DIR. The thin idea is thoroughly embodied.
- **Evolution potential 2.** Quiet empty, counts on stderr, nested-EACCES warnings. Further growth is a grep clone. The candidate text already states the kill condition: if the only delta is exit 0.
- **Reality-Stripped Strength 1.** Peel the name off and this is grep with exit 0 on miss. Empirical excellence does not create a remainder. Polished clone of a searcher with a policy flag.

**KILL**

---

## Verdict

| Candidate | Remainder (name ignored) | RSS | Decision |
| --- | --- | --- | --- |
| 01 | Tagged two-parent resolve + per-span parent ledger | 4 | KEEP |
| 02 | Declaration/assignment disagreement pair for one key | 3 | KEEP |
| 03 | Change-removed names still claimed by the remaining tree; doc-named missing files | 3 | KEEP |
| 04 | Named {env map, file hashes} with dual diff and env replay | 3 | KEEP |
| 05 | Per-variable env source, including empty file override | 4 | KEEP |
| 06 | Exclusive identity kind, then identical/distinct | 4 | KEEP |
| 07 | Search with empty-success exit | 1 | KILL |

KEEP: 01, 02, 03, 04, 05, 06.
KILL: 07.

The three strongest remainders after branding is removed are 01 (resolution as provenance), 05 (empty override as a sourced event), and 06 (typed equality with no default). 02, 03, and 04 are useful compositions whose nearest workflows are obvious; each still loses a bound observable if replaced. 07 loses only an exit polarity that `|| true` already buys, and `rg` already splits miss from error.

Do not average these scores with other judges. Disagreement on 04 (composition vs glue) and 06 (contract vs thin dispatcher) is expected. 07 should not survive Reality-Stripped even if another role keeps it for the `&&` story.
