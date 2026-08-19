# hybrid-05 — tenure

## Primitive

A path-condition occupies history. Given `FILE:LINE`, reconstruct the nested predicates still in force (`when`), then walk git emitting eras of **this stack held** plus **who sat in it**. Same TRUE, different occupants → a new era.

Not `when | held`. held/perch grep tokens. The if-text lives on the guard. Occupancy is the lines that run under the stack. Files that still *mention* a token without sitting in the stack are echoes, not holders.

## Why this might not exist

Reviewers ask two questions at once and get two tools. `when parse.rs:60` says the line is legal after four early-return givens. `perch grep isEnabled` says that token is TRUE in two Swift files. One of those files is `arbiter.isEnabled = …`. It never runs under `guard isEnabled`.

The missing object is the **tenure of the stack**: intervals where that condition obtained, split when the occupant set changed, with a name for bystanders. Ancestor `held` compresses a boolean. `perch --boolean` is that ancestor for greps. `tenure --boolean` is that ancestor for a path-condition.

Discarded as concatenation: `when FILE:LINE | perch grep <pred-text>`, or running `when` at each checkout. That is two reports. The join is one occupancy.

## How to run

```bash
chmod +x ./tenure
./tenure --selftest
./demo.sh
./tenure -C /Users/annenpolka/ghq/github.com/annenpolka/kizu src/git/parse.rs:60
./tenure -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone Sources/SitboneCore/PresenceArbiter.swift:81
./tenure --boolean --grain files FILE:LINE
```

Python 3.10+, stdlib only, git. Vendored `whenline` parsers from candidate-20. Exit 0 if the stack holds at the last sample.

## Empirical transcript

### Before the improvement (commit `47c02b7`)

Synthetic fixture already split `given ready | if x > 0` the way perch splits TOKEN_B: occupancy never died; holders `src/app.py:process` → `src + tests` → tests-only ghost. `--boolean` recovered `FT`. `--grain loci` split the sibling body line that functions grain ignored.

kizu `src/git/parse.rs:60` — four fallthrough givens. Occupancy is one TRUE island (22/24 first-parent). Holders move with the function. `git log -- src/git/parse.rs` is one commit; the stack occupied `git.rs` for 17.

```
FALSE  2 commits
TRUE  17 commits  holders: src/git.rs:parse_diff_git_header
TRUE   5 commits  holders: src/git/parse.rs:parse_diff_git_header
       + src/git/parse.rs:parse_diff_git_header
       - src/git.rs:parse_diff_git_header
now=TRUE  true=22/24  eras=3  boolean=2  holder_splits=1  probes=232
```

sitbone `PresenceArbiter.swift:81` — `guard isEnabled`. Functions grain was one TRUE island, one holder. **Looked like held.**

```
FALSE  9 / TRUE 22
holders: Sources/SitboneCore/PresenceArbiter.swift:detect
```

`perch grep isEnabled` on the same repo named two files: `PresenceArbiter.swift, SitboneCore.swift`. Tenure occupants were only PresenceArbiter. v1 did not say so. 232 kizu probes came from seeding `starts_with`. Ghost era on the fixture named tests as holder and was silent that production now sits in `given enabled | given ready | if x > 0`.

### After the improvement (this commit)

Forced by sitbone `isEnabled`, not polish.

1. **Echoes.** A scanned file that does not occupy the pin is an echo: `mention` (token, no occupant) or `deeper` / `related` / `shallower` when its stacks share frames. Ghost era now names the deeper stack production moved into. sitbone now names the bystanders perch grep treated as holders.
2. **Seeds from condition frames, stop-listed methods.** `starts_with` no longer walks the tree. kizu probes 232 → 46.

Same fixture command, ghost era after production grew `enabled`:

```
TRUE   1 commit   holders: tests/test_app.py:test_process
       - src/app.py:process
       ghost: production left; the stack still perches in tests/docs
       echo   src/app.py:process  deeper  given enabled | given ready | if x > 0
now=TRUE  ghost_now=1
hint: src/app.py:process now sits in a deeper stack: given enabled | given ready | if x > 0
```

sitbone, same pin. Occupant unchanged. Echoes are the grep lie:

```
TRUE  22 commits  holders: Sources/SitboneCore/PresenceArbiter.swift:detect
       echo   Sources/SitboneCore/SitboneCore.swift  mention (token, no occupant)
       echo   Sources/SitboneSensors/SitboneSensors.swift  mention …
       echo   Sources/SitboneUI/NotchOverlay.swift  mention …
       echo   Tests/…  mention …
```

`SitboneCore.swift:355` is `arbiter.isEnabled = isCameraEnabled`. It never runs under `guard isEnabled`. perch's extra holder is tenure's first echo.

kizu move is unchanged as occupancy (still the money shot). Former `git.rs` is a dropped holder, not a mention echo. probes=46.

`--grain regions` on sitbone still splits the TRUE island when hysteresis was inserted above `detect()` (`:59-62` → `:64-67` → `:79-82`). That is line motion, not a new occupant; functions grain is the default for the same reason perch's default is files.

`./demo.sh` — 29 assertions, exit 0.

## Dogfood targets

| target | what we asked |
| --- | --- |
| synthetic fixture | birth, copy, extra body line, production guard-growth → ghost + deeper echo |
| `kizu/src/git/parse.rs:60` | four-given unquoted-form stack; file move `git.rs` → `parse.rs` |
| `sitbone/.../PresenceArbiter.swift:81` | `guard isEnabled` occupants vs `isEnabled` mentions |
| `sitbone/.../PresenceArbiter.swift:93` | deeper stack `guard isEnabled \| guard !active.isEmpty` |
| `perch grep isEnabled` / `b_prefix_start` | concat baseline: unique tokens accidentally agree, `isEnabled` does not |

Read-only on the real repos.

## Surprises

- The valuable kizu "when" is still the negation of the last four early returns. Tenure adds: that stack occupied `git.rs` for 17 first-parent commits, then moved. `when` is a snapshot; the snapshot's object has a tenure.
- Unique identifiers (`b_prefix_start`) make `when | perch grep` accidentally right. Common ones (`isEnabled`, `starts_with`) make it wrong. The sitbone miss is the proof the object is the stack, not the token.
- sitbone functions grain is supposed to look like held. The distinctive fact is the echo list. regions grain is perch `--grain lines`: insertion above `detect()` shifts the occupant span.
- Default grain is functions because regions on kizu fragment on every comment above the unquoted body (`git.rs:241-242` → `:466-467` → … → `parse.rs:59-60`).

## Failures

1. **Mention echoes are loud** on sitbone (tests + NotchOverlay + sensors). They are correctly not holders; they still flood the TRUE era. `--code` / `--no-echo` would help.
2. **`--rev` pins the worktree file** when it exists, so "stack as of that commit" needs a missing path. Historical pin is a mutation.
3. **`--prefix` match is not default.** Extra frames kill occupancy (correct for "this stack") and show up as deeper echoes instead. Asking "who still has at least these givens" is a different verb.
4. **Match-arm / `if let` pred quality** inherited from `when` (`len<5+ 2`, `if a_side!= b_side`).
5. **Full-history eras** follow `git log --reverse`, not a merge diamond.
6. **`exists`-style path identity** is not a tenure query. Rename without stack match is perch `--follow`.

## Suggested mutations

- `--echo no|mention|related` to quiet sitbone tests.
- `--rev` as the pin blob, not just the walk end.
- `--prefix` so extra frames still count as occupying a parent stack.
- Cache probes `(sha, cond_key, grain)`.
- Pipe from `when --scan`: every deep stack in a file, then tenure the interesting ones.
- `tenure --same-as FILE:LINE` at HEAD only (the rhyme of *when*, no history).

## Flipped assumption: bought and lost

`when` assumed the stack is a snapshot. `perch` assumed the predicate is a grep/exists/exec the user wrote. Concatenation assumes token occupancy *is* stack occupancy.

**Bought**

- Copy and move of a *condition* without a FALSE gap become visible (fixture; kizu `git.rs` → `parse.rs`).
- `grep isEnabled` that treats SitboneCore as a holder is no longer the answer. The occupant is `detect`; SitboneCore is an echo.
- Production that grew a guard is not "the old stack still held in src". It is ghost occupancy in tests plus a deeper echo in src.
- `--boolean` downcasts to held. Grain is a knob: functions / files / regions / loci.

**Lost**

- Eras are no longer a pure boolean occupancy, and they are no longer "files that mention the if-text".
- Growing modules fragment at regions/loci grain (kizu line drift).
- "Who is holding" for a unique token (`b_prefix_start`) agrees with perch. The interesting splits are common predicates and ghost stacks.
- Echo is a heuristic over scanned candidates, not a proof the mention is dead (`when` at that line already answers).
- Two snapshots still need `tell`. tenure does not invent the stack; it pins one.

## Kill / keep

**Keep.** It is a small verb, it is not a wrapper, and on the first real Swift `guard` it showed that `grep isEnabled` occupancy is not path-condition occupancy. The v1→v2 change was forced by sitbone `SitboneCore.swift`, not polish.
