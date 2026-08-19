# destroyer-19 — gist

Adversarial pass on **gist** (mutation-67), the 0-based LSP `textDocument/publishDiagnostics` rewriter. Isolated worktree. Never merge to main. Do not rewrite the victim. Not leftover-name. Not pin.

Victim: `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-cb7959a1069d`

Report: [DESTROYER_GIST.md](DESTROYER_GIST.md) · [lab/judges/DESTROYER_GIST.md](lab/judges/DESTROYER_GIST.md)

Artifacts: `/tmp/destroy-gist/` (`attack.py`, `transcript.txt`, `followup.txt`, `fixtures/`)

## Primitive

Rewrite stale nested locators inside an LSP publishDiagnostics stream from `--from-dir` onto `--to-dir`. Path is `uri`. Line is 0-based `range.start.line`. Off-by-one is load-bearing. `Content-Length` is dest-owned. SARIF `startLine` is not this schema.

## How to re-run

```bash
# victim still green after the battery
/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-cb7959a1069d/demo.sh

# full battery
python3 /tmp/destroy-gist/attack.py

# one attack
GIST=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-cb7959a1069d/gist
$GIST --from-dir /tmp/destroy-gist/fixtures/split-from \
      --to-dir   /tmp/destroy-gist/fixtures/split-to --trace \
      < /tmp/destroy-gist/fixtures/multihunk.json
```

Requires Python 3.9+. gist never calls git. Dogfood copies of kizu / sitbone / voidtrace are `git archive`d by the attack driver.

## Three examples

kizu gold, still 0-based, still not 17:

```bash
$GIST --from-dir /tmp/destroy-gist/trees/kizu-b4e6a5d \
      --to-dir   /tmp/destroy-gist/trees/kizu-HEAD \
      < /tmp/destroy-gist/fixtures/kizu.publish.json
# range.start.line  528 → 16
# no origin diagnostics: []
```

UTF-16 identity, source column kept:

```bash
$GIST --from-dir /tmp/destroy-gist/fixtures/wide2-to \
      --to-dir   /tmp/destroy-gist/fixtures/wide2-to \
      < /tmp/destroy-gist/fixtures/utf16-identity.json
# dest  WIDE_TOKEN_QZX 😀     py_len=16  utf16=17
# character 22 stays 22
```

SARIF 1-based stuffed into an LSP field lands on dest 17:

```bash
# range.start.line=529  (the SARIF integer, not 528)
# gist → layout.rs line 17, not 16
```

## Verdict

**Mutate, do not kill.** Gold `528 → 16`, sitbone `44 → 74`, voidtrace line 0, SARIF 529 stays 529, dest-owned `Content-Length` all survived. Mutate toward blot's origin-clear and UTF-16 clamp, honest rustc gutter re-fingerprint, `}`-as-neighbor, fail-closed pretty ingest, and refuse of stuffed 1-based integers. flare already owns `529 → 528`.
