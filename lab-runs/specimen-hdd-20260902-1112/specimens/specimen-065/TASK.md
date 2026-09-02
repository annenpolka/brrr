# TASK

A docker language hook runs from inside a container (CI docker-in-docker / cgroup v2). pre-commit binds `-v <cwd>:/src`. The path it passes as the source is the *in-container* cwd, not the host path Docker would actually mount from.

On cgroup v1 hosts the same hook remaps cwd through `docker inspect` of the current container. On cgroup v2 it behaves as if it were not in Docker at all.

The developer wants to know which `/proc` file decided “we are / are not in Docker”, which container id (if any) was read, and which path ended up in the `-v` flag.
