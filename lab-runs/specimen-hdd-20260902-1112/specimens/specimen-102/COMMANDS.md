```
# not executed on this lab host
# failing_ref 77f271063993020770ee785469226e33324576be
# crates/uv-distribution/src/metadata/requires_dist.rs from_metadata23
# crates/uv-distribution/src/metadata/lowering.rs from_requirement sources==None
# crates/uv/tests/it/sync.rs lock_git_poetry_path_dependency (on the PR, not failing_ref)

# public shape:
# git source subdirectory=root; Poetry path = "../child"
# uv lock --no-cache
# failing: child source.directory = absolute git checkout path
```

Source-backed only. Do not execute untrusted checkouts on the host.
