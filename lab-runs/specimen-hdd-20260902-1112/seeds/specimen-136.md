CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

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

# OBSERVED

Public pantsbuild/pants#16963 (closed 2022-09-27). PR 17017 merge `510f1755680d23c3d6c68815ae77ad4a4f836021` (parent `02fa93e2947789cf1f9f8c025e7ceaca01169ef2`). Local pants was not performed on this lab host.

Issue body: generated version string cached and not invalidated after amend/commit; deleting `~/.cache/pants` restores the current git describe. Maintainer: MaybeGitWorktree is uncacheable so the enclosing rule always runs; the underlying setuptools_scm process was still memoized.

On failing_ref, `VenvPexProcess` has no `cache_scope`. `ProcessCacheScope` is **not** imported on the failing revision. It is added by PR 17017.

Not this packet: specimen-075 rustc incremental false-green / next-solver anon-task. pants#23645 leftover process cache vs env is still OPEN (env without cache key). pants#18334 is process metadata, not leftover cache identity.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 02fa93e2947789cf1f9f8c025e7ceaca01169ef2
# src/python/pants/backend/python/util_rules/vcs_versioning.py
# generate_python_from_setuptools_scm VenvPexProcess

# public shape:
# leftover generated version after amend/commit
# git hash omitted from process cache identity
# enclosing MaybeGitWorktree rule reruns; child process reused
# until ~/.cache/pants deleted
```

Source-backed only. Do not execute untrusted checkouts on the host.

pantsbuild/pants
  src/python/pants/backend/python/util_rules/vcs_versioning.py
  ~/.cache/pants

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  vcs_version generate_to template
  leftover process cache after amend/commit

Case A (second export-codegen, same HEAD):
  current cache identity
  not leftover-after-git-change

Case B (amend or new commit, leftover process cache):
  leftover: previous setuptools_scm stdout / generated version module
  git hash omitted from VenvPexProcess identity
  enclosing MaybeGitWorktree rule reran; child process reused

Case C (rm -rf ~/.cache/pants):
  fresh process identity
  not leftover previous git describe

Case D (PER_SESSION cache_scope):
  cache miss after git change
  not leftover previous version string

Not this packet:
  rustc incremental false-green (specimen-075)
  pants leftover process cache vs env (pants#23645 OPEN)

### vcs_versioning_failing.py

# Reduced excerpt of generate_python_from_setuptools_scm on failing_ref
# src/python/pants/backend/python/util_rules/vcs_versioning.py
# 02fa93e2947789cf1f9f8c025e7ceaca01169ef2
# VenvPexProcess has no cache_scope. Git hash omitted from process identity.

from pants.engine.process import ProcessResult
from pants.vcs.git import GitWorktreeRequest, MaybeGitWorktree

@rule
async def generate_python_from_setuptools_scm(
    request: GeneratePythonFromSetuptoolsSCMRequest,
    setuptools_scm: SetuptoolsSCM,
) -> GeneratedSources:
    # A GitWorktreeRequest is uncacheable, so this enclosing rule will run every time its result
    # is needed, meaning it will always return a result based on the current underlying git state.
    maybe_git_worktree = await Get(MaybeGitWorktree, GitWorktreeRequest())
    argv = ["--root", str(maybe_git_worktree.git_worktree.worktree), "--config", config_path]
    result = await Get(
        ProcessResult,
        VenvPexProcess(
            setuptools_scm_pex,
            argv=argv,
            input_digest=input_digest,
            description=f"Run setuptools_scm for {request.protocol_target.address.spec}",
            level=LogLevel.INFO,
            # no cache_scope=ProcessCacheScope.PER_SESSION
        ),
    )
    version = result.stdout.decode().strip()

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.
