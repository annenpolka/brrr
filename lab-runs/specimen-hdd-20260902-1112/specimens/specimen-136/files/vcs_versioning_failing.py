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
