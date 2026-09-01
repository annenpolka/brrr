# FINAL HERETIC — final jury (HDD)

Judge: Heretic. Clock: 2026-09-02 ~07:41 JST. Isolated from other final judges. Did not rewrite tools. Did not merge.

Stance: keep a tool only if the *interaction* is unfamiliar. A new name on grep, diff, env, cmp, sha256sum, or mergetool is a kill even when the demo is green. Honesty FIXes are not novelty. JSON encodings are not objects. Multiple KEEP is allowed. Polish is not a score. Sum is not a ranking. Ranking key is **novelty then primitive**.

`FIRST_HERETIC` (`lab-hdd/judges/FIRST_HERETIC.md`) is first-selection evidence, not a ranking to rubber-stamp. That judge closed on the seven `candidate-*` embodiments. This one has DESTROYER batteries and the Gen-3 / mutation objects that did not exist then. Disagreement with the first heretic is the job. Disagreement with Unix / Toolsmith / Skeptic is the job. Do not average.

Targets (origins hidden until after the cut):

- `lab-hdd/lineages/gen3-01__whence-empty`
- `lab-hdd/lineages/gen3-02__envfrom-dir`
- `lab-hdd/lineages/gen3-03__stated-honest`
- `lab-hdd/lineages/gen3-04__effect-compact`
- `lab-hdd/lineages/mutation-02__owes-strict`
- `lab-hdd/lineages/mutation-04__capdiff-json`

All six `./demo.sh` runs exited 0. All six shipped test suites exited 0. Empirical credibility is therefore not a differentiator. The cut is the remaining operation after the name is stripped.

same and hits are not in this jury. Destroyers already killed them as primitives. This judge would still KEEP same’s refusal-to-guess identity and still KILL hits as grep-with-the-empty-bit-flipped. Out of scope.

---

## Stance

The night produced three interactions a developer has not typed, two compositions that are not quite grep, and one named `diff`.

**One unseen object, one verb.** Whence is refuse-unmarked-mix: a hybrid is illegal unless every non-common span is parent-tagged, and the product is the blob *plus* the parentage list. Envfrom is empty-override vs inherited: `printenv` cannot show a wipe that has not happened yet. Effect is the deferred-name join: `timeout` sites that say `${WAIT}` / `os.getenv("WAIT")` pull WAIT into the same record; EFFECTIVE is unknown unless the layers statically agree. Those are not the same filter.

Stated is the disagreement pair, not a hit list. Owes is leftover mentions a change still owes. Capdiff is `sha256sum` + `diff` + `env` with a folder for a name.

Gen-3 FIX (empty hybrid, `--dir` missing-tree honesty, `.env` is not a declaration, compact JSON on the joint record) completed contracts. It did not mint new verbs. `--json` on capdiff is encoding. Do not promote a FIX commit to a keep.

Preserve the strange strong primitives even when DESTROYER named lethal holes. Mutate the hole. Do not throw away the verb because the sidecar used to wipe a hunk.

Do not collapse stated into effect. Do not collapse envfrom into effect. Three questions.

---

## Ranked keep (novelty + primitive)

Five objects. Vehicles named. **Do not collapse.** Order is the ranking.

| # | Object (not the CLI) | Vehicle | N | P |
| --- | --- | --- | ---: | ---: |
| 1 | Hybrid is illegal unless every non-common span is parent-tagged; empty is not a merge | **whence** | 4 | 5 |
| 2 | File empty-override vs inherited process value, would-apply vs did-apply | **envfrom** | 4 | 4 |
| 3 | Names sites defer to ride with the key; EFFECTIVE refuses to pick a winner | **effect** | 4 | 4 |
| 4 | Declaration-vs-assignment **pair** (not a hit list); dotenv is not a declaration | **stated** | 3 | 3 |
| 5 | Leftover identifiers a change still owes | **owes** | 3 | 3 |

KILL: **capdiff** — labeled `{env map, file hashes}` is a filing convention. `--json` did not change the compared object.

Carry, not extra ranks: stdin hybrid and empty-sidecar refuse are peels of whence. `--dir` missing-tree / BOM / invalid UTF-8 are peels of envfrom. Compact JSON and quote-masking are peels of stated. Compact JSON on the joint record is a peel of effect. Strict `MUST exist:` / `required file:` (not backtick-after-must) is a peel of owes, not a second product.

---

## Survivors, scored

Primitive in one sentence. Decision. Mutation. Evidence. Ranking comment vs first heretic where it moves.

Axes: Novelty / Utility / Primitive / Composability / Empirical / Evolution / Reality-Stripped. Integer 0–5. One paragraph each.

### 1. whence — tagged hybrid + refuse unmarked / empty

Shipped CLI: `./whence` (`python3 whence`; zsh already owns the word).

N4 U4 P5 C4 E5 X4 RS4. **Keep. Rank 1. Unchanged vs FIRST_HERETIC.** Empty-sidecar refuse completed the contract; it did not mint a second verb.

The interaction that is not mergetool: a hybrid whose contested spans must be tagged `[ours:…]` / `[theirs:…]`, untagged text must be a substring of *both* parents, and a JSON provenance list names the parent of every kept contested span. Untagged mix leaves the conflict markers in the file and writes no `.prov`. An empty sidecar / empty stdin / whitespace-only pipe is exit 3, markers stay, no `"mode": "empty"`. That last clause is the Gen-3 honesty: a forgotten empty file is not a successful tagged merge.

This judge watched, on this machine:

```text
[ours:color = red]
size = [theirs:2]
```

resolved to `color = red` / `size = 2` with spans ours `"color = red"`, theirs `"2"`. The same sidecar without tags: exit 1, file still conflicted. `touch empty-hybrid && python3 whence resolve conflict.txt --hybrid empty-hybrid` → exit 3, stderr `An empty sidecar is not a hybrid and must not wipe the hunk`, markers still at lines 2/5/8. `git merge-file --ours` printed `color = red` / `size = 1` and stopped. A throwaway two-branch `git merge` produced real `<<<<<<< HEAD` markers; `--ours` kept `value = 1\n`.

| Axis | Score |
| --- | ---: |
| Novelty | 4 |
| Utility | 4 |
| Primitive strength | 5 |
| Composability | 4 |
| Empirical credibility | 5 |
| Evolution potential | 4 |
| Reality-Stripped Strength | 4 |

**Novelty (4).** Conflict markers are old. `--ours` is `git merge-file --ours`. The contract is not: you may not emit a hybrid unless every non-common span is parent-tagged, and the product is the resolved text *plus* the parentage list, and empty is not a parent. DESTROYER_WHENCE reconstructed unique tokens from git stages without whence — the user typed the tags; `.prov` is persistence of a mapping already declared. That does not make the refusal ordinary. Mergetool will happily emit `color = red` + `size = 2` with no record. Whole-side paste into `--hybrid` is still refused (`test_untagged_ours_copy_refused`). Diff3 `|||||||` is still refused. The tagging language is the unfamiliar part. Empty-hybrid refuse is the same language, closed.

**Utility (4).** Real overlapping `value = 1` vs `value = 2` produced two-parent markers. Messy three-region fixture with nested `\"` and no trailing newline resolved; a short sidecar named `region 3/3 … MISSING tagged block` instead of dying opaquely. You would run this on a conflicted file when you need the parent list or the hard fail. You would not run it as a mergetool driver (there is none). `FILE -` without `--output` no longer writes a file named `-` (exit 3). That is hygiene, not the product.

**Primitive strength (5).** One primitive: every kept contested span has an explicit parent, or the tool refuses and the file is untouched. Report, ours, theirs, per-region `--choice`, tagged hybrid, empty hybrid, dual-stdin, and FILE-as-stdin-without-output are all that primitive. No JS/YAML intelligence, no TUI, no invented merge, no `mode: empty`. Strong and small. DESTROYER skip-middle (tagged extract, not cover) and unique-vs-shared provenance are mutations of the same law, not a reason to delete it.

**Composability (4).** Provenance is JSON on stdout and `FILE.prov`. `--prov -` skips the sidecar. `--output` and `--hybrid -` are filter-shaped. Hybrid blocks split on `%%`. FILE `-` requires `--output`. The tagging language is a second syntax you have to learn; Unix would score this down for not being a pure text filter. The heretic keeps the language because it *is* the interaction. zsh `whence` is a real pipe hazard; invoke `python3 ./whence`.

**Empirical credibility (5).** Demo covered ours, theirs, file sidecar, stdin sidecar, generated pipe, BOM stdin, empty stdin, empty file sidecar, FILE `-` without `--output`, dual stdin, untagged refusal, diff3 refusal, `git merge-file` contrast, a throwaway two-branch merge, messy quotes, short sidecar, wrong-parent tag, xxd tail (`23 2065 6f66` = `# eof` with no final NL). 31 tests against the shipped file, including `test_hybrid_empty_file_sidecar_refused` and `test_untagged_ours_copy_refused`. Extra probe: empty sidecar on a copied `simple.conflict` left markers in place.

**Evolution potential (4).** Honest next cuts: mergetool/`merge` driver that writes `.prov` or a git note; unique-vs-shared span flags (DESTROYER §9); cover-or-explicit-drop for skip-middle (DESTROYER §8). Death mode is becoming a semantic merge engine, or SequenceMatcher auto-tags that soften refuse-mix. The refuse-unmarked-mix / refuse-empty contract should stay.

**Reality-Stripped Strength (4).** Ignore the name. Operation: parse `<<<<<<<` / `=======` / `>>>>>>>`, accept only an explicit parent choice per region or per tagged span, refuse empty hybrid, write text, write parentage. Nearest ordinary workflow: edit the markers, or `git merge-file --ours|--theirs`, or a mergetool. What is lost if that workflow replaces this: the per-span parent list, the hard fail on unmarked mix, and the hard fail on empty-as-success. Ordinary tools will emit a blob and forget. That loss is real.

Unix would KEEP too, and would grumble that `--ours` is `git checkout --ours`. The heretic KEEP is for the tagged hybrid and the refusals, not for whole-hunk ours/theirs. DESTROYER: mutate, do not kill. Agree.

---

### 2. envfrom — empty-override vs inherited

Shipped CLI: `./envfrom`.

N4 U4 P4 C4 E5 X3 RS4. **Keep. Rank 2. Unchanged vs FIRST_HERETIC.** `--dir` missing-tree / BOM / invalid UTF-8 are honesty, not a new fact.

The interaction that is not `printenv`: a key can be inherited, assigned at a dotenv `file:path:line` (including emptying it), or unset — and `--run` without `--load` prints the *would-apply* override while the child still has the inherited value.

This judge watched, with process `LIBRARY_PATH=/usr/local/lib:/usr/lib` and fixture `.env` line 2 `LIBRARY_PATH=`:

```text
LIBRARY_PATH
VALUE=
SOURCE: file:…/fixtures/empty-override/.env:2
EMPTY_OVERRIDE: yes
INHERITED: /usr/local/lib:/usr/lib
```

`printenv LIBRARY_PATH` still `/usr/local/lib:/usr/lib` after the report. `--fail-empty` exit 2. `--run` without `--load`: child `LIBRARY_PATH=/usr/local/lib:/usr/lib`. `--run --load`: child `LIBRARY_PATH=''`. `--dir /no/such/envfrom-dir` is `directory not found`, exit 1, not a silent `SOURCE: env`. Invalid UTF-8 `.env` is exit 1 without a traceback. UTF-8 BOM on the first key is stripped (`FOO=bom` kept).

| Axis | Score |
| --- | ---: |
| Novelty | 4 |
| Utility | 4 |
| Primitive strength | 4 |
| Composability | 4 |
| Empirical credibility | 5 |
| Evolution potential | 3 |
| Reality-Stripped Strength | 4 |

**Novelty (4).** `env` prints values. `direnv status` prints loading. Neither answers “which file line would wipe `LIBRARY_PATH`, and what did I inherit.” Empty file assignment vs inherited process value, plus would-apply vs did-apply (`--run` without `--load`), is an unfamiliar pair of facts in one block. Not `env` with a new name. `--json` is the same record as an array of objects `{key, value, source, empty_override, inherited}` with `inherited: null` not the text token `(unset)`. Encoding.

**Utility (4).** People paste `.env` next to inherited `LIBRARY_PATH` / `PYTHONPATH` and then cannot tell why a child is empty. `--fail-empty` is a gate. `--load` is an explicit apply, not a silent side effect of reporting. PATH dump is honest and noisy; the interesting row is next to it. Missing `--dir` while cwd has no `.env` still reports `SOURCE: env` — that is cwd-default, not the missing-DIR bug. The bug was `--dir /no/such/dir` printing inherited PATH as if the tree existed.

**Primitive strength (4).** Per-key source: `env` | `file:<path>:<line>` | `unset`, with empty-override as a first-class flag and inherited value retained. Later files win (`.env.local`). That is one primitive. `--run`/`--load` are the same primitive applied to a child, not a second product. `--dir` that is a file / `/dev/null` / a directory named `.env` / a self-symlink `.env` is exit 1, not a silent inherit. Same primitive, fewer lies.

**Composability (4).** Keys as args, `--dir`, `--fail-empty` exit 2, `--run -- CMD` exec, `--json`. Block-formatted stdout is a bit rigid (newlines in values would smash it; `--json` already round-trips). Does not edit files. `--json --run` still concatenates the JSON document and the child on the same stdout — a mutate, not a keep-reason.

**Empirical credibility (5).** Demo hit empty-override, fail-empty, would-apply vs load, quoted/export/inline-comment/empty-quoted, `--dir` here-vs-there, missing DIR, BOM, invalid UTF-8. 31 tests including `.env.local` wins, `--fail-empty` blocking exec, `/dev/null` as DIR, self-symlink dotenv. Extra probe: `printenv` after a no-`--load` report still showed the inherited `LIBRARY_PATH`.

**Evolution potential (3).** Source *chain* when both `.env` and `.env.local` set the key; relative SOURCE paths; newline encoding in text `VALUE=`. Interpolation / `KEY+=` is how it becomes direnv. Keep provenance; do not become a loader with extra verbs.

**Reality-Stripped Strength (4).** Ignore the name. Operation: for each requested key, say whether the effective value is process env, a dotenv assignment at file:line, or unset, and whether a file assignment is empty (including the inherited value it would wipe). Nearest ordinary workflow: `printenv KEY` plus `cat .env`. What is lost: the empty-override fact when the process still has a value (because the loader has not run), the file:line, and the would-vs-did split. `printenv` cannot show a wipe that has not happened yet. That is the whole point.

Unix would KEEP. Agreement.

---

### 3. effect — deferred-name join as one record

Shipped CLI: `./effect`.

N4 U3 P4 C4 E5 X3 RS4. **Keep. Rank 3. FIRST_HERETIC never saw this.** Do not fold it into stated. Do not fold it into envfrom.

The interaction that is not `stated KEY; envfrom KEY`: name a configuration key; emit one record with DECLARED, ASSIGNED, ENV_SOURCE (the key, its case variant, and names those sites defer to), and EFFECTIVE (a comparable scalar if the layers statically agree; otherwise `unknown` with a reason). Exit 2 only on declared-literal vs assigned-literal. Dotenv is env-layer, never a declaration.

This judge ran the kill test on `fixtures/deferred` (`timeout: ${WAIT}`, `timeout = os.getenv("WAIT")`, `.env` `WAIT=10`, process `WAIT=from-shell`):

```text
stated timeout  → UNKNOWN, interpolation vs call, exit 0
envfrom timeout → SOURCE: unset
envfrom WAIT    → SOURCE: file:.env:1 VALUE=10   # you already had to know WAIT
effect timeout  → ENV_SOURCE WAIT file:.env:1 why=deferred
                  EFFECTIVE 10
                  exit 0
```

Concatenation loses WAIT unless the operator already extracted it. Compact `{"timeout": 5}` vs `timeout = 10` is now DECLARED 5 / ASSIGNED 10 / EFFECTIVE unknown / exit 2 — not a false assigned-only 10.

| Axis | Score |
| --- | ---: |
| Novelty | 4 |
| Utility | 3 |
| Primitive strength | 4 |
| Composability | 4 |
| Empirical credibility | 5 |
| Evolution potential | 3 |
| Reality-Stripped Strength | 4 |

**Novelty (4).** stated answers “do these two literals disagree.” envfrom answers “where does this *named* var come from.” Neither answers “what would this key actually be, given declaration, assignment, and the env names those sites defer to.” The deferred join (`${WAIT}`, `os.getenv("WAIT")`, `os.environ.get`, `process.env.WAIT`) is the unseen part. The four-field dump is a report format around that join. A wrapper that prints both CLIs’ stdout is a mashup and still misses WAIT. This is not that wrapper.

**Utility (3).** “It only broke after I changed the timeout” is a real session, and this is the record you want when the timeout is not a literal. Exit 2 on comparable declared-vs-assigned is scriptable. Nested keys (`server.timeout`) are invisible. `os.getenv("TIMEOUT", "5")` is a call, not a static default — honest, and it means EFFECTIVE stays unknown next to an empty-override TIMEOUT (demo: `unknown literal 5 vs env (empty)`, exit 0). You will not type this every morning. You will type it when the three layers disagree and you do not already know the deferred name.

**Primitive strength (4).** One primitive: names that sites defer to ride with the key; EFFECTIVE is unknown unless layers statically agree. DECLARED / ASSIGNED / ENV_SOURCE are inputs to that decision, not three products. Case-variant TIMEOUT next to key timeout is the same primitive. Compact-JSON leaders are scanner honesty so EFFECTIVE cannot lie “assigned-only 10” when a one-line object declared 5. Silent 2MiB skip that lies about EFFECTIVE is still a hole (DESTROYER_CONFIG 3.4) — mutate, do not kill.

**Composability (4).** `effect KEY [DIR]`, `--json` one object, exit 0/1/2. Pipeable. Does not try to repair. You cannot get stated’s pair without also seeing env provenance — that is a real loss versus running stated alone, and it is why they stay distinct vehicles rather than why effect dies.

**Empirical credibility (5).** Demo: disagree (yaml 5 vs py 10, `.env TIMEOUT=30` in ENV_SOURCE, inherited from-shell retained), agree EFFECTIVE 5, config-only, empty-override deferred TIMEOUT, deferred WAIT EFFECTIVE 10, unknown unset WAIT, comments, `os.environ.get` / `process.env.WAIT`, JSON joint object, compact JSON exit 2. 18 tests including `test_compact_json_declaration_is_not_false_effective` and `test_json_deferred_join`. Extra probe: the concatenation kill test fails on deferred, as claimed.

**Evolution potential (3).** Never emit EFFECTIVE after a silent file skip. Static default of `os.getenv("X", "5")`. Nested key paths. Death: runtime evaluator / config linter / “effective” that picks a winner. Keep the unknown. Do not add auto-fix.

**Reality-Stripped Strength (4).** Ignore the name. Operation: given a key, collect config declarations (not dotenv), source assignments, and env provenance of the key plus names those sites mention as getenv/interpolation; say whether a static effective value exists. Nearest ordinary workflow: `rg KEY`, `cat .env`, `printenv`, then think. What is lost: the deferred-name join as one record, and EFFECTIVE unknown instead of a guessed winner. `stated KEY; envfrom KEY` does not recover WAIT. That loss is the product.

Unix will likely KEEP this as a composition and call it a report. Toolsmith will ask whether anyone types four fields. This judge keeps the join, not the dashboard.

---

### 4. stated — disagreement pair

Shipped CLI: `./stated`.

N3 U4 P3 C4 E5 X3 RS3. **Keep. Rank 4. Same object as FIRST_HERETIC.** Dotenv exclusion and quote-masking are honesty. Compact JSON is a scanner peel. The pair is still the cut. Do not absorb into effect.

The interaction that is not `rg timeout`: the observable is a *disagreement pair* (declaration site vs contradicting site), or an honest non-comparison. Demo, disagree fixture (`config.yaml` `timeout: 5` vs `app.py` `timeout = 10`):

```text
status: DISAGREE
disagreement:
  declared     5	config.yaml:1	timeout: 5	value=5
  contradicted 10	app.py:3	timeout = 10	value=10
exit: 2
```

Interpolation vs `os.getenv("WAIT")` printed `UNKNOWN` / `not comparable: interpolation` / `not comparable: call`, exit 0. Comments and docstrings listing `99` were labeled and ignored. Compact `{"timeout": 5}` is a declaration (DISAGREE vs `timeout = 10`). `.env timeout=99` / `TIMEOUT=30` is not: `stated timeout` on that tree still pairs yaml 5 vs py 10 and does not mention `.env`; `stated TIMEOUT` is NONE, not DECLARED_ONLY 30. `msg = "timeout = 99 is wrong"` is not an assignment (DECLARED_ONLY 5).

This judge’s `rg -n timeout` on the dotenv fixture hit the docstring, the assignment, and the yaml line, and skipped `.env` because it is hidden. `rg --hidden` would have treated dotenv as another hit. stated’s cut is not “skip hidden files”; it is “dotenv is a different layer.” Extra probe confirmed TIMEOUT from `.env` is NONE.

| Axis | Score |
| --- | ---: |
| Novelty | 3 |
| Utility | 4 |
| Primitive strength | 3 |
| Composability | 4 |
| Empirical credibility | 5 |
| Evolution potential | 3 |
| Reality-Stripped Strength | 3 |

**Novelty (3).** Walking a tree for `KEY:` / `KEY=` is grep. The cut that is not grep is: pair comparable scalars across config-shaped files and source-shaped files, refuse to compare interpolations and calls, park comment hits, and treat dotenv as not-a-declaration. That is a small unfamiliar output, not a new search. Close to a rename; the pair keeps it alive. Dotenv exclusion makes stated *more distinct* from envfrom/effect, not more novel. Quote-masking is a false-assignment peel (DESTROYER_CONFIG 2.5). Compact JSON is the same pair on a one-line object.

**Utility (4).** “It only broke after I changed the timeout” is a real session. Exit 2 on comparable disagreement is something a script can branch on. Nested keys (`server.timeout`) are invisible; that is an honest limit. Case-sensitive: `timeout` does not match `TIMEOUT`. You would run this. You would not install it tomorrow.

**Primitive strength (3).** The primitive is the disagreement pair, not the hit list. Implementation is line regex plus a comment tracker plus a quote mask, not parsers. Same-side contradiction is handled. It will still lie on `/* x */ int timeout = 5;` on one line. Strong enough to keep, not a new law of nature. Scanner remains grep-shaped. Mutate the scanner; do not delete the pair.

**Composability (4).** `stated KEY [DIR]`, `--json`, exit 0/1/2. JSON carries pairs, declarations, assignments, comments. Pipeable. Does not try to repair. Missing DIR exit 1.

**Empirical credibility (5).** Demo: disagree, agree, declared-only, unknown, comments, JSON pair, compact JSON, dotenv-not-decl, TIMEOUT NONE, string-literal not-assignment. 22 tests including identifier-boundary (`timeout` vs `timeout_ms`), comment separation, dotenv excluded from JSON declarations, real assignment still pairs next to a string mention.

**Evolution potential (3).** Nested key paths, case-insensitive env keys, typed Python assignments. The death is “becomes a config linter / typechecker” or “becomes effect.” Keep the pair; do not add auto-fix; do not merge the binary with effect.

**Reality-Stripped Strength (3).** Ignore the name. Operation: given a key, find declaration-shaped lines in config files (not dotenv) and assignment-shaped lines in source, compare literals when both look like scalars. Nearest ordinary workflow: `rg KEY` in yaml and py, then read both. What is lost: automatic pair emission, exit 2, UNKNOWN instead of a false equal, comment hits parked, dotenv not counted as a declaration. You can do this by eye on a small tree. The tool is the eye-skip, not a new object. Enough.

Unix FIRST KILL’d parent stated as grep-plus-status. This judge still keeps it for the pair-as-observable, not for the scanner. Mild disagreement on how new it is; live disagreement on the verdict. DESTROYER_CONFIG: do not honor Unix as a KILL. Agree with DESTROYER on that.

---

### 5. owes — leftover identifiers a change still owes

Shipped CLI: `./owes`.

N3 U3 P3 C4 E5 X4 RS3. **Keep. Rank 5. Cold keep. Same object as FIRST_HERETIC.** Strict companions closed a Skeptic landmine. They did not deepen the verb. The leftover-identifier join is the keep. The planted `MUST exist:` phrase is not a product.

The interaction: a change (unified diff, or before/after snapshots) plus the remaining tree, then two obligation kinds — removed identifiers still mentioned, and companion paths remaining docs still require via a closed phrase set.

Deleted-function fixture:

```text
unkept references:
  validate_input
    README.md:3: Call `validate_input` before saving user data.
exit: 2
```

Missing-companion fixture no longer names `docs/adr.md` from `must read \`docs/adr.md\``. Prose-backticks fixture (`must see \`README.md\`` and no `MUST exist:`) is `no unkept obligations`, exit 0. Parent `candidate-03__owes` on that same fixture flags `README.md`. Clean helper-delete: exit 0.

This judge’s Unix composition on the leftover:

```text
rg '^-[^-]' fixtures/deleted-fn/change.diff   # -def validate_input(value):
rg -n 'validate_input' fixtures/deleted-fn/tree
# README.md:3: Call `validate_input` before saving user data.
```

owes joins those. That join is the whole object.

| Axis | Score |
| --- | ---: |
| Novelty | 3 |
| Utility | 3 |
| Primitive strength | 3 |
| Composability | 4 |
| Empirical credibility | 5 |
| Evolution potential | 4 |
| Reality-Stripped Strength | 3 |

**Novelty (3).** “Names the diff deleted that remaining files still mention” is `git diff` plus `rg`. The slightly unfamiliar question is *what does this change still owe*. Cross-method: previous brrr’s zanei asked leftover *claims* a diff made false. This is the thinner cousin (identifiers, not typed claims). Independent rediscovery is evidence the question is real, not a reason to inflate the score. The `MUST exist:` / `required file:` phrases remain a planted mini-DSL — the fixture was written for the matcher. Strict-vs-parent is “do not fire on `must see \`README.md\``.” That is a landmine fix, not an unfamiliar interaction. Smell, not a kill.

**Utility (3).** Stale README after deleting `validate_input` is a review moment. A moved function is still reported (false unkept). Comment-only leftovers count. Companion check only looks at `*.md` and is not bound to files the diff touched. Useful on the fixtures; noisy on a real rename. Absolute host paths (`/etc/passwd`) are no longer omitted just because they exist on the host (DESTROYER FIX). Still not a thing you install.

**Primitive strength (3).** Two related obligations, one scan. Identifier extraction is `def|class|function|fn|…` and `CONST =`. Companion paths are two regexes. Unified-diff headers now require `--- ` / `+++ ` / `@@ ` so a deleted `--def validate_input():` encoded as `---def validate_input():` is a minus line, not a file header (DESTROYER FIX). The primitive is real; the extraction is thin. Next mutation must bind companions to the change and skip identifiers that still have a definition. More phrase regexes is death.

**Composability (4).** `owes DIR` with two snapshot layouts, or `--tree` + `--diff`. `--json`. Exit 0/2/1. Tests invoke the shipped process. Fits a pre-commit or review pipeline without becoming a policy engine. Stdin ignored (`cat change.diff | owes` is usage) — awkward, honest.

**Empirical credibility (5).** Demo asserted four fixtures (deleted-fn, missing-companion, clean, prose-backticks). 14 tests: JSON shape, `--tree/--diff`, plus-line changelog skip, dash-def minus line, absolute host path, usage errors. Extra probe: `rg` recovers the leftover identifier; owes is the join.

**Evolution potential (4).** Skip identifiers that still have a definition in the remaining tree (kills the move false-positive). Optionally ignore comment-only mentions. Bind missing companions to files the diff actually touched. Search tests for MUST-like phrases. Those mutations deepen the same primitive. Death: CVE/ticket oracles, or a growing phrase lexicon.

**Reality-Stripped Strength (3).** Ignore the name. Operation: parse removed identifiers from a unified diff; search the remaining tree; also look in remaining markdown for two required-path phrases and test existence inside the tree. Nearest ordinary workflow: `git diff` + `rg validate_input` + `test -f`. What is lost: the change and the leftover mentions as one report, and the companion miss as a first-class row. Most of the value is recoverable with two Unix tools; the bundling is the delta. Previous-night zanei is the stronger object in this family if anyone still has it.

Unix FIRST KILL’d parent owes (snapshot protocol). This judge KEEP is reluctant: the identifier half is familiar, the companion half is half-invented. Still a survivor because the *question* is not “grep the repo”, it is “what did this change fail to keep.” DESTROYER: mutate, not kill. Agree. If the next cut is more phrases, kill then.

---

## Kill

### capdiff — named dumps. `--json` is not an object

Shipped CLI: `./capdiff`.

N2 U3 P2 C3 E5 X2 RS2. **Kill. FIRST_HERETIC kill stands.** Ordinary mutation added a JSON encoding of the same six buckets. DESTROYER said mutate the compared object; they encoded it instead.

Demo captured fixture env-a vs env-b, printed ENV modified `API_KEY` local vs remote, FILES extra `extra.txt`, exit 2; replay printed `local-ci-key` / `remote-ci-key`; missing `.env` captured as empty env map. `--json` emits `{a, b, env, files}` with object arrays. Extra/missing are `{key, value}` / `{path, hash}`, not the text line `API_KEY=local-ci-key`. Identical JSON is six empty arrays, exit 0.

This judge’s honesty check: `diff -ru .capdiff/a .capdiff/b` showed the same `.env` delta and the same extra `extra.txt` hash in the manifests. `sha256sum` of the live trees matched the FILE hashes. The labeled store is a directory `diff -ru` already reads.

| Axis | Score |
| --- | ---: |
| Novelty | 2 |
| Utility | 3 |
| Primitive strength | 2 |
| Composability | 3 |
| Empirical credibility | 5 |
| Evolution potential | 2 |
| Reality-Stripped Strength | 2 |

**Novelty (2).** Named snapshot of `.env` plus sha256 of relative paths, then diff, then `exec` with overlayed env. That is `sha256sum` + `diff` + `env KEY=val cmd` with a `.capdiff/NAME` directory as the label. “Labeled capture not ad-hoc dump” is a filing convention, not a new operation. ENV vs FILES both reporting `.env` (parsed keys *and* bytes, including comments) is a mild twist, not an unfamiliar interaction. `--json` is the same six buckets as a document. Empty buckets as `[]` instead of `(none)` is encoding. `NAME=.` / `NAME=..` rejected, corrupt manifest no traceback, truncated captures not claimed identical: FIX pack. Green FIX is not a keep.

**Utility (3).** Local-CI key vs remote-CI key is a real “why did this job see a different secret” moment. Replay does not restore file bodies — capture never stored them — so `--files` writes only `.env`. Overlay does not unset host vars absent from the capture. Useful as a reminder; not a reproducer. Truncation at 5000 files used to claim identity while trees differed; the test now refuses that lie. The compared object is still hashes, not bodies.

**Primitive strength (2).** The compared object is a directory of `{env map, file hashes}`. That is a bundle, not a primitive. Three subcommands (capture / diff / replay) already want to be a small product. Replay is `os.execvpe` after copying env. JSON did not shrink it.

**Composability (3).** Names, exit 2 on delta, JSON on stdout, JSON manifest on disk. You can `capdiff diff a b` in CI. You cannot compose it as a filter. The store is hidden state in cwd. `diff -ru .capdiff/a .capdiff/b` is the composition that already existed.

**Empirical credibility (5).** Demo and 21 tests did what they claimed, including JSON extra/missing as objects, embedded `=`, `.` / `..` rejected, corrupt manifest, truncated-not-identical, env-only replay in a tree that has no live `API_KEY`. Green is not a keep.

**Evolution potential (2).** Store bodies, `env -i` unset, include/exclude globs, env-from-`os.environ`. Those mutations make it rsync/direnv. FIRST_HERETIC already said the current object is too thin to deepen without becoming those tools. `--json` was the mutation they spent. It did not change the object. Kill rather than wait for the next flag.

**Reality-Stripped Strength (2).** Ignore the name. Operation: copy `.env` if present, hash files, diff two such records, overlay env and exec. Nearest ordinary workflow: `diff -ru`, `sha256sum`, `env`. What is lost: a name on the pair so you do not forget which dump was local. That is bookkeeping. If the ordinary workflow replaces this tool, almost nothing operational is gone; you still see `API_KEY` differ and `extra.txt` exist. This judge watched `diff -ru` of the store say so.

**Unix disagreement.** A Unix judge is likely to KEEP this as a tidy composition (three verbs, text output, exit 2, now JSON). FIRST_UNIX KILL’d parent capdiff. Live disagreement is therefore inside Unix, not only heretic-vs-Unix. This judge kills it either way: familiar tools with a store directory. The experiment does not need another named `diff`.

DESTROYER_REST: MUTATE (`--json` is encoding). This judge does not MUTATE a renamed Unix. **KILL.**

---

## Summary

| Lineage | Novelty | Utility | Primitive | Composability | Empirical | Evolution | Reality-Stripped | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| gen3-01 whence-empty | 4 | 4 | 5 | 4 | 5 | 4 | 4 | **KEEP** |
| gen3-02 envfrom-dir | 4 | 4 | 4 | 4 | 5 | 3 | 4 | **KEEP** |
| gen3-04 effect-compact | 4 | 3 | 4 | 4 | 5 | 3 | 4 | **KEEP** |
| gen3-03 stated-honest | 3 | 4 | 3 | 4 | 5 | 3 | 3 | **KEEP** |
| mutation-02 owes-strict | 3 | 3 | 3 | 4 | 5 | 4 | 3 | **KEEP** |
| mutation-04 capdiff-json | 2 | 3 | 2 | 3 | 5 | 2 | 2 | **KILL** |

KEEP (5): **whence**, **envfrom**, **effect**, **stated**, **owes**.

KILL (1): **capdiff**.

What survived is not polish. **whence** keeps a parent-tagged resolve that mergetools throw away, and now refuses empty as a merge. **envfrom** keeps empty-override vs inherited and would-apply vs did-apply. **effect** keeps the deferred-name join that `stated KEY; envfrom KEY` loses. **stated** keeps the disagreement pair (not a hit list; dotenv is not a declaration). **owes** keeps “what this change still owes,” even though half of it is grep-after-diff.

What died is a named `diff` of env+hashes, including its JSON coat.

Do not average these with Unix / Toolsmith / Skeptic / Reality-Stripped. If those judges KEEP capdiff, that is disagreement, not a vote to resurrect. If they KILL stated or owes, that is the Unix/Skeptic hole this judge already named and declined.

---

## vs FIRST_HERETIC

Independent. First heretic was right about a lot. The night moved.

| Object | FIRST_HERETIC | this judge |
| --- | --- | --- |
| **whence** | KEEP N4 P5. Tagged hybrid + refuse unmarked mix. | **Keep. Rank 1.** Empty hybrid from any source is now refused. Same verb. |
| **envfrom** | KEEP N4 P4. Empty-override vs inherited. | **Keep. Rank 2.** `--dir` missing is exit 1. Same verb. |
| **stated** | KEEP N3 P3. Pair, not hit list. | **Keep. Rank 4.** Dotenv out; compact JSON in; quote-mask. Same verb. Not absorbed by effect. |
| **owes** | KEEP N3 P3, reluctant. | **Keep. Rank 5, colder.** Strict companions are a landmine FIX. Identifier join still the object. |
| **capdiff** | **KILL** N2 P2. Named dumps. | **Kill.** `--json` is encoding. `diff -ru` of the store is the tool. |
| **effect** | did not exist | **Keep. Rank 3. Elevate.** Deferred-name join is the hybrid that is not concatenation. |
| **same** | KEEP (refusal to guess) | not in this jury; destroyer KILL primitive. Heretic would still keep the refusal. |
| **hits** | KILL (grep empty-exit) | not in this jury; destroyer KILL. Heretic kill stands. |

### Elevate (first heretic could not rank)

| object | why |
| --- | --- |
| **effect** | Kill test `stated KEY; envfrom KEY` fails on deferred WAIT. Four-field record is the join, not a mashup. Compact JSON FIX closed a false EFFECTIVE. Distinct from stated. Distinct from envfrom. |

### Downrank / unchanged

| object | move |
| --- | --- |
| **owes** | Carry, colder. Parent backtick-after-must was a Skeptic landmine; closing it did not make leftover-identifiers less like `git diff` + `rg`. zanei is the stronger object in the family. |
| **capdiff** | Kill stands. JSON was the ordinary mutation. It encoded the trenchcoat. |
| **stated** | Unchanged rank-class (N3). Honesty cuts made it a cleaner pair, not a stranger one. |

Do not treat DESTROYER MUTATE as a heretic KEEP. DESTROYER MUTATE on capdiff meant “the compared object is still a directory of hashes.” That is a kill sentence with a polite verb.

---

## Unix disagreement (predicted / first-selection)

Do not wait for FINAL_UNIX. First-selection Unix already split.

| Object | Unix FIRST | this judge | the disagreement |
| --- | --- | --- | --- |
| whence | KEEP | KEEP | Agreement on verdict. Unix likes `--ours` more than this judge does. |
| envfrom | KEEP | KEEP | Agreement. |
| stated | **KILL** | **KEEP** | Unix: grep-plus-status. Heretic: the pair is the observable. Live. |
| owes | **KILL** | **KEEP** | Unix: snapshot protocol / composition. Heretic: leftover-owe is a question. Reluctant live. |
| capdiff | **KILL** | **KILL** | Agreement (Unix FIRST). A later Unix that KEEP’s JSON capdiff is the renamed-diff temptation. Heretic veto. |
| effect | (none) | KEEP | Unix may KEEP as composition or KILL as a report. Heretic KEEP is the WAIT join. |
| hits | KEEP | (out of scope, would KILL) | The live first-selection split. Not this jury. |
| same | KEEP | (out of scope, would KEEP) | Toolsmith/Skeptic killed; heretic kept the refusal. Destroyer later killed the primitive. |

Preserve this split. Averaging it is a sixth judge in a trenchcoat.

---

## Tomorrow Test

Deliberately small. Empty slots allowed. This slot is empty.

Install and try tomorrow:

*(none)*

Remember without PATH:

- **whence** — only the refuse: unmarked mix and empty sidecar are not merges. Do not install a mergetool you have to teach `[ours:…]`.
- **envfrom** — the fact: `LIBRARY_PATH=` at file:line vs inherited process value, would-apply vs `--load`. Type it in the incident; do not add a daily binary for a question-word.
- **effect** — WAIT rides with timeout. A record, not a PATH entry.

stated and owes are breeding objects. capdiff is dead.

Toolsmith may fill PATH. Skeptic may put envfrom on the desk. This judge does not install. Unfamiliar interactions are to preserve, not to abundance. Empty remaining slots.

---

## Origins (after the cut)

Hidden until the objects were scored.

| lineage | origin (after) |
| --- | --- |
| gen3-01 whence-empty | hdd-merge → candidate-01 → mutation-03 stdin → Gen3 FIX empty hybrid / FILE `-` |
| gen3-02 envfrom-dir | hdd-env → candidate-05 → mutation-01 json → Gen3 FIX `--dir` / BOM / invalid UTF-8 |
| gen3-03 stated-honest | hdd-debug → candidate-02 → mutation-05 jsonobj → Gen3 honesty (dotenv out, quote-mask) |
| gen3-04 effect-compact | hybrid stated×envfrom → Gen3 FIX compact JSON on the joint record |
| mutation-02 owes-strict | hdd-agent → candidate-03 → strict companions + dash-def / host-path FIX |
| mutation-04 capdiff-json | hdd-ci → candidate-04 → `--json` encoding of the same six buckets |

HDD-only questions that survive this jury: parent-tagged merge provenance; empty-override vs inherited; deferred-name EFFECTIVE. Leftover obligations independently rediscovered (owes ∥ zanei). Named env+file `diff` did not become an interaction by growing a JSON document.

Dreamer transcripts were not evidence.

---

## Execution (this judge, 2026-09-02 ~07:41 JST)

All runs in the lineage directories. Extra probes in `/tmp/final-heretic-probes` and a throwaway capdiff cwd.

| Lineage | `./demo.sh` | tests | extra |
| --- | ---: | --- | --- |
| gen3-01 whence-empty | 0 | 31 OK | empty sidecar left markers, rc=3 |
| gen3-02 envfrom-dir | 0 | 31 OK | `printenv` after no-`--load` still inherited |
| gen3-03 stated-honest | 0 | 22 OK | `rg timeout` vs dotenv-not-decl; TIMEOUT NONE |
| gen3-04 effect-compact | 0 | 18 OK | `stated`; `envfrom timeout`; `envfrom WAIT`; `effect` on deferred |
| mutation-02 owes-strict | 0 | 14 OK | `rg` leftover identifier; prose-backticks rc=0 |
| mutation-04 capdiff-json | 0 | 21 OK | `diff -ru .capdiff/a .capdiff/b` same delta |

Green is not a keep. Capdiff was the greenest renamed Unix in the set.
