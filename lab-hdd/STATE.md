# Experiment state

- Start: 2026-09-01 22:00 JST
- Hard end: 2026-09-02 09:00 JST
- Clock: 2026-09-01 22:39 JST
- Phase: HDD Cambrian Explosion (22:00–00:00)
- Parent role: coordinator only
- Previous brrr: SEALED (`lab-hdd/SEAL.md`)
- Heartbeat scheduler: `01a05d01751a7e50b363750dcac94179` every 15m (durable, foreground)
- R1: DeepSeek R1 via OpenRouter through `hdd.py`; critic transport manual (host Red Pen)
- Effective R1 cap: **$10.00** (OpenRouter remaining ~$11.16 at start; experiment hard cap $50)
- Observed R1 spend: **~$0.29** (OpenRouter usage delta)

## Active workers

| Slot | Kind | assignment | status |
| --- | --- | --- | --- |
| G1 | Grounder | candidate-01 whence | worktree live; demo/tests OK; archive present; subagent may still dogfood |
| — | — | candidate-02 stated | DONE HEAD 3cc7bcd |
| — | — | candidate-03 owes | DONE HEAD 2e29625 |
| — | — | candidate-04 capdiff | DONE HEAD fd75f04 |
| — | — | candidate-05 envfrom | DONE HEAD 7cad6b3 |

## Notes

- Do not merge candidate product code onto `main`.
- Do not edit `EVOLUTION_REPORT.md`, `lab/`, or the previous master prompt.
- Product lives in `~/.grok/worktrees/annenpolka-brrr/candidate-*` and archives under `lab-hdd/lineages/`.
