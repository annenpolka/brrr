# destroy-tacit

Adversarial battery against **tacit** (candidate-40, v0.2). Does not rewrite the victim.

- Victim: `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b83-5900-7902-9188-72c70d715bf7`
- Report: `DESTROYER_TACIT.md` in that worktree
- Driver: `attack.py`
- Transcript: `transcript.txt`
- Follow-up: `followup.txt`
- Fixtures: `fixtures/{kwpos,multiline,comments,nested,clap,overload,wrapper,swiftmore}`
- Git repos: `repos/{move,rename,shift,born,float,clapmove,quotes,fossilonly,fossil40}`
- TSV dumps: `logs/`

```bash
python3 /tmp/destroy-tacit/attack.py
```

Verdict: mutate, do not kill.
