# mutation-88 — aloud

## Primitive

A BLAST survivor that later **says the new default** is a different object than a site that stayed omitted, and different from SHADOW-of-old. aloud names that object: omitted → explicit-equal-to-new-default (FOSSIL of the *new* value, not the old).

## Why this might not exist

tacit already names TACIT vs SHADOW at one snapshot, and BLAST vs FOSSIL vs PRE across a default-moving diff. HEAD still collapses three histories into one SHADOW-of-0.45:

```
MUTE    rode the blast, still omits          — will follow the next move
ALOUD   rode the blast, then wrote 0.45      — pinned the inherited world
PRE     already wrote 0.45 *in* the blast    — never a survivor
LATE    born later already writing 0.45      — never rode it
FOSSIL  still writes 0.4                     — SHADOW of the old value
```

`rg presentThreshold: 0.45` sees ALOUD, PRE, and LATE as the same token. tacit's two-point `--git OLD NEW` sees ALOUD as ordinary SHADOW-of-new (or as PRE if you only look at HEAD). The missing verb is: *who rode the blast silently, then spoke?*

Discarded: leftover-name search, lockset clone, clock-cut clone, inverse-printf walker, wrapping tacit with a flag that still emits BLAST.

## How to run

From the worktree root:

```bash
chmod +x ./aloud ./demo.sh
./aloud --selftest
./demo.sh
./aloud -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone --blast e9b0f75 --summary presentThreshold
./aloud -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone --blast e9b0f75 --until e9b0f75 --summary presentThreshold
./aloud -C /Users/annenpolka/ghq/github.com/annenpolka/kizu --blast 3d4b543 --summary agent
./aloud -C /Users/annenpolka/ghq/github.com/annenpolka/kizu --blast 3d4b543 --all --summary agent
```

Python 3.10+, stdlib, `git`. `--blast REV` means `REV^..REV`; `--until` defaults to the worktree. Exit 0 ok, 1 `--check` found ALOUD, 2 error.

## Empirical transcript

### v0.1 — three snapshots, join by siblings-excluding-slot

`--selftest` green: Swift rename `threshold=0.4 → presentThreshold=0.45`, Python `greeting="hi"→"yo"`, TS positional `attempts=3→5`. Four sites in one file become ALOUD / MUTE / FOSSIL / PRE; a fifth born-after SHADOW is LATE. At `--until BLAST`, ALOUD is 0 (control). Join key drops the spoken slot so `presentThreshold: 0.45` still matches the omitted rider.

First dogfood:

| tree | query | v0.1 |
| --- | --- | --- |
| sitbone | `--blast e9b0f75 presentThreshold` | **ALOUD 0, MUTE 27.** Production `SitboneCore.swift:68` and every hysteresis test still omit. Money shot: the blast is still silent. |
| sitbone | `--until e9b0f75` | **ALOUD 0, MUTE 27.** Control: nobody can have spoken *yet*. |
| sitbone | `--blast e9b0f75 PresenceArbiter` | **MUTE 54** = 27 present + 27 absent (born slot). Matches tacit's BLAST 54. |
| kizu | `--blast 3d4b543 --summary agent` | **empty.** LATE was not a default fate, so the interesting rows vanished. |
| kizu | `--all --summary agent` | **LATE 31, BOUND 2.** Mud: SHADOW `--agent claude-code`, OVERRIDE `cursor`/`cline`, and TACIT command lines shared one bucket. |

sitbone paid rent immediately. kizu lied: 31 LATE looked like "someone spoke" including sites that overrode to cline.

### v0.2 — one improvement, from that run

Honesty of *false ALOUD*, not more fates:

1. **LATE is only born-after SHADOW of the new default.** Born-after OVERRIDE is LOCK. Born-after TACIT is FRESH. BOUND stays BOUND.
2. **LATE is a default fate.** `--summary` without `--all` still shows the thing people confuse with ALOUD.
3. Empty blast interval warns on stderr instead of printing nothing.

After v0.2: `./demo.sh 0` **24 passed, 0 failed**.

kizu:

```
HookPostTool  agent  ALOUD=0 MUTE=0 FOSSIL=0 PRE=0 LATE=14
HookStop      agent  ALOUD=0 MUTE=0 FOSSIL=0 PRE=0 LATE=4
--all: LATE=18 FRESH=6 LOCK=7 BOUND=2
```

Tests restated `--agent claude-code` after the slot was born. They were never tacit riders of a moving default. `--check` exits 0: LATE is not ALOUD.

sitbone unchanged: 0 ALOUD, 27 MUTE, `--check` exits 0.

## Dogfood targets

- `./aloud --selftest` (21): Swift rename-move, py, ts positional, ordinal zip of twin fingerprints, LATE ≠ ALOUD, LOCK ≠ LATE, comment residue.
- `./demo.sh` synthetic three-commit git + sitbone e9b0f75 + kizu 3d4b543.
- `/Users/annenpolka/ghq/github.com/annenpolka/{sitbone,kizu}`.

## Surprises

- sitbone's hysteresis tests **document 0.45 in comments** and in the 0.40 middle-band stimulus, override `emaAlpha: 1.0`, and still omit `presentThreshold`. Years after e9b0f75 they are MUTE, not ALOUD. Speaking the world you inhabit is a different act than riding it.
- kizu's `--agent claude-code` restatements *look* like ALOUD to `rg`. They are LATE: the call-sites did not exist at birth. The slot was born without riders, then tests arrived already speaking. tacit's SHADOW count cannot say this; aloud's ALOUD=0 LATE=18 is the sentence.
- Position pairing from tacit is still load-bearing: `threshold → presentThreshold` at the same index is one moved slot. Name-only join would report death+birth and every later `presentThreshold: 0.45` as LATE (born speaking a new name) instead of ALOUD/MUTE of a renamed rider.
- Two `PresenceArbiter(sensors: ["camera"])` in one file join by ordinal inside the sibling-arg group. Speaking the second does not steal the first's key, because the spoken slot is excluded from the fingerprint.

## Failures

- Inserting a same-fingerprint call between blast and later shifts ordinals; the zip can pair the wrong survivor. Distinct sibling args (the sitbone `emaAlpha: 1.0` vs not) dodge this; twins do not.
- File rename between BLAST and `--until` looks like GONE+LATE, not MUTE/ALOUD of the same site. No git-follow.
- Clap TACIT still needs a command-shaped line (`kizu ` / `command:`). Prose in README is silent. Inherited from tacit, not the hole.
- `--blast` wants the commit that *moved* the default. There is no `--scan` to find e9b0f75 for you.
- Default expressions that are not literals (`Double.random(in: 0...1)`) do not compare as SHADOW, so they cannot become ALOUD.
- Swift unlabeled first arguments are ignored (honesty: comment residue). Same as tacit.

## Suggested mutations

- **`--emit`**: rewrite ALOUD back to TACIT (unspeak the pin) or MUTE to SHADOW (pin the inherited world). The patch is the witness that the fate was real.
- **`--scan OLD..HEAD`**: harvest consecutive revs, emit blast commits that grew MUTE/ALOUD. Stops needing to know e9b0f75.
- **follow**: identity across file rename / callee rename between blast and later (ditto/erst, not leftover-name).
- **echo** (from tacit): a MUTE site whose enclosing body restates the new literal in a comment or `XCTAssertEqual(..., 0.45)`. The test *thinks* it spoke.

## Kill / keep

**Keep.** tacit names omission at a snapshot and FOSSIL of the *old* value across a blast. aloud names the blast survivor that then fossilized the *new* value. sitbone e9b0f75 is still 27 MUTE; kizu `--agent claude-code` is LATE not ALOUD. Those two sentences do not exist in tacit's TSV.

Park: treating this as leftover-claims (zanei) or as tacit's PRE. PRE already spoke *at* the blast. ALOUD spoke *after* riding it. LATE never rode it. Three objects, one later literal.
