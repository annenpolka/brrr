# destroyer-21 — smolder

Leftover **claim** locus in, adversarial invert out. Break smolder (mutation-63): dest locus → falsifying commit / ash regenerate.

Not leftover-name search (haunt/wraith). `FILE:LINE` is legal **input**. Victim is not rewritten.

## Primitive

Ask smolder the invert (this leftover line, which commit made it false?) at dest-rename, lockfile-vs-comment, October, two `version`s, vendor, 2 MB dest, Japanese bindings, and ash vs believer. Peel dest identity with tinder.

## How to run

Python 3.9+ and `git` on `PATH`. Victim and peel binaries:

```
SMOLDER=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-cb3a629800b3/smolder
TINDER=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bad-eb91-7d80-9aa0-1040781e71b7/tinder
```

```bash
chmod +x ./demo.sh /tmp/destroy-smolder/*.py
./demo.sh                    # replay lethal cases; exits 0 if gold still holds and holes still fire
python3 /tmp/destroy-smolder/rest.py   # rebuild follow-up fixtures + transcript
```

Transcripts: `/tmp/destroy-smolder/transcript.txt`, `/tmp/destroy-smolder/followup.txt`.
Report: `DESTROYER_SMOLDER.md` (also `lab/judges/DESTROYER_SMOLDER.md`).

Exit of `./demo.sh`: `0` gold intact and dest:84 leftover-name still fires; `1` a gold died or a hole closed without a rewrite we own.

## Examples

**1. Dest leftover that moved is leftover-name, not dest identity.**

```bash
$SMOLDER --no-color --explain --no-hunk -C kizu docs/deep-research-ai-agent-hooks.md:84
# FALSIFIED a75d4ea  STR "kizu hook-post-tool" → "kizu' hook-post-tool"
$TINDER --no-color --no-hunk -C kizu docs/deep-research-ai-agent-hooks.md:84
# none — timeout is still 10
```

**2. Generated lockfile dest is ash; believer leftover of a lockfile-only bump blames a comment.**

```bash
$SMOLDER --no-color -C kizu Cargo.lock:168
# regenerate  cargo
$SMOLDER --no-color --no-hunk -C /tmp/destroy-smolder/fixtures/lock-ash README.md:1
# FALSIFIED … comment now says 0.7.0   src/lib.rs:1
```

**3. Two packages named version; October on the same line as timeout.**

```bash
$SMOLDER --no-color --no-hunk -C /tmp/destroy-smolder/fixtures/workspace pkg_b/Cargo.toml:3
# FALSIFIED pkg_a 0.3.0 → 0.7.0
$SMOLDER --no-color --no-hunk -C /tmp/destroy-smolder/fixtures/october-named docs/us.md:1
# timeout shipped 10/01/2024  →  HOOK_TIMEOUT 10 → 30
```

Verdict: **mutate, do not kill.** See `DESTROYER_SMOLDER.md`.
