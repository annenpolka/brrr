# destroyer-24 — peal

Adversarial pass on **peal(1)**: chime as `rg |` filter. Isolated branch. Never merge to main. The victim is not rewritten.

Victim: `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b6a-b1f0-7600-ae0c-3b73b8f2249f` (`7e89ad1`).

Report: `DESTROYER_PEAL.md` (also `lab/judges/DESTROYER_PEAL.md`). Transcript: `/tmp/destroy-peal/`.

## Verdict

**Mutate, do not kill.** `rg -n 'let b_side' parse.rs | peal` still equals `chime parse.rs:60`, including `Some(bytes_to_path)`. First-locator, substring pins, `pins[:16]`, and `rg -nH` basename are mutations.

## Install / run

Python 3.10+, stdlib, `rg`. Victim tests must still pass.

```bash
PEAL=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b6a-b1f0-7600-ae0c-3b73b8f2249f
python3 -m unittest tests.test_peal -q   # from $PEAL; 26/26
python3 /tmp/destroy-peal/attack.py      # 89 cases → /tmp/destroy-peal/transcript.txt
```

## Examples

```bash
# 1. Gold pipe still scans (not a filter). Some(bytes_to_path) is not in the rg hit.
cd ~/ghq/github.com/annenpolka/kizu
rg -n 'let b_side' src/git/parse.rs | $PEAL/peal --explain

# 2. First locator is the seed. return None; chimed the quoted-form arm.
rg -n 'return None;' src/git/parse.rs | $PEAL/peal --explain

# 3. Nested cwd: -nH basename dies; LINE:text pin recovery lives.
cd src/git
rg -nH 'let b_side' parse.rs | $PEAL/peal --explain   # rc=2
rg -n  'let b_side' parse.rs | $PEAL/peal --explain   # rc=0
```

Dogfood: kizu `src/git/parse.rs:60`, sitbone `PresenceArbiter.swift:76/80`. Compared with chime, not a third ambit.

See `DESTROYER_PEAL.md` for the rest of the battery (ambiguous pins, v2 recover, substring uniqueness, empty/binary/huge, `--column` / json / ANSI).
