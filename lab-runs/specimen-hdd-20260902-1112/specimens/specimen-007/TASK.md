# TASK

`git_index_add` is asked to add a blob at a path that collides with an existing tree (directory) entry, or the reverse. The call returns success. The conflicting stale entry remains in the index. Git's own `git add` would replace the conflicting entry.

The collision is missed only when other entries sort *before* the insertion point. Tests that seed a single prior entry (insertion position 0) do not see the failure.

The developer wants to know why the operation reported success and which index entries still conflict.
