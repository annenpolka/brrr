# destroyer-12 — berth

Adversarial pass on **file-identity occupancy**. A rename is supposed to be one roost. This branch does not rewrite the victim and must not merge to `main`.

Victim: `mutation-52/berth` @ `2c5fe99`
`/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b6b-7144-7812-8fcb-cbf1c493bd9a`

Report: [`DESTROYER_BERTH.md`](DESTROYER_BERTH.md) (also `lab/judges/DESTROYER_BERTH.md`).
Transcript: `/tmp/destroy-berth/transcript.txt`
Follow-up: `/tmp/destroy-berth/followup.txt`
Fixtures / drivers: `/tmp/destroy-berth/{fixtures,attack.py,followup.py}`

Verdict: **mutate, do not kill.**

## Install / run

```bash
# victim still gold after the attacks
/path/to/berth/demo.sh 0          # PASS=79 FAIL=0

# replay the battery (writes /tmp/destroy-berth/transcript.txt)
python3 /tmp/destroy-berth/attack.py
python3 /tmp/destroy-berth/followup.py
```

Python 3.9+, `git`. No other dependencies. Isolated worktree only.

## Examples

**1. First-parent dead name is never-held. Dest on the same walk is TRUE.**

```bash
berth -C kizu exists deep-research-ai-agent-hooks.md
# FALSE 24/24  hint: --full (path diagnosis)

berth -C kizu exists docs/deep-research-ai-agent-hooks.md
# TRUE 21/24  origin 321a830 as the old name
# aka=docs/… only — identity chain dropped the old path
```

`--full` from either name is still the 187-commit roost. Rove already fixed this for `grep -- PATH` by resolving identity from all reachable R.

**2. Living leftover name occupies the other file.**

```bash
git mv old.txt new.txt && echo REINCARNATED > old.txt && git add -A && git commit
berth exists old.txt
# identity: old.txt → new.txt   holders at HEAD: new.txt
# the file sitting at old.txt is invisible
berth --no-follow exists old.txt
# TFT  leftover occupant
```

**3. C056 leftover blob is not a follow (copy stays copy).**

```bash
berth -C kizu --full exists src/init.rs            # aka=src/init.rs
berth -C kizu --full exists src/init/install.rs    # unique birth at 5671a72
```

Do not turn this into leftover-name search. crib/ditto/pup already name COPY vs FOLLOW.

## Kill / keep

**Keep. Mutate.** Next mutation is rove's all-reachable R for `exists`, plus tip-occupant seed so a leftover path is its own roost. Not a rewrite in this pass.
