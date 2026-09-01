# Final jury — Skeptic

Role: assume the tool should not exist until execution evidence shows otherwise.
Date: 2026-09-02.

Did **not** read `EVOLUTION_REPORT.md`, `lab/`, previous-brrr reports, other final-jury files, or `.hdd/` Dreamer transcripts. Origin method/trial in `CANDIDATE.md` is ignored until after the CLI ran. The CLI either did something on input I ran, or it did not.

I ran `./demo.sh` and the shipped unittest command in each of:

- `lab-hdd/lineages/gen3-01__whence-empty`
- `lab-hdd/lineages/gen3-02__envfrom-dir`
- `lab-hdd/lineages/gen3-03__stated-honest`
- `lab-hdd/lineages/gen3-04__effect-compact`
- `lab-hdd/lineages/mutation-02__owes-strict`
- `lab-hdd/lineages/mutation-04__capdiff-json`

All six demos exited 0. All six test suites exited 0 (whence 31, envfrom 31, stated 22, effect 18, owes 14, capdiff 21). I then pointed each binary at non-fixture input (live git merge, this repo’s `.env.hdd` keys / `HOME`, `lab-hdd/scripts` / `lab-hdd/judges` / `lab-hdd` itself, a deleted real `can_spend`, parent binaries for FIX contrast). Fixture-only success is not a 5 on empirical credibility. A FIX that I did not re-run is not a FIX.

KEEP bar: I saw an object I cannot get from one ordinary command without writing a script. A JSON flag around an existing dump is not a new object. Closing a hole in a KEEP’d object does not mint a second binary.

| Candidate | Decision | N | U | P | C | E | Ev | RS | Sum |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| gen3-01 whence-empty | **KEEP** | 4 | 3 | 4 | 4 | 5 | 3 | 4 | 27 |
| gen3-02 envfrom-dir | **KEEP** | 3 | 4 | 4 | 4 | 5 | 3 | 4 | 27 |
| gen3-03 stated-honest | **KEEP** | 3 | 2 | 3 | 3 | 3 | 3 | 3 | 20 |
| gen3-04 effect-compact | **KEEP** | 4 | 3 | 4 | 3 | 4 | 3 | 4 | 25 |
| mutation-02 owes-strict | **KEEP** | 3 | 2 | 3 | 3 | 4 | 3 | 3 | 21 |
| mutation-04 capdiff-json | **KEEP** | 2 | 3 | 3 | 3 | 4 | 2 | 2 | 19 |

N Novelty · U Utility · P Primitive strength · C Composability · E Empirical credibility · Ev Evolution potential · RS Reality-Stripped Strength. 0–5. Not averaged with other judges. Sum is not a ranking.

Tomorrow I would actually type **envfrom** and **whence**. Four empty PATH slots. The other KEEPs stay in the breeding pool; they are not install candidates. I am not minting six binaries.

---

## gen3-01 whence-empty — KEEP

### Execution

`./demo.sh` exit 0. `python3 -m unittest discover -s tests -v`: 31 tests, OK (demo already runs this suite; I ran it again).

Demo showed, on this machine:

- `report` of `fixtures/simple.conflict` (HEAD vs feature).
- `--ours` / `--theirs` overwrite plus JSON provenance and a `.prov` sidecar.
- `--hybrid fixtures/hybrid-tagged.txt` kept `color = red` from ours and `2` from theirs; `"hybrid": {"source": "file", ...}`.
- the same tags on stdin (`--hybrid -`) produced identical resolved bytes; `"hybrid": {"source": "stdin"}`.
- generated pipe `python3 -c 'print("[ours:color = red]"); print("size = [theirs:2]")'` matched the file sidecar.
- UTF-8 BOM on stdin matched the file sidecar.
- empty stdin `--hybrid -` exit 3, markers stayed.
- empty file sidecar exit 3, markers stayed.
- `FILE -` without `--output` exit 3, no file named `-`; with `--output` wrote the blob.
- FILE and `--hybrid` both `-` exit 3.
- untagged mix refused, exit 1, markers left.
- diff3 `|||||||` refused, exit 2.
- `git merge-file -p --ours` printed a blob and stopped.
- a throwaway two-branch git repo with `merge.conflictStyle=merge` produced real `<<<<<<< HEAD` markers; `--ours` kept `value = 1\n`.
- messy three-region hybrid: short sidecar named `region 3/3 … MISSING tagged block`; wrong-parent quoted name pointed at theirs; successful hybrid left `# eof` with no trailing newline.

### Extra probe (not the demo)

Live git merge of `color = red` / `size = 9` vs `color = blue` / `size = 2`, then tagged hybrid on stdin. Exit 0. Resolved file:

```text
shared
color = red
size = 2
end
```

Provenance spans: ours `"color = red"`, theirs `"2"`. That is the primitive on a real conflict, not `--ours` on a fixture.

Empty sidecar on a second live conflict: exit 3, file byte-identical to the conflicted blob, no `.prov`. Whitespace-only sidecar (`"  \n\n"`) same. Parent `mutation-03__whence-stdin` on the same empty sidecar: exit 0, file collapsed to `shared\nend`, `.prov` `"mode": "empty"`. The FIX is the refusal. I watched the parent wipe the hunk.

### Dreamer vs demo

CANDIDATE claims match what ran. Empty hybrid is not a successful tagged merge. `--ours`/`--theirs` are still `git merge-file` plus JSON; they are not the delta. Hybrid is not semantic merge; substring tags only. zsh builtin collision is real; I invoked `python3 ./whence`.

### Scores

- **Novelty 4.** Whole-hunk ours/theirs is `git merge-file`. The object that is not merge-file is: contested spans must be parent-tagged or the write is refused, and the product includes a per-span parent list. Empty-sidecar refusal is a hole close, not a new universe. I watched unmarked mix fail, tagged hybrid succeed, and empty sidecar leave markers.
- **Utility 3.** You have to adopt `[ours:…]` / `[theirs:…]` (and `%%` between regions). I would still use mergetool for the edit. I would use this when I need to *record* a hybrid, or when I want the resolve to fail instead of silently inventing text — including inventing nothing from an empty file.
- **Primitive strength 4.** Contract is sharp: every kept contested span has a parent, or exit ≠ 0 and the file is untouched. Empty stdin, empty sidecar, dual stdin, `FILE -` without `--output` are usage errors, not `mode: empty`. Two parents only; diff3 refused on purpose.
- **Composability 4.** JSON on stdout, sidecar `.prov`, `--output` / `--prov -`, hybrid on stdin, `FILE -` with `--output`, exit 1 refuse / 2 parse / 3 usage. Name collision with zsh `whence` is a real pipe hazard.
- **Empirical credibility 5.** Demo, 31 CLI tests, live git merge in the demo, live hybrid I ran, empty-sidecar contrast against the parent binary on the same conflict.
- **Evolution potential 3.** Empty hybrid is closed. Mergetool driver, git-notes instead of sidecar, unique-vs-shared tags — all still the same object, and easy to ruin. I am not scoring a wish list.
- **Reality-Stripped Strength 4.**

### Reality-stripped

Operation remaining: parse `<<<<<<<` / `=======` / `>>>>>>>`, replace each region with an explicit parent (or tagged mix of both), emit which parent supplied each contested span. Refuse empty hybrid input.

Nearest ordinary workflow: `git mergetool` / `git merge-file --ours|--theirs` / edit the markers by hand.

Lost if replaced: the refuse-unmarked-mix contract (including refuse-empty-hybrid), and a machine-readable parentage list next to the resolved blob. merge-file gives you the blob and forgets. An empty sidecar is a forgotten pipe; git will not save you from it either.

### Verdict

**KEEP.** The provenance object and the tagged-hybrid refusal are real. The empty-sidecar FIX is real against the parent I ran. Do not KEEP it as “ours/theirs CLI”; that already exists. Do not KEEP it as “stdin hybrid”; that was already the parent. KEEP the refuse-unmarked-mix object.

---

## gen3-02 envfrom-dir — KEEP

### Execution

`./demo.sh` exit 0. `python3 -m unittest tests.test_envfrom -v`: 31 tests, OK.

Demo used **this process’s** environment (`LIBRARY_PATH` injected, `PATH` the real login PATH) plus fixtures:

- `LIBRARY_PATH` VALUE empty, SOURCE `file:…/.env:2`, `EMPTY_OVERRIDE: yes`, INHERITED the injected `/usr/local/lib:/usr/lib`.
- `APP_ENV` file `dev` vs inherited `from-shell`.
- `PATH` SOURCE `env` (full real PATH string).
- `NOT_A_REAL_VAR` SOURCE `unset`.
- `--fail-empty LIBRARY_PATH` exit 2.
- `--run` without `--load`: child kept inherited `LIBRARY_PATH`.
- `--run --load`: child `LIBRARY_PATH=''`, `APP_ENV=dev`.
- `--json` array of `{key, value, source, empty_override, inherited}`.
- quoted-export fixture: `export PREFIX`, unquoted quotes, inline comment stripped, `EMPTY_QUOTED=""`, quoted `# not a comment`.
- `--dir` from cwd `here` vs `--dir there` read different trees.
- missing `--dir /no/such/envfrom-dir` exit 1, `directory not found`, not `SOURCE: env`.
- UTF-8 BOM kept `FOO=bom`; invalid UTF-8 exit 1, no traceback.

### Extra probe

Copied non-secret `HDD_*` keys from this repo’s `.env.hdd` into a temp `.env`.

```text
HDD_DREAMER_TRANSPORT  VALUE=openrouter  SOURCE: file:…/.env:1  INHERITED: (unset)
HDD_APP_TITLE          VALUE=hdd-loop    SOURCE: file:…/.env:5  INHERITED: (unset)
HOME                   VALUE=/Users/annenpolka  SOURCE: env
PATH                   SOURCE: env
NOT_A_REAL_VAR         SOURCE: unset
```

Then `HOME=` as a file empty override of the real home directory: `EMPTY_OVERRIDE: yes`, INHERITED `/Users/annenpolka`; `--run --load` child `HOME=''`. `--json` of that record: `"empty_override": true, "inherited": "/Users/annenpolka"`.

`--dir` that is this repo’s `.env.hdd` file: `not a directory`, exit 1.

Hyphen key: `FOO-BAR=hyphen` in the file, `envfrom FOO-BAR` → `SOURCE: unset`. The line exists; the tool reports absence. Interpolation `FOO=${BAR}` is reported as the literal `${BAR}` (documented; not a lie). `.env.local` later-wins: `FOO=two` from `.env.local:1`.

### Dreamer vs demo

Writeup matches the run. Missing DIR is no longer a silent inherit. BOM / invalid UTF-8 match the demo. `--run` without `--load` printing a *would-apply* override while the child stays inherited is shown. Hyphen-key silence is not claimed as done; I still hit it.

### Scores

- **Novelty 3.** `printenv` shows the map. This shows *which line would win*, including the empty assignment that wipes an inherited value. `--dir` exist/isdir is hygiene, not novelty. `--json` is the same record as bytes. It is still dotenv provenance, not a new universe.
- **Utility 4.** “Why is this child’s `LIBRARY_PATH` / `HOME` empty?” is a question I have actually asked. `--fail-empty` is a gate. `--dir` that errors instead of pretending the tree is empty is the difference between a gate and a lie. Highest utility in this set. I would run it tomorrow on a directory with a suspicious `.env`.
- **Primitive strength 4.** SOURCE ∈ {`env`, `file:path:line`, `unset`} plus EMPTY_OVERRIDE plus INHERITED. `--load` is explicit. File assignment is “would apply,” process env is inherited — the split is the contract. Missing DIR / file-as-DIR / unreadable UTF-8 are exit 1. Hyphen keys collapsing to unset weaken the “source” claim.
- **Composability 4.** Keys as argv, `--dir`, `--json`, `--fail-empty` exit 2, `--run --load -- CMD`. JSON is one array. `--run` exec is right.
- **Empirical credibility 5.** Demo on real PATH; my probe on real HOME and a real env file from this repo; missing-DIR / file-as-DIR; 31 tests; quoted-export in the same demo.
- **Evolution potential 3.** Source chain when both files set a key is already last-wins. Dropped-line record for `FOO-BAR` / `KEY+=`. Stop before it becomes direnv.
- **Reality-Stripped Strength 4.**

### Reality-stripped

Operation remaining: for named keys, report whether the process map or a dotenv `KEY=` line supplies the value, and whether that line is empty while the process still has a value; optionally exec a child with the overlay. Honor `--dir`. Error if DIR is missing or not a directory.

Nearest ordinary workflow: `printenv KEY`; `grep KEY .env .env.local`; `set -a; source .env; set +a`.

Lost if replaced: file:line, the empty-override bit, the inherited value that would be wiped, the would-apply vs did-apply split (`--run` without `--load`), `--fail-empty`, missing-DIR as an error. `printenv` after sourcing has already forgotten the wipe. `grep` on a missing directory is also an error; the join is not.

### Verdict

**KEEP.** Strongest everyday object in the set. The DIR FIX is real (I saw exit 1, not `SOURCE: env`). I would run it tomorrow. Do not KEEP it as “`--json` around envfrom”; that is encoding.

---

## gen3-03 stated-honest — KEEP

### Execution

`./demo.sh` exit 0. `python3 -m unittest tests.test_stated -v`: 22 tests, OK.

Demo (all under `fixtures/`):

- `timeout` disagree `config.yaml: 5` vs `app.py: 10` → status DISAGREE, exit 2, one pair.
- both 5 → AGREE, exit 0.
- config only → DECLARED_ONLY.
- `${WAIT}` vs `os.getenv("WAIT")` → UNKNOWN, not a fake equality. Displayed `value=${WAIT` — the closing `}` is eaten (`--json` `"raw_value": "${WAIT"`).
- comments/docstrings/`/* */` labeled, not counted as contradictions; `int timeout = 5` counted.
- `--json` disagreement pair.
- compact JSON `{"timeout": 5, "host": "localhost"}` vs `timeout = 10` → DISAGREE, exit 2.
- dotenv `.env TIMEOUT=30` / `timeout=99` is not a declaration; `stated timeout` still yaml 5 vs py 10; `stated TIMEOUT` → NONE, not DECLARED_ONLY.
- string literal `"timeout = 99 is wrong"` is not an assignment; DECLARED_ONLY 5.
- `strlit_and_assign` (I ran): string ignored, real `timeout = 10` still DISAGREE.

### Extra probe on **this repo**, not fixtures

```text
$ python3 stated HDD_DREAMER_MODEL <brrr-root>
status: NONE
note: no declaration or assignment sites

$ python3 stated HDD_APP_TITLE <brrr-root>
status: NONE

$ python3 stated timeout lab-hdd/scripts
status: UNKNOWN
assignments:
  credits.py:40  with urllib.request.urlopen(req, timeout=30) as resp:
  value=30) as resp: (not comparable: expression)
```

Temp tree with this repo’s `.env.hdd` copied to `.env` plus `credits.py` / `POPULATION.json`: `HDD_DREAMER_MODEL` NONE, `HDD_APP_TITLE` NONE, `timeout` UNKNOWN on the kwargs site. Dotenv-not-declaration is doing what it says. It also means this repo’s actual config values are invisible to the pair.

`stated timeout lab-hdd` (the tree that contains every copy of the toy): status DISAGREE, **420** disagreement pairs. Declaration `candidate-02/fixtures/comments/config.yaml timeout: 5` is paired with assignments in *other* lineages’ `app.py`. The pair is a cartesian product of every comparable declaration with every comparable assignment in the walk, not “this project’s config vs this project’s source.”

Nested `{"server": {"timeout": 5}}` vs `timeout = 10`: ASSIGNED_ONLY 10. `stated server.timeout`: NONE.

I never got a DISAGREE pair off real non-fixture input. Keyword argument `timeout=30` is still scanned as an assignment (UNKNOWN, garbage `value=`). Unquoted env values are now excluded rather than compared.

### Dreamer vs demo

CANDIDATE sells honesty: dotenv is env-layer, compact JSON is a declaration, a quoted `timeout = 99` is not an assignment. All three ran on fixtures. “The result is a disagreement pair, not a hit list” is true **on the integer fixtures** and a lie **on lab-hdd**, where the result is four hundred cross-copy pairs. `${WAIT}` truncation is a leftover hole; UNKNOWN still fired, so it did not invent equality.

### Scores

- **Novelty 3.** The pair as the observable, plus an honest UNKNOWN, plus dotenv-not-decl, is more than `rg KEY`. Compact JSON as a declaration is a real cut versus start-of-line `KEY:`. It is still grep plus a scalar matcher. Cartesian pairing is grep-shaped in the worst way.
- **Utility 2.** Exit 2 on comparable disagree is CI-shaped. I would not have caught a real config drift in this tree. The honesty cut made `.env.hdd` disappear. Keyword-arg false friend remains. Pointed at a directory of copies of itself, it screams. First Selection’s install condition (“unquoted env values and call kwargs stop looking like the product”) failed.
- **Primitive strength 3.** Declaration vs assignment vs comment, comparable vs not, dotenv out of the declaration list: that cut is real on toys. Nested keys are not paths. The pair algebra (every decl × every assign) is the wrong object for a multi-package tree. I saw the UNKNOWN gate refuse to guess; that is still the strong part.
- **Composability 3.** `stated KEY [DIR]`, `--json`, exit 2 only on comparable disagreement. Stdin ignored. Cartesian stdout is anti-composition: you cannot pipe “the pair” when there are 420 of them across unrelated fixtures.
- **Empirical credibility 3.** Demo and tests are green and match the writeup **for fixtures**. Compact JSON, dotenv-not-decl, strlit: I saw them. The advertised disagreement pair did not appear on real input I ran except as a cartesian of the toys. `${WAIT` is a display/token bug I measured. Credibility is not 5.
- **Evolution potential 3.** Nested paths, not treating `f(timeout=30)` as assignment, keep the `}` of `${WAIT}`, pair within a file or package instead of the whole walk. Worth breeding. Easy to become a fake multi-language interpreter; kill that. Cartesian pairing is a primitive fix, not a feature.
- **Reality-Stripped Strength 3.**

### Reality-stripped

Operation remaining: walk config-like vs source-like files, regex `KEY` with `:` / `=`, skip dotenv, skip quoted string assignments, compare trailing tokens if they look like scalars, print declaration/contradiction pairs. Compact JSON object members count as declarations.

Nearest ordinary workflow: `rg KEY` and read the two sites.

Lost if replaced: exit 2 on a comparable mismatch, the UNKNOWN refusal, comment labeling, dotenv-not-decl, compact-JSON declarations. You still find the sites with rg. You do not get a pair object or a non-zero CI bit unless you write the comparison. You also do not get 420 cross-copy pairs unless you write that mistake.

### Verdict

**KEEP** as a breeding object (the pair + UNKNOWN gate + dotenv-not-decl + compact JSON). Do not install. Do not KEEP it as “timeout debugger”; that still only works on `5` vs `10`. The cartesian product on a real tree of copies is evidence against the pair algebra, not for it.

---

## gen3-04 effect-compact — KEEP

### Execution

`./demo.sh` exit 0. `python3 -m unittest tests.test_effect -v`: 18 tests, OK.

Demo (joint record, not two CLIs concatenated):

- disagree: DECLARED 5, ASSIGNED 10, ENV_SOURCE `TIMEOUT file:.env:2 value=30`, EFFECTIVE unknown `declared 5 vs assigned 10`, exit 2.
- inherited `TIMEOUT=from-shell` still shows file 30 as the would-apply overlay; EFFECTIVE still unknown on the 5 vs 10.
- agree both 5, env unset → EFFECTIVE 5, exit 0.
- config only → EFFECTIVE 5.
- empty override: declared 5, `os.getenv("TIMEOUT", "5")` not comparable, file `TIMEOUT=` EMPTY_OVERRIDE, EFFECTIVE unknown `literal 5 vs env (empty)`.
- deferred: config `${WAIT}`, `os.getenv("WAIT")`, file `WAIT=10` vs inherited `from-shell` → ENV_SOURCE WAIT `why=deferred`, **EFFECTIVE 10**.
- unknown interpolation, WAIT unset → EFFECTIVE unknown `sites defer to unset env`.
- comments ignored; EFFECTIVE 5.
- `os.environ.get` / `process.env.WAIT`: EFFECTIVE unknown `literal 5 vs env 10`.
- `--json` joint object with `env_source`, `effective`, `disagree`.
- compact JSON `{"timeout": 5}` vs `timeout = 10` → DECLARED 5, EFFECTIVE unknown, exit 2.

### Extra probe

Kill test on the deferred fixture (the CANDIDATE’s own “kill if concatenation loses nothing”):

```text
stated timeout  → UNKNOWN  (${WAIT} vs os.getenv("WAIT"))
envfrom timeout → SOURCE: unset
envfrom WAIT    → file:.env:1 value=10  INHERITED: from-shell
effect timeout  → EFFECTIVE 10
```

To recover 10 from the parents you must read the sites, name WAIT, and ignore printenv’s inherited from-shell. Concatenation of `stated timeout; envfrom timeout` is UNKNOWN + unset. The join is the object. I saw it.

Parent `hybrid-01__effect` on this lineage’s `fixtures/compact_json`: DECLARED (none), EFFECTIVE 10, exit 0 — a false assigned-only 10. This binary: DECLARED 5, EFFECTIVE unknown, exit 2. The compact-JSON FIX is real against the parent I ran.

Real `.env.hdd` copied to `.env`: `effect HDD_DREAMER_MODEL` prints ENV_SOURCE `file:.env:7 value=deepseek/deepseek-r1` and EFFECTIVE unknown `no declaration or assignment sites`. Honest. `effect timeout lab-hdd/scripts` is the same kwargs garbage as stated (`value=30) as resp:`), EFFECTIVE unknown.

Nested `{"server": {"timeout": 5}}` vs `timeout = 10`: DECLARED (none), EFFECTIVE **10**, exit 0. Compact-JSON FIX is top-level members only. Nested still lies the way the parent lied on compact JSON.

`os.getenv("TIMEOUT", "5")` with file `TIMEOUT=10` and declared 5: EFFECTIVE unknown `literal 5 vs env 10`. The static default `"5"` is not used. Honest unknown, not a false 5.

### Dreamer vs demo

“Not `stated KEY && envfrom KEY`” is true on the deferred fixture. Compact JSON miss that made EFFECTIVE a false 10 is closed at top level; I compared the parent. Nested JSON still does that lie. getenv default is not claimed as done.

### Scores

- **Novelty 4.** The four-field record with deferred-name env join is not either parent. Dotenv as env-layer, `${WAIT}` / `os.getenv("WAIT")` / `process.env.WAIT` pulling WAIT into the same record, EFFECTIVE refusing to pick a winner when layers disagree — I have not seen that as one CLI. Compact-JSON copy is a FIX, not novelty.
- **Utility 3.** “What would this key actually be, given config + source + env?” is a question I ask. On this repo the answer was UNKNOWN plus an env source line, which is still more than `rg`. I would reach for **envfrom** first for empty-override, and **effect** only when the name in the source is not the key I typed. Not a daily PATH entry.
- **Primitive strength 4.** DECLARED / ASSIGNED / ENV_SOURCE / EFFECTIVE is a sharp record. Exit 2 is declared-literal vs assigned-literal, not an env fight. Deferred `why=` is the contract. Nested compact JSON emitting EFFECTIVE 10 with DECLARED none is the same primitive failure the FIX was supposed to close, one shape down.
- **Composability 3.** `effect [--json] KEY [DIR]`, exit 2 on comparable decl/assign disagree. Block-oriented stdout. Stdin ignored (same as stated). `--json` is the pipe form.
- **Empirical credibility 4.** Demo + 18 tests green. Kill test I ran. Compact JSON vs parent I ran. Real `.env.hdd` ENV_SOURCE I ran. Not 5: EFFECTIVE 10 is a fixture; nested JSON still reports a false assigned-only 10; kwargs garbage is shared with stated.
- **Evolution potential 3.** Nested JSON members, getenv static default, announce skipped files. Stop before it becomes a runtime interpreter. The join is the thing to breed, not a third scanner.
- **Reality-Stripped Strength 4.**

### Reality-stripped

Operation remaining: for a named key, list config declarations (not dotenv), source assignments, and env provenance of the key plus names those sites defer to; if the comparable layers agree, print that scalar, else `unknown` plus why.

Nearest ordinary workflow: `rg KEY`; `grep KEY .env`; `printenv`; read the getenv argument by eye.

Lost if replaced: the deferred-name join (WAIT riding on a `timeout` query), dotenv kept out of DECLARED, EFFECTIVE as a first-class unknown. `stated KEY; envfrom KEY` loses WAIT. Nested JSON EFFECTIVE 10 is not lost with grief; that one is a lie.

### Verdict

**KEEP.** The join is real; concatenation fails the deferred fixture. Compact-JSON FIX holds at top level against the parent. Do not install until nested JSON stops inventing EFFECTIVE. Do not KEEP it as “stated plus envfrom printed together.”

---

## mutation-02 owes-strict — KEEP

### Execution

`./demo.sh` exit 0. `python3 tests/test_owes.py -v`: 14 tests, OK.

Demo:

1. deleted `validate_input`, still in README → unkept reference, exit 2.
2. remaining doc `MUST exist: SECURITY.decision.md` / `required file: docs/threat-model.md` → missing companions, exit 2. Backtick `must read \`docs/adr.md\`` is not a companion.
3. clean change → `no unkept obligations`, exit 0.
4. prose markdown with incidental `README.md` backticks → exit 0.

Plus-line changelog fixture (I ran): leftover README mention of `validate_input`; CHANGELOG plus-line `"Removed validate_input…"` skipped. Exit 2. Matches the parent claim.

### Extra probe

Copied real `lab-hdd/scripts/r1_budget.py`, deleted `def can_spend(...)`, left the call site. Exit 2:

```text
unkept references:
  can_spend
    r1_budget.py:207: ok, reason = can_spend(ledger, phase)
```

That half of the primitive fired on a real function. `--json` listed the same site and `missing_companions: []`.

`--diff` via process substitution (`<(git diff …)`): `owes: diff not found: /dev/fd/12`, exit 1. Needs a real file path.

`--tree lab-hdd --diff` of an empty (0-byte) git diff still reported missing companions: `/etc/passwd`, `/no/such/owes-abs-missing`, `PATH`, `SECURITY.decision.md`, `docs/threat-model.md`, `util.py`, and the token `|required` harvested from DESTROYER prose `MUST exist:|required`. Companion scan does **not** consult the diff. On a tree that *describes* the tool, the tool reports its own documentation as broken obligations.

Own README / CANDIDATE.md as remaining tree, dummy change `old`→`new`: `MUST exist: PATH` and `SECURITY.decision.md` self-hits, exit 2. Strict companions closed backticks (fixture 4, exit 0). They did not close “the README that documents the phrases.”

`---def validate_input(value):` as a minus line (no space after `---`): this binary exit 2, `validate_input` in README. Parent `candidate-03__owes` on the same snapshot: `no unkept obligations`, exit 0. The header-collision FIX is real against the parent I ran.

`MUST exist: /etc/passwd` with no such file in the snapshot: reported missing. Companions resolve in the remaining tree, not `Path("/etc/passwd").exists()` on the host. That is the intended remaining-tree rule; I saw it.

### Dreamer vs demo

“Incidental backtick paths in prose are not obligations” — shown (fixture 4). “Companion harvest is only `MUST exist:` / `required file:`” — shown, and then those two phrases fire on every markdown file that *mentions* them. CANDIDATE does not say companions ignore the diff. Punished. Leftover identifier plus plus-line skip match the writeup.

### Scores

- **Novelty 3.** Leftover identifier after a delete is `git diff` + `rg`. Packaging it with plus-line skip is a small composition. Strict companions vs parent backticks is a real delta versus the parent landmine, not versus `rg 'MUST exist:'`. `|required` as a path is the phrase matcher eating regex prose.
- **Utility 2.** Identifier leftover on `can_spend` is something I would want. Companion half is still unusable on real markdown — including this lineage’s README and the destroyer writeup. Empty diff + full-tree companion walk is a linter for a convention almost no repo uses, pointed at the docs that describe it.
- **Primitive strength 3.** “Names defined on minus lines still mentioned in the remaining tree” is a real object; I saw it, including `---def` that the parent dropped. Companions are a second, weaker object, unbound from the change. Two objects glued under one noun.
- **Composability 3.** `DIR` as `before/`+`after/` or `change.diff`+`tree/`, `--tree` `--diff`, `--json`, exit 2. Unix-shaped until `--diff` refuses `/dev/fd/N`. Stdin ignored (`cat change.diff | owes` is usage).
- **Empirical credibility 4.** Demo/tests green. Plus-line skip verified. Real `can_spend` leftover verified. Dashdef vs parent verified. `/etc/passwd` remaining-tree verified. Real-tree companion run was self-hits and a 0-byte diff. Not 5: the “tied to the change” story for companions is still false.
- **Evolution potential 3.** Bind companions to files the diff touched, or delete the companion half. Skip identifiers still defined in the remaining tree. Do not add more phrase regexes.
- **Reality-Stripped Strength 3.**

### Reality-stripped

Operation remaining: take minus-line `def`/`class`/`function`/CONST names (headers are `--- ` / `+++ ` / `@@ ` with a following space), search the remaining tree; also regex `MUST exist:` / `required file:` in `*.md` and test existence inside that tree.

Nearest ordinary workflow: `git diff` + `rg old_name`. For companions: `rg 'MUST exist:'`.

Lost if replaced: plus-line skip (changelog “Removed foo” not counted), `---def` treated as a minus line, one exit code for leftover mentions. Companion half is lost without grief; rg of the same phrases is more honest because it does not pretend to be about the change. Backtick-after-must is already gone; do not resurrect it.

### Verdict

**KEEP** for leftover identifiers. Treat companion scanning as a landmine, not a feature, until it is bound to the diff. Not a PATH tool. Strict phrases fixed the parent’s prose-backtick fire; they did not fix “docs that mention `MUST exist: PATH`.”

---

## mutation-04 capdiff-json — KEEP

### Execution

`./demo.sh` exit 0. `python3 -m unittest discover -s tests -v`: 21 tests, OK.

Demo:

- capture `a` (2 files, 1 env) and `b` (3 files, 1 env).
- `diff a b` exit 2: ENV modified `API_KEY` local-ci-key vs remote-ci-key; FILES modified `.env` hashes; FILES extra `extra.txt`.
- env-only replay printed `local-ci-key` then `remote-ci-key` via `fixtures/print_key.py` with no host `API_KEY` required.
- capture of a dir with no `.env` → 0 env vars; diff vs `a` reports `ENV missing: API_KEY=local-ci-key` and FILES missing `.env` / `app.txt`.
- `diff a b --json` exit 2: `{a, b, env, files}` with object arrays; empty buckets `[]`, not `(none)`.
- `diff a none --json` missing is `{key, value}` / `{path, hash}`.
- `diff a a --json` exit 0, all buckets `[]`.

### Extra probe

`--files` (not in `demo.sh`): replay into an empty dir. Child saw `API_KEY=local-ci-key`; dir gained a `.env`. File body of `app.txt` was **not** restored. Matches README honesty.

Real `lab-hdd/scripts` (12 files, 0 env) vs `lab-hdd/judges` (10 files, 0 env). Diff exit 2, FILES extra/missing listed the actual names (`AXES.md` … vs `credits.py` …), ENV all `(none)`. `--json` exit 2, `env` buckets empty arrays, file extra/missing as `{path, hash}`. Named hash-diff of two real directories works. There is no `.env` in those trees, so the env half of the object was idle.

`capture .` / `capture ..`: `NAME must match ^[A-Za-z0-9._-]+$`, exit 1. Corrupt `manifest.json`: `capdiff: corrupt capture bad: …`, exit 1, including under `--json`. Hand-set `"truncated": true` on an otherwise identical pair: text prints `truncated: comparison incomplete`, JSON grows `"truncated":{"a":true,"b":true}`, exit 2 not 0.

### Dreamer vs demo

“Compared object is the labeled capture, not an ad-hoc pair of dumps” — I saw `.capdiff/NAME/{.env,manifest.json}` in cwd. “Replay restores env, not file bodies” — shown. `--json` is the same six buckets as a document; I parsed it. Default text mode unchanged from the parent story. JSON is encoding.

### Scores

- **Novelty 2.** This is a named directory of `{parsed .env, sha256 map}` plus `diff` and `export+exec`. `--json` is `json.dumps` of that. I can do it with `cp`, `find | xargs shasum`, `diff`, and `env`. The label is the product. Empty JSON arrays vs `(none)` is not a new noun.
- **Utility 3.** “Local CI vs remote CI” is a job I have had. ENV vs FILES split on `.env` (parsed `API_KEY` **and** hash of comments) is the one thing `diff -ru` does not say in one glance. Replay that cannot restore hashed files is half a time machine. JSON helps a script; I still `diff -rq` by hand.
- **Primitive strength 3.** The capture is a real noun. I compared two names, not two paths. `.` / `..` are not labels. Overlay replay does not unset host keys; empty env map means “add nothing.” Truncated comparison is not identity. Cap 5000 files. Honest, small.
- **Composability 3.** Three verbs, exit 2 on any delta, `--json` one line, exec for replay. Store is cwd `.capdiff`, not a stream. Not a pipe tool. JSON is the only pipe-shaped output, and it is a dump of the store.
- **Empirical credibility 4.** Demo+21 tests green; `--files` verified by me; real dirs hashed; `.`/`..` / corrupt / truncated verified. Not 5 because the headline “capture / diff / replay” replay cannot replay the files it hashed.
- **Evolution potential 2.** `--json` was the mutation. Process-env subset, include/exclude globs, `env -i` unset — bounded, and a step toward flag soup. Do not add tarball import or vaults. I am not breeding encoding.
- **Reality-Stripped Strength 2.**

### Reality-stripped

Operation remaining: copy `.env` if present, hash files, store under a name, print ENV/FILES modified/extra/missing between two names (text or JSON), overlay parsed env and exec.

Nearest ordinary workflow: `diff -rq A B`; `env $(cat .env | xargs) cmd`; keep dated dump directories by hand.

Lost if replaced: a single name for “this env map + this tree fingerprint,” and the parsed-key vs file-hash split on the same `.env`. You can reconstruct both with a script. You do not get file-body replay from this tool either. JSON empty arrays instead of `(none)` are not lost with grief.

### Verdict

**KEEP** as a labeled capture noun, thin on purpose. `--json` is not a reason to KEEP it harder. Kill if it grows daemons or tarball restore. I would still `diff -rq` tomorrow unless I needed the ENV/FILES split.

---

## Skeptic notes (not averaged)

- **envfrom** and **whence** are the only two I would type tomorrow. Both produced an object on real input that `printenv` / `git merge-file` do not. Empty PATH slots for the other four.
- **effect** is the only new KEEP-worthy *join* in this set. `stated timeout; envfrom timeout` loses WAIT. I ran that. Compact JSON FIX holds at top level against `hybrid-01`. Nested JSON still invents EFFECTIVE 10. Breeding object, not PATH.
- **stated** honesty cuts (dotenv-not-decl, strlit, compact JSON) are real on fixtures. Real trees: NONE on this repo’s env keys, UNKNOWN on `timeout=30` kwargs, 420 cartesian pairs on `lab-hdd`. Failed the First Selection install condition. KEEP the pair; do not install the binary.
- **owes** leftover identifier still fires on `can_spend`. Strict companions closed backticks and `--def` headers; they did not bind companions to the change. Empty diff of `lab-hdd` still screams `MUST exist: PATH`. KEEP leftover names; treat companions as a landmine.
- **capdiff** is a named dump plus JSON encoding. KEEP the noun; I will not fight Unix for `diff -rq`. `.` / `..` / corrupt / truncated behave; file-body replay still does not exist.
- Empirical 5 means I ran it and it matched, not that it should exist. High E without a 5 on stated/effect/owes/capdiff where advertised behavior was fixture-only or still lying on a nearby shape (nested JSON, unbound companions, replay of hashed files).
- I did not see stated’s disagreement pair on non-fixture input, owes’s companions-tied-to-a-change, capdiff file-body replay, or effect EFFECTIVE on a real (non-fixture) deferred name, because those things did not happen.
- Parent contrast is evidence, not authority: empty hybrid wipe (`mutation-03`), false EFFECTIVE 10 (`hybrid-01`), dropped `---def` (`candidate-03`). I ran those three binaries on the same inputs as the children.
- Multiple KEEP is satisfied: six KEEP, zero KILL. Empty PATH slots are allowed; I am not minting six binaries. Tomorrow list is two.

### Tomorrow list

1. **envfrom** — empty override vs inherited, with `--dir` that errors on a missing tree.
2. **whence** — tagged hybrid + provenance + refuse empty/unmarked.

Slots 3–6 empty.
