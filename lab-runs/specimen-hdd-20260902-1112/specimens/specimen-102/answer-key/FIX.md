KNOWN FIX (sealed): astral-sh/uv PR 19269 squash a1c90c1fa12c95485f3d6a210daa4e6cc7466a90.

failing_ref is squash first parent 77f271063993020770ee785469226e33324576be.

Repair: when no uv workspace is found, from_metadata23_with_source_context still runs a git-origin rewriter on path URLs under fetch_root and locks them as Git+subdirectory. from_requirement's sources==None arm uses the same rewriter. path_source's existing git_member branch is shared. Added lock_git_poetry_path_dependency (child source git=?subdirectory=child).

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
