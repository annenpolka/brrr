# curation

Decision: ACCEPT_R1

contrastiveness: high — same cache-keys config; regular clone records a
commit, linked worktree records null; pack-refs also nulls the clone.
reproducibility: detailed public shell recipe; not locally run.
information_density: high — uv_cache.json contrast plus .git file vs
directory layouts.
safety: public uv; recipe uses temp dirs.
nontriviality: high — git identity of HEAD is layout-dependent
(worktree file, commondir, packed-refs).
ecosystem: rust / uv
mechanism: cache key identity for git commit/tags
suitability: the question is which git objects the cache key actually
bound.

Do not propose an affordance here.
