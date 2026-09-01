# FINAL_EXTINCT — Extinctions Judge (judge-14)

Source: isolated worktree `subagent-01a01c4f-d862-7dc1-94b1-fd50a1dc5d4d`, branch `judge-14-final-extinct`. Clock window: 2026-08-20 08:20–08:40 JST. This judge did not author any lineage and did not rewrite a victim.

Mandate: **promising ideas that failed empirical testing**, for `EVOLUTION_REPORT.md` §5. Not the Kill Judge. Obvious junk (`pstree` with extra flags, a third leftover-name search, a fourth cinch) is out of scope. An idea earns a slot here only if it looked like a missing Unix verb, paid some rent (demo, dogfood, or first-selection keep), and then an experiment falsified the *claim*.

Axes used as a filter, not a scoreboard: Novelty of the *object*, Empirical credibility of the *killing run*. Utility of the surviving harvest is recorded so a later jury does not throw away the descendant with the corpse.

---

## Stance

Extinction is a claim dying under a named experiment. Three shapes:

| Shape | What died | Typical harvest |
| --- | --- | --- |
| **Product extinct** | The CLI / default walk / default producer | A sharper sibling (cusp, invert, ambit, cinch 0.3) |
| **Object extinct** | The interaction itself is empty or strictly worse | Nothing, or a different cluster (zanei/wraith vs haunt) |
| **Assumption extinct** | A load-bearing identity/proof/occupancy rule is a lie | Mutate-do-not-kill; later shoal/holt/shim/badge |

This night produced too many *join-history-to-the-living-tree* tools and too many walkers that own ignore policy. Several of those were still *good bets* at 01:00. The experiments below are why they are not products at 08:20.

I re-read author transcripts, first-selection judges, bakeoffs, and DESTROYER reports. I did not re-run the destroyer fixtures (they live under `/tmp/destroy-*` and are not in this worktree). Every killing command is cited from a harvested transcript with a path.

---

## 1. haunt — inverse dead-code lost the poster leftover

**Lineage.** candidate-05. Parent `./demo.sh` PASS (`lab/SHIPS.md`). First-selection: kill (Unix / Heretic / Toolsmith / Skeptic / GHOST_CLUSTER).

**Why it was promising.** Dead-code tools find living symbols with no references. The inverse — *names that died in history but the living tree still talks about* — is a real daily loop (`git log -S` + `rg`). Haunt packaged that join and split ARCHIVE (plans/ADRs) from HAUNT. On kizu v0.2 it still named leftover comments (`scope_incompatible` documented as current, absent from `src/`). The interaction is not conventional.

**Killing experiment.** skills `preact-zero-mock` is the cluster gold: the skill died at `127df9c`, README still advertises it.

v0.1 treated a deleted `SKILL.md` as a haunt of every remaining `SKILL.md`:

```
$ ./haunt -C …/skills --tsv -v
scanned 49 commits, 26 unique deaths
3 haunts, 23 dead, 0 moves
HAUNT  file  circuit-breaker/skills/circuit-breaker/SKILL.md   # false: basename SKILL.md
HAUNT  file  preact-zero-mock/SKILL.md                         # false: basename SKILL.md
HAUNT  file  circuit-breaker/scripts/init.sh                   # false: basename init.sh
```

v0.2 unique-basename matching *zeroed the repo*:

```
$ ./haunt -C …/skills -v
0 haunts, 0 archival, 26 dead, 0 moves
no haunts
```

The same tree, same night, **wraith** reports the leftover the cluster actually wanted:

```
$ ./wraith -C …/skills --ok-exit
wraith  1 name linger, 1 mention
preact-zero-mock
  died path  127df9c4  preact-zero-mock/SKILL.md  remove preact-zero-mock
  README.md:15  doc  | **preact-zero-mock** | …
```

**Why that kills the object, not just a filter.** The basename FP and the real leftover are the *same name*. Tightening identity until skills is silent throws away the only dogfood hit that distinguished haunt from `rg` of a name you already remember. What remains on kizu is leftover *comments* after a rename — wraith’s untyped-fringe hunt with a weaker filter. GHOST_CLUSTER Σ 21 vs wraith 23 is the critic spelling of the same result.

**Harvest.** One leftover-*name* survivor: **wraith** (parked, archaeology). Leftover *claims* are **zanei**. Occupancy of a still-true ghost name is **perch** (`TRUE 21 SKILL / TRUE 10 README+SKILL / TRUE 16 README only`). Do not revive haunt.

**Verdict.** **Object extinct.** Inverse-of-dead-code as a *name* join is strictly worse wraith.

Evidence: `lab/lineages/candidate-05__haunt/CANDIDATE.md`, `lab/lineages/candidate-12__wraith/CANDIDATE.md`, `lab/judges/GHOST_CLUSTER.md`.

---

## 2. folk — handshake table with an empty CI gate

**Lineage.** candidate-19. WAVE2 parent demo `author 0`. DISTINCT parked. Unix parked. Toolsmith parked. Heretic killed. Skeptic parked.

**Why it was promising.** RAII linters need *taught* pairs. Folk learned inverse-shaped call pairs from the repo (`beginConfiguration`/`commitConfiguration`, `set_var`/`remove_var`) with zero annotations and asked which paths broke them. sitbone’s camera session really does `beginConfiguration` / `commitConfiguration` on both the happy path and the `guard` failure path. That is a calling convention nobody wrote down. v0.1 found planted leaks on `fixtures/toy`. The object is sharp.

**Killing experiment.** Honesty filter vs the four dogfood trees.

v0.1 statistical collocation:

| repo | pairs | orphans |
| --- | ---: | ---: |
| sitbone/Sources | 6 | 4 |
| kizu/src | 66 | **714** |
| tenaoshi Engine+Shell | 81 | 240 |
| voidtrace | 89 | 915 |

Cross-language `lock`/`work` condemned Python `lock()`. SwiftUI `Text`/`font`/`padding` and commander/jest chains were “protocols.”

v0.2 (inverse-shaped only, language-scoped, generic inverses need same receiver + score ≥ 0.35):

| repo | pairs | orphans |
| --- | ---: | ---: |
| sitbone/Sources | **1** | **0** |
| kizu/src | **2** | **0** |
| tenaoshi / voidtrace / skills | 0 | **0** |

Toy still reports planted `forgotten_commit` / `leaked_lock` / `wrapped_orphan`. Real trees: the one sitbone pair is *honored* (both paths commit). kizu `set_var`/`remove_var` together=7 score=1.000; `push_back`/`pop_front` same_recv=3. Both honored.

**Why that kills the product.** A `--check` that is never red on the night’s own dogfood is not a linter. The honesty filter that made the table *true* also made the gate *empty*. Planted-fixture orphans are not rent. DISTINCT’s one-line park (“0 real orphans after honesty filter”) is the experiment.

**Harvest.** Keep the *idea* of a pinned `protocols.tsv` for a repo that actually has half-pairs. Do not spend another slot mining sitbone/kizu/voidtrace. **schism** (caller clusters by protocol halves) only after orphans exist in the wild.

**Verdict.** **Product extinct / object parked empty.** Not junk. Not PATH. Not a Gen-3 vehicle.

Evidence: `lab/lineages/candidate-19__folk/CANDIDATE.md`, `lab/judges/DISTINCT.md`.

---

## 3. nigh — string-distance firehose; the leftover column is the cut

**Lineage.** candidate-17. WAVE2 parent demo `author 0`. WAVE3: `nigh → cusp`. First-selection: nigh as default dies; **cusp** remains.

**Why it was promising.** The join *predicates ⋈ constructed vocabulary, with a metric* is not coverage, not mutation testing, not leftover-name search. Real hits survived the second dogfood:

- sitbone `CommandLine.arguments.contains("--auto-start")` — flag tested, never constructed.
- voidtrace `case "critical-tier.resolve-binary-roll"` — only occurrence in the repo; sibling family values *are* constructed. The arm is a fall-through.
- tenaoshi `http.statusCode == 401` against a produced `400` on the same field.

`--probe` inverts the join. TSV pipes it. That is a Unix column.

**Killing experiment (the NIGH class).**

v0.1 on voidtrace: JS template `${...}` desynced the lexer; `ENOENT` NIGH-matched `event` at d=2. kizu: Rust lifetimes parsed as strings (`impl < 'a> SelectState<'`) → 148 gates, 28 NIGH, 31 CLOSED.

v0.2 killed `ENOENT ↛ event` (first letter + shared prefix) and dropped lifetimes. voidtrace then: **849 gates, CLOSED=5, NIGH=0**. The string-edit class that justified the name `nigh` went to zero on the tree that had produced it. Remaining NIGH elsewhere is name-alias soup (`lib.py:3` ≈ `lib.py`, `has_more` ≈ `hasMore`) — aka/sic’s surface, different question, worse metric.

**cusp** (mutation-11) extracted the leftover *cut* column and dropped string-edit. v0.1 still drowned (tenaoshi 50 OFFBY of `0`/`1` soup). v0.2 same-field + drop `{0,1,2,-1}` vs `{0,1,2,-1}` left 401/400, `suffix(2)`, exclusive `3`. That is what nigh had actually discovered.

**Verdict.** **Product extinct.** Default nigh (CLOSED+NIGH+string distance) is a firehose. The surviving object is **cusp** (BRINK/OFFBY/SENTINEL/NEIGHBOR). Do not bring NIGH spelling back.

Evidence: `lab/lineages/candidate-17__nigh/CANDIDATE.md`, `lab/lineages/mutation-11__cusp/CANDIDATE.md`, `lab/WAVE3.md`, `lab/FIRST_SELECTION.md`.

---

## 4. unfmt walkers — inverse printf is real; `-C` is not the vehicle

**Lineage.** candidate-08 unfmt, candidate-13 unfmt (convergent), reimpl-01 stencil, mutation-02 sluice, mutation-15 invert. UNFMT_BAKEOFF ~01:50 JST.

**Why it was promising.** `rg 'user 42 not found'` is 0 hits on `user {uid} not found`. Two isolated inventors shipped the same primitive in Gen-1. Parent re-ran unfmt-08 **PASS 28/28** including real repos. sluice flipped the buried assumption (templates arrive on a stream, **PASS 40/40**). invert bound *names* and reported leftover prefix as a *span*. This is one of the night’s actual new verbs.

**Killing experiment (walkers as products).** Same pastes, four binaries. Battery = kizu hit + sitbone camera + 7-hole Logger + tenaoshi untracked + correct miss.

| Tool | Battery | What the experiment showed |
| --- | --- | --- |
| **invert** | 5/5 | Named holes, cleanest kizu rank, stream-shaped. **Vehicle.** |
| unfmt-13 | 5/5 | Named holes; **slowest walker**; noisier kizu rank. |
| **stencil** | 5/5 | Honest unfmt-08 reimpl; **camera fixed**; still anonymous; leaks `git {} failed`. Walker spare. |
| **unfmt-08** | **4/5** | **Camera miss** (nested Swift quotes). Cleanest *walker* rank on kizu. |

The camera paste:

```
$ ./unfmt -C sitbone 'camera presence enabled'
# unfmt-08: no template
# source: "camera presence \(self.isCameraEnabled ? "enabled" : "disabled", privacy: .public)"
# scanner terminated the string at the nested quote
```

stencil, rebuilt from *behavior only*, binds it. WAVE3 “stencil beats original on camera” is confirmed. unfmt-13 v0.2 also binds it (score 0.775) after a Swift-aware scanner — and is still a walker with a second ignore policy.

**Why that kills the walkers, not the primitive.** The object is instance → template. The *product* that owns `git ls-files` + skip-dirs is worse than `rg | invert`. invert’s leftover prefix is a **span** (`2026-08-19T23:50:01Z ERROR`, span=27-64); silently stripping the wrapper (sluice/unfmt) made `--exact` meaningless. Two walkers that agree 5/5 still disagree on rank and cost. Bakeoff: “Do not keep two walkers. If one-shot `-C` is needed, wrap invert’s kernel in an optional producer.”

**Harvest.** **invert** (then stump / lede / splice). stencil is the `-C` spare, not a second PATH entry. sluice is the anonymous kernel. moor is two objects in a trenchcoat (Heretic kill). Do not grow another ignore policy.

**Verdict.** **Products extinct** (unfmt-08, unfmt-13 as ships). **Object survived** as a filter.

Evidence: `lab/judges/UNFMT_BAKEOFF.md`, `lab/lineages/candidate-08__unfmt/CANDIDATE.md`, `lab/lineages/candidate-13__unfmt/CANDIDATE.md`, `lab/lineages/reimpl-01__stencil/CANDIDATE.md`.

---

## 5. cinch 0.2 — CLEAN-on-red is occupancy of nothing

**Lineage.** hybrid-03 cinch v0.2.0 @ `d7195b5`. DESTROYER_CINCH. LOCKSET_BAKEOFF vs cinch 0.3 (mutation-48) and snug (reimpl-06).

**Why it was promising.** Same dirty tree: winnow wheat = `print("debug")` **and** `return a + b`; cinch wheat = the return only. Tests stay at NEW. Predicate is pass/fail, not a command fingerprint. That is not `alibi | winnow`. Demo money shot survived every later attack. All three bakeoff binaries still drop the print and keep the return. The lockset is real.

**Killing experiment (CLEAN-on-red).** Production unchanged (`return a + b`). Dirty `test.py`: `assert add(2, 3) == 99`.

```
$ ./cinch -C $TEST_ONLY_RED --json -- python3 test.py   # 0.2.0
{
  "status": "CLEAN",
  "trials": 0,
  "production_units": 0,
  "held_tests": ["test.py"],
  "notes": ["no production source units differ from base; skipped test runs"],
  "new_run": null
}
# rc=0  elapsed=0.093s
```

The suite never ran. Zero production units skipped NEW. Occupancy of nothing, reported as clean, exit 0. CANDIDATE already named this; DESTROYER_CINCH §1 confirmed it; LOCKSET_BAKEOFF reproduced it on the rebuilt fixture (`HEAD ff37e16dfdec`).

cinch 0.3 and snug on the *same tree*:

```
status BROKEN  trials=1  notes: refusing to isolate while the new tree is already red
new_run exit_code=1  "assert add(2, 3) == 99"
# rc=3
```

**Sibling occupancy lie (same destroyer, same product).** FAST timeout `--timeout 0.5`: 0.2 (and snug) wheat = `FAST` + `VALUE`. Drop `FAST` and the assertion still passes in 8s. Timeout mapped to fail, so a speed hunk is wheat. 0.3 files FAST as `budget`; wheat patch is VALUE only. Honest / 4: 0.2 scores **2**, snug **3**, 0.3 **4**.

**Verdict.** **Product extinct.** Do not keep 0.2 as a ship. The lockset object survived as **cinch 0.3**. snug is the reimpl transcript, not a second kernel. Shared leftover holes (exit-5 = empty, `generated/` locks, nested git, `--max-trials` all-required) do not pick a vehicle.

Evidence: `lab/judges/DESTROYER_CINCH.md` §1, `lab/judges/LOCKSET_BAKEOFF.md` case 2, `lab/lineages/mutation-48__cinch/CANDIDATE.md`.

---

## 6. amid — spare, not the advertised stream

**Lineage.** mutation-35 amid vs mutation-35 ambit. AMBIT_AMID_BAKEOFF 2026-08-20 04:27 JST. Same object: **under as a file stream** (`rg | tool`). Same pipes on kizu `src/git/parse.rs`.

**Why it was promising.** `under` still walks a tree. Reviewers already have locators. `rg | amid` should expand each hit into the *file-local* path-condition, including fallthrough `given` lines that never mention the token. amid’s extra is real: `rg --json` always names the file, and peeling `if !P` means the locator can name the condition (`rg --json starts_with | amid --kind given` — no snippet). That is the more honest Unix stream.

**Killing experiment (the pipe people type).** Single-file `rg -n` omits the path (LINE:text). That is the `when` footgun. The mutation’s own default is `rg FILE | tool`.

```
$ cd kizu && rg -n 'return None;' src/git/parse.rs | ./amid --kind given 'a/' --explain
# rc=2
amid: locators are LINE:text with no file (rg FILE omits the name).
Pass the FILE, or use rg -nH / rg --json.
```

```
$ cd kizu && rg -n 'return None;' src/git/parse.rs | ./ambit --kind given 'a/' --explain
# rc=0
…/kizu/src/git/parse.rs:59-60
  given  bytes.starts_with(b"a/")  (L51)←
  here   let b_side = …
```

rg never printed L60. Only ambit absorbs LINE:text: `(line, text)` pins against `git ls-files` and scans if unique. From `kizu/` the advertised pipe is the invert of `when parse.rs:60`.

Battery (3 named pipes): **ambit 2/3**, **amid 1/3**. amid wins JSON+peel; refuses LINE:text; `--repo` unused for pin recovery. Inherited `_payload_score` still ties `}` with the payload — `here }` vs ambit’s `here Some(bytes_to_path(a_side))`.

**Verdict.** **Default producer extinct.** Carry **ambit**. Keep amid as the json/derive spare. Do not implement a third clone. Do not graft json+peel onto ambit in the same slot; that is a flag, not a sibling binary.

Evidence: `lab/judges/AMBIT_AMID_BAKEOFF.md`, `lab/lineages/mutation-35__amid/CANDIDATE.md`.

---

## 7. Lethal DESTROYER holes (assumption extinct)

These four are not “kill the tool.” DESTROYER verdicts were **mutate, do not kill**. The *load-bearing claim* each sold is dead. Later mutations (shoal, holt, shim, badge) are descendants, not proof the ancestor claim survived.

### 7.1 keel — `git remote add` is `--any-repo`

**Claim that died.** A keel token’s repo identity is **normalized remotes ∩ + tip witnesses**, not `rev-list --max-parents=0 --all`. A depth-1 clone of the same project should resolve; a stranger should fail-close unless `--any-repo`. Bought: kizu `src/app.rs:529@b4e6a5d → src/app/layout.rs:17` on full clone **and** on `git clone --depth 1 file://$KIZU`. Foreign git *roots* still exit 1. Orphan extra roots are not a different repository.

**Killing experiment.** Foreign `other/util` with the same `helper_keep` line. Token `keel1:r:github.com/keel-lab/ugly;w:…`. Root resolve without `--any-repo` is the bought refuse (`rc=1`, different repository). Then:

```
$ git -C $FOREIGN remote add extra git@github.com:keel-lab/ugly.git
$ ./keel resolve --repo $FOREIGN --to HEAD --porcelain "$HELPER"
moved	-	src/calc.py:4	pkg/util.py:1	1.000
# rc=0
```

No fetch. Intersection does not require dest to have fetched the pin, to share objects, or to be a fork. A stranger who can edit `.git/config` is the project. `git remote set-url origin https://github.com/keel-lab/ugly.git` is the same landing. Remotes ∩ short-circuits witnesses.

**Sibling (same destroyer, also lethal).** `git fetch $UGLY 4dcf37ca7282f41b` then `object_exists` lands the helper with remotes still `other/util`. kizu steal: copy `layout.rs` + fetch HEAD → `moved src/app.rs:529 → src/app/layout.rs:17 1.000` on a stranger. Spoof only the remote, no `layout.rs`: origin check **still passes**, then `deleted` rc=0 — the refuse never ran.

**What is extinct.** “Remotes ∩ is proof of project.” “Witness occupancy (`cat-file -e`) is identity.” Missing `o` / gitless `--to-dir` as a silent global locator.

**Harvest.** **shoal** (mutation-110): origin is *signed remotes at mint* + required witnesses; extra remotes are not walked. Fork-PR CI (`alice/ugly` shallow of a later tip) still has no verb that is not `--any-repo`.

Evidence: `lab/judges/DESTROYER_KEEL.md` §1–§2, `lab/lineages/mutation-110__shoal/CANDIDATE.md`.

### 7.2 berth — first-parent “either name” is a lie

**Claim that died.** `berth --follow` occupies a **file identity**. A recorded rename is one roost. Query the old name or the new name; occupancy stays TRUE and holders still split. `--full` still stitches kizu `R100 deep-research-ai-agent-hooks.md → docs/…` as one **187-commit** roost from either name. Copy / C056 leftover blob is not a follow. sitbone FocusRiverView island and skills `preact-zero-mock` ghost still hold.

**Killing experiment.** The first real-repo rename is `4e37f16` `R100 deep-research-ai-agent-hooks.md → docs/…`. The merge first-parent sees (`ca0577a`) adds dest as **A**, not R.

```
$ ./berth exists docs/deep-research-ai-agent-hooks.md
FALSE   3 / TRUE 21
       origin: 321a830  … as deep-research-ai-agent-hooks.md
aka=docs/deep-research-ai-agent-hooks.md
# dest-only. old name not in aka.

$ ./berth exists deep-research-ai-agent-hooks.md
FALSE  24 commits
now=FALSE  true=0/24  never=1
hint: never held on first-parent, but existed in 13 reachable
      commits off the mainline. rerun with --full
```

`--follow` and `--no-follow` on the dead name produce the same first-parent lie. `git log --follow -- deep-research-ai-agent-hooks.md` still names `4e37f16`. Synthetic non-ff merge is the same object. `--full` on that fixture **invents deaths** (list order ≠ merge lattice): `FTFTFT`.

**Sibling (same destroyer, load-bearing).** Default `exists` seeds from the *first* `cat-file` hit of the query path, then walks R forward. After `git mv old.txt new.txt` + recreate `old.txt`, `exists old.txt` occupies **new.txt**. After a serialized name-swap, `exists a.txt` occupies the file that now lives at `b.txt`. The living name is the wrong handle for its occupant.

**What is extinct.** “Query either name on the default walk.” Default first-parent `exists` is dest-only occupancy plus a `--full` hint, or the wrong roost at a leftover name.

**Harvest.** **rove** already resolved identity from all-reachable R for `grep -- PATH`. **holt** (mutation-104) made all-reachable R the *default* for `exists` and seeded from the tip occupant. `--full` lattice flicker is still DESTROYER_OCCUPANCY’s lie, now after a successful R stitch.

Evidence: `lab/judges/DESTROYER_BERTH.md` §3 and §8, `lab/lineages/mutation-104__holt/CANDIDATE.md`.

### 7.3 xref — `*getenv` suffix is not a getenv proof

**Claim that died.** DUE is a `getenv` / `env::var` *call site* that uses this name. xref already killed assay’s 12,596 LLVM-opcode flood (sysroot rustc is 44 names, due=38). Direct `getenv("DIRECT_ENV_NAME")` is still DUE. Orphan cstrings are still not DUE by default. Homebrew libpython still prints `PYTHON_GIL DUE` / `PYTHONHOME LATENT`. `/bin/ls` is `CLICOLOR_FORCE`, not the `COLOR_FORCE` peel. That is not `strings(1)`.

**Killing experiment.** `getenv_sym_kind`: `n.endswith("getenv")` or `"3env3var" in name`.

```c
char *not_a_getenv(const char *n) { puts(n); return 0; }
void forgetenv(const char *n) { (void)n; }
/* main: not_a_getenv("FALSE_DUE_NAME"); forgetenv("FORGET_ENV_NAME"); */
```

```
$ nm bins/false-O0 | grep getenv
0000000100000460 T _not_a_getenv
0000000100000490 T _forgetenv
$ otool -tv bins/false-O0   # _main
bl _not_a_getenv     ; x0 = "FALSE_DUE_NAME"
bl _forgetenv        ; x0 = "FORGET_ENV_NAME"
# no bl _getenv

$ ./xref --app bins/false-O0
DUE  FALSE_DUE_NAME   call  getenv
DUE  FORGET_ENV_NAME  call  getenv
```

`--calls` *labels* `getenv`. KIND is DUE. libc `getenv` is never called. `-O2` without `noinline` inlines `puts` and the lie disappears; `-O0` / `-fno-inline` is the object the symbol table actually contains. Same heuristic: `getenv_sym_kind("foo3env3variable") == "env::var"`.

**Inductive hole.** DUE is “a call to something *named* getenv,” not “a call to getenv.”

**Siblings (same column).** One-hop `_env_to_dict(&key[4])` / `mov x0, x3`: Homebrew `PYTHONHOME` is LATENT (real getenv, documented-only badge). `kind_of` else-DUE: `--loose` orphans print as DUE (`BITSET_CANONICAL`, `DATA_CONST`). `--vs-program` needles are occupancy of bytes with KIND copied from the source extractor. Fat Mach-O DUE is a proof of the *native slice*, not the image.

**Harvest.** **shim** (mutation-108): allowlist (`getenv` / `secure_getenv` / `_Py_GETENV` / rust `__var`), not `endswith`. rustup/xcselect print `shim`, not the same `(no owed names)` as `int main(){return 0;}`. lash still owns the one-hop wrapper. wad still owns inlined Rust `CString`.

Evidence: `lab/judges/DESTROYER_XREF.md` §1–§3, `lab/lineages/mutation-108__shim/CANDIDATE.md`.

### 7.4 maiden — never-red is a parser × string id

**Claim that died.** The never-red set is “this *test* has never been red.” Gold 2019-fail + 2024-green still names `pkg.T::alpha` **SCARRED** and `--skeptic`; `--latest` still maidens it. sitbone `swift test list` is **213 UNKNOWN**, kizu `cargo --list` is **489 UNKNOWN**. SKIP-only is not maiden. That is not `rg PASS` and not alibi.

**Killing experiment (rename).** Same body, new spelling:

```
$ ./maiden --no-ledger --header rename-fail.xml rename-pass.xml
SCARRED  pkg.T::compute_diff              # failed 2019
MAIDEN   pkg.T::compute_operation_diff    # born green 2024
# --skeptic  SKEPTIC 0
```

Classname move is the same split (`pkg.Old::alpha` SCARRED, `pkg.New::alpha` MAIDEN). The test was red. The new string has never been red. kizu’s live identity `app::tests::compute_operation_diff_empty_when_identical` is this spelling. A module split is a new maiden column unless the ledger is rewritten.

**Siblings (same destroyer, same lie).**

- Surefire `<flakyFailure>` / `<rerunFailure>` / `status="failed"` with no child → **MAIDEN**. The file says the test failed, then passed. `--check MAIDEN` fires as if it had never been red.
- Unrecognized fail (`--- FAIL: TestAlpha`, bun `✗`, nextest FAIL) → `{}`. Then a cargo-looking `test TestAlpha ... ok` **maidens** the go fail. Occupancy of nothing, then a recognized pass of the same string.
- `--census` ∩ runner list is **0/489** (kizu) and **0/213** (sitbone). Green run maidens an ORPHAN. `--latest --skeptic` deletes the fail (`SKEPTIC 0`).
- Ledger `"status":"red"` is not in STATUS_MAP → fail dropped, pass remains, MAIDEN.

**What is extinct.** “This test has never been red.” What survived is “this *canonical string* has no *parsed* fail in the fold.”

**Harvest.** **badge** (candidate-43): key is `(suite, class, method)` across rename/alias; `<flakyFailure>` is red; `--latest --skeptic` exits 2. Unrecognized dialect as a silent empty that a later cargo pass can launder is still open unless badge refuse-closes it.

Evidence: `lab/judges/DESTROYER_MAIDEN.md` §4 and §6, `lab/lineages/candidate-43__badge/CANDIDATE.md`.

---

## Compact ledger

| Idea | Promising claim | Killing experiment | What died | What remains |
| --- | --- | --- | --- | --- |
| **haunt** | inverse dead-code: dead names still speaking | skills v0.2 → 0 haunts; wraith still has `preact-zero-mock` @ README:15 | the name-join object | wraith (names), zanei (claims), perch (ghost tenure) |
| **folk** | unwritten call-pair orphans as a CI gate | honesty filter: sitbone 0, kizu 0, tenaoshi/voidtrace/skills 0 orphans | the product / `--check` | parked table; `protocols.tsv` only if orphans appear |
| **nigh** | string-edit NIGH of literals vs cuts | voidtrace v0.2: 849 gates, NIGH=0; `ENOENT`≈`event` was the class | default nigh | **cusp** (cut, not spelling) |
| **unfmt-08/13** | inverse printf as a *tree walk* | bakeoff 4/5 (camera miss) / slow noisy 5/5; invert 5/5 stream | walker products | **invert** + stencil spare |
| **cinch 0.2** | lockset occupancy, including “no prod ⇒ CLEAN” | test-only red: CLEAN rc=0, suite never ran | 0.2 as a ship | **cinch 0.3** (NEW always; timeout=unknown) |
| **amid** | `rg FILE \| amid` is the under-stream | LINE:text `rc=2`; ambit 2/3 vs amid 1/3 | default producer | **ambit**; amid json/derive spare |
| **keel remotes** | remotes ∩ is the project | `git remote add extra victim.git` lands stranger @ 1.000 | remotes-as-identity | **shoal** (signed remotes at mint) |
| **berth FP** | either name, default walk, one roost | kizu dead name `exists` never-held; dest-only aka | default first-parent claim | **holt** (all-reachable R + tip seed) |
| **xref DUE** | DUE is a getenv *use* | `not_a_getenv` / `forgetenv` → DUE; no `bl _getenv` | suffix-as-proof | **shim** allowlist; lash/wad hops |
| **maiden id** | never-red of a *test* | rename maidens the new spelling; `<flakyFailure>` MAIDEN | string-id axiom | **badge** (suite/class/method) |

---

## What this judge is not extinguishing

These failed *some* test and are still not this report:

- **winnow / glean** — Heretic kills them as 1970s ddmin. Skeptic/Toolsmith keep them because the *substrate* (uncommitted hunks) is not `git bisect`. Utility disagreement, not an empirical empty.
- **pin leftover-stub / 1.000-twice** — DESTROYER_PIN_INVERT conceptual holes; unique kizu tokens still do not hallucinate onto voidtrace. Mutate. Not an extinction of the token.
- **due / lode / orbit** — Homebrew `python3` stub printed 0 names (payload is libpython). That *is* an empirical miss of due-as-PATH-binary, and lode/xref/assay already flipped the image. Conventional-cousin debate belongs to Kill / Skeptic, not here, except as the ancestor of xref’s DUE claim.
- **akin similarity / once** — 0 exact-blob kin on kizu/sitbone/voidtrace/tenaoshi. Right death of simultaneous-blob, wrong next oracle (SequenceMatcher). Adjacent, thinner than the assigned list; park `--port` only.
- **moor / pinch∥hitch / kiln∥clutch** — composition / duplicate-vehicle kills. Not “looked promising, then a fixture lied.”
- **Generated/`<module>`/exit-5 on cinch 0.3** — still open, shared, not a reason 0.3 is extinct.

If a later jury needs one sentence for §5:

> Haunt lost `preact-zero-mock` by tightening identity; folk’s honesty filter emptied the gate; nigh’s NIGH class went to zero on voidtrace; unfmt walkers lost the camera paste and the stream bakeoff; cinch 0.2 called a red suite CLEAN; amid refused the `rg` people type; keel treated `git remote add` as identity; berth’s default walk broke “either name”; xref DUE’d `*getenv`; maiden maidened a renamed spelling and a `<flakyFailure>`.

---

## Evidence of independence

Read, not rubber-stamped: `lab/judges/{GHOST_CLUSTER,DISTINCT,UNFMT_BAKEOFF,AMBIT_AMID_BAKEOFF,LOCKSET_BAKEOFF,DESTROYER_CINCH,DESTROYER_KEEL,DESTROYER_BERTH,DESTROYER_XREF,DESTROYER_MAIDEN,FIRST_*}.md`, author `CANDIDATE.md` for haunt/folk/nigh/unfmt-08/unfmt-13/stencil/cusp/amid/cinch-0.2/cinch-0.3/shoal/holt/shim/badge, plus `lab/{FIRST_SELECTION,WAVE2,WAVE3,SHIPS,STATUS}.md`.

Did **not** re-execute `/tmp/destroy-*` or `/tmp/lockset-bakeoff` in this worktree. Those transcripts are the experiment of record.

Did **not** kill anything because it was conventional, unpolished, or a Heretic-novelty miss. Those are other judges.

Canonical copy: `lab/judges/FINAL_EXTINCT.md`.
