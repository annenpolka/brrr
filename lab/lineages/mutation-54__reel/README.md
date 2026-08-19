# reel

A mixed commit as a **`git format-patch` mailbox of name-closed acts**.

`git format-patch` needs already-split commits. canto reported the plot
(PRELUDE / PAYOFF / ASIDE / SPOIL). reel *emits* it: one `git am` patch
per act, in reading order. Default stdout is the mailbox, not a report.
`--check` still exits 1 on SPOIL or TANGLE.

A name is a plot point if this diff defines it. An act is a name-closed
set of files. Later acts may use earlier defs; the reverse is TANGLE.
Independent name sets are tracks.

## Install / run

Python 3.9+, `git`, stdlib. From this directory:

```bash
chmod +x ./reel ./demo.sh
./reel --help
./reel --selftest
./demo.sh 0
./reel -C /path/to/repo HEAD | git am
./reel -C /path/to/repo -o /tmp/story --verify COMMIT
./reel -C /path/to/repo --check COMMIT
./reel -C /path/to/repo --report COMMIT
```

Default range: dirty worktree vs HEAD, else `HEAD^ HEAD`.
Default grain: **file** (what a patch series can name).
Emit needs a commit TO (`--report` / `--check` for a dirty tree).

## Examples

**1. Unsquash a mixed commit (sitbone dual-threshold hysteresis)**

```bash
./reel -C sitbone e9b0f75
# Subject: [PATCH 1/3] PRELUDE: PresenceArbiter.swift
# Subject: [PATCH 2/3] PAYOFF: PresenceHysteresisTests.swift
# Subject: [PATCH 3/3] ASIDE: PresenceArbiterTests.swift
```

`git am` on `e9b0f75^` reconstitutes `e9b0f75` (`--verify`). ASIDE is parked
last so a blank-line sibling does not interrupt the story (`--aside inline`
keeps plot order).

**2. Write numbered patches, like `git format-patch -o`**

```bash
./reel -C repo -o /tmp/story --verify FROM TO
# 0001-PRELUDE-lexer.py.patch
# 0002-PRELUDE-parse.py.patch
# 0003-PAYOFF-test_parse.py.patch
```

**3. CI: fail closed on a feature dump**

```bash
./reel -C kizu --check 04adde1
# exit 1 — src/highlight.rs is SPOIL (prod + #[test] in one file)
```

`--report` is the opt-in porcelain plot. `--against` scores recovered
acts vs the original commits in `FROM..TO`. Emit parks ASIDE last
(report stays topo). `--cover` writes `0000-cover-letter.patch` (needs `-o`).

Exit `0` ok, `1` `--check` failed or `--verify` miss, `2` usage/error.
