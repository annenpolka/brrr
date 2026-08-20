# Lineages

Each directory is one inventor's harvest.

Always present (reports):

- `CANDIDATE.md` — primitive, transcript, kill/keep
- `README.md` — how to run
- `demo.sh` — parent-run demo
- `WORKTREE.txt` / `HEAD.txt` / `BRANCH.txt` / `COMMITS.txt` — origin in `~/.grok/worktrees/annenpolka-brrr/`

Also present when the worktree still held the tool (archived 2026-08-20 after 09:00):

- the CLI (usually a Python shebang with the tool's name)
- `fixtures/`, `tests/`, extra `*.py` as needed

Skip `subagent-*` dumps (incomplete harvest.sh copies). Destroyer slots are reports only.

Run from the lineage directory:

```bash
chmod +x ./demo.sh ./<tool>
./demo.sh 0
```
