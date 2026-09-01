# Final jury — Unix

Judge: Unix. Independent. Origins ignored as quality. Other judges unread.

Values: tiny orthogonal primitives, composition, pipes, exit codes, text.
Not polish. Not LOC. Not README length. Strange strong primitives KEEP even if ugly. Polished clones KILL.

Tomorrow test: which binaries would this judge actually put on PATH. Empty slots allowed. KEEP of an object is not an install.

Method: README.md + CANDIDATE.md for each lineage. `./demo.sh` and `python3 -m unittest discover -s tests -q` run from that directory on 2026-09-02. Extra probes (stdin, mixed stdout, missing DIR, capture names) by this judge. Empirical scores use those runs only.

---

## gen3-01__whence-empty

**What remains:** Parse `<<<<<<<` / `=======` / `>>>>>>>`, resolve only by an explicit parent (`--ours` / `--theirs` / `--choice` / tagged `[ours:…]` `[theirs:…]` hybrid), emit JSON naming the parent of every kept contested span. Untagged mixed text is refused. Two parents only; `|||||||` is refused. Empty hybrid — stdin, whitespace-only pipe, or 0-byte sidecar file — is usage, not a successful `mode: empty`. `FILE -` requires `--output PATH` (not `-`); dual stdin is refused.

### Empirical evidence (this judge)

`./demo.sh` → **exit 0**. Observed: ours-only provenance `spans: [{"parent":"ours","text":"color = red\nsize = 1\n"}]`; file sidecar and `--hybrid -` produced identical resolved bytes (`cmp`); generated pipe tags matched; UTF-8 BOM on stdin matched the sidecar; empty stdin `--hybrid -` **exit 3**, markers stayed; empty file sidecar **exit 3**, markers stayed (`An empty sidecar is not a hybrid and must not wipe the hunk`); `FILE -` without `--output` **exit 3**, no file named `-`; dual stdin **exit 3**; untagged mix **exit 1**, markers left; diff3 **exit 2**; real two-branch `git merge` conflict resolved `--ours` with `mode: ours`; messy three-region hybrid preserves no trailing newline (`xxd` tail `23 2065 6f66` = `# eof`). Demo ran 31 unittests internally, OK.

`python3 -m unittest discover -s tests -q` → **exit 0**, `Ran 31 tests in 1.437s OK`.

This judge also: `whence resolve - --ours --prov - </dev/null` → **exit 3** (`FILE is '-' (stdin); pass --output PATH`). `whence report -` on empty stdin prints `conflicts: 0` and **exit 0** (report is not resolve).

Shipped CLI is `./whence` (862 lines). zsh already has a builtin `whence`; the demo correctly invokes `python3 ./whence`.

### Scores

**Novelty — 4.** Git already takes ours/theirs. What does not exist is a merge *product* that still says, for each contested span, which parent supplied it, plus a contract that unmarked mix is illegal and that an empty sidecar is not a tagged merge. The empty-hybrid refuse is not a new verb; it is the same verb, sealed.

**Utility — 4.** Overlapping edits are daily. `git mergetool` throws the parentage away the moment the blob is clean. A `.prov` sidecar (or stdout JSON) next to the resolved file is something a later review or `git notes` step could actually consume. Name collision with zsh is a real adoption tax, not a reason the operation is fake.

**Primitive strength — 4.** One sharp rule: no invented merge. Whole-side choice, per-region `--choice`, or tagged spans that must be ordered substrings of a named parent. Empty hybrid is not a parent. That is a primitive, not a mergetool. The `[ours:…]` sidecar with `%%` and `\]` escaping is more language than Unix wants; the refuse-unmarked-mix / refuse-empty-hybrid core would still stand without it.

**Composability — 4.** Provenance JSON on stdout is pipeable; `--hybrid -` and file `-` speak stdin; `--prov -` skips the sidecar; `--output` is required when FILE is stdin so the tool cannot mint a file named `-`. Default behavior still overwrites `FILE` and writes `FILE.prov` — mergetool-shaped, not a filter. No driver wiring, so it does not yet sit in `git merge`. Exit table is honest: 0 ok, 1 refuse, 2 parse, 3 usage.

**Empirical credibility — 5.** This judge watched a real `git merge` produce two-parent markers, empty stdin and empty sidecar leave markers in place, `FILE -` refuse a dash-file, untagged mix leave the conflict, and a no-trailing-newline messy resolve match `xxd`. Tests call the shipped file, not a reimplementation.

**Evolution potential — 3.** The next honest cuts are a mergetool/`merge` driver and provenance as a git note instead of a sidecar. BOM/CRLF/empty-sidecar sealing was the right refuse; more hybrid-language surface is not. SequenceMatcher auto-tags would soften the refuse-mix contract and should be a separate tool.

**Reality-Stripped Strength — 4.** Ignore the name. Operation: resolve conflict markers by named parent and emit which parent won each span; refuse an empty or untagged mash-up as a resolution. Nearest ordinary workflow: edit the markers, or `git checkout --ours/--theirs`, or `git merge-file --ours`. What that workflow loses: per-span parentage and the refusal to accept an untagged or empty sidecar as a merge. That loss is the tool.

### Verdict: KEEP

Ugly (zsh name, hybrid DSL, in-place write). The primitive is not a clone of `merge-file`. Empty hybrid is now an error, as it should be.

---

## gen3-02__envfrom-dir

**What remains:** Name a variable. Report whether its effective value is inherited process env, a dotenv `file:path:line` assignment, or unset. A file line `KEY=` is an empty override even when the process already has `KEY`. `--fail-empty` exits 2. `--dir DIR` reads dotenv from DIR; missing or non-directory DIR is exit 1, not a silent `SOURCE: env`. `--run` prints provenance then execs; `--load` actually applies file assignments onto the child.

### Empirical evidence (this judge)

`./demo.sh` → **exit 0**. Observed with `LIBRARY_PATH=/usr/local/lib:/usr/lib` and fixture `.env` line 2 `LIBRARY_PATH=`: `VALUE=` `SOURCE: file:…/empty-override/.env:2` `EMPTY_OVERRIDE: yes` `INHERITED: /usr/local/lib:/usr/lib`. `--fail-empty LIBRARY_PATH` **exit 2**. `--run` without `--load`: child keeps inherited `LIBRARY_PATH=/usr/local/lib:/usr/lib`. `--run --load`: `child LIBRARY_PATH=''`. Quoted-export: `export PREFIX=app`, unquoted inline comment stripped (`COLOR=red`), `EMPTY_QUOTED=""` is empty override, quoted `# not a comment` stays a value. `--dir` on a sibling tree reports that tree's `FOO=from-there`, not cwd. `--dir /no/such/envfrom-dir PATH` → `envfrom: directory not found` **exit 1** (not `SOURCE: env`). UTF-8 BOM keeps `FOO=bom`; invalid UTF-8 **exit 1** with `cannot read … invalid start byte` and no traceback.

`python3 -m unittest discover -s tests -q` → **exit 0**, `Ran 31 tests in 1.315s OK`.

This judge also: `--dir /dev/null PATH` → `not a directory` **exit 1**. No keys → **exit 1**. `--json --run -- python3 -c 'print("CHILD")'` concatenates the JSON array and `CHILD` on the same stdout. `--fail-empty PREFIX` (nonempty) **exit 0**; `--json --fail-empty LIBRARY_PATH` **exit 2**.

Shipped CLI is `./envfrom` (314 lines).

### Scores

**Novelty — 4.** `printenv` shows values. It does not show that `.env:2` would wipe `LIBRARY_PATH`. `direnv status` shows loading activity, not per-key provenance. Empty-override-vs-inherited is a real missing env object. `--dir` is not novelty; it is the tree argument every Unix scanner already owes.

**Utility — 4.** Empty `LIBRARY_PATH=` / `PYTHONPATH=` in a dotenv file is a classic “child is empty and nobody knows why.” `--fail-empty` is a gate you could put in front of a test runner. `--dir` makes the lookup honest when cwd is not the tree. `--run --load` duplicates dotenv loaders; the useful split is that observation does not mutate unless `--load` is named.

**Primitive strength — 4.** One lookup: source of KEY. Three sources (`env` / `file:path:line` / `unset`) plus the empty-override bit. `--run`/`--load` are a second tool (wrapper/exec) riding along; they do not ruin the lookup, and requiring `--load` to actually apply file values is the right refusal of magic. Missing DIR as exit 1 is the same primitive, not a new one.

**Composability — 3.** `--fail-empty` is a predicate. `--json` is one record per key. Block format (`KEY` / `VALUE=` / `SOURCE:`) is parseable and worse than one record per line for `awk`. `--run` is a wrapper, not a pipe; `--json --run` observed mixing provenance JSON and child stdout on fd 1, so `jq` cannot consume it. Default “must name KEY” is Unix-good. `--dir` is the right composition with `cd`.

**Empirical credibility — 5.** This run showed inherited vs empty file override, fail-empty exit 2, run-without-load keeping the child inherited, run-with-load emptying it, missing DIR exit 1, BOM vs binary, and `--json --run` concatenating on stdout. 31 tests OK.

**Evolution potential — 3.** Source *chain* when `.env` and `.env.local` both set the key; newline-safe VALUE; provenance on stderr (or fd 3) when `--run` is used. Stay a provenance tool. Drop `--run` into a sibling. Interpolation/`KEY+=` would become a shell.

**Reality-Stripped Strength — 4.** Ignore the name. Operation: look up KEY in process env and dotenv files in a named directory; report who won; flag empty file assignment; optionally refuse it. Nearest workflow: `printenv KEY`, `grep KEY .env`, `direnv status`. What that workflow loses: the pair (file emptied this / inherited used to be that) and a file:line source. That pair is the tool.

### Verdict: KEEP

The empty-override provenance is a primitive `env` does not have. `--dir` is now honest. Keep the lookup; do not let `--run` eat the lineage.

---

## gen3-03__stated-honest

**What remains:** Walk a tree, regex-find `KEY:` / `KEY=` in config-like files and assignments in source, compare trailing literal scalars, print a disagreement pair or a status document. Dotenv is not a declaration. Quoted `timeout = 99` inside a string is not an assignment. Compact `{"timeout": 5}` is a declaration. Exit 2 only on comparable disagreement; everything else is exit 0.

### Empirical evidence (this judge)

`./demo.sh` → **exit 0**. Observed: disagree fixture `status: DISAGREE` declared `5` vs contradicted `10`, tool **exit 2**; agree both `5` **exit 0**; config-only `DECLARED_ONLY` **exit 0**; interpolation vs `os.getenv` `status: UNKNOWN` **exit 0**; comments fixture `status: AGREE` with docstring/`/* */`/`#` hits listed as comments; `--json` disagreement pair has `declared_value: "5"`, `contradicted_value: "10"`; compact JSON `{"timeout": 5}` vs `timeout = 10` **exit 2**; `stated timeout` on dotenv fixture still DISAGREEs yaml 5 vs py 10 (no `.env` sites); `stated TIMEOUT` on the same tree is `NONE` **exit 0**, not DECLARED_ONLY 30; string-literal `timeout = 99` is DECLARED_ONLY 5.

`python3 -m unittest discover -s tests -q` → **exit 0**, `Ran 22 tests in 0.673s OK`.

This judge also: missing DIR **exit 1**; no args **exit 1**. No stdin.

Shipped CLI is `./stated` (727 lines).

### Scores

**Novelty — 2.** This is `rg KEY` across two filename classes, then compare the token after `:`/`=`. Pairing declaration vs assignment is a report shape, not a new operation. Excluding dotenv and masking string literals is honesty about grep, not a new operation. People already do this by eye when a timeout “only broke after I changed yaml.”

**Utility — 3.** The disagree fixture is a real debug question. Comment/docstring false positives and the string-literal false assignment were real bugs and got fixed. Nested keys, interpolations, and typed Python (`timeout: int = 5`) are still outside the scanner, so it will lie or go UNKNOWN on the trees where you actually need it. Dotenv-out is the right cut if you keep the tool; it does not make the tool worth keeping.

**Primitive strength — 2.** Too many statuses (`disagree` / `agree` / `declared_only` / `assigned_only` / `unknown` / `none`) for one binary question. Exit 0 is overloaded: agree, one-sided, unknown, and nothing-found are the same code. A Unix primitive would make “comparable disagreement” vs “not a comparable pair” vs “no sites” distinct exits. Comment-state machine + quote mask + per-language file lists is a mini-linter, not one orthogonal cut.

**Composability — 2.** Document on stdout, not records. `--json` is the only composition path. Cannot take `rg` hits on stdin and just do the compare. You cannot write `stated timeout && deploy` unless you are willing to treat UNKNOWN and NONE as success.

**Empirical credibility — 5.** Demo and 22 tests passed here, including compact JSON, dotenv-not-declaration, and string-literal dogfood. The CLI is real.

**Evolution potential — 2.** Nested `server.timeout`, case-insensitive env, richer parsers, markdown: this grows a linter. The primitive does not sharpen; the product fattens. Distinct exits would be the only Unix mutation left, and even then the scanner is still grep.

**Reality-Stripped Strength — 2.** Ignore the name. Operation: grep a key in config and source, compare trailing literals, skip dotenv and quoted mentions. Nearest workflow: `rg timeout` and read the hits. What you lose: automatic scalar compare, comment/string filtering, exit 2 on a numeric mismatch. That is a convenience wrapper around grep, not a missing Unix verb.

### Verdict: KILL

Useful composition, not a primitive. Overloaded exit 0 is a Unix defect. Honesty about dotenv does not change the shape.

---

## gen3-04__effect-compact

**What remains:** Name a configuration key. Emit one document with DECLARED (config, not dotenv), ASSIGNED (source), ENV_SOURCE (process/dotenv of KEY, case variants, and names those sites defer to), and EFFECTIVE (a comparable scalar or `unknown`). Exit 2 only if a declared literal disagrees with an assigned literal. Compact `{"timeout": 5}` is a declaration.

### Empirical evidence (this judge)

`./demo.sh` → **exit 0**. Observed: disagree yaml 5 vs py 10, ENV_SOURCE still has `.env TIMEOUT=30`, EFFECTIVE `unknown declared 5 vs assigned 10`, **exit 2**; inherited `TIMEOUT=from-shell` still lost to file `30`; agree both 5, EFFECTIVE `5`, **exit 0**; config-only EFFECTIVE `5` **exit 0**; empty-override fixture: declared 5, assigned `os.getenv("TIMEOUT", "5")`, file `TIMEOUT=` empty override of inherited `/already/set`, EFFECTIVE `unknown literal 5 vs env (empty)`, **exit 0**; deferred WAIT: config `${WAIT}` + `os.getenv("WAIT")` + file `WAIT=10`, EFFECTIVE `10`, **exit 0**; unknown interpolation vs getenv, WAIT unset, EFFECTIVE `unknown sites defer to unset env`, **exit 0**; `os.environ.get` / `process.env.WAIT` with file WAIT=10 vs declared 5, EFFECTIVE `unknown literal 5 vs env 10`, **exit 0**; compact JSON `{"timeout": 5}` vs `timeout = 10` **exit 2**.

`python3 -m unittest discover -s tests -q` → **exit 0**, `Ran 18 tests in 0.609s OK`.

This judge also: missing DIR **exit 1**.

Shipped CLI is `./effect` (945 lines). Fattest object in this set.

### Scores

**Novelty — 3.** The deferred-name join (`timeout` sites that name `WAIT`, then look up WAIT in dotenv) is a real question neither `stated` nor `envfrom KEY` answers. Compact JSON is a scanner patch, not novelty. Four-field dashboards are the ordinary shape of “I glued two reports.”

**Utility — 3.** “What would this key actually be, given yaml / assignment / .env / getenv?” is a daily debug question. The document answers it on the fixtures. Exit 0 when declared 5 vs empty env override means `effect timeout && deploy` is a lie on the most interesting case. EFFECTIVE picking `10` from WAIT while DECLARED is interpolation is a policy, not an observation.

**Primitive strength — 1.** Not one cut. Two scanners plus an env lookup plus an EFFECTIVE policy engine. Exit 2 is only declared-vs-assigned; env mismatches are `unknown` with success. That is a product. Unix would keep `envfrom WAIT` and a grep, or a 40-line join that prints records, not a 945-line report.

**Composability — 1.** One document. No stdin. `--json` is the only machine path. You cannot pipe DECLARED into ENV_SOURCE; they are glued. `--json --run` is not even here, and that is the only mercy. `effect KEY && …` treats env-layer disagreement as success.

**Empirical credibility — 5.** Demo and 18 tests passed here, including compact JSON now visible, deferred WAIT join, and empty-override EFFECTIVE unknown with exit 0. The CLI is real. The exit table is also real, and it is the defect.

**Evolution potential — 2.** Suggested mutations (announce skipped files, dotenv decode policy, `os.getenv` defaults) grow the dashboard. Splitting back into lookup + compare would be the Unix cut, and that is a retreat to the parents.

**Reality-Stripped Strength — 2.** Ignore the name. Operation: grep KEY in config and source, also grep getenv/interpolation names, look those up in `.env`, print a four-section report, guess an effective scalar. Nearest workflow: `rg timeout`, `rg getenv`, `envfrom WAIT`. What you lose: the join and the EFFECTIVE guess. The join is a script. The guess is where it lies.

### Verdict: KILL

A dashboard. The deferred join is the only missing field, and it does not justify one fat binary with a success exit on env mismatch.

---

## mutation-02__owes-strict

**What remains:** Given a unified diff and a remaining tree, list (1) identifiers removed on minus lines that remaining files still mention, and (2) paths that remaining `*.md` name via `MUST exist:` / `required file:` that are absent. Incidental backtick paths after “must” are not companions. Exit 2 if either list is nonempty.

### Empirical evidence (this judge)

`./demo.sh` → **exit 0**. Observed: deleted `validate_input` still in README → `unkept references:` + **exit 2**; missing companions `SECURITY.decision.md`, `docs/threat-model.md` → **exit 2** (no `docs/adr.md` from `must read \`docs/adr.md\``); clean fixture `no unkept obligations` **exit 0**; prose-backticks fixture (incidental `README.md` / `CONTRIBUTING.md` / `LICENSE.md`) `no unkept obligations` **exit 0**.

`python3 -m unittest discover -s tests -q` → **exit 0**, `Ran 14 tests in 0.522s OK`.

This judge also: `--diff -` → `owes: diff not found: -` **exit 1** (stdin is not a path named `-`). `--diff /dev/stdin` with a redirected `change.diff` **exit 2** and lists `validate_input` — composition only by accident of a device node. `--json` on deleted-fn is a document with `unkept_references` / `missing_companions`.

Shipped CLI is `./owes` (488 lines). Inputs are a custom `DIR/{change.diff,tree}` or `DIR/{before,after}` layout, or `--tree` + `--diff FILE`. Diff is not read from `-`.

### Scores

**Novelty — 2.** `git diff` plus `rg` for the deleted name is the ordinary workflow. “Required file” matching is a second, fixture-shaped checker (`MUST exist:`, `required file:`). Closing the backtick-after-must landmine is a leak fix, not a new operation. Gluing two jobs under one noun still does not make a new operation.

**Utility — 3.** Leftover mentions after a delete are a real review miss. Strict companions make the file-miss half usable on real markdown; parent’s backtick harvest was not. Moved functions, comment-only leftovers, and short names will still false-positive. Companion scanning still looks only at `*.md` and does not consult the diff.

**Primitive strength — 2.** Two jobs. Identifier extraction is a pile of `def|class|function|fn|…` regexes, not a language-agnostic cut. The snapshot directory protocol (`before/`/`after/` or `change.diff`+`tree/`) is an application layout, not a primitive interface. Strict phrases sharpen job (2) only.

**Composability — 1.** Unix would be `git diff | owes TREE`. This CLI refuses `-` as stdin. `/dev/stdin` works because `Path.is_file()` is true, not because the tool is a filter. Human report / JSON document. Exit 2 is the only composable bit. Two glued checkers behind a snapshot protocol.

**Empirical credibility — 5.** Four demo fixtures behaved; 14 tests OK. `--diff -` exit 1 and `/dev/stdin` exit 2 were observed here. Prose-backticks is a real parent-vs-this contrast on the same markdown.

**Evolution potential — 2.** Skipping identifiers that still have a definition, and binding companions to files the diff actually touched, would sharpen job (1) and job (2) separately. They should not stay one binary. Stdin `-` would be the Unix mutation; it was not this mutation.

**Reality-Stripped Strength — 2.** Ignore the name. Operation: names on minus lines still occurring in the tree, plus two closed phrases for required paths in markdown. Nearest workflow: `git diff` and `rg`. What you lose: packaging two leaky checks and a custom directory layout. Strict phrases remove a false companion; they do not create a missing verb.

### Verdict: KILL

Should have been a stdin filter with one job. Strict companions are a bugfix. Two glued checkers behind a snapshot protocol is still not Unix.

---

## mutation-04__capdiff-json

**What remains:** Named capture of a directory’s parsed `.env` plus sha256 of relative files, stored under `.capdiff/NAME`. Diff two names as ENV vs FILES (exit 2 on any delta). `--json` emits `{a,b,env,files}` with modified/extra/missing as arrays of objects. Replay overlays captured env and execs a command; `--files` restores only the captured `.env`, not file bodies.

### Empirical evidence (this judge)

`./demo.sh` → **exit 0**. Observed: capture `a` (2 files, 1 env) and `b` (3 files, 1 env); `diff a b` **exit 2** with `ENV modified: API_KEY` `local-ci-key` vs `remote-ci-key` and `FILES extra: extra.txt`; replay a/b print `local-ci-key` / `remote-ci-key`; capture without `.env` is empty env map; `diff a none` **exit 2** with `ENV missing: API_KEY=local-ci-key` and FILES extra `readme.txt` / missing `.env` `app.txt`. `diff a b --json` one line, extra/missing are objects (`{"hash":…,"path":"extra.txt"}`, `{"a":"local-ci-key","b":"remote-ci-key","key":"API_KEY"}`), **exit 2**. `diff a none --json` missing env is `{"key":"API_KEY","value":"local-ci-key"}` not the text line `API_KEY=local-ci-key`. `diff a a --json` six empty arrays, **exit 0**.

`python3 -m unittest discover -s tests -q` → **exit 0**, `Ran 21 tests in 1.436s OK`.

This judge also: `capdiff capture - fixtures/env-a` accepted NAME `-` and wrote `.capdiff/-` (**exit 0**). `capdiff capture -- …` accepted NAME `--` and wrote `.capdiff/--`. Those names match `^[A-Za-z0-9._-]+$`. Capture still does not emit a document to stdout; it mutates cwd. (Probe captures removed after the run.)

Shipped CLI is `./capdiff` (492 lines). Three subcommands. Stateful store in cwd.

### Scores

**Novelty — 2.** `sha256sum` a tree, parse `.env`, `diff` two dumps, `env KEY=val cmd`. Binding those dumps to a name in `.capdiff/` is bookkeeping. `--json` is an encoding of the same six buckets. The ENV-vs-FILES split (parsed keys *and* `.env` bytes) is a small honest distinction, not a new verb.

**Utility — 3.** “Local CI key vs remote CI key, plus an extra file” is a real comparison. JSON extra/missing as objects (not `KEY=value` strings) is the right machine record; scripts can round-trip a value that contains `=`. Replay without restoring hashed bodies is honest and also means the name “capture” oversells: you cannot recreate the tree. Missing `.env` as empty map (not an error) matches how repos actually look.

**Primitive strength — 2.** Three verbs (`capture` / `diff` / `replay`) around a hidden store. Unix wants one object on stdout: a text capture you can save, `diff`, and `env` from. Replay is `env`+`exec`. File-hash compare is `cmp`/`sha256sum`. JSON does not make three verbs one. NAME `-` / `--` accepted into the store is the opposite of a sharp interface.

**Composability — 2.** `--json` is pipeable *output*. Inputs are still names in `.capdiff/`, not files or stdin. Capture does not emit a portable document; it mutates cwd. Replay exec is composition of a sort, then it stops being a filter. Exit 0/2/1 on diff is the only Unix-shaped bit.

**Empirical credibility — 5.** Demo and 21 tests passed here, including JSON extra/missing as objects, identical empty arrays exit 0, and env-only replay. NAME `-` and `--` accepted into the store were observed in this probe.

**Evolution potential — 2.** Include/exclude globs, `os.environ` subsets, `--env-only`, unset-missing-keys: this becomes direnv/docker-lite. The Unix cut would be “write the capture as text and stop.” JSON was the encoding of that document, still trapped in a named store.

**Reality-Stripped Strength — 2.** Ignore the name. Operation: hash files, parse `.env`, remember two labeled dumps, overlay env, exec, optionally print the delta as JSON. Nearest workflow: `diff -ru`, `sha256sum`, `env $(grep -v ^# .env) cmd`, maybe `direnv`. What you lose: a name so you remember which dump was local vs remote, plus a jq-able delta. That is memory and encoding, not a missing operation.

### Verdict: KILL

Stateful three-command store around tools that already exist. JSON is an encoding, not a primitive.

---

## KEEP list

Multiple survivors. Not a ranking. KEEP is “this object is a primitive worth keeping.” It is not PATH.

| Lineage | Verdict | Unix reason |
|---------|---------|-------------|
| **gen3-01__whence-empty** | **KEEP** | Missing merge object: explicit parent + per-span provenance; refuse unmarked mix *and* empty hybrid. |
| **gen3-02__envfrom-dir** | **KEEP** | Per-key env provenance; empty file override vs inherited is a real primitive; `--dir` is now honest. |
| gen3-03__stated-honest | KILL | Grep-plus-status document; exit 0 overloaded. Dotenv-out is hygiene. |
| gen3-04__effect-compact | KILL | Dashboard join; exit 0 on env mismatch; not a tiny orthogonal cut. |
| mutation-02__owes-strict | KILL | Two checkers; no `-` stdin; snapshot directory protocol. Strict phrases are a bugfix. |
| mutation-04__capdiff-json | KILL | Three-command hidden store around `diff`/`sha256`/`env`. JSON is encoding. |

**KEEP:** `whence`, `envfrom`.

---

## Tomorrow — binaries this judge would actually install

Empty slots allowed. Deliberately small.

| Binary | Install? |
|--------|----------|
| `envfrom` | **yes** — `envfrom LIBRARY_PATH` and `envfrom --fail-empty KEY` are questions this judge already hits. Put it on PATH. Do not advertise `--run` as a dotenv loader. |
| `whence` | **no** — KEEP the object; do not install the *name*. zsh already owns `whence`. Default in-place write is mergetool-shaped. Would keep the file in a repo as `python3 ./whence`, not drop it on PATH tomorrow morning. |
| `stated` | **no** |
| `effect` | **no** |
| `owes` | **no** |
| `capdiff` | **no** |

**PATH tomorrow:** `envfrom` only.

Four empty slots. That is the point.
