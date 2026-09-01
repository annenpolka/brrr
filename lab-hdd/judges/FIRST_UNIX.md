# First Selection — Unix

Judge: Unix. Independent. Origins ignored. Other judges unread.

Values: tiny orthogonal primitives, composition, pipes, exit codes, text.
Not polish. Not LOC. Not README length. Strange strong primitives KEEP even if ugly. Polished clones KILL.

Method: README.md + CANDIDATE.md for each candidate. `./demo.sh` and `python3 -m unittest discover -s tests -q` run from that directory on 2026-09-02. Empirical scores use those runs only.

---

## candidate-01__whence

**What remains:** Parse `<<<<<<<` / `=======` / `>>>>>>>`, resolve only by an explicit parent (`--ours` / `--theirs` / `--choice` / tagged `[ours:…]` `[theirs:…]` hybrid), emit JSON naming the parent of every kept contested span. Untagged mixed text is refused. Two parents only; `|||||||` is refused.

### Empirical evidence (this judge)

`./demo.sh` → **exit 0**. Observed: ours-only provenance `spans: [{"parent":"ours","text":"color = red\nsize = 1\n"}]`; hybrid tagged success keeps ours `color = red` + theirs `2`; untagged mix **exit 1**, markers left in the file; diff3 fixture **exit 2** (`diff3 ancestor marker (|||||||)… whence tracks two parents only`); `git merge-file --ours` prints a blob and stops; a throwaway two-branch merge conflict is resolved `--ours` with `mode: ours`; messy three-region hybrid preserves no trailing newline (`xxd` tail `23 2065 6f66` = `# eof`). Demo also ran 18 unittests internally, OK.

`python3 -m unittest discover -s tests -q` → **exit 0**, `Ran 18 tests in 0.599s OK`.

Shipped CLI is `./whence` (772 lines). zsh already has a builtin `whence`; the demo correctly invokes `python3 ./whence`.

### Scores

**Novelty — 4.** Git already takes ours/theirs. What does not exist is a merge *product* that still says, for each contested span, which parent supplied it, plus a contract that unmarked mix is illegal. The hybrid tag language is invented surface, but the provenance report is a real missing object.

**Utility — 4.** Overlapping edits are daily. `git mergetool` throws the parentage away the moment the blob is clean. A `.prov` sidecar (or stdout JSON) next to the resolved file is something a later review or `git notes` step could actually consume. Name collision with zsh is a real adoption tax, not a reason the operation is fake.

**Primitive strength — 4.** One sharp rule: no invented merge. Whole-side choice, per-region `--choice`, or tagged spans that must be ordered substrings of a named parent. That is a primitive, not a mergetool. The `[ours:…]` sidecar with `%%` and `\]` escaping is more language than Unix wants; the refuse-unmarked-mix core would still stand without it.

**Composability — 3.** Provenance JSON on stdout is pipeable; `--hybrid -` and file `-` speak stdin; `--prov -` skips the sidecar. Default behavior overwrites `FILE` and writes `FILE.prov` — mergetool-shaped, not a filter. No driver wiring, so it does not yet sit in `git merge`. Exit table is honest: 0 ok, 1 refuse, 2 parse, 3 usage.

**Empirical credibility — 5.** This judge watched a real `git merge` produce two-parent markers, `whence resolve --ours` keep `value = 1\n`, untagged mix leave the conflict in place, and a no-trailing-newline messy resolve match `xxd`. Tests call the shipped file, not a reimplementation.

**Evolution potential — 4.** The next honest cuts are a mergetool/`merge` driver, provenance as a git note instead of a sidecar, and optional stripping of a diff3 ancestor hunk while still tracking only ours/theirs. SequenceMatcher auto-tags would soften the refuse-mix contract and should be a separate tool.

**Reality-Stripped Strength — 4.** Ignore the name. Operation: resolve conflict markers by named parent and emit which parent won each span. Nearest ordinary workflow: edit the markers, or `git checkout --ours/--theirs`, or `git merge-file --ours`. What that workflow loses: per-span parentage and the refusal to accept an untagged mash-up as a resolution. That loss is the tool.

### Verdict: KEEP

Ugly (zsh name, hybrid DSL, in-place write). The primitive is not a clone of `merge-file`.

---

## candidate-02__stated

**What remains:** Walk a tree, regex-find `KEY:` / `KEY=` in config-like files and assignments in source, compare trailing literal scalars, print a disagreement pair or a status document. Exit 2 only on comparable disagreement; everything else is exit 0.

### Empirical evidence (this judge)

`./demo.sh` → **exit 0**. Observed: disagree fixture `status: DISAGREE` declared `5` vs contradicted `10`, tool **exit 2**; agree both `5` **exit 0**; config-only `DECLARED_ONLY` **exit 0**; interpolation vs `os.getenv` `status: UNKNOWN` **exit 0**; comments fixture `status: AGREE` with docstring/`/* */`/`#` hits listed as comments; `--json` disagreement pair has `declared_value: "5"`, `contradicted_value: "10"`.

`python3 -m unittest discover -s tests -q` → **exit 0**, `Ran 14 tests in 0.428s OK`.

Shipped CLI is `./stated` (629 lines). No stdin.

### Scores

**Novelty — 2.** This is `rg KEY` across two filename classes, then compare the token after `:`/`=`. Pairing declaration vs assignment is a report shape, not a new operation. People already do this by eye when a timeout “only broke after I changed yaml.”

**Utility — 3.** The disagree fixture is a real debug question. Comment/docstring false positives were a real bug and got fixed. Nested keys, interpolations, and typed Python (`timeout: int = 5`) are still outside the scanner, so it will lie or go UNKNOWN on the trees where you actually need it.

**Primitive strength — 2.** Too many statuses (`disagree` / `agree` / `declared_only` / `assigned_only` / `unknown` / `none`) for one binary question. Exit 0 is overloaded: agree, one-sided, unknown, and nothing-found are the same code. A Unix primitive would make “comparable disagreement” vs “not a comparable pair” vs “no sites” distinct exits. Comment-state machine + per-language file lists is a mini-linter, not one orthogonal cut.

**Composability — 2.** Document on stdout, not records. `--json` is the only composition path. Cannot take `rg` hits on stdin and just do the compare. You cannot write `stated timeout && deploy` unless you are willing to treat UNKNOWN as success.

**Empirical credibility — 5.** Demo and 14 tests passed here, including the comments dogfood path. The CLI is real.

**Evolution potential — 2.** Suggested mutations (nested `server.timeout`, case-insensitive env, richer parsers, markdown) grow a linter. The primitive does not sharpen; the product fattens.

**Reality-Stripped Strength — 2.** Ignore the name. Operation: grep a key in config and source, compare trailing literals. Nearest workflow: `rg timeout` and read the hits. What you lose: automatic scalar compare, comment filtering, exit 2 on a numeric mismatch. That is a convenience wrapper around grep, not a missing Unix verb.

### Verdict: KILL

Useful composition, not a primitive. Overloaded exit 0 is a Unix defect. Polished grep-plus-status.

---

## candidate-03__owes

**What remains:** Given a unified diff and a remaining tree, list (1) identifiers removed on minus lines that remaining files still mention, and (2) paths that remaining `*.md` name via `MUST exist:` / `required file:` / `must \`path\`` that are absent. Exit 2 if either list is nonempty.

### Empirical evidence (this judge)

`./demo.sh` → **exit 0**. Observed: deleted `validate_input` still in README → `unkept references:` + **exit 2**; missing companions `SECURITY.decision.md`, `docs/adr.md`, `docs/threat-model.md` → **exit 2** (no `make test` false companion); clean fixture `no unkept obligations` **exit 0**.

`python3 -m unittest discover -s tests -q` → **exit 0**, `Ran 10 tests in 0.372s OK`.

Shipped CLI is `./owes` (475 lines). Inputs are a custom `DIR/{change.diff,tree}` or `DIR/{before,after}` layout, or `--tree` + `--diff FILE`. Diff is not read from stdin.

### Scores

**Novelty — 2.** `git diff` plus `rg` for the deleted name is the ordinary workflow. “Required file” matching is a second, fixture-shaped checker (`MUST exist:`, `required file:`). Gluing them under one noun does not make a new operation.

**Utility — 3.** Leftover mentions after a delete are a real review miss. Moved functions, comment-only leftovers, and short names will false-positive; `LICENSE` without a dot is ignored after the filename-like filter. Companion scanning only looks at `*.md`. Fine for the fixtures; leaky on a real tree.

**Primitive strength — 2.** Two jobs. Identifier extraction is a pile of `def|class|function|fn|…` regexes, not a language-agnostic cut. The snapshot directory protocol (`before/`/`after/` or `change.diff`+`tree/`) is an application layout, not a primitive interface.

**Composability — 1.** Unix would be `git diff | owes TREE`. This CLI refuses that: no stdin, mandatory snapshot directory or two flags pointing at files. Human report / JSON document. Exit 2 is the only composable bit.

**Empirical credibility — 5.** Three demo fixtures behaved; 10 tests OK. Dogfood that dropped `make test` as a companion is visible in this run (fixture 2 names three files, not a command).

**Evolution potential — 3.** Skipping identifiers that still have a definition, and binding companions to files the diff actually touched, would sharpen job (1) and job (2) separately. They should not stay one binary.

**Reality-Stripped Strength — 2.** Ignore the name. Operation: names on minus lines still occurring in the tree, plus regex for required paths in markdown. Nearest workflow: `git diff` and `rg`. What you lose: packaging two leaky checks and a custom directory layout. The layout is a cost, not a delta.

### Verdict: KILL

Should have been a stdin filter with one job. Two glued checkers behind a snapshot protocol is not Unix.

---

## candidate-04__capdiff

**What remains:** Named capture of a directory’s parsed `.env` plus sha256 of relative files, stored under `.capdiff/NAME`. Diff two names as ENV vs FILES (exit 2 on any delta). Replay overlays captured env and execs a command; `--files` restores only the captured `.env`, not file bodies.

### Empirical evidence (this judge)

`./demo.sh` → **exit 0**. Observed: capture `a` (2 files, 1 env) and `b` (3 files, 1 env); `diff a b` **exit 2** with `ENV modified: API_KEY` `local-ci-key` vs `remote-ci-key` and `FILES extra: extra.txt`; replay a/b print `local-ci-key` / `remote-ci-key`; capture without `.env` is empty env map; `diff a none` **exit 2** with `ENV missing: API_KEY=local-ci-key` and `FILES missing: .env` / `app.txt`.

`python3 -m unittest discover -s tests -q` → **exit 0**, `Ran 11 tests in 0.657s OK`.

Shipped CLI is `./capdiff` (367 lines). Three subcommands. Stateful store in cwd.

### Scores

**Novelty — 2.** `sha256sum` a tree, parse `.env`, `diff` two dumps, `env KEY=val cmd`. Binding those dumps to a name in `.capdiff/` is bookkeeping. The ENV-vs-FILES split (parsed keys *and* `.env` bytes) is a small honest distinction, not a new verb.

**Utility — 3.** “Local CI key vs remote CI key, plus an extra file” is a real comparison. Replay without restoring hashed bodies is honest and also means the name “capture” oversells: you cannot recreate the tree. Missing `.env` as empty map (not an error) matches how repos actually look.

**Primitive strength — 2.** Three verbs (`capture` / `diff` / `replay`) around a hidden store. Unix wants one object on stdout: a text capture you can save, `diff`, and `env` from. Replay is `env`+`exec`. File-hash compare is `cmp`/`sha256sum`. The suite is a small product.

**Composability — 2.** Nothing pipes. Capture does not emit a portable document; it mutates `.capdiff/` in cwd. Diff’s labeled sections are readable text with a good exit 2, but the inputs are names in a store, not files. Replay exec is composition of a sort, then it stops being a filter.

**Empirical credibility — 5.** Demo and 11 tests passed here, including the no-`.env` capture path and env-only replay in a directory that has no `.env`.

**Evolution potential — 2.** Include/exclude globs, `os.environ` subsets, `--env-only`, unset-missing-keys: this becomes direnv/docker-lite. The Unix cut would be “write the capture as text and stop.”

**Reality-Stripped Strength — 2.** Ignore the name. Operation: hash files, parse `.env`, remember two labeled dumps, overlay env, exec. Nearest workflow: `diff -ru`, `sha256sum`, `env $(grep -v ^# .env) cmd`, maybe `direnv`. What you lose: a name so you remember which dump was local vs remote. That is memory, not a missing operation.

### Verdict: KILL

Stateful three-command store around tools that already exist. Not a tiny primitive.

---

## candidate-05__envfrom

**What remains:** Name a variable. Report whether its effective value is inherited process env, a dotenv `file:path:line` assignment, or unset. A file line `KEY=` is an empty override even when the process already has `KEY`. `--fail-empty` exits 2. `--run` prints provenance then execs; `--load` actually applies file assignments onto the child.

### Empirical evidence (this judge)

`./demo.sh` → **exit 0**. Observed with `LIBRARY_PATH=/usr/local/lib:/usr/lib` and fixture `.env` line 2 `LIBRARY_PATH=`: `VALUE=` `SOURCE: file:…/empty-override/.env:2` `EMPTY_OVERRIDE: yes` `INHERITED: /usr/local/lib:/usr/lib`. `--fail-empty LIBRARY_PATH` **exit 2**. `--run` without `--load`: child keeps inherited `LIBRARY_PATH=/usr/local/lib:/usr/lib`. `--run --load`: `child LIBRARY_PATH=''`. Quoted-export fixture: `export PREFIX=app`, unquoted inline comment stripped (`COLOR=red`), `EMPTY_QUOTED=""` is empty override, quoted `# not a comment` stays a value.

`python3 -m unittest discover -s tests -q` → **exit 0**, `Ran 14 tests in 0.584s OK`.

Shipped CLI is `./envfrom` (281 lines). Requires KEY args unless `--run`.

### Scores

**Novelty — 4.** `printenv` shows values. It does not show that `.env:2` would wipe `LIBRARY_PATH`. `direnv status` shows loading activity, not per-key provenance. Empty-override-vs-inherited is a real missing env object.

**Utility — 4.** Empty `LIBRARY_PATH=` / `PYTHONPATH=` in a dotenv file is a classic “child is empty and nobody knows why.” `--fail-empty` is a gate you could put in front of a test runner. `--run --load` duplicates dotenv loaders; the useful split is that observation does not mutate unless `--load` is named.

**Primitive strength — 4.** One lookup: source of KEY. Three sources (`env` / `file:path:line` / `unset`) plus the empty-override bit. `--run`/`--load` are a second tool (wrapper/exec) riding along; they do not ruin the lookup, and requiring `--load` to actually apply file values is the right refusal of magic.

**Composability — 3.** `--fail-empty` is a predicate. Block format (`KEY` / `VALUE=` / `SOURCE:`) is parseable and worse than one record per line for `awk`. `--run` is a wrapper, not a pipe. Default “must name KEY” is Unix-good. Absolute `SOURCE` paths are ugly in transcripts and correct.

**Empirical credibility — 5.** This run showed inherited vs empty file override, fail-empty exit 2, run-without-load keeping the child inherited, run-with-load emptying it, and the quoted-export parser cases. 14 tests OK.

**Evolution potential — 4.** Source *chain* when `.env` and `.env.local` both set the key; relative SOURCE paths; newline-safe VALUE. Stay a provenance tool. Interpolation/`KEY+=` would become a shell.

**Reality-Stripped Strength — 4.** Ignore the name. Operation: look up KEY in process env and dotenv files; report who won; flag empty file assignment; optionally refuse it. Nearest workflow: `printenv KEY`, `grep KEY .env`, `direnv status`. What that workflow loses: the pair (file emptied this / inherited used to be that) and a file:line source. That pair is the tool.

### Verdict: KEEP

The empty-override provenance is a primitive `env` does not have. Keep the lookup; do not let `--run` eat the lineage.

---

## candidate-06__same

**What remains:** Compare two local paths under exactly one required identity kind (`--inode` | `--bytes` | `--json`). Omit the kind: refuse. Exit 0 identical, 2 distinct, 1 usage/IO/parse. One line of text.

### Empirical evidence (this judge)

`./demo.sh` → **exit 0**. Observed:

- omit kind → `usage: same --inode|--bytes|--json A B` **exit 1**
- hardlink `--inode` → `IDENTICAL inode 16777233:128975858` **exit 0**
- two empty files `--inode` → `DISTINCT inode 16777233:128975855 16777233:128975856` **exit 2**
- same two empties `--bytes` → `IDENTICAL bytes sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` **exit 0**
- JSON key order `--json` → `IDENTICAL json {"a":2,"b":1}` **exit 0**
- symlink `--bytes` follows → IDENTICAL sha256 of `hello` **exit 0**
- missing path → `same: …/fixtures/no-such: No such file or directory` **exit 1** (no traceback)
- `--json` on binary → `same: …/binary.bin: not JSON (not UTF-8 text)` **exit 1**

`python3 -m unittest discover -s tests -q` → **exit 0**, `Ran 13 tests in 0.265s OK`.

Shipped CLI is `./same` (98 lines).

### Scores

**Novelty — 3.** `stat`, `cmp`, and `jq -S` each already implement one identity. The novelty is the *required kind*: the tool will not guess inode vs bytes vs JSON. That is a small novelty and the entire point.

**Utility — 4.** “Are these the same file?” silently means three different things in pipelines. Two empty files that `cmp` calls equal are DISTINCT under `--inode` on this volume — the demo showed both numbers. That is a confusion this tool makes inexpressible without naming.

**Primitive strength — 5.** Tiny, orthogonal, one job, one required flag, text line, exit 0/2/1. `--json` is a slightly different kind of identity (canonical content, follows `open()` unlike `--inode`’s `lstat`), but still exactly one kind per invocation. Refusing mixed or omitted kinds *is* the primitive.

**Composability — 5.** `same --inode A B && …` / `same --bytes A B || …` is how Unix predicates look. Stderr for errors, stdout for the verdict. No store, no subcommands, no document. Paths not stdin — correct for this operation.

**Empirical credibility — 5.** Hardlink, two empties under two kinds, JSON order, symlink follow, missing file, binary-as-JSON: all observed in this demo. 13 tests OK. Empty-file sha256 matched the known digest.

**Evolution potential — 3.** An N-path table still under one kind is a fair next cut. Flag soup around `cmp` would kill it. Canonical JSON with `Decimal` so `1.0` ≠ `1` is a sharpening of `--json`, not a new product.

**Reality-Stripped Strength — 4.** Ignore the name. Operation: compare two names under a named identity. Nearest workflow: `stat`, `cmp`, `jq -S`. What that workflow loses: the refusal to guess which identity you meant. That refusal is the whole tool, and it is enough.

### Verdict: KEEP

The Unix-shaped object in this set. Do not grow it.

---

## candidate-07__hits

**What remains:** Recursive search of a directory tree. Zero matches is success (exit 0, prints `0 matches`). Bad `--regex` is exit 2. Unreadable root DIR is exit 3. Usage is exit 1. Hits print `file:line:text`. Default match is a literal substring. NUL in the first 8KiB skips the file.

### Empirical evidence (this judge)

`./demo.sh` → **exit 0**. Observed: two hits under `fixtures/has` **exit 0**; miss prints `0 matches` **exit 0**; `hits needle fixtures/miss && echo still-running` prints `0 matches` then `still-running`; literal `[` is not regex (`0 matches`); `--regex needle` hits; `--regex '['` → `hits: bad regex: unterminated character set at position 0` **exit 2**; no args **exit 1**; mixed tree skips `blob.bin`, keeps `note.txt`; `--glob '*.txt'` same; `--glob '*.md'` miss still `still-running`; unreadable DIR **exit 3**.

`python3 -m unittest discover -s tests -q` → **exit 0**, `Ran 19 tests in 0.396s OK`.

Shipped CLI is `./hits` (169 lines). No stdin. Nested EACCES is skip, not exit 3.

### Scores

**Novelty — 2.** This is grep with the miss exit remapped to 0 and errors split (bad pattern vs unreadable dir). `grep` already uses 0/1/2. The claimed invention is polarity: absence is a normal outcome for `cmd && next`.

**Utility — 3.** `set -e` / `grep … || true` really does swallow bad patterns and IO errors. Distinguishing miss from `exit 2`/`3` is the only reason to type this instead of grep. The search itself is a worse grep (no `-i`, no context, no stdin, tree-only).

**Primitive strength — 3.** The exit table is a real primitive. The search is a clone. Printing `0 matches` on stdout is the wrong half of the contract: a miss should be empty stdout + exit 0 so pipes still work. Nested unreadable files reporting `0 matches` / exit 0 is a lie relative to exit 3.

**Composability — 3.** `hits PAT && next` after a miss works — observed. `hits PAT | wc -l` on a miss is `1` because of `0 matches`, which fights pipes. grep-format hits compose; the miss line does not. No stdin filter mode.

**Empirical credibility — 5.** Hit, miss-and-still-running, literal vs regex, bad regex 2, usage 1, binary skip, glob miss, unreadable dir 3: all observed. 19 tests OK.

**Evolution potential — 2.** Quiet empty (print nothing on miss) is the mutation that makes it Unix. Count on stderr, nested EACCES warnings: fine. If the lineage only polishes grep features, it is already dead.

**Reality-Stripped Strength — 2.** Ignore the name. Operation: recursive search; miss is success; bad query and unreadability are other exits. Nearest workflow: `grep -R` / `rg`, or `grep … || true`. What you lose: miss vs bad pattern vs IO as separate exits, without `|| true` collapsing them. Small, real, and almost entirely the exit table.

### Verdict: KEEP

A grep clone with one sharp exit-code contract. Ugly (`0 matches` on stdout). Keep *because* of the polarity, not the search. If the next cut is more grep flags, kill it then.

---

## KEEP list

Multiple survivors. Not a ranking.

| Candidate | Verdict | Unix reason |
|-----------|---------|-------------|
| **candidate-01__whence** | **KEEP** | Missing merge object: explicit parent + per-span provenance; refuse unmarked mix. |
| candidate-02__stated | KILL | Grep-plus-status document; exit 0 overloaded. |
| candidate-03__owes | KILL | Two checkers; no stdin; snapshot directory protocol. |
| candidate-04__capdiff | KILL | Three-command hidden store around `diff`/`sha256`/`env`. |
| **candidate-05__envfrom** | **KEEP** | Per-key env provenance; empty file override vs inherited is a real primitive. |
| **candidate-06__same** | **KEEP** | Required identity kind; tiny predicate; text + exit 0/2/1. |
| **candidate-07__hits** | **KEEP** | Exit polarity so miss is success without `|| true`; search is otherwise a clone. |

**KEEP:** `whence`, `envfrom`, `same`, `hits`.
