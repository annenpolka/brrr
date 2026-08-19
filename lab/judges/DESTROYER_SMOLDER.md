# DESTROYER — smolder

Adversarial pass on the leftover-*claim invert* (locus in, falsifying commit out). No leftover-name search (haunt/wraith). `FILE:LINE` is legal **input**. No rewrites: the victim binary is untouched. Failures are conceptual except a size-cap that reports a live dest as `missing`.

- **smolder** (mutation-63, v0.2.0) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-cb3a629800b3`
- Peel: **tinder** (mutation-81, dest-file identity then the fact) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bad-eb91-7d80-9aa0-1040781e71b7`
- Transcript: `/tmp/destroy-smolder/transcript.txt`
- Follow-up: `/tmp/destroy-smolder/followup.txt`
- Fixtures: `/tmp/destroy-smolder/fixtures/`
- Attack drivers: `/tmp/destroy-smolder/{attack,followup,rest}.py`
- `./smolder self-test` still exit 0 after the battery. Victim not rewritten.

Attacks: dest rename / dest identity, leftover-name after dest move, generated lockfile vs comment origin, October as timeout 10, two packages named `version`, `vendor/` skip, 2 MB dest omit, Japanese as the binding, ash vs believer.

Verdict: **mutate, do not kill.** Gold kizu `plugin/plugin.json:4` is still `53cbd1a` Cargo.toml `0.3.0 → 0.3.1` (not `git blame`'s `bff820fb`, not Cargo.lock). Gold sitbone `CLAUDE.md:329` is still `e9b0f75` `0.4 → 0.45`. Named lockfile dest is still `regenerate cargo`. ISO `2024-10-01` is still not timeout 10. The invert verb is real. The holes are dest identity, leftover-name of dest text, workspace `version`, a calendar mask that only knows ISO/dot-version, a dead `SKIP_DIRS`, and ash as a path/banner table.

Do not repeat DESTROYER_ZANEI. Those attacks are the *forward* leftover scan (diff in, dest afterimages out). This pass only asks the invert: this dest locus, which commit made the claim false?

---

## Primitive restated

Given a leftover dest locus (`FILE:LINE` or stdin locators), emit the **diff (commit) that falsified the claim**. Regenerated dest (`generated/`, `oracle/`, lockfile, `*.generated.*`, `@generated` banner) is **ash**: leftover *build*. Ash answers **regenerate**. A believer leftover names the falsifying commit and origin hunk.

Forward tools (zanei / ember / cinder) take a diff and print leftover afterimages. smolder inverts. A *fact* is a typed bound name/value, rename, or polarity flip. Not leftover names.

`git blame` answers who last *touched the leftover line*. `git log -S leftover -- dest/newpath` after `git mv` answers dest recency. The invert has to name the fact.

---

## 1. Dest rename — live path names the fact; dead path is missing; leftover-name eats dest:84 (conceptual)

Path-limited pickaxe names the rename. That is tinder's peel of dest recency, not a leftover-name search.

```
$ git -C dest-rename log -S 10 --oneline -- docs/最終.md
c545867 rename dest to CJK

$ git -C dest-rename log -S 10 --oneline -- .
720fcfe timeout 10 to 30
333b222 timeout 10
```

A 100% dest rename does not change the repo-wide token count, so whole-repo `-S` skips it. smolder walks `-- .`. On the **live** holder after `help.md → guide.md → 最終.md` it names the fact, not the rename:

```
$ ./smolder --no-color --explain --no-hunk -C dest-rename docs/最終.md:1
smolder: leftover  docs/最終.md:1
CLAIM timeout default is 10
FALSIFIED 720fcfe3d178 timeout 10 to 30
FACT HOOK_TIMEOUT: 10 → 30   src/config.py:1   score 62
```

Dead dest names are not dest identity. They are `missing`:

```
$ ./smolder -C dest-rename docs/guide.md:1
smolder: missing  docs/guide.md:1
# rc=1

$ ./smolder -C dest-rename docs/help.md:1
smolder: missing  docs/help.md:1
# rc=1

$ ./tinder -C dest-rename docs/help.md:1
tinder: leftover  docs/最終.md:1  dest docs/help.md → docs/guide.md → docs/最終.md
FALSIFIED 720fcfe3d178 timeout 10 to 30
FACT HOOK_TIMEOUT: 10 → 30
```

Dest-line slip after a heading prepend: old `FILE:LINE` on the new heading is `none` (`# Guide`). The leftover sentence one line down still names the fact. The dead name is still `missing`. tinder slips onto dest-file text after follow. smolder cannot be asked at the name the leftover used to have.

**The dest-moved leftover is leftover-name, not dest recency.** Fixture: dest still claims `"timeout": 10` (still true), dest is `git mv`'d into `docs/`, later a test quote tweaks `"toy hook-post-tool"` → `"toy' hook-post-tool"`:

```
$ ./smolder -C dest-hungry docs/hooks.md:1
smolder: leftover  docs/hooks.md:1
CLAIM { "command": "toy hook-post-tool", "timeout": 10 }
FALSIFIED b186ecd1da63 tweak quote in test string
STR "toy hook-post-tool" → "toy' hook-post-tool"   tests/e2e/init.test.ts:1   score 96
         why: same-line-name, old-string, claim:docs
# rc=0

$ ./tinder -C dest-hungry docs/hooks.md:1
tinder: none  docs/hooks.md:1  dest hooks.md → docs/hooks.md
  no falsifying fact mutation found for this leftover claim.
# rc=1
```

Default `--kinds` includes `string`. The dest line leftover-matches a quote. That is haunt/wraith on dest *text*, inverted. The timeout claim is still true.

Gold kizu dest leftover that *moved* (`4e37f16` into `docs/`):

```
$ git -C kizu log -S 10 --oneline -- docs/deep-research-ai-agent-hooks.md
4e37f16 fix(ui): use char-aware truncation …

$ ./smolder --no-color --explain --no-hunk -C kizu docs/deep-research-ai-agent-hooks.md:84
smolder: leftover  docs/deep-research-ai-agent-hooks.md:84
CLAIM { "command": "kizu hook-post-tool", "timeout": 10 }
FALSIFIED a75d4ea62b61 refactor: branch cleanup — dedupe, dead code, TOCTOU, hot-path clone
STR "kizu hook-post-tool" → "kizu' hook-post-tool"   tests/e2e/init.test.ts:46   score 96

$ ./smolder -C kizu deep-research-ai-agent-hooks.md:84
smolder: missing  deep-research-ai-agent-hooks.md:84
# rc=1

$ ./tinder -C kizu docs/deep-research-ai-agent-hooks.md:84
tinder: none  … dest deep-research-ai-agent-hooks.md → docs/…
  { "command": "kizu hook-post-tool", "timeout": 10 }
# rc=1
```

smolder does **not** name rename `4e37f16` (whole-repo pickaxe). It names leftover-name `a75d4ea`. The dest line still claims `"timeout": 10`, which is still true of the installer. Dead dest name is `missing`. tinder follows dest identity and then refuses the string kind: **none**.

A dest-only copy (no R record) leftover-claims the same timeout 10; both tools name the fact. Copy is not the hole.

Not a one-line fix: dest identity is R records (tinder/berth). Default kinds must not treat dest leftover as a hungry string. `--follow` that is `git log --follow` is blob identity (ditto), not dest-file identity.

---

## 2. Generated lockfile leftover blames a comment (conceptual, load-bearing)

Named lockfile dest is ash. That advertised win holds:

```
$ ./smolder -C lock-ash Cargo.lock:6
smolder: ash  Cargo.lock:6
regenerate  cargo (Cargo.lock — lockfile)
# rc=0   excerpt is version = "0.7.0"; no FALSIFIED
```

kizu `Cargo.lock:168` is the same `regenerate cargo`. Invert of cinder dest status applies to dest *and* to origin: a Cargo.toml + Cargo.lock bump still names Cargo.toml.

The invert hole is the other object: **a believer leftover of a lockfile-only bump**. Lockfile origin is skipped (`is_cinder_path` / `LOG_EXCLUDES`). If nothing else moved the fact, dest prose is honest `none` (`lock-only` README `crate version 0.3.0`). If a later *comment* binds the same `version`, the leftover names the comment:

```
# lockfile regen 0.3.0 → 0.7.0 (Cargo.toml still 0.3.0)
# then src/lib.rs  // version = "0.3.0"  →  // version = "0.7.0"

$ ./smolder -C lock-ash README.md:1
smolder: leftover  README.md:1
CLAIM plugin version 0.3.0
FALSIFIED 51736c39bc34 comment now says 0.7.0
FACT version: 0.3.0 → 0.7.0   src/lib.rs:1   score 84
```

The generated lockfile *was* the change that left `0.3.0` behind. Ash origin skip made that commit factless. The comment is the only remaining binding. Dest lockfile banner (`Cargo.lock:1`) still says regenerate — dest ash is fine. Believer dest of an ash-only bump is either silent or a blamed comment.

Unrecognized lock-shaped dest (`constraints.txt` `toy==0.3.0 → toy==0.7.0`): dest and leftover README are both `none`. `PAIR_RE` does not parse `==`. Not ash, not a fact. A custom lockfile is invisible as origin *and* as dest.

---

## 3. October is timeout 10 when the dest line names timeout (conceptual)

Advertised ISO case survived. `CHANGELOG.md` `shipped 2024-10-01` under `## timeout` is `none`. `timeout shipped 2024-10-01` is `none`. `timeout shipped 2024.10.01` is `none` (version-dot lookaround `(?<![\d.])10(?![\d.])`). Real leftover `timeout default is 10` still names `HOOK_TIMEOUT: 10 → 30`.

`CALENDAR_RE` only blanks `\d{4}-\d{2}-\d{2}` and `\d{4}/\d{2}/\d{2}`. Nearby `## timeout` is used for *scoring*, not for *seeding*. A date-only dest line does not seed integer 10 (common number, dest line does not name a value). Pickaxe never sees the timeout commit. That is why heading-plus-date survived.

The dest line that *names* timeout and writes October as a date the mask does not know is leftover timeout 10:

```
$ ./smolder -C october-named docs/us.md:1
CLAIM timeout shipped 10/01/2024
FALSIFIED b07bcadfdd93 timeout 10 to 30
FACT HOOK_TIMEOUT: 10 → 30   src/config.py:1   score 62
         why: name-stem, old-value, claim:docs

$ ./smolder -C october-named docs/oct.md:1
CLAIM timeout on October 10, 2024
FACT HOOK_TIMEOUT: 10 → 30

$ ./smolder -C october-named docs/dmy.md:1
CLAIM timeout shipped 10-01-2024
FACT HOOK_TIMEOUT: 10 → 30
```

ISO / dotted-version on the same tree stay `none`. The calendar object is a pair of regexes, not a date. US `10/01/2024`, `10-01-2024`, and English `October 10` are month 10 with a timeout stem on the same line. That is the zanei date hole, inverted: dest seeds `10` because the line says `timeout`, then leftover-matches the month.

A one-character class add would hide `10-01` and would not decide what a date is. Not applied.

---

## 4. Two packages named `version` are one noun (conceptual, lethal to workspace leftovers)

```
pkg_a/Cargo.toml  0.3.0 → 0.7.0
pkg_b/Cargo.toml  version = "0.3.0"          # still true of pkg_b
pkg_b/README.md   pkg_b version 0.3.0
```

```
$ ./smolder -C workspace pkg_b/README.md:1
CLAIM pkg_b version 0.3.0
FALSIFIED f40a7c1cfa2a bump pkg_a only to 0.7.0
FACT version: 0.3.0 → 0.7.0   pkg_a/Cargo.toml:3   score 84

$ ./smolder -C workspace pkg_b/Cargo.toml:3
CLAIM version = "0.3.0"
FALSIFIED f40a7c1cfa2a bump pkg_a only to 0.7.0
FACT version: 0.3.0 → 0.7.0   pkg_a/Cargo.toml:3   score 103
         why: same-line-name, old-value, claim:config, version-config
```

`pkg_a/README.md` already says `0.7.0`: honest `none`. The leftover that is still true (`pkg_b` is 0.3.0) is scored *higher* as config (`version-config` +15). Gold kizu plugin.json is this story *without* workspace identity, and it is the intended win. Two crates named `version` cannot tell which package the dest leftover is about. CANDIDATE already listed this. Confirmed, and dest `pkg_b/Cargo.toml` is not a docs ghost — it is the live binding of the other package.

---

## 5. `vendor/` skip — `SKIP_DIRS` is dead; vendor dest is a believer (conceptual)

`SKIP_DIRS` includes `vendor`, `dist`, `node_modules`. It is never read. Invert walk is explicit `FILE:LINE` plus `git log -S` over `.`. Vendor is not in `LOG_EXCLUDES` or `CINDER_DIR_NAMES`.

CANDIDATE said vendor stays skip-invisible as a falsifying origin. The opposite is true. Vendor-only `TIMEOUT 10 → 30` in `vendor/bundle.js`, source untouched:

```
$ ./smolder -C vendor README.md:1          # at e6e42d5 vendor-only
CLAIM timeout default is 10
FALSIFIED e6e42d5d446e vendor-only timeout 10 to 30
FACT TIMEOUT: 10 → 30   vendor/bundle.js:1   score 84
```

Vendored dest leftover of a *source* bump is a believer, not ash:

```
$ ./smolder -C vendor-dest vendor/pkg/index.js:1
CLAIM const TIMEOUT = 10; // do not edit, vendored
FALSIFIED 389b53e4049a source+docs 10 to 30, vendor leftover
FACT TIMEOUT: 10 → 30   src/config.py:1   score 72
         why: same-line-name, old-value, claim:code
```

`// do not edit, vendored` does not trip `CINDER_BANNER_RE` (`generated` is required). The invert says: edit this leftover claim; here is the commit. The file is leftover *build*.

Same class: `dist/app.js` and `third_party/bundle.js` (`.gitattributes linguist-generated=true` unread) are believers. `docs/generated/CONTRACTS.md` is ash because a path component is `generated` — a human contracts leftover under `docs/generated/` answers regenerate. `generated_helpers.py` (stem starts with `generated`) is ash. `src/oracle.py` (filename, not directory `oracle/`) is a believer.

Ash vs believer is a directory/banner/stem table, not generated-ness. Both directions fire.

---

## 6. 2 MB dest is `missing`, not omit (operational + conceptual)

`read_dest_text` (`smolder:1257`): `st_size > 1_500_000` → `None`. `main` prints `smolder: missing  path:line` and JSON `status: "missing"`. The leftover is on disk.

Tiny git history, dest written in the worktree after the fact commit (so pickaxe is not walking 2 MB blobs):

| dest | bytes | result |
| ---: | ---: | --- |
| `docs/ok.md:1` | 22 | leftover, `HOOK_TIMEOUT 10 → 30` |
| `docs/mid.md:1` | 1_400_022 | leftover, same fact |
| `docs/over.md:1` | 1_600_022 | **`missing`** rc=1 |
| `docs/god.md:1` | 2_000_022 | **`missing`** rc=1 |

```
$ ls -l fixtures/god-wt/docs/god.md
-rw-r--r--  2000022  …/docs/god.md

$ ./smolder --json -C god-wt docs/god.md:1
"status": "missing", "action": "none"
# rc=1
```

No warning. The file exists. The leftover sentence is line 1. The invert answers “that path is not here.” Same class as pin’s 1 MB godfile omit, inverted: dest load, not dest walk. A committed 2 MB sibling also makes `git log -S` on a *small* dest hang on the huge blobs (godfile repo with 5 MB of history: `docs/ok.md:1` did not return in 120s). Size-cap on dest read plus unbounded pickaxe on sibling blobs.

---

## 7. Japanese *as the binding* — aliases only search (conceptual)

ASCII `HOOK_TIMEOUT = 10 → 30`, leftover `タイムアウトは 10 秒です`: **hit**, score 62, `name-stem`. That advertised alias path survived.

Japanese *as the changed line* extracts nothing. `IDENT_RE` / `PAIR_RE` keys are Latin. `タイムアウト = 10 → 30`:

```
$ ./smolder -C japanese docs/ja.md:1
smolder: none  docs/ja.md:1
  タイムアウトは 10 秒です。

$ ./smolder -C japanese docs/en.md:1
smolder: none  docs/en.md:1
  timeout default is 10

$ ./smolder -C japanese docs/bind.md:1
smolder: none  docs/bind.md:1
  タイムアウト = 10

$ ./smolder -C japanese docs/fw.md:1
smolder: none  docs/fw.md:1
  TIMEOUT = １０
```

All rc=1. The dest leftover is sitting on disk. Pickaxe of dest seeds (`タイムアウト` is not an ident; `10` may seed) does not recover a typed fact from the origin hunk. Fullwidth `１０` is not integer 10 (`needle_in_line` is ASCII digits). Japanese rename `最大リトライ → 最大試行` plus `3 → 8`: dest `最大リトライは 3 です` is `none`.

Unicode *filenames* (`docs/最終.md`) round-trip on the live path. Paths are not the hole. Bindings are. Same object as DESTROYER_ZANEI §4, inverted: dest Japanese of an English fact matches; origin Japanese is not a fact.

---

## 8. Ash vs believer — table, not generated-ness (conceptual)

| dest | ash? | invert |
| --- | --- | --- |
| kizu `Cargo.lock:168` | ash | regenerate cargo |
| `generated/README.md` | ash | regenerate (path) |
| `oracle/timeout.json` | ash | regenerate (oracle) |
| `src/schema.gen.ts` | ash | regenerate (`.gen.ts`) |
| `docs/generated/CONTRACTS.md` | **ash** | regenerate — human leftover under `generated/` |
| `generated_helpers.py` | **ash** | regenerate — stem starts with `generated` |
| `src/oracle.py` | believer | FALSIFIED source — filename `oracle.py`, not dir `oracle/` |
| `vendor/out.js` | believer | FALSIFIED source |
| `dist/app.js` | believer | FALSIFIED source |
| `third_party/bundle.js` | believer | FALSIFIED source — `.gitattributes linguist-generated` unread |
| `docs/Cargo.lock.example` | believer | FALSIFIED plugin.json `0.3.0 → 0.7.0` — lock-shaped, not a lockfile name |
| `plugin.json:2` after bump | none | origin now holds the new value |

Ash dest never prints `FALSIFIED` / “edit this line.” That half of the primitive holds for the table. The table is not the repo. Over-ash turns a docs leftover into regenerate. Under-ash turns leftover *build* into a blamed source commit.

---

## What survived

- Gold **kizu** `plugin/plugin.json:4` → `53cbd1a` Cargo.toml `0.3.0 → 0.3.1` score 103. `git blame` on that line is still `bff820fb` (when the leftover was written). Those are different objects. That is still the “why doesn’t this exist?” moment.
- Gold **kizu** `Cargo.lock:168` → `regenerate cargo`. No `FALSIFIED`.
- Gold **sitbone** `CLAUDE.md:329` → `e9b0f75` `threshold 0.4 → 0.45` PresenceArbiter.
- JSON-only quoted `version` is a named fact (full token, not `0.3`). Self-test + demo path still green.
- ISO `2024-10-01` and `2024.10.01` are not leftover timeout 10. Real `timeout default is 10` still resolves.
- Live dest after 100% `git mv` names the **fact** commit, not path-limited dest recency.
- Empty `--kinds` / no locators: exit 2. Usage fail-closed.
- `self-test` 0 after the battery. Victim not rewritten.

---

## Kill / keep

**Keep. Mutate. Do not rewrite in this pass.**

The object is still “this leftover claim, which commit made it false?” Ash dest still says regenerate. Gold kizu plugin.json and sitbone CLAUDE.md come out. October-as-ISO is not timeout 10. Killing smolder because dest:84 is leftover-name, or because `pkg_b` shares the noun `version`, would throw away the invert to hide a kinds/identity table. tinder already peeled dest-file identity; it is the mutation, not the kill.

| do not kill because | mutate toward |
| --- | --- |
| kizu plugin.json `53cbd1a` Cargo.toml, not blame / not lock; sitbone `e9b0f75` 0.4→0.45; named lockfile dest regenerate | **Dest leftover is a typed claim.** Default kinds `value,rename,polarity`. String is opt-in. kizu dest:84 / dest-hungry quote tweak must be **none** (timeout still 10), not `STR "kizu hook-post-tool"`. |
| Live dest after `git mv` already names the fact (whole-repo pickaxe skips 100% rename) | **Dest identity is R records, then the fact.** Dead `docs/help.md:1` follows to the live holder. Do not name dest recency. Copy has no R. |
| ISO date dest is none; real timeout leftover found | **Dates are not old integers** even when the dest line says `timeout`. Mask US / `October 10` / `10-01-2024`, or refuse to seed `10` from a calendar token. |
| Cargo.lock dest regenerate; Cargo.toml+lock names Cargo.toml | **Lockfile-only bump is still a fact** for believer dest, or dest leftover of an ash-only change is `none` *without* blaming a later comment binding. Do not skip ash origin and then leftover-match `// version`. |
| | **Workspace identity.** `pkg_a` 0.3.0→0.7.0 does not falsify `pkg_b` 0.3.0. Gold kizu plugin.json is one product, not two packages. |
| | **Ash is generated-ness**, not `generated` in the stem / a `docs/generated/` path / unread `.gitattributes`. `vendor/` `dist/` `third_party/` dest is leftover build (regenerate or skip-visible), not a believer. `generated_helpers.py` and `docs/generated/CONTRACTS.md` can be leftovers. |
| | **Japanese bindings are facts** or they are not. `タイムアウト = 10 → 30` must extract if leftover Japanese of English timeout is already a hit. Fullwidth `１０` is `10`. |
| | **Size-cap dest is omit-visible**, not `missing`. `docs/god.md` exists. Exit 2 or print `omit`, never “path not here.” Pickaxe must not hang on sibling 2 MB blobs. |

A one-line `SKIP_DIRS` consult on origin paths would hide vendor-as-origin and would not touch dest:84 leftover-name, `pkg_b` version, or `timeout shipped 10/01/2024`. Not applied.

Do not grow a review platform. The next mutation is dest-file identity then a *typed* leftover claim (tinder’s peel), plus workspace identity and a date that is not integer 10 — not a smarter `git log -S`.
