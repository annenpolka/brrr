# curation

Decision: ACCEPT_R1

contrastiveness: high — same sources and target dir; only presence of
`-Zpublic-dependency` changes; `cargo clean` restores the expected
warning polarity.
reproducibility: issue recipe plus snapshot test at pinned SHA; nightly
only; not locally run.
information_density: high — six-step table, missing `[CHECKING]` lines.
safety: public cargo tests.
nontriviality: high — stale diagnostics after a flag-only rerun.
ecosystem: rust / cargo
mechanism: rebuild detection when compiler invocation shape changes
suitability: the question is whether the cached unit matches the
current rustc command line.

Do not propose an affordance here.
