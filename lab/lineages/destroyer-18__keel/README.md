# DESTROYER — keel

Adversarial pass on keel (mutation-60): **origin is remotes + tip witnesses, not root SHAs.** Isolated worktree. Victim not rewritten. Not a second pin-v0.5 leftover-stub destroyer.

## Primitive under attack

A keel token is supposed to name a **project**. A `file://` depth-1 clone of the same remote should resolve. A stranger should fail-close unless `--any-repo`.

The attacks show the key is still **config ∪ object occupancy**: `git remote add extra git@github.com:victim.git` is identity; fetching one witness SHA is identity; missing origin is allowed.

## Install / run

Victim (read-only):

```bash
KEEL=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-cb0da2df3d3e/keel
chmod +x "$KEEL"
"$KEEL" --selftest
```

This battery:

```bash
chmod +x ./demo.sh ./attack.py ./attack2.py
./demo.sh
```

Writes `/tmp/destroy-keel/{transcript,transcript-round2}.txt`, `cases.json`, fixtures, kizu file:// shallow.

## Examples

Foreign git root still refuses (bought):

```bash
./keel resolve --repo $FOREIGN --to HEAD --porcelain "$HELPER"
# rc=1  token belongs to a different repository (…/ugly vs …/other/util)
```

Same dest after `git remote add extra git@github.com:keel-lab/ugly.git` (no fetch):

```bash
./keel resolve --repo $FOREIGN --to HEAD --porcelain "$HELPER"
# moved  src/calc.py:4  →  pkg/util.py:1  1.000
```

kizu pin on a stranger that copied `layout.rs` and fetched kizu HEAD:

```bash
./keel resolve --repo $STEAL --to HEAD --porcelain "$SEEN"
# moved  src/app.rs:529  →  src/app/layout.rs:17  1.000
```

## Report

[DESTROYER_KEEL.md](DESTROYER_KEEL.md) — also `lab/judges/DESTROYER_KEEL.md`.

Verdict: **mutate, do not kill.**
