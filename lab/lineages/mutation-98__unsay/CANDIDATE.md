# mutation-98 — unsay

## Primitive

A named ALOUD site is not a witness. unsay emits the unified diff that **unspeaks** it: delete the explicit new-default argument so the BLAST survivor rides again (ALOUD → TACIT). Optionally `--pin` writes that default at MUTE sites (MUTE → SHADOW). PRE, LATE, and FOSSIL are not unsaid.

## Why this might not exist

aloud names omitted-then-spoken. Naming still leaves the pin in the tree. `rg presentThreshold: 0.45` / leftover-claims would also rewrite PRE (spoke *at* the blast) and LATE (never rode). The missing verb is: *take the spoken new-default back, and only that*.

The patch is the proof the fate was real: after `unsay --emit | git apply`, the mic site is MUTE and lidar/new still speak.

Discarded: leftover-name search, lockset clone, inverse-printf walker, wrapping aloud with a flag that still only prints TSV.

## How to run

From the worktree root:

```bash
chmod +x ./unsay ./demo.sh
./unsay --selftest
./demo.sh
./unsay -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone --blast e9b0f75 --emit presentThreshold
./unsay -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone --blast e9b0f75 --emit --pin presentThreshold
./unsay -C /Users/annenpolka/ghq/github.com/annenpolka/kizu --blast 3d4b543 --emit agent
```

Python 3.10+, stdlib, `git`. `--blast REV` means `REV^..REV`; `--until` defaults to the worktree. Exit 0 ok, 1 `--check` found ALOUD, 2 error. `--emit` is a unified diff on stdout.

## Empirical transcript

### v0.1 — emit deletes ALOUD, not PRE/LATE/FOSSIL

`--selftest` green: parent aloud fates plus rewrite. Naive `, presentThreshold: 0.45` regex would also unspeak PRE and LATE; unsay does not. Re-harvest after rewrite: ALOUD became MUTE (two tacit riders), PRE/LATE/FOSSIL unchanged. Unified diff `git apply`s. Python keyword and TS positional too. Multiline Swift drops the labeled line and `--pin` adds a trailing comma.

`./demo.sh 0` **35 passed, 0 failed**.

Synthetic three-commit repo (`threshold=0.4 → presentThreshold=0.45`, then mic speaks 0.45):

```
--- a/arbiter.swift
+++ b/arbiter.swift
@@ -3,7 +3,7 @@
     let mute = PresenceArbiter(sensors: ["camera"])
-    let spoken = PresenceArbiter(sensors: ["mic"], presentThreshold: 0.45)
+    let spoken = PresenceArbiter(sensors: ["mic"])
     let fossil = PresenceArbiter(sensors: ["radar"], presentThreshold: 0.4)
     let pre = PresenceArbiter(sensors: ["lidar"], presentThreshold: 0.45)
     let late = PresenceArbiter(sensors: ["new"], presentThreshold: 0.45)
```

`git apply` then `--summary presentThreshold`: **ALOUD 0, MUTE 2, FOSSIL 1, PRE 1, LATE 1**. `--check` exits 0. lidar/new/radar untouched. At `--until BLAST`, `--emit` is empty (nobody has spoken yet).

| tree | query | v0.1 |
| --- | --- | --- |
| sitbone | `--blast e9b0f75 --emit presentThreshold` | **empty stdout.** `unsay: 0 ALOUD; nothing to unspeak`. MUTE 27. Money shot: the blast is still silent, so there is nothing to unspeak. |
| sitbone | `--emit --pin presentThreshold` | **27** `+ presentThreshold: 0.45` across SitboneCore + three test files. 0 deletions. Production multiline call gains a trailing comma and the arg. Hysteresis `emaAlpha: 1.0` becomes `emaAlpha: 1.0, presentThreshold: 0.45`. `git apply` on a copy of those four files: exit 0. |
| kizu | `--blast 3d4b543 --emit agent` | **empty stdout.** LATE 18. `--agent claude-code` is not deleted. `--check` exits 0. `--emit --pin`: `0 MUTE; nothing to pin` (LATE is not MUTE). |

sitbone paid rent: empty `--emit` is the witness that 27 riders never spoke. `--pin` is the dual witness that MUTE was real (27 insertions, `git apply` clean). kizu paid the false-ALOUD rent: 18 later SHADOW-of-new sites are not in the patch.

### v0.2 — one improvement, from that run

Honesty of *empty emit*, not more rewrites:

sitbone and kizu both printed `unsay: 0 ALOUD; nothing to unspeak`. Those are opposite objects. sitbone's 27 MUTE *still ride*. kizu's 18 LATE *look* like ALOUD to `rg` and were never riders. v0.1 collapsed them into one sentence, so a skeptic could not tell "nothing spoke" from "spoke but we refused."

v0.2 names the refusal on stderr from the default fates (not from `--only`):

```
sitbone --emit presentThreshold
unsay: 0 ALOUD (27 MUTE still ride); nothing to unspeak

kizu --emit agent
unsay: 0 ALOUD (18 LATE born-speaking, never rode); nothing to unspeak

kizu --emit --pin agent
unsay: 0 ALOUD (18 LATE born-speaking, never rode); nothing to unspeak
unsay: 0 MUTE (18 LATE is not MUTE); nothing to pin
```

`--only late --emit` still emits nothing (LATE cannot be unsaid) and still names LATE. `--pin` still will not write `--agent claude-code` onto born-speaking tests.

After v0.2: `./unsay --selftest` **40** ok. `./demo.sh 0` **39 passed, 0 failed**.

## Dogfood targets

- `./unsay --selftest` (40): Swift rename-move, py, ts positional, ordinal zip, LATE ≠ ALOUD, emit-only-ALOUD, naive-regex control, apply-then-MUTE, multiline pin comma, empty-emit MUTE≠LATE.
- `./demo.sh` synthetic three-commit git apply + sitbone e9b0f75 + kizu 3d4b543.
- `/Users/annenpolka/ghq/github.com/annenpolka/{sitbone,kizu}`.

## Surprises

- sitbone HEAD is still 0 ALOUD / 27 MUTE years after e9b0f75. `--emit` being empty is the gold, not a miss. `--pin` of the production `PresenceArbiter(` in `SitboneCore.swift:68` needed a trailing comma on `frameProvider: frameProvider` and the same indent as sibling args — multiline pin is load-bearing, not a pretty-printer.
- Hysteresis tests already write `0.45` in comments and in the 0.40 middle-band stimulus, override `emaAlpha: 1.0`, and omit `presentThreshold`. `--pin` makes the *call* match the comment. Speaking the world you inhabit is a different act than documenting it (aloud's surprise, now a patch).
- kizu `--agent claude-code` restatements are LATE. `--emit --pin` refuses them as 0 MUTE. A leftover-name or `rg --agent claude-code` rewriter would have deleted or pinned the wrong object.
- Unified diffs mashed into one line until body lines kept their newlines (`splitlines(keepends=True)`). `git apply` is the test; substring checks on the patch are not.

## Failures

- Inserting a same-fingerprint call between blast and later still zips the wrong survivor (inherited from aloud). unsay would then unspeak the wrong site.
- File rename between BLAST and `--until` looks like GONE+LATE; no emit of the renamed rider.
- Unfolded nested slots (`thresholds.driftDelay`) are skipped (`.` in the param). Cannot unspeak a leaf inside an omitted `Foo()`.
- Clap TACIT still needs a command-shaped line. Clap ALOUD can delete `--flag value`; not dogfooded (kizu has no ALOUD).
- `--blast` still wants the commit that moved the default. No `--scan`.
- Default expressions that are not literals cannot become ALOUD, so they cannot be unsaid.

## Suggested mutations

- **`--scan OLD..HEAD`**: harvest consecutive revs, emit blast commits that grew ALOUD (sites that *became* speakable, then unsay them).
- **echo**: MUTE whose body restates the new literal in a comment / `XCTAssertEqual(..., 0.45)`. Pin would make the call agree with the comment; echo would name the lie while omitted.
- **follow**: identity across file rename between blast and later, so ALOUD of a moved file is still unsaid.
- Inverse **fossil-unspeak**: delete old-value FOSSIL args so they ride the *new* default (different verb: they never rode the blast as TACIT).

## Kill / keep

**Keep.** aloud names ALOUD. unsay *undoes* it. sitbone e9b0f75 `--emit` empty (27 MUTE) and kizu `--emit` empty (18 LATE, not deleted) are two sentences `rg` cannot produce. The synthetic apply (ALOUD → MUTE, PRE/LATE intact) is the witness that the fate was a real span, not a leftover name.

Park: treating this as leftover-claims (zanei) or as "delete every SHADOW of 0.45". PRE and LATE are SHADOW of 0.45. Only ALOUD rode silently and then spoke.
