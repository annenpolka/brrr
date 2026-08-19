# mutation-63 — smolder

## Primitive

Given a leftover dest locus (`FILE:LINE` or stdin locators), emit the **diff (commit) that falsified the claim**. Ash answers **regenerate**.

Forward tools (zanei / ember / cinder) take a diff and print leftover afterimages. smolder inverts: leftover in, falsifying change out. A *fact* is a typed bound name/value, rename, or polarity flip (ember). Honor cinder dest status: `generated/`, `oracle/`, lockfile-regenerated dest, `*.generated.*`, `@generated` banner is leftover *build* — name the generator if you can, never "edit this line". A believer leftover names the falsifying commit and origin hunk.

Not leftover names (haunt / wraith). `FILE:LINE` is legal **input**.

## Why this might not exist

`git blame` answers who last *touched the leftover line*. That is the last editor of the stale sentence, not the change that made it false. `git log -S` answers when a token's count moved, without typing the fact (October is integer 10; `0.3.0` truncates; a lockfile regen looks like a version bump). cinder answers "what else still believes this diff?" and even suggested `cinder blame <path>:<line>` as the invert — it was not built.

The missing verb is: **this leftover claim, which commit made it false?** Ash must not produce an edit.

## How to run

From this worktree root (Python 3.9+, `git` on `PATH`, no other deps):

```bash
chmod +x ./smolder ./demo.sh
./smolder self-test
./demo.sh                 # exits 0; fixtures + gold kizu/sitbone if present
./smolder --help
./smolder -C <repo> path/to/file:LINE
printf 'README.md:7\n' | ./smolder -C <repo>
git diff A B | ./smolder --diff - -C <repo> leftover.md:3
```

Exit `0` found (falsifier or regenerate), `1` none, `2` usage/error.

## Empirical transcript

### Before the improvement (v0.1)

Toy fixture, implementation changed, claims left behind. Uncommitted dest names `WORKTREE`; after commit, the leftover names that commit and the origin hunk.

```
$ ./smolder --no-color --no-hunk -C fixtures/.run/toy README.md:7
smolder: leftover  README.md:7

CLAIM plugin version 0.3.0, hook timeout 10 seconds.
  README.md:7

FALSIFIED <sha> change facts, forget the claims
FACT version: 0.3.0 → 0.7.0   plugin.json:3   score 84
```

JSON-only quoted `"version": "0.3.0" → "0.7.0"` still resolves dest prose `plugin version 0.3.0` (full token, not nagori's `0.3`). Adjacent `package-lock.json` is **ash** (`regenerate  npm`), not a blamed comment.

Ash plant: `Cargo.lock:6` → `regenerate  cargo`. `OraclesGenerated.swift:1` → `regenerate  tools/spec-gen.ts`. `generated/vendor_bundle.js` and `hook_bundle.js` say regenerate, never `FALSIFIED`. README leftover on the same tree still names the timeout bump.

Destroyer dates: `CHANGELOG.md:2` `shipped 2024-10-01` under `## timeout` → **exit 1 none**. `docs/help.md:1` `timeout default is 10` on the same tree → `HOOK_TIMEOUT: 10 → 30`.

Gold kizu / sitbone:

```
$ ./smolder --no-color --no-hunk -C kizu plugin/plugin.json:4
smolder: leftover  plugin/plugin.json:4

CLAIM "version": "0.3.0",
  plugin/plugin.json:4

FALSIFIED 53cbd1a055f5 chore: bump version to 0.3.1
FACT version: 0.3.0 → 0.3.1   Cargo.toml:3   score 103
```

`Cargo.lock:168` `version = "0.3.0"` → `regenerate  cargo`. `plans/v0.3.md:103` leftover still resolves to the same Cargo.toml bump.

```
$ ./smolder --no-color --no-hunk -C sitbone CLAUDE.md:329
smolder: leftover  CLAUDE.md:329

CLAIM @Test("カメラのみpresent → 総合present（weight 0.50 > threshold 0.4）")
  CLAUDE.md:329

FALSIFIED e9b0f75deabd Implement dual-threshold hysteresis in PresenceArbiter
FACT threshold: 0.4 → 0.45   Sources/SitboneCore/PresenceArbiter.swift:30   score 84
```

`./demo.sh` → `passed=80 failed=0`.

v0.1 hole: a dest line that leftover-claims *two* facts from the same commit (`タイムアウトは 10 秒です。MAX_RETRIES はまだ 3 のまま。`) only printed the higher-scoring rename. The timeout 10→30 on that line was silent.

### After the improvement (v0.2)

Emit **every** leftover claim the dest line still asserts from that falsifying commit, not only `max(score)`.

```
$ ./smolder --no-color --no-hunk -C toy 日本語コメント.md:3
smolder: leftover  日本語コメント.md:3

CLAIM タイムアウトは 10 秒です。MAX_RETRIES はまだ 3 のまま。
  日本語コメント.md:3

FALSIFIED <sha> change facts, forget the claims
RENAME MAX_RETRIES → MAX_ATTEMPTS   src/retry.py:3   score 92
FACT MAX_RETRIES: 3 → 8   src/retry.py:3   score 84
FACT HOOK_TIMEOUT: 10 → 30   src/retry.py:4   score 62
```

Same for the destroyer prose sentence — v0.1 showed only the version token; v0.2 also names the timeout on that line:

```
CLAIM plugin version 0.3.0, hook timeout 10 seconds.
FACT version: 0.3.0 → 0.7.0   plugin.json:3   score 84
FACT HOOK_TIMEOUT: 10 → 30   src/retry.py:4   score 62
```

Gold kizu / sitbone / ash regenerate / October-none unchanged. `./demo.sh` → `passed=83 failed=0`.

## Dogfood targets

| Target | What was run | Outcome |
| --- | --- | --- |
| `fixtures/toy` | worktree + committed `FILE:LINE` | WORKTREE then named commit; rename / timeout / polarity / JSON version; v0.2 dual claims on one line |
| `fixtures/ash` | lockfile / generated / oracle / banner / README | **regenerate** cargo/npm/spec-gen.ts; docs leftover still a believer |
| destroyer JSON hunk | README `plugin version 0.3.0` vs quoted plugin.json bump | **full token**; lockfile ash |
| destroyer dates | `CHANGELOG.md:2` vs `docs/help.md:1` | October none; real timeout leftover found |
| kizu `plugin/plugin.json:4` | current worktree | **53cbd1a Cargo.toml 0.3.0→0.3.1**, not Cargo.lock |
| kizu `Cargo.lock:168` | current worktree | **regenerate cargo** |
| kizu `plans/v0.3.md:103` | current worktree | same Cargo.toml falsifier |
| sitbone `CLAUDE.md:329` / `:332` | current worktree | **e9b0f75 0.4→0.45 PresenceArbiter** |

## Surprises

- `git blame` on kizu `plugin.json:4` names `bff820fb` (when the leftover was *written*). The falsifier is `53cbd1a` (when Cargo.toml left `0.3.0`). Those are different objects. That is the "why doesn't this exist?" moment.
- Pickaxe of the name `timeout` does not see `HOOK_TIMEOUT = 10 → 30` (the token count of "timeout" is unchanged). The dest *claim* has to seed the bound integer when the line names timeout — calendar-masked, so October still does not seed `10`.
- A commit that bumps crate version rewrites Cargo.lock first in the patch. Deduping facts by `(kind,name,old,new)` without skipping ash origins made the lockfile *eat* the Cargo.toml fact. Invert of cinder dest status has to apply to the **origin** too.

## Failures

- No language parser. Historical dest via `--rev` does not recurse nested repos. Japanese *as the binding* still does not parse (`タイムアウト = 10` is not extracted as a fact); leftover Japanese of an *English* fact still matches via alias.
- Two packages named `version` are one noun (workspace identity, same as cinder).
- Size-cap omit of a 2 MB dest file is still silent.
- `vendor/` stays skip-invisible as a falsifying origin (DESTROYER hole cinder also left).

## Suggested mutations

- Workspace identity so `pkg_a` 0.3.0→0.7.0 does not accuse `pkg_b`.
- Learn generated-ness from the repo (`just spec-gen`, `.gitattributes linguist-generated`) instead of a directory/banner table.
- `--follow` a leftover across dest-file renames (slip/pin) then still name the falsifying *fact* commit, not the rename of the stale file.

## Kill / keep

**Keep.** The invert is a new Unix verb (leftover locus in, falsifying commit/hunk out, ash says regenerate). Gold kizu plugin.json and sitbone CLAUDE.md come out. October is not timeout 10. JSON-only `plugin version 0.3.0` still resolves. A generated lockfile leftover does not blame a comment.
