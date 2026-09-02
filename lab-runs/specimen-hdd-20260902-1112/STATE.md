# Experiment state

- Run: `specimen-hdd-20260902-1112`
- Start: 2026-09-02 11:12:00 JST
- Hard end: 2026-09-03 00:00:00 JST
- Preservation start: 2026-09-02 23:25:00 JST
- Clock: 2026-09-03 00:00:15 JST
- Phase: **HARD STOP**. No new spawns. Claim returns null; enqueue raises. Jury complete. Tomorrow = bindname. job-0731 DONE 23:25:40. Isolation MATCH bootstrap. PATH recheck 23:58: demo ×2 identical to 23:26; tests 119/119 OK. 23 frozen scouts left READY (unclaimable).
- Parent role: coordinator only (`main` `432f954`; no candidate product merge)
- Previous brrr/HDD: **UNSEALED** after `FIRST_SELECTION.md` (~12:10 JST)
- HDD transport: DeepSeek R1 via OpenRouter through `hdd.py --root .hdd-runs/specimen-hdd-20260902-1112`
- Critic transport: host/manual Red Pen
- Effective R1 cap: **$9.25** (spent ~$2.93 remaining ~$6.32)

## Clock note

Updated 2026-09-02 23:26 JST. Preservation. Isolation hashes MATCH bootstrap. Canonical `isolation-after.txt` written for gating compare. bindname preservation demo ×2 identical; tests 119/119 OK.

## Progress

- FIRST_SELECTION.md: bindname/ordleak keep; envlayers lineage-only; Skeptic dissent recorded
- FINAL_JURY.md / TOMORROW.md: PATH `bindname` only; Skeptic empty-PATH recorded
- Specimen Judge: `judges/FINAL_SPECIMEN.md` (job-0730)
- CONVERGENCE.md filled
- Run-local EVOLUTION_REPORT.md preservation artifact (sections 1–18; not historical repo EVOLUTION_REPORT.md)
- job-0731 DONE 23:25:40 worker=preserve-final; pack completed with canonical isolation-after + R1_BUDGET render + preservation demos
- Historical isolation hashes unchanged (`0d0eaa39` / `b22f0bcb` / `36785c9c` / `af79bcee` / `8e1a35f0`)
- bindname CLI sha256 `c7d985ed9b0ebb42f775ff3bacefc3c27e9505ff37f25a03abdd82a18609755f`

## Notes

- Do not merge candidate product code onto `main`.
- Do not edit historical reports, `lab/`, `lab-hdd/`, or `.hdd/`.
- Product lives in isolated worktrees; archives under `lineages/`.
- No new broad R1 after 22:45. Exceptional-jump not warranted.
- HARD STOP reached 2026-09-03 00:00:15 JST. Preservation pack sealed. Parent may mark the goal complete. Do not merge candidate product onto `main`.
