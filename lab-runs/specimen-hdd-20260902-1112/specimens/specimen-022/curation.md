# curation

Decision: ACCEPT_R1

contrastiveness: high — same executable path, only `PYTHONEXECUTABLE`
presence changes; second lookup still prints the first lookup's venv.
reproducibility: unit test at pinned SHA; issue 21062 is a heavier
worktree story. Packet is source-backed.
information_density: high — two commands, two stdout lines, cache
bucket named in the issue.
safety: public uv tests; do not run against host venvs with secrets.
nontriviality: high — env var changes reported identity without
changing the requested path.
ecosystem: rust / uv
mechanism: interpreter metadata cache vs launcher environment
suitability: the question is which identity a cached interpreter query
is bound to.

Do not propose an affordance here.
