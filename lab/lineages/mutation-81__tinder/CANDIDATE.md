# mutation-81 — tinder

## Primitive

Given a leftover dest locus (`FILE:LINE` or stdin locators), `--follow` the leftover across **dest-file identity** (berth/slip), then emit the commit that falsified the **fact**. Ash answers **regenerate**. A dest-only rename is not a falsifier.

smolder inverts leftover: dest locus in, falsifying commit/hunk out. Hole: leftover that **moved with a dest-file rename** still names the rename (`git log -S leftover -- dest/newpath`), not the fact-falsifying commit.

Not leftover-name search. `FILE:LINE` is legal input. Honor generated dest (ash/regenerate). October is not timeout 10.

## Why this might not exist

`git blame` names who last wrote the leftover (often the dest author). `git log -- dest/newpath` after `git mv` names **only the rename**. `git log -S leftover -- dest/newpath` names the rename because the token *appeared* on that path. smolder's whole-repo pickaxe skips the 100% rename, then leftover-matches the dest line as a hungry string. berth occupies dest identity but does not invert a claim. slip rewrites a locator but does not name a fact.

The missing verb is: **this leftover, which moved with the dest file, which commit made the fact false?**

Discarded as concatenation: `git log --follow -S leftover -- dest` plus smolder. That still names dest recency or leftover-name, never dest identity *then* a typed fact.

## How to run

From this worktree (Python 3.9+, `git` on `PATH`, no other deps):

```bash
chmod +x ./tinder ./demo.sh
./tinder self-test
./demo.sh
./tinder --help
./tinder -C <repo> path/to/file:LINE
./tinder -C <repo> old-name.md:7
./tinder --no-follow -C <repo> old-name.md:7
printf 'README.md:7\n' | ./tinder -C <repo>
```

Exit `0` found (falsifier or regenerate), `1` none, `2` usage/error.

## Empirical transcript

### Before the improvement (v0.1)

Dest-rename fixture: fact `HOOK_TIMEOUT 10 → 30`, then `git mv docs/help.md docs/guide.md`. Path-limited pickaxe names the rename. tinder on either name names the fact commit. `--no-follow` on the dead name is missing. 3-hop CJK dest still follows. Ash dest that moved still says regenerate.

Gold still holds: kizu `plugin/plugin.json:4` → `53cbd1a` Cargo.toml `0.3.0 → 0.3.1`. sitbone `CLAUDE.md:329` → `e9b0f75` `0.4 → 0.45`. tenaoshi `OraclesGenerated.swift:1` → regenerate `tools/spec-gen.ts`. October none.

Wrong dest identity, forced by that run:

1. **Copy is follow.** `cp docs/最終.md docs/copy.md` — `git log --follow` walks the *blob*, so `copy.md` identity still listed `docs/help.md`. Copy is not a dest-file rename (no R record).
2. **kizu dest leftover that moved is leftover-name.** `docs/deep-research-ai-agent-hooks.md:84` (and the dead `deep-research-ai-agent-hooks.md:84`) follows dest identity (`deep-research-ai-agent-hooks.md → docs/…`) and does **not** name rename `4e37f16`. It names `a75d4ea` `STR "kizu hook-post-tool" → "kizu' hook-post-tool"` from `tests/e2e/init.test.ts`. The dest line still claims `"timeout": 10`, which is still true of the installer. That is leftover-name, not a fact-falsifier.
3. Dest rewrite after the move (heading prepended) keeps the old `FILE:LINE` on the new heading.

`./demo.sh` → passed=116 failed=0 (copy assertion dropped so v0.1 could ship).

### After the improvement (v0.2)

Forced by that dest-copy JSON and the kizu dest:84 transcript, not a feature list:

1. **Dest identity is R records (berth), not `git log --follow`.** Copy has no R; `docs/copy.md` identity is itself. Query the old name still walks `help.md → guide.md → 最終.md`.
2. **Dest leftover is a typed claim.** Default kinds `value,rename,polarity`. String is opt-in. dest:84 is **none** (timeout still 10), not a quote tweak.
3. **Dest-line slip.** Dead `docs/help.md:1` after a heading prepend lands on the leftover sentence, not `# Guide`.

```
$ ./tinder --no-color --no-hunk -C kizu plugin/plugin.json:4
tinder: leftover  plugin/plugin.json:4

CLAIM "version": "0.3.0",
  plugin/plugin.json:4

FALSIFIED 53cbd1a055f5 chore: bump version to 0.3.1
FACT version: 0.3.0 → 0.3.1   Cargo.toml:3   score 103
```

```
$ ./tinder --no-color --no-hunk -C kizu docs/deep-research-ai-agent-hooks.md:84
tinder: none  docs/deep-research-ai-agent-hooks.md:84  dest deep-research-ai-agent-hooks.md → docs/deep-research-ai-agent-hooks.md
  { "command": "kizu hook-post-tool", "timeout": 10 }
  no falsifying fact mutation found for this leftover claim.
# exit 1
```

Same locator on the dead name follows to the same none. `--no-follow` on the dead name is `missing`. `git log -S 10 -- docs/deep-research-ai-agent-hooks.md` is still `4e37f16`.

```
$ ./tinder --no-color --no-hunk -C sitbone CLAUDE.md:329
tinder: leftover  CLAUDE.md:329

CLAIM @Test("… threshold 0.4）")
  CLAUDE.md:329

FALSIFIED e9b0f75deabd Implement dual-threshold hysteresis in PresenceArbiter
FACT threshold: 0.4 → 0.45   Sources/SitboneCore/PresenceArbiter.swift:30   score 84
```

Dest-rename fixture: new name, dead name, 3-hop CJK, dest-line slip, copy-is-not-follow, ash dest rename. October after dest rename still none on the date line.

`./demo.sh` → passed=127 failed=0. `./tinder self-test` 0.

## Dogfood targets

| Target | What was run | Outcome |
| --- | --- | --- |
| dest-rename fixture | `docs/guide.md:1` after `git mv` | fact `10→30`, not rename sha. Path-limited pickaxe names the rename |
| dead dest name | `docs/help.md:1` | follows; same fact. `--no-follow` missing |
| 3-hop CJK dest | `help.md` → `guide.md` → `最終.md` | same fact, live holder `最終.md` |
| dest copy | `docs/copy.md:1` | v0.1 identity listed help.md; v0.2 copy is not dest identity |
| dest-line slip | dead `help.md:1` after heading prepend | v0.2 slipped onto leftover sentence |
| ash dest rename | `generated/vendor_bundle.js` → `generated/out.js` | regenerate, never FALSIFIED |
| kizu `plugin/plugin.json:4` | gold | **53cbd1a Cargo.toml 0.3.0→0.3.1**, not Cargo.lock |
| kizu `Cargo.lock:168` | gold ash | regenerate cargo |
| kizu dest leftover that moved | `:84` new + dead name | v0.1 hungry string `a75d4ea`; v0.2 **none** (timeout still 10). Not `4e37f16` |
| sitbone `CLAUDE.md:329` / `:332` | gold | **e9b0f75 0.4→0.45 PresenceArbiter** |
| tenaoshi `OraclesGenerated.swift:1` | ash | regenerate `tools/spec-gen.ts` |

## Surprises

- The dest-rename lie is **path-limited pickaxe**, not whole-repo pickaxe. `git log -S 10 -- docs/guide.md` names the rename because the token appeared on that path. smolder already walks `-- .`; its dest-rename hole on kizu was leftover-name of the dest line after follow, not dest recency.
- `git log --follow -- dest/copy.md` is blob identity. That is ditto's COPY, not berth's R. v0.1 inherited the blob walk.
- kizu dest:84 following dest identity and *not* naming `4e37f16` is not enough. A still-true `"timeout": 10` must be none. Naming `a75d4ea`'s quote tweak is haunt/wraith on dest text.
- dest-line slip is dest-file text, not leftover-name search of the tree. October on a neighboring dest line still does not steal timeout 10.

## Failures

- No language parser. Historical dest via `--rev` does not recurse nested repos. Japanese *as the binding* still does not parse; leftover Japanese of an English fact still matches via alias. Fullwidth `１０` is not `10`.
- Dest-path reincarnation (delete, later a new file at the old name, then rename) can still join lives if an R old-name matches the asked path. berth's commit-ordered occupancy is stricter.
- A dest split (`src/git.rs` → `parse.rs`) is tenure, not dest-file identity. tinder does not follow it.
- Default kinds drop string. A dest leftover that only leftover-matches a string fact needs `--kinds …,string`.
- `--max-commits` 80 / `--limit` 1 omit silently. Size-cap omit of a 2 MB dest is still silent.
- `vendor/` stays skip-invisible as a falsifying origin.
- Two packages named `version` are one noun.

## Suggested mutations

- Workspace identity so `pkg_a` 0.3.0→0.7.0 does not accuse `pkg_b`.
- Learn generated-ness from the repo (`just spec-gen`, `.gitattributes linguist-generated`) instead of a directory/banner table.
- Dest occupancy: how long HEAD has held the leftover *after* dest identity settled.
- First-parent merge that added dest as A (no R on the walk) should still follow from all-reachable R records (rove already did this for grep).

## Kill / keep

**Keep.** The object changed. smolder's default is leftover locus → falsifying commit, and a dest that moved still names dest recency or leftover-name. tinder's default is dest-file identity then the *fact*. Gold kizu plugin.json and sitbone CLAUDE.md come out. kizu dest leftover that moved is none (not `4e37f16`, not `a75d4ea`). October is not timeout 10. Ash dest that moved still says regenerate. Kill only if a later generation proves `git log --follow -S` plus smolder is the same object — it is not: path-limited pickaxe names `4e37f16`, smolder names `a75d4ea`, tinder names none or the fact.
