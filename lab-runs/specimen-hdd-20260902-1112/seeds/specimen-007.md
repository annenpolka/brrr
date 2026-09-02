CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

`git_index_add` is asked to add a blob at a path that collides with an existing tree (directory) entry, or the reverse. The call returns success. The conflicting stale entry remains in the index. Git's own `git add` would replace the conflicting entry.

The collision is missed only when other entries sort *before* the insertion point. Tests that seed a single prior entry (insertion position 0) do not see the failure.

The developer wants to know why the operation reported success and which index entries still conflict.

# OBSERVED

Public libgit2/libgit2#7160 / PR 7332.

- `git_index_add` succeeds.
- Stale conflicting file/dir entry remains.
- Existing collision tests with a single prior entry pass (insertion position happens to be 0).
- PR adds `add_blob_with_conflicting_dir_not_at_start`: sibling entries force a non-zero insertion position; conflict is missed on the failing revision.

# COMMANDS

libgit2 test: `add_blob_with_conflicting_dir_not_at_start` (PR 7332). Not executed on the lab host.

src/libgit2/index.c
tests/ for index add collisions

RELEVANT MATERIAL

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
