# FINAL_COMPOSER — 08:20 JST final jury

Composer judge. Isolated worktree. Values: **pipes**. Which survivors compose (`rg | X`, `git diff | X`, `X | git apply`)? Which are monoliths wearing a CLI? Which “hybrids” exist only because the naive pipe was a lie?

Axes of record: **Composability** (C) and **Unix-shaped vs app-shaped**. Other axes only where they change a keep/park. Integer 0–5. A 4+ on Empirical requires a run this session or a cited destroyer transcript, not a README. Several survivors. No single winner. Haunt stays dead. Folk stays parked. No third ambit. No fourth cinch. No leftover-name search. No inverse-printf walker.

Assigned destroyers: `DESTROYER_PEAL`, `DESTROYER_WEFT`, `DESTROYER_WELD`, `DESTROYER_BECK`. Assigned lineages: ambit/peal/seed, weft/woof/tally, weld/stile/solder, plait/hank/quire/braid/tilde, ditto/pup/crib. Other survivors appear only as producers, consumers, or counterexamples.

Evidence tags:

- **PARENT** — this judge re-ran the binary on kizu / sitbone / tenaoshi / fixtures, 2026-08-20.
- **DESTROYER** — cited adversarial pass, victim unpatched.
- **AUTHOR** — lineage `CANDIDATE.md` / `demo.sh` only.
- **UNVERIFIED** — not re-run here.

---

## Stance

Unix-shaped means four things at once:

1. **The object is on stdin or stdout**, not behind a flag that happens to read a file.
2. **Exit 0/1/2 is the conversation** (found / miss-or-leak / usage). Human pretty-print is a tty extra.
3. **It refuses to walk when a producer already exists.** `rg` picks files. `git diff` is the patch. `gh api` is the comment stream. Directories on `--templates` exit 2.
4. **It does not absorb a sibling object to hide a hole.** Leftover `\nDone.` is rime, not a weld flag. `--forbid number` is snag, not weft. JSON field-cover is facet, not beck.

App-shaped means the tool owns the tree, the ignore policy, the test runner, the LSP, the GitHub session, or the process tree. Those can still be *good*. They are not filters. Pretending `cinch -- pytest` is `rg | X` is how you grow a platform.

A hybrid that **refused to pipe** because concatenating the CLIs answers a different question is a **new object**, not a composition failure. `plait | sate` prints two fates and cannot say SUPERSEDED of the union. braid exists because that pipe is a lie. `ditto | sh` pastes `held --follow`; live `held` does not parse `--follow`. pup exists because that pipe is a lie.

The night’s real Unix win is not “sixteen vehicles.” It is **five mouths** that actually attach to existing producers, plus a handful of honest refusals.

---

## Composition graph (survivors)

Producers on the left. Mouths in the middle. Siblings that must **not** merge on the right.

```
rg -n / rg -nH / rg -l / git grep
        │
        ├─► ambit 'snippet'     ── spare (predicate invert; no third clone)
        ├─► peal                ── gold unique locator; first-locator LIES
        └─► seed                ── VEHICLE: one content pin or refuse the bag
                                      broken: rg -nH from nested cwd (repo-relative)

rg 'format!|+\s*"' / --templates -
        │
        ├─► invert / sluice     ── VEHICLE: named-hole inverse printf (filter)
        ├─► splice              ── string-first concat
        ├─► weld / solder       ── expr-first concat (proving string backward)
        ├─► stile               ── distinctive proving string (not 4-char floor)
        └─► rime / caulk        ── leftover operand; NOT weld stdout
                                      broken: leftover `\nDone.` is not a fresh query

git diff / git diff A B
        │
        ├─► ply                 ── dump (ancestor)
        ├─► weft --only docs    ── CI gate; docs/** glob FREES code
        ├─► woof --only prose   ── class, not path
        ├─► tally --only prose --chg ── VEHICLE: fence number *change*
        ├─► snag --forbid number ── tripwire; COMPOSE with weft/woof, do not clone
        ├─► zanei --diff -      ── leftover claims
        ├─► sic --check / aka --check
        └─► sate --diff -       ── occupancy of a patch, not apply --check
                                      broken: weft fence+path swallow; lockfile skip;
                                              binary stdin traceback (shared)

gh api …/pulls/N/comments
        │
        ├─► plait               ── algebra only (COMMUTE/JAM/STACK)
        ├─► braid -C TREE       ── occupy the *fold* (not N rows)
        ├─► tilde -C TREE       ── occupy the *nits*, NFC keys
        ├─► hank --emit -C TREE ───┐
        └─► quire --emit -C TREE ──┼─► git apply     VEHICLE
                                      broken: plait|sate; hank emit without -C;
                                              quire partial-tree emit (closed)

ditto A B
        │
        ├─► | sh                ── BROKEN (held --follow unrecognized)
        ├─► | pup               ── VEHICLE: covering in, eras out
        └─► crib exists SRC     ── unary walker; does not read the pipe

a | b | c  (the pipeline under study)
        │
        ├─► beck --needle N --sh 'a|b|c'   ── first producer of a byte
        ├─► innard                         ── descend $() / mid 2>&1
        └─► facet -n N                     ── same-object JSON fields
                                      broken: { } is not $(); greedy crate coincidence;
                                              --run + strips quotes; tee-dir ≠ JSON --save
```

Do not draw arrows between families. `rg | peal | weft` is not a product. `weld | rime` is not a byte pipe (leftover is structured: `--matched` / `--remainder`). `ditto | crib` was suggested and **not built**.

---

## Evidence this session (PARENT)

Re-ran binaries in their worktrees. Did not patch victims. Did not merge.

| pipe | result | rc |
| --- | --- | --- |
| `cd kizu && rg -n 'let b_side' src/git/parse.rs \| peal --explain` | three spans incl. `Some(bytes_to_path)` rg never printed | 0 |
| same `\| seed --explain` | same three spans | 0 |
| `rg -n 'return None;' parse.rs \| peal` | seeds quoted-form `:33-34` | 0 **lie** |
| same `\| seed` | `locators name 9 stacks` | **2** |
| `cd kizu/src/git && rg -nH 'let b_side' parse.rs \| peal` | advertised producer, repo-relative miss | **2** |
| `rg -n` from same nested cwd `\| peal` | pin recovery, gold | 0 |
| `printf '' \| peal` | `No cwd walk` | 2 |
| `printf '\x00\xff' \| peal` | `UnicodeDecodeError` traceback | 1 **crash=miss** |
| `weft --only docs < mixed-money.diff` | FAIL `30 → 60` | 1 |
| `woof/tally` same stdin | FAIL number | 1 |
| `weft --only docs < fence-number.md.diff` | **OK leaked=0** | 0 **swallow** |
| `woof/tally --chg` same fence | FAIL `30 → 60` | 1 |
| `weft --only docs < docs-generated-api.rs.diff` | **OK** (`docs/` glob) | 0 |
| `woof/tally` same | FAIL ident+number | 1 |
| `woof < fence-new-sample.md.diff` | FAIL 4 ident inserts | 1 |
| `tally --chg` same new sample | **OK leaked=0** | 0 |
| `git diff sitbone 77df1da^..77df1da \| weft --only docs` | FAIL leaked=21 Makefile | 1 |
| same `\| woof --only prose` | FAIL leaked=144 ident=126 | 1 |
| same `\| tally --only prose --chg` | FAIL leaked=22 (Makefile; README `2048` gone) | 1 |
| `snag --forbid number < mixed-money` | TRIP `30 → 60` | 1 |
| `snag --forbid number < comment-number.diff` | TRIP (comment-interior) | 1 |
| `weld --templates concat.js $'{"ok":true}\nDone.'` | `{response}={"ok":true}` | 0 |
| `solder` / `stile` same | identical bind | 0 |
| `weld … $'\nDone.'` | `no template for: Done.` | 1 |
| `weld thin.go 'ERROR worker crashed abcd'` | `{body}abcd` | 0 **every-log-line** |
| `stile` same | miss | 1 |
| `rg -g '*.swift' 'Done\.' tenaoshi \| weld --templates - $'{"ok":true}\nDone.'` | EditPlanParserTests.swift:318 | 0 |
| `weld --templates fixtures/` | refuse directory | 2 |
| `hank --emit -C commute-tree commute.jsonl \| git apply` | tree `ALPHA/beta/GAMMA` | 0 |
| `hank --emit commute.jsonl` (no `-C`) | `need -C to fill COMMUTE gaps` | 3 |
| `hank --emit jam.jsonl` | `JAMMED; not emitting` | 2 |
| `quire --emit -C two-file \| git apply` | `ALPHA/beta` and `GAMMA/delta` | 0 |
| `quire --emit two-file.jsonl` (no `-C`) | empty stdout, need tree-image | 3 |
| `braid -C commute-a-only` | occupy=SUPERSEDED of the fold | 0 |
| `tilde -C commute` | occupy nits `alpha\|gamma`, not covering | 0 |
| `ditto -C kizu 5671a72^ 5671a72` | `copy src/init.rs → src/init/install.rs` | 0 |
| `ditto … \| pup -C kizu` | copy eras TRUE 5/24, origin 5671a72 | 0 |
| `held --follow exists deep-research-…` | `unrecognized arguments: --follow` | usage |
| `beck --needle fatal:… --sh 'git -C /tmp status \| cat'` | MINT stage 0 **stderr**, tee MISS, piped 0 | 0 |
| naive `git -C /tmp status \| tee … \| cat` | tee0_bytes=0 | — |
| `beck` sed prefix wrap | WRAP sed, pieces glue `fatal: ` + printf | 0 |
| `beck --sh '{ printf kizu \| tr k K; } \| cat'` | NONE (brace split) | 1 |
| tiny JSON `\| jq '.name+"@"+.version'` via beck | WRAP jq, glue `@` | 0 |
| `facet -n 'kizu@0.7.0'` two-package fixture | siblings `.name`+`.version`; greedy COINCIDENCE named | 0 |
| `rg format!\|anyhow! kizu \| invert '… failed to spawn…'` | span leftover `prefix: 2026-08-19T23:50:01Z ERROR` | 0 |
| `invert --templates kizu/` | refuse directory | 2 |
| `git diff v0.3.0 v0.7.0 -- Cargo.toml \| zanei --diff -` | plugin.json still `"version": "0.3.0"` | 0 |

---

## Five lineages (assigned)

C = composability. Shape = Unix filter / Unix emitter / app / **new object because the pipe lied**.

### 1. Locator stream — ambit / peal / seed

**Object.** Path-condition stack. Address = locator. Producer = `rg`. Not a snippet walk of cwd (`under`/`chime` default). Not `rg` of the `if`.

| tool | mouth | C | shape | verdict |
| --- | ---: | ---: | --- | --- |
| under / chime | argv `FILE:LINE`, optional DIR walk | 3 | walker with a filter flag | park (ancestors) |
| ambit | `rg \| ambit 'snippet'` | 4 | Unix filter (predicate invert) | keep spare |
| peal | `rg \| peal` | 4 | Unix filter (stack rhyme) | keep; first-locator hole |
| seed | `rg \| seed` | **5** | Unix filter that **refuses a bag** | **mutate / PATH** |
| amid | `rg --json` peel | 3 | other ingest, LINE:text refuse | park (bakeoff 1/3) |

Gold pipe **PARENT**: unique locator `let b_side` expands to `Some(bytes_to_path)`. Scan ≠ `--hits` filter. Empty stdin is usage, not a walk.

Broken producer (DESTROYER_PEAL + PARENT):

| advertised pipe | empirical |
| --- | --- |
| `rg 'return None;' \| peal` | first locator is the seed → quoted-form `:34`. seed **rc=2**, lists 9 stacks. That refuse listing *is* the product. |
| `rg -nH` from `src/git` | peal joins `parse.rs` to git toplevel → rc=2. `rg -n` (no `-H`) recovers. Error text recommends the producer that dies. |
| uniqueness | substring `in`; decoy comment steals the file (DESTROYER). seed strips the line. |
| `pins[:16]` | 17th disambiguator thrown away (DESTROYER). seed scans every pin. |
| `--column` | `60:5: text` parsed as LINE:text. |
| binary stdin | traceback rc=1, same class as weft/plait. |

Do not grow a third ambit. Snippet invert (ambit) and stack rhyme (peal/seed) are opposite ends of `when`. `--hits` is the ancestor line filter; default stdin is a **file scan**. Kill only if a later generation walks cwd again.

**Skeptic one-liner that loses:** `rg 'starts_with(a/)'` never prints `let b_side`. The invert is unusable until locators name files.

---

### 2. Ply gate — ply / weft / woof / tally (+ snag)

**Object.** A unified diff is a superposition of syntactic classes. Project onto an allow-list (weft/woof/tally) or a forbid-list (snag). Exit 1 = leak/trip.

| tool | mouth | C | shape | verdict |
| --- | ---: | ---: | --- | --- |
| ply | dump ply-edits | 4 | Unix filter, wrong default (firehose) | park ancestor |
| weft `--only docs` | `git diff \| weft` | 4 | Unix CI gate, **path glob** | keep ancestor |
| woof `--only prose` | `git diff \| woof` | 5 | Unix CI gate, class not path | keep |
| tally `--chg` | `git diff \| tally --only prose --chg` | **5** | Unix CI gate, fence *change* | **mutate / PATH** |
| snag `--forbid number` | `git diff \| snag` | **5** | Unix tripwire | **compose, do not merge** |

Gold **PARENT**: mixed-line `30 → 60` fails all three allow-lists. sitbone `77df1da` Makefile still leaks under weft (21), tally (22), woof (144). That is the review cheat: README PR that also rewrote the Makefile.

Broken weft (DESTROYER_WEFT + PARENT):

| stdin | weft `--only docs` | woof `--only prose` | tally `--chg` |
| --- | --- | --- | --- |
| mixed-line number | FAIL | FAIL | FAIL |
| README fence `30→60` | **OK** (backtick-string + path) | FAIL number | FAIL number chg |
| `docs/generated/api.rs` | **OK** (`docs/` glob) | FAIL ident+number | FAIL |
| new bash sample, no number | OK | FAIL 4 idents | **OK** |
| sitbone README `2048` insert | not a leak | number ins + 114 idents | **not a leak** |
| comment-interior `// 30→60` | OK (comment ply) | OK | OK — **snag TRIP** |

`--only docs` on weft is `paths-filter` with a lexer. DESTROYER: do not kill the class gate to hide the glob. woof closed the glob. tally closed the ident flood. snag closed the comment-interior number. **Three objects. Pipe them.**

```
git diff origin/main...HEAD | tally --only prose --chg     # docs PR: number *change* leaked?
git diff origin/main...HEAD | snag --forbid number         # any number ply, even inside //
```

Do not lower weft so `{x}\n`-shaped every-token noise returns (that was ply v0.1). Do not make tally global `--chg` (Makefile `tccutil` deletes are `del`, occupancy of nothing). Binary / rename / lockfile skip remain occupancy of nothing (DESTROYER_WEFT, DESTROYER_WOOF). Shared operational hole: binary stdin traceback.

**Skeptic one-liner that loses:** `git diff --stat` and `paths-filter: docs/**` both pass `docs/generated/lib.rs` and a fenced timeout.

---

### 3. Inverse-printf concat — weld / stile / solder (+ invert, rime, caulk)

**Object.** Concat may **start at an expression**. A later string proves the chain. Names bind. Middle-drop stuffing is a miss. Directories exit 2. rustc locators refused.

| tool | mouth | C | shape | verdict |
| --- | ---: | ---: | ---: | --- |
| unfmt / stencil | paste + walk | 2 | **app-shaped walker** | park |
| sluice / invert | `rg \| invert paste` | **5** | Unix filter | keep invert as named-hole vehicle |
| splice | string-first `"lit" + expr` | 4 | Unix filter | keep ancestor |
| weld | `rg \| weld --templates - paste` | **5** | Unix filter, 4-char floor lie | keep vehicle |
| solder | same mouth, clean-room | 5 | proof the primitive is strong | keep spare |
| stile | same mouth, distinctive static | 5 | Unix filter, floor mutation | **mutate** |
| rime / caulk | `--matched` + `--remainder` | 4 | Unix, **not weld stdout** | keep siblings |

Gold **PARENT**: `response() + "\nDone."` binds `{response}` on concat.js and on tenaoshi via `rg | weld --templates -`. splice extracts holes=0 `\nDone.` and misses. `weld --templates fixtures/` refuses to walk (rc=2), same banner as invert.

Broken weld (DESTROYER_WELD + PARENT):

| query | weld | stile | whose object |
| --- | --- | --- | --- |
| full `{"ok":true}\nDone.` | bind | bind | concat |
| leftover `\nDone.` | miss (`Done.` after strip) | miss | **rime/caulk** |
| `{body}abcd` every log line | **hit** | miss | stile floor |
| incomplete fence leftover | truncated success | miss | caulk complete operand |
| `{a}:{b}` on a URL | hit (2-hole exemption) | still hits | ranking, not floor |
| `cleaned + "\n"` | not extracted | not extracted | leftover-only ≠ inverse-printf |
| `fmt.Sprint` spaces | treated as `+` | same | sibling operator |
| `MAX_FILE_BYTES` | silent omit | same | warn, do not walk |

solder **PARENT** byte-matches weld on concat.js (`score=0.71`, `{response}={"ok":true}`). Clean-room survived. It is not a new mouth.

Do not: start the scanner at every identifier (walker); lower `visible < 4` so `{cleaned}\n` matches every line; leftover-name search `deserted={0}`; hide wrap with a no-bindings guard; grow a rustc parser.

`weld | rime` is **not** a byte pipe. Leftover is a structured query (`--remainder $'\nDone.'`, or parse invert’s `prefix:` line). That is composition of *objects*, not `stdout | stdin`. Honest.

**Skeptic one-liner that loses:** `rg 'Done.'` finds the proving string and not `{response}`. `rg '{"ok"'` finds the paste and not the template.

---

### 4. Suggestion strands — plait / braid / hank / quire / tilde

**Object.** Review suggestions are strands (span + before→after). Composition algebra first (COMMUTE / STACK / JAM / SPLIT). Then **either** occupy the fold **or** emit it as a patch. Not GitHub outdated. Not `git apply --check`. Not N occupancy rows.

| tool | mouth | C | shape | verdict |
| --- | ---: | ---: | --- | --- |
| plait | `gh api \| plait` | 4 | Unix algebra (no tree) | keep |
| braid | `gh api \| braid -C HEAD` | 4 | occupy the covering | keep; chimera hole |
| tilde | `gh api \| tilde -C HEAD` | 4 | occupy the **nits**, NFC | mutate occupancy |
| hank | `gh api \| hank --emit -C HEAD \| git apply` | **5** | Unix emit | **PATH occupy-then-apply** |
| quire | `gh api \| quire --emit -C HEAD \| git apply` | **5** | Unix tree-image emit | **PATH multi-file** |
| sate / plea | occupy **each** claim | 4 | Unix, wrong object for a fold | keep for patches, not suggestions |

Gold **PARENT**:

```
hank --emit -C commute-tree commute.jsonl | git apply
# tree becomes ALPHA / beta / GAMMA   rc=0

quire --emit -C two-file two-file.jsonl | git apply
# app.py ALPHA/beta  util.py GAMMA/delta   rc=0
```

JAM refuses to emit (rc=2, empty stdout). COMMUTE without `-C` refuses (rc=3): concatenation of nits is not a covering. quire without `-C` refuses the **whole** tree-image (does not emit `app.py` alone). That refuse is the object.

`plait | sate` is the conventional hybrid and a lie. DESTROYER_BRAID: stack-mid tree is plea `APPLIED` round1 + `PENDING` round2; braid is one `SUPERSEDED` of `beta→beta3`. Do not “fix” that by piping.

Broken (DESTROYER_PLAIT / BRAID + PARENT):

| hole | who still has it | who closed it |
| --- | --- | --- |
| two fates ≠ SUPERSEDED of union | plait\|sate | braid / tilde |
| covering paints HEAD gaps (chimera pad) | braid v0.2 | **tilde** occupies nits |
| NFC `café` vs `café` two PARALLEL files | plait / braid | tilde |
| hank v0.1 wholesale needs `--unidiff-zero` | — | hank v0.2 mixed hunks **PARENT apply** |
| missing-path still emits the file that covered | hank | **quire** all-or-nothing |
| three-round STACK SPLIT, no occupy | braid | open |
| `--remarks` MIXED / COVER-on-replies | plait/braid | not this object |

Ship **two mouths**, not five PATH entries: algebra is plait (spare); occupy is tilde (NFC, nits not canvas); emit is quire (tree-image; hank is the single-file ancestor). Do not grow a GitHub client. `--apply` that writes the worktree is a convenience, not a new object.

**Skeptic one-liner that loses:** clicking “Commit suggestion” three times. `git apply` of two STACK fences looks for `beta2` in the origin file.

---

### 5. Copy covering — ditto / crib / pup

**Object.** Same blob still on A and also born on B is **COPY**, not FOLLOW. `git mv` is identity. `cp` is an extra holder. ditto classifies two trees. crib occupies unary `copy SRC`. pup occupies the **pipe**.

| tool | mouth | C | shape | verdict |
| --- | ---: | ---: | --- | --- |
| ditto | two trees in; prints `held` lines | 3 | Unix **emitter of paste** | keep producer |
| crib | `crib exists SRC` (no stdin) | 2 | **app-shaped walker** | keep unary spare |
| pup | `ditto A B \| pup` | **5** | Unix covering→eras | **PATH** |
| glyph `--follow` | exclusive-side SHA = rename | 2 | wrong object for remaining blob | park |
| held | `exists` / `grep` eras | 4 | does **not** parse `--follow` | keep; do not fake copy |

Gold **PARENT**:

```
ditto -C kizu 5671a72^ 5671a72 | pup -C kizu
# copy src/init.rs → src/init/install.rs
# TRUE 5/24 first-parent, origin 5671a72
```

kizu R100 is still FOLLOW (`ditto` emits `held --follow exists deep-research-…`). Sitbone FocusRiverView stays `grep`, never copy.

Broken paste **PARENT**:

```
$ held -C kizu --follow --rev 4e37f16 --limit 12 exists deep-research-ai-agent-hooks.md
held: error: unrecognized arguments: --follow
```

`ditto A B | sh` is occupancy of nothing. CANDIDATE already named `ditto | berth --stdin` and `ditto | crib`; crib **does not read the pipe** (unary path query, 405 probes on C056 vs pup parsing the sheaf). pup is the mouth that was missing. Do not stuff `--stdin` onto crib so unary occupancy grows a flag.

**Skeptic one-liner that loses:** `git diff --name-status -C` prints `C056` and then you still paste `held exists DEST`, which is TRUE for unique births and follow dests alike.

---

## Meta-pipe — beck / facet / innard

Not a filter in the `rg | X` sense. The object **is a pipeline**. Needle in; first producer out. Exit 0 found, 1 miss, 2 usage.

| tool | C | shape | verdict |
| --- | ---: | --- | --- |
| beck | 4 | Unix query of a pipe (runs it) | **mutate**; `{ }` / greedy JSON open |
| innard | 4 | descend `$()`; mid-command `2>&1` is merge | keep mutation |
| facet | **5** | JSON stdin field-cover | **PATH sibling**; do not merge into beck |
| knot | 3 | wait-source of pipe∩process tree | keep; not first-producer |
| `tee \| grep` | — | skeptic | answers exact-in-dump, misses unpiped stderr |

Gold **PARENT**: `git -C /tmp status | cat` → MINT git **stderr**, tee MISS, naive tee 0 bytes. Sed prefix wrap disagrees with tee (tee names sed; beck names glue + payload). Tiny JSON WRAP jq, pieces `kizu` + glue `@` + `0.7.0`.

Broken (DESTROYER_BECK + PARENT):

- `{ printf kizu | tr k K; } | cat` → NONE (parser is not `$()`). CANDIDATE listed braces as nested. Empirical: three bash errors.
- cargo `kizu@0.7.0` greedy cover steals `@0.7.0` from `notify-debouncer-full@0.7.0`. Facet **PARENT** names the coincidence and keeps `.name`+`.version` of kizu. That is why facet exists.
- `--run +` joins with spaces (quotes gone). `--sh` is the honest door.
- Trace **dir** of tee dumps cannot see unpiped stderr. JSON `--save` can.

Do not grow a pipeline debugger. Do not merge facet into beck (byte-cover vs same-object fields). Do not merge knot (wait-source).

---

## Other Unix-shaped survivors (compose, do not re-litigate)

Filters whose mouth is already a producer. Keep. Do not spend Gen-3 merging them into the five families.

| pipe | tool | note |
| --- | --- | --- |
| `rg \| invert paste` | invert | named holes + span leftover. **PARENT** kizu timestamp span. |
| `git diff \| zanei --diff -` | zanei | leftover **claims**. **PARENT** kizu `0.3.0→0.7.0` still in plugin.json. |
| `git diff \| sic --check` | sic | exact wire key. Inflection is aka. |
| `git diff \| aka --check` | aka | inflection identity. Do not merge with sic. |
| `git diff \| sate` | sate | occupancy of a **patch**, not a suggestion fold. |
| `cat ci.log \| flume --from-dir A --to-dir B` | flume | gitless locator rewrite. gist is LSP 0-based, different schema. |
| `cat publish.json \| gist --from-dir A --to-dir B` | gist | JSON-RPC filter. Unix-shaped, schema-shaped. Not an LSP host. |
| `tell A B` | tell | emits predicates; `| held` is still **paste** (AUTHOR). |
| `sow f --emit json` | sow | producer of fixtures. JSON out is Unix; running tests is not. |
| `cusp --format tsv` | cusp | TSV cut. |
| `erst HEAD` / `gh pr diff \| erst -` | erst | natal keys that inflect. Commit/diff in, never FILE:LINE. |

`pin mint | pin resolve` is a **token**, not a stream. Composable as an address, not as `rg | pin`. Keep.

---

## App-shaped survivors (keep as apps)

These earned a keep on other judges’ axes. Composer does **not** pretend they are filters.

| tool | why app | honest Unix edge |
| --- | --- | --- |
| cinch / winnow / glean / alibi | spawn the test command, ddmin the dirty tree | `--format patch` / `--format drop` can feed `git restore` |
| knot / spoor / cling / coast | process tree, waitpid, attach | JSON report; not `rg \|` |
| unfmt / stencil | own ignore policy, walk the repo | invert already is the filter; park the walkers |
| held / perch / berth / crib / ford | history walkers | TSV/JSON out; predicates in **as argv** |
| lode / orbit | inspect binaries / PATH guise | `ldd` cousin |
| maiden / badge | run tests, redness | not a stream |
| folk | linter with 0 orphans | parked |
| kiln / clutch / sinter | generation lots | fuse is sinter; not a pipe |

FIRST_SKEPTIC kept winnow+cinch because the Unix one-liner loses the *dirty hunk* object. Composer agrees they are real, and still calls them apps. `winnow | cinch` is the conventional hybrid and the wrong object (fingerprint wheat vs pass/fail lockset). Same shape as `plait | sate`.

---

## Broken pipes ledger

Pipes that were advertised, suggested, or look like Unix, and empirically are not.

| claimed | empirical | fix already in tree? |
| --- | --- | --- |
| `rg FILE \| peal` (bag of returns) | first locator wins | **seed** refuses |
| `rg -nH` from nested cwd \| peal | repo-relative join, rc=2 | **open** (cwd then repo) |
| `rg \| chime` / `rg \| under` | stdin is line filter / default is walk | ambit/peal flipped the mouth |
| `git diff \| weft --only docs` on `docs/lib.rs` | glob frees code ply | **woof** |
| `git diff \| weft` on a fenced `30→60` | backtick-string + path OK | **woof/tally** |
| `git diff \| woof` on a new fence sample | 114 ident inserts | **tally --chg** |
| `git diff \| weft` comment-interior number | comment ply OK | **snag** (do not clone into weft) |
| `ditto \| sh` | `held --follow` unrecognized **PARENT** | **pup** |
| `ditto \| crib` | crib does not read stdin | pup; do not flag-stuff crib |
| `plait \| sate` / `plait \| plea` | two rows, not SUPERSEDED of union | **braid/tilde** |
| `hank \| git apply` without `-C` | no covering | refuse rc=3 **PARENT** |
| `hank --emit` of a missing sibling path | join the file that covered | **quire** all-or-nothing |
| `weld $'\nDone.'` | strip newline, miss | **rime/caulk** |
| `weld` `{body}abcd` | 4-char floor | **stile** |
| `beck --sh '{ a \| b; }'` | three syntax errors **PARENT** | innard / open |
| `beck` cargo `kizu@0.7.0` | greedy foreign `.id` | **facet** |
| `beck --run -- printf '%s\n' 'hello world' + cat` | quotes stripped | `--sh` only |
| `pin \| invert` | relocates a line, binds dest names now | dowel said wrong object; do not PATH this |
| `when \| held` | occupancy of a token, not of a stack | tenure; not a pipe |
| `tell A B \| held` | paste a generated command | open (held does not parse tell stdout) |
| binary stdin (weft/peal/plait/zanei class) | `UnicodeDecodeError` rc=1 | fail closed **exit 2**; do not `errors=replace` (fail open) |

A one-line decode-or-die on stdin would hide the traceback and would not touch first-locator, `docs/lib.rs`, leftover `\nDone.`, or cargo coincidence. Destroyers left it unpatched on purpose. Composer agrees: do not spend the last twenty minutes on that.

---

## Unix-shaped vs app-shaped (assigned + vehicles)

```
UNIX FILTERS (stdin object, refuse walk)
  seed  peal  ambit
  tally woof weft snag ply
  invert sluice weld stile solder splice
  zanei sic aka sate
  flume gist
  hank-emit quire-emit plait
  pup
  facet

UNIX QUERIES (argv is the object, stdout is the answer, still small)
  beck innard
  pin mint/resolve
  erst  tell  sow-emit  cusp
  when/chime (argv FILE:LINE)

UNIX because they refused to be the naive pipe
  braid / tilde     (not plait|sate)
  seed              (not first-locator peal)
  pup               (not ditto|sh)
  quire             (not concatenating hank files)
  stile             (not raising visible<4)
  facet             (not greedy beck cover)

APP (keep, label honestly)
  cinch winnow glean alibi
  knot spoor cling
  unfmt stencil
  held perch berth crib ford
  lode orbit maiden

DEAD / PARKED as products
  haunt  folk  nigh-as-default  pinch∥hitch  kiln∥clutch
```

---

## Do not merge

Orthogonal objects. Pipe them or cite them. Concatenating CLIs is how this night almost died.

| keep separate | why |
| --- | --- |
| ambit ≠ peal/seed | snippet invert ≠ stack rhyme |
| weft ≠ snag | allow-list ≠ forbid-list |
| woof ≠ tally | every code ply ≠ fence number *change* |
| weld ≠ rime/caulk | fresh concat ≠ leftover operand |
| weld ≠ stile | proving string exists ≠ proving string is distinctive |
| splice ≠ weld | string-first ≠ expr-first |
| invert ≠ weld | format template ≠ concat chain |
| plait ≠ braid/tilde | algebra ≠ occupancy of the fold |
| hank ≠ quire | per-file covering ≠ tree-image |
| braid ≠ tilde | covering canvas ≠ nits + NFC |
| sate ≠ braid | patch occupancy ≠ suggestion fold |
| ditto ≠ pup ≠ crib | covering emitter ≠ pipe occupancy ≠ unary walker |
| glyph-follow ≠ ditto-copy | remaining blob is not a rename |
| beck ≠ facet | first byte ≠ same JSON object |
| beck ≠ knot | first producer ≠ wait-source |
| pin ≠ flume ≠ gist | token ≠ log stream ≠ LSP schema |
| aka ≠ sic | inflection ≠ exact wire bytes |
| winnow ≠ cinch | fingerprint ≠ pass/fail lockset |
| zanei ≠ wraith | claims ≠ leftover names |

Coordinator already banned: third ambit, fourth cinch, leftover-name search, inverse-printf walker. Composer adds: **do not merge occupy and emit** (braid/tilde vs hank/quire); **do not merge allow-list and tripwire** (weft/tally vs snag); **do not teach weld to consume leftovers**.

---

## Preserve (Composer PATH, several)

Not a ranking. Mouths a developer can type tomorrow that Unix one-liners cannot.

1. **`rg | seed`** — rest of that path-condition arm, or a listed refuse of the bag. peal remains the unique-locator gold.
2. **`git diff | tally --only prose --chg`** then **`git diff | snag --forbid number`** — docs gate × number tripwire. woof if you want every fence ident.
3. **`rg | invert paste`** and **`rg | weld --templates - paste`** — named-hole format vs expr-first concat. stile if the proving string is thin. rime/caulk for leftovers.
4. **`gh api …/comments | quire --emit -C HEAD | git apply`** — tree-image of the fold. hank for one file. tilde to occupy nits without applying.
5. **`ditto A B | pup`** — copy eras without `sh`. crib stays unary.
6. **`git diff | zanei --diff -`** — leftover claims.
7. **`beck --needle N --sh 'a | b'`** plus **`facet -n N`** on JSON — first producer, then same-object fields.

Spare, do not PATH: ambit, peal (after seed), weft (after woof/tally), ply, splice, solder, plait, braid, ditto (as a command you paste), held.

---

## Scores (assigned lineages only)

C is the ranking axis here. Σ is diagnostic.

| ID | tool | N | U | P | C | E | Ev | Σ | shape | verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| mut-35 | ambit | 4 | 4 | 5 | 4 | 5 | 2 | 24 | filter | keep spare |
| mut-51 | peal | 4 | 4 | 5 | 4 | 5 | 3 | 25 | filter | keep |
| hyb-19 | seed | 4 | 5 | 5 | 5 | 5 | 4 | 28 | filter | **mutate** |
| cand-37 | ply | 4 | 3 | 5 | 4 | 4 | 2 | 22 | dump | park |
| mut-50 | weft | 5 | 4 | 5 | 4 | 5 | 2 | 25 | gate | keep ancestor |
| mut-90 | woof | 4 | 5 | 5 | 5 | 5 | 3 | 27 | gate | keep |
| mut-99 | tally | 4 | 5 | 5 | 5 | 5 | 4 | 28 | gate | **mutate** |
| mut-61 | snag | 4 | 5 | 5 | 5 | 5 | 3 | 27 | tripwire | **compose** |
| mut-15 | invert | 5 | 5 | 5 | 5 | 5 | 3 | 28 | filter | keep |
| mut-59 | weld | 5 | 5 | 5 | 5 | 5 | 3 | 28 | filter | keep vehicle |
| mut-109 | stile | 4 | 5 | 5 | 5 | 5 | 4 | 28 | filter | **mutate** |
| re-11 | solder | 3 | 5 | 5 | 5 | 5 | 2 | 25 | reimpl | keep spare |
| mut-79 | rime | 4 | 4 | 5 | 4 | 4 | 3 | 24 | leftover | keep sibling |
| mut-91 | caulk | 4 | 4 | 5 | 4 | 4 | 2 | 23 | leftover | keep sibling |
| cand-38 | plait | 5 | 4 | 5 | 4 | 5 | 2 | 25 | algebra | keep |
| hyb-12 | braid | 5 | 4 | 5 | 4 | 5 | 3 | 26 | occupy fold | keep |
| hyb-18 | tilde | 4 | 4 | 5 | 4 | 5 | 3 | 25 | occupy nits | mutate occupy |
| mut-87 | hank | 4 | 5 | 5 | 5 | 5 | 3 | 27 | emit \| apply | keep |
| mut-97 | quire | 4 | 5 | 5 | 5 | 5 | 4 | 28 | tree emit | **mutate** |
| mut-66 | ditto | 5 | 4 | 5 | 3 | 5 | 2 | 24 | paste emitter | keep producer |
| mut-84 | crib | 4 | 4 | 5 | 2 | 5 | 2 | 22 | walker | keep unary |
| mut-94 | pup | 4 | 5 | 5 | 5 | 5 | 3 | 27 | covering\|eras | **mutate** |
| cand-41 | beck | 5 | 4 | 5 | 4 | 5 | 4 | 27 | pipe query | **mutate** |
| mut-96 | facet | 5 | 4 | 5 | 5 | 5 | 3 | 27 | JSON cover | keep sibling |
| mut-107 | innard | 4 | 4 | 4 | 4 | 4 | 3 | 23 | $() descent | keep |

E=5 only where PARENT or DESTROYER ran the binary. rime/caulk/innard AUTHOR+destroyer cite, not re-run this session.

---

## Disagreement with other first-selection judges (Composer only)

FIRST_UNIX’s sixteen vehicles were objects. Composer’s seven PATH mouths are **pipes**. Invert stays. under is now seed (the stream), not under (the walker). cinch stays an app. pin stays a token. flume stays a log filter next to gist, not next to pin. perch/held stay walkers that *emit* Unix, they are not `rg |`.

FIRST_SKEPTIC’s four (winnow, cinch, invert, zanei) mix two apps and two filters. Composer keeps the two filters on PATH and keeps the two apps in the toolbox, labelled apps.

A “hybrid” score of 5 on C is not a license to concatenate two CLIs. braid C4 is *higher* than `plait | sate` would have been, because it refused the pipe.

---

## What not to spend the preservation hour on

1. Pretty explain dumps, GitHub Actions annotations, TUIs that paint the recovered file.
2. Teaching held `--follow` so `ditto | sh` turns green. That hides the copy object. pup already occupies the covering.
3. A one-line stdin `errors=replace`. Fail closed exit 2, later.
4. Merging tally into weft, stile into weld, facet into beck, quire into hank, seed into peal.
5. Another leftover-name search. Another inverse-printf walker. A third under-stream. A fourth cinch.

The night composed when a mutation **changed the mouth** (walker→stream, glob→class, paste→parse, N rows→one fold, first-locator→refuse). It failed when a README drew a pipe the binary does not speak. Composer keeps the mouths that attach to `rg`, `git diff`, `gh api`, `ditto`, and `git apply`. Everything else is an app or a spare.

No single winner. Seven pipes. Five families. Several orthogonal siblings. Haunt dead. Folk parked.
