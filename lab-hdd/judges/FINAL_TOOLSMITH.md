# FINAL_TOOLSMITH

Role: Toolsmith. Question: **what would a real developer use repeatedly?**
Not polish. Not origin story. Not other judges.

Ran every `./demo.sh` and the shipped tests, then pointed the CLIs at trees that were not the happy fixture.

## Verdict

**KEEP**

- `gen3-02__envfrom-dir` (`envfrom`)
- `gen3-03__stated-honest` (`stated`)
- `gen3-04__effect-compact` (`effect`)
- `gen3-01__whence-empty` (`whence`)

**KILL**

- `mutation-02__owes-strict` (`owes`)
- `mutation-04__capdiff-json` (`capdiff`)

Multiple survivors. Two objects I would not put on a PATH, ever.

## Tomorrow install

Deliberately small. Third slot empty on purpose.

| slot | tool | from |
|------|------|------|
| 1 | `envfrom` | `lab-hdd/lineages/gen3-02__envfrom-dir/envfrom` |
| 2 | `stated` | `lab-hdd/lineages/gen3-03__stated-honest/stated` |
| 3 | — | empty |

I would copy those two into `~/bin` tomorrow as `envfrom` and `stated`. I would **not** PATH `effect`, `whence`, `owes`, or `capdiff` this week.

- `effect` stays KEEP: the deferred-name join is real, and concatenating `stated` then `envfrom` loses it. I still will not install three overlapping scanners on day one. If next month I keep running both halves, I replace `stated` with `effect`.
- `whence` stays KEEP: per-span parentage is a primitive git does not have. zsh already owns the name `whence` (builtin). I would invoke it as `python3 whence` or `git-whence` on the next ugly merge, not as a PATH verb tomorrow.

## Execution (this sitting)

| lineage | `./demo.sh` | tests |
|---------|-------------|-------|
| gen3-01 whence-empty | 0 | 31 OK |
| gen3-02 envfrom-dir | 0 | 31 OK |
| gen3-03 stated-honest | 0 | 22 OK |
| gen3-04 effect-compact | 0 | 18 OK |
| mutation-02 owes-strict | 0 | 14 OK |
| mutation-04 capdiff-json | 0 | 21 OK |

Extra probes (not the demo):

- `stated` + `envfrom` on `effect`'s `fixtures/deferred` vs `effect timeout` on the same tree.
- `stated MAX_FILES` on the shipped `capdiff` file (no `.py` suffix).
- `owes --tree` on its own lineage plus a real `git diff`.
- `capdiff capture` of envfrom's `quoted-export` fixture; compared parsed `COLOR` to `envfrom COLOR`.
- `envfrom --json --run` on the empty-override fixture (stdout mix).
- `type whence` in zsh.

## Scores (0–5)

Toolsmith weights **Utility** and **Composability**. Other axes still scored. Not an average with anyone else.

| candidate | Nov | Util | Prim | Comp | Emp | Evo | Real | call |
|-----------|-----|------|------|------|-----|-----|------|------|
| envfrom | 3 | 5 | 4 | 5 | 5 | 4 | 4 | KEEP |
| stated | 3 | 4 | 4 | 4 | 5 | 3 | 4 | KEEP |
| effect | 4 | 4 | 3 | 4 | 5 | 4 | 4 | KEEP |
| whence | 4 | 3 | 5 | 4 | 5 | 3 | 4 | KEEP |
| owes | 2 | 1 | 2 | 3 | 4 | 2 | 2 | KILL |
| capdiff | 2 | 2 | 2 | 3 | 4 | 3 | 2 | KILL |

---

## gen3-02__envfrom-dir — KEEP (install tomorrow)

**Novelty 3.** `printenv` prints the live map. `grep .env` prints a line. Nobody joins them with `file:path:line`, an empty-override flag, and the inherited value the file would wipe.

**Utility 5.** This is the weekly tool. I have spent real mornings on "why is `LIBRARY_PATH` empty." Demo: `.env` line 2 is `LIBRARY_PATH=`, process still has `/usr/local/lib:/usr/lib`, output is `EMPTY_OVERRIDE: yes` plus `INHERITED: …`. `--fail-empty` exits 2. `--run --load` actually blanks the child. `--dir` reads that tree, not cwd. Missing dir exits 1 instead of lying `SOURCE: env`. That is the motion I already do by eye, finished.

**Primitive 4.** The object is **source of an effective value** (`env` / `file:…:N` / `unset`), not a prettier `env`. Last-wins `.env` then `.env.local` is the right default.

**Composability 5.** `--json` is a real array I piped into Python: `[('LIBRARY_PATH', True, 'file'), ('APP_ENV', False, 'file')]`. `--fail-empty` is a CI gate. `--dir` is how I inspect another checkout without `cd`. `--run --load` is one-shot direnv. Known hole I can live with: `--json --run` concatenates the JSON document and the child on stdout (I truncated it; `CHILD_OK` sits on the same stream). I would not combine those flags.

**Empirical 5.** Demo + 31 tests + missing-dir / BOM / invalid-UTF8 probes all behaved. Invalid UTF-8 is a one-line error, no traceback.

**Evolution 4.** Source chain when both dotenv files set the same key; stop mixing `--json` with child stdout. Do not add interpolation until the empty-override record is boring.

**Reality-stripped 4.** Drop the origin story and it is still: name a key, see whether a file emptied it.

Install: `chmod +x` and drop on PATH. Name is rememberable. No zsh collision.

---

## gen3-03__stated-honest — KEEP (install tomorrow)

**Novelty 3.** I already `rg timeout`. The extra is the **disagreement pair** (declaration site vs contradicting assignment) with comments, docstrings, and quoted mentions out of the comparison.

**Utility 4.** I would type `stated timeout .` inside a service directory. Demo disagreement is the paste I want in a PR:

```
status: DISAGREE
disagreement:
  declared     5    config.yaml:1  timeout: 5
  contradicted 10   app.py:3       timeout = 10
```

exit 2. Agree / declared-only / unknown exit 0. Compact `{"timeout": 5}` is a declaration. `.env TIMEOUT=30` is **not** — `stated TIMEOUT` on that tree is `NONE`. `msg = "timeout = 99 is wrong"` is **not** an assignment (DECLARED_ONLY 5). Those honesty cuts are why I would trust it after one week; a false assignment from a string would have been an uninstall.

Limits I actually hit: pointed `stated MAX_FILES` at `mutation-04__capdiff-json` → `NONE`. The assignment is `MAX_FILES = 5000` in an extensionless `capdiff` file. Copied to `capdiff.py` → `ASSIGNED_ONLY 5000`. So this scanner does not see the way these CLIs are shipped. Fine for a normal `*.py` service. Also: pointed `stated timeout` at the whole stated lineage and got a 32-pair cartesian product across fixtures. Operator error (run it on one app), but it will bite a monorepo root.

**Primitive 4.** The pair is the product. Not a hit list. Exit 2 only when comparable scalars disagree.

**Composability 4.** `--json` is the pair as data. Exit codes are CI-shaped. No `--dir` flag because DIR is positional; that is fine.

**Empirical 5.** Demo + 22 tests. String-literal and dotenv cuts are in the shipped tests, not just README.

**Evolution 3.** Nested keys (`server.timeout`) and extensionless scripts are the next real holes. Case-insensitive env names are effect's job, not this one.

**Reality-stripped 4.** "Where is KEY declared, and does source assign a different literal?" survives without HDD lore.

Why this gets the PATH slot instead of `effect`: I already have `envfrom` for the env layer. `stated`'s headline **is** the pair I paste. `effect` is a dashboard whose name I would forget.

---

## gen3-04__effect-compact — KEEP (not tomorrow)

**Novelty 4.** This is the one object that is not `stated KEY; envfrom KEY`. I ran the kill test.

`stated timeout fixtures/deferred` → `UNKNOWN`, `${WAIT}` vs `os.getenv("WAIT")`.
`envfrom WAIT timeout TIMEOUT` → `WAIT` is file value 10, `timeout`/`TIMEOUT` unset. You have to already know to ask for `WAIT`.
`effect timeout` with `WAIT=from-shell` → ENV_SOURCE `WAIT file:.env:1 value=10 why=deferred`, EFFECTIVE `10`.

Concatenation never pulls `WAIT` into the timeout record. That is the join.

**Utility 4.** The 2am question is "what would this key actually be." Four fields (DECLARED / ASSIGNED / ENV_SOURCE / EFFECTIVE) answer it. Compact JSON miss is closed: `{"timeout": 5}` vs `timeout = 10` is EFFECTIVE unknown, exit 2, not a false assigned-only 10. On `dotenv_not_decl`, dotenv stays in ENV_SOURCE (`timeout=99`, `TIMEOUT=30`) and exit 2 is still yaml 5 vs py 10.

Why it is not on PATH tomorrow: I will not install `stated` and `effect` the same morning. The name `effect` is generic. EFFECTIVE is often `unknown` (honest, but then I am reading the same pair `stated` already prints, plus env). `--run` / `--fail-empty` live on `envfrom`, not here.

**Primitive 3.** It is a join, and it says so. The new bit is deferred-name env lookup riding in the same record. Keep it for that, not because it has more flags.

**Composability 4.** `--json` is one object (`declared`, `assigned`, `env_source`, `deferred`, `effective`, `disagree`). Exit 2 only on declared-literal vs assigned-literal, same as `stated`, so I can still gate CI without treating env disagreement as a hard fail.

**Empirical 5.** Demo + 18 tests. Concatenation kill test reproduced here, not quoted from a log.

**Evolution 4.** Silent 2MiB skip still lies about EFFECTIVE. `os.getenv("X", "5")` static default. Dotenv decode should match envfrom (BOM / invalid UTF-8). Those are mutations I would want if I installed it.

**Reality-stripped 4.** Strip the hybrid story and the four-field record is still the product.

---

## gen3-01__whence-empty — KEEP (not tomorrow)

**Novelty 4.** `git checkout --ours` / `git merge-file` write a blob and forget which parent supplied each contested token. `whence resolve --hybrid` keeps that parentage as JSON next to the text. Tagged sidecar `[ours:color = red] size = [theirs:2]` is a small language, not a TUI.

**Utility 3.** I do not resolve conflicts every day. When I do, I usually use the editor. I **would** use this on a generated-file / lockfile / config hybrid, and I would keep the `.prov` sidecar when someone later asks "who picked `size = 2`." Empty hybrid (stdin, whitespace-only pipe, 0-byte sidecar) now exits 3 and **leaves the markers**. `FILE=-` without `--output` exits 3 and does not create a file named `-`. Those are trust fixes. They are why I would keep the binary around, not why I would PATH it tomorrow.

zsh: `whence is a shell builtin`. Installing this as `whence` on a zsh machine is a footgun. Demo and README already say `./whence` / `python3 whence`. Tomorrow PATH wants a name I can type; this one is taken.

**Primitive 5.** Explicit parent choice + per-span provenance is the strongest primitive on the table. Untagged mix is refused. diff3 `|||||||` is refused (two parents only). Wrong-parent tag names the other parent. Short sidecar lists the missing region. That is a tool, not a wrapper around `git merge-file`.

**Composability 4.** Provenance JSON on stdout; `--prov -` skips the sidecar; `--hybrid -` takes a pipe; stdin FILE requires `--output`. I could hang this off a mergetool later. Not hung today.

**Empirical 5.** Demo covers ours/theirs/hybrid file/hybrid stdin/BOM/empty/dash-file/dual-stdin/untagged/diff3/real `git merge`/messy three-region. 31 tests OK. I watched empty sidecar exit 3 with markers still in the file.

**Evolution 3.** Mergetool driver, unique-vs-shared span, BOM on the conflict FILE, transactional dest. Without mergetool wiring this stays a specialist.

**Reality-stripped 4.** "Resolve markers only by named parent, record which parent kept each span, refuse empty hybrid" does not need a trial name.

---

## mutation-02__owes-strict — KILL

**Novelty 2.** Minus-line identifiers still mentioned in the tree is `git diff` plus `rg`. Companions are a closed phrase set (`MUST exist: PATH`, `required file: PATH`). After the strict cut, incidental backticks no longer fire — I reproduced `fixtures/prose-backticks` exit 0. That is a fix of a landmine, not a new verb.

**Utility 1.** I would not use this repeatedly.

1. Deleted `validate_input` still in README: I already `rg validate_input` after deleting a function. Tests fail if a call site remains. Docs going stale is a review item, not a weekly CLI.
2. Companions only fire if the team adopts those two phrases. No repo I actually work in writes `MUST exist:`. Adopting the dialect to feed the linter is a tax.
3. Dogfood on the lineage itself: `owes --tree mutation-02__owes-strict --diff <HEAD~3>` reports missing companions `PATH`, `SECURITY.decision.md`, `docs/threat-model.md`, `util.py` — mostly from **documenting the phrase** in README/CANDIDATE.md. A tool that cannot scan its own tree without treating its docs as obligations is a tool I will not run on a real repo.
4. Companion scan does not consult the diff. Missing companions are true of the remaining tree, not of this change. That is a tree linter pretending to be a change linter.
5. Snapshot layout (`DIR/tree` + `DIR/change.diff`, or `before/`/`after/`) is friction versus reading `git diff` in a repo. Pointing it at the repo root is a usage error.

**Primitive 2.** Two weak scanners glued. Strict companions made it honest and smaller. Smaller is not enough.

**Composability 3.** `--json` and `--tree/--diff` are fine. Exit 2 on any obligation is fine. I still would not put it in a pre-commit.

**Empirical 4.** Demo + 14 tests pass. The self-hit is also empirical, and it is why I kill it.

**Evolution 2.** Skip identifiers that still have a definition; bind companions to touched files. Even then I would not install it. The remaining work is "become a worse Semgrep."

**Reality-stripped 2.** Without the HDD-agent story it is grep-for-deleted-names plus a phrase linter for a dialect you must invent.

KILL. Not on the install list. Not in the toolbox.

---

## mutation-04__capdiff-json — KILL

**Novelty 2.** Named `{.env map, file hashes}` you can diff later. `diff -ru` two directories, `sha256sum`, and `env` already cover the pieces. The label is the extra. `--json` is an encoding of the same six buckets.

**Utility 2.** I would not start a capture/replay practice.

- Files: I have git. Capture does not store bodies; `--files` restores only `.env`. Honest, and therefore not a restore tool.
- Env: I `diff` two `.env` files, or `direnv`, or `set -a; source .env`. Replay overlays captured keys and does **not** unset host keys missing from the capture. Empty env map means "add nothing."
- Store: `.capdiff/NAME/` in cwd is another cache to gitignore.

`--json` is the mutation. I ran `diff a b --json`: objects for modified/extra/missing, empty arrays not `(none)`, `API_KEY` not glued as `KEY=value`. That is a correct encoder. It is not a reason to install the tool.

Parser is weaker than the envfrom I **would** install. Captured envfrom's `quoted-export` fixture: envfrom reports `COLOR=red` (inline comment stripped); capdiff's manifest stores `COLOR` as `red # inline comment`. I will not maintain two dotenv parsers.

**Primitive 2.** Labeled dump + set-diff. Replay is `exec` with overlay. No new question.

**Composability 3.** `--json` is scriptable. `capture` / `diff` / `replay` is a closed loop that does not compose with `envfrom`'s record.

**Empirical 4.** Demo + 21 tests OK. Identical JSON is six empty arrays, exit 0. Parser drift versus envfrom is also a real run.

**Evolution 3.** `--env-only`, globs, `env -i` replay, capture from `os.environ`. That is a bigger product I still would not adopt over direnv + git.

**Reality-stripped 2.** "Snapshot .env and hashes, diff names, overlay env" is a script, not a verb I would type.

KILL. JSON did not save it.

---

## What I would actually type next week

```bash
envfrom LIBRARY_PATH
envfrom --dir other-checkout --fail-empty LIBRARY_PATH
stated timeout .
stated --json timeout .  # paste into a ticket
```

When those two leave me with `UNKNOWN` interpolations:

```bash
effect timeout .
```

That last one is why `effect` is KEEP and not installed tomorrow.

When I am staring at conflict markers I cannot hybrid in the editor:

```bash
python3 whence resolve FILE --hybrid sidecar.txt
```

Not `whence`, because zsh.

I would not type `owes` or `capdiff`.

## After origin (hidden until now)

These origins did not change the calls: envfrom/stated/effect/whence came from env/debug/hybrid/merge trials; owes and capdiff from agent/ci. The weekly motions I already have are env provenance and config-vs-code drift. Merge parentage is rare and real. "Obligations a change appears to break" and "named CI captures" are stories I do not live.
