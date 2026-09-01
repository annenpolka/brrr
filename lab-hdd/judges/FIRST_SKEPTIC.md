# First Selection — Skeptic

Role: assume the tool should not exist until execution evidence shows otherwise.
Date: 2026-09-02.

Did **not** read `EVOLUTION_REPORT.md`, `lab/`, previous lineages, previous judge reports, or `.hdd/` Dreamer transcripts. Origin method/trial in `CANDIDATE.md` is ignored. The CLI either did something on input I ran, or it did not.

I ran `./demo.sh` and the shipped unittest command in each of `lab-hdd/lineages/candidate-01__whence` … `candidate-07__hits`. All seven demos exited 0. All seven test suites exited 0. I then pointed each binary at non-fixture input (live git merge, this repo’s `.env.hdd` / `lab-hdd/scripts` / `lab-hdd/judges` / `POPULATION.json`, a deleted real function, `grep` contrast). Fixture-only success is not enough for a 5 on empirical credibility. Dreamer-sounding claims that the demo does not show are punished on that axis and on utility.

KEEP bar: I saw an object I cannot get from one ordinary command without writing a script. A mandatory flag around `stat`/`cmp`/`grep` is not an object.

| Candidate | Decision | N | U | P | C | E | Ev | RS | Sum |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 01 whence | **KEEP** | 4 | 3 | 4 | 4 | 5 | 4 | 4 | 28 |
| 02 stated | **KEEP** | 3 | 2 | 3 | 4 | 3 | 4 | 3 | 22 |
| 03 owes | **KEEP** | 3 | 2 | 3 | 4 | 3 | 4 | 3 | 22 |
| 04 capdiff | **KEEP** | 2 | 3 | 3 | 3 | 4 | 3 | 2 | 20 |
| 05 envfrom | **KEEP** | 3 | 4 | 4 | 4 | 5 | 3 | 4 | 27 |
| 06 same | **KILL** | 2 | 2 | 3 | 3 | 5 | 2 | 2 | 19 |
| 07 hits | **KILL** | 1 | 2 | 2 | 2 | 5 | 2 | 1 | 15 |

N Novelty · U Utility · P Primitive strength · C Composability · E Empirical credibility · Ev Evolution potential · RS Reality-Stripped Strength. 0–5. Not averaged with other judges.

Tomorrow I would actually type **envfrom** and **whence**. The other KEEPs are breeding objects, not PATH entries. `same` and `hits` are lectures around tools I already have.

---

## candidate-01 whence — KEEP

### Execution

`./demo.sh` exit 0. `python3 -m unittest discover -s tests -v`: 18 tests, OK (demo already runs this suite; I ran it again).

Demo showed, on this machine:

- `report` of `fixtures/simple.conflict` (HEAD vs feature).
- `--ours` / `--theirs` overwrite plus JSON provenance and a `.prov` sidecar.
- `--hybrid fixtures/hybrid-tagged.txt` kept `color = red` from ours and `2` from theirs; spans named both parents.
- untagged mix `color = red` + `size = 2` refused, exit 1, markers left in the file, no `.prov`.
- diff3 `|||||||` refused, exit 2.
- `git merge-file -p --ours` printed a blob and stopped.
- a throwaway two-branch git repo with `merge.conflictStyle=merge` produced real `<<<<<<< HEAD` markers; `--ours` kept `value = 1\n` and recorded `mode: ours`.
- messy three-region hybrid: short sidecar named `region 3/3 … MISSING tagged block`; wrong-parent quoted name pointed at theirs; successful hybrid left `# eof` with no trailing newline (`xxd` tail `23 2065 6f66`).

Extra probe (not the demo): live git merge of `color = red` / `size = 9` vs `color = blue` / `size = 2`, then tagged hybrid on stdin. Exit 0. Resolved file:

```text
shared
color = red
size = 2
end
```

Provenance spans: ours `"color = red"`, theirs `"2"`. That is the primitive on a real conflict, not `--ours` on a fixture.

### Dreamer vs demo

CANDIDATE claims match what ran. No mergetool driver (listed under Failures; not shown; not counted). Hybrid is not semantic merge; substring tags only — demo and my live merge both used that. zsh builtin collision is real; I invoked `python3 ./whence`.

### Scores

- **Novelty 4.** Whole-hunk ours/theirs is `git merge-file`. The object that is not merge-file is: contested spans must be parent-tagged or the write is refused, and the product includes a per-span parent list. I watched unmarked mix fail and tagged hybrid succeed.
- **Utility 3.** You have to adopt `[ours:…]` / `[theirs:…]` (and `%%` between regions). I would still use mergetool for the edit. I would use this when I need to *record* a hybrid, or when I want the resolve to fail instead of silently inventing text.
- **Primitive strength 4.** Contract is sharp: every kept contested span has a parent, or exit ≠ 0 and the file is untouched. Two parents only; diff3 refused on purpose. That is a primitive, not a TUI.
- **Composability 4.** JSON on stdout, sidecar `.prov`, `--output` / `--prov -`, hybrid on stdin, exit 1 refuse / 2 parse / 3 usage. Name collision with zsh `whence` is a real pipe hazard.
- **Empirical credibility 5.** Demo, 18 CLI tests, live git merge in the demo, live hybrid I ran. Claims about `git merge-file` having no parentage were checked in the same demo.
- **Evolution potential 4.** Mergetool driver, git-notes instead of sidecar, SequenceMatcher tag proposals — all still the same object. Easy to ruin by adding a third parent or a language parser.
- **Reality-Stripped Strength 4.**

### Reality-stripped

Operation remaining: parse `<<<<<<<` / `=======` / `>>>>>>>`, replace each region with an explicit parent (or tagged mix of both), emit which parent supplied each contested span.

Nearest ordinary workflow: `git mergetool` / `git merge-file --ours|--theirs` / edit the markers by hand.

Lost if replaced: the refuse-unmarked-mix contract, and a machine-readable parentage list next to the resolved blob. merge-file gives you the blob and forgets.

### Verdict

**KEEP.** The provenance object and the tagged-hybrid refusal are real. Do not KEEP it as “ours/theirs CLI”; that already exists.

---

## candidate-02 stated — KEEP

### Execution

`./demo.sh` exit 0. `python3 -m unittest tests.test_stated -v`: 14 tests, OK.

Demo (all under `fixtures/`):

- `timeout` disagree `config.yaml: 5` vs `app.py: 10` → status DISAGREE, exit 2, one pair.
- both 5 → AGREE, exit 0.
- config only → DECLARED_ONLY.
- `${WAIT}` vs `os.getenv("WAIT")` → UNKNOWN, not a fake equality.
- comments/docstrings/`/* */` labeled, not counted as contradictions; `int timeout = 5` counted.
- `--json` disagreement pair.

Extra probe on **this repo**, not fixtures:

```text
$ python3 stated HDD_DREAMER_MODEL <brrr-root>
status: UNKNOWN
note: declared, but no comparable scalar
declarations:
  .env.hdd:7  HDD_DREAMER_MODEL=deepseek/deepseek-r1
  value=deepseek/deepseek-r1 (not comparable: expression)

$ python3 stated HDD_APP_TITLE <brrr-root>
status: UNKNOWN
  HDD_APP_TITLE=hdd-loop  (not comparable: unparsed)

$ python3 stated timeout lab-hdd/scripts
status: UNKNOWN
assignments:
  credits.py:40  with urllib.request.urlopen(req, timeout=30) as resp:
  value=30) as resp: (not comparable: expression)
```

I never got a DISAGREE pair off real input. Slash in a model id is “expression”. Hyphenated `hdd-loop` is “unparsed”. A keyword argument `timeout=30` is scanned as an assignment.

### Dreamer vs demo

CANDIDATE sells “it only broke after I changed the timeout” and “the result is a disagreement pair, not a hit list.” The pair exists **on the integer fixtures**. README’s “literal scalars (`5`, `"5"`, `true`)” is the honest scope. Real env-style values in this repo did not compare. Comment-handling dogfood is in the current demo (after-state only; I did not reproduce the pre-fix false DISAGREE).

### Scores

- **Novelty 3.** The pair as the observable, plus an honest UNKNOWN, is more than `rg KEY`. It is still grep plus a scalar matcher. Easy to dismiss; the dismissal is half right until the matcher survives real values.
- **Utility 2.** Exit 2 on comparable disagree is CI-shaped. I would not have caught a real config drift in this tree. Keyword-arg false friend plus “unparsed” on ordinary unquoted strings makes the advertised debugging loop miss the files I actually opened.
- **Primitive strength 3.** Declaration vs assignment vs comment, comparable vs not: that cut is real on toys. It is a line regex, not a language. Nested keys are not paths. I saw the UNKNOWN gate refuse to guess; that is the strong part.
- **Composability 4.** `stated KEY [DIR]`, `--json`, exit 2 only on comparable disagreement. That is a filter.
- **Empirical credibility 3.** Demo and tests are green and match the writeup **for fixtures**. The primitive (disagreement pair) did not appear on real input I ran. Credibility is not 5.
- **Evolution potential 4.** Nested keys, hyphenated/path scalars, not treating `f(timeout=30)` as assignment — all still the same pair object. Worth breeding. Easy to become a fake multi-language interpreter; kill that.
- **Reality-Stripped Strength 3.**

### Reality-stripped

Operation remaining: walk config-like vs source-like files, regex `KEY` with `:` / `=`, compare trailing tokens if they look like scalars, print declaration/contradiction pairs.

Nearest ordinary workflow: `rg KEY` and read the two sites.

Lost if replaced: exit 2 on a comparable mismatch, the UNKNOWN refusal, comment labeling. You still find the sites with rg. You do not get a pair object or a non-zero CI bit unless you write the comparison.

### Verdict

**KEEP** as a breeding object (the pair + UNKNOWN gate). Do not install until unquoted env values and call kwargs stop looking like the product. Punished for selling timeout-debugging on fixtures that are `5` vs `10`.

---

## candidate-03 owes — KEEP

### Execution

`./demo.sh` exit 0 (three fixtures only). `python3 tests/test_owes.py -v`: 10 tests, OK.

Demo:

1. deleted `validate_input`, still in README → unkept reference, exit 2.
2. remaining doc `MUST exist: SECURITY.decision.md` / `required file: docs/threat-model.md` / `must read \`docs/adr.md\`` → missing companions, exit 2. No `make test` (the false companion they documented).
3. clean change → `no unkept obligations`, exit 0.

Claims **not** in `demo.sh` that I ran myself:

- `fixtures/plus-line-changelog`: leftover README mention of `validate_input`, CHANGELOG plus-line `"Removed validate_input…"` skipped. Exit 2. Matches CANDIDATE.

Extra probe, real tree:

```text
$ python3 owes --tree lab-hdd --diff <git diff HEAD~1 -- lab-hdd>
missing companions:
  *.md          (from CANDIDATE.md “MUST-like phrases, not only `*.md`”)
  LICENSE\      (from Failures: “must ship \`LICENSE\`”)
  PATH          (from README documenting `MUST exist: PATH`)
  SECURITY.decision.md
  \]            (from whence CANDIDATE “must be escaped as `\]`”)
  docs/adr.md
  docs/threat-model.md
  path\
  util.py
exit=2
```

Companion scan does **not** consult the diff. `find_missing_companions` walks remaining `*.md` regardless of the change. On a tree that *describes* the tool, the tool reports its own documentation as broken obligations.

Second extra probe: copied real `lab-hdd/scripts/r1_budget.py`, deleted `def can_spend`, left the call site. Exit 2:

```text
unkept references:
  can_spend
    r1_budget.py:183: ok, reason = can_spend(ledger, phase)
```

That half of the primitive fired on a real function.

### Dreamer vs demo

“Missing companion artifact named by remaining docs is a first-class miss **tied to the change**” is not what the code does. Fixture 2 looks tied to the change because the fixture directory contains nothing else. On `lab-hdd` it is a repo-wide phrase grep. CANDIDATE Failures already say they will not understand policy language; they do not say companions ignore the diff. Punished.

Plus-line skip is real (I ran it). `make test` false positive is gone from the current demo.

### Scores

- **Novelty 3.** Leftover identifier after a delete is `git diff` + `rg`. Packaging it with plus-line skip is a small composition. Companion phrases are a linter for a convention almost no repo uses (`MUST exist: PATH`).
- **Utility 2.** Identifier leftover on `can_spend` is something I would want. Companion half is unusable on real markdown — including the candidate’s own README, which cannot document `MUST exist: PATH` without hitting itself.
- **Primitive strength 3.** “Names defined on minus lines still mentioned in the remaining tree” is a real object; I saw it. Companions are a second, weaker object, unbound from the change.
- **Composability 4.** `DIR` as `before/`+`after/` or `change.diff`+`tree/`, `--tree` `--diff`, `--json`, exit 2. Unix-shaped.
- **Empirical credibility 3.** Demo/tests green. Plus-line claim verified by me, not by `demo.sh`. Real-tree companion run was mostly self-hits. Identifier run on `r1_budget.py` was genuine.
- **Evolution potential 4.** Skip identifiers still defined in the remaining tree; bind companions to files the diff touched (listed, not done). Both would make the object true.
- **Reality-Stripped Strength 3.**

### Reality-stripped

Operation remaining: take minus-line `def`/`class`/`function`/CONST names, search the remaining tree; also regex `MUST exist:` / `required file:` / `must \`path\`` in `*.md` and test existence.

Nearest ordinary workflow: `git diff` + `rg old_name`. For companions: `rg 'MUST exist:'`.

Lost if replaced: plus-line skip (changelog “Removed foo” not counted), one exit code for “the change appears to break a leftover mention.” Companion half is lost without grief; rg of the same phrases is more honest because it does not pretend to be about the change.

### Verdict

**KEEP** for leftover identifiers. Treat companion scanning as a landmine, not a feature, until it is bound to the diff. Not a PATH tool.

---

## candidate-04 capdiff — KEEP

### Execution

`./demo.sh` exit 0. `python3 -m unittest discover -s tests -v`: 11 tests, OK.

Demo:

- capture `a` (2 files, 1 env) and `b` (3 files, 1 env).
- `diff a b` exit 2: ENV modified `API_KEY` local-ci-key vs remote-ci-key; FILES modified `.env` hashes; FILES extra `extra.txt`.
- env-only replay printed `local-ci-key` then `remote-ci-key` via `fixtures/print_key.py` with no host `API_KEY` required.
- capture of a dir with no `.env` → 0 env vars; diff vs `a` reports `ENV missing: API_KEY=local-ci-key` and FILES missing `.env` / `app.txt`.

`--files` is **not** in `demo.sh`. I ran it: capture fixture `a`, `replay … --files -- <empty-dir> python3 -c …`. Child saw `API_KEY=local-ci-key`; empty dir gained a `.env`. File bodies of `app.txt` were not restored. Matches README honesty.

Extra probe: capture real `lab-hdd/scripts` (12 files, 0 env) vs `lab-hdd/judges` (5 files, 0 env). Diff exit 2, FILES extra/missing listed the actual names, ENV all `(none)`. Named hash-diff of two real directories works. There is no `.env` in those trees, so the env half of the object was idle.

### Dreamer vs demo

“Compared object is the labeled capture, not an ad-hoc pair of dumps” — I saw `.capdiff/NAME/{.env,manifest.json}` in cwd. “Replay restores env, not file bodies” — shown. First-commit “missing `.env` is an error” is historical; current demo shows empty map. CANDIDATE’s unittest list still names `test_missing_env_is_error`; living tests name `test_missing_env_is_empty_not_crash`. Transcript drift, not a live lie.

### Scores

- **Novelty 2.** This is a named directory of `{parsed .env, sha256 map}` plus `diff` and `export+exec`. I can do it with `cp`, `find | xargs shasum`, `diff`, and `env`. The label is the product.
- **Utility 3.** “Local CI vs remote CI” is a job I have had. ENV vs FILES split on `.env` (parsed `API_KEY` **and** hash of comments `# local CI` vs `# remote CI`) is the one thing `diff -ru` does not say in one glance. Replay that cannot restore hashed files is half a time machine.
- **Primitive strength 3.** The capture is a real noun. I compared two names, not two paths. Overlay replay does not unset host keys; empty env map means “add nothing.” Cap 5000 files. Honest, small.
- **Composability 3.** Three verbs, exit 2 on any delta, exec for replay. Store is cwd `.capdiff`, not a stream. Not a pipe tool.
- **Empirical credibility 4.** Demo+tests green; `--files` verified by me; real dirs hashed. Not 5 because the headline “capture / diff / replay” replay cannot replay the files it hashed.
- **Evolution potential 3.** Process-env subset, include/exclude globs, `env -i` unset. Bounded. Do not add tarball import or vaults.
- **Reality-Stripped Strength 2.**

### Reality-stripped

Operation remaining: copy `.env` if present, hash files, store under a name, print ENV/FILES modified/extra/missing between two names, overlay parsed env and exec.

Nearest ordinary workflow: `diff -rq A B`; `env $(cat .env | xargs) cmd`; keep dated dump directories by hand.

Lost if replaced: a single name for “this env map + this tree fingerprint,” and the parsed-key vs file-hash split on the same `.env`. You can reconstruct both with a script. You do not get file-body replay from this tool either.

### Verdict

**KEEP** as a labeled capture noun, thin on purpose. Kill if it grows daemons or tarball restore. I would still `diff -rq` tomorrow unless I needed the ENV/FILES split.

---

## candidate-05 envfrom — KEEP

### Execution

`./demo.sh` exit 0. `python3 -m unittest tests.test_envfrom -v`: 14 tests, OK.

Demo used **this process’s** environment (`LIBRARY_PATH` injected, `PATH` the real login PATH) plus fixtures:

- `LIBRARY_PATH` VALUE empty, SOURCE `file:…/.env:2`, `EMPTY_OVERRIDE: yes`, INHERITED the injected `/usr/local/lib:/usr/lib`.
- `APP_ENV` file `dev` vs inherited `from-shell`.
- `PATH` SOURCE `env` (full real PATH string).
- `NOT_A_REAL_VAR` SOURCE `unset`.
- `--fail-empty LIBRARY_PATH` exit 2.
- `--run` without `--load`: child kept inherited `LIBRARY_PATH`.
- `--run --load`: child `LIBRARY_PATH=''`, `APP_ENV=dev`.
- quoted-export fixture: `export PREFIX`, unquoted quotes, inline comment stripped, `EMPTY_QUOTED=""`, quoted `# not a comment`.

Extra probe: copied non-secret keys from this repo’s `.env.hdd` into a temp `.env`.

```text
HDD_DREAMER_TRANSPORT  VALUE=openrouter  SOURCE: file:…/.env:5  INHERITED: (unset)
HDD_APP_TITLE          VALUE=hdd-loop    SOURCE: file:…/.env:11 INHERITED: (unset)
HOME                   VALUE=/Users/annenpolka  SOURCE: env
PATH                   SOURCE: env
NOT_A_REAL_VAR         SOURCE: unset
```

Then `HOME=` as a file empty override of the real home directory: `EMPTY_OVERRIDE: yes`, INHERITED `/Users/annenpolka`; `--run --load` child `HOME=''`.

That is the primitive on a real inherited key, not only `LIBRARY_PATH` the demo exported.

### Dreamer vs demo

Writeup matches the run. `--run` without `--load` printing a *would-apply* override while the child stays inherited is shown, not hand-waved. First-parser failures (`export` dropped, quotes stuck) are historical; current demo shows the after. No interpolation (`${OTHER}`) — not claimed as done.

### Scores

- **Novelty 3.** `printenv` shows the map. This shows *which line would win*, including the empty assignment that wipes an inherited value. I have not seen that as a one-shot CLI. It is still dotenv provenance, not a new universe.
- **Utility 4.** “Why is this child’s `LIBRARY_PATH` / `HOME` empty?” is a question I have actually asked. `--fail-empty` is a gate. Highest utility in this set.
- **Primitive strength 4.** SOURCE ∈ {`env`, `file:path:line`, `unset`} plus EMPTY_OVERRIDE plus INHERITED. `--load` is explicit. File assignment is “would apply,” process env is inherited — the split is the contract.
- **Composability 4.** Keys as argv, `--dir`, `--fail-empty` exit 2, `--run --load -- CMD`. Block-oriented stdout (not JSON) is worse for pipes; `--run` exec is right.
- **Empirical credibility 5.** Demo on real PATH; my probe on real HOME and a real env file from this repo; 14 tests; quoted-export in the same demo.
- **Evolution potential 3.** Source chain when `.env` and `.env.local` both set a key; interpolation. Parser is already a mini-dotenv — stop before it becomes direnv.
- **Reality-Stripped Strength 4.**

### Reality-stripped

Operation remaining: for named keys, report whether the process map or a dotenv `KEY=` line supplies the value, and whether that line is empty while the process still has a value; optionally exec a child with the overlay.

Nearest ordinary workflow: `printenv KEY`; `grep KEY .env .env.local`; `set -a; source .env; set +a`.

Lost if replaced: file:line, the empty-override bit, the inherited value that would be wiped, the would-apply vs did-apply split (`--run` without `--load`), `--fail-empty`. `printenv` after sourcing has already forgotten the wipe.

### Verdict

**KEEP.** Strongest everyday object in the set. I would run it tomorrow on a directory with a suspicious `.env`.

---

## candidate-06 same — KILL

### Execution

`./demo.sh` exit 0. `python3 -m unittest tests.test_same -v`: 13 tests, OK.

Demo (this volume):

- omit kind → usage, lists `inode, bytes, json`, exit 1.
- hardlink `--inode` → `IDENTICAL inode 16777233:128975858`, exit 0 (`demo.sh` recreates the link; git does not preserve it).
- two empty files `--inode` → DISTINCT two inodes, exit 2; `--bytes` → `IDENTICAL bytes sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (known empty digest), exit 0.
- JSON key order `--json` → `IDENTICAL json {"a":2,"b":1}`.
- `--bytes` follows symlink.
- missing path: `same: PATH: No such file or directory`, exit 1, no traceback.
- `--json` on binary: `same: PATH: not JSON (not UTF-8 text)`, exit 1.

Extra probe on real `lab-hdd/POPULATION.json`:

- `--bytes` / `--inode` / `--json` of the file against itself: IDENTICAL, exit 0.
- `--json` printed the **entire canonical JSON document on one line**. Unusable as a verdict on a real population file.
- `--bytes` vs `STATE.md`: DISTINCT two hashes, exit 2.
- `--inode` on two different scripts: DISTINCT two `dev:ino`, exit 2.
- omit kind on the real JSON pair: usage, exit 1.

### Dreamer vs demo

Claims match. The interesting sentence — two empties that `cmp` would call equal are DISTINCT under `--inode` — is true on this disk. That sentence is also `stat` vs `cmp`. `--json` dumping the discriminator in full is not advertised as a problem; on real input it is the output.

### Scores

- **Novelty 2.** Mandatory `--inode|--bytes|--json` is a usage rule. Each kind is `lstat`, `sha256`, `json.dumps(sort_keys=True)`. The refusal to guess is the only interaction.
- **Utility 2.** I will type `cmp`, `stat`, or `jq -S`. On a real JSON file the tool shouted the payload at me. Teaching demo for juniors, not a daily binary.
- **Primitive strength 3.** “Kind is required” is a real constraint; I hit it. IDENTICAL vs DISTINCT under one named kind is a clear object. It is a seatbelt, not a new operation. Strength is the refusal, which is a negative space around three existing operations.
- **Composability 3.** Two paths, one kind, exit 0/2/1. Fine. Large-JSON stdout is anti-composition.
- **Empirical credibility 5.** Demo, tests, real files, known empty hash, named errors. The tool is what it says. Credibility is not the same as necessity.
- **Evolution potential 2.** N-way table still one kind — maybe. CANDIDATE already says kill if it becomes flag soup around `cmp`. I am killing it before the soup.
- **Reality-Stripped Strength 2.**

### Reality-stripped

Operation remaining: compare two local paths under exactly one of {device+inode via lstat, sha256 of followed content, canonical JSON}.

Nearest ordinary workflow: `stat`; `cmp` / `shasum`; `jq -S`.

Lost if replaced: a hard error when you forget to say which sameness you meant. You can still get the wrong answer from `cmp` when you meant inode. That is operator error, not a missing Unix object.

### Verdict

**KILL.** I saw it work. Working is not enough. This is three ordinary comparisons with a lecture. Preserve the *sentence* (“name the kind”) in a comment; do not preserve the binary.

---

## candidate-07 hits — KILL

### Execution

`./demo.sh` exit 0. `python3 -m unittest tests.test_hits -v`: 19 tests, OK.

Demo:

- hit → `file:line:text`, exit 0.
- miss → `0 matches`, exit 0, `&& echo still-running` ran.
- literal `n.edle` → `0 matches`; `--regex 'n.edle'` hit.
- bad regex `[` → stderr, exit 2.
- no args → usage, exit 1.
- mixed tree: binary with NUL skipped, text hit kept.
- `--glob '*.txt'` hit; `--glob '*.md'` miss still success.
- `chmod 000` temp dir → `unreadable directory`, exit 3.

Extra probe on real `lab-hdd/judges`:

```text
$ hits Skeptic lab-hdd/judges
…/ROLES.md:9:Roles: Unix, Toolsmith, Heretic, Skeptic, Reality-Stripped.
…/ROLES.md:15:Same five roles plus …
exit=0

$ hits xyzzy-no-such-token-brrr-judge lab-hdd/judges && echo still-running
0 matches
still-running

$ grep -R xyzzy-no-such-token-brrr-judge lab-hdd/judges; echo $?
# no output
grep_miss_exit=1

$ hits can_spend lab-hdd/scripts
r1_budget.py:67:def can_spend(...)
r1_budget.py:208:        ok, reason = can_spend(...)
```

I saw empty-success on a real miss, and grep’s exit 1 on the same miss. That is the entire delta.

### Dreamer vs demo

CANDIDATE is unusually honest: “Keep if `hits PAT && next` is something you would actually type instead of `grep … || true`. Kill if the only delta is exit 0.” I typed `&& echo still-running` because the demo told me to. I would not type this instead of `rg`. `0 matches` on **stdout** is a fake record in a pipe. Nested EACCES is skipped (exit 0), not exit 3 — listed under Failures, shown as root-DIR-only in the demo.

### Scores

- **Novelty 1.** GNU grep already uses 0 match / 1 no match / 2 error. This inverts 0/1 and splits usage/regex/IO. A status convention, not a new search.
- **Utility 2.** `set -e` pipelines that wanted “none is fine” already write `|| true` and keep a grep they know. I would not install a second grep to save `|| true` and then parse `0 matches` out of stdout.
- **Primitive strength 2.** Empty success is a policy. Distinguishing bad regex (2) from unreadable root (3) is real and I saw both. Nested unreadables collapsing into empty success weaken the policy.
- **Composability 2.** Aimed at `&&`. Miss writes a line to stdout, so `hits pat | wc -l` cannot mean “number of hits.” That is worse than grep’s silent miss.
- **Empirical credibility 5.** Demo, 19 tests, real tree, grep contrast, unreadable dir. The clone is well tested. That does not make it necessary.
- **Evolution potential 2.** Quiet empty, count on stderr. Still grep. `--glob` is fnmatch, not gitignore.
- **Reality-Stripped Strength 1.**

### Reality-stripped

Operation remaining: walk a tree, print `file:line:text` for substring/regex matches, or print `0 matches`; exit 0 unless usage / bad regex / unreadable root DIR.

Nearest ordinary workflow: `rg PATTERN DIR` or `grep -R`; `grep … || true` when absence is allowed.

Lost if replaced: almost nothing. `|| true` collapses miss and error; hits splits 2 vs 3. I did not need that split enough to keep a grep clone. Binary skip is what grep already does (and grep at least *says* “Binary file matches”; CANDIDATE’s own dogfood showed hits used to print a forged text line — they fixed the skip).

### Verdict

**KILL.** Execution is fine. The product is an inverted grep exit. CANDIDATE already wrote the kill condition; it holds.

---

## Skeptic notes (not averaged)

- **envfrom** and **whence** are the only two I would type tomorrow. Both produced an object on real input that `printenv` / `git merge-file` do not.
- **stated** and **owes** are KEEP for breeding: pair+UNKNOWN, leftover identifier. Both CANDIDATE stories overfit fixtures. Real input punished them (unparsed env values; companion self-hits on markdown that *describes* `MUST exist:`).
- **capdiff** is a named dump. KEEP the noun; I will not fight Unix for `diff -rq`.
- **same** and **hits** work. Working clones still die. Required identity kind is a lecture. Empty search success is `|| true`.
- Empirical 5 means I ran it and it matched, not that it should exist. hits and same have high E and a KILL. Do not average E with novelty.
- I did not see stated’s disagreement pair, owes’s companions-tied-to-a-change, or capdiff file-body replay, because those things did not happen. Low E where advertised.
- Multiple KEEP is satisfied: five KEEP, two KILL. Empty PATH slots are allowed; I am not minting seven binaries.
