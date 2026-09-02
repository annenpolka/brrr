# Harvest: hdd-wtcache (transfer)

- Core Affordance: Name which identity component was omitted from a cache key (worktree vs commit/tags).
- Affordance Classification: USEFUL_COMPOSITION
- Source Specimens: specimen-062
- Origin trial: hdd-wtcache
- Transfer onto: lockident / uv023 / freshmiss
- Embodiment: no new CLI; owned `wt_cache.py` already names same-key-if-worktree-omitted
- Rejected: invented tox-worktree-util
