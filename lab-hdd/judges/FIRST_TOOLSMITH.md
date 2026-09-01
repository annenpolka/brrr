# First Selection — Toolsmith

Lens: what a real developer would put on PATH and type again next week, not what looks clever in a README. Polish, LOC, and origin branding ignored. Strange strong primitives kept; polished clones of `grep` / `cmp` / `stat` killed.

Evidence is only this judge's runs on 2026-09-02 against `lab-hdd/lineages/candidate-0{1..7}__*`. For each candidate: README.md + CANDIDATE.md read, `./demo.sh` executed, unit tests executed. All seven demos exited 0; all seven test suites exited 0.

## KEEP

- `candidate-02__stated`
- `candidate-05__envfrom`
- `candidate-01__whence`
- `candidate-03__owes`
- `candidate-04__capdiff`

## KILL

- `candidate-06__same`
- `candidate-07__hits`

I would actually install the five KEEP tools. `stated` and `envfrom` are weekly. `whence` is the missing merge-provenance primitive. `owes` and `capdiff` are less frequent but they close loops I currently glue by hand. `same` and `hits` are exit-code skins on tools I already have.

---

## Score table (0–5)

| candidate | Nov | Util | Prim | Comp | Emp | Evo | R-S | verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 01 whence | 4 | 3 | 4 | 4 | 5 | 4 | 4 | KEEP |
| 02 stated | 3 | 5 | 4 | 4 | 5 | 4 | 4 | KEEP |
| 03 owes | 3 | 3 | 3 | 4 | 5 | 4 | 3 | KEEP |
| 04 capdiff | 3 | 3 | 3 | 4 | 5 | 3 | 3 | KEEP |
| 05 envfrom | 3 | 5 | 5 | 5 | 5 | 4 | 4 | KEEP |
| 06 same | 2 | 2 | 3 | 3 | 5 | 2 | 2 | KILL |
| 07 hits | 2 | 2 | 2 | 3 | 5 | 2 | 2 | KILL |

Do not average these. Disagreement with other judges is expected: I am scoring *repeat use*, not purity of Unix cut.

---

## candidate-01__whence — KEEP

Shipped CLI `./whence` (zsh already owns the name `whence`; demo correctly used `python3 ./whence`).

**Run:** `./demo.sh` exit 0. `python3 -m unittest discover -s tests -v` → 18 tests, OK. Demo also re-ran those 18 tests. Observed: ours-only kept `color = red` / `size = 1` and wrote JSON provenance + `.prov`; theirs-only kept blue/2; tagged hybrid kept ours color + theirs `2`; untagged mix exit 1 and left `<<<<<<<` in the file; diff3 `|||||||` refused exit 2; `git merge-file --ours` produced a blob and stopped; a real two-branch git merge (exit 1, `merge.conflictStyle=merge`) was resolved `--ours` with span parent `ours` / `value = 1\n`; messy three-region hybrid preserved no trailing newline (`xxd` tail `23 2065 6f66` = `# eof`).

**Novelty 4.** Taking a whole side is `git checkout --ours`. What I do not already have is a merge product that still names the parent of each contested span, plus a contract that unmarked mixed text is illegal. Hybrid tags (`[ours:...]` / `[theirs:...]`) are a new interaction, not a mergetool skin.

**Utility 3.** I merge often enough to want this, but not as a sidecar language. `--ours` / `--theirs` / `--choice ours,theirs,ours` plus `.prov` is the part I would wire. The tagged hybrid is extra ceremony versus editing the conflict in place. The zsh builtin collision is a real install tax: this will never be a bare `whence` on my PATH.

**Primitive strength 4.** The cut is sharp: explicit parent choice, two parents only, refuse unmarked mix, emit provenance. It does not pretend to understand YAML or invent a merge. That refusal is the primitive.

**Composability 4.** JSON on stdout, `.prov` sidecar, `--output`, `--prov -`, `--hybrid -`, `--choice` list. A mergetool driver or a review bot can consume this without parsing English.

**Empirical credibility 5.** Demo, 18 CLI tests, a throwaway git repo with a real conflict, and a messy fixture with nested `\"` all ran here. Failures were the intended nonzero exits.

**Evolution potential 4.** Next cuts I would actually take: git mergetool / merge driver that writes `.prov`, git notes instead of a sidecar, SequenceMatcher-proposed tags. Diff3 stripping is optional; octopus is out of scope and should stay out.

**Reality-Stripped Strength 4.** Forget the name. Operation left: parse `<<<<<<<` / `=======` / `>>>>>>>`, apply an explicit parent (or tagged hybrid), record which parent supplied each kept span. Nearest ordinary workflow: editor mergetool or `git merge-file --ours`. What that workflow loses: per-span parentage, and the refusal to silently accept an unmarked mix. That loss is why this is not a clone.

---

## candidate-02__stated — KEEP

Shipped CLI `./stated`.

**Run:** `./demo.sh` exit 0. `python3 -m unittest tests.test_stated -v` → 14 tests, OK. Observed: `timeout` in `fixtures/disagree` → status DISAGREE, declared `5` at `config.yaml:1` vs contradicted `10` at `app.py:3`, exit 2; agree both `5` exit 0; config-only DECLARED_ONLY exit 0; `${WAIT}` vs `os.getenv("WAIT")` → UNKNOWN, not a fake match, exit 0; comments fixture AGREE at `5` with docstring/`/* */`/`#` 99s labeled comments; `--json` disagreement pair is machine-shaped.

**Novelty 3.** This is grep plus a scalar compare. The uncommon part is treating the *disagreement pair* as the object, not the hit list, and refusing to compare interpolations and calls.

**Utility 5.** This is the tool I would type next week. "The YAML says 5, why is production using 10?" is a weekly debugging move. `rg timeout` dumps every mention; `stated timeout` answers the question I actually have. Exit 2 is CI-shaped.

**Primitive strength 4.** Declaration site vs contradicting assignment, or an honest UNKNOWN. Comments are reported and ignored for comparison — that is the difference between a linter and a toy. Nested keys (`server.timeout`) are still line tokens; that is a real hole, not a reason to kill the cut.

**Composability 4.** `stated KEY [DIR]`, `--json`, exit 0/1/2. I can drop it in a script: `stated timeout || …`. It does not need a daemon or a language server.

**Empirical credibility 5.** Demo covered disagree / agree / one-sided / unknown / comments / JSON. 14 tests against the shipped CLI, OK.

**Evolution potential 4.** Nested key paths, case-insensitive env keys, a few more languages. Stay a disagreement-pair CLI; do not grow into a runtime config tracer.

**Reality-Stripped Strength 4.** Operation left: walk config-like files and source files for one identifier, compare literal scalars, emit pairs (or say the values are not statically comparable). Nearest workflow: `rg KEY` then eyeball. What eyeballing loses: the pair, the comparable/unknown split, and an exit code that means "these two numbers disagree."

---

## candidate-03__owes — KEEP

Shipped CLI `./owes`.

**Run:** `./demo.sh` exit 0. `python3 tests/test_owes.py -v` → 10 tests, OK. Observed: deleted `validate_input` still mentioned in README → unkept reference, exit 2; remaining docs naming `SECURITY.decision.md`, `docs/adr.md`, `docs/threat-model.md` → missing companions, exit 2, and `must run \`make test\`` is *not* reported as a file (the filename-like filter held); clean helper-delete → `no unkept obligations`, exit 0. Tests also cover plus-line changelog skip, `--json` shape, `--tree`/`--diff`.

**Novelty 3.** "Names on minus lines still in the tree" is `git diff` + `rg`. The first-class miss of a companion file that remaining docs still require is the less common half.

**Utility 3.** I want this after a delete-heavy PR. I do *not* want to stage a `DIR/change.diff` + `DIR/tree` snapshot to get it. `--tree TREE --diff DIFF` is enough: `git diff HEAD > /tmp/c.diff && owes --tree . --diff /tmp/c.diff`. Without that git-shaped default, adoption is slower. False positives (moved functions, comment leftovers) will train me to ignore it unless the next cut skips still-defined names.

**Primitive strength 3.** Two obligation kinds: leftover identifier mentions, missing required files. Identifier harvest is regex (`def`/`class`/`fn`/ALLCAPS). Companion harvest is a small phrase set (`MUST exist:`, `required file:`, filename-like backticks after `must`). That is a real cut, currently leaky.

**Composability 4.** Directory snapshot *or* `--tree`/`--diff`, `--json`, exit 2 on unkept. Fits a pre-commit or review bot. Stdlib only; no git subprocess required.

**Empirical credibility 5.** Three demo fixtures behaved; 10 CLI tests OK, including the changelog plus-line skip that would otherwise have been a noisy false unkept.

**Evolution potential 4.** Skip identifiers that still have a definition in the remaining tree. Bind missing companions to files the diff actually touched. Default `owes` on `git diff HEAD` so I stop inventing snapshot dirs. Do not grow a policy-language parser.

**Reality-Stripped Strength 3.** Operation left: parse a unified diff for removed names, search the remaining tree, also flag docs that name a file that is not there. Nearest workflow: `git diff` + `rg`. What that loses: the companion-file miss tied to the change, plus-line self-mentions skipped, and a single exit 2. The first half is close to a clone; the second half is why I keep it.

---

## candidate-04__capdiff — KEEP

Shipped CLI `./capdiff`.

**Run:** `./demo.sh` exit 0. `python3 -m unittest discover -s tests -v` → 11 tests, OK. Observed: capture `a` (2 files, 1 env) and `b` (3 files, 1 env); `diff a b` exit 2 with ENV modified `API_KEY` local-ci-key vs remote-ci-key *and* FILES modified `.env` hashes plus FILES extra `extra.txt`; replay a/b printed those keys via `print_key.py` with env overlay only; missing `.env` capture `none` did not crash; `diff a none` reported `ENV missing: API_KEY=local-ci-key` and FILES missing `.env` / `app.txt`.

**Novelty 3.** `diff -ru`, `env`, and `direnv` exist. The object here is a *named* pair `{parsed env map, file hashes}` you can diff later and then exec with. Small composition, not a new physics.

**Utility 3.** "Works on my laptop, CI has a different `API_KEY` and an extra file" is a real loop. I would `capdiff capture local .` and `capdiff capture ci .` then `diff` then `replay ci -- . pytest`. I would not run this daily. Replay restoring only `.env` (not hashed bodies) is honest and also the ceiling: this will not reproduce a missing source file.

**Primitive strength 3.** Three verbs (capture / diff / replay) around one object. The interesting split, confirmed in the demo, is that `.env` shows up twice: parsed `API_KEY` as ENV, bytes (including comments) as FILES. Empty env map on missing `.env` is the right default. Overlay replay does not unset host keys absent from the capture — that is a sharp edge, currently undocumented in the happy path.

**Composability 4.** Named store `.capdiff/NAME/`, diff exit 2, replay `exec` in DIR. I can put capture on both sides of a CI matrix and diff the artifacts.

**Empirical credibility 5.** Demo + 11 tests, including identical captures exit 0, replay without host `API_KEY`, `--files` writing dotenv, missing `.env` as empty not crash.

**Evolution potential 3.** Capture a listed subset of `os.environ`, `--env-only` / `--files-only`, include/exclude globs, explicit `env -i` unset. Stay a capture object; do not become a tarball/vault.

**Reality-Stripped Strength 3.** Operation left: snapshot a directory's dotenv + sha256 manifest under a name; print ENV/FILES extra/missing/modified; overlay captured env and exec. Nearest workflow: `diff -ru` plus `env $(cat .env) cmd`. What that loses: a labeled pair you can keep, the ENV-vs-FILES split on the same `.env`, and replay from a capture that the live tree no longer has.

---

## candidate-05__envfrom — KEEP

Shipped CLI `./envfrom`.

**Run:** `./demo.sh` exit 0. `python3 -m unittest tests.test_envfrom -v` → 14 tests, OK. Observed on this machine: process `LIBRARY_PATH=/usr/local/lib:/usr/lib` vs fixture `.env:2` `LIBRARY_PATH=` → VALUE empty, `SOURCE: file:…/.env:2`, `EMPTY_OVERRIDE: yes`, `INHERITED: /usr/local/lib:/usr/lib`; `APP_ENV` file `dev` over inherited `from-shell`; `PATH` `SOURCE: env` (noisy, honest); `NOT_A_REAL_VAR` `SOURCE: unset`; `--fail-empty LIBRARY_PATH` exit 2; `--run` without `--load` child kept inherited LIBRARY_PATH; `--run --load` child `LIBRARY_PATH=''` and `APP_ENV=dev`; quoted-export fixture unquoted `"hello world"`, `'Ada Lovelace'`, stripped inline comment on `COLOR=red`, treated `EMPTY_QUOTED=""` as empty override, kept `# not a comment` inside quotes, accepted `export PREFIX=app`.

**Novelty 3.** `printenv` and `direnv status` exist. Per-variable provenance with empty-file-override as a first-class fact is the gap they leave.

**Utility 5.** Strongest daily driver in this set. "Why is `LIBRARY_PATH` empty in the child?" is a question I actually ask. I would put this on PATH tomorrow. `--fail-empty` is a script gate. `--run --load` is a visible dotenv, not a silent one.

**Primitive strength 5.** Three sources: `env`, `file:path:line`, `unset`. Empty override is not the same as unset, and the inherited value is still printed. `--run` without `--load` prints the *would-apply* override and then the child keeps the process env — that split is the honest rule, not a bug.

**Composability 5.** `envfrom KEY…`, `--dir`, `--fail-empty`, `--run [--load] -- CMD`. Last-wins `.env` then `.env.local`. Output is block-shaped and grepable. Exec overlay is the composition point.

**Empirical credibility 5.** Demo exercised inherited vs empty override, fail-empty, run-with and without load, quoted/export/comment parser. 14 tests OK.

**Evolution potential 4.** Source chain when both `.env` and `.env.local` set the same key (today last-wins, no chain). Interpolation / `KEY+=` only if dogfood demands it. Relative SOURCE paths. Do not become a repair tool.

**Reality-Stripped Strength 4.** Operation left: for named keys, say whether the effective value is process env, a dotenv assignment at file:line, or unset, and whether a file assignment is emptying a key the process already had. Nearest workflow: `printenv` plus opening `.env`. What that loses: which line wiped the key, the inherited value next to the empty VALUE, and a fail-empty gate before exec.

---

## candidate-06__same — KILL

Shipped CLI `./same`.

**Run:** `./demo.sh` exit 0. `python3 -m unittest tests.test_same -v` → 13 tests, OK. Observed: omit kind → usage + `available kinds: inode, bytes, json`, exit 1; hardlink `--inode` IDENTICAL `16777233:128975858` exit 0; two empty files `--inode` DISTINCT two inodes exit 2, `--bytes` IDENTICAL empty sha256 `e3b0c442…` exit 0; JSON key order IDENTICAL `{"a":2,"b":1}`; `--bytes` follows symlink; missing path one-line `same: …: No such file or directory` exit 1, no traceback; `--json` on binary `not JSON (not UTF-8 text)` exit 1.

**Novelty 2.** `stat`/`ls -i`, `cmp`/`sha256`, `jq -S` already implement the three identities. The twist is refusing to guess the kind. That is an API constraint, not a new operation.

**Utility 2.** I would not type `same --bytes a b` instead of `cmp -s a b`. I already know which identity I mean. JSON canonical compare is the most useful mode and is still `jq -S`. This will not earn a PATH slot.

**Primitive strength 3.** Requiring exactly one kind is a clean refusal (two flags also exit 1). The discriminators themselves are stock: `lstat` dev:ino, sha256, `json.dumps(sort_keys=True)`. Symlink vs target DISTINCT under `--inode` and IDENTICAL under `--bytes` is correct and already how Unix works.

**Composability 3.** One-line stdout, exit 0 identical / 2 distinct / 1 error. Fine in a script. Three modes behind required flags is still three tools.

**Empirical credibility 5.** Demo and 13 tests all behaved, including the dogfood error-shape cases.

**Evolution potential 2.** An N-path table is more of the same. Easy to rot into flag soup around `cmp`. Nothing here wants a lineage.

**Reality-Stripped Strength 2.** Operation left: compare two local paths under a named identity. Nearest workflow: `stat` / `cmp` / `jq -S`. What replacement loses: forced naming of the kind, and unified IDENTICAL/DISTINCT exit codes. That is not enough to keep a clone.

---

## candidate-07__hits — KILL

Shipped CLI `./hits`.

**Run:** `./demo.sh` exit 0. `python3 -m unittest tests.test_hits -v` → 19 tests, OK. Observed: two hits in `fixtures/has` exit 0; miss prints `0 matches` exit 0 and `hits … && echo still-running` still ran; literal `n.edle` is not a regex (0 matches); `--regex 'n.edle'` hits; bad regex `[` exit 2; no args exit 1; mixed tree skips NUL `blob.bin`, keeps `note.txt`; `--glob '*.txt'` same; `--glob '*.md'` miss still success; unreadable DIR exit 3.

**Novelty 2.** Recursive substring search with inverted empty-exit. `grep`/`rg` already search. The delta is policy: miss is success, bad pattern is 2, unreadable root is 3.

**Utility 2.** Interactively I will keep using `rg`. In scripts I already write `grep … || true` and lose error distinction — that pain is real, and this CLI does distinguish miss vs bad regex vs I/O. I still would not install a grep subset to get that. A ten-line wrapper around grep preserves the same contract without starting a search-tool lineage.

**Primitive strength 2.** Empty-is-success is a policy on grep, not a new operation. Binary skip (NUL in first 8KiB) is the correct grep-ish behavior after the forged-line bug; it is not a primitive. Nested EACCES still reports `0 matches` / exit 0 — the I/O story is only about the root DIR.

**Composability 3.** `hits PAT && next` is the intended composition, and the demo proved it. Distinct 1/2/3 is script-friendly. Output is `file:line:text` or `0 matches`. Fine, thin.

**Empirical credibility 5.** Demo and 19 tests OK, including unreadable dir, binary skip, glob miss, skip `.git`.

**Evolution potential 2.** Feature race with `rg` (`-i`, context, gitignore globs) is a dead end. Quiet-empty and nested-EACCES warnings are polish, not a new cut.

**Reality-Stripped Strength 2.** Operation left: walk a tree, print matching lines, treat zero matches as success. Nearest workflow: `rg` / `grep -R`. What replacement loses: exit 0 on miss and split error codes. Recoverable without this tool.

---

## Toolsmith notes (not scores)

- Empirical credibility is high across the board because every candidate shipped a real CLI, a demo that asserts exits, and tests that subprocess that CLI. That is necessary and not sufficient. I am not ranking on test count.
- `stated` and `envfrom` are the two I would install this afternoon. They answer questions I currently answer by opening two files.
- `whence` is the one I would not want to lose even if I used it less: git throws parentage away; this keeps it.
- `owes` and `capdiff` survive as complete small loops (leftover obligations; named env+hash capture) that I currently improvise. They need git-shaped defaults (`owes` on `git diff`) and honest replay limits (`capdiff` never stored bodies) more than they need features.
- `same` and `hits` are the polished clones. Required-kind and empty-is-success are cute contracts. Cute is not enough.

KEEP list again: **stated, envfrom, whence, owes, capdiff**.
