# Final Jury — Reality-Stripped

Judge: Reality-Stripped. Date: 2026-09-02. Window: 07:40–08:20.

Scope: shipped CLIs under

- `lab-hdd/lineages/gen3-01__whence-empty`
- `lab-hdd/lineages/gen3-02__envfrom-dir`
- `lab-hdd/lineages/gen3-03__stated-honest`
- `lab-hdd/lineages/gen3-04__effect-compact`
- `lab-hdd/lineages/mutation-02__owes-strict`
- `lab-hdd/lineages/mutation-04__capdiff-json`

Names, HDD origin, generation labels, and “FIX/mutation” lore are ignored until after the operation is named. The question is what remains if the label is peeled off, and whether replacing that remainder with an ordinary workflow loses an observable.

Method: read README.md and the shipped file; run `./demo.sh` and the unittest suite in each lineage directory in this session. Substitution probes against `git merge-file`, `printenv`/`grep`, `rg`, `stated`+`envfrom` concatenation, parent `owes`, and `diff -ru` were run on the same fixtures. Did not read other final-jury reports. Did not average with Unix / Toolsmith / Heretic / Skeptic.

Empirical rule: scores on Empirical credibility are taken from this run, not from README claims.

| Artifact | Demo | Tests | Observed in this run |
| --- | --- | --- | --- |
| gen3-01 | `./demo.sh` exit 0 | 31 OK | Tagged hybrid wrote `color = red` / `size = 2` with spans `ours`/`theirs`. Empty stdin hybrid exit 3, markers stay. Empty file sidecar exit 3, markers stay, no `mode: empty`. `FILE -` without `--output` exit 3, no file named `-`. Untagged mix exit 1, markers stay. `git merge-file --ours` wrote `color = red` / `size = 1` and stopped. |
| gen3-02 | `./demo.sh` exit 0 | 31 OK | `LIBRARY_PATH=` at `.env:2` → `VALUE=`, `EMPTY_OVERRIDE: yes`, `INHERITED: /usr/local/lib:/usr/lib`. `--dir /no/such/envfrom-dir PATH` → `directory not found`, exit 1, not `SOURCE: env`. BOM keeps `FOO=bom`. Invalid UTF-8 exit 1, no traceback. `--run` without `--load` child keeps inherited; `--run --load` child `''`. |
| gen3-03 | `./demo.sh` exit 0 | 22 OK | yaml `timeout: 5` vs `timeout = 10` → DISAGREE exit 2. Compact `{"timeout": 5}` vs `timeout = 10` → DISAGREE. `.env TIMEOUT=30` / `timeout=99` is not a declaration (`TIMEOUT` → NONE). `msg = "timeout = 99 is wrong"` → DECLARED_ONLY 5. `${WAIT}` vs `os.getenv("WAIT")` → UNKNOWN exit 0. |
| gen3-04 | `./demo.sh` exit 0 | 18 OK | Compact JSON: DECLARED 5 vs ASSIGNED 10, EFFECTIVE unknown, exit 2 (not a false assigned-only 10). Deferred: `timeout: ${WAIT}` / `os.getenv("WAIT")` joins `WAIT` from `.env:1` value 10, EFFECTIVE 10. `stated` on the same tree is UNKNOWN and never names WAIT. `envfrom timeout` is unset unless WAIT is already an argument. |
| mutation-02 | `./demo.sh` exit 0 | 14 OK | Deleted `validate_input` still in README → exit 2. `MUST exist: SECURITY.decision.md` / `required file: docs/threat-model.md` → exit 2. Clean helper delete → `no unkept obligations` exit 0. Prose `must see \`README.md\`` → exit 0. Parent `candidate-03` on that same fixture flags `README.md` as a missing companion, exit 2. Plus-line changelog “Removed validate_input” is skipped; leftover README still fires. |
| mutation-04 | `./demo.sh` exit 0 | 21 OK | Diff `a b` exit 2: ENV `API_KEY` local vs remote, FILES extra `extra.txt`, FILES modified `.env` hashes. Replay printed `local-ci-key` then `remote-ci-key`. `--json` is `{a,b,env,files}` object arrays (extra/missing are `{key,value}` / `{path,hash}`, not text lines). Identical `a a --json` six empty arrays, exit 0. `diff -ru` on the live trees mixed comment+key into one hunk and said `Only in … extra.txt`. |

Do not rank by polish, LOC, or README size. A Gen-3 honesty cut is not a new remainder. A JSON encoder is not a new remainder. Kill only if substitution loses nothing observable.

---

## gen3-01 — tagged two-parent resolve + per-span parent ledger (empty hybrid is not a merge)

Shipped file: `whence` (invoked as `python3 ./whence`; a shell builtin of the same word is irrelevant).

### 1. Operation that remains

Parse `<<<<<<<` / `=======` / `>>>>>>>` regions. Resolve only by an explicit parent choice: whole-side ours, whole-side theirs, per-region choice list, or a hybrid sidecar in which every contested span is tagged `[ours:…]` / `[theirs:…]`. Untagged text must be common to both parents. Emit JSON naming the parent of every kept contested span, and write the same document beside the resolved file.

Refuse unmarked mixes, invented text, wrong-parent tags, diff3 `|||||||` ancestor hunks, binaries, a hybrid sidecar with the wrong number of blocks, empty hybrid from stdin **or** from a 0-byte/whitespace file, a TTY on `--hybrid -`, and `FILE -` without `--output PATH`. An empty sidecar is not a successful tagged merge and must not overwrite the hunk.

### 2. Nearest ordinary workflow

`git checkout --ours/--theirs`, `git merge-file --ours|--theirs|--union`, a mergetool, or hand-editing the markers until the file looks right.

### 3. What is lost if that workflow replaces this tool

The merge product stops being a blob-with-forgotten-parents. In this run `git merge-file --ours` printed `color = red` / `size = 1` and stopped. It did not say both lines came from ours, and it cannot say a hybrid took ours' color and theirs' size. The tagged-hybrid contract is also lost: pasting `color = red` + `size = 2` without tags is currently a nonzero refusal that leaves the conflict in place. After replacement, that unmarked mix becomes a silent new file.

The empty-hybrid refuse is the same remainder, closed: `touch empty && resolve FILE --hybrid empty` exited 3 in this run, markers still in FILE. Ordinary mergetools and a forgotten empty sidecar will write nothing over the hunk and call it resolved. That wipe is the capability substitution reintroduces.

`FILE -` requiring `--output` is hygiene (do not create a file named `-`). It is not the remainder.

### Classification

USEFUL_COMPOSITION. The tagged grammar plus the parent ledger is the nearest thing in this set to a new operation (“resolution is a provenance event”). It is still two-parent text merge, not a new universe.

- **Novelty 4.** Whole-hunk ours/theirs is old. Per-span parent list plus refuse-unmarked-mix plus refuse-empty-hybrid is not how merge tools work.
- **Utility 4.** After a hybrid merge, “which parent did this token come from?” is unanswerable from the blob. Two-parent text only; honest boundary.
- **Primitive strength 4.** Explicit parent or tagged span, else refuse. Diff3 refused rather than half-handled. Empty hybrid refused rather than `mode: empty`.
- **Composability 4.** JSON on stdout, sidecar `.prov`, `--prov -`, hybrid on stdin, `--choice`, `--output`. A mergetool driver can sit on top.
- **Empirical credibility 5.** This run: report, ours, theirs, file hybrid, stdin hybrid, BOM stdin, empty stdin, empty file sidecar, `FILE -` refuse, dual-stdin refuse, untagged mix, diff3 refuse, `git merge-file` contrast, real two-branch merge, messy three-region tags, 31/31 tests.
- **Evolution potential 3.** Mergetool driver, provenance as a git note, unique-vs-shared spans. Further growth that understands YAML/JS is a different product.
- **Reality-Stripped Strength 4.** Peel the name off and the operation is still there: tagged two-parent resolve that will not write a blend it cannot attribute, including a blend that is empty.

**KEEP**

---

## gen3-02 — per-variable env provenance, including empty file override (missing DIR is not inherit)

Shipped file: `envfrom`.

### 1. Operation that remains

Name a variable. Report its would-apply value and source: process env, a dotenv `file:path:line`, or unset. A `.env` line `KEY=` (or `KEY=""`) is an empty override even when the process already has `KEY`; the report shows `VALUE=`, `EMPTY_OVERRIDE: yes`, and the inherited value that would be wiped. Later files win (`.env` then `.env.local`). `--run` prints that provenance then execs; `--load` actually applies file assignments onto the child; without `--load` the child keeps inherited values. `--fail-empty` exits 2 if a reported key is empty-overridden.

`--dir DIR` reads dotenv from DIR, not cwd. A missing path, a non-directory, or a `.env` that exists but is not a file is exit 1, not a silent `SOURCE: env`. Invalid UTF-8 is exit 1 without a traceback. A UTF-8 BOM on the first key is stripped.

### 2. Nearest ordinary workflow

`printenv KEY`; `grep KEY .env`; `set -a; source .env`; `direnv status`; `env -C DIR`.

### 3. What is lost if that workflow replaces this tool

`printenv` shows the current map, not which file emptied a key, and not the inherited value that an empty assignment would destroy. In this run, with `LIBRARY_PATH=/usr/local/lib:/usr/lib` in the process and `LIBRARY_PATH=` at `.env:2`:

- `printenv LIBRARY_PATH` → `/usr/local/lib:/usr/lib`
- `grep LIBRARY_PATH .env` → a comment plus `LIBRARY_PATH=`
- this CLI → `VALUE=`, `SOURCE: file:…/.env:2`, `EMPTY_OVERRIDE: yes`, `INHERITED: /usr/local/lib:/usr/lib`

`--run` without `--load` still gave the child the inherited path; `--run --load` gave the child `''`. That would-apply vs actually-loaded split is the remainder. `source .env` applies; it does not explain. `direnv status` shows loader activity, not per-variable file:line vs inherited vs unset.

`--dir /no/such/envfrom-dir PATH` in this run is `directory not found`, exit 1. Substitution with `printenv PATH` (or with a CLI that treats a missing tree as “no dotenv, inherit everything”) reports the live PATH and calls it done. The missing-DIR refuse is honesty of the same remainder, not a new one. JSON is encoding.

### Classification

USEFUL_COMPOSITION. Empty-override-as-sourced-event is a clean cut. `--dir` error policy is not a cut.

- **Novelty 3.** Env dumping is old. “File assigned empty” as a different event from unset and from inherited, with a file:line, is not how dumpers work.
- **Utility 4.** “Why is LIBRARY_PATH empty in the child?” is a real, expensive debug. The fixture is that case.
- **Primitive strength 4.** Name a key, get source. Would-apply versus apply is an honest split. Missing DIR is an error. No interpolation, no `KEY+=`.
- **Composability 4.** Keys as arguments. `--fail-empty`. `--run [--load] -- CMD`. `--json` array of `{key,value,source,empty_override,inherited}`.
- **Empirical credibility 5.** Demo plus 31/31 tests: empty override, fail-empty, run with and without load, `--dir` vs cwd, missing DIR, file-as-DIR, `/dev/null`, BOM, invalid UTF-8, quoted export, JSON round-trip.
- **Evolution potential 3.** Source chain when both files set the same key is the natural next cut. Interpolation clones a shell.
- **Reality-Stripped Strength 4.** Peel the name off and this is still not `printenv`: report which file:line would override this variable, including emptying it, and optionally exec under that story.

**KEEP**

---

## gen3-03 — declaration site vs assignment site as a disagreement pair (dotenv is not a declaration)

Shipped file: `stated`.

### 1. Operation that remains

Name a key. Walk config-like files for `KEY:` / `KEY=` declarations and source files for assignments of the same identifier. Parse a trailing token as a comparable scalar, or as not comparable (interpolation, call, identifier, expression). The observable is a disagreement pair (declaration site vs contradicting site), or a confirmation that comparable scalars agree, that only one side exists, or that comparison is refused.

Dotenv (`.env`, `.env.*`, `*.env`) is not a declaration. Compact JSON `{"timeout": 5, …}` is a declaration. A quoted `timeout = 99` inside a string is not an assignment. Whole-line `#` / `//`, `/* */`, and Python docstrings are labeled comments and ignored for comparison.

### 2. Nearest ordinary workflow

`rg KEY` (or `git grep`) across config and source, then read both hits and compare the numbers by eye. `rg --hidden --no-ignore` if dotenv should even be visible.

### 3. What is lost if that workflow replaces this tool

Grep returns a hit list. This returns a pair, or an honest non-pair.

On `fixtures/dotenv_not_decl` in this run:

- `rg timeout` listed the docstring, `timeout = 10`, `return timeout`, and `timeout: 5`. No pair, no exit 2. Default `rg` did not show `.env` (hidden / ignore).
- `rg --hidden --no-ignore -i timeout` added `.env: TIMEOUT=30` and `timeout=99` as hits. A human can now treat env-layer as a third “declaration.”
- this CLI `timeout` → DISAGREE `config.yaml:1 timeout: 5` vs `app.py:3 timeout = 10`, exit 2. `--json` declaration paths: `['config.yaml']` only.
- this CLI `TIMEOUT` → NONE, not DECLARED_ONLY 30.

On `fixtures/strlit`: `rg timeout` hit `msg = "timeout = 99 is wrong"` and `timeout: 5`. This CLI → DECLARED_ONLY 5. The string mention is not an assignment.

On `fixtures/compact_json`: `rg` listed both lines. This CLI extracted `5` from the one-line object and DISAGREEd it with `10`.

On `fixtures/unknown`: `${WAIT}` vs `os.getenv("WAIT")` was UNKNOWN exit 0, not a false match.

Substitution loses the pair, the exit-on-comparable-disagreement, the comment/code split, the refusal to compare interpolations, the refusal to treat dotenv as config, and the refusal to treat a string mention as an assignment. Compact JSON and quote-masking are honesty of that pair, not a new operation.

### Classification

USEFUL_COMPOSITION. The walk-and-regex is ordinary. The remainder is “pair, don’t list” plus “unknown is not disagree” plus “dotenv is not config.”

- **Novelty 3.** Still grep-plus-compare. Dotenv exclusion is a flipped assumption, not a new search engine.
- **Utility 4.** Config scalar vs hardcoded assignment is a daily debug. Exit 2 is usable in CI. Nested keys remain line tokens.
- **Primitive strength 3.** One key, two sides, comparable-or-not. Dotenv out keeps the sides honest. Nested `server.timeout` is not a path.
- **Composability 4.** `--json` emits the pair. Exit 2 on comparable disagreement, 0 otherwise, 1 on usage.
- **Empirical credibility 5.** Demo: disagree / agree / declared-only / unknown / comments / JSON / compact JSON / dotenv excluded / TIMEOUT NONE / strlit. 22/22 tests.
- **Evolution potential 3.** Nested key paths would help. Case-folding env names would start cloning effect. Richer parsers turn this into a product.
- **Reality-Stripped Strength 3.** Peel the name off and this is grep-plus-compare. The remainder that is not grep is the disagreement pair, the unknown refusal, and dotenv-not-decl. Enough to keep; not a new universe.

**KEEP**

---

## gen3-04 — one record: declared, assigned, env (including deferred names), effective-or-unknown

Shipped file: `effect`.

### 1. Operation that remains

Name a configuration key. Emit **one record** with four fields: DECLARED (config-file sites, dotenv excluded), ASSIGNED (source-file assignment sites), ENV_SOURCE (process/dotenv provenance of KEY, of its case variant, and of names those sites defer to: `${WAIT}`, `$WAIT`, `os.getenv("WAIT")`, `os.environ.get` / `os.environ[]`, `process.env.WAIT`, `env::var`), EFFECTIVE (a comparable scalar if the layers statically agree; otherwise `unknown` with a reason).

Exit 2 if a declared literal disagrees with an assigned literal. Env provenance is still printed. Compact `{"timeout": 5}` is a declaration, so EFFECTIVE cannot become a false assigned-only 10.

This is not `stated KEY && envfrom KEY`. Concatenation does not join `${WAIT}` / `os.getenv("WAIT")` to WAIT's file assignment.

### 2. Nearest ordinary workflow

`stated KEY; envfrom KEY` (or `envfrom KEY WAIT TIMEOUT` if the human already extracted the deferred names). Or `rg KEY` then `cat .env`.

### 3. What is lost if that workflow replaces this tool

The join. On `fixtures/deferred` (`timeout: ${WAIT}`, `timeout = os.getenv("WAIT")`, `.env` `export WAIT=10`, process `WAIT=from-shell`) in this run:

- `stated timeout` → UNKNOWN, interpolation vs call. Does not name WAIT.
- `envfrom timeout WAIT TIMEOUT` → `timeout` unset; `WAIT` file value 10; `TIMEOUT` unset. WAIT is in the report only because this judge already knew to ask for it.
- this CLI → DECLARED interpolation, ASSIGNED call, ENV_SOURCE WAIT `file:.env:1` value 10 `INHERITED: from-shell` `why=deferred`, EFFECTIVE `10`.

A wrapper that prints both CLIs still requires the human to notice WAIT in the sites and re-query env. The four-field record is the product.

On `fixtures/compact_json` this CLI reported DECLARED 5 vs ASSIGNED 10, EFFECTIVE unknown, exit 2. Missing that declaration would have been a false EFFECTIVE 10 with `disagree: false`. That is honesty of the joint record, same hole stated already closed, not a second remainder.

On `fixtures/empty-override`, declared 5 vs `os.getenv("TIMEOUT", "5")` vs file `TIMEOUT=` produced EFFECTIVE unknown (`literal 5 vs env (empty)`), exit 0 (exit 2 is only declared-literal vs assigned-literal). Concatenation would put TIMEOUT in envfrom if asked, and 5 in stated, and never say they conflict.

What is *not* claimed: runtime evaluation of `os.getenv("TIMEOUT", "5")` defaults. The call stays a call.

### Classification

USEFUL_COMPOSITION. The hybrid is the join, not a new primitive. Kill if `stated KEY; envfrom KEY` loses nothing. This run’s deferred fixture fails that kill test.

- **Novelty 3.** Both parent walks are ordinary. Pulling deferred env names into the same record as the key is the cut.
- **Utility 4.** “What would timeout actually be?” is the question people think `rg timeout && cat .env` answers. It does not.
- **Primitive strength 3.** Four fields share one exit. EFFECTIVE is a static agreement test, not an interpreter. Nested keys are still line tokens. The join is real; it is not one irreducible atom.
- **Composability 4.** `--json` is one object (`declared`, `assigned`, `env_source`, `deferred`, `effective`, `disagree`). Exit 2 only on declared-vs-assigned literals.
- **Empirical credibility 5.** Demo plus 18/18 tests: disagree with TIMEOUT in ENV_SOURCE, inherited TIMEOUT, agree, config-only, empty override, deferred WAIT, unknown unset, comments, `environ.get` / `process.env`, compact JSON, JSON joint object.
- **Evolution potential 3.** `os.getenv("X", "5")` static default is the next honest cut. Silent 2MiB skip still lies about EFFECTIVE. Do not grow a runtime evaluator.
- **Reality-Stripped Strength 4.** Peel the name off and the remainder is still not two CLIs concatenated: one record that follows names the sites defer to, and refuses to pick a winner when layers disagree.

**KEEP**

---

## mutation-02 — remaining-tree obligations a change fails to keep (companions are closed phrases)

Shipped file: `owes`.

### 1. Operation that remains

Take a unified diff (or before/after snapshots) plus the remaining tree. Report (a) identifiers that appear on minus lines as definitions and still appear in remaining files, skipping mentions whose stripped line text was introduced on a plus line of the same change; (b) paths that remaining `*.md` files name with `MUST exist: PATH` or `required file: PATH` when those paths are absent.

Incidental backtick paths in prose (`must see \`README.md\``, `must read \`docs/adr.md\``) are not companions. Shell commands such as `must run \`make test\`` are not files. Exit 2 if anything is unkept, 0 if not.

### 2. Nearest ordinary workflow

`git diff`, then `rg` the deleted names through docs and tests, then read CONTRIBUTING for required files and `test -e` them.

### 3. What is lost if that workflow replaces this tool

The binding. Diff stops at hunks. `rg validate_input` does not know the name was removed *by this change*, and it will also hit the changelog line the change itself just wrote.

In this run:

- deleted-fn: `rg validate_input` found `README.md:3`. This CLI bound it as an unkept reference, exit 2.
- plus-line-changelog: leftover README mention still fires; `CHANGELOG.md` “Removed validate_input from the public API.” does not.
- missing-companion: `MUST exist:` / `required file:` fired; incidental backticks did not.
- prose-backticks: `rg -i 'must|README'` listed `README.md` five times in a tree that has no `README.md`. This CLI printed `no unkept obligations`, exit 0. Parent `candidate-03` on the same fixture: `missing companions: README.md` from `must see \`README.md\``, exit 2.

Hand `diff`+`rg` does not do the plus-line skip or the closed-phrase companion harvest unless someone writes it every time. The mutation’s remainder versus its parent is the landmine removal, not a new obligation theory. Versus ordinary tools, the bound report is still the remainder.

Honesty limit, still part of the remainder: missing companions are scanned from remaining docs and do not consult the diff. They are “true of the remaining tree,” not “caused by this hunk.” Unkept identifier references *are* change-tied.

### Classification

USEFUL_COMPOSITION. Ordinary mutation of a composition. Companion harvest is now a closed phrase set. That is narrower, not stronger.

- **Novelty 3.** Stale-reference search exists in IDEs. Scoping it to identifiers the *change* removed, plus explicit-phrase missing companions, is not a stock command. Not a new theory of obligations.
- **Utility 3.** Leftover README calls after a delete are real review misses. `MUST exist:` / `required file:` is a dialect few repos speak. False positives remain (moved functions, comment leftovers).
- **Primitive strength 3.** Two scans share an “unkept” exit. Identifier extraction is regex over `def`/`function`/`CONST =`. The closed companion phrases keep the file-miss half from firing on ordinary markdown; they also make that half thinner.
- **Composability 4.** DIR snapshot, or `--tree` + `--diff`. `--json` with `unkept_references` / `missing_companions`. Exit 2 is scriptable.
- **Empirical credibility 5.** Four demo fixtures behaved as asserted. 14/14 tests, including prose-backticks empty, plus-line changelog skip, `---def` minus lines, absolute host path not a companion, JSON shape.
- **Evolution potential 3.** Skip identifiers that still have a definition; bind companions to files the diff touched. Searching every `*.py` for MUST-like phrases would re-open the landmine.
- **Reality-Stripped Strength 3.** Peel the name off and this is diff-removed names still in the tree, plus docs that say `MUST exist:` / `required file:` for absent paths. Ordinary tools can approximate it; they do not emit the bound report or the changelog exception by default. The backtick-after-must refuse is why the approximation no longer explodes on prose.

**KEEP**

---

## mutation-04 — named {env map, file hashes} capture, dual diff, env replay (JSON is encoding)

Shipped file: `capdiff`.

### 1. Operation that remains

Under a name, store a directory’s parsed `.env` (missing `.env` = empty map, not an error) and a sha256 manifest of relative files. Diff two names as ENV modified/extra/missing and FILES modified/extra/missing. Replay overlays captured env vars onto the current environment and execs a command in a directory. `--files` writes only the captured `.env`; other file bodies were never stored. The compared object is the labeled capture, not an ad-hoc pair of live trees.

`--json` emits `{a, b, env, files}` with the same six buckets as object arrays. Empty buckets are `[]`, not the text token `(none)`. Extra/missing env is `{key, value}` (embedded `=` round-trips). Extra/missing files is `{path, hash}`. Default text mode and exit codes (0 identical, 2 delta, 1 error) are unchanged.

### 2. Nearest ordinary workflow

`diff -ru` of two checkouts; `find | sort | xargs sha256sum`; `export $(grep -v '^#' .env)` / `env KEY=val cmd`; `direnv` for loading, not for named historical snapshots. `jq` on a homegrown dump if a script wants objects.

### 3. What is lost if that workflow replaces this tool

Two things, both observed in this run. First, the dual report. `diff -ru` on the live fixture trees mixed `# local CI` / `API_KEY=local-ci-key` into one hunk and reported `Only in … extra.txt`. This CLI split `API_KEY` local vs remote as ENV modified, `.env` as FILES modified (comment bytes changed the hash), and `extra.txt` as FILES extra. `diff -ru` does not name the key.

Second, the capture outlives the original directory as a fingerprint-plus-env-map: replay printed `local-ci-key` / `remote-ci-key` from the capture. `direnv` loads a live `.envrc`; it does not keep a named pair you can diff later.

What is *not* lost, and must not be claimed: restoring hashed file bodies (capture never stored them); a new object type from `--json`. JSON is the same six buckets as a document. A script that already parsed the text sections does not gain an operation. Extra now carrying a hash is data the text mode still omits — that is a small encoding delta, not a reason to keep a clone.

### Classification

USEFUL_COMPOSITION, closest to shell glue. The mutation itself is THIN_WRAPPER around the parent’s record (encoding). The parent object still has a remainder versus `diff -ru` + `env`.

- **Novelty 2.** Dump, hash, diff, and `env` prefix are ordinary. Naming the dump and splitting parsed ENV from hashed FILES is a small composition. JSON is syntax.
- **Utility 3.** Local-vs-remote CI “what env and what files” is a real debug. Replay of env into a tree that does not hold the secrets is useful. File-body restore is honestly absent.
- **Primitive strength 3.** The object `{name → (env map, path→sha256)}` with diff and env-exec is a real object. Weakened by overlay-not-unset and by the 5000-file cap. JSON does not strengthen it.
- **Composability 4.** Three verbs: capture, diff, replay. Exit 2 on any delta. `--json` is scriptable without parsing `  extra.txt`. Replay is an exec.
- **Empirical credibility 5.** Demo and 21/21 tests: text dual split, JSON objects not text lines, embedded `=` extra, identical empty arrays, missing capture exit 1, missing `.env` empty, replay without host `API_KEY`, `--files` writes dotenv, `.` / `..` names rejected, truncated captures not identical.
- **Evolution potential 2.** `--env-only` / `--files-only`, glob filters, capture a listed subset of process env, explicit unset-missing-keys. Storing file bodies would destroy the primitive by turning it into tar. Further JSON flags are not evolution of the object.
- **Reality-Stripped Strength 3.** Peel the name off and this is still more than `diff -ru`: a labeled fingerprint with parsed env vs hashed files, plus env replay. Peel `--json` off and nothing operational remains that the text mode did not already say, except extra-file hashes in the machine record. Keep as a composition, not as a flagship, and do not count the encoder twice.

**KEEP** (the capture object). Do not treat `--json` as a second survivor.

---

## Verdict

| Artifact | Remainder (name ignored) | Class | RSS | Decision |
| --- | --- | --- | --- | --- |
| gen3-01 | Tagged two-parent resolve + per-span parent ledger; empty hybrid is not a merge | USEFUL_COMPOSITION | 4 | KEEP |
| gen3-02 | Per-variable env source, including empty file override; missing DIR is not inherit | USEFUL_COMPOSITION | 4 | KEEP |
| gen3-03 | Declaration/assignment disagreement pair; dotenv is not a declaration | USEFUL_COMPOSITION | 3 | KEEP |
| gen3-04 | Four-field record: declared, assigned, env including deferred names, effective-or-unknown | USEFUL_COMPOSITION | 4 | KEEP |
| mutation-02 | Change-removed names still claimed by the remaining tree; `MUST exist:` / `required file:` only | USEFUL_COMPOSITION | 3 | KEEP |
| mutation-04 | Named {env map, file hashes} with dual diff and env replay. JSON is encoding. | USEFUL_COMPOSITION | 3 | KEEP |

KEEP all six as objects. KILL none: each still loses an observable if replaced by its nearest ordinary workflow. That is not an install list.

What the Gen-3 / mutation cuts added, after branding is removed:

| Cut | Remainder, or hygiene? |
| --- | --- |
| empty hybrid refuse (file and stdin) | Honesty of gen3-01’s remainder. Prevents a silent wipe. Not a new operation. |
| `--dir` missing is exit 1 | Honesty of gen3-02’s remainder. Prevents a fake inherit. Not a new operation. |
| dotenv not a declaration; quote-mask assignments | Honesty of gen3-03’s pair. Prevents env-layer and string mentions from posing as config/source. |
| compact JSON is a declaration | Honesty of gen3-03’s pair and gen3-04’s EFFECTIVE. Prevents a false assigned-only 10. |
| deferred-name env join in one record | **Remainder.** `stated KEY; envfrom KEY` loses WAIT unless the human already knew to ask. |
| companion phrases closed (`MUST exist:` / `required file:`) | Narrowing. Removes a landmine. Does not add an obligation kind. |
| `capdiff diff --json` | Encoding. Same six buckets. Do not breed from the encoder. |

The three strongest remainders after branding is removed are gen3-01 (resolution as provenance), gen3-02 (empty override as a sourced event), and gen3-04 (deferred join into EFFECTIVE). gen3-03 is a useful pair whose nearest workflow is obvious; dotenv-not-decl is why the pair stayed honest. mutation-02 is a bound report whose companion half is now thin enough to trust. mutation-04 is still the set’s closest shell glue; `--json` does not rescue it from that.

Do not average these scores with other judges. Disagreement is expected on gen3-04 (join vs mashup), mutation-04 (composition vs glue), and gen3-03 vs gen3-04 (pair-only vs joint record). This role keeps both stated and effect as objects: stated’s `TIMEOUT` → NONE is a different answer from effect’s case-variant ENV_SOURCE. Tomorrow does not install both.

---

## Tomorrow Test

Which binaries should a human actually install and try tomorrow? A primitive can be worth remembering without a PATH entry. Empty slots are allowed. This list is not the KEEP table.

**Install (PATH):**

1. **whence** — after a messy two-parent merge I will type this instead of `git merge-file`. Substitution loses the parent ledger and the refuse-unmarked / refuse-empty contracts. Observed in this run.
2. **envfrom** — when `LIBRARY_PATH` is empty in a child I will type this instead of `printenv` + `grep .env`. Substitution loses empty-override + inherited-alongside-empty + would-apply vs `--load`. Observed in this run.

**Try once, do not PATH yet:**

3. **effect** — on one real service tree, `effect timeout .`. If deferred names never appear, the join was a lab fixture and this slot empties. If they do, this is the record `stated; envfrom` cannot emit.

**Not tomorrow (remember, no PATH):**

- **stated** — the pair is real; I will still `rg` unless I already have effect. Do not install two walkers for one key.
- **owes** — useful on a review that just deleted a public name. `git diff` + `rg` is what I will type at 10:00. Closed companion phrases are too dialect-specific for a daily binary.
- **capdiff** — labeled capture is real; I will still `diff -ru` and copy a `.env`. JSON does not change that.

**Empty slots: 4, 5, 6.**

Do not fill them to reward abundance. Do not average this list with a judge that PATH-installs all six KEEP objects.
