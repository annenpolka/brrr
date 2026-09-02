# TASK

Pants `vcs_version` / `export-codegen` can keep the identity of a **previous git describe** after an amend or a new commit should have been a different hash. `generate_python_from_setuptools_scm` always reruns because `MaybeGitWorktree` is uncacheable. The child `VenvPexProcess` that runs setuptools_scm was still memoized. Git hash is omitted from that process cache identity.

On failing_ref `02fa93e2947789cf1f9f8c025e7ceaca01169ef2`:

```
result = await Get(
    ProcessResult,
    VenvPexProcess(
        setuptools_scm_pex,
        argv=argv,
        input_digest=input_digest,
        description=f"Run setuptools_scm for {request.protocol_target.address.spec}",
        level=LogLevel.INFO,
    ),
)
```

`from pants.engine.process import ProcessResult` — no `ProcessCacheScope`. `argv` is `--root` worktree path plus synthetic toml. `input_digest` is that toml only. Git state is not in the process key.

Public report (pantsbuild/pants#16963). `vcs_version(generate_to=..., template=...)`; `./pants export-codegen`; amend or commit; leftover previous `some-tag.dev1+g1bd665ffd` until `rm -rf ~/.cache/pants`.

In-tree after the repair (not on failing_ref): `cache_scope=ProcessCacheScope.PER_SESSION` on that `VenvPexProcess`.

Case A — second `export-codegen` with unchanged HEAD:
  cache identity is current
  not leftover-after-git-change

Case B — amend or new commit, leftover process cache:
  leftover: previous setuptools_scm stdout / generated version module
  git hash omitted from VenvPexProcess identity
  enclosing rule reran; child process reused

Case C — `rm -rf ~/.cache/pants` then export-codegen:
  fresh process identity
  not leftover previous git describe

Case D — process cache scoped to the session (post-repair shape, not on failing_ref):
  cache miss after git change
  not leftover previous version string

The developer wants to know which identity case B actually used for the generated version after the amend/commit: leftover previous-git-describe results (git hash omitted from process key), current git identity, or omitted (no cache).
